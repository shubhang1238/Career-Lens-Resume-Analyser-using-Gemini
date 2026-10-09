from flask import Flask, render_template, request, jsonify, session
from resume_parser import extract_text
from gemini_utils import analyze_resume_jobdesc, gemini_chat
from werkzeug.utils import secure_filename
import uuid
import os
import traceback

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

# Vercel allows writes only to /tmp.
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "10"))
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def _save_upload(file):
    """Save an uploaded document using a unique, sanitized filename."""
    original = secure_filename(file.filename or "")
    extension = os.path.splitext(original)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, DOC, or TXT.")

    filename = f"{uuid.uuid4().hex}_{original}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    return path


@app.errorhandler(413)
def request_too_large(_error):
    return (
        jsonify(
            {
                "error": f"File upload is too large. Maximum total request size is {MAX_UPLOAD_MB} MB."
            }
        ),
        413,
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    """Simple deployment health endpoint."""
    return jsonify({"status": "ok", "service": "CareerLens AI"}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    resume_path = None
    jd_path = None

    try:
        if "resume" not in request.files:
            return jsonify({"error": "Resume file is missing."}), 400

        if "jobdesc" not in request.files:
            return jsonify({"error": "Job description file is missing."}), 400

        resume_file = request.files["resume"]
        jd_file = request.files["jobdesc"]

        if not resume_file.filename:
            return jsonify({"error": "Resume file was not selected."}), 400

        if not jd_file.filename:
            return jsonify({"error": "Job description file was not selected."}), 400

        resume_path = _save_upload(resume_file)
        jd_path = _save_upload(jd_file)

        resume_text = extract_text(resume_path)
        jd_text = extract_text(jd_path)

        if not resume_text or not resume_text.strip():
            return (
                jsonify(
                    {
                        "error": "Could not extract text from the resume. Please use a text-based PDF/DOCX."
                    }
                ),
                400,
            )

        if not jd_text or not jd_text.strip():
            return (
                jsonify(
                    {
                        "error": "Could not extract text from the job description. Please use a text-based PDF/DOCX."
                    }
                ),
                400,
            )

        result = analyze_resume_jobdesc(resume_text, jd_text)

        # Keep only the document text required for the chat endpoint.
        session["chat_id"] = str(uuid.uuid4())
        session["resume_text"] = resume_text[:30000]
        session["jd_text"] = jd_text[:30000]

        return jsonify(result), 200

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    except Exception as exc:
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {type(exc).__name__}: {exc}"}), 500

    finally:
        # /tmp is ephemeral, but cleaning files prevents unnecessary accumulation.
        for path in (resume_path, jd_path):
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        user_message = str(data.get("message", "")).strip()

        if not user_message:
            return jsonify({"response": "Please enter a message."}), 400

        resume_text = session.get("resume_text", "")
        jd_text = session.get("jd_text", "")

        if not resume_text or not jd_text:
            return (
                jsonify(
                    {
                        "response": "Please run a resume analysis first so I can use your resume and target job."
                    }
                ),
                400,
            )

        response = gemini_chat(resume_text, jd_text, user_message)
        return jsonify({"response": response}), 200

    except Exception as exc:
        traceback.print_exc()
        return jsonify({"response": f"Chat error: {type(exc).__name__}: {exc}"}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
    )

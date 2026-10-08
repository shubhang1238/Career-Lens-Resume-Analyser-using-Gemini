import os
import re
import json
from dotenv import load_dotenv
from google import genai

# -------------------------------
# Setup Gemini
# -------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")

client = genai.Client(api_key=API_KEY)

# Use latest free Flash model
MODEL = "gemini-3.7-flash"

# -------------------------------
# Utility: Safe JSON Extraction
# -------------------------------

def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in model response")
    return json.loads(match.group())

# -------------------------------
# Skill Extraction via Gemini
# -------------------------------

def extract_skills(resume_text, jd_text):
    prompt = f"""
Extract technical skills from the resume and job description.

Return ONLY raw JSON:
{{
  "resume_skills": [],
  "jd_skills": []
}}

Rules:
- Extract tools, frameworks, languages, platforms.
- Include implicit skills (e.g., Flask APIs → Flask, REST API).
- Do NOT include explanation text.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:3000]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return extract_json(response.text)
    except Exception:
        return {"resume_skills": [], "jd_skills": []}

# -------------------------------
# Skill Equivalence Mapping
# -------------------------------
SKILL_EQUIVALENCES = {
    # ============================================================
    # PROGRAMMING LANGUAGES
    # ============================================================
    "python": ["python 3", "python3", "py"],
    "javascript": ["js", "ecmascript", "es6", "es2015"],
    "typescript": ["ts"],
    "java": ["java se", "java ee", "core java"],
    "c++": ["cpp", "cplusplus"],
    "c#": ["csharp", ".net c#"],
    "go": ["golang"],
    "rust": ["rustlang"],
    # ============================================================
    # AI / GENERATIVE AI / LLM
    # ============================================================
    "artificial intelligence": ["ai", "artificial intelligence", "ai engineering"],
    "machine learning": ["ml", "machine learning", "ml engineering"],
    "deep learning": [
        "deep learning",
        "deep neural networks",
        "neural networks",
        "dnn",
    ],
    "generative ai": [
        "genai",
        "gen ai",
        "generative artificial intelligence",
        "generative-ai",
    ],
    "large language models": [
        "llm",
        "llms",
        "large language model",
        "large language models",
    ],
    "llm application development": [
        "llm applications",
        "llm app development",
        "llm engineering",
        "llm application engineering",
    ],
    "prompt engineering": [
        "prompt engineering",
        "prompt design",
        "prompt optimization",
        "prompting",
    ],
    "ai agents": [
        "ai agents",
        "agentic ai",
        "agentic systems",
        "autonomous agents",
        "llm agents",
        "ai agent development",
    ],
    "llm orchestration": [
        "llm orchestration",
        "ai orchestration",
        "llm workflow orchestration",
    ],
    "langchain": ["lang chain", "langchain framework"],
    "langgraph": ["lang graph"],
    "llamaindex": ["llama index", "llamaindex"],
    "hugging face": ["huggingface", "hugging face transformers", "transformers"],
    # ============================================================
    # RAG / VECTOR SEARCH / AI DATA
    # ============================================================
    "rag": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "retrieval augmented ai",
        "rag pipelines",
        "rag systems",
    ],
    "vector databases": [
        "vector db",
        "vector database",
        "vector databases",
        "vector store",
        "vector stores",
    ],
    "vector search": [
        "semantic search",
        "similarity search",
        "embedding search",
        "vector retrieval",
    ],
    "embeddings": ["text embeddings", "embedding models", "vector embeddings"],
    "knowledge graphs": [
        "knowledge graph",
        "graph-based retrieval",
        "graph rag",
        "graphrag",
    ],
    "ai evaluation": [
        "llm evaluation",
        "model evaluation",
        "ai evaluation",
        "rag evaluation",
        "llm evals",
        "evals",
    ],
    "fine tuning": [
        "fine-tuning",
        "model fine tuning",
        "llm fine tuning",
        "parameter efficient fine tuning",
        "peft",
    ],
    "nlp": ["natural language processing", "natural language processing nlp"],
    # ============================================================
    # AI / ML FRAMEWORKS
    # ============================================================
    "pytorch": ["torch"],
    "tensorflow": ["tf"],
    "keras": ["keras", "tensorflow keras"],
    "scikit-learn": ["sklearn", "scikit learn"],
    # ============================================================
    # APIS / WEB SERVICES
    # ============================================================
    "rest api": [
        "restful api",
        "rest apis",
        "restful apis",
        "rest api development",
        "rest services",
        "rest web services",
    ],
    "graphql": ["graphql api", "graphql apis"],
    "grpc": ["grpc api", "grpc services", "remote procedure call"],
    "api development": ["api design", "api development", "web api", "api integration"],
    "api integration": [
        "api integrations",
        "third party api integration",
        "third-party api integration",
        "service integration",
    ],
    "webhooks": ["webhook", "webhooks integration"],
    # ============================================================
    # BACKEND
    # ============================================================
    "backend development": [
        "backend engineering",
        "server side development",
        "server-side development",
    ],
    "flask": ["flask framework", "python flask"],
    "django": ["django framework", "python django"],
    "fastapi": ["fast api", "python fastapi"],
    "node.js": ["nodejs", "node js"],
    "express.js": ["express", "expressjs", "express js"],
    "spring boot": ["springboot", "spring boot framework"],
    "spring": ["spring framework", "spring boot"],
    # ============================================================
    # FRONTEND
    # ============================================================
    "frontend development": [
        "front end development",
        "frontend engineering",
        "front-end development",
    ],
    "react": ["reactjs", "react js"],
    "next.js": ["nextjs", "next js"],
    "angular": ["angularjs", "angular js"],
    "vue.js": ["vue", "vuejs", "vue js"],
    "html": ["html5", "hypertext markup language"],
    "css": ["css3", "cascading style sheets"],
    "tailwind css": ["tailwindcss", "tailwind"],
    # ============================================================
    # DATABASES
    # ============================================================
    "sql": ["structured query language", "sql queries", "sql programming"],
    "mysql": ["mysql database", "mysql server"],
    "postgresql": ["postgres", "postgres database", "postgresql database"],
    "mongodb": ["mongo", "mongo db", "mongodb database"],
    "redis": ["redis cache", "redis database"],
    "nosql": ["no sql", "non relational database", "non-relational database"],
    "databases": ["database systems", "database management", "dbms"],
    # ============================================================
    # DATA ENGINEERING
    # ============================================================
    "data engineering": [
        "data engineer",
        "data engineering",
        "data platform engineering",
    ],
    "etl": ["extract transform load", "extract-transform-load", "etl pipelines"],
    "data pipelines": [
        "data pipeline",
        "data processing pipelines",
        "data engineering pipelines",
    ],
    "data processing": ["data transformation", "data preprocessing", "data wrangling"],
    "apache spark": ["spark", "pyspark"],
    "apache kafka": ["kafka", "kafka streaming"],
    "airflow": ["apache airflow", "airflow orchestration"],
    "dbt": ["data build tool", "dbt core"],
    # ============================================================
    # DATA / ANALYTICS
    # ============================================================
    "pandas": ["python pandas"],
    "numpy": ["python numpy"],
    "data analysis": ["data analytics", "data analysis", "data analytics"],
    "data visualization": ["data visualisation", "data visualization"],
    "statistics": ["statistical analysis", "statistics and probability"],
    # ============================================================
    # CLOUD
    # ============================================================
    "aws": ["amazon web services", "aws cloud", "amazon aws"],
    "azure": ["microsoft azure", "azure cloud"],
    "gcp": ["google cloud", "google cloud platform"],
    "cloud computing": ["cloud technology", "cloud services", "cloud platforms"],
    "cloud infrastructure": [
        "cloud infrastructure",
        "cloud architecture",
        "cloud environment",
    ],
    "serverless": ["serverless computing", "serverless architecture"],
    # ============================================================
    # CONTAINERS / DEVOPS
    # ============================================================
    "docker": ["docker containers", "docker containerization"],
    "kubernetes": ["k8s", "kubernetes orchestration"],
    "containerization": [
        "containerisation",
        "containerized applications",
        "containerised applications",
        "containers",
    ],
    "helm": ["helm charts", "helm kubernetes"],
    "terraform": ["terraform infrastructure", "infrastructure as code terraform"],
    "infrastructure as code": [
        "iac",
        "infrastructure-as-code",
        "infrastructure as code",
    ],
    "ansible": ["ansible automation"],
    # ============================================================
    # CI / CD
    # ============================================================
    "ci/cd": [
        "cicd",
        "continuous integration",
        "continuous delivery",
        "continuous deployment",
        "ci cd",
        "ci/cd pipelines",
    ],
    "github actions": ["github workflows", "github actions workflows"],
    "jenkins": ["jenkins ci", "jenkins pipeline"],
    "gitlab ci": ["gitlab pipelines", "gitlab cicd", "gitlab ci/cd"],
    # ============================================================
    # DEVOPS
    # ============================================================
    "devops": ["dev ops", "devops engineering", "development operations"],
    "platform engineering": ["platform engineer", "internal developer platform", "idp"],
    # ============================================================
    # OBSERVABILITY
    # ============================================================
    "observability": [
        "application observability",
        "system observability",
        "cloud observability",
    ],
    "monitoring": [
        "application monitoring",
        "system monitoring",
        "infrastructure monitoring",
    ],
    "prometheus": ["prometheus monitoring"],
    "grafana": ["grafana dashboards", "grafana monitoring"],
    "opentelemetry": ["open telemetry", "otel"],
    "logging": ["application logging", "centralized logging", "centralised logging"],
    # ============================================================
    # VERSION CONTROL
    # ============================================================
    "git": ["git version control", "distributed version control"],
    "github": ["github repositories", "github platform"],
    "gitlab": ["gitlab repositories", "gitlab platform"],
    "bitbucket": ["bitbucket repositories"],
    "version control": ["source control", "version control systems", "vcs"],
    # ============================================================
    # TESTING / QA
    # ============================================================
    "unit testing": ["unit tests", "unit test automation"],
    "integration testing": ["integration tests", "integration test automation"],
    "pytest": ["python pytest", "pytest framework"],
    "selenium": ["selenium webdriver", "selenium testing"],
    "cypress": ["cypress testing", "cypress automation"],
    "postman": ["postman api testing", "postman testing"],
    # ============================================================
    # SOFTWARE ENGINEERING
    # ============================================================
    "object oriented programming": [
        "oop",
        "object-oriented programming",
        "object oriented design",
    ],
    "data structures": ["data structures and algorithms", "dsa"],
    "algorithms": ["algorithm design", "data structures and algorithms", "dsa"],
    "system design": [
        "software architecture",
        "system architecture",
        "distributed system design",
    ],
    "distributed systems": ["distributed system", "distributed computing"],
    "microservices": [
        "microservice architecture",
        "microservices architecture",
        "microservice based architecture",
    ],
    # ============================================================
    # SECURITY
    # ============================================================
    "cybersecurity": ["cyber security", "information security", "infosec"],
    "application security": ["appsec", "application security engineering"],
    "cloud security": ["cloud cybersecurity", "cloud security engineering"],
    "authentication": ["user authentication", "identity authentication"],
    "authorization": ["access control", "user authorization"],
    "oauth": ["oauth2", "oauth 2.0"],
    "jwt": ["json web token", "json web tokens"],
    # ============================================================
    # AGILE / DELIVERY
    # ============================================================
    "agile": ["agile methodology", "agile development", "agile software development"],
    "scrum": ["scrum methodology", "scrum framework"],
    "kanban": ["kanban methodology", "kanban framework"],
    "jira": ["atlassian jira", "jira software"],
    # ============================================================
    # AI / SOFTWARE DEVELOPMENT TOOLS
    # ============================================================
    "ai coding assistants": [
        "ai coding tools",
        "ai developer tools",
        "coding copilots",
        "ai copilot",
    ],
    "github copilot": ["copilot", "github ai copilot"],
    "ai workflow automation": [
        "ai automation",
        "intelligent automation",
        "ai-powered automation",
        "ai workflow",
    ],
    # ============================================================
    # COMMUNICATION / PROFESSIONAL SKILLS
    # ============================================================
    "problem solving": ["problem-solving", "analytical problem solving"],
    "analytical thinking": ["analytical skills", "analytical thinking"],
    "communication": [
        "communication skills",
        "written communication",
        "verbal communication",
    ],
    "collaboration": ["team collaboration", "cross-functional collaboration"],
}

# -------------------------------
# Normalization
# -------------------------------

def normalize(skill: str) -> str:
    return skill.lower().strip().replace("-", "").replace("_", "")

# -------------------------------
# Matching Logic
# -------------------------------

def is_full_match(resume_skill, jd_skill):
    r = normalize(resume_skill)
    j = normalize(jd_skill)

    if r == j:
        return True

    if r in SKILL_EQUIVALENCES and j in [normalize(x) for x in SKILL_EQUIVALENCES[r]]:
        return True

    if j in SKILL_EQUIVALENCES and r in [normalize(x) for x in SKILL_EQUIVALENCES[j]]:
        return True

    return False


def is_partial_match(resume_skill, jd_skill):
    r = normalize(resume_skill)
    j = normalize(jd_skill)

    if is_full_match(resume_skill, jd_skill):
        return False

    if r in j or j in r:
        return True

    return False

# -------------------------------
# Semantic Skill Matching
# -------------------------------

def semantic_skill_matching(resume_skills, jd_skills):

    analysis = []
    matched = []
    partial = []
    missing = []

    for jd in jd_skills:
        found = False

        for rs in resume_skills:
            if is_full_match(rs, jd):
                analysis.append({
                    "jd_skill": jd,
                    "status": "Full Match",
                    "resume_evidence": rs,
                    "confidence": "High"
                })
                matched.append(jd)
                found = True
                break

        if not found:
            for rs in resume_skills:
                if is_partial_match(rs, jd):
                    analysis.append({
                        "jd_skill": jd,
                        "status": "Partial Match",
                        "resume_evidence": rs,
                        "confidence": "Medium"
                    })
                    partial.append(jd)
                    found = True
                    break

        if not found:
            analysis.append({
                "jd_skill": jd,
                "status": "Missing",
                "resume_evidence": "",
                "confidence": "Low"
            })
            missing.append(jd)

    total = len(jd_skills)
    full_score = len(matched)
    partial_score = len(partial) * 0.5

    similarity_score = int(((full_score + partial_score) / total) * 100) if total else 0

    return {
        "analysis": analysis,
        "matched_skills": matched,
        "partial_matches": partial,
        "missing_skills": missing,
        "similarity_score": similarity_score
    }

# -------------------------------
# Experience + Project Evaluation
# -------------------------------

def evaluate_experience_and_projects(resume_text, jd_text):

    prompt = f"""
Evaluate the resume against the job description.

Return ONLY JSON:
{{
  "experience_score": number,
  "project_score": number,
  "improvements": [],
  "summary": ""
}}

Score from 0–100.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:2000]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return extract_json(response.text)
    except Exception:
        return {
            "experience_score": 0,
            "project_score": 0,
            "improvements": [],
            "summary": "Evaluation failed"
        }

# -------------------------------
# Final ATS Analysis
# -------------------------------

def analyze_resume_jobdesc(resume_text, jd_text):

    skills = extract_skills(resume_text, jd_text)
    resume_skills = skills.get("resume_skills", [])
    jd_skills = skills.get("jd_skills", [])

    skill_result = semantic_skill_matching(resume_skills, jd_skills)
    exp_result = evaluate_experience_and_projects(resume_text, jd_text)

    skill_score = skill_result["similarity_score"]
    exp_score = int(exp_result.get("experience_score", 0))
    proj_score = int(exp_result.get("project_score", 0))

    final_ats = round(
        skill_score * 0.70 +
        exp_score * 0.20 +
        proj_score * 0.10
    )

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "analysis": skill_result["analysis"],
        "matched_skills": skill_result["matched_skills"],
        "partial_matches": skill_result["partial_matches"],
        "missing_skills": skill_result["missing_skills"],
        "improvements": exp_result.get("improvements", []),
        "summary": exp_result.get("summary", ""),
        "score_breakdown": {
            "skill_match": skill_score,
            "experience_match": exp_score,
            "project_match": proj_score
        },
        "final_ats_score": final_ats
    }

# -------------------------------
# Chat Feature
# -------------------------------

def gemini_chat(resume_text, jd_text, user_msg):

    prompt = f"""
Answer the user's question about resume-job match.
Be specific and actionable.

RESUME:
{resume_text[:1500]}

JOB DESCRIPTION:
{jd_text[:1500]}

QUESTION:
{user_msg[:400]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception:
        return "Chat failed."

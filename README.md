```markdown
# 🚀 CareerLens AI — Intelligent Resume & Job Description Analyzer

<p align="center">

**AI-Powered Resume Intelligence • ATS Matching • Skill Gap Analysis • Career Optimization**

CareerLens AI is an intelligent web application that analyzes a candidate's resume against a target Job Description (JD) using **Generative AI, NLP-based skill extraction, semantic skill matching, weighted ATS scoring, and interactive data visualization**.

The platform helps candidates understand:

- 🎯 How closely their resume matches a specific job
- 🧠 Which technical skills are already aligned
- ⚠️ Which skills are only partially matched
- ❌ Which important skills are missing
- 📊 How their ATS score is calculated
- 💼 How their experience and projects fit the role
- ✨ How they can improve their resume before applying

---

## 📸 Project Overview

CareerLens AI transforms a traditional resume checker into an interactive AI-powered career intelligence dashboard.

### Core Workflow

```text
                ┌───────────────────────┐
                │      Candidate        │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │     Resume Upload     │
                │       PDF/DOCX/TXT    │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   Job Description     │
                │       Upload          │
                └───────────┬───────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │     Document Extraction     │
              │  PDF / DOCX / TXT Parsing  │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │       Gemini AI / LLM       │
              │  Skill & Context Analysis   │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │    Skill Normalization      │
              │   & Semantic Matching       │
              └─────────────┬──────────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │      ATS Score Engine       │
              │ Skills + Experience +       │
              │ Projects                    │
              └─────────────┬──────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │          CareerLens Dashboard           │
        │                                         │
        │  ATS Score       Skill Alignment        │
        │  Charts          Skill Gaps              │
        │  Improvements    Recruiter Readout       │
        │  AI Career Chat                         │
        └─────────────────────────────────────────┘
```

---

# ✨ Key Features

## 🎯 1. AI-Powered ATS Resume Analysis

CareerLens AI evaluates the candidate's resume against a target job description and generates an overall compatibility score.

The ATS score considers:

```text
              ATS SCORE
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
     Skills   Experience  Projects
      70%        20%        10%
```

### Current scoring model

```text
Final ATS Score =
    Skill Score × 70%
  + Experience Score × 20%
  + Project Score × 10%
```

This makes the system more meaningful than simply counting matching keywords.

---

# 🧠 2. Generative AI Integration

CareerLens AI uses **Google Gemini** as the primary Large Language Model.

Gemini is used for understanding the semantic meaning and context of resumes and job descriptions.

### Gemini is used for

- Resume skill extraction
- Job description skill extraction
- Contextual skill interpretation
- Experience evaluation
- Project relevance evaluation
- Resume improvement suggestions
- Recruiter-style summary generation
- Interactive career Q&A

The application sends structured resume and JD content to Gemini and converts the response into structured information used by the ATS engine.

---

# 🤖 3. AI / ML Pipeline

CareerLens AI combines traditional software logic with modern AI techniques.

```text
Resume
   │
   ▼
Text Extraction
   │
   ▼
NLP / LLM Understanding
   │
   ▼
Skill Extraction
   │
   ▼
Skill Normalization
   │
   ▼
Semantic / Equivalence Matching
   │
   ├───────────────┐
   │               │
   ▼               ▼
Exact Match    Related Match
   │               │
   └───────┬───────┘
           ▼
      Skill Score
           │
           ▼
Experience Analysis
           │
           ▼
Project Analysis
           │
           ▼
      ATS Score
           │
           ▼
Interactive Dashboard
```

---

# 🔬 4. NLP & Semantic Understanding

The project is not limited to exact keyword matching.

For example:

```text
Resume:
RESTful API

Job Description:
REST API Development
```

The analyzer can recognize these as related skills.

Similarly:

```text
Resume:
PostgreSQL

Job Description:
SQL Database
```

can be interpreted as a related database capability.

This is implemented using a configurable skill-equivalence taxonomy.

---

# 🧩 5. Intelligent Skill Taxonomy

CareerLens AI maintains a structured skill-equivalence system covering modern technology stacks.

### AI / GenAI

```text
Generative AI
LLM
Prompt Engineering
RAG
Vector Databases
Embeddings
AI Agents
LangChain
LangGraph
LlamaIndex
Hugging Face
LLM Evaluation
Fine-Tuning
NLP
```

### Programming

```text
Python
Java
JavaScript
TypeScript
C
C++
C#
Go
Rust
```

### Backend

```text
Flask
Django
FastAPI
Node.js
Express.js
Spring
Spring Boot
REST API
GraphQL
gRPC
API Integration
Webhooks
```

### Frontend

```text
React
Next.js
Angular
Vue.js
HTML
CSS
Tailwind CSS
```

### Databases

```text
SQL
MySQL
PostgreSQL
MongoDB
Redis
NoSQL
Database Management
```

### Data Engineering

```text
ETL
Data Pipelines
Apache Spark
PySpark
Apache Kafka
Airflow
dbt
Data Processing
```

### Cloud

```text
AWS
Azure
GCP
Cloud Computing
Cloud Infrastructure
Serverless
```

### DevOps

```text
Docker
Kubernetes
Helm
Terraform
Ansible
CI/CD
GitHub Actions
Jenkins
GitLab CI
DevOps
Infrastructure as Code
```

### Observability

```text
Observability
Monitoring
Prometheus
Grafana
OpenTelemetry
Logging
```

### Security

```text
Cybersecurity
Application Security
Cloud Security
OAuth
JWT
Authentication
Authorization
```

---

# 🔍 6. Exact, Partial & Missing Skill Detection

The system categorizes skills into three major groups.

### 🟢 Strong Match

The resume contains the required skill or a strong equivalent.

Example:

```text
JD:
Python

Resume:
Python
```

Result:

```text
✓ Python
```

---

### 🟡 Partial Match

The resume contains a related capability but not the exact requirement.

Example:

```text
JD:
REST API

Resume:
Flask
```

Result:

```text
~ REST API
```

This indicates that the candidate may have relevant exposure but should explicitly mention REST API experience if they genuinely possess it.

---

### 🔴 Missing Skill

The JD requires a skill that was not detected in the resume.

Example:

```text
JD:
Kubernetes

Resume:
Docker
```

Result:

```text
✕ Kubernetes
```

Importantly, the analyzer avoids treating every related technology as identical.

---

# 📊 7. Interactive Data Visualization

The new dashboard provides visual representations of the analysis instead of showing raw text alone.

### ATS Score Ring

The overall score is displayed through an animated circular visualization.

```text
             ╭────────────╮
          ╭──│            │──╮
        ╭─  │     82      │  ─╮
       │    │    /100     │    │
        ╰─  │            │  ─╯
          ╰──│            │──╯
             ╰────────────╯
```

---

## 📈 Match Breakdown Chart

The application visualizes:

```text
Skills
████████████████████ 90%

Experience
████████████████    78%

Projects
██████████████      70%
```

This helps candidates understand where their profile is strongest.

---

## 🍩 Skill Coverage Chart

The dashboard also visualizes:

```text
        Skill Coverage

          █████
       ███     ███
      ██         ██
     ██   MATCH   ██
      ██         ██
       ███     ███
          █████

Matched
Partial
Missing
```

The chart shows the proportion of:

- Matched skills
- Partially matched skills
- Missing skills

---

# 💼 8. Experience & Project Analysis

A resume should not be evaluated purely through technical keywords.

Gemini analyzes:

### Experience

- Relevance to the target role
- Technology alignment
- Responsibility alignment
- Industry relevance
- Role progression

### Projects

- Technical relevance
- Technology usage
- Complexity
- Relationship to JD requirements
- Evidence of practical implementation

The resulting scores contribute to the final ATS score.

---

# 📝 9. AI Recruiter Readout

CareerLens AI generates a concise recruiter-style assessment.

Example:

```text
The candidate demonstrates strong alignment with the
target role through Python, SQL and API development
experience. The profile would benefit from explicitly
highlighting cloud deployment, Docker and CI/CD exposure.
```

This helps the candidate understand how their resume may appear from a hiring perspective.

---

# 🛠️ 10. AI Resume Improvement Roadmap

Instead of simply saying:

```text
Missing: Kubernetes
```

the application provides actionable recommendations.

Example:

```text
01
Explicitly highlight REST API development in your
professional experience if applicable.

02
Add measurable impact to your project descriptions.

03
Mention Docker/containerization where genuinely used.

04
Move the most relevant technical skills closer to
the top of the resume.

05
Add JD-specific terminology naturally where supported
by your actual experience.
```

---

# 💬 11. Gemini Career Assistant

CareerLens AI includes an interactive AI chat assistant.

After analyzing a resume and JD, users can ask questions such as:

```text
What are my biggest skill gaps?

How can I improve my ATS score?

Which skills should I highlight?

Is my experience relevant to this job?

How should I rewrite my project?

What should I add to my professional summary?

Which skills are most important for this JD?
```

The assistant uses the analyzed resume and job description as context.

---

# 📂 12. Supported File Formats

The application supports:

```text
PDF
DOCX
TXT
```

The uploaded documents are temporarily processed by the Flask backend.

Files are validated before processing and temporary uploaded files can be cleaned after analysis.

---

# 🏗️ Project Architecture

```text
CareerLens AI
│
├── app.py
│
├── gemini_utils.py
│
├── resume_parser.py
│
├── requirements.txt
│
├── .env
│
├── uploads/
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── main.js
```

---

# 🔄 Application Architecture

```text
                 Browser
                    │
                    ▼
            ┌───────────────┐
            │  index.html   │
            │  Dashboard UI │
            └───────┬───────┘
                    │
             HTTP / Fetch API
                    │
                    ▼
            ┌───────────────┐
            │    Flask      │
            │   app.py      │
            └───────┬───────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
   resume_parser.py     gemini_utils.py
          │                   │
          │                   ▼
          │             Gemini API
          │                   │
          └─────────┬─────────┘
                    │
                    ▼
             ATS Score Engine
                    │
                    ▼
             JSON Response
                    │
                    ▼
              Dashboard
```

---

# 🧰 Technology Stack

## Backend

| Technology | Purpose |
| --- | --- |
| Python | Core programming |
| Flask | Web backend |
| Werkzeug | Secure file handling |
| python-dotenv | Environment configuration |
| Google GenAI SDK | Gemini integration |

---

## AI / ML

| Technology | Purpose |
| --- | --- |
| Gemini | LLM reasoning |
| NLP | Resume/JD understanding |
| Semantic matching | Skill comparison |
| Skill taxonomy | Skill normalization |
| Weighted scoring | ATS calculation |

---

## Frontend

| Technology | Purpose |
| --- | --- |
| HTML5 | Application structure |
| CSS3 | UI / animations |
| Bootstrap | Responsive utilities |
| JavaScript | Frontend logic |
| Chart.js | Data visualization |
| Bootstrap Icons | Interface icons |
| Google Fonts | Typography |

---

# 🧠 How AI Is Used

The application uses AI in several stages.

### Stage 1 — Resume Understanding

Gemini identifies relevant information from the resume:

```text
Skills
Experience
Projects
Technologies
Responsibilities
Achievements
```

---

### Stage 2 — JD Understanding

Gemini identifies:

```text
Required skills
Preferred skills
Experience requirements
Technology stack
Responsibilities
Role expectations
```

---

### Stage 3 — Skill Normalization

Skills are normalized before comparison.

Example:

```text
React.js
ReactJS
React JS

        ↓

React
```

Another example:

```text
RESTful API
REST API
REST APIs

        ↓

REST API
```

---

### Stage 4 — Semantic Matching

The analyzer compares normalized resume skills with normalized JD skills.

```text
Exact Match
     ↓
Strong Equivalent
     ↓
Partial / Related
     ↓
Missing
```

---

### Stage 5 — Experience Evaluation

Gemini evaluates whether the candidate's professional experience aligns with the role.

---

### Stage 6 — Project Evaluation

Projects are evaluated for technical and functional relevance.

---

### Stage 7 — Final ATS Score

The scores are combined using the weighted scoring model.

```text
                 Skill Score
                     │
                    70%
                     │
                     ▼
Experience ────────► ATS ◄──────── Projects
   20%               Score            10%
```

---

# 📐 ATS Scoring Methodology

The current model uses:

```python
final_score = (
    skill_score * 0.70
    + experience_score * 0.20
    + project_score * 0.10
)
```

### Example

Suppose:

```text
Skill Score       = 85
Experience Score  = 75
Project Score     = 80
```

Then:

```text
ATS =
(85 × 0.70)
+
(75 × 0.20)
+
(80 × 0.10)

= 59.5
+ 15
+ 8

= 82.5
```

Final ATS Score:

```text
82.5 / 100
```

---

# 🔐 Security Considerations

The application is designed to avoid hard-coding sensitive API credentials.

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_supported_gemini_model
FLASK_SECRET_KEY=your_random_secret
```

### Never commit `.env`

Add this to `.gitignore`:

```gitignore
.env
__pycache__/
*.pyc
uploads/
venv/
.venv/
```

If an API key is accidentally exposed publicly, revoke it and generate a new key.

---

# ⚙️ Project Setup

## 1. Clone the repository

```bash
git clone https://github.com/your-username/careerlens-ai.git
```

Move into the project:

```bash
cd careerlens-ai
```

---

# 🐍 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

---

# 📦 3. Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

If `requirements.txt` does not exist:

```bash
pip install

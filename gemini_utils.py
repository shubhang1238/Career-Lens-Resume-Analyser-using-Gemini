import os
import re
import json
from dotenv import load_dotenv
from google import genai

# ============================================================
# Configuration
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")

client = genai.Client(api_key=API_KEY)

# Override in Vercel if required:
# GEMINI_MODEL=gemini-2.5-flash
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

MAX_SKILL_TEXT = int(os.getenv("MAX_SKILL_TEXT", "16000"))
MAX_EVAL_TEXT = int(os.getenv("MAX_EVAL_TEXT", "10000"))


# ============================================================
# Utility: Safe JSON extraction
# ============================================================

def extract_json(text: str):
    """Extract the first valid JSON object from a model response."""
    if not text:
        raise ValueError("Empty model response")

    text = text.strip()

    # Remove Markdown fences.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    # First try the complete response.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Then find the outer JSON object.
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in model response")

    decoder = json.JSONDecoder()
    try:
        value, _ = decoder.raw_decode(text[start:])
        return value
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON from model: {exc}") from exc


def unique_clean(values):
    """Clean, normalize and deduplicate a list while preserving order."""
    result = []
    seen = set()

    for value in values or []:
        if value is None:
            continue

        value = str(value).strip()
        value = re.sub(r"\s+", " ", value)

        if not value:
            continue

        key = normalize(value)

        if key not in seen:
            seen.add(key)
            result.append(value)

    return result


# ============================================================
# Skill Knowledge Base
#
# This is intentionally broad so the application can work even
# when Gemini extraction is unavailable. The dictionary covers
# current AI/GenAI, data, cloud, cybersecurity, software,
# analytics and professional hiring terminology.
# ============================================================

SKILL_EQUIVALENCES = {

    # ----------------------------------------------------------
    # Programming
    # ----------------------------------------------------------
    "python": ["python 3", "python3", "py"],
    "javascript": ["js", "ecmascript", "es6", "es2015"],
    "typescript": ["ts"],
    "java": ["java se", "java ee", "core java"],
    "c": ["c language", "c programming"],
    "c++": ["cpp", "cplusplus", "c plus plus"],
    "c#": ["csharp", "c sharp"],
    "go": ["golang", "go programming"],
    "rust": ["rustlang", "rust language"],
    "kotlin": ["kotlin language"],
    "swift": ["swift programming"],
    "scala": ["scala language"],
    "ruby": ["ruby programming"],
    "php": ["php programming"],
    "r": ["r programming", "r language"],
    "dart": ["dart language"],
    "matlab": ["matlab programming"],
    "powershell": ["powershell scripting", "powershell scripting language"],
    "bash": ["bash scripting", "shell scripting"],
    "shell scripting": ["shell script", "shell scripting"],

    # ----------------------------------------------------------
    # AI / Machine Learning / GenAI
    # ----------------------------------------------------------
    "artificial intelligence": ["ai", "artificial intelligence", "ai engineering"],
    "machine learning": ["ml", "machine learning", "ml engineering"],
    "deep learning": ["deep neural networks", "neural networks", "dnn"],
    "generative ai": ["genai", "gen ai", "generative artificial intelligence", "generative-ai"],
    "large language models": ["llm", "llms", "large language model", "large language models"],
    "llm application development": ["llm applications", "llm app development", "llm engineering", "llm application engineering"],
    "prompt engineering": ["prompt design", "prompt optimization", "prompting"],
    "prompt evaluation": ["prompt testing", "prompt evaluation"],
    "ai agents": ["ai agent", "agentic ai", "agentic systems", "autonomous agents", "llm agents", "agent development"],
    "agentic ai": ["agentic systems", "agentic artificial intelligence"],
    "agentic workflows": ["agent workflows", "ai agent workflows", "agentic workflow"],
    "llm orchestration": ["ai orchestration", "llm workflow orchestration"],
    "model context protocol": ["mcp", "model context protocol"],
    "function calling": ["tool calling", "function-calling", "function calling"],
    "multimodal ai": ["multimodal artificial intelligence", "multimodal llm"],
    "computer vision": ["cv", "computer vision"],
    "natural language processing": ["nlp", "natural language processing"],
    "speech recognition": ["automatic speech recognition", "asr", "speech-to-text"],
    "reinforcement learning": ["rl", "reinforcement learning"],
    "transfer learning": ["transfer learning"],
    "fine tuning": ["fine-tuning", "model fine tuning", "llm fine tuning", "parameter efficient fine tuning", "peft"],
    "retrieval augmented generation": ["rag", "retrieval-augmented generation", "retrieval augmented ai", "rag pipelines", "rag systems"],
    "vector databases": ["vector db", "vector database", "vector databases", "vector store", "vector stores"],
    "vector search": ["semantic search", "similarity search", "embedding search", "vector retrieval"],
    "embeddings": ["text embeddings", "embedding models", "vector embeddings"],
    "knowledge graphs": ["knowledge graph", "graph-based retrieval", "graph rag", "graphrag"],
    "ai evaluation": ["llm evaluation", "model evaluation", "ai evaluation", "rag evaluation", "llm evals", "evals"],
    "llmops": ["llm ops", "llm operations"],
    "mlops": ["ml ops", "machine learning operations"],
    "ai observability": ["llm observability", "model observability"],
    "responsible ai": ["responsible artificial intelligence"],
    "ai governance": ["generative ai governance"],
    "ai security": ["generative ai security", "llm security"],
    "prompt injection": ["prompt injection attacks"],
    "retrieval systems": ["retrieval system", "information retrieval"],
    "recommendation systems": ["recommender systems", "recommendation engine"],

    # ----------------------------------------------------------
    # AI Providers / Models
    # ----------------------------------------------------------
    "openai": ["openai api", "openai platform"],
    "google gemini": ["gemini", "gemini api", "google gemini"],
    "anthropic claude": ["anthropic", "claude", "claude ai"],
    "llama": ["llama 2", "llama 3", "llama 3.1", "llama 3.2", "meta llama"],
    "mistral": ["mistral ai", "mistral models"],
    "hugging face": ["huggingface", "hugging face transformers"],
    "transformers": ["hugging face transformers", "transformers library"],

    # ----------------------------------------------------------
    # AI Frameworks / Libraries
    # ----------------------------------------------------------
    "langchain": ["lang chain", "langchain framework"],
    "langgraph": ["lang graph"],
    "llamaindex": ["llama index", "llamaindex"],
    "pytorch": ["torch", "pytorch framework"],
    "tensorflow": ["tf", "tensorflow framework"],
    "keras": ["tensorflow keras"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "xgboost": ["xgboost"],
    "lightgbm": ["light gbm"],
    "opencv": ["open cv"],
    "spaCy": ["spacy", "spacy nlp"],

    # ----------------------------------------------------------
    # Data Science / Analytics
    # ----------------------------------------------------------
    "pandas": ["python pandas"],
    "numpy": ["python numpy"],
    "data analysis": ["data analytics", "data analysis"],
    "data visualization": ["data visualisation", "data visualization"],
    "statistics": ["statistical analysis", "statistics and probability"],
    "data storytelling": ["data story", "data storytelling"],
    "business intelligence": ["bi", "business intelligence"],
    "data quality": ["data quality management"],
    "data governance": ["data governance"],
    "data modeling": ["data modelling", "data model"],
    "data science": ["data scientist", "data science"],
    "feature engineering": ["feature extraction", "feature engineering"],
    "exploratory data analysis": ["eda", "exploratory data analysis"],
    "a/b testing": ["ab testing", "a-b testing", "split testing"],
    "experimentation": ["experimentation framework"],
    "power bi": ["powerbi", "microsoft power bi"],
    "power query": ["microsoft power query"],
    "tableau": ["tableau desktop", "tableau server"],
    "microsoft excel": ["excel", "ms excel", "microsoft excel"],
    "advanced excel": ["advanced microsoft excel", "excel pivot tables"],
    "looker": ["looker studio", "google looker"],
    "qlik": ["qlik sense", "qlikview"],

    # ----------------------------------------------------------
    # SQL / Databases
    # ----------------------------------------------------------
    "sql": ["structured query language", "sql queries", "sql programming"],
    "mysql": ["mysql database", "mysql server"],
    "postgresql": ["postgres", "postgres database", "postgresql database"],
    "mongodb": ["mongo", "mongo db", "mongodb database"],
    "redis": ["redis cache", "redis database"],
    "oracle database": ["oracle db", "oracle database"],
    "microsoft sql server": ["sql server", "mssql"],
    "sqlite": ["sqlite database"],
    "nosql": ["no sql", "non relational database", "non-relational database"],
    "databases": ["database systems", "database management", "dbms"],
    "database design": ["database architecture"],
    "pinecone": ["pinecone vector database"],
    "weaviate": ["weaviate vector database"],
    "chroma": ["chromadb", "chroma db"],
    "qdrant": ["qdrant vector database"],
    "pgvector": ["postgres vector", "pg vector"],
    "neo4j": ["neo4j graph database"],

    # ----------------------------------------------------------
    # Data Engineering
    # ----------------------------------------------------------
    "data engineering": ["data engineer", "data platform engineering"],
    "etl": ["extract transform load", "extract-transform-load", "etl pipelines"],
    "elt": ["extract load transform"],
    "data pipelines": ["data pipeline", "data processing pipelines", "data engineering pipelines"],
    "data processing": ["data transformation", "data preprocessing", "data wrangling"],
    "apache spark": ["spark", "pyspark"],
    "apache kafka": ["kafka", "kafka streaming"],
    "apache airflow": ["airflow", "airflow orchestration"],
    "dbt": ["data build tool", "dbt core"],
    "databricks": ["databricks platform"],
    "snowflake": ["snowflake data warehouse"],
    "delta lake": ["delta lake"],
    "apache flink": ["flink", "apache flink"],
    "data warehousing": ["data warehouse", "data warehousing"],
    "data lake": ["data lake", "data lakehouse"],
    "lakehouse": ["data lakehouse", "lake house"],

    # ----------------------------------------------------------
    # APIs / Backend
    # ----------------------------------------------------------
    "rest api": ["restful api", "rest apis", "restful apis", "rest api development", "rest services", "rest web services"],
    "graphql": ["graphql api", "graphql apis"],
    "grpc": ["grpc api", "grpc services", "remote procedure call"],
    "api development": ["api design", "api development", "web api"],
    "api integration": ["api integrations", "third party api integration", "third-party api integration", "service integration"],
    "webhooks": ["webhook", "webhooks integration"],
    "backend development": ["backend engineering", "server side development", "server-side development"],
    "flask": ["flask framework", "python flask"],
    "django": ["django framework", "python django"],
    "fastapi": ["fast api", "python fastapi"],
    "node.js": ["nodejs", "node js"],
    "express.js": ["expressjs", "express js"],
    "spring boot": ["springboot", "spring boot framework"],
    "spring": ["spring framework"],
    "microservices": ["microservice architecture", "microservices architecture", "microservice based architecture"],
    "web services": ["web service", "web services"],
    "serverless": ["serverless computing", "serverless architecture"],

    # ----------------------------------------------------------
    # Frontend / Web
    # ----------------------------------------------------------
    "frontend development": ["front end development", "frontend engineering", "front-end development"],
    "react": ["reactjs", "react js"],
    "next.js": ["nextjs", "next js"],
    "angular": ["angularjs", "angular js"],
    "vue.js": ["vue", "vuejs", "vue js"],
    "svelte": ["svelte js"],
    "html": ["html5", "hypertext markup language"],
    "css": ["css3", "cascading style sheets"],
    "tailwind css": ["tailwindcss", "tailwind"],
    "bootstrap": ["bootstrap css", "bootstrap framework"],
    "jquery": ["jquery js"],
    "ajax": ["asynchronous javascript and xml"],
    "responsive web design": ["responsive design"],

    # ----------------------------------------------------------
    # Cloud
    # ----------------------------------------------------------
    "aws": ["amazon web services", "aws cloud", "amazon aws"],
    "azure": ["microsoft azure", "azure cloud"],
    "gcp": ["google cloud", "google cloud platform"],
    "cloud computing": ["cloud technology", "cloud services", "cloud platforms"],
    "cloud infrastructure": ["cloud architecture", "cloud environment"],
    "aws lambda": ["lambda functions", "amazon lambda"],
    "amazon s3": ["s3", "amazon s3"],
    "azure functions": ["azure function", "azure serverless"],
    "azure openai": ["azure openai service"],
    "google vertex ai": ["vertex ai", "google vertex ai"],
    "google cloud run": ["cloud run", "google cloud run"],
    "cloud security": ["cloud cybersecurity", "cloud security engineering"],

    # ----------------------------------------------------------
    # DevOps / Platform / CI-CD
    # ----------------------------------------------------------
    "docker": ["docker containers", "docker containerization"],
    "kubernetes": ["k8s", "kubernetes orchestration"],
    "containerization": ["containerisation", "containerized applications", "containerised applications"],
    "helm": ["helm charts", "helm kubernetes"],
    "terraform": ["terraform infrastructure", "infrastructure as code terraform"],
    "infrastructure as code": ["iac", "infrastructure-as-code"],
    "ansible": ["ansible automation"],
    "ci/cd": ["cicd", "continuous integration", "continuous delivery", "continuous deployment", "ci cd", "ci/cd pipelines"],
    "github actions": ["github workflows", "github actions workflows"],
    "jenkins": ["jenkins ci", "jenkins pipeline"],
    "gitlab ci": ["gitlab pipelines", "gitlab cicd", "gitlab ci/cd"],
    "devops": ["dev ops", "devops engineering", "development operations"],
    "platform engineering": ["platform engineer", "internal developer platform", "idp"],
    "site reliability engineering": ["sre", "site reliability engineering"],
    "github": ["github repositories", "github platform"],
    "git": ["git version control", "distributed version control"],
    "gitlab": ["gitlab repositories", "gitlab platform"],
    "bitbucket": ["bitbucket repositories"],
    "version control": ["source control", "version control systems", "vcs"],

    # ----------------------------------------------------------
    # Observability
    # ----------------------------------------------------------
    "observability": ["application observability", "system observability", "cloud observability"],
    "monitoring": ["application monitoring", "system monitoring", "infrastructure monitoring"],
    "prometheus": ["prometheus monitoring"],
    "grafana": ["grafana dashboards", "grafana monitoring"],
    "opentelemetry": ["open telemetry", "otel"],
    "logging": ["application logging", "centralized logging", "centralised logging"],
    "elk stack": ["elasticsearch logstash kibana", "elastic stack"],

    # ----------------------------------------------------------
    # Testing / Quality
    # ----------------------------------------------------------
    "unit testing": ["unit tests", "unit test automation"],
    "integration testing": ["integration tests", "integration test automation"],
    "pytest": ["python pytest", "pytest framework"],
    "selenium": ["selenium webdriver", "selenium testing"],
    "cypress": ["cypress testing", "cypress automation"],
    "postman": ["postman api testing", "postman testing"],
    "test automation": ["automated testing", "test automation"],
    "quality assurance": ["qa", "quality assurance"],
    "performance testing": ["load testing", "stress testing"],

    # ----------------------------------------------------------
    # Software Engineering
    # ----------------------------------------------------------
    "object oriented programming": ["oop", "object-oriented programming", "object oriented design"],
    "data structures": ["data structures and algorithms", "dsa"],
    "algorithms": ["algorithm design", "data structures and algorithms", "dsa"],
    "system design": ["software architecture", "system architecture", "distributed system design"],
    "distributed systems": ["distributed system", "distributed computing"],
    "software development": ["software engineering", "software development"],
    "design patterns": ["software design patterns"],
    "clean code": ["clean coding"],
    "technical documentation": ["technical documentation", "software documentation"],

    # ----------------------------------------------------------
    # Security
    # ----------------------------------------------------------
    "cybersecurity": ["cyber security", "information security", "infosec"],
    "application security": ["appsec", "application security engineering"],
    "network security": ["network cybersecurity", "network security"],
    "zero trust security": ["zero trust", "zero-trust"],
    "identity and access management": ["iam", "identity access management"],
    "authentication": ["user authentication", "identity authentication"],
    "authorization": ["access control", "user authorization"],
    "oauth": ["oauth2", "oauth 2.0"],
    "jwt": ["json web token", "json web tokens"],
    "devsecops": ["dev sec ops", "devsecops"],
    "threat intelligence": ["cyber threat intelligence", "threat intel"],
    "security operations": ["soc", "security operations center", "security operations centre"],
    "vulnerability management": ["vulnerability assessment"],
    "penetration testing": ["pen testing", "pentesting"],
    "encryption": ["data encryption"],
    "cryptography": ["crypto", "cryptographic algorithms"],

    # ----------------------------------------------------------
    # Automation / Productivity
    # ----------------------------------------------------------
    "ai workflow automation": ["ai automation", "intelligent automation", "ai-powered automation", "ai workflow"],
    "workflow automation": ["business process automation", "process automation"],
    "microsoft copilot": ["ms copilot", "copilot for microsoft"],
    "power automate": ["microsoft power automate"],
    "zapier": ["zapier automation"],
    "n8n": ["n8n automation"],

    # ----------------------------------------------------------
    # Microsoft / Collaboration / Business Ops
    # ----------------------------------------------------------
    "microsoft teams": ["ms teams", "teams"],
    "sharepoint": ["microsoft sharepoint"],
    "learning management systems": ["lms", "learning management system"],
    "reporting": ["management reporting", "operational reporting"],
    "kpi reporting": ["kpi reports", "key performance indicator reporting"],
    "process improvement": ["continuous improvement", "process optimization", "process optimisation"],
    "requirements gathering": ["requirements analysis", "business requirements"],
    "stakeholder management": ["stakeholder engagement", "stakeholder coordination"],
    "project management": ["project coordination", "project delivery"],
    "documentation": ["business documentation", "technical documentation"],

    # ----------------------------------------------------------
    # Agile / Delivery
    # ----------------------------------------------------------
    "agile": ["agile methodology", "agile development", "agile software development"],
    "scrum": ["scrum methodology", "scrum framework"],
    "kanban": ["kanban methodology", "kanban framework"],
    "jira": ["atlassian jira", "jira software"],
    "confluence": ["atlassian confluence"],

    # ----------------------------------------------------------
    # Professional / Human Skills
    # ----------------------------------------------------------
    "problem solving": ["problem-solving", "analytical problem solving"],
    "analytical thinking": ["analytical skills", "analytical thinking"],
    "critical thinking": ["critical thinking"],
    "communication": ["communication skills", "written communication", "verbal communication"],
    "collaboration": ["team collaboration", "cross-functional collaboration"],
    "leadership": ["leadership skills", "team leadership"],
    "creative thinking": ["creative problem solving", "creative thinking"],
    "adaptability": ["adaptable", "adaptability"],
    "resilience": ["resilience", "resilience and flexibility"],
    "attention to detail": ["detail oriented", "attention-to-detail"],
    "time management": ["time-management", "time management skills"],
    "prioritization": ["task prioritization", "work prioritization"],
    "curiosity and lifelong learning": ["continuous learning", "lifelong learning", "learning agility"],
    "systems thinking": ["system thinking", "systems thinking"],
    "customer service": ["customer support", "service orientation"],
    "presentation skills": ["presentation", "presentation skills"],

    # ----------------------------------------------------------
    # Emerging / Specialized
    # ----------------------------------------------------------
    "robotics": ["robotics engineering"],
    "internet of things": ["iot", "internet of things"],
    "edge computing": ["edge technology", "edge computing"],
    "quantum computing": ["quantum technology", "quantum computing"],
    "blockchain": ["block chain", "blockchain technology"],
    "smart contracts": ["smart contract development"],
}


# ============================================================
# Normalization / Canonicalization
# ============================================================

def normalize(skill: str) -> str:
    """Normalize a skill for reliable comparison."""
    skill = str(skill).lower().strip()
    skill = skill.replace("&", "and")
    skill = skill.replace("–", "-").replace("—", "-")
    skill = re.sub(r"[\u2018\u2019]", "'", skill)
    skill = re.sub(r"\s+", " ", skill)
    skill = re.sub(r"[-_/]+", " ", skill)
    skill = re.sub(r"[^\w\s+#.+]", "", skill)
    return skill.strip()


def build_alias_index():
    """Map canonical skills and aliases to their canonical skill."""
    index = {}

    for canonical, aliases in SKILL_EQUIVALENCES.items():
        index[normalize(canonical)] = canonical

        for alias in aliases:
            index[normalize(alias)] = canonical

    return index


ALIAS_INDEX = build_alias_index()


def canonicalize_skill(skill):
    """Return the canonical name when the skill is known."""
    key = normalize(skill)
    return ALIAS_INDEX.get(key, str(skill).strip())


def canonicalize_list(skills):
    result = []
    seen = set()

    for skill in skills or []:
        canonical = canonicalize_skill(skill)

        if not canonical:
            continue

        key = normalize(canonical)

        if key not in seen:
            seen.add(key)
            result.append(canonical)

    return result


# ============================================================
# Deterministic Skill Extraction
#
# This is the important fallback. Even if Gemini fails, obvious
# skills can still be extracted from the resume/JD.
# ============================================================

def extract_dictionary_skills(text):
    if not text:
        return []

    found = []
    lower_text = text.lower()

    # Longer aliases first reduces accidental overlap.
    candidates = []

    for canonical, aliases in SKILL_EQUIVALENCES.items():
        candidates.append((canonical, canonical))
        candidates.extend((alias, canonical) for alias in aliases)

    candidates.sort(key=lambda x: len(x[0]), reverse=True)

    for alias, canonical in candidates:
        alias = str(alias).strip()

        # Avoid dangerous tiny aliases such as "ai", "ml", "js",
        # "go", etc. Gemini can still return these contextually.
        if len(normalize(alias)) < 3:
            continue

        escaped = re.escape(alias.lower())

        # Word-boundary matching for normal terms.
        # For terms containing punctuation, use a whitespace-aware
        # boundary so C++, C#, Node.js, Next.js, etc. still work.
        pattern = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"

        if re.search(pattern, lower_text):
            found.append(canonical)

    return canonicalize_list(found)


# ============================================================
# Gemini Skill Extraction
# ============================================================

def extract_skills(resume_text, jd_text):
    """
    Extract skills using both deterministic dictionary matching
    and Gemini contextual extraction.

    Gemini is an enrichment layer, not a single point of failure.
    """

    resume_text = resume_text or ""
    jd_text = jd_text or ""

    resume_excerpt = resume_text[:MAX_SKILL_TEXT]
    jd_excerpt = jd_text[:MAX_SKILL_TEXT]

    # Always extract obvious skills locally first.
    resume_dictionary = extract_dictionary_skills(resume_text)
    jd_dictionary = extract_dictionary_skills(jd_text)

    prompt = f"""
You are an expert ATS and technical recruiting skill extractor.

Extract skills from BOTH documents.

Return ONLY valid JSON:
{{
  "resume_skills": [],
  "jd_skills": []
}}

Rules:
1. Extract explicit and strongly implied professional skills.
2. Include programming languages, frameworks, libraries, databases,
   cloud, DevOps, cybersecurity, AI/ML, GenAI, LLM, data analytics,
   BI, automation, APIs, testing and relevant business skills.
3. Recognize abbreviations and equivalents:
   JS=JavaScript, ML=Machine Learning, GenAI=Generative AI,
   LLM=Large Language Models, NLP=Natural Language Processing,
   K8s=Kubernetes, AWS=Amazon Web Services.
4. If a technology is clearly demonstrated by an action, infer it:
   "built Flask APIs" -> Flask, REST API
   "used pandas for analysis" -> Pandas, Data Analysis
   "built a RAG pipeline" -> RAG, Embeddings, LLM
5. Do NOT invent skills without textual evidence.
6. Do NOT include job titles, company names, degrees or generic nouns
   unless they represent an actual professional skill.
7. Do not duplicate skills.
8. Use standard professional skill names.
9. Return arrays only. No markdown. No explanation.

RESUME:
{resume_excerpt}

JOB DESCRIPTION:
{jd_excerpt}
"""

    gemini_resume = []
    gemini_jd = []
    gemini_error = None

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        data = extract_json(response.text)

        gemini_resume = data.get("resume_skills", [])
        gemini_jd = data.get("jd_skills", [])

        if not isinstance(gemini_resume, list):
            gemini_resume = []

        if not isinstance(gemini_jd, list):
            gemini_jd = []

    except Exception as exc:
        # Do NOT convert the whole extraction to an unexplained 0.
        gemini_error = f"{type(exc).__name__}: {exc}"
        print(f"Gemini skill extraction failed: {gemini_error}")

    # Merge dictionary + Gemini results.
    resume_skills = canonicalize_list(resume_dictionary + gemini_resume)
    jd_skills = canonicalize_list(jd_dictionary + gemini_jd)

    result = {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills
    }

    # Useful for debugging without breaking the frontend.
    if gemini_error:
        result["extraction_warning"] = gemini_error

    return result


# ============================================================
# Skill Matching
# ============================================================

def is_full_match(resume_skill, jd_skill):
    r = canonicalize_skill(resume_skill)
    j = canonicalize_skill(jd_skill)

    return normalize(r) == normalize(j)


def is_partial_match(resume_skill, jd_skill):
    r = normalize(canonicalize_skill(resume_skill))
    j = normalize(canonicalize_skill(jd_skill))

    if not r or not j or r == j:
        return False

    # Token overlap rather than raw substring matching.
    # This prevents false matches such as Java -> JavaScript.
    r_tokens = set(r.split())
    j_tokens = set(j.split())

    if not r_tokens or not j_tokens:
        return False

    overlap = len(r_tokens & j_tokens) / min(len(r_tokens), len(j_tokens))

    return overlap >= 0.5


def semantic_skill_matching(resume_skills, jd_skills):
    analysis = []
    matched = []
    partial = []
    missing = []

    resume_skills = canonicalize_list(resume_skills)
    jd_skills = canonicalize_list(jd_skills)

    for jd in jd_skills:
        found = False

        # Full match.
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

        if found:
            continue

        # Partial match.
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

    similarity_score = (
        int(((full_score + partial_score) / total) * 100)
        if total else 0
    )

    return {
        "analysis": analysis,
        "matched_skills": matched,
        "partial_matches": partial,
        "missing_skills": missing,
        "similarity_score": min(100, similarity_score)
    }


# ============================================================
# Experience + Project Evaluation
# ============================================================

def evaluate_experience_and_projects(resume_text, jd_text):
    prompt = f"""
Evaluate the resume against the job description.

Return ONLY valid JSON:
{{
  "experience_score": 0,
  "project_score": 0,
  "improvements": [],
  "summary": ""
}}

Rules:
- Score experience relevance from 0-100.
- Score project relevance from 0-100.
- Base scores only on evidence in the resume.
- Do not invent experience.
- Improvements must be specific and actionable.
- Keep the summary concise.

RESUME:
{(resume_text or "")[:MAX_EVAL_TEXT]}

JOB DESCRIPTION:
{(jd_text or "")[:MAX_EVAL_TEXT]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        result = extract_json(response.text)

        return {
            "experience_score": max(0, min(100, int(result.get("experience_score", 0)))),
            "project_score": max(0, min(100, int(result.get("project_score", 0)))),
            "improvements": result.get("improvements", [])
            if isinstance(result.get("improvements", []), list) else [],
            "summary": str(result.get("summary", ""))
        }

    except Exception as exc:
        print(f"Experience/project evaluation failed: {type(exc).__name__}: {exc}")

        return {
            "experience_score": 0,
            "project_score": 0,
            "improvements": [
                "Experience/project evaluation could not be completed."
            ],
            "summary": "Skill matching was completed, but AI-based experience evaluation failed."
        }


# ============================================================
# Final ATS Analysis
# ============================================================

def analyze_resume_jobdesc(resume_text, jd_text):

    skills = extract_skills(resume_text, jd_text)

    resume_skills = skills.get("resume_skills", [])
    jd_skills = skills.get("jd_skills", [])

    skill_result = semantic_skill_matching(
        resume_skills,
        jd_skills
    )

    exp_result = evaluate_experience_and_projects(
        resume_text,
        jd_text
    )

    skill_score = skill_result["similarity_score"]
    exp_score = int(exp_result.get("experience_score", 0))
    proj_score = int(exp_result.get("project_score", 0))

    final_ats = round(
        skill_score * 0.70 +
        exp_score * 0.20 +
        proj_score * 0.10
    )

    result = {
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

    if skills.get("extraction_warning"):
        result["extraction_warning"] = skills["extraction_warning"]

    return result


# ============================================================
# Chat Feature
# ============================================================

def gemini_chat(resume_text, jd_text, user_msg):

    prompt = f"""
You are an ATS resume and career assistant.

Answer the user's question specifically using the resume and job
description below.

Be concise, accurate and actionable.
Do not invent experience or skills.

RESUME:
{(resume_text or "")[:6000]}

JOB DESCRIPTION:
{(jd_text or "")[:6000]}

QUESTION:
{(user_msg or "")[:1000]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text or "No response generated."

    except Exception as exc:
        print(f"Chat failed: {type(exc).__name__}: {exc}")
        return f"Chat failed: {type(exc).__name__}: {exc}"

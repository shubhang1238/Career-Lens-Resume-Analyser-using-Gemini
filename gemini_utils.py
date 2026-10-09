"""

gemini_utils.py

ATS Resume/JD analyzer using Google Gemini + deterministic skill extraction.



Required environment variables:

    GEMINI_API_KEY

Optional:

    GEMINI_MODEL (default: gemini-3.8-flash)

    MAX_SKILL_TEXT (default: 30000)

    MAX_EVAL_TEXT (default: 20000)

"""

import os

import re

import json

from dotenv import load_dotenv

from google import genai

from google.genai import types

load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it to Vercel Environment Variables."
    )


MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

MAX_SKILL_TEXT = int(os.getenv("MAX_SKILL_TEXT", "30000"))

MAX_EVAL_TEXT = int(os.getenv("MAX_EVAL_TEXT", "20000"))


client = genai.Client(api_key=API_KEY)


def normalize(skill):
    """Normalize skill text for comparison."""

    if skill is None:

        return ""

    s = str(skill).lower().strip()

    s = s.replace("&", " and ")

    s = s.replace("–", "-").replace("—", "-")

    s = re.sub(r"[\u2018\u2019]", "'", s)

    s = re.sub(r"\s+", " ", s)

    s = re.sub(r"[-_/]+", " ", s)

    s = re.sub(r"[^\w\s+#.]", "", s)

    return s.strip()


def unique_clean(values):

    result = []

    seen = set()

    for value in values or []:

        if value is None:

            continue

        value = re.sub(r"\s+", " ", str(value).strip())

        if not value:

            continue

        key = normalize(value)

        if key and key not in seen:

            seen.add(key)

            result.append(value)

    return result


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
    "prompt engineering": ["prompt design", "prompt optimization", "prompting"],
    "prompt evaluation": ["prompt testing", "prompt evaluation"],
    "ai agents": [
        "ai agent",
        "agentic ai",
        "agentic systems",
        "autonomous agents",
        "llm agents",
        "agent development",
    ],
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
    "fine tuning": [
        "fine-tuning",
        "model fine tuning",
        "llm fine tuning",
        "parameter efficient fine tuning",
        "peft",
    ],
    "retrieval augmented generation": [
        "rag",
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
    "data pipelines": [
        "data pipeline",
        "data processing pipelines",
        "data engineering pipelines",
    ],
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
    "api development": ["api design", "api development", "web api"],
    "api integration": [
        "api integrations",
        "third party api integration",
        "third-party api integration",
        "service integration",
    ],
    "webhooks": ["webhook", "webhooks integration"],
    "backend development": [
        "backend engineering",
        "server side development",
        "server-side development",
    ],
    "flask": ["flask framework", "python flask"],
    "django": ["django framework", "python django"],
    "fastapi": ["fast api", "python fastapi"],
    "node.js": ["nodejs", "node js"],
    "express.js": ["expressjs", "express js"],
    "spring boot": ["springboot", "spring boot framework"],
    "spring": ["spring framework"],
    "microservices": [
        "microservice architecture",
        "microservices architecture",
        "microservice based architecture",
    ],
    "web services": ["web service", "web services"],
    "serverless": ["serverless computing", "serverless architecture"],
    # ----------------------------------------------------------
    # Frontend / Web
    # ----------------------------------------------------------
    "frontend development": [
        "front end development",
        "frontend engineering",
        "front-end development",
    ],
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
    "containerization": [
        "containerisation",
        "containerized applications",
        "containerised applications",
    ],
    "helm": ["helm charts", "helm kubernetes"],
    "terraform": ["terraform infrastructure", "infrastructure as code terraform"],
    "infrastructure as code": ["iac", "infrastructure-as-code"],
    "ansible": ["ansible automation"],
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
    "security operations": [
        "soc",
        "security operations center",
        "security operations centre",
    ],
    "vulnerability management": ["vulnerability assessment"],
    "penetration testing": ["pen testing", "pentesting"],
    "encryption": ["data encryption"],
    "cryptography": ["crypto", "cryptographic algorithms"],
    # ----------------------------------------------------------
    # Automation / Productivity
    # ----------------------------------------------------------
    "ai workflow automation": [
        "ai automation",
        "intelligent automation",
        "ai-powered automation",
        "ai workflow",
    ],
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
    "process improvement": [
        "continuous improvement",
        "process optimization",
        "process optimisation",
    ],
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
    "communication": [
        "communication skills",
        "written communication",
        "verbal communication",
    ],
    "collaboration": ["team collaboration", "cross-functional collaboration"],
    "leadership": ["leadership skills", "team leadership"],
    "creative thinking": ["creative problem solving", "creative thinking"],
    "adaptability": ["adaptable", "adaptability"],
    "resilience": ["resilience", "resilience and flexibility"],
    "attention to detail": ["detail oriented", "attention-to-detail"],
    "time management": ["time-management", "time management skills"],
    "prioritization": ["task prioritization", "work prioritization"],
    "curiosity and lifelong learning": [
        "continuous learning",
        "lifelong learning",
        "learning agility",
    ],
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


# Build canonical alias lookup once.

ALIAS_INDEX = {}

for canonical, aliases in SKILL_EQUIVALENCES.items():

    ALIAS_INDEX[normalize(canonical)] = canonical

    for alias in aliases:

        ALIAS_INDEX[normalize(alias)] = canonical


def canonicalize_skill(skill):

    value = str(skill).strip()

    return ALIAS_INDEX.get(normalize(value), value)


def canonicalize_list(skills):

    result = []

    seen = set()

    for skill in skills or []:

        canonical = canonicalize_skill(skill)

        key = normalize(canonical)

        if key and key not in seen:

            seen.add(key)

            result.append(canonical)

    return result


def extract_dictionary_skills(text):
    """

    Local extraction. This guarantees useful output even if Gemini is

    unavailable, rate-limited, returns invalid JSON, or the API key fails.

    """

    if not text:

        return []

    text_lower = text.lower()

    found = []

    candidates = []

    for canonical, aliases in SKILL_EQUIVALENCES.items():

        candidates.append((canonical, canonical))

        candidates.extend((alias, canonical) for alias in aliases)

    # Longest first.
    candidates.sort(key=lambda x: len(normalize(x[0])), reverse=True)

    for alias, canonical in candidates:

        alias = str(alias).strip()

        normalized_alias = normalize(alias)

        # Skip very short aliases because they cause false positives.
        if len(normalized_alias) < 3:

            continue

        # Special handling for aliases containing regex punctuation.
        escaped = re.escape(alias.lower())

        pattern = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"

        if re.search(pattern, text_lower):

            found.append(canonical)

    return canonicalize_list(found)


def _json_schema():

    return {
        "type": "OBJECT",
        "properties": {
            "resume_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
            "jd_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["resume_skills", "jd_skills"],
    }


def extract_skills(resume_text, jd_text):
    """

    Hybrid extraction:

      1. Deterministic dictionary matching always runs.

      2. Gemini 3.8 Flash enriches contextual/implicit skills.

      3. Results are merged and canonicalized.

    """

    resume_text = resume_text or ""

    jd_text = jd_text or ""

    # Local extraction is independent of Gemini.
    resume_local = extract_dictionary_skills(resume_text)

    jd_local = extract_dictionary_skills(jd_text)

    prompt = f"""

You are an expert ATS resume and job-description skill extractor.



Extract professional skills from BOTH documents.



Return ONLY the requested JSON structure.



Rules:

- Extract skills explicitly supported by the text.

- Extract programming languages, frameworks, libraries, databases,

  cloud platforms, DevOps, cybersecurity, AI/ML, GenAI, LLM,

  data analytics, BI, APIs, testing, automation and relevant

  professional/business skills.

- Recognize common abbreviations:

  JS=JavaScript, ML=Machine Learning, GenAI=Generative AI,

  LLM=Large Language Models, NLP=Natural Language Processing,

  K8s=Kubernetes, AWS=Amazon Web Services.

- Infer a skill only when the action clearly supports it.

  Example: "built Flask APIs" -> Flask, REST API.

- Do not invent skills.

- Do not include job titles, company names, degrees, locations,

  responsibilities or generic nouns as skills.

- Do not duplicate skills.

- Use standard professional skill names.



RESUME:

{resume_text[:MAX_SKILL_TEXT]}



JOB DESCRIPTION:

{jd_text[:MAX_SKILL_TEXT]}

"""

    gemini_resume = []

    gemini_jd = []

    warning = None

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=_json_schema(),
            ),
        )

        # Structured output should already be JSON.
        raw = response.text or ""

        if not raw.strip():

            raise ValueError("Gemini returned an empty skill-extraction response.")

        data = json.loads(raw)

        gemini_resume = data.get("resume_skills", [])

        gemini_jd = data.get("jd_skills", [])

        if not isinstance(gemini_resume, list):

            gemini_resume = []

        if not isinstance(gemini_jd, list):

            gemini_jd = []

    except Exception as exc:

        warning = f"Gemini skill extraction failed: {type(exc).__name__}: {exc}"

        print(warning)

    # IMPORTANT: local extraction remains even if Gemini fails.
    resume_skills = canonicalize_list(resume_local + gemini_resume)

    jd_skills = canonicalize_list(jd_local + gemini_jd)

    result = {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "extraction_source": (
            "dictionary+gemini" if not warning else "dictionary_fallback"
        ),
    }

    if warning:

        result["extraction_warning"] = warning

    return result


def is_full_match(resume_skill, jd_skill):

    return normalize(canonicalize_skill(resume_skill)) == normalize(
        canonicalize_skill(jd_skill)
    )


def is_partial_match(resume_skill, jd_skill):

    r = normalize(canonicalize_skill(resume_skill))

    j = normalize(canonicalize_skill(jd_skill))

    if not r or not j or r == j:

        return False

    r_tokens = set(r.split())

    j_tokens = set(j.split())

    if not r_tokens or not j_tokens:

        return False

    overlap = len(r_tokens & j_tokens) / min(len(r_tokens), len(j_tokens))

    return overlap >= 0.5


def _skill_weight(skill):
    """Weight JD skills so core technical requirements matter more than generic soft skills."""
    key = normalize(canonicalize_skill(skill))

    soft = {
        "communication",
        "collaboration",
        "leadership",
        "adaptability",
        "resilience",
        "problem solving",
        "analytical thinking",
        "critical thinking",
        "creative thinking",
        "attention to detail",
        "time management",
        "prioritization",
        "presentation skills",
        "curiosity and lifelong learning",
        "systems thinking",
        "customer service",
    }

    common = {
        "documentation",
        "reporting",
        "agile",
        "scrum",
        "kanban",
        "project management",
        "requirements gathering",
        "stakeholder management",
        "process improvement",
    }

    if key in soft:
        return 0.45
    if key in common:
        return 0.65
    return 1.0


def _related_skill_score(resume_skill, jd_skill):
    """Return 0..1 similarity for skills that are not exact aliases."""
    r = normalize(canonicalize_skill(resume_skill))
    j = normalize(canonicalize_skill(jd_skill))

    if not r or not j:
        return 0.0
    if r == j:
        return 1.0

    # Strong token overlap for compound skills.
    rt = set(r.split())
    jt = set(j.split())
    if rt and jt:
        overlap = len(rt & jt) / max(1, min(len(rt), len(jt)))
        if overlap >= 0.75:
            return 0.75
        if overlap >= 0.5 and len(rt) > 1 and len(jt) > 1:
            return 0.55

    # Fuzzy comparison for spelling/format variants that escaped alias matching.
    from difflib import SequenceMatcher

    ratio = SequenceMatcher(None, r, j).ratio()
    if ratio >= 0.88:
        return 0.65

    return 0.0


def semantic_skill_matching(resume_skills, jd_skills):
    """
    Weighted skill alignment.

    Exact canonical/alias matches receive full credit.
    Strong related matches receive partial credit.
    Generic soft skills have lower weight so a JD containing many soft skills
    does not unfairly crush an otherwise strong technical match.
    """
    resume_skills = canonicalize_list(resume_skills)
    jd_skills = canonicalize_list(jd_skills)

    analysis = []
    matched = []
    partial = []
    missing = []
    total_weight = 0.0
    earned_weight = 0.0

    for jd in jd_skills:
        weight = _skill_weight(jd)
        total_weight += weight

        best_score = 0.0
        best_resume = ""

        for rs in resume_skills:
            score = _related_skill_score(rs, jd)
            if score > best_score:
                best_score = score
                best_resume = rs
                if score >= 1.0:
                    break

        if best_score >= 0.99:
            status = "Full Match"
            confidence = "High"
            matched.append(jd)
            earned_weight += weight
        elif best_score >= 0.50:
            status = "Partial Match"
            confidence = "Medium"
            partial.append(jd)
            earned_weight += weight * best_score
        else:
            status = "Missing"
            confidence = "Low"
            missing.append(jd)

        analysis.append(
            {
                "jd_skill": jd,
                "status": status,
                "resume_evidence": best_resume,
                "confidence": confidence,
                "weight": weight,
                "match_score": round(best_score * 100),
            }
        )

    similarity_score = (
        round((earned_weight / total_weight) * 100) if total_weight else 0
    )

    return {
        "analysis": analysis,
        "matched_skills": matched,
        "partial_matches": partial,
        "missing_skills": missing,
        "similarity_score": min(100, max(0, similarity_score)),
        "match_counts": {
            "full": len(matched),
            "partial": len(partial),
            "missing": len(missing),
            "total": len(jd_skills),
        },
    }


def _extract_json_object(text):
    """Extract a JSON object even if Gemini wraps it in markdown/code fences."""
    if not text:
        raise ValueError("Gemini returned an empty response.")

    raw = str(text).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object found in Gemini response: {raw[:300]}")
        return json.loads(match.group(0))


def _extract_resume_section(text, headings):
    """Extract a resume section between common headings."""
    if not text:
        return ""

    raw = text.replace("\r", "\n")
    heading_pattern = "|".join(re.escape(h) for h in headings)

    start_match = re.search(
        rf"(?im)^\s*(?:{heading_pattern})\s*:?\s*$",
        raw,
    )
    if not start_match:
        return ""

    remainder = raw[start_match.end() :]

    next_heading = re.search(
        r"(?im)^\s*(?:"
        r"experience|work experience|professional experience|employment|"
        r"internships?|education|projects?|technical skills|skills|"
        r"certifications?|achievements?|summary|profile|"
        r"responsibilities|publications?|awards?"
        r")\s*:?\s*$",
        remainder,
    )

    return remainder[: next_heading.start()] if next_heading else remainder


def _section_skill_coverage(section_text, jd_skills):
    if not section_text or not jd_skills:
        return 0.0

    found = 0.0
    total = 0.0
    lower = section_text.lower()

    for skill in jd_skills:
        weight = _skill_weight(skill)
        total += weight

        aliases = [skill]
        canonical = canonicalize_skill(skill)
        if canonical in SKILL_EQUIVALENCES:
            aliases += SKILL_EQUIVALENCES[canonical]

        hit = False
        for alias in aliases:
            alias = str(alias).strip().lower()
            if len(normalize(alias)) < 3:
                continue
            pattern = rf"(?<![A-Za-z0-9]){re.escape(alias)}(?![A-Za-z0-9])"
            if re.search(pattern, lower):
                hit = True
                break

        if hit:
            found += weight

    return (found / total) * 100 if total else 0.0


def _fallback_experience_project_score(
    resume_text, jd_text, resume_skills=None, jd_skills=None
):
    """
    Evidence-based local evaluator.

    Unlike the previous fallback, experience and projects are scored against
    the relevant resume sections instead of using only keyword counts.
    """
    resume = resume_text or ""
    jd_skills = canonicalize_list(jd_skills or [])
    resume_skills = canonicalize_list(resume_skills or [])

    if not resume.strip():
        return 0, 0

    experience_section = _extract_resume_section(
        resume,
        [
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "internship",
            "internships",
        ],
    )
    project_section = _extract_resume_section(
        resume,
        ["projects", "project experience", "academic projects", "personal projects"],
    )

    # If headings cannot be detected, use the full resume with a confidence cap.
    exp_coverage = _section_skill_coverage(experience_section or resume, jd_skills)
    proj_coverage = _section_skill_coverage(project_section or resume, jd_skills)

    resume_lower = resume.lower()

    exp_signals = sum(
        1
        for x in [
            "experience",
            "worked",
            "responsible",
            "developed",
            "implemented",
            "engineer",
            "developer",
            "analyst",
            "intern",
            "employment",
        ]
        if x in resume_lower
    )
    project_signals = sum(
        1
        for x in [
            "project",
            "built",
            "developed",
            "implemented",
            "created",
            "deployed",
            "application",
            "dashboard",
            "api",
            "system",
        ]
        if x in resume_lower
    )

    # Additional evidence from matched skills, but only as a secondary factor.
    rs = {normalize(x) for x in resume_skills if normalize(x)}
    js = {normalize(x) for x in jd_skills if normalize(x)}
    overall_overlap = (len(rs & js) / len(js) * 100) if js else 0

    # Evidence-based fallback. Keep the scores meaningful even when the resume
    # does not use conventional section headings.
    experience_score = round(
        exp_coverage * 0.68 + overall_overlap * 0.22 + min(exp_signals, 10) * 1.0
    )
    project_score = round(
        proj_coverage * 0.68 + overall_overlap * 0.22 + min(project_signals, 10) * 1.0
    )

    # Dedicated sections are stronger evidence, but do not discard useful
    # whole-resume evidence when a heading is absent.
    if experience_section:
        experience_score = round(exp_coverage * 0.75 + overall_overlap * 0.25)
    if project_section:
        project_score = round(proj_coverage * 0.75 + overall_overlap * 0.25)

    return (
        max(0, min(100, experience_score)),
        max(0, min(100, project_score)),
    )


def evaluate_experience_and_projects(
    resume_text, jd_text, resume_skills=None, jd_skills=None
):
    """Evaluate experience/project relevance with Gemini and a deterministic fallback."""
    prompt = f"""
You are an expert ATS resume evaluator and recruiter.

Compare the RESUME against the JOB DESCRIPTION.

Return JSON only with:
- experience_score: integer 0-100
- project_score: integer 0-100
- improvements: array of 3-6 concise strings
- summary: concise recruiter-friendly string

Rules:
- Score actual evidence in the resume, not assumptions.
- Equivalent technologies and transferable experience count when supported.
- Do not invent employers, technologies, projects, responsibilities or achievements.
- Experience Fit measures employment/internship relevance.
- Project Fit measures project relevance.
- A candidate with relevant evidence should not receive 0 merely because section headings differ.

RESUME:
{(resume_text or "")[:MAX_EVAL_TEXT]}

JOB DESCRIPTION:
{(jd_text or "")[:MAX_EVAL_TEXT]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "experience_score": {"type": "INTEGER"},
                        "project_score": {"type": "INTEGER"},
                        "improvements": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                        },
                        "summary": {"type": "STRING"},
                    },
                    "required": [
                        "experience_score",
                        "project_score",
                        "improvements",
                        "summary",
                    ],
                },
            ),
        )

        result = json.loads(response.text or "{}")
        experience_score = max(0, min(100, int(result.get("experience_score", 0))))
        project_score = max(0, min(100, int(result.get("project_score", 0))))

        improvements = result.get("improvements", [])
        if not isinstance(improvements, list):
            improvements = [str(improvements)] if improvements else []
        improvements = [str(x).strip() for x in improvements if str(x).strip()]

        summary = str(result.get("summary", "")).strip()
        if not summary:
            summary = (
                "Your experience and projects were evaluated against the role "
                "requirements using evidence from the submitted resume."
            )

        return {
            "experience_score": experience_score,
            "project_score": project_score,
            "improvements": improvements[:6],
            "summary": summary,
            "evaluation_source": "gemini",
        }

    except Exception as exc:
        print(
            f"Experience/project Gemini evaluation failed: "
            f"{type(exc).__name__}: {exc}"
        )

        experience_score, project_score = _fallback_experience_project_score(
            resume_text, jd_text, resume_skills, jd_skills
        )

        return {
            "experience_score": experience_score,
            "project_score": project_score,
            "improvements": [
                "Add the most important JD technologies to relevant experience bullets.",
                "Quantify project impact with measurable results.",
                "Use JD terminology naturally where it accurately describes your work.",
            ],
            "summary": (
                "Your experience and projects were evaluated against the role "
                "requirements using evidence from the submitted resume."
            ),
            "evaluation_source": "local_fallback",
            "evaluation_warning": (
                f"Gemini evaluation unavailable: {type(exc).__name__}: {exc}"
            ),
        }


def analyze_resume_jobdesc(resume_text, jd_text):
    """Run the complete ATS analysis and return a frontend-safe payload."""
    resume_text = resume_text or ""
    jd_text = jd_text or ""

    skills = extract_skills(resume_text, jd_text)
    resume_skills = canonicalize_list(skills.get("resume_skills", []))
    jd_skills = canonicalize_list(skills.get("jd_skills", []))

    skill_result = semantic_skill_matching(resume_skills, jd_skills)

    exp_result = evaluate_experience_and_projects(
        resume_text, jd_text, resume_skills, jd_skills
    )

    skill_score = max(0, min(100, int(skill_result.get("similarity_score", 0))))
    exp_score = max(0, min(100, int(exp_result.get("experience_score", 0))))
    proj_score = max(0, min(100, int(exp_result.get("project_score", 0))))

    # Skill coverage is the primary ATS signal. Experience and project evidence
    # prevent a skills-only match from overstating the candidate's fit.
    final_ats = round(skill_score * 0.65 + exp_score * 0.20 + proj_score * 0.15)

    counts = skill_result.get("match_counts", {})
    full_count = int(counts.get("full", len(skill_result["matched_skills"])))
    partial_count = int(counts.get("partial", len(skill_result["partial_matches"])))
    missing_count = int(counts.get("missing", len(skill_result["missing_skills"])))
    total_count = int(counts.get("total", len(jd_skills)))

    if final_ats >= 85:
        score_label = "Excellent Match"
    elif final_ats >= 70:
        score_label = "Strong Match"
    elif final_ats >= 55:
        score_label = "Moderate Match"
    elif final_ats >= 40:
        score_label = "Needs Improvement"
    else:
        score_label = "Low Match"

    # Keep recruiter-facing text clean; technical API diagnostics stay in debug.
    recruiter_readout = str(exp_result.get("summary", "")).strip()
    if not recruiter_readout:
        recruiter_readout = (
            "Your experience and projects were evaluated against the role "
            "requirements using evidence from the submitted resume."
        )

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "analysis": skill_result.get("analysis", []),
        "matched_skills": skill_result.get("matched_skills", []),
        "partial_matches": skill_result.get("partial_matches", []),
        "missing_skills": skill_result.get("missing_skills", []),
        "improvements": exp_result.get("improvements", []),
        "summary": recruiter_readout,
        "recruiter_readout": recruiter_readout,
        # Existing UI supports these names; aliases keep older UI versions safe.
        "score_breakdown": {
            "skill_score": skill_score,
            "experience_score": exp_score,
            "project_score": proj_score,
            "skill_match": skill_score,
            "experience_match": exp_score,
            "project_match": proj_score,
        },
        "skill_score": skill_score,
        "experience_score": exp_score,
        "project_score": proj_score,
        "ats_score": final_ats,
        "final_ats_score": final_ats,
        "score_label": score_label,
        "chart_data": [
            {"label": "Skill Alignment", "value": skill_score},
            {"label": "Experience Fit", "value": exp_score},
            {"label": "Project Fit", "value": proj_score},
        ],
        "match_breakdown": {
            "full_match": full_count,
            "partial_match": partial_count,
            "missing": missing_count,
            "total": total_count,
        },
        "evaluation_source": exp_result.get("evaluation_source", "unknown"),
        "extraction_source": skills.get("extraction_source", "unknown"),
        "debug": {
            "resume_text_chars": len(resume_text),
            "jd_text_chars": len(jd_text),
            "resume_skill_count": len(resume_skills),
            "jd_skill_count": len(jd_skills),
            "matched_skill_count": full_count,
            "partial_skill_count": partial_count,
            "missing_skill_count": missing_count,
            "gemini_model": MODEL,
            "evaluation_source": exp_result.get("evaluation_source"),
        },
        "diagnostics": {
            "extraction_warning": skills.get("extraction_warning"),
            "evaluation_warning": exp_result.get("evaluation_warning"),
        },
    }


def gemini_chat(resume_text, jd_text, user_msg):

    prompt = f"""

You are an ATS resume and career assistant.



Answer the user's question using the resume and job description.

Be concise, accurate and actionable.

Do not invent experience or skills.



RESUME:

{(resume_text or "")[:10000]}



JOB DESCRIPTION:

{(jd_text or "")[:10000]}



QUESTION:

{(user_msg or "")[:1500]}

"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3),
        )

        return response.text or "No response generated."

    except Exception as exc:

        print(f"Chat failed: {type(exc).__name__}: {exc}")

        return f"Chat failed: {type(exc).__name__}: {exc}"

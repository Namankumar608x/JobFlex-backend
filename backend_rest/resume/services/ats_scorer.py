from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

_model = None


def get_model():
    """
    Loads sentence transformer model once at first call.
    all-MiniLM-L6-v2 is ~90MB — lightweight and fast for this use case.
    Converts text into 384-dimensional semantic vectors.
    """
    global _model
    if _model is None:
        print("Loading ATS scoring model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ── Skills taxonomy ───────────────────────────────────────────────────────
# Instead of extracting all words and trying to blacklist generic ones,
# we only match against known technical/domain skills. This eliminates
# false positives like "preferable", "therefore", "comprehend" entirely.

SKILLS_TAXONOMY = {
    # ── Programming languages ──
    "python", "java", "javascript", "typescript", "go", "golang", "rust",
    "c++", "c#", "c", "ruby", "php", "swift", "kotlin", "scala", "perl",
    "r", "matlab", "lua", "haskell", "elixir", "clojure", "dart",
    "objective-c", "assembly", "shell", "bash", "powershell", "sql",
    "nosql", "html", "css", "sass", "scss", "less",

    # ── Frameworks & libraries ──
    "django", "flask", "fastapi", "tornado", "celery",
    "spring", "spring-boot", "hibernate", "maven", "gradle",
    "react", "reactjs", "angular", "vue", "vuejs", "svelte",
    "nextjs", "next.js", "nuxt", "nuxtjs", "gatsby", "remix",
    "node", "nodejs", "node.js", "express", "expressjs",
    "rails", "ruby-on-rails", "laravel", "symfony",
    "dotnet", ".net", "asp.net", "blazor",
    "tensorflow", "pytorch", "keras", "onnx",
    "pandas", "numpy", "scipy", "scikit-learn", "matplotlib",
    "opencv", "pillow", "spark", "hadoop", "airflow", "dbt",
    "bootstrap", "tailwind", "tailwindcss", "material-ui", "antd",
    "redux", "mobx", "zustand", "rxjs", "redux-saga",
    "strapi", "sanity", "contentful", "wordpress",

    # ── Databases ──
    "postgresql", "mysql", "sqlite", "oracle", "mssql", "mariadb",
    "mongodb", "couchdb", "dynamodb", "firestore", "firebase",
    "redis", "memcached", "elasticsearch", "solr",
    "cassandra", "neo4j", "graphql", "prisma", "sequelize",
    "typeorm", "mongoose", "sqlalchemy", "alembic",
    "snowflake", "bigquery", "redshift", "databricks",

    # ── Cloud & infrastructure ──
    "aws", "azure", "gcp", "google-cloud",
    "ec2", "s3", "lambda", "rds", "cloudfront",
    "route53", "ecs", "eks", "fargate", "beanstalk",
    "cloudformation", "cdk", "sam",
    "azure-functions", "app-service", "blob-storage",
    "gke", "cloud-run", "pub/sub", "bigtable",
    "vercel", "netlify", "heroku", "digitalocean",

    # ── DevOps & CI/CD ──
    "docker", "kubernetes", "k8s", "helm",
    "terraform", "ansible", "puppet", "chef",
    "jenkins", "github-actions", "gitlab-ci", "circleci",
    "travis", "bamboo", "argocd",
    "nginx", "apache", "caddy", "traefik",
    "linux", "ubuntu", "centos", "debian",
    "prometheus", "grafana", "datadog", "newrelic", "sentry",
    "elk", "kibana", "logstash", "fluentd", "splunk",

    # ── APIs & protocols ──
    "api", "rest", "restapi", "restful", "graphql", "grpc",
    "websocket", "websockets", "soap",
    "oauth", "oauth2", "jwt", "saml", "sso", "openid",
    "swagger", "openapi", "postman",

    # ── Architecture & patterns ──
    "microservices", "monolith", "serverless", "soa",
    "event-driven", "cqrs", "event-sourcing",
    "containers", "containerization", "virtualization",
    "load-balancing", "caching", "cdn",
    "mq", "message-queue", "kafka", "rabbitmq", "activemq", "sqs",
    "pub/sub", "event-bus",

    # ── Methodologies & practices ──
    "agile", "scrum", "kanban", "xp", "safe",
    "tdd", "bdd", "ci/cd", "cicd", "devops", "devsecops",
    "git", "github", "gitlab", "bitbucket", "svn",
    "code-review", "pair-programming",

    # ── Testing ──
    "jest", "mocha", "chai", "cypress", "playwright",
    "selenium", "puppeteer", "testing-library",
    "pytest", "unittest", "nose",
    "junit", "mockito", "testng",
    "karma", "jasmine", "vitest",
    "locust", "jmeter", "k6", "artillery",

    # ── Mobile ──
    "react-native", "flutter", "xamarin", "ionic",
    "ios", "android", "swiftui", "jetpack",

    # ── Data & ML ──
    "machine-learning", "deep-learning", "nlp", "llm",
    "computer-vision", "reinforcement-learning",
    "data-engineering", "data-science", "data-analytics",
    "etl", "data-pipeline", "data-warehouse", "data-lake",
    "power-bi", "tableau", "looker",

    # ── Security ──
    "ssl", "tls", "https", "encryption", "rsa",
    "owasp", "waf", "firewall", "vpn",
    "penetration-testing", "vulnerability",

    # ── Design & tools ──
    "figma", "sketch", "adobe", "invision",
    "jira", "confluence", "notion", "slack", "trello",
    "webpack", "vite", "rollup", "babel", "eslint", "prettier",
    "storybook", "chromatic",

    # ── Domain terms ──
    "saas", "paas", "iaas",
    "fintech", "edtech", "healthtech", "ecommerce",
    "blockchain", "web3", "smart-contract",
    "iot", "embedded", "firmware",
    "automation", "orchestration",
}


def extract_skills(text: str) -> set:
    """
    Extracts only recognized technical/domain skills from text.
    Uses the skills taxonomy so generic words like 'preferable',
    'therefore', 'comprehend' are never returned.
    Handles case-insensitive matching and common variant names.
    """
    text_lower = text.lower()

    found = set()
    for skill in SKILLS_TAXONOMY:
        escaped = re.escape(skill)
        # Match whole skill only — bounded by non-alphanumeric chars
        if re.search(rf'(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])', text_lower):
            found.add(skill)

    return found


def score_resume(resume_text: str, jd_text: str) -> dict:
    """
    Scores a resume against a job description using two methods:

    1. Semantic similarity (sentence-transformers + cosine similarity)
       Captures meaning — e.g. "built REST APIs" matches "API development"
       even without exact word overlap.

    2. Skill gap analysis
       Matches against a taxonomy of known technical skills.
       Only real skills are compared — no generic filler words.

    Final ats_score is a weighted blend:
       40% semantic similarity + 60% skill match rate
    """
    model = get_model()

    # Encode both texts into vectors
    resume_vec = model.encode([resume_text])
    jd_vec = model.encode([jd_text])

    # Semantic similarity score (0 to 100)
    similarity = cosine_similarity(resume_vec, jd_vec)[0][0]
    semantic_score = max(0, (similarity - 0.4) / 0.6) * 100
    semantic_score = round(min(semantic_score, 100), 1)

    # Skill analysis — only known technical skills
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)

    matched = jd_skills & resume_skills
    missing = jd_skills - resume_skills

    # All skills from the taxonomy are technical, so equal weight
    keyword_match_rate = (len(matched) / len(jd_skills)) * 100 if jd_skills else 0
    keyword_match_rate = round(keyword_match_rate, 1)

    # Penalty for missing skills that are in the JD
    penalty = len(missing) * 3

    experience_bonus = 0

    if re.search(r'\b\d+\+?\s+years?\b', resume_text.lower()):
        experience_bonus += 5

    if "project" in resume_text.lower():
        experience_bonus += 3

    # Weighted blend for final ATS score
    ats_score = (semantic_score * 0.4) + (keyword_match_rate * 0.6)
    ats_score -= penalty
    ats_score = max(0, min(ats_score, 100))
    ats_score = round(ats_score)
    ats_score = min(100, ats_score + experience_bonus)

    # ── Suggestions ──────────────────────────────────────────────────────
    suggestions = []

    for skill in sorted(missing):
        suggestions.append(
            f"Include experience with {skill} if applicable — it's mentioned in the job description."
        )

    if len(missing) > len(matched):
        suggestions.append(
            "Your resume is missing several skills from the JD. Tailor your skills section to match the job posting."
        )

    if not re.search(r'\b\d+\+?\s+years?\b', resume_text.lower()):
        suggestions.append(
            "Add measurable experience (e.g. '3+ years of Python') to strengthen your profile."
        )

    if "project" not in resume_text.lower():
        suggestions.append(
            "Highlight specific projects that demonstrate the required skills."
        )

    suggestions.append(
        "Use action verbs: Built, Designed, Led, Optimized, Deployed to strengthen impact."
    )

    if semantic_score < 50:
        suggestions.append(
            "Your resume's overall narrative doesn't closely match the job description. "
            "Consider rewording your summary to align with the role."
        )

    # ── Strengths ───────────────────────────────────────────────────────
    strengths = sorted(list(matched))[:8]

    return {
        "ats_score": ats_score,
        "semantic_raw": similarity,
        "semantic_scaled": semantic_score,
        "keyword_score": keyword_match_rate,
        "penalty": penalty,
        "matched_keywords": sorted(list(matched)),
        "missing_keywords": sorted(list(missing)),
        "total_jd_keywords": len(jd_skills),
        "matched_count": len(matched),
        "strengths": strengths,
        "suggestions": suggestions,
    }
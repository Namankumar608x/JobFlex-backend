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


def extract_keywords(text: str) -> set:
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]{2,}\b', text.lower())

    stopwords = {
        "and", "the", "for", "with", "you", "your", "are", "have",
        "will", "this", "that", "from", "into", "about"
    }

    # Only keep meaningful tokens
    keywords = [w for w in words if w not in stopwords]

    return set(keywords)

def score_resume(resume_text: str, jd_text: str) -> dict:
    """
    Scores a resume against a job description using two methods:

    1. Semantic similarity (sentence-transformers + cosine similarity)
       Captures meaning — e.g. "built REST APIs" matches "API development"
       even without exact word overlap.

    2. Keyword gap analysis
       Exact keyword matching to find what's present and what's missing.
       This is what real ATS systems primarily use.

    Final ats_score is a weighted blend:
       60% semantic similarity + 40% keyword match rate
    This gives a more balanced, real-world score.
    """
    model = get_model()

    # Encode both texts into vectors
    resume_vec = model.encode([resume_text])
    jd_vec = model.encode([jd_text])

    # Semantic similarity score (0 to 100)
    similarity = cosine_similarity(resume_vec, jd_vec)[0][0]
    semantic_score = max(0, (similarity - 0.4) / 0.6) * 100
    semantic_score = round(min(semantic_score, 100), 1)

    # Keyword analysis
    jd_keywords = extract_keywords(jd_text)
    resume_keywords = extract_keywords(resume_text)

    IMPORTANT_SKILLS = {
      "python", "django", "node", "react", "postgresql",
      "aws", "docker", "kubernetes", "api", "sql"
    }

    matched = jd_keywords & resume_keywords
    missing = jd_keywords - resume_keywords

    # Weighted keyword scoring
    score = 0
    total = 0

    for word in jd_keywords:
        weight = 2 if word in IMPORTANT_SKILLS else 1
        total += weight
        if word in matched:
            score += weight

    keyword_match_rate = (score / total) * 100 if total else 0
    keyword_match_rate = round(keyword_match_rate, 1)

    missing_important = [w for w in missing if w in IMPORTANT_SKILLS]
    penalty = len(missing_important) * 5

    experience_bonus = 0

    if re.search(r'\b\d+\+?\s+years?\b', resume_text.lower()):
        experience_bonus += 5

    if "project" in resume_text.lower():
        experience_bonus += 3

    # Weighted blend for final ATS score
    # ats_score = round((semantic_score * 0.6) + (keyword_match_rate * 0.4), 1)
    ats_score = (semantic_score * 0.4) + (keyword_match_rate * 0.6)
    ats_score -= penalty
    ats_score = max(0, min(ats_score, 100))
    ats_score = round(ats_score, 1)
    ats_score = min(100, ats_score + experience_bonus)

    return {
        "ats_score": ats_score,
        # "semantic_score": semantic_score,
        # "keyword_match_rate": keyword_match_rate,
        # "matched_keywords": sorted(list(matched)),
        # "missing_keywords": sorted(list(missing)),
        # "total_jd_keywords": len(jd_keywords),
        # "matched_count": len(matched),
        "semantic_raw": similarity,
        "semantic_scaled": semantic_score,
        "keyword_score": keyword_match_rate,
        "penalty": penalty
    }

from transformers import pipeline

# We load the model once when Django starts
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        print("Loading NLP model... (this happens once)")
        _classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
    return _classifier

# These are the categories we want to detect in job emails
LABELS = [
    "rejected",
    "interview scheduled",
    "offer received",
    "application received",
    "under review",
    "assessment or test assigned",
    "not job related"
]

def classify_email(subject: str, body: str) -> dict:
    # Combine subject + first 512 characters of body
    text = f"{subject}. {body[:512]}"

    clf = get_classifier()
    result = clf(text, candidate_labels=LABELS)

    return {
        "status": result["labels"][0],        # top predicted category
        "confidence": round(result["scores"][0], 3),  # how confident (0 to 1)
        "all_scores": dict(zip(result["labels"], [round(s, 3) for s in result["scores"]]))
    }

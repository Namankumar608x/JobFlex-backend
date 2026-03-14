import base64
import re

def decode_email_body(payload: dict) -> str:
    """
    Gmail sends email body as base64 encoded text.
    This function extracts and decodes it to plain text.
    """
    body = ""

    # Emails can be plain text, HTML, or multipart (both)
    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            data = part.get("body", {}).get("data", "")

            if mime_type == "text/plain" and data:
                # Decode base64 → bytes → string
                body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                break  # prefer plain text over HTML
            elif mime_type == "text/html" and data:
                raw_html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                body = strip_html(raw_html)
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return body.strip()


def strip_html(html: str) -> str:
    """Remove HTML tags and clean up whitespace."""
    clean = re.sub(r"<[^>]+>", " ", html)       # remove tags
    clean = re.sub(r"\s+", " ", clean)            # collapse whitespace
    return clean.strip()


def extract_headers(headers: list) -> dict:
    """
    Gmail returns headers as a list of {name, value} dicts.
    This converts it to a simple dictionary for easy access.
    """
    return {h["name"].lower(): h["value"] for h in headers}

# Words commonly found in ads/opportunity emails but NOT in status update emails
AD_KEYWORDS = [
    "unsubscribe", "click here to apply", "we found jobs for you",
    "jobs you may like", "job alert", "new job listings",
    "explore opportunities", "recommended for you", "fill out this form",
    "register now", "join our talent pool", "submit your resume",
    "we are hiring", "we're hiring", "open to new opportunities"
]

def is_likely_advertisement(subject: str, body: str) -> bool:
    """
    Returns True if the email looks like a job ad or mass mailer
    rather than a status update for an application the user submitted.
    """
    combined = (subject + " " + body).lower()
    matches = sum(1 for kw in AD_KEYWORDS if kw in combined)
    return matches >= 2  # if 2 or more ad keywords found, treat as ad

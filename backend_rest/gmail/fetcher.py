from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from .parser import decode_email_body, extract_headers
from .classifier import classify_email
import os
import json

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service(user_token_data: dict = None):
    """
    Authenticates with Gmail and returns a service object.

    user_token_data: if you're storing tokens per user in DB, pass the dict here.
    For now, falls back to token.json file for testing.
    """
    creds = None

    # Load credentials from file (for local testing)
    if os.path.exists(settings.GMAIL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(settings.GMAIL_TOKEN_PATH, SCOPES)

    # If no valid credentials, start OAuth login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # silently refresh if token expired
        else:
            # This opens a browser window for the user to log in
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GMAIL_CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the token for next time
        with open(settings.GMAIL_TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def fetch_and_classify_emails(max_results: int = 20) -> list:
    """
    Fetches recent emails from Gmail, filters job-related ones,
    classifies each one, and returns the results.
    """
    service = get_gmail_service()

    # Search query — only fetch emails likely related to job applications
    # Can expand this query later
    query = "subject:(application OR interview OR offer OR rejection OR hiring OR position OR role)"

    # Get list of matching email IDs
    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    classified_emails = []

    for msg in messages:
        # Fetch full email by ID
        full_msg = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        payload = full_msg.get("payload", {})
        headers = extract_headers(payload.get("headers", []))
        body = decode_email_body(payload)

        subject = headers.get("subject", "No Subject")
        sender = headers.get("from", "Unknown")
        date = headers.get("date", "")

        classification = classify_email(subject, body)

        # Skip emails the model thinks are not job related
        if classification["status"] == "not job related" and classification["confidence"] > 0.7:
            continue

        classified_emails.append({
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "date": date,
            "status": classification["status"],
            "confidence": classification["confidence"],
            "all_scores": classification["all_scores"]
        })

    return classified_emails

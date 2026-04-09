from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from .parser import decode_email_body, extract_headers, extract_email_address, normalize_timestamp
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

def fetch_recent_thread(service, recruiter_email: str) -> list:
    """
    Fetches the 5 most recent emails from/to a specific recruiter using batching.
    """
    if not recruiter_email:
        return []

    # Search for emails where the recruiter is the sender OR the recipient
    query = f"from:{recruiter_email} OR to:{recruiter_email}"
    try:
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=5
        ).execute()

        messages = results.get("messages", [])
        if not messages:
            return []

        thread_responses = {}
        def callback(request_id, response, exception):
            if exception is None and response:
                thread_responses[response["id"]] = response

        batch = service.new_batch_http_request()
        for msg in messages:
            batch.add(service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["Subject", "Date", "From", "To"]
            ), callback=callback)

        batch.execute()

        thread_details = []
        for msg in messages:
            response = thread_responses.get(msg["id"])
            if not response:
                continue

            headers = extract_headers(response.get("payload", {}).get("headers", []))
            subject = headers.get("subject", "No Subject")
            date_str = headers.get("date", "")
            from_hdr = headers.get("from", "")
            direction = "incoming" if recruiter_email.lower() in from_hdr.lower() else "outgoing"

            thread_details.append({
                "id": response["id"],
                "subject": subject,
                "snippet": response.get("snippet", ""),
                "date": normalize_timestamp(date_str),
                "direction": direction
            })

        return thread_details
    except Exception as e:
        print(f"Failed to fetch thread for {recruiter_email}: {e}")
        return []

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
    recruiter_thread_cache = {}

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

        reply_to = headers.get("reply-to", "")
        raw_recruiter_email = reply_to if reply_to else sender
        recruiter_email = extract_email_address(raw_recruiter_email)

        if recruiter_email not in recruiter_thread_cache:
            recruiter_thread_cache[recruiter_email] = fetch_recent_thread(service, recruiter_email)

        full_thread = recruiter_thread_cache[recruiter_email]
        recent_thread = []
        for t in full_thread:
            if t["id"] == msg["id"]:
                continue
            if len(recent_thread) >= 5:
                break
            recent_thread.append({
                "subject": t["subject"],
                "snippet": t["snippet"],
                "date": t["date"],
                "direction": t["direction"]
            })

        classified_emails.append({
            "email_id": msg["id"],
            "subject": subject,
            "classification": classification["status"],
            "confidence": classification["confidence"],
            "recruiter": recruiter_email,
            "recent_thread": recent_thread
        })

    return classified_emails

from supabase import create_client
from django.conf import settings
import uuid


def get_supabase():
    """
    Creates and returns a Supabase client using credentials from settings.
    Called fresh each time — client is lightweight, no need to cache.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upload_resume_to_supabase(file, username: str) -> str:
    """
    Uploads a PDF file to Supabase Storage.

    File path format: resumes/{username}/{uuid}.pdf
    - Using username as a folder keeps files organized per user
    - UUID prevents filename collisions if user uploads multiple times

    Returns: the file path inside the bucket (not the full URL)
             We store this path and generate signed URLs on demand.
    """
    supabase = get_supabase()

    file_bytes = file.read()
    file_path = f"resumes/{username}/{uuid.uuid4()}.pdf"

    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        path=file_path,
        file=file_bytes,
        file_options={"content-type": "application/pdf"}
    )

    return file_path


def delete_resume_from_supabase(file_path: str):
    """
    Deletes the old resume file from Supabase when user uploads a new one.
    Keeps the bucket clean — no orphaned files accumulating over time.
    """
    supabase = get_supabase()
    supabase.storage.from_(settings.SUPABASE_BUCKET).remove([file_path])


def get_signed_url(file_path: str, expires_in: int = 3600) -> str:
    """
    Generates a temporary signed URL for the resume file.

    expires_in: seconds until the URL expires (default 1 hour)

    Why signed URLs instead of public URLs:
    - Resumes contain personal data — they must not be publicly accessible
    - Signed URLs expire automatically, limiting exposure window
    - Even if someone copies the URL, it stops working after 1 hour
    """
    supabase = get_supabase()
    response = supabase.storage.from_(settings.SUPABASE_BUCKET).create_signed_url(
        file_path,
        expires_in
    )
    return response["signedURL"]

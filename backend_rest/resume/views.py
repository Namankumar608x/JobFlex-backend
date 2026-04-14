from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Resume
from .services.resume_parser import extract_text_from_pdf
from .services.ats_scorer import score_resume
from .services.supabase_storage import (
    upload_resume_to_supabase,
    delete_resume_from_supabase,
    get_signed_url
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_resume(request):
    """
    POST /api/resume/upload/
    Accepts a PDF, uploads to Supabase, extracts text, saves to DB.

    If user already has a resume, the old Supabase file is deleted first
    so we don't accumulate orphaned files in storage.
    """
    file = request.FILES.get("resume")

    if not file:
        return Response({"error": "No file provided."}, status=400)

    if not file.name.lower().endswith(".pdf"):
        return Response({"error": "Only PDF files are accepted."}, status=400)

    # Extract text first — if extraction fails, don't upload to Supabase
    extracted_text = extract_text_from_pdf(file)

    if not extracted_text or len(extracted_text.split()) < 50:
        return Response({
            "error": "Could not extract enough text from this PDF. "
                     "Make sure it is not a scanned image or empty document."
        }, status=400)

    # Delete old Supabase file if user already has a resume
    try:
        existing = Resume.objects.get(user=request.user)
        delete_resume_from_supabase(existing.file_path)
    except Resume.DoesNotExist:
        pass  # first upload — nothing to delete

    # Reset file pointer after reading in extract_text_from_pdf
    file.seek(0)

    # Upload to Supabase
    file_path = upload_resume_to_supabase(file, request.user.username)

    # Save or update DB record
    resume, _ = Resume.objects.update_or_create(
        user=request.user,
        defaults={
            "file_path": file_path,
            "extracted_text": extracted_text
        }
    )

    return Response({
        "message": "Resume uploaded successfully.",
        "word_count": len(extracted_text.split()),
        "uploaded_at": resume.uploaded_at
    }, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_resume(request):
    """
    GET /api/resume/
    Returns resume metadata + a fresh signed URL for drag-drop.
    Signed URL expires in 1 hour — always fresh on each popup open.
    """
    try:
        resume = Resume.objects.get(user=request.user)
    except Resume.DoesNotExist:
        return Response({
            "error": "No resume found. Please upload one."
        }, status=404)

    signed_url = get_signed_url(resume.file_path)

    return Response({
        "file_url": signed_url,
        "word_count": len(resume.extracted_text.split()),
        "uploaded_at": resume.uploaded_at
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ats_scan(request):
    """
    POST /api/resume/ats-scan/
    Body: { "jd_text": "...job description scraped from page..." }

    Fetches the user's stored resume text from DB (no re-parsing needed),
    runs ATS scoring against the provided JD, returns full results.
    """
    jd_text = request.data.get("jd_text", "").strip()

    if not jd_text:
        return Response({"error": "No job description provided."}, status=400)

    if len(jd_text.split()) < 30:
        return Response({
            "error": "Job description is too short to score accurately. "
                     "Make sure you are on a full job listing page."
        }, status=400)

    try:
        resume = Resume.objects.get(user=request.user)
    except Resume.DoesNotExist:
        return Response({
            "error": "No resume found. Please upload your resume first."
        }, status=404)

    results = score_resume(resume.extracted_text, jd_text)

    return Response(results)

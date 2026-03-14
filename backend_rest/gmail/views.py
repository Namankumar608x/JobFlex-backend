from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .fetcher import fetch_and_classify_emails

@api_view(["GET"])
def scan_emails(request):
    """
    GET /gmail/scan/
    Fetches and classifies the user's job application emails.
    Returns a list of emails with their detected status.
    """
    try:
        results = fetch_and_classify_emails(max_results=20)
        return Response({
            "count": len(results),
            "emails": results
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

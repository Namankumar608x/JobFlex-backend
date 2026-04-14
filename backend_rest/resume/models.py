from django.db import models
from django.conf import settings


class Resume(models.Model):
    """
    One resume per user (OneToOneField).
    Uploading a new resume replaces the old one.

    file_url     → path inside Supabase bucket (not the full URL)
                   We store just the path and generate signed URLs on demand
                   so they're always fresh and secure.
    extracted_text → plain text pulled from the PDF by PyMuPDF.
                     Stored so we don't re-parse on every ATS scan request.
    """
    embedding = models.JSONField(null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume'
    )
    file_path = models.CharField(max_length=512)  # path inside Supabase bucket
    extracted_text = models.TextField()
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume — {self.user}"

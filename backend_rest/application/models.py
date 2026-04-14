from django.db import models
# from user.models import User
from django.conf import settings

class Application(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Offer', 'Offer'),
        ('Hired', 'Hired'),
        ('Rejected', 'Rejected'),
    ]

    APP_ID = models.AutoField(primary_key=True)
    id = models.IntegerField(null=True, blank=True)  # company's job posting number e.g. Microsoft 200031626
    jobrole = models.CharField(max_length=150)
    company = models.CharField(max_length=150, null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Applied')
    platform = models.CharField(max_length=100, null=True, blank=True)  # LinkedIn, Microsoft, etc.
    location = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now=True)
    U_ID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='U_ID')

    class Meta:
        db_table = 'application'

    def __str__(self):
        return f"{self.jobrole} - {self.company} ({self.status})"

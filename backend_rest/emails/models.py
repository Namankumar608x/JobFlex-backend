from django.db import models
from application.models import Application

class Email(models.Model):
    email_id = models.AutoField(primary_key=True)
    APP_ID = models.ForeignKey(Application, on_delete=models.CASCADE, db_column='APP_ID')
    sender = models.CharField(max_length=255, null=True, blank=True)
    emailbody = models.TextField(null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    emaildate = models.DateTimeField(auto_now_add=True)
    detected_status = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'email'

    def __str__(self):
        return f"{self.subject} from {self.sender}"
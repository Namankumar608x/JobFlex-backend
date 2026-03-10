from django.db import models
from user.models import User

class Application(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Interview', 'Interview'),
        ('Offered', 'Offered'),
        ('Rejected', 'Rejected'),
    ]
    id = models.IntegerField(unique=True, default=0)
    APP_ID = models.AutoField(primary_key=True)
    jobrole = models.CharField(max_length=150)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Applied')
    changed_at = models.DateTimeField(auto_now=True)
    link = models.TextField(null=True, blank=True)
    company = models.CharField(max_length=150, null=True, blank=True)
    U_ID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='U_ID')

    class Meta:
        db_table = 'application'

    def __str__(self):
        return f"{self.jobrole} - {self.company} ({self.status})"
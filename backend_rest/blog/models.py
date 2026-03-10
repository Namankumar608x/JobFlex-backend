from django.db import models
from user.models import User

class Blog(models.Model):
    id = models.AutoField(primary_key=True)
    U_ID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='U_ID')
    title = models.CharField(max_length=255)
    blogtext = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'blog'

    def __str__(self):
        return self.title
from django.db import models
class User(models.Model):
    U_ID = models.AutoField(primary_key=True)
    uname = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.TextField()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.uname



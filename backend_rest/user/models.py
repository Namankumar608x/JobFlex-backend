from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    username = None

    U_ID = models.AutoField(primary_key=True)
    uname = models.CharField(max_length=100)

    email = models.EmailField(max_length=255, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['uname']

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.uname
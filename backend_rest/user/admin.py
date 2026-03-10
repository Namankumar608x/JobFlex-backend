from django.contrib import admin
from .models import User

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("U_ID", "uname", "email", "is_staff")
    ordering = ("email",)

admin.site.register(User, CustomUserAdmin)
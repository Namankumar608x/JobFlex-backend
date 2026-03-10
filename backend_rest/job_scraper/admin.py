
# job_scraper/admin.py

from django.contrib import admin
from .models import ScrapedJob


# ──────────────────────────────────────────────────────────
# VIVA EXPLANATION:
# ─────────────────
# Django Admin = Built-in web interface to manage DB data
# Access it at: http://localhost:8000/admin
#
# @admin.register() → Registers our model with the admin panel
# ModelAdmin       → Lets us customize how model appears in admin
# ──────────────────────────────────────────────────────────


@admin.register(ScrapedJob)
class ScrapedJobAdmin(admin.ModelAdmin):

    # Columns to show in the list view
    list_display = ["title", "company", "location", "salary", "source", "scraped_at"]

    # Filters shown in right sidebar
    list_filter = ["source", "scraped_at", "location"]

    # Search bar - searches these fields
    search_fields = ["title", "company", "location"]

    # Make scraped_at and id non-editable
    readonly_fields = ["id", "scraped_at"]

    # Default ordering - newest first
    ordering = ["-scraped_at"]

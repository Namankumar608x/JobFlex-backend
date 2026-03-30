from django.contrib import admin
from .models import ScrapedJob

@admin.register(ScrapedJob)
class ScrapedJobAdmin(admin.ModelAdmin):

    # Columns
    list_display = ["title", "company", "location", "salary", "source", "scraped_at"]
    # Filters
    list_filter = ["source", "scraped_at", "location"]
    # Search bar
    search_fields = ["title", "company", "location"]
    # Make scraped_at and id non-editable
    readonly_fields = ["id", "scraped_at"]
    # Default ordering - newest first
    ordering = ["-scraped_at"]

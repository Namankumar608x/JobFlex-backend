from django.apps import AppConfig

class JobScraperConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # VIVA: BigAutoField = Auto-incrementing integer ID field (64-bit)
    # Used as primary key for every model in this app
    name = "job_scraper"
    


# job_scraper/models.py

from django.db import models


# ──────────────────────────────────────────────────────────
# VIVA EXPLANATION:
# ─────────────────
# A Django Model = A database table
# Each attribute = A column in that table
# Django ORM automatically creates SQL from this class
#
# Why save scraped jobs to DB?
#   → So we don't scrape on every request (saves time + avoids bans)
#   → We can serve data from DB when scrape.do is down
#   → Frontend can get jobs instantly from DB
# ──────────────────────────────────────────────────────────


class ScrapedJob(models.Model):

    # ── Fields (Database Columns) ───────────────────────────

    title = models.CharField(max_length=255)
    # CharField = Short text field with a max length
    # Used for job title like "Python Developer"

    company = models.CharField(max_length=255)
    # Company name like "TechCorp Pvt Ltd"

    location = models.CharField(max_length=255, blank=True)
    # blank=True means this field is optional in forms
    # e.g. "Bangalore, India"

    salary = models.CharField(max_length=100, blank=True, default="Not Disclosed")
    # default="Not Disclosed" → used when salary is not provided

    experience = models.CharField(max_length=100, blank=True)
    # e.g. "0-2 years"

    posted_on = models.CharField(max_length=100, blank=True)
    # e.g. "2 days ago" (stored as string since format varies)

    job_url = models.URLField(max_length=500, unique=True)
    # URLField validates that value is a proper URL
    # unique=True prevents saving duplicate job listings

    source = models.CharField(max_length=100, default="Internshala")
    # Which website this job was scraped from

    query = models.CharField(max_length=100, blank=True)
    # What search term was used e.g. "python"

    scraped_at = models.DateTimeField(auto_now_add=True)
    # auto_now_add=True → automatically sets timestamp when record is created
    # VIVA: We never set this manually, Django handles it

    # ── Meta Class ──────────────────────────────────────────
    class Meta:
        ordering = ["-scraped_at"]
        # VIVA: Orders results by newest first (- means descending)

        verbose_name = "Scraped Job"
        verbose_name_plural = "Scraped Jobs"

    # ── String Representation ────────────────────────────────
    def __str__(self):
        # VIVA: This is what shows in Django Admin panel
        return f"{self.title} at {self.company}"

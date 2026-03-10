
# job_scraper/urls.py

from django.urls import path
from .views import ScrapeJobsView, JobListView, JobDeleteView


# ──────────────────────────────────────────────────────────
# VIVA EXPLANATION:
# ─────────────────
# urlpatterns = List of URL routes for this app
#
# path()       → Maps a URL pattern to a View
# .as_view()   → Converts class-based view into a callable
#
# URL Summary:
#   GET  /api/scraper/scrape/       → Scrape fresh jobs from Internshala
#   GET  /api/scraper/jobs/         → Get saved jobs from database
#   DELETE /api/scraper/jobs/<id>/  → Delete a specific job by ID
#
# <int:pk> is a path converter:
#   int: means it only matches integers
#   pk  is the variable name passed to the view
# ──────────────────────────────────────────────────────────


urlpatterns = [
    path("scrape/", ScrapeJobsView.as_view(), name="scrape-jobs"),
    # Triggers fresh scraping from Internshala

    path("jobs/", JobListView.as_view(), name="job-list"),
    # Returns saved jobs from database (fast, no scraping)

    path("jobs/<int:pk>/", JobDeleteView.as_view(), name="job-delete"),
    # Delete a job by its database ID
]

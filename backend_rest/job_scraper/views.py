
# job_scraper/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ScrapedJob
from .serializers import ScrapedJobSerializer
from .scraper import scrape_internshala_jobs


# ──────────────────────────────────────────────────────────
# VIVA EXPLANATION:
# ─────────────────
# APIView → Base class from Django REST Framework
#           Lets us define get(), post(), delete() methods
#           Each method handles a different HTTP request type
#
# Response → DRF's response class, auto-converts dict to JSON
#
# status → DRF's HTTP status codes module
#   status.HTTP_200_OK         → 200 (Success)
#   status.HTTP_201_CREATED    → 201 (Created)
#   status.HTTP_404_NOT_FOUND  → 404 (Not Found)
#   status.HTTP_400_BAD_REQUEST→ 400 (Bad Request)
# ──────────────────────────────────────────────────────────


class ScrapeJobsView(APIView):
    """
    Endpoint: GET /api/scraper/scrape/
    Query Params:
        - query    : job title to search (default: "python")
        - location : city/country       (default: "india")

    VIVA:
        This view scrapes fresh jobs from Internshala,
        saves them to DB to avoid duplicates, and returns
        the results as JSON.
    """

    def get(self, request):

        # ── Step 1: Read query parameters from URL ───────────────
        # VIVA: query_params reads values after ? in URL
        # e.g. /scrape/?query=django&location=bangalore
        query = request.query_params.get("query", "python")
        location = request.query_params.get("location", "india")

        # ── Step 2: Call the scraper ─────────────────────────────
        scraped_jobs = scrape_internshala_jobs(query=query, location=location)

        if not scraped_jobs:
            return Response(
                {
                    "success": False,
                    "message": "No jobs found or scraping failed. Try again.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ── Step 3: Save to Database (avoid duplicates) ──────────
        # VIVA: get_or_create() checks if record exists first
        #   If it exists → returns (object, False)
        #   If it doesn't → creates it and returns (object, True)
        # This prevents saving the same job twice
        saved_jobs = []
        for job_data in scraped_jobs:
            obj, created = ScrapedJob.objects.get_or_create(
                job_url=job_data["job_url"],    # unique field to check duplicate
                defaults={                       # fields to set only on CREATE
                    "title": job_data["title"],
                    "company": job_data["company"],
                    "location": job_data["location"],
                    "salary": job_data["salary"],
                    "experience": job_data["experience"],
                    "posted_on": job_data["posted_on"],
                    "source": job_data["source"],
                    "query": query,
                },
            )
            saved_jobs.append(obj)

        # ── Step 4: Serialize and Return ─────────────────────────
        # VIVA: many=True means we're serializing a LIST of objects
        serializer = ScrapedJobSerializer(saved_jobs, many=True)

        return Response(
            {
                "success": True,
                "count": len(saved_jobs),
                "query": query,
                "location": location,
                "jobs": serializer.data,   # .data = serialized JSON-ready dict
            },
            status=status.HTTP_200_OK,
        )


class JobListView(APIView):
    """
    Endpoint: GET /api/scraper/jobs/
    Query Params:
        - query    : filter by job title keyword (optional)
        - location : filter by location          (optional)

    VIVA:
        This view fetches already-saved jobs from the DB.
        It does NOT scrape fresh — it reads from database.
        Much faster than scraping every time.
    """

    def get(self, request):

        # ── Step 1: Start with all jobs ──────────────────────────
        # VIVA: .all() fetches all rows from ScrapedJob table
        queryset = ScrapedJob.objects.all()

        # ── Step 2: Apply optional filters ───────────────────────
        # VIVA: __icontains = case-insensitive "contains" SQL LIKE query
        # e.g. filter(title__icontains="python") → WHERE title LIKE '%python%'
        query = request.query_params.get("query", None)
        location = request.query_params.get("location", None)

        if query:
            queryset = queryset.filter(title__icontains=query)

        if location:
            queryset = queryset.filter(location__icontains=location)

        # ── Step 3: Serialize ─────────────────────────────────────
        serializer = ScrapedJobSerializer(queryset, many=True)

        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "jobs": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class JobDeleteView(APIView):
    """
    Endpoint: DELETE /api/scraper/jobs/<id>/

    VIVA:
        Deletes a specific job from the database by its ID.
        <id> in the URL is called a path parameter (not query param).
    """

    def delete(self, request, pk):
        # VIVA: pk = Primary Key = unique ID of the record
        try:
            job = ScrapedJob.objects.get(pk=pk)
            job.delete()
            return Response(
                {"success": True, "message": f"Job {pk} deleted."},
                status=status.HTTP_200_OK,
            )
        except ScrapedJob.DoesNotExist:
            # VIVA: DoesNotExist is raised when .get() finds no matching record
            return Response(
                {"success": False, "message": "Job not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

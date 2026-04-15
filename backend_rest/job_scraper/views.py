# job_scraper/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from .models import ScrapedJob
from .serializers import ScrapedJobSerializer
from .scraper import scrape_internshala_jobs, scrape_remoteok_jobs
from redis_client import redis_client
CACHE_TTL=24*60*60
class ScrapeJobsView(APIView):
    """
    Endpoint: GET /api/scraper/scrape/
    Query Params:
        - query    : job title to search (default: "python")
        - location : city/country       (default: "india")
        - source   : "internshala" | "remoteok" | "all" (default: "all")
    """

    def get(self, request):
        query    = request.query_params.get("query", "python")
        location = request.query_params.get("location", "india")
        source   = request.query_params.get("source", "all").lower()
        key=f"postings_{location}_{query}_{source}"
        
        data=redis_client.get(key)
        if data:
            print("returning cached postings")
            return Response(json.loads(data.decode()))
        scraped_jobs = []

        # Call scraper based on source param
        if source == "internshala":
            scraped_jobs = scrape_internshala_jobs(query=query, location=location)

        elif source == "remoteok":
            scraped_jobs = scrape_remoteok_jobs(query=query)

        else:
            # source == "all" → scrape both and combine
            internshala_jobs = scrape_internshala_jobs(query=query, location=location)
            remoteok_jobs    = scrape_remoteok_jobs(query=query)
            scraped_jobs     = internshala_jobs + remoteok_jobs

        if not scraped_jobs:
            return Response(
                {"success": False, "message": "No jobs found or scraping failed. Try again."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Save to DB (skip duplicates using get_or_create)
        saved_jobs = []
        for job_data in scraped_jobs:
            obj, created = ScrapedJob.objects.get_or_create(
                job_url=job_data["job_url"],
                defaults={
                    "title":      job_data["title"],
                    "company":    job_data["company"],
                    "location":   job_data["location"],
                    "salary":     job_data["salary"],
                    "experience": job_data["experience"],
                    "posted_on":  job_data["posted_on"],
                    "source":     job_data["source"],
                    "query":      query,
                },
            )
            saved_jobs.append(obj)

        serializer = ScrapedJobSerializer(saved_jobs, many=True)
        redis_client.setex( 
            key,
            CACHE_TTL,
            json.dumps(serializer.data,default=str)
        )
        return Response(
            {
                "success": True,
                "count":    len(saved_jobs),
                "query":    query,
                "location": location,
                "source":   source,
                "jobs":     serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class JobListView(APIView):
    """
    Endpoint: GET /api/scraper/jobs/
    Query Params:
        - query    : filter by job title    (optional)
        - location : filter by location     (optional)
        - source   : filter by source site  (optional)
    """

    def get(self, request):
        queryset = ScrapedJob.objects.all()

        query    = request.query_params.get("query", None)
        location = request.query_params.get("location", None)
        source   = request.query_params.get("source", None)

        if query:
            queryset = queryset.filter(title__icontains=query)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if source:
            # iexact = case-insensitive exact match
            # e.g. "remoteok" matches "RemoteOK"
            queryset = queryset.filter(source__iexact=source)

        serializer = ScrapedJobSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count":   queryset.count(),
                "jobs":    serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class JobDeleteView(APIView):
    """
    Endpoint: DELETE /api/scraper/jobs/<id>/
    Deletes a specific job from DB by its primary key
    """

    def delete(self, request, pk):
        try:
            job = ScrapedJob.objects.get(pk=pk)
            job.delete()
            return Response(
                {"success": True, "message": f"Job {pk} deleted."},
                status=status.HTTP_200_OK,
            )
        except ScrapedJob.DoesNotExist:
            return Response(
                {"success": False, "message": "Job not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
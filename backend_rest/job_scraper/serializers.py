
from rest_framework import serializers
from .models import ScrapedJob

class ScrapedJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScrapedJob         
        fields = [                
            "id",
            "title",
            "company",
            "location",
            "salary",
            "experience",
            "posted_on",
            "job_url",
            "source",
            "query",
            "scraped_at",
        ]
        read_only_fields = ["id", "scraped_at"]
       

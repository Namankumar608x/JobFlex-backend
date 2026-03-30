from django.db import models

class ScrapedJob(models.Model):


    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
   

    location = models.CharField(max_length=255, blank=True)

    salary = models.CharField(max_length=100, blank=True, default="Not Disclosed")
   

    experience = models.CharField(max_length=100, blank=True)
  

    posted_on = models.CharField(max_length=100, blank=True)
  
    job_url = models.URLField(max_length=500, unique=True)
 

    source = models.CharField(max_length=100, default="Internshala")
    
    query = models.CharField(max_length=100, blank=True)
  

    scraped_at = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        ordering = ["-scraped_at"]

        verbose_name = "Scraped Job"
        verbose_name_plural = "Scraped Jobs"
    def __str__(self):
        return f"{self.title} at {self.company}"

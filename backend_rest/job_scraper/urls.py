
from django.urls import path
from .views import ScrapeJobsView, JobListView, JobDeleteView



urlpatterns = [
    path("scrape/", ScrapeJobsView.as_view(), name="scrape-jobs"),
    path("jobs/", JobListView.as_view(), name="job-list"),
    

    path("jobs/<int:pk>/", JobDeleteView.as_view(), name="job-delete"),
   
]

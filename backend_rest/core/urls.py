from django.contrib import admin
from django.urls import path, include
from .views import home

urlpatterns = [
    path('user/', include('user.urls')),
    path('', home),
    path('admin/', admin.site.urls),
    path('api/scraper/', include('job_scraper.urls')),
    path('api/applications/', include('application.urls')),  # NEW
    path('gmail/', include('gmail.urls')),
]

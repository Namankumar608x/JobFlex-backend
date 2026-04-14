from django.urls import path
from .views import application_detail,application_list,dashboard_summary,applications_timeline,recent_applications,platform_stats

urlpatterns = [
    path('', application_list, name='application-list'),
    path('<int:app_id>/', application_detail, name='application-detail'),
     path('summary/',dashboard_summary),
    path('timeline/', applications_timeline),
    path('platforms/', platform_stats),
    path('recent/', recent_applications),
]
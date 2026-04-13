from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list),         
    path('<int:pk>/', views.blog_detail),
    path('<int:pk>/comment/', views.add_comment),
    path('<int:pk>/upvote/', views.toggle_upvote),
]
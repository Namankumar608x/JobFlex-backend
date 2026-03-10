from django.urls import path
from .views import test_api,register,me,login
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('', test_api),
    path('register/',register),
    path("login/", login, name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("me/", me),

]
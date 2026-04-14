from django.urls import path
from .views import test_api,register,me,login,logout,google_login,fetch_leetcode,fetch_codeforces,refresh_token,extension_login,update_profile_links
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', test_api),
    path('register/', register),
    path("login/", login, name="login"),
    path("extension-login/", extension_login, name="extension-login"),  # NEW
    path("refresh/", refresh_token, name="refresh"),
    path("me/", me),
    path("update-profile-links/", update_profile_links, name="update-profile-links"),
    path("logout/", logout),
    path("auth/google/", google_login),
    path("leetcode/", fetch_leetcode),
    path("codeforces/", fetch_codeforces),
]

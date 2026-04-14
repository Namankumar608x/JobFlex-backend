from django.urls import path
from .views import test_api, register, me, login, logout, google_login, fetch_leetcode, fetch_codeforces, refresh_token, extension_login

urlpatterns = [
    path('', test_api),
    path('register/', register),
    path("login/", login, name="login"),
    path("extension-login/", extension_login, name="extension-login"),
    path("refresh/", refresh_token, name="refresh"),
    path("me/", me),
    path("logout/", logout),
    path("auth/google/", google_login),
    path("leetcode/<str:username>/", fetch_leetcode),
    path("codeforces/<str:username>/", fetch_codeforces),
]
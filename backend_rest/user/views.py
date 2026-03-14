from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.conf import settings

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):

    token = request.data.get("token")
    print("TOKEN RECEIVED:", token)

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo["email"]

        user, created = User.objects.get_or_create(
          email=email,
          defaults={
          "uname": email.split("@")[0],
       }
      )

        refresh = RefreshToken.for_user(user)

        access_token = str(refresh.access_token)

        response = Response({"message": "Login success"})

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,   # True in production
            samesite="Lax"
        )

        return response

    except Exception as e:

        print("Google auth error:", e)
        return Response({"error": str(e)}, status=401)


@api_view(['GET'])
def test_api(request):
    return Response({"message": "Accounts API working"})


@api_view(['POST'])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # generate JWT tokens
        refresh = RefreshToken.for_user(user)

        response= Response({
            "message": "User registered successfully",
            "user": {
                "id": user.U_ID,
                "uname": user.uname,
                "email": user.email
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

        access_token=str(refresh.access_token)
        refresh_token=str(refresh)
         # Set access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,   # True in production (HTTPS)
            samesite="Lax"
        )

         # Set refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        "id": user.U_ID,
        "uname": user.uname,
        "email": user.email
    })

@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid credentials"}, status=401)

    if not user.check_password(password):
        return Response({"error": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    response = Response({
        "message": "Login successful",
        "user": {
            "id": user.U_ID,
            "uname": user.uname,
            "email": user.email
        }
    })

    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,   # True in production
        samesite="Lax"
    )

    # Refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax"
    )

    return response

@api_view(["POST"])
def logout(request):
    response = Response({"message": "Logged out"})
    response.delete_cookie("access_token")
    return response

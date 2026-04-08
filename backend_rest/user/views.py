from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from redis_client import redis_client
from .services.leetcode import fetch_leetcodeData 
from .services.codeforces import fetch_CFData

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
User = get_user_model()


@api_view(["GET"])
def fetch_leetcode(request, username):
    data = fetch_leetcodeData(username)
    return Response(data) 


@api_view(["GET"])
def fetch_codeforces(request, username):
    data = fetch_CFData(username)
    return Response(data)


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

        response = Response({
            "message": "Login success",
            "user": {
                "id": user.U_ID,
                "uname": user.uname,
                "email": user.email
            }
        })

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,   # True in production
            samesite="Lax"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
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
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "message": "User registered successfully",
            "user": {
                "id": user.U_ID,
                "uname": user.uname,
                "email": user.email
            },
            "refresh": refresh_token,
            "access": access_token
        }, status=status.HTTP_201_CREATED)

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
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def logout(request):
    response = Response({"message": "Logged out"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh the access token using the refresh token from cookies.
    
    Can accept refresh token from:
    1. Cookies (httpOnly)
    2. Request body (for extensions/mobile apps)
    """
    # Try to get refresh token from cookies first, then from request body
    refresh_token_str = request.COOKIES.get("refresh_token") or request.data.get("refresh")
    
    if not refresh_token_str:
        return Response(
            {"error": "No refresh token provided"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        refresh = RefreshToken(refresh_token_str)
        access_token = str(refresh.access_token)
        
        response = Response({
            "message": "Token refreshed successfully",
            "access": access_token  # Also return in body for non-cookie clients
        })

        # Update access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # True in production
            samesite="Lax"
        )

        return response

    except Exception as e:
        print("Token refresh error:", e)
        return Response(
            {"error": "Invalid or expired refresh token"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def extension_login(request):
    """
    Login endpoint for browser extensions/mobile apps that can't use httpOnly cookies.
    Returns tokens in response body.
    """
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)

    return Response({
        "success": True,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.U_ID,
            "uname": user.uname,
            "email": user.email
        }
    }, status=status.HTTP_200_OK)
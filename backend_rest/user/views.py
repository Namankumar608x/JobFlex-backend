from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model


User = get_user_model()

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
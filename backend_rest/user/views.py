from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


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

        return Response({
            "message": "User registered successfully",
            "user": {
                "id": user.U_ID,
                "uname": user.uname,
                "email": user.email
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

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
"""
Views for the users app.

Handles user authentication and registration using Django REST Framework (DRF),
including login and signup with JWT token generation.
"""

from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, LoginSerializer, SignupSerializer

def get_tokens_for_user(user: User) -> dict:
    """
    Generate JWT refresh and access tokens for a given user.

    Args:
        user (User): The authenticated user.

    Returns:
        dict: A dictionary containing refresh and access tokens.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class LoginView(APIView):
    """
    API for user login and JWT token generation.

    - Validates user credentials (email & password).
    - Returns JWT tokens upon successful authentication.
    """

    def post(self, request) -> Response:
        """
        Handle user login request.

        Args:
            request (Request): The HTTP request containing user credentials.

        Returns:
            Response: A response containing JWT tokens or an error message.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = get_object_or_404(User, email=email)

            if not user.check_password(password):
                return Response({"error": "Invalid credentials"},
                                status=status.HTTP_401_UNAUTHORIZED)

            user.last_login = now()
            user.save(update_fields=["last_login"])

            return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignupView(APIView):
    """
    API for user registration and automatic JWT token generation.

    - Creates a new user upon successful validation.
    - Automatically generates JWT tokens for the new user.
    """

    def post(self, request) -> Response:
        """
        Handle user signup request.

        Args:
            request (Request): The HTTP request containing user registration data.

        Returns:
            Response: A response containing the new user's details and JWT tokens.
        """
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response(
                {"user": UserSerializer(user).data, "tokens": tokens},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

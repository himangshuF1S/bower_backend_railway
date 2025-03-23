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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User
from .serializers import UserSerializer, LoginSerializer, SignupSerializer


def get_tokens_for_user(user: User) -> dict:
    """
    Generate JWT refresh and access tokens for a given user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class LoginView(APIView):
    """
    API for user login and JWT token generation.
    Supports login via email or phone number.
    """

    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Authenticate user using email or phone number. Returns JWT tokens upon success.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                "Successful login",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    def post(self, request) -> Response:
        """
        Handle user login request.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            phone_number = serializer.validated_data.get("phone_number")
            password = serializer.validated_data["password"]

            user = None

            if email:
                user = User.objects.filter(email=email).first()
            elif phone_number:
                user = User.objects.filter(phone_number=phone_number).first()

            if not user or not user.check_password(password):
                return Response({"error": "Invalid credentials"},
                                status=status.HTTP_401_UNAUTHORIZED)

            user.last_login = now()
            user.save(update_fields=["last_login"])

            return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupView(APIView):
    """
    API for user registration and automatic JWT token generation.
    Supports signup via email or phone number.
    """

    @swagger_auto_schema(
        operation_summary="User Signup",
        operation_description="Register a new user with email or phone number. Returns JWT tokens upon success.",
        request_body=SignupSerializer,
        responses={
            201: openapi.Response(
                "User created successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user": openapi.Schema(type=openapi.TYPE_OBJECT),
                        "tokens": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                                "access": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
            400: "Bad Request",
        },
    )
    def post(self, request) -> Response:
        """
        Handle user signup request.
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

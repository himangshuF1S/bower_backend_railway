"""
Serializers for the users app.

Defines serializers for user authentication and registration,
including signup, login, and user profile serialization.
"""

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile data."""

    class Meta:
        """Metadata for the UserSerializer."""
        model = User
        ields = ["id", "email", "name", "first_name", "last_name", "phone_number", "created_at", "updated_at"]

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email and password.

    Since this serializer is only for validation, the create and update
    methods are implemented as placeholders.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        """Placeholder method (not used)."""
        raise NotImplementedError("LoginSerializer does not support create()")

    def update(self, instance, validated_data):
        """Placeholder method (not used)."""
        raise NotImplementedError("LoginSerializer does not support update()")

class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    - Requires an email, name, first name, last name, and password.
    - Ensures password is at least 6 characters long and write-only.
    """

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        """Metadata for the SignupSerializer."""
        model = User
        fields = ["email", "name", "first_name", "last_name", "password"]

    def create(self, validated_data):
        """Create and return a new user with a hashed password."""
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user

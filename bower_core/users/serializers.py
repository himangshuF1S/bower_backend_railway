"""
Serializers for the users app.

Defines serializers for user authentication and registration,
including signup, login, and user profile serialization.
"""

"""
Serializers for the users app.

Defines serializers for user authentication and registration,
including signup, login, and user profile serialization.
"""

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data.
    """

    class Meta:
        """Metadata for the UserSerializer."""
        model = User
        fields = ["id", "email", "phone_number", "first_name", "last_name", "created_at", "updated_at"]

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login via email or phone number.
    """

    email = serializers.EmailField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True, min_length=10, max_length=15)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        """
        Ensure that either an email or phone number is provided.
        """
        if not data.get("email") and not data.get("phone_number"):
            raise serializers.ValidationError("Either email or phone number is required.")
        return data

class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    - Users can sign up using either email or phone number.
    - Ensures password is at least 6 characters long and write-only.
    """

    email = serializers.EmailField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True, min_length=10, max_length=15)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        """Metadata for the SignupSerializer."""
        model = User
        fields = ["email", "phone_number", "first_name", "last_name", "password"]

    def validate(self, data):
        """
        Ensure at least email or phone number is provided.
        """
        if not data.get("email") and not data.get("phone_number"):
            raise serializers.ValidationError("Either email or phone number is required.")
        return data

    def create(self, validated_data):
        """
        Create and return a new user with a hashed password.
        """
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user

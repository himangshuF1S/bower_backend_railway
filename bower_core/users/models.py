import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    Provides methods to create regular users and superusers.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.
        """
        extra_fields.setdefault("is_admin", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    """
    Custom User model with email authentication.

    - Uses UUID as the primary key.
    - Replaces Django's default username-based authentication with email.
    - Includes fields for personal details and account status.
    - Includes an optional phone number.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional phone number
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_mentor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()  # Custom manager for user creation

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self) -> str:
        """
        Return the user's email as the string representation.
        """
        return str(self.email)

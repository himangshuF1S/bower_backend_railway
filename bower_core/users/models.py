import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    Provides methods to create regular users and superusers.
    """

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        """
        Create and return a regular user with either an email or a phone number.
        """
        if not email and not phone_number:
            raise ValueError("Either email or phone number must be set")

        email = self.normalize_email(email) if email else None
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with email and password.
        """
        extra_fields.setdefault("is_admin", True)
        return self.create_user(email=email, password=password, **extra_fields)

class User(AbstractBaseUser):
    """
    Custom User model with email or phone authentication.

    - Uses UUID as the primary key.
    - Allows login via email or phone number.
    - Includes personal details and account status.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"  # Default login field (can also use phone)
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email if self.email else self.phone_number

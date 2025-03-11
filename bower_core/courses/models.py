import uuid
from django.db import models
from users.models import User

class Course(models.Model):
    """Model for individual courses."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    image = models.ImageField(upload_to="course_images/")
    duration_weeks = models.IntegerField()
    min_credits = models.IntegerField()
    total_credits = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

class CourseBundle(models.Model):
    """Model for user-created course bundles."""
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bundles")
    title = models.CharField(max_length=255)
    courses = models.ManyToManyField(Course, related_name="course_bundles")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        """Returns True if the bundle is active."""
        return self.status == "active"

    def __str__(self):
        return f"{self.title} - {self.user.email} ({self.status})"

class PredefinedCourseBundle(models.Model):
    """Model for pre-configured course bundles assigned to users."""
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("active", "Active"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    courses = models.ManyToManyField(Course, related_name="predefined_bundles")
    assigned_users = models.ManyToManyField(User, related_name="assigned_bundles", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        """Returns True if the bundle is active."""
        return self.status == "active"

    def __str__(self):
        return f"{self.title} ({self.status})"

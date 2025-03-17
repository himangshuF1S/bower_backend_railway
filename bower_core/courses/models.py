import uuid
from django.db import models
from users.models import User


class Course(models.Model):
    """Model for individual courses with multiple mentors."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    mentors = models.ManyToManyField(User, related_name="mentored_courses")  # Multiple mentors
    image = models.ImageField(upload_to="course_images/")
    duration_weeks = models.IntegerField()
    min_credits = models.IntegerField()
    total_credits = models.IntegerField()
    difficulty_level = models.CharField(
        max_length=50,
        choices=[("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced")],
        default="beginner",
        )
    category = models.CharField(max_length=100, null=True, blank=True)  # Ex: AI, Leadership, Marketing
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """Tracks which users are enrolled in which courses."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)  # Track progress in percentage

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.progress}%)"


class CourseBundle(models.Model):
    """Model for user-created course bundles."""
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    CHECKOUT_STATUS = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bundles")
    title = models.CharField(max_length=255)
    courses = models.ManyToManyField(Course, related_name="course_bundles")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    checkout_status = models.CharField(max_length=20, choices=CHECKOUT_STATUS, default="not_started")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        """Returns True if the bundle is active."""
        return self.status == "active"

    def enroll_user(self):
        """Enrolls the user in all courses in the bundle upon successful checkout."""
        if self.checkout_status == "completed":
            for course in self.courses.all():
                Enrollment.objects.get_or_create(user=self.user, course=course)

    def __str__(self):
        return f"{self.title} - {self.user.email} ({self.status})"


class PredefinedCourseBundle(models.Model):
    """Model for pre-configured course bundles curated by mentors/admins."""
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("active", "Active"),
        ("expired", "Expired"),
    ]

    CHECKOUT_STATUS = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    courses = models.ManyToManyField(Course, related_name="predefined_bundles")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_predefined_bundles")  # Mentor/Admin who curated it
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    checkout_status = models.CharField(max_length=20, choices=CHECKOUT_STATUS, default="not_started")
    learning_path = models.CharField(max_length=255, blank=True, null=True)  # Ex: "AI Track", "Leadership Program"
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        """Returns True if the bundle is active."""
        return self.status == "active"

    def enroll_user(self, user):
        """Enrolls the user in all courses in the bundle upon successful checkout."""
        if self.checkout_status == "completed":
            for course in self.courses.all():
                Enrollment.objects.get_or_create(user=user, course=course)

    def __str__(self):
        return f"{self.title} ({self.status})"

class CourseProgress(models.Model):
    """Tracks user progress in a specific course."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="course_progress")
    lessons_completed = models.IntegerField(default=0)
    total_lessons = models.IntegerField(default=1)  # Default to 1 to avoid division errors
    last_accessed = models.DateTimeField(auto_now=True)

    def calculate_progress(self):
        """Updates the progress based on completed lessons."""
        if self.total_lessons > 0:
            self.enrollment.progress = (self.lessons_completed / self.total_lessons) * 100
            self.enrollment.save()

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.enrollment.course.title} ({self.enrollment.progress}%)"

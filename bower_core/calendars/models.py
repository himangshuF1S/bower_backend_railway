import uuid
from django.db import models
from users.models import User
from courses.models import Course
from django.contrib.postgres.fields import JSONField


class Event(models.Model):
    """Model to store participants and accepted users for a session."""
    
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    all_participants = models.JSONField(default=list)  # Stores list of user IDs
    accepted = models.JSONField(default=list)  # Stores list of accepted user IDs

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Event {self.event_id}"


class Session(models.Model):
    """Model for individual online sessions within a course, now linked to Event."""
    
    EVENT_TYPE_CHOICES = [
        ("learning", "Learning"),
        ("community_interaction", "Community Interaction"),
        ("competitions", "Competitions"),
        ("1:1_sessions", "1:1 Sessions"),
    ]

    MODE_CHOICES = [
        ("online", "Online"),
        ("offline", "Offline"),
    ]

    RECURRING_CHOICES = [
        ("none", "None"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True)  
    end_date = models.DateTimeField(null=True, blank=True) 
    start_time = models.TimeField()
    end_time = models.TimeField()
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="online")
    meet_link = models.URLField(max_length=500, null=True, blank=True)
    participants = models.ManyToManyField(User, related_name="participated_sessions", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_sessions")
    created_by_mentor = models.BooleanField(default=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_sessions")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default="learning")

    # Recurrence fields
    recurring_type = models.CharField(max_length=10, choices=RECURRING_CHOICES, default="none")

    # Foreign Key to Event
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sessions", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.start_time}) - Recurring: {self.get_recurring_type_display()}"

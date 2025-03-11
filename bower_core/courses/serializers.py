from rest_framework import serializers
from .models import Course, CourseBundle, PredefinedCourseBundle

class CourseSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source="mentor.name", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "mentor", "mentor_name", "image", "duration_weeks", "min_credits", "total_credits", "created_at"]

class CourseBundleSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    is_active = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = CourseBundle
        fields = ["id", "title", "user", "user_email", "courses", "status", "is_active", "created_at"]
        extra_kwargs = {"user": {"read_only": True}}

class PredefinedCourseBundleSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = PredefinedCourseBundle
        fields = ["id", "title", "description", "courses", "assigned_users", "status", "is_active", "created_at"]

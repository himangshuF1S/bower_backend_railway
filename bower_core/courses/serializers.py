from rest_framework import serializers
from .models import Course, Enrollment, CourseBundle, PredefinedCourseBundle, CourseProgress
from users.models import User


# ------------------------------
# USER SERIALIZER (Minimal for related fields)
# ------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


# ------------------------------
# COURSE SERIALIZER
# ------------------------------
class CourseSerializer(serializers.ModelSerializer):
    mentors = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"


# ------------------------------
# ENROLLMENT SERIALIZER
# ------------------------------
class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "user", "course", "enrolled_at", "progress"]
        read_only_fields = ["user"]


# ------------------------------
# COURSE PROGRESS SERIALIZER
# ------------------------------
class CourseProgressSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)

    class Meta:
        model = CourseProgress
        fields = ["id", "enrollment", "lessons_completed", "total_lessons", "last_accessed"]

    def update(self, instance, validated_data):
        """Update progress and recalculate completion percentage"""
        instance.lessons_completed = validated_data.get("lessons_completed", instance.lessons_completed)
        instance.total_lessons = validated_data.get("total_lessons", instance.total_lessons)
        instance.calculate_progress()
        instance.save()
        return instance


# ------------------------------
# COURSE BUNDLE (USER-CREATED)
# ------------------------------
class CourseBundleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    courses = CourseSerializer(many=True, read_only=True)
    total_credits = serializers.SerializerMethodField()

    class Meta:
        model = CourseBundle
        fields = ["id", "user", "title", "courses", "status", "checkout_status", "total_credits", "created_at"]

    def get_total_credits(self, obj):
        """Calculate total credits for all courses in the bundle."""
        return sum(course.total_credits for course in obj.courses.all())


# ------------------------------
# PREDEFINED (MENTOR-CURATED) COURSE BUNDLE
# ------------------------------
class PredefinedCourseBundleSerializer(serializers.ModelSerializer):
    main_mentor = UserSerializer(read_only=True)
    courses = CourseSerializer(many=True, read_only=True)
    assigned_users = UserSerializer(many=True, read_only=True)
    total_credits = serializers.SerializerMethodField()

    class Meta:
        model = PredefinedCourseBundle
        fields = ["id", "title", "description", "main_mentor", "courses", "assigned_users", "status", "learning_path", "total_credits", "created_at"]

    def get_total_credits(self, obj):
        """Calculate total credits for all courses in the predefined bundle."""
        return sum(course.total_credits for course in obj.courses.all())

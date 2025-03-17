"""
Django REST Framework views for managing Courses, Course Bundles, and Predefined Course Bundles.

This module provides API endpoints for:
- CRUD operations on Courses.
- Managing user-created Course Bundles.
- Handling Predefined Course Bundles.
- Enrollments and Course Progress Tracking.
"""
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Course, Enrollment, CourseBundle, PredefinedCourseBundle, CourseProgress
from .serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    CourseBundleSerializer,
    PredefinedCourseBundleSerializer,
    CourseProgressSerializer,
)

# ------------------------------
# COURSE MANAGEMENT
# ------------------------------
class CourseListView(generics.ListAPIView):
    """
    List all available courses.
    
    - **Permission**: Public (Anyone can view courses)
    - **Response**: List of all courses with title, description, and mentors.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    """
    Retrieve details of a single course.
    
    - **Permission**: Public
    - **Response**: Detailed course information.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

# ------------------------------
# ENROLLMENT MANAGEMENT
# ------------------------------
class EnrollInCourseView(APIView):
    """
    Enroll an authenticated user in a specific course.
    
    - **Permission**: Authenticated Users Only
    - **Request**: Course ID in URL
    - **Response**: Enrollment success message
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        return Response({"message": "Enrolled successfully!"}, status=status.HTTP_201_CREATED)


class UserEnrollmentsView(generics.ListAPIView):
    """
    List all courses the authenticated user is enrolled in.
    
    - **Permission**: Authenticated Users Only
    - **Response**: List of enrolled courses.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

# ------------------------------
# CUSTOM COURSE BUNDLES (User-created)
# ------------------------------
class CourseBundleListCreateView(generics.ListCreateAPIView):
    """
    List all user-created course bundles OR create a new bundle.
    
    - **Permission**: Authenticated Users Only
    - **Response**: List of course bundles OR newly created bundle.
    """
    serializer_class = CourseBundleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseBundle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CourseBundleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user's custom course bundle.
    
    - **Permission**: Bundle owner only.
    - **Response**: Bundle details or update status.
    """
    serializer_class = CourseBundleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseBundle.objects.filter(user=self.request.user)


class AddCourseToBundleView(APIView):
    """
    Add a course to a user's custom bundle.
    
    - **Permission**: Bundle owner only.
    - **Request**: Bundle ID & Course ID in URL
    - **Response**: Success message
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, bundle_id, course_id):
        bundle = get_object_or_404(CourseBundle, id=bundle_id, user=request.user)
        course = get_object_or_404(Course, id=course_id)
        bundle.courses.add(course)
        return Response({"message": "Course added to bundle!"}, status=status.HTTP_200_OK)


class CheckoutBundleView(APIView):
    """
    Checkout a bundle (confirm purchase & enroll user in all courses).
    
    - **Permission**: Bundle owner only.
    - **Response**: Enrollment confirmation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, bundle_id):
        bundle = get_object_or_404(CourseBundle, id=bundle_id, user=request.user)

        if bundle.checkout_status == "completed":
            return Response({"message": "Bundle already checked out!"}, status=status.HTTP_400_BAD_REQUEST)

        bundle.checkout_status = "completed"
        bundle.save()

        for course in bundle.courses.all():
            Enrollment.objects.get_or_create(user=request.user, course=course)

        return Response({"message": "Checkout successful! You are now enrolled in all courses."}, status=status.HTTP_200_OK)

# ------------------------------
# PREDEFINED MENTOR-CURATED BUNDLES
# ------------------------------
class PredefinedBundleListView(generics.ListAPIView):
    """
    List all predefined mentor-curated course bundles.
    
    - **Permission**: Public (Anyone can view)
    """
    queryset = PredefinedCourseBundle.objects.filter(status="active")
    serializer_class = PredefinedCourseBundleSerializer
    permission_classes = [permissions.AllowAny]


class CheckoutPredefinedBundleView(APIView):
    """
    Checkout a predefined mentor-curated bundle (Enroll user).
    
    - **Permission**: Authenticated Users Only
    - **Response**: Enrollment confirmation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, bundle_id):
        bundle = get_object_or_404(PredefinedCourseBundle, id=bundle_id, status="active")

        if bundle.checkout_status == "completed":
            return Response({"message": "You are already enrolled in this bundle!"}, status=status.HTTP_400_BAD_REQUEST)

        bundle.checkout_status = "completed"
        bundle.save()

        for course in bundle.courses.all():
            Enrollment.objects.get_or_create(user=request.user, course=course)

        return Response({"message": "You are now enrolled in all courses in this bundle!"}, status=status.HTTP_200_OK)

# ------------------------------
# COURSE PROGRESS TRACKING
# ------------------------------
class CourseProgressView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update progress for an enrolled course.
    
    - **Permission**: Authenticated Users Only
    - **Response**: Course progress details.
    """
    serializer_class = CourseProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseProgress.objects.filter(enrollment__user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.calculate_progress()

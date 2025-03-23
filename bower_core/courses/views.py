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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# ------------------------------
# COURSE MANAGEMENT
# ------------------------------
class CourseListView(generics.ListAPIView):
    """
    List all available courses.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="List all courses",
        operation_description="Returns a list of all available courses.",
        responses={200: CourseSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CourseDetailView(generics.RetrieveAPIView):
    """
    Retrieve details of a single course.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Retrieve a course",
        operation_description="Fetch details of a specific course by its ID.",
        responses={200: CourseSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# ------------------------------
# ENROLLMENT MANAGEMENT
# ------------------------------
class EnrollInCourseView(APIView):
    """
    Enroll an authenticated user in a specific course.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Enroll in a course",
        operation_description="Enroll the authenticated user in the specified course.",
        responses={201: openapi.Response("Enrollment successful!")}
    )
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        return Response({"message": "Enrolled successfully!"}, status=status.HTTP_201_CREATED)



class UserEnrollmentsView(generics.ListAPIView):
    """
    List all courses the authenticated user is enrolled in.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List user's enrolled courses",
        operation_description="Retrieve all courses the authenticated user is enrolled in.",
        responses={200: EnrollmentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)

# ------------------------------
# CUSTOM COURSE BUNDLES (User-created)
# ------------------------------
class CourseBundleListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for managing user-created course bundles.
    """
    serializer_class = CourseBundleSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all user-created course bundles",
        operation_description="""
        **GET Method:**  
        - Returns a list of course bundles created by the authenticated user.
        - Requires authentication.
        """,
        responses={200: CourseBundleSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new course bundle",
        operation_description="""
        **POST Method:**  
        - Creates a new course bundle for the authenticated user.
        - Requires authentication.
        - Returns the newly created course bundle.
        """,
        responses={201: CourseBundleSerializer()},
        request_body=CourseBundleSerializer
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return CourseBundle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CourseBundleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user's custom course bundle.
    """
    serializer_class = CourseBundleSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve a course bundle",
        operation_description="Fetch details of a specific course bundle by its ID.",
        responses={200: CourseBundleSerializer()}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a course bundle",
        operation_description="Modify an existing course bundle.",
        responses={200: CourseBundleSerializer()},
        request_body=CourseBundleSerializer
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a course bundle",
        operation_description="Remove an existing course bundle.",
        responses={204: "Course bundle deleted successfully"}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

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
    """
    queryset = PredefinedCourseBundle.objects.filter(status="active")
    serializer_class = PredefinedCourseBundleSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="List predefined course bundles",
        operation_description="Retrieve all predefined mentor-curated course bundles.",
        responses={200: PredefinedCourseBundleSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



class CheckoutPredefinedBundleView(APIView):
    """
    Checkout a predefined mentor-curated bundle (Enroll user).
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Checkout a predefined course bundle",
        operation_description="Enroll the authenticated user in all courses of the selected predefined bundle.",
        responses={200: openapi.Response("Enrolled in the predefined bundle")}
    )
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

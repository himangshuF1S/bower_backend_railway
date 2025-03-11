from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Course, CourseBundle, PredefinedCourseBundle
from .serializers import CourseSerializer, CourseBundleSerializer, PredefinedCourseBundleSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """API to manage individual courses."""
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

class CourseBundleViewSet(viewsets.ModelViewSet):
    """API for users to create and manage course bundles."""
    serializer_class = CourseBundleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourseBundle.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="add-course")
    def add_course(self, request, pk=None):
        """Allows users to add courses to their bundle."""
        bundle = self.get_object()
        course_id = request.data.get("course_id")

        try:
            course = Course.objects.get(id=course_id)
            bundle.courses.add(course)
            return Response({"message": "Course added to bundle."})
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=400)

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """Allows admin or payment system to update bundle status."""
        bundle = self.get_object()
        status = request.data.get("status")

        if status not in ["pending", "active", "expired", "cancelled"]:
            return Response({"error": "Invalid status."}, status=400)

        bundle.status = status
        bundle.save()
        return Response({"message": f"Bundle status updated to {status}."})

class PredefinedCourseBundleViewSet(viewsets.ModelViewSet):
    """API to assign predefined course bundles to users."""
    queryset = PredefinedCourseBundle.objects.all()
    serializer_class = PredefinedCourseBundleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="assign-to-user")
    def assign_to_user(self, request, pk=None):
        """Assigns a predefined bundle to the logged-in user."""
        bundle = self.get_object()

        if bundle.status != "active":
            return Response({"error": "Bundle is not active."}, status=400)

        bundle.assigned_users.add(request.user)
        return Response({"message": "Bundle assigned to user."})

from django.urls import path
from .views import (
    CourseListView,
    CourseDetailView,
    EnrollInCourseView,
    UserEnrollmentsView,
    CourseBundleListCreateView,
    CourseBundleDetailView,
    AddCourseToBundleView,
    CheckoutBundleView,
    PredefinedBundleListView,
    CheckoutPredefinedBundleView,  # Updated import
    CourseProgressView,
)

urlpatterns = [
    # Course management
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/<uuid:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<uuid:course_id>/enroll/", EnrollInCourseView.as_view(), name="course-enroll"),
    path("enrollments/", UserEnrollmentsView.as_view(), name="user-enrollments"),

    # Custom Course Bundles
    path("bundles/", CourseBundleListCreateView.as_view(), name="bundle-list"),
    path("bundles/<uuid:pk>/", CourseBundleDetailView.as_view(), name="bundle-detail"),
    path("bundles/<uuid:bundle_id>/add_course/<uuid:course_id>/", AddCourseToBundleView.as_view(), name="bundle-add-course"),
    path("bundles/<uuid:bundle_id>/checkout/", CheckoutBundleView.as_view(), name="bundle-checkout"),

    # Predefined Mentor-Curated Bundles
    path("predefined-bundles/", PredefinedBundleListView.as_view(), name="predefined-bundle-list"),
    path("predefined-bundles/<uuid:bundle_id>/checkout/", CheckoutPredefinedBundleView.as_view(), name="predefined-bundle-checkout"),  # Updated path

    # Course Progress Tracking
    path("progress/<uuid:pk>/", CourseProgressView.as_view(), name="course-progress"),
]

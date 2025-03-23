"""
URL configuration for the Bower project.

This module defines the URL patterns for the application, including:
- Admin panel
- API endpoints for users and courses
- Swagger API documentation

The URLs are mapped using Django's `path`, `include`, and `re_path` functions.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Define the schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Bower API",
        default_version="v1",
        description="API documentation for Bower",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/courses/", include("courses.urls")),
    # path("api/calendars/", include("calendars.urls")),

    # Swagger documentation URLs
    path("api/docs/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/docs/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path(r"^api/docs/swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]

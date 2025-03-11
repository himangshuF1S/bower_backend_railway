"""
URL configuration for the Bower project.

This module defines the URL patterns for the application, including:
- Admin panel
- API endpoints for users and courses
- Swagger API documentation

The URLs are mapped using Django's `path` and `include` functions.
"""

from django.contrib import admin
from django.urls import path, include
from .swagger import urlpatterns as swagger_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/courses/", include("courses.urls")),
    # path("api/calendars/", include("calendars.urls")),
]

urlpatterns += swagger_urls

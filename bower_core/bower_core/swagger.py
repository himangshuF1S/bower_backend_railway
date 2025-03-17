"""
Swagger API documentation for the Bower project.
"""

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authentication import BasicAuthentication, SessionAuthentication


# Renamed to SchemaViewInstance to follow naming conventions
SchemaViewInstance = get_schema_view(
    openapi.Info(
        title="Bower API",
        default_version="v1",
        description="API documentation for Bower",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # Allows public access
    authentication_classes=(BasicAuthentication, SessionAuthentication),  # Bypass JWT for docs
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            SchemaViewInstance.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$',
            SchemaViewInstance.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$',
            SchemaViewInstance.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

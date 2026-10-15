"""URL Configuration for AutoLab project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("", include("laboratorios.urls", namespace="laboratorios")),
    path("exercicios/", include("exercicios.urls", namespace="exercicios")),
]

"""Rotas dos laboratorios."""

from django.urls import path
from . import views

app_name = "laboratorios"

urlpatterns = [
    path("arquivos/", views.arquivos, name="arquivos"),
]

"""Rotas dos laboratorios."""

from django.urls import path
from . import views

app_name = "laboratorios"

urlpatterns = [
    path("arquivos/", views.arquivos, name="arquivos"),
    path("arquivos/organizar/", views.organizar_arquivos, name="organizar_arquivos"),
    path("arquivos/exemplo/", views.exemplo_arquivos, name="exemplo_arquivos"),
]

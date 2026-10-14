"""Rotas dos exercicios."""

from django.urls import path
from . import views

app_name = "exercicios"

urlpatterns = [
    path("", views.lista, name="lista"),
]

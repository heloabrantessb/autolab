"""Rotas dos exercicios."""

from django.urls import path
from . import views

app_name = "exercicios"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("organizacao-arquivos/materiais/", views.materiais_arquivos, name="materiais_arquivos"),
    path("<slug:slug>/", views.detalhe, name="detalhe"),
]

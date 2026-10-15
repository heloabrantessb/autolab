"""Rotas dos laboratorios."""

from django.urls import include, path
from . import resultados_urls, views

app_name = "laboratorios"

urlpatterns = [
    path("laboratorios/", include([
        path("arquivos/", views.arquivos, name="arquivos"),
        path("arquivos/organizar/", views.organizar_arquivos, name="organizar_arquivos"),
        path("arquivos/exemplo/", views.exemplo_arquivos, name="exemplo_arquivos"),
    ])),
    path("resultados/", include(resultados_urls.urlpatterns)),
]

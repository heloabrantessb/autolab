"""URLs públicas por token; arquivos permanecem fora de static e media."""

from django.urls import path
from . import views

urlpatterns = [
    path("<uuid:token>/", views.resultado, name="resultado"),
    path("<uuid:token>/download/", views.download_resultado, name="download_resultado"),
]

"""Views dos laboratorios de automacao."""

from django.http import HttpResponse


def arquivos(request):
    """Laboratorio de Arquivos e Pastas."""
    return HttpResponse("Laboratorio de Arquivos")

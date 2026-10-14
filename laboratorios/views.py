"""Views dos laboratorios de automacao."""

from django.shortcuts import render


def arquivos(request):
    """Laboratorio de Arquivos e Pastas."""
    return render(request, "laboratorios/arquivos.html")

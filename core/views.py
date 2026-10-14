"""Views basicas do modulo core."""

from django.http import HttpResponse


def home(request):
    """Pagina inicial / dashboard."""
    return HttpResponse("AutoLab - Plataforma de Automacao")


def catalogo(request):
    """Catalogo de laboratorios."""
    return HttpResponse("Catalogo de Laboratorios")

"""Views basicas do modulo core."""

from django.shortcuts import render


def home(request):
    """Pagina inicial / dashboard."""
    return render(request, "core/home.html")


def catalogo(request):
    """Catalogo de laboratorios."""
    return render(request, "core/catalogo.html")

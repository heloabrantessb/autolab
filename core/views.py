"""Views basicas do modulo core."""

from django.shortcuts import render

from .catalogo import LABORATORIOS


def home(request):
    """Pagina inicial / dashboard."""
    return render(request, "core/home.html", {
        "laboratorios_destaque": [lab for lab in LABORATORIOS if lab["mvp"]],
    })


def catalogo(request):
    """Catalogo de laboratorios."""
    return render(request, "core/catalogo.html", {
        "laboratorios_mvp": [lab for lab in LABORATORIOS if lab["mvp"]],
        "laboratorios_futuros": [lab for lab in LABORATORIOS if not lab["mvp"]],
    })

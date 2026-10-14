"""Views dos exercicios."""

from django.shortcuts import render


def lista(request):
    """Lista de exercicios."""
    return render(request, "exercicios/lista.html")

"""Views dos exercicios."""

from django.http import HttpResponse


def lista(request):
    """Lista de exercicios."""
    return HttpResponse("Lista de Exercicios")

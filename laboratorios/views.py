"""Views dos laboratorios de automacao."""

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe


ETAPAS_ARQUIVOS = (
    ("aprender", "Aprender"), ("executar", "Executar"),
    ("codigo", "Código Python"), ("exercicio", "Exercício"),
    ("desafio", "Desafio"), ("resultado", "Resultado"),
)


@require_safe
def arquivos(request):
    """Laboratorio de Arquivos e Pastas."""
    return render(request, "laboratorios/arquivos.html", {
        "etapas": ETAPAS_ARQUIVOS,
    })


@require_safe
def exemplo_arquivos(request):
    """Entrega somente o material fictício versionado, sem aceitar caminhos."""
    caminho = settings.BASE_DIR / "materials" / "arquivos" / "exemplo.zip"
    try:
        arquivo = caminho.open("rb")
    except FileNotFoundError as exc:
        raise Http404("Material de exemplo não encontrado.") from exc
    return FileResponse(
        arquivo, as_attachment=True, filename="autolab-arquivos-exemplo.zip",
        content_type="application/zip",
    )

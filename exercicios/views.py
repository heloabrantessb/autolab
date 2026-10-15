"""Views dos exercicios."""

from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def lista(request):
    """Lista de exercicios."""
    return render(request, "exercicios/lista.html")


@require_safe
def detalhe(request, slug):
    if slug != "organizacao-arquivos":
        raise Http404("Exercício não encontrado.")
    return render(request, "exercicios/arquivos.html")


@require_safe
def materiais_arquivos(request):
    """Empacota somente arquivos públicos fixos, sem a referência do instrutor."""
    base = settings.BASE_DIR / "codespaces_exercises" / "arquivos"
    arquivos = [(base / nome, nome) for nome in (
        "README.md", "starter.py", "apoio.py", "tests/verificar.py",
    )]
    arquivos.append((settings.BASE_DIR / "materials/arquivos/exemplo.zip", "exemplo.zip"))
    buffer = BytesIO()
    try:
        with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as pacote:
            for caminho, nome in arquivos:
                pacote.writestr(nome, caminho.read_bytes())
    except FileNotFoundError as exc:
        raise Http404("Material do exercício não encontrado.") from exc
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="autolab-exercicio-arquivos.zip", content_type="application/zip")

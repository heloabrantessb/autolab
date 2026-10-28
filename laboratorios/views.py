"""Views dos laboratorios de automacao."""

from pathlib import Path

from django.conf import settings
from django.db import DatabaseError
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_safe

from .forms import UploadPlanilhaForm, UploadZIPForm
from .models import ResultadoTemporario
from .services.planilha_reader import LimitesPlanilha, PlanilhaInvalida, ler_planilha
from .services.resultados import caminho_resultado, criar_resultado
from .services.zip_validator import ArquivoInvalido


ETAPAS_LABORATORIO = (
    ("aprender", "Aprender"), ("executar", "Executar"),
    ("codigo", "Código Python"), ("exercicio", "Exercício"),
    ("desafio", "Desafio"), ("resultado", "Resultado"),
)


@require_safe
def arquivos(request):
    """Laboratorio de Arquivos e Pastas."""
    return render(request, "laboratorios/arquivos.html", {
        "etapas": ETAPAS_LABORATORIO,
        "etapa_ativa": "aprender",
        "form": UploadZIPForm(),
    })


@require_POST
@never_cache
def organizar_arquivos(request):
    """Valida, organiza e redireciona para evitar reenvio ao atualizar."""
    form = UploadZIPForm(request.POST, request.FILES)
    status = 400
    if form.is_valid():
        try:
            resultado = criar_resultado(form.cleaned_data["arquivo_zip"], form.limites_zip)
        except ArquivoInvalido as exc:
            form.add_error("arquivo_zip", str(exc))
        except (OSError, DatabaseError):
            form.add_error(None, "Não foi possível gerar o resultado agora. Tente novamente mais tarde.")
            status = 503
        else:
            return HttpResponse(status=303, headers={
                "Location": reverse("laboratorios:resultado", kwargs={"token": resultado.token}),
            })
    return render(request, "laboratorios/arquivos.html", {
        "etapas": ETAPAS_LABORATORIO,
        "etapa_ativa": "executar",
        "form": form,
    }, status=status)


def _obter_resultado(token):
    return ResultadoTemporario.objects.filter(token=token, kind="arquivos").first()


def _indisponivel(request, expirado=False):
    return render(request, "laboratorios/resultado_indisponivel.html", {
        "expirado": expirado,
    }, status=410 if expirado else 404)


@require_safe
@never_cache
def resultado(request, token):
    registro = _obter_resultado(token)
    if registro is None:
        return _indisponivel(request)
    if registro.expires_at <= timezone.now():
        return _indisponivel(request, expirado=True)
    try:
        caminho_resultado(registro)
    except OSError:
        return _indisponivel(request)
    response = render(request, "laboratorios/arquivos.html", {
        "etapas": ETAPAS_LABORATORIO, "etapa_ativa": "resultado",
        "form": UploadZIPForm(), "resultado": registro,
    })
    response["Referrer-Policy"] = "no-referrer"
    return response


@require_safe
@never_cache
def download_resultado(request, token):
    registro = _obter_resultado(token)
    if registro is None:
        return _indisponivel(request)
    if registro.expires_at <= timezone.now():
        return _indisponivel(request, expirado=True)
    try:
        arquivo = caminho_resultado(registro).open("rb")
    except OSError:
        return _indisponivel(request)
    response = FileResponse(
        arquivo, as_attachment=True, filename="autolab-arquivos-organizados.zip",
        content_type="application/zip",
    )
    response["Referrer-Policy"] = "no-referrer"
    return response


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


@require_safe
def planilhas(request):
    """Conteúdo didático de Planilhas; processamento em entrega própria."""
    return render(request, "laboratorios/planilhas.html", {
        "etapas": ETAPAS_LABORATORIO, "etapa_ativa": "aprender",
        "limite_mib": settings.MAX_SPREADSHEET_UPLOAD_BYTES / (1024 * 1024),
        "form": UploadPlanilhaForm(),
    })


@require_safe
def exemplo_planilhas(request):
    caminho = settings.BASE_DIR / "materials/planilhas/clientes.csv"
    try:
        arquivo = caminho.open("rb")
    except FileNotFoundError as exc:
        raise Http404("Material de exemplo não encontrado.") from exc
    return FileResponse(
        arquivo, as_attachment=True, filename="autolab-clientes-exemplo.csv",
        content_type="text/csv; charset=utf-8",
    )


@require_POST
@never_cache
def receber_planilha(request):
    """Lê entrada limitada para prévia; não limpa ou persiste resultados."""
    form = UploadPlanilhaForm(request.POST, request.FILES)
    tabela = None
    if form.is_valid():
        arquivo = form.cleaned_data["arquivo_planilha"]
        try:
            tabela = ler_planilha(arquivo, Path(arquivo.name).suffix[1:].lower(), LimitesPlanilha(
                upload_bytes=settings.MAX_SPREADSHEET_UPLOAD_BYTES,
                linhas=settings.MAX_SPREADSHEET_ROWS,
                colunas=settings.MAX_SPREADSHEET_COLUMNS,
            ))
        except PlanilhaInvalida as exc:
            form.add_error("arquivo_planilha", str(exc))
    return render(request, "laboratorios/planilhas.html", {
        "etapas": ETAPAS_LABORATORIO, "etapa_ativa": "executar",
        "limite_mib": settings.MAX_SPREADSHEET_UPLOAD_BYTES / (1024 * 1024),
        "form": UploadPlanilhaForm() if tabela else form,
        "tabela": tabela,
    }, status=200 if tabela else 400)

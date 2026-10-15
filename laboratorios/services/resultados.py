"""Coordenação Django de resultados privados e descarte do upload original."""

from datetime import timedelta
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from laboratorios.models import ResultadoTemporario
from .arquivo_service import organizar_zip
from .zip_validator import LimiteExcedido


NOME_SAIDA = "arquivos_organizados.zip"


def criar_resultado(arquivo, limites):
    """Guarda somente a saída; em falha descarta a área desta execução."""
    if settings.RESULT_TTL_MINUTES <= 0:
        raise ImproperlyConfigured("RESULT_TTL_MINUTES deve ser positivo.")
    raiz = Path(settings.RESULTS_ROOT).resolve()
    raiz.mkdir(mode=0o700, parents=True, exist_ok=True)
    token = uuid4()
    area = raiz / str(token)
    area.mkdir(mode=0o700)
    try:
        with TemporaryDirectory(prefix="upload-", dir=area) as temporario:
            entrada = Path(temporario) / "entrada.zip"
            arquivo.seek(0)
            total = 0
            with entrada.open("xb") as destino:
                for parte in arquivo.chunks(chunk_size=64 * 1024):
                    total += len(parte)
                    if total > limites.upload_bytes:
                        raise LimiteExcedido("O ZIP excede o tamanho máximo permitido.")
                    destino.write(parte)
            organizado = organizar_zip(entrada, area, limites=limites)
        organizado.output_path.rename(area / NOME_SAIDA)
        organizado.output_path.parent.rmdir()
        return ResultadoTemporario.objects.create(
            token=token, relative_path=f"{token}/{NOME_SAIDA}",
            expires_at=timezone.now() + timedelta(minutes=settings.RESULT_TTL_MINUTES),
            total_arquivos=organizado.total_arquivos,
            por_categoria=organizado.por_categoria, avisos=organizado.avisos,
        )
    except BaseException:
        shutil.rmtree(area)
        raise


def caminho_resultado(resultado):
    """Aceita somente o caminho canônico do token, sem links simbólicos."""
    if resultado.kind != "arquivos" or resultado.relative_path != f"{resultado.token}/{NOME_SAIDA}":
        raise FileNotFoundError("Caminho de resultado inválido.")
    raiz = Path(settings.RESULTS_ROOT).resolve()
    area = raiz / str(resultado.token)
    caminho = area / NOME_SAIDA
    if area.is_symlink() or caminho.is_symlink() or not caminho.is_file():
        raise FileNotFoundError("Resultado ausente ou inválido.")
    if not caminho.resolve().is_relative_to(raiz):
        raise FileNotFoundError("Resultado fora da área privada.")
    return caminho

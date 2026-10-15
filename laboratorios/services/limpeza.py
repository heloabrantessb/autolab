"""Limpeza restrita às áreas canônicas de resultados expirados."""

from pathlib import Path

from django.conf import settings
from django.db import transaction

from laboratorios.models import ResultadoTemporario
from .resultados import NOME_SAIDA


def _area_limpeza(resultado):
    if resultado.relative_path != f"{resultado.token}/{NOME_SAIDA}":
        raise OSError("Caminho de resultado inválido.")
    raiz = Path(settings.RESULTS_ROOT).resolve()
    area = raiz / str(resultado.token)
    if area.is_symlink() or (area.exists() and not area.is_dir()):
        raise OSError("Área de resultado inválida.")
    if not area.exists():
        return area
    # Não percorre outras áreas, links ou conteúdo desconhecido.
    for entrada in area.iterdir():
        if entrada.name != NOME_SAIDA or entrada.is_symlink() or not entrada.is_file():
            raise OSError("A área contém uma entrada inesperada.")
    return area


def limpar_resultado(token, corte, *, simular=False):
    """Revalida prazo/tipo, remove só a saída conhecida e depois os metadados.

    A operação de arquivos não é transacional. Se o banco falhar depois da
    remoção, uma nova execução conclui a limpeza dos metadados remanescentes.
    """
    with transaction.atomic():
        resultado = ResultadoTemporario.objects.select_for_update().filter(
            token=token, expires_at__lte=corte, kind="arquivos",
        ).first()
        if resultado is None:
            return False
        area = _area_limpeza(resultado)
        if not simular:
            (area / NOME_SAIDA).unlink(missing_ok=True)
            try:
                area.rmdir()
            except FileNotFoundError:
                pass
            resultado.delete()
        return True

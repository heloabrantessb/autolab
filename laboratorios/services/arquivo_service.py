"""Organização por extensão em ZIP privado, sem extrair caminhos de entrada."""

import csv
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path
import shutil
import stat
import tempfile
import unicodedata
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from .zip_validator import (
    LimitesZIP, copiar_entrada_zip, inspecionar_zip, normalizar_caminho_zip,
)


CATEGORIAS = {
    "Documentos": {".pdf", ".doc", ".docx", ".txt"},
    "Planilhas": {".csv", ".xls", ".xlsx"},
    "Imagens": {".png", ".jpg", ".jpeg"},
    "Outros": set(),
}
RESERVADOS = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefixo}{numero}" for prefixo in ("COM", "LPT")
    for numero in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "¹", "²", "³")
}
MAX_NOME_BYTES = 200


@dataclass(frozen=True)
class ResultadoOrganizacao:
    output_path: Path
    total_arquivos: int
    por_categoria: dict[str, int]
    avisos: list[str]


def _categoria(nome):
    extensao = Path(nome).suffix.lower()
    return next((grupo for grupo, extensoes in CATEGORIAS.items() if extensao in extensoes), "Outros")


def _cortar_utf8(texto, max_bytes):
    return texto.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore")


def _nome_seguro(nome):
    nome = "".join(
        "_" if char in '<>:"/\\|?*' or unicodedata.category(char).startswith("C") else char
        for char in unicodedata.normalize("NFC", nome)
    ).strip(" .") or "arquivo"
    if nome.split(".", 1)[0].rstrip(" .").upper() in RESERVADOS:
        nome = "_" + nome
    extensao = _cortar_utf8(Path(nome).suffix, 32)
    base = nome[:-len(Path(nome).suffix)] if Path(nome).suffix else nome
    base = _cortar_utf8(base, MAX_NOME_BYTES - len(extensao.encode("utf-8"))) or "arquivo"
    return base + extensao


def _nome_unico(nome, usados):
    extensao = Path(nome).suffix
    base = nome[:-len(extensao)] if extensao else nome
    candidato, numero = nome, 2
    while candidato.casefold() in usados:
        sufixo = f"_{numero}"
        limite = MAX_NOME_BYTES - len((sufixo + extensao).encode("utf-8"))
        candidato = _cortar_utf8(base, limite) + sufixo + extensao
        numero += 1
    usados.add(candidato.casefold())
    return candidato


def _celula_texto(valor):
    return "'" + valor if valor.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")) else valor


def _zip_info(nome, diretorio=False):
    info = ZipInfo(nome, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = ((stat.S_IFDIR | 0o700) if diretorio else (stat.S_IFREG | 0o600)) << 16
    if diretorio:
        info.external_attr |= 0x10
    return info


def organizar_zip(entrada: Path, diretorio_trabalho: Path, *, limites: LimitesZIP) -> ResultadoOrganizacao:
    """Valida e produz um ZIP em subdiretório exclusivo da área existente.

    A área é controlada pelo servidor. A saída permanece nela para o chamador
    gerenciar seu ciclo de vida; qualquer falha remove a execução incompleta.
    """
    raiz = Path(diretorio_trabalho).resolve(strict=True)
    if not raiz.is_dir():
        raise NotADirectoryError("A área de trabalho deve ser um diretório existente.")
    execucao = None
    try:
        with Path(entrada).open("rb") as arquivo:
            inspecionar_zip(arquivo, limites)
            with ZipFile(arquivo) as original:
                entradas = sorted(
                    ((normalizar_caminho_zip(info), info) for info in original.infolist() if not info.is_dir()),
                    key=lambda item: item[0],
                )
                execucao = Path(tempfile.mkdtemp(prefix="organizacao-", dir=raiz))
                destino = execucao / "arquivos_organizados.zip"
                contagens = dict.fromkeys(CATEGORIAS, 0)
                usados = {grupo: set() for grupo in CATEGORIAS}
                linhas, avisos, total_bytes = [], [], 0
                with ZipFile(destino, "x", compression=ZIP_DEFLATED) as organizado:
                    for grupo in CATEGORIAS:
                        organizado.writestr(_zip_info(grupo + "/", diretorio=True), b"")
                    for caminho, info in entradas:
                        nome_original = caminho.rsplit("/", 1)[-1]
                        grupo = _categoria(nome_original)
                        nome_final = _nome_unico(_nome_seguro(nome_original), usados[grupo])
                        nome_saida = f"{grupo}/{nome_final}"
                        with organizado.open(_zip_info(nome_saida), "w") as saida:
                            total_bytes += copiar_entrada_zip(
                                arquivo, original, info, saida, limites, total_anterior=total_bytes,
                            )
                        contagens[grupo] += 1
                        basename_original = info.orig_filename.replace("\\", "/").rsplit("/", 1)[-1]
                        alterado = nome_final != basename_original
                        if alterado:
                            avisos.append(f"Nome de saída ajustado: {nome_saida}.")
                        linhas.append((info.orig_filename, nome_saida, grupo, "renomeado" if alterado else "organizado"))
                    with organizado.open(_zip_info("relatorio.csv"), "w") as binario:
                        with TextIOWrapper(binario, encoding="utf-8", newline="") as texto:
                            writer = csv.writer(texto)
                            writer.writerow(("caminho_original", "nome_saida", "categoria", "status"))
                            writer.writerows(tuple(_celula_texto(valor) for valor in linha) for linha in linhas)
                return ResultadoOrganizacao(destino, len(entradas), contagens, avisos)
    except BaseException:
        if execucao is not None:
            shutil.rmtree(execucao)
        raise

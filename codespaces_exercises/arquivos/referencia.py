"""Referência do instrutor; excluída do pacote e do caminho didático principal."""

from pathlib import PurePosixPath
from apoio import executar_cli


def categoria(nome):
    extensao = PurePosixPath(nome).suffix.lower()
    for grupo, extensoes in {
        "Documentos": {".pdf", ".doc", ".docx", ".txt"},
        "Planilhas": {".csv", ".xls", ".xlsx"},
        "Imagens": {".png", ".jpg", ".jpeg"},
    }.items():
        if extensao in extensoes:
            return grupo
    return "Outros"


def nome_unico(nome, usados):
    extensao = PurePosixPath(nome).suffix
    base = nome[:-len(extensao)] if extensao else nome
    candidato, numero = nome, 2
    while candidato.casefold() in usados:
        candidato = f"{base}_{numero}{extensao}"
        numero += 1
    usados.add(candidato.casefold())
    return candidato


def linha_inventario(caminho_original, nome_saida, grupo):
    alterado = PurePosixPath(caminho_original).name != PurePosixPath(nome_saida).name
    return (caminho_original, nome_saida, grupo, "renomeado" if alterado else "organizado")


if __name__ == "__main__":
    executar_cli(categoria, nome_unico, linha_inventario)

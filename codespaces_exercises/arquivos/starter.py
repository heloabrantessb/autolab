"""Complete os três TODOs e execute os testes locais descritos no README."""

from apoio import executar_cli


def categoria(nome):
    """Retorna Documentos, Planilhas, Imagens ou Outros pela extensão."""
    # TODO 1: use pathlib.Path e normalize a extensão com .lower().
    raise NotImplementedError("Complete categoria(nome).")


def nome_unico(nome, usados):
    """Retorna nome livre e registra seu casefold() no conjunto usados."""
    # TODO 2: preserve a extensão e tente _2, _3... enquanto houver colisão.
    raise NotImplementedError("Complete nome_unico(nome, usados).")


def linha_inventario(caminho_original, nome_saida, grupo):
    """Retorna (original, saída, categoria, status) para o relatório."""
    # TODO 3: compare os nomes base para decidir organizado/renomeado.
    raise NotImplementedError("Complete linha_inventario(original, saida, grupo).")


if __name__ == "__main__":
    executar_cli(categoria, nome_unico, linha_inventario)

"""Infraestrutura do exercício: somente o ZIP fictício versionado é aceito.

O participante implementa regras de negócio em starter.py. Esta infraestrutura
não é um processador de uploads: o site usa outro serviço com inspeção completa.
"""

import argparse
import csv
from hashlib import sha256
from io import BytesIO, StringIO
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZIP_DEFLATED


PASTA = Path(__file__).resolve().parent
EXEMPLO_SHA256 = "0bdf85b083b4af072dc4588276faeb505b1e17bfc9bd0251784ead0b73e7e93d"
GRUPOS = ("Documentos", "Planilhas", "Imagens", "Outros")


def exemplo_padrao():
    local = PASTA / "exemplo.zip"
    return local if local.is_file() else PASTA.parents[1] / "materials/arquivos/exemplo.zip"


def organizar(categoria, nome_unico, linha_inventario, saida, *, exemplo=None):
    """Aplica as funções do participante ao material conhecido, sem extrair."""
    exemplo = Path(exemplo) if exemplo is not None else exemplo_padrao()
    if exemplo.stat().st_size > 1024 * 1024:
        raise ValueError("Use o ZIP fictício original fornecido com o exercício.")
    data = exemplo.read_bytes()
    if sha256(data).hexdigest() != EXEMPLO_SHA256:
        raise ValueError("Use o ZIP fictício original fornecido com o exercício.")
    planos, linhas = [], []
    usados = {grupo: set() for grupo in GRUPOS}
    contagens = dict.fromkeys(GRUPOS, 0)
    destinos = set()
    with ZipFile(BytesIO(data)) as entrada:
        for info in sorted(entrada.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            original = info.filename
            base = PurePosixPath(original).name
            grupo = categoria(base)
            if grupo not in GRUPOS:
                raise ValueError("A função categoria deve retornar uma das quatro categorias.")
            nome = nome_unico(base, usados[grupo])
            if not isinstance(nome, str) or not nome or "/" in nome or "\\" in nome or nome in (".", ".."):
                raise ValueError("nome_unico deve retornar um nome base válido.")
            destino = f"{grupo}/{nome}"
            if destino.casefold() in destinos:
                raise ValueError("Uma colisão de nomes não foi resolvida.")
            destinos.add(destino.casefold())
            linha = linha_inventario(original, destino, grupo)
            if not isinstance(linha, (tuple, list)) or len(linha) != 4 or not all(isinstance(v, str) for v in linha):
                raise ValueError("linha_inventario deve retornar quatro textos.")
            linhas.append(linha)
            planos.append((destino, entrada.read(info)))
            contagens[grupo] += 1
    relatorio = StringIO(newline="")
    writer = csv.writer(relatorio)
    writer.writerow(("caminho_original", "nome_saida", "categoria", "status"))
    writer.writerows([
        tuple("'" + valor if valor.lstrip().startswith(("=", "+", "-", "@")) else valor for valor in linha)
        for linha in linhas
    ])
    # O modo exclusivo recusa uma saída existente, inclusive o ZIP de entrada.
    # Todos os TODOs são chamados antes de criar a saída.
    saida = Path(saida)
    criado = False
    try:
        with saida.open("xb") as arquivo:
            criado = True
            with ZipFile(arquivo, "w", compression=ZIP_DEFLATED) as resultado:
                for grupo in GRUPOS:
                    resultado.writestr(grupo + "/", b"")
                for destino, conteudo in planos:
                    resultado.writestr(destino, conteudo)
                resultado.writestr("relatorio.csv", relatorio.getvalue().encode("utf-8"))
    except BaseException:
        if criado:
            saida.unlink(missing_ok=True)
        raise
    return contagens


def executar_cli(categoria, nome_unico, linha_inventario):
    parser = argparse.ArgumentParser(description="Organize apenas o material fictício do exercício.")
    parser.add_argument("--saida", type=Path, required=True, help="Novo ZIP a criar, sem sobrescrever arquivos.")
    args = parser.parse_args()
    try:
        contagens = organizar(categoria, nome_unico, linha_inventario, args.saida)
    except NotImplementedError as exc:
        parser.exit(2, f"{exc} Consulte os TODOs de starter.py e rode os testes locais.\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Não foi possível gerar o ZIP: {exc}\n")
    print(f"Total: {sum(contagens.values())}. Categorias: {contagens}")

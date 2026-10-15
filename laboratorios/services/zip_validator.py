"""Inspeção ZIP sem escrita e cópia limitada para destinos controlados.

Estruturas ZIP: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
"""

from dataclasses import dataclass
import ntpath
import stat
import struct
import unicodedata
import zipfile
import zlib


class ArquivoInvalido(Exception):
    """Entrada não corresponde ao contrato de ZIP permitido."""


class LimiteExcedido(ArquivoInvalido):
    """Um limite de recursos foi excedido."""


@dataclass(frozen=True)
class LimitesZIP:
    upload_bytes: int
    entradas: int
    descompactado_bytes: int
    entrada_bytes: int


@dataclass(frozen=True)
class InspecaoZIP:
    caminhos: tuple[str, ...]
    total_bytes: int


def _diretorio_central(entrada, limites):
    """Conta registros antes de ZipFile materializar sua lista de entradas."""
    entrada.seek(0, 2)
    tamanho = entrada.tell()
    if tamanho > limites.upload_bytes:
        raise LimiteExcedido("O ZIP excede o tamanho máximo permitido.")
    inicio = max(0, tamanho - 65557)
    entrada.seek(inicio)
    fim = entrada.read(65557)
    pos = fim.rfind(b"PK\x05\x06")
    if pos < 0 or len(fim) - pos < 22:
        raise ArquivoInvalido("O arquivo não é um ZIP válido ou está corrompido.")
    _, disco, disco_central, neste_disco, declaradas, tamanho_central, offset, comentario = struct.unpack_from("<4s4H2IH", fim, pos)
    if disco or disco_central or neste_disco != declaradas:
        raise ArquivoInvalido("ZIP dividido em vários volumes não é permitido.")
    if declaradas == 65535 or tamanho_central == 0xffffffff or offset == 0xffffffff:
        raise ArquivoInvalido("ZIP64 não é permitido neste laboratório.")
    if declaradas > limites.entradas:
        raise LimiteExcedido("O ZIP excede a quantidade máxima de entradas.")
    if pos + 22 + comentario != len(fim) or offset + tamanho_central != inicio + pos:
        raise ArquivoInvalido("A estrutura do ZIP está inconsistente.")
    cursor, quantidade = offset, 0
    while cursor < offset + tamanho_central:
        entrada.seek(cursor)
        cabecalho = entrada.read(46)
        if len(cabecalho) != 46 or cabecalho[:4] != b"PK\x01\x02":
            raise ArquivoInvalido("O diretório do ZIP está corrompido.")
        nome, extra, nota = struct.unpack_from("<3H", cabecalho, 28)
        cursor += 46 + nome + extra + nota
        quantidade += 1
        if quantidade > limites.entradas:
            raise LimiteExcedido("O ZIP excede a quantidade máxima de entradas.")
    if cursor != offset + tamanho_central or quantidade != declaradas:
        raise ArquivoInvalido("A quantidade de entradas do ZIP está inconsistente.")
    return offset


def normalizar_caminho_zip(info):
    nome = info.orig_filename.replace("\\", "/")
    if not nome or nome.startswith("/") or ntpath.splitdrive(nome)[0]:
        raise ArquivoInvalido("O ZIP contém um caminho absoluto ou inválido.")
    partes = nome.split("/")
    if ".." in partes or any(":" in parte for parte in partes):
        raise ArquivoInvalido("O ZIP contém um caminho que não é permitido.")
    if any(unicodedata.category(char) == "Cc" for char in nome):
        raise ArquivoInvalido("O ZIP contém caracteres de controle no nome.")
    partes = [parte for parte in partes if parte not in ("", ".")]
    if not partes:
        raise ArquivoInvalido("O ZIP contém um nome vazio.")
    if any(parte.casefold() in ("__macosx", ".ds_store", "thumbs.db") for parte in partes):
        raise ArquivoInvalido("Remova os metadados de sistema do ZIP antes de enviá-lo.")
    return unicodedata.normalize("NFC", "/".join(partes))


def _ler_entrada(entrada, archive, info, limite_total, limite_entrada, offset_central, destino=None):
    # ZipFile.open confere cabeçalho local, nome e sobreposição de entradas.
    # Não lemos pelo ZipExtFile: ele pode truncar saída pelo tamanho declarado.
    with archive.open(info):
        pass
    entrada.seek(info.header_offset)
    local = entrada.read(30)
    if len(local) != 30 or local[:4] != b"PK\x03\x04":
        raise ArquivoInvalido("O cabeçalho de uma entrada está corrompido.")
    flags, metodo = struct.unpack_from("<2H", local, 6)
    if flags != info.flag_bits or metodo != info.compress_type:
        raise ArquivoInvalido("Os cabeçalhos de uma entrada estão inconsistentes.")
    comprimido_local, tamanho_local = struct.unpack_from("<2I", local, 18)
    if 0xffffffff in (comprimido_local, tamanho_local):
        raise ArquivoInvalido("ZIP64 não é permitido neste laboratório.")
    if not flags & 8 and (
        comprimido_local != info.compress_size or tamanho_local != info.file_size
        or struct.unpack_from("<I", local, 14)[0] != info.CRC
    ):
        raise ArquivoInvalido("Os tamanhos ou a integridade declarada estão inconsistentes.")
    nome, extra = struct.unpack_from("<2H", local, 26)
    inicio = info.header_offset + 30 + nome + extra
    if inicio + info.compress_size > offset_central:
        raise ArquivoInvalido("Uma entrada ultrapassa a área de dados do ZIP.")
    entrada.seek(inicio)
    restantes, total, crc = info.compress_size, 0, 0
    descompressor = zlib.decompressobj(-15) if info.compress_type == zipfile.ZIP_DEFLATED else None
    pendente = b""
    while restantes or pendente:
        capacidade = min(65536, limite_total - total + 1, limite_entrada - total + 1)
        if pendente:
            dados = pendente
        else:
            dados = entrada.read(min(restantes, capacidade))
            if not dados:
                raise ArquivoInvalido("Uma entrada do ZIP está incompleta.")
            restantes -= len(dados)
        if descompressor:
            saida = descompressor.decompress(dados, capacidade)
            pendente = descompressor.unconsumed_tail
            if descompressor.unused_data or (descompressor.eof and (restantes or pendente)):
                raise ArquivoInvalido("Uma entrada comprimida tem dados extras inválidos.")
        else:
            saida, pendente = dados, b""
        total += len(saida)
        if total > limite_entrada or total > limite_total:
            raise LimiteExcedido("O conteúdo descompactado excede os limites permitidos.")
        crc = zlib.crc32(saida, crc)
        if destino is not None and destino.write(saida) != len(saida):
            raise OSError("Não foi possível gravar todo o conteúdo da entrada.")
    if descompressor and not descompressor.eof:
        raise ArquivoInvalido("Uma entrada comprimida está corrompida ou incompleta.")
    if total != info.file_size or (crc & 0xffffffff) != info.CRC:
        raise ArquivoInvalido("O tamanho ou a integridade de uma entrada está incorreto.")
    return total


def copiar_entrada_zip(entrada, archive, info, destino, limites, total_anterior=0):
    """Copia após inspeção completa, repetindo limites reais e integridade.

    O chamador deve descartar toda a saída se esta operação falhar.
    """
    offset = _diretorio_central(entrada, limites)
    try:
        return _ler_entrada(
            entrada, archive, info, limites.descompactado_bytes - total_anterior,
            limites.entrada_bytes, offset, destino=destino,
        )
    except (zipfile.BadZipFile, EOFError, ValueError, RuntimeError,
            NotImplementedError, zlib.error, struct.error) as exc:
        raise ArquivoInvalido("Não foi possível copiar uma entrada íntegra do ZIP.") from exc


def inspecionar_zip(entrada, limites: LimitesZIP) -> InspecaoZIP:
    """Valida um arquivo binário seekable e restaura sua posição ao início."""
    try:
        offset_central = _diretorio_central(entrada, limites)
        entrada.seek(0)
        with zipfile.ZipFile(entrada) as archive:
            infos = archive.infolist()
            vistos, arquivos, declarados = set(), [], 0
            for info in infos:
                if info.volume:
                    raise ArquivoInvalido("ZIP dividido em vários volumes não é permitido.")
                caminho = normalizar_caminho_zip(info)
                chave = caminho.casefold()
                if chave in vistos:
                    raise ArquivoInvalido("O ZIP contém caminhos repetidos ou ambíguos.")
                vistos.add(chave)
                if info.flag_bits & 0x41:
                    raise ArquivoInvalido("ZIP criptografado não é permitido.")
                if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    raise ArquivoInvalido("Use um ZIP com compressão Stored ou Deflate.")
                if info.extract_version > 20:
                    raise ArquivoInvalido("O ZIP usa recursos não permitidos neste laboratório.")
                tipo = stat.S_IFMT(info.external_attr >> 16)
                if tipo not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ArquivoInvalido("O ZIP contém links ou arquivos especiais.")
                diretorio = info.is_dir()
                if info.external_attr & 0x10 and not diretorio:
                    raise ArquivoInvalido("O ZIP contém uma entrada de diretório inválida.")
                if (tipo == stat.S_IFDIR and not diretorio) or (diretorio and tipo == stat.S_IFREG):
                    raise ArquivoInvalido("O ZIP contém uma entrada de diretório inválida.")
                if diretorio and info.file_size:
                    raise ArquivoInvalido("Um diretório do ZIP contém dados inesperados.")
                if info.file_size > limites.entrada_bytes:
                    raise LimiteExcedido("Uma entrada excede o tamanho permitido.")
                declarados += info.file_size
                if declarados > limites.descompactado_bytes:
                    raise LimiteExcedido("O conteúdo descompactado excede o tamanho total permitido.")
                if not diretorio:
                    arquivos.append(caminho)
            if not arquivos:
                raise ArquivoInvalido("O ZIP deve conter pelo menos um arquivo regular.")
            total = 0
            for info in infos:
                total += _ler_entrada(entrada, archive, info,
                    limites.descompactado_bytes - total, limites.entrada_bytes, offset_central)
            return InspecaoZIP(tuple(arquivos), total)
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError, OSError,
            ValueError, RuntimeError, NotImplementedError, zlib.error, struct.error) as exc:
        raise ArquivoInvalido("Não foi possível ler o ZIP: arquivo inválido ou corrompido.") from exc
    finally:
        entrada.seek(0)

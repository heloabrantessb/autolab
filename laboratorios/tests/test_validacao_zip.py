"""ZIPs adversariais construídos em memória, sem extração de conteúdo."""

from dataclasses import replace
from io import BytesIO
import stat
import struct
from unittest.mock import patch
import warnings
import zipfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from laboratorios.services.zip_validator import (
    ArquivoInvalido, LimiteExcedido, LimitesZIP, inspecionar_zip,
)


def criar_zip(entradas, compressao=zipfile.ZIP_DEFLATED):
    buffer = BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(buffer, "w", compression=compressao) as archive:
            for nome, conteudo in entradas:
                archive.writestr(nome, conteudo)
    return buffer.getvalue()


def adulterar(data, indice=0, tamanho=None, crc=None, flags=None, comprimido=None):
    """Altera cabeçalhos local e central, como em um upload malicioso."""
    result = bytearray(data)
    with zipfile.ZipFile(BytesIO(data)) as archive:
        local = archive.infolist()[indice].header_offset
    central = struct.unpack_from("<I", data, data.rfind(b"PK\x05\x06") + 16)[0]
    for _ in range(indice):
        central += 46 + sum(struct.unpack_from("<3H", data, central + 28))
    for value, local_offset, central_offset, formato in (
        (tamanho, 22, 24, "<I"), (crc, 14, 16, "<I"),
        (flags, 6, 8, "<H"), (comprimido, 18, 20, "<I"),
    ):
        if value is not None:
            struct.pack_into(formato, result, local + local_offset, value)
            struct.pack_into(formato, result, central + central_offset, value)
    return bytes(result)


class TestInspecaoZIP(SimpleTestCase):
    limites = LimitesZIP(100000, 100, 10000, 1000)

    def inspecionar(self, data, limites=None):
        stream = BytesIO(data)
        try:
            return inspecionar_zip(stream, limites or self.limites)
        finally:
            self.assertEqual(stream.tell(), 0)

    def test_accepts_example_and_both_supported_methods(self):
        data = (settings.BASE_DIR / "materials/arquivos/exemplo.zip").read_bytes()
        resultado = self.inspecionar(data)
        self.assertEqual(len(resultado.caminhos), 6)
        for method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            with self.subTest(method=method):
                result = self.inspecionar(criar_zip([("pasta/", b""), ("pasta/notas.txt", b"abc")], method))
                self.assertEqual(result.caminhos, ("pasta/notas.txt",))
                self.assertEqual(result.total_bytes, 3)

    def test_rejects_non_zip_empty_and_directories_only(self):
        for data in (b"texto", criar_zip([]), criar_zip([("pasta/", b"")])):
            with self.subTest(data=data[:12]), self.assertRaises(ArquivoInvalido):
                self.inspecionar(data)

    def test_rejects_unsafe_paths(self):
        for name in ("../fora.txt", "a/../../fora", "/absoluto", "C:/arquivo", "C:arquivo", "..\\fora", "\\\\servidor\\pasta", "pasta/c:arquivo", "a\nb.txt"):
            with self.subTest(name=name), self.assertRaises(ArquivoInvalido):
                self.inspecionar(criar_zip([(name, b"a")]))

    def test_rejects_nul_in_raw_filename(self):
        data = criar_zip([("safe.txt", b"a")]).replace(b"safe.txt", b"bad\x00.txt")
        with self.assertRaises(ArquivoInvalido):
            self.inspecionar(data)

    def test_rejects_system_metadata(self):
        for name in ("__MACOSX/a", "pasta/.DS_Store", "Thumbs.db"):
            with self.subTest(name=name), self.assertRaises(ArquivoInvalido):
                self.inspecionar(criar_zip([(name, b"a")]))

    def test_rejects_ambiguous_normalized_paths(self):
        for names in (("a.txt", "a.txt"), ("a.txt", "A.TXT"), ("pasta/a.txt", "pasta/./a.txt"), ("pasta/a.txt", "pasta\\a.txt"), ("café.txt", "cafe\u0301.txt")):
            with self.subTest(names=names), self.assertRaises(ArquivoInvalido):
                self.inspecionar(criar_zip([(name, b"a") for name in names]))

    def test_rejects_symlink_and_special_entries(self):
        for kind in (stat.S_IFLNK, stat.S_IFIFO, stat.S_IFCHR, stat.S_IFBLK, stat.S_IFSOCK):
            info = zipfile.ZipInfo("especial")
            info.create_system = 3
            info.external_attr = (kind | 0o600) << 16
            with self.subTest(kind=kind), self.assertRaises(ArquivoInvalido):
                self.inspecionar(criar_zip([(info, b"a")]))

    def test_rejects_encryption_and_other_compression(self):
        with self.assertRaises(ArquivoInvalido):
            self.inspecionar(adulterar(criar_zip([("a", b"a")]), flags=1))
        for method in (zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA):
            with self.subTest(method=method), self.assertRaises(ArquivoInvalido):
                self.inspecionar(criar_zip([("a", b"a")], method))

    def test_limits_include_directories_and_count_before_zipfile(self):
        data = criar_zip([("a/", b""), ("b/", b""), ("b/f.txt", b"a")])
        with patch("laboratorios.services.zip_validator.zipfile.ZipFile") as constructor:
            with self.assertRaises(LimiteExcedido):
                self.inspecionar(data, replace(self.limites, entradas=2))
            constructor.assert_not_called()

    def test_counts_real_central_records_despite_false_declared_count(self):
        data = bytearray(criar_zip([("a", b"a"), ("b", b"b")]))
        end = data.rfind(b"PK\x05\x06")
        struct.pack_into("<2H", data, end + 8, 1, 1)
        with self.assertRaises(LimiteExcedido):
            self.inspecionar(bytes(data), replace(self.limites, entradas=1))

    def test_limits_declared_sizes_and_upload_size(self):
        data = criar_zip([("a", b"12345"), ("b", b"12345")])
        for limits in (
            replace(self.limites, upload_bytes=len(data) - 1),
            replace(self.limites, entrada_bytes=4),
            replace(self.limites, descompactado_bytes=9),
        ):
            with self.subTest(limits=limits), self.assertRaises(LimiteExcedido):
                self.inspecionar(data, limits)

    def test_bounds_real_output_when_size_is_falsified(self):
        for method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            data = adulterar(criar_zip([("a", b"x" * 10000)], method), tamanho=1)
            with self.subTest(method=method), self.assertRaises(LimiteExcedido):
                self.inspecionar(data, replace(self.limites, entrada_bytes=8))

    def test_bounds_real_total_when_second_size_is_falsified(self):
        data = adulterar(criar_zip([("a", b"123456"), ("b", b"123456")]), indice=1, tamanho=1)
        with self.assertRaises(LimiteExcedido):
            self.inspecionar(data, replace(self.limites, descompactado_bytes=8))

    def test_detects_wrong_crc_truncation_and_size(self):
        original = criar_zip([("a", b"abc")])
        for data in (adulterar(original, crc=0), original[:-10], adulterar(original, tamanho=1)):
            with self.subTest(data=data[:12]), self.assertRaises(ArquivoInvalido):
                self.inspecionar(data)

    def test_rejects_overlapping_entries(self):
        data = adulterar(criar_zip([("a", b"a"), ("b", b"b")]), comprimido=100)
        with self.assertRaises(ArquivoInvalido):
            self.inspecionar(data)

    def test_rejects_mismatched_local_header(self):
        original = criar_zip([("a", b"a")])
        for offset, value in ((6, 1), (8, zipfile.ZIP_STORED)):
            data = bytearray(original)
            struct.pack_into("<H", data, offset, value)
            with self.subTest(offset=offset), self.assertRaises(ArquivoInvalido):
                self.inspecionar(bytes(data))

    def test_accepts_archive_written_with_data_descriptor(self):
        class NonSeekable(BytesIO):
            def seek(self, *args):
                raise OSError("fluxo sem seek")
        buffer = NonSeekable()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("a", b"abc")
        self.assertEqual(self.inspecionar(buffer.getvalue()).total_bytes, 3)

    def test_rejects_zip64_marker(self):
        data = bytearray(criar_zip([("a", b"a")]))
        struct.pack_into("<2H", data, data.rfind(b"PK\x05\x06") + 8, 65535, 65535)
        with self.assertRaises(ArquivoInvalido):
            self.inspecionar(bytes(data))

    def test_rejects_entry_starting_on_another_disk(self):
        data = bytearray(criar_zip([("a", b"a")]))
        struct.pack_into("<H", data, data.find(b"PK\x01\x02") + 34, 1)
        with self.assertRaises(ArquivoInvalido):
            self.inspecionar(bytes(data))

    def test_nested_zip_is_not_opened_or_extracted(self):
        data = criar_zip([("interno.zip", b"ZIP interno propositalmente invalido")])
        with patch.object(zipfile.ZipFile, "extractall") as extractall, patch.object(zipfile.ZipFile, "extract") as extract:
            result = self.inspecionar(data)
            self.assertEqual(result.caminhos, ("interno.zip",))
            extractall.assert_not_called()
            extract.assert_not_called()

    def test_accepts_exact_uncompressed_limits(self):
        result = self.inspecionar(criar_zip([("a", b"1234")]), replace(self.limites, entrada_bytes=4, descompactado_bytes=4))
        self.assertEqual(result.total_bytes, 4)

    def test_streams_large_valid_members_in_bounded_blocks(self):
        entries = [("a", b"x" * 90000), ("b", b"y" * 90000)]
        limits = LimitesZIP(300000, 100, 180000, 90000)
        for method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            with self.subTest(method=method):
                self.assertEqual(self.inspecionar(criar_zip(entries, method), limits).total_bytes, 180000)


class TestValidacaoZIPView(SimpleTestCase):
    def post_zip(self, data):
        return self.client.post(reverse("laboratorios:organizar_arquivos"), {
            "arquivo_zip": SimpleUploadedFile("exemplo.zip", data),
        })

    def test_invalid_structure_is_rejected_with_safe_message(self):
        for data in (b"nao e ZIP", criar_zip([("../arquivo", b"a")]), adulterar(criar_zip([("a", b"a")]), crc=0)):
            response = self.post_zip(data)
            self.assertContains(response, "Não foi possível receber o arquivo", status_code=400)
            self.assertNotContains(response, "Traceback", status_code=400)
            self.assertNotContains(response, "ZIP validado:", status_code=400)

    @override_settings(MAX_ZIP_UNCOMPRESSED_BYTES=3)
    def test_expansion_limit_is_applied_by_form(self):
        response = self.post_zip(criar_zip([("a", b"1234")]))
        self.assertContains(response, "tamanho total permitido", status_code=400)

    def test_valid_zip_shows_file_count_without_generating_result(self):
        response = self.post_zip(criar_zip([("a/", b""), ("a/1.txt", b"a"), ("2.txt", b"b")]))
        self.assertContains(response, "ZIP validado:")
        self.assertContains(response, "2 arquivos")
        self.assertContains(response, "nenhum resultado foi gerado")

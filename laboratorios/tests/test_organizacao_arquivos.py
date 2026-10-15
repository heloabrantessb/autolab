"""Organização e inventário em área exclusiva, sem extração dos uploads."""

from concurrent.futures import ThreadPoolExecutor
import csv
from dataclasses import replace
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED

from django.conf import settings
from django.test import SimpleTestCase

from laboratorios.services.arquivo_service import organizar_zip
from laboratorios.services.zip_validator import ArquivoInvalido, LimiteExcedido, LimitesZIP
from .test_validacao_zip import criar_zip


class TestOrganizacaoArquivos(SimpleTestCase):
    limites = LimitesZIP(1000000, 100, 2000000, 1000000)

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.raiz = Path(self.temp.name)
        self.area = self.raiz / "trabalho"
        self.area.mkdir()
        self.entrada = self.raiz / "entrada.zip"

    def organizar(self, entradas, *, limites=None, compressao=ZIP_DEFLATED):
        self.entrada.write_bytes(criar_zip(entradas, compressao))
        return organizar_zip(self.entrada, self.area, limites=limites or self.limites)

    def linhas(self, archive):
        return list(csv.DictReader(StringIO(archive.read("relatorio.csv").decode("utf-8"))))

    def test_example_generates_expected_archive_and_inventory(self):
        self.entrada.write_bytes((settings.BASE_DIR / "materials/arquivos/exemplo.zip").read_bytes())
        original = self.entrada.read_bytes()
        result = organizar_zip(self.entrada, self.area, limites=self.limites)
        self.assertEqual(result.total_arquivos, 6)
        self.assertEqual(result.por_categoria, {"Documentos": 3, "Planilhas": 1, "Imagens": 1, "Outros": 1})
        self.assertTrue(result.output_path.is_relative_to(self.area))
        self.assertEqual(self.entrada.read_bytes(), original)
        with ZipFile(result.output_path) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), {
                "Documentos/", "Planilhas/", "Imagens/", "Outros/", "relatorio.csv",
                "Documentos/comunicado.txt", "Documentos/comunicado_2.txt", "Documentos/notas.txt",
                "Planilhas/clientes.csv", "Imagens/marca.png", "Outros/LEIA-ME",
            })
            self.assertNotEqual(archive.read("Documentos/comunicado.txt"), archive.read("Documentos/comunicado_2.txt"))
            rows = self.linhas(archive)
            self.assertEqual(len(rows), 6)
            self.assertEqual(list(rows[0]), ["caminho_original", "nome_saida", "categoria", "status"])
            self.assertIn("subpasta/comunicado.txt", [row["caminho_original"] for row in rows])
            self.assertEqual(sum(row["status"] == "renomeado" for row in rows), 1)
        self.assertEqual(len(result.avisos), 1)

    def test_extensions_are_case_insensitive_and_unknown_goes_to_outros(self):
        result = self.organizar([("foto.JPG", b"a"), ("DADOS.CSV", b"b"), ("LEIA-ME", b"c"), ("arquivo.bin", b"d")])
        self.assertEqual(result.por_categoria, {"Documentos": 0, "Planilhas": 1, "Imagens": 1, "Outros": 2})
        with ZipFile(result.output_path) as archive:
            self.assertIn("Documentos/", archive.namelist())
            self.assertEqual(archive.read("Imagens/foto.JPG"), b"a")
            self.assertEqual(archive.read("Planilhas/DADOS.CSV"), b"b")

    def test_names_do_not_collide_with_generated_suffixes(self):
        result = self.organizar([
            ("a/relatorio.txt", b"a"), ("b/RELATORIO.TXT", b"b"),
            ("c/relatorio_2.txt", b"c"), ("d/Relatorio.txt", b"d"),
        ])
        with ZipFile(result.output_path) as archive:
            rows = self.linhas(archive)
            self.assertEqual(len({row["nome_saida"].casefold() for row in rows}), 4)
            self.assertEqual({archive.read(row["nome_saida"]) for row in rows}, {b"a", b"b", b"c", b"d"})
            self.assertIn("Documentos/Relatorio_3.txt", archive.namelist())

    def test_normalizes_unicode_and_resolves_collisions(self):
        result = self.organizar([("a/cafe\u0301.txt", b"a"), ("b/café.txt", b"b")])
        with ZipFile(result.output_path) as archive:
            self.assertEqual(archive.read("Documentos/café.txt"), b"a")
            self.assertEqual(archive.read("Documentos/café_2.txt"), b"b")
            self.assertTrue(all(row["status"] == "renomeado" for row in self.linhas(archive)))

    def test_sanitizes_special_and_reserved_names(self):
        result = self.organizar([("CON.txt", b"a"), ("AUX.foo.txt", b"b"), ("<planilha>.csv", b"c"), ("nome?.txt", b"d"), ("...", b"e")])
        with ZipFile(result.output_path) as archive:
            for name in ("Documentos/_CON.txt", "Documentos/_AUX.foo.txt", "Planilhas/_planilha_.csv", "Documentos/nome_.txt", "Outros/arquivo"):
                self.assertIn(name, archive.namelist())

    def test_long_utf8_names_and_suffixes_stay_within_portable_limit(self):
        name = "á" * 200 + ".txt"
        result = self.organizar([("a/" + name, b"a"), ("b/" + name, b"b")])
        with ZipFile(result.output_path) as archive:
            rows = self.linhas(archive)
            for row in rows:
                basename = row["nome_saida"].rsplit("/", 1)[-1]
                self.assertLessEqual(len(basename.encode("utf-8")), 200)
            self.assertNotEqual(rows[0]["nome_saida"], rows[1]["nome_saida"])

    def test_inventory_neutralizes_formulas_and_quotes_csv_correctly(self):
        names = ["=formula.txt", "+formula.txt", "-formula.txt", "@formula.txt", " =formula.txt", 'nome,"aspas".txt']
        result = self.organizar([(name, b"a") for name in names])
        with ZipFile(result.output_path) as archive:
            rows = self.linhas(archive)
            for row in rows:
                original = row["caminho_original"]
                if "formula" in original:
                    self.assertTrue(original.startswith("'"))
                else:
                    self.assertEqual(original, 'nome,"aspas".txt')
                self.assertEqual(archive.read(row["nome_saida"]), b"a")

    def test_archive_is_deterministic_regardless_of_input_order(self):
        entries = [("b/a.txt", b"b"), ("a/a.txt", b"a")]
        first = self.organizar(entries)
        second = self.organizar(list(reversed(entries)))
        self.assertNotEqual(first.output_path, second.output_path)
        self.assertEqual(first.output_path.read_bytes(), second.output_path.read_bytes())

    def test_input_report_name_does_not_overwrite_generated_inventory(self):
        result = self.organizar([("relatorio.csv", b"original")])
        with ZipFile(result.output_path) as archive:
            self.assertEqual(archive.read("Planilhas/relatorio.csv"), b"original")
            self.assertEqual(len(self.linhas(archive)), 1)
            self.assertEqual(result.total_arquivos, 1)

    def test_rejects_traversal_before_creating_output(self):
        with self.assertRaises(ArquivoInvalido):
            self.organizar([("../fora.txt", b"a")])
        self.assertEqual(list(self.area.iterdir()), [])
        self.assertFalse((self.raiz / "fora.txt").exists())

    def test_limits_still_apply_to_organization(self):
        with self.assertRaises(LimiteExcedido):
            self.organizar([("a.txt", b"abcde")], limites=replace(self.limites, entrada_bytes=4))
        self.assertEqual(list(self.area.iterdir()), [])

    def test_copy_failure_removes_only_its_own_execution(self):
        previous = self.organizar([("a.txt", b"a")])
        original = self.entrada.read_bytes()
        def falhar_apos_escrita(entrada, archive, info, destino, limites, **kwargs):
            destino.write(b"saida parcial")
            raise OSError("falha simulada")

        with patch("laboratorios.services.arquivo_service.copiar_entrada_zip", side_effect=falhar_apos_escrita):
            with self.assertRaises(OSError):
                organizar_zip(self.entrada, self.area, limites=self.limites)
        self.assertEqual(list(self.area.iterdir()), [previous.output_path.parent])
        self.assertTrue(previous.output_path.is_file())
        self.assertEqual(self.entrada.read_bytes(), original)

    def test_parallel_runs_have_independent_outputs(self):
        self.entrada.write_bytes(criar_zip([("a.txt", b"a")]))
        def run(_):
            return organizar_zip(self.entrada, self.area, limites=self.limites)
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(run, range(2)))
        self.assertNotEqual(results[0].output_path.parent, results[1].output_path.parent)
        self.assertEqual(results[0].output_path.read_bytes(), results[1].output_path.read_bytes())

    def test_streams_both_methods_and_keeps_payload_exact(self):
        payload = b"conteudo" * 20000
        for method in (ZIP_STORED, ZIP_DEFLATED):
            with self.subTest(method=method):
                result = self.organizar([("arquivo.txt", payload)], compressao=method)
                with ZipFile(result.output_path) as archive:
                    self.assertEqual(archive.read("Documentos/arquivo.txt"), payload)

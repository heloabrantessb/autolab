"""Distribuição do exercício e verificação local sem executar código no site."""

from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from zipfile import ZipFile

from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class TestExercicioArquivos(SimpleTestCase):
    def setUp(self):
        self.pasta = settings.BASE_DIR / "codespaces_exercises/arquivos"
        self.detalhe = reverse("exercicios:detalhe", kwargs={"slug": "organizacao-arquivos"})
        self.materiais = reverse("exercicios:materiais_arquivos")

    def carregar_apoio(self):
        spec = spec_from_file_location("apoio_do_exercicio", self.pasta / "apoio.py")
        apoio = module_from_spec(spec)
        spec.loader.exec_module(apoio)
        return apoio

    def test_listing_detail_and_lab_link_to_the_activity(self):
        self.assertContains(self.client.get(reverse("exercicios:lista")), f'href="{self.detalhe}"')
        page = self.client.get(self.detalhe)
        for text in ("categoria", "nome_unico", "linha_inventario", "python tests/verificar.py", "não recebe nem executa", "validação no serviço hospedado ainda está pendente"):
            self.assertContains(page, text)
        self.assertContains(page, f'href="{self.materiais}"')
        self.assertContains(self.client.get(reverse("laboratorios:arquivos")), f'href="{self.detalhe}"')

    def test_unknown_slug_and_mutations_are_rejected(self):
        self.assertEqual(self.client.get(reverse("exercicios:detalhe", kwargs={"slug": "nao-existe"})).status_code, 404)
        for url in (reverse("exercicios:lista"), self.detalhe, self.materiais):
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url).status_code, 405)
                self.assertEqual(self.client.head(url).status_code, 200)

    def test_bundle_contains_only_fixed_public_material_and_no_solution(self):
        response = self.client.get(self.materiais, {"arquivo": "../../.env", "referencia": "true"})
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn("autolab-exercicio-arquivos.zip", response["Content-Disposition"])
        with ZipFile(BytesIO(b"".join(response.streaming_content))) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), {"README.md", "starter.py", "apoio.py", "tests/verificar.py", "exemplo.zip"})
            self.assertIn(b"NotImplementedError", archive.read("starter.py"))
            self.assertEqual(archive.read("exemplo.zip"), (settings.BASE_DIR / "materials/arquivos/exemplo.zip").read_bytes())
            self.assertEqual(archive.read("apoio.py"), (self.pasta / "apoio.py").read_bytes())

    def test_missing_material_returns_404(self):
        with TemporaryDirectory() as area, override_settings(BASE_DIR=Path(area)):
            self.assertEqual(self.client.get(self.materiais).status_code, 404)

    def test_reference_passes_all_student_criteria_in_isolated_python(self):
        result = subprocess.run(
            [sys.executable, "-I", "-S", str(self.pasta / "tests/verificar.py"), "--referencia"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ran 6 tests", result.stderr)
        self.assertIn("OK", result.stderr)

    def test_starter_reports_pending_todos_and_does_not_create_output(self):
        with TemporaryDirectory() as area:
            output = Path(area) / "resultado.zip"
            result = subprocess.run(
                [sys.executable, "-S", str(self.pasta / "starter.py"), "--saida", str(output)],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("TODOs", result.stderr)
            self.assertFalse(output.exists())

    def test_downloaded_bundle_is_self_contained_and_checks_the_starter(self):
        response = self.client.get(self.materiais)
        data = b"".join(response.streaming_content)
        with TemporaryDirectory() as area, ZipFile(BytesIO(data)) as archive:
            root = Path(area)
            for name in ("README.md", "starter.py", "apoio.py", "tests/verificar.py", "exemplo.zip"):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
            result = subprocess.run(
                [sys.executable, "-I", "-S", str(root / "tests/verificar.py")], cwd=root,
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("NotImplementedError", result.stderr)
            self.assertNotIn("ModuleNotFoundError", result.stderr)
            self.assertFalse(list(root.glob("resultado*.zip")))
            # Simula o participante concluindo os TODOs, sem acrescentar arquivos
            # ao pacote ou instalar dependências.
            (root / "starter.py").write_bytes((self.pasta / "referencia.py").read_bytes())
            completed = subprocess.run(
                [sys.executable, "-I", "-S", str(root / "tests/verificar.py")], cwd=root,
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Ran 6 tests", completed.stderr)
            output = root / "resultado.zip"
            executed = subprocess.run(
                [sys.executable, "-S", str(root / "starter.py"), "--saida", str(output)], cwd=root,
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(executed.returncode, 0, executed.stderr)
            self.assertIn("Total: 6", executed.stdout)
            with ZipFile(output) as organized:
                self.assertIsNone(organized.testzip())
                self.assertIn("Documentos/comunicado_2.txt", organized.namelist())

    def test_modified_example_is_rejected_before_opening_zip_or_running_todos(self):
        apoio = self.carregar_apoio()
        with TemporaryDirectory() as area:
            root = Path(area)
            sample = root / "alterado.zip"
            sample.write_bytes(b"nao e o material ficticio")
            output = root / "resultado.zip"
            todo = Mock()
            with patch.object(apoio, "ZipFile") as zip_class:
                with self.assertRaises(ValueError):
                    apoio.organizar(todo, todo, todo, output, exemplo=sample)
                zip_class.assert_not_called()
            todo.assert_not_called()
            self.assertFalse(output.exists())

    def test_bad_student_outputs_are_rejected_before_writing(self):
        apoio = self.carregar_apoio()
        for category, name, row in (
            (lambda _: "desconhecido", lambda n, _: n, lambda *r: r),
            (lambda _: "Outros", lambda *_: "../fora.txt", lambda *r: r),
            (lambda _: "Outros", lambda n, _: n, lambda *r: ("faltam", "colunas")),
            (lambda _: "Outros", lambda *_: "repetido.txt", lambda *r: (*r, "organizado")),
        ):
            with TemporaryDirectory() as area:
                output = Path(area) / "resultado.zip"
                with self.assertRaises(ValueError):
                    apoio.organizar(category, name, row, output)
                self.assertFalse(output.exists())

    def test_partial_output_is_removed_after_write_failure(self):
        apoio = self.carregar_apoio()
        sequencia = iter(range(6))
        with TemporaryDirectory() as area:
            output = Path(area) / "resultado.zip"
            with patch.object(apoio.ZipFile, "writestr", side_effect=OSError("falha simulada")):
                with self.assertRaises(OSError):
                    apoio.organizar(lambda _: "Outros", lambda *_: f"{next(sequencia)}.txt",
                                    lambda *r: (*r, "organizado"), output)
            self.assertFalse(output.exists())

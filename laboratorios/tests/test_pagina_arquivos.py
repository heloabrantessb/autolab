"""Página didática e material público, sem processamento de uploads."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class TestPaginaArquivos(SimpleTestCase):
    def test_page_has_six_accessible_steps(self):
        response = self.client.get(reverse("laboratorios:arquivos"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "partials/lab_tabs.html")
        for slug, title in (
            ("aprender", "Aprender"), ("executar", "Executar"),
            ("codigo", "Código Python"), ("exercicio", "Exercício"),
            ("desafio", "Desafio"), ("resultado", "Resultado"),
        ):
            with self.subTest(slug=slug):
                self.assertContains(response, f'aria-controls="arquivos-{slug}"')
                self.assertContains(response, f'aria-labelledby="arquivos-{slug}-tab"')
                self.assertContains(response, title)
        self.assertContains(response, 'role="tabpanel"', count=6)
        self.assertContains(response, "Categorias previstas")

    def test_page_distinguishes_reference_from_execution(self):
        response = self.client.get(reverse("laboratorios:arquivos"))
        self.assertContains(response, "A organização de arquivos ainda não está disponível.")
        self.assertContains(response, "Esta é uma referência didática, não o resultado de uma execução.")
        self.assertContains(response, "Exercício no Codespaces em breve")
        self.assertContains(response, '<input type="file"')
        self.assertContains(response, "comunicado_2.txt")
        self.assertContains(response, "relatorio.csv")

    def test_zip_download_contains_only_expected_material(self):
        response = self.client.get(reverse("laboratorios:exemplo_arquivos"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn('attachment;', response["Content-Disposition"])
        self.assertIn('autolab-arquivos-exemplo.zip', response["Content-Disposition"])
        data = b"".join(response.streaming_content)
        response.close()
        with ZipFile(BytesIO(data)) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), {
                "comunicado.txt", "notas.txt", "subpasta/comunicado.txt",
                "clientes.csv", "marca.png", "LEIA-ME",
            })
            self.assertNotEqual(archive.read("comunicado.txt"), archive.read("subpasta/comunicado.txt"))
            self.assertTrue(archive.read("marca.png").startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertIn("fictício", archive.read("comunicado.txt").decode())

    def test_download_ignores_client_supplied_path(self):
        response = self.client.get(reverse("laboratorios:exemplo_arquivos"), {"arquivo": "../.env"})
        data = b"".join(response.streaming_content)
        response.close()
        with ZipFile(BytesIO(data)) as archive:
            self.assertEqual(len(archive.namelist()), 6)
            self.assertNotIn(".env", archive.namelist())

    def test_missing_example_returns_404(self):
        with TemporaryDirectory() as directory, override_settings(BASE_DIR=Path(directory)):
            response = self.client.get(reverse("laboratorios:exemplo_arquivos"))
        self.assertEqual(response.status_code, 404)

    def test_page_and_example_reject_post(self):
        for route in ("laboratorios:arquivos", "laboratorios:exemplo_arquivos"):
            with self.subTest(route=route):
                self.assertEqual(self.client.post(reverse(route)).status_code, 405)

"""Prévia web de dados de entrada, com conteúdo escapado e sem persistência."""

from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from .test_planilha_reader import xlsx_bytes


class TestPreviaPlanilhas(SimpleTestCase):
    def upload(self, dados, nome="entrada.csv"):
        return self.client.post(reverse("laboratorios:receber_planilha"), {
            "arquivo_planilha": SimpleUploadedFile(nome, dados, content_type="application/octet-stream"),
        })

    def test_fixture_preview_has_eight_rows_and_does_not_clean(self):
        dados = (Path(__file__).resolve().parents[2] / "materials/planilhas/clientes.csv").read_bytes()
        response = self.upload(dados)
        self.assertContains(response, "Planilha lida para prévia")
        tabela = response.context["tabela"]
        self.assertEqual(len(tabela.linhas), 8)
        self.assertEqual(tabela.linhas[0], tabela.linhas[1])
        self.assertEqual(tabela.linhas[2][1], " Bruno Exemplo ")
        self.assertEqual(tabela.linhas[4], ("", "", "", "", ""))
        self.assertContains(response, "003")
        self.assertContains(response, "não foram limpos")
        self.assertNotContains(response, "<input type=\"hidden\" name=\"dados\"")

    def test_xlsx_text_ids_and_formula_are_displayed_without_calculation(self):
        response = self.upload(xlsx_bytes([["id", "valor"], ["001", "=1+1"]]), "entrada.XLSX")
        self.assertContains(response, "XLSX")
        self.assertContains(response, ">001</td>")
        self.assertContains(response, "=1+1")
        self.assertContains(response, "sem cálculo")

    def test_html_cells_and_headers_are_escaped(self):
        response = self.upload(b'<img src=x onerror=alert(1)>\n<script>alert(2)</script>\n')
        self.assertContains(response, "&lt;img")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(2)</script>")
        self.assertNotContains(response, "<img src=x")

    def test_preview_only_shows_first_ten_rows(self):
        dados = "id\n" + "\n".join(f"registro-{i:02}" for i in range(12)) + "\n"
        response = self.upload(dados.encode())
        self.assertContains(response, "registro-09")
        self.assertNotContains(response, "registro-10")
        self.assertEqual(len(response.context["tabela"].linhas), 12)

    @override_settings(MAX_SPREADSHEET_ROWS=1, MAX_SPREADSHEET_COLUMNS=2)
    def test_configured_dimensions_are_enforced_in_web_flow(self):
        response = self.upload(b"a,b\n1,2\n3,4\n")
        self.assertContains(response, "limite de 1 linhas", status_code=400)
        response = self.upload(b"a,b,c\n1,2,3\n")
        self.assertContains(response, "até 2 colunas", status_code=400)

    def test_malformed_content_returns_error_without_success_or_preview(self):
        for dados, nome in ((b"falso", "a.xlsx"), (b'a,b\n1,"sem fim', "a.csv")):
            with self.subTest(nome=nome):
                response = self.upload(dados, nome)
                self.assertContains(response, "Não foi possível receber a planilha", status_code=400)
                self.assertNotContains(response, "Planilha lida para prévia", status_code=400)
                self.assertIsNone(response.context["tabela"])

    def test_reading_has_no_database_or_result_files(self):
        with TemporaryDirectory() as area, override_settings(RESULTS_ROOT=Path(area)):
            self.assertEqual(self.upload(b"a\n001\n").status_code, 200)
            self.assertEqual(list(Path(area).iterdir()), [])
        # SimpleTestCase proíbe consultas, inclusive criação de metadados de resultado.

    def test_long_preview_text_is_abbreviated_without_changing_read_data(self):
        cabecalho = "a" * 100 + "fim-cabecalho"
        celula = "x" * 300 + "fim-celula"
        response = self.upload(f"{cabecalho}\n{celula}\n".encode())
        self.assertNotContains(response, "fim-cabecalho")
        self.assertNotContains(response, "fim-celula")
        self.assertEqual(response.context["tabela"].cabecalho, (cabecalho,))
        self.assertEqual(response.context["tabela"].linhas, ((celula,),))

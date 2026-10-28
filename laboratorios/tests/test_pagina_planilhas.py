"""Conteúdo didático de Planilhas e material fictício, sem processamento."""

import csv
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class TestPaginaPlanilhas(SimpleTestCase):
    def test_six_steps_reuse_lab_navigation_and_define_scope(self):
        response = self.client.get(reverse("laboratorios:planilhas"))
        self.assertTemplateUsed(response, "partials/lab_tabs.html")
        self.assertContains(response, 'role="tabpanel"', count=6)
        for slug in ("aprender", "executar", "codigo", "exercicio", "desafio", "resultado"):
            self.assertContains(response, f'aria-controls="planilhas-{slug}"')
            self.assertContains(response, f'aria-labelledby="planilhas-{slug}-tab"')
        self.assertContains(response, "Limpeza e exportação ainda estão em preparação.")
        self.assertContains(response, "não o resultado de uma execução no site")
        self.assertContains(response, "Não apague linhas parcialmente preenchidas")
        self.assertContains(response, "XLS e XLSM ficam fora deste corte")
        self.assertContains(response, "Processamento de planilhas em breve")
        self.assertContains(response, '<input type="file"')

    def test_sample_matches_educational_counts_and_preserves_partial_records(self):
        response = self.client.get(reverse("laboratorios:exemplo_planilhas"), {"path": "../../.env"})
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("autolab-clientes-exemplo.csv", response["Content-Disposition"])
        self.assertIn("attachment;", response["Content-Disposition"])
        rows = list(csv.DictReader(StringIO(b"".join(response.streaming_content).decode("utf-8"))))
        self.assertEqual(len(rows), 8)
        self.assertEqual(list(rows[0]), ["id", "nome", "email", "setor", "observacao"])
        self.assertEqual(rows[0], rows[1])
        self.assertEqual(sum(all(value == "" for value in row.values()) for row in rows), 1)
        # Confere a referência fixa publicada, não implementa serviço de limpeza.
        normalizadas = [tuple(value.strip() for value in row.values()) for row in rows]
        referencia = list(dict.fromkeys(row for row in normalizadas if any(row)))
        self.assertEqual(len(referencia), 5)
        self.assertEqual([row[0] for row in referencia], ["001", "002", "003", "004", "005"])
        self.assertEqual(referencia[2][2], "")
        self.assertTrue(all(row["email"].endswith("@example.invalid") for row in rows if row["email"]))

    def test_missing_sample_returns_404(self):
        with TemporaryDirectory() as area, override_settings(BASE_DIR=Path(area)):
            response = self.client.get(reverse("laboratorios:exemplo_planilhas"))
        self.assertEqual(response.status_code, 404)

    def test_page_and_sample_are_read_only(self):
        for route in ("laboratorios:planilhas", "laboratorios:exemplo_planilhas"):
            with self.subTest(route=route):
                self.assertEqual(self.client.post(reverse(route)).status_code, 405)
                self.assertEqual(self.client.head(reverse(route)).status_code, 200)

    def test_navigation_offers_learning_without_claiming_automation_available(self):
        response = self.client.get(reverse("laboratorios:planilhas"))
        self.assertContains(response, 'href="/laboratorios/planilhas/"', count=2)
        self.assertContains(response, "Planilhas: aprender", count=2)
        catalogo = self.client.get(reverse("core:catalogo"))
        self.assertContains(catalogo, 'disabled aria-label="Planilhas: em breve"')
        self.assertNotContains(catalogo, 'aria-label="Acessar Planilhas"')

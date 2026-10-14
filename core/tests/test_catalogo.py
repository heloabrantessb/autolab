"""Critérios de navegação e disponibilidade do catálogo."""

from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse


class TestCatalogo(SimpleTestCase):
    def test_catalogo_lists_six_labs_with_levels_and_summaries(self):
        response = self.client.get(reverse("core:catalogo"))
        self.assertContains(response, "Primeiros laboratórios")
        self.assertContains(response, "Módulos futuros")
        for title in ("Arquivos &amp; Pastas", "Planilhas", "IA &amp; Prompts", "PDFs", "APIs", "Automação Web"):
            with self.subTest(title=title):
                self.assertContains(response, title)
        self.assertContains(response, "Nível: Iniciante", count=2)
        self.assertContains(response, "Nível: Básico", count=4)
        self.assertContains(response, "gere um inventário")
        self.assertContains(response, "HTTP e JSON")
        self.assertContains(response, "relatórios")

    def test_incomplete_labs_have_no_execution_links(self):
        response = self.client.get(reverse("core:catalogo"))
        self.assertContains(response, 'class="badge badge-status-em-breve px-2 py-1"', count=6)
        self.assertContains(response, 'disabled aria-label=', count=6)
        self.assertNotContains(response, "badge-status-disponivel")
        self.assertNotContains(response, ">Acessar</a>")

    def test_home_only_highlights_mvp(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'class="autolab-card p-4 h-100 d-flex flex-column"', count=3)
        for title in ("PDFs", "APIs", "Automação Web"):
            self.assertNotContains(response, title)

    def test_availability_change_applies_to_home_and_catalogo(self):
        lab = {
            "slug": "arquivos", "titulo": "Arquivos & Pastas",
            "resumo": "Exemplo", "nivel": "Iniciante", "mvp": True,
            "disponivel": True, "rota": "laboratorios:arquivos",
        }
        with patch("core.views.LABORATORIOS", (lab,)):
            for route in ("core:home", "core:catalogo"):
                with self.subTest(route=route):
                    response = self.client.get(reverse(route))
                    self.assertContains(response, "badge-status-disponivel")
                    self.assertContains(response, '<a href="/laboratorios/arquivos/" class="btn btn-sm btn-outline-primary" aria-label="Acessar Arquivos &amp; Pastas">Acessar</a>', html=True)

    def test_available_flag_without_route_does_not_offer_execution(self):
        lab = {
            "slug": "planilhas", "titulo": "Planilhas",
            "resumo": "Exemplo", "nivel": "Iniciante", "mvp": True,
            "disponivel": True, "rota": None,
        }
        with patch("core.views.LABORATORIOS", (lab,)):
            response = self.client.get(reverse("core:catalogo"))
        self.assertNotContains(response, ">Acessar</a>")
        self.assertNotContains(response, "badge-status-disponivel")
        self.assertContains(response, 'disabled aria-label="Planilhas: em breve"')

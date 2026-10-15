"""Testes da pagina inicial / dashboard."""

from django.test import SimpleTestCase
from django.urls import reverse


class TestHomePage(SimpleTestCase):
    """Testa conteudo e estrutura da pagina inicial."""

    def setUp(self):
        self.url = reverse("core:home")
        self.response = self.client.get(self.url)

    def test_home_status_200(self):
        """Pagina inicial responde com status 200."""
        self.assertEqual(self.response.status_code, 200)

    def test_home_uses_correct_template(self):
        """Pagina inicial usa template core/home.html."""
        self.assertTemplateUsed(self.response, "core/home.html")
        self.assertTemplateUsed(self.response, "base.html")

    def test_home_contains_hero_section(self):
        """Pagina inicial contem secao hero com titulo e CTA."""
        self.assertContains(self.response, "Bem-vindo ao AutoLab")
        self.assertContains(self.response, "Explorar Laboratórios")

    def test_home_contains_three_steps(self):
        """Pagina inicial apresenta fluxo em 3 passos."""
        self.assertContains(self.response, "1. Aprenda")
        self.assertContains(self.response, "2. Execute")
        self.assertContains(self.response, "3. Resolva")

    def test_home_contains_lab_cards(self):
        """Pagina inicial mostra cards dos laboratorios MVP."""
        self.assertContains(self.response, "Arquivos &amp; Pastas")
        self.assertContains(self.response, "Planilhas")
        self.assertContains(self.response, "IA &amp; Prompts")

    def test_home_shows_availability_badges(self):
        """Pagina inicial mostra badges de disponibilidade."""
        self.assertContains(self.response, '<span class="badge badge-status-em-breve px-2 py-1">Em breve</span>', count=2, html=True)
        self.assertContains(self.response, "badge-status-disponivel", count=1)
        self.assertContains(self.response, "Plataforma em desenvolvimento")

    def test_home_cta_links_to_catalogo(self):
        """CTA principal linka para o catalogo de laboratorios."""
        catalogo_url = reverse("core:catalogo")
        self.assertContains(self.response, f'href="{catalogo_url}"')

    def test_unavailable_lab_actions_are_disabled(self):
        """Somente Arquivos oferece acesso; demais módulos seguem em breve."""
        for label in (
            "Planilhas: em breve",
            "IA &amp; Prompts: em breve",
        ):
            with self.subTest(label=label):
                self.assertContains(
                    self.response,
                    f'<button type="button" class="btn btn-sm btn-outline-secondary" disabled aria-label="{label}">Em breve</button>',
                    html=True,
                )
        self.assertContains(self.response, 'aria-label="Acessar Arquivos &amp; Pastas"')

    def test_home_contains_codespaces_mention(self):
        """Pagina inicial menciona GitHub Codespaces."""
        self.assertContains(self.response, "Codespaces")

    def test_catalogo_uses_correct_template(self):
        """Pagina do catalogo usa template core/catalogo.html."""
        url = reverse("core:catalogo")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "core/catalogo.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Catálogo de Laboratórios")
        self.assertContains(response, "Primeiros laboratórios")
        self.assertContains(response, "Módulos futuros")

    def test_navigation_targets_show_preparation_state(self):
        """Destinos existentes usam layout e deixam as pendencias explicitas."""
        for route, template, message in (
            ("laboratorios:arquivos", "laboratorios/arquivos.html", "Envie um ZIP para organizar os arquivos"),
            ("exercicios:lista", "exercicios/lista.html", "Os exercícios e o ambiente Codespaces ainda estão em preparação."),
        ):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertTemplateUsed(response, template)
                self.assertTemplateUsed(response, "base.html")
                self.assertContains(response, message)

"""Testes de sanidade e integridade da configuracao inicial do Django."""

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import resolve, reverse


class TestSystemSanity(SimpleTestCase):
    """Testa integridade das configuracoes e rotas basicas do AutoLab."""

    def test_settings_loaded(self):
        """Verifica se configuracoes essenciais estao definidas corretamente."""
        self.assertTrue(hasattr(settings, "RESULTS_ROOT"))
        self.assertTrue(hasattr(settings, "RESULT_TTL_MINUTES"))
        self.assertTrue(hasattr(settings, "MAX_ZIP_UPLOAD_BYTES"))
        self.assertEqual(settings.RESULT_TTL_MINUTES, 30)
        self.assertFalse(settings.LLM_ENABLED)

    def test_core_home_resolves_and_responds(self):
        """Verifica se rota core:home resolve e responde 200."""
        url = reverse("core:home")
        self.assertEqual(url, "/")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_core_catalogo_resolves_and_responds(self):
        """Verifica se rota core:catalogo resolve e responde 200."""
        url = reverse("core:catalogo")
        self.assertEqual(url, "/laboratorios/")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_laboratorios_arquivos_resolves_and_responds(self):
        """Verifica se rota laboratorios:arquivos resolve e responde 200."""
        url = reverse("laboratorios:arquivos")
        self.assertEqual(url, "/laboratorios/arquivos/")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_exercicios_lista_resolves_and_responds(self):
        """Verifica se rota exercicios:lista resolve e responde 200."""
        url = reverse("exercicios:lista")
        self.assertEqual(url, "/exercicios/")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

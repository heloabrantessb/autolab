"""Inicialização da prévia, origem CSRF e links do ambiente de programação."""

import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, override_settings
from django.urls import reverse


class TestCodespaces(SimpleTestCase):
    def executar_inicio(self, ambiente, *, python_presente=True):
        with TemporaryDirectory() as area:
            root = Path(area)
            scripts = root / ".devcontainer"
            scripts.mkdir()
            script = scripts / "start-site.sh"
            script.write_bytes((settings.BASE_DIR / ".devcontainer/start-site.sh").read_bytes())
            if python_presente:
                python = root / ".venv/bin/python"
                python.parent.mkdir(parents=True)
                python.write_text(
                    '#!/bin/sh\nprintf "%s\\n" "$DJANGO_ALLOWED_HOSTS" "$DJANGO_CSRF_TRUSTED_ORIGINS" "$LLM_ENABLED" "$*"\n',
                )
                python.chmod(0o700)
            return subprocess.run(
                ["bash", str(script)], capture_output=True, text=True, timeout=5,
                env={"PATH": os.environ["PATH"], **ambiente},
            )

    def ambiente_codespaces(self):
        return {"CODESPACES": "true", "CODESPACE_NAME": "oficina-exemplo-123",
                "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN": "app.github.dev"}

    def test_preview_uses_only_current_forwarded_host_and_origin(self):
        env = self.ambiente_codespaces() | {"DJANGO_ALLOWED_HOSTS": "*", "DJANGO_CSRF_TRUSTED_ORIGINS": "https://outro.invalid", "LLM_ENABLED": "true"}
        result = self.executar_inicio(env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "localhost,127.0.0.1,oficina-exemplo-123-8000.app.github.dev",
            "https://oficina-exemplo-123-8000.app.github.dev", "false",
            "manage.py runserver 0.0.0.0:8000",
        ])

    def test_local_preview_preserves_explicit_hosts_and_disables_ai(self):
        result = self.executar_inicio({"DJANGO_ALLOWED_HOSTS": "localhost", "DJANGO_CSRF_TRUSTED_ORIGINS": "https://localhost", "LLM_ENABLED": "true"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[:3], ["localhost", "https://localhost", "false"])
        self.assertEqual(result.stdout.splitlines()[3], "manage.py runserver 127.0.0.1:8000")

    def test_missing_environment_or_setup_never_starts_the_server(self):
        result = self.executar_inicio({}, python_presente=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("setup.sh", result.stderr)
        for missing in ("CODESPACE_NAME", "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"):
            env = self.ambiente_codespaces()
            del env[missing]
            result = self.executar_inicio(env)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_forwarded_preview_accepts_csrf_only_from_its_origin(self):
        result = self.executar_inicio(self.ambiente_codespaces())
        hosts, origin = result.stdout.splitlines()[:2]
        host = hosts.split(",")[-1]
        with override_settings(ALLOWED_HOSTS=hosts.split(","), CSRF_TRUSTED_ORIGINS=[origin], DEBUG=False):
            client = Client(enforce_csrf_checks=True)
            page = client.get(reverse("laboratorios:arquivos"), secure=True, HTTP_HOST=host)
            self.assertEqual(page.status_code, 200)
            csrf = client.cookies["csrftoken"].value
            data = (settings.BASE_DIR / "materials/arquivos/exemplo.zip").read_bytes()
            def enviar(origem):
                return client.post(reverse("laboratorios:organizar_arquivos"), {
                    "csrfmiddlewaretoken": csrf, "arquivo_zip": SimpleUploadedFile("exemplo.zip", data),
                }, secure=True, HTTP_HOST=host, HTTP_ORIGIN=origem)
            with patch("laboratorios.views.criar_resultado", return_value=SimpleNamespace(token=uuid4())) as criar:
                self.assertEqual(enviar("https://outro.invalid").status_code, 403)
                criar.assert_not_called()
                self.assertEqual(enviar(origin).status_code, 303)
                criar.assert_called_once()

    def test_codespaces_links_select_integrated_dev_branch(self):
        for url in (reverse("laboratorios:arquivos"), reverse("exercicios:detalhe", kwargs={"slug": "organizacao-arquivos"})):
            response = self.client.get(url)
            self.assertContains(response, 'href="https://codespaces.new/heloabrantessb/autolab/tree/dev"')
            self.assertContains(response, 'rel="noopener noreferrer"')
            self.assertContains(response, "validação no serviço hospedado ainda está pendente")

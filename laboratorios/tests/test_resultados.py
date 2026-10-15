"""Fluxo real de upload, resumo e download de resultados privados."""

from datetime import timedelta
from io import BytesIO, StringIO
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from uuid import uuid4
from zipfile import ZipFile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from laboratorios.models import ResultadoTemporario
from laboratorios.services.resultados import caminho_resultado, criar_resultado
from laboratorios.services.zip_validator import ArquivoInvalido, LimitesZIP
from .test_validacao_zip import criar_zip


class TestResultados(TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.raiz = Path(temp.name) / "privado"
        override = override_settings(RESULTS_ROOT=self.raiz)
        override.enable()
        self.addCleanup(override.disable)
        self.limites = LimitesZIP(10485760, 100, 52428800, 10485760)

    def gerar(self, data=None):
        if data is None:
            data = (settings.BASE_DIR / "materials/arquivos/exemplo.zip").read_bytes()
        response = self.client.post(reverse("laboratorios:organizar_arquivos"), {
            "arquivo_zip": SimpleUploadedFile("exemplo.zip", data),
        })
        self.assertEqual(response.status_code, 303)
        token = response["Location"].strip("/").split("/")[-1]
        return ResultadoTemporario.objects.get(token=token), response["Location"]

    def urls(self, registro):
        return [reverse(route, kwargs={"token": registro.token}) for route in (
            "laboratorios:resultado", "laboratorios:download_resultado",
        )]

    def test_upload_redirect_summary_download_and_inventory(self):
        before = timezone.now()
        registro, url = self.gerar()
        self.assertGreaterEqual(registro.expires_at, before + timedelta(minutes=30))
        self.assertLessEqual(registro.expires_at, timezone.now() + timedelta(minutes=30))
        self.assertEqual(registro.total_arquivos, 6)
        self.assertEqual(registro.por_categoria, {"Documentos": 3, "Planilhas": 1, "Imagens": 1, "Outros": 1})
        resumo = self.client.get(url)
        self.assertContains(resumo, "6 arquivos")
        self.assertContains(resumo, "comunicado_2.txt")
        self.assertContains(resumo, "Quem tiver este link")
        self.assertContains(resumo, 'id="arquivos-resultado-tab"')
        download = self.client.get(self.urls(registro)[1])
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download["Content-Type"], "application/zip")
        self.assertIn('attachment;', download["Content-Disposition"])
        self.assertIn("autolab-arquivos-organizados.zip", download["Content-Disposition"])
        self.assertIn("no-store", download["Cache-Control"])
        self.assertIn("no-store", resumo["Cache-Control"])
        self.assertEqual(resumo["Referrer-Policy"], "no-referrer")
        self.assertEqual(download["Referrer-Policy"], "no-referrer")
        data = b"".join(download.streaming_content)
        download.close()
        with ZipFile(BytesIO(data)) as archive:
            self.assertIsNone(archive.testzip())
            rows = list(csv.DictReader(StringIO(archive.read("relatorio.csv").decode())))
            self.assertEqual(len(rows), 6)
            self.assertNotEqual(archive.read("Documentos/comunicado.txt"), archive.read("Documentos/comunicado_2.txt"))
        self.assertEqual([p.name for p in caminho_resultado(registro).parent.iterdir()], ["arquivos_organizados.zip"])

    def test_refresh_summary_does_not_repeat_processing(self):
        registro, url = self.gerar()
        original = caminho_resultado(registro).read_bytes()
        with patch("laboratorios.views.criar_resultado") as criar:
            for _ in range(2):
                self.assertEqual(self.client.get(url).status_code, 200)
            criar.assert_not_called()
        self.assertEqual(ResultadoTemporario.objects.count(), 1)
        self.assertEqual(caminho_resultado(registro).read_bytes(), original)

    @override_settings(RESULT_TTL_MINUTES=7)
    def test_configurable_expiration_and_exact_boundary(self):
        now = timezone.now()
        with patch("laboratorios.services.resultados.timezone.now", return_value=now):
            registro, _ = self.gerar()
        self.assertEqual(registro.expires_at, now + timedelta(minutes=7))
        with patch("laboratorios.views.timezone.now", return_value=registro.expires_at):
            for url in self.urls(registro):
                response = self.client.get(url)
                self.assertContains(response, "Resultado expirado", status_code=410)
                self.assertNotContains(response, "Baixar ZIP organizado", status_code=410)
                self.assertIn("no-store", response["Cache-Control"])
        self.assertTrue(caminho_resultado(registro).exists())

    def test_unknown_and_malformed_tokens_do_not_expose_content(self):
        for token in (str(uuid4()), "invalido", ".."):
            for suffix in ("", "download/"):
                response = self.client.get(f"/resultados/{token}/{suffix}")
                self.assertEqual(response.status_code, 404)

    def test_deleted_file_returns_safe_404(self):
        registro, _ = self.gerar()
        caminho_resultado(registro).unlink()
        for url in self.urls(registro):
            response = self.client.get(url)
            self.assertContains(response, "Resultado não encontrado", status_code=404)
            self.assertNotContains(response, str(self.raiz), status_code=404)

    def test_tampered_relative_paths_are_never_served(self):
        registro, _ = self.gerar()
        for path in ("../.env", "/etc/passwd", f"{uuid4()}/arquivos_organizados.zip"):
            registro.relative_path = path
            registro.save(update_fields=["relative_path"])
            for url in self.urls(registro):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_symlink_file_and_directory_are_never_served(self):
        registro, _ = self.gerar()
        caminho = caminho_resultado(registro)
        externo = self.raiz.parent / "segredo.txt"
        externo.write_text("não entregar")
        caminho.unlink()
        caminho.symlink_to(externo)
        self.assertEqual(self.client.get(self.urls(registro)[1]).status_code, 404)
        caminho.unlink()
        caminho.parent.rmdir()
        caminho.parent.symlink_to(self.raiz.parent, target_is_directory=True)
        for url in self.urls(registro):
            self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(externo.read_text(), "não entregar")

    def test_query_parameters_cannot_select_another_file(self):
        registro, _ = self.gerar()
        response = self.client.get(self.urls(registro)[1], {"path": "../.env"})
        data = b"".join(response.streaming_content)
        response.close()
        self.assertEqual(data, caminho_resultado(registro).read_bytes())

    def test_head_is_supported_and_mutations_are_rejected(self):
        registro, _ = self.gerar()
        for url in self.urls(registro):
            head = self.client.head(url)
            self.assertEqual(head.status_code, 200)
            head.close()
            self.assertEqual(self.client.post(url).status_code, 405)
            self.assertEqual(self.client.delete(url).status_code, 405)

    def test_separate_clients_have_separate_tokens_and_areas(self):
        first, _ = self.gerar(criar_zip([("a.txt", b"primeiro")]))
        self.client.cookies.clear()
        second, _ = self.gerar(criar_zip([("a.txt", b"segundo")]))
        self.assertNotEqual(first.token, second.token)
        self.assertNotEqual(caminho_resultado(first).parent, caminho_resultado(second).parent)
        for registro, expected in ((first, b"primeiro"), (second, b"segundo")):
            with ZipFile(caminho_resultado(registro)) as archive:
                self.assertEqual(archive.read("Documentos/a.txt"), expected)

    def test_invalid_upload_does_not_create_metadata_or_files(self):
        response = self.client.post(reverse("laboratorios:organizar_arquivos"), {
            "arquivo_zip": SimpleUploadedFile("mau.zip", criar_zip([("../fora.txt", b"a")])),
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ResultadoTemporario.objects.exists())
        self.assertFalse(self.raiz.exists())

    def test_processing_failure_discards_only_current_run(self):
        anterior, _ = self.gerar()
        with patch("laboratorios.services.resultados.organizar_zip", side_effect=OSError("detalhe privado")):
            response = self.client.post(reverse("laboratorios:organizar_arquivos"), {
                "arquivo_zip": SimpleUploadedFile("a.zip", criar_zip([("a.txt", b"a")])),
            })
        self.assertContains(response, "Tente novamente mais tarde", status_code=503)
        self.assertNotContains(response, "detalhe privado", status_code=503)
        self.assertEqual(list(self.raiz.iterdir()), [caminho_resultado(anterior).parent])
        self.assertEqual(ResultadoTemporario.objects.count(), 1)

    def test_metadata_failure_removes_generated_file(self):
        with patch("laboratorios.services.resultados.ResultadoTemporario.objects.create", side_effect=DatabaseError("falha")):
            with self.assertRaises(DatabaseError):
                criar_resultado(SimpleUploadedFile("a.zip", criar_zip([("a.txt", b"a")])), self.limites)
        self.assertEqual(list(self.raiz.iterdir()), [])

    def test_domain_error_during_processing_is_shown_as_form_error(self):
        with patch("laboratorios.views.criar_resultado", side_effect=ArquivoInvalido("O ZIP ficou inválido.")):
            response = self.client.post(reverse("laboratorios:organizar_arquivos"), {
                "arquivo_zip": SimpleUploadedFile("a.zip", criar_zip([("a.txt", b"a")])),
            })
        self.assertContains(response, "O ZIP ficou inválido.", status_code=400)

    def test_result_names_are_escaped_and_input_directories_not_counted(self):
        registro, url = self.gerar(criar_zip([("pasta/", b""), ("pasta/<script>.txt", b"a"), ("outro/<script>.txt", b"b")]))
        self.assertEqual(registro.total_arquivos, 2)
        # Avisos são dados não confiáveis, mesmo quando vierem do banco.
        registro.avisos = ["<script>alert(1)</script>"]
        registro.save(update_fields=["avisos"])
        response = self.client.get(url)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_other_result_kinds_are_not_served_as_archives(self):
        registro, _ = self.gerar()
        registro.kind = "planilhas"
        registro.save(update_fields=["kind"])
        for url in self.urls(registro):
            self.assertEqual(self.client.get(url).status_code, 404)

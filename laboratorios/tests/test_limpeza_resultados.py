"""Limpeza de expirados, simulação e preservação de áreas não autorizadas."""

from datetime import timedelta
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.utils import timezone

from laboratorios.models import ResultadoTemporario
from laboratorios.services.limpeza import limpar_resultado
from laboratorios.services.resultados import NOME_SAIDA


class TestLimpezaResultados(TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.raiz = self.base / "resultados"
        self.raiz.mkdir()
        override = override_settings(RESULTS_ROOT=self.raiz)
        override.enable()
        self.addCleanup(override.disable)
        self.agora = timezone.now()

    def criar(self, *, expirado=True, kind="arquivos"):
        registro = ResultadoTemporario.objects.create(
            relative_path="", expires_at=self.agora + timedelta(minutes=-1 if expirado else 10),
            total_arquivos=1, kind=kind,
        )
        registro.relative_path = f"{registro.token}/{NOME_SAIDA}"
        registro.save(update_fields=["relative_path"])
        area = self.raiz / str(registro.token)
        area.mkdir()
        (area / NOME_SAIDA).write_bytes(b"saida ficticia")
        return registro, area

    def executar(self, **kwargs):
        stdout, stderr = StringIO(), StringIO()
        call_command("limpar_resultados", stdout=stdout, stderr=stderr, **kwargs)
        self.assertEqual(stderr.getvalue(), "")
        return stdout.getvalue()

    def test_removes_only_expired_results_and_metadata(self):
        expired, expired_area = self.criar()
        active, active_area = self.criar(expirado=False)
        other, other_area = self.criar(kind="planilhas")
        self.assertIn("Removidos: 1", self.executar())
        self.assertFalse(expired_area.exists())
        self.assertFalse(ResultadoTemporario.objects.filter(pk=expired.pk).exists())
        self.assertTrue(ResultadoTemporario.objects.filter(pk=active.pk).exists())
        self.assertTrue(ResultadoTemporario.objects.filter(pk=other.pk).exists())
        self.assertTrue((active_area / NOME_SAIDA).is_file())
        self.assertTrue((other_area / NOME_SAIDA).is_file())
        self.assertTrue(self.raiz.is_dir())

    def test_dry_run_changes_neither_files_nor_database(self):
        registro, area = self.criar()
        before = (area / NOME_SAIDA).read_bytes()
        self.assertIn("Elegíveis: 1. Simulação", self.executar(dry_run=True))
        self.assertEqual((area / NOME_SAIDA).read_bytes(), before)
        self.assertTrue(ResultadoTemporario.objects.filter(pk=registro.pk).exists())

    def test_missing_output_or_directory_still_cleans_metadata(self):
        missing_file, file_area = self.criar()
        missing_area, area = self.criar()
        (file_area / NOME_SAIDA).unlink()
        (area / NOME_SAIDA).unlink()
        area.rmdir()
        self.assertIn("Removidos: 2", self.executar())
        self.assertFalse(file_area.exists())
        self.assertFalse(ResultadoTemporario.objects.filter(pk__in=[missing_file.pk, missing_area.pk]).exists())

    def test_empty_and_repeated_runs_are_idempotent(self):
        self.assertIn("Removidos: 0", self.executar())
        self.criar()
        self.assertIn("Removidos: 1", self.executar())
        self.assertIn("Removidos: 0", self.executar())

    def test_multiple_batches_do_not_skip_deleted_rows(self):
        for _ in range(5):
            self.criar()
        self.assertIn("Removidos: 5", self.executar(batch_size=2))
        self.assertFalse(ResultadoTemporario.objects.exists())
        self.assertEqual(list(self.raiz.iterdir()), [])

    def test_non_positive_batch_is_rejected_without_changes(self):
        registro, area = self.criar()
        for tamanho in (0, -1):
            with self.subTest(tamanho=tamanho), self.assertRaises(CommandError):
                self.executar(batch_size=tamanho)
        self.assertTrue((area / NOME_SAIDA).exists())
        self.assertTrue(ResultadoTemporario.objects.filter(pk=registro.pk).exists())

    def test_canonical_path_is_required_and_other_results_survive(self):
        other, other_area = self.criar(expirado=False)
        for path in ("../segredo.txt", str(self.base / "segredo.txt"), other.relative_path):
            registro, area = self.criar()
            registro.relative_path = path
            registro.save(update_fields=["relative_path"])
            with self.subTest(path=path), self.assertRaises(OSError):
                limpar_resultado(registro.pk, self.agora)
            self.assertTrue((area / NOME_SAIDA).exists())
            self.assertTrue(ResultadoTemporario.objects.filter(pk=registro.pk).exists())
        self.assertTrue((other_area / NOME_SAIDA).exists())

    def test_symbolic_file_and_directory_do_not_delete_targets(self):
        outside = self.base / "privado.txt"
        outside.write_bytes(b"preservar")
        registro, area = self.criar()
        (area / NOME_SAIDA).unlink()
        (area / NOME_SAIDA).symlink_to(outside)
        with self.assertRaises(OSError):
            limpar_resultado(registro.pk, self.agora)
        (area / NOME_SAIDA).unlink()
        area.rmdir()
        area.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(OSError):
            limpar_resultado(registro.pk, self.agora)
        self.assertEqual(outside.read_bytes(), b"preservar")
        self.assertTrue(area.is_symlink())
        self.assertTrue(ResultadoTemporario.objects.filter(pk=registro.pk).exists())

    def test_unexpected_content_is_preserved_without_partial_deletion(self):
        registro, area = self.criar()
        (area / "desconhecido.txt").write_bytes(b"preservar")
        with self.assertRaises(OSError):
            limpar_resultado(registro.pk, self.agora)
        self.assertTrue((area / NOME_SAIDA).exists())
        self.assertTrue((area / "desconhecido.txt").exists())

    def test_unregistered_directories_are_not_swept(self):
        orphan = self.raiz / "upload-em-andamento"
        orphan.mkdir()
        (orphan / "entrada.zip").write_bytes(b"preservar")
        self.assertIn("Removidos: 0", self.executar())
        self.assertEqual((orphan / "entrada.zip").read_bytes(), b"preservar")

    def test_cutoff_is_fixed_and_expiry_is_rechecked_before_deletion(self):
        registro, area = self.criar()
        registro.expires_at = self.agora + timedelta(seconds=1)
        registro.save(update_fields=["expires_at"])
        self.assertFalse(limpar_resultado(registro.pk, self.agora))
        self.assertTrue((area / NOME_SAIDA).exists())
        with patch("laboratorios.management.commands.limpar_resultados.timezone.now", return_value=registro.expires_at):
            self.assertIn("Removidos: 1", self.executar())
        self.assertFalse(area.exists())

    def test_io_failure_preserves_record_and_command_continues(self):
        bad, bad_area = self.criar()
        good, good_area = self.criar()
        original_unlink = Path.unlink
        def falhar(path, *args, **kwargs):
            if path.parent == bad_area:
                raise PermissionError("detalhe privado")
            return original_unlink(path, *args, **kwargs)
        stdout, stderr = StringIO(), StringIO()
        with patch.object(Path, "unlink", falhar), self.assertRaises(CommandError):
            call_command("limpar_resultados", stdout=stdout, stderr=stderr, batch_size=1)
        self.assertIn("Removidos: 1", stdout.getvalue())
        self.assertNotIn("detalhe privado", stderr.getvalue())
        self.assertNotIn(str(self.raiz), stderr.getvalue())
        self.assertTrue(ResultadoTemporario.objects.filter(pk=bad.pk).exists())
        self.assertFalse(ResultadoTemporario.objects.filter(pk=good.pk).exists())
        self.assertTrue((bad_area / NOME_SAIDA).exists())
        self.assertFalse(good_area.exists())
        self.assertIn("Removidos: 1", self.executar())

    def test_database_failure_after_file_removal_can_be_retried(self):
        registro, area = self.criar()
        with patch.object(ResultadoTemporario, "delete", side_effect=DatabaseError("falha")):
            with self.assertRaises(DatabaseError):
                limpar_resultado(registro.pk, self.agora)
        self.assertTrue(ResultadoTemporario.objects.filter(pk=registro.pk).exists())
        self.assertFalse(area.exists())
        self.assertIn("Removidos: 1", self.executar())
        self.assertFalse(ResultadoTemporario.objects.filter(pk=registro.pk).exists())

    def test_suspicious_area_is_also_rejected_in_dry_run(self):
        registro, area = self.criar()
        (area / "subpasta").mkdir()
        with self.assertRaises(OSError):
            limpar_resultado(registro.pk, self.agora, simular=True)
        self.assertTrue((area / NOME_SAIDA).exists())

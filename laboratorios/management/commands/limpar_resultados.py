"""Remove resultados expirados sem varrer arquivos de outras execuções."""

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from django.utils import timezone

from laboratorios.models import ResultadoTemporario
from laboratorios.services.limpeza import limpar_resultado


class Command(BaseCommand):
    help = "Remove resultados de Arquivos expirados e seus metadados."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Simula sem alterar arquivos ou banco.")
        parser.add_argument("--batch-size", type=int, default=100, help="Registros por lote (default: 100).")

    def handle(self, *args, **options):
        tamanho = options["batch_size"]
        if tamanho <= 0:
            raise CommandError("--batch-size deve ser positivo.")
        corte, cursor = timezone.now(), None
        total, falhas = 0, 0
        while True:
            candidatos = ResultadoTemporario.objects.filter(expires_at__lte=corte, kind="arquivos")
            if cursor is not None:
                candidatos = candidatos.filter(token__gt=cursor)
            tokens = list(candidatos.order_by("token").values_list("token", flat=True)[:tamanho])
            if not tokens:
                break
            for token in tokens:
                try:
                    total += limpar_resultado(token, corte, simular=options["dry_run"])
                except (OSError, DatabaseError):
                    falhas += 1
                    self.stderr.write("Falha ao limpar uma execução; metadados preservados para nova tentativa.")
            cursor = tokens[-1]
        if options["dry_run"]:
            self.stdout.write(f"Elegíveis: {total}. Simulação: nenhum arquivo ou registro alterado.")
        else:
            self.stdout.write(f"Removidos: {total}.")
        if falhas:
            raise CommandError(f"Falhas na limpeza: {falhas}. Verifique as áreas privadas e execute novamente.")

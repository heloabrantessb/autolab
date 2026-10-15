"""Metadados mínimos dos resultados temporários, sem guardar o upload."""

import uuid

from django.db import models


class ResultadoTemporario(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    relative_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    kind = models.CharField(max_length=20, default="arquivos")
    total_arquivos = models.PositiveIntegerField()
    por_categoria = models.JSONField(default=dict)
    avisos = models.JSONField(default=list)

"""Formulários de entrada e validações dos laboratórios."""

from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator

from .services.zip_validator import ArquivoInvalido, LimiteExcedido, LimitesZIP, inspecionar_zip


class UploadZIPForm(forms.Form):
    arquivo_zip = forms.FileField(
        label="Arquivo ZIP",
        validators=[FileExtensionValidator(
            allowed_extensions=["zip"],
            message="Envie um arquivo com extensão .zip.",
        )],
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control", "accept": ".zip,application/zip",
        }),
        error_messages={
            "required": "Selecione um arquivo ZIP.",
            "empty": "O arquivo enviado está vazio.",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limite_bytes = settings.MAX_ZIP_UPLOAD_BYTES
        self.limites_zip = LimitesZIP(
            upload_bytes=self.limite_bytes,
            entradas=settings.MAX_ZIP_ENTRIES,
            descompactado_bytes=settings.MAX_ZIP_UNCOMPRESSED_BYTES,
            entrada_bytes=settings.MAX_ZIP_ENTRY_BYTES,
        )
        self.fields["arquivo_zip"].help_text = (
            f"Envie um único ZIP de até {self.limite_bytes / (1024 * 1024):g} MiB. "
            f"Máximo de {self.limites_zip.entradas} entradas, "
            f"{self.limites_zip.descompactado_bytes / (1024 * 1024):g} MiB descompactados "
            f"e {self.limites_zip.entrada_bytes / (1024 * 1024):g} MiB por arquivo. "
            "Use um ZIP Stored ou Deflate, sem senha e sem metadados de sistema."
        )

    def clean_arquivo_zip(self):
        arquivo = self.cleaned_data["arquivo_zip"]
        erro_limite = forms.ValidationError(
            "O arquivo excede o tamanho máximo permitido.", code="limite_excedido",
        )
        if arquivo.size > self.limite_bytes:
            raise erro_limite

        # Confere também os bytes lidos, sem extrair ou interpretar o conteúdo.
        total = 0
        try:
            for parte in arquivo.chunks(chunk_size=64 * 1024):
                total += len(parte)
                if total > self.limite_bytes:
                    raise erro_limite
        finally:
            arquivo.seek(0)
        if total == 0:
            raise forms.ValidationError("O arquivo enviado está vazio.", code="empty")
        try:
            self.inspecao = inspecionar_zip(arquivo, self.limites_zip)
        except ArquivoInvalido as exc:
            codigo = "limite_excedido" if isinstance(exc, LimiteExcedido) else "zip_invalido"
            raise forms.ValidationError(str(exc), code=codigo) from exc
        return arquivo

    def clean(self):
        dados = super().clean()
        if hasattr(self.files, "getlist") and sum(
            len(self.files.getlist(nome)) for nome in self.files
        ) > 1:
            raise forms.ValidationError("Envie apenas um arquivo ZIP por vez.")
        return dados


class UploadPlanilhaForm(forms.Form):
    arquivo_planilha = forms.FileField(
        label="Planilha CSV ou XLSX",
        validators=[FileExtensionValidator(
            allowed_extensions=["csv", "xlsx"],
            message="Envie um arquivo com extensão .csv ou .xlsx.",
        )],
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control", "accept": ".csv,.xlsx",
        }),
        error_messages={
            "required": "Selecione um arquivo CSV ou XLSX.",
            "empty": "O arquivo enviado está vazio.",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limite_bytes = settings.MAX_SPREADSHEET_UPLOAD_BYTES
        self.fields["arquivo_planilha"].help_text = (
            f"Envie um único CSV ou XLSX de até {self.limite_bytes / (1024 * 1024):g} MiB. "
            "Nesta etapa conferimos somente extensão e tamanho. "
            "O conteúdo ainda não será lido, limpo ou exportado."
        )

    def clean_arquivo_planilha(self):
        arquivo = self.cleaned_data["arquivo_planilha"]
        erro_limite = forms.ValidationError(
            "O arquivo excede o tamanho máximo permitido.", code="limite_excedido",
        )
        if arquivo.size > self.limite_bytes:
            raise erro_limite
        total = 0
        try:
            for parte in arquivo.chunks(chunk_size=64 * 1024):
                total += len(parte)
                if total > self.limite_bytes:
                    raise erro_limite
        finally:
            arquivo.seek(0)
        if not total:
            raise forms.ValidationError("O arquivo enviado está vazio.", code="empty")
        return arquivo

    def clean(self):
        dados = super().clean()
        if hasattr(self.files, "getlist") and sum(
            len(self.files.getlist(nome)) for nome in self.files
        ) > 1:
            raise forms.ValidationError("Envie apenas uma planilha por vez.")
        return dados

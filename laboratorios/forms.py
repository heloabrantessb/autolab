"""Formulários de entrada; inspeção de ZIP pertence à próxima entrega."""

from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator


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
        self.fields["arquivo_zip"].help_text = (
            f"Envie um único ZIP de até {self.limite_bytes / (1024 * 1024):g} MiB. "
            "Use o exemplo fictício para experimentar o envio."
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
        return arquivo

    def clean(self):
        dados = super().clean()
        if hasattr(self.files, "getlist") and sum(
            len(self.files.getlist(nome)) for nome in self.files
        ) > 1:
            raise forms.ValidationError("Envie apenas um arquivo ZIP por vez.")
        return dados

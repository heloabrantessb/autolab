"""Recebimento inicial de ZIP e proteção do endpoint de upload."""

from pathlib import Path
from tempfile import TemporaryDirectory
from io import BytesIO
from zipfile import ZipFile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, override_settings
from django.urls import reverse

from laboratorios.forms import UploadZIPForm


class TestUploadZIP(SimpleTestCase):
    def setUp(self):
        self.url = reverse("laboratorios:organizar_arquivos")

    def zip_bytes(self):
        buffer = BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr("notas.txt", "Exemplo")
        return buffer.getvalue()

    def upload(self, name="exemplo.zip", content=None, **kwargs):
        if content is None:
            content = self.zip_bytes()
        return self.client.post(self.url, {
            "arquivo_zip": SimpleUploadedFile(name, content, **kwargs),
        })

    def test_get_shows_form_with_csrf_and_limit(self):
        response = self.client.get(reverse("laboratorios:arquivos"))
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="arquivo_zip"')
        self.assertContains(response, "10 MiB")

    def test_success_confirms_inspection_without_organization(self):
        response = self.upload()
        self.assertContains(response, "ZIP validado:")
        self.assertContains(response, "Estrutura, caminhos, integridade e limites")
        self.assertContains(response, "nenhum resultado foi gerado")
        self.assertContains(response, 'class="tab-pane autolab-lab-panel active" id="arquivos-executar"')

    def test_uppercase_extension_and_untrusted_mime(self):
        response = self.upload("exemplo.ZIP", content_type="text/plain")
        self.assertEqual(response.status_code, 200)

    def test_missing_empty_and_wrong_extension(self):
        responses = (
            (self.client.post(self.url), "Selecione um arquivo ZIP."),
            (self.upload(content=b""), "O arquivo enviado está vazio."),
            (self.upload("texto.txt"), "Envie um arquivo com extensão .zip."),
        )
        for response, message in responses:
            with self.subTest(message=message):
                self.assertContains(response, message, status_code=400)
                self.assertContains(response, 'class="tab-pane autolab-lab-panel active" id="arquivos-executar"', status_code=400)

    def test_limit_accepts_exact_size_and_rejects_larger(self):
        data = self.zip_bytes()
        with override_settings(MAX_ZIP_UPLOAD_BYTES=len(data)):
            self.assertEqual(self.upload(content=data).status_code, 200)
            response = self.upload(content=data + b"x")
        self.assertContains(response, "tamanho máximo", status_code=400)

    @override_settings(MAX_ZIP_UPLOAD_BYTES=4)
    def test_actual_bytes_are_checked_despite_small_declared_size(self):
        arquivo = SimpleUploadedFile("exemplo.zip", b"12345")
        arquivo.size = 1
        form = UploadZIPForm(files={"arquivo_zip": arquivo})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()["arquivo_zip"][0].code, "limite_excedido")
        self.assertEqual(arquivo.tell(), 0)

    def test_multiple_files_rejected(self):
        response = self.client.post(self.url, {"arquivo_zip": [
            SimpleUploadedFile("a.zip", b"a"), SimpleUploadedFile("b.zip", b"b"),
        ]})
        self.assertContains(response, "Envie apenas um arquivo ZIP por vez.", status_code=400)

    def test_extra_file_under_another_field_is_rejected(self):
        response = self.client.post(self.url, {
            "arquivo_zip": SimpleUploadedFile("a.zip", b"a"),
            "outro": SimpleUploadedFile("b.zip", b"b"),
        })
        self.assertContains(response, "Envie apenas um arquivo ZIP por vez.", status_code=400)

    def test_only_post_is_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_csrf_blocks_post_without_token_and_allows_valid_token(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, {"arquivo_zip": SimpleUploadedFile("exemplo.zip", b"a")})
        self.assertEqual(response.status_code, 403)
        client.get(reverse("laboratorios:arquivos"))
        token = client.cookies["csrftoken"].value
        response = client.post(self.url, {
            "csrfmiddlewaretoken": token,
            "arquivo_zip": SimpleUploadedFile("exemplo.zip", self.zip_bytes()),
        })
        self.assertEqual(response.status_code, 200)

    def test_upload_does_not_persist_results(self):
        with TemporaryDirectory() as directory, override_settings(RESULTS_ROOT=Path(directory)):
            self.assertEqual(self.upload().status_code, 200)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_filename_is_escaped(self):
        response = self.upload("<script>.zip")
        self.assertContains(response, "&lt;script&gt;.zip")
        self.assertNotContains(response, "<script>.zip")

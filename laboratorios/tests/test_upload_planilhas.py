"""Recebimento inicial, sem interpretação ou armazenamento de planilhas."""

from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, override_settings
from django.urls import reverse

from laboratorios.forms import UploadPlanilhaForm


class TestUploadPlanilha(SimpleTestCase):
    def setUp(self):
        self.url = reverse("laboratorios:receber_planilha")

    def upload(self, nome="clientes.csv", conteudo=b"id,nome\n001,Ana\n", **kwargs):
        return self.client.post(self.url, {
            "arquivo_planilha": SimpleUploadedFile(nome, conteudo, **kwargs),
        })

    def test_form_has_csrf_limit_and_single_file_input(self):
        response = self.client.get(reverse("laboratorios:planilhas"))
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="arquivo_planilha"')
        self.assertContains(response, 'accept=".csv,.xlsx"')
        self.assertContains(response, "20 MiB")
        self.assertNotContains(response, "multiple")

    def test_csv_receipt_is_explicitly_initial_and_does_not_echo_data(self):
        response = self.upload(conteudo=b"campo\nconteudo-privado\n")
        self.assertContains(response, "Arquivo recebido para conferência inicial")
        self.assertContains(response, "O conteúdo não foi interpretado")
        self.assertContains(response, "o envio não foi salvo como resultado")
        self.assertNotContains(response, "conteudo-privado")
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, 'class="tab-pane autolab-lab-panel active" id="planilhas-executar"')
        self.assertIn("no-store", response["Cache-Control"])

    def test_uppercase_csv_and_xlsx_ignore_untrusted_mime(self):
        for nome in ("clientes.CSV", "clientes.XLSX"):
            with self.subTest(nome=nome):
                # Conteúdo propositalmente arbitrário: esta etapa não valida formato.
                response = self.upload(nome, b"recebimento apenas", content_type="application/octet-stream")
                self.assertContains(response, "O conteúdo não foi interpretado")

    def test_required_empty_and_unsupported_extensions(self):
        responses = [
            (self.client.post(self.url), "Selecione um arquivo CSV ou XLSX."),
            (self.upload(conteudo=b""), "O arquivo enviado está vazio."),
        ]
        for extensao in ("xls", "xlsm", "zip", "txt", "csv.exe"):
            responses.append((self.upload(f"clientes.{extensao}"), "Envie um arquivo com extensão .csv ou .xlsx."))
        for response, message in responses:
            with self.subTest(message=message):
                self.assertContains(response, message, status_code=400)
                self.assertContains(response, "selecione o arquivo novamente", status_code=400)
                self.assertContains(response, 'class="tab-pane autolab-lab-panel active" id="planilhas-executar"', status_code=400)

    @override_settings(MAX_SPREADSHEET_UPLOAD_BYTES=4)
    def test_exact_size_accepted_and_larger_rejected(self):
        self.assertEqual(self.upload(conteudo=b"1234").status_code, 200)
        response = self.upload(conteudo=b"12345")
        self.assertContains(response, "tamanho máximo", status_code=400)

    @override_settings(MAX_SPREADSHEET_UPLOAD_BYTES=4)
    def test_actual_bytes_checked_even_with_false_declared_size(self):
        arquivo = SimpleUploadedFile("dados.csv", b"12345")
        arquivo.size = 1
        form = UploadPlanilhaForm(files={"arquivo_planilha": arquivo})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()["arquivo_planilha"][0].code, "limite_excedido")
        self.assertEqual(arquivo.tell(), 0)

    def test_zero_actual_bytes_rejected_and_pointer_reset_on_success(self):
        arquivo = SimpleUploadedFile("dados.csv", b"")
        arquivo.size = 1
        form = UploadPlanilhaForm(files={"arquivo_planilha": arquivo})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()["arquivo_planilha"][0].code, "empty")
        arquivo = SimpleUploadedFile("dados.csv", b"id\n001\n")
        form = UploadPlanilhaForm(files={"arquivo_planilha": arquivo})
        self.assertTrue(form.is_valid())
        self.assertEqual(arquivo.tell(), 0)

    def test_multiple_files_in_same_or_extra_field_rejected(self):
        for extra in ("arquivo_planilha", "outro"):
            dados = {"arquivo_planilha": SimpleUploadedFile("a.csv", b"a")}
            if extra == "arquivo_planilha":
                dados[extra] = [dados[extra], SimpleUploadedFile("b.csv", b"b")]
            else:
                dados[extra] = SimpleUploadedFile("b.csv", b"b")
            with self.subTest(extra=extra):
                self.assertContains(self.client.post(self.url, dados), "Envie apenas uma planilha por vez.", status_code=400)

    def test_only_post_is_allowed(self):
        for metodo in ("get", "head", "put", "delete"):
            with self.subTest(metodo=metodo):
                self.assertEqual(getattr(self.client, metodo)(self.url).status_code, 405)

    def test_csrf_required_and_valid_token_accepted(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(self.url).status_code, 403)
        client.get(reverse("laboratorios:planilhas"))
        response = client.post(self.url, {
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
            "arquivo_planilha": SimpleUploadedFile("a.csv", b"id\n001\n"),
        })
        self.assertContains(response, "Arquivo recebido para conferência inicial")

    def test_upload_does_not_persist_or_use_client_filename_as_path(self):
        with TemporaryDirectory() as area, override_settings(RESULTS_ROOT=Path(area)):
            response = self.upload("<script>.csv")
            self.assertContains(response, "Arquivo recebido para conferência inicial")
            self.assertNotContains(response, "<script>")
            self.assertEqual(list(Path(area).iterdir()), [])
        # SimpleTestCase também impede acesso acidental ao banco de resultados.

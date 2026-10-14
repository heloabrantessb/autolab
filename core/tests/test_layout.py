"""Testes de integridade, acessibilidade e renderizacao do layout base."""

from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase
from django.contrib.messages.storage.base import Message


class TestBaseLayout(SimpleTestCase):
    """Testa renderizacao do template base.html e componentes parciais."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_base_template_renders_skip_link(self):
        """Verifica presenca do link de acessibilidade (skip link)."""
        request = self.factory.get("/")
        template = Template(
            "{% extends 'base.html' %}"
            "{% block content %}<p>Conteudo de Teste</p>{% endblock %}"
        )
        rendered = template.render(Context({"request": request}))

        self.assertIn('href="#main-content"', rendered)
        self.assertIn("class=\"skip-link\"", rendered)
        self.assertIn("Pular para o conteúdo principal", rendered)

    def test_base_template_includes_semantic_elements(self):
        """Verifica presenca de tags semanticas estruturais e atributos de acessibilidade."""
        request = self.factory.get("/")
        template = Template(
            "{% extends 'base.html' %}"
            "{% block content %}<h1>Pagina Teste</h1>{% endblock %}"
        )
        rendered = template.render(Context({"request": request}))

        self.assertIn("<header class=\"autolab-navbar", rendered)
        self.assertIn("<nav class=\"autolab-sidebar", rendered)
        self.assertIn("<main id=\"main-content\"", rendered)
        self.assertIn("<footer class=\"autolab-footer\"", rendered)
        self.assertIn("aria-label=\"Navegação Principal\"", rendered)
        self.assertIn("aria-controls=\"mobileSidebar\"", rendered)

    def test_base_template_static_assets_linked(self):
        """Verifica se arquivos estaticos essenciais estao referenciados no HTML."""
        request = self.factory.get("/")
        template = Template(
            "{% extends 'base.html' %}"
            "{% block content %}<p>Assets</p>{% endblock %}"
        )
        rendered = template.render(Context({"request": request}))

        self.assertIn("static/vendor/bootstrap/css/bootstrap.min.css", rendered)
        self.assertIn("static/css/autolab.css", rendered)
        self.assertIn("static/vendor/bootstrap/js/bootstrap.bundle.min.js", rendered)
        self.assertIn("static/js/autolab.js", rendered)

    def test_base_template_blocks_extensible(self):
        """Verifica se blocos title, extra_head, content e extra_js sao sobrescritos corretamente."""
        request = self.factory.get("/")
        template = Template(
            "{% extends 'base.html' %}"
            "{% block title %}Titulo Customizado | AutoLab{% endblock %}"
            "{% block extra_head %}<meta name=\"custom-meta\" content=\"teste\">{% endblock %}"
            "{% block content %}<div id=\"custom-content\">Meu Conteudo</div>{% endblock %}"
            "{% block extra_js %}<script>console.log('custom-js');</script>{% endblock %}"
        )
        rendered = template.render(Context({"request": request}))

        self.assertIn("<title>Titulo Customizado | AutoLab</title>", rendered)
        self.assertIn('<meta name="custom-meta" content="teste">', rendered)
        self.assertIn('<div id="custom-content">Meu Conteudo</div>', rendered)
        self.assertIn("<script>console.log('custom-js');</script>", rendered)

    def test_alerts_rendering_with_messages(self):
        """Verifica renderizacao de mensagens nos formatos esperados de alerta."""
        request = self.factory.get("/")
        messages = [
            Message(level=20, message="Operação concluída com sucesso!", extra_tags="success"),
            Message(level=40, message="Erro crítico no processamento.", extra_tags="error"),
            Message(level=30, message="Aviso de atenção.", extra_tags="warning"),
        ]
        template = Template(
            "{% extends 'base.html' %}"
            "{% block content %}<p>Com mensagens</p>{% endblock %}"
        )
        rendered = template.render(Context({"request": request, "messages": messages}))

        self.assertIn('role="alert"', rendered)
        self.assertIn("alert-success", rendered)
        self.assertIn("alert-danger", rendered)
        self.assertIn("alert-warning", rendered)
        self.assertIn("Operação concluída com sucesso!", rendered)
        self.assertIn("Erro crítico no processamento.", rendered)
        self.assertIn("Aviso de atenção.", rendered)

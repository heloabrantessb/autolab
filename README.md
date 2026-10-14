# AutoLab

Plataforma web educacional desenvolvida para a oficina de **Automação de Processos com IA e Python**.

O AutoLab permite que os participantes aprendam conceitos de automação, executem fluxos diretamente no navegador com dados fictícios, inspecionem e alterem códigos Python no GitHub Codespaces e resolvam desafios práticos sem necessidade de configurar dependências em suas máquinas locais.

---

## 🛠️ Stack Tecnológica

- **Backend:** Python 3.12+ e Django 5.2 LTS (Arquitetura Monolítica MVT)
- **Frontend:** Django Templates, Bootstrap 5.3 e CSS customizado acessível
- **Banco de Dados:** SQLite (desenvolvimento e testes) / PostgreSQL (produção)
- **Ambiente de Exercícios:** GitHub Codespaces (com `.devcontainer`)
- **Testes:** Pytest e Django TestCase

As versões exatas estão fixadas em `requirements.txt`; Django 5.2.18 foi
validado com Python 3.12.3. Para regenerar o arquivo ao atualizar Django:

```bash
uv pip compile requirements.in -o requirements.txt --upgrade-package django
```

Após atualizar as dependências, execute as verificações e os testes abaixo.

---

## 📁 Estrutura do Projeto

```text
autolab/
├── config/              # Configuracao central do Django (settings, urls, wsgi, asgi)
├── core/                # Modulo central: Home, catalogo geral e paginas base
├── laboratorios/        # Modulo dos laboratorios de automacao e servicos de dominio
│   └── services/        # Operacoes Python desacopladas da camada web
├── exercicios/          # Modulo de enunciados, desafios e integracao Codespaces
├── templates/           # Templates Django globais e parciais
├── static/              # Arquivos estaticos (CSS, JS, imagens)
├── docs/                # Documentacao de planejamento e padroes de branch/commit
├── manage.py            # Utilitario de linha de comando do Django
├── requirements.in      # Dependencias diretas de alto nivel
├── requirements.txt     # Dependencias compiladas com versoes fixadas
└── pytest.ini           # Configuracao da suite de testes pytest
```

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos

- Python 3.12 ou superior instalado
- Git
- `uv` (recomendado) ou `pip`

### 2. Configurar o Ambiente Virtual

Usando `uv`:

```bash
uv venv .venv
source .venv/bin/activate
```

Ou usando `venv` padrão:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
# ou com uv:
uv pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

### 5. Executar Verificações e Testes

```bash
python manage.py check
python manage.py test
# ou:
pytest
```

### 6. Iniciar o Servidor de Desenvolvimento

```bash
python manage.py migrate
python manage.py runserver
```

Acesse [http://127.0.0.1:8000/](http://127.0.0.1:8000/) no seu navegador.

---

## 📐 Padrões de Contribuição

O projeto adota regras estritas de desenvolvimento em branches pequenas e commits atômicos padronizados:

- **Branches permanentes:** `main` (estável/produção) e `dev` (integração).
- **Branches de funcionalidade:** `feat/<funcionalidade>` criadas a partir de `dev`.
- **Commits:** Conventional Commits no padrão `<tipo>(<escopo>): <descrição no imperativo>`.

Consulte os guias em:
- [`docs/PADRAO_BRANCHES_COMMITS.md`](docs/PADRAO_BRANCHES_COMMITS.md)
- [`docs/PLANEJAMENTO_AUTOLAB.md`](docs/PLANEJAMENTO_AUTOLAB.md)

# AutoLab

Plataforma web educacional desenvolvida para a oficina de **Automação de Processos com IA e Python**.

O AutoLab permite aprender conceitos de automação, executar o fluxo de Arquivos no navegador com dados fictícios e praticar Python localmente com um pacote de exercício baixável. Planilhas está na etapa de conteúdo didático; seu processamento ainda será implementado.

---

## 🛠️ Stack Tecnológica

- **Backend:** Python 3.12+ e Django 5.2 LTS (Arquitetura Monolítica MVT)
- **Frontend:** Django Templates, Bootstrap 5.3 e CSS customizado acessível
- **Banco de Dados:** SQLite (desenvolvimento e testes) / PostgreSQL (produção)
- **Ambiente de Exercícios:** Python local; GitHub Codespaces opcional, pausado antes da validação hospedada
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

### Resultados temporários de Arquivos

Após aplicar as migrações, a página `/laboratorios/arquivos/` recebe o ZIP,
organiza os arquivos e redireciona para um resumo com download. O material
fictício está em `materials/arquivos/exemplo.zip`.

`RESULTS_ROOT` deve ficar fora de diretórios públicos de static/media. Cada
resultado usa uma área privada por UUID e um link que permite acesso a quem
o possuir, sem login. `RESULT_TTL_MINUTES` deve ser positivo (default: 30).
O upload original é descartado após processamento; o ZIP organizado e os
metadados permanecem até a limpeza. Expirar bloqueia novos acessos, sem
interromper downloads já iniciados.

O laboratório de Arquivos está disponível no catálogo. Para simular e executar
a limpeza de resultados expirados:

```bash
python manage.py limpar_resultados --dry-run
python manage.py limpar_resultados --batch-size 100
```

A execução periódica exige um agendador externo; o processo web não inicia
essa rotina. Antes da oficina/publicação, configure uma execução a cada cinco
minutos, sem sobreposição, usando o mesmo banco e `RESULTS_ROOT` da aplicação.
Consulte a [operação dos resultados](docs/OPERACAO_RESULTADOS.md) para retenção,
exemplo de agendamento e tratamento de falhas. Nenhum agendador foi instalado
ou ativado automaticamente.

---

## Exercício Python de Arquivos

O [exercício de Arquivos](codespaces_exercises/arquivos/README.md) pode ser
executado com Python 3.12+, sem dependências do site. Acesse `/exercicios/`
para baixar o pacote do participante ou, no clone do repositório:

```bash
cd codespaces_exercises/arquivos
python tests/verificar.py
python starter.py --saida resultado.zip
```

Os testes do exercício falham inicialmente até resolver os três TODOs.
Eles verificam o código local; o site não executa soluções dos participantes.
O ambiente Codespaces está no [PR #13](https://github.com/heloabrantessb/autolab/pull/13),
em rascunho e sem integração. Contêiner local e CI foram validados; nenhum
Codespace foi criado. A validação hospedada está pausada por decisão de evitar
cobranças. Use o pacote com Python local; não é necessária conta GitHub.

Para o instrutor, `python tests/verificar.py --referencia` verifica a solução
de referência no repositório completo. Ela não é incluída no pacote baixado.
O CI do site verifica tanto as falhas esperadas do starter quanto a aprovação
da referência e o funcionamento do pacote completado, sem dependências externas.

## Conteúdo didático de Planilhas

Acesse `/laboratorios/planilhas/` pelo menu **Planilhas: aprender** para as seis
etapas e o download do [CSV fictício](materials/planilhas/README.md). O exemplo
contém duplicatas, espaços e uma linha vazia; a referência preserva registros
parcialmente preenchidos e identificadores com zeros iniciais.

Upload, leitura CSV/XLSX, limpeza e exportação ainda serão entregues em branches
próprias. A tabela de referência não representa uma execução no site, e a
automação continua indisponível no catálogo.

## 📐 Padrões de Contribuição

O workflow [Testes Django](.github/workflows/tests.yml) executa em pushes para
`feat/*`, `dev` e `main`, e em PRs destinados a `dev` ou `main`. Usa Python 3.12,
dependências fixadas, verificações do Django, migrações pendentes e as suítes
Django e pytest. A IA permanece desativada e não são necessários segredos.
Qualquer etapa que falhar faz o check `Django / Python 3.12` falhar.

Para reproduzir as verificações após instalar as dependências:

```bash
python -m pip check
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python -m pytest -p no:cacheprovider
```

O [modelo de PR](.github/pull_request_template.md) segue a seção 13 da política
de versionamento. Remova placeholders como `Closes #XX` quando não houver issue.
Depois da primeira execução remota bem-sucedida, o check pode ser exigido na
proteção de branches; o workflow não configura essa proteção automaticamente.

O projeto adota regras estritas de desenvolvimento em branches pequenas e commits atômicos padronizados:

- **Branches permanentes:** `main` (estável/produção) e `dev` (integração).
- **Branches de funcionalidade:** `feat/<funcionalidade>` criadas a partir de `dev`.
- **Commits:** Conventional Commits no padrão `<tipo>(<escopo>): <descrição no imperativo>`.

Consulte os guias em:
- [`docs/PADRAO_BRANCHES_COMMITS.md`](docs/PADRAO_BRANCHES_COMMITS.md)
- [`docs/PLANEJAMENTO_AUTOLAB.md`](docs/PLANEJAMENTO_AUTOLAB.md)

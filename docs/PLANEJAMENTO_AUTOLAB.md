# AutoLab — Planejamento e Especificação Técnica

**Versão:** 2.0 — especificação de implementação para agentes de IA  
**Data:** 15/10/2026
**Status:** implementação incremental em andamento: base Django, layout, CI, catálogo, página didática, recebimento, inspeção e serviço de organização ZIP integrados em `dev`. Resumo web, download por token e bloqueio por expiração implementados na `feat/download-resultado`, aguardando envio e revisão. Limpeza, exercícios e Codespaces ainda pendentes. Este documento é a fonte de verdade para implementação.

## 1. Objetivo

Construir uma plataforma web educacional para oficina de **Automação de Processos com IA e Python**. Participantes devem aprender conceitos, executar automações prontas, inspecionar/modificar código Python em ambiente pré-configurado e resolver desafios sem instalar dependências localmente.

A plataforma deverá continuar útil para oficinas futuras, com laboratórios e exercícios extensíveis.

## 2. Decisões consolidadas

- Nome provisório: **AutoLab**.
- Framework principal: **Django** (substitui a proposta anterior React + FastAPI).
- Frontend inicial: **Django Templates, HTML, CSS, JavaScript e Bootstrap 5**. Evitar SPA separada no MVP.
- Banco inicial: **SQLite**; considerar PostgreSQL na produção, conforme carga e necessidade.
- Automação: funções/serviços Python internos, invocados por views Django com validação.
- IA: integração com provedor de LLM via backend; chave nunca exposta no navegador; limites de uso e operações permitidas.
- Ambiente de programação: **GitHub Codespaces**, com `.devcontainer/devcontainer.json`, arquivos de exercícios e dependências instaladas. `github.dev` serve para edição, mas não execução Python.
- Desenvolvimento: Git/GitHub; distribuição/hospedagem futura com Docker, HTTPS e servidor web.
- Sem login obrigatório no MVP. Histórico persistente e autenticação ficam para fase posterior.
- Cada laboratório usa padrão: **Aprender → Demonstração/Executar → Código Python → Exercício → Desafio → Resultado**.
- Duas experiências complementares: automação pronta no site e exercício de programação no Codespaces.
- Dados dos exercícios devem ser fictícios; arquivos enviados temporários e removidos segundo política de retenção.
- Não executar código arbitrário de participantes no processo Django; execução livre apenas em ambiente isolado, como Codespaces.

## 3. Público e oficina

Público-alvo: participantes iniciantes ou com conhecimentos básicos de programação. A oficina deverá ser prática, participativa e utilizável pelo navegador. Duração sugerida anteriormente: duas horas, sujeita à confirmação. Roteiro sugerido: introdução à automação, tipos de automação, prompting, estudo de caso e apresentação de resultados.

## 4. Páginas e navegação

1. **Início / dashboard**: apresentação, instruções, acesso aos laboratórios.
2. **Catálogo de laboratórios**: lista dos módulos e status de disponibilidade.
3. **Arquivos e pastas**: organização, renomeação, classificação e inventário.
4. **Planilhas**: leitura de CSV/Excel, limpeza, filtros e exportação.
5. **PDFs**: extrair, unir e gerar documentos (fase futura).
6. **APIs**: HTTP/JSON e consumo de dados públicos (fase futura).
7. **Automação web**: formulários fictícios e navegação automatizada (fase futura).
8. **IA**: prompting, classificação e integração Python + LLM.
9. **Exercícios e desafios**: enunciados, arquivos-base, critérios e validação.
10. **Resultados**: visualização e download; histórico persistente apenas depois do MVP.
11. **Ambiente Python**: acesso externo ao Codespaces por links dos exercícios.

Navegação sugerida: menu lateral no desktop, adaptável para telas menores. Cada laboratório reutiliza o mesmo layout de abas e componentes.

## 5. Laboratórios e bibliotecas previstas

| Laboratório | Operações | Bibliotecas sugeridas | Prioridade |
|---|---|---|---|
| Arquivos | Organizar por extensão, renomear, inventariar, detectar duplicatas | `pathlib`, `zipfile`, `shutil`, `hashlib` | MVP, primeiro |
| Planilhas | Ler CSV/Excel, remover duplicatas, tratar vazios, exportar | `pandas`, `openpyxl` | MVP |
| IA | Prompts, classificação de dados, apoio ao código | SDK/API de LLM | MVP básico |
| PDFs | Extrair texto, juntar, gerar relatório | `pypdf`, `PyMuPDF`, `reportlab` | Futuro |
| APIs | Requisições, JSON, relatórios | `requests` | Futuro |
| Web | Preenchimento de formulários e navegação em site de demonstração | `playwright` | Futuro |

## 6. Fluxo de uso

1. Participante acessa a página inicial.
2. Escolhe um laboratório.
3. Lê conceitos e objetivos.
4. Executa demonstração no site com dados fictícios ou arquivo próprio.
5. Visualiza resultado e baixa saída.
6. Abre Codespaces com exercício e dependências preparados.
7. Modifica código com apoio de IA, quando apropriado.
8. Resolve desafio e verifica resultado; validação automatizada será progressiva.

## 7. MVP — entregáveis

- Dashboard e catálogo de laboratórios.
- Layout padrão de laboratório e exercício.
- Laboratório de Arquivos funcional (primeiro).
- Laboratório de Planilhas funcional.
- Laboratório de IA com integração limitada e controlada.
- Arquivos de exemplo, instruções e desafios.
- Repositório e devcontainer para Codespaces.
- Visualização e download de resultados.

**Fora do MVP:** editor Python próprio embutido no site, execução livre de código no servidor, construtor visual de fluxos, autenticação obrigatória, progresso persistente, PDFs, APIs e automação web completos.

## 8. Primeiro laboratório — Organização de arquivos

### 8.1 Problema

Uma organização recebeu uma pasta compactada com documentos, planilhas e imagens misturados. O participante deve automatizar a separação dos arquivos em categorias, gerar um inventário e disponibilizar um ZIP organizado.

### 8.2 Entrada

- Upload de um único arquivo `.zip` por execução.
- ZIP fictício de exemplo para download.
- Limites de tamanho do ZIP, quantidade de entradas e tamanho total descompactado: **valores a definir antes da implementação**.
- Somente arquivos regulares; rejeitar links simbólicos e tipos especiais, caminhos absolutos e travessia de diretórios.
- Ignorar ou rejeitar entradas de metadados do sistema conforme regra a definir.

### 8.3 Processamento

1. Validar formulário e arquivo enviado.
2. Inspecionar entradas e limites do ZIP antes de extrair.
3. Processar em diretório temporário isolado, nunca usando caminhos de entrada diretamente como destinos.
4. Classificar pela extensão, sem confiar no conteúdo como prova do tipo real.
5. Categorias iniciais sugeridas: `Documentos` (`.pdf`, `.doc`, `.docx`, `.txt`), `Planilhas` (`.csv`, `.xls`, `.xlsx`), `Imagens` (`.png`, `.jpg`, `.jpeg`), `Outros` (restante permitido).
6. Resolver nomes duplicados sem sobrescrever arquivos (sufixos incrementais).
7. Gerar `relatorio.csv` com nome original, nome final, categoria e status.
8. Criar ZIP de saída com diretórios categorizados e relatório.
9. Retornar resumo e link de download com validade curta, ou entregar diretamente na resposta conforme decisão de implementação.
10. Limpar arquivos temporários após o período definido.

### 8.4 Saída esperada

```text
arquivos_organizados.zip
├── Documentos/
├── Planilhas/
├── Imagens/
├── Outros/
└── relatorio.csv
```

Resumo exibido na página: total de arquivos processados, quantidade por categoria e eventuais avisos.

### 8.5 Exercício no Codespaces

- Script-base Python incompleto para classificar arquivos.
- ZIP de exemplo e instruções `README.md`.
- Desafio: implementar classificação, tratamento de colisões e inventário.
- Testes locais simples para verificar organização e contagens.
- IA como apoio para explicar erros e sugerir melhorias; participante deve entender e testar a solução.

### 8.6 Critérios de aceite

- Upload ZIP válido produz ZIP organizado e inventário correto.
- Arquivos repetidos não são sobrescritos.
- ZIP malicioso, corrompido ou acima dos limites é recusado com mensagem compreensível.
- Nenhum arquivo é escrito fora da área temporária de processamento.
- Usuários simultâneos não compartilham arquivos temporários.
- Resultado pode ser baixado e diretórios temporários são eliminados conforme política definida.

## 9. Rotas Django iniciais propostas

| Método | Caminho | Função |
|---|---|---|
| GET | `/` | Página inicial |
| GET | `/laboratorios/` | Catálogo |
| GET | `/laboratorios/arquivos/` | Página do laboratório |
| POST | `/laboratorios/arquivos/organizar/` | Upload e processamento com CSRF |
| GET | `/exercicios/` | Lista de exercícios |

Outras rotas, inclusive download de resultados, serão definidas na implementação. Views HTML inicialmente; JSON somente onde realmente necessário.

## 10. Organização inicial sugerida do projeto

```text
autolab/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/                 # início, catálogo e navegação
├── laboratorios/         # views, forms, urls e templates dos laboratórios
│   └── services/         # operações Python isoladas por domínio
├── exercicios/           # enunciados, desafios e links Codespaces
├── templates/
├── static/
├── materials/            # exemplos e arquivos-base de exercícios
├── .devcontainer/
│   └── devcontainer.json
├── requirements.txt
├── Dockerfile             # fase de publicação
├── compose.yaml          # fase de publicação
└── README.md
```

Esta é uma sugestão inicial, ajustável antes de criar os apps Django.

## 11. Segurança, privacidade e operação

- CSRF em formulários POST; validar extensão, assinatura/estrutura e limites de uploads.
- Proteção contra ZIP Slip, zip bombs, arquivos especiais, colisões e exaustão de recursos.
- Operações do site são predefinidas; sem `eval`, `exec`, shell arbitrário ou execução de código de usuários.
- Para automações demoradas, considerar fila de tarefas/worker separado; não é obrigatório para o primeiro exercício pequeno.
- Segredos de IA no servidor, com cotas e restrições por usuário/sessão.
- Arquivos temporários isolados e política explícita de limpeza.
- Testes de concorrência e de capacidade antes da oficina.
- HTTPS, configurações de produção do Django, logs sem dados pessoais e limites de requisição.
- Verificar previamente contas, cotas, custos e inicialização do Codespaces para todos os participantes.

## 12. Etapas de desenvolvimento

1. **Planejamento:** consolidar escopo, fluxos, primeiro exercício e contrato de entradas/saídas. (Em andamento)
2. **Ambiente:** repositório, projeto Django, dependências, devcontainer e configurações.
3. **Interface:** base HTML, Bootstrap, navegação, dashboard, catálogo e template de laboratório.
4. **Automações:** serviço de arquivos, formulário, views, downloads e testes; depois planilhas.
5. **Codespaces:** arquivos-base, README, dependências, links e testes com contas distintas.
6. **IA:** selecionar provedor, configurar chave, cotas, prompts e funcionalidades controladas.
7. **Desafios:** enunciados, arquivos, validação e feedback.
8. **Publicação:** Docker, HTTPS, teste de carga e simulação da oficina.

## 13. Próximas decisões em aberto

- Nome definitivo e identidade visual.
- Limites concretos de uploads e retenção de resultados.
- Hospedagem, domínio e capacidade simultânea esperada.
- Provedor/modelo de IA e orçamento.
- Forma de disponibilização dos resultados (download imediato ou URL temporária).
- Política de avaliação de exercícios sem login.
- Se a oficina exigirá conta GitHub de todos os participantes ou terá alternativa sem Codespaces.

## 14. Próxima ação

Enviar `feat/download-resultado`, abrir PR para `dev`, confirmar o CI e revisar. Após integração, iniciar `feat/limpeza-resultados`: comando com simulação e remoção isolada de resultados expirados, testes e instruções de agendamento externo. Depois seguem exercício e Codespaces, Planilhas, IA controlada e preparação para publicação. A autorização de 15/10/2026 permite seguir essas etapas sem nova aprovação a cada branch, parando quando houver decisão pendente ou ação externa necessária. Push manual permanece a cargo do responsável. Organização integrada pelo PR #9.

---

**Regra de manutenção:** atualizar este documento sempre que houver decisão arquitetural, mudança de escopo ou conclusão relevante de uma etapa. Registrar o que está implementado separadamente do que está apenas planejado.


# PARTE II — CONTRATO DE IMPLEMENTAÇÃO PARA OUTRA IA

## 15. Como interpretar esta especificação

**Decisões confirmadas:** Django monolítico, Django Templates, Bootstrap 5, JavaScript progressivo, Python, SQLite em desenvolvimento, GitHub Codespaces para programação, módulos e sequência de aprendizado, ausência de login obrigatório no MVP. **Não substituir** Django por FastAPI, React ou SPA sem aprovação expressa. **Não substituir** Bootstrap por Tailwind no MVP.

**Propostas técnicas adotadas neste documento para tornar o MVP implementável (podem ser revistas explicitamente):** Python 3.12+, Django 5.2 LTS (ou versão LTS suportada na data de implementação), Bootstrap 5.3.x, dependências com versões fixadas após validação, upload ZIP de até 10 MiB, no máximo 100 arquivos, tamanho total descompactado de até 50 MiB, máximo de 10 MiB por entrada, retenção de downloads de até 30 minutos, limite de 20 MiB para planilhas, tempo-alvo de até 15 segundos por requisição de processamento. Os números são **defaults propostos**, não decisões anteriores do usuário. Expor via settings/variáveis de ambiente, documentar e testar. Não prometer limites de CPU/tempo seguros apenas com uma view síncrona; aplicar limites no servidor e infraestrutura.

**Ainda requer definição do responsável:** identidade visual final, domínio e infraestrutura, número de participantes simultâneos, modelo/provedor e orçamento de IA, termos de privacidade e política final de retenção. Não bloquear a implementação local por essas decisões; usar placeholders e serviços opcionais explicitamente desativados.

**Regra para agentes:** primeiro inspecionar repositório e documentação; preservar decisões; implementar em fatias verticais pequenas; executar testes; registrar comandos e resultados; atualizar seção de progresso deste Markdown. Nunca afirmar que uma funcionalidade está pronta sem evidência de teste. Não instalar serviços pagos nem publicar sem autorização.

## 16. Personas, objetivos e jornadas

**Participante iniciante:** acessa site sem login, escolhe laboratório, lê objetivo, baixa exemplo, executa demonstração, visualiza resumo e baixa resultado; depois pode abrir Codespaces. **Participante com Python:** faz os mesmos passos e completa script de exercício, roda testes e compara resultados. **Instrutor:** prepara arquivos fictícios, demonstra fluxos e fornece suporte; painel administrativo dedicado não é obrigatório no MVP.

Jornada de ponta a ponta do laboratório de Arquivos:
1. GET `/` mostra proposta e chamada para `/laboratorios/`.
2. GET `/laboratorios/` mostra três laboratórios MVP (Arquivos, Planilhas, IA) e três futuros (PDFs, APIs, Web), com status reais; laboratórios ainda não prontos devem aparecer claramente como indisponíveis, sem botão funcional enganoso.
3. GET `/laboratorios/arquivos/` exibe título, objetivo, abas acessíveis (Aprender, Executar, Código, Exercício, Desafio, Resultado), exemplos e formulário de upload.
4. Participante pode baixar ZIP de exemplo versionado em `materials/`.
5. POST multipart com CSRF para `/laboratorios/arquivos/organizar/` valida entrada, organiza em diretório temporário isolado, retorna resposta HTML com contagens e link de download.
6. GET `/resultados/<uuid:token>/download/` entrega ZIP somente enquanto token existir e não expirar; token aleatório, não enumerável. Alternativa mais simples de download imediato só pode ser adotada se documentada, sem quebrar a experiência.
7. Participante abre exercício via link Codespaces associado ao repositório e à pasta de exercício, edita script e roda testes no próprio Codespace.
8. Validação automática do site para código externo não será fingida: no MVP a validação de código ocorre por testes locais no Codespaces; a plataforma pode apresentar checklist de conclusão sem persistência.

## 17. Especificação das telas

### 17.1 Layout global

Cabeçalho com marca AutoLab (nome provisório), navegação acessível, link de ajuda. Menu lateral no desktop, menu recolhível no mobile; área central com largura máxima confortável; rodapé com versão e créditos. Componentes reutilizáveis: `base.html`, `partials/sidebar.html`, `partials/navbar.html`, `partials/lab_card.html`, `partials/alerts.html`, `partials/lab_tabs.html`, `partials/upload_form.html`, `partials/result_summary.html`. Bootstrap 5 com tema customizado via CSS em `static/css/autolab.css`. Evitar dependência de jQuery. Respeitar contraste, foco visível, labels, navegação por teclado e mensagens `aria-live` para estados de processamento.

### 17.2 Páginas e estados

| Página | Conteúdo obrigatório | Estados |
|---|---|---|
| Home | título, explicação, CTA laboratórios, fluxo 3 passos | normal |
| Catálogo | cards com resumo, nível, status, ação | disponível / em breve |
| Arquivos | seis abas, arquivo exemplo, upload ZIP, categorias, exemplo de saída | vazio / enviando / erro / sucesso / expirado |
| Planilhas | introdução, CSV exemplo, opção remover duplicatas e linhas vazias, tabela de prévia | vazio / enviando / erro / sucesso |
| IA | introdução a prompts, campo de texto e exemplo de classificação | IA configurada / indisponível / limite atingido / erro |
| Exercícios | cards com enunciado, materiais, link para Codespaces e critérios | pronto / em breve |
| Resultado | métricas, avisos, arquivo gerado e expiração | sucesso / expirado / não encontrado |

**Não criar** cadastro/login, perfil, gamificação, dashboard de métricas persistentes, editor próprio, pagamentos ou painel de administração específico sem necessidade do MVP.

### 17.3 Conteúdo didático de cada módulo

Dados obrigatórios por atividade: `slug`, título, objetivo, nível, pré-requisitos, duração estimada, problema realista, arquivo de entrada, instruções, demonstração, trecho de código comentado, exercício guiado, desafio, resultado esperado, critérios de aceitação, link de Codespaces, dicas e seção de erros comuns. Os conteúdos podem começar como arquivos Markdown/JSON estáticos versionados; não criar modelos de banco sem necessidade.

## 18. Estrutura concreta recomendada

```text
plataforma-autolab/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── laboratorios/
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── arquivo_service.py
│   │   ├── planilha_service.py
│   │   └── ia_service.py
│   └── tests/
│       ├── test_arquivos.py
│       ├── test_planilhas.py
│       └── test_views.py
├── exercicios/
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── templates/
│   ├── base.html
│   ├── core/
│   ├── laboratorios/
│   ├── exercicios/
│   └── partials/
├── static/
│   ├── css/autolab.css
│   └── js/autolab.js
├── materials/
│   ├── arquivos/{exemplo.zip,README.md}/
│   ├── planilhas/{clientes.csv,README.md}/
│   └── ia/{solicitacoes.csv,README.md}/
├── codespaces_exercises/
│   ├── arquivos/{README.md,starter.py,solution_reference.py,tests/}/
│   ├── planilhas/{README.md,starter.py,solution_reference.py,tests/}/
│   └── ia/{README.md,starter.py,tests/}/
├── .devcontainer/{devcontainer.json,Dockerfile}
├── scripts/cleanup_results.py
├── .env.example
├── .gitignore
├── requirements.in
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── README.md
└── PLANEJAMENTO_AUTOLAB.md
```

`solution_reference.py` deve ser mantido fora do caminho principal de apresentação dos desafios ou entregue apenas quando desejado pelo instrutor. Não incluir arquivos reais sensíveis. `materials` pode ser servido como arquivos estáticos públicos somente quando fictícios e inofensivos. Os diretórios de uploads e resultados não ficam sob `static/` nem sob uma pasta pública de media sem proteção.

## 19. Rotas e contrato HTTP detalhado

| Método | Rota | Nome sugerido | Resposta |
|---|---|---|---|
| GET | `/` | `core:home` | HTML 200 |
| GET | `/laboratorios/` | `laboratorios:catalogo` | HTML 200 |
| GET | `/laboratorios/arquivos/` | `laboratorios:arquivos` | HTML 200 |
| POST | `/laboratorios/arquivos/organizar/` | `laboratorios:organizar_arquivos` | HTML 200/303 em sucesso; HTML 400 em entrada inválida; 413 se infraestrutura suportar |
| GET | `/laboratorios/planilhas/` | `laboratorios:planilhas` | HTML 200 |
| POST | `/laboratorios/planilhas/processar/` | `laboratorios:processar_planilha` | HTML 200/303 ou 400 |
| GET | `/laboratorios/ia/` | `laboratorios:ia` | HTML 200 |
| POST | `/laboratorios/ia/classificar/` | `laboratorios:classificar_ia` | HTML 200/303, 400/429/503 conforme erro |
| GET | `/exercicios/` | `exercicios:lista` | HTML 200 |
| GET | `/exercicios/<slug:slug>/` | `exercicios:detalhe` | HTML 200/404 |
| GET | `/resultados/<uuid:token>/download/` | `laboratorios:download_resultado` | FileResponse 200, 404/410 se inválido/expirado |
| GET | `/resultados/<uuid:token>/` | `laboratorios:resultado` | Resumo HTML 200, 404/410 se ausente/expirado |

Usar `reverse()` e `{% url %}` em templates; não espalhar URLs hardcoded. No MVP HTML com formulários Django, não construir API REST paralela sem necessidade. Em POST bem-sucedido, preferir padrão POST/Redirect/GET se houver estado temporário associado; documentar alternativa se escolhida. Todas as rotas POST usam CSRF e métodos restritos.

## 20. Laboratório de Arquivos — algoritmo exato

### 20.1 Formulário e validações

Campo obrigatório `arquivo_zip` (`forms.FileField`), com ajuda textual: formato ZIP, tamanho máximo e tipos de conteúdo aceitos. Conferir limite por bytes reais recebidos, não somente extensão e `Content-Type`. Abrir via `zipfile.ZipFile` e capturar `BadZipFile`, `LargeZipFile` e erros de leitura. Rejeitar ZIP vazio, ZIP criptografado, entrada com caminho absoluto, `..`, barra invertida tratada como separador, drive Windows, entradas especiais e links simbólicos (quando metadados indicarem). Ignorar apenas entradas de diretório normais; não aceitar ZIP aninhado como algo a extrair recursivamente. Limitar número de entradas, tamanho descompactado anunciado e bytes realmente copiados; desconfiar dos metadados. Rejeitar entradas com mesmo caminho normalizado que causem ambiguidades.

**Perfil implementado nesta primeira fatia:** ZIP comum com métodos Stored (0) ou Deflate (8), sem criptografia, ZIP64 ou múltiplos volumes. Outros métodos são recusados explicitamente para manter a leitura limitada. Diretórios normais contam no limite de entradas, mas não como arquivos no resumo. Metadados `__MACOSX`, `.DS_Store` e `Thumbs.db` são recusados, inclusive em subpastas; essa decisão resolve a pendência da seção 8.2. Nomes são comparados após normalização de separadores, Unicode NFC e casefold. ZIP aninhado pode ser um arquivo regular, mas seu conteúdo não é aberto recursivamente.

### 20.2 Mapeamento

| Extensões | Categoria |
|---|---|
| `.pdf`, `.doc`, `.docx`, `.txt` | `Documentos` |
| `.csv`, `.xls`, `.xlsx` | `Planilhas` |
| `.png`, `.jpg`, `.jpeg` | `Imagens` |
| demais arquivos regulares aceitos | `Outros` |

Normalizar extensão para minúsculas. Arquivos sem extensão vão para `Outros`. A classificação é **por nome/extensão**, não antivírus ou inspeção real de formato. Nunca executar, abrir como programa ou renderizar arquivos enviados.

### 20.3 Processamento e colisões

Processar entradas em ordem determinística (por caminho original normalizado). Utilizar somente o nome base do arquivo no destino; remover subpastas originais do layout de saída, preservando caminho original no relatório. Para colisões de nome dentro da categoria, gerar `nome_2.ext`, `nome_3.ext` etc., sem sobrescrita; comparar nomes sem distinção de maiúsculas/minúsculas para resultado previsível em Windows/macOS. Higienizar nomes de arquivo (caracteres de controle, nomes especiais e comprimentos excessivos) mantendo rastreabilidade. Gerar CSV UTF-8 com cabeçalho `caminho_original,nome_saida,categoria,status`; escapar conteúdo como texto ao exportar para CSV e neutralizar células que começam com `=`, `+`, `-` ou `@` para reduzir risco de fórmula em planilhas. CSV final fica na raiz do ZIP; não listar o próprio relatório como arquivo de entrada. Criar ZIP de saída com `Documentos/`, `Planilhas/`, `Imagens/`, `Outros/` (podem estar vazios) e `relatorio.csv`.

### 20.4 Contrato do serviço

Criar serviço Python desacoplado de `HttpRequest`/templates, com assinatura conceitual:

```python
@dataclass(frozen=True)
class ResultadoOrganizacao:
    output_path: Path
    total_arquivos: int
    por_categoria: dict[str, int]
    avisos: list[str]


def organizar_zip(entrada: Path, diretorio_trabalho: Path) -> ResultadoOrganizacao:
    """Valida e organiza ZIP sem escrever fora do diretório de trabalho."""
```

A view trata formulário, mensagens, token de download e status HTTP; o serviço trata exclusivamente regras de domínio. Exceções de domínio devem ser específicas (ex.: `ArquivoInvalido`, `LimiteExcedido`) e traduzidas para mensagens seguras ao usuário. Nunca exibir traceback na UI.

**Contrato implementado:** `organizar_zip(entrada, diretorio_trabalho, *, limites: LimitesZIP)` exige limites explícitos, sem importar settings Django. A área de trabalho deve existir e ser controlada pelo chamador; cada execução cria nela um subdiretório privado exclusivo e retorna o ZIP gerado. A entrada é inspecionada integralmente antes de criar a saída e copiada em blocos diretamente para o novo ZIP, sem extração em disco. Limites reais e integridade são conferidos também na cópia. Falhas descartam somente a execução incompleta; o chamador gerencia a retenção das saídas concluídas.

Nomes de saída usam Unicode NFC, substituem caracteres especiais e nomes reservados do Windows e ficam limitados a 200 bytes UTF-8, com extensão de até 32 bytes. Colisões incluem nomes gerados por sufixos anteriores. O CSV registra caminho original, caminho relativo completo de saída, categoria e status `organizado`/`renomeado`; células com prefixos de fórmula recebem apóstrofo, inclusive após espaços iniciais. Classificação usa a extensão original, sem inspecionar o formato real. Ordem de entradas e datas internas fixas tornam o ZIP reproduzível no ambiente testado.

### 20.5 Resultados temporários

Criar `RESULTS_ROOT` fora de static/media pública. Para cada execução usar UUID aleatório e diretório isolado; manter metadados mínimos (`token`, `arquivo`, `criado_em`, `expira_em`) em SQLite ou manifesto protegido no servidor. Escolha recomendada: modelo `ResultadoTemporario` com UUID como chave pública, path relativo, criação e expiração; não armazenar caminho absoluto fornecido pelo cliente. Download via view que valida token, prazo, existência e localização sob `RESULTS_ROOT`, usando `FileResponse` com `Content-Disposition: attachment`; `Cache-Control: no-store`. Rotina de limpeza por management command (`python manage.py limpar_resultados`) e agendamento externo; **não** depender de cron dentro do processo web. Garantir que exclusão não afete arquivos de outra execução. Para MVP sem login, quem possuir o link de resultado pode baixá-lo até expirar; informar isso e usar token imprevisível.

**Implementado na entrega de download:** modelo SQLite com migração, UUID4, caminho relativo canônico, criação/expiração, tipo e resumo (contagens e avisos). Nome do upload não é persistido nem usado como caminho; campos de resumo permitem POST/Redirect/GET sem guardar o arquivo original ou depender de sessão. POST válido responde 303 para a página de resumo; atualizar essa página não processa novamente. Upload inválido retorna 400; falha de armazenamento retorna 503 com mensagem segura. O upload original é descartado ao terminar a organização. Falhas de processamento ou gravação dos metadados removem somente a área recém-criada.

Resumo e download aceitam GET/HEAD e usam `Cache-Control: no-store`; em sucesso também usam `Referrer-Policy: no-referrer`. Token inexistente, tipo diferente, arquivo ausente, caminho adulterado ou link simbólico retornam 404; prazo atingido retorna 410. A área usa caminho `<token>/arquivos_organizados.zip`, fora de static/media. `RESULT_TTL_MINUTES` positivo mantém default de 30 minutos, contado após o processamento. O prazo bloqueia novos acessos e não interrompe um download já iniciado. Não há exclusão automática nesta branch; o comando de limpeza será entregue em seguida, com agendamento externo necessário antes da oficina. O catálogo permanece em breve até completar esse ciclo de vida.

### 20.6 Exemplo de saída

Entrada: `relatorio.pdf`, `foto.JPG`, `clientes.csv`, `notas.txt`, `subpasta/relatorio.pdf`. Saída: `Documentos/relatorio.pdf`, `Documentos/relatorio_2.pdf`, `Documentos/notas.txt`, `Imagens/foto.JPG`, `Planilhas/clientes.csv` e `relatorio.csv`. Contagens: Documentos=3, Planilhas=1, Imagens=1, Outros=0, total=5.

## 21. Laboratório de Planilhas — primeira versão

Entrada: um `.csv` UTF-8 ou `.xlsx`, com dados fictícios; limite proposto de 20 MiB, até 10 mil linhas e 30 colunas, ajustáveis. Não aceitar `.xlsm` nem executar macros; `.xls` fica fora do primeiro corte. Operações selecionáveis: remover linhas completamente vazias, remover duplicatas completas, aparar espaços em células textuais. **Não apagar registros com campos parcialmente vazios automaticamente**; apenas reportar quantidade, a menos que o usuário selecione explicitamente regra futura. Processar com pandas, exportar `resultado.csv` em UTF-8 com BOM ou `resultado.xlsx` de forma consistente e documentada. Exibir até 10 linhas de prévia escapadas pelo template e métricas antes/depois. Limitar memória e dimensões; não renderizar HTML vindo de células com `safe`. CSVs devem ter tratamento contra formula injection na exportação; arquivos XLSX gerados devem tratar valores iniciados por fórmula como texto. Gerar arquivo de exemplo com duplicatas, espaços e campos vazios.

Contrato conceitual: `processar_planilha(entrada: Path, opcoes: OpcoesPlanilha, saida: Path) -> ResultadoPlanilha`, retornando contagens e caminho de saída. Usar serviço independente da view. Exercício Codespaces: ler CSV, limpar dados, exportar e validar contagem com `pytest`.

## 22. Laboratório de IA — primeira versão e fallback

**Objetivo didático:** demonstrar a diferença entre automação determinística e análise com LLM. Caso: classificar solicitações administrativas fictícias em categorias predefinidas (`TI`, `Financeiro`, `Acadêmico`, `Outros`) e prioridade (`baixa`, `media`, `alta`). Entrada: texto curto ou CSV de solicitações fictícias, com limite de tamanho e quantidade de registros; saída: tabela com categoria, prioridade e justificativa curta, além de CSV para download.

Implementar interface `classificar_solicitacoes(itens: list[str]) -> list[Classificacao]` e provedor desacoplado. Credencial `LLM_API_KEY` apenas no backend e variável `LLM_ENABLED=false` por padrão. Provedor/modelo são **pendências**, portanto não fixar marca, endpoint ou preço. Validar resposta estruturada com schema; limitar quantidade de itens, tokens, timeout, concorrência e orçamento. Não permitir que prompt do usuário selecione ferramentas, comandos shell, URLs arbitrárias ou arquivos do servidor. Tratar texto enviado como dados não confiáveis (prompt injection). Se IA estiver desativada, mostrar página didática e exemplo de saída **explicitamente rotulado como simulação**, sem fingir chamada real. Testes devem usar mocks, sem custo de API.

## 23. GitHub Codespaces — contrato de preparação

Manter `.devcontainer/devcontainer.json` com Python e extensões úteis (Python, Pylance), `postCreateCommand` para instalar dependências e `forwardPorts` apenas se necessário. Repositório deve ter `README.md` com requisitos de conta GitHub, como abrir Codespaces, iniciar terminal, executar `python --version`, instalar dependências se necessário e rodar `pytest`. Separar arquivos `starter.py` com `TODO`s, `README.md` de cada exercício, dados fictícios e testes locais. Não colocar chave de IA, `.env`, tokens ou dados reais no Git. Fornecer URL de Codespaces apenas quando nome do repositório for conhecido; nunca inventar URL. Não depender de Codespaces para funcionamento dos botões de demonstração do site. Preparar plano B: scripts `.py` e materiais para download, executáveis localmente por quem já tenha Python.

## 24. Configuração e dependências

`.env.example` deve documentar ao menos:

```dotenv
DJANGO_SECRET_KEY=trocar-em-producao
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=
DATABASE_URL=
RESULTS_ROOT=./var/results
RESULT_TTL_MINUTES=30
MAX_ZIP_UPLOAD_BYTES=10485760
MAX_ZIP_ENTRIES=100
MAX_ZIP_UNCOMPRESSED_BYTES=52428800
MAX_ZIP_ENTRY_BYTES=10485760
LLM_ENABLED=false
LLM_API_KEY=
LLM_MODEL=
```

Ler variáveis com biblioteca adequada ou stdlib, sem incluir segredos no versionamento. Configuração local pode usar SQLite. Em produção: `DEBUG=False`, hosts explícitos, HTTPS, cookies seguros, cabeçalhos adequados, estáticos servidos por solução apropriada, banco persistente, backups quando houver dados persistentes, limites de requisição no proxy, observabilidade e worker/timeout dimensionados. Bootstrap pode usar CDN no protótipo, mas para oficina com rede instável preferir assets versionados locais. Fixar dependências testadas e fornecer `requirements.txt` reproduzível.

## 25. Modelagem de dados mínima

O MVP não precisa de modelo de usuário, curso ou progresso. Modelo opcional/recomendado para resultado temporário:

| Campo | Tipo | Regra |
|---|---|---|
| `token` | UUIDField primary_key | `uuid4`, não sequencial |
| `relative_path` | CharField | path relativo controlado pelo servidor |
| `created_at` | DateTimeField | automático |
| `expires_at` | DateTimeField | UTC-aware |
| `kind` | CharField | `arquivos`, `planilhas`, `ia` |
| `total_arquivos` | PositiveIntegerField | total de arquivos processados |
| `por_categoria` | JSONField | contagens do resumo |
| `avisos` | JSONField | ajustes de nomes; exibição escapada |

Na primeira implementação, o nome do upload não é armazenado por não ser necessário à apresentação. Contagens e avisos são os metadados adicionais usados para reconstruir o resumo após redirecionamento; o conteúdo dos arquivos permanece somente no ZIP temporário.

Nunca persistir conteúdo de arquivos ou prompts por padrão. Evitar adicionar modelos de `Laboratorio`/`Exercicio` se dados estáticos versionados atenderem ao MVP; avaliar modelagem no futuro para painel do instrutor.

## 26. Critérios de qualidade e testes

Usar `pytest` + `pytest-django` ou `django.test.TestCase` de forma consistente. Cobertura prioritária:

1. GET home, catálogo, laboratório, exercícios retornam 200 e conteúdo esperado.
2. POST sem CSRF é bloqueado em teste que habilite verificação de CSRF.
3. Upload ausente, ZIP corrompido, vazio, criptografado e acima do limite produz erro compreensível.
4. ZIP com `../`, caminho absoluto, backslash malicioso, symlink e entradas especiais é rejeitado.
5. ZIP bomb por tamanho declarado ou cópia real é interrompido.
6. Extensões maiúsculas, arquivos sem extensão, diretórios vazios e nomes duplicados produzem categorias corretas.
7. `relatorio.csv` tem colunas, contagens e linhas esperadas; arquivos de entrada não são sobrescritos.
8. Duas execuções paralelas têm diretórios/tokens independentes.
9. Download por token válido funciona; token inexistente e expirado não disponibilizam arquivo.
10. Limpeza apaga somente resultados expirados, com tratamento de arquivos ausentes.
11. Planilha remove duplicatas corretamente e não elimina linhas parcialmente preenchidas sem opção explícita.
12. IA desabilitada não chama provedor; IA mockada retorna estrutura validada; erros de provedor são tratados.
13. Templates escapam dados controlados pelo usuário; nenhum traceback ou segredo aparece na resposta.
14. Verificar usabilidade manual em desktop e mobile, foco de teclado, mensagens de erro e abertura do Codespaces.

Comandos esperados após setup (ajustar à ferramenta de testes escolhida):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver
```

## 27. Critérios de pronto por entrega

**Fase 1 — Base Django:** projeto inicia, apps registrados, rotas e templates funcionam, Bootstrap aplicado, `manage.py check` passa, README de setup atualizado.

**Fase 2 — Arquivos (primeira fatia funcional):** upload, validação, processamento, relatório, download, expiração, limpeza e testes de segurança funcionam de ponta a ponta. Essa é a **primeira release demonstrável**.

**Fase 3 — Planilhas:** upload CSV/XLSX, operações documentadas, prévia, métricas, download e testes.

**Fase 4 — Codespaces:** devcontainer abre, dependências instalam, `starter.py` executa, testes locais funcionam; instrutor verifica com outra conta.

**Fase 5 — IA:** página educativa, modo simulado rotulado, integração real apenas após definir provedor e orçamento; testes com mocks e limites de uso.

**Fase 6 — Oficina/publicação:** domínio/HTTPS definidos, simulação com usuários, limites de upload/proxy configurados, materiais revisados, plano de contingência e checklist do instrutor.

## 28. Sequência exata de tarefas para o agente implementador

1. Inspecionar o repositório, registrar o que existe e comparar com este documento.
2. Criar projeto Django, apps `core`, `laboratorios`, `exercicios`, `.gitignore`, `.env.example`, requirements e README.
3. Configurar settings por ambiente, rotas com namespace e templates globais.
4. Criar layout Bootstrap responsivo, dashboard, catálogo e página do laboratório de Arquivos com estados de UI.
5. Implementar serviço puro `organizar_zip` e testes unitários **antes** de conectar à view.
6. Implementar formulário, view POST, armazenamento temporário, resultado, download e comando de limpeza.
7. Criar ZIP fictício de exemplo e exercício Codespaces para Arquivos.
8. Rodar testes, corrigir problemas, registrar arquivos criados e evidências no changelog.
9. Repetir fatia vertical para Planilhas.
10. Criar IA com modo simulado claramente identificado; conectar provedor real somente após decisão.
11. Implementar catálogo de exercícios e links reais do repositório.
12. Preparar Docker/publicação e ensaio da oficina somente após testes locais.

Para cada passo, entregar: arquivos alterados, justificativa curta, comandos executados, resultados dos testes, pendências e atualização deste `.md`. Não avançar para novos módulos quando o fluxo básico de Arquivos ainda estiver quebrado.

## 29. Não objetivos e anti-padrões

- Não criar frontend React/Vue/Next separado nem migrar para FastAPI.
- Não substituir Bootstrap por Tailwind sem solicitação.
- Não criar editor VS Code embutido, servidor Jupyter multiusuário ou sandbox própria no MVP.
- Não executar `eval`, `exec`, `subprocess` com código do usuário nem comandos shell baseados em entrada externa.
- Não extrair ZIP com `extractall()` sobre conteúdo não confiável sem validação; preferir cópia controlada de cada entrada.
- Não deixar uploads ou resultados permanentemente acessíveis por URL pública previsível.
- Não usar credenciais reais em exercícios nem expor chaves de IA no HTML/JavaScript.
- Não apresentar operações ainda não implementadas como disponíveis.
- Não inventar URL do GitHub, domínio, fornecedor LLM ou valores de custos.
- Não considerar a plataforma finalizada só porque as páginas renderizam; processamento, segurança e testes são parte da entrega.

## 30. Registro de decisões e progresso

| Data | Tipo | Decisão/estado |
|---|---|---|
| 14/10/2026 | Confirmado | Plataforma educacional modular para automação com IA e Python |
| 14/10/2026 | Confirmado | Django monolítico no lugar de React + FastAPI |
| 14/10/2026 | Confirmado | Bootstrap 5 em vez de Tailwind para o MVP |
| 14/10/2026 | Confirmado | GitHub Codespaces como ambiente externo de programação |
| 14/10/2026 | Confirmado | Arquivos primeiro; Planilhas e IA no MVP; PDFs/APIs/Web depois |
| 14/10/2026 | Proposta técnica | Limites e retenção da seção 15, sujeitos à validação |
| 14/10/2026 | Implementado | Base Django e layout Bootstrap 5.3.3 integrados na `dev` local; settings por ambiente, rotas com namespace, navegacao responsiva e mensagens |
| 14/10/2026 | Integrado | Dashboard inicial com apresentacao, fluxo em tres passos e destaques MVP; todos os laboratorios marcados como em breve; PR #2 integrado em `dev` |
| 14/10/2026 | Escopo | Catalogo, Arquivos e Exercicios possuem apenas paginas provisorias com layout para sustentar a navegacao; nao representam funcionalidades completas |
| 14/10/2026 | Integrado | Django atualizado de 5.1.15 para 5.2.18; dependencias restantes preservadas; README alinhado; PR #3 integrado em `dev` |
| 14/10/2026 | Integrado | Layout integrado pelo PR #1; PRs #1, #2 e #3 preservam commits com merge commit; `dev` sincronizada em `28ab2b8` |
| 14/10/2026 | Integrado | Workflow de testes e modelo de PR integrados pelo PR #4; falha inicial de contexto corrigida; checks remotos aprovados |
| 14/10/2026 | Integrado | Catalogo com seis laboratorios, niveis, resumos e disponibilidade; PR #5 integrado com dois checks aprovados; todas as automacoes permanecem em breve |
| 14/10/2026 | Integrado | Pagina didatica de Arquivos com seis etapas e ZIP ficticio baixavel; PR #6 integrado com os dois checks aprovados |
| 14/10/2026 | Integrado | Formulario e POST de recebimento ZIP integrados pelo PR #7 com dois checks aprovados |
| 14/10/2026 | Implementado na feature | Inspecao ZIP desacoplada de Django; limites de entradas e bytes reais, caminhos, tipos, CRC e cabecalhos; sem extracao ou escrita |
| 15/10/2026 | Integrado | Inspeção ZIP integrada pelo PR #8 com dois checks aprovados; `dev` sincronizada em `5ffb3ff` |
| 15/10/2026 | Implementado na feature | Serviço de organização por extensão com nomes seguros, colisões sem sobrescrita, inventário CSV e ZIP isolado; integração web em entrega posterior |
| 15/10/2026 | Integrado | Organização integrada pelo PR #9 com dois checks aprovados; `dev` sincronizada em `5779eb3` |
| 15/10/2026 | Implementado na feature | Resumo e download temporário com token, POST/Redirect/GET e expiração; limpeza ainda em entrega própria |
| 14/10/2026 | Decisao tecnica | Primeiro perfil aceita Stored/Deflate; recusa ZIP64, criptografia, multiplos volumes, outros metodos e metadados de sistema; restricoes explicitas na UI e materiais |
| 14/10/2026 | Rotas existentes | Catalogo permanece em `core:catalogo` no caminho `/laboratorios/`; a sugestao `laboratorios:catalogo` da secao 19 nao foi adotada |

### Evidencias da entrega do dashboard

Registro histórico da implementação, anterior ao envio e aos merges dos PRs #1 e #2. As pendências de sincronização abaixo já foram resolvidas; a verificação visual continua pendente.

- Branch: `feat/dashboard-inicial`; base local: `dev`, commit `1b456be`.
- `git fetch origin` executado; `git rev-list --left-right --count dev...origin/dev` retornou `5 0`. A base local inclui cinco commits ainda nao presentes na `origin/dev`; reconciliar a integracao do layout antes de publicar o PR do dashboard.
- `.venv/bin/python manage.py check`: sem problemas.
- `.venv/bin/python manage.py test`: 21 testes, todos passaram.
- `.venv/bin/python -m pytest -p no:cacheprovider`: 21 testes passaram.
- `git diff --check`: sem problemas.
- Testes cobrem renderizacao da home, fluxo em tres passos, CTA do catalogo, estados em breve, acoes desativadas e paginas provisorias de navegacao, alem dos testes existentes de layout e configuracao.
- Verificacao visual em navegador, mobile e teclado ainda nao realizada. Os testes de HTML nao comprovam contraste ou usabilidade visual.
- Sem processamento de uploads, downloads, exercicios executaveis ou devcontainer nesta entrega. Sem push, merge ou publicacao.

### Changelog

- **15/10/2026 — download de resultados:** view conectada à organização, metadados temporários com migração, resumo após redirecionamento e download com validação de token/caminho/prazo. Upload descartado ao concluir; limpeza periódica pendente. Organização integrada pelo PR #9.
- **15/10/2026 — organização de arquivos:** serviço Python independente de Django gera categorias, inventário e ZIP em diretório exclusivo. Cópia limitada reutiliza o leitor da validação; erros eliminam a saída parcial. Validação integrada pelo PR #8; fluxo web de resultados permanece pendente.
- **14/10/2026 — validação ZIP:** pré-inspeção limitada do diretório central, inspeção de metadados e leitura limitada de Stored/Deflate com CRC. Formulário traduz erros de domínio; resumo exibe quantidade de arquivos sem gerar resultados. Upload integrado pelo PR #7.
- **14/10/2026 — upload:** formulário ZIP e endpoint POST adicionados com validação inicial de extensão, arquivo vazio, quantidade e tamanho. Conferência de bytes lidos e estados de erro/recebimento na aba Executar. Página didática integrada pelo PR #6.
- **14/10/2026 — página de Arquivos:** seis etapas Bootstrap, categorias, trecho Python comentado, exercício conceitual, desafio e resultado esperado. ZIP fictício versionado com download por rota fixa GET/HEAD, sem acesso a caminhos do cliente. Catálogo integrado pelo PR #5.
- **14/10/2026 — catálogo:** catálogo completo com três módulos da primeira versão e três futuros; conteúdo estático em `core/catalogo.py`, card reutilizável e disponibilidade centralizada na home. Testes e verificações visuais desktop/mobile concluídos; sem processamento de automações.
- **14/10/2026 — qualidade:** workflow GitHub Actions e modelo obrigatório de PR adicionados; README explica checks e reprodução local. Progresso reconciliado com a integração dos PRs #1, #2 e #3, sem alterar os contratos funcionais.
- **14/10/2026 — Django LTS:** dependência direta alterada para `>=5.2,<5.3`, lock regenerado, ambiente sincronizado e compatibilidade validada pelos testes existentes. Sem alterações funcionais, de settings ou de modelos.
- **14/10/2026 — dashboard:** progresso alinhado ao repositorio; home implementada e testada na feature, disponibilidade corrigida e paginas provisorias de navegacao preservadas. Contratos funcionais do MVP mantidos.
- **v2.0:** contrato de implementação detalhado, UX, rotas, algoritmos, defaults operacionais, serviços, segurança, testes, critérios de aceite, tarefas e decisões confirmadas vs. propostas.
- **v1.0:** planejamento geral, módulos, arquitetura Django e primeiro laboratório.

### Checklist vivo de progresso

- [x] Objetivo, módulos, navegação e arquitetura definidos.
- [x] Bootstrap 5 escolhido.
- [x] Especificação técnica de Arquivos e contratos de MVP documentados.
- [x] Repositório Django criado.
- [x] Layout e navegação integrados em `dev` local e remota (PR #1).
- [x] Dashboard inicial implementado, testado e integrado em `dev` (PR #2).
- [x] Django 5.2.18 instalado, validado e integrado em `dev` (PR #3).
- [x] Workflow CI e modelo de PR implementados na feature, com validação local.
- [x] CI confirmado no GitHub e qualidade integrada pelo PR #4.
- [x] Catálogo completo integrado em `dev` pelo PR #5.
- [x] Página didática e ZIP de exemplo integrados em `dev` pelo PR #6.
- [x] Formulário e recebimento ZIP integrados em `dev` pelo PR #7.
- [x] Inspeção ZIP implementada, testada e integrada em `dev` pelo PR #8.
- [x] Serviço de organização e inventário implementado, testado e integrado pelo PR #9.
- [x] Resumo, download por token e bloqueio por expiração implementados e testados na feature (envio e integração pendentes).
- [ ] Limpeza de resultados expirados implementada e agendada externamente.
- [ ] Laboratório de Arquivos implementado e testado.
- [ ] Laboratório de Planilhas implementado e testado.
- [ ] Devcontainer Codespaces validado.
- [ ] Laboratório de IA implementado e testado.
- [ ] Testes de concorrência e ensaio da oficina.
- [ ] Publicação em ambiente online.

**Instrução para a próxima IA:** comece pelo item 1 da seção 28. Antes de modificar escopo, confira as decisões confirmadas na seção 15. Atualize esta documentação após cada etapa.

### Evidencias e dependencias da atualizacao LTS

Registro histórico da implementação: o envio e a integração aqui descritos como pendentes foram concluídos pelos PRs #1, #2 e #3. A base encadeada foi resolvida antes do merge para `dev`.

- Branch: `feat/atualizacao-django-lts`; origem excepcional: `feat/dashboard-inicial`, commit `75494ff`. Essa dependência segue o fluxo de branches encadeadas da política de versionamento.
- `git pull --ff-only origin dev` executado: Already up to date. A `dev` local continua cinco commits à frente do remoto; nenhum push direto em `dev` foi feito.
- O push do dashboard foi tentado, mas falhou por ausência de credenciais HTTPS do GitHub. Não confundir commits locais com envio concluído.
- `uv pip compile requirements.in -o requirements.txt --upgrade-package django --cache-dir /tmp/autolab-uv-cache`: fixou Django 5.2.18 sem atualizar as outras nove dependências.
- `uv pip sync requirements.txt --python .venv/bin/python --cache-dir /tmp/autolab-uv-cache`: substituiu Django 5.1.15 por 5.2.18.
- `.venv/bin/python -m django --version`: 5.2.18.
- `.venv/bin/python manage.py check`: sem problemas.
- `.venv/bin/python manage.py test` e `.venv/bin/python -m pytest -p no:cacheprovider`: 21 testes passaram em cada suíte.
- `.venv/bin/python manage.py makemigrations --check --dry-run`: No changes detected.
- `uv pip check --python .venv/bin/python --cache-dir /tmp/autolab-uv-cache`: dependências compatíveis.
- Nenhum teste adicional foi necessário: a suíte existente verifica as rotas, configuração e renderização afetadas pela atualização. Validação visual e configuração de produção permanecem em suas entregas próprias.
- PR previsto: LTS → dashboard enquanto a base não estiver integrada. Ordem de integração: layout → dashboard → LTS. Após integração da base, atualizar a branch e mudar o destino do PR para `dev` antes do merge. Push, merge e rebase não foram realizados nesta entrega.

### Evidências da qualidade do repositório

- Branch: `feat/qualidade-repositorio`; base: `dev` sincronizada, commit `28ab2b8`. Nenhuma alteração funcional nos laboratórios.
- `.github/workflows/tests.yml`: GitHub Actions em PRs para `dev`/`main` e pushes para `feat/**`, `dev` e `main`; Python 3.12 em Ubuntu 24.04; instalação de dependências fixadas; `pip check`, `manage.py check`, verificação de migrações, testes Django e pytest.
- Actions oficiais checkout e setup-python v7 fixadas por SHA consultado na API pública do GitHub. Permissão `contents: read`, sem credenciais persistidas no checkout; IA desativada e resultados temporários. Execuções antigas do mesmo PR/ref são canceladas; job limitado a dez minutos.
- `.github/pull_request_template.md`: modelo da seção 13 da política de branches, sem alterações de requisitos.
- Dependências instaladas em ambiente novo `/tmp/autolab-ci-venv`, com Python 3.12.3. Comandos do CI reproduzidos com as variáveis de ambiente de teste; `pip check` e `manage.py check` passaram, nenhuma migração pendente, 21 testes passaram em cada suíte.
- YAML lido com PyYAML; eventos, permissões e modo IA conferidos. `git diff --check` passou.
- Nenhum teste adicional de produto necessário: a entrega configura a execução dos testes existentes. Falhas de comandos encerram a etapa; não há `continue-on-error`.
- Execução real de actions, cache e runner hospedado ainda não confirmada; depende do push e do primeiro check remoto. Não declarar o CI remoto aprovado com base na execução local.
- Proteção de branches não foi modificada. Exigir o check `Django / Python 3.12` requer configuração separada após a primeira execução.
- Primeira execução remota: run `38630913222` falhou antes dos jobs por uso inválido de `runner.temp` no bloco `jobs.django.env`. Corrigido para configurar `RESULTS_ROOT` em uma etapa via `RUNNER_TEMP` e `GITHUB_ENV`. A validação YAML local não substitui a validação das expressões do GitHub; aguardar nova execução antes da integração.
- Atualização: runs `38631610859` e `38631608939`, no commit `a7dc53c`, concluídos com sucesso. PR #4 integrado com merge commit em `4734c14`; `dev` local sincronizada. As pendências de execução remota acima descrevem o estado anterior à correção.

### Evidências da entrega do catálogo

- Branch: `feat/catalogo-laboratorios`, criada da `dev` em `28ab2b8`. A qualidade foi integrada durante o desenvolvimento; a base foi atualizada por merge da `dev` em `4734c14`, sem conflitos ou reescrita de commits.
- Dados estáticos versionados em `core/catalogo.py`; catálogo mantém a rota `core:catalogo` em `/laboratorios/`. Nenhum modelo de banco adicionado.
- Arquivos, Planilhas e IA na primeira versão; PDFs, APIs e Automação Web explicitamente futuros. Níveis estimados para orientar iniciantes; conteúdos detalhados ficam nas entregas didáticas próprias.
- `partials/lab_card.html` compartilhado entre home e catálogo. Um botão de acesso só aparece quando disponibilidade e rota válida estiverem declaradas. Todos os seis módulos atuais permanecem em breve; Arquivos tem apenas página provisória.
- `.venv/bin/python manage.py check`: sem problemas; `.venv/bin/python manage.py test` e `.venv/bin/python -m pytest -p no:cacheprovider`: 26 testes passaram em cada suíte; migrações pendentes: nenhuma.
- Testes cobrem seis módulos, níveis/resumos, três destaques MVP na home, ações incompletas desativadas, disponibilidade compartilhada e flag disponível sem rota.
- Verificação no navegador local em desktop e mobile 390 × 844: cards legíveis e sem rolagem horizontal no tamanho mobile testado; menu mobile abriu. Tab seguido de Enter no link para pular ao conteúdo levou o foco a `main-content`. Isso não constitui auditoria completa de acessibilidade ou contraste.
- Evidências visuais locais: `/tmp/autolab-catalogo-desktop.png` e `/tmp/autolab-catalogo-mobile.png` (não versionadas).
- Execução remota desta branch ainda pendente do push manual e do PR. Nenhum upload, download, exercício ou operação de laboratório implementado nesta entrega.
- Atualização: catálogo integrado pelo PR #5 após aprovação dos dois checks; `dev` local sincronizada em `94dbb4a`. A pendência de envio acima é histórica.

### Evidências da página didática de Arquivos

- Branch: `feat/laboratorio-arquivos-pagina`; base: `dev`, commit `94dbb4a`.
- Seis etapas: Aprender, Executar, Código Python, Exercício, Desafio e Resultado; abas Bootstrap com IDs, controles e painéis associados. Sem JavaScript, um fallback mostra todas as seções; esse fallback não foi testado em navegador nesta entrega.
- Categorias e rastreabilidade conforme contrato; código exibido somente classifica nomes. Duração de 20 minutos é uma sugestão didática, a validar no ensaio.
- `materials/arquivos/exemplo.zip` contém seis entradas fictícias: três TXT, um CSV, um PNG válido e um arquivo sem extensão. Documentos homônimos em pastas diferentes têm conteúdos distintos. README descreve contagens e resultado esperado.
- GET/HEAD `/laboratorios/arquivos/exemplo/`, nome `laboratorios:exemplo_arquivos`, entrega exclusivamente o ZIP público versionado via FileResponse. POST recusado; parâmetros do cliente não determinam o caminho. Material ausente retorna 404.
- `.venv/bin/python manage.py check`: sem problemas; testes Django e pytest: 32 passaram em cada suíte; `makemigrations --check --dry-run`: nenhuma mudança; `git diff --check`: sem problemas.
- Testes cobrem as seis etapas, estado ainda indisponível, distinção entre referência e execução, conteúdo e integridade do ZIP, caminho fixo, 404 e recusa de POST.
- Navegador local: seis abas verificadas por clique; seta direita alternou Aprender → Executar e atualizou foco/seleção; download do exemplo concluído. Desktop e mobile 390 × 844 sem rolagem horizontal da página, incluindo aba Código Python. Verificação pontual, sem auditoria completa de acessibilidade.
- Capturas locais: `/tmp/autolab-arquivos-desktop.png` e `/tmp/autolab-arquivos-mobile.png`, não versionadas.
- Catálogo mantém Arquivos indisponível para execução. Formulário, validação segura, serviço, resultados temporários e exercício Codespaces permanecem nas próximas branches. Nenhum código de participante executado no servidor.
- Atualização: PR #6 integrado após os dois checks aprovados; `dev` local sincronizada em `4c7e013`. As pendências de envio acima são históricas; o formulário foi desenvolvido na entrega seguinte.

### Evidências do recebimento inicial de ZIP

- Branch: `feat/upload-arquivos`; base: `dev`, commit `4c7e013`. Duas imagens locais não versionadas preexistentes foram preservadas e não incluídas nos commits.
- Campo obrigatório `arquivo_zip`; formulário multipart com CSRF, extensão `.zip` sem distinção de maiúsculas e limite configurável `MAX_ZIP_UPLOAD_BYTES`, mantendo o default proposto de 10 MiB.
- Arquivo ausente, vazio, extensão incorreta, bytes acima do limite e múltiplos arquivos (inclusive em campos extras) são recusados. `Content-Type` do cliente não é usado como prova de formato. A verificação inicial lê os bytes recebidos e restaura a posição do arquivo, sem interpretar o ZIP.
- POST `/laboratorios/arquivos/organizar/`, nome `laboratorios:organizar_arquivos`: HTML 200 em recebimento aceito; 400 para erro do formulário; 403 sem CSRF; 405 para métodos diferentes de POST. O nome da rota segue o contrato, mas a organização ainda não ocorre.
- Aba Executar ativa após POST, com erro acessível ou confirmação explícita de que apenas nome/tamanho foram conferidos. Nome do arquivo escapado pelo template. Não há resultado persistido, download de saída ou execução de código.
- Resposta HTML direta, sem POST/Redirect/GET por enquanto: esta entrega não cria estado persistente ou resultado temporário. O padrão será revisto quando a organização e seus tokens forem integrados.
- Arquivos podem ser temporariamente armazenados pelos upload handlers padrão do Django durante a requisição; não são salvos pela aplicação. O limite do formulário é posterior ao recebimento HTTP e não substitui limites no proxy ou servidor.
- `.venv/bin/python manage.py check`: sem problemas; testes Django e pytest: 44 passaram em cada suíte; migrações: nenhuma mudança; `git diff --check`: sem problemas.
- Testes cobrem CSRF real, método, tamanho exato e acima do limite, bytes reais apesar de metadado menor, envios múltiplos, MIME não confiável, escape do nome e ausência de resultados persistidos.
- Navegador local: envio do ZIP fictício aceito com confirmação correta; README enviado como arquivo inválido retornou erro de extensão e manteve a aba Executar ativa. Mobile 390 × 844 sem rolagem horizontal no estado aceito. Capturas locais `/tmp/autolab-upload-sucesso.png` e `/tmp/autolab-upload-erro-mobile.png`, não versionadas.
- Catálogo mantém Arquivos como em breve. ZIPs corrompidos, criptografados, com caminhos maliciosos ou expansões abusivas ainda não são inspecionados; não extrair ou organizar até concluir `feat/validacao-zip`. CI remoto desta feature depende do push manual.
- Atualização: upload integrado pelo PR #7 com dois checks aprovados; `dev` sincronizada em `6a02433`. A limitação de inspeção acima é histórica e foi tratada pela entrega seguinte.

### Evidências da inspeção ZIP

- Branch: `feat/validacao-zip`; base: `dev`, commit `6a02433`. Imagens locais não versionadas preservadas fora do diff.
- Serviço `inspecionar_zip(entrada, limites)` em `laboratorios/services/zip_validator.py`, independente de Django, recebe fluxo binário seekable e limites explícitos; retorna caminhos normalizados e bytes reais. Exceções `ArquivoInvalido` e `LimiteExcedido` são convertidas em erros seguros do formulário.
- Pré-inspeção de tamanho/EOCD/diretório central conta registros reais antes de `ZipFile` criar sua lista de entradas; recusa inconsistências e contagem falsificada. Depois valida nomes, tipos, flags, métodos, diretórios e tamanhos declarados antes de descompactar qualquer entrada.
- Nenhuma extração ou escrita. Entradas são lidas em blocos limitados; Deflate usa `zlib.decompressobj` com máximo de saída por chamada e limites reais por entrada/total. Isso evita depender de leitura truncada pelo tamanho anunciado. CRC, EOF, tamanhos reais, cabeçalhos local/central e sobreposição são conferidos.
- Dados descartados após a inspeção, sem abrir arquivos internos como programas ou renderizá-los. ZIPs aninhados não são inspecionados recursivamente. A validação não é antivírus e não identifica o formato real de cada documento.
- Defaults mantidos: upload 10 MiB, 100 entradas incluindo diretórios, 50 MiB descompactados e 10 MiB por entrada. A view síncrona não garante limite rígido de CPU/tempo; limites HTTP, concorrência e timeout operacional permanecem nas entregas de infraestrutura.
- `.venv/bin/python manage.py check`: sem problemas; testes Django e pytest: 69 passaram em cada suíte; migrações: nenhuma mudança; `git diff --check`: sem problemas.
- Testes cobrem ZIP inválido/vazio, diretórios apenas, caminhos absolutos/Windows/UNC/travessia, caracteres de controle/NUL, duplicatas normalizadas, symlink/tipos especiais, metadados, criptografia, métodos recusados, múltiplos volumes e ZIP64. Também cobrem contagem falsa, tamanhos declarados/reais, limite acumulado, CRC, truncamento, cabeçalhos inconsistentes, sobreposição, data descriptor e arquivos válidos maiores que um bloco.
- Navegador local: exemplo válido retornou 200 com seis arquivos; ZIP de teste com `../fora.txt` retornou 400 com erro compreensível, mantendo Executar ativa. Mobile 390 × 844 sem rolagem horizontal da página no estado de erro. Capturas locais `/tmp/autolab-zip-validado.png`, `/tmp/autolab-zip-rejeitado.png` e `/tmp/autolab-zip-rejeitado-mobile.png`, não versionadas.
- Catálogo continua com automação em breve: esta entrega apenas inspeciona. Organização, relatório, saída, tokens, expiração e limpeza aguardam branches próprias. CI remoto da feature depende do push manual e da revisão.
- Atualização: inspeção integrada pelo PR #8 com dois checks aprovados; `dev` sincronizada em `5ffb3ff`. A pendência de envio acima é histórica.

### Evidências da organização de arquivos

- Branch: `feat/organizacao-arquivos`, iniciada sobre `feat/validacao-zip` em `5861e5a` enquanto aguardava envio manual. Após integração do PR #8, `dev` em `5ffb3ff` incorporada por merge sem conflitos. Destino do PR: `dev`; dependência encadeada resolvida.
- `laboratorios/services/arquivo_service.py`: contrato da seção 20.4, quatro categorias inclusive vazias, contagens, avisos de nomes alterados e inventário UTF-8. Sem dependência de Django, novas bibliotecas, modelos ou caminhos de entrada usados como destinos no sistema de arquivos.
- `zip_validator.py`: normalização de caminhos reutilizável e cópia limitada para destino controlado; inspeção existente continua sem escrita. Resultado permanece em subdiretório privado gerado pelo servidor; cópia interrompida elimina a saída parcial sem alterar entrada ou execuções anteriores.
- `.venv/bin/python manage.py check`: sem problemas; testes Django e pytest: 83 passaram em cada suíte; `makemigrations --check --dry-run`: nenhuma mudança; `git diff --check`: sem problemas.
- Quatorze novos testes cobrem exemplo completo, extensões maiúsculas/desconhecidas, categorias vazias, colisões com nomes gerados, Unicode, nomes especiais/longos, CSV com fórmulas e aspas, ordem determinística, relatório de entrada, travessia, limites, falha após escrita parcial, execuções paralelas e conteúdo Stored/Deflate maior que um bloco.
- Demonstração executada em Python sem inicializar Django: exemplo produziu seis arquivos, Documentos=3, Planilhas=1, Imagens=1, Outros=1; segundo comunicado virou `comunicado_2.txt`. Integridade do ZIP e inventário conferidos. Artefato local `/tmp/autolab-arquivos-organizados-demo.zip`, fora do Git.
- A view ainda apenas inspeciona o upload; catálogo mantém automação em breve. Resumo web, persistência de token, download, expiração e limpeza permanecem nas entregas seguintes. Nenhuma alteração visual nesta branch; testes de capacidade da oficina continuam pendentes.
- CI remoto desta branch aguarda push manual e abertura do PR. Testes locais não comprovam execução remota.
- Atualização: serviço integrado pelo PR #9 com dois checks aprovados; base sincronizada em `5779eb3`. A pendência de envio acima é histórica.

### Evidências do download de resultados

- Branch: `feat/download-resultado`; base: `dev`, commit `5779eb3`. Objetivo: integrar serviço, resumo e acesso temporário ao ZIP. PR previsto para `dev`; nenhuma dependência pendente de outra feature.
- `ResultadoTemporario` e migração `0001_initial` adicionados. Modelo não registra conteúdo nem nome do upload; guarda token, caminho e resumo mínimo. Aplicar `python manage.py migrate` antes de iniciar a aplicação.
- Coordenação em `services/resultados.py`: diretório UUID privado, upload temporário e saída com nome fixo. Caminho de entrada nunca vem de parâmetro do cliente. A saída é persistida somente após organização completa; falhas descartam a área desta execução.
- Rotas existentes preservadas; inclusão de resultados sob `/resultados/` no mesmo namespace `laboratorios`. Não foi criada API REST nem nova arquitetura.
- `.venv/bin/python manage.py check`: sem problemas; testes Django e pytest: 98 passaram em cada suíte; `makemigrations --check --dry-run`: nenhuma mudança; `git diff --check`: sem problemas.
- Testes de integração cobrem exemplo, inventário, upload original descartado, redirecionamento, atualização sem reprocessar, TTL configurável e fronteira exata, token desconhecido, arquivos ausentes, caminhos adulterados, links simbólicos, parâmetros ignorados, métodos HTTP, isolamento entre clientes, falhas de serviço/banco, escape de avisos e tipos de resultado incompatíveis. Testes antigos foram atualizados para o novo contrato. Ao consumir FileResponse integralmente no cliente Django, o iterador já fecha a resposta; retirado fechamento duplicado dos testes do exemplo público para compatibilidade com isolamento de banco do pytest.
- Navegador local com banco e resultados isolados em `/tmp`: envio do ZIP fictício retornou 303, resumo mostrou seis arquivos e contagens 3/1/1/1; botão baixou ZIP íntegro, byte a byte igual ao gerado. Resultado expirado retornou página 410 sem link de download. Migração aplicada com sucesso nesse banco de demonstração, sem modificar o banco local do responsável.
- Resumo conferido em desktop e mobile 390 × 844, sem rolagem horizontal no exemplo. Capturas locais `/tmp/autolab-download-desktop.png`, `/tmp/autolab-download-mobile.png` e `/tmp/autolab-download-expirado.png`, fora do Git. Verificação pontual; não constitui auditoria completa de acessibilidade.
- Limpeza e agendamento não implementados nesta branch. A UI informa que expiração de acesso não é exclusão imediata. Catálogo continua em breve até concluir o ciclo de vida. CI remoto aguarda push manual.

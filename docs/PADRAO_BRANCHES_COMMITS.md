# AutoLab — Política de Branches, Commits e Pull Requests

**Versão:** 1.1  
**Data:** 14/10/2026  
**Aplicação:** repositório do AutoLab (Django, Bootstrap 5, Python, Codespaces).  
**Status:** padrão de trabalho a ser seguido por pessoas e agentes de IA.

## 1. Objetivo e princípios obrigatórios

1. Toda funcionalidade deve ser dividida em **branches pequenas, independentes e revisáveis**, cada uma responsável por uma entrega coerente.
2. O nome de **toda branch de funcionalidade** deve seguir `feat/<funcionalidade>` (letras minúsculas, palavras em `kebab-case`, sem espaços, acentos ou caracteres especiais). Exemplos: `feat/layout-base`, `feat/upload-arquivos`, `feat/validacao-zip`.
3. **Cada mudança significativa deve gerar seu próprio commit**, com mensagem clara e escopo restrito. Não agrupar alterações sem relação em um mesmo commit.
4. Uma branch corresponde a uma **unidade pequena de entrega**, não necessariamente a uma funcionalidade completa de negócio. Uma funcionalidade maior deve ser decomposta em várias branches `feat/*`.
5. Nenhum desenvolvimento deve ser feito diretamente em `main` ou `dev`.
6. Antes de iniciar cada branch, definir objetivo, base, dependências, arquivos afetados e critérios de aceite.
7. Mudanças de escopo exigem uma nova branch ou revisão explícita do planejamento, não expansão silenciosa do PR.
8. Não incluir credenciais, `.env`, bancos SQLite locais, arquivos de usuários ou artefatos temporários nos commits.

## 2. Branches permanentes e fluxo de integração

- `main`: código estável e apto a publicação. Protegida, sem push direto.
- `dev`: integração das funcionalidades concluídas e aprovadas. Protegida, sem push direto.
- `feat/<funcionalidade>`: branches temporárias, abertas para cada entrega específica.

**Fluxo padrão:** `dev` → `feat/<entrega>` → Pull Request para `dev` → testes/revisão → merge → exclusão da branch de feature. Quando a versão estiver validada, abrir Pull Request de `dev` para `main`.

**Regra de dependências:** preferir que todas as branches saiam da versão atualizada de `dev`. Se a entrega B depender de código ainda não incorporado da entrega A, preferir integrar A primeiro. Quando não for possível, é permitido criar B a partir de A, registrando essa dependência no PR, e abrir PR de B para A (stacked PR). Depois de A entrar em `dev`, atualizar B e trocar sua base para `dev` antes do merge. Não enviar B diretamente para `dev` enquanto depender de alterações não integradas sem explicitar e revisar essa dependência.

**Branches de correção:** por padrão, utilizar também `feat/<entrega>` quando a correção fizer parte de uma funcionalidade em desenvolvimento. Para incidentes de produção, o fluxo de hotfix deve ser combinado separadamente; não fazer correções diretamente em `main`.

## 3. Como dividir funcionalidades em branches

Dividir por **entregas verificáveis** e não simplesmente por arquivo ou camada. Cada branch deve poder ser entendida e revisada isoladamente.

Exemplo — funcionalidade maior: **Laboratório de Arquivos**

| Ordem | Branch | Entrega | Dependência |
|---|---|---|---|
| 1 | `feat/laboratorio-arquivos-pagina` | Página Django, rota e instruções do laboratório | `dev` |
| 2 | `feat/upload-arquivos` | Formulário e validação inicial do upload | Página integrada em `dev` |
| 3 | `feat/validacao-zip` | Inspeção segura de ZIP, limites e erros | Upload integrado em `dev` |
| 4 | `feat/organizacao-arquivos` | Serviço Python que organiza arquivos por extensão | Validação ZIP integrada em `dev` |
| 5 | `feat/download-resultado` | Geração e download do ZIP de saída | Organização integrada em `dev` |
| 6 | `feat/exercicio-organizacao` | Exercício, arquivos fictícios e instruções | Fluxo de organização integrado em `dev` |
| 7 | `feat/codespaces-arquivos` | Ambiente e scripts do exercício no Codespaces | Exercício integrado em `dev` |

Exemplo — funcionalidade maior: **Laboratório de Planilhas**

- `feat/laboratorio-planilhas-pagina`
- `feat/upload-planilhas`
- `feat/leitura-csv-xlsx`
- `feat/limpeza-dados`
- `feat/exportacao-planilhas`
- `feat/exercicio-planilhas`

Exemplo — **Estrutura inicial do AutoLab**

- `feat/configuracao-django`: projeto Django, apps essenciais, settings básicos.
- `feat/layout-base`: template base, Bootstrap 5, cabeçalho e menu.
- `feat/dashboard-inicial`: página inicial e catálogo resumido.
- `feat/catalogo-laboratorios`: listagem de laboratórios e estados de disponibilidade.

**Critério de corte:** se uma branch acumular múltiplas entregas independentes, dividir antes de iniciar ou antes de abrir PR. Não criar microbranches para mudanças triviais inseparáveis de uma mesma entrega (ex.: HTML e CSS do mesmo componente).

## 4. Convenção de commits

Utilizar o formato **Conventional Commits**:

```text
<tipo>(<escopo>): <descrição curta no imperativo>
```

Tipos permitidos:

| Tipo | Uso |
|---|---|
| `feat` | Nova capacidade ou comportamento |
| `fix` | Correção de defeito |
| `refactor` | Reorganização interna sem alterar comportamento |
| `test` | Inclusão ou melhoria de testes |
| `docs` | Documentação |
| `style` | Formatação e estilo sem mudança de comportamento |
| `chore` | Manutenção e configuração |
| `build` | Dependências, build e empacotamento |
| `ci` | Integração contínua |
| `perf` | Melhoria de desempenho |

**Regras:**

- Escrever descrições em português, consistentes em todo o repositório.
- Usar verbo no imperativo: `adiciona`, `implementa`, `valida`, `corrige`, `documenta` (forma adotada pela equipe, apesar de gramaticalmente ser presente do indicativo).
- Preferir linha de assunto de até 72 caracteres.
- Indicar o escopo sempre que possível: `arquivos`, `planilhas`, `core`, `ui`, `codespaces`, `docs`.
- Um commit deve representar uma mudança lógica autocontida, idealmente com testes associados quando aplicáveis.
- Commits não devem conter `WIP`, `ajustes`, `mudanças`, `fix`, `update` ou `final` como única descrição.
- Não usar `git add .` sem revisar o que será incluído; preferir `git add <caminhos>` ou `git add -p`.

**Exemplo de histórico de uma única branch `feat/upload-arquivos`:**

```text
feat(arquivos): cria formulario de upload de arquivos ZIP
feat(arquivos): implementa view de recebimento de arquivos
fix(arquivos): rejeita extensoes nao permitidas
 test(arquivos): cobre uploads validos e invalidos
 docs(arquivos): documenta limites e formatos aceitos
```

*Nota:* espaços iniciais no exemplo acima são apenas de apresentação; mensagens reais não devem começar com espaços.

**Exemplo de separação correta:** criar formulário, implementar view, validar entrada, adicionar testes e documentar podem ser commits distintos se forem mudanças significativas. Se uma mudança não puder funcionar sem outra, os commits ainda devem manter uma sequência compreensível e o PR final deve passar nos testes.

## 5. Procedimento obrigatório para abrir uma branch

1. Confirmar que a árvore de trabalho está limpa: `git status`.
2. Atualizar a base:

```bash
git fetch origin
git switch dev
git pull --ff-only origin dev
```

3. Criar a branch com nome descritivo:

```bash
git switch -c feat/upload-arquivos
```

4. Desenvolver uma alteração lógica por vez.
5. Revisar mudanças antes de cada commit:

```bash
git status
git diff
git add -p
git diff --cached
git commit -m "feat(arquivos): cria formulario de upload de arquivos ZIP"
```

6. Executar os testes pertinentes e checagens do Django:

```bash
python manage.py check
python manage.py test
```

7. Enviar a branch:

```bash
git push -u origin feat/upload-arquivos
```

8. Abrir Pull Request para `dev` e solicitar revisão. Não fazer merge antes de satisfazer os critérios de aceite.
9. Após o merge, excluir a branch remota e local quando não for mais necessária.

## 6. Política de Pull Requests

**Título:** `<tipo>(<escopo>): <resultado da entrega>`.

**Descrição obrigatória:**

```markdown
## Objetivo
Qual entrega esta branch implementa?

## Contexto e dependências
Issue relacionada, branch base e pré-requisitos.

## Alterações realizadas
- Mudança 1
- Mudança 2

## Como testar
1. Comando ou passo inicial
2. Cenário principal
3. Cenário de erro

## Critérios de aceite
- [ ] Funcionalidade implementada
- [ ] Testes relevantes adicionados ou justificativa
- [ ] `python manage.py check` executado
- [ ] Sem segredos ou arquivos temporários
- [ ] Documentação atualizada quando necessário

## Evidências
Capturas de tela, logs ou exemplos (sem dados sensíveis).
```

**Merge:** preferir **merge commit** ou **rebase merge** quando for importante preservar os commits bem definidos da branch. Evitar **squash merge** como padrão, pois ele apaga a separação dos commits no histórico de `dev`. O método de merge deve ser consistente no repositório. Proteger `main` e `dev` com PR obrigatório, revisão e verificações automáticas, quando disponíveis.

## 7. Regras para agentes de IA

Antes de codificar, o agente deve:

1. Ler `PLANEJAMENTO_AUTOLAB.md` e este documento.
2. Verificar a branch atual, o estado do repositório e o histórico recente.
3. Apresentar a decomposição da funcionalidade em branches `feat/*`, com ordem e dependências.
4. Solicitar confirmação da próxima branch quando o usuário estiver conduzindo a implementação passo a passo.
5. Não criar branches adicionais, fazer merge, rebase ou push sem autorização apropriada para essas ações.
6. Implementar somente o escopo da branch ativa.
7. Separar commits por mudança significativa; nunca fazer um commit único de toda a funcionalidade grande.
8. Informar arquivos alterados, comandos de teste, resultados, commits realizados e pendências.
9. Atualizar a documentação do AutoLab sempre que decisões de arquitetura ou comportamento mudarem.
10. Nunca alegar que testes foram executados ou commits enviados sem execução comprovada.

**Formato sugerido para proposta de branch:**

```markdown
Funcionalidade: [nome]
Branch: feat/[entrega]
Base: dev
Objetivo: [resultado verificável]
Dependências: [nenhuma ou branches/PRs anteriores]
Escopo incluído: [itens]
Fora do escopo: [itens]
Commits previstos:
1. feat(escopo): ...
2. test(escopo): ...
3. docs(escopo): ...
Critérios de aceite: [itens verificáveis]
```

## 8. Situações especiais e segurança do histórico

- **Correção antes do merge:** adicionar um novo commit `fix(...)` na mesma branch quando a correção pertencer à entrega.
- **Mudança sem relação:** abrir outra `feat/*` baseada em `dev` atualizado.
- **Conflito:** entender as alterações de ambos os lados, resolver conscientemente e testar novamente; nunca aceitar automaticamente tudo de um lado.
- **Branch desatualizada:** atualizar com `dev` após `git fetch`; escolher merge ou rebase conforme política do time. Não reescrever histórico compartilhado sem coordenação.
- **Rebase em andamento:** resolver conflitos e continuar com `git rebase --continue`, ou abortar com `git rebase --abort` quando necessário. Não criar novos commits normais no meio do rebase.
- **Push rejeitado:** verificar divergência com `git fetch` e `git log --graph --oneline --decorate --all`; não usar `git push --force` como solução automática.
- **Force push:** proibido em `main` e `dev`. Em branch própria, somente após avaliação explícita; se indispensável, usar `--force-with-lease` e comunicar colaboradores.
- **Migrations Django:** incluir migrações correspondentes às mudanças de modelos e verificar consistência; evitar misturar migrações de funcionalidades independentes.
- **Segredos:** usar variáveis de ambiente e `.gitignore`; caso um segredo seja exposto, revogá-lo/rotacioná-lo, não apenas apagá-lo em um commit posterior.

## 9. Exemplo de ciclo completo

Funcionalidade: processamento de arquivos ZIP.

```text
dev
 ├─ feat/laboratorio-arquivos-pagina ── PR #1 → dev
 ├─ feat/upload-arquivos ────────────── PR #2 → dev
 ├─ feat/validacao-zip ──────────────── PR #3 → dev
 ├─ feat/organizacao-arquivos ───────── PR #4 → dev
 └─ feat/download-resultado ─────────── PR #5 → dev

(dev validada) ── PR de release → main
```

Cada linha representa uma branch criada a partir da `dev` atualizada **depois da integração da dependência anterior**, não cinco branches necessariamente simultâneas.

## 10. Checklist antes de finalizar uma entrega

- [ ] Branch segue `feat/<funcionalidade>`.
- [ ] Branch possui escopo pequeno, coeso e critérios de aceite claros.
- [ ] Commits possuem mensagens específicas e representam mudanças significativas separadas.
- [ ] Código e testes pertinentes foram revisados.
- [ ] `python manage.py check` passou.
- [ ] `python manage.py test` passou ou limitações foram registradas.
- [ ] Migrações e documentação foram atualizadas quando necessário.
- [ ] Nenhum segredo, banco local ou arquivo temporário foi incluído.
- [ ] PR aponta para a base correta (`dev`, salvo stacked PR explícito).
- [ ] Dependências e evidências foram documentadas.
- [ ] Merge ocorreu somente após revisão e validação.

## 11. Regras adicionais de granularidade e dependências

### 11.1 Quando abrir uma nova branch

Abrir uma nova `feat/<entrega>` quando a mudança representar uma responsabilidade funcional separada, puder ser descrita por critérios de aceite próprios ou puder ser revisada independentemente. Não criar uma branch para cada arquivo ou linha alterada. Uma branch pode incluir view, formulário, template e testes quando todos forem necessários para **a mesma entrega**.

Exemplo para o laboratório de arquivos (sequência sugerida, não branches simultâneas obrigatórias):

1. `feat/laboratorio-arquivos-pagina`: exibir página e instruções.
2. `feat/upload-arquivos`: receber arquivos com formulário e view.
3. `feat/validacao-zip`: verificar tipo, tamanho, limites e caminhos.
4. `feat/organizacao-arquivos`: processar arquivos e gerar resultado.
5. `feat/download-resultado`: entregar ZIP gerado ao usuário.
6. `feat/exercicio-organizacao`: publicar enunciado e material didático.

**Pré-requisito:** cada branch parte de `dev` atualizada, após integração das dependências. Se for indispensável desenvolver em paralelo sobre outra feature, registrar explicitamente branch-base, PR-base, ordem de integração e procedimento de atualização da base.

### 11.2 Critérios para um commit atômico

Um commit deve conter **uma mudança lógica coerente** e deixar o projeto em estado compreensível. Criar commits distintos para implementação, correção de defeito, refatoração independente, testes adicionais ou documentação substancial quando forem mudanças separáveis. Não é necessário um commit por arquivo.

Exemplo de histórico em `feat/upload-arquivos`:

```text
feat(arquivos): adiciona formulario de upload
feat(arquivos): implementa recebimento de arquivos ZIP
feat(arquivos): valida tamanho e extensao do upload
test(arquivos): cobre uploads invalidos
docs(arquivos): documenta regras de envio
```

Evitar mensagens como `update`, `fix`, `ajustes`, `mudancas` e `commit final`. Não adicionar ao stage todos os arquivos indiscriminadamente; preferir `git add <arquivos>` ou `git add -p`, revisando `git diff --cached` antes do commit.

## 12. Proteção de branches e política de merge

- Proteger `main` e `dev` nas configurações do GitHub: exigir PR, bloquear push direto e force push; exigir checks automáticos quando estiverem configurados.
- **Padrão preferencial:** *rebase and merge* para preservar commits atômicos em histórico linear, desde que a equipe tenha revisado o histórico e compreenda o comportamento do GitHub.
- **Squash and merge:** exceção justificada para limpar histórico de commits intermediários sem valor individual; não utilizar como padrão se a intenção é preservar cada mudança significativa.
- **Merge commit:** permitido quando a equipe decidir manter a topologia da integração; registrar essa decisão no PR.
- Nenhum agente de IA deve efetuar merge, rebase destrutivo, exclusão remota ou push forçado sem autorização explícita.
- Após merge em `dev`, excluir a branch temporária apenas quando não houver trabalho pendente e a integração tiver sido confirmada.
- A promoção de `dev` para `main` deve ocorrer por PR próprio, após validação da versão.

## 13. Modelo de Pull Request obrigatório

Salvar este modelo em `.github/pull_request_template.md` quando o repositório for criado:

```markdown
## Objetivo
Descreva a entrega específica desta branch.

## Issue relacionada
Closes #XX

## Branch-base e dependências
- Base: dev
- Dependências: nenhuma / PR #XX

## Alterações realizadas
- [ ] Mudança funcional 1
- [ ] Mudança funcional 2

## Como testar
1. Comando ou ação para reproduzir.
2. Resultado esperado.

## Verificações
- [ ] Commits atômicos e mensagens claras
- [ ] Testes automatizados executados (ou justificativa)
- [ ] Verificação manual quando aplicável
- [ ] Documentação e migrações atualizadas quando necessário
- [ ] Sem segredos, `.env` ou arquivos gerados
- [ ] Critérios de aceite atendidos

## Evidências e pendências
Capturas, logs não sensíveis, limitações e próximos passos.
```

## 14. Procedimento obrigatório para agentes de IA

Antes de modificar código:

1. Ler `PLANEJAMENTO_AUTOLAB.md` e este documento.
2. Executar `git status`, identificar branch atual e alterações locais existentes.
3. Verificar `git fetch origin` e a base apropriada sem sobrescrever trabalho não commitado.
4. Identificar issue, objetivo, dependências, critérios de aceite e nome `feat/<entrega>`.
5. Informar o plano de mudanças e confirmar ações destrutivas ou integrações quando necessárias.

Durante a implementação:

1. Manter o escopo da branch; demandas independentes exigem outra branch.
2. Fazer commits após unidades lógicas concluídas e revisar o conteúdo staged.
3. Executar testes relevantes; para Django, considerar `python manage.py check`, `python manage.py test` e `python manage.py makemigrations --check --dry-run` quando pertinente.
4. Não afirmar que comandos ou testes foram executados se não foram.
5. Não publicar credenciais, dados pessoais, `.env`, bancos locais ou arquivos temporários.

Ao concluir:

1. Mostrar branch, base, lista de commits e resumo dos arquivos alterados.
2. Informar testes executados, resultados, pendências e riscos.
3. Preparar o PR com o modelo padronizado.
4. **Não realizar merge nem push forçado sem autorização.**

## 15. Tamanho de branches, exceções e reversão

Não impor número fixo de arquivos, linhas ou commits por branch. Se uma entrega acumular responsabilidades independentes, dividir em novas branches com critérios de aceite próprios. Uma correção diretamente ligada à feature pode permanecer na mesma branch; correções não relacionadas devem ser isoladas.

Para desfazer alterações já integradas, preferir `git revert` por PR em vez de reescrever o histórico compartilhado. Antes de qualquer `reset --hard`, `rebase` com risco de perda ou exclusão de branch, verificar impactos e solicitar autorização. Em caso de conflito, resolver conscientemente e repetir os testes afetados.

---

**Relação com o planejamento:** este documento complementa `PLANEJAMENTO_AUTOLAB.md`. Em caso de conflito sobre Git, branches, commits e PRs, esta política é a referência específica; em caso de conflito de requisitos funcionais, prevalece o planejamento do AutoLab até decisão explícita em contrário.

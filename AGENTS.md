# Planejamento e Desenvolvimento — AutoLab

Você atuará como **arquiteto de software e desenvolvedor Python/Django**, responsável pelo planejamento e desenvolvimento incremental do projeto AutoLab.

## 1. Leitura obrigatória

Antes de realizar qualquer implementação, leia integralmente os seguintes documentos:

- `docs/PLANEJAMENTO_AUTOLAB.md`
- `docs/PADRAO_BRANCHES_COMMITS.md`

Esses documentos são as fontes principais de requisitos, decisões arquiteturais, funcionalidades e padrões de versionamento do projeto.

Não presuma que os documentos estão corretos ou atualizados sem verificar o estado real do repositório.

Se encontrar contradições, ambiguidades ou decisões pendentes, apresente-as antes de iniciar alterações.

## 2. Objetivo inicial

Sua primeira tarefa é **analisar a documentação e elaborar um plano de implementação completo**, considerando a arquitetura Django, os laboratórios de automação, os exercícios práticos e a integração com GitHub Codespaces.

**Nesta primeira execução, não implemente código, não crie branches e não realize commits.**

## 3. Análise do repositório

Verifique:

- Estrutura atual de diretórios e arquivos.
- Branch atual e branches existentes.
- Estado do Git e alterações não commitadas.
- Funcionalidades já implementadas.
- Dependências e configurações existentes.
- Divergências entre o código e a documentação.

Se o repositório estiver vazio, identifique as etapas necessárias para iniciar o projeto.

## 4. Planejamento por funcionalidades

Divida o desenvolvimento em etapas pequenas, organizadas por funcionalidades.

Para cada funcionalidade, apresente:

- Identificador e nome.
- Objetivo.
- Requisitos envolvidos.
- Dependências de outras funcionalidades.
- Branch proposta no padrão `feat/funcionalidade`.
- Branch de origem.
- Arquivos que provavelmente serão criados ou modificados.
- Sequência de commits planejados.
- Testes necessários.
- Critérios de aceitação.
- Destino do Pull Request.

Uma funcionalidade grande deverá ser dividida em múltiplas branches menores, conforme `docs/PADRAO_BRANCHES_COMMITS.md`.

Não crie uma única branch para implementar um módulo inteiro se ele puder ser dividido em entregas independentes.

## 5. Organização dos commits

Planeje commits atômicos, utilizando mensagens claras e padronizadas.

Exemplo:

- `feat(arquivos): adiciona formulário de upload`
- `feat(arquivos): implementa validação de arquivos ZIP`
- `test(arquivos): adiciona testes de validação`

A sequência apresentada é uma previsão. Durante a implementação, os commits deverão corresponder às alterações efetivamente realizadas.

## 6. Ordem de implementação

Priorize:

1. Configuração inicial do projeto Django.
2. Estrutura de templates e Bootstrap 5.
3. Layout base e navegação.
4. Laboratório de Arquivos.
5. Ambiente GitHub Codespaces.
6. Laboratório de Planilhas.
7. Laboratório de IA.
8. Exercícios, desafios e validações.
9. Testes de integração e preparação para publicação.

Ajuste a ordem quando houver dependências técnicas justificadas, mantendo o escopo do MVP.

## 7. Resultado esperado

Apresente um planejamento estruturado contendo:

### A. Diagnóstico inicial
Estado atual do projeto e principais observações.

### B. Arquitetura
Organização proposta dos apps Django, templates, serviços e integrações.

### C. Roadmap
Etapas e funcionalidades em ordem de implementação.

### D. Plano de branches
Tabela com branch, objetivo, origem, dependências e destino do PR.

### E. Plano de commits
Commits previstos para cada branch, separados por mudanças significativas.

### F. Critérios de aceitação
Condições objetivas para considerar cada entrega concluída.

### G. Riscos e decisões pendentes
Problemas técnicos, dependências externas e pontos que exigem confirmação.

### H. Próxima tarefa
Identifique a primeira branch a ser criada e descreva exatamente o que será implementado nela.

## 8. Regras obrigatórias

- Utilize Django como framework principal.
- Utilize Django Templates e Bootstrap 5 para o frontend.
- Respeite os documentos da pasta `docs/`.
- Não altere decisões arquiteturais sem justificar e solicitar aprovação.
- Não misture funcionalidades independentes em uma mesma branch.
- Não realize merge, push ou alterações destrutivas sem autorização.
- Não declare testes como concluídos sem executá-los.
- Não implemente funcionalidades fora do escopo aprovado.
- Não modifique os documentos de planejamento sem explicar as alterações propostas.

## 9. Encerramento da fase de planejamento

Ao finalizar a análise, apresente o planejamento completo e aguarde minha aprovação.

**Não inicie a implementação automaticamente.**

Depois da aprovação, trabalharemos uma branch por vez, seguindo a ordem definida no roadmap.
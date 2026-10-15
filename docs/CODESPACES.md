# Ambiente Python no GitHub Codespaces

## Estado e requisitos

A configuração fica em `.devcontainer/`: Python 3.12, ambiente virtual do
projeto, dependências fixadas, migrações e extensões Python/Pylance. README e
starter do exercício de Arquivos são abertos automaticamente no editor web.
A validação no Codespaces hospedado ainda precisa ser concluída; testes locais
e de contêiner não comprovam conta, cota ou conectividade dos participantes.

É necessária uma conta GitHub com acesso ao repositório e cota para Codespaces.
Revise as condições mostradas pelo GitHub antes de criar o ambiente; não é
necessário informar credenciais no AutoLab. A demonstração do site funciona
independentemente do Codespaces.

## Abrir o ambiente

Após a integração da configuração em `dev`, use:

[Preparar Codespace do AutoLab em dev](https://codespaces.new/heloabrantessb/autolab/tree/dev)

O link escolhe `dev` porque `main` ainda não recebeu o desenvolvimento. Confira
a branch na tela de criação e só então confirme a criação no GitHub. Para
validar um PR antes de integrá-lo, selecione sua branch de feature na mesma
tela. Criar um ambiente ou reconstruir um existente exige que os arquivos
tenham sido enviados ao GitHub.

O link leva à criação, não abre automaticamente a pasta do exercício em um
Codespace existente. A configuração `openFiles` prepara README e starter em um
ambiente novo. Se reutilizar um Codespace antigo, confira sua branch e faça
rebuild do contêiner quando a configuração tiver mudado.

## Preparação automática

`postCreateCommand` executa `bash .devcontainer/setup.sh` na raiz do repositório:

1. Cria ou atualiza `.venv` com o Python do contêiner.
2. Instala `requirements.txt` e verifica as dependências.
3. Copia `.env.example` para `.env` somente se ele ainda não existir.
4. Prepara a área local de resultados, aplica migrações e executa `manage.py check`.

O setup não sobrescreve `.env`, não limpa o banco, não executa os TODOs do
participante e não inicia servidor ou agendador. Se falhar por rede, confira
os logs e repita `bash .devcontainer/setup.sh` na raiz do projeto. Não use esse
script em produção nem com uma `.venv` de outro sistema que precise preservar.

## Resolver o exercício

No terminal iniciado na raiz do repositório:

```bash
python --version
cd codespaces_exercises/arquivos
python tests/verificar.py
python starter.py --saida resultado.zip
```

As falhas iniciais de `NotImplementedError` são esperadas. Complete os três
TODOs conforme o README aberto no editor. Ao terminar, os seis critérios devem
passar e a saída deve conter os seis arquivos fictícios e o inventário. Use um
nome novo em `--saida` para não sobrescrever uma saída existente.

O código é executado no ambiente pessoal do participante, nunca no servidor
Django. A referência do instrutor está fora do percurso principal e do pacote
baixável. Para conferi-la no clone completo, execute a partir da pasta do
exercício `python tests/verificar.py --referencia`.

## Prévia opcional do site

Volte à raiz do repositório e execute:

```bash
bash .devcontainer/start-site.sh
```

O servidor de desenvolvimento escuta na porta 8000 do contêiner. Abra a aba
Ports e mantenha a visibilidade **Private** antes de abrir a prévia. A
configuração encaminha somente essa porta e não altera sua visibilidade.

No Codespaces, o script usa `CODESPACE_NAME` e
`GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN` para configurar somente o host
encaminhado e sua origem HTTPS para CSRF. Esses valores substituem hosts e
origens no processo da prévia, sem editar `.env`. Fora do Codespaces, os valores
explícitos de ambiente/configuração local são preservados. IA fica desativada.
O bind é `0.0.0.0:8000` dentro do Codespaces, para o encaminhamento, e
`127.0.0.1:8000` fora dele.

Envie `materials/arquivos/exemplo.zip` na aba Executar e confira as contagens
3/1/1/1 e o download. Para testar limpeza no ambiente de desenvolvimento, use
`python manage.py limpar_resultados --dry-run` na raiz. Não configure cron
dentro do processo web; o agendamento operacional tem instruções próprias em
[operação dos resultados](OPERACAO_RESULTADOS.md).

## Checklist de validação hospedada antes da oficina

- Criar um Codespace novo na branch correta e aguardar o setup concluir.
- Conferir Python 3.12, `.venv` selecionada e os dois arquivos abertos.
- Rodar os critérios com a referência; os seis devem passar.
- Abrir o starter e confirmar a falha esperada dos TODOs, sem alterar a referência.
- Iniciar o site, conferir porta privada e enviar o exemplo com sucesso.
- Baixar o ZIP organizado e conferir inventário e comunicados distintos.
- Repetir com outra conta participante para conferir permissões, cota e tempo de início.
- Salvar alterações em uma branch própria ou baixar os arquivos antes de descartar o ambiente.
- Parar o Codespace pelo GitHub ao terminar e revisar ambientes sem uso conforme a conta.

Essa verificação depende de ações do responsável no GitHub. Não considerar a
configuração validada para a oficina apenas porque os testes locais passaram.

## Evidências locais desta entrega

CLI oficial Dev Containers 0.89.0 leu a configuração e criou o ambiente em uma
cópia temporária do projeto, sem `.env`, banco, `.venv` ou credenciais do
workspace original. Imagem fixada por digest, usuário `vscode` e Python 3.12.15.
O setup instalou as dependências fixadas, aplicou migrações e passou no check.

Nesse contêiner, 127 testes Django e 127 testes pytest passaram; os seis
critérios do exercício também passaram com a referência. A prévia iniciada pelo
script real foi testada com host/origem de Codespaces simulados: formulário,
CSRF, resumo e download íntegro funcionaram. Repetir o setup preservou `.env`
personalizado e registros do banco. O contêiner de teste foi removido ao final.

Isso não valida criação no GitHub, instalação das extensões no editor web,
arquivos abertos automaticamente, túnel privado ou acesso por outra conta.
Esses itens continuam no checklist de validação hospedada.

## Alternativa sem Codespaces

No site, abra Exercícios e baixe o pacote de Arquivos. Descompacte em uma pasta
nova e siga seu README usando Python 3.12+ local, sem instalar Django ou outras
bibliotecas. O pacote inclui o ZIP fictício e os testes; não exige conta GitHub.

## Manutenção e fontes

A imagem oficial Python Bookworm está fixada por digest no Dockerfile.
Atualizações exigem obter uma nova imagem, conferir o digest e repetir setup,
testes e prévia; alterar somente uma tag sem testar não atualiza o digest.
Dependências Python continuam fixadas em `requirements.txt`.

Fontes oficiais consultadas para a configuração:

- [Configuração Python do Codespaces](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/setting-up-your-python-project-for-codespaces).
- [Links com branch predefinida](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/setting-up-your-repository/facilitating-quick-creation-and-resumption-of-codespaces).
- [Arquivos abertos automaticamente](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/configuring-dev-containers/automatically-opening-files-in-the-codespaces-for-a-repository).
- [Variáveis do Codespaces](https://docs.github.com/en/codespaces/developing-in-a-codespace/default-environment-variables-for-your-codespace).
- [Encaminhamento de portas](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace).
- [Especificação Dev Containers](https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainerjson-reference.md).

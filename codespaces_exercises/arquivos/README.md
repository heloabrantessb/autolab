# Exercício — organizar arquivos com Python

Objetivo: classificar seis arquivos fictícios, resolver nomes repetidos e gerar
um inventário. Nível iniciante; pré-requisitos: funções, conjuntos, laços e
noções de caminhos/extensões. Reserve cerca de 25 minutos (estimativa).

## Preparação

Use Python 3.12 ou superior. Não são necessários Django, pip ou acesso à rede.
No repositório completo, abra um terminal e entre nesta pasta:

```bash
cd codespaces_exercises/arquivos
```

Se você baixou o pacote do exercício pelo site, descompacte-o em uma pasta
nova e abra o terminal nessa pasta. O pacote já inclui `exemplo.zip`. No
repositório completo, o apoio encontra o mesmo arquivo em `materials/arquivos`.
A configuração do Codespaces está preparada no repositório; a validação no
serviço hospedado ainda está pendente. Após sua integração em `dev`, use
[Preparar Codespace](https://codespaces.new/heloabrantessb/autolab/tree/dev),
com conta GitHub e cota disponível. Confira a branch antes de criar o ambiente.
Também é possível executar os comandos em uma instalação local de Python.

## Problema e entrada

Uma equipe recebeu documentos misturados em um ZIP. O exemplo tem três TXT,
um CSV, um PNG e um arquivo sem extensão. Os dois `comunicado.txt` têm conteúdos
diferentes e devem ser preservados. Todos os dados são fictícios.

O apoio aceita **somente o ZIP original fornecido**, conferindo sua assinatura
SHA-256 antes de abri-lo, sem extrair arquivos no sistema. Ele não substitui
a validação do site nem deve ser usado para processar ZIPs arbitrários.

## Passo a passo

1. Abra `starter.py` e leia os contratos das três funções com TODO.
2. Complete `categoria(nome)`: obtenha a extensão com `pathlib.Path`, converta
   para minúsculas e retorne uma das categorias abaixo.
3. Complete `nome_unico(nome, usados)`: tente o nome original; se o seu
   `casefold()` estiver em `usados`, tente `_2`, `_3` etc. antes da extensão.
   Registre o `casefold()` do nome escolhido no conjunto e retorne o nome.
4. Complete `linha_inventario(original, saida, grupo)`: retorne uma tupla com
   esses três textos e o status. Use `renomeado` se o nome base mudou, ou
   `organizado` se permaneceu igual. Preserve o caminho original completo.
5. Rode os testes e ajuste sua solução. Você pode pedir à IA para explicar uma
   falha, mas confira o raciocínio e o conteúdo dos arquivos por conta própria.

| Categoria | Extensões |
|---|---|
| Documentos | `.pdf`, `.doc`, `.docx`, `.txt` |
| Planilhas | `.csv`, `.xls`, `.xlsx` |
| Imagens | `.png`, `.jpg`, `.jpeg` |
| Outros | demais extensões e arquivos sem extensão |

Classificar por extensão não comprova o formato real do conteúdo.

## Verificar e executar

```bash
python tests/verificar.py
python starter.py --saida resultado.zip
```

Inicialmente os testes falham com `NotImplementedError`, pois os TODOs ainda
não foram resolvidos. Isso é esperado: a verificação avalia o seu arquivo
local, não envia código ao site e não atribui progresso persistente.
Com as três funções prontas, os seis testes devem passar e o segundo comando
deve mostrar total 6 e contagens 3/1/1/1.

O script recusa sobrescrever um arquivo existente. Para repetir, escolha outro
nome, como `--saida resultado-2.zip`. Ele também recusa modificar o ZIP de
entrada. O apoio gera o ZIP e o CSV; sua responsabilidade são as três regras
de negócio. Leia o apoio depois de concluir, para entender o fluxo completo.

## Saída e critérios de conclusão

```text
resultado.zip
├── Documentos/comunicado.txt
├── Documentos/comunicado_2.txt
├── Documentos/notas.txt
├── Planilhas/clientes.csv
├── Imagens/marca.png
├── Outros/LEIA-ME
└── relatorio.csv
```

O ZIP também inclui os quatro diretórios de categoria. O inventário UTF-8 tem
as colunas `caminho_original,nome_saida,categoria,status` e seis linhas de dados;
o próprio relatório não conta como arquivo de entrada. O segundo comunicado
deve ter status `renomeado` e conteúdo diferente do primeiro.

- Os seis testes locais passam.
- As contagens são Documentos=3, Planilhas=1, Imagens=1, Outros=1.
- Nenhum conteúdo é perdido por colisão de nomes.
- Os caminhos originais aparecem completos no CSV.
- O ZIP original e saídas existentes permanecem inalterados.

## Desafio e erros comuns

Explique por que `foto.JPG` deve ser imagem e `LEIA-ME` deve ir para Outros.
Teste `nome_unico` com `a.txt` e `a_2.txt` já usados e confirme que retorna
`a_3.txt`. Repita com letras maiúsculas e um nome sem extensão.

Se os comunicados desaparecerem, confira colisões e atualização do conjunto.
Se o relatório perder as subpastas, você usou somente o nome base na coluna
original. Se houver `ModuleNotFoundError`, execute os comandos a partir desta
pasta e confira se o pacote foi descompactado completo. Uma mensagem pedindo
o ZIP original indica material alterado: baixe o pacote novamente.

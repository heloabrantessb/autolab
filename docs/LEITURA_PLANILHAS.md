# Leitura de CSV/XLSX

Esta entrega lê uma tabela e mostra até dez linhas na aba Executar. Não limpa,
remove duplicatas, exporta ou guarda o envio para uma requisição futura. O
catálogo mantém a automação em breve até concluir o fluxo de limpeza/exportação.
Use somente dados fictícios.

## Perfil de entrada

- Um CSV UTF-8, com ou sem BOM, separado por vírgulas. Aspas delimitam campos
  com vírgulas ou quebras de linha. Outros separadores não são detectados.
- Ou um XLSX com exatamente uma aba de tabela, sem células mescladas, erros de
  célula, vínculos externos, macros, mídia ou componentes binários.
- Primeira linha como cabeçalho, com nomes preenchidos e únicos após comparar
  sem espaços nas pontas e sem distinguir maiúsculas. Os nomes originais são
  preservados; XLSX exige cabeçalho textual.
- Pelo menos uma linha de dados. CSV deve manter a largura do cabeçalho; uma
  linha física completamente vazia é preenchida com células vazias e preservada.
  No XLSX, lacunas entre registros são preservadas e dados além das colunas do
  cabeçalho são rejeitados.
- Limites configuráveis: `MAX_SPREADSHEET_UPLOAD_BYTES` (20 MiB),
  `MAX_SPREADSHEET_ROWS` (10.000 linhas de dados, sem contar cabeçalho),
  `MAX_SPREADSHEET_COLUMNS` (30 colunas).
- Limite adicional de 32.768 caracteres por célula. Cabeçalhos também são
  células. Caracteres de controle, exceto tabulação e quebras de linha, são
  rejeitados. Cabeçalho sem dados não é uma tabela válida neste perfil.

Identificadores como `001` devem estar armazenados como texto. O leitor não
reconstrói formatação visual do Excel: número `1` com máscara `000` é lido como
`1`. Datas/horas são convertidas para texto ISO; demais números e booleanos para
sua representação textual Python. Células vazias viram texto vazio. Fórmulas
simples são texto literal, sem cálculo; tipos especiais não representáveis
como texto escalar são recusados. A leitura não executa código ou macros.

## Serviço e proteção de recursos

`laboratorios/services/planilha_reader.py` não depende de Django. O contrato é
`ler_planilha(stream_binario, formato, limites) -> TabelaLida`. A tabela imutável
contém cabeçalho, linhas e formato; `previa` limita a visualização a dez linhas.
A entrada é rebobinada mesmo em falha. Não há extração ou escrita pelo serviço.

O leitor limita bytes reais antes de interpretar. CSV usa a biblioteca padrão
sem alterar a configuração global `csv.field_size_limit`. XLSX usa openpyxl
em modo somente leitura e com fechamento explícito. Antes da biblioteca:

1. Reutiliza a inspeção ZIP com limites reais/CRC: até 100 entradas, 50 MiB
   descompactados e 20 MiB por entrada, Stored/Deflate, sem ZIP64 ou criptografia.
2. Aceita apenas componentes XML/relacionamentos, sem binários; recusa tipos de
   macro e relacionamentos externos, inclusive partes que não seriam exibidas.
3. Faz pré-inspeção XML com defusedxml, proibindo DTD, entidades e referências
   externas. Limita profundidade a 128 e a um milhão de elementos por parte,
   removendo elementos processados para não acumular a árvore inteira.
4. Confere posições reais de linhas e células antes do carregamento, inclusive
   lacunas esparsas, coordenadas repetidas e limites de linhas/colunas. Ignora
   dimensões declaradas para que metadados falsos não ocultem ou ampliem dados.

O limite de bytes inclui metadados do XLSX. Esse perfil recusa algumas pastas de
trabalho válidas que tenham recursos adicionais; copie a tabela para um arquivo
simples compatível ou use o CSV fictício. Não é um validador geral de Excel.
Pandas permanece previsto para a próxima etapa de limpeza sobre os dados já
limitados; a arquitetura do planejamento não mudou.

Openpyxl e defusedxml foram fixados em `requirements.txt`. As orientações de
[segurança do openpyxl](https://openpyxl.readthedocs.io/en/stable/#security)
recomendam defusedxml; o [modo de leitura](https://openpyxl.readthedocs.io/en/stable/optimized.html)
exige fechamento do livro e atenção às dimensões declaradas. Os limites e a
pré-inspeção adicionais são decisões desta implementação.

## Prévia web

A resposta POST mantém Executar ativa, com HTTP 200 na leitura bem-sucedida e
400 para entrada inválida; preserva CSRF e bloqueio de cache. O template usa
escape padrão, sem `safe`, e não inclui o conjunto de dados em campos ocultos.
A prévia abrevia cabeçalhos em 80 caracteres e células em 200; dados completos
continuam no objeto de leitura durante a requisição. Espaços são visíveis com
`white-space: pre-wrap`; a tabela tem rolagem interna no celular.

O exemplo CSV mantém oito linhas de dados nesta fase. A tabela de cinco registros
na aba Resultado é uma referência didática para a futura limpeza. Uma linha sem
e-mail não é descartada. Entradas e resultados não são persistidos por este
fluxo; Django pode usar arquivos temporários durante o recebimento HTTP.

## Validação

Os testes cobrem os dados fictícios, Unicode/BOM, aspas e quebras de linha,
limites exatos e excedidos, cabeçalhos inválidos, XLSX corrompido, células
esparsas, dimensões falsas, XML ativo, macros, vínculos externos e erros de
célula. Testes web verificam escape HTML, abreviação, limites configurados,
prévia de dez linhas e ausência de acesso ao banco/escrita de resultados.

Execute `python manage.py test` e `python -m pytest -p no:cacheprovider`.
Limpeza, exportação e exercício de Planilhas serão entregues separadamente.

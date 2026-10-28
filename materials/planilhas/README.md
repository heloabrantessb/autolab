# CSV fictício — limpeza de planilhas

`clientes.csv` é um material público UTF-8, separado por vírgulas, sem BOM.
Tem cinco colunas e oito linhas de dados, além do cabeçalho. Nomes e registros
são inventados; os e-mails usam o domínio reservado `example.invalid`.
Para abrir em um editor de planilhas, importe como UTF-8 e trate `id` como texto
para preservar os zeros iniciais.

## Casos presentes

- Duas linhas idênticas de Ana, id `001`.
- Duas versões de Bruno, id `002`: uma tem espaços extras em nome/setor.
- Carla, id `003`, sem e-mail, com os demais dados preenchidos.
- Uma linha completamente vazia, representada por `,,,,`.
- Diego, id `004`, e Elisa, id `005`, com dados fictícios.

## Referência didática

Aplicando, nesta ordem, as três operações:

1. Aparar espaços nas pontas das células de texto.
2. Remover somente linhas completamente vazias.
3. Remover duplicatas completas, mantendo a primeira ocorrência.

Oito linhas passam a cinco: uma linha vazia e duas duplicatas são removidas.
Permanecem os ids `001`, `002`, `003`, `004` e `005`, nessa ordem. Carla continua
sem e-mail; nenhum registro parcialmente preenchido é removido por esse motivo.
As cinco colunas e os zeros iniciais dos identificadores devem ser preservados.

A tabela da aba Resultado é uma referência fixa, não uma limpeza feita pelo
site. Na aba Executar, a leitura do CSV mostra as oito linhas originais, sem
aparar espaços ou remover registros. Limpeza e exportação virão em branches
próprias. Veja o [contrato de leitura](../../docs/LEITURA_PLANILHAS.md) para
CSV/XLSX, cabeçalhos e limites. Não sobrescreva o material de entrada.

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

A tabela exibida no laboratório é uma referência fixa, não um processamento
feito pelo site. O laboratório oferece conteúdo didático, download do CSV e conferência inicial
de recebimento (extensão e tamanho). Leitura CSV/XLSX, limpeza e exportação
virão em branches próprias; enviar o arquivo ainda não interpreta seu conteúdo.
Não sobrescreva o material de entrada ao implementar a automação.

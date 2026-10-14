# Exemplo fictício — organização de arquivos

`exemplo.zip` é o material público do primeiro laboratório. Todos os textos e
registros são inventados. A imagem é um quadrado azul de 32 × 32 pixels.

## Entrada

| Caminho | Categoria esperada |
|---|---|
| comunicado.txt | Documentos |
| notas.txt | Documentos |
| subpasta/comunicado.txt | Documentos |
| clientes.csv | Planilhas |
| marca.png | Imagens |
| LEIA-ME | Outros |

Os dois comunicados têm conteúdos diferentes. Não sobrescreva um com o outro:
o segundo nome de saída deve ser `comunicado_2.txt`.

## Resultado esperado

Seis arquivos: Documentos=3, Planilhas=1, Imagens=1, Outros=1, além de
`relatorio.csv` na raiz do ZIP de saída. O relatório não conta como entrada.
Preserve o caminho original no inventário.

## Estado da atividade

A página didática, o download do exemplo e o recebimento inicial de um ZIP estão
disponíveis. O envio inspeciona estrutura, caminhos, integridade e limites,
sem extrair ou organizar o conteúdo. Use ZIP Stored ou Deflate sem senha;
ZIP64, outros métodos de compressão e metadados de sistema (__MACOSX,
.DS_Store e Thumbs.db) são recusados nesta versão. ZIPs aninhados não são
abertos recursivamente. Processamento, resultados e script-base Codespaces
ficam nas próximas entregas. O site não executa código do participante.

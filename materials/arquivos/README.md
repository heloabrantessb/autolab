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

A página didática, a organização, o resumo e o download do resultado estão
disponíveis. O envio inspeciona estrutura, caminhos, integridade e limites
antes de organizar. Use ZIP Stored ou Deflate sem senha;
ZIP64, outros métodos de compressão e metadados de sistema (__MACOSX,
.DS_Store e Thumbs.db) são recusados nesta versão. ZIPs aninhados não são
abertos recursivamente. O resultado tem prazo de acesso; sua remoção física
depende da rotina de limpeza descrita em `docs/OPERACAO_RESULTADOS.md`.

O exercício guiado, com script-base e testes locais, está em
`codespaces_exercises/arquivos/README.md` e pode ser baixado pelo site. Ele usa
exclusivamente este ZIP original, conferido por SHA-256, e não processa arquivos
arbitrários. O Codespaces será configurado na próxima entrega. O site não
recebe nem executa código do participante.

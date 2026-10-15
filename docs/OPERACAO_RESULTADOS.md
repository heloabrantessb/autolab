# Operação dos resultados temporários

## Acesso e retenção

O upload original é descartado ao finalizar o processamento. A aplicação
mantém apenas o ZIP organizado e metadados mínimos de resumo e expiração.
`RESULTS_ROOT` deve ser privado, fora de static/media pública, gravável somente
pelo usuário da aplicação. O banco e os resultados devem ser os mesmos para o
servidor web e para a rotina de limpeza.

`RESULT_TTL_MINUTES` limita o acesso e deve ser positivo (default: 30 minutos).
Quem possuir o link pode acessar o resultado até o prazo, sem login. A partir
da expiração, novos acessos retornam 410. Um download já iniciado pode terminar.
Depois da remoção dos metadados, o token passa a retornar 404.

A remoção física ocorre na próxima limpeza bem-sucedida. Com uma execução a
cada cinco minutos, resultados são normalmente removidos até cinco minutos
depois de expirar. Isso depende do agendador e da ausência de falhas; não é uma
garantia de exclusão exatamente aos 30 minutos.

## Comandos

Execute no ambiente virtual e no diretório do projeto, com as mesmas variáveis
de ambiente do servidor, após `python manage.py migrate`:

```bash
python manage.py limpar_resultados --dry-run
python manage.py limpar_resultados --batch-size 100
```

`--dry-run` valida as áreas elegíveis e informa a contagem sem alterar arquivos
ou banco. `--batch-size` controla o tamanho de cada lote de consulta, deve ser
positivo e não limita a quantidade total removida na execução. O instante de
corte é fixado ao iniciar; resultados que expiram depois ficam para a próxima
execução. A rotina revalida o prazo antes de apagar cada resultado.

A limpeza trata somente registros expirados do tipo `arquivos`. Aceita apenas
o caminho canônico `<token>/arquivos_organizados.zip`, remove esse arquivo e
seu diretório vazio e então os metadados. Não percorre outras pastas nem segue
links simbólicos. Arquivo ou diretório já ausente não impede remover metadados.
Outros tipos de resultado precisarão de contratos próprios quando implementados.

## Agendamento externo antes da oficina

O Django não agenda a rotina. Configure um único job a cada cinco minutos,
sem execuções sobrepostas, no host ou no agendador da hospedagem. No SQLite,
`select_for_update` não fornece bloqueio de linha; a exclusão mútua é
responsabilidade do agendador. Não inicie cron dentro do processo web.

Exemplo para Linux com cron e `flock` disponíveis. Substitua `/caminho/autolab`
pelo caminho real, garanta que `var/` existe e pertence ao usuário da aplicação
e use o mesmo arquivo de lock em todas as instâncias do job:

```cron
*/5 * * * * cd /caminho/autolab && flock -n /caminho/autolab/var/limpar-resultados.lock /caminho/autolab/.venv/bin/python manage.py limpar_resultados >> /caminho/autolab/var/limpar-resultados.log 2>&1
```

O exemplo é uma instrução de implantação: nenhum agendamento foi configurado
nesta entrega. Valide o comando manualmente em simulação, confirme as variáveis,
ative o job e confira sua execução com dados fictícios antes da oficina.
Restrinja o acesso e configure rotação dos logs conforme a hospedagem.

## Falhas e recuperação

Falha de arquivo ou banco em uma execução não impede tentar limpar as demais.
O comando informa a quantidade removida e termina com erro se houver falhas,
para permitir alertas do agendador. Mensagens não imprimem caminhos ou nomes
dos arquivos. Resultados válidos permanecem disponíveis dentro do prazo.

Arquivo e banco não participam de uma transação única. Se a remoção física
funcionar e a remoção dos metadados falhar, executar novamente conclui a
limpeza dos registros remanescentes. Não é necessário recriar o ZIP expirado.

Áreas com caminhos adulterados, links, arquivos especiais ou conteúdo extra
são preservadas com erro para inspeção do operador. A rotina não varre áreas
sem registro: isso evita atingir uploads em andamento. Uma interrupção abrupta
do processo pode deixar uma área sem registro; nesses casos, investigue as
execuções ativas e faça manutenção controlada. Não apague recursivamente toda
a raiz de resultados para resolver uma falha.

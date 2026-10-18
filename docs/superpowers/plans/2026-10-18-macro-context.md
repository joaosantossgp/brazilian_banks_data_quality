# Contexto macroeconômico — plano de execução

Issue164, pesquisa159/PR163. João autorizou coletar contexto econômico e pesquisar fontes; seleção factual passou por revisão independente. Execução nativa Root e revisão antes de coleta/aceite. Não há mudança de método dos indicadores financeiros.

## Contrato

Base9026afc. Destinos e allowlist naIssue164: módulo/coletor e perfil finito adjacentes, CLI, teste, esta nota e arquitetura. Nenhuma dependência nova. Pacote macro separado, com junção trimestral por período; não substituir a base financeira, não promover seu ponteiro. Preservar bruto/recibo e observações textuais; painel trimestral conserva frações exatas dos valores publicados e indica transformação. A precisão publicada não é precisão econômica adicional.

## Fatia única de incorporação SIDRA

- [ ] TDD: cabeçalho/identidade nacional/variável/categoria/período, tokens e sentinelas, duplicatas, HTML inválido; trimestre civil e janela completa; média de três meses versus estoque final, PIB nominal TTM.
- [ ] Perfil público finito com oito consultas SIDRA já pesquisadas. PNAD começa2012, demais séries usam2009 como pré-história para2010. Juros/curva pendentes explícitos.
- [ ] Coletor finito preserva bytes/UTC/status/headers/hash e erros; replay usa somente corpos capturados e hashes fixados. Saídas exclusivas e sem sobreposição às fontes.
- [ ] Observações e painel trimestral em Parquet consultável por DuckDB/Python, valores como tokens/frações; inventário e cobertura por série/variável/categoria em manifest.
- [ ] Revisão independente de código antes da captura completa. Coleta autorizada e conferência integral de identidade/cobertura, amostras econômicas e ausência estrutural, preservando falhas.
- [ ] Revisão de dados/SHA, PR/CI/integração; atualizar a nota com comandos/pins e limitações. Nada de teste causal, índice composto ou classificação Sr calculada neste lote.

## Limites

Média de índices mensais exige três observações; IPCA acumulado oficial do mês final tem janela própria, sem média de taxas. Renda real conserva vintage/base móvel. Índices encadeados setoriais não são aditivos. PIB nominal TTM soma quatro fluxos, em milhões de reais; estoque/PIB exige conversão explícita em consulta futura. Erro HTTP/HTML não é ausência econômica. Dados posteriores a2024 não entram por conveniência da captura.

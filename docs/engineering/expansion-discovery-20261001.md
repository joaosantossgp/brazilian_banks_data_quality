# Descoberta limitada para expansão do IF.data

Etapa de planejamento autorizada em 2026-10-01, no LAPTOP-U0J6PT8Q. **Nenhum dado financeiro de novo trimestre foi coletado.** Foram analisados os arquivos oficiais já arquivados e feito um GET adicional de catálogo (HTTP 200, 1.649.748 bytes). Evidência estruturada e inventário por trimestre: `expansion-discovery-20261001.json` e `.csv` neste diretório.

## Disponibilidade anunciada

| Catálogo oficial | Trimestres | Intervalo | Relatórios individuais por trimestre |
|---|---:|---|---:|
| [2000–2024](https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024) | 100 | 200003–202412 | 4 |
| [2025–2030](https://www3.bcb.gov.br/ifdata/rest/relatorios2025a2030) | 6 | 202503–202606 | 4 |

Há 106 datas trimestrais, sem lacunas no intervalo anunciado. Todos os trimestres anunciam cadastro individual e os relatórios Resumo, Ativo, Passivo e Demonstração de Resultado. O nome da DRE contém um espaço final em 24 registros; o nome original deve ser preservado. **Presença no catálogo não comprova que todos os arquivos podem ser baixados nem que todas as células foram informadas.** Nenhum novo arquivo de valores foi solicitado para testar essa disponibilidade.

Resumo individual usa 19 colunas até 2024 e 20 a partir de 2025. Há quatro famílias de IDs de coluna no catálogo: 200003–201812 (76 trimestres), 201903–202009 (7), 202012–202412 (17), 202503–202606 (6). Esse agrupamento identifica alterações de estrutura; não prova equivalência econômica entre famílias. A metodologia oficial confirma mudança Cosif em 2025-01-01. Os caminhos atuais usam o prefixo `ifdata_2025_2030//...`, tal como publicado; não construir caminhos por suposição nem unir séries pelo nome da coluna. [Notas e fontes primárias](expansion-source-research.md).

## Cobertura cadastral efetivamente observada

| Trimestre | Linhas cadastro REST | Códigos distintos | Códigos no Resumo | Diferenças entre conjuntos | Duplicatas |
|---|---:|---:|---:|---:|---:|
| 201012 | 1.976 | 1.976 | 1.976 | 0 | 0 |
| 202412 | 1.585 | 1.585 | 1.585 | 0 | 0 |

Os dois cadastros REST retornaram 200; não há código vazio, nome vazio ou trimestre divergente nesses arquivos. Isso permite afirmar **correspondência integral entre o cadastro REST recuperado e a tabela Resumo recuperada**, por códigos de exibição da mesma fonte. Não resolve a indisponibilidade OData, equivalência de namespaces, todas as instituições historicamente existentes nem a população de capital aberto. O `cadastro_complete=false` do piloto é conservador e não deve ser trocado por um único booleano “universo completo”; a próxima entrega explicitará cada denominador e fonte.

O cadastro contém grupos bancários e não bancários, inclusive muitos registros com códigos `b3S`. Perfis brutos de `c3` são preservados no JSON. Não traduzir o campo nem usar uma seleção de tipos para definir a amostra sem a definição oficial. O universo IF.data amplo é um apoio opcional para inventário/comparação; o foco continua capital aberto.

## Fluxos e versões

As notas oficiais distinguem resultados acumulados janeiro–março, janeiro–junho, julho–setembro e julho–dezembro. Assim, setembro e dezembro não são dois lucros trimestrais independentes. A subtração para obter Q4 exige a mesma entidade/nível, definição e versões compatíveis. O catálogo informa geração de 202409 em 14/04/2025 e 202412 em 15/04/2026; isso impede assumir compatibilidade de revisões. Mesmo dezembro contra dezembro deve preservar versão e composição. [Evidência específica](expansion-source-research.md).

## Volume e custo operacional

Os exportadores independentes bem-sucedidos arquivaram **21.544.834 bytes HTTP em 201012** e **39.426.044 em 202412**, além dos pequenos CSVs/capturas gerados. O catálogo antigo representa 13.527.657 bytes desses totais. O navegador carrega shards trimestrais compartilhados, que incluem outros relatórios/níveis; só o Resumo individual é aceito como observação. Essas medições vêm dos 20 e 23 manifests bem-sucedidos, não das tentativas fracassadas.

Estimativa para **um trimestre adicional semelhante a 2024**: aproximadamente **25–45 MB de corpos brutos**, ou **12–32 MB** se o catálogo já arquivado puder ser reutilizado com origem/horário explícitos. São estimativas baseadas em apenas dois trimestres, não tamanhos confirmados de 202312. Reserva proposta: **150 MiB de disco para a entrega**; teto de **80 MiB de corpos brutos por tentativa**, **480 s por execução**, no máximo **duas tentativas**. Parar e registrar excedentes/falhas; não aumentar o lote automaticamente. Esses limites precisam ser implementados/testados, não estão todos ativos no exportador atual.

Só como ordem de grandeza, o intervalo hipotético 201012–202412 teria 57 trimestres; extrapolar os dois tamanhos medidos produziria cerca de **1,2–2,3 GB HTTP**, antes de saídas derivadas, tentativas e versões. Não é um orçamento validado nem uma escolha da janela da tese. Não executar essa expansão. O volume cresce muito mais com trimestres/versões do que com aceitar mais um relatório sobre shards já arquivados, mas adicionar relatórios exige validação própria de estrutura/semântica.

## Recomendação

Primeiro fechar dois trabalhos sem novas requisições financeiras: cobertura/marcadores por fonte e um dossiê de identidade temporal para os três emissores já examinados. **O menor próximo lote financeiro útil recomendado é apenas 202312, individual, Resumo**, com revisão explícita do catálogo. Ele tem as mesmas 19 colunas/IDs de 202412, fica antes da mudança de 2025 e compara dezembro contra dezembro, reduzindo o risco de janelas de fluxo diferentes. Não fixa uma série anual nem a amostra final.

202409 é alternativa para testar mudanças intra-ano de estoques, mas acrescenta a diferença de janela dos fluxos. 202503 exige primeiro um estudo específico da quebra de esquema/Cosif. Ativo, Passivo, DRE e histórico completo ficam fora deste lote. A existência do caminho anunciado de 202312 foi verificada; seu cadastro, valores, tamanho e quantidade de instituições ainda são desconhecidos.

Decisões humanas antes de escalar a amostra da tese: **unidade de análise** (instituição individual ou nível consolidado, após casos de holding), **janela temporal final** e **regra de elegibilidade**, explicitando o papel distinto de registro CVM e evidência B3. A evidência atual não autoriza um vínculo automático do emissor Itaú Unibanco Holding com o banco individual ou conglomerado. CVM/B3 continuam apenas como metadados, com estados históricos desconhecidos quando não houver prova datada.

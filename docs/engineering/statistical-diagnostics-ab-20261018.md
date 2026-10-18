# Execução das camadas de diagnóstico e robustez

Registro da [Issue 175](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/175), conforme o [protocolo de tratamentos e testes](statistical-treatment-protocol-20261018.md) e o [plano de execução](../superpowers/plans/2026-10-18-statistical-diagnostics-ab.md). A execução local e suas revisões estão concluídas. Publicação, SHA entregue, integração e CI pós-merge têm evidência própria na Issue; este documento não substitui essa verificação remota.

## Escopo e entradas fixas

Camada A: integridade, elegibilidade, ausências, sinais dos componentes, cobertura e distribuição, com reconciliação exata. Camada B: influência da retirada de cada unidade e sensibilidade à composição entre datas. Todas as métricas e janelas disponíveis de 2010–2024, com Financeiro, Capital e Individual separados; agregados gerais, Tcb e SrAnalitico em sua janela própria. Não há interpretação econômica nem teste inferencial.

A seleção foi descoberta pelo ponteiro privado compartilhado `data/curated/current-indicators.json`, com contrato e hashes autenticados:

| Entrada | Pacote relativo ao checkout principal | SHA-256 do manifest |
| --- | --- | --- |
| Indicadores | `data/curated/historical-links32-composition-20261018-run3` | `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60` |
| Macro, somente metadados | `data/curated/macro-context-20261018-run2` | `9920b6ebe130854130ab9ec7e7bfe98410556f22f81b969128be2704be8de118` |

As variáveis macro não são necessárias para essas verificações e seus valores não foram consumidos. O ponteiro deve ser revalidado no fechamento; uma nova promoção exige migração explícita e nova execução em destino próprio. Pacotes aceitos e ponteiro não são modificados.

## Instrumentos e preservação

Instrumentos descartáveis, testes, recibos, saídas, revisões e tentativas ficam no diretório privado ignorado `.scratch/statistical-diagnostics-ab/` do worktree desta frente. O Git recebe somente este registro e o plano. Reutilizam-se os helpers canônicos de elegibilidade, agregação e aritmética exata, sem novo módulo de produção ou dependência. Frações e sinais são preservados; arredondamento pertence somente à apresentação.

As linhas nativas e as companhias nominais sem contribuição são separadas. A conferência do piloto identificou que o produtor canônico acrescenta algumas linhas nominais após a escrita da cobertura nativa. O instrumento inicial não reproduzia esse passo; a expansão foi suspensa, corrigida e revista novamente, sem alterar o pacote aceito. Tentativas falhas permanecem identificadas como falhas.

## Limites para a decisão posterior

A retirada de unidades é uma sensibilidade determinística, não um intervalo de confiança. A interseção de códigos entre datas mede composição de reporte, sem certificar identidade ou perímetro econômico estável. Denominadores remanescentes zero são não calculáveis, nunca zeros financeiros. A composição compara trimestres efetivamente consecutivos, dezembros consecutivos e extremos calculáveis; lacunas não são comprimidas.

Médias institucionais, medianas e razões das somas são quantidades diferentes. A execução não testa independência, normalidade ou estacionariedade; TTM contém sobreposição mecânica. Nenhum diagnóstico autoriza automaticamente Welch, Levene/Brown–Forsythe ou inferência temporal. A escolha acadêmica continua com João/orientador na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

## Verificação e entrega

A integral concluiu localmente com `pass` no instrumento: 3.240 contextos-base, 5.021.050 linhas nativas e 8.862 nominais, 4.300.156 contribuições elegíveis e 167.368 resumos/detalhes. Foram realizadas 2.330.192 conferências exatas. O tempo foi 1.577,08 segundos e o pico de memória do processo, 870.379.520 bytes. Recibo: SHA-256 `e27c5529847015791ab8153af9c4442b29cdcf9ed96c7ee8ff9e3ed4df53ab65`.

A revisão independente integral A aprovou o gate antes de B: streaming de todos os resumos/detalhes e 4.300.156 contribuições elegíveis; 12.960 agregados gerais comparados diretamente aos aceitos em 259.200 campos; 35 contextos de fronteira e 19 testes pertinentes conferidos. Nenhum achado material aberto. A falha inicial de parsing do verificador do revisor foi preservada, com recibo corrigido próprio; não foi falha do resultado A.

B piloto concluiu localmente: 3 contextos-base, 128 resumos de influência, 23.814 retiradas e 125 pares de composição. Das retiradas, 16 ficaram não calculáveis. Tempo 58,15 segundos e pico 786.677.760 bytes. A revisão independente aprovou inventários, calendário e cálculos amostrais antes da expansão.

B integral concluiu localmente com `pass`: 106.516 resumos de influência, 21.478.654 retiradas, das quais 8.188 não calculáveis; 103.476 pares trimestrais, 24.534 pares de dezembro e 2.641 pares extremos, total 130.651. Todas as 4.300.156 contribuições nativas elegíveis foram consumidas e reconciliadas por contexto com A. Tempo 844,77 segundos e pico 1.208.233.984 bytes. Recibo: SHA-256 `b4182f6ddf20a2048ce6bd98f7c2e6d10777c09f2470164e9680cf51bd97837b`.

Os 3.152 contextos-base com contribuições elegíveis em B são subconjunto dos 3.240 auditados em A; os 88 sem contribuições elegíveis permanecem explicitados em A, sem criar zero financeiro. Da mesma forma, A conserva os 60.852 resumos sem unidade elegível, além dos 106.516 com contribuições usados em B. Essas contagens repetem unidades entre datas/indicadores e não medem observações independentes.

A revisão independente B aprovou hashes, encadeamento, todos os inventários, contagens e calendário. Recalculou, com implementação independente, 8.906 retiradas em 18 contextos e 18 pares de composição. Essa aritmética independente foi amostral, sem alegar conferência independente de todas as frações das 21 milhões de retiradas. Nenhum achado material aberto.

## Relatório e inventário privado

O relatório `presentation2/diagnosticos.md` e o CSV `presentation2/series-diagnostics.csv`, relativos ao diretório privado contratado, apresentam diagnóstico de 3.784 séries e exemplos de distribuição, influência em 202412 e composição 202312→202412. Todos os demais resultados permanecem nos arquivos completos A/B. Exemplos foram fixados antes da leitura dos resultados; a revisão da apresentação acrescentou a coorte unknown para tornar explícita a partição completa, sem mudar qualquer cálculo A/B.

Na primeira apresentação, a legenda de remaining não explicitava unknown. A versão foi preservada e substituída em destino novo; remaining significa unidades fora da seleção com pertença conhecida, enquanto unknown conserva pertença não resolvida. Contagens nativas e componentes são aditivos entre as três coortes disjuntas; razões e quartis não são. Não se completaram vínculos ou classificações para eliminar unknown.

A revisão real da apresentação recompôs todas as 3.784 séries e 68.112 campos, conferiu todos os números das cinco tabelas Markdown, 17 contextos de influência e 17 pares de composição diretamente na fonte, além de 45 distribuições e 225 valores de quartis/mínimo/máximo. Percentuais e pontos percentuais foram conferidos por arredondamento racional a quatro casas. O relatório tem SHA-256 `030deb14c8f8d8d09d901092c5203cf9f54ff17955fd10e7c1a40820effe248f`.

| Destino privado relativo | Conteúdo |
| --- | --- |
| `run-a-full1/` | Resumos CSV, detalhes completos comprimidos, todas as contribuições elegíveis, auditoria e recibo autenticado |
| `run-b-full1/` | Todas as retiradas comprimidas, resumos, composição completa, listas/proxies, auditoria e recibo |
| `presentation2/` | Relatório Markdown, inventário das séries e recibo com hashes/linhagem |
| `delivery2/` | ZIP compacto de revisão e recibo; detalhes grandes ficam externos, inventariados por caminho/hash |
| Raiz privada e destinos anteriores | Instrumentos, testes, verificadores independentes, pareceres, logs, pilotos e tentativas preservadas |

O ZIP é pacote de consulta e evidência, não backup integral do repositório/dados. Os instrumentos conservam sua localização original no worktree e seu vínculo à base de código `970e3f3417a83a84eca9adf369176348e39f19b9`. Os pacotes de origem não são copiados. Não há upload dos resultados privados ao Git público.

ZIP final: 66.019.766 bytes, 77 membros, SHA-256 `79e31e516e43316edfdfc4126ca5993bd5f97428cf596d475d448861530fe8c2`. CRC e hashes de todos os membros foram conferidos por leitura de volta. O manifest inventaria quatro arquivos grandes de detalhes e 34 arquivos de pilotos/tentativas preservados externamente. O log ainda aberto da própria geração foi excluído do pacote; a geração anterior e seu produtor foram preservados. O parecer independente do ZIP acompanha a entrega fora do arquivo, evitando uma referência circular.

Foram aprovados 46 testes de código pertinentes, com RED/GREEN e correções preservados; são testes dos instrumentos, não hipóteses estatísticas. As revisões por fatia e a execução real verificam aspectos diferentes desses testes. Não foi executada suíte de produção por causa dos dois Markdown: o check documental e a revisão do SHA final têm evidência na Issue.

## Composição da entrega

Inventário público completo: duas adições Markdown, este registro e o plano; nenhum rename/delete. Sem alteração de produção, dependências, camada arquitetural, fórmulas, pacote aceito, ponteiro, explorador ou manuscrito. Os diretórios existentes mantêm suas responsabilidades. O worktree preserva os artefatos ignorados e não deve ser arquivado sem preservá-los.

Durante a execução, main recebeu cinco commits documentais de outras frentes, até `8893be447ade5acc8fdd47078b69b93f43aef1ff`; nenhum alterou os helpers de produção usados. Esta frente mantém a base executada e sua allowlist, com revisão final da composição no SHA entregue. O checkpoint final na Issue registra os checks, pareceres, PR, ancestralidade e CI pós-merge, sem afirmar sincronização do checkout principal.

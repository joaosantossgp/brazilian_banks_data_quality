# Indicadores por Tcb: composição e adequação

Registro da [Issue #192](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/192), execução iniciada em 19/10/2026 UTC. **Expansão histórica, composição, diagnósticos A/B e documentação aceitos localmente após revisão independente. Publicação e integração pendentes.** O objetivo é preservar os 20 indicadores existentes e acrescentar os sete adotados no Financeiro, com diagnóstico e lacunas próprios. Não se declara cobertura metodológica completa das cinco dimensões para todas as atividades.

## Conjunto adotado e recorte

| Novidade | Pergunta e fórmula | Janela/perspectiva | Contrato e fonte |
|---|---|---|---|
| L1, encaixe voluntário | Disponibilidades / depósitos à vista | Ponto; Financeiro | [Piloto #189](tcb-assaf-sensitivity-pilot-20261018.md), Assaf (2015), p. 334. |
| PL_DEP, capital sobre depósitos | PL / depósitos | Ponto; Financeiro | #189, Assaf, p. 337; capital contábil, não prudencial. |
| R3, margem sobre receita de intermediação | LL / RIF | Trimestre/TTM; Financeiro | #189, Assaf, p. 341; denominador selecionado. |
| RIF_AT, receita de intermediação por ativo médio | RIF / AT médio | Trimestre/TTM; Financeiro | #189, Assaf, p. 342; adaptação temporal explícita, não margem líquida. |
| E2-W, eficiência sobre renda selecionada ampliada, principal | −(pessoal + administração) / (RBIF − resultado de provisão + serviços + tarifas + outras receitas operacionais) | Trimestre/TTM; Financeiro | [Conciliação #182](tcb-income-reconciliation-20261018.md) e [piloto #190](tcb-income-indicator-pilot-20261018.md); adaptação própria, Assaf, p. 342, e FMI (2019), §§5.16/5.25/7.60–63, sem equivalência automática. |
| E2-WP, sensibilidade incluindo participações | Mesmo numerador; denominador de W + participações | Trimestre/TTM; Financeiro | #190; custos das investidas podem estar fora do numerador. Série distinta de W e E2-B. |
| QL, intensidade contábil da provisão de arrendamento | −provisão de arrendamento / recebíveis antes dessa provisão | Ponto; Financeiro | [Conciliação #183](tcb-leasing-reconciliation-20261018.md) e [piloto #191](tcb-leasing-indicator-pilot-20261018.md); Cosif e adaptação descritiva, não inadimplência ou suficiência regulatória. |

As [decisões de #189](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6258035046) e [#190/#191](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6258359846) fecham a lista. Outros candidatos permanecem na [fila #188](tcb-additional-measures-feasibility-20261018.md), sem adoção por inferência. As notas dos pilotos identificam contas/contextos, sinais, janelas, fundamentos, limites e regras de cálculo de cada novidade.

Os 20 atuais mantêm nomes e fórmulas: R1/R2, Q1/Q2, C1/C3/C4, L2/L3, E2-B, LA/LC, LF-DEP/LF-OC/LF-EM/LF-REP e RS/E3/R4/R5. C3/C4 continuam na perspectiva própria; Individual conserva suas séries já aceitas. Os sete novos não são impostos implicitamente ao Individual: a composição usa as perspectivas dos manifests autenticados, registradas em `complement_perspectives`. A existência de binding Individual no motor não equivale à adoção acadêmica ou a um piloto dessa perspectiva.

## Adequação: oito famílias e cinco dimensões

“Condicional” significa interpretação dependente de função econômica, composição, data/perímetro e componentes, não exclusão automática da unidade. Uma dimensão pode ter descrições contábeis disponíveis e ainda carecer de medida específica. Tcb organiza famílias; SegmentoTb refina os subtipos. Tc/Td/Sr/SrAnalitico esclarecem controle, unidade e regime, sem produzir uma fórmula para cada cruzamento. Atividade não retorna aos filtros. A disponibilidade computacional e a adequação econômica são campos distintos.

O inventário da **base de entrada aceita**, no Financeiro de 201003 a 202412, contém 89.476 unidades-trimestre. São ocorrências ao longo do tempo, não instituições distintas:

| Tcb observado | Unidades-trimestre |
| --- | ---: |
| B1 | 5.853 |
| B2 | 2.092 |
| B3S | 60.515 |
| B3C | 2.189 |
| B4 | 240 |
| N1 | 7.988 |
| N2 | 9.120 |
| N4 | 1.440 |
| Sem Tcb observado | 39 |
| **Total** | **89.476** |

Consulta: agrupar `unit_periods.parquet`, autenticado pelo pin inicial abaixo, por `json_extract_string(payload, '$.classifications.Tcb')`, filtrando `dataset='financial'` e a janela principal. Os 39 casos sem Tcb ficam preservados; nenhuma família é imputada. A mesma base contém 44 unidades-trimestre com vínculo desconhecido: classificação desconhecida e vínculo desconhecido são atributos diferentes. Os tokens B3/N3 de outros períodos do [inventário amplo](ifdata-segmentation-inventory-20261013.md) não aparecem neste recorte financeiro, sem se inventar um de-para para eles.

| Tcb | Rentabilidade | Qualidade de ativos/crédito | Capital/alavancagem | Liquidez/financiamento | Eficiência |
|---|---|---|---|---|---|
| B1 | R1/R2; R3/R4/RIF_AT/R5 condicionados ao mix de intermediação e serviços. | Q1/Q2 para crédito próprio; QL se houver recebíveis de leasing. NPL e cobertura específica continuam lacunas. | C1 contábil; C3/C4 em regime e perímetro demonstrados. PL_DEP é relação com depositantes, não requerimento. | L1/L2/L3 na função depositária; LA/LF descrevem composição. Estresse, recursos livres e maturidade continuam próprios. | E2-W principal; E2-B sob seu conceito; E2-WP separada. E3 mede custo/ativo; RS, composição. Não medem eficiência técnica. |
| B2 | R1/R2 e composição; R3/RIF_AT não resumem necessariamente serviços, câmbio ou mercado. | Crédito próprio e leasing condicionais; não imputar risco de clientes ou custódia ao ativo próprio. | C1 e prudenciais conforme regime; fontes, contrapartes e posições próprias importam. | L1/L2/L3 somente quando DV e depósitos representam a pergunta; LA/LF não resolvem liquidação, colateral ou prazos. | E2-W amplia a renda selecionada; E2-WP exige olhar investidas. Custos restritos e negociação própria limitam comparação. |
| B3S | R1/R2 medem retorno contábil; benefício ao cooperado não se reduz a ROE. | Q1/Q2 na carteira própria; QL se houver recebíveis. NPL, garantias e concentração não são substituídos por provisão. | C1 e capital do regime; S5 não autoriza preencher CP com PR ou certificar opção PRS5. | L1/L2/L3 condicionados à captação; LA/LF contábeis. Centralização 145, restrições e resgate não individualizados. | E2-W/E3/RS sob composição; benefício e preço ao cooperado, além de produtividade, exigem dados próprios. |
| B3C | Retorno contábil e composição, sem somar razões para inventar sistema cooperativo consolidado. | Exposição própria, sem somar carteiras das filiadas por nome; QL condicional. | C1 e prudenciais pertinentes; filiação e suporte não equivalem a conglomerado com eliminações. | Obrigações 445 e recursos de suporte precisam de abertura. AIL/depósitos interfinanceiros não é índice de centralização. | Custos e renda próprios; operações internas e suporte condicionam comparação com singulares. |
| B4 | R1/R2 e intermediação caracterizam sustentabilidade; adicionalidade e mandato continuam medidas próprias. | Q1/Q2 e QL onde aplicáveis; prazo, garantias e NPL não são providos por essas razões. | C1/C3/C4 conforme unidade e regime; garantia pública não é capital elegível por inferência. | LA/LF para composição; L2 sobre DV não encerra liquidez. Faltam maturidades, restrições, agenda de desembolso e fontes institucionais individualizadas. | E2-W/E3 descrevem custos selecionados; resultado do mandato e eficiência do financiamento requerem produtos e objetivos. |
| N1 | R1/R2 para retorno contábil; R3/RIF_AT condicionados à intermediação. Abrir por SegmentoTb: fomento, leasing, financeiras e SCD/SEP não são equivalentes. | Q1/Q2 somente para crédito próprio compatível; QL é extensão específica para recebíveis de leasing, inclusive fora de N1. Rendimento do leasing continua não adotado. | C1 e prudenciais quando pertinentes; regras, optantes e ausência de CP são verificados, não inferidos da categoria. | LA/LF contábeis; depósitos condicionam L1/L2/L3/PL_DEP. Fomento e imobiliário exigem prazo e restrição; SEP não recebe carteira própria inventada. | E2-W/E3/RS condicionados ao subtipo e composição; volume por produto e custos próprios seguem como lacunas. |
| N2 | R1/R2 com renda própria, serviços e negociação explicitados; R3 seleciona intermediação. | Somente exposições próprias de crédito ou leasing, quando existentes. Custódia ou contas de clientes não viram carteira própria. | C1 e regime prudencial aplicável, sem equivalência automática com bancos ou regra de 2025 retroativa. | Recursos próprios livres, obrigações de clientes, margem, garantias e D+1…D+5 faltam nos agregados. LA/LF e DV não suprem essa correspondência. | E2-W é complemento fundamentado à renda estreita; custos próprios, repasses e produtos condicionam leitura. Não mede produtividade de transações. |
| N4 | Retorno da unidade e sua composição; R3/RIF_AT podem representar pouco um negócio de serviços. | Risco de crédito próprio, se demonstrado; recebíveis de usuários ou arranjo não são carteira bancária por rótulo. | C1 não substitui regime específico de IP; CP/PR do banco do grupo não preenche capital da operadora. | A conta 110560 de pré-paga é componente desde 202006; faltam recursos elegíveis ou vinculados e modalidade/regime. LA/LF não são salvaguarda ou conformidade. | E2-W com numerador restrito; E2-WP separada; TPV, preços e custos por serviço não estão medidos. |

Fontes e próximos recortes: [centralização #184](tcb-cooperative-liquidity-feasibility-20261018.md), [financiamento #185](tcb-funding-maturity-feasibility-20261018.md), [clientes #186](tcb-client-obligations-feasibility-20261018.md), [pagamentos #187](tcb-payment-safeguarding-feasibility-20261018.md) e [demais medidas #188](tcb-additional-measures-feasibility-20261018.md). A matriz sintetiza adequação conceitual, não uma certificação de cada unidade. Classe observada, derivada, conflitante e desconhecida continua nas tabelas; Td=I não comprova independência societária, e Sr não é simples faixa de tamanho.

Representatividade em AT, crédito e PL mostra a parcela dos estoques conhecidos que pertence às unidades elegíveis; não equivale à cobertura da atividade específica. Em QL, por exemplo, incluir um banco com grande ativo e pequena carteira de leasing não demonstra grande cobertura do mercado de arrendamento. O agregado do indicador usa os próprios recebíveis antes da provisão como denominador, enquanto os estoques contemporâneos contextualizam as instituições atendidas. Ambos conservam desconhecidos, sinais e limites de sobreposição econômica do universo observado.

## Retrato de cobertura em dezembro de 2024

O retrato usa ponto para estoques e TTM para os quatro indicadores de fluxo, conforme seleção fixada antes dos diagnósticos. Inclui todas as 1.422 unidades Financeiro observadas, nas oito Tcb. Os casos sem classificação observados em outros períodos permanecem no histórico. As companhias constituem uma dimensão nominal separada: 32 no escopo analítico, dentro do registro de 55.

| Indicador | Janela | Unidades elegíveis / presentes | Companhias elegíveis / escopo | AT conhecido | Crédito conhecido | PL conhecido |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| L1 | Ponto | 676 / 1422 | 27 / 32 | 85,9659% | 89,1529% | 76,3858% |
| PL_DEP | Ponto | 969 / 1422 | 32 / 32 | 97,9280% | 99,7693% | 94,8900% |
| QL | Ponto | 27 / 1422 | 13 / 32 | 57,6437% | 55,2763% | 50,9229% |
| R3 | TTM | 1341 / 1422 | 32 / 32 | 99,4611% | 99,5506% | 99,5837% |
| RIF_AT | TTM | 1336 / 1422 | 32 / 32 | 99,4517% | 99,5493% | 99,6202% |
| E2-W | TTM | 1352 / 1422 | 32 / 32 | 99,4721% | 99,5506% | 99,6456% |
| E2-WP | TTM | 1352 / 1422 | 32 / 32 | 99,4721% | 99,5506% | 99,6456% |

Percentuais são aproximações de apresentação com quatro casas; componentes e frações persistidas permanecem exatos. A cobertura usa somente estoques próprios conhecidos, com sinais preservados; não equivale à parcela do SFN consolidado ou da atividade específica. Em particular, o AT dos bancos elegíveis para QL não mede a cobertura do mercado de leasing. Pesos de PL negativos permanecem sinalizados.

Os três CSVs privados revisados enumeram 984.236 registros nativos, 36.300 de companhias e 123.772 de categorias, nos 660 contextos indicador/janela/período. Os recortes cobrem Tcb, SegmentoTb, Tc, Td, Sr original e SrAnalitico, conservando estado observado, derivado, conflitante ou desconhecido conforme a fonte. Nomes de companhias exportados são metadados de 2024, sem imputação de nomes históricos. As listas completas de unidades e companhias suprem o detalhe nominal; listas limitadas dos resumos de segmentos não são usadas para reconstruí-lo.

A consulta do retrato usa `aggregates.parquet` autenticado, `dataset='financial'`, `period='202412'`, coorte total extraída do payload e as janelas acima; lê `counts`, `asset_coverage.share_of_known_fraction` e `representation_coverage.credit/PL.share_of_known_fraction`. A conferência integral dos CSVs comparou 1.144.308 linhas, todos os payloads e colunas projetadas com os Parquets.

## Lacunas remanescentes e próximos recortes

Esta é uma ordem operacional proposta para futuras conciliações, após o conjunto adotado. Não autoriza nova coleta ou adoção automática. As pesquisas concluídas podem demonstrar uma lacuna sem que isso bloqueie os sete indicadores já escolhidos. Fontes e decisões novas conservam seus contratos próprios.

| Prioridade | Recorte e lacuna | Natureza | Próximo passo pequeno e verificável |
| --- | --- | --- | --- |
| 1 | Liquidez de B3S/B3C, B4/N1, N2 e N4 | Dados: centralização e restrição, prazos e fontes, obrigações de clientes, recursos elegíveis e modalidade não estão individualizados nos agregados examinados. O conceito econômico muda conforme a atividade. | Escolher uma atividade e demonstrar os componentes correspondentes na mesma unidade e data, seguindo [#184](tcb-cooperative-liquidity-feasibility-20261018.md) a [#187](tcb-payment-safeguarding-feasibility-20261018.md). Não somar medidas diferentes nem usar L1/L2 como substituto universal. |
| 1 | Inadimplência e cobertura de crédito | Dados e definição: faltam NPL com critério datado e a correspondência entre carteira e provisão. Q1/Q2 e QL não suprem essas informações. | Conciliar um recorte de crédito relevante com componentes compatíveis antes de propor NPL/carteira ou provisão/NPL; [fila #188](tcb-additional-measures-feasibility-20261018.md). |
| 2 | Folga de capital e regimes simplificados | Método e dados: mínimos e adicionais por unidade/data, opção pelo regime e perímetro. A existência de PR, CP, RWA ou ACP não fecha sozinha a medida. | Verificar um regime e uma data, com regra e componentes próprios. Preservar C3/C4 e sua ausência observada; não preencher CP com PR nem impor percentual mínimo uniforme. Ver #188. |
| 2 | Rendimento do leasing | Conciliação conceitual e abertura de dados: rendas, resultado de cessão e ativos produtores ainda não têm alcance equivalente demonstrado. | Fechar primeiro o alcance das rubricas e a abertura faltante, conforme [#183](tcb-leasing-reconciliation-20261018.md). QL permanece medida separada; não liberar rendimento por analogia com crédito. |
| 2 | Benefício ao cooperado, mandato e produtividade de serviços | Método e dados: definir resultado econômico pertinente e produtos, volumes e custos correspondentes. | Escolher uma pergunta por atividade e seu dado observável. Retorno contábil, custo/ativo ou custo/renda continuam descrições próprias, sem certificar benefício, adicionalidade ou eficiência técnica. Ver #184/#185/#188. |
| 3 | Imobilização, custo de captação, remuneração do capital e valor econômico | Candidatos não adotados; parte exige conciliação de rubricas e parte exige fontes ou parâmetros adicionais. | Consumir as fichas de #188, distinguir o que já é calculável do que exige ajuste/fonte e submeter a eventual adoção. Não acrescentar razões somente porque a conta existe. |

Nesta entrega, dados ausentes, ausência de histórico, conceito inadequado e não aplicabilidade continuam estados diferentes. Nenhuma dessas lacunas é resolvida por exclusão silenciosa de instituições ou pela composição de um índice único.

## Verificações de realização

A composição local final, com manifest SHA-256 `f374150e5d4c515f032fdf3fad3cb27b4e196486cee8d81c19150c39df45981b`, passou pela revisão independente integral. Contém **6.005.286 contribuições**: 5.021.050 anteriores e 984.236 novas; 214.500 registros de companhia, 15.600 agregados, 15.600 distribuições, 719.860 recortes de segmentação, 551.595 comparações e 355.632 células conjuntas. Cada uma das tabelas estruturais de unidades e de estoques contém 244.001 registros, que atravessam as três perspectivas; não são instituições distintas nem totais financeiros somáveis.

Em dezembro de 2024, o Financeiro contém 1.422 unidades e 25 IDs de indicadores; Individual, 1.585 unidades e 18 IDs; Prudencial, 1.367 unidades e dois IDs. São **27 IDs distintos** no conjunto, com sete novidades somente no Financeiro. Valores, estados e flags de todas as 5.021.050 contribuições anteriores foram preservados, incluindo os 16 resultados Terra. As 984.236 contribuições novas foram reconciliadas com os 30 pacotes de origem. Foram rederivados independentemente os 2.640 agregados, 2.640 distribuições, 123.772 recortes, 94.809 comparações e 50.336 células conjuntas novos, nas 60 referências.

A revisão também identificou uma perda de proveniência no replay: campos de vínculo acrescentados depois da composição original não eram integralmente propagados. A [correção finita registrada na Issue](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/192#issuecomment-6260298291) restaurou, a partir da base aceita, 1.755 campos em 810 contribuições e 45 estoques, sem alterar valores, flags, coortes ou fórmulas. O piloto de dois cortes precedeu a ampliação. A prova integral comparou 6.249.287 linhas nas duas tabelas: fora dos 855 IDs, todos os payloads e colunas permanecem idênticos; os outros sete arquivos foram copiados byte a byte. O wrapper conserva as fontes, seus pins e a ancestralidade Terra.

A estrutura não é descrita como idêntica à base anterior: 45 motivos de seleção foram atualizados e houve adições de evidência em três unidades e em relações de 54 registros de companhia, todos conferidos com a mesma fonte histórica pinada. Essas diferenças não criam associação, controle, coorte ou método novos. Uma consulta inicial de revisão excedeu seu limite de memória; a verificação integral subsequente percorreu os 60 trimestres, sem amostragem ou redução do universo.

Pin inicial `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`, descoberto pelo diretório Git comum; baseline técnico original `b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`. Destinos novos por ano e tipo de janela, no diretório privado curated existente. O motor calcula somente os sete IDs; composição lê valores persistidos e preserva as correções e vínculos atuais. Não há nova coleta, emenda de perspectivas ou modificação dos pacotes aceitos.

O primeiro gate histórico, de 2010/2019, concluiu quatro pacotes, 306.289 componentes e 137.775 resultados/coberturas, com 89.138 razões OK rederivadas independentemente. TTM de 2010 antes de dezembro conserva falta de histórico; fluxos de abertura não liberados não são imputados. R3/TTM de 201903/06/09 conserva incompatibilidade de definição, sem transplantar pontes de R1/R2. Esse gate liberou os 13 anos restantes, sem convertê-lo em aceite da futura composição integral.

A revisão integral dos demais 26 pacotes aprovou 2.254.998 componentes e 846.461 resultados, dos quais 698.533 OK foram rederivados com aritmética racional. A expansão completa fecha em **30 pacotes, 2.561.287 componentes e 984.236 resultados**, com **787.671 razões OK** conferidas independentemente. As contagens repetem unidades entre indicadores e períodos; não são observações independentes nem contagem de instituições distintas. Os nove arquivos da base de entrada aceita e o ponteiro compartilhado permaneceram inalterados.

A disponibilidade das expansões revisadas é a seguinte. Cada linha corresponde a uma janela: a mesma unidade aparece em vários indicadores e trimestres. “OK” informa que a razão foi calculada; a elegibilidade exige também aplicabilidade confirmada. Esta tabela antecede o remapeamento final de vínculos e não mede representatividade econômica.

| Indicador | Janela | Resultados esperados | Razões OK | OK com aplicabilidade confirmada |
| --- | --- | ---: | ---: | ---: |
| L1 | Ponto | 89.476 | 51.143 | 51.143 |
| PL_DEP | Ponto | 89.476 | 60.599 | 60.599 |
| QL | Ponto | 89.476 | 2.099 | 2.039 |
| R3 | Trimestre | 89.476 | 87.937 | 87.937 |
| R3 | TTM | 89.476 | 77.252 | 77.252 |
| RIF_AT | Trimestre | 89.476 | 88.121 | 88.121 |
| RIF_AT | TTM | 89.476 | 81.101 | 81.101 |
| E2-W | Trimestre | 89.476 | 88.345 | 88.345 |
| E2-W | TTM | 89.476 | 81.364 | 81.364 |
| E2-WP | Trimestre | 89.476 | 88.346 | 88.346 |
| E2-WP | TTM | 89.476 | 81.364 | 81.364 |
| **Total de ocorrências** | | **984.236** | **787.671** | **787.611** |

Em QL, os 60 cálculos com aplicabilidade desconhecida preservam denominadores negativos e ficam fora dos agregados elegíveis; cálculo não prova recebíveis economicamente compatíveis. As 86.683 ocorrências com denominador zero e as 694 com nulo não são classificadas automaticamente como não aplicáveis. L1 conserva 37.639 denominadores zero e PL_DEP, 28.183. Nos fluxos TTM, 5.435 ocorrências por indicador conservam histórico insuficiente; R3 registra ainda 3.938 incompatibilidades de definição. Nulos, bindings ausentes e aberturas indisponíveis conservam seus estados próprios. A consulta agrupa `metric`, `horizon`, `status` e `applicability` de `unit_coverage.parquet` dos 30 manifests autenticados; o recibo privado registra hashes, contagens e grupos completos.

A composição respeita os escopos autenticados por perspectiva e exige todas as unidades e periodicidades declaradas. O ajuste passou por RED/GREEN, teste com Individual próprio e complemento apenas Financeiro, 19 testes de composição e revisão independente antes dos dados. Uma guarda impede avaliação de fórmulas durante a composição real. Os indicadores antigos não são reavaliados; estatísticas descritivas e remapeamentos têm conferência separada.

O primeiro piloto de composição, com 201003, 201903 e 201912, passou pela revisão integral: 250.496 contribuições antigas e 49.159 novas preservadas; 780 agregados, 780 distribuições, 38.088 segmentos, 29.151 comparações e 19.260 células conjuntas conferidos. Essa seleção não exercitava a correção Terra de 202412. Antes da ampliação, a inspeção da derivação demonstrou que o replay da configuração original perderia os 16 resultados corrigidos depois dela. O [checkpoint da Issue](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/192#issuecomment-6259095356) registra a preservação desses resultados já aceitos, por adaptador privado e pela operação finita existente, com fontes e hashes explícitos e sem avaliação de fórmulas. Um piloto adicional de 202412 precede o aceite integral. A ponte anterior não é ampliada aos indicadores novos.

Esse piloto adicional aprovou 80.916 contribuições anteriores, incluindo os 16 resultados Terra, e 15.642 novas. Todos os derivados de 202412 foram conferidos independentemente. A primeira tentativa integral foi interrompida por dimensionamento de armazenamento: os CSVs temporários das nove tabelas aceitas exigiriam ao menos 24,57 GB, antes das séries novas e saídas finais. A tentativa parcial de 0,92 GB foi preservada, sem manifest completo ou aceite. O registro inicial de buffers vazios antecedia a parada e foi [corrigido explicitamente](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/192#issuecomment-6259269232).

A execução retomada usa um adaptador privado que grava blocos de 4.096 linhas por meio do Writer existente, autentica suas partes Parquet e concatena os mesmos payloads. O piloto de equivalência aprovou as nove tabelas integralmente; maior CSV temporário individual de 29,37 MB e soma dos máximos de 110,29 MB. Não houve alteração de código de produção, fórmulas ou dependências por esse ajuste de armazenamento. A estimativa de espaço para o lote integral é uma projeção operacional, não garantia de tamanho. Os instrumentos e tentativas permanecem no inventário privado da tarefa.

Checks pertinentes aprovados: 119 testes do motor, com um skip existente; 39 testes seletivos; 19 testes de composição. Os instrumentos estatísticos privados passaram por 37 testes. Essas verificações de software não substituem as revisões econômicas e dos dados.

Os diagnósticos A/B reutilizam [#175](statistical-diagnostics-ab-20261018.md) e o [protocolo #173](statistical-treatment-protocol-20261018.md), exclusivamente sobre as sete séries novas. Núcleos exatos foram preservados; os executores usam o candidato pinado após aceite local independente, mantendo o ponteiro compartilhado antigo intacto. Contextos explícitos fora do recorte são rejeitados, sem execução parcial silenciosa. Não há winsorização, cortes, imputação, testes inferenciais ou índice composto. Interseção de códigos entre datas não certifica continuidade de perímetro econômico.

O diagnóstico A completo passou pela revisão independente: 660 contextos-base, 984.236 contribuições nativas e 1.562 ocorrências nominais de companhias admitidas sem unidade correspondente. Os 787.611 registros elegíveis foram exportados integralmente; 34.364 resumos passaram por 478.456 reconciliações exatas. A revisão recalculou quartis tipo 2, IQR, MAD, extremos e sinais em todos os grupos, além de confrontar listas completas e estoques conhecidos/desconhecidos. Os recortes estatísticos de A seguem os eixos all, Tcb e SrAnalitico aprovados em #175; os seis eixos de cobertura permanecem nos CSVs e nas células conjuntas.

O diagnóstico B completo passou pela revisão independente: 787.611 contribuições elegíveis, 645 contextos-base com elegíveis e 19.375 contextos de influência. Foram conferidas exatamente 3.927.994 retiradas unitárias; os 2.591 deltas indefinidos correspondem a grupos sem unidades remanescentes, sem receber razão zero. Os 23.703 pares de composição incluem 18.752 trimestrais, 4.469 entre dezembros e 482 entre extremos, com conjuntos, assinaturas, estoques e variações reconciliados.

## Sensibilidade e interpretação dos resultados

O quadro utiliza o sistema Financeiro observado completo: ponto para estoques e TTM para fluxos, seleção fixada antes da leitura dos resultados. A retirada unitária é feita uma unidade de cada vez, mantendo as demais. A maior mudança absoluta em dezembro de 2024 é uma sensibilidade determinística, sem intervalo de confiança. As variações entre dezembro de 2023 e dezembro de 2024 comparam o agregado dinâmico com o agregado restrito aos códigos presentes nas duas datas.

| Indicador | Maior mudança por retirada, p.p. | Códigos comuns 2023/2024 | Variação dinâmica, p.p. | Variação nos códigos comuns, p.p. |
| --- | ---: | ---: | ---: | ---: |
| L1 | 1,6048 | 669 | 3,7918 | 3,7761 |
| PL_DEP | 2,5771 | 901 | −0,5653 | −0,5590 |
| QL | 50,8286 | 25 | 0,5454 | 0,5730 |
| R3 | 0,8441 | 1267 | −0,2718 | −0,4479 |
| RIF_AT | 0,3737 | 1256 | 1,0512 | 1,1108 |
| E2-W | 1,2806 | 1279 | 1,6928 | 1,7755 |
| E2-WP | 1,2830 | 1279 | 1,3243 | 1,3949 |

QL exige atenção especial à concentração: uma retirada altera substancialmente a razão agregada, embora sua cobertura institucional já seja pequena. Isso não autoriza excluir a unidade, truncar o resultado ou interpretar provisão como inadimplência. R3 também apresenta diferença entre as variações dinâmica e nos códigos comuns. Essas diferenças mostram que composição e influência precisam acompanhar a comparação; não identificam causalidade ou significância estatística. Permanência do código de reporte não certifica identidade ou perímetro econômico constante.

Os 34.364 contextos de A incluem 14.989 sem unidade elegível, 2.591 com uma única unidade e 3.468 com pesos elegíveis não convexos. São ocorrências entre indicadores, janelas, coortes, categorias e datas, não frequências de instituições distintas. Quartis tipo 2, mediana, IQR e MAD descrevem a distribuição entre unidades; o agregado é razão de somas e não sua média aritmética. Extremos e sinais permanecem nas saídas, sem winsorização. O inventário privado contém 792 séries de diagnóstico e seus estados completos.

Não foram executados testes inferenciais. Uma etapa futura precisa escolher a quantidade econômica de interesse: média institucional, dispersão entre instituições ou trajetória da razão agregada. Welch e Brown–Forsythe não respondem automaticamente à pergunta sobre agregados; TTM tem sobreposição mecânica, e independência, estacionariedade ou normalidade não foram estabelecidas. Os diagnósticos não escolhem limiares, índice composto ou pesos acadêmicos.

**Resultado local aceito:** a revisão independente da apresentação conferiu as 792 séries e as cinco tabelas completas; o delta documental também foi aprovado. Publicação e integração ainda dependem do SHA/PR/CI e CI pós-merge. O explorador e a promoção controlada pertencem à #193, após aceite da base e do artefato.

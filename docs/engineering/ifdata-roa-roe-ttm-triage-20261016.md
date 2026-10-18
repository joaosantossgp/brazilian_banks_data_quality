# Triagem de ROA e ROE de 12 meses — Financeiro, 2010–2024

Data: 2026-10-16. Contrato: [Issue 144](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/144). Resultado local, sem recalcular indicadores, modificar dados aceitos ou atualizar o explorador. Janela operacional autorizada: 20–30 minutos, iniciada às 21:28 UTC. Base de código: `087700ccafa81ad96c963df62b633fb317d4ca21`, worktree `monograph-docs`.

## Conclusão e prioridade

A principal oportunidade é investigar a transição de reporte da **Caixa**, de banco individual no universo financeiro para conglomerado financeiro. A unidade atual `C0051626` fica sem ROA e ROE de 12 meses de **3T2021 a 2T2022**. Seus ativos representam **11,42%–12,13%** dos ativos conhecidos usados na cobertura nesses quatro trimestres. Há histórico anterior sob `00360305`, mas a mudança inclui composição do grupo: não foi aprovada nem aplicada uma ponte.

Não apareceu, nas dependências ausentes examinadas, valor nativo finito de lucro, ativo ou patrimônio líquido que o seletor tivesse deixado de aproveitar. Isso afasta uma correção imediata de seleção nesse recorte; não certifica todo o processamento ou a plausibilidade financeira dos valores existentes.

## Escopo e método reproduzível

Foram lidos 60 trimestres, 89.476 pares unidade–período e **178.952 resultados** de ROA/R1 e ROE/R2 de 12 meses na perspectiva Financeiro. Os seis resultados seletivos aceitos de 2019 substituem explicitamente suas posições no baseline; lacunas já corrigidas não foram recontadas. A comparação é dos resultados existentes e das dependências, não um novo cálculo de ROA ou ROE.

O diagnóstico consulta componentes e posições nativas dos relatórios admitidos, separando código sem histórico anterior, ausência interna de reporte, nulo nativo, abertura anterior ao núcleo e proteção metodológica conhecida. Contas do Resumo: lucro líquido `78187`, ativo `78182`, patrimônio líquido `78186`. Uma classificação primária organiza a triagem; uma ocorrência pode ter outras dependências problemáticas. Contagens de dependências repetidas entre indicadores não são contagens de células únicas na fonte.

Representatividade usa ativo conhecido na própria lacuna. O máximo histórico apenas ajuda a ordenar unidades quando necessário: o campo privado `max_AT_observed_other_period` significa **máximo em qualquer data observada, inclusive datas da lacuna**, apesar do nome. Não houve imputação de ativo, identidade por nome ou extrapolação de continuidade econômica.

## Dimensão das lacunas

Há **16.756 resultados sem valor**, nos mesmos pares unidade–período e com os mesmos estados primários para R1 e R2. Depois da janela inicial, são **2.943 pares unidade–período**, abrangendo **746 códigos de reporte**. Isso não significa 746 companhias diferentes.

| Causa primária | Pares unidade–período por indicador | Resultados R1 + R2 |
| --- | ---: | ---: |
| Janela inicial de 1T–3T2010, sem 12 meses completos | 5.435 | 10.870 |
| Histórico insuficiente sob o mesmo código | 1.971 | 3.942 |
| Dependência com nulo nativo | 873 | 1.746 |
| Lacuna interna de reporte do mesmo código | 59 | 118 |
| Abertura necessária em dezembro de 2009 | 37 | 74 |
| Proteção da Stone/IP já revisada em 2019 | 3 | 6 |
| **Total** | **8.378** | **16.756** |

“Antes do primeiro reporte” refere-se ao primeiro código observado no corpus admitido. Não prova que a instituição nasceu naquela data ou que o negócio não existia. A Caixa demonstra por que mudanças de código/perímetro precisam ser distinguidas da entrada econômica de uma instituição.

## Caso prioritário: Caixa

O cadastro autenticado em 4T2020, 1T2021 e 2T2021 contém o banco `00360305`, sem conglomerado financeiro associado, com líder `00360305` e conglomerado prudencial `C0080738`. Em 3T2021 passam a aparecer:

- conglomerado financeiro `C0051626`, com o mesmo líder;
- banco `00360305` ligado ao conglomerado financeiro;
- Caixa DTVM `42040639`, também ligada ao conglomerado, com início de atividade cadastrado em `202109`.

Os relatórios financeiros nativos têm LL/AT/PL sob o código do banco até 2T2021 e sob o conglomerado em 3T2021. Logo, existe história anterior aproveitável **como candidata a uma ponte**, mas a identidade do líder não basta para certificar equivalência de perímetro, fluxos ou estoques. A data de início cadastral da DTVM é evidência datada, não uma certificação independente de todas as operações do grupo.

| Trimestre afetado | Cobertura atual de ativos conhecidos — ROA e ROE | Participação da Caixa nos ativos conhecidos |
| --- | ---: | ---: |
| 3T2021 | 87,14% | 12,13% |
| 4T2021 | 87,81% | 11,85% |
| 1T2022 | 88,05% | 11,80% |
| 2T2022 | 88,46% | 11,42% |

Em 2T2021 a cobertura era 99,36%; em 3T2022 volta a 99,86%, com a Caixa elegível. São coberturas observadas, não uma estimativa contrafactual de rentabilidade. Se uma ponte for fundamentada e aceita, seu potencial é recuperar até a participação de ativos indicada; a recuperação não foi realizada ou garantida.

A conferência das 120 coberturas período–indicador reproduziu o explorador. Usa ativo nativo conhecido **e cadastro contemporâneo disponível**, conforme a regra já aceita. Posições sem cadastro datado não recebem participação mesmo quando há um token de ativo. A conferência usa frações exatas; percentuais são apresentação. Não houve mudança dessa regra.

## Demais casos e possibilidade de resolução

| Prioridade / caso | Janela afetada | Evidência e encaminhamento |
| --- | --- | --- |
| **1 — Caixa** | 3T2021–2T2022 | Mudança banco → conglomerado; até R$ 1,49 trilhão de AT nas datas afetadas. Conferir toda a transição de perímetro e componentes antes de decidir ponte. Potencial elevado; resolução condicionada. |
| **2 — BNP Paribas, `01522368`** | 3T2023–2T2024 | Até R$ 102,55 bilhões de AT. Antes, banco pertencia a `C0051516`, cujo grupo incluía Cetelem `00558456`; depois aparece sem conglomerado financeiro. Mesmo líder, composição diferente: ponte conglomerado → banco exige cautela e ainda não foi aceita. |
| Cielo / Redecard | 4T2017–3T2018 | Máximos de AT nas lacunas de R$ 88,62 / 64,28 bilhões. Histórico anterior insuficiente sob esses códigos; início no corpus não demonstra nascimento econômico. Verificar disponibilidade/perímetro anterior em lote se o ganho justificar. |
| XP, `C0052120` | 4T2019–3T2020 | Até R$ 66,26 bilhões de AT. Histórico insuficiente do código de conglomerado; possível continuidade ainda sem demonstração. |
| Nubank, `C0052058` | 4T2019–3T2021 | Dependências nulas nativas; há datas sem AT conhecido. Resolver exige esclarecer divulgação ou fonte alternativa. Não substituir nulo por zero. |
| BRB | 3T2022–3T2023 | Cinco trimestres afetados por dependências. **Estacionado por decisão de João**, sem ampliar busca nesta triagem. |
| Lacunas internas de outros códigos | Janelas próprias no CSV | Original, Stone, XP corretora e outros. Confirmar mudança de código/perímetro ou reporte antes de buscar fora. Menor prioridade que Caixa. |
| Janela inicial / abertura de 2009 | 1T–3T2010 e aberturas específicas | Depende de história anterior ao núcleo ou alteração explícita da janela. Não é reparo simples de um resultado e não justifica modificar a regra nesta tarefa. |
| Proteção Stone/IP de 2019 | 1T–3T2019 | Preservar exceções já revisadas; esta triagem não apresenta nova evidência para removê-las. |

Na seleção histórica usada nos resultados atuais, além do BRB, aparecem lacunas dos códigos de BR Partners e DMCARD por histórico insuficiente. Essa seleção corresponde ao recorte anterior das 24 companhias/20 unidades financeiras. A seleção posterior estudada nas Issues 142/143 não foi retroprojetada sobre resultados já calculados.

O próximo recorte recomendado é **somente Caixa, com toda a janela e abertura necessárias**, para avaliar uma ponte econômica/contábil e seu limite de perímetro. O diagnóstico já justifica essa prioridade, sem esperar a revisão de novos indicadores. A adoção de ponte exige fundamento e decisão metodológica; nenhum preenchimento automático é conclusão desta nota.

## Evidência, limites e revisão

Entradas privadas em `data/curated/`, sem alterações:

- baseline `ifdata-universe-analysis-20261014-final-run3`, manifest SHA-256 `b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`;
- financeiro nativo `ifdata-odata-20261011/financial`, manifest `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095`, 60 partes verificadas;
- cadastro `ifdata-cadastro-20261011`, manifest `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1`;
- mapa de unidades/ativos do diagnóstico L2, manifest `bc1e41dad042c2a9f19f917533f48137931ef61f50db833e5591ceff65409889`;
- seis overlays financeiros R1/R2 em março, junho e setembro de 2019, hashes individuais registrados no recibo da triagem.

Artefatos privados na pasta de visualização `2026/10/13/01a1361f-f20f-7f23-b187-beee4d316e48`: `triar-roa-roe-ttm.py`, cinco CSVs `ttm-triage-144-{gaps,dependencies,priority,windows,counts}.csv`, recibo JSON, `conferir-transicoes-144.py`, probe JSON de transições e JSON de cobertura. O produtor principal, SHA-256 `550e6b08747d980ce7b1abaf137fc05e9361b1030324707c8be48fc12bf17c8a`, levou 58,03 segundos. O orçamento da tarefa inclui inspeção, interpretação, documentação e revisão, além dessa consulta.

Revisões independentes A e B/final: **PASS, sem achado material**. A ressalva de nomenclatura do máximo de AT foi incorporada acima; a revisão final conferiu as transições, os pares ausentes, as frações de cobertura e a allowlist. `git diff --check` passou e os hashes protegidos do núcleo, perfil, nota de benchmark e HTML permanecem iguais aos da entrada. Esta entrega cria somente esta nota pública; nenhum código, perfil, resultado financeiro ou HTML foi modificado. A pesquisa da [Issue 143](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/143) pode continuar em paralelo no checkout principal, com destinos próprios de indicadores por atividade. Não houve commit, PR, coleta externa ou alteração de método acadêmico.

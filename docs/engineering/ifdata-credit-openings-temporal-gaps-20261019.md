# Aberturas de crédito IF.data e lacunas temporais de N1/N2

[Pesquisa196](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/196), autorização de João em19/10/2026, incluindo ingestão organizada mínima e aproveitamento para outros indicadores e análises. [Proveniência e reprodução](ifdata-credit-openings-temporal-gaps-20261019.provenance.md). Owner e integrador: Root, execução in-line; revisão independente somente leitura.

## Resultado para fechar o conjunto

**Não é necessário buscar uma fonte externa para obter as oito aberturas de crédito examinadas.** Os relatórios7–14 já estavam nos brutos oficiais preservados em11/10; estavam fora da importação contábil. O importador existente incorporou **15.373.438 linhas** em pacote novo, em240,61segundos, sem mudar código, fórmulas, indicadores, perfis, explorador ou ponteiro. Isso é ingestão técnica aceita após revisão; não é adoção de indicadores novos.

As aberturas permitem analisar composição do crédito reportado noSCR e preparar indicadores por risco, modalidade, prazo e concentração setorial/geográfica. Não resolvem sozinhas inadimplência90+, cobertura deNPL, liquidez por vencimentos dos dois lados do balanço ou as falhas históricas de lucro/ativo médio deN1/N2. Dados disponíveis não tornam toda razão calculável ou economicamente equivalente ao crédito contábil.

Para evitar atrasar o início da análise, recomenda-se conservar o conjunto já adotado e suas condições por atividade; incorporar estas aberturas como base técnica e explicativa; selecionar qualquer nova medida somente após sua disponibilidade conjunta no universo-alvo. Não foi adotado limiar de cobertura, exclusão de unidades, imputação ou substituição de janela. Uma lacuna de atividade não deixa de existir porque não foi escolhida uma razão inadequada.

## O que entrou e como acessar

Raiz privada compartilhada neste computador: `data/curated/ifdata-credit-openings-20261019-full/`, no checkout principal. Dois pacotes do contrato existente `ifdata-odata-parquet-v1`, sem novo leitor:

| Pacote | Seleção nativa | Períodos observados | Linhas | SHA-256 do manifest |
|---|---|---|---:|---|
| `core/` | Tipo2, relatórios7–14 | 42datas,201409–202412 |14.984.990|`b69fbcbe68cc38168403bc60a147dc761c444c507d22021db2e1e573baa255d2`|
| `early/` | Tipo2,7,8,10–14 |201406|388.448|`246ec46328821041ae676f601393064c6e1b8eb5324a129ce3552e422862b86d`|

`receipt.json` identifica ambos os manifests, seleção, origem e comandos. Separar a primeira data evita enfraquecer o contrato do importador: o relatório9 não aparece em201406. Todos os16campos permanecemVARCHAR; `Saldo` conserva lexemas, null, vazio, zero e negativos. As43partes foram autenticadas e343contagens relatório×data reconciliadas com os brutos. Não houve duplicação de chaves identificadas completas. **3.350linhas da fonte têmCodInstnull**: preservadas como ocorrências sem identidade, sem agrupá-las como uma instituição nem atribuir coorte/companhia.

| ID | Abertura | Pergunta financeira ou analítica | Limite imediato |
|---|---|---|---|
|7|Indexador|A que indexadores está exposto o crédito reportado?|Composição de indexadores não mede descasamento de juros sem financiamento/reprecificação.|
|8|Nível de riscoAA–H|Como se distribui o crédito entre classificações de risco?|Classificação não equivale a atraso; disponibilidade conjunta varia porTcb.|
|9|Região|Como se distribui geograficamente o crédito?|Região da operação não é sede da instituição; não mede concentração por devedor.|
|10|Clientes e operações|Quantos clientes/operações são reportados?|Contagens não são aditivas entre instituições como clientes únicos do sistema.|
|11|PF: modalidade e vencimento|Qual o perfil da carteiraPF, seus vencimentos e atraso publicado?|Componentes nulos impedem somas completas; atraso publicado é≥15dias.|
|12|PJ:CNAE|Qual a concentração por setor do tomador?|CNAE do tomador não reintroduzAtividade como filtro da instituição.|
|13|PJ: modalidade e vencimento|Qual o perfil de prazo/modalidade da carteiraPJ?|Mesmos cuidados de total, sigilo/nulos e perímetro doSCR.|
|14|Porte do tomadorPJ|Como varia a exposição por porte do cliente?|Porte do tomador não éSr nem tamanho da instituição.|

Cada abertura conserva contas, grupos, descrição, período e proveniência nativos. Foram inventariados269contextos de variáveis; a quantidade não certifica estabilidade semântica. Os dados continuam separados do conjunto de resultados dos indicadores. O [protocolo metodológico](institution-type-indicator-methodology-20261012.md) e as decisões da[Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) continuam valendo.

## Oferta histórica: API, bruto e navegador são evidências diferentes

A [metodologia oficial](https://www3.bcb.gov.br/ifdata/index.html) anuncia crédito financeiro/SCR de201206a202412. Na captura local autenticada de60datas201003–202412, as aberturas7,8,10–14 sobTipo2 aparecem somente desde201406; região9 desde201409. Consultas atuais de8/Tipo2 em201206e201203 retornaram arrays vazios, sem erro de transporte. Isso descreve a rota/data/tipo consultados, não ausência universal doIF.data.

O navegador oficial, em[index2024.html](https://www3.bcb.gov.br/ifdata/index2024.html), oferece em06/2012 uma opção específica **Conglomerados Financeiros e Instituições Independentes(SCR)**. O CSV de risco foi baixado e preservado:1.697linhas institucionais datadas e27linhas de seções/agregados após o cabeçalho, escalaR$mil, códigos de exibição do portal. O arquivo contém1.724linhas após o cabeçalho; esse número inclui as seções de agregadosTD/TCB/TC e não é uma contagem de instituições. A interface virtualizada informou1.701itens; a relação exata com esse contador ficou não certificada. O arquivo é piloto de acesso, **não foi emendado aOData ou ligado por nome/padding de códigos**.

Assim, a extensão anterior a201406 continua possível dentro doIF.data, mas requer conciliação da rota, namespace, escala e perímetro. Não é falta comprovada de fonte externa nem tarefa concluída de integração histórica. Para acelerar, a importação aceita do trecho local não ficou bloqueada por essa extensão.

O relatório aberto no portal também informa mudança do valor mínimo de operações individualizadas noSCR: R$1.000 até05/2016 eR$200 desde06/2016, além de tolerância/divergências em relação aos demonstrativos contábeis. Essa fronteira importa para comparações históricas de carteira, clientes e operações; não preencher a parte anterior com zeros.

## Piloto de viabilidade econômica:4T2024, sistema inteiro

Os oito relatórios contêm1.422códigos cada um nesse corte, mas isso **não significa1.422carteiras informadas**. Das366.876linhas do piloto,203.572têmSaldo null,53.871zero,109.349positivo e84negativo. Negativos são preservados para diagnóstico, não automaticamente corrigidos. Nenhum nulo foi convertido emzero.

Contas centrais: risco total24454; faixas23349–23357; exterior23383; totalPF24452; totalPJ24453. O totalSCR exclui carteiras adquiridas com retenção de risco por outra instituição, conforme descrição nativa. Não adicionarTotalExterior novamente sem demonstrar sua relação com o total. A escalaOData é mantida conforme o contrato localBRL, separada doCSVportalR$mil.

| Tcb | Unidades com totalSCR conhecido e positivo | Com as nove faixasAA–H disponíveis | CréditoSCR conhecido positivo coberto por essas unidades |
|---|---:|---:|---:|
|B1|89|53|98,32%|
|B2|26|13|78,40%|
|B3S|752|439|88,72%|
|B3C|20|0|0,00%|
|B4|4|4|100,00%|
|N1|189|22|27,61%|
|N2|1|0|0,00%|
|N4|35|5|2,14%|

O denominador dessa cobertura é o créditoSCR **conhecido e positivo**, porTcb; não éAT, crédito contábil nem total econômico desconhecido. O alvo é explicitamente esse subconjunto de carteiras; códigos presentes com total nulo ouzero não são carteira positiva observada. Há536unidades com total positivo e todas as nove faixas. Isso justifica estudar a distribuição onde há cobertura; não certificar cobertura integral deN1/B3C/N4 nem interpretar suas ausências como não aplicabilidade.

Uma razão geral de atraso≥15dias baseada na soma estrita das16modalidadesPF/PJ e seus totais positivos tem componentes completos em **apenas10unidades, todasB1**, nesse corte. Não é candidata pronta a indicador comum do sistema. A presença de uma conta de atraso não resolve automaticamente a qualidade do crédito para cada atividade. Não substituir90dias por15dias silenciosamente nem somar somente modalidades informadas como se fossem a carteira inteira.

Verificações aritméticas do piloto:PF+PJ coincide exatamente com total de risco em1.409casos; nos536com nove faixas,516somas coincidem exatamente e20diferem. Estas20divergências permanecem diagnósticas; não foram classificadas como erro ou corrigidas por tolerância inventada. Comparando totalSCR e crédito contábil78191 nos1.406casos conjuntamente disponíveis,572são exatamente iguais e834diferem. Portanto, não usar provisão contábil/SCR como cobertura certificada sem conciliar os universos. Igualdade numérica também não prova equivalência conceitual.

## N1/N2: qual lacuna foi investigada e o que é recuperável

O ponto de partida foi o diagnóstico da[Pesquisa176](data-readiness-diagnostic-20261018.md), reaproveitado criticamente. Consulta às tabelas aceitas, sem recálculo financeiro:20métricas/26combinações métrica–janela,1.092contextos porcoorte,3.005observações unidade×trimestre deROA/TTM e21reconciliações exatas comTcb total. O aprofundamento causal foi **R1/TTM**; a seleção paraR2 não cobre suas falhas exclusivas e não permite alegar diagnóstico causal exaustivo de todos os indicadores.

| Recorte inteiro | Menor coberturaAT conhecido emR1/TTM | Causa demonstrada e remediabilidade |
|---|---|---|
|N2,4T2016–4T2018|27,63% em4T2018|XP sobC0051994 tem nulos nativos em parte do histórico;02332886 não tem linhas financeiras nas datas de abertura necessárias. Em4T2018,LLTTM está disponível, mas faltaAT de4T2017 sob esse código. Outra conta do trimestre final não recompõe oATmédio.|
|N2,3T2022–1T2024|34,33% em2T2023|WarrenC0052333, S3Caceis62318407 eVórtxC0052364 têm históricos insuficientes sob os códigos reportados nas janelas. Warren em2T2023 exigeAT de2T2022 ausente sob o mesmo código. Recuperação por código predecessor exigiria prova temporal/perímetro; não é mero remapeamento de rubrica.|
|N1,4T2020–4T2021|56,64% em3T2021|NubankC0052058 tem nulos nativos em componentes de2020 que afetamTTM posterior; MercadoCrédito37679449 não tem linhas sob o código nas datas anteriores necessárias. Pefisa43180355 tem dados correntes e faltas históricas; não confundir entrada da unidade com falha do trimestre final.|

Foram356resultadosR1/TTM indisponíveis nessas janelas:266`binding_missing` e90`native_null`. A decomposição identificou320coordenadas distintas código×data combinding ausente: **nenhuma possui linha noFinanceiro contábil local sob o mesmo código/data**. Outras65coordenadas de inputs separam nulos. Números são ocorrências/coordenadas, não356ou320companhias. As faltas de fluxo e estoque podem coexistir no mesmo resultado.

As contas equivalentes deResumo/Ativo/DRE foram conferidas nos casos nativos centrais: Nubank202009 eXP/C0051994 em201609 têmAT/LL nulos também nas respectivas aberturas. Não se demonstrou recuperação imediata desses casos pela escolha de outra coluna do mesmo perímetro. A fonte pode conter história sob outra unidade, mas ligá-la exige evidência; não usarIndividual/Prudencial como substitutoFinanceiro nem buscar demonstração societária como se mantivesse automaticamente o perímetro.

**Conclusão delimitada:** as novas aberturasSCR ampliam o crédito, mas não preenchem lucro/ATmédio históricos. Não há correção simples demonstrada para os grandes casos examinados dentro do mesmo código financeiro local. Eventual continuidade entre códigos, recuperação pelo portal ou fonte adicional é uma investigação separada, somente para o trecho dependente. Não foi reabertoBRB.

## Sequência curta recomendada

1. Começar a análise dos indicadores já adotados, com cobertura porcategoria/período visível e painel desbalanceado. Não apresentarN1/N2 nas janelas críticas como população integral; conservar faltas, composição e unidades nominais explícitas.
2. Usar imediatamente as aberturas importadas para caracterizar carteira, prazo, indexador e setores, respeitando nulos e mudanças de oferta/definição. Não exigir todas as aberturas em cada observação para qualquer análise.
3. Se for acrescentada uma medida de risco, começar por um piloto específico emB1/B4 e avaliarB3S/B2; conferir a história e decidir a fórmula antes do cálculo. A foto4T2024 não autoriza cobertura histórica nem adoção universal. Não lançar agora uma razão geral deatraso15dias com cobertura de10unidades.
4. Manter como extensões as fontes externas de liquidez específica e as pontes entre códigos. Só o recorte que depende delas fica limitado; não bloquear todos os indicadores e toda a monografia esperando por esses complementos.

Há uma decisão acadêmica de fechamento, não uma necessidade de novo framework: quais complementos entram no núcleo e quais ficam como interpretação/extensão. Esta pesquisa fornece a viabilidade; mantém a decisão comJoão/orientador. A[Issue193](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/193) conserva seu gate visual próprio, sem promoção do ponteiro por esta entrega.

## Verificação, revisão e limites

Revisões independentes liberaram pilotoAPI, investigação decomponentes, importação seletiva e sua expansão. A revisão do pacote final confirmou os dois manifests e43hashes, contagens343, precisão e identidade desconhecida preservada. A composição documental é conferida independentemente no SHA entregue; estado remoto, checks e encerramento ficam naIssue196.

Checks pertinentes: hashes/schema/contagens/uniquidade identificada, tokens/nulos, disponibilidade conjunta,21reconciliações e fontes/localizadores. Não rodar suíte integral de software para duas notas sem alteração de código. Tentativas falhas e correções do diagnóstico estão preservadas na proveniência. Nenhuma equivalência econômica, recuperação histórica ou cobertura integral decorre apenas dePASS técnico.

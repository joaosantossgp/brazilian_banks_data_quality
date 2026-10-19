# Quatro sensibilidades de Assaf — piloto de 18/10/2026

Entrega da [Issue189](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/189), após a [auditoria181](tcb-indicator-input-readiness-20261018.md). João escolheu explicitamente as quatro métricas na [decisão da3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6258035046). Foram implementadas e verificadas em um piloto do sistema completo; não houve expansão aos60trimestres, composição final192ou atualização do explorador193.

## Métricas e perguntas

| ID e nome | Fórmula, exibida em% | Financeiro Tipo2: componentes | Fonte conceitual e limites |
|---|---|---|---|
|L1, encaixe voluntário|100×DISPt/DVt|Ativo2/78188;Passivo3/78282|Assaf2015,11.ed.,p.334. Compara disponibilidades com depósitos à vista; não resolve liquidez de desenvolvimento, IP ou intermediário semDV.|
|R3, margem sobre receitas de intermediação|100×LLw/RIFw|Resumo1/78187;DRE4/78208|Assafp.341; margem específica de intermediação, sem serviços e demais rendas no denominador. Não é margem sobre toda receita operacional.|
|RIF_AT, lucratividade dos ativos pela receita de intermediação|100×RIFw/ATmédiow|DRE4/78208;Resumo1/78182|Assafp.342, adaptação para média temporal. Mede receita selecionada em relação ao ativo, não retorno líquido, NIM ou spread contratual.|
|PL_DEP, capital sobre depósitos|100×PLt/DEPt|Resumo1/78186;Passivo3/78287|Assafp.337. Capital contábil em relação aos depósitos, sem equivalência com PR/RWA ou capital principal.|

Fontes reaproveitadas da [leitura178](tcb-indicators-assaf-atlas-20261018.md) e da [proveniência111](financial-dimensions-literature-20261014.provenance.md); não se afirma nova leitura dessas páginas nesta implementação. As adaptações temporais e o desenho permanecem no [plano aprovado](../superpowers/plans/2026-10-18-tcb-indicators.md). Os IDs IF.data não são códigos Cosif.

L1 e PL_DEP usam estoques na mesma data. R3 e RIF_AT usam trimestre efetivo ou TTM de quatro trimestres disjuntos; os fluxos nativos respeitam reset semestral. AT médio usa pontos trimestrais, abertura e média trapezoidal ponderada por dias. Não houve anualização por multiplicação por4 ou soma de estoques.

Aplicabilidade técnica de L1/PL_DEP exige DV/DEP positivos, sem inferir adequação econômica universal. Zero deixa o cálculo indefinido; denominador negativo mantém a fração assinada/alerta e aplicabilidade desconhecida. Null, binding ausente, falta de abertura e incompatibilidade de definição permanecem estados próprios. PL negativo é preservado em PL_DEP com alerta `negative_equity`; RIF negativo permanece assinado. Esses alertas não são regras acadêmicas de exclusão.

Tcb orienta o modelo, refinado porSegmentoTb, composição/data/perímetro. L1/PL_DEP explicam a função depositária onde observada; R3/RIF_AT ajudam a decompor a geração de renda, mas podem representar mal uma operadora de serviços quando a intermediação é pequena. Tc/Td/Sr e SrAnalitico permanecem estratos/contextos, não geradores de outras fórmulas. Atividade continua fora dos filtros. Nenhuma unidade foi retirada da população por um indicador não calculável.

## Implementação seletiva e entradas

O registro complementar e os ramos existentes de `evaluate_metric` receberam os quatro IDs; a lista histórica `METRICS` e o perfil JSON instalado foram preservados. A compilação aditiva inclui RIF como fluxo, com Conta78208/DRE4 e descrição literal de somatório de rendas; Grupo/NomeColuna completos vêm do catálogo autenticado. O contexto precisa corresponder à própria perspectiva e cobrir as60referências; ambiguidades ou mudanças não aprovadas interrompem. Não existe outro motor, módulo, camada ou dependência.

O produtor `calculate-complements` já aceita seleção explícita de métricas/períodos; não foi necessária mudança da CLI. A revisão do código ocorreu antes dos lotes, com hashes dos quatro arquivos fixados no instrumento privado. Root é o único writer de core desta fatia, na branch de integração `codex/tcb-research-182-188`, base `ef192beb2d80693be1b07cc074fed245acb05359`.

Ponteiro vigente redescoberto e autenticado: composição `historical-links32-composition-20261018-run3`, manifest `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`. A origem das observações na tabela autenticada conduz ao baseline técnico `ifdata-universe-analysis-20261014-final-run3`, pin `b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`, requerido pela operação existente. A escolha foi rastreada pela proveniência, não por data/nome de pasta.

Os novos pacotes mantêm membership/companies desse baseline técnico, como prevê o produtor. A cobertura apresentada foi calculada por junção dos valores persistidos com a unidade/data e os vínculos da composição vigente, sem reavaliar as razões. Isso é diagnóstico: o remapeamento nos pacotes finais pertence à192. Não afirmar que o piloto persistido já é a composição das32companhias.

| Pacote privado novo | Escopo | Componentes | Resultados/cobertura | Manifest SHA-256 |
|---|---|---:|---:|---|
|`tcb-piloto-sensibilidades-20261018-run1-stock`|L1/PL_DEP,202412|7.110|2.844|`f5c88c837a34fe42e1023f6854648f6acf2d4d380f31c3d5ec3ab85af2d6d47e`|
|`tcb-piloto-sensibilidades-20261018-run1-flow`|R3/RIF_AT,201812/201903/202412,quarter/TTM|45.804|16.496|`49aeba38d8da7440dc16d5d59edb5d9fcc3db64b712a73a5f3396e5e24e34c40`|

Destinos relativos a `data/curated/` compartilhada, sem sobrescrever aceitos. Tempo:5,953sestoques e24,172sfluxos. As partições nativas e manifests foram autenticados pelo produtor; o recibo conserva origem/pins, inventário e snapshot do código. Não houve nova coleta.

## Cobertura real e fronteira2019

| Indicador/janela |201812elegíveis/esperadas|201903elegíveis/esperadas|202412elegíveis/esperadas|
|---|---:|---:|---:|
|L1pontual|Não selecionado|Não selecionado|676/1.422|
|PL_DEPpontual|Não selecionado|Não selecionado|969/1.422|
|R3trimestral|1.345/1.357|1.335/1.345|1.377/1.422|
|R3TTM|1.342/1.357|0/1.345|1.341/1.422|
|RIF_ATtrimestral|1.348/1.357|1.332/1.345|1.391/1.422|
|RIF_ATTTM|1.342/1.357|1.325/1.345|1.336/1.422|

Em L1/202412,739denominadoresDVzero e7null; em PL_DEP,446DEPzero e7null. Isso não demonstra inadequação de toda a dimensão de liquidez/capital a essas unidades. Os tipos não depositários continuam com LA/LC/LF e pesquisas específicas.

R3/TTM/201903 não foi liberado:1.330incompatibilidades de definiçãoLL,14bindings ausentes e1null. As pontes anteriores de lucro não foram estendidas a esta métrica por analogia. O trimestre de201903 permanece calculável em1.335unidades; TTM exige contrato explícito de compatibilidade antes de mudar esse resultado. O piloto não disfarça essa lacuna como ausência de atividade ou resultado zero.

As listas privadas contêm todas as19.340linhas nominais e294células por indicador/janela/data/Tcb/coorte, com nomes, códigos, companhias e todos os eixos cadastrais separados, estados/flags e frações de AT/crédito/PL conhecidos e elegíveis. Os estoques desconhecidos têm contagens próprias. Em202412a população vigente é24sample+1.398remaining;55companhias nominais permanecem no roster181. Cobertura sobre estoques conhecidos não estima o estoque das unidades sem informação ou elimina sobreposição econômica de conglomerados.

## Verificações e revisão

TDD observado: testes focados inicialmente falharam por `unknown_metric` e bindingRIF ausente; após a adição mínima passaram. Frações1/4,−1/4e1/10, trimestre/TTM, zero/null/negativo, definiçãoLL incompatível, abertura ausente e janela errada são exercitados. Uma primeira fixture de teste tinha argumento duplicado; foi corrigida antes do RED causal. A primeira chamada ampla foi interrompida e permanece distinta de PASS; a execução integral posterior concluiu115testes em224,885s, com1skip, e a suíte seletiva34testes em31,248s.

Comparação determinística antes/depois:20métricas antigas,28avaliações sintéticas completas em suas janelas, com payloads idênticos. Essa prova é sintética, não recálculo de toda a base. Todos os hashes das nove tabelas da composição aceita também conferiram após o piloto; os lotes selecionaram somente os quatro novos IDs.

Revisor independente `review_189_code`: código aprovado antes do lote, condicionado aos testes posteriormente satisfeitos. Na revisão real, confrontou todos os52.914componentes com tokens/contextos nativos e rederivou os16.459resultadosOK com aritméticaFraction independente, incluindo N/D, fluxos e média por dias. Inventários e estados de todas as unidades conferidos. Na cobertura vigente, rederivou todas as19.340linhas/294células, contagens/flags e somas exatas dos estoques. Nenhum achado material no resultado; a nota e o SHA entregue têm conferência própria na Issue.

Preparação privada `.scratch/tcb-piloto-sensibilidades/`: logsRED/GREEN, comparador de preservação, pins, runner, recibos, cobertura e listas nominais. Dados privados não vão aoGit. A arquitetura reaproveita os módulos, testes e destinos existentes, sem rename/delete; a CLI não mudou. Nenhum ponteiro ou explorador foi promovido. Antes da ampliação histórica e da composição192, conservar as séries separadas, revisar os períodos/pontes realmente liberados e aplicar o protocolo de diagnóstico pertinente às novas métricas, sem refazer os20indicadores antigos.

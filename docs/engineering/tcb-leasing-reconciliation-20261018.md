# Arrendamento: carteira, provisão e renda — 18/10/2026

Pesquisa da [Issue183](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/183), baseada na [entrada autenticada181](tcb-indicator-input-readiness-20261018.md). Abrange o sistema Financeiro Tipo2 em2010–2024, com Tcb/SegmentoTb próprios. A carteira não é atribuída apenas aN1; bancos e conglomerados com leasing permanecem no inventário. Nenhuma fórmula foi adotada ou calculada.

## Conciliação patrimonial

| Campo IF.data, Ativo2 | Contexto e definição literal | Interpretação delimitada |
|---|---|---|
|78194, Arrendamento Mercantil a Receber(e1)|Grupo Arrendamento Mercantil; `[17000000]-[17900007]`|Recebíveis antes da provisão179; não equivale a todos os ativos de leasing ou ao principal contratual não descontado.|
|78195, Imobilizado de Arrendamento(e2)|Mesmo grupo; `[23000001]`|Componente patrimonial distinto dos recebíveis.|
|78196, Credores por Antecipação de Valor Residual(e3)|Mesmo grupo; `[49908008]`|VRG, com sinal nativo; não é carteira de crédito.|
|78197, Provisão sobre Arrendamento Mercantil(e4)|Mesmo grupo; `[17900007]`|Provisão assinada do subgrupo; não é estoque inadimplente.|
|78198, Arrendamento Mercantil Líquido de Provisão(e)|Mesmo grupo; `[17000000] + [23000001] + [49908008]`|Agregado líquido, não denominador bruto alternativo escolhido por disponibilidade.|
|78196, Credores por Antecipação de Valor Residual(j)|Grupo nulo; `[49908008]`|Segunda apresentação do mesmo código; contexto separado.|

Pela álgebra das definições, o confronto é `78198 −(78194+78195+78196(e3)+78197)`. Provisão e VRG entram com os sinais da fonte; não se subtrai novamente o valor absoluto da provisão nem se somam as duas apresentações de78196. A auditoria conserva os resíduos exatos, sem tolerância. A disponibilidade da identidade patrimonial exige apenas os cinco estoques, separada da disponibilidade da DRE.

Nos88.782conjuntos finitos do histórico, os dois contextos de78196 apresentam valores iguais. Isso é uma conciliação empírica e literal destes dados, não autorização para ignorar Grupo/NomeColuna em outras contas ou novos regimes. Há resíduos pequenos, porém não nulos, na identidade patrimonial; o máximo na conferência primária amostral foi3/1.000.000.000de real. Todos permanecem no inventário.

## Renda e despesas têm abrangência própria

| Campo IF.data, DRE4 | Grupo | Definição |
|---|---|---|
|78204, Rendas de Operações de Arrendamento Mercantil(a2)|Resultado de Intermediação Financeira - Receitas de Intermediação Financeira|`[71200004]+[81940000]`|
|78211, Despesas de Operações de Arrendamento Mercantil(b3)|Resultado de Intermediação Financeira - Despesas de Intermediação Financeira|`[81300004]+[81830550]`|

Portanto78204 já contém a parcela8194, uma despesa de cessão de créditos de arrendamento, no sinal nativo. Não é uma receita contratual bruta pura. A [compilação histórica Cosif2024, função8.1.9.40.00-0, PDFp184](https://www3.bcb.gov.br/aplica/cosif/manual/funcoes-2024-historico.pdf) permite identificar essa natureza; a mesma compilação, funções1.7.9.30/35/40/50/80, PDFpp31–32, separa provisões de modalidades de arrendamento. Ela documenta a versão histórica2024, não prova por si só vigência uniforme em2010–2024.

O [manual oficial Cosif, operações de arrendamento, seções10 e11](https://www3.bcb.gov.br/aplica/cosif/manual/09021771869a1a0f.htm) distingue antecipação do VRG e provisionamento; a base normativa de provisão envolve valor presente das contraprestações. A página é uma compilação consultada em19/10/2026UTC: as referências a normas históricas não constituem uma cronologia regulatória completa. O acesso à seção de avaliação patrimonial adjacente retornou502, preservado na proveniência; não se preencheu o trecho por suposição.

Assaf Neto, *Estrutura e análise de balanços*,11.ed.,Atlas,2015, pp.321–322 e324: releitura visual do exemplar privado, PDF342–343/345. O autor distingue recebíveis, provisão e estrutura da DRE; essas páginas sustentam os conceitos, não uma fórmula específica de leasing apresentada como sua. Identificação/hash do exemplar reaproveitados da [proveniência111](financial-dimensions-literature-20261014.provenance.md), sem nova autenticação do PDF completo. O retorno médio do crédito da p.342, reaproveitado da178, não é transplantado automaticamente.

## Proposta implementável e lacuna demonstrada

**QL, intensidade de provisão sobre recebíveis de arrendamento**, candidata: `100×(−78197t)/78194t`. Pergunta: quanto de provisão contábil existe em relação aos recebíveis antes da provisão, na mesma unidade/data? Dimensão de proteção/qualidade da exposição; adaptação própria, Financeiro/Ativo2/mesmo grupo. Não mede NPL, perda realizada, probabilidade de default ou suficiência regulatória. O denominador ainda reflete os demais critérios contábeis do subgrupo170, incluindo retificadoras como rendas a apropriar; chamá-lo de carteira contratual nominal seria indevido.

Aplica-se à exposição observada, inclusive emB1/B2/N1, refinada porSegmentoTb e composição, sem classificar todaN1 como leasing. Recebível positivo com provisão zero admite resultado zero; recebível zero deixa a razão indefinida, sem concluir não aplicabilidade. Null/ausência são estados de dados; denominador negativo e provisão positiva/reversão permanecem assinados e sinalizados, sem leitura ordinal automática. Estoque pontual, sem média ou anualização. Agregação futura=Σ(−provisão)/Σrecebíveis na mesma interseção válida, com contagens/AT-crédito-PL conhecidos e distribuição; não agregar com Q1crédito numa razão mista.

**Rendimento de leasing: não está fechado para implementação.** O inventário prova componentes existentes, mas não a correspondência entre toda renda78204 e78194 isolado. Imobilizado, VRG, cessões e modalidades participam de forma distinta. As33unidades com recebíveis+imobilizado positivos em2024 não são o mesmo conjunto das27com recebíveis positivos. Usar a menor carteira para aumentar o retorno ou somar estoques sem critério econômico produziria uma métrica inadequada.

O próximo recorte mínimo, se rendimento for escolhido, é conciliar separadamente receitas de arrendamento financeiro/operacional, cessões, despesas e estoque produtor correspondente por modalidade; conferir rendas a apropriar, depreciação e VRG em notas/dados próprios. Só depois escolher receita/estoque médio ou resultado específico/estoque médio. Não foi inventada uma razão para completar rentabilidade: ROA/ROE e composição de resultados permanecem disponíveis, com sua interpretação contábil própria.

## Cobertura do universo e listas nominais

Auditoria integral:89.476unidades-trimestre,60referências;88.782conjuntos finitos de carteira+DRE, coincidentes com os conjuntos patrimoniais finitos nesta base. Coortes financeiras no período:1.401sample,88.031remaining e44unknown; são ocorrências temporais, não companhias distintas. Classificações ausentes e vínculos desconhecidos não foram removidos.

| Tcb,202412 | Esperadas | Conjunto de componentes finito | Recebíveis positivos | Recebíveis+imobilizado positivos |
|---|---:|---:|---:|---:|
|B1|97|97|15|16|
|B2|31|31|8|12|
|B3C|29|27|0|0|
|B3S|753|753|0|0|
|B4|4|4|0|0|
|N1|226|224|4|5|
|N2|136|135|0|0|
|N4|146|144|0|0|

Essa tabela de disponibilidade não é cálculo de QL ou teste de aplicabilidade. Sete unidades no corte têm null, não valor financeiro zero. As listas privadas identificam todas as unidades e companhias associadas, os positivos/zeros/negativos/null/ausentes de cada componente, Tcb/SegmentoTb/Tc/Td/Sr/SrAnalitico, estoques conhecidos/desconhecidos e a interseção de recebíveis positivos. O roster55da181 mantém as companhias sem unidade; não se restringe a pesquisa às32associadas.

Em2024, as quatroN1com recebíveis positivos são LeasePlan, CSILatina, CHG-Meridian e HP Financial Services. As outras23unidades positivas pertencem aB1/B2, inclusive conglomerados: logo um piloto limitado às sociedades de arrendamento omitiria parte relevante da atividade. Os nomes/códigos completos, coortes e componentes de leasing ficam em `nominal.jsonl`; AT/crédito/PL por unidade estão em `representation_stocks.parquet` da base pinada e suas somas por recorte em `summary.json`. Não se infere licença ou identidade societária pelo nome.

## Verificação e encaminhamento

Root é writer desta nota e de `.scratch/tcb-conciliacao-leasing/`, branch de integração `codex/tcb-research-182-188`, base `ef192beb2d80693be1b07cc074fed245acb05359`. Sem mudança estrutural, fórmula, motor, fonte aceita, ponteiro ou explorador. Pin vigente redescoberto `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`; catálogo/OData e tabelas aceitas autenticados, hashes individuais no recibo. Ferramentas locais existentes, sem nova coleta financeira ou instalação.

Piloto201003/202412:3.239unidades e123resumos, revisão independente antes da expansão. Uma melhoria separou identidade patrimonial e presençaDRE; delta conferido integralmente antes dos60períodos. Integral em12,125s:3.709resumos. Revisor `review_182_income` reautenticou76hashes, todos os nominais/resumos/estoques e confrontou diretamente10.467unidades de sete referências contra os brutos. A nota, as fontes e o SHA final possuem revisão própria na Issue; teste de software não substitui esse exame contábil.

A proposta QL precisa de escolha explícita na3antes do piloto191; não há adoção automática por disponibilidade ou conclusão da pesquisa. Rendimento fica com lacuna delimitada, sem impedir QL, as sensibilidades189ou as pesquisas184–188. Um eventual piloto191 deverá testar sinal de provisão, zero/null, contextos duplicados, agregação própria e preservação dos indicadores antigos antes de ampliar.

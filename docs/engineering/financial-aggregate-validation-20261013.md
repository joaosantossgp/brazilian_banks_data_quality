# Verificação de valores financeiros e agregados IF.data

[Issue117 — Validar valores financeiros e agregados do IF.data](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/117) · [plano](../superpowers/plans/2026-10-13-financial-aggregate-validation.md).

## Pergunta e recorte

Os valores financeiros e seus agregados locais têm escala demonstrada, coerência contábil e composição compatível com as referências usadas? Diagnóstico de dezembro2010/2014/2017/2020/2024, sem seleção CVM/B3, novas fórmulas acadêmicas ou inferência causal. Cobertura não certifica correção do valor.

## Versão conferida

Base de código/documentação `91bd20ccb205e72d47d42536eefbb529da551f16`, após fetch. O pacote recebido `snapshot-cvm-b3-20261013`, associado à relação histórica, trouxe outra restauração; não demonstrou nova versão dos saldos IF.data neste recorte. Comparação independente da seleção de versão:334arquivos locais de cadastro/catálogo/quatro conjuntos OData, todos presentes no recebido e com hashes idênticos aos pins do inventário113, zero arquivos locais modificados. Não promover ou sobrescrever dados foi necessário.

Origem local: cadastro `data/curated/ifdata-cadastro-20261011/`, valores `data/curated/ifdata-odata-20261011/`, catálogo `data/curated/ifdata-variable-catalog-20261011/`. Evidência privada daIssue117 em `.scratch/financial-aggregate-validation-20261013/`; recibo de comparação `preflight.json`,334entradas. Inputs do inventário ancorados no SHA-256 `67fb9e4d7a50fc5b838bd1665c6c0539c1ec1b1a111822cbb1a6988609944bad` de seu arquivo de pins.

## Escala, preservação e coerência contábil — fatia A

A [documentação oficial OData](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao), especificação `IfDataValores/Saldo`, declara valores monetários em **R$**. A propriedade também pode conter indicadores, cuja escala não foi convertida em moeda. HTML preservado, SHA-256 `72736b41ccf4c496a62e5cc98aeea25d6497b9bf0fcb97df05e845a54f518529`. O portal aplica formatação de apresentação; a indicaçãoR$mil de outro contexto não altera a unidade bruta OData.

Foram comparadas **566.164 células** dos quatro relatórios financeiros nas cinco datas, com tokens/localizadores e campos nativos iguais entre bruto eParquet; nenhuma diferença de escala ou valor introduzida na conversão. PythonDecimal90 nas contas e Decimal120 na reprodução independente, sem corte de precisão ou transformação emfloat.

| Verificação | Resultado e limite |
|---|---|
| Identidades contábeis/subtotais documentados |142.646igualdades exatas,6.054resíduos nãozero,8.698resultados inconclusivos; são testes porunidade/data/identidade, não contagem de companhias |
| Maior resíduo literal |R$0,0001; já existe nos operandos originais. Causa no produtor não comprovada |
| Sensibilidade separada a centavos |Os6.054resíduos zeram; não altera tokens, não institui tolerância e não muda o estado das igualdades exatas |
| Equação patrimonial |AtivoTotal78182 versus PassivoTotal78300; este incluiPL, portanto não somarPL novamente. Única diferença com dados:96477906/202412,R$0,00000001 |
| Join temporal |Sem multiplicação; três unidades sem cadastro preservadas:201012/C0051736 e202012/C0051554,C0052113 |
| Observações sem código |150linhas em202012,75contextos repetidos duasvezes; origem por `source_row`, sem identidade inventada |
| Hierarquia de depósitos |7.495testes inconclusivos: não assumir que a numeração/rótulo dos componentes prova completude da identidadeCOSIF |
| Demais inconclusivos |1.200testes com operandos ausentes e três joins sem cadastro; null não virou zero |

O crédito líquido foi conferido pela fórmulaCOSIF literal: crédito78191 mais provisão78192, cujo sinal nativo é preservado. Não subtrair novamente uma provisão já negativa. Conta78196 aparece em dois grupos e deve manter contexto; não presumir chave global porConta.

Os metadados oficiais arquivados de Resumo eDRE nas cinco datas descrevem dezembro como julho–dezembro. A correspondência dessa janela com todas as linhas OData permanece **contextual/inconclusiva**, sem campo de janela no payload ou ponte certificada. Nenhum lucro foi anualizado. Datas de estoque permanecem as referências `AnoMes`.

RevisãoA reproduziu566.164valores/campos e628.158operandos, hashes de21inputs finais e os334pins nas duas cópias. Parecer: PASS do diagnóstico computacional, sem aprovação global dos valores. O [plano](../superpowers/plans/2026-10-13-financial-aggregate-validation.md#decisão-técnica-no-gate-ab) registra por que B pode investigar composição e somas diagnósticas, mantendo resíduos originais/causa desconhecida e sem instituir tolerância.

## Composição e somas observadas — fatia B

O contrato `TipoInstituicao=2` da documentaçãoOData corresponde ao universo financeiro. A [metodologia histórica do portal](https://www3.bcb.gov.br/ifdata/index2024.html), `divMetodoMount`,nota2, apresenta conglomerados financeiros consolidados e instituições individuais que não integram conglomerados financeiros. O prudencial tem outro alcance. Compartilhar grupo prudencial não autoriza excluir uma unidade da soma financeira nem somar o próprio prudencial ao financeiro.

Nas cinco datas, a auditoria cadastral não encontrou vínculo financeiro não-self entre unidades observadas nem grupos financeiros compartilhados. O contrato da fonte e essa evidência sustentam o **uso descritivo da soma das unidades publicadas**, preservadas as lacunas. Não há certificação exaustiva de independência por ausência de vínculo. Também não é um balanço consolidado doSFN: posições entre unidades, como operações interfinanceiras, não foram eliminadas.

| Dezembro | Unidades com código | Ativo | Operações de crédito | Depósitos | Patrimônio líquido |
|---|---:|---:|---:|---:|---:|
|2010|1.786|4,335|1,616|1,478|0,431|
|2014|1.570|7,435|3,060|1,974|0,560|
|2017|1.401|8,484|3,105|2,346|0,750|
|2020|1.316|11,434|3,961|4,004|1,020|
|2024|1.422|17,481|6,160|6,107|1,573|

**R$trilhões nominais**, apresentação arredondada a três casas; cálculos e ledger preservam a precisão original. Contas78182/relatório1,78191/relatório2,78287/relatório3,78186/relatório1. Operaçõesdecrédito é a rubrica nativa78191, sem transportar definições de crédito ampliado/arrendamento/IFRS. Somam-se ocorrências numéricas observadas; null não vira zero e não é estimado. O total2020 inclui as ocorrências sem código explicitadas abaixo; a coluna de unidades conta somente códigos presentes. São cinco fotografias, sem inferência de crescimento orgânico ou continuidade trimestral.

Em2020, oito ocorrências nas quatro contas estão semCodInst: ativoR$565.642.676,21; créditoR$4.202.032,40; depósitosR$159.445.341,34;PLR$50.098.758,11. Permanecem separadas por localizador, sem atribuir instituição. As duas unidades identificadas sem cadastro têm ativoR$8.180.237.713,06(C0051554) eR$243.978.283,33(C0052113); os saldos não foram excluídos. Em2010/C0051736, as quatro contas estão null, logo sua importância não pode ser inferida por ausência de valor.

Grupos prudenciais compartilhados aparecem em 0/0/5/25/99 unidades, respectivamente; isso descreve perímetro, sem comprovar dupla contagem financeira. A composição contém 7.495 unidades identificadas/data e oito ocorrências sem código, totalizando 7.503 linhas. Os artefatos privados também conservam 100 posições top20. Top20 é inspeção, não corte amostral; unidades sem ativo ficam com importância desconhecida.

As16pontes entre fotografias(quatro contas×quatro intervalos) reconciliam exatamente a mudança da soma em entradas/saídas de códigos, mudança em códigos comuns, aparecimento/desaparecimento de valores e ocorrências anônimas. CodInst comum não certifica identidade longitudinal ou perímetro constante. A metodologia também registra inclusão de agências no exterior das independentes a partir2018; não atribuir todo o crescimento a atividade econômica.

## Comparações oficiais e limites — fatia C

A comparação externa foi delimitada, sem coleta de nova base. Metadados oficiais e referências numéricas foram classificados por compatibilidade; não converter coincidência de nomes/códigos ou montantes em identidade.

Em202412, a unidade financeira nativa `C0010069`,ITAU, tem ativoR$2.766.166.427.516,94; créditoR$835.635.320.396,22; depósitosR$1.102.160.071.372,71;PLR$211.259.988.306,98. Os quatro tokens coincidem com a publicação antiga oficial já aceita para instituição10069/contexto1005 da mesma referência. A ponte formal entre identificadores dos dois serviços não foi certificada nesta tarefa: a coincidência é evidência numérica contextual, não aceite de identidade pela semelhança.

| Referência2024 | Ativo(R$milhões) | Compatibilidade |
|---|---:|---|
|ITAU financeiroOData|2.766.166,42751694|Unidade financeira nativa desta investigação |
|ItaúUnibancoS.A.individualBRGAAP|2.273.107|Outro perímetro, comparação contextual |
|ItaúUnibancoHolding consolidadoIFRS|2.854.475|Outro perímetro/regime, comparação contextual |

Fontes externas: [demonstrações individuais, balanço na página1](https://www.itau.com.br/download-file/v2/d/42787847-4cf6-4461-94a5-40ed237dca33/dd67daea-735a-ada7-d49b-98b91702a184?origin=1) e [Manual daAssembleia2025,AnexoII,páginas19–20](https://www.itau.com.br/download-file/v2/d/42787847-4cf6-4461-94a5-40ed237dca33/beacdf46-3f22-f0c9-d854-91532c4ad065?origin=1). Texto primário acessível pela ferramentaweb; download local retornou403 e a captura visual não concluiu, logo não há hash local dessesPDFs. As diferenças entre montantes não demonstram erro na extração e não foram reconciliadas como ponte econômica: perímetro/regime já são diferentes.

A pesquisa de cinco datas × quatro contas encontrou referências de companhia apenas para 2024; nas outras 16 posições não localizou uma referência na busca limitada. As referências de 2024 são contextuais, não referências do total. A matriz final mantém **as 20 comparações agregadas inconclusivas**. Não confundir referência não localizada com inexistência de fonte oficial ou divergência demonstrada do total.

Oito comparações contextuais de montantes de uma unidade foram calculadas separadamente com Decimal120, após a revisãoB, convertendo R$milhões da referência para reais apenas nessa tabela. As diferenças aritméticas são registradas, mas não classificadas como erros por serem perímetros/regimes distintos. Diferenças relativas não foram usadas por essa incompatibilidade, sem denominador artificial. A revisão documental reproduziu os quatro montantes individuais; para aholding, reproduziu ativo ePL pelo resultado indexado do documento, sem reproduzir integralmente crédito/depósitos. Essa limitação não vira confirmação independente dos oito benchmarks.

## Interpretação e reprodução

Há evidência favorável de escala, preservação dos valores e coerência contábil nas cinco fotografias. Não apareceu erro de multiplicação por mil, alteração na conversão ou resíduo contábil acima de R$0,0001 nos testes disponíveis. As somas observadas têm contrato de universo e composição rastreável, podendo orientar exploração descritiva com as limitações declaradas.

Continuam abertos: mecanismo de geração dos resíduos subcentavo, ponte de janela dos fluxos para OData, hierarquia de depósitos, identidade das ocorrências sem código, certificação exaustiva de composição e referência externa compatível para reconciliar os totais. A expansão trimestral e correções de dados não estão implicitamente aceitas por este diagnóstico. Não inventar tolerância, completar ausências ou equiparar financeiro,prudencial e societário para obter concordância.

Evidência privada: `preflight.json`; `a_results.json`,dicionário,ledger e exceções; `b_results.json`,composição,ocorrências anônimas e16pontes; `c_sources.json`,documentos/localizadores e `c_comparison.json`; pareceres `review_a.md`, `review_b.md` e `review_c.md`; manifesto de execução com hashes. A âncora de preflight usada emA é distinguida de sua atualização posterior de metadados em `a_preflight_metadata.json`;334pins idênticos, sem reconstrução fictícia da versão anterior.

Na raiz primária de dados, os comandos privados reproduzíveis são:

```powershell
.venv/Scripts/python.exe .scratch/financial-aggregate-validation-20261013/a_validate.py
.venv/Scripts/python.exe .scratch/financial-aggregate-validation-20261013/a_sensitivity.py
.venv/Scripts/python.exe .scratch/financial-aggregate-validation-20261013/b_validate.py
.venv/Scripts/python.exe .scratch/financial-aggregate-validation-20261013/c_compare.py
```

Scripts de pesquisa finitos, sem ferramenta de produção nova. Usam dados autenticados existentes, uma thread,256MB de limiteDuckDB e precisãoDecimal explícita. A consulta principalA levou aproximadamente11–13segundos;B,4,314segundos. Não representam o tempo de pesquisa/revisão/publicação ou um benchmark geral. Os inputs foram novamente conferidos após as consultas, sem diferenças.

## Estado da investigação

Revisões independentes por fatia concluídas para A/B/C, sem achados materiais pendentes no diagnóstico. A composição documental e o SHA entregue têm gate final próprio. Os resultados são diagnósticos; o agregado acadêmico específico ainda depende dos vínculos temporais aceitos da frente108. Entrega local/revisada/publicada/integrada é registrada separadamente naIssue117, sem concluir a relação histórica ou a pesquisa bibliográfica.

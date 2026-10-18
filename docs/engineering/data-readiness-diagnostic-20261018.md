# Prontidão da base para análise — diagnóstico de 18/10/2026

[Issue 176](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/176) · [Plano e escopo](../superpowers/plans/2026-10-18-data-readiness-diagnostic.md)

## Resultado e decisão pendente

A base permite avançar na análise, mas há uma prioridade antes de fechar as comparações de alguns fluxos: a transição da Caixa em **3T2021–2T2022**. Persistem **28 resultados unidade×indicador×janela** indisponíveis nessa transição; ROA e ROE de 12 meses já estão corrigidos. As outras limitações principais são recortes com poucas unidades, classificação Sr incompleta, aplicação desigual de indicadores de crédito/depósitos e períodos anteriores à janela/regime disponível. Não são todas falhas a corrigir.

No agregado geral, as perdas podem parecer pequenas e ainda serem graves dentro de uma categoria: N2 chega a apenas 27,63% do AT conhecido coberto no ROA TTM em 4T2018, e N1 a 56,64% em 3T2021. Essas janelas também precisam de tratamento explícito antes de interpretar a categoria inteira.

Esta entrega **quantifica e propõe**, sem alterar indicadores, estoques, macro, fórmulas, ponteiro ou explorador. Não certifica plausibilidade de cada valor nem adota uma imputação. O congelamento final depende das decisões de João/orientador e do aceite dos diagnósticos estatísticos da [Issue 175](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/175). A 175 conserva robustez, influência e sensibilidade à composição; seus resultados não foram presumidos aceitos aqui.

## Entradas fixas e método

Ponteiro compartilhado `data/curated/current-indicators.json`, localizado pelo [comando canônico](local-queries-20261013.md#base-de-indicadores-vigente-entre-tasks), autenticado antes da leitura. Raiz privada neste computador: `C:/Users/JoãoPereira/Documents/Projects/brazilian_banks_data_quality/data/curated/`.

- Financeiro e perspectivas complementares: `historical-links32-composition-20261018-run3`; SHA-256 do manifest `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`.
- Contexto macro: `macro-context-20261018-run2`; SHA-256 do manifest `9920b6ebe130854130ab9ec7e7bfe98410556f22f81b969128be2704be8de118`.
- Base efetiva da fatia: `970e3f3417a83a84eca9adf369176348e39f19b9`, que inclui a PR174 documental da outra frente; referência inicial `96a678b4b206a27d9b87de12f43f28158583adc7`. O diff próprio contém somente os dois Markdown desta entrega. Instrumento finito privado, sem módulo/dependência nova ou mudança de arquitetura.

O instrumento lê células conjuntas e tabelas já persistidas; soma componentes e estoques com `Fraction`, sem reavaliar fórmulas financeiras. Autentica os arquivos consumidos, verifica conservação de tamanho/data dos inputs e reconcilia contagens, numeradores, denominadores e ativos com agregados aceitos. A cobertura é **estoque conhecido das unidades elegíveis ÷ estoque conhecido das unidades esperadas**, separadamente para AT, crédito e PL. Não é a fração do total econômico quando há estoque desconhecido; PL negativo exige leitura de pesos assinados.

Uma linha representa trimestre×perspectiva×indicador×janela×coorte×recorte. `total` inclui `sample`, `remaining` e `unknown`, estados disjuntos. As 32 companhias vinculadas não são 32 contribuintes adicionais: em 4T2024 correspondem a 24 unidades financeiras. Os vínculos históricos admitidos são os do pacote, sem projetar automaticamente registro/listagem atuais para o passado. Financeiro é principal; Individual e Prudencial não se somam a ele.

Faixas 0, 1, 2–4, 5–9, 10+ unidades e cobertura <80%, 80–95%, 95–100%, 100% são **descrições**, não critérios de exclusão ou validade estatística. Categoria ausente, cadastro datado ausente, classificação desconhecida, antes do regime e indicador não calculável são estados diferentes.

A execução completa aceita leu **305.296 células**, produziu **285.514 contextos observados** e reconciliou **12.230 contextos gerais**, em **86,8 segundos**, sem recálculo financeiro. Outros **730 contextos gerais aceitos são vazios**, conferidos separadamente: 12.230 + 730 = 12.960. A grade de categorias alguma vez observadas contém 305.966 combinações período/contexto não observadas; isso **não é uma contagem de dados perdidos**, pois inclui categorias inexistentes naquele período e Sr anterior ao regime.

## Tcb: dimensão do problema no Financeiro

Referência comparável: ROA de 12 meses, 4T2024. `elegíveis/esperadas` conta unidades IF.data; cobertura se refere a AT conhecido. Não representa a cobertura de todos os outros indicadores.

| Tcb | Sistema: elegíveis/esperadas | AT conhecido coberto | Seleção 32: unidades | Restante: unidades | AT restante coberto |
| --- | --- | --- | --- | --- | --- |
| B1 | 94/97 | 99.60% | 19/19 | 75/78 | 98.77% |
| B2 | 30/31 | 99.77% | 1/1 | 29/30 | 99.75% |
| B3S | 751/753 | 100.00% | 0/0 | 751/753 | 100.00% |
| B3C | 27/29 | 100.00% | 0/0 | 27/29 | 100.00% |
| B4 | 4/4 | 100.00% | 0/0 | 4/4 | 100.00% |
| N1 | 205/226 | 97.61% | 2/2 | 203/224 | 97.43% |
| N2 | 123/136 | 96.94% | 1/1 | 122/135 | 96.88% |
| N4 | 103/146 | 96.96% | 1/1 | 102/145 | 96.35% |

No geral são **1.337/1.422 unidades** e **99,50% do AT conhecido**; seleção 24/24 e 100%; restante 1.313/1.398 e 98,87%. Há **sete unidades com AT desconhecido**, todas no restante. Portanto B3C 100% de AT conhecido com 27/29 unidades não significa cobertura econômica integral.

B4 tem somente quatro unidades no sistema. Na seleção, B2, N2 e N4 têm uma unidade cada; N1 tem duas. Isso limita generalização/dispersão, mesmo com cobertura de ativos de 100%. N2 selecionado representa Oliveira Trust; N4 representa Cielo neste trimestre. Não concluir que o conjunto N2 ou N4 do sistema tenha uma única unidade.

### Duração dos recortes pequenos

A tabela abaixo percorre a janela inteira do **ROA TTM financeiro**, excluindo os três trimestres de aquecimento ao contar períodos de comparação. Mínimo/máximo consideram apenas períodos com elegíveis; primeiro/último não asseguram continuidade. O CSV completo contém cada trimestre, demais indicadores, três perspectivas e cruzamentos Tcb×Sr; não extrapolar esta síntese para outra fórmula.

| Recorte | Categoria | Coorte | Primeiro–último elegível | n elegível mín.–máx. | Trimestres com 1–4 / observados pós-aquecimento | AT coberto mínimo |
| --- | --- | --- | --- | --- | --- | --- |
| SrAnalitico | S1 | Restante | 4T2018–4T2024 | 2–8 | 13/24 | 99.95% |
| SrAnalitico | S2 | Restante | 1T2018–4T2024 | 1–8 | 23/28 | 99.19% |
| SrAnalitico | S3 | Restante | 2T2017–4T2024 | 10–43 | 0/31 | 89.60% |
| SrAnalitico | S4 | Restante | 1T2017–4T2024 | 2–276 | 1/32 | 79.48% |
| SrAnalitico | S5 | Restante | 4T2018–4T2024 | 529–694 | 0/25 | 99.46% |
| SrAnalitico | S1 | Seleção | 2T2017–4T2024 | 4–6 | 2/31 | 100.00% |
| SrAnalitico | S2 | Seleção | 2T2017–4T2024 | 1–2 | 28/28 | 100.00% |
| SrAnalitico | S3 | Seleção | 2T2017–4T2024 | 4–10 | 1/31 | 87.38% |
| SrAnalitico | S4 | Seleção | 3T2017–4T2024 | 1–5 | 29/30 | 86.75% |
| SrAnalitico | S5 | Seleção | 2T2024–3T2024 | 1–1 | 2/2 | 100.00% |
| SrAnalitico | S1 | Sistema | 2T2017–4T2024 | 4–13 | 2/31 | 99.99% |
| SrAnalitico | S2 | Sistema | 2T2017–4T2024 | 1–9 | 22/31 | 99.38% |
| SrAnalitico | S3 | Sistema | 2T2017–4T2024 | 14–53 | 0/31 | 89.11% |
| SrAnalitico | S4 | Sistema | 1T2017–4T2024 | 2–279 | 1/32 | 82.08% |
| SrAnalitico | S5 | Sistema | 4T2018–4T2024 | 529–694 | 0/25 | 99.46% |
| Tcb | B1 | Restante | 4T2010–4T2024 | 70–78 | 0/57 | 95.74% |
| Tcb | B2 | Restante | 4T2010–4T2024 | 29–36 | 0/57 | 94.66% |
| Tcb | B3C | Restante | 4T2010–4T2024 | 27–39 | 0/57 | 98.86% |
| Tcb | B3S | Restante | 4T2010–4T2024 | 751–1276 | 0/57 | 99.80% |
| Tcb | B4 | Restante | 4T2010–4T2024 | 4–4 | 57/57 | 100.00% |
| Tcb | N1 | Restante | 4T2010–4T2024 | 98–203 | 0/57 | 51.51% |
| Tcb | N2 | Restante | 4T2010–4T2024 | 114–168 | 0/57 | 27.53% |
| Tcb | N4 | Restante | 4T2018–4T2024 | 4–102 | 1/29 | 70.16% |
| Tcb | B1 | Seleção | 4T2010–4T2024 | 18–20 | 0/57 | 99.44% |
| Tcb | B2 | Seleção | 2T2013–4T2024 | 1–1 | 43/51 | 100.00% |
| Tcb | N1 | Seleção | 4T2010–4T2024 | 1–2 | 57/57 | 99.87% |
| Tcb | N2 | Seleção | 1T2021–4T2024 | 1–1 | 16/16 | 100.00% |
| Tcb | N4 | Seleção | 4T2018–4T2024 | 1–1 | 25/29 | 100.00% |
| Tcb | B1 | Sistema | 4T2010–4T2024 | 90–98 | 0/57 | 98.31% |
| Tcb | B2 | Sistema | 4T2010–4T2024 | 29–37 | 0/57 | 94.88% |
| Tcb | B3C | Sistema | 4T2010–4T2024 | 27–39 | 0/57 | 98.86% |
| Tcb | B3S | Sistema | 4T2010–4T2024 | 751–1276 | 0/57 | 99.80% |
| Tcb | B4 | Sistema | 4T2010–4T2024 | 4–4 | 57/57 | 100.00% |
| Tcb | N1 | Sistema | 4T2010–4T2024 | 100–205 | 0/57 | 56.64% |
| Tcb | N2 | Sistema | 4T2010–4T2024 | 115–169 | 0/57 | 27.63% |
| Tcb | N4 | Sistema | 4T2018–4T2024 | 5–103 | 0/29 | 81.30% |

O antigo código Tcb B3 não é emendado automaticamente a B3S/B3C. Entrada/saída de categoria altera composição. Ausência de categoria na seleção pode ser característica do conjunto escolhido, não ausência do sistema. Células sem unidades não recebem indicador zero.

## Sr analítico: falta de classificação e não de indicador

ROA TTM financeiro, 4T2024:

| Sr analítico | Sistema elegíveis/esperadas | Seleção | Restante | AT sistema coberto no recorte |
| --- | --- | --- | --- | --- |
| S1 | 12/12 | 5/5 | 7/7 | 100.00% |
| S2 | 9/9 | 1/1 | 8/8 | 100.00% |
| S3 | 47/48 | 10/10 | 37/38 | 98.51% |
| S4 | 279/300 | 3/3 | 276/297 | 98.70% |
| S5 | 694/710 | 0/0 | 694/710 | 99.46% |
| Desconhecido | 296/343 | 5/5 | 291/338 | 95.82% |

O rótulo desconhecido concentra **6,39% do AT conhecido do sistema**, **2,22% da seleção** e **11,68% do restante** em 4T2024. Essas unidades continuam nos agregados gerais se o indicador é calculável: classificação faltante prejudica a decomposição por Sr, sem por si reduzir o agregado geral. Os cinco Sr desconhecidos da seleção são Cielo, BNB, Banese, BR Partners e Oliveira Trust.

Há candidato finito para Banese: a instituição 13009717 aponta para C0081634, cujo Sr analítico S4 foi derivado de membro com rótulo nativo S4. A regra atual usa **um nível de evidência nativa** e não propaga o rótulo derivado novamente. A cadeia datada de dois vínculos pode fundamentar uma extensão explícita, preservando original/conflitos; não é perda técnica comprovada nem enquadramento oficial próprio recuperado. Nos outros quatro, o pai também está desconhecido: essa extensão sozinha não os resolve.

Antes de 1T2017, Sr é `before_regime`, não lacuna a preencher com o enquadramento atual. Os 12 rótulos financeiros S1 em 4T2024 **não são 12 conglomerados prudenciais independentes**: unidades financeiras podem compartilhar grupo prudencial. Não reconstruímos S oficial por AT/PIB. [Regra e fontes normativas já capturadas](ifdata-classification-gaps-20261016.md).

## Lacunas que efetivamente restringem os agregados

### Categorias com perdas históricas relevantes

ROA TTM financeiro, sistema observado. Estes são episódios selecionados do inventário integral; mínimo é cobertura de AT conhecido, não o valor do indicador. Os nomes são exemplos documentados no contexto mínimo, não ranking exaustivo das perdas.

| Recorte | Janela inteira de cobertura <95% | Mínimo / trimestre | Exemplo e classificação preliminar |
| --- | --- | --- | --- |
| Tcb N2 | 4T2016–4T2018, 9 trimestres | 27,63% / 4T2018 | XP Investimentos; `binding_missing`. Candidato prioritário de componentes/abertura na janela completa. |
| Tcb N2 | 3T2022–1T2024, 7 trimestres | 34,33% / 2T2023 | Warren, S3 Caceis, Vórtx; `binding_missing`. Transições são investigáveis, sem ponte já provada. |
| Tcb N1 | 4T2020–4T2021, 5 trimestres | 56,64% / 3T2021 | Nubank, Mercado Crédito; faltas de vínculo/componentes e nulos. Diagnóstico nominal finito antes de concluir sobre N1 inteiro. |
| Tcb N4 | 4T2017–3T2019, 8 trimestres | 0% / 4T2017; quatro trimestres sem agregado | Cielo, Redecard, Getnet, Stone e Nu entre exemplos. Entrada na fonte, abertura e quebra de definição/IPs; parte do período é estrutural e as exceções da ponte2019 foram preservadas. |
| Tcb N4 | 1T2020–4T2020, 4 trimestres | 87,99% / 2T2020 | Stone e outras IPs; proteção/ausência de componentes, não imputar lucro pela rubrica apenas. |
| Sr S4 | 3T2017–3T2018, 5 trimestres | 82,08% / 1T2018 | Crefisa/BS2/Tullett; `binding_missing`. Classificação recuperada não resolve automaticamente histórico do fluxo. |
| Sr S3 | 4T2019–3T2020, 4 trimestres | 92,80% / 3T2020 | XP; `binding_missing`. Mesma causa institucional pode afetar Tcb e Sr em janelas distintas. |
| Sr S3 | 2T2023–3T2023, 2 trimestres | 89,11% / 3T2023 | BNP, BRB, Crédit Agricole, BS2; motivos mistos. BRB permanece adiado; não declarar todos recuperáveis. |

Essas perdas **afetam o agregado daquela categoria**, mesmo quando o geral permanece bem coberto. Não usar a média de N2 desses anos como desempenho integral do segmento sem aviso. A prioridade é global para Caixa e específica para N2/N1 nessas janelas. Propõe-se uma segunda frente curta agrupada por transição/causa; se não houver prova, delimitar a leitura em vez de preencher. `critical-windows.csv` traz também os demais episódios, coortes e cruzamentos, incluindo perdas menores e ausência completa.

### Caixa: prioridade finita, 3T2021–2T2022

A consulta nominal à tabela de contribuições encontrou 28 `binding_missing` em 104 linhas da unidade C0051626 nessa janela. Isso não é 28 companhias nem 28 trimestres.

| Trimestre | Resultados indisponíveis | Indicador/janela |
| --- | --- | --- |
| 3T2021 | 12 | E2-B/ttm, E3/quarter, E3/ttm, Q2/quarter, Q2/ttm, R1/quarter, R2/quarter, R4/quarter, R4/ttm, R5/quarter, R5/ttm, RS/ttm |
| 4T2021 | 6 | E2-B/ttm, E3/ttm, Q2/ttm, R4/ttm, R5/ttm, RS/ttm |
| 1T2022 | 6 | E2-B/ttm, E3/ttm, Q2/ttm, R4/ttm, R5/ttm, RS/ttm |
| 2T2022 | 4 | E3/ttm, Q2/ttm, R4/ttm, R5/ttm |

Em **E3 TTM no 3T2021**, a interseção cobre **87,14% do AT conhecido do sistema**, **99,97% da seleção** e **67,95% do restante**. Essa diferença de população é material para a comparação entre coortes.

Se uma ponte economicamente válida recuperar a elegibilidade da Caixa, mantendo tudo mais igual, a cobertura conhecida desse contexto passaria a **99,27% no sistema e 98,23% no restante**. É uma conta condicional de cobertura, **não uma previsão do valor de E3**, prova de ponte admissível ou correção já executada.

As janelas completas são: E2-B/RS TTM, 3T2021–1T2022; E3/Q2/R4/R5 TTM, 3T2021–2T2022; R1/R2/E3/Q2/R4/R5 trimestrais, 3T2021. Q2/R5 também excluem negócios sem crédito: recuperar Caixa não elimina todas as diferenças. [Evidência anterior da transição e limites da ponte](caixa-financial-transition-2021-20261016.md).

### Demais famílias e períodos

| Família / janela | Cobertura e janela financeira do sistema | Causa / possibilidade |
| --- | --- | --- |
| R1/R2 TTM | 57/60 trimestres com resultado; os 57 a partir de 4T2010 têm AT conhecido coberto ≥95% | Três primeiros trimestres de 2010 sem histórico suficiente no pacote. Propor uso TTM a partir de 4T2010; trazer 2009 exigiria admissão própria. Trimestral já começa 1T2010. |
| Q2/E2-B/E3/R4/R5/RS TTM | Mesmo aquecimento de 1T–3T2010 | Não preencher com zero ou anualização ×4. Ausência de histórico aceito não prova inexistência na fonte. |
| C1, LA, LC pontuais | 60/60; 100% do AT conhecido | Mantêm unidades sem estoque explicitamente fora do peso conhecido. |
| LF-DEP/LF-OC/LF-EM/LF-REP | 60/60; mínimo 98,59%, 4T2018 | Não há queda abaixo da faixa descritiva de 95% no geral; não exige ampliação antes de analisar. |
| L3 pontual | 60/60; mínimo 96,61%, 3T2019 | Uso com cobertura explícita; não provada necessidade de correção global. |
| E2-B/RS trimestrais | 60/60; mínimo 97,74%, 4T2017 | Negativos em B3C já foram conferidos: contribuição líquida contábil pode produzir sinal negativo; não cortar por sinal. |
| L2 pontual | Todos os 60 trimestres abaixo de 95%; mínimo 84,61%, 4T2017 | Depósito à vista zero e negócios sem essa captação. Limitação de aplicabilidade, não sinônimo de falta de liquidez. LA já oferece visão complementar; não trocar denominador silenciosamente. |
| Q1 pontual | Abaixo de 95% apenas em 4T2023 (94,94%) e 4T2024 (94,98%) | Negócios sem carteira de crédito, além de nulos. Comparar atividade aplicável. |
| Q2/R5 TTM, além de Caixa/aquecimento | Abaixo de 95% em 4T2022–2T2024 e 4T2024; mínimo pós-Caixa 93,95% | Há denominadores zero em pagamentos e faltas de componentes. Lista de motivos não é diagnóstico de bug; não forçar indicador de crédito em toda atividade. |

Os motivos e pesos constam por trimestre no inventário; a existência de agregado não significa população constante. Não estimamos o valor contrafactual dos indicadores ausentes. BRB continua adiado conforme decisão anterior. Transições XP/Warren/Nubank são candidatos finitos importantes para as categorias e janelas destacadas acima, sem nova correção demonstrada; não bloqueiam automaticamente o agregado geral, mas condicionam a interpretação integral desses recortes. [Diagnóstico N2/B3C](ifdata-n2-b3c-diagnostic-20261017.md).

## Perspectivas complementares e C4

O inventário inclui Individual e Prudencial separadamente, por Tcb/Sr e cruzamento. O Individual pode conter instituições de grupos: sua soma não se adiciona ao Financeiro nem mede sistema consolidado sem sobreposições. O Prudencial do pacote começa em 2015; não é ausência de cinco anos de uma mesma série financeira. [Desenho do universo](ifdata-analytical-update-20261017.md).

C3/C4 prudenciais no geral:

| Período | Indicador | Elegíveis/esperadas |
| --- | --- | --- |
| 4T2017 | C3 | 1352/1395 |
| 4T2017 | C4 | 1352/1395 |
| 4T2018 | C3 | 1305/1354 |
| 4T2018 | C4 | 436/1354 |
| 4T2024 | C3 | 1358/1367 |
| 4T2024 | C4 | 444/1367 |

A queda do C4 após 2018 acompanha nulos de capital principal e mudanças de regime/aplicabilidade documentadas. Não foi demonstrada falha de processamento. Sr S5 não prova opção individual por um regime. Não substituir C4 por zero, derivar capital principal de patrimônio líquido, nem tratar os 444/1.367 de 4T2024 como cobertura ponderada de ativos. Este pacote não dispõe de estoque AT próprio prudencial para essa certificação; não foi emprestado o financeiro. [Diagnóstico de toda a janela 2018–2024 e fontes](ifdata-c4-prudential-gaps-20261016.md).

Em 4T2024, a composição prudencial geral inclui 24 unidades selecionadas, 561 restantes e **782 de vínculo de coorte desconhecido**. Portanto `sistema = seleção + restante` não é identidade geral: o estado desconhecido precisa aparecer. Não transformar desconhecido em não aberto. Essa restrição é especialmente relevante à comparação de coortes nessa perspectiva complementar.

## Variáveis agregadas e econômicas

AT/crédito/PL foram conferidos uma vez por perspectiva×período×coorte×recorte: **14.573 contextos observados**, sem variação do mesmo estoque entre indicadores/janelas (**zero divergências**). Esses estoques contemporâneos próprios não são o saldo médio usado no denominador de alguns indicadores. Esta conferência verifica consistência do pacote, não certifica a fonte inteira ou independência entre unidades.

As sete unidades financeiras sem AT/crédito/PL em 4T2024 são: confederações Sicredi (03795072) e Sicoob (04891850), RCCL (23757411), FFA (24537861), Mundinvest (25674235), Qesh (31818873) e For You (46009412). Todas estão no restante. Sem seus estoques, não é possível afirmar sua irrelevância por peso. É razoável uma consulta curta ao material já capturado de Resumo/Ativo; não existe aqui prova de uma recuperação disponível.

O pacote macro tem **25 combinações de série/método/unidade** e 1.476 observações trimestrais: **22 com 60/60 trimestres**, três PNAD com **52/60**, de 1T2012 a 4T2024. Não há buracos internos nas séries aceitas; a ausência PNAD de 2010–2011 é estrutural. PIB, IPCA e Selic permitem a leitura do núcleo 2010–2024; renda/desocupação exigem janela desde 2012.

Preservar vintage: renda real nos preços do último trimestre publicado da captura (2026T2), não preços constantes de 2024. Selic Over efetiva acumulada em 3/12 meses não é meta Copom anualizada; juro real Fisher é ex post, não taxa neutra/ex ante/custo de crédito bancário. Curva de juros/meta Copom são extensões fora do MVP, não reparos necessários. Não emendar PNAD/PME sem método. Uma observação macro Brasil por trimestre não vira observação independente para cada Tcb/Sr. [Fontes, transformações e limites macro](macroeconomic-context-2010-2024-20261018.md).

## Lista finita para decidir o fechamento

| Prioridade | Resultado proposto | Esforço relativo e condição | Precisa modificar a base agora? |
| --- | --- | --- | --- |
| P0 | Resolver ou aceitar explicitamente a perda da Caixa nos 28 resultados de toda a transição | Médio, finito: verificar componentes/perímetro e ponte por família; seletivo, preservando originais e os ROA/ROE TTM já conferidos | Recomendo tratar antes de comparar os fluxos afetados em 2021–2022. Ainda é candidato, não correção garantida. |
| P1 | Tratar as quedas históricas de N2 (XP/Warren) e N1 (Nubank), junto dos Sr afetados | Médio, finito: consultar todas as janelas listadas, agrupar causas e provar componentes/perímetro; reutilizar correção somente quando admitida | Necessário resolver ou aceitar expressamente o recorte incompleto antes de interpretar essas categorias inteiras; não exige recálculo geral. |
| P1 | Fechar janelas de uso: trimestral desde 1T2010; TTM desde 4T2010; Sr desde regime/observação; PNAD desde 2012 | Baixo: decisão explícita e documentação; sem indicador novo | Não exige recálculo. Trazer histórico anterior seria escopo separado, não condição geral para analisar. |
| P1 | Conferência curta dos sete estoques desconhecidos de 4T2024 nos dados já capturados | Baixo a médio; parar se não houver evidência própria; avaliar janela inteira se houver causa comum | Recomendo uma última verificação limitada; se irrecuperável, preservar desconhecidos e peso não mensurável. |
| P2 | Medir/adotar ou rejeitar extensão Sr de dois vínculos, começando por Banese | Médio, finito: toda a janela/cadeias análogas, conflitos/ciclos/provas; exige decisão metodológica | Melhora recortes; não altera indicador geral. Não prometer recuperar os outros quatro desconhecidos da seleção. |
| Aceitar com limites | Recortes pequenos, categorias vazias, L2/crédito inaplicáveis, C4 pós-2018, PNAD inicial, perímetros | Documentar e mostrar contagem/cobertura; nenhum preenchimento artificial | Não são motivos para uma reforma do motor ou coleta sem prazo. Indicador adaptado só com conceito/fonte/adoção própria. |
| Gate final | Incorporar aceite da 175 e fixar o pacote a analisar, dicionário, universo, janelas e exceções | Dependência de outra frente; não duplicar seus testes | O diagnóstico 176 pode concluir; o congelamento acadêmico ainda não foi declarado. |

Não há estimativa honesta em horas para as pontes sem conferir componentes. O escopo proposto é pequeno e seletivo; o levantamento completo de cobertura em 86,8 s mostra que esta decisão não exige rodar o motor inteiro. Não expandir indefinidamente a busca por todo rótulo ausente. Se a conferência curta não produzir evidência, registrar o limite e avançar à análise com a janela/atividade adequada.

## Reprodução, arquivos e revisão

Somente esta nota e o plano são públicos. O instrumento e os dados diagnósticos ficam em `.scratch/data-readiness/` no worktree `data-readiness`, com bundle privado e hashes. O Git não distribui os pacotes aceitos: outra task precisa seguir o ponteiro canônico e conferir os pins antes de reutilizar estes resultados.

- `diagnostic.py --output .scratch/data-readiness/<destino-novo>`: inventário completo, sem fórmula financeira; `--pilot` restringe o piloto.
- `test_diagnostic.py`: testes causais de contagem/coorte/frações, duplicação, ausência/zero, pesos desconhecidos/assinados e exemplos compactados.
- `summarize.py` e `audit_details.py`: pós-processamento do inventário e consultas direcionadas ao pin; nenhuma alteração dos inputs.
- `full-run3/contexts.csv`: 285.514 linhas, todos os períodos/categorias/estados/coortes/indicadores/janelas; contagens e AT/crédito/PL exatos, flags e motivos. **Listas nominais compactadas não são exaustivas** e não fornecem ranking global das maiores perdas.
- `full-run3/critical-windows.csv`: 711 janelas consecutivas de cobertura financeira baixa/ausente por recorte; não é lista de 711 bugs. Para Sr pré-regime e outros não observados, usar `unobserved-grid.csv`, sem imputar zero.
- `full-run3/facts.json`: consulta nominal Caixa, estoques desconhecidos, contagens C3/C4 e resumos históricos. `macro-coverage.csv`: cada uma das 25 combinações.
- `full-run3/receipt.json`: pins, hashes e `financial_recalculation=false`. SHA-256 do instrumento aceito: `4e10728d9e6e3744239bf70c67045048e7a03ed1e69fc95a512b373f06c26120`; do CSV completo: `841947259268c1f03fdbb6ca78c4baba5c7176ef6cf3d1964c4d35247929e2e9`.

Revisão independente aprovou o piloto antes da ampliação (111 contextos), quatro testes causais e a conferência estratificada completa de 5.916 contextos em 1T2010/1T2017/4T2024, nas três perspectivas e quatro estados de coorte, sem divergências de contagem, N/D, razão e estoques. Cruzamentos Tcb×Sr tiveram conferência própria no piloto. Cobertura macro 22×60 + 3×52 também foi conferida.

Tentativas falhas foram preservadas: cadastro nulo/listas compactadas no piloto; limite insuficiente de memória e ordenação física fragmentada no inventário. Não são PASS nem discrepância demonstrada da base. A tentativa completa aceita usou ordenação explícita, uma thread e limite DuckDB de 2 GiB, após medir recursos; a reconciliação integral de contagens entre células persistidas e agregados deu zero divergências. Não se ampliou o motor.

A revisão final da nota, inventário e SHA entregue, os checks documentais, PR e integração ficam registrados na Issue 176. Nenhum rename/delete ou arquivo de outra frente integra esta entrega.

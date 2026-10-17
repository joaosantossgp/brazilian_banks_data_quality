# Revisão dos indicadores por atividade e viabilidade no IF.data

**Guia de leitura visual — 17/10/2026:** o [atlas de fórmulas por recorte](financial-indicators-formulas-20261017.md) abre componentes, sinais, contas e janelas das dez métricas atuais e sete propostas prioritárias. Três mapas adicionais abrem Tcb, Tc, Td, Sr e SrAnalitico com contagens do sistema em 202412. A matriz de famílias explicita aplicação e lacunas; as figuras não adotam novas métricas nem substituem as fichas e a cobertura abaixo.

Pesquisa dirigida da [Issue 143](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/143), 16/10/2026, para a monografia de Ciências Econômicas/UNICAMP. **Proposta para decisão, sem adoção de indicadores novos, alteração de fórmulas, cálculo de razões financeiras novas ou mudança do explorador.** O sistema observado inteiro é o objeto principal da pesquisa e da seleção dos indicadores; companhias associadas constituem recorte comparativo. Financeiro é principal; Individual e Prudencial são complementares separados. Núcleo 2010–2024; 2025–2026 não integra as matrizes de cobertura por unidade/período. O arquivo de contextos conserva metadados originais do catálogo, inclusive listas e contagens completas quando a mesma definição atravessa 2025; suas listas do núcleo e do complemento permanecem separadas.

A entrega combina esta nota, [proveniência](financial-indicators-activity-review-20261016.provenance.md), [matriz resumida de cobertura](financial-indicators-activity-coverage-20261016.csv), [matriz integral comprimida](financial-indicators-activity-coverage-20261016.csv.gz) e [contextos dos componentes](financial-indicators-activity-components-20261016.csv). O CSV legível contém todos os períodos sem segmentação e todos os seis eixos em 202412; o gzip contém todos os períodos/eixos/coortes, sem redução da auditoria. Scripts, contagens nominais, fontes e pareceres estão no staging privado explicitado na proveniência; PDFs privados não são reproduzidos. Cobertura de componentes, validade econômica e indicador calculado são estados diferentes.

## Conclusão proposta e decisões que permanecem humanas

Recomenda-se preservar ROA, ROE e PL/AT como núcleo contábil comum, com limitações de objetivo e perímetro; manter Q1/Q2 para carteiras de crédito compatíveis e C3/C4 em séries prudenciais próprias; restringir a interpretação de L2/L3 ao modelo de captação que seus denominadores representam. **Ampliar a dimensão liquidez/financiamento exige uma pequena família de medidas de composição e financiamento, acompanhada de uma lacuna explícita de maturidade/estresse.** Aumentar cobertura contábil não certifica liquidez disponível.

Os primeiros candidatos são: participação de disponibilidades+AIL no ativo; crédito/AT; perfil de financiamento com rubricas não sobrepostas; margens da intermediação e renda de serviços; custo pessoal/administração por AT médio como complemento de E2-B. Não se recomenda substituir todos os denominadores por AT, reconstruir LCR/NSFR com TVM genérico, criar uma fórmula para cada cruzamento cadastral ou produzir índice único. A escolha do conjunto final e de eventuais fontes financeiras adicionais cabe a João/orientador.

O desempenho financeiro de uma cooperativa ou banco de desenvolvimento precisa ser lido também como sustentabilidade da operação, e não maximização de lucro do acionista. O [BCB REB 2022, pp. 39–43](https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb2022p.pdf) examina benefícios ao cooperado além das sobras; [Ferraz, Além e Madeira 2013, pp. 30–31/35–37](https://web.bndes.gov.br/bib/jspui/bitstream/1408/1421/1/RB%2040_final-A.pdf) distinguem sustentabilidade de cumprimento do mandato. Para IPs, corretoras e distribuidoras, receitas de serviços e obrigações de clientes podem dominar o negócio; carteira de crédito nula não torna a unidade ineficiente nem sana a necessidade de medir risco de contraparte, liquidação e liquidez próprios. Não há base para chamar as cinco dimensões integralmente cobertas em todas as atividades.

## Estado reconciliado das entradas

| Entrada conferida | Estado e uso nesta pesquisa |
|---|---|
| [Pesquisa 111](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/111), fichas e proveniência de 14/10 | Entregue e integrada; 25 candidatos, dez métricas iniciais posteriormente adotadas. A auditoria de 1430/1440 era presença conjunta contemporânea na amostra antiga, não cobertura calculável do sistema. Reaproveitar conceitos e fontes, sem repetir seus estados históricos como correntes. |
| [Inventário 113](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/113) | Entregue; separa cadastro geral e unidades com valores, 438 contextos e 60 trimestres financeiros/individuais. Atualização desta pesquisa incorpora SrAnalitico e exclui Atividade dos eixos. |
| [Implementação 127](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/127) e [universo 130](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/130) | Entregues; dez métricas, trimestres efetivos/TTM, médias aproximadas ponderadas pelo tempo, quatro coortes: total, vinculadas, restante, vínculo desconhecido. Perspectivas mantêm unidades próprias. |
| [Decisão 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3), correções 133–138 | Ponte LL 2019 e SrAnalitico têm entregas locais posteriores aos pacotes originais. Esta pesquisa não regenera resultados nem confunde baseline histórico com correções locais aceitas. |
| [C4/139](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/139) | CP nulo em 25272/37415 posições de 2018–2024; 12138 elegíveis, 1 RWA nulo com CP observado, 4 RWA zero. PR S5 é explicação regulatória para padrão, sem provar opção individual; S5 não implica CP nulo e CP não é PR. |
| [L2/140](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/140) | Em 89476 posições financeiras: 51143 disponíveis, 37639 DV zero, 694 nulos. Todos os cinco componentes auditados são nulos nessas 694; zero DV não prova não aplicabilidade. BNDES 33657248 tem DV zero em 60/60. |
| [BRB/141](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/141) | Fontes alternativas encontradas, sem admissão; 169 nulls nativos e 66 resultados afetados documentados. Diferenças de perímetro/revisão preservadas. Não houve busca BRB adicional nesta pesquisa. |
| [Universo 142](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/142) | Decisão vigente: 55 companhias, 32 associadas e 24 unidades distintas em 2024, 23 sem correspondência principal. Documentação em outro worktree; cálculos anteriores: 24 companhias/20 unidades permanecem históricos. Não projetar vínculo de 2024 para 2010 nem atribuir balanço do grupo à subsidiária. |

O checkout primário estava limpo em `d9d8d8d0db5d69fbad466596b6ab3bde2c4750fc`, branch `codex/indicator-pilot`; `origin/main` autenticada por fetch em `4061111fe12e4113869eba7ec90f0774cc74cd4e`. Notas atuais foram lidas nos worktrees do mesmo repositório, com alterações locais preservadas. Root escreve somente os cinco arquivos novos da 143 e staging privado; protocolo/arquitetura/amostra 142 têm owner distinto. Não se transplantou árvore de implementação nem se declarou sincronização deste checkout.

## Famílias econômicas e estratificações

`Tcb` e `SegmentoTb` fornecem pistas para famílias de negócio; composição de ativos, receitas e financiamento testa sua pertinência. `Tc` explica controle, `Td` consolidação; `Sr` descreve proporcionalidade prudencial. **SrAnalitico é atributo separado**, com prioridade ao original, origem de derivação contemporânea e conflitos preservados. Não é Sr oficial recuperado. Nulo em qualquer eixo permanece desconhecido; nenhum cruzamento cria sozinho uma fórmula nova.

`Atividade` permanece na fonte original, mas foi retirado dos filtros analíticos por decisão humana. Não foi usado como eixo da matriz nem como classificação oculta. As famílias abaixo são propostas interpretativas para selecionar fichas; não são de-para histórico aprovado, recodificação do cadastro ou classificação calculada a partir de nomes.

| Família proposta | Categorias literais de SegmentoTb a examinar | Tcb como pista, sem regra suficiente |
|---|---|---|
| Intermediação bancária diversificada/depositária | Banco Comercial; Banco Comercial Estrangeiro - Filial no país; Banco Múltiplo; Banco do Brasil - Banco Múltiplo; Caixa Econômica Federal | B1/B2; conferir licenças, carteira e captação do perímetro. |
| Bancos cooperativos | Banco Comercial Cooperativo; Banco Múltiplo Cooperativo | Banco cooperativo e cooperativa singular não são a mesma unidade. |
| Desenvolvimento/fomento | BNDES; Banco de Desenvolvimento; Agência de Fomento | B4 e N1 conforme unidade; não transportar norma de banco estadual ao BNDES ou agência. |
| Cooperativas e estruturas centrais | Cooperativa de Crédito; Confederação de Serviços | B3S/B3C; subtipos, centralização financeira, serviços e sobreposição precisam conferência; não proibir L2 por família. |
| Crédito especializado/não bancário | Sociedade de Crédito, Financiamento e Investimento; Sociedade de Crédito ao Microempreendedor; Sociedade de Crédito Direto; Sociedade de Empréstimo entre Pessoas | N1 é pista; exposição própria e intermediação de terceiros precisam separar-se. |
| Imobiliário e arrendamento | Associação de Poupança e Empréstimo; Companhia Hipotecária; Sociedade de Crédito Imobiliário - Repassadora; Sociedade de Arrendamento Mercantil | Adequação depende de carteira e passivo próprios; crédito e arrendamento não se concatenam automaticamente. |
| Mercado de capitais, investimento e câmbio | Banco de Investimento; Banco de Câmbio; Sociedade Corretora de Câmbio; Sociedade Corretora de TVM; Sociedade Distribuidora de TVM | B2/N2; tesouraria, conta própria e serviços podem coexistir; não impor carteira de empréstimos como produto único. |
| Pagamentos | Instituição de Pagamento | N4; modalidade e salvaguarda próprias, não depósitos bancários genéricos. |
| Sem classificação observada ou família inconclusiva | SegmentoTb nulo, Tcb nulo, combinações conflitantes, unidade consolidada sem decomposição suficiente | Manter medidas contábeis válidas e marcar adequação desconhecida. Não excluir do total nem atribuir família por nome. |

Os 26 rótulos acima são os observados junto aos datasets de valores no núcleo, segundo o inventário antecedente; o cadastro geral possui 30, inclusive unidades sem valores. B3/N3 aparecem no cadastro amplo, sem de-para certificado e sem observação financeira equivalente no recorte 113; não fabricar cobertura nem traduzir por semelhança. A matriz determinística atualizada é a autoridade para contagens do corpus usado.

## Prioridades determinadas pelo sistema inteiro

O universo principal de seleção e avaliação dos indicadores é o **sistema observado completo**, por perspectiva e trimestre. O recorte das companhias associadas é complementar. As recomendações abaixo partem de todas as 89476 posições financeiras, 99401 individuais e 55124 de capital; os 43086 registros de Segmentação técnica apoiam interpretação própria. Nenhuma família precisa estar entre as companhias abertas para entrar na pesquisa.

### Financeiro: todos os Tcb, 2010–2024

As três colunas de presença para LA, E2-B e Q1 coincidem neste corpus: os mesmos conjuntos contemporâneos são finitos, incluindo zeros. Isso evidencia que **oferta contábil semelhante não significa adequação econômica semelhante**. A coluna DV positivo provém do diagnóstico 140 sobre todo o universo e não serve como classificação de licença. AT conhecido é soma observada em 202412, sem eliminações entre grupos.

| Tcb observado | Unidades-trimestre | Componentes conjuntos LA/E2-B/Q1 | DV positivo/L2, toda janela | Unidades em 202412 | AT conhecido em 202412, R$bi |
|---|---:|---:|---:|---:|---:|
| B1 | 5853 | 5847 | 5452 | 97 | 14211,349 |
| B2 | 2092 | 2091 | 217 | 31 | 330,077 |
| B3S | 60515 | 60064 | 44832 | 753 | 803,857 |
| B3C | 2189 | 2178 | 358 | 29 | 204,207 |
| B4 | 240 | 240 | 69 | 4 | 875,858 |
| N1 | 7988 | 7888 | 202 | 226 | 316,895 |
| N2 | 9120 | 9020 | 0 | 136 | 22,389 |
| N4 | 1440 | 1427 | 8 | 146 | 715,982 |
| Desconhecido | 39 | 27 | 5 | 0 | — |

Cooperativas B3S/B3C respondem por 62704 posições, com modelos singulares, centrais e serviços que não se reduzem a bancos comerciais. B4 tem 240 posições e apenas 69 DV positivos: LA/LC/LF e maturidade respondem à lacuna de toda a família de desenvolvimento, incluindo BNDES. N2 tem 9020 posições com os componentes propostos e nenhum DV positivo; N4 tem 1427 com componentes e somente oito DV positivos. N1 tem 7888 com componentes e 202 DV positivos. Esses padrões justificam pesquisar serviços, funding não depositário e obrigações específicas por modelo, sem escolher métricas pela situação das 32 companhias.

As 70 unidades financeiras com SegmentoTb desconhecido em 202412 continuam no universo e na matriz. Não converter rótulos genéricos de conglomerado, ausência ou conflito em família de negócio. Comparações por Tc/Td/Sr/SrAnalitico explicam diferenças de controle, consolidação e regime; não criam novas fórmulas para cada cruzamento.

### Financeiro: todas as categorias SegmentoTb observadas

Esta tabela abrange os 25 rótulos financeiros e desconhecidos. Os 26 rótulos da união das perspectivas incluem um rótulo adicional Individual, preservado separadamente. Referências com valor observado não datam criação/extinção da atividade ou mudanças de licença; a matriz integral registra cada trimestre e o cadastro literal.

| SegmentoTb literal | Referências observadas | Unidades-trimestre | Componentes conjuntos LA/E2-B/Q1 | Unidades em 202412 |
|---|---:|---:|---:|---:|
| Desconhecido | 60 | 4630 | 4606 | 70 |
| Agência de Fomento | 60 | 955 | 944 | 16 |
| Associação de Poupança e Empréstimo | 60 | 84 | 81 | 1 |
| BNDES | 60 | 60 | 60 | 1 |
| Banco Comercial | 60 | 326 | 325 | 5 |
| Banco Comercial Cooperativo | 4 | 4 | 4 | 0 |
| Banco Comercial Estrangeiro - Filial no país | 60 | 159 | 159 | 2 |
| Banco Múltiplo | 60 | 3262 | 3261 | 58 |
| Banco Múltiplo Cooperativo | 60 | 60 | 60 | 1 |
| Banco de Desenvolvimento | 60 | 180 | 180 | 3 |
| Banco de Investimento | 60 | 282 | 281 | 4 |
| Caixa Econômica Federal | 46 | 46 | 46 | 0 |
| Companhia Hipotecária | 60 | 235 | 235 | 4 |
| Cooperativa de Crédito | 60 | 62702 | 62242 | 780 |
| Sociedade Corretora de Câmbio | 60 | 3183 | 3140 | 51 |
| Sociedade Corretora de TVM | 60 | 2305 | 2284 | 21 |
| Sociedade Distribuidora de TVM | 60 | 3365 | 3334 | 61 |
| Sociedade de Arrendamento Mercantil | 60 | 271 | 270 | 4 |
| Sociedade de Crédito Imobiliário - Repassadora | 56 | 261 | 234 | 0 |
| Sociedade de Crédito ao Microempreendedor | 60 | 1949 | 1913 | 20 |
| Sociedade de Crédito, Financiamento e Investimento | 60 | 2260 | 2249 | 51 |
| Banco de Câmbio | 44 | 69 | 69 | 3 |
| Instituição de Pagamento | 29 | 1440 | 1427 | 146 |
| Sociedade de Crédito Direto | 24 | 1219 | 1211 | 107 |
| Sociedade de Empréstimo entre Pessoas | 23 | 167 | 167 | 11 |
| Confederação de Serviços | 1 | 2 | 0 | 2 |

As categorias de presença rara ou curta também orientam a seleção: SCD/SEP exigem separar carteira própria e intermediação, arrendamento exige abrangência própria, confederação de serviços não deve receber uma carteira presumida. Os dois casos de Confederação de Serviços em 202412 têm null nativo no conjunto examinado, conservado como lacuna de dados. Nenhum caso é retirado por não existir nas companhias associadas.

**Ordem de implementação proposta para o sistema:** (1) LA/LC/LF em famílias não depositárias e depositárias, com casos e nulos de todas as categorias; (2) RS e composição da renda para mercado de capitais, câmbio, pagamentos e bancos mistos, antes de alterar E2-B; (3) R4/R5 e E3 como explicações compatíveis; (4) fontes de maturidade/salvaguarda/contraparte/NPL conforme a pergunta. Benefício cooperativo e mandato de desenvolvimento permanecem limites econômicos próprios. A nova lista de companhias não determina essa ordem.

O sistema completo, as vinculadas, o restante e o vínculo desconhecido permanecem quatro leituras; o total inclui os três recortes exclusivos. No Prudencial e Individual, as mesmas seis segmentações são examinadas na matriz, com conceitos e denominadores próprios. Não transportar a composição financeira às demais perspectivas.

## Cobertura atualizada: presença, denominador e representatividade

O inventário A1 e a consulta A2 autenticaram entradas e preservaram hashes. A2 examinou 160 partições/períodos: 60 Financeiro, 60 Individual e 40 Capital, 38 conjuntos candidatos (25 da 111 + 13 diagnósticos), sem avaliar razão financeira. A matriz integral tem 513565 linhas após acrescentar os dois conjuntos de capital da fórmula; o resumo tem 25335. O arquivo de componentes conserva 212 contextos com observação em 2010–2024, dentro do catálogo 438 que também inclui 2025–2026, com chave JSON tipada e listas explícitas de períodos. O JSON distingue Grupo nulo de vazio.

No universo com valores há 25 rótulos SegmentoTb no Financeiro, 26 no Individual e seis em Capital/Segmentação. O 26º da união, Banco do Brasil - Banco Múltiplo, não foi imputado ao Financeiro. Os oito Tcb, três Tc, cinco Sr e cinco SrAnalitico mantêm distribuição por perspectiva/data, inclusive nulos e conflitos. Td tem apenas I em Individual; isso não prova independência societária. A Segmentação técnica não dispõe de SrAnalitico 136: `not_in_attribute_scope` é distinto de ausência cadastral.

### Universo financeiro, 60 trimestres

| Componente/conjunto | Presença finita conjunta ou estado nativo | Interpretação permitida |
|---|---:|---|
| ROA/ROE, Q1/Q2, C1, L2/L3, E2-B e novos LA/LC/RS/E3/LF | 88782/89476 unidades-trimestre; 694 com null; em 202412, 1415/1422 | Presença contemporânea, inclusive zero/negativo; **não calculabilidade da fórmula/janela**. Histórico/médias e denominador ainda restringem. |
| AT | 88781 positivos, 1 negativo, 694 null | AT negativo preservado, sem correção ou exclusão automática. |
| PL | 88258 positivos, 521 negativos, 3 zero, 694 null | ROE exige média; sinal pode inverter interpretação, cobertura nominal não resolve. |
| Crédito 78191 | 76026 positivos, 12756 zero, 694 null | Presença não demonstra exposição própria relevante para toda atividade. |
| DV/L2 | 51143 positivos, 37639 zero, 694 null | Reproduz diagnóstico 140; L2 observado não cobre universalmente liquidez. |
| Depósitos totais/L3 | 60599 positivos, 28183 zero, 694 null | Depósitos não são funding universal. |
| Captações Passivo 3/78185 | 64795 positivos, 23987 zero, 694 null | LF tem base observada além de depósitos, mas não todas as obrigações/recursos do balanço. |

Em 202412, os 1415 AT finitos somam R$ 17480613833662,29; sete AT são desconhecidos. O mesmo conjunto possui os componentes contemporâneos dos candidatos prioritários, logo alcança todos os **ativos conhecidos**, sem afirmar cobertura do ativo econômico total. LA/LC têm AT positivo nas 1415 posições dessa data; isso ainda não certifica liquidez própria. Para L2, apenas 676/1422 unidades têm denominador positivo e o diagnóstico 140 mede 85,96588287% do AT conhecido; para L3 são 969 denominadores positivos, e para LF 1024. Não escolher a fórmula pelo percentual mais alto.

**Financiamento conciliado:** nas 88782 posições financeiras e 98713 individuais com as cinco rubricas finitas, `CaptaçõesPassivo3 = DEP + compromissadas + emissões + empréstimos/repasses` exatamente em Decimal. Zero divergências também entre Captações Resumo 1 e Passivo 3 nessas posições. 694 Financeiro/688 Individual não têm o conjunto completo. A identidade sustenta ajuste delimitado LF, sem provar funding total, maturidade, origem FAT, disponibilidade ou continuidade normativa.

### Capital: separar fórmula e controle publicado

| Conjunto em 55124 posições prudenciais de 2015–2024 | Dois componentes finitos da fórmula | Também índice publicado finito | Diferença |
|---|---:|---:|---:|
| C3 PR/RWA | 53799 | 53392 | 407 |
| C4 CP/RWA | 29617 | 29225 | 392 |

As 799 posições da diferença **não são recuperação de resultados**: demonstram que exigir o índice publicado como terceiro input subestima presença dos dois componentes. No CSV, `C3_core/C4_core` são dois componentes; `C3/C4` conservam o conjunto de três controles da 111. RWA zero, CP null, regime e sobreposição continuam próprios; não chamar 53799 ou 29617 de resultados válidos. O diagnóstico 139 de 12138 C4 elegíveis em 2018–2024 usa janela/denominador válido, não é contradito pela contagem de presença em 2015–2024.

### Companhias: histórico antigo e decisão corrente separados

Na amostra histórica 24, reaparecem 1430/1440 combinações companhia/trimestre com componentes contábeis: BR Partners não tem operadora nativa mapeada nas nove referências 201003–201203; BRB tem null em 202209. C3/C4 core têm 959/932 combinações, respectivamente; capital pré-2015 não é emendado. A matriz nominal inteira conserva companhia, código, trimestre, candidato e motivo, sem exigir interseção de todas as dimensões para permanecer na amostra.

**Corte documental 142 em 202412:** 32 companhias/24 códigos financeiros têm componentes contemporâneos para o núcleo contábil e os complementos LA/LC/LF/RS/E3; C3 core tem 32 companhias/24 códigos prudenciais correspondentes; C4 core tem 31/23. **Cielo**, financeira 01027058 → prudencial C0084710, tem CP nulo, e não foi excluída da amostra ou preenchida com PR. Trata-se de presença, sem projetar vínculos ou comparabilidade ao passado.

L2 tem DV positivo para **27/32 companhias e 19/24 unidades** do corte; cinco companhias/unidades têm DV zero: Porto Seguro/Portoseg C0051444, BR Partners 13220493, DM Financeira C0052357, Cielo 01027058, Oliveira Trust/DTVM 36113876. Depósitos totais e captações têm denominador positivo para as 32/24 no corte; isso não os torna medidas suficientes de liquidez. Os números antigos 21/24 companhias e 17/20 unidades L2, do diagnóstico 140, continuam históricos; não são a cobertura da nova lista.

| Soma dos 24 códigos financeiros conhecidos em 202412 | R$ | Participação aritmética no universo observado conhecido, sem eliminações |
|---|---:|---:|
| AT | 9773403343238,74 | 55,90995509% |
| Crédito 78191 | 3277383756212,85 | 53,20250054% |
| PL | 786641485824,87 | 49,99594687% |

Todos os 24 valores dessas três rubricas são conhecidos; os denominadores observados são AT 17480613833662,29, crédito 6160206235951,83 e PL 1573410516537,41. Esses percentuais são diagnóstico de somas nativas, **não representatividade estatística, cobertura integral do SFN ou agregado consolidado livre de sobreposição**. Companhia ≠ unidade: 32 nomes não criam 32 balanços. Controle compartilhado Cielo/BB/Bradesco e vínculos indiretos têm ressalvas na 142; não contar novamente por companhia, nem atribuir todo grupo à subsidiária.

As 23 sem correspondência principal permanecem nominadas no corte: Investimentos Bemge, Alfa Holdings, BB Seguridade, Caixa Seguridade, IRB Brasil Resseguros, Qualicorp, Wiz, XP Investimentos S.A., Reag Capital Holding, BNDESPAR, Cia Participações Aliança Bahia; Brazilian Securities, SECME, PDG Securitizadora, Infrasec, Leads, Travessia Securitizadora, Cia Sec Cartões Consignados I, Cia Sec Cartões Consignados II, Travessia Securitizadora Créditos Financeiros, Porto Vitória Securitizadora, Travessia Créditos Mercantis VI e AUZZA. Não receberam valor zero ou não aplicabilidade; exigem fonte/perímetro adicional se o objetivo passar a medir suas demonstrações próprias. Identidades CNPJ/CVM, nomes exatos, unidades elegíveis e faltantes por categoria/data estão nas tabelas nominais da proveniência.

## Crítica das dez métricas atuais

| Métrica | Manutenção/adaptação proposta | Limite e complemento necessário |
|---|---|---|
| ROA/ROE | Manter LL e médias adotadas; separar quarter/TTM e explicitar objetivos do negócio. | ROE elevado pode refletir alavancagem/PL negativo. Sobras cooperativas e mandato público não medem benefício total pelo lucro. Ponte LL 2019 tem prova delimitada; não generalizar alteração literal. Margem/mix ajudam explicar. |
| Q1 provisão/crédito | Manter como intensidade de provisionamento. | Estoque de proteção contábil não mede atraso. Crédito nulo não prova ausência de toda exposição de crédito/contraparte. Arrendamento exige contrato próprio. |
| Q2 custo de provisão/crédito médio | Manter quando carteira, despesa/reversão e janela têm abrangência compatível. | Variação do estoque não é despesa. Reversão negativa é informação. Complementar com NPL somente de fonte/definição compatível. |
| C1 PL/AT | Manter como capitalização contábil comum. | Não é folga regulatória nem capital principal. Seu inverso AT/PL é apresentação redundante, não outra dimensão independente. |
| C3 PR/RWA | Manter prudencial separado, com regime e cobertura. | Não prolongar automaticamente ao capital financeiro pré-2015; não usar limiar uniforme histórico nem equiparar PR a CP. |
| C4 CP/RWA | Manter onde disponível, assinalando quebra de 2018 e regimes. | Null não vira PR/zero. C3 mede outro conceito e complementa C4 sem preenchê-lo. Alternativa PR S5 requer norma/opção/perímetro próprios. |
| L2 (disponibilidades+AIL)/DV | Manter leitura específica para exposição a DV. | DV zero é indefinição matemática, não falta de liquidez; BNDES e IP exigem alternativas. Não denominar LCR. |
| L3 crédito/depósitos | Manter como dependência relativa de depósitos quando representam funding. | Para desenvolvimento/letras/repasses, incorporar perfil de financiamento; trocar denominador cria indicador novo. Não usar crédito/depósitos como liquidez universal. |
| E2-B | Manter como proxy estreita custo/renda selecionada; diagnosticar composição de receitas antes de comparar famílias. | Não é eficiência técnica, IEO literal de Assaf ou índice BCB reproduzido. Outras receitas/participações podem dominar. E3 e participação de serviços complementam; E2-C não se resolve pelo nome Resultado Operacional. |

Assaf, 11. ed., 2015, pp. 333–335, 337, 341–342, foi relido nesta rodada; pp. 321–331 e suplemento de critérios/estatística são reaproveitados da 111. O livro orienta interpretação bancária e análise contextual; suas afirmações didáticas sobre relação crédito/liquidez/retorno não são hipóteses causais demonstradas para todos os modelos, nem seu exemplo histórico de capital define mínimos regulatórios de 2010–2024.

## Contrato comum das fichas propostas

**Quebras a preservar nos novos recortes:** LL/DRE muda conceito em 201903; o Passivo Total 78300 muda definição em 202212 e não é exigível por presunção; a composição de Outros Depósitos 78285 muda em 202006, passando a subtrair COSIF41930005 e a usar o rótulo Depósitos Outros (a6), distinto de Outros Depósitos (a5) anterior. As listas exatas do catálogo separam as variantes. Não montar uma soma histórica de cinco folhas de depósitos ignorando a rubrica pré-paga ou a mudança de abrangência. Regimes CP/PRS5 pós-2018, início Sr e 2025 permanecem separados. Essas mudanças não invalidam automaticamente todo indicador: delimitam o que precisa de conciliação antes de uma adaptação.

Classes: **1** fundamentado e calculável com componentes/contratos atuais demonstrados; **2** adaptação fundamentada que exige ajuste delimitado; **3** relevante, exige fonte adicional ou abertura não instalada; **4** inadequado, redundante ou suporte insuficiente para a pergunta. Presença conjunta de saldos não promove automaticamente 2 a 1. Uma alternativa 3 pode ser prioritária apesar de pouca cobertura; uma 4 pode ter cobertura alta.

Notação: `xNNNNN` é saldo assinado da Conta, com dataset/tipo/relatório/grupo/definição exatos da matriz de componentes. Conta não é código COSIF. `AT=x78182`, `PL=x78186`, `LL=x78187`, `CR=x78191`, `P=x78192`, `DISP=x78188`, `AIL=x78189`, `TVMD=x78190`, `DV=x78282`, `DEP=x78287`, `EM=x78294`, `REP=x78295`. No contexto financeiro Tipo 2: AT/PL/LL no Resumo 1; demais ativos no relatório 2; passivos no relatório 3; DRE no relatório 4. Prudencial usa dataset capital/Tipo 1/relatório 5. Contexto Individual Tipo 3 exige binding/prova próprios, nunca mera troca de rótulo.

Para a DRE compatível, `C=−(x78218+x78219)` e `S=x78215−x78213+x78216+x78217`: custos de pessoal/administração e renda selecionada antes da provisão. Sinais negativos nativos são preservados; `abs()` generalizado é proibido. Essas construções reaproveitam a implementação E2-B já adotada; sua aplicação a famílias não certifica que S seja receita operacional total.

Estoque/estoque: mesma referência, fotografia trimestral, síntese de dezembro; fluxo/fluxo: mesma janela efetiva ou TTM disjunto; fluxo/estoque: denominador médio temporal com abertura e observações intermediárias, conforme motor atual. Não anualizar trimestre multiplicando por quatro nem diminuir janela para aumentar cobertura. Fonte/revisão/perímetro/nome/definição fazem parte da compatibilidade.

Zero no denominador produz indefinido; zero legítimo no numerador é resultado, não missing. Null/binding ausente/história insuficiente/incompatibilidade de definição são estados distintos. Negativo válido é preservado e sinalizado; receitas/AT/PL negativos retiram interpretação usual e exigem relato, sem exclusão silenciosa. Razão de somas usa exatamente a mesma interseção válida para numerador e denominador; mediana descreve outra pergunta. Não misturar LA com L2 ou métricas regulatórias numa média única.

## Fichas recomendadas e candidatas

### R1/R2 — retorno dos recursos e capital contábil

**Pergunta/dimensão:** quanto resultado líquido a unidade gera por recursos empregados/capital próprio; rentabilidade. **Fórmula:** LL da janela/AT médio ou PL médio, em %; lucro ou prejuízo mantém sinal. **Fundamento:** Assaf, p. 341, releitura; médias são adaptação temporal já adotada, não fórmula literal do livro. FMI final de 2019, pp. 90–91, §§7.46–7.55, explicita média de AT e preferência de ROA antes de tributos, distinta da definição LL adotada. Não atribuir PL médio literalmente ao §7.52 nem converter o recibo draft da 111 em final.

**Aplicação:** todas as famílias com demonstração compatível, leitura de sustentabilidade para cooperativas/desenvolvimento, sem ranking universal de sucesso. Financeiro principal; Individual separado; lucro prudencial ausente não é emprestado do Financeiro. Componentes 78187/78182/78186 e histórico da própria unidade. **Classe 1** no contrato atual e nos alvos da ponte de 2019 já aceitos; histórico/definição/abertura não demonstrados continuam indisponíveis. PL zero indefinido, negativo sinalizado; agrega por razões de somas com PL negativo explicitado e sem alegar ponderação convexa. **Alternativas:** R4, RS e E3 para mecanismos; ROA antes dos tributos é sensibilidade de classe 2 após conciliar 78226, não substituição automática.

### Q1/Q2 — proteção reconhecida e custo de perdas

**Pergunta/dimensão:** intensidade da proteção contábil e incidência de perdas reconhecidas; qualidade do crédito parcial. **Fórmulas:** provisão em magnitude econômica conciliada/CR bruto na data; `−x78213/CRmédio` na janela compatível, preservando reversões. Percentuais. **Fundamento:** Assaf, p. 324 (reaproveitado da 111); CMN 2682, arts. 1–9, e REF de novembro de 2024, p. 37/gráfico 1.2.3.6 (reaproveitados); nenhuma equivalência com inadimplência.

**Aplicação:** crédito próprio de bancos, desenvolvimento, cooperativas e não bancárias, sob abrangência compatível; não impor a IP/serviços sem carteira. Contextos Ativo 2/78191+78192 e DRE 4/78213; quarter/TTM com média da mesma carteira. **Classe 1** nas definições atuais; adaptação a arrendamento/crédito fora da abrangência é 2 e exige contrato. Denominador zero indefinido; não aplicável só com prova econômica, não pela ausência. Agregação mesma carteira/interseção, sem somar provisão genérica e específica em duplicidade. **Complementos de classe 3:** NPL 90+, provisionamento específico/NPL, baixas/recuperações se a fonte não os demonstrar; risco de contraparte de N2/N4 exige abertura própria.

### C1/C3/C4 — capital contábil e capital regulatório separados

**Pergunta/dimensão:** suporte próprio do balanço e suporte elegível frente a riscos; capital/alavancagem. **Fórmulas:** PL/AT %; PR 79649/RWA 79665 %; CP 79645/RWA 79665 %, cada qual no próprio perímetro. **Fundamento:** Assaf, p. 337 (releitura); normas CMN/BCBS/FMI da 111 e diagnóstico 139. **Aplicação:** C1 comum; C3/C4 somente unidades/regimes prudenciais pertinentes, 40 trimestres admitidos de 2015–2024. **Classe 1** para definições atuais; reconstrução de capital financeiro pré-2015 ou PR S5 específico é 2/3 até componentes e regime comprovados.

Estoque na data, dezembro síntese. AT/RWA zero indefinido, PL negativo preservado, CP nulo desconhecido sem imputação. Índices publicados não se somam; razão de somas CP/RWA/PR só em população/perímetro compatível sem sobreposição comprovada. **Alternativas de classe 4:** AT/PL como nova dimensão (recíproco de C1); CP=PR; folga uniforme de 11/13%; norma S1 aplicada a S5. Folga regulatória própria é 3 por cronologia/individualização ainda incompleta.

### L2/L3 — relações de liquidez e financiamento dos modelos depositários

**Pergunta/dimensão:** ativos de caixa/AIL frente a DV, e carteira financiada relativamente a depósitos. Fórmulas `(DISP+AIL)/DV` e `CR/DEP`, %, mesmo estoque/data. **Fundamento:** Assaf, pp. 334–335, releitura. Contextos 2/78188+78189, 3/78282; 2/78191, 3/78287. **Classe 1**, interpretação restrita ao denominador econômico; famílias depositárias de bancos/cooperativas, outras unidades com denominador observado exigem exame do perímetro. Não classificar licença apenas por Tcb.

DV/DEP zero indefinido, null desconhecido, negativo sinalizado sem interpretação usual; aplica contrato comum de agregação. L3 elevado pode refletir REP/EM, não crise; **não usar L2/L3 como medição suficiente da dimensão em desenvolvimento, IP ou mercado de capitais**. Não reduzir zeros ou adaptar fórmula com depósitos totais silenciosamente. Alternativas LC/LA/LM/LS abaixo; maturidade/estresse exige classe 3.

### LA — participação de disponibilidades e AIL no ativo

**Pergunta/dimensão:** qual parcela dos recursos está nas duas classes contábeis associadas a caixa/aplicações interfinanceiras; composição do ativo como apoio à liquidez. **Fórmula candidata:** `(DISP+AIL)/AT`, %, estoque trimestral. **Fundamento:** adaptação explícita do projeto a partir de Assaf, pp. 333–335 e conceito FMI de liquid assets/AT, cuja elegibilidade não está reproduzida. **Classe 2**, não FSI líquidos/AT certificado.

**Aplicação:** todas as famílias com balanço, especialmente desenvolvimento e crédito não depositário; pagamentos exigem separar recursos salvaguardados e livres. Contextos Financeiro 2/relatório 2/78188+78189 e Resumo 1/78182. Disponibilidade conjunta é contemporânea; não requer lag. AT zero indefinido; caixa/AIL zero observado é informação; negativo preservado e investigado. **Interpretação:** mais participação contábil não prova capacidade de resgate, ausência de restrições ou liquidez sob estresse. Agregar soma dessas classes/soma AT no mesmo conjunto. Não incluir TVMD 78190 genericamente: derivativos, restrições e negociabilidade impedem considerá-lo HQLA. Alternativa de classe 3 é elegibilidade/maturidade dos ativos; alternativa de classe 4 é batizar LA de LCR/IL BCB.

### LC — participação do crédito no ativo

**Pergunta/dimensão:** intensidade da aplicação em crédito, para contextualizar liquidez/financiamento e modelo, não rentabilidade realizada. **Fórmula:** CR/AT %, estoque na data. **Fundamento direto:** Assaf, p. 335, releitura; carteira de menor liquidez comparada a caixa depende cessão, garantias e maturidade. **Classe 2** para especificar CR bruto 78191 em vez da carteira 78183 classificada; duas rubricas não são intercambiáveis. Após aceitar binding/abrangência, implementação seletiva simples.

**Aplicação:** bancos, desenvolvimento, cooperativas, não bancárias e imobiliário compatível; não classificar ausência de crédito em serviços como pior desempenho. Financeiro Tipo 2/Ativo 2/78191+Resumo 1/78182. AT zero indefinido, CR zero resultado, null desconhecido. Dezembro fotografia anual, não média de fluxos. Agregação soma CR/soma AT, comparável sob composição/perímetro. Não mede qualidade, maturidade, demanda de caixa nem contribuição social. Complementa LA/LF, não substitui medida de obrigações.

### LF — perfil de financiamento por fontes contábeis

**Pergunta/dimensão:** dependência de depósitos, operações compromissadas, instrumentos emitidos e empréstimos/repasses; financiamento. **Fórmula candidata prioritária:** participações `DEP/F`, `OC/F`, `EM/F`, `REP/F`, com `OC=x78288` e `F=x78185` no **Passivo 3**, após conciliar a identidade de quatro rubricas e sua abrangência. Assaf, pp. 321–325 (reaproveitadas da 111) e 333–335 (releitura) fundamentam o mecanismo; percentuais são adaptação própria. **Classe 2**. A cesta histórica L4 de três rubricas `DEP+EM+REP` permanece alternativa parcial explicitamente nomeada, sem ser confundida com a base que inclui compromissadas.

Financeiro Tipo 2/Passivo 3/78287+78288+78294+78295, comparados ao pai 78185. O catálogo localiza 78185 tanto no Resumo 1, Grupo nulo, quanto no Passivo 3, Grupo Captações, com chave própria: não somar os dois. O Passivo identifica `(e)=(a)+(b)+(c)+(d)` e descrição `[41000007]+[42000006]+[43000005]+[46000002]`; a identidade de tokens e o residual precisam ser conferidos, sem forçar igualdade ou completar null. Datas trimestrais; zero em F indefinido, fonte zero é participação zero, negativos/reclassificações sinalizados. Agregar somas das mesmas rubricas/base nos mesmos códigos. **Aplicação:** depositárias, desenvolvimento e crédito não bancário; N2/N4 podem ter outras obrigações principais, e F zero não significa ausência de financiamento.

**Limite substantivo:** mesmo a base nativa de captações não demonstra todas as fontes de financiamento do balanço, nem identifica separadamente FAT, recursos vinculados, exigibilidade, estabilidade e vencimento. Banco de desenvolvimento exige composição das fontes institucionais e cronograma. Não trocar F por Passivo Total 78300 sem remover PL/conciliar definições. Alternativa de classe 3: decomposição necessária via abertura oficial adicional; classe 4: tratar F como ASF/NSFR ou receita de captação. Fontes bibliográficas sobre desenvolvimento não autorizam nova ingestão financeira.

### LM/LS — maturidade, recursos livres e salvaguarda

**Pergunta/dimensão:** ativos realmente mobilizáveis cobrem obrigações exigíveis nos horizontes pertinentes? **Candidatos de classe 3:** FMI ativos líquidos/passivos de curto prazo, GAPs de vencimento/fluxos previstos para desenvolvimento e funding institucional; LCR/NSFR no escopo próprio; IP recursos elegíveis de salvaguarda/obrigações correspondentes, por modalidade e data. Não são uma fórmula intercambiável.

FMI/BCBS definem elegibilidade/horizonte; para IP normas distintas disciplinam recursos dos usuários. IF.data Resumo/Ativo/Passivo/DRE sem maturidade, restrição e obrigações segregadas não basta. **Contas/contextos exatos não identificados no corpus admitido**, não inventar denominações COSIF. Logo disponibilidade conjunta não aferível com os quatro relatórios; cobertura deve constar como requisito não observado, não zero unidades aplicáveis. Fonte adicional/revisão/quebra e escopo exigem contrato próprio. Nulos não recebem hipótese de plena fungibilidade. Comparar famílias só por pergunta coerente; não somar cobertura regulatória de IP com LCR bancário.

### R4/R5 — margem financeira e rendimento do crédito

**Pergunta/dimensão:** de onde vem retorno? `x78215/ATmédio` e `x78203/CRmédio`,% na janela real/TTM. Assaf, p. 342, direto; média é adaptação da fórmula de estoque do livro. **Classe 2**, pois janela/sinal/abrangência das novas rubricas e carteira produtora precisam de contrato, embora componentes estejam no corpus.

**Aplicação:** intermediação/crédito compatível; serviços/N2/N4 podem ter leitura parcial. Financeiro Tipo 2/DRE 4/78215 ou 78203 e Resumo 1/78182 ou Ativo 2/78191 com lags. RBIF contém provisão; não chamar de margem líquida de juros (NIM) nem spread contratual. Preservar prejuízo/reversão; denominador zero indefinido, média ausente indisponível. Agrega fluxos/somas de estoques médios válidos, sem substituir a temporalidade. Custo de captação/depósitos a prazo do livro não é universal quando o funding é REP/EM/FAT; candidato fora da prioridade até abrangência conciliada.

### RS — papel das receitas de serviços e tarifas

**Pergunta/dimensão:** quanto da renda selecionada vem de serviços, para explicar rentabilidade e adequação de E2-B? `(x78216+x78217)/S`,% fluxo/fluxo. **Classe 2**, adaptação analítica própria; não fórmula atribuída literalmente a Assaf/FMI. Fonte conceitual: Assaf, DRE pp. 321–322/retorno p. 341, e FMI, renda líquida de juros + não juros; contraprova E2-C da 111 mostra itens omitidos.

**Aplicação:** mercado de capitais/câmbio/pagamentos, bancos de serviços e cooperativas centrais; não medir produtividade física nem volumetria transacional. Financeiro Tipo 2/DRE 4/78215,78213,78216,78217, mesmo trimestre/TTM disjunto. S zero indefinido; S negativo mantém valor/sinal sem interpretação de participação convexa; parcela >100% pode refletir resultado negativo em intermediação, não erro automático. Agregar somas de serviços/soma S no mesmo conjunto, comparando S com outras rendas sempre que disponíveis. Se outras rendas dominarem, nova renda operacional ampla requer E2-C/ajuste delimitado, sem inventar fonte.

### E2-B/E3 — custo relativo à renda e aos recursos

**Pergunta/dimensão:** como custos de pessoal e administração se relacionam com renda selecionada e escala? `C/S` é E2-B vigente, classe 1; `C/ATmédio` é E3 candidata, classe 2. Assaf, p. 342, para IE literal e FMI para cost-income, diferenças explicitadas. E3 é complemento proposto do projeto, não eficiência técnica publicada por Tecles/Tabak. Contextos Financeiro 2/DRE 4/78218+78219, S e AT 78182 com abertura/tempo.

**Aplicação:** todas as famílias com custos/renda compatíveis, com separação entre modelos; para operação de serviços, AT baixo pode aumentar E3 sem menor produtividade. C negativo por reversão preservado, S zero indefinido/S negativo sinalizado, AT zero indefinido; quarter/TTM, não somar custo de trimestres acumulados. Agrega C/S ou C/soma AT médio em interseções próprias. **Alternativas:** IE literal de Assaf/E2-C e DEA/SFA permanecem 2/3/4 conforme pergunta/de-para/dados de produtos; não implementar fronteira para completar tabela. Contas de outras despesas 78223 não equivalem a todas as operacionais.

## Destino dos demais candidatos da 111

As 25 fichas antecedentes foram conservadas na auditoria, incluindo candidatas sem componentes comprovados. A avaliação abaixo completa as fichas priorizadas; ausência de implementação não é reprovação conceitual.

| Candidato antecedente | Classe e recomendação nesta revisão |
|---|---|
| R3 LL/RIF | 2: margem específica de intermediação, baixa prioridade diante de RS e composição de receitas. Não é margem sobre toda receita operacional. |
| R6 antes de tributos/AT médio | 2: sensibilidade conceitualmente relevante, conciliar 78226 e seus itens; não substituir LL por Resultado Operacional. |
| C2 AT/PL | 4 como ampliação informacional: é recíproco de C1; pode ser apresentado em vezes sem contar como outro fator independente. |
| C5 folga regulatória | 3: cronologia, adicionais, regime e opção da unidade ainda necessários; mínimo uniforme histórico seria 4. |
| L1 disponibilidades/DV | 2: complemento analítico de encaixe, baixo ganho frente a L2 e decomposição; não resolve modelos sem DV. |
| L4 cesta de financiamento | 2: manter cesta parcial histórica explicitada; priorizar LF com compromissadas e captações conciliadas. |
| L5/L6 LCR/NSFR | 3: elegibilidade, estresse, vencimentos e ponderações ausentes do corpus; reconstrução genérica por TVM é 4. |
| Q3/Q4 NPL e cobertura específica | 3: relevantes para qualidade do crédito, sem componentes de atraso/default/provisão específica demonstrados nos quatro relatórios instalados. |
| E1 IE literal Assaf/E2-C reprodução BCB | 2/3: não há de-para conciliado de todas as despesas/rendas; pesquisa delimitada pode aproveitar contas locais, e abertura adicional depende da lacuna identificada. Não trocar nome de E2-B. |
| E4 IE de fomento | 4 para reprodução imediata: PECLD/estoque/fluxo/sinal não conciliados. Souza et al. 2021 continua contraponto de atividade, não fórmula pronta. Pode voltar à avaliação após resolver o conceito, sem ser adotado só por citar fomento. |

QL (provisão/arrendamento), margem LL/S e receitas de serviços/AT são adaptações de classe 2 auditadas como alternativas. Para QL, os candidatos 78194/78197 têm abrangência própria; não usar arrendamento 78198 ou duplicidade 78196 como crédito bruto por conveniência. Para LL/S, S não é renda total e a parcela pode depender de resultados financeiros negativos. Essas alternativas ficam abaixo de LA/LC/LF/RS na ordem proposta; não há soma carteira crédito+arrendamento adotada.

Atividades do universo descritivo 55 fora do perímetro IF.data precisam ser visíveis. Seguros/resseguros, holdings de participações e securitizadoras sem unidade principal admitida não recebem fórmulas bancárias por analogia. Risco de subscrição, reservas técnicas, sinistralidade, patrimônios separados de emissão e risco de ativos cedidos são perguntas distintas, com componentes não identificados nesta base. Permanecem classe 3 se essenciais ao objetivo, sujeitas à decisão sobre fonte financeira adicional; CVM/B3 não se tornam fontes financeiras por esta pesquisa. A presença de Banco B3 ou Portoseg tampouco representa todo o grupo B3/Porto.

## Matriz de decisão por família e dimensão

Esta matriz substantiva complementa o CSV determinístico por categoria/período. “Investigar” não é adoção; “3” não é não aplicabilidade. C1/ROA/ROE só com perímetro e objetivos adequados; classificação desconhecida permanece visível.

| Família | Rentabilidade | Qualidade de crédito | Capital/alavancagem | Liquidez/financiamento | Eficiência |
|---|---|---|---|---|---|
| Bancos depositários/diversificados | R1/R2; R4/R5/RS de classe 2 explicativos | Q1/Q2; NPL de classe 3 | C1; C3/C4 prudenciais | L2/L3; LA/LC/LF de classe 2; LM de classe 3 | E2-B; E3 de classe 2; E2-C de classe 2/3 |
| Bancos cooperativos/singulares | R1/R2 como sustentabilidade; R4/R5 de classe 2 | Q1/Q2; NPL de classe 3 | C1; C3/C4/regime próprio | L2/L3 quando a captação for aplicável; centralização LA/LF de classe 2; LM de classe 3 | E2-B; E3 de classe 2; benefícios aos cooperados de classe 3 |
| Centrais/confederações de serviços | R1/R2; RS de classe 2 conforme a operação | Carteira própria Q1/Q2; exposições interfinanceiras de classe 3 | C1 e prudencial pertinente | LA/LF de classe 2; centralização/maturidade de classe 3 | E2-B sob renda selecionada; E3 de classe 2 |
| Desenvolvimento/fomento | R1/R2 sustentabilidade; R4/R5 de classe 2; mandato de classe 3 | Q1/Q2; NPL de classe 3 | C1 e prudencial próprio | LA/LC/LF de classe 2 prioritários; LM de classe 3 fundamental; L2/L3 insuficientes | E2-B; E3 de classe 2; eficiência do mandato de classe 3 |
| Crédito não bancário/imobiliário | R1/R2; R4/R5 de classe 2 | Q1/Q2 compatíveis; arrendamento de classe 2; NPL de classe 3 | C1 e prudencial conforme o escopo | LA/LC/LF de classe 2; LM de classe 3; depósitos não impostos | E2-B; E3 de classe 2 com composição da carteira |
| Mercado de capitais/investimento/câmbio | R1/R2; RS de classe 2; R4 composição | Q1/Q2 só na carteira própria; contraparte/mercado de classe 3 | C1; C3/C4 se pertinentes | LA de classe 2 limitado; obrigações com clientes/margens/vencimento de classe 3 | E2-B com cobertura da renda; E3 de classe 2; volumes de classe 3 |
| Pagamentos | R1/R2 da operadora; RS de classe 2 | Não impor Q1/Q2; exposição à contraparte/recebíveis de classe 3 | C1; requerimentos IP próprios de classe 3 | LA de classe 2 com restrição; LS de classe 3 central; DV não é conta de pagamento | E2-B com renda de serviços; E3 de classe 2 limitado; transações de classe 3 |
| Não identificada/conflitante | Contábeis válidos sem atribuir família | Adequação desconhecida | Regime/perímetro desconhecidos | Composição descritiva, capacidade desconhecida | Sem ranking entre pares inventados |

## Plano seletivo para decisão e implementação

1. **Escolher shortlist, sem alterar dados:** decidir LA/LC/LF como primeira família complementar e R4/R5/RS/E3 como explicação de rentabilidade/eficiência; manter as dez atuais. Confirmar quais perguntas exigem fontes de classe 3. Não exigir painel balanceado com todas as métricas; cada família terá cobertura própria.
2. **Um recorte de estoque antes dos fluxos:** contratar Financeiro/202412/LA+LC, selecionar contas já localizadas, validar origem/sinais/zero/null/perímetros, oráculo Decimal/Fraction para poucos casos + BNDES + IP + cooperativa + unknown; revisar antes ampliar aos 60 trimestres. Para LF, provar rubricas irmãs/cesta/residual antes de razão; não misturar captações pai/filhos. Não reconstruir universo/motor.
3. **Um recorte de fluxo:** RS/E3/R4 ou R5 em janela completa, com sinais, acumulados semestrais, abertura e ponte 2019 próprias. Reusar preparação/janelas/avaliador seletivo existente, com testes causais de história ausente, reversão e fronteira 201903. Só novos componentes/indicadores, não full build.
4. **Cobertura e composição antes da comparação:** por período/família/coorte listar quantas/quais unidades e companhias, razões de ausência, AT/crédito/PL conhecidos e desconhecidos. Adotar vínculos da 142 somente após contrato histórico/temporal; 32 companhias e 24 códigos em 2024 não certificam 32 trajetórias históricas. Examinar sobreposição Cielo/BB/Bradesco, conglomerado/membros, subsidiária/grupo; não atribuir duas vezes.
5. **Estatística pertinente:** séries dos agregados ΣN/ΣD; medianas/IQR/quantis e extremos nominais; contagens e entradas/saídas; comparação de unidades comuns quando útil. Decompor ROE por ROA e alavancagem apenas com bases médias compatíveis. Examinar correlação/redundância E2-B/E3/R1 e C1/C2 sem declarar causalidade; não normalizar em índice único. Pesos naturais dependem do denominador, não AT para tudo.
6. **Inferência somente quando responde à pergunta:** observações de unidade repetidas não são amostra aleatória independente; total observado é universo descritivo do nosso corpus. Testes múltiplos/tendências/modelos dependem de hipóteses, dependência temporal e composição. Se contratados, relatar efeitos/intervalos, cluster por unidade e/ou blocos temporais conforme desenho, sensibilidade a PL/renda não positivos e correção de multiplicidade; não adotar automaticamente t-test, regressão, bootstrap ou valor-p. Robustez de janela, perímetro, coorte comum e quebras precede sofisticação.
7. **Revisão por fatias e composição final:** revisor independente confere contas/fontes/nomes/perímetro/contagens/allowlist, resultados seletivos e igualdade dos demais; testes de software não certificam validade econômica. Só então integrar/atualizar o explorador em tarefa autorizada. Fontes de classe 3 continuam sem coleta neste escopo.

## Lacunas priorizadas

| Prioridade | Lacuna metodológica | Lacuna de dados/implementação | Próximo passo delimitado |
|---|---|---|---|
| P1 liquidez não depositária | LA/LC/LF descrevem composição/financiamento; não resolvem capacidade por vencimento. | Falta abertura de maturidade, restrições e recursos livres; FAT/governamentais não têm identificação individual comprovada. | Adotar complemento contábil com limite; definir pergunta/horizonte para LM; pesquisar fonte documental própria antes de coletar. |
| P1 pagamentos/mercado de capitais | Depósitos/crédito não são produto universal; salvaguarda/contraparte/serviços precisam de conceitos próprios. | Obrigações com clientes/recursos segregados/volumetria sem abertura admitida comprovada. | Escolher LS/LM ou medida de contraparte se essencial, conservar ROA/ROE/C1/E2B com ressalvas. |
| P1 representatividade | Correspondência da companhia ≠ desempenho consolidado da emissora. | 55/32/24 decididos em 2024 não foram operacionalizados temporalmente nos datasets atuais; 23 sem correspondência. | Reusar 142 com contrato próprio, sem imputar finanças SUSEP/CVM/B3 ou retroprojetar controle. |
| P2 qualidade do crédito | Provisão não mede inadimplência; carteira/arrendamento/contraparte diferem. | NPL/atraso, provisão específica, baixas/recuperações não comprovados nos 4 relatórios. | Definir abrangência/horizonte/fonte de classe 3; manter Q1/Q2 nomeados. |
| P2 eficiência/mix | Rendas estreitas podem distorcer E2-B para N2/N4/desenvolvimento. | De-para de renda ampla E2-C e produtos DEA/SFA não demonstrado. | RS/E3 e abertura da renda antes de alterar E2-B; sem ranking universal. |
| P2 capital/regime | CP nulo não certifica PR S5; folga exige norma individual/datada. | C4 pós-2018, capital pré-2015 e BRB já diagnosticados. | Manter C3/C4/cobertura; eventual alternativa PR S5 ou admissão BRB tem contrato próprio, sem retomar busca BRB. |
| P3 comparações temporais | Quebras contábeis/perímetros/composição não são tendência econômica pura. | Abertura/LL 2019/definições de passivo 202212/Sr/novos modelos. | Preservar regimes/estado; ensaiar seletivamente e comparar coorte comum, sem harmonização automática. |

O produto desta pesquisa é um conjunto de alternativas verificáveis e uma ordem de implementação. Decidir e implementar são entregas posteriores. Estado de revisão, números finais de cobertura e recibos constam na proveniência; nenhum PASS de software é apresentado como certificação das cinco dimensões.

## Publicação da pesquisa — 17/10/2026

A entrega local de 16/10 foi reconciliada com `main` na base `95615f865aef4fcda02b42a1d6934e4ebe9c7556`, que já contém a documentação do universo de companhias da Issue 142/PR 145. Os cinco arquivos seguem na [Issue 143](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/143), agora também responsável pela publicação e integração conforme o workflow vigente. Os três artefatos tabulares conservam os bytes e hashes do snapshot revisado; este adendo não altera fontes, conclusões, indicadores propostos, fórmulas ou dados.

A pesquisa continua tendo o sistema observado inteiro como objeto principal. A revisão independente do commit de publicação, os checks de CI e o estado confirmado do PR/integração são registrados na mesma Issue, separados do aceite local original. A adoção metodológica e a implementação seletiva permanecem decisões posteriores.

# Renda e custos por modelo de negócio — conciliação de 18/10/2026

Pesquisa da [Issue182](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/182), após a [entrada181](tcb-indicator-input-readiness-20261018.md). O resultado prepara uma escolha entre medidas de custos sobre renda mais abrangente; não adota denominador nem modifica E2-B. Financeiro Tipo2 é o perímetro desta auditoria; Prudencial e Individual não foram transplantados.

## O que a conciliação demonstra

A DRE local distingue resultado de intermediação, receitas de serviços, tarifas, participações, outras receitas e despesas. Assim, a renda selecionada de E2-B pode omitir receitas relevantes em N2, N4, bancos de investimento e conglomerados diversificados. Incluir essas parcelas é uma alternativa implementável, mas não transforma o denominador em receita bruta total nem o numerador atual em todas as despesas operacionais. Categoria Tcb orienta a pergunta; SegmentoTb e composição das contas refinam sua pertinência, sem inferir atividade por saldo zero.

Em cada unidade/data foram confrontadas cinco identidades literais, com os saldos assinados da fonte:

| Identidade publicada no IF.data | Confronto da auditoria |
|---|---|
| RIF78208 | Soma de78203,78204,78205,78206,78207,78231 |
| DIF78214 | Soma de78209 a78213 |
| RBIF78215 | RIF78208 + DIF78214 |
| Outras receitas/despesas78224 | Soma de78216 a78223 |
| Resultado operacional78225 | RBIF78215 +78224 |

São identidades entre agregados e filhos; usa-se uma representação ou a outra, nunca ambas somadas. Resultado operacional78225 já contém despesas de pessoal, administrativas, tributárias e outras: usá-lo como receita de um índice cujo numerador contém esses custos descontaria custos também do denominador.

Os resíduos são diferenças exatas entre tokens nativos, conservadas individualmente e por período/Tcb/SegmentoTb/coorte. No piloto201812/201903/202412, os máximos absolutos foram RIF=1/50000, DIF=1/1000000, RBIF=1/10000, outras=1/500000 e operacional=1/50000 reais. São pequenos, porém não nulos. Não foi adotada tolerância, arredondamento ou correção dos saldos. O inventário integral preserva inclusive somas dos módulos, para evitar que resíduos de sinais opostos se anulem no diagnóstico.

## Fontes e limites conceituais

ASSAF NETO, *Estrutura e análise de balanços*, 11.ed., Atlas,2015: releitura visual nesta execução das pp.321–322 e342, imagens PDF342–343 e363 do exemplar privado do projeto. A p.322 separa os blocos da DRE; a p.342 apresenta IE como despesas operacionais/receitas de intermediação. A adaptação abaixo mantém o custo estreito já usado pelo projeto e amplia a renda; portanto não reproduz o IE literal. Metadados e identificação do exemplar, SHA-256 `d41dccd16d2a9c174fb95cd87e5d3abd0666f461514d8402594367cc913d367b`, são reaproveitados da [proveniência111](financial-dimensions-literature-20261014.provenance.md), sem alegar novo hash do PDF completo.

O [FMI, *Financial Soundness Indicators Compilation Guide*,2019](https://www.imf.org/-/media/files/data/2019/2019-fsi-guide.pdf), §§5.16,5.25 e7.60–7.63, distingue renda não proveniente de juros e custos operacionais, com exclusão de provisões do custo. A fonte exige correspondência das rubricas e recomenda fluxos acumulados no ano. O projeto usa trimestre efetivo/TTM e um custo restrito: nenhuma das propostas é homologação do FSI. Leitura textual dirigida desses trechos em19/10/2026UTC; demais evidências são reuso111/143/178. Pesquisa delimitada, sem protocolo de revisão sistemática ou nova coleta financeira.

## Componentes exatos e versões

Todos os IDs abaixo pertencem à DRE4, TipoInstituicao2. São IDs IF.data; a descrição literal contém códigos Cosif, sem converter um no outro. O arquivo privado `catalog.json` conserva Grupo, NomeColuna, DescricaoColuna, versões e períodos completos, inclusive whitespace e falhas aparentes de redação.

| Símbolo | Conta e nome nativo | Grupo |
|---|---|---|
| RBIF |78215, Resultado de Intermediação Financeira | Resultado de Intermediação Financeira |
| P |78213, Resultado de Provisão para Créditos de Difícil Liquidação | Resultado de Intermediação Financeira - Despesas de Intermediação Financeira |
| SERV/TAR |78216, Rendas de Prestação de Serviços;78217, Rendas de Tarifas Bancárias | Outras Receitas/Despesas Operacionais |
| PESS/ADM |78218, Despesas de Pessoal;78219, Despesas Administrativas | Outras Receitas/Despesas Operacionais |
| TRIB/PART |78220, Despesas Tributárias;78221, Resultado de Participações | Outras Receitas/Despesas Operacionais |
| OUTR/OUTD |78222, Outras Receitas Operacionais;78223, Outras Despesas Operacionais | Outras Receitas/Despesas Operacionais |
| OUT/RO |78224, Outras Receitas/Despesas Operacionais;78225, Resultado Operacional | Respectivamente Outras Receitas/Despesas Operacionais e grupo nulo |

Em78223, a descrição troca a parcela81955002 por81956001 em201903. A rubrica78230 também muda de juros sobre capital próprio para juros sobre capital social de cooperativas; não se deve criar continuidade por nome. A descrição de78222 contém a sequência literal `[71990101][71990125]`, sem operador explícito: foi preservada, não reparada por inferência. A conciliação empírica não certifica um de-para Cosif completo ou a pureza econômica de cada residual.

## Duas alternativas para decisão

Definir, no mesmo intervalo w: C=−(PESS+ADM); S=RBIF−P+SERV+TAR, a renda vigente; G=S+OUTR; GP=G+PART. Remover o resultado de provisão do denominador preserva a opção atual de E2-B, sem transformar provisões em inadimplência ou ignorar sua relevância em Q1/Q2.

| Proposta, ainda candidata | Fórmula percentual | Pergunta e recorte economicamente pertinente | Limite |
|---|---|---|---|
| E2-W, custos sobre renda ampliada sem participações |100×C/G | Quanto a renda selecionada, incluindo outras receitas da operadora, suporta pessoal/administração? Prioridade N2/N4 e modelos de serviços; demais Tcb conforme composição. | OUTR pode conter recuperações, reclassificações e itens não recorrentes; não separa todo produto nem é receita bruta total. |
| E2-WP, custos sobre renda ampliada com participações |100×C/GP | Como os mesmos custos se relacionam com a renda que também incorpora participações? Sensibilidade para conglomerados e unidades com esse resultado. | Custos das investidas podem estar fora do numerador; menor razão pode refletir composição patrimonial, não maior eficiência da operadora. |

Ambas são adaptações próprias fundamentadas na leitura da DRE, não fórmulas atribuídas literalmente a Assaf/FMI. E2-W é a candidata principal para a pergunta operacional; E2-WP serve a uma pergunta de abrangência patrimonial distinta. Não há recomendação de escolher a variante que produz o menor valor ou maior cobertura. As séries precisam permanecer separadas; E2-B continua disponível para comparação com seu denominador explícito.

Numerador C mantém apenas pessoal/administração. Incluir automaticamente TRIB e OUTD para chamar o numerador de despesas operacionais completas não é recomendado: OUTD é heterogênea e muda em2019; a conciliação literal não demonstra sua correspondência integral ao conceito. Reprodução de IE literal ou FSI exige contrato adicional de abrangência, se essa for a pergunta escolhida.

Fichas comuns: fluxos em reais; resultado adimensional apresentado em%; trimestre efetivo ou TTM de quatro trimestres disjuntos, com reset semestral do motor atual. Sem multiplicação por4. G/GP zero é indefinido; negativo preserva a fração e recebe alerta, sem leitura ordinal de eficiência. C negativo é preservado, com reversão/composição a examinar. Null, célula ausente e histórico insuficiente impedem o cálculo, cada qual em seu estado; ausência de dados não significa não aplicabilidade. A denominação e o conjunto de unidades aplicável dependem da decisão humana.

Agregação futura: ΣC/ΣG ou ΣC/ΣGP somente na interseção válida da mesma fórmula/janela/perspectiva, acompanhada de contagens, estoques conhecidos e distribuição. Não misturar W/WP/B num mesmo agregado. Não usar AT como peso universal nem multiplicar a contribuição de uma unidade pelo número de companhias vinculadas.

## Viabilidade, cobertura e próximo passo

O inventário182 examina todos os89.476unidade-períodos financeiros. As listas nominais e estoques exatos estão no pacote privado desta pesquisa; a [matriz181](tcb-indicator-input-readiness-20261018.md) complementa a suficiência temporal. A presença contemporânea não certifica trimestre/TTM calculável: bindings e dependências temporais devem ser liberados no piloto190, sem estender pontes2019 por analogia.

Em202412, são1.422unidades esperadas e1.415com componentes finitos; sete possuem null na fonte, com estoques desconhecidos. O piloto de três datas teve18unidade-períodos com null explícito, nenhuma conta ausente nessas datas; `missing` é o rótulo agregado do instrumento. G e GP são positivos em1.410unidades no corte, negativos emcinco. S é positivo em1.393, zero emsete e negativo emquinze; essa diferença descreve abrangência, não prova adequação.

| Tcb,202412 | Esperadas | S positivo | G/GP positivos | Leitura |
|---|---:|---:|---:|---|
| B1 |97|91|97| Composição de receitas e participações exige leitura do conglomerado. |
| B2 |31|30|31| Outras receitas podem mudar a representação do negócio. |
| B3C |29|26|26| Duas unidades sem componentes e uma renda G/GP negativa; centralização tem pesquisa própria184. |
| B3S |753|752|752| Uma renda G/GP negativa; benefícios ao cooperado não são medidos. |
| B4 |4|4|4| Sustentabilidade contábil não mede mandato. |
| N1 |226|216|221| Crédito e leasing conservam componentes próprios. |
| N2 |136|130|135| Renda ampliada não mede volume de clientes. |
| N4 |146|144|144| Renda/custo da operadora não mede salvaguarda de usuários. |

Cobertura por nomes, códigos, companhias, datas, Tcb, SegmentoTb e coortes permanece no nominal. As55companhias e as23sem unidade no corte não desaparecem: o roster autenticado181 liga o diagnóstico por unidade/data, sem importar a elegibilidade de outro indicador. AT/crédito/PL conhecidos e desconhecidos acompanham as interseções; não estimam estoque das unidades sem informação.

Allowlist pública: somente esta nota; Root integra os paths próprios na branch `codex/tcb-research-182-188`, base `d65f1e517a370eff5d7ec59ee6011c13826f6f41`. Preparação privada `.scratch/tcb-conciliacao-renda/`: instrumento, catálogo, identidades, nominal, resumo e recibos por tentativa; sem camada/dependência nova. O ponteiro foi redescoberto e manteve manifest `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`, com hashes das tabelas e fontes autenticados. Nenhum indicador novo foi avaliado.

Piloto de4.124unidades em201812/201903/202412 revisado independentemente por `review_182_income`: conferência de todos os brutos, cinco identidades, somas C/S/G/GP,189resumos e hashes. Somente depois expandiu-se aos60trimestres. A primeira expansão parou num cadastro com classificações nulas; corrigiu-se apenas o acesso ao objeto, preservando a tentativa e a categoria UNKNOWN. A execução integral `full2` terminou em24,766s. Revisão integral/fontes/SHA e publicação têm registros próprios na Issue.

O piloto190 só começa após escolha explícita de W e/ou WP, com teste de dupla contagem, reversão, renda não positiva, histórico e fronteiras; preservação das20métricas existentes; revisão antes de ampliar. Até essa escolha, este resultado é pesquisa concluível com decisão metodológica pendente, sem impedir as pesquisas183–188 ou as quatro sensibilidades já aprovadas para189.

Suplemento de inventário antes da integração:390linhas nativas da DRE em2010–2024 têm CodInstnulo e não podem ser atribuídas às unidades identificadas. Foram preservadas separadamente, com contexto/token/proveniência, em `unmapped-supplement/native-rows.json` e recibo próprio na preparação privada182. Não são390instituições, não foram imputadas nem alteram os resultados das unidades conhecidas. Não houve linha com código conhecido fora da população aceita neste recorte.

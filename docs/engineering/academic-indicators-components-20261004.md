# Indicadores acadêmicos: fontes, componentes e lacunas

**Nota histórica, não carteira vigente — atualização documental de17/10/2026:** esta proposta registra o estágio anterior à seleção/implementação. Fundamentos e decisões posteriores estão na [pesquisa111](financial-dimensions-literature-20261014.md); o conjunto atual foi implementado nas [entregas127](ifdata-monograph-analysis-20261014.md) e [130](ifdata-universe-analysis-20261014.md). Para ampliação por negócio no sistema inteiro, usar a [pesquisa143](financial-indicators-activity-review-20261016.md) e o [atlas de fórmulas](financial-indicators-formulas-20261017.md). Pendências e fórmulas propostas no corpo abaixo conservam seu alcance histórico; não anulam decisões posteriores.

## Proposta vigente — 2026-10-11

A [Issue 14] foi reformulada com aprovação de João: organizar componentes por rentabilidade, crédito/risco e patrimônio/capital, propondo indicadores com fórmula, unidade, janela e disponibilidade. A proposta é **prospectiva**; substitui a obrigação de recuperar a lista antiga, sem reconstruí-la. A janela principal continua **2010–2024**, com **2025–2026 complementar**. Adoção de indicadores, cálculo, amostra e método permanecem decisões de João/orientador na [Issue 3].

Base desta pesquisa: `af1336c542208cbe7eb984caeb960fa3d1743bd8`, branch `codex/ifdata-cadastro`. Executor: agente pesquisador da Issue 14; integrador: coordenador. Único destino de escrita: esta nota existente em `docs/engineering/`; nenhuma mudança estrutural. **Rentabilidade aprovada em revisão independente antes da ampliação, conforme comunicação do integrador em 2026-10-11. Crédito/risco e patrimônio/capital estão preparados para revisão de conteúdo e composição final.**

### Como ler esta proposta

O [catálogo temporal](ifdata-variable-catalog-20261011.md) contém definições e cobertura de registros nos conjuntos aceitos. Nesta atualização, suas tabelas foram consultadas por `bank_quality.ifdata_variable_catalog.query_catalog`, que confere o inventário e os hashes dos arquivos antes da leitura. Não foram consultados saldos individuais nem adquiridos novos valores do BCB. A chave operacional é o conjunto literal **dataset + TipoInstituicao + NumeroRelatorio + Conta + definição**; nomes e códigos isolados não certificam equivalência.

Para os componentes de rentabilidade abaixo: `dataset=financial`, `TipoInstituicao='2'`; `NumeroRelatorio='1'` é Resumo e `'4'` é Demonstração de Resultado no catálogo OData. **Esses identificadores não são a perspectiva `1005` e os relatórios `92/98/118/119` do portal legado.** A evidência histórica de unidade/janela daquele portal não foi transportada para OData. Tipo literal, perímetro econômico, emissor e unidade analítica exigem conferências próprias.

### Rentabilidade: candidatos para escolha, sem cálculo

LL = lucro líquido; AT = ativo total; PL = patrimônio líquido; RAT = resultado antes da tributação e participações; RIF = receitas de intermediação financeira. `W` significa uma **janela ainda a comprovar** na fonte de cada componente. `média_W` é um operador proposto, cuja frequência e regra precisam ser escolhidas; não corresponde a uma série já construída. Todas as razões abaixo seriam adimensionais, apresentáveis em `%` mediante multiplicação por 100, **somente após comprovar unidade/escala compatíveis** dos componentes. O catálogo não demonstra a unidade monetária nem a janela de acumulação de OData.

| Indicador candidato e conceito | Fórmula proposta e fonte | Componentes literais / relatórios | Disponibilidade observada por época | Lacunas e pontos para escolha |
|---|---|---|---|---|
| **ROE contábil**: retorno relativo ao patrimônio empregado | `LL_W / média_W(PL)`. Alternativa operacional inspirada no FMI, §§7.51–7.55; o FMI recomenda resultado após tributos e capital/reservas. A associação a PL IF.data é proposta a conciliar. [F] | Resumo `1`: LL `78187`, PL `78186`; complementar: LL `141870`, PL `140246`. Detalhes e variantes na tabela seguinte. | Componentes em 60 referências trimestrais `201003–202412`; LL possui duas definições, separadas em `201903`. Complementar: seis referências `202503–202606`. | Escolher janela e média, conferir composição de LL/PL, perímetro e mudanças. PL pontual não prova média disponível. ROE com PL contábil não reproduz o BCB com PL ajustado e média mensal. Denominador zero/negativo exige regra explícita; não excluir automaticamente. |
| **ROA antes dos tributos**: retorno relativo ao ativo empregado | `RAT_W / média_W(AT)`. O FMI prefere resultado antes dos tributos e AT médio (§§7.47–7.50); conciliação IF.data ainda necessária. [F] | DRE `4`: RAT `78226`; AT `78182` no Resumo `1`. Complementar: RAT `141867` na DRE `4`, AT `140220` no Resumo `1`. | Ambos os componentes em 60 referências `201003–202412`; complementar em seis `202503–202606`. | `78226` inclui o resultado antes de participações; isso não demonstra igualdade ao numerador FMI. Conciliar rubricas, sinais e tratamento das participações. Alternativa `LL_W / média_W(AT)` pode ser discutida como **ROA após tributos**, com outro numerador e identificação própria; não trocar silenciosamente. |
| **Margem líquida sobre receitas de intermediação**: parcela de resultado líquido em relação à receita dessa atividade | `LL_W / RIF_W`, fórmula de Lima et al. (2018), tabela 4, p.190. [L] | DRE `4`: LL `78187` e RIF `78208`; LL também aparece no Resumo `1`, sem presumir equivalência de cada ocorrência. | Componentes observados em 60 referências `201003–202412`; variante de LL em `201903`. Não há agregado literal equivalente a `78208` na DRE complementar consultada. | Dois fluxos devem ter a mesma janela, unidade e perímetro. Resultado de intermediação `78215`/`141851` não substitui receita. Não construir receita 2025 pela soma de rubricas sem contrato e evidência próprios. Denominador zero/negativo e equivalência à receita Economática usada pelo artigo são questões abertas. |

O objetivo desta seleção é oferecer operações simples com componentes identificáveis. Não há hierarquia aprovada entre candidatos, aprovação de fórmula final ou indicação de investimento. Disponibilidade aritmética potencial não basta para interpretação econômica.

### Inventário dos componentes da fatia

Cada intervalo da tabela corresponde à lista de períodos efetivamente retornada pelo catálogo, com a frequência trimestral observada e sem lacunas **entre os extremos da respectiva definição**. Isso não afirma cobertura por banco, população elegível ou continuidade de entidade. Descrições entre crases são literais; o texto explicativo fora delas é desta pesquisa.

| Relatório / Conta / componente | Definição literal relevante | Referências observadas | Registros com Saldo não null / Saldo null |
|---|---|---|---:|
| Resumo `1` / `78182` / AT | `[10000007] + [20000004]` | `201003–202412`, 60 | 88.792 / 697 |
| Resumo `1` / `78186` / PL | `[60000002] + [70000009]+ [80000006]` | `201003–202412`, 60 | 88.792 / 697 |
| Resumo `1` / `78187` / LL | `[70000009]+[80000006]-[81955002]` | `201003–201812`, 36 | 56.610 / 544 |
| Resumo `1` / `78187` / LL | `[70000009]+[80000006]-[81956001]` | `201903–202412`, 24 | 32.182 / 153 |
| DRE `4` / `78226` / RAT | `Somatório do Resultado Operacional e do Resultado Não Operacional` | `201003–202412`, 60 | 88.792 / 697 |
| DRE `4` / `78208` / RIF | `Somatório de Rendas de Operações de Crédito, Rendas de Operações de Arrendamento Mercantil, Rendas de Operações com TVM, Rendas de Operações com Instrumentos Financeiros Derivativos, Resultado de Operações de Câmbio e Rendas de Aplicações Compulsórias` | `201003–202412`, 60 | 88.792 / 697 |
| Resumo `1` / `140220` / AT | `[1000000009] + [2000000008]` | `202503–202606`, 6 | 11.364 / 180 |
| Resumo `1` / `140246` / PL | `[6000000004]+ [7000000003]+ [8000000002]` | `202503–202606`, 6 | 11.364 / 180 |
| Resumo `1` / `141870` / LL | `[7000000003] + [8000000002] - [8195600001]` | `202503–202606`, 6 | 11.363 / 181 |
| DRE `4` / `141867` / RAT | `[7100000006] + [7300000002] + [8100000005] + [8300000001] - [8195600001]` | `202503–202606`, 6 | 11.363 / 181 |

A consulta também confirmou LL na DRE `4`, com as mesmas duas descrições `78187` e períodos da tabela, e `141870` em `202503–202606`. AT existe em Ativo `2` e, no complementar, DRE `4`; PL em Passivo `3`. Essas ocorrências permanecem separadas no catálogo; a proposta usa Resumo para AT/PL e DRE para a margem, evitando somar registros duplicados entre relatórios. Não houve conferência célula a célula entre ocorrências nesta pesquisa.

**Limite das contagens:** são linhas com/sem Saldo no catálogo aceito, não bancos distintos ou interseções válidas do indicador. `com_valor` inclui zero. Não foi medida cobertura conjunta LL/PL/AT/RIF por instituição/janela, nem identidade temporal, abertura ou médias. A mudança literal `81955002 → 81956001` em `201903` impede tratar o numerador como uma única definição certificada. A descrição de RAT antes de 2025 é genérica: sua estabilidade não prova composição contábil constante.

### Janelas e unidades: o que ainda impede operacionalizar

Para usar qualquer candidato, comprovar **unidade/escala, janela do fluxo, data do estoque, perímetro e versão** por componente na fonte OData. Trimestre de referência não prova fluxo de três meses, e ausência de unidade no catálogo não autoriza presumir BRL ou R$ mil. As notas legadas de lucro semestral reaproveitadas abaixo continuam restritas àqueles contratos. `LL_junho + LL_dezembro` seria apenas alternativa condicionada à comprovação das janelas e compatibilidade; não foi adotada ou calculada.

Como alternativa de média, o FMI admite abertura/fechamento como mínimo para AT e encoraja maior frequência (§7.48). Se escolhido método anual que exige abertura, **200912 é insumo necessário para 2010**, mas não aparece nos componentes aqui catalogados, que começam em `201003`. Segundo o índice do pacote bruto consultado pelo integrador nesta entrega, 200912 está disponível no bruto recebido; ainda fora do catálogo e exige conferência/importação própria se esse método for escolhido. Este pesquisador não leu ou importou o bruto. Logo, 60 referências de componentes não significam 15 anos de ROA/ROE anual operacionalmente prontos. Média trimestral é alternativa metodológica, sem equivalência à média mensal ajustada do BCB.

Para contraste documental, a pesquisa de 2026-10-04 registrou o ROE do **REB 2023, p.49, nota 24**, com lucro de doze meses e média de PL ajustado dos treze meses findos em dezembro. [B23] Esse resultado é **evidência reaproveitada**, não nova certificação de componentes OData. Nesta rodada a abertura web identificou o PDF, mas a leitura textual dirigida posterior falhou; não se afirma nova confirmação da nota 24. Os candidatos contábeis desta fatia não são anunciados como reprodução do indicador BCB.

Em 2025, as mudanças de códigos/composições documentadas exigem tratar os seis trimestres como complemento separado até conciliação. A [pesquisa de comparabilidade](sample-comparability-research-20261008.md) e a [ponte normativa](financial-2025-normative-bridge-20261004.md) são evidência local reaproveitada, sem nova leitura das normas nesta fatia; nenhum de-para foi construído. A falta de agregado de receita equivalente no catálogo complementar é lacuna do mapeamento observado, não prova de inexistência na fonte oficial.

### Proveniência e verificação da fatia de rentabilidade

**Consulta nova, 2026-10-11:** Issue 14 real (corpo/labels/claim); duas tabelas do catálogo local autenticadas pelo leitor; FMI 2019, título/sumário e §§7.47–7.55, pp.90–91 (PDF páginas 106–107, contagem a partir de 1); artigo original Lima et al. na SciELO, tabela 4 (fórmula da margem), confrontado com o localizador p.190 registrado na pesquisa anterior. O artigo fornece a fórmula, não valida equivalência dos componentes IF.data. Consulta documental web somente, sem endpoints de valores/cadastro.

**Evidência reaproveitada:** pesquisa de 2026-10-04 preservada abaixo, nota do catálogo de 2026-10-11 e pesquisas locais de comparabilidade/ponte 2025. Não houve nova autenticação dos corpos primários desses ledgers. Matt `research` foi aplicado por agente delegado; Feynman `pdf-explore` orientou localização e cruzamento do capítulo de rentabilidade do FMI com suas definições e limites, com extratos/localizadores registrados nesta própria nota. `verification-before-completion` orienta a conferência do diff e das afirmações; revisão independente é etapa do integrador, ainda pendente neste checkpoint. TDD/testes de software não se aplicam ao delta documental.

Consulta reproduzível: executar `query_catalog('data/curated/ifdata-variable-catalog-20261011', SQL)` usando `SELECT` sobre `catalogo_variaveis`. Filtrar `dataset='financial'`, `TipoInstituicao='2'` e os pares `(NumeroRelatorio, Conta)` da tabela; manter `DescricaoColuna`, `periodos`, `numero_referencias`, `periodos_sem_registro_entre_extremos`, `com_valor`, `sem_valor`. Para conferir a falta de agregado de receita complementar, inspecionar **todas** as definições de `NumeroRelatorio='4'`, `202503–202606`, sem substituir receita por resultado. Não somar variantes ou relatórios. O leitor valida arquivos pelo manifesto; esta consulta não constitui nova auditoria integral do catálogo ou da cadeia primária.

Âncora do catálogo consultado: `catalogo_variaveis.parquet` SHA-256 `644265316851705e0f9187a59ecc5aeb4d6125d5e137c7fa3a34e263563dd30e`; `cobertura_variaveis.parquet` SHA-256 `38df9f355964fd8f2fd1b4f57a93e070058579c8e1888a2019d11167849133c3`. O manifesto registra 438 definições/contextos e 11.331 linhas de cobertura. Todos os números desta fatia são metadados de cobertura; nenhum indicador ou valor financeiro foi calculado.

### Crédito/risco: dois candidatos com recorte explícito

Neste grupo, os componentes consultados são `dataset=financial`, tipo literal `2`, relatórios Ativo `2` e Passivo `3`. São propostas contábeis de **estoques na mesma data**, cuja unidade/escala e referência efetiva devem ser comprovadas; não há janela de acumulação de fluxo a anualizar. As razões seriam adimensionais ou `%` após compatibilização. A fórmula de crédito/depósitos e a de provisão/crédito vêm do artigo original [L], tabela 4, p.190, já consultado nesta entrega; adaptação a rubricas IF.data permanece proposta.

| Candidato e conceito | Fórmula proposta / fonte | Componentes literais | Disponibilidade por época | Lacunas e escolha |
|---|---|---|---|---|
| **Crédito/depósitos**: relação entre operações de crédito e financiamento por depósitos | `operações de crédito / depósitos`. [L] | Ativo `2`: `78191`, descrição `[16000001]-[16900008]`; Passivo `3`: `78287`, `[41000007]`. Complementar: Ativo `140205`, `[1600000007]`; Passivo `140228`, `[4100000009]`. | Cada componente anterior: `201003–202412`, 60 referências; cada complementar: `202503–202606`, seis. | Conciliar crédito bruto/líquido, rubricas e perímetro. Não substituir por carteira classificada `78183` ou captações `78185`. Crédito2025 tem composição distinta; sem ponte certificada. A razão trata estrutura de financiamento, não mensura diretamente inadimplência ou suficiência de liquidez. |
| **Provisão sobre operações de crédito**: provisão contábil relativa à carteira correspondente | `provisão estoque / operações de crédito`. Adaptação da PDD/crédito de [L], sujeita à conciliação. | Ativo `2`: provisão `78192`, `[16900008]`; crédito `78191`, `[16000001]-[16900008]`. | Ambos em `201003–202412`, 60 referências; não foi localizado estoque de provisão equivalente na estrutura de Ativo complementar examinada. | Confirmar sinal e base bruta/líquida antes de formular cálculo; não aplicar valor absoluto por conveniência. O fluxo DRE `78213` ou `141842` não substitui estoque de provisão. PDD/crédito é proxy do artigo, não uma taxa observada de atraso/inadimplência. Não transportar AA–H para estágios2025. |

Os três novos componentes anteriores (`78191`, `78192`, `78287`, nos relatórios indicados) têm listas trimestrais contínuas no intervalo; para cada um, a cobertura é **88.792 registros com Saldo / 697 null**. Complementar: `140205` tem **11.223 / 175**; `140228`, **11.364 / 180**. Contagens não demonstram interseção por instituição. A descrição de `78191` conserva a subtração literal; `78193` é rotulado “Operações de Crédito Líquidas de Provisão”, com `[16000001]`. Nenhum sinal ou crédito bruto foi reconstruído a partir desses nomes. A composição precisa de validação contábil antes de implementação.

### Patrimônio/capital: separar contabilidade e prudencial

| Candidato e conceito | Fórmula proposta / fonte | Componentes / dataset, tipo, relatório | Disponibilidade por época | Lacunas e escolha |
|---|---|---|---|---|
| **Capitalização contábil simples**: participação do PL no ativo | `PL / AT`. Adaptação **sem ajustes** da capitalização PL ajustado/AT ajustado registrada no BCB REB2020, tabela4, p.159. [B20] | `financial/2/1`: `78186/78182`; complementar `140246/140220`, já inventariados acima. | 60 referências `201003–202412`; seis `202503–202606` em códigos próprios. | Não reproduz a medida ajustada do BCB nem capital regulatório. Mesmo código/período não elimina mudanças contábeis. Estoques da mesma data/perímetro e unidade/escala compatíveis; razão adimensional, `%` apenas com convenção explícita. PL negativo e AT zero exigem regras, sem exclusão automática. |
| **Índice de Basileia nativo**: capital regulatório relativo ao risco | Conceito `PR / RWA`; **proposta de usar o índice publicado**, sem recalcular. BCB REF abril2025, Anexos, “Conceitos e Metodologias”, verbete IB. [REF25] | `capital/1/5`: índice `79664`; PR `79649`, RWA `79665`. No recorte antigo `financial/2/1`, `79664` também existe, mantido separado. | Índice financeiro antigo: `201003–201412`, 20 referências. Capital: variantes nativas entre `201503–202606`, separadas na tabela seguinte; principal até `202412`, complementar desde `202503`. | Não emendar datasets/perímetros para fabricar série2010–26. Fórmula de referência é conceitual; preservar escala publicada até comprovar se o Saldo representa fração ou percentual. Não confrontar com limite regulatório atual em toda a história. Não requer join com PL contábil. |
| **Índice de Capital Principal nativo**: capital de melhor qualidade relativo ao risco | Conceito `CP / RWA`; **usar índice publicado**, sem recalcular. Mesmo documento BCB, verbete ICP. [REF25] | `capital/1/5`: índice `79659`; CP `79645`, RWA `79665`. | Variantes entre `201503–202606`; nenhuma observação deste índice anterior a201503 no catálogo consultado. | Não presumir zero ou ausência estrutural antes de2015. Versões de rótulos coexistem em intervalos e não autorizam escolher automaticamente uma. Estoques/prudencial na referência; escala publicada desconhecida, sem anualização. Unidade acadêmica e correspondência à população da monografia permanecem abertas. |

Fonte de capitalização: **reaproveitamento explícito** da pesquisa2026-10-04 e seu localizador BCB, sem nova confirmação textual da tabela4 nesta ampliação. Para IB/ICP, consulta nova ao PDF oficial [REF25] em2026-10-11 identificou título/sumário e a seção “Conceitos e Metodologias”, iniciada na p.100; as definições dos verbetes IB/ICP foram retornadas pelo índice da busca no próprio documento BCB. A leitura textual dirigida subsequente falhou; registrar como **evidência oficial indexada**, sem alegar página exata dos verbetes ou auditoria da regulação histórica. As descrições literais do catálogo corroboram as relações PR/RWA e CP/RWA.

| Dataset/tipo/relatório / Conta | Variante literal do índice e períodos efetivos | Referências / com Saldo / null |
|---|---|---:|
| `financial/2/1` / `79664` | `Índice de Basileia`; `201003–201412`, contínuo | 20 / 31.905 / 2.038 |
| `capital/1/5` / `79664` | `Índice de Basileia \n(m) = (e) / (i)`; `201503–202306`, exceto `202212` | 33 / 44.006 / 1.619 |
| `capital/1/5` / `79664` | `Índice de Basileia \n(n) = (e) / (j)`; `202212–202606`, exceto `202303/202306` | 13 / 20.157 / 407 |
| `capital/1/5` / `79659` | `Índice de Capital Principal \n(k) = (a) / (i)`; `201503–202209`, contínuo | 31 / 25.316 / 17.600 |
| `capital/1/5` / `79659` | `Índice de Capital Principal (k) = (a) / (i)`; somente `202303/202306` | 2 / 856 / 1.853 |
| `capital/1/5` / `79659` | `Índice de Capital Principal \n(l) = (a) / (j)`; `202212–202606`, exceto `202303/202306` | 13 / 6.594 / 13.970 |

Na tabela, `\n` indica a quebra de linha literal do nome, não uma normalização aplicada aos dados. Esses intervalos/variantes foram conferidos pelas listas exatas do catálogo; lacuna de uma variante não equivale a trimestre ausente de todo o código. RWA `79665` também possui variantes `(i)` e `(j)` com os mesmos intervalos/exceções de Basileia, enquanto PR `79649` muda de rótulo em `202412` (39 referências até202409; sete desde202412). CP `79645` tem 46 referências `201503–202606`, **33.158 com Saldo / 33.031 null**. Ausências materiais reforçam que disponibilidade temporal de uma rubrica não certifica amostra ou cobertura conjunta. Não foram agregados valores nem unidas perspectivas.

### Escolhas encaminhadas e checkpoint final de conteúdo

Esta é uma primeira seleção de **oito candidatos** nas três dimensões, não catálogo exaustivo de indicadores. GAP, reserva de liquidez e demais alternativas históricas continuam documentados abaixo, sem obrigação de reconstruir a proposta perdida ou acrescentá-los à seleção vigente. Para João/orientador, as escolhas se concentram em: **(1)** candidatos e adaptações que respondem à pergunta da monografia; **(2)** unidade/amostra e tratamento de desconhecidos; **(3)** janelas/médias e apresentação separada dos regimes, incluindo eventual abertura200912 já recebida. Nenhuma dessas escolhas foi adotada.

As consultas novas da ampliação leram somente as definições/coberturas do catálogo autenticado e documentação primária. Pesquisas de amostra/comparabilidade e ponte normativa são reutilizadas como limites, sem duplicação ou novo de-para. **Próximo gate: revisão independente dos dois grupos ampliados e da composição integral.** A rentabilidade já recebeu revisão parcial antes desta expansão; conclusão integral, publicação e integração dependem da evidência do integrador. Nenhum cálculo ou execução sobre valores está autorizado por esta proposta.

<details>
<summary>Pesquisa histórica de 2026-10-04 — preservada; seus blockers e estados não substituem o escopo reformulado em 2026-10-11</summary>

Pesquisa da [Issue 14](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/14), em 2026-10-04, sobre `main` `17fbf474320078af0769ee3f3fc664f5697565a4`, branch `codex/issue-32-historical-frontier`. A nota prepara alternativas para a [decisão humana na Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3). Seu destino é `docs/engineering/`, conforme a [arquitetura](../architecture.md#organização-dos-arquivos-e-pastas); nenhuma camada ou contrato de dados novo é criado.

**Resultado e limite material:** o histórico da Issue 14 registra sete candidatos revisados, sete extensões e nove testes semânticos propostos, mas não enumera a proposta integral. A consulta ao corpo/comentários das Issues 14 e 3 e a busca dirigida nas notas locais de preparação/publicação não recuperaram essa lista nem suas fórmulas completas. Portanto, esta nota consolida somente conceitos explicitamente rastreáveis nesses registros e nas fontes; não reconstrói os sete candidatos nem declara a proposta integral concluída. Recuperar o artefato corrigido de 2026-10-03 e seu complemento é requisito para conferir nomes, versões e componentes de cada candidato. [Issue 14]

Não houve cálculo de indicadores, escolha de amostra/método ou nova aquisição de valores, cadastros ou dicionários IF.data. Fonte documental adicional não é indicador adicional aprovado. Pesquisa, revisão técnica, aceite da proposta e adoção metodológica são etapas distintas.

## Fontes e localizadores conferidos

| Referência primária | Localizador e evidência usada | Alcance |
|---|---|---|
| [Lima, Fonseca, Silveira e Assaf Neto (2018)][L] | RAC 22(2), pp.178–200; tabela 4, p.190, PDF página 13; metodologia pp.187–189 e discussão do GAP p.189 | Fórmulas do artigo; dados trimestrais Economática/BR GAAP. Não demonstra disponibilidade equivalente em IF.data. |
| [BCB, REB 2020][B20] | Tabela 4, p.159, PDF página 159; contexto pp.157–158 | Capitalização Cosif ajustada; provisões/crédito SCR em recorte banco/modalidade/localidade/tempo. |
| [BCB, REB 2023][B23] | Capítulo 4, p.49, nota 24, PDF página 49 | Definição do ROE anual publicado pelo BCB. |
| [FMI, FSI Compilation Guide (2019)][F] | Capítulo 7, §§7.46–7.55, pp.90–91, PDF páginas 106–107; sumário e título conferidos | Referência complementar para ROA/ROE e médias de estoques; não valida adaptação IF.data. |
| [Contrato financeiro 202412][C] e [execução da admissão][E] | `1005/92/202412`; mapa de métricas, pointers D/O e cobertura; [perfil fechado][P] `/report/rp` e `/metrics` | Evidência local aceita para seis montantes e duas quantidades, exclusivamente nesse snapshot. |

Publicação do artigo é **2018**; aprovação em 2017 não altera o ano bibliográfico. Assaf Neto (2015) e Marion (2009), citados como pendência na Issue 14, permanecem sem edição/página operacional comprovada nesta pesquisa. A [página do próprio Instituto Assaf][A] descreve análise de bancos na Parte V, mas não fornece as páginas/fórmulas das edições requeridas. Não usar referências de terceiros para preencher essa lacuna. [L], [Issue 14], [A]

## Conceitos recuperáveis: fórmula da fonte e adaptação pendente

Esta tabela é um mapa de evidências, **não a lista recuperada dos sete candidatos**. AT = ativo total; PL = patrimônio líquido; LL = lucro líquido; PDD = provisão para devedores duvidosos; AS/PS = ativos/passivos sensíveis. Os quocientes monetários são adimensionais, desde que componentes tenham escala compatível; apresentação em percentual exigiria convenção explícita. Estoques usam a mesma data; fluxos usam a mesma janela.

| Conceito citado na Issue 14/3 | Fórmula e recorte da fonte | Componentes e adaptação a esclarecer | Cobertura efetivamente demonstrada |
|---|---|---|---|
| Crédito/depósitos, dimensão liquidez | Operações de crédito / depósitos, tabela 4. [L] | Estoques de crédito e depósitos na mesma unidade/data; conciliar crédito bruto/líquido e rubricas do denominador. Captações não são automaticamente depósitos. | Existe carteira classificada `78183`; o Resumo admitido não possui depósitos separados. Equivalência da carteira ao numerador da fonte e cobertura bilateral desconhecidas. [C], [E] |
| Provisão/crédito, dimensão qualidade do ativo | PDD / operações de crédito, tabela 4. [L] REB usa volume de provisões / volume de crédito no SCR. [B20] | Estoque da provisão, sinal apresentado, crédito bruto/líquido e abrangência da carteira exigem prova. Despesa com provisão é fluxo distinto; não trocar numeradores. | Provisão não está nas oito métricas admitidas. Carteira classificada isolada não comprova denominador equivalente nem cobertura da razão. [C], [E] |
| Margem líquida, dimensão desempenho | LL / receitas de intermediação financeira, tabela 4. [L] | Dois fluxos da mesma janela/perímetro/regime; demonstrar rubricas de receitas. Receita e resultado de intermediação não são substitutos automáticos. | LL `ifd=79718`, `lid=78187` é julho–dezembro; receitas não fazem parte do Resumo admitido. Razão anual não demonstrada. [C], [P] |
| GAP, exposição a juros | **AS / PS**, tabela 4. [L] | Estoques bilaterais, critérios de sensibilidade e composição das carteiras exigem mapeamento. Não converter em AS−PS ou diferenças por faixas. | Nenhum dos dois agregados sensíveis está admitido. AT e passivo total não substituem AS/PS. Cobertura desconhecida. [C], [E] |
| Capitalização contábil | PL **ajustado** / AT **ajustado**, tabela 4. [B20] | Dois estoques na mesma data/perímetro; explicitar ajustes. PL/AT sem ajustes seria adaptação contábil distinta, sujeita à Issue 3. | PL `78186` e AT `78182` disponíveis por variável; ajustes não demonstrados. Isso não comprova reprodução da medida BCB ou adequação prudencial. [C], [E] |
| ROE: return on equity, retorno sobre patrimônio | LL em doze meses / média do PL ajustado dos treze meses findos em dezembro, nota 24. [B23] | Fluxo anual e série mensal ajustada; média trimestral ou abertura/fechamento é alternativa metodológica distinta. | Apenas LL semestral e PL da referência estão admitidos nesse recorte. Não há série mensal ajustada ou numerador anual comprovado. [C], [E] |
| ROA: return on assets, retorno sobre ativos | FMI: resultado líquido, preferencialmente **antes dos tributos**, / ativo total médio; §§7.47–7.48. [F] | Referência complementar, sem atribuir essa definição à proposta perdida. Numerador IF.data e ajustes precisam ser conciliados; LL não prova equivalência ao resultado antes de tributos. | AT pontual disponível; numerador equivalente, médias e cobertura anual desconhecidos. A fonte operacional específica da proposta permanece pendente. [C], [E], [Issue 14] |

**Reserva contábil de liquidez:** a Issue 14 menciona falta de fonte operacional específica. Nome, fórmula exata, componentes, eventuais restrições aos ativos e denominador da proposta original continuam desconhecidos. Não inferir uma composição nem substituir por LCR, que o REB 2020 identifica separadamente como indicador de Basileia III. Sem a proposta original e a página primária, unidade/janela/perímetro e cobertura deste conceito não são verificáveis. [Issue 14], [B20]

## O que as oito métricas provam

O perfil fechado usa perspectiva **1005, Conglomerados Financeiros e Instituições Independentes**, relatório **92**, referência **202412**. Não representa automaticamente emissor/holding, consolidado societário ou todos os bancos elegíveis. Cada ocorrência precisa de vínculo datado; as [oito relações históricas ainda desconhecidas](capital-aberto-identity-dossier.md) permanecem desconhecidas. [C], [Issue 3]

| Métricas admitidas | Localizadores do dicionário D / células | Unidade/janela | Cobertura por variável na admissão |
|---|---|---|---|
| AT; carteira de crédito classificada; passivo circulante/exigível a longo prazo/resultados futuros; captações; PL | D `/455..459`; `ifd=lid=78182..78186`, respectivamente | BRL bruto inferido do formatador do portal; estoques em 31/12/2024 inferidos do conceito | Cada variável: 1.415 células numéricas armazenadas / 1.422 registros cadastrais. [C], [E] |
| LL | D `/605`; `ifd=79718`, `lid=78187` | BRL bruto inferido; **01/07–31/12/2024**, nota `rp` 1 | 1.415 / 1.422. [C], [E], [P] |
| Agências; postos de atendimento | D `/591..592`; cadastro `c16`, `c17` | Contagens cadastrais na referência | Cada variável: 1.422 / 1.422. [C], [E] |

São **11.334 observações admitidas**: 8.490 montantes e 2.844 quantidades; **42 posições monetárias sem armazenamento** ficam na cobertura. Cinco entidades não armazenadas e duas sem cada localizador monetário não são NI/NA ou zero observados. Zeros reais de crédito/captações permanecem zeros; tratamento de denominador zero ou PL negativo pertence ao método, sem exclusão automática. [C], [E]

Cobertura por variável não é cobertura de indicador, banco/ano ou amostra acadêmica. Esta pesquisa não reprocessou observações nem mediu interseções analíticas; a tabela resume os ledgers aceitos. Não há prova neste recorte de depósitos, provisões, receitas de intermediação, ativos/passivos sensíveis, componentes ajustados ou médias históricas. Ausência no Resumo admitido não comprova ausência em todos os relatórios IF.data. [C], [E]

## Janelas, comparabilidade e alternativas

1. **Fluxos:** o `rp` define março/junho como janeiro–março/janeiro–junho, e setembro/dezembro como julho–setembro/julho–dezembro. Dezembro isolado não é anual; somar quatro saldos trimestrais acumulados duplicaria parcelas. Junho + dezembro é somente possibilidade condicionada a notas, rubricas, vintages e perímetro compatíveis, ainda sem comprovação financeira histórica. [P], [C], [Issue 3]
2. **Médias:** a Issue 3 conserva alternativas de média trimestral trapezoidal e média abertura/fechamento para ROA/ROE. Ambas, como ali propostas, exigem abertura comparável; **200912 seria insumo de abertura de 2010 se esse método for escolhido**, sem alterar automaticamente a janela acadêmica 2010–2024 nem autorizar coleta. O FMI aceita abertura/fechamento como mínimo e encoraja maior frequência; não prescreve aqui a aproximação trimestral proposta. [Issue 3], [F] §7.48
3. **ROE BCB:** a média de treze meses de PL ajustado exige componente/frequência próprios. Uma média trimestral de PL contábil não reproduz automaticamente o REB 2023. Comparabilidade econômica e de consolidação precisa ser provada, mesmo com divisão aritmética possível. [B23], [C]
4. **Perfil agregado:** média/mediana dos índices por instituição e razão das somas são escolhas distintas, mantidas na Issue 3. Não escolher pesos, eliminar faltantes, winsorizar ou definir elegibilidade nesta nota. O [glossário](../../GLOSSARY.md) separa ocorrência, unidade analítica, janela e vintage. [Issue 3]

Equivalência de rubricas, sinais, composição e consolidação não segue de nomes iguais. A [comparabilidade de 2025](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16) tem escopo próprio; esta pesquisa não costura regimes/perspectivas ou promove dados individuais existentes a cobertura financeira histórica.

## Três perguntas para João/orientador — Issue 3

1. **População/unidade:** qual critério temporal de capital aberto (CVM/B3) e qual unidade financeira vinculada a emissor/holding serão adotados? Conservar os oito vínculos desconhecidos até prova datada; cadastro técnico não decide elegibilidade.
2. **Método anual/perfil:** qual janela de resultado, numerador (incluindo tributos/ajustes), média de estoques e agregação do perfil serão adotados? Especificar necessidade de abertura 200912 e compatibilidade de junho/dezembro; obter fonte/página para adaptações antes de calcular.
3. **GAP:** operacionalizar AS/PS com componentes bilaterais comprovados, ou reformular o objetivo quantitativo? Diferença por faixas requer outro fundamento e decisão própria.

A recuperação da proposta corrigida e do complemento bibliográfico é uma lacuna de entrada, anterior à comparação completa dos sete candidatos. Esta nota é revisável como pesquisa de fontes/componentes e desconhecidos; não satisfaz sozinha o aceite integral da proposta, a escolha da Issue 3 ou uma autorização de implementação.

## Verificação e estado

Foram lidos AGENTS, arquitetura, glossário, contrato da Issue 14 e decisão da Issue 3, sem comentários adicionais retornados; perfil fechado, contrato/ledger de admissão e registro privado da revisão anterior foram conferidos. Matt `research` foi aplicado como pesquisa por agente dedicado; Feynman `pdf-explore` foi aplicado à leitura cruzada de métodos/tabelas/notas por ferramentas PDF disponíveis, sem instalação ou execução alegada de deep-research.

Os PDFs de Lima/FMI/REB 2023 e seus localizadores foram conferidos via consulta documental; a consulta web do REB 2020 falhou em leituras posteriores, então seu PDF oficial foi lido localmente com `pypdf` do runtime já disponível. Documento de 253 páginas, SHA-256 `295250c29a4f8c14785a0de2e2bd2a92075ad046a9a82eec1a8fc9fb5adbbf1c`, consulta em 2026-10-04. Extrações/proveniência ficam na preparação privada; nenhum valor bancário foi publicado. Links e correspondência com o perfil são checks documentais; testes de software não se aplicam a esta nota.

Revisão independente e publicação desta nota devem ser confirmadas na Issue/PR real pelo integrador. Não são afirmadas aqui. A lista original, fontes/páginas Assaf/Marion, mapeamentos operacionais e cobertura analítica continuam pendentes; nenhum indicador foi implementado ou calculado.

</details>

[Issue 14]: https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/14
[Issue 3]: https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3
[L]: https://www.scielo.br/j/rac/a/ZPMKdbB7pSn3hBB7Rs8XkYL/?lang=pt
[B20]: https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb_2020.pdf
[B23]: https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb2023p.pdf
[REF25]: https://www.bcb.gov.br/content/publicacoes/ref/202504/RELESTAB202504-refPub.pdf
[F]: https://www.imf.org/-/media/files/data/2019/2019-fsi-guide.pdf
[A]: https://www.institutoassaf.com.br/product/estrutura-e-analise-de-balancos/
[C]: financial-snapshot-202412-contract-20261003.md
[E]: financial-snapshot-202412-execution-20261003.md
[P]: ../../bank_quality/financial-profile-202412.json

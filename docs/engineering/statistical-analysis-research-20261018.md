# Análises estatísticas e econométricas para a monografia

Pesquisa da [Issue162](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/162), 18/10/2026. **Proposta para decisão acadêmica**, baseada em literatura primária e diagnóstico de dados aceitos; não adota estimador, limiar, índice ou estratégia causal novos. Núcleo2010–2024; complemento2025–2026 permanece separado. Plano e checks no [plano de execução](../superpowers/plans/2026-10-18-statistical-analysis.md); fontes e limitações na [proveniência](statistical-analysis-research-20261018.provenance.md).

## Recomendação e alcance

O núcleo proporcional ao objetivo atual é **descritivo e comparativo**: evolução das cinco dimensões no sistema observado e por Tcb; distribuição das unidades; comparação das associadas às companhias com o restante; cobertura e composição em cada resultado. Sr e SrAnalitico acrescentam recortes em janelas próprias quando a pergunta e a disponibilidade justificarem. Econometria pode aprofundar uma pergunta delimitada, mas não constitui obrigação inferida da existência de um painel. A pesquisa não examinou exigências curriculares da UNICAMP e não substitui a orientação acadêmica.

Essa recomendação é síntese do pesquisador aplicada aos dados. O FMI mostra por que indicadores agregados precisam de concentração e distribuição para revelar heterogeneidade [F1, cap12]; a literatura econométrica delimita o que inferências sobre séries/painéis exigem [E1–E6]. Nenhuma fonte escolhe automaticamente o método desta monografia.

As versões autorais consultadas no Drive preservam intenções de avaliar evolução, comparar tipos e investigar explicações. Versões diferentes incluem hipóteses sobre gestão de risco/macroeconomia e promessa de índice. Essas intenções precisam ser reconciliadas com o protocolo atual: demonstrações contábeis não observam diretamente qualidade da gestão; associação não identifica causa; índice/ranking continua condicionado na [decisão3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3). Não foram alterados manuscritos, nem publicadas suas cópias, links privados ou trechos integrais.

**Pergunta de trabalho proposta:** como evoluem e diferem as dimensões econômico-financeiras dos negócios representados no IF.data em2010–2024, no conjunto e por Tcb, e em que medida os padrões observados se relacionam à composição e aos recortes institucionais disponíveis? As unidades vinculadas às companhias elegíveis constituem comparação específica, sujeita à evidência temporal dos vínculos. João/orientador decidem sua redação final.

## Entrada fixa e diagnóstico efetivamente executado

O ponteiro compartilhado `data/curated/current-indicators.json` foi lido pelo procedimento do [guia local](local-queries-20261013.md#base-de-indicadores-vigente-entre-tasks). Seleção `accepted_local`: pacote privado `data/curated/ifdata-composition-terra-20261017-run2`; manifesto SHA-256 `ce57545b643d9efcfbb09ee26234c97f131080627d42622c2b4cfbf998f7c524`, contrato `ifdata-composed-analysis-v1`. Este pin permanece a entrada da tarefa mesmo se outra frente atualizar o ponteiro.

O manifesto registra32 companhias analíticas, provenientes das associações admitidas; a referência documental abrange55 companhias. Companhia, código nativo, ocorrência unidade/data e cluster independente são objetos distintos. A presença de32 na configuração não certifica cobertura histórica integral dessas companhias nem das55.

Foram autenticadas individualmente e verificadas por contagem/unicidade de id:

| Tabela aceita consumida | Linhas | Uso nesta pesquisa |
|---|---:|---|
| aggregates.parquet |12.960| Presença de resultado, estados, unidades/companhias esperadas e elegíveis por trimestre/indicador/coorte |
| joint_cells.parquet |305.090| Contagens de unidades por Tcb e cruzamentos Sr/SrAnalitico, preservando estados |
| unit_periods.parquet |244.001| Disponibilidade literal de classificações por perspectiva/data |

O diagnóstico de leitura produziu12.960 linhas de cobertura agregada por contexto/período no total do arquivo,216 resumos de agregado,234.292 linhas de cobertura de categorias/cruzamentos e4.992 grupos de classificações. Outputs, script, hashes e comandos estão no staging privado identificado na proveniência. Não recalculou indicadores financeiros nem estimou modelos. Frações financeiras permanecem como numerador/denominador exatos; contagens não foram usadas para redefinir aceite da base.

| Recorte efetivamente observado | Disponibilidade de agregado | Consequência para o desenho |
|---|---|---|
| Financeiro, sistema, indicadores pontuais C1/L2/L3/LA/LC/LF-DEP/LF-EM/LF-OC/LF-REP/Q1 |60 referências201003–202412| Há eixo temporal para descrever; isso não implica todas as unidades/componentes elegíveis |
| Financeiro, sistema, fluxos E2-B/E3/Q2/R1/R2/R4/R5/RS, trimestre efetivo |60 referências201003–202412| Pode sustentar inspeção trimestral com sazonalidade e conceitos próprios |
| Mesmos fluxos,12meses |57 referências201012–202412| Três referências iniciais sem agregado TTM; não encurtar janela nem anualizar trimestre por quatro |
| Capital prudencial, sistema, C3/C4 pontuais |40 referências201503–202412| Não produzir série2010–2024 contínua mediante emenda financeira |
| Sr original não vazio no cadastro deste pacote |Primeira observação201706 no Financeiro/Capital;201703 no Individual| Oferta normativa2017+ e observação no pacote são afirmações diferentes |
| SrAnalitico não vazio |Primeira observação201703 nas três perspectivas| Derivado tem origem/qualificações próprias; não substitui automaticamente o Sr original |

No Financeiro da coorte sample, R1/R2/E2-B emTTM têm agregado em57 referências, mas todas as unidades esperadas são elegíveis em36 das60 referências. Q2/TTM tem agregado em57, sem referência com todas as unidades esperadas elegíveis. Portanto, a impressão de completude temporal pode coexistir com seleção variável de unidades. O indicador de elegibilidade é estritamente relativo à população esperada do pacote; não transforma ausência ou inaplicabilidade em erro de dados, nem mede participação nacional. A composição por Tcb/Sr ainda precisa acompanhar cada comparação escolhida.

Tcb literal financeiro observado incluiB1,B2,B3C,B3S,B4,N1,N2,N4 e ausências. Não se preenche categoria faltante nem se define uma ordenação econômica automática. Listas unitárias de alguns payloads são truncadas por contrato: o diagnóstico usa contagens, não essas listas para afirmar relação exaustiva de nomes.

A saída categórica atual contém sample/remaining/unknown; não contém total diretamente. A revisãoA reconciliou28.140 contagens categóricas e3.240 identidades total=sample+remaining+unknown, sem divergência. Para apresentar cobertura do sistema porTcb, o caderno posterior deve derivar as contagens das coortes disjuntas e registrar essa operação; não somar razões ou quartis dessas coortes. O cruzamento conserva estado da variávelSr, mas só valor daTcb cruzada; a visãoTcb isolada conserva também seu estado.340 contextos não-total ausentes das células têm zero unidades esperadas/elegíveis. Esses detalhes impedem interpretar linha ausente automaticamente como dado financeiro faltante.

## Matriz pergunta → quantidade → técnica → argumento

| Pergunta | Quantidade de interesse e saída | Método candidato e dados | Interpretação e limite |
|---|---|---|---|
| Como evoluiu cada dimensão? | Trajetória trimestral e síntese anual, sistema/Tcb | Razão das somas já contratada; níveis e variações em pontos percentuais para índices na mesma escala | Evolução do conjunto elegível; não experiência da instituição típica. Exibir n/cobertura e quebras. [F1–F2] |
| O agregado oculta diferenças? | Mediana e faixa interquartil, contagem de unidades | Reusar quantis tipo2 sem peso já adotados; dados unitários válidos no mesmo contexto | IQR descreve dispersão, não intervalo de confiança, risco absoluto ou classificação bom/ruim. [F1, cap12] |
| Como muda o peso das categorias? | Razões porTcb e composição do denominador | ComponentesN/D de grupos compatíveis, estados e participações próprias | Mudança no total combina pesos e resultados dos grupos. Pesos negativos impedem interpretação convexa. [F1, §§7.5,12.21] |
| Sr ajuda a interpretar diferenças dentro deTcb? | Poucos cruzamentos pertinentes, com n e faltantes | Estatísticas anteriores por enquadramento contemporâneo; original e derivado em saídas distintas | Recorte prudencial observado/derivado, não relação linear tamanho→risco. Janela própria. [F2–F3] |
| Associadas diferem do restante? | Diferença de agregados em p.p., trajetórias e distribuições | Coortes disjuntas sample/remaining e unknown visível; sistema como referência que contém as anteriores | Diferença descritiva, sem efeito de listagem. Restante é relativo aos vínculos admitidos, não lista comprovada de todas as fechadas. |
| A mudança depende de composição? | Entradas/saídas, reclassificações e sensibilidade no conjunto comum | Identidade/perímetro demonstrados nas datas; série dinâmica ao lado do conjunto comum | Balanceamento muda população e pode selecionar sobreviventes. Não corrige automaticamente seleção. [F5] |
| Poucas unidades conduzem o agregado? | Contribuições aoN/D, influência leave-one-out e cobertura perdida | Componentes unitários exatos; só em ticket próprio | Sensibilidade descritiva, sem apagar extremos ou tratar amplitude comoIC. Pesos assinados são necessários quandoD negativo. [F1, inferência aplicada] |
| Há associação com o ciclo/entre dimensões? | Gráfico, sequência temporal e eventualmente correlação/modelo | Pergunta e pares definidos; contexto macro da159; diagnóstico da dinâmica | Relações entre agregados não provam relação individual ou causal. TTM compartilha parcelas. [E1–E4] |

Aplicabilidade econômica precede completude: não eleger uma métrica bancária para todas asTcb apenas porque há valor calculável. Crédito/provisão não é inadimplência observada; liquidez contábil não éLCR/NSFR; eficiência de razão contábil não é fronteira produtiva. As [fórmulas e limites existentes](financial-indicators-formulas-20261017.md) continuam a referência; esta pesquisa não cria novos bindings ou denominadores.

### Agregado, ponderação e instituição típica

O FMI distingue agregação dos componentes e distribuição institucional. Razão das somas é `soma(N_i)/soma(D_i)` na mesma interseção elegível. Quando todos osD_i pertinentes são positivos, equivale à média das razões ponderada porD_i; com pesos negativos perde-se a interpretação como média convexa. Não substituir por média simples dos índices. Somar grupos consolidados não elimina exposições entre grupos nem consolida economicamente todo o setor. [F1, cap6 e§7.5]

O guia usa denominador do indicador para DP ponderado (§12.21), mas AT para quartis ponderados comparáveis entre indicadores (§12.28/Box12.1). São objetos diferentes. Os quantis sem peso já adotados não serão silenciosamente substituídos. Quantis ponderados,HHI e faixas próprias são candidatos condicionais, não exigências desta entrega. O REFabril2024 oferece precedente de mostrar distribuição doROE por participação nos ativos e contagem deIF ao mesmo tempo, mas usa metodologia/ajustes próprios que não são reproduzidos aqui. [F1,F4]

### Cobertura que acompanha cada resultado

1. **Indicador/componentes:** unidades observadas, esperadas e elegíveis, janela, denominador, status e motivos de não cálculo.
2. **Vínculos:** companhias esperadas, associações admitidas, desconhecidos e unidades únicas por referência.32 companhias não significam32 contribuições independentes.
3. **Peso econômico conhecido:** AT/crédito/PL próprios e compatíveis; participação apenas no universo cujo estoque é conhecido, ausências explícitas e cuidado comPL negativo. Não chamar essa fração de cobertura total certificada.

Não há nesta pesquisa limiar universal de percentual, n mínimo,topN ou regra de exclusão. Uma célula com uma unidade pode ser descritível, mas não caracteriza heterogeneidade interna; pequeno n e alta concentração devem aparecer. Critérios de seleção do corpo principal devem ser justificados por conceito/cobertura e registrados antes de buscar resultados favoráveis.

## Quando a econometria acrescentaria uma resposta

### RotaA — descrição e comparação fundamentadas: recomendada como núcleo

Responde como os indicadores evoluem e diferem no universo observado. Tabelas, trajetórias, magnitude das diferenças, distribuição e contexto documentado não exigem p-valores por rotina. Há erro de mensuração, cobertura e interpretação mesmo sem amostragem aleatória; observar o universo definido não elimina toda incerteza nem cria automaticamente uma superpopulação para inferência.

### RotaB — associação em poucas séries agregadas: extensão possível

Pergunta adicional precisa definir variável resposta, regressores, horizonte, estimando, janela, transformação e defasagens. No máximo60 referências trimestrais,57 emTTM e menos nas segmentações não sustentam automaticamente muitos regressores/lags. Antes de estimar: gráficos, valores extremos, persistência, sazonalidade, estabilidade de conceito/perímetro, tendência e alinhamento temporal com a macro da159.

TTM consecutivos compartilham três fluxos trimestrais; isso induz dependência mesmo num exemplo com fluxos independentes. Para razões com estoques móveis, persistência e composição, não demonstra erroMA(3) nem justifica bandwidth3 automático. Correlação Pearson/Spearman pode ser exploração descritiva, mas seu teste usual de independência não fica válido só por escolher ranks.

Uma regressão parcimoniosa com covariânciaHAC é candidata para associação sob hipóteses explícitas, com diagnóstico/sensibilidade. HAC não remove endogeneidade, omissão, quebra ou regressão espúria; consistência assintótica não garante inferência boa em amostra curta. Kiefer/Vogelsang discutem sensibilidade ao bandwidth e alternativas com valores críticos próprios. [E1] Granger/Newbold mostram riscos de regressão em níveis de séries integradas independentes; não justificam diferenciar tudo nem exigir bateriaADF/KPSS para gráficos descritivos. [E2] Estacionariedade/cointegração formal exigiria contrato e literatura adicionais.

### RotaC — painel institucional: somente com outra pergunta e validação

Pergunta entre/dentro das unidades precisa de identidade temporal, unidade não sobreposta, eventos e seleção explicitados. FE de unidade absorve uma categoriaTcb/Sr que não varia naquela unidade; FE completos de tempo absorvem uma macrovariável igual para todas as unidades na mesma data. Mudanças de categoria não viram variação exógena.

Erros clusterizados exigem escolher o nível de dependência e justificar aproximação; poucos clusters e tamanhos desiguais podem prejudicá-la, sem corte seguro universal. Não clusterizar mecanicamente pelas poucas categoriasTcb/Sr. Cluster por unidade não resolve por si só dependência transversal; Pesaran discute diagnóstico inclusive em painéis desbalanceados, sob condições que precisam ser examinadas. [E3–E4] O número de linhas/companhias não mede informação independente.

PainelFE, painel dinâmico/GMM,VAR/VECM,DiD, estudos de eventos,DEA/SFA ePCA não são um pacote obrigatório. Não se adota qualquer um deles sem pergunta, medida, identificação e diagnóstico próprios. DEA/SFA abordam eficiência de fronteira;PCA maximiza variação estatística, não valida um índice econômico de qualidade/risco. Essa delimitação preserva o contrato da pesquisa financeira existente, sem constituir uma revisão específica desses métodos.

### Hipóteses múltiplas e seleção

Se houver inferência, definir uma família pequena de hipóteses e separar exploração de confirmação. Holm pode controlar erro familiar sob dependência arbitrária com p-valores individuais válidos; ajustes/reamostragem não consertam testes mal especificados. Romano–Wolf exige esquema compatível com a dependência. FWE eFDR respondem a critérios diferentes. Não selecionar só resultados significativos para depois ajustar sua multiplicidade. [E5–E6] Selecionar indicadores por conceito/cobertura é defensável se transparente; escolher pelo sinal desejado e declarar hipótese prévia não é.

## Estrutura de redação que o plano pode sustentar

- **Introdução:** problema, relevância, objetivo de evolução/comparação e alcance observado; reconciliar promessa de índice e linguagem de causas com o método efetivamente escolhido.
- **Referencial institucional/teórico:** modelos de negócio, cinco dimensões e canais de financiamento/crédito/capital/resultado; distinguir mecanismo plausível de efeito identificado.
- **Dados e método:** população documental e associações, unidade/perímetro, período, indicadores, precisão/janelas, agregação/distribuição, cobertura, quebras e escolha dos recortes. Incluir limitações da seleção fixa2024 e da história dos vínculos.
- **Resultados:** cobertura/composição → panorama das dimensões → Tcb → cruzamentosSr pertinentes → associadas/restante quando sustentado → sensibilidade e discussão conjunta.
- **Conclusão:** responder à pergunta e aos limites, sem converter posição relativa em melhora absoluta ou correlação em recomendação/causalidade.

O objetivo pode ser redigido agora como proposta; resultados concretos só entram após aceite das saídas correspondentes. Esta entrega não escreve capítulo no Word nem escolhe a versão autoral vigente por data de arquivo.

## Fontes primárias e localizadores efetivamente lidos

**F1.** FMI. *Financial Soundness Indicators Compilation Guide*, edição final2019. [PDF oficial](https://www.imf.org/-/media/files/data/2019/2019-fsi-guide.pdf). Cap6 §§6.1–6.6,p67; cap7 §§7.5–7.7,pp84–85; cap12 §§12.1–12.3,12.12–12.13,12.18–12.29 eBox12.1,pp156–162 impressas. PDF tem preliminares: usar numeração impressa e parágrafo para localizar. Fonte central de agregação/distribuição, sem equivalência automáticaIF.data–FSI.

**F2.** BCB. *IF.data — Esclarecimentos e Metodologia*, pp1–2, notas1–3. [Documento corrente](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf). Sem data editorial comprovada; descreve perspectivas, disponibilidades e inclusão de agências externas das independentes desde2018.

**F3.** CMN. Resolução4.553/2017, versão originalv1, arts1–4,6–8,10,pp1–5. [PDF original](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50335/Res_4553_v1_O.pdf). Fonte de origem da segmentação, sem reconstrução retrospectiva de todas as versões.

**F4.** BCB. *Relatório de Estabilidade Financeira*, abril2024, §1.2.3,p32, gráficos1.2.3.1–2 e notas44–49. [PDF](https://www.bcb.gov.br/content/publicacoes/ref/202404/RELESTAB202404-refPub.pdf). Precedente de distribuição/contagem com ajustes próprios.

**F5.** Nakane,M.; Weintraub,D. *Bank Privatization and Productivity: Evidence for Brazil*, BCBWP90,2004. [Artigo original](https://bcb.gov.br/content/publicacoes/WorkingPaperSeries/wps90.pdf). Introdução,pp5–6, e método,pp12–13 impressas: seleção, saídas e eventos. Leitura parcial delimitada, sem transportar resultados/modelo.

**E1.** Kiefer,N.; Vogelsang,T. *A New Asymptotic Theory for Heteroskedasticity-Autocorrelation Robust Tests*, revisão23/03/2005, §§1–3 e5.1–5.2,pp1–9/13–18 do manuscrito. [Texto dos autores](https://kiefer.economics.cornell.edu/newasym2.pdf); [DOI](https://doi.org/10.1017/S0266466605050565). Equação6 e experimentos não garantem desempenho em nossa base.

**E2.** Granger,C.; Newbold,P. *Spurious Regressions in Econometrics*,1974, §§4–5,pp115–118. [DOI editorial](https://doi.org/10.1016/0304-4076(74)90034-7); [cópia do artigo primário lida](https://gwern.net/doc/economics/1974-granger.pdf). Hospedagem da cópia não editorial, identificada como limitação.

**E3.** Cameron,A.; Miller,D. *A Practitioner's Guide to Cluster-Robust Inference*,2015. [Manuscrito dos autores](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf), §§III–VI,pp12–32, equações17–18; [DOI](https://doi.org/10.3368/jhr.50.2.317). Hipóteses de dependência, FE e poucos clusters.

**E4.** Pesaran,M. *General Diagnostic Tests for Cross Section Dependence in Panels*, IZADP1240,agosto2004. [PDF](https://docs.iza.org/dp1240.pdf), §9,pp17–18,equação31,e conclusão§12. Não confundir versão2004 com publicação posterior.

**E5.** Romano,J.; Wolf,M. *Exact and Approximate Stepdown Methods for Multiple Hypothesis Testing*,2005. [Texto dos autores](https://www.econ.uzh.ch/dam/jcr:ffffffff-935a-b0d6-ffff-ffffd823d949/jasa.pdf), §1,p94;Example4,p97;abertura§4,pp100–101; [DOI](https://doi.org/10.1198/016214504000000539).

**E6.** Romano,J.; Shaikh,A.; Wolf,M. *Formalized Data Snooping Based on Generalized Error Rates*,2008. [Texto dos autores](https://www.econ.uzh.ch/dam/jcr:ffffffff-935a-b0d6-ffff-ffffff21355a/et_2008.pdf), §§1–2,pp404–406; [DOI](https://doi.org/10.1017/S0266466608080171).

Newey/West consta como leitura bibliográfica complementar na proveniência: acesso limitado a metadados/resumoNBER. Não se declara leitura de seus teoremas. Afirmações técnicasHAC acima dependem deE1. O conjunto é uma revisão narrativa dirigida, sem busca sistemática/exaustiva de toda a literatura.

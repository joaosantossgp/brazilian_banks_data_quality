# Proposta de protocolo: tratamentos, testes e robustez dos indicadores

Pesquisa da [Issue 173](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/173), 18/10/2026. **Proposta para João/orientador; nenhum tratamento ou teste inferencial adotado ou executado por este documento.** Não interpreta resultados, atribuição de outra task. [Plano](../superpowers/plans/2026-10-18-statistical-treatment-protocol.md) e [proveniência](statistical-treatment-protocol-20261018.provenance.md).

## Recomendação

Adotar um núcleo de **validação dos dados, diagnóstico de extremos e verificações de robustez** para as comparações selecionadas. Acrescentar testes de hipóteses somente quando estiverem definidos a quantidade comparada, a origem da incerteza e um procedimento compatível com a dependência dos dados. A existência de testes em um artigo semelhante não torna esses testes obrigatórios para outra pesquisa.

A proposta fecha três camadas: A — integridade e comparabilidade; B — sensibilidade das medidas; C — inferência condicional. A e B sustentam o núcleo descritivo/comparativo escolhido na [decisão 165](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/165). C pode ser útil sem se transformar numa investigação causal, mas requer aprovação acadêmica e validação técnica próprias. Significância não mede magnitude ou importância econômica; a [ASA, princípios 1–6, p. 2](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf), recomenda desenho adequado, transparência e avaliação que ultrapasse um limiar de p-valor.

## O que o artigo SOBER 2012 oferece

O PDF indicado é *Análise do desempenho econômico das empresas agroindustrais de capital aberto no Brasil*, Martins, Silveira e Bacic, SOBER 2012; [registro público autoral](https://www.researchgate.net/publication/264759277_Analise_do_desempenho_economico_das_empresas_agroindustrais_de_capital_aberto_no_Brasil). A leitura foi feita no arquivo fornecido pelo Drive, preservado privadamente. São 20 páginas físicas, com capa adicional: **página PDF = impressa +1** no corpo do trabalho.

| Elemento conferido | Procedimento do artigo | Aplicação nesta proposta |
|---|---|---|
| pp. 4–5, método | Indicadores empresariais, média/mediana/DP por ano; comparação 1995–2001 vs 2002–2010, corte motivado pelo cenário de commodities | Aproveitar a ligação entre pergunta, medida e comparação; não importar o corte temporal |
| p. 5 e nota 4 | Testes t de médias e F de variâncias, normalidade pressuposta, alternativa bilateral e significância de 10%; graus de liberdade alternativos para variâncias diferentes | Não adotar F→t ou alfa de 10% por precedente; definir estimador e pressupostos adequados |
| pp. 5–6, amostra |101 companhias, admitindo dados incompletos | Não confundir companhias, anos e observações independentes; registrar composição |
| p. 11; tabelas pp. 10,13,15,17 | Ressalva sobre normalidade; tabelas com estatísticas/p-valores | Conferir hipóteses, caudas, n e graus de liberdade antes de reproduzir testes |

Há motivos adicionais para leitura crítica. A p. 5 declara teste bilateral, enquanto a tabela 5/p. 13 combina t=−0,0034 com p=0,4987, indício de cauda única; em uma distribuição t simétrica, um t tão próximo de zero teria p bilateral próximo de1. A fórmula e os graus de liberdade descritos também precisam ser reconciliados antes de uma reprodução. O texto/p. 15 diverge da tabela 6 ao atribuir valores ao ROE. Não estão disponíveis dados, código e n/gl por teste para resolver essas divergências ou reproduzir a execução. Na metodologia examinada, não foi localizado tratamento explícito da dependência temporal ou ajuste de multiplicidade; isso não prova que nunca tenham sido considerados.

O artigo serve de referência para formular comparações. Suas escolhas e inconsistências não validam nem invalidam automaticamente os indicadores IF.data. Esta pesquisa não reproduz seus resultados, fórmulas ou explicações econômicas.

## Entrada fixa e condições da nossa base

O ponteiro aceito foi descoberto pelo [procedimento vigente](local-queries-20261013.md#base-de-indicadores-vigente-entre-tasks). Esta pesquisa sucessora **migra explicitamente** para `data/curated/historical-links32-composition-20261018-run3`, manifest SHA-256 `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`, contrato `ifdata-composed-analysis-v1`. Não altera o pin ou o caderno da 166. A [revisão de vínculos históricos](historical-company-links-32-20261018.md) descreve a atualização; a coorte de referência 2024 não equivale a abertas históricas em todos os trimestres.

Foram autenticados hashes e conferidas contagens/schema de `aggregates` (12.960 linhas), `joint_cells` (305.296) e `unit_coverage` (5.021.050). Esta foi uma inspeção estrutural: não calculou nova cobertura por indicador, distribuição, normalidade, autocorrelação, extremos ou significância. Não transportar os números do pin anterior como diagnóstico novo.

As tabelas têm colunas textuais e payload JSON. `unit_coverage` conserva componentes N/D, fração do indicador, tipo de linha, identificadores da unidade/resultado, status, classificação, vínculos e origem. Isso permite planejar influência e composição; não certifica automaticamente unicidade ou continuidade econômica. As listas nominais de agregados/células podem ser truncadas: uma futura execução deve usar registros nativos completos, sem reconstruir trajetórias a partir dessas listas.

O núcleo continua 2010–2024, por perspectiva e janela própria. Financeiro é principal; Capital prudencial e Individual separados. Capital não recebe série financeira para preencher 2010–2014; SrAnalitico não é retroprojetado antes de sua oferta e deve conservar estados/proveniência. Fluxo trimestral, TTM e estoque pontual não são observações intercambiáveis. TTM consecutivos compartilham fluxos; a escolha de dezembro reduz a sobreposição mecânica entre janelas anuais, mas não demonstra independência e reduz o número de datas.

## A — Preparação e diagnóstico essenciais

“Essencial” designa o mínimo recomendado **se este protocolo for adotado**, sem criar um novo critério de aceite da base.

| Procedimento | Regra proposta e saída auditável |
|---|---|
| Identidade e duplicação | Selecionar linhas nativas, separar placeholders/associações e validar uma contribuição por unidade×perspectiva×data×indicador×janela×método/versão. Unicidade de id não basta. Não multiplicar uma unidade porque está ligada a várias companhias; não somar conglomerado e membros sobrepostos |
| Conceito e período | Conferir fórmula, escala, interseção elegívelN/D, horizonte e aplicabilidade por Tcb. Registrar mudanças de perímetro/regime, especialmente 2014/2015,2018 quando pertinente e2025 separado; não harmonizar só por nome |
| Ausências | Manter estrutural, não observado, NA, NI, null, vazio e zero distintos; tabela de motivos por grupo/data. Principal usa observações elegíveis segundo contratos existentes. Não imputar média, zero, interpolação ou último valor por rotina |
| Cobertura e seleção | Informar unidades esperadas/elegíveis, companhias distintas, unknown e peso econômico conhecido na mesma perspectiva/data; lacunas de AT/crédito/PL explícitas. Não chamar cobertura conhecida de cobertura nacional certificada, nem tratar ausência como amostra aleatória |
| Denominadores e sinais | Preservar zero/negativo e flags existentes; zero segue a regra de não cálculo do indicador. ExaminarN/D separadamente, sinais e magnitude relativa em escala compatível. Não adicionar constante nem impor piso monetário comum |
| Extremos e distribuição | Inspecionar distribuição por indicador/grupo/data, mediana/quartis/IQR, extremos ordenados e componentes dos casos destacados. Contrastar com a própria história somente se identidade/perímetro comparáveis. Não misturar todas as Tcb/datas para definir uma distribuição única |
| Registro de tratamento | Cada ocorrência recebe motivo, referência, status e ação: conservar; investigar; erro comprovado encaminhado para correção versionada; ou sensibilidade explicitamente separada. Nenhuma alteração silenciosa do original |

Um valor extremo pode ser correto. A orientação [NIST, detecção de outliers, §§Introduction/Labeling](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm) distingue sinalizar, acomodar e testar um extremo. A proposta preserva observações válidas no resultado principal. Boxplot ou distância à mediana podem ajudar a triagem; cortes como 1,5 IQR, z = 3 ou winsorização de 1% **não são regras de exclusão adotadas**. Se forem necessários para organizar auditoria, seus parâmetros e casos degenerados — IQR/MAD zero, pequeno grupo — serão registrados antes da execução.

Para razões, “denominador pequeno” não tem um corte universal. O exame deve mostrar sua escala econômica e a sensibilidade do agregado. Denominadores negativos podem cancelar positivos: a razão das somas deixa de ser uma média convexa. Não removerPL negativo apenas para obter uma série mais regular. A literatura sobre [razões, Franz 2007, pp. 6–12/15–18](https://arxiv.org/pdf/0710.2024) também alerta para inferência instável quando um denominador estimado se aproxima de zero; esse problema de inferência não deve ser confundido com erro contábil comprovado.

Não padronizar ou transformar os dados para “passar” em normalidade. Logaritmo exclui valores não positivos e muda a quantidade analisada; médias aparadas e winsorização também mudam o objeto. Qualquer alternativa precisa de motivação própria, preservação do principal e aprovação se mudar o método acadêmico.

## B — Robustez descritiva das comparações escolhidas

Executar depois de A, em derivados novos, com regras fixadas antes de examinar quais variantes favorecem uma conclusão. Cada comparação principal deve ter uma ficha de sensibilidade; nenhuma amplitude abaixo é um intervalo de confiança.

| Verificação | Execução proposta | O que registrar |
|---|---|---|
| Instituição influente | Retirar **uma unidade por vez**, dentre todas as elegíveis do recorte, e recomputar a razão dos componentes restantes; não excluir permanentemente a unidade | Mudança em p.p./escala original, unidade omitida, quantidade e peso conhecido retirados, caso não calculável |
| Composição | Ao comparar duas datas/janelas previamente escolhidas, apresentar população dinâmica e conjunto comum com identidade/perímetro sustentados | Entradas, saídas, reclassificações, perdas de contagem e de peso conhecido; conjunto comum muda a população e pode selecionar sobreviventes |
| Cobertura | Comparar a disponibilidade dos mesmos componentes e recortes entre datas/grupos; repetir em janela comum justificada quando necessário | Período efetivo, perdas e motivos; não escolher janela apenas porque dá diferença maior |
| Agregado e distribuição | Razão das somas ao lado de mediana/quartis institucionais já contratados | São quantidades diferentes, não duas estimativas intercambiáveis do mesmo objeto; não exigir mesmo sinal |
| Horizonte | Para fluxo pertinente, contrastar a apresentação TTM com trimestres efetivos e síntese anual conceitualmente adequada | Sazonalidade, dependência e número de datas. Não multiplicar trimestre por 4 nem tratar média dos estoques como estoque de fechamento |
| Classificações e vínculos | Preservar categoria contemporânea e unknown; descrever reclassificações. Sr original e SrAnalitico separados | Origem/conflitos; eventual subamostra de classificação estável tem perdas e outro universo, sem congelamento retrospectivo automático |

Para a influência, sendo `N=ΣN_i`, `D=ΣD_i`, `A=N/D`, calcular `A_(-i)=(N−N_i)/(D−D_i)` e `Δ_i=A_(-i)−A`, na mesma interseção elegível. Se o denominador remanescente for zero ou não restarem unidades elegíveis, registrar “não calculável”. Manter precisão exata na composição e converter apenas apresentação. O registro deve conservar valores assinados e casos de cancelamento; não interpretar contribuições como participações positivas se os denominadores tiverem sinais diferentes. Essa aplicação é proposta do pesquisador, motivada pela distinção entre agregado e distribuição do [FMI 2019, cap. 12, §§12.1–12.3/12.18–12.30](https://www.imf.org/-/media/files/data/2019/2019-fsi-guide.pdf), não uma fórmula de teste do FMI.

Não incluir retirada de “crises”, empresas ou trimestres para obter significância. Cortes substantivos, choques e mudanças regulatórias podem motivar sensibilidades previamente justificadas; não são exclusões neutras. Erros comprovados precisam de correção na frente de dados, não de winsorização para ocultá-los.

## C — Quais testes podem entrar, e em quais condições

Antes de um teste, preencher: **o que é aleatório aqui?** A diferença entre dois agregados no universo observado de uma data é uma descrição condicionada aos dados aceitos. Um p-valor de amostragem não certifica sua correção. Generalizar para outras instituições ou para um processo temporal exige explicar a população/processo e as hipóteses. Registros administrativos incompletos não se tornam amostra probabilística. Essa distinção aplica à monografia a discussão de [Abadie et al. 2020, introdução, pp. 265–267](https://economics.mit.edu/sites/default/files/publications/ECTA12675.pdf), sem importar seus estimadores causais.

### Matriz de decisão

| Pergunta/objeto | Procedimento candidato | Condições e decisão proposta |
|---|---|---|
| Os dados precisam ser normais para descrever agregados/medianas/quartis? | Nenhum teste obrigatório de normalidade | **Não.** Q–Q/histograma podem diagnosticar uma distribuição específica; normalidade não é selo geral da base |
| Uma técnica posterior depende de normalidade? | Shapiro–Wilk, se compatível com observações e desenho; Q–Q complementar | Aplicar no objeto exigido pela técnica, como diferenças/resíduos, não no painel inteiro. Não rejeitar não prova normalidade; rejeitar não escolhe sozinho o substituto |
| Dois grupos institucionais têm médias diferentes em um corte? | Welch bilateral como candidato para médias, sem rotina préviaF→t | Só se a média institucional for a quantidade desejada e houver justificativa de inferência/independência; assimetria severa e n desigual exigem cautela. **Não testa diretamente diferença de razões das somas** |
| Há diferença institucional segundo uma hipótese distributiva ou de ordenação explicitada? | Wilcoxon–Mann–Whitney, condicionado à hipótese e ao desenho | Não é genericamente teste de medianas nem teste consistente contra toda diferença de distribuição; sua interpretação e validade dependem das hipóteses. Mudanças de dispersão/forma importam. Ranks não resolvem dependência, empates ou seleção. Kruskal–Wallis não é atalho para painel empilhado |
| A dispersão institucional é uma pergunta própria? | Levene centrado na mediana/Brown–Forsythe de dispersão, condicional | Pode ser mais resistente à não normalidade que F/Bartlett; continua exigindo desenho adequado. Não usar como porteiro para escolher o teste de médias |
| Agregados de dois grupos diferem persistentemente ao longo da janela? | Série contemporânea `d_t=A_g,t−A_h,t`; média temporal, erro HAC ou bootstrap em blocos como alternativas condicionais | Preferir este objeto ao t ingênuo sobre trimestres. Definir alvo temporal, estabilidade, dependência e ajuste de precisão; pouca informação ou quebras podem impedir inferência defensável |
| Houve mudança entre subperíodos? | Contraste temporal com corte justificado e modelo/reamostragem que respeite a dinâmica | Não copiar t independente pré/pós do artigo. Mudança descritiva não identifica causa do evento; não escolher ponto de quebra pelo menor p |
| As mesmas instituições mudaram entre duas datas? | Análise das diferenças pareadas; inferência apenas com unidade e dependência defensáveis | Pareamento por código sozinho não comprova perímetro estável. Teste pareado convencional ainda pressupõe independência entre pares, não resolve grupos econômicos/choques comuns |

Base metodológica: [NIST sobre normalidade](https://www.itl.nist.gov/div898/handbook/prc/section2/prc213.htm) e [KS de uma amostra](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm); [Delacre et al. 2017](https://rips-irsp.com/articles/10.5334/irsp.82) **com [correção de 2022](https://rips-irsp.com/articles/10.5334/irsp.661)**, que limita generalizações sobre forte assimetria/tamanhos desiguais; [Fay–Proschan 2010, §§3/5.1.1/5.3.2–5.3.3](https://pmc.ncbi.nlm.nih.gov/articles/PMC2857732/); [NIST Levene/Brown–Forsythe](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35a.htm). O KS usual com média/variância ajustadas na mesma amostra não tem os valores críticos do caso completamente especificado; trocar o teste de normalidade não cura a dependência.

### Rota inferencial preferida, se houver uma pergunta adicional

Para o foco atual em agregados/Tcb, **propor um piloto pequeno de diferença entre séries contemporâneas**, em vez de uma bateria de testes sobre todos os indicadores × Tcb × Sr. A escolha de indicador, dois grupos, janela e hipótese será de João/orientador, por conceito e cobertura, antes dos p-valores. Associadas/restante são disjuntas; sistema/associadas não são grupos independentes, pois o sistema contém as associadas. Grupos disjuntos ainda podem compartilhar choques e vínculos econômicos.

1. Formar `d_t` apenas em datas comuns calculáveis e comparáveis; manter o calendário e as lacunas explícitas. Não juntar trimestres separados por lacunas como se fossem consecutivos, interpolar ou fazer compressão temporal. Se faltas/composição impedirem uma janela defensável, manter descrição e sensibilidades.
2. Definir o alvo: por exemplo, média esperada da diferença trimestral num processo temporal com média estável, ou coeficiente de contraste num modelo explicitamente especificado. A média de diferenças temporais não é a razão dos componentes somados ao longo dos anos, nem um efeito de Tcb/listagem.
3. Inspecionar trajetória, sazonalidade, persistência, composição e quebras do objeto/resíduos. ACF é diagnóstico; não rejeição de um teste de autocorrelação não autoriza assumir independência. Ljung–Box, se empregado para resíduos de modelo temporal, precisa de defasagens/graus de liberdade coerentes; [NIST, Box–Ljung](https://www.itl.nist.gov/div898/handbook/pmc/section4/pmc4481.htm) o apresenta como diagnóstico de ajuste, não validador universal de série bruta.
4. Escolher **um procedimento principal**, com sensibilidade previamente definida. HAC exige condições de momentos e dependência que sustentem a aproximação assintótica, regra de kernel/bandwidth e referência inferencial compatível; o desempenho em poucas dezenas de datas pode ser frágil. [Kiefer–Vogelsang 2005, §§1–2/5](https://kiefer.economics.cornell.edu/newasym2.pdf) mostram a importância dessas escolhas. Não fixar lag 3 porque TTM compartilha três fluxos: isso não prova erro MA(3).
5. Se a alternativa for bootstrap em blocos, justificar estabilidade/estacionariedade, dependência fraca e condições de momentos/limite adequadas à estatística, comprimento dos blocos, intervalo, semente e número de replicações/precisão Monte Carlo. Reamostrar conjuntamente o vetor dos grupos por blocos de datas contíguas, preservando covariação contemporânea, ou a própria diferença validada; não sortear os grupos separadamente ou trimestres isolados. Essa aplicação deriva de [Politis 2003, pp. 219–225, §§1–2.3](https://math.ucsd.edu/~politis/StatSci03.pdf). Bootstrap não conserta automaticamente quebras ou denominador instável.
6. Não escolher HAC/blocos/bandwidth pela significância obtida. Na execução futura, validar a implementação e sua adequação ao desenho antes de usar o resultado; um intervalo aparentemente preciso não supera cobertura/identidade insuficientes. Se for necessário um painel institucional ou inferência sobre a própria razão estimada, abrir contrato específico; não importar Fieller i.i.d. ou cluster automático pelas poucas Tcb/Sr.

Esta rota envolve modelagem da incerteza temporal, mesmo sem regressão explicativa. Ela **não é necessária para a descrição** e não foi adotada pela decisão 165. Painel institucional, independência transversal e poucos clusters requerem discussão própria; [Cameron–Miller 2015, §§III–VI](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf) impedem tratar número de linhas como informação independente. Não há n mínimo ou número de clusters universal definido aqui.

## Registro prévio e critérios de execução

Antes de produzir qualquer p-valor, registrar numa ficha por pergunta:

- indicador/fórmula/escala, perspectiva, versão, unidade, grupos, identidade temporal e janela; quantidade desejada e origem da incerteza;
- H0/alternativa, direção e magnitude economicamente relevante quando justificável; exploração separada de confirmação;
- proposta padrão **bilateral, alfa de 5% e IC de 95%**, sujeita a João/orientador; não migrar para 10% ou unilateral após ver o resultado. IC marginal não se torna simultâneo por ajustar p-valores;
- família completa de contrastes/indicadores/janelas a testar; **Holm** como candidato simples para controlar erro familiar quando os p-valores individuais forem válidos; reportar todos, com p bruto/ajustado. Não repartir artificialmente famílias para facilitar rejeição. [Romano–Wolf 2005, pp. 94–97/105](https://www.econ.uzh.ch/dam/jcr:ffffffff-935a-b0d6-ffff-ffffd823d949/jasa.pdf);
- método principal e sensibilidades, regras de cobertura/lacunas, parâmetros, aproximações numéricas, versões, semente/replicações quando houver; n de unidades, datas e dependências efetivos;
- condições de não executar: componentes/perímetros incompatíveis, identidade necessária não sustentada, duplicação não resolvida, calendário insuficiente para o método escolhido, denominador instável sem tratamento justificável ou hipóteses temporais incompatíveis com a série. Registrar motivo; não substituir por um teste mais conveniente.

Relatar estimativa, unidade,IC quando defensável, estatística, graus de liberdade/referência de distribuição, p bruto/ajustado, cobertura e sensibilidades. Não rejeitar H0 não prova igualdade, equivalência, ausência de diferença relevante ou validade dos pressupostos. Equivalência exigiria margem e desenho próprios. Não apresentar IQR, intervalo mínimo–máximo de sensibilidades ou amplitude leave-one-out comoIC.

## Proposta de execução futura e entregáveis

1. **DiagnósticoA:** tabela por indicador×grupo×data de elegibilidade, motivos, sinais/componentes e qualificações, mais inventário auditável de extremos destacados. Abrange recortes escolhidos sem alterar o pacote aceito.
2. **RobustezB:** ficha de cada comparação principal com população dinâmica/comum, perdas de cobertura, influência unitária e distinção agregado/distribuição. Saídas exatas e apresentação separadas; resultados não autorizam mudança silenciosa do método.
3. **DecisãoC:** escolher entre encerrar emA+B ou aprovar um piloto inferencial delimitado. Se aprovado, executar apenas após contrato/ficha e validação técnica; depois avaliar ampliação, sem seleção pelo p-valor.

Essas etapas são uma proposta de trabalho, **não resultados executados**. A execução pode produzir tabelas de diagnóstico e sensibilidade para a task de interpretação; sua discussão econômica e a redação do capítulo ficam naquela frente. Não há recomendação de inferir causalidade, substituir dados ausentes, eliminar extremos, construir índice ou aplicar uma bateria de testes apenas para demonstrar rigor.

## Estado da pesquisa e limites

A evidência do artigo/base recebeu revisão independente antes da síntese; a pesquisa metodológica inclui fontes primárias e correções editoriais. Fontes, buscas, trechos/páginas examinados, falhas e verificação final constam da proveniência e daIssue 173. Revisão narrativa dirigida, sem pretensão de busca exaustiva ou de exigência curricular daUNICAMP. Disponibilidade estrutural não confirma que qualquer comparação específica passe nos critérios acima. A decisão acadêmica final permanece na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

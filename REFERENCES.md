# Referências da monografia

Biblioteca comentada para fundamentar conceitos, selecionar indicadores e planejar a análise. Organizada em 2026-10-13 na [Issue 109](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/109); contexto e decisões no [README](README.md) e na [nota metodológica](docs/engineering/institution-type-indicator-methodology-20261012.md).

**Esta lista não é a bibliografia final; o conjunto inicial adotado está na decisão humana vinculada à pesquisa111.** O [protocolo aprovado](docs/engineering/institution-type-indicator-methodology-20261012.md#protocolo-aprovado--2026-10-13) exige cinco dimensões: **rentabilidade, qualidade do crédito, capital/alavancagem, liquidez/financiamento e eficiência operacional**. Todas precisam de fundamentação sólida, com especial atenção a Assaf Neto e complementação pelas fontes mais adequadas a cada área. Uma fonte pode orientar uma pergunta sem justificar determinada fórmula, amostra ou estimador; seleção final sob direção de João/orientador na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

**Ordem de trabalho:** inventariar as segmentações e componentes reais da base antes de aprofundar a pesquisa/seleção de indicadores. Segmentação inclui porte, setor/atividade, modelos de negócio, controle e outros recortes viáveis, não apenas S1–S5; distinguir campos nativos de recortes derivados e atividade da instituição de setor dos tomadores. A literatura avaliará também a validade desses recortes. Essa foi a ordem preservada na consolidação da [Issue112](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/112). Após entrega do [inventário113](docs/engineering/ifdata-segmentation-inventory-20261013.md), a [pesquisa111](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/111) retomou em 14/10/2026: leitura substantiva e verificação independente das fontes concluídas; [síntese e25 fichas candidatas](docs/engineering/financial-dimensions-literature-20261014.md) com revisão própria e [coberturaC auditada](docs/engineering/financial-dimensions-literature-20261014.md#cobertura-dos-componentes-na-amostra-resultado-da-fatiac), usando handoff125aceito. A biblioteca não decide método; João adotou depois o conjunto inicial e a regra temporal, conforme [decisão3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6174707162).

## Como usar e atualizar

Cada entrada informa papel, localizador e limite. Estados de evidência:

- **Consulta atual:** conteúdo ou metadados primários examinados nesta organização; o alcance é declarado.
- **Evidência reaproveitada:** leitura/localizador documentado numa pesquisa existente, sem alegar nova conferência do corpo original.
- **Identificada no manuscrito:** referência presente no texto autoral consultado; conteúdo e dados bibliográficos ainda exigem conferência própria.
- **Candidata:** material a avaliar para uma lacuna; não significa adoção de método.

O manuscrito **Mono2 — versão revisada.docx**, com modificação no Drive em 12/10/2026, foi consultado em 13/10 como contexto autoral. **Word no Drive é o arquivo principal; João indica a versão vigente.** Cópias de consulta no checkout são privadas/ignoradas pelo Git, identificadas por origem, versão, data e SHA-256. Corpos e links privados do manuscrito e dos PDFs não são distribuídos neste repositório público. Não há sincronização automática nem edição do Word nesta entrega. Passagens que ainda prometem índice obrigatório ou descrevem a unidade anterior precisam de reconciliação futura com o protocolo.

O conector inicialmente não retornou texto de Assaf Neto. Depois do recebimento do exemplar privado, a folha de rosto e os dados editoriais foram conferidos visualmente; essa verificação bibliográfica não equivale à leitura dos capítulos. Em14/10, capítulos17–18 receberam leitura substantiva dirigida e verificação independente, delimitadas abaixo. Os estados distinguem leitura de conteúdo, confirmação de metadados e proposta de pesquisa.

## Fundamentos de análise e indicadores

### Assaf Neto — referência central de análise de balanços

ASSAF NETO, Alexandre. *Estrutura e análise de balanços: um enfoque econômico-financeiro*. 11. ed. São Paulo: Atlas, 2015. **Autor, título, edição, editora, local e ano confirmados visualmente no exemplar recebido**, páginas 4–5 do PDF (contagem do arquivo), conforme [registro de conferência bibliográfica](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6153092250).

**Uso:** eixo principal das cinco dimensões e interpretação conjunta de retorno, risco, funding e custos. **Localizadores efetivamente lidos:** cap17, pp.321–331/PDF342–352; cap18, pp.332–352/PDF353–373; adicionalmente cap3, pp.46–56/PDF67–77, e seção14.10, pp.275–279/PDF296–300;48 páginas substantivas verificadas independentemente. Liquidez p334, crédito/depósitos p335, capitalização p337, retornos/margens/custos pp341–342; comparação/contexto/qualidade informacional pp47/50/53–55 e mediana/quartis pp275–279. **Estado:** leitura visual dirigida do scan, semOCR; não leitura integral do livro. **Limites:** médias e ajustes dePL de p339 pertencem à taxa de reinvestimento; adaptações de médias/janelas nos candidatos continuam propostas. Percentuais históricos não são limites universais; inconsistências de exemplos foram registradas, sem reprodução automática. [Síntese](docs/engineering/financial-dimensions-literature-20261014.md) e [proveniência/localizadores](docs/engineering/financial-dimensions-literature-20261014.provenance.md). PDF integral privado, fora do Git público.

### FMI — conceitos, perímetros e indicadores de solidez

INTERNATIONAL MONETARY FUND. *Financial Soundness Indicators Compilation Guide*. Washington, DC: IMF, 2019. [Página oficial](https://www.imf.org/en/data/statistics/fsi-guide).

**Uso:** conceitos de solidez, agregação, bases de consolidação e contraprovas das definições. **Consulta substantiva14/10:** *Prepublication Draft 2019*, [exemplar distribuído pelo CEMLA](https://www.cemla.org/actividades/2019-final/2019-07-indicadores/2019-07-indicadores-1.pdf), no [curso coorganizado comFMI](https://www.cemla.org/actividades/2019/2019-07-indicators.html). §§6.3–6.6/6.22–6.30(perímetros),7.5(agregação),7.46–7.63(retorno/receitas/custos),7.29/7.34–7.42(NPL),12(distribuição); páginas efetivamente lidas na [proveniência](docs/engineering/financial-dimensions-literature-20261014.provenance.md). **Estado:** leitura dirigida e verificação independente do draft. **Limites:** acesso à edição final retornou403/429; não atribuir os localizadores do draft à final. §7.48 especifica média de AT/ROA; §7.52 não especifica literalmente média de PL/ROE. Gross income não éRIF bruta; provisões não sãoNPL; guia não certifica equivalência das contasIF.data nem fornece ranking pronto.

### Lima et al. — evidência brasileira sobre ratings bancários

LIMA, Fabiano Guasti; FONSECA, Camila Veneo Camargo; SILVEIRA, Rodrigo Lanna Franco da; ASSAF NETO, Alexandre. Os determinantes dos ratings de crédito dos bancos brasileiros. *Revista de Administração Contemporânea*, v.22, n.2, p.178–200, 2018. [DOI](https://doi.org/10.1590/1982-7849rac2018160373).

**Uso:** contraponto empírico brasileiro para retorno, liquidez e qualidade dos ativos. **Leitura14/10:** metodologia pp.187–192, tabela4p.190 e resultados pp.194–196 no [PDF original](https://www.scielo.br/j/rac/a/ZPMKdbB7pSn3hBB7Rs8XkYL/?format=pdf&lang=pt), com verificação independente. **Limites:**12 bancos comrating/2006–2015; seleção e coeficientes não se transportam à amostra2024. INADIM do artigo usa provisão/crédito, não atraso observado; nenhuma exclusão de extremos ou peso foi adotado. [Análise e proveniência](docs/engineering/financial-dimensions-literature-20261014.provenance.md).

### Tecles e Tabak — fronteiras e heterogeneidade bancária

TECLES, Patricia; TABAK, Benjamin M. *Determinants of Bank Efficiency: The Case of Brazil*. BCB,Working Paper210,2010. [OriginalBCB](https://www.bcb.gov.br/content/publicacoes/WorkingPaperSeries/wps210.pdf). **Leitura14/10:** impressas11–20, métodos/resultados/conclusão; verificação independente.156 bancos/1.517 observações semestrais2000–2007, fronteira estocástica bayesiana. Definições de produtos, porte e depósitos alteram a comparação. **Uso:** fundamentar cautela por modelo de negócio. **Limite:** razão custo/receita não éSFA/DEA; não transferir benchmarks, transformações de prejuízo ou vantagem estimada porcontrole.

### Souza et al. — indicadores e atividade de fomento

SOUZA, Juliana Ribeiro; OLIVEIRA, Joice Garcia de; BARBOSA NETO, João Estevão; PINHEIRO, Juliano Lima. Eficiência e rentabilidade das agências financeiras de fomento. *RAP*,55(4),969–994,2021. [DOI](https://doi.org/10.1590/0034-761220200111); [PDF original](https://www.scielo.br/j/rap/a/6jxpJsqNWrGD6wwtBVMQHfd/?format=pdf&lang=pt). **Leitura14/10:** pp.978–981/988–990; quadro2p.979 conferido visualmente e independentemente.14 agências/88 observações anuais2012–2018. **Uso:** comparar definição deIEO/IE/retorno da carteira. **Limites:**IEO eIE não são recíprocos; PECLD exige contrato estoque/fluxo/sinal. Não transportar quartis, cortes ou amostra de fomento para o projeto; não justifica inclusão de agências no recorteCVM/B3.

## Fontes oficiais, contabilidade e perímetros

| Referência e acesso | Papel na pesquisa / localizador | Limite e estado |
|---|---|---|
| BCB. [IF.data: esclarecimentos e metodologia](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf), sem data editorial demonstrada. | Leitura integral14/10 das2 páginas:perímetros/disponibilidade. | Fonte reutilizada autenticada e verificada. Notas não são códigosAPI; definição corrente não certifica vínculo ou versão histórica de cada unidade. |
| CMN. [Resolução 4.966, de 25 nov.2021](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=4966). | Regime de instrumentos financeiros e fronteira 2025; [ponte normativa existente](docs/engineering/financial-2025-normative-bridge-20261004.md). | Objeto e vigência consultados no [comunicado BCB](https://www.bcb.gov.br/detalhenoticia/17574/nota); ponte normativa reaproveitada. Consultar versão/dispositivos e vigência para cada uso; não construir equivalência automática entre classificações antigas e novas. |
| CPC. [CPC 36 (R3): Demonstrações Consolidadas](https://www.cpc.org.br/CPC/Documentos-Emitidos/Pronunciamentos/Pronunciamento?Id=67&lang=pt). | Apêndice A e itens sobre controle: distinguir consolidado societário de perímetros BCB. | Página oficial/versões consultadas. Não aplicar R3 retroativamente a toda a janela; conferir regra vigente e demonstrações de cada caso. |
| BCB. [Relatório de Economia Bancária 2023](https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb2023p.pdf). Brasília: BCB, 2024. | Contexto bancário/modelos de pagamentos; ROE, p.49, nota24, documentado nas pesquisas existentes. | Evidência reaproveitada. Indicador BCB com ajustes/médias próprios não é reproduzido automaticamente com PL pontual trimestral. |
| BCB. [Relatório de Estabilidade Financeira, abr.2025](https://www.bcb.gov.br/content/publicacoes/ref/202504/RELESTAB202504-refPub.pdf), v.24, n.1. | Contexto macrofinanceiro e conceitos/metodologias de capital; localizadores específicos nas pesquisas de componentes. | Leitura dirigida14/10, pp.100–104, verificada independentemente: LTD, capital, IL/ILE. Não reproduzir esses indicadores por nomes de contas; IL30 diasúteis difere do LCR30 diascalendários. Não aplicar regras atuais como limites históricos universais. |
| CVM. [Cadastro de companhias abertas](https://dados.cvm.gov.br/dataset/cia_aberta-cad) e [Formulário de Referência](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre). | Identidade, estrutura societária e vigência; apoio à relação entre emissor e unidade financeira. | Evidência reaproveitada da [pesquisa de amostra](docs/engineering/sample-comparability-research-20261008.md); cadastro corrente não prova trajetória histórica. Fundação técnica na #108; fechamento da amostra e vínculos na #125, com aceite próprio. |
| B3. [Empresas listadas](https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/acoes/consultas/empresas-listadas.htm). | Contexto de instrumentos/listagem; fontes históricas e limites na pesquisa de amostra e #108. | Referência de acesso, não universo histórico certificado. Registro CVM, listagem e ocorrência de negócios são fatos diferentes. |

**Eficiência e custo de provisão — complemento14/10:** BCB, REF setembro2016(pp.40–41,nota44), abril2024(pp.33–34,nota52) e **novembro2024**(pp.37–38,nota56 e gráfico1.2.3.6/nota1; arquivo na pasta202410). Leitura dirigida e verificação independente. Administrativas doREF incluem pessoal; resultado operacional IF.data não é denominador homologado por nome. Q2 tem referênciaBCB direta, mas conta/sinal/média continuam a conciliar. [AlternativasE2-A/B/C](docs/engineering/financial-dimensions-literature-20261014.md#eficiência-três-alternativas-concretas-para-e2) e [URLs/versões/proveniência](docs/engineering/financial-dimensions-literature-20261014.provenance.md#suplemento-focal-e2q2-bcb2016-e2024). Após a pesquisa, João adotou E2-B e Q2 com limitações; não houve cálculo ou reprodução oficial certificada nesta entrega.

Normas de capital, crédito e liquidez efetivamente lidas em 14/10: Resoluções3.490/2007,4.193/2013,2.682/1999(compilaçãov2P),4.401/2015,4.616/2017 e Circular3.360/2007; BCBSLCR2013 eNSFR2014. [URLs, versões, artigos/páginas e hashes](docs/engineering/financial-dimensions-literature-20261014.provenance.md#guias-e-normas-versões-e-localizadores). Originais e compilações antigas não são cronologia completa para folga regulatória2010–2024.

## Métodos estatísticos e eventual índice: candidatos

### OCDE/JRC — construção de indicadores compostos

OECD; EUROPEAN UNION; EUROPEAN COMMISSION, JOINT RESEARCH CENTRE. *Handbook on Constructing Composite Indicators: Methodology and User Guide*. Paris: OECD Publishing, 2008. [Página oficial e DOI](https://www.oecd.org/en/publications/handbook-on-constructing-composite-indicators-methodology-and-user-guide_9789264043466-en.html).

**Uso candidato:** organizar escolhas de quadro teórico, seleção de variáveis, dados ausentes, normalização, ponderação/agregação e robustez. **Localizador:** [PDF oficial](https://www.oecd.org/content/dam/oecd/en/publications/reports/2008/08/handbook-on-constructing-composite-indicators-methodology-and-user-guide_g1gh9301/9789264043466-en.pdf), Parte 1, §§1.1–1.2 (pp.22–23), §1.6 (pp.33–34) e §1.7 (pp.34–35), páginas impressas; leitura dirigida, sem revisão integral. **Limite:** o manual discute principalmente índices entre países e não fornece pesos ou uma função de risco bancário para esta monografia; nenhuma alternativa foi adotada. **Estado:** candidata, página editorial primária consultada e leitura dirigida do manual nesta organização.

### Wooldridge — dados em painel

WOOLDRIDGE, Jeffrey M. *Econometric Analysis of Cross Section and Panel Data*. 2. ed. Cambridge, MA: MIT Press, 2010. [Página da editora](https://mitpress.mit.edu/9780262232586/econometric-analysis-of-cross-section-and-panel-data/).

**Uso candidato:** avaliar hipóteses de modelos em painel caso a pergunta empírica exija estimação. **Localizador:** capítulos/estimadores ainda não selecionados nem lidos nesta entrega. **Limite:** painel, regressão ou efeitos fixos não garantem identificação causal; escolher método depende da pergunta, estrutura dos dados e hipóteses. **Estado:** candidata, metadados editoriais consultados; não é bibliografia metodológica já adotada.

### Lacunas a resolver antes de calcular ou classificar

| Decisão | Evidência necessária | Ponto de partida |
|---|---|---|
| Segmentações e componentes antes da pesquisa | Campos/valores, significado, cobertura histórica, nulos, perspectiva; recortes nativos versus derivados e ligação com componentes. | Cadastro, catálogo e bases existentes; conferência de duas referências não é inventário completo nem cobertura da população. |
| Indicadores nas cinco dimensões obrigatórias | Conceito, direção econômica, componentes e adequação às atividades; dimensão obrigatória não torna toda métrica aplicável. | [Pesquisa111:25 candidatos](docs/engineering/financial-dimensions-literature-20261014.md), Assaf central e complementos verificados; revisãoB e adoção ainda pendentes, sem impor métricas a toda atividade. |
| Disponibilidade conjunta | Componentes na mesma unidade, janela, regime e referência; cobertura por instituição e motivos de ausência. | Catálogo e dados locais autenticados; presença no catálogo não demonstra cobertura conjunta. |
| Comparação temporal e entre unidades | Estoques/médias, duração dos fluxos, eventos, mudanças de perímetro e 2025. | Pesquisa de comparabilidade e ponte normativa. |
| Estatística descritiva | Distribuições, extremos, denominadores problemáticos, ausências e composição da amostra. | Desenho a delimitar; não excluir/imputar observações por conveniência. |
| Índice comparativo | Significado medido, normalização, pesos, compensação entre dimensões e informações redundantes. | OCDE/JRC como candidato; índice não equivale a rating oficial ou probabilidade de inadimplência. |
| Robustez e interpretação | Sensibilidade a escolhas/amostra e confronto com evidências independentes. | Plano próprio após escolha dos indicadores; não inferir causalidade de correlações. |

## Outras referências identificadas no manuscrito

Estas entradas preservam a bibliografia autoral e sua função proposta. **Estado comum: identificadas no manuscrito; textos e metadados não foram todos conferidos nesta entrega.** Os usos abaixo são rotas de leitura, não afirmação de que cada obra valida nossos indicadores.

| Referência conforme manuscrito | Papel proposto / limite |
|---|---|
| SCHUMPETER, Joseph A. *Teoria do desenvolvimento econômico*. Tradução Maria Sílvia Possas. São Paulo: Nova Cultural, 1997. | Crédito e desenvolvimento; contexto teórico, sem fórmula bancária ou identificação causal automaticamente derivada. |
| STIGLITZ, Joseph E.; WEISS, Andrew. Credit rationing in markets with imperfect information. *American Economic Review*, v.71, n.3, p.393–410, 1981. | Informação, seleção e incentivos no crédito; orientar hipóteses, não usar juros altos como sinal unívoco de bom desempenho. |
| LEVINE, Ross. Financial development and economic growth: views and agenda. *Journal of Economic Literature*, v.35, n.2, p.688–726, 1997. | Funções da intermediação; distinguir desempenho institucional de desenvolvimento financeiro agregado. |
| MINSKY, Hyman P. *The Financial Instability Hypothesis*. Levy Economics Institute, Working Paper74, 1992. [Acesso institucional](https://www.levyinstitute.org/pubs/wp74.pdf). | Fragilidade e financiamento; não converter categorias teóricas em classificação empírica sem definição operacional. |
| LAPAVITSAS, Costas. Theorizing financialization. *Work, Employment & Society*, v.25, n.4, p.611–626, 2011. | Financeirização como contexto interpretativo; lucro bancário não mede sozinho contribuição social ou alocativa. |
| MATOS, Orlando Carneiro de. *Desenvolvimento do sistema financeiro e crescimento econômico no Brasil: evidências de causalidade*. BCB, Trabalhos para Discussão49, 2002. [BCB](https://www.bcb.gov.br/pec/wps/port/wps49.pdf). | Evidência agregada; conferir definição de causalidade e evitar transferir resultados diretamente para bancos individuais. |
| ROCHA, Bruno de Paula; SOUZA, Igor Viveiros de. Novas evidências de causalidade entre sistema financeiro e crescimento econômico no Brasil usando séries de tempo no domínio da frequência. *Nova Economia*, v.28, n.1, p.273–295, 2018. [DOI](https://doi.org/10.1590/0103-6351/2718). | Interação macrofinanceira por horizonte; não identifica automaticamente causas de diferenças entre instituições. |
| PAULA, Luiz Fernando de; OREIRO, José Luis; BASILIO, Flavio A. C. Estrutura do setor bancário e o ciclo recente de expansão do crédito: o papel dos bancos públicos federais. *Nova Economia*, v.23, n.3, p.473–520, 2013. [DOI](https://doi.org/10.1590/S0103-63512013000300001). | Estrutura e papel dos bancos públicos; examinar objetivo/modelo de negócio nas comparações. |
| SILVA, Tarcio Lopes da; JORGE NETO, Paulo de Melo. Economia de escala e eficiência nos bancos brasileiros após o Plano Real. *Estudos Econômicos*, v.32, n.4, p.577–619, 2002. [Periódico](https://revistas.usp.br/ee/article/download/215512/197635/645078). | Eficiência e escala; método de fronteira não se confunde com razão contábil ou ranking simples. |
| GOUVEA, Marcus Freitas. Fintechs: respostas regulatórias brasileiras. *Revista da Procuradoria-Geral do Banco Central*, v.14, n.2, p.33–48, 2020. [Periódico](https://revistapgbc.bcb.gov.br/revista/article/download/1075/55/1157). | Contexto regulatório; conferir atividade e regime aplicável em cada data. |
| TOLENTINO, Morgana; CATALDO, Bruna. Resultados preliminares do Open Finance Brasil: uma análise descritiva do perfil de acesso ao ecossistema. *Revista Estudos Institucionais*, v.9, n.2, p.320–342, 2023. [DOI](https://doi.org/10.21783/rei.v9i2.765). | Contexto de transformação/concorrência; resultados descritivos não provam efeito sobre lucro ou risco dos grupos. |
| BCB. [Sistema Financeiro Nacional](https://www.bcb.gov.br/estabilidadefinanceira/sfn); [bancos e caixas econômicas](https://www.bcb.gov.br/estabilidadefinanceira/bancoscaixaseconomicas); [bancos de investimento](https://www.bcb.gov.br/pre/composicao/bi.asp). Sem data. | Contexto institucional; consultar versões e não classificar atividade histórica apenas pela descrição corrente. |
| BCB. *Estatísticas monetárias e de crédito*, nota de 27 set.2024. [Documento oficial](https://www.bcb.gov.br/content/estatisticas/hist_estatisticasmonetariascredito/202409_Texto_de_estatisticas_monetarias_e_de_credito.pdf). | Contexto agregado da introdução, localizador p.2 conforme manuscrito; conferir corpo antes de reutilizar números. |

## Evidência já produzida no projeto

- [Pesquisa profunda, mecanismos e fichas nas cinco dimensões](docs/engineering/financial-dimensions-literature-20261014.md), com [proveniência, versões e fontes](docs/engineering/financial-dimensions-literature-20261014.provenance.md): fontes e sínteseB verificadas, coberturaC revisada; propostas para seleção, sem indicadores acadêmicos calculados.
- [Componentes, fórmulas candidatas e lacunas](docs/engineering/academic-indicators-components-20261004.md): distingue propostas, definições literais e janelas ainda a comprovar.
- [Aplicabilidade por atividade e decisão parcial](docs/engineering/institution-type-indicator-methodology-20261012.md): fundamenta o desenho sem adotar uma classificação universal.
- [Amostra e comparabilidade](docs/engineering/sample-comparability-research-20261008.md): alternativas temporais, desconhecidos e vieses possíveis.
- [Piloto exploratório](docs/engineering/ifdata-indicator-pilot-20261011.md): execução técnica não equivale à escolha dos indicadores da monografia.
- [Catálogo temporal](docs/engineering/ifdata-variable-catalog-20261011.md): apoio à investigação de componentes, sem certificar equivalências.

Ao usar uma referência numa fórmula ou interpretação, registrar trecho/página, edição/versão, alcance e limites na nota responsável. Atualizar o estado de consulta após leitura efetiva; não inventar páginas, citações ou adoção.

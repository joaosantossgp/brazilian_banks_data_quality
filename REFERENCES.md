# Referências da monografia

Biblioteca comentada para fundamentar conceitos, selecionar indicadores e planejar a análise. Organizada em 2026-10-13 na [Issue 109](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/109); contexto e decisões no [README](README.md) e na [nota metodológica](docs/engineering/institution-type-indicator-methodology-20261012.md).

**Esta lista não é uma metodologia adotada nem a bibliografia final da monografia.** Uma fonte pode orientar uma pergunta sem justificar determinada fórmula, amostra ou estimador. A seleção final permanece sob direção de João/orientador na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

## Como usar e atualizar

Cada entrada informa papel, localizador e limite. Estados de evidência:

- **Consulta atual:** conteúdo ou metadados primários examinados nesta organização; o alcance é declarado.
- **Evidência reaproveitada:** leitura/localizador documentado numa pesquisa existente, sem alegar nova conferência do corpo original.
- **Identificada no manuscrito:** referência presente no texto autoral consultado; conteúdo e dados bibliográficos ainda exigem conferência própria.
- **Candidata:** material a avaliar para uma lacuna; não significa adoção de método.

O manuscrito **Mono2 — versão revisada** foi consultado por conector de leitura em 2026-10-13 como contexto autoral. Ele e os PDFs de apoio permanecem no Drive privado de João; seus corpos e links privados não são distribuídos neste repositório público. O arquivo de Assaf Neto foi localizado, mas o conector não retornou seu texto. A bibliografia abaixo distingue essa limitação de uma leitura efetiva. Não há sincronização automática com o manuscrito: mudanças de objetivo/metodologia exigem reconciliação explícita.

## Fundamentos de análise e indicadores

### Assaf Neto — referência central de análise de balanços

ASSAF NETO, Alexandre. *Estrutura e análise de balanços: um enfoque econômico-financeiro*. 11. ed. São Paulo: Atlas, 2015. **Edição/ano conforme manuscrito; ainda não confrontados com a folha de rosto do exemplar.**

**Uso:** referência central indicada por João para interpretação econômico-financeira, financiamento, aplicações, risco e leitura conjunta de indicadores. **Localizador:** capítulos/páginas do exemplar ainda não verificados. **Limite:** não atribuir fórmula, citação ou recomendação específica ao livro sem ler o trecho; não transferir diretamente indicadores de empresas não financeiras para bancos. **Estado:** identificada no manuscrito; exemplar localizado, conteúdo não extraído. A [página do Instituto Assaf](https://www.institutoassaf.com.br/product/estrutura-e-analise-de-balancos/) foi consultada e identifica uma parte dedicada a bancos, mas não confirma a edição de 2015 nem suas páginas.

### FMI — conceitos, perímetros e indicadores de solidez

INTERNATIONAL MONETARY FUND. *Financial Soundness Indicators Compilation Guide*. Washington, DC: IMF, 2019. [Página oficial](https://www.imf.org/en/data/statistics/fsi-guide).

**Uso:** definições, bases de consolidação, componentes de indicadores e metadados para interpretação. **Localizadores:** capítulo 6, §§6.30–6.34, agregação/consolidação, consultados no conteúdo oficial indexado; capítulo 7, §§7.46–7.55, pp.90–91 impressas, para retornos sobre ativos/capital, conforme [pesquisa de componentes](docs/engineering/academic-indicators-components-20261004.md). **Limite:** guia de solidez financeira não é método pronto de ranking de companhias abertas; seus conceitos não certificam equivalência automática com rubricas IF.data. **Estado:** consulta atual ao material oficial de consolidação; rentabilidade com evidência reaproveitada. O capítulo 7 não foi integralmente revalidado nesta entrega.

### Lima et al. — evidência brasileira sobre ratings bancários

LIMA, Fabiano Guasti; FONSECA, Camila Veneo Camargo; SILVEIRA, Rodrigo Lanna Franco da; ASSAF NETO, Alexandre. Os determinantes dos ratings de crédito dos bancos brasileiros. *Revista de Administração Contemporânea*, v.22, n.2, p.178–200, 2018. [DOI](https://doi.org/10.1590/1982-7849rac2018160373).

**Uso:** avaliar dimensões candidatas de desempenho, liquidez e qualidade dos ativos. **Localizador:** metodologia e tabela 4, pp.187–190; resultados/limites pp.193–197, conforme [pesquisa por atividade](docs/engineering/institution-type-indicator-methodology-20261012.md). **Limite:** estudo de ratings numa amostra/período específicos; coeficientes não são pesos transferíveis para nosso índice. A proxy provisão/crédito não é taxa observada de atraso. **Estado:** metodologia/contexto relidos no [artigo original](https://www.scielo.br/j/rac/a/ZPMKdbB7pSn3hBB7Rs8XkYL/?lang=pt); fórmulas/tabela 4 com evidência reaproveitada, sem nova extração integral da imagem da tabela.

## Fontes oficiais, contabilidade e perímetros

| Referência e acesso | Papel na pesquisa / localizador | Limite e estado |
|---|---|---|
| BCB. [IF.data: esclarecimentos e metodologia](https://www3.bcb.gov.br/ifdata/index.html). Página dinâmica; consultada em 13 out.2026. | Formas de consolidação; tabelas de disponibilidade contábil, capital e crédito; periodicidade e atualizações. | Consulta atual ao conteúdo oficial indexado; abertura direta pode retornar apenas a interface dinâmica. Definição vigente não certifica todas as versões históricas, nem a cobertura de uma companhia. |
| CMN. [Resolução 4.966, de 25 nov.2021](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolu%C3%A7%C3%A3o%20CMN&numero=4966). | Regime de instrumentos financeiros e fronteira 2025; [ponte normativa existente](docs/engineering/financial-2025-normative-bridge-20261004.md). | Objeto e vigência consultados no [comunicado BCB](https://www.bcb.gov.br/detalhenoticia/17574/nota); ponte normativa reaproveitada. Consultar versão/dispositivos e vigência para cada uso; não construir equivalência automática entre classificações antigas e novas. |
| CPC. [CPC 36 (R3): Demonstrações Consolidadas](https://www.cpc.org.br/CPC/Documentos-Emitidos/Pronunciamentos/Pronunciamento?Id=67&lang=pt). | Apêndice A e itens sobre controle: distinguir consolidado societário de perímetros BCB. | Página oficial/versões consultadas. Não aplicar R3 retroativamente a toda a janela; conferir regra vigente e demonstrações de cada caso. |
| BCB. [Relatório de Economia Bancária 2023](https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb2023p.pdf). Brasília: BCB, 2024. | Contexto bancário/modelos de pagamentos; ROE, p.49, nota24, documentado nas pesquisas existentes. | Evidência reaproveitada. Indicador BCB com ajustes/médias próprios não é reproduzido automaticamente com PL pontual trimestral. |
| BCB. [Relatório de Estabilidade Financeira, abr.2025](https://www.bcb.gov.br/content/publicacoes/ref/202504/RELESTAB202504-refPub.pdf), v.24, n.1. | Contexto macrofinanceiro e conceitos/metodologias de capital; localizadores específicos nas pesquisas de componentes. | Evidência reaproveitada. Distinguir contexto do sistema de explicação causal de uma instituição; não aplicar regras atuais como limites históricos universais. |
| CVM. [Cadastro de companhias abertas](https://dados.cvm.gov.br/dataset/cia_aberta-cad) e [Formulário de Referência](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre). | Identidade, estrutura societária e vigência; apoio à relação entre emissor e unidade financeira. | Evidência reaproveitada da [pesquisa de amostra](docs/engineering/sample-comparability-research-20261008.md); cadastro corrente não prova trajetória histórica. Implementação e aceite de vínculos pertencem à #108. |
| B3. [Empresas listadas](https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/acoes/consultas/empresas-listadas.htm). | Contexto de instrumentos/listagem; fontes históricas e limites na pesquisa de amostra e #108. | Referência de acesso, não universo histórico certificado. Registro CVM, listagem e ocorrência de negócios são fatos diferentes. |

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
| Indicadores comuns e condicionais | Conceito, direção econômica, componentes e adequação às atividades do conglomerado/independente. | Assaf Neto, FMI, Lima e pesquisa por atividade; aprofundar lacunas sem impor indicadores bancários a todo modelo. |
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

- [Componentes, fórmulas candidatas e lacunas](docs/engineering/academic-indicators-components-20261004.md): distingue propostas, definições literais e janelas ainda a comprovar.
- [Aplicabilidade por atividade e decisão parcial](docs/engineering/institution-type-indicator-methodology-20261012.md): fundamenta o desenho sem adotar uma classificação universal.
- [Amostra e comparabilidade](docs/engineering/sample-comparability-research-20261008.md): alternativas temporais, desconhecidos e vieses possíveis.
- [Piloto exploratório](docs/engineering/ifdata-indicator-pilot-20261011.md): execução técnica não equivale à escolha dos indicadores da monografia.
- [Catálogo temporal](docs/engineering/ifdata-variable-catalog-20261011.md): apoio à investigação de componentes, sem certificar equivalências.

Ao usar uma referência numa fórmula ou interpretação, registrar trecho/página, edição/versão, alcance e limites na nota responsável. Atualizar o estado de consulta após leitura efetiva; não inventar páginas, citações ou adoção.

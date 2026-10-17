# Glossário da pesquisa

Conceitos para ler a monografia e interpretar seus dados. Os nomes técnicos da fonte permanecem literais nos arquivos; aqui usamos português e distinguimos conceitos que não devem ser confundidos. Fórmulas e decisões ficam nas [pesquisas](docs/engineering/institution-type-indicator-methodology-20261012.md); fontes teóricas e normativas, em [REFERENCES](REFERENCES.md).

## Companhias, unidades e atividades

**Companhia aberta / emissor:** pessoa jurídica com registro de emissor na CVM, segundo a categoria e a situação aplicáveis à data. O registro, sozinho, não comprova que suas ações estavam listadas na B3 naquele momento.

**Listagem e negociação:** listagem é a condição de admissão do instrumento no mercado; negociação é a ocorrência de operações. Uma ação sem negócios em determinada data não é, por isso, uma ação com listagem cancelada.

**Holding:** sociedade que detém participações em outras sociedades. Seu patrimônio e resultado individuais não descrevem necessariamente, linha a linha, os negócios de suas investidas.

**Instituição individual:** entidade apresentada separadamente no IF.data, em nível não consolidado. Exemplo: o banco operacional de um grupo é uma instituição; o conglomerado não é outra pessoa jurídica equivalente a ele.

**Instituição independente:** instituição que não integra conglomerado na perspectiva considerada. A condição é relativa ao perímetro e à referência; não significa companhia independente de qualquer controlador.

**Conglomerado financeiro:** conjunto consolidado apresentado na perspectiva financeira do IF.data, com escopo próprio definido pelo BCB. O nome não significa todas as atividades que, no uso comum, chamamos de financeiras.

**Conglomerado prudencial:** conjunto consolidado para fins prudenciais e contábeis segundo as regras aplicáveis, que pode incluir entidades fora do perímetro financeiro. Não é sinônimo de holding, nem uma visão limitada a índices de capital.

**Consolidado societário:** demonstração da controladora e de suas controladas segundo as regras contábeis aplicáveis. Seu perímetro não é automaticamente igual ao financeiro ou ao prudencial do IF.data.

**Perímetro:** conjunto de entidades e operações representado por uma medida. Dois indicadores com o mesmo nome podem descrever conjuntos distintos quando seus perímetros diferem.

**Vínculo temporal:** relação entre entidades sustentada por evidência referente a uma data ou intervalo. Controle, participação em conglomerado e identidade jurídica são relações diferentes; uma fonte corrente não prova todo o passado.

**Unidade analítica:** entidade ou conjunto representado por cada observação, identificado por perspectiva, referência e perímetro. O desenho corrente compara o sistema observado IF.data, unidades vinculadas às companhias selecionadas, restante e vínculos desconhecidos. Companhia e unidade não são contagens equivalentes; várias companhias podem remeter à mesma unidade. A [lista aprovada de 55 companhias](docs/engineering/cvm-open-financial-universe-2024-20261016.md) é documental e não recalcula os resultados dos contratos anteriores.

**Ocorrência de reporte (reporting occurrence):** representação de uma unidade numa perspectiva e referência específicas da fonte. Mesmo nome em duas datas não comprova identidade ou perímetro estável.

**Atividade / modelo de negócio:** operações e fontes de receita, financiamento e risco que caracterizam a unidade. Um conglomerado pode reunir atividades distintas; segmento regulatório e atividade econômica não são classificações intercambiáveis.

**População técnica e amostra acadêmica:** população técnica é o conjunto representado nos dados disponíveis; amostra acadêmica é o recorte escolhido para responder à pesquisa. O sistema observado inteiro é o universo da pesquisa de indicadores; o recorte das companhias permite comparação, sem limitar a avaliação de cobertura às associadas. Estar no IF.data não comprova registro CVM ou vínculo com uma companhia; registro CVM não exige negociação em bolsa no corte aprovado.

**Tcb e SegmentoTb:** campos observados que ajudam a identificar tipo institucional e modelo de negócio. Não são equivalentes nem definem sozinhos uma fórmula aplicável. As famílias econômicas usadas na pesquisa são agrupamentos interpretativos, sem de-para histórico automático. [Inventário e categorias](docs/engineering/ifdata-segmentation-inventory-20261013.md).

**Tc e Td:** Tc estratifica o tipo de controle; Td distingue conglomerado e instituição no cadastro correspondente. Td=I não prova independência societária. Controle não identifica causalidade, e consolidação exige numerador/denominador no mesmo perímetro, sem dupla contagem de conglomerado e membros.

**Sr e SrAnalitico:** Sr original informa enquadramento prudencial observado, com S1–S5 e ausências; não é simples faixa de tamanho. SrAnalitico é derivado, com origem/conflitos preservados e recorte separado do original. Ausência de Sr não prova inaplicabilidade; C3/C4 exigem componentes, unidade, regra e data próprios. [Quadros e limites por recorte](docs/engineering/financial-indicators-formulas-20261017.md).

## Demonstrações, medidas e interpretação

**IF.data:** plataforma do BCB que divulga dados selecionados de entidades supervisionadas, em relatórios e perspectivas próprios. Seus conceitos e cobertura são documentados na [metodologia oficial](https://www3.bcb.gov.br/ifdata/index.html).

**Cosif:** padrão contábil das instituições reguladas pelo BCB, conforme a versão e regras aplicáveis. A mudança de regime em 2025 exige examinar conceitos e mensuração, além de códigos e nomes.

**Resumo, Ativo, Passivo e DRE:** relatórios do IF.data que organizam medidas sintéticas, posições patrimoniais e resultados. A presença da mesma medida em dois relatórios não autoriza somá-la duas vezes.

**Estoque:** posição medida numa data, como ativo ou patrimônio líquido. Não é um montante acumulado durante todo o trimestre.

**Fluxo:** montante apurado durante uma janela, como receita, despesa ou lucro. A data de publicação não determina, sozinha, a duração desse fluxo.

**Janela de apuração (reporting window):** intervalo coberto por um fluxo ou cálculo. Lucros semestrais e trimestrais não se tornam comparáveis apenas por terem referência em dezembro ou março.

**Indicador candidato, adotado e implementado:** candidato é uma medida proposta com fundamentos e condições; adotado é aquele escolhido explicitamente; implementado é o cálculo entregue em código/contrato próprios. A [pesquisa143](docs/engineering/financial-indicators-activity-review-20261016.md) distingue dez métricas atuais e sete complementos prioritários ainda candidatos. Implementação não certifica adequação universal a todos os negócios; existir num piloto ou diagrama não significa adoção.

**Aplicabilidade:** pertinência de um indicador à pergunta, atividade e unidade medidas. Crédito/depósitos, por exemplo, exige examinar o papel de depósitos no financiamento da unidade.

**Disponibilidade:** existência dos componentes necessários numa fonte e recorte determinados. Componentes disponíveis não asseguram uma observação calculável nem interpretação válida.

**Consolidação contábil:** apresentação de entidades como um conjunto, com os ajustes e eliminações exigidos pelo perímetro. Não equivale a somar balanços ou tirar a média dos indicadores individuais.

**Índice composto:** síntese de várias medidas segundo uma regra explícita de normalização, ponderação e agregação. Sua construção é uma escolha metodológica distinta da consolidação contábil.

**Associação e efeito causal:** associação descreve covariação observada; efeito causal exige uma estratégia de identificação que sustente a interpretação. Uma regressão ou precedência temporal, isoladamente, não resolve essa distinção.

## Tempo, versões e comparabilidade

**Referência trimestral:** data-base identificada pela fonte. É distinta da data de coleta e pode coexistir com diferentes janelas de resultados.

**Versão da fonte (source vintage):** geração ou revisão do material recuperado. Arquivos coletados em instantes diferentes não comprovam uma única versão conjunta da publicação.

**Revisão da fonte:** nova versão de material anteriormente publicado, preservada ao lado da anterior. Diferença nos bytes não demonstra, por si só, mudança econômica.

**Conjunto de publicações recuperadas:** fontes usadas conjuntamente para interpretar uma referência, perspectiva e relatório. Sua reunião não presume que tenham sido publicadas ou revisadas simultaneamente.

**Associação variável–relatório (report variable binding):** relação entre uma posição no relatório e sua definição, identificadores, unidade e janela. Código ou nome igual em estruturas distintas não certifica equivalência conceitual.

**Quebra de comparabilidade:** mudança de conceito, mensuração, composição, perímetro ou janela que altera o significado de uma comparação. Uma série sem lacunas pode conter quebras.

**Recorte analítico (analytical cut):** seleção documentada de referências, unidades, perspectivas e versões para uma pergunta. A seleção não modifica as observações oficiais originais.

## Ausências, cobertura e proveniência

**Ausência estrutural:** variável ausente da estrutura observada de um relatório/período. Difere de uma célula existente cujo valor não foi informado.

**Célula não observada:** combinação unidade–variável para a qual não retornou observação numa estrutura observada. Não é automaticamente NA, NI ou zero.

**NA / NI:** tokens da fonte preservados como estados distintos. Seu significado deve ser conferido nas notas do relatório e da versão correspondentes; não expandir as siglas por suposição.

**Nulo, vazio e zero:** nulo é um estado sem valor; vazio é conteúdo textual sem caracteres; zero é um valor numérico. A representação literal e as notas da fonte determinam o tratamento.

**Desconhecido:** questão não resolvida pela evidência disponível. Vínculo desconhecido não é vínculo inexistente; classificação desconhecida não é motivo silencioso de exclusão.

**Disponibilidade anunciada:** período ou relatório listado pela fonte. Não comprova aquisição bem-sucedida, dados completos ou elegibilidade histórica.

**Cobertura cadastral observada:** correspondência entre os identificadores dos valores e do cadastro efetivamente recuperados na mesma referência. Não comprova a identidade de um emissor ou a completude do universo histórico.

**Resposta bruta:** corpo retornado pela fonte, preservado sem alteração, inclusive em falhas. Erro de requisição não significa população zero.

**Proveniência:** evidência da origem e transformação de uma observação, incluindo fonte, contexto, datas e integridade. Permite distinguir o dado oficial de uma seleção ou interpretação da pesquisa.

**Reprodução / replay:** reexecução delimitada a partir de entradas identificadas e preservadas, para conferir resultados. Não equivale a adquirir novamente a fonte ou sobrescrever uma saída aceita.

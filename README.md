# Dados bancários para a monografia

Este projeto apoia a monografia de Ciências Econômicas de João Victor Santos Gonçalves Pereira, na UNICAMP, sobre a evolução do **desempenho econômico-financeiro dos negócios financeiros vinculados a companhias abertas**. A pesquisa pretende comparar instituições, investigar possíveis explicações para suas diferenças e avaliar a construção de um índice comparativo.

O núcleo acadêmico é **2010–2024**. **2025–2026** é complemento separado, condicionado às mudanças contábeis, de perímetro e de disponibilidade. A infraestrutura guarda observações nativas e sua proveniência; a seleção da amostra, dos indicadores e do método precisa de decisões próprias.

## Como a pesquisa se organiza

![Mapa da pesquisa: CVM/B3 identifica companhias e elegibilidade; IF.data fornece valores e contexto; vínculos temporais permitem selecionar conglomerados financeiros e instituições independentes; literatura e disponibilidade orientam indicadores e análise, com perímetros separados.](docs/agents/assets/monograph-research-map-20261013.svg)

[Versão PNG](docs/agents/assets/monograph-research-map-20261013.png).

**Como ler:** CVM/B3 ajuda a responder **quem pertence ao universo de interesse**. IF.data informa **o que foi reportado e por qual unidade/perímetro**. Os vínculos históricos conectam essas duas perguntas. Só então um indicador pode ser avaliado pelo seu significado e pela disponibilidade dos componentes.

**Alternativa textual:** companhias e instrumentos elegíveis + dados IF.data → vínculo temporal documentado → unidade financeira identificada → indicadores candidatos e componentes compatíveis → comparação e interpretação. Esse percurso é o desenho da pesquisa; não certifica que todos os vínculos ou cálculos já estão concluídos.

## O que será medido

A decisão parcial de **13/10/2026** inclui **conglomerados financeiros e instituições independentes** vinculados às companhias elegíveis CVM/B3, mantendo explícito o tipo da unidade. A medição será direta nesse nível; decompor todas as subsidiárias e combinar seus indicadores não é uma obrigação.

| Perspectiva | Papel no desenho | Cuidado principal |
|---|---|---|
| Financeira | Unidades principais: conglomerados e independentes vinculados às companhias de interesse. | O perímetro do IF.data não é automaticamente toda a holding ou todas as atividades chamadas de financeiras. |
| Prudencial | Considerar indicadores e comparações pertinentes, especialmente capital e solidez; também oferece balanço e DRE. | Identificar perímetro, referência e regime próprios; não transportar índices para a unidade financeira como se fossem equivalentes. |
| Individual | Recurso para perguntas específicas sobre uma entidade. | Não somar às observações consolidadas ou exigir uma segunda amostra completa por rotina. |

Um indicador precisa ser **teoricamente pertinente e empiricamente viável**. A seleção procurará candidatos comuns e condicionais à atividade, com adaptações justificadas quando necessárias. Fórmulas, pesos, critérios temporais finais e composição do índice permanecem em aberto. [Decisão e fundamentos](docs/engineering/institution-type-indicator-methodology-20261012.md) · [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

<a id="guia-de-leitura-atual--2026-10-12"></a>

## Por onde começar

| Quero… | Leia |
|---|---|
| Entender os conceitos e diferenças entre unidades | [Glossário](GLOSSARY.md). |
| Conhecer a fundamentação e as lacunas metodológicas | [Referências comentadas](REFERENCES.md). |
| Consultar dados, componentes ou o piloto | [Guia de consultas locais](docs/engineering/local-queries-20261013.md). |
| Entender módulos, tabelas e relações | [Mapa técnico e dicionário físico](docs/engineering/repository-review-20261012.md). |
| Contribuir como agente | [AGENTS](AGENTS.md), depois a Issue real e seus contratos. |
| Acompanhar execução e decisões | [Mapa das frentes — Issue 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2), com atualizações datadas. |

## O que já existe — posição documental em 13/10/2026

A base técnica descrita nas entregas [84](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/84), [85](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/85) e [87](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/87) reúne valores, cadastro e catálogo temporal. Os registros dessas entregas informam **18.228.826 observações nativas**; financeiro/individual cobrem 66 referências de 201003 a 202606. Capital e segmentação têm janelas próprias. Isso descreve a base técnica, não a amostra final nem séries harmonizadas da monografia.

![Arquitetura técnica: arquivos de origem sustentam valores, cadastro temporal, catálogo de variáveis e piloto, mantendo os contratos históricos separados.](docs/agents/assets/repository-architecture-20261012.png)

[SVG do mapa técnico](docs/agents/assets/repository-architecture-20261012.svg). **Alternativa textual:** fontes preservadas alimentam leitores e conjuntos consultáveis; cadastro identifica ocorrências por data; catálogo registra definições/cobertura; piloto explora indicadores com regras explícitas. Consulte o [relatório técnico](docs/engineering/repository-review-20261012.md) para relações e limites observados.

O piloto contém oito candidatos e variantes de cálculo, com motivos de indisponibilidade; é uma ferramenta exploratória, não a seleção acadêmica final. O [ledger do piloto](docs/engineering/ifdata-indicator-pilot-20261011.md) explica métodos, regimes e limites.

**O clone não contém a base local.** Dados e artefatos aceitos são ignorados pelo Git. A [Release IF.data de 12/10/2026](https://github.com/joaosantossgp/brazilian_banks_data_quality/releases/tag/snapshot-ifdata-20261012) tem transporte criptografado e instruções de restauração próprias; não substitui o código nem o handoff de outras frentes.

## Frentes e decisões

A [Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108) trata da relação histórica CVM–B3–IF.data e sua cobertura. A [Issue 109](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/109) organiza esta documentação em frente isolada. Estado de execução/aceite é conferido nas Issues, sem transformar este README num diário operacional.

As decisões restantes estão na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3): elegibilidade e amostra históricas, periodicidade/janelas, fórmulas e eventual índice. Desconhecido não significa inelegível; presença de dados não certifica comparabilidade. A documentação pode evoluir sob direção de João, preservando decisões, fontes e limites.

## Consultar a base IF.data

[Valores e consultas nativas](docs/engineering/local-queries-20261013.md#consultar-a-base-ifdata). As pastas operacionais `financial`, `individual`, `capital` e `segmentation` têm tipos/contextos próprios; identificadores da rota OData não devem ser confundidos com os do portal histórico.

## Catálogo temporal de variáveis

[Definições, cobertura e exemplos](docs/engineering/local-queries-20261013.md#catálogo-temporal-de-variáveis). Estabilidade de nome/código não certifica equivalência econômica.

## Cadastro temporal e vínculos

[Consultas e auditoria cadastral](docs/engineering/local-queries-20261013.md#cadastro-temporal-e-vínculos). Correspondência por código/data não comprova, sozinha, identidade com companhia aberta.

## Piloto de indicadores consultável

[Resultados, componentes e limites](docs/engineering/local-queries-20261013.md#piloto-de-indicadores-consultável).

## Comandos locais verificados

[Comandos preservados e contexto de execução](docs/engineering/local-queries-20261013.md#comandos-locais-verificados). A reorganização documental conferiu sua preservação; não reexecutou consultas/replays sobre dados locais.

<a id="L70"></a>
<a id="L76"></a>

## Contratos e histórico

[Arquitetura e destinos](docs/architecture.md) · [Workflow](docs/agents/workflow.md) · [Tracker](docs/agents/issue-tracker.md) · [Modelo lógico](docs/superpowers/specs/2026-10-04-logical-data-model-design.md) · [Histórico operacional](docs/agents/operational-history-20261013.md).

Referências antigas às linhas deste README encontram seu contexto na [versão anterior preservada no Git](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/f93d37f17898d69713d06f07bb393eb1f2444331/README.md).

A licença própria do código/documentação ainda não foi escolhida; notices e licenças upstream conservam seu alcance. Fontes privadas, dados locais e credenciais não são publicação automática.

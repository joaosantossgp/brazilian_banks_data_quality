# Companhias abertas: identidade CVM–IF.data e metodologia por tipo

Registro iniciado em **2026-10-12**, [Issue 99](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/99). Responsável: Root. Base de preparação `dcf3202`; branch `codex/cvm-methodology-plan-20261012`, em worktree isolada. Documento específico da frente, com planejamento, fontes, notas de leitura, decisões e lacunas. **Entrega inicial de planejamento e pesquisa documental; não representa levantamento exaustivo, base CVM adquirida, vínculos aceitos ou metodologia acadêmica aprovada.**

## Direção autorizada por João

Em 2026-10-12, João definiu bancos e outras instituições cobertas pelo IF.data como universo principal desta frente. Demais instituições financeiras abertas são complemento opcional se não exigirem muito trabalho/tempo adicional. Pediu referências com apoio das skills Feynman e documentação metodológica específica, pois a monografia depende delas.

A janela acadêmica principal permanece 2010–2024; 2025–2026 é complemento separado. A prioridade de cobertura não resolve unidade individual/consolidada, tratamento das holdings, definição de capital aberto, regras de entradas/saídas ou método de comparação. Essas escolhas continuam na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3), com João/orientador. Não excluir uma companhia por falta de vínculo, nem declarar elegibilidade com registro atual.

Esta nota é a entrada desta frente; reutiliza os contratos e não cria tracker, glossário ou metodologia concorrentes:

- [Dossiê de identidade](capital-aberto-identity-dossier.md): casos BB, Bradesco e Itaú; vínculos antigos não resolvidos.
- [Pesquisa de amostra e comparabilidade](sample-comparability-research-20261008.md): alternativas temporais, unidade, seleção e rupturas.
- [Pesquisa de componentes/indicadores](academic-indicators-components-20261004.md): candidatos, fórmulas propostas e limitações.
- [Piloto exploratório](ifdata-indicator-pilot-20261011.md): implementação exploratória em perspectivas próprias; não define amostra acadêmica.
- [Cadastro temporal IF.data](ifdata-cadastro-20261011.md) e [arquitetura](../architecture.md): entradas nativas e destinos existentes.

## Perguntas que a frente precisa responder

1. Quais emissores satisfazem o critério escolhido de companhia aberta em cada referência de 2010–2024?
2. Qual pessoa jurídica ou conglomerado IF.data representa cada emissor, com qual relação comprovada e em qual intervalo?
3. Qual atividade/tipo institucional a unidade representa naquele período, inclusive em grupos diversificados?
4. Quais indicadores são economicamente interpretáveis e contabilmente comparáveis em cada grupo?
5. Quais lacunas impedem inclusão, cálculo ou comparação, sem confundir desconhecido, não aplicável, ausência e zero?

## Alternativas e recomendação de trabalho

| Alternativa | Benefício | Limitação/decisão |
|---|---|---|
| Cadastro atual CVM e correspondência simples | Descoberta rápida de candidatos | Não reconstrói elegibilidade histórica nem comprova controle/perímetro; insuficiente para a pergunta temporal |
| Identificação histórica CVM + ligação documentada IF.data + método por tipo | Reutiliza a base principal e explicita validade, ausências e comparabilidade | Recomendada para pesquisa; aquisição e implementação terão contratos próprios |
| Todo o setor financeiro com fontes adicionais | Maior alcance potencial | Pode exigir dados, regimes e metodologias próprios; não colocar no caminho crítico |

Para o complemento fora do IF.data, fazer apenas uma avaliação documental curta: fontes oficiais estruturadas, cobertura 2010–2024 anunciada/observada, regras contábeis, identidade, reaproveitamento técnico e esforço incremental estimado por atividade. Não prometer prazo sem esse diagnóstico. Adiar se exigir pipeline próprio, coleta manual extensa, nova harmonização ou atrasar o núcleo. Registrar candidato, ganho, custo, lacuna e recomendação; adoção acadêmica ou mudança do contrato de fontes financeiras vai a João. A permissão condicional não é autorização para coletar todas as fontes.

## Trilha A — cadastro histórico e vínculos

### Fontes e função

Cadastro CVM serve como ponto de partida e conferência atual. FCA é candidato para informações cadastrais/valores mobiliários históricos; FRE para atividades, participações e eventos societários. B3 entra se o critério exigir listagem/negociação de ações. Identificar o emissor, o instrumento e o registro/listagem são perguntas distintas. As fontes documentais C1–C5 abaixo foram consultadas; os ZIPs não foram adquiridos/inspecionados nesta entrega.

A disponibilidade anual de FCA/FRE desde 2010 não demonstra painel completo de intervalos. Distinguir referência, entrega, reapresentação, vigência do evento e recuperação. Mudanças do FRE em 2016/2023 exigem inventário de esquemas, sem normalização silenciosa.

### Modelo proposto para a ligação

| Objeto lógico proposto | Conteúdo mínimo | Condição de aceitação futura |
|---|---|---|
| Emissor e observação cadastral | Código CVM textual, CNPJ completo textual, denominação, situação/categoria recebidas, documento/versão e datas | Preservar valor original e fonte; eventos não viram intervalos por suposição |
| Ocorrência IF.data | Código/namespace nativo, referência, perspectiva, atributos de consolidação e vínculo cadastral | Reusar cadastro autenticado; não completar código para CNPJ de 14 dígitos |
| Evidência de relação | Duas pontas, `same_legal_entity`, `controls` ou `member_of_conglomerate`, vigência, localizador e estado | Fonte primária datada conforme contrato de identidade; sem equivalência por nome/raiz de CNPJ |
| Evento e decisão de elegibilidade | Entrada/saída, reorganização, regra aplicada, período, justificativa e versão da regra | Regra acadêmica aprovada e evidência; resultado desconhecido permanece explícito |

São objetos de desenho, sem tabelas novas implementadas. Documentos de apoio precisam de URL/parâmetros, recuperação UTC, status/diagnóstico, corpo/hash e localizador; o desenho de aquisição deve definir armazenamento e autenticação. Nome/ticker ajudam a buscar, não aceitam vínculo. Fonte atual não confirma passado. Não inventar início/fim de controle por interpolação entre documentos.

Um emissor pode ligar-se a várias entidades; uma entidade pode pertencer a grupos em períodos distintos. Antes de qualquer join de valores, declarar cardinalidade e papel de cada relação, conferir duplicação e impedir soma repetida de controladas/conglomerado. Holding, banco operacional e consolidado permanecem separados; vínculo jurídico não certifica equivalência econômica. Registrar eventos sem colar séries de antecessor/sucessor automaticamente.

Primeira prova proposta: **BB, Bradesco e Itaú Holding/banco operacional**, reaproveitando o dossiê. Deve produzir evidência aceita ou lacuna explícita em referências delimitadas, sem extrapolar o resultado para toda a janela/amostra. A seleção das datas será parte do contrato de aquisição/prova.

## Trilha B — classificação e documentação metodológica

Separar **tipo jurídico/regulatório**, **atividade/modelo de negócio** e **perímetro de divulgação**; não usar segmento prudencial, nome ou ticker como substituto dos três. Classificação histórica exige fonte/validade e pode mudar. Conglomerado diversificado pode demandar grupo próprio, em vez de herdar o tipo da instituição líder. A correspondência entre categorias FMI e brasileiras exige pesquisa; não é de-para já aprovado.

| Família proposta de investigação | Questões para selecionar indicadores | Limite atual |
|---|---|---|
| Bancos com crédito e captação de depósitos | Rentabilidade, qualidade do crédito, estrutura de financiamento, liquidez e capital | Conferir atividade, denominadores e perímetro por época |
| Instituições especializadas em crédito | Financiamento, concentração, risco de crédito e rentabilidade | Crédito/depósitos pode não representar seu financiamento; não trocar denominador sem justificativa |
| Corretoras/distribuidoras e serviços financeiros | Composição de receitas, custos, rentabilidade e riscos próprios | Razões bancárias de crédito podem não responder à atividade |
| Instituições de pagamento cobertas pela fonte | Modelo de receitas, recursos próprios e regime aplicável | Investigar cobertura histórica e comparabilidade; não presumir toda a janela |
| Holdings e conglomerados diversificados | Participações, resultado próprio e representatividade do perímetro operacional | Não confundir PL/lucro da holding com os do banco/conglomerado |

Essas famílias organizam a pesquisa; não são classificação observada ou método adotado. Seguradoras e demais instituições fora da cobertura principal ficam na avaliação opcional, sem puxar balanços CVM para o núcleo IF.data implicitamente.

### Ficha obrigatória de cada candidato

Registrar na pesquisa de indicadores existente, com referência nesta nota: pergunta econômica; conceito e fórmula; fonte original/localizador; adaptação brasileira; grupo aplicável e motivo; numerador/denominador e códigos/contextos; sinal/unidade/escala; janela de fluxo; data e média dos estoques; anualização; perspectiva/perímetro; regime/versão; disponibilidade conjunta por entidade/data; regras para zero/negativo e ausências; quebras; limitações de interpretação; alternativas/sensibilidades; decisão humana, data e versão.

Estados analíticos propostos: **comparável**, **comparável sob condições**, **não aplicável**, **evidência insuficiente**. Aplicabilidade metodológica e disponibilidade de dado são eixos distintos: um indicador aplicável pode ter dados ausentes; ausência de rubrica não prova não aplicabilidade. Não excluir extremos, imputar, winsorizar ou escolher estimador silenciosamente.

Alternativa para decisão futura: conjunto comum de candidatos apenas onde houver equivalência demonstrada, mais indicadores específicos por grupo. Comparações dentro de grupo e entre grupos responderão a perguntas diferentes. Planejar painel desbalanceado e subpainel comum como alternativas/sensibilidade, sem impor desenho ou alegar correção de viés. Reusar análise de seleção da pesquisa de amostra.

### Notas de leitura Feynman — fundamentos e limites

**M1, FMI 2019:** o sumário separa setores (cap. 2), contabilidade (4–5), consolidação (6), instituições captadoras de depósitos (7–8) e outras financeiras (9). O §2.17 fundamenta agrupamento por funções/comportamento; não fornece uma classificação pronta para o IF.data. No cap. 7, ROA prefere resultado antes dos tributos e ativo médio; a anualização deve constar dos metadados (§§7.47–7.48). ROE recomenda resultado após tributos e capital/reservas, com ressalva sobre alavancagem (§§7.51–7.55). No cap. 9, o guia trata outras financeiras e subsetores com escopos próprios (§§9.1–9.9), não prescrevendo o mesmo conjunto bancário para todos. Isso justifica investigar aplicabilidade; não valida fórmulas brasileiras nem impõe os FSIs macroprudenciais a uma análise de desempenho de companhias.

A leitura cruzou classificação, fórmulas e escopo setorial. As correspondências IF.data continuam propostas a conciliar na nota de componentes. Não recalcular indicadores nesta entrega. Para 2010–2024, conferir normas históricas e quebras identificadas; não aplicar consolidado regulatório atual retroativamente. Manter 2025 separado até evidência de comparabilidade própria.

## Fontes, proveniência e estado da consulta

Consulta documental web em **2026-10-12**; URLs primárias e localizadores abaixo. Data desta consulta não é vigência nem data do evento. Nesta fatia não foram arquivados corpos locais/headers/hashes: trata-se de leitura documental, sem autenticação de fonte para admissão de dados. Antes de aceitar evidência de identidade/valores, capturar e verificar esses elementos em destino autorizado. Esta tabela funciona como registro de proveniência da nota; não simula manifesto de aquisição.

| ID | Referência primária e localizador | O que foi conferido / limite |
|---|---|---|
| C1 | [CVM, Informação Cadastral](https://dados.cvm.gov.br/dataset/cia_aberta-cad), descrição e Informações Adicionais | Consulta nesta conversa: cadastro referente ao último dia útil, atualização diária. Não comprova trajetória histórica nem listagem de ações |
| C2 | [CVM, FCA](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca), descrição, lista dos arquivos, atualização e histórico | Consulta nesta conversa: conteúdo estruturado geral/valores mobiliários; reapresentações semanais; histórico anunciado desde 2010 |
| C3 | [CVM, índice FCA](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/), nomes anuais 2010–2024 | Consulta nesta conversa: arquivos anunciados para a janela. Sem inspeção de ZIP, completude, campos ou eventos |
| C4 | [CVM, FRE](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre), histórico do emissor, participações, reorganização e notas 2016/2023 | Nova consulta nesta fatia: funções documentais e mudanças de estrutura; índice de seção não comprova evento de companhia |
| C5 | [BCB, IF.data até 2024](https://www3.bcb.gov.br/ifdata/index2024.html) e [metodologia corrente](https://www3.bcb.gov.br/ifdata/index.html), formas de consolidação | Busca oficial na conversa anterior e evidência local do piloto reaproveitadas. Abertura direta até2024 nesta fatia falhou; não declarar nova leitura integral ou prova histórica por instituição |
| M1 | International Monetary Fund, Statistics Department. **Financial Soundness Indicators Compilation Guide**, 2019. [Página oficial](https://www.imf.org/en/data/statistics/fsi-guide), [PDF](https://www.imf.org/-/media/files/data/2019/2019-fsi-guide.pdf). DOI [10.5089/9781484396209.069](https://doi.org/10.5089/9781484396209.069) | Nova consulta: sumário; §2.17, p.10; §§7.46–7.55, pp.90–91; §§9.1–9.9, p.125. PDF: páginas 26, 106–107 e 141 (contagem a partir de 1). Guia setorial/macroprudencial, não certificação IF.data |

**Evidência local reaproveitada:** documentos vinculados no início, inspecionados de forma dirigida. Não reautenticados seus corpos primários ou manifests nesta fatia. A nota de componentes já contém referências acadêmicas e limitações de consulta; sua bibliografia não é automaticamente nova leitura aqui. Próxima pesquisa deve ampliar literatura original por atividade, buscando método/amostra/dados/resultados/limites e evitando usar apenas resumos para justificar fórmulas.

**Skills e mecanismo real:** Feynman `deep-research` e `pdf-explore` foram lidas por pedido explícito. `deep-research` remete a `/deepresearch`, indisponível nesta interface; não executado e nenhum runtime foi instalado. Alternativa admitida pelo workflow: busca/leitura primária com ferramenta web, cruzamento de seções do PDF e notas/localizadores nesta seção conforme `pdf-explore`. Proveniência integrada neste arquivo por organização canônica e pedido de documento específico, sem pasta `outputs/` paralela. Brainstorming organizou alternativas/escopo; requesting-code-review e verification-before-completion orientam revisão e encerramento. Não alegar revisão acadêmica/orientador ou levantamento sistemático exaustivo.

## Fatias propostas e condições de avanço

As fatias futuras abaixo são propostas, sem claim de execução pronta. Cada contrato deve registrar owner, base/head, inputs, allowlist/forbidden, recursos e revisão antes de ampliar. O arquivo atual é a fatia documental inicial; não autoriza coleta por desdobramento automático.

| Fatia | Resultado observável | Dependências e ownership/destinos propostos | Checks e condição de saída |
|---|---|---|---|
| A1 — contrato de fontes CVM | Inventário de recursos/esquemas/versões, cobertura e plano de aquisição delimitado | Pode preparar sem #3; pesquisador em nota própria `docs/engineering/`, destino exato aprovado na Issue antes de escrita | Fontes/localizadores e ausência de promessas de completude; revisão independente antes da aquisição |
| A2 — prova de identidade | BB/Bradesco/Itaú com pontas, datas, relações e evidência/lacunas | Depende A1 e autorização de aquisição/destinos; executor de dados em destinos novos `data/raw/`/`data/curated/`, paths exatos a contratar | Hashes, vigência, cardinalidade, não duplicação e revisão de domínio; unresolved não vira falso |
| B1 — referências por tipo | Matriz de aplicabilidade e fichas dos candidatos, lacunas e alternativas | Pesquisa pode acompanhar A1; pesquisador de método em nota de indicadores existente ou destino próprio explicitado; não disputar o dossiê de A2 | Ler métodos/fontes primárias; distinguir conceito, fórmula e adaptação; revisão independente antes de ampliar conclusões |
| D — escolhas acadêmicas | Decisão datada sobre população, unidade/holding, classificação e método | João/orientador na #3, com insumos A/B suficientes; cada escolha libera só seus dependentes | Registro fiel, consequências e lacunas; sem aprovação presumida |
| E — base e análise | Cadastro/vínculos aplicados e indicadores por tipo em recorte aprovado | Depende contratos de aquisição/implementação, dados admitidos e escolhas aplicáveis; pacote/scripts/testes existentes, allowlist futura finita | Testes causais de identidade/tempo/cardinalidade/cálculos + conferência econômica/contábil/financeira + revisão por fatia e composição final |

O primeiro recorte recomendado para a próxima sessão é **A1 + preparação bibliográfica B1**, aproveitando as entradas existentes, sem adquirir datasets. Isso prova um contrato viável de fontes e uma matriz de perguntas; não prova amostra final, vínculos de toda a janela ou indicadores comparáveis calculados. A2 deve começar pequeno e só expandir após aceite dos casos.

## Decisões, pendências e fronteira de paralelismo

| Registro | Estado e consequência |
|---|---|
| Prioridade IF.data; demais instituições condicionais | Autorizada por João em 2026-10-12; não substituir por levantamento universal |
| Documentação específica + referências Feynman | Solicitada por João; entregue inicialmente nesta nota, com mecanismo/limitação declarados |
| Capital aberto: registro, categoria, ações/listagem e intervalo | Decisão humana pendente na #3; preparar evidência sem selecionar amostra |
| Unidade, holdings, consolidado e duplicação | Pendentes; pesquisar relações sem substituir emissor pelo banco |
| Tipos e indicadores por época; médias/janelas e sensibilidades | Propostas a fundamentar/revisar; oito candidatos não limitam a pesquisa nem constituem método aprovado |
| Cobertura histórica efetiva FCA/FRE e eventos | Ainda não verificada nos arquivos; documentação/índices só anunciam disponibilidade |
| Extensão fora IF.data | Avaliação curta opcional; sem esforço/prazo medido ou incorporação aprovada |

Na conferência inicial, #91 (revisão da base) estava em execução com allowlist própria de relatório/visuais; esta nota não toca seus arquivos nem os controles compartilhados. #99 pode produzir esta documentação sem esperar #3. A1/B1 são trabalhos de pesquisa compatíveis pelo conteúdo, mas precisam de contratos próprios antes de claim `ready`. A2/E dependem das entradas/autorização/decisões indicadas, sem bloquear pesquisa independente. Atualizações da fronteira ficam no mapa existente #2; Project /3 continua com Zec. Estado remoto final deve ser conferido na Issue, não deduzido desta nota.

## Verificação e manutenção

Conferir links locais, inventário da allowlist e coerência entre fontes/afirmações/pendências; revisão independente em snapshot exato antes da publicação. Texto não exige suíte de software. Revisões posteriores desta frente atualizam esta nota com data, fonte/localizador, alteração, motivo, decisão e limites, referenciando evidência especializada sem duplicá-la. O pedido de documentação vale para esta frente; não foi gravado como alteração de memória global.

Histórico inicial: 2026-10-12 — direção de João registrada, contratos existentes reutilizados, fontes CVM/FMI consultadas e primeira rota proposta. Estado de revisão/publicação e hash do snapshot serão registrados na Issue 99; nenhuma aprovação final de método é declarada neste arquivo.

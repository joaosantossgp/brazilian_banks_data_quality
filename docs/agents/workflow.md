# Workflow obrigatório de Issues

Este guia operacionaliza o [contrato aprovado em 2026-10-03](../superpowers/specs/2026-10-03-issue-workflow-design.md), na frente da [Issue 17](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/17). Leia primeiro o [AGENTS](../../AGENTS.md), depois a Issue e somente os contratos pertinentes. O [tracker único](issue-tracker.md) define a autoridade das superfícies: Issue guarda tarefa, dependências e aceite; repositório guarda contratos e evidências; [Project /3](https://github.com/users/joaosantossgp/projects/3) acompanha as mesmas Issues e continua com Zec. Documento local não confirma estado remoto.

## Nome e labels

Título obrigatório: **`[Tipo] Verbo + resultado ou recorte`**. Descreva o resultado; estado, executor e skills ficam nos campos próprios.

| Prefixo | Label de tipo | Exemplo de título |
|---|---|---|
| `[Mapa]` | `kind:map` | `[Mapa] Planejar expansão 2010–2026` |
| `[Decisão]` | `kind:decision` | `[Decisão] Definir unidade e janela da monografia` |
| `[Pesquisa]` | `kind:research` | `[Pesquisa] Validar contrato financeiro 2024/2025` |
| `[Entrega]` | `kind:task` | `[Entrega] Converter inventário offline para Parquet` |
| `[Governança]` | `kind:governance` | `[Governança] Definir workflow obrigatório de Issues` |

Toda Issue aberta deve ter as quatro dimensões abaixo, coerentes com o título e o corpo:

| Dimensão | Cardinalidade | Catálogo obrigatório |
|---|---|---|
| Tipo | Exatamente uma | Os cinco `kind:*` da tabela acima |
| Responsabilidade | Exatamente uma principal | `role:research`, `role:implementation`, `role:review`, `role:integration` |
| Área | Uma ou mais | `area:research`, `area:domain`, `area:data`, `area:docs`, `area:infra`, `area:governance` |
| Estado operacional | Exatamente uma | `status:needs-triage`, `status:ready`, `status:blocked`, `status:in-progress`, `status:in-review`, `status:done` |

Labels são metadados, sem conceder acesso, ownership de arquivos ou autorização de publicação. A migração aplica-se às Issues abertas, preservando números, links, histórico e labels não substituídas. Entregas encerradas conservam seus títulos/labels históricos; `area:converter`, `area:contract-2025` e `area:academic-indicators` são classificações anteriores por frente. Categorias `bug`/`enhancement` e [estados de triagem Matt](triage-labels.md) são opcionais e distintos do estado operacional. `ready-for-agent` não prova prontidão. Não exigir priority, lane ou persona como quinta dimensão.

## Contrato obrigatório

A Issue deve permitir executar e conferir a tarefa sem reconstruir conversas. Tarefa pequena usa contrato curto e links precisos, sem nova spec por rotina.

1. **Problema e resultado:** tipo de trabalho, resultado observável e spec/plano aplicáveis.
2. **Áreas e domínio:** domínio concreto de cada área, conceitos e limites, com referências ao [glossário](../../GLOSSARY.md), [arquitetura](../architecture.md), [ADRs](../adr/) ou fontes pertinentes. Label isolada não satisfaz este campo.
3. **Workflow:** etapas ordenadas, entradas, saídas e condição de conclusão; explicitar quando uma etapa opcional é necessária.
4. **Skills por etapa:** família e identificador original, motivo, obrigatória ou condicional, gatilho, entregável e mecanismo realmente disponível. Selecionar apenas as pertinentes.
5. **Execução:** responsável identificável, perfil técnico, role principal, branch/base, allowlist de arquivos/destinos, exclusões e arquivos compartilhados com integrador definido. Declarar impacto na arquitetura (nenhum + motivo, ou inventário e justificativa de novos arquivos/pastas, movimentos/deletes) conforme os [destinos canônicos](../architecture.md#organização-dos-arquivos-e-pastas).
6. **Dependências e prontidão:** links dos blockers, entradas/decisões faltantes e condição de desbloqueio, ou declaração explícita de que não há pendências para começar. Separar requisitos externos das etapas internas de execução/revisão.
7. **Aceite e evidência:** critérios observáveis, checks pertinentes, revisão independente e conferência de domínio quando aplicável; registrar comandos/saídas, artefatos e links confirmados.
8. **Encerramento:** distinguir resultado local, revisão aprovada e publicação/integração confirmada. Pesquisa e decisão podem concluir com artefato ou decisão, sem PR de código.

## Entrada e prontidão

Antes de assumir trabalho, ler o estado atual da Issue, conferir contrato, dependências, recursos e destinos, registrar branch/base de revisão e evitar execução duplicada. Sem Issue publicada, declarar **“não publicada — tarefa local”** e apontar ao brief existente; não inventar número ou URL.

| Estado | Condição observável |
|---|---|
| `status:needs-triage` | Entrada ainda sem contrato completo; registrar o que falta para avaliar. |
| `status:ready` | Contrato completo, escopo aprovado, dependências satisfeitas e entradas/recursos disponíveis; nenhuma pendência impede começar. É confirmação positiva explícita. |
| `status:blocked` | Requisito concreto ausente; informar blocker, evidência faltante e condição de desbloqueio. |
| `status:in-progress` | Tarefa pronta assumida por executor identificável, com escopo conferido. |
| `status:in-review` | Resultado entregue; revisão independente e/ou checks ainda pendentes. |
| `status:done` | Aceite confirmado e evidência registrada, inclusive quando a Issue for encerrada. |

**Ausência de `status:blocked` não basta.** Issue sem domínio, workflow, skills ou estado confirmado não é presumida pronta. Checks e revisão que serão produzidos durante o trabalho são etapas futuras, sem constituir blockers prévios por si só. Uma Issue mapa organiza a rota e aponta para tarefas executáveis; não se torna implementação pronta por não listar blockers.

Dependências nativas e sub-issues são usadas quando disponíveis e verificadas; links no corpo são fallback explícito. Uma pendência deve bloquear somente o recorte que depende dela. Preparar alternativas metodológicas pode ser pesquisa pronta; decidir método continua com João/orientador.

## Áreas, domínio e seleção de skills

Áreas classificam competências e orientam skills. **Não são filas exclusivas nem limites de paralelismo.** Uma skill pode servir a várias áreas; uma Issue pode ter várias áreas. A tabela indica candidatas, sem exigir todas as skills da linha.

| Área | Domínio | Skills pertinentes conforme a tarefa |
|---|---|---|
| `area:research` | Evidência primária, bibliografia, proveniência e incertezas | Matt `research`; Feynman `deep-research`, `pdf-explore` |
| `area:domain` | Conceitos econômicos, contábeis e financeiros; unidades, janelas, perímetros e método | Matt `domain-modeling`, `grilling`, `grill-with-docs`; Feynman `pdf-explore` para prova em PDFs |
| `area:data` | Aquisição autorizada, inventários, normalização, persistência e integridade | Superpowers `brainstorming`, `writing-plans`, `test-driven-development`, `systematic-debugging`, execução e revisão; `diagram-design:diagram-design` para fluxos pertinentes |
| `area:docs` | Specs, planos, contratos e documentação rastreável | Matt `to-spec`, `to-tickets`, `domain-modeling`; Superpowers desenho/plano/revisão/verificação; `diagram-design:diagram-design` |
| `area:infra` | CI, ferramentas, dependências e ambiente do projeto | Superpowers desenho/plano/TDD/debug/revisão/verificação; Context7 para documentação técnica; `diagram-design:diagram-design` |
| `area:governance` | Entrada, decomposição, dependências, nomenclatura, responsabilidades e integração | Matt `triage`, `wayfinder`, `to-spec`, `to-tickets`; Superpowers planejamento/coordenação/revisão/verificação; `diagram-design:diagram-design` |

### Invocação e limites

O agente seleciona as skills pelo contrato antes de atuar; registra as instruções e procedimentos realmente usados, sem depender de lembretes para cada etapa. Os [nomes legíveis e identificadores](issue-tracker.md#nomes-legíveis-e-identificadores-das-skills) ajudam a localizar a skill. Ler sua instrução quando aplicável não prova registro de slash command, autodisparo ou execução de runtime.

- **Matt:** direção (`wayfinder`), pesquisa (`research`), exame de alternativas (`grilling`, `grill-with-docs`), domínio (`domain-modeling`), spec (`to-spec`), tickets (`to-tickets`) e triagem (`triage`). Preservar `disable-model-invocation: true` e `allow_implicit_invocation: false` onde existirem. Identificar solicitação e mecanismo explícito autorizado; aplicação de instruções sob direção do usuário não equivale a comando registrado. Setup e prototype dependem de necessidade concreta.
- **Superpowers:** usar desenho existente; `brainstorming` entra quando comportamento/arquitetura ainda precisam de definição. `writing-plans` organiza execução com múltiplas etapas; `executing-plans` ou `subagent-driven-development` executam conforme contrato. Código/correções usam `test-driven-development`; falhas usam `systematic-debugging`; conclusão usa `requesting-code-review`, `receiving-code-review` quando houver feedback e `verification-before-completion`.
- **Feynman:** somente `deep-research` e `pdf-explore` compõem a seleção atual. `pdf-explore` entra quando métodos, tabelas ou citações exigem cruzar PDFs/páginas com ferramentas disponíveis. Investigação extensa pode exigir `deep-research`, mas `/deepresearch` não foi validado neste Codex. Registrar disponibilidade ou alternativa de pesquisa com ferramentas verificadas e proveniência que satisfaça o contrato aprovado; não instalar runtime para presumir compatibilidade.
- **Context7:** para biblioteca, framework, SDK, API, CLI ou serviço, obter documentação atual via `resolve-library-id` e depois `query-docs`, por conceito e conforme a versão usada. Não é necessário para revisão de código, lógica de negócio ou edição textual sem consulta técnica. Indisponibilidade exige registrar a limitação e uma alternativa admitida, sem afirmar consulta feita.
- **`diagram-design:diagram-design`:** usar a instalação disponibilizada por João quando workflow, arquitetura ou dependências beneficiarem de visual. Entregar SVG ou imagem embutida em Markdown, com descrição textual, título/descrição acessíveis e inspeção renderizada de conteúdo, conectores, legibilidade e recortes. HTML temporário local pode servir de fonte, sem ser a única documentação visual pública.

Mecanismo obrigatório indisponível vira pendência ou alternativa expressamente admitida na Issue. Não simular invocação, copiar/reinstalar plugin nem modificar metadados upstream. Nenhuma skill amplia escopo, autoriza nova coleta ou altera permissões, credenciais e proteções.

## Workflow por natureza

| Natureza | Etapas e saídas |
|---|---|
| Mapa | Matt `wayfinder` quando explicitamente solicitado e disponível → rota, decisões e recortes → tarefas ligadas com dependências reais. O mapa acompanha a rota; tarefas assumidas têm seus próprios contratos. |
| Pesquisa | Matt `research` delimita pergunta/fontes → Feynman `pdf-explore` ou `deep-research` quando o gatilho e disponibilidade forem satisfeitos → nota com fontes/localizadores, proveniência e desconhecidos → revisão independente das conclusões → resultado na Issue. Questão metodológica passa à decisão humana correspondente. |
| Entrega de software ou dados | Ler desenho/spec/ADR → Matt `to-spec` se faltar síntese e `to-tickets` se precisar decompor → Superpowers `writing-plans` para múltiplas etapas → TDD e execução → diagnóstico se falhar → revisão independente e feedback → verificação → publicação/integração e CI pós-merge quando houver PR. Aquisição exige autorização própria. |
| Decisão metodológica | Matt `research` prepara evidência → `grilling`/`grill-with-docs` examinam alternativas quando necessário → João/orientador escolhe → `domain-modeling` registra conceito/ADR pertinente após aprovação → decisão datada libera ou mantém bloqueados os dependentes. |
| Governança ou documentação pequena | Ler contratos e usar desenho delimitado → alterar destinos autorizados → conferir links, coerência e escopo → revisão independente → verificação e integração aplicáveis. Não exigir TDD nem suíte integral para texto; código do checker exige regressões e checks de software. |

Os perfis descrevem responsabilidade, sem criar filas de área: `role:research` produz evidência; `role:implementation` executa a entrega; `role:review` lê e reporta independentemente; `role:integration` reúne alterações compartilhadas e confirma publicação/integração. O autor não revisa sua própria implementação como revisão independente.

## Paralelismo e handoff

Issues com `status:ready` confirmado podem avançar simultaneamente, **inclusive na mesma área**. Por exemplo, duas pesquisas `area:research` com entradas disponíveis e destinos distintos podem ser executadas em paralelo. Uma terceira pesquisa que dependa de fonte ausente fica bloqueada somente por essa dependência; a área comum não bloqueia as outras.

**Comunicação permanente solicitada por João em 2026-10-04:** cada entrega, handoff ou mudança de blocker confere o estado real das Issues e atualiza a fronteira no mapa existente da [Issue 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2). A atualização ao usuário informa títulos/links das tarefas que podem avançar juntas, recorte autorizado, dependências satisfeitas e ownership compatível; identifica as bloqueadas com requisito/condição de desbloqueio e a próxima fatia. No encerramento, distinguir execução concluída, revisão pendente e trabalho que ainda pode começar; não anunciar como pronta uma pesquisa só possível após triagem ou autorização. Não criar tracker concorrente nem operar o Project, que segue com Zec.

Preparar evidência ou alternativas pode ser independente da decisão que adotará o resultado. Conferir o aceite da Issue: uma proposta de indicadores com lacunas explícitas pode ser pesquisada enquanto João/orientador escolhem o método; cálculo e recorte acadêmico dependentes continuam bloqueados. Se a Issue mistura essas entregas, delimitar o recorte e seus critérios antes de confirmar prontidão, preservando o histórico e a autoridade humana. Não reduzir o aceite para encerrar artificialmente a tarefa.

Reservar apenas arquivos realmente compartilhados. Conflito concreto de escrita, recurso ou entrada exige dependência/handoff e altera a prontidão afetada; não inferir conflito pelo nome da área. Cada executor recebe allowlist limitada, excluídos dados, artefatos aceitos e arquivos alheios ao contrato. README, AGENTS, arquitetura, glossário, tracker e controles de CI/governança têm integrador único por lote. Checkouts/destinos isolados ficam neste repositório e computador autorizado, somente quando contemplados pelo contrato.

Handoff informa Issue, responsável, base/head, inventário completo de arquivos, origem/destino de renames e deletes, diff/patch, comandos/saídas, incertezas, revisão independente e integração necessária nos arquivos compartilhados. Coordenação privada não vai ao repositório; registros públicos usam Issue/frente/branch. Não enviar mensagens a outros chats sem autorização.

O revisor confere conformidade com os destinos/responsabilidades da arquitetura, além da allowlist. Atualizar o contrato estrutural no mesmo lote quando a estrutura aprovada mudar; nova raiz/camada fora do escopo exige decisão de João antes da escrita. Esse gate é documental e de revisão, sem enforcement automático de pastas instalado.

## Exemplos concretos de contrato

Estes exemplos orientam seleção, sem afirmar alteração de estado remoto ou execução histórica dessas skills.

| Referência | Domínio e workflow/skills | Dependência e aceite |
|---|---|---|
| [Planejamento de amostra e comparabilidade, Issue 16](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16) | `area:research` + `area:domain` + `area:data` + `area:docs`: elegibilidade/vínculos temporais, vieses, contas, unidades, janelas, perímetros e rupturas. Reusar pesquisas publicadas → alternativas e matriz de comparabilidade → revisão por fatia → plano de execução nas Issues existentes. | Pesquisa de alternativas tem contrato próprio; adoção de unidade/amostra/método depende de João/orientador na #3, indicadores permanecem na #14. Entregas nativas e nota normativa não certificam harmonização. Conferir a Issue real para fontes/lacunas, sem reabrir blockers históricos já resolvidos. |
| [Conversor offline, Issue 15](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/15) | `area:data`: tokens/Decimal, ausências, inventário, Parquet e proveniência. Ler spec/ADR → Superpowers plano quando necessário → TDD/execução → revisão independente → verificação → PR/CI/integração. | Requer inventário e destino autorizados; converter o piloto individual não depende da ponte 2025. Aceite verifica preservação e integridade. Issue encerrada permanece histórica. |
| [Decisão de unidade e janela, Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) | `area:domain`: população histórica, emissor/holding, unidade IF.data e período acadêmico. Matt `research` → `grilling` se necessário → escolha João/orientador → `domain-modeling` para registro aprovado. | A escolha humana pendente bloqueia implementação dependente. Aceite é decisão datada, referenciada, com consequências para os dependentes; preparar alternativas não decide o método. |

## Revisões e testes por fatias

Orientação de João em 2026-10-08, registrada na [Issue 17](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/17): detectar e corrigir erros durante a implementação, sem deixar a primeira revisão independente para o fim do trabalho. Aplica-se a entregas de código, dados e pesquisa; o tipo de verificação depende do resultado. João esclareceu que a PR pode ter o tamanho necessário: o requisito é revisão parcial da implementação, não tamanho ou quantidade de PRs.

Antes de escrever ou executar, o plano/Issue divide o trabalho em fatias que entreguem um resultado verificável. Para cada fatia, registrar resultado, entradas/dependências, owner, base/head ou snapshot imutável, allowlist/destinos, checks pertinentes, revisão independente e condição de saída. Usar as Issues existentes quando o contrato comportar o recorte; desdobramentos precisam de escopo explícito e atualização da #2, sem criar tarefas apenas para contar etapas.

1. Implementar uma fatia delimitada e executar os testes que verificam seu comportamento e os contratos afetados. Correção de bug pede regressão causal; pesquisa pede fontes/localizadores e conferência de domínio; documentação pede links/coerência/escopo, sem testes que apenas repetem texto.
2. Solicitar revisão independente dessa fatia **antes de ampliar a implementação**. O revisor compara resultado e diff com contrato/allowlist e arquitetura; em dados/pesquisa, verifica também conceitos, precisão, cobertura, janelas/perímetros e fontes conforme o aceite. Registrar revisor, revisão exata e achados na Issue/handoff.
3. Resolver achados materiais e falhas antes da próxima fatia. Preservar a tentativa original; diagnosticar a causa, corrigir e reexecutar os checks afetados. Não repetir a mesma suíte sem mudança, falha ou dúvida concreta que justifique a repetição. Passes de casos reexecutados isoladamente não transformam uma execução global falha em PASS.
4. Registrar checkpoint: resultado local/revisado/integrado, base/head ou hashes do snapshot, inventário completo, comandos/saídas, checks não executados, limitações e entrada entregue à próxima fatia. Se o head mudar, o registro anterior continua histórico e o delta exige avaliação; não transferir aprovação automaticamente.
5. A PR pode reunir quantas fatias forem necessárias ao escopo autorizado, com checkpoints revisados explícitos. Não exigir PR pequena, separação por fatia ou justificativa de tamanho/transição indivisível. Na expansão de dados, aceitar cada lote/janela antes de ampliar; não implementar pipeline ou criar PR por trimestre. Handoff de fontes, admissão/Parquet/query/replay e aceite são resultados distintos.

A revisão final confere a composição entre fatias, os deltas desde os checkpoints aprovados, conflitos, inventário/allowlist, preservação e **SHA final entregue**. Não substitui revisão precoce nem elimina regressões/CI/gates finais pertinentes ao conjunto. Suíte completa roda no marco de integração exigido pelo contrato ou por impacto transversal; novos erros/mudanças justificam nova execução. Gates do ambiente real (por exemplo Windows antes de coleta) conservam seu aceite próprio, mesmo com CI em outro sistema aprovada. Esta regra é documental; não instala enforcement, runner ou proteção.

## Revisão, integração e conclusão

Dentro do escopo aprovado, executar, revisar e integrar autonomamente após checks pertinentes e revisão independente aprovados. Chamar João quando houver mudança de escopo ou decisão metodológica; não repetir aprovação rotineira já concedida. Essa autonomia preserva requisitos de aquisição, fontes, permissões e decisões humanas ainda pendentes.

Revisão/checks identificam o head efetivamente entregue; resolver achados que impeçam aceite antes de integrar. Testes de software verificam comportamento/integridade. Conferência econômica, contábil e financeira verifica conceitos, componentes, unidades, janelas, perímetros, regimes, versões e fontes; uma não substitui a outra. Revisão de agente é técnica, sem alegar aprovação humana ou review elegível no GitHub.

Para entrega com PR, confirmar publicação, checks do head, revisão independente, integração autorizada e CI pós-merge. Pesquisa ou decisão sem PR conclui com seu artefato/decisão e aceite verificado. Registrar na mesma Issue resultado, evidência, limitações e dependências remanescentes; `status:done` exige esse aceite, sem encerrar perguntas metodológicas distintas. Project /3 segue com Zec.

O checker de paths permanece **observação offline**, sem validar campos da Issue. Conferência explícita de contrato/prontidão não equivale a enforcement remoto. Este workflow não cria parser universal, serviço de orquestração, required check, ruleset, proteção ou mecanismo de credenciais.

## Diagrama do workflow

Estilo: padrão claro de diagram-design, escolhido explicitamente por João em 2026-10-03. SVG usa fallback local quando a fonte da skill não estiver instalada; PNG conserva a renderização conferida.

![Workflow de Issues: contrato completo leva à conferência positiva de prontidão; requisitos pendentes bloqueiam apenas a tarefa afetada; Issues prontas podem executar em paralelo, inclusive na mesma área, e seguem para revisão, verificação e conclusão conforme o contrato.](assets/issue-workflow.svg)

[Versão PNG](assets/issue-workflow.png). O diagrama é ilustrativo; não comprova paralelismo executado sobre tarefas reais.

**Alternativa textual:** contrato → conferir dependências/entradas/escopo → `status:ready` explícito ou blocker com condição de resolução → assumir execução; duas Issues prontas da mesma área podem avançar simultaneamente → entregar resultado → revisão independente e checks → concluir com evidência, integrando e verificando CI pós-merge quando houver PR. Se método ou escopo exigirem decisão humana, registrá-la como pendência antes do trabalho dependente.

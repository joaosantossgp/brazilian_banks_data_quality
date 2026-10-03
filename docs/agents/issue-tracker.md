# Acompanhamento do trabalho

**Atualização de estado — 2026-10-03:** a fundação e o piloto do [PR 1](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1) foram integrados em main em 2026-10-02T18:37:51Z, no [merge 3234c20](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/3234c20); [CI pós-merge 37048733876](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37048733876) concluiu com sucesso. O instante exato é o registro da auditoria coordenada; as páginas públicas confirmam merge, data, commit e sucesso. Menções abaixo ao draft, ausência de merge ou confirmação pendente são histórico da preparação/publicação inicial, não o estado corrente. Isso não confirma publicação do novo conversor, sincronização atual do Project ou autorização para futuras integrações.

## Autoridade de cada superfície

- **Repositório:** código, contratos, arquitetura, glossário, decisões, specs/planos e evidências rastreáveis. Entradas comuns: [README](../../README.md), [AGENTS](../../AGENTS.md), [arquitetura](../architecture.md), [spec da fundação](../superpowers/specs/2026-10-02-governance-research-design.md) e [plano autorizado](../superpowers/plans/2026-10-02-governance-foundation-plan.md).
- **Issue real:** problema/objetivo, escopo/arquivos, dependências, critérios de aceite e links da evidência/revisão. Enquanto não publicada, declarar “não publicada — tarefa local” e apontar ao ticket/brief, sem inventar ID ou URL.
- **Project existente /3:** [Brazilian banks data quality](https://github.com/users/joaosantossgp/projects/3), privado, acompanha estado e links das mesmas tarefas/Issues. Não criar outro Project. Estado remoto requer leitura/verificação remota; documento local não prova atualização do board.

Na leitura de preparação em 2026-10-02, o remoto público tinha default main e nenhuma branch; o checkout ainda não tinha commits. Essa observação é datada, não uma afirmação permanente de remoto vazio. O Project privado não privatiza repo/Issues. A autorização explícita de publicação de 2026-10-02 permite completar/revisar a fundação, CI offline mínimo, commit/push do conjunto revisado, bootstrap mínimo de main, draft PR e reconciliação das mesmas Issues/cards no Project /3 por ferramenta suportada. Os gates anteriores de não publicar/não implementar CI são histórico datado e foram substituídos para esta entrega. Não autoriza merge, deploy, nova coleta, capítulo, calendário, runtime/contas/chaves, mudança de segurança/permissões/tokens/proteções ou outro Project. Publicação e CI foram confirmadas em 2026-10-02 pelos commits e runs abaixo; não há novo gate humano para o escopo já aprovado.

## Histórico da publicação inicial (superado para estado do PR pela atualização acima)

Fundação de governança: **publicada na branch, com PR em rascunho e CI verificado**, conforme [plano autorizado](../superpowers/plans/2026-10-02-governance-foundation-plan.md). Tasks 1–5 e revisão final concluídas; o plano contém objetivo, dependências, arquivos e aceite. Briefs/restrições complementares em `.superpowers/sdd/` são registros operacionais somente locais, excluídos da publicação. A publicação inicial não criou Issues. A tarefa real [Planejar expansão 2010–2026 e atualização](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) já foi verificada; a reconciliação dos demais rascunhos e vínculos pertence a outro trabalho coordenado, sem alteração de Project/Issues nesta correção documental. Relatórios de execução/revisão são evidência local; não representam aceite humano ou publicação por suposição.

Workflow autorizado: Issue → branch → draft PR → checks pertinentes → revisão; integração/merge não foi autorizado. O CI mínimo reutiliza testes offline existentes; sua execução remota passou no push e no PR exato, conforme os runs abaixo. Proteções de branches e segurança não serão alteradas. A [proposta concreta aprovada](../engineering/governance-publication-proposal.md) e o manifesto delimitam os arquivos/exclusões/audiência; o conjunto inicial e os commits foram confirmados no remoto; o manifesto conserva o snapshot auditado da publicação inicial, não os hashes de revisões documentais posteriores. A [pesquisa oficial de governança](../engineering/governance-source-research-20261002.md) fundamenta o desenho.

### Evidência remota verificada em 2026-10-02

- Bootstrap de quatro arquivos em main: [commit 2c0d5a7](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/2c0d5a766cc9ea197b37a0a062c5efb124bcbd02).
- Conjunto inicial de 119 arquivos / 808.531 bytes: [commit 00d6fe4](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/00d6fe46828955cfde9db4d2de1377c0fe20ff2b).
- [PR de publicação do piloto e da fundação](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1): aberto em rascunho, base main e head feat/ifdata-two-quarter-pilot; sem merge.
- [CI do push](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37044529701) e [CI do PR](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37044656911): sucesso no commit inicial. Python, budget e portal-ready passaram; estes runs não comprovam checks de commits posteriores.

Esses links registram a publicação e a verificação inicial, não o estado de todos os cards do Project. O status corrente de cada Issue/PR/check vem do GitHub; esta correção apenas fecha as referências documentais comprovadas, preservando os registros locais e o histórico.

## Rascunhos históricos e migração coordenada

O registro anterior descreveu seis cards Todo em draft no Project (escopo capital aberto, referências MIT, piloto, bruto, cobertura e CVM/B3). Isso é histórico, sem leitura remota atual nesta tarefa; não afirmar que seus estados continuam Todo. [Spec do piloto](../superpowers/specs/2026-10-01-ifdata-pilot-design.md), [plano histórico](../superpowers/plans/2026-10-01-ifdata-pilot.md) e [ledger](../engineering/pilot-execution.md) preservam decisões/evidência locais.

Quatro rascunhos da expansão vivem em `.scratch/ifdata-expansion/map.md` (mapa de preparação somente local, excluído da publicação), com tickets locais e dependências. `.scratch` é preparação transitória, não tracker remoto. O lote 202312 individual/Resumo **já foi executado**, conforme [ledger de expansão](../engineering/expansion-execution.md); descrições antigas de “próximo lote” são históricas. As decisões acadêmicas e os vínculos sem prova continuam abertos com João/orientador.

A reconciliação das mesmas tarefas foi autorizada em 2026-10-02 e exige ler os itens atuais do Project/Issues, conferir o conteúdo/evidência e registrar correspondência **item original → Issue real → item de acompanhamento**, incluindo os identificadores efetivamente retornados. Não prometer que conversão preserve IDs, duplicar tarefas ou sincronizar cegamente. Atualizar estado somente com evidência e respeitando dependências/aceite; conservar rastreabilidade e links históricos.

Wayfinder/to-spec/to-tickets organizam trabalho sob esse contrato; handlers research/prototype não ampliam a autorização de escopo. A política de pesquisa e redação assistida vigente é a spec, com [tooling e limitações](../engineering/research-tooling-20261002.md).

## Etapas, skills, entregáveis, gates e owners

Frente desta proposta: [Governança de workflow e escopo, Issue 17](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/17); acompanhamento pelo worker autorizado no Project existente.

Esta matriz organiza o contrato existente; não é outro tracker. Issue mantém objetivo/aceite/dependências, o Project existente acompanha a mesma Issue e o repositório guarda contratos/evidência. Uma role principal por Issue; passagem de etapa não significa fechamento automático.

| Etapa | Skill conforme necessidade e disponibilidade | Entregável | Gate observável | Owner principal |
|---|---|---|---|---|
| Entrada e direção | AGENTS + contrato; Mapear decisões — `/wayfinder` para direção ampla | Objetivo, limites e decisões no item existente | Frente/base/dependências e destino definidos | `role:research` ou responsável da tarefa |
| Fatos e conceitos | Pesquisar fontes — `/research`; Examinar decisões — `/grilling`; Examinar com documentação — `/grill-with-docs`; Modelar domínio — `/domain-modeling` se mudar | Nota com fontes primárias, versão/data/página e incertezas | Evidência sustenta afirmação; decisão acadêmica humana permanece explícita | `role:research` |
| Desenho e síntese | Desenhar a solução — `superpowers:brainstorming`; Definir especificação — `/to-spec` opcional | Spec única no destino existente | Revisão do desenho e autorização do escopo; nenhuma spec duplicada | Responsável da tarefa |
| Decomposição e plano | Decompor em tarefas — `/to-tickets`; Planejar execução — `superpowers:writing-plans` para múltiplas etapas | Tarefas ligadas, dependências e plano executável | Aceite e paths de cada owner delimitados | `role:implementation` ou `role:integration` |
| Execução | Executar com agentes — `superpowers:subagent-driven-development` ou Executar o plano — `superpowers:executing-plans`; Testar primeiro — `superpowers:test-driven-development` | Patch e fixtures/testes pertinentes | RED/GREEN observado e preservação fora da allowlist | `role:implementation` |
| Diagnóstico quando falhar | Diagnosticar falhas — `superpowers:systematic-debugging` | Causa, reprodução e correção mínima | Regressão e evidência da causa | Responsável pela correção |
| Revisão e verificação | Solicitar revisão — `superpowers:requesting-code-review`; Verificar conclusão — `superpowers:verification-before-completion` | Revisão independente e resultados frescos | Achados críticos/importantes resolvidos; software distinto de rigor econômico/contábil/financeiro | `role:review` |
| Handoff e integração | Contrato + verificação do diff/escopo; revisão exata da proposta | Base/head, diff completo e arquivos compartilhados integrados | Autorização aplicável, executor confiável e evidência remota antes de afirmar publicação | `role:integration` |

Feynman deep-research entra somente para investigação profunda com runtime/expansão verificados; pdf-explore quando a evidência exige cruzar páginas de PDF e ferramentas disponíveis. Context7 apoia documentação técnica conferida contra a versão usada. Setup/prototype são condicionais a necessidade concreta. Presença não prova invocação; `disable-model-invocation: true` exige caminho real de invocação, sem autofiring presumido. Nenhuma skill autoriza publicar por conta própria.

## Roles, áreas e ownership

Roles orientativas: `role:research`, `role:implementation`, `role:review`, `role:integration`. Áreas orientativas: `area:converter`, `area:contract-2025`, `area:academic-indicators`. Não expandir o catálogo para toda etapa; governança é integração. Labels não são ACL, ownership de filesystem ou autenticação de executor.

O contrato da tarefa contém responsável identificável, Issue/frente, branch/base, allowlist, forbidden, shared paths/integrador, dependências e evidência de conclusão. Scopes ativos não se sobrepõem; shared paths ficam reservados somente ao integrador daquele lote, com allowlist limitada. Um handoff aprovado muda a reserva na política da base antes do trabalho seguinte. Pesquisadores usam destino separado, sem escrita no checkout concorrente; destinos novos para contrato 2025/indicadores continuam propostos.

O diff real do conversor informa sua allowlist; mudanças nos quatro controles compartilhados não delegam edição de governança ao implementador. O integrador consolida essas mudanças preservando conteúdo do conversor. Um PR misto só passa sob contrato de integração previamente aprovado na base, cobrindo exatamente todos os paths; não somar labels para criar permissões. Revisão por agente é evidência técnica, não aprovação GitHub por pessoa elegível.

## Wayfinding operations

Usar o tracker existente: mapa de direção é uma Issue existente ou proposta para o worker responsável; tickets são as mesmas Issues ligadas, sem criar outro Project ou arquivos de status concorrentes. Consultar tarefas relacionadas conforme necessidade; não carregar todas as notas a cada sessão. Criar/publicar/atribuir/comentar/fechar Issues requer escopo autorizado e ferramenta verificada; workers de documentação produzem handoff para quem já gere Issues/Project.

Fronteira executável: tarefa aberta, responsável explícito e todas as dependências satisfeitas por evidência. Direção ampla usa wayfinder; uma tarefa já delimitada não exige mapa novo. Quando disponível e autorizado, usar relações nativas de dependência/sub-issue; caso contrário, preservar links explícitos no corpo, sem alegar relação nativa criada. Claim e handoff não derivam de uma label nem do documento local. Não executar efeitos upstream de skills contra a autorização da sessão.

## Estados e evidência

`proposta/local` → `pronta` após contrato e dependências → `em execução` → `em revisão` → `validada localmente` → `integrada/publicada` somente após confirmação remota. `bloqueada` conserva causa e dependência; estados do Project só mudam pelo worker autorizado, com leitura/evidência. Checker usa somente projeção `ready`/`blocked`/`done` aprovada na base; é reserva de escopo, não tracker concorrente nem sync automático do board.

O [contrato técnico do checker](../engineering/pr-scope-observation.md) define observação, limites de confiança, bootstrap e evidência. Este pacote não instala labels, check remoto, CODEOWNERS ou proteções. CODEOWNERS permanece decisão aberta: precisa de reviewer real elegível, distinto do autor para aprovação; identidade de role/área não satisfaz esse requisito.

## Configuração Matt aplicada

Setup aplicado localmente em 2026-10-03 a partir da skill instalada, sem reinstalação. Tracker escolhido: **GitHub Issues** do repo existente; [Project /3](https://github.com/users/joaosantossgp/projects/3) acompanha as mesmas Issues, não recebe specs/status duplicados. **PRs as a request surface: no.** Layout de domínio: [single-context](domain.md). Na primeira aplicação, triage estava ausente e a etapa foi omitida. Após pedido explícito de instalar `/triage`, o setup foi complementado com [mapeamento local](triage-labels.md); nenhuma label remota foi criada/aplicada.

O procedimento upstream é adaptado ao contrato do repositório: regras de autorização prevalecem sobre create/publish/claim/labels/commit sugeridos pela skill. CLI `gh` ou conector autorizado podem ser usados quando realmente disponíveis e verificados; setup não instala CLI, faz login ou comprova acesso remoto. Publicação de specs/tickets depende do worker que já gere Issues/Project; não criar outro tracker em `.scratch`. Rascunho local, quando necessário, é preparação de handoff, não fonte paralela de estado.

| Pedido da skill | Operação neste projeto | Gate |
|---|---|---|
| Fetch/read ticket | Ler a Issue real e comentários por ferramenta suportada; linkar spec/plano do repo | Identidade e acesso verificados; leitura local não confirma remoto |
| Publish spec (`/to-spec`) | Sintetizar no destino existente; worker vincula/atualiza a Issue autorizada | Spec única; não duplicar o contrato nem publicar automaticamente |
| Publish tasks (`/to-tickets`) | Entregas pequenas completas, ligadas à Issue/mapa existente e bloqueadores | Decomposição/aceite aprovados; handoff para worker sem duplicar Issues/cards |
| Map/child/frontier (`/wayfinder`) | Direção ampla em Issue existente; filhos/dependências nativas quando disponíveis | Fronteira = aberta, sem blockers pendentes e sem claim concorrente; não inferir API disponível |
| Claim/resolve | Responsável autorizado atribui, comenta/fecha e registra contexto no mapa existente | Evidência de aceite; não iniciar escrita remota apenas porque upstream manda |

Se sub-issues/dependências nativas não estiverem disponíveis, usar links explícitos no corpo e declarar o fallback. Convenções upstream `wayfinder:map`/`wayfinder:<tipo>` não são criadas implicitamente: mapear ao item existente e encaminhar eventual necessidade ao worker, sem ampliar o catálogo de labels por conta própria. Roles/áreas não substituem relações de dependência nem permissões. Nenhuma operação remota foi executada no setup.

## Nomes legíveis e identificadores das skills

Os nomes PT-BR abaixo são descrições de leitura. Diretórios, identificadores e comandos originais não foram renomeados; estes rótulos não criam aliases executáveis. Referem-se às nove skills originais e à triage acrescentada explicitamente, todas na revisão instalada, não ao catálogo upstream mais recente.

| Nome de leitura | Identificador/comando original | Quando usar |
|---|---|---|
| Mapear decisões | `/wayfinder` | Direção ampla: mapa de decisões e fronteira, antes de executar entregas |
| Pesquisar fontes | `/research` | Investigar fatos em fontes primárias e produzir nota rastreável |
| Examinar decisões | `/grilling` | Perguntas e cenários para resolver decisões com o usuário |
| Examinar com documentação | `/grill-with-docs` | Combinar grilling e domain-modeling quando discussão altera conceitos/decisões |
| Modelar domínio | `/domain-modeling` | Precisar linguagem e registrar conceitos/ADRs pertinentes; não é mera leitura |
| Definir especificação | `/to-spec` | Sintetizar conversa e contexto em spec única, sem entrevista adicional |
| Decompor em tarefas | `/to-tickets` | Fatias completas com aceite e dependências, sem publicação implícita |
| Experimentar uma hipótese | `/prototype` | Protótipo descartável para uma pergunta de lógica/estado/interface; sem produção implícita |
| Configurar workflow Matt | `/setup-matt-pocock-skills` | Configurar tracker, mapeamento de triagem e leitura de domínio, reutilizando contratos existentes |
| Avaliar e encaminhar pedidos | `/triage` | Verificar/recomendar categoria e estado e produzir brief; mudanças remotas só com autorização |

**Etapa** é o momento do trabalho (pesquisa, desenho, revisão); **skill** é o procedimento escolhido; **role** é a responsabilidade principal na Issue; **área** é a frente afetada. Uma skill não é persona, ACL ou estado do Project. As [roles/áreas](#roles-áreas-e-ownership) e a [matriz por etapa](#etapas-skills-entregáveis-gates-e-owners) continuam separadas e usam poucos rótulos.

Superpowers mantém nomes originais inequívocos na matriz: Desenhar a solução (`superpowers:brainstorming`), Planejar execução (`superpowers:writing-plans`), Testar primeiro (`superpowers:test-driven-development`), Diagnosticar falhas (`superpowers:systematic-debugging`), Solicitar revisão (`superpowers:requesting-code-review`) e Verificar conclusão (`superpowers:verification-before-completion`). Feynman: Investigar em profundidade (`deep-research`, com `/deepresearch` somente se runtime verificado) e Explorar evidência em PDFs (`pdf-explore`). Context7 é ferramenta de consulta de documentação por versão, não role ou etapa. As views do Project ficam com o worker responsável; este setup não as cria nem muda o board.

## Adaptação de triagem — pedido explícito 2026-10-03

Avaliar e encaminhar pedidos — `/triage` foi acrescentada sozinha, na revisão Matt existente, com AGENT-BRIEF/OUT-OF-SCOPE/metadados/licença. Dependências de discussão `grilling` e `domain-modeling` já estavam selecionadas; nenhum catálogo completo, runtime ou CLI foi instalado. **Instalada** significa arquivos e dependências verificadas; **setup aplicado** significa roteamento/mapeamento documental configurado. Registro/autodisparo de slash command nesta interface e execução GitHub não foram testados; `disable-model-invocation: true` e `allow_implicit_invocation: false` continuam intactos.

Usar [categorias e estados](triage-labels.md) para avaliar uma Issue real; ler histórico, glossário/ADRs, verificar redundância e recomendar antes de aplicar resultado. Categoria e estado de triagem não substituem role/área, status do Project ou contrato de paths. PRs as a request surface permanece **no**: não descobrir/executar triagem de PRs nesta configuração; pedido explícito de PR exige escopo específico, sem checkout/execução de código não confiável por esta instalação.

O brief no comentário complementa a tarefa e referencia a spec/plano existentes; não substitui AGENTS/ADR/spec/allowlist por declarar-se contrato. Preservar objetivo, dependências, aceite e path contract versionado, mesmo quando o template upstream recomenda evitar paths para durabilidade. `.out-of-scope/` não é criado preventivamente: rejeições ficam na Issue/decisão existente; qualquer novo arquivo só com tarefa e destino autorizados, sem tracker paralelo. Confirmação humana/autoridade para fechar ou rejeitar não é simulada.

Comentários/Issues efetivamente publicados por triage preservam o aviso upstream `This was generated by AI during triage.` no início. Este turno instala/configura; não publica comentários, atribui, aplica labels, fecha Issues nem muda Project/views. O worker responsável recebe handoff quando houver uma operação remota explicitamente solicitada. Superpowers e os limites de Feynman/Context7 permanecem.

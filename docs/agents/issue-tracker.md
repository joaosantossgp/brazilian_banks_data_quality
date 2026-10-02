# Acompanhamento do trabalho

## Autoridade de cada superfície

- **Repositório:** código, contratos, arquitetura, glossário, decisões, specs/planos e evidências rastreáveis. Entradas comuns: [README](../../README.md), [AGENTS](../../AGENTS.md), [arquitetura](../architecture.md), [spec da fundação](../superpowers/specs/2026-10-02-governance-research-design.md) e [plano autorizado](../superpowers/plans/2026-10-02-governance-foundation-plan.md).
- **Issue real:** problema/objetivo, escopo/arquivos, dependências, critérios de aceite e links da evidência/revisão. Enquanto não publicada, declarar “não publicada — tarefa local” e apontar ao ticket/brief, sem inventar ID ou URL.
- **Project existente /3:** [Brazilian banks data quality](https://github.com/users/joaosantossgp/projects/3), privado, acompanha estado e links das mesmas tarefas/Issues. Não criar outro Project. Estado remoto requer leitura/verificação remota; documento local não prova atualização do board.

Na leitura de preparação em 2026-10-02, o remoto público tinha default main e nenhuma branch; o checkout ainda não tinha commits. Essa observação é datada, não uma afirmação permanente de remoto vazio. O Project privado não privatiza repo/Issues. A autorização explícita de publicação de 2026-10-02 permite completar/revisar a fundação, CI offline mínimo, commit/push do conjunto revisado, bootstrap mínimo de main, draft PR e reconciliação das mesmas Issues/cards no Project /3 por ferramenta suportada. Os gates anteriores de não publicar/não implementar CI são histórico datado e foram substituídos para esta entrega. Não autoriza merge, deploy, nova coleta, capítulo, calendário, runtime/contas/chaves, mudança de segurança/permissões/tokens/proteções ou outro Project. Publicação e CI foram confirmadas em 2026-10-02 pelos commits e runs abaixo; não há novo gate humano para o escopo já aprovado.

## Trabalho corrente e publicação confirmada

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

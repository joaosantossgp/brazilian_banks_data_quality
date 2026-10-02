# Entrada operacional dos agentes

Leia este arquivo antes de atuar neste checkout. O contrato aprovado está na [spec da fundação](docs/superpowers/specs/2026-10-02-governance-research-design.md), com complemento operacional e rigor **econômico, contábil e financeiro**. [Arquitetura](docs/architecture.md), [glossário](GLOSSARY.md), [tracker](docs/agents/issue-tracker.md), [plano autorizado](docs/superpowers/plans/2026-10-02-governance-foundation-plan.md) e [tooling](docs/engineering/research-tooling-20261002.md) são as referências comuns ao README; não criar contratos ou trackers concorrentes.

## Escopo e autoridade

- Trabalhar somente neste checkout, no computador autorizado por João. Não acessar outros computadores nem o projeto CVM separado; preservar arquivos não relacionados.
- Implementado: IF.data **individual/Resumo 201012, 202312 e 202412**. A expansão 202312 foi executada e validada localmente; [ledger e limitações](docs/engineering/expansion-execution.md). A base 2010–2026 financeira principal, prudencial/individual complementares é alvo, ainda não implementado. Financeiro é IF.data; CVM/B3 fornecem apenas metadados.
- A autorização explícita de publicação de 2026-10-02 permite completar/revisar a fundação, CI offline mínimo, commit/push do conjunto revisado, bootstrap mínimo de main, draft PR e reconciliação das mesmas Issues/cards no Project /3 por ferramenta suportada. Os gates anteriores de não publicar/não implementar CI são histórico datado e foram substituídos para esta entrega. Não autoriza merge, deploy, nova coleta, capítulo, calendário, runtime/contas/chaves, mudança de segurança/permissões/tokens/proteções ou outro Project. Publicação e CI remotas continuam pendentes de confirmação; não há novo gate humano para o escopo já aprovado.
- Na preparação local sem HEAD, usar snapshots imutáveis/diff para revisão. O commit/push autorizado segue somente o manifesto revisado, bootstrap mínimo e draft PR; não criar commits por conveniência. CI usa apenas testes offline existentes, sem coleta/upload/deploy; não alterar proteções de branches.
- A monografia conserva 2010–2024 e capital aberto. Unidade final, janela, holdings, amostra/eligibilidade, método e implicações econômicas, contábeis e financeiras pertencem a João/orientador. Nunca inventar indicadores, cálculos, identidades ou recomendações de investimento.

## Antes de executar uma tarefa

1. Ler arquitetura/glossário, spec e apenas o brief da tarefa designada com restrições complementares. Confirmar objetivo, dependências satisfeitas, arquivos autorizados e aceite observável; limites locais/externos vêm antes da escolha de ferramenta.
2. Registrar o **link real da Issue**. Se ainda não publicada, declarar **“não publicada — tarefa local”** e apontar ao brief/ticket local existente, sem inventar número, URL ou estado remoto. O [tracker](docs/agents/issue-tracker.md) define a autoridade de cada superfície.
3. Registrar base de revisão e arquivos a tocar; usar o snapshot existente quando disponível e preservar código, dados, bruto, relatórios e histórico fora do escopo. Capturar evidência necessária sem nova coleta implícita.
4. Usar os [comandos offline verificados no README](README.md#comandos-locais-verificados) conforme o impacto. Replay usa destino novo; scripts que escrevem em artefatos aceitos exigem inspeção prévia do destino. Documentação pede links/coerência/escopo; não adicionar testes que apenas repitam o texto nem repetir suíte sem necessidade.

**Fundação corrente:** Tasks 1–4 revisadas PASS; Task 5 prepara CI, autoridade, privacidade e conjunto público exato, conforme [plano aprovado](docs/superpowers/plans/2026-10-02-governance-foundation-plan.md). Revisão independente da Task 5, checks da árvore curada e verificação remota permanecem pendentes. Briefs/restrições, snapshots e relatórios em `.superpowers/sdd/` são evidência operacional somente local, excluída da publicação. Não inventar Issue/PR/estado remoto.

## Decisões e evidência durante a execução

Método, fórmula ou arquitetura precisam de motivação, fonte/evidência primária, versão/data/página ou localizador e limites. Registrar no contrato/nota correspondente já existente, ligando a tarefa à decisão; não repetir o corpo da spec aqui. Dúvida factual gera pesquisa verificável; mudança metodológica ou escolha acadêmica vai a João/orientador, sem promover uma hipótese a decisão aprovada.

Para dados financeiros, justificar conceito, componentes/fórmula, unidade, janela, referência, perspectiva/perímetro, regime, versões e quebras. Não emendar financeiro/prudencial/individual por nome, nem presumir continuidade em 2014/2015 ou Cosif 2025. Estoque e fluxo têm janelas diferentes; dezembro não prova resultado anual. Cadastro CVM, listagem B3 e vínculo emissor/holding–unidade financeira exigem evidência temporal própria. Desconhecido não é negativo nem critério silencioso de exclusão.

Preservar corpos e proveniência: URL/parâmetros, recuperação UTC, status/headers/diagnósticos e SHA-256, inclusive falhas. Separar ausência estrutural, NA, NI, null, vazio e zero. Falha HTTP/schema não significa população zero. Atualizar explicitamente incertezas, contagens e limites no documento de evidência pertinente; não sobrescrever originais ou confirmar os oito vínculos ainda desconhecidos sem prova datada.

## Encerramento e revisão

Só encerrar com arquivos/resultados verificáveis, comandos e saídas, critérios atendidos ou bloqueios, revisão de escopo e atualização documental das incertezas. Comparar o snapshot/diff e hashes protegidos; manter relatórios anteriores intactos. **Testes de software** verificam comportamento/integridade; a **conferência econômica, contábil e financeira** verifica conceitos, comparabilidade, janelas/perímetros e fontes. Um não substitui o outro.

Distinguir **resultado local**, **revisão aprovada** e **publicação confirmada**. Reviewer lê e reporta; revisão prevista não significa revisão concluída. Done aponta para evidência. Nenhum arquivo local altera por si o estado de Issue/Project. O fluxo futuro Issue → branch → PR → checks → revisão → integração será aplicado quando autorizado e verificado; não afirma CI, proteções ou publicação ativos agora. A publicação deste conjunto já foi aprovada em 2026-10-02; revisar o manifesto concreto, concluir checks e verificar o remoto sem repetir esse gate. A licença própria permanece não escolhida, com notices MIT upstream preservados.

## Ferramentas e redação assistida

Nove skills Matt existentes organizam direção/domínio/spec/tickets; Superpowers já é global e não deve ser duplicado. Context7 auxilia documentação técnica, conferida contra a versão efetivamente usada. Somente Feynman deep-research/pdf-explore estão ativas; MIT, hashes e seleção permanecem nos [registros de tooling](docs/engineering/research-tooling-20261002.md). Recursos upstream de governança no pacote não substituem este contrato. `/deepresearch` não foi validado no Codex nativo; não instalar runtime nem reativar o bundle para presumir compatibilidade.

João permite apoio à redação acadêmica sob sua direção, revisão e responsabilidade, com fontes/dados/citações/referências verificáveis, sem fabricação e observando transparência institucional aplicável. Essa decisão substitui a antiga proibição geral; não há capítulo solicitado nesta tarefa. Paper-writing segue inativa até necessidade concreta. Histórico de aprovações e decisões permanece na spec, [nota de desenho](docs/engineering/brainstorming-2010-2026-20261002.md) e ledgers do [piloto](docs/engineering/pilot-execution.md)/[expansão](docs/engineering/expansion-execution.md).

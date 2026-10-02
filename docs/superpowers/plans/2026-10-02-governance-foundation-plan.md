# Fundação de governança — Implementation Plan

**Autoridade vigente em 2026-10-02:** publicação e CI mínimos explicitamente aprovados; o complemento final deste documento prevalece sobre gates anteriores, preservados como histórico datado. Não solicitar nova aprovação do mesmo escopo. Verificação da publicação inicial e do CI concluída; evidência de encerramento abaixo. A reconciliação do Project continua separada.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidar uma navegação documental única, um workflow de tarefa/aceite/evidência e um conjunto revisável para futura sincronização com o GitHub existente, preservando código/dados e as decisões de João.

**Architecture:** Reutilizar README, AGENTS, glossário, specs, planos e relatórios existentes. Repo contém documentos/código, Issues guardam tarefa/aceite e o Project existente acompanha as mesmas tarefas. A fundação não altera o coletor; desenho/implementação da expansão financeira permanecem separados.

**Tech Stack:** Markdown, templates GitHub, Git, Python 3.12 e Node 22; CI offline mínimo autorizado no complemento Task 5. Nenhuma instalação de dependência, serviço ou backend novo.

## Global Constraints

- Ambiente: computador autorizado para esta tarefa. Checkout: `raiz deste checkout`. Nunca acessar outros computadores não autorizados ou o projeto CVM separado.
- Spec aprovada: [governance-research-design](../specs/2026-10-02-governance-research-design.md), incluindo a alteração explícita de João sobre redação assistida, aprovação explícita registrada em 2026-10-02.
- A amostra acadêmica é filtro posterior, sem limitar armazenamento. A monografia mantém seu texto atual 2010-2024, foco capital aberto e decisões metodológicas humanas.
- Financeiro somente IF.data; CVM/B3 somente metadados. Perspectivas financeira, prudencial e individual permanecem separadas; este plano não adquire novos períodos nem define relatórios/variáveis da expansão.
- Redação assistida pode ser usada sob orientação, revisão e responsabilidade de João, com fontes verificáveis, sem fabricação de dados/citações/referências e respeitando transparência institucional aplicável. Não redigir capítulo nesta tarefa nem reativar paper-writing automaticamente.
- Nove skills Matt intactas, Superpowers global, Context7 para documentação técnica da versão usada; apenas Feynman deep-research/pdf-explore ativas, MIT/proveniência preservados. `/deepresearch` não foi validado no Codex nativo; não instalar runtime para contornar essa limitação.
- Não alterar calendário, permissões, segredos, segurança ou configuração global. Não sobrescrever bruto, evidências anteriores ou arquivos não relacionados.
- **Limite da aprovação inicial, superado para publicação pelo complemento Task 5:** João aprovou este plano e execução com agentes por tarefa, com revisão entre etapas. Naquele estágio, nenhum commit, push, PR, merge, deploy, Issue ou alteração do Project estava autorizado por esta entrega. A etapa de publicação exige aprovação concreta posterior; a preferência da skill por commits frequentes não revoga este limite.

## Contexto que o executor deve conhecer

**Na preparação inicial:** checkout sem commits, branch `feat/ifdata-two-quarter-pilot`; os arquivos existentes estavam locais. A publicação posterior está registrada no encerramento da Task 5 abaixo. O piloto/expansão implementados abrangem apenas 201012, 202312 e 202412, individual/Resumo, 40.904 observações. A interface do coletor continua limitada; documentação de base alvo não autoriza ampliar sua allowlist. O dossiê conserva oito relações históricas desconhecidas.

Referências existentes: `docs/engineering/expansion-execution.md`, `reports/expansion-20261001.verification.json` (evidência somente local, excluída da publicação), `docs/engineering/capital-aberto-identity-dossier.md`, `docs/engineering/research-tooling-20261002.md`, `third_party/mattpocock-skills/provenance.json` e `third_party/feynman/provenance.json`. O Project único é `https://github.com/users/joaosantossgp/projects/3`; seu estado atual deve vir de leitura suportada ou do coordenador, não da descrição histórica dos seis rascunhos.

Setup de verificação em PowerShell, no computador autorizado (a partir da raiz do checkout):

```powershell
$foundationRepo = (Get-Location).Path
$foundationPython = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$foundationNode = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$foundationGit = (Get-Command git).Source
hostname
Set-Location -LiteralPath $foundationRepo
& $foundationGit -c "safe.directory=$foundationRepo" status --short --branch
```

Esperado: computador autorizado conferido, checkout correto e estado real registrado. Se encontrar alterações concorrentes, preservar e ajustar o plano ao diff observado. Usar worktree apenas se necessário e viável; um checkout sem commits não permite tratar uma base de worktree como existente. Não criar commit só para viabilizar isolamento. Não automatizar a UI Codex.

## Arquivos e responsabilidades

| Arquivo | Ação e responsabilidade |
|---|---|
| `README.md` | Modificar navegação humana e diferença entre implementado/alvo/local/publicado |
| `AGENTS.md` | Modificar instruções atuais e referências; preservar decisões/histórico relevante |
| `GLOSSARY.md` | Reutilizar termos; não duplicar definições em outros documentos |
| `docs/architecture.md` | Criar mapa curto das responsabilidades existentes e contratos alvo |
| `docs/agents/issue-tracker.md` | Atualizar fluxo e fontes únicas de tarefa/status |
| `.github/ISSUE_TEMPLATE/work-item.md` | Criar um template Markdown de tarefa com aceite/evidência |
| `.github/pull_request_template.md` | Criar template curto para futuras revisões autorizadas |
| `.gitignore` | Ajustar exclusões locais já necessárias antes de propor publicação |
| `reports/governance-foundation.verification.json` | Criar evidência de execução desta fundação; não substituir relatórios do piloto |

Não criar Wiki, outro Project, ADR duplicando a spec, suite de testes de texto ou framework adicional. Specs/planos antigos permanecem históricos; não mudar sua aprovação original retroativamente.

### Task 1: Navegação e arquitetura documental única

**Files:** Modify `README.md`, `AGENTS.md`, `docs/agents/issue-tracker.md`; Create `docs/architecture.md`. Reuse `GLOSSARY.md` e a spec aprovada.

**Interfaces:** Consumes spec aprovada e evidência existente; produces entradas README/AGENTS que apontam ao mesmo contrato, arquitetura e tracker. Nenhuma API de código é modificada.

- [ ] **Step 1:** Registrar hashes dos arquivos de `bank_quality/`, `tests/`, `scripts/` e relatórios anteriores para comparação ao final. Registrar estado Git e nome dos documentos que serão editados; a evidência de base do piloto não é apagada.
- [ ] **Step 2:** Criar `docs/architecture.md` com este conteúdo mínimo completo:

```markdown
# Arquitetura e contratos

## Referência de decisões
O contrato aprovado é [fundação de governança, pesquisa e rigor](superpowers/specs/2026-10-02-governance-research-design.md).
Termos de domínio ficam no [glossário](../GLOSSARY.md); tarefas seguem o [tracker](agents/issue-tracker.md).

## Comportamento implementado
`bank_quality/archive.py` conserva respostas/proveniência; `ifdata.py` e `portal.py` implementam aquisição limitada; `inventory.py` e `coverage.py` inventariam valores/cobertura; `metadata.py` trata evidência cadastral; `replay.py` reproduz o derivado do bruto verificado.
O código atual cobre os lotes individuais/Resumo 201012, 202312 e 202412. O [ledger de execução](engineering/expansion-execution.md) registra evidência e limitações.

## Base alvo, ainda não implementada
Aquisição IF.data -> bruto imutável/versionado -> inventários por referência/perspectiva/relatório -> metadados temporais CVM/B3 e vínculos comprovados -> recortes documentados para monografia e outros projetos.
Financeiro é principal; prudencial e individual são complementares identificados separadamente. Não emendar perímetros, regimes ou conceitos por nome. Registro CVM, listagem e identidade são atributos distintos; desconhecido não significa negativo.
Relatórios/variáveis da expansão e modelo de consulta serão decididos em desenho separado. A amostra acadêmica é filtro posterior.

## Aceite e limites
Testes de software verificam comportamento/integridade; validade econômica, contábil e financeira exige definições e evidência. Fórmulas, unidades, janelas, versões, quebras, ausências e limitações devem ser rastreáveis conforme a spec.
README é entrada humana; AGENTS orienta agentes; Issues têm tarefa/aceite; o Project existente tem acompanhamento. Publicação só é afirmada depois de verificação remota.
```

- [ ] **Step 3:** Em README/AGENTS, apontar para arquitetura, spec, plano, tracker e tooling. Identificar o piloto como comportamento implementado e a expansão como alvo. Consolidar apenas blocos atuais redundantes; preservar os registros anteriores como históricos, sem continuar descrevendo dezembro/2023 como lote futuro. Não copiar o corpo da spec para README/AGENTS.
- [ ] **Step 4:** Atualizar `docs/agents/issue-tracker.md`: repo para contratos/evidência, Issue para tarefa/aceite/dependências, Project/3 para estado e links das mesmas tarefas. Descrições antigas de rascunhos são histórico; `.scratch` não passa a ser tracker remoto. Identificar que migração exige leitura atual e registro de correspondência entre item original e Issue, sem prometer IDs preservados automaticamente.
- [ ] **Step 5:** Abrir todos os links relativos adicionados; confirmar existência do destino e coerência de estado. Aceite: uma navegação sem links quebrados, nenhuma alegação de publicação ou expansão executada, decisões abertas claramente atribuídas a João, redação assistida conforme a decisão mais recente.

### Task 2: Templates pequenos para tarefa e revisão

**Files:** Create `.github/ISSUE_TEMPLATE/work-item.md`, `.github/pull_request_template.md`; reference `docs/agents/issue-tracker.md`.

**Interfaces:** Consumes links da Task 1; produces templates nativos Markdown. Não cria labels, regras de branch, integrações automáticas ou itens remotos.

- [ ] **Step 1:** Criar o template de Issue exatamente abaixo; os títulos são instruções reutilizáveis, não dados de uma tarefa já publicada:

```markdown
---
name: Trabalho técnico
about: Tarefa delimitada com critérios de aceite e evidência
title: ''
labels: ''
assignees: ''
---

## Problema e resultado esperado
Descreva o comportamento concreto e o resultado observável.

## Escopo e dependências
Liste arquivos/contratos afetados e links às tarefas bloqueadoras, spec e plano.

## Critérios de aceite
- [ ] Resultado verificado com evidência correspondente ao escopo.
- [ ] Estados desconhecidos, limitações e decisões humanas pendentes explícitos.
- [ ] Documentação atualizada por referência, sem outro tracker.

## Validação e evidência
Registre comandos, resultados e links aos artefatos. Separe teste de software de validação econômica, contábil e financeira.

## Estado de entrega
Declare o que foi validado localmente e o que foi publicado; inclua links remotos somente após confirmação.
```

- [ ] **Step 2:** Criar o template de PR abaixo para uso futuro; esta tarefa não abre PR:

```markdown
## Problema e comportamento resultante
Descreva o trigger e a mudança observável; ligue a Issue e a spec aplicáveis.

## Validação
Registre checks executados e evidências; declare limitações e checks não executados.

## Escopo de revisão
Identifique mudanças de contrato, dados/fontes, unidades/perímetros ou decisões humanas afetadas. Confirme a correspondência ao plano autorizado.
```

- [ ] **Step 3:** Conferir `name`/`about` no frontmatter e localização dos arquivos. O reconhecimento remoto depende de os templates chegarem à branch padrão; não declarar ativos no GitHub por existirem localmente. A referência técnica já foi conferida via Context7 `/github/docs` e [documentação primária GitHub](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates).
- [ ] **Step 4:** Simular uma tarefa local usando o resultado da Task 1: problema de navegação divergente, arquivos efetivos editados, links de aceite conferidos e estado local. Não criar um cartão/Issue paralelo. Aceite: um revisor consegue avaliar a entrega usando os campos, sem status ou decisões duplicados.

### Task 3: Verificação local e evidência de aceite

**Files:** Read existing `tests/test_*.py`, `tests/test-budget.cjs`, `tests/test-portal-ready.cjs`; Create `reports/governance-foundation.verification.json`.

**Interfaces:** Consumes arquivos/documents da Tasks 1–2 e hashes de base; produces um relatório de checks, sem mudar o coletor ou o bruto. Não acrescentar testes que apenas espelhem texto de documentação.

- [ ] **Step 1:** Rodar uma vez os testes existentes, a partir do repo. Se a execução desta fundação já produziu baseline com os mesmos arquivos/inputs protegidos por hash, reutilizar esse resultado e verificar os hashes em vez de repetir a suite sem mudança:

```powershell
& $foundationPython -B -m unittest discover -s tests -v
& $foundationNode tests/test-budget.cjs
& $foundationNode --test tests/test-portal-ready.cjs
```

Esperado: testes Python sem falhas (54 no baseline observado), mensagem `byte, deadline and reserve guards passed` e suite Node sem falhas. Não tratar a contagem histórica como promessa se o diff concorrente mudar a suite. Nenhum desses comandos realiza coleta financeira ou exige novo pacote.

- [ ] **Step 2:** Comparar os hashes de base com os arquivos após a fundação; esperar código, testes, scripts e relatórios anteriores intactos. Conferir 36 entradas do manifesto Matt e as 30 entradas Feynman nos caminhos ativos/inativos atuais; esperar somente dois SKILL.md Feynman ativos, 14 no backup e MIT preservado.
- [ ] **Step 3:** Conferir navegação/documentos novos e os seis critérios de rigor da spec. Não recalcular amostra, fórmula econômica/contábil/financeira ou resultados acadêmicos nesta etapa; verificar que esses critérios foram referenciados e decisões humanas não foram assumidas. Confirmar que deep-research continua descrita como dependência não validada.
- [ ] **Step 4:** Registrar JSON com campos `checked_at_utc`, `hostname`, `branch`, `scope`, `changed_files`, `checks` (cada comando/status/evidência), `protected_files_unchanged`, `skill_verification`, `published` (false), `limitations`, `next_gate`. Os valores devem vir desta execução, não de exemplos inventados. Evitar stdout sensível e caminhos pessoais em evidência proposta para publicação.
- [ ] **Step 5:** Revisar o diff desta fundação contra a spec e o plano, corrigindo contradições locais. Aceite: links existentes, checks com status real, limite de software versus validade contábil explícito e nenhum novo dado/coleta/serviço. Uma falha concreta é diagnosticada antes de repetir a suite; não afirmar sucesso parcial como aceite completo.

### Task 4: Preparar sincronização oficial e parar no gate de publicação

**Files:** Modify `.gitignore`; Read tudo que entrar no manifesto proposto; reuse relatório da Task 3. Não criar uma nova governança paralela.

**Interfaces:** Consumes fundação validada; produces conjunto de arquivos e ações remotas concretos para aprovação, com destino no repo/Project existentes.

- [ ] **Step 1:** Preservar `.gitignore` existente e acrescentar somente padrões ainda ausentes:

```gitignore
data/runs/
expansion-stage/
.scratch/
third_party/feynman/inactive-20261002/
third_party/feynman/provenance-before-selection-20261002.json
```

`data/raw/`, `data/derived/`, collections, caches e tooling temporário já têm padrões. Nada é apagado por ignorar. Publicação de dados derivados/brutos é decisão separada, não parte deste plano.

- [ ] **Step 2:** Verificar que exemplos sensíveis/temporários estão excluídos e inspecionar os candidatos sem staging:

```powershell
& $foundationGit -c "safe.directory=$foundationRepo" check-ignore --no-index data/raw/probe.bin data/runs/probe/raw/probe.bin .scratch/probe.md third_party/feynman/inactive-20261002/skills/paper-writing/SKILL.md
& $foundationGit -c "safe.directory=$foundationRepo" ls-files --cached --others --exclude-standard
```

Esperado: os quatro probes são ignorados; a listagem permite revisão arquivo por arquivo. Manifesto proposto inclui somente o subconjunto aprovado, não automaticamente toda a listagem. Nunca usar `git add -A` ou commit para tornar a proposta concreta.

- [ ] **Step 3:** Preparar a relação exata de arquivos, licenças/notices e mudanças. Inspecionar dados/capturas, caminhos pessoais, segredos, rascunhos e source notices; remover da proposta o que não pertence à entrega pública. Preservar tudo local. A licença MIT das referências não escolhe automaticamente a licença do código próprio; apresentar essa escolha junto ao conjunto concreto antes de publicar.
- [ ] **Step 4:** Preparar a correspondência dos itens atuais do Project com Issues futuras: ler estado/itens por ferramenta suportada ou solicitar ao coordenador a leitura; usar o Project existente /3 e repo existente. Cada Issue terá escopo/aceite/evidência reais, e cada item terá links de correspondência para evitar duplicação. Se não houver ferramenta suportada de Project, fornecer ao coordenador o mapeamento e os passos manuais mínimos; não editar internals nem automatizar UI.
- [ ] **Step 5:** Entregar o conjunto concreto e pedir aprovação somente das ações ainda não autorizadas: arquivos/branch/licença/audiência, commit/push e criação/migração de Issues/atualização do Project. **Parar aqui** nesta autorização. Depois da aprovação específica, verificar conteúdo/commit remoto, branch padrão/templates e links das mesmas Issues no Project antes de afirmar GitHub como fonte documental sincronizada. Não abrir PR, merge ou deploy sem instrução explícita correspondente.

Aceite desta task: proposta verificável e gate real identificado, com nenhum commit/push ou escrita GitHub executados antecipadamente. A limitação de ferramenta de Project não impede completar docs, templates e testes locais.

## Cobertura da spec e revisão deste plano

| Requisito | Entrega/check |
|---|---|
| Navegação, arquitetura e linguagem únicas | Task 1, links e glossário reutilizado |
| Tarefa/aceite/status em lugares definidos | Task 2 e mapeamento da Task 4 |
| Ferramentas enxutas, versões, licenças e limites | Task 1 referências, Task 3 hashes, Task 4 notices |
| Proveniência/população/fórmulas/perímetros/ausências/reprodução/limitações | Contratos referenciados na Task 1 e verificados documentalmente na Task 3; conferência econômica, contábil e financeira posterior permanece humana |
| Redação assistida sob responsabilidade de João | Spec/AGENTS coerentes; nenhuma redação de capítulo ou reativação Feynman extra |
| GitHub como referência oficial sem falsa publicação | Task 4, proposta + autorização + confirmação remota posterior |
| Escopo delimitado e reutilização de evidência | Não alterar collector/dados; Task 3 usa testes existentes |

Revisão do plano: paths/commands/interfaces conferidos contra o checkout; conteúdos dos templates estão completos; não há função/API nova indefinida. As decisões futuras de amostra/relatórios/backend estão fora desta fundação, não são lacunas implementadas por suposição. Nenhum check acima foi executado como implementação deste plano durante sua elaboração.

## Handoff de execução

João escolheu a opção 1 abaixo; a implementação local está autorizada. Opções registradas como histórico do handoff:

1. **Subagent-driven (recomendado pelo Superpowers):** agente por tarefa, com revisão entre tarefas, usando subagent-driven-development. Adequado para revisão independente; tasks com arquivos compartilhados seguem sequenciais.
2. **Inline:** execução nesta sessão com executing-plans e checkpoints. Menor coordenação para esta fundação documental pequena.

A escolha inicial autorizou executar a fundação local dentro deste plano; não autorizava coletar história, redigir capítulo, instalar runtime, alterar calendário ou publicar. O gate de publicação da Task 4 foi atendido pela autorização posterior da Task 5 e pela publicação verificada abaixo. Coleta histórica e novas decisões metodológicas permanecem fora desta entrega.


## Complemento vinculante de execução

AGENTS é a entrada operacional do agente, não apenas uma descrição: escopo/arquitetura/comandos/limites, objetivo/dependências/aceite da tarefa, Issue real ou “não publicada” com tarefa local, justificativa/fonte para decisões, evidência de conclusão e atualização das incertezas. Task 1 implementa esse contrato; Task 2 reflete vínculo/aceite/revisão nos templates; Task 3 distingue software de conferência econômica, contábil e financeira; Task 4 prepara a publicação concreta sem executá-la. Rigor financeiro não autoriza inventar cálculo, indicador, amostra ou recomendação de investimento.

Na preparação sem HEAD e sem autorização de commit, snapshots imutáveis e pacotes de diff da árvore de arquivos substituíram BASE/HEAD para revisão. Após a publicação autorizada, commits reais identificam a base e o diff de revisões posteriores. Não criar commit ou outro checkout por conveniência do workflow. Agentes implementadores são sequenciais; reviewer é leitura apenas. Novos testes que apenas espelhem documentação não são necessários; conferir links/frontmatter e utilizar os testes existentes conforme a tarefa.

## Autoridade efetiva e Task 5 — publicação aprovada em 2026-10-02

A autorização explícita de publicação de 2026-10-02 permite completar/revisar a fundação, CI offline mínimo, commit/push do conjunto revisado, bootstrap mínimo de main, draft PR e reconciliação das mesmas Issues/cards no Project /3 por ferramenta suportada. Os gates anteriores de não publicar/não implementar CI são histórico datado e foram substituídos para esta entrega. Não autoriza merge, deploy, nova coleta, capítulo, calendário, runtime/contas/chaves, mudança de segurança/permissões/tokens/proteções ou outro Project. Publicação e CI iniciais foram confirmadas pelos links de encerramento abaixo; não há novo gate humano para o escopo já aprovado. Todas as restrições anteriores de commit/push/CI e o gate posterior da Task 4/handoff são histórico da autorização anterior; este complemento prevalece. Tasks 1–4 foram revisadas PASS; não repetir etapas por essa atualização.

### Task 5: CI mínimo e conjunto público exato

**Files:** `.github/workflows/ci.yml`, documentos próprios identificados na proposta, `.gitignore`, proposta e manifesto existentes. Backups e relatório de execução/revisão ficam somente em `.superpowers/sdd/`, excluída da publicação. Não alterar código/testes/scripts/raw/relatórios antigos nem bytes vendorizados.

- [x] Preservar originais locais e sanitizar apenas caminhos pessoais, IDs e citações privadas, mantendo decisões e métodos.
- [x] Reconciliar autoridade vigente e links com o conjunto publicado; evidências excluídas são descritas como somente locais.
- [x] Preparar workflow CI, push/pull_request, contents read, Linux/Python 3.12/Node 22, actions v6 pinadas, sem instalação/coleta/upload/deploy; usar unittest, budget e portal-ready existentes.
- [x] Atualizar proposta e manifesto com paths/bytes/SHA-256 exatos; licença própria não escolhida e notices MIT preservados.
- [x] Revisão independente e final; checks offline na árvore curada, hashes protegidos e links ao conjunto exato verificados.
- [x] Bootstrap de quatro arquivos em main e feature/draft PR revisada publicados; sem merge.
- [x] SHAs/conteúdo/templates/PR e runs/checks CI reais confirmados no commit inicial.
- [ ] Reconciliação do Project /3 e vínculos das mesmas Issues: trabalho separado do coordenador, somente após leitura suportada, sem IDs fabricados ou ampliação de escopos; esta correção não altera Project/Issues.

Aceite: software offline verificado separadamente da validade econômica/contábil/financeira, fontes protegidas intactas, privacidade revisada, conjunto exato e estado remoto observado. Bloqueio observado na preparação de Project CLI: read:project ausente; não renovar escopos/tokens nem duplicar cards.

### Encerramento comprovado da publicação inicial — 2026-10-02

Tasks 1–5 e revisão final concluídas. As instruções/checklists das Tasks 1–4 acima preservam o plano original e seus gates históricos; não são tarefas a executar novamente. A expansão financeira permanece desenho separado, sem nova coleta autorizada por este encerramento.

| Resultado | Evidência verificada |
| --- | --- |
| Bootstrap main, quatro arquivos | [commit 2c0d5a7](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/2c0d5a766cc9ea197b37a0a062c5efb124bcbd02) |
| Feature inicial, 119 arquivos / 808.531 bytes | [commit 00d6fe4](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/00d6fe46828955cfde9db4d2de1377c0fe20ff2b) |
| PR aberto em rascunho, base main | [Publicação do piloto e da fundação](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1) |
| CI push e pull_request no commit inicial | [push: sucesso](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37044529701); [PR: sucesso](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37044656911) |
| Planejamento da expansão, não implementação | [Planejar expansão 2010–2026 e atualização](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) |

Os runs comprovam o commit inicial, não commits posteriores; cada atualização exige checks próprios. O manifesto auditado permanece snapshot imutável daquela publicação. A fonte corrente de estado remoto é o GitHub; não inferir sincronização de todo o Project, merge, validade metodológica ou base histórica completa deste registro. Licença própria não escolhida e notices MIT preservados. O bloqueio anterior de aprovação da publicação foi resolvido pela autorização direta específica do usuário.

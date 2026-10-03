# Workflow obrigatório de Issues — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Cada Issue aberta explicita domínio, workflow/skills, nomenclatura, labels e pendências; agentes seguem o escopo aprovado até revisão e integração sem lembretes rotineiros.

**Architecture:** AGENTS exige a entrada por Issue; o tracker referencia um guia operacional único. Templates indicam os campos obrigatórios; áreas classificam competências e dependências governam prontidão. GitHub Issues são autoridade de tarefas; Project /3 continua delegado a Zec.

**Tech Stack:** Markdown, SVG/PNG, GitHub Issues/PR/CI existentes; skills Matt, Superpowers, Feynman, Context7 e diagram-design disponíveis, respeitando limitações verificadas.

## Global Constraints

- Spec aprovada: [contrato de Issue](../specs/2026-10-03-issue-workflow-design.md). Issue real: [17](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/17). Base `4faea4770f57679f5b649543ff86ad1715ebf2f9`; branch `codex/issue-17-issue-workflow` no checkout autorizado.
- Somente documentação/templates e as mesmas Issues abertas; nenhum código de pipeline/checker, dado, licença upstream, runtime global, proteção ou Project alterado.
- O integrador da Issue 17 na branch `codex/issue-17-issue-workflow` reúne AGENTS/README/tracker/templates. Executor do guia escreve somente o novo guia; executor visual escreve somente SVG/PNG e usa fonte temporária ignorada. Revisores leem e reportam.
- Sem testes que repitam texto; links/coerência/diff e revisão independente para documentação. CI existente continua verificando integridade de software.
- User autorizou publicação e integração dentro do escopo aprovado, após revisão independente e checks; decisões metodológicas permanecem humanas.

## Allowlist exata

`AGENTS.md`, `README.md`, `.github/ISSUE_TEMPLATE/work-item.md`, `.github/pull_request_template.md`, `docs/architecture.md`, `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/workflow.md`, `docs/agents/assets/issue-workflow.svg`, `docs/agents/assets/issue-workflow.png`, `docs/superpowers/specs/2026-10-03-issue-workflow-design.md`, `docs/superpowers/plans/2026-10-03-issue-workflow.md`.

Extensão solicitada por João após o primeiro lote: organização estrutural no `docs/architecture.md` existente, impacto estrutural em Issue/PR/guia e conferência pelo revisor. Sem mover arquivos históricos, editar CI ou instalar enforcement automático. Padrão claro da skill escolhido explicitamente; gate de estilo resolvido.

## Task 1: Contrato e entrada operacional

**Files:** spec/plano acima; novo guia `docs/agents/workflow.md`; AGENTS, README, tracker, triage-labels e templates.

**Consumes:** decisões aprovadas; catálogo instalado de skills; quatro dimensões de labels e cinco tipos de título.
**Produces:** entrada e guia coerentes, com matriz área/domínio/skill, workflows específicos e autonomia delimitada.

- [x] Incorporar nomenclatura, cardinalidade/semântica de labels e diagram-design na spec.
- [x] Escrever guia único: contrato obrigatório; seleção/invocação real; perfis; prontidão; execução/revisão/integração.
- [x] Integrador atualizar entradas/templates por links e instruções precisas; substituir regras antigas conflitantes sem apagar histórico de entregas.
- [x] Verificar links relativos, escopo e consistência; revisão independente do lote documental.
- [x] Acrescentar destinos/responsabilidades na arquitetura existente e impacto estrutural/revisão em AGENTS/guia/templates, conforme solicitação posterior.

## Task 2: Documentação visual publicável

**Files:** `docs/agents/assets/issue-workflow.svg` e `.png`; embed no guia. Fonte temporária local fora do manifesto público.

**Consumes:** contrato; diagram-design instalada; escolha de estilo do primeiro uso.
**Produces:** SVG acessível e PNG legível que representam fielmente disponibilidade e paralelismo.

- [x] Ler guia de estilo/type/semântica/export; usar escolha de estilo do usuário.
- [x] Renderizar fluxo com contrato, guard de prontidão, bloqueio, duas execuções da mesma área, revisão e conclusão contextual.
- [x] Exportar SVG e PNG; inspeção visual; conferir ausência de scripts/recursos externos e links de embed. Entregar somente SVG/PNG.

## Task 3: Reconciliação das mesmas Issues

**Remote scope:** Issues abertas 2, 3, 14, 16, 17 e labels deste repositório. Sem alteração no analysis ou no Project.

**Consumes:** docs revisadas; leitura fresca de títulos/corpos/labels e bloqueios reais.
**Produces:** títulos e quatro dimensões corretas, domínio/workflow/skills explícitos e prontidão verdadeira.

- [x] Ler catálogo; criar somente labels aprovadas que faltarem. Preservar labels informativas fora da migração.
- [x] Preparar corpos/labels/títulos completos, preservando evidência/histórico. Não promover pesquisas a implementação nem aprovar método humano.
- [x] Aplicar com leitura prévia e verificar campos/cardinalidades remotamente. Contrato atual fica na Issue; história datada permanece identificada.

## Task 4: Revisão, publicação e integração

**Files:** allowlist acima; descrição de PR e registros públicos das mesmas Issues.

- [ ] Revisão independente de escopo, semântica, instruções e visual no head exato; tratar achados antes de merge.
- [ ] `git diff --check`; checks documentais e CI existente. Não repetir suíte local por alteração exclusiva de texto/imagem.
- [ ] Publicar PR ligado à Issue 17, anexar à conversa, confirmar checks do head e integrar conforme autorização.
- [ ] Conferir CI pós-merge, sincronizar main local/remota e registrar entrega na Issue 17. Delimitar pendências anteriores/futuras do checker sem afirmar enforcement remoto concluído.

## Evidência de conclusão

Este arquivo é o snapshot de planejamento/execução anterior à revisão final e integração. Estado corrente e evidência de conclusão ficam na mesma Issue 17 e no PR real, evitando um tracker paralelo.

Registros frescos em Issue/PR: head/base/manifesto, revisão, validação de links e visual, labels/contratos conferidos, checks e merge. Conclusão deste lote não encerra escolhas de #3, gaps de #14/#16 ou instalação futura de runner/contratos concretos do checker.

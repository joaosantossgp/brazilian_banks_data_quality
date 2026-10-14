# Reorganização documental — plano de implementação

> **For agentic workers:** executar com revisão independente por fatia, conforme workflow do projeto. Usar `executing-plans` para a edição pelo integrador e `requesting-code-review` para revisores independentes.

**Goal:** tornar o projeto compreensível para autor/orientador e operacional para agentes, com bibliografia comentada e desenho parcial fiel.

**Architecture:** entradas curtas remetem aos responsáveis existentes; consultas detalhadas e histórico ficam em destinos documentais existentes. Sem alteração de software/dados.

**Tech Stack:** Markdown, SVG/PNG e ferramentas locais existentes para renderização/links.

**Spec:** [desenho aprovado](../specs/2026-10-13-monograph-documentation-design.md).

## Restrições globais

Issue [109](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/109), base `f93d37f17898d69713d06f07bb393eb1f2444331`, branch `codex/monograph-docs-20261013`; Root integrador. Sem nova coleta financeira, edição de dados/código/CI/108, outro computador ou Project. Documentação pede verificação de links/coerência/escopo e revisão de domínio, sem testes que repitam texto. Não transferir PASS de checkpoints para SHA posterior.

## Fatia A — contrato e decisão parcial

Paths: esta spec/plano e `docs/engineering/institution-type-indicator-methodology-20261012.md`.

- [ ] Registrar a decisão de 2026-10-13, preservando a de 2026-10-12 como histórico.
- [ ] Conferir deltas, links e aderência à conversa/Issue; solicitar revisão independente.
- [ ] Corrigir achados antes de iniciar a fatia B; registrar commit/resultado na Issue.

## Fatia B — referências e linguagem

Criar `REFERENCES.md`; modificar `GLOSSARY.md`. Dependência: A aprovada.

- [ ] Organizar fontes já presentes na monografia e pesquisas existentes por papel, com limites de consulta e localizadores.
- [ ] Mapear lacunas de indicadores por atividade, estatística, índices/normalização/ponderação/robustez; não adotar método.
- [ ] Reescrever verbetes conceituais em português por tema e preservar as distinções anteriores.
- [ ] Conferir URLs primárias/localizadores e links; revisão independente antes de ampliar.

## Fatia C — entradas, consultas e visual

Modificar `README.md`, `AGENTS.md`; criar `docs/engineering/local-queries-20261013.md`, `docs/agents/operational-history-20261013.md`, `docs/agents/assets/monograph-research-map-20261013.svg` e `.png`. Modificar apenas destinos/responsabilidades na tabela de `docs/architecture.md`. Dependência: B aprovada.

- [ ] Preservar AGENTS anterior no histórico com precedência explícita e links ajustados.
- [ ] Reaproveitar comandos do README no guia, separando consulta atual de reprodução/portal histórico.
- [ ] Explicar propósito, mapa e limites no README; manter âncoras referenciadas por docs existentes.
- [ ] Criar mapa claro 1200×640, inspecionar SVG e PNG, embutir com texto alternativo.
- [ ] Conferir links/âncoras e preservação de todos os paths fora da allowlist; revisão independente.

## Fatia D — composição e integração

- [ ] Conferir inventário final, ausência de corpos privados e diff estrutural finito.
- [ ] Revisar o SHA final e corrigir/revalidar deltas se necessário.
- [ ] Publicar PR vinculada à 109; conferir checks do head e integrar conforme autorização vigente.
- [ ] Conferir CI pós-merge e ancestralidade; atualizar 109/3/2 sem encerrar lacunas metodológicas.

Checkpoints e resultados efetivos ficam na Issue 109; as caixas descrevem o plano e não certificam execução.

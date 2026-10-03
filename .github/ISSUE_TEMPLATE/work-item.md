---
name: Trabalho técnico
about: Tarefa delimitada com contrato de escopo, aceite e evidência
title: '[Entrega] '
labels: 'kind:task,status:needs-triage'
assignees: ''
---

## Problema e resultado esperado
Descreva o comportamento observável; ligue spec/plano existentes, sem duplicá-los.

Título obrigatório: `[Tipo] Verbo + resultado ou recorte`. Tipos: Mapa, Decisão, Pesquisa, Entrega, Governança. Ajuste `kind:*` ao tipo: map, decision, research, task, governance.
Labels obrigatórias: exatamente uma `kind:*`, uma `role:*`, uma `status:*` e ao menos uma `area:*` do [catálogo](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/agents/workflow.md). Defaults acima não completam a triagem; preencher role/áreas antes de executar.

## Domínio e áreas
Área(s): research / domain / data / docs / infra / governance. Explicite conceitos, entidades, fontes, unidades/janelas/perímetros relevantes, restrições e refs ao glossário/ADRs/spec. Se não aplicável, justifique. Áreas classificam competências, não dependências nem filas exclusivas.

## Frente, responsável e base
- Frente e Issue real; se local: "não publicada — tarefa local" + brief existente.
- Responsável identificável e uma role principal: research / implementation / review / integration.
- Área(s) e domínio preenchidos acima; labels não são ACL.
- Branch proposta, branch base e SHA revisada; destino separado quando houver concorrência.
- Versão do contrato na política confiável; vínculo PR→tarefa antes do check.

## Escopo de arquivos e ownership
- Impacto na arquitetura: nenhum + motivo, ou inventário de arquivos/pastas criados/movidos/removidos, destino canônico e responsabilidade. Seguir [organização estrutural](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/architecture.md#organização-dos-arquivos-e-pastas); pasta nova exige justificativa, estrutura fora do escopo exige decisão antes de escrever.
- Allowed paths: lista exata; subárvore somente quando aprovada, terminada em `/`.
- Forbidden paths: bruto, artefatos aceitos, skills upstream e exclusões aplicáveis.
- Shared paths e integrador único: cada arquivo e owner do handoff, também com allowlist limitada.
- Controles sensíveis (CI, política/checker, templates, contratos): justificar e reservar para integração.
- Renames: origem e destino; deletes: cada path removido. Labels/PR não ampliam allowlist.

## Workflow e skills obrigatórios
Preencher a sequência adequada ao resultado, com entradas, entregáveis e gate de saída. Referenciar [workflow único](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/agents/workflow.md); usar somente as etapas necessárias.

| Etapa | Skill (família/identificador) | Obrigatória ou condicional + gatilho | Motivo / entrada → entregável / gate | Mecanismo disponível ou limitação |
|---|---|---|---|---|
| Preencher | Preencher | Preencher | Preencher | Preencher |

Matt direciona pesquisa/spec/tickets; Superpowers desenho/plano/TDD/debug/review/verificação. Feynman é condicional; Context7 exige versão usada. Visual: diagram-design disponível, SVG/PNG embutidos e alternativa textual; HTML temporário excluído. Presença/testes não provam invocação; skill ausente exige fallback explícito, sem instalação implícita.

## Dependências e prontidão
Listar bloqueador real, link, entrada faltante, responsável pelo desbloqueio e evidência para resolvê-lo; ou declarar **nenhuma pendência externa para iniciar**, com verificação. Separar vínculos de contexto de bloqueadores e etapas internas futuras.

Estado operacional único: needs-triage / ready / blocked / in-progress / in-review / done. `status:ready` exige contrato completo, escopo aprovado e dependências satisfeitas; ausência de blocked não basta. Issues prontas podem avançar em paralelo na mesma área, com ownership compatível. Claim registra executor/branch/paths e muda para in-progress.

## Critérios de aceite
- [ ] Resultado verificado com evidência correspondente ao escopo.
- [ ] Diff completo corresponde à allowlist, sem conflitos de ownership ou dependências abertas.
- [ ] Estados desconhecidos, limitações e decisões humanas pendentes explícitos.
- [ ] Revisão independente e handoff de shared paths documentados.
- [ ] Documentação atualizada por referência, sem outro tracker.
- [ ] Inventário do diff e destinos canônicos conferidos na revisão independente; arquitetura/ADR atualizados quando a estrutura ou responsabilidade mudarem.

## Validação e evidência
Registre comandos, resultados e links aos artefatos. Separe teste de software de validação econômica, contábil e financeira.
Registre base/head e patch/inventário completo incluindo renames/deletes, checks executados e não executados.
Checker começa em observação, não required; não autentica autoria nem autoriza merge/publicação.

## Estado de entrega
Declare o que foi validado localmente e o que foi publicado; inclua links remotos somente após confirmação.
Coordenação privada fica fora do repo; material público usa Issue/frente/branch e evidência sanitizada.
Dentro do escopo aprovado: executar, revisar e integrar após checks pertinentes e revisão independente; João decide mudanças de escopo ou método. Project /3 fica com Zec.

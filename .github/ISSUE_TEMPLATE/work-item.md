---
name: Trabalho técnico
about: Tarefa delimitada com contrato de escopo, aceite e evidência
title: ''
labels: ''
assignees: ''
---

## Problema e resultado esperado
Descreva o comportamento observável; ligue spec/plano existentes, sem duplicá-los.

## Frente, responsável e base
- Frente e Issue real; se local: "não publicada — tarefa local" + brief existente.
- Responsável identificável e uma role principal: research / implementation / review / integration.
- Área(s): converter / contract-2025 / academic-indicators. Labels são orientativas, não ACL.
- Branch proposta, branch base e SHA revisada; destino separado quando houver concorrência.
- Versão do contrato na política confiável; vínculo PR→tarefa antes do check.

## Escopo de arquivos e ownership
- Allowed paths: lista exata; subárvore somente quando aprovada, terminada em `/`.
- Forbidden paths: bruto, artefatos aceitos, skills upstream e exclusões aplicáveis.
- Shared paths e integrador único: cada arquivo e owner do handoff, também com allowlist limitada.
- Controles sensíveis (CI, política/checker, templates, contratos): justificar e reservar para integração.
- Renames: origem e destino; deletes: cada path removido. Labels/PR não ampliam allowlist.

## Dependências e skills por etapa
Tarefas bloqueadoras, evidência de conclusão e handoffs; usar matriz do tracker existente.
Skills necessárias, motivo e forma de invocação disponível; declarar runtime/tooling ausente.
Matt direciona pesquisa/spec/tickets; Superpowers desenho/plano/TDD/debug/review/verificação.
Feynman é condicional; Context7 exige versão usada. Presença/testes não provam invocação.

## Critérios de aceite
- [ ] Resultado verificado com evidência correspondente ao escopo.
- [ ] Diff completo corresponde à allowlist, sem conflitos de ownership ou dependências abertas.
- [ ] Estados desconhecidos, limitações e decisões humanas pendentes explícitos.
- [ ] Revisão independente e handoff de shared paths documentados.
- [ ] Documentação atualizada por referência, sem outro tracker.

## Validação e evidência
Registre comandos, resultados e links aos artefatos. Separe teste de software de validação econômica, contábil e financeira.
Registre base/head e patch/inventário completo incluindo renames/deletes, checks executados e não executados.
Checker começa em observação, não required; não autentica autoria nem autoriza merge/publicação.

## Estado de entrega
Declare o que foi validado localmente e o que foi publicado; inclua links remotos somente após confirmação.
Coordenação privada fica fora do repo; material público usa Issue/frente/branch e evidência sanitizada.

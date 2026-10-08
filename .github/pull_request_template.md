## Problema e comportamento resultante
Descreva o trigger e a mudança observável; ligue a Issue e a spec aplicáveis.

## Contrato de escopo e ownership
- PR→tarefa e versão da política **já na base confiável**:
- Frente, responsável, role principal e áreas; labels não são ACL:
- Branch/base SHA e head SHA exatos; branch corresponde ao contrato:
- Allowed/forbidden paths; shared paths e integrador com allowlist limitada:
- Dependências e evidência dos handoffs concluídos:
- Título/tipo e labels obrigatórias da Issue; domínio, workflow/skills definidos e prontidão conferida:

## Diff completo
Liste added/modified/removed/renamed; origem e destino em renames, cada path em deletes.
Impacto na arquitetura da Issue e conformidade com [destinos canônicos](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/architecture.md#organização-dos-arquivos-e-pastas): justificar novos arquivos/pastas e registrar atualização de arquitetura/ADR quando necessária. Revisão independente confere essa estrutura junto ao inventário real do diff.
Declare conflitos e alterações em CI, política/checker, templates ou contratos sensíveis.
O PR não amplia sua própria autorização; compare com política e validator da base.

## Checkpoints de revisão e testes parciais
Identifique a fatia integrável entregue e suas dependências/handoffs. Se várias fatias permanecerem na mesma PR, justificar a transição indivisível; não guardar a primeira revisão para o conjunto inteiro. Seguir o [workflow](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/agents/workflow.md#revisões-e-testes-por-fatias).

| Fatia / resultado | Base e head ou snapshot/hashes revisados | Checks / resultado / limitações | Revisor / verdict / achados resolvidos | Evidência na Issue ou handoff |
|---|---|---|---|---|
| Preencher | Preencher | Preencher | Preencher | Preencher |

Registrar falhas originais e correções; passes isolados posteriores não substituem o resultado global. Explicitar os deltas após os checkpoints e a revisão final de composição/inventário/SHA; confirmar os checks finais pertinentes. Não declarar uma revisão antiga como aprovação automática do head atual.

## Validação
Registre checks executados e evidências; declare limitações e checks não executados.
Checker: observação, verdict/erros, versão, base/head; não required nesta fase.
Registre revisão independente e skills efetivamente usadas; teste não prova invocação de skill.
Separe integridade de software de rigor econômico, contábil e financeiro.
Se houver documentação visual, entregar SVG/PNG embutidos em Markdown, alternativa textual e evidência da inspeção; HTML de renderização permanece temporário.

## Escopo de revisão
Identifique mudanças de contrato, dados/fontes, unidades/perímetros ou decisões humanas afetadas. Confirme a correspondência ao plano autorizado.
O integrador resolve shared paths preservando conteúdo das frentes. Declare estado local/revisão/remoto confirmado.
Este template não ativa ruleset, proteção, CODEOWNERS exigido, permissões ou credenciais.
Conforme o [workflow](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/agents/workflow.md), integrar dentro do escopo aprovado após checks e revisão independente; João decide mudança de escopo/método. Project /3 é acompanhado por Zec.

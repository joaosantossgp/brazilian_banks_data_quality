# Documentação de domínio

Layout **single-context**: um [GLOSSARY.md](../../GLOSSARY.md) na raiz e decisões em [docs/adr/](../adr/). Este arquivo contém regras de consumo; não repete definições, specs ou estado de tarefas. O [tracker único](issue-tracker.md#configuração-matt-aplicada) registra o setup e o [AGENTS](../../AGENTS.md#agent-skills) é a entrada operacional.

Antes de discutir/nomear conceitos, ler o glossário e somente os ADRs pertinentes à frente. Usar a linguagem canônica nos títulos de Issue, hipóteses, propostas e testes. O [ADR DuckDB/Parquet](../adr/0001-duckdb-parquet.md) orienta o conversor; não reinterpretar suas escolhas por nome de skill.

Consumo de documentos não é invocação de Modelar domínio — `/domain-modeling`. Usar essa skill quando conceitos ou decisões forem realmente alterados; conceitos resolvidos vão ao glossário, sem detalhes de implementação. Decisões difíceis de reverter, surpreendentes sem contexto e com trade-off real podem gerar ADR numerado após conferir o existente. Não criar ADR/estrutura por rotina nem outra spec para a mesma decisão.

Se uma proposta conflitar com ADR/spec, explicitar conflito, motivo, evidência e autoridade para reabertura; nunca sobrescrever silenciosamente. Ausência de arquivo opcional não exige scaffold antecipado; consultar AGENTS/spec e criar apenas quando houver decisão autorizada. Não criar GLOSSARY-MAP ou contexts adicionais sem sinal e desenho de monorepo.

Financial IF.data, metadados CVM/B3, perímetros, tokens ausentes e decisões acadêmicas continuam nos contratos/glossário existentes. A escolha humana de método/amostra não é promovida por skill, labels ou teste. Matt não substitui Superpowers no desenho/plano/TDD/debug/review/verificação nem os limites condicionais de Feynman/Context7.

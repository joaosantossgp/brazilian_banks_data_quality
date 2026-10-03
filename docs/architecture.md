# Arquitetura e contratos

## Referência de decisões

O contrato aprovado é a [fundação de governança, pesquisa e rigor](superpowers/specs/2026-10-02-governance-research-design.md); a execução documental segue o [plano autorizado](superpowers/plans/2026-10-02-governance-foundation-plan.md). Termos ficam no [glossário](../GLOSSARY.md), tarefas no [tracker](agents/issue-tracker.md) e ferramentas/proveniência no [registro de tooling](engineering/research-tooling-20261002.md). README é entrada humana; AGENTS é entrada operacional. Esta arquitetura resume os contratos, sem duplicar a spec.

## Organização dos arquivos e pastas

Este é o contrato estrutural do projeto, solicitado em 2026-10-03. Toda Issue usa o [workflow](agents/workflow.md) e declara seu impacto na arquitetura antes de criar, mover ou remover arquivos. O agente inspeciona apenas a árvore pertinente, escolhe o destino canônico e registra paths completos relativos ao repositório na allowlist. A estrutura existente é a referência; pasta nova precisa de responsabilidade concreta, conteúdo previsto e motivo para não usar um destino já existente.

| Destino canônico | Responsabilidade e limites |
|---|---|
| Raiz: `README.md`, `AGENTS.md`, `GLOSSARY.md`, `.gitignore`, manifests de dependência existentes | Entradas, linguagem do domínio e configuração do projeto. Novos documentos temáticos vão em `docs/`; não acrescentar relatórios ou scripts avulsos na raiz. |
| `bank_quality/` | Código reutilizável do pipeline e contratos de dados; aquisição, arquivo/proveniência, inventário, cobertura, metadados, replay e Parquet. Reutilizar o módulo responsável, com dependências explícitas; evitar cópias de lógica em scripts. |
| `scripts/` | Entradas operacionais/CLI, diagnósticos e verificações delimitadas; lógica reutilizável pertence ao pacote. Nome descritivo consistente com os scripts existentes. |
| `tests/`, `tests/fixtures/` | Verificação de comportamento/integridade e fixtures offline pertinentes. Não misturar fixtures sintéticas com dados financeiros observados nem criar testes que só reproduzam documentação. |
| `docs/adr/` | Decisões arquiteturais motivadas, numeradas e ligadas à tarefa. Mudança de pasta pequena não exige ADR por rotina; mudança de camada/responsabilidade exige decisão registrada. |
| `docs/agents/` e `docs/agents/assets/` | Governança operacional e seus visuais SVG/PNG; uma entrada por contrato, referências em vez de cópias. |
| `docs/engineering/` | Pesquisa técnica, evidência/limites de execução e ledgers datados. Método econômico/contábil/financeiro conserva fontes e autoridade humana. |
| `docs/superpowers/specs/`, `docs/superpowers/plans/` | Specs e planos rastreáveis, nomeados com data e assunto conforme o padrão existente. |
| `.github/` | Workflows, templates e política de governança existentes. Controles compartilhados têm integrador e allowlist próprios. |
| `.agents/skills/`, `third_party/` | Skills locais selecionadas e registros/licenças upstream. Não duplicar skills globais nem editar cópias upstream por conveniência. |
| `reports/` | Relatórios versionados já aceitos e sanitizados; nova publicação requer destino/aceite na Issue. Saídas temporárias não entram aqui automaticamente. |
| `data/raw/`, `data/derived/`, `data/runs/`, `data/curated/` | Dados locais ignorados, com contratos de imutabilidade/proveniência e destino de execução novo quando exigido. Não mover bruto ou sobrescrever artefatos aceitos para organizar pastas. |
| `.scratch/`, `.superpowers/`, `.tools/`, `.playwright-cli/`, `.venv/`, `.worktrees/` | Preparação, evidência privada, ferramentas e ambientes locais ignorados. Não são trackers públicos nem destinos de entrega. |

### Entrada, revisão e integração estrutural

1. **Issue:** preencher `Impacto na arquitetura: nenhum` com motivo, ou listar arquivos/pastas criados, movidos ou removidos, responsabilidade/destino canônico, dependências, compartilhamentos e documentação afetada. Isso complementa a allowlist; uma área ou skill não autoriza criar estrutura.
2. **Execução:** conferir AGENTS, esta seção e o contrato da tarefa. Usar o destino existente e nomes consistentes. Evitar pastas vazias, módulos genéricos sem dono, trackers duplicados ou infraestrutura para componentes ainda não aprovados. Colisão concreta exige handoff.
3. **Revisão independente:** comparar inventário real do diff (`git diff --name-status BASE HEAD`, ou snapshot equivalente) com a Issue e os destinos acima, incluindo origem/destino de renames e deletes. Verificar responsabilidade, dependências, exclusões/artefatos locais e atualização documental; achar código correto não dispensa essa conferência.
4. **Integração:** aceitar o lote após conformidade estrutural e checks pertinentes. Se a mudança aprovada altera estrutura/responsabilidades, atualizar esta seção e o ADR aplicável no mesmo lote. Nova raiz ou mudança de camada não prevista no escopo aprovado exige decisão de escopo antes da escrita.

Esse gate é uma obrigação do executor/revisor/integrador e dos templates. O checker atual de paths é offline em observação; ainda não existe um check automático de organização de pastas na CI. Enforcement adicional precisa de tarefa própria, regra reproduzível e regressões antes de ser alegado como instalado. A organização atual não pede migração dos arquivos históricos; reorganização futura deve ser uma entrega delimitada com inventário, preservação e revisão próprios.

## Comportamento implementado

- `bank_quality/archive.py` conserva respostas/proveniência e verifica corpos por hash.
- `ifdata.py` e `portal.py` implementam aquisição limitada IF.data/OData e portal oficial com guardas; não são um coletor histórico geral.
- `inventory.py` e `coverage.py` inventariam valores, estados e cobertura dos snapshots obtidos.
- `metadata.py` trata evidência cadastral/listagem temporal sem transformar status atual em fato histórico.
- `replay.py` reproduz derivados a partir do bruto verificado.

O código cobre lotes **individual/Resumo 201012, 202312 e 202412**. O padrão original 201012/202412 permanece; 202312 foi uma expansão explícita portal-only, sem tentativa OData. O [ledger de expansão](engineering/expansion-execution.md) registra 40.904 observações, 52 corpos verificados, 7 artefatos idênticos e limitações; o [ledger original](engineering/pilot-execution.md) preserva o piloto e suas decisões. Reproduzir não significa coletar novamente.

Corpos/manifests e índices locais → verificação de integridade → inventários/cobertura/metadados → replay/relatórios de evidência. Arquivos brutos não são publicação automática; os destinos de replay devem preservar derivados aceitos. Comandos offline estão no [README](../README.md#comandos-locais-verificados).

## Base alvo, ainda não implementada

A camada de análise local foi decidida e implementada inicialmente sobre o piloto existente: [DuckDB + Parquet](adr/0001-duckdb-parquet.md), com [contrato offline](superpowers/specs/2026-10-03-offline-parquet-design.md) e [medidas/limites](engineering/offline-parquet-20261003.md). `parquet.py` captura os sete arquivos do inventário, preserva as colunas originais e os complementos, acrescenta DECIMAL após perfil e grava Parquet comprimido por referência. Um coordenador reserva o destino; manifesto escrito por último aceita o conjunto. Falha mantém arquivos para diagnóstico sem aceite; reuso verifica conteúdo e hashes. Consultas abrem a lista explícita do snapshot em DuckDB em memória. Essa implementação não estende a aquisição histórica nem define o modelo econômico final.

Aquisição IF.data → bruto imutável/versionado → inventários por referência/perspectiva/relatório → metadados temporais CVM/B3 e vínculos comprovados → recortes documentados para monografia e outros projetos.

A direção técnica é trimestral 2010–2026 com atualização; **financeiro principal**, **prudencial** e **individual complementares**, separados. Não emendar perímetros, regimes ou conceitos por nome. Registro CVM, listagem e identidade são atributos distintos; desconhecido não significa negativo. Financeiro vem somente de IF.data; CVM/B3 não acrescentam observações financeiras.

Relatórios/variáveis, modelo de consulta, vínculos e política detalhada de revisões/validação 2025 exigem desenho separado. A amostra acadêmica é filtro posterior, sem limitar armazenamento; a monografia conserva seu texto atual 2010–2024. Decisões metodológicas, unidade final, holdings e elegibilidade temporal cabem a João/orientador. As [notas de desenho](engineering/brainstorming-2010-2026-20261002.md) conservam aprovações e perguntas abertas; não inferir que a direção aprovada executou a expansão.

## Aceite e limites

Testes de software verificam comportamento/integridade; validade **econômica, contábil e financeira** exige definições e evidência. Fórmulas/componentes, unidades, janelas, perímetros/regimes, versões, quebras, ausências e limitações precisam ser rastreáveis conforme a spec. Evidência de poucos períodos não valida todo o histórico; os oito vínculos do [dossiê temporal](engineering/capital-aberto-identity-dossier.md) continuam desconhecidos. Método/fórmula/arquitetura novos precisam de justificativa e fonte, sem cálculo ou escolha acadêmica inventados.

O repositório guarda contratos/código/evidência; Issue guarda tarefa/aceite/dependências; o Project existente /3 acompanha as mesmas tarefas. Resultado local, revisão aprovada e publicação confirmada são distintos. A fundação foi integrada pelo [PR 1](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1), commit `3234c20`, com [CI aprovado](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37048733876). Em 2026-10-03 João autorizou reconciliar, revisar e publicar branches/PRs do conversor e da governança, acompanhados nas Issues 15 e 17; os checks de cada head e o estado remoto precisam de confirmação própria. Proteções/segurança não serão alteradas e nova coleta não está autorizada. O [conjunto exato da fundação](engineering/governance-publication-proposal.md) conserva suas exclusões e licença própria ainda não escolhida.

Redação assistida é permitida sob direção/revisão/responsabilidade de João e fontes verificáveis/transparência aplicável; nenhum capítulo foi solicitado agora. A spec contém a decisão vigente e seus limites.

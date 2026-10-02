# Arquitetura e contratos

## Referência de decisões

O contrato aprovado é a [fundação de governança, pesquisa e rigor](superpowers/specs/2026-10-02-governance-research-design.md); a execução documental segue o [plano autorizado](superpowers/plans/2026-10-02-governance-foundation-plan.md). Termos ficam no [glossário](../GLOSSARY.md), tarefas no [tracker](agents/issue-tracker.md) e ferramentas/proveniência no [registro de tooling](engineering/research-tooling-20261002.md). README é entrada humana; AGENTS é entrada operacional. Esta arquitetura resume os contratos, sem duplicar a spec.

## Comportamento implementado

- `bank_quality/archive.py` conserva respostas/proveniência e verifica corpos por hash.
- `ifdata.py` e `portal.py` implementam aquisição limitada IF.data/OData e portal oficial com guardas; não são um coletor histórico geral.
- `inventory.py` e `coverage.py` inventariam valores, estados e cobertura dos snapshots obtidos.
- `metadata.py` trata evidência cadastral/listagem temporal sem transformar status atual em fato histórico.
- `replay.py` reproduz derivados a partir do bruto verificado.

O código cobre lotes **individual/Resumo 201012, 202312 e 202412**. O padrão original 201012/202412 permanece; 202312 foi uma expansão explícita portal-only, sem tentativa OData. O [ledger de expansão](engineering/expansion-execution.md) registra 40.904 observações, 52 corpos verificados, 7 artefatos idênticos e limitações; o [ledger original](engineering/pilot-execution.md) preserva o piloto e suas decisões. Reproduzir não significa coletar novamente.

Corpos/manifests e índices locais → verificação de integridade → inventários/cobertura/metadados → replay/relatórios de evidência. Arquivos brutos não são publicação automática; os destinos de replay devem preservar derivados aceitos. Comandos offline estão no [README](../README.md#comandos-locais-verificados).

## Base alvo, ainda não implementada

Aquisição IF.data → bruto imutável/versionado → inventários por referência/perspectiva/relatório → metadados temporais CVM/B3 e vínculos comprovados → recortes documentados para monografia e outros projetos.

A direção técnica é trimestral 2010–2026 com atualização; **financeiro principal**, **prudencial** e **individual complementares**, separados. Não emendar perímetros, regimes ou conceitos por nome. Registro CVM, listagem e identidade são atributos distintos; desconhecido não significa negativo. Financeiro vem somente de IF.data; CVM/B3 não acrescentam observações financeiras.

Relatórios/variáveis, modelo de consulta, vínculos e política detalhada de revisões/validação 2025 exigem desenho separado. A amostra acadêmica é filtro posterior, sem limitar armazenamento; a monografia conserva seu texto atual 2010–2024. Decisões metodológicas, unidade final, holdings e elegibilidade temporal cabem a João/orientador. As [notas de desenho](engineering/brainstorming-2010-2026-20261002.md) conservam aprovações e perguntas abertas; não inferir que a direção aprovada executou a expansão.

## Aceite e limites

Testes de software verificam comportamento/integridade; validade **econômica, contábil e financeira** exige definições e evidência. Fórmulas/componentes, unidades, janelas, perímetros/regimes, versões, quebras, ausências e limitações precisam ser rastreáveis conforme a spec. Evidência de poucos períodos não valida todo o histórico; os oito vínculos do [dossiê temporal](engineering/capital-aberto-identity-dossier.md) continuam desconhecidos. Método/fórmula/arquitetura novos precisam de justificativa e fonte, sem cálculo ou escolha acadêmica inventados.

O repositório guarda contratos/código/evidência; Issue guarda tarefa/aceite/dependências; o Project existente /3 acompanha as mesmas tarefas. Resultado local, revisão aprovada e publicação confirmada são distintos. Publicação só é afirmada após autorização e verificação remota. A publicação do conjunto revisado e o CI mínimo foram autorizados em 2026-10-02. O workflow offline está preparado localmente; execução/checks remotos seguem pendentes de confirmação. Proteções/segurança não serão alteradas e nova coleta não está autorizada. O [conjunto exato](engineering/governance-publication-proposal.md) registra exclusões e licença própria ainda não escolhida.

Redação assistida é permitida sob direção/revisão/responsabilidade de João e fontes verificáveis/transparência aplicável; nenhum capítulo foi solicitado agora. A spec contém a decisão vigente e seus limites.

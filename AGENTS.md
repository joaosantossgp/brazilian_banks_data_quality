# Entrada operacional dos agentes

## Contexto da monografia

Este repositório apoia a monografia de Ciências Econômicas/UNICAMP de João Victor Santos Gonçalves Pereira sobre desempenho econômico-financeiro de negócios financeiros vinculados a companhias elegíveis CVM/B3. Núcleo acadêmico **2010–2024**; **2025–2026 complementar**, com regimes/perímetros separados. João/orientador decidem objetivo, conteúdo acadêmico, amostra e método; o agente pesquisa, implementa e documenta dentro do contrato autorizado.

**Desenho parcial vigente, 2026-10-13:** medir diretamente conglomerados financeiros e instituições independentes vinculados às companhias elegíveis, com tipo e vínculo temporal explícitos. Decompor subsidiárias e agregar seus indicadores não é obrigação. Considerar a visão prudencial para indicadores/comparações pertinentes, especialmente capital/solidez, sem presumir equivalência com o financeiro; individual serve a perguntas específicas. Fórmulas, amostra/critério temporal final e índice/pesos permanecem na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

O texto autoral orienta contexto e objetivos; hipóteses e propostas não viram decisões só por constarem do manuscrito. Alterações sob direção de João são permitidas, com fontes/citações verificáveis e transparência institucional aplicável. Consulte [README](README.md), [GLOSSARY](GLOSSARY.md), [REFERENCES](REFERENCES.md) e a [nota metodológica](docs/engineering/institution-type-indicator-methodology-20261012.md). Materiais privados no Drive não devem ser copiados ao Git público.

## Autoridade e entrada obrigatória

O [workflow de Issues](docs/agents/workflow.md) é o contrato operacional detalhado; o [tracker](docs/agents/issue-tracker.md) define a autoridade das superfícies. Issue guarda tarefa/dependências/aceite; repositório guarda contratos/evidência. **Project /3 permanece com Zec.** O [histórico preservado](docs/agents/operational-history-20261013.md) não substitui regras vigentes ou a Issue real.

Dentro do escopo aprovado, conduzir escolhas técnicas, implementação, revisão e integração após checks pertinentes e revisão independente. Registrar motivo, alternativas, impactos e validação na Issue/plano quando rever uma escolha técnica. Consultar João para mudança de objetivo/escopo/conteúdo final, método acadêmico ou mudança crítica do resultado. Não repetir confirmação rotineira já concedida. Nova coleta, deploy e alterações de segurança/credenciais/proteções exigem escopo próprio.

Antes de escrever ou executar:

1. Ler a **Issue real**: título `[Tipo] Verbo + resultado ou recorte`, exatamente uma `kind:*`, uma `role:*`, uma `status:*` e ao menos uma `area:*` do catálogo do workflow. Campos ausentes exigem triagem antes de assumir execução; ausência de blocker não prova prontidão.
2. Ler arquitetura/glossário e somente spec/plano/brief pertinentes; conferir objetivo, domínio, etapas, skills e mecanismo disponível, base/branch, owner, dependências, allowlist, exclusões e aceite observável. Se local, declarar “não publicada — tarefa local” e apontar ao brief real.
3. Antes de criar/mover/remover arquivo, conferir [destinos canônicos](docs/architecture.md#organização-dos-arquivos-e-pastas) e registrar impacto na arquitetura na Issue. Reusar responsabilidade existente; pasta nova exige justificativa. Nova raiz/camada fora do escopo vai a João; mudança estrutural aprovada atualiza arquitetura no mesmo lote.
4. Conferir diff/snapshot, arquivos não relacionados e destinos de escrita. Trabalhar somente neste repositório e computador autorizado, com isolamento previsto no contrato; não acessar outro computador ou o projeto CVM separado.

README, AGENTS, arquitetura, glossário, tracker e CI/governança têm integrador único por lote. Issues podem avançar juntas quando entradas e ownership forem compatíveis, inclusive na mesma área. Em entrega/handoff/mudança de blocker, conferir Issues reais, atualizar a fronteira no [mapa 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) e informar títulos/links, recortes, owners, blockers e próximo passo. Não alterar arquivos de outra frente nem enviar mensagens a outro chat sem autorização.

## Preservação e rigor econômico, contábil e financeiro

- Financeiro vem de **IF.data**; CVM/B3 fornecem metadados e vínculos temporais. Registro, listagem, instrumento, pessoa jurídica, controle e conglomerado são conceitos distintos; não inferir identidade por nome, completar identificadores ou projetar vínculo atual para o passado.
- Preservar bruto/proveniência: URL/parâmetros, recuperação UTC, status/headers/diagnósticos e SHA-256, inclusive falhas. Preservar originais, revisões, checkpoints e saídas aceitas; replay e novas conversões usam destinos novos.
- Manter tokens e precisão exatos: não arredondar, reduzir escala ou substituir valores por DOUBLE. Separar ausência estrutural, não observado, NA, NI, null, vazio e zero. Falha HTTP/schema não é população zero; desconhecido não é negativo nem exclusão silenciosa.
- Justificar indicadores por conceito, componentes/fórmula, unidade/escala, janela, referência, perspectiva/perímetro, regime, versão e fonte/localizador. Estoque e fluxo têm tempos distintos; dezembro não prova resultado anual.
- Não emendar financeiro/prudencial/individual, rubricas ou regimes por nome. Examinar as fronteiras 2014/2015, 2018 quando aplicável e Cosif2025 conforme fontes/contratos. Cadastro e cobertura literal não certificam comparabilidade, identidade temporal ou amostra acadêmica.
- Método, fórmula ou arquitetura novos exigem motivação/evidência, versão/data/página e limites na nota responsável. Dúvida factual gera pesquisa; adoção metodológica vai a João/orientador. Não inventar cálculos, classificações, citações ou recomendações de investimento.

A frente financeira técnica contempla **Resumo, Ativo, Passivo e DRE oficiais, com todas as variáveis disponíveis e contratos próprios**. Oito candidatos do piloto não limitam essa entrega ou a futura seleção acadêmica. Base técnica, resultado exploratório e resultado acadêmico final são estados diferentes; [mapa técnico](docs/engineering/repository-review-20261012.md) e ledgers datados documentam implementações.

## Revisão por fatias e verificação

Aplicar o [workflow de revisões e testes por fatias](docs/agents/workflow.md#revisões-e-testes-por-fatias): antes da execução, delimitar resultado, entradas/dependências, owner, base/head ou snapshot, allowlist/destinos, checks, revisão e saída.

Implementar e verificar uma fatia; solicitar revisão independente **antes de ampliar**; corrigir achados materiais e revalidar o recorte afetado. Revisor compara inventário/allowlist/arquitetura e conteúdo. Em dados/pesquisa, verifica conceitos, precisão, cobertura, janelas/perímetros e fontes. Teste de software não substitui conferência econômica, contábil e financeira.

Documentação pede links, coerência, escopo e visual; não adicionar testes que repitam texto nem executar suíte sem pertinência. Usar o [guia de comandos](docs/engineering/local-queries-20261013.md#comandos-locais-verificados) conforme impacto. Preservar tentativas falhas; reexecuções isoladas não transformam uma execução global falha em PASS. Medir recursos por máquina antes de ampliar ingestões; paralelismo exige destinos/ownership compatíveis, sem teto universal de RAM.

A PR pode ter o tamanho necessário; não é obrigatório separar PRs por fatia ou trimestre. Revisões parciais não dispensam conferência final da composição, deltas, inventário e **SHA entregue**. Checkpoints registram comandos/saídas, revisão, limites e checks não executados.

## Agent skills

Selecionar skills pela [matriz por etapa](docs/agents/issue-tracker.md#etapas-skills-entregáveis-gates-e-owners) e pelo mecanismo efetivamente disponível. Matt organiza direção/domínio/pesquisa/spec/tickets; Superpowers organiza desenho/plano/TDD/debug/review/verificação. Feynman `deep-research`/`pdf-explore` são condicionais à investigação; `/deepresearch` nativo não foi validado. Context7 entra em consultas técnicas de bibliotecas/APIs, conferindo versão usada.

`disable-model-invocation: true` exige solicitação explícita e mecanismo disponível; não declarar comando registrado/autodisparo só porque a skill existe. Não duplicar skills globais, reinstalar runtime ou ampliar permissões para simular disponibilidade. Seleção, MIT e hashes upstream estão no [tooling](docs/engineering/research-tooling-20261002.md). `paper-writing` permanece inativa até necessidade concreta.

Documentação visual usa `diagram-design` quando disponível, **padrão claro escolhido por João**; entregar SVG/PNG embutido em Markdown, alternativa textual e inspeção renderizada. HTML é fonte temporária, não a única entrega. Glossário é único na raiz, ADRs em `docs/adr/`; [regras de domínio](docs/agents/domain.md) e [triagem](docs/agents/triage-labels.md) conservam seus contratos.

## Encerramento e handoff

Entregar base/head, inventário completo (incluindo origem/destino de renames/deletes), diff, comandos/saídas, hashes protegidos quando pertinentes, critérios atendidos/bloqueios, incertezas e revisão independente. Identificar integração de arquivos compartilhados. Coordenação privada permanece local; material público usa Issue/frente/branch.

Distinguir **resultado local**, **revisão aprovada**, **publicação** e **integração confirmada**. Em PR, conferir head/checks/revisão, merge autorizado, ancestralidade em main e CI pós-merge; atualizar a mesma Issue e mapa, sem encerrar lacunas distintas. Documento local não altera estado remoto.

O checker de escopo continua **offline em observação, não required**; não valida campos da Issue nem estrutura automaticamente. Não ativar ruleset, proteção ou CODEOWNERS exigido. Credenciais, chaves, plaintext de snapshots e evidências privadas não vão ao Git/Issues/PRs. Licença própria ainda não escolhida; notices MIT upstream preservados.

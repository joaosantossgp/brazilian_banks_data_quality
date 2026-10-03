# Contrato de Issue: domínio, workflow, skills e prontidão

Data: 2026-10-03. Frente: [Definir workflow e validar escopo de PR, Issue 17](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/17). Base de desenho: `main` `4faea4770f57679f5b649543ff86ad1715ebf2f9`. Status: desenho preparado para revisão escrita; implementação e alterações remotas desta revisão ainda não realizadas.

Complementa a [spec da fundação](2026-10-02-governance-research-design.md). O [tracker](../../agents/issue-tracker.md) continua sendo a referência operacional; [AGENTS](../../../AGENTS.md), [arquitetura](../../architecture.md), [glossário](../../../GLOSSARY.md) e ADRs conservam seus contratos. Este documento não é outro tracker.

## Direção acordada

Cada Issue deve informar obrigatoriamente o domínio das áreas envolvidas, seu workflow, as skills aplicáveis e suas dependências. Áreas classificam especialidades e orientam a seleção de skills; não dividem filas exclusivas nem determinam paralelismo. Uma skill pode servir a várias áreas e uma Issue pode ter várias áreas.

A disponibilidade para execução vem da prontidão explícita da Issue. Issues prontas podem avançar simultaneamente, inclusive na mesma área. Conflitos concretos de trabalho ou arquivos são registrados como dependência ou handoff, sem presumir conflito pela coincidência de labels.

João definiu autonomia dentro do escopo aprovado: executar, revisar e integrar após testes pertinentes e revisão independente aprovados; chamar João quando houver mudança de escopo ou decisão metodológica. Essa autonomia não elimina pendências de aquisição, fontes, permissões ou decisões humanas ainda não satisfeitas no contrato da tarefa.

## Contrato obrigatório em cada Issue

1. **Problema e resultado:** comportamento ou artefato observável, tipo de trabalho e links da spec/plano aplicáveis.
2. **Áreas e domínio:** labels de área, domínio concreto de cada área, conceitos/limites pertinentes e referências a glossário, arquitetura, ADR ou fontes. Uma label isolada não satisfaz esse campo.
3. **Workflow:** etapas em ordem; entrada, saída e condição de conclusão de cada etapa. Etapas opcionais têm condição explícita. A Issue deve ser compreensível sem reconstruir conversas.
4. **Skills por etapa:** família e identificador original, motivo de seleção, obrigatória/condicional, condição de uso, entregável e disponibilidade real. A Issue lista as skills selecionadas, não todo o catálogo.
5. **Execução:** responsável/perfil técnico, papel principal, branch/base, arquivos e destinos autorizados, exclusões e compartilhamentos que realmente afetam a tarefa. O executor não revisa sua própria implementação como revisão independente.
6. **Dependências e prontidão:** blockers com links e condição de resolução, informações ou decisões faltantes, ou declaração explícita de que não existem pendências para começar. Distinguir dependências externas de etapas internas do workflow.
7. **Aceite e evidência:** checks pertinentes, revisão independente e critérios de domínio quando aplicáveis; comandos/resultados, artefatos e links confirmados.
8. **Encerramento:** resultado local, revisão e publicação/integração identificados separadamente; Issue de pesquisa ou decisão pode concluir com artefato/decisão sem PR de código.

Tarefa pequena usa contrato curto e referências precisas. Não exige entrevista, pesquisa extensa ou uma nova spec quando o desenho necessário já está aprovado. Issues mapa descrevem a rota e apontam para tarefas executáveis; não são tratadas como implementações prontas por não possuírem blockers.

## Áreas e domínio das skills

Proposta de catálogo enxuto para a implementação, a ser aplicada de forma coordenada às Issues abertas:

| Área | Domínio | Skills pertinentes, conforme a tarefa |
|---|---|---|
| `area:research` | Evidência primária, bibliografia, proveniência e incertezas | Matt `research`; Feynman `deep-research` e `pdf-explore` |
| `area:domain` | Conceitos econômicos, contábeis e financeiros; unidades, janelas, perímetros e método | Matt `domain-modeling`, `grilling`, `grill-with-docs`; Feynman `pdf-explore` quando a prova exige PDFs |
| `area:data` | Aquisição autorizada, inventários, normalização, persistência e integridade dos dados | Superpowers `brainstorming`, `writing-plans`, `test-driven-development`, `systematic-debugging`, execução e revisão |
| `area:docs` | Specs, planos, contratos e documentação rastreável | Matt `to-spec`, `to-tickets`, `domain-modeling`; Superpowers `brainstorming`, `writing-plans`, revisão/verificação |
| `area:infra` | CI, ferramentas, dependências e ambiente do projeto | Superpowers desenho, plano, TDD/debug, revisão/verificação; Context7 para documentação técnica |
| `area:governance` | Entrada, decomposição, dependências, nomenclatura, responsabilidades e integração | Matt `triage`, `wayfinder`, `to-spec`, `to-tickets`; Superpowers planejamento, coordenação, revisão/verificação |

Esse mapeamento não manda executar todas as skills da linha. `area:converter`, `area:contract-2025` e `area:academic-indicators` são classificações existentes por frente; sua migração será explícita e preservará números, links e histórico. Roles existentes descrevem responsabilidade, separadamente de área e estado. Não criar uma label para cada skill nem atribuir labels a arquivos de skill como se fossem Issues.

## Workflow por natureza do trabalho

### Pesquisa

Matt `research` delimita a pergunta e as fontes. Feynman `pdf-explore` entra quando métodos/tabelas/citações dependem de múltiplas páginas; `deep-research` entra quando a investigação extensa o exige e seu workflow estiver operacional. Saídas: nota com fontes/localizadores, proveniência e desconhecidos; revisão independente das conclusões; registro do resultado na Issue. Questão metodológica passa para a decisão humana correspondente, sem converter hipótese em método aprovado.

### Entrega de software ou dados

Usar o desenho existente; aplicar Superpowers `brainstorming` somente quando houver comportamento/arquitetura ainda a definir. Matt `to-spec` consolida o desenho quando necessário; `to-tickets` decompõe entregas amplas com dependências reais; Superpowers `writing-plans` detalha execução com múltiplas etapas. Executar via `executing-plans` ou `subagent-driven-development`, com `test-driven-development` para código/correções. Falhas usam `systematic-debugging`. Concluir com `requesting-code-review`, tratamento de feedback via `receiving-code-review`, `verification-before-completion`, integração e CI pós-merge quando houver PR.

### Decisão metodológica

Matt `research` prepara evidência; `grilling`/`grill-with-docs` examinam alternativas quando necessário; `domain-modeling` registra o conceito/ADR pertinente após decisão. João/orientador escolhe. A saída é decisão datada e referenciada que libera ou mantém bloqueadas as tarefas dependentes. Autonomia de implementação não delega essa escolha ao agente.

### Governança ou documentação pequena

Ler contratos, propor/usar desenho delimitado, alterar somente os destinos autorizados, conferir links/coerência/escopo e obter revisão independente. Não exigir TDD ou suíte integral para texto que não muda comportamento de software. Mudanças no checker exigem regressões e verificação de código. Setup de skills ocorre apenas quando existe necessidade concreta, sem reinstalação recorrente.

## Exemplos de contrato por tarefa

Exemplos de seleção para as frentes existentes, sem afirmar mudança de estado remoto ou execução histórica dessas skills:

| Natureza e referência | Domínio e áreas propostas | Workflow e skills selecionadas | Pendência que deve ficar explícita |
|---|---|---|---|
| Pesquisa na frente [Contrato financeiro 2024/2025](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16) | `area:research` + `area:domain`; definições Cosif/IF.data, escala, janelas, perspectiva 1005 e rupturas | Delimitar evidência via Matt `research` → conferir fontes/PDFs via Feynman `pdf-explore` quando necessário → matriz de conceitos e desconhecidos → revisão independente → registrar resultado | Dicionário específico 202503 e ponte normativa não comprovados; cadastro 1005 bloqueia replay financeiro completo, sem impedir análise de metadados já disponíveis |
| Entrega exemplificada pelo [Conversor offline](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/15) | `area:data`; tokens/Decimal, estados de ausência, inventário, Parquet e proveniência | Ler spec/ADR → Superpowers `writing-plans` se exigir plano → TDD → execução → revisão independente → verificação → PR/CI/integração | Exige inventário e destino autorizados; não depende da ponte 2025 para converter o piloto individual. A Issue já encerrada permanece histórica |
| [Decisão de unidade e janela](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) | `area:domain`; população histórica, emissor/holding, unidade IF.data e período acadêmico | Matt `research` para evidência → `grilling` se alternativas precisarem exame → escolha de João/orientador → `domain-modeling` para registrar decisão aprovada → liberar dependentes | A escolha humana continua pendente; não apresentar implementação dependente como pronta. Preparar alternativas é trabalho distinto de tomar a decisão |

## Disponibilidade e invocação

O agente lê o contrato da Issue e seleciona as skills pertinentes antes de atuar, sem depender de João lembrar cada etapa. A evidência de execução registra as instruções/procedimentos realmente usados. Invocação de slash command, autodisparo e execução de runtime não são afirmados sem verificação.

Skills Matt com `disable-model-invocation: true` ou `allow_implicit_invocation: false` preservam metadados upstream. O workflow deve identificar a forma de uso autorizada e disponível; leitura/aplicação explícita de instruções sob direção do usuário não é apresentada como registro/autodisparo de comando. Se um mecanismo obrigatório estiver indisponível, registrar a pendência ou usar alternativa expressamente admitida na Issue, sem simular a skill.

O `/deepresearch` Feynman não está validado neste Codex. Não é requisito universal nem pretexto para instalar runtime. Quando necessário, registrar disponibilidade, ou usar pesquisa com ferramentas verificadas e proveniência se essa alternativa atender ao contrato aprovado. Presença dos arquivos não prova execução do workflow. Somente `deep-research` e `pdf-explore` permanecem na seleção Feynman atual; outras skills exigem necessidade e decisão próprias.

## Prontidão e execução em paralelo

- `status:ready`: contrato completo, escopo aprovado, dependências satisfeitas, recursos/entradas disponíveis e nenhuma pendência que impeça começar. Checks e revisão que serão produzidos durante a execução são etapas futuras, não blockers prévios por si só.
- `status:blocked`: falta de requisito concreto; informar blocker, evidência faltante e condição de desbloqueio. Issue sem estado ou com contrato incompleto não é presumida pronta.
- `status:in-progress`: tarefa pronta assumida por executor identificável. Antes de assumir, conferir estado atual para evitar execução duplicada.
- Revisão e integração seguem o workflow da Issue. Fechamento exige aceite verificável; pesquisa/metodologia pendente continua explícita.

Relações nativas de dependência/sub-issue serão usadas quando disponíveis e verificadas; links no corpo são fallback explícito. Estado e dependências são reconciliados antes de selecionar trabalho; labels antigas não substituem essa conferência. Issues prontas de qualquer área podem ser distribuídas. Reservar apenas arquivos realmente compartilhados; conflitos reais mudam a prontidão afetada. Checkouts/destinos isolados usam somente este repositório e computador autorizado, quando essa operação estiver contemplada no contrato; este desenho não cria checkouts adicionais.

O Project /3 continua com Zec. A execução atualiza as mesmas Issues e seus links; não cria tracker/Project concorrente nem envia mensagens a outros chats sem autorização.

## Implementação delimitada após revisão escrita

Atualizar AGENTS, tracker, template de Issue e referências de PR para exigir o contrato acima e uma entrada por tarefa que confira prontidão. Documentar matriz área/domínio/skill em um destino operacional único e referenciá-la. Aplicar nomenclatura `[Tipo] Verbo + resultado/recorte` às Issues abertas, preservando histórico; definir labels e completar seus contratos sem atribuir prontidão fictícia. Não reabrir nem reescrever entregas históricas concluídas apenas por mudar o template.

A primeira entrega usa os mecanismos existentes e conferência explícita de prontidão pelo agente. O checker de paths permanece observação offline; não será apresentado como validador dos campos da Issue. Não criar parser universal, serviço de orquestração, required check, ruleset ou mudança de credenciais/proteções neste lote. Caso haja uma lacuna de enforcement após o piloto, ela terá tarefa própria e evidência reproduzível.

## Aceite do workflow

1. Uma Issue de pesquisa, uma de implementação e uma de decisão possuem domínio, etapas e skills concretas, sem placeholders de contrato.
2. Duas tarefas prontas na mesma área podem ser selecionadas em paralelo; blocker real impede a afetada mesmo com labels corretas.
3. Issue sem domínio, workflow ou skills não é marcada pronta; ausência de `status:blocked` não basta.
4. Decisões metodológicas e aquisição não autorizada permanecem pendentes; revisão por agente é registrada como técnica, sem alegar aprovação humana/GitHub elegível.
5. Skills condicionais têm gatilho e alternativa/limitação explícitos; não exigir todo o catálogo nem alegar Feynman indisponível como executado.
6. Documentação, Issue e resultado remoto correspondem; revisões e checks citam o head efetivamente entregue. Dados, artefatos aceitos, upstream e Project são preservados fora do escopo.

## Referências técnicas

- [Skills no Codex: descoberta, invocação e metadados](https://learn.chatgpt.com/docs/build-skills): a seleção depende de descrição/contexto; política de invocação explícita é distinta da presença do arquivo.
- [Dependências de Issues no GitHub](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies): blockers representam requisitos reais entre tarefas.
- [Labels do analysis](https://github.com/joaosantossgp/analysis/labels): referência de separação entre área e prontidão, sem importar permissões, release ou lanes daquele repositório.

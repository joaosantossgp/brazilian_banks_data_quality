# Configuração local de pesquisa — 2026-10-02

Computador verificado: LAPTOP-U0J6PT8Q. Esta configuração é separada da implementação do produto, ainda em desenho. Não houve nova coleta financeira, commit, publicação, criação de credenciais ou alteração global.

## Matt e Superpowers

As nove skills Matt continuam instaladas sem alterações: wayfinder, grill-with-docs, to-spec, to-tickets, grilling, domain-modeling, setup-matt-pocock-skills, research e prototype. `/research` já existia; nenhuma cópia adicional foi criada. Os 36 arquivos do manifesto Matt conferem com os hashes registrados no revision `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`, preservando MIT. Fonte local: `third_party/mattpocock-skills/provenance.json`.

Superpowers global permanece disponível, incluindo brainstorming, writing-plans, TDD e verification-before-completion. Não foi instalado novamente. Matt organiza direção, perguntas, termos, specs e tarefas; Superpowers conduz desenho, plano, execução/revisão/verificação sob os gates aplicáveis. A presença das skills não aprova execução.

## Context7

Confirmados `resolve_library_id` e `query_docs`, ambos chamados com sucesso. A consulta de teste usou `/python/cpython`, documentação primária de `csv.reader`: leitura retorna strings por padrão e `newline=''` deve ser usado no arquivo. O Context7 retornou documentação de `main`; como o piloto usa Python 3.12, a informação também foi conferida na [documentação oficial Python 3.12](https://docs.python.org/3.12/library/csv.html). Documentação de outra versão não será tratada como contrato automaticamente compatível. Este teste verifica acesso à documentação, não a validade contábil do parser nem a execução de código novo.

## Feynman: seleção mínima local — duas skills ativas

A [documentação oficial](https://www.feynman.is/docs/getting-started/installation/) oferece scope Repo em `.agents/skills/feynman`. O instalador PowerShell foi baixado e inspecionado, mas não executado: substitui o destino existente e omite LICENSE. Para preservar arquivos e licença, copiamos somente os recursos correspondentes ao layout oficial, do arquivo do commit fixo do [repositório oficial](https://github.com/Companion-Inc/feynman/tree/e17f5fd0ea57775def66ebd2b16b40b39d3dc867).

- Release: **v0.5.22**; commit: `e17f5fd0ea57775def66ebd2b16b40b39d3dc867`.
- Arquivo-fonte SHA-256: `82dac00b137286edd72831308b2b07a01a45379df6835896d0dff5cc72bd25b2`.
- Instalador inspecionado SHA-256: `0dbeb009d1499a73b914fb460a673f4929773455bde7abab740de03852ff619b`.
- 16 SKILL.md, 11 prompts, AGENTS.md, CONTRIBUTING.md e LICENSE: **30 arquivos de origem, 70.870 bytes**, verificados byte a byte após a cópia. Esses hashes documentam a cópia recuperada, sem alegar assinatura ou checksum oficial de release.
- Os AGENTS.md e CONTRIBUTING.md do pacote ficaram dentro de `.agents/skills/feynman`; não substituíram a governança raiz. Licença MIT Companion, Inc. preservada no pacote e em `third_party/feynman/LICENSE`; manifesto em `third_party/feynman/provenance.json`.
- Nenhum terminal Feynman, runtime Node/Pi, Docker, pandoc, provider, chave ou login foi instalado/configurado.

**Correção solicitada por João:** o conjunto inicial de 16 era maior que o necessário. Após ler todas as descrições e instruções, ficaram ativas apenas:

- **deep-research:** corresponde ao pedido de investigação profunda técnico/econômico-contábil, com fontes e proveniência; uso condicional, pois `/deepresearch` ainda depende de expansão/runtime não disponível ou validado nesta sessão. O wrapper menciona researcher/verifier/reviewer; o prompt permite caminho direto para perguntas estreitas. Não instalar runtime para resolver essa limitação por suposição.
- **pdf-explore:** leitura/cruzamento de páginas, tabelas, notas e métodos em PDFs primários, conservando atribuição por página. O arquivo não exige terminal Feynman; usar ferramentas PDF já disponíveis conforme a fonte. A seleção não equivale a uma pesquisa PDF nova executada.

Preservados no ativo o prompt `prompts/deepresearch.md` e os recursos upstream AGENTS.md, CONTRIBUTING.md e LICENSE, sem mudança no conteúdo. Não se presume que o prompt ou outras skills substituam a integração de slash commands. Os recursos de governança do pacote continuam isolados da raiz do projeto.

**14 skills desativadas**, movidas sem exclusão para `third_party/feynman/inactive-20261002/skills/`: alpha-research, autoresearch, docker, eli5, literature-review, ml-training-recipe, paper-code-audit, paper-writing, preview, replication, research-review, session-log, session-search e source-comparison. Os dez prompts excedentes estão no mesmo backup em `prompts/`, fora de `.agents/skills` e `.codex/skills`. A licença e os 30 arquivos-fonte continuam verificáveis por hash. O manifesto atual aponta os caminhos ativos/inativos; `provenance-before-selection-20261002.json` preserva o estado anterior e `selection-20261002.json` documenta a decisão e dependências de cada skill.

Motivos: ML/experimentos/replicação/containers não fazem parte da tarefa atual; paper-writing não é necessária nesta fundação e não será reativada automaticamente; pesquisa comparativa curta e continuidade já cabem em Matt research e nos documentos existentes. Literatura/review genéricos acrescentariam wrappers ao fluxo profundo e à revisão já prevista; não são dependências declaradas das duas skills retidas. Preview adicionaria ferramentas sem necessidade para esta entrega. Alpha/sessões dependem de runtime/conta ausentes. Nenhuma skill biomédica existia nesta revisão; não foi adicionada. As nove skills Matt e Superpowers global permanecem iguais.

**Limite funcional atual:** a skill retida deep-research é wrapper para um slash workflow Feynman. Literature-review e os demais wrappers excedentes estão inativos no backup. O pacote skills-only não fornece o runtime que expande esses comandos ou seus agentes Pi. Não há ferramenta Feynman exposta nesta sessão, e a execução profunda no Codex nativo não foi validada. Portanto, arquivos instalados não significam `/deepresearch` operacional. Alpha research pode exigir login; preview requer pandoc/LaTeX; Docker exige runtime correspondente. Não foram realizadas essas configurações. Recursos procedurais, como inspeção de PDFs, só podem usar ferramentas disponíveis dentro do escopo autorizado.

## Limites do projeto e verificação

Financeiro vem somente de IF.data; CVM/B3 fornecem metadados. Pesquisas de economia/contabilidade priorizam documentos primários, fontes oficiais e literatura original, com versão/data, página e escopo das afirmações. João passou a permitir redação assistida por agentes sob sua orientação, revisão e responsabilidade, com fontes/dados/citações/referências verificáveis e sem ocultar exigências institucionais aplicáveis de transparência. Essa decisão supera a proibição anterior; não autoriza fabricar resultados, selecionar a amostra final por suposição ou substituir julgamento humano. A tarefa atual não pede escrever capítulo ou alterar o manuscrito. Paper-writing segue fora da descoberta ativa até necessidade concreta, sem reativação automática. Convenções do pacote não criam um segundo tracker nem governança concorrente.

Verificação: 30 arquivos Feynman conferidos com a origem, 36 arquivos Matt intactos, 38 arquivos existentes de código/testes/scripts/reports intactos e governança raiz preservada na instalação. A documentação raiz foi depois atualizada intencionalmente para registrar esta configuração. Sem execução de workflow de pesquisa Feynman ou testes de implementação nova. A [auditoria de fontes](feynman-source-research-20261002.md) detalha dependências e conflitos de convenções.


Verificação após seleção: somente dois SKILL.md ativos, 14 SKILL.md no backup, apenas deepresearch.md em prompts ativos, 30 arquivos-fonte preservados com hashes iguais e 36 arquivos Matt intactos. Nenhuma instalação de runtime, nova credencial, nova pesquisa, coleta ou implementação foi realizada. A configuração inicial de 16 acima é histórico de aquisição, não o conjunto ativo atual.

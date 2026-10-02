# Fundação de governança, pesquisa e rigor

**Autoridade vigente em 2026-10-02:** publicação e CI mínimos explicitamente aprovados; o complemento final deste documento prevalece sobre gates anteriores, preservados como histórico datado. Não solicitar nova aprovação do mesmo escopo. Verificação remota permanece pendente.

Estado: **spec aprovada por João em 2026-10-02 com a alteração explícita sobre redação assistida, aplicada nesta versão**. Sintetiza as duas seções aprovadas e as instruções explícitas de ferramentas/rigor; não declara a expansão financeira completamente desenhada nem autoriza implementação ou publicação.

## Objetivo e limites

Organizar o repositório existente como referência oficial futura de código, contratos, decisões, evidências e trabalho. A base técnica será multiuso, trimestral IF.data 2010-2026: financeiro principal, prudencial complementar e individual complementar, sempre identificados separadamente. Preservar universo IF.data; cadastro CVM, listagem de ações e relações com emissores/holdings são atributos temporais distintos. A amostra acadêmica é filtro posterior, sem limitar armazenamento. A monografia mantém seu texto atual 2010-2024, foco capital aberto e decisões metodológicas humanas.

João aprovou as seções de base/metadados/recortes/governança e atualização/revisões/validação/falhas. Também solicitou Matt, Superpowers, Context7, skills oficiais Feynman, boas práticas e rigor. Esta especificação cobre a fundação de documentação/workflow/pesquisa e seus critérios; coleta histórica, seleção final de relatórios/variáveis, backend de consulta e amostra final são desenhos posteriores. Não criar um segundo Project, outro checkout ou governança global.

## Onde cada informação pertence

- **Repositório:** código, arquitetura, glossário de domínio, decisões relevantes, specs/planos e relatórios técnicos com evidências rastreáveis. README serve como entrada humana; AGENTS orienta agentes. Ambos apontam para os mesmos documentos, sem duplicar decisões ou status de tarefas.
- **Issues:** tarefa concreta, dependências, critérios de aceite e links de evidência. **Project existente /3:** estado e acompanhamento das mesmas tarefas. Rascunhos atuais são transitórios; migração deve preservar rastreabilidade, sem presumir preservação automática de IDs ao converter itens.
- **Bruto local:** corpos imutáveis e manifestos. GitHub documenta proveniência e reprodução; ser referência oficial não exige publicar todo corpo bruto. Arquivos só se tornam referência remota depois de sincronização verificada. Repo é público e Project privado; a privacidade do Project não se estende a Issues/repo.

## Workflow de trabalho

Uma tarefa começa com problema, escopo, dependências e aceite observável. Se houver dúvida factual, produzir nota de pesquisa com fontes e evidências; se houver decisão metodológica, perguntar a João/orientador. Matt auxilia direção, termos, síntese e decomposição. Superpowers conduz desenho por seções, revisão da spec escrita, plano executável e, quando autorizado, implementação/testes/revisão/verificação.

Execução segue lotes pequenos com resultados verificáveis. O aceite distingue validade de software, adequação econômica, contábil e financeira e publicação. Done aponta para evidência; “validado localmente” não significa “publicado”. No passo futuro de publicação, revisar exatamente os arquivos, licenças/proveniência, audiência e exclusões de raw/capturas/segredos; somente após autorização para commit/push e confirmação remota atualizar o status correspondente. Nenhuma configuração de segurança, chave ou permissão persistente é parte desta fundação.

## Pesquisa técnica e teórica

Manter as nove skills Matt existentes e Superpowers global. Context7 fornece documentação técnica, com checagem da versão efetivamente usada. Matt research produz notas enxutas a partir de fontes primárias. Feynman fica restrito a **deep-research** (investigação profunda com fontes/proveniência) e **pdf-explore** (evidência em páginas/tabelas/notas de PDFs), em v0.5.22, commit e17f5fd0ea57775def66ebd2b16b40b39d3dc867, com MIT. As 14 skills excedentes e dez prompts foram movidos para backup recuperável fora da descoberta ativa, preservando os 30 arquivos de origem e seus hashes. Retém-se apenas o prompt deepresearch e os recursos compartilhados de licença/governança do pacote; a governança raiz prevalece. Matt research continua responsável por consultas enxutas; planejamento, código e revisão permanecem com Matt/Superpowers, evitando workflows duplicados.

**Limites das duas skills:** deep-research exige a expansão `/deepresearch` e capacidades de busca/verificação; seus agentes researcher/verifier/reviewer pertencem ao fluxo Feynman e não são fornecidos pela cópia de Markdown. O prompt admite pesquisa direta em perguntas estreitas, mas não se presume execução nativa compatível. Pdf-explore é um procedimento de leitura cruzada que pode usar ferramentas PDF existentes; não exige terminal específico no seu arquivo. Nenhum runtime, provider, login, chave ou ferramenta extra foi instalado. Pesquisa profunda não será declarada operacional sem validação; essa limitação não justifica ampliar a instalação.

Fontes: documentação e código oficiais para software; BCB/CVM/B3 e documentos normativos originais para os respectivos fatos; literatura original para conceitos econômicos, contábeis e financeiros. Cada afirmação factual deve registrar fonte, data/versão, trecho/página ou evidência equivalente, interpretação e grau de confirmação. Fontes secundárias podem indicar caminhos, mas não substituem a evidência primária que sustenta o resultado. Falta de acesso ou conflito entre fontes fica explícito.

## Critérios verificáveis de rigor

1. **Proveniência e versões:** cada resultado financeiro liga a resposta IF.data, URL/parâmetros, referência, perspectiva, recuperação, hash, status e versão da fonte quando disponível. Revisões preservam originais; produtos derivados identificam o conjunto de versões usado.
2. **População temporal:** distinguir registro CVM, listagem e vínculo ao grupo em cada referência. Evidência positiva, negativa comprovada e desconhecida são estados diferentes. Status atual não prova elegibilidade histórica. Inclusões/exclusões e vínculos precisam de regra documentada; a amostra final e eventuais implicações metodológicas cabem a João/orientador. Não eliminar silenciosamente casos sem evidência nem limitar o passado aos sobreviventes atuais.
3. **Semântica contábil:** documentar conceito, fórmula, unidade, janela, perímetro e regime. Financeiro e prudencial não equivalem automaticamente ao consolidado societário. Mudanças por relatório, capital 2014/2015 e Cosif 2025 ficam explícitas. Dezembro de uma variável de fluxo não será chamado anual sem validar a janela; derivações guardam componentes e justificativa.
4. **Ausências e incertezas:** estrutural, NA, NI, null, vazio e zero permanecem distintos. Falha HTTP/schema é falha de obtenção/interpretação, não população zero ou fato econômico negativo. Resultados desconhecidos e incompletos têm contagem e diagnóstico visíveis.
5. **Reprodução:** replay do bruto validado, hashes, dimensões por referência/perspectiva/relatório, ausência de duplicação indevida e preservação de versões nas revisões. Validar schema/notas/fórmulas na fronteira de 2025, sem inferir equivalência pelo nome. A atualização normal consulta novos trimestres; revalidação histórica dirigida é comando separado, sem agendamento implícito.
6. **Limitações e julgamento:** testes de software demonstram comportamento/integridade; não demonstram, por si, comparabilidade econômica, contábil e financeira, validade da amostra, validade causal ou adequação de um método acadêmico. Relatórios indicam o que foi observado, verificado, inferido, desconhecido e não executado. Evidência de poucos períodos não valida todo o histórico.

É permitido apoio de agentes à redação acadêmica, sob orientação, revisão e responsabilidade de João. Toda afirmação, dado, citação e referência deve ser verificável; não fabricar resultados ou fontes, nem ocultar exigências institucionais de transparência sobre uso de IA. Verificar as exigências aplicáveis antes de uma entrega acadêmica, sem presumir aprovação ou proibição institucional. A restrição anterior à redação assistida foi substituída pela decisão explícita de João.

Esta tarefa não solicita redigir capítulo, executar análise acadêmica ou alterar o manuscrito agora. Paper-writing continua inativa no backup até uma necessidade concreta; não reativá-la automaticamente. Preservar calendário, decisões metodológicas humanas e demais limites de publicação. Não emitir recomendações de investimento ou substituir julgamento humano. Pesquisa técnica e levantamento de evidências continuam com fontes primárias e incertezas explícitas.

## Aceite desta fundação

- Uma navegação documental central identifica estado atual, contratos aprovados, próximos desenhos e evidência, com README/AGENTS coerentes.
- Ferramentas têm presença e limites verificados; versões/licenças/proveniência ficam registradas. Nenhuma alegação de workflow Feynman executado sem evidência.
- Tarefas, critérios e status têm lugares definidos, usando somente repo/Issues/Project existente. Não afirmar sincronização antes da verificação.
- Os seis critérios de rigor acima acompanham os desenhos e aceites posteriores; decisões metodológicas abertas não viram requisitos assumidos.
- A revisão escrita de João foi recebida e a alteração específica aplicada; writing-plans produz o [plano da fundação](../plans/2026-10-02-governance-foundation-plan.md), separado da expansão dos dados. A escolha de execução local é o próximo passo, sem autorização de publicação implícita.

## Evidências e documentos relacionados

- [Diálogo e opções de desenho](../../engineering/brainstorming-2010-2026-20261002.md)
- [Configuração e limites de pesquisa](../../engineering/research-tooling-20261002.md)
- [Auditoria Feynman](../../engineering/feynman-source-research-20261002.md)
- [Fontes oficiais de governança GitHub](../../engineering/governance-source-research-20261002.md)
- [Execução anterior preservada](../../engineering/expansion-execution.md)

As aprovações de seções e a revisão escrita de João aprovam esta fundação, com a alteração registrada. O plano executável fica disponível para escolha de execução; o desenho financeiro completo permanece separado. Não houve implementação do produto, nova coleta, redação de capítulo, commit ou publicação nesta rodada.


## Complemento aprovado: governança operacional dos agentes

João aprovou o plano e agentes por tarefa, com revisão entre etapas, exigindo governança clara e rigor também **financeiro**, além de econômico e contábil. AGENTS.md será a entrada obrigatória: escopo atual, arquitetura/glossário, comandos verificados, plano/tarefa e limites de autoridade. Antes de executar, cada agente identifica objetivo, dependências, arquivos autorizados, critérios de aceite e vínculo com Issue real; se ainda não publicada, declara explicitamente essa condição e aponta à tarefa local, sem inventar ID.

Decisões de método, fórmula ou arquitetura registram motivação, fontes/evidências e limites no contrato/documento correspondente. Um agente só encerra uma tarefa com evidência verificável, documentação/estado de incertezas coerentes e revisão do escopo; testes de software são separados da conferência econômica, contábil e financeira, que não é presumida por testes passando. Resultado local, revisão aprovada e publicação confirmada são estados distintos. Repo mantém contratos/código/evidências; Issues mantêm tarefa/aceite/dependências; o Project existente acompanha as mesmas Issues. Nenhum estado remoto deriva apenas de um arquivo local.

A implementação da fundação está autorizada, incluindo ajustes/testes/revisões locais. Coleta histórica e capítulos não estão solicitados agora. Commit/push e alterações de Issues/Project continuam sujeitos à proposta concreta e aprovação posterior. Reutilizar os documentos existentes, sem rituais ou registros concorrentes.

## Autoridade efetiva de publicação — 2026-10-02

A autorização explícita de publicação de 2026-10-02 permite completar/revisar a fundação, CI offline mínimo, commit/push do conjunto revisado, bootstrap mínimo de main, draft PR e reconciliação das mesmas Issues/cards no Project /3 por ferramenta suportada. Os gates anteriores de não publicar/não implementar CI são histórico datado e foram substituídos para esta entrega. Não autoriza merge, deploy, nova coleta, capítulo, calendário, runtime/contas/chaves, mudança de segurança/permissões/tokens/proteções ou outro Project. Publicação e CI remotas continuam pendentes de confirmação; não há novo gate humano para o escopo já aprovado. Os limites de publicação implícita e aprovação posterior registrados acima descrevem a autorização anterior; este complemento prevalece para o conjunto da [proposta aprovada](../../engineering/governance-publication-proposal.md). A licença própria não foi escolhida; notices MIT upstream permanecem.

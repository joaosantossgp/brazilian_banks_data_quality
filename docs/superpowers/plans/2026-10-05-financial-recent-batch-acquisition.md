# Aquisição financeira recente por janela — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Nesta Issue, root coordena executores frescos por tarefa e revisão independente; nenhum gate humano rotineiro adicional é criado.

**Goal:** Um comando cobre onze referências 202312–202606, reutiliza quatro conjuntos locais sem GET e captura C/D/N nativos necessários dos sete membros restantes, com autoridade cumulativa e handoff verificável por referência.

**Architecture:** Compor sete jobs singleton existentes, cada qual com autoridade, journal writer, pending e destino próprios. O coordenador mantém claim exclusivo e ledger de fases; não duplica transporte, resolver nem budgets. Metadata começa serial e pode chegar a dois membros após diagnóstico; somente depois da barreira metadata7 entram values seriais.

**Tech Stack:** Python existente, stdlib, APIs locais financial_acquisition/windows_acquisition/archive e unittest; Windows Job Objects para execução real. Sem dependência ou camada nova.

**Spec e Issue:** [54 — Adquirir fontes financeiras nativas do lote 202312–202606](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/54). Uma Issue/um PR, base main `d93fab5eb07056388e9282e072ab3cec8085c160` após integração51 e CI pós-merge aprovada, branch `codex/financial-recent-batch`. Root coordena/integrador único, executores distintos por tarefa e revisão independente. O plano não afirma implementação, autoridades dos sete inicializadas ou nova coleta.

## Entradas e restrições comuns

- Entrada: AGENTS → contrato real da [Issue54](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/54) → [workflow](../../agents/workflow.md) → [arquitetura](../../architecture.md) → este plano. Desenho revisto independentemente APP após corrigir compatibilidade403 e recovery de fases; o contrato consolidado tem autoridade.
- Janela literal: `(202312, 202403, 202406, 202409, 202412, 202503, 202506, 202509, 202512, 202603, 202606)`. Acquire7: `(202406, 202409, 202506, 202509, 202512, 202603, 202606)`. Reuse4: `(202312, 202403, 202412, 202503)`.
- Scope do lote: `financial-recent-202312-202606-v1`; scopes singleton: esse literal + `/202406`, `/202409`, `/202506`, `/202509`, `/202512`, `/202603`, `/202606`. Não aceitar outros scopes, períodos, calendário gerado, latest, 202609/202612, URL/policy livre ou nonce para renovar saldo.
- Financeiro1005/quatro relatórios nativos/todas as variáveis. 202406/409: `[92,96,101,98]`; demais novos: `[119,107,110,118]`. Preservar annotations, membership1004 nos metadados, janela/perímetro e ausências; membership não autoriza adquirir1004. N somente após resolução do D próprio; nenhum N1/perfil/schema herdado.
- Por membro: políticas50 máximas, 14 tentativas, 330MiB de corpos, 1.680s de tentativas +35s backoff reserváveis. Soma7: 98 tentativas, 2.310MiB corpos, 12.005s de autorização/reserva. Tempo não é hard elapsed/SLA; extinção/overshoot observado consome saldo e pode exceder a reserva final. Corpos não são teto de disco total.
- Halt entre fases: três membros com fase terminalmente falha; duas conclusões consecutivas da mesma guarda integridade/schema/deadline; persistência/containment crítico interrompe imediatamente novos despachos. Ordem = append durável de conclusões. Metadata2 pode deixar uma fase ativa e chegar a quatro membros falhos; não prometer zero GET após gatilho.
- Retomada: reconciliar todos os inícios sem conclusão antes de qualquer fase nova; extinção/journal/receipt/checkpoint atuais e pins autenticados. Resultado ou ordem relevante inconclusivos → halt conservador, reservas preservadas. Nenhum lease por GET, orçamento compartilhado duplicado ou transação distribuída.
- Compatibilidade403: APIs/CLI/autoridade/budget antigos preservados. Zero despacho403 é regra somente do coordenador. Bootstrap-v1 não contém codehash; specs/receipts antigos preservam seus pins e cada tentativa nova fixa código atual. Nenhuma migração/reset/recoleta403 nesta janela.
- Forbidden: reader/adapter/perfis/registry51; archive.py em escrita; capturas/autoridades/receipts aceitos403 e demais inputs; dados raw/derived/curated existentes; AGENTS/GLOSSARY/tracker/.github/skills/dependências; segurança/credenciais/proteções/deploy/Project3/outros computadores/projetos. Sem dados/valores no stdout ou GitHub.

## Arquivos, destinos e interfaces

| Arquivo | Owner e responsabilidade |
|---|---|
| `bank_quality/financial_acquisition_batch.py` novo | Executor: composição finita, autenticação de reuse, vínculo do lote, ledger, gates e handoff; funções inicialmente privadas; sem export em __init__.py. |
| `tests/test_financial_acquisition_batch.py` novo | Executor: fixtures sintéticas, composição, bypass, budgets, concorrência, crash/recovery. |
| `bank_quality/financial_acquisition.py` | Tasks2–3: trusted singleton scopes e integração interna com coordenador; manter protocolo/journal existentes. |
| `bank_quality/windows_acquisition.py` | Task3: somente validação spec do lote se necessária e regressões de contenção; manter Job Objects atuais. |
| `scripts/acquire-financial.py` | Task3: subcomandos do lote finos, sem lógica reutilizável. |
| `tests/test_financial_acquisition.py`, `tests/test_windows_acquisition.py` | Tasks2–3: regressões legadas e novas fronteiras reais Windows. |
| `docs/superpowers/plans/2026-10-05-financial-recent-batch-acquisition.md` novo | Root publica o plano consolidado no handoff. |
| `docs/engineering/financial-recent-batch-acquisition-20261005.md` novo | Root: execução, recursos, estados/pins/limites sem valores. |
| `README.md`, `docs/architecture.md` | Root/integrador único, somente orientação operacional e responsabilidade implementada. |

Sem rename/delete/nova raiz. Módulo focado adjacente no pacote, testes no destino existente. Run privado ignorado fixo: `data/runs/financial-historical-acquisition-202312-202606-20261005/`, com `preparation/`, `members/<period>/sessions/<attempt_id>/` e ledger/handoff. Autoridades dos sete no destino existente `data/runs/financial-acquisition-authority/<job_sha256>/`. Se destino/binding parcial existir, preservar e reconciliar; não apagar/reinicializar. Novos arquivos operacionais são efeitos das APIs, confinados ao contrato; não ampliar allowlist de código.

### Interface proposta, implementada progressivamente

Todos os retornos são dicts JSON estritos e explicitamente versionados; rejeitar chaves desconhecidas, bool como int, duplicatas JSON, hash não hexadecimal, paths absolutos/escape/reparse e conjuntos incorretos.

```python
# Task1: não grava, não inicializa e não executa HTTP; nomes privados.
_prepare_batch(catalog_index: Path, catalog_index_sha256: str,
               reuse_index: Path, reuse_index_sha256: str) -> dict
_verify_draft(draft: dict) -> dict

# Task2: explicitamente offline; destino e pins externos obrigatórios.
_initialize_batch(draft_path: Path, draft_sha256: str, destination: Path,
                  *, code_pins: dict) -> dict
_verify_batch(bundle_path: Path, bundle_sha256: str,
              *, bootstrap_sha256: str) -> dict
_recover_batch(bundle_path: Path, bundle_sha256: str,
               *, bootstrap_sha256: str, output: Path) -> dict

# Task3: uma execução por janela; metadata_workers só1 ou2, values sempre1.
_run_batch(bundle_path: Path, bundle_sha256: str,
           *, bootstrap_sha256: str, metadata_workers: int = 1) -> dict
```

Task1 produz `financial-acquisition-batch-draft-v1`: `contract`, `scope`, `selection`, `acquire_periods`, `reuse_periods`, `catalogs`, `members`, `reuse`, `policies`, `caps`, `executable` (False). Cada membro: `period`, `job` (candidate completo), `job_sha256` (canônico), `session_root`; nenhuma autoridade/bootstrap real alegada. Paths/pins de execução só surgem na Task2.

Task2 produz bundle `financial-acquisition-batch-v1`: seleção/descriptors/reuse/policies/caps do draft, mapa exato dos sete job paths/hashes canônicos e físicos/bootstrap pins/authority destinations e code_pins. Batchbootstrap próprio e seu hash externo ficam fora do bundle, evitando autorreferência de hashes; initialize retorna esses pins separados. Bootstrap singleton-v1 é deterministicamente derivável de scope/job/policies/targets: os pins previstos podem compor o bundle antes da escrita, mas cada arquivo real deve coincidir antes de aceitar inicialização. Não chamar pin previsto de autoridade física já inicializada. Code_pins fixa commit completo revisto, SHA worker/archive/launcher/CLI/módulo batch, runtime e policy. Identidade/binding do scope impede novo saldo por caminho/workers/nonce/código. Bootstrap/bundle imutáveis e hash físico externo são separados do jobhash canônico. Bundle não é um journal compartilhado de workers.

## Task 1 — Composição finita offline e reuso autenticado

**Allowlist exclusiva:** criar somente `bank_quality/financial_acquisition_batch.py` e `tests/test_financial_acquisition_batch.py` no snapshot privado fornecido pelo root. Código existente é somente leitura. Nenhuma CLI, autoridade ou dataset novo nesta task.

**Viabilidade conferida:** `prepare_job(index, pin, periods, limits=...)` já compila candidatos multi-período, autentica índices/catálogos/corpos e entrega descriptors/targets. Exige prefixo `issue50/` no índice; `_execution_job` ainda aceita só403. Usar o índice50 congelado para preparar os11 com `dict(_POLICIES)`, selecionar cada descriptor dos sete, derivar targets C/D por período, compor candidate singleton com os scopes literais acima e recomputar `_job_hash`. Reutilizar `_catalogs`, `_descriptor`, `_target`, `_canonical`, `_digest`, `_local` e `_authenticated`; nenhuma permissão global/scope falso para executar. É proposta não executável até Task2 instalar validação/executor. Não tentar `initialize_authority` dos novos membros na Task1.

Root provou o preparo offline das onze referências em 0,343s: onze descriptors/22 targets metadata, cinco fontes numéricas anunciadas por membro, candidato não executável e executor antigo recusando a seleção fora403. Essa prova autentica a oferta; o lote novo seleciona acquire7/reuse4 e não autoriza22GET.

**Índice de catálogo existente:** `data/runs/financial-historical-acquisition-202403-20261004/preparation/catalog-index.json`, hash `a373bd96661d95d65b00a4c0bc62d287ea7279de327fe76e7b29b522a776d10e`. Bodies O/N: `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` / `b8977d383e4ea51f56ed391571aca7af1c109b83b9c17ceef8b926841d658206`; usar refs completas do índice, não só bodies.

**Reuso literal:** índice privado `financial-acquisition-batch-reuse-index-v1` com somente `contract`, `scope`, `entries`; quatro entradas únicas, cada qual `period`, `kind`, `manifest_path`, `manifest_sha256`, `evidence` (refs adicionais explicitamente pinadas). Paths/pins abaixo são fixos; index externo só os transporta, não instala novas fontes/políticas:

| Referência/tipo | Manifest/job existente e pin físico |
|---|---|
|312/accepted_parquet|`data/curated/financial-historical-202312-20261004/manifest.json`; `facbc0b6a1d06c10879caa6744e9bb573b29b827dd81d45753477b12ca45d8e6`|
|412/accepted_parquet|`data/curated/financial-four-reports-202412-20261004-run2/manifest.json`; `c9d58a9a6cd105fa1b73b711ba167e6a8909e56e695f16e414e96e6e0e14cd41`|
|503/accepted_parquet|`data/curated/financial-four-reports-202503-20261004-run2/manifest.json`; `64d09fbaf7a40ff279cfc23e3fc002b671979585b22425c561af9138af013d6e`|
|403/accepted_sources|`data/runs/financial-historical-acquisition-202403-20261004/preparation/job.json`; físico `43f775d20a4dd9cf686f975c2232a39b26a3f9afb23ff9732e920c5bb9296ed5`, canônico `b16a582e865f6de1f097820f67fa9b063b5be9fe5ddf0be8dc617415f864c4de`|

312/412/503: contratos próprios, accepted=True, seleção1005 e four native; autenticar bytes/hash de **todos** os `files`, confinados no diretório do manifest, incluindo `metadata/source-manifest.json`. Conferir seleção/profile/source_manifest_sha256/source_files contra essa cópia autenticada e refs de admissão/perfil/origem explicitamente pinadas no índice privado; não inferir outros arquivos em glob nem abrir SQL/readers51. Hashing incremental de arquivos; legado nunca vira bounded.403: bootstrap `026d372570fff21a53d3b59fbf9acf1a164adb377e810811965d80e3251a5a9c`, receipt B `9f380fb46aa7455b5156e739c885d2c5041a12a13c22c22f36229e69ecfaf429`, checkpoint B `f30878c4e4cdcae135913351652a707bc0398bbde006f42a283fac8a2f009373` sob `values-real-01/`; metadata sob `metadata-real-01/`. Delegar verificação de autoridade atual/prefixos ao `verify_authority` existente e autenticar A/B/manifest/body/sidecars necessários; receipt antigo não restaura saldo. Fixture injeta somente root/pins/claim OS, preservando validadores. Root conferiu diretamente os reusos e seus pins: inventories31281/41281/503112 arquivos,403receiptB seq9/prefixo aceito em currentseq10, pending0/failures0/attempts3/body16.342.157; usar refs/pins completos desse registro, sem tratá-lo como revalidação SQL ou nova autoridade. Executor Task1 prova o comportamento em fixtures, sem repetir o hashing do corpus por rotina.

- [ ] Escrever RED `BatchCompositionTests`: seleção exata11, acquire7/reuse4, singleton targets2, descriptor catálogo O `/97`/`/98` e N `/1`–`/5`, reports/filenames/prefixo2025 dupla barra e membership1004 preservados. Expected independently literal, sem extrair expectativa de `_MEMBERS`.
- [ ] Escrever RED mutações: índice/pin/corpo/manifest alterado, duplicate period/entry/key, 609/612, wrong1005/report/pointer/prefixo, reuse ausente/tamper file/escape/profile mismatch, policy/nonce/keys não permitidos. Cada falha deve ocorrer sem saída/GET; `_verify_draft` recusa drift após preparo.
- [ ] Rodar `& .\.venv\Scripts\python.exe -B -m unittest tests.test_financial_acquisition_batch -v`; RED por import/API ausente, nunca por rede. Implementar funções privadas e índices estritos mínimos; fixture source files pequena, sem copiar grandes corpora para teste.
- [ ] Provar candidate não autoriza execução: `executable is False`; zero chamada a initialize/run/archive.fetch; alterar logistics não muda sete identidades/saldo, alterar seleção/policy é rejeitado. Rodar GREEN o mesmo comando; se a composição pedir regressão do seam, rodar somente `tests.test_financial_acquisition.AcquisitionTests.test_descriptor_matches_independent_compiler`, sem repetir baseline/fullsuite.
- [ ] Entregar diff/snapshot, inventário de apenas dois arquivos, comandos/saídas e incertezas ao root. Revisão independente confere escopo/descriptors/reuse. Commit isolado pelo integrador após APP; Task2 depende desse gate. Nenhum GET ou bootstrap real é condição de conclusão desta task.

## Task 2 — Autoridade singleton, binding e ledger conservador

**Files:** modificar módulo batch + `financial_acquisition.py`; testes batch + aquisição. Windows/CLI continuam sem alteração nesta etapa. **Consumes:** draft Task1 autenticado. **Produces:** bundle/bootstrap atuais, claims/ledger e verify/recover offline; runner privado serial com injectable phase callable para testes. Bootstrap real dos sete somente por inicialização explícita dessa task/Task4, sem alegar que já existe.

- [ ] RED trustedscope: `_execution_job` valida mapa scope→período/IDs/catalog/pointers/targets/caps e sete-source bound por membro. Recusa arbitrário/multiperíodo/excesso;403 passa intocado. `prepare_job` aceita apenas scopes novos exatos além do comportamento legado. `_worker_authorization` usa scope validado do job, não `_SCOPE` global; cadastro usa descriptor.period, não202403 constante.
- [ ] RED fronteira supported: APIs públicas singleton `initialize_authority`, `run_acquisition`, recover/verify e CLI legada não executam novos scopes do lote sem contexto interno autenticado do coordenador. Criar seam interno mínimo para coordenador; contexto vincula membro, bundle/bootstrap e claim. Worker verifica journal/head **do membro** e vínculo imutável do lote, sem head mutable global. Testar job/spec falsos, memberpin trocado e chamada standalone; não prometer segurança contra Python local arbitrário malicioso.
- [ ] RED binding/estado: inicialização única offline; mesmo scope com job/policy/path/nonce distinto rejeitado, parcial não ganha saldo novo. Claims ordem lote→membro, writer/pending próprios. Ledger append-only `phase_start` durável/fsync/verificado antes do dispatch e `phase_finish` após resultado; sequência/hash anterior/pins e status obrigatórios. Só coordenador escreve; executor retorna resultado terminal + receipt/checkpoint/error guard, sem append do lote.
- [ ] RED recovery: crash após membro terminar e antes do append finish; restart reconcilia offline/idempotente antes de fase nova. Live/unknown identity, tail parcial, head/binding ausente, outcome sem prova e ordem recuperada relevante incerta → halt sem refund/novo despacho. Autoridade antiga/receipt stale nunca restaura counters. Totais são soma dos sete journals atuais, inclusive reservas; nenhuma segunda contabilidade de budget.
- [ ] Implementar seams e recuperação sobre APIs existentes `_open_authority`, `_verify_receipt`, `_recover_pending`, `_write_exclusive`, `_replace_head` e claim; não duplicar `_apply_record` nem transportar `_Authority` entre threads. Bundle valida pins/codehead antes de qualquer GET; specs futuros pinam código corrente sem reinterpretar bootstrap-v1 legado.
- [ ] GREEN `& .\.venv\Scripts\python.exe -B -m unittest tests.test_financial_acquisition_batch tests.test_financial_acquisition -v`. Revisão independente do diff/base/head exatos e allowlist. Entregar APIs/esquema efetivamente implementados para Task3; ajustar este plano pelo root se seam técnico equivalente ficar menor.

## Task 3 — Concorrência contida, CLI única e resource gate

**Files:** batch, aquisição, windows_acquisition somente spec/auth necessária, CLI existente; três testes correspondentes. **Consumes:** bundle/ledger Task2. **Produces:** `batch-prepare`, `batch-initialize`, `batch-run`, `batch-recover`, `batch-verify`; comando janela + resultados de diagnóstico sem coletaBCB de teste.

- [ ] RED scheduler com fases sintéticas controladas por threading.Event: metadata_workers1/2 somente; todas metadata7 terminam antes do primeiro values, values1 sem overlap. Threads executam cada `run_acquisition` singleton sob seu próprio claim; coordenador serializa despacho/append/guard. Falha parcial metadata bloqueia aceite e registra missing set; values só dos membros com A autenticado após fim da barreira.
- [ ] RED stops: três membros falhos, duas guardas consecutivas, persistência/containment imediato; no metadata2 uma chamada em voo pode terminar, no novo dispatch após halt. Sequência finish define streak; sucesso limpa guarda; job retry interno continua budget próprio. Fasestart sem conclusão impede nova execução **na retomada**, sem bloquear o segundo metadata durante operação normal.
- [ ] RED Windows/localHTTP: dois coordenadores excluídos; workers/descendentes extintos após callbackfailure/deadline/crash do coordenador, inclusive dois membros ativos. Pins CLI/batch/worker/archive/launcher/runtime alterados rejeitados antesGET. Specs batch versionados separados dos v1 legados, chaves/pins exatos; aproveitar `run_contained_attempt`/JobObject, sem shutdown global por editar módulo. Verificar árvores, não só futures/threads. Linux skip explícito não comprova garantia Windows.
- [ ] Implementar CLI fina preservando `prepare/initialize-authority/metadata/values/recover/verify`403 e seus args. Novos commands usam paths/pins externos, `allow_abbrev=False`, pares de args obrigatórios; erro exit2, resultado sanitizado com status/hashes/counters/missing, sem fontes/valores. `batch-run --bundle PATH --bundle-sha256 SHA --bootstrap-sha256 SHA --metadata-workers 1` percorre a janela, sem sete comandos manuais. Preparo é DRAFT, inicialização offline explicita bundle, run retoma com ledger atual.
- [ ] GREEN `& .\.venv\Scripts\python.exe -B -m unittest tests.test_financial_acquisition tests.test_financial_acquisition_batch tests.test_windows_acquisition tests.test_archive -v`; help/erros CLI nas fixtures. Diagnóstico offline/localHTTP primeiro1 e2: WS/commit agregado da árvore, memória/commit livres, disco/overhead, tempo, extinção. Registrar baseline/resource policy por máquina e margem; sem teto universal de RAM, sem concurrência com gate pesado. Pool1 é entrega útil válida; elevar metadata2 somente com margem e par pequeno real autorizado medido na Task4. Values1 permanece.
- [ ] Root congela head/código/runtime e bundle/codepins revistos. Revisão independente mais capaz disponível confere código/pins exatos, contenção/gates/recovery/allowlist. Nenhum GETBCB antesAPP+GREEN+recurso. Commit de código/manifest revisado antes run real para pin completo; não incluir inputs/ledger privados em Git.

## Task 4 — Aquisição bounded dos sete membros e handoff das onze referências

**Ownership:** root/worker de execução, zero código após pin; efeitos somente run54/autoridades dos sete previstos. **Consumes:** Task3 APP/head/pins/diagnóstico e reuse autenticado. **Produces:** A/B+receipts/fontes7 ou estados incompletos honestos; handoff11.

- [ ] Conferir head/pins físicos atuais, hashes protegidos, recursos/disco e ausência de outro gate pesado; compilar/autenticar draft privado e inicializar explicitamente apenas autoridades novas. Se parcial existir, executar recover/verify atuais; nunca bootstrap substituto. Autenticar reusos sem GET e confirmar zero despacho403.
- [ ] Fixar e registrar no ledger público sanitizado command efetivo `batch-run` com paths/pins externos reais gerados pelo initialize; não escrever SHA inventado. Primeira execução metadata1; depois de par pequeno real diagnosticado, metadata2 só se recurso permitir. A mudança de workers não renova identidade/budget. A fase real contém somente alvos congelados dos sete.
- [ ] Concluir metadata7/barreira: A próprio autenticado, C/D nativos e resolução ownD. Registrar áreasN efetivamente necessárias; nenhum numeric antesA nem herdado. Começar values1 e seguir journal/budgets atuais; monitor root da árvore preserva partial/reservas e encerra somente processos próprios quando a guarda medida exigir.
- [ ] Registrar tentativas/body bytes/scheduling reservado+observado/backoffs/overshoot/WS/commit/disco/elapsed/missing por membro e soma. Caps máximos por soma, sem claim elapsed12.005s hard. Falhas/guardas interrompem novos despachos e deixam evidência auditável; não repetir coleta para provocar erro ou provar replay.
- [ ] Produzir onze entradas de handoff: quatro reuse com tipos/pins honestos e sete adquiridos com C/D/N completos+validados+origens ou incomplete/missing explícitos. Dataset completo somente se missing7 vazio.403 é fonte aceita, não Parquet; nenhuma admissão/Parquet/query nova alegada. Revalidar offline produz handoff equivalente em destino novo semGET.
- [ ] Root registra evidência/limitações e revisão independente do bundle/receipts/handoff/protegidos. Se fonte/schema físico tornar captura inválida, preservar e diagnosticar tecnicamente; não inventar método/harmonização ou aceitar silêncio como zero. Task5 pode integrar executor com bloqueio de dados explicitamente registrado, sem fechar aceite integral54 como done.

## Task 5 — Revisão do conjunto, documentação e integração verificadas

**Files root:** dois docs novos, README e arquitetura; allowlist de código real apenas arquivos das Tasks1–3. **Consumes:** head final+handoff/limites/reviews. **Produces:** um PR da Issue54, checks/review/integração/CI reais e mapa2 atualizado pelo root.

- [ ] Publicar plano único/ledger sanitizados nos destinos fixos; referenciar contratos existentes sem copiar grandes specs. README explica um comando janela + prepare/initialize/recover/verify/pins; arquitetura declara módulo/responsabilidade/destino e remove claim de runtime403-only somente onde a implementação nova provar. Preservar notas históricas.
- [ ] Conferir inventário completo `git diff --name-status BASE HEAD` e protectedhashes contra allowlist/arquitetura, incluindo zero rename/delete não previsto, nenhum privado/dado/segredo no conjunto. Wholebranch review independente no head completo com domínio: nativo1005, annotations/perímetros/janelas/missing e reuso distintos; softwarePASS não harmoniza períodos2025 nem prova método acadêmico.
- [ ] Uma fullsuite offline final `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`; checks Node verificados `node tests/test-budget.cjs` e `node --test tests/test-portal-ready.cjs`. Checker de scope somente observação da base confiável. Repetir somente se nova mudança/falha exigir; registrar skips Windows em CI. Docs pedem links/escopo, sem testes de prosa.
- [ ] Resolver achados antes integração, publicar branch/umPR, attachPR, confirmar checks do SHA final/revisão independente, merge autorizado no mesmo escopo e CI pós-merge. Atualizar mesma Issue54 e fronteira real na Issue2; Project3 com Zec. Done somente com aceite integral e evidência; separar resultado local/review/publicação/integração, sem equiparar automação a review GitHub humano.

## Handoff e paralelismo

Cada tarefa entrega base/head ou snapshot imutável, inventário/diff, API efetiva, comandos/saídas, review e desconhecidos. Task1→2→3→4→5 são dependências internas da mesma Issue, sem aprovação humana rotineira de modo/plano/publicação. Fresh executor/reviewer designados pelo root; reviewers não escrevem arquivos do executor. Documentos compartilhados integrados sequencialmente. Acquisition/CLI/testes têm ownership separado do reader/adapter/perfis51; outras Issues só concorrem após root conferir contratos/prontidão reais e atualizar mapa2. Coleta/resourcegate não concorre com carga pesada sem medida conjunta.

Entrega útil de uma sessão: executor com composição finita11, reuso4 autenticado e comando janela bounded, mesmo com metadata1. Cobertura física sete depende dos resultados reais; não estimar completar histórico66 nem prometer duração do lote. Desconhecidos atuais: C/D/N físicos novos, schemas/populações/larguras, timing, ganho metadata2, admissão/Parquet/comparabilidade dos sete. Nenhum deles foi preenchido por este plano.

## Autoconferência do planejamento

Cobertura: seleção/reuse → Task1; scope/budgets/binding/recovery → Task2; barreira/contenção/CLI/capacidade → Task3; captura/limites/handoff → Task4; docs/revisão/checks/integração → Task5. Draft e bundle separados impedem bootstrap alegado antes implementação. Fontes de leitura: workflow/arquitetura/tracker, desenho/APP/triagem, APIs/functions e testes existentes, metadados pequenos dos manifests aceitos. Nesta preparação não foram executados Git/HTTP/testes/pipeline/SQL; somente leitura e escrita destes dois arquivos privados. Root consolida/publica este plano após conferência técnica.

## Consolidação técnica antes da Task1

Índice externo de reuso transporta somente os quatro membros/pins físicos literais acima; não estabelece novas fontes confiáveis, perfis ou cobertura aceita por si. Guardas de arquivo e identidade conferem todos os payloads referenciados e seleção/profile/source-manifest próprios. Fixtures podem injetar root e trust anchors sintéticos internos, mantendo validadores reais. O draft deve ser revalidado/recompilado antes da Task2, rejeitando descritores/policies/reuso alterados coerentemente com um hash novo do documento. Nenhum campo caller-controlled renova orçamento ou autoriza outra janela.

Inicializar bootstrap e executar rede são estados posteriores ao candidato. Metadata preserva desconhecidos das fontes físicas dos sete até sua aquisição; a preparação rápida e os testes offline não provam throughput real, contenção Windows ou dados aceitos dos sete. Docstrings e stdout devem respeitar essa diferença.

# Aquisição financeira histórica — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** implementar aquisição limitada, retomável e auditável, provar primeiro 202403/1005/quatro relatórios depois de fixtures e revisão.

**Architecture:** archive.py transporta/preserva evidência; financial_acquisition.py resolve fontes e controla estado; windows_acquisition.py contém workers e claim no host; CLI fina. Sem alterar admissão/Parquet ou criar camada/raiz.

**Tech Stack:** Python 3.12/stdlib/ctypes/unittest existentes, Windows autorizado; nenhuma dependência nova.

**Spec:** docs/engineering/financial-historical-batch-design-20261004.md e [Issue 50](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/50), contrato específico revisto.

**Execução verificada:** Tasks1–4/correções revisadas independentemente; codehead `1a5a4e4d22195c234e510055c0dd4a72865c9cec`, suíte Windows339PASS/zero skips e3NodePASS. CI push/PR do codehead SUCCESS. Prova real202403:3GETs/16.342.157bytes, pausa entre fases/reusoC/D/metadata→N1, checkpoints externos e recuperação/verificação offline. [Ledger de execução](../../engineering/financial-historical-acquisition-20261004.md) conserva contagens, hashes, recursos e limites. Os checkboxes abaixo registram o plano original; comandos/casos prescritos não substituem os resultados concretos do ledger. Revisão whole-branch/fechamento remoto permanecem posteriores.

**Review Focus:**

1. Corpo JSON válido transportado parcialmente: conferir framing/EOF e preservar falha.
2. Receita antiga e sessões concorrentes: usar autoridade atual sob claim, sem renovar saldo.
3. Perda abrupta do parent/launcher: criar já contido e provar extinção da árvore.
4. Catálogo/C/D de períodos ou namespaces diferentes: resolver somente origens/pins exatos.
5. Tail incompleto ou falha de sincronização/recursos: impedir rede, debitar conservadoramente e preservar evidência.

---

# Aquisição financeira limitada e retomável — plano candidato v2

> Execução escolhida: Superpowers `subagent-driven-development`, TDD e revisão independente, sob o contrato real da Issue 50 e o goal aprovado. Originais privados v1/v2 e pareceres preservados. Código/coleta ainda não executados ao registrar este plano.

**Objetivo:** fechar os dois P2 do plano v1 — rollback/renovação de budget e crash do parent — e implementar primeiro a aquisição Windows 202403 com C/D antes dos shards resolvidos.

**Base:** `main` `965151f48ffdadc710c48991864d3612980bed08`, nota 47 publicada SHA-256 `a134a8b4745dd69473b1b9bd777e3c514687ec61986597c574327b348052b181`. Capturar novo SHA se `main` avançar antes do claim. Python local/stdlib/unittest/ctypes; sem dependência nova ou alteração de segurança do SO.

**Arquitetura:** transporte opt-in em `archive.py`; resolução física e workflow em `financial_acquisition.py`; helper local `windows_acquisition.py` para claim/Job Object. CLI fina e documentos compartilhados com integrador root. Os 11 paths da Issue candidata v2 são a allowlist completa; novos destinos operacionais precisam de referência na arquitetura no mesmo lote.

## Invariantes globais

- Job finito com hash canônico de seleção/catálogos/targets/políticas; períodos/targets ordenados, sessions/timestamps/paths/worker count excluídos. `acquisition_scope` estável da Issue/recorte e binding local fixam o único job/ bootstrap aceitos. Job/limites novos exigem execução revisada com gasto anterior registrado; `prepare` não renova autoridade. Somente o hash externo fixado no contrato executa GET.
- Autoridade fixa por job, bootstrap imutável e claim OS exclusivo; parent único escritor do journal/head. Session/receipt antigo nunca é fonte atual de saldo.
- Reserva e head sincronizados antes de criar child; qualquer falha de integrity/durability impede launch/rede. Nenhuma recuperação oculta de orçamento.
- Windows real: criação suspensa já associada ao Job Object, handle do job só no parent e `KILL_ON_JOB_CLOSE`; sem BREAKAWAY/fallback não contido. Unsupported recusa antes de GET.
- Linux CI: lógica/framing offline e rejeição do runner real; sem alegação de contenção ou crash universal. `recover` é offline, inclusive quando o claim precisa da plataforma Windows.
- C/D específicos; somente áreas de folhas `td=3` com anúncio exato; groups/attrs/pointers/lexemas/annotations nativos. `validated` é schema físico, não admissão econômica.
- 202403 real somente; 1 worker; C/D 5 MiB acumulados cada, N 64 MiB por shard, 2 tentativas, rede 30 s, deadline 120 s, sem redirects. Máximo conservador 7 arquivos/14 GETs/330 MiB, reduzido por origens/reuso.
- Fonte nova não sobrescreve body/manifest/receipt aceito; autoridade operacional é o estado mutable específico, sob claim. Todos os dados/headers ficam privados.

## Task 1 — Transporte limitado, independente do resolver

**Owner/paths:** implementador de transporte, `bank_quality/archive.py` e `tests/test_archive.py` somente. Pode avançar junto à Task 2; nenhum arquivo/test utility compartilhado novo. Legado `fetch/load_body/preserve_generated` mantém comportamento/defaults.

**Interface a produzir:** `fetch_bounded(url: str, root: Path, label: str, context: dict, *, body_budget_bytes: int, timeout_seconds: float = 30) -> dict`. Recebe primitivas e não importa tipos do resolver. Retorna manifest da tentativa, sem body em RAM no parent; não contém coordenação/deadline de processo. Um fake opener injetável nos testes restringe rede aos fixtures.

- [ ] RED: `test_complete_body`; `test_valid_json_shorter_than_content_length`; `test_duplicate_or_invalid_content_length`; `test_missing_length_requires_eof`; `test_chunked_incomplete`; `test_cap_without_eof_rejected`; `test_redirect_target_never_contacted`; `test_http_failure_preserved`; `test_unexpected_encoding`; `test_incomplete_read_partial_preserved`; `test_write_failure_not_ok`.
- [ ] Implementar chunks até o remaining budget, hash incremental e arquivos exclusivos. Preservar response metadata e a lista bruta de headers antes do body/projeção em dict, sem perder duplicatas; bytes observados/partial e diagnóstico tipado. Content-Length único/coerente e EOF/framing positivos; Content-Length/Transfer-Encoding ambíguos e encoding não identity falham. Não ler byte adicional fora do cap para provar EOF.
- [ ] Parsing não faz parte de completude de transporte: JSON válido truncado é falha. Manifest incompatível/incompleto não recebe `outcome=ok`; header ausente não vira comprimento zero.
- [ ] GREEN: `.venv/Scripts/python.exe -B -m unittest tests.test_archive -v`. Legado segue igual e servidor local não contacta BCB. Handoff: diff/base/head, comportamento e schema do manifest; nenhuma alegação de deadline duro de processo nesta Task.

## Task 2 — Job, origens e schema físico, independente do transporte novo

**Owner/paths:** implementador do resolver, `bank_quality/financial_acquisition.py` e `tests/test_financial_acquisition.py`. Usa `load_body` legado estável quando necessário; nenhum import de helper novo/worker. Todas as funções abaixo são offline.

**Interfaces a produzir:**

- `prepare_job(catalog_index: Path, catalog_index_sha256: str, periods: tuple[int, ...], *, limits: dict, reuse_index: Path | None = None, reuse_index_sha256: str | None = None) -> dict`.
- `resolve_sources(job: dict, metadata_sources: dict) -> dict`: checkpoint A com C/D autenticados, árvore/definitions/pointers, origens e lista mínima N; não confia em source spec declarada sem revalidar corpo.
- `validate_numeric_source(body: bytes, *, area: int, required_origins: list[dict]) -> dict`: relatório físico de N com schema/tipos/IDs/pointers e faltantes, sem células financeiras derivadas ou coerção.

**Job mínimo:** contract/version, `acquisition_scope` da Issue/recorte, seleção canônica, catálogos e descriptor hashes, períodos/reports/pointers, literal filenames, policies e source refs. Períodos/targets são ordenados canonicamente; `job_sha256` exclui execution ID/destino/timestamp/worker count. A execução real exige job e bootstrap externos fixados no binding do scope; `prepare` só cria candidato offline e nunca bootstrap de budget novo. Source refs usam `source_id`, role, area quando aplicável, announcement pointer/literal filename, manifest path relativo e hashes externos de manifest/body/provenance. A raiz é fixa e derivada do pacote; raw/runs aprovados, sem root arbitrário, absoluto/URL/escape/symlink/reparsepoint.

- [ ] RED: `test_catalog_hash_changed`; `test_period_202609_rejected`; `test_wrong_selection`; `test_multi_perspective_membership_preserved`; `test_double_slash_literal`; `test_sparse_shards_not_range`; `test_missing_or_duplicate_report`; `test_escape_or_symlink_rejected`; `test_duplicate_json_keys`; `test_job_hash_stable_across_sessions`; `test_reordered_periods_same_job_hash`; `test_changed_limits_do_not_create_executable_authority`.
- [ ] Implementar seleção dos catálogos O/N congelados da 47 e subset explícito dos 66 períodos. Conservar report metadata/annotations e links de pais/filhos. `prepare` não baixa latest/trel/sel/filtro e não ativa perfil.
- [ ] C: array de objetos com schema nativo uniforme registrado, c0 opaco/único/não vazio e c1 literal do período; sem padding/38 fixo. D: definição inteira/única por ID, `td/a/lid` suportados; todos os nós encontram definição. Group/children/td estrutural coerentes; atributo aponta campo C real; numérico aponta lid/área anunciados.
- [ ] RED de origem: `test_dictionary_from_other_period_rejected`; `test_missing_definition_blocks`; `test_attribute_outside_cadaster_blocks`; `test_group_has_no_numeric_origin`; `test_unannounced_area_blocks`; `test_two_bindings_share_one_source_without_merging_occurrences`.
- [ ] N mínimo: objeto `id/values`; `id` corresponde à área; values é lista de objetos `e/v`; `e` número inteiro canônico único; v é lista de objetos `i/v`; i inteiro canônico único por e. Tipos/lexemas numbers/strings/null preservados, sem float binário/coerção; bool/container/constante JSON/chave repetida/forma estrutural não suportada impedem `validated`. Extensão de schema desconhecida conserva corpo e diagnóstico, sem silenciosa normalização.
- [ ] RED de N: `test_numeric_wrong_area`; `test_duplicate_entity`; `test_duplicate_information`; `test_noncanonical_identifier`; `test_numeric_lexeme_and_string_distinct`; `test_unsupported_value_shape`; `test_missing_cadaster_entity_is_coverage_not_bad_schema`; `test_shared_foreign_entities_not_filtered`; `test_all_origin_pointers_present`.
- [ ] GREEN: `.venv/Scripts/python.exe -B -m unittest tests.test_financial_acquisition -v`. Handoff da Task 2 antes da Task 3 modificar os mesmos paths. `source_complete`, `source_validated`, `origin_resolved` e `admitted` são estados distintos; o último não é produzido nesta Issue.

## Task 3 — Autoridade local e contenção Windows, integração após Tasks 1/2

**Owner/paths:** integrador de aquisição recebe o módulo/teste da Task 2 e cria `bank_quality/windows_acquisition.py` / `tests/test_windows_acquisition.py`. Novo helper é pequeno e local: somente claim de arquivo e launch/kill do worker conhecido. Nenhum registry de plataforma/motor genérico.

**Interfaces a produzir:**

- `open_authority(job: dict, *, bootstrap_sha256: str) -> context manager`: claim exclusivo e estado atual verificado; não bootstrap automático.
- `reserve_attempt(authority, target: dict, *, session_id: str) -> dict`: commit durável de tentativa/reserva antes de qualquer criação de processo.
- `run_contained_attempt(spec_path: Path, spec_sha256: str, *, deadline_seconds: float, before_resume: Callable[[dict], None]) -> dict`: helper Windows lança somente o módulo interno conhecido e verifica contenção. Antes de `ResumeThread`, chama no parent `before_resume` com PID/creation-time obtidos dos handles; o integrador faz o commit durável desse registro na autoridade. Falha do callback encerra o job e espera os processos sem liberar o worker. Retorna estado/PIDs/exit/deadline; unsupported levanta erro antes do launch. O callback tem esse único papel, sem API genérica de lifecycle.
- `run_acquisition(job_path: Path, job_sha256: str, session: Path, *, phase: str, bootstrap_sha256: str, checkpoint_sha256: str | None = None, resume_from: Path | None = None, resume_sha256: str | None = None) -> dict`.
- `recover_authority(job_path: Path, job_sha256: str, *, bootstrap_sha256: str, output: Path) -> dict`: offline, com claim, receipt novo; jamais invoca transporte.

### Autoridade e protocolo de commit

`data/runs/financial-acquisition-authority/<job_sha256>/` contém bootstrap imutável, journal e head atual. No destino pai, `scope-<scope_sha256>.binding.json` fixa acquisition scope, job e bootstrap, e `scope-<scope_sha256>.lock` é o claim comum. Um binding desta única execução basta; não criar catálogo/serviço global. Inicialização offline explícita sob claim cria binding/bootstrap exclusivos; seu SHA faz parte do contrato de execução. `run/resume/recover` não inicializam autoridade ausente ou outro job no mesmo scope. Paths de sessions não mudam esse local. Revisão futura de job/limites exige registro explícito com despesa anterior; não implementar migração automática na primeira fatia.

Record mínimo do journal: `sequence`, `previous_record_sha256`, `kind`, `job_sha256`, `attempt_id`, `target_key`, `session_id`, `attempt_delta`, `reserved_bytes`, `observed_bytes` quando conclusivo, `reserved_attempt_seconds`, `observed_attempt_seconds`, `reserved_backoff_seconds`, `observed_backoff_seconds`, failure count/streak, status/source refs e record hash. Target é referência/papel/área/literal filename/catalog hash. Head registra última sequência/hash comprometidos e digest do estado acumulado. Recomputar todos os contadores sob claim; não copiar counters de receipt antigo.

1. Adquirir claim OS e validar bootstrap, journal completo, head e receipts/fontes atuais.
2. Append de `reserve`, flush + sincronização; gravar/sincronizar head temporário e substituir atomicamente o head. Confirmar ambos antes do launch. Failure em qualquer operação produz zero criação/GET.
3. Criar worker suspenso já contido. Registrar PID/creation-time do worker e sincronizar esse record/head antes de liberar execução.
4. Após resultado, parent verifica body/hash/framing/schema e append de conclusão/despesa. Só conclusão verificável substitui reserva por bytes observados e libera a parte não consumida; não usar ausência de body como prova de zero tráfego.
5. Receipt final imutável aponta à autoridade/sequência/hash atuais e às fontes; é fotografia para auditoria. Resume sempre consulta head/journal atuais após obter claim.

Journal append-only com tail parcial, head adiantado ou cadeia inválida é integrity failure: zero GET. Não truncar/reescrever log para permitir continuidade. Recover primeiro comprova extinção da árvore de cada tentativa: handles/associação ou PID com creation-time, nunca PID nu. Processo próprio ainda vivo ou identidade/término não comprovados bloqueiam a reconciliação; não ler body como se estivesse fechado. Sem conclusão verificável, cobrar tentativa, bytes e tempo reservados conservadoramente. Recover pode incorporar offline record completo ainda não comprometido; preserva evidências e grava novo receipt/record de recovery. Tail inválido permanece blocker explícito. Não prometer recuperação automática de toda corrupção ou resistência a rollback adversarial de todo o estado local.

**Relógios:** deadline da tentativa usa monotônico local, começa imediatamente antes de criar o worker e termina após extinção comprovada; cap 120 s reservado antes do launch. Cada backoff permitido é outra reserva de no máximo 5 s, medida uma vez, no máximo 7 na fatia. Scheduling agregado = 1.715 s, composto por até 1.680 s de tentativas e 35 s de backoff. Reservas órfãs consomem seu teto; sessões retomadas recebem apenas o restante atual. Não comparar monotônicos de processos/boots diferentes nem usar UTC para devolver tempo. Preparo/revisão/pausas/validação offline são medidos separadamente, sem prometer wall SLA de 1.715 s.

- [ ] RED: `test_old_receipt_cannot_restore_budget`; `test_valid_old_prefix_conflicts_with_current_head`; `test_two_sessions_share_one_authority`; `test_new_session_does_not_change_job_hash`; `test_reserve_fsync_failure_no_launch`; `test_head_commit_failure_no_launch`; `test_counter_underflow_or_reduced_counter_rejected`; `test_missing_authority_not_reinitialized`; `test_orphan_reservation_charged`; `test_recover_transport_calls_zero`; `test_partial_journal_tail_blocks_without_truncation`; `test_recover_live_worker_refused`; `test_backoff_charged_once_across_resume`; `test_deadline_failure_streak_not_reset_by_receipt`.
- [ ] Claim Windows via CreateFileW com compartilhamento zero e handle não herdado. Parent único escritor; nenhuma criança recebe handle da autoridade. Teste real de dois processos: enquanto um detém claim, o segundo falha/aguarda sem callback de rede; após release usa o head atualizado. Linux executa modelo puro/fake claim, sem declarar prova OS equivalente.

### Job Object e janela de criação

Fluxo Windows: `CreateJobObjectW` sem nome/handle herdado → configurar `KILL_ON_JOB_CLOSE` → `InitializeProcThreadAttributeList`/`UpdateProcThreadAttribute(JOB_LIST)` → `CreateProcessW(CREATE_SUSPENDED | EXTENDED_STARTUPINFO_PRESENT)` com associação no próprio nascimento → verificar associação → record/head de PID durável → `ResumeThread`. Fixar application/module/spec autenticados, sem shell/URL livre. Não usar BREAKAWAY nem flags de segurança/tokens/ACLs novos.

O parent mantém o único handle do job; child não o herda nem duplica. Deadline/cancelamento encerra o job e espera os processos próprios; crash do parent fecha o último handle pelo SO e elimina associados/descendentes. Associação/API/nested job incompatíveis falham fechadas. Criar suspenso e associar manualmente depois não fecha sozinho a janela de órfão entre essas chamadas, portanto não é fallback aceitável para esta garantia.

- [ ] Windows RED/GREEN: `test_worker_contained_before_first_callback`; `test_identity_commit_callback_before_resume`; `test_identity_commit_failure_kills_suspended_worker_without_get`; `test_parent_crash_after_creation_before_resume`; `test_parent_crash_after_resume_kills_launcher_and_grandchild`; `test_job_handle_not_inherited`; `test_job_list_failure_no_process_or_get`; `test_resume_failure_kills_suspended_worker`; `test_deadline_kills_owned_tree`; `test_second_claim_owner_after_crash_uses_existing_reserve`.
- [ ] Fixtures usam callbacks/servidor local e um supervisor de teste externo ao job; nenhuma rede BCB. Injetar crash antes da criação, imediatamente após criação, depois de PID commit e após primeiro callback. Prova inclui zero GET antes de liberação, ausência de sobreviventes e reserva intacta; não basta observar apenas exit do launcher.
- [ ] Linux CI: `test_platform_unsupported_before_launch`, replay/counters/schema/framing. Windows-only skips devem ser explícitos; antes da fonte real, os testes Windows passam no host autorizado. Unsupported nunca troca para `subprocess.Popen` desprotegido.
- [ ] GREEN: `.venv/Scripts/python.exe -B -m unittest tests.test_archive tests.test_financial_acquisition tests.test_windows_acquisition -v`; evidenciar plataforma/casos executados/skips, não alegar a mesma garantia em Linux.

## Task 4 — CLI, primeira fonte e documentos compartilhados

**Paths:** `scripts/acquire-financial.py`; teste financeiro após handoff; root integra plano/ledger/README/arquitetura nos paths da allowlist. Interfaces CLI: `prepare`, inicialização offline explícita da autoridade, `metadata`, `values`, `recover`, `verify`. `recover/verify/prepare` não abrem transporte. Operações reais exigem job SHA, bootstrap SHA, plataforma suportada e autoridade atual; values exige também checkpoint A SHA.

- [ ] RED/GREEN: prepare zero GET; recover zero GET mesmo com pendências; valores antes de checkpoint recusados; receipt antigo com session nova não renova budget; destination/authority ausente/adulterados falham; errors retornam exit 2 com causa visível; nenhum absolute/root/base/URL livre; source metadata privada não sai no stdout.
- [ ] Job 202403: O `/96`, C `/files/0/f`, D `/files/9/f`, reports 92/96/101/98 nos pointers 29/32/12/33; N anúncios 3..7. Fase A teto 4 GETs/10 MiB/480 s; Fase B no máximo 10 GETs/320 MiB/1.200 s, reduzidos pelo resolver/reuso. Shard 1 e cadastro 38 não são defaults desta seleção.
- [ ] Review independente do head verifica P2 fechados, interfaces/allowlist, todos casos de framing/schema e contenção Windows real. Resolver/source validation não libera perfil de admissão ou inferência econômica.
- [ ] Diagnóstico pequeno offline/localhost mede memória/commit/disco/processos e reserva para host. Sob contrato específico da Issue, executar fonte real com 1 worker: metadata → autoridade/head + checkpoint A → valores requeridos. Não executar outros lotes ou gate pesado concorrente sem ownership/recursos reavaliados.
- [ ] Interrupção real entre fases comprova reuso: nova session consulta a mesma autoridade e não faz GET de C/D aceitos. Crash/deadline são provocados em fixtures, sem coleta redundante para fabricar falha. Mudança de fonte/vintage não sobrescreve corpo anterior.
- [ ] Ledger publica somente proveniência mínima, GETs/tentativas/budgets/bytes/tempos/memória/framing/source completeness/validation/missing set e comandos realmente executados. README recebe apenas comandos verificados; arquitetura descreve helper Windows, módulo, CLI e autoridade operacional na responsabilidade existente. AGENTS/CI/política/segurança ficam intactos.
- [ ] Hashes protegidos e diff/allowlist, revisão independente e checks antes da integração; PR/checks/merge/CI têm confirmação real. Atualizar fronteira do mapa 2; Project /3 continua com Zec.

## Simplificação e fronteira das próximas entregas

Indispensável agora: transporte/framing, resolver/schema C/D/N, uma autoridade local durável, claim exclusivo, um helper Windows contido e receipt/recover offline. Não criar banco de jobs, serviço/scheduler, motor de plataforma, retry universal, assinatura criptográfica própria ou 66 pipelines. Um ledger/journal local por job e módulos focados bastam para o recorte.

Expansões: quatro batches completos, concorrência real maior que 1, admissão/registry/Parquet/query, guardas de processo Linux e estratégias de reparo de corrupção mais amplas. Lotes continuam 11/12/23/20 referências, mas esta Issue mede 202403 e não valida regimes desconhecidos por extrapolação. Questões acadêmicas/produto/conteúdo complementar seguem a autoridade própria de João/orientador.

**Execução do intervalo:** 202403 é a prova inicial do mecanismo, não uma estratégia de execução manual trimestre a trimestre. Após este gate, preparar jobs para os lotes da nota 47, começando por 202312–202606, e medir a concorrência de downloads adequada ao host. As fontes nativas continuam separadas por referência; checkpoints e contratos preservam essa separação mesmo quando várias fontes são adquiridas em paralelo. O reuso autenticado evita novos GETs. Concorrência de rede e concorrência de admissão/conversão são medidas separadamente; a versão desta Issue, com um worker real, ainda não comprova o agendamento concorrente dos lotes.

## Fontes e verificação desta revisão

APIs consultadas via Context7 nas primárias oficiais: [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects), [CreateJobObjectW](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-createjobobjectw), [CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw), [AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject), [UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute), [CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew). JOB_LIST Windows 10+ é recorte explícito, não suporte inferido para qualquer Windows.

Conferidos `main`/nota publicada/código/arquitetura e preservação dos originais privados. Nesta tarefa foram escritas somente as duas candidatas v2; consulta de documentação não adquiriu dados IF.data. Não foram executados código de produção, testes de processo/transporte ou coleta. Comandos/casos acima são prescrições para a implementação; não resultados já aprovados.

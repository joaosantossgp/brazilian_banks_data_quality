# Quatro relatórios financeiros 202412 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Admitir e consultar integralmente Resumo, Ativo, Passivo e DRE financeiro 202412, preservando estrutura, lexemas, precisão por binding, ausências e fontes, com replay e capacidade do ciclo completo medidos.

**Architecture:** Contrato novo fechado para o conjunto 202412/1005/92,96,101,98. Reader e adapter adjacentes focados no pacote existente; APIs financeiras recebem dispatch mínimo por contrato explícito. Uma grade textual conserva o dado original; projeções numéricas tipadas por binding evitam o Decimal global impossível e a união que arredonda. Não alterar regime/contratos/defaults legados nem o modelo lógico aprovado.

**Tech Stack:** Python 3.12, biblioteca padrão, unittest, DuckDB 1.5.6 já instalado, Parquet ZSTD; nenhuma dependência nova.

**Issue e autoridade:** [42](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/42), parent2, base `4b2b8baa2a8b18f2d7e38d9b26b0668eb2daca98`, branch `codex/financial-four-reports-202412`. [Contrato 39](../../engineering/financial-four-reports-202412-contract-20261004.md) revisado/integrado no PR41; CI pós37225254800 SUCCESS. João autorizou a rota por goal, todos os quatro relatórios/variáveis e escolhas técnicas autônomas, inclusive reconsideração baseada em evidência, mantendo testes/revisão. Modo escolhido: subagent-driven-development, fresh implementer e task-review por tarefa, broad review final. Não repetir confirmação rotineira do desenho/plano/modo no mesmo escopo.

## Global Constraints

- Somente período202412, perspectiva1005, conjunto ordenado `[92,96,101,98]`; índice explícito de cinco fontes O/C5/D/P/N1. Sem rede/latest/auto-discovery ou parâmetros de perfil não confiáveis.
- Índice `ifdata-financial-reports-sources-v1`; admissão `ifdata-financial-reports-snapshot-202412-v1`; Parquet `ifdata-financial-reports-parquet-202412-v1`; perfil instalado `ifdata-financial-reports-profile-202412-v1`. Contextos por chamada, sem alterar globais legados.
- Perfil fixa seleção, quatro árvores/definições/annotations e pins de corpo/manifest/projeção completa da proveniência dos cinco roles (somente indexed_manifest relativo local pode variar). Corpo e manifest/contexto/schema/URL/UTC têm que corresponder; fonte faltante/alterada bloqueia aceite. Não reescrever contexto1006 de aquisições shared como1005.
- Cadastro nativo38, c0 opaco/único e matching literal aos lexemas e/i inteiros; não normalizar holding/paddedID/flags, filtrar n4/TD/TCB/SR, inferir elegibilidade ou usar1006.
- c/sc recursivo:121nós reais,9grupos sem célula,112folhas. ifd≠lid; chaves por snapshot/ocorrência/report/posição/source. Duplicação de lid em bindings não é deduplicação nem soma. d/nac/formatter/rp opacos/preservados.
- Atributos/códigos permanecem texto; quantidade é distinta de atributo; JSON number/string/lexema/Decimal, empty/NA/NI/null/zero/ausência são distintos. Não síntese NI/zero, float/arredondamento, execução de fórmulas ou anualização. DRE e lucro de dezembro: julho–dezembro; estoques na referência com base inferida, unidadeBRLcrua inferida e vintage não conjunta explícitas.
- Fonte real pglobal40/s27, cada binding≤38. Grade geral original textual, **sem numeric_decimal global**. Part/view numérica por binding com tipo exato; nenhuma UNION numérica entre tipos. Originais são autoritativos, projeção derivada verificada por Decimal Python.
- Saídas cinco payloads admitidos `financial-cadastro.csv`, `financial-cells.csv`, `financial-observations.csv`, `financial-variables.json`, `financial-diagnostics.json` +manifestfinal. Campos de células reutilizam `financial.FIELDS`; report_id/catálogo por binding; metadados incluem toda árvore/grupos/annotations/fontes. Cadastro envelope de conjunto e38campos, não fingir report_id único de todo conjunto.
- Parquet: grade textual epartições tipadas explícitas emparts, complementos emmetadata commanifestoriginal; inventário completo derivado do perfil/bindings, nenhum glob/extra/partial. Hash externo na conversão/abertura; destino novo; manifest por último. Abertura copia bytes verificados para scratch próprio, materializa em memória, não segue arquivo mutável durante query. Conexão segura existente: extensões/rede/acesso externo bloqueados e caminhos próprios explícitos.
- Inventário protegido de76arquivos distintos, incluindo dezarquivos das cinco fontes; dois códigos autorizadospara dispatch têm hash anterior/final, não alegar78imutáveis. Zero alteração de individual, scripts, perfis legados, CI/política/skills/segurança/credenciais/proteções/deploy/Project3. Sem nova camada/raiz/rename/delete.
- Fixtures antes de real. Recurso por máquina:≈7,36GiBvisível/1,53GiBlivre no diagnóstico, preflightpeak457MiB não é pipeline. Reavaliar livre antesdeexecução real; umworker/budgetinicial1GiB específico destehost, deadline medido/guardado peloexecutor, ajustável por evidência. Não iniciar histórico/concorrência longa antesde gate completo. Sem tetoRAMuniversal.

## File Structure e ownership

| Path | Responsabilidade / owner |
|---|---|
| `bank_quality/financial_reports.py` | Reader/admissão do conjunto fechado; implementerTask1 |
| `bank_quality/financial-reports-profile-202412.json` | Metadados/pins/annotations sem observações; implementerTask1 |
| `tests/test_financial_reports.py` | Fixtures e regressões independentes da admissão; implementerTask1 |
| `bank_quality/financial_reports_parquet.py` | Projeção/abertura/consulta exata porbinding; implementerTask2 |
| `tests/test_financial_reports_parquet.py` | Integridade/precisão/consulta/replay/corrida; implementerTask2 |
| `bank_quality/financial.py`, `bank_quality/financial_parquet.py` | Dispatches mínimos para contrato novo e regressões; implementerTask3, após handoff |
| `README.md`, `AGENTS.md`, `docs/architecture.md`, este plano e ledger `docs/engineering/financial-four-reports-202412-execution-20261004.md` | Integrador único root, Task4 |

Os novos módulos separam responsabilidade do conjunto recursivo/heterogêneo, sem reescrever módulos legados grandes. Reutilizar helpers de integridade/arquivo/JSON/CSV/conexão/Decimal onde conservem a semântica. O contrato39 citava candidatos existentes; desdobramento técnico e ownership exatos foram aprovados pela autonomia e registrados na Issue42 antes de escrever.

Preparação privada `.superpowers/sdd/financial-four-reports-implementation-20261004/`; admissões `data/derived/financial-four-reports-202412-20261004/` e`-replay`; Parquet aceito `data/curated/financial-four-reports-202412-20261004-run2/` e`-run2-replay`; destino original parcial preservado sem aceite; `.scratch` temporário comownership. Destinos ignorados e novos; nenhum executor remove/reescreve artefatos aceitos. Cada task recebe allowlist estreita e não edita docs/shared ou arquivos de outra task. Commits por task preservam base/head; root único publica/integra.

## Task 1 — Reader/admissão do conjunto nativo

**Files:** Create `financial_reports.py`, perfil e teste de admissão acima. Demais paths readonly.

**Interfaces:** `admit(index_path:Path, output:Path)->dict`; helpers internos para contexto/perfil/pins, árvore/bindings, leitura e validação de admissão reutilizável pelo adapter. Mantém selection/cells/observations/cadaster_records/accepted/contract no manifest, sem contagens de produção como guardas de fixtures. Perfil fixtures mockado somente emteste, nunca porCLI/index.

- [x] Construir fixture pequena independente com quatro reports, grupo recursivo, atributocódigo/texto/data, quantidade string, moneyJSONlexemas, ifd≠lid/lidrepetido entrebindings, cad38, fontes/pins exatos somentefixture. Valores grandes/1e-27/-0.00/markers/null/empty e fonte/entidade/informação ausentes.
- [x] RED: testes da API ausente/contrato, grade/observações/árvore/grupo, origem/tipo/lexema/precisão/estado/janela e hashing completo; destino existente/schema/hash/contexto/referência/árvore/duplicates rejeitados. Observar falha real antes de implementação.
- [x] Gerar perfil instalado somente de metadados oficiais/pins já conferidos na39, sem corpo/cadastro/observações, comannotations de espécie/unidade/janela eparent/children/pointers. Preservar fórmulas suspeitas como texto. Implementar reader mínimo por contexto fechado e proveniência completa, sem JS ou cálculo.
- [x] GREEN e self-review: fixtures/legados pertinentes, diff/hash/profile/privateleak/allowlist. Commit sóos três paths, sem publicação. Handoff base/head/diff/comandos/incertezas.
- [x] Revisor fresco Task1 confere spec+qualidade/contrato/perfil/pins e regressões; corrigir P1/P2 comRED/GREEN antes deTask2. Task1 produz admissão offline testável sem depender deParquet/dispatch.

## Task 2 — Parquet e consulta exata por binding

**Files:** Create `financial_reports_parquet.py` e seu teste. Reader/perfil/readertests readonly salvo achado encaminhado aoowner.

**Interfaces:** `convert_financial(source,destination,*,source_manifest_sha256)`, `validate_snapshot(destination,*,manifest_sha256)`, `snapshot_connection(...)->DuckDBPyConnection`. Helpers de validação/admissão daTask1 importados, `_connection` seguro reutilizado. Manifest inclui `decimal_type='per_binding'` para compatibilidade de relatórioCLI e mapaexato de tipos/views/files porbinding; marcador não é tipoSQL.

- [x] RED: fixtureadmitidaTask1 com pglobal40 e bindings locais≤38; texto/código ficaVARCHAR, numericoriginais eDecimal derivados exatos, missing/NI/null semzero. Nenhumcampo numérico global e nenhuma UNIONarredondada. Rejeitarbindingindividual>38 na projeção semmanifest deaceite.
- [x] RED: fonte/manifest/snapshot/inventário/perfil/grade/schema/type/proveniência adulterados coerentemente, filesextras/paths/membership, destinoexistente, troca de bytes entrehash e leitura e mutação de arquivo após carregar conexão. Abertura permanece semraw/rede.
- [x] GREEN: partição textual FIELDS32 eprojeções de cada bindingnumérico comkeys institution_id/report_id/catalog_pointer+numeric_decimal, tipo local explicitamente calculado/verificado. Headers/CSVtextual force_not_null/ordem; operações emdestinos próprios. Validar igualdadequali por célula, schema/type e reconstrução dos doisCSVadmitidos contra hashes originais.
- [x] Views `financial_cells`/`financial_observations` de texto+snapshot/source_snapshot/entity/binding/celllocators; `financial_bindings` expõeestrutura/mapeamento. Views numéricas com nomesdeterminísticos gerados deIDsinteiros confiados e tipos porbinding, sem SQLde nomes/fórmulasraw. Todasrepresentamumsnapshot, semjoinentreperíodos/perspectivas.
- [x] GREEN/self-review/testeslegados, commit doispaths e handoff; reviewTask2freshspec+qualidade, resolverP1/P2 antesTask3.

## Task 3 — Integrar APIs/CLIs financeiras existentes

**Files:** Modify dois módulosfinanceiroslegacy apenasdispatch. Ajustes de testes nas duas novas suítes somente mediantehandoff, nenhumtestelegacyreescrito porconveniência.

- [x] RED: chamadas públicas `financial.admit`/`financial_parquet.convert_financial`/validate/snapshot eCLIs existentes paraíndice/manifestcontrato novo, semflagperfil/parâmetroarbitrário. Fixtures alternamlegacy202312/Resumo202412/conjunto202412; defaults/globais/schemas e source/snapshotqualificados porcontrato exato.
- [x] GREEN: dispatch lazy/localsomentepara contratos conhecidos validados; preserve hash externo antesda seleção deadapter. Nãoafrouxar `_profile_for_selection`/width38/scopelegacy. Nenhumaprodução/coletarealnestaTask.
- [x] Rodar suíteoffline completa eguardas pertinentes uma vezapós mudanças, self-reviewdiff/allowlist, commit sódoisdispatches/testesnovosautorizados; Task3reviewindependente fresca e broad wholebranchreview apósTask4.

## Task 4 — Gate real completo, documentação e integração

**Owner:** rootintegrador. Allowlistshared/destinoprivados somenteconformeIssue42; nenhumaescrita nos códigosrevisados sem regressão/novarevisão.

- [x] Conferirperfil/fonte/codehashes/protected/destinos/disco/memórialivre e configurarprocessounico monitorado, budgetpormáquina/deadline/peak+commitmedidos por etapa. Não confundirpreflightdiagnóstico comcapacidadeintegral. Se limiteameaçado, preservarestado parcial, revercaminhotécnico e testar antesdenovorun/destino; não aumentarbudgetàscegas.
- [x] ExecutarAPI/CLIadmissão→Parquet→abertura→queries de grade/observações/metadata/bindings e tipos→replay nosdestinosnovos. Contagens reais1422/121/112/9/159264/158746/518/24, literalprovenance/lexemas/tipos/janelas e Decimalexato porbinding; fontes/perfis/snapshotslegacy/protected76 preservados.
- [x] Comparar payloadsdeterminísticos byte-a-byte, manifests UTC/hashes externos separados; registrar duração/peak/commit/I/O/disco/cardinalidades, limites/recursos eprodutopendente, commandscomdestinosagoraexistentes. Atualizarledger/README/AGENTS/arquitetura/plano pelo integrador.
- [ ] Self-reviewdo conjuntoeallowlist12paths, checks/links/diff/privacidade/sourcehashes, commitrevisável, reviewerfreshwholebranchheadexact. P1/P2corrigidos/re-revistos eCIheadfinalSUCCESS antesPRready/merge, semadmin/proteções/board. PostCI/árvores/main0/0limpas/Issue42done/mapaatualizadocomparalelismoconfirmado.

O goalcontinua parafontes/contratos202503 e escala histórica/complementares depois deste lote; não declararbaseinteiraoumetodologia concluída porum snapshotcompleto.

Checkpoint: implementação e aceite local do ciclo/replay concluídos no ledger42; revisão ampla, CI/publicação/integração têm estado verificável na Issue42.

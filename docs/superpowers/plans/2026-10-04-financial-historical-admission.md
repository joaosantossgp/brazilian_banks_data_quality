# Admissão financeira histórica — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** generalizar a admissão financeira preservacional para 66 seleções finitas e provar 202312 completo sem HTTP.

**Architecture:** registry instalado de oferta e perfis congelados por referência; compilação offline autenticada antes de instalação, contexto por chamada e reader/adapter responsáveis existentes. Os contratos anteriores permanecem no caminho original; novos snapshots têm contrato histórico próprio.

**Tech Stack:** Python 3.12, DuckDB/Parquet e unittest existentes; nenhuma dependência nova.

**Spec:** docs/engineering/financial-historical-batch-design-20261004.md, modelo lógico27 e [Issue 51](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/51).

**Execução e autoridade atuais:** modo Superpowers `subagent-driven-development`, TDD, revisão independente e integração pelo root sob o goal aprovado. Base pública `0f64dc4dc358a3a046aa5e4e3dad5f3ad74da263`, branch `codex/financial-historical-admission`. Tasks 1–3, fix de completude, perfil/registry e ajuste de representação v2 revisados independentemente e integrados localmente. Gate real 202312 passou: admissão/Parquet/query/replay de 155.120 células/154.898 armazenadas/222 ausências; 75 bindings DECIMAL, um texto exato largo e 105.260 linhas Decimal/None conferidas. Recusa inicial de largura 40 preservada como evidência; v2 adotado no adendo final. Suíte pública final, revisão whole-branch e CI/integração são etapas separadas com evidência no ledger/Issue. O planejamento original abaixo é histórico, não claim de estado corrente.

**Framing antes do freeze:** C/D/N novos/reutilizados exigem `bounded-http-archive-v1`, conclusão positiva coerente, counters/cap e sidecar físico autenticado/headers sem ambiguidade. Hashes ou header chunked isolados não comprovam completude. Conservar os cinco pins legados202312 exatos e as provas próprias de catálogo/portal congelados; não ampliar exceção a outros datasets. O builder sintético representa captura íntegra e não substitui autenticação por mock.

**Handoff de fontes:** collector50 preserva seus checkpoints/receipts A/B originais. O bundle de autoria de perfil usa também catálogo/portal já arquivados e autenticados, exigidos pelo compiler; acrescentar refs não significa recoletar ou alterar captura aceita. Um bundle derivado recebe novos pins físicos/A→B próprios e mantém a relação com os originais. Para202312, usar somente o wrapper fechado de cinco fontes/índiceSummary exato; corpos e índice originais permanecem intactos. Não presumir que B do collector sozinho satisfaz todas as fontes do perfil instalado.

**Review Focus:**

1. Fonte historicamente completa com contexto original diferente: autenticar pins sem relabel ou relaxamento global.
2. Mesmos IDs/pointers/lexemas em shards distintos: comparar origem instalada e impedir troca entre corpos.
3. Candidatos e descritores inativos: rejeitar admissão antes de fonte/perfil instalado completos.
4. Cadastro com largura e metadata diferentes: preservar campos nativos, unknowns e grupos sem padding.
5. Precisão maior que 38 ou host insuficiente: recusar aceite numérico inexato, preservar admissão/partial e diagnosticar.

---

# Admissão financeira histórica — proposta de plano técnico

> Para execução futura: usar `executing-plans` ou `subagent-driven-development`, conforme contrato da Issue real e ownership do root. Este arquivo é uma proposta privada solicitada; não inicia implementação, coleta, commit ou publicação.

**Objetivo:** generalizar o mecanismo financeiro preservacional para um registry finito de 66 referências, provar a primeira extensão real 202312 e manter os snapshots aceitos.

**Arquitetura:** lookup de descritor instalado → compilação offline de candidato C/D/O → freeze após fontes completas → perfil instalado/revisão → contexto local → reader/adapter existentes. Um único mecanismo, um snapshot por execução, Decimal por binding.

**Tecnologias:** Python/DuckDB/Parquet existentes; nenhuma dependência nova. APIs de biblioteca não são alteradas por este planejamento. Context7 entra na implementação somente se for necessária consulta de API/configuração técnica.

## Restrições globais

- Planejamento atual HTTP zero; nenhuma aquisição implícita. Execução futura de coleta pertence à Issue própria.
- Exatamente 66 referências da lista literal 47; financeiro 1005, Resumo/Ativo/Passivo/DRE com IDs/metadata respectivos. Não incluir 202609/202612, subset ou perspectiva de dados arbitrária.
- Contratos/defaults/perfis/pins 202412/202503, Summary 202312/202412 e individual preservados, sem migrar artefatos aceitos.
- Perfil instalado interno e hash verificado; candidato privado não ativa runtime; fonte incompleta não produz aceite.
- Esquema C, origens/shards, listas de perspectivas e bindings congelados por referência; nenhum proxy de período vizinho/família.
- Sem float/escala implícita, anualização, soma de filhos, deduplicação por lid, unidade/janela inventada, indicação acadêmica ou investimento.
- Grade de 32 colunas VARCHAR e tipos Decimal locais <=38; sem UNION numérica global, silencioso fallback ou retenção de 66 snapshots abertos.
- Hash externo antes de dispatch/SQL; imagens verificadas próprias, reconstrução integral, CSV streaming/release dos corpos consumidos, destinos novos e manifest por último.
- Integrador único dos shared dispatches/docs; acquisition e admission têm ownership separado. Projeto/CI/credenciais/proteções/segurança fora do recorte.

## Interfaces propostas — contrato único a consolidar pelo root

As assinaturas abaixo são novas propostas, não APIs já implementadas. Todas pertencem a `bank_quality/financial_report_profiles.py`; reader chama apenas o loader instalado no runtime. Compilação/freeze são ferramentas de autoria offline e nunca chamadas implicitamente pela admissão.

```python
def descriptor_for_selection(selection: dict) -> dict: ...
def load_installed_context(selection: dict) -> dict: ...
def wrap_legacy_202312_index(index_path: Path, *, index_sha256: str) -> dict: ...
def compile_metadata_candidate(handoff_path: Path, *, handoff_sha256: str) -> dict: ...
def freeze_profile(candidate_path: Path, final_handoff_path: Path,
                   *, candidate_sha256: str, final_handoff_sha256: str) -> dict: ...
```

`descriptor_for_selection` aceita somente membro canônico do registry instalado de oferta. `load_installed_context` exige perfil ativo/hash interno; devolve seleção, envelope/contratos/part, `cadaster_columns`, `cad_csv_fields`, mapa de membros/origens, metadata e limitações. Valores devolvidos são locais, sem mutação global. `_context(selection=None)` antigo mantém seu default; novo histórico usa seleção/contrato autenticados com loader dedicado, evitando ambiguidade de 202312 Summary.

Handoff proposto: `contract`, seleção canônica, digest do descritor instalado, catálogo com body/manifest/provenance hashes e reference pointer, `sources` ordenadas e checkpoint A. Cada fonte tem `source_id`, `role`, `area` quando numérica, anúncio/pointer/nome literal, `manifest_path` e SHA externo. Final B inclui conjunto completo requerido, falhas preservadas separadamente e SHA externo do checkpoint A. `source_id` identifica a origem; autenticidade/integridade exigem todos os hashes e contexto original.

**Âncora nova:** `manifest_path` relativo à raiz fixa deste checkout, derivada internamente pelo pacote; não aceitar root/base arbitrário no índice. Resolver somente destinos autorizados sob `data/raw/` ou `data/runs/`, recusando absoluto/URL/escape/symlink/junction; `body_path` continua contido na pasta do manifest. Índices antigos mantêm a âncora já existente. Testes usam root temporário somente por patch de constante interna. Essa âncora foi coordenada com a frente de aquisição; root fecha um único contrato antes da execução.

Checkpoint A da aquisição pode conter bindings resolvidos e shardlist, mas o compilador autentica e refaz o confronto C/D/O. Campos faltantes são erro, não resolução aceita por declaração. Candidato devolve `required_sources`, `missing_sources` e interpretações conhecidas/unknown com evidência; não produz pins fictícios para N faltante. `freeze_profile` requer missing set vazio, corpos completos e pins de fonte, mantém capturas/contextos originais e devolve artifact instalável. Ele não escreve no pacote ou altera registry automaticamente. Instalação é mudança de código/metadata revisada pelo integrador.

**Caminho independente para 202312:** o wrapper autentica o índice legado por SHA externo, confirma sua seleção original 202312/1005/Resumo 92 e os cinco manifests originais, reancora seus paths relativos ao índice para a âncora nova do checkout e mapeia numeric para `numeric:1`. Produz um handoff privado para a seleção de quatro relatórios 202312 instalada no descritor, conservando também bytes/hash/seleção do índice original e contextos das fontes. A seleção nova deriva de O autenticado; não promove as oito métricas legadas a aceite das 112 folhas. Esse wrapper não depende do checkpoint A ou do transporte novo, não executa HTTP e não modifica índice/source/manifest aceito. Perfil candidato/freeze para 202312 requerem nova conferência completa, incluindo exceções D/N exatas; ser source do Summary não é aprovação automática.

## Task 1 — registry e compilação offline sem ativação automática

**Arquivos:** novos `bank_quality/financial_report_profiles.py`, `bank_quality/financial-reports-registry.json`, `tests/test_financial_report_profiles.py`. Perfis 202412/202503 readonly. Candidatos sob destinos exclusivos `data/runs/` da execução futura.

**Entrega independente:** loader finito + compiler de metadata/freeze testados; nenhuma admissão habilitada só por catálogo.

- [ ] Escrever fixture C/D/O pequena independente: seleção 201403/1005/[1,3,4,5], cadastro 24 strings **sintético, não schema real 201403**, report membership 1004/1005, grupo/folhas e áreas 1/3, origens resolvidas, unidades/janelas desconhecidas. Repetir com cadastro 32/38 e annotations numéricas lexicais. IDs/classes da fixture não substituem metadata real.
- [ ] RED `test_registry_rejects_noncanonical_unlisted_subset_and_profile_override`: rejeitar 201003.0, perspectiva string/1004, reorder/subset, 202609/202612, path de perfil injetado, digest/hash incorretos e perfil ativo ausente antes de carregar metadata ou executar SQL.
- [ ] RED `test_candidate_missing_numeric_sources_cannot_be_frozen`: C/D/O válidos geram somente candidato; N ausente mantém `missing_sources`; tentar freeze falha sem arquivo instalado/manifest de aceite.
- [ ] RED `test_legacy_202312_wrapper_authenticates_without_acquisition`: SHA externo incorreto ou seleção/contexto/path alterados rejeitam; source bundle autenticado produz candidato de quatro reports preservando o índice Summary original, sem collector/checkpoint A. Não instala perfil nem anuncia corpo integral pronto.
- [ ] RED `test_compile_crosschecks_native_metadata`: mutar D/árvore/contexto da fonte/URL/double slash/campo de C/membership/pointer/área não anunciada; hashes coerentes novos não substituem descriptor/catalog pins. Nenhum fallback de família/vizinho.
- [ ] Rodar `.venv/Scripts/python.exe -m unittest tests.test_financial_report_profiles -v`, registrar falha por funcionalidade ausente, implementar interfaces acima e rodar GREEN. Não escrever testes que apenas espelham o número 66; verificar membros/pointers/IDs contra O/N autenticados na geração do registry.
- [ ] Conferir registry exatamente contra a lista literal 47 e catálogos congelados próprios; cada report/annotation permanece próprio. Perfis existentes ficam ativos com seus paths/hashes originais, os demais inativos. Perfil ausente não recebe SHA fake ou flag de ativação por valor truthy.
- [ ] Self-review de privacidade/inventário/hash → revisão independente exata de registry/compilação. Commit somente diff aprovado, conforme workflow; não selecionar 66 perfis que ainda não existem.

## Task 2 — reader histórico com cadastro variável e multishard

**Arquivos:** `bank_quality/financial_reports.py`; root integra ramo novo de `bank_quality/financial.py`; novo `tests/test_financial_reports_historical.py`. Sem alteração de Summary/individual/perfis antigos.

**Consome:** contexto instalado Task 1 e índice histórico completo autenticado. **Produz:** manifest histórico e cinco payloads admitidos; CSV cadastral tem a lista exata do contexto, grade conserva 32 campos.

- [ ] RED `test_historical_native_grade_keeps_variable_cadaster_and_exact_membership`: public `financial.admit` recebe índice histórico; grades sintéticas 24/32/38 passam apenas com C exato, `c0` único/opaco/`c1` literal; membership original 1004/1005 é conservada sem adquirir 1004; missing/extrafield rejeita.
- [ ] RED `test_multishard_identity_and_absence_are_scoped`: usar dois shards com e/lid/pointers iguais e valores distintos. Ambos são legítimos em suas origens; token mutado no mesmo `(source_id,c0,lid)` falha, pointer do outro shard falha; ausência da entidade somente em N3 não torna ausente N1. Duplicate e/i dentro de um shard rejeita mesmo fora das folhas selecionadas.
- [ ] RED `test_physical_source_is_required_but_unknown_semantics_is_preserved`: origem física inválida/missing bloqueia; unidade/janela unknown com motivo/pointer permanece nos metadados/CSV; número conhecido não vira BRL/ano por caption/nome do relatório. Atributo numérico continua texto; quantidade é separada; grupos não têm células.
- [ ] RED `test_source_guards_are_closed_and_legacy_exceptions_exact`: role/cardinalidade/URL/path literal/finalURL/UTC/framing/manifest/body/provenance adulterados rejeitam. Para 202312, somente D/N exatos com truncamento undeclared e contexto/diagnósticos próprios; nenhuma exceção por data em geral, nem estado promovido a false.
- [ ] Implementar seleção/contexto/schema e origem por fonte. Separar `origin_kind` físico (`cadaster`, `numeric`, `group`) de `kind`/interpretação econômica no novo perfil; projeção Decimal depende de origem numérica/quantidade, não de assumir toda td=3 monetária. As chaves/pointers de reconstrução incluem source_id.
- [ ] Processar cada shard autenticado uma vez, validar seu schema/duplicatas inteiro, reter apenas os valores necessários ao cadastro/bindings daquele snapshot e liberar a imagem consumida. Não agregar buffers de 66 referências. Preservar lexemas e metadata lexical sem float.
- [ ] Rodar `.venv/Scripts/python.exe -m unittest tests.test_financial_report_profiles tests.test_financial_reports_historical tests.test_financial_reports_202503 tests.test_financial_reports -v`; registrar total real/RED/GREEN. Alternar 202412→histórico→202503→202412 e Summary 202312/202412, conferindo defaults/contratos/metadata/hashes de bytes antigos.
- [ ] Revisão independente de conceitos/origens/schema/guardas e diff exact-head; fix P 1/P 2 exige RED/GREEN e re-review antes de corpus.

## Task 3 — adapter histórico e dispatch fechado

**Arquivos:** `bank_quality/financial_reports_parquet.py`; root integra `bank_quality/financial_parquet.py`; novo `tests/test_financial_reports_historical_parquet.py`.

**Interfaces públicas preservadas:** `convert_financial(source,destination,*,source_manifest_sha256)`, `validate_snapshot(destination,*,manifest_sha256)`, `snapshot_connection(destination,*,manifest_sha256)`. Dispatch distingue contrato histórico exato após hash externo, sem extrair ano de substring ou aceitar perfil do manifest.

- [ ] RED `test_historical_parquet_reconstructs_all_sources_and_local_decimals`: fixture multishard produz part única textual, views por binding e round-trip integral de cadastro/grade/observações/origens/metadata;1 e-27, acima de 2^53, -0.00/stringnumérica/NA/NI/null/empty/zero/ausências distintos.
- [ ] RED `test_hash_selection_contract_and_profile_precede_sql`: hashes incorretos, histórico com contrato legado ou legado com perfil histórico, membro inativo/subset de relatórios, manifest/profile e arquivo extra adulterados rejeitam antes de adapter/SQL/views.
- [ ] RED `test_owned_images_and_partial_are_preserved`: trocar arquivo externo após leitura/hash e depois de query não modifica consulta; interromper writer deixa partial semmanifest de aceite; destino existente recusa. Corpo/companion/view de fonte extra não passa inventário.
- [ ] RED `test_width_over_38_rejects_exact_conversion`: binding exigindo 39 dígitos rejeita; admissão/raw permanece; nenhum float/cast/UNION global ou fallback para omitir binding. Se algum corpo real exigir isso, criar contrato de projeção específico antes de aceitar outra representação.
- [ ] Implementar apenas diferenças de contexto/schema/origem/kinds históricos, preservando `_decimal_type`, grade ordenada, streaming/release, imagem própria em scratch e CSV reconstruction. KEYS numéricas atuais podem continuar: cada binding já fixa origem pelo perfil/grade; source_id é derivado do binding/contexto autenticados, e área/role/body/hash são os campos de origem já presentes na grade de 32 colunas, sem misturar snapshots.
- [ ] Rodar `.venv/Scripts/python.exe -m unittest tests.test_financial_report_profiles tests.test_financial_reports_historical tests.test_financial_reports_historical_parquet tests.test_financial_reports_202503 tests.test_financial_reports tests.test_financial_reports_parquet -v`; depois do código final `.venv/Scripts/python.exe -m unittest discover -s tests -v` uma vez. Não presumir total 205 após novos testes.
- [ ] Check de escopo/privacy/protected e revisão independente exact-head antes do gate.

## Task 4 — primeiro gate real pequeno e handoff de ativação posterior

**Primeiro membro:** 202312, fontes locais explicitamente indexadas, conjunto completo de quatro reports [92,96,101,98], cadastro 32. Não reutilizar o aceite Summary de oito bindings como prova do completo. Nenhum GET nesta Task.

**Perfil inicial:** novo `bank_quality/financial-reports-profiles/202312.json`; registry alterado somente para ativação deste membro após metadata/sources/review. Novo destino `data/derived/financial-historical-202312-<execução>/`, `data/curated/financial-historical-202312-<execução>/` e replay igualmente novo; a execução registra nomes concretos ausentes antes de escrever, sem sobrescrever fonte/candidato/aceite anterior.

- [ ] Autenticar C/D/O/P/N existentes em índice fechado; comprovar transporte/bytes/schema e origens completas para os 121 nós/112 folhas/9 grupos antes de instalar perfil. Recheck de toda definição/pointer/annotation/pin, sem usar somente nota Markdown.
- [ ] Separar cada exceção legada por hashes exatos/body_capture/contexto/diagnósticos; preservar truncamento desconhecido. Se fonte necessária não é demonstrável, registrar missing e parar esse gate semHTTP.
- [ ] Proteger inventário de raw/snapshots/perfis anteriores; os quatro códigos autorizados recebem before/after separado, não status de imutáveis. Integrador define inventário real, não reutiliza contagem 261 cegamente após expansão.
- [ ] Medir recursos livres/commit/disco/scratch e custo do runtime por estágio. Começar umworker, monitor da árvore própria/deadline e margem por máquina; decidir budgets concretos pelo preflight e baseline 46, sem teto universal. Capacidade inadequada preserva partial/receipt e exige diagnóstico/review. Sem gate pesado concorrente.
- [ ] Admitir, converter, abrir e comparar **todas** as linhas/32 campos textuais, cadastro nativo e cada view/Decimal com os dados admitidos. Perfil de precisão/contagens/ausências é medido dos bytes, não pré-fixado pelas contagens Summary.
- [ ] Repetir admissão/conversão em novos destinos, comparar hashes/digests de outputs descontando somente metadata de execução comprovadamente variável; medir queries integralmente e fechar connections antes de outro snapshot.
- [ ] Ledger distinguindo fixture, perfil gerado/revisto, dados adquiridos/admitidos, query/replay/gate e estado remoto. Alegações documentais sem evidência do corpus não recebem PASS. Revisão ampla whole-branch e checks/CI/publicação/integração ficam com root.

## Próxima tranche e dependências concretas

Aquisição 202403 tem C/D/shards próprios sob outra Issue. Enquanto ela desenvolve transporte/fixtures, Task 1–3 podem avançar offline com ownership separado; um contrato compartilhado de handoff é a dependência de integração. Um checkpoint A permite candidato/schema/shardlist, mas não freeze/admissão. Após final B completo, ativar 202403 por perfil próprio e diff/review, reutilizando o código já integrado. Ordem recente L1→demais lotes vem da nota 47; nenhuma lista de lote produz aceite automático dos membros.

O contrato de aquisição revisto deve registrar journal/reservas duráveis de orçamento por job, claim exclusivo, containment antes do GET e recovery offline/schema positivo. Esse código e seus controles ficam fora da allowlist desta frente. Compilação/freeze revalida fontes arquivadas e aceita somente estado final completo reconciliado do handoff, com hashes/framing e schema positivo; checkpoint interrompido não vira fonte aceita. As duas propostas podem ser concluídas independentemente, mas essa fronteira deve estar revista antes do primeiro 202403 real. Não se propõe executar aquisição em host/plataforma diferente do primeiro Windows autorizado por essa frente.

Produzir 66 resultados requer finalmente, para cada membro, fontes completas/pins, perfil ativo/revisto, origem resolvida, grade/Decimals ou contrato especial aprovado, gate/replay e manifests verificáveis. Consulta multissnapshot/harmonização é outra entrega; a presente API abre um snapshot explícito. Se um schema/origem não cabe no suporte fechado, bloquear aquele membro e criar recorte específico, sem ampliar heurística global.

## Self-review do planejamento

As dependências físicas desconhecidas estão explicitamente bloqueadas, não preenchidas com hipótese. O perfil é escrito somente após C/D/O e freeze completo; registry de oferta 66 não é registry de aceite 66. Métodos/janelas/unidades acadêmicos não foram adotados. Allowlist segue pacote/testes/destinos existentes, com pasta de perfil proposta justificada e paths compartilhados sob root. Este plano descreve trabalho futuro testável e contratos propostos; assinaturas propostas não são software já escrito, testes não foram executados e nenhuma prontidão remota foi afirmada.

## Conferência concreta de compatibilidade 202312 neste planejamento

Executado offline via `.venv/Scripts/python.exe -` com parser que rejeita chaves JSON repetidas, conferência SHA dos corpos O/D/C, traversal de todos os reports/colunas e associação integral ifd→D→campo C ou área N. Foram lidos somente O/D/C arquivados; o corpo N1 não foi lido e nenhum pipeline foi executado.

| Relatório | Nós | Folhas | Grupos | Atributos C | Quantidades C | Numéricas td=3 |
|---|---:|---:|---:|---:|---:|---:|
| Resumo 92 |17|17|0|9|2|6|
| Ativo 96 |28|26|2|9|0|17|
| Passivo 101 |33|30|3|9|0|21|
| DRE 98 |43|39|4|9|0|30|
| Total |121|112|9|36|2|74|

Todos os 121 ifd existem em D312. Os 38 bindings cadastrais usam somente `c0,c1,c2,c3,c4,c6,c10,c11,c12,c16,c17`; todos esses campos existem nos 1.385 registros C, cujo schema exato é `c0..c31`, strings e `c1='202312'`. Nenhum binding pede c32..37. Todas as 74 folhas td=3 declaram a=1. Resultado: 0 definição faltante/0 origem ou campo C inválido nesse confronto. Isso sustenta 202312 como primeiro candidato; **não prova cobertura/valores/precisão/grade integral de N1, fontes completas atuais, perfil instalado ou capacidade de execução**.

Corpos confrontados com hashes registrados nas Issues 47/34: O `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07`; D312 `11a0704ec62d3123c8af2ceb7c98b545c683781e297f8a3f4d89e449122c7ee2`; C312 `30ab717bcba0279c1d4431e40bc216293ef93407872499e95051baca09af684e`. Os manifests deram respectivamente `b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7`, `f26d028164139e20faa2094b31bab08e8fbcd1410b28bd917b406018cf2c0425`, `e9d9fa198ed547adc62367ba253bd98e026fea05c6a695b55b0a9d7eada49a8c`.

Se a conferência futura contra os bytes esperados divergir, o perfil fica bloqueado: não preencher campos, reduzir o objetivo all-vars ou aplicar D412. Explicar a lacuna e escolher outro membro pequeno completo, ou contratar classificação estrutural específica sustentada pela fonte. A conclusão positiva acima está restrita aos bytes O/D/C examinados.


**Representação de origem na grade de 32 campos:** `source_id` não é uma coluna adicional. Cada binding do perfil instalado contém `origin_source_id`; o contexto autenticado mapeia esse ID para `(role, area, body_path, body_sha256)` de modo único. A linha mantém `source_role` (numeric ou cadaster), `area`, `source_body` e `source_sha256`. A reconstrução deriva o source_id do binding e do mapa instalado, confere todos esses campos de origem da linha e então usa as chaves `(source_id,c0,lid)`, `(source_id,pointer)` e `(source_id,c0)`. Não aceita source_id declarado arbitrariamente pelo CSV ou mapa ambíguo. Campos iguais e pointers repetidos entre shards distintos são permitidos; origem trocada, inclusive com lexema igual, é rejeitada. Contratos legados conservam sua representação e suas guardas.

## Correção do contrato de origem antes do código

Ruling técnico do root: o campo source_id proposto existe no perfil e no handoff, não no CSV de 32 campos. Task 2 e Task 3 devem acrescentar teste RED `test_origin_mapping_rejects_cross_shard_swaps`: fixture N1/N3 com mesmos IDs/pointers e lexemas iguais, troca isolada de area, role, body ou hash na linha, mapa ambiguamente associado e binding com origem divergente são rejeitados. Fixture legítima conserva ambas as origens e sua ausência local. Derivar a identidade instalada e verificar a origem antes de reconstruir ou executar SQL; não criar coluna 33 ou alterar snapshots antigos.

**Precisão da ordem no adapter, registrada na Issue 51:** a conversão valida grade CSV e origens antes de qualquer SQL. A reabertura valida hash externo, contrato/perfil instalado e inventário antes de SQL, lê privadamente a grade textual Parquet por DuckDB e confronta todos os campos/origens antes de casts Decimal, projeções/views públicas ou retorno da conexão. A leitura inicial é necessária à reconstrução; não alegar origem validada antes de todo SQL na reabertura. Preservar imagens próprias e recusa de mutação coerente antes das projeções, sem nova dependência/parser ou alteração do conteúdo/aceite.

Shared docs do integrador: README.md, AGENTS.md, docs/architecture.md, este plano e docs/engineering/financial-historical-admission-20261004.md. O contrato real da51/base pública/allowlist15 e inventário protegido533 foram registrados na Issue antes da integração;7paths existentes autorizados têm hashes before separados. Não aplicar os counts261/500 de entregas anteriores como se fossem atuais.

## Ajuste técnico adotado — representação histórica exata larga

Diagnóstico real/refinamento independente confirmam que não há remoção exata de zeros capaz de fazer o binding312/98/18583 caber38. Dentroda autonomia técnica aprovada, adotar a alternativa mínima da revisão: **projeção histórica Parquetv2 explícita e accessorPythonDecimal**. Todos os dados/variáveis/estados/origens/contratosanteriores preservados; nenhum novo objetivo/método/indicador/coleta/dependência. Não oferecer SQLDECIMAL40 nativo. Alternativas rejeitadas: arredondamento/DOUBLE perderiam dados; componentesDECIMAL partidos complicam uso/validação e não resolvem aritméticaSQL comum; Arrowdecimal256 requer depnova e não prova consumoDuckDBexato; manterblocked impediria aceite semcorrigir representação.

Contrato novo exato: `ifdata-financial-reports-historical-parquet-v2`. Converter somente histórico e só quando algum binding validado exige largura>38; históricos<=38 continuamv1 com schema/bytes anteriores, legados jamais recebem exceção. Grade32VARCHAR/admissão/profile/sourcepinsimutáveis. v2 acrescenta somente top-level `numeric_projection: "mixed_exact_v1"` ao schema fechado anterior. Cada `numeric_bindings`v2 tem os campos antigos e cinco campos obrigatórios: `encoding`, `precision`, `scale`, `value_column`, `storage_type`. `precision`é largura medida max(1,inteiros+escala);`scale`inteiro medido, ambos sembool/callerchoice.

Para largura<=38: encoding`duckdb_decimal`, value_column`numeric_decimal`, decimal_type/storage_type`DECIMAL(p,s)`exato. Para largura>38: encoding`decimal_text_v1`, value_column`numeric_exact_text`, storage_type`VARCHAR`, decimal_type`null`. Textoguarda numeric_value admitido verbatim ouSQLNULL, nunca texto"null"; raw/ausência/NA/NI/zero/lexemasna gradeautoritativa. Não renomeartexto para numeric_decimal. v2 exige pelo menosumwide; todos os descriptors são recompilados da gradeautenticada/reconstruída e têm comparaçãoexata antespart/viewsaceitos. Paths/SQLselecionadossomenteprofileinstalado; rejeitar encodings/campos/type/selection/hash/originmutants e coerce via caller.

API nova no adapter existente: `iter_numeric_decimals(destination, *, manifest_sha256, binding_id=None)`. binding_id opcional é tupla exata(report_id,column_id) de doisinteiros não-bool e membroconfiável. Iteradorabre/autentica/reconstróiumsnapshot umaúnicavez, valida todosbindings antesprimeirovalor, itera emchunks bounded e fechaownedconnection emfinally/earlyclose/failure. Retornadicts com `institution_id`, `report_id`, `column_id`, `catalog_pointer`, `numeric_decimal` (PythonDecimalouNone). NativoreutilizaDecimal doDuckDB;wideDecimal(stringvalidada), semnormalize/quantize/aritmética decontexto. NenhumaUDF/castfloat; accessor não é garantia de aritméticaSQLlarganativa.

Aceite revisto: todos os155120campos32textuais/origens/cadastro/replay iguais,75typedDECIMAL+1explicittextwide na202312; leitura numérica integral de todosbindings retornaDecimals exatos viaaccessorumaabertura. SQLwidepermiteidentidade/NULL/textoexato; ordenação lexical/SUMtextual/castnão representam cálculoexato. Não sãoindicadores/cálculosdoescopodestaIssue.

Workflow do ajuste: freshimplementerTDDsomente `bank_quality/financial_reports_parquet.py`, `bank_quality/financial_parquet.py`, `tests/test_financial_reports_historical_parquet.py`; review independente desseartifact; root integra shared docs/gate scripts, reexecutaconversão emdstnovo aindaausente e query/replay/fullchecks/wholebranch/CI. Allowlist15inalterada,533anteriores+13novosaccepted/checkpointsprotegidos; antigo código doadapter antes/depois é mutableautorizado. REDwide+mixed/null/exponente/trailingzero/type/precision/originmutants/singleopen/close/contextlowprecision, GREENregressãodoscontratos anteriores; não repetirgate real oufullsuitepúblicaporimplementer. Nenhumfixfora destaallowlist semmotivação/revisãoroot. Isso generaliza suporte mecânico às próximas referências, sem66pipelines.

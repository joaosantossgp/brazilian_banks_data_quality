# Quatro relatórios financeiros202503 — execução e limites

Entrega da [Issue46](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/46), conforme [contrato43](financial-sources-202503-contract-20261004.md), [plano](../superpowers/plans/2026-10-04-financial-four-reports-202503.md) e [modelo lógico27](../superpowers/specs/2026-10-04-logical-data-model-design.md). Base pública de preparação `39de52f34f8dc174c319adf2bb260eab91c4bd09`; branch `codex/financial-four-reports-202503`; código medido `b74ea32d15a94f3f22500132096186b49f798f04`. Estado de revisão final/PR/CI/integração tem autoridade na Issue real, sem inferência por existência deste ledger.

## Resultado local verificado

Resumo119, Ativo107, Passivo110 e DRE118 financeiro202503/1005, todas as variáveis oficiais nas cinco fontes arquivadas. Cadastro1425/38campos;158nós/143folhas/15grupos;105bindings monetários/98lids,2quantidades e36atributos.203775células/202830armazenadas/945nãoarmazenadas (525entidade+420informação). Estados70668numeric/80862zero/50985text/315empty/945unobserved_cell. Grupos conservam metadata/parent/children sem células artificiais; ifd/lid e bindings repetidos permanecem distintos, sem somar/deduplicar.

| Relatório | Folhas | Células | Armazenadas | Não armazenadas |
|---|---:|---:|---:|---:|
| Resumo119 |18|25650|25587|63|
| Ativo107 |33|47025|46809|216|
| Passivo110 |31|44175|43977|198|
| DRE118 |61|86925|86457|468|

Consultas confrontaram todas as203775linhas e seus32campos textuais contra o CSV admitido, inclusive lexemas/origem/estados/IDs/pointers/fontes.107views numéricas têm152475linhas/151530Decimal não nulos/945ausências, comparadas integralmente com Decimal Python/chaves e tipos locais. Views gerais `financial_cells`, `financial_observations`, `financial_bindings` confirmaram203775/202830/158linhas. Os158nós/árvores/definições/annotations e cinco pins foram confrontados independentemente com O/D/manifest originais antes do corpus, além da validação de abertura.

## Arquitetura, contratos e fontes

Os mesmos `financial_reports.py` e `financial_reports_parquet.py` selecionam dois perfis instalados finitos por chamada, sem globals mutáveis ou profile/path arbitrário.202412 conserva defaults/contratos/constantes;202503 usa os novos contratos `ifdata-financial-reports-snapshot-202503-v1`, `ifdata-financial-reports-parquet-202503-v1` e `ifdata-financial-reports-profile-202503-v1`. Índice explícito `ifdata-financial-reports-sources-v1`. Guarda compartilhada de fonte reconhece apenas o novo contexto fechado202503 e URLs nativas; catálogo2025a2030 e prefixo literal `ifdata_2025_2030//202503/`, sem normalizar barra dupla. Summary202312/202412 e individual permanecem próprios.

Perfil `bank_quality/financial-reports-profile-202503.json`, SHA-256 LF `fc8a3007d656af499c762b1128743e24b30c843d523d99a15106d399c4e09ded`, contém somente metadata oficial e pins. Fonte shared mantém contexto/UTC original; não se relabelam1006/1005. Pins cobrem corpo, manifest e projeção completa de proveniência, sem headers/cadrows/observações públicas.

| Role | Manifest SHA-256 | Corpo SHA-256 |
|---|---|---|
| catalog | `8ab9f7f82eed8d7103525d3fb7c64e4d5150fd17a6caf6f07a6df00bc7b3bf12` | `b8977d383e4ea51f56ed391571aca7af1c109b83b9c17ceef8b926841d658206` |
| cadaster | `ffcb589bfbb52b1f4767b6a2d6c8ce83560ecd68ac2c4571f9470029d8adfce2` | `eabe1481f1d5918b8156f399638a51dc908c195a8fff737888c0a8b76b790da4` |
| dictionary | `6ece988aa9f7ac13e116e7668b04a81e68796615837cac578debb669c967c3b3` | `b8f1c2c2dc428af21367ea0dbaf0212181f160be984d258bb0af03fbd1a4fdae` |
| numeric | `095ee805cabffe42acf6bc1a7f7d59722f79fa6033856b26deaa46be81d6e382` | `8d57dd77ea0de359c9e5245c68ef79b7f2ee506232b145eee2a84a04f45515e2` |
| portal | `5757f812b56dbd414e2fa3d68075cafbf50157a010a9b4b330126fab86dd211a` | `234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153` |

Parquet: grade32VARCHAR em `parts/financial-cells-202503.parquet`,107parts numéricas e três complementos originais, mais manifest de admissão. `numeric_bindings` identifica report/column/pointer/kind/path/view/DECIMAL local; cada binding cabe38, tipo global exigiria40. Grade textual autoritativa; nenhuma coluna/cast/UNION numérica global. Abertura autentica hash externo antes de seleção/views, inventário/schema/fontes/proveniência/contagens e reconstrução/hash dosCSVs; usa imagens próprias conferidas em scratch materializadas no DuckDB em memória, sem bruto/rede/paths externos mutáveis durante consulta.

Conferidos261arquivos protegidos distintos, incluindo fontes/corpos e entregas aceitas anteriores; quatro códigos autorizados têm hashes antes/depois separados. Perfil202412, individuais, scripts, CI/política/skills/segurança/proteções/Project3 preservados. Dois novos paths perfil/teste em destinos canônicos existentes; refatoração limitada de contexto nos mesmos módulos, nenhuma nova raiz/camada/dependência/rename/delete. Ledger/plano nos destinos documentais existentes.

## Capacidade, interrupção e repetição

Primeira admissão real passou. Conversão inicial interrompida pela guarda em3,734s: orçamento805306368bytes (768MiB), agregadoWS807301120/commit799186944. Na conferência física final, o destino original `data/curated/financial-four-reports-202503-20261004/` e seu manifest estão ausentes; não houve Parquet aceito nesse run. Os recibos da interrupção foram preservados. A primeira anotação privada inferiu incorretamente pasta vazia de uma listagem sem resultados; o erratum registra essa correção. O código reserva o destino após a validação, mas os recibos não observam o instante preciso da interrupção ou existência anterior da pasta. Recibos e diagnóstico permanecem privados.

O baseline integral202412 já alcançava commit798703616 sob esse teto; os dois CSVs cresceram157421180→199976844bytes (+27%) e a grade159264→203775 (+28%). Root escolheu medir sob teto máximo já previsto1,25GiB, limitado ao livre atual−256MiB; floor768MiB para conversão/abertura, floor512MiB e teto768MiB para admissão. Revisão independente do ajuste PASS antes do run2. Nenhuma mudança de código ou novo teste artificial de configuração; monitor tinha3checks de limite/memória/sucesso PASS.

Umworker por etapa, deadline300s, livre/disco reevaluados antes de cada etapa, sem ingestão pesada concorrente. Guarda acompanha launcher `.venv` e descendentes, sampledworking-set/commit50ms e peaks internos; não é cota imposta peloSO. Budgets efetivos abaixo são por host/etapa, sem tetoRAMuniversal ou inferência de capacidade histórica.

| Etapa aceita | Guarda bytes | Duração s | Peak worker WS | Peak worker commit | Peak agregado WS | Peak agregado commit |
|---|---:|---:|---:|---:|---:|---:|
| admit-real | 778649600 | 8.354 | 573378560 | 568500224 | 577556480 | 568537088 |
| convert-real-run2 | 975831040 | 18.663 | 903270400 | 943128576 | 908226560 | 944037888 |
| query-real-run2 | 1233301504 | 22.199 | 1013538816 | 1007771648 | 1017442304 | 1007173632 |
| admit-replay | 805306368 | 8.308 | 573419520 | 568680448 | 577605632 | 568795136 |
| convert-replay-run2 | 1221111808 | 18.163 | 903929856 | 944041984 | 900730880 | 934776832 |
| query-replay-run2 | 1342177280 | 22.189 | 1014382592 | 1008205824 | 1018269696 | 1007628288 |

## Replay e comandos

Cinco payloads admitidos e111filescurated (108parts+3companions) byteiguais nos destinos novos de replay. Manifests operacionais de UTC/index/code/source-manifest são registrados separadamente; igualdade de payload não significa manifest idêntico. HTTPzero em todo ciclo.

| Manifest | Inicial SHA-256 | Replay SHA-256 |
|---|---|---|
| Admissão | `b9df726f6e137cbf35d994d0733867412c80f3bcfcad092a99591130d3e755f5` | `a1bc7c5c5ab4ab5254864c06f5d357be95f0a2e65e60d0b8f8c7214f83b8a9fb` |
| Parquet | `64d09fbaf7a40ff279cfc23e3fc002b671979585b22425c561af9138af013d6e` | `7d93aa95518d7e4609992fca4d86f2b08f95592378de4fbdca5dfda3c5d6f6f6` |

Execução real usou worker root pelas APIs públicas `financial.admit`, `financial_parquet.convert_financial` e `snapshot_connection`; monitor/receipts/índices explícitos são evidência privada ignorada, não ferramentas públicas instaladas. CLI existente foi executada sobre fixtures reais dos scripts na suíte; não afirmar CLI real do corpus. Admissão inicial `data/derived/financial-four-reports-202503-20261004/`, replay `…-replay`; Parquet aceito `data/curated/financial-four-reports-202503-20261004-run2/`, replay `…-run2-replay`.

Exemplo de reprodução com o índice local já conferido e **destinos ainda inexistentes**, não rerodar nas pastas aceitas:

```powershell
.venv/Scripts/python.exe scripts/admit-financial.py --index .superpowers/sdd/financial-four-reports-202503-20261004/source-index-real.json --output data/derived/financial-four-reports-202503-new-run
```

Conversão do manifest inicial aceito para outro destino novo:

```powershell
.venv/Scripts/python.exe scripts/convert-financial.py --source data/derived/financial-four-reports-202503-20261004 --source-manifest-sha256 b9df726f6e137cbf35d994d0733867412c80f3bcfcad092a99591130d3e755f5 --output data/curated/financial-four-reports-202503-new-run
```

Índices e dados ignorados não vêm com clone público; reconstrução exige esses cinco arquivos arquivados exatamente, respeitando seu escopo. Consulta ao snapshot aceito exige o SHA externo `64d09fbaf7a40ff279cfc23e3fc002b671979585b22425c561af9138af013d6e`; views pertencem a um snapshot, sem harmonização ou catálogo histórico global.

Suíte final205tests/41,178sPASS, incluindo55targeted/30,198s; fixtures independentes, sourceguards/seleção/alternância/CLI/schema/lexemas/typed/inventário/troca debytes/destinos e regressões antigas. ReviewTask1 independente exactheadPASSspec+qualidade; revisão de recursoPASS; review ampla/CI/integração são próximos registros verificáveis na Issue46, não assumidos pelo ledger.

## Limites de domínio e próximos lotes

UnidadeBRLcrua e estoque2025-03-31 permanecem inferidos; DRE/lucroResumo janeiro–março, sem anualização. SRCc32 e IDs/bindings nativos2025 não recebem equivalência2024. Vintage conjunta, ponte normativa/econômica, população/identidade/holding/elegibilidade/método acadêmico não são certificados por tests/hashes. Fórmulas/formatters opacos e zero/null/empty/NA/NI/ausência permanecem separados. Gate técnico completo de202503 não conclui todo o histórico2010–2026, complementares ou produto de análise consolidada.

# Quatro relatórios financeiros 202503 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Admitir e consultar os quatro relatórios financeiros nativos202503 com todas as variáveis, precisão, ausência e proveniência, conservando os snapshots/defaults anteriores.

**Architecture:** Reutilizar reader/adapter existentes com contextos locais e apenas dois perfis instalados conhecidos:202412 e202503. Cada contrato, seleção, namespace, janela e partição permanece próprio. Grade textual original e projeções numéricas por binding exato, sem união numérica entre períodos ou harmonização econômica.

**Tech Stack:** Python3.12/biblioteca padrão/unittest, DuckDB1.5.6 instalado e ParquetZSTD; nenhuma dependência nova.

**Spec:** [Contrato nativo43](../../engineering/financial-sources-202503-contract-20261004.md), [modelo lógico27](../specs/2026-10-04-logical-data-model-design.md) e desenho técnico delimitado na [Issue46](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/46). Base39de52f34f8dc174c319adf2bb260eab91c4bd09; branch `codex/financial-four-reports-202503`. João aprovou os quatro relatórios e delegou escolhas técnicas/modo/reconsideração dentro do goal. Root escolheu SDD: uma implementação coesa, revisão independente, aceite real/docs e revisão ampla final. Isso não afirma aprovação humana específica deste plano.

## Global Constraints

- HTTPzero; fontes já arquivadas O/C5/D/P/N1 exclusivamente. Seleções ordenadas e finitas:202412/1005/[92,96,101,98] e202503/1005/[119,107,110,118]. Nenhum perfil/path/período/subset arbitrário pelo índice/CLI.
- Índice `ifdata-financial-reports-sources-v1`. Novos contratos `ifdata-financial-reports-snapshot-202503-v1`, `ifdata-financial-reports-parquet-202503-v1`, `ifdata-financial-reports-profile-202503-v1`; contratos/defaults/constantes202412 e Summary202312/202412 intactos. Contextos por chamada, sem monkeypatch/globais mutáveis em produção.
- Fonte202503: catálogo `/ifdata/rest/relatorios2025a2030`; arquivos `/ifdata/rest/arquivos` com parâmetro único `nomeArquivo=ifdata_2025_2030//202503/{filename}` literal. Portal compartilhado mantém URL/contexto original. Não normalizar a barra dupla ou relabelar proveniência.
- Perfil instalado congela todas as árvores/definições/annotations e pins de corpo/manifest/projeção completa da proveniência das cinco fontes. Hash externo antes de dispatch/carga; fonte íntegra com manifest/contexto alterados continua inválida. Fonte, URL/finalURL, UTC, GET200 completo, bytes/hash/path/enquadramento e contextos são verificados.
- Cadastro202503 nativo38strings, c0único/opaco e c1literal202503. Grupos sem células; ifd≠lid, lidrepetido, report/posição e parent/children/pointers preservados. SRC2025 emc32 é namespace nativo; não equiparar2024.
- Atributos/códigos texto, quantidades distintas, dinheiro origemN1. JSONnumber/string/lexema/Decimal, empty/NA/NI/null/zero/unobserved separados. Fórmulas/formatter/rp opacos, metadata não passa por float. DRE/lucro202503 janeiro–março; estoque na referência e BRLcru inferidos; fontes com vintage não conjunta. Nenhum indicador/cálculo/filtroacadêmico.
- Grade textual com os32FIELDS existentes; novo part `parts/financial-cells-202503.parquet`. Projeção numérica por binding com DECIMAL≤38 e chavesVARCHAR; global40 não é representável. Não criar numeric_decimal global ou UNION que arredonde. Manifest/inventário exatos e escrito por último; destino novo, partial preservado.
- Abertura verifica bytes próprios/copias scratch materializadas; não lê arquivo externo mutável durante query. Reconstrução dosCSVs e hashes de todas as linhas/colunas antes de aceitar. Preservar CSVstreaming e liberação dos dois corpos já consumidos antes da projeção.
- Inventário protegido:261 arquivos distintos, incluindo fontes/corpos e snapshots aceitos anteriores. Quatro códigos autorizados têm hashes antes/depois separados. Perfil202412, individuais/scripts/CI/política/skills/segurança/credenciais/proteções/Project3/metodologia fora do diff. Nenhuma raiz/camada/rename/delete nova.
- Fixtures pequenas antes de real, nenhuma execução realTask1. Root mede ciclo integral/replay202503; umworker, deadline300s, orçamento inicial máximo1,25GiB apenas com pelo menos1,5GiBlivres e margem medida. Guarda por árvore do processo/sampling+peak interno, não cotaSO; recurso ajustável por máquina/evidência. Falha exige preservar partial, diagnóstico/teste/revisão e novo destino; não elevar às cegas.

## File Structure e ownership

| Paths | Responsabilidade/owner |
|---|---|
| `bank_quality/financial_reports.py`, `bank_quality/financial_reports_parquet.py` | Contextos/seleção fechada na admissão, validação, projeção e abertura; Task1 |
| `bank_quality/financial.py` | Dispatch e ramo fechado202503 da guarda compartilhada `_source`; Task1 |
| `bank_quality/financial_parquet.py` | Dispatch por contrato reconhecido/hash externo; Task1 |
| `bank_quality/financial-reports-profile-202503.json` | Novo perfil oficial metadata/pins, sem observações; Task1 |
| `tests/test_financial_reports_202503.py` | Novas fixtures/regressões do conjunto202503; Task1 |
| `tests/test_financial_reports.py`, `tests/test_financial_reports_parquet.py` | Ajustes somente pertinentes à compatibilidade/regressão; Task1 |
| `README.md`, `AGENTS.md`, `docs/architecture.md`, este plano, `docs/engineering/financial-four-reports-202503-execution-20261004.md` | Evidência/destinos/comandos/limites; rootTask2 |

Allowlist13paths da Issue; Task1 recebe apenas oito paths código/perfil/testes. Reuso da guarda autenticada evita duplicação: ramo novo exige contexto202503 com contrato/perfil/seleção fechados; os callers Summary existentes nunca selecionam esse contexto. Não aceitar namespace arbitrário nem afrouxar regras dos períodos anteriores. Destinos canônicos existentes, sem módulo novo.

Private `.superpowers/sdd/financial-four-reports-202503-20261004/`; derived `data/derived/financial-four-reports-202503-20261004/` e`-replay`; curated `data/curated/financial-four-reports-202503-20261004/` e`-replay`, todos novos/ignorados. Fonte de handoff `primary-sources.json`/`source-index.json`; `protected-before.json` e `approved-code-before.json` são evidência privada desta Issue.

## Review Focus

1. Alternar202412→202503→202412 conserva contrato, seleção, janela, part e defaults; Task1 testa admissão/conversão/abertura alternadas sem globais mutáveis.
2. Corpo oficial com manifest/contexto/URL/finalURL/hash alterados é rejeitado; Task1 testa fontes2024/2025, namespace errado, barra dupla e perfil/membership/annotations mutantes.
3. Externalhash incorreto, contratos misturados, tipo não canônico/subset/report/período arbitrário bloqueiam antes de adapter/views; Task1 testa APIs públicas e CLIs reais sobre fixtures.
4. Atributo com aparência numérica/SRc32, quantidades/formatter, markers/null/empty e binding repetido não viram dinheiro ou zero; Task1 testa origem/lexema/tipo/estado/ausência/janela e IDs/árvore/pointers.
5. Writer interrompido, destino existente, arquivo extra e troca de bytes após hash/leitura não produzem aceite ou consulta inconsistente; Task1 mantém/testa guardas relevantes e ownership da imagem verificada, sem repetir testes de implementação.

## Task 1 — Estender o mecanismo fechado com contexto202503

**Files:** Os oito paths código/perfil/testes acima; demais readonly. Não executar corpus real nem editar shared docs/Issue/Project/coletar. Ler contrato43, modelo27, AGENTS/workflow e handoff privado somente desta Issue.

**Interfaces:** APIs públicas preservadas `financial.admit(index_path, output)->dict`, `financial_parquet.convert_financial(source,destination,*,source_manifest_sha256)->dict`, `validate_snapshot(destination,*,manifest_sha256)` e `snapshot_connection(destination,*,manifest_sha256)->DuckDBPyConnection`. `_context(selection=None)->dict` do reader mantém default202412 e aceita apenas seleção fechada202503, carrega perfil instalado correspondente e devolve selection/contract/envelope/part/limitations locais. Helpers reader/adapter recebem contexto explicitamente onde usam período/contrato/report/part, sem substituir globais. Contexto202503 na guarda `_source(role,manifest_path,context)` só reconhece perfil/seleção fechados e URLs acima; comportamento2024 permanece. Produzir manifest/contracts/files/views qualificados por seleção autenticada e seleção sempre validada antes de trustedmetadata.

- [ ] Construir fixture pequena independente202503 com quatro IDs nativos, grupo/child/pointers, dinheiroN1/quantidade/atributosc32, ifd≠lid/lidrepetido e cadastro38. Tokens grandes/1e-27/-0.00/numericstring/NA/NI/null/empty; entidade/informação ausentes. Fonte/pins exatos sófixture; report metadata incluindo números opacos.
- [ ] RED antes de código: admissão202503 atualmente rejeitada, assertions de contrato/janelas/IDs/grade/states/c32/payload/replay/views exatas. Mutantes das cinco classes acima; fixtures alternadas2024/2025 e Summarylegado. Registrar falhas e causas; testes de corpus real não são unitários.
- [ ] Gerar perfil somente de fontes primárias O/D/pins já revisadas43, preservando metadata nativa/annotations e proveniência completa, sem cadrows/observações/headers.158nós/15grupos/143folhas reais; definição do lucroResumo ifd79859/lid141870 é fluxo, DRE118 janeiro–março, demais moneyestoque inferido; quantidadefid2, atributo demaistd1. Conferir todos os nós contra O/D, não transcrever notaMarkdown.
- [ ] Implementar parâmetros locais/contexto fechado e ramo mínimo de fonte/dispatch; cadreference/catalogannouncement/unitwindow/limitations/contracts/part percontext. Novoperfil path fixo interno; fixtures podem mockar esse path no teste, nunca índice/CLI. Conservar guardas de canonicaltypes, sourcepins, schema, inventário, metadata/pointers, CSVstream/releaseconsumedimages, externalhash antes de dispatch e exactDecimal local.
- [ ] GREEN: `.venv/Scripts/python.exe -m unittest tests.test_financial_reports_202503 tests.test_financial_reports tests.test_financial_reports_parquet -v`; todos passam e exercitam os APIs/CLIs reais sobre fixtures, sem rede/corpus. Rodar `.venv/Scripts/python.exe -m unittest discover -s tests -v` após código final; registrar total real, não assumir188. Self-review inventory/protected261/pins/metadata/publicprivacy, commit somente allowlistTask1 e report base/head/comandos/saídas/incertezas.
- [ ] Revisor fresco confere spec compliance + code quality do Task1 e perfis/fontes/fixture/riscos, diff e exacthead. Achados P1/P2 exigem RED/GREEN e re-review antes do gate real; self-review não substitui review.

## Task 2 — Aceitar o corpus/replay e integrar evidência

**Owner:** root único, shared docs/private/outputallowlist. Consome código/perfilTask1 após revisão; mudanças de código por achado voltam ao owner com teste/revisão.

- [ ] Validar fontes/pins/perfil/protected261/codehead/novosdestinos e medir memória/disco/host; preparar worker próprio e receipts, HTTPzero. Medir admissão→Parquet→abertura/query→replay sequenciais; critérios de resource no GlobalConstraints. Apenas o preflight453MiB de43 e o ciclo2024 não comprovam2025.
- [ ] Executar APIs reais sobre corpus43. Esperado:cad1425/38,158nós/143folhas/15grupos,105money/98lids+2qty+36attrs;203775cells/202830stored/945abs=525entity+420info,315empty; estados70668numeric/80862zero/50985text/315empty/945unobserved.107viewsnuméricas/152475rows/151530nonnull; grade32VARCHAR e107typedparts. Comparar todas as linhas/colunas/chaves/Decimal/metadata158 contra admissão e O/D; query sem raw/rede.
- [ ] Replay em novosdestinos: cinco payloads admitidos e111filescurated (108parts+3companions) byteiguais. Manifests operacionais UTC/hash/code/index/source-manifest podem diferir, registrando ambas hashes externas; não confundir payload determinístico com manifest idêntico.
- [ ] Documentar comandos/saídas/durações/peak/commit/disco/protected/pins/contagens/limites no ledger, README/AGENTS/arquitetura e checkboxes; preservar evidências anteriores. Registrar exacthead e revisão ampla fresca gpt6astra, diff13paths reais/privacidade/escopo/links/testes. Correções requerem regressão e revisão exata.
- [ ] PR→CIheadfinal→independentreview→merge semadmin→CIpós→tree/main0/0clean→Issue46done/mapa2 atualizado. Checker trustedbase observação/nãorequired; UNKNOWN_PR registra limitação, não mudar política/proteção. Branchpreservada/PRattached/Project3 comZec.

O goal continua para escala histórica/contratos próprios e complementares; este snapshot não conclui a base2010–2026 nem prova equivalência2024/2025. Issues com dependência/ownership compatível podem avançar em paralelo, mas ainda não há outra ingestão histórica ready; não simular prontidão por área/ausência de blocked.

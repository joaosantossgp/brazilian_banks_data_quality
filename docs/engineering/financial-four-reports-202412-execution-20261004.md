# Quatro relatórios financeiros 202412 — execução e limites

Entrega da [Issue42](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/42), conforme [contrato39](financial-four-reports-202412-contract-20261004.md), [plano](../superpowers/plans/2026-10-04-financial-four-reports-202412.md) e modelo lógico aprovado. Base pública `4b2b8baa2a8b18f2d7e38d9b26b0668eb2daca98`; branch `codex/financial-four-reports-202412`; código medido `c6ff310f53a7d3b7315623205716a26b8a40d34b`. Estado de revisão final, PR, CI e integração pertence à Issue real, não é inferido deste arquivo.

## Resultado local verificado

Conjunto financeiro nativo202412/1005: Resumo92, Ativo96, Passivo101 e DRE98, todas as variáveis oficiais disponíveis nas cinco fontes arquivadas. Cadastro1422 registros/38campos;121nós,9grupos estruturais e112folhas (74bindings monetários,2quantidades,36atributos). A grade tem159264células;158746armazenadas e518nãoarmazenadas (370entidade+148informação). Preservados61430numeric,46124zero,51168text,24empty e518unobserved_cell. Grupos conservam metadata/parent/children, sem célula artificial. Repetição de lid embindings não é deduplicada/somada; fórmulas/formatters permanecem opacos.

| Relatório | Folhas | Células | Armazenadas | Não armazenadas |
|---|---:|---:|---:|---:|
| Resumo92 |17|24174|24132|42|
| Ativo96 |26|36972|36853|119|
| Passivo101 |30|42660|42513|147|
| DRE98 |39|55458|55248|210|

As consultas compararam as159264linhas e seus32campos originais por hash canônico ao CSV admitido, incluindo lexemas, tipos de origem, estados, pointers e proveniência. As76views numéricas tipadas têm108072linhas (107554valores Decimal não nulos,518ausências), confrontadas integralmente com Decimal Python e chaves próprias. Views gerais `financial_cells`, `financial_observations` e `financial_bindings` confirmaram159264/158746/121linhas.

## Organização física e contratos

`financial_reports.py` admite o contrato fechado `ifdata-financial-reports-sources-v1`; perfil instalado `financial-reports-profile-202412.json` fixa seleção, árvores/definições/annotations e hashes completos dos cinco roles. Saída `ifdata-financial-reports-snapshot-202412-v1`: cinco payloads CSV/JSON e manifesto final. `financial_reports_parquet.py` converte/abre `ifdata-financial-reports-parquet-202412-v1`. As APIs financeiras e os dois scripts existentes delegam somente pelos contratos exatos; defaults/perfis antigos e individual continuam próprios.

O snapshot tem uma grade de32campos VARCHAR em `parts/financial-cells-202412.parquet`,76parts numéricas e três complementos originais em `metadata/`, além do manifest de admissão. Cada `numeric_bindings` contém report_id, column_id, catalog_pointer, kind, decimal_type, view, path e rows. Views/parts `financial_numeric_r{report_id}_c{column_id}` usam três chaves VARCHAR e seu DECIMAL exato. O máximo global exigiria40dígitos; cada binding cabe38. `decimal_type='per_binding'` é marcador do manifest, não tipo SQL. Não há coluna DECIMAL global nem UNION numérica que arredonde. A grade textual continua autoritativa; projeções são derivadas e verificadas.

Abertura autentica o hash externo do manifest, inventário completo/schema/fontes/contagens/payloads, reconstrói hashes dos CSVs originais e verifica os tipos físicos/valores/chaves de todas asparts. Lê imagens próprias dos bytes conferidos em `.scratch`, materializa DuckDB em memória e remove apenas esse scratch; conexão devolvida não segue arquivos externos mutáveis. Sem rede, extensão automática ou coleta. Não implanta catálogo global, sete tabelas persistidas ou consulta histórica consolidada.

## Fontes e imutabilidade

Índice explícito local inicial SHA-256 `32daa773024935273660b0ff1af0513173304aed3e21c2fd4da25cea8869a085`; perfil SHA-256 `e2423c9299caae81b02c7c95c6a57903457bb90fadccfe50f50f2e62b28c35ab`. O índice contém somente os cinco manifests locais aprovados; seus caminhos relativos podem variar, os pins/corpos/contexto/schema/URL/UTC não. Corpo shared capturado com contexto1006 mantém esse contexto original, sem relabel1005.

| Role | Manifest SHA-256 | Corpo SHA-256 |
|---|---|---|
| catalog | `b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7` | `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` |
| cadaster | `e5dc177cc63391238acb818615167359624d8ce0bb1c375fabc496a1ac2a655e` | `eec996cd9b6b219d26a7e63a1b803273ad0a418c6e022b06506f3a226b9c98e1` |
| dictionary | `45b12d698f2b6bcaae34ebf09f8d051f7fab1e3036e27ef1a147eee979b9192e` | `9c09219eeb7aa558e0ac74e32b905ba940ec00b0bc01f761b1d086aef86cca28` |
| numeric | `2e782a8c6b9fc02ad109921550a4f9ebde49cfd534a26e851e368840abbfaa07` | `c0f14556464dfd191df00d6867023fa894174b0eeb007a2bd5f5714187fa0474` |
| portal | `5757f812b56dbd414e2fa3d68075cafbf50157a010a9b4b330126fab86dd211a` | `234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153` |

Conferidos76arquivos protegidos distintos, **incluindo** dezarquivos das cinco fontes; não86arquivos. Os dois dispatches autorizados têm hashes anteriores/finais separados. Nenhum bruto, perfil legado, snapshot aceito, script, individual, CI/checker/política/skill, segurança/proteção ou Project foi alterado. Novos módulos/perfil/testes usam destinos canônicos do pacote/tests; plano/ledger nos destinos documentais existentes. Nenhuma raiz/camada/rename/delete/dependência nova.

## Capacidade medida e reparo técnico

Host Windows com7712836KiB de memória visível;1116140KiB livres antes do primeiro ciclo, disco C livre200834625536bytes. A margem disponível levou ao orçamento operacional768MiB (805306368bytes), umworker e deadline300s por etapa, revisável por máquina; não é teto universal. O monitor acompanha launcher `.venv` e descendentes Windows a cada≈50ms, soma working set/commit e termina os processos próprios ao exceder orçamento/deadline. É guarda amostrada, não cota rígida do SO; peaks internos do worker e agregados do monitor são distintos.

A primeira conversão, no código124816c, foi interrompida após1,812s com813400064bytes de working set agregado. Não criou destino/manifest Parquet aceito; a admissão concluída permaneceu intacta. Diagnóstico isolou `decode`+`StringIO`: somente a primeira linha do CSV de78847886bytes alocava393249074bytes adicionais de pico Python. Leitura incremental dos bytes autenticados com `TextIOWrapper(BytesIO(...), utf-8-sig, newline='')` preservou o hash da linha e reduziu o pico frio para63345bytes. TDD com BOM/Unicode/aspas/CRLF embutido/tokens e CSV inválido: RED6707495bytes versus orçamento524288; GREEN,81testes focados e revisão independente do reparo aprovados. O teste mede buffers transitórios; não impõe RAM universal à base.

A segunda conversão, após leitura incremental, avançou até a projeção mas foi interrompida em7,766s com826593280bytes de commit agregado. O destino parcial original ficou preservado, sem manifest aceito. Probe offline confirmou retenção de157421180bytes nas imagens dos CSVs já validados: liberar essas duas imagens antes da escrita reduziu WS620388352→462970880 ecommit614326272→456597504, mantendo159264células validadas. Reparo mínimo no adapter libera apenas os dois CSVs consumidos, mantendo os três complementos e todas as validações; regressão de memória percorre admissão/validação/conversão reais de fixture, sem afirmar chamadas a pop. Destinos novos run2/run2-replay foram registrados na Issue antes da escrita. A verificação constrói seus mapas de comparação após a abertura, evitando inflar o pico da validação com overhead do harness.

Antes da abertura/query, memória livre foi reavaliada em1704052KiB; o orçamento dessa etapa voltou ao1GiB inicialmente previsto, deixando margem para a grade DuckDB em memória coexistir com a validação e depois os mapas de comparação. Admissão/conversão mantiveram768MiB. Depois dos reparos, o ciclo completo e o replay passaram com os orçamentos explícitos abaixo e processos separados por etapa. Tempos são do worker (não incluem inicialização/monitor); bytes inteiros evitam confundir MiB/MB. Abrir/query inclui validação integral, sem depender do bruto disponível.

| Etapa | Orçamento bytes | Tempo s | PeakWS worker bytes | Peakcommit worker bytes | PeakWS agregado amostrado bytes | Peakcommit agregado bytes |
|---|---:|---:|---:|---:|---:|---:|
| admit-real | 805306368 | 7.174 | 531902464 | 526581760 | 536903680 | 527491072 |
| convert-real-final | 805306368 | 14.555 | 760647680 | 799969280 | 763760640 | 798703616 |
| query-real | 1073741824 | 17.624 | 809947136 | 802779136 | 814043136 | 802521088 |
| admit-replay | 805306368 | 7.250 | 532258816 | 527065088 | 537264128 | 527974400 |
| convert-replay | 805306368 | 13.731 | 760692736 | 800149504 | 750784512 | 775991296 |
| query-replay | 1073741824 | 17.533 | 809259008 | 801935360 | 813359104 | 801669120 |

A primeira admissão foi produzida pelo código124816c; conversão/abertura e replay pelo código acima após reparo. Manifests registram sourcehashes/code_revision/inputhash/UTC próprios; metadata declarada pelo índice não substitui comprovação do Git/receipt. Capacidade deste snapshot não prova história integral, execução concorrente ou retenção multissnapshot. O preflight de457MiB era diagnóstico, não este gate completo.

## Destinos, hashes e replay

- Admissão inicial: `data/derived/financial-four-reports-202412-20261004/manifest.json`, SHA-256 `1ba10d6b124645199d9f838c4494696a2d5fb09d0540a124ebd0ca41abfb30bc`.
- Admissão replay: mesmo nome com sufixo `-replay`, SHA-256 `2ad72f397e69f08fb119c1292c47b5579500b7424aa6f3ee9e388c5cf4d534ac`.
- Parquet inicial: `data/curated/financial-four-reports-202412-20261004-run2/manifest.json`, SHA-256 `c9d58a9a6cd105fa1b73b711ba167e6a8909e56e695f16e414e96e6e0e14cd41`.
- Parquet replay: mesmo nome com sufixo `-replay`, SHA-256 `4307ce09133d1f4c816dc01acd5f2d2d12d7c225c1a7cac40bc6c40926b93a71`.

Os cinco payloads admitidos e80arquivos Parquet/complementos (77parts+3metadata) foram iguais byte a byte. Manifest original dentro do snapshot e manifests externos podem diferir por UTC/proveniência do replay; não afirmar igualdade desses manifests. Saídas/brutos/índices/receipts operacionais são locais ignorados, não dados publicados pelo PR. Para reproduzir em outro checkout, disponibilizar as cinco fontes pelos pins acima e reconstruir o índice explícito; não iniciar nova coleta por executar estes comandos.

```powershell
# Exemplo do ciclo verificado; escolher destinos novos para repetir.
& .\.venv\Scripts\python.exe -B scripts/admit-financial.py --index .superpowers/sdd/financial-four-reports-implementation-20261004/source-index.json --output data/derived/financial-four-reports-202412-20261004
& .\.venv\Scripts\python.exe -B scripts/convert-financial.py --source data/derived/financial-four-reports-202412-20261004 --source-manifest-sha256 1ba10d6b124645199d9f838c4494696a2d5fb09d0540a124ebd0ca41abfb30bc --output data/curated/financial-four-reports-202412-20261004-run2
```

```python
from pathlib import Path
from bank_quality.financial_parquet import snapshot_connection
con = snapshot_connection(Path('data/curated/financial-four-reports-202412-20261004-run2'), manifest_sha256='c9d58a9a6cd105fa1b73b711ba167e6a8909e56e695f16e414e96e6e0e14cd41')
try:
    print(con.execute('SELECT report_id, presence, count(*) FROM financial_cells GROUP BY report_id, presence ORDER BY report_id, presence').fetchall())
    print(con.execute('SELECT report_id, column_id, kind, numeric_view, decimal_type FROM financial_bindings ORDER BY report_id, column_id').fetchall())
finally:
    con.close()
```

Execução real monitorada usou as APIs públicas acima em worker próprio; testes end-to-end executaram os scripts reais via `runpy`/argparse somente com fixture/perfil mockado no teste. Não atribuir às CLIs uma execução real que foi da API. Suite completa após reparos:188testes Python PASS; três guardas Node PASS no head de dispatch anterior, sem alteração Node posterior. `git diff --check`, pins/protected/replay/queries conferidos. Revisões por tarefa são distintas da revisão ampla/CI/integração final registradas na Issue42.

## Limites econômicos, contábeis e de produto

BRL cru e estoque na referência têm base inferida explicitada; lucro/DRE de dezembro preservam julho–dezembro, sem anualização. Vintage conjunta não comprovada; desconhecido não vira zero, negativo, exclusão ou elegibilidade acadêmica. Nenhuma fórmula, equivalência de regime/perímetro, harmonização2025, vínculo holding/listagem ou indicador foi criado. Fontes/cadastro202503 têm contrato próprio na43; ainda não são valores admitidos por esta implementação. O histórico trimestral2010–2026 e complementares permanecem entregas posteriores do goal; um snapshot completo não encerra a base.

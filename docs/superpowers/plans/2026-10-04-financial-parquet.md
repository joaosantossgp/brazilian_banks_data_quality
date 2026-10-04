# Parquet financeiro 202412 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Converter a admissão financeira 1005/92/202412 em snapshot Parquet verificável e consultável, preservando integralmente tokens, estados, grade e proveniência.

**Architecture:** Um adapter financeiro isolado materializa a grade uma vez e expõe observações por view em DuckDB em memória. Manifests e hashes explícitos delimitam entrada/saída; o hash final é calculado externamente, sem autorreferência. Os contratos individuais e a admissão financeira existente permanecem intactos.

**Tech Stack:** Python 3.12, biblioteca padrão, DuckDB 1.5.6 já instalado na `.venv`, Parquet ZSTD, unittest; sem novas dependências/servidor.

**Spec:** [Modelo lógico aprovado](../specs/2026-10-04-logical-data-model-design.md), [ADR 0001](../../adr/0001-duckdb-parquet.md), [contrato financeiro](../../engineering/financial-snapshot-202412-contract-20261003.md) e [entrada admitida](../../engineering/financial-snapshot-202412-execution-20261003.md).

**Tarefa:** [Issue 29](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/29); branch `codex/financial-parquet-202412`, base documental `fe3d3223c7306a4c394a2cf156610e5ac3b84ee0`. **Estado: plano escrito para revisão de João; implementação não iniciada.** A aprovação do modelo em 2026-10-04 é anterior e distinta dessa revisão.

## Global Constraints

- Somente financeiro / Resumo / 1005 / 92 / 202412; contrato de origem `ifdata-financial-snapshot-202412-v1`.
- Entrada local: `data/derived/financial-202412-20261003/`, manifest SHA-256 `f46858edc76c2e9d1d619b40fcdfaa083792cd7664a146d5d6dcaed5ae106043`.
- 1.422 registros, oito variáveis, 11.334 observações; grade 11.376 e 42 posições sem armazenamento. Não impor essas contagens reais às fixtures sintéticas.
- Estados: `numeric`, `zero`, `NA`, `NI`, `NA_percent`, `NI_percent`, `json_null`, `literal_null`, `blank`; presença `stored`, `entity_not_stored`, `information_not_stored`; ausências diretas com `unobserved_cell`.
- Tokens/tipo fonte preservados; Decimal exato complementar, sem float/arredondamento. Perfil real `DECIMAL(35,22)`; precisão necessária maior que 38 rejeita a conversão.
- Lucro conserva `ifd=79718`, `lid=78187`, janela julho–dezembro; unidade monetária inferida e vintage não conjunta continuam limites, sem promoção a anual/comparável.
- Códigos literais são ocorrências no snapshot, sem identidade transversal, exclusão acadêmica, joins CVM/B3 ou indicadores.
- Sem coleta, migração de legados, catálogo global, seleção `latest`, consulta multissnapshot ou ponte 2025 neste recorte. Os demais cenários da spec pertencem a adapters/contratos futuros.
- Destinos novos ignorados em `data/curated/` e `data/runs/`; não sobrescrever bruto, CSV/JSON, manifests ou snapshots anteriores. Aceite exige marcador final completo; falha pode deixar diretório parcial para diagnóstico.
- Allowlist pública: os três arquivos novos de código/CLI/testes abaixo; README.md, AGENTS.md, docs/architecture.md, spec acima, este plano e `docs/engineering/financial-parquet-20261004.md`. Nada em CI/política/checker/skills/credenciais/proteções. Documentos compartilhados têm um integrador neste lote.

## Review Focus

1. Manifest correto com CSVs coerentemente adulterados: conferir hashes/tamanhos e seleção antes da projeção; Task 1, `test_input_hash_and_semantic_guards`.
2. IDs ambíguos e grade duplicada: rejeitar padding/colisão/duplicata, sem deduplicar nem multiplicar fatos; Task 1, `test_literal_keys_and_grid`.
3. Exponente extremo, zero negativo e marcadores percentuais: perfilar sem expansão descontrolada, preservar token e usar NULL tipado só nos estados não numéricos; Task 1, `test_exact_decimal_and_markers`.
4. Interrupção ou corrida pelo destino: nenhum consumidor aceita parcial ou marcador substituído; Task 1, `test_new_destination_and_final_marker`.
5. Arquivo Parquet incidental ou complemento alterado na leitura: ler somente arquivos do manifest validado e exigir hash final esperado; Task 2, `test_explicit_snapshot_and_tampering`.

---

## Mapa físico e interfaces decididas

Criar somente `bank_quality/financial_parquet.py` (validação/conversão/leitura reutilizável), `scripts/convert-financial.py` (entrada CLI) e `tests/test_financial_parquet.py` (fixtures temporárias offline e comportamento). Não copiar helpers privados de `parquet.py`, mudar `financial.py` ou criar pasta pública de fixtures por conveniência; constantes públicas da admissão podem ser lidas sem alterá-las.

Contrato de saída: `ifdata-financial-parquet-202412-v1`. Arquivos declarados: `parts/financial-cells-202412.parquet`, `metadata/source-manifest.json`, `metadata/financial-cadastro.csv`, `metadata/financial-variables.json`, `metadata/financial-diagnostics.json`, mais `manifest.json` final. Complementos e manifest de origem são cópias byte a byte. O Parquet conserva as 32 colunas originais (`financial.FIELDS`) como VARCHAR e acrescenta `numeric_decimal`; não substituir `numeric_value` textual.

Manifest final: contrato/seleção, UTC de execução, versão/hash LF do adapter e DuckDB, hash do manifest de origem, inventário dos cinco arquivos de entrada, cinco arquivos de saída com hash/tamanho, contagens por presença/estado, tipo Decimal, digest das linhas originais e limites preservados. Digest: SHA-256 de JSON UTF-8 com `ensure_ascii=False`, separadores `(',', ':')`, sem newline, contendo listas de valores em ordem FIELDS e na ordem original de `financial-cells.csv`. O hash desse manifest só vai ao retorno da API/CLI/ledger, nunca ao próprio arquivo.

Views `financial_cells` e `financial_observations` preservam os campos físicos e acrescentam: `snapshot_id` (hash final conferido), `source_snapshot_id` (hash do manifest admitido), `entity_locator` (pointer cadastral `/n`, associação literal única), `binding_locator` (catalog_pointer validado) e `cell_locator='single'`. Observações filtram `presence='stored'`. Uma chave completa é `(snapshot_id, entity_locator, binding_locator, cell_locator)`. Código/IDs/nome da variável são atributos; não criar sete tabelas só porque a spec tem sete conjuntos lógicos. A proveniência completa continua nos complementos/manifest e nos pointers originais.

### Task 1: Validar entrada e converter a grade exata

**Files:** Create `bank_quality/financial_parquet.py`; Test `tests/test_financial_parquet.py`.

**Interfaces:** Consumes o diretório admitido e seu hash externo. Produces `convert_financial(source: Path, destination: Path, *, source_manifest_sha256: str) -> dict`, retornando o manifest completo mais `manifest_sha256` calculado após escrita; arquivos acima sustentam Task 2.

- [ ] **Step 1: Escrever testes RED em unittest com fixture sintética independente.** Fixtures geram cadastro, oito bindings e grade completa nos formatos aceitos, manifest final e hashes; não importar uma classe de testes existente como API. Fixar assertions:

```python
# test_exact_decimal_and_markers: conferir cada token e tipo fonte preservados.
self.assertEqual(row['raw_value'], '9007199254740993.0100')
self.assertEqual(row['numeric_decimal'], Decimal('9007199254740993.0100'))
self.assertEqual(tiny['numeric_decimal'], Decimal('1.10e-18'))
self.assertEqual(negative_zero['raw_value'], '-0.00')
self.assertIsNone(na_percent['numeric_decimal'])
# test_literal_keys_and_grid: sem renormalização ou deduplicação.
with self.assertRaisesRegex(ValueError, 'duplicate'):
    convert_financial(source, target, source_manifest_sha256=expected_hash)
```

Cobrir todos os estados/presenças, exponentes que exigem precisão >38, source_kind incoerente, hash externo errado, arquivo/hash/tamanho ausente/divergente, path fora do destino, JSON com chave duplicada, cabeçalho/seleção/contrato errados, observações diferentes da projeção stored, célula faltante/duplicada, código literal inválido e binding/pointer/unidade/janela divergentes. `test_new_destination_and_final_marker`: destino existente falha, corrida tem um único reservador, erro antes do marcador deixa snapshot não aceito, marcador pré-existente não é substituído. Mutantes semânticos recalculam hashes para provar validação além da integridade.
- [ ] **Step 2: Rodar RED:** `.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_financial_parquet.py -v`; esperar falha de import/API ausente, sem coleta.
- [ ] **Step 3: Implementar `convert_financial(...)` no módulo decidido.** Capturar cada entrada em bytes uma vez, validar manifest/hash e exatamente os cinco nomes/headers; validar grade cadastro × bindings, projeção stored, metadados e perfil existentes. Associação cadastro/valor por código literal único; comparar atributos/pointers de células a bindings e fontes do manifest, sem reler raw. A confiança é no hash da admissão aceita, não uma segunda aquisição/conferência econômica. Duplicatas/erros devem falhar, sem fallback.
- [ ] **Step 4: Implementar projeção/escrita dentro do mesmo módulo.** Perfilar Decimal a partir dos tokens de numeric/zero, corroborando `numeric_value`; dimensionar inteiro+escala por tupla Decimal antes de expandir exponente. Gravar Parquet com schema explícito e ZSTD; comparar linhas originais e Decimal em round-trip antes do aceite. Copiar complementos/manifest original, calcular hashes/digest e publicar o manifest por último com arquivo pendente fsync e hardlink exclusivo, como a admissão existente. Reservar destino sem `exist_ok`; não reutilizar snapshot financeiro nesta versão.
- [ ] **Step 5: Rodar GREEN:** mesmo comando da Step 2, todos os testes desta tarefa passam. Registrar RED/GREEN e `git diff --check`; não executar corpus real ainda.
- [ ] **Step 6: Commit:** `git add bank_quality/financial_parquet.py tests/test_financial_parquet.py`; `git commit -m "feat: convert admitted financial snapshot to exact Parquet"`.

### Task 2: Validar leitura, expor chaves/views e CLI

**Files:** Modify `bank_quality/financial_parquet.py`; Create `scripts/convert-financial.py`; Test `tests/test_financial_parquet.py`.

**Interfaces:** Consumes saída de `convert_financial(...)`. Produces `validate_snapshot(destination: Path, *, manifest_sha256: str) -> dict` e `snapshot_connection(destination: Path, *, manifest_sha256: str) -> duckdb.DuckDBPyConnection`. O chamador fecha a conexão; erros de leitura/contrato não viram dados vazios. CLI exige `--source`, `--source-manifest-sha256` e `--output`; sucesso imprime JSON de contagens/hash final, erro previsto ValueError/OSError sai com código 2 e diagnóstico visível.

- [ ] **Step 1: Acrescentar testes RED para leitura/chaves/CLI.** Fixar assertions:

```python
# test_snapshot_views: hash externo separa execução de identidade econômica.
self.assertEqual(cells_count, expected_grid)
self.assertEqual(observations_count, expected_stored)
self.assertEqual(distinct_complete_keys, cells_count)
self.assertEqual(snapshot_ids, {result['manifest_sha256']})
# test_explicit_snapshot_and_tampering
with self.assertRaises(ValueError):
    validate_snapshot(target, manifest_sha256='0' * 64)
```

Verificar ligações /n e catalog_pointer únicas, códigos desconhecidos mantidos, zero/NULL distinguíveis, lucro 79718/78187 com julho–dezembro, hash final ausente/divergente, parte/complemento/cópia do manifest alterados, parte extra não declarada ignorada, schema Decimal/linha/chave/contagem/digest divergentes mesmo sob hash final recalculado. Copiar só a saída para outro diretório sem a entrada/raw: leitura segue íntegra e não depende dos paths históricos. CLI por subprocesso em outro cwd: argumentos obrigatórios/erro visível/nenhuma saída aceita em falha/sucesso com hash conferível.
- [ ] **Step 2: Rodar RED:** `.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_financial_parquet.py -v`; esperar falha das APIs/views/CLI ausentes, preservando Task 1 GREEN.
- [ ] **Step 3: Implementar `validate_snapshot(...)`.** Exigir hash externo, contrato/seleção e inventário exatos; validar arquivos/schema, complementos, contagens, digest das 32 colunas, bindings/cadastro e equivalência Decimal antes da consulta. Corroborar os três complementos com hashes do manifest original copiado; preservar seus limites e fontes. A validação é de integridade/contrato, sem alegar autenticidade.
- [ ] **Step 4: Implementar `snapshot_connection(...)`.** DuckDB `:memory:`, threads=1, desativar instalação/carregamento automático de extensões e limitar acesso externo aos arquivos explícitos antes de desligá-lo. Construir associação temporária cadastro→entity_locator somente após prova 1:1, criar views com parâmetros para valores/paths e nomes fixos; `read_parquet` sem glob/hive_partitioning. Não unir diretórios/revisões implicitamente. Esta API não é sandbox para SQL arbitrário com privilégios.
- [ ] **Step 5: Implementar CLI fina**, importando a API pela raiz do projeto como `admit-financial.py`; nenhuma lógica financeira duplicada no script.
- [ ] **Step 6: Rodar GREEN:** mesmo comando da Step 2, todos passam; `git diff --check`. Commit dos três arquivos com mensagem `feat: validate and query explicit financial Parquet snapshots`.

### Task 3: Provar equivalência offline e integrar a entrega

**Files:** Create `docs/engineering/financial-parquet-20261004.md`; Modify README.md, AGENTS.md, docs/architecture.md e este plano (execução/estado). Spec só muda se houver correção aprovada, sem alterar modelo por conveniência.

**Interfaces:** Consumes as três APIs das Tasks 1–2 e CLI. Produces ledger com entrada/head/hashes/contagens/limites/comandos/saídas, revisão independente e publicação confirmadas.

- [ ] **Step 1: Revisão independente do código no head exato.** Conferir Issue/allowlist/arquitetura/precisão e testes de comportamento; resolver achados antes de converter corpus aceito. Executar uma vez `.venv\Scripts\python.exe -B -m unittest discover -s tests -v`, `node tests/test-budget.cjs`, `node --test tests/test-portal-ready.cjs` e `git diff --check`; ampliar somente se houver nova mudança/falha.
- [ ] **Step 2: Capturar hashes protegidos em preparação privada.** Inventariar arquivos da admissão financeira e replay, seus cinco corpos/manifests de aquisição referenciados, inventário/Parquet individual aceitos; registrar contagem real e hashes antes/depois. Não escrever nesses destinos. Conferir ausência dos três novos destinos, `.gitignore`, versão DuckDB e hash da entrada. Atualizar a data/destinos da Issue antes de escrever se a execução ocorrer após 2026-10-04; nunca apagar/reutilizar destino existente.
- [ ] **Step 3: Executar conversão e replay**, uma execução por destino novo:

```powershell
.venv\Scripts\python.exe -B scripts/convert-financial.py --source data/derived/financial-202412-20261003 --source-manifest-sha256 f46858edc76c2e9d1d619b40fcdfaa083792cd7664a146d5d6dcaed5ae106043 --output data/curated/financial-parquet-202412-20261004
.venv\Scripts\python.exe -B scripts/convert-financial.py --source data/derived/financial-202412-20261003 --source-manifest-sha256 f46858edc76c2e9d1d619b40fcdfaa083792cd7664a146d5d6dcaed5ae106043 --output data/curated/financial-parquet-202412-20261004-replay
```

Esperar sucesso/JSON e manifests completos; registrar os dois hashes finais, sem embutir no próprio manifest. Comparar cinco saídas byte a byte e projeção exata; manifests podem diferir por UTC. Não ocultar divergência Parquet: se a serialização não for determinística, registrar/explicar e revisar antes do aceite.
- [ ] **Step 4: Consultar cada snapshot via API com hash esperado**, em helper privado sob `data/runs/financial-parquet-202412-20261004/`. Conferir grade=11.376, observações=11.334, ausências=42 (30 entity_not_stored e 12 information_not_stored), cadastro=1.422, bindings=8 e tipo DECIMAL(35,22). Comparar integralmente as 32 colunas/Decimal com CSVs admitidos e provar unicidade das chaves; demonstrar lucro 79718→78187/julho–dezembro e NULL sem zero-fill. Medir bytes, tempo de conversão/consulta e ambiente, sem extrapolar capacidade para toda a história.
- [ ] **Step 5: Registrar evidência e atualizar entradas.** Hashes protegidos iguais antes/depois; publicar só ledger sanitizado, código/testes e documentos permitidos. Guardar logs/dados privados ignorados. Marcar Tasks concluídas com evidência; registrar que engenharia não prova comparabilidade econômica, vintage conjunta, elegibilidade ou ponte 2025.
- [ ] **Step 6: Revisar diff/head final, publicar PR e integrar.** Revisão independente cobre inclusive ledger/documentos e inventário added/modified; exigir CI aprovada no head entregue. Integrar autonomamente no escopo aprovado, verificar CI pós-merge e sincronizar main/origin. Só então encerrar Issue 29 com status:done e links confirmados; Project /3 segue com Zec. Se a etapa documental foi integrada antes, o PR do código fecha esta mesma Issue.

## Revisão do plano e documentação técnica

Auto-revisão writing-plans é inline: cobertura do recorte mapeada às Tasks 1–3; demais famílias/método/multissnapshot explicitamente adiados; interfaces/nomenclatura consistentes; cinco Review Focus ligados a testes; nenhum corpo de implementação transcrito. Conferência independente de publicação não substitui a revisão do plano por João.

Recomendação de execução: **Native**, um executor para as duas tarefas do mesmo módulo e revisão independente do conjunto antes do corpus real e da integração. João ainda pode escolher Subagent-driven; a escolha deve ficar registrada antes do código.

Context7 consultado na preparação: `/duckdb/duckdb-web`, APIs Python/read_parquet/COPY. Referências oficiais: [Python API](https://github.com/duckdb/duckdb-web/blob/main/docs/current/clients/python/reference/index.md), [DB API](https://github.com/duckdb/duckdb-web/blob/main/docs/current/clients/python/dbapi.md), [tipos numéricos](https://duckdb.org/docs/current/sql/data_types/numeric). Conferir APIs contra DuckDB 1.5.6 instalado ao executar; documentação current não substitui testes da versão local.

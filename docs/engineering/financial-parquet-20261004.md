# Parquet financeiro 202412 — execução offline de 2026-10-04

[Issue 29](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/29), [plano autorizado](../superpowers/plans/2026-10-04-financial-parquet.md), [modelo lógico](../superpowers/specs/2026-10-04-logical-data-model-design.md) e [ADR 0001](../adr/0001-duckdb-parquet.md). João autorizou execução Native após esclarecer objetivo e disposição dos dados. Base de implementação `0981987f6e38bc61a960b8385ad6d01946206ccf`; código executado `7a98e5e0ff1ba1e7ca93626023460ef66de13f31`. Resultado local concluído; revisão final, PR, CI e integração são registrados na Issue real, sem confundir esta evidência local com confirmação remota.

## Entrada e resultado

Somente admissão aceita `data/derived/financial-202412-20261003/`, contrato `ifdata-financial-snapshot-202412-v1`, seleção financeiro/Resumo/1005/92/202412. Hash externo do manifest: `f46858edc76c2e9d1d619b40fcdfaa083792cd7664a146d5d6dcaed5ae106043`. Nenhum HTTP/coleta ou alteração da admissão, bruto, perfil e conversor individual.

| Conferência | Resultado em ambos os destinos |
|---|---|
| Cadastro / bindings | 1.422 / 8 |
| Grade / observações armazenadas | 11.376 / 11.334 |
| Sem armazenamento | 42: 30 `entity_not_stored`, 12 `information_not_stored` |
| Estados | 9.015 `numeric`, 2.319 `zero`, 42 `unobserved_cell` |
| Tipo complementar | `DECIMAL(35,22)`, sem float/arredondamento |
| Equivalência | Todas as 32 colunas e todos os Decimal iguais à admissão |
| Chaves / janela | 11.376 chaves completas únicas; lucro 79718→78187 conserva julho–dezembro |
| Replay | Cinco saídas byte a byte idênticas; manifests diferem somente por UTC |
| Preservação | 51 arquivos protegidos, hashes antes/depois iguais |

Os 51 protegidos incluem admissão/replay financeiros, cinco corpos/manifests de aquisição referenciados, snapshot Parquet individual, inventários individuais equivalentes e quatro arquivos de implementação/perfil existentes. Lista e hashes completos ficam em evidência privada ignorada; este ledger não publica observações ou corpos brutos.

## Estrutura e consulta

Contrato novo `ifdata-financial-parquet-202412-v1`: uma grade em `parts/financial-cells-202412.parquet`, três complementos financeiros e cópia do manifest de origem em `metadata/`, mais `manifest.json` final. Complementos são cópias exatas. As 32 colunas `financial.FIELDS` permanecem VARCHAR; `numeric_decimal` é o único campo físico acrescentado.

`financial_cells` expõe 38 colunas: as 33 físicas mais `snapshot_id`, `source_snapshot_id`, `entity_locator`, `binding_locator` e `cell_locator`. `financial_observations` filtra `presence='stored'`. Grão: ocorrência IF.data × variável × célula dentro do snapshot. A chave completa usa snapshot/ocorrência/binding/célula; código cadastral não ganha identidade entre períodos. A API exige hash final externo e valida arquivos, contrato, schema, tokens, Decimal, grade e reconstrução dos CSVs originais antes de consultar. Copia os bytes Parquet verificados para imagem transitória própria em `.scratch/`, materializa em DuckDB em memória e remove a imagem; a conexão não passa a ler arquivos mutáveis durante consultas.

```python
from pathlib import Path
from bank_quality.financial_parquet import snapshot_connection

with snapshot_connection(
    Path('data/curated/financial-parquet-202412-20261004'),
    manifest_sha256='6ef6872f082aaa75864565af8e53c5206a2d174b1644ee2f3eafa59f2c031e17',
) as con:
    print(con.execute('SELECT count(*) FROM financial_cells').fetchone())  # (11376,)
    print(con.execute('SELECT count(*) FROM financial_observations').fetchone())  # (11334,)
```

## Reprodução e hashes

Os comandos abaixo foram executados uma vez por destino novo, com sucesso e stderr vazio. **Esses destinos agora existem e são aceitos; para repetir, escolher outros destinos ausentes.** Logs/receipts e conferência integral estão em `data/runs/financial-parquet-202412-20261004/` e no workspace privado do plano, ignorados pelo Git.

```powershell
.venv\Scripts\python.exe -B scripts/convert-financial.py --source data/derived/financial-202412-20261003 --source-manifest-sha256 f46858edc76c2e9d1d619b40fcdfaa083792cd7664a146d5d6dcaed5ae106043 --output data/curated/financial-parquet-202412-20261004
.venv\Scripts\python.exe -B scripts/convert-financial.py --source data/derived/financial-202412-20261003 --source-manifest-sha256 f46858edc76c2e9d1d619b40fcdfaa083792cd7664a146d5d6dcaed5ae106043 --output data/curated/financial-parquet-202412-20261004-replay
```

Hash do manifest final principal: `6ef6872f082aaa75864565af8e53c5206a2d174b1644ee2f3eafa59f2c031e17`; replay: `cd94ac609075b5cd86b32a01d4cb69896090db392615d2d294db6a721e28e561`. Calculados externamente, sem autorreferência. Adapter v1, hash de fonte LF: `40b39b7318d00419382f8ea006bd86fdfa74b5acb3b7fc8659a30bfae40fc22d`.

| Arquivo relativo ao snapshot | Bytes | SHA-256, igual no replay |
|---|---:|---|
| `parts/financial-cells-202412.parquet` | 252.894 | `044c501283326439d2f9604db9d31d246c38fbd9c03efb31da7e12e5cef04561` |
| `metadata/source-manifest.json` | 6.904 | `f46858edc76c2e9d1d619b40fcdfaa083792cd7664a146d5d6dcaed5ae106043` |
| `metadata/financial-cadastro.csv` | 676.222 | `211d865e09d6d2bd95ac1150e2ca8b45f45e10887be3ab9be5a49d6bff9dc194` |
| `metadata/financial-variables.json` | 6.308 | `2cb1ced7fed01b7061f311ca66961f27aafe3815ed7b98099ebb460d6545d841` |
| `metadata/financial-diagnostics.json` | 2.820 | `914a9c917abfdbc8e28709d4f70055cc6ef21c15aeb7d6d6a32751d967e0aa7a` |

## Validação, medidas e limites

Windows, Python 3.12.14, DuckDB 1.5.6 local, threads=1. Suíte final: `.venv\Scripts\python.exe -B -m unittest discover -s tests -v` → 141 testes PASS em 12,219 s; subset financeiro 21 PASS, também confirmado pelo reviewer no head exato. `node tests/test-budget.cjs` e `node --test tests/test-portal-ready.cjs` → PASS (dois testes de portal); `git diff --check` → PASS. TDD incluiu mutantes de integridade/semântica/precisão/destino/CLI e corrida entre hash e leitura; o achado independente P2 dessa corrida foi reproduzido RED e corrigido GREEN antes da execução real. Conferência independente pré-corpus confirmou `7a98e5e`; revisão documental final/publicação têm autoridade na Issue/PR.

| Medida, uma execução por destino | Principal | Replay |
|---|---:|---:|
| Conversão CLI | 133,793596 s | 135,031218 s |
| Abertura com validação | 1,727353 s | 1,727192 s |
| Consulta de contagens após abertura | 0,008823 s | 0,004228 s |
| Snapshot, incluindo manifest final | 948.833 bytes | 948.833 bytes |

O CSV original da grade tem 5.584.099 bytes; o Parquet tem 252.894 bytes. Duas novas saídas acrescentam 1.897.666 bytes, além dos logs locais; nada foi removido. Medidas pontuais, sem série de benchmark, medição de RSS ou promessa de capacidade/velocidade para toda a história.

Este resultado prova integridade, conversão exata e consulta de **um** snapshot. Não prova unidade monetária oficial (inferida), vintage conjunta, lucro anual, autenticidade além do hash confiado, universo elegível, durabilidade contra perda de energia ou comparabilidade econômica. Cadastro/dicionário/valores mantêm geração desconhecida; report conserva sua geração/versão original. História 2010–2026, prudencial, contratos individuais adicionais, cadastro temporal, ponte 2025, vínculos CVM/B3 e apresentação analítica com variáveis em colunas exigem entregas próprias. O modelo lógico não é sete tabelas físicas implantadas.

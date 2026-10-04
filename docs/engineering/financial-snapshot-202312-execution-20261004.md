# Snapshot financeiro 202312 — execução offline de 2026-10-04

[Issue 36](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/36), [contrato](financial-snapshot-202312-contract-20261004.md), [plano](../superpowers/plans/2026-10-04-financial-snapshot-202312.md), [modelo lógico](../superpowers/specs/2026-10-04-logical-data-model-design.md) e [ADR 0001](../adr/0001-duckdb-parquet.md). Base `7545fc5cfa9d2235ba605c500503bdbedf56d931`, branch `codex/financial-snapshot-202312`. Execução inline dentro da autonomia técnica autorizada por João para o goal em 2026-10-04. Resultado local aceito; revisão do head exato, PR, CI e integração têm registros próprios na Issue real. Esta nota não confirma estado remoto.

## Entrada e resultado

Cinco fontes locais do contrato 34, seleção explícita `202312/1005/92`, sem HTTP ou nova coleta. Índice de produção com paths relativos ao próprio índice, separado do índice diagnóstico. O perfil fechado `financial-profile-202312.json` exige cadastro nativo de 32 campos; o perfil 202412 continua com 38. Defaults e APIs 202412 preservados. Reader v2; adapter Parquet v3.

| Conferência | Resultado nos destinos novos |
|---|---|
| Cadastro / bindings | 1.385 / 8 |
| Grade / observações armazenadas | 11.080 / 11.062 |
| Sem armazenamento | 18 `entity_not_stored`, estado `unobserved_cell`, Decimal null |
| Associação literal | ifd 79718 → lid 78187 |
| Lucro em dezembro | Julho–dezembro de 2023, sem anualização |
| Decimal físico | `DECIMAL(37,24)`, derivado exato; lexemas originais conservados |
| Chaves completas únicas | 11.080 na consulta validada |
| Replay da admissão | Cinco payloads byte a byte idênticos |
| Replay final Parquet | Part e quatro complementos byte a byte idênticos à primeira conversão |
| Preservação | 49 arquivos imutáveis e cinco inputs do contrato, hashes iguais; snapshot aceito 202412 revalidado |

O inventário anterior de 51 hashes também incluía `financial.py` e `scripts/admit-financial.py`, códigos explicitamente autorizados para mudança nesta Issue. Seus hashes anteriores/finais ficam na evidência de implementação; os outros 49 continuam protegidos. Não afirmar que 51 ficaram imutáveis. Perfil 202412, dados/raw/derivados aceitos e conversor individual não foram alterados. Nenhuma raiz/camada, rename, delete ou dependência nova.

Dois manifests legados, D/N1, não declaram truncamento: o perfil fixa os hashes exatos dos corpos **e dos manifests**, diagnóstico/contexto de captura, URLs/status/schema revistos. Proveniência mantém `undeclared_legacy` e bytes decodificados, sem inventar `truncated=false` ou alegar captura comprimida de rede. Exceção exclusivamente 202312; adulteração coerente das fontes ou da proveniência do manifest admitido falha. Unidade BRL crua continua inferida do formatter, vintage não conjunta e ausências não são zero/NI.

## Medidas e ajuste técnico

Windows, Python 3.12.14, DuckDB 1.5.6 local, threads=1. Duas admissões: 3,875 s e 3,687 s; cada destino contém 11.189.403 bytes. Conversão inicial por binding de arrays Python em lotes: 134,000 s e 131,313 s. Os destinos iniciais foram preservados para comparação, sem substituição.

O gargalo justificou revisar a escrita antes de escalar. Ensaio offline de carga CSV levou 0,406 s de escrita e produziu o mesmo part byte a byte. A implementação usa CSV temporário próprio dentro do destino novo, schema de colunas original explícito, `force_not_null` nos campos textuais, Decimal derivado por cast exato, `parallel=false`, modo estrito e preservação da ordem de inserção. A conexão restringe os arquivos à área própria e conserva bloqueio de extensões/acesso externo. Aspas, vírgulas, Unicode, multilinha, strings vazias e Decimal null têm teste de regressão. O temporário é removido após fechamento da conexão; não é payload aceito. [Documentação oficial DuckDB consultada via Context7](https://duckdb.org/docs/stable/data/csv/overview.html).

| Medida final, uma execução por destino | Principal `-bulk` | Replay `-bulk-replay` |
|---|---:|---:|
| Conversão completa | 1,344 s | 1,109 s |
| Abertura com validação | 1,687 s | 1,672 s |
| Snapshot, incluindo manifest | 915.451 bytes | 915.451 bytes |
| Parquet | 259.921 bytes | 259.921 bytes |

Part e quatro complementos coincidem byte a byte com o baseline que usa a mesma admissão. Os manifests finais diferem por UTC e versão/hash do adapter; cada um exige hash externo próprio. As primeiras duas admissões têm UTC distintos: seus manifests não são prometidos idênticos. São medidas pontuais de um snapshot, sem RSS, benchmark histórico integral ou promessa de velocidade universal. Paralelismo continua opção para lotes independentes após medir capacidade por máquina; não foi necessário para resolver este gargalo.

## Reprodução e consulta

As APIs `admit`, `convert_financial` e `snapshot_connection` foram executadas diretamente pelo executor privado, com as mesmas entradas e guardas das CLIs finas. Comandos equivalentes abaixo; **os destinos registrados já existem**, portanto escolher destinos ausentes para novo replay. Índice e raw permanecem privados/ignorados; clonagem somente do código não contém dados aceitos.

```powershell
.venv\Scripts\python.exe -B scripts/admit-financial.py --index .superpowers/sdd/financial-202312-implementation-20261004/source-index.json --output data/derived/financial-202312-20261004
.venv\Scripts\python.exe -B scripts/convert-financial.py --source data/derived/financial-202312-20261004 --source-manifest-sha256 af9e42c2404a2e3799c202705fe4cde4cca5160dfab1c332db099ab4415096a0 --output data/curated/financial-parquet-202312-20261004-bulk
```

Manifest admitido principal: `af9e42c2404a2e3799c202705fe4cde4cca5160dfab1c332db099ab4415096a0`; replay: `b1959c91305b256786973f0d1cc63af93a93878334305156155e4dee3c2a939f`.

Manifest final principal: `1e7839e149a971807518d9459e7354676dadf8c06b5071ddf813fe6e88f34fc9`; replay: `9d7ed027356390a715fea60d276296b7368b957b5a5a51c58f21ac1c508f267d`. Part em ambos: `f1647a2c842e549a153e3b29bdef1119d4d21f10c3546d302da962f589c4a630`. Hashes calculados externamente, sem autorreferência. Receipts dos quatro destinos Parquet e duas admissões ficam no workspace privado, sem publicar corpos ou observações.

```python
from pathlib import Path
from bank_quality.financial_parquet import snapshot_connection

with snapshot_connection(
    Path('data/curated/financial-parquet-202312-20261004-bulk'),
    manifest_sha256='1e7839e149a971807518d9459e7354676dadf8c06b5071ddf813fe6e88f34fc9',
) as con:
    assert con.execute('SELECT count(*) FROM financial_cells').fetchone() == (11080,)
    assert con.execute('SELECT count(*) FROM financial_observations').fetchone() == (11062,)
```

Contrato próprio `ifdata-financial-parquet-202312-v1`, part `parts/financial-cells-202312.parquet`, cadastro/dicionário/diagnósticos e manifest de origem em `metadata/`. As 32 colunas de células continuam texto; cadastro 32/38 é outro schema. A view acrescenta identificadores snapshot/ocorrência/binding/célula. Abertura exige hash esperado, valida seleção/contrato/inventário/schema/valores/chaves e reconstrução dos CSVs; carrega imagem verificada em memória, conservando o snapshot original. Uma conexão representa um snapshot, sem join temporal automático.

## Validação e limites

TDD com RED/GREEN em admissão e Parquet, mutações de legado/referência/manifest/schema, ordem canônica cadastral, precisão/ausências e CSV em lote. Suíte final local: `.venv\Scripts\python.exe -B -m unittest discover -s tests -v` → **149 testes PASS**, 9,427 s. Guardas de orçamento Node e dois testes de prontidão do portal → PASS; arquivos Node não mudaram na otimização. Revisão independente e checks remotos são registrados separadamente na Issue/PR.

Esta entrega prova integridade técnica, reprodução e consulta de **Resumo com oito variáveis em 202312**. A frente financeira aprovada exige Resumo, Ativo, Passivo e DRE oficiais, todas as variáveis disponíveis e contratos próprios, nas referências disponíveis do alvo trimestral 2010–2026; continua pendente. Prudencial/individual complementares, contrato 2025, comparabilidade, cadastro temporal, vínculos CVM/B3, elegibilidade/indicadores acadêmicos e apresentação histórica têm recortes próprios. A [pesquisa normativa paralela 37](financial-2025-normative-bridge-20261004.md) esclarece a ausência de correspondência direta AA–H/estágios e registra lacunas de versão/dicionário; não harmoniza dados nem conclui a Issue 16. Project /3 com Zec.

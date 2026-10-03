# Conversão offline DuckDB + Parquet — 2026-10-03

Entrega local no branch `feat/offline-duckdb-parquet`, ainda sem publicação. [ADR aceito](../adr/0001-duckdb-parquet.md), [desenho](../superpowers/specs/2026-10-03-offline-parquet-design.md), [plano](../superpowers/plans/2026-10-03-offline-parquet.md) e [medidas JSON](../../reports/offline-parquet-20261003.json) são o contrato e a evidência. Tarefa local ainda não publicada como Issue. Revisão independente e verificação final serão registradas ao concluir.

## Conteúdo e integridade

Snapshot `data/curated/offline-pilot-20261003/snapshot`: 40.904 observações individual/Resumo, sendo 15.808 em 201012, 12.416 em 202312 e 12.680 em 202412. Todos os 16 campos originais são VARCHAR, com perspectiva `individual` e projeção numérica `DECIMAL(37,24)`. Comparação integral verificou cada campo original e cada valor Decimal. IDs, unidade, token exibido, estado, corpo e hash fonte permanecem; nenhum float foi introduzido pela conversão. Não há arquivo .duckdb nem consulta a novos dados externos.

Estados preservados: numeric 31.846, zero 6.127, blank 2.685, NI 246. NA/NI_percent/json_null/literal_null/invalid e limites decimais são exercitados por fixtures sintéticas; sua cobertura em testes não afirma presença no piloto. Ausência estrutural permanece no CSV complementar, sem linha financeira fabricada. A conversão preserva o inventário aceito; não corrige eventual precisão perdida anteriormente ao produzir tokens por float, nem valida comparabilidade econômica ou unidade final da monografia.

O replay executado neste trabalho reproduziu os sete arquivos byte a byte a partir da evidência arquivada. A retomada verificou esses sete arquivos novamente, sem repetir o replay. Todos os hashes de entrada coincidem com o perfil capturado antes de qualquer mudança. 260 arquivos em data/raw foram comparados por hash antes/depois da finalização, sem mudança. O original do rascunho de ADR foi preservado em backup local; pesquisa e nota financeira anterior também mantiveram seus hashes.

Coordenador reserva destino novo por mkdir exclusivo; cada worker escreve sua partição e fecha a conexão. Hashes, conteúdo, schema, contagens, unidades/IDs e DECIMAL são verificados antes do manifesto. `manifest.json` escrito por último, com fsync de arquivo e rename no mesmo diretório, marca aceite; isso não promete transação entre arquivos nem durabilidade de diretório/power loss. Diretório parcial e manifesto inválido/corrompido são rejeitados. Reuso idêntico verificou hashes e mtime sem alteração.

## Espaço medido

| Camada, sem sobrepor subtotais | Bytes lógicos | MiB |
|---|---:|---:|
| Bruto existente. respostas e auxiliares | 126.437.764 | 120.58 |
| Derivados anteriores. CSV/JSON (inclui inventário fonte) | 160.415.231 | 152.98 |
| Snapshot ativo completo | 1.496.082 | 1.43 |
| Cópia de replay retida | 18.986.490 | 18.11 |
| Benchmarks aceitos duplicados | 2.992.164 | 2.85 |
| Staging interrompido retido. sem aceite | 136 | 0.00 |
| Ambiente .venv do projeto | 50.550.084 | 48.21 |

As observações CSV têm 18,267,701 bytes; os três Parquet, 773,981 bytes, redução de **95.76% no formato das observações**. O inventário fonte completo tem 18,986,490 bytes e está incluído nos derivados anteriores. O snapshot completo inclui Parquet, seis arquivos complementares preservados, manifesto e reserva. Metadados/falhas originais do bruto permanecem, assim como todas as versões aceitas.

Não houve redução efetiva total no SSD: novos dados/replay/benchmarks retidos somam 23,474,872 bytes, e .venv soma 50,550,084, total adicional dessas duas camadas **74,024,956 bytes (70.60 MiB)**. Código, documentos e ledgers não estão nesse delta; não foi capturado baseline do volume inteiro. Bytes são tamanhos lógicos reais de arquivos, não espaço alocado por cluster, pico temporário/RSS ou estimativa de todo o histórico. Nenhuma cópia foi apagada para melhorar o resultado.

## Conversão e consulta

Uma execução completa por configuração: **262,8081 s (1 worker)** e **274,8610 s (2 workers)**, uma thread DuckDB por conexão. Ambas têm o mesmo hash lógico `3a3b1f6099ca95b665ecc1c02bfb9cd1a3ffcaf40cd2abbef138ec4569ad56e0` e arquivos idênticos. Nesta amostra não houve ganho com dois workers; o padrão permanece um. Não extrapolar uma única medição, cache aquecido, ordem fixa ou custo desta implementação de binding para toda a história.

A programação inicial de seis repetições foi encerrada após os dois resultados úteis. Um terceiro destino já reservado ficou com 136 bytes, sem manifesto e sem aceite; preservado e contabilizado. O script agora limita execução a uma por configuração e grava recibos por execução. A finalização recuperou os tempos arredondados a quatro casas do log original, validou os dois snapshots e mediu reuso/consultas/bytes; não executou nova conversão. O erro inicial de caminho relativo foi reproduzido e corrigido por teste de regressão.

Na conexão em memória já validada, cinco consultas com fetch: mediana **3.575 ms** para contagem por estado/referência e **44.791 ms** para seleção numérica 202412 (12,638 registros). Abrir e validar o snapshot custou **0.6726 s**, medido separadamente. Tempos incluem cache do sistema e retorno a Python; não são benchmark de SSD frio nem cálculo de indicadores. SQL exato e cada observação de tempo estão no JSON.

## Verificação e limites da entrega

TDD comprovou RED→GREEN para precisão/estados, publicação, falha de rename, corrupção, reuso, concorrência, CLI e regressão do benchmark. Concorrência real entre publicadores e fronteiras de 38 dígitos/24 casas também foram verificadas. A suíte final e a revisão independente serão registradas após sua execução, sem promover checks remotos ou publicação.

DuckDB oficial 1.5.6, wheels Python 3.12 Windows amd64/Linux x86_64 pinados por SHA-256 em requirements-duckdb.txt. Instalação apenas na .venv, sem dependências transitivas novas. [Documentação oficial Python](https://duckdb.org/docs/current/clients/python/overview), [Parquet](https://duckdb.org/docs/current/data/parquet/overview) e [DECIMAL](https://duckdb.org/docs/current/sql/data_types/numeric) foram conferidas com Context7 e a versão realmente instalada. Licenças das nove skills Matt e demais notices existentes ficaram intactas; isso não escolhe licença do código próprio.

Sem alteração de bruto/CSV/JSON aceitos, coleta externa, capítulo, amostra/vínculos novos, calendário, projetos pausados, servidor, permissões, push/PR/merge/deploy. O contrato continua restrito a individual/Resumo e às três referências existentes.

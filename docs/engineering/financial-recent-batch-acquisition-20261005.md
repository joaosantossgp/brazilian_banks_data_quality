# Aquisição financeira recente por janela — 2026-10-05

[Issue 54](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/54), [plano único](../superpowers/plans/2026-10-05-financial-recent-batch-acquisition.md) e [arquitetura](../architecture.md). Resultado real local concluído; revisão do conjunto, publicação, CI e integração são estados separados, confirmados na Issue/PR. Project /3 permanece com Zec.

## Resultado e fronteira

A janela cobre onze referências: 202312, 202403, 202406, 202409, 202412, 202503, 202506, 202509, 202512, 202603 e 202606. Reutilizou quatro conjuntos sem GET: Parquet financeiro aceito de 202312/202412/202503 e fontes aceitas de 202403. Coletou e validou cadastro C, dicionário D e valores N1 dos sete restantes. Todos os catorze resultados de fase são completos; não há períodos faltantes, reservas pendentes, falhas ou halt.

| Referência adquirida | GETs | Bytes de corpos | Segundos de tentativa contabilizados | Sequência final do membro |
|---|---:|---:|---:|---:|
| 202406 | 3 | 16.441.414 | 12 | 9 |
| 202409 | 3 | 16.720.041 | 14 | 9 |
| 202506 | 3 | 15.696.537 | 10 | 9 |
| 202509 | 3 | 15.937.630 | 13 | 9 |
| 202512 | 3 | 17.133.647 | 13 | 9 |
| 202603 | 3 | 17.025.275 | 12 | 9 |
| 202606 | 3 | 16.628.036 | 11 | 9 |
| **Soma** | **21** | **115.582.580** | **85** | **28 no coordenador** |

Não houve backoff, retry ou nova requisição aos quatro reusos. As três entradas Parquet continuam sendo os únicos snapshots financeiros completos admitidos dessa janela. 202403 e os sete novos são **fontes**, ainda sem perfil/admissão/Parquet novos. A [Issue 55](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/55) trata 202403; admissão dos sete tem contrato posterior. Oferta de 66 referências, fonte arquivada, perfil instalado e cobertura admitida são estados distintos.

Os journals registram 21 reservas e 21 conclusões: reservas brutas de 2.520 s de tentativa e 543.162.368 bytes de corpos; consumo observado de 85 s e 115.582.580 bytes. A soma dos tempos nativos medidos é 74,425012 s; a contabilização por tentativa arredonda para cima. Overshoot zero, nenhum deadline atingido, 21 árvores extintas e todos os workers exit0. Reservas brutas não são consumo final nem renovação de orçamento.

## Domínio e integridade

Perspectiva financeira 1005, quatro relatórios nativos e todas as suas variáveis: Resumo/Ativo/Passivo/DRE com IDs `[92,96,101,98]` em 202406/202409 e `[119,107,110,118]` nos cinco períodos a partir de 202506. O prefixo literal `ifdata_2025_2030//` conserva a barra dupla. Cada cadastro/dicionário pertence à sua referência; áreas numéricas foram resolvidas pelo D próprio antes do GET de valores. Não se herdou N1 ou esquema por nome de outro período.

Capturas preservam URL/parâmetros, recuperação UTC, status/headers/diagnósticos, contexto e hashes dos corpos/manifests/proveniência. A autoridade autentica cada recibo e o prefixo do journal; B aponta ao A físico da mesma referência. Metadados de membership 1004 não autorizam coleta prudencial. Cadastro, origem e schema nativos passaram nas guardas de aquisição; contagens da grade, ausências, precisão, unidade/janela e tipos consultáveis pertencem à admissão posterior. Isto não harmoniza regimes, transforma dezembro em resultado anual, escolhe amostra ou estabelece joins acadêmicos.

## Execução e recursos medidos

Código de execução congelado no commit `5c0257789a3a6f54f8fbe98f95cef4eb4a68cf75`, com os cinco arquivos de execução, executável Python e policy fisicamente pinados. Inicialização offline criou as sete autoridades e um bundle exclusivo; nenhuma autoridade/budget anterior foi renovada. A CLI recusou code-pins no diretório privado de preparação antes de mutação. A API revisada `_initialize_batch` recebeu os mesmos pins, e os inputs foram copiados para `preparation/` somente depois da criação exclusiva do run. A restrição de raiz da CLI foi preservada.

Um diagnóstico operacional privado usou os seams revisados do coordenador, sem alterar código de produção: metadata1 de 202406, pausa em fronteira concluída, par metadata2 de 202409/202506 e depois scheduler da janela com os quatro metadados restantes e values1. Todas as metadata7 terminaram antes do primeiro valor. As pausas conservaram budgets, claims, journals, recibos e resultados; nenhum arquivo foi baixado para repetir um benchmark. Cancelamento por recursos combina o evento do monitor e o evento nativo do scheduler, com encerramento da árvore inteira.

O operador recebeu revisão independente depois de corrigir enumeração de processos, tratamento de falhas/término, margens iniciais, persistência de erros tardios e largura registrada. Sete probes offline passaram no artefato final; não foram tratados como capacidade BCB. As medidas reais seguintes são amostradas, incluindo coordenador e descendentes; picos observados são limites inferiores, não máximos matemáticos.

| Execução real | Pico WS da árvore, MiB | Pico commit privado, MiB | Mínimo físico livre, GiB | Mínimo commit disponível, GiB | Tempo incluindo provas/cleanup |
|---|---:|---:|---:|---:|---:|
| Metadata1 inicial | 185,96 | 169,05 | 1,376 | 8,710 | 19,250 s |
| Par metadata2 | 294,84 | 252,44 | 1,313 | 8,577 | 23,301 s |
| Restante metadata2 + values1 | 699,91 | 695,12 | 0,779 | 8,045 | 197,618 s |

Soma dessas execuções: 240,168 s, aproximadamente quatro minutos. Isso inclui preparação de fases, autenticação de reusos, validação, monitor e cleanup; não é comparação controlada de throughput1 versus2. Árvores próprias extintas, nenhum erro do monitor/cleanup ou guarda acionada. Os 85 s contabilizados de tentativa não são o tempo total de parede.

Margens explícitas desta máquina: 512 MiB físico livre, 1.024 MiB commit disponível e 4.096 MiB de disco livre; ajustáveis por evidência, sem teto universal de RAM. Disco livre mínimo observado: 200.055.549.952 bytes. Inventário dos diretórios do run e das sete autoridades depois do handoff: 197 arquivos, 733.576.667 bytes; exclui bindings/claims no pai, preparação privada, ferramentas e atividade alheia. Corpos somados não são teto de artefatos/disco. Caps autorizados permanecem 14 tentativas/330 MiB de corpos/1.680 s de tentativa+35 s backoff por membro, sem promessa de SLA de parede.

## Comandos e pins efetivamente usados

Run local ignorado: `data/runs/financial-historical-acquisition-202312-202606-20261005/`. Bundle e bootstrap não incluem seus próprios hashes externos:

| Artefato | SHA-256 físico |
|---|---|
| `bundle.json` | `557e4fbc22b552c4ec3179d39560c17d6c0ea8ec4102c971f602705a1a25c890` |
| `bootstrap.json` | `ac04474c43a17920e30597724e922c8a1f36c6b3999d6bc2b462b443dfb04bd3` |
| `preparation/code-pins.json` | `4042c8af451d74051e18b078613a49b29599789415c2ed61d0351f61a4274154` |
| `preparation/draft.json` | `777fc0c8097166dad2270244835ab8432624db106c175af1be74234d889d0d69` |
| `handoff.json` e reconstrução `handoff-replay.json` | `5b7fb2274f336e02dcbc8bb22e0e25f1c95587fed83b9178ff272c113b99bfc5` |

Depois da captura, a CLI suportada percorreu o mesmo lote completo, autenticou inputs/reusos/recibos/checkpoints/fontes e devolveu os mesmos campos públicos/counters em 76,367 s, exit0, sem nova tentativa/GET. `halt` interno é omitido da saída sanitizada por contrato, não uma diferença de estado. O comando efetivo foi:

```powershell
& .\.venv\Scripts\python.exe -B scripts/acquire-financial.py batch-run `
  --bundle data/runs/financial-historical-acquisition-202312-202606-20261005/bundle.json `
  --bundle-sha256 557e4fbc22b552c4ec3179d39560c17d6c0ea8ec4102c971f602705a1a25c890 `
  --bootstrap-sha256 ac04474c43a17920e30597724e922c8a1f36c6b3999d6bc2b462b443dfb04bd3 `
  --metadata-workers 2
```

É registro de uma execução concluída sob HEAD/runtime pinados, não instrução para renovar a janela. `batch-prepare` produz draft sem autoridade; `batch-initialize` exige destino/binding novos e code-pins externos em raiz permitida. `batch-run` reconcilia todos os inícios pendentes antes de despachar e exige HEAD/código/runtime atual aprovados antes de GET. `batch-recover` escreve recibo novo, sem reset/refund; resultado inconclusivo mantém halt/reservas. `batch-verify` é inspeção offline e exige os bytes/runtime do bundle, sem exigir HEAD histórico para essa leitura. Outros períodos/janelas exigem contrato próprio; não há `latest` ou calendário futuro implícito.

O handoff tem onze entradas, distinguindo Parquet reutilizado, fonte reutilizada e fonte recém-adquirida. Foi reconstruído por nova leitura de bundle/journal/A/B/recibos/heads em destino novo, após autenticação offline dos corpos; bytes e hash iguais. Journals correntes continuam nos mesmos prefixos de recibos, sequências/counters, sem novas tentativas. Artefatos, paths privados e corpos não são publicados no Git.

## Verificação e integração

Tasks1–3 tiveram revisão independente dos artefatos exatos. Task3: 211 testes de quatro módulos PASS em 91,828 s, zero skips, mais quatro probes independentes PASS em 7,680 s, incluindo cancelamento/crash de duas árvores nativas Windows. Isso é verificação pertinente, não a suíte completa. Root conferiu 733 arquivos protegidos antes da coleta, sem diferenças; resultado local/código revisado não afirma CI ou publicação.

Suíte offline final: **455 testes PASS em 258,176 s, exit0, sem skips**. Checks Node `tests/test-budget.cjs` e `--test tests/test-portal-ready.cjs`: exit0. Conferência dos83 links locais dos quatro documentos e `git diff --check`: PASS. Nenhum código mudou depois desses checks; revisão independente do conjunto e estado remoto de PR/CI/merge/pós-merge têm autoridade na Issue real. Capturas e evidência privada permanecem fora do Git. O próximo passo de dados é perfil/admissão/Parquet das fontes completas; o objetivo histórico66 e complementares separados continua ativo.

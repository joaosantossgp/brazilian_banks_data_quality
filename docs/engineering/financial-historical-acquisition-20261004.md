# Aquisição financeira histórica: prova 202403

[Issue 50](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/50), [plano](../superpowers/plans/2026-10-04-financial-historical-acquisition.md) e [inventário de lotes](financial-historical-batch-design-20261004.md). Execução local em 2026-10-04, capturas UTC 2026-10-05. Este registro distingue a prova real de fonte, os testes offline e a publicação.

## Resultado e limites

O job fechado financeiro 202403/1005/[92,96,101,98] adquiriu C/D antes de resolver N. Dos cinco shards numéricos anunciados, somente N1 era necessário aos quatro relatórios. Foram **3 GETs, 3 tentativas, 16.342.157 bytes**, sem retry, falha ou pendência. Cadastro nativo: **1.397 registros e 32 campos**; árvores: **121 nós, 112 folhas e 9 grupos**, com 38 origens cadastrais e 74 numéricas.

N1 conserva **4.315 entidades e 744.797 valores nativos**, inclusive entidades fora do cadastro financeiro selecionado. Para os 74 bindings numéricos requeridos, 103.230 posições encontram valores e 148 ficam explicitamente ausentes. Essas contagens são validação física da fonte; não são a grade admitida inteira. O reader financeiro, a interpretação das quantidades/atributos e o Parquet histórico têm a [Issue 51](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/51). Nenhum perfil 202403 foi ativado por esta prova.

`source_complete`, `source_validated` e `origin_resolved` estão comprovados neste recorte. Não se afirma admissão financeira, comparabilidade, equivalência entre regimes, resultado anual, amostra acadêmica ou aquisição das 66 referências. Os snapshots anteriores permanecem separados e protegidos.

## Fontes e pins externos

Catálogo O congelado: corpo SHA-256 `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07`, anúncio `/96`. Reports Resumo/Ativo/Passivo/DRE: pointers 29/32/12/33. Prefixo nativo `ifdata/202403/`; nenhuma atualização de catálogo, trel, sel ou filtro foi solicitada.

| Origem | Pointer no catálogo | Arquivo nativo | Bytes | SHA-256 do corpo |
|---|---|---|---:|---|
| C | `/96/files/0/f` | `cadastro202403_1005.json` | 634.072 | `20e29f0221483f2e81266deb3cb7bcbd31a77a07993d2913c3839a61eea512e2` |
| D | `/96/files/9/f` | `info202403.json` | 174.579 | `11a0704ec62d3123c8af2ceb7c98b545c683781e297f8a3f4d89e449122c7ee2` |
| N1 | `/96/files/3/f` | `dados202403_1.json` | 15.533.506 | `b3da5094a8388db0392c3e57567f375a39a82534e1d2795800f3fc658b9435d0` |

As URLs, recuperação UTC, HTTP status/headers originais, diagnósticos, hashes físicos e proveniência completa são conservados nos manifests privados referenciados pelo handoff. HTTP 200 e JSON válido não bastam: as três capturas têm contrato `bounded-http-archive-v1`, framing positivo autenticado por Content-Length, corpo íntegro e schema físico aprovado. Os hashes da tabela vieram dessas capturas autenticadas.

Pins fixados na Issue antes do GET:

- Codehead executado: `1a5a4e4d22195c234e510055c0dd4a72865c9cec`.
- Job canônico: `b16a582e865f6de1f097820f67fa9b063b5be9fe5ddf0be8dc617415f864c4de`; arquivo do job: `43f775d20a4dd9cf686f975c2232a39b26a3f9afb23ff9732e920c5bb9296ed5`.
- Bootstrap: `026d372570fff21a53d3b59fbf9acf1a164adb377e810811965d80e3251a5a9c`.
- Checkpoint A físico: `51993dc1e9e8a0edd7361b6f297566fbf5a53a0c1feb4bf90fca77a3f9c124f0`; receipt metadata: `3357ff2d3719a2a4c51f61d299947adf856e949124afb83f3c7c5f06b6994536`.
- Checkpoint B físico: `f30878c4e4cdcae135913351652a707bc0398bbde006f42a283fac8a2f009373`; receipt values: `9f380fb46aa7455b5156e739c885d2c5041a12a13c22c22f36229e69ecfaf429`.

O hash externo do job é canônico, distinto do hash físico do arquivo. Preparação offline mantém `executable:false` e não cria autoridade. Inicialização explícita cria binding/bootstrap exclusivos; repetir não renova orçamento. A autoridade atual fica em `data/runs/financial-acquisition-authority/<job_sha256>/`, com binding e claim do scope no diretório pai.

Capturas imutáveis de tentativa ficam em `data/runs/financial-historical-acquisition-202403-20261004/<session>/attempt-<id>/`; corpo, manifest e sidecar são parte da evidência dessa execução. A mudança de layout foi registrada na Issue antes da aquisição. Não há promoção/movimento automático para `data/raw`, admissão ou publicação. Sessions reais novas: `metadata-real-01` e `values-real-01`; o job fica em `preparation/job.json`.

## Retomada, despesas e contenção

Houve interrupção real entre metadata e values. A segunda fase fixou A e o receipt por SHA externo, reautenticou C/D e fez somente o GET de N1. A verificação posterior do receipt metadata reportou `receipt_is_historical:true` e as despesas atuais de 3 tentativas/16.342.157 bytes; não restaurou o saldo antigo. Recovery offline sem pendências escreveu receipt novo, conservou as mesmas despesas e foi verificado. Não houve GET adicional nessas operações.

O parent é o único escritor do journal. Reserva durável precede nascimento; PID/creation-time são commitados antes de liberar o worker. Claim Win32 exclusivo, associação ao Job Object no nascimento suspenso e `KILL_ON_JOB_CLOSE` impedem fallback não contido. Worker exige reserva/head/ancestralidade atuais; execução standalone não autoriza rede. Recovery conserva despesa pendente e não inicia transporte.

Políticas fechadas: duas tentativas por target, C/D até 5 MiB cumulativos por target, N até 64 MiB por shard, timeout de rede 30 s, deadline de tentativa 120 s e backoff até 5 s. O resolver reduziu o teto teórico de 14 GETs/330 MiB para o conjunto necessário. Despesa real: 14 segundos cobrados às três tentativas, zero backoff/falha. Deadline e bytes são despesas distintas de tempo total ou de memória.

## Recursos medidos nesta máquina

Diagnóstico anterior offline/localhost: job autenticado e fixture de 16 mil valores/497.829 bytes, pico de processo 122.486.784 bytes, zero GET BCB. Não é aceite de N real ou capacidade máxima. Antes da fase real, o host Windows 11 tinha aproximadamente 1,79 GB físicos livres; antes de values, 1,70 GB. Sem outro gate pesado concorrente.

| Fase real | Tempo monitorado | Pico agregado amostrado WS | Pico agregado amostrado commit |
|---|---:|---:|---:|
| Metadata C/D | 3,766 s | 180.137.984 bytes | 146.731.008 bytes |
| Values N1 e validação | 16,656 s | 697.356.288 bytes | 693.522.432 bytes |

Um worker de rede. Budget desta árvore: min(1,25 GiB, memória física livre − 256 MiB), com piso de início 512 MiB e reserva de commit 512 MiB; nas duas fases coube 1,25 GiB. Watchdog privado da execução conserva partial/reserva se interromper a árvore própria. A amostragem não é quota de memória do SO nem teto universal; não demonstra que vários parsers simultâneos cabem neste host. Download e validação/admissão/conversão terão concorrências medidas separadamente no lote seguinte.

## Validação de software, revisão e remoto

Suíte completa no codehead executado: **339 testes PASS / 105,054 s / zero skips no Windows**, mais **3 testes Node PASS**. Testes nativos cobrem claim, identidade antes de resume, falha de commit/resume, deadline, crash antes/depois da liberação, launcher/descendentes extintos e autorização do worker. Fixtures HTTP cobrem framing, partial/chunked, cap, redirect e autenticação de evidência de sucesso/falha.

A CI Linux anterior em 53f76c1 falhou porque três testes puros chamavam identidade Windows real. O fix fornece identidade simulada somente nesses casos; não adiciona skips ou fallback. Outra fixture publicava marker JSON antes de terminar a escrita; regressão determinística RED/GREEN e publicação atômica fecharam a corrida. Receipts/jobs não objetos agora falham explicitamente com exit 2. Todas essas correções tiveram revisão independente.

CI do codehead 1a5a4e4: [push 37253537244](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37253537244) e [PR 37253539541](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37253539541) SUCCESS. [PR 52](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/52) permanece draft até revisão do conjunto final/documentos/escopo; isso não afirma merge ou CI pós-merge. Inventário protegido e estado final são conferidos no fechamento da mesma Issue.

## Comandos efetivamente usados

Inicialização/metadata/values/recover escreveram destinos novos: são histórico de execução, não instrução para repetir nos destinos aceitos. O job, bootstrap, A e receipts são obrigatórios; valores sem A e sessões existentes são recusados. Não há parâmetros livres de URL, raiz, período, worker ou política na CLI desta prova.

Comando de inspeção offline executado, sem escrever ou coletar:

```powershell
& .\.venv\Scripts\python.exe -B scripts/acquire-financial.py verify --job data/runs/financial-historical-acquisition-202403-20261004/preparation/job.json --job-sha256 b16a582e865f6de1f097820f67fa9b063b5be9fe5ddf0be8dc617415f864c4de --bootstrap-sha256 026d372570fff21a53d3b59fbf9acf1a164adb377e810811965d80e3251a5a9c --receipt data/runs/financial-historical-acquisition-202403-20261004/metadata-real-01/receipt.json --receipt-sha256 3357ff2d3719a2a4c51f61d299947adf856e949124afb83f3c7c5f06b6994536
```

Prepare/inicialização explícita/metadata/values/recover/verify foram exercitados pela CLI contra fixtures; inicialização, metadata, values, recover e verify também foram executados no job real. O preparo real usou a API offline autenticada. Não declarar que um comando de coleta livre por intervalo já existe.

## Próximo lote

Após integrar este mecanismo e o registry/admissão históricos, o contrato seguinte cobre a janela 202312–202606, 11 referências. Cada arquivo mantém seleção, período e proveniência nativos; isso permite agendar um intervalo inteiro e downloads independentes em paralelo. O scheduler concorrente ainda tem recorte próprio: parent único para journal, destinos compatíveis, recursos medidos, reuso autenticado e aceites por referência. Não é necessário abrir uma implementação manual por trimestre nem duplicar este pipeline 66 vezes.

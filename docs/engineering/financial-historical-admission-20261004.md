# Registry e admissão financeira histórica — execução de 2026-10-04

Issue real: [51 — Generalizar admissão financeira com registry histórico finito](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/51). [Plano](../superpowers/plans/2026-10-04-financial-historical-admission.md), [desenho histórico](financial-historical-batch-design-20261004.md) e [arquitetura](../architecture.md) permanecem as referências únicas desta frente.

## Estado verificável

Resultado **local validado na branch `codex/financial-historical-admission`**, base `0f64dc4dc358a3a046aa5e4e3dad5f3ad74da263`. Tasks 1–3, correções de completude, perfil/registry e ajuste v2 receberam revisão independente antes dos respectivos gates. Admissão, conversão, consulta integral e replay de 202312 passaram. Suíte pública final, revisão whole-branch, PR/CI/integração são etapas separadas; estado remoto tem autoridade na Issue real. Este resultado não encerra a base 2010–2026.

O registry contém 66 ofertas finitas, não 66 snapshots aceitos. Os perfis anteriores 202412/202503 e seus contratos permanecem intactos; 202312 usa contrato histórico próprio e 63 outras ofertas continuam sem perfil ativo. A coleta 202403 da [Issue 50](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/50) não equivale a uma admissão ou a um Parquet 202403.

## Implementação e ownership

`bank_quality/financial_report_profiles.py` concentra lookup instalado e autoria offline explícita de candidato/perfil. `bank_quality/financial-reports-registry.json` congela oferta, árvores, anúncios e ativação interna por hash. O novo destino `bank_quality/financial-reports-profiles/` contém somente perfis históricos instalados; nesta entrega, apenas `202312.json`. São metadata do pacote existente, sem nova raiz, camada, dependência ou pipeline por trimestre.

Reader e adapter continuam em `financial_reports.py` e `financial_reports_parquet.py`, com dispatch mínimo nos módulos `financial.py`/`financial_parquet.py`. A grade autoritativa tem 32 colunas VARCHAR; cadastro conserva sua largura nativa. Origem é identificada por membro de fonte e pointer, inclusive quando IDs se repetem em shards distintos. Nenhuma unidade, janela, soma, escala ou comparabilidade é inferida da oferta histórica.

O root integra os paths compartilhados. A allowlist da Issue tem 15 paths; 533 arquivos anteriores foram conferidos byte a byte intactos. Os sete paths existentes autorizados a mudar têm baseline separado. Capturas, snapshots aceitos, perfis legados, individual, aquisição, CI/governança, credenciais/proteções e Project 3 estão fora deste diff. O novo conjunto admitido e os checkpoints foram igualmente fixados por hashes antes da revisão da representação numérica.

## Primeiro perfil real: quatro relatórios 202312

Seleção exata: `202312 / 1005 / [92, 96, 101, 98]`, Resumo, Ativo, Passivo e DRE. Wrapper restrito às cinco fontes legadas já arquivadas da Issue 36, sem GET, reclassificação dos contextos originais ou alteração de seus corpos. O truncamento não declarado dos D/N legados permanece desconhecido, sob os pins exatos revistos; a exceção não se estende a outros datasets.

Novos C/D/N exigem captura bounded completa, término coerente, counters/cap e sidecar físico autenticado. Header chunked isolado e hashes de corpo não comprovam término. Catálogos/portal congelados conservam suas provas próprias.

| Artefato | SHA-256 dos bytes físicos |
| --- | --- |
| Checkpoint A | `1cf7cabb6e383dc894af16bb6d7b7666008802f12c31ebaf521e93ad97cc6f3a` |
| Candidato | `3b9c5b674fd7f2725c21e2f3f2b77bda7297bb69d8dccd0bada35be3a5b85bad` |
| Checkpoint B | `7305bf01dc2af403d71a86cca49adfa9203e6118b5faf34881c5d934182f68e7` |
| Perfil instalado LF | `3dd39242b3e555809a369d57789b8fee15d0410561ea03fcccf7bba80a852435` |
| Registry após ativação 202312 | `ccb7f2d8531f79b1ddbbddcc8d8f3fc11ed6c56fb9e1bbc305ba90c6547ad815` |

Checkpoints/candidato originais ficam em `data/runs/financial-historical-admission-202312-20261004/`, ignorado no Git. Perfil público contém projeções sanitizadas e hashes, sem corpos, valores financeiros, cadastro, headers privados ou paths absolutos de coordenação. Revisão independente confrontou os cinco membros físicos, C/D/O/portal, 264 reports/66 ofertas e todos os pointers/definições do perfil; não repetiu integralmente o parsing de N.

Resultado de metadata: cadastro 1.385 × 32, 121 nós, 112 folhas, nove grupos; 74 numéricas, duas quantidades e 36 atributos. Cinco fontes requeridas, nenhuma ausente. Unidade e janela permanecem `unknown` onde não há evidência específica do binding.

## Admissão real e recusa de precisão

API `financial_reports.admit` executada com checkpoint B fisicamente fixado pelo perfil instalado, em destino novo `data/derived/financial-historical-202312-20261004/`. Manifest aceito sob `ifdata-financial-reports-historical-snapshot-v1`, SHA-256 `ff8ac90885cf4fe65db9bc611eced3fde6084c23fed124b8616e285d01f3863a`.

- Grade: **155.120 células**, 154.898 observações armazenadas e 222 posições sem armazenamento.
- Cadastro: 1.385 registros, 32 campos nativos.
- Metadata: 121 nós, 112 folhas e nove grupos; nenhum grupo produz célula financeira.
- HTTP: zero. Isso não valida equivalência econômica, amostra acadêmica ou todo o histórico.

A API de conversão autenticou a admissão, mas `_decimal_type` recusou um dos 76 bindings numéricos. Diagnóstico incremental do CSV autenticado isolou DRE/report 98, column 18583, pointer `/95/files/33/trel/c/10/sc/7`: 1.382 valores em 1.385 linhas, máximo de 11 dígitos inteiros e escala 29, exigindo largura comum 40. Os outros 75 bindings cabem em 38. Não arredondar nem converter para DOUBLE para superar o gate.

DuckDB instalado **1.5.6**, conferido contra `requirements-duckdb.txt`; a [documentação oficial de tipos numéricos](https://duckdb.org/docs/stable/sql/data_types/numeric.html) limita DECIMAL a largura 38. A guarda funcionou como previsto, antes de criar `data/curated/financial-historical-202312-20261004/`. Naquela primeira tentativa não houve manifest Parquet ou output parcial. A admissão e a evidência da recusa permanecem intactas; a reexecução v2 aprovada e os resultados posteriores estão abaixo.

O passo seguinte foi comparar representações exatas, registrar a escolha v2 e revisar sua implementação antes da reexecução, conforme o resultado abaixo. Não reduzir o aceite dos quatro relatórios ou alegar um DECIMAL SQL 40 nativo. Contratos anteriores e seus valores permanecem preservados.

## Recursos e verificações realizadas

Uma execução pesada por vez, neste host: orçamento monitorado `min(1,25 GiB, RAM disponível − 256 MiB)`, piso de 768 MiB, margem de commit 512 MiB, disco livre mínimo 1 GiB e deadline 600 s por estágio. São parâmetros desta execução, não teto universal ou quota do sistema operacional. Monitor amostra a árvore própria; picos amostrados não equivalem a contadores exatos de todas as alocações.

| Estágio real | Tempo | Pico amostrado de working set | Resultado |
| --- | --- | --- | --- |
| Preparação/freeze | 11,58 s | 441.491.456 bytes | perfil gerado, posteriormente revisto |
| Admissão | 8,78 s | 390.840.320 bytes | manifest aceito |
| Conversão | 6,58 s | 651.722.752 bytes | recusa de precisão, antes do destino |

TDD e revisões privadas: Task 1/2/3 aprovadas; fix de completude com 137 testes financeiros PASS, zero falhas/erros/skips, mais oito testes focados executados independentemente. Esses resultados não são a suíte pública integrada. Após ativar 202312, um teste que pressupunha somente dois perfis ativos teve RED esperado; uma condição foi ajustada para exigir carregamento válido de todo membro ativo e recusa dos inativos. GREEN de um teste e revisão independente aprovados, sem fallback por existência de arquivo.

Após os gates reais: conferir protected/privacy/diff/links, rodar a suíte pública final e checks pertinentes, revisão independente do SHA final e confirmar PR/CI/merge/pós-merge. Project permanece com Zec.

## Escala posterior

A primeira janela planejada é **202312–202606, 11 referências**. Reaproveitar snapshots/fontes aceitos e medir downloads paralelos; manter autoria de perfil, validação, admissão e evidência por referência. Arquivos por trimestre não exigem tarefas manuais ou mecanismos separados por trimestre. A autoridade executável da aquisição 50 ainda está fechada em 202403; a extensão por lote tem contrato próprio posterior. A [Issue 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) registra a fronteira real e os blockers.

## Ajuste de representação adotado após diagnóstico

Revisão técnica independente confirmou largura40 mesmo retirando zeros finais sem alterar valores. A escolha técnica registrada na Issue/plano é a projeção fechada `ifdata-financial-reports-historical-parquet-v2`, somente para históricos com binding>38: DECIMAL nativo nos que cabem, `numeric_exact_text` VARCHAR explícito nos largos, com encoding/precision/scale/storage no manifest e accessor validado `iter_numeric_decimals` para PythonDecimal exato. v1 e contratos legados não recebem campos opcionais ou exceção silenciosa. A grade/admissão/profilepins permanecem intactos. Isso preserva dados sem prometer aritmética SQL nativa de precisão40; consultas/cálculos acadêmicos não são introduzidos.

Implementação TDD concluída no adapter, dispatch e teste histórico autorizados; revisão independente APP nos três hashes exatos, sem P1/P2. Foram conferidos 727 arquivos protegidos sem divergência. Histórico: 16 testes PASS/20,576s; regressões financeiras: 160 PASS/72,098s, zero skips; reviewer reexecutou três riscos PASS/2,524s. A observação P3 sobre a grade validada residente no iterador é não bloqueante; abertura/consumo foram medidos e não se promete memória constante. Root mantém docs, reexecução medida em destinos novos, suíte final, revisão whole-branch e Git. Mapa2 atualizado no handoff; nenhuma outra Issue de implementação pronta foi confirmada neste momento. Evidência da primeira recusa e source admitido permanecem preservados.

## Gate real v2 e replay — 2026-10-05

Destino novo `data/curated/financial-historical-202312-20261004/`, contrato `ifdata-financial-reports-historical-parquet-v2`, manifest físico `facbc0b6a1d06c10879caa6744e9bb573b29b827dd81d45753477b12ca45d8e6`. Grade de 155.120 células/32 campos textuais, 154.898 armazenadas/222 ausências, cadastro 1.385 × 32; 76 bindings numéricos, sendo 75 DECIMAL e um `numeric_exact_text` VARCHAR. Nenhum cast global, float, arredondamento ou modificação do admitido.

APIs efetivamente executadas: `financial_reports.admit` sobre checkpoint B autenticado; `financial_parquet.convert_financial` sobre o admitido com `source_manifest_sha256` externo; `financial_parquet.snapshot_connection` sobre o curated com `manifest_sha256` externo; `financial_reports_parquet.iter_numeric_decimals` sobre esse mesmo destino/hash. Uma abertura SQL validou grade, todas as origens/CSVs reconstruídos, schemas/contagens/estados e todas as parts. Após fechar essa conexão, uma invocação do accessor confrontou as **105.260 linhas** numéricas/quantidade contra o CSV admitido autenticado, em identidade, ordem e Decimal/None. O teste independente observou uma única abertura por invocação; a validação materializa o snapshot, portanto o consumo em chunks não equivale a memória constante.

Replay em destinos novos com sufixo `-replay`: todos os cinco payloads da admissão e todos os 80 payloads Parquet/companions são byte a byte iguais. Exceções somente os manifests de execução e sua cópia `metadata/source-manifest.json`: `created_utc` diferente e os hashes derivados desse timestamp. Conteúdo e inventários restantes são idênticos. A primeira comparação do harness não descontava o hash da cópia desse manifest já descontado no payload; diagnóstico confirmou que apenas esse descritor e os dois campos de execução diferiam. Harness corrigido para autenticar explicitamente a cópia e comparar todo o restante, sem alteração de adapter, fonte ou saída; comparação PASS.

533 arquivos anteriores e 13 novos checkpoints/perfil/admitidos permaneceram intactos. Nenhum GET; nenhuma reescrita de destino aceito. Nativos e históricos que cabem em DECIMAL38 conservam v1; comparação independente de fixtures v1 registrou todos os payloads byte iguais, manifests distintos apenas por criação.

| Estágio v2 | Tempo | Pico amostrado working set | Resultado |
| --- | --- | --- | --- |
| Conversão | 13.687 s | 715,382,784 bytes | PASS |
| Consulta e accessor integrais | 24.766 s | 793,227,264 bytes | PASS |
| Replay de admissão | 8.641 s | 391,634,944 bytes | PASS |
| Replay de conversão | 13.953 s | 729,059,328 bytes | PASS |
| Replay de consulta/accessor | 24.703 s | 794,779,648 bytes | PASS |

Monitor usou orçamento local de 1,25 GiB e apenas uma etapa pesada por vez. Isso prova capacidade neste host/recorte; não autoriza paralelismo pesado sem medição conjunta. Suíte pública final e integração remota terão seu próprio registro abaixo.

## Checks públicos finais

`.venv/Scripts/python.exe -B -m unittest discover -s tests -v`: **383 testes PASS em 160,245 s**, zero falhas/erros/skips neste Windows. `node tests/test-budget.cjs`: guards de bytes/deadline/reserva PASS; `node --test tests/test-portal-ready.cjs`: dois testes PASS, zero skips. Não houve coleta de dados nesses checks. Código permaneceu nos hashes revistos; a suíte não foi repetida apenas para atualizar documentação.

Gate real, replay e checks de software passaram; revisão independente do conjunto final, PR/CI e integração seguem etapas próprias na Issue 51. Não se declara aqui cobertura das 66 referências, comparabilidade econômica ou aceite acadêmico.

# Lote financeiro recente — execução e checkpoint de migração

Issue: [#57](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/57). [Plano](../superpowers/plans/2026-10-05-financial-batch-sanitization.md) e [mapa do Goal #2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2). Base pública: `7cb4f7e81713995357cd5ad2d837004531f3d3f2`; branch de trabalho: `codex/financial-batch-sanitization`.

## Resultado local em 2026-10-05

Os sete novos snapshots concluíram admissão, Parquet, consulta integral pelo accessor Decimal e replay, sem coleta nesta Issue. Com os quatro anteriores, são **11/66 financeiros validados localmente**. CI integral, revisão final do conjunto e integração permanecem pendentes neste checkpoint; a cobertura integrada em main ainda é quatro. Não encerrar a Issue ou o Goal pela existência destes arquivos.

| Referência | Cadastro: registros × campos | Células da grade | Observações armazenadas | Linhas numéricas conferidas | Bindings: DECIMAL / texto numérico exato |
|---|---:|---:|---:|---:|---:|
| 202406 | 1400 × 32 | 156800 | 156504 | 106400 | 75 / 1 |
| 202409 | 1415 × 32 | 158480 | 158258 | 107540 | 75 / 1 |
| 202506 | 1426 × 38 | 203918 | 203000 | 152582 | 107 / 0 |
| 202509 | 1436 × 38 | 205348 | 204088 | 153652 | 106 / 1 |
| 202512 | 1466 × 38 | 209638 | 205858 | 156862 | 107 / 0 |
| 202603 | 1461 × 38 | 208923 | 204828 | 156327 | 107 / 0 |
| 202606 | 1458 × 38 | 208494 | 203034 | 156006 | 107 / 0 |

Resumo, Ativo, Passivo e DRE conservam todas as variáveis nativas, árvores, atributos, fontes, ausências e janelas. Diferenças entre grade e armazenamento permanecem explícitas; não preencher com zero, arredondar ou harmonizar regimes. Texto numérico exato acima da largura38 usa o contrato histórico v2 já aprovado e accessor Decimal; não há UNION numérica global. Consulta técnica não certifica comparabilidade econômica ou anualização da DRE.

## Execução, integridade e recursos

Tentativa1 preservada em `data/runs/financial-batch-sanitization-202312-202606-20261005/`: plano SHA-256 `196b0f423c65888ee01c67c199de7bf505a08fcc336e4e7b586b2f80f34272aa`, admissão202406 concluída e conversão interrompida por margem física livre. Nenhum novo aceite daquela tentativa. Destinos parciais e journal não foram sobrescritos.

Tentativa2: `data/runs/financial-batch-sanitization-202312-202606-20261005-attempt2/plan.json`, SHA-256 `86d6432c3238699947b4c5d1dc63d367848ec225eb80fb30cf94234a736569f5`. Preparação83,324s; os sete perfis são byte a byte idênticos aos previamente revisados/instalados. Execução real960,089s, exit0, **49/49 etapas completas**; todos os receipts/payloads reautenticados posteriormente. Processos nasceram contidos e suas árvores terminaram extintas. Working set máximo observado854.028.288bytes; memória física livre mínima759.971.840bytes. São medidas deste lote e máquina, sem previsão para o histórico.

Política preservada: workers1, deadline1800s por etapa, margem física512MiB, commit1GiB, disco4GiB, amostragem0,2s. Recursos não foram relaxados. Compartilhamento local limitado da última string igual por campo e expectativas incrementais na consulta reduziram cópias, mantendo tokens/tipos/ordem/valores. Diagnóstico sintético motivou a mudança; o aceite acima vem do lote real.

Protegidos conferidos: **203 arquivos versionados** fora dos paths autorizados e **1570 arquivos de dados anteriores**, total2.790.740.496bytes, com hashes originais preservados. Registry tem somente sete ativações autorizadas; perfis e pins do plano conferidos. Fontes54, quatro aceites anteriores e defaults nativos continuam próprios. O controle de arquitetura é documental e por revisão.

Comando efetivamente executado nesta máquina, com Python/runtime/código pinados no plano:

```powershell
& .\.venv\Scripts\python.exe -B scripts/run-financial-pipeline.py run --plan data/runs/financial-batch-sanitization-202312-202606-20261005-attempt2/plan.json --plan-sha256 86d6432c3238699947b4c5d1dc63d367848ec225eb80fb30cf94234a736569f5 --resources data/runs/financial-batch-sanitization-inputs-20261005/resources.json --resources-sha256 e710613623c0837e06019f5af1b40f139e1d81a6ca2474910690183bb03daf24
```

Esse comando registra a execução; **não repetir um run concluído nem usar seus pins absolutos para despachar no computador novo**. Status inspeciona plano/journal/receipts pequenos, sem reabrir todo o corpus. A leitura dos dados exige os arquivos locais e seus hashes esperados.

## Software, revisão e próximos passos

Tarefas1/2, ajuste de relógio, perfis e ajuste de memória receberam revisões independentes em snapshots pinados. **105 testes afetados PASS** depois do ajuste de memória. A suíte anterior tinha487 testes e uma falha Win32, corrigida com dois testes focais aprovados; isso não equivale a uma nova suíte integral PASS. CI integral do conjunto atual permanece obrigatória antes de merge.

João solicitou encerrar o trabalho neste computador e retomar o Goal em outro mais potente. Publicar este checkpoint em branch/PR draft permite clonar o código; **Git não contém `data/raw`, `data/runs`, `data/derived`, `data/curated` nem a evidência privada `.superpowers`**. O pacote de migração local separado conserva dados, receipts, revisões e o candidato59. Copiar esse pacote junto ao clone e conferir seu SHA-256 antes de extrair; conservar o original até verificação na nova máquina. `.venv` deve ser recriada conforme o README, sem transportar o ambiente como instalação portátil.

O pacote também conserva os bytes físicos do código deste checkpoint, pois conversão de terminações LF/CRLF no clone altera hashes. Após clonar a branch exata, restaurar os arquivos do pacote e verificar o inventário; não reformatar o código para tentar satisfazer um pin. O runtime executado anteriormente é preservado como evidência privada, não como instalação executável portátil.

Retomada: conferir branch/HEAD/Issues, integridade do pacote e paths; configurar runtime e recursos da máquina nova, preservando provas e planos antigos. Completar revisão final/CI/integração57; depois integrar/revisar o candidato59, executar seus checks Windows e comprovar leitura54/202403/11 snapshots antes de GET. O candidato59 teve revisão independente r2 APP, mas ainda é software privado; coleta dos55, CI e integração59 não foram executadas. Não continuar plano antigo alterando pins, sobrescrever outputs, renovar budgets ou confundir revisão privada com publicação.

A rota restante é #57 → #59/#60 → #61, em paralelo com a decisão62 → complementos63, e auditoria64. O mapa2 distingue cobertura local/integrada, checklists, dependências e ownership; Project3 permanece com Zec.

## Preparação para integrar em main

João solicitou integrar o PR65 em main antes da migração. A CI Linux do checkpoint registrou489 testes/um erro no teste do launcher Windows: a recusa de plataforma precedia a validação de prazo esperada. A fixture agora isola somente `require_supported` nas duas verificações de inputs, sem mudar produção, prazo120s ou contenção. RED reproduzido com recusa de plataforma; GREEN do mesmo caso e os dois testes do módulo passaram em Windows, incluindo nascimento contido/extinção. README e arquitetura descrevem o executor no destino canônico. Revisão independente do SHA final, CI desse SHA e CI pós-merge precisam ser confirmadas na Issue57/PR65; o registro de draft acima conserva o checkpoint anterior. O pacote de migração final deve corresponder a main, para não restaurar a fixture/documentação antigas sobre o clone atualizado.

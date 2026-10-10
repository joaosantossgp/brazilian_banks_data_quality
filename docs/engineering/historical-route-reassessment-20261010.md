# Reavaliação da rota histórica — 2026-10-10

Pesquisa e replanejamento na [Issue59](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/59#issuecomment-6097602099), solicitados por João para reduzir demora e complexidade. As duas recomendações foram aprovadas em 2026-10-10; a aprovação da rota não significa que seus gates técnicos já passaram. Base ca63ee9674f58f9a80221af721fe6ebfc00025d3; checkpoint aeaf50877c30cb5844c2806a50d3f42668e098fa. Root integra a documentação; pesquisa independente somente leitura conferiu as alternativas. Nenhum GET, teste demorado, alteração de autoridade ou dado nesta pesquisa.

## Evidência e diagnóstico

A [PR73](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/73) está aberta em draft; as duas CIs Offline tests do checkpoint terminaram SUCCESS. Isso não significa entrega dos 55 períodos. O diff acrescenta aproximadamente 974 linhas no batch e 1.177 em seu teste; a fixture histórica inerte de 2.126 linhas é contabilizada separadamente. Tamanho não prova excesso por si só: o problema é o caminho restante até o primeiro dado útil.

O módulo batch tem 3.032 linhas. A continuação começa em `_historical_continuation_candidate` e já inclui preparação, ativação, replay e writers, mas ainda exige transporte Worker4, fechamento das fases, scheduler/export e CLI para executar. A maior parte dessa ampliação preserva a mesma autoridade executável depois da mudança de software. Não é requisito intrínseco de ler dados financeiros de todos os períodos.

Fontes primárias: [batch](../../bank_quality/financial_acquisition_batch.py), funções `_code_identity_v2`, `_reconcile`, `_historical_continuation_candidate`, `_open_continuation`; [plano corrente](../superpowers/plans/2026-10-08-historical-monitor-continuation.md). Os pins correntes fechados e o halt impedem simplesmente executar o bundle antigo com código corrigido. Não editar esses pins nem apagar halt para contornar o problema.

## Alternativas

| Alternativa | Consequência | Avaliação provisória |
|---|---|---|
| Terminar overlay/Worker4 | Mantém a continuidade pela cadeia implementada, mas exige vários contratos executáveis adicionais | Maior trabalho restante; retirar da prioridade até comparar com sucessão restrita |
| Preservar F1-01 e substituí-la por execução explicitamente vinculada | Reutiliza executor comum após provar aposentadoria exclusiva e orçamento cumulativo | Candidata preferida; menor esforço provável, ainda sem desenho/teste que confirme essa vantagem |
| Criar coletor novo independente | Pode capturar bruto, mas recria controles e interfaces | Não recomendado como primeira simplificação |

Substituição não significa saldo novo silencioso: preservar predecessor, impedir execução dupla e descontar gasto/reservas inconclusivas. O caso atual registra interrupção antes da primeira reserva; a classificação precisa continuar apoiada na evidência física, sem concluir extinção de processo apenas pela ausência de arquivos.

## Controles essenciais e simplificações propostas

Manter bruto imutável, URL/parâmetros/UTC/status/headers, SHA, diagnóstico das falhas, limites de bytes e tempo, orçamento cumulativo e destino novo. Reutilizar [fetch_bounded](../../bank_quality/archive.py) e a ordem reserva antes do lançamento em [acquisition._attempt](../../bank_quality/financial_acquisition.py). Contenção/deadline/extinção e exclusividade precisam de implementação comprovada; uma ficha mais simples pode substituir registros redundantes, não a proteção que eles oferecem.

Separar entregas: capturado, validado e consultável. Bruto preservado pode ser examinado antes da admissão, mas resposta parcial/falha não conta como fonte completa nem período aceito. Revisar e testar cada lote antes de ampliar. Não exigir sanitização de todos os 55 antes do primeiro resultado consultável.

Generalização proposta: transporte e leitura comuns, com descritores nativos por família/período. Reutilizar resolução, validação numérica, compilador de metadata e adapters existentes: [profiles](../../bank_quality/financial_report_profiles.py), [reader](../../bank_quality/financial_reports.py), [Parquet](../../bank_quality/financial_reports_parquet.py). Nenhum pipeline manual por trimestre, inferência de equivalência contábil ou conversão para DOUBLE. O contrato de entrada da60 ainda precisa acomodar o handoff59; leitura genérica não elimina essa adaptação.

Registros: uma síntese vigente por Issue/lote, inventário dos corpos e respectivas provas necessárias; evitar repetir narrativa e históricos inteiros em cada checkpoint. Uma revisão pertinente por resultado antes de ampliar e conferência final de composição. Não somar testes isolados para declarar PASS global.

## Árvore de decisões e próxima rodada

1. Prioridade: primeiro lote capturado e consultável com limitações explícitas, ou somente entrega após validação final de todo o corpus? Recomendação: primeiro lote útil, depois expansão e refinamento por lote; manter aceite final dos66.
2. Continuidade: preservar a identidade executável da execução interrompida, ou preservar histórico, contabilidade cumulativa e exclusividade admitindo sucessão explícita? Recomendação: segunda alternativa, sujeita ao desenho restrito e à prova.
3. Após essas respostas: fechar menor mudança técnica, arquivos e checks; decidir destino dos componentes da PR73 sem promover código incompleto nem descartar correções úteis do monitor. Não exigir nova Issue para cada etapa.

João respondeu **“Vou com recomendação”** em 2026-10-10, aprovando as duas primeiras escolhas: primeiro lote útil com limitações explícitas e substituição preservando histórico, contabilidade e exclusividade. Não repetir confirmação de execução técnica no escopo aprovado. O glossário existente já distingue resposta bruta, disponibilidade anunciada e recorte analítico; nenhum termo novo resolvido nesta rodada exige alteração.

## Rota escolhida e plano de execução

Usar uma única variante operacional instalada de F1-01, com scopes novos para batch e quatro membros e destino novo determinístico. Não alterar a tabela/policy financeira original nem seu SHA. Derivar catálogos, descritores, relatórios, áreas, targets e limites do compilador existente; somente identidades operacionais mudam. Os contratos de execução job-v2/batch-v2/worker-v3 e os journals, receipts, scheduler e export comuns serão reutilizados. Reusar a classificação física já implementada do predecessor sem ativar overlays. Não criar sucessão arbitrária, novo Worker4 ou envelopes novos de eventos.

Só reconhecer o predecessor conhecido, sem reservas, identities, fontes ou despesas nos quatro membros. Comprovar a ordem durável anterior ao lançamento. Registrar uma ligação imutável única predecessor→sucessor sob os claims originais, antes da inicialização nova. Uma falha parcial bloqueia e conserva evidência; não implementar agora recuperação genérica, segundo destino ou nova franquia. A abertura/execução deve conferir a ligação e conservar exclusividade com o predecessor. O worker comum autentica o bundle/prefixo vigente; não recebe exceção de leitura de claims antigos. Identificar exatamente a contabilidade original zero comprovada e seu orçamento remanescente, sem extrapolar para execuções com gasto.

Três checkpoints de resultado, com implementação Root e revisão independente antes de ampliar:

| Checkpoint | Resultado e arquivos responsáveis | Checks e condição de saída |
|---|---|---|
| A — Executor comum habilitado para a substituição restrita | Derivação única, ligação durável, abertura/exclusividade e CLI nos módulos existentes `financial_acquisition_batch.py`, `financial_acquisition.py`, `scripts/acquire-financial.py`; testes adjacentes | Rejeitar predecessor alterado/com reserva, scope/destino/budget caller, segunda ligação, colisão de claims e inicialização parcial; comprovar caminho worker-v3→receipt→export em fixture, sem GET externo. Conferir composição com correções úteis do monitor, revisão e SHA/checks pertinentes antes da execução real |
| B — Primeiro lote útil | Destinos novos ignorados de execução; ledger59 existente. Metadata dos quatro membros, values201003 representante, depois restante da janela pela mesma execução | Preflight Windows/pins/runtime/recursos atual, captura limitada/proveniência/falhas, revisão do representante antes de remaining, handoff de quatro períodos com hashes e ligação ao predecessor. Mostrar capturado e validado separadamente; preservar11 e predecessor. Não repetir gates antigos sem impacto ou falha que justifique |
| C — Consulta e expansão | Interface/composer e reader/adapter existentes da60, catálogo61; allowlist própria da60 antes de código | Adaptar handoff59 uma vez, validar admissão/Decimal/ausências/Parquet/query/replay do primeiro lote, revisão antes de ampliar famílias. Próxima janela59 pode coexistir com sanitização60 se destinos e recursos forem compatíveis. Repetir até55 novos/66 aceitos, mantendo os aceites finais existentes |

Antes do código de A, fechar em um único registro na59 os nomes físicos da variante e da ligação, schema mínimo, pontos de validação e allowlist exata. Esse detalhamento é técnico, não nova decisão de produto. Não criar Issue/PR por checkpoint. Uma PR pode reunir o escopo necessário. A nota e os documentos anteriores bastam para este replanejamento; não duplicar histórico em outra spec/plano.

Destino da PR73: permanece draft como evidência do trabalho anterior. Sua revisão/CI não aprovam automaticamente a substituição. Preservar commits e testes anteriores; selecionar as correções úteis de monitor/medição e retirar o overlay da composição executável da rota escolhida, após conferência do delta. Não fazer merge da continuação incompleta para contabilizar uma entrega.

O primeiro resultado operacional é metadata e o representante201003, não uma base inteira saudável. O primeiro lote consultável depende da adaptação60, que deve começar com a primeira janela e não esperar55. Não oferecer prazo numérico sem medir o primeiro lote.

## Fronteira de trabalho

Issue59 concentra esta reavaliação; expansão Worker4 interrompida para evitar ampliar custo antes da escolha. Issue60 depende do primeiro handoff e contrato próprio; seu desenho pode ser preparado antes dos55. Issue61 tem implementação inicial, expansão final depende dos dados aceitos da60. Issue16 está ready para pesquisa em documentação própria, reutilizando3/14; adoção acadêmica continua humana. Issues62/63/64 conservam decisão de conteúdo e dependências finais. Project3 permanece com Zec.

## Método e limitações

Instruções locais de grill-with-docs aplicadas por leitura de grilling e domain-modeling; pesquisa de fatos delegada ao revisor existente, somente leitura. Não há ferramenta Skill nesta interface: não alegar slash command executado. Revisão independente sustenta o diagnóstico e a plausibilidade da alternativa, não comprova seu custo, prazo ou funcionamento. A rodada de decisões foi concluída; próximo passo é o checkpointA da rota escolhida, com detalhamento técnico e validação proporcionais.

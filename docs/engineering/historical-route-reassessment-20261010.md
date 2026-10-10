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

### Conferência das onze Issues e estimativas — 2026-10-10

Corpos reais das onze Issues e entregas pertinentes foram conferidos, com revisão independente. O mapa vigente continua na2; esta nota explica a mudança de rota, sem criar outro tracker.

| Issue | Próximo resultado e dependência real |
|---|---|
| 2 | Síntese vigente das onze frentes; comentários guardam checkpoints, sem repetir históricos inteiros |
| 3 | Decisão humana de unidade/amostra/método; alternativas14/16 podem preceder a decisão, sem bloquear base nativa |
| 14 | Pesquisa parcial integrada em PR33; proposta integral ainda depende de lista/complemento original ausente ou reformulação explícita, fontes/componentes e decisões3. Pesquisa factual delimitada pode avançar |
| 16 | Pesquisa ready de amostra/comparabilidade em seus dois destinos documentais; adoção/cálculo dependem3 |
| 17 | Workflow e revisões parciais entregues em PR69/70. Owner/bindings reais e runner remoto são escopo futuro indefinido, sem dependência financeira; pausa antiga e checkbox de PR pequena são históricos superados |
| 59 | Substituição restrita, representante/janela, handoff; depois demais janelas. Software ainda incompleto, nenhuma fonte nova nesta revisão |
| 60 | Preparar interface agora; primeiro lote real depende de handoff59, contrato e allowlist próprios. Não esperar55 |
| 61 | Inicial integrado em PR71/b2d72c8, ancestral de main; manter11/66 e expandir incrementalmente após aceites60. Não refazer catálogo/CLI |
| 62 | Escolha humana do conteúdo complementar; alternativas podem ser pesquisadas com contrato próprio, sem bloquear financeiro |
| 63 | Implementar quantidade/conjuntos definidos em62; não estimar coletor amplo com conteúdo ainda desconhecido |
| 64 | Conferência incremental dos handoffs e composição final59/60/61/63; método acadêmico e automação17 não bloqueiam base nativa |

Estimativas separadas, sem confundir esforço de software com relógio de execução:

- **Software59:** orçamento inicial de planejamento de4–8horas para ligação restrita, integração do executor/CLI, testes pertinentes e revisão. Confiança baixa, não medição nem prazo garantido. Reavaliar ao terminar A2; caso a solução exija outro transporte ou máquina de estados, interromper expansão e rever a escolha.
- **Software60 e primeiro lote consultável:** orçamento inicial de4–8horas para contrato/dispatch da interface e primeira família, com testes/revisão. Confiança baixa; dados reais e diferenças de família ainda podem alterar esse esforço. Não inclui a expansão inteira.
- **Coleta55:** falta medir o representante. Há até288targets anunciados na policy; cenários ilustrativos de10/30/60segundos por target, uma tentativa, dão48min/2h24/4h48. Não são benchmarks ou previsão do BCB. O orçamento máximo configurado de tentativas/esperas é19h36; primeira janela tem65min20. Não são limites garantidos do tempo total.
- **Validação/conversão55:** medir o primeiro lote completo e projetar por família/tamanho, separando leitura, admissão, Parquet, consulta e replay. Não usar tempo de download como estimativa dessas fases.
- **Goal inteiro:** sem ETA fechado enquanto conteúdo63 e decisões humanas próprias não estiverem definidos. Isso não impede estimar e entregar a frente financeira separadamente.

### Checkpoint parcial de código A1

Resultado: `_derive_historical_replacement` deriva somente F1-01-R1 a partir do draft original reautenticado. Scopes novos com sufixo `/replacement-1`, destino novo com `-replacement-1`, hashes/session roots recalculados; policy e dados financeiros idênticos. Nenhum alias executável instalado: os gates continuam recusando a variante atéA2.

Allowlist: batch, teste batch e esta nota; impacto arquitetural nenhum. RED:4casos/9falhas por helper ausente,0,275s, log privado `.scratch/replacement-identity-red-20261010.log`. GREEN:4PASS/0,633s, `.scratch/replacement-identity-green-20261010.log`. Regressões existentes, separadas:16janelas1PASS/1,744s; rejeição de jobs adulterados1PASS/0,252s. Não declarar PASS global pela soma.

Revisão independente APP, sem achados materiais, dos dois arquivos físicos sobre7de3bb6: batchSHA256 `23a510b46a606785d521ed2c580ac1563bd41436b616ede086296071bb06df93`; testeSHA256 `79db8ae80322190365151f9c18912c43e1dc7cbea9e6867394c12305f4dc1527`. Isso permite detalhar/revisar A2, sem inicializar autoridade ou GET. Próximo: ligação única e durável com predecessor, usando a exclusividade global histórica já existente; claims originais apenas na emissão/prova, sem exceção nova de leitura no child.

### Checkpoint parcial de código A2

Resultado implementado: `initialize_historical_replacement` autentica a prova física da interrupção sem tentativas, reserva uma ligação única com F1-01-R1 e inicializa os mesmos contratos batch-v2/job-v2. Verificação, autoridades de membros, reserva e contexto worker-v3 usam o executor existente. CLI `historical-replacement-initialize` recebe somente prova/hash e pins/hash; scope, destino, seleção e orçamento não são livres. A exclusividade global permanece durante a emissão/inicialização; os cinco claims originais são liberados antes da inicialização comum. Os arquivos aceitos e o predecessor real não foram alterados; nenhum GET ou autoridade real foi ativado.

Allowlist: batch, CLI, testes batch e esta nota. Sem pasta, camada ou dependência nova. A montagem privada `_assemble_bundle` calcula identidades sem conceder execução; a validação R1 exige ligação autenticada. O desenho inicial tinha um ciclo entre construção e validação, encontrado e corrigido na revisão antes do código.

Revisão parcial do código encontrou dois P2 reproduzidos: endpoint comum contornava o bloqueio após inicialização parcial (RED1FAIL/15,784s); releitura não pinada podia persistir ligação após alteração do predecessor (RED1FAIL/3,163s). Correções: capability privada válida apenas durante a emissão sob claim global, invalidada em `finally`, sem opção pública/CLI; hash dos bytes usados na derivação e reconstrução integral imediatamente antes do CAS. Logs privados `replacement-partial-bypass-red-20261010.log` e `replacement-bundle-drift-red-20261010.log`.

RED inicial corrigido:7FAIL por API ausente/10,458s. Primeira execução implementada:7casos/6PASS e uma comparação incorreta do formato de retorno worker no teste,119,284s; corrigido o teste para o formato que remove `record_sha256` após conferência. Execução composta A1+A2:12PASS/128,155s, incluindo claims nativos Windows, mesma execução; log privado `replacement-composed-green-attempt2-20261010.log`. Regressão separada das16janelas existentes:1PASS/1,777s. CLI help e `git diff --check` conferidos. Revisão final do recorte registrada na Issue59; não confundir com aprovação global da PR73 ou execução operacional.

Próximo checkpoint: retirar a rota de overlay abandonada do conjunto executável, conservar apenas sua prova de leitura necessária à ligação e verificar composição/CLI/regressões antes de emitir pins atuais. A estimativa de software permanece orçamento de planejamento de baixa confiança; ainda falta composição e gate operacional, portanto não há ETA medido para coleta.

### Checkpoint parcial A3: retirada da rota abandonada

Removidos por símbolos13helpers/classes de overlay, registro privado de owners e import/decorador exclusivos:555linhas de produção. Saem ativação, replay/verify alternativo, writers e reserva própria; ficam a preparação/reconstrução somente de leitura e a substituição no executor comum. Foram retirados41testes das três classes exclusivas da implementação descartada; isso não é aumento de cobertura nem correção de suas falhas. O teste da superfície executável exige que sete entrypoints/classes abandonados estejam indisponíveis: RED1caso/7FAIL/0,117s → GREEN1PASS/0,109s. Busca em produção/scripts não encontrou chamadas residuais; o único uso dos nomes em testes é a conferência de indisponibilidade.

Allowlist: batch, teste batch, esta nota, parágrafo da arquitetura e aviso inicial do ledger da aquisição; ampliação documental registrada na Issue59 antes da escrita. Mesmo módulo/destino, sem camada/dependência nova. Histórico dos commits e todos os registros anteriores preservados. Revisões estrutural e documental independentes APP. Módulo batch completo:129PASS/504,322s, sem skips, em uma execução (`replacement-common-batch-composition-20261010.log`). Conferência real do snapshot externo:24/24 hashes preservados. Nenhum dado/autoridade real alterado.

A revisão da composição identificou falta do controle específico R1 até worker/receipt/representante/remaining/export. Acrescentado reaproveitando o helper de roundtrip existente, com inicialização R1 e comparação dos32arquivos protegidos; não modifica produção. Primeiro controle:1ERROR/71,980s por helper `write` ausente na fixture, corrigido por delegação ao helper existente. Controle corrigido em execução separada; não somar resultados para promover PASS global nem liberar coleta antes do terminal/revisão/SHA. Transporte, ancestry e recursos são simulados nesse controle offline; ele valida os kernels e a ligação, não contenção nativa ou rede real.

### Checkpoint causal A4: trabalho duplicado na policy

CI do SHA8426491 cancelada pelo limite vigente de10min; no run38056731932, o unittest concluiu690casos/OK/skipped20 em600,859s, mas Budget guards/Portal não executaram. O segundo run38056735098 também foi cancelado. Não é PASS de CI nem falha de asserção demonstrada. Não aumentar timeout ou alterar workflow/proteções.

O perfil local de uma validação R1 mediu1,784s/5,8milhões de chamadas, com191validações da policy e serialização repetida do mesmo objeto. Ajuste restrito a `_historical_policy`: calcular os bytes canônicos instalados uma vez por chamada, conferir SHA fresco e comparar objeto distinto aos mesmos bytes; closed_data e deepcopy permanecem. Sem cache entre chamadas, mudança da policy ou bypass. RED3casos/duas falhas/0,118s; GREEN3PASS/0,118s, incluindo mutação instalada entre chamadas rejeitada, cópia isolada e objeto distinto adulterado rejeitado. Perfil posterior no mesmo controle:1,454s, redução observada de18,5%; não é previsão de CI ou coleta.

Allowlist A4: batch, testes batch e esta nota, registrada na Issue59 antes da escrita. Revisão focal independente APP dos dois arquivos de código/teste. Execução completa do módulo com133casos em andamento e nova CI pendente da publicação; resultados serão registrados na Issue/PR no SHA entregue. Guards Node locais PASS e portal2/2PASS, em execuções próprias. Gates operacionais e cobertura11/66 permanecem próprios.

### Revisão do orçamento de CI após integração

PR73 integrado em main f64c6dcf5d2334e8f60e7ae928a21f269fa93a86. As duas tentativas pós-merge do run38058720006 foram canceladas pelo teto de10min, sem falha de asserção registrada; não são PASS. A mesma árvore concluiu693testes/OK/skipped20 em335,701s no run38057824823 e357,595s na segunda tentativa do run38057821075, com guards Node e portal2/2PASS. Intervalos dos cancelamentos mostraram lentidão distribuída próxima de2x, sem causa física demonstrada.

A decisão técnica de A4 de conservar10min fica superada: timeout do job offline passa a15min, margem proporcional aos tempos completos e à variação observada. Isso permite conclusão do mesmo trabalho sem retirar testes ou ampliar o orçamento de coleta. Repetir sem mudança conserva o mesmo teto; otimização ampla da suíte aumentaria escopo antes de demonstrar necessidade. Allowlist registrada na Issue59 antes da escrita: `.github/workflows/ci.yml` e esta nota; integrador único, destinos existentes, sem impacto estrutural. Comandos, permissões, dependências e versões das ações permanecem idênticos. Revisão independente e CI real são o aceite; este registro não antecipa seus resultados.

A árvore integrada em main f64 foi validada pelo módulo batch com133PASS/905,033s no Windows, executado no SHA5298f19306f6ae845b4654b78e329af5ed5b5809 antes do merge; no HEADf64, monitor37PASS/6,807s, compatibilidade54+202403 e leitura dos11conjuntos também concluíram, em execuções próprias e com revisão independente. Não somar esses recortes como PASS global Windows. Uma primeira tentativa da leitura parou antes da consulta por corrida no helper privado entre duas imagens de processos; correção delimitada de associação PID/creation foi reproduzida e revista, seis controles passaram e a leitura completa ocorreu em destino novo. Nenhuma fonte, autoridade real ou artefato aceito foi alterado. Para commits somente CI/documentação, eventual reaproveitamento exige identidade autenticada dos bytes de código, runtime e dados; o SHA original dos gates continua explícito.

## Método e limitações

Instruções locais de grill-with-docs aplicadas por leitura de grilling e domain-modeling; pesquisa de fatos delegada ao revisor existente, somente leitura. Não há ferramenta Skill nesta interface: não alegar slash command executado. Revisão independente sustenta o diagnóstico e a plausibilidade da alternativa, não comprova seu custo, prazo ou funcionamento. A rodada de decisões foi concluída; próximo passo é o checkpointA da rota escolhida, com detalhamento técnico e validação proporcionais.

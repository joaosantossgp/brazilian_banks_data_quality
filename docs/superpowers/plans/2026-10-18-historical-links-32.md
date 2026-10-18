# Vínculos históricos das32companhias — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking. AGENTS exige revisão independente por fatia, inclusive na execução nativa.

**Goal:** Corrigir vínculos datados das32companhias em2010–2024 com evidência, preservando indicadores e atualizando recortes seletivamente.

**Architecture:** Reutilizar população/cadastro e composição armazenada. Evidência explícita produz mapas de membership; seu delta define os recortes a reduzir. O sistema financeiro total não ganha/perde contribuições e não chama fórmulas.

**Tech Stack:** Python3.12, DuckDB1.5.6 e Fraction já existentes; nenhuma instalação/dependência nova.

**Spec:** [Especificação](../specs/2026-10-18-historical-links-32-design.md).

## Global Constraints

- Coorte2024 e32companhias preservadas;60referências201003–202412.
- Fonte financeira IF.data; CVM/RI sustentam metadados/vínculos. Não equiparar balanço da emissora e da operadora.
- Base aceita fixada pelo ponteiro compartilhado: manifest ce57545b643d9efcfbb09ee26234c97f131080627d42622c2b4cfbf998f7c524.
- Entrada original: código base2393bbb. Checkpoint18/10: PR153/155 integradas; branch avançado para0d2d389, preservando os deltas locais. Novas instruções de descoberta da base já integradas separadamente pelaPR158, sem alterar dados.
- Destinos novos data/curated/historical-links32-*; fontes/recibos ignorados. Root é integrador. Nenhum arquivo aceito sobrescrito.
- Matriz32×60inclui estados negativos/ausentes/desconhecidos distintos; ausência de prova não é prova de ausência universal.

## Review Focus

1. Mesmo nome com outro CNPJ, especialmente OTParticipações: recusar identidade divergente no teste da fatia1.
2. Prova em2021 não autoriza2010–2020: testar fronteira e eventual fonte comparativa.
3. TTM começa antes da aquisição: preservar janela e sinalizar limite de controle no teste da fatia1.
4. Duas companhias compartilham alvo: uma contribuição por unidade/contexto no teste da fatia2.
5. Alteração do ponteiro durante task paralela: executor mantém pin inicial; testar que o estágio usa argumento/pin fixados e não escolhe automaticamente outra pasta.

## Divisão aprovada e publicada — Issues160/161

1. **Recompor Oliveira Trust com controle datado de1T2021–4T2024.** Plano/spec aprovados por João; execução nativa e entrada factual revisada PASS. Entrega pesquisável:15datasadicionais, originais preservados e recortes novos verificáveis, semretroação.
2. **Revisar asdemais31companhias e consolidar cobertura histórica.** Bloqueada pelo aceite da primeira fatia (fronteira/semântica e mecanismo seletivo demonstrados). Entrega matriz nominal completa, correções comprovadas e limites visíveis no explorador, sem ampliar regras automaticamente.

A divisão evita tickets horizontais de código/dados/UI isolados. A ordem respeita Oliveira primeiro; a leitura/auditoria preliminar das32já realizada não depende da implementação.

## Task1 — Oliveira de ponta a ponta

**Files:** Modify bank_quality/ifdata_population.py, scripts/analyze-ifdata.py, tests/test_ifdata_population.py; recomposição adjacente em bank_quality/ifdata_universe_analysis.py e tests/test_ifdata_composition.py; atualizar a nota engineering e somente metadata/avisos necessários do exporter/template existentes.

**Interfaces:** manter APIs atuais; acrescentar evidência opcional `historical_evidence` às funções de vínculo/build. Formato finito versionado de claims por identidade/data/hash/página. Nova operação adjacente `recompose_membership_changes(composition, pin, membership, membership_pin, output)` consome resultados persistidos e gera derivação com allowlist explícita. Sem framework geral ou alteração de fórmulas.

- [x] Pesquisar16fechamentos/60estados e obter revisão independente factual (16PDFs/pins/páginas conferidos).
- [x] Escrever e observar RED para prova válida1T2021 e recusa4T2020/identidade divergente/cadastro conflitante;202412permaneceigual.
- [x] Implementar admissão finita dos claims, autenticação e registro de origem; executar testes da função pura até GREEN.
- [x] Testar builder/CLI em fixture autenticada: mesmos universos/valores, novos vínculos comprovados, claims duplicados/conflitantes recusados, destinos aceitos protegidos.
- [x] Implementar delta de membership e recomposição seletiva com o redutor existente; teste proíbe `evaluate_metric`, mantém frações totais, deduplica e preserva payloads fora do recorte.
- [x] Medir um contexto real com inputs fixados antes de rodar todas as datas afetadas; se o custo for desproporcional, resolver o gargalo demonstrado, sem reescrever o motor.
- [x] Revisão independente de código antes do lote; depois pacote novo e revisão factual/temporal e econômica independente do lote, incluindo estatística de cobertura e total financeiro inalterado.
- [x] Registrar3T2014–4T2020nãoadmitidos e18datasanteriores àconstituição sem preenchimento artificial. Não transformar proxy de operadora em consolidado da holding.
- [x] Commit da fatia verificada, sem promoção do ponteiro enquanto o pacote não tiver aceite.

## Task2 — Asdemais31 e fechamento

**Files:** mesmos módulos/testes adjacentes daTask1, nota de pesquisa, spec/plano/ledger; exporter/template apenas para metadata necessária. Sem README/AGENTS/glossário/arquitetura/CI fora da integração autorizada. Registrar extensão da allowlist naIssue antes de necessária.

**Interfaces:** consumir claims/mapas daTask1 e auditoria32×60; preservar os32CNPJ e seus códigosCVM. Cada correção declara fonte temporal e allowlist própria; caso semprova permanece diagnosticado.

- [x] Inventariar deterministamente os1.920mapas existentes e seus estados sem calcular indicadores.
- [x] Revalidar proveniência dos28casos com60/60unidades e os eventosPAN/DM/Daycoval/BRPartners. Conferir Cielo e Nacional na janela inteira; não chamar ausência de reporte de inexistência econômica.
- [x] Nenhuma outra diferença de alvo foi comprovada. Para eventual diferença comprovada, adicionar caso causal RED, implementar mudança mínima e conferir GREEN; separar conflitos/falta deprova do que é corrigível. Não exigir documento novo por trimestre quando a regra de intervalo tiver prova suficiente, nem criar regra desse tipo sem explicitá-la.
- [x] Executar somente metadados e recortes atingidos, preservando a base aceita e as correçõesTerra/Caixa jáincorporadas. Medir antes de ampliar e registrar impacto real.
- [x] Revisão independente porfatias de correções; comparar integralmente contribuições/foraescopo e N/D/coortes/companhias/cobertura, sem refazer fórmulas.
- [x] Exportar HTMLnovo e conferir dados/filtros/proveniência; copiar privadamente aoDrive se aplicável, mantendo anterior.
- [ ] Revisão final de inventário/allowlist/SHA e testes concluídos; PR/CI/integração em acompanhamento. Não apresentar resultado local como integração.
- [ ] Após aceite local, promover explicitamente current-indicators.json e registrar no mapa2; tarefas paralelas mantêm seus pins. Integração/CI remota em acompanhamento.

## Self-review e handoff

O plano cobre os requisitos da spec, usa uma fronteira de vínculo/composição existente e sóduasfatias completas. Não houve código de produto ou promoção. Proposta de execução: **nativa pelo integrador, com revisões independentes nas duas fatias**, para reduzir releitura/custo; alternativa é implementar por subagentes. A escolha e revisão do plano são de João, conforme writing-plans/to-tickets solicitados. Aprovação recebida em18/10/2026; execução nativa com revisão independente por fatia, conforme Issue156.
## Checkpoint de entrega local

Fatia160 e161 com revisão independente PASS; commit inicial b41d862. HTML novo exportado e conferido:305.296células/4.300.156frações,54recortes exatos,13kagregados comparados. SHA HTML903b77a302a46b30af206d608fba6277f9064cf54148a46548755672eff5892d. Nova cópia privada estática noDrive,98.315.714bytes e pastaMono2confirmados porreadback, anterior preservada. Não se alega nova inspeção visual humana: o aceite visual anterior referia-se à versão anterior. A primeira execução doQA falhou na guarda do destino dooráculo; helpers foram copiados ao workspace próprio e a segunda execução concluiu PASS, preservando o log anterior.

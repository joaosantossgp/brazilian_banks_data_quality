# Fronteiras dos módulos financeiros — 2026-10-12

Entrega incremental da [Issue95](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/95), após documentação92, seleção OData93 e CI Windows94. Base da primeira fatia: `dcf32026d02e1326d2c7cd599d858192cfd4c67b`. O [review91](repository-review-20261012.md) identifica o acoplamento e o legado ativo. Este registro não altera contratos acadêmicos, perfis instalados ou dados aceitos.

## Fatia A: âncora e prova física da captura202403

`financial_acquisition_batch.verify_trusted_202403_sources(entry: dict) -> dict` passa a ser a fronteira pública para a captura histórica aprovada. O batch compara os bytes JSON canônicos da entrada inteira com a âncora instalada antes de chamar a prova física existente. Campos extras, tipos diferentes (inclusive float/int e bool/int), hashes, paths ou outra captura não podem virar uma nova âncora. O retorno é uma cópia independente; não concede aquisição, instalação, recuperação ou admissão financeira.

O helper físico conserva sua validação completa: corpos e referências autenticados, resolução nativa, ligações A/B, prefixos de receipts e estado corrente da autoridade. A nova API não trata coerência interna de outra captura como aprovação. `financial_report_profiles.compose_acquisition_handoffs` continua responsável pelo arquivo externo pinado/confinado e pela projeção dos handoffs, consumindo a API pública para a confiança202403. A prova interna usada pelo próprio batch permanece privada; outros acessos privados da ponte agregada ficam para a próxima fatia.

Alternativas examinadas: somente renomear o helper não centralizaria o invariante de confiança; extrair o coordenador inteiro ampliaria imports, ownership e pins sem necessidade. A API específica move uma responsabilidade concreta, sem prometer eliminar o ciclo completo acquisition↔batch.

### Arquivos e execução

AllowlistA: `bank_quality/financial_acquisition_batch.py`, `bank_quality/financial_report_profiles.py`, `tests/test_financial_report_profiles.py`, esta nota e `docs/architecture.md`. Root executa e integra compartilhados; reviewer independente lê e reporta. A nota reutiliza `docs/engineering/`; não há módulo, raiz, camada ou dependência nova, renames ou deletes. Preparação privada fica em `.scratch/module-boundaries-20261012/`.

1. A1: testes da fronteira pública RED por API ausente; implementação mínima; GREEN com recusa antes de I/O, prova física real, equivalência e isolamento do retorno. Revisão independente PASS no checkpoint `f43b9db` antes de migrar o caller.
2. A2: teste do caller RED (zero chamadas públicas); migração para a API; revalidação das contraprovas físicas e handoffs existentes. Captura alternativa coerente também é recusada diretamente pela API pública antes do helper.
3. Composição: revisão independente dos cinco paths, checks pertinentes e SHA final antes da integração. Resultados, tempos e estados remotos são registrados na Issue/PR; este documento não presume CI ou merge pendentes como aprovados.

Testes direcionados: `python -B -m unittest discover -s tests -p test_financial_report_profiles.py -k AcquisitionBridgeTests -v`. Os nomes também selecionam as classes de ponte batch/histórica, revalidando a composição próxima. Suítes de autoria/batch/pipeline e CI Ubuntu/Windows seguem o impacto; não repetir a mesma suíte sem mudança ou dúvida concreta.

### Pins e compatibilidade

Alterar batch e profiles muda seus bytes. Batch participa de `_CODE_FILES`/`_CODE_FILES_V2`; ambos participam dos onze módulos em `financial_pipeline._code_pins`. **Planos antigos continuam recusando código diferente**, sem reescrever pins, manifests, receipts, bootstrap ou fixtures históricas para contornar essa proteção. Novos planos, somente quando seu contrato autorizar, têm nova identidade. A fatia não executa ou migra planos antigos nem coleta dados.

A conferência usa pins capturados na base anterior e `_check_code` real: espera recusa após a mudança; pins correntes devem ser aceitos pelo mesmo verificador. Os outros nove módulos e a fixture histórica `.evidence` devem conservar seus hashes. A preservação de evidências físicas é também conferida pelos snapshots das fixtures nos testes de ponte. Contratos de admissão/Parquet, handoffs projetados e seus hashes permanecem próprios.

## Próximas fatias da mesma frente

- **B — snapshot consistente da autoridade batch:** reduzir os acessos da autoria a `_open_batch`, estado e helpers. Definir primeiro a leitura única, prova e estrutura de retorno; manter a consistência autenticada e a barreira antes de qualquer projeção.
- **C — contratos finitos acquisition↔batch:** reduzir dependência circular das constantes/políticas de execução. Exige identidade de execução, ownership e tratamento de pins explícitos; não é uma extração mecânica de constantes.

B/C exigem contrato, allowlist, regressões e revisão próprios antes da escrita. A conclusão de A não encerra a Issue95 nem comprova que o pacote inteiro foi modularizado. Código legado ativo e evidências anteriores permanecem preservados.

## Fatia B: snapshot sob a autoridade corrente

[Contrato B](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/95#issuecomment-6129092513), base `ae25c25`, branch `codex/module-boundaries-bc-20261012`. A allowlist reutiliza os mesmos cinco arquivos de A; sem novo módulo, camada ou dependência. A prova corrente v1 não é substituída por `verify_historical_capture`, que autentica evidência histórica sob contrato distinto e sem claim do runtime antigo.

`verified_recent_capture(bundle_path, handoff_path, *, bundle_sha256, bootstrap_sha256, handoff_sha256, authoring_state_paths=())` é um contexto público no batch. Autentica a janela finita e todas as entradas, mantém uma única claim durante prova e projeção e entrega um snapshot independente. Preserva o inventário físico anterior: bundle, handoff, registry de autoria, código pinado, bootstraps, journals, heads, jobs, bindings, checkpoints e receipts. Paths adicionais são relativos e confinados, acrescentam imagens antes/depois e não concedem autoridade. Na saída, reconfere bytes imutáveis e imagens; a projeção só pode ser retornada depois da saída bem-sucedida.

Profiles conserva a seleção do descritor instalado e a projeção das fontes. Não recebe o objeto `_Batch`, handles, callbacks de execução ou journals mutáveis. O retorno da ponte conserva contrato, shape, seleção, fontes, hashes, contadores e sequências; não concede aquisição, recuperação, admissão ou comparabilidade.

Plano de execução e checkpoints:

- B1: três testes RED pela ausência da API; extração da prova existente; GREEN com arquivos reais, abertura/prova únicas, isolamento do snapshot, mudança do registry detectada na saída e liberação da claim após erro. Checkpoint `a4dbf18`, revisão independente PASS antes da migração.
- B2: regressão causal do caller RED (zero chamadas públicas); migração para o contexto público; testes de adulteração/pending/halt e contraprovas de ausência de projeção em falha inicial e mudança durante a projeção. `python -B -m unittest discover -s tests -p test_financial_report_profiles.py -k AcquisitionBridgeTests -v`: 18 testes PASS em 93,200 s. Composição `4b62624` revisada independentemente PASS antes de C; diff/allowlist e verificador real de pins conferidos.
- Integração: CI integral Ubuntu/Windows e pós-merge; árvores revista/integrada equivalentes. Evidências de tempos, SHA e estados remotos na Issue95/PR, sem antecipar PASS.

Os pins de batch/profiles mudam novamente; valem as mesmas restrições de A. Os nove outros módulos pinados e fixtures históricas permanecem intactos até uma eventual allowlist posterior explícita. Nenhum plano aceito é regravado.

## Fatia C: contrato finito dos membros recentes

[Contrato C](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/95#issuecomment-6129223394), base B revista `4b62624`, mesma branch. Allowlist: batch, acquisition, `tests/test_financial_acquisition.py`, esta nota e arquitetura. Composição B+C: sete arquivos, sem novo módulo, camada, dependência, move ou delete.

`financial_acquisition_batch.recent_member_contract(acquisition_scope: str) -> dict | None` é consulta pura dos sete scopes recentes v1. Devolve cópia de período/políticas ou `None`; não concede execução. Acquisition usa esse contrato público para conferir singleton na preparação e políticas exatas na verificação executável, em vez de reconstruir o mapa a partir de constantes privadas.

Preparação continua aceitando candidatos `issue50/*` com limites próprios e `executable=False`. A execução conserva caps standalone, schema/version/executable/políticas fechados dos membros batch, catálogo/descritor/targets, dispatch histórico v2 e a capability do coordenador. Não se transfere uma restrição de execução para a preparação incidentalmente. Imports tardios entre aquisição e batch permanecem onde a autorização do runtime exige contexto; esta fatia não promete eliminar o ciclo inteiro.

Plano e checkpoints:

- C1: teste RED da API ausente, sete scopes exatos, desconhecidos/aliases/tipos, retorno isolado e ausência de I/O; implementação mínima GREEN. Checkpoint `628bb1f`, revisão independente PASS antes de migrar callsites.
- C2: regressão causal das chamadas públicas RED (zero de duas chamadas); migração de `prepare_job` e `_execution_job`; candidato com limites alternativos prepara mas não executa. `python -B -m unittest discover -s tests -p test_financial_acquisition.py -k AcquisitionTests -v`: 57 testes PASS em 2,761 s. Suíte batch pertinente e revisão independente da composição B+C seguem antes de publicação/integração; resultados e tempos na Issue95/PR.
- Pins finais mudam acquisition/batch/profiles, sem modificar os oito outros módulos ou a fixture histórica. O verificador real deve recusar pins anteriores e aceitar correntes. CI integral Ubuntu/Windows e pós-merge continuam gates próprios.

## Inventário de encerramento do review91

R1 seleção OData: Issue93/PR97. R2 validação Windows: Issue94/PR98. R3 orientação atual, R4 mapas/dicionário e R6 links relativos: Issue92/PR96. R5 interfaces: Issue95, A/PR101 e composição B/C desta nota. Os estados de integração e CI são conferidos nas Issues/PRs reais. Legado ativo, evidências e contratos próprios permanecem; apagar módulos antigos não faz parte do aceite. A pesquisa metodológica99 e decisão acadêmica3 têm escopo separado e não são bloqueios técnicos desta frente.

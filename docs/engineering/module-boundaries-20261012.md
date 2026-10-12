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

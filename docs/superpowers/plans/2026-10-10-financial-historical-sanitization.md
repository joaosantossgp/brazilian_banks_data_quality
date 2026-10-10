# Sanitização histórica comum — plano da Issue 60

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans para implementar por checkpoint, com revisão independente antes da expansão. Não há obrigação de PR por checkpoint.

**Goal:** reutilizar o executor financeiro existente para sanitizar as 55 referências restantes por janela autenticada, mantendo os 11 aceites anteriores e chegando a 66/66.

**Architecture:** acrescentar leitura autenticada de captura histórica concluída ao módulo de aquisição existente, uma ponte versionada no composer e dispatch genérico no pipeline. Reutilizar os readers/adapters e os sete estágios atuais; não criar outro executor, ledger, backend ou pipeline por período.

**Tech Stack:** Python 3.12.13, DuckDB 1.5.6, Parquet e contenção Windows existentes; sem dependência nova.

**Spec:** contrato da [Issue 60](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/60#issuecomment-6099664402), [rota aprovada](../../engineering/historical-route-reassessment-20261010.md) e contratos/fluxo da [Issue 57](2026-10-05-financial-batch-sanitization.md). O plano57 e seus artefatos aceitos permanecem imutáveis.

Base: `main fbcad8555d72f88d233e8b87bcf23ff24c4632bf`. Branch: `codex/financial-historical-sanitization`. Root executa e integra; reviewer independente lê/testa somente o recorte delegado. Este plano prepara software; não afirma primeiro handoff59 disponível ou autorização para retomar a coleta inconsistente.

## Restrições globais

- Universo: as55 referências e16 janelas da policy `16949510b28c525348590a10d93fcacfe25114815c08fc0e2b5df4e98eb31663`; quatro relatórios oficiais e todas as variáveis disponíveis, sem oito variáveis fixas ou pipelines por trimestre.
- Preservar contratos v1/aceites57, registros originais, native IDs, precisão/Decimal, árvores, ausências, unidades, janelas e regimes. Não harmonizar conceitos nem escolher método/amostra acadêmicos.
- Inputs: bundle, bootstrap e export completos com SHA externos. Captura incompleta, halt, pending, incoerência, fonte incompleta ou associação ambígua interrompem a preparação.
- Captura antiga é evidência: nenhuma execução de código/runtime antigo; nenhuma abertura de claim, recovery, reset, alteração de orçamento, GET ou instalação na leitura60.
- Pins atuais do executor60 são separados dos pins imutáveis da captura59. Não trocar HEAD/runtime dentro de bundle, journal ou receipt para torná-los atuais.
- Destinos novos em data/runs, data/derived e data/curated; replay próprio. Um lote conta como aceito após perfil/admissão/Parquet/query/accessor/replay/comparação, e não apenas por fonte/perfil existente.
- Resultado da janela conta somente seus membros aceitos. Cobertura global continua na61/mapa2; não criar suplemento ou ledger de cobertura paralelo por conveniência.
- Somente este checkout/máquina; Project3 com Zec. Sem segurança, credenciais, proteções, deploy, outros hosts/projetos, runtime/dependência novos.

## Ownership e impacto na arquitetura

A etapa documental cria somente este plano em destino canônico e atualiza a nota de rota existente. Software proposto: `bank_quality/financial_acquisition_batch.py`, `bank_quality/financial_report_profiles.py`, `bank_quality/financial_pipeline.py` e seus três testes adjacentes. O primeiro módulo recebe somente a leitura de captura; seus gates de execução permanecem exigidos e testados. Composer/pipeline conservam suas responsabilidades atuais. Sem nova raiz, camada, rename ou delete.

Readers `financial_reports.py`, adapters `financial_reports_parquet.py`/`financial_parquet.py`, Windows, registry/perfis instalados, README e arquitetura ficam fora do primeiro recorte de software. Registry/perfis entrarão apenas no aceite de cada lote real, em allowlist exata do integrador. A CLI `scripts/run-financial-pipeline.py` só entra se não conseguir delegar à API existente sem mudança; registrar a necessidade antes de escrever.

## Foco da revisão

1. Captura concluída sob HEAD anterior continua legível; captura incompleta ou modificada é recusada, sem afrouxar gates executáveis59.
2. Um export coerente superficialmente não substitui replay dos journals e vínculo físico entre receipts, A/B, resolução e fontes.
3. Período, seleção, família e quantidade vêm da janela/policy autenticadas, nunca de defaults recentes ou nomes comuns.
4. Planos57 continuam executáveis em seu contrato; novos planos60 não ganham acesso a membros ou destinos arbitrários.
5. Precisão, largura cadastral e ausências vêm dos dados nativos, incluindo bindings com largura superior a38; contagem de lote não fabrica cobertura global.

## Checkpoint A — leitura de captura e ponte histórica

Resultado observável: uma captura v2 completa vira envelopes por membro sem tocar autoridade nem executar o código capturado. A validação do contrato/allowlist precede código. Dados reais continuam bloqueados pelo handoff59.

### A1. Prova read-only no módulo existente

Proposta de API:

```python
verify_historical_capture(bundle_path: Path, handoff_path: Path, *,
                          bundle_sha256: str, bootstrap_sha256: str,
                          handoff_sha256: str) -> dict
```

Inputs dentro dos destinos já autorizados, com path containment e proteção de reparse existentes. O hash externo do export ancora seu head/summary/code_pins; bundle/bootstrap externos ancoram seleção, jobs, policy e bindings. Validar schema fechado dos pins capturados e sua igualdade entre export/bundle. Não exigir que esses pins coincidam com HEAD60 nem afirmar que representam execução atual. Nenhuma imagem histórica é importada/executada.

- [ ] Escrever testes causais com captura sintética completa, usando fixtures históricas existentes; executar RED.
- [ ] Reconstituir bundle/draft/jobs/bindings e policy por dados. Reusar validações puras existentes, separando-as da conferência de identidade executável apenas quando necessário; manter essa identidade obrigatória nas APIs59.
- [ ] Reusar `_replay_phase_records`, `_replay_member_records`, `_prove_receipt_prefix` e `_prove_phase_sources` para autenticar journals, heads, contadores, fases, receipt/session e A→B. Exigir completo, sem halt/pending, todos os membros/seleções exatos e nenhuma fonte extra.
- [ ] Autenticar resolução e corpos/manifests/sidecars por hashes e semântica nativa existente; não aceitar só JSON ou só o digest do export.
- [ ] Retornar projeção de estado/membros e inventário dos inputs efetivamente lidos. Conferir imutabilidade ao final; pipeline reautentica esse inventário ao usar a projeção.
- [ ] Testar mutações de cada elo, contador booleano, journal truncado, head divergente, binding/job alterado, receipt antigo inadequado, A/B trocados, source incompleto, membro faltante/duplicado/extra e troca de arquivo durante leitura.
- [ ] Provar zero chamadas a claim/recovery/launcher/fetch e ausência de escrita nos inputs. Demonstrar HEAD60 diferente aceito somente na leitura; execução59 com pins antigos continua recusada.
- [ ] GREEN pertinente e revisão independente antes de A2.

Variantes técnicas de janela exigem sua prova de derivação/ligação preservada. Não aceitar sufixos arbitrários. F1-01-R1 hoje está falho e não é input admissível; eventual continuação2010 da59 deve fornecer prova correspondente antes de seu aceite60. Isso é pendência dentro dos55, não exclusão de2010 do objetivo.

### A2. Ponte no composer existente

Proposta de API:

```python
compose_historical_acquisition_handoffs(bundle_path: Path, handoff_path: Path, *,
                                       bundle_sha256: str, bootstrap_sha256: str,
                                       handoff_sha256: str) -> dict
```

- [ ] Projetar `ifdata-financial-historical-sources-v1` por seleção usando `descriptor_for_selection` e `_project_acquisition_handoffs`; mesmos `compile_metadata_candidate`/`freeze_profile`.
- [ ] Retornar `ifdata-financial-acquisition-batch-bridge-v2`, com batch/policy/window, source_state/source_state_files e membros ordenados da janela autenticada. O contrato v1 permanece próprio.
- [ ] Testar as16 janelas/famílias anunciadas e erros de associação com fixtures; usar árvores e D/N suficientes para conferir bindings, escala/largura/ausências em famílias representativas. Não confundir catálogo anunciado com dados reais aceitos.
- [ ] Revisão parcial antes de ampliar ao pipeline.

## Checkpoint B — dispatch comum de preparação e execução

Resultado observável: o mesmo pipeline prepara perfis e executa seus sete estágios para membros da janela histórica autenticada, sem listas literais por ano/período.

- [ ] Introduzir contratos `ifdata-financial-sanitization-prepare-v2` e `ifdata-financial-sanitization-plan-v2`. Derivar a lista fechada de membros da ponte validada/policy; preservar `_WINDOW` e defaults do caminho v1.
- [ ] Adaptar validação/dispatch/worker, paths, journal e status ao contrato fechado v2. Reusar APIs `prepare_profiles`, `run_pipeline`, `read_status`; não acrescentar modo permissivo ou lista de períodos fornecida pelo caller.
- [ ] No v2, recusar suplemento legado de aceites recentes. Registrar resultado/aceites da própria janela; catálogo61 agrega a cobertura depois do aceite. Reutilizar a captura de registry-before/proposed e a instalação exata externa, sem modificar perfis no prepare.
- [ ] Reusar admit/convert/query/replay-admit/replay-convert/replay-query/compare. Manter contenção, quarentena, replay, recursos por máquina e falhas locais/globais do executor57.
- [ ] TDD: janela fora da policy, membro extra/duplicado, mistura v1/v2, plano alterado, destinos reaproveitados, perfil/registry diferente da proposta, falha/schema/quarentena e retomada; verificar identidade e todos os valores numéricos em query/accessor/replay.
- [ ] Revisão parcial por mudanças no worker/runner; regressão pertinente do v1 e conferência final de composição/checks/CI. Uma PR pode reunir A+B; tamanho não determina o checkpoint.

## Checkpoint C — primeiro lote real consultável

Bloqueado até captura59 completa/revisada. Pode ser a primeira janela disponível; não depende de todos55 nem de ordem cronológica sem justificativa técnica.

- [ ] Fixar hashes externos do handoff real e inventário protegido dos11; medir recursos e usar destinos novos.
- [ ] Preparar/revisar perfis nativos da janela, com todas as variáveis; integrador instala exatamente propostas/ativações revisadas.
- [ ] Executar os sete estágios, conferir contagens/ausências/Decimal/tokens/identidades, replay integral e preservação dos11.
- [ ] Revisão do lote antes de ampliar famílias/janelas; registrar fontes capturadas, perfis, aceites locais, publicação de software e catálogo separadamente.

## Checkpoint D — completar55 e conferir66

- [ ] Repetir por janela com o mesmo executor. Diferença de família comprovada gera correção comum, teste causal e revisão antes da expansão, sem pipeline/PR por trimestre.
- [ ] Resolver também2010 e qualquer variante/continuação59 necessária; nenhum período pendente pode desaparecer da cobertura final.
- [ ] Atualizar catálogo61 por lotes aceitos, preservar originais e evidência de falha/ausência, concluir composição/revisão/CI e auditoria64.
- [ ] Confirmar55 novos aceites completos e66/66 globais por evidência atual. Método/amostra/indicadores e conteúdo complementar62/63 conservam decisões próprias.

## Evidência dos checkpoints de software — 2026-10-10

A1 e A2 receberam revisão independente APP antes da expansão. A1 verificou captura completa e mutações sem autoridade/GET; A2 passou o módulo completo de28 testes em134,616s. A matriz de55 seleções/16 janelas verifica associação e dispatch, não prova árvores/D/N reais de todas as famílias. Uma janela sintética de quatro membros2010 exercitou compilação, preparação e os sete estágios reais com launcher isolado; a rodada posterior à redução de releituras passou dois testes em138,966s.

B conserva o inventário completo, mas deriva dos manifests pinados quais corpos aceitos pertencem a cada membro: checagens globais por estágio autenticam estado/manifests/sidecars e tentativas falhas; o corpo em uso é conferido antes do consumo. Entrada/retomada e fechamento verificam o conjunto integral. Isso remove releitura dos corpos de todos os outros membros em cada estágio; não há benchmark real nem promessa de prazo baseada na fixture.

A revisão parcial encontrou P2: o score reabria o bundle depois de uma falha de integridade. Corrigido para usar membros do plano autenticado; halt global torna os membros quarentenados e zera aceites da janela. O teste causal com score real reproduziu o erro antes da correção e passou depois; outro cobre aceito→halt global→quarentena. Revisão independente APP do código B/composição nos oito paths, condicionada aos checks finais.

A suíte ampla Windows foi interrompida deliberadamente após cerca de28min, sem terminal global, para publicar a PR e usar a CI existente como gate integral. Seu log parcial conserva os casos concluídos, incluindo os quatro testes históricos novos e as regressões anteriores já percorridas; isso não constitui PASS da suíte nem do módulo pipeline inteiro. O módulo nativo CPU Windows passou em rodada própria: dois testes/0,385s, contenção e extinção reais. Guards Node e portal2/2 passaram. A suíte completa no SHA publicado continua obrigatória antes do merge; essa mudança de execução evita exigir duas rodadas amplas por padrão, sem retirar a verificação pertinente do Windows ou os checkpoints independentes.

C/D permanecem pendentes: nenhum destes testes aceita dados reais. Cobertura continua11/66; a captura59 inconsistente está preservada, sem nova execução financeira neste recorte. Variantes de recuperação/continuação também continuam pendentes dentro do objetivo55.

## Comandos de verificação previstos

Testes focados por nome durante RED/GREEN. Após composição A+B, usar `python -B -m unittest discover -s tests -p test_financial_acquisition_batch.py -v` e os padrões correspondentes de profiles/pipeline, ou a suíte pública única `python -B -m unittest discover -s tests -v`, além dos checks de escopo/documentação existentes conforme o diff. Testes nativos pertinentes no Windows e suíte CI existente no SHA final. Não somar execuções isoladas como PASS global nem repetir read11 completo sem mudança que o justifique.

Nenhum prazo de ingestão é estimado a partir de fixtures. Medir o primeiro lote real para estimar execução; a disponibilidade de fontes e a inconsistência59 continuam incertezas explícitas.

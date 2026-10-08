# Catálogo financeiro local — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task após claim explícito na Issue 61. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** localizar e consultar os 66 snapshots financeiros reais por período, perspectiva e relatório nativo, iniciando software com 11 aceitos sem reduzir o aceite final 66.

**Architecture:** catálogo JSON fechado, determinístico, pinado e imutável, com metadata leve para descoberta e abertura delegada aos adapters existentes. Autoridade histórica, disponibilidade das etapas e saúde atual permanecem separados.

**Tech Stack:** Python stdlib e unittest existentes; DuckDB/Parquet somente na abertura de snapshots. Nenhuma dependência ou runtime novo.

Issue: [#61](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61); [spec](../specs/2026-10-06-financial-catalog-design.md); [mapa 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2). Base de consolidação: main `c7455f06ff2dc52a7958e300b19df01bca9b92c7`; branch `codex/financial-catalog`. Responsável: root, implementação e integração. Conferir HEAD/estado real antes de claim de código.

## Inventário, arquitetura e exclusões

| Arquivo | Responsabilidade |
|---|---|
| `bank_quality/financial_catalog.py` | Parser das autoridades, catálogo, descoberta, resolução e ponte lazy de um snapshot |
| `scripts/query-financial.py` | CLI fina, parâmetros, templates de consulta e erros JSON |
| `tests/test_financial_catalog.py` | Integridade, autoridades, oferta/aceite, revisões e determinismo |
| `tests/test_financial_catalog_query.py` | Adapter real/Decimal, query/CLI e fechamento no cancelamento |
| `docs/superpowers/specs/2026-10-06-financial-catalog-design.md` | Contrato desta responsabilidade |
| `docs/superpowers/plans/2026-10-06-financial-catalog.md` | Etapas, checks e checkpoints |
| `docs/engineering/financial-catalog-20261006.md` | Ledger de execução/limites/evidência |
| `README.md`, `docs/architecture.md` | Acesso humano e responsabilidade adjacente, integrador único |

Todos os destinos/pastas já existem; sem rename/delete, nova raiz/camada ou serviço. A arquitetura precisa incorporar a responsabilidade adjacente antes de código. A etapa documental atual escreve apenas spec/plano; claim posterior enumera a allowlist de implementação e novos destinos privados.

Somente checkout/host autorizado. Leitura dos módulos/perfis/registry existentes; nenhum write em readers/adapters/pipeline/registry/perfis instalados. Exclusões: aquisição/compat/launchers 59, authoring 60, dados aceitos, bruto, archives/chaves, requirements/runtime, CI/proteções, AGENTS/GLOSSARY/tracker, Project 3 e outros hosts/projetos. Gates/query usam destinos novos; catálogo anterior é preservado.

## Task 0 — entrada, contrato e claim

- [x] Conferir autoridade dos três legados e suplemento 403, refs físicas/nativas/índices/replays e estados disponíveis; preservar receipts 42/46 ausentes, sem flags inventados.
- [x] Conferir payloads primários/replay 42/46 e embedded source correspondente à própria admissão.
- [x] Conferir plano/result/head/49 receipts e outputs dos sete membros 57; preparar os sete wrappers fechados.
- [x] Registrar interface prospectiva 60→61: contrato versionado/gates integrais, tipo/parser próprios revisados antes de novos membros; unknown rejeitado até extensão.
- [x] Revisar spec/plano públicos e registrar evidência/resultado na 61 (APP documentalbb77; claim6061550752).
- [x] Atualizar arquitetura e claim de implementação com HEAD/base, allowlist, owner, destinos privados e recursos medidos. Prontidão positiva do software inicial 11 é distinta do corpus final 66.

Os quatro checkpoints de entrada possuem hashes/escopos na spec. A conferência dos helpers não substitui o parser futuro nem o gate Windows 59. Autoridade confiável é derivada da base Git e pins externos, nunca de boolean fornecido pelo caller ou tabela alterada pelo candidato.

## Task 1 — integridade, autoridades e catálogo

- [x] RED: criar testes causais de hash obrigatório/mismatch, duplicate JSON keys/inputs/selections/reports, fields extras, NaN, IDbool/zero, path absoluto/UNC/drive/backslash/escape/symlink/junction, output existente.
- [x] RED: testar oferta 66≠aceite 66; tipo desconhecido, falso accepted, hashes/links/perfil/seleção divergentes, replay como primary e whitelist histórica ampliada.
- [x] Executar somente o módulo novo e observar falha pela ausência do comportamento exigido.
- [x] Implementar parser fechado e captura dos bytes pinados uma vez; sem import pesado na descoberta. Reautenticar três tipos finitos 11 da spec, sem copiar toda a aquisição/lineage ou chamar authoring/run.
- [x] Implementar serialização determinística, registry/proofs pequenos congelados, oferta/aceite/revisões/active separados; rejeitar duplicação antes de normalizar.
- [x] GREEN: executar módulo novo, conferir ausência de imports DuckDB/writes/GET no list. Revisão independente parcial e resolver achados antes da ponte de consulta.

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_financial_catalog.py -v
```

API/schema/ordenação/erros exatos estão na spec. Testar que hash alternativo ou caller não amplia os três anchors; stage_evidence absent_from_transport não se torna false gate. Catálogo congelado continua listável após mudança de outro membro no registry.

## Task 2 — resolução e consultas nativas

- [x] RED: seleção desconhecida/sem gate/revisão ambígua/explícita, report fora da seleção, drift do membro/perfil e metadados alterados. Não escolher latest/mtime automaticamente.
- [x] RED: ponte real às fixtures dos adapters, precisão larga/texto/Decimal e None, filtro report parametrizado sem reduzir a seleção do perfil, binding grupo/texto/IDdesconhecido.
- [x] Implementar snapshot_connection/iter_numeric_decimals delegando ao adapter nativo com hash externo; um snapshot por vez, fechamento de conexão e iterator no cancelamento.
- [x] GREEN: executar somente os dois módulos 61; revisão independente da seleção/ponte antes de CLI e corpus.

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_financial_catalog*.py' -v
```

Nenhum cast/UNION numérico global, SQL DECIMAL>38, DOUBLE, arredondamento, annualização, fórmula ou join acadêmico. Reader conserva todas as variáveis oficiais e ausências nativas.

## Task 3 — CLI e corpus 11

- [ ] RED: commands catalog-prepare/list/show/counts/bindings/cells/decimals, hash externo, filtros/limites, Decimal textual, exits 0/2/3 e erros sem payload completo/segredo. Conferir ausência de SQLarbitrário.
- [ ] Implementar CLI fina conforme spec; células default 100/max 10000 e parâmetros vinculados.
- [ ] Medir recursos livres nesta máquina e preparar janela serial para corpus. Não impor teto universal, não concorrer com 59 sem orçamento positivo.
- [ ] Criar catálogo em destino novo ignorado dos 11 wrappers, com hash externo; conferir 66 ofertas/11 aceitos/55 unavailable, determinismo, refs internas e preservação de entradas/catálogos anteriores.
- [ ] Consultar 11 reais serialmente com contagens/bindings/Decimal e comparação às metadata; documentar escopo real, medida e hashes protegidos. Não afirmar fresh gate por proof histórico ou read 11 anterior.
- [ ] Revisão independente parcial do resultado antes de ampliar cobertura.

Os helpers da preparação não são ferramentas públicas instaladas. Antes de comando real, registrar na 61 o input/hash, destino inexistente, recursos e comandos próprios; nunca repetir execução sobre destino aceito.

## Task 4 — documentação, composição e integração

- [ ] Ledger com comandos/saídas, recursos, refs, domínio/limites, resultado local/revisão/publicação separados; exemplos públicos com paths/hashes explícitos e sem dados privados.
- [ ] Conferir links, inventário/diff vs allowlist, arquitetura e hashes protegidos; testes novos+regressões pertinentes do pacote. Suíte final/checks proporcionais; não repetir fullsuite sem nova mudança/falha que justifique.
- [ ] Revisão independente do SHA final/composição, checks, publicar PR autorizada, integrar após gates aplicáveis e verificar CI pós-merge/main ancestry.
- [ ] Atualizar 61/mapa 2 com paralelo/#16 e blockers. PRtamanho livre; checkpoints/revisões parciais obrigatórios durante a implementação.

## Task 5 — expansão até 66

- [ ] Após primeiro handoff 60, fechar schema/tipo novo com refs reais e testes causais; revisão antes de admitir membros. Nenhum fallback pipeline57 ou anchor histórico ampliado.
- [ ] Preparar novos catálogos por janelas aceitas com parent pinado, preservando revisões anteriores e escolha ativa explícita; conferir antes de cada ampliação.
- [ ] Conferir 66 seleções financeiras reais aceitas, quatro relatórios/allvariables, descoberta e consulta/precisão por membro. Oferta/fixture/profile 66 não prova aceites 66.
- [ ] Aceite final 61 e evidência reproduzível, revisão de domínio/software distintas e atualização 64/Goal. Manter 3/14/16 metodologia e 62/63 conteúdo em seus contratos.

A integração do software inicial 11 não encerra 61 ou Goal. A coleta 59 continua sujeita a Windows/compat54/202403/read11/pins/recursos, e 60 ao handoff/contrato próprios. Decisão acadêmica e conteúdo final permanecem comJoão/orientador.

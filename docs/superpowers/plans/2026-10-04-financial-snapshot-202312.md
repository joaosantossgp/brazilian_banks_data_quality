# Snapshot financeiro 202312 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Admitir e consultar o snapshot financeiro202312/1005/Resumo92 offline com precisão, ausências e proveniência preservadas, sem alterar a semântica dos snapshots202412/individuais.

**Architecture:** Extensão delimitada dos módulos financeiros existentes, com seleção explícita entre dois perfis fechados. Contexto de referência/perfil passa por cada chamada, sem trocar constantes globais durante execução. O perfil202312 fixa cadastro32 e exceção legada dos dois manifests/corpos revistos; perfil202412 permanece intacto. Parquet/abertura derivam contrato/partição/schema exclusivamente da seleção validada e continuam de um único snapshot.

**Tech Stack:** Python, biblioteca padrão/unittest, DuckDB1.5.6 já instalado, Parquet ZSTD; sem dependência nova.

**Spec:** [Contrato202312](../../engineering/financial-snapshot-202312-contract-20261004.md), [modelo lógico aprovado](../specs/2026-10-04-logical-data-model-design.md), [ADR0001](../../adr/0001-duckdb-parquet.md).

**Issue:** [36](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/36), parentmapa2; base7545fc5cfa9d2235ba605c500503bdbedf56d931, branchcodex/financial-snapshot-202312. **Execução inline autorizada:** João pediu continuidade e, em2026-10-04, um goal para fazer os passos em sequência, consultando-o apenas para decisões de produto/objetivo/mudança crítica. Esta autonomia substitui novos gates rotineiros de confirmação do plano/modo/publicação para o escopo aprovado; revisão independente/checks permanecem obrigatórios. Pesquisa [37](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/37) tem nota exclusiva e roda em paralelo, sem dependência para iniciar36.

## Global Constraints

- Somente202312/202412, perspectiva1005/Resumo92, defaults e APIs202412 preservados. Não aceitar referência arbitrária/latest, rede, cadastro1006, multissnapshot, calendário, metodologia/indicadores ou comparabilidade automática.
- Perfil202412/Parquet individual e dados aceitos imutáveis. Índice explícito202312 com cinco manifests resolve paths em relação ao próprio arquivo; índice diagnóstico da34 não é entradaCLI.
- Cadastro202312 exatamente32strings;202412 exatamente38. Não fazer padding ou união silenciosa dos schemas.
- D/N1legados202312: hashes exatos do corpo E manifest, URL/método/status/contexto/diagnóstico/schema qualificados. Truncamento não declarado permanece desconhecido; modificar campos ou hash impede aceite. Nenhuma exceção no perfil202412.
- Grade20231211.080,armazenadas11.062,ausentes18;1.385registros e8bindings. Fixtures não recebem essas contagens fixadas.
- Tokens/Decimal/tipo original/pointers preservados; lucro julho–dezembro2023, BRL cru inferido do formatter, vintage não conjunta. Estados/ausências conforme contrato; NI/zero não sintetizados.
- Saídas novas ignoradas emdata/derived/financial-202312-20261004/ e-replay; data/curated/financial-parquet-202312-20261004/ e-replay. Manifest final por último, hash externo na conversão/abertura. Não sobrescrever entradas/snapshots.
- Allowlist36: financial.py, financial-profile-202312.json, financial_parquet.py, as duas CLIsfinanceiras, tests/test_financial_202312.py, README/AGENTS/arquitetura, este plano e ledgerdocs/engineering/financial-snapshot-202312-execution-20261004.md.37só escreve sua nota; integrador único nos shared docs.
- Ruling: o inventário anterior de51hashes inclui financial.py e scripts/admit-financial.py, explicitamente autorizados para mudança nestaIssue. Proteger os49demais arquivos e oscincoinputs do contrato34; registrar SHA anterior/final desses dois códigos como mudança aprovada, sem alegar51imutáveis ou preservar código impedindo a feature.

## Review Focus

1. Fontelegada adulterada coerentemente: hash do manifest e corpo devem coincidir com perfil fechado; recusar alteração de diagnóstico/truncated/contexto/referência mesmo com integridade interna recalculada.
2. Mistura2023/2024: seleção, contrato, perfil, cad32/38, janela e partição devem concordar em admissão/conversão/abertura.
3. Precisão/ausência: preservar9007199254740993.0100,1.10e-18,-0.00,marcadorespercentuais e ausência de entidade/informação; não virarfloat,zero/NI ou evento anual.
4. Alternância de chamadas2023/2024: contexto local, sem mudar defaults/globais ou afetar snapshot202412aceito.
5. Destino/manifest parcial e consultaadulterada: aplicar guardas atuais, hash externo, reconstrução doCSV e materialização da imagem verificada; não aceitar parcial/paths extras.

## Task 1 — Admitir202312 por perfil fechado

**Files:** bank_quality/financial.py; Create bank_quality/financial-profile-202312.json; tests/test_financial_202312.py; scripts/admit-financial.py.

**Interfaces:** manter admit(index_path:Path,output:Path)->dict e defaults públicos202412. Helper interno `_profile_for_selection(selection)` valida seleção fechada e retorna contexto imutável por chamada comprofile/bytes/path/selection/contract/period/cadaster_fields. `_source(role,path,context)` qualifica legado somente quando o perfil202312contém pins revistos. Não parametrizar perfil porCLI/env/entrada não confiável.

- [x] RED: fixture202312independente, cad32 e dois manifestslegados qualificados com pins somente no perfil sintético de teste; testes admit_native_schema_and_window, legacy_mutations_rejected, cross_period_and_cadaster_rejected. Testar lexemas,ausência,lid,perfildefaultinalterado e destino existente.
- [x] Rodar targetedunittest e observar falha real de referência/API ausente.
- [x] GREEN: selecionar perfil por seleção exata; aplicar contexto emURLs/notes/bindings/cadastro/janela/contrato/proveniência e saídas, guardaslegadas exatas. Versionar reader2; preservar estruturas202412e defaultconstantes.
- [x] Rodar novos e existentes testes de admissão; não ampliar contrato para resolver fixture.

## Task 2 — Converter e consultar202312

**Files:** bank_quality/financial_parquet.py; scripts/convert-financial.py; tests/test_financial_202312.py.

**Interfaces:** manter convert_financial(source,destination,*,source_manifest_sha256), validate_snapshot(destination,*,manifest_sha256) e snapshot_connection(...). Contrato202312 `ifdata-financial-parquet-202312-v1`, part `parts/financial-cells-202312.parquet`; validar seleção/contrato antes de escolherinventário, perfil e schema. Complementos/hashschema/Decimal/CSVreconstruction/chaves dos views continuam atuais.

- [x] RED: converter/consultarfixture202312e guardar token/Decimal/32campos/janela/contrato; rejeitar source/snapshot2023rotulado2024mesmocomhashrecalculado; alternar snapshots2023/2024semestadoglobal.
- [x] GREEN: contexto fechado emcommon/metadata/conversão/abertura, headercad32/38 e inventáriopart dinâmico apenas para períodos admitidos. Manter guardas de integridade/semântica/externalaccess.
- [x] Rodar ambos os testes financeiros e suíteoffline/guardas pertinentes; usar falhas para corrigir raiz, sem desabilitar contratos.

## Task 3 — Aceitar lote real, documentar e integrar

**Files:** ledger/README/AGENTS/arquitetura/plano; revisor independente somente leitura de todaunião36+37.

- [x] Construir índice produção202312 com paths relativos ao índice e seleção explícita, sem alterar fontes34; executar duas admissões e conversões/consultas em destinos novos; medir duração/disco e comparar cinco arquivosadmitidos e Parquet/complementos determinísticos. Manifests de execuções têm UTC distintos: comparar campos determinísticos e hashes externos próprios, sem prometer igualdademanifestUTF8.
- [x] Confrontar1.385/11.080/11.062/18,Decimal/tokens/chaves e cad32; verificar49protegidos/cincoinputs e reabrir o snapshot202412aceito como regressão sem escrever nele.
- [x] Atualizar ledger, comandos e estado implementado; leitura/checks/links/diff/allowlist completos e nota37congelada. Self-review: contrato→Task1/2/3, sem gapconhecido ou nova camada.
- [ ] Commit conjunto revisável, revisão independente doheadexato, corrigir P1/P2comregressão, publicarPR/checks/integração/pósCI e sincronizar main. Atualizar Issues36/37/parent16/mapa2com estados verificados e frentes prontas; Project3comZec.

O goal segue depois destas fatias até a rota aprovada, sem declarar basehistórica/amostra/método concluídos com o snapshot202312.

## Ajuste técnico durante execução

Binding de arrays Python em lotes: 134,000 s e131,313 s; ensaio CSV tipado0,406 s de escrita com part byte idêntico. Reavaliada a escrita com documentação oficial DuckDB via Context7, schema explícito, force_not_null textual, cast Decimal exato, parallel=false, ordem preservada e temporário próprio. Adapter3, teste de aspas/vírgulas/Unicode/multilinha/vazios precedente e149 testes PASS. Destinos adicionais privados novos -bulk/-bulk-replay autorizados na Issue antes da execução: conversões completas1,344 s/1,109 s, part e quatro complementos iguais ao baseline. Sem RSS/capacidade integral medida. Sem alterar semântica/dependências/camada; detalhes e hashes no ledger36.

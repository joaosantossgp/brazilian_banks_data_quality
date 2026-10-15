# Plano de ampliação do motor ao universo IF.data

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reutilizar o motor 127 para comparar sistema completo, amostra fixa das 24 e restante, com agregados e segmentações por perspectiva.

**Architecture:** Separar população/marcação da matemática existente. Calcular por unidade nativa uma vez, processar em lotes e produzir recortes como consultas/reduções do mesmo conjunto. Preservar API, perfil e pacotes da amostra anterior.

**Tech Stack:** Python local, DuckDB instalado, Parquet/CSV/JSON textual, Fraction/Decimal; nenhuma dependência nova.

**Spec:** [Contrato do universo](../specs/2026-10-14-ifdata-universe-analysis-design.md), [Issue 130](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/130).

## Estado e restrições globais

**Execução autorizada em 14/10/2026:** Goal ativo e branch `codex/ifdata-universe-analysis-20261014`, base `d33d4fd762bf11dcef2b8746e99235956f3c7fb0`, após integração do planejamento PR131 e CI pós-merge bem-sucedido. A Issue130 confirma os doze paths vigentes abaixo, incluindo o ajuste técnico da fatia2. Fatias0/1 revisadas e concluídas; fatia2 em implementação. Estados iniciais de planejamento neste documento são checkpoints históricos. Priorizar regras, comparação e replay em código versionado, conforme requisito de João incorporado à spec; os scripts privados de diagnóstico não serão o mecanismo único de reprodução.

Planejamento em 14/10/2026, base `3c983b0fbabd3cbe03ecbd3c5f5f98b7c4a41d9b`. Nenhum novo cálculo/código implementado por este plano. João aprovou universo completo incluindo a amostra, financeiro principal e prudencial/individual separados. Fórmulas, núcleo 2010–2024, precisão e ausência seguem a spec 127. Sem coleta financeira nova, alterações globais, índice/ranking ou pesquisa bibliográfica integral repetida.

Root é executor/integrador; cada fatia tem reviewer independente somente leitura. Achado material bloqueia ampliação até correção/revalidação. Execução futura registra branch/base, pins, allowlist e destinos antes de escrever. A seleção técnica dos lotes não muda a população acadêmica. Não afirmar prontidão de bindings individuais ou abertura só pela existência do arquivo.

## Inventário e impacto arquitetural

Preparação atual: criar esta spec/plano; atualizar somente decisão vigente na nota metodológica e acrescentar guia didático ao inventário 113. Quatro paths públicos, sem código ou pasta nova.

Allowlist proposta da execução, a reconfirmar no contrato da Issue 130 antes da escrita:

- Criar `bank_quality/ifdata_population.py` e `tests/test_ifdata_population.py`: população e pertencimento temporal, responsabilidade adjacente aos leitores.
- Modificar `bank_quality/ifdata_analysis.py`, `scripts/analyze-ifdata.py`, `tests/test_ifdata_analysis.py`: novo build explícito, processamento limitado e saídas próprias, mantendo o legado.
- Criar `bank_quality/ifdata_universe_analysis.py`: orquestração do contrato130, autenticação/admissão/I/O/verificação/comparação; reutiliza matemática127 via wrappers lazy no módulo legado. Ajuste técnico justificado e adicionado à Issue antes da criação, sem nova camada/dependência; allowlist total de doze paths.
- Criar `bank_quality/ifdata-analysis-universe-profile-2010-2024.json`: bindings liberados e abertura do universo, sem modificar o perfil 127.
- Atualizar `docs/architecture.md`, spec/plano e nota metodológica; criar `docs/engineering/ifdata-universe-analysis-20261014.md` como ledger de execução.

Destinos planejados novos e ignorados: `data/curated/ifdata-population-20261014-run1/` e `-replay/`, `data/curated/ifdata-universe-opening-200912-20261014-run1/` e `-replay/` quando houver bytes, `data/curated/ifdata-universe-analysis-20261014-run1/` e `-replay/`. Se já existirem ao executar, escolher sufixo novo e registrar. Preparação: `.scratch/ifdata-universe-plan-20261014/`. Sem raiz/camada/dependência nova; arquitetura registra os novos módulos/perfil na mesma fatia de implementação.

Protegidos: perfil e saídas 127, fontes/manifests aceitos, leitores/piloto, benchmark untracked, Word/PDF, README/AGENTS/GLOSSARY/REFERENCES, CI/segurança/credenciais/runtime/Project /3. Não corrigir o teste legado de alias Windows nesta ampliação.

## Fatia 0 — preflight e contratos finitos

**Owner/paths:** Root, spec/plano/ledger/arquitetura; leitura de fontes aceitas. **Dependências:** #111/#113/#125/#127 integradas, plano revisado. **Saída:** inventário autenticado, definição executável da população e matriz de admissibilidade por perspectiva.

- [x] Conferir Issue real, base atual, quatro inputs de valores/cadastro/catálogo/amostra e seus hashes; registrar arquivo/contrato, cobertura temporal e chaves distintas por perspectiva. Ler somente snapshots existentes.
- [x] Identificar unidades, nulos e eventuais linhas agregadas com prova nativa; registrar limites de certificação de cada total. Não filtrar Situacao por padrão. Co-presença prudencial não libera exclusão automática de membros nem total certificado livre de sobreposição.
- [x] Confrontar os contextos da perspectiva individual com catálogo/fonte; liberar só os comprovados, mantendo as métricas prudenciais em capital e estados desconhecidos explícitos.
- [x] Conferir abertura 200912 já capturada para financeiro e individual, sem estender a lista liberada 127. Importação/replay em destino novo somente se fonte e continuidade técnica de unidade/contexto forem comprovadas.
- [x] Registrar medição inicial de headroom e orçamento de512MiB/uma thread para queries de preflight; medir novamente antes de ampliar escala.
- [x] Revisão independente focal de população, bindings, abertura, organização e allowlist; correção de pertencimento e re-review concluídos. Ausência de dado gera lacuna nominal, não coleta implícita nem certificação de cobertura. Implementação, importação e cálculos mantêm gates próprios.

## Fatia 1 — população e três recortes

**Paths:** novo módulo/teste de população; ledger/arquitetura. **Consome:** pares root/hash dos inputs. **Produz:** `build_population(config, output)` e `open_population(output, expected_manifest_sha256)`, tabelas unit_periods/membership_links com schema da spec. **Dependência:** fatia 0 revisada.

- [x] Escrever RED para identidade `(dataset, TipoInstituicao, CodInst, period)`, duplicata, fonte adulterada, código nulo e agregado nativo não liberado.
- [x] Escrever o caso abaixo como teste de pertencimento, sem fabricar CNPJ de instituição não listada:

```python
# Fixture: duas companhias mapeiam para A; B não pertence à seleção;
# C tem vínculo de perspectiva indeterminado. Cada unidade entra uma vez.
unit_rows = [
    {"unit_id": "A", "membership": "sample", "company_id": "issuer-1"},
    {"unit_id": "A", "membership": "sample", "company_id": "issuer-2"},
    {"unit_id": "B", "membership": "remaining", "company_id": None},
    {"unit_id": "C", "membership": "unknown", "company_id": None},
]
cohorts = partition_membership(unit_rows)
total_units = cohorts["total"]
sample_units = cohorts["sample"]
remaining_units = cohorts["remaining"]
unknown_membership_units = cohorts["unknown"]
assert len(total_units) == 3
assert sample_units == {"A"}
assert remaining_units == {"B"}
assert unknown_membership_units == {"C"}
assert not (sample_units & remaining_units)
assert total_units == sample_units | remaining_units | unknown_membership_units
```

- [x] Testar vínculo prudencial muitos-financeiros/uma-unidade, vínculo individual comprovado versus código coincidente, ausência de um emissor da amostra no trimestre e classificação histórica null/conflitante.
- [x] Implementar autenticação, seleção e tabelas sem restringir universo aos códigos da amostra; manifest por último e output exclusivo. Não atribuir vínculo atual ao passado.
- [x] GREEN focal, replay da população e revisão independente de chaves/pertencimento/cobertura antes do motor.

Run focal planejado, cwd na branch de execução, usando Python do Primary:

```powershell
& 'C:/Users/JoãoPereira/Documents/Projects/brazilian_banks_data_quality/.venv/Scripts/python.exe' -B -m unittest discover -s tests -p test_ifdata_population.py -v
```

## Fatia 2 — reaproveitar matemática e limitar memória

**Paths:** módulo adjacente `ifdata_universe_analysis.py`, wrappers no módulo/testes de análise existentes, CLI, novo perfil; ledger/arquitetura. **Consome:** população autenticada, contextos liberados e dependências temporais. **Produz:** `build_universe_analysis(config, output)` e subcomando `build-universe`; antigo build/verify/query preservado. **Dependência:** fatia 1 e liberações da fatia 0 revisadas. A nova fronteira evita misturar orquestração130 com matemática/contrato127; revisão confere ausência de cópia de fórmulas e preservação dos consumidores legados.

- [x] RED para rejeição de hash/perfil arbitrário, perspectiva errada, abertura não liberada, escrita em destino aceito e configuração legada que deve continuar válida.
- [x] Testar ausência sem reduzir população esperada, zero de denominador, reversão, definição de lucro incompatível, unidade sucessora e estoque de abertura faltante.
- [x] Reutilizar quarter_flow/flow_12_months/mean_stock/evaluate_metric; ampliar somente despacho de inputs e seleção finita de perfil. Não duplicar fórmulas ou forçar oito métricas financeiras no prudencial.
- [x] Processar uma janela e lotes de unidades; persistir componentes/resultados em ordem determinística, com frações exatas. Testar que dados lidos do lote anterior não vazam para o seguinte.
- [ ] Comparar todas as linhas sobrepostas à amostra 127 sob os mesmos pins/perímetros, incluindo estados e dependências, sem arredondamento para obter igualdade.
- [x] Rodar lote delimitado com conglomerado, instituição fora da amostra, cooperativa e não bancária quando presentes nas fontes; medir memória/tempo e verificar todas as representações.
- [x] GREEN focal e revisão independente econômica/contábil antes de ampliar agregação.

Fatia2 aceita no commit `49eb70dc10d15908ca703502ae25c5db21274f8e`, após correção e re-review dos quatro achados do verificador/comparador; detalhes e pins no ledger. Os três recortes reais têm814resultados comuns exatamente iguais, incluindo derivações trimestrais e compatibilidade. A comparação de todas as linhas dos60trimestres continua no gate da fatia4; o item integral acima permanece aberto. Fatia3 em implementação, sem execução completa declarada.

## Fatia 3 — agregados, segmentos e comparações

**Paths:** módulo/testes/CLI, ledger. **Consome:** resultados por unidade e pertencimento. **Produz:** `aggregate_unit_results(rows)` e tabelas aggregates/distributions/segment_coverage/cohort_comparisons. **Dependência:** fatia 2 revisada.

- [x] Escrever RED com A = 1/100 e B = 18/900: agregado total 19/1000, amostra A = 1/100, restante B = 18/900; média simples 0,015 não é o total 0,019.
- [x] Testar reconciliação por N/D com pertencimento desconhecido, métricas sem unidades elegíveis e denominadores assinados; não somar razões, medianas ou quartis.
- [x] Testar cada eixo Tcb/Td/Tc/Sr/Atividade/SegmentoTb com categoria histórica, null, sem cadastro e conflito; Situacao diagnóstico e Uf/Municipio apenas sede.
- [x] Implementar recortes a partir do mesmo resultado unitário, sem recalcular ou duplicar unidade por companhia. Total inclui a amostra; comparar dentro de cada perspectiva e categoria compatível.
- [x] Conferir equivalência com agregados/segmentos 127 na interseção idêntica e teste de lote: numeradores, denominadores, quantis e payloads finais iguais para tamanho de lote 1 e outro tamanho medido.
- [ ] Revisão independente com fixture própria, contraprovas de dupla contagem e conferência de cobertura econômica. Não promover S1, top-N ou percentuais a regra de exclusão.

## Fatia 4 — execução completa e entrega

**Paths:** ledger/spec/plano/metodologia/arquitetura conforme resultado, sem ampliar código sem correção causal. **Dependência:** fatias anteriores aceitas e inputs/destinos/pins confirmados.

- [ ] Capturar pins pré-execução e congelar código/perfil; executar 60 trimestres por perspectiva disponível, com horizontes válidos e limites temporais próprios.
- [ ] Publicar tabelas de contagens/nomes/motivos, cobertura/participação da amostra e reconciliação total/amostra/restante/desconhecido. Não certificar universo SFN exaustivo pelo nome do arquivo.
- [ ] Auditar independentemente componentes, casos por dimensão/perspectiva, grandes ausências, agregado/quantis e casos de classificação/vínculo desconhecido.
- [ ] Replay em destino novo, conteúdo determinístico idêntico com UTC próprio; preservar originais e registrar recursos/contagens reais.
- [ ] Testes focais/regressões pertinentes; suíte inteira no marco integração/CI. Preservar falhas e limitações da plataforma; não somar probes para produzir PASS global.
- [ ] Conferir allowlist/diff/links, revisão independente da composição e SHA; PR anexada, checks do head, integração, CI pós-merge e ancestralidade.
- [ ] Atualizar #130 e mapa #2, distinguindo execução local, revisão e integração. Nenhum Goal é criado por este plano; João pode solicitar execução/Goal posteriormente.

## Handoff do planejamento

A #3 foi reconciliada com decisões já implementadas e com a ampliação agora aprovada. Permanecem sem adoção corte de representatividade essencial, faixas acadêmicas próprias, índice/econometria e reconciliação do Word. Esses itens não exigem repetir pesquisa 111 nem bloqueiam recortes nativos/indicadores já aprovados. Executar código somente sob a etapa de implementação da Issue 130, após registrar seu contrato/prontidão e revisão deste plano.

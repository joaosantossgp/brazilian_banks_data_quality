# Piloto de oito indicadores — implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** testar os oito candidatos com saídas SQL/estatísticas/visuais nas duas unidades aprovadas por João, preservando contextos e motivos de não cálculo.
**Architecture:** módulo adjacente aos leitores autenticados existentes gera componentes e resultados em destino novo ignorado. Mesma tabela alimenta CSV/Parquet, estatística e painel HTML local; sem servidor ou dependência adicional.
**Tech Stack:** Python 3.12, DuckDB existente, Decimal, HTML/SVG/JavaScript nativos.
**Spec:** contrato aprovado no diálogo e [Issue88](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/88), proposta [14](../engineering/academic-indicators-components-20261004.md).

## Restrições e ownership

Base13941954917f205fcc1458f0e3e3fc3627d286a2, branchcodex/indicator-pilot. Allowlist exata naIssue88: módulo, CLI, teste, este plano, nota única de pesquisa/evidência, README e arquitetura. Root escreve código/integra; pesquisador escreve somente a nota de engenharia; revisores somente leitura. Fonte bruta e Parquet aceitos imutáveis. Nada de coleta de valores, board, credenciais, CI/proteções ou dependência nova. População técnica não é amostra elegível de capital aberto. Não somar unidades ou copiar índice prudencial para perímetro financeiro/individual. Decimal para componentes/cálculos; floats somente representação gráfica e estatística aproximada explicitada, nunca sobrescrita de fonte.

## A — conceito demonstrável antes de calcular

- [x] Pesquisador verifica especificação oficial OData, Td, unidade, janela e índices; nota única com fontes/localizadores/limites.
- [x] Root confere tipos/cadastro e códigos em consultas somente leitura, sem transportar números das notas do portal para API.
- [x] Revisor independente confere regras propostas e decisões residuais antes de liberar cálculo.

## B — motor e testes antes dos dados reais

Arquivos: bank_quality/ifdata_indicators.py; tests/test_ifdata_indicators.py. API pretendida: `calculate(numerator, denominator)` para razão Decimal finita/status e `build_pilot(values_root, cadastro, output, periods=None)` para novo destino; detalhes de janelas somente após A. `open_pilot(output)` expõe resultados, componentes, cobertura e estatísticas consultáveis.

- [x] Testes RED: razão precisa, null/zero/negativo, tokens inválidos; duplicatas conflitantes e mesma conta em relatórios diferentes; integridade/novo destino; classificação temporal e separação de perímetros; janela/abertura ausente explícita.
- [x] GREEN mínimo usando leitores autenticados; nunca max/sum para escolher célula duplicada.
- [x] Revisão parcial independente de código/testes/allowlist antes de ampliar.

Exemplo de contrato aritmético: `calculate('1.00','8.0')` deve produzir razão textual `0.125`, preservando os componentes literais; denominador0 produz null com motivo, negativo preservado com flag. Isso não autoriza fórmula, janela ou conversão de escala sem prova.

## C — dados, estatística e exploração visual

Arquivos: mesmo módulo, scripts/pilot-ifdata-indicators.py, teste adjacente; README/arquitetura. Destino novo data/curated/ifdata-indicator-pilot-20261011/.

- [x] Executar primeiro período aprovado; reconstrução independente dos componentes/resultados e revisão antes da expansão histórica.
- [x] Expandir mesma lógica aos períodos aceitos; oito candidatos com status explícito inclusive quando não calculáveis. Preservar variantes/regimes2019/2025, cadastro desconhecido e fontes.
- [x] Gerar tabela longa, larga, componentes/cobertura, estatística por indicador/período/perspectiva/versão, JSON gráfico e painel HTML autossuficiente com filtros, séries, distribuição, dispersão e cobertura. Números de gráfico derivam da mesma tabela, denominadores/população visíveis, sem inferência causal ou exclusão de extremos.
- [ ] Revisão independente de dados reais e inspeção do painel renderizado. Corrigir achados antes da ampliação/entrega.

## D — composição e entrega

- [ ] Conferir diff/allowlist, docs/comandos, hashes fontes, testes pertinentes e revisão final do SHA entregue.
- [ ] Publicar PR no escopo aprovado, conferir CI, integrar, conferir ancestralidade/igualdade e CI pós-merge.
- [ ] Registrar entregas/limitações em88, fronteira2 e escolhas residuais3; não declarar fórmula/amostra acadêmica adotadas.

Comandos focais: `.venv/Scripts/python.exe -B -m unittest tests.test_ifdata_indicators -v`; composição inclui readers/cadastro/catálogo afetados. CLI prevista `scripts/pilot-ifdata-indicators.py build VALUES_ROOT CADASTRO OUTPUT` e `query OUTPUT SQL`; confirmar nomes reais e comandos na entrega. CI existente fornece marco de integração, sem duplicar suíte integral por rotina.

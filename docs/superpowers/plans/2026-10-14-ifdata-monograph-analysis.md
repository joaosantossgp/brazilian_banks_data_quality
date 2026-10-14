# Implementação dos indicadores da monografia — plano de execução

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task, with independent review between slices. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Entregar os dez indicadores aprovados, a cobertura nominal, os agregados e a distribuição reproduzíveis para a amostra fixa de 2024 da Issue 125, no núcleo 2010–2024.

**Architecture:** Motor adjacente no pacote `bank_quality`, com perfil finito de bindings tipados e reutilização dos leitores autenticados existentes. CLI fina, dados novos ignorados, precisão racional e revisão independente por fatia, preservando os contratos do piloto.

**Tech Stack:** Python 3.12+, stdlib (`Decimal`, `Fraction`, `datetime`, `csv`, `json`, `hashlib`), DuckDB já instalado conforme `requirements-duckdb.txt` e `unittest` offline.

**Spec:** [Contrato de cálculo](../specs/2026-10-14-ifdata-monograph-analysis-design.md), da [Issue 127 — Implementar indicadores e cobertura da monografia 2010–2024](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/127). A base de execução será o merge confirmado da Issue 111; o histórico do chat não substitui a spec.

## Restrições globais

- Núcleo 2010–2024; amostra da Issue 125 fixa em 2024, com companhias domiciliadas no Brasil e complementos separados.
- Dez métricas: R1, R2, Q1, Q2, C1, C3, C4, L2, L3 e E2-B. Sem score, ranking ou econometria.
- R1/R2/Q2/E2-B: trimestres efetivos e horizontes de 12 meses; fechamento anual calculado pelos componentes de 12 meses. R1/R2/Q2 usam estoque médio ponderado pelo tempo, incluindo abertura; E2-B não tem estoque médio. Não multiplicar trimestre por quatro.
- Q1/C1/C3/C4/L2/L3: razões de estoques contemporâneos; síntese anual em dezembro, sem média aritmética das razões trimestrais.
- O contrato proposto `native-semester-analysis-v2` da spec delimita a inferência de janelas para os contextos finitos 78213/78215/78216/78217/78218/78219. Exige versão, contexto literal e cadeia de evidência por binding; revisão de domínio nesta Issue precede sua implementação. Não amplia retroativamente o aceite do piloto 88.
- Q2 é a proxy de custo de provisão no escopo publicado. A equivalência exclusiva entre as contas de provisão e a carteira 78191 não foi certificada; essa limitação acompanha os resultados. Não prometer certificação exclusiva de carteira, inadimplência observada ou reprodução certificada do REF.
- Nenhuma nova coleta financeira, dependência, runtime, deploy, mudança de segurança, operação no Project /3 ou edição de artefatos aceitos.
- SHA externo de entrada, contexto completo com null tipado, proveniência e distinção entre ausência e zero. Valores racionais exatos; display com 100 dígitos significativos e `ROUND_HALF_EVEN` explícito.
- Root é o executor e integrador único dos dez paths públicos da Issue 127, após a exceção factual registrada antes da escrita. Sem rename, delete ou nova camada. O arquivo untracked de benchmark preexistente permanece intacto.
- Testes pertinentes e revisão independente de cada fatia antes de ampliar. Revisão final da composição e do SHA entregue, PR, checks, CI pós-merge e ancestralidade continuam obrigatórios.

## Allowlist e responsabilidades

| Path público | Responsabilidade |
|---|---|
| `bank_quality/ifdata_analysis.py` | Motor temporal, cálculo, cobertura, agregação e verificação. |
| `bank_quality/ifdata-analysis-profile-2010-2024.json` | Registro finito de definições, contextos, versões, janelas e sinais. |
| `scripts/analyze-ifdata.py` | CLI fina para build/verify/query. |
| `tests/test_ifdata_analysis.py` | Testes offline causais. |
| `docs/superpowers/specs/2026-10-14-ifdata-monograph-analysis-design.md` | Contrato técnico. |
| `docs/superpowers/plans/2026-10-14-ifdata-monograph-analysis.md` | Plano por fatias. |
| `docs/engineering/ifdata-monograph-analysis-20261014.md` | Ledger de execução, fontes, revisões e limites. |
| `docs/engineering/institution-type-indicator-methodology-20261012.md` | Registro conciso das escolhas humanas no trecho corrente. |
| `docs/architecture.md` | Responsabilidade adjacente do módulo, perfil e destinos; Root integra. |
| `docs/engineering/financial-dimensions-literature-20261014.md` | Exceção factual: corrigir somente as listas disjuntas RWA/IB/ICP e o alcance das categorias da operadora, conforme ajuste da Issue 127. |

Dados novos ignorados usam `data/curated/ifdata-analysis-20261014-run1/`, `data/curated/ifdata-analysis-20261014-replay/` e, se necessária, a abertura offline em `data/curated/ifdata-analysis-opening-200912-20261014/`. A preparação privada usa os destinos `.scratch/` já delimitados na Issue. Não usar `ifdata-odata-financial-20261011` sem manifesto. Inputs aceitos, módulos leitores/piloto, referências da Issue 111 fora da exceção factual acima, arquivos das Issues 108/125 e demais exclusões da Issue 127 ficam preservados.

Para cada fatia, Root registra base/head ou snapshot imutável, inventário e allowlist efetiva, dependências, comandos/saídas, checks não executados, revisor, achados e condição de saída no ledger/Issue. Achado material interrompe a expansão até correção e revalidação. Commits, publicação e integração cabem somente a Root no escopo autorizado; o plano descreve etapas e não confirma sua execução.

## Fatia 0 — desenho e contratos de fonte

**Arquivos:** spec e plano; depois o ledger. Alterar somente o trecho corrente da nota metodológica e a responsabilidade adjacente na arquitetura. Não editar as referências da Issue 111.

**Dependências:** Issue 127 real, decisões da Issue 3, pesquisa 111 e handoff autenticado da amostra 125. Desenho/plano podem avançar enquanto a integração 111 é concluída; produção aguarda essa integração e a revisão do contrato.

- [x] Conferir a Issue 127 real, o merge da Issue 111, o código/pins dos leitores e os artefatos da Issue 125 disponíveis; registrar base/head e allowlist.
- [x] Conferir os dados de 200912 já capturados, a abertura financeira TipoInstituicao=2/Resumo NumeroRelatorio=1 aceita e a possibilidade de importar Ativo NumeroRelatorio=2 do mesmo TipoInstituicao=2 via `import_package` existente para destino novo. Não executar GET.
- [x] Documentar o algoritmo trapezoidal em dias, os trimestres efetivos, os 12 meses, os quantis tipo 2 e os estados de denominadores não positivos. Ligar as escolhas de João às adaptações técnicas próprias, distinguindo-as de valores diários observados.
- [x] Conferir janela, sinal e escopo das rubricas 78213/78215–78219 segundo o contrato proposto `native-semester-analysis-v2`. Registrar a cadeia de evidência e os contextos literais do catálogo autenticado que serão copiados para o perfil na fatia 2. Contextos fora do contrato ou sem prova permanecem não liberados, com motivo explícito.
- [x] Registrar a convenção de custo como oposto do resultado assinado publicado, sem `abs`; receitas/reversões positivas nativas permanecem possíveis. Preservar o limite de escopo publicado da proxy Q2, sem exigir ou prometer equivalência exclusiva de carteira.
- [x] Solicitar revisão independente de desenho, arquitetura, allowlist e conceitos econômicos/contábeis. Corrigir achados antes da fatia 1.

**Saída:** spec/plano revisados, escolhas humanas refletidas na nota metodológica e contrato operacional viável. A pesquisa 111 e a adoção de fórmula não certificam por si cada binding.

## Fatia 1 — motor temporal e aritmética exata

**Arquivos:** criar `bank_quality/ifdata_analysis.py` e `tests/test_ifdata_analysis.py`; atualizar o ledger. Ainda sem leitor, dado ou perfil.

**Interfaces:** `quarter_flow(current: dict, previous: dict | None = None) -> dict`, `flow_12_months(quarters: list[dict], end_period: str) -> dict` e `mean_stock(points: list[dict], start: date, end: date) -> dict`. Cada observação contém `period`, `token`, `unit_key` (dataset, tipo, código), `definition_id`, `scale`, `window_rule`, `binding` literal e `sources`. O perfil atribui grupos de definição e regras; o motor puro não cria equivalência. Retorno comum: status, `value_fraction` com numerador/denominador em texto, value display, inputs, flags e método. Erro de contrato produz estado declarado. Helpers privados validam períodos e convertem `Decimal` finito em `Fraction`.

- [x] Escrever testes antes do código: março = 10, junho = 25, setembro = 7 e dezembro = 18 produzem fluxos trimestrais 10, 15, 7 e 11 e fluxo anual 43. A sequência alternante não soma 60. Junho menos março exige mesma janela compatível, contexto e unidade.
- [x] Escrever caso de 12 meses atravessando semestre/ano e caso de definição de lucro líquido incompatível em 201903. Abertura ou observação ausente não encurta a janela.
- [x] Encadear `quarter_flow` → `flow_12_months`: cada trimestre retorna period, intervalo start/end e identidade/regra herdados; TTM recebe quatro desses resultados e soma value_fraction exata após validar consecutividade e disjunção, jamais value display. Testar frações cuja exibição arredondada difere da soma exata.
- [x] Testar o fechamento de dependências: pedido apenas de 202412 lê também 202312/202403/202406/202409 e os contextos necessários, sem outputs extras. Q2/Q4 exigem Q1/Q3 do semestre; 12 meses exigem quatro trimestres disjuntos e seus acumulados. A exceção 200912 admite somente estoques de abertura autenticados, nunca fluxos de 2009. TTM em 201003/201006/201009 retorna `insufficient_history`; 201012 pode usar os quatro fluxos de 2010 e os cinco estoques desde 200912.
- [x] Testar o predicado auditável de compatibilidade: identificador nativo, dataset/tipo/perímetro, escala R$, papel stock/flow, regra temporal e grupo de definição autorizado. Mudança de descrição exige grupo/prova explícitos; quebra de lucro em 201903 não tem ponte. Mudança de código não recebe continuidade por nome nem saldo de sucessor. Registrar chaves, contextos, períodos, prova, versão e resultado do predicado; mudança anual de controle permanece flag separado.
- [x] Escrever média manual dos estoques 100/200/200 em 31/12, 31/03 e 30/06: `(150 × 90 + 200 × 91) / 181`; repetir ano bissexto com 91/91 dias e conferir intervalos de 91/92 dias. Trimestre de 0 a 300 tem média 150; abertura ausente permanece ausente.
- [x] Escrever regressões para token de 40 dígitos e escala longa, zero, negativos, NaN, vazio, null, datas duplicadas/desordenadas, período fora de 2010–2024 e divergência de perímetro/escala/contexto.
- [x] Rodar `& 'C:/Users/JoãoPereira/Documents/Projects/brazilian_banks_data_quality/.venv/Scripts/python.exe' -B -m unittest discover -s tests -p test_ifdata_analysis.py -v` em PowerShell com cwd no managed worktree. Registrar o RED esperado antes da implementação; a `.venv` pertence ao Primary e não existe relativamente ao managed.
- [x] Implementar as funções mínimas com `Fraction`/`Decimal`, sem arredondamento intermediário, retendo metadados de entrada e display explícito com 100 dígitos. Repetir os testes e registrar o GREEN.
- [x] Congelar snapshot/diff/hashes e solicitar revisão independente da fatia 1. Corrigir e revalidar o recorte afetado. Root só inclui em commit os arquivos revisados da allowlist.

**Saída:** mecanismo temporal e precisão aprovados, ainda sem claim de indicadores reais.

## Fatia 2 — bindings, inputs autenticados e cálculos

**Arquivos:** ampliar módulo/teste; criar perfil JSON instalado e CLI; atualizar o ledger. A importação opcional da abertura usa CLI existente e destino novo ignorado, sem editar o importer.

**Dependências:** fatias 0/1 revisadas, integração da Issue 111 confirmada e inputs autenticados disponíveis.

**Interfaces:** `evaluate_metric(metric: str, inputs: dict, horizon: str) -> dict` e `build_analysis(config: dict, output: Path) -> dict`. Config contém pares root/`expected_manifest_sha256` para amostra, catálogo, cadastro, financeiro, capital e abertura, lista única de períodos e perfil instalado. Resultados longos contêm métrica, unidade, companhias, janela, status, componentes, numerador/denominador exatos, valor/flags e proveniência.

- [x] Escrever testes RED para hashes adulterados, arquivos faltantes/extra, path traversal, duplicatas, divergência de schema/contrato, `Grupo = null` distinto de vazio e duas definições com o mesmo nome. Não executar CSV, expressões COSIF ou `reproduce.py`.
- [x] Reusar `open_dataset`, `open_cadastro`, `query_catalog` e a coalescência literal da Issue 123. Testar fonte idêntica com localizadores distintos e saldo igual em fontes/contextos diferentes, que continua ambíguo.
- [x] Extrair o perfil finito literalmente do catálogo autenticado; registrar versão, períodos, janela, sinal e prova de cada binding. Selecionar conta/código não homologa metadata. Gate de liberação: reviewer confere por contexto/época a cadeia de fonte e composição 7/8 do contrato `native-semester-analysis-v2`, versões e rupturas, e registra uma lista finita de bindings liberados. O perfil só marca verified nessa lista; fora dela permanece unverified_window. Não somar variantes de capital sobrepostas.
- [x] Fixar Q2 como `−x13` para todo sinal finito após liberar o contrato: saldo positivo da fonte resulta custo negativo/reversão, sem abs ou gate que exija fonte negativa. Manter a limitação de escopo publicado e de população exclusiva não certificada, sem exigir prova impossível de equivalência REF para calcular a proxy própria aprovada.
- [x] Testar independentemente as dez fórmulas: R1/R2 com lucro e AT/PL médios; Q1 com crédito bruto, crédito líquido e provisão assinada; Q2 com reversões e limite de escopo publicado; E2-B com serviços/tarifas disjuntos e renda antes da provisão; C1/C3/C4 nos perímetros próprios; L2 com depósitos à vista e L3 com crédito bruto/depósitos totais. Denominador zero/negativo, custos positivos e reversões conservam flags, sem `abs`.
- [x] Conferir os resíduos nativos de `RIF 78208 + DIF 78214` versus `RBIF 78215` como diagnóstico. Usar o agregado publicado; não reparar saldo, impor identidade estrita ou introduzir tolerância silenciosa. O token defeituoso de 78219 permanece expressão inerte.
- [x] Importar Ativo NumeroRelatorio=2/TipoInstituicao=2 de abertura 200912 somente após autenticar a fonte e revisar a seleção. Verificar manifest/hash e replay em destino novo. Vincular unidade/cadastro ao mesmo perímetro; não trocar 78191 por 78183.
- [x] Conferir contexto literal e cadastro de 200912 e 201003 antes de admitir os estoques de abertura no mesmo grupo de definição. Testar a recusa de fluxos 2009 e saldos 2025 e a ausência de fallback por nome/código sucessor.
- [x] Implementar entradas e cálculos sob os contratos revisados. Selecionar contas/unidades por queries parametrizadas após autenticação e medir memória. Escrever outputs determinísticos, com manifest por último e output novo exclusivo.
- [x] Executar lote pequeno com 2010, ruptura de 2019 e 2024. Auditar pelo menos um caso manual por dimensão, todos os estados e as fontes. Registrar diferenças nativas por arredondamento como diagnósticos medidos.
- [x] Solicitar revisão independente de código, dados, conceitos e allowlist. Resolver achados e revalidar antes de ampliar para agregados.

**Saída:** indicadores reais do recorte pequeno, com provas e estados, preservando inputs. Binding ainda não verificado é lacuna nominal explícita; não reduz silenciosamente o aceite.

## Fatia 3 — cobertura nominal, agregados e distribuição

**Ajuste técnico após o lote delimitado:** a revisão encontrou herança indevida da cobertura conjunta principal no bloco complementar; corrigir e testar a separação explícita por bloco. Os 180 complementos da amostra 125 conservam adoção somente observacional, inclusive quando há caminho documental de controle: preservar evidência e disponibilidade própria anual, sem atribuição quantitativa ao emissor ou ingresso nos agregados. A cobertura conjunta principal distingue seis métricas point mais quatro quarter ou quatro TTM, sempre como diagnóstico.

O lote de doze referências consumiu pico de 2,26 GiB, enquanto a disponibilidade observada da máquina era cerca de 2,3 GiB. Antes da expansão, substituir a materialização integral da escrita/verificação por processamento por linhas/lotes, dentro dos mesmos paths, sem nova dependência. Preservar inventário, hashes, esquema, contagens, duplicatas, precisão, null/vazio e equivalência entre representações, incluindo leitura dos pacotes stage2. Testes causais e revisão focal precedem novo lote/replay; não alterar outros processos ou configurações globais.

**Arquivos:** módulo, teste, CLI e ledger, dentro dos mesmos paths.

**Dependência:** fatia 2 revisada, incluindo o lote delimitado e a conferência econômico-contábil.

**Interfaces:** `aggregate_results(rows: list[dict]) -> dict` e `verify_analysis(output: Path, expected_manifest_sha256: str) -> dict`. Cobertura parte do mapa esperado, não das linhas calculadas. Query da CLI permite somente SELECT sobre pacote verificado.

- [ ] Escrever RED: duas companhias ligadas ao mesmo conglomerado contam duas companhias e uma unidade no agregado econômico. Principal/complemento e financeiro/prudencial permanecem separados. Holding/subsidiária conflitante conserva estado, sem rateio.
- [ ] Escrever RED: duas unidades financeiras distintas ligadas à mesma unidade prudencial produzem duas relações documentais e uma contribuição prudencial no agregado C3/C4. Deduplicar pela chave nativa da perspectiva de cada métrica, não pela unidade financeira de origem; conservar todas as companhias vinculadas.
- [ ] Escrever RED: unidades A, com AT 100 e numerador 1, e B, com AT 900 e numerador 18, dão agregado 1,9% e mediana 1,5%. Faltando B, mostrar 10% do AT conhecido compatível e a ausência nominal de B; AT null não vira peso zero. Numerador/denominador usam a mesma interseção.
- [ ] Escrever RED para PL/receita negativa e denominador total zero. Companhias permanecem; flags explicam perda da interpretação de pesos convexos. Q2 e R1 ponderam pelo denominador próprio, sem aplicar AT indiscriminadamente.
- [ ] Escrever RED para quantis tipo 2 manuais com n = 1/2/4/5/20 e empates, quartis/IQR sem rótulo de qualidade, Sr null antes de 2017, atividade distinta de setor do tomador, categorias conflitantes e não aplicável somente com prova.
- [ ] Escrever RED distinguindo calculabilidade e aplicabilidade: atividade desconhecida permite valor diagnóstico, mas não ingresso no agregado/distribuição principal. Zero ou ausência não provam não aplicável. A companhia permanece no universo; zero unidades com aplicabilidade comprovada produz `no_eligible_units`. Testar regras/localizadores de atividade/período, sem inferir o mix do conglomerado pelo setor da holding.
- [ ] Implementar `company_coverage`, `aggregates`, `distributions` e `segment_coverage` com listas nominais, estados, motivos e ativos desconhecidos. Cobertura conjunta é diagnóstico, sem exclusão amostral.
- [ ] Separar na cobertura aplicabilidade desconhecida, valor diagnóstico disponível e casos admitidos ao agregado. Conferir R1/R2/C1 na unidade financeira com demonstrações próprias; Q1/Q2/L2/L3/E2-B pela atividade/composição da ficha; C3/C4 pelo vínculo e perímetro prudencial pertinente.
- [ ] Testar adulterações em verify, saída parcial e query somente SELECT. Comparar replay do lote pequeno sem o UTC de execução; ordenar arquivos/tabelas e eliminar nondeterminismo SQL.
- [ ] Solicitar revisão independente com fixture econômica própria e contraprovas; corrigir antes do lote completo.

**Saída:** agregado e heterogeneidade com cobertura da base visível, sem duplicar ou ocultar companhias.

## Fatia 4 — execução, replay e entrega

**Arquivos:** atualizar ledger/spec/plano/metodologia/arquitetura ao resultado, dentro da allowlist. Código/perfil/testes mudam somente por correção causal.

**Dependência:** fatias anteriores revisadas; destinos novos, pins e base de execução confirmados.

- [ ] Capturar pins pré-execução e definir `data/curated/ifdata-analysis-20261014-run1/` e config JSON privado explícito. Executar build para 60 trimestres; R1/R2/Q2/E2-B também têm 12 meses onde o horizonte for válido, com 15 fechamentos anuais. Q1/C1/C3/C4/L2/L3 têm sínteses de estoque em dezembro. Registrar UTC, código, perfil, memória e contagens.
- [ ] Auditar as vinte unidades de 2024 versus a lista da Issue 125, sem projetar a contagem para o histórico. Conferir BR Partners em 2010–2012, BRB em 202209 e capital principal de DM como estados esperados a investigar; não criar assertions que forcem a fonte.
- [ ] Fazer conferência econômica independente de amostra de valores de cada dimensão, janelas, resets, sinais, agregados, segmentos, denominadores e companhias grandes ausentes. A validação não se limita a executar o script do autor.
- [ ] Investigar nominalmente os casos relevantes de aplicabilidade ainda desconhecida antes de encerrar; documentar evidência, diagnóstico e motivo de não admissão ao agregado principal, sem retirar companhias do universo.
- [ ] Executar replay em destino novo separado: tabelas determinísticas idênticas e UTC próprio no manifest; comparar conteúdo semântico completo. Conferir igualdade dos hashes protegidos pré/pós.
- [ ] Executar testes novos e regressões do piloto/leitores afetados; rodar suíte inteira no marco de integração/CI. Não produzir PASS global pela junção de reexecuções isoladas. Registrar falhas e limites preservando cada tentativa.
- [ ] Conferir diff, links e allowlist; concluir revisão independente da composição e do SHA final. Root publica a PR correspondente, anexa no app, confere checks do head, integração em main, CI pós-merge e ancestralidade.
- [ ] Atualizar a Issue 127 e o mapa da Issue 2 com resultado, links, limites, fronteira de paralelismo e ownership. Encerrar Issue 127 e Goal somente quando pesquisa, plano, implementação, execução, replay e entrega estiverem confirmados; não reportar contador de tokens sem budget.

**Saída:** resultado local, revisão e publicação/integração distinguidos e documentados, com lacunas nominais e limites preservados. O encerramento exige evidência final do conjunto entregue.

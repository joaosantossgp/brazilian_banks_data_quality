# Entrada para a análise da monografia

**Seleção acadêmica D1/D2 — 20/10/2026:** ler a [matriz operacional aprovada](monograph-operational-matrix-20261020.md) para medidas, unidades, prioridades, janelas, apresentação monetária, subperíodos, CODACE e complemento das abertas. Ela sucede propostas anteriores de seleção editorial; esta entrada mantém a responsabilidade pela descoberta/autenticação dos dados. D3–D5 permanecem abertas nas Issues #2/#3. O roteiro não dispensa conferir a base vigente e seus hashes antes de consultar valores.

Contrato: [Pesquisa #198](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/198), articulada à [Entrega #193](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/193). Plano operacional: [fatias e verificações](../superpowers/plans/2026-10-19-analysis-ready-explorer.md). Este documento propõe a sequência de análise; o fechamento acadêmico final cabe a João/orientador. A base é o universo observado inteiro, com seleção vinculada, restante e vínculo desconhecido separados.

## Onde estão os dados e qual versão usar

Não há um único banco de dados servidor por trás do explorador. A base local é organizada em pacotes imutáveis, consultados porDuckDB, e oHTML é uma projeção autocontida. A entrada operacional única para esta análise é este documento: não escolher a última pasta por data, nem tratar umJSON de interface como fonte contábil.

```text
IF.data bruto preservado / macro bruto
    → importações nativas Parquet, com tokens e proveniência
    → resultados dos indicadores e composição aceita de27métricas
        → joint_cells: filtros e agregados do painel Indicadores
        → unit_periods: cadastro datado, vínculos e categorias
    → Ativo/Passivo nativos + crédito SCR + cadastro datado
        → JSON de contextos conjuntos para Balanço/Crédito
    → quarterly.parquet macro, em pacote separado
        → exportador + template → HTML privado + recibo
```

| Responsabilidade | Local no checkout principal | Leitura correta |
|---|---|---|
| Originais IF.data | `data/raw/ifdata-odata-20261011/` | Respostas originais; não sobrescrever/reclassificar tokens. Manifesto bruto autentica captura, não comparabilidade econômica. |
| Ativo/Passivo/Resumo/DRE importados | `data/curated/ifdata-odata-20261011/financial/` | Relatórios1–4 nativos; o exploradorBalanço seleciona2/3. Fluxo DRE nativo não é automaticamente trimestre efetivo. Manifest `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095`. |
| Indicadores e recortes de análise | Composição27f374 indicada abaixo | Resultados, coberturas e células observadas; não recalcular fórmulas para abrir o explorador. |
| Cadastro e vínculos usados na interface | `unit_periods.parquet` da mesma composição | Unidade/código/período exatos; categorias e Sr derivado datados. CVM/B3 fornecem metadados/vínculos, não os saldos financeiros. |
| Crédito SCR | Pacotes `core/` e `early/` da196 indicados abaixo | Oito relatórios7–14, com contexto literal. Separado do crédito contábil dos indicadores. |
| Macro | Pacote `macro-context-20261018-run2/` indicado abaixo | `quarterly.parquet`,25séries/1.476observações; períodos, unidades e janelas próprios. |
| Auditoria e retomada | `data/curated/indicator-economic-audit-20261019-full2/` | `handoff.json` fixa evidência econômica. `analysis-ready-handoff.json` fixa a entrega v3; `analysis-ready-handoff-v4.json` fixa a candidata4 com os seis recortes eMacro autônoma. O recibo4é a entrada corrente da candidata; não substitui silenciosamente o handoff3 ou o ponteiro aceito. |
| Código de apresentação | `scripts/export-ifdata-explorer.py`, `scripts/ifdata-explorer-contexts.py`, `scripts/ifdata-explorer-template.html` | Redução/filtragem de valores persistidos, sem indicador novo. Código é versionado noGit; dados privados não são distribuídos pelo clone. |
| HTML eJSON de apresentação | Diretório privado de visualizações da tarefa | Cópias de leitura, com recibos e hashes próprios. Arquivo mais novo não significa aceite; a [nota193](tcb-indicators-explorer-20261018.md) distingue a última candidata da versão aceita. |

A composição aceita contém nove tabelas. Seus manifests inventariam caminhos, hashes e quantidades; os valores exatos e estados permanecem no campo `payload` dosParquets.

| Tabela | Linhas neste pin | Granularidade / finalidade |
|---|---:|---|
| `unit_periods` |244.001| Unidade reportante × período × perspectiva; presença, vínculo e classificações datadas. |
| `unit_coverage` |6.005.286| Unidade × indicador × janela × período; resultado/estado, N/D, aplicabilidade e origem. |
| `company_coverage` |214.500| Companhia esperada e seu vínculo/resultado; não multiplicar saldos por companhias que compartilham unidade. |
| `representation_stocks` |244.001| Estoques próprios conhecidos de AT/crédito/PL para representatividade, separados da elegibilidade da razão. |
| `aggregates` |15.600| Razões agregadas por contexto e coorte; somaN/somaD da mesma interseção elegível. |
| `distributions` |15.600| Distribuições institucionais por contexto; mediana/quartis não equivalem à razão agregada. |
| `segment_coverage` |719.860| Cobertura e resultados por eixo/categoria/estado, preservando desconhecidos. |
| `cohort_comparisons` |551.595| Comparações entre coortes e recortes conforme o contrato persistido; não certificam causalidade. |
| `joint_cells` |355.632| Células conjuntas observadas dos seis eixos e coortes disjuntas, usadas para recompor filtrosAND sem inventar cruzamentos. |

**Versões e autoridade:** `current-indicators.json` é a referência corrente aceita no computador. Na abertura desta entrega ele selecionava20métricas/d47; a análise adotou explicitamente27métricas/f374, aceita localmente na192 e pinada abaixo. A promoção controlada e o aceite do explorador são registrados na193. A próxima tarefa deve ler o ponteiro real e autenticar os hashes, sem interpretar o checkpoint histórico20/d47 como seleção eterna. PRpublicada, CIaprovada, dado aceito, artefato visual aceito e integração emmain são estados distintos. Não alterar o pin de uma tarefa já iniciada sem migração explícita.

A próxima tarefa deve: resolver o checkout principal peloGit comum; ler o ponteiro; autenticar a entrada explícita desta análise e as tabelas consumidas; ler a nota193 para o recibo do candidato corrente. Se estiver em outro computador e o pacote privado faltar, parar nesse ponto e obter a cópia autorizada, em vez de reconstruir dados pela idade das pastas. A Release antiga não é promessa de sincronização com27métricas ou crédito196.

## A mesma entrada na próxima tarefa

Descobrir o checkout principal pelo diretório Git comum e autenticar o ponteiro conforme o [comando canônico](local-queries-20261013.md#base-de-indicadores-vigente-entre-tasks). Não escolher pasta por nome/data, não reconstruir a seleção pelo chat e não confundir o HEAD do checkout principal com o do worktree de entrega. Registrar o pin inicial e conferir os hashes das tabelas consumidas.

Nesta tarefa houve migração explícita da entrada de auditoria da composição de20métricas(d47abaixo) para a composição aceita de27métricas(f374). Oponteiro de20foi preservado durante a validação; sua promoção posterior depende do aceite registrado na193. A seleção corrente deve ser verificada no arquivo real. O conjunto fixado aqui permanece identificável por hash, inclusive para tarefas que conservaram pins anteriores. Os caminhos abaixo são relativos ao checkout principal, privados e válidos neste computador; o clone Git não distribui os dados.

| Entrada | Caminho relativo | SHA-256 do manifest |
|---|---|---|
| Indicadores, composição aceita #192 | `data/curated/tcb-composicao-adequacao-20261019-final3-provenance` | `f374150e5d4c515f032fdf3fad3cb27b4e196486cee8d81c19150c39df45981b` |
| Ponteiro anterior, 20 métricas | `data/curated/historical-links32-composition-20261018-run3` | `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60` |
| Macro | `data/curated/macro-context-20261018-run2` | `9920b6ebe130854130ab9ec7e7bfe98410556f22f81b969128be2704be8de118` |
| Crédito, núcleo | `data/curated/ifdata-credit-openings-20261019-full/core` | `b69fbcbe68cc38168403bc60a147dc761c444c507d22021db2e1e573baa255d2` |
| Crédito, abertura inicial | `data/curated/ifdata-credit-openings-20261019-full/early` | `246ec46328821041ae676f601393064c6e1b8eb5324a129ce3552e422862b86d` |

Para abrir **este pin fixado**, mesmo que o ponteiro corrente seja outro:

```powershell
$analysisPrimary = [IO.Path]::GetFullPath((Split-Path -Parent (git rev-parse --path-format=absolute --git-common-dir)))
$analysisPackage = Join-Path $analysisPrimary 'data/curated/tcb-composicao-adequacao-20261019-final3-provenance'
$analysisPin = 'f374150e5d4c515f032fdf3fad3cb27b4e196486cee8d81c19150c39df45981b'
$analysisHash = (Get-FileHash -LiteralPath (Join-Path $analysisPackage 'manifest.json') -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
if ($analysisHash -cne $analysisPin) { throw 'Pin da análise divergente; não consultar' }
$analysisManifest = Get-Content -LiteralPath (Join-Path $analysisPackage 'manifest.json') -Raw | ConvertFrom-Json
if ($analysisManifest.contract -ne 'ifdata-composed-analysis-v1') { throw 'Contrato inesperado' }
# Antes de ler uma tabela, autenticar também seu arquivo.
$analysisEntry = @($analysisManifest.files | Where-Object file -eq 'unit_coverage.parquet')
if ($analysisEntry.Count -ne 1) { throw 'Tabela ausente ou ambígua' }
$analysisTable = Join-Path $analysisPackage $analysisEntry[0].file
if ((Get-FileHash -LiteralPath $analysisTable -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant() -cne $analysisEntry[0].sha256) { throw 'Hash da tabela divergente' }
[pscustomobject]@{ Package=$analysisPackage; ManifestSHA256=$analysisHash; Table=$analysisTable; Selection='pin explícito da198; não altera o ponteiro' }
```

Os manifests de crédito são os da importação; conferir os nomes concretos no [ledger #196](ifdata-credit-openings-temporal-gaps-20261019.md) antes de executar. Não selecionar o CSV piloto do portal como parte desses pacotes. A [auditoria econômica](indicator-economic-plausibility-20261019.md) identifica seu recibo próprio e o explorador #193 documenta o artefato entregue.

## Como pedir a outra tarefa

Pode copiar esta instrução, acrescentando a pergunta de análise desejada:

> Use a base vigente deste projeto, sem nova coleta nem recálculo de indicadores. Leia AGENTS.md e docs/engineering/analysis-start-20261019.md. Resolva o checkout principal pelo diretórioGit comum; leia data/curated/current-indicators.json e autentique o manifest e as tabelas consumidas. Informe o caminho e o SHA-256 fixados, a versão do explorador e os pins de macro, balanço e crédito aplicáveis. Para esta etapa acadêmica, confira a composição de27métricas/f374 e o núcleo2010–2024, no sistema observado inteiro, com vinculadas/restante/vínculo desconhecido separados. Preserve perspectivas, estados de ausência, janelas e limites; não use o HTML como base canônica, não escolha pasta por data e não migre um pin de tarefa em andamento silenciosamente. Então execute: [descrever a análise].

No ponteiro, `package`+`manifest_sha256` identificam os indicadores. `macro_context`, `balance_context` e `credit_context` identificam fontes separadas; `native_contexts` identifica a projeção conjunta deBalanço/Crédito; `explorer` fixaHTML/recibo; `analysis_context` aponta para esta entrada e a auditoria. Cada referência consumida tem autenticação própria: conferir somente o manifest dos indicadores não autentica todas as fontes adicionais. Esses campos são metadados do ponteiro existente, não novos bancos ou uma segunda seleção corrente. Os snapshots dehandoff permanecem evidência datada; o estado operacional atual vem do ponteiro e das Issues reais.

Se o ponteiro ainda selecionar outro pin, relatar a divergência e ler a193: não substituir a seleção automaticamente. Em outro computador, o pacote deve ser restaurado em escopo autorizado antes de configurar a referência; oGit não transfere os dados privados.

## Plano enxuto de análise

1. **Caracterizar o universo e a composição.** Por trimestre e Tcb, apresentar unidades, companhias vinculadas e estoques conhecidos de AT, crédito e PL, incluindo nulos e sinais. A seleção está contida no sistema; companhias que compartilham unidade não multiplicam seus saldos. Tc, Td e Sr explicam estratos e perímetros; SegmentoTb distingue subtipos econômicos. Atividade não volta aos filtros.
2. **Descrever desempenho por famílias.** Apresentar a razão agregada (soma dos numeradores/soma dos denominadores elegíveis), ao lado da mediana e dispersão entre unidades, cobertura institucional e econômica. Começar pelos indicadores comuns R1, R2, C1 e composição de ativos/fontes, depois os específicos da [matriz por Tcb](tcb-indicators-delivery-20261018.md#adequação-oito-famílias-e-cinco-dimensões). E2-W é a medida principal de eficiência de renda selecionada; E2-B e E2-WP são séries distintas. Não montar um agregado misturando fórmulas por Tcb.
3. **Explicar crédito e contexto macro.** Usar as aberturas de crédito para risco, modalidade, atividade do tomador, região e demais contas efetivamente disponíveis, sem confundir SCR com o estoque contábil usado no indicador. Macro contextualiza trajetória, não identifica causalidade. Toda comparação conserva perspectiva, unidade, janela e definição.
4. **Testar robustez descritiva antes de inferir.** Reusar diagnósticos A/B dos 20 anteriores e dos sete novos. Confrontar agregado dinâmico, distribuição institucional, influência de unidades e códigos comuns entre datas; códigos comuns não garantem perímetro constante. Somente depois escolher testes/modelos ligados à pergunta econômica e à dependência temporal. TTM sobreposto não fornece observações trimestrais independentes.

Não há decisão nesta tarefa de índice/pesos, winsorização, exclusão por valor, imputação ou painel balanceado obrigatório. A tabela principal deve preservar o universo dinâmico observado; sensibilidades são apresentadas separadamente.

## Calendário utilizável e lacunas

| Dado/pergunta | Recorte temporal principal | Tratamento |
|---|---|---|
| Estoques financeiros e fluxos trimestrais | 201003–202412, conforme componentes | Ausência de unidade, nulo, zero e incompatibilidade permanecem distintos. Trimestre efetivo não é dezembro tratado como anual. |
| Fluxos TTM | A partir de 201012 quando houver histórico e definição compatíveis | 201003/06/09 sem histórico não recebem zero. R3/TTM em 201903/06/09 conserva incompatibilidade; pontes de R1/R2 não são transplantadas. |
| Capital prudencial C3/C4 | 201503–202412 | Não emendar capital financeiro de 2010–2014. CP ausente não recebe PR. Nulos desde 2018 exigem regime/unidade, não corte global. |
| Sr original | A partir de 201703, com desconhecidos posteriores | SrAnalitico derivado é apresentado separadamente; não é simples porte. Td=I não demonstra independência societária. |
| N4 observado | A partir de 201712 neste pacote | A entrada não prova inexistência anterior da atividade; controlar início e composição. Pré-paga 110560 aparece desde 202006, sob definição própria. |
| Crédito OData | 201409–202412; 201406 tem sete relatórios, sem relatório9 | Nenhum preenchimento pré-2014. O piloto portal201206 é evidência de oferta histórica, não uma série conciliada. Mudança do limiar individual SCR em junho2016 limita comparabilidade de composição. |
| Macro geral | 201003–202412 | Cada série mantém unidade/janela próprias; PIB TTM já dispõe de histórico, sem aplicar warm-up dos indicadores. |
| Mercado de trabalho | 201203–202412 | 2010–2011 ausentes. Renda real conserva a base de preços da captura; não deflacionar novamente por inferência. |

O pacote principal tem 60 trimestres acadêmicos, mas isso não assegura 60 pontos utilizáveis para cada indicador/Tcb. Não excluir toda uma família por uma lacuna localizada: usar calendários por indicador, denominador e categoria, exibidos no explorador. O período complementar2025–2026 fica separado pelo Cosif2025 e fora destas tabelas centrais.

**Janelas que merecem apresentação separada:** ROA/TTM em N2, 201612–201812 e 202209–202403, e N1, 202012–202112, têm perdas relevantes de cobertura de AT conhecido (mínimos documentados de27,63%,34,33% e56,64%, respectivamente). Não usar a razão dos disponíveis como se representasse toda a família. Manter a série com cobertura visível; confrontar trimestre efetivo e janela alternativa compatível, sem preencher fontes faltantes ou impor um limiar acadêmico não adotado. A investigação #196 demonstrou faltas nos componentes nativos de vários casos; não é apenas um filtro que possa ser removido.

## Regras de apresentação e encerramento

- Valores extremos permanecem na base; razão com denominador pequeno ou negativo recebe contexto, e ROE com PL negativo não sustenta ranking simples de rentabilidade. Provisão não é inadimplência, L2 não é LCR, C1 não é adequação regulatória.
- Mudanças de composição: mostrar entradas/saídas e comparação de códigos comuns, registrar aquisições/perímetros conhecidos e manter vínculo desconhecido fora do restante. Vínculo no fechamento não certifica controle durante todo o TTM. Não retroagir a coorte de2024 para toda a história.
- Agregados com denominadores negativos podem ter pesos não convexos; mediana e agregado respondem a perguntas distintas. QL é concentrado e específico: a retirada de uma unidade pode alterar muito o agregado. Preservar análise de influência própria.
- Não somar total e seus componentes, nem perspectivas ou cooperativas centrais e filiadas como se fossem consolidação com eliminações. Clientes/operações por instituição não viram pessoas únicas do sistema.
- Critério para começar a redação: pins reproduzíveis, auditoria de níveis revisada, calendário explícito, cobertura e composição acompanhando os resultados. Lacunas remanescentes ficam explicadas; não exigem inventar medidas nem adiar toda a análise por fontes externas.

O próximo executor deve ler esta entrada, a auditoria econômica e o recibo do explorador antes de calcular estatísticas. Adoções finais e eventuais correções materiais permanecem registradas na Issue3 e nas Issues responsáveis, sem transformar esta proposta em decisão do orientador.

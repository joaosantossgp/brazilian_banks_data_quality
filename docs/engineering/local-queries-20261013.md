# Consultas locais e reprodução IF.data

Guia operacional separado do [README](../../README.md) na [Issue 109](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/109), em 2026-10-13. Comandos e evidências migrados da versão de 2026-10-12, sem mudança das CLIs. Não se afirma nova execução de consultas/replays nesta revisão documental.

## Base de indicadores vigente entre tasks

A referência única neste computador é `data/curated/current-indicators.json` no checkout principal compartilhado. Em um worktree, sua própria pasta `data/` pode estar ausente; descubra o checkout principal pelo diretório Git comum. O ponteiro contém `contract=ifdata-current-indicators-v1`, `package` relativo ao checkout principal, `manifest_sha256`, `validation=accepted_local`, `code_commit` e as referências de publicação. O estado local aceito não implica integração do código na main.

Este comando PowerShell funciona tanto no checkout principal quanto em seus worktrees, sem instalar dependências. Ele confere o caminho, o contrato e o pin antes de apresentar a seleção:

```powershell
$primaryRoot = [IO.Path]::GetFullPath((Split-Path -Parent (git rev-parse --path-format=absolute --git-common-dir)))
$pointer = Join-Path $primaryRoot 'data/curated/current-indicators.json'
$selection = Get-Content -LiteralPath $pointer -Raw -ErrorAction Stop | ConvertFrom-Json
if ($selection.contract -ne 'ifdata-current-indicators-v1' -or $selection.validation -ne 'accepted_local' -or $selection.manifest_sha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'Ponteiro de indicadores inválido ou não aceito' }
$packageRoot = [IO.Path]::GetFullPath((Join-Path $primaryRoot $selection.package))
$curatedRoot = [IO.Path]::GetFullPath((Join-Path $primaryRoot 'data/curated')) + [IO.Path]::DirectorySeparatorChar
if (-not $packageRoot.StartsWith($curatedRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Pacote fora de data/curated' }
$manifest = Join-Path $packageRoot 'manifest.json'
$hash = (Get-FileHash -LiteralPath $manifest -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
if ($hash -cne $selection.manifest_sha256) { throw 'Hash da base diverge do ponteiro; não consultar' }
$packageMetadata = Get-Content -LiteralPath $manifest -Raw -ErrorAction Stop | ConvertFrom-Json
if ($packageMetadata.contract -ne 'ifdata-composed-analysis-v1') { throw 'Contrato de indicadores inesperado' }
[pscustomobject]@{ Package=$packageRoot; ManifestSHA256=$hash; Validation=$selection.validation; CodeCommit=$selection.code_commit }
```

A saída identifica a pasta das tabelas Parquet, consultáveis por DuckDB/Python; `payload` conserva os campos e frações exatas. A verificação acima autentica o manifest, não revalida todos os arquivos ou a metodologia. Ao iniciar uma consulta importante, conferir também os hashes das tabelas consumidas contra o inventário desse manifest, como exigem os leitores autenticados existentes. Registrar o pin inicial na tarefa e mantê-lo mesmo se outra entrega atualizar o ponteiro.

Se o ponteiro não existir em outro computador, os dados não foram configurados ali: não procurar automaticamente uma pasta parecida nem presumir que a Release antiga seja a versão do explorador. Copiar/restaurar o pacote em escopo autorizado, validar e só então configurar sua referência local.

Para publicar uma nova seleção local, o integrador registra primeiro a nova pasta imutável, hash do manifest, evidência de aceite e código/PR de origem. Só depois atualiza o ponteiro, preservando a versão anterior para tarefas já fixadas. Saída em construção, tentativa parcial ou pasta mais recente não é versão vigente. O arquivo privado não entra no Git; estas instruções são versionadas para descoberta por outras tasks.

## Antes de executar

Execute na raiz do checkout que contém os dados e a `.venv` configurada, não na pasta deste documento. O clone distribui código/contratos, não os dados locais. Os exemplos dependem dos artefatos identificados pelos ledgers; consulte as instruções e validações da [Release IF.data](https://github.com/joaosantossgp/brazilian_banks_data_quality/releases/tag/snapshot-ifdata-20261012) quando precisar restaurá-los. A Release é datada, não uma promessa de sincronização com qualquer outra frente.

Consultas/contagens leem conjuntos existentes. `import`, `build`, conversão e replay escrevem saídas: use destinos novos e o contrato da Issue. Comandos de aquisição e inicialização são operações diferentes, com autorização própria. Preserve fontes, hashes e precisão. Python/DuckDB locais seguem [requirements-duckdb.txt](../../requirements-duckdb.txt); este guia não autoriza instalar runtime global ou executar nova coleta.

A rota **OData** abaixo é a base consultável atual descrita nas PRs84/85/87. A rota **portal** no fim mantém contratos/snapshots próprios; identificadores de relatório e perspectiva não são intercambiáveis. Oito candidatos do piloto exploratório não limitam nem definem a seleção final da monografia.

## Consultar a base IF.data

A importação offline de 2026-10-11 disponibiliza **18.228.826 registros** do serviço oficial IfDataValores em Parquet local. Os quatro conjuntos ficam em `data/curated/ifdata-odata-20261011/`:

| Pasta | Conteúdo nativo | Trimestres | Janela | Registros |
|---|---|---:|---|---:|
| `financial` | Tipo 2: Resumo, Ativo, Passivo e DRE | 66 | 201003–202606 | 7.945.863 |
| `individual` | Tipo 3: Resumo, Ativo, Passivo e DRE | 66 | 201003–202606 | 8.679.083 |
| `capital` | Tipo 1: Capital | 46 | 201503–202606 | 1.344.190 |
| `segmentation` | Tipo 1: Segmentação | 38 | 201703–202606 | 259.690 |

Python 3.12 e DuckDB existentes bastam. Para consultar a base já importada:

```powershell
# Inventário por período, tipo e relatório, incluindo saldos ausentes.
.venv/Scripts/python.exe scripts/import-ifdata.py counts data/curated/ifdata-odata-20261011/financial

# Consulta aos campos nativos. Troque financial pela outra pasta desejada.
.venv/Scripts/python.exe scripts/import-ifdata.py query data/curated/ifdata-odata-20261011/financial "SELECT AnoMes, CodInst, NumeroRelatorio, Conta, Grupo, Saldo FROM ifdata WHERE AnoMes = '202606' LIMIT 10"
```

Para reproduzir a conversão financeira a partir do pacote privado em `data/raw/ifdata-odata-20261011/`, escolha **um destino novo**:

```powershell
.venv/Scripts/python.exe scripts/import-ifdata.py import data/raw/ifdata-odata-20261011 data/curated/ifdata-odata-reproducao --periods 201003 201006 201009 201012 --types 2 --reports 1 2 3 4
```

O exemplo reproduz quatro trimestres; omitir `--periods` importa toda a oferta do pacote, inclusive anos fora do alvo. Para os complementos, use tipo 3/relatórios 1–4, tipo 1/relatório 5 ou tipo 1/relatório 6, com a janela da tabela.

`Saldo` conserva o número original em texto, incluindo casas decimais/expoentes; null permanece distinto de zero. `bank_quality.ifdata_odata.saldo_decimal` retorna Decimal Python exato. IDs, Grupo, tipo e relatório permanecem literais. Cada linha conserva arquivo, hash, URL oficial, instante de coleta, contexto e posição de origem. Os tipos são populações próprias e não devem ser somados automaticamente.

O pacote não contém cadastro institucional completo. A consulta usa os códigos nativos, inclusive ausências explícitas; amostra, vínculos e indicadores permanecem em suas Issues. A captura OData tem data própria e não substitui silenciosamente os 11 snapshots antigos, que continuam acessíveis pela CLI anterior. Os registros datados abaixo descrevem essa rota histórica, sem limitar a cobertura OData atual.

Os 428 gzip recebidos passaram na conferência de hashes/tamanhos. Pilotos foram revisados antes da expansão; a conferência integral dos resultados e a integração estão registradas na [PR 84](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/84) e no [plano vigente](../../docs/superpowers/plans/2026-10-05-financial-historical-acquisition-remaining.md). Conversão financeira: 194,844 segundos; os três complementos, em sequência: 236,969 segundos. São medidas desta máquina e pacote. Pacote, Parquet e credenciais ficam fora do GitHub.

## Catálogo temporal de variáveis

O catálogo dos quatro conjuntos está em `data/curated/ifdata-variable-catalog-20261011/`, com duas tabelas SQL e cópias CSV:

- `catalogo_variaveis`: 438 combinações literais de variável/contexto/definição; nome, descrição/composição, código, grupo, períodos observados, extremos, variantes e alertas.
- `cobertura_variaveis`: 11.331 combinações definição/trimestre, com registros, saldos presentes/null, códigos distintos e registros sem código. Reconciliam os 18.228.826 registros da base.

| Conjunto | Definições/contextos | Linhas de cobertura |
|---|---:|---:|
| financial | 196 | 5.140 |
| individual | 193 | 5.080 |
| capital | 37 | 927 |
| segmentation | 12 | 184 |

2010–2024 é a janela principal da monografia; `periodos_2010_2024` e `periodos_2025_2026` permitem separar o complemento. Uma definição literal pode ser observada em muitos trimestres. As 438 linhas não representam 438 séries econômicas harmonizadas.

```powershell
# Procurar lucro líquido e examinar mudanças de composição/código.
.venv/Scripts/python.exe scripts/catalog-ifdata-variables.py query data/curated/ifdata-variable-catalog-20261011 "SELECT Conta, NomeColuna, DescricaoColuna, primeira_referencia, ultima_referencia FROM catalogo_variaveis WHERE dataset='financial' AND NumeroRelatorio='1' AND lower(NomeColuna) LIKE '%lucro%' ORDER BY primeira_referencia"

# Reproduzir em destino novo, usando somente os Parquet já aceitos.
.venv/Scripts/python.exe scripts/catalog-ifdata-variables.py build data/curated/ifdata-odata-20261011 data/curated/ifdata-variable-catalog-reproducao
```

As cópias `catalogo_variaveis.csv` e `cobertura_variaveis.csv` podem ser importadas como CSV UTF-8. `variantes_no_contexto` sinaliza diferentes nomes/descrições no mesmo dataset/tipo/relatório/Conta/Grupo. `codigos_com_mesmo_nome` ajuda a investigar códigos diferentes com rótulo igual. `periodos_sem_registro_entre_extremos` mostra somente lacunas observadas entre primeira e última aparição de cada definição, dentro do eixo disponível do conjunto; não identifica ausência estrutural. `atravessa_2025` sinaliza contexto presente dos dois lados da fronteira2025.

A comparabilidade fica `nao_certificada`: estabilidade literal e cobertura não comprovam unidade, janela de fluxo, mensuração ou perímetro. O catálogo preserva descrições e auxilia a pesquisa dos componentes de indicadores, sem calcular/adotar indicadores ou inventar equivalências. [Fontes, dicionário e exemplos observados](../../docs/engineering/ifdata-variable-catalog-20261011.md).

## Cadastro temporal e vínculos

O cadastro recebido está em `data/curated/ifdata-cadastro-20261011/`: **512.959 registros, 6.517 códigos distintos e 106 trimestres (200003–202606)**. A view `cadastro` preserva os 16 campos nativos e a origem. A view `vinculos` expõe separadamente as relações financeiras e prudenciais declaradas em cada data-base; não define identidade com emissores/holdings ou amostra acadêmica.

```powershell
.venv/Scripts/python.exe scripts/import-ifdata-cadastro.py query data/curated/ifdata-cadastro-20261011 "SELECT CodInst, Data, NomeInstituicao, CodConglomeradoFinanceiro, CodConglomeradoPrudencial FROM cadastro WHERE Data = '202412' LIMIT 10"
```

Para consultar valores com cadastro, informe o conjunto nativo. A view `ifdata_cadastrado` faz `LEFT JOIN` por `CodInst` e `AnoMes = Data`, preservando todas as linhas e sinalizando `cadastro_encontrado`:

```powershell
.venv/Scripts/python.exe scripts/import-ifdata-cadastro.py query data/curated/ifdata-cadastro-20261011 "SELECT AnoMes, CodInst, NomeInstituicao, Conta, Saldo, cadastro_encontrado FROM ifdata_cadastrado WHERE AnoMes = '202412' LIMIT 10" --values data/curated/ifdata-odata-20261011/financial
.venv/Scripts/python.exe scripts/import-ifdata-cadastro.py audit data/curated/ifdata-cadastro-20261011 data/curated/ifdata-odata-20261011
```

A auditoria dos quatro conjuntos preservou **18.228.826 linhas**, com **4.464 sem cadastro no mesmo trimestre**, incluindo 972 com código nulo na fonte. O conjunto individual teve correspondência integral. Os relatórios locais `coverage.csv`, `unmatched.csv`, `declared_links.csv` e `link-audit.json` detalham resultados; ausência permanece explícita. `CnpjInstituicaoLider` recebido tem oito caracteres quando preenchido: não completar para 14 nem assumir identidade jurídica. `DataInicioAtividade=180001` é preservado sem interpretar como início real.

Para reproduzir a importação, use destino novo:

```powershell
.venv/Scripts/python.exe scripts/import-ifdata-cadastro.py build data/raw/ifdata-cadastro-20261011/ifdata_cadastro data/curated/ifdata-cadastro-nova-execucao
```

[Execução, cobertura e limites do cadastro](../../docs/engineering/ifdata-cadastro-20261011.md). Dados continuam locais/ignorados; JSONs são fonte autoritativa para distinguir vazio e nulo.

## Piloto de indicadores consultável

A [Issue 88](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/88) implementa oito candidatos: ROE, ROA, margem líquida, crédito/depósitos, provisão/crédito, PL/ativo, Basileia e capital principal. ROE e ROA têm duas variantes de média: abertura/fechamento e trimestral com pesos iguais, incluindo a abertura. As saídas ficam em `data/curated/ifdata-indicator-pilot-20261011/`.

```powershell
# Consultar valores, componentes e motivos de não cálculo.
.venv/Scripts/python.exe scripts/pilot-ifdata-indicators.py query data/curated/ifdata-indicator-pilot-20261011 "SELECT dataset, unit_class, code, period, indicator, method, numerator, denominator, value, status FROM results WHERE period='202412' AND indicator='roe' LIMIT 20"

# Examinar cobertura: n inclui resultados calculáveis e indisponíveis.
.venv/Scripts/python.exe scripts/pilot-ifdata-indicators.py query data/curated/ifdata-indicator-pilot-20261011 "SELECT dataset, indicator, method, status, sum(n) AS n FROM coverage GROUP BY ALL ORDER BY ALL"

# Reproduzir em um destino novo; sem coletar dados ou alterar fontes.
.venv/Scripts/python.exe scripts/pilot-ifdata-indicators.py build data/curated/ifdata-odata-20261011 data/curated/ifdata-cadastro-20261011 data/curated/ifdata-indicator-pilot-reproducao --opening-root data/curated/ifdata-indicator-opening-200912-20261011
```

| Tabela SQL / arquivo | Uso |
|---|---|
| `results` / `results.parquet` | Uma linha por conjunto/código/trimestre/indicador/método; componentes literais, resultado textual, fórmula, janela, versão, cadastro e evidência JSON completa. |
| `wide` / `wide.parquet` | Uma linha por unidade/trimestre, com colunas de valor, estado e versão para cada indicador/método. |
| `coverage` / `coverage.parquet` | Contagens por contexto, trimestre, indicador, método, versão e estado. |
| `statistics` / `statistics.parquet` | Contagem total/válida, média, desvio padrão, mínimo, quartis, mediana e máximo. Aproximação DOUBLE explícita, sem excluir extremos. |

Cada tabela tem cópia CSV UTF-8. `results.csv` omite os três campos JSON `numerator_definition`, `denominator_definition` e `mean_stock_inputs`; o Parquet mantém a evidência completa. Os números de cálculo permanecem texto decimal com precisão de divisão de 100 algarismos significativos; para análise, use `Decimal(value)` em Python. O painel e as estatísticas usam aproximações gráficas/numéricas, sem substituir esses valores.

Abra `painel.html` localmente no navegador para filtrar contexto, indicador/método, versão, trimestre e instituição, explorar séries, distribuição, dispersão e motivos de indisponibilidade. O painel funciona offline e exporta os valores do recorte mostrado; suas versões separam definições e durações distintas.

Financeiro, individual e prudencial têm populações próprias: `dataset` identifica a fonte e `unit_class` distingue conglomerado, independente, individual e cadastro desconhecido. Não some essas populações. Índices prudenciais não são copiados para unidades financeiras. A população técnica não é a amostra final de empresas de capital aberto.

Fluxos de março/setembro cobrem três meses; junho/dezembro, seis meses do semestre correspondente. Os retornos não são anualizados. A abertura de 2025 atravessa regime não conciliado e fica indisponível; margem e provisão/crédito de 2025–2026 também permanecem sem cálculo quando não há componente conciliado. Ausências, duplicatas, denominadores zero e definições desconhecidas têm motivos explícitos; sinais negativos são preservados. [Fundamentos e evidência do piloto](../../docs/engineering/ifdata-indicator-pilot-20261011.md).

## Verificação de software e rota portal histórica

Os comandos a seguir foram preservados do README anterior. Contagens, pins e inspeções datadas pertencem aos respectivos ledgers; os 11 snapshots do catálogo portal não limitam a cobertura da rota OData. Não repetir escrita/coleta em destinos aceitos. Em documentação, verificar links, coerência e escopo; suíte de software somente conforme impacto/contrato.

## Comandos locais verificados

Executar deste checkout. As rotinas existentes foram verificadas na etapa anterior, conforme os ledgers; nesta fundação documental não foi repetida a suíte de base. Python 3.12+ e Node já existem no runtime Codex deste laptop. Não instalar runtime ou repetir coleta para esta entrega.

```powershell
$pilotPython = Join-Path $PWD '.venv\Scripts\python.exe'
& $pilotPython -B -m unittest discover -s tests -v
$pilotNode = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
& $pilotNode --test tests/test-portal-ready.cjs tests/test-budget.cjs

# Replay offline para destino novo, preservando os derivados aceitos.
$replayOutput = Join-Path $env:TEMP ("ifdata-replay-" + [guid]::NewGuid().ToString())
& $pilotPython -B -m bank_quality replay --collection data/derived/expansion-20261001/collection.json --output $replayOutput
```

Replay verifica hashes dos corpos arquivados e reconstrói o derivado. O bruto precisa estar disponível localmente; referências documentais não substituem esses arquivos. Scripts de aceite/verificação que escrevem nos diretórios aceitos não são comandos de inspeção inocentes: avaliar destinos antes de executá-los. Disponibilidade de ferramentas e testes passando não demonstram validade econômica, contábil e financeira.

Para preparar a dependência Parquet em outro checkout, criar `.venv` com Python 3.12 e instalar somente o pin oficial: `python -m pip install --no-deps --only-binary=:all: --require-hashes -r requirements-duckdb.txt`, usando o Python da `.venv`. O arquivo pinado contém wheels oficiais para Windows amd64 e Linux x86_64, ambos Python 3.12; outras combinações exigem verificar o wheel correspondente. Replay e coleta não importam DuckDB; a suíte ampliada precisa dele.

```powershell
# Conversão offline; destino novo ou reuso validado de entrada idêntica.
& .\.venv\Scripts\python.exe -B -m bank_quality parquet --inventory data/derived/expansion-20261001/inventory --output data/curated/offline-pilot-20261003/snapshot --workers 1
```

Consulta direta em Python: `from pathlib import Path; from bank_quality.parquet import snapshot_connection`; `with snapshot_connection(Path('data/curated/offline-pilot-20261003/snapshot')) as con: result = con.execute('SELECT period, value_state, count(*) FROM observations GROUP BY period, value_state').fetchall()`. A view `observations` fixa os arquivos do manifesto validado. Cada abertura verifica hashes, schema, contagens, tokens e DECIMAL; não usa glob nem junta revisões.

Admissão financeira offline verificada, usando o índice explícito de cinco manifests já arquivados. O contrato do índice e a reprodução estão no [registro financeiro](../../docs/engineering/financial-snapshot-202412-execution-20261003.md#entrada-e-reprodução). Ambos os destinos abaixo precisam estar ausentes; para repetir, escolher outros destinos novos. Nenhum pedido HTTP é feito pelo leitor.

```powershell
& .\.venv\Scripts\python.exe -B scripts/admit-financial.py --index data/runs/financial-admission-202412-20261003/sources-reviewed.json --output data/derived/financial-202412-20261003
& .\.venv\Scripts\python.exe -B scripts/admit-financial.py --index data/runs/financial-admission-202412-20261003/sources-reviewed.json --output data/derived/financial-202412-20261003-replay
```

O financeiro 1005/92/202312 e 202412 tem conversor próprio: `scripts/convert-financial.py`, com `--source`, `--source-manifest-sha256` e `--output` obrigatórios. Exige os cinco arquivos admitidos, hash externo do manifest e destino novo; não usa o comando Parquet individual acima. [Comandos e hashes 202412](../../docs/engineering/financial-parquet-20261004.md) e [202312](../../docs/engineering/financial-snapshot-202312-execution-20261004.md). A seleção vem do índice/manifest validado; nenhum perfil é escolhido por parâmetro de usuário.

Na consulta financeira, cada linha é uma unidade IF.data × variável dentro do snapshot/referência. A view `financial_cells` conserva a grade completa; `financial_observations` seleciona `presence='stored'`. As colunas originais da admissão permanecem textuais. Nas projeções numéricas que cabem, `numeric_decimal` tem DECIMAL exato local ao binding; os bindings largos preservam texto exato e accessor Python Decimal. Os identificadores acrescentados pela view delimitam snapshot, ocorrência e binding. `snapshot_connection` exige o path e o hash final esperados e valida integralmente o conjunto antes da consulta. Uma apresentação com variáveis em colunas e séries históricas exige seleção/comparabilidade e contrato próprios.

Inspeção da aquisição: `& .\.venv\Scripts\python.exe -B scripts/acquire-financial.py --help` e `verify` com job/bootstrap/receipt externos foram executados. [Comando offline e pins reais](../../docs/engineering/financial-historical-acquisition-20261004.md#comandos-efetivamente-usados). Inicialização, coleta e recovery escrevem destinos novos ou estado de autoridade; usar o contrato da Issue, não repetir a execução aceita por conveniência.

A aquisição por janela usa `batch-prepare` → `batch-initialize` → `batch-run`, com paths/hashes externos, destino novo e identidade/budget imutáveis. [Execução, recursos e comando real](../../docs/engineering/financial-recent-batch-acquisition-20261005.md#comandos-e-pins-efetivamente-usados). `batch-recover` reconcilia antes de novos despachos; `batch-verify` inspeciona offline o conjunto com os bytes/runtime pinados. Uma janela concluída não pode ser reinicializada para renovar saldo; nova janela exige contrato. Coleta exige HEAD/código/runtime aprovados e margem atual; inspeção offline não faz GET nem exige HEAD histórico. Dados locais ignorados precisam estar disponíveis, sem glob/perfil arbitrário ou calendário futuro.

### Catálogo financeiro autenticado do portal histórico

A [Issue61](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61) adiciona `scripts/query-financial.py` para preparar, descobrir e consultar snapshots aceitos, com paths e hashes externos explícitos. A oferta de66referências não prova66aceites: o catálogo inicial local possui11aceitos/55indisponíveis. Entradas, provas e catálogos ficam em destinos privados ignorados; os comandos abaixo exigem os artefatos locais descritos no [ledger](../../docs/engineering/financial-catalog-20261006.md), não fornecidos pelo clone.

```powershell
$catalogFile = 'data/runs/financial-catalog-20261008-initial11/catalog.json'
$catalogHash = 'bc26107246a00d19b735d1e386a0a1ce27c65f889d840ec99cb3f723ef4463a3'
& .\.venv\Scripts\python.exe -B scripts/query-financial.py list --catalog $catalogFile --catalog-sha256 $catalogHash
& .\.venv\Scripts\python.exe -B scripts/query-financial.py show --catalog $catalogFile --catalog-sha256 $catalogHash --period 202312 --perspective 1005
& .\.venv\Scripts\python.exe -B scripts/query-financial.py counts --catalog $catalogFile --catalog-sha256 $catalogHash --period 202606 --perspective 1005
```

`list` usa somente metadados congelados e mantém cobertura global ao filtrar. `show` confere metadados/presença locais e informa `metadata_verified`/`not_run`; a saúde do payload depende da abertura pelo adapter. `counts`, `bindings`, `cells` e `decimals` usam templates fixos e validam o snapshot completo. Recebem período/perspectiva, report opcional e revision explícita quando necessário. `cells` aceita filtro de instituição; `decimals` exige `--report`/`--column` e retorna Decimal como texto exato, preservando null. Saídas cells/decimals têm default100/max10000linhas por `--limit`, com truncamento explícito. O filtro de report não reduz o perfil nativo ou cria uma série harmonizada.

Preparação: `catalog-prepare --inputs <índice-local> --inputs-sha256 <hash-externo> --output data/runs/financial-catalog-<novo-run>`. Exige destino inexistente e handoffs aceitos/autenticados do contrato; não autoriza coleta nem aceita `accepted:true` fornecido sem prova. JSON de erro usa exit2 para argumentos/seleção/indisponibilidade/ambiguidade/binding e exit3 para integridade/stale/I/O/falha inesperada, sem imprimir conteúdo privado da exceção. Detalhes e limites: [spec](../../docs/superpowers/specs/2026-10-06-financial-catalog-design.md).

## Histórico e contratos

A [versão anterior do README](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/f93d37f17898d69713d06f07bb393eb1f2444331/README.md) conserva os relatos de fundação/portal nas datas originais. [Arquitetura](../architecture.md), [mapa técnico](repository-review-20261012.md) e [workflow](../agents/workflow.md) são entradas para responsabilidades, schemas e execução. Não usar autorizações antigas como contrato de uma nova tarefa.

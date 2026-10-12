# Brazilian banks data quality

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

Os 428 gzip recebidos passaram na conferência de hashes/tamanhos. Pilotos foram revisados antes da expansão; a conferência integral dos resultados e a integração estão registradas na [PR 84](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/84) e no [plano vigente](docs/superpowers/plans/2026-10-05-financial-historical-acquisition-remaining.md). Conversão financeira: 194,844 segundos; os três complementos, em sequência: 236,969 segundos. São medidas desta máquina e pacote. Pacote, Parquet e credenciais ficam fora do GitHub.

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

A comparabilidade fica `nao_certificada`: estabilidade literal e cobertura não comprovam unidade, janela de fluxo, mensuração ou perímetro. O catálogo preserva descrições e auxilia a pesquisa dos componentes de indicadores, sem calcular/adotar indicadores ou inventar equivalências. [Fontes, dicionário e exemplos observados](docs/engineering/ifdata-variable-catalog-20261011.md).

**Retomada — 2026-10-06:** a [Release de snapshot](https://github.com/joaosantossgp/brazilian_banks_data_quality/releases/tag/snapshot-ifdata-11-20261006) transporta os dados locais sob criptografia, com `RETOMADA.md`, hashes e helpers de restauração em staging novo. O transporte foi validado no receptor e os11 conjuntos aceitos passaram na leitura integral/consultas; o candidato59 foi reconciliado em branch própria, com compatibilidade de runtime histórico, revisão/checks e recursos ainda necessários antes de coletar. A [nota59](docs/engineering/financial-historical-acquisition-remaining-20261005.md) registra provas e limitações. O clone ou download do ZIP de código não traz a base local; chave e pacote aberto permanecem privados e não entram no GitHub. Cobertura permanece11/66, sem nova coleta59.

**Direção aprovada — 2026-10-04:** a frente financeira final cobre Resumo, Ativo, Passivo e DRE oficiais, com todas as variáveis disponíveis e contratos próprios, nas referências trimestrais disponíveis do alvo2010–2026. O piloto de oito variáveis é uma primeira fatia, sem comprovar o histórico completo. A execução avança pelas Issues do [mapa2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2), com decisões técnicas autônomas registradas, testes/revisão e paralelismo medido entre lotes independentes. Decisões de objetivo/conteúdo final, metodologia acadêmica e mudanças críticas permanecem com João.

**Estado da rota — 2026-10-05:** os quatro relatórios financeiros oficiais estão validados localmente em **11/66 referências**, na janela recente 202312–202606. A [aquisição54](docs/engineering/financial-recent-batch-acquisition-20261005.md) forneceu as fontes; a [entrega55](docs/engineering/financial-historical-admission-202403-20261005.md) completou202403; o [executor comum57](docs/engineering/financial-batch-sanitization-20261005.md) concluiu os sete restantes em49 etapas de admissão, Parquet, consulta e replay, sem nova coleta. Publicação, CI e integração são conferidas na [Issue57](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/57)/[PR65](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/65). Faltam55 referências históricas: [coleta59](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/59) e [sanitização60](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/60), depois catálogo, complementos aprovados e auditoria. O [mapa2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) mantém etapas e paralelismo. Dados locais ignorados exigem o pacote de transferência além do clone; perfil instalado ou oferta não são cobertura aceita.

**Atualização de estado — 2026-10-03:** a fundação e o piloto do [PR 1](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1) foram integrados em main em 2026-10-02T18:37:51Z, no [merge 3234c20](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/3234c20); [CI pós-merge 37048733876](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37048733876) concluiu com sucesso. O instante exato é o registro da auditoria coordenada; as páginas públicas confirmam merge, data, commit e sucesso. Menções abaixo ao draft, ausência de merge ou confirmação pendente são histórico da preparação/publicação inicial, não o estado corrente. Isso não confirma publicação do novo conversor, sincronização atual do Project ou autorização para futuras integrações.

Base local de engenharia para a monografia de João sobre bancos brasileiros com **capital aberto**, preservando seu texto atual 2010–2024. O comportamento implementado é IF.data **individual/Resumo em 201012, 202312 e 202412**, além da admissão/consulta Parquet offline **financeira/Resumo 202312 e 202412 (1005/92), oito variáveis por referência**, além dos **quatro relatórios financeiros completos202412 e202503** descritos nos [ledger42](docs/engineering/financial-four-reports-202412-execution-20261004.md) e [ledger46](docs/engineering/financial-four-reports-202503-execution-20261004.md); a base multiuso financeira/prudencial/individual 2010–2026 permanece alvo em execução. Unidade acadêmica, janela final, tratamento de holdings e elegibilidade temporal continuam decisões de João/orientador.

Checkout no computador autorizado, na raiz deste repositório. A fundação e o piloto foram integrados em `main` pelo [PR 1](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1), commit `3234c20`, com [CI aprovado](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37048733876). O Project privado não torna privado o repositório público nem suas Issues.

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

[Execução, cobertura e limites do cadastro](docs/engineering/ifdata-cadastro-20261011.md). Dados continuam locais/ignorados; JSONs são fonte autoritativa para distinguir vazio e nulo.

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

Fluxos de março/setembro cobrem três meses; junho/dezembro, seis meses do semestre correspondente. Os retornos não são anualizados. A abertura de 2025 atravessa regime não conciliado e fica indisponível; margem e provisão/crédito de 2025–2026 também permanecem sem cálculo quando não há componente conciliado. Ausências, duplicatas, denominadores zero e definições desconhecidas têm motivos explícitos; sinais negativos são preservados. [Fundamentos e evidência do piloto](docs/engineering/ifdata-indicator-pilot-20261011.md).

## Entradas e contrato único

- [Arquitetura atual, alvo e contratos](docs/architecture.md)
- [Modelo lógico aprovado da base IF.data](docs/superpowers/specs/2026-10-04-logical-data-model-design.md), com ER SVG/PNG; aprovado por João em 2026-10-04. O [primeiro Parquet financeiro 202412](docs/engineering/financial-parquet-20261004.md), na [Issue 29](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/29), implementa o [plano Native autorizado](docs/superpowers/plans/2026-10-04-financial-parquet.md): grade completa e observações consultáveis, com contratos individuais preservados. Expansão histórica e apresentação consolidada para análise continuam entregas próprias.
- [Glossário de domínio](GLOSSARY.md) e [entrada operacional dos agentes](AGENTS.md)
- [Spec aprovada da fundação](docs/superpowers/specs/2026-10-02-governance-research-design.md) e [plano autorizado](docs/superpowers/plans/2026-10-02-governance-foundation-plan.md)
- [Tracker: tarefa, aceite e estado de publicação](docs/agents/issue-tracker.md)
- [Ferramentas de pesquisa, proveniência e limites funcionais](docs/engineering/research-tooling-20261002.md)

A autorização explícita de publicação de 2026-10-02 permite completar/revisar a fundação, CI offline mínimo, commit/push do conjunto revisado, bootstrap mínimo de main, draft PR e reconciliação das mesmas Issues/cards no Project /3 por ferramenta suportada. Os gates anteriores de não publicar/não implementar CI são histórico datado e foram substituídos para esta entrega. Não autoriza merge, deploy, nova coleta, capítulo, calendário, runtime/contas/chaves, mudança de segurança/permissões/tokens/proteções ou outro Project. Publicação da fundação e CI pós-merge estão confirmados na atualização datada acima; não há novo gate humano para o escopo já aprovado. O [conjunto exato e limites de licença](docs/engineering/governance-publication-proposal.md) orienta a publicação. A licença do código/documentação próprios não foi escolhida; MIT upstream não a substitui.

## Resultado implementado e evidência preservada

A [aquisição financeira histórica](docs/engineering/financial-historical-acquisition-20261004.md) foi provada em 202403/1005/quatro relatórios: 3 GETs, 16.342.157 bytes, cadastro/dicionário antes de N1, pausa/retomada sem recoleta. Essa rota standalone permanece fechada em 202403. O [coordenador por janela](docs/engineering/financial-recent-batch-acquisition-20261005.md) acrescenta comandos `batch-*`, onze referências e sete autoridades próprias: um ou dois períodos nos metadados após medição, todos os sete metadados antes dos valores, valores sequenciais, 21 GETs/115.582.580 bytes/zero falhas. Nenhuma captura nova é admissão ou Parquet; o comando por lote conserva contratos/checkpoints por referência.

A [Issue46](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/46) acrescenta o conjunto nativo202503:Resumo119/Ativo107/Passivo110/DRE118,1425cadastros/158nós/143folhas,203775células/202830armazenadas/945ausências. Os mesmos reader/adapter usam contextos locais e dois perfis fechados, preservando202412 e os legados. Grade textual e107projeções numéricas exatas, consultas completas e replay byteigual. [Comandos, hashes, capacidade e limites](docs/engineering/financial-four-reports-202503-execution-20261004.md); sem equivalência econômica2024/2025 ou aceite histórico integral.

A [Issue42](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/42) entrega Resumo, Ativo, Passivo e DRE financeiros202412 com todas as variáveis oficiais:1.422cadastros,121nós/112folhas,159.264células,158.746armazenadas e518ausências. Grade Parquet textual e76projeções numéricas por binding preservam precisão exata sem cast/UNION global; consultas e replay foram confrontados integralmente. [Comandos, hashes, capacidade medida e limites](docs/engineering/financial-four-reports-202412-execution-20261004.md). APIs/CLIs existentes selecionam o novo contrato fechado; snapshots do piloto e individuais conservam seus contratos. Publicação/revisão/CI têm estado na Issue real; isto não encerra o alvo2010–2026.

A [Issue 36](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/36) acrescenta o snapshot financeiro 202312: 1.385 registros, cadastro nativo com 32 campos, oito variáveis, 11.062 observações e 18 posições sem armazenamento. Perfis fechados por seleção, manifests legados qualificados por hashes exatos e Parquet consultável conservam proveniência/precisão/ausências; defaults 202412 e contratos individuais permanecem. O [ledger de execução](docs/engineering/financial-snapshot-202312-execution-20261004.md) traz reprodução, hashes e limites: conversão em lote 1,344 s versus 134 s do baseline, payload idêntico. São medidas do piloto Resumo; o conjunto completo202412 está descrito abaixo, enquanto a expansão histórica de todos os relatórios continua própria. Estado remoto e revisão têm autoridade na Issue real.

Na [Issue 25](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/25), o leitor financeiro offline admitiu cinco fontes arquivadas de 202412: 1.422 registros cadastrais, oito variáveis e 11.334 observações. A grade conserva 42 posições monetárias sem armazenamento; replay reproduziu cinco arquivos byte a byte. O [registro de execução](docs/engineering/financial-snapshot-202412-execution-20261003.md) separa integridade técnica, limites de unidade/janela/vintage e publicação. As saídas `financial-*` têm contrato próprio e não entram no conversor Parquet individual.

Em 2026-10-03 foi aceita a camada local Python + DuckDB + Parquet, conforme [ADR](docs/adr/0001-duckdb-parquet.md), [desenho](docs/superpowers/specs/2026-10-03-offline-parquet-design.md) e [plano](docs/superpowers/plans/2026-10-03-offline-parquet.md). A preparação original foi somente local; a autorização posterior de João inclui reconciliar, revisar e publicar esta entrega por branch/PR, acompanhada na [Issue 15](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/15). O comando offline `parquet` preserva os campos originais como texto e acrescenta DECIMAL exato, sem substituir bruto/CSV/JSON ou criar banco persistido. Os resultados medidos estão no [registro de execução](docs/engineering/offline-parquet-20261003.md).

O piloto original 201012/202412 permanece preservado: [design](docs/superpowers/specs/2026-10-01-ifdata-pilot-design.md), [plano histórico](docs/superpowers/plans/2026-10-01-ifdata-pilot.md), [resultado](reports/pilot-20261001.md), [ledger](docs/engineering/pilot-execution.md) e [comparação das quatro referências MIT](docs/engineering/reference-comparison.md). Os comandos de aquisição desses registros são históricos, sem autorização de reexecução nesta fundação.

A expansão limitada **202312 está concluída**, por portal oficial, individual/Resumo: 1.552 instituições, 8 indicadores, 12.416 observações. A composição tem 40.904 observações, 52 corpos de evidência verificados e 7 artefatos reproduzidos byte a byte. São resultados da verificação registrada no [ledger de expansão](docs/engineering/expansion-execution.md), [relatório](reports/expansion-20261001.md) e verificação local preservada (`reports/expansion-20261001.verification.json`, excluída da publicação), não uma execução nova de coleta ou testes por esta tarefa documental.

O [dossiê temporal](docs/engineering/capital-aberto-identity-dossier.md) mantém oito relações emissor–IF.data desconhecidas. Cobertura compara snapshots recuperados; não prova universo histórico ou elegibilidade acadêmica. OData não foi tentado para 202312. Valores de fluxo em dezembro não se tornam anuais por convenção: a evidência existente registra julho–dezembro. CSVs derivados preservam tokens/unidades/hashes; `value_state` distingue null, vazio, NA, NI e zero.

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

Admissão financeira offline verificada, usando o índice explícito de cinco manifests já arquivados. O contrato do índice e a reprodução estão no [registro financeiro](docs/engineering/financial-snapshot-202412-execution-20261003.md#entrada-e-reprodução). Ambos os destinos abaixo precisam estar ausentes; para repetir, escolher outros destinos novos. Nenhum pedido HTTP é feito pelo leitor.

```powershell
& .\.venv\Scripts\python.exe -B scripts/admit-financial.py --index data/runs/financial-admission-202412-20261003/sources-reviewed.json --output data/derived/financial-202412-20261003
& .\.venv\Scripts\python.exe -B scripts/admit-financial.py --index data/runs/financial-admission-202412-20261003/sources-reviewed.json --output data/derived/financial-202412-20261003-replay
```

O financeiro 1005/92/202312 e 202412 tem conversor próprio: `scripts/convert-financial.py`, com `--source`, `--source-manifest-sha256` e `--output` obrigatórios. Exige os cinco arquivos admitidos, hash externo do manifest e destino novo; não usa o comando Parquet individual acima. [Comandos e hashes 202412](docs/engineering/financial-parquet-20261004.md) e [202312](docs/engineering/financial-snapshot-202312-execution-20261004.md). A seleção vem do índice/manifest validado; nenhum perfil é escolhido por parâmetro de usuário.

Na consulta financeira, cada linha é uma unidade IF.data × variável dentro do snapshot/referência. A view `financial_cells` conserva a grade completa; `financial_observations` seleciona `presence='stored'`. As colunas originais da admissão permanecem textuais. Nas projeções numéricas que cabem, `numeric_decimal` tem DECIMAL exato local ao binding; os bindings largos preservam texto exato e accessor Python Decimal. Os identificadores acrescentados pela view delimitam snapshot, ocorrência e binding. `snapshot_connection` exige o path e o hash final esperados e valida integralmente o conjunto antes da consulta. Uma apresentação com variáveis em colunas e séries históricas exige seleção/comparabilidade e contrato próprios.

Inspeção da aquisição: `& .\.venv\Scripts\python.exe -B scripts/acquire-financial.py --help` e `verify` com job/bootstrap/receipt externos foram executados. [Comando offline e pins reais](docs/engineering/financial-historical-acquisition-20261004.md#comandos-efetivamente-usados). Inicialização, coleta e recovery escrevem destinos novos ou estado de autoridade; usar o contrato da Issue, não repetir a execução aceita por conveniência.

A aquisição por janela usa `batch-prepare` → `batch-initialize` → `batch-run`, com paths/hashes externos, destino novo e identidade/budget imutáveis. [Execução, recursos e comando real](docs/engineering/financial-recent-batch-acquisition-20261005.md#comandos-e-pins-efetivamente-usados). `batch-recover` reconcilia antes de novos despachos; `batch-verify` inspeciona offline o conjunto com os bytes/runtime pinados. Uma janela concluída não pode ser reinicializada para renovar saldo; nova janela exige contrato. Coleta exige HEAD/código/runtime aprovados e margem atual; inspeção offline não faz GET nem exige HEAD histórico. Dados locais ignorados precisam estar disponíveis, sem glob/perfil arbitrário ou calendário futuro.

### Catálogo financeiro autenticado

A [Issue61](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61) adiciona `scripts/query-financial.py` para preparar, descobrir e consultar snapshots aceitos, com paths e hashes externos explícitos. A oferta de66referências não prova66aceites: o catálogo inicial local possui11aceitos/55indisponíveis. Entradas, provas e catálogos ficam em destinos privados ignorados; os comandos abaixo exigem os artefatos locais descritos no [ledger](docs/engineering/financial-catalog-20261006.md), não fornecidos pelo clone.

```powershell
$catalogFile = 'data/runs/financial-catalog-20261008-initial11/catalog.json'
$catalogHash = 'bc26107246a00d19b735d1e386a0a1ce27c65f889d840ec99cb3f723ef4463a3'
& .\.venv\Scripts\python.exe -B scripts/query-financial.py list --catalog $catalogFile --catalog-sha256 $catalogHash
& .\.venv\Scripts\python.exe -B scripts/query-financial.py show --catalog $catalogFile --catalog-sha256 $catalogHash --period 202312 --perspective 1005
& .\.venv\Scripts\python.exe -B scripts/query-financial.py counts --catalog $catalogFile --catalog-sha256 $catalogHash --period 202606 --perspective 1005
```

`list` usa somente metadados congelados e mantém cobertura global ao filtrar. `show` confere metadados/presença locais e informa `metadata_verified`/`not_run`; a saúde do payload depende da abertura pelo adapter. `counts`, `bindings`, `cells` e `decimals` usam templates fixos e validam o snapshot completo. Recebem período/perspectiva, report opcional e revision explícita quando necessário. `cells` aceita filtro de instituição; `decimals` exige `--report`/`--column` e retorna Decimal como texto exato, preservando null. Saídas cells/decimals têm default100/max10000linhas por `--limit`, com truncamento explícito. O filtro de report não reduz o perfil nativo ou cria uma série harmonizada.

Preparação: `catalog-prepare --inputs <índice-local> --inputs-sha256 <hash-externo> --output data/runs/financial-catalog-<novo-run>`. Exige destino inexistente e handoffs aceitos/autenticados do contrato; não autoriza coleta nem aceita `accepted:true` fornecido sem prova. JSON de erro usa exit2 para argumentos/seleção/indisponibilidade/ambiguidade/binding e exit3 para integridade/stale/I/O/falha inesperada, sem imprimir conteúdo privado da exceção. Detalhes e limites: [spec](docs/superpowers/specs/2026-10-06-financial-catalog-design.md).

## Pesquisa, rigor e decisões abertas

Financeiro vem somente de IF.data; CVM/B3 são metadados temporais distintos. A [spec](docs/superpowers/specs/2026-10-02-governance-research-design.md) é autoridade para fontes primárias verificáveis, fórmulas/unidades/janelas/perímetros, quebras, versões, ausências, reprodução e incertezas. A [nota de desenho](docs/engineering/brainstorming-2010-2026-20261002.md) conserva a discussão e decisões anteriores; relatórios/variáveis da expansão, consulta, vínculos e filtro acadêmico exigem desenho/decisão posteriores.

As nove skills Matt e Superpowers global permanecem; Context7 teve acesso verificado, exigindo checagem da versão efetivamente usada. Somente Feynman **deep-research** e **pdf-explore** estão ativas, com MIT/proveniência preservados. `/deepresearch` no Codex nativo permanece não validado; não ampliar instalação para contornar isso. O [registro de tooling](docs/engineering/research-tooling-20261002.md) contém versões, hashes e histórico.

Redação acadêmica assistida é permitida sob direção, revisão e responsabilidade de João, com fontes/dados/citações/referências verificáveis e transparência institucional aplicável. Não há capítulo solicitado agora; paper-writing permanece inativa.

Entrada de trabalho: [workflow obrigatório de Issues](docs/agents/workflow.md), com título `[Tipo] Verbo + resultado ou recorte`, labels de tipo/role/área/estado, domínio e skills por etapa. Dependências satisfeitas e escopo aprovado permitem execução paralela, inclusive na mesma área; checks pertinentes e revisão independente permitem integração autônoma. João decide mudanças de escopo e método. O [tracker único](docs/agents/issue-tracker.md#etapas-skills-entregáveis-gates-e-owners) mantém autoridade e histórico; o Project /3 é acompanhado por Zec.

Documentação visual: `diagram-design:diagram-design` disponível, entregando [SVG](docs/agents/assets/issue-workflow.svg) e [PNG](docs/agents/assets/issue-workflow.png) visíveis no GitHub, com alternativa textual. O [checker de escopo do PR](docs/engineering/pr-scope-observation.md) foi integrado pelo PR 19 e continua offline em observação; não há runner remoto/required nem validação automática dos campos de Issue.

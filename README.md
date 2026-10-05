# Brazilian banks data quality

**Direção aprovada — 2026-10-04:** a frente financeira final cobre Resumo, Ativo, Passivo e DRE oficiais, com todas as variáveis disponíveis e contratos próprios, nas referências trimestrais disponíveis do alvo2010–2026. O piloto de oito variáveis é uma primeira fatia, sem comprovar o histórico completo. A execução avança pelas Issues do [mapa2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2), com decisões técnicas autônomas registradas, testes/revisão e paralelismo medido entre lotes independentes. Decisões de objetivo/conteúdo final, metodologia acadêmica e mudanças críticas permanecem com João.

**Trabalho local validado — Issue 51:** o [registry histórico e a admissão comum](docs/engineering/financial-historical-admission-20261004.md) têm perfil 202312 revisto, quatro relatórios admitidos e Parquet/query/replay reais aprovados: 155.120 células, 154.898 observações e 222 ausências. Projeções preservam 75 bindings DECIMAL nativos e um texto numérico exato largo, com leitura Python Decimal validada. Suíte pública final, revisão whole-branch e integração são etapas separadas, verificadas na Issue. Main confirma a aquisição 202403 da Issue 50; oferta de 66 referências não é cobertura aceita. Próxima janela planejada 202312–202606: reuso do arquivado, um comando de lote e paralelismo medido.

**Atualização de estado — 2026-10-03:** a fundação e o piloto do [PR 1](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1) foram integrados em main em 2026-10-02T18:37:51Z, no [merge 3234c20](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/3234c20); [CI pós-merge 37048733876](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37048733876) concluiu com sucesso. O instante exato é o registro da auditoria coordenada; as páginas públicas confirmam merge, data, commit e sucesso. Menções abaixo ao draft, ausência de merge ou confirmação pendente são histórico da preparação/publicação inicial, não o estado corrente. Isso não confirma publicação do novo conversor, sincronização atual do Project ou autorização para futuras integrações.

Base local de engenharia para a monografia de João sobre bancos brasileiros com **capital aberto**, preservando seu texto atual 2010–2024. O comportamento implementado é IF.data **individual/Resumo em 201012, 202312 e 202412**, além da admissão/consulta Parquet offline **financeira/Resumo 202312 e 202412 (1005/92), oito variáveis por referência**, além dos **quatro relatórios financeiros completos202412 e202503** descritos nos [ledger42](docs/engineering/financial-four-reports-202412-execution-20261004.md) e [ledger46](docs/engineering/financial-four-reports-202503-execution-20261004.md); a base multiuso financeira/prudencial/individual 2010–2026 permanece alvo em execução. Unidade acadêmica, janela final, tratamento de holdings e elegibilidade temporal continuam decisões de João/orientador.

Checkout no computador autorizado, na raiz deste repositório. A fundação e o piloto foram integrados em `main` pelo [PR 1](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1), commit `3234c20`, com [CI aprovado](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37048733876). O Project privado não torna privado o repositório público nem suas Issues.

## Entradas e contrato único

- [Arquitetura atual, alvo e contratos](docs/architecture.md)
- [Modelo lógico aprovado da base IF.data](docs/superpowers/specs/2026-10-04-logical-data-model-design.md), com ER SVG/PNG; aprovado por João em 2026-10-04. O [primeiro Parquet financeiro 202412](docs/engineering/financial-parquet-20261004.md), na [Issue 29](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/29), implementa o [plano Native autorizado](docs/superpowers/plans/2026-10-04-financial-parquet.md): grade completa e observações consultáveis, com contratos individuais preservados. Expansão histórica e apresentação consolidada para análise continuam entregas próprias.
- [Glossário de domínio](GLOSSARY.md) e [entrada operacional dos agentes](AGENTS.md)
- [Spec aprovada da fundação](docs/superpowers/specs/2026-10-02-governance-research-design.md) e [plano autorizado](docs/superpowers/plans/2026-10-02-governance-foundation-plan.md)
- [Tracker: tarefa, aceite e estado de publicação](docs/agents/issue-tracker.md)
- [Ferramentas de pesquisa, proveniência e limites funcionais](docs/engineering/research-tooling-20261002.md)

A autorização explícita de publicação de 2026-10-02 permite completar/revisar a fundação, CI offline mínimo, commit/push do conjunto revisado, bootstrap mínimo de main, draft PR e reconciliação das mesmas Issues/cards no Project /3 por ferramenta suportada. Os gates anteriores de não publicar/não implementar CI são histórico datado e foram substituídos para esta entrega. Não autoriza merge, deploy, nova coleta, capítulo, calendário, runtime/contas/chaves, mudança de segurança/permissões/tokens/proteções ou outro Project. Publicação da fundação e CI pós-merge estão confirmados na atualização datada acima; não há novo gate humano para o escopo já aprovado. O [conjunto exato e limites de licença](docs/engineering/governance-publication-proposal.md) orienta a publicação. A licença do código/documentação próprios não foi escolhida; MIT upstream não a substitui.

## Resultado implementado e evidência preservada

A [aquisição financeira histórica](docs/engineering/financial-historical-acquisition-20261004.md) foi provada em 202403/1005/quatro relatórios: 3 GETs, 16.342.157 bytes, cadastro/dicionário antes de N1, pausa e retomada sem recoletar metadata. CLI `scripts/acquire-financial.py` e autoridade local limitada têm revisão independente; fonte completa/validada ainda depende de admissão histórica para gerar Parquet. O lote seguinte cobre um intervalo de referências, com concorrência medida; a CLI desta prova permanece fechada em 202403.

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

Na consulta financeira, cada linha é uma unidade IF.data × variável dentro do snapshot/referência. A view `financial_cells` conserva a grade completa; `financial_observations` seleciona `presence='stored'`. As 32 colunas da admissão são texto preservado; `numeric_decimal` é DECIMAL exato; cinco chaves/identificadores acrescentados pela view delimitam snapshot, ocorrência e binding. `snapshot_connection` exige o path e o hash final esperados e valida integralmente o conjunto antes da consulta. Uma apresentação com variáveis em colunas e séries históricas exige seleção/comparabilidade e contrato próprios.

Inspeção da aquisição: `& .\.venv\Scripts\python.exe -B scripts/acquire-financial.py --help` e `verify` com job/bootstrap/receipt externos foram executados. [Comando offline e pins reais](docs/engineering/financial-historical-acquisition-20261004.md#comandos-efetivamente-usados). Inicialização, coleta e recovery escrevem destinos novos ou estado de autoridade; usar o contrato da Issue, não repetir a execução aceita por conveniência.

## Pesquisa, rigor e decisões abertas

Financeiro vem somente de IF.data; CVM/B3 são metadados temporais distintos. A [spec](docs/superpowers/specs/2026-10-02-governance-research-design.md) é autoridade para fontes primárias verificáveis, fórmulas/unidades/janelas/perímetros, quebras, versões, ausências, reprodução e incertezas. A [nota de desenho](docs/engineering/brainstorming-2010-2026-20261002.md) conserva a discussão e decisões anteriores; relatórios/variáveis da expansão, consulta, vínculos e filtro acadêmico exigem desenho/decisão posteriores.

As nove skills Matt e Superpowers global permanecem; Context7 teve acesso verificado, exigindo checagem da versão efetivamente usada. Somente Feynman **deep-research** e **pdf-explore** estão ativas, com MIT/proveniência preservados. `/deepresearch` no Codex nativo permanece não validado; não ampliar instalação para contornar isso. O [registro de tooling](docs/engineering/research-tooling-20261002.md) contém versões, hashes e histórico.

Redação acadêmica assistida é permitida sob direção, revisão e responsabilidade de João, com fontes/dados/citações/referências verificáveis e transparência institucional aplicável. Não há capítulo solicitado agora; paper-writing permanece inativa.

Entrada de trabalho: [workflow obrigatório de Issues](docs/agents/workflow.md), com título `[Tipo] Verbo + resultado ou recorte`, labels de tipo/role/área/estado, domínio e skills por etapa. Dependências satisfeitas e escopo aprovado permitem execução paralela, inclusive na mesma área; checks pertinentes e revisão independente permitem integração autônoma. João decide mudanças de escopo e método. O [tracker único](docs/agents/issue-tracker.md#etapas-skills-entregáveis-gates-e-owners) mantém autoridade e histórico; o Project /3 é acompanhado por Zec.

Documentação visual: `diagram-design:diagram-design` disponível, entregando [SVG](docs/agents/assets/issue-workflow.svg) e [PNG](docs/agents/assets/issue-workflow.png) visíveis no GitHub, com alternativa textual. O [checker de escopo do PR](docs/engineering/pr-scope-observation.md) foi integrado pelo PR 19 e continua offline em observação; não há runner remoto/required nem validação automática dos campos de Issue.

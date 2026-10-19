# Proveniência: aberturas de crédito e lacunas N1/N2

Companheira da[nota de resultados](ifdata-credit-openings-temporal-gaps-20261019.md),[Issue196](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/196). Não é revisão sistemática nem nova leitura bibliográfica deAssaf. Reaproveita inventário113, pesquisa143, diagnóstico176 e viabilidades181–192; a contribuição nova é fonte/acesso, ingestão e diagnóstico empírico finito.

## Entradas fixas e ownership

Base pública de execução:`8c997385970643e165ba8111c0636cb60b900110`, branch`codex/ifdata-credit-gaps-196`, worktree isolado`ifdata-credit-gaps/brazilian_banks_data_quality`. Root é único writer e integrador das duas notas; revisor independente não escreve nem coleta. Não há alteração de arquitetura: destinos canônicosengineering e dados privadosraw/curated existentes; nenhum módulo/camada/dependência/CI novo. Outro worktree conserva o candidato visual193.

Ponteiro compartilhado lido e autenticado no checkout principal, conservado integralmente:

| Entrada | SHA-256 |
|---|---|
|manifest de`historical-links32-composition-20261018-run3`|`d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`|
|unit_coverage.parquet|`c45dcb06b99945ec088c2d1ac008df18efa15520ec4830a66cdc771a50db32b6`|
|baseline manifest de`ifdata-universe-analysis-20261014-final-run3`|`b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`|
|baseline results.parquet|`22d70671f661a8fc5fec2b5048a44ba05e35f4b9ec52a42da9d672746ffdb0f4`|
|baseline components.parquet|`0a1aa6035a943368d6e15b20aa7bf4588abf5cb70f97cbf3ac0a1fd6993941b1`|
|bruto`ifdata-odata-20261011/manifesto.json`|`710e4de74c05c76f13a2f26edad6cb1e7e669d721e1cdd7cd516664db8a6b760`|

O suplemento de comparação192, manifest`f374150e5d4c515f032fdf3fad3cb27b4e196486cee8d81c19150c39df45981b`, foi explicitamente identificado como não promovido; o aprofundamento temporal usa20métricas do pin vigente,d47. Não alegar auditoria causal dos sete complementos novos desta tarefa. `temporal-summary.json` registra também os hashes das tabelas de segmentação consumidas; a consulta econômica do piloto usa unit_periods autenticada pelo inventário.

## Estratégia e fontes primárias

Perguntas delimitadas: quais aberturas existem e por qual rota; quais componentes estão conjuntamente disponíveis; quais faltas críticas deN1/N2 são de conta, nulo, janela ou código/perímetro. Critério de seleção: fonte oficialBCB com campos/data verificáveis ou dado local autenticado; não usar bancos de dados secundários para completar faltas. Consultas de busca web iniciais sem resultado útil foram substituídas pela documentação primária, API, bruto preservado e navegação oficial. Busca bibliográfica geral/externa não foi reaberta.

| Fonte e localizador | Leitura/captura desta tarefa | Papel e limites |
|---|---|---|
|[IF.data, metodologia corrente](https://www3.bcb.gov.br/ifdata/index.html), seçõesInformações deCrédito/Cosif2025|HTML e navegação19/10/2026|Oferta/calendário e perímetros. Não prova cobertura individual; o trecho201206–201403 não foi inferido como disponível naAPI Tipo2.|
|[OlindaIFDATA, documentação](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao),`especificacao.recursos`→IfDataValores eListaDeRelatorio|HTTP200, corpoSHA`72736b41ccf4c496a62e5cc98aeea25d6497b9bf0fcb97df05e845a54f518529`|Parâmetros nativos, descrições e relatórios. ListaDeRelatorio é função sem parâmetros; usar`ListaDeRelatorio()`.|
|[OData metadata](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/$metadata),FunctionImport/Function|HTTP200, corpoSHA`d57e34182fd227a0ba4efd2d8affb23370a150c57250da3601c7a43191075ce6`|Contrato de acesso; não interpreta equivalência econômica.|
|[ListaDeRelatorio()](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/ListaDeRelatorio()?%24format=json)|HTTP200,16relatórios,SHA`897ebef3a5276c891b27c27b760f523f5dad8663e8446488d1ce06b4192e73f4`|7–14 são as oito aberturas do núcleo.16é relatório novo, não emendado ao riscoAA–H.|
|[IfDataValores](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao),Tipo2,relatórios8/11/13,202412|15.642/82.476/105.228linhas completas, semnextLink|Tokens e chaves coincidiram com a captura local; seleção mínima do parâmetro`$select` em11/13 conserva campos decontexto/valor.|
|[Portal histórico](https://www3.bcb.gov.br/ifdata/index2024.html),06/2012→Financeiro(SCR)→risco|NavegaçãoCua e downloadCSV; cabeçalho, seleção, escala e observaçãoSCR lidos|Prova de acesso alternativa; códigos portal não são assumidos comoCNPJ/CodInst. Não certificar completude pela tabela virtualizada.|

Capturas novas privadas em`data/raw/ifdata-credit-gaps-20261019/`, com corpos e manifests do transportador existente:URL completa/parâmetros,UTC,status,headers,diagnósticos,SHA. Índices`source-index.json` e`source-stage2-index.json` em`.scratch/ifdata-credit-gaps/` apontam cada tentativa. Headers/status do download do navegador não foram expostos pela ferramenta e **não foram inventados**.

Hashes dos corpos completos novos: relatório8/202412`e7bcb46f55ad9f3f99083de586b3799f61e1b4fc7cec35075ef470431b477b1d`;11/202412`61ba84315750e1bca1ddd11e2397985581519f863ffacc901172b9d578f9ffaf`;13/202412`5847bfe062989fec48cce008f79d0b17ad022941d05233df0cba3aeba7dee04e`. Arrays vazios8/201206e201203:`51cdb1f4d7ea16f4a4b5079fcb838ec74add3de052afdddb61d4ed61ab4e93e4`.

CSVportal original:`portal-risk-201206-original.csv`,SHA`85afbb17cd5644cde5e3494f961c043164d8bf8e5e79674cd7d8666eb4b1123a`; recibo`portal-risk-201206-receipt.json`. Download original também permanece no destino deDownloads, sem remoção. O recibo registra seleções, cabeçalho, escala, namespace e data de corte mostrada25/03/2019. São1.697linhas institucionais datadas e27linhas de seções/agregados;1.724após o cabeçalho não é contagem de instituições. OUTC do recibo é de arquivamento; o índice de navegador constitui a evidência da operação, sem alegar HTTP capturado.

## Consultas e reprodução local

Python3.12/DuckDB já configurados na`.venv` do checkout principal; nenhum runtime/pacote instalado. Antes da expansão, memória observada32.454,7MiBtotal/9.200,4MiBlivre aproximadamente, importação sequencial porpágina, piloto já medido. Importador público preservado:[scripts/import-ifdata.py](../../scripts/import-ifdata.py) e[bank_quality/ifdata_odata.py](../../bank_quality/ifdata_odata.py).

Importação do piloto:

```powershell
& $python -X utf8 scripts/import-ifdata.py import $raw $newPilot --periods 202412 --types 2 --reports 7 8 9 10 11 12 13 14
```

`$python` é o executável da`.venv` existente;`$raw` é a raiz bruta autenticada; os destinos devem serNOVOS. Para o pacote completo,`--periods` enumera42datas trimestrais201409–202412; o pacote`early` seleciona201406 e7,8,10–14. O recibo completo conserva os argumentos literais. A divisão economiza42releituras de gzip comparada à alternativa sete relatórios mais uma importação separada de região. Os imports escrevem somente destinos novos. Não sobrescrever pacotes para replay.

Consultas públicas existentes:

```powershell
& $python -X utf8 scripts/import-ifdata.py counts $core
& $python -X utf8 scripts/import-ifdata.py query $core 'select NumeroRelatorio, Conta, Grupo, NomeColuna, DescricaoColuna, min(AnoMes), max(AnoMes) from ifdata group by all'
```

Instrumentos finitos privados, sem criar motor do projeto:

| Instrumento em`.scratch/ifdata-credit-gaps/` | Saída/checagem |
|---|---|
|`source_pilot.py`,`source_stage2.py`|Captura limitada, falhas e paginação.|
|`raw_inventory.py`|60páginas/contextosFinanceiro; SHA/sizegzip contra manifesto; contagem de tokensNumeroRelatorio reconciliada ao total bruto.17,03segundos. As contagens foram posteriormente revalidadas pelo importador/Parquet.|
|`import_full.py`|Importador existente, core+early,240,61segundos;receipt com hashes e comandos.|
|`verify_full.py`|43partsSHA,343contagens contra bruto, unicidade identificada,3.350linhas sem código conservadas;269contextos devariáveis e556grupos de disponibilidadeTcb/coorte/data.|
|`pilot_checks.py`|Chaves/tokens, contas, disponibilidade conjunta e reconciliações aritméticas4T2024;`pilot-checks.json`.|
|`temporal_audit.py`|Pin explícitod47, hashes,20métricas/26janelas,21reconciliaçõesR1/TTM;nominais/status/coortes sem fórmulas.|
|`component_followup.py`|Referências persistidas deR1; componentes nulos/ausentes; busca no mesmo código/dataFinanceiro.356falhas,385coordenadas deinput,320binding sem linhas e65coordenadas adicionais nulas.|

Contagens, mínimo temporal e representatividade usam valores persistidos/Fraction; a apresentação percentual da cobertura usaDecimal. Não converter saldos aDOUBLE. A consulta porTcb usa`$.classifications.Tcb`;coortes nativas permanecemsample/remaining/unknown. Disponibilidade não é aplicabilidade; resultados comdenominadorzero/nãoaplicabilidade não foram automaticamente somados como falhas de dados.

Os arquivos de evidência incluem`raw-credit-inventory.json`,`full-verification.json`,`credit-variable-contexts.csv`,`credit-joint-availability.csv`,`pilot-economic-coverage.json`,`temporal-summary.json`,`nominal-roa-ttm.json`,`missing-all-metrics.jsonl`,`failure-decomposition-r1-r2.jsonl`,`component-failures.jsonl`,`binding-native-availability.json`. O nome de arquivo`missing-all-metrics` inventaria status nãook, inclusive estados deaplicabilidade; não significa que cada linha seja dado faltante a recuperar. Dados/evidências não vão aoGit público.

## Tentativas e correções preservadas

- Busca inicial comglob dePowerShell emrg retornou caminho inválido/arquivo inexistente; descoberta refeita por`rg --files`, sem assumir ausência de capacidade.
-`ListaDeRelatorio` sem parênteses retornouHTTP400, corpoSHA`a2320872c4b0a3f0edfd291515fd21a68ce2d5359c9f5a0e16fa9675be6c11d3`; sintaxe corrigida após metadata, tentativa preservada.
- Primeiro piloto13/202412/top10 falhou porrede/timeout. Repetição limitada completa foiHTTP200; a falha não virou ausência histórica.
- Consulta exploratória digitou`group by1`; corrigida para`group by 1`. Não era problema do dataset.
- Primeiro comparadorAPI usouparse_float=str, mas não parse_int=str:63tokens inteiros no relatório8 apareciam diferentes de strings. Parser corrigido conforme leitor existente, sem reescrever fonte. Comparação final de8/11/13 exata; logs anteriores preservados.
- Primeiro verificador deunicidade incluiuCodInstnull como se fosse uma identidade. Falhou em202009; investigação provou ocorrências sem código. Conservação de3.350linhas e verificação de chaves identificadas separadas; não deduplicar nulls nem fabricar instituição. A primeira execução continua registrada como falha do check, seguida de execução corrigida e seu escopo.
- Primeiro aprofundamentoR1 selecionava códigos com falha em qualquer data da janela e incluía uma ocorrência fora doTcb alvo no trimestre. Seleção final faz interseção período×código com os nominais eassert de356casos;357 não é o total final.
- Componentes brutos podem terstatusok e tokennull: isso prova presença da conta, não valor calculável. Diagnóstico ajustado para distinguir esse caso de binding ausente, mantendo logs1/2. Nenhum componente financeiro foi corrigido.

## Revisão e encerramento

Revisor independente`review_credit_196`, somente leitura: entrada/contrato; pilotoAPI antes de ampliar; instrumento temporal antes dos componentes; pilotoimportação antes da expansão; todos osmanifests/parts da importação; conclusões econômicas e composição final das duas notas. A revisão distingue ingestão íntegra, possibilidade de indicador e adoção acadêmica. Evidência final/SHA/checks/publicação constam naIssue196.

Exclusões preservadas: fontes externas, BRB, cálculo de novo indicador, união por nome, fusão de perspectivas, promoção do ponteiro e aceite visual193. Limitações dependentes ficam identificadas, sem bloquear o início de toda análise.

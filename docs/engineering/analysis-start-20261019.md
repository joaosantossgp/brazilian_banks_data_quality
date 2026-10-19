# Entrada para a análise da monografia

Contrato: [Pesquisa #198](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/198), articulada à [Entrega #193](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/193). Plano operacional: [fatias e verificações](../superpowers/plans/2026-10-19-analysis-ready-explorer.md). Este documento propõe a sequência de análise; o fechamento acadêmico final cabe a João/orientador. A base é o universo observado inteiro, com seleção vinculada, restante e vínculo desconhecido separados.

## A mesma entrada na próxima tarefa

Descobrir o checkout principal pelo diretório Git comum e autenticar o ponteiro conforme o [comando canônico](local-queries-20261013.md#base-de-indicadores-vigente-entre-tasks). Não escolher pasta por nome/data, não reconstruir a seleção pelo chat e não confundir o HEAD do checkout principal com o do worktree de entrega. Registrar o pin inicial e conferir os hashes das tabelas consumidas.

Nesta tarefa houve migração explícita da entrada de auditoria do ponteiro de 20 métricas (d47 abaixo) para a composição aceita de 27 métricas (f374). Enquanto a promoção controlada da #193 não estiver registrada, **o ponteiro antigo continua selecionando 20 métricas**. O conjunto fixado aqui é identificável independentemente da promoção. Os caminhos abaixo são relativos ao checkout principal, privados e válidos neste computador; o clone Git não distribui os dados.

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

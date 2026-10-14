# Reconciliação de agregados financeiros — dezembro de 2024

[Issue 120](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/120) · complemento da [verificação das cinco fotografias](financial-aggregate-validation-20261013.md), Issue 117.

## Resultado e alcance

As somas observadas dos quatro estoques coincidem **exatamente**, em reais, entre os dados OData locais e os valores brutos usados pelo portal oficial IF.data para dezembro de 2024. A exportação CSV efetivamente baixada também reproduz a apresentação oficial. Isso reforça a evidência de que escala, extração e soma estão corretas neste recorte.

A concordância entre dois serviços do Banco Central não constitui validação por fonte econômica independente. Sete unidades têm valores ausentes em cada estoque, e a correspondência nominal de uma unidade permanece inconclusiva. As somas são de valores observados; não estimam essas ausências nem representam um balanço consolidado do SFN com eliminação de posições entre unidades.

O universo desta conferência é **Conglomerados Financeiros e Instituições Independentes**, `TipoInstituicao=2`, referência `202412`. O recorte diagnóstico não seleciona companhias CVM/B3 nem modifica a população acadêmica. A relação histórica da Issue 108 não foi usada implicitamente para formar uma amostra.

## Fontes, versão e unidades

A base de código/documentação é `201848e21c259c59cafff99f118b3f62e0651897`. Foram preservados os 334 arquivos de entrada já autenticados na Issue 117, além dos cadastros e metadados históricos necessários à ponte entre serviços. Nenhum dado aceito foi sobrescrito ou promovido.

No [portal oficial de 2000–2024](https://www3.bcb.gov.br/ifdata/index2024.html), foram selecionados `12/2024`, o universo financeiro e os relatórios Resumo, Ativo e Passivo. Os três arquivos foram baixados pelo comando **CSV** da própria interface. O portal gera esses arquivos no navegador; não há resposta HTTP de um endpoint CSV a registrar. O cabeçalho informa **R$ mil** e documentos entregues até **13/04/2026**.

| Exportação original | Bytes | SHA-256 |
|---|---:|---|
| Resumo | 224.437 | `b50f82822b75d8eafd76f645271cc0e3132e072f63c2e8682de9257e185c05fc` |
| Ativo | 275.386 | `be65d2550190a5109fb2baa70a0b65214a92e9bdacca783f0fb3c02fb785eb90` |
| Passivo | 288.017 | `2fc8291cebb03993d3b6bba4a5b94e032a16a781337f53bf68eb7693ba93dced` |

Os valores monetários brutos OData são em **R$**, conforme a [documentação `IfDataValores/Saldo`](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao). O CSV exibe inteiros em R$ mil: não permite recuperar os centavos originais. Por isso, a igualdade monetária é verificada entre tokens brutos, com `Decimal` de precisão 120; a concordância do CSV é uma verificação separada da formatação oficial. Não se instituiu tolerância nem se arredondaram os saldos antes da comparação.

## Correspondência nominal e rubricas

Cada CSV contém 1.422 códigos únicos de instituição. Há cabeçalhos de seção, percentuais e 18 subtotais por estoque; eles não são instituições e não são adicionados à soma. Não há linha de total geral na exportação.

Foram demonstradas **1.421 correspondências únicas e injetivas**: 1.352 identificadores institucionais no domínio nativo de oito dígitos e 69 conglomerados pela cadeia cadastral abaixo. Zeros à esquerda são explicitados como normalização do domínio; os identificadores originais permanecem preservados.

> Código do conglomerado financeiro no portal → vínculo financeiro declarado no cadastro individual → CNPJ do líder no cadastro OData → código financeiro OData da mesma data e população.

O cadastro individual serve apenas como evidência de identidade. Nenhum saldo individual foi somado ao financeiro. Por exemplo, o portal `10069`, com vínculo financeiro `00010069`, conecta-se ao líder `60872504` no cadastro individual; o OData declara esse líder para `C0010069`, cujo código coincide com seu vínculo financeiro. Isso resolve a ponte que permanecia aberta para Itaú no diagnóstico anterior, sem equiparar o líder ao conglomerado ou comprovar vínculo societário com um emissor.

**BARU permanece inconclusivo:** o líder `58006471` não está no cadastro individual histórico usado como intermediário. A semelhança entre portal `52656` e OData `C0052656`, os nomes e os montantes coincidentes não foram usados para completar a identidade. O portal informa ativo de R$ 6.772.195,41, crédito de R$ 3.350.347,29, depósitos de zero e PL de R$ 6.243.726,14 para essa unidade; esses valores contextualizam a lacuna, sem certificá-la.

| Estoque | Conta / relatório OData | Relatório do portal |
|---|---|---|
| Ativo total | `78182` / Resumo, 1 | Resumo, 92 |
| Operações de crédito | `78191` / Ativo, 2 | Ativo, 96 |
| Depósitos | `78287` / Passivo, 3 | Passivo, 101 |
| Patrimônio líquido | `78186` / Resumo, 1 | Resumo, 92 |

As fórmulas e os identificadores nativos dos bindings estão preservados no dicionário da execução. Operações de crédito não foi substituída pela carteira classificada do Resumo, e PL contábil não foi equiparado ao patrimônio de referência regulatório.

## Valores e agregações conferidos — fatia A

Foram confirmadas **5.656 igualdades monetárias exatas**, com resíduo máximo zero: 1.414 valores por estoque. As outras 32 posições permanecem inconclusivas: quatro de BARU e 28 ausências, sete por estoque. As ausências têm `null` no OData e `NI` no CSV; não viraram zero. Valores zero observados continuam numéricos.

Os **5.688 tokens** dos três CSV correspondem à apresentação dos valores do portal arquivado: 5.660 numéricos e 28 `NI`. A reprodução executa somente as duas funções puras de formatação extraídas literalmente do HTML oficial pinado. A regra `fid13` divide por 1.000 e usa a apresentação `Number/toFixed(0)` do cliente; essa execução em JavaScript verifica o display, enquanto a aritmética monetária permanece em `Decimal`.

| Estoque | Soma observada portal = OData, em R$ | Diferença em R$ |
|---|---:|---:|
| Ativo total | 17.480.613.833.662,29 | 0,00 |
| Operações de crédito | 6.160.206.235.951,83 | 0,00 |
| Depósitos | 6.106.569.522.039,50 | 0,00 |
| Patrimônio líquido | 1.573.410.516.537,41 | 0,00 |

A igualdade das somas completas observadas é numérica; a ponte nominal ainda tem a lacuna de BARU. Não classificar essa coincidência agregada como prova adicional de identidade.

Os **72 subtotais** dos quatro estoques reproduzem a apresentação oficial. Para a comparação com OData, **36 têm correspondência nominal e todos os valores numéricos**; os outros 36 conservam cobertura inconclusiva por ausências e/ou BARU. Vinte destes últimos coincidem na soma observada, mas essa coincidência não certifica completude. Os 16 que incluem BARU mantêm a parcela sem ponte separada. As dimensões TCB, SR, TD e TC são formas alternativas de agrupar a mesma população, não parcelas para somar entre si.

Há uma particularidade relevante de SR: o CSV pode ocultar a classificação na linha, enquanto o agregador oficial usa o campo cadastral nativo `c12`. Somar apenas o SR visível perderia, no grupo S5, R$ 179.715.840.334,62 de ativo, R$ 16.580.200.000,00 de depósitos e R$ 15.789.347.846,79 de PL; o crédito desses casos é zero. A regra de apresentação e o metadado do filtro comprovam a diferença. Isso não justifica preencher automaticamente o SR ausente no OData.

## Referências publicadas e compatibilidade

Foram examinados três documentos oficiais, dentro da busca finita autorizada: [Relatório de Estabilidade Financeira de abril de 2025](https://www.bcb.gov.br/content/publicacoes/ref/202504/RELESTAB202504-refPub.pdf), seu [anexo estatístico](https://www.bcb.gov.br/content/publicacoes/ref/202504/RELESTAB202504-refAnexoEstatistico.xlsx) e a [nota monetária e de crédito de janeiro de 2025](https://www.bcb.gov.br/content/estatisticas/hist_estatisticasmonetariascredito/202501_Texto_de_estatisticas_monetarias_e_de_credito.pdf).

| Referência | Uso possível e limite |
|---|---|
| REF, p. 16, nota 9; p. 17, gráfico 1.2.1.1.a | Captação do sistema bancário no perímetro financeiro: candidato parcial para depósitos. Exige conferir população e componentes. |
| REF, p. 75 e pp. 101–102, concentração | Perímetro prudencial, ativo ajustado e outra definição de depósitos. Percentuais de concentração não validam os quatro estoques absolutos. |
| Nota monetária, p. 1, seção 2 | Crédito do SFN de aproximadamente R$ 6,4 trilhões. A população e a rubrica não foram ponteadas à conta `78191`; referência contextual. |

Não foi estabelecida, nessa busca, uma referência economicamente independente e diretamente compatível com os quatro agregados. Isso não prova inexistência de fonte. O REF também pode reutilizar informações regulatórias da mesma origem; publicação distinta não garante independência econômica.

Os documentos foram recuperados em 14/10/2026. O PDF da edição abril de 2025 informa `Last-Modified` em 28/04/2025; o XLSX atualmente servido informa **06/08/2026**. A edição do relatório, a última modificação HTTP, a recuperação e o corte de entregas do portal são tempos diferentes. Não foi demonstrado que os arquivos representam o mesmo vintage, nem que revisões expliquem qualquer parcela da diferença.

Âncoras das fontes: PDF REF `a4e8b6488ea2d484ea4a98e2f620e2df66ec70e26c47f1000df01e28217077ec`; XLSX `673126bdf23a43b09ccc1676b76ac647ad62ab6fb45d0dc92037526fd01437d0`; nota monetária `c8dac708a38218952aabca93242ea509424f3477df5d153d5a65967a36fb7b87`. O recibo privado conserva URLs, recuperação UTC, status, headers e bytes dos três sucessos HTTP 200. Uma tentativa anterior de localização retornou 404; seu diagnóstico foi preservado, mas não há corpo/headers desse insucesso, portanto não se alega proveniência HTTP integral dele.

## Adaptação do agregado bancário — fatia B

A nota 9 do REF define o sistema bancário da análise de liquidez pelas classes de bancos comerciais, múltiplos, caixas, bancos de câmbio e de investimento, no perímetro **financeiro**. O filtro nativo do portal descreve essas classes como **B1 e B2**. Esse fundamento permite um recorte diagnóstico mais próximo do REF, sem comprovar a composição nominal exata da publicação.

Aplicando a classificação nativa de dezembro de 2024, o recorte contém **128 unidades: 97 B1 e 31 B2**. Todas têm ponte nominal única e dados numéricos nos quatro estoques e nos seis componentes de depósitos: **1.280 pares monetários portal–OData exatamente iguais**. As 1.294 unidades excluídas, de B3S, B3C, B4, N1, N2 e N4, permanecem identificadas no ledger; BARU e as sete ausências por estoque pertencem a N1 e continuam explícitas no diagnóstico global.

| Estoque | B1+B2, portal = OData, em R$ | Demais classes, valores observados em R$ |
|---|---:|---:|
| Ativo total | 14.541.425.737.786,89 | 2.939.188.095.875,40 |
| Operações de crédito | 5.263.154.357.639,79 | 897.051.878.312,04 |
| Depósitos | 5.369.376.570.776,37 | 737.192.951.263,13 |
| Patrimônio líquido | 1.112.968.681.580,24 | 460.441.834.957,17 |

Em cada estoque, a soma B1+B2 mais as demais classes reproduz exatamente o agregado observado da fatia A. Não foram acrescentados saldos de instituições integrantes aos de seus conglomerados. Os 128 códigos e suas contrapartes são únicos. Há 79 registros classificados como conglomerado e 49 como independentes; entre os primeiros, 55 vínculos financeiros preenchidos são distintos e 24 estão vazios. Preservar esses vazios limita a afirmação ao grão de reporte nativo, sem certificar independência econômica irrestrita ou uma lista nominal do REF.

### Depósitos: o que pode ser comparado

O catálogo nativo distingue vista `78282`, poupança `78283`, interfinanceiros `78284`, prazo **`78286`**, conta pré-paga `110560` e outros `78285`. Prazo corresponde ao COSIF `41500002`; `78285` é **outros depósitos**, não prazo. O total `78287` corresponde a `41000007`. O binding efetivo, sua fórmula e seu contexto foram conferidos antes do cálculo.

No anexo do REF, a planilha `Graf 1.2.1.1.a` identifica prazo, poupança, depósitos judiciais e vista em B6/C6/H6/I6. A última linha, 17, representa dezembro de 2024: A17 contém “Dez”, após A16 “Jun 2024”, e o gráfico da p. 17 confirma o ano. Foram lidos os tokens literais do XML original, sem conversão por ponto flutuante. O gráfico informa **R$ bilhões**; dividir esses tokens por um bilhão reproduz seus rótulos 2.646 / 1.025 / 387 / 279. Isso demonstra a escala de apresentação; a célula do XLSX não tem metadado explícito de unidade.

| Componente por nome | IF.data B1+B2 | REF | Diferença aritmética IF.data − REF |
|---|---:|---:|---:|
| Prazo | 3.532,650 | 2.646,063 | 886,587 |
| Poupança | 1.052,864 | 1.024,543 | 28,321 |
| Vista | 461,929 | 279,105 | 182,824 |

**R$ bilhões, apresentação arredondada a três casas;** cada diferença foi calculada antes do arredondamento, com os tokens originais. As três comparações são **inconclusivas economicamente**, apesar de a subtração ser reproduzível. O REF descreve instrumentos de captação, mas não fornece a ponte completa entre seus instrumentos e as fórmulas COSIF selecionadas, nem foi obtida uma lista nominal de unidades que comprove a mesma população. Geografia e vintage também não foram reconciliados.

Os três componentes nativos somam R$ 5.047.443.253.131,00; os três tokens de mesmo nome no REF somam R$ 3.949.711.016.935,15664. A diferença de **R$ 1.097.732.236.195,84336** permanece sem decomposição causal demonstrada. Não a classificar como erro de extração, dupla contagem ou reapresentação.

Interfinanceiros, conta pré-paga e outros depósitos somam, no IF.data B1+B2, R$ 321.933.317.645,3699990763. Essa é a parcela nativa fora do comparativo de três nomes; não significa que esteja integralmente fora do REF. A identidade entre o total nativo e seus seis componentes conserva um resíduo de **R$ 0,0000009237**: Itaú `C0010069`, +R$ 0,000001; ABC `C0052072`, −R$ 0,0000000763. Ele já está nos tokens originais, não foi arredondado e sua causa não foi atribuída.

Depósitos judiciais aparecem separadamente no REF, com token R$ 387.497.776.272,76001. Não foi demonstrado se e como se sobrepõem a vista/prazo no IF.data; somá-los novamente para aproximar os totais não constitui uma reconciliação aceita. A nota 10 da p. 17 trata da estimativa **líquida** do gráfico 1.2.1.1.c; não foi aplicada automaticamente ao estoque bruto do gráfico 1.2.1.1.a.

## Interpretação e próximos limites

A conferência fortalece a confiança nos números financeiros de dezembro de 2024: valores brutos, escala, apresentação CSV e somas observadas concordam entre portal e OData. O recorte B1+B2 também é reproduzível e tem cobertura completa nas dez medidas selecionadas. Isso permite explorá-lo como diagnóstico com composição explícita.

A adaptação do perímetro, sozinha, **não fechou a comparação com o REF**. Permanecem abertas a ponte nominal da população publicada, as definições de instrumentos, a posição doméstica/exterior e a compatibilidade temporal das versões. Não há uma parcela residual atribuída a cada causa. Ativo, crédito e PL tampouco receberam um benchmark externo compatível nesta busca. A conclusão preserva essas lacunas, sem mudar números ou transformar uma hipótese em método da monografia.

## Reprodução, revisão e entrega

Evidência privada na raiz primária de dados: `.scratch/financial-aggregate-reconciliation-20261014/`. Os originais CSV/PDF/XLSX, recibos, cadastros intermediários, scripts e ledgers têm hashes próprios e não integram a publicação Git. A nota é a única adição pública da Issue 120, no destino canônico `docs/engineering/`; não altera software, dados aceitos ou documentos acadêmicos.

| Artefato privado | Responsabilidade |
|---|---|
| `official-export-manifest.json`, três `official-*.csv` | Exportações originais, seleção, unidade, corte e hashes |
| `a_results.json`, `a_bridge.csv`, `a_ledger.csv`, `a_groups.csv` | Correspondência nominal, valores, apresentação e cobertura dos subtotais |
| `a_filter_receipt.json`, `a_filter202412.json` | Único GET adicional de filtro, derivado do catálogo, HTTP 200; prova do agrupador SR |
| `sources_provenance.json`, `sources/`, `ref-page17.png` | Fontes publicadas, recibos, XML e inspeção visual |
| `b_results.json`, `b_composition.csv`, `b_reconciliation.csv` | Recorte nominal, pontes entre classes, componentes, diferenças e limites |
| `review_a.md`, `review_b_sources.md`, `review_b.md` | Pareceres independentes por fatia |
| `a-artifact-snapshot.json`, `b_snapshot.json` | Checkpoints congelados das fatias revisadas |

Na raiz primária, os comandos privados de cálculo foram:

```powershell
.venv/Scripts/python.exe .scratch/financial-aggregate-reconciliation-20261014/a_script.py
.venv/Scripts/python.exe .scratch/financial-aggregate-reconciliation-20261014/a_report.py
.venv/Scripts/python.exe .scratch/financial-aggregate-reconciliation-20261014/b_validate.py
```

São scripts finitos de pesquisa, não ferramentas de produção. Uma reexecução escreve os outputs privados e seus horários; conservar o checkpoint antes de reproduzir. A reprodução independente usou scripts próprios `review_*`, sem executar os writers sobre os artefatos congelados. Os cálculos monetários usam `Decimal` 120; B usa uma thread e 256 MB em DuckDB, com traps de arredondamento/conversão float. Os 334 pins protegidos e os inputs efetivos foram conferidos antes e depois.

Na fatia A, um formatter transcrito incorretamente foi substituído pelas funções literais oficiais, e a cobertura dos subtotais passou a distinguir concordância observada de completude. O diagnóstico inválido foi preservado como tal; não é divergência da fonte. O checkpoint inicial foi conservado, sendo o definitivo aprovado após o congelamento. Em B, seleção explícita de bindings e descrição de vínculos vazios corrigiram asserções preliminares sem alterar dados.

A revisão independente A confirmou 1.421 pontes, 5.656 igualdades monetárias, 5.688 tokens CSV e 72 subtotais, mantendo as lacunas. A revisão B reproduziu 1.280 pares, 220 linhas de composição, 11 diferenças aritméticas do ledger, os tokens/escala do REF e os hashes protegidos. Ambas aprovaram **o diagnóstico e seus limites**, sem certificar equivalência econômica com o REF. A composição final, SHA entregue, publicação, checks e integração têm registro verificável na Issue 120.

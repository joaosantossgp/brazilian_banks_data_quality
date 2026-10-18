# L2 financeiro: diagnóstico completo de 2010–2024

[Issue140](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/140),16/10/2026. João autorizou o aviso de coberturaC4 e o diagnósticoL2 emtodos60trimestres, sem recalcular toda a base. O diagnóstico não modifica fórmula, valores, elegibilidade ou classificações; somente o avisoC4 foi acrescentado ao explorador.

## Resultado e interpretação

**Não foi encontrada perda de valores ou seleção incorreta das contas doL2 nos controles documentados.** A fórmula vigente é `(cash + interfinancial) / sight_deposits`, isto é, disponibilidades+aplicações interfinanceiras de liquidez sobre depósitos à vista, no próprio perímetro/data.

| Estado entre2010–2024 | Ocorrências de unidade-trimestre |
|---|---:|
|L2 disponível, depósitos à vista positivos|51143|
|Depósitos à vista observados zero|37639|
|Componentes nulos na fonte|694|
|Total identificado|89476|

Não há denominadores negativos ou bindings ausentes desses cinco componentes nos contextos próprios examinados. Todas as37639posições zero permanecem com aplicabilidade desconhecida, e todas as694nulas também. Não se converteu zero em proibição de captar ou não aplicabilidade. As694posições têm **os cinco campos examinados nulos**, incluindo AT e depósitos totais; não são apenas falhas isoladas do denominadorL2.

A fórmula mede uma relação específica de liquidez frente a depósitos à vista, não a liquidez universal de qualquer negócio financeiro. A [nota de fontes](ifdata-l2-sources-20261016.md) reúne Assafp334, conforme leitura já aceita na111, e normas/documentaçãoBCB sobre modalidades de captação e limites. A referênciaAssaf é reaproveitada, não nova leitura. L2 não éLCR.

**Recuperação direta demonstrada: zero.** As ausências/zeros observados não se resolvem liberando uma proteção geral ou copiando outra rubrica. Trocar depósitos à vista por depósitos totais ou obrigações diferentes mede outra relação e exige método próprio. Licença/subtipo/perímetro e vigência podem fundamentar não aplicabilidade em uma etapa posterior, sem fabricar valor.

## Cobertura ao longo da janela

Todos os60trimestres têm resultados agregadosL2; a questão é cobertura de unidades, não interrupção universal da série.

| Referência | Unidades presentes | L2 disponível | Denominador zero | Componentes nulos | Cobertura do AT conhecido |
|---|---:|---:|---:|---:|---:|
|1T2010|1817|1072|718|27|86,14168978%|
|4T2010|1786|1051|702|33|84,63242537%|
|4T2015|1508|900|600|8|85,61375053%|
|4T2017|1401|825|574|2|84,60971247%|
|4T2020|1316|738|566|12|86,33174988%|
|4T2024|1422|676|739|7|85,96588287%|

Cobertura conhecida mínima84,60971247% em4T2017 e máxima87,38119668% em2T2020. Foi conferida por soma exata dos tokensAT (Fraction/Decimal) das unidades elegíveis dividida pela somaAT conhecida de todas as unidades identificadas; o arredondamento é de apresentação. AT desconhecido é separado. Não certifica cobertura do total econômicoSFN nem ausência de sobreposição entre unidades reportantes do universo observado.

Em4T2024, a amostra das24 tem **17/20unidades** e **21/24companhias** elegíveis, com99,61139641% doAT conhecido da amostra. Restante:659/1402unidades e69,53601054% doAT conhecido desse complemento. O total inclui amostra e restante; não somar razões/percentuais ou inferir que a baixa cobertura numérica equivale a baixa cobertura econômica.

## Segmentações e padrões de captação

Contagens porTcb em toda a janela, por unidade-trimestre:

| Tcb | Depósitos à vista positivos/L2 disponível | Denominador zero | Nulos |
|---|---:|---:|---:|
|B1|5452|395|6|
|B2|217|1874|1|
|B3S|44832|15232|451|
|B3C|358|1820|11|
|B4|69|171|0|
|N1|202|7686|100|
|N2|0|9020|100|
|N4|8|1419|13|
|Tcb ausente|5|22|12|

Não são regras de autorização nem exclusão. N4comL2disponível em8posições, N1em202 eB2em217 reforçam a necessidade de conferir o perímetro/unidade antes de inferir modelo operacional pelo tipo. B3S contém subtipos depositários e capital-e-empréstimo; não excluir a família inteira. Categorias positivas não certificam licença.

Nas37639posições comdenominadorzero:

- 27864 têm numerador positivo e depósitos totais zero;
- 9428 têm numerador positivo e depósitos totais positivos;
- 319 têm numerador zero e depósitos totais zero;
- 28 têm numerador zero e depósitos totais positivos.

Logo, **9456posições** têm depósitos totais positivos, mas depósitos à vista zero. A existência de funding/ativos líquidos não cria o denominador específico doL2. O CSVsegment_coverage permite cruzarTcb/Td/Tc/Sr/SrAnalitico/SegmentoTb por período, sem inferir subtipos pela ausência.

Há395zerosB1 distribuídos por33códigos; não justificá-los em bloco como impossibilidade de captar. Dois códigos têm zero nos60trimestres:09274232 eC0051413. Os rótulos de09274232 mudam na série (Natixis/StateStreet); manter código/data, sem afirmar continuidade econômica apenas por código. Outros padrões incluem C0051767 em48posições entre2T2011–4T2024, sem presumir continuidade sem lacunas. unit_windows e transitions conservam todas as posições e mudanças.

## Unidades representativas e amostra

Em4T2024, exemplos deATpróprio conhecido fora doL2 por depósitos à vista zero:

| Unidade reportante | Tcb | AT na data |
|---|---|---:|
|33657248 — BNDES|B4|R$835928013371,46|
|C0052058 — Nubank|N1|R$176097862319,76|
|01425787 — RedecardIP|N4|R$128999092769,67|
|01027058 — CieloIP|N4|R$120211374935,14|
|18236120 — NuPagamentosIP|N4|R$94467214159,25|

Esses valores são dos perímetros reportantes, não uma lista para somar: conglomerados/IPs podem ter vínculos ou sobreposição, e não se afirma equivalência entre unidade e companhia. O BNDES está presente na base; fica fora desse indicador porque o denominador observado ézero. Isso é uma limitação de alcance, sem juízo de desempenho.

Na seleção das24, PortoSeguro(C0051444) temzero nos60trimestres. BRPartners temzero em34posições C0051822/2T2012–3T2020 e17posições13220493/4T2020–4T2024, sem inventar vínculo anterior à disponibilidade. A companhia selecionadaDM tem unidades91669747 em51posições1T2010–3T2022 eC0052357 em9posições4T2022–4T2024, todoszeros; os rótulos nativos e os vínculos da seleção são fatos separados. Não confundir o rótulo fonteFinansinos do primeiro código com prova de controlehistóricoDM.

**BRB FinanceiroC0031976/3T2022:** os cinco componentes examinados estão nulos. A lacuna coincide temporalmente com a exceção doC4prudencial139, mas os códigos/perímetros são próprios; não copiar valores entre perspectivas. É candidato a busca alternativa oficial curta, se necessária, para toda a ocorrência afetada e métricas dependentes, sem interpolação ou pesquisa geral.

## Fonte sem identidade e escopo de fidelidade

Foram autenticadas60partições financeiras e60GZ originais da captura de11/10/2026. Conferidas447445linhas selecionadas para:

| Componente | Relatório/conta | Descrição literal |
|---|---|---|
|Disponibilidades|2/78188|[11000006]|
|Aplicações interfinanceiras|2/78189|[12000005]|
|Depósitos à vista|3/78282|[41100000]|
|Depósitos totais|3/78287|[41000007]|
|AT de cobertura|1/78182|[10000007] + [20000004]|

Os cinco contextos mantêm nomes/descrições ao longo das60datas, com89489linhas selecionadas porcomponente incluindo as não identificadas. Comparação fontebruta→Parquet considera9campos literais de identidade/relatório/conta/metadados, equivalência exataDecimal doSaldo e hash/posição deorigem. Equivalência de valor não é identidade lexical.

**65linhas selecionadas têm CodInst nulo**, emnovedatasde3T2019–3T2021:5em201909/201912/202003/202006/202109 e10em202009/202012/202103/202106. Foram preservadas emunkeyed_source_rows, comConta/Saldo/posição/hash. Não se inventou identidade nem se escolheram valores entre códigosnulos duplicados. Não são65instituições e não pertencem ao denominador de unidades identificadas. Essa incerteza limita o universo observado e não pode ser declarada resolvida por preenchimento de cadastro.

Para asunidadesidentificáveis:447380tokens decomponentes conferidos contra os armazenados;89476estados, aplicabilidade e três fraçõespointL2 reconciliados; para os51143resultados disponíveis, numerador e denominador armazenados conferidos exatamente sem divisão/geração de novos indicadores. O contextoAT selecionado éanalysis_period=period, separado das reutilizações do estoque como abertura de médias futuras. Transporte/seleção/estado sem divergências nos checks; não certifica qualidadeeconômica da fonte/licença/perímetro/continuidade.

## AvisoC4 no explorador — fatiaA

O novo aviso aparece somente emPrudencial/C4, distinguindo datas anteriores2015, comparação pré2018 e a quebra2018–2024. Explica ausêncianativa, hipótesePRS5, S5≠provaindividual, exceções eCP≠PR. Pin139 visível; nenhuma classificação unitária ou valor foi alterado.

`aplicar-aviso-c4-explorador.py` preserva o packed inteiro **byte por byte** da versão138, isto é,todas295404linhas/metadados anteriores. HTMLSHA256 `29c46a4b0effe3eca6d6d480fdcec0e45446d830aba8bf9d2f07d0dab2c88f12`, reciboexplorador-c4-aviso-recibo.json. Seischecks específicos+oitoregressõesdesktop PASS, imageminspecionada e revisãoindependenteA PASS. Semverificação de celular. Não foiacrescentado avisoL2 nesta tarefa.

## Reprodução, artefatos e próximo passo

```powershell
python scripts/diagnose-ifdata-l2.py --root "<data/curated>" --raw "<data/raw/ifdata-odata-20261011>" --output "<novo destino>"
```

Saída `data/curated/ifdata-l2-diagnostic-20261016-run1`, contratoifdata-l2-diagnostic-v1, manifestoSHA256 `bc1e41dad042c2a9f19f917533f48137931ef61f50db833e5591ceff65409889`. SeteCSVs:unit_diagnosis,period_coverage,segment_coverage,source_definitions,transitions,unit_windows,unkeyed_source_rows. Execução aceita84,75s; não confundir com o tempo de cálculo de um indicador. Foram lidos originais60trimestres para conferência, sem build/recalc/reagrupamento de indicadores.

Pins principais:base130 `b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`; financial `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095`; Sr136 `a8e09826ec1b50becab01a844fa4954762a71a6fdfd60b245be53ebce372a3be`. Manifestoreúne hashes deentradas/saídas/produtor.

Consulta reproduzível para concentração, preservando monetários textuais:

```sql
SELECT Tcb, diagnostic_class, count(*) AS unit_periods
FROM read_csv('<saida>/unit_diagnosis.csv', all_varchar=true)
GROUP BY ALL ORDER BY Tcb, diagnostic_class;
```

CoberturaAT se reproduz usandoFraction(Decimal(tokenAT)) dosregistroscomATconhecido, somando numerator somente result_status=ok e dividindo pelo totalconhecido, porperíodo/coorte. Sem limiar ou exclusão adicional.

Próximoencaminhamento proposto:explicar noexplorador o alcanceL2 e depósitoszero, mantendoaplicabilidade desconhecida; examinar apenas exceçõesrepresentativas comalternativaoficialdatada (BRB202209), emvezde perseguirtodoszeros. Indicadorcomplementar abrangente exigiria decisão/fundamentação própria, sem substituirL2. Não alterado nesta entrega.

Revisão independente B/conclusões/composição final PASS, sem achados materiais, registrada na Issue140. CoberturaAT reproduzida independentemente com Fraction/Decimal; ajuste editorial dos quatro itens da lista aplicado. Compilação/diffcheck e hashes core/perfil/benchmark protegidos conferidos. Sem commit/PR, nova coleta IFdata, Goal, Word, Project3 ou outro computador.

# Cobertura temporal e diagnóstico do ROA de 12 meses em 1T2019

## ROA e ROE Individual: janela completa de 2019 — Issue 138

A [Issue 138](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/138) aplica a ponte do lucro a **R1/R2, últimos 12 meses, Individual, 201903/201906/201909**. A inspeção da janela incluiu os trimestres efetivos e dezembro: estes já tinham resultados e foram preservados. Não houve reconstrução integral.

### Evidência e limite da ponte

A mesma troca literal de conta de remuneração do capital ocorre no lucro nativo Individual: antes de março, `[70000009]+[80000006]-[81955002]`; depois, `[70000009]+[80000006]-[81956001]`. A fundamentação normativa e os limites contábeis são os da ponte financeira documentada abaixo. Entretanto, todos os valores, bindings e cadastros desta entrega são **TipoInstituicao3**, com namespace `individual:`, sem importar valores ou provas Tipo2. O teste rejeita evidência financeira colocada no contexto Individual.

O lucro publicado conserva tributos e não recebe nova dedução/adição de JCP. AT e PL permanecem estoques nativos; não há ajuste contrafactual de regime. Oito partições nativas, 201803–201912, foram autenticadas. Os contextos de AT e PL mantêm suas definições. Numeradores e pesos temporais são os mesmos das expressões e médias trapezoidais da seção ROE financeiro abaixo, aplicados aos próprios valores Individual.

IPs exigem JCP observado zero e LLResumo=DRE em cada dependência de lucro consumida. Ausência, null, duplicidade ou valor não zero não equivalem a zero. Há cinco candidatas em março e sete em junho/setembro; elegibilidade ainda depende dos estoques e demais inputs. Stone, código16501555, apresenta JCP201812 de −R$32.012.000,10 e permanece incompatível nos seis recortes. Não foram observados consórcios N3 na população Individual admitida desses três alvos; isso não prova inexistência no SFN. Não se retroage a Circular3937/2019.

### Resultados e cobertura

Percentuais de 12 meses, razão das somas dos componentes elegíveis:

| Período | ROA sistema observado | ROE sistema observado | Unidades elegíveis / presentes | Cobertura do AT conhecido |
|---|---:|---:|---:|---:|
|1T2019|1,7609712232%|15,8311365900%|1473/1494|99,6732828814%|
|2T2019|1,8400749180%|16,5937668743%|1457/1479|99,6088002205%|
|3T2019|1,8951122528%|16,7990973408%|1444/1472|99,4639103488%|

| Período | Amostra: ROA / ROE; unidades | Restante: ROA / ROE; unidades | Vínculo desconhecido: ROA / ROE; unidades |
|---|---|---|---|
|1T2019|2,015990% / 16,173389%;89/90|1,303120% / 12,945095%;139/141|1,422705% / 15,941194%;1245/1263|
|2T2019|2,154884% / 17,581023%;88/89|1,262279% / 12,627258%;141/143|1,429879% / 15,484591%;1228/1247|
|3T2019|2,172011% / 17,464308%;87/88|1,368047% / 13,674461%;141/144|1,543920% / 16,219977%;1216/1240|

As 24 companhias têm ao menos uma unidade vinculada elegível em cada data. Isso não implica cobertura integral de seus negócios: Banco Hyundai Capital Brasil, código30172491, é uma unidade da amostra com binding/histórico insuficiente nas três janelas. O grupo de vínculo desconhecido permanece separado do restante. Individual não consolida os membros de um grupo e não pode ser somado aos conglomerados ou tomado como um agregado SFN sem sobreposições.

Lacunas por métrica: março21 (14 bindings ausentes,6 nulls,1 incompatível); junho22 (18 bindings,3 nulls,1 incompatível); setembro28 (24 bindings,3 nulls,1 incompatível). A ponte não elimina controles de abertura, null, definição ou denominador zero. PL médio negativo ocorre em2/3/3 unidades, sinalizado; AT médio negativo, em zero. Os extremos de ROE com PL pequeno/negativo ficam preservados e não são interpretação automática de bom desempenho.

### Reprodução e proveniência

Fonte nativa `data/curated/ifdata-odata-20261011/individual`, manifesto `484a0e30269d0e830ef254958a408fe8e797011aa24b6b23ae29ea3d399f91fc`. Base e cadastro usam os pins das entregas anteriores. Diagnóstico privado `diagnostico-individual-2019.json`, SHA256 `c4d534007a0aeb5555baf240f660d6648f94e1f1bdc7dd2cb58daa3090f4e0c8`.

Saídas novas em `data/curated/ifdata-selective-individual-{R1|R2}-{PERIODO}-20261016-run1`, sete tabelas JSON/CSV/Parquet por pacote:

| Período / métrica | Manifesto SHA256 | Tempo |
|---|---|---:|
|201903/R1|`9a93ad26a9995649df85ae4f64ea79de337e50b1b625744d9a72f2523053a13c`|7,73s|
|201903/R2|`0508f77980da1398507ed8a5dc6061a6fb488f799ed25e9106b34842fa174e13`|8,53s|
|201906/R1|`02d9a60b37d56cff5c6460cdf90c228b09b1b8666b4003d10ad230ad889b0662`|7,67s|
|201906/R2|`8246f446aaa9ba3d493608e3182d99dba487a2f8bc3038d3df0f5427ae353a93`|8,32s|
|201909/R1|`05b8dd45d265e69b30e1e0848e5ec2250f8e89d069cf2ba3ec8ea53c0b2389e2`|7,65s|
|201909/R2|`e90e9d71fe535bd1956feaf1704824efc49a071b07fd12c7a03992f847e36fc0`|8,19s|

Reusar o comando `recalculate-universe` abaixo com `--dataset individual --metric R1` ou `R2 --horizon ttm`, cada uma das três datas e destino novo; executar a janela inteira como lote. Não é necessário rodar a base completa. O seletor continua finito; a extensão não autoriza outra janela/métrica/perspectiva.

### Explorador e validação

**Aceite final138:** 27 testes pertinentes PASS; 40 verificações desktop PASS, sem erros de execução. Revisão independente A/B/C e composição final PASS, sem achados materiais. Conferidos novamente hashes do núcleo/perfil/nota protegida e diff sem erros de whitespace.

A projeção `aplicar-individual2019-explorador.py` autentica os seis pacotes e substitui914 linhas dos alvos, incluindo Tcb/Td/Tc/Sr/SegmentoTb/SrAnalitico. As294490 linhas fora dos alvos permanecem exatamente iguais. HTML SHA256 `c028e720ed1c067def11aaded22bc78bf3ec7b511b6f27a4d5b0a9c07e2adb98`; recibo `explorador-individual2019-recibo.json`. Após exportação antiga, aplicar as projeções133→134→136→137→138.

SrAnalitico Individual é idêntico ao Sr nativo:4445 unidades-períodos dos alvos conferidas, sem atribuição derivada/conflito. Por isso a apresentação replica as linhas Sr corrigidas para SrAnalitico, sem reexecutar o reagrupamento136. Atributos e classificações originais permanecem intactos.

TDD: os seis contextos Individual falharam antes da ampliação; os dez testes seletivos passam, incluindo namespaces/tipos e exceções. Revisão independente A aprovou código/escopo antes do lote; B autenticou seis manifestos/126 arquivos e reproduziu **8748 cálculos exatos**, seus numeradores, médias de AT/PL, composição e somas das quatro coortes. A verificação desktop acrescenta dez verificações Individual (seis alvos, dezembro preservado, quatro coortes e CSV), além das30 verificações anteriores. Revisão final da apresentação/documentação registrada na Issue138. Entrega local, sem commit/PR; o núcleo e o perfil congelado permanecem protegidos.



## ROE financeiro: janela completa de 2019 — Issue 137

João autorizou investigar a janela inteira do ROE financeiro em 2019 e aplicar a ponte do ROA quando sustentada pela evidência, sem reconstruir a base. A [Issue 137](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/137) implementa **R2/TTM/Financeiro em 201903, 201906 e 201909**. O diagnóstico incluiu 201812–202003: ROE trimestral em todo 2019 e TTM de dezembro já tinham resultados e permanecem exatamente iguais. A primeira entrega ROA e suas extensões estão preservadas nas seções históricas abaixo.

### Aplicabilidade da ponte e patrimônio líquido

ROA e ROE usam o mesmo LL nativo. A ponte semântica revisada libera somente sua compatibilidade entre as fórmulas anteriores/posteriores a 201903. Para ROE, o denominador passa a ser **PL médio nativo**, sem ajuste de JCP, tributos ou contrafactual de regime. A mudança de registro da remuneração pode afetar os saldos publicados; isso não autoriza corrigi-los para simular outro regime.

PL/Resumo1/Conta78186 mantém a composição literal `[60000002] + [70000009]+ [80000006]`, `window_rule=stock`, compatibilidade `d88656f43073dada1e5cfc420e0a4a4bdae8e6b6bc542eb907de8be17c6d2760`. Oito partições 201803–201912 autenticadas confirmaram contexto e unicidade dos bindings; o perfil reconhece esse mesmo contexto nos 60 períodos. Não se identificou quebra adicional de definição de PL que impedisse usar a ponte do LL no ROE. Isso não certifica equivalência com ROE CVM/IFRS, PL ajustado ou continuidade societária pelo nome/código.

Mantêm-se as condições das IPs: JCP observado zero e LLResumo=DRE nos inputs de lucro efetivamente consumidos. Cinco IPs atendem à ponte em março; sete em junho/setembro. Acesso ainda não tem o estoque de abertura necessário em junho. Stone permanece incompatível nas três janelas por JCP201812 não zero. Não se retroage a Circular3937/2019.

A média de PL usa os cinco estoques trimestrais, aproximação trapezoidal ponderada por dias. Os pesos das quatro diferenças de datas são 91/92/92/90 em março, 92/92/90/91 em junho e 92/90/91/92 em setembro, totalizando 365 dias. Numeradores independentes equivalentes:

- 1T2019: LL201806 − LL201803 + LL201812 + LL201903;
- 2T2019: LL201812 + LL201906;
- 3T2019: LL201812 − LL201809 + LL201906 + LL201909.

São conferências da soma dos quatro trimestres efetivos; os inputs intermediários usados nas derivações mantêm seus controles, mesmo quando se cancelam nas expressões acima. PL nulo, estoque de abertura ausente, definição incompatível ou média zero não são liberados pela ponte. Média negativa conserva o sinal e a flag existente.

### Resultados aceitos localmente

| Período | ROE sistema observado | Amostra das 24 | Restante | Elegíveis / presentes no sistema | Cobertura do AT conhecido |
|---|---:|---:|---:|---:|---:|
|1T2019|15,8610171222%|16,4568368801%|15,0475006743%|1324/1345|99,6647043829%|
|2T2019|16,4514861303%|17,7931257465%|14,6614741968%|1307/1330|99,5999092383%|
|3T2019|16,9343176209%|18,0544166663%|15,4657702444%|1293/1322|99,4698170863%|

As 21 unidades ligadas às 24 companhias têm ROE elegível nas três datas. Lacunas restantes: março21 (14 bindings, 6 nulls, Stone); junho23 (19 bindings, 3 nulls, Stone); setembro29 (25 bindings, 3 nulls, Stone). Cobertura econômica continua usando AT próprio conhecido, enquanto PL médio é o denominador do ROE. Há respectivamente 6/3/4 unidades com AT contemporâneo desconhecido; cobertura do conhecido não certifica cobertura do total.

Há **1/2/2 casos de PL médio negativo**, distintos de contagens de estoque negativo no último dia. Os códigos são 29283884 em março; 29283884/71677850 em junho; 50657675/71677850 em setembro. Em setembro, 71677850/Frente Corretora tem PL médio exatamente `-4507303/18250` (aproximadamente −R$247) e ROE em fração `26206.571949456249...` (aproximadamente 2,62 milhões%). O extremo reproduz os tokens, pois o denominador médio é pequeno e negativo. Não se arredondou a média, eliminou a unidade ou criou limiar automático. `negative_denominator` e `non_convex_denominator_weights` permanecem explícitos; um ROE positivo com prejuízo/PL negativo não representa automaticamente bom desempenho. O agregado usa razão das somas, sem calcular média simples dos ROEs individuais.

### Pacotes e execução seletiva

O seletor existente passou a aceitar somente R1 ou R2, TTM, Financeiro, nas três datas revisadas. Para R2, consulta também PL78186 e conserva AT para cobertura. O helper da ponte, o núcleo `ifdata_analysis.py` e o perfil congelado não foram alterados. Saídas novas, contrato `ifdata-selective-analysis-v1`, sete tabelas JSON/CSV/Parquet:

| Saída em data/curated | Manifesto SHA256 | Tempo |
|---|---|---:|
|ifdata-selective-roe-201903-20261016-run1|`d5081eef68e5f2a5b0a9d133fad68359de97962201d49faab42d5face07a31c6`|7,90s|
|ifdata-selective-roe-201906-20261016-run1|`eaaebf79d3ea6b34218806f90bf8ba34ba8f20ec5c82ec272762ad4d5af9db02`|8,07s|
|ifdata-selective-roe-201909-20261016-run1|`a2d194e1eff4ccfd1f5db158fac8487b80537718928527e34ca15738e217c50e`|8,09s|

Reprodução: mesmo comando `recalculate-universe` documentado abaixo, com `--metric R2 --horizon ttm --dataset financial` e cada uma das três datas; executar como lote da janela inteira, com destinos novos. Os pins da base e da fonte financeira continuam os mesmos da entrega ROA. O diagnóstico primário privado `diagnostico-roe2019.json` tem SHA256 `d79c0c352dd8c215bfd233820ce58bd9c896de049d281e9aab821d87c150fe2d`.

### Sr analítico e explorador

O reagrupador existente aceita agora `--target DATASET PERIODO METRICA JANELA`, repetido para os três alvos `financial 201903 R2 ttm`, `financial 201906 R2 ttm`, `financial 201909 R2 ttm`. Isso filtra as contribuições armazenadas antes de reagrupar. No modo seletivo, `complete` refere-se aos alvos declarados; os demais resultados SrAnalitico aceitos permanecem próprios. O default de reagrupamento completo da Issue136 conserva seu comportamento.

Com os três pacotes ROE como `--correction ROOT SHA256` e os atributos136 aceitos, foram reagrupadas apenas **3997 contribuições**, em **0,92s**, gerando **76 linhas** de SrAnalitico. Saída `data/curated/ifdata-sr-roe-regroup-20261016-run1`, manifesto `9be640d63160fe514a468a44c5d38033079d5bf697a1bd24433e01b11cc25561`. Não se repetiram os 64 contextos da Issue136 nem se reavaliaram fórmulas financeiras. Sr original, atribuições, conflitos e SegmentoTb continuam intactos.

A projeção local substituiu **375 linhas**, exclusivamente R2/TTM/Financeiro nas três datas, nos agregados e eixos Tcb/Td/Tc/Sr/SegmentoTb/SrAnalitico. As **295029 linhas restantes permanecem exatamente iguais**, incluindo ROA, outros períodos/perspectivas, ROE trimestral, TTM201912 e demais recortes SrAnalitico. HTML SHA256 `4f5f51f05897ccdbfecbf36764ed71911db17295ab295e3e9ab1ae408e88d7a7`; recibo `explorador-roe2019-recibo.json`. A série agregada ROE de 2019 fica contínua nas três coortes, com cobertura, Stone e flags de denominador visíveis. As frações exatas ficam nos pacotes; float permanece restrito à apresentação.

Após exportação integral antiga, aplicar as projeções locais133→134→136→137. `aplicar-roe2019-explorador.py` autentica os quatro pacotes consumidos, usa a apresentação aceita após136 e compara todas as linhas fora do recorte. Não é necessário reconstruir o motor ou a apresentação integral para atualizar esta janela.

### Verificação e estado

TDD: as três integrações R2 falharam antes da ampliação do seletor; os nove testes seletivos passaram, incluindo seis combinações R1/R2×trêsdatas e controles PL zero/null/ausente/incompatível/negativo. O filtro Sr teve regressão RED por helper ausente e dez testes Sr passaram. Revisão A antes do lote real PASS. Revisão B autenticou os 63 arquivos e reproduziu exatamente **3924 ROEs**, seus numeradores LL iguais ao ROA aceito, médias de PL e agregados/coortes, incluindo os extremos negativos. Revisão C autenticou o regroup seletivo e reconciliou as 76 linhas e 12 partições período/coorte por frações exatas.

Quatro scripts desktop passaram **30 verificações**, sem erros JavaScript, com CSV, todos os trimestres2019, Sr analítico, correções ROA, ROE trimestral/dezembro preservados e screenshot inspecionado. Composição final independente PASS: projeção, preservação fora do recorte, escopo e documentação conferidos. A suíte pertinente final reuniu 26 testes, todos PASS em7,22s. Resultado local, sem commit/PR, Goal novo, coleta IF.data ou alteração do Project3.


## Extensão ao 2T e 3T2019 — Issue 134, 16/10/2026

João autorizou estender somente **R1/TTM/Financeiro a 201906 e 201909** na [Issue 134](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/134). Esta seção atualiza o escopo corrente; a seção da #133 abaixo registra a primeira entrega e seus números, preservados. Sem reconstrução da base completa ou mudança de ROE, outras perspectivas e períodos.

A mesma ponte semântica permanece: lucro nativo publicado, tributos retidos como informados e nenhuma correção adicional de JCP. A exceção suficiente para IPs/consórcios exige JCP/DRE zero observado e LLResumo=DRE exato em **todos os inputs de lucro consumidos**, com bindings reconhecidos, únicos e finitos. Não há retroação da Circular3937/2019, cuja publicação em 8/4/2019 permanece a referência normativa. Para conglomerados, mantém-se a própria unidade financeira e o lucro publicado.

| Alvo | Datas dos saldos para a média de AT | Inputs de LL consumidos | Numerador TTM equivalente |
|---|---|---|---|
|2T2019|201806/09/12, 201903/06|201809/12, 201903/06|LL201812 + LL201906|
|3T2019|201809/12, 201903/06/09|201809/12, 201903/06/09|LL201812 − LL201809 + LL201906 + LL201909|

As expressões são conferências independentes da soma de quatro trimestres efetivos, não substituição do núcleo temporal. Em junho, LL201806 não é consumido; AT201806 continua obrigatório. Os lucros intermediários usados nas derivações trimestrais continuam sujeitos à prova de compatibilidade mesmo quando se cancelam na expressão final. O núcleo matemático e o perfil congelado permanecem iguais.

Sete IPs satisfazem a ponte de lucro em cada alvo: Cielo, Redecard, Super Pagamentos, Getnet, Nu Pagamentos, Acesso e BPP. Acesso ainda não tem ROA calculável em junho por falta de AT de abertura; em setembro passa. Stone mantém JCP201812=`-32012000.1` e permanece incompatível nas duas janelas. Outras IPs sem histórico conservam ausência, sem proxy zero. O diagnóstico local `diagnostico-roa201906-201909-ips-zero.json` tem SHA256 `9757430386bd5b1aa86d77ef7314da678ddd8f028965f02fb8219015034674f4`; autentica fontes e lista as posições. A identidade auxiliar da DRE tem resíduo máximo de R$0,000001 nas candidatas; não se arredonda o nativo nem se exige identidade auxiliar exatamente zero.

### Resultados e reprodução seletiva

| Alvo / recorte | Elegíveis / presentes | ROA TTM | Cobertura do AT conhecido |
|---|---:|---:|---:|
|2T2019 · Sistema|1307/1330|1,4937855337%|99,5999092383%|
|2T2019 · Amostra das 24|21/21|1,5761135692%|100%|
|2T2019 · Restante|1286/1309|1,3772971662%|99,0355116269%|
|3T2019 · Sistema|1293/1322|1,5544308217%|99,4698170863%|
|3T2019 · Amostra das 24|21/21|1,6021763845%|100%|
|3T2019 · Restante|1272/1301|1,4866249134%|98,7269710612%|

Junho conserva 23 lacunas: 19 `binding_missing`, 3 `native_null`, 1 `incompatible_definition`. Setembro conserva 29: 25 bindings ausentes, 3 nulos e 1 incompatibilidade. Há respectivamente 3 e 4 unidades com AT contemporâneo desconhecido; cobertura do conhecido não certifica cobertura de todo o universo. Nas duas datas, as 21 unidades financeiras vinculadas representam as 24 companhias da seleção, todas com vínculo elegível; companhia não é contribuição econômica adicional.

Saídas novas, em `data/curated/`, contrato `ifdata-selective-analysis-v1`, sete tabelas JSON/CSV/Parquet como na #133:

- `ifdata-selective-roa-201906-20261016-run1`: manifesto `aa90ae19dbfe388f4352ea78d839ac778dd7c00305912552822b204bee28c13d`, 8,26 segundos;
- `ifdata-selective-roa-201909-20261016-run1`: manifesto `2c3ff18775dbea3edc04ded5cdff021a607d63f79a184a3d0c1d1ef5088742f2`, 8,06 segundos.

Usar o mesmo comando abaixo, com `--period 201906` ou `--period 201909` e destino novo. O seletor aceita apenas os três alvos explicitamente revisados; não é uma ponte genérica. Baseline e manifesto do resultado de março permanecem intactos. Não há commit/PR nesta rodada.

**Verificação:** oito testes seletivos, incluindo integração nos três alvos, passaram em 2,53 segundos; regressões preservam março, rejeitam outros indicadores/perspectivas/janelas e mantêm null, binding, escala e identidade. Revisão independente da fatia A passou antes da execução. A revisão independente da fatia B autenticou os 21 arquivos de cada saída, fontes e CSV de unidades; confirmou exatamente 1307 + 1293 resultados, médias trapezoidais de AT com pesos de dias 92/92/90/91 e 92/90/91/92, e razões das somas das coortes. Motivos adicionais antes mascarados pela incompatibilidade ficaram explícitos após a ponte.

O explorador substituiu somente **221 linhas** dos dois recortes/agregados e cinco eixos. As **276745 demais linhas permanecem exatamente iguais**, incluindo todo o recorte 1T2019, ROE e outros períodos/perspectivas. HTML SHA256 `ae5079d0d97682adca8147013915a2c518cb5612a4610f1616a8d21f29062e08`; recibo local `explorador-roa-2t3t-recibo.json`, com identidade de todas as linhas não afetadas. A atualização `aplicar-roa-2t3t-explorador.py` autentica os dois pacotes e usa a cópia da apresentação já corrigida em março. Para reproduzir após exportação integral do gerador antigo: aplicar primeiro o script da #133 e depois o da #134; os backups e pins preservam essa ordem sem recalcular indicadores.

Dezesseis checks desktop passaram nos dois scripts de conferência, sem erros JavaScript: valores/cobertura, IPs 6/13 e 7/18, Stone visível, CSV, março e ROE preservados, quatro trimestres2019 nas três coortes, filtros e outras perspectivas. Screenshot inspecionado, com série contínua em2019. Revisão final de composição registrada na #134; resultado local, sem publicação Git.

## Primeira entrega — correção seletiva implementada, Issue 133

João autorizou fechar a regra, implementar o cálculo seletivo e atualizar o explorador. A [Issue 133](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/133) delimita esta entrega **local**, sem commit/PR. A ponte está implementada para **R1/TTM/Financeiro/201903**; os diagnósticos e ensaios abaixo são históricos quando descrevem a adoção como pendente. Nenhuma outra janela, indicador ou perspectiva recebeu a ponte.

**Regra fechada:** conglomerados usam a própria unidade financeira e a rubrica LL nativa publicada antes da remuneração do capital retirada pela fórmula, mantendo tributos e demais efeitos publicados. Não se exige mapa de todas as subsidiárias nem se certifica lucro fiscal uniforme. Para IPs/consórcios, cada uma das cinco datas deve ter JCP/DRE 78230 observado exatamente zero, LLResumo 78187=DRE 78187 exato e metadados das contas antigas/posteriores reconhecidos. Ausência, null, duplicata, dado não finito ou valor não zero não libera. Não há retroação da Circular 3937/2019. Cinco IPs satisfazem a regra; **Stone não**, pois JCP 201812 é `-32012000.1`. Identidade DRE é evidência auxiliar; não se quantizam tokens ou impõe resíduo contábil zero para completar uma série.

O comando `recalculate-universe` da CLI existente aceita somente o alvo revisado e escreve em destino novo. Reutiliza `resolve_component`, `evaluate_metric`, o writer e as reduções existentes; consulta cinco partições em um lote DuckDB. A agregação seletiva declara os cinco eixos atuais; o default histórico do agregador conserva os seis eixos para não alterar verificação/replay dos pacotes antigos. Código novo permanece no módulo responsável; sem nova camada ou dependência.

### Resultado aceito localmente

Saída `data/curated/ifdata-selective-roa-201903-20261016-run1`, contrato `ifdata-selective-analysis-v1`, manifesto **`4b62afc3107b4a8fe16e71829c7319939b3321f1f0d9ed51e7a8db6e71f530ed`**, referenciando a base 130 intacta. Sete tabelas JSON/CSV/Parquet: components 13450, results 1345, unit_coverage 1345, aggregates 4, distributions 4, segment_coverage 168, cohort_comparisons 129. As observações originais, seus contextos e fontes são preservados em components; resultados registram a ponte aplicada e a prova de cada exceção. Os Parquets são consultáveis diretamente por DuckDB/Python. O verificador integral do contrato 130 não deve ser usado para este contrato seletivo distinto.

| Recorte | Unidades elegíveis / presentes | ROA de 12 meses | Cobertura de AT conhecido |
|---|---:|---:|---:|
| Sistema observado |1324/1345|1,4281170477%|99,6647043829%|
| Amostra das 24 |21/21|1,4624992183%|100%|
| Restante |1303/1324|1,3796830404%|99,1935363670%|

São **21 ausências**: 14 bindings ausentes, 6 nulos nativos e 1 incompatibilidade (Stone). Seis unidades têm AT desconhecido; cobertura do conhecido não certifica cobertura do total. As 21 unidades vinculam-se às 24 companhias, todas com vínculo elegível nesse recorte; não somar companhias como novas contribuições econômicas. Os 1324 cálculos coincidem exatamente com o ensaio anterior nas mesmas unidades; a diferença no agregado vem da exclusão explícita de Stone, não de ajuste dos valores das demais.

O explorador substituiu **103 linhas** apenas desse alvo nos cinco eixos/agregado. As **276863 linhas restantes são exatamente iguais** à exportação anterior, incluindo ROE e outros períodos/perspectivas. Metadados distinguem manifesto da base 130 e da correção 133; aviso visível explica a ponte, a regra das IPs e Stone, com lista nominal das 21 ausências. As frações exatas ficam nas tabelas; float continua restrito à projeção visual já utilizada.

### Reprodução, tempo e revisão desta implementação

Exemplo a partir do worktree com o código corrente e Python do projeto; usar caminhos locais explícitos para os dois diretórios, com destino ainda inexistente:

```powershell
python scripts/analyze-ifdata.py recalculate-universe `
  --baseline "<diretório da base ifdata-universe-analysis-20261014-final-run3>" `
  --expected-baseline-manifest-sha256 b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192 `
  --metric R1 --horizon ttm --dataset financial --period 201903 `
  --output "<diretório novo para este recorte>"
```

Consulta direta, com a biblioteca já instalada no projeto:

```python
import duckdb
rows = duckdb.sql("SELECT code, status, payload FROM read_parquet('NOVO_DESTINO/results.parquet')").fetchall()
```

Exportação local: `aplicar-roa-seletivo-explorador.py` autentica o manifesto seletivo e os arquivos consumidos, preserva a exportação anterior, compara todas as linhas não afetadas e aplica somente esse alvo. O gerador integral antigo exporta a base 130; após usá-lo, executar novamente a projeção seletiva para incluir a correção. Não é necessário exportar toda a apresentação para atualizar este recorte.

Execução real pela CLI: **7,27 segundos** incluindo leitura/autenticação das entradas selecionadas, cálculo e persistência; não é benchmark do universo completo. O núcleo `ifdata_analysis.py` efetivamente utilizado tem SHA **`4d529ffa5e9588d455fcfd9485e1542163854730e63d06ef202891cc56b41624`**, igual ao blob do HEAD 087700 e preservado nesta entrega; o perfil permanece `59e8df39ca9622ebdc490ef901d374ee26d3acbe9d30b162f3b92c56ddc54ca6`. O manifesto registra separadamente o hash do módulo seletivo produtor. Esse registro atende à sugestão de proveniência da revisão, sem atribuir o fingerprint atual ao produtor histórico da 130.

TDD: testes seletivos falharam antes das funções e passaram após implementação. **7 testes novos passaram**; a suíte pertinente `test_ifdata_analysis.py` executou 109 testes com 1 skip preexistente, sem falhas. Revisões independentes das fatias A/B: PASS; revisor autenticou os 21 arquivos do pacote, recalculou 1324 oráculos e somas por frações exatas, confirmou Stone bloqueada e a imutabilidade do núcleo/perfil. QA desktop seletivo e regressão do explorador passaram sem erros JS, incluindo IPs 5/11, CSV, ROE intacto e ROA 2T2019 intacto. Revisão final da composição/HTML/documentação é registrada na 133; dados e benchmark preexistentes preservados. Nenhum teste de celular, nova coleta ou reconstrução global.

## Histórico — diagnóstico e ensaio anteriores à implementação

Rodada de 16/10/2026 sob a [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6217849577), autorizada por João. Owner Root, base `087700ccafa81ad96c963df62b633fb317d4ca21`, worktree existente da documentação. Destino canônico: `docs/engineering/`; sem nova pasta, camada, runtime ou dependência. Allowlist documental: esta nota e o [protocolo responsável](institution-type-indicator-methodology-20261012.md). Dados, perfis, código do motor, livro, Word e benchmark preexistente preservados nesse diagnóstico inicial. HTMLs/scripts/recibos de diagnóstico permanecem locais fora do repositório. Não houve nova coleta financeira, recálculo do universo, commit ou PR nessa rodada inicial.

## Decisões e limites

- Remover `Atividade` dos recortes analíticos e seletores dos dois exploradores; preservar o campo original e saídas históricas. Novas execuções deverão respeitar essa decisão; o perfil histórico das Issues 127/130 continua representando o lote efetivamente calculado, sem reescrita retroativa.
- Priorizar completude de `Tcb`, depois `Sr`, por último `SegmentoTb`. Resolver também `Td`/`Tc` e demais lacunas, aproveitando causas compartilhadas; não excluí-las do escopo futuro.
- Separar recuperação do dado original, tratamento metodológico derivado e explicação de limitação. Uma proxy não transforma ausência em dado observado. Não preencher desconhecido como negativo nem transportar classificação recente ao passado.
- Diagnosticar um caso por vez com consultas delimitadas; não repetir construção/verificação integral para cada SELECT. A melhoria do motor permanece orientada a medição do gargalo, cálculo seletivo e lotes no DuckDB. Não há benchmark comparável nem promessa de ganho/cronograma nesta rodada.
- Análises estatísticas de variáveis/indicadores fazem parte do desenvolvimento acadêmico futuro, com hipóteses, universo e interpretação fundamentados. Não foram executadas ou escolhidas aqui. A plausibilidade financeira de todos os valores do explorador também não foi certificada.

## Evidência de completude e prioridades

Mapa temporal reutiliza o pacote aceito 130, manifesto `b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`: 244.001 unidades-período e 268.634 contextos de segmento reconciliados; núcleo 60 trimestres 2010–2024. Classificação vem do cadastro da própria unidade/data. `Atividade` permanece no inventário histórico de diagnóstico, mas não nos seletores correntes. Presença de alguma categoria no trimestre não prova preenchimento de todas as unidades.

| Campo prioritário | Evidência no pacote | Encaminhamento |
|---|---|---|
| Tcb | Financeiro: 39 unidades-período sem cadastro em 32 trimestres; Prudencial: 5 em 5 trimestres; Individual: preenchido nos 60 trimestres para todas as unidades. Em 4T2024, 1422/1422 financeiras e 1367/1367 prudenciais preenchidas. | Rastrear os 44 registros sem cadastro contemporâneo, sem inferir tipo apenas pelo código. O cadastro ausente também explica lacunas de Td/Tc nessas unidades. São ocorrências, não 44 instituições distintas. |
| Sr | Primeiro valor observado: Financeiro/Prudencial 2T2017, Individual 1T2017. Em 4T2024: 1049/1422 financeiras, 999/1367 prudenciais, 1212/1585 individuais. S4 não aparece em Financeiro/Prudencial de 4T2017 a 3T2018; na entrada da lacuna, um código deixa de reportar. | Distinguir campo nulo, eventual não aplicabilidade e ausência de unidade. Investigar código/perímetro na lacuna S4; não classificar todas as ausências como erro de ingestão. Faixas próprias de ativos são alternativa metodológica ainda não adotada; não se chamariam S1–S5. |
| SegmentoTb | Em 4T2024: 1352/1422 financeiras, 782/1367 prudenciais, 1585/1585 individuais. As duas categorias prudenciais com lacunas internas começam com ausência de um código reportante. | Após Tcb/Sr, verificar definição e alcance do campo por perspectiva e unidade; completude individual não autoriza copiar o tipo de um membro para o conglomerado. |

Das nove séries categoria/perspectiva com lacunas internas no inventário original, cinco envolvem mudanças de Atividade, incluindo para nulo, e quatro começam com ausência de um código reportante. Há causas compartilhadas entre perspectivas; não são nove erros independentes nem percentual de valores recuperáveis. As mudanças de Atividade não exigem harmonização para os recortes correntes, pois o eixo foi retirado; sua evidência permanece preservada. Lacunas de indicador, abertura, vínculo e não aplicabilidade continuam próprias.

## Caso delimitado: R1/ROA, TTM, Financeiro, 201903, sistema sem segmentação

### Por que o motor bloqueia

`bank_quality/ifdata_analysis.py`, `_compatibility` e `flow_12_months`, compara unidade, definição, escala e regra de janela dos quatro fluxos trimestrais. O perfil `bank_quality/ifdata-analysis-universe-profile-2010-2024.json` distingue `LL-pre201903` e `LL-from201903`. A Conta 78187 permanece “Lucro Líquido”, mas sua descrição muda:

| Até 201812 | A partir de 201903 |
|---|---|
| `[70000009]+[80000006]-[81955002]` | `[70000009]+[80000006]-[81956001]` |

O TTM de 1T2019 depende de 2T/3T/4T2018 e 1T2019; 1T2018 é necessário para retirar o acumulado na reconstrução do 2T2018. A diferença de `definition_id` aciona `incompatible_definition`. Logo, não se trata de ausência generalizada do lucro. A regra executa fielmente a proteção adotada; a questão é se essa divisão semântica é mais restritiva que o necessário para o conceito pesquisado.

Na projeção aceita do agregado deste caso: **1345 unidades esperadas, zero calculáveis/elegíveis**, com motivos registrados `incompatible_definition`: 1330, `binding_missing`: 14 e `native_null`: 1. A proteção explica a maior parte da lacuna desse recorte, mas sua liberação não corrigiria os 15 outros casos nem garante estoque médio, continuidade da unidade ou elegibilidade final das 1330.

### Fontes primárias e interpretação

1. [Circular 2739/1997](https://www.bcb.gov.br/pre/normativos/circ/1997/pdf/circ_2739_v1_O.pdf), arts.1–4, pp.1–2: remuneração do capital registrada como despesa 81955002; para demonstrações publicadas, previa ajustes de remuneração e efeitos tributários/equivalência patrimonial. A regra de publicação não prova por si que cada rubrica da API já reflita todos os ajustes.
2. [Resolução 4706/2018](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50703/Res_4706_v1_O.pdf), arts.1–7, pp.1–2: registro da remuneração em contrapartida a lucros/reservas e aplicação prospectiva desde 1/1/2019; exclui cooperativas, administradoras de consórcio e instituições de pagamento de seu alcance.
3. [Carta Circular 3935/2019](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50731/C_Circ_3935_v1_O.pdf), arts.1 VII/2 I/4 I/5, pp.1–3: exclui 81955002 e cria 81956001 para juros sobre capital social de cooperativas; vigência contábil a partir da data-base fevereiro 2019.
4. [Circular 3937/2019](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50746/Circ_3937_v1_O.pdf), arts.1–7, pp.1–2: tratamento próprio para IP/consórcios; aplicação prospectiva e vigência na publicação, DOU 8/4/2019. Não retroagir automaticamente a 1T2019 com base em minuta/voto preparatório.

**Inferência sustentada, ainda não ponte adotada:** no período antigo, subtrair uma despesa assinada negativa retira seu efeito do lucro. No novo, a remuneração das instituições abrangidas passa a contas patrimoniais, enquanto a fórmula retira a despesa específica das cooperativas. Há fundamento para comparar o lucro nativo antes da distribuição de remuneração do capital. Não basta dizer “mesma conta/nome”: existem mudanças normativas, alcance por tipo de instituição e possíveis diferenças tributárias/equivalência patrimonial a explicitar.

Não subtrair JCP novamente do lucro antigo nem adicioná-lo ao novo: isso duplicaria o ajuste já presente nas fórmulas. A ponte proposta preservaria tributos e demais resultados como publicados; não reconstruiria um lucro contrafactual sob regime tributário uniforme.

### Conferência nativa delimitada

Leitura de cinco partições financeiras 201803/201806/201809/201812/201903, autenticadas pelo manifesto `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095`. Selecionados 41.112 registros de Resumo/DRE: LL 78187, resultado antes tributos 78226, IR/CS 78228, participações 78229 e JCP/juros cooperativas 78230. Decimal sem quantização; nenhum ROA produzido ou saída aceita alterada.

| Data | Unidades | LL finito no Resumo | Resumo LL=DRE LL, exato | Juros ao capital negativos/zero/null |
|---|---:|---:|---:|---|
| 201803 |1399|1396|1396|260/1136/3|
| 201806 |1384|1382|1382|286/1096/2|
| 201809 |1367|1363|1363|288/1075/4|
| 201812 |1357|1352|1352|751/601/5|
| 201903 |1345|1339|1339|213/1126/6|

Nenhuma observação positiva de juros ao capital nesse recorte. A identidade nativa `LL = resultado antes tributos + IR/CS + participações`, usando componentes assinados, apresenta resíduos menores que 0,01 unidade monetária nativa em todas as observações finitas; máximo 0,00001. São resíduos dos tokens publicados, não nova tolerância do motor. Igualdade entre Resumo/DRE não demonstra comparabilidade intertemporal nem resolve estoque médio/perímetro/história de cada unidade.

### Conclusão e próximo teste

**O bloqueio universal apenas pela troca literal de conta parece excessivo para o conceito de lucro nativo antes da distribuição de remuneração do capital.** Há uma ponte conceitual defensável, com ressalvas, e não prova de incomparabilidade universal. A proteção geral continua útil para mudanças não examinadas; não deve ser removida globalmente.

Para produzir o resultado deste caso, falta delimitar a ponte por entidade/perímetro e vigência, especialmente IP/consórcios, aprovar sua interpretação metodológica e executar um ensaio somente R1/TTM/Financeiro/201903. O ensaio deve manter bloqueios de unidade/escala/janela/null/denominador e construir a mesma interseção elegível do agregado. Usar um caso com juros ao capital e outro sem, além das exceções normativas; comparar numerador/estoque médio/statuses independentemente antes de ampliar. Os 1339 lucros finitos em 201903 não equivalem a 1339 ROAs TTM recuperáveis.

No diagnóstico inicial, a causa foi esclarecida e a alternativa delimitada, sem implementar a ponte. João autorizou posteriormente o ensaio descrito abaixo; **a ponte permanece sem adoção em produção**. Se aprovação/validação não sustentarem uma unidade, manter sua ausência explícita. Trimestre efetivo disponível pode ser apresentado como outra janela; não é proxy equivalente de 12 meses.

## Ensaio autorizado de R1/TTM/Financeiro/201903 — continuação em 16/10/2026

Contrato na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6218324787). Executado somente este indicador/janela/período/perspectiva, sem segmentação; amostra/restante são reduções dos mesmos resultados unitários. Script local `ensaio-roa-financeiro-201903.py`, saídas `.json` e `.csv` adjacentes na pasta de visualizações desta conversa. Nenhuma alteração no motor, perfil, pacote aceito ou HTML; os valores originais do explorador permanecem intactos.

### Intervenção única e conferência

Autenticados perfil `59e8df39ca9622ebdc490ef901d374ee26d3acbe9d30b162f3b92c56ddc54ca6`, manifesto financeiro, cinco partições nativas e CSV de unidades do pacote 130. Selecionados 20.556 registros de LL/AT/JCP. O motor atual, no HEAD `087700ccafa81ad96c963df62b633fb317d4ca21`, tem SHA `4d529ffa5e9588d455fcfd9485e1542163854730e63d06ef202891cc56b41624`, conferido contra seu blob Git; não é o fingerprint anterior do finalizador do pacote aceito. O primeiro preflight parou nessa diferença, antes dos cálculos. A reconciliação fixou explicitamente o pin atual, sem atribuí-lo ao produtor histórico; revisão AST confirmou matemática temporal/avaliação intacta e Financeiro com identidade tipo 2 preservada.

Primeiro, o perfil original reproduziu exatamente a contagem do baseline aceito: 1330 `incompatible_definition`, 14 `binding_missing`, um `native_null`. Depois, somente em cópias das observações de LL, os dois `definition_id` foram substituídos por `experimental-LL-before-capital-distribution-2019`. Tokens, bindings originais, unidade, escala, janela, fontes e flags foram preservados; o script verifica a restauração lógica da cópia. `evaluate_metric` não foi alterado.

Em cada resultado calculável, conferência independente com frações exatas:

- Lucro TTM: `LL201806 − LL201803 + LL201812 + LL201903`.
- Ativo médio: média trapezoidal dos cinco saldos, ponderada por **91, 92, 92 e 90 dias**, total 365.
- ROA: razão do numerador pelo denominador; agregado é razão das somas na mesma interseção elegível.

Todos os **1325** numeradores, denominadores e ROAs conferiram exatamente, sem tolerância. Revisor independente recalculou os mesmos resultados a partir dos tokens e também confirmou as somas do agregado, o hash do script e a preservação do código/perfil.

### Resultado experimental

| Transição | Unidades |
|---|---:|
| Incompatibilidade de definição → cálculo disponível |1325|
| Incompatibilidade de definição → nulo nativo antes mascarado |5|
| Binding ausente → binding ausente |14|
| Nulo nativo → nulo nativo |1|

Portanto, a ponte permite calcular **1325/1345 unidades (98,51%)** neste ensaio. Restam 20 ausências reais para o cálculo:14 bindings ausentes e seis nulos, sem imputação ou encurtamento da janela. Os cinco nulos antes mascarados são Credisau (`02966385`), Crehnor Central (`05879577`), Flex (`07584094`), Multimoney (`12586596`) e Caltec (`14425205`), com LL e AT nulos em 201903. A sexta unidade com `native_null` é Mutual Apetrim (`18941229`). A lista nominal completa das 20 está no CSV; não se conclui, sem rastrear cada binding, que todos os 14 casos restantes sejam criação de instituições.

| População | Unidades esperadas | Calculáveis/tecnicamente elegíveis | ROA na sensibilidade ampla |
|---|---:|---:|---:|
| Sistema observado |1345|1325|1,4299549772%|
| Unidades vinculadas à amostra das 24 |21|21|1,4624992183%|
| Restante |1324|1304|1,3842431715%|

As 21 unidades da amostra se vinculam nominalmente às 24 companhias no recorte aceito; companhias não são contribuições econômicas adicionais. A sensibilidade ampla inclui **99,8186862235% dos ativos contemporâneos conhecidos**; seis unidades têm AT desconhecido, por isso esse percentual não certifica cobertura dos ativos totais.

### Alcance normativo sem exclusão silenciosa

| Situação diagnóstica | Unidades esperadas | Calculáveis após ponte |
|---|---:|---:|
| Tipo institucional independente com alcance sustentado |1258|1245|
| Exceção/vigência pendente — IPs |11|6|
| Alcance não demonstrado — conglomerados/classificação insuficiente |76|74|

O cenário amplo é **sensibilidade técnica à ponte proposta**, não novo ROA aceito do sistema. Uma segunda redução apenas das 1245 unidades com tipo sustentado produz 1,3879454467%, mas cobre só cerca de 31,22% dos ativos conhecidos. **Não é recomendação de excluir conglomerados nem resultado substituto do sistema.** `Td=C`/`SegmentoTb=null` indica insuficiência da evidência usada para enquadramento normativo neste ensaio, não prova de lucro incomparável. A dúvida deve ser tratada no nível da definição nativa e do alcance da norma, sem exigir constância econômica integral ou reconstrução societária ilimitada.

Exemplos conferidos: Unicred Sul Catarinense (`00075847`), com juros ao capital negativos, ROA experimental 2,3971311104%; Sicredi Crateús (`00068389`), juros zero,0,8640816568%; Cielo (`01027058`), IP/vigência pendente,3,3137468609% somente na sensibilidade ampla. Não há ajuste adicional de JCP.

### Conclusão do ensaio e eficiência

A restrição de definição é a causa dominante e sua liberação delimitada gera resultados aritmeticamente consistentes:1325 cálculos recuperáveis tecnicamente, com 20 lacunas remanescentes identificadas. Isso sustenta revisar a proteção por uma ponte explícita para as duas definições examinadas, preservando os demais controles. Não sustenta remover comparabilidade global nem aceitar automaticamente o agregado amplo. O próximo passo de adoção é resolver a interpretação do alcance/ressalvas do conceito de lucro publicado, especialmente IPs e unidades conglomeradas; tipos sem prova permanecem visíveis, sem serem excluídos silenciosamente.

Execução local do script: **8,44 segundos**, incluindo autenticação/leitura das entradas selecionadas e cálculo do recorte. Mostra que a investigação e o cálculo seletivo são viáveis sem reconstrução global; não é benchmark comparável da execução histórica completa nem promessa de tempo para todos os indicadores. Os scripts e resultados deste ensaio são diagnósticos locais, não uma nova CLI de produção.

## Reprodução e revisão

Evidência local na pasta de visualizações desta conversa: `diagnostico-roa201903-fontes.py/.json`, `probe-cadastro-tcb-20261016.py/.json`, `diagnostico-completude-20261016.json` e recibos dos dois HTMLs. O script de ROA autentica manifesto e cinco Parquets antes de consultar as cinco contas; é diagnóstico descartável, não nova CLI de produção. O probe cadastral confere manifesto 130 e SHA do CSV unit_periods antes de contar ausência de cadastro. O inventário de completude deriva do mapa já reconciliado com essa mesma fonte.

Checks: os cinco eixos selecionáveis carregam no explorador e mapa; contagens do mapa reconciliam todas as populações/campos/trimestres; os controles de Financeiro/Individual/Prudencial e os casos 2019/2012 continuam funcionando; nenhum erro de JavaScript nos testes desktop. Não foram executados testes de celular nem suíte integral do motor, que não foi alterado. Revisão independente documental concluída em 16/10/2026, sem achados materiais: fontes normativas, interpretação da ponte como proposta, contagens, hashes dos HTMLs, allowlist e preservação do benchmark conferidos. O revisor utilizou os recibos de QA desktop sem repetir navegação ou construção integral. `git diff --check` passou; registro de encerramento local na Issue 3, sem alegar publicação destes documentos.

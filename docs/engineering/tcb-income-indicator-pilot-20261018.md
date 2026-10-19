# Eficiência com renda ampliada — piloto de 18/10/2026

Entrega da [Issue190](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/190), após a [conciliação182](tcb-income-reconciliation-20261018.md). João adotou [E2-W principal e E2-WP como sensibilidade separada](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6258359846). E2-B permanece disponível com seu próprio conceito. O piloto contempla o sistema Financeiro observado completo nas datas201812,201903e202412, sem restringir a companhias vinculadas ou a um Tcb.

## Contrato econômico e contábil

Definindo C=−(pessoal+administração) e S=RBIF−resultado de provisão+serviços+tarifas:

| ID e nome | Fórmula, exibida em% | Componentes Financeiro Tipo2 |
|---|---|---|
|E2-W, eficiência sobre renda selecionada ampliada|100×Cw/(Sw+outras receitas operacionaisw)|DRE4:78218,78219;78215,78213,78216,78217;78222|
|E2-WP, eficiência ampliada incluindo participações|100×Cw/(Sw+outras receitas operacionaisw+participaçõesw)|Mesmas contas, acrescidas de78221|

O numerador mede apenas pessoal e administração. A ampliação do denominador responde à omissão de outras receitas na medida anterior; não torna o numerador custo operacional completo. Participações podem conter resultado de investidas cujos custos não estão no numerador, justificando a série WP separada. Em negócios de serviços, negociação própria, câmbio ou grupos diversificados, a composição da renda ainda precisa acompanhar a leitura. Menor razão não prova maior eficiência tecnológica ou produtiva, sobretudo com reversões ou renda negativa.

Assaf Neto,11.ed.,2015, cap.18,p.342, fornece o índice despesas operacionais/RIF; as duas medidas são adaptações próprias, não reprodução desse índice. FMI2019,§§5.16/5.25/7.60–63, distingue renda não proveniente de juros, custos e renda bruta. Leitura de Assaf e do [guia final FMI](https://www.imf.org/-/media/files/data/2019/2019-fsi-guide.pdf) reaproveitada da182, com localizadores e divergências ali registrados. O título não certifica equivalência com o FSI do FMI.

As janelas são trimestre efetivo e TTM de quatro trimestres disjuntos, com reset semestral dos fluxos nativos; sem anualização×4. Não usa LL nem78223, e não depende de uma ponte artificial de LL em201903. Custo ou renda negativos preservam o sinal; custo revertido recebe `signed_cost_reversal`, denominador negativo recebe `negative_denominator`, zero é indefinido, e null/binding ausente/histórico incompatível permanecem estados distintos. Não houve exclusão acadêmica ou imputação.

## Implementação e preservação

Dois IDs e dois componentes foram acrescentados ao motor complementar existente. Os bindings de78222/78221 são próprios por perspectiva, literais e conferidos contra o catálogo nas60referências; janelas de fluxo são explícitas. A descrição aparente sem operador em78222é preservada exatamente, sem reparação ou interpretação do texto como fórmula executável. O perfil histórico JSON, E2-B e demais indicadores anteriores permaneceram intactos.

TDD registrou RED por `unknown_metric` e por ausência de bindings antes do código. GREEN:8testes matemáticos pertinentes e36testes seletivos,37,085s. O revisor independente verificou ainda102comparações idênticas de payloads das24métricas anteriores em três cenários e contraprovas TTM exatas. O produtor limita uma conexão/um thread e512MiB: a tentativa `run1` falhou na conversão CSV→Parquet com256MiB; uma reprodução isolada confirmou o limite, inclusive sem paralelismo. A conversão exata com512MiB passou e foi conferida campo a campo antes da nova execução integral `run2`. A tentativa falha e buffers foram preservados; seu estado não foi promovido aPASS.

Entradas: ponteiro corrente autenticado, manifest `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`; baseline técnico rastreado pela origem dos estoques, manifest `b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`. O piloto conserva a coorte original desse baseline; a cobertura diagnóstica usa join datado com a coorte corrente. A composição192deverá adotar explicitamente o vínculo atualizado, sem fingir que o produtor já o fez.

Novo pacote privado `data/curated/tcb-piloto-renda-20261018-run2-flow`, manifest `4f073a333de03735a3989cfae2302399f3d5ae51f72a80edaa2dfe2bddb907ae`:126.268componentes,16.496resultados e16.496coberturas. As entradas aceitas e o ponteiro permanecem inalterados. Não houve expansão aos60trimestres, composição192ou alteração do explorador193.

## Cobertura e comparação

| Data | Esperadas por medida/janela | OK trimestre | OK TTM |
|---|---:|---:|---:|
|201812|1.357|1.348|1.345|
|201903|1.345|1.339|1.325|
|202412|1.422|1.388|1.352|

As contagens coincidem entre W/WP neste piloto; os denominadores e valores permanecem separados. Em202412/trimestre, cada série mantém3denominadores zero,22bindings ausentes e9null. Por Tcb, a cobertura elegível de W no trimestre é B1:95/97;B2:31/31;B3C:27/29;B3S:753/753;B4:4/4;N1:218/226;N2:125/136;N4:135/146. Cálculo disponível não certifica adequação econômica universal. SegmentoTb refina a família; Tc/Td/Sr/SrAnalitico são contextos, sem fórmula por cruzamento ou filtro Atividade.

O nominal privado identifica nomes/códigos/companhias/estados por medida e período. As252células de cobertura corrente conservam vinculadas/restante/vínculo desconhecido e total, AT/crédito/PL conhecidos e desconhecidos, somas exatas totais e elegíveis. Nenhuma ausência vira zero. Os16.194resultadosOK foram integralmente rederivados comFraction pelo revisor, incluindo43flags de denominador negativo e86de custo revertido nas duas medidas/janelas.

A comparação separada leu8.248resultados E2-B já persistidos e os pareou com cada nova série, sem recalcular a fórmula antiga. Em8.082paresOK por medida, todos os numeradores coincidem. W fica abaixo deE2-B em7.295pares, igual em555e acima em232; WP em7.286/545/251. Isso descreve a mudança do denominador, não uma melhora econômica causada pela troca de medida. Sinais e participações impedem supor monotonicidade universal. Nominal e matriz preservam data/janela/Tcb/coorte para interpretar esses totais.

Root, branch `codex/tcb-research-182-188`, base41887e5; quatro paths de motor/testes e esta nota, sem nova camada/dependência. Preparação `.scratch/tcb-piloto-renda/`, com tentativas, comandos, recibos, diagnóstico e cobertura. Revisões independentes de código, correção de memória e piloto precederam expansão; comparação e nota têm gate próprio antes da entrega. A seleção de famílias e a expansão/composição final continuam nas192/193.

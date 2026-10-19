# Recursos e obrigações de clientes em N2 — 18/10/2026

Pesquisa da [Issue186](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/186). O Financeiro observado permite descrever ativos e obrigações agregados; não separa os recursos próprios livres, as obrigações por cliente, margens e prazos necessários a uma medida de capacidade de liquidação. Nenhuma razão nova foi adotada. A consulta cobriu o sistema inteiro2010–2024, com destaque para N2, sem limitar a companhias vinculadas.

## Conceito e fontes

Pergunta: os recursos próprios mobilizáveis da operadora permitem cumprir suas obrigações de liquidação, inclusive perante clientes, no prazo pertinente? Patrimônio próprio, recursos de clientes a liquidar, instrumentos em custódia, garantias recebidas e garantias próprias comprometidas têm papéis diferentes. Não se somam automaticamente para formar caixa disponível. A liquidação exige data, contraparte e condições; um valor de custódia não é receita nem ativo próprio por inferência.

O [BCB descreve corretoras/distribuidoras](https://www.bcb.gov.br/estabilidadefinanceira/corretoradistribuidora) como intermediários, com custódia, conta margem e outros serviços. Consulta dirigida em19/10/2026UTC; o resultado indexado forneceu a descrição, mas a abertura web retornou somente aviso deJavaScript, limite preservado. A [nota metodológica152](institution-type-indicator-methodology-20261012.md) e [pesquisa178](tcb-indicators-assaf-atlas-20261018.md) são reaproveitadas para distinguir serviços, negociação própria e câmbio. N2não identifica uma operação homogênea, e não fornece licença individual completa.

Leitura direta da [compilação histórica Cosif2024](https://www3.bcb.gov.br/aplica/cosif/manual/funcoes-2024-historico.pdf), versão214p., em19/10/2026UTC: funções4.9.5.30.00-5/PDFpp123–124,4.9.5.80.00-0/PDFp124,4.9.5.85.00-5/PDFp125 e3.0.6.20.00-3/9.0.6.20.00-5/PDFpp62/193. A primeira contempla contas de liquidações pendentes com controle diário por cliente e vencimento; as demais distinguem conta margem e registros de compensação. A versão2024não certifica a cronologia completa desses títulos desde2010. Assaf,11.ed.,2015,p.334, leitura178 reaproveitada, fundamenta liquidez bancária depositária, sem fornecer uma fórmula específica validada para estas obrigações.

## Correspondência com as variáveis instaladas

Financeiro Tipo2, mesma data, estoques em reais nativos; contexto completo/versão/localizadores preservados no catálogo autenticado.

| Relatório/ID | Definição literal | O que falta para a pergunta |
|---|---|---|
|Ativo2/78188, disponibilidades|`[11000006]`|Livre versus vinculado, propriedade econômica e disponibilidade para liquidação.|
|Ativo2/78189, aplicações interfinanceiras|`[12000005]`|Resgate, liquidação, vinculação e moeda.|
|Ativo2/78190,TVM/derivativos|`[13000004]`|Títulos livres versus comprometidos, haircut, elegibilidade e prazo; não é somente títulos líquidos.|
|Ativo2/78199, outros créditos líquidos|`[18000009]`|Direitos por contraparte/cliente, prazo e correspondência com a obrigação.|
|Ativo2/78200, outros ativos realizáveis|`[19000008] + [14000003] + [15000002]`|Parcelas heterogêneas, sem identificação dos recursos próprios livres.|
|Passivo3/78296, derivativos|`[47000001]`|Exposição própria, garantias/margens e agenda de chamadas.|
|Passivo3/78297, outras obrigações|`[49000009] + [45000003] + [44000004]`|Inclui o grupo490que contém495, mas não individualiza contas de clientes ou liquidações.|
|Passivo3/78298, exigível|`[40000008]`|Mistura prazos, fontes e contrapartes; não é o total específico devido a clientes.|

A inspeção do catálogo completo dos relatórios financeiros instalados não encontrou bindings próprios de49530/49580/49585ou30620/90620. O agregado490não permite recuperar essas parcelas por diferença de saldos sem uma identidade contábil completa. A classificação “próprio” ou “terceiro” tampouco é dedutível apenas deAT, PL, nome institucional ou ausência de depósitos. Não se propõe disponibilidades/78297como substituto: o denominador não corresponde à pergunta.

## Cobertura e estados

Auditoria de oito contas:89.476unidades-trimestre,60referências,3.709células por data/Tcb/SegmentoTb/coorte. Nominal conserva código/nome, companhias, Tc/Td/Sr/SrAnalitico e cada componente com contexto, fração e estado. Somatórios deAT/crédito/PL conhecidos/desconhecidos e da interseção conjunta são exatos. Não confundir cobertura dos agregados com cobertura de recursos livres ou de obrigações de clientes.

| N2, SegmentoTb |201003: esperadas/conjuntas|202412: esperadas/conjuntas|
|---|---:|---:|
|Corretora de câmbio|44/42|51/51|
|Corretora deTVM|59/58|21/20|
|Distribuidora deTVM|62/61|61/61|
|Segmento desconhecido|5/5|3/3|

Em202412são136N2,135com oito componentes finitos. O sistema inteiro tem1.422unidades,1.415conjuntas e7com null preservado. O nominal permite identificar as unidades/companhias faltantes em cada referência; a matriz separa total, vinculadas, restante e vínculo desconhecido. As104linhas nativas sem código são registradas separadamente, sem interpretá-las como instituições adicionais. Zero/negativo/null/ausente são estados diferentes; negativos permanecem assinados. Esta disponibilidade não autoriza chamar uma falta de dado de não aplicabilidade.

## Resultado implementável e lacunas

Mantêm-se rentabilidade/capitalização e renda/custo com os limites de composição/perímetro já estabelecidos. LA eLF permanecem descrições contábeis; L1/L2/L3exigem a função depositária correspondente e não são escolhas padrão para corretoras ou câmbio.

A primeira fatia adicional deve obter, para uma operadora/data, obrigações de liquidação próprias e de clientes por prazo/moeda, recursos próprios livres, restrições/garantias e direitos correspondentes. Começar pela mesma data-base e conferir posição versus fluxos D+1…D+5, mantendo separadas operações vencidas. A fonte pode ser notas ou abertura contábil/operacional própria, sob autorização de aquisição distinta. Somente após pareamento e definição do horizonte cabe formular uma razão; não se inventa uma métrica para completar a dimensão.

Root, branch `codex/tcb-research-182-188`, basefd0c486; única nota pública e `.scratch/tcb-obrigacoes-clientes-n2/`. Sem mudança de arquitetura, motor, dados aceitos ou ponteiro. Pin corrente autenticado `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`; piloto revisto antes da expansão; `full1` registra13,844s. Comandos, hashes e tentativas preservados; revisão independente integral/fontes/SHA na Issue. A lacuna é de correspondência e dados, sem encerrar a medição da dimensão.

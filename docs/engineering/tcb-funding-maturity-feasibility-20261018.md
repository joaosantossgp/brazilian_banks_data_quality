# Financiamento e compatibilidade de prazos — 18/10/2026

Pesquisa da [Issue185](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/185), após o [inventário181](tcb-indicator-input-readiness-20261018.md). O universo é todo o Financeiro observado,2010–2024; B4 e N1 são recortes prioritários, não a população exclusiva. A base permite medir a composição contábil do financiamento. Não permite calcular um descasamento de vencimentos nem identificar recursos institucionais livres apenas pelo agregado empréstimos/repasses.

## Pergunta e fundamento

A pergunta econômica proposta é: em cada data, os recursos mobilizáveis e recebimentos contratuais cobrem os pagamentos exigíveis nos próximos30dias,90dias e um ano, considerando restrições e linhas efetivamente disponíveis? Esses horizontes delimitam a informação a obter, sem adotar nesta pesquisa um novo indicador acadêmico ou cenário de estresse. A comparação exige o mesmo perímetro financeiro, moeda e data de posição; fluxos futuros não podem ser substituídos por estoques vencidos ou por receita contábil.

Assaf Neto, *Estrutura e análise de balanços*,11.ed.,Atlas,2015, cap.18,p.334, sustenta o exame da liquidez bancária; pp.343–345 tratam da sensibilidade de juros. Leitura da [pesquisa178](tcb-indicators-assaf-atlas-20261018.md) reaproveitada, sem alegar nova leitura destas páginas. O GAP de reprecificação usa o momento de revisão da taxa e a exposição sensível, que podem diferir do vencimento de caixa. Não se transforma uma diferença crédito−captação em qualquer um desses GAPs.

Ferraz, Além e Madeira,[2013](https://web.bndes.gov.br/bib/jspui/bitstream/1408/1421/1/RB%2040_final-A.pdf),pp.30–31/35–37, leitura143/152 reaproveitada conforme178, fundamentam a interpretação do financiamento do desenvolvimento e sua sustentabilidade. Trata-se de argumento econômico sobre mandato e atuação, não requisito regulatório ou evidência de que toda obrigação460seja FAT. As referências são conceituais; os bindings e a cobertura abaixo vêm dos arquivos locais autenticados.

## O que o IF.data instalado contém

Todos os componentes são estoques Financeiro Tipo2, em reais nativos. Os contextos completos, Grupo/NomeColuna/descrição, versões e datas estão no catálogo preservado; as expressões abaixo são literais Cosif, e os IDs são IF.data.

| Relatório/ID | Variável e definição | Utilidade e limite |
|---|---|---|
|Ativo2/78188|Disponibilidades `[11000006]`|Caixa contábil, sem prova de disponibilidade irrestrita.|
|Ativo2/78189|Aplicações interfinanceiras `[12000005]`|Estoque, sem vencimento, resgate antecipado ou vínculo.|
|Ativo2/78191|Crédito antes da provisão `[16000001]-[16900008]`|Carteira, sem agenda de recebimentos, juros futuros ou atraso.|
|Passivo3/78185|Captações `[41000007] + [42000006] + [43000005] + [46000002]`|Base da composição LF, não passivo exigível completo.|
|Passivo3/78287|Depósitos `[41000007]`|Uma fonte, sem buckets de retirada/vencimento.|
|Passivo3/78288|Compromissadas `[42000006]`|Fonte com características próprias, sem prazo/colateral individualizados.|
|Passivo3/78294|Emissões `[43000005]`|Não identifica por si FAT, estabilidade ou vencimentos.|
|Passivo3/78295|Empréstimos/repasses `[46000002]`|Agregado não separa credor institucional, contrato, carência, indexador ou condição de utilização.|
|Passivo3/78298|Circulante e exigível a longo prazo `[40000008]`|Curto e longo prazo juntos: o nome não oferece duas parcelas separadas.|

As quatro parcelas de LF permanecem descrições distintas, cada uma dividida por78185 segundo o motor existente. Não foram misturadas com o exigível78298 nem chamadas de índices de estabilidade. A inspeção do catálogo financeiro completo, além de busca pelos termos de maturidade/restrição, confirmou a ausência de abertura contratual de vencimentos nos relatórios instalados. “Depósitos a Prazo”78286é uma categoria de produto, não uma distribuição por prazo residual.

O contexto de resultados de exercícios futuros78299existe de201003a202209; o total passivo78300muda em202212. Esses componentes não integram a disponibilidade conjunta das nove contas nem foram prolongados com zero. O contexto Resumo1/78184agrega exigível e resultados futuros; não é uma abertura adicional por vencimento.

## Cobertura observada e representatividade

Inventário determinístico das nove contas em89.476unidades-trimestre,60referências,3.709células data×Tcb×SegmentoTb×coorte. Conserva nome/código, Tc/Td/Sr/SrAnalitico, companhias e estados por componente; disponibilidade conjunta não é adequação metodológica. Total se decompõe em vinculadas, restante e vínculo desconhecido, sem dupla contagem. A amostra não restringiu a consulta.

| Recorte |201003: esperadas/conjuntas|202412: esperadas/conjuntas|
|---|---:|---:|
|B4, incluindo BNDES|4/4|4/4|
|N1, agências de fomento|14/14|16/16|
|N1, companhias hipotecárias|3/3|4/4|

Em202412o sistema completo tem1.422unidades,1.415com as nove contas finitas e7com null preservado. Zero em captação não vira ausência de recursos ou não aplicabilidade: podem existir PL e obrigações fora do agregado. Valores negativos permanecem assinados, com seu estado; nenhuma razão foi calculada. As117linhas nativas sem código são inventariadas separadamente, não117instituições. O nominal identifica quais unidades e companhias ficam sem componentes em cada período; a matriz conserva AT/crédito/PL conhecidos e desconhecidos, com somas exatas de toda célula e da parcela conjunta. Essa representação econômica mede cobertura do inventário, não acesso a funding ou prazo.

## Lacuna e execução mínima futura

| Informação necessária | Situação atual | Próximo recorte verificável |
|---|---|---|
|Recebimentos e pagamentos por prazo residual|Ausente nos agregados|Notas com análise de vencimentos da mesma unidade/data, incluindo juros e premissas.|
|Fonte institucional/FAT e condições|460agregado; sem identificação contratual|Separar credor/fundo, saldo, disponibilidade, carência, indexador, prazo e restrições.|
|Ativos livres, colaterais e linhas|Não identificados individualmente|Parear ativo elegível/restrição com obrigação e regra de mobilização.|
|Reprecificação|Sem faixas de revisão de taxas|Obter agenda e base sensível, separada da agenda de caixa.|

A primeira fatia futura pode conciliar uma B4 e uma agência de fomento em uma data comum, com fontes e vencimentos da própria unidade. Requer contrato de fonte adicional; esta pesquisa não fez coleta financeira. Somente após conciliar ambos os lados e definir hipóteses cabe escolher fórmula, horizonte e agregação. Não somar razões com conceitos diferentes nem substituir depósitos à vista porAT para fabricar liquidez.

Root é writer/integrador da única nota pública, branch `codex/tcb-research-182-188`; base de assunção41887e5mais entrega documental184, preparação privada `.scratch/tcb-prazo-financiamento/`. Sem mudança de arquitetura, core, fórmulas ou dados aceitos. Pin atual autenticado `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`; piloto1422revisto antes da expansão. `full1` registra14,890s no recibo; execução anterior e hashes preservados. A pesquisa conclui pela fonte adicional precisamente delimitada; não encerra a dimensão por falta de dados. Revisão independente integral e SHA são registrados na Issue.

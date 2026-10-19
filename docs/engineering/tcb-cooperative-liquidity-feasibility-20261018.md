# Liquidez cooperativa e centralização — 18/10/2026

Pesquisa da [Issue184](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/184), sistema financeiro observado2010–2024. A base atual permite descrever caixa/aplicações e composição do financiamento, mas não individualiza o estoque de centralização financeira nem sua disponibilidade. Não há fundamento para adotar AIL/depósitos interfinanceiros como medida substituta dessa liquidez.

## Mapa econômico e evidência primária

Singulares podem transferir recursos para centrais, confederações e bancos cooperativos, que os alocam e podem prestar suporte de liquidez. Os dois lados dessa relação não são o mesmo ativo disponível e exigem perguntas diferentes: acesso da filiada aos recursos versus capacidade da entidade central de atender retiradas/suporte. Somar exposições internas não elimina a relação dentro do sistema.

Fonte principal: BCB, [*Panorama do Sistema Nacional de Crédito Cooperativo*, dezembro2024](https://www.bcb.gov.br/content/estabilidadefinanceira/coopcredpanorama/Panorama_Cooperativas_SNCC_FINAL_dez2024.pdf), p.22/PDF22, nota10 e gráficos3.1.6–7; pp.24–26, discussão de gestão centralizada e suporte. Leitura dirigida em19/10/2026UTC, conferindo texto e localizadores; não se transfere automaticamente a organização2024 para todas as datas históricas. Assafp.334, reaproveitado da178, fundamenta a liquidez imediata bancária, sem substituir esta fonte sobre cooperativas.

A [compilação histórica Cosif2024](https://www3.bcb.gov.br/aplica/cosif/manual/funcoes-2024-historico.pdf), função1.4.5.10.00-5/PDFp16 e4.4.5.10.00-6/PDFp110, identifica recursos transferidos pelas filiadas e recebidos pelas centrais. Essas rubricas pertencem a140/440, não aos agregados120/413. A compilação é uma versão histórica específica, sem certificar uma cronologia completa dos títulos/regimes em2010–2024.

TcbB3S/B3C identifica famílias; SegmentoTb, cadastro e perímetro refinam o tipo. Bancos cooperativos requerem sua identificação própria e não são reclassificados paraB3por nome. Os campos de conglomerado financeiro/prudencial não são cadastro completo de filiação cooperativa. Td=I não prova independência societária; Sr/SrAnalitico não identificam acesso ao suporte. Faltam relação filiada–central–banco datada e regras contratuais para certificar uma visão do sistema com eliminações.

## Componentes na base atual

Financeiro Tipo2, ID IF.data e contexto completo preservados no catálogo privado:

| Conta/relatório | Definição literal | Resultado da conciliação |
|---|---|---|
|78189/Ativo2, Aplicações Interfinanceiras de Liquidez, grupo nulo|`[12000005]`|Existe, mas não identifica o total de recursos transferidos pela centralização.|
|78284/Passivo3, Depósitos Interfinanceiros, grupo Captações - Depósito Total|`[41300006]`|Existe, com outras finalidades/contrapartes; não é o passivo445individualizado.|
|78285/Passivo3, outros depósitos, mesmo grupo|Antes202006:`[41400009]+[41600005]+[41700008]+[41800001]+[41900004]`; depois deduz41930005|Mudança efetiva de nome/definição; não confundir com a obrigação de centralização.|
|78200/Ativo2, Outros Ativos Realizáveis, grupo nulo|`[19000008] + [14000003] + [15000002]`|Contém o grupo140, porém sem abertura145na célula.|
|78297/Passivo3, Outras Obrigações, grupo nulo|`[49000009] + [45000003] + [44000004]`|Contém440, mas não separa445ou prazo de resgate.|
|78199/Ativo2, Outros Créditos - Líquido de Provisão, grupo nulo|`[18000009]`|Não representa exclusivamente recurso livre ou centralizado.|

A inspeção percorreu o catálogo financeiro completo do núcleo; não há binding específico das rubricas145/445nesses relatórios agregados. A inclusão de um grupo pai demonstra onde uma parcela pode estar contabilizada, sem permitir isolá-la por subtração de outras contas heterogêneas. Os valores ficam em reais nativos, com frações e sinais exatos; nomes e códigos iguais não dispensam contexto/versão.

## Cobertura e contraprova ao atalho AIL

Auditoria das seis contas no universo inteiro:89.476unidades-trimestre; matriz e nominal por data/Tcb/SegmentoTb/coorte, com Tc/Td/Sr/SrAnalitico preservados. O catálogo conserva as60referências dos agregados e a mudança de78285em202006. O conjunto finito, os sinais/zeros/null/ausentes e AT/crédito/PL conhecidos/desconhecidos acompanham cada célula, sem excluir entidades por desconhecimento.

| Família,202412 | Esperadas | Seis componentes finitos | AIL positivo / zero | Depósitos interfinanceiros positivos / zero |78297positiva|
|---|---:|---:|---:|---:|---:|
|B3S|753|753|312/441|110/643|753|
|B3C|29|27|22/5|4/23|27|

As duasB3Cfaltantes têm null nos componentes e estoques desconhecidos; não são zeros ou exclusões por inadequação. A presença das outras27não certifica disponibilidade livre. Em441singulares o AIL é zero, o que não demonstra ausência de centralização: o agregado que contém140é outro. A razão AIL/depósitos interfinanceiros combinaria contas com abrangências distintas, mesmo quando o denominador fosse positivo.

As listas nominais incluem todas as unidades, nomes, companhias associadas e estados; AT/crédito/PL por unidade vêm da tabela aceita `representation_stocks.parquet`, suas somas por recorte estão no resumo privado. O roster55da181 preserva as companhias sem unidade e a pesquisa não se limita às32associadas. Percentuais sobre estoques conhecidos não estimam as duas observações sem informação nem eliminam relações internas entre membros.

O inventário nativo adicional conserva78linhas sem código, com contexto e token, em nove referências. Não são78instituições; não se lhes imputou filiação ou identidade. O achado foi corrigido e revisado antes da expansão. Zero numérico, null e código ausente permanecem estados distintos.

## Medição mantida, lacunas e implementação mínima

Mantêm-se LA e LF como descrições contábeis, L2/L3onde a função depositária for pertinente, com limites explícitos. LA não se torna liquidez disponível da filiada; LF não se torna estabilidade ou acesso ao fundo de liquidez. Sem a abertura centralizada/livre, não foi criada uma nova fórmula apenas para preencher a dimensão.

| Pergunta específica | Disponível | Componente/contrato necessário | Classe |
|---|---|---|---|
|Quanto a filiada pode mobilizar no horizonte escolhido?|Caixa e agregados patrimoniais|Saldo centralizado próprio, parcela livre/vinculada, condições/prazo de resgate e saídas correspondentes|Fonte adicional|
|A central suporta resgates das filiadas?|Agregados de ativo/passivo próprios|Ativos líquidos elegíveis/livres; obrigações445por filiada, prazo e linhas de suporte contingentes|Fonte adicional|
|Como o sistema cooperativo distribui liquidez internamente?|Unidades e classificações observadas|Filiação datada e contrapartes para eliminar relações internas e manter perímetro coerente|Conciliação de perímetro/fonte adicional|

Primeiro recorte futuro: uma filiada e sua central em data comum, com rubricas145/445e condições de resgate identificadas; conferir os dois lados, restrições e pertinência do horizonte. Só então definir a medida e revisá-la antes de ampliar. A fonte pode ser demonstração/notas ou abertura contábil própria, em contrato de aquisição separado; esta pesquisa não fez coleta financeira.

Não aplicabilidade econômica e falta de dado permanecem separadas. A lacuna de liquidez centralizada é metodológica e de dados; a disponibilidade dos agregados não a resolve, e sua ausência não encerra a medição da dimensão. O resultado desta pesquisa é uma decisão implementável sobre o que a base atual sustenta e a abertura mínima que falta.

Root, branch `codex/tcb-research-182-188`, base41887e5, única nota pública e preparação `.scratch/tcb-centralizacao-cooperativa/`; nenhum core/shared ou mudança estrutural. Ponteiro/manifests/tabelas reautenticados no pin `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`. Pilotos antes das expansões:1.422unidades; revisão independente de contagens/estoques/contextos, correção do inventário sem código e inclusão de78297após identificação da conta445. As execuções anteriores permanecem; `full2` é a integral de seis contas. Não calculou indicador, alterou dados aceitos ou promoveu ponteiro/explorador. Revisão integral/fontes/SHA na Issue.

# Pagamentos: obrigações e salvaguarda — 18/10/2026

Pesquisa da [Issue187](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/187), universo Financeiro observado2010–2024. Existe uma abertura de contas pré-pagas no IF.data instalado:110560, desde202006. Isso corrige a hipótese de ausência completa do componente de obrigações. Ainda faltam recursos elegíveis/vinculados, obrigações complementares e modalidade/regime datados para formular uma cobertura de salvaguarda. Não foi criado indicador de conformidade nem coletada informação financeira adicional.

## Conceitos e recortes legais

Salvaguarda protege recursos dos usuários; capital absorve perdas da instituição segundo seu regime; liquidez própria trata dos recursos mobilizáveis para cumprir obrigações próprias. Essas perguntas não se resolvem pela mesma conta ou razão. PR/CP de um banco do grupo não substitui capital daIP, e recursos protegidos não são automaticamente caixa livre da operadora.

Leitura dirigida de fontes primárias em19/10/2026UTC:

| Fonte/localizador | Evidência e limite temporal |
|---|---|
|[Lei12.865/2013, Câmara, texto atualizado](https://www2.camara.leg.br/legin/fed/lei/2013/lei-12865-9-outubro-2013-777235-normaatualizada-pl.html),arts.6/12|Define conta/instituição de pagamento e separação patrimonial dos recursos em conta; não autoriza tratá-los como depósitos à vista bancários. A página é consolidada, e não uma edição congelada em2013.|
|Mesma lei,arts.12-A/12-B/12-C e notas de alteração|Proteção dos fluxos de liquidação e bens/direitos vinculados; introdução pelaMP930/2020, conversão naLei14.031/2020. Não projetar esse texto para2010nem confundir toda obrigação de liquidação com saldo pré-pago.|
|[Voto122/2024–BCB](https://normativos.bcb.gov.br/Votos/BCB/2024122/Voto_do_BC_122_2024.pdf),1/8/2024,§§15–18,PDFpp3–4|Descreve a aplicação do art.22daResoluçãoBCB80/2021em espécie noBCB ou títulos públicos registrados noSelic, incluindo compromissadas, e discute elegibilidade. É exposição/proposta datada, não substitui a norma nem comprova sua entrada em vigor.|

O [portal daResolução80](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=80&tipo=Resolu%C3%A7%C3%A3o+BCB) retornou aviso deJavaScript nesta leitura; a limitação foi preservada. Não se atribui a esse acesso uma leitura integral da redação original/consolidada. A descrição primária2024é suficiente para mostrar por que caixa/AIL/TVM agregados não provam elegibilidade; uma aplicação regulatória exigiria reconstruir a norma vigente na data, inclusive transições e modificações. Os requisitos de2025–26não foram aplicados retroativamente ao núcleo.

Modalidades precisam de identificação datada: emissão de moeda eletrônica/pré-pago, emissão pós-paga, credenciamento e iniciação têm obrigações e fluxos distintos; podem coexistir na mesma unidade. A distinção é reaproveitada da [pesquisa178](tcb-indicators-assaf-atlas-20261018.md) e [nota152](institution-type-indicator-methodology-20261012.md), sem inferir modalidade/licença a partir deN4ou do nome. O cadastro instalado ofereceN4/SegmentoTb “Instituição de Pagamento”, sem certificar a história completa de autorizações por modalidade. Assaf não é forçado como fonte exclusiva dessas regras.

## Bindings e cobertura realmente disponíveis

Financeiro Tipo2, estoques em reais nativos; contextos completos no catálogo autenticado:

| Relatório/ID | Definição | Cobertura e interpretação |
|---|---|---|
|Passivo3/110560,Conta de Pagamento Pré-Paga(a5)|`[41930005]`|19referências,202006–202412. Um componente de obrigações pré-pagas; não toda obrigação de usuário/arranjo/modalidade.|
|Passivo3/78285,Outros Depósitos(a5)|`[41400009]+[41600005]+[41700008]+[41800001]+[41900004]`|41referências,201003–202003;4193não está separada nesta célula.|
|Passivo3/78285,Depósitos Outros(a6)|Mesma expressão menos`[41930005]`|19referências a partir202006; quebra explícita, sem emendar silenciosamente a série anterior.|
|Ativo2/78188,disponibilidades|`[11000006]`|Não isola recursos segregados ouCCME.|
|Ativo2/78189,aplicações interfinanceiras|`[12000005]`|Não isola elegibilidade/vinculação/prazo.|
|Ativo2/78190,TVM/derivativos|`[13000004]`|Inclui ativos heterogêneos; não equivale a títulos públicos elegíveis de salvaguarda.|
|Passivo3/78297,outras obrigações|`[49000009] + [45000003] + [44000004]`|Não fornece obrigações complementares de usuários ou arranjos separadamente.|

As seis contas do inventário conjunto são110560,78285,78188,78189,78190e78297;78285tem duas definições datadas. A inspeção do catálogo completo não revelou um binding próprio que pareie o saldo pré-pago com seus ativos elegíveis/vinculados e fluxos em trânsito. Não se calcula caixa/110560,AIL/110560ouTVM/110560para chamar o resultado de salvaguarda. Tampouco se usaDVcomo denominador substituto.

| Data | Sistema: esperadas/conjuntas |110560positiva, sistema|N4: esperadas/conjuntas|110560positiva,N4|
|---|---:|---:|---:|---:|
|202003|1.305/0|Não observável separadamente|20/0|Não observável separadamente|
|202006|1.303/1.299|41|22/22|13|
|202412|1.422/1.415|200|146/144|103|

O zero da coluna conjunta em202003indica a ausência estrutural de110560no relatório, não falta de proteção nem inatividade. Antes202006o estado é`absent`, sem imputar zero; em202412as144N4finitas têm103saldos positivos e41zeros, com2null conservados. Zero não identifica uma modalidade pós-paga/iniciadora, e saldo positivo não certifica a integralidade da obrigação regulatória.

Os200saldos positivos202412se repartem em18B1,3B2,1B3S,64N1,11N2e103N4. A abertura pertence ao universo observado e não apenas àsIPs classificadasN4. Não se deduz autorização ou modalidade desses números. Não haviaN4observada em201003; isso não afirma inexistência econômica de atividades de pagamento anteriores.

O inventário cobre89.476unidades-trimestre,60referências e3.709células data×Tcb×SegmentoTb×coorte. Nominal identifica códigos/nomes/companhias e Tc/Td/Sr/SrAnalitico; matriz separa vinculadas/restante/desconhecido e total, estados por componente, AT/crédito/PL conhecidos/desconhecidos e somas exatas conjuntas. As75linhas nativas sem código são preservadas à parte. Cobertura dos agregados não é cobertura regulatória, e ausência de dado não é não aplicabilidade.

## Fonte adicional mínima e próximo recorte

Para emissão de moeda eletrônica, conciliar uma unidade/modalidade/data: saldo de usuários e valores em trânsito/outros itens exigidos na redação vigente; recursos em espécie e títulos/compromissadas efetivamente vinculados; identificação, valor elegível, moeda, vencimento e restrições; instante diário de apuração e regra de avaliação. Para credenciamento/pós-pago, identificar obrigações de liquidação e garantias da cadeia própria; para iniciação, primeiro demonstrar se existe custódia de recursos na atividade examinada. Não aplicar um denominador pré-pago universal.

Somente após esse pareamento e uma revisão da norma datada cabe propor uma razão, mantendo salvaguarda, capital e liquidez própria separados. Demonstrações/notas ou dados operacionais/regulatórios específicos exigem aquisição autorizada em outro recorte. Não há nova decisão de fórmula pendente nesta pesquisa, pois a ficha numérica ainda não tem os componentes demonstrados.

Root, branch `codex/tcb-research-182-188`, base7bfeed2; única nota pública e `.scratch/tcb-salvaguarda-n4/`, sem mudança estrutural/core. Pin corrente autenticado `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`; piloto revisto antes da expansão, `full1` registra11,671s. Ponteiro/dados aceitos intactos. Comandos, hashes, versões, limites de acesso e revisão independente integral/SHA acompanham a Issue. A pesquisa resolve a viabilidade com a base atual e mantém explícitas as lacunas de dados e de regime.

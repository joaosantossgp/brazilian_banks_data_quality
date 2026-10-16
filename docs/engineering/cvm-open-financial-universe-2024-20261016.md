# Universo aprovado de companhias abertas financeiras — corte de 2024

[Issue 142](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/142) · [decisão humana na Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) · [entrega anterior, Issue 125](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/125).

## Decisão vigente e estado de execução

João aprovou, nesta conversa de **16/10/2026**, o universo descritivo de **55 companhias domiciliadas no Brasil**, com registro de companhia aberta CVM **A ou B em 31/12/2024**, incluindo a securitizadora AUZZA com situação suspensa explicitada. A análise conserva **2010–2024, trimestral, com verificação anual dos vínculos**. A lista nominal abaixo é o universo adotado nesta decisão; não é um censo certificado de todas as financeiras registradas.

As 55 dividem-se em **32 com associação IF.data comprovada no corte**, representadas por **24 códigos financeiros distintos**, e **23 sem correspondência principal admitida**. As últimas permanecem no universo descritivo e na explicação de cobertura; não são excluídas por indisponibilidade. A associação pode ser direta, por operadora controlada ou por pertencimento a conglomerado. Não equivale, em todos os casos, às demonstrações próprias/consolidadas da emissora.

**Esta entrega atualiza documentação, não os cálculos nem os datasets.** Os artefatos e percentuais anteriores continuam descrevendo 24 companhias/20 unidades. Depois das outras implementações e pesquisas de tarefas, João solicitará a uma tarefa própria o recálculo baseado neste universo pesquisado e documentado. Nenhum recálculo foi executado ou antecipado nesta entrega. As métricas, fórmulas, janelas e correções de indicadores já aceitas conservam seus contratos.

A decisão substitui o requisito anterior de ações/Units negociáveis pelo de registro CVM A/B no corte. Mantém a coorte fixa 2024, não a população dinâmica de abertas em cada ano. Domicílio é da companhia selecionada, independentemente de controlador estrangeiro. Holding estrangeira/BDR não é companhia brasileira por possuir operadora doméstica; emissoras domésticas como XP Investimentos S.A. são identidades distintas de sua controladora estrangeira.

## Critério setorial e composição

O universo financeiro amplo inclui bancos/crédito/arrendamento, distribuição de valores mobiliários, pagamentos, infraestrutura de mercado, seguros/resseguros/corretagem, securitização e holdings com atividade ou controladas financeiras documentadas no corte. Rótulo CVM/B3 é pista: atividade efetiva e direção do controle precisam de suporte temporal. Aplicações, holding genérica, serviço tecnológico para bancos ou participação minoritária isolada não bastam para selecionar uma operadora.

A composição aprovada é **43 financeiras dos grupos A/B + 11 securitizadoras ativas + AUZZA suspensa = 55**. São **35 categoria A e 20 categoria B**, com **54 registros ativos e um suspenso** no corte. O cenário de descoberta 56 incluía Invesc/CADIP e não AUZZA; o 55 adotado **retira essas duas fronteiras públicas e acrescenta AUZZA**. Os antigos 56/57 são cenários de triagem, não a lista adotada.

Invesc, CADIP e SIMPAR/BBC ficam fora desta lista, mantendo pendências próprias. O tratamento da suspensão é explícito: não se introduziu um requisito silencioso de registro Ativo. A suspensão de AUZZA em 16/08/2024 não é cancelamento; o cancelamento informado posteriormente é de 07/05/2026.

## Ampliação em relação à pesquisa anterior

| Medida | Pesquisa anterior | Decisão de 16/10 | Variação |
|---|---:|---:|---:|
| Companhias com correspondência principal IF.data |24|32|**+8; +33,33%**|
| Unidades financeiras distintas no corte |20|24|**+4; +20,00%**|
| Universo documental financeiro anterior |31|55|**+24; +77,42%**, condicionado à mudança de critério e ampliação da descoberta|
| Companhias sem correspondência principal admitida |7|23|+16; permanecem no universo descritivo|

O aumento 24→32 vem de Daycoval, Paraná, Cielo, Oliveira Trust S.A., RCI, Nacional, Bradesco Leasing e Dibens. **Somente quatro acrescentam códigos 2024:** Daycoval C0051987, Paraná C0030881, Cielo 01027058 e Oliveira DTVM 36113876. RCI compartilha Santander, Nacional compartilha BTG, Bradesco Leasing compartilha Bradesco e Dibens compartilha Itaú. O registro aberto delas não cria quatro outros balanços financeiros.

Os 31 anteriores eram o universo documental observado da pesquisa 125, não um censo. Comparar 31→55 não demonstra ganho de representatividade econômica. Nenhum percentual financeiro de ativos/crédito/PL anterior foi reaplicado ao novo universo. A comparação solicitada de correspondência é 24→32; a comparação de unidades é 20→24.

## A — 32 companhias com associação IF.data comprovada

Categoria/situação referem-se ao corte. Todas deste grupo são ativas no corte. CNPJ e denominação são os identificadores documentais da emissora; alguns nomes CVM são abreviados. Código de grupo não é demonstração própria da subsidiária. Fontes individuais trazem IDs FCA 2024/FCA 2025, ligados aos arquivos primários em Fontes.

| Nº | Companhia | CNPJ | CVM | Cat. | Unidade financeira 2024 | Natureza da associação | IDs FCA 2024 /2025 |
|---:|---|---|---:|:---:|---|---|---|
|1|BCO BRASIL S.A.|00.000.000/0001-91|001023|A|`C0049906`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|135645 / 146477|
|2|BRB BANCO DE BRASILIA S.A.|00.000.208/0001-00|014206|A|`C0031976`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|137122 / 153632|
|3|PORTO SEGURO S.A.|02.149.205/0001-69|016659|A|`C0051444`|Holding→Portoseg; não consolidado societário Porto|138421 / 148651|
|4|BCO AMAZONIA S.A.|04.902.979/0001-44|000922|A|`04902979`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|133368 / 144088|
|5|BCO ESTADO DO PARA S.A.|04.913.711/0001-08|001171|A|`04913711`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|137878 / 148729|
|6|BCO NORDESTE DO BRASIL S.A.|07.237.373/0001-20|001228|A|`07237373`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|133810 / 144612|
|7|B3 S.A. - BRASIL, BOLSA, BALCÃO|09.346.601/0001-25|021610|A|`00997185`|Holding→Banco B3; não consolidado societário B3|135749 / 144895|
|8|BR ADVISORY PARTNERS PARTICIPAÇÕES S.A.|10.739.356/0001-03|025860|A|`13220493`|Holding→banco sob controle indireto; não consolidado da holding|142792 / 154059|
|9|BCO ESTADO DE SERGIPE S.A. - BANESE|13.009.717/0001-46|001120|A|`13009717`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|137628 / 148121|
|10|BCO MERCANTIL DO BRASIL S.A.|17.184.037/0001-10|001325|A|`C0020152`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|137991 / 148823|
|11|BANESTES S.A. - BCO EST ESPIRITO SANTO|28.127.603/0001-78|001155|A|`C0030159`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|137008 / 153763|
|12|BCO ABC BRASIL S.A.|28.195.667/0001-06|020958|A|`C0041856`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|143874 / 145219|
|13|BCO BTG PACTUAL S.A.|30.306.294/0001-45|022616|A|`C0049944`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|146342 / 148494|
|14|Mercantil Financeira S.A. - Crédito, Financiamento e Investi|33.040.601/0001-87|008540|A|`C0020152`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|139159 / 152243|
|15|BCO MERCANTIL DE INVESTIMENTOS S.A.|34.169.557/0001-72|001309|A|`C0020152`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|137986 / 148820|
|16|BCO PAN S.A.|59.285.411/0001-13|021199|A|`C0049944`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|148274 / 148662|
|17|BCO BRADESCO S.A.|60.746.948/0001-12|000906|A|`C0010045`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|137121 / 148197|
|18|ITAU UNIBANCO HOLDING S.A.|60.872.504/0001-23|019348|A|`C0010069`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|141278 / 145293|
|19|BANCO BMG S/A|61.186.680/0001-74|024600|A|`C0030290`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|134853 / 148239|
|20|ITAÚSA S.A.|61.532.644/0001-15|007617|A|`C0010069`|Controle compartilhado via IUPAR→ITH; compartilha Itaú|138300 / 153503|
|21|BCO PINE S.A|62.144.175/0001-20|020567|A|`C0050304`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|139282 / 144493|
|22|BCO SANTANDER (BRASIL) S.A.|90.400.888/0001-42|020532|A|`C0030379`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|143412 / 148845|
|23|DM FINANCEIRA S.A. - CRÉDITO, FINANCIAMENTO E INVESTIMENTO|91.669.747/0001-92|006076|A|`C0052357`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|134735 / 146613|
|24|BCO ESTADO DO RIO GRANDE DO SUL S.A.|92.702.067/0001-96|001210|A|`C0030173`|Direta: emissor/instituição identificado no cadastro→unidade financeira nativa; não equivalência universal de códigos com CNPJ.|135976 / 152119|
|25|BCO DAYCOVAL S.A.|62.232.889/0001-90|020796|B|`C0051987`|Direta: emissor bancário → conglomerado Daycoval.|138244 / 145398|
|26|PARANA BCO S.A.|14.388.334/0001-99|020729|A|`C0030881`|Direta: emissor bancário → conglomerado Paraná.|138473 / 144649|
|27|CIELO S.A. -  Instituição de Pagamento|01.027.058/0001-91|021733|B|`01027058`|Direta: IP independente; controle compartilhado BB/Bradesco e sobreposição a examinar.|141555 / 148800|
|28|OLIVEIRA TRUST S.A.|21.110.778/0001-23|026417|A|`36113876`|Holding → DTVM sob controle indireto de 100% no corte; não consolidado da holding.|138282 / 148365|
|29|BANCO RCI BRASIL S.A.|62.307.848/0001-15|021466|B|`C0030379`|Emissor individual 62307848 → grupo Santander; controle conjunto; não balanço próprio.|134227 / 148748|
|30|BANCO NACIONAL S.A.|17.157.777/0001-67|001350|A|`C0049944`|Emissor individual 17157777 → grupo BTG desde 202409; não histórico BTG anterior.|143036 / —|
|31|BRADESCO LEASING S.A. ARREND MERCANTIL|47.509.120/0001-82|019640|B|`C0010045`|Emissor individual 47509120 → grupo Bradesco; não balanço próprio.|141395 / 151221|
|32|DIBENS LEASING S.A. - ARREND.MERCANTIL|65.654.303/0001-73|014214|B|`C0010069`|Emissor individual 65654303 → grupo Itaú; não balanço próprio.|141279 / 145297|

### Identidade e evidência histórica das oito adições

| Companhia/CVM | Categoria histórica | Presença TI2 no histórico e limite |
|---|---|---|
|Daycoval 20796|B desde 24/08/2016|23 trimestres 62232889,201003–201509;37 trimestres C0051987,201512–202412. Não certificar perímetro contínuo pela justaposição.|
|Paraná 20729|A desde 26/11/2020|60/60C0030881; nomes J.Malucelli/Paraná. Não usar a categoria B de 2017 como vigente 2024.|
|Cielo 21733|B desde 26/08/2024|29/60 trimestres 01027058 desde 201712. Cadastro anterior não significa valores anteriores. Controle BB/Bradesco exige exame da sobreposição.|
|Oliveira Trust 26417|A desde 29/11/2021|60/60DTVM 36113876. Controle indireto 100% explícito para 31/12/2024 não retroprojeta propriedade nem transforma DTVM em consolidado da holding.|
|RCI21466|B desde 01/01/2010 no FCA|Cadastro 60/60, sem valores TI2 individuais 62307848 no inventário consultado. Grupo Santander no corte; controle conjunto, participação 39,89%.|
|Nacional 1350|A ativo no corte; cancelamento 15/05/2025|Cadastro 60/60; liquidação até 202406; BTG/A desde 202409. Sem valores TI2 individuais 17157777 no inventário consultado. Controle BTG concluído 15/08/2024.|
|Bradesco Leasing 19640|B desde 01/01/2010 no FCA|Cadastro/vínculo Bradesco 60/60, sem valores TI2 individuais 47509120. Não usar homônima inativa 43833821.|
|Dibens 14214|B desde 01/01/2010 no FCA|Cadastro/vínculo Itaú 60/60, sem valores TI2 individuais 65654303. FRE 2025, p 36, explicita ausência de atividade operacional em 31/12/2024.|

**Oliveira Trust S.A.**,21.110.778/0001-23, CVM26417, é a companhia adotada. **Oliveira Trust Participações S.A.**,05.310.054/0001-77, é outra pessoa jurídica e não foi comprovada como emissora aberta nesta pesquisa. Não tratar a correção como mera abreviação de nome. Ausência de valores TI2 individuais não afirma ausência em outras perspectivas IF.data.

## B — 11 financeiras sem correspondência principal admitida

| Nº | Companhia | CNPJ | CVM | Cat. | Justificativa/pendência | IDs FCA 2024 /2025 |
|---:|---|---|---:|:---:|---|---|
|33|INVESTIMENTOS BEMGE S.A.|01.548.981/0001-79|006041|A|Identidade/perímetro de 01548981 Financeira Bemge divergente; não atribuir todo Itaú à controlada Investimentos Bemge.|139494 / 145296|
|34|ALFA HOLDINGS S.A.|17.167.396/0001-69|009954|A|Downstream coligadas; não atribuir Alfa/Safra por participação minoritária.|142014 / 146280|
|35|BB SEGURIDADE PARTICIPAÇÕES S.A.|17.344.597/0001-94|023159|A|Seguridade; sem unidade principal admitida. Ausência IF.data não exclui elegibilidade.|137432 / 149148|
|36|CAIXA SEGURIDADE PARTICIPAÇÕES S.A.|22.543.331/0001-00|023795|A|Seguridade; sem unidade principal admitida.|138014 / 150098|
|37|IRB - BRASIL RESSEGUROS S.A.|33.376.989/0001-91|024180|A|Resseguro; sem unidade principal admitida.|137143 / 145762|
|38|QUALICORP CONSULTORIA E CORRETORA DE SEGUROS S.A.|11.992.680/0001-93|022497|A|Corretagem/benefícios; sem unidade principal admitida.|142080 / 146264|
|39|WIZ CO PARTICIPAÇÕES E CORRETAGEM DE SEGUROS S.A.|42.278.473/0001-03|023590|A|Corretagem; sem unidade principal admitida.|133778 / 148810|
|40|XP Investimentos S.A.|16.838.421/0001-26|027111|B|Emissora brasileira distinta de XPInc. Banco XP passou a controlar XPS.A./XPCCTVM; não inverter controle para atribuir C0052120.|138575 / 148977|
|41|Reag Capital Holding S.A.|10.452.416/0001-02|026964|B|Holding financeira/RSF 86% no FRE; passo RSF→DTVM34829992 não comprovado. Cancelamento 06/10/2025 não retroage.|143726 / 152737|
|42|BNDES PARTICIPACOES S.A. - BNDESPAR|00.383.281/0001-09|016772|B|Veículo de participações financeiras; não selecionar controlador BNDES pela subsidiária.|137660 / 146253|
|43|CIA PARTICIPACOES ALIANCA DA BAHIA|01.938.783/0001-11|018708|A|Holding com 100% da seguradora Aliança no FRE 2024; pessoa distinta da seguradora cujo registro foi cancelado 2024.|138646 / 148434|

## C — 12 securitizadoras, sem correspondência principal admitida

Onze ativas e AUZZA suspensa integram o universo descritivo adotado. Não preencher ausência IF.data com DFPCVM, balanços próprios ou valores de patrimônios separados. Ausência de âncora direta nesta pesquisa não certifica inexistência de dados ou de controladas. Securitização permanece atividade própria; não presumir aplicação de métricas bancárias.

| Nº | Companhia | CNPJ | CVM | Cat. | Situação no corte | Unidade IF.data | IDs FCA 2024 /2025 |
|---:|---|---|---:|:---:|---|---|---|
|44|BRAZILIAN SECURITIES CIA SECURITIZACAO|03.767.538/0001-14|018759|B|Ativo|Não admitida|148281 / 148664|
|45|SECME - COMPANHIA SECURITIZADORA DE CRÉDITOS IMOBILIÁRIOS|07.119.838/0001-48|019720|B|Ativo|Não admitida|139308 / 147002|
|46|PDG COMPANHIA SECURITIZADORA|09.538.973/0001-53|021644|B|Ativo|Não admitida|135460 / 145066|
|47|INFRASEC SECURITIZADORA S.A.|10.488.244/0001-19|021750|B|Ativo|Não admitida|135777 / 148013|
|48|LEADS CIA. SECURITIZADORA|21.414.457/0001-12|023558|B|Ativo|Não admitida|137999 / 152313|
|49|Travessia Securitizadora S.A.|26.609.050/0001-64|024082|B|Ativo|Não admitida|138541 / 148435|
|50|CIA SEC DE CRÉDITOS FINANCEIROS CARTÕES CONSIGNADOS I|27.137.879/0001-74|024147|B|Ativo|Não admitida|141802 / 144581|
|51|CIA SECURITIZADORA DE CRED. FIN. CARTÕES CONSIGNADOS II|35.522.178/0001-87|026107|B|Ativo|Não admitida|— / 144582|
|52|TRAVESSIA SECURITIZADORA DE CRÉDITOS FINANCEIROS S.A.|38.042.694/0001-00|025240|B|Ativo|Não admitida|138542 / 148237|
|53|PORTO DE VITORIA COMPANHIA SECURITIZADORA DE CREDITOS FINANC|40.997.635/0001-20|026239|B|Ativo|Não admitida|138538 / 148210|
|54|Travessia Securitizadora de Créditos Mercantis VI S.A.|43.335.774/0001-86|026824|B|Ativo|Não admitida|138539 / 148205|
|55|AUZZA SECURITIZADORA S. A.|27.956.690/0001-03|024333|B|Suspenso desde 16/08/2024|Não admitida|— / 149827|

Cartões Consignados II26107: FCA 2025ID 144582, ref 01/01/2025, B/Ativo desde 29/07/2021. AUZZA24333: FCA 2025ID 149827, ref 01/01/2025, B desde 19/01/2018, Suspenso desde 16/08/2024. Não são casos sustentados apenas pelo cadastro corrente.

## As 24 unidades financeiras no corte

São 16 conglomerados e 8 independentes,20B1 + B2 e 4 não bancárias(Porto N1, DMN1, Oliveira N2, Cielo N4). TI2 é a perspectiva Conglomerados Financeiros e Instituições Independentes. Prudencial/individual permanecem próprios. Código distinto não certifica independência econômica ou ausência de sobreposição.

| Código financeiro 2024 | Tipo | Companhias CVM associadas |
|---|---|---|
|`00997185`|Instituição independente|021610|
|`01027058`|Instituição independente|021733|
|`04902979`|Instituição independente|000922|
|`04913711`|Instituição independente|001171|
|`07237373`|Instituição independente|001228|
|`13009717`|Instituição independente|001120|
|`13220493`|Instituição independente|025860|
|`36113876`|Instituição independente|026417|
|`C0010045`|Conglomerado financeiro|000906, 019640|
|`C0010069`|Conglomerado financeiro|019348, 007617, 014214|
|`C0020152`|Conglomerado financeiro|001325, 008540, 001309|
|`C0030159`|Conglomerado financeiro|001155|
|`C0030173`|Conglomerado financeiro|001210|
|`C0030290`|Conglomerado financeiro|024600|
|`C0030379`|Conglomerado financeiro|020532, 021466|
|`C0030881`|Conglomerado financeiro|020729|
|`C0031976`|Conglomerado financeiro|014206|
|`C0041856`|Conglomerado financeiro|020958|
|`C0049906`|Conglomerado financeiro|001023|
|`C0049944`|Conglomerado financeiro|022616, 021199, 001350|
|`C0050304`|Conglomerado financeiro|020567|
|`C0051444`|Conglomerado financeiro|016659|
|`C0051987`|Conglomerado financeiro|020796|
|`C0052357`|Conglomerado financeiro|006076|

## Pendências e casos reservados

- **Invesc 15199** e **CADIP 15717**: fora das 55; definição setorial para veículos públicos permanece pendente. Registros B no corte sustentados; ausência IF.data não foi motivo da reserva. CADIP tem data B01/01/2010 no FCA versus 24/06/2010 no CAD, ambas anteriores ao corte; divergência não resolvida.
- **SIMPAR 25003/BBC**: fora das 55, decisão setorial sobre holding de logística com braço financeiro permanece própria. BBC financeiro 01852137, B1/I, diferente de C0084480 prudencial e do homônimo inativo 09777383. Inventário TI2 contém 38 trimestres 201409–202412, com lacunas; não consolidado SIMPAR nem controle histórico certificado.
- **REAG Trust 27634, Wealth 27685, Asset Management Participações 27561**: tinham registro em 2024, mas atividade/perímetro financeiro no corte pendentes; descrições de tecnologia/imóveis não podem ser substituídas por nomes/reorganizações 2025. Não incluídas nas 55. **REAG Investimentos/Get Ninjas 25887** conserva a exceção anterior de reorganização 2025.
- **IFIN 26905 e MNLT 26611**: atividade/perímetro pendentes; rótulo de securitização/investimentos não certifica correspondência. MNLT cessou adquirência 2018 e não recebe Stone por vínculo com empresa irmã. Betapart/Habitasul conservam exclusões de atividade anteriormente fundamentadas.
- Cancelamentos anteriores ao corte permanecem motivos de exclusão, inclusive Alfa Banco/Financeira/Consórcio, PAN Financeira, Alper e seguradora Aliança. Não confundir PAN Financeira com Banco PAN nem seguradora Aliança com holding Aliança.
- Registros CVM legados ITH 1279(cancel 1998) e BMG 1716(cancel 1994), no mesmo CNPJ, não cancelam registros correntes 19348/24600. Identidade cadastral exige CNPJ + CVM. Cancelamentos posteriores de PAN, DM, Oliveira, Nacional e outros não retroagem.

## Handoff para o futuro recálculo — ainda não executado

1. Ler esta nota e o protocolo vigente. Usar as 55 como universo descritivo e as 32 do grupo A como companhias com associação admitida, com 24 códigos apenas no corte de dezembro de 2024. As 23 sem correspondência continuam sem unidade principal admitida. Não associar por nome aproximado, completar com saldos CVM/B3 ou escolher um controlador por conveniência.
2. Aguardar a conclusão das outras implementações e pesquisas indicadas por João e seu pedido explícito à tarefa que fará os recálculos; então abrir o contrato/Issue dessa execução. A Issue 142 é documental e não autoriza a execução. Conferir as correções mais recentes nas Issues 3, 127, 130 e 133–141, no código, perfis e ledgers vigentes. Não voltar a fórmulas ou janelas antigas porque esta nota é nova.
3. Validar o pertencimento por trimestre a partir das operadoras e do cadastro contemporâneo, preservando o mapa anual e os eventos da Issue 125. Não congelar os 24 códigos de 2024 nos 60 trimestres: PAN, DM, BR Partners e Daycoval mudam unidade ou perímetro. Nacional não recebe o histórico BTG de 2010–2024. Holdings não retroprojetam seu controle de 2024.
4. Deduplicar por código, perspectiva e trimestre, conservando as companhias na descrição. Não somar controladora/membro ou perspectivas diferentes. Cielo deve ter resultados separados e a sobreposição com BB/Bradesco explicitada; agregar sem verificar o perímetro continua pendente. A opção de 23 códigos sem Cielo discutida na pesquisa era uma proposta conservadora, **não uma decisão de excluir Cielo ou adotar 23 unidades**.
5. Manter indicadores adequados por atividade e regime, bem como as decisões recentes de ROA/ROE em 2019, liquidez L2 e capital C4. BRB em 202209 conserva estados nativos; a pesquisa de fonte alternativa não libera imputação automática. Presença da unidade não garante todos os componentes ou indicadores. Separar ausência, não aplicabilidade, zero e desconhecido.
6. Usar destinos novos para resultados e replay, autenticar fontes e manifestos, revisar cada fatia e a composição final, e comparar com o recorte anterior de 24 companhias/20 unidades. Recalcular a cobertura pertinente quando autorizado; os percentuais de ativos/crédito/PL da Issue 125 continuam históricos e não representam o recorte de 32/24 ou o universo de 55.
7. Informar companhias, códigos e cobertura por período, com janelas, faltantes e eventos. Os 24 códigos de 2024 não são 24 séries homogêneas certificadas. A coorte selecionada em 2024 condiciona a história observada à sobrevivência, registro e vínculo no corte; não representa todas as abertas de cada ano nem o efeito causal da listagem.

## Pesquisa, fontes e proveniência

A investigação examinou 733 registros FCA 2024,71 casos setoriais e 37 holdings Sem Setor Principal; o inventário combinado de 112 identidades incluiu excluídas, estrangeiras e pendentes. Não 112 elegíveis. A decisão adotou uma lista finita 55 entre os casos documentados; outras omissões podem exigir pesquisa posterior, sem mudar silenciosamente a lista.

Cadastro atual é pista, não certificado retrospectivo. FCA 2024 ref 01/01/2024 sozinho não comprova 31/12; FCA 2025 ref 01/01/2025 com datas de alteração e documentosde eventos sustenta o corte quando explicitamente aplicável. Categoriaatual ou nomeposterior não retroage. Fontes abaixo foram lidas na pesquisa de 16/10 e/ou no pacote 125 autenticado; nenhuma coleta financeira nova nesta entrega.

### Fontes cadastrais e nativas

- [Resolução CVM 80, arts 2–3 e conversão de categoria](https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol080.pdf): A/B não equivalem a listagem; mudança A→B não é cancelamento.
- [FCA 2024](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_2024.zip): membro fca_cia_aberta_geral_2024.csv; SHA-256 55ad239eee3a922e25a599f72eb835e0e0a0ae50de0b50c738997143302f5e49 no pacote anterior. IDs nas tabelas permitem localizar cada formulário.
- [FCA 2025](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_2025.zip): membro fca_cia_aberta_geral_2025.csv; SHA-256 cd4616b2fc02f9e94efc4910d45f4627e8c4b3222403fec856601c083fb69bb1, recuperado 14/10/2026T16:16:10.161274Z, status 200. Bradesco Leasing ID 151221, linha 538; Dibens ID 145297, linha 639, com cabeçalho.
- [Cadastro atual CVM](https://dados.cvm.gov.br/dataset/cia_aberta-cad): último dia útil, somente pista/corroborador de eventos, associado por CNPJ + CVM.
- [FRE 2024](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_2024.zip): participações societárias; SHA-256 0c252f04d8da3c7fabf5e9c9eb13b504f4f9ddf2a09b808cb665f334eadeb35d. Aliança Participações linhas 354–359; SIMPAR 1108–1109; REAG Capital 2442–2451/ID 146565. Participação sem campo de controle não recebe certeza adicional.
- [Cadastro IF.data 202412](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/IfDataCadastro(AnoMes=@AnoMes)?@AnoMes=202412&$format=json): usados bytes locais; manifest de cadastro 874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1. Valores TI2 nativos 202412: arquivo ifdata_202412_tipo2.json.gz, SHA-256 d0980ab42f2ec2e1f55d6aa06c42103faee0a0c6fe8a1b36ecfae58b208eb019. Financeiro exclusivamente IF.data, sem copiar saldos de DF societária.

### Fontes de identidade, controle e eventos

- [Oliveira Trust ITR 2T2025](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/befa7afd-cff6-3fcd-793d-4647b089e646?origin=2), nota 2, pp 21–22: coluna explícita 31/12/2024, controle indireto 100% da DTVM. [Documento TJAM](https://www.tjam.jus.br/images/Sistemas-capital/Conv%C3%AAnios_-_Data_05-04-2022.pdf) distingue OTSA e OTParticipações por CNPJ.
- [Nacional DF 3T2024](https://www.bnsa.com.br/assets/documents/balance-sheet/demonstracoes-financeiras-br-gaap-3q24.pdf), pp 3/11, e[FR13/09/2024](https://www.bnsa.com.br/assets/documents/material-facts/fato-relevante-240913.pdf): saída liquidação 14/08 e controle BTG concluído 15/08/2024. Nenhum valor desses documentos foi usado como IF.data.
- [Santander 20-F 2024](https://cms.santander.com.br/sites/WRI/documentos/url-20f2024-en/25-02-28_212447_20f_2024.pdf), F-60: RCI controle conjunto. [Santander DF 2024](https://cms.santander.com.br/sites/WRI/documentos/url-DF-IFRS-4T24/25-02-28_211350_demonstracoes_financeiras_ifrs_4t24.pdf), nota 5: participação/controle conjunto, sem substituir perímetro nativo.
- [Dibens FRE 2025](https://www.itau.com.br/download-file/v2/d/7fa32f0b-e69c-44ad-9879-7ec6d8b9a6fc/9f5a0e67-d94a-688e-dd89-c3ec6764a1e1?origin=1), p 36: controlada integral e ausência de atividade operacional referidas a 31/12/2024.
- [Banco XP DF 2024](https://publicidadelegal.monitormercantil.com.br/wp-content/uploads/2025/04/BANCO-XP-S-A-Balanco-2024.pdf), notas 11/17, e[XP, documento SEC 2024](https://www.sec.gov/Archives/edgar/data/1787425/000095010325002120/dp225026_ex9901.htm), nota 1.3: direção do controle e reorganização novembro 2024. Não atribuir grupo XP à filha aberta automaticamente.
- [MNLT DF 2024](https://docs.stone.com.br/wp-content/uploads/2025/03/MNLT-ITR-4T24.pdf): cessação adquirência 2018, sem selecionar Stone. [SIMPAR 2024](https://automob.com.br/wp-content/uploads/2025/08/Simpar2024-PORT_.pdf): braço financeiro não é consolidado SIMPAR.
- [Nota anterior 125](fixed-financial-sample-2024-20261014.md): provas B3/BRPartners/Porto/Itaúsa, BB/Bradesco/Cielo, exceções Bemge/Alfa e eventos; permanece histórico auditado, não é substituído retroativamente.

### Integridade e revisões

Pacote 125 manifest **bf54640a70964ca8468cdefc1fc2aaf53d1aab8985779005de21fc9b847467eb**,221 arquivos autenticados. Auditoria privada 16/10: audit-review.csv, SHA-256 00789712911560928fb68d76eb4b021c0bce27bae4ca1f0a959e2428e3a533dd; candidates.json, SHA-256 78880dc58d275c8bf551f6c81621952d3644bd7a7943890db5fb1d72a3ef6c56; omissions.json, SHA-256 5acb8d5d13e2782b671033f8dcd899f04b7ef6ab5fe7bb49e15408a341386b24. Contêm 112 identidades e IDs/URLs/localizadores; arquivos privados não acompanham clone. As tabelas públicas desta nota preservam as 55 identidades e a síntese de controle, sem exigir o pacote privado para conhecer a lista aprovada.

A pesquisa teve revisão independente por fatias e composição, com correções de CAD legado ITH/BMG, Consignados II e AUZZA. A entrega documental 142 tem revisão e checks próprios na Issue; revisão da pesquisa não é aprovação automática de um diff posterior. Esta nota não declara execução de indicadores, publicação Git ou integração; esses estados requerem evidência própria na Issue 142.

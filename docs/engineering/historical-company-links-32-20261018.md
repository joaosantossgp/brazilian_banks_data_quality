# Vínculos históricos das 32 companhias — pesquisa de 18/10/2026

[Issue 156](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/156). Pesquisa factual e registro de execução autorizada, em pacote derivado separado e sem recálculo de fórmulas. Coorte de referência de 2024 preservada. A primeira fatia corrige Oliveira Trust; a segunda audita a proveniência das outras 31, sem declarar certificação societária universal.

## Pesquisa pré-execução preservada

As seções iniciais registram o diagnóstico anterior à implementação. Expressões como “hoje apenas202412”, “proposta” e “regra futura” referem-se àquela etapa. O resultado autorizado, os pins e a revisão concluída estão em “Execução e verificação das duas fatias”, ao final.

## Oliveira Trust: identidade e conclusão

A companhia selecionada é **Oliveira Trust S.A., CNPJ 21.110.778/0001-23, CVM 26417**, anteriormente Confiance Participações S.A. A operadora é **Oliveira Trust Distribuidora de Títulos e Valores Mobiliários S.A., CNPJ 36.113.876/0001-91**, código IF.data `36113876`. Oliveira Trust Participações S.A., CNPJ 05.310.054/0001-77, continua pessoa distinta; não substituir a emissora por essa identidade. Identidades/corte CVM conservam a [nota do universo aprovado](cvm-open-financial-universe-2024-20261016.md#ampliação-em-relação-à-pesquisa-anterior).

A **ITR 1T2021, notas 1–2, PDF p. 28 / página CVM 27**, comprova a reorganização no primeiro trimestre de 2021 e o controle indireto integral da DTVM em 31/03/2021. A tabela compara com 31/12/2020, sem essa participação. A nota 20, PDF p. 54 / CVM 53, descreve a conferência das ações MCFL/DTVM em 29/01/2021. O registro de companhia aberta é outro evento: não deve determinar sozinho a data inicial do vínculo da coorte de 2024. [ITR 1T2021](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/97dee979-e31c-65b2-f10d-352b67fc40b6?origin=1).

A **DF 2021, notas 1–2 e 21, PDF pp. 21–24 e 53**, informa constituição da holding em setembro/2014, reorganização em 2021 e distinção entre controle pelos mesmos acionistas e controle pela holding. Nota 2 menciona 31/03/2021 para a estrutura integral via MCFL; nota 21 descreve atos de 29/01/2021. Isso não altera o fechamento trimestral inicial candidato, 31/03/2021, mas impede escolher uma data diária única sem examinar todos os atos. Há inconsistências percentuais literais na narrativa histórica da nota 2; a proposta não depende delas. [DF 2021](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/c2390542-6cf9-9b60-715f-644ea37e4287?origin=2).

**Proposta factual para correção:** admitir a operadora vinculada nos **16 fechamentos de 202103–202412**, com fontes por data abaixo. Hoje apenas 202412 é admitido; seriam **15 novos trimestres de vínculo**. Não é necessário presumir continuidade apenas entre duas DFs anuais. Há documento próprio para cada fechamento; o de 4T2023 exige o corroborador explícito explicado adiante. Esta pesquisa não implementa a alteração.

## Cobertura da janela completa: 60 trimestres

|Janela|Trimestres|Conclusão para esta identidade de holding|
|---|---:|---|
|201003–201406|18|Anterior à constituição documentada em setembro/2014; a existência anterior da DTVM não cria a holding retrospectivamente.|
|201409–202012|26|Não admitir vínculo positivo retrospectivo. A documentação descreve reorganização em 2021; controle comum pelos acionistas não é controle pela holding. Comparativos 2020 documentam perímetro anterior. Ausência de prova específica para um fechamento não vira certeza universal de ausência de relação.|
|202103–202412|16|Controle indireto comprovado por fechamento; candidato finito a membership, condicionado ao cadastro contemporâneo IF.data e à verificação pelo motor existente.|

A disponibilidade nativa da DTVM nos 60 trimestres é uma entrada já identificada pelo inventário do projeto; não foi recalculada nem certificada por esta pesquisa documental. A regra futura deve conferir cadastro/código contemporâneo por perspectiva, preservando estado desconhecido/conflito se algum fechamento não corroborar o vínculo. Não atribuir às demonstrações da emissora os saldos da DTVM como se fossem consolidados societários.

## Fontes por fechamento

Todas as páginas abaixo são **páginas físicas PDF, contagem iniciada em 1**. ITRs exportadas pela CVM podem apresentar rodapé `PÁGINA` iniciado em zero e paginação interna adicional. As fontes foram recuperadas em 18/10/2026 UTC, HTTP 200, sem autenticação; cada arquivo tem recibo URL/UTC/status/headers/SHA-256 e cópia privada fora do Git.

|Referência|Fonte primária|Página PDF da nota 2|SHA-256 do documento|Evidência/ressalva|
|---|---|---:|---|---|
|202103|[ITR/DF 1T21](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/97dee979-e31c-65b2-f10d-352b67fc40b6?origin=1)|28|`67fea9bda4bf681c3eb02afd4e1f8ada757dd6a76f2e5de9e279c4874321d3f8`|Controle indireto 100% na nota 2.|
|202106|[ITR/DF 2T21](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/b603da09-cb44-528b-921d-071f37bbc479?origin=1)|31|`45fa08fc7713e56c3e861732c68f10d698522b820db0926d4f7453d6f1c49a20`|Controle indireto 100% na nota 2.|
|202109|[ITR/DF 3T21](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/30ac1c23-2501-7a84-fe81-70fc14219fb3?origin=1)|17|`a92372961e6612a9c1773769055f1767ab9e24cb5bf2e24d5c455d9ea3f1c73d`|Controle indireto 100% na nota 2.|
|202112|[ITR/DF 4T21](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/c2390542-6cf9-9b60-715f-644ea37e4287?origin=2)|22|`e6583598badc377c48376f24500d65b1a10ebe03f6d155a58ed53c778ff78c51`|Controle indireto 100% na nota 2.|
|202203|[ITR/DF 1T22](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/8254354a-cf09-777e-8537-69d30f2f6853?origin=2)|33|`6d4ffe8152beb3ab47432f3b141a8bac96d34d31ac0f20304605f10bb429e6f0`|Controle indireto 100% na nota 2.|
|202206|[ITR/DF 2T22](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/40efe214-3411-2ee0-bf7f-18ce2d00599e?origin=2)|27|`d6af45752f8b43e667868215236b8f8d0e3fcb579262e05c69dc88647c5b3079`|Controle indireto 100% na nota 2.|
|202209|[ITR/DF 3T22](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/3200848a-b51d-14bf-0ca0-bdee7f12ea35?origin=2)|25|`0d225f2c6cf678e0176d9876097ace54c1dbdd2fa1f8e9d7d212e9f8d4eafb98`|Controle indireto 100% na nota 2.|
|202212|[ITR/DF 4T22](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/49086c5b-dc14-b5e1-994c-d98131d5d7a1?origin=1)|21|`fab40191da49c2f8f8ed0cfa677cbf864c9f7630b745ec196b2aec3d2d6039e9`|Controle indireto 100% na nota 2.|
|202303|[ITR/DF 1T23](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/60f85bf3-88af-cb50-6dc6-4fa204f372df?origin=1)|23|`92dfdeafe2150a7d829152d6ae08a21abb94dd28cf7d89827dab2badfc65bfa0`|Controle indireto 100% na nota 2.|
|202306|[ITR/DF 2T23](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/d545d3fa-60b5-700a-155f-3dbf46f2c7b5?origin=2)|24|`cd4298f6750e329cc8dab39b6cfbea07c272d9223e1dd86f2c7a803917f73b40`|Controle indireto 100% na nota 2.|
|202309|[ITR/DF 3T23](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/58af4019-f10e-6c57-627f-275210d61244?origin=2)|24|`6e2e8402be74d78d0beac2d8163260de0a6e929faf02eebce7bf1d8164d31d40`|Controle indireto 100% na nota 2.|
|202312|[ITR/DF 4T23](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/5d55a7f6-ff44-04c7-9845-d45fe79f28c2?origin=1)|24|`46bb74f3378854abe23986b76b812e58f6ae656475fe18eb6571b1e0abe362c4`|Cabeçalho nativo errado; corroborar com 1T24 e 4T24.|
|202403|[ITR/DF 1T24](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/07d0df2f-614b-4eec-73ef-92f415bd02f4?origin=2)|24|`c2001a904739d4c08c6f9f60559040983963b913b2967fd5fd40835e470caffe`|Controle indireto 100% na nota 2.|
|202406|[ITR/DF 2T24](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/d3dceff9-e85a-0adf-f05e-bced4bf1670e?origin=1)|25|`a58ff365ab60bf34a2c9f8c15516333236e7dc4f55ddfd05f7120ca236af04cc`|Controle indireto 100% na nota 2.|
|202409|[ITR/DF 3T24](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/9b07630d-0f2d-1df2-feae-8f53994a85e9?origin=2)|25|`7002bc671e406219bfe5feb4e0619b8628a353031220ec87976030d6c17a8466`|Controle indireto 100% na nota 2.|
|202412|[ITR/DF 4T24](https://api.mziq.com/mzfilemanager/v2/d/410e719e-47a0-4f99-806d-605be31a69cc/336f053c-0063-e819-b2ad-166ca3ea478e?origin=2)|34|`e03d93955d765db02749314b9d008aa13a73305e89875b351f22195d14668fb4`|Controle indireto 100% na nota 2.|

**4T2023:** a tabela da DF 2023, p. 24, traz literalmente `31/12/2013` no cabeçalho, apesar de o documento se referir ao exercício de 2023. Isso foi conferido na imagem renderizada; não é artefato de extração. Não corrigir silenciosamente o literal nem usá-lo para provar 2013. O controle em **31/12/2023** é corroborado explicitamente pela coluna comparativa da **ITR 1T2024, p. 24**, e da **DFP 2024, PDF p. 34 / nota impressa p. 25**. Essa última também comprova 31/12/2024. A decisão temporal usa os corroboradores, preservando a anomalia da fonte 2023.

## Regra candidata e limites para o plano

1. Adicionar somente os 15 vínculos antes ausentes entre 202103 e 202409, conservando 202412 e todas as observações financeiras originais. Avaliar as perspectivas Financeiro, Individual e Prudencial por seus próprios códigos contemporâneos; a prova de controle societário não equipara os perímetros.
2. Conservar as frações de indicadores existentes. Membership muda coortes, contagens e agregados por recorte; isso pode ser recomposto seletivamente sem avaliar fórmulas novamente. Não prometer valores ou percentuais antes dessa recomposição autorizada.
3. A série vinculada em 202103 pode conter indicadores de 12 meses cujos componentes financeiros antecedem a aquisição. Identificar isso como desempenho da unidade hoje vinculada, não resultado de 12 meses sob controle da holding. Se a pergunta for desempenho sob controle durante toda a janela, precisará de filtro acadêmico adicional explícito.
4. Não ampliar automaticamente para 2010–2020 com base em marca, acionistas comuns, mesma DTVM ou demonstrações combinadas. Fazer isso mudaria a unidade histórica/pergunta; a pesquisa não autoriza essa opção.

## Proveniência e verificações desta fatia

Destino privado canônico: `data/raw/historical-links32-research-20261018/oliveira/` no checkout de dados deste computador. `verified-quarter-*.pdf` e `df-2021.pdf` são as referências finais; seus arquivos `.receipt.json` preservam cabeçalhos e hashes. `quarter-document-index.json` registra o primeiro lote 2022–2024; recibos individuais cobrem também os documentos acrescentados de 2021 e 1T2022. `oliveira-60-quarter-research-states.json` é um inventário **de pesquisa**, não membership aceito.

A primeira extração do carrossel omitiu um espaço em `4T24 ` e gerou nomes provisórios deslocados (`df-*`, exceto `df-2021.pdf`). Esses arquivos foram preservados para diagnóstico, mas **não são referência de períodos**. A segunda extração (`verified-quarter-*`) considerou o espaço, conferiu a data dentro de cada PDF e registrou os hashes acima. O link de DF de 4T2024 está vazio na homepage; foi usado o ITR/DFP adjacente, com a data 31/12/2024 explicitamente verificada no PDF. As falhas de ferramenta/dependência foram preservadas no histórico da execução; não exigiram instalar biblioteca nova.

Foram conferidas as tabelas da nota 2 por extração local e, para 1T2021 e a anomalia 4T2023, também por renderização visual. Nenhuma fonte secundária serviu para aceitar um vínculo. A minuta de prospecto CVM de agosto/2021 serviu apenas à descoberta e foi substituída por ITR/DFs identificadas; não se tomou sua hipótese de oferta como listagem realizada. Revisão independente e adoção do plano ainda cabem ao integrador desta entrega.


## Auditoria preliminar dos vínculos armazenados das 32

Consulta determinística, sem avaliar fórmulas: 32 identidades × 60 trimestres = 1.920 posições nominais no pacote de membership autenticado pela composição aceita `ce57545b643d9efcfbb09ee26234c97f131080627d42622c2b4cfbf998f7c524`. As 28 companhias fora dos quatro casos abaixo têm unidade financeira presente nas 60 datas. Presença e vínculo técnico não são nova certificação societária; a próxima fatia revisa a proveniência e os eventos existentes, sem considerar a etiqueta `preserved_sample125` suficiente por si.

|Caso|Referências com unidade financeira presente|Causa registrada / exame necessário|
|---|---:|---|
|BR Partners|51/60|Sem alvo nos nove trimestres 201003–201203; transição entre grupo e banco individual nos demais. Verificar constituição/início de reporte e cadeia já admitida.|
|Cielo|29/60|Reporte financeiro observado apenas desde 201712. Distinguir ausência de divulgação nesta perspectiva de inexistência da companhia.|
|Oliveira Trust|1/60|59 datas bloqueadas como controle histórico desconhecido; pesquisa acima sustenta 15 novos candidatos, sem 2010–2020.|
|Banco Nacional|2/60|Associação BTG só em 202409–202412, após evento datado; manter liquidação/perímetro anterior separados.|

As mudanças de alvo também incluem PAN, DM e Daycoval, além de BR Partners; são pontos de revisão mesmo sem lacuna de presença. Companhias que compartilham um alvo não multiplicam suas contribuições. A matriz privada preserva cada posição nominal e sua referência, com resumo por companhia, períodos ausentes e alvo por perspectiva. Os oito acréscimos ao universo e os vínculos legados conservam suas fontes próprias; não estão todos certificados por esta consulta.

## Significado de S1 e recorte observado

No corte Financeiro/202412, Sr analítico S1 contém 12 unidades: cinco conglomerados da seleção (BB, Bradesco, Itaú, Santander e BTG), Caixa e seis IPs. As cinco unidades selecionadas representam 11 companhias nominais: BB; Bradesco/Bradesco Leasing; Itaú Unibanco Holding/Itaúsa/Dibens; Santander/RCI; BTG/PAN/Nacional. Prudencial separadamente contém os seis conglomerados, com cinco na seleção. Não somar as duas perspectivas nem tomar as 12 unidades financeiras por 12 conglomerados S1 distintos.

A categoria conserva significado prudencial oficial, não vira faixa própria calculada sobre AT/PIB financeiro. A [Resolução4.553 original](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50335/Res_4553_v1_O.pdf), arts2–4, define o S1 por porte de pelo menos10%doPIB ou atividade internacional relevante (ativos consolidados no exterior de pelo menosUS$10bilhões), com enquadramento consolidado para membros de conglomerado. Porte usa exposição total; ativo total só na hipótese normativa de substituição. O [BCB](https://www.bcb.gov.br/detalhenoticia/16073/nota) descreve alinhamento integral aos padrões de Basileia para S1. Sr analítico derivado atribui o segmento via vínculo datado, sem certificar que a unidade financeira isolada cumpre o limiar nem que comprovamos conformidade a todos os requisitos. Aplicar versão/data normativa pertinentes; não retroagir Sr a 2010–2016.

## Estado da revisão

Revisão independente factual Oliveira: PASS sobre a versão original da nota, com conferência dos16PDFs/páginas/recibos e render das fronteiras1T2021/4T2023. O apêndice de auditoria é uma consulta adicional do integrador, não promoção. João aprovou o plano e duas fatias em 18/10, com execução nativa, revisão independente por fatia e PR. O pacote original e o ponteiro foram preservados durante a execução.



## Proveniência da auditoria das outras31

A matriz deriva da [pesquisa125 e sua verificação anual](fixed-financial-sample-2024-20261014.md#verificação-anual-e-disponibilidade-trimestral), ampliada pela [pesquisa142, lista nominal e fontes CVM/RI](cvm-open-financial-universe-2024-20261016.md). Pacote125 autenticado: `bf54640a70964ca8468cdefc1fc2aaf53d1aab8985779005de21fc9b847467eb`,221arquivos conferidos. Os estados anuais vêm de `annual-verification.json` e os caminhos trimestrais de `company-quarter-map.json`; cada aresta conserva ID/documentoFRE, membro/linha, data, URL e hash da captura original. A matriz sintetiza esses estados, sem convertê-los em prova de controle no encerramento.

Entradas da auditoria: composição `ce57545b643d9efcfbb09ee26234c97f131080627d42622c2b4cfbf998f7c524`, membership `e3c18fd7d21931a508bd26b3b79c5590258f5e4afed0b4e4de573833c68001bb`. Localizadores adicionais2024 preservados: `source-inputs/issuer-research/bancob3-2024.pdf`, p.1; [DF BRPartners2024](https://estadaori.estadao.com.br/wp-content/uploads/2025/02/br-advisory-partners-participacoes-sa-balanco-2025-02-12_23-59-06.pdf), p.7, com evento de2012 na p.3; Porto, registroFRE2024 de participação integral emPortoseg, conforme locators da pesquisa125; [DF IUPAR2024](https://estadaori.estadao.com.br/wp-content/uploads/2025/03/iupar-itau-unibanco-participacoes-sa-balanco-2025-03-01_08-20-25.pdf), p.1, e rota IUPAR→ITH noFRE2024. Essas provas corroboram2024, sem preencher automaticamente estados anuais ausentes ou de mera participação.

## Matriz de evidência existente e limite

| Companhia / CNPJ | Presenças financeiras | Alvos por intervalo | Evidência e limite |
|---|---:|---|---|
| BCO BRASIL S.A. / 00000000000191 | 60/60 | 201003–202412: `C0049906` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BRB BANCO DE BRASILIA S.A. / 00000208000100 | 60/60 | 201003–202412: `C0031976` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| PORTO SEGURO S.A. / 02149205000169 | 60/60 | 201003–202412: `C0051444` | 13 caminhos anuais; 2023 desconhecido; 2024 participação no mapa 125. Portoseg não equivale ao consolidado segurador Porto. A prova adicional 2024 não resolve os anos anteriores. |
| BCO AMAZONIA S.A. / 04902979000144 | 60/60 | 201003–202412: `04902979` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO ESTADO DO PARA S.A. / 04913711000108 | 60/60 | 201003–202412: `04913711` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO NORDESTE DO BRASIL S.A. / 07237373000120 | 60/60 | 201003–202412: `07237373` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| B3 S.A. - BRASIL, BOLSA, BALCÃO / 09346601000125 | 60/60 | 201003–202412: `00997185` | 13 caminhos anuais explícitos; 2023/24 registram participação sem controle certificado no mapa 125. A DF 2024 p. 1 corrobora controle integral em 2024. Banco B3 não equivale ao consolidado B3. |
| BR ADVISORY PARTNERS PARTICIPAÇÕES S.A. / 10739356000103 | 51/60 | 201003–201203: `None`; 201206–202009: `C0051822`; 202012–202412: `13220493` | Controle da holding não estabelecido em 2010–2020 no mapa 125; caminhos em 2021/22 e participação em 2023/24. DF 2024 p. 7 prova controle indireto no corte. Constituição, autorização, reporte e controle têm datas distintas. |
| BCO ESTADO DE SERGIPE S.A. - BANESE / 13009717000146 | 60/60 | 201003–202412: `13009717` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO MERCANTIL DO BRASIL S.A. / 17184037000110 | 60/60 | 201003–202412: `C0020152` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BANESTES S.A. - BCO EST ESPIRITO SANTO / 28127603000178 | 60/60 | 201003–202412: `C0030159` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO ABC BRASIL S.A. / 28195667000106 | 60/60 | 201003–202412: `C0041856` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO BTG PACTUAL S.A. / 30306294000145 | 60/60 | 201003–202412: `C0049944` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| Mercantil Financeira S.A. - Crédito, Financiamento e Investi / 33040601000187 | 60/60 | 201003–202412: `C0020152` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO MERCANTIL DE INVESTIMENTOS S.A. / 34169557000172 | 60/60 | 201003–202412: `C0020152` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO PAN S.A. / 59285411000113 | 60/60 | 201003–202103: `C0031323`; 202106–202412: `C0049944` | C0031323 até 202103; BTG/C0049944 desde 202106. Aquisição de participação em 2011 e mudança de consolidação em 2021 são eventos distintos. |
| BCO BRADESCO S.A. / 60746948000112 | 60/60 | 201003–202412: `C0010045` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| ITAU UNIBANCO HOLDING S.A. / 60872504000123 | 60/60 | 201003–202412: `C0010069` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BANCO BMG S/A / 61186680000174 | 60/60 | 201003–202412: `C0030290` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| ITAÚSA S.A. / 61532644000115 | 60/60 | 201003–202412: `C0010069` | 13 caminhos anuais; 2023/24 desconhecidos no mapa 125. A rota IUPAR→ITH tem prova adicional 2024. Participação direta minoritária não substitui essa rota nem resolve 2023. |
| BCO PINE S.A / 62144175000120 | 60/60 | 201003–202412: `C0050304` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO SANTANDER (BRASIL) S.A. / 90400888000142 | 60/60 | 201003–202412: `C0030379` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| DM FINANCEIRA S.A. - CRÉDITO, FINANCIAMENTO E INVESTIMENTO / 91669747000192 | 60/60 | 201003–202209: `91669747`; 202212–202412: `C0052357` | Operadora 91669747, Finansinos/DM; independente até 202209 e conglomerado desde 202212. Identidade persistente não certifica perímetro constante. |
| BCO ESTADO DO RIO GRANDE DO SUL S.A. / 92702067000196 | 60/60 | 201003–202412: `C0030173` | Identidade direta da emissora/operadora e pertencimento ao alvo no cadastro contemporâneo. Sustenta correspondência analítica nativa; não certifica perímetro constante ou comparabilidade econômica de todos os componentes. |
| BCO DAYCOVAL S.A. / 62232889000190 | 60/60 | 201003–201509: `62232889`; 201512–202412: `C0051987` | Identidade bancária direta; independente até 201509 e conglomerado desde 201512. Conservar a mudança de perímetro. |
| PARANA BCO S.A. / 14388334000199 | 60/60 | 201003–202412: `C0030881` | C0030881 nos 60 trimestres; nomes J. Malucelli/Paraná e categorias CVM são fatos próprios. Categoria de 2024 não retroage. |
| CIELO S.A. -  Instituição de Pagamento / 01027058000191 | 29/60 | 201003–201709: `None`; 201712–202412: `01027058` | 29 reportes desde 201712; antes disso, ausência neste recorte financeiro. Companhia constituída em 1995. Controle compartilhado e sobreposição com BB/Bradesco devem permanecer explícitos. |
| BANCO RCI BRASIL S.A. / 62307848000115 | 60/60 | 201003–202412: `C0030379` | Operadora 62307848→Santander nos 60 cadastros. Controle conjunto de 2024 tem fonte própria; não representa balanço RCI isolado nem controle exclusivo Santander. |
| BANCO NACIONAL S.A. / 17157777000167 | 2/60 | 201003–202406: `None`; 202409–202412: `C0049944` | 58 trimestres anteriores sem alvo BTG; apenas 202409/202412 admitidos. FR 15/08/2024 comprova conclusão da aquisição. Não transferir o passado BTG ao Nacional. |
| BRADESCO LEASING S.A. ARREND MERCANTIL / 47509120000182 | 60/60 | 201003–202412: `C0010045` | Operadora 47509120→Bradesco nos 60 cadastros; identidade distinta da homônima 43833821. Alvo de grupo não é balanço próprio Leasing. |
| DIBENS LEASING S.A. - ARREND.MERCANTIL / 65654303000173 | 60/60 | 201003–202412: `C0010069` | Operadora 65654303→Itaú nos 60 cadastros. FRE 2025 p. 36 refere ausência de operação em 31/12/2024; isso não apaga o vínculo nem cria saldo zero. |


## Execução e verificação das duas fatias

A fatia160 gerou membership novo: 45 unidades/períodos alterados, 15 em cada perspectiva Financeiro, Individual e Prudencial. São exclusivamente 202103–202409; 202412 e todos os períodos anteriores permanecem com a seleção anterior. Oliveira tem agora16fechamentos positivos e44anteriores sem alvo admitido. O prudencial usa C0084040 contemporâneo; não é o mesmo perímetro do código financeiro36113876.

Membership: manifest `bedc7294f2576319e8c990291adf82e1e33d40625454e114ab84715cda183465`. Composição derivada: `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`. O lote recompôs810contextos armazenados em782,314s, sem avaliar fórmulas financeiras. O primeiro contexto completo levou0,426s; a medição inicial apenas do redutor levou0,235s. Tempo de cálculo/redução, leitura e gravação do pacote são distintos.

A revisão independente confirmou: hashes dos nove arquivos de membership;60mapas Oliveira; os810payloads financeiros afetados integralmente idênticos após remover somente cinco campos de membership/proveniência;244.001estoques/origens preservados; payloads fora do delta nas nove tabelas com multiconjuntos SHA-256 idênticos, incluindo5.020.240contribuições não atingidas. Conferiu todos os3.240contextos totais (12.960linhas nas quatro coortes), preservando frações, numeradores/denominadores e contagens de unidades. Contagens nominais e recortes abertas/restante mudam pela associação comprovada.

TDD e testes direcionados de população/composição:60PASS em47,137s; regressão adicional do exporter assegura que a nova derivação não apaga o aviso/proveniência da ponte Terra. Revisão independente do código e do delta exporter/template sem bloqueio material após corrigir a recusa de provas nominais duplicadas. As correções Terra/Caixa e os estados de classificação continuam preservados.

A fatia161 auditou a proveniência das31demais identidades e os221arquivos do pacote125 autenticado. Não encontrou outra mudança de alvo comprovada. B3/Porto/Itaúsa/BRPartners conservam lacunas ou participação sem controle integral certificado em parte dos estados anuais legados; os registros societários adicionais de2024 não retroagem. Os alvos técnicos aceitos são preservados, com esse limite exposto no explorador. A aquisição do Nacional pelo BTG em15/08/2024 é corroborada pelo [fato relevante, p.1](https://www.bnsa.com.br/assets/documents/material-facts/fato-relevante-240815.pdf); não cria associação antes do evento.

Tentativas e limites operacionais: o primeiro lote de recomposição foi interrompido sem manifest aceito durante diagnóstico de progresso; a segunda tentativa com instrumentação faulthandler encerrou sem aceite, com saída preservada. A terceira execução normal concluiu. O primeiro verificador amplo falhou por memória512MiB; medidos31,7GiB totais e cerca de7GiB livres, a revisão utilizou2GiB e concluiu em298,511s. Esses resultados não transformam tentativas anteriores emPASS. Pacotes parciais e originais foram preservados, sem sobrescrita.

A conclusão local e a revisão estão demonstradas; publicação, CI, integração e promoção do ponteiro são registradas separadamente naIssue156/160/161 e no encerramento desta entrega. A coorte2024 não mudou e esta auditoria não transforma presença técnica em certificação societária de todos os trimestres.

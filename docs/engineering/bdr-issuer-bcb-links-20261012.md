# Emissores de BDR e unidades BCB — evidência societária datada

Extensão documental da [Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6136084706), de 2026-10-12, pesquisa BDR. Base `f93d37f17898d69713d06f07bb393eb1f2444331`, branch `codex/cvm-b3-history-2010-2024`. Único novo documento público desta fatia; as notas A/B anteriores permanecem congeladas. Impacto arquitetural: nota no destino responsável existente `docs/engineering/`, evidência privada em `.scratch/cvm-b3-history-20261012/bdr/`; sem camada, código público, runtime ou dataset financeiro novo.

**Resultado:** há prova documental útil de instrumentos B3 em 2024 e de controle de operadoras brasileiras por Nu, Inter, XP, Stone e PagSeguro em datas expressas. Essa prova não produz uma relação contínua para os 60 trimestres. Emissor estrangeiro, programa, BDR, custodiante/depositária, operadora brasileira e conglomerado IF.data são objetos distintos. A origem brasileira não foi usada como filtro de descoberta. Ações, units e BDRs conservam a mesma prioridade de investigação, sem decisão de amostra acadêmica.

Os documentos SEC são **declarações do emissor arquivadas na SEC**, não certificação da SEC sobre cada afirmação. A prova composta pode combinar essas declarações com identificadores CVM/BCB e observações B3. Isso exige um contrato de evidência que aceite a composição explicitamente; não se presume que o validador existente já admita essas fontes ou relações.

## Fontes, captura e força de evidência

Aplicadas as instruções locais Feynman `deep-research`/`pdf-explore` e `research`. `/deepresearch` indisponível: usado fallback autorizado de pesquisa primária, leitura dos originais, extrações e proveniência. Foram lidas capa/identidade do declarante, estrutura corporativa, notas de consolidação/participações e eventos relevantes dos documentos SEC, cruzando narrativa e tabelas. PDFs B3 foram mapeados por página; p. 61 do BDI foi também conferida visualmente. Não se adotaram saldos, resultados ou indicadores dos relatórios financeiros incidentais.

| ID | Fonte primária / localizador |
|---|---|
| N | [Nu Holdings, 20-F 2024](https://www.sec.gov/Archives/edgar/data/1691493/000129281425001517/nuform20f_2024.htm), nota 1; nota 3 `Basis of consolidation`, tabela `Schedule of subsidiaries`, cabeçalho 2024/2023/2022; item 4C; evento de cancelamento do programa nível III |
| I | [Inter & Co, 20-F 2024](https://www.sec.gov/Archives/edgar/data/1864163/000162828025020965/intr-20241231.htm), história/reorganização de 23/6/2022; item 4C; tabela `The following table shows the subsidiaries in each year`, colunas 12/31/2024, 12/31/2023, 12/31/2022; nota de planos de opções confirma HoldFin |
| X | [XP Inc., 20-F 2024](https://www.sec.gov/Archives/edgar/data/1787425/000162828025019508/xp-20241231.htm), item 4C, tabela de participações 2024/2023/2022; nota 5 `Group structure`, tabela de controladas indiretas; seção `Our Regulatory Position` |
| S | [StoneCo, 20-F 2024](https://www.sec.gov/Archives/edgar/data/1745431/000162828025019653/stne-20241231.htm), seção 4.1.2 `Subsidiaries of the Group`, pp. F-23/F-24, tabela `Group's equity interest`, colunas December 31, 2024/2023, especialmente Stone IP; offset 901745 no texto derivado |
| P | [PagSeguro Digital, demonstrações de 31/12/2024 arquivadas em 6-K](https://www.sec.gov/Archives/edgar/data/1712807/000162828025006747/a081_pagseguroxfsx6k.htm), nota 1 `General information`; nota 4 `Consolidation of subsidiaries`, primeira tabela `As of December 31, 2024`, pp. internas 14 e 32–35 |
| B | [B3, BDI de 10/12/2024, nº 239](https://arquivos.b3.com.br/bdi/download/bdi/2024-12-10/BDI_02_20241210_en-Us.pdf), 116 páginas; pp. físicas/impressas 60–62, tabela de carteira com ticker/nome/tipo; globais pp. 48 e 89; editais XP pp. 109–110 |
| B21 | [B3, notícia de 28/1/2021](https://www.b3.com.br/pt_br/noticias/bdrs-de-acoes-e-etfs-listados.htm), anúncio de negociação PagSeguro a partir de 1/2/2021 |
| S21 | [B3, edital StoneCo datado de 6/8/2021](https://www.b3.com.br/data/files/10/55/D1/E6/12C1B71027085EA7AC094EA8/STOC31%20-%20090821%20_072_%20-%20Edital.pdf), p. 1: BDR STOC31/DR1, leilão anunciado para 10/8/2021 |
| B23 | [B3, consulta pública 005/2023-VPC](https://www.b3.com.br/data/files/5A/36/45/A0/23836810DE2C7168AC094EA8/CE%20005-2023-VPC%20Consulta%20p%C3%BAblica%20BDR%20nos%20%C3%8Dndices.pdf), 11 páginas, p. física 8/anexo III: exemplos StoneCo DR1, PagSeguro DRN, Nu DR3, XP DR1 e Inter DR2; documento de consulta, não regra final adotada |
| C | [CVM, programas de BDR aprovados](https://sistemas.cvm.gov.br/asp/cvmwww/progdr/progdraprov_Link.asp), listagem capturada pela pesquisa A; posição expressa em 12/10/2026. Cabeçalhos: emissora, nível, custodiante, depositário, espécie, número/data de registro |
| F | [CVM, cadastro corrente de companhias estrangeiras](https://dados.cvm.gov.br/dados/CIA_ESTRANG/CAD/DADOS/cad_cia_estrang.csv), linhas identificadas por CNPJ/CD_CVM; recuperado pelo integrador, corpo autenticado nesta pesquisa. CSV decodificado estritamente como CP1252 após rejeição de UTF-8; sem reparo de bytes |
| D | IF.data `IfDataCadastro`, pacote local aceito `ifdata-cadastro-20261011`, 60 JSONs 201003–202412 e partes Parquet autenticadas no checkpoint B. Aqui se conferem as linhas exatas de 202412 e descobertas nominais ao longo do recorte |

As páginas B3 foram descobertas em resultados de busca apontando para os URLs oficiais acima, sem fabricar uma URL de download. O BDI foi descoberto por consulta `site.b3.com.br Nu Inter XP Stone PagSeguro BDR 2022 2024`. Não houve acesso alternativo aos COTAHIST bloqueados. B é evidência de uma publicação B3 datada, com composição de carteira e editais; **não** é uma série diária de negócios, prova de execução do leilão ou data inicial de listagem.

## Instrumentos e programas: pontos datados

| Emissor estrangeiro | Identificador SEC / auxiliar CVM | Instrumento observado em B, 10/12/2024 | Eventos/fontes e limites |
|---|---|---|---|
| Nu Holdings Ltd. | CIK 1691493; F: CNPJ 24.410.913/0001-44, CD_CVM 80209 | ROXO34, NU HOLDINGS, DRN, p. 61 | C informa nível I BDR/2023/00003, registro 28/6/2023. N declara aprovação da descontinuidade nível III em 28/6/2023 e cancelamento aprovado em 31/10/2023; F registra cancelamento nessa última data. Cancelamento do registro do emissor/nível III não equivale a ausência do BDR nível I observado em 2024 |
| Inter & Co, Inc. | CIK 1864163; F: CNPJ 42.737.954/0001-21, CD_CVM 80217 | INBR32, INTER CO, DR2, p. 61 | C contém nível II BDR/2021/00071 de 29/10/2021 **e outra linha nível I de 2026**. F informa DT_REG do emissor 8/8/2022. São eventos/objetos distintos; não corrigir uma data pela outra. I declara ações Banco Inter listadas de abril/2018 até reorganização de 23/6/2022 |
| XP Inc. | CIK 1787425; CNPJ estrangeiro não estabelecido nesta fatia | XPBR31, XP INC, DR1, p. 62 | C: nível I BDR/2021/00057 de 28/7/2021. Editais B pp. 109–110 anunciam leilão XPBR31 para 11/12/2024. Não substituir por XPBR34 corrente/2025 |
| StoneCo Ltd. | CIK 1745431; CNPJ estrangeiro não estabelecido nesta fatia | STOC31, STONE CO, DR1, p. 61 | S21 confirma instrumento STOC31 em edital de agosto/2021; anuncia leilão, não execução. A linha Stone não foi resolvida na seleção da listagem C. Não substituir por STOC34 de material posterior |
| PagSeguro Digital Ltd. | CIK 1712807; CNPJ estrangeiro não estabelecido nesta fatia | PAGS34, PAGSEGURO, DRN, p. 61 | C: nível I BDR/2021/00002 de 15/1/2021. B21 anuncia negociação a partir de 1/2/2021. A data de registro e a data anunciada de negociação têm significados distintos |

CIK identifica o declarante nos arquivos SEC; os CNPJs em F identificam os emissores estrangeiros registrados, não as operadoras brasileiras. F contém duas linhas Santander com o mesmo CNPJ/CD_CVM no recorte encontrado; não é razão para duplicar um emissor. Ausência de XP/Stone/PagSeguro nesse cadastro corrente não significa ausência de BDR histórico. A listagem corrente C conserva datas anteriores, mas não fornece por si todas as alterações, encerramentos e intervalos de validade.

## Controle das operadoras: fatos explicitamente datados

| Emissor → entidade brasileira | Fato societário documentado | Data que a fonte efetivamente suporta | Localizador e certeza |
|---|---|---|---|
| Nu → Nu Pagamentos S.A. – Instituição de Pagamento | Participação indireta de 100% no capital total | Fechamentos de 2022, 2023 e 2024, separados | N, nota 3, tabela e cabeçalho anual; controle declarado, não interpolação |
| Nu → Nu Financeira S.A. – SCFI | Participação indireta de 100% | Mesmos três fechamentos | N, mesma tabela; nota 1 identifica atividade/país. O item 4C usa redação corrente e não deve substituir a data da tabela |
| Nu → Nu Investimentos CTVM | Participação indireta de 100%; nota 1 diz aquisição em junho/2021 e reconhece denominação anterior Nu Invest | Fechamentos de 2022, 2023 e 2024; evento de aquisição em junho/2021 sem dia fixado nesta pesquisa | N, notas 1/3. No cadastro D de 202412 permanece `NU INVEST CORRETORA DE VALORES S.A.`; a diferença de denominação deve ser preservada |
| Inter & Co → Inter Holding Financeira → Banco Inter S.A. | Holding direta e Banco Inter indireto, 100% cada; reorganização em 23/6/2022 tornou Inter & Co dono indireto de todas as ações do banco | Evento de 23/6/2022 e três fechamentos 2022/2023/2024 | I, história, tabela anual e nota de opções que nomeia HoldFin. Não levar Inter & Co para o período anterior à reorganização |
| XP Inc. → Banco XP S.A. e XP CCTVM | Ambos controlados indiretamente, participação de 100% | Fechamentos 2022/2023/2024 | X, item 4C e nota 5 `Group structure`, tabelas concordantes; autorização para investimento estrangeiro até 100% é outro fato, não substitui participação efetiva |
| StoneCo → Stone Instituição de Pagamento S.A. | Participação do grupo de 100% | 31/12/2023 e 31/12/2024 | S, seção 4.1.2 `Subsidiaries of the Group`, pp. F-23/F-24, primeira parte da tabela (offset 901745); o quadro não atribui nesta leitura cada intermediária da cadeia |
| StoneCo → Stone SCD / Stone SCFI | Tabela declara 100% para SCD em 2023/2024; SCFI 100% em 2024 e traço em 2023 | Somente as colunas explicitadas | S, seção 4.1.2 `Subsidiaries of the Group`, pp. F-23/F-24, continuação (offset 901745 identifica o início da seção). Traço não foi convertido em zero nem em inexistência universal. Pontas nominais em D de 202412: 34590184 e 53505601; identidade completa/cadeia ficam adicionais |
| PagSeguro Digital → PagSeguro Internet IP | 99,99% das ações aportadas em 4/1/2018; controle mantido; participação direta 99,99% no quadro de 2024 | Evento de 4/1/2018 e fotografia de 31/12/2024 | P, notas 1/4. O evento não preenche automaticamente todos os trimestres 2018–2024 |
| PagSeguro Digital → BS Holding → BancoSeguro | BS Holding direto 100%; BancoSeguro indireto 100%; narrativa identifica BancoSeguro como subsidiária de BS Holding | 31/12/2024 | P, notas 1/4, primeira tabela com cabeçalho 2024; não confundir tabela seguinte comparativa de 2023 |

Não se transportaram esses percentuais para 2010. Nomes semelhantes não estabelecem relação societária: StoneCo e StoneX/INTL FCStone são candidatos distintos. A busca exploratória por fragmentos de nomes produziu falsos positivos; somente as entidades explicitamente nomeadas nas fontes de controle entraram no quadro acima. Participação econômica, controle IFRS e direitos de voto são conceitos diferentes; o texto não converte percentuais de capital total em percentuais votantes quando a fonte não o faz.

## Pontas IF.data e CNPJ: composição possível e pendências

Todos os códigos abaixo foram conferidos em D com `Data=202412`; são códigos nativos de oito caracteres, preservados com zeros. A lista não nasce de classificação por nome: o nome serve à descoberta, e a prova societária está nas fontes N/I/X/S/P. A equivalência de identidade entre a entidade nominal dessas fontes e a PJ BCB exige composição documental verificável antes de admissão automatizada.

| Entidade / CodInst em D | Tipo nativo 202412 | Identificação adicional e grau de captura |
|---|---|---|
| Nu Pagamentos / `18236120` | N4, Instituição de Pagamento | [Contrato oficial Nu, cláusula 1.8](https://nubank.com.br/contratos/termos-e-condicoes-emprestimo-pessoal): CNPJ **18.236.120/0001-58**, original HTTP 200 capturado. Identificador auxiliar corrente; não fixa estabelecimento histórico em 2024 |
| Nu Financeira / `30680829` | N1, Sociedade de Crédito, Financiamento e Investimento | Mesmo contrato, cláusula 1.7: CNPJ **30.680.829/0001-43**, original capturado. Base8 concorda; vigência do estabelecimento não retroprojetada |
| Nu Invest Corretora / `62169875` | N2, Sociedade Corretora de TVM | N declara denominação anterior; CNPJ14 não capturado nesta fatia. Não substituir denominação histórica pela atual |
| Banco Inter / `00416968` | B1, Banco Múltiplo | [Página oficial Inter, rodapé corrente](https://inter.co/acesso-rapido/) retornou em busca CNPJ **00.416.968/0001-01**. Auxiliar de descoberta; original da página não capturado. Outra declaração SEC de 2022 com CNPJ foi descoberta, mas seu GET retornou 403 |
| Banco XP / `33264668` | B1, Banco Múltiplo | [Contrato oficial XP, preâmbulo](https://web.xpi.com.br/xp/documentos/contrato-de-abertura-de-conta-banco-xp-s-a/) retornou na busca CNPJ **33.264.668/0002-86**; GET 403. É estabelecimento /0002 observado na busca, não matriz /0001 inventada |
| XP CCTVM / `02332886` | N2, Sociedade Corretora de TVM | [Contrato oficial XP, preâmbulo](https://www.xpi.com.br/documentos/contrato-de-intermediacao/) retornou na busca CNPJ **02.332.886/0001-04**; GET 403. Identificação auxiliar sem original capturado |
| Stone IP / `16501555` | N4, Instituição de Pagamento | [Stone Docs, rodapé](https://docs.stone.com.br/conta-stone/) retornou na busca CNPJ **16.501.555/0001-57**; GET 403. Identificação auxiliar, sem vigência histórica de estabelecimento demonstrada |
| PagSeguro Internet IP / `08561701` | N4, Instituição de Pagamento | [Página oficial PagBank, rodapé](https://faq.pagbank.com.br/) retornou na busca CNPJ **08.561.701/0001-01**; GET 403. Identificação auxiliar |
| BancoSeguro / `10264663` | B1, Banco Múltiplo | [Página oficial BancoSeguro, rodapé](https://www.bancoseguro.pagbank.com.br/) retornou na busca CNPJ **10.264.663/0001-77**; GET 403. Identificação auxiliar |

As seis pontas de CNPJ14 baseadas somente em resultados oficiais de busca são **pistas documentais**, não corpo autenticado nem vínculo admitido. `identity-search-only.json` separa URL/localizador/CNPJ observado; `identity-provenance.json` registra falhas, sem retry ou contorno. As duas pontas Nu possuem documento corrente original; isso fortalece a identidade da PJ por base8, sem criar uma afirmação sobre estabelecimento14 vigente em cada trimestre. Ausência de CNPJ14 histórico não autoriza inventá-lo nem exige descartar um vínculo de PJ já positivamente corroborado por outro caminho oficial.

Vínculos nativos em 202412: Nu Pagamentos/Nu Financeira/Nu Invest compartilham o prudencial `C0084693`, com líder `18236120`; XP CCTVM/Banco XP declaram `C0082475`, líder `33264668`; PagSeguro IP/BancoSeguro declaram `C0084813`, líder `08561701`; Stone IP declara `C0084686`, líder `16501555`; Banco Inter declara `C0080996`, líder `00416968`. São vínculos do cadastro BCB, distintos do controle acionário SEC. Esses conglomerados não devem receber automaticamente o perímetro financeiro internacional das holdings emissoras.

## Emissores globais: inventário aberto sem filtro por origem

O quadro combina **emissores efetivamente encontrados em C** e **pontas nominais brasileiras observadas em D**. Ele é uma fila de investigação, não prova de que a primeira coluna controla a terceira. Datas são as de registro declaradas na página C corrente; não são vigências completas nem primeira negociação B3. Instituições cadastradas, inclusive inativas, não equivalem a unidades operantes naquele trimestre.

| Emissor em C | Programa / data declarada | Ponta nominal BCB para investigar | Estado do controle nesta fatia |
|---|---|---|---|
| Citigroup Inc. | BDR/2010/00016, 9/11/2010 | Banco Citibank `33479023` | Não provado; Citibank N.A. na coluna custodiante não comprova controle da PJ brasileira |
| HSBC Holdings plc | BDR/2020/00082, 23/9/2020 | Banco HSBC `53518684`; HSBC Bank Brasil `01701201` aparece em 2010–2016 | Não provado; não confundir banco vendido/renomeado e entidade posterior |
| Goldman Sachs Group Inc. | BDR/2010/00002, 20/8/2010 | Banco `04332281`, corretora `09605581` | Não provado. B pp. 48/89 observa GSGI34 DRN em 2024 |
| Morgan Stanley | BDR/2012/00015, 10/1/2012 | Banco `02801938`, corretora `04323351` | Não provado. B pp. 48/89 observa MSBR34 DRN em 2024 |
| Bank of America Corporation | BDR/2010/00003, 20/8/2010 | Banco Múltiplo Merrill Lynch `62073200` | Não provado; nome e base8 são descoberta, não cadeia de controle |
| Banco Santander SA, Espanha | BDR/2019/00097, 27/8/2019 | Banco Santander (Brasil) `90400888` | Não provado nesta extensão. F também contém emissor estrangeiro CNPJ05.707.616/0001-10/CD80160, cancelado em 14/11/2018; separar do emissor brasileiro e do programa posterior |
| JPMorgan Chase & Co | BDR/2012/00008, 4/1/2012 | Banco `33172537`, corretora `32588139` | Não provado; não promover ETFs JPMorgan encontrados na página a ações do emissor |
| UBS Group AG | BDR/2016/00022, 24/5/2016 | Banco de investimento `18520834`; mudança nominal UBS/UBS BB observada no cadastro | Não provado; aquisição/reorganização exige datas e fontes próprias |
| Credit Suisse Group AG | BDR/2020/00071, 23/9/2020 | Banco `32062580`, banco de investimento `33987793` | Não provado; não herdar automaticamente relação UBS após reorganizações |
| Deutsche Bank AG | BDR/2019/00026, 9/4/2019 | Banco `62331228` | Não provado |
| Barclays plc | BDR/2020/00061, 23/9/2020 | Banco `61146577`, nome observado até 201612 | Não provado; fonte não confirma sobreposição temporal da operação brasileira com o BDR |
| Wells Fargo & Company | BDR/2010/00019, 9/11/2010 | Não resolvida nesta busca limitada | Desconhecido, não exclusão |

B também mostra H1SB34/HSBC HOLDING DRN nas pp. 48/89. Esse inventário não é exaustivo do universo estrangeiro: outras fontes/períodos podem revelar emissores e subs controladas. Controle global deve ser provado por registro de subsidiárias/atos oficiais datados antes de transformar cada candidato em relação. A origem, país, ausência do cadastro estrangeiro corrente ou a falta de uma ponta nominal nesta busca não são critérios silenciosos de exclusão.

## Próximo checkpoint: claims separados e lacunas

O desenho técnico pode representar separadamente: identidade do emissor; identidade/lastro do instrumento; registro do programa; observação B3 datada; identidade da PJ BCB; participação/controle declarado em data; vínculo cadastral com conglomerado e perspectiva. Cada claim deve carregar fonte, hash, localizador, data do fato, recuperação e limite de certeza. Um evento de reorganização não é uma tabela de 60 relações; percentuais anuais não preenchem trimestres intermediários, e uma composição de índice não prova negócio em cada dia.

Antes de admissão: revisão independente deste pacote; completar originais das pontas CNPJ auxiliares quando pertinentes; confirmar a cadeia nominal→PJ nas datas selecionadas; resolver mudanças de denominação e os programas de níveis distintos; preservar `unknown` nos intervalos não cobertos. Para emissores globais, selecionar fontes societárias datadas por vínculo, sem exigir origem brasileira. Método, perímetro de comparação entre holdings e operadoras, elegibilidade e indicadores continuam decisões de João/orientador na Issue 3.

Não se requer nova coleta financeira para aproveitar os fatos societários. O benefício imediato é impedir joins por ticker corrente, nome de grupo ou CNPJ da depositária, e fornecer pontos positivos de controle em datas identificáveis. Ações/units históricas do Banco Inter devem coexistir com os BDRs do novo emissor na trilha de instrumentos, sem confundir as duas identidades jurídicas.

## Proveniência do pacote privado

Novos GETs documentais: 16 tentativas sequenciais, timeout 30s, máximo 20MiB por corpo, sem retry automático; dez HTTP200 e seis HTTP403. Nenhuma tentativa COTAHIST. Originais SEC preservados integralmente como documentos incidentais; projeção societária finita em `corporate-extracts.json` e `pags-ownership-projection-only.json`; nenhum saldo financeiro admitido. Cache de extração textual/PDF auxilia auditoria, não novo dataset financeiro.

| ID / arquivo privado | Recuperação UTC, 2026-10-13 | Bytes | SHA-256 do original |
|---|---|---|---|
| N / nu2024.html | 01:30:48.864252Z | 7.403.420 | `07f7c84c5067851fb5cf524e534a19e9d146d70482027fcc6a5c592a2b58066e` |
| I / inter2024.html | 01:30:49.951539Z | 7.334.163 | `e69971cca78b1c227706fd3e6118026d342ff62a75d39d367d7f2e0f0b08cd7a` |
| X / xp2024.html | 01:30:51.238233Z | 7.205.200 | `3c329e5764a8f30796f3e3bead298db0a1fff94d00fc09eeb9ef8786a363aefb` |
| S / stone2024.html | 01:30:52.501775Z | 6.462.428 | `190b4981a21f29b2a5179c1fc5d5a5c0bfcab84f4805bc14ecc795d70f083859` |
| P / pags2024.html | 01:30:53.650859Z | 1.965.480 | `37ae16455580e22d3294ead02affb8fe2b7a6d75140931aafa8fad25b3af91eb` |
| B21 / b3pags2021.html | 01:30:54.430458Z | 61.785 | `0fdcd50af29473d31954b7d2f9be49ea5ee745547abe0ce6f350d5f35020a007` |
| B23 / b3consult2023.pdf | 01:30:54.584040Z | 156.093 | `5eb12b2e0c9fb084675109bf16fcce0f4523389024a379e2f7eff2e3e06ea0cd` |
| B / b3bdi20241210.pdf | 01:30:54.745004Z | 2.170.989 | `1859af080076fae8c1be34002c2063f13bf566807c5bdd694a7a88d1debdcf97` |
| Identidade Nu / nu-cnpj.html | 01:36:21.718489Z | 399.549 | `8c286858703a40d698ff53072d7a2218e03bbf80ad0a7059db7dba00f993b885` |
| S21 / stone-b3-2021.pdf | 01:36:22.458552Z | 94.244 | `d45e81f8979dbd27f9eaee2db642a6833f352fccb252fa4345136f9cc67aa273` |

`new-provenance.json` e `identity-provenance.json` guardam as URLs exatas, UTC, status, tamanhos/hashes e os headers disponíveis, sem cookies; as seis falhas da segunda captura guardam corpo/status/hash, mas não headers completos. Esse limite do diagnóstico permanece explícito. Identidade Nu corrente e edital Stone2021 têm pins completos no segundo índice. Localizadores SEC adicionais usam offsets em texto derivado e seções/tabelas; PDFs mantêm índices de página de base1. `inventory.json` fecha o inventário para revisão.

C foi reutilizada, sem GET, de `.scratch/cvm-b3-history-20261012/a/`: corpo de programas aprovados SHA-256 `dff97b128bd757e3fc2ed319379262544509b085f078e2469ec63ac3ea0feb8e`, recuperação 2026-10-13T01:18:31.029018Z no índice original. O timestamp do nome de arquivo corresponde ao início da captura e não substitui esse campo. `reused-provenance.json` conserva índices originais e `cvm-program-selected-rows.json` mantém as sete células nativas selecionadas, com custodiante e depositário separados.

F foi reutilizado de `data/raw/cvm-b3-history-20261012/foreign-cad/` no checkout principal autorizado: manifest SHA-256 `a1288dff9ee5b8ba23506c8b5d31053877744d5f52cd832a26a046cc1cd02d35`, corpo `9fe853e64092c7fe443e2fad60a926ea73e33fb8482e35e9db2fe661242c5335`, 15.422 bytes. Projeção restrita a identidade/registro da pessoa jurídica; contatos e responsáveis não entram na nota nem na projeção final.

D: manifest do pacote aceito SHA-256 `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1`; fonte JSON202412 `9b5ee21a572fbdbc8de6e5071fb7986b024292691edc42530b9a6ee36560436e`. Os 60 pins originais permanecem no checkpoint privado B, reutilizado somente para leitura. `bcb-exact-202412.json` conserva campos nativos das pontas inspecionadas; arquivo de descoberta nominal não equivale a relação aceita.

Validação documental: autenticação dos corpos reutilizados, leitura cruzada das datas/colunas de participações, preservação dos códigos e inventário da allowlist. Sem testes de software, commit, alteração de tracker ou decisão de amostra nesta fatia. Resultado local; revisão independente e uso em admissão ainda pendentes.

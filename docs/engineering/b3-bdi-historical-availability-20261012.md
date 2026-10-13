# BDI B3: disponibilidade histórica e uso documental, 2010–2024

Pesquisa A2 da [Issue 108, contrato de extensão](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6136154672), no worktree da branch `codex/cvm-b3-history-2010-2024`, base `f93d37f17898d69713d06f07bb393eb1f2444331`. Complementa a pesquisa A congelada, sem alterá-la. Ações, UNITs e BDRs conservam a mesma prioridade. Esta nota avalia fontes e viabilidade técnica; não escolhe amostra nem converte presença em índice em negociação comprovada.

## Resultado e recomendação

O BDI é uma fonte oficial útil para evidências datadas de instrumentos e eventos. **A disponibilidade de 60 observações trimestrais de 2010–2024 não foi demonstrada neste checkpoint.** Há um capítulo de 2024 autenticado localmente e um boletim completo de 2020 legível no leitor web, mas as três tentativas de transporte dos PDFs legados retornaram 403. O catálogo histórico indicado pela B3 falhou na resolução de DNS neste ambiente. Esses resultados não demonstram inexistência dos documentos e não autorizam contornar o bloqueio.

Recomenda-se uma rota documental com estados separados: instrumento em carteira de índice vigente, instrumento em prévia de carteira, registro de cotação/negociação, informação de evento e listagem declarada pelo emissor. Reutilizar FCA/CVM como declaração autônoma. Um documento trimestral pode corroborar uma observação em uma data; não demonstra todas as negociações ou instrumentos que existiram durante o trimestre. Também não substitui a união histórica de candidaturas: uma seleção de 60 dias pode perder instrumentos com existência ou negociação entre os pontos escolhidos.

A próxima aquisição deve ser finita e precedida da conferência do catálogo, do capítulo e da data efetiva. Não executar 60 downloads pelo simples sucesso de uma URL de 2024. Preservar candidatos não resolvidos de todas as três naturezas, inclusive BDRs fora de índices ou sem registro CVM do emissor. Ausência na carteira não é ausência na B3.

## Distribuição oficial e mudanças de formato

A [notícia B3 de 29/03/2022](https://www.b3.com.br/pt_br/noticias/boletim-diario-do-mercado.htm), título “Melhorias no BD e BDI”, anuncia consulta navegável a partir de 04/04/2022 e downloads de informativo completo, capítulos e tabelas em PDF e/ou CSV. Isso documenta a distribuição por componentes e uma mudança de formato; não garante que a mesma estrutura de arquivo exista desde 2010.

O [portal BDI](https://arquivos.b3.com.br/bdi/) informa que boletins publicados há mais de 20 dias estão no Acervo B3 em PDF. A leitura web indexada mostra boletim completo e subcapítulos, com estados de publicação, errata e atualização. O GET textual do leitor web ao portal mostrou somente a exigência de JavaScript; portanto a renderização indexada não foi tratada como um catálogo físico autenticado. Sem consultar APIs ocultas.

O [boletim oficial de FIIs de julho de 2024](https://www.b3.com.br/data/files/7B/24/5B/04/39E21910812F0F09AC094EA8/Boletim%20FII%20-%2007M24.pdf), página 1, aponta o Acervo MUB3 para o histórico superior a 20 dias e distingue lista de instrumentos, carteiras teóricas e fechamento de índices. O domínio [Acervo B3](https://acervob3.com.br/) também é referenciado pela B3 na [Tabela de Preços 2024](https://b3.com.br/data/files/E8/33/8D/B8/0A6FD810066AFDD8AC094EA8/Tabela%20de%20Pre%C3%A7os%202024.pdf), item 7.4. Essa referência confirma o destino institucional, mas não a disponibilidade de todos os BDIs de 2010–2024. Não foi possível enumerar anos, datas e objetos do catálogo neste checkpoint.

Essas páginas e PDFs foram consultados pelo leitor web para descoberta e localizadores; não se apresentam como corpos capturados pelo transporte privado desta fatia. As quatro tentativas adicionais de aquisição estão inventariadas abaixo.

### Extensão textual: localizar o capítulo correto

Na extensão autorizada após as quatro sondagens, somente busca/leitura web, sem transporte privado adicional: o portal oficial lista “Summary of equities”, “Indicators and information” e outros subcapítulos. A [página oficial Quotes](https://www.b3.com.br/main.jsp?doui_processActionId=setLocaleProcessAction&locale=en_US&lumA=1&lumII=8AE690F76F80368E016F8AC2AE912405&lumPageId=8AE690F76F80368E016F8AC2AE7023F7) aponta a navegação Equities → Summary of equities → Tick by tick desde 15/12/2025. Essa migração posterior não prova o capítulo ou disponibilidade de 2024. Uma [consulta de resumo com data 24/12/2024](https://arquivos.b3.com.br/bdi/tabelas/24-12-2024?classification=7b1adb82-a8be-4d9d-8fcf-335da462fc25&lang=en-US&table=DailyAverageStocks), descoberta em busca e lida como página pública, retornou “Figures not found for this period”; isso não é prova de ausência de negociações ou PDF histórico. Não foram reproduzidas chamadas internas da aplicação.

Um caso de controle reforça a necessidade de conferir o conteúdo: [BDI_04-2_20260908.pdf](https://arquivos.b3.com.br/bdi/download/bdi/2026-09-08/BDI_04-2_20260908.pdf), URL encontrada em referência de descoberta e verificada diretamente no leitor web oficial, contém 98 páginas e abre com “Empréstimos registrados”, com Código IF, ISIN, mercado e número de contratos. Trata-se de empréstimos de ativos, não de cotações à vista; as taxas podem repetir o último valor disponível quando não há negociação no ativo. É um exemplo de 2026, fora da janela, usado somente para evitar escolher o capítulo errado. Não foi capturado nem autenticado localmente. Não se confirmou um índice oficial que associe todos os números de arquivos às tabelas e datas de 2010–2024; nenhum número, como `01` ou `04-2`, foi promovido a endpoint histórico de cotações por tentativa.

## Documentos e sondagens: origem e resultado

| Ano/objeto | URL e origem | Resultado local | Alcance comprovado |
| --- | --- | --- | --- |
| Catálogo | [Acervo B3](https://acervob3.com.br/), domínio referenciado pela B3 | Falha DNS `getaddrinfo`, sem resposta HTTP ou corpo | Destino institucional descoberto; inventário histórico não obtido |
| 2010 | [bdi_00_20101230.pdf](https://bvmf.bmfbovespa.com.br/download/BOLETINSDIARIOS/bdi_00_20101230.pdf), **SONDAGEM** derivada do padrão oficial de 2020 | HTTP 403, 17 bytes | Não confirma existência, data de pregão, conteúdo ou tamanho do PDF |
| 2015 | [bdi_00_20151230.pdf](https://bvmf.bmfbovespa.com.br/download/BOLETINSDIARIOS/bdi_00_20151230.pdf), **SONDAGEM** derivada do padrão oficial de 2020 | HTTP 403, 17 bytes | Não confirma existência, data de pregão, conteúdo ou tamanho do PDF |
| 2020 | [bdi_00_20200904.pdf](https://bvmf.bmfbovespa.com.br/download/BOLETINSDIARIOS/bdi_00_20200904.pdf), URL oficial descoberta em busca | HTTP 403, 17 bytes; leitor web apresentou PDF com 162 páginas | Conteúdo documental legível no leitor web; PDF não autenticado localmente nesta fatia |
| 2024 | [BDI_02_20241210_en-Us.pdf](https://arquivos.b3.com.br/bdi/download/bdi/2024-12-10/BDI_02_20241210_en-Us.pdf), captura existente da pesquisa BDR | Reutilizado: HTTP 200, 2.170.989 bytes, 116 páginas | Capítulo “Indicators and Information”, referente a 10/12/2024, nº 239 |

Os pontos 2010/2015 foram escolhidos apenas para sondagem técnica do padrão antigo, sem afirmar que a data escolhida foi pregão ou que o catálogo publicou o recurso. As quatro tentativas foram sequenciais, sem retry, com timeout de 30 s e limite de 16 MiB por resposta. O PDF de 2024 foi reutilizado, sem novo GET. Não houve tentativa de COTAHIST nesta fatia, mudança de credenciais ou rota para contornar 403.

## Localizadores e distinção entre cotações e índices

No [BDI de 04/09/2020](https://bvmf.bmfbovespa.com.br/download/BOLETINSDIARIOS/bdi_00_20200904.pdf), a página física 1 identifica o dia e o segmento Bovespa e remete às cotações à vista, a termo e de opções. A página física 47 mostra operações a termo com `BBDC3T`, `BBDC4T` e `BBAS3T`; o sufixo e o mercado não devem ser apagados. A página física 58 inclui `SANB11F` com espécie `UNT` e `BCSA34F` com espécie `DRN`. Esses exemplos não são um censo nem uma chave jurídica. O leitor web fornece páginas e texto; hashes dos bytes do PDF e conferência visual/tabular local ainda faltam. A URL antiga não prova que o formato novo possa ser retroaplicado a 2010.

O PDF de 2024 foi autenticado contra o manifesto da pesquisa BDR. Seu hash SHA-256 é `1859af080076fae8c1be34002c2063f13bf566807c5bdd694a7a88d1debdcf97`. O mapa privado cobre a abertura das 116 páginas e os termos selecionados. Localizadores em páginas físicas, contadas a partir de 1:

| Página | Evidência localizada | Interpretação permitida |
| --- | --- | --- |
| 1 | “Indicators and Information”, data 10/12/2024, nº 239; participação de investidores com outra data de acumulação | Data do boletim não é a data efetiva de toda tabela |
| 18 | “Composition of Indices' Portfolios”, setembro a dezembro de 2024; nota sobre participação no início do pregão de 02/12/2024; `BBAS3`, `BBDC3`, `BBDC4`, `ITUB4` | Composição e referência da carteira indicada, não quantidade de negócios no dia |
| 19 | `SANB11`, espécie `UNT`, quantidade teórica e participação | Evidência documental de UNIT em carteira; não confundir quantidade teórica com volume negociado |
| 48–49 | `H1SB34` e `ROXO34`, espécie `DRN` | Evidência de BDRs na carteira identificada no contexto da tabela |
| 61–62 | `INBR32` (`DR2`), `ROXO34` (`DRN`), `XPBR31` (`DR1`) | Preservar tipo nativo e emissor abreviado; não derivar depositária ou controle BCB |
| 63 | “Preview of Indices' Theoretical Portfolios” e calendário de divulgação de três prévias | Prévia separada de carteira vigente; não converter toda linha posterior em instrumento vigente na data do boletim |
| 109 | Informação de leilão envolvendo `XPBR31` | Evento específico, não automaticamente registro de negócio executado |

O documento contém carteiras, prévias e comunicados. Uma busca por ticker pode retornar contextos diferentes no mesmo PDF. Não foi localizado campo de contagem de negócios nesses exemplos do capítulo 02. O número `02` não deve ser usado como contrato universal de cotações; o índice e o título do capítulo precisam determinar sua responsabilidade em cada geração do BDI.

## Desenho mínimo para eventual observação trimestral

Manter `reference_quarter`, data solicitada, data do boletim, data efetiva da tabela, data de publicação/atualização, idioma, geração do formato, capítulo, título da tabela, página/linha, ticker, nome e espécie literais, tipo de evidência e hash da fonte. Preservar quantidade teórica e participação somente se necessárias para conferir a carteira; não admiti-las como valores financeiros bancários ou como volume de negócios. Identificadores e relações BCB/CVM continuam com evidências próprias.

Uma regra técnica posterior pode buscar uma observação datada em cada trimestre, mantendo a distância até a referência e todas as ausências. Escolher o último pregão da referência exige calendário e comprovação do documento; não basta preencher uma URL com o último dia civil. A data de 10/12/2024 aqui é exemplo disponível, não substituição aprovada para dezembro nem encerramento trimestral. Se o objetivo for “houve negociação em qualquer dia do trimestre”, um único boletim não é suficiente; requer cobertura diária ou fonte que resuma expressamente esse intervalo. Se o objetivo for “aparece neste documento datado”, o alcance é mais estreito e deve constar do nome do estado.

Invariantes de aquisição/admissão:

1. URL descoberta e URL de sondagem têm estados distintos; sucesso HTTP não basta sem corpo íntegro e tipo esperado. Falha DNS/HTTP/schema preserva diagnóstico e nunca vira população zero.
2. Fixar SHA-256 externo de corpo e manifesto; conferir tamanho, fechamento e PDF legível. Manter errata e reapublicação como versões, sem sobrescrever fonte anterior.
3. Conferir título, data, idioma, capítulo e tabela. Datas efetivas diferentes da capa permanecem separadas; prévias e carteiras vigentes não são fundidas.
4. Guardar contexto e localizador por registro; extração de PDF que junte colunas, páginas ou cabeçalhos gera quarentena, sem reparo silencioso. O texto extraído de 2024 contém substituições de caracteres em alguns trechos; confrontar o PDF antes de promover grafia jurídica ou identificador.
5. Não tratar sufixo 11 como UNIT, sufixo 34 como vínculo de controle ou nome abreviado como CNPJ. ON/PN/UNT/DRN/DR1/DR2 permanecem literais até classificação sustentada por fonte.
6. Ausência em índice, capítulo ou dia não é negativa universal de listagem/negociação. Preservar a fila de ações, UNITs e BDRs sem corroboração direta.

## Custo, inventário e limites

As quatro tentativas adicionais produziram três corpos de erro de 17 bytes, totalizando **51 bytes**, e uma falha DNS sem corpo. O custo real de 60 boletins completos, sua expansão textual, esforço de extração e cobertura ainda não foram medidos. O único tamanho útil disponível é 2.170.989 bytes para o capítulo de 116 páginas de 2024; extrapolar esse valor para PDFs completos antigos ou para 60 referências produziria uma estimativa sem base. Preço/licenciamento de eventual serviço alternativo não apurado. Não foi contratado serviço nem instalado runtime/dependência.

Preparação privada em `.scratch/cvm-b3-history-20261012/bdi/`: `capture-index.json` registra URLs, classificação de descoberta, UTC, status/erro, headers sem cookies, tamanho, SHA-256 e tempo; `bdi2010.bin`, `bdi2015.bin` e `bdi2020.bin` preservam as falhas HTTP. Os três corpos têm SHA-256 `2938e9f1284180959e33ab1718d0793a72ff6e4cdb8108c34dcd14e69446de5c`. `reused-2024-profile.json` registra proveniência reaproveitada, mapa completo de páginas e localizadores. `capture.py` e `profile.py` são auxiliares privados, não software público.

O PDF reutilizado permanece em `.scratch/cvm-b3-history-20261012/bdr/b3bdi20241210.pdf`, com manifesto em `new-provenance.json` e texto por página em `b3bdi20241210-pages.json`; nenhum desses arquivos foi alterado. A pesquisa A e seus índices também permaneceram congelados. Feynman deep-research/pdf-explore aplicadas pela rota alternativa autorizada: `/deepresearch` indisponível, fontes oficiais e ferramentas locais existentes. A conferência desta nota é do autor; revisão independente ainda é necessária.

Checkpoint proposto: registrar as falhas e a disponibilidade parcial, revisar este recorte e obter enumeração oficial de datas/capítulos do Acervo antes de autorizar lote. O BDI pode fornecer corroboração documental pontual; neste estado não fecha a cobertura histórica universal ou os 60 pontos. Nenhum vínculo novo foi admitido, nenhuma equivalência entre índice e negociação foi adotada e nenhum artefato aceito foi modificado.

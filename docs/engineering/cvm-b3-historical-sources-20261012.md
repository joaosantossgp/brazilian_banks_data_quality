# Fontes históricas CVM–B3: ações, UNITs e BDRs, 2010–2024

Pesquisa A da [Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108), base `f93d37f17898d69713d06f07bb393eb1f2444331`, branch `codex/cvm-b3-history-2010-2024`. Ações, UNITs e BDRs têm **a mesma prioridade**, conforme decisão de João durante a pesquisa. Esta nota fundamenta desenho e aquisição finita; não seleciona amostra acadêmica, não prova vínculos universais e não altera metadados aceitos.

## Recomendação executável

Construir três trilhas independentes: **observação de negociação por instrumento/dia**, **listagem/negociação declaradas pelo emissor com datas explícitas** e **identidade/controle do emissor em relação à instituição ou conglomerado BCB**. A primeira usa 15 arquivos anuais COTAHIST; a segunda reutiliza 15 arquivos anuais FCA autenticados e documentos B3 de admissão/cancelamento; a terceira reutiliza as entregas das Issues 102/105 e acrescenta programa BDR/emissor estrangeiro/controle quando aplicável. Não condensar as três em um booleano de capital aberto.

O universo candidato deve ser a união de instrumentos/declarações de todos os anos, incluindo canceladas e descontinuadas, com ramos para BDRs dispensados de registro do emissor. Não iniciar pelo catálogo de empresas atualmente listadas, Ibovespa ou lista atual de BDRs. Priorizar conferência de bancos/financeiras sem eliminar instrumentos ainda sem vínculo BCB: manter fila identificável de não resolvidos e motivo. Emissores estrangeiros controladores de subsidiárias BCB entram nessa fila com igual prioridade; depositária brasileira não representa automaticamente o grupo econômico do lastro.

A rota é factível em processamento incremental, mas **os 15 ZIPs anuais não foram obtidos**: 15 requisições HEAD e 2 requisições GET Range das extremidades retornaram 403. Tamanhos reais anuais, expansão dos ZIPs, cobertura diária e tipologias presentes ainda não foram medidos. O contrato de aquisição precisa tratar esse resultado concreto; não fazer retries/rotas alternativas que contornem bloqueio. CVM/FCA e documentação já permitem avançar o desenho e o inventário de candidaturas enquanto o acesso oficial B3 é resolvido.

## Fontes, alcance e diferença entre prova e inferência

| Fonte oficial | Cobertura/objeto | Prova útil | Limite |
| --- | --- | --- | --- |
| [Cotações históricas B3](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-a-vista/cotacoes-historicas/) | Histórico anunciado desde 1986; ZIP/TXT por período | Produto/documentação pública e instruções de download | Preços da época sem ajuste; a página não é garantia de negociação de todo ativo listado em todo dia |
| [Formulário oficial de séries](https://bvmf.bmfbovespa.com.br/pt-br/cotacoes-historicas/FormSeriesHistoricasArq.asp) | Elemento select `cboAno` contém 1986–2026, incluindo cada ano de 2010–2024 | Nomes literais dos 15 recursos | Opção no formulário não prova disponibilidade HTTP ou integridade |
| [Layout COTAHIST](https://www.b3.com.br/data/files/33/67/B9/50/D84057102C784E47AC094EA8/SeriesHistoricas_Layout.pdf) | Registros de 245 bytes: 00 (cabeçalho), 01 (instrumento, mercado e dia), 99 (rodapé) | Campos e tabelas; ISIN e ticker observados por data | Sem CNPJ ou código CVM; sem eventos completos de admissão/cancelamento; dicionário de 2020 precisa ser confrontado com dados de 2010–2024 |
| [FCA CVM](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca) | 15 recursos de 2010–2024 já autenticados na Issue 102 | CNPJ do emissor, instrumento, classe, mercados, datas declaradas e versões | Declaração do emissor; campos vazios; sem ISIN; não cobre necessariamente emissor de BDR dispensado de registro |
| [Listadas B3](https://sistemaswebb3-listados.b3.com.br/listedCompaniesPage/?language=pt-br) e [canceladas](https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/acoes/consultas/empresas-com-listagem-cancelada/) | Consulta corrente; a página de canceladas anuncia atualização semanal | Complemento de identificação/eventos encontrados | Não demonstrado arquivo histórico completo; não usar ausência atual como exclusão em 2010–2024 |
| [Programas BDR da CVM](https://sistemas.cvm.gov.br/asp/cvmwww/registro/ProgramadeDR.asp), [aprovados](https://sistemas.cvm.gov.br/asp/cvmwww/progdr/progdraprov_Link.asp) | Tabela posição de 12/10/2026 com registro/data e detalhes | Programa, emissor, lastro, depositária, custodiante, nível e tipo | Tabela corrente não garante programas cancelados/convertidos; aprovação não é data do primeiro negócio |
| [CVM estrangeiras](https://dados.cvm.gov.br/dataset/cia_estrang-cad) | Cadastro do último dia útil | CNPJ/CD_CVM/país/datas cadastrais quando presentes | Não histórico completo; BDR de nível I pode dispensar registro do emissor |
| [UP2DATA dados disponíveis](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/up2data/dados-disponiveis/) | Instrumentos, empresas e eventos; canais regulatórios, legados e comerciais distintos | Documentação e esquemas exatos abaixo | Não foi demonstrado pacote aberto integral de 2010–2024 com CNPJ de todos os emissores |

## COTAHIST: contrato proposto para negociação observada

O [PDF](https://www.b3.com.br/data/files/33/67/B9/50/D84057102C784E47AC094EA8/SeriesHistoricas_Layout.pdf) recuperado tem 10 páginas físicas. A capa conserva 13/04/2017, revisão 01; a p. 2 registra 05/10/2020, versão 2, e as pp. 3–10 indicam revisão 02. Fixar hash dos bytes, não presumir versão pela capa ou resultado de busca. Localizadores: p. 3, conceitos e cabeçalho; p. 4, campos iniciais; p. 5, negócios; p. 6, ISIN, distribuição e rodapé; p. 7, BDI; pp. 8–10, espécies; p. 10, mercados.

Extrair somente metadados e contagem técnica de negócios necessária para distinguir presença de cotação e negócio efetivo. Campos nativos relevantes, posições contadas a partir de 1 (1-based) inclusivas:

| Campo | Posições | Uso |
| --- | --- | --- |
| TIPREG | 1–2 | 00/01/99, controle da estrutura |
| Data pregão | 3–10 | Data observada no formato AAAAMMDD, distinta da geração |
| CODBDI | 11–12 | Classificação nativa, conservar |
| CODNEG | 13–24 | Ticker literal, não canonizar por sufixo |
| TPMERC | 25–27 | 010 (vista), 020 (fracionário), 017 (leilão); os demais mercados têm códigos próprios |
| NOMRES | 28–39 | Nome abreviado, não usar como chave jurídica |
| ESPECI | 40–49 | Espécie + direitos/segmento, conservar o valor literal |
| TOTNEG | 148–152 | Número de negócios; se zero, não afirmar negócio efetivo |
| CODISI | 231–242 | ISIN/código interno conforme layout |
| DISMES | 243–245 | Distribuição/estado de direitos, não descartar |

Não usar ticker sozinho como identidade longitudinal. Chave de observação proposta inclui data, ticker, mercado, ISIN e distribuição; inventariar duplicatas antes de fixar unicidade. Um ISIN pode ocorrer em lote padrão e fracionário com tickers distintos; ambos não representam duas participações acionárias independentes. Não derivar CNPJ pelo prefixo do ISIN. `first_seen`/`last_seen` no arquivo são limites observados, não IPO/deslistagem. Ausência em um dia/trimestre não prova ausência de listagem; suspensão, iliquidez e mudança de ticker continuam possíveis. Registrar separadamente presença de registro e `TOTNEG>0`.

Não filtrar exclusivamente CODBDI 02: o dicionário inclui condições de recuperação/intervenção e outros eventos. Não aceitar toda linha de mercado 010 como ação: há direitos, recibos, fundos, BDRs e certificados. A classe deve vir de combinação validada de campos/fontes; espécies novas/desconhecidas ficam em inventário de conflito, não exclusão silenciosa. O layout não contém lista explícita de UNIT/UNT localizada nesta versão; isso torna a sondagem anual real necessária.

[Demonstração oficial](https://www.b3.com.br/data/files/9C/F3/01/C4/297BE410F816C9E492D828A8/SeriesHistoricas_DemoCotacoesHistoricas12022003.zip), link na página Cotações: ZIP de 27.334 bytes, um TXT de 136.591 bytes, 553 registros, todos com 245 bytes; CRC e rodapé com contagem 553 conferidos. Refere-se a 12/02/2003, fora da janela: valida mecanismo/layout, não cobertura de 2010. Contém `BBDC3`/`BBDC3F` com o mesmo ISIN e mercados 010/020; ESPECI inclui `ON *EJ N1` e direitos. Isso demonstra por que remover apenas `F` ou comparar espécie exata `ON` perde semântica. O tutorial B3 indica Windows ANSI; contratação do parser deve testar bytes reais e definir encoding explícito, sem fallback silencioso. Cortes posicionais devem operar em bytes antes de decodificar.

Checks mínimos antes de admissão: hash externo do manifest; status 200 e corpo completo; CRC do ZIP, membro esperado, nomes seguros e limites medidos por arquivo e no agregado; cabeçalho e rodapé com 245 bytes e contagem incluindo ambos; datas válidas e pertencentes ao ano; campos nativos como strings; relatório de campos, espécies, duplicatas e ISINs vazios; preservação de bytes e linhas; sem converter falha para universo vazio. Preços/volumes não serão usados como financeiro de bancos nesta entrega.

## Recursos anuais e custo medido

A cadeia de descoberta é página B3 Séries → iframe FormSeriesHistoricasArq.asp → `cboAno`; o próprio [JS referenciado pelo formulário](https://bvmf.bmfbovespa.com.br/js/SeriesHistoricas.js), função de download, concatena `/InstDados/SerHist/` e nome da opção. URLs abaixo portanto têm proveniência oficial. Sondagens HEAD sequenciais, com timeout de 30 s, em 13/10/2026 UTC, sem retry. Em 2010/2024, GET Range `bytes=0-1023` também retornou 403 com 17 bytes de erro, sem Content-Range; não houve corpo ZIP parcial ou total. Nenhum redirecionamento/bloqueio foi contornado.

| Ano | URL estática oficial | HEAD | Tamanho do ZIP |
| --- | --- | ---: | --- |
| 2010 | [COTAHIST_A2010.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2010.ZIP) | 403 | não informado |
| 2011 | [COTAHIST_A2011.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2011.ZIP) | 403 | não informado |
| 2012 | [COTAHIST_A2012.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2012.ZIP) | 403 | não informado |
| 2013 | [COTAHIST_A2013.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2013.ZIP) | 403 | não informado |
| 2014 | [COTAHIST_A2014.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2014.ZIP) | 403 | não informado |
| 2015 | [COTAHIST_A2015.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2015.ZIP) | 403 | não informado |
| 2016 | [COTAHIST_A2016.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2016.ZIP) | 403 | não informado |
| 2017 | [COTAHIST_A2017.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2017.ZIP) | 403 | não informado |
| 2018 | [COTAHIST_A2018.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2018.ZIP) | 403 | não informado |
| 2019 | [COTAHIST_A2019.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2019.ZIP) | 403 | não informado |
| 2020 | [COTAHIST_A2020.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2020.ZIP) | 403 | não informado |
| 2021 | [COTAHIST_A2021.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2021.ZIP) | 403 | não informado |
| 2022 | [COTAHIST_A2022.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2022.ZIP) | 403 | não informado |
| 2023 | [COTAHIST_A2023.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2023.ZIP) | 403 | não informado |
| 2024 | [COTAHIST_A2024.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2024.ZIP) | 403 | não informado |

Tamanho/custo integral: **não medido**, sem estimativa inventada de RAM, tempo ou disco. Contrato subsequente deve sondar disponibilidade por canal oficial suportado, medir tamanho e expansão por ano, processar um arquivo por vez e materializar somente metadados. Os 15 arquivos são inventário finito, não 15 pipelines. Custo financeiro/licenciamento de alternativas UP2DATA não apurado; não pressupor contratação nem redistribuição pública dos ZIPs.

## FCA: forte declaração temporal, limite material de ticker

Reutilizado `data/curated/cvm-identity-20261012/valores_mobiliarios_fca.csv`, autenticado contra manifest da Issue 102 nesta pesquisa. Hash do CSV `a7dd017d47ee5f1968660c577d95cf58b2d37c7586e838b84bdcdd09bb1e2af8`. Cabeçalho nativo com 18 campos inclui CNPJ, Data_Referencia, Versao, ID_Documento, Nome, Valor_Mobiliario, classe preferencial, Codigo_Negociacao, Composicao_BDR_Unit, Mercado, administradora, início/fim de negociação, segmento e início/fim de listagem. Dicionário oficial já arquivado na Issue 102: `meta_fca_cia_aberta_valor_mobiliario.txt`, localizadores Campo de cada nome. Datas de eventos declarados podem anteceder a referência do formulário e não devem ser apagadas por escolher somente dezembro.

Perfil offline autenticado: 2010 tem 635 linhas/546 CNPJs e **635 tickers vazios**; 2024 tem 1023 linhas/670 CNPJs e 453 tickers vazios. Em 2024 há 14 linhas `Units` e 2 `BDRs`, além de outras grafias de certificados. São linhas de fonte, não contagens de instrumentos/emissores elegíveis. Em 2010 não há PN explícita no domínio observado; isso não autoriza concluir ausência de preferenciais. Os valores brutos e versões devem ser preservados.

A ligação FCA → COTAHIST somente por ticker é inviável como solução universal. O nome abreviado no COTAHIST somente gera candidato; fechar instrumento/emissor com documento primário que una identificadores por data. Formulários múltiplos/reapresentações podem mudar datas ou classe: preservar versão/data de recebimento e emitir conflitos; não escolher silenciosamente a maior versão como toda verdade histórica. Data de fim vazia significa fim não informado nessa declaração, não vigência eterna. Lista atual da B3 serve para corroborar pontas, não retroagir um ticker de 2026 a 2010.

## Ações, UNITs e BDRs: tratamento de mesma prioridade

[UNIT B3](https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/certificado-de-deposito-de-acoes-units.htm), seções Produto/Características técnicas: reúne classes de valores mobiliários; o sufixo 11 também ocorre em outros ativos. Conservar composição, classe e vigência do certificado. Uma UNIT negociada não prova que cada ação subjacente negociava separadamente. ON, PN, PNA/PNB e certificados devem poder coexistir para o mesmo emissor sem duplicar o grupo BCB.

BDR é certificado brasileiro de lastro no exterior. Separar instrumento BDR/ISIN brasileiro, ação/ISIN do título estrangeiro, programa CVM, emissor do lastro, depositária brasileira, custodiante no exterior e subsidiária BCB. A [Resolução CVM 182](https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/100/resol182.pdf), p. 4, art. 6, III, dispensa registro do emissor no nível I nas condições previstas; pp. 6–7, arts. 12/13 exigem registro nos níveis II/III; pp. 8–9, arts. 17/18 tratam do registro do programa. Não exigir CAD/FCA do emissor como condição universal de candidatura de BDR. Esta norma é de 2023; a [página oficial](https://conteudo.cvm.gov.br/legislacao/resolucoes/resol182.html) identifica a anterior ICVM 332 para investigação histórica, sem aplicar a Resolução 182 retroativamente.

[Programas aprovados pela CVM](https://sistemas.cvm.gov.br/asp/cvmwww/progdr/progdraprov_Link.asp), tabela Brazilian Depositary Receipts, colunas Emissora/Nível/Custodiante/Depositário/Espécie/Registro Número/Data, posição de 12/10/2026. Alguns depositários estão vazios na tabela; o detalhe individual é necessário. Exemplos localizados: Nu BDR/2023/00003 de 28/06/2023; XP BDR/2021/00057 de 28/07/2021; Pagseguro BDR/2021/00002 de 15/01/2021; Citigroup BDR/2010/00016 de 09/11/2010; HSBC BDR/2020/00082 de 23/09/2020. São registros de programa, não prova de controle BCB ou negociação em cada trimestre. A tabela atual de Inter aponta registro de 2026: ilustra risco de promover catálogo corrente a histórico completo. StoneCo não foi positivamente identificada na tabela por busca nominal deste checkpoint; StoneX é entidade distinta.

[Detalhe oficial de Nu](https://sistemas.cvm.gov.br/asp/cvmwww/registro/ofertasreg2/Bdrdet.asp?Nr_Ano=2023&Sg_uf=RJ&Nr_Proc=1088&status=R), rótulos Emissora, Instituição Custodiante, Instituição Depositária, Origem, Registro, Quantidade, Espécie/Classe e Tipo: Nu Holdings, Cayman, BNYM, Bradesco, registro em 28/06/2023, 6 BDR/ação, ordinária classe A, nível I, não patrocinado. Isso fecha papéis do programa, não identidade Nu = Bradesco. Não extrair nomes/CNPJ sem papel tipado.

O [boletim B3 de abril de 2025](https://www.b3.com.br/data/files/A4/32/0D/1B/59BC69106B8BCB69AC094EA8/Boletim%20BDR%2004M25.pdf) fornece candidatos Nu/Inter/XP/Stone/Pagseguro com tickers/depositária/paridade; é descoberta posterior, não prova de 2024. Preservar candidatos estrangeiros como Citi/HSBC e outros que apareçam nas fontes; vínculo às subsidiárias BCB exige documentos de controle/composição contemporâneos. Não usar origem brasileira como filtro de exclusão nem igualar nome comercial a grupo.

[CIA_ESTRANG CAD](https://dados.cvm.gov.br/dataset/cia_estrang-cad), [dicionário](https://dados.cvm.gov.br/dados/CIA_ESTRANG/CAD/META/meta_cad_cia_estrang.txt), contém 49 campos, entre eles CNPJ/CD_CVM, DENOM_SOCIAL, PAIS_ORIGEM, DT_REG/DT_CANCEL, SIT/CATEG_REG e datas associadas. O catálogo afirma último dia útil: serve à identidade corrente/declarada, não ao universo BDR histórico. Proposta de aquisição futura: projetar somente identificadores, datas, país e situação; excluir dados de contato/pessoais. [IPE CVM](https://dados.cvm.gov.br/dataset/cia_aberta-doc-ipe) inclui categoria de BDR não patrocinado/descritivo operacional e links de documentos, mas anuncia os últimos cinco anos; documentos antigos precisam de consulta oficial por programa/data e preservação individual, sem prometer cobertura de 2010 pelo arquivo atual.

## Cadastro mestre de instrumentos (instrument master), eventos e condições de acesso

Documentação UP2DATA autenticada: [mapeamento BVBG028](https://www.b3.com.br/data/files/1A/45/CC/29/4C11881036DB3088AC094EA8/BVBG.028%20para%20UP2DATA.xlsx), planilha XML sheet1, linhas 30 (ISIN opcional), 31 (distribuição) e 35 (ticker); o par ISIN/distribuição identifica versão de ativo. CNPJ aparece em outros grupos, sheet6, linha 45, e sheet14, linha 82, com origem em outro sistema/NoMe: **não foi demonstrado CNPJ universal no cadastro mestre de ações (equities)**. [Dicionário UP2DATA](https://www.b3.com.br/data/files/2B/45/88/01/24C01A10C90F7F0AAC094EA8/Catalogo%20de%20Taxonomia%20-%20Portugues.xlsx) tem SecurityList, AnalyticsBDR, Listed_Companies e outros canais; extratos privados conservam sheet XML/linha. Não confundir campos de debênture/fundo com equities somente porque compartilham o nome ISIN/CNPJ. A disponibilidade temporal de 2010–2024 e o custo comercial desses canais não foram demonstrados.

O [CE 092/2020](https://www.b3.com.br/data/files/0E/B6/BE/6A/B35C3710CC8AD9378C094EA8/CE%20092-2020-VOP%20Melhorias_acesso_AB%2BLC_REVISADO.pdf), p. 1, documenta download padronizado de cadastro/negociação e histórico dos últimos 10 dias, não um arquivo de 15 anos. [CE 065/2022](https://www.b3.com.br/data/files/F5/C6/57/5A/85AD1810C493CD08AC094EA8/CE%20065-2022-VPC%20Divulga%C3%A7%C3%A3o%20novos%20BDRs_rev%20Compliance.pdf), p. 1, muda as novas admissões de BDR desde 15/07/2022 para notícias + dados públicos. [CE 001/2026](https://www.b3.com.br/data/files/24/92/1D/71/773CB9109B5E99B9AC094EA8/CE%20001-2026-VTEC_NOVA%20DATA%20PARA%20DESCONTINUACAO%20DA%20PAGINA%20DE%20DADOS%20PUBLICOS_PT.pdf), pp. 1–2, encerra a página antiga em 31/03/2026 e mapeia o cadastro de instrumentos para BDI/Renda Variável/Resumo de Ações. Portanto a falha da rota antiga é condição investigada, não prova de ausência dos dados. Não foi encontrada distribuição estática aberta integral do cadastro mestre de 2010–2024 neste checkpoint.

Condição literal no [Hub B3](https://www.b3.com.br/pt_br/dados/hub-de-dados-publicos/), parágrafo antes de Renda Fixa: “é expressamente vedada a coleta automatizada, inclusive por meio de ferramentas de inteligência artificial”. O contexto delimita dados disponibilizados nessa página. [Termos](https://www.b3.com.br/pt_br/termos-de-uso-e-protecao-de-dados/termos-de-uso/), Proteção à propriedade intelectual/Difusão de Dados, tratam de utilização pessoal, comercial e redistribuição. Já a página específica Cotações orienta o download de ZIP/TXT/layout/demonstração. Não inferir daqui nem licença aberta para redistribuir ZIPs nem proibição universal de usar qualquer documentação. Registrar condições por canal; não instalar gate humano genérico por interpretação desta nota. Nenhuma API oculta foi usada; o bloqueio 403 não foi contornado.

## Evidência, limites do checkpoint e próxima fatia

Capturas privadas em `.scratch/cvm-b3-history-20261012/a/`: 25 corpos documentais/sondagens, 3.962.758 bytes, 23 respostas HTTP 200 e 2 redirecionamentos 302 preservados; limites técnicos por GET de 2 ou 4 MiB, timeout de 30 s, execução sequencial, sem retry. Mais 15 HEAD e 2 GET Range com resposta 403/17 bytes cada, diagnosticados em `cotahist-head.json`/`cotahist-range.json`. O ZIP de demonstração é o único dado de cotação transportado, fora de 2010–2024, para validar o mecanismo. Nenhum ano COTAHIST, nem o cadastro estrangeiro CSV completo, foi adquirido.

Índice `capture-index.json` SHA256 `7ff6607302bdfd30e4ed68f1d330fbb0f9035b74c12fcd20db69f96a5c3c0570`; cada item contém URL, UTC, status, tamanho, hash e nome do corpo/manifest. `verified-inventory.json` adiciona hash do manifest; `demo-profile.json` CRC/rodapé; `fca-profile.json` perfil offline; `b3-schema-extracts.json` localizadores XML; `pdf-locators.md` mapa de leitura completa; `access-condition-extract.txt` localiza a condição sem publicar headers/cookies.

| Label privado | HTTP | Bytes | SHA256 do corpo |
| --- | ---: | ---: | --- |
| b3-cotacoes-page | 200 | 59576 | `565af85a4a46a7368d05a9cccca5c7fb1f18bf95987d0d28dccb7aa22786c9ec` |
| b3-series-page | 200 | 51879 | `52d7210f1a0d9f70542c7dfe69a0c09736a0a14c5d16d7527fdb307054fc321c` |
| b3-layout | 200 | 421286 | `8b9633c44e1dc2229fb529931b4deb1d29fda9305a027d9c2c90a7ca96e8268f` |
| b3-cancelled-page | 302 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| b3-download-form | 200 | 15864 | `0125d613fef12caa49abbe29085ecd959eda3af72ab61df0a0a833e9210e5c48` |
| b3-hub-terms | 302 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| b3-demo | 200 | 27334 | `b0043b2d89f10e2c641d817586d19e880a862a53d1c633c787d5e7fc44c41618` |
| b3-series-js | 200 | 27519 | `7ee5efa6bdb5cadcdf58c824bc21a750f44200e9486d319ed7ee7a2f9c057f58` |
| b3-hub-canonical | 200 | 74202 | `85ef5c341ff5e5b831f6fcb108fe5a33dbd3251fa21a579eac969cb407ca596c` |
| b3-terms | 200 | 36129 | `a4316db8d0ec6fff4e40ca9d651ca9e36259c0b524dc3e32e0cebce1f93b6ff3` |
| b3-cancelled-canonical | 200 | 45099 | `75da923a2a95446bfdf0f8c8a4b7f85fc0636e3fe6ef336f0b283a885aefadae` |
| b3-units | 200 | 43989 | `811bc60ee600f906ca2e2750cb7f517d6ba5595f0006b52db8d943675d994570` |
| cvm-bdr-programs | 200 | 1190 | `ede5bb58a18e5cc517d695dd78557630c0b639a006d25446c165be89c680774b` |
| cvm-bdr-approved | 200 | 926601 | `dff97b128bd757e3fc2ed319379262544509b085f078e2469ec63ac3ea0feb8e` |
| cvm-bdr182 | 200 | 681470 | `b0be4b21f4daf33c935b4fb11470b39a2a25c3c4346bd5d9623d05426f371145` |
| cvm-foreign-cad-catalog | 200 | 25860 | `7a18665393b887a3dc553bc333f5156444738cc70b01b452e1e1f96fc6abbd91` |
| b3-bdr2025-boletim | 200 | 340145 | `f3031fb7ecf77685e4e94fe0d6882778f15ade4278b7edc7f65b1593862d282f` |
| cvm-foreign-dictionary | 200 | 8796 | `63712e2ddac843701be1e3f69973f0bdeb2f95d8038969dfa1a9ee50bcb02c51` |
| b3-up2data-page | 200 | 123036 | `5bac9c2dd317a51a38d5fd6e7a878f90f4dd67de62fc15346a42a6c321d4b6cb` |
| b3-bvbg028-mapping | 200 | 227347 | `6bb1cd941a6dbc8feaeb8f71e094ba44bed341f927f1ab02b9eeda3d77c01b7b` |
| b3-up2data-dictionary | 200 | 449283 | `96eacd4cc34f20d4157bb2f6973aee9dde59bcd90e0f16b258b2e2e11ada3faf` |
| cvm-nu-program-detail | 200 | 3162 | `2badb57cd5bd6a3d095fe05115e15ad6cd574820fe1e2947ddfe5f66b5820c29` |
| b3-public-data-2020 | 200 | 148605 | `99d8db5ae4ef7eae6056f8036432bb966bb3c7fd9e0575752e5784a945eeb006` |
| b3-bdr-admission-2022 | 200 | 88932 | `90464ab2030d2a1beb15f2ee0805918bd3d6b4c63864a8ab31d0baaa653630e0` |
| b3-public-data-migration2026 | 200 | 135454 | `10d15e722d1ccc904fc913fc8399507870eda629b4eee82aae6fc3a79150c6e1` |

Checks executados: hash/tamanho de 25 corpos + manifests, CRC/tamanhos/245 bytes/rodapé do ZIP de demonstração, CSV FCA contra o manifest da Issue 102, perfis de 2010/2024, esquemas XLSX inspecionados por XML e normas/PDFs lidos com localizadores. Conferência do autor, não revisão independente. Feynman deep-research/pdf-explore lidos; `/deepresearch` indisponível; rota alternativa autorizada: web primária + ferramentas locais, sem runtime/dependência nova. Nenhum software público, teste, commit ou alteração em dados aceitos.

Próxima fatia revisável: contrato de captura dos 15 COTAHIST com disponibilidade/tamanhos reais, arquivo de fontes e evidências de acesso; adição finita de programas BDR/CIA_ESTRANG/IPE necessária às candidaturas; classificação instrumental em camadas e fila de emissores/BCB. Pode começar offline com FCA + cadastro BCB existentes para 60 referências. A aquisição B3 bloqueada no ambiente permanece um limite técnico objetivo e não justifica certificar cobertura. O aceite completo exige explicitar, por referência/instrumento, quais relações foram provadas e quais não, sem excluir BDRs por CAD ausente ou confundir depositária com controladora.

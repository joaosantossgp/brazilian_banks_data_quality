# Vínculos jurídicos CVM–IF.data: identidade, controle e conglomerados

[Issue 105](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/105), continuação da entrega 102. Base de pesquisa: `2f6b95a684a1a6930cb8bfe82312d436b7b7cd3a`; branch `codex/cvm-ifdata-linkage-20261012`. Pesquisa A/B, pacote v2 e replay aprovados independentemente. São seis correspondências de pessoa jurídica, doze participações cadastrais e duas relações de controle. Não houve alteração de software ou escolha acadêmica de amostra. Estado de publicação/integração e revisão final da branch têm autoridade na Issue real.

## Problema corrigido na investigação

A entrega anterior autenticou CAD/FCA e reuniu ocorrências de BB, Bradesco e Itaú em 201012/202412. As chamadas exploratórias a `identity_evidence` forneceram `relationship=None` e nenhuma identidade jurídica completa da unidade BCB; seus resultados `unknown` descrevem esse objeto incompleto. Não demonstram inexistência de vínculo, nem uma investigação documental suficiente para descartá-lo. O arquivo privado anterior permanece intacto como registro daquela avaliação.

A revisão independente inicial da Issue 105 confirmou limitações estruturais do contrato legado: CNPJ completo obrigatório para qualquer ponta, uma única fonte e uma única vigência compartilhada. Esse formato não representa adequadamente um conglomerado identificado pelo BCB, nem uma cadeia documental de identidade. A revisão não aprovou nenhum vínculo real e não dispensou as fontes.

## Afirmações distintas

| Afirmação | O que precisa ser provado | O que não decorre dela |
|---|---|---|
| Mesma pessoa jurídica | Identificadores oficiais, sua semântica e as observações de cada ponta | Mesmo estabelecimento, registro CVM ativo ou listagem histórica |
| Controle holding–operadora | Controladora e controlada distintas, relação expressa e posição na data | Identidade entre as entidades ou substituição dos seus balanços |
| Instituição pertencente a conglomerado | Código oficial do grupo, instituição e relação cadastral na referência | CNPJ próprio do conglomerado ou equivalência entre consolidado financeiro e prudencial |
| Perímetro comparável para indicadores | Componentes, perspectiva, regime, janelas e regra metodológica aprovada | Resultado automático de identidade, controle ou liderança |

Uma pessoa jurídica pode ter estabelecimentos identificados por CNPJ completo. O conglomerado deve conservar seu namespace/código oficial; atribuir-lhe o CNPJ da líder mistura entidades de naturezas diferentes. A documentação oficial dos identificadores será examinada na [nota BCB](bcb-institution-identity-evidence-20261012.md), e controle/fatos declarados na [nota CVM/emissores](cvm-issuer-control-evidence-20261012.md).

## Tempo da observação e tempo do fato

Registrar separadamente referência do cadastro BCB, referência do formulário CVM, data do documento, data de entrega/reapresentação e data do fato localizado. Publicação posterior pode declarar posição em dezembro; isso exige o localizador do fato, não uma vigência inventada a partir da capa.

Para identidade por identificador oficial, observações em datas diferentes podem identificar a mesma pessoa jurídica se a semântica e a continuidade do identificador estiverem demonstradas. Não exigir artificialmente um novo documento CVM em dezembro apenas para reconhecer identidade; também não transmitir a dezembro o status ou a listagem observados em janeiro. Controle, composição e demais fatos mutáveis exigem sua própria prova temporal.

## Contrato e limites da pesquisa

Primeiro checkpoint: BB, Bradesco e Itaú nas referências 201012 e 202412, mantendo a ocorrência individual da holding Itaú separada da operadora e dos conglomerados. A/B possuem notas e bruto exclusivos; Root integra esta síntese. O contrato inicial e seu PASS independente autorizam somente pesquisa documental. Software ou artefatos de vínculos aceitos dependem de contrato adicional e revisão da evidência antes de sua escrita.

Reutilizar pacotes autenticados 102 e cadastro IF.data de 106 referências sem nova recuperação dos seus corpos. Arquivar documentos complementares em `data/raw/cvm-linkage-20261012/` com URL inicial/final, UTC, status, headers sanitizados, SHA-256 e localizador. Os limites de aquisição e as extensões fechadas de fonte constam na Issue. Falhas HTTP ou de aplicação permanecem diagnósticos, sem virar ausência de entidade.

`research` delega as investigações; Feynman `pdf-explore` orienta inspeção multipágina e localizadores. `/deepresearch` permanece indisponível nesta interface: usar fontes oficiais verificáveis e registrar a limitação, sem instalar runtime. Nenhuma fonte financeira complementar é admitida como dataset de valores; documentos societários são examinados para identidade, controle e perímetro.

Unidade, população, janela e adoção dos indicadores permanecem na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3), sob João/orientador. Investigar relações alternativas não escolhe a unidade acadêmica. A fronteira operacional permanece no [mapa 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2), sem operar o Project /3.

## Resultado por entidade e relação

| Emissor CVM observado | Código CVM literal FCA | CNPJ completo observado CVM | Individual IF.data identificado como mesma PJ | Referências verificadas |
|---|---|---|---|---|
| Banco do Brasil | `001023` | `00.000.000/0001-91` | `00000000` | 201012 e 202412 |
| Banco Bradesco | `000906` | `60.746.948/0001-12` | `60746948` | 201012 e 202412 |
| Itaú Unibanco Holding | `019348` | `60.872.504/0001-23` | `60872504` | 201012 e 202412 |

São seis correspondências, com datas próprias de observação: os FCA têm referência em 01/01; o cadastro BCB tem competência de dezembro. O dossiê conserva versão, ID documental, registro lógico, membro e hashes. Em 2024, os nomes CVM de BB/Bradesco usam `BCO`; o BCB usa `BANCO`. As duas denominações literais são conservadas. A identificação positiva usa a cadeia documental dos identificadores oficiais, sem matcher por nomes.

A [documentação IFData](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao), recurso `IfDataCadastro`, identifica `CodInst` como CNPJ da instituição ou código UNICAD do conglomerado. Tipo, campos de participação, linha própria do grupo e perspectiva desambiguam essas pontas. A [Circular 3500](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/49576/Circ_3500_v1_O.pdf), art. 1 e 2, identifica nominalmente as quatro bases e estava vigente em dezembro de 2010. O [layout RFB](https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf), p. 1, e a [Nota 47/2024](https://www.gov.br/receitafederal/dados/nota_cocad_no_47_2024.pdf), itens 1.1.1/4.1.2, distinguem entidade por básico e estabelecimento por inscrição completa. Os pins, localizadores e limites estão na nota A.

| Instituição individual | Financeiro em 201012 e 202412 | Prudencial em 202412 | Líder declarado nas duas referências |
|---|---|---|---|
| BB / `00000000` | `C0049906` | `C0080329` | `00000000` |
| Bradesco / `60746948` | `C0010045` | `C0080075` | `60746948` |
| Holding / `60872504` | `C0010069` | `C0080099` | `60872504` |
| Itaú Unibanco S.A. / `60701190` | `C0010069` | `C0080099` | `60872504` |

São oito participações financeiras e quatro prudenciais explicitamente declaradas nas linhas individuais autenticadas. As nove linhas dos conglomerados correspondentes foram conferidas. Campos prudenciais vazios em 201012 são preservados como ausência observada no recurso; não significam inexistência de grupo econômico. Códigos financeiros e prudenciais permanecem separados. O líder é um atributo declarado, sem virar identidade do grupo ou prova de controle acionário.

| Controladora → controlada | Data do fato | Capital votante declarado | Capital total declarado | Caminho do controle |
|---|---|---|---|---|
| Holding `60872504` → Itaú Unibanco S.A. `60701190` | 31/12/2010 | 100,00% | Desconhecido nesta prova | Direto ou indireto; modalidade exclusiva não estabelecida |
| Mesmas PJs distintas | 31/12/2024 | 100,00% | 100,00% | Direto ou indireto; modalidade exclusiva não estabelecida |

Em 2010, o [20-F, item 4C/p. 100](https://www.sec.gov/Archives/edgar/data/1132597/000114420411037730/v226649_20f.htm), remete à lista de subsidiárias da data; o [anexo 8.1](https://www.sec.gov/Archives/edgar/data/1132597/000114420411037730/v226649_ex8-1.htm), linha da operadora brasileira, explicita participação votante. Em 2024, o [20-F, nota 2(c)I, F-11/F-12](https://www.sec.gov/Archives/edgar/data/1132597/000129281425001684/itubform20f_2024.htm), descreve controle direto ou indireto e separa colunas de capital votante/total por ano. Os filings ocorreram em 27/06/2011 e 28/04/2025, respectivamente; os fatos localizados continuam sendo 31/12/2010 e 31/12/2024. São declarações do emissor arquivadas na SEC, sem presumir certificação pelo regulador. Pontas por PJ/nome/país e localizadores foram revisados em A+B; não foi fabricada matriz CNPJ14 histórica da operadora.

## Pacote consultável e regra de curadoria

Destino novo ignorado: `data/curated/cvm-ifdata-linkage-20261012-v2/`. Replay separado: `data/curated/cvm-ifdata-linkage-replay-20261012-v2/`. Cinco arquivos, inventário fechado pelo manifest:

| Arquivo | Conteúdo | Registros | SHA-256 |
|---|---|---:|---|
| `identity.csv` | Emissor observado → individual da mesma PJ | 6 | `d37872514ce3851e655a18103c3d233238a7ba61b593375f1f95fc9e7f40d0eb` |
| `membership.csv` | Instituição → conglomerado, perspectiva/referência/líder | 12 | `530f89289de5dbd2aa81e65681ec9a80c1221fa8dd63b018931f75e48618a3f5` |
| `control.csv` | Holding → operadora, data/tipo de participação/limites | 2 | `14ecd4ed73f0bb486ea4954679ad1111df601ca1d0094fb8efd6f4202714f385` |
| `claims.json` | 20 afirmações com observações literais, fontes e localizadores | 20 | `409b5e0ac25c4eb1f183d441e85e91c4f780a0df63a6a3fa7bce39e4d2f13dd9` |
| `manifest.json` | Pins de entrada, contagens e hashes dos quatro arquivos | — | `5aaf7c8d8beb0dc5fb496483cdfec5d275e6e8865441d7f0473712ad1374812b` |

Esta é **curadoria documental finita revisável**, não um algoritmo universal de identidade. Os valores `known` correspondem às afirmações delimitadas de identidade/controle; `declared_by_bcb` qualifica a participação cadastral. Aceite do pacote exige registro independente externo na Issue com o pin do manifest. Hash autentica bytes; não substitui conferência do conteúdo das fontes. O JSON conserva limitações e explicita que a API legada `identity_evidence` não foi usada.

A versão inicial permanece intacta, com manifest `fb9fe1def22c0f528166059b8bdd46eb511c409e829882b7115d25f95564f9e6`, como checkpoint anterior à correção documental P3. A versão 2 inclui o índice SEC2010 e campos próprios `filing_date`, `period_of_report` e fonte do filing para 2010/2024; uma data de emissão distinta não foi estabelecida e não é fabricada. Os três CSVs e as vinte conclusões permaneceram iguais. A [extensão do contrato](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/105#issuecomment-6135119890) precedeu os dois destinos novos; os cinco arquivos v2 e replay têm hashes iguais. A versão 2 recebeu PASS independente no pin final acima; P3 encerrado. A versão inicial não deve ser confundida com o pacote aceito final.

Foi escolhido entregar a prova consultável neste recorte. Afrouxar guardas da API legada misturaria contratos; construir uma engine genérica antes da expansão aumentaria custo sem resolver uma lacuna documental adicional. Nenhum caller legado muda de comportamento. A futura admissão em lote precisa adotar os tipos/distinções demonstrados aqui, com contrato e testes próprios; não usar o `unknown` legado para apagar a curadoria revisada, nem usar estas vinte afirmações como autorização de qualquer join.

A reextração autenticou o manifest CVM `5abaef4891fdf9eb8eb86aecedbce7694005d98999b85561881018b71c3b79a7` e o cadastro `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1`. Corpus documental A: índice `48d6bf5566a07cf29275ccc6cd5bc72e455b34ba2be72563582700fd4429f36c`; B: inventário `41f5bcca28ebefeb27ce7d07a71a9c5b5db7d464214726a86eadd6a2bb3d6d15`. Fonte/UTC/hash/posição do cadastro e fonte/membro/documento/versão/ordinal CVM estão nas observações. Corpos normativos/SEC possuem URL, UTC, SHA e localizador próprios; headers/cookies ficam fora do pacote consultável e do Git.

## Implicação metodológica e pendências reais

Para a monografia, há agora prova documental que distingue **emissor, banco operacional e conglomerado** nestes casos. Escolher a unidade analítica continua necessário: o emissor Holding não deve receber automaticamente índices calculados com o individual da operadora, nem o conglomerado ser tratado como a mesma PJ da holding. Rentabilidade, crédito, capital, médias/janelas e fronteiras regulatórias precisam conservar perspectiva e componentes na unidade escolhida. A [proposta por tipo institucional](institution-type-indicator-methodology-20261012.md) permanece a referência de alternativas; nenhum indicador foi adotado ou recalculado nesta fatia.

Permanecem fora do aceite: trajetória do registro CVM 1279, reconciliação das datas Itaú de listagem/negociação, estado histórico contínuo de registro/listagem, composição jurídica integral dos conglomerados, equivalência entre perímetros e expansão para outras entidades/referências. São questões distintas das identidades e controles positivamente provados. Não condicionam retrospectivamente estas vinte afirmações a um estabelecimento14 idêntico ou a uma escolha acadêmica futura.

Expansão deve usar novas observações datadas e tratar reorganizações/conflitos por entidade. Não interpolar o intervalo 2010–2024 a partir dos extremos, classificar elegibilidade por cadastro atual ou transformar cada igualdade de oito caracteres em identidade. A inexistência de regra universal de não reutilização nas fontes examinadas limita a generalização; não desfaz a identificação positiva dos quatro casos nomeados e revisados.

## Verificação por checkpoint

- Pesquisa A: PASS independente dos bytes `8c6f60b3b6ca2f9e7b20b361b180c79ffb938ae135d336f21828b3bcaec24360`, 17 corpos/520.454 bytes, 10 HTTP200/7 falhas. Conferidos documentos, duas fontes JSON/Parquet, 17 linhas selecionadas, CAD e limitação BCBase.
- Pesquisa B: PASS independente dos bytes `d276c357b913d9649333b6ada39db4e14b51a2e6f5784596e58ecf24df69fee2`, 16 tentativas/29.345.027 bytes. Conferidos seis localizadores FCA e documentos SEC de controle; falhas preservadas.
- Contratos de admissão A2 e composição A+B: PASS independente antes da criação dos artefatos, nos comentários [A2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/105#issuecomment-6135035422) e [composição](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/105#issuecomment-6135077603).
- Reextração e geração local: seis identidades, doze participações, dois controles; IDs únicos, observações e corpos autenticados. Nomes abreviados CVM foram conservados separadamente do nome BCB, sem normalização silenciosa. Replay em destino novo produziu os mesmos cinco hashes, incluindo manifest. Preparação operacional preservada em `.scratch/cvm-linkage-20261012/root/curate.py`; não é módulo de produção ou matcher reutilizável.
- Revisão independente do pacote v2/composição: PASS no manifest `5aaf7c8d8beb0dc5fb496483cdfec5d275e6e8865441d7f0473712ad1374812b`, 20 afirmações, 14 fontes documentais e 40 observações. CSVs/JSON/manifest/replay conferidos; P3 documental corrigido em destino novo e revalidado.
- Checks documentais do integrador: 42 links Markdown inspecionados nas três notas, todos os destinos locais existentes; inventário público restrito às três notas novas, sem alteração de arquivos tracked anteriores. Revisão final de branch/SHA e estados remotos são registrados na Issue. Testes de software não se aplicam ao diff documental; a conferência das fontes e dos dados não é descrita como teste de software.

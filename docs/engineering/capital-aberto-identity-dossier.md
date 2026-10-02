# Dossiê de identidade: emissores de capital aberto e unidades IF.data

Etapa 2 executada em 2026-10-01, no computador autorizado. Esta entrega separa o emissor observado no cadastro CVM/B3 atual, os candidatos observados nos cadastros individuais IF.data de 201012/202412 e qualquer vínculo legal/temporal entre eles. Não produz junção de valores financeiros nem define a amostra da tese.

O ledger `data/derived/expansion-20261001/identity-evidence.csv` (somente local, excluído da publicação) contém **8 registros de candidatos**, pertencentes a três casos e dois períodos: BB (2), Bradesco (2), Itaú Holding (2) e o banco operacional como candidato distinto do caso Itaú (2). Todos os vínculos emissor–unidade IF.data permanecem `unknown`. Ausência de prova não significa que a relação não existe nem exclusão definitiva da amostra. O ledger inclui os resultados reproduzíveis da API, linhas cadastrais originais, localizadores, URLs, corpos, manifests, hashes e horários de recuperação.

## Banco do Brasil

O cadastro CVM atual observa código **1023**, denominação `BANCO DO BRASIL S.A.`, CNPJ **00.000.000/0001-91**, `SIT=ATIVO` e evento `DT_REG=1977-07-20` (CVM, linha CD_CVM=1023). B3 observa `codeCVM=1023`, prefixo `BBAS`, CNPJ bruto **191** e `dateListing=18/06/1921` (B3-1023). A correspondência atual CVM–B3 usa o código CVM exato; o CNPJ B3 permanece bruto, sem completar zeros a partir de outra fonte.

Os dois cadastros IF.data individuais recuperados observam nome `BANCO DO BRASIL S.A.` e código de exibição **0** (CAD-201012/CAD-202412, c0=0). Em 202412 o campo bruto c33 contém `00000000`; em 201012 c33 está estruturalmente ausente. O dicionário oficial define a coluna de código id79706/lid0 como `Conglomerado ou CNPJ` (INFO-201012/INFO-202412). Ele não fornece aqui CNPJ legal completo de 14 dígitos nem uma cadeia temporal exata que confirme a identidade desse registro com o emissor. O nome e os zeros semelhantes são indícios para investigação, não prova aceita. Vínculo legal/temporal, registro histórico, listagem histórica e tickers históricos: **unknown**.

## Bradesco

O cadastro CVM atual observa código **906**, denominação `BANCO BRADESCO S.A.`, CNPJ **60.746.948/0001-12**, `SIT=ATIVO` e `DT_REG=1977-07-20` (CVM, CD_CVM=906). O resultado B3 selecionado por `codeCVM=906` observa CNPJ **60746948000112**, prefixo `BBDC` e `dateListing=26/11/1946` (B3-906). Os dois CNPJs completos observados concordam no cadastro atual após remover apenas pontuação. Esse resultado atual não cria intervalo histórico de elegibilidade.

O cadastro IF.data individual observa `BANCO BRADESCO S.A.`, c0=**60746948**, nos dois períodos. Em 202412 c33 também contém `60746948`; em 201012 c33 está ausente. Os oito dígitos não são completados com filial/verificadores para produzir os 14 do emissor. Falta documento primário que identifique exatamente as duas pontas e date o vínculo na referência analisada. Vínculo emissor–IF.data e elegibilidade histórica: **unknown** (CAD-201012/CAD-202412 e INFO-201012/INFO-202412).

A busca atual B3 retornou quatro pessoas jurídicas. A seleção pelo nome `BRADESCO` isoladamente juntaria bancos de cartões/financiamentos e arrendamento mercantil ao emissor selecionado. A presença de `dateListing=31/12/9999` em outros resultados é preservada no corpo B3, sem usá-la como data histórica de listagem (B3-906, results completo).

## Itaú Unibanco Holding e banco operacional

O emissor CVM **19348** possui CNPJ **60.872.504/0001-23** e denominação `ITAÚ UNIBANCO HOLDING S.A.`, com `SIT=ATIVO` e `DT_REG=2002-12-30` no cadastro atual (CVM, CD_CVM=19348). B3 selecionado pelo código exato observa **60872504000123**, prefixo `ITUB` e `dateListing=30/12/2002` (B3-19348). A busca B3 também retorna outra entidade; ela não é o emissor 19348.

**A própria holding aparece no cadastro individual IF.data dos dois períodos**, c0=**60872504**, separada de `ITAÚ UNIBANCO S.A.`, c0=**60701190**. As duas linhas compartilham campos brutos de agrupamento, como c14/c23, mas isso não estabelece equivalência econômica, controle legal ou perímetro consolidado. Em 202412 suas linhas têm c33 `60872504` e `60701190`, respectivamente; em 201012 c33 está ausente. Os nomes e códigos observados tornam os dois candidatos reviewáveis, sem convertê-los em CNPJ completo ou cadeia jurídica datada (CAD-201012/CAD-202412).

O cadastro individual de 202412 também inclui `c4=C` e `c5=Conglomerado` nas quatro linhas escolhidas, enquanto o nível de consulta é 1006 individual. Esses campos são retidos como atributos brutos do cadastro, sem reclassificar a observação financeira selecionada para um nível consolidado. A metodologia oficial define o nível individual por personalidade jurídica, não consolidado (BCB-METHOD, divMetodoMount, Instituições Individuais). Qual entidade representa a pergunta da tese e quais vínculos/scope documentalmente sustentam essa representação continuam em aberto.

Identidade exata emissor–registro da holding, relação holding–banco, membros/perímetro de conglomerado e continuidade entre referências: **unknown**. A presença do registro da holding oferece uma opção direta para investigação; não autoriza substituir silenciosamente o emissor por seu banco operacional.

## Regras de aceitação da API

`identity_evidence(issuer, reporting_entity, relationship)` conserva as identidades separadas e os campos recebidos. Sem relação fornecida, devolve `unknown` e razões. Para uma relação `known`, exige CNPJ completo **textual** das duas pontas, CNPJs documentados iguais aos recebidos, namespace/código exatos da unidade, tipo explícito (`same_legal_entity`, `controls` ou `member_of_conglomerate`) e fonte primária BCB/CVM/B3 com URL HTTPS, SHA-256, recuperação UTC e localizador.

A evidência deve declarar **uma data pontual exatamente igual à referência** ou **intervalo fechado que contenha a referência**. `same_legal_entity` exige igualdade dos dois CNPJs completos; uma relação de controle mantém as pessoas jurídicas distintas. Data de registro, data de listagem, nome parecido, status atual, oito dígitos ou número com zeros perdidos não substituem esses requisitos. Intervalo sem fim explícito não presume continuidade até o presente.

A API valida os metadados fornecidos; o chamador deve primeiro verificar o hash/corpo e a afirmação jurídica no localizador. Os documentos presentes foram verificados com `archive.load_body`. Nenhum deles fornece, nesta entrega, o conjunto de requisitos para confirmar vínculo emissor–IF.data. Mesmo uma relação conhecida não promove os estados de registro ou listagem históricos e não produz junção financeira. Fixtures dos testes que aceitam relações são sintéticas e não fundamentam as conclusões reais.

O campo c33 é retido sem semântica confirmada. O dicionário disponível associa id79706/lid0 ao código c0 e descreve `Conglomerado ou CNPJ`; não demonstrou a definição de c33. Não foi feita reconstrução de código ou mapeamento por prefixos.

## Limites temporais e próximas decisões humanas

O documento oficial CVM explicita cadastro referente ao último dia útil e atualização diária (CVM-DOC, descrição/Periodicidade). Datas de eventos e status ativo atuais não provam registro ativo ininterrupto em 2010/2024. Os resultados B3 atuais trazem datas, sem painel de intervalos históricos no corpo recuperado; listagem histórica, classes e tickers ficam `unknown`. As evidências atuais selecionadas não são uma população histórica completa de emissores e não definem regra de sobrevivência.

| Opção de unidade | O que representa | Consequência dos três casos / prova necessária |
|---|---|---|
| Pessoa jurídica individual do próprio emissor | Cada registro IF.data não consolidado cuja identidade exata com emissor elegível for comprovada | BB/Bradesco ainda precisam de identidade legal completa datada. Itaú Holding tem candidato próprio observado, cuja equivalência jurídica precisa ser documentada. Não substituir a holding pelo banco por conveniência. |
| Banco operacional individual vinculado ao emissor | Pessoa jurídica bancária regulada, diferente da holding quando aplicável | Itaú exige duas identidades legais exatas e relação de controle datada. A medida não representa automaticamente todas as operações da holding. |
| Conglomerado financeiro ou prudencial | Perímetro consolidado definido pela fonte escolhida | Exige prova datada do elo com emissor, namespace/código do conglomerado e composição/perímetro; os dois níveis não são intercambiáveis. A entrega atual só observa cadastro de nível individual. |

Antes de ampliar a amostra, a decisão humana precisa escolher **unidade principal**, tratamento de holdings e papel de cada nível consolidado; **janela temporal final**; e **regra de elegibilidade de capital aberto**, distinguindo registro CVM de evidência B3 de negociação/listagem. Os extremos 201012/202412 e o lote técnico 202312 não escolhem a janela da tese. A ausência de prova exige investigação ou estado desconhecido, não exclusão definitiva. Sem esses critérios e uma cadeia de identidade aceita, nenhuma das alternativas é escolhida automaticamente.

Documentação adicional prioritária, caso a decisão demande confirmação: cadastro oficial com identidade legal completa na data de referência; ato societário/registro primário que identifique ambas as pontas e vigência; evidência B3 histórica para instrumento/classe elegível; e, para consolidação, documento oficial de membros/perímetro naquela data. Não se realizou busca ampla de históricos nem coleta de demonstrações financeiras CVM/B3.

## Proveniência verificável

Os corpos de cadastro, B3, dicionário e metodologia já estavam arquivados e foram reutilizados com validação de SHA-256. O único GET novo desta etapa foi a documentação cadastral CVM: HTTP 200, **25.205 bytes**, sem falhas; manifesto preservado em `data/raw/expansion-20261001-identity/`. Não se recuperou arquivo financeiro nem consulta de outro projeto. Horário de recuperação não é data de vigência da relação.

| ID | URL exata | SHA-256 | Recuperado UTC | Corpo no repositório |
|---|---|---|---|---|
| CVM | [Fonte oficial](https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv) | `5b648b892a52706b09da97241514743e3682b35b6c8781742fe384b1e50f8796` | 2026-10-01T01:56:33.106361+00:00 | `data/raw/discovery-20261001/20261001T015632921533Z_cvm_cadastro_ee4a3cd3d46d4fd8acae79f4ebca1a88.bin` |
| CVM-DOC | [Fonte oficial](https://dados.cvm.gov.br/dataset/cia_aberta-cad) | `b23efb40a7bdc683eefe8c76e5d3f093d6d2220388a4b63a331e7a5607ac5819` | 2026-10-01T03:29:32.448918+00:00 | `data/raw/expansion-20261001-identity/20261001T032932242529Z_cvm_cadastro_documentation_00977561260145478cf9517ffb7f76dc.bin` |
| B3-1023 | [Fonte oficial](https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetInitialCompanies/eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjIwLCJjb21wYW55IjoiQkJBUyJ9) | `4c6eadc8076bc3f76e7f7631a012510424d92ba2399b2f72ebc08c36abc49c81` | 2026-10-01T02:01:58.259633+00:00 | `data/raw/discovery-20261001/20261001T020158134000Z_b3_current_metadata_c1aa82fa60c14f718e51ea7b02163c94.bin` |
| B3-906 | [Fonte oficial](https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetInitialCompanies/eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjIwLCJjb21wYW55IjoiQlJBREVTQ08ifQ==) | `f6b776637f15b746d10bf17e7e2e1b36bae29bebe4ef8f1e7f72a936ddd6e5aa` | 2026-10-01T02:01:58.369603+00:00 | `data/raw/discovery-20261001/20261001T020158268142Z_b3_current_metadata_3e2258400ddf4b0b8110e5a567f3151d.bin` |
| B3-19348 | [Fonte oficial](https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetInitialCompanies/eyJsYW5ndWFnZSI6InB0LWJyIiwicGFnZU51bWJlciI6MSwicGFnZVNpemUiOjIwLCJjb21wYW55IjoiSVRBVSBVTklCQU5DTyJ9) | `cee11df245e9528fca6c5c4c5694ee080dec114cbec942a4fe1fcb2b6cd5bb4b` | 2026-10-01T02:01:58.500718+00:00 | `data/raw/discovery-20261001/20261001T020158377108Z_b3_current_metadata_920e7679a30544fe9ed629dd059e1572.bin` |
| CAD-201012 | [Fonte oficial](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F201012%2Fcadastro201012_1006.json) | `49ff09d550bccbc401e016f6b7427b5e6ca475c8272d8654e9f46e698d0a9ddc` | 2026-10-01T01:32:34.196345+00:00 | `data/raw/discovery-20261001/20261001T013233187408Z_portal_cadastro_201012_357cd54cfbe74ee8abf53155089380a2.bin` |
| INFO-201012 | [Fonte oficial](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F201012%2Finfo201012.json) | `aa32c85142afecb62c9a5999af1ee220246d9aa1383bc416a5c251177d0f03bb` | 2026-10-01T01:32:34.414722+00:00 | `data/raw/discovery-20261001/20261001T013234212213Z_portal_info_201012_c47cbdb67f7d406db3615157e4feeff5.bin` |
| CAD-202412 | [Fonte oficial](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Fcadastro202412_1006.json) | `5200301d6dabad5240b2d65aada6cb2179d75d497999c9b08d6c011a74043685` | 2026-10-01T01:32:35.145451+00:00 | `data/raw/discovery-20261001/20261001T013234426740Z_portal_cadastro_202412_c363a9e39165404aa08831eaa26dd2f5.bin` |
| INFO-202412 | [Fonte oficial](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Finfo202412.json) | `9c09219eeb7aa558e0ac74e32b905ba940ec00b0bc01f761b1d086aef86cca28` | 2026-10-01T01:32:36.021567+00:00 | `data/raw/discovery-20261001/20261001T013235163159Z_portal_info_202412_4b180f95c53d44d4b5f3a4444c586e20.bin` |
| BCB-METHOD | [Fonte oficial](https://www3.bcb.gov.br/ifdata/index2024.html) | `bd8936773c7f54933cd428d918671bed7f767060618021540b6488671c3780f1` | 2026-10-01T01:28:20.707297+00:00 | `data/raw/discovery-20261001/20261001T012820520704Z_portal2024_8d85bdfd34dc4e81b52a360e00439840.bin` |

Cada corpo tem o manifesto `.json` correspondente, preservando URL/parâmetros, status HTTP, headers e diagnósticos. O CSV inclui caminhos exatos de ambos por candidato. Localizadores de fonte estão em cada caso/linha; estado desconhecido é explícito quando inexiste documento/intervalo de relação.

## Verificação de implementação

RED: `python -B -m unittest discover -s tests -p test_metadata.py -v` executou 16 testes; 23 falhas de assertions/subtestes esperadas por `identity_evidence API missing`, sem erro de importação; os três testes anteriores passaram. GREEN: a mesma suíte executou **16 testes, todos OK** após a implementação. Os testes rejeitam junção por nomes, CNPJ truncado/numérico, falta de fonte/intervalo, namespace/código divergente e datas de evento convertidas em estado histórico; aceitam apenas provas sintéticas completas dentro de sua vigência.

Verificação complementar executada nesta etapa: `python -B -m unittest discover -s tests -v` passou em **42/42 testes**. Conferência do CSV verificou **8 registros**, **9 manifests referenciados nas linhas**, igualdade de URLs/hashes/horários/caminhos e replay exato da API a partir do JSON preservado; todos os estados históricos e vínculos sem prova permaneceram `unknown`. A metodologia BCB adicional no dossiê também teve o corpo/hash verificado, totalizando 10 corpos primários reutilizados/arquivados nesta entrega.

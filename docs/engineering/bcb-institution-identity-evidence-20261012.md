# Identidade institucional BCB: evidência por pessoa jurídica e conglomerado

Pesquisa A da [Issue105](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/105), base `2f6b95a684a1a6930cb8bfe82312d436b7b7cd3a`, branch `codex/cvm-ifdata-linkage-20261012`. Checkpoint local para revisão independente; não constitui admissão de vínculos nem seleção acadêmica de unidade. Reutiliza os pacotes102 e cadastro106referências, sem nova coleta financeira. Destino conforme arquitetura: nota de evidência em engineering, documentação bruta em data/raw e preparação em .scratch.

## Resultado que a evidência sustenta

As quatro instituições individuais Banco do Brasil, Banco Bradesco, Itaú Unibanco Holding e Itaú Unibanco aparecem separadamente nas referências IF.data201012 e202412. A cadeia de identificação é mais forte que coincidência de prefixo: o dicionário BCB identifica o campo nativo como CNPJ da instituição; o cadastro temporal contém nome, código e vínculos; a Circular3500 identifica nominalmente as quatro bases em documento vigente em dezembro2010; BCBase retorna base8, identificador interno e CNPJ14 juntos nas duas consultas. A raiz identifica a entidade; ordem/DV distinguem seus estabelecimentos. A matriz CVM e o estabelecimento indicado pelo BCBase podem ter14posições diferentes sem serem pessoas jurídicas diferentes. Isso exige uma relação tipada e evidência temporal, não completar seis dígitos no código IF.data.

Para BB/Bradesco/Holding, a identidade com a pessoa jurídica emissora CVM é sustentada pela cadeia abaixo, sujeita ao gate independente e ao contrato técnico. A identidade da operadora Itaú está positivamente identificada no BCB; sua relação de controle com a Holding depende do dossiê B. Identidade não implica controle, listagem, registro ativo em cada data ou perímetro contábil equivalente. Nenhum vínculo foi escrito ao validador.

## Fontes e localizadores

**IFData, documentação v1.** [Documento oficial](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao), JSON embutido na atribuição `$scope.especificacao`, recurso `IfDataCadastro`, `tipo.propriedades` por `localizacao.nome`: `CodInst` designa CNPJ da instituição ou código de conglomerado UNICAD; `CodConglomeradoFinanceiro`/`CodConglomeradoPrudencial` designam participação no respectivo conglomerado; `CnpjInstituicaoLider` identifica a líder financeira/prudencial; `Data` é referência AAAAMM. `Td` distingue I/C, mas a descrição abreviada chama I de independente enquanto as linhas individuais abaixo têm I mesmo integrando conglomerado. Portanto não interpretar `Td=I` como ausência de participação; consultar os campos próprios e a perspectiva. `Situacao=A` é atividade BCB, não statusCVM. Documento atual recuperado em2026 não prova sozinho a versão do cadastro2010.

**Metodologia IF.data.** [PDF oficial](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf), p1 tabela Informações Contábeis e de Capital e p2 notas1–3. Individuais são apresentados por personalidade jurídica em nível não consolidado, disponíveis desde março2000; conglomerados financeiros representam consolidação de entidades relacionadas. Prudencial é perspectiva própria, disponível desde março2014. A consolidação não atribui personalidade jurídica ao conjunto. O PDF também explicita mudança em2018 nas agências externas das independentes; identidade não elimina essa diferença de perímetro.

**BCBase v2.** [Catálogo oficial](https://dadosabertos.bcb.gov.br/tr/dataset/dados-cadastrais-de-entidades-autorizadas), descrição e fonte UNICAD; [documentação oficial](https://olinda.bcb.gov.br/olinda/servico/BcBase/versao/v2/documentacao), `$scope.especificacao.recursos`, `EntidadesSupervisionadas`: parâmetro `dataBase`, formato MM-DD-YYYY; propriedades `database`, `codigoCNPJ8`, `codigoCNPJ14`, `codigoIdentificadorBacen`. A documentação define a base8 como raiz de identificação da pessoa jurídica e o identificadorBacen como gerado pelo cadastro único. A descrição de `database` informa a data selecionada na consulta; não promete que todos os atributos retornados sejam versões históricas preservadas daquela data. O catálogo descreve cadastro mestre mantido por autorizações. Não transformar essa função em arquivo vintage sem evidência adicional.

**Circular3500/2010.** [Original BCB](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/49576/Circ_3500_v1_O.pdf), p1 art1 tabela CNPJ/nome, ordens2,5,6; p2 art2: vigência01/08/2010–31/01/2011. Identifica00.000.000 Banco do Brasil,60.746.948 Bradesco,60.872.504 Holding e60.701.190 Itaú Unibanco. É amostra TBF/TR: não prova composição completa de grupo, participação acionária ou perímetro IF.data. A data de publicação e a vigência são independentes da data de recuperação2026. P3 conserva a ressalva DOU/Sisbacen.

**RFB: entidade e estabelecimento.** A [extensão de domínio autorizada](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/105#issuecomment-6134893663) cobre apenas os dois PDFs documentais. [Layout CNPJ](https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf), p1 EMPRESAS/ESTABELECIMENTOS: base8 pertence à empresa; ordem identifica estabelecimento e DV completa a inscrição; há marcador matriz/filial. [Nota Técnica47/2024](https://www.gov.br/receitafederal/dados/nota_cocad_no_47_2024.pdf), alterada pela86/2024, p1 item1.1.1 e p2 item4.1.2: distingue entidade8 de estabelecimento14. São documentos semânticos atuais, não fontes de situação cadastral2010. Não houve aquisição de universoRFB. A leitura mapeou os PDFs completos e seus limites, registrada privadamente.

## Pontas IF.data autenticadas

Reuso do pacote local documentado na [nota cadastro](ifdata-cadastro-20261011.md). Manifest curated SHA256 `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1`. Os JSON originais foram autenticados contra `source_sha256` do manifest; Parquet correspondentes também conferidos. Extrações CSV foram comparadas campo a campo com JSON para as17linhas selecionadas. Posições abaixo são índices1-based em `value` do JSON; correspondem à linhaCSV posição+1.

| Referência | Pessoa jurídica / CodInst literal | Posição JSON | Financeiro | Prudencial | Líder literal |
| --- | --- | ---: | --- | --- | --- |
|201012|BB / `00000000`|105|C0049906|vazio|00000000|
|201012|Bradesco / `60746948`|41|C0010045|vazio|60746948|
|201012|Holding / `60872504`|315|C0010069|vazio|60872504|
|201012|Operadora / `60701190`|316|C0010069|vazio|60872504|
|202412|BB / `00000000`|117|C0049906|C0080329|00000000|
|202412|Bradesco / `60746948`|48|C0010045|C0080075|60746948|
|202412|Holding / `60872504`|639|C0010069|C0080099|60872504|
|202412|Operadora / `60701190`|386|C0010069|C0080099|60872504|

Todas oito linhas têm `Td=I`, `Situacao=A`. Não há código prudencial preenchido201012; isso não é evidência de inexistência de qualquer grupo econômico. Os códigosC possuem linhas próprias TdC: BB financeiro posições264/291; Bradesco274/331; Itaú314/384, respectivamente201012/202412. Em202412, prudenciais BB292,Bradesco332,Itaú385. Relação explícita de participação vem do campo de cada instituição; liderança vem do campo específico, sem substituir códigoC pelo CNPJ da líder. Líder igual em duas referências não prova continuidade em todos os dias intermediários.

| Fonte reutilizada | SHA256 |
| --- | --- |
| JSON201012,4596linhas | `73f0fe02ecd9fe625e235a03fa9c03d94eadc96eee06276c0155d799eb71c9a0` |
| JSON202412,5744linhas | `9b5ee21a572fbdbc8de6e5071fb7986b024292691edc42530b9a6ee36560436e` |
| Parquet201012 | `f52e0868207d1eac406c51b922db1917980ea1fb3d65a7e1ef51f4b351c99ff2` |
| Parquet202412 | `5ab1d3a0f46fd14b80b7ed2240aede829a8df627b78198d136f27206829d9ce9` |

Origem local autorizada: `data/raw/ifdata-cadastro-20261011/ifdata_cadastro/json/` e `data/curated/ifdata-cadastro-20261011/` do checkout principal. Nenhum GET repetido. Preservar também URL/UTC do pacote de origem; este checkpoint não reconstitui cabeçalhos inexistentes da aquisição anterior.

## Consulta BCBase finita e diferença material nos14dígitos

Duas respostas HTTP200, `EntidadesSupervisionadas(dataBase=@dataBase)`, datas12-31-2010/12-31-2024, filtro OR somente quatro bases, projeção sete campos e `$top=8`. Cada resposta contém quatro registros, sem `@odata.nextLink`, sem truncamento observado; `database` retorna exatamente2010-12-31/2024-12-31. URLs integrais e parâmetros estão em cada manifest e no índice bruto. A consulta é finita e não varreu universo de instituições. Resultados abaixo são iguais nas duas respostas, exceto `database`.

| Nome | Base8 | Identificador Bacen | CNPJ14 observado BCBase | Situação |
| --- | --- | --- | --- | --- |
| Banco do Brasil S.A. |00000000|Z9999996|00000000787949|3 / Autorizada em Atividade|
| Banco Bradesco S.A. |60746948|Z9982916|60746948984457|3 / Autorizada em Atividade|
| Itaú Unibanco Holding S.A. |60872504|Z9982883|60872504000980|3 / Autorizada em Atividade|
| Itaú Unibanco S.A. |60701190|Z9982935|60701190500255|3 / Autorizada em Atividade|

O serviço devolveu estabelecimentos distintos das matrizesCVM. Não afirmar que esses estabelecimentos existiam nas duas datas: o contrato do parâmetro não assegura historicidade de cada atributo. A constância do identificador interno, nome e raiz corrobora identidade das pontas, junto à Circular vigente2010 e ao cadastroIF.data datado. Não tratar a igualdade de CNPJ14 entre consultas como prova de persistência histórica da sede.

O pacote102 contém CAD de BB `00.000.000/0001-91`/CVM1023, Bradesco `60.746.948/0001-12`/906 e Holding `60.872.504/0001-23`/19348 e1279. Manifest SHA256 `5abaef4891fdf9eb8eb86aecedbce7694005d98999b85561881018b71c3b79a7`; CAD SHA256 `e3201269c374ae3fc83c4cedb2750588216905638b67548e7535c3c9894dd782`. Linhascurated260,248,1538/1537; `__source_row`259,247,1537/1536. O código1279 é registro separado, não duplicata apagável; a situação histórica de registro/listagem exige sua própria evidência. CAD atual sozinho não prova estadoCVM em dezembro2010/2024. A evidênciaFCA e de controle temporal é responsabilidade da pesquisaB e da síntese.

## Implicações para contrato técnico e limites residuais

1. Separar namespace IF.data individual por CNPJ-base, identificadorBacen, CNPJ de estabelecimento, códigoC financeiro/prudencial e códigoCVM. Conservar literais e leadingzeros. `00000000` é baseBB expressamente identificada por norma vigente2010 e cadastro; não é null nem número zero descartável.
2. Admitir relação de mesma pessoa jurídica quando as duas pontas autenticadas, os nomes históricos e os identificadores tipados fecharem a cadeia. Não derivar CNPJ14, não exigir que matrizCVM e estabelecimentoBCBase tenham14iguais, nem aceitar só prefixo sem prova das pontas.
3. Admitir separadamente participação financeira, participação prudencial e liderança por referência, usando campos nativos e linha de conglomerado. Conglomerado tem código próprio; exigir CNPJ14 próprio do conjunto inventa personalidade/identificador que a fonte não oferece. Não transformar líder em identidade do conglomerado.
4. Holding60872504 e operadora60701190 são pessoas jurídicas distintas nas duas datas. Participar de C0010069 e ter líder60872504 não prova sozinho participação acionária exata, controle ou igualdade de perímetro consolidado. Essas relações permanecem próprias.
5. Não foi localizada, nas fontes primárias consultadas, regra universal explícita de não reutilização do CNPJ básico. Isso impede afirmar um teorema longitudinal para qualquer raiz/período, mas não invalida identificação positiva dos quatro casos por registros datados, nomes, Circular vigente2010 e identificadorBacen. Não interpolar alterações, statusCVM ou continuidade diária; expansão exige novas observações e busca por alterações/reorganizações.
6. As respostasBCBase devem ser classificadas como cadastro consultado por data-base com limitação de historicidade dos atributos. Erro de consulta não equivale a zero. As consultas iniciais com espaço codificado como `+` produziram400; alternativa com parênteses também400; a URL OData com espaços `%20` retornou200. Foram tentativas manualmente distintas, sem retry automático; todas preservadas.

## Inventário e verificação local

Aquisição documental sequencial encerrada em17corpos,520.454bytes:10HTTP200 e7falhas preservadas. Limites contratados24corpos,20MiB/corpo,128MiBtotal,timeout30s,semretry automático respeitados. HEAD foi medido quando possível: alguns deram403/502 e os catálogos relataram6402bytes apesar do corpoGET maior; limite real foi aplicado aos bytes recebidos. Nenhum universo cadastral/financeiro foi adquirido. Não houve instalação ou alteração de software. `/deepresearch` indisponível; fallback de busca/leitura primária e PDFs com localizadores, sem alegar operação daquela ferramenta.

Bruto em `data/raw/cvm-linkage-20261012/a/`: `capture-index.json`, SHA256 `48d6bf5566a07cf29275ccc6cd5bc72e455b34ba2be72563582700fd4429f36c`. O índice aponta nome de manifest,URL,UTC,status,resultado,tamanho e hash de cada corpo; cada manifest aponta corpo e cabeçalhos/diagnóstico preservados em arquivo adjacente. Respostas502 do IF.data atual/2024/legado são falhas, não documentos de apoio. O índiceprivado `verified-inventory.json` contém também hash de todos manifests e nomes exatos dos corpos; não publicar headers/cookies incidentais.

| Recurso / label no índice | HTTP | Bytes | SHA256 corpo |
| --- | ---: | ---: | --- |
| bcb-supervised-catalog | 200 | 41382 | `a4c0ee4a517774eacb7bbf60b3b6083870488f96678a5d4a3f93063322cf028c` |
| ifdata-2024-methodology | 502 | 5015 | `34e426d2a8f30663be4d50cbeec9c100fdf5df8488c97e6041e21fcad55e287f` |
| ifdata-current-methodology | 502 | 5015 | `34e426d2a8f30663be4d50cbeec9c100fdf5df8488c97e6041e21fcad55e287f` |
| ifdata-catalog | 200 | 37566 | `baa8a39d1d3a60a8f1352e3bc353847b92860b4c4a085f477675e5d11ef744df` |
| ifdata-methodology-pdf | 200 | 72209 | `c83577a710a57d147c8f10d043db111a63d31cf8cd8a7a9b58a08f8733d70896` |
| bcbase-doc | 200 | 32640 | `d739cd8db6e85bd8e964cb1a99f19ebb6923dcba4418bbb754724382564724e1` |
| ifdata-doc | 200 | 20102 | `72736b41ccf4c496a62e5cc98aeea25d6497b9bf0fcb97df05e845a54f518529` |
| rfb-layout | 200 | 59315 | `0a52d6bdfb61a07425e352a0e692932306a5ec9ecad682f5f9e28059e1a5fce0` |
| rfb-note47 | 200 | 197508 | `a317abd377881b97fb7c93078a02c591229f71544d9416d9729fa0da9938d498` |
| ifdata-legacy | 502 | 5015 | `34e426d2a8f30663be4d50cbeec9c100fdf5df8488c97e6041e21fcad55e287f` |
| bcb-circular3500 | 200 | 41605 | `af7ae26ee9c034857bff36d1905f870927906f8d3750983a32501f6c536afbdf` |
| bcbase-cases-2010 | 400 | 103 | `c7bac45072c486cb6424e7b28844d03741bb3bbddd580a4b3725f6b75b5014c6` |
| bcbase-cases-2024 | 400 | 103 | `c7bac45072c486cb6424e7b28844d03741bb3bbddd580a4b3725f6b75b5014c6` |
| bcbase-cases-parentheses-2010 | 400 | 64 | `a2320872c4b0a3f0edfd291515fd21a68ce2d5359c9f5a0e16fa9675be6c11d3` |
| bcbase-cases-parentheses-2024 | 400 | 64 | `a2320872c4b0a3f0edfd291515fd21a68ce2d5359c9f5a0e16fa9675be6c11d3` |
| bcbase-cases-odata-2010 | 200 | 1374 | `1b0d963ee59949d7526b0091d2624b47ad53f8de355831aa760f2aa639db089b` |
| bcbase-cases-odata-2024 | 200 | 1374 | `3d94b1ee773f1365ebf8c958629d20b41faacf3520a964ddfa87913d7c4a1b54` |

Verificação realizada: recomputação SHA256/tamanho de17corpos e seus manifests; autenticação de dois JSON e doisParquet contra manifest prévio; comparação das17linhasCSV selecionadas com JSONoriginais; CAD contra manifest102; respostasBCBase quatro raízes,semnextLink,datasretornadas; leitura e mapa completo dos quatroPDFs de apoio. Isto é conferência do autor para handoff, não revisão independente.

Evidência privada em `.scratch/cvm-linkage-20261012/a/`: `authenticated-case-rows.json`, `cadastro-cases.json`, `reused-evidence.json`, `verified-inventory.json`, `ifdata-doc-spec.json`, `bcbase-doc-spec.json`, `pdf-reading-notes.md`. Nenhum teste de software se aplica à fatia documental. Próximo gate: revisão independente desta cadeia e definição pelo integrador do contrato de vínculos, antes de mudanças no validador ou vínculosaceitos.

# Tipos institucionais IF.data e limites históricos — 2010–2024

Pesquisa B da [Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108), contrato de 2026-10-12. Base de revisão `f93d37f17898d69713d06f07bb393eb1f2444331`, branch `codex/cvm-b3-history-2010-2024`. Resultado documental local, sujeito a revisão independente; não define amostra, indicadores ou método da monografia. Impacto arquitetural: uma nota no destino existente `docs/engineering/`; evidência operacional privada em `.scratch/cvm-b3-history-20261012/b/`, sem código público ou alteração de dados aceitos.

## Conclusão para o contrato histórico

O cadastro oferece classificações complementares, não um único “setor financeiro”. `SegmentoTb` descreve o tipo institucional com mais detalhe; `Tcb` agrupa tipos e também classifica conglomerados; `Atividade` descreve atuação com mudanças de metodologia; `Sr` é segmentação prudencial; `Tc` é controle; `Td` distingue registros individuais e de conglomerados, com uma descrição abreviada na API que não basta para provar independência. Líder e unidade consolidada precisam de atributos separados. Nenhum desses campos comprova listagem B3 ou registro CVM.

Há 60 respostas trimestrais de 201003 a 202412 no pacote aceito, totalizando **303.792 linhas de instituição/data consultada**, incluindo inativas e conglomerados. Isso não equivale a 303.792 instituições, nem a uma população trimestral de instituições em funcionamento. A documentação corrente não dá vigência histórica a todos os códigos: há valores não enumerados, sinais de revisões metodológicas e cadastros cuja presença na resposta não prova autorização contemporânea. A relação histórica deve preservar o literal, a data consultada e a data de recuperação, com lacuna explícita sobre vigência quando não houver prova.

## Fontes e método de leitura

Foram aplicadas as instruções locais Feynman `deep-research` e `pdf-explore`, com o fallback autorizado de fontes primárias e extração local. `/deepresearch` não está disponível e não foi executado. PDFs foram mapeados por página, com leitura cruzada das definições, notas de perímetro e disposições temporais; nenhuma conclusão abaixo depende somente de resumo de busca. As fontes são BCB, inclusive o texto CMN publicado pelo BCB. Não se usaram classificações inferidas de nomes nem tabelas secundárias como de-para.

| ID | Fonte primária e localizador efetivamente lido | Limite temporal |
|---|---|---|
| D1 | [Olinda IFDATA v1, documentação](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao), recurso `IfDataCadastro`, `propriedades` de cada campo; corpo reutilizado da Issue 105 e autenticado | Documentação recuperada em 2026; versão v1 não é um codebook histórico datado |
| D2 | [IFData — Esclarecimentos e Metodologia](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf), duas páginas: tabela de relatórios e notas 1–4 na p. 2; corpo reutilizado da Issue 105 | Declara marcos de cobertura/perímetro; não enumera todos os campos cadastrais |
| D3 | [Resolução 4.553/2017, texto original](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50335/Res_4553_v1_O.pdf), cinco páginas, arts. 1–11 | Texto original, não consolidação de todas as alterações posteriores |
| D4 | [REF abril/2017, seção 2.5](https://www.bcb.gov.br/content/publicacoes/ref/201704/RELESTAB201704-refSegmentacaoSFN.pdf), três páginas físicas = pp. impressas 52–54; especialmente p. 53, tabela 2.5.1 e nota 72 | Explicação contemporânea da criação da segmentação; tabela inicial usa parâmetros de junho/2016 |
| D5 | [SCR.data — Metodologia](https://www.bcb.gov.br/content/estabilidadefinanceira/scr/scr.data/scr_data_metodologia.pdf), oito páginas; seção 4(a–b), pp. físicas 4–5 | Corrobora nomenclatura TCB/SR em outra publicação BCB; não certifica retrospectivamente o cadastro IF.data |
| D6 | [REF abril/2025](https://www.bcb.gov.br/content/publicacoes/ref/202504/RELESTAB202504-refPub.pdf), 109 páginas, glossário p. física/impressa 93, entradas B1/B2; PDF reutilizado da Issue 102 | Explica classificação de conglomerados em 2025; não fixa vigência de cada regra em 2010–2024 |
| L1 | Pacote local aceito `data/curated/ifdata-cadastro-20261011/manifest.json`, contrato `ifdata-cadastro-parquet-v1`; 106 partes/512.959 linhas no pacote total. Recorte de 60 partes/303.792 linhas nesta nota | Capturado em 2026-10-11, não arquivado contemporaneamente em cada trimestre |

`open_cadastro` autenticou todas as 106 partes e a unicidade `(CodInst, Data)`; também foram autenticados os 60 JSONs de origem contra `source_sha256` no manifest, conferindo suas contagens. Não foi feita nova consulta de valores financeiros. O recorte filtra `Data` entre 201003 e 202412 e meses 03/06/09/12, sem filtro de instituição, situação ou perspectiva. As contagens incluem repetições temporais. Extremos: 4.588 linhas em 201003 e 5.744 em 202412. Distribuições por trimestre, domínios completos, exemplos e pins ficam privados para revisão; não constituem um novo dataset aceito.

## Campos: significado comprovado e uso permitido pela evidência

| Campo | Significado oficial | Observado no recorte e cautela |
|---|---|---|
| `Tcb` | Tipo de consolidado bancário; D1 enumera B1, B2, B3S, B3C, B4, N1, N2, N4 | Dez literais observados, incluindo B3 e N3 não enumerados em D1. É classificação do registro consultado, individual ou agregado; não copiar do líder |
| `Td` | D1 descreve I como instituição independente e C como conglomerado | I/C em todos os 60 trimestres; **49.419 linhas I têm código financeiro e/ou prudencial preenchido**. Portanto a descrição “independente” não é predicado suficiente. Participação deve ser lida nos campos próprios |
| `Tc` | Controle: 1 público, 2 privado nacional, 3 privado com controle estrangeiro | Três literais em todos os trimestres. Não é atividade econômica, tipo societário, elegibilidade de capital aberto nem identidade do controlador |
| `SegmentoTb` | Segmento de atuação da instituição; D1 não fornece enumeração nem critérios | 30 textos não nulos; 26.091 nulos. Inclui Banco Comercial, Banco Múltiplo, Sociedade Corretora de TVM, Sociedade Distribuidora de TVM, Cooperativa de Crédito, tipos de pagamento e crédito. Esses textos vêm do campo nativo, não da leitura do nome |
| `Atividade` | Atividade da instituição; D1 não enumera nem explica algoritmo | 60 textos não nulos; 194.725 nulos. Há classificações de crédito, atacado/varejo, tesouraria, serviços, IP e CTVM/DTVM, com coexistência de versões. Não equiparar a CNAE ou carteira autorizada |
| `Sr` | Segmento da Resolução 4.553/2017, S1–S5 | Cinco códigos não nulos; 271.635 nulos. Classifica regulação proporcional por porte/atividade internacional/perfil; não mede especialização financeira. Ausência não implica S5 |
| `Situacao` | D1 enumera A em atividade e I inativa | Também F, LE e LO. Sem definição oficial desses três no material lido, manter desconhecido; não expandir siglas por plausibilidade. Não usar a presença na resposta como prova de atividade |
| `CnpjInstituicaoLider` | D1: CNPJ da instituição líder do conglomerado prudencial/financeiro | Referência nominal/cadastral do líder; não tipo do grupo, composição completa, controlador CVM ou estabelecimento completo de 14 dígitos. Na base aceita há identificadores de oito caracteres; preservar namespace e largura |
| `CodConglomeradoFinanceiro`, `CodConglomeradoPrudencial` | D1: códigos dos conglomerados dos quais a instituição participa | São dois vínculos diferentes. O campo singular de líder não esclarece sozinho a associação quando ambos existem. Não fundir perspectivas ou assumir liderança idêntica |
| `Data`, `DataInicioAtividade` | Data consultada em AAAAMM e início de atividade cadastrado | Início não é início de validade de Tcb/Atividade/Sr. Valores como 180001 exigem semântica própria; não corrigir por hipótese |

### De-para oficial disponível para Tcb

O quadro descreve **D1 na captura atual**, corroborado em nomenclatura por D5, seção 4(a). Não declara que o rótulo era vigente durante todos os trimestres em que o código aparece.

| Literal observado | Definição em D1 | Linhas / trimestres observados / limites |
|---|---|---|
| B1 | Banco comercial, múltiplo com carteira comercial ou caixa econômica | 25.517 / 60 / 201003–202412 |
| B2 | Múltiplo sem carteira comercial, banco de câmbio ou investimento | 12.320 / 60 / 201003–202412 |
| B3S | Cooperativa de crédito singular | 139.540 / 60 / 201003–202412 |
| B3C | Central e confederação de cooperativas de crédito | 2.903 / 60 / 201003–202412 |
| B4 | Banco de desenvolvimento | 896 / 60 / 201003–202412 |
| N1 | Não bancário de crédito | 38.050 / 60 / 201003–202412 |
| N2 | Não bancário do mercado de capitais | 77.652 / 60 / 201003–202412 |
| N4 | Instituições de pagamento | 5.528 / 60 / 201003–202412; vigência retrospectiva não demonstrada |
| B3 | **Não enumerado em D1** | Uma linha em 201012; CodInst 13081722, SegmentoTb Cooperativa de Crédito. Coocorrência não autoriza converter para B3S |
| N3 | **Não enumerado em D1** | 1.385 / 44 / 201403–202412. Coocorre com SegmentoTb Administradora de Consórcio; associação observada, sem promover a de-para normativo |

D1 usa caixa inconsistente na descrição (por exemplo b1/n2), enquanto os dados usam os literais acima; a nota transcreve a nomenclatura sem modificar os dados. D5 agrupa B1/B2/B4 como bancário, N1/N2/N4 como não bancário e B3S/B3C como cooperativas, **no contexto SCR.data**. Esse agrupamento é uma alternativa oficial documentada, não uma regra de elegibilidade acadêmica ou certificação histórica IF.data.

### Perímetro e liderança

D2 distingue instituição individual com personalidade jurídica própria, conglomerado financeiro e conglomerado prudencial. O prudencial alcança também entidades de pagamentos, consórcios, aquisição de crédito/recebíveis, participações exclusivas e certos fundos; logo pode conter atividades heterogêneas. A nota de D2 informa mudança a partir de 2018 para independentes, incluindo a entidade no país e dependências no exterior. Cobertura disponível não prova equivalência entre os perímetros. A tabela de D2 inicia o contábil prudencial em 201403 e o capital prudencial em 201503, enquanto o financeiro contábil começa em 200003.

D6 explicita que B1 pode designar um conglomerado que contenha ao menos uma instituição dos tipos bancários B1; B2 também possui regra de composição/exclusão. Essa definição explica por que tipo do conglomerado e do líder são dimensões diferentes, sem demonstrar sua vigência completa desde 2010.

Exemplos exclusivamente cadastrais, ligados por identificador e mesma data, sem inferência pelo nome:

| Data | Registro agregado / Tcb | Líder declarado / Tcb individual |
|---|---|---|
| 201003 | C0051293 / B1 | 60770336 / B2 |
| 201003 | C0051341 / N1 | 00806535 / N2 |

É incorreto substituir Tcb do grupo pelo do líder. A consulta exploratória encontrou 11.267 pares registro/líder com Tcb diferente, incluindo membros individuais; essa contagem não é de conglomerados únicos nem de erro de cadastro. Os exemplos acima restringem explicitamente `Td=C`.

## Marcos temporais: documentação versus observação

| Marco | Evidência documental | O que os 60 trimestres mostram / limite |
|---|---|---|
| 2014–2015 | D2: início de coberturas prudenciais contábil/capital distintos | N3 e segmento de IP não sujeita a autorização aparecem desde 201403; isso não determina início legal dessas categorias |
| 2016–2017, atividade | Não foi localizado neste recorte o documento oficial com critérios e transição completa de `Atividade` | Sete literais mencionam “metodologia até dez/2016”; seis terminam em 201612. `Não-Classificado - metodologia até dez/2016` persiste até 202012. Novos rótulos como Crédito Atacado/Varejo, Tesouraria e Negócios e Complexo aparecem em 201703. Não criar equivalência automática entre versões |
| 2017, prudencial | D3 art. 11 entra em vigor na publicação; DOU de 31/1/2017 indicado na p. 5. D4 pp. 52–54 explica finalidade, enquadramento e exclusões | S4 aparece em 201703; S1/S2/S3 em 201706; S5 apenas em 201812. Essas primeiras observações não são datas normativas de criação dos segmentos |
| 2018, atividade | Critérios completos não localizados | Rótulos `CTVM DTVM - ...` aparecem desde 201803, enquanto rótulos genéricos como Bolsa/Outros continuam até 201912; coexistência impede troca universal em uma única data |
| 2018–2019, novos tipos | Sem fechar nesta pesquisa a cadeia de normas/autorização de cada entidade | SegmentoTb Sociedade de Crédito Direto desde 201812 e Sociedade de Empréstimo entre Pessoas desde 201906; primeiras observações não substituem normas nem datas de autorização |
| 2010–2024, N4 | D1 corrente diz IP, sem vigência retroativa | Há 12 registros N4 em 201003, todos com SegmentoTb e Atividade nulos e Situacao I. Ex.: CodInst 01027058. Não certifica que já eram IP autorizadas na data. Entre todas as linhas N4, 2.630 têm SegmentoTb nulo |

O texto original D3 associa enquadramento de membros a informações consolidadas (art. 2º §6º), estabelece critérios quantitativos, prazos de mudança e poderes do BCB (arts. 3–8), e usa junho/2016 para o enquadramento inicial divulgado em 2017 (art. 10). Assim, `Sr` não pode ser reconstruído apenas aplicando um corte de ativo no trimestre. D4 apresenta S5 no enquadramento inicial apesar de a primeira ocorrência desse literal no pacote ser 201812. Nenhuma norma foi usada aqui para recalcular o campo. Alterações posteriores de D3 não foram inventariadas integralmente; o corte 2024 deve exigir versões normativas pertinentes antes de qualquer derivação.

Há **87 mudanças observadas de Tcb entre trimestres consecutivos do mesmo CodInst**; não houve salto de referência nesses 87 pares. Incluem B2→B1, N1→B2 e N4→N1, entre outros. Podem refletir eventos institucionais, revisão cadastral ou regra de classificação; esta contagem não escolhe a causa. Uma classificação fixa pelo último trimestre apagaria essas mudanças.

### Cuidado adicional com vintage e situação

`Situacao` tem 126.324 A, 171.473 I, 2.638 F, 1.385 LE e 1.972 LO no recorte. A documentação de D2 descreve relatórios de instituições em operação normal, mas o **recurso cadastral** contém registros inativos e administradoras de consórcio (N3), inclusive quando D2 diz não disponibilizar informações sobre essas administradoras. Portanto não estender a descrição de disponibilidade dos relatórios para afirmar que todo registro cadastral tem demonstrações ou integra a população ativa.

Em 201003 há registros A cujo `DataInicioAtividade` chega a 201004. Isso exige esclarecimento da semântica temporal, sem concluir erro ou aplicar exclusão por conta própria. A captura de 2026 de uma resposta parametrizada por 201003 não prova uma fotografia imutável publicada em março/2010. Para provar autorização, atividade, nome e classificação vigentes naquele instante, pode ser necessário ato/datamento oficial complementar. Preservar essa incerteza na relação histórica e evitar transformar `Situacao != A` em inexistência da instituição.

## Proposta de esquema e próximos checks — ainda não implementados

Recomenda-se uma dimensão de **observação cadastral**, chave nativa `(CodInst, Data)`, mantendo todos os literais, nulls, nomes e vínculos, com fonte/hash, recuperação UTC e namespace do identificador. Separadamente, um dicionário versionado por campo/código/fonte/localizador deve registrar o significado comprovado, a vigência documental conhecida e o estado `não demonstrada` quando faltar. `primeira/última observação` deve permanecer diferente de `início/fim de vigência`.

Tipo individual, Tcb do agregado, tipo individual do líder, Atividade, Tc e Sr devem permanecer colunas distintas, com perspectiva financeira/prudencial explícita nos vínculos. Atributos de líder não devem preencher atributos ausentes do grupo. O campo singular de líder requer regra de resolução documentada ou estado ambíguo quando as perspectivas não forem desambiguadas. Não usar preenchimento retrospectivo/prospectivo, voto majoritário entre trimestres, normalização silenciosa de B3 ou inferência por nomes.

Para a discussão de indicadores da Issue 3, as dimensões permitem **preparar alternativas**: bancos de depósito/crédito, especialistas de crédito, intermediários de mercado/serviços, cooperativas, pagamentos e agregados diversificados. Essa lista é sugestão de organização da pesquisa, não de-para aprovado. Em especial, N2 não define um único modelo de receita, Banco Múltiplo não discrimina sozinho a carteira comercial, e uma holding emissora CVM não recebe automaticamente o tipo da operadora IF.data. Aplicabilidade dos indicadores exige componentes, janelas e perímetro próprios, além de decisão de João/orientador.

Lacunas para o próximo checkpoint:

1. Obter codebooks oficiais históricos para B3/N3, F/LE/LO e critérios completos de SegmentoTb/Atividade, incluindo revisões de 2017/2018 e exceções remanescentes.
2. Esclarecer se cada atributo do cadastro é histórico ou retrospectivamente atualizado, começando pelos exemplos N4/201003 e início de atividade posterior à referência. Não exigir inexistência de revisão como pressuposto silencioso.
3. Separar população cadastral de disponibilidade de relatórios e autorização vigente; cruzamento de metadados não é admissão financeira.
4. Completar normas de segmentação pertinentes até 2024 e a semântica do líder por perspectiva se houver uso analítico desses campos.
5. Levar à Issue 3 a decisão sobre grupos comparáveis, holdings, conglomerados, entradas/saídas e elegibilidade; a presente pesquisa não efetua essa adoção.

## Proveniência e verificação do checkpoint

Fontes reutilizadas, sem novo GET: D1 SHA-256 `72736b41ccf4c496a62e5cc98aeea25d6497b9bf0fcb97df05e845a54f518529`, 20.102 bytes, HTTP 200, recuperação 2026-10-12T23:58:48.036046Z; D2 `c83577a710a57d147c8f10d043db111a63d31cf8cd8a7a9b58a08f8733d70896`, 72.209 bytes, HTTP 200, 2026-10-12T23:58:47.469873Z; D6 `a4e8b6488ea2d484ea4a98e2f620e2df66ec70e26c47f1000df01e28217077ec`, HTTP 200, 2026-10-12T17:24:52.975267Z. D1/D2 corpos e manifests em `data/raw/cvm-linkage-20261012/a/`; D6 PDF/proveniência em `.scratch/cvm-front-20261012/b1/`. Pins foram reconferidos; os destinos originais não foram alterados.

Novas capturas documentais privadas, sequenciais, timeout 30s, sem retry automático, HTTP 200:

| Fonte | Recuperação UTC | Bytes | SHA-256 |
|---|---|---|---|
| D3 | 2026-10-13T01:18:45.129214Z | 185.832 | `54f11213c83f09015248fb6d64a770c4d64d9449255f4d854a5e37fed175d236` |
| D4 | 2026-10-13T01:18:45.495302Z | 686.252 | `4bdd19ff6271b94760cb9322368f090dbcc70184964e4800f6371f71f0519293` |
| D5 | 2026-10-13T01:18:46.721066Z | 550.671 | `5b9f3ec6635e4ba973ce248343f86e7ede8c597675ce69a6825a1aace52c044d` |

O endereço antigo de download de D3, retornado pela busca BCB, falhou no leitor web com 404; não foi aceito como corpo. O endereço oficial `normativos.bcb.gov.br` acima forneceu o original legível. `source-provenance.json` guarda URLs, HTTP, headers sem cookies, hashes e UTC das capturas privadas; extrações `*-pages.json` conservam páginas completas para revisão cruzada.

Manifest L1 SHA-256 `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1`. JSON 201003 `0e212b6a73f839aab5869a667a7ce223f6bdc3d9ac654279f3f9d6941a94659c`; JSON 202412 `9b5ee21a572fbdbc8de6e5071fb7986b024292691edc42530b9a6ee36560436e`. Os 60 pins completos estão em `cadastro-pins.json` privado. Leituras usaram ambientes Python já existentes, sem instalação. Scripts privados `research.py`, `sources.py`, `distributions.py`, `examples.py` e `pins.py` permitem reproduzir inspeções. Não foram executados testes de software: esta fatia altera somente documentação; os checks pertinentes são autenticação, contagens, leitura das fontes, coerência de localizadores e inventário da allowlist. Revisão independente e integração são etapas seguintes, sem claim de aprovação ou estado remoto alterado.

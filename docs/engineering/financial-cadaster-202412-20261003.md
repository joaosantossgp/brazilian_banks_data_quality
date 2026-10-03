# Cadastro financeiro IF.data 202412: evidência e limites

## Resultado e escopo

Na [Issue 21](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/21), foi adquirido e validado o arquivo oficial `cadastro202412_1005.json`, anunciado para **Conglomerados Financeiros e Instituições Independentes**, referência **202412**. O corpo contém **1.422 registros cadastrais**, com identificadores brutos únicos e não vazios e 38 campos string por registro. Essa contagem descreve o arquivo adquirido; não é uma contagem validada de bancos, unidades analíticas, linhas observadas do Resumo 92 ou entidades com valores disponíveis. [O/C5; localizadores e conferência abaixo]

A aquisição desta entrega foi restrita a dois GETs: catálogo histórico e cadastro financeiro anunciado, ambos HTTP 200, sem retry. Nenhum arquivo numérico, outro período ou perspectiva foi adquirido. A base de revisão é `effe4964f9bfcbcba3bc8905d4dd08b5b22bceae`, branch `codex/financial-cadaster-202412`; a única alteração pública desta pesquisa é esta nota, no destino existente `docs/engineering/`. Fontes e auditoria permanecem locais, nos destinos novos ignorados previstos na Issue. O domínio segue a [arquitetura](../architecture.md) e o [glossário](../../GLOSSARY.md).

## Fontes primárias e proveniência

Os localizadores JSON são pointers no corpo original, sem reordenar arrays. Para HTML, os offsets são bytes UTF-8, zero-based. Os sete corpos foram lidos por `bank_quality.archive.load_body`, que verifica SHA-256, e seus tamanhos foram conferidos. Todos têm `http_status=200`, `outcome=ok`, `truncated=false` e diagnósticos vazios. Os manifests conservam URL final, método, parâmetros, recuperação UTC e headers; esta nota publica somente proveniência científica mínima, sem cookies ou headers de sessão.

| Fonte oficial | Recuperação UTC | Bytes | SHA-256 |
|---|---|---:|---|
| [O: catálogo 2000–2024, novo](https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024) | 2026-10-03T20:42:19.737446+00:00 | 13527657 | `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` |
| [C5: cadastro 202412/1005](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Fcadastro202412_1005.json) | 2026-10-03T20:42:20.380990+00:00 | 739235 | `eec996cd9b6b219d26a7e63a1b803273ad0a418c6e022b06506f3a226b9c98e1` |
| [O anterior: mesmo catálogo](https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024) | 2026-10-01T01:30:04.206286+00:00 | 13527657 | `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` |
| [D: dicionário info202412](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Finfo202412.json) | 2026-10-01T01:32:36.021567+00:00 | 188690 | `9c09219eeb7aa558e0ac74e32b905ba940ec00b0bc01f761b1d086aef86cca28` |
| [P: portal index.html](https://www3.bcb.gov.br/ifdata/index.html) | 2026-10-01T01:27:56.936588+00:00 | 92483 | `234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153` |
| [P24: portal index2024.html](https://www3.bcb.gov.br/ifdata/index2024.html) | 2026-10-01T01:28:20.707297+00:00 | 86647 | `bd8936773c7f54933cd428d918671bed7f767060618021540b6488671c3780f1` |
| [C6: cadastro 202412/1006](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Fcadastro202412_1006.json) | 2026-10-01T01:32:35.145451+00:00 | 824810 | `5200301d6dabad5240b2d65aada6cb2179d75d497999c9b08d6c011a74043685` |

Manifests novos em `data/raw/financial-cadaster-202412-20261003/`:

- O: `20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json`.
- C5: `20261003T204219927653Z_cadaster_202412_1005_7b7b18e295244083817afa94960b883a.json`.

Manifests preservados em `data/raw/discovery-20261001/`:

- O anterior: `20261001T012952763821Z_portal_catalog_retry_1e8743faa0be4262b5c2b64c02dad2f7.json`.
- D: `20261001T013235163159Z_portal_info_202412_4b180f95c53d44d4b5f3a4444c586e20.json`.
- P: `20261001T012756759142Z_portal_56229187f15948a0a353b4b194b7cb3f.json`.
- P24: `20261001T012820520704Z_portal2024_8d85bdfd34dc4e81b52a360e00439840.json`.
- C6: `20261001T013234426740Z_portal_cadastro_202412_c363a9e39165404aa08831eaa26dd2f5.json`.

Cada manifesto indica seu `body_path`. O índice e a auditoria sanitizada estão em `data/runs/financial-cadaster-202412-20261003/acquisition.json` e `cadaster-audit.json`. Esses arquivos e os corpos/manifests permanecem em destinos ignorados e não foram publicados. A inspeção anterior encontrou 123 manifests e nenhum com a perspectiva 1005 em seus metadados; esta entrega acrescentou os dois manifests acima.

## Associação de referência, perspectiva e relatório

| Fato diretamente observado em O | Pointer | Valor |
|---|---|---|
| Referência | `/99/dt` | `202412` |
| Cadastro financeiro | `/99/files/0/f` | `ifdata/202412/cadastro202412_1005.json` |
| Cadastro individual separado | `/99/files/1/f` | `ifdata/202412/cadastro202412_1006.json` |
| Seletor financeiro | `/99/files/10/sel/1` | `id=1005`, nome Conglomerados Financeiros e Instituições Independentes, `di=200001`, `df=207901` |
| Resumo financeiro | `/99/files/28/trel` | `id=92`, `n=Resumo`, `s=[{"id":1005}]`, 17 colunas |
| Texto de geração do relatório | `/99/files/28/trel/ge` | `15/04/2026` |
| Filtro de construção do relatório | `/99/files/28/trel/fx` | string vazia |

Em P/P24, `selectRelatorio` constrói o nome esperado com referência e seletor e requisita o `f` anunciado por GET em `rest/arquivos?nomeArquivo=...`. Localizadores P/P24: `expectedCadastroFileName`, bytes **11642/11644**; expressão HTTP `urlArquivos + "?nomeArquivo=" + cadastroFile.f`, **14962/14964**. A referência também é confirmada pelo campo `c1` de todos os registros C5. A perspectiva vem da associação explícita do catálogo e da URL/parâmetro solicitado; `c4=C` isoladamente não prova perspectiva financeira.

## Campos, schema e identificadores

P/P24, `getValueFromIfd`, bytes **17354/17356**, lê `cad["c"+ifd.lid]` quando `td=1`. Os seguintes conceitos cadastrais foram localizados em D:

| Campo | Conceito oficial / ID | Pointer D |
|---|---|---|
| `c0` | Código: Conglomerado ou CNPJ / 79706 | `/593` |
| `c1` | Data-base / 79678 | `/565` |
| `c2` | Nome da instituição / 79670 | `/557` |
| `c3` | TCB, classificação interna / 79671 | `/558` |
| `c4` | TD, I independente / C conglomerado / 79675 | `/562` |
| `c8` | Segmento / 79677 | `/564` |
| `c14` | Código do conglomerado financeiro / 79702 | `/589` |
| `c15` | Código do conglomerado prudencial / 79703 | `/590` |
| `c23` | Conglomerado financeiro / 79713 | `/600` |
| `c22` | Conglomerado prudencial / 79728 | `/615` |

D foi adquirido com contexto de seleção individual 1006; o próprio catálogo anuncia o mesmo `info202412.json` para a referência, e as colunas de Resumo 92 ligam os conceitos acima. Esse uso documental não altera o contexto de aquisição de D nem prova vintage cadastral idêntico.

A conferência de C5 cobre o array inteiro, pointers `/0` a `/1421`: exatamente 38 chaves `c0..c37`, presentes em todos os registros e com valores string. `c0`: 1.422 únicos, nenhum vazio, duplicado ou espaço de padding; `c1`: 1.422 ocorrências de `202412`. Os strings originais e seus estados foram preservados. Não foram preenchidos vazios nem reinterpretados como zero/NA/NI; os tokens zero observados em outros campos permanecem distintos de vazio.

O namespace operacional desta nota é **código bruto do arquivo cadastro202412_1005**, separado do cadastro1006 e de CNPJ, código OData, emissor/holding e código apresentado. A coluna Código do Resumo 92 possui `nac` que subtrai 200000000 dos códigos na faixa 200000000–299999999, em O `/99/files/28/trel/c/1/nac`; seus flags `na=true`, `nc=true` indicam transformação e ocultação visual. Os `c0` de C5 têm de cinco a oito caracteres, portanto nenhum cai nessa faixa de nove dígitos. Isso não estabelece que o código seja CNPJ completo nem torna a transformação dispensável em futuros corpos.

Para eventual acesso numérico, P/P24 usa `cad.c0` com `info.a` e `info.lid`, via `findBinDataByEntInf`; a identidade fonte deve acompanhar essa associação. Nenhuma equivalência entre observações monetárias das perspectivas foi testada ou assumida nesta entrega.

## Cadastro adquirido e população do Resumo

C5 apresenta TD `C=195`, `I=1225` e vazio `=2`; C6 contém `C=357`, `I=1226` e vazio `=2`, apesar de ser o cadastro individual. Esses fatos impedem usar TD sozinho como prova do arquivo selecionado ou como contagem de conglomerados financeiros. C5 também apresenta 146 registros `c3=n4`, todos com `c8=41`. D `/558` descreve `n4` como instituições de pagamento, e `/564` descreve 41 da mesma forma.

P, metodologia “Formas de Consolidação”, item 3, byte **67652**, define o conglomerado financeiro como subgrupo das entidades do prudencial autorizadas pelo BCB, consolidado como uma entidade, além das instituições independentes; descreve exclusão de instituições de pagamento e administradoras de consórcio do conglomerado financeiro. O texto não oferece uma regra suficiente para excluir automaticamente os 146 registros n4 deste cadastro. Sua presença exige qualificação do universo e do tratamento futuro; não foi corrigida por filtro silencioso. A metodologia foi recuperada em 2026 e não comprova cada perímetro histórico em 202412.

Os dois registros com `c8="42"` ficam sem interpretação: D `/564` não enumera 42. O campo `c9` está preenchido em 1.023 registros e vazio em 399, mas não foi localizado conceito `td=1/lid=9` em D; não lhe atribuir semântica por posição, nome parecido ou conteúdo. Os dois TD vazios permanecem desconhecidos.

Em P/P24, `mountData`, bytes **19834/19836**, percorre `selCadastro` e cria uma linha por registro que não tenha sido rejeitado por `trel.fx`. Para Resumo 92, `fx` está vazio; nesse estágio não há exclusão automática por `c8`, `c9`, n4 ou ausência de uma observação numérica. O ramo numérico de `getValueFromIfd` pode devolver `NI` quando não encontra a célula. Posteriormente, filtros escolhidos na interface podem ocultar linhas: `applyFiltrosAtivos`, bytes **57692/57888**. `updateIfCompleted` exige cadastro, dicionário e todos os shards esperados antes de construir a tabela.

Assim, C5 é uma entrada cadastral para a construção, não prova de 1.422 linhas financeiras efetivamente carregadas/renderizadas nem de observações disponíveis. Não foi executado o portal financeiro ou validado seu conjunto numérico neste recorte; filtros, agregações e NI de apresentação não constituem comprovação de cobertura monetária.

## Comparação restrita com o cadastro individual

A comparação utiliza igualdade exata de strings `c0` de C5/C6, sem converter os identificadores em números:

| Relação entre os corpos | Registros |
|---|---:|
| C5 | 1422 |
| C6 | 1585 |
| IDs brutos compartilhados | 1352 |
| Somente C5 | 70 |
| Somente C6 | 233 |

As 1.352 linhas compartilhadas são idênticas em todos os 38 campos. As 70 exclusivas de C5 têm `c4=C` e `c8` nos segmentos 196–199 descritos em D `/564`; os 233 registros exclusivos de C6 têm `c14` preenchido. O conjunto de códigos `c14` desses registros não é literalmente igual ao conjunto `c0` exclusivo de C5: a representação contém zeros à esquerda. A diferença de representação deve ser preservada; não autoriza juntar namespaces automaticamente, comprovar identidade legal ou composição de conglomerados, nem substituir o cadastro financeiro pelo individual.

### Conferência offline reproduzível

O procedimento abaixo requer os corpos e manifests locais listados para C5/C6; sem esses arquivos, os links oficiais permitem consultar a fonte, mas uma nova recuperação não reproduz necessariamente os hashes desta entrega. Não depende dos helpers privados:

1. Na raiz do checkout, usar o Python local e importar `json`, `pathlib.Path` e `bank_quality.archive.load_body`. Para cada C5/C6, ler seu manifesto com `json.loads(path.read_text(encoding="utf-8"))` e executar `body = load_body(manifest, path.parent)`. Exigir `len(body) == manifest["bytes"]`, SHA da tabela, HTTP 200, `outcome="ok"`, `truncated=false` e diagnósticos vazios.
2. Interpretar cada corpo com `json.loads(body)`, exigir array não vazio e conferir todas as linhas: chaves exatamente `{f"c{i}" for i in range(38)}`, todos os valores string, `c1 == "202412"`, `c0` não vazio e igual a `c0.strip()`. Exigir `len({row["c0"] for row in rows}) == len(rows)`; para C5/C6, respectivamente 1.422/1.585 registros.
3. Construir dois mapas por `c0` string, sem conversão numérica, e comparar seus conjuntos: interseção 1.352, diferença C5−C6 70, diferença C6−C5 233. Exigir igualdade integral dos dois dicionários de linha para cada ID compartilhado. Contar `c4`/`c3` e estados vazios diretamente nas strings originais; os resultados esperados de C5 estão acima.
4. Para as afirmações documentais, repetir `load_body` nos demais manifests da tabela, conferir tamanho/SHA e localizar os pointers e funções/offsets indicados nesta nota. Igualdade cadastral e passagem nesses checks não verificam as observações numéricas do Resumo.

## Vintage, aceite e trabalho remanescente

O catálogo novo é byte a byte idêntico ao anterior pelo SHA-256 e tamanho. C5 foi recuperado em outubro de 2026 para referência dezembro de 2024. Seu corpo cadastral não contém `ge` ou outro campo explícito de geração: os 38 campos observados são `c0..c37`. O `ge=15/04/2026` e `v="1"` pertencem ao metadado do relatório 92, não foram transferidos ao cadastro como data de geração. GETs separados e hashes iguais do catálogo não garantem atomicidade entre cadastro, dicionário e shards numéricos ou primeira publicação histórica.

**Aceite local cadastral atendido:** arquivo anunciado e solicitado para referência/perspectiva corretas; respostas íntegras; schema, strings, chaves, datas-base, unicidade e estados conferidos; comparação opaca com C6 e ambiguidades explícitas. A auditoria local concluiu com exit 0; esta nota foi conferida contra os corpos primários. Isso não afirma revisão independente aprovada, publicação ou integração, que têm evidência própria na Issue/PR.

O cadastro faltante deixou de ser uma ausência de aquisição. Continuam não apurados: cobertura de valores do Resumo 92, população financeira elegível, composição legal e vínculos temporais emissor/holding, significado do segmento 42/c9 e tratamento dos n4/TD desconhecidos. Nenhuma conclusão metodológica, monetária, de amostra acadêmica ou ponte de regimes foi promovida a decisão. A [Issue 16](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16) conserva a pesquisa mais ampla e os gaps de 2025; o [mapa da Issue 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) recebe esta evidência delimitada.

O próximo recorte possível é especificar separadamente a admissão do snapshot financeiro 202412/Resumo 92, com identidade bruta, arquivos/áreas, vintage, estados e denominadores de cobertura demonstrados. Adquirir este cadastro não autoriza por si a execução desse snapshot.

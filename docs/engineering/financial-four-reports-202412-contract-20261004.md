# Quatro relatórios financeiros IF.data 202412: contrato técnico completo

## Resultado e autoridade

Pesquisa offline da [Issue 39](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/39), base `588c9218b12a64898cf8db126d983eff01f0feb6`, branch `codex/financial-four-reports-contracts`. João aprovou Resumo, Ativo, Passivo e DRE oficiais com todas as variáveis; o objetivo final supera as oito métricas do piloto. Esta nota fecha exclusivamente **202412/1005/92,96,101,98**, com os cinco corpos oficiais já preservados. Não implementa, admite, coleta ou anualiza valores, nem escolhe amostra, unidade acadêmica, indicadores, joins, equivalência histórica ou ponte 2025. [O/C5/D/P/N1, abaixo]

O catálogo tem **70 nós no primeiro nível**, mas suas árvores `sc` contêm **121 nós: 9 agrupadores e 112 folhas**. As folhas são 36 posições de atributos cadastrais (nove em cada relatório), duas quantidades cadastrais e 74 posições monetárias, que usam **69 `lid` distintos**. Todas as folhas foram associadas ao dicionário e a sua origem: não há binding ou shard necessário desconhecido neste corpus. Agrupadores são estrutura, sem observação financeira inventada. [O `/99/files/12,28,31,32/trel/c`; D; P `getColsFolhas`]

A grade diagnóstica tem **159.264 posições**, com 158.746 armazenadas e 518 não armazenadas. O contrato anterior e o adapter atual continuam fechados em Resumo/oito bindings. Ampliá-los exige uma entrega própria: os novos números também tornam impossível um único DECIMAL exato de largura até 38, pois a grade completa combina 13 dígitos inteiros e escala 27. Tipos exatos por binding são suficientes neste corpus. [Preflight; código `financial._profile_for_selection`, `financial_parquet._numbers` na base]

Impacto na arquitetura: uma nota em `docs/engineering/`, destino canônico de contratos e evidência; preflight privado em preparação ignorada, sem raiz/camada, move/delete ou alteração de artefato aceito. Reutiliza [arquitetura](../architecture.md#organização-dos-arquivos-e-pastas), [glossário](../../GLOSSARY.md), [modelo lógico aprovado](../superpowers/specs/2026-10-04-logical-data-model-design.md) e [ADR 0001](../adr/0001-duckdb-parquet.md). Referências existentes: [cadastro](financial-cadaster-202412-20261003.md), [contrato das oito métricas](financial-snapshot-202412-contract-20261003.md), [admissão 25](financial-snapshot-202412-execution-20261003.md), [adapter 29](financial-parquet-20261004.md), [contrato 202312](financial-snapshot-202312-contract-20261004.md) e [execução 36](financial-snapshot-202312-execution-20261004.md). A pesquisa [40](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/40) tem destino exclusivo; nenhuma dependência de 202503 é necessária para este contrato 202412.

## Fontes primárias e integridade

Leitura local por `archive.load_body`; reconferidos os cinco hashes externos dos manifests e dos corpos, tamanho, GET, HTTP 200, `outcome=ok`, `truncated=false`, diagnósticos vazios. Nenhuma requisição IF.data, execução de `nac`/formatter, navegador, instalação, admissão ou Parquet foi utilizada. Links identificam as primárias; uma recuperação futura pode ter outros bytes. Os manifests preservam contexto e headers privados; abaixo somente proveniência mínima. Pointers são zero-based no corpo original, sem reordenar arrays; offsets de P são bytes UTF-8. [Manifests O/C5/D/P/N1]

| Fonte | Recuperação UTC | Bytes | SHA-256 corpo | SHA-256 manifest |
|---|---|---:|---|---|
| [O: catálogo 2000–2024](https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024) | 2026-10-03T20:42:19.737446+00:00 | 13527657 | `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` | `b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7` |
| [C5: cadastro 202412/1005](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Fcadastro202412_1005.json) | 2026-10-03T20:42:20.380990+00:00 | 739235 | `eec996cd9b6b219d26a7e63a1b803273ad0a418c6e022b06506f3a226b9c98e1` | `e5dc177cc63391238acb818615167359624d8ce0bb1c375fabc496a1ac2a655e` |
| [D: info202412](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Finfo202412.json) | 2026-10-01T01:32:36.021567+00:00 | 188690 | `9c09219eeb7aa558e0ac74e32b905ba940ec00b0bc01f761b1d086aef86cca28` | `45b12d698f2b6bcaae34ebf09f8d051f7fab1e3036e27ef1a147eee979b9192e` |
| [P: portal](https://www3.bcb.gov.br/ifdata/index.html) | 2026-10-01T01:27:56.936588+00:00 | 92483 | `234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153` | `5757f812b56dbd414e2fa3d68075cafbf50157a010a9b4b330126fab86dd211a` |
| [N1: dados202412_1](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Fdados202412_1.json) | 2026-10-01T02:18:25.001757+00:00 | 15612512 | `c0f14556464dfd191df00d6867023fa894174b0eeb007a2bd5f5714187fa0474` | `2e782a8c6b9fc02ad109921550a4f9ebde49cfd534a26e851e368840abbfaa07` |

O `/99/dt=202412`, `/99/files/10/sel/1` identifica **1005, Conglomerados Financeiros e Instituições Independentes**. C5 é o cadastro anunciado em `/99/files/0/f`, D em `/99/files/9/f`, N1 em `/99/files/3/f`. Todos os quatro `trel.s=[{id:1005}]`, `fx=""`, `v="1"`, `ge="15/04/2026"`. `ge` é texto de geração do relatório sem fuso/horário; não é a referência nem a recuperação. D tem contexto de aquisição 1006 e N1 veio da descoberta individual/shared; seu reaproveitamento é sustentado pela associação literal dos arquivos na referência, sem reclassificar o contexto da aquisição como financeiro. Cadastro, dicionário e números não provam geração conjunta. [O; manifests D/N1/C5]

O anuncia `dados202412_1..5.json` em `/99/files/3..7/f`. **Somente `_1` é requerido pelos 74 bindings `td=3/a=1` deste recorte**. Os shards 2–5 não são entradas necessárias destes quatro relatórios; a existência no catálogo não implica aquisição nem ausência financeira. Não baixar shards por associação. Os quatro relatórios vêm das estruturas `trel` embutidas em O; esta nota não presume download dos arquivos `trel202412_*.json` anunciados. [O; D]

## Schema, caminhos e denominadores

C5 é array de **1.422 registros**, cada um com as chaves nativas `c0..c37` (38), `c1="202412"` e `c0` string opaca, não vazia, única. Preservar os 38 campos, sem padding, coercão de identificador ou exclusão por TCB/TD/SR. O denominador é registro cadastral, não “1.422 bancos”, emissor de capital aberto ou amostra acadêmica. N1 é `{id:1, values:[{e,v:[{i,v}]}]}`; contém **4.087 entidades compartilhadas**, com `e` e `i` JSON number, únicos no arquivo/entidade respectivamente. Correspondência literal `C5.c0 == lexema(N1.e)` encontra **1.417/1.422**; cinco entidades não estão armazenadas. Em cada `lid` selecionado, dois dos 1.417 correspondentes não têm informação; todos os demais 1.415 têm JSON number. [C5; N1; preflight]

P `getValueFromIfd`, byte 17354: `td=1` usa `cad['c'+lid]`; `td=3` seleciona a área `a`, entidade `cad.c0` e informação `lid`. P `findBinDataByEntInf`, byte 4417, busca `e/i`. P `getColsFolhas`, byte 17149, visita recursivamente `sc` e seleciona somente folhas; `mountData`, byte 19834, monta as linhas cadastrais. Os nove `td=2/ty=0/lid=-1` têm filhos e servem como cabeçalhos; não se busca `i=-1`, não se gera célula null/NI para grupo e não se calcula sua soma. Os totais explícitos são outras folhas `td=3` existentes no shard. [P; O/D]

| Relatório | Pointer O (`/trel` incluído) | Topo | Nós | Grupos | Folhas | Atributos | Quantidades | Monetárias | Grade | Armazenadas | Não armazenadas |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 92 Resumo | `/99/files/28/trel` | 17 | 17 | 0 | 17 | 9 | 2 | 6 | 24174 | 24132 | 42 |
| 96 Ativo | `/99/files/31/trel` | 20 | 28 | 2 | 26 | 9 | 0 | 17 | 36972 | 36853 | 119 |
| 101 Passivo | `/99/files/12/trel` | 15 | 33 | 3 | 30 | 9 | 0 | 21 | 42660 | 42513 | 147 |
| 98 Demonstração de Resultado | `/99/files/32/trel` | 18 | 43 | 4 | 39 | 9 | 0 | 30 | 55458 | 55248 | 210 |

Grade = 1.422 × folhas por relatório; os nove grupos não entram. **518** posições monetárias não armazenadas = `5×74=370 entity_not_stored` + `2×74=148 information_not_stored`. Há **104.710** posições monetárias armazenadas (`1.415×74`), **2.844** quantidades e **51.192** atributos (`1.422×9×4`). A repetição dos atributos e dos `lid` entre bindings é posição oficial do relatório, sem deduplicar observações por nome ou somar duplicatas. Todos os campos/folhas selecionados foram encontrados no schema, logo não houve ausência estrutural ou fonte ausente. [Preflight]

Estados dos valores armazenados: **61.430 numeric**, **46.124 zero**, **51.168 text**, **24 empty**; os 518 ausentes ficam em cobertura e não viram observação. As strings vazias são quatro SR/c12 e dois TD/c4 em C5, repetidos em quatro relatórios. Quantidades vêm de JSON strings, valores monetários de JSON numbers, atributos de strings. Não se observou NA, NI, null JSON, null literal ou valor inválido nas células selecionadas existentes; isso não autoriza colapsar esses estados no leitor futuro. P pode sintetizar NI para falta de célula; o contrato não o executa nem promove essa apresentação a token observado. [C5/N1/P; preflight]

## Bindings completos, conceitos e janelas

Todos os 121 nós estão contabilizados abaixo: os 36 atributos são explicitamente associados nas quatro posições 0–8; as outras 85 linhas inventariam as duas quantidades, os 74 saldos e nove grupos, incluindo os 51 descendentes além do topo. Cada linha se liga a O, D e origem; nenhum binding pendente. **`ifd` não é `lid`, nem conta Cosif.** `td` (tipo da origem em D) não é o atributo de consolidação TD/c4. `a=1` é área numérica; os flags de coluna `a/na/nc` são metadados de apresentação/agregação, não identidade da fonte. [O/D/P]

As composições `D.d` são transcrições documentais ou paráfrases identificadas dos somatórios textuais; não são fórmulas executáveis, certificação contábil ou valores reconstruídos. Nome com letra, subtotal ou `=` não permite refazer valor. Os dados continuam 202412 sob as definições nativas anteriores à quebra de 2025; nomes iguais não estabelecem continuidade com outros períodos, perspectivas ou regimes. [D; contratos existentes]

### Nove atributos em cada relatório

Para **cada** R ∈ {92,96,101,98}, `base` é o pointer da tabela anterior: a origem O é `base/c/k`, D é o pointer indicado, C5 é `/j/cN`. São nove folhas `td=1/a=1/ty=0`; unidade é texto/código/data, janela é atributo observado em 202412, sem saldo monetário ou identidade histórica. Os `column_id` são sequenciais: Resumo `18408+k`, Ativo `18488+k`, Passivo `18626+k`, DRE `18549+k`. [O/D/C5]

| k | Conceito | ifd | D | lid/campo C5 | fid | Tratamento nativo |
|---:|---|---:|---|---|---:|---|
| 0 | Instituição | 79670 | `/557` | 2 / c2 | 8 | Nome literal |
| 1 | Código | 79706 | `/593` | 0 / c0 | 9 | Código opaco; `nc=true`/`nac` só apresentação |
| 2 | TCB | 79671 | `/558` | 3 / c3 | 1 | Classificação literal; conservar inclusive n4 |
| 3 | SR | 79679 | `/566` | 12 / c12 | 1 | Segmento literal; vazio observado separado |
| 4 | TD | 79675 | `/562` | 4 / c4 | 1 | Consolidação literal; vazio separado |
| 5 | TC | 79676 | `/563` | 6 / c6 | 1 | Controle literal |
| 6 | Cidade | 79672 | `/559` | 11 / c11 | 1 | Cidade da sede literal |
| 7 | UF | 79673 | `/560` | 10 / c10 | 1 | Estado literal |
| 8 | Data | 79678 | `/565` | 1 / c1 | 14 | Data-base literal, sem executar formatter |

D `/593/d` descreve código como conglomerado ou CNPJ, sem provar qual entidade legal corresponde a cada ocorrência. O `c/1/nac` subtrai 200.000.000 de determinado intervalo e `nc=true` oculta sua célula; O `c/3/nac` pode ocultar SR por c3/c31. **Não executar nem aplicar essas regras aos valores nativos**: conservar código e SR e guardar as regras como metadados opacos. As definições TCB/TD/TC/SR vêm de D nos pointers da tabela; ausência e segmentações não qualificadas continuam explícitas conforme a nota cadastral. [O/D/C5; P]

### Unidade e janela das demais folhas

Folhas `td=3/ty=1/fid=13` são monetárias nos quatro relatórios; O `base/cp` informa **R$ mil na apresentação**. P `getTdClass`, case 13 byte 28520, e `getCsvClass`, case 13 byte 33835, dividem por 1.000 e arredondam; inglês também divide por `cot`. Inferência técnica mantida: a unidade de entrada é real nominal, inferida do renderer, sem tomar CSV arredondado ou converter PTAX. `cot=6.1923` é metadado de apresentação desta vintage, não um valor escolhido para conversão. Nenhuma folha percentual foi encontrada (`fid` das folhas: 1,2,8,9,13,14); o leitor futuro não deve interpretar outros fid/ty automaticamente como moeda. [O/P/D]

**Resumo:** seis saldos monetários, sendo lucro 79718→78187 fluxo de **01/07/2024 a 31/12/2024**, conforme O `/99/files/28/trel/rp`, item 1. Os outros cinco são estoques na referência, classificação técnica baseada nos conceitos; agências/postos são contagens cadastrais na referência (strings originais e Decimal derivado separados). **Ativo e Passivo:** todas as folhas monetárias são posições de estoque em 31/12/2024, inferido dos conceitos, sem janela semestral. **DRE:** todas as 30 folhas monetárias são fluxo do segundo semestre, **01/07/2024 a 31/12/2024**, apoiado diretamente em O `/99/files/32/trel/rp`, item 1. A DRE de dezembro não é anual nem trimestre isolado. Grupos não têm valor/unidade/janela de célula; guardam o contexto do relatório. [O/D]

Em cada tabela, `c/...` é sufixo de `base` da tabela dos relatórios; `/sc/...` conserva exatamente o caminho da árvore. D aponta à definição original; `td/lid` determinam origem (`1→C5 cN`, `3→N1 i=N`, `2/-1→grupo`). Área de todos = 1. Para `td=3`, `Decimal(p,s)` é diagnóstico por binding neste corpus; para quantidade é derivação opcional exata; para grupo é inaplicável. As composições entre colchetes permanecem literais. [O/D; preflight]

### 92 — Resumo

| Caminho O | column_id / ifd | D | td / lid | fid | Conceito / composição documental | Decimal(p,s) |
|---|---|---|---|---:|---|---|
| `c/9` | 18417 / 78182 | `/455` | 3 / 78182 | 13 | Ativo Total; `[10000007] + [20000004]` | (15,2) |
| `c/10` | 18418 / 78183 | `/456` | 3 / 78183 | 13 | Carteira de Crédito Classificada; `[31000000]` | (15,2) |
| `c/11` | 18419 / 78184 | `/457` | 3 / 78184 | 13 | Passivo Circulante e Exigível a Longo Prazo e Resultados de Exercícios Futuros; `[40000008] + [50000005]` | (15,2) |
| `c/12` | 18420 / 78185 | `/458` | 3 / 78185 | 13 | Captações; `[41000007] + [42000006] + [43000005] + [46000002]` | (15,2) |
| `c/13` | 18421 / 78186 | `/459` | 3 / 78186 | 13 | Patrimônio Líquido; `[60000002] + [70000009]+ [80000006]` | (14,2) |
| `c/14` | 18422 / 79718 | `/605` | 3 / 78187 | 13 | Lucro Líquido; `[70000009]+[80000006]-[81956001]` | (33,22) |
| `c/15` | 18423 / 79704 | `/591` | 1 / 16 | 2 | Número de Agências; `Número de Agências, incluídas as sedes (exceto para cooperativas)` | (4,0) |
| `c/16` | 18424 / 79705 | `/592` | 1 / 17 | 2 | Número de Postos de Atendimento; `Número de Postos de Atendimento` | (4,0) |

### 96 — Ativo

| Caminho O | column_id / ifd | D | td / lid | fid | Conceito / composição documental | Decimal(p,s) |
|---|---|---|---|---:|---|---|
| `c/9` | 18497 / 79681 | `/568` | 3 / 78188 | 13 | Disponibilidades (a); `[11000006]` | (13,2) |
| `c/10` | 18498 / 78189 | `/461` | 3 / 78189 | 13 | Aplicações Interfinanceiras de Liquidez (b); `[12000005]` | (14,2) |
| `c/11` | 18499 / 78190 | `/462` | 3 / 78190 | 13 | TVM e Instrumentos Financeiros Derivativos (c); `[13000004]` | (14,2) |
| `c/12` | 18500 / 79674 | `/561` | 2 / -1 | 4 | Operações de Crédito; grupo sem composição/célula | — |
| `c/12/sc/0` | 18501 / 78191 | `/463` | 3 / 78191 | 13 | Operações de Crédito (d1); `[16000001]-[16900008]` | (15,2) |
| `c/12/sc/1` | 18502 / 78192 | `/464` | 3 / 78192 | 13 | Provisão sobre Operações de Crédito (d2); `[16900008]` | (13,2) |
| `c/12/sc/2` | 18503 / 78193 | `/465` | 3 / 78193 | 13 | Operações de Crédito Líquidas de Provisão (d); `[16000001]` | (15,2) |
| `c/13` | 18504 / 79687 | `/574` | 2 / -1 | 4 | Arrendamento Mercantil; grupo sem composição/célula | — |
| `c/13/sc/0` | 18505 / 78194 | `/466` | 3 / 78194 | 13 | Arrendamento Mercantil a Receber (e1); `[17000000]-[17900007]` | (19,9) |
| `c/13/sc/1` | 18506 / 78195 | `/467` | 3 / 78195 | 13 | Imobilizado de Arrendamento (e2); `[23000001]` | (12,2) |
| `c/13/sc/2` | 18507 / 78196 | `/468` | 3 / 78196 | 13 | Credores por Antecipação de Valor Residual (e3); `[49908008]` | (12,2) |
| `c/13/sc/3` | 18508 / 78197 | `/469` | 3 / 78197 | 13 | Provisão sobre Arrendamento Mercantil (e4); `[17900007]` | (11,2) |
| `c/13/sc/4` | 18509 / 78198 | `/470` | 3 / 78198 | 13 | Arrendamento Mercantil Líquido de Provisão (e); `[17000000] + [23000001] + [49908008]` | (13,2) |
| `c/14` | 18510 / 78199 | `/471` | 3 / 78199 | 13 | Outros Créditos - Líquido de Provisão (f); `[18000009]` | (14,2) |
| `c/15` | 18511 / 78200 | `/472` | 3 / 78200 | 13 | Outros Ativos Realizáveis (g); `[19000008] + [14000003] + [15000002]` | (14,2) |
| `c/16` | 18512 / 78201 | `/473` | 3 / 78201 | 13 | Permanente Ajustado (h); `[20000004]-[23000001]` | (21,9) |
| `c/17` | 18513 / 78202 | `/474` | 3 / 78202 | 13 | Ativo Total Ajustado (i) = (a) + (b) + (c) + (d) + (e) + (f) + (g) + (h); `[11000006] + [12000005] + [13000004] + [16000001] + [17000000] + [23000001] + [49908008] + [18000009] + [19000008] + [14000003] + [15000002] + [20000004]-[23000001]` | (15,2) |
| `c/18` | 18514 / 79682 | `/569` | 3 / 78196 | 13 | Credores por Antecipação de Valor Residual (j); `[49908008]` | (12,2) |
| `c/19` | 18515 / 79683 | `/570` | 3 / 78182 | 13 | Ativo Total (k) = (i) - (j); `[10000007]+[20000004]` | (15,2) |

### 101 — Passivo

| Caminho O | column_id / ifd | D | td / lid | fid | Conceito / composição documental | Decimal(p,s) |
|---|---|---|---|---:|---|---|
| `c/9` | 18635 / 79684 | `/571` | 2 / -1 | 4 | Captações; grupo sem composição/célula | — |
| `c/9/sc/0` | 18636 / 79693 | `/580` | 2 / -1 | 4 | Depósito Total; grupo sem composição/célula | — |
| `c/9/sc/0/sc/0` | 18637 / 78282 | `/504` | 3 / 78282 | 13 | Depósitos à Vista (a1); `[41100000]` | (14,2) |
| `c/9/sc/0/sc/1` | 18638 / 78283 | `/505` | 3 / 78283 | 13 | Depósitos de Poupança (a2); `[41200003]` | (14,2) |
| `c/9/sc/0/sc/2` | 18639 / 78284 | `/506` | 3 / 78284 | 13 | Depósitos Interfinanceiros (a3); `[41300006]` | (13,2) |
| `c/9/sc/0/sc/3` | 18640 / 78286 | `/508` | 3 / 78286 | 13 | Depósitos a Prazo (a4); `[41500002]` | (14,2) |
| `c/9/sc/0/sc/4` | 18641 / 79720 | `/607` | 3 / 110560 | 13 | Conta de Pagamento Pré-Paga (a5); `[41930005]` | (13,2) |
| `c/9/sc/0/sc/5` | 18642 / 79721 | `/608` | 3 / 78285 | 13 | Depósitos Outros (a6); `[41400009]+[41600005]+[41700008]+[41800001]+[41900004]-[41930005]` | (21,10) |
| `c/9/sc/0/sc/6` | 18643 / 78287 | `/509` | 3 / 78287 | 13 | Depósito Total (a); `[41000007]` | (15,2) |
| `c/9/sc/1` | 18644 / 78288 | `/510` | 3 / 78288 | 13 | Obrigações por Operações Compromissadas (b); `[42000006]` | (14,2) |
| `c/9/sc/2` | 18645 / 79694 | `/581` | 2 / -1 | 4 | Recursos de Aceites e Emissão de Títulos; grupo sem composição/célula | — |
| `c/9/sc/2/sc/0` | 18646 / 78289 | `/511` | 3 / 78289 | 13 | Letras de Crédito Imobiliário (c1); `[43235007]` | (14,2) |
| `c/9/sc/2/sc/1` | 18647 / 78290 | `/512` | 3 / 78290 | 13 | Letras de Crédito do Agronegócio (c2); `[43240009]` | (14,2) |
| `c/9/sc/2/sc/2` | 18648 / 78291 | `/513` | 3 / 78291 | 13 | Letras Financeiras (c3); `[43250006]` | (14,2) |
| `c/9/sc/2/sc/3` | 18649 / 78292 | `/514` | 3 / 78292 | 13 | Obrigações por Títulos e Valores Mobiliários no Exterior (c4); `[43500000]` | (13,2) |
| `c/9/sc/2/sc/4` | 18650 / 78293 | `/515` | 3 / 78293 | 13 | Outros Recursos de Aceites e Emissão de Títulos (c5); `[43000005] - [43235007] - [43240009] - [43250006] - [43500000]` | (36,25) |
| `c/9/sc/2/sc/5` | 18651 / 78294 | `/516` | 3 / 78294 | 13 | Recursos de Aceites e Emissão de Títulos (c); `[43000005]` | (14,2) |
| `c/9/sc/3` | 18652 / 78295 | `/517` | 3 / 78295 | 13 | Obrigações por Empréstimos e Repasses (d); `[46000002]` | (14,2) |
| `c/9/sc/4` | 18653 / 79685 | `/572` | 3 / 78185 | 13 | Captações (e) = (a) + (b) + (c) + (d); `[41000007] + [42000006] + [43000005] + [46000002]` | (15,2) |
| `c/10` | 18654 / 78296 | `/518` | 3 / 78296 | 13 | Instrumentos Derivativos (f); `[47000001]` | (14,2) |
| `c/11` | 18655 / 78297 | `/519` | 3 / 78297 | 13 | Outras Obrigações (g); `[49000009] + [45000003] + [44000004]` | (14,2) |
| `c/12` | 18656 / 78298 | `/520` | 3 / 78298 | 13 | Passivo Circulante e Exigível a Longo Prazo (h) = (e) + (f) + (g); `[40000008]` | (15,2) |
| `c/13` | 18657 / 79782 | `/669` | 3 / 78186 | 13 | Patrimônio Líquido (i); `[60000002] + [70000009]+ [80000006]` | (14,2) |
| `c/14` | 18658 / 79783 | `/670` | 3 / 78300 | 13 | Passivo Total (j) = (h) + (i); `[40000008] + [60000002] + [70000009]+ [80000006]` | (21,8) |

### 98 — Demonstração de Resultado

| Caminho O | column_id / ifd | D | td / lid | fid | Conceito / composição documental | Decimal(p,s) |
|---|---|---|---|---:|---|---|
| `c/9` | 18558 / 79695 | `/582` | 2 / -1 | 4 | Resultado de Intermediação Financeira; grupo sem composição/célula | — |
| `c/9/sc/0` | 18559 / 79688 | `/575` | 2 / -1 | 4 | Receitas de Intermediação Financeira; grupo sem composição/célula | — |
| `c/9/sc/0/sc/0` | 18560 / 78203 | `/475` | 3 / 78203 | 13 | Rendas de Operações de Crédito (a1); `[71100001]+[71910002]+[71915007]+[71920009]+[71925004]+[71950000]+[71980001]+[81945005]+[81950007]+[81915004]` | (19,8) |
| `c/9/sc/0/sc/1` | 18561 / 78204 | `/476` | 3 / 78204 | 13 | Rendas de Operações de Arrendamento Mercantil (a2); `[71200004]+[81940000]` | (12,2) |
| `c/9/sc/0/sc/2` | 18562 / 78205 | `/477` | 3 / 78205 | 13 | Rendas de Operações com TVM (a3); `[71400000]+[71500003]-[71580009]+[71940003]+[71945008]+[71947006]+[71990053]+[71990101]+[71990156]+[71990204]+[81500000]-[81550005]+[81830055]+[81830103]+[81830158]+[81830206]` | (25,14) |
| `c/9/sc/0/sc/3` | 18563 / 78206 | `/478` | 3 / 78206 | 13 | Rendas de Operações com Instrumentos Financeiros Derivativos (a4); `[71580009]+[81550005]+[71990266]+[81830268]` | (20,10) |
| `c/9/sc/0/sc/4` | 18564 / 78207 | `/479` | 3 / 78207 | 13 | Resultado de Operações de Câmbio (a5); `[71300007]+[81400007]` | (23,12) |
| `c/9/sc/0/sc/5` | 18565 / 78231 | `/503` | 3 / 78231 | 13 | Rendas de Aplicações Compulsórias (a6); `[71955005]+[71960007]+[71965002]+[71990125]+[81830127]` | (12,2) |
| `c/9/sc/0/sc/6` | 18566 / 78208 | `/480` | 3 / 78208 | 13 | Receitas de Intermediação Financeira (a) = (a1) + (a2) + (a3) + (a4) + (a5) + (a6); `Somatório textual em D /480/d; conservar definição completa` | (24,12) |
| `c/9/sc/1` | 18567 / 79689 | `/576` | 2 / -1 | 4 | Despesas de Intermediação Financeira; grupo sem composição/célula | — |
| `c/9/sc/1/sc/0` | 18568 / 78209 | `/481` | 3 / 78209 | 13 | Despesas de Captação (b1); `[81100008]+[81980008]+[81986002]+[81912007]` | (14,2) |
| `c/9/sc/1/sc/1` | 18569 / 78210 | `/482` | 3 / 78210 | 13 | Despesas de Obrigações por Empréstimos e Repasses (b2); `[81200001]+[81960004]` | (13,2) |
| `c/9/sc/1/sc/2` | 18570 / 78211 | `/483` | 3 / 78211 | 13 | Despesas de Operações de Arrendamento Mercantil (b3); `[81300004]+[81830550]` | (12,2) |
| `c/9/sc/1/sc/3` | 18571 / 78212 | `/484` | 3 / 78212 | 13 | Resultado de Operações de Câmbio (b4); `[71300007]+[81400007]` | (17,8) |
| `c/9/sc/1/sc/4` | 18572 / 78213 | `/485` | 3 / 78213 | 13 | Resultado de Provisão para Créditos de Difícil Liquidação (b5); `[71990307]+[71990352]+[71990400]+[71990503]+[71990606]+[81830309]+[81830354]+[81830402]+[81830505]+[81830608]` | (25,14) |
| `c/9/sc/1/sc/5` | 18573 / 78214 | `/486` | 3 / 78214 | 13 | Despesas de Intermediação Financeira (b) = (b1) + (b2) + (b3) + (b4) + (b5); `Somatório textual em D /486/d; conservar definição completa` | (26,14) |
| `c/9/sc/2` | 18574 / 78215 | `/487` | 3 / 78215 | 13 | Resultado de Intermediação Financeira (c) = (a) + (b); `Somatório textual em D /487/d; conservar definição completa` | (23,12) |
| `c/10` | 18575 / 79690 | `/577` | 2 / -1 | 4 | Outras Receitas/Despesas Operacionais; grupo sem composição/célula | — |
| `c/10/sc/0` | 18576 / 78216 | `/488` | 3 / 78216 | 13 | Rendas de Prestação de Serviços (d1); `[71700009]-[71794008]-[71795007]-[71796006]-[71797005]-[71798004]+[71970004]` | (37,26) |
| `c/10/sc/1` | 18577 / 78217 | `/489` | 3 / 78217 | 13 | Rendas de Tarifas Bancárias (d2); `[71794008]+[71795007]+[71796006]+[71797005]+[71798004]` | (12,2) |
| `c/10/sc/2` | 18578 / 78218 | `/490` | 3 / 78218 | 13 | Despesas de Pessoal (d3); `[81718005]+[81727003]+[81730007]+[81733004]+[81736001]+[81737000]+[81990201]` | (13,2) |
| `c/10/sc/3` | 18579 / 78219 | `/491` | 3 / 78219 | 13 | Despesas Administrativas (d4); `[71930006]+[8170006]-[81718005]-[81727003]-[81730007]-[81733004]-[81736001]-[81737000]+[81810006]+[81820003]+[81910009]` | (37,26) |
| `c/10/sc/4` | 18580 / 78220 | `/492` | 3 / 78220 | 13 | Despesas Tributárias (d5); `[81925001]+[81930003]+[81933000]+[81990108]+[81990304]+[81990902]` | (12,2) |
| `c/10/sc/5` | 18581 / 78221 | `/493` | 3 / 78221 | 13 | Resultado de Participações (d6); `[71800002]+[71990802]+[71990905]+[71990709]+[81600003]+[81830804]+[81830907]+[81830701]` | (20,10) |
| `c/10/sc/6` | 18582 / 78222 | `/494` | 3 / 78222 | 13 | Outras Receitas Operacionais (d7); `[71900005]-[71910002]-[71915007]-[71920009]-[71925004]-[71930006]-[71940003]-[71945008]-[71947006]-[71950000]-[71955005]-[71960007]-[71965002]-[71970004]-[71980001]-[71990053]-[71990101][71990125]-[71990156]-[71990204]-[71990266]-[71990307]-[71990352]-[71990400]-[71990503]-[71990606]-[71990709]-[71990802]-[71990905]` | (38,27) |
| `c/10/sc/7` | 18583 / 79719 | `/606` | 3 / 78223 | 13 | Outras Despesas Operacionais (d8); `[81800009]-[81810006]-[81820003]-[81830055]-[81830103]-[81830127]-[81830158]-[81830206]-[81830268]-[81830309]-[81830354]-[81830402]-[81830505]-[81830550]-[81830608]-[81830701]-[81830804]-[81830907]+[81900002]-[81910009]-[81912007]-[81915004]-[81925001]-[81930003]-[81933000]-[81940000]-[81945005]-[81950007] -[81956001]-[81960004]-[81980008]-[81986002]-[81990108]-[81990201]-[81990304]-[81990902]` | (38,27) |
| `c/10/sc/8` | 18584 / 78224 | `/496` | 3 / 78224 | 13 | Outras Receitas/Despesas Operacionais (d) = (d1) + (d2) + (d3) + (d4) + (d5) + (d6) + (d7) + (d8); `Somatório textual em D /496/d; conservar definição completa` | (22,11) |
| `c/11` | 18585 / 78225 | `/497` | 3 / 78225 | 13 | Resultado Operacional (e) = (c) + (d); `Somatório textual em D /497/d; conservar definição completa` | (23,12) |
| `c/12` | 18586 / 78227 | `/499` | 3 / 78227 | 13 | Resultado Não Operacional (f); `[73000006]+[83000003]` | (23,13) |
| `c/13` | 18587 / 78226 | `/498` | 3 / 78226 | 13 | Resultado antes da Tributação, Lucro e Participação (g) = (e) + (f); `Somatório textual em D /498/d; conservar definição completa` | (33,22) |
| `c/14` | 18588 / 78228 | `/500` | 3 / 78228 | 13 | Imposto de Renda e Contribuição Social (h); `[89410006]+[89420003]` | (12,2) |
| `c/15` | 18589 / 78229 | `/501` | 3 / 78229 | 13 | Participação nos Lucros (i); `[89700008]` | (12,2) |
| `c/16` | 18590 / 79717 | `/604` | 3 / 78187 | 13 | Lucro Líquido (j) = (g) + (h) + (i); `[70000009]+[80000006]-[81956001]` | (33,22) |
| `c/17` | 18591 / 79716 | `/603` | 3 / 78230 | 13 | Juros Sobre Capital Social de Cooperativas (k); `[81956001]` | (11,2) |

D `/491/d`, ifd 78219, contém literalmente `[8170006]` com sete dígitos; D `/494/d`, ifd 78222, contém `[71990101][71990125]` sem operador entre as rubricas. A pesquisa não corrige esses textos nem assume fórmula pretendida. Guardar o corpo/definição íntegros, marcar a composição como não executada e impedir qualquer reconstrução que dependa de sanear a fórmula. Estes pontos não impedem preservar o valor oficial já armazenado. `/478/d` e `/484/d` descrevem o mesmo conjunto de rubricas cambiais, mas seus `lid` são distintos: não deduplicar por composição ou nome. [D]

Ativo usa `ifd=79682` e `ifd=78196` para o mesmo `lid=78196`, em posições distintas; `ifd=79683→78182`, Passivo `79685→78185`, `79782→78186`, `79783→78300`, `79720→110560`, `79721→78285`, DRE `79719→78223`, `79717→78187`, `79716→78230` e Resumo `79718→78187` demonstram por que a chave é binding/posição dentro do relatório, não só `ifd`, nome ou `lid`. Mesma célula pode sustentar múltiplas posições oficiais, sem representar observações econômicas independentes para agregação. [O/D/N1]

## Contrato de leitura, persistência e rejeição proposto

Entrada fechada: índice explícito O/C5/D/P/N1 e pins de corpos/manifests, período/perspectiva/relatórios/versionamento explícitos, destino novo. Resolver somente as quatro árvores observadas, mantendo os nove cabeçalhos, 112 folhas e 38 campos nativos do cadastro. Hash externo não comprova autenticação além da fonte confiada; corpo/manifest/localizador e geração desconhecida acompanham cada interpretação. Não aceitar glob, fallback para 1006, descoberta pela rede, arquivo de outro período ou `nac` executável. [Contrato técnico desta Issue; modelo existente]

1. **Integridade antes do aceite:** status/outcome/tamanho/hash/contexto/diagnóstico/truncamento/schema exatos; JSON sem chaves duplicadas ou constantes não padrão; `info.id` único; `c0` único e string; `e/i` únicos e lexemas inteiros; quatro seletores 1005; tipos `td/a/ty/lid/fid`, árvore e relações pai/filho coerentes. Input ausente/schema corrompido não vira população zero. A rejeição registra evidência e não produz manifest de aceite.
2. **Identidade e estrutura:** origem aponta C5 `/j/cN` ou N1 `/values/j/v/k/v`; catálogo e dicionário têm hashes/pointers. Namespace mantém ocorrência no snapshot financeiro/202412. Binding incorpora report_id, column_id, pointer da árvore e parent/children; texto/número/código/data/quantidade são conceitos distintos. `sc`/`d`/flags/`nac` e notas do relatório permanecem metadados integrais. Grupo não entra na grade, e valor de subtotal existente é lido, nunca recalculado.
3. **Precisão e estados:** parse JSON numérico sem float; lexema numérico exato, string original, tipo JSON e Decimal derivado permanecem distintos. Token textual admite seu JSON source pointer no corpo íntegro; não confundir string numérica com JSON number. Preservar negativos, expoentes, zeros finais e sinais nos lexemas; não arredondar nem aplicar taxas. `numeric`, `zero`, `text`, `empty`, NA, NI, json_null, literal_null, inválido, campo/célula/entidade ausente e input/shard ausente são estados distintos. Cobertura mantém ausência sem observação sintetizada; fonte faltante bloqueia aceite completo.
4. **Modelo/artefatos:** usar as responsabilidades existentes de `financial.py`/`financial_parquet.py`, perfis e CLIs financeiras, com contratos versionados próprios do conjunto 202412; não enviar ao conversor individual nem relaxar defaults Resumo202312/202412. Complementos cadastrais e de variáveis preservam estrutura/nativos; grade e observações carregam os 112 bindings folha, tipos/unidade/janela e provenance. Os nove grupos ficam no complemento de bindings, sem tabela monetária inventada. A chave inclui snapshot/ocorrência/relatório/posição da folha e origem, conforme o modelo lógico existente.
5. **Parquet e consulta exata:** a estratégia global de `_numbers` exige **DECIMAL(40,27)** e deve continuar rejeitando overflow no contrato anterior. Para o novo contrato, perfilar por binding (larguras desta tabela) e escrever partições/buckets por tipo exato, dentro dos destinos financeiros existentes. Todos os bindings cabem em largura até 38 neste corpus; nenhum cast global ou união numérica que arredonde ou promova a DOUBLE é permitido. Uma grade/view geral conserva texto Decimal canônico e lexema, com consultas numéricas tipadas somente na partição/binding cujo tipo esteja explícito nos metadados. Não oferecer `numeric_decimal` global menor que o necessário nem promover string em moeda. **Alternativas:** texto + Decimal Python preserva tudo sem nova dependência, mas retira consulta numérica SQL direta; buckets/partições tipados preservam consulta exata por binding com a dependência atual; decimal256 exigiria dependência/adaptação novas ainda sem necessidade comprovada. Coeficiente/escala também preserva números, mas aumentaria schema e operações. Recomenda-se grade textual comum + partição tipada por binding/bucket como menor mudança sobre Parquet/DuckDB, mantendo contrato próprio e expondo limite de agregação entre tipos. Aceite exige equality Python Decimal↔Parquet por célula e consulta por binding; consultas entre tipos recebem decisão explícita/checagem de representabilidade. O limite global não bloqueia preservação nativa nem o objetivo completo aprovado.
6. **Replay e preservação:** recusar destino existente; fontes aceitas nunca sobrescritas, manifest final escrito após verificações. Replay em destino novo reconstrói todos os tokens, associações, metadados e contagens; hashes de saídas determinísticas iguais, UTC operacional separado. Antes/depois, comparar inventário protegido definido pelo integrador, além dos dez arquivos das fontes aqui conferidos. A pesquisa não substitui essa revisão do conjunto protegido.

O integrador executou um probe **sintético**, DuckDB 1.5.6: `UNION ALL` de `DECIMAL(27,27)` com `DECIMAL(13,0)` promoveu ambos a `DECIMAL(38,25)` e `1e-27` virou `0E-25`. Portanto, cast exato em cada bucket não basta para uma união numérica global segura. Proibir essa união no novo contrato; usar a grade textual comum e views tipadas por binding/bucket, com igualdade verificada. O receipt foi lido nesta pesquisa e não contém valores reais do corpus; não é resultado de implementação/Parquet. [Probe sintético do integrador]

Fonte/dicionário preservados não provam equivalência histórica. Unidade crua inferida, vintage não simultânea, cadastro com vazios, contabilidade da unidade IF.data, identidade emissor/holding e elegibilidade acadêmica mantêm suas qualificações; nenhum join acadêmico foi feito. `rp` de todos os quatro reports registra possibilidade de reapresentação/republicação na referência de dezembro; períodos recuperados em momentos diferentes não são conciliados automaticamente. [O `rp`; contratos existentes]

## Menor implementação e gate de capacidade

A menor entrega completa é **um conjunto fechado 202412 com os quatro relatórios**, 112 folhas e estrutura de 9 grupos, no reader/adapter financeiros existentes. Resumo de oito métricas continua aceito no contrato anterior. Um arquivo de perfil próprio guarda estrutura/inputs/bindings versionados, em vez de parâmetros genéricos para períodos desconhecidos. Allowlist candidata para a próxima Issue: `bank_quality/financial.py`, `bank_quality/financial_parquet.py`, novo perfil específico em `bank_quality/`, `scripts/admit-financial.py`, `scripts/convert-financial.py`, testes financeiros pertinentes e plano/ledger datados em seus destinos canônicos; bruto readonly e saídas novas ignoradas em `data/derived/`/`data/curated/`. Nome exato do novo perfil/teste e compartilhados será fixado na Issue de implementação antes da escrita; esta proposta não concede ownership. [Arquitetura; APIs atuais; modelo lógico]

Pré-condições: contrato revisado, perfil e guardas verificáveis, novo contrato de tipos múltiplos e recurso medido no computador executor. **Nenhuma fonte adicional é requisito para este snapshot**. Os desconhecidos conceituais explicitados permitem preservação nativa, mas impedem usar o aceite técnico como comparabilidade ou método. A disponibilidade numérica não remove o trabalho de implementação/revisão/capacidade nem comprova aceitação de produção.

Aceite mínimo da próxima entrega: fixtures pequenas antes da escrita (árvore/group, ifd≠lid, binding duplicado por lid, texto/código/data/quantidade, Decimal40 global rejeitado e tipos locais exatos, estados/ausências/schema/hash/fonte faltante); execução real delimitada dos cinco inputs; grade **159.264**, armazenadas **158.746**, ausências **518**, 121 nós/112 folhas/9 grupos; igualdade lexical e Decimal para todas as células; consultas de cada relatório/binding e replay em destino novo; preservação dos contratos 202312 e Resumo202412 e do inventário protegido; checks pertinentes e revisão independente do head. Conferência contábil conserva definições e janelas; não exige validar identidades acadêmicas inexistentes.

Antes de história ou concorrência longa, medir uma admissão+Parquet+abertura+consulta+replay completos em **um** snapshot desta dimensão: pico working set/commit quando disponível, tempo, I/O, bytes e cardinalidades por etapa, processo, lotes/threads/workers. Ajustar recursos por máquina; avaliar workers somente com inputs/destinos/ownership separados. O preflight abaixo mediu diagnóstico Python, sem Parquet/produção; ele não é gate integral ou prova de capacidade 2010–2026. `sc` multiplicou as posições além do topo e a materialização de índices ocupa memória; reduzir batches de escrita não demonstra reduzir esse estado global. Não impor teto universal baseado neste computador.

## Execução reproduzível e evidência

O preflight privado usa somente biblioteca padrão Python e `archive.load_body` existente. Procedimento: (1) abrir explicitamente os cinco manifests referenciados no contrato anterior e conferir os pins da tabela; (2) carregar/verificar corpos; (3) parse de números em classe lexical e object_pairs_hook que rejeita duplicatas; (4) localizar O `/99`, os quatro reports/seletores, caminhar `c/sc` e associar cada `ifd` ao D; (5) validar C5 c0..c37 e N1 id/e/i, construir índices por igualdade lexical; (6) contar somente folhas por registro cadastral, estados/tipos, pointers testemunha e dimensões Decimal por binding; (7) gravar resultado/receipt somente em destino ausente e reconferir os dez hashes de origem. Saídas privadas não publicam valores brutos nesta nota. O script recusa reaproveitar output e não é leitor de produção. [Execução local]

Script SHA-256: `b61eac0d0e95ad503f5193f20a11e782d8959f8448d30dc7a536a6f20f3f2d62`. Resultado diagnóstico SHA-256: `a457e365b0fc9d77d19f8c480ff58b19d45e00bcb9652f384c958f62062bc656`. Foram verificados **822,822 objetos JSON** nos quatro corpos JSON e cinco manifests, sem chave duplicada/constante inválida; P foi conferido como bytes/UTF-8 e pelos localizadores citados. O perfil Decimal observou `integer=13`, `scale=27`, largura global `40`, maior largura por binding `38`. [Preflight/receipt privados]

Medição pontual do preflight revisto, Windows 11/Python 3.12.14: **3.469980 s** wall, **3.437500 s** CPU, **479,559,680 bytes** peak working set (457.34 MiB), inicial 25,522,176 bytes. Método: `GetProcessMemoryInfo`, processo único, decode e índices de fontes existentes. Tempo inclui leitura/validação/contagens, encerra antes de escrita de receipts/recheck final; pico é amostrado ao final dessa etapa e não inclui garantia de pico do ciclo posterior. Não mediu DuckDB/Parquet, integral histórico, commit/RAM total da máquina ou série estatística; números não dimensionam workers automaticamente. Primeira execução anterior à adição do perfil de largura teve as mesmas contagens, em 3,694082 s e peak 479.453.184 bytes; diferenças de tempo não demonstram otimização. [Receipt]

Validação local: 10 vínculos de arquivos conferidos, 85 linhas de grupos/saldos/quantidades + 36 posições de atributos = 121 nós, nove grupos sem célula; contagens, bindings, sources, tipos e perfil Decimal idênticos nas duas execuções após adição do perfil de largura, excluindo medições operacionais. Os dez arquivos de fonte tiveram hashes reconferidos antes/depois. A nota teve conferência de whitespace; o integrador confere inventário protegido completo e diff final. Revisão independente ainda pendente, identifica o conteúdo/hash e o head publicado. Resultado local não confirma revisão, CI, PR, merge, Issue done ou Project. Não se rodou suíte de software para esta nota/preflight privado. A conclusão da pesquisa não encerra o alvo 2010–2026, 202503, método ou comparabilidade.

# Snapshot financeiro IF.data 202312/Resumo 92: fontes e contrato

## Resultado, autoridade e organização

Entrega da [Issue 34](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/34), ligada ao [mapa 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2), base `a5a37e1fef0a309a384cbad367b1601357319e2f`, branch `codex/financial-sources-202312`. João autorizou em 2026-10-04 a aquisição exclusiva do cadastro financeiro 202312/1005 e a conferência offline do [lote proposto](historical-coverage-inventory-20261004.md#primeiro-lote-proposto-financeiro-202312100592). O cadastro foi recuperado na primeira tentativa: HTTP 200, 629.912 bytes, sem truncamento observado, em 0,469 s medidos pelo executor. O limite era duas tentativas, 5 MiB acumulados de corpos e 120 s por tentativa; redirects não foram seguidos. Não houve refresh de catálogo, dicionário, portal ou valores. [C5, recibo de aquisição]

O preflight encontrou **1.385 registros cadastrais**, **32 campos `c0..c31`**, oito bindings e **11.062 posições armazenadas**, em grade de 11.080; **18 posições não armazenadas** permanecem na cobertura. Isto é diagnóstico sobre corpos arquivados, **sem admissão, Parquet financeiro 202312, consulta histórica ou indicadores implementados**. As seis métricas monetárias correspondem à área1; agências/postos vêm do cadastro. Os códigos e os denominadores não são uma amostra de bancos academicamente elegíveis. [O, C5, D, N1]

Uma nota em `docs/engineering/`, bruto novo ignorado em `data/raw/financial-cadaster-202312-20261004/` e diagnósticos privados nos destinos contratados seguem a [arquitetura](../architecture.md#organização-dos-arquivos-e-pastas) e o [glossário](../../GLOSSARY.md). Sem raiz/camada nova, movimento/delete, mudança de código, perfil, dependência ou artefato aceito. O [modelo lógico aprovado](../superpowers/specs/2026-10-04-logical-data-model-design.md) e o [contrato 202412](financial-snapshot-202412-contract-20261003.md) são reutilizados como referência; o schema de 2023 é conferido separadamente. Superpowers verification-before-completion e requesting-code-review orientam verificação e revisão; systematic-debugging foi aplicada à divergência cadastral de 32/38 campos. Não houve nova pesquisa ampla, PDF, visual ou instalação de skill.

## Índice explícito, proveniência e limites das fontes

O/C5/D/P/N1 são as cinco fontes exatas. Pointers JSON abaixo são zero-based nos corpos identificados; `body_path` resolve na pasta de cada manifest. Todos os cinco corpos e manifests passaram por conferência de SHA-256/tamanho, URL final, método GET, HTTP200/outcome ok. Os quatro corpos JSON passaram por parsing integral sem chaves de objeto duplicadas, constantes não padrão ou conversão de números para float binário. Os manifests originais foram preservados. Headers, linhas de instituições e tokens financeiros ficam somente na evidência local ignorada.

| ID / fonte primária | Recuperação UTC | Bytes do corpo | SHA-256 do corpo |
|---|---|---:|---|
| [O: catálogo 2000–2024](https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024) | 2026-10-03T20:42:19.737446+00:00 | 13.527.657 | `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` |
| [C5: cadastro202312_1005](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202312%2Fcadastro202312_1005.json) | 2026-10-04T16:32:31.993557+00:00 | 629.912 | `30ab717bcba0279c1d4431e40bc216293ef93407872499e95051baca09af684e` |
| [D: info202312](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202312%2Finfo202312.json) | 2026-10-01T03:37:20.509Z | 174.579 | `11a0704ec62d3123c8af2ceb7c98b545c683781e297f8a3f4d89e449122c7ee2` |
| [P: portal arquivado](https://www3.bcb.gov.br/ifdata/index.html) | 2026-10-01T01:27:56.936588+00:00 | 92.483 | `234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153` |
| [N1: dados202312_1](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202312%2Fdados202312_1.json) | 2026-10-01T03:37:24.367Z | 15.316.532 | `fb85523b59409bb6ebc8bb32bf78751a2380eea3b880873f27331398e5511eae` |

Manifests exatos, sem descoberta por glob para a seleção:

- O: `data/raw/financial-cadaster-202412-20261003/20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json`.
- C5: `data/raw/financial-cadaster-202312-20261004/20261004T163231508621Z_cadaster_202312_1005_dc90945ec0a54d2abc1f042bc4cc48b9.json`.
- D: `data/runs/expansion-202312-20261001/raw/2026-10-01T033720509Z_202312_e1bacaca-f0b3-4c23-a40d-8defa2891ca2.json`.
- P: `data/raw/discovery-20261001/20261001T012756759142Z_portal_56229187f15948a0a353b4b194b7cb3f.json`.
- N1: `data/runs/expansion-202312-20261001/raw/2026-10-01T033724367Z_202312_5477956f-562c-4989-acdb-a72c933a3d42.json`.

**Exceção legada explícita:** O/C5/P registram `truncated=false` e diagnósticos vazios. D/N1, capturados na expansão individual pelo navegador, **não declaram `truncated`** e registram `Playwright stores decoded response-body bytes`. Seus hashes são dos corpos decodificados preservados, não de bytes comprimidos na rede. O preflight conserva `truncation_state=undeclared_legacy`; parsing completo e integridade não transformam a ausência do campo em `false` nem provam completude econômica/global. A utilização futura destes dois corpos exige compatibilidade delimitada por role, referência, URL, hashes de corpo/manifest, schema e essa qualificação; não alterar os manifests, aceitar arbitrariamente outros legados ou esvaziar diagnósticos. [D, N1]

Hashes dos manifests legados contratados: D `f26d028164139e20faa2094b31bab08e8fbcd1410b28bd917b406018cf2c0425`; N1 `9d35989367a25ab9ae12551c8a5f6ddf7c51249d6a0f181bd34240f63a74e6db`. O índice/diagnóstico conserva também hashes de manifests dos outros três papéis.

O `/95/dt` é 202312. `/95/files/0/f` anuncia o cadastro1005; os mesmos arquivos `info202312.json` e `dados202312_1.json` também são anunciados uma vez nesse trimestre. `/95/files/29/trel` tem `id=92`, `n=Resumo`, perspectiva1005, 17 colunas, `fx=""`, `v="1"` e `ge="14/04/2025"`. O seletor1005 nomeia “Conglomerados Financeiros e Instituições Independentes”. As entradas de D/N1 continuam ligadas à aquisição original individual; reutilizar o corpo compartilhado não muda seu contexto nem prova vintage simultânea com C5. `ge` é texto de geração do relatório, sem horário/fuso, e não data de geração comprovada dos outros corpos. [O, D, N1, C5]

## Cadastro, bindings, unidade e janela

C5 contém 1.385 objetos com **exatamente `c0..c31`, todos strings**; `c1=202312`, `c0` único, não vazio e sem padding decimal. O cadastro202412 tem `c0..c37`: os seis campos adicionais não são preenchidos artificialmente no cadastro202312. O contrato preserva cada schema nativo; igualdade dos oito bindings selecionados não estabelece equivalência dos demais campos cadastrais. Todos os registros são conservados, sem filtro acadêmico ou exclusão por classificação. [C5; contrato202412]

As oito definições abaixo são iguais aos objetos correspondentes do perfil revisado202412; as oito colunas selecionadas também coincidem. São igualdades de metadados específicas, sem provar continuidade de perímetro, vintage ou comparabilidade econômica dos valores. Cada binding possui pointer O `/95/files/29/trel/c/k`; `ifd` resolve `D.id`, enquanto `lid` resolve `N1.i` ou `C5["c"+lid]`. [O, D, perfil202412]

| Conceito | k / ifd | Pointer D | td / área / lid / fid | Composição em D `d` |
|---|---|---|---|---|
| Ativo Total | 9 / 78182 | `/455` | 3 / 1 / 78182 / 13 | `[10000007] + [20000004]` |
| Carteira de Crédito Classificada | 10 / 78183 | `/456` | 3 / 1 / 78183 / 13 | `[31000000]` |
| Passivo Circulante e Exigível a Longo Prazo e Resultados de Exercícios Futuros | 11 / 78184 | `/457` | 3 / 1 / 78184 / 13 | `[40000008] + [50000005]` |
| Captações | 12 / 78185 | `/458` | 3 / 1 / 78185 / 13 | `[41000007] + [42000006] + [43000005] + [46000002]` |
| Patrimônio Líquido | 13 / 78186 | `/459` | 3 / 1 / 78186 / 13 | `[60000002] + [70000009]+ [80000006]` |
| Lucro Líquido | 14 / 79718 | `/605` | 3 / 1 / **78187** / 13 | `[70000009]+[80000006]-[81956001]` |
| Número de Agências | 15 / 79704 | `/591` | 1 / 1 / 16 / 2 | Quantidade cadastral, incluídas sedes exceto cooperativas |
| Número de Postos de Atendimento | 16 / 79705 | `/592` | 1 / 1 / 17 / 2 | Quantidade cadastral |

P `getValueFromIfd` (byte17354) associa `td=3` por área/`cad.c0`/`lid`, e `td=1` por campo cadastral. `findBinDataByEntInf` (byte4417) procura entidade `e` e informação `i`. N1 possui `{id:1, values:[{e,v:[{i,v}]}]}`; pointers `/values/j/v/k/v` identificam células existentes, e `/j/c16` ou `/j/c17` identificam quantidades em C5. O preflight verificou unicidade das entidades, informações por entidade, definições e códigos cadastrais, sem associação decimal que altere strings. [P, N1, C5]

O `/95/files/29/trel/cp` anuncia **R$ mil**. P `getTdClass`/`getCsvClass`, `case13`, bytes28520/33835, divide a entrada por1000 e arredonda a exibição em português. **Unidade crua BRL inferida tecnicamente**, separada da escala e precisão de apresentação; não arredondar os lexemas de N1 nem substituir por CSV renderizado. Para as cinco primeiras métricas monetárias, estoque na referência é inferência do conceito. Para Lucro Líquido, a nota O `rp`, item1, determina **julho–dezembro de2023**, não resultado anual. Agências/postos são contagens cadastrais na referência. O item4 permite republicação/reapresentação. O mesmo portal arquivado sustenta a hipótese de interpretação; não houve captura visual financeira202312 nem validação econômica de seus valores. [O, P]

## Preflight offline e denominadores

N1 contém **4.252 entidades** de uma área compartilhada. A associação literal entre `C5.c0` e o lexema inteiro `N1.e` encontra **1.382/1.385** registros; três códigos não possuem entidade armazenada. Nos 1.382 correspondentes, as seis informações monetárias estão presentes. As 2.870 entidades fora de C5 ficam fora do recorte, sem classificação de perspectiva ou elegibilidade presumida. A fonte compartilha dados; não contar todas as entidades como financeiras. [C5, N1]

| Métrica | Armazenadas | Numéricas não zero | Zero observado | Entidade não armazenada | Informação não armazenada | Denominador C5 |
|---|---:|---:|---:|---:|---:|---:|
| Ativo Total | 1382 | 1382 | 0 | 3 | 0 | 1385 |
| Carteira de Crédito Classificada | 1382 | 1109 | 273 | 3 | 0 | 1385 |
| Passivo Circulante/Exigível/Resultados Futuros | 1382 | 1380 | 2 | 3 | 0 | 1385 |
| Captações | 1382 | 987 | 395 | 3 | 0 | 1385 |
| Patrimônio Líquido | 1382 | 1382 | 0 | 3 | 0 | 1385 |
| Lucro Líquido | 1382 | 1381 | 1 | 3 | 0 | 1385 |
| Agências `c16` | 1385 | 585 | 800 | 0 | 0 | 1385 |
| Postos `c17` | 1385 | 582 | 803 | 0 | 0 | 1385 |

São **8.292 posições monetárias armazenadas** em grade de8.310 e **2.770 quantidades armazenadas** em grade de2.770: total11.062 em grade11.080. As **18 posições não armazenadas (`3×6`)** são ausência de entidade na fonte compartilhada, sem NI/zero/null sintetizado ou interpretação financeira atribuída. Os campos existentes selecionados têm somente tokens JSON number nas monetárias e JSON string nas quantidades; não foram observados NA, NI, NA%, NI%, null JSON, null literal, vazio ou inválido. O contrato continua distinguindo esses estados se surgirem em outro corpo, além de ausência estrutural/célula não armazenada. [C5, N1]

Execuções independentes do preflight: `.venv/Scripts/python.exe -B .superpowers/sdd/financial-sources-202312-20261004/preflight.py` e o mesmo comando com argumento `replay`. Cada processo leu e validou novamente as cinco fontes e produziu índice/diagnóstico em destino novo ignorado `verified-preflight`/`verified-preflight-replay`, dentro da pasta operacional contratada. **809.834 objetos JSON** dos quatro corpos e cinco manifests foram conferidos por execução. Comparação byte a byte dos dois arquivos por execução passou; hashes: `source-index.json` = `3769c0b06ab6ed525a7a8087b5678883d2ea68e5929da4f6af278670e3229fb0`, `preflight.json` = `f646de3c5859c69de4e78c3f7014ed042d0eb857e6b0d3a4ae2445690665a92c`. Os **51 arquivos protegidos anteriores** permanecem íntegros. A primeira tentativa de diagnóstico, com esquema38 herdado, foi rejeitada antes de produzir aceite; o diagnóstico intermediário em `data/runs/financial-snapshot-preflight-202312-20261004/` ficou preservado e não é o recibo final. [Recibos locais]

O índice final diagnóstico usa `ifdata-financial-preflight-index-202312-v1`, com cinco paths relativos à raiz do repositório e `source_path_basis=repository_root`; **não é entrada da CLI de produção**. Um índice futuro de admissão deve resolver os paths em relação ao próprio arquivo, registrar hashes de manifests/corpos e a referência202312 explicitamente. Disco livre foi conferido antes da aquisição, superior à reserva250MiB. Este lote não mede RSS nem valida tempo/capacidade da admissão/Parquet ou da expansão histórica integral.

## Contrato técnico para a implementação dependente

1. **Escopo e fontes:** referência202312, perspectiva1005, Resumo92, somente O/C5/D/P/N1 acima, sem rede/fallback/glob. Preservar bruto, contexto real, recuperação e qualificações. Perfil202312 próprio fecha relatório/notas/bindings, schema cadastral32, hashes e comportamento do portal. Para D/N1, compatibilidade legada explícita conserva ausência do campo de truncamento e o diagnóstico de captura decodificada; exigir exatamente os hashes de corpo/manifest revistos, HTTP200/outcome ok e schema integral. Essa exceção não relaxa o perfil202412 nem aceita legados desconhecidos. Marcador de admissão registra limites, não completude de transporte inventada.
2. **Identidade/precisão:** `c0` string opaca no namespace financeiro1005, associação literal ao lexema inteiro `e`; rejeitar padding/colisão/duplicatas e mudança não contratada de tipo. Preservar tokens numéricos com Decimal exato, tipo original, `ifd/td/a/lid/fid`, source/definition/catalog pointers e hashes. Lucro usa `ifd79718→lid78187`; quantidades usam strings de`c16/c17`, sem shard extra. Não arredondar, agregar, inferir CNPJ/holding ou refazer composições Cosif.
3. **Ausências e cadastro:** preservar exatamente `c0..c31`, sem completar os seis campos202412. Grade/cobertura e observações existentes separadas; ausência de entidade/informação não gera observação financeira, NI ou zero. NA/NI/percentuais/null/vazio/zero/inválido têm estados distintos. Falha HTTP/hash/schema/área impede aceite e não vira população zero. Nenhuma exclusão acadêmica ou troca de cadastro1005 por1006.
4. **Saídas e vintage:** futura família `ifdata-financial-snapshot-202312-v1`, nomes financeiros e seleção explícita, conforme núcleo do modelo lógico. `financial-cadastro.csv` tem campos nativos202312; demais grade/observações/variáveis/diagnósticos conservam chaves e qualificações. Captura/geração não conjunta ficam separadas da referência e do `ge/v` do relatório. Lucro julho–dezembro, BRL cru inferido e escala de exibição registrados; nenhum indicador/calendário/ponte2025. Não misturar com inventário/conversor individual.
5. **Replay e aceite:** destino novo, manifest completo publicado por último após checks; nova execução offline deve reproduzir bytes/hashes e estes denominadores, preservando51protegidos e os cinco inputs. Comparar tokens/pointers e ausência de duplicatas, e repetir leitura consultável somente após futura conversão. Diagnóstico deste lote não substitui os testes/aceite da implementação.

Menor próxima entrega proposta: delimitar extensão de `bank_quality/financial.py`, perfil financeiro202312, entrada `scripts/admit-financial.py`, adapter/CLI financeiros Parquet e testes pertinentes, preservando defaults/contratos202412 e todos os individuais. Allowlist, plano, modo de execução e destinos derivados/curados/replay precisam constar da **Issue dependente ainda não publicada**; estes paths são proposta, sem implementação autorizada nesta entrega. Compatibilidade legada precisa de regressões que recusem alteração de hashes/metadados/schema e fontes de outra referência; cadastro32/38 precisa de testes que impeçam padding silencioso. Admissão e conversão podem ser subdivididas se o diff exigir. Não executar a CLI202412 trocando apenas o período.

## Limites, revisão e paralelismo

O contrato define associação/integridade dos corpos preservados, sem certificar valores econômicos, primeira publicação, vintage simultânea, comparabilidade2023/2024, pontes2025, elegibilidade temporal CVM/B3 ou método anual. Os oito vínculos históricos desconhecidos e as decisões da [Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) continuam próprios. A proposta de indicadores da [Issue14](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/14) permanece parcial; estes oito bindings não são aprovação do conteúdo final da base.

**Fronteira:** aquisição/preflight/contrato34 avançam independentemente da ponte2025 da [Issue16](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16). Pesquisa normativa2025 e recuperação/reformulação da lista original14 são frentes separáveis, mas continuam sem claim de prontidão antes de seus contratos/entradas. O próximo código202312 depende desta nota revisada e da Issue/plano próprios; não está ready por associação. O mapa2 recebe o estado confirmado ao encerrar; Project3 segue com Zec. Resultado local, revisão independente e publicação/CI/integração devem ser conferidos na Issue34/PR real, sem este texto inventar estado remoto.

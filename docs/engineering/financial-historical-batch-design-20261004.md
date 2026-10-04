# Expansão financeira nativa 2010–2026: desenho finito de lotes

Pesquisa offline da [Issue 47](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/47), no [mapa 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2), base publicada de preparação `39de52f34f8dc174c319adf2bb260eab91c4bd09`. O conteúdo aprovado é financeiro/1005, **Resumo, Ativo, Passivo e DRE oficiais, todas as variáveis disponíveis**, preservadas nativamente. A [Issue 32](historical-coverage-inventory-20261004.md) já estabeleceu a oferta; esta pesquisa percorre os catálogos congelados para fechar um inventário executável de fontes e lacunas. Não houve HTTP, nova aquisição, admissão, conversão, consulta de dados ou alteração de código. O desenho técnico abaixo é proposto; aprovação de método, amostra, identidade e interpretação acadêmica conserva autoridade própria.

O inventário contém **66 referências e 264 relatórios**, com **dez árvores distintas do conjunto de quatro relatórios**. A aquisição proposta divide o calendário em **quatro lotes**, com duas fases por lote e checkpoints por referência. A implementação futura reutiliza o reader/adapter financeiros e um registry instalado finito; não cria 66 pipelines. Oferta, aquisição, admissão e consulta são estados distintos. Os períodos 202609/202612 não aparecem nestes corpos e ficam fora da lista executável. [O/N, apêndice]

Impacto na arquitetura: uma nota técnica nova no destino existente `docs/engineering/financial-historical-batch-design-20261004.md`, sem raiz/camada, rename/delete, dados publicados ou alterações compartilhadas. [Arquitetura](../architecture.md#organização-dos-arquivos-e-pastas), [workflow](../agents/workflow.md), [glossário](../../GLOSSARY.md), [modelo lógico](../superpowers/specs/2026-10-04-logical-data-model-design.md) e [ADR 0001](../adr/0001-duckdb-parquet.md) permanecem referências. Código, perfis, aquisição e dados têm futuras Issues/allowlists próprias. Project /3 permanece com Zec.

## Fontes congeladas e método de conferência

Todos os links de endpoints abaixo identificam a fonte; nenhum foi aberto nesta pesquisa. SHA-256 de corpo/manifest, byte count e parsing JSON sem chaves repetidas foram conferidos localmente. Pointers são base zero no corpo autenticado; não identificam um eventual catálogo atualizado. Não são publicados bodies, headers, cadrows ou valores financeiros. [O/N/D312/D412/D503]

| Fonte primária | Recuperação UTC | Bytes | SHA-256 corpo | SHA-256 manifest |
|---|---|---:|---|---|
| [O: catálogo 2000–2024](https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024) | 2026-10-03T20:42:19.737446+00:00 | 13527657 | `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` | `b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7` |
| [N: catálogo 2025–2030](https://www3.bcb.gov.br/ifdata/rest/relatorios2025a2030) | 2026-10-01T02:55:33.366905+00:00 | 1649748 | `b8977d383e4ea51f56ed391571aca7af1c109b83b9c17ceef8b926841d658206` | `8ab9f7f82eed8d7103525d3fb7c64e4d5150fd17a6caf6f07a6df00bc7b3bf12` |
| [D312: info202312](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202312%2Finfo202312.json) | 2026-10-01T03:37:20.509Z | 174579 | `11a0704ec62d3123c8af2ceb7c98b545c683781e297f8a3f4d89e449122c7ee2` | `f26d028164139e20faa2094b31bab08e8fbcd1410b28bd917b406018cf2c0425` |
| [D412: info202412](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Finfo202412.json) | 2026-10-01T01:32:36.021567+00:00 | 188690 | `9c09219eeb7aa558e0ac74e32b905ba940ec00b0bc01f761b1d086aef86cca28` | `45b12d698f2b6bcaae34ebf09f8d051f7fab1e3036e27ef1a147eee979b9192e` |
| [D503: info202503 específico](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata_2025_2030%2F%2F202503%2Finfo202503.json) | 2026-10-04T18:21:19.687771+00:00 | 188690 | `b8f1c2c2dc428af21367ea0dbaf0212181f160be984d258bb0af03fbd1a4fdae` | `6ece988aa9f7ac13e116e7668b04a81e68796615837cac578debb669c967c3b3` |

Manifest O: `data/raw/financial-cadaster-202412-20261003/20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json`; N: `data/raw/expansion-discovery-20261001/20261001T025532086391Z_current_catalog_96354c8529f24aa3822eeb07c6c3a2ce.json`. D312: `data/runs/expansion-202312-20261001/raw/2026-10-01T033720509Z_202312_e1bacaca-f0b3-4c23-a40d-8defa2891ca2.json`; D412: `data/raw/discovery-20261001/20261001T013235163159Z_portal_info_202412_4b180f95c53d44d4b5f3a4444c586e20.json`; D503: `data/raw/financial-dictionary-202503-20261004/20261004T182119273855Z_dictionary_202503_1698540fbc9c452facc744f2899090ea.json`. Cada body resolve pelo `body_path` na pasta do manifest. D312 conserva captura legada com truncamento não declarado; seus hashes exatos não convertem esse estado em `false`. [Contrato 202312](financial-snapshot-202312-contract-20261004.md#índice-explícito-proveniência-e-limites-das-fontes)

A conferência seleciona a referência `dt`, o seletor `id=1005` e um único relatório por nome oficial e membership 1005 em `trel.s`, conservando nomes/listas literais. Percorre `c/sc` recursivamente, sem executar `nac`, somar filhos ou resolver nomes por IDs do período vizinho. Para cada ocorrência registra pointer, pai/filhos, `id/ip/ifd/fid/o`, folha/grupo e hash dos metadados originais. Hash de árvore = SHA-256 do JSON de `c`, UTF-8, `ensure_ascii=false`, chaves ordenadas, separadores `,`/`:`, listas na ordem fonte. Hash do conjunto = SHA-256 dessa mesma serialização da lista dos quatro hashes, em ordem Resumo/Ativo/Passivo/DRE. Hash canônico não é hash dos bytes brutos. Annotations `rp/ri/cp/ci`, `v/ge` e árvore completa têm pointers/hashes próprios; não são deduplicadas pela assinatura reduzida de scheduling. [O/N]

## Famílias estruturais e limites nativos

| Família | Referências inclusive | Qtde | IDs Resumo/Ativo/Passivo/DRE | Nós/folhas/grupos | Localizador |
|---|---|---:|---|---|---|
| F1 | 201003–201412 | 20 | 1/3/4/5 | 124/115/9 | O `/40..59` |
| F2 | 201503–201709 | 11 | 75/3/4/5 | 121/112/9 | O `/60..70` |
| F3 | 201712–201812 | 5 | 75/3/4/5 | 121/112/9 | O `/71..75` |
| F4 | 201903–201909 | 3 | 92/3/4/91 | 121/112/9 | O `/76..78` |
| F5 | 201912–202003 | 2 | 92/96/97/98 | 121/112/9 | O `/79..80` |
| F6 | 202006–202009 | 2 | 92/96/101/98 | 122/113/9 | O `/81..82` |
| F7 | 202012–202209 | 8 | 92/96/101/98 | 122/113/9 | O `/83..90` |
| F8 | 202212–202309 | 4 | 92/96/101/98 | 121/112/9 | O `/91..94` |
| F9 | 202312–202412 | 5 | 92/96/101/98 | 121/112/9 | O `/95..99` |
| F10 | 202503–202606 | 6 | 119/107/110/118 | 158/143/15 | N `/0..5` |

Essas famílias descrevem igualdade da árvore catalogada de quatro relatórios, **não regimes econômicos ou definições equivalentes**. A família F4, por exemplo, conserva Ativo3/Passivo4 e DRE91; o Resumo92 não autoriza aplicar o conjunto 202412. Campos cadastrais, tipos, origem, unidade crua, precisão e cobertura precisam de C/D/valores específicos. Uma árvore igual entre duas referências não prova dicionário ou população igual. [O/N; D312/D412/D503]

Entre **201403 e 201909**, Ativo/Passivo/DRE selecionados anunciam `s=[{id:1004},{id:1005}]`: 23 referências. O contrato futuro deve conservar a lista, selecionar 1005 e usar seu cadastro; exigir singleton1005 como em 202412 excluiria oferta financeira válida. A lista múltipla não autoriza soma/join de populações, nem admissão prudencial nesta frente. Antes/depois dessa faixa, os quatro relatórios selecionados têm lista singleton1005 nestes catálogos. [O `/56..78`, reports no apêndice]

As **264 captions `cp`** declaram apresentação monetária em R$ mil; isso não prova unidade dos lexemas de origem nem aprova um multiplicador global. As **132 annotations `rp` de Resumo/DRE** explicitam receitas/despesas janeiro–março, janeiro–junho, julho–setembro e julho–dezembro. Preservar a annotation literal em cada referência e vincular interpretação somente ao binding ao qual ela efetivamente se aplica. Junho não vira abril–junho, dezembro não vira anual, e coluna cadastral não recebe janela de receita. Unidade/janela não comprovada fica `unknown` com o motivo e a fonte disponível. Ativo/Passivo não recebem janela de fluxo por herança de Resumo/DRE. [O/N, cada `trel/cp` e `trel/rp` indicado no apêndice; contratos39/43]

`ge` está ausente em 120 metadados de relatório, e a ausência permanece explícita. Em N `/5`/202606 as quatro gerações declaradas divergem: Resumo18/08/2026, Ativo20/08/2026, Passivo28/08/2026 e DRE20/08/2026. Nenhuma geração declarada prova UTC de captura, versão do Cosif historicamente vigente ou vintage conjunta das fontes. A [ponte normativa](financial-2025-normative-bridge-20261004.md) conserva sua pergunta de comparabilidade; falta de equivalência não impede arquivamento/preservação nativa bem identificados. [O/N `ge`; contrato43]

## Corpus demonstrado e fontes ainda necessárias

| Referência | Corpo já recuperado / estado na base publicada | Origem/shard resolvido nesta pesquisa | Falta para quatro relatórios nativos |
|---|---|---|---|
| 202312 | Cinco fontes, cadastro32/1385; oito bindings de Resumo admitidos/consultáveis. [Contrato34](financial-snapshot-202312-contract-20261004.md), [execução36](financial-snapshot-202312-execution-20261004.md) | Todos121 nós encontram D312; bindings numéricos declarados apontam `a=1`. N1 é candidato já recuperado, sujeito ao contrato do conjunto completo. | Perfil e contrato completo dos112 bindings-folha, origens/lexemas/ausências/precisão; replay e gate completo. Admissão anterior não cobre Ativo/Passivo/DRE. |
| 202412 | Cinco fontes e conjunto completo implementado, admitido/consultável; cadastro38/1422,112 folhas. [Contrato39](financial-four-reports-202412-contract-20261004.md), [execução42](financial-four-reports-202412-execution-20261004.md) | D412 resolve todos121 nós;74 bindings monetários usam `a=1`; N1 já recuperado. | Serve de baseline de regressão/representante físico, sem nova aquisição implícita ou autorização transversal para outros períodos. |
| 202503 | Cinco fontes e contrato nativo119/107/110/118, cadastro38/1425,143 folhas; aquisição não é admissão. [Contrato43](financial-sources-202503-contract-20261004.md), [dicionário40](financial-dictionary-202503-execution-20261004.md) | D503 resolve todos158 nós;105 bindings monetários usam `a=1`; N1 já recuperado. | Reader/adapter/perfil, admissão/consulta/replay/gate próprios dependem da46; esta pesquisa não afirma sua implementação. |
| Outros63 períodos | Catálogo preservado; conjunto financeiro completo não demonstrado nas notas de execução examinadas. A32 registra corpos compartilhados201012, candidatos a reuso, não aceitação financeira. | `ifd`/árvore conhecidos; `td/a/lid`, schemas C/D, origem e shards necessários permanecem desconhecidos nesta conferência. | Inventário de reuso autenticado → C1005/D específicos → resolução de todas as ocorrências → valores estritamente requeridos → contrato/perfil/aceite por referência. |

Não foi lido cadastro ou shard para gerar novas contagens de população, células, precisão ou perdas. As contagens da tabela são resultados das entregas referidas na base publicada, não diagnósticos executados nesta pesquisa. Nenhum shard shared define a população: a população técnica vem do cadastro1005 específico e a associação deve preservar identificadores opacos/lexemas e ausências. Não estender exceções legadas ou a interpretação do portal de202412 sem evidência própria. [Código42 `_cadaster/_read`; contratos34/39/43]

Os anúncios de shards variam: 201003–201312 `{1,3}`; 201403–201706 `{1,3,4}`; 201709–202209 `{1,2,3,4}`; 202212–202606 `{1,2,3,4,5}`. O número máximo não implica sequência densa nem necessidade de todos. Para os63 períodos não resolvidos há **218 anúncios** de valores, limite superior finito para seleção futura, não instrução para baixar218 arquivos. Primeiro resolver D; `a` de cada folha `td=3` precisa corresponder a um arquivo anunciado exato; área ausente/incompatível bloqueia aquele binding/período. `td=1` resolve em cadastro e não exige shard; grupo não gera célula financeira. [O/N `/files`; D312/D412/D503; portal conforme contratos39/43]

## Quatro lotes, duas fases, retomada finita

**Proposta a contratar na próxima aquisição, não aquisição autorizada por esta nota.** Cada lote guarda lista explícita de referências, sourcehash do catálogo, URLs/pointers literais, roles e limites. Não há crawl, latest, refresh de catálogo, descoberta por tentativa de nomes ou download automático de `trel`: as árvores já estão embutidas nos catálogos. GET de arquivo usa `https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=<path codificado>`; o argumento é exatamente o path anunciado, incluindo `ifdata_2025_2030//` com duas barras. [O/N; aquisição43]

| Lote proposto | Lista finita | Qtde | C/D não demonstrados neste recorte | Máximo de arquivos de valores ainda não resolvidos | Teto conservador de arquivos novos / GETs com2 tentativas |
|---|---|---:|---:|---:|---|
| L1 recente | 202312–202606 | 11 | 16 | 40 | 56 /112 |
| L2 intermediário | 202012–202309 | 12 | 24 | 52 | 76 /152 |
| L3 anterior | 201503–202009 | 23 | 46 | 82 | 128 /256 |
| L4 inicial | 201003–201412 | 20 | 40 | 44 | 84 /168 |

Intervalos incluem todos os trimestres `{03,06,09,12}` até o término indicado, e a lista literal66 do apêndice é a autoridade de membros. Máximo agregado conservador: **344 arquivos /688 GETs**, antes de comprovar reuso adicional; não é previsão de tráfego. Não inclui os cinco roles já demonstrados para202312/202412/202503, seus catálogos/portal, complementares ou os dois períodos2026 não anunciados. Sob a hipótese ainda não validada de apenas um shard por cada um dos63 períodos restantes e sem reuso extra, seriam189 arquivos; essa hipótese não entra no contrato de seleção. [Derivação aritmética de O/N e corpus acima]

1. **Preflight sem rede e reuso:** confirmar catálogo/hash/pointers/selection/membros/destino novo/recursos/ownership e conferir fontes locais explicitamente indexadas. Corpo compartilhado só é reutilizável após manifest/body/schema/contexto/URL/bytes/estado de geração autenticados; manter contexto da aquisição original. Candidato, completo e reaproveitado são estados separados. Inventário de reuso atualiza a lista faltante e reduz orçamento antes do primeiro GET; não é busca implícita em outro projeto. [Contratos34/39/43]
2. **Fase A — C/D:** recuperar somente cadastro1005 e info específicos ainda faltantes, em loops finitos e budgets por arquivo/role; validar transporte e arquivar antes de interpretar. Conferir C nativo sem padding, D sem duplicateIDs, cada nó/binding e annotation. Gerar ledger completo: origem `td/a/lid`, definitionpointer/hash, campo cadastral ou arquivo-shardpointer, grupos, unidade/janela conhecida ou `unknown` e conjunto faltante. Alteração de schema/catálogo não recebe fallback de perfil vizinho. [O/N/D; Código42]
3. **Checkpoint A:** fixar o índice finito de shards requeridos por referência e reduzir/confirmar budget. Fonte fora dos anúncios ou papel fora do contrato volta ao escopo; não expandir endpoints silenciosamente. Ausência de origem não equivale a ausência de valor financeiro e impede anúncio de readiness de admissão completa. [Proposta motivada pela associação específica em39/43]
4. **Fase B — valores:** adquirir somente shards requeridos e faltantes; um corpo pode servir a várias folhas/reports da mesma referência sem deduplicar suas ocorrências. Validar framing/hash/schema/identificadores e preservar ausências. Cada referência ganha receipt de aquisição separado; falha bloqueia apenas dependentes, sem converter parcial em conjunto aceito. [Código42/contratos39/43]
5. **Handoff offline:** conjunto completo de inputs autenticados, bindings resolvidos e desconhecidos qualificados → contrato/perfil instalado/revisão → admissão/conversão/query/replay/gate. Uma tranche pode fechar a aquisição sem admissão implementada. Finalizar os66 snapshots exige aceite próprio para cada referência, não repetir o pipeline manualmente66 vezes. [Workflow; arquitetura]

Budgets propostos e configuráveis na futura Issue: no máximo2 tentativas sequenciais por arquivo, **5MiB acumulados** para cadastro ou dicionário e **64MiB acumulados** por shard requerido, somando tentativas completas/parciais. Timeout de rede30s, deadline duro120s por tentativa, nenhum redirect; `Accept-Encoding: identity`. Limites conservam a escala dos orçamentos da40/43, mas tamanhos históricos são desconhecidos e atingir o teto não autoriza aumentá-lo em silêncio. Tetos agregados conservadores dos quatro lotes são2640/3448/5478/3016MiB de corpos; teto global14582MiB, excluindo manifests/eventos/derivados/replay/scratch. São limites de falha, não estimativas de armazenamento ou RAM. Budget/deadline global do lote derivam da lista exata e são registrados antes de executar. [Aquisição40/43; aritmética dos anúncios]

EOF/framing têm guarda positiva: HTTP200, URL final exata, estado completo sem truncamento, bytecount/hash, EOF confirmado e `Content-Length` coerente quando presente. Comprimento ausente não vira zero; preservar esse estado e exigir conclusão comprovada pelo framing/EOF usado. JSON válido sozinho não prova transporte completo. Se o cap for atingido sem EOF comprovado, recusar aceite. Streaming em chunks contabiliza bytes observados enquanto grava destino temporário exclusivo e calcula hash; preserva erro/parcial/UTC/status/URLs/parâmetros/diagnóstico e headers privados. A aquisição legada `archive.fetch` publicada lê até64MiB+1 e segue redirects padrão; **não satisfaz por si este desenho de guardas**. Reutilizar a responsabilidade de arquivo/proveniência, implementando/testando a guarda limitada em uma Issue de código própria; não afirmar API pronta. [Código `archive.py:17–63`; correção de framing43]

Retry somente da classe explicitamente contratada de falha transitória, sem reclassificar schema/hash/redirect/EOF inválido como sucesso. Proposta de failurebudget: parar novo agendamento do lote após três arquivos terminarem sem aceite, ou duas falhas consecutivas da mesma guarda; timeout/memória de pipeline fecha primeiro o diagnóstico do estágio. Tentativas já iniciadas concluem/encerram dentro de seus budgets e preservam receipt. Recomeçar somente membros pendentes com orçamento restante ou um contrato de execução revisto, sem reset oculto de contadores. [Escolha técnica proposta; falhas documentadas em42/43]

Checkpoint aceita somente fonte completa autenticada; cada tentativa usa novo nome/destino, e a mesma URL com bytes novos é outra recuperação/vintage. Reinício confere receipts/hashes de fontes completas e mantém falhas para diagnóstico; não concatena fragmentos de rede ou modifica manifest antigo. Manifests finais de admissão/Parquet ficam para seus estágios, escritos por último em destinos novos. Destinos candidatos `data/raw/financial-historical-<lote>-<execução>/`, `data/derived/financial-historical-<lote>-<execução>/`, `data/curated/financial-historical-<lote>-<execução>/` precisam de allowlist/impacto na arquitetura na futura Issue. Não sobrescrever os snapshots aceitos ou mover corpos para organizar pastas. [Arquitetura; Código42 `admit/convert_financial`]

## Registry instalado e reuso do mecanismo publicado

O reader publicado `bank_quality/financial_reports.py` e o adapter `financial_reports_parquet.py` são focados e fechados em202412. `_context` fixa cadastro38, área1 e regras de binding desse perfil; `_read` exige índice de cinco fontes e compara estrutura/proveniência; `_cadaster` exige38, referência202412 e código opaco único. O perfil legado202312 de oito métricas tem32, em outro contrato. Não basta trocar `period`/report IDs em caller, nem aplicar D412 como proxy. [Código42: `_context` linhas80–119, `_cadaster`146–154, `_read`203–255; perfil instalado202412; execução36]

Código primário inspecionado na base publicada: [reader](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/39de52f34f8dc174c319adf2bb260eab91c4bd09/bank_quality/financial_reports.py), SHA-256 do blob `9af062a55fb740976614a6f7507e21b9f3df5d69be0a404d30334971db110459`; [adapter](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/39de52f34f8dc174c319adf2bb260eab91c4bd09/bank_quality/financial_reports_parquet.py), `60f729fc8b157e955aaea86b0046a1679f17e1ef54da24cb4b8ad1784e17e607`; [perfil42](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/39de52f34f8dc174c319adf2bb260eab91c4bd09/bank_quality/financial-reports-profile-202412.json), `e2423c9299caae81b02c7c95c6a57903457bb90fadccfe50f50f2e62b28c35ab`; [archive](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/39de52f34f8dc174c319adf2bb260eab91c4bd09/bank_quality/archive.py), `69b51682a69f2d893a2b2680f8bd0bca51bbf0b136f6cfda1c2c155712a72f5b`. Hashes são dos bytes retornados por `git show`, sem depender das alterações concorrentes do working tree.

Proposta: evoluir os mesmos módulos responsáveis para carregar uma **lista instalada finita de66 seleções** revisadas, cada uma com namespace, período, perspectiva 1005, quatro IDs exatos, reportmetadata/árvore/annotations, schemaC, bindings/definitionpointers/origens, semântica conhecida ou desconhecida explícita, sourcepins e digest da projeção de proveniência. Objetos de árvore realmente idênticos podem ser internados em dez famílias; diferenças de D/C/proveniência/annotations continuam nos registros próprios. Pode-se organizar registry e artefatos de perfil por lote/família, com allowlist futura em `bank_quality/`; não criar um arquivo de pipeline por trimestre. Um compilador offline pode produzir candidatos a partir dos inputs autenticados, mas runtime não aceita perfil arbitrário passado pelo usuário, catálogo latest ou seleção não instalada. [Escolha técnica; princípios de `_context/_check_sources`; arquitetura]

A lista múltipla de perspectivas deve ser validada exatamente contra o perfil aprovado, com membership1005 separado do seu cadastro. A origem de cada binding pode exigir áreas distintas: generalizar somente após D próprio comprovar suporte e arquivo/pin; não manter `area==1` como verdade universal nem relaxar para qualquer número. Tipos/fieldsC também vêm de fonte específica. `unknown` de unidade/janela/interpretação pode ser preservado nativamente com annotation e limite explícitos; origem física sem resolução impede produzir células por adivinhação. [O multi-perspectiva; D312/D412/D503; Código42]

A grade textual permanece autoritativa. Per-binding DECIMAL exato é reutilizável como mecanismo após profiling de cada corpus, sem presumir larguras202412/202503. `financial_reports_parquet._decimal_type` recusa largura>38; grade textual permite preservar lexema/estado quando novo binding ainda não tem projeção exata suportada, mas isso exigirá contrato/revisão explícitos, sem fallback silencioso. Manter nós de grupo, chaves de ocorrência e nomes nativos; não somar filhos, deduplicar `lid` entre relatórios, gerar uma coluna numérica histórica global ou UNION que reduza escala. [Código adapter42 linhas66–91; contratos39/43]

Essa proposta não declara46 integrada, runtime histórico implementado, cadastro temporal resolvido ou consulta multissnapshot pronta. Abertura publicada autentica e materializa um snapshot em memória; uma consulta histórica conjunta exige contrato de persistência/capacidade próprio, sem reter66 snapshots abertos como efeito colateral. [Código adapter42 `snapshot_connection/_open_snapshot`; arquitetura]

## Capacidade por máquina e critérios positivos de conclusão

Aquisição e etapas de parsing/admissão/conversão/query têm pools e limites separados. Inicializar cada classe com um worker no diagnóstico representativo; medir depois de fixtures offline e antes de gate real, com recursos livres observados, disco, working set/commit da árvore própria, CPU, wall, saída/scratch/replay e deadlines. Na42, o ciclo202412 mediu peaks agregados de aproximadamente537MB na admissão,799MB de commit na conversão e814MB de working set na query; budgets768MiB e1GiB pertenciam àquele host/estágio. Na43, preflight mediu aproximadamente463MB de working set agregado, sem DuckDB/Parquet. Esses números não são teto universal nem prova de concorrência/histórico. [Ledgers42/43, seções de capacidade]

Proposta de dimensionamento: escolher por host uma reserva para SO/apps/monitor/cache e uma margem explícita sobre o pico representativo de cada classe; admitir uma combinação de workers somente se soma dos envelopes cabe na RAM/commit disponível, disco/scratch e limites deCPU/I/O/rede. Antes de subir workers, medir um par pequeno de referências independentes com destinos/ownership separados e comparar o agregado; leitura/parsing de um mesmo corpo compartilhado não deve duplicar buffers sem necessidade. Mais RAM pode permitir mais workers; o host fraco começa com um e não fixa limite de outras máquinas. Ajustar recursos é decisão técnica registrada com evidência. [Proposta técnica sob autonomia; problemas de buffers/retenção documentados42]

Não concorrer com um gate pesado ainda em curso na46 antes de reavaliar recursos. Contratos independentes podem ser pesquisados/revisados em paralelo; execução de rede ou pipeline depende da autorização/ownership/recursos e do checkpoint correspondente. Pools não escrevem mesma fonte/destino/manifest, registry/sharedcallers ficam com único integrador; aquisição de lote completo não libera automaticamente admissão de perfil ausente. [Workflow; contrato da47]

| Estado | Evidência positiva exigida | O que não prova |
|---|---|---|
| Ready de pesquisa/desenho | Contrato47, O/N autenticados, código/base e destinos disponíveis | Autorização para nova coleta |
| Ready de aquisição | Issue própria, membros/GETs/roles/bytes/deadline/failurebudget/reuse/novo destino/ownership/recursos e catálogo fixados; FaseB depende de D/origens | Ausência de labelblocked, igualdade de árvore ou perfil202412 |
| Adquirido completo | Todos inputs necessários do período com framing/hash/receipt e schema validados; missing set vazio | População elegível, equivalência econômica ou admissão |
| Ready de admissão | Contrato/perfil instalado revisto, todas origens resolvidas e unknown semântico qualificado, fontes/pins completos e capacidade inicial medida | Dicionário de período vizinho ou fontes apenas anunciadas |
| Admitido/consultável/replay | Toda grade/origem/estado/pointer/lexema verificados, tipos próprios exatos conforme contrato, manifest externo autenticado, queries porbinding/reconstrução/replay em destinos novos e gate completo | Indicadores/amostra acadêmica, harmonização ou capacidade de66aberturas |
| Integrado | Revisão independente do head/allowlist/arquitetura, checks pertinentes, publicação/merge/CI confirmados na Issue | Nota local ou revisão apenas prevista |

Os próximos contratos podem concentrar aquisição de C/D e shardlists dos quatro lotes em uma entrega finita, reutilizar a46 depois de handoff para o registry/reader/adapter, e admitir lotes offline com checks por referência. Não são necessários66 tickets/pipelines para repetir mecânica; mudanças excepcionais de schema/origem/precisão recebem recorte específico. A46 e esta pesquisa têm paths compatíveis; desenho offline pode avançar enquanto ela trabalha, mas novo caller/perfil precisa do handoff/revisão e nova coleta precisa de contrato próprio. Atualização da fronteira real no mapa2 pertence ao integrador; nenhuma prontidão remota é declarada por este documento. [Workflow/contrato47; proposta técnica]

## Verificação e limites da entrega

Conferidos dois catálogos, três dicionários específicos e código publicado via `git show 39de52f:<path>`, com hashes; parsing estrito,66 `dt` únicos,264 seleções únicas,66cadastros1005/66info anunciados, todos nós/pointers/árvores/annotations, dez famílias e resumo dos lotes. São conferências de integridade/metadados, sem teste que espelhe prosa, execução de pipeline ou validade acadêmica. Matriz machine-readable privada conserva inventário completo, bindings/origens conhecidas e `null` para desconhecidos; reviewer dispõe dessa matriz e do extrator offline reproduzível. A nota pública conserva a enumeração66 a seguir. Revisão independente/publicação/checks/merge ainda devem ser registrados pelo integrador na47. [Procedimento offline desta pesquisa; fontes acima]

Permanecem desconhecidos fora dos corpos/contratos específicos: schemas/hashes futuros C/D/shards, população/cobertura/precisão/tempos por referência, causa econômica/normativa de cada fronteira, unidade crua e interpretação por binding histórico, vintage conjunta e equivalência entre regimes. São lacunas distintas: origem física precisa ser resolvida para leitura; interpretação pode permanecer qualificada como desconhecida na preservação nativa. O objetivo financeiro não autoriza harmonização, complementar prudencial/individual, associação acadêmica de holdings, amostra/indicadores ou aquisição dos dois períodos2026 não anunciados. [Fontes e contratos citados; arquitetura]

## Apêndice: todas as66 referências e pointers

Cada célula de report usa `id@f`, com pointer `/{q}/files/{f}/trel` no catálogo O ou N da linha. C/I são índices de `cadastro{p}_1005.json`/`info{p}.json`, pointer `/{q}/files/{f}/f`; os nomes de valores são `dados{p}_{shard}.json`. Para O, prefixo literal `ifdata/{p}/`; para N, `ifdata_2025_2030//{p}/`. Cada reportfile é `trel{p}_{id}.json`, anunciado sob o mesmo prefixo. O hash H aponta ao conjunto das quatro árvores na ordem da tabela, pelo algoritmo canônico descrito acima. Os hashes não incluem D/C/valores ou validam comparabilidade. [O/N]

| H | SHA-256 do conjunto de árvores |
|---|---|
| H1 | `6ff51af868b07dc4dbf1ba1be4fe1a9181800e3fba5a0e43fb836fc327437916` |
| H2 | `13bd893c8992b61924dd7c1f95057d4411a25b9cd7057f8971ee1b5e876ac4d0` |
| H3 | `cc9e19681f12537a4903c3e5d61a5a37f5b2dc3d2542e95b0e414ea7b9cafbce` |
| H4 | `a438c938a882ff679a7cfbfe1e0408a2cd41ad9b7badcb52e2ecfad990834781` |
| H5 | `514a741f3552cd7bc2bd7f4dec8bb6bea7ca603ca93999a98832870c46ee1e4b` |
| H6 | `b47a0431d7dc7a15c8d8ef3ca026f50721594ba5599ddf25b1787fe6e4660aea` |
| H7 | `c2e6415a7ee5e20de06173dd11e16179cd43694fcde808d8261977a069a8ea68` |
| H8 | `0aa894a3802ce60b6e391002231b24fb76a795320a5cc646cc50b43ca982185b` |
| H9 | `5906d637613a4f03a1f1056865c3c7bac63a218c0a105f4910f11189a7232a8f` |
| H10 | `76181557c001321ca0749cdf8cc6ac72160ba97f52a3448e048216dd60e26b54` |

| Período | Catálogo/q | Resumo | Ativo | Passivo | DRE | C/I | Shards anunciados | Necessários | H |
|---|---|---|---|---|---|---|---|---|---|
| 201003 | O/40 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201006 | O/41 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201009 | O/42 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201012 | O/43 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201103 | O/44 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201106 | O/45 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201109 | O/46 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201112 | O/47 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201203 | O/48 | 1@7 | 3@8 | 4@9 | 5@10 | 0/5 | 1,3 | unknown | H1 |
| 201206 | O/49 | 1@8 | 3@9 | 4@10 | 5@11 | 0/6 | 1,3 | unknown | H1 |
| 201209 | O/50 | 1@8 | 3@9 | 4@10 | 5@11 | 0/6 | 1,3 | unknown | H1 |
| 201212 | O/51 | 1@8 | 3@9 | 4@10 | 5@11 | 0/6 | 1,3 | unknown | H1 |
| 201303 | O/52 | 1@8 | 3@9 | 4@10 | 5@11 | 0/6 | 1,3 | unknown | H1 |
| 201306 | O/53 | 1@8 | 3@9 | 4@10 | 5@11 | 0/6 | 1,3 | unknown | H1 |
| 201309 | O/54 | 1@8 | 3@9 | 4@10 | 5@11 | 0/6 | 1,3 | unknown | H1 |
| 201312 | O/55 | 1@8 | 3@9 | 4@10 | 5@11 | 0/6 | 1,3 | unknown | H1 |
| 201403 | O/56 | 1@10 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H1 |
| 201406 | O/57 | 1@9 | 3@10 | 4@11 | 5@12 | 1/7 | 1,3,4 | unknown | H1 |
| 201409 | O/58 | 1@9 | 3@10 | 4@11 | 5@12 | 1/7 | 1,3,4 | unknown | H1 |
| 201412 | O/59 | 1@10 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H1 |
| 201503 | O/60 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201506 | O/61 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201509 | O/62 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201512 | O/63 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201603 | O/64 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201606 | O/65 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201609 | O/66 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201612 | O/67 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201703 | O/68 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201706 | O/69 | 75@24 | 3@11 | 4@12 | 5@13 | 1/8 | 1,3,4 | unknown | H2 |
| 201709 | O/70 | 75@25 | 3@12 | 4@13 | 5@14 | 1/9 | 1,2,3,4 | unknown | H2 |
| 201712 | O/71 | 75@25 | 3@12 | 4@13 | 5@14 | 1/9 | 1,2,3,4 | unknown | H3 |
| 201803 | O/72 | 75@25 | 3@12 | 4@13 | 5@14 | 1/9 | 1,2,3,4 | unknown | H3 |
| 201806 | O/73 | 75@25 | 3@12 | 4@13 | 5@14 | 1/9 | 1,2,3,4 | unknown | H3 |
| 201809 | O/74 | 75@25 | 3@12 | 4@13 | 5@14 | 1/9 | 1,2,3,4 | unknown | H3 |
| 201812 | O/75 | 75@25 | 3@12 | 4@13 | 5@14 | 1/9 | 1,2,3,4 | unknown | H3 |
| 201903 | O/76 | 92@29 | 3@11 | 4@12 | 91@28 | 1/9 | 1,2,3,4 | unknown | H4 |
| 201906 | O/77 | 92@29 | 3@11 | 4@12 | 91@28 | 1/9 | 1,2,3,4 | unknown | H4 |
| 201909 | O/78 | 92@29 | 3@11 | 4@12 | 91@28 | 1/9 | 1,2,3,4 | unknown | H4 |
| 201912 | O/79 | 92@29 | 96@33 | 97@34 | 98@35 | 1/9 | 1,2,3,4 | unknown | H5 |
| 202003 | O/80 | 92@29 | 96@33 | 97@34 | 98@35 | 1/9 | 1,2,3,4 | unknown | H5 |
| 202006 | O/81 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H6 |
| 202009 | O/82 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H6 |
| 202012 | O/83 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H7 |
| 202103 | O/84 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H7 |
| 202106 | O/85 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H7 |
| 202109 | O/86 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H7 |
| 202112 | O/87 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H7 |
| 202203 | O/88 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H7 |
| 202206 | O/89 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H7 |
| 202209 | O/90 | 92@29 | 96@33 | 101@12 | 98@34 | 1/9 | 1,2,3,4 | unknown | H7 |
| 202212 | O/91 | 92@30 | 96@33 | 101@13 | 98@34 | 1/10 | 1,2,3,4,5 | unknown | H8 |
| 202303 | O/92 | 92@30 | 96@33 | 101@13 | 98@34 | 1/10 | 1,2,3,4,5 | unknown | H8 |
| 202306 | O/93 | 92@30 | 96@33 | 101@13 | 98@34 | 1/10 | 1,2,3,4,5 | unknown | H8 |
| 202309 | O/94 | 92@29 | 96@32 | 101@12 | 98@33 | 0/9 | 1,2,3,4,5 | unknown | H8 |
| 202312 | O/95 | 92@29 | 96@32 | 101@12 | 98@33 | 0/9 | 1,2,3,4,5 | 1 | H9 |
| 202403 | O/96 | 92@29 | 96@32 | 101@12 | 98@33 | 0/9 | 1,2,3,4,5 | unknown | H9 |
| 202406 | O/97 | 92@29 | 96@32 | 101@12 | 98@33 | 0/9 | 1,2,3,4,5 | unknown | H9 |
| 202409 | O/98 | 92@29 | 96@32 | 101@12 | 98@33 | 0/9 | 1,2,3,4,5 | unknown | H9 |
| 202412 | O/99 | 92@28 | 96@31 | 101@12 | 98@32 | 0/9 | 1,2,3,4,5 | 1 | H9 |
| 202503 | N/0 | 119@21 | 107@13 | 110@16 | 118@20 | 0/9 | 1,2,3,4,5 | 1 | H10 |
| 202506 | N/1 | 119@21 | 107@13 | 110@16 | 118@20 | 0/9 | 1,2,3,4,5 | unknown | H10 |
| 202509 | N/2 | 119@21 | 107@13 | 110@16 | 118@20 | 0/9 | 1,2,3,4,5 | unknown | H10 |
| 202512 | N/3 | 119@21 | 107@13 | 110@16 | 118@20 | 0/9 | 1,2,3,4,5 | unknown | H10 |
| 202603 | N/4 | 119@21 | 107@13 | 110@16 | 118@20 | 0/9 | 1,2,3,4,5 | unknown | H10 |
| 202606 | N/5 | 119@21 | 107@13 | 110@16 | 118@20 | 0/9 | 1,2,3,4,5 | unknown | H10 |

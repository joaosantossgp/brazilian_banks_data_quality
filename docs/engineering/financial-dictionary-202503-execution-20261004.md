# Dicionário específico IF.data 202503 — execução de 2026-10-04

[Issue 40](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/40), recorte da [Issue 16](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16), sob o [goal e conteúdo financeiro aprovados no mapa 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2). Base `588c9218b12a64898cf8db126d983eff01f0feb6`, branch `codex/financial-four-reports-contracts`. Resultado local disponível; revisão independente, PR, checks e integração têm autoridade na Issue real. Nota única no destino canônico `docs/engineering/`, sem mudança de runtime, código, camada ou raiz.

## Fonte, orçamento e recuperação

O catálogo 2025–2030 já arquivado anuncia literalmente `/0/files/9/f = ifdata_2025_2030//202503/info202503.json`. O namespace e as duas barras foram preservados no parâmetro, sem normalizar ou tentar outro endereço. A guarda pré-rede recusou o path inicialmente presumido `ifdata/202503/info202503.json`; **nenhuma requisição** usou esse path. A correção técnica foi registrada na Issue antes da coleta.

URL consultada: [dicionário específico 202503](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata_2025_2030%2F%2F202503%2Finfo202503.json). Somente esse GET foi autorizado nesta Issue; nenhum catálogo, cadastro, portal, shard de valores, login ou POST foi adquirido. A perspectiva 1005 e quatro relatórios contextualizam o uso pretendido; o arquivo de definições é compartilhado, não uma população financeira admitida.

| Controle ou medida | Registro |
|---|---|
| Orçamento | Até 2 tentativas sequenciais, 5 MiB agregados de corpos, deadline duro de 120 s por tentativa / máximo 240 s, timeout de rede 30 s, sem redirects |
| Execução | 1 tentativa, HTTP 200, `outcome=ok`, URL final igual à pedida, `truncated=false`, diagnósticos vazios |
| Duração / corpo | 0,391 s / 188.690 bytes |
| Recuperação UTC | `2026-10-04T18:21:19.687771+00:00` |
| SHA-256 do corpo | `b8f1c2c2dc428af21367ea0dbaf0212181f160be984d258bb0af03fbd1a4fdae` |
| SHA-256 do manifest | `6ece988aa9f7ac13e116e7668b04a81e68796615837cac578debb669c967c3b3` |
| Preservação | 78 arquivos protegidos, hashes anteriores/finais iguais |

Executor privado reutiliza as guardas da aquisição 34, adaptando apenas seleção, destino, catálogo e contexto. Fixtures locais verificaram corpo completo, redirect recusado e corpo parcial limitado/preservado; não fizeram requisições IF.data. Cada tentativa preserva URL/parâmetros, método, status, headers, diagnósticos, corpo, SHA-256 e UTC; falha/partial não vira população zero. Pasta nova ignorada `data/raw/financial-dictionary-202503-20261004/`, manifest `20261004T182119273855Z_dictionary_202503_1698540fbc9c452facc744f2899090ea.json`, com `body_path` relativo. Corpo e headers permanecem privados, sem sobrescrever originais.

Catálogo de referência: [2025–2030](https://www3.bcb.gov.br/ifdata/rest/relatorios2025a2030), corpo SHA-256 `b8977d383e4ea51f56ed391571aca7af1c109b83b9c17ceef8b926841d658206`, recuperado `2026-10-01T02:55:33.366905+00:00`; manifest SHA-256 `8ab9f7f82eed8d7103525d3fb7c64e4d5150fd17a6caf6f07a6df00bc7b3bf12`. Pointers a seguir usam índices JSON de base zero nesses corpos congelados, não um endpoint futuro.

## Integridade, definições e relatórios

UTF-8 e JSON com rejeição de chaves repetidas; lista com **776 definições e IDs inteiros únicos**, cada objeto com `a,d,di,id,lid,n,ni,td,ty`. Report e definição são entidades distintas. A árvore `c/sc` foi percorrida integralmente: nós de grupo não viram células numéricas por associação.

| Relatório financeiro 1005 | Pointer no catálogo | Colunas de topo | Nós recursivos | TD cadastral / grupo / numérico |
|---|---|---:|---:|---|
| Ativo 107 | `/0/files/13/trel` | 20 | 37 | 9 / 4 / 24 |
| Passivo 110 | `/0/files/16/trel` | 16 | 34 | 9 / 3 / 22 |
| DRE 118 | `/0/files/20/trel` | 18 | 69 | 9 / 8 / 52 |
| Resumo 119 | `/0/files/21/trel` | 18 | 18 | 11 / 0 / 7 |
| Total de ocorrências | Quatro árvores | 72 | 158 | 38 / 15 / 105 |

As 158 ocorrências referenciam **131 IDs de definição distintos**, todos encontrados; todas têm área declarada 1 no dicionário. TD 1/2/3 e área são códigos da fonte: área 1 não transforma atributo cadastral em saldo monetário, e TD 2 conserva estrutura de grupo. O preflight não executou JavaScript `nac`, não somou filhos e não gerou admissão, cobertura populacional ou Parquet. Bindings, pais/filhos, objetos de definição e pointers completos ficam no receipt privado reexecutável.

Catálogo reporta geração `17/04/2026`, versão `1` para esses relatórios. O dicionário recuperado não declara uma geração equivalente: `source_generation_state=unknown`. A nota do DRE delimita, para março, resultado acumulado janeiro–março; janelas de outros trimestres seguem as notas próprias, sem anualizar dezembro. O corpus de metadados não prova unidade/escala/perímetro de cada valor ou versão conjunta com cadastro/shards ainda não adquiridos.

## Comparação limitada com o proxy anterior

O [dicionário info202412 arquivado](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2Finfo202412.json), SHA-256 `9c09219eeb7aa558e0ac74e32b905ba940ec00b0bc01f761b1d086aef86cca28`, também contém 776 IDs. Não há IDs adicionados/removidos neste par recuperado. **772 objetos de definição são idênticos por ID**; os IDs 79645, 79647, 79652 e 79655 diferem no campo `a`. Nenhum desses quatro integra as 131 definições dos quatro relatórios financeiros selecionados: todos os objetos usados por eles coincidem integralmente entre os dois corpos. Os corpos completos têm hashes distintos.

Essa igualdade documental explica por que o proxy anterior já continha definições novas, mas não o promove a fonte específica 202503. A recuperação própria remove a lacuna de entrada atual; **não certifica vintage histórica, continuidade monetária, funções das rubricas ou regras de mensuração**. Não comparar automaticamente AA–H/estágios nem transportar normas posteriores para 202503. A [nota normativa 37](financial-2025-normative-bridge-20261004.md) continua válida quanto às demais lacunas e versões.

## Verificação e próximos requisitos

Dois preflights offline em destinos privados novos reconferiram corpo/manifest/catalog/proxy, estrutura/IDs/árvores/pointers e 78 protegidos. Conteúdo determinístico reproduzido; durações pontuais 0,156 s e 0,188 s, sem RSS ou benchmark integral. Nenhuma suíte de software foi repetida para esta nota: não houve mudança de código de produto; fixtures do executor, hashes e conferência semântica são as verificações pertinentes. Evidência privada em `.superpowers/sdd/financial-four-reports-20261004/dictionary202503/`; clones públicos não contêm os inputs.

Resultado local é **fonte específica e preflight de metadados**, não snapshot sanitizado de valores. Faltam cadastro 202503/1005, shards necessários, contrato de leitura/admissão/consulta, aceite de capacidade e validação das definições de unidade/janela/perímetro por variável; equivalências entre regimes exigem prova e decisão metodológica próprias. A Issue 16 continua sem aceite amplo. A [Issue 39](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/39) contrata os quatro relatórios 202412 em paralelo, com nota/ownership separados. Project /3 continua com Zec.

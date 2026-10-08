# Catálogo financeiro — execução e limites

Issue: [#61](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61), [spec](../superpowers/specs/2026-10-06-financial-catalog-design.md), [plano](../superpowers/plans/2026-10-06-financial-catalog.md), [PR draft71](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/71).

## Entrada e responsabilidade — 2026-10-08

Base main `c7455f06ff2dc52a7958e300b19df01bca9b92c7`; contrato documental revisado no commit `bb77f67aabf99164ccc19b3a4282112f1daa94b7`. Root assumiu implementação no [claim61](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61#issuecomment-6061550752), na branch `codex/financial-catalog`. Arquitetura registra o módulo adjacente antes do código; allowlist de nove arquivos consta no claim/plano. Refs das 11 autoridades são preparação autenticada, não software ou final66.

Skills usadas: executing-plans e test-driven-development. Ruling: a exigência humana de revisões parciais e o plano desta Issue prevalecem sobre a orientação genérica da skill inline de uma única revisão no final. Root implementa; revisão independente por checkpoint antes de ampliar, além da revisão final de composição. PR tem tamanho livre.

## Checkpoint de integridade de metadata

Testes sintéticos em diretório temporário próprio. RED observado: módulo ausente, import error, exit1. Implementadas captura de bytes com hash externo, limite de tamanho, JSON sem keys duplicadas ou não finitos, schema/inteiro estritos, serialização determinística e paths canônicos/contidos sem symlink/reparse. Imagem capturada conserva bytes e reconstrói JSON sem dicionário mutável compartilhado.

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_financial_catalog.py -v
```

Resultado local: 13 testes, exit0, 0,103s, dois skips de symlink porque Windows negou sua criação (WinError1314). Fixture real de junction não exige esse privilégio: criação exclusiva, rejeição de diretório/root reparse, remoção apenas do link e preservação do arquivo alvo passaram. Não declarar cobertura nativa dos dois skips; a CI Ubuntu poderá executar symlink.

RAM livre no claim:1.323.956KiB física e5.496.472KiB virtual. Testes somente stdlib/metadata, sem DuckDB ou corpus. Medir novamente antes de consulta pesada; essa observação não libera gate de recursos59 ou orçamento global.

O checkpoint não implementa parser de autoridades, criação/listagem do catálogo, resolução, CLI ou consultas. Não autentica novos aceites a partir de `accepted:true` e não faz coleta/replay. Próximos checkpoints do plano implementam esses contratos; final66 depende dos55 aceites60.

Revisão parcial identificou P2: o root podia ser um diretório normal sob um ancestral junction. A checagem somente do root/descendentes aceitava esse redirecionamento anterior. Acrescentada regressão real Windows para root abaixo de junction; RED observado (CatalogError não levantado, exit1), corrigida a inspeção de todos os ancestrais até a raiz do filesystem e GREEN13testes/exit0, mantendo os dois skips de symlink. A regressão equivalente sob symlink executará onde houver privilégio. Não alterar proteções nem presumir que esses skips passaram.

Revisão focal da correção concluída APP antes de ampliar ao parser; resultado local/revisão não são integração/publicação confirmadas. Dados aceitos, perfis/registry/readers/adapters/pipeline/requirements e proteções não foram modificados. Gate Windows59 continua pendente.

## Parser das três autoridades históricas

Base do checkpoint: `f761ebf8ca50a1bc15003d51e778bb841d70193a`. Handoff possui campos fechados e seleção com quatro IDs inteiros/únicos; shape válido não produz aceite. Tipos desconhecidos e futuros60 são rejeitados. O parser histórico limita-se a202312/202412/202503, baseGit externa c745, manifests exatos da tabela confiável, perfil físico/nativo, índice fonte, admissão/Parquet/embedded/replays e transporte/ledger. Código capturado é somente AST/literal, nunca executado. 202312confere também schemas originais fechados, contagens, typedviews/precisão/accessor e comparação;42/46mantêm etapas ausentes explicitamente.

RED funções ausentes observado; GREEN inicial20testes. Revisão parcial detectou refs de proof sem shape prévio e pin singularCRLF do código; acrescentados testes causaisRED→GREEN. Agora somente os dois pins físicos CRLF/LF da imagem Git confiávelc745 são admitidos, com captura/hash externo antes do AST e coincidência normalizada com GitLF. Isso não normaliza financeiro/manifests/receipts/fontes ou certifica portabilidade integral. Perfis instalados e fontes históricas conservam seus regimes/pins próprios.

Resultado focal final:22testes/exit0,0,122s,dois skips de symlinkWindows. Verificação real read-only dos três wrappers pinados (`3f97546b7ed0103d7a9ee456db00d364a0459fe11d37310ffbb02b7ea71aa87c`) reconheceu três aceites históricos e preservou `available` para202312/`absent_from_transport` para42/46; captura13/10/10imagens metadata. Variações do wrapper202412 com stage inventado, pin primário alternativo e ref de replay malformada foram rejeitadas como integrity. Nenhum Parquet/payload/query/replay/GET executado. A etapa não implementa403/57, builder, listagem, seleção/CLI ou consultas; essas partes continuam no plano. Revisão final do recorte concluída APP antes de ampliar.

## Checkpoint das autoridades 202403 e pipeline57

Base do recorte: `2502444b6f89fc16ccf463ef9eb153aa199a73a0`; [observação e escopo na Issue61](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61#issuecomment-6062163941). O suplemento202403 exige seu pin exato e oito referências autenticadas. O pipeline57 exige os pins reais de plan/result/head, membro único, sete receipts e seus artefatos/outputs; a autoridade do journal é conferida pela API existente `read_status`, somente leitura de metadata. Perfis instalados usam a política nativa LF explicitamente limitada a seus paths; a imagem capturada conserva o hash físico. Manifests, receipts e dados não recebem normalização.

RED observado com handlers ausentes; GREEN focal:24testes,exit0,0,146s,dois skips de symlinkWindows. Observação dos oito wrappers reais:202403 e sete membros57 reconhecidos,10/47imagens por membro,exit0,4,875s. Nenhuma nova query, replay, leitura de payload ou coleta foi executada.

Revisão independente parcial concluída APP, sem achados bloqueantes; `git diff --check` passou. A aprovação cobre o parser deste recorte, antes de ampliar para builder/descoberta. O builder deverá congelar também a autoridade do journal e fechar o inventário dos companions, para que a listagem histórica não dependa da sobrevivência da coordenação externa. Builder, descoberta, CLI/consultas, autoridade futura60 e aceite final das66 referências permanecem fora desta aprovação.

A PR pode conter toda a entrega. Os checkpoints são revisões e testes durante a implementação, com correções antes de ampliar o trecho e revisão final da composição; não são limites de tamanho ou obrigação de dividir PRs.

## Checkpoint de entradas, registry congelado e escolha ativa

Base `360fec49b332e0a9c5427883cb76dd4e9d830f30`. Sete novos testes falharam por ausência dos comportamentos, antes da implementação. GREEN:31testes,exit0,0,151s,dois skips de symlinkWindows. A observação somente metadata do registry físico `c0299e6240bb85473b25b50940cbff3cd44e6cd453c73540ad527b7468fd2ba1` reconheceu66 ofertas201003–202606 e zero revisões; oferta/perfil não fabricam aceite.

Inputs têm campos fechados e rejeitam refs/seleções duplicadas antes de ordenar. Registry confere conjunto finito, seleção e ordem nativa dos reports, digest do descritor no regime existente e paths próprios de perfil. A projeção não compartilha seleção mutável com o caller. Escolhas ativas não nulas exigem revisão verified única; null preserva aceites sem selecionar latest. Todas as escolhas são validadas antes de aplicadas, evitando alteração parcial por erro.

Revisão independente parcial APP, sem achados bloqueantes, antes de builder persistente; diff/check e inventário de dois arquivos conferidos. Não cobre persistência, API pública, descoberta, consultas ou aceite final66. CI do SHA publicado2502444 concluiu success em push37792423895 e PR37792431086; esse resultado não é atribuído aos novos commits locais.

Ruling: congelar autoridade em fragments derivados fechados, sob hash externo/inventário interno do catálogo, conservando refs físicas e projeções exatas autenticadas no builder — evita depender de coordenação externa removida ou copiar transporte/código/logs inteiros. Alternativa de copiar toda a coordenação foi rejeitada por duplicação/privacidade; simplesmente guardar `accepted:true` perderia os vínculos de autoridade. Revisão independente do desenho adequada, com exigência de distinguir original/cópia canônica, perfil físico/nativo e validação original/projeção congelada. Especificação atualizada antes da implementação. Se houver erro nessa fronteira, load poderia confiar em incoerência interna; os testes causais de companions e vínculos são gate antes de consultas. Nenhum fragment vindo do caller passa a ser autoridade.

## Checkpoint da projeção autenticada do journal57

Base `8bd9c980bde5c46d0cc917ab7c1881230b660800`. Journal capturado sob pin físico finito `b14d7051fc54dd95b3f10743fdf1f688ae15335beb30c7e94086532f6bb25c7d`. A projeção conserva ref/bytes/head e sete finishes do membro com specs/receipts; confere cadeia inteira, sequência inteira estrita, plano, pares start/finish, exclusividade, ordem das sete etapas, ausência de estágios incompletos e igualdade start.spec→receipt.spec. Não copia journal original nem coordenação executável. O parser conserva também os checks somente metadata da API `read_status` existente.

RED inicial:três comportamentos ausentes. A observação real encontrou path montado com barra dupla; teste causal reproduziu a rejeição antes de corrigir a constante. Revisão parcial retornou CHANGES/P2 para ordem das etapas e spec de início sem vínculo explícito ao receipt. Os casos causais reproduziram as lacunas antes da correção: journal completo reencadeado com compare antes de admit foi aceito; vínculo de spec ainda não era exigido. Acrescentada progressão por membro e mapa obrigatório de specs autenticadas, sem alterar pipeline/readers.

GREEN final focal:37testes,exit0,0,255s,dois skips de symlinkWindows. Observação real dos sete wrappers:exit0,4,839s,98registros e sete finishes por membro;48imagensmetadata capturadas, sem reabrir corpus/payload/query/replay/GET. Revisão focal das duas correções concluída APP, sem achados materiais remanescentes, antes de persistência. Skills receiving-code-review e verification-before-completion aplicadas à avaliação causal/evidência, sem alegação de suíte completa ou conclusão61.

CI do SHA8bd9c98 concluiu success em push37794909014 e PR37794914860; ainda não valida o delta deste checkpoint. Task0 do plano marcada conforme APP/claim já registrados; Task1 permanece incompleta até persistência/descoberta e revisão correspondente.

## Checkpoint de persistência e descoberta

Base `7599bdd85af4b80aded4be2b485d17cd373f1bcf`. Implementadas prepare_catalog/load_catalog/discover e contexto Catalog opaco, com bytes/estado imutáveis registrados pelo loader. Inputs e registry têm cópia interna exata; gates conservam imagem exata e canônica, distinguindo hash físico original. Manifests/perfis pequenos e fragments derivados possuem inventário fechado. Captura própria da preparação reutiliza bytes por path; não permite pin conflitante nem mantém cache entre comandos. Destino novo e catalog.json gravado por último, sem apagar parcialmente produzido ou sobrescrever aceites.

RED: sete APIs/comportamentos ausentes. Freeze detectou captura repetida idêntica do perfil403; regressão permitiu deduplicar imagens iguais e rejeitar bytes conflitantes. Revisão parcial retornou CHANGES/P2 por dependências/origens de gate sem vínculos e projeções registry/active não cruzadas com input. Adicionados estados sintéticos pós-validação com uma revisão, testes de frozen_document e loader, para que catálogo vazio não seja a única evidência. Não são aceites reais nem passam pelo parser de autoridade pública.

Casos causais RED→GREEN: dependências omitidas/origem não listada, registry com pin divergente, escolha null indevida, API relativa ligada ao cwd, refs originais não canônicas, semântica do gate canônico alterada mantendo pin original e ausência do escopo de captura. Corrigidos os vínculos/paths e preservação de parent pinado. Uma edição de teste moveu asserts para o método errado e gerou NameError; restaurada a separação dos métodos antes da verificação final, sem modificar o comportamento esperado.

Ruling: manter também a cópia exata pequena do gate, além da canônica — permite conferir o pin original e a semântica derivada no loader, sem depender do arquivo original. Não copia corpoHTTP, código, logs ou coordenação. Parent tem projeção leve de origens derivada somente de catálogo autenticado; loader exige preservação de todos gates novos/herdados e não transfere coordenação executável. Descoberta relata local_health not_checked/payload not_run, pois lê somente metadata congelada; abertura/show verificarão a saúde local. Spec atualizada para estes schemas antes da execução real.

GREEN focal atual:56testes/exit0,2,762s,dois skips de symlinkWindows. Inclui determinismo, oferta66/aceite0, contexto forjado/mutação, filtros, hash/schema/counts, companions removidos/alterados/extras, remoção de inputs/registry/parent externos, revisão sintética com aceite e origem herdada inválida, e processo Python novo sem imports DuckDB/pipeline/acquisition na listagem. Os dados reais11 ainda não foram preparados por este builder; revisão focal dos vínculos solicitada antes de executar. Resources nesta máquina:2.081.256KiB física/4.256.072KiB virtual; metadata-only, sem liberar gate59 ou consultas pesadas.

CI7599bdd push37796547918/PR37796553702 concluiu success, referente à base deste checkpoint. Resolução, CLI, queries/corpus11, futura autoridade60 e aceite final66 continuam pendentes. Nenhum payload/query/replay/GET foi executado nesta implementação.

### Persistência real inicial11 — 2026-10-08

Preflight publicado na [Issue61](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61#issuecomment-6063497121), após revisão parcial APP do builder/load/discover. Preparação serial com runtime `.venv` existente e `-B`; recursos livres antes do preparo:2.967.780KiB física/6.255.848KiB virtual. Inputs/handoffs canônicos em destino novo ignorado `.scratch/catalog61-persistent-inputs-20261008/`; input SHA `63e731f43abc230dce6eae6ba254fb798f524255eefe45ffad91bc5d1e07c1ff`. Fontes são os dois wrappers externos pinados declarados no preflight, sem reabrir payloads. O helper privado inicialmente tratou document como atributo e recebeu TypeError antes de qualquer escrita; corrigido para document(), preservando o mesmo plano e destinos novos.

Comando privado de preparação: `.venv/Scripts/python.exe -B .scratch/catalog61-prepare-initial11-20261008.py`, exit0. Dois destinos novos `data/runs/financial-catalog-20261008-initial11/` e `data/runs/financial-catalog-20261008-initial11-repeat/` geraram o mesmo SHA físico de catalog.json: `bc26107246a00d19b735d1e386a0a1ce27c65f889d840ec99cb3f723ef4463a3`. Ambos carregados sob esse pin externo:66ofertas/11seleções aceitas/55unavailable/11revisões, preservando autoridade histórica e etapas disponíveis. Cada inventário possui69arquivos JSON pequenos; nenhuma cópia de Parquet/CSV/corpoHTTP/código/journal original.

Verificação em processo novo: `.venv/Scripts/python.exe -B .scratch/catalog61-check-initial11-20261008.py`, exit0. Descobertas idênticas nos dois catálogos; seleções aceitas202312/202403/202406/202409/202412/202503/202506/202509/202512/202603/202606, uma revisão selecionada por membro. Sem imports DuckDB/pipeline/acquisition; accepted informa local_health=not_checked e payload_validation=not_run. Loader confere pin/schema/inventário físico dos companions. Git check-ignore confirmou os artefatos privados ignorados.

Revisão independente parcial dos artefatos:APP, sem achados materiais, separada da revisão APP do código. Conferiu input/hash, gates originais, load/discover, determinismo e68companions/4.725.263bytes idênticos; 202412/202503 conservam absent_from_transport. Helper SHA `5c05db31f0d16ea7f9ddd568aa98afd26a3daec27262b992ac865d708dc05c2f`; resultado JSON SHA `04ef72e5ae81676f67a62f4e0658954f43a3de98ad166e73afcd7df98517a0c8`. Não executa query/replay/GET e não libera gate59; resolução/CLI/corpus11 e os55aceites restantes continuam pendentes. CI verde da base7599 não valida o delta ainda não publicado.

## Checkpoint de resolução e ponte nativa

Base `c9686c2b29e526a55ce49de373053157ef541171`; CI dessa base push37803463937/PR37803475206success, conferida nos próprios handles, sem repetir jobs. Task2 implementa seleção única/explicit revision, unknown_selection/unavailable/ambiguous_revision e health local. Descritor/report/perfil correntes do membro precisam corresponder ao catálogo; drift válido de outro membro é informado por current_registry_sha256/registry_drift e não bloqueia o snapshot antigo. Não utiliza latest/mtime ou reduz o perfil pelo filtro de report.

RED inicial:quatro testes falharam pela API ausente. Inventário extra local foi inicialmente aceito; regressão causal falhou antes da implementação do inventário fechado. Registro do drift físico estava ausente; teste RED KeyError antes do retorno explícito. GREEN resolução62tests/exit0 e revisão parcialAPP do código/saúde. Resolução lê/hash metadata e confere presença/tamanho dosparts, sem hash de payload; same-size payload alterado conserva not_run até adapter, por teste explícito. Originais de admissão/raw não são necessários para o Parquet autocontido. Duas revisões pós-validação sintéticas carregadas mantêm ambiguidade sem active; explicit revision resolve sem alterar descoberta. Fixtures sintéticas não provam autoridade histórica nem cobertura real.

Após [preflight](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61#issuecomment-6063762711), `.venv/Scripts/python.exe -B .scratch/catalog61-resolve-initial11-20261008.py` exit0 resolveu as11revisões aceitas sob pin do catálogo real. Todas metadata_verified/not_run e registry_drift=false. Resultado privado SHA `bdc66ac521986218961cb933845b30ce99e8c64dacc26284c49abbe7e8d7b4a4`; helper SHA `205e4bf9fe8c01f5fb60f7b81f042d6212aa2318eccdd66fb9d6cde5501c3729`. Revisão independenteAPP do helper/artefato/spec, sem payload/query/replay/GET. Este resultado não é read11/query atual nem libera59.

Ponte implementada após esse APP: snapshot_connection delega snapshot completo/hash externo ao adapter existente, conexão pertence ao chamador. iter_numeric_decimals é lazy, guarda o binding numérico do manifest pinado, delega par report/column e fecha iterator no abandono ou erro. Import do adapter ocorre apenas na abertura; nenhum DuckDB na descoberta. Sem cast/UNION global, fórmula, join ou mudança no reader/adapter.

Testes novos em `tests/test_financial_catalog_query.py` usam fixtures históricas offline pequenas do adapter real; stub somente do resultado da resolução, que tem testes próprios. Setup inicial faltou instalar a fixture e gerou AttributeError antes do RED válido; corrigido o setup. Cinco RED por APIs ausentes, depois implementação. Uma expectativa de report inteiro foi corrigida para VARCHAR do contrato nativo das células, sem coerção de produção. Conferem todosreports, Decimal largo exato/None sob prec3, binding duckdb_decimal=1e-27, group/text/IDdesconhecido antesSQL, cancelamento lazy/close e erro de hash do adapter. GREEN final: `.venv/Scripts/python.exe -B -m unittest discover -s tests -p 'test_financial_catalog*.py'`,68tests/exit0/8,616s/dois skips symlinkWindows. Revisão parcial da ponte APP antes da CLI; identidade final e CI do novo SHA serão conferidas na publicação.

CLI/corpus11/composição/regressões finais e autoridade60/55novosaceites permanecem pendentes. Queries neste checkpoint somente fixtures; nenhum payload financeiro real reaberto. Cobertura operacional11/66, coleta55bloqueada pelo gateWindows59. PR tamanho livre, revisão parcial aplicada durante o desenvolvimento.

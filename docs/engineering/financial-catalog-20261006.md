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

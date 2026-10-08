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

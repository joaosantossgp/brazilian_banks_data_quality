# Sanitização financeira por lote — Issue 57

Issue: [#57 — Automatizar sanitização e concluir o lote financeiro 202312–202606](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/57). Rota e cobertura: [mapa #2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2). Base de integração: `main` em `7cb4f7e81713995357cd5ad2d837004531f3d3f2`; branch `codex/financial-batch-sanitization`.

## Resultado e limites

Entregar um executor offline comum e aceitar os sete conjuntos financeiros já coletados: `202406`, `202409`, `202506`, `202509`, `202512`, `202603` e `202606`. Resumo, Ativo, Passivo e DRE oficiais conservam todas as variáveis, IDs, árvores, perímetros, janelas, versões, atributos e ausências nativas. O aceite desses sete leva a cobertura financeira de **4/66 a 11/66**, depois da integração da entrega.

Esta Issue não coleta fontes. A aquisição dos 55 históricos restantes pertence à [#59](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/59), e sua sanitização à [#60](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/60). Elas reutilizarão o executor mediante contrato de entrada explícito. Não implementar um pipeline ou PR por trimestre, inferir equivalência entre regimes, anualizar DRE, escolher amostra/indicadores acadêmicos ou operar o Project /3.

## Entradas e autoridade

Fontes imutáveis da [#54](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/54), no run `data/runs/financial-historical-acquisition-202312-202606-20261005/`:

| Entrada | SHA-256 dos bytes físicos |
|---|---|
| `bundle.json` | `557e4fbc22b552c4ec3179d39560c17d6c0ea8ec4102c971f602705a1a25c890` |
| `bootstrap.json` | `ac04474c43a17920e30597724e922c8a1f36c6b3999d6bc2b462b443dfb04bd3` |
| `handoff.json` | `5b7fb2274f336e02dcbc8bb22e0e25f1c95587fed83b9178ff272c113b99bfc5` |

Preservar os cinco pins físicos da aquisição, todos os corpos, manifests, jobs, bindings, receipts e journals originais. O handoff declara três Parquet aceitos naquele instante. A quarta referência, `202403`, integrada pela [#55](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/55), exige suplemento separado de evidência autenticada: perfil, manifests de admissão/Parquet e replay, consultas e comparação. O arquivo/hash externo é entrada explícita de `prepare`; sem suplemento válido, não somar essa referência. Perfil instalado ou fonte existente não comprova aceite.

## Tarefas e handoffs

| Tarefa | Entregável | Condição de passagem |
|---|---|---|
| 1. Ponte agregada | `compose_batch_acquisition_handoffs`: prova do lote uma vez e projeção dos sete envelopes de autoria | Testes pertinentes e revisão independente; contrato anterior `202403` preservado |
| 2. Executor e contenção | APIs `prepare_profiles`, `run_pipeline`, `read_status`; CLI `prepare/run/status`; worker CPU conhecido e launcher Windows | Preparação, execução, consultas, replay, falhas e retomada comprovados com fixtures; revisão independente; suíte final de software |
| 3. Lote real | Sete propostas de perfil e registry, instalação exata após revisão e sete gates completos | Recursos e destinos conferidos; originais protegidos; admissão, Parquet, consultas, valores exatos e replay de cada membro comprovados |
| Publicação | Ledger de execução, arquitetura/README, diff final, PR e integração | Revisão independente do conjunto final, checks/CI aprovados, integração e CI pós-merge confirmadas; mapa atualizado |

O integrador é o único responsável por perfis instalados, registry, arquivos compartilhados, Git e tracker. Delegados recebem snapshots privados e allowlists limitadas. A revisão de software privado não equivale à publicação nem ao aceite de dados reais.

## Fluxo do executor

1. `prepare` exige paths e hashes externos do bundle/handoff/bootstrap, destino novo e recursos fechados. Um worker contido autentica o lote inteiro uma vez; workers por membro compilam e congelam os perfis, sem repetir abertura global. Plano executável somente depois das sete propostas completas. Não instalar perfis pelo executor.
2. Revisão agregada confronta os sete perfis com descritores, fontes, árvores, folhas/grupos, anotações, ausências e largura cadastral nativa. Root instala exatamente as sete propostas e somente as sete ativações do registry. As demais entradas ficam preservadas.
3. `run` exige plano/hash, código/runtime/recursos pinados e registry instalado idêntico à proposta revisada. Para cada membro: `admit`, `convert`, `query`, `replay-admit`, `replay-convert`, `replay-query`, `compare`.
4. Consulta confere grade textual, contagens, presenças, estados, schemas e bindings. Uma abertura SQL é encerrada antes de uma abertura do accessor Decimal; confrontar todas as linhas numéricas e suas identidades/origens com o CSV admitido autenticado. Os 32 campos VARCHAR pertencem à grade, não impõem largura ao cadastro.
5. Replay autentica inventários completos e compara todos os payloads. Permitir somente `created_utc` dos manifests e hashes diretamente derivados dos manifests já demonstrados iguais no restante. Não excluir metadata em bloco, arredondar, usar DOUBLE, preencher ausência com zero ou criar UNION numérica global.

DECIMAL permanece nos bindings que cabem em 38 dígitos; largura superior usa a representação textual exata explícita do contrato histórico v2 e accessor Python Decimal. A validação não certifica comparabilidade econômica entre snapshots.

## Recursos, falhas e retomada

Usar o Python/DuckDB já instalados. Recursos são política explícita da máquina: prazo por etapa, mínimos disponíveis de memória física/commit/disco e intervalo de medição. Registrar diagnóstico e valores antes do gate; não impor teto universal de RAM. Manter workers1 até a prova integral dos sete. Depois, aumento de workers exige patch/policy registrada e revisada, capacidade conjunta medida e ownership compatível.

Worker nasce contido; resultado somente após extinção comprovada da árvore. Medição desconhecida, prazo excedido, falha de recurso, integridade, seleção, código, registry, path ou exceção inesperada interrompe novos despachos globalmente. Falha local de schema tem classe explícita `NativeSchemaError` na fronteira mínima dos validadores nativos puros do reader, preserva parciais e não conta como aceite. Reautenticar os inputs da etapa antes de permitir classificação local; `ValueError` desconhecido permanece global. Não classificar por mensagem, substring ou origem do traceback.

Claim exclusivo e journal durável vinculam sequência, hash anterior, plano, membro, etapa, início e resultado. Carregar/reconstituir o journal e decidir criação/retomada sob a mesma posse do claim usada para append; não autorizar despacho por estado anterior ao lock. Retomada autentica etapas concluídas antes de pulá-las. Etapa iniciada sem terminal fica em quarentena depois de comprovar extinção; preservar destino parcial, sem apagá-lo ou sobrescrevê-lo. Nova tentativa exige plano/destinos novos. CLI: exit 0 somente para os sete replays completos; exit 2 para parcial/quarentena; exit 3 para interrupção global.

## Ownership e arquitetura

Allowlist de software:

- `bank_quality/financial_report_profiles.py`, `tests/test_financial_report_profiles.py`;
- `bank_quality/financial_reports.py`: fronteira mínima de erro nativo tipado, mantendo contratos, representação e payloads;
- `bank_quality/financial_pipeline.py`, `tests/test_financial_pipeline.py`;
- `bank_quality/windows_financial_pipeline.py`, `tests/test_windows_financial_pipeline.py`;
- `scripts/run-financial-pipeline.py`.

Allowlist de perfis: sete JSONs próprios em `bank_quality/financial-reports-profiles/` e sete ativações em `bank_quality/financial-reports-registry.json`. Root registra destinos concretos novos de execução, admissão, Parquet e replay antes do gate em `data/runs/`, `data/derived/` e `data/curated/`. Documentação: este plano, `docs/engineering/financial-batch-sanitization-20261005.md`, `docs/architecture.md` e `README.md`.

Composer fica no módulo responsável existente. Coordenador e launcher CPU são adjacentes no pacote; CLI somente delega. Launcher próprio reusa helpers existentes sem alterar `windows_acquisition.py` e quebrar os pins da #54. Sem nova raiz, camada, dependência, parser/modelo de domínio ou runtime importado de scripts privados. Comparar diff/inventário com a allowlist e os [destinos canônicos](../../architecture.md#organização-dos-arquivos-e-pastas) na revisão final.

## Workflow, skills e verificação

Aplicar o [workflow obrigatório](../../agents/workflow.md). Superpowers: desenho/plano existentes; `subagent-driven-development`, TDD para software, diagnóstico quando falhar, revisão independente por tarefa/conjunto e verificação antes de conclusão. Matt depende de invocação e mecanismo disponível; Feynman quando pesquisa primária/PDF for necessária; Context7 para API/biblioteca concreta. Documentação visual, quando necessária, usa diagram-design em SVG/PNG, padrão claro.

Testes focados verificam comportamento real com fixtures pequenas, incluindo Nx múltiplos, cadastro variável, precisão acima de 38 dígitos, null/zero/NA/NI/vazio/atributos e falhas/retomada. Rodar a suíte final de código uma vez após os ajustes revisados; não repetir por perfil JSON ou trimestre sem mudança de comportamento. Dados reais exigem seu próprio gate completo. Done exige sete conjuntos aceitos, protegidos intactos, revisão/checks, integração confirmada e mapa com cobertura/restante/próximo passo/paralelismo atualizados.

## Ajuste de memória — 2026-10-05

Primeira tentativa do gate interrompida na conversão202406 por margem física livre, sem novo aceite. Preservar tentativainicial e destinoemquarentena; usar novo plano/destinos para repetir. Manterworkers1/margem512MiB. Diagnóstico offline delimitado mede compartilhamento local de strings CSV repetidas e mostra redução de retenção; não certifica pico real.

Allowlist acrescenta `tests/test_financial_reports.py`: teste causal de memória materializada e preservação de tokens/ordem. `financial_reports.py` reaproveita somente strings iguais ao último valor por campo, cache local limitado ao schema, sem intern/global/cardinalidade acumulada. `financial_pipeline.py` elimina listas integrais de expectativa em `verify_query`, usando contadores e gerador em uma passagem, com ordem/bindings/quantidades conferidos. TDD/erro/schema permanecem; revisão independente e realgate completos antes do aceite. Nenhum novo módulo/dependência/contrato de dados ou relaxamento da margem.

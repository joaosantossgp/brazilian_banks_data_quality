# Expansão mínima IF.data — plano de execução autorizado e verificado

> **For agentic workers:** Use Superpowers executing-plans inline, TDD e revisão independente ao implementar. As tarefas 1–3 foram autorizadas, executadas e verificadas; a tarefa 4 permanece decisão humana. Este fechamento documental não repete coleta. Não repetir aprovação da direção geral já aceita, nem tratar a unidade/amostra ainda aberta como decidida.

**Goal:** Fechar os controles necessários à tese de capital aberto e preparar um único novo trimestre (202312, individual, Resumo), antes de considerar escala.

**Architecture:** Reutilizar archive, portal acceptance e inventory. Adicionar um perfil explícito de cobertura/janelas e um ledger temporal de identidades separado; parametrizar a coleta exclusivamente por allowlist, sem generalização para histórico inteiro.

**Tech Stack:** Python 3.12+, stdlib/unittest; Node 18+, Playwright já disponível, navegador existente. Sem instalação global.

**Spec:** `docs/superpowers/specs/2026-10-01-ifdata-expansion-design.md`.

## Global Constraints

- Escopo executado: um novo trimestre 202312, com arquivos novos e piloto original preservado.
- Lote realizado: somente 202312 individual/Resumo; coleta nova aceita `(202312,)` em modo portal explícito, default original `(201012,202412)` preservado. Replay pode compor os três períodos; sem opção todos.
- Financeiro somente BCB; CVM/B3 metadados; foco capital aberto; comparação IF.data ampla explicitamente opcional.
- Preservar fontes/URLs/horários/hashes/falhas, NA/NI/null/branco/zero e estados desconhecidos.
- Limites aplicados ao novo lote: 150 MiB reserva, 80 MiB bruto/tentativa, 480 s/execução, duas tentativas no máximo.
- Não presumir listagem histórica, identidade/conglomerado, continuidade econômica de nomes/IDs ou versão compatível.
- Sem histórico completo, 2025+, outras demonstrações, acadêmico/calendário, global/unrelated changes ou commit/push/publicação.

## Review Focus

- Cadastro completo **no arquivo recuperado** não vira universo histórico completo — testes na tarefa Cobertura.
- Ausência de chave numérica em campo calculado/cadastral não vira zero/faltante — testes na tarefa Cobertura.
- Emissor listado/holding e instituição individual com nome parecido não viram a mesma entidade — testes na tarefa Dossiê.
- Fluxos semestrais, vintages diferentes e novos IDs não viram valores trimestrais/economicamente equivalentes — testes na tarefa Lote.
- Catalogado mas inacessível, HTTP500 ou orçamento excedido não vira coleta completa vazia — testes na tarefa Lote.

### Task 1: Cobertura e semântica dos trimestres já coletados

**Files:** create `bank_quality/coverage.py`, `tests/test_coverage.py`; use existing `bank_quality/archive.py`, `bank_quality/portal.py`; write `data/derived/<run>/coverage.json`, `reports/<run>-coverage.md`.

**Interfaces:** `audit_coverage(cadastro: list[dict], table_ids: set[str], period: int) -> dict`; consumes hash-verified source records; emits source/period counts, duplicates, missing identifiers, set differences and separate claims about observed coverage. `reporting_window(period: int) -> tuple[str, str]` emits official result-window dates, never derives financial values.

- [x] Escrever testes de divergência de conjuntos, código duplicado/vazio e trimestre errado; verificar RED.
- [x] Implementar perfis por fonte/denominador e janelas acumuladas; manter significado de cada claim explícito.
- [x] Rodar `python -B -m unittest discover -s tests -p test_coverage.py -v`; GREEN esperado.
- [x] Demonstrar cobertura REST↔Resumo de 1.976 e 1.585 códigos, OData indisponível e universo histórico desconhecido. Classificar campo direto/computado/cadastral/marcador segundo definição oficial, sem adivinhar campos.

### Task 2: Dossiê de emissores e unidades IF.data

**Files:** extend `bank_quality/metadata.py`, `tests/test_metadata.py`; write `docs/engineering/capital-aberto-identity-dossier.md` and `data/derived/<run>/identity-evidence.csv`.

**Interfaces:** `identity_evidence(issuer: dict, reporting_entity: dict, relationship: dict | None) -> dict`; retain distinct issuer/CVM identity and source IF.data namespace, dated relationship evidence, known/unknown state. No financial join is produced.

- [x] Escrever testes que rejeitam identidade por nome, vínculo sem intervalo/fonte e conversão de data de evento em listagem histórica; verificar RED.
- [x] Construir três casos já iniciados (BB, Bradesco, Itaú Holding), usando arquivos existentes e poucas fontes primárias históricas pertinentes; delimitar lacunas e evitar repetir o cadastro atual como prova histórica.
- [x] Rodar testes de metadados; GREEN. Cada conclusão tem documento/URL/hash/data ou estado desconhecido.
- [x] Entregar opções de unidade individual/consolidada e janela final para decisão humana, com impacto dos casos, sem escolher pelo usuário.

### Task 3: Um novo trimestre, do raw ao inventário

**Blocked by:** Task 1. Task 2 deve preceder por prioridade temática, mas não é bloqueio técnico da comparação IF.data opcional. A coleta não define a amostra de capital aberto.

**Files:** modify `bank_quality/ifdata.py`, `bank_quality/portal.py`, `bank_quality/replay.py`, `bank_quality/__main__.py`, `scripts/export-portal.cjs`; extend `tests/test_ifdata.py`, `tests/test_portal.py`, `tests/test_replay.py`, `tests/test-portal-ready.cjs`; new immutable raw/derived run and report.

**Interfaces:** preserve existing default pilot; add explicit CLI `--periods 202312` and validated `collect(root: Path, periods: tuple[int, ...]) -> dict`. Accepted periods are only 201012, 202312, 202412; single next run requires `(202312,)`. Discover exact source report/path/schema from the hashed catalog. Replay accepts only the same explicit run scope and reconstructs archived bodies.

- [x] Escrever testes de allowlist, estrutura divergente, orçamento, catálogo inacessível e replay de três trimestres com período/janela/versionamento; RED.
- [x] Implementar somente as mudanças para 202312, orçamentos e proveniência. Não remover guardas para aceitar datas arbitrárias, buscar relatórios T ou reconstruir prefixos 2025.
- [x] Rodar suites Python e Node; GREEN, incluindo reprodução inalterada do piloto original.
- [x] Em execução autorizada, adquirir somente 202312 individual/Resumo em diretório novo; parar nas condições de orçamento/falha, preservando tentativas. Nenhum resultado de 202312 é esperado antes do download real.
- [x] Reconstruir inventários 201012/202312/202412 sem sobrescrever os originais, com códigos de fonte, janelas, versões, NI/NA/null/branco/zero, diferenças de cadastro e de estrutura. Comparar estoques e fluxos de mesma janela; nenhuma derivação Q4 automática.
- [x] Verificar hashes/replay/contagens reais e revisão independente; produzir handoff com custo/volume real e próximo bloqueio. Sem commit/push.

### Task 4: Decisão humana antes da escala da tese

**Blocked by:** Task 2, não Task 3.

- [ ] Examinar os três casos para decidir a unidade principal e como representar holdings; uma cadeia documentada é requisito de aceitação do vínculo.
- [ ] Decidir a janela temporal final. 201012–202412 é apenas intervalo usado para estimativa, não seleção silenciosa da tese.
- [ ] Explicitar a regra de elegibilidade de capital aberto e o papel distinto de registro CVM/evidência B3; não inferir o critério a partir do título.
- [ ] Registrar decisão e critérios de elegibilidade temporal; não tratar ausência de prova como exclusão definitiva ou incluir só sobreviventes atuais.
- [ ] Só então propor lotes maiores e possível comparação ampla. A revisão Cosif 2025 permanece uma tarefa separada se a janela escolhida alcançar esse período.

## Handoff

Quatro rascunhos individuais estão em `.scratch/ifdata-expansion/issues/`, com bloqueios/aceite. A conversa principal organiza o Project existente. Este plano foi auto-revisado contra escopo, fontes e interfaces; tarefas 1–3 concluídas e verificadas. A tarefa 4 permanece decisão humana antes de escala. Nenhum cronograma acadêmico foi alterado.

## Fechamento documental

João autorizou a execução da etapa, incluindo dezembro/2023, registrada no fechamento de 2026-10-02. A execução local já foi validada; este fechamento documental não autoriza nova coleta ou escala. Unidade, janela final e elegibilidade de capital aberto permanecem decisões humanas.

Resultado: 40.904 observações nos três períodos ; 52 corpos verificados e 7 artefatos de replay idênticos. Reconferência offline: 54 testes Python passaram; nenhuma nova coleta. Ver `docs/engineering/expansion-execution.md` para critérios de cobertura/dossiê, oito vínculos desconhecidos e evidências.

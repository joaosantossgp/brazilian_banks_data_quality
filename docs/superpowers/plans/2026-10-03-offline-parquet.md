# Offline DuckDB + Parquet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans; execução nativa autorizada, seguida de revisão independente da branch inteira.

**Goal:** Converter e verificar offline o inventário aceito de 40.904 observações em novo snapshot Parquet.

**Architecture:** CSV original integral como texto, DECIMAL exato adicional e arquivos complementares preservados. Workers por referência escrevem staging independente; coordenador publica manifesto por último. DuckDB consulta diretamente a lista de Parquet aceita, sem banco persistido.

**Tech Stack:** Python 3.12, stdlib, DuckDB 1.5.6 oficial; .venv local; Parquet ZSTD.

**Spec:** [desenho autorizado](../specs/2026-10-03-offline-parquet-design.md).

## Global Constraints

- Referências 201012, 202312 e 202412; perspectiva individual/Resumo; somente dados existentes, offline.
- Preservar bruto, CSV/JSON, IDs, unidades, estados, tokens, precisão e hashes; destino novo, nenhuma exclusão.
- Uma dependência DuckDB oficial local; nenhuma instalação global, servidor ou edição de projetos pausados.
- Documentos sem identificadores pessoais; branch local sem push, PR, merge, deploy ou permissão.

## Review Focus

- Tokens exponentiais, negativos, zeros e limites DECIMAL devem manter o valor exato ou rejeitar.
- JSON null, literal null, blank, NA/NI e invalid devem manter a causa, sem virar zero.
- Entrada alterada durante leitura ou conversão deve impedir aceite ou deixar snapshot fiel aos hashes capturados.
- Dois publicadores e falha de rename não devem tornar visível conjunto parcial nem substituir snapshot aceito.
- Manifesto adulterado, caminhos externos e perda de arquivos devem falhar antes de consulta/reuso.

### Task 1: contrato, ambiente e conversão exata

**Files:** `requirements-duckdb.txt`, `.gitignore`, `docs/adr/0001-duckdb-parquet.md`, `bank_quality/parquet.py`, `tests/test_parquet.py`.
**Interfaces:** `convert_inventory(source: Path, destination: Path, workers: int = 1) -> dict`; `validate_snapshot(destination: Path) -> dict`; `snapshot_connection(destination: Path) -> DuckDBPyConnection`, view `observations`.

- [x] Registrar ADR aceito e marcar proposta PostgreSQL anterior como superada, preservando original em backup local; instalar DuckDB somente em .venv e registrar licença/hash.
- [x] Escrever teste `test_exact_tokens_decimals_and_complementary_inventory`: igualdade de todos os campos originais, IDs com zeros, Decimal('9007199254740993.01'), zero e estados distintos; arquivos complementares byte idênticos. Rodar e observar falha por conversor ausente.
- [x] Implementar leitura CSV integral, perfil DECIMAL até 38 dígitos, estados consistentes, Parquet por referência e validação de conteúdo/decimal. Rodar teste verde.

### Task 2: publicação, falhas e CLI

**Files:** `bank_quality/parquet.py`, `bank_quality/__main__.py`, `tests/test_parquet.py`, `.github/workflows/ci.yml`.
**Interfaces:** mesmas da Task 1; CLI `python -m bank_quality parquet --inventory DIR --output NEWDIR --workers {1,2}`.

- [x] RED: testes de reuso sem modificar hashes/mtime; entrada diferente; lock concorrente; parcial sem manifesto; rename falho; Parquet adulterado; caminho fora do snapshot; tipo decimal além de 38; estados incompatíveis; todos rejeitados sem aceite.
- [x] GREEN: mkdir exclusivo, estágio por job, manifesto por último, validação no reuso/leitura, seleção exata de arquivos e erros claros. CLI importa DuckDB somente nesse comando, mantendo replay/coleta existentes. CI instala pin oficial para executar novos testes offline quando for publicada futuramente.
- [x] RED/GREEN: dois workers produzem mesmo conteúdo lógico que um; teste real de CLI sem rede e validação de referências/unidades/contagens. Rodar suíte inteira Python/Node.

### Task 3: replay, medidas e revisão local

**Files:** `scripts/benchmark_parquet.py`, `docs/engineering/offline-parquet-20261003.md`, `reports/offline-parquet-20261003.json`; evidência detalhada em `.superpowers/sdd/2026-10-03-offline-parquet/`.
**Interfaces:** conversor/consulta da Task 1; replay existente, sem alteração.

- [x] Verificar hashes protegidos e reconstruir inventário em destino novo via replay; comparar sete arquivos byte a byte.
- [x] Executar conversão de uma e duas workers em novos destinos ignorados; validar 40.904 observações e conteúdo integral, DECIMAL e inventários complementares; reutilizar um snapshot e confirmar idempotência.
- [x] Medir bytes de bruto, derivados CSV/JSON, curado, metadados, staging/duplicação e .venv; cronometar consulta de estados e seleção numérica por referência; guardar comandos/resultados sem caminhos pessoais nos documentos técnicos.
- [x] Revisar branch completa com reviewer independente; corrigir achados relevantes com RED/GREEN e suíte verde. Fazer commit local somente dos arquivos desta tarefa, com bruto e curado ignorados. Entregar caminho, branch, números reais, limites e pendências, sem publicação.

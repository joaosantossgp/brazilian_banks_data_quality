---
status: accepted
date: 2026-10-03
---

# DuckDB + Parquet para análise local da monografia

A monografia usará Python e snapshots Parquet, consultados diretamente por DuckDB embutido. A escolha foi aceita para operação local e uso de SSD, sem manter outra cópia integral em um banco .duckdb. Substitui a proposta local de 2026-10-02 que recomendava PostgreSQL para alinhar ferramentas de projetos distintos; essa proposta era rascunho e não havia sido implementada. Projetos pausados e o PostgreSQL de outro projeto não são alterados.

Bruto e proveniência permanecem imutáveis; Parquet é uma camada derivada. O contrato preserva todos os tokens, IDs, estados, unidades e hashes e acrescenta DECIMAL exato após perfil, sem float nem arredondamento silencioso. Um coordenador aceita o conjunto por manifesto escrito por último; workers usam destinos próprios. Consultas fixam a lista de arquivos do manifesto, evitando misturar revisões ou perspectivas. Não se agregam financeiro, prudencial e individual por usar o mesmo motor.

Consequências: sem servidor/credenciais novos; snapshots e backups ainda consomem espaço e falhas de publicação exigem diagnóstico. DuckDB não oferece transação automática entre arquivos Parquet; rename não prova durabilidade contra perda de energia. DECIMAL admite até 38 dígitos e divisão retorna ponto flutuante, portanto nenhuma razão financeira é calculada nesta entrega. A conversão do piloto existente não resolve unidade final, amostra capital aberto ou equivalência econômica entre regimes.

Implementação e aceite seguem o [desenho](../superpowers/specs/2026-10-03-offline-parquet-design.md) e o [plano](../superpowers/plans/2026-10-03-offline-parquet.md). Dependência oficial única DuckDB 1.5.6, consultada no PyPI em 2026-10-03, instalação local Python 3.12. Context7 `/duckdb/duckdb-web` conferido com documentação oficial: [Python](https://duckdb.org/docs/current/clients/python/overview), [Parquet](https://duckdb.org/docs/current/data/parquet/overview), [tipos numéricos](https://duckdb.org/docs/current/sql/data_types/numeric), [concorrência](https://duckdb.org/docs/current/connect/concurrency) e [pacote PyPI](https://pypi.org/project/duckdb/1.5.6/).

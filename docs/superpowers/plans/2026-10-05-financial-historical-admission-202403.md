# Plano — admissão financeira nativa 202403

Issue: [55](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/55). [Contrato](../../engineering/financial-historical-admission-202403-contract-20261005.md), [ledger](../../engineering/financial-historical-admission-202403-20261005.md) e [arquitetura](../../architecture.md). Autonomia técnica aprovada, sem nova decisão acadêmica. Branch `codex/financial-admission-202403`; integração a partir de `6172b38395830be7655d41a185c4c97841577333`, após a entrega de aquisição 54. O desenho e fixtures usaram uma base anterior imutável cujos dois blobs responsáveis foram comparados antes da integração.

## Resultado e limites

Admitir, converter, consultar e reproduzir os quatro relatórios nativos 1005/202403, todas as variáveis, cadastro, origens e ausências. Zero coleta adicional; nenhuma alteração de fonte/autoridade/contrato aceito ou de proteção/credencial/deploy. Não harmonizar regimes, annualizar DRE ou decidir amostra/indicadores. O mapa 2 acompanha a meta financeira 66 e os complementos separados.

## 1. Ponte autenticada e fixtures

Paths: `bank_quality/financial_report_profiles.py` e `tests/test_financial_report_profiles.py`. Reusar a prova de aquisição, conferir anchor antes da resolução e conservar as duas ligações A/B. Catálogo/portal explícitos e normais; sem extensão das exceções legadas. Autoria pura não grava fontes, instala perfil ou ativa registry.

TDD de corrupção de pins/seleção/origens/receipts/journal, pending/failure/reset, portal ausente e autoridade alternativa coerente. Handoff exato de dois arquivos, RED/GREEN e revisão independente de spec/qualidade antes de dados reais. Concluído localmente; ver provas no ledger.

## 2. Perfil real, domínio e instalação

Integrador agenda recurso livre e compõe envelope/A/B em run novo, pinos físicos externos e originais preservados. Compiler/freeze existentes geram candidato/perfil draft, sem ativar. Medir árvore de processos, working set, commit, disco e margem disponível; falha de medição/guard encerra toda a árvore e conserva parciais.

Revisor independente confronta fontes, todas as árvores/definições/annotations/origens e schema cadastral; verifica envelope externamente pinado, originais versus projetados e journal corrente versus receipts históricos. Só após APP instalar exatamente `bank_quality/financial-reports-profiles/202403.json` e atualizar os dois campos do membro 202403 no registry. Preservar os outros perfis/membros; regressão de lookup pertinente.

## 3. Admissão, Parquet, consulta e replay

APIs existentes: `financial_reports.admit`, `financial_parquet.convert_financial`, `financial_parquet.snapshot_connection` e `financial_reports_parquet.iter_numeric_decimals`. Fixar código/perfil/registry e baseline antes do gate. Destinos derived/curated novos contratados e replay `-replay`. Cada estágio pesado sequencial e contido no mesmo host; recursos por máquina, sem teto universal de RAM ou alterações dos workers de aquisição.

Gate confere grão/32 campos textuais, todas as origens e partes, cadastro, nós/folhas, contagens/estados/ausências e todos os bindings. Confrontar cada linha numérica/quantidade com CSV autenticado, identidade/ordem/Decimal/None, após fechar conexão SQL anterior. Largura>38 mantém representação v2 exata; registrar a representação observada, sem prometer precisão SQL inexistente.

Reexecutar em destinos novos, validar todas as consultas/accessor e comparar todos os payloads byte a byte. Descontar somente `created_utc` e hashes de manifests derivados desse timestamp, autenticando explicitamente a cópia/inventário. Conferir arquivos protegidos e registrar tempo/picos/margens/saídas. Não repetir GETs ou usar contagens do shard como aceite da seleção.

## 4. Checks, revisão final e integração

Allowlist documental: este plano, contrato/ledger 202403, `README.md` e `docs/architecture.md`. Integrador único; atualizar destinos e estado comprovado. Nenhuma outra camada, raiz, dependência ou arquivo compartilhado. Testes históricos adicionais somente se comportamento afetado exigir caso pertinente, com escopo registrado antes da escrita.

Checks pertinentes e suíte pública final uma vez após mudanças finais de código/perfil; links, privacidade, inventário e hashes protegidos. Revisão independente do SHA exato e diferenças autorizadas, PR/CI/merge/CI pós-merge confirmados antes de Done. Atualizar mesma Issue/mapa com cobertura real; Project 3 permanece com Zec.

## Paralelismo e conclusão

Revisão read-only do perfil e preparação privada de gate/documentação têm ownership compatível. Registry/instalação/docs/Git têm um integrador; gates pesados dependem de recurso medido. Não há outra Issue de implementação pronta conferida. O lote posterior dos sete trimestres já coletados terá contrato comum próprio, reutilizando os mecanismos existentes.

Março/2024 só eleva o financeiro de 3/66 a 4/66 após aceite completo e integração. Done desta Issue não encerra o goal; faltam os sete recentes, 55 referências fora da janela e os complementos com conteúdo final próprio.

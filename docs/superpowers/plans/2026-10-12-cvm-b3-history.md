# Plano de execução — relação histórica CVM–B3–IF.data

> Execução por `subagent-driven-development` nas fatias delegadas, com revisão independente antes de ampliar; Root integra. [Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108).

**Objetivo:** entregar relação histórica auditável 2010–2024, priorizando conglomerados e ações/units/BDRs igualmente, com fontes, tipos nativos e lacunas.

**Arquitetura:** [desenho](../specs/2026-10-12-cvm-b3-history-design.md). Dois módulos adjacentes: admissão societária e relação temporal, CLI fina, sem rede no build e sem dependências novas. Base `f93d37f17898d69713d06f07bb393eb1f2444331`, branch `codex/cvm-b3-history-2010-2024`.

## Restrições globais

- Somente metadados; financeiro continua IF.data. Nenhuma fórmula, amostra definitiva ou ranking adotados.
- 60 referências 201003–202412, sem preencher intervalos ou equiparar conglomerado financeiro/prudencial/individual/emissor.
- Inputs autenticados por pin externo e destinos novos; nenhuma alteração dos aceitos. Pessoas físicas e valores contábeis não projetados do FRE.
- Quarentena de segmentos inválidos inteira, sem reparo ou admissão permissiva. Falhas HTTP não viram população zero.
- Allowlist e ownership na Issue; Root integra compartilhados e mapa #2. Project 3 com Zec.

## Fatia 1 — pesquisa e transporte

- [x] Investigar fontes CVM/B3 e classificações IF.data com Feynman e proveniência.
- [x] Reautenticar cadastro existente; recorte 60 referências/303.792 linhas.
- [x] Capturar e revisar transporte FRE piloto/expansão: 15 anos/122.304.751 bytes; registrar 14 segmentos não estritos no diagnóstico.
- [x] Revisão independente final da nota A; B já PASS. Desenho/plano também revisados; alternativa BDI revisada, sem certificação de cobertura integral.
- [x] Pesquisar BDR/emissores/controladas com nota e fontes originais; pesquisa revisada após corrigir localizadores Stone. Composição e admissão de vínculos continuam próprias.

## Fatia 2 — admissão FRE

**Arquivos:** criar `bank_quality/cvm_corporate_metadata.py`, `tests/test_cvm_corporate_metadata.py`. Preparação privada e índice de fontes em destinos delimitados na Issue.

**Interfaces:** `build_corporate_metadata(index_path, expected_index_sha256, output)`; `verify_corporate_metadata(output, expected_manifest_sha256)`.

- [x] Testes RED para fonte/pin/URL/truncamento, ZIP seguro e esquema; corpus sintético estrito e segmento malformado com múltiplas linhas.
- [x] Implementação inicial de captura offline autenticada, projeção finita, exclusão PJ/PF explícita e quarentena; schema textual preservado. Os dois achados iniciais foram corrigidos e revalidados no checkpoint seguinte.
- [x] GREEN inicial: 11 testes do módulo e 17 regressões CVM; confirmado independentemente, sem substituir as contraprovas da revisão.
- [x] Revisão independente de código/contrato antes de execução real; dois P2 corrigidos e revalidados em `c089f7f`, 31 testes PASS.
- [x] Build real novo e replay; confirmar inventário/hashes, qualidade, contagens e 15 anos. O pacote inicial teve dois P2 de ausência de CNPJ; correção `9091533` passou por re-review/34 testes. Pacote v2 aceito após conferência integral de 189.035 observações, 50.860 lacunas, 36 quarentenas, fontes e replay; outputs iniciais preservados sem aceite.

## Fatia 3 — relação histórica

**Arquivos:** criar `bank_quality/historical_issuer_links.py`, `tests/test_historical_issuer_links.py`, `scripts/build-historical-issuer-links.py`.

**Interfaces:** build com pacotes CVM/cadastro/societário e pins explícitos; verificar manifest externo; consulta por referência/entidade/perspectiva sem rede.

- [x] Testes RED para identidade por identificador, conflito/colisão, nome insuficiente, controle datado sem preenchimento, classes sem duplicação, financeiro/prudencial, atributos do grupo/líder e códigos desconhecidos.
- [x] Implementar tabelas de observações, instrumentos, relações, cadastro, cobertura e fila de lacunas; nenhum zero-fill. Commit local `4d574084c1811b93f89a6de5eef3c09f79139c83`; tempo/memória no corpus real ainda não medidos.
- [x] GREEN do autor: 15 históricos, 34 CVM/FRE e sete cadastro. Contraprovas e handoff privados preservados; lexer da saída canônica confrontado com DuckDB devido ao leitor CSV do Python3.12 perder null/vazio.
- [ ] Review independente de código antes de execução real, em andamento no head acima.
- [ ] Build real 60 referências e replay em destinos novos; conferência de chaves/cardinalidades/fontes e não alteração dos inputs.

## Fatia 4 — BDR e evidência complementar

- [ ] Revisar nota/claims BDR; admitir somente relações com pontas, papéis, datas e fontes comprovados.
- [ ] Incorporar cadastro estrangeiro/programas correntes como auxiliares, sem universo histórico presumido.
- [ ] Exibir BDRs não resolvidos e motivo com a mesma prioridade; não atribuir depositário ao grupo do lastro.
- [ ] Conferência independente de composição e datas/perímetros antes de declarar cobertura.

## Fatia 5 — entrega verificável

**Arquivos:** nota `docs/engineering/cvm-b3-historical-relation-20261012.md`, entradas pertinentes README/arquitetura; fontes e preparações locais preservadas.

- [ ] Registrar todos os comandos, pins, contagens, decisões, bibliografia/localizadores, falhas e cobertura real.
- [ ] Comparar diff/allowlist, links e inputs protegidos; revisão independente exata do head.
- [ ] Checks pertinentes; publicar PR anexada ao chat, integrar após revisão/checks, confirmar CI pós-merge.
- [ ] Atualizar Issue108/mapa2 e decisões efetivamente tomadas na #3. Encerrar goal somente se o objetivo tiver sido atingido; lacuna material irredutível não pode ser disfarçada de relação completa.

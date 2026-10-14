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
- [x] Implementar tabelas de observações, instrumentos, relações, cadastro, cobertura e fila de lacunas; nenhum zero-fill. Commit local inicial `4d574084c1811b93f89a6de5eef3c09f79139c83`; execução completa ainda não medida. Medidas parciais da primeira tentativa e correção posterior constam abaixo e no ledger.
- [x] GREEN do autor: 15 históricos, 34 CVM/FRE e sete cadastro. Contraprovas e handoff privados preservados; lexer da saída canônica confrontado com DuckDB devido ao leitor CSV do Python3.12 perder null/vazio.
- [x] Review independente de código: P2 de ciclos corrigido em `187cc770cc135f8fbbcd213f60efdbf91665351b`, re-review PASS com 16 testes e oráculo independente de 512 grafos.
- [x] Build real60referências e replay em destinos novos, com chaves/cardinalidades/fontes e inputs preservados. A primeira execuçãoV1 interrompida porRAM permanece diagnóstica; a retomadaV2 e correçãoR2a passaram por build/verify/replay e revisão de domínio, conforme checkpoint posterior e ledger, sem afirmar elegibilidade histórica universal.

## Fatia 4 — BDR e evidência complementar

- [x] Revisar nota/claims BDR; admitir somente relações com pontas, papéis, datas e fontes comprovados.
- [x] Incorporar cadastro estrangeiro/programas correntes como auxiliares, sem universo histórico presumido.
- [x] Exibir BDRs não resolvidos e motivo com a mesma prioridade; não atribuir depositário ao grupo do lastro.
- [x] Conferência independente de composição e datas/perímetros antes de declarar cobertura.

## Fatia 5 — entrega verificável

**Handoff solicitado em2026-10-13:** publicar código revisado e snapshot para retomada em computador mais forte, antes de novas execuções pesadas. Código entregue v1/oitoCSV; normalização v2 somente proposta revisada. CNPJ, notícias e pesquisa foram aceitos por João como evidência de identificação, sem documento jurídico formal por aresta; registrar origem/confiança/temporalidade. Esta publicação de checkpoint não encerra a relação histórica nem a Issue108. O [handoff](../../engineering/cvm-b3-handoff-20261013.md) distingue bases aceitas, diagnósticos, código, transporte e passos pendentes.

**Arquivos:** nota `docs/engineering/cvm-b3-historical-relation-20261012.md`, entradas pertinentes README/arquitetura; fontes e preparações locais preservadas.

- [x] Registrar todos os comandos, pins, contagens, decisões, bibliografia/localizadores, falhas e cobertura real.
- Gate final — Comparar diff/allowlist, links e inputs protegidos; revisão independente exata do head.
- Gate final — Checks pertinentes; publicar PR anexada ao chat, integrar após revisão/checks, confirmar CI pós-merge.
- Gate final — Atualizar Issue108/mapa2 e decisões efetivamente tomadas na #3. Encerrar goal somente se o objetivo tiver sido atingido; lacuna material irredutível não pode ser disfarçada de relação completa.

## Retomada autorizada no receptor — R1 a R4

Base `91bd20ccb205e72d47d42536eefbb529da551f16`, branch `codex/cvm-b3-history-resume`; contrato na [Issue108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6159541071). Usar a spec existente, incluindo adoção técnica V2. O handoff V1 permanece histórico. Root integra documentação/Git; execução por subagentes e revisão independente antes de ampliar. Inputs autenticados no checkout primário, em `.scratch/receiver-cvm-b3-20261013/restored/data/curated/`; nunca alterá-los. Código no worktree isolado, runtime local Python3.12.13/DuckDB1.5.6; sem instalação nova.

### R1 — representação V2 e escrita limitada

Owner implementer; allowlist `bank_quality/historical_issuer_links.py`, `tests/test_historical_issuer_links.py`, `scripts/build-historical-issuer-links.py`. Root exclusivo nesta spec/plano, ledger de execução, handoff e arquitetura. Sem novo módulo, camada ou dependência.

Complemento de verificação: Root também possui `.github/workflows/ci.yml`, inicialmente para acrescentar `fetch-depth: 0` no checkout do job `offline-tests`, para que o blob V1 pinado da base esteja disponível ao oráculo de equivalência. Mesmo pin da action e `persist-credentials: false`; nenhum job, permissão ou proteção muda. O job Windows nativo não executa esse oráculo e conserva sua configuração.

Complemento posterior de recurso, [Issue108/comment6160844085](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6160844085): Root altera também somente o timeout do job offline de15 para25minutos. Base CI853testes/726,522s e componente ampliado72testes/444,481s fundamentam o orçamento finito; revisão independente recomendou o ajuste. Windows permanece15; testes/actionpins/permissões/proteções inalterados. Não é confirmação antecipada do CI no novo head.

- [x] RED: caminho compartilhado em referências/perspectivas deve ocupar um único registro; expandir IDs deve reconstruir exatamente a representação V1. Carregar o módulo V1 do blob Git da base como oráculo, sem copiar implementação para o teste.
- [x] RED: adulteração/repin de ID, rota, datas, suportes, ponta, referência ausente e registro extra devem falhar; consulta vazia conserva lista de caminhos vazia. Casos cíclicos e datas distintas preservam os estados anteriores.
- [x] GREEN: nove schemas/versões V2; serializar caminho uma vez no cache, ID por SHA-256 do JSON canônico, relações com IDs ordenados e consulta com todos os caminhos referenciados. Verificador fecha inventário e rederiva campos/caminhos/referências integralmente.
- [x] RED/GREEN de cap do escritor com teto pequeno no teste: rejeitar CSV acima do mesmo `MAX_TABLE_BYTES` do leitor. Escrita incremental preserva bytes canônicos/null/vazio sem cópias integrais.
- [x] Rodar testes históricos focados e regressões pertinentes; salvar RED/GREEN e diff, commit somente allowlist. Revisão independente de contrato+código antes de R2.

### R2 — execução real e replay

Owner Root; preparação privada `.scratch/issue108-resume/`; outputs novos no checkout primário `data/curated/historical-issuer-links-resume-v2/` e `data/curated/historical-issuer-links-resume-v2-replay/`. Adaptação de paths de diagnóstico conserva original autenticado.

- [x] Reautenticar três pins, medir RAM/commit/disco e comparar recorte finito V2 com V1 sem alterar fontes ou descartar caminhos.
- [x] Build completo com monitor de recursos e interrupção controlada somente de processo próprio se necessário; preservar tentativa e métricas. Guardar pin externo do manifest produzido.
- [x] Verify e consultas por companhia/referência/perspectiva; replay em novo destino e confronto integral dos bytes/contagens/chaves/suportes. Conferência econômica/contábil de identidade, tipo, temporalidade e perímetros independente dos testes.
- [x] Review dos dados/recursos antes de admitir o lote. Otimização adicional exige regressão causal, registro técnico e re-review; não elevar cap ou afirmar PASS somando tentativas.

### R3 — evidência complementar e BDR

Preparação de curadoria readonly pode avançar junto à R1, owner pesquisador, único relatório privado `.scratch/issue108-resume/bdr-preparation.md`. Root fixa contrato/allowlist suplementar antes da implementação/admissão. Reusar notas/fontes/dossiês autenticados; aquisição posterior somente no escopo C público de metadados da Issue108, com proveniência integral.

- [x] Inventariar 17 candidatos, identificadores, programa/depositário/lastro/unidade IF.data, datas, natureza/confiança/conflitos, fontes e ausências. Zero admissão automática.
- [x] Revisar proposta de suplemento finito; especificar fonte/claim/pontas/papéis/datas e validação/tamper antes de escrever comportamento novo. CNPJ/notícias/pesquisa são permitidos, sem prova jurídica universal, mas sem identidade por nome ou retroprojeção temporal.
- [x] Admitir o recorte sustentado e exibir não resolvidos; replay e revisão independente de fontes/composição antes de ampliar.

### R4 — composição e entrega

- [x] Relatório/consulta evidencia companhia → instrumento/registro → unidade IF.data, com tipo, fonte, datas sustentadas, entradas/saídas/mudanças observáveis e lacunas. Sem adotar amostra acadêmica por disponibilidade.
- [x] Registrar todos os resultados/limites no ledger público existente; atualizar arquitetura para inventário final, sem duplicar tracker.
- Gate final — Full checks pertinentes no marco final, revisão independente do SHA entregue e allowlist; PR, integração, ancestralidade e CI pós-merge. Só então atualizar aceite da108/mapa2 e Goal, preservando decisões3 e pesquisa111 próprias.

## Checkpoints posteriores e suplemento R3 contratado — 2026-10-14

R1 concluída no SHA `c224dedbad0ed35b9b7450b11da5c03c24340c82`, 20 testes/revisão independente PASS. R2 encontrou falso conflito por preenchimento zero de código CVM; correção R2a `661ef9eaaa970a7882608378ffea9f81081b89c7`, 22 testes e review fresco PASS. Primeiro pacote/replay ficam diagnósticos, sem aceite de domínio. Novo pacote `historical-issuer-links-resume-v2-code-key`, pin `5d3f1fa01872c50b581218be28e602722af242190fd549388ea487a23b859ba0`: build38,094s, verify87,219s, replay37,000s/verify86,453s;11arquivos integralmente iguais e três inputs intactos. Revisão independente do delta de domínio PASS; consulta BB201012/financeiro passou em86,203s. Core técnico local revisado, sem implicar conclusão108/amostra.

Contrato R3 adotado na spec existente e na [Issue108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6160293510), após revisão de desenho com quatro P2 resolvidos. Mesmos três arquivos de código/CLI/testes, sem novo módulo/dependência. Root documentação/Git/CI; curador em inputbundle novo e preparação privada, separado do writer de código.

### R3a — índice curado e evidência autenticada

- [x] RED para schemas exatos/quatro listas/IDs/pins/bytes/paths/projeções/excertos Unicode; preservar strings/null/vazio e rejeitar duplicata antes de ordem canônica.
- [x] RED para matriz de tipos/papéis/namespaces/literais, datas e referência, DAG e clausura transitiva de fontes/estados necessários; não lavar blocked/shell/search/conflict em associação terminal.
- [x] GREEN da API `validate_issuer_supplement_index(index, expected_index_sha256, evidence_root)` e helper privado de admissão; CLI `supplement-check`. Não derivar relações nem produzir pacote real aceito nesta fatia.
- [x] Focados pertinentes, snapshot/diff/commit e revisão independente antes de ampliar R3b. Curadoria de input pode avançar em ownership distinto, mas claims compostos só passam após review semântico próprio.

### R3b — derivação pontual, pacote e consultas

- [x] RED para sete JSONs/evidências deduplicadas/inventário fechado, reconstrução do índice sob pin externo e tamper/repin; core imutável e uma única autenticação/carga por operação.
- [x] RED para associations/undated_associations/derived_unresolved separados do unresolved curado; candidato sem relação continua visível; companhia→instrumento→operadora→unidade preserva namespaces, tipo, fonte, data, confiança e lacuna.
- [x] GREEN build/verify/query e trio opcional da consulta core conforme assinaturas/schema da spec; matriz temporal impede expansão de desconhecido para60referências e não atribui vigência a anúncio/publicação.
- [x] Regressões core/suplemento, review independente, depois build real do input curado revisado, verify/query/replay em destinos novos; confronto integral e revisão de domínio/composição.

### Curadoria paralela, limites e pausa

Inputbundle novo PRIMARY `data/raw/historical-issuer-supplement-resume-v1/`, budget256MiB/índice4MiB; cópias por hash e projeções dos originais existentes, sem nova coleta, movimento ou sobrescrita. Corpus17BDR+fontes globais revisadas e três companhias/20claims do dossiê105 aceito, pin `5aaf7c8d8beb0dc5fb496483cdfec5d275e6e8865441d7f0473712ad1374812b`. Candidaturas, fatos e compostos propostos permanecem distintos do aceite. Outputs novos `data/curated/historical-issuer-supplement-resume-v1/` e-replay.

João determinou pausa caso não conclua em três horas: limite `2026-10-14T06:29:39Z`, 03:29:39SãoPaulo. Não iniciar nova execução/coleta/teste/publicação/integração após o limite; interromper somente processos/agentes próprios, preservar checkpoint e marcar Goal paused, sem encerramento artificial da108. O monitor privado lê deadline persistido; controller confere o relógio entre etapas.

Estado dos gates finais de SHA/checks/publicação/integração/CI pós-merge e encerramento: autoridade na Issue108 e na PR vinculada, com evidências datadas. Os checkpoints acima registram execução local/revisada e não antecipam o sucesso desses gates. O Goal só fecha após sua confirmação; o deadline humano permanece aplicável enquanto incompleto.

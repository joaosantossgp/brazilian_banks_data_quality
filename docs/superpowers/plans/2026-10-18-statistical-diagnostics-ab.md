# Execução dos diagnósticos e robustez — camadas A e B

> Execução por fatias com Superpowers planejamento, TDD, revisão independente e verificação; instrumentos finitos privados, sem novo motor de produção.

**Objetivo:** executar as camadas 1 e 2 autorizadas por João na [Issue 175](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/175), sem interpretação ou inferência. **Desenho:** [protocolo 173](../../engineering/statistical-treatment-protocol-20261018.md). **Stack:** Python/Fraction/Decimal, DuckDB 1.5.6 e helpers existentes. **Base:** `970e3f3417a83a84eca9adf369176348e39f19b9`, branch `codex/statistical-diagnostics-ab`, worktree isolado já anexado.

## Contrato e entradas

Ponteiro financeiro descoberto e manifesto autenticado no início: `historical-links32-composition-20261018-run3`, SHA256 `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`. Macro descoberto no mesmo ponteiro: `macro-context-20261018-run2`, manifest `9920b6ebe130854130ab9ec7e7bfe98410556f22f81b969128be2704be8de118`, autenticado; séries não necessárias para A/B e não consumidas. Reconsultar ponteiro antes de cada expansão e entrega; eventual promoção exige nova execução explícita no novo pin, preservando anterior, conforme pedido de usar a última aceita.

Allowlist pública: este plano e `docs/engineering/statistical-diagnostics-ab-20261018.md`. Preparação/instrumentos/testes/saídas/revisões/ZIP: `.scratch/statistical-diagnostics-ab/`, destinos novos por tentativa. Responsabilidades canônicas existentes, sem raiz/camada/módulo/dependência nova; nenhum rename/delete. Root integra apenas os 2 Markdown, sem arquivos compartilhados. Pacote aceito, ponteiro, fórmulas, manuscrito, explorador e frentes paralelas preservados.

## Recorte fixado antes dos resultados

- Todas métricas/janelas 2010–2024 disponíveis, por perspectiva separada. Sistema e coortes disjuntas; Tcb e SrAnalitico isolados, com estados e janela própria. Individual complementar separado. Não há segmentação macro nem novo vínculo.
- A: unicidade e correspondência de identidade, status/aplicabilidade/ausências/flags, sinais/componentes, cobertura e quantis tipo2 existentes; reconciliação exata com agregados e células aceitos. Separar nominais sem contribuição e nativas. Sem limiar de exclusão/extremo: inventário ordenado e influência medem amplitude sem apagar observações.
- B: retirada de cada unidade elegível do agregado geral/Tcb/SrAnalitico. Guardar todos os resultados em arquivo privado comprimido e resumo por contexto; denominador remanescente zero vira não calculável, não zero.
- B composição: todos os pares trimestrais consecutivos, dezembros consecutivos e primeiro–último disponível de cada série. Interseção por código é **sensibilidade de reporte**, não certificação de identidade/perímetro econômico estável. Registrar mudanças de classificação e flags; não sustenta painel inferencial.
- Agregado/distribuição e trimestre/TTM mantêm objetos distintos, lado a lado; não exigir mesmo sinal nem multiplicar trimestre por 4. Ausência e perda de cobertura explicitadas. Sem p-valores, normalidade, testes de diferenças, causalidade ou explicações econômicas.

## Fatias e gates

- [x] Escrever testes causais antes do instrumento: frações, duplicação, elegibilidade, quantis, denominadores assinados/zero, influência, conjuntos comuns e pareamento de calendário; observar RED e GREEN.
- [x] A piloto em contexto finito, autenticar tabelas consumidas e medir tempo/recursos. Inicial: RAM total ~31,7GiB/livre~7,9GiB; DuckDB 1 thread/2GB, sem instalação. Revisão independente antes de ampliar.
- [x] A integral: reduzir dados nativos completos, conferir linhas/identidades/estados e reconciliar todas as somas/contagens selecionadas com aceitos. Relatório de falhas/casos não comparáveis, sem exclusão silenciosa. Revisão independente antes de B.
- [x] B: influência completa e sensibilidades de composição, cobertura/horizonte/classificação, preservando componentes exatos e desconhecidos. Revisão independente dos dados e matemática.
- [x] Apresentação local: relatório em Markdown/CSV e ZIP privado com scripts/recibos; exemplos, critérios e hashes conferidos em revisão própria. A apresentação final explicita unknown junto às demais coortes; a versão anterior foi preservada.

Publicação e integração têm rastreio na Issue 175: conferir diff/links, inventário e SHA final, revisão independente, CI pertinente, ancestralidade e CI pós-merge; depois atualizar a mesma Issue e o mapa 2. O estado remoto e seus hashes não são inferidos deste plano local.

Falhas/tentativas e revisões são preservadas; rerun isolado não transforma tentativa global falha em PASS. Métodos inferenciais da camada C continuam pendentes de decisão humana.

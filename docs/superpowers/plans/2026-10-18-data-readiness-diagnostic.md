# Diagnóstico de prontidão dos dados — plano

> Execução nativa por Root com Superpowers executing-plans; pesquisa e revisão independentes por fatia. Contrato de desenho: [Issue176](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/176), sob autorização de18/10/2026.

**Objetivo:** quantificar e classificar as limitações antes de decidir as mudanças finais e o congelamento dos dados.

**Arquitetura:** somente leitura de pacotes autenticados pelo ponteiro compartilhado; instrumento finito privado em `.scratch/data-readiness/`, nota em `docs/engineering/data-readiness-diagnostic-20261018.md`. Nenhum motor, módulo, pasta pública, dependência ou dado aceito muda. Python stdlib/Fraction e DuckDB existentes. Tabelas e reprodução completas ficam privadas; este plano e a nota são os únicos arquivos públicos.

**Entradas fixas:** composição `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`, macro `9920b6ebe130854130ab9ec7e7bfe98410556f22f81b969128be2704be8de118`. Referência inicial `96a678b4b206a27d9b87de12f43f28158583adc7`; base efetiva do worktree `970e3f3417a83a84eca9adf369176348e39f19b9`, já contendo a PR174 documental. Diff próprio restrito aos dois Markdown. Não mudar ponteiro, explorador, indicadores ou manuscrito. #175 conserva robustez/influência/composição; saídas dessa frente só entram como evidência após aceite, sem mensagens ou escrita alheia.

## Fatia1 — inventário piloto verificável

- [x] Autenticar manifests e tabelas consumidas, registrar recursos e hashes do instrumento.
- [x] Testes causais: coortes disjuntas/total, deduplicação de companhias, frações e contagens; zero versus ausente; estoques desconhecidos/negativos; faixas descritivas.
- [x] Executar Financeiro/ROA12meses/4T2024, por total/Tcb/SrAnalitico/cruzamento, e conferir contagens/pesos contra agregados e segmentações aceitos. Não reavaliar fórmulas.
- [x] Revisão independente antes de ampliar.

## Fatia2 — cobertura completa, causas e prontidão

- [x] Executar todos os contextos2010–2024 das três perspectivas, sistema/sample/remaining/unknown, com contagens, AT/crédito/PL próprios conhecidos, motivos, estados e listas nominais. Períodos sem observação e Sr antes do regime ficam explícitos. Não emprestar AT ao Prudencial.
- [x] Resumir janelas consecutivas de lacunas, incluindo entrada/saída de categorias e mudança da composição. Quantificar agregado ausente versus interseção reduzida, sem atribuir valor contrafactual aos ausentes.
- [x] Conferir estoques agregados uma vez por unidade/período e as25séries macro: janela, status, unidades, lacunas e proveniência. Separar cobertura da plausibilidade econômica e da inferência.
- [x] Confrontar causas com fontes/código e diagnósticos já capturados; registrar resolvido/investigável/adaptação acadêmica/estrutural e incertezas. Pesquisa externa ou coleta adicional não autorizadas nesta entrega.
- [x] Revisão independente de composição, dados e propostas. Entregar lista finita de mudanças com impacto/esforço/ressalva; dependência explícita do aceite175 para robustez antes do congelamento final.

## Faixas e limites de leitura

Contagens0,1,2–4,5–9,10+e cobertura conhecida<80%,80–95%,95–100%,100%organizam o inventário; não são cortes de amostra nem regra de validade. Frações exatas são preservadas, percentuais de apresentação arredondados explicitamente. PL ou outros pesos assinados não viram proporção convexa.100%do conhecido não mede unidades sem estoque. Recorte pequeno pode cobrir muita atividade e recorte numeroso pode excluir unidade grande. Não confundir baixa representação das abertas com falta de cobertura do sistema.

## Encerramento

Revisão e integração finais registradas na [Issue176](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/176): inventário dos dois Markdown, links/coerência/whitespace, SHA entregue, PR/checks, ancestralidade e CI pós-merge; atualizar176 e mapa2. Nenhum rename/delete. O goal encerra o diagnóstico, sem declarar congelamento acadêmico.

## Checkpoint da execução

Piloto revisado antes da expansão. Execução aceita full-run3:305.296células,285.514contextos,12.230reconciliações gerais e730contextos vazios verificados;86,8s,sem recálculo financeiro. Quatro testes causais PASS e5.916contextos de conferência independente estratificada sem divergências. Estoques14.573contextos/zero variantes;macro22×60+3×52. Detalhes e prioridades na [nota final](../../engineering/data-readiness-diagnostic-20261018.md). Tentativas falhas preservadas e separadas do PASS. A lista nominal compactada é exemplificativa;100%conhecido não cobre peso desconhecido.

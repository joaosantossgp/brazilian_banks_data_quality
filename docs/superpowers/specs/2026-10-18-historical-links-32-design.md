# Vínculos históricos das 32 companhias — especificação

Estado: aprovado por João em18/10/2026, Issue156; execução nativa e revisão independente por fatia. Síntese da conversa pelo workflow Matt to-spec, com vocabulário do glossário e destino canônico. Não altera a decisão de coorte2024 nem promove vínculos.

## Problem Statement

Recortes temporais da seleção parecem sem dados mesmo quando uma operadora possui indicadores: o vínculo histórico pode estar desconhecido. Em Oliveira Trust, a DTVM tem60observações e apenas4T2024 é associado à holding. Usar a relação atual em todo o passado daria controle inexistente ou não provado; conservar desconhecidos onde existe prova também prejudica a análise.

## Solution

Auditar 32×60 posições nominais e corrigir apenas relações sustentadas por evidência temporal, começando por Oliveira. Preservar o universo técnico e todas as frações financeiras. Atualizar coortes, cobertura e recortes atingidos em pacote novo, com originais/proveniência e comparação exata. A base vigente só muda após aceite independente e atualização explícita do ponteiro compartilhado.

## User Stories

1. Como pesquisador, quero ver cada uma das32companhias nas60datas, inclusive quando não há unidade associada.
2. Quero distinguir holding, operadora e unidade reportante para não atribuir balanço de conglomerado à emissora indevidamente.
3. Quero uma fonte datada para cada admissão ou regra de intervalo temporal.
4. Quero manter desconhecido e conflito sem convertê-los em vínculo negativo.
5. Quero corrigir primeiro Oliveira, sem aplicar sua regra automaticamente às demais.
6. Quero identificar períodos anteriores à constituição, aquisição e reporte na perspectiva.
7. Quero preservar cada valor de indicador já calculado e recompor apenas os recortes afetados.
8. Quero ver Financeiro como principal e Individual/Prudencial com identidades próprias.
9. Quero que companhias com a mesma unidade não multipliquem os valores agregados.
10. Quero preservar o literal incorreto da fonte e usar corroboradores explícitos, como4T2023.
11. Quero saber quando um TTM inclui desempenho anterior ao controle observado no fechamento.
12. Quero reproduzir a seleção por comando/pins e localizar a versão aceita em outra task.
13. Quero distinguir alteração de membership de mudança científica de amostra ou fórmula.
14. Quero receber uma PR revisada com resultados/limites, sem dados privados no Git.

## Implementation Decisions

- Coorte de referência2024 mantida; não criar população dinâmica nem excluir períodos pré-IPO por decisão técnica.
- Oliveira: candidatas as15datas202103–202409, conservando202412. Fontes por fechamento sustentam controle indireto; sem ponte positiva para2010–2020.
- Vínculo é avaliado no fechamento. TTM com componentes anteriores ao controle recebe ressalva; não reconstruir resultado exclusivamente sob controle sem decisão acadêmica.
- Prova documental societária e cadastro IF.data contemporâneo são verificações distintas. Conflito de código/perímetro recusa promoção.
- Reusar o módulo de população, leitores autenticados e redutores existentes; sem novo módulo, dependência ou arquitetura. Entrada de evidência opcional e versionada mantém compatibilidade da operação atual.
- Cada claim contém identidade da companhia, operadora, referência, fonte/hash/localizador e natureza da relação. Não inferir por nome, código atual, maioria de membros ou mera continuidade aparente.
- Comparar mapas antigos/novos e calcular a allowlist exata de unidades, períodos e coortes. Atualizar metadados e reduzir contextos afetados; nenhuma fórmula financeira será chamada.
- Totais financeiros do sistema observado devem permanecer iguais: apenas atribuição às coortes/companhias pode mudar. Não confundir total inalterado com todas as listas/contagens nominais inalteradas.
- Não executar compose/build global por rotina. Medir um contexto afetado antes de ampliar; guardar pacotes anteriores e resultados fora do recorte exatamente.
- Sr e Sr analítico continuam distintos, com semântica prudencial oficial, data e origem. Esta entrega não preenche Sr/SegmentoTb nem muda seus métodos.

## Testing Decisions

Seam principal: entrada de evidência + cadastro/mapas → membership datado e composição armazenada. Testar comportamento observável com fixtures pequenas, não contagem de consultas nem prosa.

- TDD na função pura de vínculo e no estágio seletivo:15novasdatas,202412igual,2010–2020semretroação; CNPJ distinto recusado, fontes/pins divergentes recusados e desconhecidos preservados.
- Exercitar conglomerado financeiro/prudencial divergentes, parent ausente/ciclo, targets concorrentes e companhia repetida sem duplicar unidade.
- Comparar frações/status/janelas/assinaturas econômicas antes/depois para todas as contribuições; proibir chamada ao avaliador de fórmulas na recomposição.
- Conferir coortes disjuntas, N/D e distribuições por redução independente; total do sistema financeiro inalterado e contagens nominais reconciliadas.
- Preservar arquivos/payloads não atingidos e recusar destino existente ou sobreposto às fontes.
- Conferir HTML contra tabelas e filtros; dados/recibos privados fora do Git. Revisão independente factual e por fatia precede expansão.

## Out of Scope

Coleta financeira nova; seguros/securitizadoras sem associação principal; ampliar55ou32; proxies/fórmulas; retroagir Sr; emendar perspectivas; atualizar silenciosamente tarefas paralelas; editar Word; outros computadores/repos; alterações de CI/segurança/Project3.

## Further Notes

[Pesquisa e fontes](../../engineering/historical-company-links-32-20261018.md). [Plano candidato](../plans/2026-10-18-historical-links-32.md). A leitura factual inicial dos32×60mapas é concluída, não validação societária integral. As etapas dependem da revisão do plano e da divisão, conforme to-spec/to-tickets/writing-plans solicitados.

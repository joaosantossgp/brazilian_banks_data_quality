# Prontidão dos componentes dos indicadores por Tcb — 18/10/2026

Resultado da [Issue181](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/181), primeira fatia do [plano seletivo](../superpowers/plans/2026-10-18-tcb-indicators.md). Inventário de disponibilidade do sistema observado completo, sem cálculo de novas razões ou adoção metodológica. A entrega local e a revisão têm recibos próprios; integração remota e CI são verificadas na Issue.

## Entradas, alcance e preservação

O ponteiro compartilhado foi descoberto pelo diretório Git comum, conforme o [comando canônico](local-queries-20261013.md#base-de-indicadores-vigente-entre-tasks). Base de código inicial `2e365173ed140912d5d190f84c5e2a74659a5b26`; Root é writer da nota e da preparação privada, branch `codex/tcb-entradas-cobertura`. Nenhuma mudança estrutural: engenharia e preparação existentes, sem novo módulo/camada, rename/delete ou alteração de arquivos compartilhados.

| Entrada | SHA-256 do manifest |
|---|---|
| Composição aceita, `historical-links32-composition-20261018-run3` | `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60` |
| OData Financeiro, `ifdata-odata-20261011/financial` | `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095` |
| Catálogo, `ifdata-variable-catalog-20261011` | `73d8e09c5662bbf8f2b4865802dfec376e8a3da3c358ca81aa3695e881171ffd` |
| Abertura200912, `ifdata-universe-opening-200912-20261014-run1` | `ead666b2223173789591a1d599dd670c96a44bc110679afc89152289c904d8e4` |
| Cadastro contemporâneo, `ifdata-cadastro-20261011` | `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1` |

Autenticados os Parquets consumidos da composição, catálogo, cadastro e partes OData/abertura; hashes completos individuais no recibo privado, revalidados no encerramento do instrumento. Cadastros conservam URL/data de coleta, arquivo e hash da fonte da própria unidade/data. Macro, Capital e Individual não são consumidos nem fundidos com Financeiro Tipo2.

## Desenho da auditoria

Reaproveita criticamente a [auditoria178](tcb-indicators-assaf-atlas-20261018.md#viabilidade-comprovada-agora-e-o-que-falta), ampliando-a com coortes, sinais por componente, estoque conhecido/desconhecido e dependências temporais. Os [diagnósticos175](statistical-diagnostics-ab-20261018.md) e [176](data-readiness-diagnostic-20261018.md) permanecem evidência própria: não foram refeitas suas distribuições, influências ou correções.

São 89.476 unidades-trimestre financeiras, 60 referências201003–202412. Tcb, SegmentoTb, Tc, Td, Sr original e SrAnalitico derivado permanecem campos separados; o status cadastral/derivação é conservado. Atividade não é filtro nem critério inferido. Mesmo código/contexto não certifica estabilidade econômica da unidade.

A população parte da tabela aceita de unidades, conferida contra OData; cadastro ausente, código nulo e linhas fora dessa população são inventariados, nunca convertidos em zero. Duplicidade da chave literal interrompe. Os grupos total/sample/remaining/unknown são conservados, com total igual à soma das três coortes disjuntas em cada contagem; o total não é outra coorte aditiva.

O inventário nominal registra código, nome, companhias, classificações, estado de cada componente, coorte e faltas de histórico por candidato/unidade/data. Um roster adicional conserva todas as55companhias e seus vínculos aceitos, inclusive as23sem unidade principal admitida em2024. O filtroR1/quarter da tabela aceita serve apenas para escolher uma cópia do roster: a elegibilidade de R1 não é transferida para candidatos. Contagens de companhia e unidade não se somam.

| Conjunto investigado | Financeiro: relatório/contas | Natureza |
|---|---|
| L1, encaixe | Ativo2/78188; Passivo3/78282 | Estoques; sinal de DV contemporâneo |
| R3, margem LL/RIF | Resumo1/78187; DRE4/78208 | Fluxos; sinal nativo contemporâneo de RIF |
| RIF_AT, geração de RIF sobre ativo | DRE4/78208; Resumo1/78182 | Fluxo e pontos de estoque para média |
| PL_DEP, capital sobre depósitos | Resumo1/78186; Passivo3/78287 | Estoques |
| Arrendamento | Ativo2/78194,78195,78197,78198; DRE4/78204,78211 | Conjunto diagnóstico; fórmula depende da183 |
| Renda ampliada | DRE4/78215,78213,78216,78217,78218,78219,78221,78222,78223 | Conjunto diagnóstico; fórmula depende da182 |
| Contextos residuais de arrendamento | Ativo2/78196, grupo Arrendamento Mercantil/(e3) e grupo nulo/(j) | Duas células separadas, sem soma ou equivalência adotada |

Grupo, nomes e descrições literais completos, versões e períodos ficam em `catalog-contexts.json`. Os IDs da tabela são IF.data, não códigos Cosif. Os dois contextos78196 foram identificados quando a guarda interrompeu a primeira seleção por número de conta; o inventário adicional verifica ambos, sem torná-los requisito automático de um indicador de arrendamento.

Para fluxos, a disponibilidade trimestral exige a referência corrente e a anterior nos fechamentos de junho/dezembro. TTM exige quatro trimestres consecutivos e suas dependências nativas; média do ativo exige também o estoque de abertura. Mudanças literais são contadas separadamente. Nenhum fluxo foi reconstruído nem média calculada nesta auditoria. As pontes2019/Terra/Caixa e a liberação canônica de bindings não são aplicadas por analogia; isso pode produzir cobertura diferente da elegibilidade de indicadores atuais.

## Resultado contemporâneo e histórico disponível

Em202412 há1.422unidades:24sample e1.398remaining; unknown tem zero observado nesse corte e permanece categoria possível nas demais datas. As32companhias com vínculo compartilham24unidades; as23sem unidade continuam nominais. Presença finita inclui zero e negativo; não equivale à aplicação econômica.

| Conjunto | Esperadas | Componentes atuais finitos | Denom. positivo / zero / negativo | Histórico trimestral finito | Histórico TTM finito |
|---|---:|---:|---|---:|---:|
| L1 | 1422 | 1415 | 676 / 739 / 0 | — | — |
| PL_DEP | 1422 | 1415 | 969 / 446 / 0 | — | — |
| R3 | 1422 | 1415 | 1389 / 16 / 10 | 1391 | 1352 |
| RIF_AT | 1422 | 1415 | 1415 / 0 / 0 | 1391 | 1336 |
| income_wide_inputs | 1422 | 1415 | Sem denominador adotado | 1391 | 1352 |
| leasing_inputs | 1422 | 1415 | Sem denominador adotado | 1391 | 1352 |
| leasing_residual_contexts | 1422 | 1415 | Sem denominador adotado | — | — |

O sinal acima é da conta nativa na data: não é sinal de fluxo trimestral/TTM reconstruído nem da média futura. As sete unidades sem componentes atuais têm AT/crédito/PL desconhecidos. Há cinco PL negativos conhecidos no corte; seus valores foram preservados. A base não autoriza inferir inatividade ou inadequação a partir de saldo zero.

AT, crédito e PL são somados como frações exatas, por candidato/trimestre/Tcb/coorte, para a população e a interseção contemporânea. Unidades sem estoque e estoques negativos possuem contagens próprias. A comparação mede representatividade sobre estoques conhecidos, sem estimar participação contrafactual de desconhecidos; somar valores nativos não elimina sobreposição econômica de conglomerados.

A matriz privada contém **8554 células** de cobertura e **626332 linhas nominais**; as células sem ocorrência de uma coorte não criam observações artificiais. O roster tem55companhias por período. Não se exige painel balanceado nem se excluem entradas/saídas para melhorar cobertura.

## Reprodução, revisão e limites

Preparação privada: `.scratch/tcb-entradas-cobertura/` no worktree desta frente. `audit.py full1` executado com o Python3.12/DuckDB já instalado, em 51.359s. Não houve instalação/coleta nova. `full1/receipt.json` fixa entradas/saídas e hashes; `coverage.json` e `coverage.csv` têm contagens e frações exatas; `nominal.jsonl` e `company_roster.jsonl` permitem identificar quais unidades/companhias; `unmapped.json` conserva linhas nativas sem correspondência; `specs.json` e `catalog-contexts.json` tornam explícito o recorte. Esses dados privados não são publicados no Git.

Tentativas falhas preservadas: decoding de caminhoGitUTF8; colisão por conta78196sem grupo; abertura que inicialmente incluía Tipo3 junto ao Tipo2. Foram corrigidas no instrumento, sem alterar dados. Piloto5:1.422unidades,9.954linhas,147células; revisão independente conferiu141hashes,35.550estados de componentes,4.234registrosCSV e estoquesFraction de todas as células. Delta piloto6: roster55e respectivo hash aprovados; demais saídas byte idênticas. Somente depois ocorreu a expansão60trimestres.

O inventário entrega disponibilidade nativa e suficiência temporal de componentes, **sem certificar calculabilidade, identidade temporal, adequação ou adoção**. Denominador futuro exige reconstrução canônica e tratamento de zero/negativo; ausência não vira não aplicabilidade. Não altera as20métricas existentes, ponteiro, explorador, população ou fórmulas. As conciliações182–188 podem usar esta entrada após o aceite independente; pilotos189–191 dependem das escolhas humanas explicitadas no plano.

Fontes e conceitos reaproveitados: [pesquisa143](financial-indicators-activity-review-20261016.md), [proveniência111](financial-dimensions-literature-20261014.provenance.md), [nota178](tcb-indicators-assaf-atlas-20261018.md) e contratos do código vigente `ifdata_odata`, `ifdata_variable_catalog`, `quarter_flow`, `flow_12_months`, `mean_stock`. Assaf2015,11.ed., cap.18,pp334/337/341–342, é leitura anterior identificada, sem alegar nova leitura nesta auditoria de dados.

Revisão independente integral por `review_181_pilot`: PASS sem achados materiais pendentes. Conferiu142hashes, população de cada um dos60trimestres contra OData, todas as626.332linhas nominais, contagens e estoquesFraction das8.554células,238.411registrosCSV e3.300linhas do roster. A suficiência histórica foi confrontada independentemente em528verificações,336nominais nos cortes201003/201412/201503/201812/201903/202412; essa prova temporal é amostral. As1.332mudanças literais deLL emR3/TTM/201903 ficam visíveis, sem liberação de equivalência. A âncora documental apontada foi corrigida. Recibo integral SHA-256 `6988f59dd50ddbe9424aace94604f45a8d8b103f8b703caf0ff6fab81f7232cf`; instrumento revisado `d2cd8ecd345aba43d5da97af74fc66221472bfc88e7d6a3adedac2435e2bf585`.

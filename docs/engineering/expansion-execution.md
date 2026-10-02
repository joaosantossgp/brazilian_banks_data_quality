# Fechamento documental da expansão IF.data

Computador conferido: **LAPTOP-U0J6PT8Q**. Repositório: `raiz deste checkout`.

João autorizou a execução da etapa, incluindo dezembro/2023. A execução local já foi validada; este fechamento documental não autoriza nova coleta ou escala. Unidade, janela final e elegibilidade de capital aberto permanecem decisões humanas. Fechamento documental reconferido em 2026-10-02T00:05:03.274180+00:00.

A leitura inicial confirmou que os resultados já estavam salvos, mas a última atualização documental não: o ledger de execução estava ausente e plano/cartões ainda diziam “não executado”. Os documentos foram reconciliados a partir dos arquivos atuais, com comparação de hash antes de cada escrita. Código, testes, scripts, dados, relatórios de resultados e cartão de decisão humana foram preservados; nenhuma nova coleta ou publicação.

## Cartão 01: cobertura e semântica — critérios cumpridos

- Gate aprovado: cadastro REST e tabela Resumo dos arquivos recuperados correspondem exatamente a 1.976 códigos em 201012 e 1.585 em 202412; sem duplicatas, códigos vazios, trimestre errado ou diferenças de conjunto. `data/derived/expansion-20261001/coverage.json` registra fontes, denominadores e hashes.
- A conclusão se limita aos snapshots adquiridos. Universo histórico e elegibilidade capital aberto são desconhecidos; falhas OData do piloto não equivalem a população zero. Em 202312 OData não foi tentado; o perfil registra essa distinção.
- Definições oficiais, IDs e tokens foram preservados. A auditoria existente comparou 17.610 células com chaves diretas e confirmou os valores. Outras 10.878 células não estavam naquela chave de definição: isso não prova faltante ou zero. O mecanismo calculado/cadastral/marcador continua desconhecido quando não verificado. Semântica de c33 não foi adivinhada.
- Estoques mantêm data de referência; resultados de dezembro abrangem julho–dezembro. Vintages, IDs e ausência estrutural de chaves permanecem separados de ausência econômica do conceito. Nenhuma derivação automática de Q4.
- Testes de divergência, duplicidade, código vazio/período errado, fonte HTTP500, estrutura e replay passaram. O replay existente do piloto permaneceu preservado; esta reconferência reconstruiu a composição de três trimestres apenas em diretório temporário.
- O resultado ponta a ponta é rastreável aos corpos/hashes já arquivados. Nenhum download financeiro foi repetido para fechar este cartão.

## Cartão 02: dossiê temporal — critérios cumpridos

O dossiê distingue emissor/CVM/CNPJ observado de unidade e namespace IF.data. Não há vínculo confirmado nos oito candidatos. Nome parecido, código truncado, CNPJ B3 numérico com zeros perdidos, status atual e datas de eventos não são tratados como identidade legal ou estado histórico contínuo. Registro/listagem históricos e tickers também permanecem desconhecidos.

| Caso / candidato | Referência | CVM do emissor | Código IF.data bruto | Vínculo histórico |
|---|---|---:|---|---|
| Banco do Brasil | 201012 | 1023 | `0` | `unknown` |
| Banco do Brasil | 202412 | 1023 | `0` | `unknown` |
| Bradesco | 201012 | 906 | `60746948` | `unknown` |
| Bradesco | 202412 | 906 | `60746948` | `unknown` |
| Itaú Holding | 201012 | 19348 | `60872504` | `unknown` |
| Itaú: banco operacional distinto da holding | 201012 | 19348 | `60701190` | `unknown` |
| Itaú Holding | 202412 | 19348 | `60872504` | `unknown` |
| Itaú: banco operacional distinto da holding | 202412 | 19348 | `60701190` | `unknown` |

Todos usam namespace `IFDATA_REST_CADASTRO_1006`, seleção individual; os códigos são strings brutas, não CNPJ completo comprovado. A holding 60872504 aparece separada do banco 60701190 nos dois períodos; atributos de agrupamento não criam controle societário, perímetro consolidado ou equivalência econômica. O CVM 19348 nas linhas do banco identifica o emissor investigado, não afirma que o banco operacional seja o emissor.

Para confirmar vínculo, faltam identidades legais completas das duas pontas e documento primário com relação, namespace/código exatos e data pontual ou intervalo que cubra cada referência. A API também exige URL, hash, horário UTC e localizador; o documento precisa efetivamente sustentar a relação. Dez corpos primários do dossiê foram reconferidos, e as oito linhas reproduziram exatamente a API. As fontes CVM/B3 contêm metadados apenas; nenhum acesso ao projeto CVM separado foi necessário.

Desconhecido não significa “não listado”, extinto ou inelegível e não determina exclusão da amostra. A entrega apresenta alternativas de unidade e seus impactos, sem escolher pelo pesquisador; por isso o cartão de entrega pode ser concluído e o de decisão permanece pendente.

## Lote 202312 e evidências preservadas

Somente 202312 individual/Resumo foi adquirido na etapa anterior, pelo portal oficial BCB: 1.552 instituições × 8 indicadores = 12.416 observações. Tokens: 9.772 numéricos, 2.632 zeros e 12 NI; sem duplicidades ou células ausentes na grade observada. 23 manifests, 39.689.207 bytes brutos, uma tentativa. Limites do novo lote: 80 MiB brutos/tentativa, 480 segundos totais, 150 MiB de reserva, até duas tentativas. O caminho OData novo é rejeitado antes da rede; original default 201012/202412 preservado.

Notas/colunas/vintage 202312 foram verificadas contra o catálogo anterior. As 19 definições do info202312 foram conferidas com o corpo HTTP e congeladas após a primeira aquisição em `bank_quality/schema-202312.json`, sem alegar pinagem prévia desse info. Mudanças em nomes, definições, unidades, notas ou vintage rejeitam aceitação automática. Descrição TCB 2023/2024 difere; não se conclui continuidade econômica das entidades.

A revisão independente anterior encerrou sem problemas Critical/Important pendentes após as correções de guardas e schema. Nesta retomada, 54 testes Python passaram; 52 corpos de evidência foram reconferidos por hash e 7 artefatos da composição foram reproduzidos idênticos em diretório temporário. Os três períodos somam 40.904 observações. Evidências originais somente locais, excluídas da publicação: `reports/expansion-20261001.verification.json` e `data/derived/expansion-20261001/collection.json`. Nenhum código ou coleta foi refeito.

## Cartão 04: decisão humana ainda necessária

Escolher a unidade principal: pessoa jurídica individual do emissor, banco operacional individual com vínculo provado ou conglomerado com perímetro documentado. Decidir tratamento de holdings/sucessões, janela temporal final e regra temporal de capital aberto, distinguindo registro CVM de evidência B3 de listagem/negociação e instrumento elegível. Exigir prova datada antes de confirmar vínculos; manter desconhecidos quando a prova faltar e evitar amostra formada apenas por sobreviventes atuais.

Os três meses de dezembro coletados são um teste técnico, não a seleção da janela final ou da amostra. As lacunas de prova e decisões acima são científicas; nenhuma nova aprovação da direção geral ou dos resultados técnicos está sendo solicitada. Sem escala automática, alteração acadêmica ou calendário.

## Estado local e organização

Repositório sem commits, branch `feat/ifdata-two-quarter-pilot`; nenhum push/PR/publicação. Nove skills Matt previamente verificadas e Superpowers global existente permanecem sem alterações. O Project privado existente é coordenado pela conversa principal; este fechamento atualizou somente documentos/cartões locais. O cartão 04 foi preservado integralmente.

Ferramentas não oferecem movimentação de chats ou verificação da associação interna ao projeto Codex. O checkout foi confirmado por hostname, caminho e estado Git; não se editou banco/configuração interna nem se automatizou a UI. A retomada solucionou o bloqueio de conexão para este fechamento.

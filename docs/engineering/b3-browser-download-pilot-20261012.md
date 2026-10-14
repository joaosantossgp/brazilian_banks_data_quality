# Piloto de download público COTAHIST 2010 pelo navegador

O piloto teve **resultado indeterminado por interrupção da ferramenta**. Foi submetida uma única seleção do ano 2010 no fluxo público normal da B3, com o evento documentado de download armado antes da ação. A ferramenta atingiu seu limite externo de execução e reiniciou a sessão antes de devolver a conclusão da seleção ou um caminho de download. Não foi confirmado arquivo concluído, não houve admissão e a seleção não foi repetida. Esse resultado não prova ausência do arquivo, falha do servidor ou indisponibilidade do canal de navegador.

Escopo: [Issue 108, contrato do piloto](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6136798477). A base desta frente é `f93d37f17898d69713d06f07bb393eb1f2444331`, na branch `codex/cvm-b3-history-2010-2024`. Este registro não altera as notas nem as tentativas de transporte anteriores.

## Fonte e ação observada

A [página oficial de Séries Históricas](https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-a-vista/series-historicas/) abriu no Brave pelo controle CUA. A interface apresentou o seletor anual, com opções de 1986 a 2026, incluindo 2010, dentro do [formulário oficial incorporado](https://bvmf.bmfbovespa.com.br/pt-br/cotacoes-historicas/FormSeriesHistoricasArq.asp). A correspondência do combobox de nome exato `Ano` foi conferida como única antes da tentativa. A pesquisa anterior preservou no formulário/script oficial a URL declarada [COTAHIST_A2010.ZIP](https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A2010.ZIP); ela não é uma URL efetiva confirmada para esta tentativa.

Havia 148.786.139.136 bytes livres no disco C antes da ação. A sequência submetida foi: armar `waitForEvent("download", {timeoutMs: 60000})`; selecionar a opção de rótulo `2010`; obter o estado da página. A chamada externa, com limite padrão de 30 segundos, retornou após 30,0683 segundos informando timeout e reinicialização da sessão. A atribuição interna do horário UTC não chegou a ser devolvida, portanto o início exato permanece desconhecido. O diagnóstico foi registrado em 2026-10-13T02:25:55Z, ainda 12 de outubro no fuso America/Sao_Paulo.

Após a interrupção, a listagem de abas ainda apresentou a mesma aba `1236808217`, com título “Séries Históricas | B3” e a URL do portal. Duas tentativas somente de recuperar o controle dessa mesma aba devolveram `Debugger unattached`. A documentação `browser-troubleshooting` foi consultada. Não foi encontrado mecanismo documentado para recuperar o handle perdido ou listar downloads já iniciados. Não houve novo clique, nova seleção, GET/HEAD adicional, download de BDI, exportação de cookies ou contorno de restrição.

## Recibo e limites

O recibo próprio está no checkout principal em `data/raw/cvm-b3-history-20261012/cotahist-browser-pilot/receipt.json`. Não contém corpo ZIP. Registra o ano, as URLs declaradas, a ação submetida, a interrupção, as reobservações e os campos desconhecidos. O caminho original, tamanho, hash do ZIP, conclusão do navegador e horário inicial são `null`, com motivo explícito. A existência ou ausência de um arquivo fora desse destino não foi investigada nem inferida.

A API documentada oferece `PlaywrightDownload.path()`; não oferece status HTTP, headers, URL efetiva, GUID ou content-length. Esses metadados ficam `null` mesmo que um futuro piloto consiga devolver um arquivo, salvo nova evidência documentada. A ferramenta também não oferece limite de bytes ou cancelamento durante o transporte. Os limites contratados de 64 MiB para o ZIP, 512 MiB de expansão total e 256 MiB por membro são limites de verificação posterior, e não proteção aplicada à rede.

Sem arquivo retornado, não foram executadas verificações de nomes, unicidade de membros, CRC, expansão ou perfil físico de linhas/cabeçalhos/rodapés. Nenhum preço, volume ou saldo foi projetado. A causa observada limita-se à ferramenta: o timeout externo perdeu o estado necessário para confirmar a etapa alcançada. Não foi possível determinar se a seleção apenas preparou outro controle ou iniciou o download.

## Consequência para a pesquisa

O portal acessível e a oferta anual visível continuam sendo evidência distinta das falhas HTTP anteriores. Este piloto acrescenta uma falha de observação da ferramenta, sem resolver a disponibilidade dos bytes. A próxima decisão técnica precisa considerar essa perda de handle antes de autorizar nova tentativa; este documento não autoriza repetição nem expansão para outros anos. O resultado e o recibo seguem para revisão independente.

O [Acervo atual MUB3](https://mub3.org.br/centro-referencia/acervo), ligado pelo portal BDI e verificado na pesquisa anterior, também permanece uma rota documental distinta. A falha DNS preservada do domínio antigo `acervob3.com.br` não caracteriza o catálogo atual. Nenhum download desse catálogo foi realizado neste piloto.

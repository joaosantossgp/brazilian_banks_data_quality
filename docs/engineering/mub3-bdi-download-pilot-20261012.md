# Piloto documental MUB3 — BDI de 30/12/2010

O único clique autorizado em **Baixar documento** foi concluído sem erro, mas não foi observado evento de download nos 25 segundos de espera. O resultado permanece **indeterminado**, sem corpo confirmado ou admitido. A sessão continuou controlável; não houve a reinicialização que interrompeu o piloto COTAHIST. Não foi repetido o clique. Timeout não prova falha do servidor, ausência do documento, cancelamento ou conclusão do transporte.

O [contrato publicado na Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6136944840) autorizou somente este documento. Base da frente: `f93d37f17898d69713d06f07bb393eb1f2444331`, branch `codex/cvm-b3-history-2010-2024`. As notas e falhas anteriores permanecem preservadas.

## Fonte, ação e reobservação

O [registro público MUB3](https://mub3.org.br/centro-referencia/acervo/451f3d63a44b4c7a90bfa2eb76044263) carregou o título “Boletim Diário de Informações - BDI - 30/12/2010”, data 30/12/2010, coleção BM&FBovespa, local SÃO PAULO e tipo Textual. O catálogo descreve informações dos pregões, estatísticas de ações e cotações. Essa descrição não comprova formato físico, completude ou categorias específicas de instrumentos.

A aba da inspeção anterior já havia sido encerrada pela limpeza de abas de pesquisa. Foi aberta a mesma URL em nova aba no Brave existente, ID de navegador `1`, aba `1236808221`. Antes da ação, foram medidos 148.793.638.912 bytes livres em C, às 2026-10-13T02:35:12.9511303Z. O botão foi confirmado pelo localizador exato `getByRole("button", {name: "Baixar documento", exact: true})`. É um botão sem `href`; nenhuma URL de arquivo foi inventada.

Às 2026-10-13T02:35:27.271Z, foi armado `waitForEvent("download", {timeoutMs: 25000})` antes de um único clique, com timeout de clique de 10 segundos e limite externo de 60 segundos. O clique retornou sem erro. Às 02:35:52.321Z, a espera devolveu timeout de 25 segundos sem handle. O limite externo não foi atingido.

A reobservação da mesma aba mostrou o registro e os botões Baixar/Visualizar, com URL inalterada. Não foi observada nova aba de documento. A inspeção read-only dos links, iframes, embeds e objects em `main` e `#conteudo` retornou apenas links de navegação: âncoras de acessibilidade, página inicial e retorno ao acervo; não expôs recurso de documento. A consulta aos logs capturados de erro e aviso retornou vazia. Uma captura de tela foi exibida no resultado CUA; não foi persistida como artefato local. Nenhuma dessas observações confirma ou nega a existência de um arquivo baixado fora do mecanismo observado. Não se investigou o sistema de arquivos do usuário para presumir um destino.

## Preservação, verificações e limites

O recibo está no checkout principal em `data/raw/cvm-b3-history-20261012/mub3-bdi-20101230-pilot/receipt.json`. Preserva ação, horário UTC, espaço livre, timeouts, estado posterior e limites. Como nenhum handle ou caminho foi devolvido, original, corpo, bytes, SHA-256, formato e conclusão permanecem `null`. Não houve arquivo para copiar, testar assinatura, abrir, contar páginas ou extrair texto. Nenhum perfil de instrumento ou medida financeira foi produzido.

Status HTTP, headers, URL efetiva, GUID e content-length também ficam `null`: a API documentada expõe somente `path()` no handle de download, que não foi obtido. O timeout da espera não cancela o transporte. A API não oferece limite de bytes durante a rede; o limite de corpo de 64 MiB é posterior. Se houvesse ZIP, aplicar-se-iam 512 MiB de expansão total e 256 MiB por membro; se PDF, assinatura, abertura e no máximo 1.000 páginas seriam verificados antes de extração. Esses checks não foram executados sem corpo retornado.

Não houve login, CAPTCHA, aceitação de cookies, contorno de restrição, GET/HEAD adicional, acesso a outro item/ano ou nova tentativa de COTAHIST. O aviso de cookies permaneceu visível, sem interação. A ausência de restrição na leitura não certifica sucesso do download.

## Alcance

A fonte documental pública existe como registro legível e botão normal acionável. O piloto não resolveu o transporte dos bytes. A falta de evento na janela observada não deve ser convertida em indisponibilidade universal ou população zero. O resultado segue para revisão independente antes de qualquer nova ação ou ampliação. Mesmo um eventual documento obtido para esse dia exigiria leitura de capítulos e páginas: carteira de índice e anúncio de leilão não equivalem a negócio executado, e um dia de 2010 não prova permanência trimestral nem cobertura de 2010–2024.

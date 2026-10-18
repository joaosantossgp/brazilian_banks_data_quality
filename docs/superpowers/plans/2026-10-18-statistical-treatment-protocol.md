# Plano de pesquisa: tratamentos, testes e robustez

Issue [173](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/173). Root; base `96a678b`; branch `codex/statistical-treatment-protocol`. Pesquisa autorizada por João em 18/10/2026, após esclarecimento de que interpretação pertence a outra task. Entrega é **proposta**, adoção acadêmica permanece na Issue 3.

## Perguntas e evidência

1. Que observações, hipóteses e testes usa o artigo SOBER 2012 indicado? Ler metodologia, notas, tabelas e referências, com páginas.
2. Que tratamentos de ausências/extremos/denominadores e verificações de composição são adequados às razões IF.data?
3. Que perguntas justificariam inferência e quais testes respeitam dependência temporal, repetição institucional e agregação?
4. O que é essencial, condicional ou inadequado por rotina? Como registrar decisões sem selecionar resultados favoráveis?

Fontes: artigo indicado via Drive (somente leitura), literatura primária de testes/inferência, guia FMI, contratos e diagnóstico do pacote aceito. Separar fontes lidas integral/parcialmente, argumentos dos autores e proposta aplicada. Revisão narrativa dirigida, não sistemática/exaustiva.

## Escala e mecanismo

Pesquisa multifacetada: Root examina artigo/base e redige síntese; pesquisador em background investiga testes e tratamentos; verificador independente confere citações após rascunho; revisor independente confere protocolo e escopo depois da verificação. Feynman `deep-research`, `literature-review`, `pdf-explore` e Matt `research`, aplicados manualmente com ferramentas disponíveis; nenhum slash command/runtime é alegado. O pedido atual aprova a direção de pesquisa já apresentada; a confirmação rotineira upstream não será repetida.

O layout upstream `outputs/` é adaptado aos destinos canônicos: este plano; rascunhos, fontes e revisões privados em `.scratch/statistical-treatment-protocol/`; final e proveniência em `docs/engineering/statistical-treatment-protocol-20261018[.provenance].md`. Sem nova raiz/camada/dependência; sem interpretar dados nem executar tratamentos/testes inferenciais.

## Entradas, ownership e fatias

- Migração explícita da pesquisa anterior para o ponteiro aceito atual: `historical-links32-composition-20261018-run3`, SHA-256 `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`. Não muda o caderno 166. Autenticar tabelas se consumidas; não recalcular base.
- Allowlist pública: este plano, protocolo e proveniência. Root único integrador; pesquisadores/revisores só escrevem notas privadas próprias. Nenhum rename/delete. Não editar arquivos compartilhados ou outra frente.
- A: artigo + fontes + diagnóstico estrutural mínimo → revisão/verificação da evidência antes de ampliar para protocolo final.
- B: síntese do protocolo, matriz de procedimentos e proposta de execução futura → verificador, depois revisor; corrigir achados materiais.
- C: checks documentais, inventário e SHA entregue; integração se checks/revisão passarem; conferir main/CI e atualizar 173/mapa 2. Sem Project 3.

## Ledger, verificação e decisões

- Entrada: Issue 173 lida com labels/contrato completos; checkout primário limpo e worktree reutilizado limpo, nova branch baseada em origin/main após fetch.
- Artigo localizado por nome exato em Mono 2; extração legível disponível, conferir métodos/tabelas em várias páginas. Cópias privadas não entram no Git.
- Rejeição/limitação de fonte ou ferramenta será preservada; não representar leitura de resumo como corpo completo.
- Checks finais: links locais e externos centrais, páginas/claims, coerência econômica/estatística, allowlist, `git diff --check` e CI documental pertinente. Não executar suíte de software por alterações apenas Markdown.
- Método final, hipóteses/recortes/nível de significância/limiares continuam propostas para João/orientador; nenhum p-valor ou resultado inferencial será produzido neste contrato.
- Fatia A: revisão independentePASS, artigo/hash/páginas e pin conferidos; precisão editorial sobre payload inicial incorporada. Só então avançou a síntese.
- Fatia B: pesquisador metodológico concluiu; Root sintetizou. Verificador independente conferiu 17 URLs do draft e três Issues, PASS com precisões sobre WMW e condiçõesHAC/blocos incorporadas no protocolo. Reviewer de composição é solicitado depois desse gate, em sequência.
- Revisão C concluída PASS, sem achados materiais; espaçamento editorial corrigido. Checks documentais locais conferidos nos três paths; conferência final do SHA e CI pertencem ao fechamento da mesma Issue/PR. Não houve mudança de conteúdo acadêmico aprovado, dados ou código produtivo.

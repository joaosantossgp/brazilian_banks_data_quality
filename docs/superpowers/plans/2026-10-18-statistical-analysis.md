# Plano de pesquisa e análise estatística — 18/10/2026

> Execução por fatias com revisão independente; Issue [162](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/162). Root integra, pesquisadores produzem notas privadas e revisores leem snapshots delimitados.

## Escopo, perguntas e entrada

João autorizou pesquisa → spec → tickets → implementação/documentação pertinente. Pergunta de trabalho: como evoluem e diferem as dimensões econômico-financeiras no sistema observado, por Tcb e, quando pertinente, Sr/SrAnalitico, distinguindo unidades associadas às companhias e restante? A formulação acadêmica final e métodos novos dependem de João/orientador. O desenho não exige econometria nem a exclui antes da pesquisa.

Entrada privada fixa: `data/curated/ifdata-composition-terra-20261017-run2`, manifest SHA-256 `ce57545b643d9efcfbb09ee26234c97f131080627d42622c2b4cfbf998f7c524`. Contrato `ifdata-composed-analysis-v1`, 60 trimestres 201003–202412. Autenticar hashes das tabelas consumidas; não migrar automaticamente se o ponteiro mudar. Base Git inicial `f0c7014e3191f27bfe7399e6a4812aeb5fd49092`, branch `codex/statistical-analysis-162`, worktree próprio.

## Skills e mecanismo

- Matt research: pesquisa primária delegada e nota citada. To-spec/to-tickets: síntese e decomposição solicitadas expressamente por João; catálogo de labels local prevalece sobre ready-for-agent upstream.
- Superpowers brainstorming/writing-plans: desenho e plano técnico; autorização de sequência já concedida não decide método acadêmico novo. Revisão e verificação antes da expansão/entrega.
- Feynman deep-research e literature-review: wrappers /deepresearch e /lit sem runtime nativo validado. Revisão manual adaptada aos mecanismos disponíveis e destinos canônicos do repo, sem alegar execução dos comandos nem instalar runtime. Pdf-explore é aplicável: mapear PDF, ler métodos/resultados/limites, cruzar páginas e registrar localizadores.
- Sequência de literatura: plano → pesquisadores → síntese Root → verifier independente das fontes → reviewer independente da síntese citada → correções → nota e proveniência. Não confundir revisão narrativa dirigida com revisão sistemática exaustiva.

## Inventário e arquitetura

Allowlist pública: este plano; `docs/engineering/statistical-analysis-research-20261018.md`; companion `.provenance.md`; `docs/superpowers/specs/2026-10-18-statistical-analysis-design.md`. Staging exclusivo `.scratch/statistical-analysis-20261018/`. São responsabilidades documentais existentes, sem pasta pública, módulo, camada ou dependência novos. Implementação de produção somente no ticket com sua allowlist após evidência/spec. Nenhuma alteração no explorador, fórmulas, dados aceitos, ponteiro, manuscrito/Drive, REFERENCES, arquitetura ou arquivos das outras frentes.

## Fatias e ledger

| Fatia | Resultado verificável | Checks e saída |
|---|---|---|
| A — enquadramento e viabilidade | Objetivos das versões Drive recuperados por leitura; pin e tabelas consumidas autenticados; cobertura por indicador/perspectiva/coorte/Tcb/Sr identificada | Hashes, contagens, unicidade/granularidade, limitações de vínculos e estados; revisão independente antes de ampliar a síntese |
| B — literatura | Matriz técnica→pergunta/estimando→hipóteses→limites→saída; fontes primárias e localizadores efetivamente lidos | Verificação de URLs/atribuição; revisão do conteúdo econômico/estatístico; corrigir achados materiais antes da spec final |
| C — spec/tickets | Núcleo descritivo e extensões condicionais; implementação necessária de diagnóstico claramente separada de adoção inferencial | Dependências reais, allowlists, aceite; revisão final de composição, links e SHA |

## Busca e seleção

Literatura de agregação/distribuição e diagnóstico financeiro: FMI FSI2019, BCB IF.data/REB e estudos originais pertinentes. Literatura estatística: dependência serial/TTM, HAC, regressão espúria/estacionariedade, inferência em painel/poucos clusters, multiplicidade e seleção. Preferir autores/periódicos/instituições originais e texto completo para afirmações críticas; registrar falhas/acesso parcial. Não selecionar técnica apenas por frequência de uso em artigos.

## Verificação e decisões

Diagnóstico não recalcula indicadores financeiros: lê saídas aceitas e produz tabelas auxiliares privadas em destino novo. Cobertura temporal de um agregado não prova completude econômica dos componentes nem cobertura de companhias. Quantidades de companhias e unidades são distintas; listas truncadas no payload não permitem identificação exaustiva.

A pesquisa macro [159](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/159), vínculos [156](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/156)/[160](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/160) e analítico [152](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/152) têm ownership próprio. Pesquisa estatística pode avançar com o pin atual; adoção de SrAnalitico revisto ou vínculos novos requer migração explícita/revisão dos efeitos. Project3 permanece com Zec.

## Encerramento

Entregar nota/proveniência, spec/plano/tickets reais, evidências privadas verificáveis, revisões por fatia e final, status de publicação/integração e limites. Atualizar Issue162/mapa2; não encerrar a decisão3 nem presumir conclusão das frentes concorrentes.

## Checkpoints executados

- A: diagnóstico concluído no pin fixo; três tabelas autenticadas e IDs únicos. Revisão independentePASS em `review-A.md`,28.140 reconciliações categóricas e3.240 identidades das coortes, com limites incorporados à nota.
- B: duas pesquisas primárias concluídas; sínteseRoot escrita; verifier independente concluiuPASS com limites em `verification-literature.md`. Reviewer crítico posterior concluiuPASS B/C em `review-B-C.md`, semFATAL/MAJOR; ajustes menores de estado, tickets e redação quantitativa incorporados. Não substitui decisão acadêmica ou revisão final doSHA.
- C: [decisão165](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/165) e [entrega166](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/166) publicadas com labels completas e dependências nativas verificadas.165 depende162;166 depende162/165. Execução166 aguarda seleção acadêmica, não confirmação técnica rotineira.
- Reconciliação: fetch seguido de fast-forward limpo no worktree para `62a0b930db69334ebb5799e6f24775d438bdf7a2`; os quatro novos documentos não colidem com33paths integrados das outras frentes. A entrada financeira permanece a mesma. Pesquisa macro159 está disponível em sua [nota própria](../../engineering/macroeconomic-context-2010-2024-20261018.md), sem coleta completa presumida.

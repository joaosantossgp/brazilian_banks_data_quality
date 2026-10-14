# Plano — amostra fixa financeira em 2024

> Execução por fatias com pesquisa delegada e revisão independente, conforme AGENTS/workflow; Root integra. O pedido de João aprova o desenho e a execução abaixo, sem nova confirmação rotineira.

**Goal:** fechar lista auditável, sem grupos duplicados, de unidades IF.data ligadas a companhias brasileiras abertas em31/12/2024, com dados trimestrais2010–2024, verificação anual e cobertura econômica explícita.

**Issue:** [125](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/125). Base `4aea6f858692c3c2b1e22284797137e328c6e3d9`, branch `codex/fixed-financial-sample-2024`. Os21candidatos anteriores são triagem, não teto nem população certificada.

**Arquitetura:** análise finita sobre pacotes locais aceitos, ferramentas existentes e pesquisa documental pontual quando necessária. Sem novo leitor, framework, dependência ou camada; fontes aceitas imutáveis. Allowlist pública: este plano; `docs/engineering/fixed-financial-sample-2024-20261014.md`; `docs/engineering/institution-type-indicator-methodology-20261012.md`; `docs/architecture.md`. Root exclusivo. Preparação privada nova `.scratch/fixed-sample-2024/` neste worktree; resultados locais novos `data/curated/fixed-financial-sample-2024/` e replay no primário. Subowners privados em issuer-research/bc-coverage/root/review, sem editar paths de outro owner.

## A — universo e contrato de seleção

- [x] Reconstituir21candidatos; conferir classificação além de Bancos, instituições independentes e companhias omitidas pela exigência de presença simultânea em2022/2023/2024. Seleção é em2024, não sobrevivência nas três datas.
- [x] Conferir identidade/domicílio/listagem no ponto2024 por fontes; CAD corrente e país aparentemente inconsistente não decidem sozinhos. Companhia brasileira pode ter controlador estrangeiro; BDR de holding estrangeira fica fora deste recorte aprovado.
- [x] Separar companhias e unidades, mapeando compartilhamento/controle sem somar mesmo consolidado duas vezes. TipoInstituicao=2 é universo principal; independente preserva sua unidade quando pertinente.
- [x] Definir denominadores: companhias financeiras/ações em2024 por setor e evidência; unidades/estoques observados no universoBCB comparável; segmento bancário quando explicativo, sem excluir silenciosamente outras atividades.
- [x] Revisão independente de método/lista candidata, fontes e exceções antes da aceitaçãoB. Findings materiais corrigidos primeiro.

## B — execução, cobertura e verificação anual

- [x] Reusar manifests/pins108 e dados OData/cadastro; autenticar inputs e preservar hashes protegidos. Scripts finitos privados registram comandos/UTC/recurso e escrevem destinos novos.
- [x] Produzir lista nominal2024, companhia→operadora→unidadeBCB e razões de inclusão/exclusão/colisão/semcorrespondência; desconhecido separado de negativo.
- [x] Verificar15dezembros2010–2024 pelo cadastro nativo, códigos, grupos/líderes e documentos de mudanças relevantes; observar60trimestres de presença dos dados. Ponto2024 não retroprojeta aquisições nem preenche ausência; identidade/unidade anterior ficam documentadas ou desconhecidas.
- [x] Quantificar unidades distintas, ativos/crédito e outras medidas nativas pertinentes sem float, dupla contagem ou mistura de perspectivas. Reusar reconciliação120/117; sete ausências e falta de correspondência mantêm limites. Cobertura histórica somente onde denominadores e contratos comparáveis.
- [x] Conferência independente/replay da seleção, agrupamento, anuais, numeradores/subconjuntos/denominadores e exclusões. Sem impor cota de empresas ou percentual de aceite inventado.

## C — entrega e encerramento

- [x] Nota final com tabela nominal, exclusões justificadas, omissões pesquisadas, representatividade nas abertas e noBCB, mapa anual e limites; CSV/JSON locais auditáveis.
- [x] Atualizar nota metodológica e Issues3/2 com decisão humana da amostra fixa, preservando histórico; não adotar fórmulas ou retomar111.
- [ ] Revisão independente do diff/allowlist e SHA final; links/coerência e checks pertinentes. Suíte de software só se houver delta de código; CI existente preservado.
- [ ] PR anexada, integração normal, ancestralidade/árvore e CIpós-merge confirmados; Issue125 eGoal encerram somente com requisitos comprovados.

## Duração e limites

Entrega concentrada em horas por reuso/consultas e tarefas independentes, evitando implementação de1–3dias. Não inventar aceites para cumprir prazo. Se surgir exceção que impeça fechar o objetivo, registrar impacto e resolver a parte técnica disponível; mudança de recorte/objetivo permanece humana. Não exigir painel balanceado desde2010 por disponibilidade, nem preencher anos anteriores à existência. Pesquisa bibliográfica de indicadores, Word, deploy, runtime, credenciais, proteções eProject3 fora do escopo.

## Checkpoint de execução

A/B e artefatos locais:24companhias/20unidades principais; complementares12pares/noveunidadesnativas+CartãoBRBsemâncora, semsoma.60trimestres/1.236chaves financeiras;360verificações anuais principais e180complementares.225coberturas recalculadas e221arquivos idênticos no replay; manifest `bf54640a70964ca8468cdefc1fc2aaf53d1aab8985779005de21fc9b847467eb`. Desconhecidos anuais, referênciasFREfora31/12 eBRB202209null preservados. Revisões parciaisPASS com fontes/pins, incluindo correções deAlfa/Itaúsa eRedecardp6/p7. Lista principal não é todo footprint controlado nem censoB3certificado. Integração eSHAfinal/checks são conferidos naIssue125/PR, sem antecipar estado pelos checks acima.

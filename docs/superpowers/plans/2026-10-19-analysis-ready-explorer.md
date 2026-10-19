# Verificação econômica e explorador para começar a análise

> Execução in-line por Root, com revisão independente antes de ampliar cada fatia. Contratos: [Pesquisa198](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/198) e [Entrega193](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/193). Este plano implementa o pedido de João de19/10/2026; não decide o fechamento acadêmico final.

**Objetivo:** verificar se os níveis dos indicadores fazem sentido, preparar uma entrada inequívoca para a próxima tarefa e entregar um explorador intuitivo com os dados já aceitos.

**Arquitetura:** reutilizar pacotes imutáveis, aritmética e exportador existentes. Instrumentos econômicos finitos ficam privados; interface autocontida apresenta valores persistidos e agregações explícitas, sem calcular indicadores novos. Não instalar dependências ou alterar amostra/fórmulas.

## Entradas e limites comuns

- Base pública inicial `a7a61bc26e919534ea63b3a4342a9600b0258908`, branch `codex/economic-analysis-ready`, worktree `ifdata-credit-gaps`.
- Redescobrir e autenticar `data/curated/current-indicators.json` pelo diretório Git comum. Pin vigente d47; migração explícita da entrada de auditoria para composição192 f374, com27métricas. Registrar hashes completos no recibo; não promover durante a investigação.
- Macro aceita: manifest `9920b6ebe130854130ab9ec7e7bfe98410556f22f81b969128be2704be8de118`. Crédito196: core `b69fbcbe68cc38168403bc60a147dc761c444c507d22021db2e1e573baa255d2` e early `246ec46328821041ae676f601393064c6e1b8eb5324a129ce3552e422862b86d`.
- Núcleo2010–2024, universo observado inteiro; vinculadas/restante/desconhecido separados. Financeiro principal, Prudencial eIndividual próprios. Sem Atividade nos filtros; Sr original e derivado separados. A seleção55/32/24 e suas relações datadas não mudam.
- Valores extremos são sinais para investigação, não exclusões. Não winsorizar, imputar, anualizar por×4 ou confundir mudança de código com continuidade econômica.

## Fatia A — plausibilidade econômica

- [x] Autenticar tabelas consumidas e fixar pin e recursos. Reusar diagnósticos175/176, sem repetir todas as retiradas de unidades.
- [x] Piloto com ROA/ROE, eficiência, composição de estoques e capital: conferir unidade/razão versus percentual, sinais, extremos e denominadores. Revisão independente do instrumento antes da integral.
- [x] Examinar todas as27métricas/janelas, unidades e agregados. Reter min/max por contexto; identidade N/D unitária integral não certificada nesta execução interrompida; triagens têm limiares operacionais explícitos, sem valor normativo ou regra de exclusão.
- [x] Rastrear os casos mais relevantes aos componentes, contas, períodos, definição e fonte: erro demonstrado, efeito econômico/aritmético explicável ou inconclusivo. Qualquer correção exige recorte e regressão causal próprios; esta auditoria não reescreve a base.
- [x] Entregar `docs/engineering/indicator-economic-plausibility-20261019.md`, evidência privada em destino novo `data/curated/indicator-economic-audit-20261019-*` e parecer independente.

## Fatia B — plano de análise e handoff

- [x] Entregar `docs/engineering/analysis-start-20261019.md`: perguntas, indicadores comuns/específicos, calendário por dado/indicador, recortes condicionados à cobertura, lacunas e comparações de composição.
- [x] Distinguir série agregada da distribuição institucional e das mesmas unidades presentes entre datas; códigos comuns não certificam perímetro estável. Preservar dependência temporal/TTM na escolha futura de testes.
- [x] Documentar o comando de descoberta da mesma base, manifests completos, origens, evidência econômica e consultas. Linkar a entrada noREADME e guia local existente. A próxima tarefa não deve selecionar pasta pela data ou depender deste chat.
- [x] Revisão independente antes de liberar a implementação final193. Adoção de tratamentos/fechamento final continua com João/orientador.

## Fatia C — explorador193

**Sujeito/público/trabalho:** desempenho dos negócios financeiros brasileiros, para o autor e orientador da monografia; permitir escolher uma pergunta e enxergar resultado, composição e limites no mesmo contexto.

**Desenho frontend-design:** fundo claro `#F5F8FC`, superfícies brancas, texto azul profundo `#142B45`, destaque petróleo `#176B87`, referência violeta `#5B4FC4`, avisos âmbar `#D29E25`, linhas `#D7E2EE`. Títulos Bahnschrift com fallback sans, corpo Segoe UI, dados Consolas; fontes locais, sem rede. A assinatura é o guia visual das oito famíliasTcb com as cinco dimensões: disponibilidade e condições reais, sem inventar pontuação de qualidade.

```text
Desempenho financeiro no Brasil                 Base e limites
Indicadores | Balanço do sistema | Crédito | Macro | Guia por Tcb
Perspectiva / população / Tcb / período     [Outros recortes]
Pergunta e medida selecionada
Gráfico de evolução                     Valores e cobertura
Tabela / exportar CSV                   Fórmula e interpretação
```

Autocrítica do desenho: uma parede de filtros ou cinco dashboards independentes dificultaria a comparação. Usar navegação por assunto, contexto comum explícito e apenas controles pertinentes; avisos detalhados ficam disponíveis sem ocupar toda a primeira tela. O guia porTcb é a escolha distintiva; o restante mantém leitura simples e pouco movimento.

- [x] Reaproveitar exportador/template e candidato193 sem tratar sua inspeção visual como já aprovada. Implementar/adaptar testes causais de exportação, precisão, coortes, cobertura e novas áreas.
- [x] Agregados contábeis vêm de componentes/estoques conciliados, sem somar conglomerados e membros entre perspectivas. Crédito soma células disjuntas identificadas; nulos e cobertura aparecem, contas de totais e detalhamento não se somam juntas. Não somar clientes como pessoas únicas.
- [ ] Piloto visual funcional e econômico independente; então exportar o arquivo completo em destinoNOVO, com receipt/hashes. Testar filtros, gráficos, tabela, fontes/fórmulas, CSV e guiaTcb, inclusive vazio/negativo e contexto incompatível.
- [ ] Documentar versão entregue, limites e seleção. Atualizar ponteiro somente após aceite previsto na193, preservando backup e pins de outras tarefas. Se a ferramenta impedir a inspeção, registrar o bloqueio; não contornar política do navegador nem alegar teste visual.
- [ ] Checks proporcionais, revisão final do SHA, PR/integração/CI e atualização das mesmasIssues/mapa2.

## Ownership e verificação

Root é único writer. A198 reserva as três notas/plano e linksREADME/guia local; a193 reserva exportador/template, helper adjacente se necessário e testes/nota próprios. Sem novo framework/camada, alteração de credenciais/proteções/Project3, coleta externa ou dados privados noGit. Revisores trabalham somente em leitura e reportam achados ao executor.

Dados aceitos e originais são imutáveis. Verificar caminhos/hashes, precisão, cobertura e conceitos; código recebe testes comportamentais pertinentes e revisão antes da expansão. Documentação recebe links/coerência/escopo. Estado local, revisado, publicado e integrado permanecem separados.

## Checkpoint de19/10/2026

GatesA/B ehelperC1 aprovados por economic_review_198; expansão decontextos/código revisada.17testes pertinentesPASS, exportaçãov1 eestrutura conferidas. Inspeção visual/manual doarquivo concreto pendente: abertura enfileirada, sem render confirmado.193não concluída nem ponteiro promovido. Oschecksainda marcadospendentes são necessáriospara aceite doartefato, mesmo que ocódigo seja integrado.

Decisão técnica: gerar a exportação completa como **candidato reviewável**, pois o piloto visual estava bloqueado e o usuário precisa de um arquivo concreto para validar. Isso não amplia o aceite visual, não libera QA visual por inferência, não promove ponteiro nem conclui193. Os dados/código já haviam passado por revisão própria; a fronteira de aceite permanece explícita.

## Continuação: controles por assunto e organização da base

Pedido de João após o candidato3: disponibilizar os demais recortes emBalanço/Crédito; retirar controles institucionais daMacro; tornar explícitas organização eúltima versão. Reusar6dimensões/cadastro datado da composição, sem Atividade, nova coleta ou recálculo de indicadores. Mesmos paths193/198; Root integra parágrafo emarquitetura compontepara entrada canônica. Fontes f374/macro/crédito preservadas, ponteirod47reauthenticado.

- [ ] Testes RED/GREEN e piloto de3datas para contextos conjuntos(Tcb,SegmentoTb,Tc,Td,Sr,SrAnalitico), comestados observados/desconhecidos/conflitantes ecoortes disjuntas. Revisão independente antesdefull.
- [ ] Expandir contextos emdestino novo; conservar totais porTcb anteriores. UI Tcb/Sr visíveis, outrosrecortes disponíveis. Macro comsérie/período/referência próprios eCSVsomente macro.
- [ ] Entrada canônica commapa fontes→Parquets→projeções→HTML, granularidade, última candidata vsaceita, recibos/comandos. Atualizar ponteiros documentaisREADME/arquitetura/guialocal semnovo catálogo concorrente.
- [ ] Exportar candidato novo, conferir dados/metadados/recibos e revisarSHA, checkspertinentes/CI; nãoinferiraceitevisual dechecksoffline.

CI3checks dohead2ee05f7PASS. Suíte localanterior globalfalha(1177testes,1failure/1error/4skip):encoding de subprocesso epath8.3/longonotestebenchmark. Preservarlog e distinguir conferências ambientais posteriores; não reclassificar o run.

# Indicadores da monografia: execução e limites

[Issue127](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/127), vinculada à [pesquisa111](financial-dimensions-literature-20261014.md), à [amostra125](fixed-financial-sample-2024-20261014.md) e às escolhas humanas na [Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6174707162). [Spec](../superpowers/specs/2026-10-14-ifdata-monograph-analysis-design.md) e [plano](../superpowers/plans/2026-10-14-ifdata-monograph-analysis.md) são os contratos desta implementação.

## Checkpoint de preparação em14/10/2026 — antes da fatia1

Dez medidas e regra temporal foram aprovadas por João. O desenho/plano passaram pela revisão independentev2: lacunas iniciais de dependências temporais, compatibilidade rastreável e aplicabilidade foram corrigidas; também foram conferidos sinais, liberação finita de janelas e deduplicação prudencial. A revisão da composição documental da fatia0 ainda está pendente. **Nenhum motor de cálculo, indicador acadêmico ou output desta Issue está implementado/aceito neste checkpoint.** Publicação e integração da pesquisa111 têm autoridade própria na PR128; este registro não declara CI ou merge dessa PR.

Snapshots da revisão v2: spec SHA256 `9e26e2ff393c23207197e970a404df2af3a53c35c2b6e627bbee0fae91fc6a06`; plano SHA256 `f9af43a98104a80d91f9caeca6b4c6e9ba8bdc383c7570fa28ab6d12ba392307`. A revisão dos três documentos adicionais da fatia0 conserva seu gate próprio até o parecer.

Root é executor/integrador único dos nove paths delimitados na Issue127. A preparação ocorre no worktree gerenciado monograph-docs; o checkout principal fornece somente runtime e inputs locais, sem alterações nos aceitos. A branch de implementação será criada após integração111 e conferência da base. Não há nova coleta financeira, instalação de dependência, servidor ou alteração de segurança/Project3.

## Investigação focal das entradas

Uma investigação somente leitura, recomputada independentemente, autenticou manifesto brutoSHA710e4de74c05c76f13a2f26edad6cb1e7e669d721e1cdd7cd516664db8a6b760 e página200912/TipoInstituicao2SHA865faec27778a4e05a8cbec2680973df6add24e84cb01487d67723f86d05b7a2:174.720linhas, com1.820registros de créditoAtivo/78191 e26nulls. Os20códigos financeiros distintos presentes no mapa201003 têm saldo finito nessa abertura, incluindo zeroB3. Isso demonstra disponibilidade dos bytes, não continuidade automática de perímetro ou controle. A abertura aceita do piloto contém apenasResumo/Rel1; Ativo/Rel2 deverá ser importado offline em destino novo após o gate aplicável.

Na auditoria dos1.236pares unidade/período principais,78213tem72saldos positivos,1.092negativos,71zeros e umnull.78219tem dois positivos. O contrato conserva ajustes/reversões com normalização assinada, semabs. RIF78208+DIF78214 coincide exatamente comRBIF78215 em1.072dos1.235pares numéricos;163têm resíduos absolutos até0,0001. Usar saldo publicado e registrar o diagnóstico; não reparar tokens, impor identidade estrita ou atribuir causa tecnológica sem prova.

O calendário `native-semester-analysis-v2` propõe extensão explícita da cadeia contábil já pesquisada no [piloto88](ifdata-indicator-pilot-20261011.md) aos contextos finitos da DRE selecionados; cada contexto/época exige liberação registrada por revisão de domínio. Q2 continua proxy de escopo publicado; população exclusiva de carteira e reprodução de ajustesREF não foram certificadas. Esses limites acompanham o indicador e não autorizam inventar equivalências.

## Sequência e evidência exigida

1. Revisão do desenho/plano, allowlist e fontes focais antes do código.
2. Motor temporal/exato com TDD e revisão própria.
3. Bindings e cálculos em lote delimitado2010/2019/2024, com conferência contábil e revisão antes da expansão.
4. Cobertura nominal/agregados/distribuição e segmentações, com revisão independente.
5. Sessenta trimestres, sínteses anuais, replay em destino separado, preservação de inputs, revisão finalSHA e entregaPR/CI/integração/CIpósmerge/ancestralidade.

Cada checkpoint registra base/head ou hashes do snapshot, inventário, comandos/saídas, testes não executados, parecer e limitações. O plano não equivale a resultado; testes de software não substituem conferência financeira. Companhias permanecem no universo mesmo quando uma métrica falta ou não se aplica, e desconhecido não se converte emzero.

## Checkpoint da fatia1 e liberação documental de bindings

O motor puro foi aceito localmente no commit `74ce00dcc4f39cb14718163d0197c660134ebc52`, após revisão independente e correção de dois problemas de validação: parser Decimal dependente do contexto externo e consumo de entradas malformadas antes da validação. O recorte final teve25testes aprovados e oráculos independentes para60trimestres efetivos,57janelas de12meses,60médias trimestrais e57anuais. Isso verifica o mecanismo temporal/exato, sem certificar indicadores sobre a base real, bindings ou execução final.

O gate documental seguinte liberou uma lista finita de18componentes/21contextos das fórmulas e três componentes/seiscontextos diagnósticos, com11Grupo null tipados. As seisrubricasDRE novas usam a inferência contábil v2 delimitada; a definiçãoLLpré/pós201903 continua separada. ÍndicesIB/ICP são somente diagnósticos nativos de escala não homologada; variantesRWA permanecem definições próprias de cada data. As regras qualificadas preservam L3com crédito zero, E2-Bcomo proxy de renda selecionada com representatividade econômica não certificada e aplicação desconhecida distinta de falta de cálculo.

A pesquisa111 integrou pela PR128 no merge `06976b8b17b4198bfec39aece5dae4e7c859f017`, com checks dohead e CI pós-merge38614188828 aprovados. A implementação127 segue local: perfil, cálculo e lote delimitado ainda exigem revisão própria; nenhuma PR127 ou aceite final é confirmado neste checkpoint.

## Correções factuais descobertas na preparação de bindings

A conferência das listas exatas de períodos confirmou que as variantes RWA/IB/ICP são disjuntas por referência. Seus intervalos mínimo–máximo se cruzam, mas isso não demonstra duas definições simultâneas na mesma data. A redação anterior da pesquisa111 usava sobreposição; a Issue127 ampliou a allowlist de nove para dez paths para corrigir somente esse trecho e o alcance das categoriasC na nota existente, com revisão focal. Não há mudança de fórmula, valor, cobertura ou amostra.

O cadastro incorporado no mapa125 é da operadora que sustenta o vínculo; a classificação da unidade financeira alvo exige consulta própria por código/data. Nos1.236pares financeiros observados, o cadastro do alvo está presente;1.063linhas companhia/período diferem em algum campo de classificação entre operadora e alvo. Manter campos e proveniência separados, sem completar SegmentoTb nulo do conglomerado com o tipo de uma subsidiária. Assim, as42.514células segmentadas na pesquisaC descrevem categorias da operadora, não uma classificação automática dos balanços dos conglomerados.

A ponte prudencial declarada em cadastro foi reconciliada por código/data, sem divergências entre operadora e alvo financeiro. Os complementos anuais separados apresentam39ocorrências com várias financeiras para uma prudencial: isso reforça a deduplicação pela perspectiva da métrica, sem admitir vínculo societário ou somar os blocos por essa coincidência. Listas finitas de bindings, aplicabilidade e janelas conservam revisão própria antes de instalação do perfil.

## Checkpoint do código e do lote delimitado da fatia 2

A lista finita revisada foi instalada no perfil. A abertura de dezembro de 2009 foi importada offline dos bytes existentes em destino novo, com replay e revisão independente: 47.320 registros de Resumo e Ativo; a exceção de cálculo admite somente AT, PL e crédito das vinte unidades iniciais, em sessenta localizadores. A mudança de atividade cadastral do BANESTES permanece sinalizada; a revisão não certifica controle societário contínuo nem composição constante do conglomerado. A abertura não admite fluxos de 2009.

A revisão do código encontrou dois problemas e exigiu correção antes da expansão: C3/C4 afirmavam aplicabilidade sem contexto Capital5 observado, e a abertura aceitava um cadastro diferente daquele efetivamente conferido. A versão corrigida exige contexto reconhecido (null nativo continua distinto de binding ausente) e ancora a exceção ao manifest de cadastro revisado. A revisão focal independente aprovou as correções e executou os 46 testes pertinentes, com sucesso.

Snapshot corrigido, ainda sem commit desta fatia:

- Módulo: SHA256 `0662ee0edd97831594a56ccc55c7b9c73943ed515ad7b45712b2a442f2a589f1`.
- Perfil: SHA256 `b186ad4c2aba24df3a7fdc3f88dd9813ec73912024a189be9fe2288d7aece34d`.
- Testes: SHA256 `f58530754b1ed9ed17d2afeaf459f9493f384f2580eaf8139e889f5d3fa35d43`.
- CLI: SHA256 `3f6aa4c251859fc411ff978b5e946a4a552293912b76496b1679c4dde8a34bd1`.

O segundo lote delimitado cobre doze referências selecionadas em 2010, na ruptura de 2019 e entre 2022 e 2024. Gerou 11.289 componentes, 3.296 resultados e 288 relações companhia/período. Construção: 97,781 segundos; verificação das representações JSON/CSV/Parquet: 7,782 segundos; pico de memória do processo: 2.412.498.944 bytes; arquivos: 751.729.109 bytes. Manifest SHA256 `dc99a4f5e8d026e2e1b86b2d9aaf7e270942c119d30d8386d3826c77c0624b9d`; configuração SHA256 `06ad9c42f99995abe2b5ac203992d77871bacc0bcdac46d09ea20eacf324ea23`. Pins das entradas e hashes do código foram conferidos antes e depois, sem alteração. A primeira tentativa permanece preservada como diagnóstico, sem aceite retroativo.

**Neste checkpoint, a revisão econômico-contábil do lote está em andamento.** A consistência entre arquivos e os testes aprovados não certificam os valores financeiros. Agregados, cobertura final, replay do pacote completo e execução dos sessenta trimestres ainda não foram entregues. Não há PR da implementação 127 neste checkpoint.

Os 180 registros anuais complementares da amostra 125 conservam sua adoção somente observacional. Os 66 caminhos documentais de controle encontrados não substituem esse estado por adoção quantitativa nem certificam cada fechamento de dezembro. A próxima fatia preservará nomes, motivos e disponibilidade de componentes em bloco separado, sem atribuição quantitativa automática ao emissor, soma aos principais ou admissão de vínculo desconhecido por coincidência prudencial.

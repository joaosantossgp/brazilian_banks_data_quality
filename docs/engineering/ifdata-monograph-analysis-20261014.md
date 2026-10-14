# Indicadores da monografia: execução e limites

[Issue127](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/127), vinculada à [pesquisa111](financial-dimensions-literature-20261014.md), à [amostra125](fixed-financial-sample-2024-20261014.md) e às escolhas humanas na [Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6174707162). [Spec](../superpowers/specs/2026-10-14-ifdata-monograph-analysis-design.md) e [plano](../superpowers/plans/2026-10-14-ifdata-monograph-analysis.md) são os contratos desta implementação.

## Estado em14/10/2026

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

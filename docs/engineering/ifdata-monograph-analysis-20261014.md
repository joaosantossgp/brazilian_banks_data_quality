# Indicadores da monografia: execução e limites

[Issue127](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/127), vinculada à [pesquisa111](financial-dimensions-literature-20261014.md), à [amostra125](fixed-financial-sample-2024-20261014.md) e às escolhas humanas na [Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6174707162). [Spec](../superpowers/specs/2026-10-14-ifdata-monograph-analysis-design.md) e [plano](../superpowers/plans/2026-10-14-ifdata-monograph-analysis.md) são os contratos desta implementação.

## Resultado local verificado — 14/10/2026

As dez métricas adotadas foram implementadas para os sessenta trimestres de 2010–2024, com quinze fechamentos anuais. A amostra mantém as 24 companhias da seleção de 2024; as unidades financeiras distintas variam entre vinte e vinte e uma no histórico. Os agregados usam a mesma interseção de numeradores e denominadores e deduplicam pela perspectiva de cada métrica. Mediana, quartis e IQR descrevem a distribuição; cobertura nominal e ativos conhecidos mostram o alcance de cada resultado. Os complementos anuais permanecem observacionais, sem atribuição quantitativa ao emissor ou soma ao principal.

A auditoria independente confrontou todos os 16.650 resultados com tokens e contextos nativos, usando Fraction próprio, e reconstruiu todos os agregados, distribuições e recortes, sem divergências. O replay completo autenticou 42 arquivos: os 21 payloads das duas execuções são byte a byte iguais; os manifests diferem somente em created_utc. Esse aceite verifica a reprodução dos snapshots e do método operacional aprovado; não equivale a reconciliação externa certificada com o REF ou avaliação da saúde das instituições. Pesquisa 111 e amostra 125 têm entregas próprias já integradas; revisão final, testes globais, PR e integração desta implementação são registrados na Issue 127, que conserva a autoridade de estado remoto.

| Tabela local | Linhas | Uso |
|---|---:|---|
| components | 28.878 | Tokens, bindings, cadastro próprio e proveniência. |
| results | 16.650 | Razões exatas por unidade, métrica e horizonte; estados e flags. |
| company_map | 1.440 | Todas as relações esperadas companhia/trimestre. |
| company_coverage | 21.960 | 20.160 relações principais e 1.800 complementares observacionais. |
| aggregates | 990 | Razão das somas e cobertura nominal por bloco/período/métrica/horizonte. |
| distributions | 990 | Mediana, quartis e IQR por unidades elegíveis distintas. |
| segment_coverage | 20.464 | Recortes pelo cadastro próprio: Tcb, Td, Tc, Sr, Atividade e SegmentoTb. |

Cada tabela tem JSON, CSV e Parquet textual. Null, vazio, zero, binding não liberado e unidade ausente conservam estados distintos. As contagens de cobertura descrevem categorias que podem se sobrepor, como calculável e aplicável; não devem ser somadas como partição do universo. A cobertura conjunta combina seis métricas point com quatro quarter ou quatro TTM, como diagnóstico, sem filtrar a amostra. As referências a componentes/resultados dentro do pacote evitam repetir toda a proveniência em cada linha.

### Leitura do fechamento de 2024

Os valores abaixo são percentuais arredondados apenas para leitura. O pacote conserva frações exatas e display com 100 dígitos. Estoques usam dezembro; fluxos usam doze meses. C3/C4 têm unidade prudencial própria; as demais métricas têm unidade financeira. Companhias e unidades não são contagens intercambiáveis.

| Métrica | Horizonte | Agregado (%) | Companhias elegíveis / 24 | Unidades elegíveis |
|---|---|---:|---:|---:|
| R1 — ROA, lucro líquido/AT médio | TTM | 1,399477 | 24 | 20 |
| R2 — ROE, lucro líquido/PL médio | TTM | 17,334323 | 24 | 20 |
| Q1 — provisão/crédito bruto | point | 6,179197 | 23 | 19 |
| Q2 — custo de provisão/crédito bruto médio | TTM | 4,589430 | 23 | 19 |
| C1 — PL/AT | point | 8,051692 | 24 | 20 |
| C3 — PR/RWA | point | 15,003164 | 24 | 20 |
| C4 — capital principal/RWA | point | 11,713999 | 24 | 20 |
| L2 — liquidez imediata | point | 330,373206 | 21 | 17 |
| L3 — crédito/depósitos | point | 89,950635 | 24 | 20 |
| E2-B — custos/renda selecionada antes da provisão | TTM | 40,145800 | 24 | 20 |

Q1/Q2 não são inadimplência observada. E2-B mede renda selecionada, com representatividade econômica integral não certificada. L2 não é LCR/NSFR. Os índices prudenciais publicados IB/ICP permanecem diagnósticos nativos de escala não homologada, sem igualdade ou conversão presumidas.

Em dezembro de 2024, Q1/Q2 têm crédito bruto zero para B3; L2 tem depósitos à vista zero para Porto, BR Partners e DM. Os estados são zero_denominator/unknown, sem prova de não aplicabilidade. As companhias permanecem no universo. L3 de B3, com numerador zero e depósitos positivos, continua calculável. As demais sete métricas cobrem as 24 companhias e vinte unidades em suas perspectivas próprias. A cobertura conjunta completa reúne vinte companhias, sem substituir a amostra de 24.

No histórico, BR Partners não tem unidade principal nas nove datas 201003–201203; mudanças posteriores de código não recebem dependências de um antecessor por nome. BRB tem null nativo em 202209, propagado pelas janelas que dependem dessa observação. DM tem capital principal null em 27 datas de 201803–202409 e finito em 202412. Janelas TTM que cruzam a quebra de lucro líquido de 201903 ficam incompatible_definition; os três primeiros TTM de 2010 não recebem história inventada. Os arquivos de cobertura conservam nomes e motivos em cada período, inclusive valores matemáticos diagnósticos que não entram no agregado principal por aplicabilidade desconhecida.

### Artefatos, integridade e execução

- Resultado: `data/curated/ifdata-analysis-20261014-run1/`, manifest SHA256 `094f1f7d71107b06e40a832dadef406a14332dd74b17f1775d0c9d6ce1c74197`.
- Replay: `data/curated/ifdata-analysis-20261014-replay/`, manifest SHA256 `872d7e6330b43318c1e06431deb134aa5dad074c452e977e211fa6bda9cae623`.
- Configuração privada: SHA256 `b6d9149480a8b75fb3214ee4f8539e7a09e6e2d766728cdd90a008efb1c04fa5`; seis entradas explicitamente ancoradas. O pacote não executa o reproduce.py da amostra.
- Módulo: SHA256 `6a5233bfba479674bef931ea925aabf4504a1bb30b6ac1a9b66f4adbd67645ca`; perfil: SHA256 `b186ad4c2aba24df3a7fdc3f88dd9813ec73912024a189be9fe2288d7aece34d`.
- Parecer financeiro independente completo e replay: SHA256 `9413b647b4f2739b377b1b2f53fc75c91aca5f409dcfd6d7e73486800fe8899e`. Os relatórios detalhados e os dados ficam nos destinos privados; este registro público conserva resultados e limites verificáveis.

| Medição real do processo | Resultado | Replay |
|---|---:|---:|
| Build (segundos) | 203,109 | 197,844 |
| Verify (segundos) | 67,297 | 80,343 |
| Pico de working set (bytes) | 2.978.394.112 | 4.420.730.880 |
| Arquivos (bytes) | 4.037.238.493 | 4.037.238.493 |

A diferença entre os picos faz parte da medição de cada execução, não de um limite universal. Escrita/verificação incremental evitam cópias integrais adicionais das representações; o build ainda materializa o recorte selecionado e os buffers nativos têm memória própria. Entradas e hashes de código/perfil permaneceram intactos antes/depois. A suíte focal final teve 66 testes aprovados; as verificações globais e a revisão do SHA entregue conservam evidência própria na Issue.

Em um checkout desta entrega com os dados restaurados nos destinos relativos acima:

```powershell
$analysisRoot = 'data/curated/ifdata-analysis-20261014-run1'
$analysisPin = '094f1f7d71107b06e40a832dadef406a14332dd74b17f1775d0c9d6ce1c74197'
python -B scripts/analyze-ifdata.py verify --output $analysisRoot --expected-manifest-sha256 $analysisPin
python -B scripts/analyze-ifdata.py query --output $analysisRoot --expected-manifest-sha256 $analysisPin --sql "SELECT period, metric, horizon, status, payload FROM aggregates WHERE period='202412' AND json_extract_string(payload, '$.block')='principal'"
```

Query aceita uma única instrução SELECT sobre as tabelas autenticadas e materializadas na conexão; leituras externas e instruções de escrita são recusadas. Os checkpoints abaixo preservam a evolução da implementação e não substituem o resultado corrente ou o estado remoto da Issue.

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

## Aceite local da fatia 2

A conferência econômico-contábil independente concluiu o recorte delimitado: todas as 3.296 razões e estados, 11.289 componentes e 288 relações companhia/período foram comparados com as fontes nativas, após autenticação de 453 arquivos. Não houve divergência numérica, de fórmula, sinal, janela final, aplicabilidade ou perspectiva. Também foram conferidos os 2.929 displays calculados com 100 dígitos, 244 diagnósticos exatos de crédito e 368 diagnósticos prudenciais com escala não homologada preservada. Os casos manuais cobrem as dez fórmulas, abertura finita, ruptura LL, zeros, nulos, reversões e denominadores negativos.

A primeira execução do oráculo independente encontrou 297 diferenças de nomenclatura interna ou de precedência da liberação finita: quebra LL usa incompatible_definition; médias fora da abertura permitida usam invalid_interval no subcomponente, enquanto o resultado final é insufficient_history; códigos fora da exceção de abertura usam binding_unverified. O verificador foi corrigido com justificativas explícitas, sem alterar código ou dados para obter aceite; as duas execuções permanecem preservadas.

Parecer econômico SHA256 `9133c7a1ac2fc7646e3a6a3960d57d940aa08f59236338649bf0e933b9d23065`. O commit local `fd4044096af6383a391d583c5cfb31225c420767` contém os quatro arquivos de código/perfil/testes/CLI e o checkpoint documental revisados. A fatia 3 está liberada para implementação; seus agregados e coberturas, execução completa, replay e entrega remota conservam gates próprios. Este aceite não certifica equivalência REF, escala de IB/ICP, representatividade integral da proxy E2-B, controle contínuo ou exclusividade de carteira em Q2.

## Revisão inicial da fatia 3 e ajuste de recurso

O primeiro lote da fatia 3 gerou 4.632 linhas de cobertura (4.032 principais e 600 complementares), 218 agregados, 218 distribuições e 4.762 recortes por categoria. São sessenta observações complementares anuais selecionadas pelas doze datas pedidas, dentre as 180 disponíveis; cada observação produz seis entradas point e quatro TTM somente documentais. O total de componentes passou a 11.799 por incorporar disponibilidade própria dos complementos. Os três arquivos de resultados e os três de mapas principais são byte a byte iguais aos da fatia 2, segundo os hashes autenticados: fórmulas e relações principais permaneceram intactas.

Manifest do lote: SHA256 `b4118013fb6aa61c2a6994dc91d183cec91e43560cee395d145c52c7f9bcd2e2`. Construção: 153,921 segundos; verificação: 8,36 segundos; pico: 2.426.195.968 bytes; arquivos: 825.826.867 bytes. Os 61 testes focais passaram. A revisão independente conferiu todos os agregados, distribuições, recortes e linhas de cobertura, além de 655 componentes de AT e contraprovas próprias de ponderação, quantis, deduplicação e estados.

Um P2 impediu o aceite: o campo de cobertura conjunta de agregados complementares herdava a lista de companhias do principal. A correção deve explicitar o universo do diagnóstico e conservar o complemento não adotado, com lista vazia, sem mudar elegibilidade ou valores financeiros. Parecer inicial SHA256 `8c809cf2b9f28e24bdc4438fc6bccd360e66b06888e3709b857d4b3daa15563c`; o lote permanece preservado e seu replay foi adiado para a versão corrigida.

A medição também justificou adaptar a escrita e a verificação para linhas/lotes. A máquina dispõe de 32 GiB físicos, mas a disponibilidade observada era aproximadamente 2,3 GiB, com cerca de 61 GB de memória comprometida de um limite de 70,8 GB. A extrapolação do pico para sessenta datas não constitui benchmark, mas indica risco de esgotar o recurso disponível. A adaptação fica nos mesmos módulos e mantém todos os checks, precisão e leitura stage2; não modifica outros processos, o sistema ou dependências. Novo lote, medição, revisão focal e replay deverão demonstrar seu efeito antes da execução completa.

## Correção da fatia 3, medição e replay delimitado

A correção separou o universo da cobertura conjunta por bloco: o principal tem diagnóstico global nominal explícito; o complemento não adotado tem lista vazia e estado próprio. Os demais cálculos permanecem intactos. O writer passou a gravar JSON/CSV por registro e a gerar Parquet pelo CSV canônico com colunas textuais e leitura sequencial. O verify percorre o array JSON e o Parquet incrementalmente e reconstrói o hash do CSV, mantendo contagens, esquema, IDs/chaves únicos, null/vazio e rejeição de conteúdo inválido ou excedente. Os bytes JSON legados no Windows foram preservados por regressão causal de CRLF. A suíte focal final contém 66 testes, aprovados em 17,642 segundos.

O novo lote delimitado mantém todas as contagens anteriores. Manifest SHA256 `3c1f1377717bd8b27ea9f9e9888e2a6e77b096e5dd839f70378f16f0c844d82b`: build 29,109 segundos, verify 12,156 segundos e pico de memória do processo 1.194.446.848 bytes. O replay independente em destino novo tem manifest SHA256 `c8928027b33ee5d6f1f653430749ce72c38a28332d44b52489cb90fa9d8a1abe`: build 28,688 segundos, verify 13,156 segundos e pico 1.197.379.584 bytes. Ambos têm 825.846.501 bytes de arquivos. A comparação autenticou os 42 arquivos das duas saídas: os 21 payloads são byte a byte iguais, e os manifests diferem somente no UTC de execução.

Essas são medições do processo no recorte real, distintas do teste sintético com tracemalloc. Na fixture fixa de 16 MiB, a adaptação também reduziu as alocações Python de escrita de aproximadamente 69,7 MB para 9,0 MB e de verificação de 145,0 MB para 7,6 MB; isso não mede memória nativa DuckDB nem estabelece teto universal. O lote completo ainda exige medição própria. Neste checkpoint, a revisão focal da correção e dos mecanismos de I/O está em andamento; execução dos sessenta trimestres e entrega remota continuam pendentes.

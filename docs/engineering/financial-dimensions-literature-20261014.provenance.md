# Proveniência da pesquisa das cinco dimensões — 14/10/2026

Companion da [síntese e fichas](financial-dimensions-literature-20261014.md), [Issue111](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/111). Abaixo distinguem-se leitura, atribuição original, inferência do projeto e adaptação proposta. Não há publicação de PDFs, imagens do livro, manuscrito, cookies, headers ou dados financeiros nesta entrega. Originais, respostas, extrações, falhas e pareceres ficam na preparação privada preservada; hashes permitem identificar versões, sem garantir disponibilidade pública futura.

## Método e alcance da busca

Busca dirigida a partir das cinco dimensões e do inventário113, seguindo referências e confrontando definições bancárias. Assaf foi lido visualmente; pesquisador bancário examinou guias/normas originais, outro pesquisador examinou estudos originais; verificação independente releu os trechos antes da síntese. Não houve protocolo de revisão sistemática, contagem exaustiva de resultados, avaliação de todo o universo de artigos ou estimativa de efeito causal. Os três estudos são complementos e contraprovas de validade; não representam todas as atividades do universo CVM/B3.

As skills research/pdf-explore orientaram delegação e leitura. O slash `/deepresearch` não está validado nesta interface; a profundidade foi executada por pesquisa, verificação e revisão com ferramentas locais/fontes primárias, conforme contrato111. Não se instalou runtime nem se declarou execução do comando indisponível. Downloads foram exclusivamente bibliográficos; não houve coleta IF.data nova.

## Fonte central: Assaf Neto

ASSAF NETO, Alexandre. *Estrutura e análise de balanços: um enfoque econômico-financeiro*. 11.ed. São Paulo: Atlas, 2015. Folha de rosto e dados editoriais: PDF4–5. Exemplar privado recebido de João; SHA-256 `d41dccd16d2a9c174fb95cd87e5d3abd0666f461514d8402594367cc913d367b`, 148.717.116 bytes, 389 páginas. Scan sem camada textual; inspeção das imagens de página extraídas com pypdf/PIL, sem OCR. Extração de uma página não significa leitura. Não se afirma leitura integral.

| Conteúdo efetivamente lido | Impresso / PDF (1-based) | Uso na síntese |
|---|---|---|
| Cap3, critérios/comparações (trecho) | pp.46–56 / PDF67–77 | Qualidade informacional, contexto, comparação temporal/entre atividades e inflação; listagem jurídica antiga não usada como orientação vigente |
| Seção14.10, padrões de análise | pp.275–279 / PDF296–300 | Mediana, decis/quartis e limites de avaliação isolada; uso até conclusão da seção, sem adotar modelos de insolvência14.11 |
| Cap17, estrutura de balanço e DRE bancários | pp.321–331 / PDF342–352 | Componentes, crédito/provisão, receitas/custos, regime de competência e contexto histórico de capital |
| Cap18, desempenho de bancos | pp.332–352 / PDF353–373 | Liquidez, funding, capitalização, retorno, custos, GAP e exemplo didático |
| Localizadores adicionais | Sumário e dados editoriais selecionados | Organização/bibliografia; não fundamentam fórmula |

48 páginas substantivas foram lidas e verificadas independentemente:32 bancárias e16 adicionais de critérios/comparação. Principais atribuições diretas: encaixe e liquidez imediata p334; crédito/depósitos e crédito/AT p335; PL/AT e AT/PL p337; retorno e margens pp341–342; despesas operacionais/RIF p342. Médias e ajustes dePL de p339 pertencem ao contexto de taxa de reinvestimento; não são regra universal atribuída a todos os ROEs. PL médio e carteira média nas fichas são propostas explícitas. Somente seção14.10 do cap14 foi usada no suplemento estatístico; não se leu o capítulo14 integral ou seção14.5/VEA. Cap16 e pp353–354 do cap18 não foram usados para claims novos.

**Contraprovas preservadas no exemplar:** p349 apresenta capital de giro em formato/unidade incompatível com a fórmula monetária PL−ANC de p335 e os saldos de p345; o quadro usa leverage com sinal de percentual e p351 repete percentual no diagrama, embora AT/PL seja vezes; a expressão alternativa de VEA em p352 inverte a ordem do retorno e custo em relação à primeira expressão. Essas divergências do exemplo não autorizam corrigir silenciosamente a fonte nem implementá-las. A síntese usa conceitos/fórmulas definidas, sem importar esses resultados didáticos; VEA não integra a shortlist. Depósito à vista de p345 foi relido em imagem ampliada:1.212,0.

### Suplemento Assaf: critérios, comparação e posições relativas

Leitura visual adicional e independente das16 páginas descritas na tabela, semOCR. Claims T01–T08: qualidade das informações e ausência de diagnóstico universal(p47); contexto de atividade/relatórios(p50); análise horizontal/vertical e comparações(pp53–55); inflação/valores históricos(pp55–56); padrões setoriais e mediana(pp275–276); decis/quartis e ressalva à classificação isolada(pp276–279). Os valores de exemplos de empresas de alimentos/papel não foram usados como benchmarks para bancos nem critério topN.

A síntese distingue mediana de agregadoΣN/ΣD; IQR, exemploA/B e cautela causal são elaborações próprias. Não se adotaram rótulos de qualidade por quartil, algoritmos de interpolação, deflator ou obrigações atuais de DFP/ITR/IAN descritas no trecho antigo. Na p277, “nove/três partes” é impreciso: nove/três são pontos de corte, não quantidade de grupos; as fronteiras percentuais e exemplos seguintes foram lidos e essa inconsistência não foi copiada como definição.

Evidência privada `assaf/comparison-statistics-supplement.md`, SHA `f5e81a814103f3b1daf1c8f6c9c94e501294bc10bd46268d05319201f9dd2252`. Parecer independente `review/assaf_comparison_verification.md`, SHA `88c387190a6d5df91dab8b767e07010193f2f32fb4488e433dbdf577c9ec6017`:PASSclaims/limites;16recibos de imagem e16reextrações byte a byte conferidos contra o PDF autenticado. A contagem48 não inclui sumário/dados editoriais nem presume leitura integral dos capítulos. Gate de fonte antes da incorporação; método permanece proposta.

## Guias e normas: versões e localizadores

| Fonte primária efetivamente examinada | Localizador lido / papel / limite |
|---|---|
| FMI. *Financial Soundness Indicators Compilation Guide*, **Prepublication Draft 2019**. [PDF distribuído pelo CEMLA](https://www.cemla.org/actividades/2019-final/2019-07-indicadores/2019-07-indicadores-1.pdf), no [curso coorganizado com FMI](https://www.cemla.org/actividades/2019/2019-07-indicators.html). | 208 páginas; impresso→PDF+14. Lidas pp58–59,67,70–71,73,84–93,113–114,125,156–157,160. §§7.5/6.3–6.6:agregação;6.22–6.30:perímetros;7.46–7.55:ROA/ROE;7.56–7.63:receitas/custos;7.29/7.34–7.42:NPL;12:distribuição. **Não atribuir estes localizadores à edição final**, cujo acesso retornou403/429. §7.48 especifica média de AT; §7.52 não especifica literalmente média de PL. |
| BCB. [IF.data: Esclarecimentos e Metodologia](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf), sem data editorial demonstrada. | 2 páginas, leitura integral; notas1–3 e disponibilidade. Números das notas não são códigosTipoInstituicao daAPI; descrição corrente não certifica todos os vínculos históricos. |
| CMN. [Resolução3.490/2007, original](https://www.bcb.gov.br/pre/normativos/res/2007/pdf/res_3490_v1_O.pdf). | p1,arts1–2:PRE e componentes de risco. Não é norma compilada para cada trimestre. |
| BCB. [Circular3.360/2007, original](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/48039/Circ_3360_v1_O.pdf). | pp1–2,art1/§§1–5:PEPR=F×EPR e fator/exceções originais. Não prova sozinha toda a vigência2010–13. |
| CMN. [Resolução4.193/2013, original](https://www.bcb.gov.br/pre/normativos/res/2013/pdf/res_4193_v1_O.pdf). | pp1–4 e7,arts3–8/18; RWA, cronograma, adicionais, exceções e vigência. Alterações posteriores não foram todas reconstruídas. |
| CMN. [Resolução2.682/1999, compilação v2P](https://www.bcb.gov.br/pre/normativos/res/1999/pdf/res_2682_v2_P.pdf). | pp1–5/início6;arts1–9,11/14. Inclui mudanças expressas2.697/2000. Provisões, atraso, baixa, renegociação; art9:atraso **igual ou superior a60 dias**. Art4 tem critérios adicionais e exceção de prazo, portanto E–H não equivale aNPL90. |
| CMN. [Resolução4.401,27/02/2015, original](https://www.bcb.gov.br/pre/normativos/res/2015/pdf/res_4401_v1_O.pdf). | pp1–2,arts1–7:escopo/LCR/cronograma original. Não universalizar a toda atividade/período. |
| CMN. [Resolução4.616/2017, original](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50474/Res_4616_v1_O.pdf). | 2 páginas, leitura integral; NSFR e aplicaçãoS1 desde01/10/2018; altera escopoLCR. |
| BCBS. [Basel III: The Liquidity Coverage Ratio and liquidity risk monitoring tools](https://www.bis.org/publications/201301-standards-basel-iii-liquidity-coverage-ratio-and-liquidity-risk-monitoring-tools.pdf),jan2013. | Impressas5–6/PDF11–12,§§17/19–22. Horizonte30 diascalendários, estresse e usoHQLA. Não se afirma leitura de todas75 páginas. |
| BCBS. [Basel III: the net stable funding ratio](https://www.bis.org/publications/201410-standards-basel-iii-net-stable-funding-ratio.pdf),out2014. | Impressas1–3/PDF5–7,§§1–17. ASF/RSF, horizonte anual, ponderações; não reconstruído com contas genéricas. |
| BCB. [REF,abril2025](https://www.bcb.gov.br/content/publicacoes/ref/202504/RELESTAB202504-refPub.pdf). | Impressas/PDF100–104:fundingLTD,capital,IL/ILE. Contexto2024, não todo o histórico. IL30 diasúteis difere deLCR30 diascalendários. Fonte reutilizada autenticada, leitura substantiva nesta pesquisa. |

## Estudos originais: evidência e limites de transferência

| Referência | Método efetivamente conferido / uso |
|---|---|
| TECLES, Patricia; TABAK, Benjamin M. *Determinants of Bank Efficiency: The Case of Brazil*. BCB,Working Paper210,2010. [Original](https://www.bcb.gov.br/content/publicacoes/WorkingPaperSeries/wps210.pdf). Série maio2010, data interna8jul2010. | Métodos impressas11–14/PDF12–15; resultados15–19/PDF16–20; conclusão20/PDF21. 156 bancos/1.517 observações semestrais2000–2007; fronteira estocástica bayesiana, heterogeneidade de porte e produtos. Depósitos como produto alteram resultados. Não equiparar cost-income a SFA/DEA, copiar benchmarks, transformações de prejuízo ou supor identidade com publicação posterior. |
| LIMA, Fabiano Guasti; FONSECA, Camila Veneo Camargo; SILVEIRA, Rodrigo Lanna Franco da; ASSAF NETO, Alexandre. Os determinantes dos ratings de crédito dos bancos brasileiros. *RAC*,22(2),178–200,2018. [DOI](https://doi.org/10.1590/1982-7849rac2018160373); [PDF original](https://www.scielo.br/j/rac/a/ZPMKdbB7pSn3hBB7Rs8XkYL/?format=pdf&lang=pt). | Métodos pp187–192/PDF10–15, tabela4p190/PDF13; resultados194–196/PDF17–19. 12 bancos comrating,2006–2015;364 observações iniciais/348 estimações,359 previsões em outra base a conciliar. Não copiar acurácia, coeficientes/pesos, descarte±4desvios ou sinais; proxyPDD/crédito não é atraso observado. |
| SOUZA, Juliana Ribeiro; OLIVEIRA, Joice Garcia de; BARBOSA NETO, João Estevão; PINHEIRO, Juliano Lima. Eficiência e rentabilidade das agências financeiras de fomento. *RAP*,55(4),969–994,2021. [DOI](https://doi.org/10.1590/0034-761220200111); [PDF original](https://www.scielo.br/j/rap/a/6jxpJsqNWrGD6wwtBVMQHfd/?format=pdf&lang=pt). | Métodos pp978–981/PDF10–13; quadro2p979/PDF11 conferido visualmente (extração textual defeituosa); resultados988–990/PDF20–22. 14 agências/88 observações anuais2012–18. IEO eIE diferentes; PECLD exige conciliação. Índices-padrão usam médias no período(p981), não cortes universais. Contexto público/fomento não é amostra deste projeto. |

A síntese identifica interpretações próprias: custo/receita não mede produtividade física; estoque/fluxo/sinal precisam contrato; pesos naturais da razão das somas dependem do denominador. Estudos fornecem contraprovas e alternativas, não adoção de modelos, testes ou rankings. Referências citadas dentro dos artigos, sem leitura própria, não foram promovidas a fonte original desta entrega.

## Suplemento focal E2/Q2: BCB2016 e2024

Pesquisa adicional delimitada às definições de eficiência, seguida de verificação independente textual/visual dos gráficos. [REF setembro2016](https://www.bcb.gov.br/content/publicacoes/ref/201609/RELESTAB201609-refSFi.pdf): impressas40–41/PDF18–19, nota44 e gráficos2.4.6/2.4.7. [REF abril2024](https://www.bcb.gov.br/content/publicacoes/ref/202404/RELESTAB202404-refPub.pdf): pp33–34, nota52 e gráfico1.2.3.5. [REF **novembro2024**](https://www.bcb.gov.br/content/publicacoes/ref/202410/RELESTAB202410-refPub.pdf), vol23,n2, data da capa apesar da pasta202410: pp37–38, nota56 e gráficos1.2.3.8/1.2.3.9. Fontes/gráficos usam12 meses; outras janelas exigem adaptação explícita.

Claims conferidos: administrativasREF incluem pessoal;78225já incorpora custos/provisão e não é denominador homologado por nome; proxy E2-A conserva RIF mas estreita custos do IEOAssaf; E2-B retira provisão assinada doRBIF e soma serviços/tarifas sob sinal/janela/abrangência comprovados; E2-C mantém de-paraBCB aberto. Todas são propostas próprias, não equivalência aprovada comFMI/BCB. Metadados contêm typos preservados: não avaliar expressões COSIF para fabricar uma ponte.

Q2 também tem fundamento externo direto: REF novembro2024, p37, gráfico1.2.3.6/nota1, despesas com provisões/saldo médio da carteira, acumulado12 meses. Não certifica conta78213, convenção de sinal, frequência da média ou ajustes de nossa amostra.

Evidência privada `banking/efficiency-supplement-20261014/efficiency-evidence.md`, SHA `3c0e3383edba6cfe6c4a121bd8fee72a992dd820d52bc3280609aed5f8021666`; provenanceSHA `5b9e5d5eccbdc5c9f6ef96b8cf9407368261f28c7de2f344658ee367820c2df2`; handoffSHA `d8fd31b7d55f4ae7e59b0dd833af81184f93beab3cfcaa61898de05789c8a8a1`. Parecer independente `review/efficiency_verification.md`, SHA `2f0c0244a48bb95852782317aeb27032a9305cbb31ad2b68749f6c45df531cb3`:PASSfontes/inferências delimitadas;359 originais e14 itens suplementares conferidos. Este gate de fontes precede a incorporação, sem aprovar método ou cobertura.

## CoberturaC: fontes, artefatos e revisão independente

A125forneceu pacote local com aceite delimitado `reviewed finite sample and historical native mapping with explicit documentary unknowns; no exhaustive B3 certification or continuous historical control claim`. ManifestSHA `bf54640a70964ca8468cdefc1fc2aaf53d1aab8985779005de21fc9b847467eb`;221 arquivos e207 pins autenticados. Root leu limites e pareceres de história/perímetros antes do usoC. Seu aceite local permitiu auditoria antes da integraçãoGit, depois confirmada no PR126/merge531df618. Nenhum arquivo125 foi alterado por111.

Datasets financeiros/capital foram abertos pelo leitor autenticado `bank_quality.ifdata_odata.open_dataset`, conservando saldos textuais, campos nativos e proveniência. Manifests `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095` (financeiro) e `01c4e2d086cc8c2ad015b18f36c5886c07ef3e4ec31434d594231bd87ffaac32` (capital). Catálogo438equatrooutputs autenticados; mapas company-quarter/anuais e complementos do125 fixados porpins. Ponte prudencial deriva do cadastro da mesma referência, sem inferência por nome ou transporte de código2024.

Artefatos privados novos em `.scratch/literature-five-dimensions-20261014/coverage-c/`: script audit_c_v5.py, run5/receipt.json/sql.json, matrizes de componentes/candidatos, conjuntos declarados, lags, resumos/nominais, suplementoCSV–Parquet, inventário e replay1. Somentev5/run5é execução completa aceita;run1–4parciais/falhas preservadas não são evidência global. B-input-pins fixa a propostaBv3 usada na auditoria; o deltaBv4não alterou os25IDs/componentes. Sinais/janelas/métodos continuam não adotados.

| Evidência privada | SHA-256 / alcance |
|---|---|
| coverage-c/findings.md | `45acca391a1ca4f00e3c957bdd7f65dc6e0a48ea57b9eeafe6fe049b968d773e`; resultado do analista |
| coverage-c/run5/receipt.json | `14890fa9e8b4a2538e655c5dde63ef5573fe6430aa1bfc91a401ba0053effb6a`; execução e pins |
| review/c_review.md | `842a61fc63ce913e864e205db3d922766886bf3d7f5d5315c9b3138b079368a9`;PASS delimitadoC |
| review/c_review_inventory.json | `1aa4e471706cda27b026b51e70c5da8b76810b78cf7efdf7c54f28dd767f72fb`; inventário da revisão |

O revisor recomputou independentemente, sem executar o script autor,38 componentes/61.560 células,25 fichas+4diagnósticos/46.980linhas, lags/resumos/ativos e42.514 células segmentadas. Conferiu221 arquivos125/207 pins,89 arquivos do handoff,60cadastros nativos e preservação antes/depois. Replay10/12byteigual e12/12multiconjunto semântico; não alegar byteigualdade de todos12.

Limite material registrado:66 observações complementares com componentes e66comcontrole documental têm interseção14, não equivalência. Evidência nominal `review/c_complementary_sets.json`. Não excluirunknowns, somar blocos ou certificar controle trimestral por documento anual. Presença finita não comprova aplicabilidade, denominator econômico, média/TTM, escala prudencial, sinalnormalizado ou fórmula adotada. Esta auditoria ainda depende dos pacotes locais ignorados; não torna o clone isolado um pipeline analítico final. Implementação reproduzível de produto será entrega posterior, sob contrato próprio.

## Falhas de acesso e lacunas preservadas

Edição final FMI2019:403/429 em URLs FMI/elibrary; usada somente versão draft identificada. Original4.958 na URL antiga:404; não houve atribuição de seus artigos. IMF19/5(Xu/Hu/Das) e Mohanram/SSRN3072574 não tiveram corpo obtido nesta busca; não receberam fórmulas/resultados atribuídos. Falha de acesso é lacuna desta busca, não ausência de literatura. Não se ampliou automaticamente coleta ou universo para sanar essas lacunas.

## Evidência reaproveitada do piloto88

[Nota do piloto](ifdata-indicator-pilot-20261011.md), complementoA e implementação/checkpoints: unidade monetária R$ no HTML oficial da aplicaçãoOlinda; inferência contábil `native-semester-v1` aceita para o ensaio emLL78187,RAT78226,RIF78208, nos respectivos contextos financeiro2/individual3. Março/setembro têm3 meses, junho/dezembro6 meses. Não é regra universal de toda DRE nem aceitação de método acadêmico final. A escala de índices nativos continua não confirmada; novas rubricas precisam conciliação. Diferenças trimestrais/TTM não foram aprovadas pelo simples aceite da janela nativa. A entrada auxiliar200912 existe no piloto; identidade/perímetro com a amostra125 não foi revalidada nesta pesquisa.

Esta é **evidência reaproveitada**, conferida na nota e no código `bank_quality/ifdata_indicators.py` (evaluate_unit e _flow_verified), sem alegar novoGET/releitura integral das normas daquela entrega. A cadeia de fontes primárias, localizadores e alcance está na nota citada, preservada emmain. Não confundir o estado histórico “janela não comprovada” no início da nota com o complemento e aceite posteriores.

## Gates de fontes e rastreabilidade privada

Preparação privada na pasta existente `.scratch/literature-five-dimensions-20261014/` do checkout primário; não é tracker concorrente nem destino de publicação. Reviewers conferiram corpos e páginas, não apenas resumos dos autores. As revisões de fontes não certificam esta sínteseB, bindings de produção, amostra125 ou método adotado.

| Evidência / parecer | SHA-256 da versão verificada | Alcance |
|---|---|---|
| assaf/research_evidence.md | 11d3e60babdfb3484cc584b77f6fff17bbfc8c0927371af5cf224155d6311c45 | A01–A17/V01–V04 |
| review/assaf_verification.md | 77487dae9d9e01ad739408f221aea9de53ac02cafe7dad3e51b51aacc92f2fb0 | PASS21 páginas |
| assaf/supplement17.md | a5060324c43bf8a344aa052c2fe7385db31f07da9d42020902b0f1d4e6d7ce4f | S01–S07 |
| review/assaf_supplement_verification.md | 4696e35eda2b78eb82a026d5d2d5a2e189dcc68609d736bfe4152e0b460ac0c6 | PASS11 páginas |
| studies/research_evidence.md | 2bbcad2f73d00cd0d0c6d6f4695268012e380f28248697441f96aeecd1656866 | T/L/S |
| review/studies_verification.md | 541b364657f156b70e2b8abca371a1f4a94c2414be0d1927a1c6c21e6b7da64d | PASSoriginais/fontes |
| banking/research_evidence-v2.md | 9455334acd66e5136784c469821eee5a160394f2abcebf3c8952a790a3747769 | B01–B18 |
| review/banking_verification.md | 503d73b4df99d990e9a5f4dff02548f755d8a17963df22608e1a664a07a36f97 | PASSnúcleo com precisões |
| review/banking_delta_verification.md | b3a0b9d508b0cb5c6271fe7ca54915df0bb8c0775f85a7910d989df2e1a9a67c | PASSv2 e356 originais preservados |

Pareceres de fontes concluídos antes da expansão paraB; a síntese recebeu revisão própria, e coberturaC usa handoff125aceito com revisão independente delimitada. Após a pesquisa, João adotou em14/10o conjunto inicial e a média ponderada pelo tempo; [decisão registrada](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6174707162). As demais propostas e gates técnicos conservam seu estado. Composição final/SHA/publicação têm autoridade naIssue111; nenhum indicador acadêmico ou software novo foi certificado por esta pesquisa.

## Recibos dos corpos

UTC abaixo é o instante da recuperação registrado no recibo, não data de publicação. Fontes reutilizadas têm hash conferido; sem novoGET nem novo horário inventado. Headers completos permanecem privados.

| ID / fonte | Recuperação UTC / estado | Bytes | SHA-256 |
|---|---|---|---|
| [BCB2682](https://www.bcb.gov.br/pre/normativos/res/1999/pdf/res_2682_v2_P.pdf) | 2026-10-14T16:32:59.376049+00:00 / 200 | 40741 | `4bb9565e24cc466c9feeb25f92ecb71426cbcaf0d0ea3e2eb1e7cbc6a00946ee` |
| [BCB4193](https://www.bcb.gov.br/pre/normativos/res/2013/pdf/res_4193_v1_O.pdf) | 2026-10-14T16:33:00.328728+00:00 / 200 | 116954 | `d7354264fe71fda2a7367d8e41523d5148fa4042e049290e026aea8bd72afdf7` |
| [BCB4401](https://www.bcb.gov.br/pre/normativos/res/2015/pdf/res_4401_v1_O.pdf) | 2026-10-14T16:33:01.128311+00:00 / 200 | 24792 | `d8a7100649d260b31671ef456e0b041506f58cd382a557b7bef6bf0b93e56b36` |
| [BISLCR2013](https://www.bis.org/publications/201301-standards-basel-iii-liquidity-coverage-ratio-and-liquidity-risk-monitoring-tools.pdf) | 2026-10-14T16:33:02.674199+00:00 / 200 | 441806 | `cb2d45abd8a04243c750d6eea841129897ad1a2f72296574ea18a394719f9c33` |
| [BISNSFR2014](https://www.bis.org/publications/201410-standards-basel-iii-net-stable-funding-ratio.pdf) | 2026-10-14T16:33:06.069882+00:00 / 200 | 413992 | `b0b4108cf49fdafb11381b56361770c6a8d037523757eba2c15956b7aab00666` |
| [BCB3490](https://www.bcb.gov.br/pre/normativos/res/2007/pdf/res_3490_v1_O.pdf) | 2026-10-14T16:33:08.300768+00:00 / 200 | 27207 | `648015bc8183588be330335f2eaba5b8a169bf1e7859e507d7cce5c1fb75c54a` |
| [IMF2019DRAFT](https://www.cemla.org/actividades/2019-final/2019-07-indicadores/2019-07-indicadores-1.pdf) | 2026-10-14T16:34:01.397750+00:00 / 200 | 7213286 | `9b68bf4b19e0f4546ff54f9e0b5fb0fa0546201c4f839265cb68d805edd67553` |
| [BCB4616](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50474/Res_4616_v1_O.pdf) | 2026-10-14T16:34:13.195699+00:00 / 200 | 139643 | `0189768e3a3b58bac743528445ccef13247465509522f0a4d8ec9a482c2df02d` |
| [IFDATAMETHOD](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf) | Reutilizada; recibo original privado / reused authenticated local source, no new GET | 72209 | `c83577a710a57d147c8f10d043db111a63d31cf8cd8a7a9b58a08f8733d70896` |
| [REF202504](https://www.bcb.gov.br/content/publicacoes/ref/202504/RELESTAB202504-refPub.pdf) | Reutilizada; recibo original privado / reused authenticated local source, no new GET | 9134103 | `a4e8b6488ea2d484ea4a98e2f620e2df66ec70e26c47f1000df01e28217077ec` |
| [BCB3360](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/48039/Circ_3360_v1_O.pdf) | 2026-10-14T16:41:38.792268+00:00 / 200 | 68527 | `92207b1529a32f649030c64c073bd0d125464910217410bca7b2f7c1fb0c51e5` |
| [T](https://www.bcb.gov.br/content/publicacoes/WorkingPaperSeries/wps210.pdf) | 2026-10-14T16:32:17.108881+00:00 / 200 | 420557 | `dd16e41df6adf44e2ba2cee9d2741b68ae07fcaf0d804c1cb3c9130d743dfefe` |
| [L](https://www.scielo.br/j/rac/a/ZPMKdbB7pSn3hBB7Rs8XkYL/?format=pdf&lang=pt) | 2026-10-14T16:32:19.039659+00:00 / 200 | 530865 | `b385833756878691c722d92705bdc2a0fab589dd9c2ccf9897cec4cab3b7f5bb` |
| [S](https://www.scielo.br/j/rap/a/6jxpJsqNWrGD6wwtBVMQHfd/?format=pdf&lang=pt) | 2026-10-14T16:32:20.279731+00:00 / 200 | 536399 | `568c0de6d63314026eede59ced80948ff9bbef89fe4ee265d39287e34b06ff29` |

### Recibos adicionais do suplemento

| ID / fonte | Recuperação UTC / estado | Bytes | SHA-256 |
|---|---|---|---|
| [REF202410](https://www.bcb.gov.br/content/publicacoes/ref/202410/RELESTAB202410-refPub.pdf) | 2026-10-14T17:08:42.210181+00:00 / 200 | 6710631 | `803691d50c0275ccd065df53d3fc7ef48c5ee5a80911b14768ddcdd8468df7e1` |
| [REF201609](https://www.bcb.gov.br/content/publicacoes/ref/201609/RELESTAB201609-refSFi.pdf) | 2026-10-14T17:08:48.331581+00:00 / 200 | 542881 | `8c482786b6eeb3394d93e7fb3ca06175face0512a243bf3c0ff7da179a42f871` |
| [REF202404](https://www.bcb.gov.br/content/publicacoes/ref/202404/RELESTAB202404-refPub.pdf) | 2026-10-14T17:08:49.880710+00:00 / 200 | 7260789 | `26dc0a73e4ed65efb35e4b31b8eedf5d11c46a6faee4bba3cfe236b50256ff33` |

## Contextos nativos confrontados

Extrato do **Parquet do catálogo autenticado**, restrito a variantes com referências2010–2024. Preserva NomeColuna, definição literal eGrupo; intervalos resumidos não substituem a lista explícita de períodos no catálogo. Valores e cobertura da amostra precisam do contrato posterior; R$ monetário e janela dos três contextos fundamentados são evidência reaproveitada88, sem ampliar a novas rubricas ou confirmar escala de índices. Sinal e contexto econômico continuam próprios. CódigoCOSIF dentro da descrição não éConta do catálogo. As descrições são metadados da fonte, inclusive eventuais grafias incomuns, não fórmulas corrigidas pelo projeto.

CatálogoCSV SHA-256 `9d3d5c8ff537c737465f81178ee369e2656f87629a6b8ba9705ec64b8f28c97a`; manifesto e demais três outputs conferidos na preparaçãoA.

ParquetSHA `644265316851705e0f9187a59ecc5aeb4d6125d5e137c7fa3a34e263563dd30e`. A reconciliaçãoCSV/Parquet identificou154contextos comGrupo `null` noParquet e campo vazioCSV; nenhumGrupo stringvazia noParquet. Por isso o apêndice usa o valor tipado doParquet: `null` é nulo, `""` seria stringvazia. A lista de períodos conserva strings nativas; resumo de intervalos não certifica continuidade econômica. O rótulo anterior “(vazio)” derivado doCSV não é usado como binding. Nenhuma fonte aceita foi alterada.

| dataset/tipo/relatório/Conta | Grupo literal/tipado | NomeColuna literal (quebra escapada) | Descrição literal | Referências no núcleo |
|---|---|---|---|---|
| capital/1/5/79645 | Patrimônio de Referência para Comparação com o RWA - Patrimônio de Referência Nível I para Comparação com RWA | Capital Principal para Comparação com RWA \n(a) | Parcela do capital de melhor qualidade e imediatamente disponível para absorver perdas | 40: 201503–202412 |
| capital/1/5/79649 | Patrimônio de Referência para Comparação com o RWA | Patrimônio de Referência para Comparação com o RWA | Montante de capital regulatório formado pela soma das parcelas de Capital Nível I e Capital Nível II | 39: 201503–202409 |
| capital/1/5/79649 | Patrimônio de Referência para Comparação com o RWA | Patrimônio de Referência para Comparação com o RWA \n(e) | Montante de capital regulatório formado pela soma das parcelas de Capital Nível I e Capital Nível II | 1: 202412–202412 |
| capital/1/5/79659 | `null` | Índice de Capital Principal \n(k) = (a) / (i) | Relação entre Capital Principal e Ativos ponderados pelo risco | 31: 201503–202209 |
| capital/1/5/79659 | `null` | Índice de Capital Principal \n(l) = (a) / (j) | Relação entre Capital Principal e Ativos ponderados pelo risco | 7: 202212–202412 |
| capital/1/5/79659 | `null` | Índice de Capital Principal (k) = (a) / (i) | Relação entre Capital Principal e Ativos ponderados pelo risco | 2: 202303–202306 |
| capital/1/5/79664 | `null` | Índice de Basileia \n(m) = (e) / (i) | Relação entre o Patrimônio de Referência e os Ativos ponderados pelo risco | 33: 201503–202306 |
| capital/1/5/79664 | `null` | Índice de Basileia \n(n) = (e) / (j) | Relação entre o Patrimônio de Referência e os Ativos ponderados pelo risco | 7: 202212–202412 |
| capital/1/5/79665 | Ativos Ponderados pelo Risco (RWA) | Ativos Ponderados pelo Risco (RWA) \n(i) = (f) + (g) + (h) | Corresponde à soma das parcelas referentes à exposição aos riscos de Crédito, de Mercado e Operacional | 33: 201503–202306 |
| capital/1/5/79665 | Ativos Ponderados pelo Risco (RWA) | Ativos Ponderados pelo Risco (RWA) \n(j) = (f) + (g) + (h) + (i) | Corresponde à soma das parcelas referentes à exposição aos riscos de Crédito, de Mercado e Operacional | 7: 202212–202412 |
| financial/2/1/78182 | `null` | Ativo Total | [10000007] + [20000004] | 60: 201003–202412 |
| financial/2/1/78183 | `null` | Carteira de Crédito Classificada | [31000000] | 60: 201003–202412 |
| financial/2/1/78184 | `null` | Passivo Circulante e Exigível a Longo Prazo e Resultados de Exercícios Futuros | [40000008] + [50000005] | 60: 201003–202412 |
| financial/2/1/78185 | `null` | Captações | [41000007] + [42000006] + [43000005] + [46000002] | 60: 201003–202412 |
| financial/2/1/78186 | `null` | Patrimônio Líquido | [60000002] + [70000009]+ [80000006] | 60: 201003–202412 |
| financial/2/1/78187 | `null` | Lucro Líquido | [70000009]+[80000006]-[81955002] | 36: 201003–201812 |
| financial/2/1/78187 | `null` | Lucro Líquido | [70000009]+[80000006]-[81956001] | 24: 201903–202412 |
| financial/2/1/79649 | `null` | Patrimônio de Referência para Comparação com o RWA | Montante de capital regulatório formado pela soma das parcelas de Capital Nível I e Capital Nível II | 20: 201003–201412 |
| financial/2/1/79664 | `null` | Índice de Basileia | Relação entre o Patrimônio de Referência e os Ativos ponderados pelo risco | 20: 201003–201412 |
| financial/2/2/78182 | `null` | Ativo Total \n(k) = (i) - (j) | [10000007]+[20000004] | 60: 201003–202412 |
| financial/2/2/78188 | `null` | Disponibilidades \n(a) | [11000006] | 60: 201003–202412 |
| financial/2/2/78189 | `null` | Aplicações Interfinanceiras de Liquidez \n(b) | [12000005] | 60: 201003–202412 |
| financial/2/2/78190 | `null` | TVM e Instrumentos Financeiros Derivativos \n(c) | [13000004] | 60: 201003–202412 |
| financial/2/2/78191 | Operações de Crédito | Operações de Crédito \n(d1) | [16000001]-[16900008] | 60: 201003–202412 |
| financial/2/2/78192 | Operações de Crédito | Provisão sobre Operações de Crédito \n(d2) | [16900008] | 60: 201003–202412 |
| financial/2/2/78193 | Operações de Crédito | Operações de Crédito Líquidas de Provisão \n(d) | [16000001] | 60: 201003–202412 |
| financial/2/2/78194 | Arrendamento Mercantil | Arrendamento Mercantil a Receber \n(e1) | [17000000]-[17900007] | 60: 201003–202412 |
| financial/2/2/78195 | Arrendamento Mercantil | Imobilizado de Arrendamento \n(e2) | [23000001] | 60: 201003–202412 |
| financial/2/2/78196 | Arrendamento Mercantil | Credores por Antecipação de Valor Residual \n(e3) | [49908008] | 60: 201003–202412 |
| financial/2/2/78196 | `null` | Credores por Antecipação de Valor Residual \n(j) | [49908008] | 60: 201003–202412 |
| financial/2/2/78197 | Arrendamento Mercantil | Provisão sobre Arrendamento Mercantil \n(e4) | [17900007] | 60: 201003–202412 |
| financial/2/2/78198 | Arrendamento Mercantil | Arrendamento Mercantil Líquido de Provisão \n(e) | [17000000] + [23000001] + [49908008] | 60: 201003–202412 |
| financial/2/2/78201 | `null` | Permanente Ajustado \n(h) | [20000004]-[23000001] | 60: 201003–202412 |
| financial/2/3/78185 | Captações | Captações \n(e) = (a) + (b) + (c) + (d) | [41000007] + [42000006] + [43000005] + [46000002] | 60: 201003–202412 |
| financial/2/3/78186 | `null` | Patrimônio Líquido \n(i) | [60000002] + [70000009]+ [80000006] | 9: 202212–202412 |
| financial/2/3/78186 | `null` | Patrimônio Líquido \n(j) | [60000002] + [70000009]+ [80000006] | 51: 201003–202209 |
| financial/2/3/78282 | Captações - Depósito Total | Depósitos à Vista \n(a1) | [41100000] | 60: 201003–202412 |
| financial/2/3/78285 | Captações - Depósito Total | Depósitos Outros \n(a6) | [41400009]+[41600005]+[41700008]+[41800001]+[41900004]-[41930005] | 19: 202006–202412 |
| financial/2/3/78285 | Captações - Depósito Total | Outros Depósitos \n(a5) | [41400009]+[41600005]+[41700008]+[41800001]+[41900004] | 41: 201003–202003 |
| financial/2/3/78286 | Captações - Depósito Total | Depósitos a Prazo \n(a4) | [41500002] | 60: 201003–202412 |
| financial/2/3/78287 | Captações - Depósito Total | Depósito Total \n(a) | [41000007] | 60: 201003–202412 |
| financial/2/3/78294 | Captações - Recursos de Aceites e Emissão de Títulos | Recursos de Aceites e Emissão de Títulos \n(c) | [43000005] | 60: 201003–202412 |
| financial/2/3/78295 | Captações | Obrigações por Empréstimos e Repasses \n(d) | [46000002] | 60: 201003–202412 |
| financial/2/3/78298 | `null` | Passivo Circulante e Exigível a Longo Prazo \n(h) = (e) + (f) + (g) | [40000008] | 60: 201003–202412 |
| financial/2/3/78299 | `null` | Resultados de Exercícios Futuros \n(i) | [50000005] | 51: 201003–202209 |
| financial/2/3/78300 | `null` | Passivo Total \n(j) = (h) + (i) | [40000008] + [60000002] + [70000009]+ [80000006] | 9: 202212–202412 |
| financial/2/3/78300 | `null` | Passivo Total \n(k) = (h) + (i) + (j) | [40000008] + [50000005] + [60000002] + [70000009]+ [80000006] | 51: 201003–202209 |
| financial/2/4/78187 | `null` | Lucro Líquido \n(j) = (g) + (h) + (i) | [70000009]+[80000006]-[81955002] | 36: 201003–201812 |
| financial/2/4/78187 | `null` | Lucro Líquido \n(j) = (g) + (h) + (i) | [70000009]+[80000006]-[81956001] | 24: 201903–202412 |
| financial/2/4/78203 | Resultado de Intermediação Financeira - Receitas de Intermediação Financeira | Rendas de Operações de Crédito \n(a1) | [71100001]+[71910002]+[71915007]+[71920009]+[71925004]+[71950000]+[71980001]+[81945005]+[81950007]+[81915004] | 60: 201003–202412 |
| financial/2/4/78208 | Resultado de Intermediação Financeira - Receitas de Intermediação Financeira | Receitas de Intermediação Financeira \n(a) = (a1) + (a2) + (a3) + (a4) + (a5) + (a6) | Somatório de Rendas de Operações de Crédito, Rendas de Operações de Arrendamento Mercantil, Rendas de Operações com TVM, Rendas de Operações com Instrumentos Financeiros Derivativos, Resultado de Operações de Câmbio e Rendas de Aplicações Compulsórias | 60: 201003–202412 |
| financial/2/4/78209 | Resultado de Intermediação Financeira - Despesas de Intermediação Financeira | Despesas de Captação \n(b1) | [81100008]+[81980008]+[81986002]+[81912007] | 60: 201003–202412 |
| financial/2/4/78213 | Resultado de Intermediação Financeira - Despesas de Intermediação Financeira | Resultado de Provisão para Créditos de Difícil Liquidação \n(b5) | [71990307]+[71990352]+[71990400]+[71990503]+[71990606]+[81830309]+[81830354]+[81830402]+[81830505]+[81830608] | 60: 201003–202412 |
| financial/2/4/78214 | Resultado de Intermediação Financeira - Despesas de Intermediação Financeira | Despesas de Intermediação Financeira \n(b) = (b1) + (b2) + (b3) + (b4) + (b5) | Somatório de Despesas de Captação, Despesas de Obrigações por Empréstimos e Repasses, Despesas de Operações de Arrendamento Mercantil, Resultado de Operações de Câmbio e Resultado de Provisão para Créditos de Difícil Liquidação | 60: 201003–202412 |
| financial/2/4/78215 | Resultado de Intermediação Financeira | Resultado de Intermediação Financeira \n(c) = (a) + (b) | Somatório de Receitas de Intermediação Financeira e Despesas de Intermediação Financeira | 60: 201003–202412 |
| financial/2/4/78216 | Outras Receitas/Despesas Operacionais | Rendas de Prestação de Serviços \n(d1) | [71700009]-[71794008]-[71795007]-[71796006]-[71797005]-[71798004]+[71970004] | 60: 201003–202412 |
| financial/2/4/78217 | Outras Receitas/Despesas Operacionais | Rendas de Tarifas Bancárias \n(d2) | [71794008]+[71795007]+[71796006]+[71797005]+[71798004] | 60: 201003–202412 |
| financial/2/4/78218 | Outras Receitas/Despesas Operacionais | Despesas de Pessoal \n(d3) | [81718005]+[81727003]+[81730007]+[81733004]+[81736001]+[81737000]+[81990201] | 60: 201003–202412 |
| financial/2/4/78219 | Outras Receitas/Despesas Operacionais | Despesas Administrativas \n(d4) | [71930006]+[8170006]-[81718005]-[81727003]-[81730007]-[81733004]-[81736001]-[81737000]+[81810006]+[81820003]+[81910009] | 60: 201003–202412 |
| financial/2/4/78223 | Outras Receitas/Despesas Operacionais | Outras Despesas Operacionais \n(d8) | [81800009]-[81810006]-[81820003]-[81830055]-[81830103]-[81830127]-[81830158]-[81830206]-[81830268]-[81830309]-[81830354]-[81830402]-[81830505]-[81830550]-[81830608]-[81830701]-[81830804]-[81830907]+[81900002]-[81910009]-[81912007]-[81915004]-[81925001]-[81930003]-[81933000]-[81940000]-[81945005]-[81950007] -[81956001]-[81960004]-[81980008]-[81986002]-[81990108]-[81990201]-[81990304]-[81990902] | 24: 201903–202412 |
| financial/2/4/78223 | Outras Receitas/Despesas Operacionais | Outras Despesas Operacionais \n(d8) | [81800009]-[81810006]-[81820003]-[81830055]-[81830103]-[81830127]-[81830158]-[81830206]-[81830268]-[81830309]-[81830354]-[81830402]-[81830505]-[81830550]-[81830608]-[81830701]-[81830804]-[81830907]+[81900002]-[81910009]-[81912007]-[81915004]-[81925001]-[81930003]-[81933000]-[81940000]-[81945005]-[81950007]-[81955002]-[81960004]-[81980008]-[81986002]-[81990108]-[81990201]-[81990304]-[81990902] | 36: 201003–201812 |
| financial/2/4/78226 | `null` | Resultado antes da Tributação, Lucro e Participação \n(g) = (e) + (f) | Somatório do Resultado Operacional e do Resultado Não Operacional | 60: 201003–202412 |

## Adoção humana posterior à pesquisa

João escolheu o conjunto R1/R2,Q1/Q2,C1+C3/C4,L2/L3 quando aplicáveis eE2-B, com limitações explícitas; trimestres efetivos, sínteses12meses e estoques médios pelas observações trimestrais incluindo abertura e ponderação pelo tempo. [Registro de14/10/2026](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6174707162). PareceresA/B/C validam evidência/propostas, e não substituem essa autoridade humana. Nenhum novo valor de indicador foi calculado pela adoção; testes, bindings, sinais, médias/fluxos e implementação seguem contrato próprio.

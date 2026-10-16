# Amostra fixa de unidades financeiras vinculadas a companhias brasileiras — 2024

[Issue125](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/125) · [decisão humana3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) · [plano](../superpowers/plans/2026-10-14-fixed-financial-sample-2024.md).

**Atualização aprovada em 16/10/2026:** o universo descritivo vigente é de **55 companhias abertas brasileiras CVM A/B**, das quais **32 têm associação IF.data comprovada no corte**, representadas por **24 unidades financeiras distintas**. A [pesquisa e lista nominal aprovada](cvm-open-financial-universe-2024-20261016.md), na [Issue 142](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/142), documenta as 55 identidades, as 23 sem correspondência principal admitida, as fontes e as pendências. A ampliação é documental: **nenhum cálculo ou dataset desta entrega anterior foi alterado**.

**Resultado histórico da Issue 125, preservado abaixo: 24 companhias/20 unidades.** Este documento conserva seleção, fontes, inventário complementar, exceções e cobertura calculada para a lista de 14/10. Não reapresentar seus percentuais, mapas temporais ou manifestos como resultados de 32 companhias/24 unidades ou do universo de 55. O requisito anterior de ações/Units negociáveis foi substituído por registro CVM A/B no corte; suspensão, controle, disponibilidade e comparabilidade continuam distintos. Estado de publicação/integração de cada entrega tem autoridade em sua própria Issue e PR, quando houver.

## Decisão e pergunta

João aprovou em14/10/2026 uma amostra fixa selecionada em **31/12/2024**, com dados financeiros **trimestrais de2010–2024** e verificação **anual** dos vínculos/unidades. A pergunta é a trajetória histórica das unidades financeiras ligadas às companhias escolhidas em2024; participação na bolsa em cada trimestre anterior não é requisito da seleção. Companhias domiciliadas no Brasil podem ter controlador estrangeiro. Holdings estrangeiras representadas porBDR ficam fora deste recorte simplificado.

Companhia emissora, instituição individual, conglomerado financeiro, prudencial e consolidado societário são identidades/perímetros distintos. Conglomerados financeiros e instituições independentes são as unidades principais, conforme dados nativos. Compartilhar grupo mantém as companhias na descrição, mas não cria outro balanço na soma. A presença de uma subsidiária listada não seleciona todo seu controlador; participação minoritária ou caminho candidato também não comprova controle.

O ponto2024 não retroprojeta aquisições, incorporações ou mudanças de perímetro. O cadastro de cada dezembro e os eventos relevantes sustentam a descrição anual; dados anteriores aoIPO podem ser usados quando a unidade histórica existe e sua correspondência está sustentada. Não repetir valores recentes, completar ausências comzero ou exigir série completa por critério silencioso.

## Universo de descoberta

Os21nomes citados inicialmente resultavam de um filtro preliminar restrito ao setorCVM“Bancos”, com registros de bolsa e candidatos nos dezembros2022/2023/2024. Eles não constituem teto, lista confirmada ou denominador das companhias financeiras. A seleção aprovada é2024, sem exigir sobrevivência nas três datas.

A pesquisa ampliou a triagem para outros setores financeiros, holdings, independentes e mudanças de2024, incluindo BRPartners, B3, Porto e casos de fronteira. Candidatura, falta de prova, exclusão fundamentada e companhia representada em grupo compartilhado permanecem separadas. PaísCAD inconsistente não define domicílio; nome/ticker posterior não é retrodatado.

## Fontes e integridade

- Núcleo108: manifest `5d3f1fa01872c50b581218be28e602722af242190fd549388ea487a23b859ba0`; CVM/FCA/FRE e relações candidatas com proveniência. Essas candidaturas são pistas para a conferência, não vínculos adotados automaticamente.
- Cadastro temporalBCB: manifest `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1`;60referências201003–202412 e15dezembros, campos nativos e null/vazio preservados.
- Valores OData, catálogo e reconciliação2024: [verificação117](financial-aggregate-validation-20261013.md) e [reconciliação120](financial-aggregate-reconciliation-20261014.md). Queries finitas em partes autenticadas, Decimal precisão120; nenhum saldo financeiro novo coletado.
- Documentos adicionais de emissores, B3/CVM/BCB e demonstrações2024: URLs, datas, corpos quando baixados, hashes e localizadores preservados na preparação privada. Uma fonte2025 só sustenta2024 quando explicita o fato/período; nome ou registro corrente sozinho não retroage.

## Denominadores BCB já conferidos

O universo principal é **Conglomerados Financeiros e Instituições Independentes**, `TipoInstituicao=2`. As1.422unidades de202412 não são1.422bancos listados; incluem outras atividades e cooperativas. O diagnósticoB1+B2 separa128unidades bancárias. Comparar contagem e peso econômico permite avaliar a diferença.

| Universo202412 | Unidades | Ativo observado R$ | Crédito observado R$ | PL observado R$ |
|---|---:|---:|---:|---:|
| Financeiro completo |1.422|17.480.613.833.662,29|6.160.206.235.951,83|1.573.410.516.537,41|
| B1+B2 |128|14.541.425.737.786,89|5.263.154.357.639,79|1.112.968.681.580,24|

Valores observados, sem estimar sete nulls do universo completo; B1+B2 tem cobertura numérica completa nesses estoques. O cadastroOData classifica B1+B2 como55Td=C/73Td=I, enquanto a ponteportal120 apresenta outra composição; os campos de fontes diferentes não foram transportados. Os sete nulls são doisB3C, doisN4, doisN1 e umN2, todos foraB1+B2.

Bindings conferidos em todas60referências: Ativo1/78182=`[10000007] + [20000004]`; Crédito2/78191=`[16000001]-[16900008]`; PL1/78186=`[60000002] + [70000009]+ [80000006]`. Estabilidade literal não certifica continuidade econômica, societária ou do regime. A verificação independente dos denominadores e de tokens nas fontes2010/2020/2024 passou.

O histórico contém89.476chaves código/trimestre e22.197código/dezembro. Dez ocorrências anuais de código não têm cadastro correspondente; a classificação é desconhecida. Há39bindings semCodInst nos60trimestres, mantidos em `ALL_OBSERVED` e separados de `ALL_NAMED`; não recebem companhia. Em dezembro2020 as ocorrências anônimas somam ativoR$565.642.676,21, créditoR$4.202.032,40 ePLR$50.098.758,11. Denominadores históricos bancários têm essa limitação de classificação.

## Lista principal fechada em 2024

**24 companhias, representadas por 20 unidades financeiras distintas: 14 conglomerados e seis independentes.** Dos 21 candidatos iniciais, 20 foram admitidos; Bemge permanece exceção de identidade/perímetro. A expansão trouxe B3, BR Partners, Porto e Itaúsa. Itaúsa compartilha a unidade Itaú e não acrescenta balanço. As 20 unidades não esgotam todas as subsidiárias ou participadas desses emissores: o inventário complementar abaixo mantém essa distinção.

| Unidade nativa BC em 202412 | Instituição/perímetro financeiro | Companhias brasileiras selecionadas |
|---|---|---|
| `00997185` | BANCO B3 S.A. | B3 S.A. - BRASIL, BOLSA, BALCÃO |
| `04902979` | BANCO DA AMAZONIA S.A. | BCO AMAZONIA S.A. |
| `04913711` | BANCO DO ESTADO DO PARÁ S.A. | BCO ESTADO DO PARA S.A. |
| `07237373` | BANCO DO NORDESTE DO BRASIL S.A. | BCO NORDESTE DO BRASIL S.A. |
| `13009717` | BANCO DO ESTADO DE SERGIPE S.A. | BCO ESTADO DE SERGIPE S.A. - BANESE |
| `13220493` | BR PARTNERS BANCO DE INVESTIMENTO S.A. | BR ADVISORY PARTNERS PARTICIPAÇÕES S.A. |
| `C0010045` | BRADESCO | BCO BRADESCO S.A. |
| `C0010069` | ITAU | ITAU UNIBANCO HOLDING S.A.; ITAÚSA S.A. |
| `C0020152` | MERCANTIL DO BRASIL | BCO MERCANTIL DO BRASIL S.A.; Mercantil Financeira S.A. - Crédito, Financiamento e Investi; BCO MERCANTIL DE INVESTIMENTOS S.A. |
| `C0030159` | BANESTES | BANESTES S.A. - BCO EST ESPIRITO SANTO |
| `C0030173` | BANRISUL | BCO ESTADO DO RIO GRANDE DO SUL S.A. |
| `C0030290` | BMG | BANCO BMG S/A |
| `C0030379` | SANTANDER | BCO SANTANDER (BRASIL) S.A. |
| `C0031976` | BRB | BRB BANCO DE BRASILIA S.A. |
| `C0041856` | ABC-BRASIL | BCO ABC BRASIL S.A. |
| `C0049906` | BB | BCO BRASIL S.A. |
| `C0049944` | BTG PACTUAL | BCO BTG PACTUAL S.A.; BCO PAN S.A. |
| `C0050304` | PINE | BCO PINE S.A |
| `C0051444` | PORTO SEGURO | PORTO SEGURO S.A. |
| `C0052357` | DMCARD | DM FINANCEIRA S.A. - CRÉDITO, FINANCIAMENTO E INVESTIMENTO |

BTG/PAN, as três companhias Mercantil e Itaú/Itaúsa aparecem uma vez por unidade nas somas. B3 é representada pelo Banco B3; Porto, pelo perímetro financeiro Portoseg. Esses balanços IF.data **não são o consolidado inteiro da B3 ou da seguradora Porto**, nem substituem demonstrações das companhias emissoras.

Identidade direta foi admitida por concordância de identificador, denominação e cadastro contemporâneo, caso a caso: é correspondência analítica explicitada, não regra universal de que todo código BC seja CNPJ. Caminhos indiretos têm suporte próprio. Banco B3: DF2024, p1, controle integral; BR Partners: DF2024, p7, controle indireto; Porto: FRE2024, participação integral em Portoseg, inferência majoritária rotulada; Itaúsa: [DF IUPAR2024, p1](https://estadaori.estadao.com.br/wp-content/uploads/2025/03/iupar-itau-unibanco-participacoes-sa-balanco-2025-03-01_08-20-25.pdf) e FRE2024, controle compartilhado IUPAR→ITH. Percentual de capital isolado não foi convertido em direitos de voto.

Porto Bank (`46350164`) não tem âncora no cadastro 202412 consultado; Porto Consórcio (`48041735`) está no cadastro, mas não no universo financeiro TI2. Ambos ficam sem incremento, preservando a companhia Porto por Portoseg. Isso não declara inexistência das entidades.

## Cobertura e representatividade

| Comparação em dezembro de 2024 | Unidades selecionadas / universo | Ativo | Crédito | PL |
|---|---:|---:|---:|---:|
| Financeiro BC completo, soma observada | 20 / 1.422 | 54,63% | 52,52% | 48,87% |
| Bancário B1+B2, unidades desse segmento | 18 / 128 | 65,52% | 61,33% | 68,93% |

Numeradores exatos completos: ativo R$9.549.478.593.289,84; crédito R$3.235.442.849.264,95; PL R$768.894.609.481,95. No segmento B1+B2: ativo R$9.527.156.478.919,44; crédito R$3.228.149.098.709,51; PL R$767.214.591.903,34. Percentuais são apresentação arredondada; o pacote conserva tokens e frações monetárias exatos. Nenhum dos três estoques das 20 unidades está ausente em 202412.

A triagem reconstituiu **55 nomes**, dos quais **31 companhias financeiras com evidência de elegibilidade em 2024** no universo documental observado. A correspondência estrita companhia→unidade principal foi aceita para **24/31 (77,42%)**. As sete restantes são Bemge, Alfa Holdings e cinco companhias de seguros/corretagem. REAG e seis casos sem prova suficiente de elegibilidade são apresentados à parte. Não foi encontrado, na busca finita, snapshot setorial oficial B3 de 2024 que certifique exaustividade; a [classificação B3 disponível](https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/acoes/consultas/classificacao-setorial/) é atualizada semanalmente. Portanto, 24/31 **não é uma estimativa certificada de todas as financeiras da Bolsa**.

O recorte tem peso econômico elevado dentro dos bancos e inclui os principais grupos bancários brasileiros com ações/Units locais; isso não prova representatividade estatística de toda a intermediação financeira. Caixa, BNDES, cooperativas, bancos privados sem emissor elegível e holdings estrangeiras explicam parte relevante da distância para o BC completo. Não foi imposto corte arbitrário de cobertura nem confundida quantidade de instituições com peso nos ativos.

## Exclusões e exceções nominais

| Casos pesquisados | Tratamento e fundamento |
|---|---|
| Investimentos Bemge | Ações/Units e controle por ITH documentados; o registro BC `01548981`, Financeira Bemge, tem identidade/perímetro divergente. Sem vínculo principal adicional admitido, sem apagar o registro nativo; Itaú já está representado por outras companhias. |
| Alfa Holdings | Continua no denominador de financeiras listadas. [ITR2024, p19](https://bancoalfa.com.br/institucional/downloads/1_5958.pdf) e [ITR2025 com comparativo2024, p17](https://bancoalfa.com.br/institucional/downloads/1_6112.pdf) classificam investimentos downstream como coligadas; não atribuir todo Alfa/Safra por participação minoritária ou inversão do controle. |
| BB Seguridade; Caixa Seguridade; IRB; Qualicorp; Wiz | Companhias do setor financeiro amplo, preservadas no denominador observado; atividade de seguros/corretagem não foi transformada em unidade financeira IF.data sem correspondência comprovada. Não são excluídas da explicação da Bolsa. |
| Cielo; Alper; Cia. Seguros Aliança da Bahia | Própria negociação/listagem encerrada em 2024, antes do corte: Cielo26/08, Alper23/09; Aliança fim de negociação19/01/fim de listagem08/02 e cancelamento08/03. Vínculo Cielo com bancos elegíveis é preservado no complementar. |
| Financeira Alfa; Consórcio Alfa; Banco Alfa Investimento | Cancelamentos CAD28/03/2024, corroborados pelo relatório Safra2024, p32. Histórico preservado, fora do ponto de seleção. |
| Paraná Banco | Término de negociação/listagem até2017 no FCA nativo; fora do corte2024. |
| REAG Trust; REAG Wealth; REAG Asset Management | FCA2025 informa início de negociação/listagem em2025; não retroagir. |
| CSU; TC; Atom; Betapart; Habitasul; Méliuz | Respectivamente tecnologia de pagamentos; plataforma de mercado; educação; holding sem operação; participações não financeiras após saída do braço financeiro; venda Bankly ao BV emnovembro2023. Clientes, aplicações em fundos, parceria comercial ou antigo setor não comprovam controle de operadora financeira em2024. |
| Inter & Co; Nu Holdings; XP Inc. | Holdings estrangeiras/BDRs fora do recorte aprovado de companhias domiciliadas no Brasil. Operadoras brasileiras são identidades distintas. Controle estrangeiro de companhia doméstica não é motivo de exclusão: Santander e ABC permanecem. |
| REAG Investimentos | Caso de fronteira: nome REAG desde30/12/2024, BDI ainda NINJ3; reorganização com efeitos17/04/2025. Não antecipar ao corte2024 o controle de operadoras de2025. |
| Santa Catarina Participações; Caixa Adm. Dívida Pública Estadual; Banco Nacional; Oliveira Trust; Daycoval; RCI Brasil | Elegibilidade de ações/Units no corte não comprovada no acervo consultado. Pendências explicitadas, fora do numerador, sem declaração de inexistência de negociação. |

As razões individuais, CNPJ14, datas FCA/CAD, códigos, URLs, hashes e localizadores constam do catálogo e recibos. Não se adotou país CAD inconsistente, ticker2025 ou ausência de volume no BDI de um único dia como veto automático. BPAC11 foi corroborado por apresentação BTG1T2024, p5, e BDI30/12/2024, p19; o token FCA `000000` ficou registrado como conflito da fonte.

As maiores unidades BC fora do principal também foram confrontadas: Caixa e BNDES são empresas públicas; Sicredi/Sicoob têm controle cooperativo/holding fechada; Nu/XP têm holdings estrangeiras; Citibank não apresentou emissor brasileiro elegível que o controle; Safra não é admitido por controlar Alfa Holdings. Ser grande ou ter controlador estrangeiro não foi, isoladamente, critério. Subsidiária listada não permite inverter o vínculo e selecionar todo seu controlador.

## Unidades ligadas em perímetro complementar

O critério uniforme do principal é o perímetro financeiro da instituição listada ou da operadora bancária/de crédito identificada sob a holding selecionada. Outras operadoras de pagamentos e participações compartilhadas permanecem no inventário complementar; a seleção do principal não obriga decomposição integral de todas as controladas. Assim, preservar um vínculo complementar não atribui seu balanço inteiro ao controlador nem elimina sobreposição.

A varredura finita de FRE2024, com até uma intermediária existente, confrontou os24 emissores e as30 maiores unidades fora do principal. O inventário contém12 pares: nove unidades BC distintas e Cartão BRB sem correspondência nativa. Não é censo de todas as subsidiárias de todos os emissores.

| Unidade/caso | Ligação observada e decisão |
|---|---|
| BV/Votorantim `C0051011`, operadora `59588111` | BB:49,99%FRE/50%DF2024,p79; [IFC, divulgado25/04/2024](https://disclosures.ifc.org/project-detail/SII/48428/gtfp-votorantim) declara propriedade e controle conjuntosBB/Votorantim. Vínculo positivo compartilhado; a tabela BB extraída agrupa coligadas/controladas em conjunto e não resolveu sozinha a classificação individual. |
| Cielo `01027058` | BB/Bradesco marcados controladores no FRE2024; DFBB2024,p79,nota6, participação total BB49,28%apósOPA. Uma unidade, deduplicada entre dois bancos; saída da própria Cielo da Bolsa não apaga o vínculo dos controladores. |
| Redecard `01425787` | [DFITH2024](https://estadaori.estadao.com.br/wp-content/uploads/2025/02/itau-unibanco-holding-sa-balanco-2025-02-19_23-18-44.pdf), físico p6,tabela100%, e p7,texto de controlada; FRE registra19,37854%diretos, não o total do grupo. Itaúsa vinculada pela rota de controle compartilhado IUPAR→ITH já documentada, não apenas pelos19,83%diretos. Uma unidade deduplicada. |
| B3 IP `47825528` | B3:100%literal no FRE2024. Participação integral documentada, sem novo balanço no principal. |
| Mulvi `03847413` | Banese:71,68%no FRE2024. Participação majoritária; não certificar direitos de voto/tipo de controle que a fonte deixou em branco. |
| Banrisul Soluções em Pagamentos `92934215` | Banrisul:99,78%no FRE2024; mesma ressalva de participação majoritária sem certificar campo de controle ausente. |
| Granito/InterPag `22177858` | BMG50% versus Inter & Co100%nas fontes2024; nome nativoInterPag. Conflito temporal/societário, sem controle BMG adotado. |
| BEN/Pluxee `30798783` | FRE registra BEN100%Santander Brasil; cadastro202412 nomeiaPluxee. Concordância de identificador candidato não certifica continuidade temporal/controle. |
| Getnet `10440482` | Unidade nativa existe; caminho2024 a partir de Santander Brasil não localizado na varredura. Marca/global parent não certifica controle pela companhia brasileira. |
| Cartão BRB `01984199` | FRE registra participação100%; âncora de CodInst8/TI2 não localizada. Identidade/domínio/perímetro permanecem desconhecidos. |

Foram rejeitados três caminhos BTG→Inter→operadoras porque a primeira aresta identifica BTG como não controlador. Também foi rejeitada a alternativa Itaúsa→ITH baseada somente em participação direta minoritária; a rota positiva IUPAR é independente. Fontes conflitantes não foram resolvidas por conveniência.

Os três casos originais tiveram seus valores nativos202412 conferidos individualmente: BV ativoR$140.976.182.780,89/créditoR$66.105.231.216,27/PLR$13.857.826.304,63; Cielo ativoR$120.211.374.935,14/créditoR$0,0/PLR$9.226.873.300,49; Redecard ativoR$128.999.092.769,67/créditoR$0,0/PLR$45.032.961.201,49. São descrições separadas, não parcelas adicionais aceitas de uma consolidação.

O complemento também conserva180 verificações par/ano:109 com operadora nativa presente e71 sem âncora;66 observações com caminho documental explícito de controle,30 participações sem certificação de controle e84 vínculos históricos não estabelecidos. Estados2024 positivos/conflitantes/desconhecidos são preservados, sem serem resolvidos automaticamente por observação antiga. Nesse complemento,83arestas de suporte têm referência diferente de31/12; vale a mesma ressalva de corpus anual, sem certificação automática de controle no encerramento.

As unidades complementares ficam individualizadas e deduplicadas, **sem soma ao principal e sem aumentar seus percentuais de cobertura**. Código distinto ou `CodConglomeradoFinanceiro=null` não prova ausência de sobreposição com demonstração consolidada do controlador. O total de TI2 é a soma observada de unidades de reporte, não consolidação nova de todo o SFN com eliminação de posições. Não criamos percentual proporcional de ativos pela participação societária.

## Verificação anual e disponibilidade trimestral

A amostra fixa seleciona as companhias de2024; a unidade correspondente é lida no cadastro **de cada trimestre**. São1.440 células companhia/trimestre (24×60), com1.431 presenças nativas e nove ausências da operadora BR Partners nos primeiros trimestres. Ausência fica sem valor, nãozero. As células companhia/trimestre não são1.440 balanços distintos: a seleção monetária é deduplicada por código/período.

Nos15dezembros, há20 unidades em2010/2011,21 em2012–2020 e20 em2021–2024. Foram31 alvos anuais diferentes do código de2024. PAN pertencia antes aoC0031323 e depois compartilhaC0049944 comBTG; DM era independente/Finansinos antes doC0052357; BR Partners reportou noC0051822 antes da unidade independente13220493. Conglomerado prudencial não substitui financeiro e campos ausentes de anos iniciais não foram preenchidos comcadastro recente.

O mapa anual de360 células distingue300 correspondências diretas de identidade,41 caminhos explícitos de controle observados no corpus documental do ano, cinco participações sem certificação de controle e14 vínculos históricos com a holding não estabelecidos. **Esses estados não certificam controle em cada31/12 nem durante todos os meses.** Das arestas documentais usadas,54 têm referência diferente de31/12, sobretudo01/01. Datas de referência, composição de capital, evento e ano do arquivo permanecem separadas. O cadastroBC de dezembro e o suporte societário anual são verificações diferentes.

A interpretação histórica é trajetória das unidades financeiras selecionadas pelo vínculo2024; não afirma que a holding já controlava a unidade antes de sua aquisição ouIPO. Assim, dados históricos disponíveis são preservados junto com os vínculos desconhecidos. Não se produziu painel artificialmente balanceado nem se retroprojetou propriedade recente.

Os60 trimestres contêm1.236 chaves financeiras código/período distintas, todas com presença de reporte. A única ausência numérica do núcleo nos três estoques é **BRB/C0031976 em202209 (`native_null`)**; os15dezembros têm valores completos no numerador. Presença de unidade não significa que todos seus valores estejam disponíveis.

| Dezembro | Unidades principais | Ativo / ALL observado | Crédito / ALL observado | PL / ALL observado |
|---|---:|---:|---:|---:|
| 2010 | 20 | 59,44% | 58,89% | 57,35% |
| 2014 | 21 | 57,58% | 54,24% | 63,30% |
| 2020 | 21 | 58,51% | 56,20% | 54,79% |
| 2024 | 20 | 54,63% | 52,52% | 48,87% |

Essas são coberturas de estoques observados e da seleção técnica, condicionadas aos vínculos históricos explicitados. Não são retorno, rentabilidade ou prova de comparabilidade econômica ao longo de15anos. As15janelas anuais completas,60trimestres de estoques, denominadores anônimos/classificação desconhecida e frações exatas ficam no pacote; histórico de códigos2024congelados foi conservado somente como diagnóstico rejeitado.


## Reprodução, integridade e revisão

Pacote local aceito em `data/curated/fixed-financial-sample-2024/`, com replay novo em `data/curated/fixed-financial-sample-2024-replay/`, no computador receptor. Manifest de ambos: **`bf54640a70964ca8468cdefc1fc2aaf53d1aab8985779005de21fc9b847467eb`**. São221arquivos registrados no manifest, incluindo207inputs congelados, dados derivados, recibos, fontes adicionais, pareceres e programa de reprodução. Os arquivos ignorados não acompanham o clone; o pacote local é necessário.

Principais saídas:

- `companies-2024.csv`, `units-2024.csv`:24companhias/20unidades principais, códigos e localizadores.
- `catalog-55.csv`, `complementary-2024.csv`, `largest-outside-reasons.csv`: catálogo integral de decisão,12pares complementares e grandes unidades externas, sem confundir desconhecido e exclusão.
- `company-quarter-map.json`, `annual-verification.json`, `complementary-annual-verification.json`:1.440células companhia/trimestre,360anuais principais e180anuais complementares, nativosNULLpreservados nosJSON.
- `stocks-quarterly.csv`, `coverage-annual.csv`, `coverage-2024.csv`:1.236chaves unidade/trimestre,225coberturas anuais com tokens/estados/frações exatos e tabela2024. CamposCSVde saldo têm estado próprio; célula vazia não ézero.
- `acceptance.json`, `input-pins.json`, `source-inputs/`: escopo aceito,207hashes de entrada e pacote congelado da evidência. Pin do índice de entrada: `f64edd8cb6196d664f9f9c59d9482296c70e4150b832d3000edcde6069c07dae`.

Reprodução finita somente com biblioteca padrãoPython, a partir do pacote local; destino deve ser novo. Não fazGETfinanceiro nem altera entradas:

```powershell
& .venv/Scripts/python.exe data/curated/fixed-financial-sample-2024/reproduce.py `
  --inputs data/curated/fixed-financial-sample-2024/source-inputs `
  --pins data/curated/fixed-financial-sample-2024/input-pins.json `
  --destination data/curated/fixed-financial-sample-2024-replay-new
```

Execução inicial e replay terminaram comexit0:225numeradores anuais recalculados a partir dos tokens trimestrais;221arquivos e manifest idênticos byte a byte. A conferência de fontes anterior autenticou cadastros, bindings e valores representativos2010/2020/2024; reprodução dos derivados não substitui essa revisão de fontes. O inventário de334inputs financeiros protegidos foi conferido antes/depois, além dos pins do núcleo108/cadastro e dos inputs usados no histórico. Nenhum saldo financeiro novo coletado, nenhum arquivo aceito anterior sobrescrito.

O desenho, descobertaA, vínculos principaisV2/mapa2024, denominadores2024/históricos, mapa temporalRoot,225coberturas numéricas e complementoV4/anual tiveram revisão independente porfatias. A correção de localizador Redecardp6/p7 foi preservada como delta do checkpointV3. Os pareceres e hashes acompanham o pacote; revisão final da composição/publicação, SHA entregue, checks e ancestralidade têm autoridade naIssue125 ePRvinculada. O registro público evita afirmar que revisão de agente seja aprovação humana elegívelGitHub.

Esta entrega fecha a lista técnica sob o recorte aprovado e conserva as exceções. Não adota indicador, fórmula, índice único, manuscrito ou comparabilidade econômica plena; pesquisa111 não foi retomada. AIssue3 conserva decisões acadêmicas restantes e aIssue2 registra a fronteira de trabalho; Project3permanece comZec.

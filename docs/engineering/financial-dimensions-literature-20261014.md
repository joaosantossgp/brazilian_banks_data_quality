# Cinco dimensões financeiras: fundamentos, candidatos e ponte para o IF.data

Pesquisa dirigida da [Issue 111](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/111), 14/10/2026. Esta nota entrega fundamentos, fichas e diagnóstico de cobertura **A–C**, com propostas de seleção **D**, após revisões independentes por fatia. As25fichas registram a pesquisa candidata; **João adotou o conjunto inicial e a regra temporal descritos na decisão ao final desta nota**. As demais alternativas permanecem candidatas. A coberturaC usa o handoff local aceito da [amostra125](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/125), depois integrado pelo PR126. A implementação seguirá as [escolhas registradas por João](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6174707162), com contratos técnicos e validação próprios. Não é revisão sistemática nem demonstração de causalidade.

Assaf Neto é o eixo conceitual. O [registro de fontes e proveniência](financial-dimensions-literature-20261014.provenance.md) identifica edição, páginas efetivamente lidas, versões e limites; [REFERENCES](../../REFERENCES.md) mantém a biblioteca geral. Os códigos foram confrontados com metadados e disponibilidade conjunta dos componentes na amostra, com limites abaixo. Não há indicadores acadêmicos calculados; somas de ativos foram usadas exclusivamente para auditoria de cobertura.

## Pergunta e alcance

O desenho vigente seleciona companhias domiciliadas no Brasil em 31/12/2024 e acompanha seus negócios financeiros em 2010–2024. Controle estrangeiro é compatível com esse domicílio; holding estrangeira por BDR está fora desse recorte. Amostra fixa de companhias não significa painel balanceado de unidades, controlador constante ou cobertura completa desde 2010. A análise descreve o histórico dos selecionados em 2024 e conserva o viés de sobrevivência/saída de mercado. A #125 é responsável por consolidar essa decisão e os vínculos; esta nota não certifica sua entrega preliminar.

Medir conglomerado financeiro ou instituição independente exige manter explícitos unidade, perspectiva e vínculo temporal com a companhia. O prudencial acrescenta a pergunta sobre capital elegível e risco; não substitui automaticamente o financeiro nem pode ser somado a ele. A soma dos conglomerados já consolidados evita repetir suas controladas, mas ainda contém exposições entre grupos: não equivale à consolidação integral do SFN. Fundamento: IF.data, notas 1–3; FMI **draft 2019**, §§6.3–6.6 e 6.22–6.30.

## Por que cinco dimensões

### Rentabilidade: como aplicações, funding e custos chegam ao resultado

O banco capta recursos, aplica em crédito e outros ativos e presta serviços. A diferença entre receitas e despesas de intermediação é um resultado monetário, não uma taxa de spread automaticamente. Despesas operacionais, provisões, tributos e outras receitas alteram o lucro final. Por isso ROA, ROE e margem respondem perguntas diferentes: resultado por ativo, resultado por capital próprio e parcela da receita retida como lucro. Assaf, cap.18, pp.332–333 e 340–342; a separação da DRE está no cap.17, pp.321–322 e 327–329.

Com bases compatíveis, `LL/PL = (LL/AT) × (AT/PL)`. Um ROE maior pode resultar de maior retorno dos ativos ou de menor participação do capital próprio. Não basta chamá-lo de melhor desempenho sem observar risco e alavancagem. A identidade é diagnóstica, não causal; misturar PL médio com AT final sem ajustar os demais termos destrói essa decomposição. Assaf, pp.341–342.

O FMI draft, §§7.46–7.55, prefere resultado antes de tributos para ROA em comparações internacionais e após tributos para ROE. Assaf usa lucro líquido em ambos. Recomenda-se manter a definição de Assaf como proposta principal brasileira, identificando o ROA antes de tributos como sensibilidade de definição; nenhum deles é superior por mera autoridade bibliográfica. Não chamar a variante após tributos de reprodução do ROA preferido pelo FMI.

### Qualidade do crédito: proteção contábil, atraso e perdas são medidas distintas

Provisão/carteira bruta informa quanto foi reconhecido contabilmente frente ao crédito. Pode aumentar por deterioração, prudência, mudança de composição ou regra; não mede sozinho atraso observado. Despesa de provisão é fluxo da DRE; provisão acumulada é estoque. Baixas, reversões e reclassificações impedem tratar sua variação como despesa. Assaf, p.324; Resolução 2.682/1999, arts.1–9, compilação v2P.

Lima et al. chamam uma razão de provisão/crédito de INADIM, mas a operação observada continua sendo uma proxy de provisionamento, não uma taxa de inadimplência (tabela 4, p.190). A nomenclatura do estudo não autoriza repetir essa equivalência no projeto. NPL exige atraso/default e carteira compatível; níveis E–H incorporam critérios além de atraso e exceções de prazo. Resolução 2.682, art.4; FMI draft, §§7.29 e 7.34–7.42.

As cinco dimensões são obrigatórias, mas o conjunto atual de provisões cobre crédito **parcialmente**. Se atraso for indispensável à conclusão, registrar necessidade de fonte adicional; não preencher a lacuna com uma razão disponível e renomeá-la. Uma unidade sem carteira relevante não recebe qualidade ruim por não aplicabilidade, nem é excluída da análise das outras dimensões.

### Capital e alavancagem: quem suporta perdas, com qual base de risco

PL/AT informa financiamento próprio contábil; AT/PL expressa a alavancagem correspondente. São recíprocos quando AT e PL são ambos não nulos, na mesma data e perímetro; não constituem dois fatores independentes para um eventual índice. PL/AT igual não implica risco igual dos ativos. Assaf, pp.336–338.

PR/RWA considera instrumentos elegíveis, deduções e riscos de crédito, mercado e operacional, inclusive exposições fora do balanço. Capital principal e Nível I qualificam a composição desse suporte. Portanto PL/AT complementa o prudencial; não reproduz Basileia e seu inverso não é a Razão de Alavancagem regulatória. FMI draft, §§7.9–7.26; Resoluções 3.490/2007, arts.1–2, e 4.193/2013, art.3.

As referências históricas de 11% e 13% do livro não são limiares universais de 2010–2024. A norma original 4.193 prevê cronograma, adicionais e exceções; o REF abr.2025 descreve regimes e transições por atividade. Esta pesquisa não reconstruiu todas as alterações trimestrais. Recomenda-se descrever os indicadores publicados e seus componentes antes de calcular folga regulatória; essa folga exige norma válida por unidade, regime e data, inclusive adicionais e transições. Resolução 4.193, arts.4–8 e 18; REF, pp.100 e 103.

### Liquidez e financiamento: caixa disponível e estrutura de funding

Liquidez é capacidade de atender obrigações e demanda de caixa; solvência é capacidade patrimonial de absorver perdas. Um ativo valioso pode não gerar caixa no momento necessário. Maturidade, negociabilidade, restrições e custo de refinanciamento importam. Caixa/depósitos à vista e liquidez imediata de Assaf observam uma parte dessa capacidade; crédito/depósitos observa a estrutura de financiamento. Nenhuma dessas razões certifica resistência a estresse. Assaf, pp.333–335.

Mais caixa tem benefício de segurança e custo de oportunidade; crédito/depósitos elevado pode refletir uso de letras, repasses ou capital, e não crise. O LTD do REF inclui outras captações e usa visão prudencial; não deve ser confundido com crédito/depósitos totais na visão financeira. Assaf, p.335; REF, pp.100–101.

LCR exige ativos elegíveis e saídas líquidas sob estresse em **30 dias calendários**; NSFR exige funding disponível e requerido com ponderações e horizonte anual. TVM agregado não equivale a HQLA. IL do REF tem horizonte de **30 dias úteis** e recursos/fluxos estressados próprios; não é reprodução automática do LCR. BCBS 2013, §§17 e 19–22; BCBS 2014, §§9 e 12–17; REF, pp.103–104. Esses indicadores ficam como necessidades específicas, sem reconstrução a partir de saldos genéricos.

### Eficiência operacional: despesas relativas à receita, com atividade explícita

Assaf define despesas operacionais/RIF (p.342). O FMI draft define despesas não juros/gross income e exclui provisões (§§7.56–7.63). RIF bruta não é gross income do FMI: este combina margem líquida de juros e outras receitas líquidas pertinentes. Pessoal + administração é uma proxy de despesas mais estreita, não sinônimo automático de todas as despesas operacionais. Assaf, pp.321–322 e 342.

Uma razão custo/receita melhora se custos caem, mas também se receitas crescem por spread, risco ou ciclo, sem aumento de produtividade física. Modelos focados em serviços, crédito ou tesouraria têm estruturas diferentes. Tecles e Tabak, pp.11–19, mostram que a definição de produtos — inclusive depósitos — altera fronteiras de eficiência bancária. Sua SFA não valida uma razão contábil como eficiência técnica. Recomenda-se nomear exatamente despesas e receita, explicar composição e não transportar rankings, coeficientes ou cortes dos estudos.

Souza et al., quadro 2, p.979, usam IEO e IE com componentes diferentes; não são recíprocos. O IE inclui PECLD e exige resolver estoque/fluxo/sinal antes de reprodução. O estudo de agências de fomento é contraponto de atividade, não justificativa para incluir essas agências na amostra CVM/B3 ou impor o índice aos conglomerados.

## Contrato comum das fichas

As fórmulas seguintes são expressas com custos/provisões em magnitude econômica positiva **depois** de conciliar o sinal nativo. Isso não autoriza `abs()` generalizado: reversões, prejuízos e saldos negativos são informação. Valor ausente não vira zero. Todos os cálculos exigem mesma unidade/perspectiva/regime e componentes sem sobreposição.

- **Estoque/estoque:** fotografia trimestral na mesma referência, razão adimensional apresentada em % ou vezes conforme nome. Síntese anual proposta: fotografia de dezembro, identificada como tal.
- **Fluxo/fluxo:** mesma janela disjunta comprovada, %; não anualizar uma razão cuja janela já coincide. Síntese anual proposta: razão das somas anuais dos fluxos, não média dos quatro percentuais.
- **Fluxo/estoque:** propor janela trimestral real e TTM como apresentação de tendência. Estoque médio é adaptação a especificar; FMI draft §7.48 determina média de AT para ROA, mas §7.52 não especifica literalmente PL médio. PL médio foi adotado posteriormente por João com a regra temporal ao final desta nota; não é atribuído literalmente ao FMI. TTM requer quatro trimestres disjuntos e base de abertura; `trimestre × 4` é taxa mecânica, não lucro anual realizado ou previsão.
- **Evidência nativa já disponível:** o [piloto88](ifdata-indicator-pilot-20261011.md#complemento-da-fatia-a-ponte-contábil-para-janelas-nativas) fundamentou e teve aceita, para o ensaio, `native-semester-v1` de LL78187 (Resumo1/DRE4), RAT78226 e RIF78208 (DRE4): março=jan–mar, junho=jan–jun, setembro=jul–set, dezembro=jul–dez. A alternância3/6 meses não é trimestre uniforme. A especificação Olinda documentou valores monetários em **R$**, sem conversão por mil; a escala de IB/ICP continua própria. Reaproveitar essa evidência e seus contextos/definições; não estendê-la automaticamente a novas rubricas.
- **Derivações novas:** trimestre por diferença dos acumulados, somas anuais e TTM permanecem propostas a contratar; a regra aceita para o piloto não as aprovou. Novas contas de custos/receitas/provisões precisam conciliação de janela. Abertura200912 já foi tratada em entrada auxiliar do piloto, mas não foi revalidada aqui para a amostra125. Comparabilidade de componentes/vínculos continua pendente mesmo quando há60 referências.
- **Denominadores:** zero gera estado indefinido; PL negativo ou receita não positiva exige advertência interpretativa e não recebe classificação automática de bom desempenho. Não excluir essas unidades silenciosamente. Valores negativos de numeradores válidos são preservados.
- **Aplicabilidade:** atividade real e composição do conglomerado precedem escolha. Banco captador, intermediária de serviços e IP não ganham a mesma métrica apenas por compartilhar o emissor. Fontes lidas não certificam, sozinhas, regras de todas as IP/CTVM/holdings.

Estados: **M** = componentes candidatos localizados; conciliação técnica/metodológica ainda necessária. **A** = adaptação conceitual relevante antes de escolher. **L** = componente ou requisito não comprovado no corpus admitido. Nenhum estado significa indicador aceito para cálculo acadêmico. Fichas identificadas abaixo herdam integralmente o contrato comum.

## Fichas: rentabilidade

| ID / pergunta e fórmula candidata | Atividade, janela e escala | Fonte e interpretação / ponte e estado |
|---|---|---|
| R1 ROA após tributos: `LL/AT médio` | Unidades operacionais com demonstrações compatíveis; fluxo/estoque, % por janela declarada. Média é adaptação à expressão LL/AT do livro. | Assaf pp.340–342; FMI draft §§7.46–7.49 para média AT. Intensidade de lucro do ativo; mix e risco alteram comparação. F1+F2; **M**, quebra LL em 201903 e média a definir. |
| R2 ROE: `LL/PL médio` | Mesmas unidades; fluxo/estoque, %. PL médio proposto, não atribuído literalmente ao FMI §7.52. | Assaf pp.341–342; FMI draft §§7.50–7.55. Retorno contábil sobre capital, sensível a alavancagem; PL negativo muda interpretação. F1+F2; **M/A**. |
| R3 Margem líquida da intermediação: `LL/RIF` | Principalmente intermediação; fluxo/fluxo, %. | Assaf p.341. Não é margem sobre toda receita; serviços relevantes podem torná-la pouco representativa. F1+F3; **M**, explicar composição de receitas. |
| R4 Margem financeira do livro: `RBIF/AT médio` | Intermediação; fluxo/estoque, %. | Assaf p.342 define RBIF/AT; média é adaptação. Diferença de receitas/despesas por ativo não é NIM de juros líquidos certificada. F1+F3; **M/A**. |
| R5 Rendimento bruto do crédito: `receita de crédito/carteira média` | Atividade creditícia; fluxo/estoque, %. | Assaf p.342; Souza quadro2/p.979 (denominador literal carteira). Carteira média é adaptação. Não deduz funding, perdas ou custos; maior taxa não prova melhor resultado. F4+F5; **M/A**, carteira produtora da receita deve coincidir. |
| R6 ROA antes de tributos: `resultado antes de tributos/AT médio` | Sensibilidade de definição; fluxo/estoque, %. | FMI draft §§7.46–7.49. Não usar resultado operacional como equivalente sem conciliar não operacional. F1+F3; **A**, NomeColuna78226 inclui “antes da Tributação, Lucro e Participação”; sua janela foi fundamentada no piloto, mas a composição não foi conciliada à definição FMI. |

## Fichas: qualidade do crédito

| ID / pergunta e fórmula candidata | Atividade, janela e escala | Fonte e interpretação / ponte e estado |
|---|---|---|
| Q1 Intensidade de provisionamento: `provisão de crédito/carteira bruta` | Unidades com crédito; estoque/estoque, %. Não usar carteira líquida de provisões. | Assaf p.324; Res2.682 arts1–6; Lima tabela4/p.190. Proteção contábil, não inadimplência. F4; **M**, sinal e abrangência crédito/arrendamento a provar. |
| Q2 Incidência do custo de perdas: `despesa líquida de provisão/carteira média` | Crédito; fluxo/estoque, %. | Assaf p.324 e Res2.682 arts6–9 para estoque/fluxo; BCB REF **novembro2024**, p37, gráfico1.2.3.6/nota1, usa despesa com provisões/carteira média, em12 meses. Aplicação IF.data é proposta, sem reproduzir ajustes/médiaBCB. F4+F5; **A**, reversões/abrangência/sinal da conta78213 e janela precisam contrato. |
| Q3 NPL: `crédito não performado/carteira bruta compatível` | Crédito; estoque/estoque, %. | FMI draft §§7.29 e 7.34–7.38. Atraso/default observado; E–H não é identidade. **L**, componentes de atraso não comprovados neste corpus. |
| Q4 Cobertura específica: `provisão específica/NPL` | Crédito; estoque/estoque, %; NPL zero indefinido. | FMI draft §§7.27–7.42. Provisão total pode ter população diferente de NPL. **L**, depende Q3 e identificação de provisões adequadas; não denominar Q1 como cobertura de inadimplência. |

## Fichas: capital e alavancagem

| ID / pergunta e fórmula candidata | Atividade, janela e escala | Fonte e interpretação / ponte e estado |
|---|---|---|
| C1 Capitalização contábil: `PL/AT` | Unidades com balanço; estoque/estoque, %. | Assaf p.337. Financiamento próprio, sem ponderação de risco. F1; **M**, principal candidato contábil; não comparar a mínimo Basileia. |
| C2 Alavancagem contábil: `AT/PL` | Mesmas unidades; estoque/estoque, vezes. | Assaf p.337. Leitura complementar de C1, não informação independente. F1; **M**, PL zero/negativo explícito. |
| C3 Basileia publicado / `PR/RWA` conciliado | Unidade prudencial aplicável; estoque/estoque, %. | FMI draft §§7.9–7.26; Res4.193 art3. F6; **M/A**, índice publicado e cálculo exigem primeiro comprovar a escala nativa, ainda não confirmada; ponte financeira2010–14 não certificada. |
| C4 Capital principal publicado / `CP/RWA` conciliado | Prudencial aplicável; estoque/estoque, %. | Mesmas fontes, qualidade do capital. F6; **M/A**, não somar perímetro com C1 nem preencher períodos anteriores. |
| C5 Folga sobre requerimento válido | Prudencial aplicável; diferença em pontos percentuais, data/regime específicos. | Res4.193 arts4–8, REF pp.100/103. **L**, cronologia completa e adicionais não reconstruídos; não usar 13% uniforme. |

## Fichas: liquidez e financiamento

| ID / pergunta e fórmula candidata | Atividade, janela e escala | Fonte e interpretação / ponte e estado |
|---|---|---|
| L1 Encaixe voluntário: `disponibilidades/depósitos à vista` | Depositária; estoque/estoque, %. | Assaf p.334. Caixa imediato versus passivo à vista; segurança/custo de oportunidade. F7+F8; **M**, sem limiar universal. |
| L2 Liquidez imediata: `(disponibilidades+aplicações interfinanceiras de liquidez)/depósitos à vista` | Depositária; estoque/estoque, %. | Assaf p.334. Proxy contábil, não LCR; verificar restrições e liquidez efetiva. F7+F8; **M**. |
| L3 Crédito/depósitos totais | Depositária com crédito; estoque/estoque, %. | Assaf p.335; diferença LTD/REF pp.100–101. Fontes alternativas explicam razão elevada. F4+F8; **M**, denominação precisa; não reproduz LTD prudencial REF. |
| L4 Perfil de funding: participações de depósitos, emissões e empréstimos/repasses em base de captação conciliada | Unidade captadora; estoque/estoque, %. | Assaf pp.321–325 e 332–335 para mecanismos; participações são proposta própria. F8; **A**, validar soma sem sobreposição, não somar rubricas e agregado pai nem chamar base incompleta de funding total. |
| L5 LCR | Prudencial e escopo regulatório; HQLA/saídas líquidas estressadas30 dias calendários, %. | BCBS2013 §§17/19–22; Res4.401 arts2–5 e Res4.616 arts6–7. **L**, componentes elegíveis/estresse não comprovados; não obrigação é ausência estrutural. |
| L6 NSFR | Prudencial aplicável; ASF/RSF, horizonte anual, %. | BCBS2014 §§9/12–17; Res4.616 arts2–3/7. **L**, maturidades e ponderações não comprovadas; L3 não o substitui. |

## Fichas: eficiência operacional

| ID / pergunta e fórmula candidata | Atividade, janela e escala | Fonte e interpretação / ponte e estado |
|---|---|---|
| E1 IEO literal: `despesas operacionais/RIF` | Intermediação; fluxo/fluxo, %. | Assaf p.342; Souza quadro2/p.979. Menor custo relativo exige receita positiva e composição compatível. F3; **A**, construir despesas operacionais corretas; outras despesas operacionais não é o total. |
| E2 Despesas administrativas e de pessoal/receita operacional compatível | Bancos e serviços sob definição própria; fluxo/fluxo, %. | Proposta estreita, confrontada com Assaf pp.321–322 e FMI draft §§7.56–7.63. F3; **A**, alternativas E2-A/B/C abaixo explicitam denominador; não chamar reprodução literal de Assaf/FMI/BCB. |
| E3 Intensidade de pessoal+administração: `(pessoal+admin)/AT médio` | Apoio à leitura do modelo; fluxo/estoque, %. | Proposta analítica, não fórmula de eficiência técnica de Tecles/Tabak. F1+F3; **A**, base média/janela; instituições com grande tesouraria diferem das focadas em serviços. |
| E4 IE de fomento: `(RBIF+serviços+PECLD)/(admin+pessoal)` | Contraponto de atividade, sem inclusão de agências na amostra. Fluxo/fluxo somente após conciliação. | Souza quadro2/p.979. **L/A**, PECLD de estoque/fluxo/sinal não resolvida; não calcular nem tratar como inverso E1. |

## Eficiência: três alternativas concretas para E2

A consulta focal ao BCB complementa Assaf e resolve a ambiguidade de nomes, sem impor uma reprodução oficial. O [REF setembro2016](https://www.bcb.gov.br/content/publicacoes/ref/201609/RELESTAB201609-refSFi.pdf), p40/nota44, abre componentes do denominador; o [REF abril2024](https://www.bcb.gov.br/content/publicacoes/ref/202404/RELESTAB202404-refPub.pdf), p33/nota52, fala em receitas operacionais; o [REF **novembro2024**](https://www.bcb.gov.br/content/publicacoes/ref/202410/RELESTAB202410-refPub.pdf), p37/nota56, fala em resultado operacional excluindo efeitos das provisões. A pasta202410 não é a data editorial da capa. Gráficos2016/p40 e novembro2024/p38 mostram que **administrativas do REF incluem pessoal**; a coluna IF.data78219 é separada de78218. A equivalência exata desse total permanece a conferir.

Notação proposta: `xNN` é o saldo assinado da coluna782NN, na mesma janela/regime/perímetro. **Somente se a convenção de despesas negativas for comprovada**, `C=−(x18+x19)` representa o custo de pessoal+administração. Outro sinal requer adapter explícito, conservando reversões; não usar valor absoluto automático.

| Alternativa | Fórmula proposta | O que mede / limite |
|---|---|---|
| **E2-A: proxy estreita ligada ao IEO de Assaf** | `C/x08` | Mantém RIF do livro, mas troca despesas operacionais totais pelo subconjunto pessoal+admin. Não é reprodução literal; serviços relevantes ficam fora da receita, e RIF incorpora resultados/ajustes nativos. |
| **E2-B: custo/renda selecionada de intermediação e serviços antes da provisão** | `C/(x15−x13+x16+x17)` | Retira a provisão assinada já incorporada no RBIF e adiciona serviços/tarifas. Sob custo positivo conciliado, retirar despesa negativa corresponde a adicionar o custo de volta. Não retirar toda78214: isso também retiraria funding e outros custos financeiros. Exclui participações/arrendamento operacional/outras linhas ainda não mapeadas; não é IEO-BCB nem gross income FMI certificado. |
| **E2-C: IEO-BCB reproduzido exatamente** | De-para ainda não demonstrado, não calculável por nome | Fonte2016 inclui participações, arrendamento operacional e outras receitas/despesas, com distinção do efeito de provisões. Requer mapear componentes, tributos, ajustes, janela e perímetro próprios; custo de pesquisa maior. |

O catálogo separa serviços78216 das tarifas78217 por suas descrições, motivando sua soma no contexto demonstrado; isso não certifica toda a continuidade econômica. Resultado operacional78225 já inclui custos de pessoal/administração/tributos via78224 e provisão via78215. Usá-lo diretamente como renda anterior aos custos mistura mecanismos e não reproduz o índice apenas por nome. A hipótese `x25−x13−x18−x19` mantém tributos e outros itens; tampouco foi demonstrada equivalente ao denominador oficial.

**Recomendação proposta:** E2-B como ponto de partida para unidades com intermediação e serviços, E2-A como sensibilidade de definição; diagnosticar participação das receitas excluídas antes de comparar atividades. Para unidade dominada por outras rendas, rever aplicabilidade/denominador explicitamente. E2-C só se a pergunta exigir reprodução oficial. Não escolher a proxy pelo resultado mais favorável. As alternativas são fluxo/fluxo, exigem renda positiva para interpretação usual e não se anualizam multiplicando apenas o numerador. TTM permanece condicionado a fluxos disjuntos comprovados.

## Localizadores dos componentes e disponibilidade documental

Fonte: [inventário 113](ifdata-segmentation-inventory-20261013.md) e [catálogo temporal](ifdata-variable-catalog-20261011.md). Números são **Conta**, não código COSIF. No contexto financeiro abaixo: `dataset=financial`, `TipoInstituicao=2`; **Grupo varia por rubrica, inclusive `null`**, e integra a chave junto com relatório, NomeColuna e definição literal. A consulta tipada doParquet distingue nulo de stringvazia, distinção perdida na serializaçãoCSV. NomeColuna pode conter a fórmula que diferencia variantes prudenciais. O agrupamento abaixo é pista de implementação; o [apêndice de proveniência](financial-dimensions-literature-20261014.provenance.md#contextos-nativos-confrontados) preserva os contextos selecionados. Não transportar esses identificadores para individual/prudencial por semelhança de nome.

| Ponte | Relatório / contas candidatas | Oferta documental no núcleo / ressalva |
|---|---|---|
| F1 | Resumo1: AT78182 `[10000007]+[20000004]`; PL78186; LL78187 | 60 referências201003–202412. LL tem variantes201003–201812 e201903–202412; definições e equivalência precisam conciliação. |
| F2 | AT/PL de abertura e observações intermediárias da mesma unidade | Não é nova conta. Precisam vínculo, referências e comparabilidade; abertura200912 é entrada auxiliar existente do piloto; sua adequação à amostra125 não foi revalidada nesta pesquisa. Não sacrificar2010 silenciosamente para TTM. |
| F3 | DRE4: RIF78208; RBIF78215; pessoal78218; admin78219; serviços78216; tarifas78217; outras despesas78223; antes tributos78226 | Contas candidatas nas60 referências; outras despesas tem variantes36/24 referências com fronteira201903. LL/RAT/RIF têm janela nativa fundamentada no piloto; demais fluxos, sinal e composição precisam conciliação. Serviços/tarifas não somados sem comprovar disjunção. |
| F4 | Ativo2: crédito78191; provisão78192; crédito líquido78193; arrendamento e provisões78194–78198 em contextos próprios | 60 referências; Resumo78183 é carteira classificada `[31000000]`, não substituto automático da carteira de crédito do ativo. |
| F5 | DRE4: receita crédito78203; despesa provisão78213; captação78209; DIF78214 | 60 referências documentais, não garantia de valor por unidade nem comprovação de janela/abrangência. |
| F6 | Capital5: PR79649, RWA79665, CP79645, IB79664, índiceCP79659 | `dataset=capital`, `TipoInstituicao=1`, grupos e definições por rubrica. Oferta desde 201503:40 trimestres no núcleo; RWA/IB/ICP têm variantes em listas efetivas de períodos disjuntas, embora os intervalos mínimo–máximo se cruzem em202212–202306; PR muda contexto em202412. Selecionar pelas listas exatas do catálogo, sem criar falsa ambiguidade porintervalo ou somar variantes. Não implica40valores porcompanhia. Capital financeiro anterior não tem ponte certificada. |
| F7 | Ativo2: disponibilidades78188; aplicações interfinanceiras78189; TVM+derivativos78190 | 60 referências. A terceira rubrica não é adicionada a L2 nem rotulada HQLA. |
| F8 | Passivo3: à vista78282; a prazo78286; total depósitos78287; emissões78294; empréstimos/repasses78295; Resumo1 captações78185 | 60 referências, com definições próprias. Outros depósitos78285 muda contexto/denominação incluindo conta pré-paga; validar antes de recorte por atividade. |

Três armadilhas impedem ampliar essa ponte por rótulos: **Passivo Total78300 inclui componentes de PL** e muda definição em 202212, portanto não é automaticamente exigível; **Permanente Ajustado78201** subtrai conta23000001, sem equivalência certificada com o ativo permanente de Assaf; a DRE e o lucro mudam definições em201903. Presença contínua do código não prova continuidade econômica. Juro passivo/DIF sobre passivo e imobilização ficam fora da shortlist até conciliação. Não inferir resultados de exercícios futuros iguais a zero porque a rubrica separada78299 termina202209.

## Segmentações para explicar os resultados

O [inventário113](ifdata-segmentation-inventory-20261013.md) é a autoridade sobre oferta observada. Esta pesquisa considera o mapa amplo IF.data + CVM/B3; não promete que todo recorte possível no portal esteja instalado ou seja significativo para a pergunta.

| Eixo | Uso proposto | Restrição temporal/conceitual |
|---|---|---|
| Tipo/atividade: Tcb, SegmentoTb, Atividade | Separar intermediação, serviços e composição efetiva; interpretar denominadores | Lacunas e de-para históricos; categoria cadastral não substitui mix do conglomerado. Atividade financeira não é setor do tomador. |
| Unidade/perspectiva: Td, códigos e vínculos | Separar conglomerado e independente, financeiro/prudencial; evitar sobreposição | Td=I isoladamente não comprova independência. Identidade temporal depende125. |
| Controle: Tc e metadata societária | Contextualizar objetivo/modelo, inclusive controle estrangeiro | Controle corrente não retroage; controle estrangeiro não é exposição internacional nem domicílio exterior. |
| S1–S5: Sr/Segmentação | Regulação proporcional, complementar à escala econômica | Sr nulo2010–2016; entradas observadasS1–S3 em201706,S4 em201703,S5 em201812. Não imputar passado nem chamar simples quintis de tamanho. |
| Porte econômico: AT, crédito e funding | Concentração e relevância econômica; faixas a propor com sensibilidade | Recorte derivado, sem topN ou limiar adotado; S e porte econômico respondem perguntas diferentes. |
| CVM/B3 | Companhia, instrumentos, elegibilidade2024, eventos e setor quando comprovado | Não é nova fonte financeira; setor da holding não classifica toda atividade do grupo. Relação125 precisa aceite. |
| Geografia/situação/outras aberturas | Usar somente se explicarem pergunta com metadados adequados | Sede não é distribuição das operações. Cadastro ativo não equivale a elegibilidade acadêmica. |
| Tomadores, CNAE, atraso e outras aberturas SCR | Lacunas a investigar se essenciais | Não comprovadas no corpus admitido; oferta no portal não autoriza coleta nem certifica cobertura. |

Partir do agregado da amostra, mostrar distribuição das unidades e abrir segmentos quando ajudam a explicar movimentos. Não cruzar automaticamente todos os eixos: células pequenas podem revelar só uma unidade, sem sustentar generalização. As cinco dimensões são obrigatórias no quadro analítico, não cinco razões uniformes em toda atividade.

## Agregado, distribuição e saúde da base

O agregado econômico proposto é `ΣN/ΣD` sobre o **mesmo conjunto** com numerador, denominador, janela e perímetro válidos. Com `D_i>0`, equivale à média de `N_i/D_i` ponderada por `D_i/ΣD`. Isso é uma identidade algébrica, não regra para ponderar tudo por ativos. Média simples/mediana respondem pela unidade típica; distribuição mostra fragilidades que o agregado pode esconder. FMI draft §§7.5, 12.1–12.3 e12.22–12.26. PL ou receita negativos retiram a interpretação de pesos convexos; não os apagar para obter um gráfico conveniente.

Proposta para a futura fatiaC: para cada indicador/período e conjunto de indicadores, entregar denominador esperado de companhias e unidades distintas, calculáveis, não aplicáveis, ausentes, desconhecidas e inválidas; **nomes** e motivos, componentes faltantes, data de vínculo e participação econômica mensurável. Quando faltam os próprios ativos, declarar representatividade desconhecida e usar somente referência alternativa explícita, sem peso inventado. Não confundir cobertura por células com importância no agregado. Companhias grandes faltantes geram investigação antes de conclusão; não podem ser incluídas por imputação arbitrária.

Amostra fixa não elimina mudanças de disponibilidade/perímetro. Comparar, como sensibilidade proposta, série observada e subconjunto comum entre referências ajuda separar composição de mudança dos índices, mas não cria identificação causal. Não condicionar toda a análise à interseção de todas as métricas, pois isso pode apagar unidades por uma dimensão estruturalmente inaplicável. Recomenda-se cobertura por métrica e por dimensão, e uma comparação comum claramente identificada.

## Cobertura dos componentes na amostra: resultado da fatiaC

Handoff125 autenticado: manifesto `bf54640a70964ca8468cdefc1fc2aaf53d1aab8985779005de21fc9b847467eb`,221 arquivos e207 pins de entrada. A [lista e seus limites](fixed-financial-sample-2024-20261014.md) define24 companhias e20 unidades principais em2024, com vínculos adicionais separados. O número histórico de unidades varia; não projetar os20códigos atuais para todos os anos. PR126 integrou a documentação no merge531df618; dados locais aceitos e estadoGit/CI são evidências distintas.

A auditoria confrontou60 trimestres,1.440 combinações companhia/trimestre,1.236chaves financeiras nativas distintas e180 observações complementares anuais de dezembro (12 pares×15 anos). São38 componentes e25 fichas, além de quatro diagnósticos. Presença finita foi verificada sem escolher fórmula, sinal normalizado, estoque médio, trimestre derivado, TTM ou aplicabilidade. Os números seguintes são **cobertura documental dos componentes contemporâneos**, não quantidade de indicadores finais calculáveis.

| Candidatos / conjunto | Componentes conjuntos no bloco principal | O que permanece fora dessa contagem |
|---|---|---|
| R1–R6, Q1–Q2, C1–C2, L1–L4, E2/E3 e E2-A | 1.430/1.440 combinações companhia/trimestre | Médias/abertura, janelas novas, sinais, denominadores econômicos e atividade aplicável |
| Diagnóstico conjunto R1+R2+Q1+C1+L2+L3+E2 | 1.430/1.440 | Não é regra de exclusão da amostra ou conjunto adotado de fórmulas |
| C3: PR/RWA/IB publicado | 959/1.440;959/960 nas referências201503–202412 | 2010–2014 sem emenda; escala/regime/perímetro ainda próprios |
| C4: CP/RWA/índiceCP | 932/1.440;932/960desde201503 | 28 nulos contemporâneos; não presume motivo regulatório |
| Diagnóstico das cinco dimensões incluindo C3+C4 | 932/1.440 | Demonstra custo de exigir capital prudencial conjuntamente; não define painel de análise |
| Q3/Q4, C5, L5/L6, E1literal, E4 e E2-C | Componentes ou conciliações não comprovados | Não são “todas as companhias sem dado”; são definições/fontes ainda não operacionalizadas |

**Quais faltam:** BR Advisory Partners Participações, de201003a201203 (nove trimestres), sem operadora nativa presente no mapa; BRB Banco de Brasília, em202209, com saldo nativo nulo nos componentes contábeis auditados. A primeira situação não prova defeito de processamento: amostra fixa de2024 não exige existência operacional desde2010. A segunda permanece lacuna da fonte, sem imputação. Não houve descarte de companhia.

Para capital principal, os28 casos nulos são **DM Financeira**, em27 trimestres de201803a202409, e **BRB202209**. CP e índiceCP têm essa mesma falta; isso não autoriza preenchê-los com zero nem declarar automaticamente inaplicabilidade/regime simplificado. O restante da amostra não ganha, por essa contagem, certificado de comparabilidade ou escala. Relacionar eventual explicação regulatória às fontes e ao enquadramento temporal próprio antes de adotá-la.

Uma armadilha adicional foi conservada: Conta78196 aparece em dois contextos de Ativo, com grupos distintos, um nulo. As1.497ocorrências afetadas (1.431principais e66complementares) ficaram como contexto distinto não reconciliado mesmo quando os saldos coincidem. Essa rubrica não foi usada para completar candidatos da shortlist. Integridade de arquivo e igualdade de saldo não resolvem identidade de variável.

A dimensão societária principal também tem limites próprios: nas360verificações anuais,300usam identidade nativa do mesmo identificador,41têm caminho de controle explícito em documento anual,14não estabelecem o controle histórico do emissor e cinco registram participação sem controle certificado. Esses estados vêm da125e permanecem visíveis; documento anual não certifica intervalo contínuo. A presença de componentes em1.430combinações não transforma negócios selecionados em2024 em negócios comprovadamente controlados pelo mesmo emissor durante toda a janela.

### Relevância econômica e dados desconhecidos

Em202412, o universo financeiro nativo observado tem ativos conhecidos de **R$17.480.613.833.662,29**; as20 unidades principais têm **R$9.549.478.593.289,84**, reconciliados com125. Sete unidades do universo têm ativo nulo/desconhecido; em201003 são27. A participação frente ao total conhecido é informativa, mas não mede todoSFN consolidado ou representatividade estatística das abertas. Os somatórios conservam exposições entre grupos.

Em202209, o próprio ativo doBRB é desconhecido: não podemos atribuir peso zero à companhia nem estimar sua importância naquele período com dado inventado. Nas ausências iniciais daBRPartners, tampouco há valor contemporâneo certificado a imputar. A matriz conserva companhia, unidade, período, componente, estado e ativos conhecidos/desconhecidos. Falta de componente e falta de peso são diagnósticos separados.

### Complementos e segmentações

As180 observações complementares anuais ficam em bloco separado. Há109presenças de operadora;66 observações com o conjunto contábil de componentes e42com a interseção prudencial adicional. Não retroprojetar60 trimestres nem somar esse bloco aos principais sem tratar vínculo e sobreposição.

O estado documental tem84 observações sem controle estabelecido,30participações sem controle certificado e66caminhos de controle explícitos. **As66com componentes e as66com controle documental não são o mesmo conjunto: sua interseção é apenas14.** As outras52de cada grupo não pertencem ao outro. Não usar coincidência de contagens para inferir identidade, controle ou elegibilidade; disponibilidade financeira e evidência societária permanecem eixos separados.

Foram produzidas42.514 células diagnósticas por período/candidato/categoria nativaTcb,Td,Tc,Sr,Atividade eSegmentoTb, preservando nulos. Esses campos vêm do cadastro da **operadora** incorporado no mapa125; não são automaticamente a classificação da unidade financeira alvo. O contrato127 prevê consultar e preservar o cadastro do alvo separadamente, sem usar a operadora como fallback. São cobertura de recortes disponíveis, não estratos adotados nem teste de que toda combinação explica desempenho. O diagnóstico de estoque anterior usa o mesmo código nativo; não certifica continuidade de propriedade/perímetro ou estoque médio. A abertura200912 continua a conferir para o mapa da amostra.

Execução completa audit_c_v5/run5 e replay novo foram verificados independentemente, sem reexecutar somente o programa do autor. Dez de12outputs comparáveis são idênticos em bytes; todos12coincidem no multiconjunto semântico completo, incluindo proveniência. Duas listas vindas deSELECT sem ordem diferem apenas na ordenação. Tentativas anteriores falhas permanecem preservadas e não compõem o aceite. [Pins, fonte e limites da revisãoC](financial-dimensions-literature-20261014.provenance.md#coberturac-fontes-artefatos-e-revisão-independente).

## Comparação e estatística descritiva: o que acrescentar ao agregado

Assaf, cap.3, pp.47/50/53–55, liga a qualidade da conclusão à qualidade das informações, à atividade, ao negócio e ao modelo de contabilização. Distingue análise horizontal (evolução no tempo), vertical (composição relativa) e comparação entre empresas/segmentos. Isso fundamenta observar movimentos do agregado e abrir seus componentes quando ajudam a explicar, preservando mudanças de regime/perímetro. A decomposição contábil identifica mecanismos compatíveis com os números; não constitui identificação causal por si só.

Na seção14.10, pp.275–279, Assaf propõe padrões comparativos setoriais, apresenta a mediana e discute decis/quartis. A mediana representa o centro da distribuição das unidades; sozinha não informa sua dispersão. O próprio autor ressalva que liquidez alta ou endividamento baixo não recebem avaliação universal: podem coexistir com recursos ociosos ou menor retorno. Portanto, recomenda-se **mediana e Q1–Q3 como descrição da heterogeneidade**, ao lado do agregado econômico e da cobertura, sem herdar rótulos automáticos de “excelente” ou “insatisfatório”. O intervalo interquartil `Q3−Q1` é extensão descritiva proposta aqui, não fórmula atribuída literalmente à seção.

Exemplo puramente didático, sem dados de companhias, supondo mesmos período, definição e perímetro:

| Unidade fictícia | Ativo médio | Lucro | Lucro/ativo médio |
|---|---|---|---|
| A | 100 | 1 | 1% |
| B | 900 | 18 | 2% |

A razão das somas é `19/1.000 = 1,9%`; média simples e mediana dos dois retornos são1,5%. A primeira responde pelo conjunto dos ativos; as outras, pelas unidades com igual peso. Se B faltasse, o agregado observado seria1% cobrindo apenas10% dos ativos conhecidos, apesar de contar metade das unidades. Esse é o motivo de publicar **nomes, componentes e importância econômica dos faltantes**, além da quantidade. Com apenas duas unidades, quartis pouco acrescentariam; a segmentação deve respeitar o tamanho e a composição do grupo.

Os exemplos do livro não especificam um algoritmo geral único de interpolação/empates para todo tamanho de amostra. A implementação futura deve declarar a convenção de quantis; não apresentar o default de uma biblioteca como reprodução literal do Assaf. Não se propõem cortes de extremos, winsorização, inferência causal, teste de significância ou ranking pelo fato de descrever a distribuição.

Assaf, pp.55–56, também alerta para inflação e valores históricos. Nesta análise, valores contábeis nominais e crescimentos nominais devem ser identificados. Deflacionamento por índice geral e correção integral do balanço não são equivalências certificadas. Nenhum deflator, coleta de preços ou regra de correção foi adotado; uma razão contábil não recebe automaticamente interpretação de retorno real por ser adimensional.

## Seleção inicial e regra temporal aprovadas por João

Após as propostas e a cobertura revisadas, João escolheu em14/10/2026 **adotar o conjunto e explicitar as limitações**, e usar **trimestres efetivos/12meses com média ponderada pelo tempo**. [Registro da decisão naIssue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6174707162).

Conjunto inicial: **R1/R2 com lucro líquido; Q1/Q2 como proxies contábeis de crédito; C1 e C3/C4 em séries próprias; L2/L3 onde aplicáveis; E2-B**. São10medidas centrais nas cinco dimensões, sem score/ranking ou exclusão de companhias por métrica faltante. C2 é leitura recíproca deC1, não outro fator independente. Outras fichas e sensibilidades continuam propostas, não ampliam automaticamente a implementação.

Fluxos trimestrais serão reconstruídos a partir das janelas nativas documentadas. Sínteses de12meses usam fluxos disjuntos, não multiplicação porquatro. Estoques médios serão aproximados pelas observações trimestrais, incluindo abertura e ponderação do tempo entre datas; algoritmo/datas/pesos e limites da aproximação ficam no contrato de implementação. Essa escolha não reproduz a média mensal ajustada doBCB. Preservar ausências de abertura, quebras, sinais e denominadores não usuais.

A decisão de fórmula não homologa escala, equivalência ou aplicabilidade de todo binding. A tabela seguinte conserva recomendações e gates técnicos da pesquisa; as duas escolhas acima estão aprovadas, e os demais limites serão conferidos antes dos respectivos cálculos.

| Aspecto / estado | Recomendação e alternativas registradas | Gate técnico para cálculo final |
|---|---|---|
| Janela de rentabilidade e intensidade | **Aprovado:** trimestre efetivo e12meses nas sínteses, com fluxos disjuntos. Anualização×4 foi alternativa não escolhida e não será tratada como resultado anual. | Reusar native-semester-v1 nos três contextos fundamentados; contratar diferenças para trimestre/TTM e definir abertura/média. Trimestre de divulgação não significa lucro trimestral. |
| Estoque médio | **Aprovado:** observações trimestrais incluindo abertura, ponderadas pelo tempo entre datas. Média apenas de abertura/fechamento e saldo final permanecem alternativas não escolhidas para a série principal. | PL médio é adaptação adotada; algoritmo/datas/pesos devem ser explícitos. Eventos mudam perímetro; não inferir abertura de2010 nem ignorar sua ausência. |
| Eficiência E2 | E2-B de renda selecionada, com E2-A como sensibilidade e receitas excluídas visíveis. E2-C se reproduçãoBCB for necessária; E1 literal só após delimitar despesas operacionais. | Sinais/janelas/abrangência da provisão e composição por atividade; gross income FMI e IEO-BCB não foram homologados por coincidência de nome. |
| Alcance de crédito | Q1 com nome provisionamento; Q2 após conciliação; explicitar limitação e avaliar necessidade de atraso para a pergunta. | Q3/Q4 exigem fonte adequada; aquisição extra tem escopo próprio. Não declarar dimensão plenamente observada apenas com provisões. |
| Capital prudencial | C1 em série própria e C3/C4 desde oferta compatível, sem emendar. | Aplicabilidade e vínculo125; folga regulatóriaC5 não pronta. |
| Estatística agregada | Razão das somas e distribuição; segmentações quando explicam; nomes/cobertura sempre junto. | Tratamento de PL/receita não positivos deve preservar casos e esclarecer interpretação; não exclusão automática. |

A coberturaC reforça a viabilidade de iniciar as cinco dimensões com medidas contábeis e prudenciais específicas, preservando suas lacunas. Ela não justifica impor a mesma métrica a todo negócio ou excluir a DM/BRB pela falta deCP. Essas propostas não reabrem escolhas já aprovadas de amostra2024 e periodicidade trimestral/sínteses anuais. Refinam fórmulas, janelas por indicador e interpretação antes da implementação. O plano posterior precisa especificar registros de componentes, estados de cálculo, proveniência, testes de janela/sinal/duplicação e resultados reproduzíveis; software correto não substitui a conferência econômico-contábil.

## Limites bibliográficos e estado da entrega

Foram efetivamente lidas 48 páginas substantivas de Assaf, três estudos originais e trechos delimitados de guias/normas; não o livro inteiro. Cap.3(pp.46–56) e seção14.10(pp.275–279) complementam os trechos bancários. Restante do capítulo14, incluindo VEA/14.5, capítulo16 e final do18 não sustentam claims novos aqui. O exemplar tem inconsistências nos exemplos de capital de giro, unidade de leverage e expressão alternativa de VEA; o registro de proveniência explica os localizadores. Esta nota não reproduz esses exemplos como fórmulas de produção. Dividendos, Ke, repricing e restrições de liquidez não foram preenchidos por aproximações.

O FMI utilizado substantivamente é **Prepublication Draft 2019**, distribuído em curso CEMLA/FMI; acesso à edição final não foi obtido. Normas originais/compilações antigas e REF2025 não são cronologia regulatória completa. Os estudos tratam períodos e atividades diferentes: mecanismos e contraprovas são úteis, resultados e cortes não se transferem automaticamente. Fontes inacessíveis não receberam fórmulas ou conclusões atribuídas.

GateA/fontes aprovado nas quatro frentes e suplemento focal E2/Q2, com delta bancário conferido. A sínteseB recebeu revisão própria e correções documentadas; os snapshots, pareceres e estado da composição final ficam na Issue111. A fatiaC foi revisada e seus resultados delimitados estão acima; composição final/SHA/publicação têm autoridade naIssue111. A seleção inicial e a regra temporal estão aprovadas na decisão acima; esta nota não confirma implementação dos indicadores. O Goal permanece maior que a pesquisa: planejamento e implementação autorizada ainda precisam de entrega própria.

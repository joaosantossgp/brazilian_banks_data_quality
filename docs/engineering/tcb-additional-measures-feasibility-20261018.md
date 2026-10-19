# Demais medidas de Assaf e prudenciais: viabilidade finita — 18/10/2026

Pesquisa da [Issue188](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/188). Esta triagem completa os tópicos daFatia4do [plano178](../superpowers/plans/2026-10-18-tcb-indicators.md), usando criticamente143/178, o catálogo atual e auditorias nativas delimitadas. Não é pesquisa exaustiva nem adoção de indicadores novos. Os sete complementos já adotados nas189–191são outra entrega; nenhuma linha desta fila foi acrescentada silenciosamente à implementação192.

## Entradas, perspectiva e fontes

Pin corrente autenticado `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`. Catálogo autenticado `73d8e09c5662bbf8f2b4865802dfec376e8a3da3c358ca81aa3695e881171ffd`; query preservada de todos os contextos Financeiro/Capital iniciados antes2025, com períodos do núcleo examinados separadamente. Os valores vêm dos pacotes locais, sem coleta adicional. Unidade/versão/perímetro não são deduzidos só pelo nome ou ID.

Reuso bibliográfico explícito, sem alegar nova leitura do exemplar nesta fatia:

- Assaf Neto,*Estrutura e análise de balanços*,11.ed.,Atlas,2015, cap.18,pp.334–345/351–354, conforme páginas efetivamente lidas na [178](tcb-indicators-assaf-atlas-20261018.md) e [proveniência143](financial-indicators-activity-review-20261016.provenance.md). PDF=impressa+21. Fórmulas contraditórias dos exemplos não se tornam regras do projeto.
- FMI2019,guia final,§§5.90–5.95/7.29/7.34–7.42/7.67–7.69, referências178paraNPL/provisões. Não confundir a edição final com o draft empregado em111, cujo limite continua documentado na proveniência histórica.
- BCBS,[LCR2013](https://www.bis.org/publications/201301-standards-basel-iii-liquidity-coverage-ratio-and-liquidity-risk-monitoring-tools.pdf),§§17/19–22, e[NSFR2014](https://www.bis.org/publications/201410-standards-basel-iii-net-stable-funding-ratio.pdf),§§9/12–17, leitura111 reaproveitada. São padrões regulatórios, não prova de que todas as unidades observadas tenham obrigação idêntica.
- [Cronologia normativa139](ifdata-c4-regime-sources-20261016.md), com originais/compilações e artigos/páginas:4.553/2017,art.2§§5–6;4.606/2017,arts.2–3/7–16/35–37;4.721/2019,arts.26–27;4.955/2021,arts.1–4;4.958/2021,arts.1/3–7/15;5.049/2022,arts.3–7/9. Leitura documental anterior reaproveitada, não reconstrução de todas as alterações nesta188. Mudanças com eficácia2025continuam fora do núcleo.

## Capital: componentes adicionais existem, mas não fecham uma folga universal

O conjuntoCapital é relatório5,**TipoInstituicao1daAPI**, e tem janela própria201503–202412. Tipos1/2/3de conglomerado regulatório são outra classificação. O primeiro piloto usou um filtro deTipo3incorreto e gerou todos os componentes ausentes: foi explicitamente invalidado e preservado. A correção foi conferida contra o catálogo, com guarda de seleção nativa não vazia e revisão independente antes da expansão. Ausência produzida por consulta incorreta não é evidência sobre a base.

| ContaCapital5 | Conceito no catálogo | Janela observada no núcleo e limite |
|---|---|---|
|79645/79647/79649|Capital Principal/NívelI/PR|40referências; componentes distintos, sem preencherCPcomPR.|
|79658|Exposição total sem ponderação de risco|40referências catalogadas, com importantes null; não substituir porATFinanceiro.|
|79665|RWA|40referências; descrição/parcelas/contextos variam, inclusive serviços de pagamento.|
|92999|Adicional de Capital Principal: conservação+contracíclico+sistêmico, referênciaDLO940|**8referências202303–202412**; existe, portanto não cabe dizer que todos os adicionais estão ausentes. Não identifica sozinho mínimo/regime integral nem autoriza subtrair um valor monetário de uma taxa.|
|98576|IRRBB,capital para risco de taxa de juros da carteira bancária,referênciaCircular3.876/2018|**1referência202412** no núcleo; não é grade de reprecificação ou série histórica pronta de GAP.|

Os contextos completos de79658/79665têm intervalos sobrepostos no catálogo; a conferência nativa não encontrou duas ocorrências da mesma unidade/data/relatório/conta nas sete contas. Cada contexto observado foi preservado. Não se harmoniza a evolução do RWA por similaridade de nome.

AuditoriaCapital:55.124unidades-trimestre,40referências,925células data×Tcb×SegmentoTb×coorte,385.868componentes examinados. Não se fabricam as20referências2010–2014. Informação financeira antiga dePR/IBemResumo1, documentada na113, permanece outra perspectiva e não é emendada. A disponibilidade conjunta dos sete componentes é444em202412; antes de202412ela é zero por ausência deIRRBB, o que não significa ausência de capital ou impossível cálculo deC3/C4.

| Data | Unidades próprias |PR/RWA: ambos finitos|CP/RWA: ambos finitos|PR/RWA/ACP: três finitos|NívelI/exposição: ambos finitos|
|---|---:|---:|---:|---:|---:|
|201503|1.557|1.548|1.548|0|0|
|202303|1.351|1.261|428|1.261|428|
|202412|1.367|1.358|444|1.358|444|

Em202412,ACPtem444positivos,914zeros e9null;IRRBBtem341positivos,1.017zeros e9null. PRtem15negativos preservados. Esses estados não identificam automaticamente opção regulatória ou suficiência. O nominal e a matriz adicional porSroriginal conservam companhias/coortes e disponibilidade por conjunto; somas exatas deRWApróprio conhecido e correspondente a cada conjunto mensuram representação, sem pesos deATFinanceiro. S5não é faixa de tamanho nem prova individual de opçãoPRS5; o [diagnóstico139](ifdata-c4-prudential-gaps-20261016.md) permanece a evidência sobre os nulos, sem reiniciar a investigaçãoBRB.

## Fila finita de decisões e fontes

Classes: **A**, componente/conceito local calculável após adoção e contrato; **B**, adaptação/ajuste delimitado a conciliar; **C**, fonte ou método adicional; **D**, leitura redundante ou medida inadequada ao uso proposto. Nenhuma classe certifica comparabilidade econômica de todos os Tcb.

| Pergunta e candidato | Fonte/localizador e alcance | Encontrado/faltante | Classe e próxima fatia mínima |
|---|---|---|---|
|Crédito problemático/NPL: NPL/carteira bruta compatível|FMI2019,§§5.90–5.95/7.29/7.34–42; unidades com exposição própria de crédito|78191crédito antes da provisão e78192provisão existem; não há exposição NPL por atraso/default correspondente nos relatórios agregados examinados. Provisão ou rating não é NPL.|C: fonte datada deNPL,critério e carteira da mesma unidade/regime; uma data/um perímetro antes da série.|
|Cobertura específica deNPL|FMI2019,§§7.34–42/7.67–69; mesmo alcance deNPL|FaltamNPL e distinção da provisão pertinente àquela exposição. Q1eQLnão preenchem esse denominador.|C: parear provisão específica eNPL;NPLzero continua indefinido, sem imputar cobertura infinita.|
|Folga dePR/CP/NívelI em relação ao requerimento aplicável|Normas139citadas; perspectiva prudencial, regime/datados|C3/C4 e92999ACPparcial disponíveis; não há série completa de mínimo+adicionais/regras individuais para todo2010–2024. Regime simplificado exige identificação e componentes próprios.|B/C: uma unidade/data com regime provado, mínimo eACP conciliados em mesma unidade/escala; só depois diferença em pontos percentuais ou moeda coerente. Não impor8/11/13%uniformes.|
|Alavancagem prudencialNívelI/exposição total|Capital5/79647/79658; descrições citamCircular3.748/2015; razão publicada79661também catalogada|Componentes locais e escala/denominador precisam de contrato próprio, com null abundante; não usarATcontábil ou capital total.|B: conciliar razão publicada e componentes em uma data/regime, depois adoção explícita. Não é o inverso deC1.|
|LCR: ativos líquidos elegíveis/saídas líquidas estressadas30dias|BCBS2013,§§17/19–22; somente perímetro/regime pertinentes|Caixa/AIL/TVM existem; faltam elegibilidade, vínculos, haircuts, fluxos e estresse pareados.|C: fonte específica deHQLA/saídas e regra vigente. L2não é LCR; não obrigação regulatória não prova irrelevância econômica da liquidez.|
|NSFR: financiamento estável disponível/requerido|BCBS2014,§§9/12–17,horizonte anual|LFe demais saldos não oferecem maturidades/ponderações deASF/RSF.|C: pares de componentes e ponderações datadas; crédito/depósitos não substituiNSFR.|
|GAP de juros/reprecificação|Assafpp.343–345; ativos/passivos sensíveis da própria unidade|98576IRRBBdesde202412não informa buckets. [Pesquisa185](tcb-funding-maturity-feasibility-20261018.md) separa vencimento de caixa de reprecificação.|C: agenda de revisão de taxas e base sensível, uma unidade/data/horizonte. Não classificar todaTVM/crédito como sensível por suposição.|
|Imobilização: permanente/PL; capital de giroPL−ANC|Assafpp.335/337; Financeiro contábil, estoques|78201permanente ajustado=`[20000004]-[23000001]`;78186PL. Não éANCcertificado nem necessariamente permanente integral do livro.|B: possível adaptação “permanente ajustado/PL” após conciliar a exclusão de imobilizado leasing;CparaANCsem abertura. PLzero indefinido,PLnegativo muda leitura; não adotar nesta188.|
|Custo da captação: despesa de captação/base correspondente|Assafp.342,DCAP/depósitos a prazo no exemplo|DRE4/78209=`[81100008]+[81980008]+[81986002]+[81912007]`;Passivo3/78286=`[41500002]`. Despesa abrange captação de mercado mais ampla que415.|B/C: mapear despesa às fontes correspondentes e janela/média; não dividir por depósitos a prazo só porque ambos existem.|
|Juros passivos: DIF/exigível compatível|Assafp.342 e exemplo352; Financeiro|78214DIF e78298=`[40000008]`exigível existem.78300incluiPL e,antes202212,REF; não é denominador equivalente.|B: definir se a pergunta inclui todas as despesas de intermediação, seu passivo remunerado/exigível e estoque/média. Não transplantarPL ouREFpor nome.|
|Leverage contábilAT/PL|Assafp.337,vezes|Recíproco deC1onde definido;C1=0/ATouPLzeroexigem tratamentos próprios.|Dcomo fator independente: pode ser apresentação derivada explicitamente, sem somá-lo aC1como nova informação de capital.|
|Benefício ao cooperado, adicionalidade/mandato e volume de serviços|PanoramaSNCC2024p.22/nota10;Ferraz/Além/Madeira2013pp.30–31/35–37, reuso178; negóciosB3/B4/fomento/N2/N4conforme pergunta|Balanço/renda não contêm preços comparáveis ao cooperado, contrafactual/adicionalidade, produtos, transações ouTPV compatível.|C: definir produto, objetivo, unidade e benchmark; obter medida própria. Não inferir fracasso de mandato deROEbaixo nem eficiência técnica deE2.|
|Retenção/TRL e limite de expansão|Assafpp.338–339; capital/dividendos próprios|LL/PLexistem, faltam dividendos e ajustes de base especificados no livro.|C: dividendos e base temporal;DIVnão observado não éDIVzero. Não usarROE/C1para imputar retenção.|
|VEA=LL−Ke×PL eMVA=VEA/Ke no exemplo|Assafpp.351–354; moeda e hipóteses de avaliação|LL/PLcontábeis não fornecemKe. P.352tem expressão invertida;353confirma(RSPL−Ke)×PL. MVAé simplificação do exemplo, não valor de mercado observado.|C: métodoKe/risco/horizonte/base e adoção;Kezeroinvalida capitalização. Não calcular com uma taxa arbitrária para completar tabela.|

## Auditoria financeira e limites de implementação

As seis contas financeirasPERM78201/PL78186/depósitos a prazo78286/despesa de captação78209/exigível78298/DIF78214foram inventariadas no sistema inteiro:89.476unidades-trimestre,60referências,3.709células. Nominal e matriz conservam contexto/estado/valor nativo, nomes/companhias/coortes eAT/crédito/PL conhecidos/desconhecidos com somas exatas. As78linhas sem código são preservadas à parte. Esta é disponibilidade contemporânea dos componentes: aDREnativa não foi convertida em fluxo trimestral nem dividida por um estoque. A presença conjunta não homologa nenhuma fórmula candidata.

Novas métricas dessas linhas exigem adoção própria depois da conciliação indicada, reusando o motor seletivo existente. A prioridade é completar componentes/regimes de medidas economicamente úteis; não aumentar quantidade de métricas redundantes ou fabricar indicadores para obter cobertura universal. Lacunas de fonte e de método ficam separadas de ausência estrutural, nulo, zero ou não aplicabilidade econômica.

Root, branch `codex/tcb-research-182-188`, base7bfeed2; única nota pública e `.scratch/tcb-viabilidade-demais-medidas/`. Sem mudança de arquitetura/core/dados aceitos/ponteiro/explorador. Pilotos corrigidos e revistos antes das expansões:Capital40referências,recibo5,672s;Financeiro60,recibo12,828s. Primeira tentativa inválida e comandos/hashes foram preservados. Revisão independente integral dos inventários, pares, fontes e nota/SHA acompanha a Issue. O aceite desta pesquisa é a fila finita de viabilidade e próximos recortes, não os indicadores adicionais implementados.

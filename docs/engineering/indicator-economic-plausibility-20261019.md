# Plausibilidade econômica dos níveis dos indicadores

[Pesquisa198](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/198), 19/10/2026. Universo observado completo, 201003–202412, 27 métricas e suas janelas/perspectivas próprias. Entrada aceita: manifest `f374150e5d4c515f032fdf3fad3cb27b4e196486cee8d81c19150c39df45981b`. Não houve recálculo de indicadores, correção de fontes, exclusão, truncamento ou imputação. [Plano para começar a análise](analysis-start-20261019.md).

## Conclusão econômica

**Há níveis extremos que impedem interpretar automaticamente rankings institucionais como desempenho. Não se demonstrou nesta auditoria um erro geral de escala percentual ou uma fórmula incorreta.** A divisão reproduz os componentes persistidos nos casos rastreados, mas alguns tokens nativos são economicamente suspeitos e não foram certificados por demonstração alternativa. Aritmética correta não certifica conteúdo econômico nem fidelidade do reporte original.

O agregado do sistema é muito menos sensível aos máximos institucionais rastreados do que esses níveis sugerem. Isso não libera toda categoria/coorte: concentração, cobertura e composição continuam próprias. Em particular, QL tem concentração material documentada na #192. A seleção do maior valor individual não identifica necessariamente a unidade de maior influência agregada; por isso se reutilizam também os diagnósticos A/B completos.

## Instrumento e alcance

Varredura determinística de 6.005.286 linhas unitárias, 15.600 agregadas e 719.860 segmentadas. Valores disponíveis foram examinados por métrica, janela, perspectiva, coorte e categoria, sem misturar unidades com agregados. Foram retidos 13.046 contextos com valores: 2.894 unitários,252 agregados,9.900 segmentados. Contagens de valores presentes:5.090.969,13.786,412.367 respectivamente. São ocorrências repetidas entre períodos/indicadores, não instituições distintas ou observações independentes. O inventário não equivale a todos esses resultados serem elegíveis.

Triagem operacional em **razões**, antes da apresentação×100: R1 acima de20%TTM/5%trimestre; R2 acima de100%TTM/25%trimestre; L1/L2/L3/PL_DEP acima de10vezes; C3/C4/R3/RS/E2 acima de2vezes; demais acima de1vez, ou0,25no trimestre. Usou-se módulo, preservando sinais. Esses limiares só organizam a investigação; não são limites teóricos, regulatórios, estatísticos ou decisões de exclusão. Houve124.942 ocorrências unitárias acima da triagem e11.349 com denominador negativo; nos agregados,314e8; nos segmentos,10.869e525. Comparar essas frequências entre métricas não mede qualidade dos dados.

O piloto inicial agrupava recortes inadequadamente e foi rejeitado. O piloto2 separou coortes e categorias e teve conferência independente integral de4.307contextos/14.991extremos. A primeira execução integral concluiu as6.005.286linhas unitárias e salvou2.894resumos, mas falhou por memória ao iniciar agregados. A retomada `full2` preservou esses resumos integralmente, conferidos pelo revisor, e percorreu as duas tabelas restantes em79,44s, com conexões separadas e2GB. A execução original permanece globalmente falha.

A identidade exata valor=N/D não apresentou divergências **nas duas tabelas retomadas**. A lista de divergências unitárias não foi persistida antes da falha; portanto não se declara PASS dessa identidade para todas as linhas unitárias nesta auditoria. A composição já aceita e suas revisões de cálculo continuam evidências separadas. O checkpoint unitário preserva níveis/sinais/min/max, não top4 ou contagens por status/período. Foram rastreados26casos de13medidas aos resultados e componentes atômicos autenticados, com fontes, tokens, períodos e definições. Isso é investigação dirigida de extremos, não certificação de cada token da população.

## Casos que mudam a interpretação

Valores monetários abaixo estão emR$; percentuais são arredondados apenas nesta apresentação. Identificação refere-se à unidade reportante na perspectiva indicada, sem inferência por nome.

| Indicador e caso | Nível observado | Componentes e diagnóstico | Uso na análise |
|---|---:|---|---|
| ROA/TTM, Solidez96477906,202309 |18.908,17%| LLTTM R$251.274.325,31 e ATmédio R$1.328.919,33. O LL nativo de202212 é R$173.679.659,86, enquanto os estoques de AT rastreados são próximos deR$1,33milhão. Há tensão econômica real na fonte; não se demonstrou erro do motor. | **Inconclusivo quanto ao reporte econômico.** Não chamar retorno extraordinário confirmado. Manter sinalização, componentes e análise de influência. |
| ROA/TTM, mesma unidade,202312 |−2.119,07%| LLTTM −R$28.172.737,38; ATmédio R$1.329.485,16. Reversão e escala dos fluxos merecem conferência da demonstração; não corrigir pelo valor parecer alto. | Mesmo tratamento; nenhuma winsorização automática. |
| ROE/TTM, Frente71677850,201909 |2.620.657,19%| Prejuízo −R$6.472.381,39 / PLmédio aproximadamente−R$246,98. Dois sinais negativos e denominador próximo de zero produzem razão positiva enorme. | Não interpretar como rentabilidade superior; separar leitura de PLnegativo sem retirar silenciosamente a unidade. |
| E2-B/TTM, SicoobPlanalto00692214,202206 |≈−5,42×10¹⁸%| Custos R$16.253.994,98 / renda selecionada−R$0,0000000003. Cancelamento de rubricas com resíduos decimais nativos, preservados exatamente. | Razão sem leitura usual de eficiência naquele caso; não arredondar o denominador para zero nem usar rank. |
| E2-B e E2-W/TTM, Solidez96477906,202109 |12.171.781.300%| Custos R$1.217.178,13 / renda R$0,01. | Explosão de razão por cancelamento; consultar renda/custos e cobertura, não concluir colapso de eficiência nessa magnitude. |
| Q1, Credrio05170343,201206 |568,02%| Provisão−R$33.219,58 / crédito antes da provisão R$5.848,31; crédito líquido−R$27.371,27. | **Suspeita econômica na composição/reporte**, não inadimplência568%. Não normalizar artificialmente a100%. |
| QL, CCB C0032119,201903 |22.791.926,17%| ProvisãoR$9.545.258,68 / recebíveis antes da provisão≈R$41,88. Em202306 os recebíveis são−R$7,84 e a aplicabilidade fica desconhecida, fora do agregado elegível. | Denominador residual e inconsistência econômica merecem investigação. Preservar a regra existente de elegibilidade; valor calculado não prova aplicação adequada. |
| C1, Cooperasa05296712,202112 |−244.646.400%| PL−R$24.464,64 / AT R$0,01. Outro caso em201009 tem AT negativo, produzindo C1positivo acima de100%. | Inconclusivo para reporte; não interpretar como capitalização econômica ordinária. |
| L1/L2, BancoFord90731688,201912 |≈9,33×10¹⁰% /3,73×10¹¹%| Depósitos à vista R$0,03; caixaR$27.980.395,66 e caixa+AILR$111.758.105,90. | Denominador imaterial ao modelo. Não usar como prova de liquidez extraordinária ou LCR; abrir fontes e prazos. |
| C3, FincapitalC0085403,202012 |1.606.973,17%| PRR$1.036.819,09 / RWA R$64,52. | Baixo RWA explica a razão; avaliar atividade e regime, sem classificá-la como erro pelo nível. |
| C4, MonteBravoC0087281,202403 |396.904,44%| CPR$153.501.760,77 / RWA R$38.674,74. | Razão regulatória com denominador pequeno; não comparar como retorno. |

Os demais extremos rastreados incluem R3/TTM com RIFR$0,29(Stark,202203) ouR$10,54(BoltCard,202106), RIF_AT de1.967,19%(CapitalConsig,202412), E2-W negativo e capital prudencial negativo. Fluxo elevado sobre estoque pequeno ou RIF pouco representativa não é erro demonstrado; requer conferir modelo e componentes. Capital negativo é fragilidade contábil/regulatória do valor reportado, não desempenho positivo por convenção de sinais.

## Materialidade agregada e decisões propostas

As retiradas abaixo são uma por vez, preservando as demais contribuições elegíveis. São sensibilidades determinísticas, não proposta de excluir unidades, teste causal ou intervalo de confiança.

| Caso | Agregado original do sistema | Mudança ao retirar o caso, p.p. |
|---|---:|---:|
| Solidez,ROA/TTM202309 |1,35406%|−0,001812|
| Solidez,ROA/TTM202312 |1,38528%|+0,000197|
| Frente,ROE/TTM201909 |16,93432%|+0,000761|
| SicoobPlanalto,E2-B/TTM202206 |45,59539%|−0,002446|
| BancoFord,L2ponto201912 |395,29278%|−0,034046|
| CCB,QLponto201903 |9,44798%|−0,127381|

Isso não demonstra baixa influência em N1/N2, nos estratos menores ou em todas as datas. Os [diagnósticos A/B anteriores](statistical-diagnostics-ab-20261018.md) cobrem os20indicadores; os [A/B da192](tcb-indicators-delivery-20261018.md#sensibilidade-e-interpretação-dos-resultados) cobrem ossete novos e incluem3.927.994retiradas. Em202412, QL tem variação de50,8286p.p.pela maior retirada; precisa acompanhar qualquer conclusão sobre o agregado dessa medida.

Proposta de apresentação: níveis e sinais preservados; mediana/dispersão ao lado da razão agregada; denominadores, cobertura e influência disponíveis; flags econômicas para casos rastreados inconclusivos; indicadores condicionais por Tcb e SegmentoTb. Não aplicar teto universal, arredondar tokens residuais, confundir provisão com inadimplência ou liberar ranking de ROE com PLnegativo. O [plano de análise](analysis-start-20261019.md) separa os calendários e janelas de cobertura fraca. Investigações adicionais de demonstrações específicas podem ser feitas se forem materiais à conclusão acadêmica, sem bloquear toda análise do sistema.

## Proveniência e reprodução

Evidência privada no checkout principal: `data/curated/indicator-economic-audit-20261019-pilot`, `pilot2`, `full` e `full2`; conservar tentativas, não escolher a mais recente como se substituísse todos os estados. `full2/receipt.json` autentica as tabelas retomadas e o checkpoint unitário; `case-traces.json` autentica os pacotes de componentes/resultados e retém26casos completos. Checkpoint unitário SHA-256 `717a6157f73e428988ddc0768a6bf295bbdb68109b95e6865fdadfe5c49d1349`. Instrumentos finitos em `.scratch/economic-analysis-ready/audit_levels.py` e `trace_cases.py` no worktree da198. Uma cópia desses instrumentos e recibo consolidado acompanha a evidência privada, sem dados pessoais/saldos noGit.

Esta etapa aplica os conceitos e fórmulas já adotados; não realizou nova leitura do Assaf nem nova coleta. Referências conceituais/páginas e contextos IF.data permanecem nos [pilotos189–191 e matriz192](tcb-indicators-delivery-20261018.md), no [protocolo173](statistical-treatment-protocol-20261018.md) e nos resultados atômicos autenticados. Revisão independente de economic_review_198 aprovou o gateA/B após conferir contagens, hashes, todos26casosN/D e os deltas publicados, além do comando de descoberta e sete arquivos dohandoff. Estado de publicação/integração é registrado no mesmo contrato198; não há aceite acadêmico final por inferência.

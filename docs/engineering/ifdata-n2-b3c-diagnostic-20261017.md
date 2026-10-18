# N2/Terra e E2-B/B3C — diagnóstico da janela completa

Diagnóstico complementar autorizado na [Issue152](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/152#issuecomment-6244042674). **Não publicada — tarefa local**, separada do [PR153](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/153), que entrega o pacote anterior. Não houve recálculo global, alteração de valores aceitos, mudança de fórmula, substituição de sinal ou emenda de perspectivas.

## Entradas e verificações

Pacote composto aceito: SHA-256 `25f72484df934ffefdead578015558a77dcaaf191da4a52f7d400c6a4a485d1b`. Financeiro nativo convertido: `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095`. Cadastro/perfil e pacotes aceitos somente leitura. Mapa N2 cobre60 trimestres201003–202412; B3C cobre todas as unidades e janelas disponíveis no mesmo intervalo.

Diagnóstico privado reproduzível: `.scratch/152-n2-b3c-diagnose.py` e `.scratch/152-n2-b3c-verify.py`; saídasJSON/CSV adjacentes. A primeira consulta com512MiB falhou porOOM antes de produzir aceite; nova execução com um thread e1GiB, após conferir memória da máquina, passou. Não houve reinício de produtor ou alteração de entrada. Todos os Parquets financeiros2010–2024 foram autenticados. O oráculo independente usou tokens nativos, contextos completos e frações para reconstruir apenas as janelasE2-B/B3C necessárias à conferência; não chamou o avaliador do motor nem persistiu substituições de indicadores.

## N2: cobertura baixa é concentrada e varia por período

ROA/ROE12meses compartilham a necessidade de lucro e estoque médio. A cobertura por ativos conhecidos de N2 não é uniformemente alta:

| Dezembro | Cobertura ROA porAT conhecido | Principal unidade excluída identificada | Estado observado |
|---|---:|---|---|
| 2016 | 48,09% | XP INVESTIMENTOS/C0051994, ATaprox.R$4,82bi | Lucro nativo null em dependências201512–201609; corrente201612 existe |
| 2018 | 27,63% | XP INVESTIMENTOS/02332886, ATaprox.R$14,01bi | Lucro dos quatro trimestres2018 existe; aberturaAT/PL201712 ausente sob esse código |
| 2022 | 45,61% | WARREN/C0052333, ATaprox.R$8,48bi | Código aparece com fluxos em202209/12; faltam dependências anteriores do conglomerado |
| 2024 | 58,71% | TERRA/03751794, AT R$8.558.633.311,49 | Fonte Financeiro anterior ausente; corrente202412 existe |

Esses estados explicam ausência no pacote, não autorizam chamar a informação de inexistente em toda fonte nem fazer de-para por nome. Os episódiosXP/Warren são candidatos distintos de transição/perímetro e precisam de prova própria. O CSV privado guarda todas as60 referências e frações de cobertura, não apenas os dezembros acima. Os três primeiros trimestres2010 ainda são aquecimento estrutural deTTM.

## Terra: toda a janela afetada

Identidade técnica03751794, início de atividade cadastral201504. Na visão Financeiro há observações201506–201906 e novamente202412:18 referências no núcleo. Os21 trimestres201909–202409 não contêm o código na fonte brutaTipo2 aceita. Essa ausência foi conferida em cadaJSONgzip, comSHA-256 contra o manifest de conversão; não foi criada peloParquet ou pelo cálculo.

Na visão Individual, o mesmo código tem dados em toda essa janela. Nos18 períodos em que ambas as perspectivas existem, **1.332 linhas de relatórios1–4 coincidem exatamente** em data, relatório, grupo, conta, nome, descrição e tokenSaldo. TipoInstituicao e proveniência são conservados e não foram declarados iguais.

Isso é forte evidência para investigar uma ponte da mesma instituição, mas não prova automaticamente equivalência nos períodos sem reporteFinanceiro. Cadastro individual202409 registraTdI, sem conglomerado financeiro e com conglomerado prudencialC0084514; ser membro prudencial não equivale a perímetroFinanceiro consolidado. No diagnóstico original, nenhuma linha Individual havia sido transplantada; a adoção e a execução finita posteriores estão registradas abaixo.

Efeitos observados:

- Em201506 os fluxos trimestrais exigem201503, anterior ao primeiro reporte. Isso afetaTTM201506–201603; o primeiroTTM disponível na série observada é201606. Não substituir abertura ou fluxo inicial por zero sem regra/evidência.
- Em202412, AT/PL/LL e DRE correntes existem; o problema é história financeira anterior para janelas e médias. ROA/ROE/E2-B/E3/R4/RS ficam sem trimestre eTTM nessa referência; estoquesC1/LA/LC estão disponíveis. Indicadores de crédito/depósitos têm causas adicionais de zero denominador e não são resolvidos universalmente pela ponte.
- Recuperar somente a contribuição daTerra emROA202412 elevaria, **hipoteticamente**, a cobertura por ativos conhecidos deN2 de58,71% para96,94%, mantendo a mesma população e os demais casos sem mudança. É cenário de cobertura, não indicador recalculado nem promessa de resultado.

**Correção candidata prioritária:** uma ponte explícita e finita de dependênciasIndividual→Financeiro para a unidadeTerra já observada em202412, com identidade/perímetro datados, igualdade nas sobreposições, flags e proveniência. Exige liberar a regra entre perspectivas; não deve inserir silenciosamente unidades financeiras em201909–202409, preencher outros códigos ou misturar conglomerados. A adoção é decisão metodológica adicional, não conserto automático de parsing.

## B3C: o negativo é histórico e vem dos componentes nativos

O agregadoE2-B é negativo em **todos os57TTM disponíveis**, de201012 a202412. No trimestre efetivo, é negativo em56de60 referências; as exceções não negativas são201012,201203,201403 e201603. Portanto não é um acidente isolado de2024.

Foram conferidas4.213 contribuiçõesB3C/E2-B calculáveis contra as seis contasDRE nativas, com reconstrução independente de trimestres eTTM e comparação exata de numerador, denominador e razão. Todas coincidem. Há771janelas unitárias com custo líquido negativo e245com denominador negativo. Outras contribuições preservam10zero_denominator,117insufficient_history,13binding_missing e25native_null. Esses estados não foram convertidos emzero.

A fórmula adotada é `−(78218+78219)/(78215−78213+78216+78217)`. A descrição nativa da conta78219 inclui positivamente **71930006** além das contas de despesa. Essa rubrica não é despesa administrativa bruta: incorpora recuperação de encargos/despesas. O nome abreviado do indicador e a flag `signed_cost_reversal` não demonstram que houve uma reversão contábil extraordinária.

Exemplo nativo de202412, Central Sicredi Centro Norte/33667205, semestre de referência: pessoal−R$17.455.905,33; administração+R$154.652.653,48. O numerador líquido invertido fica negativo. O sinal positivo de administração já está na fonte, não foi introduzido pela subtração de trimestres. As cinco centraisSicredi33667205,33737818,70119680,80230774,87437687 estão entre os maiores contribuintes negativos em2024.

Uma fonte primária contextualiza o mecanismo: as [DF2024/1 da Central Sicredi Brasil Central](https://www.sicredi.com.br/media/produtos/filer_public/2024/08/29/central_sicredi_brasil_central.pdf), p.8 e notas18–19,p.17, apresentam despesas administrativas e recuperação de encargos/despesas separadamente, com recuperação relevante e operações com filiadas/partes relacionadas. A extração textual foi consultada; a tentativa de screenshot pela ferramenta falhou porcachemiss. Não se afirma conciliação exataDF×IF.data, pois diferenças de apresentação, atualização e arredondamento não foram reconciliadas. A prova do sinal do indicador usa os tokensIF.data, não valores copiados doPDF.

## O que corrigir e o que não corrigir

1. **Não há erro aritmético demonstrado emB3C.** Não aplicarabs, inverter sinais porTcb, zerar, truncar ou excluir negativos para produzir uma taxa de eficiência convencional.
2. **A interpretação deve ser corrigida.** B3C/E2-B mede custo líquido de certas recuperações sobre renda selecionada; valor negativo não é eficiência superior. A flag atual é um sinal numérico, não diagnóstico de evento contábil. Essa ressalva vale para toda a janela, não só2024, e também alertaE3, que usa o mesmo numerador; E3 não foi revalidado integralmente nesta fatia.
3. **Um indicador específico/bruto requer componentes adicionais e decisão.** Separar despesa bruta, recuperações e rateios/centralização seria mais informativo. A conta agregada78219 não permite decompor isoladamente71930006. Usar DF publicada ou aberturaCosif seria outro contrato, sem coleta/ampliação implícita.
4. **Terra é o candidato de maior ganho imediato em2024**, mas a recuperação por ponte não é mudança técnica neutra de perspectiva. Manter o financeiro literal e eventual versão com ponte identificados. XP/Warren pedem provas próprias; não generalizar a regra daCaixa ou daTerra.

Não foi demonstrada falha do motor que justifique reprocessar a base. O diagnóstico fundamentou a proposta finita adotada abaixo. O PR153 não recebe a nova regra ou este diagnóstico; a entrega é separada.


## Adoção e execução seletiva da Terra — Issue 154

João aprovou explicitamente a ponte finita, com originais e ressalvas preservados; [decisão registrada na Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6244309849). A regra `terra-individual-history-financial-202412-v1` atende somente Financeiro/03751794/202412. Dependências anteriores consumidas vêm de Individual/202312–202409; o corrente 202412 permanece Financeiro. Não há inserção dos 21 períodos de ausência da unidade na fonte Financeiro nem extensão a XP/Warren.

O CLI `analyze-ifdata.py recalculate-terra` usa a composição aceita como comparação obrigatória, o perfil instalado, tokens e bindings nativos, cadastro nas cinco datas, e as mesmas fórmulas/janelas existentes. Recusa grupo financeiro, identidade divergente, contexto incompatível, valor nativo ausente ou histórico Financeiro já existente. Saída em pacote novo, sem sobrescrever entradas: 16 originais, 16 contribuições corrigidas e observações/proveniência completas. O original dos valores continua acessível na composição anterior e em `original_unit_coverage` do patch.

Execução real: **2,414 segundos**, 16 contribuições, 12 `ok`; Q2 e R5, trimestre/TTM, permanecem `zero_denominator`. O ROA TTM da Terra é **0,024274469246%** e o ROE TTM **8,361017721273%**. Revisão independente dos tokens nativos, diferenças semestrais e médias ponderadas pelo tempo confirmou exatamente numeradores, denominadores e razões. Foram preservados cadastro, vínculo, classificações, estoques de representação e os 16 originais; 36 observações históricas têm ponte explícita. Nenhuma referência corrente usa Individual.

O pacote de patch tem SHA-256 de manifest `5c6562ab3a368386b77fdcd5134040146e9d0210c8335e2d11148da7e3096cb0`. A revisão econômica não chamou o motor. O cálculo seletivo não certifica perímetro econômico constante nem resolve os episódios anteriores de N2. Dados/recibos privados ficam fora do Git. A recomposição do explorador tem aceite separado de preservação e de cobertura.

## Recomposição seletiva conferida

A atualização armazenada usa `analyze-ifdata.py apply-terra`: autentica composição e patch, exige igualdade com os 16 originais, preserva classificações/vínculos/estoques e reduz apenas os 16 contextos Financeiro/202412. Nenhuma fórmula é avaliada nessa etapa. As contribuições corrigidas apontam ao patch e guardam a origem anterior; seus digests correspondem aos novos campos econômicos.

A segunda tentativa concluiu em **75,293 segundos**, com manifest `ce57545b643d9efcfbb09ee26234c97f131080627d42622c2b4cfbf998f7c524`. A primeira tentativa falhou na associação posicional de parâmetros do COPY/DuckDB; foi preservada como falha, corrigida por parâmetros nomeados e coberta por regressão causal. Nenhum pacote aceito foi sobrescrito.

A revisão independente comparou literalmente **5.021.034 contribuições não atingidas**, todos os derivados fora dos 16 contextos e as três tabelas estruturais (estas byte-exatas). Conferiu também as 16 substituições e reduções exatas de 16 contextos × 1.422 unidades, com 2.000 células conjuntas. Contagens globais preservadas: 5.021.050 contribuições nativas e 9.672 ocorrências nominais de companhias admitidas sem unidade; elegíveis passam de 4.300.144 para **4.300.156**, aumento de 12.

Em Financeiro/Tcb N2/ROA TTM/202412, a cobertura do **AT conhecido** passou de 58,71% para **96,936206152169%**, com **123 de 136 unidades elegíveis**. Isso não certifica 100% da população ou cobertura de ativos desconhecidos. As demais lacunas N2 e os episódios XP/Warren permanecem sem ponte automática. O conjunto das companhias abertas não muda: Terra pertence ao restante neste corte.

Verificação direcionada no checkout de publicação: **48 testes PASS em 37,955 segundos**, abrangendo seletivos e composição. Revisões independentes por fatia e de inventário/proveniência concluídas; CI e publicação têm estados próprios, registrados na Issue 154.

O novo HTML autocontido foi conferido contra a composição aceita: **305.090 células, 4.300.156 frações elegíveis**, 60 períodos e três perspectivas. O núcleo JavaScript com BigInt coincidiu com 12.620 agregados não vazios, 340 vazios, distribuições e estoques persistidos; recortes combinados foram conferidos em 54 contextos. O aviso Terra depende da metadata da ponte; o aviso B3C explica o custo líquido sem alterar sinais. Esta é conferência automática de dados/código, sem afirmar nova inspeção visual humana. HTML/dados e cópia privada no Drive ficam fora do Git; a versão anterior foi preservada.

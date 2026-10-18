# BRB em 3T2022: fonte alternativa e janela afetada

[Issue 141](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/141), 16/10/2026. Busca curta oficial, conferência dos indicadores afetados e aviso L2. Sem ingestão, substituição ou recálculo.

## Fontes encontradas e possibilidade de recuperação

Há divulgação oficial para setembro de 2022, apesar dos nulos recebidos. O [Pilar III 3T22](https://ri.brb.com.br/upload/files/3208_Relatorio-Gerenciamento-de-Riscos-Pilar-III-3T22.pdf), p.4/KM1, e seu [anexo estruturado](https://ri.brb.com.br/upload/files/3261_3T22-Anexo-do-Relatorio-Gerenciamento-de-Riscos-Pilar-III.xlsx) trazem capital e índices. O [ITR 3T22 versão 3](https://ri.brb.com.br/upload/files/0740_ITR-3T22.pdf) contém demonstrações BRB-Múltiplo e BRB-Consolidado Cosif, além das primeiras tabelas individuais. A [nota de fontes](brb-202209-official-sources-20261016.md) guarda localizadores, precisão, versões, UTC, headers, status e hashes. A busca terminou após obter evidência suficiente.

| Frente | Evidência | Estado permitido |
|---|---|---|
|Prudencial C3/C4|Pilar/anexo KM1: ICP7,97% e Basileia14,35% publicados, CP/PR/RWA.|Candidato forte; admissão exige precisão e identificação de perímetro próprias. Não são novos índices calculados nesta tarefa.|
|Financeiro L2 e demais|ITR Cosif consolidado: depósitos à vista, disponibilidades, aplicações, AT/PL/DRE.|Fonte candidata; comparativo2021 não coincide com C0031976 além do arredondamento.|
|Individual|Coluna BRB-Múltiplo e demonstrações individuais.|Candidato próprio; não preencher conglomerado com coluna individual.|

Não adotar CP=PR ou trocar lucro do controlador pelo total. A existência de fonte oficial não transforma o nulo original em erro de processamento.

## Janela inteira dos indicadores afetados

Autenticados manifesto130/Parquets necessários, três manifests/partições202209 e três GZ originais. Todos os **169 valores admitidos** desses códigos na data estão nulos também nos originais:75 Financeiro C0031976,75 Individual00000208 e19 Prudencial C0080288. Os primeiros abrangem Resumo/Ativo/Passivo/DRE; o último, relatório5. Cadastro contemporâneo liga as três unidades à seleção BRB, preservando códigos/perspectivas e raiz de líder00000208; isso não comprova os membros de qualquer consolidado externo.

Conferidos 1T2022–4T2023, incluindo margens. **66 resultados indisponíveis** por native_null:32 Financeiro,32 Individual e2 Prudencial. São combinações indicador/janela/data, não66 indicadores diferentes.

| Perspectivas | Indicadores/janelas afetados | Datas |
|---|---|---|
|Financeiro e Individual, separadamente|C1 PL/AT; Q1 provisão/crédito; L2; L3, todos saldo na data|3T2022|
|Financeiro e Individual, separadamente|R1 ROA, R2 ROE, Q2 custo de provisão, E2-B eficiência; trimestre efetivo|3T e4T2022|
|Financeiro e Individual, separadamente|R1, R2, Q2, E2-B; últimos12meses|3T2022,4T2022,1T2023,2T2023,3T2023|
|Prudencial|C3 PR/RWA e C4 CP/RWA, saldo na data|3T2022|

Todos os resultados examinados desses códigos em1T/2T2022 e4T2023 estão disponíveis. A ausência202209 afeta a derivação do4T2022 e o estoque de abertura de médias posteriores. Uma eventual recuperação deve tratar o lote de dependências até3T2023, preservando margens e demais unidades.

Artefatos privados emV: conferir-janela-brb-202209.py, brb-202209-window.csv, brb-202209-native.csv e brb-202209-window-recibo.json. Consulta/conferência2,77s, sem avaliador ou divisão para gerar indicador.

## Precisão e confronto com uma referência disponível

Tokens XML de setembro na abaKM1, valores em R$milhões: CP/E9=1838.0376052700001; PR/E11=3308.9411171500001; RWA/E15=23059.334440619998. ICP/E17=7.9709048411745087E-2 e Basileia/E19=0.14349681798799707, frações formatadas como%. E7 é etiqueta mensal de setembro; encerramento30/09 vem doPDF. Caudas Excel não são precisão econômica certificada nem foram arredondadas silenciosamente.

Comparação com o nativo de2T2022, colunaF do mesmo anexo:

| Componente | Fonte convertida exatamente aR$ | IF.data nativoR$ | DiferençaR$ |
|---|---:|---:|---:|
|CP|1995744912.0799999|1995744912.08|−0.0000001|
|PR|2974219533.9699997|2974219533.97|−0.0000003|
|RWA|21626003000.000001|21626002997.23|2.770001|

Há forte coerência prudencial de conceito/grandeza, mas não igualdade exata. Se admitida, a fonte conserva token, escala, precisão e proveniência próprios, distinguindo índice publicado de razão calculada. Não se adotou tolerância automática.

No Financeiro, o consolidado doITR p.37 em31/12/2021, comparado com C0031976 nativo:

| Componente | ITR consolidadoR$mil | IF.data FinanceiroR$ | Diferença após escalaR$ |
|---|---:|---:|---:|
|AT|31710381|30555181303.99|1155199696.01|
|Disponibilidades|162054|161495982.86|558017.14|

As diferenças excedem arredondamento ao milhar. O ITR inclui outras entidades/atividades e versões de comparativos; a contribuição de perímetro, conceito e revisão **ainda não foi decomposta**. Não importar silenciosamente suas rubricas de30/09/2022. PL/lucro de controlador e não controlador e jan–set/jul–set são separados na fonte.

Confronto determinístico em conferir-brb-fontes-alternativas.py e brb-202209-alternative-comparison.json, com hashes e tokens XML, sem float ou ratios novos. ITR privado tem16777216bytes conforme Content-Length e padding zero após%%EOF; bytes originais preservados, sem corte. PDFs extraídos/renderizados para inspeção, não publicados integralmente.

## L2 e cobertura metodológica por atividade

João reafirmou o desenho original: **atividades e segmentações precisam de indicadores adequados ou adaptações fundamentadas**. A dimensão de liquidez dos bancos de desenvolvimento não fica atendida somente porque L2 não é calculável. BNDES33657248 tem depósitos à vista zero em60/60trimestres observados.

A cobertura por atividade é pendência de pesquisa/implementação, começando pela lacuna identificada de liquidez para desenvolvimento. Nenhuma fórmula alternativa, proxy, limiar ou agregação entre métricas diferentes foi adotada nesta tarefa. Exigir componentes, referência, precisão, perímetro, janela e comparabilidade; manter protocolo/Issue3. Não converter Tcb/zero automaticamente em não aplicabilidade.

O explorador recebeu aviso somente em Financeiro/L2: alcanceDV, zero≠baixa liquidez, coberturaAT e indicadores poratividade ainda não implementados emtodossegmentos. Origem técnica em detalhe expansível. C4 preservado e packed byte-exato, mantendo295404linhas/metadados. HTML SHA256 d38634b5655f70dae35dfbedff7b812c5496082b783f9dde88c3ecde5769b76d; aplicar-aviso-l2-explorador.py e explorador-l2-aviso-recibo.json.6checksL2+6C4+8gerais PASS, screenshot inspecionada, revisão independenteA PASS.

## Encaminhamento e aceite

Próximo lote possível:admissão seletiva da fonte prudencial BRB/202209 com contrato de precisão/perímetro/proveniência, seguida somente dos alvosC3/C4 afetados, se aprovado o uso dessa fonte. Financeiro/Individual exigem antes fechar diferenças de escopo/revisão/conceito; não há recuperação automática dos66resultados.

Outra pendência é pesquisar liquidez adequada a desenvolvimento e demais atividades não cobertas, conforme desenho já aprovado, sem substituirL2 universalmente ou misturar métricas no mesmo agregado.

Revisão independente B/fontes/janela/composição final PASS, sem achados materiais, registrada na Issue141. Conferidos por revisor:66resultados nulos,78resultados de margens disponíveis, hashes, renders e comparações de precisão. Compilação dos scripts e diff sem erros de whitespace. Resultado local; sem nova ingestãoIF.data, recálculo, alteração motor/perfil, commit/PR/Goal, Word ouProject3.

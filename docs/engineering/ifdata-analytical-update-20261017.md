# Atualização analítica IF.data — entrega152

## Resultado e escopo

A [Issue152](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/152) atualiza a exploração2010–2024 sem reavaliar as dez fórmulas anteriores: incorpora universo descritivo55identidades/32associações admitidas/24unidades financeiras no corte2024, oito correçõesROA/ROE da Caixa e dez novas métricas escalares em sete famílias aprovadas. Financeiro é principal; Individual e Prudencial permanecem separados. Atividade fica fora dos filtros.

O [plano](../superpowers/plans/2026-10-17-analytical-update.md) e a [matrizTcb](ifdata-tcb-indicator-adequacy-20261017.md) detalham contratos e limites. A seleção de referência2024 não certifica por si população dinâmica de companhias listadas; vínculos são datados, sobreposições e desconhecidos explícitos. As23identidades sem associação admitida permanecem no diagnóstico nominal.

## Responsabilidades e comandos

`bank_quality/ifdata_universe_analysis.py` mantém orquestração, composição e cobertura; reutiliza a matemática exata em `ifdata_analysis.py`. `ifdata_population.py` operacionaliza pertencimento; `ifdata_cadastro.py` mantémSr analítico separado do original. A CLI `scripts/analyze-ifdata.py --help` oferece operações de cálculo seletivo, complementos, composição e consulta. Configurações autenticam os manifests de origem e a allowlist de períodos/métricas/perspectivas. Saídas novas não sobrescrevem pacotes aceitos.

- `recalculate-caixa`: ponte banco00360305→conglomeradoC0051626, somente Financeiro/R1,R2/TTM em202109,202112,202203,202206.
- `calculate-complements`: somente os complementos selecionados; não reavalia as métricas anteriores.
- `compose-analysis`: reúne valores persistidos, correções finitas e pertencimento; constrói nove tabelas, sem chamar o avaliador das fórmulas anteriores.
- `query-composition`: consulta autenticada sobre tabelas persistidas, sem recalcular indicadores.
- `scripts/export-ifdata-explorer.py --composition ROOT --expected-manifest-sha256 SHA256 --output NEW_HTML`: gera HTML autocontido a partir do pacote aceito. Destino deve ser novo.

Para sintaxe e campos completos, usar `--help` da operação. Configurações, pacotes financeiros e HTML com dados permanecem privados, fora doGit.

## Complementos e precisão

LA=(disponibilidades+aplicações interfinanceiras)/AT; LC=crédito/AT; LF divide quatro parcelas reconciliadas pelo funding reconhecido. RS relaciona serviços/tarifas à renda selecionada; E3 relaciona custos aoATmédio; R4 relaciona resultado de intermediação aoATmédio; R5 relaciona rendas de crédito à carteira média. R4 não éNIM e R5 não éspread líquido. A matrizTcb documenta componentes, referências e interpretação por negócio.

Trimestres efetivos respeitam reset semestral; TTM usa quatro trimestres, com abertura e média de estoques ponderada pelo tempo. Não há anualização por multiplicação por quatro. Frações/Decimal preservam tokens e precisão; apenas apresentação arredonda. Zero, null, ausente, negativo e não aplicabilidade são distintos. Denominadores negativos e reversões não são eliminados silenciosamente.

A ponteCaixa é continuidade do perímetro observado, não reconstrução de perímetro constante. Divergências de junho2021 estão documentadas na [nota de fontes](caixa-financial-transition-sources-20261016.md). A ponte não foi estendida automaticamente aE2-B/RS/E3/R4/R5: 18de32contribuições dos novos fluxos na transição ainda têmbinding_missing. As correções2019 conservam os limites de definição e dasIPs.

## Saídas e exploração

Pacote composto: `unit_periods`, `unit_coverage`, `company_coverage`, `representation_stocks`, `aggregates`, `distributions`, `segment_coverage`, `cohort_comparisons`, `joint_cells`, emParquet com campos econômicos exatos noJSONpayload.

As células conjuntas contêm apenas tuplas observadas Tcb/SegmentoTb/Tc/Td/Sr/SrAnalitico e coortes disjuntas seleção/restante/desconhecido. FiltrosAND e atalhosOR explícitos recompõem N/D e distribuições persistidas comBigInt, sem reavaliar fórmulas financeiras. O total inclui seleção/restante/desconhecido quando presentes. Estoques própriosAT/crédito/PL, contagens e cobertura são mantidos; Prudencial não recebe proxy de ativo financeiro. Distribuições conservam todas as frações elegíveis e quantisType2; exemplos de unidades têm limite explícito de oito, companhias nominais não são truncadas.

Moeda nativa: SaldoOData emR$, escala1. Não transplantar R$mil doportal. Não há eliminação econômica de exposições entre unidades ou soma entre perspectivas. IF.data é sistema observado, nãoSFN exaustivo. Os agregados sãoΣN/ΣD da mesma interseção elegível; não médias simples de razões.

## Evidência da execução e revisão

Execução completa de composição:60trimestres, três perspectivas,4.031,6235s; zero avaliações das fórmulas anteriores. Preserve2.359.880contribuições anteriores e16.892dos recortes corrigidos. Produziu244.001unidades-períodos,5.021.050contribuições,178.200linhas nominais,12.960agregados/distribuições e305.090células conjuntas.

Manifest composto SHA-256: `25f72484df934ffefdead578015558a77dcaaf191da4a52f7d400c6a4a485d1b`. Revisão independenteF: todas5.021.050assinaturas econômicas contra16origens autenticadas, hashes/IDs/contagens, registry55/seleção32, partições e dez contextos diretos×cincofiltros×quatrocoortes. Recibo privado: `5b7eb0afad39d4b32218fb448be6ef6350454acc442246145ab00fee710704f0`.

HTML final SHA-256: `8745cb34691fea6cf709c4d46f0572b293fa5b719c4191568e701a72b0dcd2bd`,98.299.074bytes, export54,7004s. QA integral comparou305.090células e4.300.144frações,12.620agregados não vazios+340vazios,37.860conferências de estoques e37.860de quartis, em54contextos. Recibo privado: `4c6d15591ab6f9e2d0b734f1fc593537c83f9c54a4a0c693d4fc0dc08bf475ef`, registro posterior das saídas observadas, sem alegação de stdout previamente capturado. Tempo62,1438s éQA emNode, não abertura no navegador. O oráculo agregado não contém contagem negativa deAT; contagens negativas de todas as células foram confrontadas com a fonte.

Revisão independente final de composição/inventário/artefato:PASS, sem achados materiais. João confirmou abertura do HTML e funcionamento dos filtros em17/10/2026, resolvendo o gate visual por aceite humano. Não é alegação de render pelo agente ou inspeção visual de todas as combinações. [Aceite registrado](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/152#issuecomment-6243944906).

## Limites e publicação

As sete famílias não encerram a seleção por negócio nem cobrem integralmente cinco dimensões. Salvaguarda de pagamentos, obrigações de clientes, centralização cooperativa, leasing e funding institucional têm necessidades específicas documentadas, ainda sem adoção automática de indicadores candidatos. Inferência, causalidade, ranking e índice composto não foram implementados.

A entrega local foi concluída antes da publicação. Este lote de integração reúne a implementação aprovada e suas dependências locais2019/Sr/diagnósticos; conserva documentação eCI atuais damain. A investigação posteriorN2/Terra eE2-B/B3C permanece separada. PR/checks/revisão doSHA publicado serão registrados naIssue152; conclusão local não prova merge ouCI pós-merge.

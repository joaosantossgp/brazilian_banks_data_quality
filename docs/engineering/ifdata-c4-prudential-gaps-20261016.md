# C4 prudencial: diagnóstico da janela 2018–2024

[Issue139](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/139), autorização de João em16/10/2026. Foram examinados todos os28trimestres de2018–2024 e os quatro de2017 como comparação. **Nenhum indicador foi recalculado e o explorador não foi alterado.**

## Conclusão e possibilidade de resolução

Não foi encontrada perda de CP, RWA, PR ou índice de capital principal entre a captura OData recebida, o Parquet admitido e os componentes/resultados armazenados, nos checks descritos abaixo. A interrupção de cobertura não se resolve removendo proteção do motor, como no caso LL2019: os valores de capital principal já são nulos na captura.

A mudança para o regime simplificado PRS5 entra em vigor em18/02/2018, alinhada à quebra. É uma explicação regulatória sustentada para o padrão, **não prova individual da opção nem significado oficial de cada null**. S5, nulos e hipótese de regime permanecem fatos distintos. Fontes, artigos, páginas e alterações de vigência estão na [nota normativa](ifdata-c4-regime-sources-20261016.md).

Na janela2018–2024, nenhuma das25272ocorrências de CP nulo tem índice de capital principal publicado disponível. Tampouco há componentes completos para reconstruir CP pelas identidades NI−CC ou PR−NII−CC. **Zero recuperações diretas de CP foram demonstradas neste corpus**, sem concluir que outra fonte externa não possa existir. PR/RWA observado não pode substituir CP/RWA silenciosamente.

## Cadeia conferida e escopo de processamento

Entradas autenticadas:

- Base130 `ifdata-universe-analysis-20261014-final-run3`, manifesto `b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`; apenas os Parquets componentes/resultados/unidades necessários, sem auditoria88GB.
- Fonte capital `ifdata-odata-20261011/capital`, manifesto `01c4e2d086cc8c2ad015b18f36c5886c07ef3e4ec31434d594231bd87ffaac32`:32partições e32GZ originais da captura de11/10/2026, com seus pins.
- Atributos136 `ifdata-sr-links-20261016-run2`, manifesto `a8e09826ec1b50becab01a844fa4954762a71a6fdfd60b245be53ebce372a3be`, sem derivação nova.

Verificadas **849908 linhas nativas** do relatório5 frente à posição original de cada registro na captura: TipoInstituicao, código, data, relatório, grupo, conta, nomes/descrições literais e equivalência exata Decimal de Saldo; null separado de zero. A equivalência monetária não exige identidade lexical entre decimal JSON e token textual. Unicidade e contagens conferidas.

Comparados **172344 componentes** CP79645/RWA79665/PR79649/ICP79659, incluindo tokens e hash de origem. Conferidas **43086 unidades-período** quanto ao conjunto de chaves, componentes point CP/RWA e status C4. O status reproduz: null em componente→native_null; RWAzero→zero_denominator; demais→ok. Compararam-se as frações armazenadas aos tokens, sem divisão, chamada ao avaliador ou geração de novos valores financeiros.

`processing_mismatches=0` significa zero divergências nesses controles de transporte, seleção e estado. Não certifica qualidade econômica da fonte, opção regulatória individual, continuidade de perímetro ou comparabilidade dos agregados. O escopo é a captura recebida, não uma consulta atual ao portal.

## Toda a janela e comparação anterior

O CSV por período contempla todos os32trimestres. Pontos de referência:

| Período | Presentes | C4 elegível | CP nulo na fonte | Outras causas |
|---|---:|---:|---:|---|
|1T2017|1440|1393|10|37 RWAzero|
|2T2017|1426|1370|17|39 RWAzero|
|3T2017|1410|1329|81|0|
|4T2017|1395|1352|43|0|
|1T2018|1391|442|949|0|
|4T2018|1354|436|918|0|
|4T2019|1304|427|877|0|
|4T2020|1307|432|875|0|
|4T2021|1311|440|871|0|
|4T2022|1344|432|912|0|
|4T2023|1351|431|919|1 RWAzero|
|4T2024|1367|444|923|0|

Entre4T2017 e1T2018, **908 códigos presentes nas duas datas** passam de C4ok para CP nulo, e um faz a transição contrária. A diferença não é explicada apenas por entrada/saída de unidades. Todos esses908 têm Sr desconhecido nas evidências contemporâneas usadas; não atribuir retrospectivamenteS5.

Somente2018–2024: **37415 unidades-período**,12138 elegíveis,25272 comCPnulo,1 comRWA nulo eCPobservado,4 comRWAzero. Incluindo2017:43086 posições,17582 elegíveis,25423CPnulo,1RWAnulo e80RWAzero. São ocorrências por trimestre, não companhias distintas.

### Regime e classificações: limites quantificados

Das25272ocorrências deCPnulo em2018–2024:

| Sr analítico contemporâneo | Ocorrências | PR observado e RWA positivo | Interpretação permitida |
|---|---:|---:|---|
|S5|15337|15253|Padrão compatível com simplificação; não comprova opção por si só.|
|S1–S4|102|83|Exceções fora do padrãoS5; não justificar genericamente pela simplificação.|
|Desconhecido|9833|8829|Causa regulatória individual não determinada; não preencherSr pelo nulo deCP.|

Há24posições elegíveisS5 na janela total2017–2024, portanto não existe equivalência bidirecionalS5⇔CPnulo. Classificação/pré-regime, definição de unidade consolidada e datas de vínculo limitam a leitura. DistribuiçãoTcb/Sr/SrAnalitico completa emCSV; original e derivado permanecem separados.

## Exceções nominais pela janela inteira

**DM, código prudencial C0083467:** CP e índice próprios são observados nos quatro trimestres2017; CP passa a nulo em1T2018 e assim fica nos27trimestres até3T2024, enquantoPR/RWA continuam observados. Sr analítico permanece desconhecido até1T2024, S5 em2T/3T2024 eS4 em4T2024, quandoCP volta a ser observado. Isso é compatível com mudança de regime/perímetro, mas não prova opção desde2018 nem continuidade econômica integral do código. A variação dePR em2T2024 exige atenção ao perímetro; não emendar valores por nome. A busca normativa curta não obteve prova individual para fechar a causa.

**BRB, C0080288:** em3T2022, CP/PR/RWA/ICP estão todos nulos na captura. CP/RWA são observados em2T e4T2022. SrS3 contemporâneo impede justificar automaticamente o caso porS5. A janela completa confirma que é exceção pontual de reporte recebido; motivo econômico/retificação fora desta captura permanece desconhecido. Recuperação exigiria fonte oficial alternativa datada para o mesmo perímetro/data, sem interpolação.

**RWA nulo com CP observado:** C0086206 em1T2022, CP69563713.42 eRWA null. **RWAzero pós2018:** C0087243 em3T2023–2T2024; estoquesCP presentes eRWAzero. Essas quatro posições conservam proteção matemática; não sãoCPnulo/S5.

## Encaminhamento simples, sem adoção automática

1. Manter C4 como CP/RWA nas unidades com componentes observados e cobertura explícita. Não chamar CP ausente de capitalzero ou baixa solvência.
2. Documentar no explorador a quebra2018 e distinguir dado ausente, regime candidato e aplicabilidade não comprovada. Isso é uma possível próxima alteração de apresentação, ainda não executada.
3. Para ampliar análise de capital, avaliar os resultados C3PR/RWA já calculados, mantendo a composição/regime próprios. Uma nova métrica PRS5/RWAS5, se necessária, exige identificação dos optantes/componentes e decisão metodológica; não é preenchimento automático deC4.
4. Uma busca por fonte alternativa deve ser curta e focada em exceções relevantes, como BRB202209. Não abrir uma coleta geral para perseguir todos os nulos. As demais frentes aprovadas podem avançar com essa limitação explícita.

## Reprodução, artefatos e aceite

`scripts/diagnose-ifdata-c4.py` somente consulta entradas e grava tabelas diagnósticas em destino novo, sem alterar motor/perfil/indicadores:

```powershell
python scripts/diagnose-ifdata-c4.py --root "<data/curated>" --raw "<data/raw/ifdata-odata-20261011>" --output "<novo destino>"
```

Saída aceita local `data/curated/ifdata-c4-diagnostic-20261016-run1`, manifestoSHA256 `202ce3539e10148703988f218007a1141fbb26f4ef33705d564747066b2a5cbe`; execução **25,26s**. SeisCSVs: unit_diagnosis, period_coverage, segment_coverage, source_definitions, transitions e named_exceptions. Fonte monetária sempre textual/Decimal, nenhuma imputação. Manifesto inclui pins e hashes de entradas/saídas/produtor; é resultado diagnóstico, não novo pacote de indicadores.

Revisão independente fatiaA PASS: contagens, chaves, hashes, script, controles e amostrasbrutas próprias. RevisãoB de fontes/conclusões e composição final PASS, sem achados materiais, registrada na Issue139. Compilação do script e `git diff --check` passaram. Semcommit/PR, nova coletaIFdata, Goal ou operaçãoProject3. O HTML138 continua comSHA256 `c028e720ed1c067def11aaded22bc78bf3ec7b511b6f27a4d5b0a9c07e2adb98`.

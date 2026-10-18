# Lacunas cadastrais por janela completa — 16/10/2026

## Sr por vínculo implementado — Issue136, 16/10/2026

João aprovou aplicar Sr por vínculo, manter o original e os conflitos explícitos e encerrar uma busca curta em lote deTcb/Td/Tc. SegmentoTb continua intacto. A [Issue136](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/136) atualiza a proposta da #135 abaixo: a derivação agora está **adotada e implementada como atributo analítico separado**, sem transformar o resultado em enquadramento oficial recuperado. A primeira investigação permanece como histórico/proveniência.

### Regra e atributos

- `sr_original`: cópia exata deSr nativo, inclusive null/vazio; sua observação tem prioridade.
- `sr_vinculo`: preenchido somente quando o original falta, com um Sr observado válidoS1–S5 e um conglomerado prudencial único nas evidências contemporâneas. Todas as evidências devem ter parent, identidade/data e origem reconhecidos; vínculos prudenciais de membros apontam ao próprio alvo.
- `sr_analitico`: original quando disponível; caso contrário, vínculo aprovado. `method` distingue `native`, `dated_link` e ausência de atribuição; `status` distingue `native`, `derived`, `conflict`, `unknown` e `before_regime`.
- Membros semSr não viram votos nem valores imputados. A prova conserva todos os membros usados, quantos têmSr e seus campos deorigem. Duas classificações diferentes produzem conflito, sem escolha por maioria, líder ou ativos. Perímetro múltiplo/não comprovado e rótulo não reconhecido não liberam a derivação.
- Antes201703 não se derivaSr por carregamento temporal. Sr nativo, Tcb, Td, Tc e SegmentoTb permanecem exatamente iguais, assim como valores financeiros, população, vínculos e elegibilidade dos indicadores.

A classificação de um grupo financeiro por vínculo é um atributo analítico associado ao perímetro prudencial identificado nas evidências; não certifica equivalência entre os perímetros. O fundamento consolidado da Res4553art2§6 está citado abaixo. Há membros semSr nas evidências de algumas atribuições; rótulo único entre os observados não certifica completude de todo o grupo.

### Resultado completo e cobertura

244001unidades-período receberam os atributos separados. Foram aplicadas **974 atribuições financeiras e1056prudenciais**, sem novas atribuições individuais. Os conflitos `financial/C0050201/202303` e `capital/C0080367/202303` continuam sem valor analítico atribuído; a categoria conflitante permanece visível. O novo campo não exclui essas unidades do universo ou dos indicadores.

| Perspectiva em4T2024 | Sr original preenchido | Acréscimo por vínculo | Sr analítico preenchido | Unidades presentes |
|---|---:|---:|---:|---:|
|Financeiro|1049|30|1079|1422|
|Prudencial|999|38|1037|1367|
|Individual|1212|0|1212|1585|

Na janela inteira S4 de4T2017–3T2018, antes interrompida no Financeiro e Prudencial, o novo atributo tem respectivamente **25/28/34/38 unidades derivadas em cada perspectiva**, sem alterar a ausência da categoria noSr original. A consulta regulatória original e o atributo analítico têm usos distintos, explicitados no explorador.

Tabela consultável em `data/curated/ifdata-sr-links-20261016-run2`: `attributes.csv`, `attributes.parquet` e `coverage.csv`, contrato `ifdata-sr-attribution-v1`, manifesto `a8e09826ec1b50becab01a844fa4954762a71a6fdfd60b245be53ebce372a3be`. Cada linha preserva os cinco campos originais, cadastro próprio e prova da atribuição. Execução15,89s. Run1 parcial semmanifesto, causado por argumento não aceito na interface Pythonread_csv, não é saída aceita; o run2 usa leituraSQL explícita que preserva null/vazio. A primeira revisão do helper precedeu o build; a revisão B comparou integralmente as244001linhas com os originais e confirmou todos os2030derivados/doisconflitos.

### Reagrupamento e explorador

O reagrupamento leu contribuições já armazenadas, com os três overlays aceitos deROA2019, acrescentando somenteSrAnalitico em cópia. Não executou `evaluate_metric` nem reconstruiu componentes financeiros. O eixo originalSr e os demais continuam iguais. Foi necessário reagrupar64contextos perspectiva/período, contendo608232contribuições de indicadores; os contextos restantes copiam a segmentaçãoSr original para o novo eixo, pois não há alteração de classificação neles.

Saída `data/curated/ifdata-sr-regroup-20261016-run1`, contrato `ifdata-sr-segmentation-v1`, manifesto `285a3aa12cce8a666e47dfbdc7c15bbfd4887fcce47a8829f19327a92c8cd7f7`:11376linhas segmentadas exatas emJSON/CSV/Parquet. Tempo79,50s incluindo persistência; probe deumcontexto0,65s foi revisado antesdaampliação. A revisão independente conferiu todas as1792partições contexto/métrica/janela/coorte, reconciliando quantidades e frações de numerador/denominador com os agregados originais e correções2019. Não houve recálculo financeiro.

Explorador local: novo eixo **Sr analítico · vínculo**, mantendo **Sr original · segmento prudencial**. Aviso apresenta contagens de originais/derivados/conflitos/desconhecidos da perspectiva/data antes do filtro decategoria; são contagens de classificação, não elegibilidade doindicador. Há categoria conflitante, aviso antes2017, flags deorigem e manifesto noCSV do novo eixo. A projeção acrescentou18438linhas e preservou **todas as276966linhas anteriores exatamente iguais**, inclusiveSegmentoTb e as correçõesROA2019. HTML SHA256 `a3ee304a8488c98e1be847e0559474dedea555acf1fc2d388f1313067d7909c5`; recibo privado `explorador-sr-vinculo-recibo.json`. Após regenerar a exportação integral antiga, reaplicar as projeções133→134→136; não recalcular indicadores para isso.

### Busca curta Tcb/Td/Tc encerrada

Foram feitas nove buscas por código exato e sete por nome/data/atributo em fontesBCB, em cerca de3minutos. **Nenhum preenchimento direto contemporâneo foi comprovado** para as dezjanelas/novecódigos da tabela abaixo. Não se atribuiu controle/tipo com base em nome ou situação atual. ParaC0052113,21partições cadastrais201909–202409 autenticadas não contêm o código emCodInst, CodConglomeradoFinanceiro ouCodConglomeradoPrudencial; identidade permaneceu desconhecida. Recibo privado `busca-cadastral-136.json` guarda consultas/status/pins. Isso não prova inexistência de outrafonte; a busca foi encerrada conforme solicitado, sem nova coletaIFdata. As44ocorrências permanecem sem preenchimento, eSegmentoTb permanece intacto.

### Reprodução e verificação

`derive_sr_by_links` pertence ao módulo cadastral existente; `scripts/classify-ifdata-sr.py` oferece os dois passos com destinos novos:

```powershell
python scripts/classify-ifdata-sr.py --baseline "<base130>" `
  --expected-baseline-manifest-sha256 b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192 `
  --diagnostic "<diagnóstico135run2>" `
  --expected-diagnostic-manifest-sha256 a7a3f33a5178a4c15ac4bacffe3ab56f5c7c5f09c40bad51cbe1f1775ed3f5ef `
  --output "<novo destino de atributos>"

python scripts/classify-ifdata-sr.py --baseline "<base130>" `
  --expected-baseline-manifest-sha256 b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192 `
  --attributes "<atributos136run2>" `
  --expected-attributes-manifest-sha256 a8e09826ec1b50becab01a844fa4954762a71a6fdfd60b245be53ebce372a3be `
  --correction "<correção201903>" 4b62afc3107b4a8fe16e71829c7319939b3321f1f0d9ed51e7a8db6e71f530ed `
  --correction "<correção201906>" aa90ae19dbfe388f4352ea78d839ac778dd7c00305912552822b204bee28c13d `
  --correction "<correção201909>" 2c3ff18775dbea3edc04ded5cdff021a607d63f79a184a3d0c1d1ef5088742f2 `
  --output "<novo destino de segmentação>"
```

Ao reproduzir o primeiro passo, o manifesto produzido terá seu próprio hash, a utilizar nosegundo. O script privado `aplicar-sr-vinculo-explorador.py` autentica os resultados e acrescenta exclusivamente o novo eixo. O CSV de atributos preserva null/vazio; preferir seuParquet para consultas tipadas textuais.

TDD: helper inicialmenteausente eprojeção inicialmenteausente geraram falhas esperadas;16testes pertinentes (noveSr e sete cadastro) passaram. Três scriptsdesktop passaram23checks, semerrosJavaScript: novo eixo, origem, S4na janela, Sr original preservado, conflito, pré2017, prudencial separado, CSV/proveniência, correções2019 e demaisrecortes. Screenshotinspecionado. Revisões A/B/C e composição final PASS; projeção/escopo/documentação confirmados independentemente. Resultado local semcommit/PR/Goalnovo, semProject3.

## Diagnóstico135 preservado


[Issue 135](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/135). João determinou investigar a janela inteira de cada lacuna, sem entregas artificiais trimestre a trimestre. Prioridade: Tcb, Sr, SegmentoTb, incluindo Td/Tc quando a causa é compartilhada. Esta rodada diagnostica presença e classificação, sem recalcular indicadores, imputar dados ou alterar os pacotes aceitos. Não houve commit/PR.

## Resultado

**Não há perda de classificação entre o cadastro recebido e a projeção analítica.** Todas as 1.220.005 posições de cinco campos, em 244.001 unidades-período, correspondem à fonte por código/data. A segunda conferência comparou os 16 campos dos 303.792 registros cadastrais de 60 datas com seus JSONs: 4.860.672 posições exatamente iguais. Isso valida a fidelidade ao corpus recebido; não certifica que o cadastro publicado pelo BCB seja completo ou historicamente correto.

Nenhuma recuperação direta foi demonstrada no corpus. As lacunas são cadastros ausentes ou nulos nativos. A correção não consiste em remover uma proteção do motor: classificar por outra data, pela líder ou pelos membros seria uma derivação com semântica própria. A lista de candidatos e seus conflitos foi preparada, sem adoção automática.

| Campo | Financeiro: posições ausentes | Prudencial: posições ausentes | Individual: posições ausentes | Diagnóstico |
|---|---:|---:|---:|---|
|Tcb|39|5|0|44 ocorrências sem cadastro contemporâneo; não há Tcb nulo em cadastro encontrado.|
|Td|39|5|0|Mesmas ocorrências cadastrais de Tcb.|
|Tc|39|5|0|Mesmas ocorrências cadastrais de Tcb.|
|Sr|68.876|34.830|74.988|178.650 nulls nativos e 44 cadastros ausentes; classificação instituída em 2017.|
|SegmentoTb|4.630|17.744|0|22.330 nulls nativos e 44 cadastros ausentes; não herdar o segmento da líder.|

São posições de campo/unidade/período, não quantidades de companhias. As cinco contagens compartilham os mesmos 44 cadastros ausentes. Não foram encontrados vazios, conflitos de projeção, valores divergentes ou valores preenchidos na fonte que tenham sido perdidos na projeção. Os dois conflitos descritos adiante são de candidatos derivados, não conflitos do campo original.

## Tcb, Td e Tc: todas as dez janelas

| Perspectiva | Código | Janela completa sem cadastro | Trimestres |
|---|---|---|---:|
|Prudencial|C0080525|3T2016–2T2017|4|
|Prudencial|C0083106|3T2024|1|
|Financeiro|C0049951|3T2013–4T2013|2|
|Financeiro|C0051183|4T2016–2T2017|3|
|Financeiro|C0051248|2T2024–3T2024|2|
|Financeiro|C0051554|4T2020|1|
|Financeiro|C0051736|1T2010–1T2011|5|
|Financeiro|C0051736|3T2014|1|
|Financeiro|C0052058|4T2019–3T2020|4|
|Financeiro|C0052113|3T2019–3T2024|21|

Os nove códigos e as 44 ocorrências estão ausentes do cadastro da mesma data, inclusive no JSON original. Cadastros anteriores/posteriores e referências de membros a um conglomerado não preenchem automaticamente seus atributos. Datas de primeira/última presença não demonstram criação ou extinção jurídica.

**Possibilidade de resolução:** uma fonte contemporânea explícita para o próprio código/unidade permitiria complementar a classificação com proveniência. Sem ela, preencher Tcb/Td/Tc por nome, prefixo do código, líder ou carregamento temporal seria outra regra, ainda não adotada. Priorizar a busca em lote dos códigos acima caso essa complementação se torne necessária à análise; não começar consultas indiscriminadas companhia a companhia.

## Sr: distinguir início histórico, ausência e vínculo

Na janela 2010–2016, 108.938 posições têm Sr nativo nulo; outras 11 não têm cadastro. **S1–S5 não vigoravam nesse período.** A [Resolução 4.553 original](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50335/Res_4553_v1_O.pdf), art.11/p.5, entrou em vigor com a publicação em 31/1/2017. O art.10/pp.4–5 usa junho de 2016 como base do enquadramento inicial divulgado em 2017; isso não autoriza retroagir a classificação a 2016.

De 1T2017 a 4T2024, há 69.745 posições sem Sr: 22.905 financeiras, 22.792 prudenciais e 24.048 individuais, incluindo 33 cadastros ausentes. Não são 69.745 erros: o alcance regulatório e o nível de consolidação variam.

- O art.2 §6/p.2 da Resolução4.553 estabelece informações consolidadas para instituições de conglomerado prudencial. Os arts.3–8/pp.2–4 incluem exposição, atividade internacional, persistência e decisões do BCB: ativo de um trimestre não basta para reproduzir S oficial.
- O [REF de abril2017, seção2.5/p.53, nota72](https://www.bcb.gov.br/content/publicacoes/ref/201704/RELESTAB201704-refSegmentacaoSFN.pdf) exclui IPs e administradoras de consórcio independentes de conglomerado prudencial. Não generalizar a exclusão a todos os N4 nem tratar null como S5.
- A [ResoluçãoBCB197/2022](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?numero=197&tipo=Resolu%C3%A7%C3%A3o+BCB), arts.1–2 e12, trata conglomerados com serviços de pagamento e segmentação dos Tipo3; vigência em 1/7/2023, após a alteração pela ResBCB258/2022. Tipo1/2/3 desse regime não equivale a TipoInstituicao1/2/3 da API IF.data.

### Candidatos por vínculo, sem aplicação

O diagnóstico encontrou **974 ocorrências financeiras e 1.056 prudenciais** em que membros declarados na mesma data fornecem um único Sr observado e um único conglomerado prudencial. São respectivamente 87 e 113 códigos ao longo de2017–2024. Em 4T2024, seriam 30 e 38 ocorrências candidatas. Não são novos Sr próprios observados e não resolvem a maioria das ausências.

Há dois casos com rótulos diferentes entre membros em 1T2023: financeiro `C0050201` e prudencial `C0080367`. Permanecem conflitos, sem escolha por maioria, maior ativo ou líder. A evidência traz cada membro, vínculo, Sr e fonte. Observações sem Sr entre outros membros também continuam visíveis.

**Proposta não adotada:** se útil, criar um atributo analítico separado de Sr sustentado por vínculo prudencial contemporâneo, mantendo `Sr` original, método e fonte da derivação, conflitos e desconhecidos. Esse atributo não deve misturar perímetros financeiros/prudenciais, substituir nulls silenciosamente ou retroagir a regra. Adoção exige decisão metodológica própria na #3; a preparação dos candidatos não equivale a essa decisão.

Pesquisa primária limitada em16/10 não confirmou arquivo externo oficial histórico em lote com data+identificador+S para2017–2024. A rota documental do BCB aponta ao relatório IF.data de segmentação; a [página atual](https://www.bcb.gov.br/estabilidadefinanceira/regprudencialsegmentacao?modalAberto=mod_S1) não teve seletor histórico comprovado nesta rodada. O endereço legado do enquadramento inicial (`https://www.bcb.gov.br/nor/basileia/enquadramento.asp?idpai=regprudencial`) retornou404. Isso não prova inexistência de outra fonte; evita prometer recuperação externa ainda não demonstrada. Não houve nova coleta IF.data.

## Quatro lacunas internas de categorias: janela inteira conferida

| Perspectiva / campo / categoria | Janela sem reportantes nessa categoria | Causa observada |
|---|---|---|
|Financeiro / Sr / S4|4T2017–3T2018, quatro trimestres|O único código S4 reportante antes da lacuna,09105360/ICAP, deixa de ser unidade reportante financeira; seu cadastro individual continua S4 na janela e muda o vínculo prudencial deC0082705 paraC0082619. Não houve desaparecimento de todas as instituições S4.|
|Prudencial / Sr / S4|4T2017–3T2018, quatro trimestres|O único código S4 anterior,C0082705, deixa de constar como unidade reportante e não tem cadastro próprio nessas datas. A composição reportante e a cobertura do campo mudam.|
|Prudencial / SegmentoTb / Sociedade de Crédito, Financiamento e Investimento|2T2015–3T2018, 14trimestres|20443996/Becker deixa de reportar individualmente nessa perspectiva e passa a declarar conglomerado prudencialC0084507. O segmento literal da instituição continua no cadastro, mas não se transfere automaticamente ao conglomerado. Em4T2018 aparece outra unidade dessa categoria.|
|Prudencial / SegmentoTb / Sociedade Corretora de TVM|3T2017–4T2021, 18trimestres|13434335/Rico deixa de ser unidade reportante prudencial, embora o cadastro da instituição continue. Há vínculos contemporâneos distintos ao longo da janela. Em1T2022 aparece outra corretora reportante,61723847/Neon; não é retorno do mesmo código.|

Durante a lacuna S4 financeira/prudencial, a perspectiva individual tem respectivamente 27,30,37 e43 unidades S4. Uma linha interrompida significa ausência de resultado daquela categoria naquela perspectiva, não desaparecimento econômico do segmento. Não há autorização para adicionar membros como contribuintes no agregado consolidado.

## Reprodução, artefatos e revisão

`scripts/diagnose-ifdata-classification-gaps.py` compara todas as datas em lote DuckDB, autentica entradas e produz contagens, janelas contíguas por unidade/campo, cobertura de categorias, contexto das lacunas e evidência dos candidatos. Sem motor novo, dependência nova ou recálculo financeiro.

```powershell
python scripts/diagnose-ifdata-classification-gaps.py `
  --baseline "<data/curated/ifdata-universe-analysis-20261014-final-run3>" `
  --expected-baseline-manifest-sha256 b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192 `
  --raw-cadastro "<data/raw/ifdata-cadastro-20261011/ifdata_cadastro>" `
  --output "<diretório novo para o diagnóstico>"
```

Run1:6,87s, comparação de projeção/cadastro e quatro CSVs, revisão independente A PASS. Run2:23,12s, incluindo fontebruta e oito CSVs; manifesto `a7a3f33a5178a4c15ac4bacffe3ab56f5c7c5f09c40bad51cbe1f1775ed3f5ef`, destino `data/curated/ifdata-classification-gaps-20261016-run2`. Fonte cadastral `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1`; CSV de unidades `09f3fca3b787c63ed59fdfc3e61b6243e1eb5a102b11eb43b2e4c0b4cba3e46a`. O manifesto lista as 60partições e hashes dos oito CSVs, sem incorporar resultados financeiros.

Os arquivos `missing_units.csv`/`missing_windows.csv` contêm201200 posições e10123 janelas, com códigos/datas/causas; `internal_category_gaps.csv` e `category_gap_context.csv` contêm as quatro lacunas e48 observações de contexto; `sr_link_evidence.csv`/`sr_link_candidates.csv` conservam46473 evidências e36207 avaliações por vínculo, inclusive os sem rótulo. Todos são consultáveis diretamente por SQL/Python. Na leitura DuckDB dos CSVs, declarar `header=true, all_varchar=true, delim=',', quote='"', escape='"'`; isso evita uma inferência incorreta do dialeto quando nomes com vírgula aparecem somente depois da amostra inicial. Não ignorar linhas com erro. Não interpretar avaliações por vínculo como novas unidades financeiras.

Revisão independente B PASS: oito CSVs autenticados, evidências de Sr reagrupadas integralmente, contagens temporais e48contextos conferidos; amostras brutas completas de201012/201712/202412 verificadas campo a campo. Os quatro arquivos da fatia A são idênticos por hash. Composição documental final PASS: escopo, fontes, contagens, janelas e distinção entre observação/derivação conferidos; `git diff --check` passou. Como não se encontrou valor perdido recuperável, o explorador e os cálculos permanecem intactos. Recuperações por outra fonte, classificações derivadas e alterações visuais dependentes terão recorte próprio; este diagnóstico já permite continuar a análise agregada com cobertura e desconhecidos explícitos.

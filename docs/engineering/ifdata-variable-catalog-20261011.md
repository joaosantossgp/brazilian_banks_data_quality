# Catálogo temporal de variáveis IF.data

Extensão da [Issue 61](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/61), em **2026-10-11**. Base de revisão: `main` `3b5da70b22499cff93bdd642e74c9157b75eb6fc`; branch `codex/ifdata-variable-catalog`. A Issue foi consultada aberta, `kind:task`, `role:implementation`, `status:in-progress`, áreas data/domain/docs. Esta nota aplica as instruções locais Matt `research` por agente delegado, mediante leitura do checkout e consulta web primária. Não foi executado comando slash nem instalado runtime. Destino canônico `docs/engineering/`, sem pasta ou camada nova; integração dos documentos compartilhados pertence ao coordenador.

Objetivo: inventariar as definições literais e sua cobertura observada nos quatro conjuntos Parquet aceitos, para subsidiar a investigação de desempenho econômico-financeiro, crédito, risco e patrimônio. **2010–2024 é a janela principal; 2025–2026 é complementar.** Não há escolha/cálculo de indicadores, seleção de instituições, join com cadastro ou certificação de comparabilidade. Cadastro e vínculos aguardam download e contrato próprios.

## Fontes documentais e limites

Consulta web em 2026-10-11, somente a documentação; sem requisições de valores ou cadastro. **D** indica texto documental obtido na abertura; **I**, conteúdo oficial retornado pelo índice de busca, sem confirmação do corpo direto. Referências locais são reaproveitamento explícito, sem nova autenticação de seus corpos fonte.

| Fonte primária | Localizador e resultado delimitado | Limite |
|---|---|---|
| [Portal IF.data](https://www3.bcb.gov.br/ifdata/index.html), I | “Atualização Contábil – Cosif 2025”: vigência desde 01/01/2025, atualização sobretudo em ativos/resultados; passivos com estrutura semelhante; referência às INs BCB 426–433. | Abertura web retornou 502; leitura direta retornou rejeição oficial. O resultado indexado não é corpo autenticado nem prova de versão histórica. Semelhança não certifica equivalência. |
| Mesmo portal, I | “Informações de Crédito”: financeiro até 12/2024, prudencial desde 03/2025; substituição do relatório por nível de risco pelo de carteiras de instrumentos financeiros. | Não demonstra enumeração OData nem equivalência entre carteiras e estágios. Não altera automaticamente a interpretação dos quatro relatórios contábeis. |
| Mesmo portal, I | “Periodicidade e Prazos”: divulgação trimestral; substituições tardias incorporadas ao reprocessamento anual em abril subsequente. | Data-base, janela do fluxo, versão e coleta são distintas. |
| [BCB, Esclarecimentos e Metodologia](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf), D, duas páginas, sem edição visível | P.1: famílias/fontes e datas de oferta; p.2, notas 1–3: individual, financeiro e prudencial são perspectivas próprias; nota 2 registra mudança das independentes desde 2018. | Os números dessas notas são localizadores do documento; não provam os valores de `TipoInstituicao` na API. Documento antigo não resolve sozinho o perímetro vigente pós-2025. |
| [Documentação Olinda IFDATA v1](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/aplicacao), D limitado | A abertura devolveu o shell da aplicação com campos de template, sem descrição legível do endpoint. | Não foi obtida nesta consulta documentação específica suficiente para certificar unidade, janela ou enumeração de `IfDataValores`. Nenhum payload foi solicitado para suprir essa lacuna. |

Não se deve transportar os números das notas do portal para `TipoInstituicao`: no contrato local aceito, as pastas `financial`/`individual` usam respectivamente **2/3**, e Capital/Segmentação usam **1**, conforme [README](../../README.md#consultar-a-base-ifdata) e [leitor](../../bank_quality/ifdata_odata.py). São os recortes operacionais importados. Preservar o tipo literal e a origem; o nome de pasta não certifica, isoladamente, perímetro financeiro pós-2025. Unidades e janelas OData permanecem desconhecidas quando a definição literal não as comprova.

## Reaproveitamento econômico, contábil e financeiro

A [nota de indicadores/componentes](academic-indicators-components-20261004.md#janelas-comparabilidade-e-alternativas) distingue provisão estoque de despesa fluxo, receita de resultado, PL de capital regulatório e médias de estoques. O catálogo parte das variáveis efetivamente capturadas e independe da lista anterior de candidatos; não adota fórmulas por possibilidade aritmética.

A [matriz de comparabilidade](sample-comparability-research-20261008.md#épocas-perímetros-e-versões) documenta, em recortes do portal antigo, DRE/lucro semestrais: março jan–mar, junho jan–jun, setembro jul–set e dezembro jul–dez. Logo, referência trimestral não define fluxo trimestral independente e dezembro não prova resultado anual. Esses recortes não autorizam imputar a mesma janela a todas as linhas OData. Tampouco a apresentação antiga em **R$ mil**, com formatador próprio, prova a unidade bruta deste endpoint. Unidade/janela requerem evidência por variável, referência, perspectiva e fonte; não aplicar conversões numéricas neste catálogo.

A [ponte normativa 2025](financial-2025-normative-bridge-20261004.md#matriz-normativa-e-conceitual) preserva fontes, versões e limites das CMN 2.682/4.966 e BCB 352. Sua evidência contemporânea do [BCB, nota de 13/03/2025, seção 5, pp.7–8](https://www.bcb.gov.br/content/estatisticas/hist_estatisticasmonetariascredito/202502_Texto_de_estatisticas_monetarias_e_de_credito.pdf) registra ausência de correspondência direta AA–H/estágios. Esta fatia reutiliza a pesquisa, sem reabrir os PDFs normativos nem construir de-para. Código/nome estável e passivo semelhante não certificam continuidade econômica; mudança de código também não prova, sozinha, mudança de conceito.

## Leitura do inventário factual

A chave de definição literal reúne **dataset, TipoInstituicao, NumeroRelatorio, NomeRelatorio, Conta, Grupo, NomeColuna e DescricaoColuna**. Não retirar acentos, espaços, caixa, null ou descrição para unir variantes. Grupo e Conta são campos nativos; nem o nome nem sua combinação constitui identidade econômica universal.

Por trimestre `AnoMes`, contar registros, `Saldo` null e códigos institucionais distintos; a execução deve explicitar o tratamento de `CodInst` null. Contagens de linhas não são contagens de instituições e a cardinalidade de códigos não prova população elegível ou identidade longitudinal. Saldo zero não é null; este inventário não reclassifica estados nativos nem calcula saldos agregados.

Listar os períodos observados e as lacunas dentro da janela declarada de cada dataset. **Ausência de registros** de uma definição é observação sobre o pacote aceito, não prova automática de ausência estrutural, população zero ou inexistência na fonte. Uma linha com Saldo null é presença observada com saldo ausente. Não imputar zero nem transportar uma definição de trimestre vizinho para cobrir lacuna.

Variantes de nome/descrição no mesmo código e códigos distintos com o mesmo nome são sinais para inspeção. Podem coexistir no mesmo período; a contagem de variantes não demonstra sucessão ou substituição. A marca desde2025 identifica uma fronteira documental relevante; antes2025 também não é um regime homogêneo certificado. **Comparabilidade não certificada** aplica-se a toda a saída: estabilidade literal, cobertura temporal e representatividade acadêmica são afirmações diferentes.

O inventário pode prosseguir independentemente das decisões da [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) e do aceite integral da [Issue 14](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/14). Interpretar/calcular indicadores dependentes de unidade, janela, perímetro, identidade ou versão desconhecidos continua sujeito aos respectivos contratos.

## Execução

### Execução local e checkpoints

Leitor e dados financeiros originais permanecem inalterados. Novo módulo/CLI/teste nos paths da arquitetura. TDD: quatro testes RED por recurso ausente → GREEN; revisão independente identificou inventário incompleto na abertura do catálogo; regressão RED para vazio/omissão/duplicata → correção →12testes catálogo+reader PASS, revalidação independente APP. Nenhuma expansão antes do aceite desse recorte.

Piloto financeiro:196definições/contextos e5.140linhas de cobertura, comparadas integralmente por revisão independente contra o Parquet aceito (EXCEPT ALL simétrico zero); todas as listas/contagens/extremos/variantes/flags reconstruídas e iguais. CSV/Parquet e hashes conferidos. Depois foi gerado o catálogo completo, mesmo código, quatro conjuntos:

| Conjunto | Definições/contextos | Coberturas definição/trimestre | Registros reconciliados | Saldo null |
|---|---:|---:|---:|---:|
| financial |196|5.140|7.945.863|74.909|
| individual |193|5.080|8.679.083|69.119|
| capital |37|927|1.344.190|407.450|
| segmentation |12|184|259.690|51.496|
| Total |438|11.331|18.228.826|602.974|

Saída `data/curated/ifdata-variable-catalog-20261011/`. O manifesto registra hashes dos quatro manifests aceitos e das duas tabelas em Parquet/CSV; não duplica fontes ou valores. Comandos de build/query no README. Conferência final integral completa e integração têm evidência na Issue61/PR correspondente; esta nota não substitui estado remoto.

### Colunas e interpretação

Dimensões literais: dataset,TipoInstituicao,NumeroRelatorio,NomeRelatorio,Conta,Grupo,NomeColuna,DescricaoColuna. A cobertura acrescenta AnoMes e: `registros` (todas as linhas), `com_valor` (Saldo não null, inclusive zero), `sem_valor` (Saldo null), `codigos_distintos` (CodInst não null distintos no recorte), `codigo_ausente` (linhas com CodInst null). Nenhuma soma de Saldo ou seleção de instituições.

O catálogo consolida contagens de linhas, primeira/última referência e lista exata de períodos por definição; `numero_referencias` conta períodos dessa definição. `periodos_sem_registro_entre_extremos` considera só o eixo observado do dataset entre os extremos dessa definição, não datas externas ou inexistência da variável. `variantes_no_contexto` conta definições distintas no mesmo dataset/tipo/relatório/Conta/Grupo, podendo coexistir. `codigos_com_mesmo_nome` lista códigos no mesmo dataset/tipo/relatório/Grupo/rótulo, sem uni-los. `atravessa_2025` considera os extremos de todas as variantes do contexto, não apenas da linha. `comparabilidade` permanece `nao_certificada`. As listas2010–2024 e2025–2026 preservam a separação pedida para a monografia.

### Exemplos concretos do Resumo financeiro observado

| Item | Código e definição observada | Cobertura |
|---|---|---|
| Lucro Líquido |78187, composição `[70000009]+[80000006]-[81955002]`|201003–201812,36referências|
| Lucro Líquido |78187, composição `[70000009]+[80000006]-[81956001]`|201903–202412,24referências|
| Lucro Líquido |141870, composição `[7000000003] + [8000000002] - [8195600001]`|202503–202606,6referências|
| Patrimônio Líquido |78186 e140246, mesmo rótulo, códigos/composições distintos|201003–202412 /202503–202606|
| Carteira de Crédito Classificada / Carteira de Crédito |78183 /141873, rótulos e composições distintos|201003–202412 /202503–202606|

São ocorrências literais verificadas no pacote, não um de-para econômico aprovado. Não interpretar mudança de código como alteração econômica por si só, nem continuidade de nome como prova de equivalência. Próxima análise pode selecionar componentes por tema (rentabilidade, crédito/risco, patrimônio/capital) e verificar unidade, janela, perímetro e composição antes de propor indicadores nas Issues14/3.

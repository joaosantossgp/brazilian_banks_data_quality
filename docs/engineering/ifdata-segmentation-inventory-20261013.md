# Segmentações utilizáveis na base IF.data

Diagnóstico da [Issue 113](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/113), autorizado por João após o [protocolo da monografia](institution-type-indicator-methodology-20261012.md). Base `1098a259bf81835a9faed45b545081a2dbbee4e7`, branch `codex/segmentation-inventory-20261013`. Root executa/integrará; pesquisa de dicionários delegada e revisão independente por fatia. **Inventário da população técnica, não seleção da população CVM/B3 nem revisão bibliográfica de indicadores.** A [relação histórica](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108) conserva contrato e implementação próprios.

## O que já existe e o que precisa ser construído

A base contém classificações de **tipo/consolidação, controle, segmento institucional, atividade e segmento prudencial**, além de localização cadastral e componentes financeiros. Esses eixos são distintos. Um recorte de porte por ativos pode ser construído depois; não existe corte acadêmico aprovado. Atividade da instituição não representa setor do tomador. A presença de um campo ou valor não certifica sua aplicabilidade, significado histórico ou cobertura na população elegível.

O cadastro tem cobertura trimestral geral em 2010–2024, mas campos específicos têm nulos e mudanças de categorias. **S1–S5 não cobrem 2010–2016**; `Sr` preenchido aparece a partir de 201703, com primeiras ocorrências diferentes por categoria. O relatório nativo Segmentação é uma fonte prudencial distinta do campo cadastral `SegmentoTb`.

## Fontes, integridade e denominadores

Foram lidos os datasets locais aceitos, sem reimportação, conversão, novos saldos ou alteração de entradas:

| Entrada | Conteúdo autenticado | Recorte usado |
|---|---|---|
| Cadastro temporal | 106 partes, 512.959 registros, 6.517 códigos, 200003–202606 | 303.792 registros, 6.188 códigos, 60 referências em 201003–202412; 34.973 registros, 5.901 códigos, seis referências em 202503–202606 |
| Financeiro OData (`TipoInstituicao=2`) | 66 partes, 7.945.863 linhas | Resumo, Ativo, Passivo e DRE; 201003–202606 |
| Individual OData (`TipoInstituicao=3`) | 66 partes, 8.679.083 linhas | Mesmos quatro relatórios; 201003–202606 |
| Capital OData (`TipoInstituicao=1`) | 46 partes, 1.344.190 linhas | Relatório 5, 201503–202606 |
| Segmentação OData (`TipoInstituicao=1`) | 38 partes, 259.690 linhas | Relatório 6, 201703–202606 |
| Catálogo temporal | 438 definições/contextos e 11.331 linhas de cobertura | Quatro conjuntos acima, sem harmonização por código/nome |

**Registros de cadastro são códigos por referência; não são companhias únicas.** Códigos distintos não certificam identidade jurídica longitudinal. As linhas de valores repetem unidades para variáveis; por isso a cobertura cadastral usa chaves distintas `(AnoMes,CodInst)`, ligadas a `(Data,CodInst)`, sem contar cada variável como outra instituição. Não filtrar automaticamente o cadastro pela situação, nem transportar classificações entre datas.

Hashes das partes foram conferidos contra seus manifests; os quatro manifests de valores coincidem com os pins do catálogo. Índice e resumo do cadastro coincidem com os hashes do manifest. O manifest do catálogo, inclusive arquivos CSV/Parquet, também foi conferido. **334 arquivos, 95.138.474 bytes, mantidos idênticos antes/depois da fatia A.** São verificações contra os artefatos locais aceitos, não prova de que uma nova consulta ao BCB retornaria a mesma revisão.

Execução A: Python local/DuckDB 1.5.6, uma thread, limite de consulta de 256 MB; 6,901 s medidos para o diagnóstico principal antes da conferência final dos hashes. Preflight observou aproximadamente 3,57 GiB livres numa máquina de 31,69 GiB; não foi imposto um orçamento universal a outras tarefas/máquinas. A proteção por hash não inclui todos os arquivos de outras frentes, que não foram abertos para escrita.

## Campos e valores efetivamente observados

A tabela abaixo usa **todo o cadastro do núcleo 2010–2024**, inclusive registros inativos. Valores distintos são tokens observados, não classes acadêmicas adotadas. Em todos os nove campos, as chaves existem nos JSONs e não foram observadas strings vazias; ausências nesta tabela são `null` explícito.

| Campo | Valores distintos | Preenchidos / 303.792 registros | Interpretação e limite |
|---|---:|---:|---|
| `Tcb` | 10 | 303.792 | Tipo de consolidado bancário. B1, B2, B3, B3C, B3S, B4, N1, N2, N3 e N4 observados; nem todos têm de-para comprovado nas fontes consultadas. |
| `Td` | 2 | 303.792 | Tipo de consolidação, C/I. Não identifica sozinho perspectiva financeira/prudencial ou independência societária. |
| `Tc` | 3 | 303.792 | Controle: 1 público, 2 privado nacional, 3 privado com controle estrangeiro, conforme documentação atual. Não separa federal/estadual nem certifica controlador jurídico por companhia. |
| `SegmentoTb` | 30 | 277.701 | Rótulos de segmento institucional/atuação, como banco múltiplo, corretora e IP. Não é o relatório Segmentação e não há ponte comprovada para códigos legados do portal. |
| `Atividade` | 60 | 109.067 | Rótulos da atividade da instituição, não CNAE dos tomadores; critérios detalhados e continuidade histórica não comprovados. |
| `Sr` | 5 | 32.157 | S1–S5, segmento prudencial; nulo até 201612 no recorte. Porte, internacionalidade e condições regulatórias não são apenas cinco faixas de ativo. |
| `Situacao` | 5 | 303.792 | A, I, F, LE e LO. A/I têm significado documentado; demais tokens preservados sem tradução inferida. Não define elegibilidade acadêmica. |
| `Uf` | 27 | 293.207 | Localização cadastral. Não é cobertura geográfica das operações ou clientes. |
| `Municipio` | 986 | 293.221 | Município da sede segundo D1; nomenclatura histórica e vínculo com território exigem conferência, sem classificação regional de negócios automática. |

### De-para comprovado e limites históricos

A [documentação oficial Olinda](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/documentacao), JSON embutido `especificacao.recursos` → `IfDataCadastro` → `tipo.propriedades`, sustenta as descrições dos campos e os códigos de controle/consolidação. Para `Tcb`, distingue B1/B2 (grupos bancários), B3S/B3C (cooperativas), B4 (desenvolvimento), N1 (crédito não bancário), N2 (mercado de capitais) e N4 (pagamentos). **B3 e N3 observados continuam sem de-para confirmado neste inventário**, sem inferir significado pela companhia/atividade. D1 não enumera os critérios detalhados de `Atividade`/`SegmentoTb` nem explica F/LE/LO. Documentação corrente não prova estabilidade semântica de cada token em todo o histórico.

`Td=I` é descrito como instituição independente em D1, mas não será usado sozinho para provar ausência de vínculo/controle: no dataset individual 202412, todos os 1.585 códigos com valores têm I. A existência de relação financeira/prudencial tem campos e perspectiva próprios; a equivalência de I com “fora de todo conglomerado” não está certificada.

O [dicionário primário do portal referente a 201012](https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F201012%2Finfo201012.json), corpo local autenticado SHA-256 `aa32c85142afecb62c9a5999af1ee220246d9aa1383bc416a5c251177d0f03bb`, contém `Segmento`/`TI` institucionais. A ponte direta dessas tabelas com `SegmentoTb` OData textual **não foi comprovada**. Esse mesmo arquivo inclui descrição de SR da Resolução 4.553/2017: a referência no nome do arquivo não data, sozinha, a vigência de todas as definições capturadas.

A [metodologia oficial](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf), p.2 do PDF, informa Segmentação desde 03/2017. Não foi comprovada tabela oficial de migração de atividades em 2016/2017. No cadastro há rótulos com “metodologia até dez/2016” ao lado de outros; registrar a mudança observada não permite concatenar categorias automaticamente.

### Primeiras ocorrências de `Sr` no cadastro do núcleo

| Valor | Primeira ocorrência preenchida | Referências com o token | Limite |
|---|---|---:|---|
| S1 | 201706 | 31 | Observação cadastral, não data universal de início do regime. |
| S2 | 201706 | 31 | Não completar 201703 ou períodos anteriores. |
| S3 | 201706 | 31 | Não derivar classificação pela semelhança de porte. |
| S4 | 201703 | 32 | Primeiro token Sr observado neste corpus. |
| S5 | 201812 | 25 | Ausência anterior é preservada; não prova inexistência normativa universal. |

### Cobertura depois de relacionar aos valores

Núcleo 2010–2024. “Sem cadastro” exige código presente e nenhuma correspondência na mesma referência. Código nulo é um estado separado; não representa uma unidade identificada.

| Dataset | Chaves com código presente | Com cadastro | Sem cadastro | Chaves com código nulo |
|---|---:|---:|---:|---:|
| Financeiro | 89.476 | 89.437 | 39 | 9 |
| Individual | 99.401 | 99.401 | 0 | 0 |
| Capital | 55.124 | 55.119 | 5 | 0 |
| Segmentação | 43.086 | 43.083 | 3 | 0 |

A unicidade do cadastro foi conferida; o join não multiplica as chaves. Estes números não são as contagens de **linhas de valores** sem cadastro da auditoria anterior: esta tabela conta chaves distintas. Não somar os quatro conjuntos para obter número de companhias; podem representar a mesma unidade ou perímetros relacionados.

No financeiro de **202412**, há 1.422 códigos presentes, todos com cadastro. `Tcb/Td/Tc` estão preenchidos para todos; `SegmentoTb` para 1.352, `Atividade` para 1.022 e `Sr` para 1.049. No capital de 202412, 1.367 códigos têm cadastro; `SegmentoTb` está preenchido para 782, `Atividade` para 1.302 e `Sr` para 999. **Cobertura cadastral geral não é cobertura de cada classificação nem da população CVM/B3.** Rótulo “não classificado” não vira classificação econômica válida pelo simples fato de não ser nulo.

## Matriz de recortes para orientar a pesquisa futura

**Nativo** significa atributo/abertura preservado na fonte; **derivado** exige regra a definir; **externo/ausente no corpus** requer outra evidência, sem autorização de aquisição nesta entrega. “Utilizável” é condicionado à pergunta, referência, unidade e cobertura; não certifica comparabilidade acadêmica.

| Recorte pretendido | Base disponível e natureza | Cobertura/limite demonstrado | Consequência para seleção futura |
|---|---|---|---|
| Tipo bancário/não bancário | `Tcb`, nativo | Campo preenchido nas 60 referências; dois tokens sem de-para demonstrado e regras correntes não certificam todo o passado. | Pode orientar grupos de atividade ampla; desconhecidos ficam próprios, sem inferir identidade. |
| Tipo institucional / setor da instituição | `SegmentoTb` e `Tcb`, nativos distintos | SegmentoTb tem 30 rótulos no cadastro do núcleo, com nulos; financeiro202412 tem 22 rótulos preenchidos. | Distinguir bancos, cooperativas, corretoras, IPs e outras categorias observadas; agrupamentos acadêmicos exigem regra/fonte, não equivalência por nome. |
| Atividade / modelo de negócio | `Atividade`, nativo; grupo econômico acadêmico seria derivado | 60 rótulos no núcleo, lacunas e mudanças; financeiro202412 tem 26 rótulos preenchidos. Exemplos: Crédito Atacado/Varejo/Diversificado, Tesouraria e Negócios, IP Credenciadora, IP Emissor Pré/Pós-Pago. | Pode apoiar comparações dentro da atividade; não identifica automaticamente todos os negócios de um conglomerado. Não concatenar classificações antes/depois2017. |
| Controle público/privado e nacional/estrangeiro | `Tc`, nativo | Três códigos preenchidos nas 60 referências, com de-para atual comprovado. O campo não separa público federal/estadual nem prova controlador jurídico. | Viável como atributo temporal documentado; não fixar classificação atual para todo2010–2024. |
| Conglomerado/instituição e perspectiva | `Td` mais dataset, códigos financeiro/prudencial e referência, nativos | C/I completos; I sozinho não comprova independência. Perspectivas têm populações/perímetros distintos. | Manter financeiro, prudencial e individual separados, com vínculo explícito quando necessário. |
| Porte regulatório | `Sr` e relatório Segmentação, nativos | Sr tem primeiras ocorrências201703/201706/201812 conforme categoria; relatório6 tem32referências no núcleo. | Recorte S possível somente nas ocorrências sustentadas; não é classificação exclusiva de tamanho nem solução para2010–2016. |
| Porte econômico / representatividade | Ativo Total, crédito e captações contábeis disponíveis como componentes; faixas/participações seriam derivadas | Componentes financeiros nos60trimestres, com valores nulos e definições próprias; denominador da população depende dos vínculos108. | Fonte para propor cortes após examinar distribuição; não há top-N, percentuais ou exclusão automática aprovados. |
| Internacionalidade | Controle estrangeiro (`Tc`) e ativos consolidados no exterior do relatório6, nativos diferentes | Campo monetário prudencial87071 em32referências, apenas1.681/43.086linhas não nulas. Isso não mede, por si, toda exposição internacional. | Controle estrangeiro não equivale a operar no exterior; unidades monetárias/perspectiva e lacunas precisam de contrato. |
| Localização | `Uf`/`Municipio`, nativos cadastrais | Município é sede; UF é localização da instituição. Ambos têm lacunas. | Não usar como região do crédito/clientes/atuação comercial sem evidência adicional. |
| Composição de ativos e financiamento | Rubricas de Ativo/Passivo, nativas; participações seriam derivadas | Crédito, TVM/derivativos, disponibilidades, depósitos, emissões, compromissadas e empréstimos/repasses aparecem nos relatórios locais. | Pode apoiar interpretação de modelos de negócio, sem classificar por limiar inventado ou misturar receitas e estoques. |
| Composição de receitas/despesas | Rubricas de DRE, nativas; agrupamentos/participações seriam derivados | Rendas de crédito, serviços/tarifas, intermediação, despesas de pessoal/administração/captação no núcleo; mudanças em2025 separadas. | Pode orientar rentabilidade/eficiência/financiamento; numerador, sinal, agregados e janela ainda precisam de fundamento. |
| Setor, porte e perfil do tomador | CNAE/PF-PJ/porte/modalidade/prazo/indexador/região são oferta documental do BCB; **não instalados neste corpus de relatórios** | Os quatro conjuntos e438definições conferidos contêm relatórios1–6, sem as aberturas específicas de crédito listadas emD3p.1. Busca nominal no catálogo foi auxílio, não prova isolada. | Não confundir com Atividade/SegmentoTb da instituição. Eventual necessidade exige novo escopo de dados; não coletar para completar este inventário. |
| Listagem, instrumento e setor da companhia emissora | Metadados/vínculos externos ao cadastro IF.data | Cadastro/relatórios não certificam CVM/B3 ou companhia elegível; implementação108 ainda própria. | A relação aceita permitirá aplicar os recortes à população. Não associar por ticker/nome nem equiparar setor da holding ao negócio medido. |

### Rótulos históricos e “não classificado”

As observações literais de atividade com “metodologia até dez/2016” incluem Atacado/Middle Market, Complexo, Crédito, Desenvolvimento, Montadora e Tesouraria e Negócios, presentes201003–201612. Porém o rótulo **“Não-Classificado - metodologia até dez/2016”** continua observado até202012 (741registros/32referências); “Não classificadas” aparece até202112 (1.864/48) e “Não Classificado” em201703–202412 (210/32). Não interpretar uma troca de grafia como de-para temporal nem transformar esses rótulos em atividade econômica conhecida. Nulos e rótulos não classificados são estados distintos a reportar.

## Componentes presentes nas cinco dimensões obrigatórias

Esta é uma **ponte de inventário**, sem adoção de indicadores/fórmulas. Localizadores `dataset / relatório / Conta` não substituem contexto de `Grupo`, definição, unidade ou regime. As 438 definições literais foram preservadas no extrato privado; a tabela exemplifica componentes que podem orientar a pesquisa, sem limitar a futura seleção a eles. A presença em 60 referências não comprova continuidade conceitual ou disponibilidade conjunta por companhia.

| Dimensão | Componentes localizados no núcleo2010–2024 | Referências observadas e limite |
|---|---|---|
| Rentabilidade | Financeiro/1: Ativo Total78182, PL78186, Lucro Líquido78187; DRE4: resultado/intermediação78208/78215, antes de tributos78226 | Componentes citados presentes nas60referências. Mesmo código de lucro possui mudanças de definição documentadas na pesquisa anterior; estoque, fluxo, tributos e médias não foram reconciliados aqui. |
| Qualidade do crédito | Financeiro/2: operações de crédito78191, provisão78192; DRE4: resultado de provisão78213 | Presentes nas60referências. Estoque de provisão/despesa/atraso não são equivalentes. Aberturas por atraso/risco/CNAE não estão demonstradas no corpus local; não escolher proxy para suprir lacuna. |
| Capital e alavancagem | Financeiro/1: PL78186 e AT78182; Capital/5: PR79649, RWA79665, CP79645, IB79664 e índiceCP79659 | Contábeis:60referências; prudenciais citados:40,201503–202412. Componentes prudenciais têm nulos importantes e perímetro próprio; não completar2010–2014 com índice de outra perspectiva. |
| Liquidez e financiamento | Financeiro/2: disponibilidades78188/aplicações interfinanceiras78189; Passivo3: depósitos78287, emissões78294, empréstimos/repasses78295 e demais aberturas | Componentes citados presentes nas60referências; não são uma grade de vencimentos nem comprovação de LCR/NSFR. Razão futura precisa de atividade, janela, sinal e conceito adequados. |
| Eficiência operacional | Financeiro/4: pessoal78218, administração78219, serviços78216, tarifas78217 e receitas de intermediação78208 | Presentes nas60referências; não certificam eficiência de fronteira nem comparação entre negócios diferentes. Sem fórmula, orientação ou score escolhido. |

### Presença não é completude

Para cada componente citado acima, o inventário preserva primeira/última referência, número de referências, linhas observadas, valor nulo/não nulo e código/contexto. **Linhas não são unidades únicas:** as rubricas contábeis exemplificadas de60referências têm89.489linhas cada,88.792não nulas e697nulas, incluindo linhas com código ausente. Isso não equivale à cobertura das89.476chaves financeiras identificadas, muito menos de companhias de capital aberto. Mesmo preenchimento igual entre rubricas não prova disponibilidade conjunta válida.

O **Resumo financeiro/1 também contém PR79649, índice de imobilização79662 e IB79664 em201003–201412**,20referências,33.943linhas por rubrica; PR tem33.514não nulas e IB31.905. Portanto a ausência de relatório prudencial5 antes2015 não significa ausência de qualquer informação de capital na base. Esses contextos financeiros antigos continuam separados dos prudenciais iniciados em201503; códigos iguais não autorizam emenda automática.

No capital, por exemplo, PR79649/RWA79665 têm53.799/55.124linhas preenchidas; CP79645 tem29.618 e índiceCP79659 tem29.225. Não interpretar as demais como capital zero, ausência de instituição ou inadequação regulatória. No relatório Segmentação, **86846 “Exposição Total ou Ativo Total (R$mil)”** tem42.781/43.086linhas preenchidas em201703–202412; **87071 “Ativos Consolidados no Exterior (US$mil)”** tem1.681/43.086. Exposição/ativo regulatório não é automaticamente ATcontábil, e reais/dólares não são somáveis.

A descrição da rubrica86846 declara substituição de exposição por ativo para instituições não sujeitas à apuração, conforme regra ali citada. A descrição de algumas flags menciona “Res4553/2007”, inconsistente com a referência2017 deSr: o texto nativo foi preservado, sem corrigir fonte ou implementar norma a partir dele. Flags numéricas no saldo do relatório6 não serão convertidas automaticamente em booleanos por suposição.

### Complemento2025–2026

Os seis trimestres complementares permanecem separados. Catálogo e inventário conservam novas contas/contextos, por exemplo resumo140220/140246/141870, crédito140201/140202 e exposição148474/ativos no exterior148475. Esses nomes/códigos são localizadores observados, **não uma ponte certificada** com78182/78186/78187,78191/78192 ou86846/87071. Não concatenar séries para completar cobertura ou inferir equivalência de AA–H/provisões e perdas esperadas.

## Entrega à próxima etapa e limites

O inventário permite **replanejar a pesquisa bibliográfica**, partindo de recortes nativos efetivamente observados e lacunas declaradas. A [fundamentação das cinco dimensões](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/111) continua interrompida; concluir este diagnóstico não significa retomar automaticamente a pesquisa ou adotar métricas. Assaf e literatura adequada por área serão confrontados com atividade, perímetro, componentes e cobertura, não usados para legitimar uma fórmula escolhida apenas pela disponibilidade.

A [relação histórica](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108) será necessária para aplicar os recortes à população elegível e listar **quantas e quais companhias** faltam em cada conjunto, com representatividade por período. O diagnóstico atual identifica lacunas da população técnica, sem atestar cobertura das muito representativas ou selecionar a amostra. Essa dependência não impediu a inspeção geral em leitura.

Não há classificação acadêmica de porte/modelo adotada, nova coleta, cálculo de indicador, alteração de código/dados/Word ou abertura da bibliografia. Lacunas de setor do tomador e definições históricas continuam explícitas; o inventário não promete recortes inexistentes nem elimina uma das cinco dimensões obrigatórias.

## Evidência reproduzível e estado

Preparação privada ignorada: `.scratch/ifdata-segmentation-inventory-20261013/`. `inventory_a.py` reúne queries finitas e pinning; `summary-a.json` registra entradas/recursos; `cadastro-field-period.json` e `cadastro-field-values.json` guardam 594 combinações campo/período e distribuições; `dataset-cadastro-join-period.json`, `dataset-field-period.json` e `dataset-field-values.json` preservam a cobertura das 216 combinações dataset/período. `catalog-definitions.json`, `catalog-report-summary.json` e `catalog-coverage.json` são extrações autenticadas do catálogo. `protected-before.json`/`protected-after-a.json` registram hashes dos 334 inputs. Fontes documentais, URL/UTC/status/headers/hashes e localizadores ficam em `dictionary-provenance.json`/`dictionary-notes.md`; seus corpos, cookies/headers e caminhos privados não são publicados.

Queries de reprodução, usando o leitor existente `open_cadastro` e partes autenticadas dos valores, sem alterar datasets:

```sql
-- Unidade de contagem: código e referência, sem multiplicar por variável.
SELECT DISTINCT AnoMes, CodInst FROM ifdata;
-- Correspondência temporal; jamais por nome ou última classificação conhecida.
SELECT k.AnoMes, k.CodInst, c.Tcb, c.Td, c.Tc, c.SegmentoTb, c.Atividade, c.Sr
FROM chaves k LEFT JOIN cadastro c ON k.CodInst=c.CodInst AND k.AnoMes=c.Data;
```

A fatia A estatística e a interpretação dos dicionários/nota foram revisadas independentemente antes da matriz B. A fatia B acrescenta `inventory_b.py`, `component-period-inventory.json` (421 contextos/janela), `catalog-names-core.json`, `catalog-name-keywords.json`, `activity-labels-unclassified.json`, `td-individual-links-202412.json` e `segmentation-token-values.json`. Foram preservados os334hashes em `protected-after-b.json`; o diagnóstico B levou0,338s após a autenticação inicial, com os mesmos limites de recursos. O delta focal do dicionário esclarece Uf/Municipio/Td, sem novas capturas. Scripts e JSONs de evidência permanecem privados, fora doGit.

A composição final, estado de revisão/publicação/integração e checks constam da Issue113 real; não presumir CI ou aceite de população por existir esta nota.

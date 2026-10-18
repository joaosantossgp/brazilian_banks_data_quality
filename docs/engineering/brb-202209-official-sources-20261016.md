# BRB em setembro de 2022: fontes oficiais alternativas

Revisão independente B e composição final PASS na Issue141, sem achados materiais; fontes permanecem candidatas, sem admissão automática ou indicador recalculado.

[Issue 141](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/141), busca curta em 16/10/2026. Escopo: identificar evidência para os nulos recebidos no IF.data, sem ingestão, substituição de componentes ou cálculo de indicadores. Downloads privados ficam em `.scratch/brb-202209-*`; nenhum relatório integral foi acrescentado ao Git.

## Conclusão

Há **fonte oficial contemporânea com os componentes prudenciais e índices publicados de setembro de 2022**, inclusive anexo estruturado mais detalhado que o PDF. Há também **demonstrações consolidadas Cosif** dentro do ITR versão 3. Elas são candidatas à recuperação seletiva, mas esta pesquisa não comprova identidade de perímetro com os códigos IF.data `C0080288` e `C0031976` nem autoriza importar valores automaticamente.

O nulo da captura IF.data não significa inexistência de divulgação pública. A recuperação deve preservar as duas fontes e suas versões, distinguir índice publicado de razão calculada e conferir composição temporal, conceitos, escala e precisão. Não usar a coluna individual para preencher o conglomerado financeiro.

## Prudencial: evidência diretamente pertinente

O [Relatório Pilar III 3T22](https://ri.brb.com.br/upload/files/3208_Relatorio-Gerenciamento-de-Riscos-Pilar-III-3T22.pdf), páginas físicas 3–5, identifica Conglomerado BRB, referência 30/09/2022 e reporte S3. A tabela KM1, página 4, publica CP de R$ 1.838 milhões, PR de R$ 3.309 milhões, RWA de R$ 23.059 milhões, ICP de 7,97% e Basileia de 14,35%. A página 2 avisa sobre arredondamento e recomenda consultar o anexo. Esses índices dão evidência para C4 e C3, respectivamente; não foram inseridos nos resultados.

O [anexo oficial 3T22](https://ri.brb.com.br/upload/files/3261_3T22-Anexo-do-Relatorio-Gerenciamento-de-Riscos-Pilar-III.xlsx), aba `KM1`, conserva os seguintes **tokens literais do XML**, extraídos sem conversão para float. Montantes estão em R$ milhões; índices são frações formatadas como porcentagem:

| Conceito | Célula | Token XML literal |
|---|---|---|
| Capital principal | E9 | `1838.0376052700001` |
| Nível I | E10 | `2125.5680116200001` |
| Patrimônio de referência | E11 | `3308.9411171500001` |
| RWA total | E15 | `23059.334440619998` |
| Índice de capital principal | E17 | `7.9709048411745087E-2` |
| Índice de Nível I | E18 | `9.2178203022014446E-2` |
| Índice de Basileia | E19 | `0.14349681798799707` |

O serial da célula E7 representa setembro/2022 usando dia 1; a data de encerramento é estabelecida pelo PDF, não inferida como saldo em 01/09. As caudas numéricas do Excel são propriedades dos tokens publicados e **não certificam precisão econômica adicional** nem autorizam arredondamento silencioso ao centavo. Não houve divisão de montantes para gerar novo indicador.

O [Pilar III 1T23](https://ri.brb.com.br/upload/files/3297_Pillar-III-Risk-Management-Report-1Q23.pdf), KM1 página 4, confirma retrospectivamente os mesmos montantes arredondados e índices de setembro/2022. Seus comparativos de outras datas não são idênticos em todos os campos ao relatório 3T22; usar a versão contemporânea para este diagnóstico e preservar revisões.

## Financeiro: candidato Cosif, sujeito a confronto do perímetro

O [ITR 3T22, versão 3](https://ri.brb.com.br/upload/files/0740_ITR-3T22.pdf) tem 106 páginas físicas. As primeiras tabelas são individuais. Entretanto, o anexo a partir da página física 35 contém demonstrações **BRB-Múltiplo e BRB-Consolidado**. A nota 2, páginas físicas 45–46 (impressas 44–45; internas 11–12/68), declara práticas brasileiras aplicáveis às instituições autorizadas pelo BCB/Cosif, eliminações intragrupo e participação de não controladores separada. Não é necessário supor equivalência IFRS. A aprovação dessas demonstrações é datada de 15/12/2022 na página física 46; a data de entrega da versão 3 não foi apurada nesta busca.

Coluna **BRB-Consolidado / 30.09.2022**, valores publicados em **R$ mil**:

| Conceito publicado | Valor | Localizador físico; interno |
|---|---:|---|
| Ativo total | 40.200.756 | p.37; 3/68 |
| Disponibilidades | 244.227 | p.37; 3/68 |
| Aplicações interfinanceiras | 1.700.171 | p.37; 3/68 |
| Operações de crédito | 29.918.942 | p.37; 3/68 |
| Provisão de crédito, rubrica específica | (745.788) | p.37; 3/68 |
| Depósitos totais | 25.063.311 | p.38 e p.74; 4/68 e 40/68 |
| Depósitos à vista | 1.347.402 | nota 18, p.74; 40/68 |
| PL atribuído ao controlador | 2.131.886 | p.38; 4/68 |
| Participação de não controladores | 339.196 | p.38; 4/68 |
| PL incluindo não controladores | 2.471.082 | p.38; 4/68 |
| Lucro atribuível a todos os acionistas, 3T22 efetivo | 71.147 | p.39; 5/68 |
| Lucro atribuível a todos os acionistas, janeiro–setembro | 261.672 | p.39; 5/68 |
| Lucro do controlador, 3T22 efetivo / janeiro–setembro | 59.273 / 249.798 | p.39; 5/68 |

Os números não são tokens em reais de precisão nativa IF.data. A composição consolidada lista banco, financeira, DTVM, cartões, seguros, serviços, participações e fundo: **não assumir que todas essas entidades pertençam ao conglomerado financeiro IF.data**. A tabela DRE distingue lucro do controlador, resultado dos não controladores e total atribuível; a seleção exige conferir a fórmula nativa. Janeiro–setembro não pode ser usado como julho–setembro nem julho–dezembro. Aplicações interfinanceiras e disponibilidades têm boa correspondência nominal com L2, mas a agregação contábil e o perímetro ainda precisam ser confrontados. Assim, L2 e demais relações financeiras têm **fonte candidata**, sem recuperação exata já demonstrada.

## Proveniência, inspeção e limite da busca

Os links foram obtidos na [central oficial com ano 2022](https://ri.brb.com.br/pt/central-de-resultados?ano=2022) e na [página oficial de gestão de riscos com ano 2022](https://ri.brb.com.br/pt/relatorio-de-gestao-de-risco?ano=2022). O seletor de ano é documentado pelo JavaScript do próprio site como `?ano=`. Não houve chamada à API IF.data nem ao projeto CVM separado.

| Arquivo privado | SHA-256 |
|---|---|
| `brb-202209-pilar.pdf` | `cb8a621391f4064128d4fec97c9d75e54543c3d14a68720974a4ce880c126a72` |
| `brb-202209-anexo.xlsx` | `f35507ff63d1b075e291173cec55709fcf14e3a6e581de98e8ff22ef0ebf2965` |
| `brb-202209-itr.pdf` | `dab4666844f10eb25424edb61d2ceda2ad20b5014cd6b760986bd37928225451` |
| `brb-202209-2.pdf` (Pilar 1T23 retrospectivo) | `405ee5859328689c56e3fba6d707368f338882cf597a4f9f2ce6a5d7c0a1e948` |

`.scratch/brb-202209-provenance.json` registra URL, status HTTP 200, headers, recuperação UTC, tamanho recuperável pelo arquivo e SHA-256. Os PDFs completos foram extraídos com `pdfplumber`; páginas 37 do ITR e 4 do Pilar foram renderizadas com `pypdfium2` e inspecionadas visualmente. Tokens relevantes do anexo foram extraídos do XML para `brb-202209-km1-tokens.json`; nenhuma macro foi executada. Sem instalar dependências ou modificar dados aceitos. A busca foi encerrada após localizar evidência suficiente; não declara inexistência de outros balancetes, relatórios ou versões oficiais.

Esta nota cobre fontes. O diagnóstico local de componentes, indicadores afetados e toda a janela de dependências fica na [nota de confronto](brb-202209-alternative-source-20261016.md), sob responsabilidade da implementação principal. Evidência de fonte alternativa não é aceite de método novo nem substituição operacional.

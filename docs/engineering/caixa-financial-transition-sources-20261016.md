# Fontes primárias da transição financeira da Caixa em 2021

Pesquisa local da [Issue 146](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/146), em 16/10/2026. Escopo: subsidiária DTVM, datas e limites de uma ponte de LL/AT/PL; nenhuma coleta foi incorporada à base aceita e nenhum indicador foi recalculado. O parecer e o confronto dos dados IF.data ficam na nota [da transição](caixa-financial-transition-2021-20261016.md).

## Cronologia documentada

A DTVM, CNPJ 42.040.639/0001-40, foi constituída em **14/04/2021**, como subsidiária integral da Caixa. Portanto, sua entrada no cadastro IF.data em setembro não permite concluir que seus ativos e resultados fossem zero em junho. Na própria demonstração de 2T2021, o balanço informa AT de **R$ 50,346 milhões**, PL de **R$ 50,190 milhões** e passivo fiscal de **R$ 156 mil**; a DRE informa lucro de **R$ 183 mil**, no período de 14/04 a 30/06. O capital de R$ 50 milhões foi integralizado em títulos públicos; os custos de constituição e operação até junho foram assumidos pela controladora. Fontes: [DTVM 2T2021](https://www.caixa.gov.br/Downloads/caixa-dtvm/DemonstracoesFinanceiras2Trimestre2021.pdf), pp. 12–13, 17, 21 e 24. A DRE da p. 13 foi também conferida visualmente.

A autorização do BCB ocorreu em **27/09/2021**. A receita de serviços da DTVM começou em **novembro de 2021**, com a migração da gestão dos fundos antes realizada pela Caixa: 271 fundos em novembro e os demais em dezembro, totalizando 383. O patrimônio dos fundos sob gestão não deve ser somado ao ativo próprio da DTVM. Fontes: [DTVM 4T2021](https://www.caixa.gov.br/Downloads/caixa-dtvm/DemonstracoesFinanceiras4Trimestre2021.pdf), pp. 4–5, 21–22 e 30. A nota de capital, pp. 27 e 29, identifica os títulos federais e sua posterior aplicação no fundo exclusivo Ibirapuera em julho.

## Diferença que impede certificar equivalência exata em junho

| Informação, em R$ mil | Caixa 2T2021, nota de investimentos | DTVM 2T2021 própria |
|---|---:|---:|
| Investimento da Caixa / PL da DTVM | 50.122 | 50.190 |
| Equivalência patrimonial / lucro da DTVM | 114 | 183 |

A tabela da [Caixa 2T2021](https://www.caixa.gov.br/Downloads/caixa-demonstrativo-financeiro/BrGaap_Demonstracoes_Contabeis_2T21.pdf), **p. 47**, informa investimento de R$ 50,122 milhões e equivalência de R$ 114 mil tanto no trimestre quanto no semestre. São diferenças de R$ 68 mil e R$ 69 mil frente à DF própria. A busca textual nas DF Caixa 2T e 3T por defasagem, mês anterior e expressões semelhantes não identificou explicação conclusiva. Não atribuir a diferença a arredondamento, defasagem ou erro como fato comprovado. A DF DTVM 2T registra autorização à publicação em 25/02/2022, p. 17; a diferença de versões/datas é uma possibilidade a esclarecer, não uma conciliação demonstrada.

Em setembro, a [Caixa 3T2021](https://www.caixa.gov.br/Downloads/caixa-demonstrativo-financeiro/BrGaap_Demonstracoes_Contabeis_3T21.pdf), p. 48, informa investimento DTVM de R$ 50,531 milhões, equivalência trimestral de R$ 410 mil e acumulada de R$ 524 mil; a p. 49 registra a conclusão da autorização. Isso reforça a existência do vínculo, sem resolver retrospectivamente junho.

## Perímetros e alternativas

O **consolidado público da companhia** não equivale automaticamente ao **conglomerado financeiro IF.data**. A Caixa 3T2021, p. 12, inclui CAIXAPAR, Loterias, Cartões, Seguridade, DTVM e FIDC Stone III, eliminando saldos, receitas, despesas e lucros internos. A p. 74 reconcilia PL individual de R$ 76,152 bilhões e consolidado de R$ 111,570 bilhões, principalmente por IHCD elegível a capital e participação de não controladores. Substituir a série IF.data pela coluna consolidada introduziria outra mudança contábil e de perímetro.

Uma **continuidade do perímetro efetivamente observado** pode usar o banco como predecessor e o conglomerado a partir da mudança, preservando código, data e marcação da mudança. Isso constitui uma aproximação metodológica documentada, não prova de identidade centavo a centavo. Já reconstruir um **perímetro constante retrospectivo** exigiria DTVM, investimento, equivalência e eliminações compatíveis em junho. Não basta somar AT/PL/LL das duas entidades: haveria dupla contagem do investimento e do resultado por equivalência. O passivo DTVM de R$ 156 mil serve apenas como cenário residual antes de conferir todos os ajustes; não é uma diferença consolidada comprovada.

## Proveniência e limites

PDFs públicos recuperados por HTTPS e guardados somente em `.scratch/caixa-transition/`. Extração com pypdf do runtime já disponível; sem instalação. Páginas são do PDF, em numeração iniciada em 1. Valores publicados em milhares não certificam a precisão de centavos dos tokens IF.data.

| Arquivo privado | Recuperação UTC em 16/10/2026 | SHA-256 |
|---|---|---|
| caixa-2t2021.pdf | 21:55:47Z | `3716079d6e8e1d85fe0cd7084d91aa71655936d2a4bffe0f31444feaa3730241` |
| caixa-3t2021.pdf | 21:53:30Z | `36f0ebd25daa5bc0a1222c2e4b3bc8eee11dfb3d8196340da0376742a5678481` |
| dtvm-2t2021.pdf | 21:54:55Z | `b86c09e855f2488927b1ec969cbb2e35f98406406087e1632cd5f7e95c4d3f67` |
| dtvm-3t2021.pdf | 21:54:56Z | `3e0d6e00b73bd8072e46e45e3a8125cea5976e8ae74857ab44e46293c4b517ba` |
| dtvm-4t2021.pdf | 21:53:31Z | `8d1a1575cb43414b510f066c4d731fead9f3d5ea5a189be31203b3b304233fa3` |

A [página oficial da Caixa Asset](https://www.caixa.gov.br/caixa-asset/Paginas/default.aspx) forneceu os links. O PDF DTVM 3T usa o mesmo diretório e nome `DemonstracoesFinanceiras3Trimestre2021.pdf`; foi extraído como apoio. A tentativa do ZIP oficial 2T2022 retornou **HTTP 429** às 21:54:57Z; não se interpretou a falha como ausência da informação e não houve insistência. O navegador de pesquisa encontrou redirecionamento circular nos PDFs; a recuperação HTTPS direta dos cinco PDFs acima funcionou. O diagnóstico de 2022 usa os valores nativos já admitidos, sob responsabilidade da nota principal. Nenhuma ponte foi adotada nesta pesquisa.

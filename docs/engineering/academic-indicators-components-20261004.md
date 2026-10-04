# Indicadores acadêmicos: fontes, componentes e lacunas

Pesquisa da [Issue 14](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/14), em 2026-10-04, sobre `main` `17fbf474320078af0769ee3f3fc664f5697565a4`, branch `codex/issue-32-historical-frontier`. A nota prepara alternativas para a [decisão humana na Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3). Seu destino é `docs/engineering/`, conforme a [arquitetura](../architecture.md#organização-dos-arquivos-e-pastas); nenhuma camada ou contrato de dados novo é criado.

**Resultado e limite material:** o histórico da Issue 14 registra sete candidatos revisados, sete extensões e nove testes semânticos propostos, mas não enumera a proposta integral. A consulta ao corpo/comentários das Issues 14 e 3 e a busca dirigida nas notas locais de preparação/publicação não recuperaram essa lista nem suas fórmulas completas. Portanto, esta nota consolida somente conceitos explicitamente rastreáveis nesses registros e nas fontes; não reconstrói os sete candidatos nem declara a proposta integral concluída. Recuperar o artefato corrigido de 2026-10-03 e seu complemento é requisito para conferir nomes, versões e componentes de cada candidato. [Issue 14]

Não houve cálculo de indicadores, escolha de amostra/método ou nova aquisição de valores, cadastros ou dicionários IF.data. Fonte documental adicional não é indicador adicional aprovado. Pesquisa, revisão técnica, aceite da proposta e adoção metodológica são etapas distintas.

## Fontes e localizadores conferidos

| Referência primária | Localizador e evidência usada | Alcance |
|---|---|---|
| [Lima, Fonseca, Silveira e Assaf Neto (2018)][L] | RAC 22(2), pp.178–200; tabela 4, p.190, PDF página 13; metodologia pp.187–189 e discussão do GAP p.189 | Fórmulas do artigo; dados trimestrais Economática/BR GAAP. Não demonstra disponibilidade equivalente em IF.data. |
| [BCB, REB 2020][B20] | Tabela 4, p.159, PDF página 159; contexto pp.157–158 | Capitalização Cosif ajustada; provisões/crédito SCR em recorte banco/modalidade/localidade/tempo. |
| [BCB, REB 2023][B23] | Capítulo 4, p.49, nota 24, PDF página 49 | Definição do ROE anual publicado pelo BCB. |
| [FMI, FSI Compilation Guide (2019)][F] | Capítulo 7, §§7.46–7.55, pp.90–91, PDF páginas 106–107; sumário e título conferidos | Referência complementar para ROA/ROE e médias de estoques; não valida adaptação IF.data. |
| [Contrato financeiro 202412][C] e [execução da admissão][E] | `1005/92/202412`; mapa de métricas, pointers D/O e cobertura; [perfil fechado][P] `/report/rp` e `/metrics` | Evidência local aceita para seis montantes e duas quantidades, exclusivamente nesse snapshot. |

Publicação do artigo é **2018**; aprovação em 2017 não altera o ano bibliográfico. Assaf Neto (2015) e Marion (2009), citados como pendência na Issue 14, permanecem sem edição/página operacional comprovada nesta pesquisa. A [página do próprio Instituto Assaf][A] descreve análise de bancos na Parte V, mas não fornece as páginas/fórmulas das edições requeridas. Não usar referências de terceiros para preencher essa lacuna. [L], [Issue 14], [A]

## Conceitos recuperáveis: fórmula da fonte e adaptação pendente

Esta tabela é um mapa de evidências, **não a lista recuperada dos sete candidatos**. AT = ativo total; PL = patrimônio líquido; LL = lucro líquido; PDD = provisão para devedores duvidosos; AS/PS = ativos/passivos sensíveis. Os quocientes monetários são adimensionais, desde que componentes tenham escala compatível; apresentação em percentual exigiria convenção explícita. Estoques usam a mesma data; fluxos usam a mesma janela.

| Conceito citado na Issue 14/3 | Fórmula e recorte da fonte | Componentes e adaptação a esclarecer | Cobertura efetivamente demonstrada |
|---|---|---|---|
| Crédito/depósitos, dimensão liquidez | Operações de crédito / depósitos, tabela 4. [L] | Estoques de crédito e depósitos na mesma unidade/data; conciliar crédito bruto/líquido e rubricas do denominador. Captações não são automaticamente depósitos. | Existe carteira classificada `78183`; o Resumo admitido não possui depósitos separados. Equivalência da carteira ao numerador da fonte e cobertura bilateral desconhecidas. [C], [E] |
| Provisão/crédito, dimensão qualidade do ativo | PDD / operações de crédito, tabela 4. [L] REB usa volume de provisões / volume de crédito no SCR. [B20] | Estoque da provisão, sinal apresentado, crédito bruto/líquido e abrangência da carteira exigem prova. Despesa com provisão é fluxo distinto; não trocar numeradores. | Provisão não está nas oito métricas admitidas. Carteira classificada isolada não comprova denominador equivalente nem cobertura da razão. [C], [E] |
| Margem líquida, dimensão desempenho | LL / receitas de intermediação financeira, tabela 4. [L] | Dois fluxos da mesma janela/perímetro/regime; demonstrar rubricas de receitas. Receita e resultado de intermediação não são substitutos automáticos. | LL `ifd=79718`, `lid=78187` é julho–dezembro; receitas não fazem parte do Resumo admitido. Razão anual não demonstrada. [C], [P] |
| GAP, exposição a juros | **AS / PS**, tabela 4. [L] | Estoques bilaterais, critérios de sensibilidade e composição das carteiras exigem mapeamento. Não converter em AS−PS ou diferenças por faixas. | Nenhum dos dois agregados sensíveis está admitido. AT e passivo total não substituem AS/PS. Cobertura desconhecida. [C], [E] |
| Capitalização contábil | PL **ajustado** / AT **ajustado**, tabela 4. [B20] | Dois estoques na mesma data/perímetro; explicitar ajustes. PL/AT sem ajustes seria adaptação contábil distinta, sujeita à Issue 3. | PL `78186` e AT `78182` disponíveis por variável; ajustes não demonstrados. Isso não comprova reprodução da medida BCB ou adequação prudencial. [C], [E] |
| ROE: return on equity, retorno sobre patrimônio | LL em doze meses / média do PL ajustado dos treze meses findos em dezembro, nota 24. [B23] | Fluxo anual e série mensal ajustada; média trimestral ou abertura/fechamento é alternativa metodológica distinta. | Apenas LL semestral e PL da referência estão admitidos nesse recorte. Não há série mensal ajustada ou numerador anual comprovado. [C], [E] |
| ROA: return on assets, retorno sobre ativos | FMI: resultado líquido, preferencialmente **antes dos tributos**, / ativo total médio; §§7.47–7.48. [F] | Referência complementar, sem atribuir essa definição à proposta perdida. Numerador IF.data e ajustes precisam ser conciliados; LL não prova equivalência ao resultado antes de tributos. | AT pontual disponível; numerador equivalente, médias e cobertura anual desconhecidos. A fonte operacional específica da proposta permanece pendente. [C], [E], [Issue 14] |

**Reserva contábil de liquidez:** a Issue 14 menciona falta de fonte operacional específica. Nome, fórmula exata, componentes, eventuais restrições aos ativos e denominador da proposta original continuam desconhecidos. Não inferir uma composição nem substituir por LCR, que o REB 2020 identifica separadamente como indicador de Basileia III. Sem a proposta original e a página primária, unidade/janela/perímetro e cobertura deste conceito não são verificáveis. [Issue 14], [B20]

## O que as oito métricas provam

O perfil fechado usa perspectiva **1005, Conglomerados Financeiros e Instituições Independentes**, relatório **92**, referência **202412**. Não representa automaticamente emissor/holding, consolidado societário ou todos os bancos elegíveis. Cada ocorrência precisa de vínculo datado; as [oito relações históricas ainda desconhecidas](capital-aberto-identity-dossier.md) permanecem desconhecidas. [C], [Issue 3]

| Métricas admitidas | Localizadores do dicionário D / células | Unidade/janela | Cobertura por variável na admissão |
|---|---|---|---|
| AT; carteira de crédito classificada; passivo circulante/exigível a longo prazo/resultados futuros; captações; PL | D `/455..459`; `ifd=lid=78182..78186`, respectivamente | BRL bruto inferido do formatador do portal; estoques em 31/12/2024 inferidos do conceito | Cada variável: 1.415 células numéricas armazenadas / 1.422 registros cadastrais. [C], [E] |
| LL | D `/605`; `ifd=79718`, `lid=78187` | BRL bruto inferido; **01/07–31/12/2024**, nota `rp` 1 | 1.415 / 1.422. [C], [E], [P] |
| Agências; postos de atendimento | D `/591..592`; cadastro `c16`, `c17` | Contagens cadastrais na referência | Cada variável: 1.422 / 1.422. [C], [E] |

São **11.334 observações admitidas**: 8.490 montantes e 2.844 quantidades; **42 posições monetárias sem armazenamento** ficam na cobertura. Cinco entidades não armazenadas e duas sem cada localizador monetário não são NI/NA ou zero observados. Zeros reais de crédito/captações permanecem zeros; tratamento de denominador zero ou PL negativo pertence ao método, sem exclusão automática. [C], [E]

Cobertura por variável não é cobertura de indicador, banco/ano ou amostra acadêmica. Esta pesquisa não reprocessou observações nem mediu interseções analíticas; a tabela resume os ledgers aceitos. Não há prova neste recorte de depósitos, provisões, receitas de intermediação, ativos/passivos sensíveis, componentes ajustados ou médias históricas. Ausência no Resumo admitido não comprova ausência em todos os relatórios IF.data. [C], [E]

## Janelas, comparabilidade e alternativas

1. **Fluxos:** o `rp` define março/junho como janeiro–março/janeiro–junho, e setembro/dezembro como julho–setembro/julho–dezembro. Dezembro isolado não é anual; somar quatro saldos trimestrais acumulados duplicaria parcelas. Junho + dezembro é somente possibilidade condicionada a notas, rubricas, vintages e perímetro compatíveis, ainda sem comprovação financeira histórica. [P], [C], [Issue 3]
2. **Médias:** a Issue 3 conserva alternativas de média trimestral trapezoidal e média abertura/fechamento para ROA/ROE. Ambas, como ali propostas, exigem abertura comparável; **200912 seria insumo de abertura de 2010 se esse método for escolhido**, sem alterar automaticamente a janela acadêmica 2010–2024 nem autorizar coleta. O FMI aceita abertura/fechamento como mínimo e encoraja maior frequência; não prescreve aqui a aproximação trimestral proposta. [Issue 3], [F] §7.48
3. **ROE BCB:** a média de treze meses de PL ajustado exige componente/frequência próprios. Uma média trimestral de PL contábil não reproduz automaticamente o REB 2023. Comparabilidade econômica e de consolidação precisa ser provada, mesmo com divisão aritmética possível. [B23], [C]
4. **Perfil agregado:** média/mediana dos índices por instituição e razão das somas são escolhas distintas, mantidas na Issue 3. Não escolher pesos, eliminar faltantes, winsorizar ou definir elegibilidade nesta nota. O [glossário](../../GLOSSARY.md) separa ocorrência, unidade analítica, janela e vintage. [Issue 3]

Equivalência de rubricas, sinais, composição e consolidação não segue de nomes iguais. A [comparabilidade de 2025](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16) tem escopo próprio; esta pesquisa não costura regimes/perspectivas ou promove dados individuais existentes a cobertura financeira histórica.

## Três perguntas para João/orientador — Issue 3

1. **População/unidade:** qual critério temporal de capital aberto (CVM/B3) e qual unidade financeira vinculada a emissor/holding serão adotados? Conservar os oito vínculos desconhecidos até prova datada; cadastro técnico não decide elegibilidade.
2. **Método anual/perfil:** qual janela de resultado, numerador (incluindo tributos/ajustes), média de estoques e agregação do perfil serão adotados? Especificar necessidade de abertura 200912 e compatibilidade de junho/dezembro; obter fonte/página para adaptações antes de calcular.
3. **GAP:** operacionalizar AS/PS com componentes bilaterais comprovados, ou reformular o objetivo quantitativo? Diferença por faixas requer outro fundamento e decisão própria.

A recuperação da proposta corrigida e do complemento bibliográfico é uma lacuna de entrada, anterior à comparação completa dos sete candidatos. Esta nota é revisável como pesquisa de fontes/componentes e desconhecidos; não satisfaz sozinha o aceite integral da proposta, a escolha da Issue 3 ou uma autorização de implementação.

## Verificação e estado

Foram lidos AGENTS, arquitetura, glossário, contrato da Issue 14 e decisão da Issue 3, sem comentários adicionais retornados; perfil fechado, contrato/ledger de admissão e registro privado da revisão anterior foram conferidos. Matt `research` foi aplicado como pesquisa por agente dedicado; Feynman `pdf-explore` foi aplicado à leitura cruzada de métodos/tabelas/notas por ferramentas PDF disponíveis, sem instalação ou execução alegada de deep-research.

Os PDFs de Lima/FMI/REB 2023 e seus localizadores foram conferidos via consulta documental; a consulta web do REB 2020 falhou em leituras posteriores, então seu PDF oficial foi lido localmente com `pypdf` do runtime já disponível. Documento de 253 páginas, SHA-256 `295250c29a4f8c14785a0de2e2bd2a92075ad046a9a82eec1a8fc9fb5adbbf1c`, consulta em 2026-10-04. Extrações/proveniência ficam na preparação privada; nenhum valor bancário foi publicado. Links e correspondência com o perfil são checks documentais; testes de software não se aplicam a esta nota.

Revisão independente e publicação desta nota devem ser confirmadas na Issue/PR real pelo integrador. Não são afirmadas aqui. A lista original, fontes/páginas Assaf/Marion, mapeamentos operacionais e cobertura analítica continuam pendentes; nenhum indicador foi implementado ou calculado.

[Issue 14]: https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/14
[Issue 3]: https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3
[L]: https://www.scielo.br/j/rac/a/ZPMKdbB7pSn3hBB7Rs8XkYL/?lang=pt
[B20]: https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb_2020.pdf
[B23]: https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb2023p.pdf
[F]: https://www.imf.org/-/media/files/data/2019/2019-fsi-guide.pdf
[A]: https://www.institutoassaf.com.br/product/estrutura-e-analise-de-balancos/
[C]: financial-snapshot-202412-contract-20261003.md
[E]: financial-snapshot-202412-execution-20261003.md
[P]: ../../bank_quality/financial-profile-202412.json

# Complementos individual e prudencial — inventário para revisão

[Issue62](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/62), [claim limitado](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/62#issuecomment-6100830679), 2026-10-10. **Fatia1 PARA REVISÃO; sem opções finais, conteúdo escolhido ou aquisição.** Pesquisador delegado, base de leitura `030a102d5613d4c9a100da1369060e378d721f5c`; escrita somente nesta preparação privada. O integrador é responsável pelo destino público aprovado `docs/engineering/complements-content-options-20261010.md`, após handoff77. Matt research aplicado por agente; verification-before-completion para evidência; leitura documental PDF conforme pdf-explore já utilizada nesta sessão. Sem instalar ferramentas ou alegar slash command.

AGENTS/workflow/arquitetura/glossário e spec do modelo lógico mantêm financeiro principal e individual/prudencial complementares separados. Alvo técnico2010–2026 não muda monografia2010–2024; seleção de conteúdo é decisão de João na62, distinta de método/amostra na3. #63 permanece dependente da escolha; não dimensionada aqui.

## Fontes locais autenticadas

O/N abaixo são catálogos primários BCB **arquivados**, lidos offline; URLs identificam proveniência, não GET novo. Cada manifest resolveu seu `body_path` na própria pasta. Nesta fatia: SHA-256 e tamanho do corpo conferidos contra manifest, parsing JSON integral, `http_status=200`, `outcome=ok`, `truncated=false`. Hash do manifest calculado para handoff, sem afirmar assinatura/autenticidade do publicador. Não imprimir headers/cookies nem publicar corpos.

| Fonte | Manifest local / corpo adjacente de mesmo stem `.bin` | SHA-256 manifest / corpo | Recuperação UTC / bytes |
|---|---|---|---|
| O, [2000–2024](https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024) | `data/raw/financial-cadaster-202412-20261003/20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json` | `b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7` / `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` | 2026-10-03T20:42:19.737446+00:00 / 13.527.657 |
| N, [2025–2030](https://www3.bcb.gov.br/ifdata/rest/relatorios2025a2030) | `data/raw/expansion-discovery-20261001/20261001T025532086391Z_current_catalog_96354c8529f24aa3822eeb07c6c3a2ce.json` | `8ab9f7f82eed8d7103525d3fb7c64e4d5150fd17a6caf6f07a6df00bc7b3bf12` / `b8977d383e4ea51f56ed391571aca7af1c109b83b9c17ceef8b926841d658206` | 2026-10-01T02:55:33.366905+00:00 / 1.649.748 |

Layout: array de referências `/q/dt`, arquivos `/q/files/f`; `trel.id/n` identifica relatório, `trel.s` é **lista** de objetos com `id` de perspectiva; `c` contém estrutura/bindings, `cp` apresentação, `rp` notas. A primeira tentativa exploratória tratou `s` como objeto e foi corrigida antes de inventariar; não houve escrita de código/dados. Inventário posterior percorreu cada elemento da lista; uma mesma estrutura pode anunciar mais de uma perspectiva. Namespaces preservados; espaços finais nos nomes foram ignorados somente no agrupamento documental, sem reescrever fontes. Ausência de duplicata perspectiva/família/referência foi conferida neste agrupamento.

O `/40..99` anuncia60 referências201003–202412; N `/0..5`, seis202503–202606. Dentro desse recorte, os intervalos das tabelas incluem `{03,06,09,12}`. Não aparecem202609/202612 na capturaN; não se infere estado atual do endpoint, disponibilidade definitiva ou aquisição. N não fornece todos os anos do nome2025–2030.

## Quatro famílias contábeis: oferta por perspectiva

IDs abaixo na ordem **Resumo / Ativo / Passivo / DRE**; são relações nativas do catálogo, sem correspondência econômica entre épocas. Pointers são zero-based do corpo identificado, e não promessas sobre endpoint futuro.

| Perspectiva / referências | IDs nativos | Quantidade de referências anunciadas / localizadores |
|---|---|---|
| Individual1006,201003–201812 | 76 /77 /78 /79 | 36; O `/40..75/files/*/trel`; primeiro `/40/files/12..15/trel` |
| Individual1006,201903–202003 | 93 /77 /78 /94 | 5; O `/76..80`; início `/76/files/30,23,24,31/trel` (ordem das famílias) |
| Individual1006,202006–202412 | 93 /77 /100 /94 | 19; O `/81..99`; extremo202412 `/99/files/29,27,11,30/trel` |
| Individual1006,202503–202606 | 120 /106 /109 /117 | 6; N `/0..5`, primeiro `/0/files/22,12,15,19/trel` |
| Prudencial1004,201403–201412 | 75 /3 /4 /5 | 4; O `/56..59`, primeiro `/56/files/15,11,12,13/trel` |
| Prudencial1004,201503–201812 | 1 /3 /4 /5 | 16; O `/60..75`, início `/60/files/10..13/trel` |
| Prudencial1004,201903–202003 | 90 /3 /4 /91 | 5; O `/76..80`; primeiro Resumo `/76/files/27/trel`, DRE `/76/files/28/trel` |
| Prudencial1004,202006–202306 | 90 /3 /99 /91 | 13; O `/81..93`; primeiro Passivo `/81/files/35/trel` |
| Prudencial1009,202309–202412 | 104 /111 /112 /113 | 6; O `/94..99`, início `/94/files/15..18/trel` |
| Prudencial1009,202503–202606 | 121 /105 /108 /116 | 6; N `/0..5`, início `/0/files/23,11,14,18/trel` |

Individual anuncia66 referências para **cada** família,60 na janela acadêmica. Prudencial1004 anuncia38 por família,1009 anuncia12; agrupamento descritivo50 referências,44 até202412. **Não** cria identidade, continuidade ou ponte1004↔1009, nem50 snapshots aceitos. Prudencial2010–2013 não aparece nesse recorteO. Troca de ID isolada não demonstra mudança contábil, permanência não demonstra equivalência.

## Outras famílias observadas e seus limites

| Família / perspectiva | Oferta observada / IDs / localizadores | Limite de interpretação |
|---|---|---|
| Informações de Capital,1004 | 201503–202212:6 (32refs);202303–202306:114 (2refs). O primeiro `/60/files/14/trel`;114 `/92..93/files/14/trel`. | Capital prudencial tem início distinto dos quatro relatórios contábeis; não projetar série desde2010. |
| Informações de Capital,1009 | 202309–202406:103 (4refs),202409–202606:115 (8refs). O `/94/files/14/trel`, `/98/files/18/trel`; N `/0..5/files/17/trel`. | São46 referências prudenciais anunciadas ao agrupar1004/1009, sem ponte econômica/perímetro. |
| Segmentação,1004 | 201703–202306:80 (26refs); primeiro O `/68/files/29/trel`. | Classificação não é condição automática de amostra ou valor monetário. |
| Segmentação,1009 | 202309–202412:102 (6refs);202503:122 (1);202506–202606:131 (5). O `/94/files/13/trel`; N `/0/files/24/trel`, `/1..5/files/32/trel`. | Agrupamento38refs. A troca122→131 existe na oferta; equivalência entre estruturas não conferida. |
| Crédito SCR,1009 | Oito famílias,6refs cada,202503–202606: PF modalidade/prazo123; clientes/operações124; indexador125; região126; PJ porte127; PJ modalidade/prazo128; PJ CNAE129; carteiras de instrumentos130. N `/0/files/25..32/trel`; `/1..5/files/24..31/trel`. | Notas de130 distinguem SCR de Cosif: não eliminam transferências intragrupo e restringem o perímetro a financeiras/pagamento autorizadas. Não equivale a todos os membros do prudencial contábil; carteiras não são automaticamente estágios. |
| Crédito anterior e câmbio, contexto externo ao complemento1006/1004/1009 | O observa crédito sob1008 em201203/201206–201403 (IDs82–89), sob1005 em201406/201409–202412 (62,64–68,71,73); câmbio1007/70 em201412–202409. | Não atribuir esses dados ao individual ou prudencial por nome de relatório. Nenhuma inclusão proposta nesta fatia. Intervalos divergem de algumas descrições genéricas; conservar fotografia do catálogo, sem decidir fonte prevalente ou cobertura histórica integral. |

Não foram observadas famílias Capital/Segmentação/Crédito sob1006 nesse recorte; isso é limite deste catálogo arquivado, não prova de inexistência universal. Inventário enumera famílias; não conta variáveis, células ou futuras unidades de implementação.

## Janelas e documentação primária

O `/43/files/12/trel/rp` e `/43/files/15/trel/rp`, item1 (individual201012); O `/56/files/13/trel/rp` (prudencial201403); N `/0/files/18..19/trel/rp` (DREprudencial/individual202503) sustentam receitas/despesas acumuladas jan–mar,jan–jun,jul–set,jul–dez. Publicação trimestral não torna DREdezembro anual. Conferência pontual de notas, sem certificação de todas as versões2010–2026. Estoques de Ativo/Passivo referem-se à data-base, inferência dos conceitos; `cp` R$mil é apresentação, unidade crua depende de contrato por binding, não certificada por catálogo.

N `/0/files/24/trel/rp`, item1, distingue publicação trimestral da Segmentação e apuração de porte/atividade internacional em30/06 e31/12 para enquadramento, remetendo ao art.5 da ResCMN4553/2017. N `/0/files/32/trel/cp/rp` distingue fonteSCR, cortes monetários e perímetro/revisões; detalhamento de variáveis e âmbito normativo não foi validado nesta fatia. Capital/Crédito contêm estoques, razões e classificações possíveis: **janela/unidade por coluna permanece pendente**, sem atribuir semestre a todo relatório.

Documentação BCB reusada/consultada nesta sessão: [Esclarecimentos e Metodologia](https://www.bcb.gov.br/conteudo/dadosabertos/BCBDesig/IFData%20-%20Esclarecimentos%20e%20Metodologia.pdf), duas páginas sem edição visível, p.1 tabelas Contábeis/Capital, p.2 notas1–3; [Resolução4280 original](https://www.bcb.gov.br/pre/normativos/res/2013/pdf/res_4280_v1_o.pdf), arts.1/4 e13, pp.1–3, delimita prudencial/vigor2014. Metodologia anuncia contábil prudencial03/2014 e Capitalprudencial03/2015; não transforma mudanças2014/15 em ponte financeira. Para2025, [ponte normativa existente](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/engineering/financial-2025-normative-bridge-20261004.md) documenta alteração de regime e ausência de de-paraAA–H/estágios; limites/versionamento permanecem. Texto metodológico sem edição é contexto, não substituto do catálogo nem certificação vigente de cada unidade.

## Oferta versus aceite e checkpoint

Os pilotos **individual/Resumo201012,202312,202412** continuam aceitos próprios,40.904 observações e contrato legado; [inventário/replay](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/engineering/expansion-execution.md), [Parquetindividual](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/main/docs/engineering/offline-parquet-20261003.md). Reutilizados como evidência delimitada, sem reexecutar/reinterpretar precisão ou migrá-los. Eles não provam quatro relatórios individuais completos, história complementar66 ou qualquer aceite prudencial. Nenhum manifest prudencial aceito foi validado nesta fatia; oferta50 não é aceite50. Financeiro11/66 permanece baseline informado separado e não amplia complementos.

Checks: leitura de2manifests/corpos autenticados e parsing integral; enumeração de perspectivas por `trel.s[]`, famílias/IDs por referência; verificação de duplicatas no agrupamento; notas pontuais acima. Sem fullsuite, execução de pipelines, escrita de dados, GETRESTnovo, código/runtime/perfis/registry/segurança/Project. Entrega privada única para revisão independente de fontes, localizadores, intervalos e limites antes de opções. Decisão humana e contrato63 continuam pendentes.

## Checkpoint1 aprovado; fatia2 para revisão

2026-10-10: coordenador comunicou revisão independente **APP, semP1/P2**, da fatia1 SHA-256 `71c720d2c7d8f2407e92415320cc9b4dd12b06ce2dadbf958ec8e8ad0890c375`; catálogos, contagens e notas pontuais confirmados. Revisor não reconfirmou o texto da Res4280 por timeout: sua referência fica como leitura contextual anterior do pesquisador, sem reconferência independente atual. Não é fundamento único das opções: períodos/perspectivas vêm dos catálogos autenticados. Preservadas as64linhas aprovadas; opções seguintes são **propostas para João, ainda não adotadas**, aguardando revisão2 e integração.

## Opções finitas de conteúdo

Cada família escolhida significa **todas as variáveis nativas oficialmente disponíveis naquele relatório/referência**, incluindo atributos, grupos/folhas e ausências com contratos próprios; não somente métricas do piloto. Isso não cria equivalência entre épocas nem autoriza preenchimento. Individual1006 e prudencial1004/1009 permanecem separados do financeiro1005 e entre si. Nenhuma opção exige recorte por emissores ou cálculo de indicador.

| Opção para decisão | Conteúdo individual | Conteúdo prudencial | Benefício, repetição aparente e lacuna |
|---|---|---|---|
| A — complemento enxuto proposto | Resumo+Ativo+Passivo+DRE na oferta201003–202606; pilotos anteriores preservados em seu contrato. | Informações de Capital na oferta201503–202606 e Segmentação201703–202606, com namespaces/IDs e versões próprios. | Acrescenta detalhe por pessoa jurídica e informação prudencial específica, contendo expansão inicial. Há sobreposição de colunas entre Resumo e relatórios detalhados, preservada como estrutura oficial. Exclui inicialmente os quatro contábeis prudenciais e SCR; não atende análise abrangente de seu perímetro contábil. |
| B — complemento amplo por perímetro | Mesmo conteúdo daA. | Quatro contábeis na oferta201403–202606, além de Capital e Segmentação nos seus intervalos próprios. | Permite investigar diferenças entre níveis, sem certificar comparabilidade. Nomes repetidos representam perímetros distintos, não duplicatas descartáveis. Mais famílias/versões a contratar e validar; preservação técnica não garante ponte1004/1009 ou societária. |
| C — ampliação prudencial primeiro | Conserva somente os pilotos individuais/Resumo201012,202312,202412; sem expansão individual nesta etapa. | Mesmo prudencial daB. | Prioriza outra visão consolidada e informação regulatória; continua sem história individual completa e tem maior sobreposição temática com o financeiro principal. Exige contratos prudenciais antes de qualquer coleta/aceite. |

**Recomendação do pesquisador: A como primeira rota, sujeita à escolha de João.** Fundamento: a direção aprovada já fornece o financeiro principal; detalhe individual acrescenta uma visão por pessoa jurídica, enquanto Capital/Segmentação acrescentam famílias prudenciais específicas. B é alternativa quando o objetivo explícito exigir também balanço/DRE do perímetro prudencial; a semelhança dos nomes não substitui esse objetivo. C serve apenas se João preferir adiar a história individual. Nenhuma dessas justificativas prova custo, utilidade acadêmica ou completude antes dos contratos/validação; não é decisão metodológica ou autorização de execução.

**SCR opcional separado:** acrescentar as oito famílias1009/123–130, na oferta202503–202606, é escolha adicional àA/B/C, com todas as variáveis nativas e contrato próprio. Fica fora da monografia2010–2024. Notas N `/0/files/32/trel/rp` distinguem recepção/consolidação/perímetroSCR e Cosif; não elimina transferências intragrupo e não inclui todas as entidades não financeiras do prudencial. Recomendação de pesquisa: deixar essa ampliação posterior, salvo objetivo de conteúdo explicitamente escolhido por João; não atribuir carteiras a estágios ou estender retroativamente ao prudencial. Crédito1005/1008 anterior e câmbio1007 não são incluídos por esta opção.

## Escolhas concretas e sequência após revisão

João precisa escolher: **(1)** A/B/C ou combinação explicitamente delimitada, incluindo/excluindo SCR; **(2)** janela técnica dos complementos — aproveitar oferta até202606 ou restringir até202412, preservando a monografia2010–2024 e sem presumir202609/202612; **(3)** limites de aceite — preservar ausências nativas e admitir lacunas documentadas, ou exigir cobertura completa dentro da oferta escolhida antes de encerrar. A primeira alternativa de aceite não transforma fonte faltante em dado aceito: o lote afetado fica pendente/falho, com motivo; desconhecido/ausência estrutural/NA/NI/vazio/zero permanecem distintos. Nenhum limiar de tolerância foi adotado. Se João exigir conteúdo fora da oferta observada, registrar nova lacuna/contrato antes de aquisição.

Depois da escolha, a #63 pode ser dimensionada por **contratos de perspectiva/família/época**, sem somar as contagens das tabelas como snapshots implementáveis ou chamar66refs de66conjuntos complementares. Próximos checkpoints propostos: (a) conferir estruturas/bindings/notas/unidades e fonte necessária do primeiro recorte, com allowlist/destino aprovados e revisão independente; (b) testar e revisar admissão/consulta/replay desse recorte antes de ampliar época/família; (c) conferir composição final, cobertura/gaps e preservação dos pilotos. Aquisição nova exige autorização/escopo próprios, sem pressupor que os arquivos financeiros compartilhados bastem para os complementos.

Reutilização técnica é **condicional** à inspeção dos contratos: arquivo/proveniência e núcleo de snapshot/binding/ocorrência do modelo existente são candidatos; compatibilidade dos readers/adapters financeiros com1006/1004/1009 não foi provada. Não mandar complementos ao pipeline financeiro por troca de parâmetro nem migrar pilotos legados silenciosamente. Evitar pipeline manual por referência; antes de implementar, conferir se o responsável existente comporta extensão explícita ou requer adapter próprio e testes causais. Sem escolha de módulos/paths de código nesta pesquisa.

Estado da fatia2: proposta documental privada para revisão independente, sem novos GETs, coleta, cálculos, código, dados ou decisão humana registrada. #62 permanece pendente da escolha; #63 não liberada; financeiro59/60 e seus aceites continuam independentes. Integrador publica a nota revisada no destino aprovado e atualiza mapa/Issues no seu escopo, sem operação de Project3.

## Estado corrente: publicação documental e decisão de conteúdo

O texto acima preserva as duas fatias e suas condições no momento da revisão. Ambas receberam APP independente, sem P1/P2: [inventário](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/62#issuecomment-6100868183) e [opções/composição](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/62#issuecomment-6100885955). A imagem pública incorpora o snapshot privado SHA256 `5a5336be3e8a278d4e741685c80c0ce785d7006852cafccca44a097661d777fa` e este registro posterior, sem publicar corpos ou arquivos privados.

**Decisão explícita de João em2026-10-10:** [opção A e toda a oferta arquivada até202606](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/62#issuecomment-6100930682). Conteúdo selecionado: individual1006 Resumo+Ativo+Passivo+DRE201003–202606; prudencial1004/1009 Capital201503–202606 e Segmentação201703–202606, em seus namespaces/versões e com todas as variáveis nativas por família. Quatro contábeis prudenciais, SCR, crédito1005/1008 e câmbio1007 ficam fora desta etapa. A periodicidade oferecida é trimestral; janelas de resultado e apuração semestral de Segmentação permanecem próprias. Monografia2010–2024 e financeiro principal não mudam.

A escolha não adotou equivalência1004/1009, método/amostra/indicadores, preenchimento ou dispensa de cobertura. Falhas/fontes faltantes permanecem pendentes, ausências nativas explícitas; não há limiar de tolerância escolhido. Os três pilotos individuais são preservados sem migração silenciosa. A #63 deve dimensionar contratos de perspectiva/família/época, endpoints/budgets/destinos/recursos e checks/revisões antes de assumir execução; a decisão de conteúdo não remove a inconsistência de persistência Windows59. Não houve coleta, cálculo ou código nesta entrega.

Integração documental Root na branch `codex/complements-content-options`, base `3557d6773c6dc8037f7ecd24ab6c418ebe552343`, após integração do PR77. Inventário público: somente esta nota em destino canônico existente; nenhum outro path, pasta/camada ou runtime alterado. A conferência final do commit público e CI tem evidência própria na Issue62; a publicação não deve ser confundida com aceite dos complementos ou encerramento do Goal.
# Primeiro caderno descritivo de indicadores — 2010–2024

Entrega da [Issue166](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/166), 18/10/2026, após a [pesquisa162](statistical-analysis-research-20261018.md) e a [decisão165](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/165). João adotou núcleo descritivo e comparativo, avaliando econometria depois. O caderno operacionaliza essa escolha com tabelas; não é redação final do capítulo, ranking, índice ou modelo inferencial.

## Entrada, arquitetura e preservação

Base de código inicial `0d2d389114ecb16652efacd5d2580f33850d46ee`, após PR167. O pin financeiro da162 foi mantido deliberadamente: `data/curated/ifdata-composition-terra-20261017-run2`, manifesto SHA256 `ce57545b643d9efcfbb09ee26234c97f131080627d42622c2b4cfbf998f7c524`. O ponteiro foi lido novamente e registrado no recibo; uma promoção em outra frente não migra esta entrega automaticamente. Tarefas novas devem consultar o ponteiro pelo [guia vigente](local-queries-20261013.md#base-de-indicadores-vigente-entre-tasks).

Allowlist pública: somente esta nota em `docs/engineering/`, responsabilidade documental já existente. Instrumentos descartáveis e artefatos detalhados permanecem privados em `.scratch/statistical-descriptive-notebook/` no worktree da tarefa: plano, `build_tables.py`, `render_notebook.py`, execuções e relatórios. Sem módulo de produção, nova pasta pública, dependência ou alteração estrutural; não foi necessário modificar arquitetura. Não houve escrita no pacote aceito, ponteiro, motor financeiro, explorador, manuscrito/Drive, fórmulas, vínculos ou arquivos das outras frentes.

## O que foi executado

1. Autenticar por SHA externo as tabelas `aggregates`, `distributions` e `joint_cells` contra o manifesto fixo e conferir contagens/IDs únicos.
2. Reagrupar células nativas disjuntas por contexto, coorte e abertura. Somar componentes N/D exatos na mesma interseção elegível; nunca somar razões. Total é união de sample/remaining/unknown, preservando as três.
3. Concatenar as frações unitárias completas das células e reusar o quantil empírico tipo2 existente para mediana e quartis. Nunca somar quartis. Companhias são deduplicadas por conjunto, sem confundi-las com unidades.
4. Preservar contagens e motivos de falta, não aplicabilidade, diagnósticos, flags matemáticas e qualificações de ativos: flags/estados de origem, ativos negativos, unidades desconhecidas e companhias com componentes de AT desconhecidos.
5. Reconciliar exatamente os contextos gerais com agregados/distribuições aceitos antes de montar a apresentação.

As perspectivas Financeiro, Capital prudencial e Individual permanecem separadas. O export integral conserva todas as métricas/janelas disponíveis; a apresentação prioriza Financeiro e Capital, com estoques pontuais e fluxosTTM. Trimestres efetivos permanecem no CSV e não foram anualizados por multiplicação.

| Resultado do instrumento final | Quantidade |
|---|---:|
| Células conjuntas aceitas consumidas |305.090|
| Contextos gerais não vazios reconciliados com agregados e quartis aceitos |12.620|
| Contextos gerais vazios sem unidades, não fabricados na saída |340|
| Contextos descritivos totais exportados |245.912|
| Eixo geral, incluindo coortes |12.620|
| EixoTcb, incluindo coortes |74.740|
| EixoSrAnalitico isolado, incluindo coortes |34.886|
| EixoTcb×SrAnalitico, incluindo coortes |123.666|
| Séries no inventário por indicador/janela/perspectiva/coorte/categoria/estado |8.508|
| Tabelas da primeira apresentação |24|

SrAnalitico isolado e cruzado começam em201703. O Sr original foi preservado na base e não recebe equivalência automática; o caderno não implementa uma nova classificação. As categorias são contemporâneas, sem retroprojeção de2024. Os contextos não formam um produto cartesiano artificial: ausência de uma categoria sem unidades não vira dado financeiro zero.

## Artefatos privados e reprodução

- `run3/descriptive-contexts.csv`: contextos, frações exatasN/D/valor, quartis/IQR, contagens de unidades/companhias, ativos conhecidos/elegíveis, lacunas, flags e razões.
- `run3/receipt.json`: contrato do instrumento, pin, ponteiro observado, hashes das entradas/saída/script/helper de quantil, base de código, UTC e reconciliações.
- `notebook-run3/series-inventory.csv`: datas iniciais/finais, quantidade de referências com valor, intervalos de elegibilidade e referências com qualificações de ativos.
- `notebook-run3/caderno-descritivo.md` e `.html`: apresentação legível em24tabelas, com recibo próprio e vínculo por hash ao CSV fonte.
- `delivery-run2/caderno-descritivo-2010-2024-166.zip`: cópia portátil privada do caderno, inventário,CSVexato, dois recibos e instruções;20.869.074bytes,SHA256 `62a1d63fa42d0e65c36f152582dbdf81fc62989d4988dc5cdb68c8636ec4415e`. IntegridadeZIP e hashes de cada arquivo após extração em memória conferidos. Não contém código/dados nativos necessários para refazer toda a base, nem autoriza publicação dos dados privados.

Comandos executados no worktree, usando Python/DuckDB1.5.6 já disponíveis na `.venv` principal: `python .scratch/statistical-descriptive-notebook/build_tables.py` e, após revisão dos dados, `python .scratch/statistical-descriptive-notebook/render_notebook.py`. Os scripts exigem destino novo; para repetir uma tentativa, declarar outro destino e preservar a anterior. Não copiar o staging privado para o Git. O clone entrega esta evidência e os contratos, não os dados/caderno privados.

A renderização em percentual com três casas é apenas apresentação. Numeradores, denominadores e frações no CSV permanecem exatos; nenhum valor financeiro foi substituído porfloat/DOUBLE. Zero é distinto de ausência do agregado; elegibilidade e denominador devem ser consultados para interpretar um travessão. Diferenças entre grupos são expressas em pontos percentuais, sem teste de significância.

## Leitura e seleção editorial proposta

O primeiro quadro apresenta disponibilidade temporal e cobertura das vinte métricas por perspectiva. O segundo compara sistema, associadas e restante no fechamento2024. Há um quadro por indicador com trajetória inicial/final, agregado, mediana, quartis, elegibilidade e qualificações de AT porTcb. Os últimos dois quadros ilustram SrAnalitico isolado e Tcb×SrAnalitico em2024 paraR1/R2/C3/C4, escolhidos por pergunta conceitual de rentabilidade/capital. Todas as demais métricas/datas continuam no inventário/CSV, sem exclusão por sinal, magnitude ou significância.

A seleção do corpo do capítulo pode começar pelo panorama das cinco dimensões e suas diferenças porTcb. Depois, SrAnalitico e associadas/restante entram quando acrescentarem interpretação com cobertura identificada. Esta é proposta editorial, não uma regra automática de amostra ou corte de completude.

Os resultados confirmam a viabilidade temporal descrita na pesquisa162: indicadores pontuais financeiros com agregado nas60referências, fluxosTTM em57desde201012 e capital prudencial em40desde201503. Isso não prova completude de todas as unidades ou componentes. A cobertura continua dependente do indicador: em202412, a coorte associada financeira tem24/24unidades elegíveis paraR1/R2/E2-B, mas21/24paraQ1/Q2 e19/24paraL2. As contagens não definem exclusões; aplicabilidade, razões de falta e peso econômico devem orientar a escolha.

Limites que acompanham a leitura:

- Sistema contém as associadas; restante é relativo aos vínculos admitidos, não identificação exaustiva das companhias fechadas. Unknown permanece categoria própria.
- Agregado e mediana respondem a perguntas diferentes. Variação entre primeira/última referência também pode refletir composição, pesos, perímetro e classificação.
- Participação no AT conhecido não é cobertura nacional certificada; ativos negativos e lacunas nominais não podem ser omitidos. Capital prudencial não recebe AT financeiro por preenchimento silencioso.
- Sr não é rating ou tamanho puro. Provisão não é inadimplência, liquidez contábil não éLCR/NSFR e eficiência de razão contábil não é fronteira produtiva.
- Não há afirmação de causa, significância, qualidade da gestão, recomendação de investimento ou conclusão acadêmica final. Contexto macro pertence à159; sua pesquisa não significa coleta completa.

## Revisões por fatia e limitações da apresentação

Run1 dos dados foi preservado com **NEEDS_CORRECTION**: o revisor encontrou omissão de52flags de pesos negativos em ativos e de3.186células nominais com companhias/AT desconhecidos sem unidades desconhecidas. Valores/frações/quartis estavam corretos. A expansão foi interrompida e os qualificadores corrigidos emrun2.

RevalidaçãoA/run2 **PASS**:211.026linhas antigas idênticas campo a campo;16.300vínculos fonte→grupo dos casos causais sem perda,208grupos afetados por ativos negativos preservados. Revisão do deltaSr/run3 **PASS**:211.026linhas anteriores intactas e34.886novas linhasSr reconciliadas integralmente com a uniãoTcb×Sr, inclusive frações, contagens e cobertura. Cinco amostras diretamente nas células verificaram início da janela, desconhecidos, nominal sem valor, zero e conflito. Relatórios privados `review-A.md`, `recheck-A-run2.md` e `recheck-A-run3.md`; o primeiro não foi reclassificado comoPASS.

Na apresentação, notebook-run1 foi preservado: oHTML era tabelar, mas a versãoMarkdown tinha linhas vazias dentro das tabelas. notebook-run2 corrigiu o agrupamento das linhas, sem alterar o CSV financeiro. RevisãoB/C **PASS** reconstruiu independentemente356linhas das24tabelas, sem divergências numéricas ou entreMarkdown/HTML. Um ajuste menor da legenda do travessão foi incorporado emnotebook-run3: significa valor indisponível/não calculável na coluna, incluindo cobertura, não apenas ausência do agregado. Dados anteriores e tentativas permanecem intactos.

Abertura automática doHTML local foi bloqueada pela política do navegador para o protocolofile; não houve tentativa de contorno por outro servidor/superfície. Portanto, não se declara inspeção visual renderizada doHTML. A conferência estrutural/numérica e a versãoMarkdown são os meios de verificação disponíveis; o material não contém gráficos científicos improvisados ou recurso externo.

A conferência do delta de legenda/ZIP e a revisão final de composição/SHA são gates próprios daIssue166/PR, com resultados e CI registrados nas superfícies reais. Este documento não transforma sua mera existência em publicação ou integração confirmada.

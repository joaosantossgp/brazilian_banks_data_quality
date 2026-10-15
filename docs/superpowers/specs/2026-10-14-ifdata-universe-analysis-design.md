# Indicadores para o universo IF.data e comparação da amostra

Desenho da [Issue 130](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/130), aprovado em seus objetivos por João em 14/10/2026. Esta entrega é planejamento; o código e os resultados ampliados ainda não existem. Base: `3c983b0fbabd3cbe03ecbd3c5f5f98b7c4a41d9b`. Reutiliza o [motor 127](2026-10-14-ifdata-monograph-analysis-design.md), a [pesquisa](../../engineering/financial-dimensions-literature-20261014.md), o [inventário](../../engineering/ifdata-segmentation-inventory-20261013.md) e a [amostra](../../engineering/fixed-financial-sample-2024-20261014.md).

## Objetivo e decisões preservadas

**Execução autorizada em 14/10/2026:** João aprovou implementar a Issue130 e pediu priorizar tudo que puder ser executado deterministicamente por código. A PR131 de planejamento foi integrada em `d33d4fd762bf11dcef2b8746e99235956f3c7fb0`; a implementação usa branch própria. O [ledger](../../engineering/ifdata-universe-analysis-20261014.md) distingue etapas concluídas de contratos ainda em admissão. Os parágrafos de estado inicial acima preservam o checkpoint do planejamento, não o estado de execução corrente.

Calcular as métricas aprovadas no universo observado do IF.data e produzir, por perspectiva e período, sistema completo, unidades vinculadas à amostra das 24 companhias e restante. O sistema completo inclui a amostra. Financeiro é principal; prudencial e individual são séries separadas. A seleção das 24 permanece fixa em 31/12/2024; o universo técnico acompanha as unidades publicadas em cada trimestre. Não chamar o restante de companhias fechadas: pode conter outras entidades e relações não incluídas na seleção.

Núcleo: 60 trimestres de 2010–2024, sínteses anuais e aberturas necessárias. 2025–2026 não entra automaticamente. Reutilizar R1/R2/Q1/Q2/C1/L2/L3/E2-B na perspectiva financeira e C3/C4 na prudencial. A perspectiva individual exige admissão dos seus contextos próprios para métricas pertinentes; nunca copiar binding financeiro por nome. As dez métricas não se tornam aplicáveis a toda instituição ou perspectiva.

Fórmulas, sinais, janelas, médias ponderadas em dias, precisão Fraction/Decimal, regras de denominadores, quantis tipo 2 e estados de ausência são os aprovados na 127. Sem pesquisa bibliográfica integral nova, índice único, ranking, imputação, código sucessor presumido ou classificação retrospectiva por dados atuais.

## População e pertencimento

Chave canônica: `(dataset, TipoInstituicao, CodInst, period)`. A população parte de unidades identificadas nos valores publicados por perspectiva/período, independentemente de ter os componentes da métrica. Cadastro sem valores é diagnóstico cadastral separado; não vira instituição reportante nem zero. CodInst nulo e eventuais agregados publicados são inventariados separadamente: a exclusão de linhas já agregadas exige prova de sua natureza, nunca faixa de códigos ou nomes presumidos. Não filtrar automaticamente `Situacao`.

Financeiro, individual e prudencial não são unidos num total econômico. Cada perspectiva utiliza as unidades nativas da sua publicação. Antes de aceitar o universo principal, conferir tipos de consolidação e presença de membros/grupos para impedir sobreposição econômica dentro da perspectiva; se a fonte não sustentar a separação, conservar diagnóstico e não certificar o total como livre de sobreposição.

O pacote 125 fornece somente a marcação da amostra, não restringe a leitura do universo. No financeiro, o recorte corresponde às chaves contemporâneas aceitas do mapa da amostra. Muitos emissores ligados à mesma unidade geram uma contribuição econômica. Company-map e ausência de vínculo de uma das 24 permanecem visíveis.

No prudencial e individual, pertencimento exige vínculo nativo/documental aceito na data e na perspectiva. Não usar igualdade numérica entre códigos como prova de identidade, nem levar todo o perímetro financeiro ao individual sem relação explícita. Se o vínculo não permite decidir pertencimento, registrar `membership_unknown`, além dos três recortes desejados. Essa categoria é reconciliação, não nova amostra adotada: entra no total técnico quando a unidade é elegível, mas não é forçada para o restante. Publicar contagens, nomes/códigos e ativos conhecidos dessa incerteza.

**Precisão operacional da fonte, revisão de 14/10/2026:** na perspectiva individual, são positivas as operadoras explicitamente admitidas125 e as unidades cujo campo financeiro contemporâneo aponta para target125 com cadastro próprio. Na prudencial, a ponte operador–target financeiro deve concordar sobre o target prudencial, com cadastros próprios na data; membros explicitamente ligados a esse target conservam sua relação e identidade próprias. O alcance é a relação nativa declarada com os targets selecionados, sem certificação de todas as participações societárias das24. A presença de um membro não substitui silenciosamente um target ausente nem demonstra elegibilidade para somá-los.

Para decidir pertencimento negativo nessas perspectivas, exigir completude das24 relações aplicáveis **naquele trimestre**, parent explícito com cadastro próprio e caminho terminal válido fora do conjunto selecionado, sem prova positiva ou conflito. Null, parent ausente, ciclo ou matriz incompleta conservam motivo desconhecido. Os campos financeiro/prudencial têm grafos separados. Não substituir essa investigação por marcar todas as unidades não nominadas como desconhecidas: vínculos positivos e negativos comprováveis devem ser usados. A implementação e seus testes/replay seguem revisão própria antes de ampliar os cálculos.

A soma das ocorrências elegíveis pode ser exibida como agregado técnico com cobertura e estado explícito de sobreposição. A revisão das fontes não liberou excluir automaticamente descendentes prudenciais nem certificar a soma como sistema livre de dupla contagem: falta conciliação datada de PR/CP/RWA entre pais e membros co-presentes. Financeiro conserva exposições entre grupos; individual é não consolidado. Esses limites não eliminam unidades nem impedem seus indicadores individuais.

## Contratos e interfaces planejados

Novo módulo adjacente `bank_quality/ifdata_population.py`, responsável pela população e marcação, sem duplicar matemática:

```python
def build_population(config: dict, output: Path) -> dict: ...
def open_population(output: Path, expected_manifest_sha256: str): ...
def partition_membership(unit_rows: list[dict]) -> dict[str, set[str]]: ...
```

Config contém períodos, perspectivas e pares root/hash externo para cadastro, valores de cada perspectiva e amostra 125. População persistida em Parquet textual e CSV/JSON com manifest por último, contrato `ifdata-population-v1`. Tabela `unit_periods`: id, perspectiva, tipo nativo, código, período, natureza/consolidação comprovada, classificação literal contemporânea, membership/status/motivo e referências das fontes. Tabela `membership_links`: vínculo explícito para companhia/unidade financeira/prudencial/individual, data, natureza, alcance e prova. Não inventar CNPJ/companhia para acomodar instituições não listadas no schema antigo.

`partition_membership` é a redução pura de linhas com `unit_id`, `membership` (sample/remaining/unknown) e companhia opcional. Retorna conjuntos `total`, `sample`, `remaining`, `unknown`; unidade repetida em companhias não duplica contagem e pertencimentos conflitantes da mesma unidade produzem unknown com diagnóstico preservado pelo caller. IDs incorporam a chave canônica, não apenas CodInst.

Ampliação com módulo adjacente `ifdata_universe_analysis.py`, wrappers públicos lazy em `ifdata_analysis.py` e CLI existente:

```python
def build_universe_analysis(config: dict, output: Path) -> dict: ...
def aggregate_unit_results(rows: list[dict]) -> dict: ...
```

**Ajuste técnico de14/10/2026, registrado na Issue antes da escrita:** o módulo novo concentra configuração/autenticação, admissão de abertura, I/O por janela/lote, normalização, verificação e comparação do contrato130. A matemática e o contrato127 permanecem no módulo existente, reutilizados sem cópia de fórmulas. Alternativa de incorporar tudo ao legado de cerca de1.225linhas aumentaria acoplamento e o levaria a2.000+linhas. Wrappers preservam os nomes públicos planejados e evitam importação circular. É responsabilidade adjacente no mesmo pacote, sem pasta/camada/dependência nova; a allowlist passa de onze para doze paths. Testes antigos/novos, regressão exata e revisão independente verificarão a fronteira e composição.

Nova entrada explícita `build-universe` e contrato `ifdata-universe-analysis-v1`; build/verify/query legados continuam aceitando os pacotes e configurações da 127. Perfis instalados têm seleção finita por ID e pin externo; manter o perfil 127 intacto e criar `ifdata-analysis-universe-profile-2010-2024.json`. Não aceitar perfil arbitrário em caminho externo.

Resultados unitários são calculados uma vez, independentemente de quantos recortes os consultem. Saída nova contém components, results, unit_periods, membership_links, unit_coverage, aggregates, distributions, segment_coverage e cohort_comparisons. Campos de resultado reutilizam os componentes/frações/estados/provas da 127, acrescentando contrato e identidade nativa. `cohort_comparisons` referencia os agregados existentes e informa interseção, cobertura e diferença descritiva quando ambos forem válidos; não infere causalidade nem teste estatístico automático.

O estágio final é o padrão de `build-universe`; o estágio explícito `unit-calculations` conserva o contrato das quatro tabelas unitárias já revisadas. Manifest declara estágio e inventário correspondentes. Relações nominais de companhia sem unidade reportante podem aparecer na cobertura, sem criar unidade, valor, contribuição ou elegibilidade. O verificador final rederiva as cinco tabelas de cobertura/agregação/comparação a partir dos resultados, componentes, unidades e provas autenticadas, por período e perspectiva, para conferir conteúdo e completude além dos hashes.

## Agregados, recortes e reconciliação

Para cada métrica/horizonte/período/perspectiva, usar a mesma interseção elegível de numerador e denominador e deduplicar pela chave nativa. Total inclui amostra, restante e eventual pertencimento desconhecido. Conferir aditividade de numeradores/denominadores e contagens das unidades distintas; razões, medianas e quartis não são somados. A identidade total = amostra + restante só é afirmada quando não há membership desconhecido e os contratos/interseções coincidem.

Os seis eixos principais são Tcb, Td, Tc, Sr, Atividade e SegmentoTb, cada um separadamente e no cadastro da própria unidade/data. Não realizar produto cartesiano de todas as categorias. Situacao é diagnóstico cadastral, não filtro de elegibilidade. Uf e Municipio podem ter recortes cadastrais adicionais, identificados como localização da sede, sem interpretação de região de negócios. Preservar null, vazio, sem cadastro e conflito. Classificações derivadas de porte/composição e cruzamentos acadêmicos novos permanecem fora desta ampliação inicial.

Cada recorte traz agregado, distribuição, contagens/listas, motivos de falta, ativos conhecidos/desconhecidos e participação mensurável da amostra no universo compatível. Não adotar limiar de representatividade, top-N ou S1 como regra automática de essencialidade.

## Entradas, abertura e capacidade

### Reexecução por código — requisito explícito de João

Seleção da população, pertencimento, fechamento de dependências, verificação dos contratos, cálculo, agregação, comparação e diagnóstico de cobertura devem ter APIs/CLI e recibos reproduzíveis. Configuração versionada e inputs autenticados governam a execução; scripts exploratórios privados não serão a única maneira de reproduzir regras/resultados. O que exigir julgamento de domínio fica explícito no perfil finito, com evidência/localizador e revisão, não em edição manual dos dados ou escolha oculta por nome.

Disponibilizar comparação automatizada contra o pacote127: mesma chave de perspectiva/unidade/período/métrica/horizonte, frações exatas, estados, flags econômicas e dependências temporais pertinentes. Comparar agregados/segmentos na mesma interseção; separar mudanças de schema/IDs de diferenças de conteúdo econômico. Emitir relatório nominal e falhar se houver diferença material não prevista por correção versionada/revisada. Não arredondar para obter igualdade.

Configuração e comandos devem separar parâmetros econômicos dos operacionais de lote. Alterar tamanho de lote não altera payload lógico nem ordem final; UTC e medições operacionais têm escopo próprio. A inclusão futura de indicador usa os componentes e o caminho comum de cálculo/verificação, com sua fórmula/perfil/evidência/testes, sem duplicar o pipeline ou prometer suporte genérico a método não aprovado.

Execução final captura automaticamente fingerprints brutos dos fontes usados, versões do runtime, configuração, perfil e pins das entradas antes de iniciar, e confere estabilidade antes de aceitar o manifest. Essa proveniência operacional fica separada do conteúdo lógico determinístico, permitindo comparar replay e tamanhos de lote mesmo com instantes próprios. Uma verificação posterior registra seu próprio código; não altera a atribuição do produtor anterior. Os probes de desenvolvimento sem fingerprint prévio do produtor permanecem identificados como tais.

Autenticar fontes já aceitas e catálogo completo. Importar abertura 200912 para as unidades adicionais somente de bytes já capturados e autenticados, com destino e perfil novos, revisão de contexto/perímetro e replay. A lista de vinte códigos da abertura 127 não libera automaticamente os demais. Se uma fonte/abertura não existir, emitir lacuna; coleta nova exige escopo próprio.

Executar por período/janela de dependência e lotes medidos de unidades, com escrita incremental e agregação global que não dependa do tamanho do lote. Não materializar o universo inteiro como expansão cega do build da amostra. Fixar ordem e usar frações exatas nas reduções. Medir tempo, memória de processo e headroom do sistema sem alterar OS/processos alheios. Começar com uma janela e ampliar após revisão.

## Aceite e ownership

Preservar, para os mesmos inputs/bindings/perímetros, todos os valores e estados unitários da amostra 127, além dos agregados e seis recortes equivalentes. Mudança comprovadamente necessária é tratada como correção versionada com causa/revisão, não diferença silenciosa. Testar unidade fora da amostra, dois emissores/uma unidade, vínculo desconhecido, agregado nativo, perspectiva diferente, ausência/zero, mudança histórica, definição incompatível e resultado independente de lotes.

Revisões por fatia antes da expansão, conferência econômico-contábil, replay completo em destino novo, revisão final do SHA e checks pertinentes. Sem PASS global por juntar probes isolados. Documentação usa links/coerência/allowlist; não exige repetir a suíte de software por esta preparação sem alteração de código.

Root integra os quatro documentos de planejamento delimitados na Issue 130. Allowlist futura de código e destinos está no plano; código/arquitetura serão alterados somente na execução. Dados aceitos, fonte bruta, leitores legados, perfil 127, piloto, Word/PDF, README/AGENTS/GLOSSARY/REFERENCES, CI/segurança/runtime/Project /3 e benchmark untracked são protegidos. Pendências reais da Issue 3 não bloqueiam os cálculos já aprovados; limitações de entradas/perímetros continuam explícitas.

## Revisão técnica da finalização — 15/10/2026

A decisão histórica de não criar recuperação de checkpoints, tomada após a primeira falha, fica substituída neste recorte técnico. A evidência mudou: `run3` e `replay3` completaram independentemente as quatro tabelas de cálculos unitários e suas três representações; o caller preservou runtime, configuração, source e manifests de entrada antes/depois. A falha posterior foi na persistência dos derivados. Repetir as fórmulas exigiria novamente cerca de80min por conjunto e duplicação física incompatível com o espaço disponível. Não se alteram método, amostra, perspectiva, precisão ou aceite final.

A retomada terá duas operações públicas no módulo/CLI responsáveis existentes. A admissão de checkpoint aceitará somente as doze representações completas das quatro tabelas unitárias, com configuração e evidências originais externamente autenticadas, inventário finito e verificação integral do estágio `unit-calculations`. O destino será novo: nenhum manifest será escrito nos diretórios originais com23arquivos. O finalizador aceitará somente um checkpoint desse estágio com pin externo, conferirá seu conteúdo e produzirá um novo pacote final, regenerando as cinco tabelas derivadas pelo mesmo código aprovado. Não se recuperam prefixos JSON nem Parquets parciais. Para próximas execuções, o fluxo público `build-universe --stage unit-calculations` seguido de finalização fornece persistência explícita sem repetir as fórmulas.

Os doze arquivos completos poderão ser hardlinks em volume compatível, com escolha explícita, inventário restrito e guardas de bytes antes/depois. Hardlinks compartilham bytes; não são cópias fisicamente isoladas. O código jamais abrirá esses caminhos para escrita, reparo ou compressão, e somente as cinco tabelas derivadas receberão Writers. Colisão, alias indevido, symlink/reparse point, falta de suporte ou mudança de bytes causa rejeição, sem fallback silencioso para cópia volumosa e sem alterar permissões. Originais e destinos falhos são preservados.

A proveniência distinguirá `calculation_producer`, sustentado pelos recibos originais do caller, do `producer` real da admissão/finalização. Não se reconstruirá retroativamente o snapshot automático que o build falho nunca publicou. Hashes dos arquivos unitários capturados posteriormente serão identificados como tais. Os bytes dos recibos e seus pins, configuração, correspondência de processo/HEAD/batch/runtime/source/entradas antes/depois e inventário ficarão interpretáveis no manifest, sem depender exclusivamente de caminhos privados. Fingerprint canônico de configuração e SHA dos bytes originais são campos distintos.

A implementação reutilizará o verificador existente de representações, contextos, componentes, métricas esperadas, referências e reconciliação de população; não criará um validador enfraquecido para a retomada. Sua conferência estrutural não substitui a auditoria econômica independente nem prova isoladamente cada fórmula. A aceitação final continua exigindo verificação completa, comparação127, duas origens de cálculo independentes com payloads finais iguais, auditoria, revisão do SHA, CI e integração. Nenhum checkpoint reaproveitado duas vezes será chamado de replay independente.

Allowlist e arquitetura: mesmas doze entradas públicas; APIs/wrappers/CLI/testes adjacentes, sem módulo, raiz, camada, dependência, coleta ou mudança de segurança. Root integra spec/plano/ledger/arquitetura/Issues. Implementador focal e revisão independente conferem o recorte antes de executar os checkpoints reais. Destinos novos ignorados permanecem em `data/curated/`; preparação privada no workspace SDD deste plano.

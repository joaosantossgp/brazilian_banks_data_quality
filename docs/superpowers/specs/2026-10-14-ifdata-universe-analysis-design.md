# Indicadores para o universo IF.data e comparação da amostra

Desenho da [Issue 130](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/130), aprovado em seus objetivos por João em 14/10/2026. Esta entrega é planejamento; o código e os resultados ampliados ainda não existem. Base: `3c983b0fbabd3cbe03ecbd3c5f5f98b7c4a41d9b`. Reutiliza o [motor 127](2026-10-14-ifdata-monograph-analysis-design.md), a [pesquisa](../../engineering/financial-dimensions-literature-20261014.md), o [inventário](../../engineering/ifdata-segmentation-inventory-20261013.md) e a [amostra](../../engineering/fixed-financial-sample-2024-20261014.md).

## Objetivo e decisões preservadas

Calcular as métricas aprovadas no universo observado do IF.data e produzir, por perspectiva e período, sistema completo, unidades vinculadas à amostra das 24 companhias e restante. O sistema completo inclui a amostra. Financeiro é principal; prudencial e individual são séries separadas. A seleção das 24 permanece fixa em 31/12/2024; o universo técnico acompanha as unidades publicadas em cada trimestre. Não chamar o restante de companhias fechadas: pode conter outras entidades e relações não incluídas na seleção.

Núcleo: 60 trimestres de 2010–2024, sínteses anuais e aberturas necessárias. 2025–2026 não entra automaticamente. Reutilizar R1/R2/Q1/Q2/C1/L2/L3/E2-B na perspectiva financeira e C3/C4 na prudencial. A perspectiva individual exige admissão dos seus contextos próprios para métricas pertinentes; nunca copiar binding financeiro por nome. As dez métricas não se tornam aplicáveis a toda instituição ou perspectiva.

Fórmulas, sinais, janelas, médias ponderadas em dias, precisão Fraction/Decimal, regras de denominadores, quantis tipo 2 e estados de ausência são os aprovados na 127. Sem pesquisa bibliográfica integral nova, índice único, ranking, imputação, código sucessor presumido ou classificação retrospectiva por dados atuais.

## População e pertencimento

Chave canônica: `(dataset, TipoInstituicao, CodInst, period)`. A população parte de unidades identificadas nos valores publicados por perspectiva/período, independentemente de ter os componentes da métrica. Cadastro sem valores é diagnóstico cadastral separado; não vira instituição reportante nem zero. CodInst nulo e eventuais agregados publicados são inventariados separadamente: a exclusão de linhas já agregadas exige prova de sua natureza, nunca faixa de códigos ou nomes presumidos. Não filtrar automaticamente `Situacao`.

Financeiro, individual e prudencial não são unidos num total econômico. Cada perspectiva utiliza as unidades nativas da sua publicação. Antes de aceitar o universo principal, conferir tipos de consolidação e presença de membros/grupos para impedir sobreposição econômica dentro da perspectiva; se a fonte não sustentar a separação, conservar diagnóstico e não certificar o total como livre de sobreposição.

O pacote 125 fornece somente a marcação da amostra, não restringe a leitura do universo. No financeiro, o recorte corresponde às chaves contemporâneas aceitas do mapa da amostra. Muitos emissores ligados à mesma unidade geram uma contribuição econômica. Company-map e ausência de vínculo de uma das 24 permanecem visíveis.

No prudencial e individual, pertencimento exige vínculo nativo/documental aceito na data e na perspectiva. Não usar igualdade numérica entre códigos como prova de identidade, nem levar todo o perímetro financeiro ao individual sem relação explícita. Se o vínculo não permite decidir pertencimento, registrar `membership_unknown`, além dos três recortes desejados. Essa categoria é reconciliação, não nova amostra adotada: entra no total técnico quando a unidade é elegível, mas não é forçada para o restante. Publicar contagens, nomes/códigos e ativos conhecidos dessa incerteza.

## Contratos e interfaces planejados

Novo módulo adjacente `bank_quality/ifdata_population.py`, responsável pela população e marcação, sem duplicar matemática:

```python
def build_population(config: dict, output: Path) -> dict: ...
def open_population(output: Path, expected_manifest_sha256: str): ...
def partition_membership(unit_rows: list[dict]) -> dict[str, set[str]]: ...
```

Config contém períodos, perspectivas e pares root/hash externo para cadastro, valores de cada perspectiva e amostra 125. População persistida em Parquet textual e CSV/JSON com manifest por último, contrato `ifdata-population-v1`. Tabela `unit_periods`: id, perspectiva, tipo nativo, código, período, natureza/consolidação comprovada, classificação literal contemporânea, membership/status/motivo e referências das fontes. Tabela `membership_links`: vínculo explícito para companhia/unidade financeira/prudencial/individual, data, natureza, alcance e prova. Não inventar CNPJ/companhia para acomodar instituições não listadas no schema antigo.

`partition_membership` é a redução pura de linhas com `unit_id`, `membership` (sample/remaining/unknown) e companhia opcional. Retorna conjuntos `total`, `sample`, `remaining`, `unknown`; unidade repetida em companhias não duplica contagem e pertencimentos conflitantes da mesma unidade produzem unknown com diagnóstico preservado pelo caller. IDs incorporam a chave canônica, não apenas CodInst.

Ampliação adjacente em `ifdata_analysis.py` e CLI existente:

```python
def build_universe_analysis(config: dict, output: Path) -> dict: ...
def aggregate_unit_results(rows: list[dict]) -> dict: ...
```

Nova entrada explícita `build-universe` e contrato `ifdata-universe-analysis-v1`; build/verify/query legados continuam aceitando os pacotes e configurações da 127. Perfis instalados têm seleção finita por ID e pin externo; manter o perfil 127 intacto e criar `ifdata-analysis-universe-profile-2010-2024.json`. Não aceitar perfil arbitrário em caminho externo.

Resultados unitários são calculados uma vez, independentemente de quantos recortes os consultem. Saída nova contém components, results, unit_periods, membership_links, unit_coverage, aggregates, distributions, segment_coverage e cohort_comparisons. Campos de resultado reutilizam os componentes/frações/estados/provas da 127, acrescentando contrato e identidade nativa. `cohort_comparisons` referencia os agregados existentes e informa interseção, cobertura e diferença descritiva quando ambos forem válidos; não infere causalidade nem teste estatístico automático.

## Agregados, recortes e reconciliação

Para cada métrica/horizonte/período/perspectiva, usar a mesma interseção elegível de numerador e denominador e deduplicar pela chave nativa. Total inclui amostra, restante e eventual pertencimento desconhecido. Conferir aditividade de numeradores/denominadores e contagens das unidades distintas; razões, medianas e quartis não são somados. A identidade total = amostra + restante só é afirmada quando não há membership desconhecido e os contratos/interseções coincidem.

Os seis eixos principais são Tcb, Td, Tc, Sr, Atividade e SegmentoTb, cada um separadamente e no cadastro da própria unidade/data. Não realizar produto cartesiano de todas as categorias. Situacao é diagnóstico cadastral, não filtro de elegibilidade. Uf e Municipio podem ter recortes cadastrais adicionais, identificados como localização da sede, sem interpretação de região de negócios. Preservar null, vazio, sem cadastro e conflito. Classificações derivadas de porte/composição e cruzamentos acadêmicos novos permanecem fora desta ampliação inicial.

Cada recorte traz agregado, distribuição, contagens/listas, motivos de falta, ativos conhecidos/desconhecidos e participação mensurável da amostra no universo compatível. Não adotar limiar de representatividade, top-N ou S1 como regra automática de essencialidade.

## Entradas, abertura e capacidade

Autenticar fontes já aceitas e catálogo completo. Importar abertura 200912 para as unidades adicionais somente de bytes já capturados e autenticados, com destino e perfil novos, revisão de contexto/perímetro e replay. A lista de vinte códigos da abertura 127 não libera automaticamente os demais. Se uma fonte/abertura não existir, emitir lacuna; coleta nova exige escopo próprio.

Executar por período/janela de dependência e lotes medidos de unidades, com escrita incremental e agregação global que não dependa do tamanho do lote. Não materializar o universo inteiro como expansão cega do build da amostra. Fixar ordem e usar frações exatas nas reduções. Medir tempo, memória de processo e headroom do sistema sem alterar OS/processos alheios. Começar com uma janela e ampliar após revisão.

## Aceite e ownership

Preservar, para os mesmos inputs/bindings/perímetros, todos os valores e estados unitários da amostra 127, além dos agregados e seis recortes equivalentes. Mudança comprovadamente necessária é tratada como correção versionada com causa/revisão, não diferença silenciosa. Testar unidade fora da amostra, dois emissores/uma unidade, vínculo desconhecido, agregado nativo, perspectiva diferente, ausência/zero, mudança histórica, definição incompatível e resultado independente de lotes.

Revisões por fatia antes da expansão, conferência econômico-contábil, replay completo em destino novo, revisão final do SHA e checks pertinentes. Sem PASS global por juntar probes isolados. Documentação usa links/coerência/allowlist; não exige repetir a suíte de software por esta preparação sem alteração de código.

Root integra os quatro documentos de planejamento delimitados na Issue 130. Allowlist futura de código e destinos está no plano; código/arquitetura serão alterados somente na execução. Dados aceitos, fonte bruta, leitores legados, perfil 127, piloto, Word/PDF, README/AGENTS/GLOSSARY/REFERENCES, CI/segurança/runtime/Project /3 e benchmark untracked são protegidos. Pendências reais da Issue 3 não bloqueiam os cálculos já aprovados; limitações de entradas/perímetros continuam explícitas.

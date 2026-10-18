# Comparação macroeconômica no explorador

Entrega da [Issue171](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/171), autorizada em18/10/2026. Usa somente a composição financeira e o [contexto macro já conferido](macroeconomic-context-2010-2024-20261018.md). Não coleta fontes, altera fórmulas ou recalcula indicadores. O pacote financeiro continua `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`; o macro, `9920b6ebe130854130ab9ec7e7bfe98410556f22f81b969128be2704be8de118`.

## Uso e interpretação

O painel Brasil aparece após a evolução financeira. Selecione uma das25combinações já existentes de série, variável, categoria e método. O intervalo De/até é comum aos dois gráficos; cada eixo vertical mantém sua unidade. O período selecionado é marcado em ambos. A tabela e o CSV da comparação alinham um registro por trimestre, com os agregados financeiros filtrados e uma observação macro nacional. A série macro não é replicada por companhia para produzir estatísticas.

Todos os filtros financeiros permanecem: perspectiva, população, Tcb, SegmentoTb, Tc, Td e Sr original/analítico. Não alteram a série Brasil. Um recorte financeiro sem unidades pode continuar mostrando a série macro; isso não preenche sua lacuna financeira. As janelas são independentes e explícitas: ROA12meses não transforma uma taxa macro trimestral em anual. Não há interpolação, seleção automática de defasagens, correlação ou inferência causal.

Percentuais macro já estão em pontos percentuais publicados: `6.2` é6,2%, não620%. Indicadores financeiros persistidos em razão conservam sua apresentação em%. Índices possuem bases próprias; PIB nominal está em milhões de reais, renda em reais. Não somar índices setoriais. Juros são acumulados3/12meses; Fisher é ex post, antes de tributos/custos. PNAD não cobre2010–2011; renda real usa preços do último trimestre divulgado na captura,2026T2. Meta Copom e curva histórica não são oferecidas. Origem, unidade, cobertura e ressalvas são exibidas por série.

## Reprodução

O exportador mantém compatibilidade com exportações sem macro. Para incluir o pacote:

```text
python scripts/export-ifdata-explorer.py --composition COMPOSICAO --expected-manifest-sha256 PIN_FINANCEIRO --macro-context PACOTE_MACRO --macro-manifest-sha256 PIN_MACRO --output NOVO_HTML
```

Informe ambos os argumentos macro ou nenhum. O exportador autentica manifest e Parquet trimestral, verifica contrato, contagem, chave única por combinação/trimestre, janela, unidades e frações. Usa somente `quarterly.parquet`, mantendo os1.476payloads completos e frações em strings. O HTML é autocontido, sem dependência de servidor, banco ou consulta externa; links de fonte são navegação opcional. Destinos existentes são recusados. Recibo registra hashes de composição, macro, template, exportador e HTML. Não altera nenhum pacote aceito.

O CSV de comparação contém as razões financeiras exatas e contagens por população, fração macro, unidade, estado, IDs e contagens das fontes, filtros, janelas e os dois manifests. É distinto do CSV financeiro já existente. Valores arredondados no gráfico/tabela são aproximações de visualização.

## Descoberta por outras tasks

Consulte `data/curated/current-indicators.json` no checkout compartilhado identificado pelo diretório Git comum, conforme o guia de [consultas locais](local-queries-20261013.md). `package` e `manifest_sha256` identificam a base financeira; `macro_context` identifica o contexto separado; `explorer` identifica o HTML vigente, seu hash e a cópia privada no Drive. Não escolher arquivos por nome mais recente. Fixar os dois pacotes e o hash do HTML no início de cada análise. Esta entrega altera somente a apresentação: os dois pins permanecem os mesmos. Tasks já iniciadas conservam suas entradas até migração explícita.

## Verificação e entrega

Testes causais cobrem adulteração, duplicatas, precisão, unidades, datas, lacunas estruturais, separação das janelas e escala percentual no JavaScript. A verificação do artefato compara integralmente suas células financeiras com o HTML aceito anterior e os payloads macro com o Parquet autenticado. Inspeção desktop e revisão independente conferem apresentação, filtros e limites; resultados e SHA final ficam naIssue171. Sem teste de celular, nova camada, biblioteca, rename ou delete. Código e esta nota são públicos; HTML, pacotes e cópia no Drive permanecem privados. O ponteiro compartilhado atualiza somente sua referência ao explorador após aceite.

Na inspeção desta entrega, o navegador automatizado excedeu seu limite de mensagem ao abrir o HTML completo de aproximadamente98MB. A comparação integral de dados foi realizada por código; a inspeção visual usou exatamente o mesmo template, com todas as séries macro e um subconjunto financeiro B1/ROA de1.577células. Isso verifica renderização e interação representativas, sem declarar inspeção visual integral de todos os dados/recortes.

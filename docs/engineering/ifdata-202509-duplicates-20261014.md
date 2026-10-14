# Duplicidades IF.data em setembro de 2025

Registro de 2026-10-14 da [Issue 123](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/123). Objetivo: localizar a origem das repetições e recuperar os cálculos afetados com intervenção limitada. Base de código: `efb563652058dfd444f9a7bc5e53fa83c4943250`; branch `codex/ifdata-202509-duplicates`.

## Diagnóstico e limite da atribuição

A comparação integral de 1.031.100 ocorrências selecionadas de 202509 encontrou igualdade entre os dez campos nativos e os seis campos de proveniência do JSON capturado e do Parquet correspondente. A multiplicação já está no bruto recebido; o conversor preservou as ocorrências. Não houve conflitos de saldo ou atributos nas chaves examinadas.

| Conjunto nativo | Ocorrências armazenadas | Tuplas nativas distintas | Repetição |
|---|---:|---:|---|
| Financeiro, tipo 2, relatórios 1–4 | 448.836 | 150.780 | 3.504 tuplas duas vezes; 147.276 três vezes |
| Individual, tipo 3, relatórios 1–4 | 466.764 | 168.420 | 38.496 tuplas duas vezes; 129.924 três vezes |
| Capital, tipo 1, relatório 5 | 99.000 | 33.000 | Todas três vezes |
| Segmentação, tipo 1, relatório 6 | 16.500 | 5.500 | Todas três vezes |

Cada resposta capturada dos três tipos tem uma página, sem `nextLink`. Os controles equivalentes de junho e dezembro de 2025 não apresentaram repetição das chaves examinadas. A prova integral é sobre os arquivos capturados, não uma reconstrução da resposta histórica do servidor.

Uma consulta finita ao [endpoint oficial IfDataValores do BCB](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/IfDataValores(AnoMes=@AnoMes,TipoInstituicao=@TipoInstituicao,Relatorio=@Relatorio)?%40AnoMes=202509&%40TipoInstituicao=2&%40Relatorio=%27T%27&%24format=json&%24top=100), em 2026-10-14, respondeu HTTP 200: 100 ocorrências, 42 tuplas distintas, sendo 24 duplas, 17 triplas e uma ocorrência única no limite da amostra. Isso reproduz a repetição na fonte financeira atual. Não comprova toda a captura passada nem respostas atuais dos tipos 1 e 3. Corpo de 40.483 bytes, SHA-256 `54821ac5f8f87bf271f9ebd8d27d15bcffb95aeab0ce9f334b0e835b39552e29`.

As três tentativas anteriores com filtro `CodInst` retornaram HTTP 400 por incompatibilidade de tipos no serviço. Foram preservadas como falhas, sem tratá-las como população vazia. A quarta consulta, sem esse filtro, foi [delimitada na Issue](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/123#issuecomment-6169535245). Nenhuma atualização histórica foi coletada ou incorporada à base.

## Correção e fronteira

O módulo existente [ifdata_indicators.py](../../bank_quality/ifdata_indicators.py) reconhece ocorrências exatamente iguais antes de avaliar os indicadores e os estoques de abertura usados nas médias. A política `identical-native-rows-same-source-v1` fica registrada no manifest derivado.

O reconhecimento exige todos os dez campos nativos presentes e iguais, inclusive os tokens de saldo, além de igualdade dos demais atributos semânticos. Exige a mesma origem autenticada: arquivo, SHA-256, URL, instante de coleta e contexto; as posições na página devem ser positivas, válidas e distintas. Cada localizador completo permanece em `source_occurrences`, ordenado por posição. O representante usa a menor posição. Nenhuma entrada é modificada em memória.

Valores iguais por si só não bastam: diferenças de conta, grupo, definição, token, cadastro ou origem continuam ambíguas. Conflitos não são escolhidos arbitrariamente; null continua null e zero continua zero. Fórmulas, versões, janelas e perímetros do piloto permanecem os mesmos.

A correção pertence à projeção analítica do piloto. Os arquivos brutos e Parquet nativos continuam contendo todas as ocorrências; consultas diretas que somem esses arquivos precisam respeitar essa multiplicidade. O conjunto de segmentação foi diagnosticado e preservado; não é uma entrada de indicadores deste piloto. Não se certifica uma deduplicação global de consultas ou de toda a história.

## Validação por fatias

1. Diagnóstico completo bruto→Parquet, controles temporais e recibos: revisão independente A, PASS antes da edição de código.
2. Regressões causais em [test_ifdata_indicators.py](../../tests/test_ifdata_indicators.py): RED demonstrou o bloqueio por duplicidade, inclusive o estoque de setembro usado em dezembro. GREEN: 21 testes, incluindo cópias, conflitos, null, origem incompleta, posições reutilizadas e média trimestral. Revisão independente B: PASS, com provas adversariais e permutações adicionais.
3. Lote real de setembro e dezembro: revisão independente C, PASS. Reprodução de valor/status das 66.942 linhas com Decimal de precisão 100; conferência de 54.552 componentes únicos e 100.862 ocorrências contra Parquet autenticado, além de cobertura, wide e contagens estatísticas.

Os três pareceres e seus snapshots estão na evidência privada `.scratch/ifdata-202509-duplicates-20261014/`. Hashes dos pareceres A/B/C, respectivamente: `dfc484857c0597ffda7c0f7bfff220c59cb799d75ad0d31b714d1a9ad9ae1874`, `0fde61973281d8c725a9ca40e5f818c10b258e59ac6702229e97d2bba0f1dbd8`, `ecec879764042fa532e2503f43973187b9ff6ecd357790fff6e8cd7a9661f66d`.

## Resultado do lote limitado

A primeira execução, com um worker e limite DuckDB de 512 MB, falhou na exportação final por memória. Não emitiu manifest e não foi aceita; o destino terminou vazio após a limpeza automática dos estágios temporários. O diretório e o recibo de falha foram preservados. O [ajuste de recursos](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/123#issuecomment-6169849184) manteve os mesmos código e inputs, usando destino novo, um worker e 768 MB. Não houve alteração de runtime global.

A execução aceita localmente produziu 66.942 linhas em 16,984 segundos; pico medido de working set do processo: 1.467.985.920 bytes. Destino ignorado: `data/curated/ifdata-indicator-duplicates-202509-202512-20261014-run2/`. Manifest SHA-256: `08483068295ded062cd1c4b48fca67fe2cdc6cba7279644668497733a757a7bb`. Foram conferidos 344 hashes protegidos antes e depois, incluindo inputs e o piloto anterior. A nota local da Issue 122 também permaneceu byte-idêntica e fora desta entrega.

| Referência | Capital: novos válidos | Financeiro: novos válidos | Individual: novos válidos | Total recuperado |
|---|---:|---:|---:|---:|
| Setembro de 2025 | 1.805 | 8.061 | 8.980 | 18.846 |
| Dezembro de 2025 | 0 | 2.740 | 3.084 | 5.824 |
| Total | 1.805 | 10.801 | 12.064 | 24.670 |

Nas duas referências, os resultados válidos passaram de 12.692 para 37.362, com o mesmo conjunto de 66.942 chaves. Nenhum dos 12.692 valores antes válidos mudou, nem seus status. Fórmulas e identificadores de versão permaneceram iguais. Das 33.018 linhas que mudaram de status, 24.670 tornaram-se válidas; as demais passaram a expor a restrição subsequente, como saldo null, denominador zero, abertura ausente ou mapeamento não comprovado. Nenhuma linha nova conservou `duplicate_binding` ou `duplicate_stock_binding`.

Dezembro foi incluído porque a média trimestral usa o estoque de setembro. Isso explica o efeito posterior sem atribuir duplicidade aos dados nativos de dezembro. Cobertura integral de 160 linhas, wide de 8.919 linhas e contagens de 82 grupos estatísticos foram conferidas.

## Uso e pendências

O novo `painel.html` contém somente as duas referências verificadas. O painel histórico de 66 trimestres em `data/curated/ifdata-indicator-pilot-20261011/` foi preservado; não foi sobrescrito nem regenerado. O resultado local pode ser consultado pela CLI existente:

```powershell
python scripts/pilot-ifdata-indicators.py query <destino-run2> "SELECT period, perspective, status, count(*) AS n FROM results GROUP BY ALL ORDER BY ALL"
```

Para uma futura geração, a CLI `build` aceita `--periods 202509 202512`, mas exige destino novo. O executor privado deste lote limitou os recursos da conexão local; a execução da CLI sem esse ajuste não reproduz necessariamente o consumo de memória medido.

Este recorte resolve as repetições idênticas demonstradas, sem resolver os mapeamentos de margem/provisão no regime de 2025, ausências de abertura, perímetros desconhecidos ou outras decisões metodológicas. Os indicadores continuam exploratórios; esta validação não adota indicadores acadêmicos nem certifica comparabilidade com REF.

Código, testes e esta nota formam o inventário público completo. Não há nova pasta, módulo, dependência ou alteração da arquitetura: implementação e regressões ficam nos módulos responsáveis existentes, e o diagnóstico usa o destino canônico `docs/engineering/`. Revisão final do SHA, CI e integração têm evidência datada na Issue 123 e na PR correspondente; os passes locais acima não antecipam esses estados remotos.

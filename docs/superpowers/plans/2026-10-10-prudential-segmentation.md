# Metadados prudenciais e ativação separada — Issue 63

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** compilar deterministicamente os metadados de Segmentação prudencial, preservando a barreira entre candidato incompleto e conjunto aceito.

**Architecture:** reutilizar seleção, autenticação e travessia O/D em `financial_report_profiles.py`. Separar o núcleo de bindings da exigência de cadastro completo, mantendo invariantes as portas financeiras e individuais. Não criar um terceiro motor, transporte ou fluxo por trimestre.

**Tech Stack:** Python e unittest existentes, offline, sem dependências novas.

**Spec:** decisão de conteúdo na [Issue62](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/62#issuecomment-6100930682), [inventário aprovado](../../engineering/complements-content-options-20261010.md), [claim da fatia A](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/63#issuecomment-6103305646).

Base: `526670dbf78372d066f314c6fbce17b49fca7dd2`; branch `codex/prudential-metadata-context`; Root integra. A revisão independente do desenho corrigiu o bloqueio excessivo: falta de C impede instalação e dados reais, mas permite software offline com fixtures explícitas.

## Escopo e limites

- Representante: `{"period":202312,"perspective":1009,"reports":[102]}`, todas as 15 variáveis, dez bindings C e cinco N1, sem grupos.
- Entrega integral permanece individual66, Capital46 e Segmentação38 até202606. Este recorte não encerra a Issue63.
- Fonte C1009 não está disponível no inventário pesquisado. Largura, população, grade e aceite reais são desconhecidos.
- Nenhum GET, execução/reparo de autoridades59, perfil instalado, admissão, Parquet, runtime, segurança ou Project /3 nesta fatia.
- Não modificar readers, adapter, registries, dados aceitos ou contratos/defaults1005/1006.

## Fontes e confiança

O catálogo nativo pinado aponta `/95` para202312, `/95/files/13/trel` para102/1009, C em `/95/files/2/f`, D em `/95/files/9/f` e N1 em `/95/files/3/f`. O cadastro anunciado é `ifdata/202312/cadastro202312_1009.json`; oferta não equivale a fonte disponível.

O: manifest `data/raw/financial-cadaster-202412-20261003/20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json`, SHA256 `b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7`; corpo `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07`.

D: manifest `data/runs/expansion-202312-20261001/raw/2026-10-01T033720509Z_202312_e1bacaca-f0b3-4c23-a40d-8defa2891ca2.json`, SHA256 `f26d028164139e20faa2094b31bab08e8fbcd1410b28bd917b406018cf2c0425`; corpo `11a0704ec62d3123c8af2ceb7c98b545c683781e297f8a3f4d89e449122c7ee2`.

N1: manifest `data/runs/expansion-202312-20261001/raw/2026-10-01T033724367Z_202312_5477956f-562c-4989-acdb-a72c933a3d42.json`, SHA256 `9d35989367a25ab9ae12551c8a5f6ddf7c51249d6a0f181bd34240f63a74e6db`; corpo `fb85523b59409bb6ebc8bb32bf78751a2380eea3b880873f27331398e5511eae`.

P: manifest `data/raw/discovery-20261001/20261001T012756759142Z_portal_56229187f15948a0a353b4b194b7cb3f.json`, SHA256 `5757f812b56dbd414e2fa3d68075cafbf50157a010a9b4b330126fab86dd211a`; corpo `234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153`.

Autenticar também a disponibilidade de N1/P permite declarar somente C faltante. Esta etapa não interpreta observações N1 nem executa P; não é validação ou admissão desses valores. D/N1 conservam a mesma qualificação de captura decodificada legada, com diagnóstico original preservado.

Autenticar contra autoridade instalada própria, sem confiar em hash escolhido pelo caller. D é captura legada decodificada: conservar contexto, diagnóstico literal, recuperação original e ausência de `truncated`; não afirmar EOF/bounded retroativamente nem herdar exceção1005/1006. Fontes adicionais e ativação posterior exigem pins e contratos próprios.

O candidato usa `ifdata-prudential-metadata-candidate-v1`, seleção completa, digest do descriptor, árvore/bindings/annotations e fontes presentes/requeridas. Sem C, declara `missing_sources` incluindo `cadaster`; não inventa schema, população ou grade. Não é um contexto instalado e deve ser rejeitado pelas portas existentes de admissão/conversão.

## Bindings e semântica

Preservar as 15 colunas na ordem nativa. Colunas17989–17996 e18002/18003 são atributos cadastrais. Colunas17997/17998/17999 usam ifd79707/79708/79709 e lid85843/85844/85845: flags. Colunas18000/18001 usam ifd79710/79711 e lid86846/87071: medidas. Todos os cinco valores N1 usam área1; origem numérica não significa dinheiro.

| Origem | kind | unit | encoding autoritativo |
|---|---|---|---|
| Dez bindings C | `attribute` | `not_applicable` | `utf8_string_exact_v1` |
| Três flags N1 | `flag` | `not_applicable` | `json_native_token_v1` |
| Duas medidas N1 | `numeric_measure` | `unknown` | `json_native_token_v1` |

`origin_kind` mantém `cadaster` ou `numeric`. Preservar tokens number/string/null, lexema, texto e estados; boolean/array/object inesperados falham sem coerção. Flags não são convertidas em boolean nem restritas a0/1 sem prova. A projeção Decimal exata não muda o significado da variável; precisão e armazenamento efetivos só serão fixados com os dados reais.

Annotations de apresentação:18000 anuncia BRL/mil,18001 USD/mil e flags Sim/Não. Não executar formatter, converter moedas ou inferir escala bruta universal. Unidade/moeda/escala de armazenamento das medidas continuam desconhecidas. Preservar ausência estrutural, não armazenado, NA, NI, null, vazio, zero e texto separadamente.

## Generalização

O representante valida mecanismos comuns; a expansão usa ofertas e fontes pinadas por família/época. A tabela aprovada define Capital1004/6 em201503–202212,1004/114 em202303–202306,1009/103 em202309–202406 e1009/115 em202409–202606; Segmentação1004/80 em201703–202306,1009/102 em202309–202412,1009/122 em202503 e1009/131 em202506–202606. Validar IDs, perspectiva, referência e árvore contra cada oferta. Não selecionar por nome nem presumir continuidade1004↔1009. Perfis futuros são derivados, não84 fluxos ou perfis editados manualmente.

## Fatia A: candidato offline

Allowlist: `bank_quality/financial_report_profiles.py`, `tests/test_prudential_segmentation_profiles.py`, este plano e `docs/architecture.md`. Root possui documentação/Git; executor de código possui somente profiles/teste. Nenhum perfil instalado ou diretório novo.

- [x] Escrever testes RED autocontidos de seleção, fonte/pointer/hash adulterados, duplicatas, bindings determinísticos, semântica e cadastro ausente.
- [x] Implementar o mínimo no responsável existente, extraindo núcleo O/D comum sem relaxar autenticação ou confundir perspectivas.
- [x] Executar o módulo novo e regressões pertinentes de profiles1005/1006; fixtures devem funcionar sem bruto local. Sintético não prova aceite real.
- [x] Conferir O/D reais somente leitura, todos os15bindings e rejeição do candidato incompleto. Não executar admissão ou consulta de dados.
- [x] Obter revisão independente da fatia, corrigir achados materiais e conferir diff/allowlist antes de ampliar.

## Etapas seguintes

**B — fonte/perfil completo:** localizar ou obter C sob contrato e gate próprios; validar pins, captura, identidade, campos nativos, C1, C0 único e localizadores. Só então fixar largura/N/grade e instalar perfil completo, com revisão de O/D/C/N1/P.

**C — dados reais:** novo claim para reader/adapter/testes/perfil e destinos novos; admissão, Parquet, consulta integral e replay de15×N com precisão e proveniência, recursos medidos e revisão parcial. Preservar três individuais,11financeiros e pilotos. Não exige PR por período ou fatia.

**D — composição:** checks pertinentes em uma composição, revisão independente do SHA final, CI/integração autorizadas e atualização63/mapa2. Não declarar PASS global somando reruns isolados nem encerrar63 antes da oferta integral aceita.

## Evidência

Desenho R2 revisado: SHA256 `726e50475067d372d791da94df128b7e9aa2b7f5c1834e6d59ee93cc3e0d7d27`, aprovação limitada à fatia A offline. Plano/arquitetura também receberam revisão parcial, SHA256 `10268e84ba1f0178d79f04b0a7d79b972b5f3a143ae6ef19c411c40bb283a59e`.

API entregue localmente: `author_prudential_metadata(selection=None)`. RED inicial: cinco falhas por API ausente; GREEN inicial: cinco testes. A inspeção durante a implementação encontrou que `reports=(102,)` era normalizado indevidamente para lista: sexto teste RED, guarda de tipos antes da canonicalização e seis testes GREEN. A revisão do primeiro snapshot não foi transferida automaticamente ao ajuste.

Composição corrente única em 2026-10-10: **50 testes PASS em 130,861s**, zero falhas/erros/skips, incluindo seis prudenciais, 28 financeiros e 16 individuais. A execução anterior de 49 testes é somente histórica. Bloco executado via stdin em `.venv/Scripts/python.exe -`:

```python
import unittest
loader = unittest.TestLoader()
suite = unittest.TestSuite(loader.discover('tests', pattern=p) for p in (
    'test_prudential_segmentation_profiles.py',
    'test_financial_report_profiles.py',
    'test_individual_report_profiles.py'))
raise SystemExit(not unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful())
```

Conferência real somente leitura: 15 bindings/pointers e fontes O/D/N1/P autenticados; candidato lógico SHA256 `d33fd08a5480433454b4507f79a1b67ab79fa1422627316958e9c98057404452`, descriptor `2b95368dedb49edeefbc1bc9ed1d7e662acbcc67e556ae9eeb6559f3fa3ab890`. As portas existentes rejeitam a seleção prudencial. Nenhum perfil instalado, fonte C, admissão, GET ou novo conjunto aceito.

Revisão independente R2 da composição corrente: **APP**, sem achados materiais. Conferiu os quatro paths, preservação do núcleo comum, correção de tipos, pins e documentação; executou independentemente os seis testes novos e rejeições antes de qualquer IO. O resultado integrado de 50 testes foi considerado como evidência do executor, sem alegar repetição pelo reviewer. A conferência do SHA exato, publicação e CI têm estado confirmado na Issue63/PR, não são presumidas por este registro local.

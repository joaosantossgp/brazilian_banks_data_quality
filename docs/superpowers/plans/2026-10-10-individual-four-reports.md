# Quatro relatórios individuais: primeiro recorte offline da Issue 63

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans` ou `superpowers:subagent-driven-development`, com revisão independente antes de ampliar cada fatia. A PR pode reunir todas as fatias; não criar PR por relatório ou trimestre.

**Goal:** admitir, converter, consultar e reproduzir os quatro relatórios individuais de dezembro de 2024 a partir das fontes arquivadas, sem nova coleta, preservando o financeiro e os pilotos individuais.

**Architecture:** estender os mecanismos existentes de contexto, árvore, proveniência e precisão com uma seleção individual fechada. O contrato e os artefatos individuais permanecem próprios; nenhuma equivalência entre perspectivas é adotada.

**Tech Stack:** Python 3.12, DuckDB/Parquet já instalados, arquivos locais explícitos e hashes externos. Sem dependência, runtime ou serviço novo.

**Spec:** [modelo lógico aprovado](../specs/2026-10-04-logical-data-model-design.md), [decisão de conteúdo](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/62#issuecomment-6100930682), [Issue 63](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/63) e contrato inline abaixo. A janela completa dos complementos continua até 202606; este primeiro recorte não redefine a entrega total.

Base: `3310eae358a07382f4801a8a230ba85c129cb452`, branch `codex/individual-four-reports`. Root integra; executor e reviewer têm ownership separado. Triagem e revisão de viabilidade foram somente leitura, sem aceite de dados.

## Contrato fechado do primeiro recorte

- Seleção: perspectiva **1006**, referência **202412**, relatórios na ordem **[93, 77, 100, 94]**: Resumo, Ativo, Passivo e DRE. Nenhum parâmetro público pode trocar perfil, subconjunto ou namespace.
- Cadastro: 1.585 ocorrências, exatamente `c0..c37`, todos strings; `c1=202412`; `c0` opaco, não vazio e único, no namespace 1006. Preservar todos os registros, sem filtro acadêmico, padding ou identidade societária inferida.
- Árvores: 129 nós, nove grupos, 120 folhas. Resumo: 19/0/19; Ativo: 30/2/28; Passivo: 35/3/32; DRE: 45/4/41. Os números indicam nós/grupos/folhas. Conservar ordem, hierarquia, metadados, flags e fórmulas opacas; nunca executar formatter ou fórmula da fonte.
- Origens: 44 posições de atributo e duas de quantidade no cadastro; 74 posições monetárias em N1. Esses são bindings por relatório, não necessariamente 74 `lid` distintos. Usar `ifd` para definição e `td/a/lid` para origem; não relacionar por nome.
- Grade esperada: **120 × 1.585 = 190.200 posições**, sem grupos como observações. Quantidade armazenada, ausências, estados e dimensões Decimal só serão conhecidas após admissão exata; não preencher esses resultados antecipadamente.
- Preservar JSON number/string, lexema, Decimal, pointers de definição/catálogo/origem e hashes. Ausência estrutural, célula não armazenada, NA, NI, null, vazio, zero e token inválido continuam distintos. Falha de schema/hash não vira ausência ou população zero.
- `cp` anuncia R$ mil; `fid=13` e o portal P arquivado dividem `value/1000.0`. Anotar **BRL cru inferido tecnicamente**, sem certificar economicamente cada escala. Estoque na referência é inferência conceitual explícita. DRE e lucro do Resumo têm janela julho–dezembro de 2024 segundo as notas/bindings pinados; não anualizar.
- Precisão por binding: DECIMAL exato quando couber até 38 dígitos; quando exceder, representação numérica textual exata explícita e accessor Decimal, como mecanismo já existente. Nunca DOUBLE, arredondamento, redução de escala ou UNION numérica global.

### Fontes imutáveis e pins

Os paths são relativos ao checkout; cada `.bin` está adjacente ao manifest e tem o mesmo stem. URLs, contextos e instantes vêm dos manifests originais, sem nova requisição.

| Papel | Manifest | SHA256 manifest | SHA256 corpo / bytes |
|---|---|---|---|
| C1006 | `data/raw/discovery-20261001/20261001T013234426740Z_portal_cadastro_202412_c363a9e39165404aa08831eaa26dd2f5.json` | `ebed46f73f39b31f450ea995abd53e5414663c169eedb7b2a4aa135a70143589` | `5200301d6dabad5240b2d65aada6cb2179d75d497999c9b08d6c011a74043685` / 824810 |
| D | `data/raw/discovery-20261001/20261001T013235163159Z_portal_info_202412_4b180f95c53d44d4b5f3a4444c586e20.json` | `45b12d698f2b6bcaae34ebf09f8d051f7fab1e3036e27ef1a147eee979b9192e` | `9c09219eeb7aa558e0ac74e32b905ba940ec00b0bc01f761b1d086aef86cca28` / 188690 |
| N1 | `data/raw/discovery-20261001/20261001T021818677646Z_portal_numeric_input_202412_1_786886e0790146b5ad208e8f86f0fdd6.json` | `2e782a8c6b9fc02ad109921550a4f9ebde49cfd534a26e851e368840abbfaa07` | `c0f14556464dfd191df00d6867023fa894174b0eeb007a2bd5f5714187fa0474` / 15612512 |
| O | `data/raw/financial-cadaster-202412-20261003/20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json` | `b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7` | `2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07` / 13527657 |
| P | `data/raw/discovery-20261001/20261001T012756759142Z_portal_56229187f15948a0a353b4b194b7cb3f.json` | `5757f812b56dbd414e2fa3d68075cafbf50157a010a9b4b330126fab86dd211a` | `234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153` / 92483 |

O contém os relatórios em `/99/files/{29,27,11,30}/trel`, na ordem da seleção. Todos anunciam `s=[{"id":1006}]`. P contém os dois `case13` nos offsets UTF-8 zero-based 28520 e 33835; esse localizador deve ser reconferido na autoria do perfil, sem executar JavaScript.

### Compatibilidade legada limitada

Os manifests conservam GET/200, outcome ok, `truncated=false`, diagnósticos vazios, tamanho físico/manifest/Content-Length registrado compatíveis e Content-Encoding ausente. Isso é evidência legada; não equivale a observação de EOF, counters, sidecar ou contrato `bounded-http-archive-v1`.

- Autenticar os cinco manifests/corpos exatos contra pins instalados independentes do caller, paths contidos e inventário explícito. Não criar exceção para qualquer fonte 1006 ou qualquer legado.
- Preservar a ausência de `source_complete` e dos campos bounded. Registrar a evidência observada e os limites; não acrescentá-los retrospectivamente ao bruto nem declarar completude econômica/global.
- Preservar o literal original de recuperação com offset `-03:00` quando presente. Uma representação UTC derivada usa conversão de instante explícita, conserva o literal e liga ambas à mesma fonte pinada. Não renomear um literal local como UTC normalizado.
- N1 mantém seu contexto original de entrada bruta do piloto/shared. Seu uso adicional é sustentado pela associação literal do catálogo; não reclassificar a aquisição original como captura conjunta dos quatro relatórios.
- Reutilizar o padrão de pins/proveniência do legado financeiro 202312, sem reutilizar sua exceção como autorização destas fontes. As validações atuais 1005/bounded continuam próprias.

## Allowlist e preservação

Allowlist da execução confirmada no claim da Issue63 após revisão independente do contrato/plano:

1. `bank_quality/financial_report_profiles.py`: autoria/validação de contexto e fontes fechadas próprias, reaproveitando árvores e origens.
2. `bank_quality/financial_reports.py`: admissão individual explícita e compartilhamento dos mecanismos existentes; manter entrypoints/defaults financeiros e rejeições de perspectiva.
3. `bank_quality/financial_reports_parquet.py`: conversão/leitura individual próprias sobre mecanismos comuns, sem misturar contratos ou diminuir precisão.
4. `bank_quality/individual-reports-profile-202412.json`: perfil instalado e revisado da seleção fechada, com pins, bindings, qualificações e contrato próprios.
5. `tests/test_individual_report_profiles.py`, `tests/test_individual_reports.py`, `tests/test_individual_reports_parquet.py`: testes de comportamento dos três recortes.
6. Este plano: `docs/superpowers/plans/2026-10-10-individual-four-reports.md`.

Responsabilidade permanece nos módulos existentes. Perfil e testes são adjacentes; nenhum módulo/camada/raiz nova. Não editar registry financeiro, aquisição, autoridade, pipeline, catálogo, CLI, README, AGENTS, arquitetura, glossário, CI, dependência ou runtime. Se a implementação exigir ampliar paths/responsabilidade, registrar motivo e revisar o delta antes de escrever.

Dados novos somente em destinos ignorados próprios: `data/derived/individual-four-reports-202412-20261010-run1` e `-run1-replay`; Parquet em `data/curated/individual-four-reports-202412-20261010-run1` e `-run1-replay`. Confirmar inexistência antes de executar; nunca reutilizar tentativa ou aceites. Evidência operacional em `.scratch/issue59-operational-20261010/`, sem publicar bruto, chave ou pacote decriptado.

Antes da primeira escrita de dados, congelar inventário/hashes dos cinco inputs, três pilotos individuais e 11 aceites financeiros usando os índices aceitos já existentes. Não reconstruir baseline por glob de qualquer pasta. Conferir novamente após admissão, conversão e replay.

## Fatias e checks antes da expansão

### A. Contexto, fontes e perfil individual

- [ ] Conferir fontes/pins/framing/literais de timestamp e as árvores/bindings; gerar candidato somente de bytes autenticados.
- [ ] Escrever testes RED para seleção trocada, caller profile override, fonte/manifest/hash/contexto/URL alterados, duplicatas JSON e timestamps sem fuso. Validar a projeção UTC derivada e preservação do literal original.
- [ ] Implementar a extensão mínima de contexto e fontes; produzir perfil individual fechado, sem relaxar regras financeiras existentes.
- [ ] Rodar `tests.test_individual_report_profiles` e os testes pertinentes de `tests.test_financial_report_profiles`; conferir defaults e seleção1005. Reviewer independente compara perfil inteiro com O/D/C/N1/P e o inventário da allowlist. Corrigir/revalidar achados materiais antes de B.

### B. Admissão dos quatro relatórios

- [ ] Testes RED de roster próprio, código opaco, origem td1/td3, ausência/zero/NA/NI/null/vazio, lexema/Decimal, ordem/hierarquia e rejeição de perspectiva/contrato cruzados.
- [ ] Implementar API individual explícita, com envelope/contrato/nomes próprios e mecanismo comum interno. A API financeira não passa a aceitar1006 por troca de parâmetro.
- [ ] Rodar `tests.test_individual_reports` e regressões pertinentes de `tests.test_financial_reports`, `tests.test_financial_reports_202503` e `tests.test_financial_reports_historical`.
- [ ] Executar admissão real no destino novo, com hashes externos. Conferir grade190200, 129nós/120folhas, todas as posições/observações/ausências, origens e estados. Confrontar lexemas e Decimal com os corpos exatos, sem float. Registrar contagens reais e limites.
- [ ] Reviewer independente confere código, dados/denominadores, conceitos/janelas/unidades e preservação. Nenhum aceite parcial vira PASS global; corrigir o recorte antes de C.

### C. Parquet, consulta e replay

- [ ] Testes RED de contratos/manifest/part trocados, tipo numérico local, binding largo, projeções por binding sem cast/UNION global automático, fonte adulterada e destino existente.
- [ ] Implementar conversão/leitura individual explícitas, mantendo grades textuais autoritativas, projeções locais e accessor Decimal exato. Metadados de origem e qualificações acompanham a saída.
- [ ] Rodar `tests.test_individual_reports_parquet`, `tests.test_financial_reports_parquet` e `tests.test_financial_reports_historical_parquet` conforme o delta.
- [ ] Converter o conjunto real; validar manifest fechado, schema/contagens/grades e consultar todas as projeções numéricas por binding, sem arredondar.
- [ ] Admitir e converter novamente em destinos de replay novos; comparar payloads/digest lógico e resultados exatos, qualificando timestamps de execução diferentes. Revalidar hashes de inputs/pilotos/11financeiros e executar leitura real dos 11 conjuntos financeiros com os leitores correntes; alteração dos leitores impede carry do PASS histórico.
- [ ] Reviewer independente aprova a composição e evidência antes de ampliar épocas/famílias. Este recorte não habilita prudencial nem outro período individual.

### D. Entrega e próxima fronteira

- [ ] Conferir diff completo, allowlist, hashes protegidos, SHA final, comandos/resultados e revisões parciais. Rodar o conjunto integrado pertinente uma vez; não declarar PASS global somando reruns isolados.
- [ ] Publicar PR com plano+perfil+código+testes necessários; CI existente, revisão final do SHA, integração, ancestry e CI pós-merge têm evidência própria. Sem PR artificial por trimestre/fatia.
- [ ] Atualizar63/mapa2 com o primeiro aceite individual e o restante selecionado: oferta348pares relatório/referência não é348snapshots aceitos. Financeiro11/66 é placar distinto.
- [ ] Próximo recorte decorre dos contratos/estruturas e fontes disponíveis, não de copiar perfil por trimestre. Prudencial requer cadastro próprio ainda não comprovado e coleta só depois do gate operacional59 e de contrato específico.

## Recursos e interrupção

Medição de 2026-10-10T18:52:15Z: RAM livre1784168448B, commit livre17310965760B, disco421581926400B. Não prova capacidade da admissão/conversão; medir por etapa e manter execução serial inicial, sem teto universal inventado. Usar supervisão/medição existente, sem instalar serviço ou alterar proteção.

Na primeira falha de integridade, persistência, recurso ou encerramento inconclusivo, preservar tentativa/logs/hashes e interromper a expansão. Não repetir lote, recuperar autoridade59, alterar segurança ou sobrescrever aceites. A execução offline não resolve automaticamente a regressão de persistência do Windows nem autoriza GET. Encerramento total63/64 exige todos os complementos escolhidos e base financeira completa, não apenas este primeiro recorte.

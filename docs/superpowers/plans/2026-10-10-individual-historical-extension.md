# Extensão individual genérica — execução da Issue 63

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` ou `superpowers:executing-plans`, com TDD e revisão independente antes de ampliar cada fatia. A PR pode reunir todas as fatias.

**Goal:** selecionar e processar a oferta individual por um mecanismo comum, congelando contextos próprios e comprovando os dois bundles adicionais arquivados sem mudar aceites anteriores.

**Architecture:** registry finito e perfis gerados na autoria; lookup sem bruto e os readers/adapters existentes. Novos contratos históricos individuais preservam o contrato202412 e as fronteiras1005/1006.

**Tech Stack:** Python e DuckDB já instalados no ambiente autorizado, JSON/CSV/Parquet; nenhuma instalação ou dependência adicional.

**Spec:** decisão de conteúdo62, contrato lógico existente e desenho/allowlist desta extensão na Issue63, comentário6101741520.

Estado: contrato revisado APP, execução da fatia E assumida no [claim6101807990](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/63#issuecomment-6101807990). Base integrada b0d886c2c4aff2b1fc6d1265d1c0be1765584dd2; branch codex/individual-historical-extension. CI pós-merge79 tem conferência própria antes de publicação desta extensão. Conteúdo aprovado na #62: quatro relatórios individuais em toda a oferta201003–202606; esta extensão constrói seleção/autoria/leitura comuns e valida os dois bundles adicionais já arquivados. Os demais períodos e o prudencial permanecem no aceite integral da #63.

## Decisão técnica e alternativas

Reutilizar compilador, autenticação, grade, reader e adapter existentes. Compilar deterministicamente na autoria; congelar contexto em perfil instalado gerado e referenciado por um registry individual finito. A consulta usa perfil instalado e bytes autenticados do snapshot, sem exigir bruto presente. Perfis são metadados gerados, não pipelines manuais por trimestre. Oferta inativa não significa fonte/aceite.

Alternativa descartada: recompilar de fontes brutas a cada leitura do Parquet; introduziria dependência operacional ausente no contrato corrente. Outra alternativa descartada: aceitar qualquer seleção/índice que tenha hash externo; integridade do caller não confere autoridade instalada. Não criar framework, banco global, transporte, camada, CLI ou dependência.

Preservar literalmente o perfil e os contratos202412, os defaults sem seleção, financeiro1005, pilotos e todos os aceites. Os novos períodos usam um único contrato histórico individual próprio, com namespace1006, seleção completa e caminho de part derivado da referência. Não reutilizar contrato financeiro ou unir grades numéricas globalmente.

## Allowlist e arquitetura

- Modificar `bank_quality/financial_report_profiles.py`: ofertas individuais, fontes/policy instaladas, autoria parametrizada, lookup de perfis; reutilizar os validadores existentes sem afrouxar regras financeiras.
- Modificar `bank_quality/financial_reports.py`: propagar seleção individual na autenticação/inventário/projeção; preservar APIs e contrato202412.
- Modificar `bank_quality/financial_reports_parquet.py` somente se necessário ao dispatch do contrato histórico individual; não refatorar por conveniência.
- Adicionar `bank_quality/individual-reports-registry.json`: oferta finita66refs e ativações por perfil/hash; bundles/policies próprios das fontes disponíveis. Sem aceitar paths arbitrários do caller.
- Adicionar `bank_quality/individual-reports-profiles/201012.json` e `202312.json`, gerados pelo autor comum. Nova pasta contém metadados instalados1006; paralela ao destino financeiro existente, evita misturar namespaces e não cria camada.
- Modificar os três testes individuais já existentes: `tests/test_individual_report_profiles.py`, `tests/test_individual_reports.py`, `tests/test_individual_reports_parquet.py`.
- Modificar `docs/architecture.md` e criar `docs/superpowers/plans/2026-10-10-individual-historical-extension.md` após claim e revisão. O plano202412 permanece histórico próprio; contrato/plano/evidência da extensão ficam juntos, sem ledger duplicado por rotina. Root é único integrador documental/Git.

Nenhum rename/delete, novo módulo ou raiz. Fora do escopo: acquisition, authority, runtime, pipeline financeiro, catálogo financeiro, registry/perfis financeiros, perfil individual202412, CI, segurança, deps, board, README, AGENTS, glossário, skills e qualquer GET. Dados novos ignorados em derived/curated com destinos novos por período/run/replay; fontes e saídas aceitas são protegidas.

## Fatia E — oferta, autoria e contexto por seleção

- [x] Escrever testes sintéticos autocontidos e observar RED causal antes da implementação.
- [x] Implementar somente oferta/autoria/contexto e gerar os candidatos locais; não admitir dados ainda.
- [x] Executar `python -B -m unittest discover -s tests -p test_individual_report_profiles.py -v` pelo runtime existente, registrar saída terminal e corrigir falhas.
- [x] Obter revisão independente do código/metadata/fontes e resolver achados antes de F. Perfis instalados só após aprovação da composição gerada e hashes.

Interfaces: `individual_descriptor_for_selection(selection)` resolve somente oferta instalada1006, sem bruto; `author_individual_profile(selection=None)` preserva default/resultado202412 e gera candidato de outra seleção somente com bundle instalado; `load_individual_context(selection=None)` preserva default202412 e carrega somente registry/perfil instalado das demais. Helpers internos de sources/autenticação/projeção propagam seleção explicitamente, sem global mutável; formas existentes sem argumento conservam202412.

Novos contratos: `ifdata-individual-reports-registry-v1`, `ifdata-individual-reports-historical-profile-v1`, `ifdata-individual-reports-historical-snapshot-v1`, `ifdata-individual-reports-historical-parquet-v1`. Índice existente `ifdata-individual-reports-sources-v1` permanece com seleção completa e hash externo. Perfis novos têm path `individual-reports-profiles/{period}.json`; cells part `parts/individual-cells-{period}.parquet`.202412 conserva seus contratos/path/hash exatos. Metadata do registry segue chaves existentes de descriptor (`selection`, `catalog`, `reports`, `source_offers`, `descriptor_sha256`, `profile_path`, `profile_sha256`), mais bundle/policy explícitos somente nos membros com fontes revisadas; hashes do caller não ativam nada.

- Ofertas66refs verificadas contra O/N pinados, preservando árvore, ordem Resumo/Ativo/Passivo/DRE, perspectiva e native_file literal, inclusive barra dupla2025. Os IDs variam por época; não inferir apenas por nome. Rejeitar seleção booleana, duplicada, fora de oferta, ordem/subconjunto ou perspectiva divergente.
- Bundle instalado próprio201012: C1976x28;202312:C1552x32;202412 permanece1585x38. Os tamanhos são checks de fonte, não modelo universal. Gerar todas as folhas a partir de td/a/lid/ifd nativos; sem padding ou filtro acadêmico.
- Política legada202312 explícita e finita: pins de manifest/corpo/proveniência/contexto, diagnóstico e captura originais. `truncated`/EOF/source_complete ausentes continuam desconhecidos; não fabricar conclusão bounded. Exceção financeiraD/N1 não se amplia para C1006 por associação. Policy202412 permanece idêntica. Resolver a policy1006 antes de qualquer ramo legado1005; projeção de C/D/N1 decoded202312 não pode reutilizar o texto fixo202412 de truncated=false/diagnóstico vazio. Projeção e validação preservam o diagnóstico literal e os campos ausentes.
- Autoria pode selecionar oferta autorizada; sem fontes próprias instaladas deve falhar antes da ativação. Geração não escreve automaticamente no pacote nem aceita override de perfil/root. Integrador instala somente após revisão.
- Metadados202412 conservam annotations atuais. Novas annotations são desconhecidas até haver evidência própria por binding; não copiar fid/unidade/janela de202412. Conferência de domínio determina o que a evidência permite registrar, sem cálculo, escala, anualização ou método acadêmico implícitos.
- TDD sintético autocontido por época, reconstrução determinística real dos dois candidatos e revisão independente do diff/fontes/metadados antes de ampliar para admissão. Testes públicos não dependem de data/.

## Fatia F — admissão, Parquet e conferência real dos dois períodos

- [ ] Escrever negativos/positivos de admissão/contexto/Parquet e observar RED antes do delta pertinente.
- [ ] Executar os módulos `test_individual_reports.py` e `test_individual_reports_parquet.py` com `unittest discover`, em testes públicos sem data/; registrar cada execução sem somá-las como PASS global.
- [ ] Revisão independente do código e dos testes antes de rodar a admissão/conversão real.
- [ ] Executar cada candidato/replay em destino novo, confrontar grade/projeções/accessor e proteção; obter revisão independente das evidências antes de G.

- Propagar contexto nos caminhos individuais existentes; autenticar inventário próprio e projeções com literal de timestamp preservado/UTC derivado. Cadastro, metadados, tokens, ausências, quantidade e precisão exata permanecem nativos.
- Testes sintéticos públicos exercitam28/32/38campos, mudança de IDs, múltiplas áreas anunciadas, ausência de fonte, contrato cruzado, adulteração repinada e leitura de Parquet sem bruto. Mantêm negativos de202412 e financeiros.
- Admitir201012 e202312 em destinos novos; confronto independente de toda grade com arquivos pinados e Decimal. Determinar contagens/precisão somente após leitura real.
- Converter, consultar todas as projeções/accessor, replay em destinos novos; medir recursos por processo/máquina e serializar execuções que disputam memória. Não inventar teto universal ou PASS global por soma de reexecuções.
- Revisão independente de código antes dos dados e dos dados antes de expansão. Rehash do inventário protegido, incluindo novo aceite202412; nenhum overwrite/retry de aquisição.

## Fatia G — composição e entrega

- [ ] Executar em processo único os nove módulos pertinentes (três individuais e seis financeiros correntes) a partir de exportação pública sem data/, como no gate de composição da PR79. Capturar imagem/import/HEAD/contagens/terminal; não usar código do checkout por engano.
- [ ] Regressão real202412 individual e11financeiros, somente se leitores comuns alterados; rehash protegido após o gate.
- [ ] Conferir diff/allowlist/hashes, obter revisão independente do SHA final e publicar o conjunto na PR própria da extensão.
- [ ] Conferir CI do SHA, integrar dentro da autorização existente, provar ancestralidade em main e CI pós-merge; atualizar63/2 sem fechar o objetivo parcial como entrega integral.

- Composição pertinente única numa exportação pública sem data/, depois de todas as alterações. Regressão real202412 individual e leitura dos11financeiros caso os leitores compartilhados mudem, com manifest/hash próprios e evidência independente.
- Comparar inventário final com allowlist, revisão independente do SHA entregue, CI, integração, ancestralidade e CI pós-merge. Não fechar#63 por três períodos aceitos.
- Atualizar mapa#2 e placar separado: financeiro11/66, individual aceites comprovados/66, prudencial ainda dependente de C1004/1009 e contrato próprio. Pesquisa de outras fontes pode avançar com ownership distinto; aquisição59 continua congelada.

## Pré-flight e controle da execução

Contrato/direção técnica, assinaturas, guardas de captura/projeção e inventário de fontes revisados APP antes do claim. Root preserva o inventário explícito de1.431arquivos, SHA8502f159c9e2a3d9c7ee010f17d9144a1684db59f6c13c2b16d790654445597f, incluindo202412individual e os11financeiros. Oito destinos novos derived/curated201012/202312run1/replay conferidos ausentes. Evidência e comandos em workspace privado ignorado; nenhum bruto/headers integrais/chave neste diff. E começa após preflight; F depende de E APP; G depende do aceite F. Estado de implementação não se confunde com contrato APP.

## Inventário finito de fontes do lote inicial

Cada corpo é adjacente ao manifest. Audit read-only de dez pares em2026-10-10 confirmou tamanho e SHA; inventário privado a85ddda777d809aaf02bc161e2c7a291e9c0532070f4748d4083b8d7bbdbf56d. O/P compartilhados são os mesmos pins202412.

| Referência/papel | Manifest | SHA manifest | SHA corpo / bytes |
|---|---|---|---|
| 201012/cadaster | data/raw/discovery-20261001/20261001T013233187408Z_portal_cadastro_201012_357cd54cfbe74ee8abf53155089380a2.json | 81f06a59d1ccacc9d2c4367c6dba305c1ff7e848d627da53a3afb8fb9fd36c13 | 49ff09d550bccbc401e016f6b7427b5e6ca475c8272d8654e9f46e698d0a9ddc / 802981 |
| 201012/dictionary | data/raw/discovery-20261001/20261001T013234212213Z_portal_info_201012_c47cbdb67f7d406db3615157e4feeff5.json | 504eb1cbd6f0308a8690018718036afea1f96229f270adfef8d0a89ccb9315d6 | aa32c85142afecb62c9a5999af1ee220246d9aa1383bc416a5c251177d0f03bb / 123407 |
| 201012/numeric:1 | data/raw/discovery-20261001/20261001T021817135894Z_portal_numeric_input_201012_1_19f951eb0f824a478d38f47c733f673b.json | 4f4a5fda8b2935540c6275ba1054e9ace1f03b680535a607dab28b0c15548f69 | 0df2240eb38b1e2a6b562d2cce50c806c85d390d3bf5d3bf0adf02d73bcee72f / 5073899 |
| 201012/catalog | data/raw/financial-cadaster-202412-20261003/20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json | b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7 | 2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07 / 13527657 |
| 201012/portal | data/raw/discovery-20261001/20261001T012756759142Z_portal_56229187f15948a0a353b4b194b7cb3f.json | 5757f812b56dbd414e2fa3d68075cafbf50157a010a9b4b330126fab86dd211a | 234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153 / 92483 |
| 202312/cadaster | data/runs/expansion-202312-20261001/raw/2026-10-01T033720561Z_202312_9446f017-d1c2-48d2-84c8-5d6e41bc03d7.json | 1241793d4ddce44040980b7db4033d4eedb8a0207d05a616ddc6aa58aa83eb2a | da6e6e4bbdfbac6be3a35e31c9dd5e1c11eb76b11b0d69888e1ac40edb65f354 / 705954 |
| 202312/dictionary | data/runs/expansion-202312-20261001/raw/2026-10-01T033720509Z_202312_e1bacaca-f0b3-4c23-a40d-8defa2891ca2.json | f26d028164139e20faa2094b31bab08e8fbcd1410b28bd917b406018cf2c0425 | 11a0704ec62d3123c8af2ceb7c98b545c683781e297f8a3f4d89e449122c7ee2 / 174579 |
| 202312/numeric:1 | data/runs/expansion-202312-20261001/raw/2026-10-01T033724367Z_202312_5477956f-562c-4989-acdb-a72c933a3d42.json | 9d35989367a25ab9ae12551c8a5f6ddf7c51249d6a0f181bd34240f63a74e6db | fb85523b59409bb6ebc8bb32bf78751a2380eea3b880873f27331398e5511eae / 15316532 |
| 202312/catalog | data/raw/financial-cadaster-202412-20261003/20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json | b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7 | 2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07 / 13527657 |
| 202312/portal | data/raw/discovery-20261001/20261001T012756759142Z_portal_56229187f15948a0a353b4b194b7cb3f.json | 5757f812b56dbd414e2fa3d68075cafbf50157a010a9b4b330126fab86dd211a | 234fcb9158bd25b222625418f2d775d438a8db8df1585e65ef1b40c7a7fb0153 / 92483 |

## Checkpoint E — oferta/autoria/contextos

APP independente do candidato E:66ofertas/árvores confrontadas com O/N autenticados, dez pins/policies/projeções conferidos, captura decoded202312 própria e lookup sem bruto. Perfis gerados201012 SHA299e53987172ca6482534afee6845c4e367a07dcfb1126cf10f0ae439b1fb489 e202312 SHAe205464bf881254f3082fa1ca9bd6b6f74f5f07cd49b93441337fac84feef022; registry SHA6d09d583e4b4a039a5db305889e8a2c3eb35b9a88bcec47656ea2f1077a11fe6. Default/perfil202412 e regras1005 preservados. Descriptor da oferta integral202412 difere do recorte ativo legado C/D/N1; F conserva o caminho legado.

Composição pertinente única `.venv/Scripts/python.exe -B -m unittest discover -s tests -p '*report_profiles.py' -v`:44testes (28financeiros+16individuais),141.306s, OK/exit0, término2026-10-10T20:30:36.6095641Z. RED causal inicial deinterfaces e RED adicional de sourceofferduplicado precederam os respectivos fixes. Sem soma de GREENs intermediários nem alegação de fullsuite.

O código testado f87c2e077d559d4a4fbd4dbae390bd0b503c16fa845367a2a65cbbdb20b6a241 recebeu apenas trim de newlineEOF: final684ee37a26f8c1cfc719bf4a864f3ee9dca537d1e4074d754e8742d2560d4e3c. Revisão reconstruiu o hash testado substituindo somente o suffix final; gitdiff--checkPASS, sem repetir testes por formatação. Esta identidade é física Windows, distinta dos blobs LF do Git.

CI pós-merge79 no baseb0d886c confirmada SUCCESS728testes/20skips,696.976s+guards+portal. EAPP permite F; nenhum novo aceite de dados ou Parquet foi declarado por metadata/fixture. Issue63 continua aberta para toda a oferta e prudencial.
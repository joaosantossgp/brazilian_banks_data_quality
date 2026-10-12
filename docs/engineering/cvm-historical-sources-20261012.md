# Fontes históricas CVM: contrato documental A1, 2010–2024

Pesquisa de **2026-10-12**, [Issue 102](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/102), derivada da [frente CVM–IF.data](cvm-ifdata-identity-methodology-plan-20261012.md). Pesquisador A1; integrador Root. Base `6535862eed9bce9cfaaaa29b9064cfc8045a5a65`, branch `codex/cvm-ifdata-front-20261012`. Esta nota entrega inventário documental e contrato proposto de aquisição; **nenhum corpo CAD/FCA/FRE de companhias foi adquirido nesta fatia**. Revisão independente e registro do contrato A2 pelo integrador precedem GET de datasets.

Destino público único desta fatia: este arquivo em `docs/engineering/`, responsabilidade documental existente conforme [arquitetura](../architecture.md#organização-dos-arquivos-e-pastas). Evidência de pesquisa privada em `.scratch/cvm-front-20261012/a1/`. Sem código de produção, dependência, camada, commit, alteração de Issue ou Project. Código, dados e evidências aceitas continuam preservados.

## Resultado e alcance

**Recomendação:** adquirir primeiro um snapshot CAD e os quinze FCA anuais 2010–2024, preservando bruto e extraindo somente índice documental, informações gerais e valores mobiliários. São 16 recursos de dados finitos, com **7.393.039 bytes anunciados por HEAD** nesta consulta. FCA documenta categoria, situação, identidade e datas de listagem/negociação; o cadastro atual funciona como conferência atual, sem substituir histórico. A presença dos quinze arquivos não demonstra cobertura dos emissores, documentos ou eventos. [CAD](https://dados.cvm.gov.br/dataset/cia_aberta-cad), [FCA](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca), [índice FCA](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/).

FRE é a fonte estruturada candidata para participações, acionistas/controladores e reorganizações. O transporte anual agrega seções financeiras e outros conteúdos fora do objetivo. Assim, a etapa principal acima não inclui GET de FRE; a extensão societária abaixo tem recursos/membros/campos finitos, mas depende de contrato explícito para o bruto incidental e de revisão dos esquemas observados. Não importar DFP/ITR, valores financeiros FRE, nem balanços CVM para complementar o IF.data. [FRE](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre).

Não houve levantamento sistemático exaustivo de documentos de cada companhia, reconstrução de intervalos, seleção da amostra, certificação de identidade ou comparação econômica. Outras financeiras fora IF.data não foram adquiridas; eventual reaproveitamento deste cadastro é apenas possibilidade documental.

## Fontes e temporalidade

| Fonte / localizador | Papel observado | Limite e tratamento |
|---|---|---|
| [CAD](https://dados.cvm.gov.br/dataset/cia_aberta-cad), descrição e periodicidade | Snapshot referente ao último dia útil; atualização diária | Não é histórico diário; `DT_REG`, `DT_CANCEL`, `DT_INI_CATEG`, `DT_INI_SIT` e `DT_INI_SIT_EMISSOR` são datas de atributos/eventos, não todas as transições anteriores |
| [FCA](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca), conteúdo estruturado e histórico | Informações gerais/valores mobiliários e outras seções cadastrais; atualização semanal com reapresentações; histórico anunciado desde 2010 | Histórico inclui arquivos fora da política corrente. O índice confirma nomes de arquivos, sem provar documentos/versionamento completos |
| [FRE](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre), seções 6, 8, 9, 15 da descrição legada; notas 2016/2023 | Histórico do emissor, reestruturações, participações e posição acionária | `grupo_economico_reestruturacao` descontinuada no formulário vigente desde 2016; nova versão desde 2023. Ausência de membro exige classificação por versão, não ausência de evento |
| [ICVM 480 original](https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/instrucoes/anexos/400/inst480.pdf), arts. 1–2, pp. 1–2; arts. 63–64, pp. 28–29 | Registro e categorias A/B; entrada em vigor 2010-01-01 e transição dos registros anteriores | Categoria A permite quaisquer valores mobiliários; B exclui ações/certificados e hipóteses conversíveis previstas. Autorização não prova negociação efetiva. Texto original não incorpora todas as alterações posteriores |
| [RCVM 80 original](https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol080.pdf), arts. 2–3, PDF pp. 1–2; arts. 23–25, pp. 9–10; arts. 69–70, p. 30 | Reitera distinção de registro/categorias; FCA atualizado por alteração e confirmação anual; FRE periódico/eventual; vigência 2022-05-02, revoga ICVM 480 | Leitura normativa de contexto, sem aplicar redação atual retrospectivamente; revisar alterações vigentes ao interpretar uma data. Prazo de entrega não é data de vigência de relação |

A leitura normativa cruzou categorias, obrigações documentais e disposições de vigência; não dependeu de uma única página. As páginas são contadas a partir de 1 no PDF. A ICVM traz também numeração impressa. Os PDFs foram consultados pela ferramenta web; download documental direto retornou HTTP 403, sem corpo/hash local autenticado. Nenhuma afirmação sobre companhia se apoia só nesses textos.

Separar pelo menos: ano do recurso; `Data_Referencia`/`DT_REFER`; recebimento `DT_RECEB` quando presente; `Versao`/`VERSAO`; geração HTTP (`Last-Modified`, `ETag`); recuperação UTC; datas específicas de categoria, situação, composição acionária, alteração e operação. Ano do ZIP não será convertido automaticamente em intervalo janeiro–dezembro. Data de composição acionária e data do documento podem divergir. Reapresentação posterior pode alterar declaração anterior; recuperação atual não prova informação disponível no passado.

**Registro, categoria, instrumento e listagem são quatro perguntas.** Conservar os campos nativos; não selecionar companhias apenas por status atual, ticker ou nome. FCA permite buscar instrumentos e datas declaradas de listagem/negociação. Se o critério acadêmico escolhido exigir efetiva listagem/negociação, conferir prova histórica B3 da classe/instrumento e seu intervalo em contrato próprio. Nenhum campo FCA cria automaticamente a decisão de elegibilidade da [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

## Inventário finito e custo observado

HEAD legítimo, sem Range/GET de payload, em **2026-10-12T17:22:09Z** aproximadamente; 31 respostas HTTP 200, com `Content-Length`. Bytes são comprimentos declarados dos objetos comprimidos, sujeitos a alteração; não equivalem a memória, tamanho descomprimido ou hash. Proveniência completa privada em `resource-head-provenance.json`.

URL CAD única: [cad_cia_aberta.csv](https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv), **1.493.831 bytes**. Para cada linha abaixo, URLs exatas são o prefixo [FCA/DADOS/](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/) + `fca_cia_aberta_ANO.zip` e [FRE/DADOS/](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/) + `fre_cia_aberta_ANO.zip`; `ANO` é exclusivamente um dos quinze anos listados.

| Ano | FCA bytes | FRE bytes |
|---|---:|---:|
| 2010 | 337720 | 6327657 |
| 2011 | 381161 | 7050662 |
| 2012 | 381058 | 7427318 |
| 2013 | 373007 | 7741288 |
| 2014 | 384748 | 7929118 |
| 2015 | 380898 | 7853370 |
| 2016 | 376154 | 7583877 |
| 2017 | 375132 | 7605478 |
| 2018 | 381642 | 7824065 |
| 2019 | 371770 | 7935765 |
| 2020 | 405892 | 9233986 |
| 2021 | 465704 | 10494738 |
| 2022 | 458286 | 10754865 |
| 2023 | 434044 | 8132900 |
| 2024 | 391992 | 8409664 |
| Total | **5899208** | **122304751** |

Índices inspecionados também anunciam 2025/2026, excluídos do recorte. As datas exibidas pelo HTML não declaram fuso; usar valores HTTP UTC preservados, sem equiparar modificação do arquivo a evento societário. Documentos de dicionário abaixo foram adquiridos; **não são datasets de companhias**.

## Esquemas documentados e allowlist proposta

Os dicionários atuais são uma âncora documental, **não uma prova de esquema retroativo**. Contêm dez membros TXT no ZIP FCA e cinquenta no FRE. Alguns campos FRE têm descrição/domínio vazios: conservar a lacuna e consultar o formulário/norma correspondente antes de interpretar. Descrições e nomes de arquivos na página FRE às vezes usam prefixo `fre_cia_`, enquanto os dicionários usam `meta_fre_cia_aberta_`; o membro de dados real precisa ser conferido, sem alias silencioso.

### Principal CAD/FCA

CAD: projetar apenas `CD_CVM`, `CNPJ_CIA`, `DENOM_SOCIAL`, `DENOM_COMERC`, `DT_REG`, `DT_CONST`, `DT_CANCEL`, `MOTIVO_CANCEL`, `SIT`, `DT_INI_SIT`, `SIT_EMISSOR`, `DT_INI_SIT_EMISSOR`, `CATEG_REG`, `DT_INI_CATEG`, `SETOR_ATIV`, `CONTROLE_ACIONARIO`, `TP_MERC`, `PAIS`. Não publicar contatos pessoais/endereço/telefone/auditor; bruto integral fica em destino ignorado autenticado. Dicionário CAD descreve CNPJ como texto e código CVM como numeric; **ambos serão preservados como texto recebido**, sem perda de zeros.

Em cada ZIP FCA: extrair somente `fca_cia_aberta_ANO.csv`, `fca_cia_aberta_geral_ANO.csv` e `fca_cia_aberta_valor_mobiliario_ANO.csv`, se presentes com esses nomes exatos após inspeção. Nomes ainda não observados no ZIP de dados: ausência/diferença bloqueia a admissão daquele membro até revisão. Os demais membros permanecem apenas no bruto comprimido, sem extração/admissão. Não abrir automaticamente `LINK_DOC`.

| Membro lógico / dicionário | Projeção permitida e finalidade |
|---|---|
| Índice FCA, `meta_fca_cia_aberta.txt` | `CATEG_DOC`, `CD_CVM`, `CNPJ_CIA`, `DENOM_CIA`, `DT_RECEB`, `DT_REFER`, `ID_DOC`, `LINK_DOC`, `VERSAO`; rastrear documentos e recebimento. Página só promete links dos últimos cinco anos; falta histórica de índice/link será lacuna explícita, sem fabricar recebimento |
| Geral, `meta_fca_cia_aberta_geral.txt` | Todos os 26 campos documentados, finitos no dicionário pinado: identidade, denominações, categoria/situação/datas, atividade/setor, espécie de controle/data, constituição, países, encerramento de exercício e página web. `Especie_Controle_Acionario` não identifica controlador/CNPJ nem equivale a tipo institucional IF.data |
| Valores mobiliários, `meta_fca_cia_aberta_valor_mobiliario.txt` | Todos os 18 campos documentados: identidade documental, instrumento/classe/unit, ticker, entidade administradora, mercado/segmento e quatro datas de início/fim listagem/negociação. Relação um-para-muitos; ticker não é chave de pessoa jurídica |

Campos comuns FCA estruturado: `CNPJ_Companhia`, `Data_Referencia`, `ID_Documento`, `Versao`; geral acrescenta `Codigo_CVM`. Não presumir que todos os membros carreguem código CVM. Quantidade de campos do dicionário não garante posição/ordem física nem presença histórica de coluna.

### Extensão FRE societária, condicionada

Primeiro diagnóstico proposto: **somente anos 2010 e 2024** para os três casos, seis tabelas lógicas no máximo conforme abaixo. Transporte desses dois ZIPs: **14.737.321 bytes por HEAD**; não expandir aos quinze anos antes da revisão da primeira prova. Para investigar rupturas, 2015/2016 e 2022/2023 são lotes posteriores candidatos, nunca aquisição automática.

| Membro lógico / dicionário exato no ZIP META | Campos/uso autorizáveis; exclusões |
|---|---|
| Índice, `meta_fre_cia_aberta.txt` | Nove campos documentados `CATEG_DOC`, `CD_CVM`, `CNPJ_CIA`, `DENOM_CIA`, `DT_RECEB`, `DT_REFER`, `ID_DOC`, `LINK_DOC`, `VERSAO`; não seguir links automaticamente |
| Histórico, `meta_fre_cia_aberta_historico_emissor.txt` | Todos os doze campos documentados, incluindo `Data_Registro_Emissor`, `Data_Constituicao_Emissor`, `Requisicao_Registro_Emissor`, `Forma_Constituicao_Emissor`; campos de descrição vazia não ganham significado inventado |
| Participação, `meta_fre_cia_aberta_participacao_sociedade.txt` | `CNPJ_Companhia`, `Data_Referencia`, `ID_Documento`, `Nome_Companhia`, `Versao`, `CNPJ`, `Codigo_CVM`, `Tipo_Sociedade`, `UF_Sede`, `Razao_Aquisicao_Manutencao`, `Descricao_Atividades`, `Razao_Social`, `Participacao_Emissor`, `Possui_Registro_CVM`, `Municipio_Sede`, `Pais_Sede`, `ID_Sociedade`. **Excluir** `Valor_Contabil`, `Valor_Mercado`, `Data_Valor_Contabil`, `Data_Valor_Mercado`; participação é metadado societário, sem uso como medida financeira |
| Posição, `meta_fre_cia_aberta_posicao_acionaria.txt` | Identidade documental + `Acionista`, `Acionista_Controlador`, `Acionista_Relacionado`, `CPF_CNPJ_Acionista`, `CPF_CNPJ_Acionista_Relacionado`, `Tipo_Pessoa_Acionista`, `Tipo_Pessoa_Acionista_Relacionado`, `ID_Acionista`, `ID_Acionista_Relacionado`, `Data_Composicao_Capital_Social`, `Data_Ultima_Alteracao`, `Participante_Acordo_Acionistas`. Projetar apenas pessoas jurídicas dos casos delimitados e relações entre elas; não publicar CPF/representantes de pessoa natural. `Acionista_Controlador` tem domínio S/N; CNPJ relacionado pode ser vazio e não prova cadeia completa |
| Posição por classe, `meta_fre_cia_aberta_posicao_acionaria_classe_acao.txt` | Inventariada para etapa posterior; **não admitida no primeiro recorte**, pois não necessária para identificar as pontas jurídicas |
| Reestruturação, `meta_fre_cia_aberta_grupo_economico_reestruturacao.txt` | Oito campos documentados: identidade documental, `Data_Operacao`, `Descricao_Operacao`, `Evento_Societario`; somente épocas em que o formulário aplica. Texto não prova automaticamente sucessão, controle ou CNPJ das pontas |

O conjunto principal não adquire FRE. Se Root registrar extensão FRE, explicitar na Issue que o ZIP bruto de transporte contém conteúdos incidentais fora da projeção, destino ignorado e retenção para auditoria; esses membros/valores nunca são admitidos no pacote consultável. Se o contrato proibir até o trânsito/armazenamento desses bytes, **bloquear GET do ZIP** e usar documentação societária individual, com URL/destino/limite registrados antes. Não alegar aquisição estritamente sem conteúdo financeiro quando o bruto contém tais seções.

## Contrato de aquisição/admissão a registrar antes de A2

Destinos propostos, ainda **não criados**: `data/raw/cvm-identity-20261012/` para bruto documental/datasets e manifest imutável; `data/curated/cvm-identity-20261012/` para projeções textuais/checks/manifest; `data/runs/cvm-identity-receipt-20261012.json` para recibo final. Owner Root/executor exclusivo; inventário exato de arquivos e revisão independentes antes da coleta. Pastas são instâncias das responsabilidades canônicas existentes, sem nova camada. Reexecução exige novo destino, nunca overwrite de aceitos. Código/parser/testes precisam de allowlist própria na Issue.

1. **Pré-voo finito:** pin do contrato/dicionários; HEAD atual dos 16 recursos principais; espaço disponível medido e orçamento local. Piloto sequencial 2010/2024 antes da expansão. Definir limites locais de bytes/descompressão/tempo por máquina; não apresentar totais comprimidos como capacidade integral. Mudança de tamanho desde esta pesquisa é revisão de fonte, não erro por si: registrar, aceitar orçamento explicitamente e não continuar ilimitadamente.
2. **Recuperação:** HTTPS em domínio oficial e lista fechada, sem descoberta recursiva ou seguir links de empresa. Guardar URL inicial/final, método/parâmetros, UTC de início/fim, status, tamanho efetivo, headers diagnósticos sanitizados e SHA-256 do corpo. Não divulgar `Set-Cookie`/tokens; headers privados de pesquisa não serão publicados em bruto. HTTP não-200, HTML de bloqueio, corpo vazio ou truncado falha; reter diagnóstico, não tratar como população vazia. Pin externo do manifest final e hashes dos membros usados.
3. **ZIP:** conferir assinatura, diretório, CRC e comprimentos, rejeitar membros duplicados, paths absolutos/traversal/symlink/encriptados e expansão além do orçamento; não extrair tudo. Registrar inventário integral de nomes/tamanhos/hashes dos membros extraídos. Ausência de membro, arquivo apenas com cabeçalho e zero linhas são estados distintos. Sem membro oficial verificado não afirmar cobertura zero.
4. **CSV/encoding:** preservar bytes originais; no diagnóstico autorizado observar cabeçalho/delimitador/aspas/terminadores/encoding por membro. Perfil candidato usa `;`, aspas duplas e encoding Latin-1; **não confirmados em payload nesta A1**. Os TXT documentais foram decodificáveis em Latin-1 e CAD não é UTF-8 válido, mas isso não prova ISO-8859-1 de todos os CSVs nem distingue CP1252. Fixar perfil após amostra e validação de acentos/bytes; sem `errors=replace`, descarte de linhas ou fallback silencioso. Suportar campos citados/multilinha, contar registros lógicos e exigir largura igual ao cabeçalho; falha de parsing interrompe membro, sem aceite parcial oculto.
5. **Schemas:** mapear por nome exato, dicionário/hash, família/ano e schema observado. Registrar cabeçalhos ordenados/hash, colunas ausentes/novas e cobertura por membro. Mudança não mapeada bloqueia admissão; revisão pode autorizar perfil histórico distinto. Não padronizar cabeçalhos/valores por aproximação nem supor continuidade nas rupturas 2016/2023. Metadados atuais não são versionamento completo do esquema histórico.
6. **Valores/chaves:** todas as colunas de entrada textuais; CNPJ normalizado só por remoção auditável de pontuação de CNPJ completo válido, sem completar oito dígitos; código CVM raw conservado, chave derivada de dígitos só com regra explícita que trate zeros de apresentação e confira CNPJ. Manter `namespace`, corpo/membro/hash, número de registro lógico e conteúdo textual como chave física. Chave documental candidata `(família, CNPJ, Data_Referencia, Versao, ID_Documento)` exige teste de consistência; não declarar chave única de participação/valor mobiliário, que são um-para-muitos. Não unir só por nome nem colapsar linhas distintas.
7. **Datas/revisões:** parse derivado de datas documentadas `AAAA-MM-DD`, preservando raw/vazio. Validar calendário e cronologia da relação; final anterior ao início é conflito, não correção automática. Preservar todas as versões observadas. Mesmo ID/versão com bytes divergentes conserva conflito de vintage. Sem recebimento histórico não simular corte de informação disponível à época. Maior versão não vira verdade temporal por default; qualquer seleção precisa de política registrada com empates/conflitos recusados. Vazio, coluna ausente, documento ausente, falha e zero continuam distintos.
8. **Aceite:** checks de transporte/parsing/esquema, reconciliação de contagens brutas/projetadas/filtradas e exceções por ano/membro/documento; replay determinístico em novo destino; hashes protegidos anteriores; revisão independente do pacote e de cada prova. Manifest/recibo final só após checks pertinentes. Cobertura anunciada, adquirida, parseada, admitida e identidade aceita são contagens diferentes.

## Prova A2: requisitos por caso e saída verificável

Primeiras referências propostas **2010-12-31 e 2024-12-31**, já presentes no [dossiê](capital-aberto-identity-dossier.md); a disponibilidade de documentos para elas será medida. Capturar os quinze FCA pode oferecer outros documentos, mas o primeiro aceite de vínculos continua restrito a seis combinações emissor/data. FRE 2010/2024 é diagnóstico condicionado; datas da posição/documento diferentes da referência produzem lacuna até prova de intervalo fechado, sem interpolação.

| Caso | Candidato local reutilizado, sem nova autenticação nesta pesquisa | Evidência exigida / lacuna que impede aceite |
|---|---|---|
| Banco do Brasil | Código CVM 1023; IF.data individual c0 `0` no dossiê | CNPJ legal completo de emissor e unidade na referência + identidade de namespace/código; zeros ou nome não estabelecem a ponta BCB. FCA pode confirmar emissor, sem resolver automaticamente identidade IF.data |
| Bradesco | Código CVM 906; cadastro atual com CNPJ completo no dossiê | Identidade completa das duas pontas datada; CNPJ atual concordante com B3 não basta para 2010/2024. Conferir instrumento/listagem separadamente se exigidos pelo método |
| Itaú Holding / banco operacional | Emissor CVM 19348; candidatos IF.data c0 `60872504` holding e `60701190` banco | Manter holding e banco separados. `same_legal_entity` requer CNPJs completos iguais; `controls` exige duas pontas diferentes, relação explícita e vigência. `Participacao_Emissor` sem semântica/controle/vigência comprovados não basta. Pertencimento a conglomerado exige evidência BCB própria, não só FRE |

Reusar `identity_evidence` e contrato já documentado: prova pontual exatamente na referência ou intervalo fechado contendo-a, CNPJs completos textuais, códigos/namespaces exatos, relação explícita, fonte primária URL/hash/UTC/localizador. Se não conseguir uma ponta/data, entregar `unknown` e razão verificável. Ausência de companhia no arquivo não é cancelamento/listagem negativa. Não promover registro atual, oito dígitos, nome, classe ou ticker a identidade histórica.

Cada linha de prova deve trazer recurso/hash/membro/registro/documento/versão, duas pontas, relação, datas de declaração/evento/vigência, referência testada, resultado e limites. Conferir cardinalidades: múltiplas classes não multiplicam emissores; acionistas repetidos por versão não multiplicam participações; controle não autoriza substituir holding por banco nem somar as duas perspectivas. Nenhum cálculo de indicadores ou regra de amostra decorre do sucesso destes casos.

## Proveniência documental e inventário de pesquisa

Recuperações GET documentais HTTP 200 em 2026-10-12; corpos locais privados e hashes abaixo. Cada URL é fonte oficial e localizador do objeto. Páginas HTML/dicionários mudam; os hashes identificam os bytes desta consulta, sem afirmar assinatura institucional. Datas UTC completas e headers estão no manifest privado.

| Objeto / URL | UTC | Bytes | SHA-256 |
|---|---|---:|---|
| [Dicionário CAD](https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/META/meta_cad_cia_aberta.txt) | 17:20:35Z | 8452 | `3bb4c788ad8e9cefd024e4d241fcde41270116fd37fb31ad53a4a6984ab43255` |
| [Dicionário FCA ZIP](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/META/fca_cia_aberta.zip) | 17:21:12Z | 6748 | `15fade6b283cfcb183c24e68fb38277747166a9dae081ad0faf68d8907b1e785` |
| [Dicionário FRE ZIP](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/META/meta_fre_cia_aberta.zip) | 17:20:35Z | 32148 | `c41bfcf693876a79ba71a817edede81a8fe38d62cee71f1bdf664bf05a454b5c` |
| [Índice FCA](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/) | 17:20:35Z | 3972 | `e7fbdb095f7a211b718ac990d24d10cc84adb36a06c6a1d25617e637b1280e25` |
| [Índice FRE](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/) | 17:20:35Z | 3972 | `e6cf28cf6c8400fb712d0e439ca62cb8ad7baf95d6aa6d0d548bce61b0ce62e3` |
| [Página CAD](https://dados.cvm.gov.br/dataset/cia_aberta-cad) | 17:22:10Z | 25762 | `1989ca6fb138fceebbb33a2784909cca43f06d8d9d195d82f94b6f0c8509b793` |
| [Página FCA](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca) | 17:22:10Z | 35769 | `06a38a70a462c4dee37e36c9e1ce3f0173fa0fd890bc1876a883f433513adc41` |
| [Página FRE](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre) | 17:22:10Z | 45636 | `bf16157d7e7351afcd48b27bc59996aead09de4e972fd5fa95e074ed0eca60de` |

Localizadores de campos são os blocos `Campo: NOME` nos TXT contidos no ZIP. Hashes de membros prioritários: FCA geral `39240c71a47f4b677ac479229d4e30a4e7aab361ccb99d34251be87ca771409c`; FCA valor mobiliário `4bf3c9376ea4c86f28be62aae8ef3e7fbe39eaaf2b68379cc34765b9dcf550ef`; FRE histórico `fe0e5e529d0cdd7744a32872a704730178137532c4eac4db4857f923fe396d87`; FRE participação `d549720ab3cd62f9b63e24fa5aea9593bf1194670f47d8a12abf450226a4c57e`; FRE reestruturação `f04df6a31791af6902c0ead32ee52180ee3f0b56ddc0cca712cb2122a52e2e37`.

Inventário privado: oito corpos documentais acima, sessenta TXT extraídos dos dois ZIPs, `document-provenance.json` e `resource-head-provenance.json`. O primeiro conserva também a tentativa incorreta `.../FCA/META/meta_fca_cia_aberta.zip` (404; endereço corrigido pelo índice oficial) e dois downloads de PDFs (403). Erros não viraram objetos autenticados. O manifest HEAD mede os 31 objetos sem baixar seus corpos. Headers privados podem conter cookies públicos de sessão do servidor; não integrar esses manifests sem sanitização. Hashes dos manifests privados, antes de qualquer transformação: documental `2eeade2483281df499606608636f38e939b54bc67f48eac1a2bd2813b72284e3`; HEAD `7e8a325ee26244292e40d56b676a27fd8bb831b303ee62623b78211e2217a50e`.

**Skills/mecanismo:** lidas `research`, Feynman `deep-research` e `pdf-explore` locais, conforme Issue. Pesquisa delegada por Root; não foi criada delegação adicional. `/deepresearch` indisponível: workflow automático não executado, sem runtime novo. Fallback real foi web/fontes CVM, leitura cruzada de PDFs e recuperação documental pequena/hash/HEAD via transporte local. Screenshot do PDF ICVM falhou; o texto multipágina estava acessível. Context7 não foi necessário para esta investigação de fontes/domínio, sem consulta de API de biblioteca. Proveniência integrada à nota canônica, sem pasta pública `outputs/` concorrente.

## Verificação e handoff

Verificações executadas nesta fatia: Issue real/labels/base; links locais de entrada e arquitetura; GET/hash de oito objetos documentais; inspeção dos dois ZIPs de dicionários e dos campos pertinentes; HEAD dos 31 recursos; soma dos comprimentos; leitura normativa multipágina; inventário da escrita pública restrita a esta nota. Não foram executados testes de software, parsing de datasets, replay ou revisão independente nesta A1. O integrador registra revisão do snapshot e contrato A2 antes de ampliar.

Pendências materiais: membros/cabeçalhos/encoding efetivos dos ZIPs anuais; cobertura de documentos/versões por companhia; índices/recebimentos antigos; vigência das relações; pontas jurídicas BCB; autorização explícita do transporte incidental FRE; evidência histórica B3 conforme critério futuro. O primeiro pacote CAD/FCA pode avançar depois do gate A1; relações societárias podem encerrar com lacuna comprovada. Decisões acadêmicas continuam na #3 e fronteira de execução no mapa #2 sob Root, sem operação do Project /3.

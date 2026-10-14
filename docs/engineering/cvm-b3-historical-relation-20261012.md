# Relação histórica CVM–B3–IF.data: execução e preservação acadêmica

[Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108). Registro em andamento, iniciado em 12/10/2026. Não constitui declaração de conclusão da relação histórica ou de cobertura integral da B3.

## Objetivo e escolhas registradas

Período da monografia: 2010–2024, com 60 referências trimestrais. Conglomerados financeiros são a unidade principal; instituições individuais são complementares. Ações, units e BDRs têm a mesma prioridade. Identificação do emissor, participação societária, presença documental de instrumento e participação nativa em conglomerado são relações distintas, com datas e fontes próprias. Fórmulas, critérios finais de amostra e comparabilidade dos indicadores continuam sujeitos à decisão acadêmica na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

O [desenho](../superpowers/specs/2026-10-12-cvm-b3-history-design.md) e o [plano](../superpowers/plans/2026-10-12-cvm-b3-history.md) delimitam admissão, verificações, consulta e revisão por fatias. Dados financeiros permanecem provenientes do IF.data; documentos CVM/B3/SEC são usados nesta entrega para metadados de identidade, controle e instrumentos.

## Preservação e referência posterior

**Direção de João em2026-10-13:** relações de CNPJ, notícias e pesquisa podem fundamentar a identificação, sem documento jurídico formal para cada ligação. Conservar origem, natureza, grau de confiança, conflitos e alcance temporal da informação. A [decisão na Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6146912313) substitui o gate de comprovação jurídica individual; não transforma dado corrente em vigência histórica contínua. O código v1 ainda conserva os estados técnicos originais; novas fontes e sua aplicação analítica ficam autorizadas para a retomada.

João pediu publicar código e snapshot para continuar em computador mais forte. Novas execuções pesadas locais e implementação da normalização foram suspensas. A normalização v2 é **proposta técnica revisada, não implementada**; o software preservado é v1/oitoCSV. O [handoff específico](cvm-b3-handoff-20261013.md) reúne o estado, a restauração e os próximos passos. Publicação do transporte, restauração no destino, processamento real e conclusão da pesquisa são estados separados.

João reiterou expressamente a necessidade de guardar as evidências para possível referência acadêmica. Os originais permanecem nos destinos de captura; cópias de preservação não os substituem. Cada captura registra URL, recuperação UTC, status, metadados de resposta, completude e SHA-256. Tentativas malsucedidas são preservadas e identificadas como falhas, sem interpretação de população zero.

Uma cópia adicional das evidências privadas de pesquisa foi autenticada no checkout principal em `.scratch/cvm-b3-history-20261012/root/research-archive-01/`: **184 arquivos, 45.176.617 bytes**, provenientes das frentes `a`, `b`, `bdr`, `bdi` e da evidência de desenvolvimento `corporate-impl`. Cada arquivo foi comparado ao original por SHA-256. O `archive-manifest.json` conserva caminho de origem, caminho da cópia, tamanho e hash; pin externo **`d1db9f8b2ecbbbe9d7760ae8e3a65104d573062ec472a0b98f7d8ead24fad40f`**. Esta cópia é local, no mesmo computador; não comprova armazenamento externo ou backup em outro dispositivo.

O material original FRE permanece separadamente em `data/raw/cvm-b3-history-20261012/`: 15 ZIPs oficiais, **122.304.751 bytes**, com recibos e metadados autenticados. O índice `corporate-source-index.json`, contrato `cvm-corporate-sources-v1`, tem pin **`f54ac4e0f84586f94cb1acdb3d3b932830f6f3f30835269270738aeb563e9e6c`**. O cadastro corrente de estrangeiras está em `foreign-cad/`, com corpo de 15.422 bytes, SHA-256 **`9fe853e64092c7fe443e2fad60a926ea73e33fb8482e35e9db2fe661242c5335`**. Os arquivos podem conter campos não projetados; a documentação pública e os produtos derivados conservam apenas os metadados autorizados.

Os destinos `.scratch/` e `data/` são locais e não são publicação Git. As notas públicas guardam metodologia, referências, localizadores e limitações. A recuperação em UTC pode cair em 13/10/2026, enquanto a data local desta sessão é 12/10/2026; recuperação, publicação do documento e data do fato estudado não se confundem.

Dois checkpoints adicionais preservam a evolução sem substituir o primeiro: `research-archive-02/`, com 11 arquivos e pin `8424714576f63a2768cfaa3673037015c16694bb9e245e0ef6b82ec4a2ae5b25`, e `research-archive-03/`, com **35 arquivos/290.805 bytes** e pin `f6ecc679c91f85851a27d436f9715297437db604ea0101ee605363c353096590`. Seus manifests encadeiam o hash anterior. O terceiro conserva relatórios de admissão/revisão, pesquisa de datas, handoffs, RED/GREEN e recibos dos pilotos inconclusivos. Cada cópia foi comparada ao original por bytes/hash durante a execução; código e documentos ainda em edição ficaram fora desse checkpoint. Os originais permanecem em seus destinos e o histórico dos commits conserva as versões de código/documentação.

## Referências e trilha de interpretação

- [Fontes históricas CVM/B3](cvm-b3-historical-sources-20261012.md): catálogo, arquivos anuais, layouts, normas, falhas de acesso e limites de cobertura.
- [Tipos institucionais IF.data](ifdata-institution-types-history-20261012.md): campos nativos, mudanças observadas, códigos sem definição histórica comprovada e diferença entre atributos da instituição, líder e conglomerado.
- [Emissores BDR e unidades BCB](bdr-issuer-bcb-links-20261012.md): referências documentais, papéis societários, datas, candidatos e pontas ainda não comprovadas; revisão independente PASS no pin `ff75bd39bd4b1d7458244d6418ebbdb0b23c0b4cb7088c323e4666b71c229445`, após corrigir três localizadores Stone. O PASS não admite automaticamente os vínculos.
- [Disponibilidade histórica do BDI](b3-bdi-historical-availability-20261012.md): diferença entre captura local autenticada e leitura web, sondagens derivadas e ausência de comprovação dos 60 pontos; revisão independente PASS para a pesquisa de disponibilidade, sem certificar cobertura histórica integral.

Cada referência deve ser usada com o localizador e a data do fato indicados na nota pertinente. Um hash atesta integridade dos bytes preservados; não atesta, por si, a interpretação econômica ou a vigência de uma relação. Inferências e decisões de João são identificadas separadamente de declarações das fontes.

## Estado verificável neste checkpoint

Pesquisa inicial de fontes e tipos, desenho e transporte FRE passaram por revisão independente. A implementação inicial da admissão societária no commit `72254775bcf66586195ba08898f4b59deff86f6f` teve 28 testes confirmados pelo revisor, mas duas contraprovas materiais impediram a liberação do build real: identificador de 11 dígitos indevidamente admitido no campo CNPJ da sociedade e localizadores/hash de segmento estruturalmente inválidos aceitos pelo verificador após repin. As correções no commit `c089f7f712ce3970aef1b418661f47b0e5517e57` passaram por nova revisão independente e 31 testes (14 societários e 17 regressões CVM); isso habilitou somente o build real da fatia societária.

O primeiro processamento real e seu replay foram executados offline em destinos novos no checkout principal, `data/curated/cvm-corporate-history-20261012/` e `data/curated/cvm-corporate-history-20261012-replay/`. Ambos tiveram inventário e bytes idênticos, inclusive manifest com pin **`420a0490c85421175a074f3287270ca308749d2437148134aed1a1244fac5d8d`**. Tempos medidos: 24,437 e 24,719 segundos. O resultado privado `.scratch/cvm-b3-history-20261012/root/corporate-real-build-result.json` tem SHA-256 `caa45e7b1ea30b628bd375817151f8916c3271b262ce80bbdbf192cd753be340`.

| Tabela do primeiro processamento | Linhas projetadas |
|---|---:|
| Participação em sociedades | 63.165 |
| Posição acionária PJ | 74.989 |
| Histórico do emissor | 8.608 |
| Reestruturações | 11.137 |

**Primeiro pacote real não aceito.** Foram registrados 31.172 segmentos em quarentena: 14 por CSV inválido, 29.207 por chave PJ, 1.929 por chave de PJ relacionada e 22 por identificador da sociedade. Havia 5.607 lacunas de identificador explicitadas e nove ausências estruturais de membro. Essas contagens são diagnóstico do primeiro processamento, não população final aceita. A revisão precisava distinguir identificadores realmente malformados de vazios/estrangeiros documentalmente permitidos, para evitar descarte indevido de declarações válidas.

A revisão independente do pacote confirmou integridade/replay e comparou integralmente as 157.899 projeções aos segmentos originais, mas encontrou dois P2 de classificação de ausência: **todos os 29.207 casos de chave PJ e todos os 1.929 de chave relacionada tinham CNPJ literalmente vazio, nenhum presente malformado**. No segundo conjunto, a PJ principal possui identificador válido e também foi descartada. Essas declarações devem ser preservadas como observações com identidade incompleta; isso não autoriza aceitar relações sem pontas identificadas. A expansão foi interrompida para correção e revalidação. Os destinos iniciais permanecem imutáveis como diagnóstico, sem aceite. Relatório agregado privado: `.scratch/cvm-b3-history-20261012/root/corporate-package-review.json`, SHA-256 `65d72d575f7e3ccf1220e574f486cb0e7281bd293091aaf447b70ff5d5a19c28`.

## Correção e admissão societária v2

O commit `9091533d0965bf26e2cee99a01962eebe8625cc7` corrigiu a classificação de CNPJ vazio nas declarações PJ, mantendo quarentena para identificador presente incompatível. As lacunas agora têm campo/papel/motivo/status/localizador, sem nome ou identificador pessoal, e são reconstruídas pelo verificador. TDD: seis falhas observadas antes da correção; **34 testes PASS**, 17 societários e 17 regressões CVM, repetidos pela revisão independente do código. O aceite de software precedeu o novo processamento.

Destinos novos no checkout principal: `data/curated/cvm-corporate-history-20261012-v2/` e `data/curated/cvm-corporate-history-20261012-v2-replay/`. Ambos os manifests têm SHA-256 **`ebecfd9cccad88c19e9aba787ec89cc0f480d217a56a87b481ce7152196c65a0`**; os seis arquivos são byte a byte idênticos. Tempos registrados: 26,125 e 26,266 segundos; resultado privado em `.scratch/cvm-b3-history-20261012/root/corporate-real-build-v2-result.json`.

**Revisão independente do pacote v2: PASS.** Foram comparadas integralmente aos segmentos originais **189.035 observações**: 63.165 participações, 106.125 posições PJ, 8.608 históricos e 11.137 reestruturações. As 157.899 projeções anteriores permanecem iguais, e as 31.136 restauradas correspondem exatamente às ausências indevidamente descartadas. As 50.860 lacunas foram reconstruídas: 5.607 de sociedade, 29.207 de acionista principal e 16.046 de relacionado. Restam 36 quarentenas (14 CSV estritos e 22 identificadores presentes incompatíveis), além de nove ausências estruturais. Permanecem excluídas 110.031 posições PF e 146.254 sem tipo declarado. Relatório `.scratch/cvm-b3-history-20261012/root/corporate-package-v2-review.json`, SHA-256 `926d32534db37ab812d0d41b6de337999a786b205579950ea88a5ba9f952db3e`.

O PASS admite as observações e a proveniência, sem confirmar identidade, controle vigente, aplicabilidade trimestral ou elegibilidade acadêmica. A relação histórica ainda precisa ser implementada/revisada no seu contrato. A conferência adicional FCA mostrou que todas as 11.108 linhas de instrumentos têm referência documental `AAAA-01-01`, com eventos posteriores em parte dos casos; essa data não será convertida em snapshot ou vigência anual. Estados de datas e lacunas constam do detalhamento técnico no desenho; pesquisa autenticada privada em `.scratch/cvm-b3-history-20261012/root/instrument-date-research.json`, pin `21678a23ca5c9bc867116e22ab5ea58b4fbaddef4bad997251c6497aa374d8f2`.

Persistem limitações materiais de identificação histórica B3: os ZIPs COTAHIST não foram recuperados; uma observação em carteira de índice não comprova negócio executado; cadastro/programas correntes não reconstituem todos os instrumentos cancelados. Processar 60 referências do cadastro BCB não resolve essas lacunas. Desconhecido permanece explícito, inclusive para emissores BDR dispensados de registro CVM e para pontas societárias sem documentação autenticada.

## Consulta histórica: implementação local em revisão

O commit `4d574084c1811b93f89a6de5eef3c09f79139c83` implementou o módulo `historical_issuer_links.py`, seu teste adjacente e a CLI `build-historical-issuer-links.py`, sobre a base societária revisada. O autor executou **15 testes históricos**, 34 regressões CVM/FRE e sete de cadastro, todos PASS. RED, contraprovas, GREEN, comandos e limites estão no worktree em `.scratch/cvm-b3-history-20261012/historical-impl/handoff.md`. A revisão independente do código está em andamento; não houve build real ou aceite do pacote histórico neste checkpoint.

As oito tabelas previstas preservam observações, identificadores, suportes e perspectivas; a consulta distingue candidatura cadastral, conflito, declaração de controle datada e candidatura sem vigência demonstrada. Python local `3.12.14` escreve `QUOTE_NOTNULL`, mas seu leitor CSV perde a diferença entre null e vazio: uma contraprova foi guardada em `python-null-reader.txt`. O módulo usa exclusivamente a gramática canônica de sua própria saída, com teste independente pelo DuckDB para null/vazio, aspas, delimitadores e campos multilinha. A execução completa no corpus real ainda não foi medida; as medidas parciais da primeira tentativa estão registradas abaixo. Materialização e enumeração de caminhos societários exigem avaliação própria de capacidade.

A revisão independente encontrou um P2 material na detecção de ciclos: no grafo `A→B, B→C, C→A, A→C`, com a mesma data, a busca marcava somente três arestas como cíclicas e deixava `A→C` sustentar declaração de controle datada. A quarta aresta também pertence a um ciclo. A execução real foi suspensa, e a correção/teste/revisão precisam terminar antes de ampliá-la. Os testes iniciais aprovados não substituem essa contraprova.

O autor corrigiu esse P2 no commit `187cc770cc135f8fbbcd213f60efdbf91665351b`, classificando as arestas internas às componentes fortemente conexas, inclusive self-loops. A contraprova falhou antes da correção e passou depois; a suíte histórica afetada teve **16 testes PASS/70,099s**. Handoff próprio `historical-impl/handoff-cycle-fix.md`, preservado na cópia03. A re-review independente está em andamento; o build real continua suspenso até seu resultado.

A re-review posterior aprovou o commit exato `187cc770cc135f8fbbcd213f60efdbf91665351b`: repetiu os 16 testes/68,589s, conferiu a contraprova, self-loop, grafo acíclico e um oráculo independente nos 512 grafos dirigidos possíveis com três nós. Esse PASS removeu o bloqueio de software, sem antecipar capacidade ou aceite dos dados reais.

**Primeira execução histórica real interrompida por recurso, sem pacote aceito.** O [gate real](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6137062997) começou às `2026-10-13T02:45:24Z`; às `02:48:30Z`, antes de criar o destino de saída, o processo tinha 6.934.847.488 bytes de memória privada e pico de working set de 4.865.490.944 bytes. A máquina tinha 7.712.836 KiB de RAM total visível e apenas 24.956 KiB livres. Root registrou o diagnóstico e interrompeu somente o processo verificado dessa execução. Os três manifests de entrada foram reautenticados e permanecem iguais. Não houve manifest de saída, verificação ou replay; nenhum destino aceito foi alterado. O diagnóstico não comprova a causa interna, que exige investigação antes do ajuste.

Script privado `root/build-historical-real.py`, amostras `root/historical-real-memory-samples.jsonl` e diagnóstico `root/historical-real-resource-interruption.json` permanecem no checkout principal sob `.scratch/cvm-b3-history-20261012/`. A interrupção forçada não executou o bloco final do script; portanto não há recibo normal de conclusão. Materialização, caminhos societários e repetição de suportes são hipóteses a distinguir, sem truncamento silencioso ou redução das observações autorizadas. O novo gate é de capacidade desta máquina; não invalida os inputs nem é autorização para recoleta.

## Canais oficiais B3: alcance de cada tentativa

A pesquisa pelo navegador encontrou o seletor anual oficial de Séries Históricas e o catálogo atual MUB3, cuja rota não é o antigo domínio com falha DNS. O [piloto COTAHIST2010](b3-browser-download-pilot-20261012.md) teve resultado **indeterminado por interrupção da ferramenta**, sem arquivo confirmado ou admitido. Uma seleção foi submetida; o timeout externo reiniciou a sessão antes de confirmar a etapa alcançada. Não houve repetição. Isso não demonstra ausência do arquivo, falha HTTP ou indisponibilidade geral do navegador.

A nota do piloto passou por revisão documental independente: pin `312cdef4920de53e5604be212dacd73f869141e467869b92a44a9321a57f265f`. Recibo preservado no checkout principal em `data/raw/cvm-b3-history-20261012/cotahist-browser-pilot/receipt.json`, SHA-256 `ad3643e5a203429af41817ae78041b30fec4efc45bc1d491f2508a27ff59bf09`; inventário privado em `.scratch/cvm-b3-history-20261012/root/b3-browser-pilot/inventory.json`, pin `d5ec6cd25da87e16c92997b82ad6d10b2ad22750b3543e86f196ab0910607127`. HTTP, caminho, tamanho, hash do ZIP e conclusão são desconhecidos. Limites de admissão posteriores ao download não são limites aplicados ao transporte.

Uma nova aba permitiu ler o [registro MUB3 do BDI30/12/2010](https://mub3.org.br/centro-referencia/acervo/451f3d63a44b4c7a90bfa2eb76044263): título, data, coleção BM&FBovespa e botão público `Baixar documento`, sem href exposto. A inspeção somente leitura está preservada em `.scratch/cvm-b3-history-20261012/root/mub3-record-inspection.md`, SHA-256 `7f666e3f5146ab35e9032fb6a6924912734d811ebf1a7a90054eb1b1d2119748`. O [contrato de piloto próprio](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6136944840) delimitou uma ação normal desse documento, com recibo e limites explícitos.

O [piloto MUB3](mub3-bdi-download-pilot-20261012.md) também terminou **indeterminado, sem corpo admitido**: o único clique foi confirmado sem erro às `2026-10-13T02:35:27.271Z`, mas o evento de download não foi observado em 25 segundos. O timeout externo era de 60 segundos, sem reset; a aba continuou controlável, sem nova URL de documento exposta no DOM. Não houve repetição. Recibo no checkout principal `data/raw/cvm-b3-history-20261012/mub3-bdi-20101230-pilot/receipt.json`, pin `f09334d95bc4ca475bbed6680c7a5ff5f9edfce7f97585f1ebfd90530685556d`; nota pública pin `686015d15afdd15bdad99196021c9d9077d4e4987cd2a188b78e7a80d4515d6d`. A nota, o recibo e seu inventário passaram por revisão documental independente, sem confirmar transporte. Não se infere ausência, erro HTTP ou inexistência de arquivo fora desse destino. Mesmo uma captura bem-sucedida de um dia não certificaria história contínua, presença trimestral ou universo completo.

## Retomada V2 no receptor — 2026-10-13

A recepção da Release `snapshot-cvm-b3-20261013` reautenticou 2.668 arquivos/4.280.712.987 bytes, três pins externos, 18.228.826 registros IF.data e 512.959 cadastrais; 57 testes focados passaram e revisão independente confirmou todos os hashes após execução. Nenhum dado aceito foi sobrescrito.

João autorizou continuar até concluir108 e criou-se Goal ativo. A proposta de normalização foi adotada tecnicamente no código `c224dedbad0ed35b9b7450b11da5c03c24340c82`, branch `codex/cvm-b3-history-resume`: contrato V2/nove CSV, caminhos únicos por hash da rota canônica e referências ordenadas, consulta com todos os caminhos referenciados, verificação por rederivação e escritor incremental com teto igual ao leitor. As passagens anteriores sobre proposta não implementada descrevem o handoff V1, não este checkpoint.

TDD RED/GREEN preservado; 20 testes históricos passaram em132,249s. Revisão independente do SHA c224ded: PASS, sem P1/P2; contraprovas independentes do escritor (0,021s) e equivalência/consulta (10,023s) passaram. Oráculo V1 vem do blob imutável da base91bd20ccb205e72d47d42536eefbb529da551f16, SHA-256392025e0db4e62b292b8dd844d6ec020c2caf4d51c110b59e34b6a2a76dd2463. O job CIoffline recebe histórico Git completo somente para disponibilizar esse blob, sem alteração de permissões/proteções/checks.

Recorte real finito autenticado: todos os inputs nativos lidos, com derivação limitada a oito ocorrências de dois terminais, mais grupos/líderes (16 linhas). As oito tabelas V1 coincidiram integralmente após expansão/ordenação dos IDsV2; 2.259 caminhos e92relações. Encerramento11,125s, pico privado2.568.302.592bytes, sem escrever pacote. Revisão independente do recorte: PASS. Seus60registros de cobertura são a grade de referências, não60trimestres completos de dados do recorte.

O build completo V2 foi iniciado após esses gates em destino novo `data/curated/historical-issuer-links-resume-v2/`; não há aceite antecipado. O monitor mede somente o processo próprio, conserva eventos de fase e recursos, e termina o worker em caso de pressão/timeout ou falha de medição. Guardas de1s são amostradas, não limite absoluto. Medir build, verify, query e replay separadamente; um PASS não presume os demais. Evidências operacionais privadas no worktree `.scratch/issue108-resume/` e ledger `.superpowers/sdd/2026-10-12-cvm-b3-history/`.

Curadoria BDR transportada foi reautenticada:17candidatos/13fontes/seis pistas, zero admissão automática. Onze timestamps foram preservados como ISO com offset e convertidos explicitamente paraUTC, sem inferência por locale; duas recuperações não disponíveis permanecem desconhecidas. Revisão independente dessa preparação: PASS. Extensão finita de fontes oficiais para12globais tem contrato específico na Issue108, preservando falhas e material corrente como auxiliar. Contrato suplementar e adoção ainda pendentes.

## Revalidação do núcleo e complemento contratado — 2026-10-14

O primeiro build V2 terminou, mas a conferência de domínio encontrou falsos conflitos entre códigos CVM numéricos com preenchimento diferente (`906`/`000906` e `1023`/`001023`). Seus destinos `historical-issuer-links-resume-v2/` e replay permanecem como diagnóstico, sem aceite. A correção no commit `661ef9eaaa970a7882608378ffea9f81081b89c7` compara somente sequências ASCII de dígitos por uma chave sem zeros iniciais, mantendo os literais originais. A documentação nativa CAD/FCA sustenta o domínio numérico. Códigos realmente distintos, como `1279`/`19348`, continuam em conflito; sinais, decimais, espaços e dígitos Unicode não recebem equivalência nova.

TDD causal e regressões: 22 testes históricos em 143,029 segundos. A revisão independente do código passou, com duas contraprovas repetidas em 8,390 segundos. O novo pacote e replay estão em `data/curated/historical-issuer-links-resume-v2-code-key/` e `data/curated/historical-issuer-links-resume-v2-code-key-replay/`, no checkout receptor. Pin externo de ambos os manifests: **`5d3f1fa01872c50b581218be28e602722af242190fd549388ea487a23b859ba0`**. Os 11 arquivos são byte a byte idênticos, e os três pins de entrada permanecem iguais.

| Medida independente | Tempo | Pico de memória privada |
|---|---:|---:|
| Build corrigido | 38,094 s | 2.653.143.040 bytes |
| Verificação completa | 87,219 s | 4.433.809.408 bytes |
| Build de replay | 37,000 s | 2.655.236.096 bytes |
| Verificação do replay | 86,453 s | 4.434.948.096 bytes |

O pacote contém 303.792 linhas cadastrais, 36.408 observações de emissores, 11.108 instrumentos, 189.035 observações societárias, 59.708 vínculos cadastrais, 43.393 relações, 51.188 caminhos, 60 referências de cobertura e 337.562 lacunas. Os estados das relações são 15.823 candidaturas cadastrais, 24.875 candidaturas de controle sem vigência, 2.686 conflitos de identificador e nove declarações de controle datadas. O maior CSV tem 375.333.629 bytes, abaixo do teto de 1 GiB. Essas contagens descrevem registros e estados, sem representar empresas únicas ou elegibilidade acadêmica.

A revisão independente de domínio rederivou os flags de conflito das 36.408 observações. Cadastro, instrumentos, societário, vínculos e caminhos mantiveram bytes idênticos ao diagnóstico anterior; a mudança nas relações e lacunas decorre da correção dos falsos conflitos. Foram conferidos suportes e vínculos de BB, Bradesco e Itaú em 201012/202412. **Aceite local do núcleo técnico: PASS**, preservando candidaturas, conflitos reais e limites temporais. Isso não confirma universo B3 completo, amostra acadêmica ou conclusão global da Issue 108.

Consulta real de BB (`00000000000191`, 201012, perspectiva financeira) passou em 86,203 segundos, pico privado 4.437.389.312 bytes. Retorna uma candidatura cadastral e uma de controle sem vigência, 12 caminhos e os códigos CVM literais `001023`/`1023`. O vínculo financeiro ao grupo `C0049906` tem suporte cadastral próprio; a existência desse grupo não converte a candidatura societária sem vigência em controle histórico certificado.

O lote complementar de pesquisa preservou 24 respostas (15 HTTP 200 e nove HTTP 403), 15.186.658 bytes e 17 extratos literais. Revisão independente reautenticou todos os corpos e localizadores após corrigir um extrato Barclays que havia normalizado espaços. Fontes correntes, respostas bloqueadas e páginas sem conteúdo substantivo conservam seus estados. O corpus é pesquisa revisada; suas relações não são automaticamente adotadas.

O [contrato complementar R3](../superpowers/specs/2026-10-12-cvm-b3-history-design.md#contrato-complementar-r3-adotado--2026-10-14) foi adotado na [Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6160293510). O suplemento separado preservará fontes, entidades, afirmações e lacunas com pins externos e identificadores por conteúdo. A admissão verifica integridade, localizadores e fechamento dos suportes; interpretação, projeção documental e alcance temporal exigem curadoria e revisão próprias. Implementação R3a e preparação do índice estão em execução, sem pacote complementar aceito neste checkpoint.

## Índice complementar revisado e universo observado

R3a foi concluída em `5225837867ffc2472bab8652ba7555bf934af853`, com revisão independente: 25 testes focados/9,485s e oito contraprovas adicionais, incluindo orçamento total, DAG de 80 níveis, conflito transitivo e erros da CLI. O índice curado congelado tem pin externo **`dab03c105115c47dcf2fe3567abda1e2765fb0878c1947a3f4044e921273c411`**, 832.942 bytes. São 20 companhias, 110 entidades, 178 afirmações, 77 fontes e 45 lacunas. Índice e evidências somam 81.603.377 bytes, sob o teto total de 256 MiB. O índice e suas cópias por conteúdo ficam no destino novo `data/raw/historical-issuer-supplement-resume-v1/`; originais permanecem imutáveis.

**Revisão semântica independente do índice: PASS.** Os dois achados materiais foram corrigidos: tipos/campos BCB nativos preservados e nove pares de operadores documentais/BCB separados quando a identidade era somente nominal. A revisão reextraiu 22 projeções PDF dos corpos originais, conferiu 13 blocos HTML, 281 localizadores, os 20 claims105 integrais e as dez clausuras de suporte. Relatório privado `curation-review.md`, SHA-256 `939a7de310ccefcd49e2c88f1ef596ece78886592b78cf6a74e41449e004a1d2`.

As dez associações declaradas no índice são oito pontos do dossiê105 em 201012/202412 e duas composições Nu202412. As últimas combinam declaração SEC de participação indireta de 100% do capital total, sem inferir votos, identificação por CNPJ em contrato corrente e cadastro BCB da referência; mantêm natureza de inferência analítica, confiança de identidade alta e temporal média. Não demonstram estabelecimento14 retrospectivo, controle contínuo, equivalência da holding internacional com perímetro BCB ou elegibilidade acadêmica. Os demais candidatos continuam como observações e lacunas.

A conferência independente contra o núcleo autenticado comparou 96 ocorrências cadastrais — 62 novas e 34 do105 — em 28 chaves e 29 afirmações de membership. Os 16 campos, tipos, grupos, líderes e suportes concordam, sem diferenças. A leitura incremental também reproduziu o CSV canônico e seus hashes, preservando null/vazio. Nu Pagamentos (`18236120`, Tcb `N4`) tem financeiro null e prudencial `C0084693`; Nu Financeira (`30680829`, Tcb `N1`) tem financeiro `C0052058` e prudencial `C0084693`. O líder nativo `18236120` permanece com seu alcance não desambiguado; compartilhar prudencial não preenche o financeiro ausente nem autoriza soma duplicada.

| Superfície observada | Registros | CNPJ14 distintos | Bases8 distintas |
|---|---:|---:|---:|
| Emissores CVM | 36.408 | 2.567 | 2.564 |
| Instrumentos documentais | 11.108 | 1.107 | 1.105 |
| União das duas superfícies | — | 2.567 | 2.564 |

O cadastro BCB contém 303.792 linhas: 295.048 Td=I e 8.744 Td=C. Há 6.008 códigos individuais distintos nas 60 referências: 5.263 com oito dígitos ASCII e 745 outros códigos preservados, sem conversão automática em CNPJ. São 4.509 ocorrências Td=I em 201003 e 5.528 em 202412. CNPJ, código cadastral, companyID e observação não são a mesma unidade de contagem. Esses universos descrevem o corpus observado, sem certificar mercado completo, continuidade de identidade ou população acadêmica. Relatório independente `membership-preflight.md`, SHA-256 `b8f59871432efa98666be77378265d6ee66ee59323035561238fc6915089fcae`.

R3b foi implementada no commit `d1c3bf781bc7de5da8977dc4a04342aef63c932a`: build/verify/query do suplemento, consulta combinada opcional e CLI, nos mesmos três paths. A execução final do componente teve **72 testes/444,481s, com um skip Windows de symlink por privilégio**. A contagem booleana em manifest foi recusada após contraprova causal e reexecução completa. A revisão independente do código está em andamento; não houve build real ou aceite do pacote neste checkpoint.

O [complemento de recurso CI](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6160844085) eleva somente o timeout do job offline de 15 para 25 minutos, mantendo Windows em 15 e todos os testes/pins/permissões. O CI da base passou 853 testes em 726,522s; a ampliação do componente fundamenta a margem finita, sem antecipar runtime ou sucesso do CI do novo SHA. Revisão final, pacote real, replay, consultas e integração continuam gates próprios.

## Pacote complementar real e consultas R4

A revisão independente do código R3b aprovou o SHA `d1c3bf781bc7de5da8977dc4a04342aef63c932a`, com dez contraprovas próprias em76,125s e uma conferência focal de clausura em10,899s. A [execução real contratada](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6160978661) usou esse código no HEAD documental `c3dd9fb3c51be410bb16468dcdf777e4e83ff9b8`, sem delta nos três arquivos de implementação. O pacote local `data/curated/historical-issuer-supplement-resume-v1/` e seu replay novo têm manifest externo **`b1c5d3ae69b1ee354797fca6a8be46c08969266ceeefde2a72d277473219aca4`**. Índice curado e núcleo conservam seus pins próprios, exigidos novamente por verify/query.

| Ação real | Tempo | Pico de memória privada |
|---|---:|---:|
| Build original |92,172s|4.546.490.368 bytes|
| Verify original independente |94,438s|4.430.323.712 bytes|
| Build replay independente |88,016s|4.545.425.408 bytes|
| Verify replay independente |93,984s|4.440.170.496 bytes|

**Integridade e replay: PASS.** Os104 arquivos/81.674.275 bytes têm caminhos, tamanhos, hashes e bytes completos idênticos, incluindo manifest. O índice, seus97 arquivos de evidência e os dez arquivos do núcleo foram reautenticados depois; nenhum guard foi acionado. O monitor guarda amostras de1s do processo próprio, sem alegar limite absoluto entre amostras. Relatório privado `supplement-replay-report.md` e comparação integral `supplement-replay-comparison.json`.

**Domínio do pacote: PASS.** A conferência independente rederivou as25relações esperadas:10individuais,9financeiras,6prudenciais;8em201012 e17em202412. Os oito pontos105 produzem20relações; as duas composições Nu202412 produzemcinco. As quatro listas reconstruídas são byte a byte iguais ao índice externo;20claims105 e45lacunas curadas permanecem integrais. Os17candidatos não geram associações e mantêm17lacunas derivadas `support_not_adoptable`. Relatório `supplement-domain-review.md`, SHA-256 `a360c33e8909042df09ed5b32608cd27ba1a5d2df08363d6bbdc27be71450224`.

A consulta geral real passou e retorna110entidades,25relações,45lacunas curadas,17derivadas e26entidades de instrumentos. O quadro abaixo usa códigos nativos distintos **por companhia/referência/perspectiva**, e não conta duas vezes um grupo compartilhado por operadoras. Não somar individual, financeiro e prudencial.

| Companhia | Referência | Individuais identificadas | Financeiro | Prudencial |
|---|---|---|---|---|
|Banco do Brasil|201012|`00000000`|`C0049906`|sem vínculo nativo nesta referência|
|Banco do Brasil|202412|`00000000`|`C0049906`|`C0080329`|
|Bradesco|201012|`60746948`|`C0010045`|sem vínculo nativo nesta referência|
|Bradesco|202412|`60746948`|`C0010045`|`C0080075`|
|Itaú Unibanco Holding|201012|`60872504`, `60701190`|`C0010069`|sem vínculo nativo nesta referência|
|Itaú Unibanco Holding|202412|`60872504`, `60701190`|`C0010069`|`C0080099`|
|Nu Holdings|202412|`18236120`, `30680829`|`C0052058` somente pela Financeira|`C0084693` compartilhado|

Esse quadro é uma identificação pontual documentada. Código igual nos dois extremos não comprova perímetro constante ou continuidade nos trimestres intermediários. Holding e banco permanecem pessoas distintas; compartilhar unidade financeira nativa não torna o conglomerado BCB equivalente à consolidação societária internacional. Ausência de grupo não vira zero ou inelegibilidade.

Instrumentos, registros, eventos e programas conservam datas e naturezas próprias. Observação em carteira BDI, anúncio ou programa corrente não comprova negócio executado, listagem contínua ou presença no trimestre da associação IF.data. As26entidades de instrumentos e os17candidatos BDR não são um universo de mercado certificado. A qualidade fixa `identity_certified=false`, `academic_eligibility_adopted=false` e `market_coverage_incomplete=true`.

**Consultas R4 e revisão de domínio: PASS.** Foram executadas e revisadas seis consultas completas: geral, BB201012/financeiro, Itaú202412/combinada, Nu202412/financeiro, Nu202412/prudencial e Citigroup202412/financeiro. Tempos observados por processo sequenciador:95,000s;93,594s;93,625s;93,578s;94,250s;93,750s. O relatório independente `r4-query-domain-review.md` tem SHA-256 `c3a0b6ce1e16eb2ac9c10b0e48a0b1aa8bf047544fff1fa2cd43e7aaca2d68f9`; recibo de verificações `r4-query-domain-check.json`, SHA-256 `68549dfcd3476da63cc338d6b2f082eb3862e9a20c952fac5d6fbf49e082f1e0`.

BB201012 mostra instituição e grupo com TcbB1/Tc1 e líder00000000; a referência prudencial continua null. Na consulta combinada de Itaú, o núcleo conserva53observações de emissores,22instrumentos e79caminhos, inclusive o conflito real CVM1279/19348 e suas candidaturas aC0010069/C0051444. O suplemento mantém duas operadoras no grupoC0010069, sob seus pontos aceitos; não sobrescreve o conflito do núcleo nem decide elegibilidade. Nu retorna somente Financeira na perspectiva financeira e duas operadoras no mesmo prudencial; a ausência financeira de Pagamentos permanece null. Citigroup retorna zero associações adotadas, mas preserva seisclaims sem referência trimestral, um instrumento, três lacunas curadas e uma derivada: isso não comprova inexistência de unidade financeira.

Na API, `undated_claims` significa **sem referência trimestral atribuída**, podendo existir data literal. A consulta geral tem79registros nessa chave, incluindo programas/instrumentos datados; não descrevê-los todos como semdata. `support_claims` conserva a clausura documental mesmo quando a data da fonte difere da referência filtrada. `events` e `instrument_observations` permanecem separados das associações IF.data, sem retroprojeção de listagem/negociação.

### Consultar o resultado local

Os comandos abaixo pressupõem uma instalação com o códigoR3b, ambiente Python3.12 existente e os pacotes locais nos destinos indicados. Dados são ignorados pelo Git; o clone sozinho não contém os manifests/evidências. Os pins são externos ao pacote consultado; não substituí-los por um hash recém-calculado de um arquivo não confiado.

```powershell
$Python = '.venv/Scripts/python.exe'
$Core = 'data/curated/historical-issuer-links-resume-v2-code-key'
$Supplement = 'data/curated/historical-issuer-supplement-resume-v1'
$CorePin = '5d3f1fa01872c50b581218be28e602722af242190fd549388ea487a23b859ba0'
$SupplementPin = 'b1c5d3ae69b1ee354797fca6a8be46c08969266ceeefde2a72d277473219aca4'
$IndexPin = 'dab03c105115c47dcf2fe3567abda1e2765fb0878c1947a3f4044e921273c411'
& $Python scripts/build-historical-issuer-links.py supplement-query $Supplement $Core --manifest-sha256 $SupplementPin --index-sha256 $IndexPin --core-sha256 $CorePin --company CIK:1691493 --reference 202412 --perspective financeiro
& $Python scripts/build-historical-issuer-links.py query $Core --manifest-sha256 $CorePin --entity 60872504000123 --reference 202412 --perspective financeiro --supplement $Supplement --supplement-sha256 $SupplementPin --supplement-index-sha256 $IndexPin
```

Seletores do suplemento são IDs exatos ou identificadores qualificados (`CIK:`, `CNPJ14:`, etc.), sem busca por nome. Para Citigroup, cujo identificador não foi fechado neste recorte, usar `entity:505e2b0bdecea7dd5fdaecf641414b06ae9c99bb9d0f3e6368a89e717c563d56`. O trio opcional da consulta combinada é obrigatório em conjunto; sem ele, a consulta do núcleo conserva seu contratoV2.

O aceite local de software, fontes, pacote, replay e consultas está documentado acima. A composição do SHA entregue, checks completos, PR, integração e CI pós-merge têm estado autoritativo na [Issue108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108) e na PR vinculada, sem inferência por este checkpoint. As decisões acadêmicas permanecem na [Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

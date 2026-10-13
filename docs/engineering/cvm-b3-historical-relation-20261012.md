# Relação histórica CVM–B3–IF.data: execução e preservação acadêmica

[Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108). Registro em andamento, iniciado em 12/10/2026. Não constitui declaração de conclusão da relação histórica ou de cobertura integral da B3.

## Objetivo e escolhas registradas

Período da monografia: 2010–2024, com 60 referências trimestrais. Conglomerados financeiros são a unidade principal; instituições individuais são complementares. Ações, units e BDRs têm a mesma prioridade. Identificação do emissor, participação societária, presença documental de instrumento e participação nativa em conglomerado são relações distintas, com datas e fontes próprias. Fórmulas, critérios finais de amostra e comparabilidade dos indicadores continuam sujeitos à decisão acadêmica na [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3).

O [desenho](../superpowers/specs/2026-10-12-cvm-b3-history-design.md) e o [plano](../superpowers/plans/2026-10-12-cvm-b3-history.md) delimitam admissão, verificações, consulta e revisão por fatias. Dados financeiros permanecem provenientes do IF.data; documentos CVM/B3/SEC são usados nesta entrega para metadados de identidade, controle e instrumentos.

## Preservação e referência posterior

João reiterou expressamente a necessidade de guardar as evidências para possível referência acadêmica. Os originais permanecem nos destinos de captura; cópias de preservação não os substituem. Cada captura registra URL, recuperação UTC, status, metadados de resposta, completude e SHA-256. Tentativas malsucedidas são preservadas e identificadas como falhas, sem interpretação de população zero.

Uma cópia adicional das evidências privadas de pesquisa foi autenticada no checkout principal em `.scratch/cvm-b3-history-20261012/root/research-archive-01/`: **184 arquivos, 45.176.617 bytes**, provenientes das frentes `a`, `b`, `bdr`, `bdi` e da evidência de desenvolvimento `corporate-impl`. Cada arquivo foi comparado ao original por SHA-256. O `archive-manifest.json` conserva caminho de origem, caminho da cópia, tamanho e hash; pin externo **`d1db9f8b2ecbbbe9d7760ae8e3a65104d573062ec472a0b98f7d8ead24fad40f`**. Esta cópia é local, no mesmo computador; não comprova armazenamento externo ou backup em outro dispositivo.

O material original FRE permanece separadamente em `data/raw/cvm-b3-history-20261012/`: 15 ZIPs oficiais, **122.304.751 bytes**, com recibos e metadados autenticados. O índice `corporate-source-index.json`, contrato `cvm-corporate-sources-v1`, tem pin **`f54ac4e0f84586f94cb1acdb3d3b932830f6f3f30835269270738aeb563e9e6c`**. O cadastro corrente de estrangeiras está em `foreign-cad/`, com corpo de 15.422 bytes, SHA-256 **`9fe853e64092c7fe443e2fad60a926ea73e33fb8482e35e9db2fe661242c5335`**. Os arquivos podem conter campos não projetados; a documentação pública e os produtos derivados conservam apenas os metadados autorizados.

Os destinos `.scratch/` e `data/` são locais e não são publicação Git. As notas públicas guardam metodologia, referências, localizadores e limitações. A recuperação em UTC pode cair em 13/10/2026, enquanto a data local desta sessão é 12/10/2026; recuperação, publicação do documento e data do fato estudado não se confundem.

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

**Aceite do pacote real ainda pendente de revisão.** Foram registrados 31.172 segmentos em quarentena: 14 por CSV inválido, 29.207 por chave PJ, 1.929 por chave de PJ relacionada e 22 por identificador da sociedade. Há 5.607 lacunas de identificador explicitadas e nove ausências estruturais de membro. A revisão deve distinguir identificadores realmente malformados de vazios/estrangeiros documentalmente permitidos, para evitar descarte indevido de declarações válidas. Essas contagens são diagnóstico do primeiro processamento, não população final aceita. Nenhuma relação histórica final foi produzida neste checkpoint. As etapas seguintes precisam registrar eventuais correções em destinos novos, revisões do pacote e cobertura efetivamente alcançada antes de ampliar à relação histórica.

Persistem limitações materiais de identificação histórica B3: os ZIPs COTAHIST não foram recuperados; uma observação em carteira de índice não comprova negócio executado; cadastro/programas correntes não reconstituem todos os instrumentos cancelados. Processar 60 referências do cadastro BCB não resolve essas lacunas. Desconhecido permanece explícito, inclusive para emissores BDR dispensados de registro CVM e para pontas societárias sem documentação autenticada.

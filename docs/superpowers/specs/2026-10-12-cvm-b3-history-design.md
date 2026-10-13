# Relação histórica CVM–B3–IF.data, 2010–2024

[Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108). João autorizou execução de ponta a ponta e escolheu conglomerados financeiros como unidade principal, instituições individuais como complemento e ações, units e BDRs com a mesma prioridade. Este desenho registra escolhas técnicas no objetivo autorizado; não decide fórmulas, amostra definitiva ou comparabilidade acadêmica na Issue 3.

## Resultado e limites verificáveis

Construir uma relação consultável e auditável nas 60 referências trimestrais de 201003 a 202412, conservando identidade do emissor, instrumento, unidade individual, conglomerado financeiro e perspectiva prudencial separadamente. Cada vínculo conserva a natureza, as datas efetivamente declaradas e suas fontes. Uma consulta pode retornar relação comprovada, declaração datada, candidatura ou desconhecido; desconhecido nunca vira instituição fechada ou exclusão silenciosa.

Cobertura de processamento das 60 referências difere de cobertura documental de todos os vínculos de mercado. Os arquivos anuais COTAHIST não foram recuperados: as tentativas oficiais retornaram 403. Não prometer negociação diária observada ou universo histórico B3 certificado sem esses dados ou prova alternativa. FCA é declaração do emissor, e catálogo/programas BDR atuais não reconstrói sozinho programas cancelados. As limitações integram o resultado e permanecem impedimentos à certificação integral quando materiais.

## Fontes e alternativas

Reutilizar os pacotes autenticados CVM 102 e cadastro BCB 86. FRE 2010–2024 acrescenta participações, controladores pessoas jurídicas e datas societárias; bruto e metadados de transporte já foram capturados e revisados independentemente. Cadastro corrente de estrangeiras e programas BDR são auxiliares, com vintage corrente explícito. Relações complementares de BDR exigem curadoria documental revisada e hashes externos; programa, depositário e emissor do lastro nunca são identificados entre si por coincidência.

Somente CAD/FCA não resolve holdings/BDRs; somente catálogo corrente causa viés de sobrevivência; correspondência por nome/ticker não prova identidade. Escolhe-se preservação de observações e relações documentais tipadas. Não construir harmonização financeira, preenchimento temporal ou classificação econômica por nome.

## Componentes e responsabilidades

- `bank_quality/cvm_corporate_metadata.py`: admissão offline finita de FRE. Consome índice de fontes com pin externo; verifica recibos, corpos, URLs, completude, UTC, ZIP e esquemas. Projeta metadados societários e registra ausências/quarentenas.
- `bank_quality/historical_issuer_links.py`: constrói e autentica a relação a partir de pacotes pinados. Preserva classificações nativas, identidades candidatas por identificador, relações societárias datadas, instrumentos e lacunas. Não calcula indicadores.
- `scripts/build-historical-issuer-links.py`: CLI fina para build/verify/query; argumentos explícitos e destinos novos. Sem rede no build/query.
- Testes adjacentes por componente; pesquisa e execução em `docs/engineering/`. Root integra entradas da arquitetura/README. Sem dependência, raiz ou camada nova.

## Admissão societária

Índice fechado `cvm-corporate-sources-v1`: recursos FRE distintos, anos 2010–2024, URL oficial exata, caminho relativo de manifest e SHA-256 externo de cada manifest. Recibos bounded exigem GET/HTTP200, corpo completo, sem truncamento, URL final exata e metadados de resposta autenticados. Limites medidos: 16 MiB por corpo, 64 MiB por membro, 256 MiB por ZIP; 15 ZIPs totalizam 122.304.751 bytes no transporte aceito.

Somente membros exatos de participação em sociedade, posição acionária, histórico do emissor e reestruturação quando presentes. Dados contábeis/mercado e posição de pessoas físicas não são projetados. Campos e strings originais permanecem; participação percentual sem semântica não se torna controle. `Acionista_Controlador=S` e `Tipo_Sociedade=Controlada` são declarações distintas, vinculadas à sua data. Ausência de tipo ou identificador impede inferência.

CSV Latin1, delimitador `;`, aspas duplas; registros admitidos precisam passar reparse estrito e largura/esquema. O diagnóstico encontrou segmentos inválidos, inclusive um intervalo de várias linhas físicas. Um leitor de enquadramento pode localizar segmentos, mas não admite leitura permissiva: cada segmento inválido inteiro fica em quarentena com hash, membro e intervalo de linhas, sem reparo. Contagem desses segmentos não certifica o número de registros originalmente pretendidos. Os demais segmentos estritos preservam ordinal diagnóstico e localizador físico; essa distinção aparece no manifest/qualidade.

Datas sintaticamente inválidas e chaves impossíveis ficam explícitas em qualidade/quarentena. Datas futuras não são corrigidas; não servem de fatos vigentes em 2010–2024. Ausências estruturais são independentes de linhas vazias. Destino precisa ser novo. Manifest fecha inventário, hashes, contagens, perfis, fontes e lacunas; verificador recebe pin externo.

## Identificadores, tempo e relação trimestral

CodInst individual e códigos de conglomerado conservam namespaces distintos. CNPJ completo CVM e CNPJ básico BCB só se relacionam após validação da estrutura e da semântica oficial; preservar os dois literais. Nome e ticker podem gerar diligência, nunca confirmar identidade. Colisões de identificadores e múltiplos registros CVM são conflitos, não seleção silenciosa do registro atual.

Cada participação em conglomerado vem do campo nativo e da referência consultada. Código do grupo, líder e atributos do próprio agregado são separados: tipo da líder não preenche tipo do conglomerado. A recuperação em 2026 não prova que cada atributo foi publicado contemporaneamente em 2010; guardar vintage e limites da pesquisa B.

Referência documental, composição do capital, última alteração, datas de listagem/negociação e recuperação UTC permanecem distintas. Não converter ano do ZIP em vigência anual. Não preencher controle entre observações ou extrapolar fim de listagem vazio. Para fatos em data distinta do trimestre, conservar declaração e indicar que vigência no trimestre não foi demonstrada. Caminhos societários precisam de pontas identificadas e interseção temporal demonstrada; ciclos ou lacunas não geram vínculo confirmado.

Múltiplas classes de ações/units/BDRs não multiplicam emissor ou consolidado. Relação muitos-emissores/um-conglomerado é permitida, com entidades separadas e cardinalidade conferida. Resultado patrimonial ou financeiro não é somado nessa relação.

## Classificação e consulta

Conservar `Tcb`, `Td`, `Tc`, `SegmentoTb`, `Atividade`, `Sr`, `Situacao` e campos nativos de vínculo por ocorrência. Tcb do agregado, atributos do líder e atividade da instituição são colunas distintas. Dicionário corrente tem vintage/alcance próprios: B3/N3 e F/LE/LO sem definição histórica demonstrada permanecem códigos literais, não classificação inventada. Primeira/última observação não são início/fim de vigência.

Produto contém tabelas textuais/CSV, manifest e relatório de qualidade/cobertura; Parquet/consulta DuckDB reutilizam dependência existente quando implementados. Identificadores ficam textuais com zeros; null e vazio continuam distintos. Exportações derivadas têm schema/contagem e hashes. Consulta filtra entidade/referência/perspectiva e retorna fonte e estado de evidência. Sem indicador ou ranking.

## Aceite e fatias

1. Pesquisa A/B revisada, fontes e campos delimitados; BDR com igual prioridade, sem excluir estrangeiras por CAD ausente.
2. Admissão FRE: testes de fontes alteradas/truncadas, ZIP/perfis, quarentena física inteira, exclusão de pessoas físicas/valores, ausências estruturais e replay. Revisão independente antes de construir relação.
3. Relação: 60 referências, fidelidade de campos, vínculo por identificador sem match por nome, datas distintas, deduplicação de classes, colisões, líder/perímetros e desconhecidos. Testes e revisão próprios.
4. Curadoria complementar BDR com fontes/localizadores/pins/revisão antes de admitir; inventário de casos não resolvidos.
5. Execução real em destinos novos, reautenticação/replay, revisão de domínio e composição final, publicação/integração/CI pós-merge. Documentar cobertura alcançada e impedir alegação de mercado integral quando faltar evidência.

Fontes originais, recibos, diagnósticos e tentativas ficam locais e imutáveis. Documentação pública contém referências, métodos, decisões e limitações sem cookies, contatos pessoais ou payload privado. O registro completo serve a auditoria e referência acadêmica posterior.

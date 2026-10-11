# Cadastro temporal IF.data e cobertura dos vínculos

[Issue86](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/86), execução offline em2026-10-11, base `af1336c542208cbe7eb984caeb960fa3d1743bd8`, branch `codex/ifdata-cadastro`. João autorizou importar o cadastro já capturado e conferir a conexão com valores por código e trimestre. Os seis paths de módulo/CLI/teste/README/arquitetura/esta nota constam na Issue; destinos canônicos existentes, sem servidor, dependência ou camada nova. Skills brainstorming (desenho delimitado aprovado), TDD, requesting-code-review e verification-before-completion; download por cua, sem nova coleta de valores/cadastro do BCB.

## Fonte recebida e preservação

Pacote `ifdata_cadastro_200003_202606.zip`, recebido por pasta privada indicada por João, SHA-256 `a7b2ce24a54c950835c17b178f7a32b3d9a5cb6f41beaf04a422162c69bec6c9`,218arquivos/387.366.719bytes descompactados. Origem local: `data/raw/ifdata-cadastro-20261011/ifdata_cadastro/`. A URL privada e os arquivos não são publicados. A documentação oficial do recurso está na [aplicação Olinda IFData](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/aplicacao#!/recursos/IfDataCadastro); o esquema efetivamente conferido é o `metadata.xml` recebido no pacote, não uma inferência a partir do shell web.

`indice_periodos.csv` informa contagens, URL e SHA-256 de106corposJSON; cada hash foi recalculado e cada corpo validado quanto a esquema, contexto, referência, quantidade e continuação. `resumo.json` informa coleta `2026-10-11T18:36:14.9876277Z`. O PASS de `verificacao.json` é declaração recebida; aceite local decorre das conferências e revisões independentes descritas abaixo.107consultas declaradas incluem202609vazio sem corpo armazenado/hash; essa referência permanece declarada sem dados, sem parte Parquet nem aceite de corpo inexistente.

Os JSONs são autoritativos para valores e nulos. O CSV recebido conflui null e vazio e não é usado para inferir essa distinção.16campos nativos preservados como VARCHAR: CodInst,Data,NomeInstituicao,DataInicioAtividade,Tcb,Td,Tc,SegmentoTb,Atividade,Uf,Municipio,Sr,CodConglomeradoFinanceiro,CodConglomeradoPrudencial,CnpjInstituicaoLider,Situacao. Os dois inteiros nativos são validados como tokens inteiros e preservados textualmente. Cinco campos de origem identificam arquivo/hash/URL/coleta/linha.

## Resultado e revisões parciais

Saída `data/curated/ifdata-cadastro-20261011/`:106Parquet e manifest. **512.959 registros por instituição/data,6.517códigos distintos,106referências200003–202606**. Nenhuma chave `(Data,CodInst)` ausente ou duplicada.6517códigos não são prova de6517identidades jurídicas longitudinais. Piloto202412:5.744linhas.

TDD: cinco testes inicialmente RED por módulo ausente→GREEN; revisão independente APP antes da expansão. Revisor comparou integralmente os106JSONs com os106Parquet: todos os16campos nativos e cinco de origem, hashes/contagens/referências e unicidade iguais, em3,699s. Segunda fatia: regressão RED por auditoria ausente→GREEN; revisão do join/CLI e piloto financeiro202412(105.228linhas preservadas, todas com cadastro) APP antes da auditoria integral. Regressão de UTF-8 da CLI reproduziu erro de codificação padrão Windows→saídaUTF-8 explícita→GREEN. Composição focal de19testes cadastro/leitor/catálogo PASS em3,526s. Revisão final/SHA/CI/integração têm evidência na Issue/PR, sem antecipação por esta nota.

## Ligação temporal com os valores

`cadastro` é a view nativa. `vinculos` conserva relações financeiras e prudenciais separadas por data, inclusive self-links declarados. Ao consultar valores, `ifdata_cadastrado` usa `LEFT JOIN` simultâneo por `CodInst` e `AnoMes=Data`; unicidade cadastral é conferida antes do join. Os campos originais dos valores permanecem próprios e `cadastro_encontrado` sinaliza a correspondência. Não transportar vínculo de outra data, inferir por nome ou juntar ambas as perspectivas sem filtro.

| Conjunto | Linhas preservadas | Com cadastro | Sem cadastro | Código nulo na fonte |
|---|---:|---:|---:|---:|
| Financeiro |7.945.863|7.941.653|4.210|972|
| Individual |8.679.083|8.679.083|0|0|
| Capital |1.344.190|1.343.971|219|0|
| Segmentação |259.690|259.655|35|0|
| Total |18.228.826|18.224.362|4.464|972|

Os972códigos nulos estão incluídos nas4.464ausências;3492linhas têm código preenchido sem cadastro na mesma referência. São65grupos dataset/período/código, não65instituições distintas. Revisão independente reconstruiu por EXISTS/anti-join todas as linhas dos relatórios, sem usar `audit_links`: diferenças zero, hashes dos valores conferidos, contagem preservada e sem fanout; comparação em0,885s.

Há105.499relações declaradas:43.125financeiras e62.374prudenciais. Um destino não foi localizado no mesmo trimestre: instituição `62816426`,202503, conglomerado prudencial `C0088390`. O vínculo é preservado; isso não prova inexistência jurídica do destino. Auditoria local em `link-audit.json`, `coverage.csv`, `unmatched.csv` e `declared_links.csv` no diretório de saída; não duplicam dados de valores nem são publicados. O comando audit reproduz o relatório em JSON na saída padrão.

## Limites de uso acadêmico

- `CnpjInstituicaoLider`:86.444registros com oito caracteres e426.515null; preservar zeros e comprimento. Não completar para14, validar como CNPJ completo ou usá-lo sozinho como identidade jurídica certificada.
- `DataInicioAtividade='180001'`:72.843ocorrências preservadas, sem interpretar o token como início real da instituição. Unidade/semântica desse marcador exige fonte própria.
- Cadastro recebido, vínculo declarado, identidade econômica, emissor/holding e elegibilidade da amostra são afirmações diferentes. Situação/tipo/código não selecionam silenciosamente a população da monografia.
- Correspondência cadastral não prova comparabilidade de variáveis/indicadores. Janela2010–2024principal e2025–2026complementar permanecem; unidade/amostra/método em#3, proposta de indicadores em#14, pesquisa de comparabilidade#16 reaproveitada.

Comandos de importação/consulta/auditoria estão no [README](../../README.md#cadastro-temporal-e-vínculos). Fontes, valores aceitos e trabalho da antiga rota transacional/PR83/stash permanecem preservados. A limpeza das Issues foi feita remotamente com histórico nos comentários; não alterou o workflow documental, a segurança, o Project3 ou as decisões acadêmicas.

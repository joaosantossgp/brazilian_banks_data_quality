# Proveniência — análises estatísticas da monografia

- Data:18/10/2026. Tarefa:[Issue162](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/162).
- Natureza: revisão narrativa dirigida, não revisão sistemática/exaustiva. Síntese Root; dois pesquisadores com ownership privado; verificador de fontes e revisor crítico em sequência.
- Mecanismo: Matt research, to-spec/to-tickets expressamente solicitadas; Superpowers desenho/plano/revisão/verificação; Feynman pdf-explore para leitura cruzada de artigos/PDFs. Deep-research/literature-review foram lidas, mas os wrappers /deepresearch e /lit não possuem runtime nativo validado nesta interface. Fluxo de literatura adaptado manualmente aos mecanismos disponíveis e destinos canônicos, conforme workflow do repositório. Não houve instalação/reativação do bundle ou execução simulada de slash commands.
- Plano:[plano canônico](../superpowers/plans/2026-10-18-statistical-analysis.md).
- Nota:[pesquisa](statistical-analysis-research-20261018.md).

## Entrada e diagnóstico

Ponteiro compartilhado lido em18/10/2026, package `data/curated/ifdata-composition-terra-20261017-run2`, manifestoSHA256 `ce57545b643d9efcfbb09ee26234c97f131080627d42622c2b4cfbf998f7c524`, accepted_local. O estado local não equivale a certificação acadêmica ou a integração de toda versão derivada. Tarefas posteriores não devem usar este documento para escolher a base vigente: precisam consultar o ponteiro e fixar seu próprio pin.

Inventário autenticado:

| Arquivo | SHA-256 |
|---|---|
| aggregates.parquet |99f6272b168ae283f1741eb327f05d3866e585f19a32a7ed1e32344bfb772336|
| joint_cells.parquet |46beb0f696b5328d74439bc60a7fb2911a5309a9a35e7c64ce40273e4a1447ae|
| unit_periods.parquet |50f2ba8d99cee90264671c74dc99b931a74b5e826f85c824a25793fb19ddd505|

Evidência privada no worktree da tarefa, `.scratch/statistical-analysis-20261018/`: `diagnose.py`, `diagnosis-run3/receipt.json`, quatroCSVs e `review-A.md`. O recibo registra hash do script, entradas, saídas, rows, versãoDuckDB1.5.6 e UTC. Comando: Python da.venv principal executando esse script no worktree. Apenas consultas e escrita em destino novo; sem reconstrução financeira, perda de precisão ou escrita no pacote aceito.

Tentativas preservadas: run1 falhou emCREATEVIEW parametrizado, operação não suportada pelo binder; foi substituída porrelation.create_view conferida no runtime local1.5.6. ConsultaContext7 retornou exemplosv2, portanto não foi tratada como prova da versão instalada. Run2 excedeu limite1GiB; os recursos medidos eram33.233.644KiB físicos/8.611.112KiB livres e35.704.212KiB virtuais livres. Run3 usou uma thread, preserve_insertion_order=false e limite4GB, sem truncar unidades/períodos; concluiu12.960/216/234.292/4.992 linhas. As tentativas falhas não foram reclassificadas comoPASS.

RevisãoA independente PASS: hashes/rows/IDs,28.140 reconciliações por categoria,3.240 identidades das coortes,340 contextos vazios. Limites preservados na nota: saída categórica não contémtotal diretamente; estados do cruzamentoTcb são mais limitados que no eixo isolado; ocorrência nativa não elimina exposição econômica intergrupo; presença de agregado não prova população completa.

## Manuscritos privados

Leitura noDrive: v1 modificada16/10/2026; v0 modificada03/09/2026; pré-projetoTécnicas modificado22/11/2024. São versões documentais distintas, não reconstrução do histórico de revisões do mesmo arquivo nem declaração de qual é o manuscrito final vigente. Respostas legíveis e metadados foram guardados em staging privado; os hashes identificam a capturaJSON do conector, não os bytes originaisDOCX:

| Captura privada | SHA-256 |
|---|---|
| drive-v1-readable.json |1ee6ad0715100ad11cf1f8981293459576678d3be6e8b4b61a8cdf22fb20c836|
| drive-v0-readable.json |487d486e0fc4ea717d07b11195521129d71b7eebf5c599ba6e14a806007d9b54|
| drive-techniques-readable.json |a993668ef86bdf09a90ef3a1788024e6dd5c464e36e548ab6b8620f47b464317|

O conector fornece texto legível best-effort, sem garantia de paginação/comentários/layout completos. A consulta recuperou objetivos e intenções metodológicas, não validou todas as referências existentes nos manuscritos. Nenhum original foi alterado; nenhuma cópia, link privado ou texto integral foi publicado.

## Busca, seleção e leitura primária

Notas intermediárias privadas:

- `research-statistical.md`, SHA256 `752daf1e097acfe0909f23e574373b75053bcabf495d47e60e1e736f53e6974f`.
- `research-financial.md`, SHA256 `cc99b5fe302016d96856efbab59657f69cacf517e281bab7064d0deca79a39c0`.

Elas registram consultas exatas, rotas de acesso, UTC e trechos/localizadores. A síntese aceita11 fontes distintas:F1–F5 eE1–E6, conforme atribuição na nota. Não são11 leituras integrais: fontes com leitura parcial têm capítulos/seções efetivamente lidos identificados. O artigoGranger/Newbold foi lido em cópia do texto primário em hospedagem não editorial, comDOI para identidade.

Buscas cobriram: IMF FSI2019 agregação/quartis;BCB REFdistribuiçãoROE; Res4553original e IF.data; seleção/composição bancária; HACamostrafinita/TTM; regressãoespúria; inferênciaclusterFE; dependênciatransversal; multiplicidade/data-snooping. A escolha é dirigida às perguntas, não uma amostra exaustiva de artigos e não uma regra de seleção por significância.

CapturasPDFs financeiros conferidas pelo pesquisador em18/10:

| Fonte | Recuperação UTC | SHA-256 do corpo |
|---|---|---|
| FMI final2019 |16:10:20.259489|a104ebd220a04a5757b18047ce94b7ca955759db3e99597a3e2b0d29cceae7dd|
| REFabril2024 |16:10:47.385031|26dc0a73e4ed65efb35e4b31b8eedf5d11c46a6faee4bba3cfe236b50256ff33|

Os demais hashes não foram inventados; URLs/localizadores e limitações constam nas notas. Como os pesquisadores registraram recuperação em memória, estes hashes identificam corpos consultados e não prometem existência dePDF arquivado neste worktree.

Consultadas com limite: Newey/West,NBERt0055/metadados-resumo, corpoPDF indisponível; não sustenta sozinho afirmações técnicas. Nakane/Weintraub teve partes lidas e falhas502/timeout em tentativas adicionais. REB2023 não usado para claims porque reaberturas não deram conteúdo confiável; substituído peloREF2024. FMIeLibrary indisponível foi substituída peloPDF final oficial. Res4553compiladav4 inclui2025: rejeitada como regra retrospectiva única. Wikipedia/RePEc/ResearchGate/snippets não foram base de afirmações críticas. PyMuPDF(fitz) indisponível não provocou instalação; leitura complementar usou pypdf já disponível, quando aplicável.

## Verificação e revisão

FatiaA:PASS independente. Literatura: verifier independente concluiuPASS com limites em `verification-literature.md`,18/10/2026,16:17:39UTC;F1–F5/E1–E6 conferidos, sem achado material. CorposBCBF4/F5 foram recuperadosHTTP200 em memória após falhaweb;REF coincide com o hash acima;WP90SHA256 `862c14e3c9a9f3e4be683476ac325d102e4dd98abc77fb5339ccc02395250292`. Leitura técnicaNewey/West continua não declarada.

Reviewer crítico posterior concluiuPASS B/C em `review-B-C.md`, semFATAL/MAJOR. Conferiu quatroCSVs, entradas/hashes, contagens da nota e capturasDrive. Três apontamentos menores foram atendidos: estado das revisões nesta proveniência, links/contratos dos tickets165/166 com dependências nativas e precisão da expressão12.960linhas no total do arquivo. Conferência final doSHA/checks/publicação/integração é registrada naIssue162/PR, sem transformar oPASS de conteúdo em estado remoto presumido. Não há estimador acadêmico adotado nem análise econométrica executada.

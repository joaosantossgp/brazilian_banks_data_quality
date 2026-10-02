# Proposta concreta de publicação da fundação

A publicação pública já foi autorizada em 2026-10-02. Esta proposta materializa o conjunto para revisão; não solicita um novo gate humano. Tasks 1–5 e a revisão final passaram. Task 5 preparou sanitização, reconciliação de autoridade, CI e manifesto final; checks na árvore curada e publicação remota foram concluídos e verificados. A Task 4 original não fez escrita remota; a execução posterior autorizada publicou o bootstrap e a feature, mantendo o PR em rascunho.

## Conjunto e exclusões

O [manifesto](../../reports/governance-publication-manifest.json) enumera arquivos explicitamente, bytes e SHA-256. A lista contém o conjunto exato após a sanitização da Task 5, incluindo `.github/workflows/ci.yml`; revisão independente e checks na árvore curada passaram antes de sua publicação no commit 00d6fe4. A coordenação conferiu fontes e blobs antes dos commits e publicou somente a lista final. O registro do próprio manifesto usa `self_reference: true` e SHA-256 null, evitando hash circular.

Incluídos: código e testes existentes, scripts, contratos e notas técnicas, relatórios públicos selecionados, duas templates, nove skills Matt e apenas Feynman deep-research/pdf-explore com arquivos de suporte e notices. As notas acadêmicas descrevem direção e decisões humanas; não há capítulo/manuscrito na lista. Nenhuma nova coleta financeira, fórmula, amostra ou recomendação foi criada.

Excluídos: `data/raw/`, `data/runs/`, `data/derived/`, índices de coleta, `.scratch/`, `expansion-stage/`, `.superpowers/`, caches, ambientes, tooling temporário, diagnósticos Playwright, backup Feynman inativo e provenance-before-selection. O relatório `reports/expansion-20261001.verification.json` também fica fora: contém caminhos pessoais absolutos em três raw_directory. Ele permanece intacto como evidência local; o relatório Markdown público conserva resultados e limitações. Nenhum corpo, captura ou dado bruto é publicado por este conjunto.

## Privacidade e verificações da Task 5

A leitura dos 117 candidatos após ignores totalizou 784.134 bytes. A busca delimitada por credenciais comuns não encontrou chave privada PEM, token GitHub, chave AWS AKIA ou chave sk longa; isso não constitui garantia universal de ausência de segredos. O regex de drive exige fronteira de palavra, evitando confundir `https:` com drive.

Sanitização aplicada com backup local ignorado e preservação semântica: README e AGENTS (checkout pessoal); brainstorming (aprovações privadas, citações de conversa e caminhos pessoais); expansion-execution e pilot-execution (caminhos); governance-source-research (arquivo pessoal); feynman-source-research (ID privado); spec/plano da fundação (IDs, trechos de aprovação privada, caminhos/comandos pessoais); selection Feynman (IDs privados). O tracker contém a URL pública legítima do proprietário/Project, não caminho privado; revisar sua autoridade e links, preservando a URL pública correta. Notas históricas não devem ser reescritas como nova execução.

Links substituídos por referências publicadas ou descrições explícitas de evidência local: AGENTS → task-1-brief/global-constraints; tracker → task-1-brief/global-constraints e `.scratch/ifdata-expansion/map.md`; capital-aberto-identity-dossier → CSV derivado identity-evidence. São seis links Markdown. O arquivo de verificação excluído está descrito como somente local onde referenciado. Identificadores de caminhos locais nos relatórios de proveniência são evidência, não downloads públicos. Links vendored para recursos upstream não autorizam copiar fontes adicionais nem modificar bytes upstream.

## Licenças e limites

Os 16 arquivos LICENSE candidatos foram lidos e preservam MIT upstream: dez notices nas skills selecionadas, Matt/Feynman em third_party e quatro referências. Proveniência/revisões selecionadas e hashes ativos permanecem verificáveis; a Task 3 conferiu 36 arquivos Matt e 30 Feynman. Não alterar fontes vendored na sanitização. A licença do código/documentação próprios ainda não foi escolhida; publicar com essa limitação explícita é autorizado, sem acrescentar MIT ao projeto por inferência. Preservar notices upstream não licencia código original. `/deepresearch` não teve runtime validado.

## Publicação inicial confirmada em 2026-10-02

- [Bootstrap main](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/2c0d5a766cc9ea197b37a0a062c5efb124bcbd02): quatro arquivos; templates chegaram à default branch main.
- [Feature completa](https://github.com/joaosantossgp/brazilian_banks_data_quality/commit/00d6fe46828955cfde9db4d2de1377c0fe20ff2b): exatamente 119 arquivos / 808.531 bytes. Manifesto SHA-256 `1d555dae7e0017bddd838d29bd678bbe3146d554ef9de84afaf5ab35c6c5a50e`; SHAs main/feature confirmados no remoto.
- [PR de publicação](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/1): rascunho aberto, main como base, sem merge.
- [CI do push](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37044529701) e [CI do PR exato](https://github.com/joaosantossgp/brazilian_banks_data_quality/actions/runs/37044656911): sucesso no commit inicial. Verificação offline anterior: 54 testes Python, guardas budget e 2 testes Node passaram; nenhum desses checks substitui validação econômica, contábil e financeira.

O manifesto JSON é o snapshot auditado do conjunto inicial no commit 00d6fe4, preservado sem reescrita. Alterações documentais posteriores têm seu próprio diff/commit e checks; seus bytes não devem ser comparados aos hashes antigos como se fossem a mesma versão. Esta correção não altera código, bruto, limites da entrega ou decisões metodológicas.

## Sequência autorizada — histórico executado e acompanhamento separado

1. Revisar bootstrap mínimo: README preparado pela coordenação, `.gitignore` e as duas templates em main. O bootstrap não contém collector; código completo ficará na entrega da feature.
2. Revisar Task 5 e manifesto exato, executar checks offline existentes na árvore curada e confirmar integridade/hashes.
3. Criar commit/push explícitos do bootstrap; publicar feature completa e abrir draft PR com CI. Sem `git add -A`, merge ou deploy.
4. Confirmar SHAs de main/feature, conteúdo remoto, templates na default branch, PR e runs/checks CI reais. Somente então registrar cada estado efetivamente observado. CI de software não valida conceitos econômicos, contábeis ou financeiros.
5. Reconciliar as mesmas tarefas com o Project existente /3, sem duplicar cards nem inventar IDs. Usar leitura suportada atual antes de mapear/atualizar estado.

Na preparação anterior à publicação, a coordenação verificou repo público, default main, sem branches/Issues naquele momento, ordinary push permitido, Actions habilitado e rulesets vazios. Isso não prova CI executada nem proteção de branches. Naquela preparação, CLI Project /3 view/item-list foi bloqueado por falta de read:project e nenhuma ferramenta Project suportada estava disponível àquela execução. Não renovar escopos/tokens nem automatizar UI. A coordenação trata esse bloqueio separadamente; publicação do código não implica sincronização confirmada do Project privado.

## Correspondência dos seis escopos históricos para Issues

O tracker histórico registra seis escopos de cards draft, mas não fornece títulos literais/IDs. A tabela usa os nomes de escopo registrados para correspondência por conteúdo, e não afirma que esses sejam títulos atuais nem que os cards permaneçam Todo. A leitura atual do Project deve confirmar o título literal e item original antes de criar/vincular Issue. Issues serão públicas no repo público.

| Escopo histórico registrado | Escopo/aceite da Issue correspondente | Evidência existente | Dependências e estado a verificar |
| --- | --- | --- | --- |
| capital aberto scope | Registrar fronteiras IF.data versus população acadêmica, elegibilidade temporal e decisões reservadas a João/orientador; sem amostra inferida | spec piloto; spec fundação; arquitetura; dossiê temporal | Antes de decisões de amostra e vínculos; ainda existem decisões humanas abertas |
| four MIT reference comparison | Comparar quatro referências pinadas, registrar mecanismos reutilizados/omitidos e conservar quatro notices | reference-comparison; third_party/references/*/LICENSE | Fundamenta collector; conferir conclusão com evidência, sem copiar implementação não autorizada |
| two-quarter pilot | Documentar 201012/202412 individual/Resumo, população/variáveis, exportação/replay e limites observados | plano/spec piloto; pilot-execution; reports/pilot-20261001.md; testes existentes | Depende de escopo e contrato de proveniência; validação local registrada e código/evidência publicados no PR; estado de Issue/Project a verificar |
| raw provenance | Preservar corpos imutáveis e manifests com parâmetros/horário/status/hash incluindo falhas; não publicar bruto | archive/replay; testes; ledger piloto; instruções README | Necessária para aceite/replay do piloto; dados continuam locais |
| coverage/missingness | Verificar grid/duplicatas, ausências estruturais e NI/blank/zero separados; não generalizar três períodos ao histórico | coverage/inventory; expansão discovery; reports/expansion-20261001-coverage.md; testes | Depende de aquisição verificada e schema/perímetro; conferência conceitual humana separada |
| temporal CVM/B3 evidence | Registrar atributos temporais e unknown sem inventar vínculo emissor/holding/unidade IF.data | metadata; dossiê capital aberto; ledger expansão; testes | Depende da fronteira de escopo e fontes temporais; oito vínculos seguem unknown |

Passos mínimos da coordenação quando a leitura estiver disponível: ler os seis itens atuais; comparar título/conteúdo com a tabela e evidência; localizar Issue existente antes de criar; preencher problema/arquivos/dependências/aceite e evidência; registrar item original → Issue real → mesmo acompanhamento; atualizar apenas estados sustentados por aceite/revisão. Sem essa leitura, o mapeamento é preparação e o Project permanece não confirmado.

## Correção posterior de identificação local — 2026-10-02

A revisão posterior dos 119 arquivos detectou identificadores de máquina que a auditoria inicial de caminhos/IDs/credenciais não cobria. A versão corrente remove esses identificadores de documentos e do campo hostname do relatório público de verificação, usando referências neutras ao computador autorizado. Contagens, fontes, períodos, hashes de corpos e resultados científicos permanecem inalterados; os originais são preservados como evidência local e no histórico Git. Não houve reescrita de histórico ou force-push.

A varredura ampliada cobre nomes locais de conta/máquina, caminhos pessoais, IDs privados de conversa e padrões de credenciais nos 119 arquivos. URLs públicas verificadas de repositório/Project/fontes e atribuições de autoria/licença upstream são preservadas. USERPROFILE nos comandos portáveis e loopback nos testes são referências técnicas genéricas, sem nomes locais de conta. Uma busca por padrões não constitui garantia universal de ausência de informação sensível; este registro corrige o alcance da alegação anterior e documenta a higienização da árvore atual, sem afirmar remoção de versões anteriores.

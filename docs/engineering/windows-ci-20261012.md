# Verificação nativa Windows offline — 2026-10-12

Entrega da [Issue94](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/94), após revisão da seleção OData93. O CI Ubuntu conserva sua suíte completa e guards Node. Um job separado `windows-native-tests`, runner `windows-2022`/Python3.12, exerce os vinte testes nativos antes ignorados no Ubuntu: claims exclusivos, compartilhamento de handles, ancestralidade, contenção, extinção das árvores e junctions.

O inventário explícito fica no próprio workflow. O runner exige host Windows, vinte casos carregados, nenhum skip e resultado unittest aprovado; um erro de importação, falha ou teste ignorado reprova o job. Não instala Node nem repete a suíte geral neste job, não faz coleta, upload ou deploy. As fixtures usam somente destinos temporários e processos locais conhecidos. Dependência DuckDB mantém o arquivo com versão/hashes existente e actions conservam seus SHAs pinados; permissões continuam somente leitura.

Configuração conferida nas [instruções oficiais de runners](https://docs.github.com/en/actions/how-tos/manage-runners/github-hosted-runners/use-github-hosted-runners) e [Python em Actions](https://docs.github.com/en/actions/tutorials/build-and-test-code/python), consultadas via Context7 em2026-10-12. A instalação pip depende de rede para obter a dependência; “offline” refere-se aos testes, sem requisições de dados financeiros.

O timeout15min é limite do job de testes, não teto universal de recursos/coleta. Tempo/resultado do host local, runner remoto e revisão independente são registrados na Issue/PR; o PASS Ubuntu não é transferido para Windows. Sem alteração de código de produção, dados aceitos, organização do pacote ou proteções.

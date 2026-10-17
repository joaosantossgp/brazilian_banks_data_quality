# Revisão documental após as pesquisas de universo e indicadores

Revisão da [Issue150](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/150), solicitada em17/10/2026. O objetivo é reconciliar as entradas de leitura com as pesquisas142/143 e tornar os quadros de fórmulas acessíveis pelo README. A revisão distingue estado corrente, execução já entregue, proposta e registro histórico; não altera método, indicadores, fontes ou dados.

## Alcance e fontes de conferência

Base de preparação: `08c843f6bf2bf67de39123a97583077a487a840d`, head revisado do [PR149](https://github.com/joaosantossgp/brazilian_banks_data_quality/pull/149). Após sua integração, esta branch avançou por fast-forward ao merge `ccb7402d448f5abf9c27a721ab23d095fcadf805`, com árvore idêntica. O preparo documental preservou o head149 e sua CI. A integração150 aguarda o pós-merge149, evitando cancelar a execução anterior de main.

O inventário Git encontrou158arquivos Markdown, dos quais127na raiz ou em `docs/`. A verificação determinística de624destinos locais de links inline nesses127documentos não encontrou destino inexistente na base. Excluiu skills/upstream, URLs externas, âncoras e links por referência. Isso é conferência estrutural, não leitura substantiva de todo o acervo ou validação de URLs remotas. Os recibos operacionais ficam no staging privado da tarefa.

A leitura substantiva concentrou-se em README, GLOSSARY, REFERENCES, arquitetura, protocolo, notas das pesquisas142/143 e suas proveniências, notas111/113, amostra125, ledgers127/130 e guia de consultas. As Issues142/143/130 e o fechamento doPR132 foram conferidos no GitHub; estado fechado não foi usado sozinho como prova de execução. A revisão de clareza usa `writing-guidelines`, [regras consultadas em17/10](https://raw.githubusercontent.com/vercel-labs/writing-guidelines/main/command.md), adaptadas aos contratos do projeto. Não instala metadados, framework, linter ou exigência editorial do produtoVercel.

## Estados que as entradas precisam distinguir

| Pergunta | Evidência corrente | Limite |
|---|---|---|
| Quem compõe o universo aprovado de companhias? | [Pesquisa142](cvm-open-financial-universe-2024-20261016.md):55companhias CVM A/B no corte31/12/2024,32associações comprovadas e24códigos financeiros distintos. |23sem correspondência principal admitida; AUZZA suspensa explícita; não é censo exaustivo nem elegibilidade retroativa. |
| O que já foi calculado? | [Implementação127](ifdata-monograph-analysis-20261014.md) e [universo130](ifdata-universe-analysis-20261014.md), integrado peloPR132/merge4061111. | Cálculos/vínculos pertencem aos seus contratos anteriores; a ampliação documental142 não os recalculou. Não transferir percentuais para as55. |
| Qual o universo da pesquisa de indicadores? | [Pesquisa143](financial-indicators-activity-review-20261016.md): sistema observado completo, vinculadas, restante e desconhecido; Financeiro principal. |Companhia e unidade são contagens diferentes; Prudencial/Individual permanecem próprios. |
| Quais métricas são atuais ou propostas? | Dez métricas atuais e sete complementos prioritários; fundamentos, fórmulas, componentes, disponibilidade e lacunas na143. |Novos candidatos não estão adotados ou implementados. Conjunto atual não garante cinco dimensões adequadas a todo negócio. |
| Como ler fórmulas por categoria? | [Atlas](financial-indicators-formulas-20261017.md): cinco quadros completos Tcb/SegmentoTb/Tc/Td/Sr original, com nome, variáveis, explicação e fonte. |Tc estratifica; Td exige perímetro; Sr exige regime. SrAnalitico é derivado separado; não criar fórmula por cruzamento ou reintroduzir Atividade. |

## Achados para reconciliação

Localizadores abaixo referem-se à base08c843f. “Prioridade1” indica risco de confundir objeto/método; “prioridade2”, navegação ou precisão documental. O aceite final registra o que foi corrigido; não significa adoção acadêmica.

| Localizador da base | Prioridade | Achado e implicação | Correção delimitada |
|---|---:|---|---|
| README:3,17–27 |1| A abertura limita a leitura a vinculadas; fórmulas/janelas aparecem genericamente em aberto apesar das decisões e implementação posteriores. | Apresentar quatro recortes do sistema; separar conjunto atual, ampliação candidata e escolhas ainda humanas. |
| README:43–61 |1| Posição de13/10 e piloto de oito candidatos dominam a entrada; pesquisas142/143 e motor130 não estão na rota de leitura. | Acrescentar estado corrente e destinos canônicos, preservando piloto como anterior. |
| README:31–41 |2| Não há caminho direto para os quadros completos com fórmulas por recorte. | Tabela de links para os cincoSVG ePNG e guia textual do atlas. |
| GLOSSARY, “Unidade analítica”/“População técnica e amostra acadêmica” |1| Definições registram apenas o desenho parcial13/10; falta distinguir comparação sistêmica e a lista ampliada documental. | Atualizar conceitos correntes com referências, preservando companhia/unidade, perímetro e vínculo temporal. |
| REFERENCES, introdução/Assaf/FMI/evidência produzida |1| Biblioteca não incorpora claramente a143 e a consulta posterior à edição finalFMI; médias já adotadas podem ser lidas como inteiramente candidatas. | Separar leitura111 e releitura143, versões e adoção temporal; apontar pesquisas/universo/atlas sem alegar nova leitura. |
| Protocolo, abertura/registro14/10 |1| Universo55 já aparece, mas o planejamento130 ainda pode ser lido como estado atual e menciona Atividade entre filtros. | Faixa de estado corrente; esclarecer execução integrada e retirada posterior de Atividade, sem apagar o planejamento histórico. |
| Pesquisa143, entrada do atlas; arquitetura, referência visual |2| A entrada fala em dois quadros completos após a extensão para cinco; referênciaSr/SrAnalitico pode ocultar a separação. | Atualizar somente navegação/contagem e escopo documental, sem modificar fichas, fontes ou matrizes. |

## Limpeza de navegação e triagem de legado

O pedido posterior de João inclui retirar legado sem uso ou documentar o que ficou defasado. A navegação do README foi consolidada em uma tabela de consultas, removendo cinco blocos repetitivos; âncoras antigas, inclusiveL70/L76, permanecem por compatibilidade. A biblioteca deixou de apresentar inventário, revisão inicial e estatística já entregues como pendências genéricas.

As quatro notas abaixo continuam referenciadas e sustentam contratos/fontes. Recebem faixas no início com seu alcance histórico e ligação para a entrada corrente; seus corpos, fontes e artefatos permanecem preservados.

| Item anterior | Uso remanescente e tratamento |
|---|---|
| [Componentes acadêmicos de 04/10](academic-indicators-components-20261004.md) | Referenciado em 7 arquivos na base. Proposta anterior à adoção; faixa histórica aponta111,127/130 e143. Não é carteira vigente. |
| [Piloto de 11/10](ifdata-indicator-pilot-20261011.md) | Referenciado em 11 arquivos. Contrato exploratório/reprodução própria; oito candidatos não limitam os dez atuais ou os novos candidatos. |
| [Pesquisa111 de 14/10](financial-dimensions-literature-20261014.md) | Referenciada em 7 arquivos. Fundamentação/decisão inicial continuam usadas; execução futura e cobertura antigas são localizadas na data, com ponte para143. |
| [Review físico de 12/10](repository-review-20261012.md) | Referenciado em 5 arquivos. Snapshot de arquitetura/tabelas, sem módulos posteriores127/130; faixa indica arquitetura e ledgers correntes. |

As contagens vêm de `git grep -l -F` pelo nome de cada arquivo no merge-base ccb7402; medem referências textuais em arquivos, não chamadas de software ou prova de leitura humana. Nenhum desses quatro documentos é órfão comprovado. A triagem não encontrou descarte inequívoco que justificasse apagar evidência nesta fatia; houve limpeza da orientação corrente e marcação dos registros anteriores. Leitores portal, snapshots, planos executados, licenças upstream e relatórios aceitos conservam seus contratos: idade, sozinha, não demonstra ausência de uso. Não houve rename/delete ou alteração de código/dados. Uma avaliação futura de código morto exige referências/chamadas e testes próprios, fora desta revisão documental.

## O que permanece separado desta revisão

Os registros datados de implementações, pilotos e pesquisas anteriores são evidência, não erros a apagar. O mapa visual de pesquisa publicado em13/10 permanece conceitual e datado; a leitura corrente deve seguir o texto e os quadros atualizados. Este lote não redesenha esse mapa nem gera novos gráficos.

O guia de consultas conserva comandos e contratos verificáveis de cada entrega. Navegar por um ledger atual não autoriza executar `build`, replay ou coleta. Não foram reexecutados comandos de dados para atualizar texto. A Release criptografada de12/10 é transporte datado e não recebe automaticamente os pacotes posteriores.

Adoção dos complementos da143, recálculo para o universo142, índice composto/econometria e reconciliação do manuscrito continuam decisões/tarefas próprias. Esta revisão não cria seus contratos, pesos, limiares ou novas exclusões. A [Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) conserva a autoridade acadêmica; o [mapa2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) conserva execução/prontidão.

## Checkpoints

Fatia1: inventário e achados aprovados independentemente antes da reconciliação, com recomendação incorporada de corrigir a tabela de pendências de REFERENCES. Fatia2: os sete achados foram tratados nas entradas autorizadas; o acréscimo de legado recebeu contrato explícito na mesma Issue e faixas em quatro notas referenciadas. Links/coerência/allowlist e revisão independente da composição/SHA precedem integração. Resultados remotos e evidências finais são registrados naIssue150; esta nota não transforma preparação em PASS global.

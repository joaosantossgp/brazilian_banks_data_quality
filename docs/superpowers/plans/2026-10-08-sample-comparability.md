# Amostra e comparabilidade — plano da Issue 16

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans por checkpoint, com revisão independente antes de ampliar cada resultado. A PR pode ter o tamanho necessário; não criar uma PR por etapa ou período.

**Goal:** entregar alternativas fundamentadas e uma sequência executável para seleção da amostra 2010–2024 e comparabilidade, reutilizando as Issues existentes. Pesquisa, decisão humana e implementação são resultados distintos.

**Architecture:** preservar a base financeira nativa, seus contratos e os complementos separados. A futura amostra será uma seleção documentada sobre ocorrências e vínculos temporais comprovados; transformações analíticas dependerão de contrato próprio, sem reescrever bruto ou aceites nativos. Este lote entrega apenas nota e plano.

**Tech Stack:** Markdown, fontes primárias BCB/CVM/B3 e contratos existentes; futura execução reutiliza Python/DuckDB/Parquet somente depois do contrato correspondente, sem dependência nova aprovada aqui.

**Spec:** [contrato real da Issue 16](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16), [claim desta entrega](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16#issuecomment-6100651695), [spec da fundação](../specs/2026-10-02-governance-research-design.md) e [pesquisa de amostra/comparabilidade](../../engineering/sample-comparability-research-20261008.md).

Base: `main 030a102d5613d4c9a100da1369060e378d721f5c`. Branch: `codex/sample-comparability-research`. Root coordena/integra; pesquisador escreve a nota, reviewer independente lê e reporta. Data de execução: 2026-10-10; nomes de arquivo conservam os destinos aprovados em 2026-10-08.

## Restrições globais e inventário

- Janela acadêmica 2010–2024, capital aberto; população/unidade/método/indicadores finais pertencem a João/orientador na #3/#14. As alternativas da nota não são decisões adotadas.
- Allowlist pública deste lote: **somente** `docs/engineering/sample-comparability-research-20261008.md` e este plano. Dois arquivos novos nos destinos canônicos existentes, sem nova pasta, camada, renames ou deletes. Nenhum módulo, registry, perfil, dado, runtime, proteção ou Project /3 alterado. Evidência operacional privada permanece em `.scratch/`.
- Base nativa continua 11/66 aceita, com aquisição59 bloqueada na evidência de persistência2012. Pesquisa não depende de concluir a aquisição, mas cálculo real depende das entradas aceitas necessárias. Não usar cadastro corrente como painel histórico, nome como vínculo ou fonte disponível como cobertura comprovada.
- Preservar oito vínculos desconhecidos do dossiê, identidade/perímetro/versão nativos, Decimal/lexemas e distinções entre ausência estrutural, NA, NI, null, vazio e zero. Não aplicar pesos, imputação, annualização ou harmonização nesta entrega.
- Nova aquisição de metadados, eventual abertura200912 e qualquer execução analítica exigem recorte/entradas/destinos próprios;200912 fica fora das66 referências. Não criar novas Issues neste lote nem mudar labels/proteções como consequência automática do plano.

## Fatias desta entrega de pesquisa

### 1. Elegibilidade e unidade — concluída/revisada localmente

- [x] Inventariar #3/#14 e dossiê; apresentar opções de população, coorte/dinâmica, aferição temporal, vínculos/eventos e painel, separando fatos, inferências e desconhecidos.
- [x] Pesquisador: somente a nota; checks de fontes/localizadores, seis links relativos e whitespace. Sem teste de software para texto ou aquisição de bases.
- [x] Revisão independente APP, sem P1/P2, snapshot `46ae126af559c5af8b6c63f7f710463d2862c5d874d3e7be92b5068a7c977a47`. [Checkpoint real](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16#issuecomment-6100730869).

### 2. Comparabilidade por família/época — concluída/revisada localmente

- [x] Acrescentar matriz de conceitos/componentes, unidade/escala, estoques/fluxos, janelas, perímetro, vintage/reapresentações e fronteiras2014–2015/2018; contexto2025 fora da amostra. Propor condições de transformação/segmentação/rejeição, sem adotá-las.
- [x] Reutilizar seis contratos/notas; acrescentar três fontes documentais, com localizadores e limites; doze links relativos/whitespace conferidos. Prefixo da primeira fatia preservado.
- [x] Revisão independente APP sem P1/P2, snapshot `2d5fc713b7f91cd45bd51a36819d9e78d8b42d2db544478a42d1716cff8cbc7b`. N1 corroborada; N2/N3 retornaram timeout na revisão, sem confirmação independente de artigos/página. Não apresentar certificação normativa integral. [Checkpoint real](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16#issuecomment-6100766476).

### 3. Plano, composição e entrega — integrador Root

- [ ] Conferir este plano contra a nota e Issues reais: nenhuma implementação dependente marcada pronta, nenhuma decisão inventada, nenhuma nova Issue.
- [ ] Reviewer independente confere as duas allowlists, arquitetura, links/âncoras, decisões/lacunas e composição; resolver achados materiais antes de publicar. Se o texto mudar depois, conferir o delta e o SHA entregue.
- [ ] Publicar branch/PR com os dois arquivos exatos, evidências das revisões parciais e limites. Executar checks documentais pertinentes; observar CI existente sem criar testes que reproduzam o texto ou alterar o workflow. Confirmar checks/head/revisão/merge e CI pós-merge antes de declarar integração.
- [ ] Atualizar a própria #16 e a fronteira da #2. O aceite desta pesquisa é proposta fundamentada + plano publicado/revisado; não depende de João já ter escolhido método. #3/#14 continuam com suas decisões/lacunas; aquisição e base completa conservam aceites próprios.

## Sequência posterior nas Issues existentes — proposta, sem claim de código

| Etapa / Issue existente | Resultado e dependências | Owner, destino e condição de saída |
|---|---|---|
| Decisão de população/unidade/tempo — [#3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) | João/orientador escolhem significado de capital aberto, coorte/dinâmica, aferição temporal, unidade principal/complementos, eventos/multiplicidades e desenho de painel. Entradas: fatias1/2; registrar alternativas rejeitadas e justificativa. | Decisores humanos; agente registra fielmente no destino de domínio aprovado na #3, com `domain-modeling` quando houver registro. Sem escrever glossário/ADR por este plano. Aceite: decisão datada com critérios observáveis, não simples concordância genérica. |
| Contrato de evidência temporal — etapa posterior da própria [#16](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16) | Depois da decisão3, especificar fontes/versões, entidades/relações/intervalos, eventos, estados desconhecidos, critérios de conflito e cobertura. Dimensionar eventual aquisição de metadados separadamente, sem assumir que FRE/B3 já cobrem cada banco. | Research/domain; reutilizar a nota como entrada. Antes de assumir execução, atualizar o contrato da mesma Issue com resultado/role principal/base/allowlist/destinos/aceite da nova fase; se a pesquisa estiver encerrada, reabrir/retriagem explícita preservando o histórico. Não iniciar uma tarefa sob o contrato de texto atual. |
| Implementar seleção e vínculos — fase condicionada da #16 | Só após contrato temporal aprovado e fontes aceitas. Reutilizar `bank_quality/metadata.py`/`tests/test_metadata.py` se forem os responsáveis confirmados; manter filtro e vínculos analíticos separados do armazenamento nativo. Publicar inventário de elegíveis/inelegíveis/unknown e razões por referência, sem inferir continuidade. | Futuro executor `role:implementation`, integrador Root. Estes paths são candidatos limitados, **não allowlist de escrita concedida**; contrato final define arquivo/destino de saída novo. Aceite: replay, vínculos auditáveis e revisão antes de ampliar a toda a amostra. |
| Componentes e ajustes por indicador — [#14](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/14) | Reutilizar pesquisa já publicada; recuperar a lista original ausente ou obter reformulação explícita. Conciliar fórmula, numerador/denominador, unidade, janela, perímetro/regime, médias e tratamento de zero/PL negativo. #3 decide adaptações; não inventar indicador substituto. | Pesquisa e decisão próprias na #14/#3; depois, triagem explícita da fase de execução e allowlist. Cada indicador tem contrato/checkpoint, podendo compartilhar PR. Dependência é cobertura dos componentes necessários, não obrigatoriamente66/66 para qualquer ensaio delimitado. |
| Transformações comparáveis e validação da análise — fase condicionada #16/#14 | Adotar somente correspondências/transformações aprovadas, por família/época e entradas aceitas. Conservar saída nativa, lineage e qualificações; manter unknown quando equivalência não for demonstrada. Escalar depois de revisão do primeiro recorte pertinente. | Owner por módulo confirmado no contrato futuro, saídas analíticas em destino canônico novo; não editar registry/perfis para fazer uma hipótese parecer nativa. Rejeitar expansão quando houver achado material. Aceite analítico não encerra base64 nem certifica método causal. |
| Complementos — [#62](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/62) → [#63](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/63) | #62 prepara alternativas e registra conteúdo individual/prudencial escolhido; #63 só implementa o aprovado. Esta decisão é distinta de amostra/unidade3; não cortar a principal financeira nem emendar perspectivas para preencher lacunas. | Ownership/destinos próprios definidos no contrato62/63. Não criar duplicata de pesquisa ou liberar coleta por esta nota. |

As fases posteriores reutilizam as Issues indicadas, sem manter duas roles principais simultâneas na mesma execução. A triagem da próxima fase é uma condição concreta de início, não uma nova autorização rotineira para a pesquisa já aprovada. Alteração de método/conteúdo continua com João; escolhas técnicas dentro de contrato aprovado conservam a autonomia vigente.

## Checks causais e checkpoints da implementação futura

Os casos abaixo são critérios de comportamento a especificar no contrato futuro, **não testes criados para este texto**. Fixtures devem comprovar a hipótese e sua rejeição antes de aplicar a regra a fontes reais.

| Recorte | Caso que deve distinguir | Checkpoint de expansão |
|---|---|---|
| Elegibilidade temporal | Registro/listagem atual não prova2010; entrada no meio da janela; cancelamento/suspensão distintos; reingresso e vigência desconhecida. | Primeiro dossiê/intervalo completo e caso adverso revisados antes de expandir emissores; ausência de prova retorna unknown com razão. |
| Identidade/perímetro | Oito dígitos não viram CNPJ completo; holding/banco diferentes; dois emissores para uma unidade; fusão/troca de controle sem continuidade presumida. | Reviewer confere documentos das duas pontas/data/namespace e multiplicidades, não somente teste de schema. |
| Fluxos | Dezembro semestral não anual; somar março/junho duplica acumulados; junho+dezembro exige mesma definição/perímetro e versões conciliadas. | Conferência contábil do primeiro par e teste que rejeite janela/perímetro incompatível antes de série completa. Nenhuma anualização aqui adotada. |
| Unidade/precisão | BRL cru versus R$mil exibido; contagem versus moeda; soma/razão excedendo representação; tokens/zeros preservados. | Comparação exata de lexemas/Decimal e limites explícitos, sem DOUBLE ou arredondamento silencioso. |
| Indicadores/cobertura | Numerador/denominador e janela corretos; provisão estoque versus despesa fluxo; médias requeridas ausentes; denominador zero/negativo conforme método aprovado. | Revisão conceito/fonte separada da integridade; evidenciar denominadores de cobertura por componente/razão/unidade, sem excluir bancos silenciosamente. |
| Replay/versões | Mesmas entradas/decisões produzem a mesma saída lógica; mudança de fonte/versão é identificável, sem sobrescrever saída aceita. | Novo destino de replay, comparação e lineage; revisão do lote antes de ampliar. Não somar passes isolados para declarar PASS global de uma execução falha. |

## Preservação, paralelismo e handoff

Esta entrega não tem migração de dados a reverter. Em futuras transformações, interrupção preserva entrada e tentativa; nova saída aceita exige contrato e destino novo, sem restaurar por cima dos nativos ou reconstruir saldo de aquisição. Erro material interrompe somente o recorte afetado e sua expansão; corrigir/revalidar antes de continuar.

Pesquisa16 e preparação de alternativas62 podem avançar independentemente da coleta59, com arquivos próprios. Cálculo/seleção implementada dependem das decisões e provas indicadas. #60 aguarda handoff59 admissível; #61 amplia catálogo após aceites nativos60; #64 audita59/60/61/63. Escolhas acadêmicas não impedem preservar/admitir/consultar a base nativa. Conferir a fronteira real na #2 em cada handoff; Project /3 permanece com Zec.

Handoff: base/head e inventário completo das duas notas, snapshots/revisões, checks/limites e links reais. Uma entrega futura inclui decisões/versões, fontes e hashes, cobertura e desconhecidos, comandos/saídas, reviewer e primeiro próximo passo. Não enviar chave, pacote decriptado, bruto ou coordenação privada ao GitHub. Concluir a pesquisa16 não significa concluir aquisição55, amostra, indicadores, complementos ou Goal.

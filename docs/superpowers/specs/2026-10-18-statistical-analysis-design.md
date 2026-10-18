# Desenho da análise estatística — 2010–2024

Issue:[162](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/162). Evidência:[pesquisa](../../engineering/statistical-analysis-research-20261018.md) e [proveniência](../../engineering/statistical-analysis-research-20261018.provenance.md). Esta spec sintetiza o recorte solicitado e diferencia execução descritiva sobre regras existentes de propostas metodológicas novas.

## Problema e solução

A base contém agregados e distribuições extensos, mas presença temporal não informa cobertura conjunta, mudanças de composição ou validade de comparação. João precisa selecionar indicadores e recortes úteis para responder aos objetivos da monografia e organizar o argumento do texto.

Preparar um caderno de evidência descritiva com dados pinados, população e perspectiva explícitas. O eixo principal é sistema observado eTcb;Sr/SrAnalitico e associadas/restante entram com janelas e cobertura identificadas. A literatura delimita extensões econométricas para decisão posterior, sem impor ranking/índice ou modelos.

## Necessidades observáveis

1. Identificar pacote aceito por ponteiro/hash e fixá-lo para a tarefa.
2. Verificar integridade das tabelas antes de consultar.
3. Saber quais períodos têm agregado e quantas/quais unidades são elegíveis ou ausentes, conforme detalhe efetivamente disponível.
4. Ver cobertura de componentes/indicadores, vínculos e peso econômico conhecido separadamente.
5. Comparar agregado e distribuição já contratados sem confundir instituição típica e peso econômico.
6. Selecionar aberturasTcb pertinentes sem fórmula bancária universal ou seleção por significância.
7. DistinguirSr original deSrAnalitico e suas janelas/fontes.
8. Comparar associadas e restante preservandounknown e sobreposição comtotal.
9. Examinar composição e sensibilidade quando houver suporte unitário e contrato.
10. Ligar cada saída a uma pergunta e afirmação permitida no texto.
11. Avaliar ganho/custo e hipóteses de econometria antes de escolher estimador.
12. Preservar originais, cálculos aceitos, manuscrito e frentes concorrentes.

## Decisões técnicas e interfaces

- Consumir saídas aceitas via leitura autenticada; não reconstruir o motor financeiro nem promover o ponteiro.
- Reusar razão das somas, quantis tipo2 e frações exatas existentes. Não somar razões/quantis de células para criar agregado total. Contagens das coortes disjuntas podem compor total depois de reconciliação.
- Saída de diagnóstico éCSV/recibo em destino privado novo; estudo e spec são públicos sem dados/manuscritos privados. O protótipo de diagnóstico já executado é evidência finita, não API pública de produção.
- Seleção editorial de indicadores permanece proposta até decisão acadêmica; inventário integral permite escolher por conceito/cobertura sem esconder os demais.
- Complemento macro pertence à159. Analítico/vínculos em outras frentes não são alterados. Migração a novo pin exige declarar deltas e repetir checks afetados.

## Alternativas e recomendação

**A. Descrição/comparação:** suficiente para a pergunta de evolução/diferenças observadas, com agregadosTcb, distribuição e cobertura. Recomendação de núcleo.

**B. Associação agregada:** extensão parcimoniosa se uma pergunta justificar regressores/janelas e diagnóstico de séries. Estimador/HAC/bandwidth não adotados.

**C. Painel institucional:** extensão se houver pergunta dentro/entre unidades, identidade temporal, amostra e inferência apropriadas. FE/clusters não tornam a comparação causal.

As rotas podem coexistir, masB/C não são pré-condição automática daA. O orientador/João escolhem métodos adicionais e conteúdo acadêmico final.

## Fatias/tickets verificáveis

1. **Pesquisa e viabilidade162:** literatura citada, diagnóstico autenticado e limites; concluível sem adoção do método.
2. **[Decisão de comparações/métodos,165](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/165):** apresentarA/B/C, seleção principal/apêndice e eventuais sensibilidades; João/orientador decidem. Depende da pesquisa162 revisada. É escolha acadêmica, não nova confirmação técnica de publicação.
3. **[Caderno descritivo sistema/Tcb,166](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/166):** consumir regras existentes, entregar matriz de disponibilidade e tabelas/recortes escolhidos; dados em destino privado novo, sem alterar explorador. Depende162 e165. Somente depois da pergunta/estimando escolhidos abrir implementação de modelo/cálculo adicional suficientemente especificada.

Esta decomposição evita um ticket genérico de “implementar toda econometria” sem pergunta ou aceite. As dependências nativas165←162 e166←162/165 foram criadas e lidas de volta noGitHub. Não há execução166 declarada enquanto165 estiver pendente.

## Checks e revisão

Diagnóstico: hash externo, rows/id únicos, zero preservado, estados/faltas separados, reconciliação coortes/categorias, sem truncar população. Literatura: fonte primária/localizador, inferência sinalizada, acesso parcial explícito, verifier e reviewer sequenciais. Documentação: UTF-8, links/coerência/allowlist e revisão de composição/SHA. Não adicionar testes que repitam a prosa.

Se o caderno requerer código reutilizável, o ticket próprio define allowlist e testes comportamentais pertinentes: hash divergente, denominadorzero, ausência versuszero, células/coortes não duplicadas e regressão de saídas existentes. Não se instala pacote estatístico ou suíte genérica antes de existir método escolhido.

## Fora do escopo e aceite

Fora: nova coleta financeira/macro, alteração de fórmulas/links/classificação/explorador, manuscrito/Drive, novo índice/pesos, imputação, corte deoutlier, regra de representatividade, modelos causais e infraestrutura/segurança/Project.

Aceite desta spec: cada proposta ligada à pergunta/dados/hipóteses/saída/limites, cobertura do pin observada e não presumida, alternativas condicionais, tickets com dependências reais e revisão independente. Não declara resultados acadêmicos finais ou validade causal.

# Indicadores por Tcb e comparação com Assaf — plano seletivo

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Use subagent-driven-development somente quando o contrato autorizar delegação; revisão independente continua obrigatória. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** viabilizar indicadores adequados a cada negócio do sistema IF.data observado, reaproveitando as bases e o motor atuais, começando pelas lacunas que têm componentes locais.

**Architecture:** manter matemática em `bank_quality/ifdata_analysis.py`, execução seletiva/composição em `bank_quality/ifdata_universe_analysis.py` e CLI fina existente. Reutilizar contratos autenticados de OData, catálogo, cadastro, fluxos e médias; não criar framework, motor por Tcb ou pipeline concorrente. Fontes específicas só entram após demonstrar a insuficiência da base atual.

**Tech Stack:** Python/DuckDB e precisão Fraction/Decimal existentes; Parquet com manifest e saídas novas; SVG/PNG documentais. Sem dependência nova.

**Spec:** [nota e caderno visual178](../../engineering/tcb-indicators-assaf-atlas-20261018.md), pedido humano registrado na [Issue178](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/178), [adequação152](../../engineering/ifdata-tcb-indicator-adequacy-20261017.md), [pesquisa143](../../engineering/financial-indicators-activity-review-20261016.md) e [protocolo vigente](../../engineering/institution-type-indicator-methodology-20261012.md).

## Limites globais e estado de autorização

- **Esta entrega planeja, não executa novos indicadores.** As caixas abaixo são trabalho futuro; nenhuma implementação ou coleta foi liberada só pela publicação do plano. Adoção de fórmula/conteúdo acadêmico pertence a João/orientador na3; após a escolha, abrir/contratar a entrega correspondente sem repetir gates rotineiros já satisfeitos.
- Sistema completo2010–2024; vinculadas/restante/desconhecido em coortes próprias. Não limitar o piloto aos32vínculos. Financeiro principal; Prudencial/Individual separados, sem empréstimo de contas ou capital entre perspectivas.
- OitoTcb observados, refinamentoSegmentoTb, data, contas e perímetro; Tc/Td/Sr contextualizam, SrAnalitico separado, Atividade fora. Não inferir licença/subtipo pelo nome nem criar uma fórmula para cada cruzamento.
- Base inicial178: `historical-links32-composition-20261018-run3`, manifest `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`. Redescobrir o ponteiro antes da futura execução; migração deve ser explícita, preservando o pin anterior. Hashes das tabelas consumidas devem conferir.
- PacoteODatafinanceiro manifest `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095`; catálogo manifest `73d8e09c5662bbf8f2b4865802dfec376e8a3da3c358ca81aa3695e881171ffd`. São pins desta auditoria, não seleção automática de bases futuras.
- Preservar20métricas aceitas; cálculo novo só para IDs/janelas selecionados, nunca rebuild global por conveniência. Novo destino em `data/curated/`, sem sobrescrever fontes, resultados, ponteiro ou explorador. Promoção/publicação do artefato de dados terá aceite próprio.
- Estoques na mesma data; fluxos trimestrais efetivos eTTM de quatro trimestres disjuntos; médias temporais com abertura e ponderação vigentes. Não anualizar por×4, somar estoques ou projetar vínculo atual para o passado.
- Zero no denominador é indefinido; null/ausente/histórico insuficiente/negativo/não aplicabilidade são estados distintos. Preservar reversões. Razões de somas só na interseção válida e mesma fórmula/unidade/perímetro.
- Sem nova coleta financeira, correçãoBRB, Ke/dividendos inventados, índice único, imputação, winsorização ou inferência causal. Não operarProject3.

## Ordem proposta e critérios de escolha

| Fatia | Resultado | Prioridade econômica / esforço | Condição para começar |
|---|---|---|---|
| 0 | Fixar entradas e aproveitar diagnósticos atuais | Evitar reabrir cobertura já medida | Contrato da futura entrega e pin autenticado |
| 1 | Piloto das sensibilidadesL1/R3/RIF_AT/PL_DEP escolhidas | Esforço baixo/moderado; explicação do banco depositário, não principal lacunaN2/N4 | João escolhe quais sensibilidades interessam; fórmulas abaixo |
| 2 | Conciliação de renda/custos ampliados | PrioridadeN2/N4/B2 e grupos diversificados | Nenhuma adoção prévia de novo denominador; nota conta a conta primeiro |
| 3 | Conciliação de arrendamento | PrioridadeN1 com leasing | Carteira/rendas/provisão compatíveis demonstradas |
| 4 | Mapa de lacunas específicas por negócio | Centralização, maturidade, clientes e salvaguarda | Pesquisar abertura local; fonte adicional só quando a lacuna estiver identificada |
| 5 | Piloto→revisão→expansão seletiva→composição | Somente das fórmulas efetivamente adotadas | Revisão econômica e teste de cada fatia anteriores |

Fatia1 e a preparação documental2/3 podem ser independentes em ownership de notas; se implementarem no mesmo avaliador, sequenciar ou delimitar trechos e reconciliar. Não há obrigação de fazer1antesde2/3: a prioridade final combina pergunta econômica e esforço. O plano não reabre os sete complementos já implementados152.

## Fatia0 — entradas, população e cobertura

**Files:** ler `bank_quality/ifdata_odata.py`, `ifdata_variable_catalog.py`, `ifdata_analysis.py`, `ifdata_universe_analysis.py`; usar `scripts/analyze-ifdata.py` e `scripts/import-ifdata.py` somente em operações de leitura. Preparação/recibos em destino privado novo do contrato futuro. Nenhuma alteração de leitor ou manifest aceito.

**Interfaces:** `open_dataset(output)` autentica todas as partesOData e expõe a view `ifdata`; `query_catalog(output, sql)` autentica catálogo; `evaluate_metric(metric, inputs, horizon)` é a matemática existente. `inputs` contém `period`, `components` com listas deObservation, `financial_statement` e `prudential_bridge`; saída já traz fraçõesN/D, estado, componentes, flags e limites. Não introduzir uma segunda implementação emSQL/explorador.

- [ ] Redescobrir `current-indicators.json` pelo comando canônico do [guia](../../engineering/local-queries-20261013.md#base-de-indicadores-vigente-entre-tasks); registrar caminho/pin e autenticar tabelas.
- [ ] Fixar datasets/cadastro da própria unidade/período e60trimestres, sem inferir subtipo por saldozero. Unidades desconhecidas ficam no diagnóstico.
- [ ] Reproduzir presença conjunta sem razões, tomando o instrumento178 como receita privada descartável. Duplicidade de chave conhecida interrompe; cadastro/código nulo conservam estados explícitos.
- [ ] Produzir por candidato×trimestre×Tcb: esperadas, presentes juntas, denominadorzero/negativo/positivo, nomes/códigos/companhias/coorte, AT/crédito/PL conhecido e desconhecido. Não chamar presença de calculabilidade.
- [ ] Conferir diagnósticos175/176 aceitos no momento. Caixa28resultados e janelasN1/N2 são frentes de cobertura próprias, não justificam alterar nova fórmula para recuperar cobertura.
- [ ] Revisão independente da população, pins, contextos e listas antes de ampliar a implementação.

**Aceite:** recibo reprodutível e manifesto de entradas; quantas/quais unidades ficam sem componentes e sem histórico, por período/coorte/Tcb; representatividade somente sobre estoques conhecidos, com desconhecidos separados. A auditoria178 já encontrou1.415/1.422conjuntos contemporâneos em4T2024; isso não antecipa o aceite de nenhum fluxo/TTM.

## Fatia1 — sensibilidades do capítulo18 com componentes locais

**Files a alterar se adotados:** `bank_quality/ifdata_analysis.py` (registro/componentes e ramo mínimo do avaliador), `bank_quality/ifdata_universe_analysis.py` (allowlist da execução seletiva), `scripts/analyze-ifdata.py` somente se a opção existente não bastar. Testes em `tests/test_ifdata_analysis.py` (inclui ComplementMetricTests) e `tests/test_ifdata_selective_analysis.py`. Usar nota178 e recibo próprio para resultados; não editar fórmula anterior nem criar módulo novo.

| Candidato | Fórmula proposta, em fração | Componentes exatos noFinanceiro | Tempo e interpretação |
|---|---|---|---|
| L1, encaixe voluntário | DISP/DV | Ativo2/78188 ePassivo3/78282 | Estoque/data. Assafp334; depositárias, abertura deL2. DVzeroindefinido. |
| R3, margem líquida da intermediação | LLw/RIFw | Resumo1/78187 eDRE4/78208 | Trimestre/TTM na mesma janela; Assafp341. LLantes/depois201903 e escopo das pontes precisam respeitar contratos. RIFnãoé receita total; renda negativa mantém sinal/alerta. |
| RIF_AT, lucratividade dos ativos | RIFw/ATmédiow | DRE4/78208 eResumo1/78182 com abertura | Assafp342; média proposta explicitamente. Não éROA nem margem. Não fabricar média se a unidade não tem histórico próprio compatível. |
| PL_DEP, capital/depositantes | PL/DEP | Resumo1/78186 ePassivo3/78287 | Estoque/data; Assafp337. Sensibilidade depositária; depósitos não são todas as fontes. PLnegativo preservado/alertado. |

Os nomesRIF_AT/PL_DEP são IDs propostos, não registrados hoje. L1/R3 já eram fichas candidatas, não decisões de rejeição. Não atribuir o motivo de priorização desta proposta como causa histórica da seleção anterior. Grupo/nome/definição devem ser copiados dos contextos completos do catálogo, nunca por busca só do número.

- [ ] Escolher as métricas que respondem à pergunta da análise; registrar opção e custo/benefício. Não ampliar por mera disponibilidade.
- [ ] Escrever testes de comportamento no avaliador antes do registro novo: L1comDISP5/DV20→fração1/4; PL_DEPcomPL−10/DEP40→−1/4ealerta; R3comLL3/RIF12→1/4eRIFzero→indefinido; RIF_ATcomRIF12/ATmédio120→1/10. Valores internos são frações, exibição percentual separada.
- [ ] Acrescentar testes de ausência/null, denominadornegativo, janela incompatível, duas definiçõesLL, quarter/TTM e histórico de abertura. Usar fixturesObservation do teste atual, preservando unidade/perímetro/escala. Reversões e resultadosnegativos não viramzero.
- [ ] Rodar `python -m unittest discover -s tests -p test_ifdata_analysis.py` e confirmar falha atribuível ao IDnovo/contrato esperado antes da alteração mínima.
- [ ] Implementar os ramos aditivos dentro de `evaluate_metric(metric, inputs, horizon)`, reaproveitando resolvedores temporais/frações. Não alterar `METRICS` anteriores nem permissões dos perfis históricos.
- [ ] Reexecutar testes pertinentes e `python -m unittest discover -s tests -p test_ifdata_selective_analysis.py`; conferir que as20métricas anteriores têm assinaturas econômicas idênticas no mesmo recorte.
- [ ] Piloto seletivo de estoqueem202412 efluxosem201812/201903/202412, sistema completo nas datas. Contrato de lote impede expandir ao restante dos60trimestres antes da revisão.
- [ ] Revisor independente confronta fontes, componente, janela, N/D e cobertura, inclusive unidades sem cálculo. Só depois ampliar os IDs/janelas adotados.

**Interfaces/saídas:** conservar campos atuais `metric`, `horizon`, `status`, `value_fraction`, `numerator_fraction`, `denominator_fraction`, `flags`, `components`, `limits`; novos resultados em pacote próprio. A CLI atual possui `calculate-complements` com baseline/pin/output/metrics/datasets/periods: adaptar a allowlist na mesma operação, sem presumir que os novosIDs já sejam aceitos. Confirmar `--help` e schema antes de criar configuração.

## Fatia2 — renda e custos mais representativos

**Files:** primeiro somente nota de conciliação nova em `docs/engineering/`, inventário privado e fontes pinadas. Se fórmula for adotada, os mesmos arquivos/testes daFatia1; não reservar código antes de fechar o desenho. Integrador único para notas de método compartilhadas.

**Entradas:** DRE4/78215,RBIF;78213,provisão;78216/17,serviços/tarifas;78218/19,pessoal/admin;78221,participações;78222,outras receitas;78223,outras despesas;78225,resultado operacional. Contextos de78223 mudam definiçãoem201903. A presença conjunta foi medida; abrangência ainda não foi conciliada.

- [ ] Montar identidade literal daDRE por versão, separando receitas, resultados líquidos, despesas e provisões. Conferir grupo/definição e evitar somar agregado e filhos.
- [ ] Comparar abrangência deSvigente com participações/outras rendas emN2/N4/B2 e conglomerados. Diagnóstico de composição, não nova razão de eficiência adotada.
- [ ] Confrontar identidade com78225 no mesmo perímetro/janela, preservando residual. Não usar Resultado Operacional líquido como receita de um índice cujo numerador contém os mesmos custos.
- [ ] Entregar duas ou mais alternativas somente se conceitualmente defensáveis, mostrando contas excluídas, sinais, fonte e tradeoff. Nenhuma fórmula pronta deEwide é definida por este plano.
- [ ] Revisão independente da reconciliação; João escolhe eventual denominação/abrangência. Se a abertura local for insuficiente, declarar precisamente o componente e a fonte necessários.
- [ ] Após adoção, escrever teste de dupla contagem com agregado/filhos, renda negativa e provisão revertida; pilotoN2/N4/umB1comparável,201812/201903/202412; revisão antes da expansão.

**Aceite:** definição da renda e custo, identidade/residual por versão, representatividade/quantas/quais unidades, comparação comE2-B/RS/E3 sem promover a variante mais favorável. Fórmulas diferentes ficam em séries separadas.

## Fatia3 — carteira, perdas e rendimento de arrendamento

**Files:** nota nova de conciliação na engenharia; código/testes atuais daFatia1 somente após adoção. InputsAtivo2/78194,78195,78196,78197,78198 eDRE4/78204,78211; catálogo completo autenticado para todas as rubricas, inclusive78196 a incluir no diagnóstico específico. O conjunto178 contém seis componentes principais; não presume que cobriu todas as identidades.

- [ ] Separar arrendamento a receber, imobilizado, rendas a apropriar, provisão e saldo líquido. Conferir composição literal e variações antes de chamar uma conta de carteira bruta.
- [ ] Conferir quais ativos produzem78204 e a função de78211; decidir se rendimento é bruto ou resultado líquido e qual denominador econômico corresponde.
- [ ] AbrirN1porSegmentoTb e composição, com carteira positiva/zero/negativa; outrasTcb com leasing permanecem no diagnóstico, sem exclusão por rótulo.
- [ ] Documentar pergunta equivalente à proteção/custo/rendimento de crédito, mas sem imporCR78191ou somarCR+leasing por conveniência. Fechar fórmula somente depois da conciliação.
- [ ] Revisão independente e escolha metodológica; depois testes de sinais, provisão/saldo líquido, ajuste de rendas e dupla contagem. Piloto de uma data de cada definição mais202412; média/TTM somente com carteira e fluxos compatíveis.

**Aceite:** carteira/renda/provisão com mesmo alcance; conta a conta, identidade e residual; zero/nulo/negativo/histórico explícitos. Se os componentes atuais bastarem, implementação seletiva simples no motor; caso contrário, lacuna de dados identificada sem inventarproxy.

## Fatia4 — específicos que a base agregada ainda não demonstra

Estas são tarefas de pesquisa delimitada, não implementações prontas nem pedidos de coleta automática.

| Recorte | Inspeção local primeiro | O que falta para fórmula/implementação |
|---|---|---|
| B3S/B3C | AIL78189/Ativo2, depósitos interfinanceiros78284/Passivo3, subtipo/regime | Distinguir centralizado, livre/vinculado, contrapartes e obrigações de suporte; não adotar AIL/depósitos interfinanceiros como índice improvisado. |
| B4/N1-fomento e demais financiadores | LFquatroparcelas, notas de restrição/definição | Prazo/cronograma de recursos/desembolsos, fontes institucionais e horizonte. LFnão individualizaFATnem certifica estabilidade. |
| N2 | OutrasObrigações78297 e contas de margem/garantias que o catálogo efetivamente mostre | Identificar obrigações de clientes, ativos elegíveis/livres e prazo; não dividir por um agregado heterogêneo pelo nome. |
| N4 | Modalidade/regime datados, contas já admitidas e segregação descrita nas fontes | Obrigação de usuários e recursos elegíveis correspondentes; não substituir conta de pagamento porDVouCP/PR. Fórmula final de salvaguarda depende desses conceitos. |
| Crédito relevante | Relatórios e eventuais aberturas já admitidas, preservando escopo | NPLcomcritério datado e carteira/provisão correspondentes. NPL/CRbruto eprovisão/NPL são conceitosFMI; quatro relatórios atuais não os operacionalizam. |
| Capital prudencial | PR79649,CP79645,RWA79665, regime/S5 e datas | Mínimos/adicionais por unidade/período parafolga. Não impor8/11/13%uniformes ou transportarCPdoFinanceiro. |
| Liquidez/juros | Rubricas existentes e conceitos de restrição/sensibilidade | HQLA/saídas30dias, maturidade ou reprecificação. L2/LA não sãoLCR; crédito/depósitos não éNSFR. Definir aplicabilidade antes de fonte. |
| Benefício/mandato/volume | Produtos/objetivos efetivamente admitidos | Condições ao cooperado, adicionalidade, transações e custos correspondentes. Sem dado de produto, não inventar eficiência técnica. |
| DemaisAssaf | 78201permanente ajustado;78209captação;78298exigível e78299antes202212, conforme contexto | Imobilização/ANC/custo de captação/juros passivos exigem de-para; dividendos,Ke e sensibilidade exigem fonte/método adicionais. Capitalgiro é moeda, leveragevezes, VEA/MVA moeda. |

**Aceite de cada pesquisa:** ficha com fonte/versão/páginas, pergunta, fórmula quando defensável, alcance, janela/perímetro, tratamento de ausências e campos encontrados/faltantes; decisão entre conciliação local ou fonte adicional. Pesquisa prepara a escolha na3; nova coleta só em contrato próprio.

## Fatia5 — composição, estatística e entrega após adoção

- [ ] Autenticar baseline, executar somenteIDs/períodos liberados em destino novo, guardar recibo e preservar hashes/assinaturas anteriores.
- [ ] Revisar um lote completo antes da ampliação; piloto não autoriza declarar cobertura histórica inteira. Históricos de2019/Caixa/IPs usam apenas pontes aceitas para cada componente, sem extensão por analogia.
- [ ] Compor valores persistidos usando a operação existente `compose-analysis`, sem chamar o avaliador das20métricas anteriores; confirmar quantas/quais contribuições mudam.
- [ ] Produzir agregadosΣN/ΣD, medianas/IQR, contagens e estoques próprios porTcb/coorte/período; sinalizar denominadornegativo e cobertura conhecida. Conservar série do sistema e demais coortes, com desconhecidos.
- [ ] Coordenar a aplicação do [protocolo estatístico](../../engineering/statistical-treatment-protocol-20261018.md) e resultados175aceitos às novas métricas: integridade, influência, composição e unidades comuns são diagnósticos; não adotar testes inferenciais, cortes ouwinsorização neste plano.
- [ ] Revisor confere domínio, novas frações, conjuntos de cobertura, preservação e inventário completo doSHA. Só então PR/checks pertinentes/integração/CIpós-merge e atualização da mesmaIssue/mapa2.
- [ ] Publicação de novo explorador e promoção deponteiro, se incluídas no contrato futuro, somente após aceite de dados/artefato; usuários/tarefas mantêm pins anteriores até migração explícita.

## Entrega documental178 e verificações

Allowlist desta entrega: nota178, este plano, onze paresSVG/PNG `docs/agents/assets/tcb-indicators-*-20261018` e um linkREADME. Preparação/diagnóstico são privados e descartáveis. Não altera código, dados aceitos, classificações, fórmulas, explorador, ponteiro, estatística175 ou docs de outras frentes.

Checks desta fatia documental: UTF8, destinos locais/âncoras novas, XML/PNG,LaTeXrenderizado, legibilidade/cortes/geometria/IDs, inventário/allowlist e hashes de entrada, revisão independente porfatias eSHAfinal. Suíte de software não é pertinente a texto/imagens; será pertinente à implementação futura. Não criar testes que apenas repitam a prosa.

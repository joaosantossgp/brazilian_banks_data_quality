# Atualização analítica IF.data — plano de implementação

> **For agentic workers:** executar por fatias com `executing-plans` ou `subagent-driven-development`, usando revisão independente antes de ampliar cada resultado.

**Goal:** atualizar universo, indicadores e explorador, preservando cálculos aceitos e adequação contábil por Tcb.

**Architecture:** manter o motor temporal exato e o módulo responsável pelo universo. Reutilizar entradas admitidas, componentes, consultas em lote, Writer e agregação. Destinos novos para saídas; nenhuma reconstrução global por conveniência.

**Tech Stack:** Python local, DuckDB/Parquet e Fraction/Decimal existentes; HTML de exploração com dados persistidos.

**Spec:** [contrato da Issue 152](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/152), pesquisas 142/143/146 e atlas 148. Aprovação humana em 17/10: universo55/32/24, ponte Caixa como continuidade do perímetro observado e sete complementos. Não adotar silenciosamente novos indicadores específicos ainda candidatos.

## Restrições e composição

- Financeiro principal, Individual e Prudencial separados; núcleo 2010–2024. Sem nova coleta financeira, dependência ou servidor.
- Reutilizar W `monograph-docs`, HEAD `087700ccafa81ad96c963df62b633fb317d4ca21` mais correções locais aceitas. Snapshot prévio `.scratch/analytical-update-152-baseline/` é a referência do delta desta entrega, não só HEAD antigo.
- Principal e arquivos compartilhados da 150 são somente leitura. Sem rebase/reset/transferência global dos deltas. Atualização de referências compartilhadas depende de handoff nominal.
- Precisão nativa e estados preservados. Cálculos novos seletivos; dez atuais preservados onde nada mudou. Atividade fora dos filtros, SrAnalitico separado de Sr.
- Tcb guia a escolha, não constitui sozinho prova de atividade, licença ou regime. Não impor todos os indicadores a todos os modelos.

## A — Caixa: código e lote, revisão em duas fronteiras

Files: modificar `bank_quality/ifdata_universe_analysis.py`, teste adjacente `tests/test_ifdata_selective_analysis.py`; CLI existente `scripts/analyze-ifdata.py` após validação da API. Evidência em `docs/engineering/ifdata-analytical-update-20261017.md`. Nenhum perfil/módulo novo.

- [x] Testar primeiro helper `bridge_caixa_transition`: apenas Financeiro/C0051626, R1/R2/TTM e quatro alvos202109/12/202203/06; fonte anterior00360305, datada, nativa, finita e com mesmo contexto econômico; preservar source code e bindings.
- [x] Testar recusa de período/unidade/perspectiva errados, cadastro ausente/conflitante, mudança de líder, contexto não reconhecido, ambiguidades/null; nunca superar guarda com simples nome igual.
- [x] Implementar helper com inputs nativos e cópia analítica marcada de continuidade/perímetro observado, conservando observações originais. O identificador lógico comum usado na matemática não transforma o input em dado nativo do conglomerado.
- [x] Implementar `recalculate_caixa_transition` para consultar uma vez as partes finitas e retornar os oito resultados em pacote novo, sem alterar baseline. Não agregar apenas a Caixa como se fosse o sistema; recomposição com todas as contribuições ocorre em F.
- [x] Oráculo independente para fixtures temporais de fluxo semestral/estoques ponderados; conferir ausência de mudança nos caminhos seletivos2019. Revisão independente antes do lote real.
- [x] Rodar lote novo; conferir oito resultados, 36 referências originalmente ausentes, origens/fontes/flags e recorte imutável. Revisão do lote antes de compor no explorador.

## B — Universo e pertencimento

- [x] Transformar lista55 em identidades nominais, manter32 associações/24 códigos apenas no corte2024 e23 semprincipal. Validar história por operadora/evento/cadastro, não por nome; sem projetar controle Nacional/BTG ou holdings ao passado.
- [x] Conferir Cielo/BB/Bradesco e demais sobreposições; deduplicação nativa não prova eliminação econômica. Registrar o tratamento antes de chamar o agregado de consolidado.
- [x] Reaproveitar valores unitários e recompor coortes/companhias/cobertura. Delimitar implementação e allowlist da etapa na152 antes da escrita; conferir casos Daycoval/PAN/DM/BRPartners/Oliveira e datas de controle.

## C — Adequação por Tcb

- [x] Auditar pesquisa143/atlas148: ficha por Tcb/dimensão com pergunta, indicador comum/adaptado/específico necessário, fonte/localizador, variáveis, janela e limites.
- [x] Completar apenas lacunas relevantes de negócio/contabilidade com pesquisa primária e Assaf; não repetir bibliografia toda. Diferenciar ausência de variável de indicador não aplicável. Alcance: auditoria dirigida, sem alegar seleção específica exaustiva.
- [x] Entregar `docs/engineering/ifdata-tcb-indicator-adequacy-20261017.md`, com revisão independente. Novas adaptações além dos sete aprovados permanecem propostas até escolha metodológica.

## D/E — Complementos aprovados

- [x] D: LA/LC/LF, primeiro recorte202412 com BNDES/IP/cooperativa/unknown; identidade de captações e rubricas irmãs, zero/null/negativos. Oráculo e revisão, depois60trimestres.
- [x] E: RS/E3/R4/R5, trimestres reais e TTM/médias de estoque vigentes, fronteira2019 e sinais. Ampliar somente após revisão de janela completa. Reutilizar cálculo por componentes em lote; nenhum fullbuild dos dez anteriores.
- [x] Antes da escrita, registrar na152 os paths nominais necessários de fórmulas/contextos/testes e comprovar preservação do perfil congelado. Não criar motor concorrente.

## F/G — Composição, cobertura e explorador

- [x] Compor cálculos preservados + correções aceitas + novos, mantendo todos os atributos/perímetros. Agregar ΣN/ΣD por interseção própria; preservar distribuições, falta nominal e representaçãoAT/crédito/PL conhecidos/desconhecidos.
- [x] Conferir regressão econômica dos valores que não mudaram, reconciliação de coortes e fontes; preparar tabelas para estatística descritiva. Inferência/modelos/índice único não são adotados automaticamente.
- [x] Gerar explorador de saídas persistidas com universo novo, indicadores e complementos, segmentações e avisos de adequação; verificar payload e render desktop. Não exigir testes de celular.
- [x] Revisão independente da composição e encerramento por requisitos, sem confundir resultado local/revisado/publicado. Atualizar152/2/3, preservandoProject3. Não concluir Goal sem todos os requisitos e limites verificados.


## Clarificação de João em 17/10 — cruzamentos no explorador

Este recorte amplia o aceite F/G, conforme [registro na152](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/152#issuecomment-6240978178). Financeiro permanece principal; Individual e Prudencial complementares. A comparação analítica usa as32 associações admitidas, correspondentes a24 unidades financeiras em2024; as55 identidades e23 não admitidas ficam no diagnóstico nominal. A referência2024 e os vínculos datados não certificam população dinâmica de listagem ao longo de todo o histórico.

- [x] Configurar explicitamente `analytical_company_scope=admitted_associations_2024`; company_coverage conserva55 com flag de participação, faltas nominais dos agregados restritas às32.
- [x] Persistir `joint_cells` somente das tuplas observadas Tcb/SegmentoTb/Tc/Td/Sr/SrAnalitico, nas três coortes disjuntas; uma contribuição por célula, sem produto cartesiano. Preservar N/D, distribuição elegível completa, união nominal e estoques conhecidos/desconhecidos/negativos.
- [x] Filtros opcionais AND Tcb, SegmentoTb, Tc, Td e Sr, com escolha Sr original/analítico. Grupos OR explícitos B1+B2, B3S+B3C e S1+S2 são atalhos, sem reinterpretar categorias genéricas históricas.
- [x] Provar sistema/B1/S1, seleção32/N1/controle público, múltiplos campos, categorias desconhecidas, filtros vazios e denominadores locais cancelados, comparando com redução direta. Reconciliar sem filtros com o agregado completo e manter indicadores unitários intactos.
- [x] Mostrar totais próprios conhecidos de AT/crédito/PL, unidades/companhias, participação da seleção nesses estoques, mediana/quartis e ΣN/ΣD elegíveis. Confirmar unidade monetária: ODataSaldo emR$, escala1, conforme especificação oficial documentada no piloto11/10; não transplantar unidadeR$mil do portal.
- [x] Gerar HTML compacto de células conjuntas, recomposição racional BigInt e quantisType2, com payload/abertura e desktop conferidos. Não apresentar fixture sintética como resultado real.


**Gate final G:** exportação e QA integral de dados/kernel PASS; em 17/10/2026 João confirmou no chat a abertura do explorador e o funcionamento dos filtros. Verificação visual humana registrada; entrega local concluída. Publicação e integração Git não realizadas.

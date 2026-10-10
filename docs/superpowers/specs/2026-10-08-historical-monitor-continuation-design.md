# Monitor histórico e continuação autenticada da autoridade

> **Atualização de 2026-10-10:** João escolheu substituição operacional explícita e primeiro lote útil, conforme o [replanejamento](../../engineering/historical-route-reassessment-20261010.md#rota-escolhida-e-plano-de-execução). Este desenho de overlay deixa de ser a rota de execução de F1-01. Preservam-se evidência histórica e componentes úteis revisados; não ampliar Worker4 nem interpretar esta spec como obrigação de terminar uma segunda máquina de execução.

Proposta técnica da [Issue 59](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/59), base `ca63ee9674f58f9a80221af721fe6ebfc00025d3`. Complementa o [plano de aquisição](../plans/2026-10-05-financial-historical-acquisition-remaining.md); não substitui sua política finita nem os contratos de dados. A revisão deste desenho precede implementação e retomada.

## Resultado e evidência

O resultado continua sendo adquirir as 55 referências restantes, em 16 janelas, com Resumo/Ativo/Passivo/DRE nativos completos, e entregar fontes autenticadas à Issue 60. A correção deve permitir a execução diante de transições breves de processos e conservar uma autoridade interrompida quando o software precisa evoluir. Nenhum saldo é renovado; desconhecido continua desconhecido.

O representante F1-01 parou em 8,071s: `_ProcessObservationPending: New process candidate lacks a retained identity`. O monitor público trata essa observação como erro imediato. A janela tem batch sequence1, uma fase metadata201003 pendente e halt `phase_outcome_unproven`; os quatro membros têm sequence0, sem reservas ou gastos registrados. A sessão contém receipt inicial, sem checkpoint/terminal. Não há fonte nova aceita. Isso não identifica o PID/ator do evento original nem prova extinção apenas pela ausência de terminal.

Gates anteriores, no mesmo HEAD: Windows r5 634 PASS/duas exclusões de privilégio nominadas; compat54/202403 PASS; read11 final em cadeia explícita, 1.088 arquivos protegidos/16 exemplos Decimal, auditoria independente APP; CI pós-merge SUCCESS. São evidências preservadas, não aprovação antecipada deste novo comportamento.

Âncoras privadas, sem conteúdo publicado:

- Bundle F1-01 `b29a3aa30888be6130e851ac475acbc7bd6cf3a464709089fe9e72b86cce7c3e`; bootstrap `77944b950fba2bc18eb3eb9a8bbed38512eee55969ead915f0f4398137d00f9c`.
- Snapshot dos 24 arquivos da interrupção `e409e42c4e1dc70e8eec65d0f5242c0a1ea4abb3602c33ab5446c48b84aef5d7`.
- Manifest de seis imagens físicas anteriores, inertes e somente leitura: `3d248e8c1e4ab4f2a9666ee62ea945e4448c7606997a237774c8d11095b8cc57`. Não importar/executar essas imagens.

## Fatia A: monitor

Responsável: `bank_quality/windows_acquisition.py`, sem modificar containment, permissões, runtime ou identidade do coordenador.

Somente `_ProcessObservationPending` abre uma janela contínua máxima de 250ms, com nova observação a cada 50ms. O relógio é monotônico. Conferir duração antes/depois das observações e antes de resolver a janela; uma amostra válida tardia também falha. Erros desconhecidos, erro de recursos da máquina, margem esgotada ou janela expirada cancelam. Não transformar `OSError87` em pending neste lote.

Durante pending, medir RAM/commit/disco frescos e conferir reservas em voo, incluindo disco reservado, com as mesmas margens. Não atribuir zero a RSS/private, reaproveitar amostra antiga ou incrementar contador de amostra completa. Nenhum novo worker pode ser liberado com medição pendente: a chamada de preflight que antecede sua retomada exige resolução completa. Workers já contidos conservam seus deadlines e reservas; nenhum refund.

Uma observação completa resolve pending e atualiza picos **amostrados**. Registrar motivo, início/duração, número de observações, recursos da máquina, reservas e resolução/expiração. Serializar a observação e seu estado entre thread de monitor e chamadas síncronas, sem segurar o lock de reservas durante esperas nem criar deadlock. Pending no encerramento impede aceite/expansão; erro terminal nunca é descartado porque o child terminou.

O schema fechado da medição original do representante precisa versão explícita para esses campos e seu significado. Leitores antigos continuam reconhecendo sua versão própria; não acrescentar silenciosamente campos à v1. A fase ainda exige receipt/checkpoint nativos e prova de extinção existente. Um teste passando em sampler sintético não certifica o representante real.

## Fatia B: classificação e continuação

O executor v2 deve continuar rejeitando HEAD/arquivos/runtime diferentes dos seis pins originais. Nunca editar bundle, jobs, bootstrap ou evidência antiga para fazê-los corresponder ao novo código. O recovery atual não remove halt e não é usado como bypass.

Introduzir um contrato explícito de continuação **da mesma autoridade**, não outro bootstrap ou outra janela. A continuação referencia hashes externos de bundle/bootstrap/binding originais, snapshot integral da interrupção, prefixos dos journals e heads, halt, receipts, seis pins anteriores e novos revisados. Conserva escopo, membros, destino fechado, política, despesas e saldo. Uma identidade de execução corrente pertence à continuação; os pins antigos permanecem proveniência e não capacidade de execução.

Antes de implementar, fechar o schema e as transições de autoridade/batch/worker/export no plano. É proibido reutilizar a rota antiga com um objeto que apenas troca `code_pins` em memória. Transporte a worker requer versão própria que autentique a continuação e sua causalidade até o binding original. Handoff de fontes também distingue original e continuação; adoção no composer/pipeline é da Issue 60, sem retroatividade à 57.

O único caso de classificação inicial deste lote é `aborted_before_authorized_attempt`, sujeito a prova conjunta:

1. Replay completo de bootstrap/journals/heads íntegros: fase inicia uma vez; autoridades dos membros sem reserva, identidade de worker, fonte, conclusão ou despesa; receipt inicial exatamente coerente com essa sequência, e ausência de artefato de lançamento dentro da sessão.
2. Imagens anteriores autenticadas demonstram que toda criação/retomada de worker HTTP depende de reserva durável anterior, e GET só pode acontecer no worker autenticado. Verificação é de dados/código, sem executar imagens antigas. Falta de reserva sem esse contrato não prova ausência de efeito.
3. Reaquisição exclusiva dos claims originais; nenhuma reserva pendente. Extinção aplicável exige identidade nativa autenticada quando houve lançamento. Se a prova classifica ausência de lançamento autorizado, explicitar essa categoria; nunca afirmar extinção de um PID desconhecido. Qualquer evidência de lançamento sem identidade/prova conserva outcome unproven.
4. A falha antiga permanece registrada. Novo evento fechado classifica a fase abortada, habilitando outra sessão metadata do mesmo membro, sem contar como fonte/metadata completo, refund, reset de budget ou eliminação do halt histórico.

Apenas um sucessor ativo por predecessor e scope, com claim atômico. Preparação offline pode produzir candidato não executável em destino novo; ativação faz CAS contra os hashes congelados e publica uma continuação encadeada. Seus journals/heads novos referenciam a sequência/hash anteriores e não contêm bootstrap de saldo. Mudança no predecessor, classificação duplicada, sucessores concorrentes, rollback/fork e continuação parcial são rejeitados ou ficam sem capacidade de execução.

Gastos originais sempre entram no estado efetivo, mesmo que algum deles não seja reembolsável. Este recorte não recupera fases com reserva, GET possível, três falhas, guard consecutivo, erro de persistência/containment ou qualquer outro halt. Essas situações mantêm o contrato conservador anterior.

## Fronteiras e aceite

Sem pasta raiz, dependência, CI/proteção, segurança, runtime ou coleta alternativa. Spec/plano ficam nos destinos canônicos existentes; dados/evidências/continuações são privados sob `.scratch/` ou `data/runs/`, com destinos exclusivos e responsabilidade declarada antes da escrita. Headers, corpos, chave e pacote decriptado nunca entram no GitHub.

Testes parciais e review por fatia precedem composição: nascimento/resolução dentro do limite, resolução tardia, pending persistente/terminal, erro desconhecido, margens/deadlines/reservas, concorrência e contadores; depois classificação/adversários, fork/rollback, pins, gasto preservado, sessão nova sem repetir GET, transporte/receipt/checkpoint/export. Finalizar somente com revisão do SHA final, checks proporcionais/Windows, integração e preflight atuais.

A retomada real usa a mesma F1-01 e para no representante medido. Review de fontes/proveniência/recursos/extinção antecede remaining e primeiro handoff60. Catálogo inicial61 não bloqueia aquisição; pesquisa16 tem ownership próprio e pode avançar. Conteúdo/método da monografia, complementos62/63 e aceite final64 continuam nas autoridades existentes.

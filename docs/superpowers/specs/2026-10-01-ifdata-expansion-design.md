# Expansão limitada: desenho autorizado e executado

## Problem Statement

O piloto produziu dados e reprodução confiáveis, mas a passagem para uma amostra de bancos de capital aberto ainda exige separar disponibilidade anunciada, cadastro observado, semântica temporal e identidade entre emissor e unidade IF.data. Escalar sem esses controles transformaria um inventário amplo em uma população histórica presumida.

## Solution

Fechar a auditoria de cobertura e janelas dos dois trimestres existentes, preparar três casos de identidade temporal e executar uma única extensão financeira em **202312, instituições individuais, Resumo**. Produzir inventários comparativos dos três trimestres, mantendo o universo IF.data amplo como comparação técnica opcional. A amostra principal de capital aberto permanece uma seleção temporal de emissores com vínculos documentados; a unidade IF.data representativa depende de decisão posterior.

João autorizou a execução da etapa, incluindo dezembro/2023, registrada no fechamento de 2026-10-02. A execução local já foi validada; este fechamento documental não autoriza nova coleta ou escala. Unidade, janela final e elegibilidade de capital aberto permanecem decisões humanas. Ver resultado em `reports/expansion-20261001.md` e fechamento em `docs/engineering/expansion-execution.md`.

## User Stories

1. Como pesquisador, distingo os 106 trimestres anunciados dos arquivos efetivamente adquiridos.
2. Como pesquisador, verifico o cadastro recuperado contra os códigos do relatório sem chamá-lo universo histórico completo.
3. Como pesquisador, vejo a janela acumulada dos fluxos, a data dos estoques e a versão de cada observação.
4. Como pesquisador, vejo quais marcadores são originais, quais são exibição do portal e quais interpretações continuam desconhecidas.
5. Como pesquisador, examino banco individual, emissor/holding e conglomerado como identidades separadas, sem vínculo presumido.
6. Como pesquisador, adiciono um trimestre sob orçamento e escopo explícitos, sem disparar uma série histórica.
7. Como pesquisador, reproduzo os inventários a partir de corpos imutáveis e identifico revisões sem sobrescrever o piloto.
8. Como pesquisador, mantenho capital aberto como foco e identifico o universo amplo como comparação opcional.

## Implementation Decisions

- Reutilizar aquisição imutável, aceitação validada de exportações e inventário existentes. Generalizar apenas o necessário para o lote de um trimestre, com allowlist explícita de 201012, 202312 e 202412; nenhuma opção “todos”. O piloto original deve continuar reproduzível.
- Fontes financeiras: somente BCB IF.data. CVM/B3: metadados históricos/identidade, sem demonstrações financeiras e sem acesso ao projeto CVM separado.
- Execução autorizada e realizada: uma aquisição de 202312, nível individual 1006 no portal/3 no OData, Resumo. Não incluir 2025, outros relatórios ou demais níveis no conjunto aceito. Shards compartilhados carregados pela fonte são evidência bruta, não ampliação automática de observações.
- Usar catálogo oficial arquivado com hash e data; período/relatório/caminho devem ser descobertos por metadados. Mudança de coluna/nota versus estrutura prevista interrompe aceitação automática. Preservar nomes/IDs originais e espaço final, quando houver.
- Descrever cobertura por fonte/denominador: cadastro REST adquirido, correspondência com relatório, cadastro OData disponível ou indisponível e universo histórico/capital aberto não estabelecido.
- Janelas de fluxo: janeiro–março, janeiro–junho, julho–setembro, julho–dezembro. Não transformar publicação trimestral em fluxos trimestrais, derivar Q4 automaticamente ou unir versões incompatíveis. Estoques e fluxos permanecem distinguíveis.
- Reter NA, NI, branco, null, zero, ausência de chave direta, variável fora da estrutura e indisponibilidade de fonte como estados diferentes. Campo calculado/cadastral sem chave direta não vira dado faltante.
- Casos de Banco do Brasil, Bradesco e Itaú Unibanco Holding: evidências atuais/datas de eventos separadas de estados históricos. Relações emissores–instituições/conglomerados precisam identidade legal, intervalo e fonte primária; desconhecido é resultado aceitável.
- Limites aplicados ao lote 202312: reserva 150 MiB de disco, teto 80 MiB bruto por tentativa, 480 s por execução e máximo duas tentativas. Estimativa de 25–45 MB para um trimestre semelhante a 2024 não é medição de 202312. Parar em vez de ampliar automaticamente.
- A janela definitiva e o nível individual/consolidado continuam decisões humanas. Nenhum ajuste ao cronograma acadêmico.

## Testing Decisions

O principal seam continua **corpos oficiais arquivados → coleção aceita → inventário**. Fixtures devem mostrar cadastro↔relatório com divergências e duplicatas, trimestres rejeitados fora da allowlist, esquema alterado, diferenças entre janela de estoque/fluxo, falta de prova temporal e estouro de orçamento. No lote real, verificar cada hash, cobertura de códigos e definição, explicitamente desconhecidos e replay idêntico. Não escrever testes que espelhem a implementação sem validar comportamento.

## Out of Scope

histórico completo; 2025+; Ativo/Passivo/DRE novos; inferência automática de listagem histórica ou conglomerados; amostra definida pelos sobreviventes atuais; extração financeira CVM/B3; textos acadêmicos; cronograma/calendário; instalação global; publicação/commit/push/PR/deploy; alteração de outro computador/projeto.

## Further Notes

Fontes: descoberta estruturada oficial e pesquisa primária registradas localmente. O Project privado existente continua canônico; as quatro tarefas locais são rascunhos para a conversa principal organizar, sem duplicação/publicação por esta tarefa. Cobertura, dossiê e lote 202312 foram entregues. Antes de escala, decidir unidade/janela/elegibilidade e documentar os vínculos necessários; nenhuma escolha foi feita pelo agente.

## Baseline de estrutura verificado

Relatório, notas, colunas e vintage 202312 conferidos contra o catálogo previamente arquivado. As 19 definições selecionadas do info202312 foram verificadas contra seu corpo HTTP e congeladas após a primeira aquisição; não se alega pinagem desse info antes do download. O perfil está em `bank_quality/schema-202312.json`. Mudanças em nomes, definições, unidades, notas ou vintage rejeitam aceitação automática. Coleta202312 exige modo portal explícito com limites; OData não foi tentado nesse trimestre.

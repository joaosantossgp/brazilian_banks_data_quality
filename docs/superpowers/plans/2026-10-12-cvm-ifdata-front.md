# Identidade CVM–IF.data e método por tipo — plano de execução

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. A execução documental/revisão usa pesquisadores delegados com ownership distinto; software só entra após contrato técnico revisado.

**Goal:** entregar inventário/contrato de metadados CVM 2010–2024, matriz metodológica fundamentada por tipo e prova delimitada de identidade, conforme [Issue102](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/102) e [nota de direção](../../engineering/cvm-ifdata-identity-methodology-plan-20261012.md).

**Architecture:** reutilizar metadados/proveniência/identidade e entradas IF.data existentes. Pesquisa em `docs/engineering/`, plano em destino existente, dados novos ignorados só após contrato A1; sem alterar checkout concorrente ou criar tracker paralelo.

**Tech Stack:** documentação Markdown, fontes primárias web/PDF, shell/GitHubCLI e Python local já disponível para verificações. Não instalar dependências/runtime. Implementação futura terá interfaces e testes concretos registrados após inventário dos esquemas, sem adivinhar contratos de arquivos.

## Restrições globais

- IF.data é a fonte financeira principal; CVM/B3 nesta frente fornecem metadados. Não coletar balanços CVM para substituir IF.data.
- Janela principal2010–2024, complemento2025–2026 separado. Amostra, unidade e método finais permanecem #3.
- Revisão independente de cada fatia antes da expansão. Contratos/allowlists são finitos e registrados na Issue real.
- Base inicial `6535862eed9bce9cfaaaa29b9064cfc8045a5a65`, branch `codex/cvm-ifdata-front-20261012`, worktree gerenciada própria. Não editar o checkout da #95.
- Preservar fontes/dados aceitos e campos nativos. Unknown não é falso/zero. Nome/ticker/raiz não comprovam relação jurídica.
- Feynman obrigatória por pedido de João: `pdf-explore` efetivo; `/deepresearch` indisponível, usar fallback documental primário e registrar limites.
- Documentos novos reutilizam destinos canônicos; nenhuma alteração estrutural na fatia inicial.

## Fatia A1 — fontes CVM e contrato de aquisição

**Owner:** pesquisador `cvm_sources_a1`; integração Root. **Allowlist:** `docs/engineering/cvm-historical-sources-20261012.md`. Preparação privada `.scratch/cvm-front-20261012/a1/`. Sem datasets de companhias/código/commits pelo pesquisador.

- [x] Conferir Issue102, nota de direção, arquitetura e fontes oficiais CAD/FCA/FRE.
- [x] Localizar dicionários/esquemas, recursos por ano, versões, datas de entrega/referência/evento, registro/categoria/instrumentos e relações societárias.
- [x] Registrar fonte/localizador/consulta/limites; separar disponibilidade anunciada e observada, falha e vazio.
- [x] Propor contrato finito de aquisição metadata-only: URLs/seleção, destinos novos, limites de bytes/tempo, encoding/ZIP/CSV, chaves/revisões e checks. Não adquirir dados antes de revisão.
- [x] Root conferir links, integridade do inventário e completude do contrato; solicitar revisão independente do snapshot/hash. Corrigir findings materiais antes da aquisição.

**Saída:** contrato aceito ou lacunas concretas. Não prova elegibilidade/identidade por instituição.

## Fatia B1 — referências e método por tipo

**Owner:** pesquisador `institution_methods_b1`; integração Root. **Allowlist:** `docs/engineering/institution-type-indicator-methodology-20261012.md`. Preparação privada `.scratch/cvm-front-20261012/b1/`. Independente de A1.

- [x] Reusar pesquisa de amostra/componentes/piloto, com limites da consulta anterior explicitados.
- [x] Buscar literatura original e fontes FMI/BCB; ler métodos/fórmulas/amostras/limites relevantes, cruzando páginas com `pdf-explore`.
- [x] Produzir matriz de aplicabilidade por família: bancos, especialistas crédito, serviços/corretoras, pagamentos, holdings/diversificados.
- [x] Registrar fichas dos candidatos: conceito/fórmula/fonte, condições, janelas/médias, sinais, unidade/perímetro/regime, denominadores problemáticos e dados necessários; separar adaptação IF.data de prescrição da referência.
- [x] Fazer apenas triagem curta do complemento foraIFdata; documentar ganho/custo/lacunas, sem pipeline adicional.
- [x] Root conferir rastreabilidade e revisão independente do snapshot antes de ampliar conclusões.

**Saída:** matriz fundamentada e alternativas para #3; não adoção de método, classe definitiva ou cálculo.

## Fatia A2 — prova delimitada de identidade e metadados utilizáveis

**Owner:** Root. **Dependência:** A1 revisada. O contrato público da Issue102 será ampliado antes de qualquer aquisição de datasets/edição de código, com inventário exato dos paths e fontes, recursos medidos e checks. A aprovação para prosseguir nesta conversa cobre executar a frente; não elimina o gate técnico de fechar esse contrato com os esquemas reais.

- [ ] Após A1, registrar seleção finita e os destinos novos de bruto/derivado/curado, preservando existentes.
- [ ] Inspecionar `bank_quality/archive.py`, `bank_quality/metadata.py` e leitores de cadastro existentes; reutilizar transporte/validação em vez de criar caminho paralelo.
- [ ] Delimitar base de metadados e prova BB/Bradesco/Itaú, com datas explícitas e pontas completas, sem preencher CNPJ por prefixo.
- [ ] Para software necessário, escrever plano técnico concreto com assinaturas/fixtures/testes causais e allowlist antes da edição; TDD e revisão pertinentes.
- [ ] Capturar fontes com URL/parâmetros/status/headers/UTC/hash e limites; validar schema/ZIP/contagens/chaves/revisões. Falhas preservadas; não promover corpo incompleto a fonte aceita.
- [ ] Produzir relações comprovadas ou lacunas por caso/data, conferir cardinalidade e não duplicação; revisor independente compara fontes e resultados antes de expandir.

**Saída:** pacote de metadados verificável e prova delimitada, sem amostra/joins financeiros acadêmicos aprovados por implicação. Se fonte não provar relação, entregar desconhecido e motivo verificável.

## Síntese e integração

**Owner Root. Allowlist inicial adicional:** `docs/engineering/cvm-ifdata-identity-methodology-plan-20261012.md` e este plano.

- [ ] Atualizar nota de direção com resultados/links/decisões e limites, sem duplicar pesquisas.
- [ ] Conferir inventário completo, links locais, whitespace e fidelidade das afirmações; testes de software apenas quando houver código/dados cujo contrato exija.
- [ ] Registrar revisões parciais, hashes/comandos/saídas e estado real na Issue102; conferir composição e SHA final independentemente.
- [ ] Publicar PR após aceite, acompanhar checks, integrar no escopo autorizado e verificar CI pós-merge. Não transferir aprovação a delta não revisado.
- [ ] Atualizar fronteira na #2: A1/B1 compatíveis; #95 com ownership distinto; #3 bloqueia apenas escolhas/dependentes. Project permanece com Zec.
- [ ] Encerrar goal somente quando os recortes autorizados tiverem evidência entregue; se decisões humanas impedirem o restante, distinguir resultado da frente de dependentes sem alegar implementação completa apenas por plano.

Verificação documental mínima: `git diff --check`; conferir cada link relativo no diretório do documento; `git diff --name-status BASE HEAD` contra allowlist; hashes SHA256 dos documentos revisados. TDD/suíte não se aplicam às notas por si só. Estado de cada checkbox deve refletir evidência observada, não intenção.

## Contrato técnico A2 fechado após piloto

Registrado antes da implementação/expansão no [comentário102](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/102#issuecomment-6129455312). Allowlist adicional finita: `bank_quality/cvm_metadata.py`, `scripts/import-cvm-metadata.py`, `tests/test_cvm_metadata.py` (implementador); `docs/architecture.md` (Root). Sem dependências ou alteração do validador `metadata.py`. Aquisição Root e implementação offline têm arquivos separados. Revisão de código antes de build real; revisão piloto/replay antes de admissão final.

Interfaces: `build_cvm_metadata(index_path, expected_index_sha256, output)` e `verify_cvm_metadata(output, expected_manifest_sha256)`, CLI build/verify delegando ao módulo. Índice `cvm-identity-sources-v1` com entradas kind/year/url/manifest relativo/hash externo; autenticar índice, manifests, corpos e resposta, HTTP200/GET completo e URLs oficiais fechadas. Uma fonte CAD, anos FCA únicos2010–2024; destino exclusivo. Conter caminhos/symlinks. ZIP valida CRC e rejeita traversal/duplicação/encriptação/symlinks; limites64MiB expandido/arquivo,256MiB agregado.

Perfil fechado aos headers observados: CAD47 com projeção18campos sem contatos; FCA índice9/geral26/valmob18. Latin1 operacional somente sem bytes0x80–0x9F; divergência de encoding/schema interrompe, exige revisão de perfil. CSV semicolon estrito, campos strings preservando zero/vazio/multilinha/duplicatas; saída UTF8 textual. Chave física fonte+membro+ordinal. Datas mantidas, sem inferência de vigência.

Quatro tabelas consolidadas: cadastro_atual/documentos_fca/geral_fca/valores_mobiliarios_fca, com fonte/ano/hash/membro/ordinal. Manifest publicado por último, hashes/contagens/schemas/limites; quality.json conserva cardinalidades, duplicatas e conflitos. Join documental somente CNPJ completo+referência+versão+ID no mesmo ano; divergência CNPJ por ID gera conflito, jamais fallback. Pacote admite observações literais, não relações jurídicas; downstream deve isolar conflitos antes do uso relacional. Nenhum financeiro/indicador/amostra calculado.

Captura adicional somente13FCA2011–2023, reutilizando pilotoCAD/2010/2024, em raw/.../remaining;8MiB/corpo, sockettimeout30s, sequencial, sem redirect/retry, parar na falha, disco medido. Índice consolidado em raw/.../source-index.json. Destinos curated exclusivos cvm-identity-20261012-pilot, pilot-replay, cvm-identity-20261012 e replay; recibo runs/... conforme arquitetura.

TDD causal cobre pins/tamper/containment/destinoexistente, texto/multiplicidade, schema/C1, conflito sem joinID, replay determinístico e adulteração de saída. Fixtures sintéticas não provam fontes reais. Aceite final exige16fontes verificadas e relatório dos seis casos BB/Bradesco/Itaú201012/202412, inclusive unknown fundamentado.

Checkpoint de revisão: contraprova independente encontrou chave documental com ID vazio recebendo matched. A expansão para build real foi interrompida. A correção exige todos os componentes CNPJ/referência/versão/ID preenchidos antes de correspondência, preservando linhas incompletas com motivo e quarentena. Testar também referência/versão vazias e duplicação dessas chaves; revisão posterior deve confirmar o delta antes do piloto. Limite de campoCSV128KiB é explícito, sem alterar estado global do parser.

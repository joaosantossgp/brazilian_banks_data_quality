# Contrato de segurança do escopo de PR — proposta 2026-10-03

Frente: [Governança de workflow e escopo, Issue 17](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/17). O workflow e os owners estão na [matriz do tracker único](../agents/issue-tracker.md#etapas-skills-entregáveis-gates-e-owners). Este documento especifica o checker/handoff técnico; não guarda estado de Issues/Project.

**Preparação da publicação — 2026-10-03:** João autorizou reconciliar, revisar e publicar esta entrega por branch/PR e atualizar as mesmas Issues/Project. A branch `codex/governance-scope-observation` é dependente de `codex/offline-duckdb-parquet`; o diff próprio tem 21 paths, incluindo os cinco arquivos oficiais de triage e sua proveniência. Os conflitos documentais em AGENTS/README foram reconciliados preservando o contrato e código do conversor e o registro datado de autorização. O PR deve apontar para a branch do conversor até sua integração, sem misturar os 17 paths da Issue 15 no diff desta frente. Política sem tarefas/bindings e owner não atribuído continuam bootstrap: não há enforcement remoto nem validação deste PR pela política proposta. Revisão humana externa ao checker continua necessária antes de integrar o bootstrap. Estado de publicação/checks fica na Issue 17 e no PR real; testes locais e revisão de código não comprovam funcionamento de runner/coletor remoto.

## Resultado local e bootstrap

`scripts/check_pr_scope.py` executa offline em Python 3.12, biblioteca padrão, sem coleta financeira ou leitura/execução do código do PR. Usa somente política JSON e nomes/status dos arquivos. Começa em **observação, não required**: retorna falha quando necessário; observação permite avaliar diagnóstico sem proteção obrigatória, nunca ocultar erro como sucesso.

`.github/governance/scope-policy.json` é bootstrap sem tarefas/bindings: todo PR desconhecido falha. Integrador explicitamente não atribuído. Fixtures em `tests/fixtures/pr_scope/` são sintéticas, não contratos reais. O integrador revisa contratos e bootstrap separadamente; não copiar permissões das fixtures para produção.

## Fronteira de confiança

1. Validator, política, runner e versão vêm de commit imutável da base confiável, escolhido pelo responsável autorizado. Mudanças no head não são carregadas/importadas. Checkout do job não pode ser merge/head do PR; paths de política/validator fixos pelo runner, sem override do PR.
2. Coletor confiável obtém PR/base/head/branch e inventário completo diretamente do provedor ou objetos Git tratados apenas como dados. Nunca aceita política, inventário ou PR indicado em artefato do job do PR. Registra snapshot; relê identidade/metadados no fim e invalida se PR, base, head ou contagem mudarem. Branch real deve corresponder ao contrato; checker local não consulta branches/provedor.
3. Runner confere vínculo PR→tarefa na política da base. Labels, texto de Issue/PR e argumento escolhido pelo autor não criam vínculo. A projeção de tarefas é reserva de escopo/dependências aprovada; Issue/Project continuam autoridades de tarefa/estado.
4. Bootstrap e mudanças de política/checker/workflow são revisados pela **versão anterior confiável**, com allowlist explícita de integração e revisão independente. Nova política só vale em execução futura após integração autorizada; nunca valida o PR que a altera.
5. Checker não autentica origem dos arquivos locais, pessoa, aprovação ou permissão. Operador que fornece política adulterada altera a decisão. Testes demonstram decisão sob política fixa, não autenticidade do executor ou uso de skills. Check names também podem ser imitados; conferir origem/run/SHAs.

## Esquema e regras

Política v1: `schema_version`, `version`, `mode=observation`, `integrator`, `forbidden_paths`, `sensitive_paths`, `shared_paths`, `tasks`, `pr_bindings`. Tarefa: owner, role, area, state (`ready`, `blocked`, `done`), Issue/brief, branch, allowed/forbidden paths, dependencies. Uma role; area da projeção é a principal, labels podem informar outras áreas. Bindings usam PR real, nunca número de Issue por suposição.

Allowlist: path exato ou prefixo terminado em `/`, com limite de componente; glob não é aceito. Tarefas não `done` não têm reservas sobrepostas. Shared paths ficam só com integrador nomeado de role integration e também exigem allowlist. Done libera reserva para handoff. Dependências existentes, acíclicas e `done`. Revisão da projeção na base não sincroniza Project automaticamente.

Input v1: `schema_version`, `pr_number`, `policy_version`, `base_sha`, `head_sha`, `complete=true`, `changed_files`, `files`. Entrada: `filename`, status `added`/`modified`/`removed`/`renamed`; somente rename tem `previous_filename`, obrigatório. Collector adapta resposta oficial, descartando patch/conteúdo. SHAs completos, PR e versão são comparados com seleção independente do runner.

Ambos os lados do rename e todo delete são checados. Desconhecidos, forbidden, controles sem integração, conflito, dependência/estado aberto e schema/status/lista inválidos falham fechado. Rejeita absolutos, traversal, backslash, controles, glob, componentes vazios, Unicode fora de NFC, JSON com chave duplicada e paths duplicados/case collisions. Deny, controles e conflito de reservas usam casefold para preservar segurança entre Windows/Linux; a allowlist exige a caixa exata aprovada. Nomes são dados, nunca interpolados em shell. Código/diff fornecido não é executado.

Global forbidden prevalece inclusive para integrador. Controles exigem integrador **e** allowlist, sem exceção ilimitada. Relatórios/licenças específicos do conversor só entram com contrato explícito; bruto/skills upstream seguem protegidos. Partir do diff real revisado, nunca `bank_quality/**`. A integração preserva a semântica e os artefatos do conversor; nos documentos compartilhados, acrescenta apenas governança e estado datado. Não presume qual será seu PR. Governança é a Issue 17; conversor é [Issue 15](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/15), contrato 2025 [Issue 16](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/16), indicadores [Issue 14](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/14); o worker autorizado mantém o board.

## Execução local

Usar Python 3.12 existente, na raiz do **pacote candidato isolado**:

```powershell
python -B -m unittest discover -s tests -v
python -B scripts/check_pr_scope.py --policy tests/fixtures/pr_scope/policy.json --changes tests/fixtures/pr_scope/changes.json --base-sha 1111111111111111111111111111111111111111 --head-sha 2222222222222222222222222222222222222222 --pr 42
```

O segundo comando é sintético. Exit 0 = pass; 1 = falha de contrato/schema/regra; 2 = JSON ilegível/inválido. Resultado JSON registra versão, PR/base/head quando válidos, task/owner e erros. Nenhum modo converte falha em pass.

## Integração futura e limites

Não há workflow Actions novo neste patch. Adaptador remoto não foi implementado/executado. Observação local permite revisar comportamento antes de validar executor; nenhum check de PR instalado é alegado. Nenhuma proteção, ruleset, CODEOWNERS exigido, label remota, segredo, permissão ou Project/Issue foi alterado por este pacote.

A documentação de [eventos Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run) situa `workflow_run` na default branch e alerta sobre privilégios. Essa é opção de desenho ainda não validada: permissions mínimas só leitura, sem secrets do projeto, download/cache/artefatos do job do PR, checkout de head ou dependências/hooks/scripts do PR. Identidade/inventário vêm diretamente do provedor. Não usar `pull_request_target` para executar código PR com secrets. `pull_request` com YAML alterável no PR não basta para estabelecer confiança.

A [API de arquivos de PR](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files) pagina e limita a 3.000 arquivos. Coletor futuro percorre páginas, confere contagem com metadados independentes e estabilidade de SHAs. >3.000, truncamento, timeout, autorização ausente ou inconsistência resultam em falha/inconclusivo, nunca pass. `complete=true`/contagem coerente são declarações do coletor, não prova criptográfica: inventário falsificado que omite arquivos não é detectável pelo checker isolado.

Testes não validam API, paginação/evento Actions real, permissões, status remoto, stale approvals, autenticação de reviewer ou regras de merge. Checker avalia nomes/contrato, não conteúdo financeiro, modos Git/symlinks/submodules, validade acadêmica ou licenças. Revisão de conteúdo e CI existente continuam necessários. Ownership é contrato de coordenação, não ACL do filesystem.

Antes de integrar: responsável único reconcilia shared paths contra head final do conversor, escolhe reviewer real elegível, revisa bootstrap/contrato e valida coletor/runner em PRs seguros de observação (self-policy, rename/delete, inventário incompleto). Registra origem/run/base/head/resultados antes de afirmar observação remota instalada. Tornar required exige decisão futura específica.

[CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) exige pessoa/time real elegível com escrita; role/label não satisfaz. Autor não aprova próprio PR; ver [revisões de PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews). Reviewer/CODEOWNERS seguem decisão aberta; nenhum arquivo com identidades inventadas é proposto.

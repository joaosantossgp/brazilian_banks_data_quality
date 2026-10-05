# Contrato financeiro nativo 202403

Issue real: [55 — Admitir e consultar os quatro relatórios financeiros de 202403](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/55). Execução sob a autonomia técnica aprovada; publicação e integração exigem checks e revisão independente. O [mapa 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) mantém a cobertura e a próxima entrega. Este contrato não define amostra ou método da monografia.

## Entrada e seleção

Seleção nativa `202403/1005/[92,96,101,98]`: Resumo, Ativo, Passivo e DRE, todas as variáveis disponíveis. Fontes já adquiridas na [Issue 50](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/50); nenhum GET adicional nesta entrega. Job físico `43f775d20a4dd9cf686f975c2232a39b26a3f9afb23ff9732e920c5bb9296ed5`, canônico `b16a582e865f6de1f097820f67fa9b063b5be9fe5ddf0be8dc617415f864c4de`, bootstrap `026d372570fff21a53d3b59fbf9acf1a164adb377e810811965d80e3251a5a9c`.

O checkpoint A original tem SHA-256 `51993dc1e9e8a0edd7361b6f297566fbf5a53a0c1feb4bf90fca77a3f9c124f0`; B original `f30878c4e4cdcae135913351652a707bc0398bbde006f42a283fac8a2f009373`. Recibos históricos e journal corrente são autenticados sem restaurar counters, renovar saldo ou reescrever originais. Pending/failure, seleção incorreta, pin divergente ou origem incompleta impedem autoria/admissão.

## Ponte de autoria e perfil

Aquisição autentica catálogo no campo próprio, enquanto o compiler exige catálogo e portal como fontes explícitas. A ponte offline `compose_acquisition_handoffs` permanece no módulo responsável `bank_quality/financial_report_profiles.py`, aceita somente o anchor confiável 202403 e reutiliza a autenticação existente. Não duplica transporte/autoridade nem generaliza automaticamente outros períodos.

A ponte produz dois checkpoints novos e um envelope de evidência. A ligação original B→A e a ligação projetada B→A são verificadas separadamente; os bytes originais, contextos e referências C/D/N permanecem intactos. Catálogo e portal têm manifests/corpos e contextos próprios; o portal não é reclassificado como uma coleta 202403. Não estender as exceções legadas D/N de 202312.

Alternativas recusadas: editar checkpoints originais, tolerar fonte implícita/ausente ou instalar perfil arbitrário do caller. A composição explícita conserva os contratos de aquisição e autoria. Compiler/freeze não conservam campos extras do envelope: o integrador e a revisão independente confrontam seu hash externo, os checkpoints físicos e a proveniência original antes da instalação.

Perfil próprio no destino existente `bank_quality/financial-reports-profiles/202403.json`, instalado somente após revisão de árvores, definições, origens, annotations, cadastro e pins. Registry finito conserva seus 66 membros e todos os perfis anteriores; alterar somente `profile_path` e `profile_sha256` do membro 202403. Candidato, perfil instalado e cobertura aceita são estados distintos.

## Domínio, precisão e ausências

Preservar cadastro nativo de 32 colunas, grupos/folhas, tokens e todas as variáveis. Estoques e fluxos conservam as annotations/janelas nativas; nenhuma annualização, equivalência por nome ou join acadêmico. Unknown permanece explícito quando não houver prova de unidade, janela ou perímetro. Não inferir a população admitida pelo tamanho do shard completo.

Reader/adapter históricos existentes fazem a admissão e a projeção: grade autoritativa de 32 campos textuais, views por binding e Decimal exato. Largura até 38 usa DECIMAL; acima disso, contrato histórico v2 com `numeric_exact_text` explícito e accessor Python Decimal, conforme a [decisão e prova anteriores](financial-historical-admission-20261004.md#ajuste-de-representação-adotado-após-diagnóstico). Não arredondar, estreitar escala, usar DOUBLE, preencher ausência com zero ou criar UNION numérica global. A representação efetivamente necessária deve constar na evidência real.

## Destinos, workflow e aceite

Arquitetura existente preservada: código/teste de autoria; perfil/registry no pacote; contrato e ledger em `docs/engineering/`; [plano](../superpowers/plans/2026-10-05-financial-historical-admission-202403.md) em plans; README/arquitetura pelo integrador único. Sem nova raiz, camada, dependência, rename ou delete. Dados locais novos: `data/runs/financial-historical-admission-202403-20261005/`, `data/derived/financial-historical-202403-20261005/`, `data/curated/financial-historical-202403-20261005/`; replay com sufixo `-replay`, nunca sobrescrevendo uma entrega.

Workflow: desenho/plano → fixtures RED/GREEN → revisão da ponte → autoria real medida → revisão independente do perfil → instalação → admissão/Parquet/consulta/replay medidos → documentação/checks/revisão do SHA final → PR/CI/integração/CI pós-merge. Superpowers organiza essas etapas, TDD, debug quando necessário e verificação. Matt somente por invocação disponível; Context7 para necessidade concreta de documentação técnica; Feynman para pesquisa primária nova, caso necessária; diagram-design somente para novo visual pertinente, SVG/PNG.

Aceite: todas as variáveis e origens validadas, cobertura/ausências registradas, consulta e accessor exatos, replay de todos os payloads byte a byte e manifests comparados descontando somente timestamps e seus hashes derivados explicitamente autenticados. Recursos são medidos por máquina, uma etapa pesada por vez até provar capacidade conjunta. Revisão independente confere o inventário autorizado e arquivos protegidos. Resultados locais e integração remota têm provas distintas no [ledger](financial-historical-admission-202403-20261005.md). Done exige a cadeia completa; não comprova as outras 63 referências ou comparabilidade acadêmica.

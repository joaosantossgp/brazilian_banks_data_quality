# Admissão financeira offline de 202412 — execução 2026-10-03

Entrega da [Issue 25](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/25), após a pesquisa da [Issue 23](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/23). Autoridade: [contrato pesquisado](financial-snapshot-202412-contract-20261003.md), [arquitetura](../architecture.md) e [workflow](../agents/workflow.md). Base `143dc3ef517c5bfc0823fc40e7fc579e4f76394b`; código executado `a0862644448efb54a7025a5936a9320d816b220b`, com revisão independente prévia PASS. Documentação acrescentada após execução; revisão final, CI e integração são estados verificáveis na Issue/PR, sem inferir publicação pelo resultado local.

## Resultado observado

Admissão técnica do conjunto recuperado: financeiro 1005, Resumo 92, referência 202412, contrato `ifdata-financial-snapshot-202412-v1`. Nenhuma aquisição, filtro acadêmico, imputação, arredondamento ou Parquet financeiro. Cadastro completo preservado, inclusive TD vazio, segmento 42 e campos não documentados.

| Medida | Resultado |
|---|---:|
| Registros cadastrais / variáveis | 1.422 / 8 |
| Observações monetárias armazenadas | 8.490 |
| Quantidades cadastrais armazenadas | 2.844 |
| Total de observações / posições na grade | 11.334 / 11.376 |
| Posições monetárias sem entidade / sem informação | 30 / 12 |
| Entidades N1 compartilhadas / correspondências cadastrais literais | 4.087 / 1.417 |
| Lexemas, pointers, tipos fonte e Decimal confrontados com os corpos | 11.334 |
| Arquivos de resultado idênticos no replay | 5 |
| Arquivos protegidos com hashes inalterados | 28 |

Cada variável monetária tem 1.415 células armazenadas, cinco entidades sem armazenamento e duas sem o localizador: 42 posições ausentes nas seis variáveis. Não equivalem a NI, zero, falta econômica de informação ou sete bancos sem dados. Crédito conserva 303 zeros; captações, 391; agências, 784; postos, 841. Observações reais monetárias são JSON numbers, quantidades são strings do cadastro; os testes sintéticos cobrem também NA/NI/null/vazio/expoentes e precisão superior a float binário.

O confronto local independente da geração releu os pointers nos corpos, comparou lexemas/tipos e Decimal em todas as observações, contou grade/cadastro, verificou hashes/tamanhos e bytes do replay. A preservação cobre dez arquivos das cinco fontes (manifests e corpos), sete arquivos do inventário individual aceito e onze do snapshot Parquet individual; não é uma alegação de auditoria de todo o arquivo histórico.

## Entrada e reprodução

CLI: [`scripts/admit-financial.py`](../../scripts/admit-financial.py); leitor [`financial.py`](../../bank_quality/financial.py); perfil [`financial-profile-202412.json`](../../bank_quality/financial-profile-202412.json). Usa exclusivamente os cinco manifests arquivados O/C5/D/P/N1 identificados na [nota primária](financial-snapshot-202412-contract-20261003.md#primárias-disponibilidade-e-vintage). O perfil valida integralmente as oito definições e o esquema/notas do relatório. O portal é fixado pelo SHA aprovado, além de verificar o fragmento de formatação; um código alterado com fragmento preservado em comentário é rejeitado.

O índice local tem `contract: "ifdata-financial-sources-v1"`, `selection: {"period": 202412, "perspective": 1005, "report": 92}`, `code_revision` e objeto `sources` com exatamente `catalog`, `cadaster`, `dictionary`, `portal`, `numeric`. Cada valor é o caminho de seu manifesto relativo ao índice (ou absoluto). Usar O/C5 da aquisição cadastral e D/P/N1 da descoberta anterior, conforme a nota; não escolher arquivos por glob nem alterar seus contextos originais. `code_revision` é declaração do executor, complementada pelos hashes de código/perfil; não é atestação Git automática. Sem o bruto local íntegro, o comando falha.

```powershell
& .\.venv\Scripts\python.exe -B scripts/admit-financial.py --index data/runs/financial-admission-202412-20261003/sources-reviewed.json --output data/derived/financial-202412-20261003
& .\.venv\Scripts\python.exe -B scripts/admit-financial.py --index data/runs/financial-admission-202412-20261003/sources-reviewed.json --output data/derived/financial-202412-20261003-replay
```

Ambos retornaram `observations=11334`, `cells=11376`, `cadaster_records=1422`, seleção 202412/1005/92. Os destinos foram novos; agora estão aceitos e não podem ser reutilizados. Para repetir, usar dois destinos ausentes e comparar os cinco arquivos de resultado. `manifest.json` difere entre execuções por `created_utc`; ambos conservam os mesmos hashes de entrada/código/perfil/saídas. Falhas anteriores à publicação final não produzem marcador de aceite, e arquivos parciais permanecem para diagnóstico.

| Arquivo reproduzido | Bytes | SHA-256 |
|---|---:|---|
| `financial-observations.csv` | 5.563.063 | `1305972bb427611e3f601531974e66f5d0a90cbc4363beb6a24bf962fd48b7f3` |
| `financial-cells.csv` | 5.584.099 | `6c8a9db45f17e7c1a3c96006ae926ff9defa9de550df7d51b14b5f286cbeda4c` |
| `financial-cadastro.csv` | 676.222 | `211d865e09d6d2bd95ac1150e2ca8b45f45e10887be3ab9be5a49d6bff9dc194` |
| `financial-variables.json` | 6.308 | `2cb1ced7fed01b7061f311ca66961f27aafe3815ed7b98099ebb460d6545d841` |
| `financial-diagnostics.json` | 2.820 | `914a9c917abfdbc8e28709d4f70055cc6ef21c15aeb7d6d6a32751d967e0aa7a` |

Hashes: leitor normalizado LF `cf76e89214d9adf43d86c75cb7ed6345d7209b09f07fd1a1db965bcd749aa81a`; perfil normalizado LF `0177b64e9590afbb54db4e3909c946a664299e32189a50d3914fdf4df573a371`; índice `991c89a20ec4b56ca81eae42ee30e9375a0286ad057034a8da6af4c50fadbf40`. Manifesto inicial `f46858edc76c2e9d1d619b40fcdfaa083792cd7664a146d5d6dcaed5ae106043`; replay `cf3724513fd2ad2e3680903c13551eafb8d12164339d5454350375603252b572`. Manifests, índice, auditoria e dados permanecem locais ignorados; só código, metadados do perfil e evidência sanitizada são públicos.

## Validação e limites

TDD reproduziu os defeitos de portal alterado e seletor `null` (dois FAIL antes da correção); depois, **14 testes financeiros PASS**. Suíte `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`: **120 PASS**. Node `tests/test-budget.cjs`: guardas PASS; `node --test tests/test-portal-ready.cjs`: **2 PASS**. CLI também testada de outro diretório, precisão/estados/duplicatas/fontes/schema/escopo, recusa de destino existente e interrupção antes do manifesto final. Perfil sintético nos testes substitui somente o hash do portal temporário; a CLI pública não oferece override do perfil instalado. Diff/links/allowlist e revisão final completam o gate antes da integração.

BRL bruto é inferência documentada do portal aprovado, que divide por mil para exibição; os valores armazenados não são escalados. Estoques têm data de referência inferida em 31/12/2024; lucro mantém `ifd=79718`, `lid=78187` e janela julho–dezembro pelo `rp`, sem promoção a lucro anual. `ge="15/04/2026"` e `v="1"` são textos observados do relatório. Recuperações O/C5 e D/P/N1 não são simultâneas; geração cadastral/dicionário/números segue desconhecida. Contextos originais de descoberta são preservados, mesmo quando descrevem individual; a associação financeira é sustentada pelo catálogo/cadastro/chaves, sem alegar vintage conjunta.

Aceite técnico e testes não comprovam correção econômica/contábil dos valores, universo histórico, elegibilidade, vínculo legal, indicadores acadêmicos ou comparabilidade 2025. Parquet financeiro, outras referências/perspectivas, aquisições e método/amostra exigem entregas próprias; os contratos e artefatos individuais permanecem preservados.

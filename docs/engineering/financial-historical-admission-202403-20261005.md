# Execução — financeiro histórico nativo 202403

Issue: [55](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/55). [Contrato](financial-historical-admission-202403-contract-20261005.md) e [plano](../superpowers/plans/2026-10-05-financial-historical-admission-202403.md). Resultado local de 2026-10-05: admissão/Parquet/consulta/replay completos. Publicação, revisão do conjunto final, CI e integração têm autoridade na Issue real. A [Issue 2](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/2) acompanha o aceite integral: três referências integradas antes desta entrega e uma quarta validada localmente.

## Ponte e testes

Ponte pura para o anchor confiável 202403 no módulo de autoria existente, sem escrita ou GET. Dois arquivos de código/teste e nenhum rename/delete/dependência. RED: seis casos, 13 falhas esperadas pela API ausente, 2,908 s. GREEN dirigido: seis PASS em 5,194 s. Módulo: 23 PASS em 15,080 s, zero skips. Revisão independente APP de spec/qualidade, com três probes sintéticos PASS em 3,846 s. Isso prova software/integridade, sem substituir a conferência do perfil real.

Integração local na base `6172b38395830be7655d41a185c4c97841577333`, após PR 56/Issue 54 e CI pós-merge aprovados. Os blobs dos dois paths foram comparados com a base de revisão anterior antes da cópia; cinco pins físicos da aquisição recente preservados.

## Autoria real medida

Run novo `data/runs/financial-historical-admission-202403-20261005/`. Compose/compile/freeze concluídos sem GET/instalação/admissão. Perfil draft SHA-256 `8b7dfde1084b86d8b0cff29a011cf3e2432e0f0dd486f14454f41da4fb427076`; envelope `3820977d6e8eb66720b55ef83fb690b1867c954f7b577c68ce0ef789cebb13fe`; A projetado `e80d0a39592ff53b3c2e122fb9ef6db8d038bc7177f214447b5109febe2c6b32`; B projetado `4d0e9108b0757a51646a42f6b243539d13419466057135657ef110d6956a7ed3`. Originais/receipts/job/autoridade têm identidade própria conservada.

Preparação: 121 nós, 112 folhas, nove grupos; 36 atributos, 74 numéricos e duas quantidades; cadastro nativo 32 colunas. Fontes necessárias completas. Estes números de perfil não comprovam a grade admitida ou o Parquet.

| Estágio | Tempo | Pico amostrado working set da árvore | Resultado |
|---|---:|---:|---|
| Compose | 2,031 s | 163.659.776 bytes | exit 0, árvore encerrada |
| Compile | 0,657 s | 153.284.608 bytes | exit 0, árvore encerrada |
| Freeze | 4,141 s | 470.171.648 bytes | exit 0, árvore encerrada |

Monitor offline usa criação contida em Job Object, identidade antes de resume e encerramento da árvore inteira; não altera os workers de aquisição. Margens locais mínimas: 512 MiB de RAM livre, 1 GiB de commit disponível e 4 GiB de disco. Sem teto universal de working set. Menor RAM livre observada no freeze: 1.501.310.976 bytes; commit disponível 9.209.950.208 bytes. Nenhum guard, erro de medição ou cleanup.

A primeira tentativa do monitor assumiu um PID único; o lançador da `.venv` criou outro processo e a checagem parou antes de criar o run. Ausência de processos/destino foi conferida; log e falha foram preservados. Monitor corrigido para criação contida e revisado independentemente antes das três execuções reais. Não reiniciar processo com base em timeout de observação.

Conferência de 931 arquivos protegidos após autoria: somente os dois códigos autorizados já revisados diferem da baseline anterior. Registry/perfis/fontes/autoridades/entregas aceitas continuavam intactos antes da instalação abaixo.

## Perfil aprovado e instalado

Revisão independente APP de spec/qualidade do perfil e do registry draft, sem P1/P2. Três conferências read-only passaram, incluindo uma passagem única pelas cinco fontes físicas, todos os 121 nós/definições/pointers/annotations, envelope externamente pinado e as duas ligações A/B. Journal corrente sequência 10 conserva o receipt histórico sequência 9; zero pending/failure/reset. Cadastro físico 1.397 × 32; 74 bindings numéricos usam 69 localizadores distintos, presentes. O shard completo tem 4.315 entidades/744.797 células; esses números não são a população/grade da admissão selecionada.

Integrador instalou os bytes exatos do perfil aprovado no destino existente e o registry SHA-256 `67aa15bee78f21e310fd6a3852af729aad9946bac877ba107545ffe317ae6400`. Conferência do diff estrutural: somente `profile_path` e `profile_sha256` do membro 202403; outros membros e campos intactos. Contexto instalado carregou o pin aprovado. Quatro perfis ativos, porém somente três referências com aceite financeiro integral neste ponto. Testes/gates finais e publicação permanecem posteriores.

O módulo de perfil após instalação passou: 23 testes em 14,453 s, zero falhas/erros/skips. O teste de lookup já valida genericamente todos os membros ativos; não foi necessário alterar sua expectativa por contagem.

## Gate real completo e reprodução

Código/perfil/registry fixados no commit local `a108d127701faba1476835d606355cfdcea69d1b` antes do gate. Operador offline revisado, inputs e aplicação pinados; baseline de 942 arquivos protegidos, nove módulos de execução e três scripts privados. Nenhum GET, alteração de fonte/autoridade ou sobrescrita de destino aceito. Cada etapa usa um processo contido, encerra sua árvore e libera memória antes da seguinte.

Admitido: `data/derived/financial-historical-202403-20261005/manifest.json`, SHA-256 `50a6a83dd38f444e9d328a1af2703e578834beb556bec6b979cdb44c2fa859dc`. Parquet: `data/curated/financial-historical-202403-20261005/manifest.json`, SHA-256 `3a649d1c9b93bae343cc86e5222fd1447e62b19df19d713f718ab78033f02585`; contrato `ifdata-financial-reports-historical-parquet-v2`.

Resultado selecionado: **156.464 células, 156.316 armazenadas e 148 ausências**, cadastro 1.397 × 32. Estados: 60.179 numéricos, 45.845 zeros, 50.292 textos e 148 células não observadas. Grade autoritativa de 32 campos VARCHAR; 121 nós, 112 folhas e nove grupos. As ausências não viraram zero ou observação armazenada.

Dos 76 bindings numéricos/quantidade, 75 cabem em DECIMAL38 e um usa `numeric_exact_text`: DRE 98/coluna 18583, precisão 41 e escala 30. O adapter v2 comum preservou o token e o Decimal sem nova alteração de código, arredondamento, DOUBLE ou estreitamento. Não existe aritmética SQL DECIMAL41 nativa prometida; o accessor retorna Python Decimal exato.

Uma abertura SQL validou a grade, cadastro, nós, estados, origens, reconstrução de CSVs e todas as parts/views. Após fechar essa conexão, uma abertura do accessor confrontou **106.172 linhas** numéricas/quantidade, uma a uma, com o CSV autenticado: instituição, relatório, coluna/pointer, ordem e Decimal/None. Replay em destinos novos com sufixo `-replay` repetiu a conferência integral.

Os cinco payloads da admissão e 80 payloads Parquet/companions são byte a byte iguais ao replay. Exceções de execução: `manifest.json` e a cópia `metadata/source-manifest.json`, com criação UTC diferente e hashes derivados desse timestamp. Os manifests/cópias/inventários foram autenticados e comparados nos demais campos; nenhuma outra diferença foi descartada. Os 942 arquivos da baseline final permaneceram iguais.

| Estágio | Tempo | Pico amostrado working set da árvore | Resultado |
|---|---:|---:|---|
| Admissão | 8,375 s | 423.591.936 bytes | aceito |
| Conversão | 14,125 s | 783.699.968 bytes | aceito |
| Consulta e accessor integrais | 25,454 s | 840.142.848 bytes | PASS |
| Replay admissão | 8,484 s | 423.694.336 bytes | aceito |
| Replay conversão | 14,312 s | 757.661.696 bytes | aceito |
| Replay consulta/accessor | 26,890 s | 840.331.264 bytes | PASS |
| Comparação integral/protegidos | 3,859 s | 77.942.784 bytes | PASS |

Orquestração completa: **102,953 s**. Todos os processos tiveram exit 0/árvore extinta, sem guard/erro de medição/cleanup. Menor RAM livre observada: 601.706.496 bytes, acima da margem local 512 MiB; menor commit disponível 8.262.615.040 bytes, disco livre sempre acima de 198 GB. Picos são amostrados e abrangem a árvore monitorada; não são garantia de capacidade em outro host ou de dois gates pesados concorrentes.

## Consulta local reproduzível

Usar a `.venv` já configurada, na raiz do checkout, sem coleta. O manifest externo é a identidade deste resultado:

```python
from pathlib import Path
from bank_quality.financial_parquet import snapshot_connection

destination = Path("data/curated/financial-historical-202403-20261005")
pin = "3a649d1c9b93bae343cc86e5222fd1447e62b19df19d713f718ab78033f02585"
connection = snapshot_connection(destination, manifest_sha256=pin)
try:
    print(connection.execute("SELECT report_id, count(*) FROM financial_cells GROUP BY report_id ORDER BY report_id").fetchall())
finally:
    connection.close()
```

O accessor `bank_quality.financial_reports_parquet.iter_numeric_decimals(destination, manifest_sha256=pin)` fornece os valores exatos, incluindo o binding largo. Essa validação materializa o snapshot; não promete memória constante.

## Próxima escala

O tempo do gate confirma que tratamento de uma referência não explica horas de preparação/revisões separadas. A [Issue 57](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/57) consolida geração de perfis e admissão/Parquet/query/accessor/replay por lote, com revisão de código por mudança do executor e evidência/estados por referência. Primeiro os sete conjuntos já coletados, depois janelas das outras 55 ofertas. Sem um pipeline/PR por trimestre; diferenças nativas e falhas reais continuam explícitas, sem reduzir o aceite dos quatro relatórios.

## Checks do conjunto público

`.venv/Scripts/python.exe -B -m unittest discover -s tests -v`: **461 testes PASS em 269,820 s**, zero falhas/erros/skips neste Windows, após o perfil instalado e a ponte integrada. Suíte final executada uma vez; não repetida por alteração somente documental. Node/JS não foram alterados neste lote; checks remotos do PR verificam o workflow existente, sem nova coleta.

Inventário final: nove arquivos autorizados, sem delete/rename/dependência; 90 links locais conferidos, privacidade e `git diff --check` aprovados. Baseline de 942 protegidos permanece igual salvo README/arquitetura, dois destinos documentais com atualização expressamente autorizada após o gate. Perfil, código e sources/payloads aceitos preservam os pins revistos. Revisão independente do SHA final e PR/CI/integração são confirmados na Issue 55, sem promover este check local a aprovação remota.

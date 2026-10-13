# Retomada CVM–B3–IF.data em outro computador — 2026-10-13

[Issue108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108), [contrato de publicação/snapshot](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108#issuecomment-6146911216). Pedido de João: salvar código, implementação e base no GitHub para continuar em computador mais forte. O snapshot será publicado em Release própria `snapshot-cvm-b3-20261013`, preservando as anteriores. Confirmações de publicação/download e os hashes finais ficam nos assets `SNAPSHOT.json`/`SHA256SUMS.txt` e na Issue; este texto não substitui a conferência desses registros.

## Estado que está sendo transportado

- Branch `codex/cvm-b3-history-2010-2024`, código societário revisado e relação histórica `historical-issuer-links-v1`. A correção de ciclos foi revisada no commit `187cc770cc135f8fbbcd213f60efdbf91665351b`: 16 testes e oráculo independente de512grafos. SHA exato do conjunto transportado em `SNAPSHOT.json`.
- Pacote CVM/CAD/FCA2010–2024, cadastro BCB106trimestres com recorte de60 para a monografia, fontes FRE15anos e pacote societário v2 aceito com189.035observações. Pacotes iniciais/replays permanecem identificados como diagnóstico ou evidência de reprodução; não adotar o primeiro processamento societário rejeitado.
- Base IF.data nativa já disponível:18.228.826linhas nos quatro conjuntos, cadastro512.959registros, catálogo438definições e piloto de indicadores já existentes. Financeiro continua exclusivamente IF.data; CVM/B3/SEC fornecem metadados nesta frente.
- Fontes originais, notas, referências, recibos, pesquisas BDR, RED/GREEN, pareceres e diagnóstico de recurso preservados. Inventário complementar BDR17candidatos é pesquisa revisada, **zero vínculos admitidos** por esse inventário.
- **Não existe pacote histórico real aceito.** A primeira tentativa foi interrompida antes de criar a saída:6,93GBprivados, pico4,87GBworking set, somente24.956KiBdeRAMlivre numa máquina7.712.836KiB. Inputs permaneceram intactos. Não houve verificação/replay desse pacote.
- Normalização v2/nona tabela de caminhos é proposta revisada, não implementada. Não esperar essa tabela ou chamar o código de v2.

## Direção acadêmica para continuar

2010–2024; conglomerados financeiros principais, instituições individuais complementares e prudencial separado. Ações, units e BDRs têm igual prioridade. João aceitou relações de CNPJ, notícias e pesquisa como fundamento da identificação, dispensando documento jurídico formal para cada ligação. Guardar fonte, natureza, confiança, conflitos e alcance temporal; desconhecido permanece desconhecido. Não exigir certificação jurídica universal para usar uma concordância cadastral na análise. Não retroprojetar cadastro/listagem corrente a todos os trimestres. Fórmulas e amostra final continuam próprias da Issue3.

## Como restaurar

1. Baixar todos os assets da Release e conferir `SHA256SUMS.txt`. O ZIP automático do GitHub contém somente código, não a base. Usar a chave privada já fornecida para os snapshots anteriores, mantida fora do GitHub.
2. Descriptografar com `Unlock-Snapshot.ps1` para arquivo novo e restaurar com `restore-snapshot.py` em **staging novo**, conforme os comandos exatos do asset `RETOMADA.md`. Os helpers autenticam o transporte e todos os membros; não sobrescrevem destinos existentes.
3. Clonar o repositório e selecionar o `code_commit` de `SNAPSHOT.json`/branch indicada. Copiar somente os destinos de dados verificados para locais novos na instalação. Fontes e manifests aceitos mantêm bytes/hashes; pesquisa privada transportada tem mapa de origem no inventário e não é runtime.
4. Criar ambiente Python3.12, instalar `requirements-duckdb.txt` com hashes e rodar os checks focados. Não transportar ou executar `.venv`, runtime antigo ou coordenação de outra máquina.

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install --require-hashes -r requirements-duckdb.txt
.venv/Scripts/python.exe -m unittest discover -s tests -p test_historical_issuer_links.py
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_cvm*metadata.py'
.venv/Scripts/python.exe -m unittest discover -s tests -p test_ifdata_cadastro.py
```

Os caminhos absolutos registrados nas pesquisas são proveniência original. Usar o mapa de origem do snapshot para localizar as cópias no novo ambiente, sem reescrever documentos autenticados. A consulta dos pacotes aceitos usa seus diretórios e pins externos, não o nome do usuário do computador anterior.

## Próxima execução

Reautenticar os inputs e medir recursos da nova máquina antes de executar. A CLI v1 aceita:

```powershell
.venv/Scripts/python.exe scripts/build-historical-issuer-links.py build data/curated/cvm-identity-20261012 data/curated/ifdata-cadastro-20261011 data/curated/cvm-corporate-history-20261012-v2 data/curated/historical-issuer-links-retomada --cvm-sha256 5abaef4891fdf9eb8eb86aecedbce7694005d98999b85561881018b71c3b79a7 --cadastro-sha256 874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1 --corporate-sha256 ebecfd9cccad88c19e9aba787ec89cc0f480d217a56a87b481ce7152196c65a0
```

O destino precisa ser novo. Guardar o hash retornado para `verify`/`query`; executar replay em outro destino e conferir campos/fontes/chaves/contagens antes de aceitar a base. Aumentar RAM não prova que o arquivo resultante cabe no limite de1GiBpor tabela do v1. Se necessário, avaliar a proposta de normalização com teste de equivalência e revisão antes de implementar; não truncar instituições, caminhos ou períodos para caber.

Depois: incorporar os candidatos BDR e as fontes adicionais aceitas por João, resolver ou expor lacunas B3, revisar a composição real e completar publicação/integração/CI da entrega. Snapshot disponível não significa restauração no computador receptor, relação histórica concluída ou monografia pronta. Project3 permanece comZec.

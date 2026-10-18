# Caixa: ponte entre banco e conglomerado financeiro em 2021

Pesquisa da [Issue 146](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/146), em 16/10/2026, a partir da [triagem 144](ifdata-roa-roe-ttm-triage-20261016.md). Resultado local; nenhum indicador, agregado ou HTML recalculado/alterado. As [fontes oficiais e sua proveniência](caixa-financial-transition-sources-20261016.md) integram este parecer.

## Resposta

**Há dados para uma ponte de continuidade histórica, com mudança explícita de perímetro. Não foi demonstrada uma reconstrução exata do conglomerado antes de setembro de 2021.** Recomenda-se a primeira alternativa para uma futura correção seletiva, condicionada à decisão metodológica de usar banco predecessor → conglomerado sucessor como série de perímetro observado.

Até 2T2021 o universo Financeiro publica a Caixa sob `00360305`, código do banco. Em 3T2021 passa a publicar `C0051626`, conglomerado financeiro liderado pelo mesmo banco, incluindo a DTVM `42040639`. Os indicadores de 12 meses sob o código novo não encontram o histórico necessário e ficam sem valor de **3T2021 a 2T2022**. Isso não indica ausência de dados da Caixa ou lucro zero.

A regra atual de exigir a mesma unidade protege contra ligações indevidas. Neste caso, há evidência para examinar uma exceção nominada e datada. Essa exceção não deve transformar qualquer líder comum em ponte automática.

## Confronto de toda a transição

Consulta determinística, somente leitura, sobre onze datas de 1T2020 a 3T2022, com cadastro, Financeiro e Individual autenticados. Consulta principal: 0,23 segundo. Em **18/18 comparações** de LL/AT/PL entre 1T2020 e 2T2021, Financeiro do banco e Individual do banco coincidem exatamente. A fonte candidata para preencher o histórico continua sendo o próprio **Financeiro do banco**; Individual serve de comparação.

Após a mudança, o banco Individual continua disponível e permite comparar contemporaneamente os dois perímetros:

| Data | AT do conglomerado menos AT do banco, R$ | PL: conglomerado menos banco, R$ | LL nativo: conglomerado menos banco, R$ |
| --- | ---: | ---: | ---: |
| 3T2021 | 105.856,54 | 0,00 | −0,00001 |
| 4T2021 | 78.695.344,00 | 0,00 | −0,00001 |
| 1T2022 | 87.279.694,07 | 0,00 | −0,00001 |
| 2T2022 | 81.835.738,98 | 0,00 | 0,00000 |
| 3T2022, comparação posterior | 89.270.719,36 | 0,00 | −0,00001 |

O ativo da Caixa nessas datas é da ordem de R$ 1,4–1,6 trilhão. As diferenças observadas de AT são pequenas frente a esse total, mas não são zero. Os tokens originais, inclusive diferenças inferiores a um centavo em LL, foram preservados. Comparações de LL são dos **saldos nativos**, não uma certificação da janela de qualquer entidade recém-criada nem um cálculo de lucro de 12 meses.

O cadastro prova liderança e vínculo datado, não igualdade contábil. Consórcios com o mesmo líder aparecem no cadastro, mas sem vínculo a `C0051626` no recorte: não foram incluídos por nome ou por líder. O conglomerado prudencial `C0080738` não é um membro operacional adicional a somar.

## O ponto que impede chamar a ponte de exata

A DTVM foi constituída em **14/04/2021**, autorizada em **27/09/2021** e começou a receber receitas de serviços com a migração da gestão de fundos em novembro. Portanto, sua primeira aparição cadastral em setembro não permite supor inexistência em junho. [Fontes e páginas](caixa-financial-transition-sources-20261016.md#cronologia-documentada).

Há diferença entre as demonstrações de junho: o banco registra investimento de R$ 50,122 milhões e resultado de equivalência de R$ 114 mil; a própria DTVM apresenta PL de R$ 50,190 milhões e lucro de R$ 183 mil. As diferenças são R$ 68 mil e R$ 69 mil, em valores publicados arredondados a milhares. Sua causa não foi conciliada. A diferença de datas de publicação pode ser relevante, mas não foi provada como explicação. [Confronto das notas oficiais](caixa-financial-transition-sources-20261016.md#diferença-que-impede-certificar-equivalência-exata-em-junho).

Assim, PL/LL iguais entre banco e conglomerado **depois** da troca não demonstram igualdade retrospectiva em junho. Tampouco é correto somar o lucro/PL da DTVM ao banco: este já registra investimento e resultado por equivalência, exigindo eliminações. O AT de R$ 50,346 milhões e o passivo fiscal de R$ 156 mil da DTVM não são ajustes consolidados automaticamente aplicáveis.

O consolidado publicado da companhia abrange outras subsidiárias e diferenças contábeis, inclusive IHCD; não deve substituir a coluna Financeiro IF.data. O patrimônio dos fundos administrados também não é ativo próprio da DTVM.

## Janela inteira, dependências e alcance da ponte

O mapa reproduzível encontrou **36 referências ausentes** nos oito resultados (quatro datas × R1/R2), contando repetições entre resultados. Todas têm um token finito candidato sob `00360305` no Financeiro. Isso demonstra disponibilidade técnica; não promove os valores a observações nativas de `C0051626`.

| Resultado de 12 meses | Estoques anteriores faltantes de AT/PL | Referências de LL anteriores faltantes |
| --- | --- | --- |
| 3T2021 | 3T2020, 4T2020, 1T2021, 2T2021 | 3T2020, 4T2020, 1T2021, 2T2021 |
| 4T2021 | 4T2020, 1T2021, 2T2021 | 1T2021, 2T2021 |
| 1T2022 | 1T2021, 2T2021 | 1T2021, 2T2021 |
| 2T2022 | 2T2021, abertura | Nenhuma: quatro trimestres de lucro já estão no conglomerado |

Os estoques incluem a abertura e todas as fronteiras trimestrais para a média ponderada pelos dias já aprovada. LL conserva a regra semestral nativa: junho menos março produz 2T; dezembro menos setembro produz 4T. Setembro não exige subtrair junho. A transição em setembro coincide com o início do segundo semestre, evitando uma subtração direta entre banco em junho e conglomerado em setembro. Isso não elimina a ressalva de perímetro.

A DTVM não existia em 3T/4T2020 ou 1T2021 segundo sua data de constituição. **2T2021 é o ponto anterior à troca que exige a ressalva contábil**, afetando a abertura/média dos quatro resultados e o lucro anterior dos três primeiros. O lucro dos 12 meses em 2T2022 não precisa de ponte; ROA e ROE ainda precisam da abertura de AT/PL em junho de 2021.

## Regra recomendada e alternativa

Para uma futura correção seletiva, recomenda-se uma **série de continuidade do perímetro observado**, com estas condições:

1. Aplicar somente a `C0051626`, Financeiro, R1/R2 de 12 meses, em `202109`, `202112`, `202203`, `202206`.
2. Usar os valores financeiros nativos do banco `00360305` nas dependências anteriores à troca, de `202009` a `202106`; manter o conglomerado nas datas posteriores. Preservar código/data/conta/token/hash e vínculo original de cada input.
3. Identificar o resultado como derivado com ponte de sucessão de reporte e mudança de perímetro; não rotular a parte antiga como conglomerado nativamente observado ou como perímetro constante.
4. Preservar fórmula, janelas e média de estoques existentes. Não acrescentar DTVM por soma, preencher nulos, arredondar entradas ou apagar a diferença de junho.
5. Refazer somente os oito resultados e os agregados/segmentações que efetivamente dependem deles; verificar os demais resultados intactos. No comparador histórico atual, Caixa pertence ao restante/sistema, não à amostra das 24; a seleção revista não foi aplicada nesta pesquisa.

Essa proposta representa continuidade econômica acompanhando a organização em cada época. É uma aproximação em relação a um conglomerado de **perímetro constante retrospectivo**, não uma nova observação da fonte. Sua adoção exige escolha metodológica explícita. Não foi criada tolerância de materialidade para admitir automaticamente a ponte.

A alternativa estrita é manter os oito resultados ausentes até obter e conciliar investimento, equivalência, saldos e eliminações da DTVM em junho, em bases/versões compatíveis. A pesquisa não recomenda prolongar essa conciliação para tentar obter identidade de centavos: os PDFs são publicados em milhares e a diferença de versões ainda não foi resolvida. A ponte documentada é o caminho de menor esforço para recuperar continuidade, aceitando sua limitação.

## Evidência e estado

Base de código `087700ccafa81ad96c963df62b633fb317d4ca21`, worktree monograph-docs. Notas nesta pasta engineering; nenhuma nova camada, dependência ou mudança de arquitetura. A pesquisa 143 e a entrega documental 142 conservam seus destinos próprios.

Recibos privados na visualização `2026/10/13/01a1361f-f20f-7f23-b187-beee4d316e48`:

- `diagnosticar-transicao-caixa-146.py`, produtor SHA-256 `61ddc7ffefdf245fe0299c50a331c24711ca3fefa17d603958ac8193b8682c5b`; `caixa-146-recibo.json` registra hashes de manifests/partes e três outputs de cadastro, valores nativos e comparações;
- `mapear-dependencias-caixa-146.py` e `caixa-146-candidate-input-map.json`: 36 referências, disponibilidade e proveniência de cada candidato, sem avaliador de indicadores;
- PDFs oficiais, extrações e evidências em `.scratch/caixa-transition/`, com URLs, hashes e UTC na nota de fontes.

Manifest de Individual `484a0e30269d0e830ef254958a408fe8e797011aa24b6b23ae29ea3d399f91fc`, financeiro `f0b5a836effbb7fe058513e8e13b6f8cff9d781827f16a4dfa1be9df17302095` e cadastro `874300bde66f759aa7ffac9a26a13df304472fa7f6a7cdff4b7d6e426973a8e1`, autenticados pela base aceita. Contextos nativos distintos permanecem próprios; não se afirma unicidade pela chave reduzida relatório/conta para todo o corpus.

Revisões independentes A e B/final: **PASS, sem achado material de revisão**. Foram conferidos as comparações, o mapa de 36 referências, hashes dos outputs e PDFs, tabelas oficiais e a DRE de junho renderizada. Compilação dos scripts e `git diff --check` passaram; hashes protegidos do núcleo, perfil e HTML permanecem iguais aos da entrada. O achado de domínio — divergência das demonstrações de junho — permanece explícito, sem correção inventada. **Nenhuma ponte foi implementada ou adotada nesta pesquisa; dados, motor, resultados e explorador permanecem intactos.** Sem commit ou PR.

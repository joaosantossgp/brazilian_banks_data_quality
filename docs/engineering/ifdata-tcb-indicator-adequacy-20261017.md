# Adequação dos indicadores por Tcb: perguntas, complementos e lacunas

Auditoria dirigida da [Issue 152, etapa C](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/152), em 17/10/2026. Entradas no checkout principal, somente leitura: [pesquisa 143](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/da6b53a119cfc70b9838093f5e90d3bc7b7cf9db/docs/engineering/financial-indicators-activity-review-20261016.md), sua [proveniência](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/da6b53a119cfc70b9838093f5e90d3bc7b7cf9db/docs/engineering/financial-indicators-activity-review-20261016.provenance.md), [matriz de componentes](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/da6b53a119cfc70b9838093f5e90d3bc7b7cf9db/docs/engineering/financial-indicators-activity-components-20261016.csv) e [atlas 148](https://github.com/joaosantossgp/brazilian_banks_data_quality/blob/08c843f6bf2bf67de39123a97583077a487a840d/docs/engineering/financial-indicators-formulas-20261017.md). Usam-se referências versionadas porque esses arquivos não estão neste worktree; não foram copiados ou alterados nesta fatia.

**Conclusão operacional:** manter os dez indicadores e implementar os sete complementos aprovados melhora a explicação do balanço e do resultado. Não encerra a seleção por negócio. É necessário distinguir indicadores comuns, adaptações contábeis e medidas específicas ainda sem componentes demonstrados. Esta nota organiza essa diferença em **40 células: oito Tcb e cinco dimensões**, sem calcular razões, alterar classificações ou adotar fórmulas adicionais. Não existe certificação de cobertura integral das cinco dimensões.

## O que a auditoria acrescenta às pesquisas anteriores

A pesquisa 143 já discute modelos de negócio, alternativas e classes de viabilidade; o atlas 148 expõe os dez indicadores e os sete complementos com marcações condicionais. O quadro visual não é uma whitelist implementada. A shortlist transversal resolve parte da necessidade, mas salvaguarda de pagamentos, obrigações de clientes, centralização cooperativa, arrendamento e funding institucional exigem outras perguntas. A cobertura elevada dos componentes comuns não demonstra adequação econômica.

O objetivo é escolher os melhores indicadores para a pergunta de cada negócio, e não multiplicar fórmulas arbitrariamente. `Tc` público/privado ou a simples combinação de `Sr` com `Tcb` não muda por si a fórmula contábil de ROA. Já a mudança de crédito bancário para leasing altera a carteira e as rendas que precisam entrar na medida. Um conglomerado B1 pode conter negócios diferentes; seu Tcb não representa licença de cada membro ou decomposição de todas as suas receitas.

Esta fatia usa Tcb como eixo inicial e exige SegmentoTb, composição contábil, perímetro e data para o detalhamento. Não infere atividade pelo nome da instituição. B3/N3 do cadastro geral e classificações ausentes continuam sem de-para presumido. Atividade permanece fora dos filtros. Financeiro é principal; Individual e Prudencial não recebem fórmulas ou atributos por transplante.

## Legenda de decisão, componentes e tempo

**Comum:** fórmula já adotada, interpretação condicionada. **Complemento aprovado:** LA, LC, LF, RS, E3, R4 ou R5, ainda sujeito à implementação/validação. **Adaptar:** desenho candidato com componentes locais possíveis, sem adoção automática. **Específico:** pergunta relevante que requer conceito/abertura própria; não equivale a indicador calculável nem a não aplicabilidade. A referência de cada célula combina a base contábil A com a fonte de negócio indicada; recomendações de seleção são síntese desta auditoria, não transcrição dessas fontes.

| Chave | Componentes comprovados no catálogo da pesquisa 143 | Janela e limite |
|---|---|---|
| R | R1/R2: LL78187, AT78182, PL78186, Resumo1. R4: resultado intermediação78215/DRE4 e AT. R5: rendas crédito78203/DRE4 e CR78191/Ativo2. | Fluxo trimestral efetivo ou TTM; AT/PL/CR médios com abertura e ponderação temporal vigentes. LL tem definições distintas antes/depois de201903. R4 contém provisão e não é NIM/spread contratual. |
| Q | Q1: CR78191 e provisão78192/Ativo2; Q2: resultado provisão78213/DRE4 e CR médio. | Q1 estoque/data; Q2 fluxo trimestral/TTM. Sinais conciliados e reversões preservadas; não são inadimplência, atraso ou perdas realizadas. |
| C | C1: PL78186/AT78182 no Financeiro. C3: PR79649/RWA79665; C4: CP79645/RWA79665, capital/Tipo1/relatório5. | Estoque na data. Prudencial admitido2015–2024, com regime próprio e ruptura de cobertura2018; C1 não mede folga regulatória. |
| L | L2: (DISP78188+AIL78189)/DV78282; L3: CR78191/DEP78287. LA: (DISP+AIL)/AT; LC: CR/AT. LF: DEP78287, compromissadas78288, emissões78294, empréstimos/repasses78295, divididos pelo pai78185 do Passivo3. | Estoques na mesma data, síntese de dezembro. LF tem quatro participações e exige identidade/residual das rubricas irmãs; não usar o pai homônimo do Resumo como parcela adicional. LF não inclui necessariamente todas as obrigações. |
| E | Custos C=−(78218+78219); renda selecionada S=78215−78213+78216+78217. E2-B=C/S; RS=(78216+78217)/S; E3=C/AT médio. Todos os fluxos são DRE4. | E2-B/RS mesma janela trimestral efetiva ou TTM; E3 usa AT médio temporal. S não é receita operacional total; E2-B não é o IE literal do Assaf. |
| X | Já localizados, não adotados: arrendamento78194/78195/78197/78198 no Ativo2; rendas78204 e despesas78211/DRE4; depósitos interfinanceiros78284/Passivo3; participações78221, outras receitas78222 e outras despesas78223/DRE4. | Existência do contexto não prova saldo finito, cobertura histórica conjunta, identidade de carteira ou fórmula final. Catálogo marca comparabilidade não certificada. Não inferir subtipo/fluxo/conta restrita a partir do rótulo. |

As contas são identificadores IF.data, não códigos COSIF. As chaves completas incluem dataset, TipoInstituicao, relatório, grupo, definição e período. A tabela não autoriza procurar apenas pelo número e fazer UNION de contextos. Financeiro usa Tipo2; os quatro relatórios financeiros foram auditados em 2010–2024 na143. Mudanças em Outros Depósitos202006, Passivo202212 e regime2025 conservam contratos próprios. Sem equivalência automática para o complemento2025–2026.

Cada célula abaixo herda a janela da chave indicada. Zero no denominador é indefinido; null, ausência, história insuficiente e não aplicabilidade são estados diferentes. Negativos legítimos são preservados e perdem a interpretação usual quando necessário. Nenhuma família recebe zero de risco porque não tem crédito, nem é retirada da amostra por uma métrica inadequada. Agregação é ΣN/ΣD na mesma interseção válida; razões de capital ou fluxos entre instituições do mesmo sistema não provam eliminação econômica.

## Matriz por Tcb e dimensão

### B1 — bancos múltiplos com carteira comercial, comerciais e caixas

| Dimensão | Pergunta econômica | Comum e complementos aprovados | Adaptação/específico ainda necessário | Componentes/janela; fundamento |
|---|---|---|---|---|
| Rentabilidade | Quanto o balanço/capital gera e qual negócio explica o retorno? | R1/R2; R4/R5 e RS distinguem intermediação, crédito e serviços. | Separar mix antes de comparar banco de varejo com grupo diversificado; resultado de participações pode ser relevante. Não confundir R5 com taxa contratual. | R, E, X; A341–342/F. |
| Qualidade dos ativos | Qual proteção e custo reconhecidos na carteira própria? | Q1/Q2; LC contextualiza exposição. | NPL, ativos problemáticos, concentração e contraparte fora da carteira exigem aberturas próprias. | Q estoque/fluxo; L; A324/F. |
| Capital | Qual suporte contábil e prudencial dos riscos? | C1 e C3/C4 nas unidades pertinentes. | Folga versus requerimento datado/individual; PL/AT não corrige composição de riscos. | C; A337/F e regime documentado143. |
| Liquidez/financiamento | Que fontes financiam a carteira e que obrigações pressionam caixa? | L2/L3 quando depósitos fazem sentido; LA/LC/LF explicam estrutura. | Liquidez por prazo/estresse e ativos livres: não reconstruir com TVM genérico. | L; A334–335/F. |
| Eficiência | Custos operacionais são compatíveis com a renda gerada? | E2-B, RS e E3 em conjunto. | Renda ampla/participações e outras despesas requerem conciliação de E2-C antes de ranking; não usar Receita=Resultado Operacional. | E/X; A342/F. |

### B2 — múltiplos sem carteira comercial, investimento e câmbio

| Dimensão | Pergunta econômica | Comum e complementos aprovados | Adaptação/específico ainda necessário | Componentes/janela; fundamento |
|---|---|---|---|---|
| Rentabilidade | Retorno vem de crédito, tesouraria, câmbio ou serviços? | R1/R2, RS e R4; R5 apenas na carteira produtora compatível. | Separar modelo via SegmentoTb e contas: não impor R5 a banco de câmbio/serviços. Ganhos de carteira e serviços não são spread de empréstimos. | R/E; A341–342/G. |
| Qualidade dos ativos | Qual o risco das exposições próprias relevantes? | Q1/Q2 na carteira de crédito própria; LC mostra sua proporção. | Risco de mercado/contraparte não é capturado por provisão sobre CR; exposição por instrumento/garantias permanece necessária. | Q/L e componentes específicos não demonstrados; A337/G. |
| Capital | Capital cobre os riscos efetivos, inclusive mercado? | C1; C3/C4 em regime prudencial próprio. | Não comparar folga por capital/ativo sem riscos ponderados; regra de requerimento não é uniforme. | C; A337/F. |
| Liquidez/financiamento | Qual dependência de compromissadas/emissões e obrigações de liquidação? | LA/LC/LF; L2/L3 condicionados à captação efetiva. | Vencimento, garantias e margens exigem abertura; depósitos baixos não provam iliquidez. | L; A334–335/G. |
| Eficiência | Custos sustentam serviços/intermediação desse modelo? | E2-B com teste da renda; RS/E3 complementam. | Renda de tesouraria/câmbio pode ser volátil ou negativa; abrir componentes antes de interpretar razão negativa como eficiência. | E/X; A342/G. |

### B3S — cooperativas singulares

| Dimensão | Pergunta econômica | Comum e complementos aprovados | Adaptação/específico ainda necessário | Componentes/janela; fundamento |
|---|---|---|---|---|
| Rentabilidade | A operação é financeiramente sustentável? | R1/R2, R4/R5, RS como leituras da unidade. | Benefício ao cooperado não se resume a sobras; taxas/serviços/destinações precisariam de dados próprios. Não adotar como nova fórmula neste lote. | R/E; A341–342/CO. |
| Qualidade dos ativos | Qual custo/proteção da carteira de associados? | Q1/Q2 e LC. | NPL/ativos problemáticos, garantias e concentração não estão demonstrados pelos quatro relatórios. | Q/L; A324/CO. |
| Capital | Há suporte contábil e atendimento ao regime da singular? | C1 e C3/C4 onde pertinentes. | Não substituir CP ausente por PR; tratamentoS5 e capital social requerem regra/datamento próprio. | C; A337/CO, diagnóstico139. |
| Liquidez/financiamento | Onde ficam os recursos e qual o acesso à liquidez do sistema? | LA/LC/LF; L2/L3 só na captação pertinente. | Centralização financeira e categoria da singular importam. Cooperativa de capital/empréstimo não herda pressuposto depositário; AIL agregado não prova liquidez livre. | L/X; A334–335/CO. |
| Eficiência | Qual custo para prestar serviços ao associado? | E2-B, RS/E3 com porte e modelo explícitos. | Custo menor não demonstra maior benefício ao cooperado; comparar produtos exige volumetria não admitida. | E; A342/CO. |

### B3C — centrais e confederações de crédito, com subtipo conferido

| Dimensão | Pergunta econômica | Comum e complementos aprovados | Adaptação/específico ainda necessário | Componentes/janela; fundamento |
|---|---|---|---|---|
| Rentabilidade | A unidade sustenta suas funções financeiras/de suporte? | R1/R2; RS/R4 conforme origem da renda; R5 só para carteira própria compatível. | Resultado financeiro de aplicação e prestação de serviços precisam ser separados; não tratá-la como banco de varejo. | R/E; A341–342/CO. |
| Qualidade dos ativos | Onde estão as exposições às filiadas e contrapartes? | Q1/Q2 apenas para CR próprio; LC é composição. | Risco interfinanceiro/garantias às filiadas não é ausência de risco quando CR=0; abertura de contraparte ainda necessária. | Q/L/X; A337/CO. |
| Capital | Qual suporte da unidade e do regime aplicável? | C1 e prudencial pertinente. | Não somar índices das filiadas nem chamar soma contábil de sistema consolidado; sobreposições e garantias exigem exame. | C; A337/CO. |
| Liquidez/financiamento | Como a central administra e disponibiliza recursos às filiadas? | LA/LF como descrição; L2/L3 apenas se denominador representar a obrigação relevante. | Precisamos distinguir centralização, recursos livres, obrigações e suporte de liquidez. Depósito interfinanceiro78284 é pista agregada, não marcador comprovado de centralização. | L/X; A334–335/CO. |
| Eficiência | Qual custo do serviço financeiro/compartilhado prestado? | E2-B, RS/E3 com renda conferida. | Custos rateados e serviços não precificados exigem outra base de produção. Confederação de serviços não é automaticamente cooperativa de crédito. | E; A342/CO. |

### B4 — bancos de desenvolvimento e BNDES

| Dimensão | Pergunta econômica | Comum e complementos aprovados | Adaptação/específico ainda necessário | Componentes/janela; fundamento |
|---|---|---|---|---|
| Rentabilidade | A instituição preserva capacidade de financiar seu mandato? | R1/R2, R4/R5 para carteira compatível; RS descreve receitas. | Retorno financeiro não mede adicionalidade/impacto; taxas e prazo dependem do mandato. Não impor maximização de ROE. | R/E; A341–342/BD. |
| Qualidade dos ativos | Proteção/custo são coerentes com carteira e nichos atendidos? | Q1/Q2 e LC. | Qualidade por prazo/setor/garantia e NPL: não comparar carteira de desenvolvimento com varejo sem composição. | Q/L; A324/BD. |
| Capital | Capital próprio/regulatório sustenta o risco assumido? | C1 e C3/C4 da unidade/regime. | Recursos institucionais e garantia pública não transformam passivo em capital elegível. Regras específicas e datas permanecem necessárias. | C; A337/BD/F. |
| Liquidez/financiamento | Fontes institucionais acompanham o prazo dos desembolsos? | LA/LC/LF prioritários; L2/L3 continuam medidas estreitas. | FAT/funding governamental e vencimentos não são individualizados por LF. Ausência de DV no BNDES impede L2, mas não encerra a dimensão; gap de maturidade é pergunta específica. | L; A334–335/BD. |
| Eficiência | Qual custo para manter a operação e cumprir o mandato? | E2-B, E3, RS como sustentabilidade/custo. | IE de fomento da literatura não tem abrangência/sinal conciliados; custo por desembolso/impacto requer outra base. Não adotar E4 por simples associação ao setor. | E/X; A342/BD, fichaE4 da143. |

### N1 — crédito, arrendamento, imobiliário e fomento: desdobramento obrigatório

| Dimensão | Pergunta econômica | Comum e complementos aprovados | Adaptação/específico ainda necessário | Componentes/janela; fundamento |
|---|---|---|---|---|
| Rentabilidade | O resultado remunera carteira própria ou serviço de intermediação? | R1/R2; R5 para crédito próprio; R4/RS conforme rendas. | Leasing pede renda/carteira de leasing; SEP não recebe carteira dos clientes como ativo próprio. Agência de fomento precisa leitura de sustentabilidade. | R/E/X; A341–342/NC/BD. |
| Qualidade dos ativos | Qual proteção acompanha cada carteira econômica? | Q1/Q2 para CR compatível. | Leasing: provisão78197 e carteira78194/78195/78198 exigem conciliação antes de QL. Imobiliário/fomento têm composição/prazo próprios. SEP pede exposição da operadora, não Q1 de créditos de terceiros. | Q/X; A324/NC, catálogo143. |
| Capital | O suporte próprio é suficiente para o modelo/regime? | C1; C3/C4 somente quando presentes/pertinentes. | SCD, financeira, leasing e fomento não ganham mesmo requerimento por Tcb. Regime/capital específico não comprovado fica sem medida. | C; A337/NC/F. |
| Liquidez/financiamento | Quais recursos financiam o crédito/arrendamento e quando vencem? | LA/LC/LF, L3 apenas no modelo depositário. | Emissões/repasses importam; LC de crédito não inclui leasing por nome. SCD/SEP, agência e imobiliário não recebem depósitos presumidos. Abrir funding e maturidade conforme subtipo. | L/X; A334–335/NC/BD. |
| Eficiência | Custo é comparável à renda efetiva de crédito, leasing ou plataforma? | E2-B e RS/E3 com renda conferida. | Leasing exige receitas/despesas próprias; plataforma pode ter pouco ativo. E3 elevado não prova ineficiência de serviço. E2 amplo é candidato de conciliação local. | E/X; A342/NC. |

Não há classificação nominal automática de N1. SegmentoTb observado é a primeira abertura; composição e licença datada confirmam o negócio. Os subcasos mínimos são SCFI/crédito próprio, SCD, SEP, arrendamento, imobiliário e agência de fomento. Um saldo de crédito zero não distingue esses subcasos.

### N2 — corretoras e distribuidoras, com modelo de câmbio/TVM conferido

| Dimensão | Pergunta econômica | Comum e complementos aprovados | Adaptação/específico ainda necessário | Componentes/janela; fundamento |
|---|---|---|---|---|
| Rentabilidade | Retorno vem de taxas/serviços, carteira própria ou câmbio? | R1/R2 e RS; R4 é parcela; R5 apenas em crédito próprio pertinente. | Renda de serviço/ativo ou margem ampla são candidatos, não adoção. Ativo baixo de intermediador não torna ROA comparável ao banco de crédito. | R/E; A341–342/G. |
| Qualidade dos ativos | Quais riscos de cliente/contraparte são assumidos pela operadora? | Q1/Q2 só no crédito próprio; LC contextualiza. | Conta-margem, garantias, contraparte e liquidação precisam de abertura específica; ativos em custódia de terceiros não viram carteira própria. | Q/L e específicos ausentes; A337/G. |
| Capital | Capital sustenta exposições próprias e operacionais? | C1 e prudencial pertinente. | C1 não mede risco dos ativos custodiados ou perdas operacionais; requerimento/limite específico exige regime e data. | C; A337/G. |
| Liquidez/financiamento | Recursos livres cobrem obrigações de liquidação/clientes? | LA/LF como composição; L2/L3 não são escolha padrão. | Outras Obrigações78297 agrega conceitos e não identifica saldo de clientes. Vinculação, margens e vencimentos precisam de contrato próprio. | L/X; A334–335/G. |
| Eficiência | Custos geram receita no negócio de intermediação/serviços? | E2-B, RS e E3 com advertência sobre base de ativos. | Melhor denominador pode exigir renda ampla ou volume de negócios/clientes; componentes78221–78223 permitem investigar o primeiro, volumes não foram admitidos. | E/X; A342/G. |

### N4 — instituições de pagamento, por modalidade e data

| Dimensão | Pergunta econômica | Comum e complementos aprovados | Adaptação/específico ainda necessário | Componentes/janela; fundamento |
|---|---|---|---|---|
| Rentabilidade | Qual retorno da operadora e de suas rendas financeiras/serviços? | R1/R2, RS; R4 parcial; R5 só com crédito próprio compatível no perímetro. | Rentabilidade não demonstra proteção do usuário. Modalidade e membros do grupo exigem conferência; não inferir carteira bancária de todo N4. | R/E; A341–342/IP. |
| Qualidade dos ativos | Quais perdas de contraparte/recebíveis/antecipação recaem sobre a unidade? | Q1/Q2 apenas na carteira com abrangência comprovada; LC é composição. | Identificar recebíveis e quem assume a perda. Não definir qualidade como zero porque CR=0. Não somar saldo de usuários ao crédito. | Q/L; A324/IP. |
| Capital | Capital próprio atende o suporte/requerimento da operadora? | C1 e prudencial somente se pertinente. | Salvaguarda não é PL. Requerimentos IP por modalidade/cronologia precisam de prova; PR de banco do grupo não preenche capital da IP. | C; A337/IP. |
| Liquidez/financiamento | Recursos elegíveis/vinculados cobrem obrigações de usuários/liquidação? | LA/LF são descritivos; LC não é medida suficiente. | Indicador específico de salvaguarda e cobertura por modalidade/horizonte é prioritário. Caixa/AIL não são automaticamente livres; DV não representa contas de pagamento. Componentes elegíveis/obrigações não foram demonstrados. | L e específicos; A334–335/IP. |
| Eficiência | Custo sustenta receita e serviço de pagamento prestado? | E2-B, RS/E3 com composição explícita. | Custo/volume e margem por transação seriam medidas específicas; volume e remuneração bruta/líquida ainda não conciliados. Não usar E3 isolado para ranking. | E/X; A342/IP. |

## Adaptações candidatas: o que pode usar a base e o que falta

Nenhuma linha abaixo acrescenta fórmula ao conjunto aprovado. São próximos recortes para decisão na [Issue3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3), com resultado verificável antes de eventual cálculo.

| Recorte prioritário | Hipótese a investigar | Evidência disponível e fronteira de resolução |
|---|---|---|
| N1/leasing | Qualidade/rendimento da carteira de arrendamento, em vez de impor CR. | Componentes X já existem:78194 descreve `[17000000]-[17900007]`,78195 imobilizado,78197 provisão,78198 combina contas/ajustes. Rendas78204 e despesas78211 são próprias. Não chamar78194 de carteira bruta sem conciliar sinal/abrangência; não somar CR+leasing automaticamente. Próximo produto: ficha QL/rendimento com fórmula, regra temporal e teste de abrangência, sem fonte financeira externa inicialmente. |
| N2/N4 e grupos diversificados | Custo/renda com denominador mais representativo que S. | DRE78221/78222/78223 estão localizadas. Resultado Operacional78225 já é líquido de várias despesas: usá-lo como receita duplicaria a lógica do custo. Próximo produto: conciliação das contas de renda/custo e alternativas E2 amplo; fonte adicional somente se a abertura local for insuficiente. |
| B3S/B3C | Exposição à centralização e colchão de liquidez do sistema. | AIL78189 e depósitos interfinanceiros78284 são agregados; não isolam livre/vinculado/filiadas. Próximo produto: mapa conceitual de obrigações e ativos elegíveis, mantendo singulares, centrais e bancos cooperativos separados. Sem criar índice sintético do sistema a partir de somas sem eliminações. |
| B4/N1-fomento | Cobertura temporal de desembolsos por funding institucional. | LF dá categorias gerais; FAT, restrições e cronograma não estão individualizados. Próximo produto: pergunta/horizonte de gap de caixa e identificação de fonte documental; não criar suposta liquidez substituindo DV por AT. Cumprimento de mandato é pergunta adicional, não obrigação de maximizar lucro. |
| N4 | Salvaguarda/obrigações de usuários por modalidade. | Sem bindings admitidos de recursos elegíveis, restrições e obrigação correspondente. Próximo produto: definir conceitos/modalidades e cronologia; só então decisão de fonte/indicador e eventual coleta autorizada. |
| B1/B2/N2 | Risco não coberto pela carteira tradicional. | CP/PR/RWA e provisões não medem cada exposição de mercado/contraparte. Próximo produto: verificar conceito/aplicabilidade de medida de contraparte, não reaproveitar Q1 por conveniência. |

**Não bloquear os sete aprovados por essas lacunas.** Implementá-los com o significado literal e avisos de adequação torna a análise mais informativa agora. A ausência de medida específica limita as conclusões daquela dimensão e daquele negócio; não invalida as outras dimensões ou a presença da companhia. A etapa C não deve ser descrita como pesquisa exaustiva de todos os subtipos e modalidades.

## Fontes, localizadores e leitura efetiva

| Chave | Fonte e localizador | Uso e estado da leitura nesta fatia |
|---|---|---|
| A | ASSAF NETO. *Estrutura e análise de balanços*,11.ed.,2015. Impressas334/PDF355,337/PDF358,342/PDF363; pp.324/335/341 na143/111. | Releitura visual efetiva de334/337/342, a partir das imagens autenticadas da143. PDF completo reautenticado SHA256 `d41dccd16d2a9c174fb95cd87e5d3abd0666f461514d8402594367cc913d367b`. Livro explica limitações da liquidez contábil, capital sem risco dos ativos, retorno/margem/eficiência bancária. Demais páginas são reaproveitadas da pesquisa, não nova leitura. Não atribuir LA/LF/RS/E3 literalmente ao livro, nem usar seu exemplo histórico como mínimo regulatório universal. |
| F | FMI.*Financial Soundness Indicators Compilation Guide2019*, edição final, pp.90–92,§§7.46–7.69; pp.58–59/§§5.90–5.93 e125/§§9.1–9.6. [PDF oficial](https://www.imf.org/-/media/files/data/2019/2019-fsi-guide.pdf). | Fundamento e localizadores reaproveitados da143, sem alegar releitura integral. O ROA preferido pelo guia é antes de tributos, diferente do LL adotado. Critérios de líquido/restrito e rendas não são automaticamente reproduzidos pelo nosso catálogo. |
| CO | BCB.*Panorama do SNCC*,data-base dezembro2024, pp.11 e24–26/boxe liquidez. [PDF oficial](https://www.bcb.gov.br/content/estabilidadefinanceira/coopcredpanorama/Panorama_Cooperativas_SNCC_FINAL_dez2024.pdf). BCB.*REB2022*,pp.39–43. [PDF](https://www.bcb.gov.br/content/publicacoes/relatorioeconomiabancaria/reb2022p.pdf). | Panorama aberto e seções citadas lidas em texto web nesta fatia: categorias das singulares e papel da centralização. Documento sobre2024 não prova estrutura/regra em2010. REB: benefício ao cooperado reaproveitado da143; sem nova apuração de benefícios. É necessária separação entre cooperativa de crédito, confederação de serviços e banco cooperativo; não imputar subtipo pelo nome. |
| BD | FERRAZ;ALÉM;MADEIRA.*A contribuição dos bancos de desenvolvimento para o financiamento de longo prazo*.Revista do BNDES40,2013,pp.30–31/35–37.[Original](https://web.bndes.gov.br/bib/jspui/bitstream/1408/1421/1/RB%2040_final-A.pdf). | Trecho da p.31 relido na extração autenticada da143: sustentabilidade e comparação de nichos. Restante reaproveitado. Autores distinguem retorno financeiro/mandato; não são norma nem demonstram causalidade. Não certifica agência/BNDES sob mesma regra. |
| NC | CMN.Res4656/2018,arts.3/6 e7–8,com alterações/revogações expressas.[PDF oficial compilado](https://normativos.bcb.gov.br/Lists/Normativos/Attachments/50579/Res_4656_v8_P.pdf). BCB.[SCFI](https://www.bcb.gov.br/estabilidadefinanceira/scfi). | Arts.3/6/7–8 relidos via web. Distinção histórica SCD/SEP justifica separar ativo próprio e operação entre terceiros. Arts.3/7 revogados desde1/1/2023; norma substituta5050 e alterações5177 precisam ser examinadas antes de regra operacional2023–2024. Não congelar descrição original de recursos próprios, pois art.6 já foi alterado em2020. SCFI reaproveitada da143. |
| G | BCB.[Corretoras e distribuidoras](https://www.bcb.gov.br/pre/composicao/corretoras_distribuidoras.asp?frame=1),seções de serviços e principais atividades. | Texto substantivo da página relido via busca web: conta própria, terceiros, serviços, conta-margem e custódia. Página histórica institucional não dá licença individual datada. PortalCVM aberto nesta fatia forneceu descrição curta de serviços, sem prova suficiente para a regra contábil de recursos de clientes. Res5008 localizada, mas abertura web retornou shellJavaScript: conteúdo não foi certificado nem usado como prova normativa. |
| IP | Brasil.Lei12865/2013,arts.6,12 e12-A–12-C.[Texto compilado oficial](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12865.htm). | Arts.6/12/12-A–12-C relidos via web; segregação patrimonial e liquidação motivam medida própria, sem fornecer fórmula/bindingIF.data. Alterações2020 identificadas; redações novas/revogadas da compilação não retroagem. Leitura não autoriza diagnóstico de conformidade das instituições. |

Esta é uma auditoria/revisão dirigida de evidências existentes, com poucas consultas primárias adicionais, não uma nova revisão sistemática. PDF privado do Assaf e staging não são publicados. Nenhum contrato de fonte financeira externa, SCR, CVM ou SUSEP foi aberto. A lista das referências já está na143; esta nota não altera REFERENCES ou o protocolo metodológico compartilhado.

## Aceite da fatia e implicação para a implementação

Escopo: um arquivo novo em `docs/engineering/`, responsabilidade já existente, sem nova camada/raiz, código, dados ou classificação. Base de implementação: branch `codex/ifdata-universe-analysis-20261014`,HEAD087700ccafa81ad96c963df62b633fb317d4ca21 mais delta preservado da152. Checkout principal foi somente leitura. Fontes e matrizes da143/148 não foram recalculadas.

Conferências documentais: 8Tcb×5dimensões; sete complementos mapeados; N1 desdobrado por negócio; componentes/tempo/fontes/limites e propostas separados. A revisão independente desta nota pertence ao checkpointC da152; o texto entregue não declara revisão concluída por antecipação. Estado efetivo, achados e hash revisado serão registrados naIssue/ledger responsável.

Para o explorador: mostrar fórmulas/nomes literais, natureza comum ou complementar, cobertura e advertência da família. Não ocultar unidade porque a métrica é inadequada nem convertê-la em resultado zero. Um aviso de N4 deve destacar salvaguarda não medida; B4, maturidade/financiamento institucional; B3C, centralização; N1, carteira e subtipo; N2, obrigações de clientes e contraparte. O mesmo cálculo pode continuar comparável contabilmente e ter alcance econômico diferente, o que precisa ficar visível.

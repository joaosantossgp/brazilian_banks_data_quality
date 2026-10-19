# Explorador dos indicadores por Tcb

Entrega da [Issue #193](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/193), dependente da [composição #192](tcb-indicators-delivery-20261018.md). **Candidato local gerado e piloto econômico/offline aprovado; inspeção visual e QA ampliada pendentes. Nenhum ponteiro promovido.** O explorador reutiliza exportador e template existentes, com valores persistidos do sistema IF.data observado inteiro de 2010–2024.

## Conteúdo e leitura

O conjunto reúne 27 IDs: os 20 anteriores e L1, PL_DEP, R3, RIF_AT, E2-W, E2-WP e QL. As sete novidades existem somente no Financeiro desta composição; Individual e Prudencial conservam seus próprios indicadores, unidades e perímetros. O seletor oferece somente os IDs efetivamente observados na perspectiva. E2-W é a medida ampliada principal; E2-WP permanece sensibilidade distinta.

A ficha do indicador apresenta nome, pergunta, fórmula, condição de uso, componentes, nomes nativos das variáveis, relatório/conta e fundamento com link. Descrições Cosif extensas ficam em detalhes expansíveis. As fontes conceituais não certificam o binding: contextos e períodos vêm dos perfis efetivamente consumidos, autenticados pelo manifesto do pacote correspondente. Contextos de definições diferentes de lucro permanecem separados. O quadro mostra a referência corrente; não demonstra sozinho disponibilidade da janela TTM ou continuidade de perímetro.

Comuns, condicionais e específicos são descrições econômicas, sem filtro automático de unidades por Tcb. QL pode atender recebíveis compatíveis fora de N1. Depósitos condicionam L1/L2/L3/PL_DEP; crédito próprio condiciona Q1/Q2/R5; capital exige o perímetro prudencial pertinente. Ausência, zero, nulo, negativo, histórico insuficiente e aplicabilidade desconhecida continuam estados distintos. A [matriz #192](tcb-indicators-delivery-20261018.md) documenta as lacunas das cinco dimensões por família de negócio.

Tcb e SegmentoTb orientam atividade e subtipo. Tc, Td e Sr contextualizam controle, consolidação e regime, sem criar uma fórmula por cruzamento. Sr original e SrAnalitico permanecem separados; Atividade não retorna aos filtros. O total contém as unidades vinculadas, restante e vínculo desconhecido. Companhias associadas à mesma unidade não multiplicam seus valores; a seleção nominal de 32 companhias fica dentro do registro diagnóstico de 55.

## Precisão e proveniência

O browser recompõe somas, distribuições e coberturas a partir das células conjuntas persistidas; não calcula novos indicadores financeiros. Frações exatas e componentes são conservados no payload e nos CSVs. A apresentação percentual arredonda somente a exibição. Estoques próprios conhecidos contextualizam instituições; não são balanços consolidados do SFN nem cobertura da atividade específica, especialmente leasing.

O denominador LF é a soma das quatro rubricas conciliadas. A rubrica nativa Captações aparece identificada como controle, sem fingir que substitui essa soma. RIF_AT recebe a mesma advertência de denominador médio das outras razões pertinentes. Provisão positiva de leasing mantém seu sinal e alerta próprio. QL não recebe interpretação de NPL ou de suficiência regulatória.

A ancestralidade da correção Terra atravessa o wrapper finito de retenção de proveniência da #192. O aviso qualifica os 16 resultados anteriores; nenhuma ponte é estendida aos sete indicadores novos. A evidência histórica de vínculos da fonte pinada conserva o aviso de Oliveira Trust, seus períodos e limites. O pacote macro anterior deve ser autenticado e preservado integralmente, sem coleta adicional ou inferência causal.

## Verificações e aceite

TDD pertinente cobre nomes/fórmulas, perspectivas observadas, integridade e épocas dos contextos, arquivo consumido e linhagem do perfil, ancestralidade com proteção contra ciclos, condições de adequação e montagem segura da ficha. Testes Node avaliam funções puras do template; isso não constitui inspeção visual ou operação de navegador.

Gates restantes: inspeção visual/operacional do piloto; reconciliação ampliada das células e CSVs com a composição, incluindo filtros combinados e preservação dos 20 anteriores; revisão final econômica/visual e do SHA, PR/CI e integração. A revisão de código/conceito, o piloto econômico/offline e a preservação macro já passaram. O HTML e o recibo devem usar destino privado novo. Nenhum dado, HTML privado ou original bibliográfico integra o Git.

A ferramenta de navegador disponível rejeitou URL local `file://` por política. A abertura no painel próprio foi somente enfileirada, sem renderização confirmada. Essa limitação não será contornada por servidor ou outro navegador; enquanto não houver inspeção permitida ou validação manual do artefato concreto, o gate visual permanece pendente. Não se descreve teste offline como aprovação visual.

A promoção de `current-indicators.json` só ocorrerá após aceite dos dados e do artefato. Deve preservar backup byte a byte, pins anteriores, metadados macro e política de migração explícita, validar os hashes por nova descoberta e não reutilizar o link Drive do artefato anterior. Upload, deploy e nova coleta não fazem parte desta entrega.

## Candidato de 19/10/2026

Após revisão independente estática e correção de uma comparação incorreta entre hashes de perfil de universo e de perfil legado, os 33 perfis reais foram autenticados. TDD: 12 testes pertinentes aprovados. A correção preserva separadamente as duas âncoras e os bytes do arquivo efetivamente consumido; não flexibiliza a validação.

A exportação terminou em 66,770 segundos, com 355.632 células conjuntas, 55 companhias no registro nominal e 1.476 registros macro. O HTML autocontido tem 117.547.129 bytes; SHA-256 `4ac82450bb68cd22ae471a01ca867e96e6ab47d7ca7a50bab4ff57427b2c33e7`. Recibo: `a431e82d2d0f03924a48da0b110989732a584fdd6353196245445b2736c18cf2`. Composição: `f374150e5d4c515f032fdf3fad3cb27b4e196486cee8d81c19150c39df45981b`; macro: `9920b6ebe130854130ab9ec7e7bfe98410556f22f81b969128be2704be8de118`.

A conferência estrutural validou hash, igualdade com o template aprovado, ausência de recursos externos carregados e sintaxe JavaScript. Isso não certifica operação, desempenho ou layout no navegador. O piloto econômico/offline selecionado é B1 com L1 e E2-W, e N1 com QL, em dezembro de 2024; a QA ampliada dos 27 IDs depende do gate do piloto.

O piloto econômico/offline passou por revisão independente: 106 células e 420 contribuições dos três casos; seis cenários e 15 reduções de coorte, incluindo filtros AND de Tc/Td/Sr, conferidos com aritmética racional. A função real de recomposição coincidiu com a redução independente, sem DOM. B1/L1 tem 88 elegíveis entre 97 presentes; B1/E2-W TTM, 95/97; N1/QL, 4/226, com duas companhias vinculadas esperadas e nenhuma elegível nesse último recorte. São contagens por caso, não instituições distintas somáveis.

Fichas, contextos, fontes e sinais desses casos conferem. O bloco macro de 1.476 observações e seus metadados é integralmente igual à entrada aceita e ao explorador anterior. Parecer do piloto: SHA-256 `fd0a35d27e9d7f58f5a6956d2edb6ce2bff6f86c5230a5ede886b274b723f7a4`. A execução do verificador levou 9,250 segundos. Não houve navegador, inspeção visual, acionamento de download CSV ou QA dos demais indicadores. A validação manual do arquivo concreto foi solicitada; ausência de resposta não constitui aprovação.

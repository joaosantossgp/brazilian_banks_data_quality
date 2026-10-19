# QL: proteção contábil dos recebíveis de arrendamento — 18/10/2026

Entrega da [Issue191](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/191), após a [conciliação183](tcb-leasing-reconciliation-20261018.md). João [adotou QL com limites expressos](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3#issuecomment-6258359846). O indicador foi implementado no motor existente e verificado no sistema Financeiro completo em201003/202412. Rendimento do leasing continua sem adoção, pois renda e ativos produtores não estão conciliados para essa pergunta.

## Indicador, fórmula e alcance

**QL — intensidade contábil da provisão sobre recebíveis de arrendamento**:

$$QL_t=100\frac{-P^{leasing}_t}{Recebíveis^{antes\ da\ provisão}_t}.$$

Financeiro Tipo2, mesma unidade e data, estoques em reais nativos:

| Papel | Relatório/ID | Definição literal |
|---|---|---|
|Provisão assinada|Ativo2/78197,grupo Arrendamento Mercantil|`[17900007]`|
|Recebíveis antes dessa provisão|Ativo2/78194,mesmo grupo|`[17000000]-[17900007]`|

O denominador exclui essa provisão, mas mantém outras retificadoras/rendas a apropriar que compõem170. Não é principal nominal dos contratos nem todos os ativos produtores da operação de leasing. Não inclui imobilizado78195,VRG78196ou o agregado líquido78198; somá-los alteraria o conceito. Crédito78191e seus indicadores próprios permanecem separados.

Fundamento: [conciliação183](tcb-leasing-reconciliation-20261018.md), incluindo a leitura da compilação históricaCosif2024,PDFpp31–32,função179, e manual de arrendamento§§10–11. A fórmula é uma adaptação descritiva própria, coerente com distinguir provisão e exposição; não é inadimplência, cobertura deNPLou teste de suficiência regulatória. Assaf Neto,11.ed.,2015,pp.321–322/324, leitura183 reaproveitada, ajuda a distinguir componentes patrimoniais/resultados, sem lhe atribuir a fórmulaQL ou um limite normativo. A norma de provisão baseada em valor presente não se reduz a esta razão contábil.

QL é pontual: não pede fluxo, média ou abertura histórica. Comparação/agregação exige o mesmo alcance, data e regime. Onde os recebíveis são positivos, há aplicabilidade técnica à pergunta contábil; isso não certifica adequação de um ranking de todos os negócios. Zero mantém razão indefinida e aplicabilidade desconhecida, sem declarar não aplicabilidade; null/ausente são próprios. Denominador negativo conserva fração assinada e `negative_denominator`, com aplicabilidade desconhecida. Provisão nativa positiva conserva sinal e alerta `positive_native_leasing_provision`, inclusive com denominador zero. Não foi adotado corte estatístico, imputação ou inversão por valor absoluto.

## Testes e piloto

TDD registrou duas falhas causais por métrica desconhecida e duas por bindings ausentes. Dois testes matemáticos cobrem denominador antes da provisão, exclusão deVRG/imobilizado/líquido, janela pontual, sinais, zero/null/ausente e perímetro. A revisão independente encontrou a perda do alerta com recebível zero; contraprovaRED e correçãoGREEN foram preservadas antes do piloto. A suíte seletiva passou38testes,40,907s; o revisor conferiu114comparações integrais idênticas das26métricas anteriores em três cenários. Dois bindings de estoque foram adicionados por contexto próprio, conferidos no catálogo nas60referências, preservando o perfilJSON instalado.

Novo destino privado `data/curated/tcb-piloto-leasing-20261018-run1-stock`, manifest `22e1cd910225ff2f02ec55f4a90fa1dc2a348de8df5af2dce36352a3716b9f6c`:9.717componentes e3.239resultados/coberturas, sem filtrar leasing paraN1. Contextos e tokens nativos foram integralmente conferidos pelo revisor;68razões com denominador não zero foram rederivadas exatamente comFraction.

| Data | Universo esperado | OK | Elegíveis | Denominador zero | Null |
|---|---:|---:|---:|---:|---:|
|201003|1.817|40|40|1.750|27|
|202412|1.422|28|27|1.387|7|

Em202412os27recebíveis positivos se distribuem em15B1,8B2e4N1. As quatroN1sãoLeasePlan,CSI Latina,CHG-Meridian eHP Financial Services, conforme nominal/cadastro; o nome não é critério de inclusão. O28ºresultadoOK é Banco Toyota do Brasil S.A.,código03215790, com recebível negativo: permanece assinado e fora da cobertura elegível, sem exclusão silenciosa do universo. Os zeros não provam licença ou inexistência de qualquer modalidade de leasing.

O nominal e40células de cobertura corrente preservam nomes/códigos/companhias, Tcb/SegmentoTb/Tc/Td/Sr/SrAnalitico, coortes e estados, AT/crédito/PL conhecidos/desconhecidos e somas exatas totais/elegíveis. Total inclui vinculadas, restante e vínculo desconhecido. Os vínculos persistidos no piloto continuam os do baseline técnico; o join diagnóstico usa a coorte corrente, e192fará a composição datada explicitamente. Não há mistura de razões diferentes em um agregado.

Pin corrente autenticado `d47a15746fc7b6cdaaa0c82cf511622e8bb8cd89386808682b57d6271a89bb60`; baseline técnico rastreado pela origem dos estoques `b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192`. Nenhum pacote aceito ou ponteiro foi alterado. Não houve expansão histórica, composição final ou mudança do explorador.

Root, branch `codex/tcb-research-182-188`, assunção apósf543396; quatro paths de motor/testes e esta nota, preparação `.scratch/tcb-piloto-leasing/`, sem nova camada/dependência. O revisor aprovou código corrigido antes do piloto e conferiu integralmente dados/cobertura antes de ampliar. Comandos, tempos, tentativas e hashes protegidos foram preservados; revisão da nota e SHA entregue acompanham a Issue. A próxima etapa é a composição seletiva192, mantendo o rendimento de leasing como lacuna delimitada, sem nova decisão rotineira sobreQL.

# Completude da seleção offline OData — 2026-10-12

Entrega da [Issue93](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/93), após a fatia documental92. Responsáveis existentes: `bank_quality/ifdata_odata.py` e `tests/test_ifdata_odata.py`; sem nova camada ou dependência, coleta ou alteração dos conjuntos aceitos.

## Contrato

- Cada período ou tipo explicitamente solicitado deve existir entre as entradas selecionadas do índice. Se ambos os filtros forem explícitos, exigir cada combinação período × tipo; o caller deve dividir pedidos com ofertas diferentes em seleções próprias.
- Eixos omitidos seguem a oferta capturada; não inferir produto cartesiano entre eixos implícitos.
- Cada relatório solicitado deve ser observado em cada contexto não vazio selecionado. Um contexto é o par período/tipo, reunindo suas páginas. Relatório ausente nesse recorte não é classificado como ausência estrutural: a conversão é recusada, indicando os contextos/IDs faltantes. Para investigar a oferta, importar sem filtro de relatório.
- Uma fonte `sem_dados` com páginas, hashes, contagens zero e corpo vazio válidos continua admissível. Ela prova zero linhas recuperadas naquele contexto, sem provar que um ID de relatório foi ofertado. Um filtro de relatórios precisa de evidência de seus IDs em pelo menos um contexto não vazio; um pacote totalmente vazio não basta para validar esse filtro.
- Erro não publica `manifest.json`; arquivos parciais ficam sem aceite. Ausência de período/tipo é detectada antes de reservar a saída. Retry exige destino novo quando houver saída parcial.

O schema/contrato dos dados e o reader não mudam: manifests anteriores continuam legíveis, sem atribuir retroativamente a eles a nova validação da seleção. Números nativos, null/zero, lexemas/Decimal e proveniência permanecem próprios. Não foi demonstrado truncamento do corpus entregue; as regressões são fixtures offline.

## Fatia e validação

1. RED: quatro testes novos, sete casos falhando por `ValueError not raised` antes da mudança, incluindo eixos incompletos, buracos do produto cartesiano, relatórios parcialmente presentes e ID desconhecido em fonte vazia.
2. GREEN: validar índice selecionado antes da escrita; observar os relatórios durante a autenticação/streaming de cada página; recusar faltas antes do manifest final. Nenhuma segunda leitura integral ou carregamento global do pacote.
3. Check: `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_ifdata_odata.py -v` — 11 testes PASS na implementação inicial; consumidores e revisão independente registrados na Issue antes da integração.

Revisão independente e CI têm autoridade na Issue/PR reais; este registro não afirma gates ainda pendentes como concluídos.

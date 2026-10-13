# Documentação da monografia: desenho aprovado

Decisão de João em 2026-10-13, [Issue 109](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/109). Base de revisão `f93d37f17898d69713d06f07bb393eb1f2444331`; branch `codex/monograph-docs-20261013`. Esta entrega é documental e independente da implementação da [Issue 108](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/108).

## Problema e público

README e AGENTS acumulam comandos, instruções e histórico; o contexto monográfico aparece tarde e algumas afirmações antigas se confundem com regras vigentes. O glossário tem definições úteis, mas pouca organização didática. A bibliografia está dispersa. README atenderá primeiro autor/orientador, com rotas próprias para consulta técnica e contribuição por agentes.

## Contexto acadêmico aprovado

Monografia de Ciências Econômicas/UNICAMP de João Victor Santos Gonçalves Pereira: desempenho econômico-financeiro de negócios financeiros ligados a companhias elegíveis CVM/B3. Núcleo 2010–2024; 2025–2026 complementar, sujeito às quebras e à comparabilidade. Interessa investigar evolução e possíveis explicações, com índice comparativo como objetivo ainda dependente de método.

Unidades principais: conglomerados financeiros e instituições independentes vinculados temporalmente às companhias elegíveis, com tipo explícito. Medição direta nesse nível; analisar cada subsidiária e agregar seus indicadores não é obrigação. Companhia, holding e conglomerado não são identidades intercambiáveis. Duas companhias vinculadas à mesma unidade não geram automaticamente duas observações independentes.

A perspectiva prudencial será considerada para indicadores e comparações pertinentes, especialmente capital/solidez, preservando perímetro, data e regime. Não significa excluir balanço/DRE prudenciais nem adotar automaticamente todos os seus indicadores. Individual permanece disponível para perguntas delimitadas. Não há escolha de indicador, peso, fórmula ou amostra final nesta entrega; [Issue 3](https://github.com/joaosantossgp/brazilian_banks_data_quality/issues/3) conserva as decisões restantes.

## Responsabilidade de cada entrada

| Documento | Responsabilidade |
|---|---|
| README | Propósito, percurso explicado por visual, entregas/limites datados e caminhos de leitura. |
| AGENTS | Contexto mínimo, autoridade corrente, sequência operacional, preservação, skills/revisão e encerramento. |
| GLOSSARY | Conceitos em português, agrupados por tema, com exemplos curtos; sem schema ou comandos. |
| REFERENCES | Bibliografia comentada: uso na pesquisa, localizador verificado, limites e estado de consulta/adoção. |
| Guia de consultas | Comandos existentes, contexto e diferenças entre rota OData e portal histórico. |
| Histórico operacional | Preservação das instruções antigas como evidência histórica sem autoridade corrente. |

Reusar architecture, workflow, tracker, pesquisas e diagramas existentes. O novo mapa mostra o percurso da monografia e a separação entre unidades/perímetros; visuais SVG/PNG embutidos com alternativa textual. Estilo claro diagram-design previamente escolhido.

## Arquivos e isolamento

Allowlist completa e fatias na Issue 109 e no [plano](../plans/2026-10-13-monograph-documentation.md). `REFERENCES.md` é nova entrada raiz explicitamente pedida por João; demais destinos reutilizam pastas existentes. `docs/architecture.md` recebe somente ajuste de destinos/responsabilidades, sem reescrever as seções que a 108 altera. Não editar dados/código/CI/contratos da 108 nem acessar outro computador.

Materiais autorais e PDFs privados do Drive são fontes de contexto; não copiar seus corpos para o Git público. Registrar bibliografia e sínteses próprias; links públicos primários quando disponíveis. O exemplar Assaf Neto foi localizado, mas o conector não extraiu seu conteúdo: edição/páginas do exemplar não serão anunciadas como verificadas. Fontes ainda não consultadas devem ser identificadas como candidatas.

## Aceite

- Propósito acadêmico aparece antes das ferramentas; comandos detalhados têm destino próprio.
- Unidades principais e papel prudencial ficam fiéis à decisão, sem ampliar a metodologia.
- Glossário distingue entidade/perímetro/tempo, ausência e desconhecido.
- Referências explicam o que sustentam e o que não sustentam, com lacunas estatísticas explícitas.
- Histórico e comandos preservados; âncoras locais existentes permanecem resolvíveis.
- Revisão independente por fatia antes da ampliação; links, escopo e visual conferidos; revisão final no SHA entregue.
- Publicação/integração e CI confirmados separadamente; não encerrar a 3 ou afirmar conclusão da 108.

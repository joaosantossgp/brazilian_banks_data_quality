# Brazilian bank data quality

The shared language for the IF.data pilot and the capital aberto thesis.

## Language

**Capital aberto**: A company's registration and securities context, assessed with dated CVM and B3 evidence. Registration alone does not prove equity listing at a historical date.

**Individual institution**: An IF.data reporting entity at the individual level. It is not interchangeable with a financial or prudential conglomerate.

**Reference quarter**: The reporting date identified by the source. It differs from the retrieval date and does not by itself define a result-flow window.

**Raw response**: The unmodified body returned by an official source, including unsuccessful responses.

**Structural absence**: A variable absent from a period's observed report structure. It is different from a reported cell with no value.

**Unobserved cell**: An institution-variable combination for which no observation was returned within an observed structure. It is not automatically NA, NI or zero.

**NA**: A source token retained separately from other missing-value states. Its meaning is interpreted only against the source's notes.

**NI**: A source token retained separately from NA, null and zero. Its meaning is interpreted only against the source's notes.

**Unknown**: A question not resolved by the available evidence. It is not a negative historical fact.

**Advertised availability**: A period or report listed by the official source. It does not establish successful acquisition, complete observations or historical universe membership.

**Observed cadastro coverage**: The relationship between identifiers in the registration snapshot actually retrieved and identifiers in the report actually retrieved. It is scoped to those sources and that reference date.

**Reporting window**: The interval over which a result-flow measure accumulates. A publication quarter and a result window can have different durations.

**Source vintage**: The source generation or revision version associated with retrieved information. It differs from the reporting date and retrieval time.

**Analytical unit**: The entity represented by each thesis observation, such as an individual regulated institution or a consolidated reporting unit. It is distinct from issuer eligibility and must be chosen explicitly.


**Financial conglomerate**: The IF.data financial consolidation perspective, whose perimeter is defined by the BCB for each reference date. It differs from the prudential perspective and does not establish identity with a listed issuer or holding.

**Prudential conglomerate**: The IF.data consolidation perspective with a prudential perimeter that can include entities outside the financial conglomerate. Its scope and historical availability must be assessed by reference date; it is not interchangeable with an individual institution or financial conglomerate.

**Reporting occurrence**: The representation of a reporting unit in a particular source perspective and reference, with its observed identifier and attributes. It does not establish identity with another period, perspective or listed issuer.

**Report variable binding**: The association between a position in an observed report and its source definition, identifiers, unit and reporting window. Equal labels or identifiers in different structures do not establish conceptual equivalence.

**Recovered publication set**: The source recoveries used together to interpret a specified reference, perspective and report. Their retrieval times may differ and do not establish a joint source vintage.

**Source revision**: A newly recovered version of previously published source material, retained alongside the earlier version. A difference in source bytes alone does not establish an economic change.

**Analytical cut**: A documented selection of references, reporting units, perspectives and source versions for a particular analytical purpose. Its eligibility and comparability rules are separate from the official observations.

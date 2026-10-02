"""Verify archived cadastro/table correspondence before any expansion financial GET."""
import json
from pathlib import Path
from urllib.parse import unquote
from bank_quality.archive import load_body
from bank_quality.coverage import audit_coverage, reporting_window

root=Path(__file__).resolve().parent.parent
collection=json.loads((root/'data/pilot-20261001.collection.json').read_text(encoding='utf-8'))
raw=root/collection['raw_directory']
profiles=[]
ignored_diagnostics=[]
for period in (201012,202412):
    candidates=[]
    for path in raw.glob('*.json'):
        try:item=json.loads(path.read_text(encoding='utf-8-sig'))
        except (ValueError,UnicodeError):
            if path.name not in ignored_diagnostics:ignored_diagnostics.append(path.name)
            continue
        if not isinstance(item,dict):continue
        if item.get('http_status')==200 and f'/cadastro{period}_1006.json' in unquote(item.get('url','')) and 'body_path' in item:
            candidates.append(item)
    if not candidates:raise RuntimeError(f'No archived official cadastro for {period}')
    manifest=candidates[-1]
    body=json.loads(load_body(manifest,raw))
    if not isinstance(body,list):raise ValueError('Unexpected cadastro JSON shape')
    index=collection['quarters'][str(period)]['portal_export_index']
    table=json.loads(load_body(index['state_manifest'],raw))
    code_column=next(i for i,col in enumerate(table['columns']) if col['ifd']==79706)
    ids={str(row[code_column]) for row in table['rows']}
    profile=audit_coverage(body,ids,period)
    profile.update(source_manifest=manifest,table_manifest=index['state_manifest'],
        result_window=reporting_window(period),raw_directory=str(raw.relative_to(root)))
    profiles.append(profile)
result={'quarters':profiles,'gate_passed':all(p['gate_passed'] for p in profiles),'ignored_nonmanifest_diagnostic_files':ignored_diagnostics,
    'limitation':'REST snapshot/table equality only; final capital-aberto unit/window and historical eligibility remain unresolved'}
output=root/'data/derived/expansion-20261001';output.mkdir(parents=True,exist_ok=True)
(output/'coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
text='# Cobertura observada: gate da expansão\n\n'
for p in profiles:
    text+=f"- {p['period']}: {p['distinct_identifiers']} códigos REST = {p['observed_table_identifiers']} códigos Resumo; gate {p['gate_passed']}. SHA cadastro `{p['source_manifest']['sha256']}`.\n"
text+='\nCorrespondência somente dos arquivos recuperados. OData indisponível no piloto; universo histórico e elegibilidade capital aberto não estabelecidos. Resultados em dezembro abrangem julho–dezembro; nenhuma transformação automática em Q4. Ausência de chave numérica direta não prova faltante em campo calculado/cadastral; preservar estados e a auditoria anterior.\n'
(root/'reports/expansion-20261001-coverage.md').write_text(text,encoding='utf-8')
print(json.dumps({'gate_passed':result['gate_passed'],'counts':{p['period']:p['distinct_identifiers'] for p in profiles}}))
if not result['gate_passed']:raise SystemExit(2)

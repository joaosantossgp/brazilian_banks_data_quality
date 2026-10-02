"""Independently compare accepted table cells with preserved official REST inputs."""
import json
from collections import Counter
from decimal import Decimal,InvalidOperation
from pathlib import Path
from bank_quality.archive import load_body
from bank_quality.inventory import _write,classify

raw=Path('data/raw/discovery-20261001');audit=[];summary={}
for period in (201012,202412):
    state=json.loads((raw/f'portal-state-{period}.utf8-capture.json').read_bytes())
    manifest=json.loads(next(raw.glob(f'*portal_numeric_input_{period}_1*.json')).read_text(encoding='utf-8'))
    source=json.loads(load_body(manifest,raw),parse_float=str)
    values={str(entry['e']):{str(cell['i']):cell['v'] for cell in entry['v']} for entry in source['values']}
    infos={info['id']:info['n'] for info in state['infos']}
    code_index=next(i for i,col in enumerate(state['columns']) if infos[col['ifd']]=='Código')
    counts=Counter()
    for row in state['rows']:
        code=str(row[code_index]);entity=values.get(code)
        for index,col in enumerate(state['columns']):
            if col['fid'] not in {2,3,4,5,6,7,10,11,12,13}:continue
            key=str(col['ifd']);table=row[index]
            present=entity is not None and key in entity
            actual=entity[key] if present else None
            equal=(actual==table)
            if present and not equal:
                try:equal=Decimal(str(actual))==Decimal(str(table))
                except InvalidOperation:pass
            relation='exact_direct_source_token' if equal and present else 'not_stored_at_report_definition_key' if not present else 'different_direct_source_value'
            if relation=='different_direct_source_value': raise ValueError(f'Raw/table direct-value mismatch: {period} {code} {key}')
            counts[relation]+=1
            audit.append({'period':period,'institution_id':code,'account':'portal_ifd:'+key,
                'direct_numeric_key_present':present,'direct_numeric_raw_value':actual,'direct_numeric_value_state':classify(actual) if present else 'unknown_computed_or_registration_field_or_not_reported',
                'portal_raw_value':table,'portal_value_state':classify(table),'relation':relation,
                'source_body':manifest['body_path'],'source_sha256':manifest['sha256']})
    summary[str(period)]=dict(counts)
output=Path('data/derived/pilot-20261001')
_write(output/'upstream-cell-audit.csv',audit,list(audit[0]))
(output/'upstream-cell-audit.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))

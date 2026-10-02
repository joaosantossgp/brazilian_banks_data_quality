"""Source-token-preserving inventory; no imputation or financial aggregation."""

import csv
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


def classify(value: object) -> str:
    if value is None:
        return 'json_null'
    token = str(value).strip()
    if token == '':
        return 'blank'
    if token in {'NA', 'NI'}:
        return token
    if token in {'NA%', 'NI%'}:
        return token[:2] + '_percent'
    if token.lower() == 'null':
        return 'literal_null'
    try:
        number = Decimal(token)
        if not number.is_finite():
            return 'invalid'
        return 'zero' if number == 0 else 'numeric'
    except InvalidOperation:
        return 'invalid'


def _write(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open('w', newline='', encoding='utf-8-sig') as output:
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def _key(row: dict) -> tuple[str, ...]:
    return tuple(str(row.get(field, '')) for field in ('NomeRelatorio', 'Conta', 'NomeColuna', 'Grupo'))


def inventory(quarters: dict, output: Path) -> dict:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    structures = {period: {_key(row) for row in quarter['values']} for period, quarter in quarters.items() if quarter['values_complete']}
    union = set().union(*structures.values()) if structures else set()
    observations, institutions, variables, missingness, structural, duplicates = [], [], [], [], [], []
    result = {'quarters': {}, 'classification': 'Raw source tokens; no imputation, aggregation or identity mapping', 'structural_comparison_complete': all(q['values_complete'] for q in quarters.values())}
    for period, quarter in quarters.items():
        rows = quarter['values']
        ids = {str(row['CodInst']) for row in rows}
        keys = structures.get(period, {_key(row) for row in rows})
        cells = Counter((str(row['CodInst']), _key(row)) for row in rows)
        states = Counter(classify(row.get('Saldo')) for row in rows)
        names = {str(row['CodInst']): row.get('NomeInstituicao', '') for row in quarter.get('cadastro', [])}
        complete = quarter['values_complete']
        unobserved = len(ids) * len(keys) - len(cells) if complete else None
        absent = len(union - keys) if complete and result['structural_comparison_complete'] else None
        result['quarters'][period] = {'values_complete': complete, 'cadastro_complete': quarter.get('cadastro_complete', False),
            'source_mode': quarter.get('source_mode', 'unknown'), 'observations': len(rows), 'institutions': len(ids),
            'variables': len(keys), 'observed_unique_cells': len(cells), 'expected_cells_within_observed_population': len(ids)*len(keys) if complete else None,
            'unobserved_cells': unobserved, 'structurally_absent_variables': absent, 'duplicate_extra_rows': sum(n-1 for n in cells.values()), 'value_states': dict(states)}
        for index, row in enumerate(rows):
            observations.append({'period': period, 'source_row': index + 1, 'institution_id': str(row['CodInst']),
                'report': row.get('NomeRelatorio'), 'account': str(row.get('Conta','')), 'variable': row.get('NomeColuna'), 'group': row.get('Grupo',''),
                'raw_value': '' if row.get('Saldo') is None else str(row['Saldo']), 'value_state': classify(row.get('Saldo')),
                'unit': row.get('_unit', 'source_odata_unit_not_assumed'), 'source_mode': quarter.get('source_mode','unknown'),
                'source_body': row.get('_source_body',''), 'source_sha256': row.get('_source_sha256',''),
                'csv_token':row.get('_csv_token',''), 'csv_body':row.get('_csv_body',''), 'csv_sha256':row.get('_csv_sha256','')})
        for identifier in sorted(ids):
            institutions.append({'period':period,'institution_id':identifier,'name':names.get(identifier,''),
                'name_state':'observed' if names.get(identifier) else 'unknown','identifier_namespace':quarter.get('identifier_namespace','odata_CodInst'),
                'observations':sum(1 for row in rows if str(row['CodInst'])==identifier)})
        for key in sorted(keys):
            variable_rows = [row for row in rows if _key(row)==key]
            counts = Counter(classify(row.get('Saldo')) for row in variable_rows)
            definition = dict(zip(('report','account','variable','group'),key))
            variables.append({'period':period,**definition,'observed_rows':len(variable_rows),'observed_institutions':len({str(row['CodInst']) for row in variable_rows})})
            for state, count in sorted(counts.items()):
                missingness.append({'period':period,**definition,'state':state,'count':count,'denominator_observed_rows':len(variable_rows)})
        if complete and result['structural_comparison_complete']:
            for key in sorted(union):
                structural.append({'period':period,**dict(zip(('report','account','variable','group'),key)),
                    'structural_state':'observed_variable' if key in keys else 'structurally_absent_from_observed_report'})
        for (identifier,key),count in sorted(cells.items()):
            if count>1: duplicates.append({'period':period,'institution_id':identifier,**dict(zip(('report','account','variable','group'),key)),'rows':count})
    _write(output/'observations.csv', observations, ['period','source_row','institution_id','report','account','variable','group','raw_value','value_state','unit','source_mode','source_body','source_sha256','csv_token','csv_body','csv_sha256'])
    _write(output/'institutions.csv', institutions, ['period','institution_id','name','name_state','identifier_namespace','observations'])
    _write(output/'variables.csv', variables, ['period','report','account','variable','group','observed_rows','observed_institutions'])
    _write(output/'missingness.csv', missingness, ['period','report','account','variable','group','state','count','denominator_observed_rows'])
    _write(output/'structural-presence.csv', structural, ['period','report','account','variable','group','structural_state'])
    _write(output/'duplicates.csv', duplicates, ['period','institution_id','report','account','variable','group','rows'])
    (output/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

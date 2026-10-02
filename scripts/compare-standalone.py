"""Accept fresh standalone exports and compare them to the original validated CLI capture."""
import csv
import json
from pathlib import Path
from bank_quality.archive import load_body
from bank_quality.portal import accept_export
from bank_quality.inventory import inventory

raw=Path('data/raw/standalone-validation-20261001')
original=json.loads(Path('data/pilot-20261001.collection.json').read_text(encoding='utf-8'))
quarters={};summary={}
fields=('AnoMes','TipoInstituicao','CodInst','Conta','NomeColuna','Saldo','NomeRelatorio','Grupo','_csv_token','_unit','_portal_row','_format_id')
for period in (201012,202412):
    paths=sorted(raw.glob(f'portal-export-{period}-*.json'))
    if len(paths)!=1:raise ValueError('Expected exactly one completed standalone export per quarter')
    index=json.loads(paths[0].read_text(encoding='utf-8'))
    quarter=accept_export(index,raw,period);quarters[str(period)]=quarter
    expected=original['quarters'][str(period)]['values']
    actual=quarter['values']
    projection=lambda rows:[tuple(row.get(field) for field in fields) for row in rows]
    if projection(actual)!=projection(expected):raise ValueError('Accepted source rows differ: '+str(period))
    old_index=original['quarters'][str(period)]['portal_export_index']
    csv_equal=load_body(index['csv_manifest'],raw)==load_body(old_index['csv_manifest'],Path(original['raw_directory']))
    summary[str(period)]={'observations':len(actual),'institutions':len({row['CodInst'] for row in actual}),
        'all_semantic_source_fields_identical':True,'official_csv_byte_identical':csv_equal,
        'archived_manifests_verified':len(index['manifests']),'export_index':str(paths[0])}
output=Path('data/derived/standalone-validation-20261001');output.mkdir(parents=True,exist_ok=True)
result=inventory(quarters,output)
expected_inventory=json.loads(Path('data/derived/pilot-20261001/inventory.json').read_text(encoding='utf-8'))
if result!=expected_inventory:raise ValueError('Inventory summary differs')
unchanged=[]
for filename in ('institutions.csv','variables.csv','missingness.csv','structural-presence.csv','duplicates.csv','inventory.json'):
    if (output/filename).read_bytes()!=Path('data/derived/pilot-20261001',filename).read_bytes():raise ValueError('Derived file differs: '+filename)
    unchanged.append(filename)
summary['inventory_byte_identical_files']=unchanged
summary['observation_provenance_difference']='Fresh immutable source paths/hashes change; every semantic row field and CSV token matches.'
collection={'periods':[201012,202412],'institution_type':3,'report_name':'Resumo','raw_directory':str(raw),'quarters':quarters}
(output/'collection.json').write_text(json.dumps(collection,ensure_ascii=False,indent=2),encoding='utf-8')
Path('reports/standalone-validation-20261001.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))

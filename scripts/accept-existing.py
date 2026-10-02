"""One-time acceptance of the already downloaded official exports; no extraction."""
import json
from datetime import datetime, timezone
from pathlib import Path
from bank_quality.archive import preserve_generated, load_body
from bank_quality.portal import accept_export

raw=Path('data/raw/discovery-20261001')
quarters={}
for period in (201012,202412):
    index_path=raw/f'portal-{period}.accepted.json'
    if index_path.exists():
        index=json.loads(index_path.read_text(encoding='utf-8'))
    else:
        items=[]
        for filename,kind in ((f'portal-state-{period}.utf8-capture.json','portal_table_state'),(f'portal-summary-{period}.original.csv','official_portal_csv')):
            path=raw/filename
            captured=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()
            items.append(preserve_generated(path.read_bytes(),raw,f'accepted_{period}_{kind}',
                f'https://www3.bcb.gov.br/ifdata/index2024.html?dt={period}',kind,
                {'period':period,'original_filename':filename,'captured_at_utc':captured,
                 'capture_clock_note':'Original saved-file timestamp; archival time is recorded separately.'}))
        index={'period':period,'complete':True,'state_manifest':items[0],'csv_manifest':items[1]}
        accept_export(index,raw,period)
        with index_path.open('x',encoding='utf-8') as out: json.dump(index,out,ensure_ascii=False,indent=2)
    quarters[str(period)]=accept_export(index,raw,period)
    print(period,len(quarters[str(period)]['values']),quarters[str(period)]['csv_table_disagreements'])
evidence=[]
for path in raw.glob('*.json'):
    try: item=json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError,UnicodeError): continue  # Retain failed diagnostic captures, never accept them.
    if isinstance(item,dict) and 'body_path' in item and 'sha256' in item:
        load_body(item,raw)
        evidence.append(item)
destination=Path('data/pilot-20261001.collection.json')
if not destination.exists():
    with destination.open('x',encoding='utf-8') as out:
        json.dump({'periods':[201012,202412],'institution_type':3,'report_name':'Resumo',
                   'raw_directory':str(raw),'quarters':quarters,'evidence_manifests':evidence},out,ensure_ascii=False,indent=2)
print('COLLECTION',destination,'VERIFIED_MANIFESTS',len(evidence))

"""Six temporal metadata checks; no financial collection or IF.data issuer mapping."""
import csv
import io
import json
from datetime import datetime
from pathlib import Path
from bank_quality.archive import load_body
from bank_quality.metadata import temporal_registration
from bank_quality.inventory import _write

raw=Path('data/raw/discovery-20261001')
cvm_manifest=json.loads(next(raw.glob('*cvm_cadastro*.json')).read_text(encoding='utf-8'))
body=load_body(cvm_manifest,raw)
try: text=body.decode('utf-8-sig')
except UnicodeError: text=body.decode('latin-1')
registrations={str(row['CD_CVM']):row for row in csv.DictReader(io.StringIO(text),delimiter=';')}
issuers={}
for path in sorted(raw.glob('*b3_current_metadata*.json')):
    manifest=json.loads(path.read_text(encoding='utf-8'))
    data=json.loads(load_body(manifest,raw))
    for item in data['results']:
        code=str(item['codeCVM'])
        if code in {'1023','906','19348'}: issuers[code]=(item,manifest)
rows=[]
for code,label in (('1023','Banco do Brasil'),('906','Bradesco'),('19348','Itau Unibanco Holding')):
    current=registrations.get(code)
    if not current or code not in issuers: raise ValueError('Required evidence missing: '+code)
    issuer,manifest=issuers[code]
    for period,date in ((201012,'2010-12-31'),(202412,'2024-12-31')):
        result=temporal_registration(current,date)
        try:
            event=datetime.strptime(issuer['dateListing'],'%d/%m/%Y').date()
            relation='on_or_before_reference' if event.isoformat()<=date else 'after_reference'
        except (ValueError,KeyError,TypeError): relation='unknown'
        rows.append({'period':period,'reference_date':date,'entity':label,'cvm_code':code,
            'cvm_cnpj':current['CNPJ_CIA'],'b3_cnpj_raw':issuer.get('cnpj',''),
            **result,'b3_issuer_prefix':issuer.get('issuingCompany',''),'b3_current_type':issuer.get('type',''),
            'b3_reported_listing_date':issuer.get('dateListing',''),'listing_event_relation':relation,
            'historical_equity_listing_state':'unknown','historical_equity_tickers':'unknown',
            'ifdata_entity_or_conglomerate_mapping':'unknown_not_attempted',
            'cvm_url':cvm_manifest['url'],'cvm_sha256':cvm_manifest['sha256'],'cvm_body':cvm_manifest['body_path'],
            'b3_url':manifest['url'],'b3_sha256':manifest['sha256'],'b3_body':manifest['body_path'],
            'retrieved_at_utc':manifest['retrieved_at_utc'],
            'listing_limitation':'Listing-event date reported by current official B3 metadata; does not prove uninterrupted historical equity listing. Join uses observed exact CVM code; no guessed CNPJ padding.'})
output=Path('data/derived/pilot-20261001/temporal-metadata-sample.csv')
_write(output,rows,list(rows[0]))
print('TEMPORAL_SAMPLE',len(rows),'ALL_HISTORICAL_STATES_UNKNOWN',output)

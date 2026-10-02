"""Archive only numeric-area inputs needed by the two accepted summary tables."""
import json
from pathlib import Path
from urllib.parse import urlencode
from bank_quality.archive import fetch,load_body
raw=Path('data/raw/discovery-20261001')
catalog_manifest=json.loads(next(raw.glob('*portal_catalog_retry*.json')).read_text(encoding='utf-8'))
catalog=json.loads(load_body(catalog_manifest,raw))
existing=[]
for path in raw.glob('*.json'):
    try: item=json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError,UnicodeError): continue
    if isinstance(item,dict) and 'body_path' in item: existing.append(item)
for period in (201012,202412):
    state=json.loads((raw/f'portal-state-{period}.utf8-capture.json').read_bytes())
    used={col['ifd'] for col in state['columns'] if col['fid'] in {2,3,4,5,6,7,10,11,12,13}}
    areas={info['a'] for info in state['infos'] if info['id'] in used and info.get('a',0)>0}
    entry=next(entry for entry in catalog if entry['dt']==period)
    for area in sorted(areas):
        name=f'ifdata/{period}/dados{period}_{area}.json'
        if not any(item['f']==name for item in entry['files']): raise ValueError('Input is not in official catalog')
        url='https://www3.bcb.gov.br/ifdata/rest/arquivos?'+urlencode({'nomeArquivo':name})
        accepted=next((m for m in existing if m.get('url')==url and m.get('http_status')==200),None)
        if accepted: load_body(accepted,raw)
        else:
            accepted=fetch(url,raw,f'portal_numeric_input_{period}_{area}',{'period':period,'purpose':'Underlying raw input for accepted individual Resumo; shared shard may contain other reports'},timeout=55)
            if accepted['outcome']!='ok': raise RuntimeError('Required raw input unavailable: '+url)
        print('NUMERIC_INPUT',period,area,accepted['http_status'],accepted['bytes'],accepted['sha256'])

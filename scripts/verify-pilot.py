"""Verify all original archived manifests and byte-identical offline regeneration."""
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
from bank_quality.archive import load_body
from bank_quality.replay import replay

raw=Path('data/raw/discovery-20261001');evidence=[];diagnostic_files=[]
for path in sorted(raw.glob('*.json')):
    try: item=json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError,UnicodeError): diagnostic_files.append(path.name);continue
    if isinstance(item,dict) and 'body_path' in item and 'sha256' in item:
        body=load_body(item,raw)
        if len(body)!=item['bytes']: raise ValueError('Byte-count mismatch: '+path.name)
        evidence.append(item)
collection=Path('data/pilot-20261001.collection.json')
data=json.loads(collection.read_text(encoding='utf-8'));data['evidence_manifests']=evidence
collection.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
source=Path('data/derived/pilot-20261001')
output=Path('data/derived/verification-replay')
result=replay(collection,output)
files=['observations.csv','institutions.csv','variables.csv','missingness.csv','structural-presence.csv','duplicates.csv','inventory.json']
hashes={}
for name in files:
    original=(source/name).read_bytes();rebuilt=(output/name).read_bytes()
    if original!=rebuilt: raise ValueError('Replay mismatch: '+name)
    hashes[name]=hashlib.sha256(original).hexdigest()
skills=json.loads(Path('third_party/mattpocock-skills/provenance.json').read_text(encoding='utf-8-sig'))
for item in skills['files']:
    if hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()!=item['sha256']:
        raise ValueError('Skill changed: '+item['path'])
actual=sorted(p.name for p in Path('.agents/skills').iterdir() if p.is_dir())
if actual!=sorted(skills['selected']):raise ValueError('Skill selection differs')
verification={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'raw_manifests_verified':len(evidence),
    'failed_diagnostic_captures_retained':diagnostic_files,'replay_byte_identical_files':hashes,
    'skill_files_verified':len(skills['files']),'active_matt_skills':actual,'inventory':result}
Path('reports/pilot-20261001.verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'raw_manifests_verified':len(evidence),'replay_byte_identical_files':len(files),'skill_files_verified':len(skills['files']),'active_matt_skills':actual}))

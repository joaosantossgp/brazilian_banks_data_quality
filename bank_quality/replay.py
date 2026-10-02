"""Offline deterministic regeneration from hash-verified accepted evidence."""
import json
from pathlib import Path
from .archive import load_body
from .portal import accept_export
from .inventory import inventory

def replay(collection_path: Path, output: Path) -> dict:
    collection=json.loads(Path(collection_path).read_text(encoding='utf-8'))
    from .ifdata import APPROVED_PERIODS
    periods=collection['periods']
    if not periods or len(set(periods))!=len(periods) or any(p not in APPROVED_PERIODS for p in periods) or set(collection['quarters']) != {str(p) for p in periods}:
        raise ValueError('Collection is outside the explicit approved quarter scope')
    raw=Path(collection['raw_directory'])
    for manifest in collection.get('evidence_manifests',[]): load_body(manifest,raw)
    quarters={}
    for period,quarter in collection['quarters'].items():
        raw=Path(quarter.get('raw_directory',collection['raw_directory']))
        for manifest in quarter.get('evidence_manifests',[]):load_body(manifest,raw)
        if quarter.get('source_mode')=='official_portal_csv_fallback':
            quarters[period]=accept_export(quarter['portal_export_index'],raw,int(period))
        else:
            from .ifdata import parse_odata, safe_next_link
            rebuilt={}
            for name,source in quarter.get('sources',{}).items():
                rows=[]
                successful=[]
                for manifest in source.get('manifests',[]):
                    body=load_body(manifest,raw)
                    if manifest.get('http_status')==200 and manifest.get('outcome')=='ok':
                        values,link=parse_odata(body)
                        successful.append((manifest,link))
                        rows.extend({**row,'_source_body':manifest['body_path'],'_source_sha256':manifest['sha256']} for row in values)
                if source.get('complete'):
                    if not successful or successful[-1][1] is not None:
                        raise ValueError('Complete source lacks a valid terminated archived page chain')
                    seen=set()
                    for position,(manifest,link) in enumerate(successful):
                        if manifest['url'] in seen: raise ValueError('Repeated successful source page')
                        seen.add(manifest['url'])
                        if position < len(successful)-1 and (link is None or safe_next_link(link,manifest['url']) != successful[position+1][0]['url']):
                            raise ValueError('Archived source page chain is incomplete or inconsistent')
                rebuilt[name]=rows if source.get('complete') else []
            if not quarter['values_complete']: raise ValueError('Cannot replay an incomplete quarter as a completed pilot')
            if not quarter.get('sources',{}).get('values_odata',{}).get('complete'):
                raise ValueError('Complete quarter lacks a completed value source')
            from .ifdata import validate_values
            quarter={**quarter,'values':rebuilt.get('values_odata',[]),'cadastro':rebuilt.get('cadastro_odata',[])}
            validate_values(quarter['values'],int(period))
            quarters[period]=quarter
    return inventory(quarters,Path(output))

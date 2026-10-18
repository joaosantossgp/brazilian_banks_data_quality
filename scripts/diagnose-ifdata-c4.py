"""Read-only C4 provenance diagnosis, 2017 comparison and complete 2018-2024 window."""
import argparse, csv, gzip, hashlib, json, sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
from time import perf_counter
import duckdb

BASE_PIN='b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192'
SR_PIN='a8e09826ec1b50becab01a844fa4954762a71a6fdfd60b245be53ebce372a3be'
ACCOUNTS={'CP':'79645','RWA':'79665','PR':'79649','ICP':'79659','NI':'79647','CC':'79646','NII':'79648','IB':'79664'}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def equivalent(a,b):
    return (a is None and b is None) or (a is not None and b is not None and Decimal(str(a))==Decimal(str(b)))

def main(root,raw,output):
    t=perf_counter();root=Path(root).resolve();raw=Path(raw).resolve();out=Path(output).resolve()
    if out.exists():raise FileExistsError(out)
    for p in (root/'ifdata-universe-analysis-20261014-final-run3',root/'ifdata-odata-20261011',root/'ifdata-sr-links-20261016-run2',raw):
        if out==p or out in p.parents or p in out.parents:raise ValueError('Output overlaps inputs')
    inputs=[]
    def auth(p,pin):
        assert sha(p)==pin,str(p)
        inputs.append(dict(path=str(p),sha256=pin))
    base=root/'ifdata-universe-analysis-20261014-final-run3'
    auth(base/'manifest.json',BASE_PIN);bm=json.loads((base/'manifest.json').read_text(encoding='utf8'))
    for f in ('components.parquet','results.parquet','unit_periods.parquet'):
        auth(base/f,next(e['sha256'] for e in bm['files'] if e['file']==f))
    cap=root/'ifdata-odata-20261011/capital'
    auth(cap/'manifest.json',bm['inputs']['capital']['expected_manifest_sha256'])
    cm=json.loads((cap/'manifest.json').read_text(encoding='utf8'))
    sr=root/'ifdata-sr-links-20261016-run2';auth(sr/'manifest.json',SR_PIN)
    sm=json.loads((sr/'manifest.json').read_text(encoding='utf8'))
    auth(sr/'attributes.parquet',next(e['sha256'] for e in sm['files'] if e['file']=='attributes.parquet'))
    parts=[e for e in cm['files'] if '201703'<=str(e['period'])<='202412']
    assert len(parts)==32
    native={}; raw_checked=0; definitions=Counter()
    for e in parts:
        auth(cap/e['file'],e['sha256'])
        rp=raw/Path(e['source_file'].replace('\\','/'));auth(rp,e['source_sha256'])
        body=json.loads(gzip.decompress(rp.read_bytes()),parse_float=Decimal,parse_int=Decimal)
        source=body['value']
        with duckdb.connect() as c:
            records=c.execute('select * from read_parquet(?)',[str(cap/e['file'])]).fetchall()
            cols=[v[0] for v in c.description]
        assert len(records)==e['rows']
        raw_cap=[x for x in source if str(x['NumeroRelatorio'])=='5']
        assert len(raw_cap)==len(records)
        seen=set()
        for values in records:
            n=dict(zip(cols,values));idx=int(n['source_row'])-1
            assert idx<len(source)
            original=source[idx]
            # source_row records the one-based position in the raw value array.
            for key in ('TipoInstituicao','CodInst','AnoMes','NomeRelatorio','NumeroRelatorio','Grupo','Conta','NomeColuna','DescricaoColuna'):
                val=original.get(key)
                assert n[key]==(None if val is None else str(val)),(e['period'],idx,key)
            assert equivalent(n['Saldo'],original.get('Saldo'))
            assert n['source_sha256']==e['source_sha256']
            k=(n['AnoMes'],n['CodInst'],n['Conta']);assert k not in seen;seen.add(k)
            native[k]=n
            definitions[(n['Conta'],n['NomeColuna'],n['DescricaoColuna'])]+=1
            raw_checked+=1
        print('authenticated',e['period'],len(records),flush=True)
    c=duckdb.connect(config={'threads':2,'memory_limit':'1GB'})
    filt="dataset='capital' and period between '201703' and '202412'"
    units={(p,k):json.loads(v) for p,k,v in c.execute(f'select period,code,payload from read_parquet(?) where {filt}',[str(base/'unit_periods.parquet')]).fetchall()}
    attrs={(p,k):(a,b,method,status) for p,k,a,b,method,status in c.execute(f'select period,code,sr_original,sr_analitico,method,status from read_parquet(?) where {filt}',[str(sr/'attributes.parquet')]).fetchall()}
    results={(p,k):json.loads(v) for p,k,v in c.execute(f"select period,code,payload from read_parquet(?) where {filt} and metric='C4' and horizon='point'",[str(base/'results.parquet')]).fetchall()}
    components={}
    for p,k,v in c.execute(f'select period,code,payload from read_parquet(?) where {filt}',[str(base/'components.parquet')]).fetchall():
        x=json.loads(v)
        if x['component'] not in ('CP','RWA','PR','ICP_published_diagnostic'):continue
        key=(p,k,x['component']);assert key not in components;components[key]=x
    c.close()
    assert set(units)==set(results)==set(attrs)
    rows=[];component_checks=0;result_checks=0
    for (period,code),u in sorted(units.items()):
        r=results[(period,code)];a=attrs[(period,code)];cl=u['classifications'] or {}
        row=dict(period=period,code=code,name=cl.get('NomeInstituicao'),Tcb=cl.get('Tcb'),Td=cl.get('Td'),Sr=a[0],SrAnalitico=a[1],sr_method=a[2],SegmentoTb=cl.get('SegmentoTb'),membership=u['membership'],companies=';'.join(str(x) for x in u.get('companies',[])),result_status=r['status'])
        for comp,account in ACCOUNTS.items():
            n=native.get((period,code,account))
            row[comp]=None if n is None else n['Saldo']
            row[comp+'_source_state']='missing' if n is None else ('null' if n['Saldo'] is None else 'observed')
            mapped='ICP_published_diagnostic' if comp=='ICP' else comp
            if mapped not in ('CP','RWA','PR','ICP_published_diagnostic'):continue
            x=components[(period,code,mapped)]
            assert n is not None and x['status']=='ok'
            assert equivalent(x['token'],n['Saldo'])
            assert x['sources'][0]['source_sha256']==n['source_sha256']
            component_checks+=1
        cp=row['CP'];rwa=row['RWA']
        expected='native_null' if cp is None or rwa is None else ('zero_denominator' if Decimal(rwa)==0 else 'ok')
        assert r['status']==expected,(period,code,r['status'],expected)
        for comp in ('CP','RWA'):
            rv=r['components'][comp]['value_fraction'];token=row[comp]
            if token is None:assert rv is None
            else:assert Decimal(rv['numerator'])==Decimal(token)*Decimal(rv['denominator'])
        result_checks+=1
        row['diagnostic_class']='source_null_CP' if cp is None else ('source_null_RWA' if rwa is None else ('source_zero_RWA' if Decimal(rwa)==0 else 'eligible'))
        row['regime_candidate']='S5_source_null_CP' if cp is None and a[1]=='S5' else ('other_source_null_CP' if cp is None else 'not_CP_gap')
        rows.append(row)
    out.mkdir()
    def write(name,rr):
        with (out/(name+'.csv')).open('w',encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    write('unit_diagnosis',rows)
    def grouped(fields):
        counts=Counter(tuple(r.get(f) for f in fields) for r in rows)
        return [dict(zip(fields,k),unit_periods=n) for k,n in sorted(counts.items(),key=lambda x:repr(x[0]))]
    write('period_coverage',grouped(['period','result_status','diagnostic_class']))
    write('segment_coverage',grouped(['period','Sr','SrAnalitico','Tcb','result_status','regime_candidate']))
    write('source_definitions',[dict(Conta=k[0],NomeColuna=k[1],DescricaoColuna=k[2],rows=n) for k,n in definitions.items()])
    transitions=[]
    lookup={(r['period'],r['code']):r for r in rows}
    for r in rows:
        if r['period']<'201803':continue
        y=int(r['period'][:4]);m=int(r['period'][4:]);prev=f'{y if m>3 else y-1}{m-3 if m>3 else 12:02}'
        before=lookup.get((prev,r['code']))
        if before and (before['result_status']!=r['result_status'] or before['SrAnalitico']!=r['SrAnalitico']):
            transitions.append(dict(period=r['period'],code=r['code'],before_status=before['result_status'],after_status=r['result_status'],before_sr=before['SrAnalitico'],after_sr=r['SrAnalitico'],before_cp=before['CP'],after_cp=r['CP']))
    write('transitions',transitions)
    named=[r for r in rows if r['code'] in ('C0083467','C0080288')]
    write('named_exceptions',named)
    summary=dict(contract='ifdata-c4-diagnostic-v1',issue=139,financial_recalculation=False,periods=sorted(set(r['period'] for r in rows)),unit_periods=len(rows),raw_rows_checked=raw_checked,component_checks=component_checks,result_status_checks=result_checks,processing_mismatches=0,
        diagnostic_counts=dict(Counter(r['diagnostic_class'] for r in rows)),regime_candidates=dict(Counter(r['regime_candidate'] for r in rows)),inputs=inputs,
        files=[dict(file=p.name,sha256=sha(p)) for p in sorted(out.glob('*.csv'))],elapsed_seconds=perf_counter()-t,producer_sha256=sha(Path(__file__)))
    (out/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs','files')},ensure_ascii=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--raw',required=True);p.add_argument('--output',required=True);a=p.parse_args();main(a.root,a.raw,a.output)

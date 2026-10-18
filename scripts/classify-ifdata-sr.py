"""Build separate dated SR attributes; regroup stored results without evaluation."""
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import duckdb
from bank_quality.ifdata_cadastro import derive_sr_by_links


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def authenticated(root,pin):
    root=Path(root).resolve()
    if sha(root/'manifest.json')!=pin:raise ValueError('Manifest hash mismatch')
    return root,json.loads((root/'manifest.json').read_text(encoding='utf-8'))


def file_from(root,manifest,name):
    entries=[e for e in manifest['files'] if e['file']==name]
    if len(entries)!=1:raise ValueError('Missing or ambiguous input: '+name)
    p=(root/name).resolve()
    if root not in p.parents or sha(p)!=entries[0]['sha256']:raise ValueError('Input hash mismatch: '+name)
    return p


def new_output(output,*inputs):
    output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if any(output==p or output in p.parents or p in output.parents for p in inputs):raise ValueError('Output overlaps an input')
    return output


def read_csv(path):
    with path.open(encoding='utf-8',newline='') as f:yield from csv.DictReader(f)


def build(baseline,baseline_pin,diagnostic,diagnostic_pin,output):
    started=perf_counter();base,bm=authenticated(baseline,baseline_pin);diag,dm=authenticated(diagnostic,diagnostic_pin)
    if bm.get('contract')!='ifdata-universe-analysis-v1' or dm['input_pins']['baseline']!=baseline_pin:
        raise ValueError('Diagnosis/baseline mismatch')
    output=new_output(output,base,diag)
    units=file_from(base,bm,'unit_periods.csv');evidence_path=file_from(diag,dm,'sr_link_evidence.csv')
    if sha(units)!=dm['input_pins']['unit_periods']:raise ValueError('Different diagnosed units')
    links=defaultdict(list)
    for r in read_csv(evidence_path):links[r['dataset'],r['code'],r['period']].append(r)
    output.mkdir(parents=True);columns=['unit_id','dataset','code','period','sr_original','sr_vinculo','sr_analitico','method','status','payload']
    path=output/'attributes.csv';totals=Counter();coverage=defaultdict(Counter);seen=set();count=0
    csv.field_size_limit(10000000)
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,quoting=csv.QUOTE_NOTNULL);writer.writerow(columns)
        for raw in read_csv(units):
            u=json.loads(raw['payload']);key=(u['dataset'],u['code'],u['period'])
            if key in seen:raise ValueError('Duplicate native reporting unit')
            seen.add(key);cad=u.get('classifications') or {};ev=links.pop(key,[])
            r=derive_sr_by_links(cad.get('Sr'),ev,dataset=key[0],code=key[1],period=key[2])
            r.update(unit_id=u['unit_id'],dataset=key[0],code=key[1],period=key[2],membership=u['membership'],
                     native_cadastro=u.get('own_cadastro'),native_classifications={k:cad.get(k) for k in ('Sr','Tcb','Td','Tc','SegmentoTb')})
            assert r['sr_original']==cad.get('Sr')
            if r['status']=='derived':assert r['sr_original'] in (None,'') and key[2]>='201703'
            writer.writerow([r.get(k) for k in columns[:-1]]+[json.dumps(r,ensure_ascii=False,separators=(',',':'))])
            totals[key[0],r['status']]+=1;coverage[key[0],key[2]][r['status']]+=1;count+=1
    if links or count!=bm['tables']['unit_periods']:raise ValueError('Evidence/units population mismatch')
    with duckdb.connect() as conn:
        conn.execute("""create temp table attributes as select * from read_csv(?,header=true,all_varchar=true,nullstr='',allow_quoted_nulls=false,delim=',',quote='"',escape='"')""",[str(path)])
        conn.execute('copy attributes to ? (format parquet,compression zstd)',[str(output/'attributes.parquet')])
        assert conn.execute('select count(*) from attributes').fetchone()[0]==count
    summary=output/'coverage.csv'
    with summary.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['dataset','period','status','units'])
        for (d,p),counts in sorted(coverage.items()):
            for status,n in sorted(counts.items()):w.writerow([d,p,status,n])
    manifest=dict(contract='ifdata-sr-attribution-v1',baseline=dict(root=str(base),sha256=baseline_pin),
        diagnostic=dict(root=str(diag),sha256=diagnostic_pin),rule='original-first-dated-unique-sr-and-prudential-perimeter-v1',
        original_preserved=True,financial_recalculation=False,rows=count,
        totals=[dict(dataset=d,status=s,units=n) for (d,s),n in sorted(totals.items())],
        files=[dict(file=p.name,sha256=sha(p)) for p in (path,output/'attributes.parquet',summary)],
        elapsed_seconds=perf_counter()-started,producer_sha256=sha(Path(__file__)),
        helper_sha256=sha(Path(__file__).resolve().parents[1]/'bank_quality/ifdata_cadastro.py'))
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest


def apply_sr_attribute(row,attribute=None):
    """Copy a stored contribution, changing only the new classification/flags."""
    r=deepcopy(row);cad=r.get('target_cadastro')
    if attribute:
        if any(attribute.get(k)!=r.get(k) for k in ('unit_id','dataset','code','period')):
            raise ValueError('SR projection identity mismatch')
        if attribute['sr_original']!=(cad or {}).get('Sr'):raise ValueError('SR original mismatch')
        if attribute['status'] in ('derived','conflict'):
            cad=r['target_cadastro']=dict(cad or {},Data=r['period'])
            if attribute['status']=='conflict':
                r.setdefault('classification_states',{})['SrAnalitico']='conflict'
                r['flags']=sorted(set(r['flags']+['sr_link_conflict']))
            else:r['flags']=sorted(set(r['flags']+['sr_from_dated_link']))
        if cad is not None:cad['SrAnalitico']=attribute['sr_analitico']
    elif cad is not None:cad['SrAnalitico']=cad.get('Sr')
    return r


def choose_sr_contexts(changes,targets=None):
    from bank_quality.ifdata_analysis import METRICS
    contexts=sorted({key[:2] for key in changes})
    if targets is None:return contexts
    keys=[tuple(t) for t in targets]
    if not keys or len(keys)!=len(set(keys)) or any(len(t)!=4 or t[:2] not in contexts or t[2] not in METRICS or t[3] not in ('point','quarter','ttm') for t in keys):
        raise ValueError('Invalid or duplicate SR regroup targets')
    return sorted({t[:2] for t in keys})


def regroup(baseline,baseline_pin,attributes,attributes_pin,corrections,output,limit=None,targets=None):
    from bank_quality.ifdata_universe_analysis import aggregate_unit_results,Writer
    from bank_quality import ifdata_analysis as math
    from contextlib import ExitStack
    started=perf_counter();base,bm=authenticated(baseline,baseline_pin);attrs,am=authenticated(attributes,attributes_pin)
    if am.get('contract')!='ifdata-sr-attribution-v1' or am['baseline']['sha256']!=baseline_pin:
        raise ValueError('Attribute/baseline mismatch')
    output=new_output(output,base,attrs)
    coverage=file_from(base,bm,'unit_coverage.parquet');ap=file_from(attrs,am,'attributes.parquet')
    overlays=[];scopes=[];pins=[]
    for root,pin in corrections:
        root,m=authenticated(root,pin);s=m['scope']
        if m['contract']!='ifdata-selective-analysis-v1' or m['baseline']['expected_manifest_sha256']!=baseline_pin:
            raise ValueError('Correction/baseline mismatch')
        key=(s['period'],s['dataset'],s['metric'],s['horizon'])
        if key in scopes:raise ValueError('Duplicate correction scope')
        scopes.append(key);overlays.append(file_from(root,m,'unit_coverage.parquet'));pins.append(dict(root=str(root),sha256=pin,scope=s))
        new_output(output,root)
    with duckdb.connect(config={'threads':2,'memory_limit':'512MiB'}) as conn:
        conn.from_parquet(str(ap)).create_view('attributes')
        changes={}
        for (payload,) in conn.execute("select payload from attributes where status in ('derived','conflict')").fetchall():
            r=json.loads(payload);changes[r['dataset'],r['period'],r['code']]=r
        contexts=choose_sr_contexts(changes,targets);selected=contexts[:limit] if limit else contexts
        conn.from_parquet(str(coverage)).create_view('baseline_coverage')
        conn.execute('create temp table correction_scopes(period varchar,dataset varchar,metric varchar,horizon varchar)')
        if scopes:conn.executemany('insert into correction_scopes values (?,?,?,?)',scopes)
        sql="select period,dataset,metric,horizon,code,payload from baseline_coverage b where not exists(select 1 from correction_scopes s where (b.period,b.dataset,b.metric,b.horizon)=(s.period,s.dataset,s.metric,s.horizon))"
        for i,p in enumerate(overlays):
            conn.from_parquet(str(p)).create_view('overlay'+str(i));sql+=' union all select period,dataset,metric,horizon,code,payload from overlay'+str(i)
        conn.execute('create view stored as '+sql)
        selection=''
        if targets is not None:
            conn.execute('create temp table requested(dataset varchar,period varchar,metric varchar,horizon varchar)')
            conn.executemany('insert into requested values (?,?,?,?)',targets)
            selection=' and exists(select 1 from requested q where (stored.dataset,stored.period,stored.metric,stored.horizon)=(q.dataset,q.period,q.metric,q.horizon))'
        output.mkdir(parents=True);files=[];checks=[];rows_written=0
        with ExitStack() as stack:
            writer=Writer(output,'segment_coverage',stack)
            for dataset,period in selected:
                rows=[json.loads(r[0]) for r in conn.execute('select payload from stored where dataset=? and period=?'+selection+' order by metric,horizon,code',[dataset,period]).fetchall()]
                if not rows:raise ValueError('Requested SR regroup has no stored results')
                if targets is not None:
                    actual={(r['dataset'],r['period'],r['metric'],r['horizon']) for r in rows}
                    if any(tuple(t) not in actual for t in targets if tuple(t[:2])==(dataset,period)):
                        raise ValueError('Requested SR metric/window is absent')
                original={}
                for r in rows:
                    k=(r['metric'],r['horizon']);n,d=original.setdefault(k,[0,0])
                    if r.get('unit_id') and r['status']=='ok' and r['applicability']=='applicable':
                        original[k]=[n+math._rational(r['numerator_fraction']),d+math._rational(r['denominator_fraction'])]
                projected=[apply_sr_attribute(r,changes.get((dataset,period,r.get('code')))) for r in rows]
                for a,b in zip(rows,projected):
                    for field in ('unit_id','unit_key','membership','companies','status','applicability','value_fraction','numerator_fraction','denominator_fraction','asset_fraction'):
                        if a.get(field)!=b.get(field):raise ValueError('Stored contribution changed: '+field)
                reduced=aggregate_unit_results(projected,fields=('SrAnalitico',))
                for a in reduced['aggregates']:
                    if a['cohort']=='total':
                        for key,expected in zip(('numerator_fraction','denominator_fraction'),original[a['metric'],a['horizon']]):
                            if (math._rational(a[key]) if a[key] else 0)!=expected:raise ValueError('Regroup total mismatch')
                for r in reduced['segment_coverage']:writer.append(r);rows_written+=1
                checks.append(dict(dataset=dataset,period=period,stored_rows=len(rows),unchanged_financial_contributions=True))
                print(json.dumps(dict(regroup_period=period,dataset=dataset,stored_rows=len(rows))),flush=True)
            files=writer.finish(conn)
    manifest=dict(contract='ifdata-sr-segmentation-v1',baseline=dict(root=str(base),sha256=baseline_pin),
        attributes=dict(root=str(attrs),sha256=attributes_pin),corrections=pins,field='SrAnalitico',
        financial_recalculation=False,original_field_unchanged=True,rows=rows_written,files=files,
        affected_contexts=[dict(dataset=d,period=p) for d,p in selected],requested_targets=targets,complete=len(selected)==len(contexts),
        completion_scope='requested_targets' if targets is not None else 'all_changed_classification_contexts',checks=checks,
        unchanged_contexts=('Keep previously accepted SrAnalitico; replace only requested targets' if targets is not None
                            else 'Copy the corresponding original Sr segmentation; classification is identical there'),
        elapsed_seconds=perf_counter()-started,producer_sha256=sha(Path(__file__)))
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for option in ('baseline','expected-baseline-manifest-sha256','output'):
        parser.add_argument('--'+option,required=True)
    for option in ('diagnostic','expected-diagnostic-manifest-sha256','attributes','expected-attributes-manifest-sha256'):
        parser.add_argument('--'+option)
    parser.add_argument('--correction',nargs=2,action='append',default=[],metavar=('ROOT','MANIFEST_SHA256'))
    parser.add_argument('--target',nargs=4,action='append',metavar=('DATASET','PERIOD','METRIC','HORIZON'))
    args=parser.parse_args()
    if args.attributes:
        if not args.expected_attributes_manifest_sha256:parser.error('Attribute manifest pin required')
        result=regroup(args.baseline,args.expected_baseline_manifest_sha256,args.attributes,args.expected_attributes_manifest_sha256,args.correction,args.output,targets=args.target)
    else:
        if not args.diagnostic or not args.expected_diagnostic_manifest_sha256:parser.error('Diagnostic root and manifest pin required')
        result=build(args.baseline,args.expected_baseline_manifest_sha256,args.diagnostic,args.expected_diagnostic_manifest_sha256,args.output)
    print(json.dumps(result,ensure_ascii=True,indent=2))

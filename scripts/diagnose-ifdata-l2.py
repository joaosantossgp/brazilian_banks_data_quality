"""Diagnose all 60 financial L2 periods from stored source and accepted outputs."""
import argparse,csv,gzip,hashlib,json
from collections import Counter,defaultdict
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from time import perf_counter
import duckdb
BASE_PIN='b61c30ee0ac3e1a0d4dadb4ae85ecc3a54dc9e6b23f23aeade51c3de8db6f192'
SR_PIN='a8e09826ec1b50becab01a844fa4954762a71a6fdfd60b245be53ebce372a3be'
ACCOUNTS={'cash':('2','78188'),'interfinancial':('2','78189'),'sight_deposits':('3','78282'),'deposits':('3','78287'),'AT':('1','78182')}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def equal(a,b):return (a is None and b is None) or (a is not None and b is not None and Decimal(str(a))==Decimal(str(b)))
def main(root,raw,output):
 t=perf_counter();root=Path(root).resolve();raw=Path(raw).resolve();out=Path(output).resolve()
 if out.exists():raise FileExistsError(out)
 for p in (root/'ifdata-universe-analysis-20261014-final-run3',root/'ifdata-odata-20261011',root/'ifdata-sr-links-20261016-run2',raw):
  if out==p or p in out.parents or out in p.parents:raise ValueError('Output overlaps input')
 inputs=[]
 def auth(p,pin):
  if sha(p)!=pin:raise ValueError('Hash mismatch '+str(p))
  inputs.append(dict(path=str(p),sha256=pin))
 base=root/'ifdata-universe-analysis-20261014-final-run3';auth(base/'manifest.json',BASE_PIN)
 bm=json.loads((base/'manifest.json').read_text(encoding='utf8'))
 for f in ('components.parquet','results.parquet','unit_periods.parquet'):auth(base/f,next(e['sha256'] for e in bm['files'] if e['file']==f))
 source=root/'ifdata-odata-20261011/financial';auth(source/'manifest.json',bm['inputs']['financial']['expected_manifest_sha256'])
 sm=json.loads((source/'manifest.json').read_text(encoding='utf8'))
 sr=root/'ifdata-sr-links-20261016-run2';auth(sr/'manifest.json',SR_PIN)
 am=json.loads((sr/'manifest.json').read_text(encoding='utf8'));auth(sr/'attributes.parquet',next(e['sha256'] for e in am['files'] if e['file']=='attributes.parquet'))
 parts=[e for e in sm['files'] if '201003'<=str(e['period'])<='202412'];assert len(parts)==60
 native={};raw_checked=0;definitions=Counter();unkeyed=[]
 condition=' or '.join("(NumeroRelatorio='"+rep+"' and Conta='"+conta+"')" for rep,conta in ACCOUNTS.values())
 for e in parts:
  auth(source/e['file'],e['sha256']);rp=raw/Path(e['source_file'].replace('\\','/'));auth(rp,e['source_sha256'])
  body=json.loads(gzip.decompress(rp.read_bytes()),parse_float=Decimal,parse_int=Decimal)['value']
  with duckdb.connect() as c:
   records=c.execute('select * from read_parquet(?) where '+condition,[str(source/e['file'])]).fetchall();cols=[v[0] for v in c.description]
  raw_selected=[x for x in body if (str(x['NumeroRelatorio']),str(x['Conta'])) in ACCOUNTS.values()]
  assert len(records)==len(raw_selected)
  for values in records:
   n=dict(zip(cols,values));idx=int(n['source_row'])-1;original=body[idx]
   for key in ('TipoInstituicao','CodInst','AnoMes','NomeRelatorio','NumeroRelatorio','Grupo','Conta','NomeColuna','DescricaoColuna'):
    v=original.get(key);assert n[key]==(None if v is None else str(v)),(e['period'],idx,key)
   assert equal(n['Saldo'],original.get('Saldo'));assert n['source_sha256']==e['source_sha256']
   definitions[(n['NumeroRelatorio'],n['Conta'],n['NomeColuna'],n['DescricaoColuna'])]+=1;raw_checked+=1
   if not n['CodInst']:
    unkeyed.append(dict(period=n['AnoMes'],NumeroRelatorio=n['NumeroRelatorio'],Conta=n['Conta'],Saldo=n['Saldo'],source_row=n['source_row'],source_sha256=n['source_sha256']))
    continue
   k=(n['AnoMes'],n['CodInst'],n['NumeroRelatorio'],n['Conta']);assert k not in native;native[k]=n
  print('authenticated',e['period'],len(records),flush=True)
 c=duckdb.connect(config={'threads':2,'memory_limit':'1GB'})
 filt="dataset='financial' and period between '201003' and '202412'"
 units={(p,k):json.loads(v) for p,k,v in c.execute(f'select period,code,payload from read_parquet(?) where {filt}',[str(base/'unit_periods.parquet')]).fetchall()}
 attrs={(p,k):(s,a,m) for p,k,s,a,m in c.execute(f'select period,code,sr_original,sr_analitico,method from read_parquet(?) where {filt}',[str(sr/'attributes.parquet')]).fetchall()}
 results={(p,k):json.loads(v) for p,k,v in c.execute(f"select period,code,payload from read_parquet(?) where {filt} and metric='L2' and horizon='point'",[str(base/'results.parquet')]).fetchall()}
 components={}
 comp_filter="json_extract_string(payload,'$.component') in ('cash','interfinancial','sight_deposits','deposits','AT') and json_extract_string(payload,'$.analysis_period')=period"
 for p,k,v in c.execute(f'select period,code,payload from read_parquet(?) where {filt} and {comp_filter}',[str(base/'components.parquet')]).fetchall():
  x=json.loads(v);key=(p,k,x['component']);assert key not in components;components[key]=x
 c.close();assert set(units)==set(results)==set(attrs)
 assert {(p,k) for p,k,report,account in native}==set(units)
 rows=[];comp_checks=0;result_checks=0
 for (period,code),u in sorted(units.items()):
  r=results[(period,code)];a=attrs[(period,code)];cl=u['classifications'] or {}
  row=dict(period=period,code=code,Tcb=cl.get('Tcb'),Td=cl.get('Td'),Tc=cl.get('Tc'),SegmentoTb=cl.get('SegmentoTb'),Sr=a[0],SrAnalitico=a[1],sr_method=a[2],membership=u['membership'],companies=json.dumps(u.get('companies',[]),ensure_ascii=False),result_status=r['status'],applicability=r['applicability'])
  for comp,(report,account) in ACCOUNTS.items():
   n=native.get((period,code,report,account));x=components[(period,code,comp)]
   assert n is not None and x['status']=='ok';assert equal(n['Saldo'],x['token']);assert n['source_sha256']==x['sources'][0]['source_sha256']
   row[comp]=n['Saldo'];row[comp+'_source_state']='null' if n['Saldo'] is None else 'observed';comp_checks+=1
  cash,inter,den=row['cash'],row['interfinancial'],row['sight_deposits']
  expected='native_null' if any(v is None for v in (cash,inter,den)) else ('zero_denominator' if Decimal(den)==0 else 'ok')
  assert r['status']==expected,(period,code,r['status'],expected)
  for comp in ('cash','interfinancial','sight_deposits'):
   v=r['components'][comp]['value_fraction'];token=row[comp]
   if token is None:assert v is None
   else:assert Fraction(int(v['numerator']),int(v['denominator']))==Fraction(Decimal(token))
  if expected=='ok':
   numerator=Fraction(Decimal(cash))+Fraction(Decimal(inter))
   assert Fraction(int(r['numerator_fraction']['numerator']),int(r['numerator_fraction']['denominator']))==numerator
   assert Fraction(int(r['denominator_fraction']['numerator']),int(r['denominator_fraction']['denominator']))==Fraction(Decimal(den))
  support='positive' if den is not None and Decimal(den)>0 else ('zero' if den is not None and Decimal(den)==0 else ('negative' if den is not None else 'null'))
  assert r['applicability']==('applicable' if support=='positive' else 'unknown')
  row['denominator_state']=support
  row['numerator_state']='null' if cash is None or inter is None else ('zero' if Decimal(cash)+Decimal(inter)==0 else ('positive' if Decimal(cash)+Decimal(inter)>0 else 'negative'))
  row['deposit_total_state']='null' if row['deposits'] is None else ('zero' if Decimal(row['deposits'])==0 else ('positive' if Decimal(row['deposits'])>0 else 'negative'))
  row['diagnostic_class']='source_null_component' if expected=='native_null' else ('source_zero_sight_deposits' if support=='zero' else ('negative_sight_deposits' if support=='negative' else 'eligible_positive_sight_deposits'))
  result_checks+=1;rows.append(row)
 out.mkdir()
 def write(name,data):
  with (out/(name+'.csv')).open('w',encoding='utf8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 write('unit_diagnosis',rows)
 if unkeyed:write('unkeyed_source_rows',unkeyed)
 def grouped(fields):
  cnt=Counter(tuple(r[f] for f in fields) for r in rows)
  return [dict(zip(fields,k),unit_periods=n) for k,n in sorted(cnt.items(),key=lambda v:repr(v[0]))]
 write('period_coverage',grouped(['period','result_status','applicability','diagnostic_class']))
 write('segment_coverage',grouped(['period','Tcb','Td','Tc','Sr','SrAnalitico','SegmentoTb','diagnostic_class']))
 write('source_definitions',[dict(NumeroRelatorio=k[0],Conta=k[1],NomeColuna=k[2],DescricaoColuna=k[3],rows=n) for k,n in definitions.items()])
 lookup={(r['period'],r['code']):r for r in rows};transitions=[]
 for r in rows:
  y=int(r['period'][:4]);m=int(r['period'][4:]);prev=f'{y if m>3 else y-1}{m-3 if m>3 else 12:02}';before=lookup.get((prev,r['code']))
  if before and before['diagnostic_class']!=r['diagnostic_class']:
   transitions.append(dict(period=r['period'],code=r['code'],before_class=before['diagnostic_class'],after_class=r['diagnostic_class'],Tcb=r['Tcb']))
 write('transitions',transitions)
 codes=defaultdict(list)
 for r in rows:codes[r['code']].append(r)
 write('unit_windows',[dict(code=k,first=v[0]['period'],last=v[-1]['period'],observed_periods=len(v),zero_periods=sum(r['denominator_state']=='zero' for r in v),positive_periods=sum(r['denominator_state']=='positive' for r in v),null_periods=sum(r['result_status']=='native_null' for r in v),sample_periods=sum(r['membership']=='sample' for r in v)) for k,v in sorted(codes.items())])
 summary=dict(contract='ifdata-l2-diagnostic-v1',issue=140,financial_recalculation=False,periods=sorted(set(r['period'] for r in rows)),unit_periods=len(rows),raw_selected_rows_checked=raw_checked,unkeyed_source_rows=len(unkeyed),component_checks=comp_checks,result_checks=result_checks,processing_mismatches=0,diagnostic_counts=dict(Counter(r['diagnostic_class'] for r in rows)),applicability_counts=dict(Counter(r['applicability'] for r in rows)),inputs=inputs,files=[dict(file=p.name,sha256=sha(p)) for p in sorted(out.glob('*.csv'))],producer_sha256=sha(Path(__file__)),elapsed_seconds=perf_counter()-t)
 (out/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in summary.items() if k not in ('files','inputs')},ensure_ascii=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--raw',required=True);p.add_argument('--output',required=True);a=p.parse_args();main(a.root,a.raw,a.output)

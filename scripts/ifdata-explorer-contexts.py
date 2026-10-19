"""Pinned native balance/credit contexts for the local explorer.

Exact sums of a single literal context across identified reporting units. No
indicator, flow transformation, company inference or total/detail addition.
Only Tcb and disjoint membership are dimensions of these presentation summaries.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import duckdb

FIELDS=('NumeroRelatorio','NomeRelatorio','Grupo','Conta','NomeColuna','DescricaoColuna')

def summarize(rows,membership,kind):
 catalog=[];lookup={};groups={};seen=set();unidentified=unmatched=0
 for row in rows:
  period,code=row['AnoMes'],row['CodInst']
  if code is None or code=='':unidentified+=1;continue
  member=membership.get((period,code))
  if member is None:unmatched+=1;continue
  cohort,tcb=member
  if cohort not in ('sample','remaining','unknown'):raise ValueError('Invalid disjoint membership')
  context=tuple(row[k] for k in FIELDS)
  ident=(period,code,context)
  if ident in seen:raise ValueError('Duplicate literal observation')
  seen.add(ident)
  if context not in lookup:
   lookup[context]=len(catalog);catalog.append(dict(zip(FIELDS,context),unit='count_non_unique' if row['NumeroRelatorio']=='10' else 'BRL',kind=kind))
  key=(period,cohort,tcb,lookup[context]);g=groups.setdefault(key,[None,0,Counter(),0])
  token=row['Saldo']
  status={None:'native_null','':'native_empty','NA':'native_NA','NI':'native_NI'}.get(token)
  if status:g[2][status]+=1;continue
  try:value=Fraction(token)
  except (ValueError,ZeroDivisionError) as exc:raise ValueError('Unsupported native numeric token') from exc
  g[0]=(g[0] or Fraction(0))+value;g[1]+=1;g[3]+=value<0
 return dict(catalog=catalog,rows=[[*key,None if v[0] is None else [str(v[0].numerator),str(v[0].denominator)],v[1],dict(v[2]),v[3]] for key,v in groups.items()],unidentified_rows=unidentified,unmatched_rows=unmatched)

def digest(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def load_package(root,pin,contract):
 root=Path(root).resolve()
 if digest(root/'manifest.json')!=pin:raise ValueError('Context manifest hash mismatch')
 m=json.loads((root/'manifest.json').read_text(encoding='utf8'))
 if m.get('contract')!=contract:raise ValueError('Context contract mismatch')
 return root,m

def authenticated(root,entry):
 path=(root/entry['file']).resolve()
 if not path.is_relative_to(root) or digest(path)!=entry['sha256']:raise ValueError('Context table hash mismatch')
 return path

def build_contexts(composition,composition_pin,balance_root,balance_pin,credit_packages,periods=None):
 root,m=load_package(composition,composition_pin,'ifdata-composed-analysis-v1')
 u=authenticated(root,next(e for e in m['files'] if e['file']=='unit_periods.parquet'))
 with duckdb.connect(config={'threads':1,'memory_limit':'512MB'}) as con:
  members={}
  for payload, in con.execute("select payload from read_parquet(?) where dataset='financial'",[str(u)]).fetchall():
   r=json.loads(payload);key=(r['period'],r['code'])
   if key in members:raise ValueError('Ambiguous financial reporting unit')
   members[key]=(r['membership'],(r.get('classifications') or {}).get('Tcb'))
  result={'composition_manifest':composition_pin,'dimension_scope':['Tcb','membership'],'perspective':'financial','sources':[]}
  for kind,packages in [('balance',[(balance_root,balance_pin)]),('credit',credit_packages)]:
   parts=[];global_catalog=[];global_lookup={};source_periods=set()
   for package_root,pin in packages:
    native,m=load_package(package_root,pin,'ifdata-odata-parquet-v1');result['sources'].append({'kind':kind,'manifest':pin})
    for entry in m['files']:
     period=str(entry.get('period',''))
     if not '201003'<=period<='202412' or periods and period not in periods:continue
     if period in source_periods:raise ValueError('Overlapping context package periods')
     source_periods.add(period);file=authenticated(native,entry)
     query='select '+','.join(['AnoMes','CodInst',*FIELDS,'Saldo'])+' from read_parquet(?)'
     if kind=='balance':query+=" where NumeroRelatorio in ('2','3')"
     cursor=con.execute(query,[str(file)]);names=[x[0] for x in cursor.description]
     def stream():
      while batch:=cursor.fetchmany(4096):
       for row in batch:yield dict(zip(names,row))
     part=summarize(stream(),members,kind);remap={}
     for i,item in enumerate(part['catalog']):
      k=json.dumps(item,sort_keys=True,ensure_ascii=False)
      if k not in global_lookup:global_lookup[k]=len(global_catalog);global_catalog.append(item)
      remap[i]=global_lookup[k]
     for row in part['rows']:row[3]=remap[row[3]]
     parts.append(part)
     print('CONTEXT',kind,period,len(part['rows']),flush=True)
   result[kind]={'catalog':global_catalog,'rows':[r for p in parts for r in p['rows']],'unidentified_rows':sum(p['unidentified_rows'] for p in parts),'unmatched_rows':sum(p['unmatched_rows'] for p in parts)}
  return result


if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--composition',required=True);parser.add_argument('--composition-pin',required=True)
 parser.add_argument('--balance',required=True);parser.add_argument('--balance-pin',required=True)
 parser.add_argument('--credit',nargs=2,action='append',required=True,metavar=('ROOT','SHA256'))
 parser.add_argument('--periods',nargs='*');parser.add_argument('--output',required=True)
 args=parser.parse_args();output=Path(args.output).resolve()
 if output.exists():raise ValueError('Refusing to replace context output')
 data=build_contexts(args.composition,args.composition_pin,args.balance,args.balance_pin,args.credit,set(args.periods) if args.periods else None)
 output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('CONTEXT_OUTPUT',str(output),digest(output),flush=True)

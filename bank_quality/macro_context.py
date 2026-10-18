"""Finite official macro context; exact published tokens and dated source receipts."""
from collections import defaultdict
from datetime import datetime,timezone
from decimal import Decimal,InvalidOperation
from fractions import Fraction
import gzip,hashlib,json,re,zlib
from pathlib import Path
import urllib.request,urllib.error

import duckdb

CONTRACT='macro-context-v1'
PROFILE=Path(__file__).with_name('macro-context-series.json')


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def _fraction(value):
    return [str(value.numerator),str(value.denominator)] if value is not None else None


def parse_sidra(body,series):
    """Preserve SIDRA sentinels without inventing zero or changing decimal scale."""
    try:
        if body[:2]==b'\x1f\x8b':body=gzip.decompress(body)
        document=json.loads(body)
    except (ValueError,UnicodeError,OSError,EOFError,zlib.error) as exc:raise ValueError('Invalid SIDRA JSON/gzip document') from exc
    if not isinstance(document,list) or len(document)<2 or not isinstance(document[0],dict):
        raise ValueError('SIDRA header and observed rows required')
    header=document[0]
    if not str(header.get('D2C','')).startswith('Variável') or not str(header.get('D3C','')).startswith(('Trimestre','Mês')):
        raise ValueError('Unexpected SIDRA variable/period dimensions')
    variables={str(v) for v in str(series['variable']).split(',')};seen=set();rows=[]
    categories=series.get('classification_path','').split('/')[-1].split(',') if series.get('classification_path') else ['total']
    for source in document[1:]:
        variable=source.get('D2C');native=source.get('D3C');category=source.get('D4C','total')
        if source.get('NC')!='1' or source.get('D1C')!='1' or variable not in variables or category not in categories:
            raise ValueError('Unexpected SIDRA national/variable/category identity')
        expected_unit=series.get('native_units',{}).get(variable)
        if not expected_unit or source.get('MC')!=expected_unit['code'] or source.get('MN')!=expected_unit['name']:
            raise ValueError('Unexpected SIDRA native unit')
        if not isinstance(native,str) or not re.fullmatch(r'\d{6}',native):raise ValueError('Invalid SIDRA period')
        year,part=int(native[:4]),int(native[4:]);quarterly=series['frequency']=='quarterly'
        if not 1900<=year<=2100 or not 1<=part<=(4 if quarterly else 12):raise ValueError('Invalid SIDRA period')
        period=f'{year}{part*3 if quarterly else part:02d}'
        key='|'.join((series['key'],variable,native,category))
        if key in seen:raise ValueError('Duplicate SIDRA observation')
        seen.add(key);token=source.get('V')
        if not isinstance(token,str):raise ValueError('SIDRA value must be an exact text token')
        value=None;status='source_sentinel'
        if re.fullmatch(r'-?\d+(?:\.\d+)?',token):
            value=Fraction(Decimal(token));status='ok'
        elif token not in ('-','..','...','X',''):
            raise ValueError('Unrecognized SIDRA value token')
        rows.append(dict(id=key,series=series['key'],table=str(series['table']),variable=variable,
                         category=category,native_period=native,period=period,frequency=series['frequency'],
                         unit=expected_unit.get('unit',series['unit']),native_unit_code=source.get('MC'),native_unit=source.get('MN'),
                         value_token=token,value_fraction=_fraction(value),status=status,source_row=source))
    if {(r['variable'],r['category']) for r in rows}!={(v,c) for v in variables for c in categories}:
        raise ValueError('Incomplete SIDRA variable/category set')
    return rows


def quarterly_panel(observations):
    groups=defaultdict(list)
    for row in observations:
        month=int(row['period'][4:]);quarter=(month-1)//3+1;period=row['period'][:4]+f'{quarter*3:02d}'
        groups[(row['series'],row['variable'],row['category'],period)].append(row)
    output=[]
    for (series,variable,category,period),items in sorted(groups.items()):
        monthly=items[0]['frequency']=='monthly'
        if not monthly:chosen=items;method='official_quarter'
        elif series=='industrial_production':chosen=items;method='mean_three_months'
        elif series=='ipca' and variable=='63':chosen=items;method='compound_three_months'
        else:chosen=[r for r in items if r['period']==period];method='quarter_end_month'
        expected=3 if method in ('mean_three_months','compound_three_months') else 1
        complete=len(chosen)==expected and len({r['period'] for r in chosen})==expected and all(r['status']=='ok' for r in chosen)
        values=[Fraction(*map(int,r['value_fraction'])) for r in chosen if r['value_fraction'] is not None]
        value=None
        if complete:
            if method=='mean_three_months':value=sum(values,Fraction())/3
            elif method=='compound_three_months':
                value=Fraction(1)
                for v in values:value*=1+v/100
                value=(value-1)*100
            else:value=values[0]
        output.append(dict(id='|'.join((series,variable,category,period,method)),series=series,variable=variable,
                           category=category,period=period,method=method,unit=items[0]['unit'],
                           value_fraction=_fraction(value),status='ok' if complete else 'incomplete_source_window',
                           source_ids=[r.get('id') for r in chosen],source_count=len(chosen),expected_source_count=expected))
    gdp={r['period']:r for r in output if r['series']=='gdp_current_brl_million'}
    for period,row in sorted(gdp.items()):
        q=int(period[:4])*4+int(period[4:])//3-1
        periods=[f'{(q-i)//4}{((q-i)%4+1)*3:02d}' for i in range(3,-1,-1)]
        selected=[gdp[p] for p in periods if p in gdp]
        complete=len(selected)==4 and all(r['status']=='ok' for r in selected)
        value=sum((Fraction(*map(int,r['value_fraction'])) for r in selected),Fraction()) if complete else None
        output.append(dict(row,id=row['id']+'|ttm',method='sum_four_quarters',value_fraction=_fraction(value),
                           status='ok' if complete else 'incomplete_source_window',source_ids=[r['id'] for r in selected],
                           source_count=len(selected),expected_source_count=4))
    return sorted(output,key=lambda r:r['id'])


def _write_table(root,name,rows):
    columns=('id','series','variable','category','period','status','payload')
    with duckdb.connect(config={'threads':1,'memory_limit':'512MiB'}) as conn:
        conn.execute('create table output('+','.join('"'+c+'" varchar' for c in columns)+')')
        if rows:conn.executemany('insert into output values (?,?,?,?,?,?,?)',
                         [[r.get(k) for k in columns[:-1]]+[json.dumps(r,ensure_ascii=False,sort_keys=True)] for r in rows])
        path=root/(name+'.parquet');conn.execute('copy output to ? (format parquet,compression zstd)',[str(path)])
    return dict(file=path.name,sha256=digest(path),rows=len(rows))


def collect_context(raw,output,*,profile=PROFILE):
    """Eight explicit SIDRA requests, exclusive receipt and analytical packages."""
    raw,output,profile=Path(raw).resolve(),Path(output).resolve(),Path(profile).resolve()
    if raw.exists() or output.exists():raise FileExistsError('Macro destinations must be new')
    if raw==output or raw in output.parents or output in raw.parents or raw in profile.parents or output in profile.parents:
        raise ValueError('Macro source/output overlap')
    config=json.loads(profile.read_text(encoding='utf8'));pin=digest(profile)
    if config.get('contract')!='macro-context-series-v1':raise ValueError('Macro profile contract mismatch')
    raw.mkdir(parents=True);observations=[];receipts=[];errors=[]
    for series in config['series']:
        if series['provider']!='IBGE_SIDRA':raise ValueError('Unreviewed macro provider')
        begin=2012 if series['key'] in ('unemployment','labor_income') else 2009
        periods=','.join(f'{y}{p:02d}' for y in range(begin,2025) for p in range(1,5 if series['frequency']=='quarterly' else 13))
        url=series['url_template'].format(periods=periods);name=series['key'];status=None;headers={};error=None
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'monograph-macro-context/1.0','Accept':'application/json'})
            with urllib.request.urlopen(request,timeout=60) as response:
                status=response.status;headers=dict(response.headers);body=response.read()
        except urllib.error.HTTPError as exc:status=exc.code;headers=dict(exc.headers);body=exc.read();error=str(exc)
        except (OSError,TimeoutError) as exc:body=b'';error=str(exc)
        path=raw/(name+'.body');path.write_bytes(body)
        receipt=dict(series=name,url=url,retrieved_utc=datetime.now(timezone.utc).isoformat(),status=status,
                     headers=headers,body=path.name,sha256=digest(path),bytes=len(body),error=error)
        try:
            if status!=200:raise ValueError('Macro HTTP request failed')
            parsed=parse_sidra(body,series)
            for row in parsed:row['source_ref']=dict(receipt_file=str(raw/(name+'.receipt.json')),body_sha256=receipt['sha256'],retrieved_utc=receipt['retrieved_utc'])
            receipt['semantic_status']='valid';observations.extend(parsed)
        except ValueError as exc:receipt['semantic_status']='invalid';receipt['diagnostic']=str(exc);errors.append(name)
        (raw/(name+'.receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8');receipts.append(receipt)
    if errors:raise ValueError('Macro sources failed; receipts retained, no accepted manifest: '+','.join(errors))
    if digest(profile)!=pin:raise ValueError('Macro profile changed during capture')
    captured=dict(contract='macro-context-capture-v1',profile_sha256=pin,files=[dict(file=p.name,sha256=digest(p)) for p in sorted(raw.iterdir())],receipts=receipts)
    (raw/'manifest.json').write_text(json.dumps(captured,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
    return _finish_context(raw,digest(raw/'manifest.json'),output,profile,config,pin,observations,receipts)


def replay_context(raw,expected_sha256,output,*,profile=PROFILE):
    """Rebuild exclusively from authenticated captured bytes; no HTTP calls."""
    raw,output,profile=Path(raw).resolve(),Path(output).resolve(),Path(profile).resolve()
    if output.exists():raise FileExistsError(output)
    if output==raw or output in raw.parents or raw in output.parents or output in profile.parents:
        raise ValueError('Macro replay source/output overlap')
    if digest(raw/'manifest.json')!=expected_sha256:raise ValueError('Macro capture manifest hash mismatch')
    manifest=json.loads((raw/'manifest.json').read_text(encoding='utf8'));pin=digest(profile)
    if manifest.get('contract')!='macro-context-capture-v1' or manifest.get('profile_sha256')!=pin:
        raise ValueError('Macro capture/profile mismatch')
    files=manifest['files']
    for entry in files:
        path=(raw/entry['file']).resolve()
        if path.parent!=raw or digest(path)!=entry['sha256']:raise ValueError('Macro captured source hash mismatch')
    config=json.loads(profile.read_text(encoding='utf8'));series={r['key']:r for r in config['series']}
    receipts=manifest['receipts'];observations=[]
    if len(receipts)!=len(series) or {r['series'] for r in receipts}!=set(series):raise ValueError('Macro capture series mismatch')
    for receipt in receipts:
        if receipt['status']!=200 or receipt['semantic_status']!='valid':raise ValueError('Macro capture not semantically valid')
        path=(raw/receipt['body']).resolve()
        if path.parent!=raw or digest(path)!=receipt['sha256']:raise ValueError('Macro receipt body hash mismatch')
        parsed=parse_sidra(path.read_bytes(),series[receipt['series']])
        for row in parsed:row['source_ref']=dict(receipt_file=str(raw/(receipt['series']+'.receipt.json')),body_sha256=receipt['sha256'],retrieved_utc=receipt['retrieved_utc'])
        observations.extend(parsed)
    return _finish_context(raw,expected_sha256,output,profile,config,pin,observations,receipts)


def _finish_context(raw,raw_pin,output,profile,config,pin,observations,receipts):
    panel=quarterly_panel(observations);panel=[r for r in panel if '201003'<=r['period']<='202412']
    output.mkdir(parents=True);files=[_write_table(output,'observations',observations),_write_table(output,'quarterly',panel)]
    coverage=[]
    keys=set()
    for series in config['series']:
        categories=series.get('classification_path','').split('/')[-1].split(',') if series.get('classification_path') else ['total']
        for variable in str(series['variable']).split(','):
            method=('official_quarter' if series['frequency']=='quarterly' else 'mean_three_months' if series['key']=='industrial_production' else 'compound_three_months' if series['key']=='ipca' and variable=='63' else 'quarter_end_month')
            for category in categories:
                keys.add((series['key'],variable,category,method))
                if series['key']=='gdp_current_brl_million':keys.add((series['key'],variable,category,'sum_four_quarters'))
    for series,variable,category,method in sorted(keys):
        selected={r['period']:r for r in panel if (r['series'],r['variable'],r['category'],r['method'])==(series,variable,category,method)}
        missing=[f'{y}{m}' for y in range(2010,2025) for m in ('03','06','09','12') if f'{y}{m}' not in selected]
        coverage.append(dict(series=series,variable=variable,category=category,method=method,expected_quarters=60,
                             observed_quarters=len(selected),valid_quarters=sum(r['status']=='ok' for r in selected.values()),
                             absent_periods=missing,absences=[dict(period=p,reason='before_pnad_continua_2012' if series in ('unemployment','labor_income') and p<'201203' else 'not_observed') for p in missing]))
    manifest=dict(contract=CONTRACT,profile_sha256=pin,profile=str(profile),periods=[f'{y}{m}' for y in range(2010,2025) for m in ('03','06','09','12')],
                  capture=dict(root=str(raw),expected_manifest_sha256=raw_pin),
                  tables=dict(observations=len(observations),quarterly=len(panel)),files=files,coverage=coverage,receipts=receipts,
                  financial_indicator_calculations=0,limits=config['limits'],producer_sha256=digest(Path(__file__)))
    if digest(raw/'manifest.json')!=raw_pin or digest(profile)!=pin:raise ValueError('Macro source changed before acceptance')
    for receipt in receipts:
        if digest(raw/receipt['body'])!=receipt['sha256']:raise ValueError('Macro source body changed before acceptance')
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
    return manifest


def parse_ipea_monthly(body,metadata):
    """Official Ipeadata dissemination of BCB effective monthly Over/Selic."""
    if (metadata.get('SERCODIGO')!='BM12_TJOVER12' or metadata.get('PERNOME')!='Mensal' or
            metadata.get('UNINOME')!='(% a.m.)' or metadata.get('PAICODIGO')!='BRA' or
            'Banco Central' not in metadata.get('FNTNOME','')):raise ValueError('Unexpected Ipeadata interest metadata')
    try:values=json.loads(body,parse_float=str,parse_int=str)['value']
    except (ValueError,KeyError,TypeError) as exc:raise ValueError('Invalid Ipeadata values') from exc
    rows=[];seen=set()
    for source in values:
        if source.get('SERCODIGO')!='BM12_TJOVER12' or source.get('NIVNOME') not in ('',None) or source.get('TERCODIGO') not in ('',None):
            raise ValueError('Unexpected Ipeadata series/territorial identity')
        date=source.get('VALDATA','')
        if not re.fullmatch(r'\d{4}-\d{2}-01T.*',date):raise ValueError('Invalid Ipeadata monthly date')
        period=date[:7].replace('-','')
        if not '01'<=period[4:]<='12':raise ValueError('Invalid Ipeadata month')
        if not '200901'<=period<='202412':continue
        if period in seen:raise ValueError('Duplicate Ipeadata month')
        seen.add(period);token=source.get('VALVALOR')
        if not isinstance(token,str) or not re.fullmatch(r'-?\d+(?:\.\d+)?',token):raise ValueError('Invalid Ipeadata exact value token')
        value=Fraction(Decimal(token))
        if value<=-100:raise ValueError('Invalid interest accumulation factor')
        rows.append(dict(id='selic_effective_monthly|BM12_TJOVER12|'+period+'|total',series='selic_effective_monthly',variable='BM12_TJOVER12',
            category='total',period=period,native_period=date,frequency='monthly',unit='percent_pm',value_token=token,
            value_fraction=_fraction(value),status='ok',source_row=source))
    return sorted(rows,key=lambda r:r['period'])


def interest_panel(observations,inflation):
    """Realized quarterly/12m benchmark, using matching official IPCA windows."""
    months={r['period']:r for r in observations};prices={(r['period'],r['variable']):r for r in inflation if r['series']=='ipca'}
    result=[]
    for period in sorted(p for p in months if p[4:] in ('03','06','09','12') and '201003'<=p<='202412'):
        end=int(period[:4])*12+int(period[4:])-1
        for count,method,variable in [(3,'compound_three_months','2263'),(12,'compound_twelve_months','2265')]:
            window=[f'{(end-i)//12}{(end-i)%12+1:02d}' for i in range(count-1,-1,-1)]
            selected=[months[p] for p in window if p in months];complete=len(selected)==count and all(r['status']=='ok' for r in selected)
            factor=None
            if complete:
                factor=Fraction(1)
                for row in selected:factor*=1+Fraction(*map(int,row['value_fraction']))/100
            row=dict(id='selic_effective_monthly|'+period+'|'+method,series='selic_effective_monthly',variable='BM12_TJOVER12',category='total',
                     period=period,method=method,unit='percent_period',status='ok' if complete else 'incomplete_source_window',
                     value_fraction=_fraction((factor-1)*100 if factor is not None else None),source_ids=[r['id'] for r in selected],source_count=len(selected),expected_source_count=count)
            result.append(row);price=prices.get((period,variable));valid=complete and price is not None and price['status']=='ok'
            denominator=1+Fraction(*map(int,price['value_fraction']))/100 if valid else None
            valid=valid and denominator>0
            realmethod='fisher_three_months' if count==3 else 'fisher_twelve_months'
            result.append(dict(row,id='real_policy_rate_expost|'+period+'|'+realmethod,series='real_policy_rate_expost',variable='Fisher_Selic_IPCA',
                method=realmethod,value_fraction=_fraction((factor/denominator-1)*100 if valid else None),status='ok' if valid else 'incomplete_source_window',
                source_ids=[row['id']]+([price['id']] if price else []),source_count=2 if price else 1,expected_source_count=2,
                limits=['ex_post_reference_before_taxes_and_costs','published_input_precision','not_neutral_rate_or_borrowing_cost']))
    return sorted(result,key=lambda r:r['id'])


def add_interest_context(context,context_pin,evidence,evidence_pin,output):
    """Append finite captured official interest, preserving the accepted SIDRA package."""
    context,evidence,output=Path(context).resolve(),Path(evidence).resolve(),Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if output==context or output in context.parents or context in output.parents or output in evidence.parents:
        raise ValueError('Macro interest output overlaps source')
    if digest(context/'manifest.json')!=context_pin or digest(evidence)!=evidence_pin:raise ValueError('Macro interest input pin mismatch')
    manifest=json.loads((context/'manifest.json').read_text(encoding='utf8'));proof=json.loads(evidence.read_text(encoding='utf8'))
    if manifest.get('contract')!=CONTRACT or proof.get('series')!='BM12_TJOVER12':raise ValueError('Macro interest contract mismatch')
    source=Path(proof['source_body']).resolve();raw=source.parent;receipts=proof['receipts']
    from urllib.parse import urlparse
    for receipt in receipts:
        path=(raw/receipt['body_file']).resolve()
        if (path.parent!=raw or receipt['status']!=200 or urlparse(receipt['url']).hostname not in ('www.ipeadata.gov.br','ipeadata.gov.br')
                or digest(path)!=receipt['sha256']):raise ValueError('Ipeadata receipt/hash mismatch')
    meta=next(r for r in receipts if "Metadados('" in r['url'] and '/Valores' not in r['url'])
    actual=json.loads((raw/meta['body_file']).read_bytes())['value']
    if len(actual)!=1 or actual[0]!=proof['metadata']:raise ValueError('Ipeadata documentary metadata mismatch')
    if not any(r['body_file']==source.name and 'Valores' in r['url'] for r in receipts):raise ValueError('Ipeadata values receipt missing')
    added=parse_ipea_monthly(source.read_bytes(),actual[0])
    if {r['period'] for r in added}!={f'{y}{m:02d}' for y in range(2009,2025) for m in range(1,13)}:
        raise ValueError('Ipeadata full192-month window required')
    for row in added:row['source_ref']=dict(evidence_file=str(evidence),expected_evidence_sha256=evidence_pin,metadata_sha256=meta['sha256'])
    tables={}
    with duckdb.connect(config={'threads':1,'memory_limit':'512MiB'}) as conn:
        for name in ('observations','quarterly'):
            entries=[e for e in manifest['files'] if e['file']==name+'.parquet']
            if len(entries)!=1 or digest(context/entries[0]['file'])!=entries[0]['sha256']:raise ValueError('Macro base table hash mismatch')
            tables[name]=[json.loads(p) for p, in conn.execute('select payload from read_parquet(?)',[str(context/entries[0]['file'])]).fetchall()]
    if any(r['series']=='selic_effective_monthly' for r in tables['observations']):raise ValueError('Interest already incorporated')
    extension=interest_panel(added,tables['quarterly']);tables['observations']+=added;tables['quarterly']+=extension
    output.mkdir(parents=True);files=[_write_table(output,n,r) for n,r in tables.items()]
    coverage=list(manifest['coverage'])
    for series,method in sorted({(r['series'],r['method']) for r in extension}):
        selected=[r for r in extension if r['series']==series and r['method']==method]
        coverage.append(dict(series=series,variable=selected[0]['variable'],category='total',method=method,expected_quarters=60,
                             observed_quarters=len(selected),valid_quarters=sum(r['status']=='ok' for r in selected),absent_periods=[],absences=[]))
    result=dict(manifest,files=files,tables={k:len(v) for k,v in tables.items()},coverage=coverage,
        interest_evidence=dict(file=str(evidence),expected_sha256=evidence_pin),derivation=dict(context=str(context),expected_manifest_sha256=context_pin),
        producer_sha256=digest(Path(__file__)))
    result['limits']=[s for s in manifest['limits'] if not s.startswith('Selic e juros reais')]+['Selic efetiva mensal disseminada pelo Ipeadata com fonte BCB; não é meta Copom','Juro real ex post pelo IPCA oficial com janela compatível; antes de tributos e custos','Meta anualizada e curva histórica não incorporadas']
    if digest(context/'manifest.json')!=context_pin or digest(evidence)!=evidence_pin:raise ValueError('Macro interest input changed')
    for receipt in receipts:
        if digest(raw/receipt['body_file'])!=receipt['sha256']:raise ValueError('Ipeadata body changed before acceptance')
    (output/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
    return result

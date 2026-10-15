"""Bounded, authenticated native-universe calculations; formulas live in analysis.

The unit-calculations stage is deliberately not an aggregated universe package.
Component observations use installed-profile and native-source references, while
all numeric and temporal fields retain the exact legacy mathematical semantics.
"""
from contextlib import ExitStack, closing
from copy import deepcopy
from pathlib import Path
import csv
import hashlib
import io
import json
import re

from . import ifdata_analysis as math

PROFILE_PATH=Path(__file__).with_name('ifdata-analysis-universe-profile-2010-2024.json')
CONTRACT='ifdata-universe-analysis-v1'
TABLES=('components','results','unit_periods','membership_links')
TYPES={'financial':'2','individual':'3','capital':'1'}


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)


def load_profile(profile_id='universe-2010-2024', expected_sha256=None):
    if profile_id!='universe-2010-2024':raise ValueError('Unknown installed universe profile')
    raw=PROFILE_PATH.read_bytes()
    if expected_sha256 is not None and hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('Universe profile hash mismatch')
    profile=math._json_unique(raw)
    if profile.get('contract')!='ifdata-analysis-universe-profile-2010-2024-v1' or profile.get('profile_id')!=profile_id:
        raise ValueError('Universe profile contract mismatch')
    for c in profile['contexts']:
        if hashlib.sha256(canonical(c['literal_context']).encode()).hexdigest()!=c['context_sha256']:
            raise ValueError('Universe literal context mismatch')
        if c['literal_context']['TipoInstituicao']!=TYPES[c['literal_context']['dataset']]:
            raise ValueError('Universe perspective mismatch')
    return profile


def prepare_opening(raw_root, output, profile_id, profile_expected_sha256):
    """Import only the already reviewed captured pages, never fetch a source."""
    from .ifdata_odata import import_package
    output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if not isinstance(profile_expected_sha256,str) or not re.fullmatch('[0-9a-f]{64}',profile_expected_sha256):
        raise ValueError('External profile pin required')
    policy=load_profile(profile_id,profile_expected_sha256)['opening_policy']
    root=Path(raw_root).resolve()
    def check():
        if math._digest_file(root/'manifesto.json')!=policy['raw_manifest_sha256']:
            raise ValueError('Reviewed opening raw manifest mismatch')
        for p in policy['pages']:
            if math._digest_file(math._contained(root,p['file']))!=p['sha256']:
                raise ValueError('Reviewed opening page mismatch')
    check()
    result=import_package(root,output,periods=['200912'],types=['2','3'],reports=['1','2'])
    check()
    return result


def opening_observation(profile,name,dataset,code,rows,next_rows,cadastro):
    """Apply the reviewed per-component predicate; missing is never a zero."""
    policy=profile['opening_policy'];component=math.COMPONENT_NAMES.get(name,name)
    empty=dict(period='200912',token=None,unit_key=(dataset,TYPES[dataset],code),
               definition_id=component,scale='BRL',window_rule='stock',binding={},sources=[],status='opening_not_released')
    if dataset not in policy['datasets'] or component not in policy['components']:return empty
    matches=[c for c in profile['contexts'] if c['component']==component and c['literal_context']['dataset']==dataset and '201003' in c['periods']]
    if len(matches)!=1:return empty
    context=matches[0];literal=context['literal_context']
    def selected(items,period):
        return [r for r in items if r.get('CodInst')==code and r.get('AnoMes')==period and all(
            type(r.get(k)) is type(v) and r.get(k)==v for k,v in literal.items() if k!='dataset')]
    before=selected(rows,'200912');after=selected(next_rows,'201003')
    a=cadastro.get((code,'200912'));b=cadastro.get((code,'201003'))
    empty.update(binding=deepcopy(context),definition_id=context['compatibility'])
    proof=dict(policy=policy['id'],opening_occurrences=len(before),comparison_occurrences=len(after),
               opening_cadastro=a,comparison_cadastro=b,changes={})
    empty['opening_proof']=proof
    if a and b:
        proof['changes']={k:dict(opening=v,comparison=b.get(k)) for k,v in a.items()
                          if k!='Data' and not k.startswith('source_') and v!=b.get(k)}
    if len(before)!=1 or len(after)!=1:return dict(empty,status='opening_occurrence_missing_or_ambiguous',sources=before)
    if not a or not b:return dict(empty,status='opening_cadastro_missing',sources=before)
    if any(a.get(k)!=b.get(k) for k in policy['identity_fields']):
        return dict(empty,status='opening_identity_changed',sources=before)
    empty.update(token=before[0]['Saldo'],sources=before,status='ok')
    if math._native_value(empty)[1] is not None:return dict(empty,token=None,status='opening_value_unavailable')
    if proof['changes']:empty['flags']=['opening_cadastro_classification_change']
    return empty


def component_periods(name,period,horizon):
    """Select only inputs the existing formula can consume, without successors."""
    end=math._period_date(period)
    if horizon=='point':return [period]
    if horizon=='ttm':return math.dependency_periods([period])
    previous=math._previous_quarter(end).strftime('%Y%m')
    if name in math.FLOW_COMPONENTS and period.endswith(('03','09')):return [period]
    return [previous,period]


class Writer:
    def __init__(self,output,table,stack):
        self.output,self.table,self.count,self.max_line=output,table,0,2*1024*1024
        self.js=stack.enter_context((output/(table+'.json')).open('w',encoding='utf-8'))
        self.cs=stack.enter_context((output/(table+'.csv')).open('w',encoding='utf-8',newline=''))
        self.writer=csv.writer(self.cs,quoting=csv.QUOTE_NOTNULL);self.writer.writerow(math.TABLE_COLUMNS)
        self.js.write('[')
    def append(self,row):
        payload=canonical(row);self.js.write((',' if self.count else '')+'\n'+payload)
        self.writer.writerow([row.get(k) for k in math.TABLE_COLUMNS[:-1]]+[payload]);self.count+=1
        self.max_line=max(self.max_line,len(payload.encode('utf-8'))*4+4096)
    def finish(self,conn):
        self.js.write('\n]\n' if self.count else ']\n');self.js.close();self.cs.close()
        columns='{'+','.join("'"+k+"':'VARCHAR'" for k in math.TABLE_COLUMNS)+'}'
        conn.execute('copy (select * from read_csv($source,header=true,auto_detect=false,columns='+columns+
            ",delim=',',quote='\"',escape='\"',nullstr='',allow_quoted_nulls=false,parallel=false,max_line_size=$limit)) "+
            'to $destination (format parquet,compression zstd,row_group_size 2048)',
            dict(source=str(self.output/(self.table+'.csv')),limit=str(self.max_line),destination=str(self.output/(self.table+'.parquet'))))
        return [dict(file=self.table+'.'+ext,sha256=math._digest_file(self.output/(self.table+'.'+ext)),rows=self.count) for ext in ('json','csv','parquet')]


def _window(conn,source,periods,dataset=None,opening=False,view="native"):
    from .ifdata_odata import COLUMNS
    from .ifdata_cadastro import FIELDS,ORIGIN
    root,manifest=source
    entries=[e for e in manifest['files'] if str(e['period']) in periods and (not opening or str(e['type'])==TYPES[dataset])]
    if not entries:return False
    fields=COLUMNS if dataset else FIELDS+ORIGIN
    for e in entries:
        if dataset and str(e.get('type'))!=TYPES[dataset]:raise ValueError('Native part perspective mismatch')
        conn.from_parquet(str(math._contained(root,e['file']))).create_view('part',replace=True)
        math._schema(conn,'part',fields)
        if conn.execute('select count(*) from part').fetchone()[0]!=e['rows']:raise ValueError('Native part count mismatch')
        field='AnoMes' if dataset else 'Data'
        if conn.execute('select count(*) from part where '+field+' is distinct from ?',[str(e['period'])]).fetchone()[0]:
            raise ValueError('Native part period mismatch')
        if dataset and conn.execute('select count(*) from part where TipoInstituicao is distinct from ?',[TYPES[dataset]]).fetchone()[0]:
            raise ValueError('Native value perspective mismatch')
    conn.from_parquet([str(math._contained(root,e['file'])) for e in entries]).create_view(view,replace=True)
    return True


def _observation_reference(observation):
    # All audit fields survive in components; formulas receive the very same
    # observation before replacement, hence no precision/window shortcut.
    return {'component_ref':observation['id']}


def _thin(row):
    result={k:deepcopy(row[k]) for k in ('id','period','token','unit_key','definition_id','scale','window_rule','status','flags') if k in row}
    result['binding']={'context_ref':row['binding']['context_sha256']} if row['binding'] else {}
    result['sources']=[{'component_ref':row['id']}] if row['sources'] else []
    return result


def _normalize_temporal(value):
    if isinstance(value,list):return [_normalize_temporal(v) for v in value]
    if not isinstance(value,dict):return value
    if 'token' in value and 'unit_key' in value and 'id' in value:return _observation_reference(value)
    return {k:_normalize_temporal(v) for k,v in value.items()}


def _compact_component(row):
    result=deepcopy(row)
    binding=result.pop('binding')
    result['binding_ref']=binding['context_sha256'] if binding else None
    # Literal native fields are reconstructed from binding + native identity;
    # provenance tokens remain literal (including null vs empty).
    literal=binding.get('literal_context',{})
    compressed=[]
    for source in result['sources']:
        compressed.append({k:v for k,v in source.items() if not (k in literal and k!='dataset' and type(v) is type(literal[k]) and v==literal[k])
                           and not (k in {'CodInst':result['code'],'AnoMes':result['period'],'Saldo':result['token']} and type(v) is type({'CodInst':result['code'],'AnoMes':result['period'],'Saldo':result['token']}[k]) and v=={'CodInst':result['code'],'AnoMes':result['period'],'Saldo':result['token']}[k])})
    result['sources']=compressed
    return result


def _expand_component(row,profile):
    result=deepcopy(row);ref=result.pop('binding_ref')
    result['binding']=deepcopy(next(c for c in profile['contexts'] if c['context_sha256']==ref)) if ref else {}
    literal={k:v for k,v in result['binding'].get('literal_context',{}).items() if k!='dataset'}
    result['sources']=[{**literal,'CodInst':result['code'],'AnoMes':result['period'],'Saldo':result['token'],**source} for source in result['sources']]
    return result


def build(config,output,*,batch_size=32):
    import duckdb
    from .ifdata_population import open_population,CONTRACT as POP_CONTRACT,_metadata
    from .ifdata_odata import CONTRACT as DATA_CONTRACT
    from .ifdata_cadastro import CONTRACT as CAD_CONTRACT
    from .ifdata_variable_catalog import CONTRACT as CAT_CONTRACT,query_catalog
    output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    required={'periods','datasets','profile_id','profile_expected_sha256','population'}
    if not isinstance(config,dict) or not required<=set(config) or set(config)-required-{'opening'}:raise ValueError('Invalid universe config')
    if type(batch_size) is not int or batch_size<1:raise ValueError('Positive batch size required')
    dependencies=math.dependency_periods(config['periods']);periods=sorted(config['periods']);datasets=config['datasets']
    if not isinstance(datasets,list) or not datasets or any(d not in TYPES for d in datasets) or len(set(datasets))!=len(datasets):raise ValueError('Invalid universe perspectives')
    pin=config['profile_expected_sha256']
    if not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{64}',pin):raise ValueError('External profile pin required')
    profile=load_profile(config['profile_id'],pin)
    poproot,pop=math._authenticate(config['population'],POP_CONTRACT,True)
    if not set(periods)<=set(pop['config']['periods']) or not set(datasets)<=set(pop['config']['datasets']):raise ValueError('Population scope mismatch')
    inputs=pop['config']['inputs']
    accepted={name:math._authenticate(inputs[name],CAT_CONTRACT if name=='catalogue' else CAD_CONTRACT if name=='cadastro' else DATA_CONTRACT)
              for name in ['catalogue','cadastro']+sorted(datasets)}
    for name in ['cadastro']+sorted(datasets):_metadata(accepted[name][1])
    for ds in datasets:
        if accepted['catalogue'][1]['inputs'].get(ds,{}).get('manifest_sha256')!=inputs[ds]['expected_manifest_sha256']:
            raise ValueError('Catalogue source lineage mismatch')
    catalog=query_catalog(accepted['catalogue'][0],'select * from catalogo_variaveis')
    catalogue={(canonical({k:r[k] for k in c['literal_context']}),str(p)) for c in profile['contexts'] for r in catalog
               if all(type(r.get(k)) is type(v) and r.get(k)==v for k,v in c['literal_context'].items()) for p in r['periodos']}
    if 'opening' in config:
        opening=math._authenticate(config['opening'],DATA_CONTRACT)
        policy=profile['opening_policy']
        if opening[1].get('source_manifest_sha256')!=policy['raw_manifest_sha256'] or inputs['cadastro']['expected_manifest_sha256']!=policy['cadastro_manifest_sha256']:
            raise ValueError('Unreviewed opening source/cadastro')
        if opening[1].get('selection')!={'periods':['200912'],'types':['2','3'],'reports':['1','2']}:raise ValueError('Unreviewed opening selection')
        allowed={p['sha256'] for p in policy['pages']}
        if any(e.get('source_sha256') not in allowed for e in opening[1]['files']):raise ValueError('Unreviewed opening pages')
        accepted['opening']=opening
    with ExitStack() as stack:
        population=stack.enter_context(open_population(poproot,config['population']['expected_manifest_sha256']))
        conn=stack.enter_context(duckdb.connect(config={'memory_limit':'512MiB','threads':1}))
        output.mkdir(parents=True,exist_ok=False)
        writers={t:Writer(output,t,stack) for t in TABLES}
        for period in periods:
            dates=math.dependency_periods([period])
            for dataset in sorted(datasets):
                units=[json.loads(r[0]) for r in population.execute('select payload from unit_periods where period=? and dataset=? order by code',[period,dataset]).fetchall()]
                native_present=_window(conn,accepted[dataset],dates,dataset,view="values_window")
                cad_present=_window(conn,accepted['cadastro'],dates,view='cadastro_window')
                opening_present='opening' in accepted and '200912' in dates and dataset!='capital' and _window(conn,accepted['opening'],['200912'],dataset,True,view='opening_window')
                accounts=sorted({c['literal_context']['Conta'] for c in profile['contexts'] if c['literal_context']['dataset']==dataset})
                for offset in range(0,len(units),batch_size):
                    lot=units[offset:offset+batch_size];codes=[u['code'] for u in lot]
                    native=math._records(conn.execute('select * from values_window where CodInst in (select unnest(?)) and Conta in (select unnest(?)) order by AnoMes,CodInst,NumeroRelatorio,Conta,source_file,source_row',[codes,accounts])) if native_present else []
                    cad=math._records(conn.execute('select * from cadastro_window where CodInst in (select unnest(?))',[codes])) if cad_present else []
                    cadres={(r['CodInst'],r['Data']):r for r in cad}
                    openings=math._records(conn.execute('select * from opening_window where CodInst in (select unnest(?))',[codes])) if opening_present else []
                    indexed={}
                    for r in native:indexed.setdefault((r['CodInst'],r['AnoMes']),[]).append(r)
                    for unit in lot:
                        code=unit['code'];uid=unit['unit_id'];cache={}
                        def component(name,p):
                            key=(name,p)
                            if key not in cache:
                                if p=='200912':
                                    ob=opening_observation(profile,name,dataset,code,openings,indexed.get((code,'201003'),[]),cadres) if opening_present else None
                                else:
                                    ob=math.resolve_component(profile,math.COMPONENT_NAMES.get(name,name),dataset,code,p,indexed.get((code,p),[]))
                                    if ob['binding'] and (canonical(ob['binding']['literal_context']),p) not in catalogue:
                                        ob.update(status='catalogue_context_missing',token=None)
                                if ob is None:return None
                                ob.update(id=hashlib.sha256((uid+'|'+name+'|'+p).encode()).hexdigest()[:32],component=name,dataset=dataset,code=code,status=ob.get('status','ok'),analysis_period=period)
                                cache[key]=ob
                            return cache[key]
                        metrics=[m for m in math.METRICS if (m in ('C3','C4'))==(dataset=='capital')]
                        for metric in metrics:
                            for horizon in (('quarter','ttm') if metric in math.FLOW_METRICS else ('point',)):
                                data={name:[_thin(ob) for p in component_periods(name,period,horizon) if p>='201003' or (p=='200912' and name in ('AT','PL','credit'))
                                            if (ob:=component(name,p)) is not None] for name in math.METRICS[metric]}
                                result=math.evaluate_metric(metric,dict(period=period,components=data,financial_statement=dataset in ('financial','individual'),prudential_bridge=dataset=='capital'),horizon)
                                result.update(id=uid+'|'+metric+'|'+horizon,unit_id=uid,unit_key=[dataset,TYPES[dataset],code],dataset=dataset,code=code,
                                              membership=unit['membership'],population_ref=uid,diagnostics={})
                                if metric=='Q1':
                                    observations=[component(n,period) for n in ('credit','provision_stock','credit_net_diagnostic')]
                                    parsed=[math._native_value(o) for o in observations]
                                    diag=dict(inputs=[_thin(o) for o in observations],status='unavailable',residual_fraction=None)
                                    if all(s is None for _,s in parsed):
                                        residual=parsed[0][0]+parsed[1][0]-parsed[2][0]
                                        diag.update(status='exact' if residual==0 else 'native_residual',residual_fraction=math._fraction_field(residual))
                                    result['diagnostics']['credit_identity']=diag
                                if metric in ('C3','C4'):
                                    result['diagnostics']['published_index']=_thin(component('IB_published_diagnostic' if metric=='C3' else 'ICP_published_diagnostic',period))
                                    result['diagnostics']['scale_comparison']='unverified_no_conversion_or_equality_imposed'
                                writers['results'].append(_normalize_temporal(result))
                        for key in sorted(cache):writers['components'].append(_compact_component(cache[key]))
                        writers['unit_periods'].append(dict(unit,id=uid,status='observed'))
                links=population.execute('select payload from membership_links where period=? and dataset=? order by link_id',[period,dataset])
                while row:=links.fetchone():
                    link=json.loads(row[0]);writers['membership_links'].append(dict(link,id=link['link_id'],status=link['membership']))
        files=[]
        for writer in writers.values():files.extend(writer.finish(conn))
        counts={t:w.count for t,w in writers.items()}
    # Persistent source mutation cannot receive an accepted output manifest.
    math._authenticate(config['population'],POP_CONTRACT,True)
    for name in accepted:math._authenticate(config['opening'] if name=='opening' else inputs[name])
    normalized=deepcopy(config);normalized['periods']=periods;normalized['datasets']=sorted(datasets)
    manifest=dict(contract=CONTRACT,stage='unit-calculations',config=normalized,inputs=inputs,profile_sha256=pin,
                  periods=periods,dependency_periods=dependencies,tables=counts,table_columns=list(math.TABLE_COLUMNS),files=files,
                  reference_contract='profile-context-and-window-component-v1',
                  limitations=['Native unit results; no final aggregates in this stage','Prudential own assets unknown; no financial proxy','Membership does not control native applicability','No constituent or issuer-control continuity inferred'])
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return manifest


def _validate_component(row,profile,contexts):
    """Close a normalized observation over its own finite typed context."""
    dataset=row.get('dataset');code=row.get('code');period=row.get('period')
    if dataset not in TYPES or row.get('unit_key')!=[dataset,TYPES[dataset],code]:
        raise ValueError('Component native identity mismatch')
    if period not in math.dependency_periods([row.get('analysis_period')]):
        raise ValueError('Component source period outside dependency window')
    ref=row.get('binding_ref')
    if ref is None:
        # Missing/ambiguous bindings are real unavailable states, not contexts
        # that may be reconstructed by name or borrowed from another source.
        if row.get('status') not in ('binding_unverified','ambiguous_binding','opening_not_released') or row.get('sources') or row.get('token') is not None:
            raise ValueError('Unbound component contains an unproved source')
        return
    context=contexts.get(ref)
    if context is None:raise ValueError('Unresolved profile reference')
    literal=context['literal_context'];component=math.COMPONENT_NAMES.get(row.get('component'),row.get('component'))
    if (literal['dataset']!=dataset or literal['TipoInstituicao']!=TYPES[dataset]
            or context['component']!=component or context['compatibility']!=row.get('definition_id')
            or context['window_rule']!=row.get('window_rule')
            or row.get('scale')!=('native_index_unverified' if 'diagnostic' in component else 'BRL')):
        raise ValueError('Typed component profile reference mismatch')
    expected_native={k:v for k,v in literal.items() if k!='dataset'}
    expected_native.update(CodInst=code,AnoMes=period)
    for source in row.get('sources',[]):
        if any(k in source and (type(source[k]) is not type(v) or source[k]!=v) for k,v in expected_native.items()):
            raise ValueError('Component source identity overrides its typed context')
    if period=='200912':
        policy=profile['opening_policy'];proof=row.get('opening_proof',{})
        if (dataset not in policy['datasets'] or component not in policy['components']
                or context['window_rule']!='stock' or policy['comparison_period'] not in context['periods']
                or proof.get('policy')!=policy['id']):
            raise ValueError('Component opening context not released')
    elif period not in context['periods']:
        raise ValueError('Component finite source period mismatch')


def _validate_context_references(value,allowed):
    if isinstance(value,list):
        for item in value:_validate_context_references(item,allowed)
    elif isinstance(value,dict):
        if 'context_ref' in value:
            if set(value)!={'context_ref'} or value['context_ref'] not in allowed:
                raise ValueError('Compatibility context reference mismatch')
        else:
            for key,item in value.items():
                if key in ('binding','bindings'):
                    bindings=item if key=='bindings' else [item]
                    if not isinstance(bindings,list) or any(not isinstance(binding,dict) or (binding and set(binding)!={'context_ref'}) for binding in bindings):
                        raise ValueError('Compatibility binding must use a profile reference')
                _validate_context_references(item,allowed)


def _reconcile_population(root,manifest):
    """Compare both proof directions to the authenticated population contract.

    The source reader already checks exact company/decision sets and scopes.
    Comparing the complete selected payload streams also catches coordinated
    changes to a unit's company list and its retained links.
    """
    from .ifdata_population import open_population,CONTRACT as POP_CONTRACT
    config=manifest['config'];descriptor=config['population']
    source_root,source=math._authenticate(descriptor,POP_CONTRACT,True)
    periods=config['periods'];datasets=config['datasets']
    if (not set(periods)<=set(source['config']['periods']) or not set(datasets)<=set(source['config']['datasets'])
            or manifest.get('inputs')!=source['config']['inputs']):
        raise ValueError('Universe population source scope mismatch')
    with open_population(source_root,descriptor['expected_manifest_sha256']) as population:
        for table,key,order in [('unit_periods','unit_id','period,dataset,code'),('membership_links','link_id','period,dataset,link_id')]:
            cursor=population.execute('select payload from '+table+' where period in (select unnest(?)) and dataset in (select unnest(?)) order by '+order,[periods,datasets])
            with closing(math._iter_json_array(root/(table+'.json'))) as actual:
                for batch in iter(lambda:cursor.fetchmany(256),[]):
                    for (payload,) in batch:
                        expected=json.loads(payload)
                        expected.update(id=expected[key],status='observed' if table=='unit_periods' else expected['membership'])
                        if next(actual,None)!=expected:
                            raise ValueError('Population membership proof reconciliation mismatch: '+table)
                if next(actual,None) is not None:
                    raise ValueError('Unexpected population membership proof: '+table)


def verify(output,expected_manifest_sha256):
    import duckdb
    root,m=math._authenticate(dict(root=str(output),expected_manifest_sha256=expected_manifest_sha256),CONTRACT,True)
    if m.get('stage')!='unit-calculations' or set(m.get('tables',{}))!=set(TABLES) or m.get('table_columns')!=list(math.TABLE_COLUMNS):
        raise ValueError('Universe stage/schema mismatch')
    if {e['file'] for e in m['files']}!={t+'.'+e for t in TABLES for e in ('json','csv','parquet')}:raise ValueError('Universe inventory mismatch')
    profile=load_profile(m['config']['profile_id'],m['profile_sha256'])
    known_contexts={c['context_sha256']:c for c in profile['contexts']}
    with duckdb.connect(config={'memory_limit':'512MiB','threads':1}) as con:
        for table in TABLES:
            con.from_parquet(str(root/(table+'.parquet'))).create_view(table)
            math._schema(con,table,math.TABLE_COLUMNS)
            if con.execute('select count(*)-count(distinct id) from '+table).fetchone()[0]:raise ValueError('Duplicate universe identity')
            cur=con.execute('select * from '+table);count=0
            buffer=io.StringIO(newline='');writer=csv.writer(buffer,quoting=csv.QUOTE_NOTNULL);digest=hashlib.sha256()
            writer.writerow(math.TABLE_COLUMNS);digest.update(buffer.getvalue().encode());buffer.seek(0);buffer.truncate(0)
            iterator=math._iter_json_array(root/(table+'.json'))
            try:
                for row in iterator:
                    count+=1
                    expected=tuple(row.get(k) for k in math.TABLE_COLUMNS[:-1])+(canonical(row),)
                    if cur.fetchone()!=expected:raise ValueError('Universe representations disagree')
                    if table=='components':_validate_component(row,profile,known_contexts)
                    writer.writerow(expected);digest.update(buffer.getvalue().encode());buffer.seek(0);buffer.truncate(0)
            finally:iterator.close()
            if cur.fetchone() is not None or count!=m['tables'][table] or digest.hexdigest()!=math._digest_file(root/(table+'.csv')):
                raise ValueError('Universe counts/representations mismatch')
            if any(e['rows']!=count for e in m['files'] if e['file'].startswith(table+'.')):raise ValueError('Universe part count mismatch')
        # Both streams have the same canonical period/dataset/code order.
        # Join one native unit at a time, never one SQL scan per result/ref.
        from itertools import groupby
        with ExitStack() as streams:
            comp_stream=math._iter_json_array(root/'components.json');streams.callback(comp_stream.close)
            result_stream=math._iter_json_array(root/'results.json');streams.callback(result_stream.close)
            unit_stream=math._iter_json_array(root/'unit_periods.json');streams.callback(unit_stream.close)
            groups=iter(groupby(comp_stream,lambda o:(o['dataset'],o['code'],o['analysis_period'])))
            results=iter(groupby(result_stream,lambda r:(r['dataset'],r['code'],r['period'])))
            for unit in unit_stream:
                key=(unit['dataset'],unit['code'],unit['period'])
                cg=next(groups,None);rg=next(results,None)
                if cg is None or rg is None or cg[0]!=key or rg[0]!=key:raise ValueError('Universe unit/result/component completeness mismatch')
                obs={o['id']:o for o in cg[1]};seen=set()
                for result in rg[1]:
                    if result['unit_id']!=unit['unit_id'] or result['unit_key']!=[unit['dataset'],unit['TipoInstituicao'],unit['code']] or result['membership']!=unit['membership']:
                        raise ValueError('Universe result/unit identity mismatch')
                    metric_key=(result['metric'],result['horizon'])
                    if result['id']!=unit['unit_id']+'|'+result['metric']+'|'+result['horizon'] or metric_key in seen:
                        raise ValueError('Duplicate or noncanonical native result identity')
                    seen.add(metric_key)
                    if set(result['components'])!=set(math.METRICS.get(result['metric'],())):
                        raise ValueError('Result component set mismatch')
                    for name,temporal in result['components'].items():
                        for ref in _references(temporal):
                            if ref not in obs:raise ValueError('Unresolved component reference')
                            if obs[ref]['component']!=name:raise ValueError('Component reference kind mismatch')
                        allowed={ob['binding_ref'] for ob in obs.values() if ob['component']==name and ob['binding_ref'] is not None}
                        _validate_context_references(temporal,allowed)
                    for ref in _references(result):
                        if ref not in obs:raise ValueError('Unresolved component reference')
                        ob=obs[ref]
                        if ob['analysis_period']!=result['period'] or ob['unit_key']!=result['unit_key']:raise ValueError('Component reference scope mismatch')
                expected={(metric,h) for metric in math.METRICS if (metric in ('C3','C4'))==(unit['dataset']=='capital')
                          for h in (('quarter','ttm') if metric in math.FLOW_METRICS else ('point',))}
                if seen!=expected:raise ValueError('Missing or extra native metric')
            if next(groups,None) is not None or next(results,None) is not None:raise ValueError('Orphan calculation group')
        if con.execute("select count(*) from membership_links l left join unit_periods u on json_extract_string(l.payload,'$.unit_id')=u.id where u.id is null").fetchone()[0]:
            raise ValueError('Orphan membership reference')
    _reconcile_population(root,m)
    return m


def _references(value):
    if isinstance(value,list):
        for v in value:yield from _references(v)
    elif isinstance(value,dict):
        if 'component_ref' in value:
            if set(value)!={'component_ref'}:raise ValueError('Invalid component reference representation')
            yield value['component_ref']
        else:
            for v in value.values():yield from _references(v)


def _resolve(value,components):
    if isinstance(value,list):return [_resolve(v,components) for v in value]
    if not isinstance(value,dict):return value
    if set(value)=={'component_ref'}:return deepcopy(components[value['component_ref']])
    return {k:_resolve(v,components) for k,v in value.items()}


def resolve_result(output,expected_manifest_sha256,result_id):
    import duckdb
    manifest=verify(output,expected_manifest_sha256);root=Path(output)
    profile=load_profile(manifest['config']['profile_id'],manifest['profile_sha256'])
    with duckdb.connect(config={'memory_limit':'512MiB','threads':1}) as con:
        row=con.execute('select payload from read_parquet(?) where id=?',[str(root/'results.parquet'),result_id]).fetchone()
        if row is None:raise KeyError(result_id)
        result=json.loads(row[0]);ids=sorted(set(_references(result)))
        obs=con.execute('select payload from read_parquet(?) where id in (select unnest(?))',[str(root/'components.parquet'),ids]).fetchall()
        expanded={r['id']:_expand_component(r,profile) for (payload,) in obs for r in [json.loads(payload)]}
    return _resolve(result,expanded)


def _economic_signature(result):
    fields=('status','value','value_fraction','numerator_fraction','denominator_fraction','applicability','flags','limits','economic_representativeness')
    signature={k:result.get(k) for k in fields}
    def observation_signature(v):
        fields=('period','token','unit_key','definition_id','scale','window_rule','flags')
        ob={k:v.get(k,[] if k=='flags' else None) for k in fields}
        ob['status']=v.get('status','ok')
        ob['context_sha256']=v.get('binding',{}).get('context_sha256')
        ob['sources']=v.get('sources',[])
        return ob
    def diagnostics(v):
        if isinstance(v,list):return [diagnostics(x) for x in v]
        if not isinstance(v,dict):return v
        if 'token' in v and 'unit_key' in v:return observation_signature(v)
        return {k:diagnostics(x) for k,x in v.items()}
    signature['diagnostics']=diagnostics(result.get('diagnostics',{}))
    def temporal_signature(value,dates):
        if isinstance(value,list):return [temporal_signature(v,dates) for v in value]
        if not isinstance(value,dict):return value
        if 'token' in value and 'unit_key' in value:return observation_signature(value)
        # Full legacy bindings and their installed-profile references denote
        # the same context. Every surrounding compatibility conclusion and
        # temporal derivation field remains in the recursive signature.
        if set(value)=={'context_ref'}:return {'context_sha256':value['context_ref']}
        if 'context_sha256' in value and 'literal_context' in value:
            return {'context_sha256':value['context_sha256']}
        normalized={}
        for key,item in value.items():
            if key=='inputs' and isinstance(item,list):
                item=[v for v in item if not (isinstance(v,dict) and 'token' in v and 'unit_key' in v and v.get('period') not in dates)]
            normalized[key]=temporal_signature(item,dates)
        return normalized
    signature['components']={name:temporal_signature(value,set(component_periods(name,result['period'],result['horizon'])))
                             for name,value in result['components'].items()}
    return signature


def compare(output,expected_manifest_sha256,baseline,baseline_manifest_sha256):
    """Stream both contracts; retain only baseline keys/digests in memory.

    Full baseline signatures are spooled to an ephemeral SQLite file, fetched
    only for differences. Every unmatched baseline key remains nominal.
    """
    from itertools import groupby
    import sqlite3
    import tempfile
    manifest=verify(output,expected_manifest_sha256);root=Path(output)
    oldroot,old=math._authenticate(dict(root=str(baseline),expected_manifest_sha256=baseline_manifest_sha256),math.ANALYSIS_CONTRACT,True)
    for ds in ('financial','capital','cadastro','catalogue'):
        if ds in manifest['inputs'] and old['inputs'][ds]['expected_manifest_sha256']!=manifest['inputs'][ds]['expected_manifest_sha256']:
            raise ValueError('Baseline native source pins differ')
    profile=load_profile(manifest['config']['profile_id'],manifest['profile_sha256'])
    if old['profile_sha256']!=profile['legacy_profile_sha256']:raise ValueError('Baseline profile is outside reviewed lineage')
    report=dict(matched=0,differences=[],missing_baseline_keys=[],outside_selected_scope=0,universe_only_count=0,
                baseline_manifest_sha256=baseline_manifest_sha256,universe_manifest_sha256=expected_manifest_sha256,
                comparison='exact economic fields and relevant temporal observations; no rounding')
    expected={};present_units=set();source_periods={}
    for ds in manifest['config']['datasets']:
        _,source=math._authenticate(manifest['inputs'][ds])
        source_periods[ds]={str(e['period']) for e in source['files']}
    with tempfile.TemporaryDirectory(prefix='ifdata-baseline-') as temporary, closing(sqlite3.connect(str(Path(temporary)/'signatures.sqlite'))) as spool, ExitStack() as streams:
        spool.execute('create table signatures (id text primary key, signature text)')
        legacy=math._iter_json_array(oldroot/'results.json');streams.callback(legacy.close)
        for row in legacy:
            if row['period'] not in manifest['periods'] or row['dataset'] not in manifest['config']['datasets']:
                report['outside_selected_scope']+=1;continue
            uid='|'.join((row['dataset'],TYPES[row['dataset']],row['code'],row['period']))
            identifier=uid+'|'+row['metric']+'|'+row['horizon']
            signature=canonical(_economic_signature(row))
            expected[identifier]=dict(key={k:row[k] for k in ('dataset','code','period','metric','horizon')},
                uid=uid,sha256=hashlib.sha256(signature.encode()).hexdigest(),status=row['status'],value_fraction=row.get('value_fraction'))
            spool.execute('insert into signatures values (?,?)',(identifier,signature))
        spool.commit()
        comp_stream=math._iter_json_array(root/'components.json');streams.callback(comp_stream.close)
        result_stream=math._iter_json_array(root/'results.json');streams.callback(result_stream.close)
        groups=iter(groupby(comp_stream,lambda o:(o['dataset'],o['code'],o['analysis_period'])))
        baseline_units={e['uid'] for e in expected.values()}
        for key,results in groupby(result_stream,lambda r:(r['dataset'],r['code'],r['period'])):
            ck,components=next(groups)
            if ck!=key:raise ValueError('Calculation component ordering mismatch')
            uid='|'.join((key[0],TYPES[key[0]],key[1],key[2]))
            if uid not in baseline_units:
                for _ in components:pass
                report['universe_only_count']+=sum(1 for _ in results);continue
            present_units.add(uid);expanded={r['id']:_expand_component(r,profile) for r in components}
            for row in results:
                previous=expected.pop(row['id'],None)
                if previous is None:report['universe_only_count']+=1;continue
                signature=_economic_signature(_resolve(row,expanded));encoded=canonical(signature)
                if hashlib.sha256(encoded.encode()).hexdigest()==previous['sha256']:report['matched']+=1
                else:
                    oldsig=json.loads(spool.execute('select signature from signatures where id=?',(row['id'],)).fetchone()[0])
                    report['differences'].append(dict(previous['key'],fields=[k for k in oldsig if oldsig[k]!=signature[k]],baseline=oldsig,universe=signature))
        for identifier,previous in sorted(expected.items()):
            key=previous['key'];captured=key['period'] in source_periods[key['dataset']]
            cause='missing_universe_result' if previous['uid'] in present_units else 'native_unit_not_reported_in_population' if captured else 'native_source_period_not_captured'
            report['missing_baseline_keys'].append(dict(key,cause=cause,baseline_status=previous['status'],baseline_value_fraction=previous['value_fraction']))
    report['status']='different' if report['differences'] or any(r['cause']=='missing_universe_result' or r['baseline_value_fraction'] is not None for r in report['missing_baseline_keys']) else 'exact_on_native_overlap'
    return report


def query(output,expected_manifest_sha256,sql):
    import duckdb
    manifest=verify(output,expected_manifest_sha256);root=Path(output)
    import tempfile
    # An ephemeral on-disk database keeps the authenticated snapshot readable
    # after external access is disabled without materializing it in RAM.
    with tempfile.TemporaryDirectory(prefix='ifdata-universe-query-') as temporary, duckdb.connect(str(Path(temporary)/'query.duckdb'),config={'memory_limit':'512MiB','threads':1,'autoload_known_extensions':False,'autoinstall_known_extensions':False}) as con:
        for table in manifest['tables']:con.execute('create table '+table+' as select * from read_parquet(?)',[str(root/(table+'.parquet'))])
        con.execute('set enable_external_access=false');statements=con.extract_statements(sql)
        if len(statements)!=1 or statements[0].type!=duckdb.StatementType.SELECT:raise ValueError('Query must be one SELECT')
        cur=con.execute(sql);fields=[c[0] for c in cur.description];rows=cur.fetchmany(10001)
        if len(rows)>10000:raise ValueError('Query row limit exceeded; select an explicit smaller scope')
        return [dict(zip(fields,row)) for row in rows]

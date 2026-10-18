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
from fractions import Fraction

from . import ifdata_analysis as math

PROFILE_PATH=Path(__file__).with_name('ifdata-analysis-universe-profile-2010-2024.json')
CONTRACT='ifdata-universe-analysis-v1'
TABLES=('components','results','unit_periods','membership_links')
TYPES={'financial':'2','individual':'3','capital':'1'}
DERIVED_TABLES=('unit_coverage','aggregates','distributions','segment_coverage','cohort_comparisons')
FINAL_TABLES=TABLES+DERIVED_TABLES
AXES=('Tcb','Td','Tc','Sr','Atividade','SegmentoTb')
COHORTS=('total','sample','remaining','unknown')
SELECTIVE_AXES=('Tcb','Td','Tc','Sr','SegmentoTb')
PROFIT_BRIDGE_PERIODS=('201803','201806','201809','201812','201903')
PROFIT_BRIDGE_WINDOWS={
    '201903':PROFIT_BRIDGE_PERIODS,
    '201906':('201806','201809','201812','201903','201906'),
    '201909':('201809','201812','201903','201906','201909')}
PROFIT_BRIDGE_ID='LL-native-before-capital-remuneration-201903-v1'
CAIXA_TRANSITION_PERIODS=('202109','202112','202203','202206')
CAIXA_TRANSITION_ID='caixa-financial-observed-perimeter-202109-v1'

TERRA_HISTORY_ID='terra-individual-history-financial-202412-v1'
TERRA_HISTORY_PERIODS=('202312','202403','202406','202409','202412')
TERRA_HISTORY_METRICS=('R1','R2','Q2','E2-B','RS','E3','R4','R5')


def bridge_terra_history(observations,individual,cadastro_rows,*,profile,period,metric,horizon):
    """Explicit same-institution history bridge approved in Issue154.

    Native Individual bindings/tokens remain Individual. Only analytical unit
    and compatibility identities align with the observed Financial endpoint.
    This never creates Financial units in dates absent from that source.
    """
    original=deepcopy(observations)
    proof=dict(rule=TERRA_HISTORY_ID,released=False,reason='unreviewed_target',replacements=[],
        limits=['Individual history is an explicit analytical bridge, not native Financial data',
                'Historical overlap evidence does not certify all missing Financial dates',
                'No new Financial unit-periods or general cross-perspective equivalence'])
    if period!='202412' or metric not in TERRA_HISTORY_METRICS or horizon not in ('quarter','ttm'):return original,proof
    names=math.METRICS.get(metric,math.COMPLEMENT_METRICS.get(metric))
    if set(observations)!=set(names) or set(individual)!=set(names):return original,proof
    target=('financial','2','03751794');source=('individual','3','03751794');dates=list(TERRA_HISTORY_PERIODS)
    cad={};proof['reason']='dated_identity_not_proven'
    for row in cadastro_rows:
        key=(row.get('Data'),row.get('CodInst'))
        if key in cad:return original,proof
        cad[key]=row
    for p in dates:
        row=cad.get((p,'03751794'))
        if not row or any(row.get(k)!=v for k,v in dict(CnpjInstituicaoLider='03751794',Td='I',
                CodConglomeradoFinanceiro=None,CodConglomeradoPrudencial='C0084514').items()):return original,proof
    changes=[];proof['reason']='native_history_not_verified'
    for name in names:
        if ([o.get('period') for o in observations[name]]!=dates or
            [o.get('period') for o in individual[name]]!=dates):return original,proof
        role=math.COMPONENT_NAMES[name]
        for index,p in enumerate(dates):
            needed=index>=3 if horizon=='quarter' else (index>0 if name in math.FLOW_COMPONENTS else True)
            if not needed:continue
            old=observations[name][index];native=individual[name][index]
            contexts={}
            for ds in ('financial','individual'):
                matches=[c for c in profile['contexts'] if c['component']==role and c['literal_context']['dataset']==ds and p in c['periods']]
                if len(matches)!=1:return original,proof
                contexts[ds]=matches[0]
            a,b=contexts['financial'],contexts['individual']
            def semantic(ctx):return {k:v for k,v in ctx['literal_context'].items() if k not in ('dataset','TipoInstituicao')}
            if semantic(a)!=semantic(b) or a['window_rule']!=b['window_rule']:return original,proof
            if (tuple(old.get('unit_key',()))!=target or old.get('binding')!=a or old.get('definition_id')!=a['compatibility'] or
                old.get('scale')!='BRL' or old.get('window_rule')!=a['window_rule'] or
                tuple(native.get('unit_key',()))!=source or native.get('binding')!=b or
                native.get('definition_id')!=b['compatibility'] or native.get('scale')!='BRL' or
                native.get('window_rule')!=b['window_rule'] or math._native_value(native)[1] is not None or not native.get('sources')):return original,proof
            literal=b['literal_context']
            if any(r.get('CodInst')!='03751794' or r.get('AnoMes')!=p or r.get('Saldo')!=native['token'] or
                   any(type(r.get(k)) is not type(v) or r.get(k)!=v for k,v in literal.items() if k!='dataset') for r in native['sources']):return original,proof
            if p=='202412':
                if math._native_value(old)[1] is not None or old['token']!=native['token'] or not old.get('sources'):return original,proof
                if any(r.get('CodInst')!='03751794' or r.get('AnoMes')!=p or r.get('Saldo')!=old['token'] or
                       any(type(r.get(k)) is not type(v) or r.get(k)!=v for k,v in a['literal_context'].items() if k!='dataset') for r in old['sources']):return original,proof
                continue
            if old.get('status')!='binding_missing' or old.get('token') is not None:return original,proof
            value=deepcopy(native)
            value.update(id=hashlib.sha256((str(old.get('id'))+'|'+TERRA_HISTORY_ID).encode()).hexdigest()[:32],
                unit_key=target,native_unit_key=deepcopy(native['unit_key']),native_definition_id=native['definition_id'],
                definition_id=a['compatibility'],reporting_transition=dict(rule=TERRA_HISTORY_ID,
                    source_period=p,source_unit_key=list(source),analysis_unit_key=list(target),analytical_definition_id=a['compatibility']),
                flags=sorted(set(native.get('flags',[])+['terra_individual_history_bridge'])))
            changes.append((name,index,value))
    if not changes:return original,proof
    for name,index,value in changes:
        original[name][index]=value
        proof['replacements'].append(dict(component=name,period=value['period'],native_unit_key=value['native_unit_key'],analytical_component_id=value['id']))
    proof.update(released=True,reason='approved_finite_same_institution_history',metric=metric,horizon=horizon,
        analysis_period=period,cadastro_evidence=deepcopy(cadastro_rows))
    return original,proof


def recalculate_terra_history(composition,expected_manifest_sha256,output):
    """Produce only sixteen Terra202412 contributions, retaining their originals."""
    from time import perf_counter
    import duckdb
    from .ifdata_odata import CONTRACT as DATA_CONTRACT
    from .ifdata_cadastro import CONTRACT as CAD_CONTRACT
    from .ifdata_variable_catalog import CONTRACT as CAT_CONTRACT,query_catalog
    started=perf_counter();output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    consumed={};guards={}
    def identity(path):
        s=_ordinary(path).stat();return s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns
    def source(spec,contract):
        root=Path(spec['root']).resolve();path=root/'manifest.json';pin=spec['expected_manifest_sha256']
        if output==root or root in output.parents or output in root.parents:raise ValueError('Terra output overlaps source')
        if not isinstance(pin,str) or not re.fullmatch('[a-f0-9]{64}',pin) or math._digest_file(path)!=pin:raise ValueError('Terra source pin mismatch')
        m=math._json_unique(path.read_bytes())
        if m.get('contract')!=contract:raise ValueError('Terra source contract mismatch')
        consumed[path]=pin;guards[path]=identity(path)
        return root,m
    def consume(root,m,name):
        entries=[e for e in m['files'] if e['file']==name]
        if len(entries)!=1:raise ValueError('Missing or ambiguous Terra source inventory')
        e=entries[0];_capture_payload(root,e);path=root/e['file'];consumed[path]=e['sha256'];guards[path]=identity(path)
        return path
    root,full=source(dict(root=str(composition),expected_manifest_sha256=expected_manifest_sha256),COMPOSITION_CONTRACT)
    def guard_sources(value):
        if isinstance(value,dict):
            if isinstance(value.get('root'),str):
                declared=Path(value['root']).resolve()
                if output==declared or declared in output.parents or output in declared.parents:
                    raise ValueError('Terra output overlaps source')
            for nested in value.values():guard_sources(nested)
        elif isinstance(value,list):
            for nested in value:guard_sources(nested)
    guard_sources(full['config'])
    base,main=source(full['config']['baseline'],CONTRACT)
    if main.get('stage')!='coverage-and-aggregation':raise ValueError('Admitted baseline required')
    profile=load_profile(expected_sha256=main['profile_sha256']);consumed[PROFILE_PATH]=main['profile_sha256'];guards[PROFILE_PATH]=identity(PROFILE_PATH)
    sources={};partitions={};dates=list(TERRA_HISTORY_PERIODS)
    for name,contract in [('financial',DATA_CONTRACT),('individual',DATA_CONTRACT),('cadastro',CAD_CONTRACT),('catalogue',CAT_CONTRACT)]:
        sr,sm=source(main['inputs'][name],contract);sources[name]=(sr,sm)
        entries=sm['files'] if name=='catalogue' else [e for e in sm['files'] if str(e.get('period')) in dates]
        if name!='catalogue' and (len(entries)!=5 or {str(e['period']) for e in entries}!=set(dates)):raise ValueError('Missing Terra dependency partition')
        for e in entries:consume(sr,sm,e['file'])
        partitions[name]=entries
    profile=compile_complement_profile(profile,query_catalog(sources['catalogue'][0],'select * from catalogo_variaveis'),['financial','individual'])
    coverage_path=consume(root,full,'unit_coverage.parquet')
    with duckdb.connect(config={'threads':1,'memory_limit':'512MiB'}) as conn:
        originals=math._records(conn.execute("select payload from read_parquet(?) where dataset='financial' and code='03751794' and period='202412'",[str(coverage_path)]))
        originals=[math._json_unique(r['payload'].encode()) for r in originals if math._json_unique(r['payload'].encode())['metric'] in TERRA_HISTORY_METRICS]
        native={}
        for ds in ('financial','individual'):
            _window(conn,sources[ds],dates,dataset=ds,view='native_'+ds)
            native[ds]=math._records(conn.execute("select * from native_"+ds+" where CodInst='03751794' and NumeroRelatorio in ('1','2','4')"))
        cr,cm=sources['cadastro'];cad=math._records(conn.execute("select * from read_parquet(?) where CodInst='03751794'",[[str(cr/e['file']) for e in partitions['cadastro']]]))
    expected={(m,h) for m in TERRA_HISTORY_METRICS for h in ('quarter','ttm')}
    keys=[(r['metric'],r['horizon']) for r in originals]
    if len(keys)!=16 or set(keys)!=expected:raise ValueError('Exact sixteen observed Terra contributions required')
    if any(r.get('unit_key')!=['financial','2','03751794'] or r.get('unit_id')!='financial|2|03751794|202412' or r.get('row_kind')!='native_unit' for r in originals):raise ValueError('Terra reporting identity mismatch')
    observations={};components={}
    for name in sorted({n for m in TERRA_HISTORY_METRICS for n in math.METRICS.get(m,math.COMPLEMENT_METRICS.get(m))}):
        for ds in ('financial','individual'):
            observations[ds,name]=[]
            for p in dates:
                ob=math.resolve_component(profile,math.COMPONENT_NAMES[name],ds,'03751794',p,native[ds])
                ob.update(id=hashlib.sha256((TERRA_HISTORY_ID+'|'+ds+'|'+name+'|'+p).encode()).hexdigest()[:32],
                    component=name,dataset=ds,code='03751794',analysis_period='202412',status=ob.get('status','ok'))
                components[ob['id']]=ob;observations[ds,name].append(ob)
    results=[];coverage=[]
    for old in originals:
        metric,horizon=old['metric'],old['horizon'];names=math.METRICS.get(metric,math.COMPLEMENT_METRICS.get(metric))
        before={n:observations['financial',n] for n in names};individual={n:observations['individual',n] for n in names}
        original_result=math.evaluate_metric(metric,dict(period='202412',components=before,financial_statement=True),horizon)
        if _composition_result_signature(original_result)!=_composition_result_signature(old):raise ValueError('Original Terra calculation differs from accepted economic result')
        bridged,proof=bridge_terra_history(before,individual,cad,profile=profile,period='202412',metric=metric,horizon=horizon)
        if not proof['released']:raise ValueError('Terra bridge not released: '+metric+'/'+horizon+'/'+proof['reason'])
        for rows in bridged.values():
            for ob in rows:components[ob['id']]=ob
        result=math.evaluate_metric(metric,dict(period='202412',components={n:[_thin(o) for o in rows] for n,rows in bridged.items()},financial_statement=True),horizon)
        result.update(id=old['result_id']+'|'+TERRA_HISTORY_ID,unit_id=old['unit_id'],unit_key=old['unit_key'],dataset='financial',code='03751794',
            membership=old['membership'],baseline_status=old['status'],reporting_transition=proof)
        result['flags']=sorted(set(result.get('flags',[])+['terra_individual_history_bridge']))
        row=deepcopy(old)
        for key in ('status','applicability','applicability_evidence','value_fraction','numerator_fraction','denominator_fraction','flags','limits','annual_summary'):row[key]=deepcopy(result.get(key))
        row.update(result_id=result['id'],reporting_transition=proof,prior_origin=deepcopy(old['origin']))
        row['flags']=sorted(set(row['flags']+old.get('flags',[])))
        results.append(_normalize_temporal(result));coverage.append(row)
    for p,pin in consumed.items():
        if identity(p)!=guards[p] or math._digest_file(p)!=pin:raise ValueError('Terra consumed source changed')
    output.mkdir(parents=True);tables=dict(components=list(components.values()),results=results,unit_coverage=coverage,original_unit_coverage=originals);files=[]
    with ExitStack() as stack,duckdb.connect(config={'threads':1,'memory_limit':'256MiB'}) as conn:
        for table,rows in tables.items():
            writer=Writer(output,table,stack)
            for row in rows:writer.append(row)
            files.extend(writer.finish(conn))
    manifest=dict(contract='ifdata-terra-history-analysis-v1',scope=dict(dataset='financial',code='03751794',periods=['202412'],metrics=list(TERRA_HISTORY_METRICS),horizons=['quarter','ttm']),
        composition=dict(root=str(root),expected_manifest_sha256=expected_manifest_sha256),baseline=full['config']['baseline'],bridge_rule=TERRA_HISTORY_ID,
        dependency_periods=dates,native_partitions=partitions,profile_sha256=main['profile_sha256'],tables={t:len(rows) for t,rows in tables.items()},files=files,
        consumed_files=[dict(file=str(p),sha256=h) for p,h in sorted(consumed.items(),key=lambda v:str(v[0]))],
        producer_sha256=math._digest_file(Path(__file__)),elapsed_seconds=perf_counter()-started,
        limits=['Explicit Individual-to-Financial dependency bridge for Terra202412 only','Original contributions retained; no new Financial unit-periods','Patch only; aggregate with unchanged contributions'])
    (output/'manifest.json').write_text(canonical(manifest)+'\n',encoding='utf8')
    return manifest


def bridge_caixa_transition(observations,predecessor,cadastro_rows,*,period,metric,horizon='ttm'):
    """Nominated reporting lineage, not a constant-perimeter reconstruction.

    Original native source identities/bindings/tokens are retained. Only the
    analytical unit identity is aligned for the existing temporal arithmetic.
    June2021 published investment/MEP discrepancies remain an explicit limit.
    """
    original=deepcopy(observations)
    proof=dict(rule=CAIXA_TRANSITION_ID,released=False,reason='unreviewed_target',
               constant_perimeter_certified=False,replacements=[],
               limits=['Observed historical perimeter changes; no retrospective consolidation',
                       'June2021 investment/equity-method differences remain unreconciled',
                       'No addition of DTVM balances or substitution from corporate consolidated accounts'])
    if period not in CAIXA_TRANSITION_PERIODS or metric not in ('R1','R2') or horizon!='ttm':return original,proof
    periods=math.dependency_periods([period]);names=math.METRICS[metric]
    if set(observations)!=set(names) or set(predecessor)!=set(names):return original,proof
    target=('financial','2','C0051626');source=('financial','2','00360305')
    for name in names:
        if ([x.get('period') for x in observations[name]]!=periods or
            [x.get('period') for x in predecessor[name]]!=periods or
            any(tuple(x.get('unit_key',()))!=target for x in observations[name])):return original,proof
    proof['reason']='dated_link_not_proven';cad={}
    for row in cadastro_rows:
        p=row.get('Data');code=row.get('CodInst')
        if p not in periods:continue
        key=(p,code)
        if key in cad:return original,proof
        cad[key]=row
    for p in periods:
        bank=cad.get((p,'00360305'))
        if not bank or bank.get('CnpjInstituicaoLider')!='00360305':return original,proof
        if p<'202109':
            if bank.get('CodConglomeradoFinanceiro') is not None or cad.get((p,'C0051626')):return original,proof
        else:
            for code in ('00360305','C0051626','42040639'):
                row=cad.get((p,code))
                if not row or row.get('CnpjInstituicaoLider')!='00360305' or row.get('CodConglomeradoFinanceiro')!='C0051626':return original,proof
            linked=[row for (date,code),row in cad.items() if date==p and row.get('CodConglomeradoFinanceiro')=='C0051626']
            if any(row.get('CnpjInstituicaoLider')!='00360305' for row in linked):return original,proof
            members={row['CodInst'] for row in linked}
            if not members<= {'00360305','C0051626','42040639','C0080738'}:return original,proof
    profile=load_profile();replacements=[]
    proof['reason']='predecessor_not_verified'
    for name in names:
        for index,p in enumerate(periods):
            # At June/December targets the opening LL precedes a native Q3/Q1;
            # it is not consumed, unlike the opening stock used in the mean.
            if p>='202109' or (name=='LL' and index==0 and period.endswith(('06','12'))):continue
            old=observations[name][index];new=predecessor[name][index]
            contexts=[c for c in profile['contexts'] if c['component']==name and c['literal_context']['dataset']=='financial' and p in c['periods']]
            if len(contexts)!=1:return original,proof
            context=contexts[0]
            if (old.get('status')!='binding_missing' or old.get('token') is not None or
                tuple(new.get('unit_key',()))!=source or new.get('status','ok')!='ok' or
                new.get('definition_id')!=context['compatibility'] or old.get('definition_id')!=context['compatibility'] or
                new.get('scale')!='BRL' or new.get('window_rule')!=context['window_rule'] or
                old.get('scale')!='BRL' or old.get('window_rule')!=context['window_rule'] or
                new.get('binding')!=context or old.get('binding')!=context or
                not new.get('sources') or math._native_value(new)[1] is not None):return original,proof
            literal=context['literal_context']
            if any(n.get('CodInst')!='00360305' or n.get('AnoMes')!=p or
                   n.get('Saldo')!=new['token'] or
                   any(type(n.get(k)) is not type(v) or n.get(k)!=v for k,v in literal.items() if k!='dataset')
                   for n in new['sources']):return original,proof
            value=deepcopy(new)
            value.update(id=hashlib.sha256((str(old.get('id'))+'|'+CAIXA_TRANSITION_ID).encode()).hexdigest()[:32],
                         unit_key=target,native_unit_key=deepcopy(new['unit_key']),
                         reporting_transition=dict(rule=CAIXA_TRANSITION_ID,observed_perimeter=True,
                             source_period=p,source_unit_key=list(source),analysis_unit_key=list(target)),
                         flags=sorted(set(new.get('flags',[])+['caixa_observed_perimeter_transition'])))
            replacements.append((name,index,value))
    if not replacements:return original,proof
    for name,index,value in replacements:
        original[name][index]=value
        proof['replacements'].append(dict(component=name,period=value['period'],
            native_unit_key=value['native_unit_key'],analytical_component_id=value['id']))
    proof.update(released=True,reason='reviewed_observed_reporting_lineage',metric=metric,analysis_period=period,
                 cadastro_evidence=[deepcopy(row) for (p,code),row in sorted(cad.items()) if code in ('00360305','C0051626','42040639','C0080738')])
    return original,proof


def bridge_profit_201903(observations,native_rows,cadastro,*,period='201903'):
    """Reviewed finite semantic bridge; native bindings/tokens never change.

    Financial conglomerates use their own published native profit, without
    fiscal normalization. IPs/consortia additionally require observed zero
    remuneration and identical Summary/DRE profit in every consumed profit input.
    """
    copied=deepcopy(observations)
    proof=dict(rule=PROFIT_BRIDGE_ID,released=False,basis=None,reason='unreviewed_context',inputs=[])
    periods=PROFIT_BRIDGE_WINDOWS.get(period)
    if not periods or len(copied)!=5 or [r.get('period') for r in copied]!=list(periods):return copied,proof
    # June opening LL is unused: Q3 and Q1 are native quarterly flows.
    used=copied[1:] if period=='201906' else copied
    proof.update(analysis_period=period,profit_dependency_periods=[r['period'] for r in used])
    unit=copied[0].get('unit_key')
    if not isinstance(unit,(list,tuple)) or len(unit)!=3 or tuple(unit[:2]) not in (('financial','2'),('individual','3')):return copied,proof
    dataset,dtype=unit[:2];prefix='individual:' if dataset=='individual' else ''
    if prefix:proof['rule']=prefix+PROFIT_BRIDGE_ID
    for r in used:
        before=r['period']<'201903';definition=prefix+('LL-pre201903' if before else 'LL-from201903')
        formula='[70000009]+[80000006]-'+('[81955002]' if before else '[81956001]')
        literal=r.get('binding',{}).get('literal_context',{})
        if (r.get('definition_id')!=definition or tuple(r.get('unit_key',()))!=tuple(unit)
            or r.get('scale')!='BRL' or r.get('window_rule')!='native-semester-analysis-v2'
            or any(literal.get(k)!=v for k,v in dict(dataset=dataset,TipoInstituicao=dtype,NumeroRelatorio='1',Conta='78187',DescricaoColuna=formula).items())):
            return copied,proof
    cadre=cadastro or {};segment=cadre.get('SegmentoTb') or ''
    exceptional=cadre.get('Tcb')=='N4' or segment=='Instituição de Pagamento' or 'consórcio' in segment.lower()
    if not exceptional and cadre.get('Tcb') not in ('B1','B2','B3S','B3C','B4','N1','N2'):
        proof['reason']='missing_or_unreviewed_classification';return copied,proof
    if exceptional:
        proof.update(basis='observed_zero_remuneration',reason='zero_effect_not_proven')
        for r in used:
            p=r['period'];expected='[81956001]' if p>='201903' else '[81955002]'
            def matches(account):
                return [n for n in native_rows if n.get('CodInst')==unit[2] and n.get('AnoMes')==p
                        and n.get('TipoInstituicao')==dtype and n.get('NumeroRelatorio')=='4' and n.get('Conta')==account]
            jcp,ll=matches('78230'),matches('78187')
            if len(jcp)!=1 or len(ll)!=1:return copied,proof
            j,s=math._native_value({'token':jcp[0].get('Saldo')});d,ds=math._native_value({'token':ll[0].get('Saldo')});v,vs=math._native_value(r)
            proof['inputs'].append(dict(period=p,remuneration=deepcopy(jcp[0]),dre_profit=deepcopy(ll[0])))
            if (s or ds or vs or j!=0 or d!=v or jcp[0].get('DescricaoColuna')!=expected
                or ll[0].get('DescricaoColuna')!=r['binding']['literal_context']['DescricaoColuna']):
                return copied,proof
    else:proof['basis']='native_published_profit'
    proof.update(released=True,reason='reviewed_semantic_compatibility',original_definitions=[r['definition_id'] for r in copied])
    for r in used:r['definition_id']=prefix+PROFIT_BRIDGE_ID
    return copied,proof


def recalculate_caixa_transition(baseline,expected_baseline_manifest_sha256,output):
    """Produce the eight reviewed Caixa patches in one finite source query.

    This is a patch package, never an aggregate of the entire financial system.
    Every native/analytical component and unavailable baseline result is retained.
    """
    from time import perf_counter
    import duckdb
    from .ifdata_odata import CONTRACT as NATIVE_CONTRACT
    from .ifdata_cadastro import CONTRACT as CADASTRO_CONTRACT
    started=perf_counter();root=Path(baseline).resolve();output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if not isinstance(expected_baseline_manifest_sha256,str) or not re.fullmatch('[0-9a-f]{64}',expected_baseline_manifest_sha256):
        raise ValueError('External baseline manifest pin required')
    if math._digest_file(root/'manifest.json')!=expected_baseline_manifest_sha256:raise ValueError('Baseline manifest hash mismatch')
    main=math._json_unique((root/'manifest.json').read_bytes())
    if main.get('contract')!=CONTRACT or main.get('stage')!='coverage-and-aggregation':raise ValueError('Accepted universe baseline required')
    profile=load_profile(expected_sha256=main['profile_sha256'])
    periods=sorted({p for target in CAIXA_TRANSITION_PERIODS for p in math.dependency_periods([target])})
    guards={};sources={};inventories={}
    def identity(path):
        s=_ordinary(path).stat();return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    for path in (root/'manifest.json',PROFILE_PATH):guards[path]=identity(path)
    for name,contract in (('financial',NATIVE_CONTRACT),('cadastro',CADASTRO_CONTRACT)):
        spec=main['inputs'][name];source=Path(spec['root']).resolve()
        if output==source or source in output.parents or output in source.parents:raise ValueError('Output overlaps native source')
        manifest_path=source/'manifest.json'
        if math._digest_file(manifest_path)!=spec['expected_manifest_sha256']:raise ValueError('Native manifest hash mismatch')
        m=math._json_unique(manifest_path.read_bytes())
        if m.get('contract')!=contract:raise ValueError('Native contract mismatch')
        entries=[e for e in m['files'] if str(e['period']) in periods]
        if len(entries)!=len(periods) or {str(e['period']) for e in entries}!=set(periods):raise ValueError('Missing or ambiguous native parts')
        guards[manifest_path]=identity(manifest_path)
        for e in entries:
            _capture_payload(source,e);guards[source/e['file']]=identity(source/e['file'])
        sources[name]=(source,m);inventories[name]=entries
    if output==root or root in output.parents or output in root.parents:raise ValueError('Output overlaps baseline')
    entries=[e for e in main['files'] if e['file']=='unit_periods.csv']
    if len(entries)!=1:raise ValueError('Missing baseline unit inventory')
    entry=entries[0];_capture_payload(root,entry);path=root/entry['file'];guards[path]=identity(path)
    units={};count=0;csv.field_size_limit(10000000)
    with path.open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            count+=1
            if row['dataset']!='financial' or row['period'] not in CAIXA_TRANSITION_PERIODS:continue
            u=math._json_unique(row['payload'].encode('utf-8'))
            if u.get('code')!='C0051626':continue
            p=row['period'];uid='financial|2|C0051626|'+p
            if p in units or u.get('dataset')!='financial' or u.get('period')!=p or u.get('unit_id')!=uid:raise ValueError('Ambiguous target unit')
            units[p]=u
    if count!=entry['rows'] or count!=main['tables']['unit_periods'] or set(units)!=set(CAIXA_TRANSITION_PERIODS):raise ValueError('Target population mismatch')
    with duckdb.connect(config={'threads':1,'memory_limit':'256MiB'}) as conn:
        _window(conn,sources['financial'],periods,dataset='financial')
        native=math._records(conn.execute("select * from native where CodInst in ('00360305','C0051626') and NumeroRelatorio='1' and Conta in ('78182','78186','78187')"))
        source,_=sources['cadastro'];parts=[str(source/e['file']) for e in inventories['cadastro']]
        cad=math._records(conn.execute("select * from read_parquet(?) where CodInst in ('00360305','C0051626','42040639','C0080738') or CodConglomeradoFinanceiro='C0051626'",[parts]))
    indexed={}
    for row in native:indexed.setdefault((row['CodInst'],row['AnoMes']),[]).append(row)
    components={};results=[];coverage=[]
    def remember(observation):
        key=observation['id']
        if key in components and canonical(components[key])!=canonical(observation):raise ValueError('Conflicting patch component identity')
        components[key]=observation
    for period in CAIXA_TRANSITION_PERIODS:
        unit=units[period];uid=unit['unit_id'];dates=math.dependency_periods([period])
        for metric in ('R1','R2'):
            original={};predecessor={}
            for name in math.METRICS[metric]:
                original[name]=[];predecessor[name]=[]
                for p in dates:
                    for code,target in (('C0051626',original),('00360305',predecessor)):
                        o=math.resolve_component(profile,name,'financial',code,p,indexed.get((code,p),[]))
                        o.update(id=hashlib.sha256((uid+'|'+code+'|'+name+'|'+p).encode()).hexdigest()[:32],
                                 component=name,dataset='financial',code=code,analysis_period=period,status=o.get('status','ok'))
                        target[name].append(o);remember(o)
            before=math.evaluate_metric(metric,dict(period=period,components=original,financial_statement=True),'ttm')
            bridged,proof=bridge_caixa_transition(original,predecessor,cad,period=period,metric=metric)
            if not proof['released']:raise ValueError('Caixa bridge not released: '+period+' '+metric+' '+proof['reason'])
            for observations in bridged.values():
                for o in observations:remember(o)
            result=math.evaluate_metric(metric,dict(period=period,components={k:[_thin(o) for o in rows] for k,rows in bridged.items()},financial_statement=True),'ttm')
            result.update(id=uid+'|'+metric+'|ttm',unit_id=uid,unit_key=['financial','2','C0051626'],dataset='financial',code='C0051626',
                          membership=unit['membership'],baseline_status=before['status'],baseline_result=_normalize_temporal(before),reporting_transition=proof)
            result['flags']=sorted(set(result['flags']+['caixa_observed_perimeter_transition']))
            results.append(_normalize_temporal(result))
            asset=math.resolve_component(profile,'AT','financial','C0051626',period,indexed.get(('C0051626',period),[]))
            av,ast=math._native_value(asset)
            if not unit.get('own_cadastro'):av,ast=None,'missing_dated_cadastro'
            covered={k:deepcopy(result.get(k)) for k in ('period','dataset','code','metric','horizon','status','applicability','applicability_evidence','value_fraction','numerator_fraction','denominator_fraction','flags','limits','annual_summary')}
            covered.update(id=result['id']+'|coverage',result_id=result['id'],row_kind='native_unit',unit_id=uid,unit_key=result['unit_key'],
                membership=unit['membership'],companies=deepcopy(unit['companies']),asset_fraction=math._fraction_field(av) if av is not None else None,
                asset_status=ast or 'ok',target_cadastro=dict(Data=period,**unit['classifications']) if unit.get('classifications') is not None else None,
                reporting_transition=proof)
            coverage.append(covered)
    for path,before in guards.items():
        if identity(path)!=before:raise ValueError('Input changed during selective calculation')
    output.mkdir(parents=True);files=[];tables=dict(components=list(components.values()),results=results,unit_coverage=coverage)
    with ExitStack() as stack,duckdb.connect(config={'threads':1,'memory_limit':'256MiB'}) as conn:
        for table,rows in tables.items():
            writer=Writer(output,table,stack)
            for row in rows:writer.append(row)
            files.extend(writer.finish(conn))
    for path,before in guards.items():
        if identity(path)!=before:raise ValueError('Input changed during selective output')
    manifest=dict(contract='ifdata-caixa-transition-analysis-v1',scope=dict(dataset='financial',code='C0051626',metrics=['R1','R2'],horizon='ttm',periods=list(CAIXA_TRANSITION_PERIODS)),
        baseline=dict(root=str(root),expected_manifest_sha256=expected_baseline_manifest_sha256),inputs={k:main['inputs'][k] for k in sources},
        native_partitions=inventories,unit_periods=entry,profile_sha256=main['profile_sha256'],bridge_rule=CAIXA_TRANSITION_ID,
        tables={k:len(v) for k,v in tables.items()},files=files,producer_sha256=math._digest_file(Path(__file__)),elapsed_seconds=perf_counter()-started,
        limits=['Patch only: merge with unchanged contributions before aggregating',
                'Observed historical perimeter, not a constant-perimeter consolidation; June2021 discrepancies retained'])
    (output/'manifest.json').write_text(canonical(manifest)+'\n',encoding='utf-8')
    return manifest


def recalculate_slice(baseline,expected_baseline_manifest_sha256,output,*,metric='R1',horizon='ttm',dataset='financial',period='201903'):
    """Recalculate one reviewed ROA/ROE slice; never rebuild or edit the baseline.

    Source partitions are queried together in DuckDB. Native math, typed
    bindings, precision and reductions are shared with the full-universe path.
    The independently declared output is directly queryable as Parquet.
    """
    from collections import Counter
    from time import perf_counter
    import duckdb
    from .ifdata_odata import CONTRACT as NATIVE_CONTRACT
    if metric not in ('R1','R2') or horizon!='ttm' or dataset not in ('financial','individual') or period not in PROFIT_BRIDGE_WINDOWS:
        raise ValueError('Not a reviewed selective target')
    periods=PROFIT_BRIDGE_WINDOWS[period]
    started=perf_counter();root=Path(baseline).resolve();output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if not isinstance(expected_baseline_manifest_sha256,str) or not re.fullmatch('[0-9a-f]{64}',expected_baseline_manifest_sha256):
        raise ValueError('External baseline manifest pin required')
    if math._digest_file(root/'manifest.json')!=expected_baseline_manifest_sha256:raise ValueError('Baseline manifest hash mismatch')
    main=math._json_unique((root/'manifest.json').read_bytes())
    if main.get('contract')!=CONTRACT or main.get('stage')!='coverage-and-aggregation':raise ValueError('Accepted universe baseline required')
    profile=load_profile(expected_sha256=main['profile_sha256'])
    native_input=main['inputs'][dataset];source=Path(native_input['root']).resolve();dtype=TYPES[dataset]
    for protected in (root,source):
        if protected in output.parents or output in protected.parents:raise ValueError('Selective output overlaps a source')
    if math._digest_file(source/'manifest.json')!=native_input['expected_manifest_sha256']:raise ValueError('Financial manifest hash mismatch')
    sm=math._json_unique((source/'manifest.json').read_bytes())
    if sm.get('contract')!=NATIVE_CONTRACT:raise ValueError('Native financial contract mismatch')
    entries=[e for e in sm['files'] if str(e['period']) in periods]
    if len(entries)!=5 or {str(e['period']) for e in entries}!=set(periods):raise ValueError('Missing or ambiguous native periods')
    guards={}
    def identity(path):
        s=_ordinary(path).stat();return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    for p in (root/'manifest.json',source/'manifest.json',PROFILE_PATH):guards[p]=identity(p)
    for e in entries:
        p=math._contained(source,e['file']);_capture_payload(source,e);guards[p]=identity(p)
    unit_entries=[e for e in main['files'] if e['file']=='unit_periods.csv']
    if len(unit_entries)!=1:raise ValueError('Missing baseline native units')
    ue=unit_entries[0];_capture_payload(root,ue);up=root/'unit_periods.csv';guards[up]=identity(up)
    units=[];seen=set();count=0;csv.field_size_limit(10000000)
    with up.open(encoding='utf-8',newline='') as f:
        for raw in csv.DictReader(f):
            count+=1
            if raw['period']!=period or raw['dataset']!=dataset:continue
            unit=math._json_unique(raw['payload'].encode('utf-8'))
            if unit['period']!=period or unit['dataset']!=dataset or unit['code'] in seen:raise ValueError('Ambiguous selective native unit')
            if unit['unit_id']!='|'.join((dataset,dtype,unit['code'],period)):raise ValueError('Native unit identity mismatch')
            seen.add(unit['code']);units.append(unit)
    if count!=ue['rows'] or count!=main['tables']['unit_periods'] or not units:raise ValueError('Native population count mismatch')
    with duckdb.connect(config={'threads':1,'memory_limit':'256MiB'}) as conn:
        _window(conn,(source,sm),list(periods),dataset=dataset)
        accounts="'78182','78187'" if metric=='R1' else "'78182','78187','78186'"
        rows=math._records(conn.execute("select * from native where (NumeroRelatorio='1' and Conta in ("+accounts+")) or (NumeroRelatorio='4' and Conta in ('78187','78230'))"))
    indexed={}
    for row in rows:indexed.setdefault((row['CodInst'],row['AnoMes']),[]).append(row)
    components=[];results=[];coverage=[];before=Counter();after=Counter()
    for unit in sorted(units,key=lambda u:u['code']):
        code=unit['code'];uid=unit['unit_id'];original={}
        for name in (('LL','AT') if metric=='R1' else ('LL','PL','AT')):
            original[name]=[]
            for p in periods:
                ob=math.resolve_component(profile,name,dataset,code,p,indexed.get((code,p),[]))
                ob.update(id=hashlib.sha256((uid+'|'+name+'|'+p).encode()).hexdigest()[:32],component=name,dataset=dataset,code=code,status=ob.get('status','ok'),analysis_period=period)
                original[name].append(ob);components.append(_compact_component(ob))
        def calculate(data):
            return math.evaluate_metric(metric,dict(period=period,components={k:[_thin(o) for o in v] for k,v in data.items()},financial_statement=True),horizon)
        baseline_result=calculate(original);before[baseline_result['status']]+=1
        native=[n for p in periods for n in indexed.get((code,p),[])]
        ll,proof=bridge_profit_201903(original['LL'],native,unit.get('classifications'),period=period)
        result=calculate(dict(original,LL=ll));after[result['status']]+=1
        result.update(id=uid+'|'+metric+'|'+horizon,unit_id=uid,unit_key=[dataset,dtype,code],dataset=dataset,code=code,
                      membership=unit['membership'],baseline_status=baseline_result['status'],profit_bridge=proof)
        if proof['released']:result['flags']=sorted(set(result['flags']+['ll_native_definition_bridge_201903']))
        results.append(_normalize_temporal(result))
        av,ast=math._native_value(original['AT'][-1])
        if not unit.get('own_cadastro'):av,ast=None,'missing_dated_cadastro'
        covered={k:deepcopy(result.get(k)) for k in ('id','period','dataset','code','metric','horizon','status','applicability','value_fraction','numerator_fraction','denominator_fraction','flags','limits','annual_summary')}
        covered.update(unit_id=uid,unit_key=[dataset,dtype,code],membership=unit['membership'],companies=unit['companies'],
                       asset_fraction=math._fraction_field(av) if av is not None else None,asset_status=ast or 'ok',
                       target_cadastro=dict(Data=period,**unit['classifications']) if unit.get('classifications') is not None else None,
                       baseline_status=baseline_result['status'],profit_bridge=proof)
        coverage.append(covered)
    derived=aggregate_unit_results(coverage,fields=SELECTIVE_AXES)
    tables=dict(components=components,results=results,unit_coverage=coverage,**derived)
    for p,guard in guards.items():
        if identity(p)!=guard:raise ValueError('Selective source changed during calculation')
    output.mkdir(parents=True)
    files=[]
    with ExitStack() as stack,duckdb.connect(config={'threads':1,'memory_limit':'256MiB'}) as conn:
        for table,values in tables.items():
            writer=Writer(output,table,stack)
            for row in values:writer.append(row)
            files.extend(writer.finish(conn))
    for p,guard in guards.items():
        if identity(p)!=guard:raise ValueError('Selective source changed during output')
    manifest=dict(contract='ifdata-selective-analysis-v1',scope=dict(metric=metric,horizon=horizon,dataset=dataset,period=period),
                  baseline=dict(root=str(root),expected_manifest_sha256=expected_baseline_manifest_sha256),
                  inputs={dataset:native_input,'native_partitions':entries,'unit_periods':ue},profile_sha256=main['profile_sha256'],
                  bridge_rule=('individual:' if dataset=='individual' else '')+PROFIT_BRIDGE_ID,segmentation_fields=list(SELECTIVE_AXES),dependency_periods=list(periods),
                  baseline_statuses=dict(before),result_statuses=dict(after),tables={t:len(v) for t,v in tables.items()},files=files,
                  elapsed_seconds=perf_counter()-started,producer_sha256=math._digest_file(Path(__file__)),
                  limits=['Native published profit; taxes retained as reported, no uniform fiscal counterfactual',
                          'No change to baseline; only the declared slice replaces its corresponding analytical projection',
                          'IPs/consortia require observed zero remuneration and equal Summary/DRE profit in all consumed profit inputs'])
    (output/'manifest.json').write_text(canonical(manifest)+'\n',encoding='utf-8')
    return manifest


def _category(row,field):
    state=row.get('classification_states',{}).get(field)
    if state in ('conflict','before_regime','unknown','missing_dated_cadastro','missing_field'):return (state,None)
    cadre=row.get('target_cadastro')
    if not cadre or cadre.get('Data')!=row['period']:return ('missing_dated_cadastro',None)
    if field not in cadre:return ('missing_field',None)
    value=cadre[field]
    return ('null' if value is None else 'empty' if value=='' else 'value',value)


def _eligible(row):
    return bool(row.get('unit_id') and row['status']=='ok' and row['applicability']=='applicable'
                and row.get('numerator_fraction') is not None and row.get('denominator_fraction') is not None
                and math._rational(row['denominator_fraction'])!=0)


def _summary_values(row):
    """Caller-local exact values; retain validation before any reduction."""
    n=d=v=None
    if row.get('unit_id') and row['status']=='ok':
        n,d,v=(math._rational(row[k]) for k in ('numerator_fraction','denominator_fraction','value_fraction'))
        if not d or n/d!=v:raise ValueError('Inconsistent native result fraction')
    return dict(numerator=n,denominator=d,value=v,
        asset=math._rational(row['asset_fraction']) if row.get('asset_fraction') is not None else None,
        eligible=bool(row.get('unit_id') and row['status']=='ok' and row['applicability']=='applicable' and n is not None and d),
        calculable=row['status']=='ok' and row.get('value_fraction') is not None)




def _unit_summary(rows,context,parsed):
    """Reduce native contributions, keeping company relations nominal only."""
    units=sorted((r for r in rows if r.get('unit_id')),key=lambda r:r['unit_id'])
    eligible_check=lambda r:parsed[id(r)]['eligible']
    eligible=[r for r in units if eligible_check(r)]
    calculable=lambda r:parsed[id(r)]['calculable']
    predicates=dict(expected=lambda r:True,eligible=eligible_check,calculable=calculable,
        missing=lambda r:not calculable(r),not_applicable=lambda r:r['applicability']=='not_applicable' and bool(r.get('applicability_evidence')),
        unknown=lambda r:r['applicability']=='unknown' or (r['applicability']=='not_applicable' and not r.get('applicability_evidence')),
        diagnostic=lambda r:calculable(r) and r['applicability']!='applicable')
    lists={name+'_units':[r['unit_id'] for r in units if predicate(r)] for name,predicate in predicates.items()}
    companies=sorted({c for r in rows for c in r.get('companies',[])})
    for name,predicate in predicates.items():
        # A company with multiple native links is missing only when none is
        # calculable; it is never an additional economic contributor.
        lists[name+'_companies']=[c for c in companies if
            (not any(calculable(r) for r in rows if c in r.get('companies',[])) if name=='missing' else
             any(predicate(r) for r in rows if c in r.get('companies',[])))]
    known=[r for r in units if r.get('asset_fraction') is not None]
    unknown=[r['unit_id'] for r in units if r.get('asset_fraction') is None]
    unknown_companies=sorted({c for r in rows if r.get('asset_fraction') is None for c in r.get('companies',[])})
    total=sum((parsed[id(r)]['asset'] for r in known),Fraction())
    covered=sum((parsed[id(r)]['asset'] for r in known if eligible_check(r)),Fraction())
    share=covered/total if total else None
    f=math._fraction_field
    assets=dict(reference='contemporaneous_own_'+context['dataset']+'_AT',
        status='own_assets_unavailable' if context['dataset']=='capital' else 'partial_known_assets' if unknown or unknown_companies else 'known_assets',
        known_units=[r['unit_id'] for r in known],unknown_units=unknown,unknown_companies=unknown_companies,
        known_asset_fraction=f(total),eligible_known_asset_fraction=f(covered),
        share_of_known_fraction=f(share) if share is not None else None,
        share_of_total_fraction=f(share) if share is not None and not unknown and not unknown_companies else None,
        flags=['negative_asset_weights'] if any(parsed[id(r)]['asset']<0 for r in known) else [])
    numerator=sum((parsed[id(r)]['numerator'] for r in eligible),Fraction())
    denominator=sum((parsed[id(r)]['denominator'] for r in eligible),Fraction())
    flags={flag for r in eligible for flag in r.get('flags',[])}
    if any(parsed[id(r)]['denominator']<0 for r in eligible):flags.add('non_convex_denominator_weights')
    status='no_eligible_units' if not eligible else 'zero_denominator' if not denominator else 'ok'
    overlap=dict(status='prudential_overlap_unproven' if context['dataset']=='capital' else 'financial_intergroup_exposures_retained' if context['dataset']=='financial' else 'individual_unconsolidated',
        certified_system_total=False,copresence=sorted({canonical(p) for r in units for p in r.get('parent_copresence',[])}))
    overlap['copresence']=[json.loads(p) for p in overlap['copresence']]
    a=dict(context,status=status,method='ratio_of_sums_same_eligible_native_unit_intersection',
        numerator_fraction=f(numerator) if eligible else None,denominator_fraction=f(denominator) if eligible else None,
        value_fraction=None,value=None,lists=lists,counts={k:len(v) for k,v in lists.items()},asset_coverage=assets,
        flags=sorted(flags),overlap=overlap,limits=sorted({limit for r in rows for limit in (r.get('limits') or [])}),
        population_states=sorted({r['population_state'] for r in rows if r.get('population_state')}),
        missing_reasons={state:sorted(r['unit_id'] for r in units if r['status']==state) for state in sorted({r['status'] for r in units if r['status']!='ok'})},
        annual_summary=context['period'].endswith('12') and context['horizon'] in ('point','ttm'))
    if status=='ok':a=math._valued(a,numerator/denominator)
    values=sorted(parsed[id(r)]['value'] for r in eligible)
    d=dict(context,status='ok' if values else 'no_eligible_units',n=len(values),method='empirical_quantile_type2',eligible_units=lists['eligible_units'],flags=a['flags'])
    quantiles={name:math._quantile2(values,p) if values else None for name,p in [('q1',Fraction(1,4)),('median',Fraction(1,2)),('q3',Fraction(3,4))]}
    quantiles['iqr']=quantiles['q3']-quantiles['q1'] if values else None
    for name,value in quantiles.items():
        d[name+'_fraction']=f(value) if value is not None else None
        d[name]=math._valued({},value)['value'] if value is not None else None
    return a,d


def _comparisons(aggregates,context):
    total=aggregates['total'];parts=[aggregates[c] for c in COHORTS[1:]]
    def fraction(row,key):return math._rational(row[key]) if row[key] is not None else Fraction()
    checks={key:total['counts'][key]==sum(a['counts'][key] for a in parts) for key in total['counts'] if key.endswith('_units')}
    checks.update({key:fraction(total,key)==sum((fraction(a,key) for a in parts),Fraction()) for key in ('numerator_fraction','denominator_fraction')})
    for key in ('known_asset_fraction','eligible_known_asset_fraction'):
        checks[key]=fraction(total['asset_coverage'],key)==sum((fraction(a['asset_coverage'],key) for a in parts),Fraction())
    if not all(checks.values()):raise ValueError('Native cohort reconciliation failed')
    output=[]
    for left,right in [('sample','total'),('sample','remaining'),('unknown','total')]:
        a,b=aggregates[left],aggregates[right]
        valid=a['status']==b['status']=='ok'
        denominator=math._rational(b['asset_coverage']['known_asset_fraction'])
        output.append(dict(context,id=context['id']+'|'+left+'-vs-'+right,left=left,right=right,
            left_aggregate_id=a['id'],right_aggregate_id=b['id'],status='descriptive' if valid else 'unavailable',
            difference_fraction=math._fraction_field(math._rational(a['value_fraction'])-math._rational(b['value_fraction'])) if valid else None,
            eligible_intersection=sorted(set(a['lists']['eligible_units'])&set(b['lists']['eligible_units'])),
            left_eligible_count=a['counts']['eligible_units'],right_eligible_count=b['counts']['eligible_units'],
            known_asset_share_fraction=math._fraction_field(math._rational(a['asset_coverage']['known_asset_fraction'])/denominator) if denominator else None,
            asset_share_scope='known_own_assets_only_not_certified_population_share',
            reconciliation=dict(status='exact',checks=checks,identity='total=sample+remaining+unknown',ratios_and_quantiles_additive=False),
            interpretation='descriptive_only_total_includes_sample_no_causal_or_statistical_inference'))
    return output


def aggregate_unit_results(rows,*,fields=None):
    """Exact pure reduction of native metric coverage, independently per axis.

    Native rows have unit_id/unit_key, membership, companies, own dated cadastro
    and AT, and result fractions/status/applicability. A missing company may have
    a nominal row with unit_id/unit_key=None; it never contributes a unit/value.
    Duplicate native contributors are rejected, including equal duplicates.
    """
    groups={};seen=set();seen_ids=set();parsed={}
    for row in rows:
        key=tuple(row[k] for k in ('period','dataset','metric','horizon'))
        if row['membership'] not in COHORTS[1:]:raise ValueError('Invalid native membership')
        if row.get('unit_id'):
            identity=(key,canonical(row['unit_key']))
            if identity in seen or (key,row['unit_id']) in seen_ids:raise ValueError('Duplicate native contributor')
            seen.add(identity)
            seen_ids.add((key,row['unit_id']))
            if row['unit_key']!=[row['dataset'],TYPES[row['dataset']],row['code']]:raise ValueError('Native coverage identity mismatch')
            if row['dataset']=='capital' and row.get('asset_fraction') is not None:raise ValueError('Capital own assets unavailable')
        elif row.get('unit_key') is not None or row.get('value_fraction') is not None or row.get('asset_fraction') is not None:
            raise ValueError('Nominal company cannot contribute native value')
        parsed[id(row)]=_summary_values(row)
        groups.setdefault(key,[]).append(row)
    output={table:[] for table in DERIVED_TABLES[1:]}
    for key,group in sorted(groups.items()):
        base=dict(zip(('period','dataset','metric','horizon'),key));base['id']='|'.join(key)
        categories=[({},group)]
        for field in (AXES if fields is None else fields):
            segments={}
            for row in group:
                # JSON typed keys keep numeric and textual native categories distinct.
                category=_category(row,field);segments.setdefault(canonical(category),(category,[]))[1].append(row)
            categories.extend((dict(field=field,category_state=category[0],category=category[1]),subset)
                              for _,(category,subset) in sorted(segments.items()))
        for category,subset in categories:
            context=dict(base,**category)
            if category:context['id']+='|'+category['field']+'|'+canonical([category['category_state'],category['category']])
            aggregates={}
            for cohort in COHORTS:
                selected=subset if cohort=='total' else [r for r in subset if r['membership']==cohort]
                a,d=_unit_summary(selected,dict(context,id=context['id']+'|'+cohort,cohort=cohort),parsed);aggregates[cohort]=a
                if category:output['segment_coverage'].append(dict(a,distribution=d))
                else:output['aggregates'].append(a);output['distributions'].append(d)
            output['cohort_comparisons'].extend(_comparisons(aggregates,context))
    return output


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


COMPLEMENT_BINDINGS={
    'funding':('3','78185','[41000007] + [42000006] + [43000005] + [46000002]'),
    'repos':('3','78288','[42000006]'),
    'issuances':('3','78294','[43000005]'),
    'loans_transfers':('3','78295','[46000002]'),
    'credit_income':('4','78203','[71100001]+[71910002]+[71915007]+[71920009]+[71925004]+[71950000]+[71980001]+[81945005]+[81950007]+[81915004]'),
}


def compile_complement_profile(profile,catalogue,datasets):
    """Append five finite own-perspective literal bindings; never edit v1.

    One unchanged eight-dimensional catalogue context must cover all sixty
    core references. A different description, missing quarter or ambiguity is
    a hard failure, with no name matching or cross-perspective transplantation.
    """
    from .ifdata_variable_catalog import DIMENSIONS
    result=deepcopy(profile)
    periods=[f'{year}{quarter}' for year in range(2010,2025) for quarter in ('03','06','09','12')]
    for dataset in datasets:
        if dataset not in ('financial','individual'):raise ValueError('Complement perspective not approved')
        for role,(report,account,description) in COMPLEMENT_BINDINGS.items():
            candidates=[r for r in catalogue if r.get('dataset')==dataset and r.get('NumeroRelatorio')==report
                        and r.get('Conta')==account and any(str(p) in periods for p in r.get('periodos',[]))]
            if len(candidates)!=1:raise ValueError('Missing or ambiguous complement catalogue context: '+dataset+'/'+role)
            row=candidates[0]
            if row.get('TipoInstituicao')!=TYPES[dataset] or row.get('DescricaoColuna')!=description:
                raise ValueError('Unreviewed complement literal context: '+dataset+'/'+role)
            observed=[str(p) for p in row['periodos'] if '201003'<=str(p)<='202412']
            if sorted(observed)!=periods or any(k not in row for k in DIMENSIONS):
                raise ValueError('Incomplete complement catalogue periods or dimensions: '+dataset+'/'+role)
            literal={k:row[k] for k in DIMENSIONS}
            digest=hashlib.sha256(json.dumps(literal,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
            result['contexts'].append(dict(component=math.COMPONENT_NAMES[role],literal_context=literal,context_sha256=digest,
                compatibility=digest,periods=periods,window_rule='native-semester-analysis-v2' if role=='credit_income' else 'stock',
                sign_rule='native_signed_no_abs',proof_rule='literal_catalogue_60_core_references',
                proof='Issue152 / research143; own dataset and TipoInstituicao, unchanged literal accounts; no cross-perimeter equivalence'))
    return result


def calculate_complements(baseline,expected_baseline_manifest_sha256,output,*,periods,datasets=None,metrics=None,formats=('json','csv','parquet')):
    """Calculate approved additions from authenticated native components only.

    Select output references explicitly (e.g. periods=['202412'], metrics=
    ['LA','LC','LF-DEP','LF-OC','LF-EM','LF-REP']). Financial is the default;
    Individual is its own optional perspective. Flows emit quarter and TTM.
    Results, unit coverage and deduplicated components use the existing Writer
    in JSON/CSV/Parquet. The additive contexts file resolves binding_ref.
    This package contains unit contributions, never a system aggregate.
    """
    from time import perf_counter
    import duckdb
    from .ifdata_odata import CONTRACT as NATIVE_CONTRACT,COLUMNS
    from .ifdata_variable_catalog import CONTRACT as CAT_CONTRACT,query_catalog
    from .ifdata_cadastro import CONTRACT as CAD_CONTRACT
    datasets=['financial'] if datasets is None else datasets
    metrics=list(math.COMPLEMENT_METRICS) if metrics is None else metrics
    if (not isinstance(periods,list) or not periods or len(set(periods))!=len(periods)
        or any(not isinstance(p,str) or math._period_date(p) is None or not '201003'<=p<='202412' for p in periods)):
        raise ValueError('Invalid complement periods')
    if (not isinstance(datasets,list) or not datasets or len(set(datasets))!=len(datasets)
        or any(d not in ('financial','individual') for d in datasets)):
        raise ValueError('Invalid complement perspectives')
    if (not isinstance(metrics,list) or not metrics or len(set(metrics))!=len(metrics)
        or any(m not in math.COMPLEMENT_METRICS for m in metrics)):
        raise ValueError('Invalid complement metrics')
    if tuple(formats) not in (('json','csv','parquet'),('parquet',)):raise ValueError('Invalid complement output formats')
    started=perf_counter();root=Path(baseline).resolve();output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if not isinstance(expected_baseline_manifest_sha256,str) or not re.fullmatch('[0-9a-f]{64}',expected_baseline_manifest_sha256):
        raise ValueError('External baseline manifest pin required')
    if math._digest_file(root/'manifest.json')!=expected_baseline_manifest_sha256:raise ValueError('Baseline manifest hash mismatch')
    main=math._json_unique((root/'manifest.json').read_bytes())
    if main.get('contract')!=CONTRACT or main.get('stage')!='coverage-and-aggregation':raise ValueError('Accepted universe baseline required')
    profile=load_profile(expected_sha256=main['profile_sha256'])
    guards={}
    def identity(path):
        s=_ordinary(path).stat();return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    def protect(path):guards[path]=identity(path)
    def no_overlap(source):
        if output==source or source in output.parents or output in source.parents:raise ValueError('Complement output overlaps source')
    def authenticate(spec,contract,selected=None):
        source=Path(spec['root']).resolve();no_overlap(source);path=source/'manifest.json'
        if math._digest_file(path)!=spec['expected_manifest_sha256']:raise ValueError('Source manifest hash mismatch')
        manifest=math._json_unique(path.read_bytes())
        if manifest.get('contract')!=contract:raise ValueError('Source contract mismatch')
        protect(path)
        if selected is not None:
            entries=[e for e in manifest['files'] if str(e.get('period')) in selected]
            if len(entries)!=len(selected) or {str(e.get('period')) for e in entries}!=set(selected):raise ValueError('Missing or ambiguous native parts')
            for entry in entries:_capture_payload(source,entry);protect(math._contained(source,entry['file']))
        return source,manifest
    no_overlap(root);protect(root/'manifest.json');protect(PROFILE_PATH)
    catroot,catmanifest=authenticate(main['inputs']['catalogue'],CAT_CONTRACT)
    catalogue=query_catalog(catroot,'select * from catalogo_variaveis')
    for e in catmanifest['files']:protect(math._contained(catroot,e['file']))
    profile=compile_complement_profile(profile,catalogue,datasets)
    catalogue_keys={(canonical({k:r[k] for k in c['literal_context']}),str(p)) for c in profile['contexts'] for r in catalogue
                    if all(type(r.get(k)) is type(v) and r.get(k)==v for k,v in c['literal_context'].items()) for p in r['periodos']}
    horizons={m:('quarter','ttm') if m in math.COMPLEMENT_FLOW_METRICS else ('point',) for m in metrics}
    required=sorted({n for m in metrics for n in math.COMPLEMENT_METRICS[m]}|{'AT'})
    dependencies=sorted({p for target in periods for m in metrics for h in horizons[m] for n in math.COMPLEMENT_METRICS[m] for p in component_periods(n,target,h)}|set(periods))
    native_periods=[p for p in dependencies if p!='200912'];sources={};inventories={}
    for ds in datasets:
        spec=main['inputs'][ds]
        if catmanifest.get('inputs',{}).get(ds,{}).get('manifest_sha256')!=spec['expected_manifest_sha256']:
            raise ValueError('Catalogue source lineage mismatch')
        sources[ds]=authenticate(spec,NATIVE_CONTRACT,native_periods)
        inventories[ds]=[e for e in sources[ds][1]['files'] if str(e.get('period')) in native_periods]
    openings=None;cadres={}
    if '200912' in dependencies:
        spec=main.get('config',{}).get('opening')
        if not spec:raise ValueError('Authenticated admitted opening input required')
        # One opening package contains both perspectives, so its finite inventory
        # is authenticated as a whole before the typed window selects each one.
        op_root,op_manifest=math._authenticate(spec,NATIVE_CONTRACT);no_overlap(op_root)
        policy=profile['opening_policy']
        if (op_manifest.get('source_manifest_sha256')!=policy['raw_manifest_sha256']
            or op_manifest.get('selection')!={'periods':['200912'],'types':['2','3'],'reports':['1','2']}
            or main['inputs']['cadastro']['expected_manifest_sha256']!=policy['cadastro_manifest_sha256']
            or any(e.get('source_sha256') not in {p['sha256'] for p in policy['pages']} for e in op_manifest['files'])):
            raise ValueError('Unreviewed opening source/cadastro')
        protect(op_root/'manifest.json')
        for e in op_manifest['files']:protect(math._contained(op_root,e['file']))
        openings=(op_root,op_manifest)
        cadsource=authenticate(main['inputs']['cadastro'],CAD_CONTRACT,['200912','201003'])
        with duckdb.connect(config={'threads':1,'memory_limit':'256MiB'}) as conn:
            _window(conn,cadsource,['200912','201003'],view='cad')
            for row in math._records(conn.execute('select * from cad')):
                key=(row['CodInst'],row['Data'])
                if key in cadres and cadres[key]!=row:raise ValueError('Ambiguous opening cadastro')
                cadres[key]=row
        sources['cadastro']=cadsource
    unit_entries=[e for e in main['files'] if e['file']=='unit_periods.csv']
    if len(unit_entries)!=1:raise ValueError('Missing baseline unit inventory')
    ue=unit_entries[0];_capture_payload(root,ue);up=math._contained(root,ue['file']);protect(up)
    units={};count=0;csv.field_size_limit(10000000)
    with up.open(encoding='utf-8',newline='') as f:
        for raw in csv.DictReader(f):
            count+=1
            if raw['dataset'] not in datasets or raw['period'] not in periods:continue
            u=math._json_unique(raw['payload'].encode('utf-8'));ds=raw['dataset'];p=raw['period'];code=u['code'];key=(ds,code,p)
            if key in units or u['dataset']!=ds or u['period']!=p or u['unit_id']!='|'.join((ds,TYPES[ds],code,p)):
                raise ValueError('Ambiguous complement native unit')
            units[key]=u
    if count!=ue['rows'] or count!=main['tables']['unit_periods'] or not units:raise ValueError('Native population count mismatch')
    if {(ds,p) for ds,_,p in units}!={(ds,p) for ds in datasets for p in periods}:raise ValueError('Missing selected population perspective/period')
    for path,before in guards.items():
        if identity(path)!=before:raise ValueError('Complement input changed during authentication')
    output.mkdir(parents=True);files=[]
    supplement=output/'complement-contexts.json';supplement.write_text(canonical(profile)+'\n',encoding='utf-8')
    with ExitStack() as stack,duckdb.connect(config={'threads':1,'memory_limit':'256MiB'}) as conn:
        writers={t:Writer(output,t,stack,formats=formats) for t in ('components','results','unit_coverage')}
        for ds in datasets:
            _window(conn,sources[ds],native_periods,dataset=ds)
            if openings:_window(conn,openings,['200912'],dataset=ds,opening=True,view='opening')
            codes=sorted({code for dataset,code,p in units if dataset==ds})
            accounts=sorted({c['literal_context']['Conta'] for c in profile['contexts'] if c['literal_context']['dataset']==ds and c['component'] in {math.COMPONENT_NAMES[n] for n in required}})
            columns=','.join('"'+c+'"' for c in COLUMNS)
            for offset in range(0,len(codes),32):
                batch=codes[offset:offset+32]
                sql='select '+columns+' from native where CodInst in (select unnest(?)) and Conta in (select unnest(?))'
                rows=math._records(conn.execute(sql,[batch,accounts]));indexed={};cache={};opening_rows=[]
                for row in rows:indexed.setdefault((row['CodInst'],row['AnoMes']),[]).append(row)
                if openings:opening_rows=math._records(conn.execute(sql.replace('from native','from opening'),[batch,accounts]))
                def component(code,name,p):
                    key=(code,name,p)
                    if key not in cache:
                        ob=(opening_observation(profile,name,ds,code,opening_rows,indexed.get((code,'201003'),[]),cadres) if p=='200912'
                            else math.resolve_component(profile,math.COMPONENT_NAMES[name],ds,code,p,indexed.get((code,p),[])))
                        if p!='200912' and ob['binding'] and (canonical(ob['binding']['literal_context']),p) not in catalogue_keys:
                            ob.update(status='catalogue_context_missing',token=None)
                        ob.update(id=hashlib.sha256(('|'.join((ds,TYPES[ds],code,p,name))).encode()).hexdigest()[:32],
                                  component=name,dataset=ds,code=code,status=ob.get('status','ok'))
                        cache[key]=ob;writers['components'].append(_compact_component(ob))
                    return cache[key]
                for code in batch:
                    for p in sorted(periods):
                        unit=units.get((ds,code,p))
                        if unit is None:continue
                        asset=component(code,'AT',p);av,ast=math._native_value(asset)
                        if not unit.get('own_cadastro'):av,ast=None,'missing_dated_cadastro'
                        for metric in metrics:
                            for horizon in horizons[metric]:
                                observations={n:[_thin(component(code,n,d)) for d in component_periods(n,p,horizon)] for n in math.COMPLEMENT_METRICS[metric]}
                                result=math.evaluate_metric(metric,dict(period=p,components=observations,financial_statement=True),horizon)
                                result.update(id=unit['unit_id']+'|'+metric+'|'+horizon,unit_id=unit['unit_id'],unit_key=[ds,TYPES[ds],code],dataset=ds,code=code,membership=unit['membership'])
                                result=_normalize_temporal(result);writers['results'].append(result)
                                covered={k:deepcopy(result.get(k)) for k in ('period','dataset','code','metric','horizon','status','applicability','applicability_evidence','value_fraction','numerator_fraction','denominator_fraction','flags','limits','annual_summary')}
                                covered.update(id=result['id']+'|coverage',result_id=result['id'],row_kind='native_unit',unit_id=unit['unit_id'],unit_key=result['unit_key'],
                                    membership=unit['membership'],companies=unit['companies'],asset_fraction=math._fraction_field(av) if av is not None else None,
                                    asset_status=ast or 'ok',target_cadastro=dict(Data=p,**unit['classifications']) if unit.get('classifications') is not None else None)
                                writers['unit_coverage'].append(covered)
        for writer in writers.values():files.extend(writer.finish(conn))
        counts={t:w.count for t,w in writers.items()}
    for path,before in guards.items():
        if identity(path)!=before:raise ValueError('Complement input changed during calculation')
    files.append(dict(file=supplement.name,sha256=math._digest_file(supplement)))
    manifest=dict(contract='ifdata-complement-analysis-v1',scope=dict(periods=sorted(periods),datasets=datasets,metrics=metrics,horizons=horizons),
        baseline=dict(root=str(root),expected_manifest_sha256=expected_baseline_manifest_sha256),inputs={k:main['inputs'][k] for k in ['catalogue']+datasets},
        opening=main.get('config',{}).get('opening') if openings else None,native_partitions=inventories,unit_periods=ue,
        profile_sha256=main['profile_sha256'],contexts_file=supplement.name,dependency_periods=dependencies,tables=counts,files=files,
        producer_sha256=math._digest_file(Path(__file__)),math_sha256=math._digest_file(Path(math.__file__)),elapsed_seconds=perf_counter()-started,
        limits=['Unit contributions only; compose complete population before system aggregation','Baseline membership is retained; updated membership is a separate composition input'])
    (output/'manifest.json').write_text(canonical(manifest)+'\n',encoding='utf-8')
    return manifest


class Writer:
    def __init__(self,output,table,stack,*,formats=('json','csv','parquet')):
        if tuple(formats) not in (('json','csv','parquet'),('parquet',)):
            raise ValueError('Writer supports historical formats or parquet only')
        self.formats=tuple(formats);self.output,self.table,self.count,self.max_line=output,table,0,2*1024*1024
        self.js=stack.enter_context((output/(table+'.json')).open('w',encoding='utf-8')) if 'json' in formats else None
        self.csv_path=output/(table+'.csv' if 'csv' in formats else '.'+table+'-buffer.csv')
        self.cs=stack.enter_context(self.csv_path.open('w',encoding='utf-8',newline=''))
        self.writer=csv.writer(self.cs,quoting=csv.QUOTE_NOTNULL);self.writer.writerow(math.TABLE_COLUMNS)
        if self.js:self.js.write('[')
    def append(self,row):
        payload=canonical(row)
        if self.js:self.js.write((',' if self.count else '')+'\n'+payload)
        self.writer.writerow([row.get(k) for k in math.TABLE_COLUMNS[:-1]]+[payload]);self.count+=1
        self.max_line=max(self.max_line,len(payload.encode('utf-8'))*4+4096)
    def finish(self,conn):
        if self.js:self.js.write('\n]\n' if self.count else ']\n');self.js.close()
        self.cs.close();columns='{'+','.join("'"+k+"':'VARCHAR'" for k in math.TABLE_COLUMNS)+'}'
        conn.execute('copy (select * from read_csv($source,header=true,auto_detect=false,columns='+columns+
            ",delim=',',quote='\"',escape='\"',nullstr='',allow_quoted_nulls=false,parallel=true,max_line_size=$limit)) "+
            'to $destination (format parquet,compression zstd,row_group_size 2048)',
            dict(source=str(self.csv_path),limit=str(self.max_line),destination=str(self.output/(self.table+'.parquet'))))
        if 'csv' not in self.formats:self.csv_path.unlink()
        return [dict(file=self.table+'.'+ext,sha256=math._digest_file(self.output/(self.table+'.'+ext)),rows=self.count) for ext in self.formats]


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


def _producer_snapshot(config,stage,batch_size):
    import platform
    import sys
    import duckdb
    from datetime import datetime,timezone
    package=Path(__file__).parent
    # Freeze the finite responsible package upfront, including lazily imported
    # readers. No module can evade stamping by loading after execution starts.
    sources=sorted(package.glob('*.py'))+[PROFILE_PATH,math.PROFILE_PATH,package.parent/'scripts/analyze-ifdata.py']
    return dict(started_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256={str(p.resolve()):math._digest_file(p) for p in sources},
        runtime=dict(python=platform.python_version(),executable=sys.executable,duckdb=duckdb.__version__,platform=platform.platform()),
        config_sha256=hashlib.sha256(canonical(dict(config=config,stage=stage)).encode()).hexdigest(),batch_size=batch_size,
        source_inventory='all_responsible_bank_quality_python_modules_plus_profiles_and_cli',
        attribution='this_build_only_not_retroactive_to_preexisting_unit_packages')


def _check_producer(producer):
    for filename,pin in producer['source_sha256'].items():
        if math._digest_file(Path(filename))!=pin:raise ValueError('Producer source changed during execution: '+filename)


def logical_payload_sha256(manifest):
    """Operational UTC, batch size and runtime are deliberately not economics."""
    payload={k:manifest[k] for k in ('contract','stage','config','inputs','profile_sha256','tables')}
    payload['files']=sorted(manifest['files'],key=lambda e:e['file'])
    return hashlib.sha256(canonical(payload).encode()).hexdigest()


def _coverage_windows(root,manifest,population):
    """One period/perspective of slim coverage; never retain temporal history."""
    from itertools import groupby
    with ExitStack() as stack:
        streams={t:math._iter_json_array(root/(t+'.json')) for t in TABLES[:3]}
        for stream in streams.values():stack.callback(stream.close)
        units=iter(groupby(streams['unit_periods'],lambda r:(r['period'],r['dataset'])))
        current=next(units,None)
        components=iter(groupby(streams['components'],lambda r:(r['analysis_period'],r['dataset'],r['code'])))
        results=iter(groupby(streams['results'],lambda r:(r['period'],r['dataset'],r['code'])))
        matrices={r['period']:r for r in population['matrices']}
        states={(r['period'],r['dataset']):r['population_state'] for r in population['periods']}
        for period in manifest['periods']:
            for dataset in manifest['config']['datasets']:
                coverage=[];linked=set();key=(period,dataset)
                copresence={}
                for p in population['parent_copresence']:
                    if (p['period'],p['dataset'])==key:copresence.setdefault(p['code'],[]).append(p)
                if current is not None and current[0]==key:
                    for unit in current[1]:
                        cg=next(components,None);rg=next(results,None);identity=(*key,unit['code'])
                        if cg is None or rg is None or cg[0]!=identity or rg[0]!=identity:raise ValueError('Derived native stream completeness mismatch')
                        observations=list(cg[1]);asset=next((o for o in observations if o['component']=='AT' and o['period']==period),None)
                        av,ast=math._native_value(asset) if asset else (None,'own_assets_unavailable')
                        if asset and not unit.get('own_cadastro'):av,ast=None,'missing_dated_cadastro'
                        if dataset=='capital':av,ast=None,'own_assets_unavailable'
                        linked.update(unit['companies'])
                        for result in rg[1]:
                            row={k:deepcopy(result.get(k)) for k in ('period','dataset','code','metric','horizon','status','applicability','applicability_evidence','value_fraction','numerator_fraction','denominator_fraction','flags','limits','annual_summary')}
                            row.update(id=result['id']+'|coverage',row_kind='native_unit',result_id=result['id'],unit_id=unit['unit_id'],unit_key=result['unit_key'],
                                membership=unit['membership'],membership_reason=unit['membership_reason'],companies=unit['companies'],
                                asset_fraction=math._fraction_field(av) if av is not None else None,asset_status=ast or 'ok',asset_component_id=asset['id'] if asset else None,
                                target_cadastro=dict(Data=period,**unit['classifications']) if unit['classifications'] is not None else None,
                                parent_copresence=copresence.get(unit['code'],[]),population_state=states[key])
                            coverage.append(row)
                    current=next(units,None)
                for company in matrices[period]['company_rows']:
                    if company['company_id'] in linked:continue
                    for metric in math.METRICS:
                        if (metric in ('C3','C4'))!=(dataset=='capital'):continue
                        for horizon in (('quarter','ttm') if metric in math.FLOW_METRICS else ('point',)):
                            coverage.append(dict(id='nominal|'+period+'|'+dataset+'|'+company['company_id']+'|'+metric+'|'+horizon,
                                row_kind='nominal_company',period=period,dataset=dataset,code=None,metric=metric,horizon=horizon,
                                unit_id=None,unit_key=None,result_id=None,membership='sample',companies=[company['company_id']],
                                status='missing_native_unit',applicability='unknown',numerator_fraction=None,denominator_fraction=None,value_fraction=None,
                                asset_fraction=None,asset_status='no_native_unit',asset_component_id=None,target_cadastro=None,
                                flags=[],company_relation=company,population_state=states[key]))
                yield coverage
        if current is not None or next(components,None) is not None or next(results,None) is not None:raise ValueError('Derived orphan native group')


def _derived_windows(root,manifest,population):
    for coverage in _coverage_windows(root,manifest,population):
        yield dict(unit_coverage=coverage,**aggregate_unit_results(coverage))


def _finish_derived(output,manifest,population):
    """Persist wide derived rows with their measured COPY budget."""
    import duckdb
    with ExitStack() as stack,duckdb.connect(config={'memory_limit':'1GiB','threads':1}) as con:
        writers={t:Writer(output,t,stack) for t in DERIVED_TABLES}
        for tables in _derived_windows(output,manifest,population):
            for table,rows in tables.items():
                for row in rows:writers[table].append(row)
        for table,writer in writers.items():
            manifest['files'].extend(writer.finish(con));manifest['tables'][table]=writer.count


def _prepare_inputs(config,batch_size=32):
    from .ifdata_population import CONTRACT as POP_CONTRACT,_metadata
    from .ifdata_odata import CONTRACT as DATA_CONTRACT
    from .ifdata_cadastro import CONTRACT as CAD_CONTRACT
    from .ifdata_variable_catalog import CONTRACT as CAT_CONTRACT,query_catalog
    required={'periods','datasets','profile_id','profile_expected_sha256','population'}
    if not isinstance(config,dict) or not required<=set(config) or set(config)-required-{'opening'}:raise ValueError('Invalid universe config')
    if type(batch_size) is not int or batch_size<1:raise ValueError('Positive batch size required')
    config=deepcopy(config)
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
    return config,periods,datasets,dependencies,pin,profile,poproot,pop,inputs,accepted,catalogue


def _unit_manifest(config,files,counts,stage='unit-calculations'):
    periods=sorted(config['periods']);datasets=config['datasets'];pin=config['profile_expected_sha256']
    dependencies=math.dependency_periods(periods)
    _,pop=math._authenticate(config['population'])
    inputs=pop['config']['inputs']
    normalized=deepcopy(config);normalized['periods']=periods;normalized['datasets']=sorted(datasets)
    manifest=dict(contract=CONTRACT,stage=stage,config=normalized,inputs=inputs,profile_sha256=pin,
                  periods=periods,dependency_periods=dependencies,tables=counts,table_columns=list(math.TABLE_COLUMNS),files=files,
                  reference_contract='profile-context-and-window-component-v1',
                  limitations=['Technical native sums are not a certified system total','Prudential own assets unknown; no financial proxy','Membership does not control native applicability','No constituent or issuer-control continuity inferred'])
    return manifest


def build(config,output,*,batch_size=32,stage='coverage-and-aggregation'):
    import duckdb
    from .ifdata_population import open_population,CONTRACT as POP_CONTRACT
    output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if stage not in ('unit-calculations','coverage-and-aggregation'):raise ValueError('Invalid universe stage')
    producer=_producer_snapshot(config,stage,batch_size)
    config,periods,datasets,dependencies,pin,profile,poproot,pop,inputs,accepted,catalogue=_prepare_inputs(config,batch_size)
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
    manifest=_unit_manifest(config,files,counts,stage)
    if stage=='coverage-and-aggregation':
        _finish_derived(output,manifest,pop)
    # Final aggregation can be long: the last authentication and source check
    # belong immediately before acceptance, not only before derived output.
    math._authenticate(config['population'],POP_CONTRACT,True)
    for name in accepted:math._authenticate(config['opening'] if name=='opening' else inputs[name])
    _check_producer(producer)
    from datetime import datetime,timezone
    producer.update(finished_utc=datetime.now(timezone.utc).isoformat(),source_stability='verified_before_manifest',
                    inputs=deepcopy(inputs),population=deepcopy(config['population']),profile_sha256=pin)
    manifest['producer']=producer
    manifest['logical_payload_sha256']=logical_payload_sha256(manifest)
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
    root,m=math._authenticate(dict(root=str(output),expected_manifest_sha256=expected_manifest_sha256),CONTRACT,True)
    return _verify_contents(root,m)


def _verify_contents(root,m):
    import duckdb
    tables=TABLES if m.get('stage')=='unit-calculations' else FINAL_TABLES if m.get('stage')=='coverage-and-aggregation' else ()
    if not tables or set(m.get('tables',{}))!=set(tables) or m.get('table_columns')!=list(math.TABLE_COLUMNS):
        raise ValueError('Universe stage/schema mismatch')
    if {e['file'] for e in m['files']}!={t+'.'+e for t in tables for e in ('json','csv','parquet')}:raise ValueError('Universe inventory mismatch')
    profile=load_profile(m['config']['profile_id'],m['profile_sha256'])
    known_contexts={c['context_sha256']:c for c in profile['contexts']}
    with duckdb.connect(config={'memory_limit':'512MiB','threads':1}) as con:
        for table in tables:
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
    if m['stage']=='coverage-and-aggregation':
        _,population=math._authenticate(m['config']['population'])
        with ExitStack() as stack:
            actual={t:math._iter_json_array(root/(t+'.json')) for t in DERIVED_TABLES}
            for stream in actual.values():stack.callback(stream.close)
            for derived in _derived_windows(root,m,population):
                for table,rows in derived.items():
                    for row in rows:
                        if next(actual[table],None)!=row:raise ValueError('Derived table/reference/reconciliation mismatch: '+table)
            for table,stream in actual.items():
                if next(stream,None) is not None:raise ValueError('Derived extra row: '+table)
        if m.get('logical_payload_sha256')!=logical_payload_sha256(m):raise ValueError('Derived logical payload digest mismatch')
        producer=m.get('producer',{})
        if not producer.get('source_sha256') or producer.get('source_stability')!='verified_before_manifest':raise ValueError('Missing producer provenance')
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
    raw=math.PROFILE_PATH.read_bytes();lf=raw.replace(b'\r\n',b'\n');crlf=lf.replace(b'\n',b'\r\n')
    # Only the two exact line-ending spellings of reviewed installed content.
    # The embedded anchor must authenticate that content before an alias can
    # authenticate a baseline; edited content cannot authorize its own hashes.
    lineage={hashlib.sha256(content).hexdigest() for content in (lf,crlf)}
    if (b'\r' in lf or raw not in (lf,crlf) or profile['legacy_profile_sha256'] not in lineage
            or old['profile_sha256'] not in lineage):
        raise ValueError('Baseline profile is outside reviewed lineage')
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
    if old.get('stage')=='coverage-and-aggregation':
        report['aggregate_projection']=_compare_aggregates(root,manifest,oldroot)
        if report['aggregate_projection']['differences']:report['status']='different'
    else:report['aggregate_projection']={'status':'baseline_has_no_aggregate_stage'}
    return report


def _aggregate_signature(row,distribution=None):
    """Normalize representation, never drop contributor identities or flags."""
    result={k:row.get(k) for k in ('status','numerator_fraction','denominator_fraction','value_fraction')}
    result['eligible_units']=sorted('|'.join([*unit,row['period']]) if isinstance(unit,list) else unit
                                    for unit in row['lists']['eligible_units'])
    result['eligible_unit_count']=row['counts']['eligible_units']
    result['flags']=row['flags']
    if distribution is not None:
        result.update({k:distribution.get(k) for k in ('q1_fraction','median_fraction','q3_fraction','iqr_fraction')},distribution_n=distribution['n'])
    return result


def _compare_aggregates(root,manifest,oldroot):
    """Public, bounded projection of principal127 onto identical native keys.

    Old company relations select the intersection, never supply new numerical
    values. New native reductions independently reconstruct economic sums and
    quantiles. Stored legacy tables are also checked against their full legacy
    coverage. Associated capital financial AT uses the dated population matrix
    as an explicit relation, and is never called own prudential assets.
    """
    import sqlite3
    import tempfile
    from itertools import groupby
    def groupkey(row,segment=False):
        return canonical([row[k] for k in ('period','dataset','metric','horizon')]+([row['field'],row['category_state'],row['category']] if segment else []))
    report=dict(status='exact_on_identical_native_intersection',aggregate_groups_compared=0,segment_groups_compared=0,
        differences=[],excluded_nominal_relations=[],associated_financial_coverage=[],
        scope='principal127 native intersection only; complementary observations are not adopted',
        coverage_scope='own perspective assets and nominal company populations are separately defined; ten-metric legacy joint coverage is not universe eligibility',groups=[])
    _,population=math._authenticate(manifest['config']['population'])
    matrices={m['period']:{r['company_id']:r for r in m['company_rows']} for m in population['matrices']}
    with tempfile.TemporaryDirectory(prefix='ifdata-aggregate-projection-') as temporary,closing(sqlite3.connect(str(Path(temporary)/'projection.sqlite'))) as db:
        db.execute('create table records (table_name text,period text,dataset text,payload text)')
        for table in ('company_coverage','aggregates','distributions','segment_coverage'):
            with closing(math._iter_json_array(oldroot/(table+'.json'))) as stream:
                for row in stream:
                    if row.get('block')=='principal' and row['period'] in manifest['periods']:
                        db.execute('insert into records values (?,?,?,?)',(table,row['period'],row['dataset'],canonical(row)))
        db.execute('create index scope on records (period,dataset,table_name)');db.commit()
        windows=_coverage_windows(root,manifest,population)
        for period,batches in groupby(windows,lambda rows:rows[0]['period']):
            native={};assets={}
            for rows in batches:
                dataset=rows[0]['dataset']
                expected={ (r['code'],r['metric'],r['horizon']) for (payload,) in db.execute("select payload from records where period=? and dataset=? and table_name='company_coverage'",(period,dataset)) for r in [json.loads(payload)] }
                native[dataset]={(r['code'],r['metric'],r['horizon']):r for r in rows if r.get('unit_id') and (r['code'],r['metric'],r['horizon']) in expected}
                if dataset=='financial':
                    assets={r['code']:dict(asset_fraction=r['asset_fraction'],asset_status=r['asset_status'],target_cadastro=r['target_cadastro']) for r in rows if r.get('unit_id')}
            for dataset,newrows in sorted(native.items()):
                oldrows=[json.loads(payload) for (payload,) in db.execute("select payload from records where period=? and dataset=? and table_name='company_coverage'",(period,dataset))]
                if not oldrows:continue
                full=math.aggregate_results([json.loads(payload) for (payload,) in db.execute("select payload from records where period=? and table_name='company_coverage'",(period,))])
                # Authenticate economic consistency of the stored127 aggregates,
                # including nominal rows outside the new native population.
                for table in ('aggregates','distributions','segment_coverage'):
                    rebuilt={groupkey(r,table=='segment_coverage'):r for r in full[table] if r['dataset']==dataset}
                    stored={groupkey(r,table=='segment_coverage'):r for (payload,) in db.execute('select payload from records where period=? and dataset=? and table_name=?',(period,dataset,table)) for r in [json.loads(payload)]}
                    for key in sorted(set(rebuilt)|set(stored)):
                        if rebuilt.get(key)!=stored.get(key):report['differences'].append(dict(scope='stored_legacy_'+table,key=key,cause='stored_table_disagrees_with_legacy_coverage'))
                selected=[];related={}
                for oldrow in oldrows:
                    key=(oldrow['code'],oldrow['metric'],oldrow['horizon']);new=newrows.get(key)
                    if new is None or oldrow.get('result_id') is None:
                        report['excluded_nominal_relations'].append({k:oldrow.get(k) for k in ('company','period','dataset','code','metric','horizon','status')})
                        continue
                    selected.append(oldrow);related.setdefault(key,[]).append(oldrow)
                oldprojection=math.aggregate_results(selected)
                projected=[dict(newrows[key],companies=sorted({r['company'] for r in relations})) for key,relations in sorted(related.items())]
                newprojection=aggregate_unit_results(projected)
                olddistributions={groupkey(r):r for r in oldprojection['distributions']}
                newdistributions={groupkey(r):r for r in newprojection['distributions'] if r['cohort']=='total'}
                for table in ('aggregates','segment_coverage'):
                    segment=table=='segment_coverage'
                    left={groupkey(r,segment):r for r in oldprojection[table]}
                    right={groupkey(r,segment):r for r in newprojection[table] if r['cohort']=='total'}
                    for key in sorted(set(left)|set(right)):
                        a,b=left.get(key),right.get(key)
                        ac=_aggregate_signature(a,a['distribution'] if segment else olddistributions[key]) if a else None
                        bc=_aggregate_signature(b,b['distribution'] if segment else newdistributions[key]) if b else None
                        if ac!=bc:report['differences'].append(dict(scope=table,key=key,baseline=ac,universe=bc))
                        report['segment_groups_compared' if segment else 'aggregate_groups_compared']+=1
                        report['groups'].append(dict(table=table,key=key,baseline_core_sha256=hashlib.sha256(canonical(ac).encode()).hexdigest(),universe_core_sha256=hashlib.sha256(canonical(bc).encode()).hexdigest()))
                # Actual company relations only: independently source their AT
                # from new financial units, behind the dated native matrix.
                associated=[];unproved=[]
                for oldrow in selected:
                    new=newrows[(oldrow['code'],oldrow['metric'],oldrow['horizon'])]
                    relation=matrices[period].get(oldrow['company'],{})
                    financial=relation.get('financial_target')
                    approved=(financial==oldrow.get('financial_unit_key',[None,None,None])[2] if oldrow.get('financial_unit_key') else False)
                    if dataset=='capital':approved=approved and relation.get('prudential_target')==oldrow['code'] and relation.get('prudential_state')=='agreed_dated_bridge'
                    else:approved=approved and financial==oldrow['code']
                    asset=assets.get(financial) if approved else None
                    if asset is None:
                        unproved.append(dict(company=oldrow['company'],code=oldrow['code'],metric=oldrow['metric'],horizon=oldrow['horizon'],reason='associated_financial_source_or_dated_relation_unavailable'));continue
                    relatedrow=dict(oldrow,**{k:new.get(k) for k in ('status','applicability','numerator_fraction','denominator_fraction','value_fraction','flags')},
                        target_cadastro={k:v for k,v in (new.get('target_cadastro') or {}).items() if k in ('Data',*AXES)},
                        asset_fraction=asset['asset_fraction'],asset_status=asset['asset_status'])
                    associated.append(relatedrow)
                eligible_relations={(r['company'],r['metric'],r['horizon']) for r in associated}
                original=math.aggregate_results([r for r in selected if (r['company'],r['metric'],r['horizon']) in eligible_relations])
                comparison=math.aggregate_results(associated)
                for table in ('aggregates','segment_coverage'):
                    segment=table=='segment_coverage';a={groupkey(r,segment):r for r in original[table]};b={groupkey(r,segment):r for r in comparison[table]}
                    for key in sorted(set(a)|set(b)):
                        ac=a[key]['asset_coverage'] if key in a else None;bc=b[key]['asset_coverage'] if key in b else None
                        if ac!=bc:report['differences'].append(dict(scope='associated_financial_coverage_'+table,key=key,baseline=ac,universe=bc))
                report['associated_financial_coverage'].append(dict(period=period,dataset=dataset,
                    reference='explicit_dated_native_relation_to_financial_AT_not_own_capital_AT',
                    compared_relations=len(associated),unproved=unproved,scope='same_proved_relation_intersection'))
    if report['differences']:report['status']='different'
    return report


def _snapshot_manifest(output,expected_manifest_sha256):
    """Authenticate accepted snapshot metadata; never claim financial revalidation."""
    if not isinstance(expected_manifest_sha256,str) or not re.fullmatch('[0-9a-f]{64}',expected_manifest_sha256):
        raise ValueError('Invalid external pin')
    root=_ordinary(output).resolve();raw=_ordinary(root/'manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_manifest_sha256:raise ValueError('Manifest external pin mismatch')
    m=math._json_unique(raw)
    if not isinstance(m,dict) or m.get('contract')!=CONTRACT:raise ValueError('Input contract mismatch')
    tables=TABLES if m.get('stage')=='unit-calculations' else FINAL_TABLES if m.get('stage')=='coverage-and-aggregation' else ()
    if not tables or set(m.get('tables',{}))!=set(tables) or m.get('table_columns')!=list(math.TABLE_COLUMNS):
        raise ValueError('Universe stage/schema mismatch')
    files=m.get('files');expected={t+'.'+e for t in tables for e in ('json','csv','parquet')}
    if not isinstance(files,list) or len(files)!=len(expected):raise ValueError('Universe inventory mismatch')
    seen=set()
    for entry in files:
        if (not isinstance(entry,dict) or entry.get('file') not in expected or entry['file'] in seen
                or not isinstance(entry.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',entry['sha256'])
                or type(entry.get('rows')) is not int or entry['rows']<0
                or entry['rows']!=m['tables'][entry['file'].rsplit('.',1)[0]]):
            raise ValueError('Invalid universe inventory item')
        seen.add(entry['file'])
        if not _ordinary(root/entry['file']).is_file():raise ValueError('Missing ordinary snapshot file')
    if {p.name for p in root.iterdir()}!=expected|{'manifest.json'}:raise ValueError('Universe inventory mismatch')
    config=m.get('config',{})
    if (config.get('profile_expected_sha256')!=m.get('profile_sha256') or config.get('periods')!=m.get('periods')
            or m.get('dependency_periods')!=math.dependency_periods(config['periods'])
            or m.get('reference_contract')!='profile-context-and-window-component-v1'):
        raise ValueError('Universe metadata contract mismatch')
    load_profile(config['profile_id'],m['profile_sha256'])
    if m.get('logical_payload_sha256')!=logical_payload_sha256(m):raise ValueError('Universe logical metadata mismatch')
    return root,m


def _capture_payload(root,entry,destination=None):
    """Hash a bounded stream, optionally retaining exactly those bytes for SQL."""
    path=_ordinary(root/entry['file']);before=path.stat();digest=hashlib.sha256()
    with ExitStack() as stack:
        source=stack.enter_context(path.open('rb'))
        target=stack.enter_context(Path(destination).open('xb')) if destination is not None else None
        for block in iter(lambda:source.read(1024*1024),b''):
            digest.update(block)
            if target is not None:target.write(block)
    after=_ordinary(path).stat()
    identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    if identity(before)!=identity(after) or digest.hexdigest()!=entry['sha256']:raise ValueError('Snapshot payload hash/identity changed: '+entry['file'])
    return digest.hexdigest()


def query(output,expected_manifest_sha256,sql):
    """Query selected authenticated bytes of a caller-pinned accepted snapshot.

    Full financial verification remains the separate verify/compare gate.
    """
    import duckdb
    import tempfile
    settings={'memory_limit':'512MiB','threads':1,'autoload_known_extensions':False,'autoinstall_known_extensions':False}
    # DuckDB's own parser identifies references before any payload is read.
    with duckdb.connect(config=dict(settings,enable_external_access=False)) as parser:
        statements=parser.extract_statements(sql)
        if len(statements)!=1 or statements[0].type!=duckdb.StatementType.SELECT:raise ValueError('Query must be one SELECT')
        selected={name.lower() for name in parser.get_table_names(sql,qualified=True)}
    if not selected<=set(FINAL_TABLES):raise ValueError('Query references a table outside the universe allowlist')
    root,manifest=_snapshot_manifest(output,expected_manifest_sha256)
    if not selected<=set(manifest['tables']):raise ValueError('Query table unavailable in this snapshot stage')
    entries={e['file']:e for e in manifest['files']}
    with tempfile.TemporaryDirectory(prefix='ifdata-universe-query-') as temporary, duckdb.connect(str(Path(temporary)/'query.duckdb'),config=settings) as con:
        for table in sorted(selected):
            copy=Path(temporary)/(table+'.parquet');_capture_payload(root,entries[copy.name],copy)
            con.execute('create table '+table+' as select * from read_parquet(?)',[str(copy)])
            math._schema(con,table,math.TABLE_COLUMNS)
        con.execute('set enable_external_access=false')
        cur=con.execute(sql);fields=[c[0] for c in cur.description];rows=cur.fetchmany(10001)
        if len(rows)>10000:raise ValueError('Query row limit exceeded; select an explicit smaller scope')
        return [dict(zip(fields,row)) for row in rows]

def _original_calculation(manifest,checkpoint):
    """Read already accepted admission evidence, not later finalization identity."""
    calculation=manifest.get('calculation_producer',{})
    if (calculation.get('evidence_kind')!='caller_preflight_and_failed_terminal_receipt'
            or checkpoint.get('capture_timing')!='captured_at_checkpoint_admission'
            or checkpoint.get('file_hashes_captured_later') is not True):
        raise ValueError('Replay requires the admitted original calculation evidence')
    evidence=checkpoint.get('evidence',{});blob=evidence.get('preflight',{})
    raw=blob.get('raw_utf8','').encode('utf-8')
    if hashlib.sha256(raw).hexdigest()!=blob.get('sha256'):raise ValueError('Original calculation receipt hash mismatch')
    pre=math._json_unique(raw)
    source=_ordinary(checkpoint.get('source_root','')).resolve()
    if (_ordinary(pre.get('output','')).resolve()!=source or type(pre.get('pid')) is not int
            or not pre.get('started_utc') or pre.get('pid')!=calculation.get('pid')
            or pre.get('started_utc')!=calculation.get('started_utc')
            or pre.get('source_before')!=calculation.get('source_sha256')):
        raise ValueError('Original calculation identity mismatch')
    return dict(source_root=str(source),pid=pre['pid'],started_utc=pre['started_utc'],
        process_created_utc=pre.get('process_created_utc'),finished_utc=calculation.get('finished_utc'),
        head=calculation.get('head'),source_sha256=calculation['source_sha256'],runtime=calculation.get('runtime'),
        evidence_descriptor_sha256=evidence.get('descriptor_sha256'),
        limitation=calculation.get('attribution_limit'),file_hashes_captured_later=True)


def compare_replay(output,expected_manifest_sha256,replay_unit_checkpoint,expected_replay_manifest_sha256,derived_source_root):
    """Compare accepted unit payloads and original derived CSV logical values.

    The caller must separately complete main full semantic validation. This
    report neither reaccepts failed derived prefixes nor certifies 27 physical
    representations of a second final package.
    """
    _,main=_snapshot_manifest(output,expected_manifest_sha256)
    replay_root,replay=_snapshot_manifest(replay_unit_checkpoint,expected_replay_manifest_sha256)
    if main['stage']!='coverage-and-aggregation' or replay['stage']!='unit-calculations':
        raise ValueError('Replay requires final main and accepted unit checkpoint')
    for key in ('config','inputs','profile_sha256','periods','dependency_periods','table_columns','reference_contract'):
        if main.get(key)!=replay.get(key):raise ValueError('Replay configuration/schema mismatch: '+key)
    main_checkpoint=main.get('unit_checkpoint',{})
    a=_original_calculation(main,main_checkpoint.get('provenance',{}))
    b=_original_calculation(replay,replay.get('unit_checkpoint',{}))
    if (expected_replay_manifest_sha256==main_checkpoint.get('manifest_sha256')
            or a['source_root']==b['source_root']
            or (a['pid'],a['started_utc'])==(b['pid'],b['started_utc'])):
        raise ValueError('Replay reused the same original calculation')
    if a['source_sha256']!=b['source_sha256']:raise ValueError('Replay original calculation source mismatch')
    derived_root=_ordinary(derived_source_root).resolve()
    if str(derived_root)!=b['source_root']:raise ValueError('Replay derived source root differs from accepted checkpoint')
    expected={e['file']:e for e in main['files']}
    unit=[];derived=[]
    for entry in replay['files']:
        if entry!=expected[entry['file']]:raise ValueError('Replay unit payload metadata mismatch')
        _capture_payload(replay_root,entry)
        unit.append(dict(entry,comparison='physical_bytes_equal',row_count_basis='accepted_manifest_and_byte_equality'))
    for table in DERIVED_TABLES:
        entry=expected[table+'.csv'];_capture_payload(derived_root,entry)
        derived.append(dict(table=table,**entry,comparison='csv_logical_values_byte_equal',
            row_count_basis='main_validated_manifest_and_byte_equality_not_reparsed'))
    return dict(status='equal',contract=CONTRACT,main_manifest_sha256=expected_manifest_sha256,
        replay_unit_manifest_sha256=expected_replay_manifest_sha256,
        unit_physical_payloads=unit,derived_csv_logical_tables=derived,
        original_calculations=dict(main=a,replay=b),
        main_full_semantic_validation='required_separate_gate',financial_acceptance=False,
        limitations=['Original failure-time unit hashes do not exist; hashes were captured at admission',
            'Distinct original process receipts and source roots support replay attribution; finalizations alone do not',
            'Only 12 unit physical payloads and five derived CSV logical tables compared; no second 27-file physical replay claim'])


def _ordinary(path):
    """Reject redirects before resolving, including Windows junctions."""
    import stat
    path=Path(path).absolute()
    for item in (path,*path.parents):
        if item.is_symlink() or (item.exists() and getattr(item.lstat(),'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400)):
            raise ValueError('Checkpoint path redirects are forbidden')
    return path


def _checkpoint_paths(source,output):
    source=_ordinary(source).resolve();output=_ordinary(output).resolve()
    if source==output or source in output.parents or output in source.parents:
        raise ValueError('Checkpoint source/output overlap')
    if output.exists():raise FileExistsError(output)
    return source,output


def _unit_inventory(root):
    inventory=[]
    for table in TABLES:
        count=0
        for ext in ('json','csv','parquet'):
            name=table+'.'+ext;path=_ordinary(root/name)
            if not path.is_file():raise ValueError('Missing ordinary unit file: '+name)
            inventory.append(dict(file=name,sha256=math._digest_file(path),bytes=path.stat().st_size))
        with closing(math._iter_json_array(root/(table+'.json'))) as stream:
            for _ in stream:count+=1
        for item in inventory[-3:]:item['rows']=count
    return inventory


def _guard_units(source,output,inventory):
    for entry in inventory:
        a=_ordinary(source/entry['file']);b=_ordinary(output/entry['file']) if output else a
        if (not a.is_file() or not b.is_file() or not a.samefile(b)
                or a.stat().st_size!=entry['bytes'] or math._digest_file(a)!=entry['sha256']):
            raise ValueError('Checkpoint unit bytes/identity changed: '+entry['file'])


def _link_units(source,output,inventory):
    import os
    output.mkdir(parents=True,exist_ok=False)
    for entry in inventory:
        # os.link fails on occupied paths or incompatible filesystems. No copy fallback.
        os.link(source/entry['file'],output/entry['file'])
    _guard_units(source,output,inventory)


def _operation_producer(config,operation,external_pin):
    producer=_producer_snapshot(config,'unit-calculations',None)
    producer.update(operation=operation,external_pin=external_pin,
        attribution='this_operation_only_not_original_unit_calculation',
        config_sha256=hashlib.sha256(canonical(dict(config=config,operation=operation,external_pin=external_pin)).encode()).hexdigest())
    return producer


def _accept_checkpoint(output,manifest,producer,guard):
    from datetime import datetime,timezone
    _prepare_inputs(manifest['config'])
    guard();_check_producer(producer)
    producer.update(finished_utc=datetime.now(timezone.utc).isoformat(),source_stability='verified_before_manifest',
        inputs=deepcopy(manifest['inputs']),population=deepcopy(manifest['config']['population']),profile_sha256=manifest['profile_sha256'])
    manifest['producer']=producer
    manifest['logical_payload_sha256']=logical_payload_sha256(manifest)
    # All guards precede the sole acceptance marker. Never overwrite one.
    with (output/'manifest.json').open('x',encoding='utf-8') as f:
        f.write(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return manifest


def finalize_universe_analysis(checkpoint,expected_manifest_sha256,output):
    """Hardlink a verified unit stage and regenerate only five derived tables."""
    # Verification belongs to this operation's initial source/runtime interval.
    producer=_operation_producer({},'finalize_universe_analysis',expected_manifest_sha256)
    source,output=_checkpoint_paths(checkpoint,output)
    _ordinary(source/'manifest.json')
    manifest=verify(source,expected_manifest_sha256)
    original=manifest.get('producer',{})
    if (manifest.get('logical_payload_sha256')!=logical_payload_sha256(manifest)
            or not isinstance(original,dict) or not original.get('source_sha256')
            or original.get('source_stability')!='verified_before_manifest'):
        raise ValueError('Checkpoint producer/logical payload provenance missing or invalid')
    if manifest['stage']!='unit-calculations':raise ValueError('Finalization requires unit-calculations')
    prepared=_prepare_inputs(manifest['config']);population=prepared[7]
    template=_unit_manifest(manifest['config'],manifest['files'],manifest['tables'])
    for key in template:
        if manifest.get(key)!=template[key]:raise ValueError('Checkpoint normalized configuration mismatch: '+key)
    # Attach authenticated config without refreshing the initial source snapshot.
    producer['config_sha256']=hashlib.sha256(canonical(dict(config=manifest['config'],
        operation=producer['operation'],external_pin=expected_manifest_sha256)).encode()).hexdigest()
    inventory=_unit_inventory(source)
    _guard_units(source,None,inventory)
    _link_units(source,output,inventory)
    result=deepcopy(manifest);result['stage']='coverage-and-aggregation'
    result['calculation_producer']=deepcopy(manifest.get('calculation_producer',manifest.get('producer')))
    result['unit_checkpoint']=dict(contract=CONTRACT,stage='unit-calculations',manifest_sha256=expected_manifest_sha256,
        logical_payload_sha256=logical_payload_sha256(manifest),inventory=inventory,
        provenance=deepcopy(manifest.get('unit_checkpoint',{})),checkpoint_producer=deepcopy(manifest.get('producer')))
    _finish_derived(output,result,population)
    def guard():
        math._authenticate(dict(root=str(source),expected_manifest_sha256=expected_manifest_sha256),CONTRACT,True)
        _guard_units(source,output,inventory)
        expected={e['file'] for e in result['files']}
        if {p.name for p in output.iterdir()}!=expected:raise ValueError('Finalizer output inventory changed')
        for entry in result['files']:
            if math._digest_file(_ordinary(output/entry['file']))!=entry['sha256']:raise ValueError('Finalizer payload changed')
    return _accept_checkpoint(output,result,producer,guard)

def _checkpoint_evidence(config,source,evidence,expected_sha256,inputs):
    """Authenticate exact caller blobs and their original reciprocal records."""
    from datetime import datetime
    path=_ordinary(evidence)
    raw=path.read_bytes()
    if not isinstance(expected_sha256,str) or not re.fullmatch('[0-9a-f]{64}',expected_sha256) or hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('External checkpoint evidence pin mismatch')
    descriptor=math._json_unique(raw)
    if set(descriptor)!={'contract','config','caller','preflight','terminal'} or descriptor['contract']!='ifdata-unit-checkpoint-evidence-v1':
        raise ValueError('Invalid checkpoint evidence descriptor')
    blobs={};pins={str(path):expected_sha256};records={}
    for name in ('config','caller','preflight','terminal'):
        entry=descriptor[name]
        if not isinstance(entry,dict) or set(entry)!={'path','sha256'}:raise ValueError('Invalid evidence blob pin')
        if not isinstance(entry['path'],str) or not Path(entry['path']).is_absolute():raise ValueError('Evidence requires ordinary absolute blob path')
        blobpath=_ordinary(entry['path'])
        if not blobpath.is_absolute() or not blobpath.is_file():raise ValueError('Evidence requires ordinary absolute blob path')
        content=blobpath.read_bytes()
        if not isinstance(entry['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',entry['sha256']) or hashlib.sha256(content).hexdigest()!=entry['sha256']:
            raise ValueError('Checkpoint evidence blob hash mismatch: '+name)
        blobs[name]=dict(path=str(blobpath),sha256=entry['sha256'],raw_utf8=content.decode('utf-8'))
        pins[str(blobpath)]=entry['sha256']
        if name!='caller':records[name]=math._json_unique(content)
    if records['config']!=config:raise ValueError('Original raw config differs from requested config')
    pre=records['preflight'];end=records['terminal']
    if pre.get('status')!='running' or end.get('status')!='failed' or pre.get('mode')!='buildverify':
        raise ValueError('Expected original failed build receipt')
    if any(end.get(k)!=v for k,v in pre.items() if k!='status'):
        raise ValueError('Original preflight/terminal reciprocity mismatch')
    if Path(pre.get('output','')).resolve()!=source or Path(pre.get('config','')).resolve()!=Path(blobs['config']['path']).resolve():
        raise ValueError('Original output/config path mismatch')
    if (type(pre.get('pid')) is not int or pre['pid']<=0 or type(pre.get('batch_size')) is not int or pre['batch_size']<1
            or not re.fullmatch('[0-9a-f]{40}',pre.get('head','')) or end.get('head_after')!=pre['head']
            or end.get('primary_status_after')!='' or pre.get('config_sha256')!=blobs['config']['sha256']
            or end.get('config_sha256_after')!=pre['config_sha256'] or pre.get('wrapper_sha256')!=blobs['caller']['sha256']):
        raise ValueError('Original PID/head/config/wrapper mismatch')
    for before,after,flag in [('source_before','source_after','source_stable'),('input_manifest_before','input_manifest_after','input_manifests_stable')]:
        values=pre.get(before)
        if (not isinstance(values,dict) or not values or end.get(after)!=values or end.get(flag) is not True
                or any(not isinstance(p,str) or not Path(p).is_absolute() or not isinstance(h,str) or not re.fullmatch('[0-9a-f]{64}',h) for p,h in values.items())):
            raise ValueError('Original source/input before-after mismatch')
    expected_inputs={str((Path(e['root'])/'manifest.json').resolve()):e['expected_manifest_sha256']
        for e in dict(inputs,population=config['population'],**({'opening':config['opening']} if 'opening' in config else {})).values()}
    if {str(Path(p).resolve()):h for p,h in pre['input_manifest_before'].items()}!=expected_inputs:
        raise ValueError('Original input manifest correspondence mismatch')
    sources={Path(p).name:h for p,h in pre['source_before'].items()}
    required={Path(p).name for p in _producer_snapshot(config,'unit-calculations',None)['source_sha256']}|{'test_ifdata_analysis.py'}
    if len(sources)!=len(pre['source_before']) or set(sources)!=required or sources[PROFILE_PATH.name]!=config['profile_expected_sha256']:
        raise ValueError('Original responsible source/profile inventory mismatch')
    runtime=pre.get('runtime',{})
    if (set(runtime)!={'python','duckdb','executable','platform'} or any(not isinstance(v,str) or not v for v in runtime.values())
            or not re.fullmatch(r'\d+\.\d+\.\d+',runtime['python']) or not re.fullmatch(r'\d+\.\d+\.\d+',runtime['duckdb'])
            or not Path(runtime['executable']).is_absolute() or not Path(pre.get('actual_executable','')).is_absolute()):
        raise ValueError('Original runtime identity mismatch')
    command=pre.get('process_command_line','')
    if not isinstance(command,str) or any(v not in command for v in (blobs['caller']['path'],pre['actual_executable'],'buildverify',str(pre['batch_size']),pre['head'])):
        raise ValueError('Original process command identity mismatch')
    try:
        times=[datetime.fromisoformat(v) for v in (pre['process_created_utc'],pre['started_utc'],end['finished_utc'])]
        if any(t.utcoffset() is None for t in times) or not times[0]<=times[1]<times[2]:raise ValueError()
    except (KeyError,TypeError,ValueError):raise ValueError('Original process chronology mismatch') from None
    error=end.get('error','')
    if not isinstance(error,str) or not all(v in error for v in ('in build','writer.finish','in finish','OutOfMemoryException')) or any(k in end for k in ('producer','manifest_sha256','verification','logical_payload_sha256')):
        raise ValueError('Expected derived persistence OOM before build returned')
    provenance=dict(evidence_kind='caller_preflight_and_failed_terminal_receipt',runtime=deepcopy(runtime),
        source_sha256=deepcopy(pre['source_before']),source_before=deepcopy(pre['source_before']),source_after=deepcopy(end['source_after']),
        input_manifest_before=deepcopy(pre['input_manifest_before']),input_manifest_after=deepcopy(end['input_manifest_after']),
        batch_size=pre['batch_size'],config_raw_sha256=blobs['config']['sha256'],wrapper_sha256=blobs['caller']['sha256'],
        head=pre['head'],pid=pre['pid'],started_utc=pre['started_utc'],finished_utc=end['finished_utc'],outcome='failed_derived_persistence',
        file_hashes_captured_later=True,attribution_limit='Receipt endpoints only; unit files were first hashed at admission, not at original failure')
    embedded=dict(descriptor_raw_utf8=raw.decode('utf-8'),descriptor_sha256=expected_sha256,**blobs)
    def guard():
        for filename,pin in pins.items():
            if math._digest_file(_ordinary(filename))!=pin:raise ValueError('Checkpoint evidence changed during admission')
    return provenance,embedded,guard


def admit_universe_unit_checkpoint(config,source_root,output,*,evidence,expected_evidence_sha256):
    """Admit complete unit files after a receipt-authenticated persistence OOM.

    Evidence descriptor contract ifdata-unit-checkpoint-evidence-v1 has exactly
    config/caller/preflight/terminal entries {path: absolute path, sha256: raw pin}.
    The descriptor itself requires an external raw pin. No source file is written.
    """
    from datetime import datetime,timezone
    source,output=_checkpoint_paths(source_root,output)
    producer=_operation_producer(config,'admit_universe_unit_checkpoint',expected_evidence_sha256)
    config,periods,datasets,dependencies,pin,profile,poproot,pop,inputs,accepted,catalogue=_prepare_inputs(config)
    provenance,embedded,evidence_guard=_checkpoint_evidence(config,source,evidence,expected_evidence_sha256,inputs)
    # Failed derived prefixes may exist but are never consumed or admitted.
    allowed={t+'.'+e for t in FINAL_TABLES for e in ('json','csv','parquet')}
    original_names={p.name for p in source.iterdir()} if source.is_dir() else set()
    if not source.is_dir() or any(p.name not in allowed or not _ordinary(p).is_file() for p in source.iterdir()):
        raise ValueError('Unmanifested failed root inventory mismatch')
    capture=datetime.now(timezone.utc).isoformat()
    inventory=_unit_inventory(source)
    files=[{k:v for k,v in e.items() if k!='bytes'} for e in inventory]
    counts={t:next(e['rows'] for e in files if e['file']==t+'.json') for t in TABLES}
    candidate=_unit_manifest(config,files,counts)
    _verify_contents(source,candidate)
    _guard_units(source,None,inventory);evidence_guard()
    _link_units(source,output,inventory)
    candidate['calculation_producer']=provenance
    candidate['unit_checkpoint']=dict(contract=CONTRACT,stage='unit-calculations',source_root=str(source),
        logical_payload_sha256=logical_payload_sha256(candidate),inventory=inventory,capture_utc=capture,
        capture_timing='captured_at_checkpoint_admission',file_hashes_captured_later=True,evidence=embedded,
        limitation='No failure-time unit hashes exist; integrity is established for this admission interval only')
    def guard():
        evidence_guard();_guard_units(source,output,inventory)
        if {p.name for p in source.iterdir()}!=original_names or any(not _ordinary(p).is_file() for p in source.iterdir()):
            raise ValueError('Original failed root inventory changed during admission')
        if {p.name for p in output.iterdir()}!={e['file'] for e in inventory}:raise ValueError('Checkpoint output inventory changed')
    return _accept_checkpoint(output,candidate,producer,guard)


COMPOSITION_CONTRACT='ifdata-composed-analysis-v1'
COMPOSITION_TABLES=('unit_periods','unit_coverage','company_coverage','representation_stocks',
                    'aggregates','distributions','segment_coverage','cohort_comparisons','joint_cells')
COMPOSITION_AXES=SELECTIVE_AXES+('SrAnalitico',)


def _composition_scope_allows(scope,row):
    """Match explicit singular selective and plural additive source scopes."""
    for singular,plural in (('period','periods'),('dataset','datasets'),('metric','metrics'),('code','codes')):
        values=[scope[singular]] if singular in scope else scope.get(plural)
        if values is not None and row.get(singular) not in values:return False
    horizons=scope.get('horizons')
    if 'horizon' in scope and row.get('horizon')!=scope['horizon']:return False
    if isinstance(horizons,dict) and row.get('horizon') not in horizons.get(row.get('metric'),[]):return False
    if isinstance(horizons,list) and row.get('horizon') not in horizons:return False
    return True


def _composition_result_signature(row):
    return canonical({k:row.get(k) for k in ('status','applicability','applicability_evidence','value_fraction',
        'numerator_fraction','denominator_fraction','limits','annual_summary')})


def _composition_stock_summary(rows,role,dataset,*,stock_cache=None,eligible_cache=None):
    native=[r for r in rows if r.get('unit_id')]
    def amount(r):
        return stock_cache[r['unit_id']][role] if stock_cache is not None else math._rational(r['representation_stocks'][role]['fraction'])
    def eligible(r):return eligible_cache[r['unit_id']] if eligible_cache is not None else _eligible(r)
    known=[r for r in native if r['representation_stocks'][role]['fraction'] is not None]
    unknown=[r['unit_id'] for r in native if r['representation_stocks'][role]['fraction'] is None]
    total=sum((amount(r) for r in known),Fraction())
    selected=sum((amount(r) for r in known if eligible(r)),Fraction())
    missing_companies=sorted({c for r in rows if not r.get('unit_id') or r['representation_stocks'][role]['fraction'] is None for c in r['companies']})
    share=selected/total if total else None;f=math._fraction_field
    return dict(reference='contemporaneous_own_'+dataset+'_'+role,status='own_stocks_unavailable' if dataset=='capital' else 'partial_known_stocks' if unknown or missing_companies else 'known_stocks',
        known_stock_fraction=f(total),eligible_known_stock_fraction=f(selected),share_of_known_fraction=f(share) if share is not None else None,
        share_of_total_fraction=f(share) if share is not None and not unknown and not missing_companies else None,
        known_units=[r['unit_id'] for r in known],unknown_units=unknown,unknown_companies=missing_companies,
        known_unit_count=len(known),unknown_unit_count=len(unknown),eligible_known_unit_count=sum(eligible(r) for r in known),
        negative_known_unit_count=sum(amount(r)<0 for r in known),
        flags=['negative_stock_weights'] if any(amount(r)<0 for r in known) else [])


JOINT_DIMENSIONS=('Tcb','SegmentoTb','Tc','Td','Sr','SrAnalitico')


def _composition_joint_cells(rows,*,stock_cache=None,eligible_cache=None):
    """Observed six-dimensional disjoint cells; never a Cartesian product.

    Each native contribution appears once. Missing admitted companies occupy
    their observed missing category and never acquire a reporting unit/value.
    All eligible fractions survive for exact Type2 quantiles after AND filters.
    """
    rows=list(rows);groups={};parsed={};seen=set()
    for row in rows:
        if row['membership'] not in COHORTS[1:]:raise ValueError('Invalid joint-cell cohort')
        context=tuple(row[k] for k in ('period','dataset','metric','horizon'))
        if row.get('unit_id'):
            identity=context+(canonical(row['unit_key']),)
            if identity in seen:raise ValueError('Duplicate joint-cell native contributor')
            seen.add(identity)
            if row['unit_key']!=[row['dataset'],TYPES[row['dataset']],row['code']]:raise ValueError('Joint-cell native identity mismatch')
        elif row.get('unit_key') is not None or row.get('value_fraction') is not None or row.get('asset_fraction') is not None:
            raise ValueError('Nominal joint-cell row cannot contribute a native value')
        parsed[id(row)]=_summary_values(row)
        dimensions={field:dict(zip(('state','value'),_category(row,field))) for field in JOINT_DIMENSIONS}
        key=context+(row['membership'],canonical(dimensions))
        groups.setdefault(key,[]).append(row)
    output=[]
    for key,subset in sorted(groups.items()):
        if not any(r.get('unit_id') or r.get('companies') for r in subset):continue
        context=dict(zip(('period','dataset','metric','horizon','cohort'),key[:5]));dimensions=json.loads(key[5])
        context['id']='|'.join(key[:5])+'|joint|'+hashlib.sha256(key[5].encode()).hexdigest()[:24]
        summary,distribution=_unit_summary(subset,context,parsed)
        summary.update(dimensions=dimensions,distribution=distribution,
            distribution_sorted_fractions=[[str(parsed[id(r)]['value'].numerator),str(parsed[id(r)]['value'].denominator)]
                for r in sorted((r for r in subset if parsed[id(r)]['eligible']),key=lambda r:parsed[id(r)]['value'])],
            source_counts=dict(rows=len(subset),native_units=sum(bool(r.get('unit_id')) for r in subset),
                eligible_units=sum(parsed[id(r)]['eligible'] for r in subset),nominal_companies=len({c for r in subset if not r.get('unit_id') for c in r['companies']})),
            partition_scope='one_observed_cell_per_native_contribution_and_admitted_missing_company')
        summary['representation_coverage']={role:_composition_stock_summary(subset,role,context['dataset'],stock_cache=stock_cache,eligible_cache=eligible_cache) for role in ('credit','PL')}
        at_known=[r for r in subset if r.get('unit_id') and r.get('asset_fraction') is not None]
        summary['asset_coverage'].update(known_unit_count=len(at_known),unknown_unit_count=sum(bool(r.get('unit_id')) and r.get('asset_fraction') is None for r in subset),
            eligible_known_unit_count=sum(parsed[id(r)]['eligible'] for r in at_known),negative_known_unit_count=sum(parsed[id(r)]['asset']<0 for r in at_known))
        output.append(_composition_compact_summary(summary))
    if sum(c['source_counts']['native_units'] for c in output)!=len(seen):raise ValueError('Joint-cell native partition mismatch')
    return output


def _composition_compact_summary(row,limit=8):
    """Keep exact counts and all nominal companies; unit identities live in coverage."""
    result=deepcopy(row);counts={}
    def visit(value,path=''):
        if not isinstance(value,dict):return
        for key,item in value.items():
            name=path+'.'+key if path else key
            if isinstance(item,list) and (key.endswith('_units') or key=='eligible_intersection'):
                counts[name]=len(item);value[key]=item[:limit]
            elif isinstance(item,dict):visit(item,name)
    visit(result)
    if 'missing_reasons' in result:
        result['missing_reason_counts']={k:len(v) for k,v in result['missing_reasons'].items()}
        result['missing_reasons']={k:v[:limit] for k,v in result['missing_reasons'].items()}
    result.update(unit_lists_complete=False,unit_lists_limit=limit,unit_list_counts=counts)
    return result


def compose_analysis(config,output):
    """Compose pinned stored contributions, never recalculate legacy formulae.

    Config requires baseline, membership and sr descriptors {root,
    expected_manifest_sha256}, corrections/complements lists of those descriptors
    plus their exact manifest scope, periods, datasets and complement_metrics.
    Output selection may be a reviewed slice; every selected native contribution
    and every declared complement must be complete. Full core runs explicitly
    select sixty periods. Only consumed Parquet files are authenticated.
    """
    import duckdb
    from time import perf_counter
    started=perf_counter();required={'baseline','membership','sr','corrections','complements','periods','datasets','complement_metrics','analytical_company_scope'}
    if not isinstance(config,dict) or set(config)!=required:raise ValueError('Explicit composition config required')
    config=deepcopy(config);periods=config['periods'];datasets=config['datasets'];new_metrics=config['complement_metrics']
    if config['analytical_company_scope']!='admitted_associations_2024':raise ValueError('Explicit admitted_associations_2024 analytical scope required')
    if (not isinstance(periods,list) or not periods or len(set(periods))!=len(periods)
        or any(not isinstance(p,str) or math._period_date(p) is None or not '201003'<=p<='202412' for p in periods)):
        raise ValueError('Invalid composition periods')
    if not isinstance(datasets,list) or not datasets or len(set(datasets))!=len(datasets) or any(d not in TYPES for d in datasets):raise ValueError('Invalid composition datasets')
    if not isinstance(new_metrics,list) or not new_metrics or len(set(new_metrics))!=len(new_metrics) or any(m not in math.COMPLEMENT_METRICS for m in new_metrics):raise ValueError('Invalid composition complement metrics')
    if not isinstance(config['corrections'],list) or not isinstance(config['complements'],list) or not config['complements']:raise ValueError('Explicit nonempty complement inputs required')
    output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    sources=[];guards={};consumed={}
    def identity(path):
        s=_ordinary(path).stat();return s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns
    def authenticate(spec,contracts):
        if set(spec)-{'root','expected_manifest_sha256','scope'} or not {'root','expected_manifest_sha256'}<=set(spec):raise ValueError('Explicit source pin required')
        pin=spec['expected_manifest_sha256'];root=Path(spec['root']).resolve();path=root/'manifest.json'
        if output==root or root in output.parents or output in root.parents:raise ValueError('Composition output overlaps source')
        if not isinstance(pin,str) or not re.fullmatch('[a-f0-9]{64}',pin) or math._digest_file(path)!=pin:raise ValueError('Composition source manifest pin mismatch')
        manifest=math._json_unique(path.read_bytes())
        if manifest.get('contract') not in contracts:raise ValueError('Composition input contract mismatch')
        entries={}
        for e in manifest.get('files',[]):
            if e['file'] in entries:raise ValueError('Duplicate composition input inventory')
            entries[e['file']]=e
        guards[path]=identity(path);consumed[path]=pin
        result=dict(root=root,manifest=manifest,entries=entries,pin=pin,spec=spec);sources.append(result)
        return result
    base=authenticate(config['baseline'],{CONTRACT})
    if base['manifest'].get('stage')!='coverage-and-aggregation' or not set(periods)<=set(base['manifest'].get('periods',[])):
        raise ValueError('Composition requires admitted baseline periods')
    basepin=base['pin'];membership=authenticate(config['membership'],{'ifdata-updated-membership-v1'})
    sr=authenticate(config['sr'],{'ifdata-sr-attribution-v1'})
    if membership['manifest'].get('baseline_manifest_sha256')!=basepin or sr['manifest'].get('baseline',{}).get('sha256')!=basepin:
        raise ValueError('Membership/Sr baseline lineage mismatch')
    if membership['manifest'].get('known_nominal_companies')!=55 or not set(periods)<=set(membership['manifest'].get('periods',[])):
        raise ValueError('Complete admitted55 membership required')
    overlays=[]
    for kind in ('corrections','complements'):
        for spec in config[kind]:
            source=authenticate(spec,{'ifdata-selective-analysis-v1','ifdata-caixa-transition-analysis-v1'} if kind=='corrections' else {'ifdata-complement-analysis-v1'})
            if source['manifest'].get('baseline',{}).get('expected_manifest_sha256')!=basepin or source['manifest'].get('scope')!=spec.get('scope'):
                raise ValueError('Overlay scope or baseline lineage mismatch')
            source.update(kind=kind,scope=spec['scope']);overlays.append(source)
    def consume(source,name):
        if name not in source['entries']:raise ValueError('Missing consumed composition input: '+name)
        entry=source['entries'][name];path=math._contained(source['root'],name)
        _capture_payload(source['root'],entry);guards[path]=identity(path);consumed[path]=entry['sha256']
        return path
    def origin(source,row,kind):
        return dict(kind=kind,root=str(source['root']),expected_manifest_sha256=source['pin'],table='unit_coverage',result_id=row.get('result_id'),coverage_id=row['id'])
    def rowkey(row):return tuple(row.get(k) for k in ('dataset','code','period','metric','horizon'))
    immutable_count=patched_count=nominal_analytical_count=0;joint_totals=dict(rows=0,native_units=0,eligible_units=0,nominal_companies=0);output.mkdir(parents=True)
    with ExitStack() as stack,duckdb.connect(config={'threads':1,'memory_limit':'512MiB','temp_directory':str(output/'.duckdb-temp')}) as conn:
        for source,names,prefix in [(base,('unit_periods','unit_coverage','components'),'base'),(membership,('companies','company_quarter_map','unit_membership'),'member'),(sr,('attributes',),'sr')]:
            for name in names:
                path=consume(source,name+'.parquet');conn.from_parquet(str(path)).create_view(prefix+'_'+name)
        for i,source in enumerate(overlays):
            source['view']='overlay_'+str(i);conn.from_parquet(str(consume(source,'unit_coverage.parquet'))).create_view(source['view'])
        def rows(view,where='',params=()):
            return [math._json_unique(row[0].encode('utf-8')) for row in conn.execute('select payload from '+view+(' where '+where if where else ''),params).fetchall()]
        companies=rows('member_companies');ids=[r['company_cnpj14'] for r in companies]
        if len(ids)!=55 or len(set(ids))!=55:raise ValueError('Membership nominal55 identity mismatch')
        company_by_id={c['company_cnpj14']:c for c in companies}
        analytical_ids={c['company_cnpj14'] for c in companies if c.get('principal_state')=='admitted_association'}
        if len(analytical_ids)!=32 or sum(c.get('principal_state')=='no_admitted_principal' for c in companies)!=23:
            raise ValueError('Analytical scope requires32 admitted/23 no principal registry identities')
        writers={t:Writer(output,t,stack,formats=('parquet',)) for t in COMPOSITION_TABLES}
        # Count and scope checks cover every overlay row, even those outside the
        # selected review slice. No undeclared correction can hide in a file.
        overlay_counts={}
        for source in overlays:
            view=source['view'];count=0
            if conn.execute('select count(*) from (select dataset,code,period,metric,horizon,count(*) as n from '+view+' group by all having n>1)').fetchone()[0]:
                raise ValueError('Duplicate overlay native contribution')
            cursor=conn.execute('select payload from '+view)
            while batch:=cursor.fetchmany(4096):
                for item in batch:
                    r=math._json_unique(item[0].encode('utf-8'));key=rowkey(r);count+=1
                    if not r.get('unit_id') or not _composition_scope_allows(source['scope'],r):raise ValueError('Overlay row outside scope')
            expected=source['manifest'].get('tables',{}).get('unit_coverage')
            if count!=expected:raise ValueError('Overlay consumed row count mismatch')
            overlay_counts[view]=count
        for period in sorted(periods):
            maps=rows('member_company_quarter_map',"json_extract_string(payload,'$.period')=?",[period])
            if len(maps)!=55 or {r['company_cnpj14'] for r in maps}!=set(ids):raise ValueError('Company quarter map incomplete or duplicate')
            for dataset in datasets:
                where="json_extract_string(payload,'$.period')=? and json_extract_string(payload,'$.dataset')=?"
                units=rows('base_unit_periods',where,[period,dataset]);updated=rows('member_unit_membership',where,[period,dataset]);attributes=rows('sr_attributes',where,[period,dataset])
                def keyed(items,key):
                    result={}
                    for r in items:
                        k=r[key]
                        if k in result:raise ValueError('Duplicate composition '+key)
                        result[k]=r
                    return result
                native=keyed(units,'unit_id');members=keyed(updated,'unit_id');attrs=keyed(attributes,'unit_id')
                if set(native)!=set(members) or set(native)!=set(attrs):raise ValueError('Membership/Sr native population mismatch')
                by_code={};stock_by_code={};stock_cache={}
                if len({r['code'] for r in units})!=len(units):raise ValueError('Duplicate native code within composition window')
                selected_stocks=rows('base_components',"period=? and dataset=? and json_extract_string(payload,'$.analysis_period')=? and json_extract_string(payload,'$.component') in ('AT','credit','PL')",[period,dataset,period]) if dataset!='capital' else []
                obs={}
                for ob in selected_stocks:
                    key=(ob['code'],ob['component'])
                    if key in obs:raise ValueError('Ambiguous contemporaneous representation stock')
                    if ob.get('unit_key')!=[dataset,TYPES[dataset],ob['code']] or ob.get('analysis_period')!=period or ob.get('period')!=period:raise ValueError('Representation stock identity mismatch')
                    obs[key]=ob
                for uid,unit in native.items():
                    updated=members[uid];attribute=attrs[uid];code=unit['code']
                    if uid!='|'.join((dataset,TYPES[dataset],code,period)):raise ValueError('Native unit identity mismatch')
                    signature=lambda r:canonical({k:r.get(k) for k in ('unit_id','dataset','code','period','classifications','own_cadastro')})
                    if signature(unit)!=signature(updated):raise ValueError('Membership changed original native attributes')
                    cad=unit.get('classifications');original=(cad or {}).get('Sr')
                    if any(attribute.get(k)!=unit.get(k) for k in ('unit_id','dataset','code','period')) or attribute.get('sr_original')!=original:
                        raise ValueError('Sr original or native identity mismatch')
                    if 'native_cadastro' in attribute and attribute['native_cadastro']!=unit.get('own_cadastro'):raise ValueError('Sr dated cadastro mismatch')
                    if original not in (None,'') and attribute.get('sr_analitico')!=original:raise ValueError('Sr analytical override of observed original')
                    if not set(updated['companies'])<=set(ids) or updated['membership'] not in COHORTS[1:]:raise ValueError('Unrecognized nominal membership')
                    item=deepcopy(updated);item['sr_attribute']=dict(root=str(sr['root']),expected_manifest_sha256=sr['pin'],attribute_id=uid,
                        sr_original=attribute['sr_original'],sr_analitico=attribute.get('sr_analitico'),status=attribute['status'],method=attribute.get('method'))
                    item['sr_analytic_status']=attribute['status']
                    if cad is not None or attribute['status'] in ('derived','conflict'):item['classifications']=dict(cad or {},SrAnalitico=attribute.get('sr_analitico'))
                    writers['unit_periods'].append(item);by_code[code]=(unit,updated,attribute)
                    values={};stock_cache[uid]={}
                    for role in ('AT','credit','PL'):
                        ob=obs.get((code,role));value,status=math._native_value(ob) if ob else (None,'component_missing')
                        if ob and ob.get('scale')!='BRL':value,status=None,'invalid_scale'
                        elif ob and ob.get('window_rule')!='stock':value,status=None,'incompatible_window'
                        elif ob and (not (ob.get('binding_ref') or ob.get('binding')) or not ob.get('sources')):value,status=None,'unverified_stock_source'
                        if dataset=='capital':value,status=None,'own_stocks_unavailable'
                        elif not unit.get('own_cadastro') or unit['own_cadastro'].get('Data')!=period or unit['own_cadastro'].get('CodInst')!=code:
                            value,status=None,'missing_dated_cadastro'
                        stock_cache[uid][role]=value
                        values[role]=dict(fraction=math._fraction_field(value) if value is not None else None,status=status or 'ok',component_ref=ob.get('id') if ob else None)
                    stock_by_code[code]=values
                    writers['representation_stocks'].append(dict(id=uid+'|representation',unit_id=uid,unit_key=[dataset,TYPES[dataset],code],dataset=dataset,code=code,period=period,
                        membership=updated['membership'],companies=updated['companies'],stocks=values,origin=dict(root=str(base['root']),expected_manifest_sha256=basepin,table='components')))
                metrics=[m for m in math.METRICS if (m in ('C3','C4'))==(dataset=='capital')]+(new_metrics if dataset!='capital' else [])
                for metric in metrics:
                    for horizon in (('quarter','ttm') if metric in math.FLOW_METRICS|math.COMPLEMENT_FLOW_METRICS else ('point',)):
                        params=[period,dataset,metric,horizon];pred='period=? and dataset=? and metric=? and horizon=?'
                        originals=rows('base_unit_coverage',pred,params) if metric in math.METRICS else []
                        original_by_code={}
                        for r in originals:
                            if not r.get('unit_id'):continue
                            if any(r[k]!=v for k,v in zip(('period','dataset','metric','horizon'),params)):raise ValueError('Baseline typed columns/payload mismatch')
                            if r['code'] in original_by_code:raise ValueError('Duplicate baseline native contribution')
                            original_by_code[r['code']]=r
                        expected_codes=set(by_code)
                        if metric in math.METRICS and set(original_by_code)!=expected_codes:raise ValueError('Incomplete baseline native metric coverage')
                        chosen={code:(r,base,'baseline') for code,r in original_by_code.items()};replaced=set()
                        for source in overlays:
                            # A singular code scope is checked on each row, so a
                            # context match must ignore only that code selector.
                            context_scope={k:v for k,v in source['scope'].items() if k not in ('code','codes')}
                            if not _composition_scope_allows(context_scope,dict(period=period,dataset=dataset,metric=metric,horizon=horizon)):continue
                            patch_rows=rows(source['view'],pred,params);patch_codes=set()
                            for r in patch_rows:
                                if any(r[k]!=v for k,v in zip(('period','dataset','metric','horizon'),params)):raise ValueError('Overlay typed columns/payload mismatch')
                                code=r['code']
                                if code not in by_code or code in patch_codes or code in replaced:raise ValueError('Overlay collision or unknown native unit')
                                patch_codes.add(code);replaced.add(code)
                                if source['kind']=='corrections' and (metric not in math.METRICS or code not in original_by_code):raise ValueError('Correction cannot introduce a metric/unit')
                                if source['kind']=='complements' and metric not in new_metrics:raise ValueError('Complement may not replace legacy metric')
                                chosen[code]=(r,source,source['kind'])
                            scope_codes=set(source['scope'].get('codes',[source['scope']['code']] if 'code' in source['scope'] else expected_codes))&expected_codes
                            if patch_codes!=scope_codes:raise ValueError('Incomplete declared overlay metric coverage')
                        if set(chosen)!=expected_codes:raise ValueError('Missing complete complement/native contribution')
                        projected=[]
                        for code,(original,source,kind) in chosen.items():
                            unit,updated,attribute=by_code[code];row=deepcopy(original);uid=unit['unit_id']
                            if row.get('unit_id')!=uid or row.get('unit_key')!=[dataset,TYPES[dataset],code]:raise ValueError('Contribution identity mismatch')
                            expected_cad=dict(Data=period,**unit['classifications']) if unit.get('classifications') is not None else None
                            if row.get('target_cadastro')!=expected_cad:raise ValueError('Contribution original cadastro mismatch')
                            if 'result_id' not in row:
                                expected_result_id=uid+'|'+metric+'|'+horizon
                                if source['manifest']['contract']!='ifdata-selective-analysis-v1' or row.get('id')!=expected_result_id:
                                    raise ValueError('Missing result reference outside exact legacy selective coverage identity')
                                row.update(result_id=expected_result_id,row_kind='native_unit')
                            if not isinstance(row['result_id'],str) or not row['result_id']:
                                raise ValueError('Invalid stored result reference')
                            signature=_composition_result_signature(row)
                            row.update(membership=updated['membership'],companies=updated['companies'],membership_reason=updated.get('membership_reason'),origin=origin(source,row,kind),representation_stocks=stock_by_code[code])
                            if row['target_cadastro'] is None and attribute['status'] in ('derived','conflict'):
                                states=row.setdefault('classification_states',{})
                                for field in SELECTIVE_AXES:states[field]='missing_dated_cadastro'
                            if attribute['status'] in ('before_regime','unknown'):
                                row.setdefault('classification_states',{})['SrAnalitico']=attribute['status']
                            if row['target_cadastro'] is not None or attribute['status'] in ('derived','conflict'):
                                row['target_cadastro']=dict(row['target_cadastro'] or {},Data=period,SrAnalitico=attribute.get('sr_analitico'))
                            if attribute['status']=='conflict':
                                row.setdefault('classification_states',{})['SrAnalitico']='conflict';row['flags']=sorted(set(row.get('flags',[])+['sr_link_conflict']))
                            if attribute['status']=='derived':row['flags']=sorted(set(row.get('flags',[])+['sr_from_dated_link']))
                            row['sr_provenance']=dict(root=str(sr['root']),expected_manifest_sha256=sr['pin'],attribute_id=uid,method=attribute.get('method'),status=attribute['status'])
                            stock=stock_by_code[code]['AT'];row.update(asset_fraction=stock['fraction'],asset_status=stock['status'])
                            if _composition_result_signature(row)!=signature:raise ValueError('Composition changed stored economic result')
                            if kind=='baseline':immutable_count+=1
                            elif kind=='corrections':patched_count+=1
                            row['preservation']=dict(status='exact_stored_economic_fields',signature_sha256=hashlib.sha256(signature.encode()).hexdigest())
                            projected.append(row);writers['unit_coverage'].append(row)
                        for cid in ids:
                            linked=[r for r in projected if cid in r['companies']]
                            status='ok' if any(r['status']=='ok' for r in linked) else 'missing_native_unit' if not linked else 'native_results_unavailable'
                            companyrow=dict(id='|'.join((period,dataset,metric,horizon,cid)),period=period,dataset=dataset,metric=metric,horizon=horizon,
                                company_cnpj14=cid,company=company_by_id[cid],analytical_included=cid in analytical_ids,status=status,unit_ids=sorted(r['unit_id'] for r in linked),
                                result_refs=[dict(unit_id=r['unit_id'],result_id=r['result_id'],status=r['status'],origin=r['origin']) for r in linked],
                                relation=next(m for m in maps if m['company_cnpj14']==cid),method='nominal_links_not_additive_company_financial_values')
                            writers['company_coverage'].append(companyrow)
                            if not linked and cid in analytical_ids:
                                nominal_analytical_count+=1
                                projected.append(dict(id=companyrow['id']+'|nominal',row_kind='nominal_company',unit_id=None,unit_key=None,result_id=None,
                                period=period,dataset=dataset,metric=metric,horizon=horizon,code=None,membership='sample',companies=[cid],status='missing_native_unit',
                                applicability='unknown',value_fraction=None,numerator_fraction=None,denominator_fraction=None,asset_fraction=None,asset_status='no_native_unit',
                                target_cadastro=None,flags=[],limits=['nominal_company_without_admitted_native_reporting_unit']))
                        analytical_rows=[]
                        for row in projected:
                            analytical=deepcopy(row);analytical['companies']=[c for c in row['companies'] if c in analytical_ids]
                            if analytical.get('unit_id') and analytical['membership']=='sample' and not analytical['companies']:
                                raise ValueError('Sample unit has no admitted analytical company link')
                            analytical_rows.append(analytical)
                        projected=analytical_rows
                        eligible_cache={r['unit_id']:_eligible(r) for r in projected if r.get('unit_id')}
                        derived=aggregate_unit_results(projected,fields=COMPOSITION_AXES)
                        for cell in _composition_joint_cells(projected,stock_cache=stock_cache,eligible_cache=eligible_cache):
                            for key in joint_totals:joint_totals[key]+=cell['source_counts'][key]
                            writers['joint_cells'].append(cell)
                        for table,values in derived.items():
                            for value in values:
                                if table in ('aggregates','segment_coverage'):
                                    subset=[r for r in projected if value['cohort']=='total' or r['membership']==value['cohort']]
                                    if value.get('field') is not None:subset=[r for r in subset if _category(r,value['field'])==(value['category_state'],value['category'])]
                                    value['representation_coverage']={role:_composition_stock_summary(subset,role,dataset,stock_cache=stock_cache,eligible_cache=eligible_cache) for role in ('credit','PL')}
                                writers[table].append(_composition_compact_summary(value))
        files=[]
        for writer in writers.values():files.extend(writer.finish(conn))
        tables={t:w.count for t,w in writers.items()}
        if joint_totals['native_units']!=tables['unit_coverage'] or joint_totals['nominal_companies']!=nominal_analytical_count:
            raise ValueError('Joint-cell full native/nominal partition reconciliation failed')
    temp=output/'.duckdb-temp'
    if temp.exists():
        # DuckDB owns its spill files; no recursive filesystem deletion.
        for child in temp.iterdir():
            if child.is_file():child.unlink()
        temp.rmdir()
    for path,pin in consumed.items():
        if identity(path)!=guards[path] or math._digest_file(path)!=pin:raise ValueError('Consumed composition input changed')
    manifest=dict(contract=COMPOSITION_CONTRACT,config=config,periods=sorted(periods),datasets=datasets,segmentation_fields=list(COMPOSITION_AXES),joint_cell_dimensions=list(JOINT_DIMENSIONS),registry_company_count=55,analytical_company_count=32,tables=tables,files=files,
        joint_partition_checks=dict(status='exact',native_contributions=tables['unit_coverage'],nominal_admitted_missing_companies=nominal_analytical_count,joint_source_counts=joint_totals,identity='Each native contribution and missing admitted company occurs in exactly one observed cohort/dimension cell'),
        monetary_scale_info=dict(currency='BRL',native_scale='1',source_note='docs/engineering/ifdata-indicator-pilot-20261011.md:14',rule='Official Olinda Saldo in R$; no portal thousands factor'),
        consumed_files=[dict(file=str(p),sha256=h) for p,h in sorted(consumed.items(),key=lambda x:str(x[0]))],
        preservation=dict(unchanged_legacy_contributions=immutable_count,corrected_legacy_contributions=patched_count,status='exact_stored_economic_fields',legacy_formula_evaluations=0),
        producer_sha256=math._digest_file(Path(__file__)),elapsed_seconds=perf_counter()-started,
        limits=['Observed native perimeters; no economic exposure elimination','Membership relative to admitted known associations; nominal gaps retained','Descriptive statistics only; no causal inference or composite index'])
    (output/'manifest.json').write_text(canonical(manifest)+'\n',encoding='utf-8')
    return manifest


def _terra_require_admitted_company_coverage(rows):
    if any(r.get('analytical_included') is True and r.get('status')=='missing_native_unit' for r in rows):
        raise ValueError('Terra context has nominal company gaps')


def _terra_applied_contribution(patch,root,pin):
    row=deepcopy(patch);row['prior_origin']=deepcopy(patch['origin'])
    row['origin']=dict(kind='corrections',root=str(root),expected_manifest_sha256=pin,coverage_id=patch['id'])
    row['preservation']=dict(status='exact_stored_economic_fields',signature_sha256=hashlib.sha256(_composition_result_signature(row).encode()).hexdigest())
    return row


def _terra_copy_context(conn,base,replacement,destination,*,unit_only=False):
    predicate="dataset='financial' and period='202412' and metric in (select unnest($metrics)) and horizon in ('quarter','ttm')"
    if unit_only:predicate="code='03751794' and "+predicate
    conn.execute('copy (select * from read_parquet($base) where not ('+predicate+') union all select * from read_parquet($replacement)) to $destination (format parquet,compression zstd,row_group_size 2048)',
        dict(base=str(base),replacement=str(replacement),destination=str(destination),metrics=list(TERRA_HISTORY_METRICS)))


def apply_terra_history(composition,composition_pin,patch,patch_pin,output):
    """Replace sixteen stored contributions; reduce only their existing contexts.

    No indicator formula is evaluated. Unaffected payload strings survive exactly;
    the three structural tables are copied byte-for-byte. Original contributions
    remain in the pinned patch, and the accepted composition remains untouched.
    """
    import duckdb
    import shutil
    from time import perf_counter
    started=perf_counter();output=Path(output).resolve();consumed={}
    if output.exists():raise FileExistsError(output)
    def protect(path):
        path=Path(path).resolve()
        if output==path or path in output.parents or output in path.parents:raise ValueError('Terra output overlaps source')
        return path
    def guard(value):
        if isinstance(value,dict):
            if isinstance(value.get('root'),str):protect(value['root'])
            for nested in value.values():guard(nested)
        elif isinstance(value,list):
            for nested in value:guard(nested)
    def package(root,pin,contract):
        root=protect(root);path=root/'manifest.json'
        if math._digest_file(path)!=pin:raise ValueError('Terra application manifest pin mismatch')
        value=math._json_unique(path.read_bytes())
        if value.get('contract')!=contract:raise ValueError('Terra application contract mismatch')
        consumed[path]=pin;guard(value);return root,value
    root,full=package(composition,composition_pin,COMPOSITION_CONTRACT)
    pr,pm=package(patch,patch_pin,'ifdata-terra-history-analysis-v1')
    if pm['composition']!=dict(root=str(root),expected_manifest_sha256=composition_pin):raise ValueError('Terra patch composition mismatch')
    expected={(m,h) for m in TERRA_HISTORY_METRICS for h in ('quarter','ttm')}
    def table(root,manifest,name):
        entries=[e for e in manifest['files'] if e['file']==name+'.parquet']
        if len(entries)!=1:raise ValueError('Terra table inventory mismatch')
        entry=entries[0];_capture_payload(root,entry);path=root/entry['file'];consumed[path]=entry['sha256'];return path
    with duckdb.connect(config={'threads':1,'memory_limit':'512MiB'}) as conn:
        def rows(path,where='',params=None):
            return [math._json_unique(p.encode()) for p, in conn.execute('select payload from read_parquet(?) '+where,[str(path)]+(params or [])).fetchall()]
        patches=rows(table(pr,pm,'unit_coverage'));originals=rows(table(pr,pm,'original_unit_coverage'))
        def valid(items):
            return len(items)==16 and {(r['metric'],r['horizon']) for r in items}==expected and all(r['dataset']=='financial' and r['period']=='202412' and r['code']=='03751794' and r['membership']=='remaining' and not r['companies'] for r in items)
        if not valid(patches) or not valid(originals):raise ValueError('Exact sixteen remaining Terra contributions required')
        old_by_id={r['id']:r for r in originals};patch_by_id={r['id']:r for r in patches}
        if len(old_by_id)!=16 or old_by_id.keys()!=patch_by_id.keys():raise ValueError('Terra patch identity mismatch')
        mutable={'status','applicability','applicability_evidence','value_fraction','numerator_fraction','denominator_fraction','flags','limits','annual_summary','result_id','reporting_transition','prior_origin'}
        for key,row in patch_by_id.items():
            if {k:v for k,v in row.items() if k not in mutable}!={k:v for k,v in old_by_id[key].items() if k not in mutable}:raise ValueError('Terra patch changed structural fields')
            if row.get('reporting_transition',{}).get('rule')!=TERRA_HISTORY_ID:raise ValueError('Terra proof missing')
        patches=[_terra_applied_contribution(r,pr,patch_pin) for r in patches]
        patch_by_id={r['id']:r for r in patches}
        paths={name:table(root,full,name) for name in COMPOSITION_TABLES}
        context="where dataset='financial' and period='202412' and metric in ("+','.join('?' for _ in TERRA_HISTORY_METRICS)+") and horizon in ('quarter','ttm')"
        context_rows=rows(paths['unit_coverage'],context,list(TERRA_HISTORY_METRICS))
        found={r['id']:r for r in context_rows if r['id'] in patch_by_id}
        if found!=old_by_id:raise ValueError('Accepted Terra originals differ from patch')
        # Finite destination has no missing admitted companies. Refuse rather
        # than silently lose nominal rows if the target cohort changes later.
        _terra_require_admitted_company_coverage(rows(paths['company_coverage'],context+" and status='missing_native_unit'",list(TERRA_HISTORY_METRICS)))
        projected=[patch_by_id.get(r['id'],r) for r in context_rows]
        derived=aggregate_unit_results(projected,fields=COMPOSITION_AXES)
        by_context={}
        for r in projected:by_context.setdefault((r['metric'],r['horizon']),[]).append(r)
        for name,values in derived.items():
            for value in values:
                if name in ('aggregates','segment_coverage'):
                    subset=[r for r in by_context[value['metric'],value['horizon']] if value['cohort']=='total' or r['membership']==value['cohort']]
                    if value.get('field') is not None:subset=[r for r in subset if _category(r,value['field'])==(value['category_state'],value['category'])]
                    value['representation_coverage']={role:_composition_stock_summary(subset,role,'financial') for role in ('credit','PL')}
            derived[name]=[_composition_compact_summary(v) for v in values]
        derived['joint_cells']=_composition_joint_cells(projected)
        derived['unit_coverage']=patches
        for path,pin in consumed.items():
            if math._digest_file(path)!=pin:raise ValueError('Terra input changed before application')
        output.mkdir(parents=True);files=[];counts={};joint_counts=None
        with ExitStack() as stack:
            for name in COMPOSITION_TABLES:
                destination=output/(name+'.parquet')
                if name not in derived:
                    shutil.copyfile(paths[name],destination);counts[name]=full['tables'][name]
                else:
                    # Writer serializes exact fractions, then DuckDB copies all
                    # untouched rows without parsing their JSON payloads.
                    writer=Writer(output,'replacement_'+name,stack,formats=('parquet',))
                    for row in derived[name]:writer.append(row)
                    entry=writer.finish(conn)[0];replacement=output/entry['file']
                    _terra_copy_context(conn,paths[name],replacement,destination,unit_only=name=='unit_coverage')
                    replacement.unlink();counts[name]=conn.execute('select count(*) from read_parquet(?)',[str(destination)]).fetchone()[0]
                files.append(dict(file=destination.name,rows=counts[name],sha256=math._digest_file(destination)))
                if name=='joint_cells':
                    sums=conn.execute("select sum(cast(json_extract_string(payload,'$.source_counts.native_units') as bigint)),sum(cast(json_extract_string(payload,'$.source_counts.nominal_companies') as bigint)),sum(cast(json_extract_string(payload,'$.source_counts.eligible_units') as bigint)) from read_parquet(?)",[str(destination)]).fetchone()
                    joint_counts=dict(native_units=sums[0],nominal_companies=sums[1],eligible_units=sums[2],rows=sums[0]+sums[1])
        if joint_counts['native_units']!=counts['unit_coverage']:raise ValueError('Terra joint partition mismatch')
        for path,pin in consumed.items():
            if math._digest_file(path)!=pin:raise ValueError('Terra input changed during application')
        manifest=deepcopy(full);manifest.update(files=files,tables=counts,
            derivation=dict(rule=TERRA_HISTORY_ID,composition=dict(root=str(root),expected_manifest_sha256=composition_pin),patch=dict(root=str(pr),expected_manifest_sha256=patch_pin),changed_contributions=16,reduced_contexts=16,formula_evaluations=0),
            consumed_files=[dict(file=str(p),sha256=h) for p,h in sorted(consumed.items(),key=lambda x:str(x[0]))],producer_sha256=math._digest_file(Path(__file__)),elapsed_seconds=perf_counter()-started)
        manifest['joint_partition_checks'].update(joint_source_counts=joint_counts,native_contributions=counts['unit_coverage'])
        manifest['preservation']=dict(status='unchanged_payloads_outside_sixteen_contributions_and_contexts',originals_retained_in_patch=True,legacy_formula_evaluations=0)
        (output/'manifest.json').write_text(canonical(manifest)+'\n',encoding='utf8')
        return manifest


def query_composition(output,expected_manifest_sha256,sql):
    """Read at most10000 rows through SELECT-only authenticated stored tables."""
    import duckdb
    import tempfile
    settings={'threads':1,'memory_limit':'512MiB','autoload_known_extensions':False,'autoinstall_known_extensions':False}
    with duckdb.connect(config=dict(settings,enable_external_access=False)) as parser:
        statements=parser.extract_statements(sql)
        if len(statements)!=1 or statements[0].type!=duckdb.StatementType.SELECT:raise ValueError('Composition query must be one SELECT')
        selected={name.lower() for name in parser.get_table_names(sql,qualified=True)}
    if not selected<=set(COMPOSITION_TABLES):raise ValueError('Composition query references unavailable table')
    root=Path(output).resolve();path=root/'manifest.json'
    if not isinstance(expected_manifest_sha256,str) or not re.fullmatch('[a-f0-9]{64}',expected_manifest_sha256) or math._digest_file(path)!=expected_manifest_sha256:
        raise ValueError('Composition manifest pin mismatch')
    manifest=math._json_unique(path.read_bytes())
    if manifest.get('contract')!=COMPOSITION_CONTRACT:raise ValueError('Composition query contract mismatch')
    entries={e['file']:e for e in manifest['files']}
    with tempfile.TemporaryDirectory(prefix='ifdata-composition-query-') as temporary,duckdb.connect(str(Path(temporary)/'query.duckdb'),config=settings) as conn:
        for table in selected:
            copy=Path(temporary)/(table+'.parquet');_capture_payload(root,entries[copy.name],copy)
            conn.execute('create table '+table+' as select * from read_parquet(?)',[str(copy)])
        conn.execute('set enable_external_access=false');cursor=conn.execute(sql);names=[c[0] for c in cursor.description];rows=cursor.fetchmany(10001)
        if len(rows)>10000:raise ValueError('Composition query row limit exceeded')
        return [dict(zip(names,r)) for r in rows]

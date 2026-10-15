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


def _category(row,field):
    if row.get('classification_states',{}).get(field)=='conflict':return ('conflict',None)
    cadre=row.get('target_cadastro')
    if not cadre or cadre.get('Data')!=row['period']:return ('missing_dated_cadastro',None)
    if field not in cadre:return ('missing_field',None)
    value=cadre[field]
    return ('null' if value is None else 'empty' if value=='' else 'value',value)


def _eligible(row):
    return bool(row.get('unit_id') and row['status']=='ok' and row['applicability']=='applicable'
                and row.get('numerator_fraction') is not None and row.get('denominator_fraction') is not None
                and math._rational(row['denominator_fraction'])!=0)


def _unit_summary(rows,context):
    """Reduce native contributions, keeping company relations nominal only."""
    units=sorted((r for r in rows if r.get('unit_id')),key=lambda r:r['unit_id'])
    eligible=[r for r in units if _eligible(r)]
    calculable=lambda r:r['status']=='ok' and r.get('value_fraction') is not None
    predicates=dict(expected=lambda r:True,eligible=_eligible,calculable=calculable,
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
    total=sum((math._rational(r['asset_fraction']) for r in known),Fraction())
    covered=sum((math._rational(r['asset_fraction']) for r in known if _eligible(r)),Fraction())
    share=covered/total if total else None
    f=math._fraction_field
    assets=dict(reference='contemporaneous_own_'+context['dataset']+'_AT',
        status='own_assets_unavailable' if context['dataset']=='capital' else 'partial_known_assets' if unknown or unknown_companies else 'known_assets',
        known_units=[r['unit_id'] for r in known],unknown_units=unknown,unknown_companies=unknown_companies,
        known_asset_fraction=f(total),eligible_known_asset_fraction=f(covered),
        share_of_known_fraction=f(share) if share is not None else None,
        share_of_total_fraction=f(share) if share is not None and not unknown and not unknown_companies else None,
        flags=['negative_asset_weights'] if any(math._rational(r['asset_fraction'])<0 for r in known) else [])
    numerator=sum((math._rational(r['numerator_fraction']) for r in eligible),Fraction())
    denominator=sum((math._rational(r['denominator_fraction']) for r in eligible),Fraction())
    flags={flag for r in eligible for flag in r.get('flags',[])}
    if any(math._rational(r['denominator_fraction'])<0 for r in eligible):flags.add('non_convex_denominator_weights')
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
    values=sorted(math._rational(r['numerator_fraction'])/math._rational(r['denominator_fraction']) for r in eligible)
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


def aggregate_unit_results(rows):
    """Exact pure reduction of native metric coverage, independently per axis.

    Native rows have unit_id/unit_key, membership, companies, own dated cadastro
    and AT, and result fractions/status/applicability. A missing company may have
    a nominal row with unit_id/unit_key=None; it never contributes a unit/value.
    Duplicate native contributors are rejected, including equal duplicates.
    """
    groups={};seen=set();seen_ids=set()
    for row in rows:
        key=tuple(row[k] for k in ('period','dataset','metric','horizon'))
        if row['membership'] not in COHORTS[1:]:raise ValueError('Invalid native membership')
        if row.get('unit_id'):
            identity=(key,canonical(row['unit_key']))
            if identity in seen or (key,row['unit_id']) in seen_ids:raise ValueError('Duplicate native contributor')
            seen.add(identity)
            seen_ids.add((key,row['unit_id']))
            if row['unit_key']!=[row['dataset'],TYPES[row['dataset']],row['code']]:raise ValueError('Native coverage identity mismatch')
            if row['status']=='ok':
                n,d,v=(math._rational(row[k]) for k in ('numerator_fraction','denominator_fraction','value_fraction'))
                if not d or n/d!=v:raise ValueError('Inconsistent native result fraction')
            if row['dataset']=='capital' and row.get('asset_fraction') is not None:raise ValueError('Capital own assets unavailable')
        elif row.get('unit_key') is not None or row.get('value_fraction') is not None or row.get('asset_fraction') is not None:
            raise ValueError('Nominal company cannot contribute native value')
        groups.setdefault(key,[]).append(row)
    output={table:[] for table in DERIVED_TABLES[1:]}
    for key,group in sorted(groups.items()):
        base=dict(zip(('period','dataset','metric','horizon'),key));base['id']='|'.join(key)
        categories=[({},group)]
        for field in AXES:
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
                a,d=_unit_summary(selected,dict(context,id=context['id']+'|'+cohort,cohort=cohort));aggregates[cohort]=a
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
        # The parallel scanner releases buffers on large escaped CSV streams;
        # the configured single thread and insertion-order preservation remain.
        conn.execute('copy (select * from read_csv($source,header=true,auto_detect=false,columns='+columns+
            ",delim=',',quote='\"',escape='\"',nullstr='',allow_quoted_nulls=false,parallel=true,max_line_size=$limit)) "+
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


def build(config,output,*,batch_size=32,stage='coverage-and-aggregation'):
    import duckdb
    from .ifdata_population import open_population,CONTRACT as POP_CONTRACT,_metadata
    from .ifdata_odata import CONTRACT as DATA_CONTRACT
    from .ifdata_cadastro import CONTRACT as CAD_CONTRACT
    from .ifdata_variable_catalog import CONTRACT as CAT_CONTRACT,query_catalog
    output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if stage not in ('unit-calculations','coverage-and-aggregation'):raise ValueError('Invalid universe stage')
    required={'periods','datasets','profile_id','profile_expected_sha256','population'}
    if not isinstance(config,dict) or not required<=set(config) or set(config)-required-{'opening'}:raise ValueError('Invalid universe config')
    if type(batch_size) is not int or batch_size<1:raise ValueError('Positive batch size required')
    config=deepcopy(config)
    producer=_producer_snapshot(config,stage,batch_size)
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
    manifest=dict(contract=CONTRACT,stage=stage,config=normalized,inputs=inputs,profile_sha256=pin,
                  periods=periods,dependency_periods=dependencies,tables=counts,table_columns=list(math.TABLE_COLUMNS),files=files,
                  reference_contract='profile-context-and-window-component-v1',
                  limitations=['Technical native sums are not a certified system total','Prudential own assets unknown; no financial proxy','Membership does not control native applicability','No constituent or issuer-control continuity inferred'])
    if stage=='coverage-and-aggregation':
        with ExitStack() as stack,duckdb.connect(config={'memory_limit':'512MiB','threads':1}) as con:
            writers={t:Writer(output,t,stack) for t in DERIVED_TABLES}
            for tables in _derived_windows(output,manifest,pop):
                for table,rows in tables.items():
                    for row in rows:writers[table].append(row)
            for table,writer in writers.items():
                manifest['files'].extend(writer.finish(con));manifest['tables'][table]=writer.count
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
    import duckdb
    root,m=math._authenticate(dict(root=str(output),expected_manifest_sha256=expected_manifest_sha256),CONTRACT,True)
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

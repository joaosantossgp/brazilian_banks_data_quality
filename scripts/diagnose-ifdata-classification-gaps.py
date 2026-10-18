"""Diagnose complete classification-gap windows from authenticated local inputs.

No indicators are evaluated and no classifications are imputed. Outputs are
CSV tables, queryable with DuckDB/Python, plus an input/output hash receipt.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter

import duckdb
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bank_quality.ifdata_cadastro import FIELDS as CADASTRO_FIELDS

FIELDS=('Tcb','Sr','SegmentoTb','Td','Tc')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def diagnose(baseline,pin,output,raw_cadastro=None):
    started=perf_counter();baseline=Path(baseline).resolve();output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if sha(baseline/'manifest.json')!=pin:raise ValueError('Baseline manifest hash mismatch')
    main=json.loads((baseline/'manifest.json').read_text(encoding='utf-8'))
    if main['contract']!='ifdata-universe-analysis-v1' or main['stage']!='coverage-and-aggregation':
        raise ValueError('Accepted universe baseline required')
    source=Path(main['inputs']['cadastro']['root']).resolve()
    for protected in (source,baseline):
        if output==protected or protected in output.parents or output in protected.parents:
            raise ValueError('Output overlaps an input')
    cadastro_pin=main['inputs']['cadastro']['expected_manifest_sha256']
    if sha(source/'manifest.json')!=cadastro_pin:raise ValueError('Cadastro manifest hash mismatch')
    cm=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    if cm['contract']!='ifdata-cadastro-parquet-v1':raise ValueError('Cadastro contract mismatch')
    parts=[e for e in cm['files'] if e['period'] in main['periods']]
    if len(parts)!=len(main['periods']) or {e['period'] for e in parts}!=set(main['periods']):
        raise ValueError('Missing or ambiguous cadastro periods')
    entries=[e for e in main['files'] if e['file']=='unit_periods.csv']
    if len(entries)!=1:raise ValueError('Ambiguous units input')
    unit_entry=entries[0];unitpath=baseline/unit_entry['file'];guards={}
    def authenticate(path,digest):
        if path.is_symlink() or not path.is_file() or sha(path)!=digest:raise ValueError('Input hash mismatch: '+str(path))
        guards[path]=(path.stat().st_size,path.stat().st_mtime_ns)
    authenticate(unitpath,unit_entry['sha256'])
    for e in parts:
        p=(source/e['file']).resolve()
        if source not in p.parents:raise ValueError('Cadastro path escapes root')
        authenticate(p,e['sha256'])
    with duckdb.connect(config={'threads':2,'memory_limit':'512MiB'}) as conn:
        conn.read_csv(str(unitpath),header=True,all_varchar=True).create_view('input_units')
        conn.execute("""create table units as select dataset,period,code,
            cast(substr(period,1,4) as integer)*4+cast(substr(period,5,2) as integer)//3 as qi,
            json_extract(payload,'$.classifications') as classifications,
            json_extract(payload,'$.classification_states') as classification_states,
            json_extract_string(payload,'$.own_cadastro.Data') as cadastro_date,
            json_extract_string(payload,'$.membership') as membership from input_units""")
        count=conn.execute('select count(*) from units').fetchone()[0]
        if count!=unit_entry['rows'] or count!=main['tables']['unit_periods']:raise ValueError('Unit count mismatch')
        if conn.execute('select count(*) from (select dataset,period,code from units group by all having count(*)<>1)').fetchone()[0]:
            raise ValueError('Duplicate reporting unit')
        conn.from_parquet([str(source/e['file']) for e in parts]).create_view('cadastro')
        if conn.execute('select count(*) from cadastro').fetchone()[0]!=sum(e['rows'] for e in parts):raise ValueError('Cadastro count mismatch')
        if conn.execute('select count(*) from (select CodInst,Data from cadastro group by all having count(*)<>1)').fetchone()[0]:
            raise ValueError('Duplicate cadastro key')
        terms=[]
        for field in FIELDS:
            terms.append(f"""select u.dataset,u.period,u.code,u.qi,'{field}' as field,
                u.membership as membership,
                json_extract_string(u.classifications,'$.NomeInstituicao') as name,
                json_extract_string(u.classifications,'$.{field}') as value,
                case when json_extract_string(u.classification_states,'$.{field}')='conflict' then 'conflict'
                     when u.cadastro_date is distinct from u.period then 'missing_dated_cadastro'
                     when not json_exists(u.classifications,'$.{field}') then 'missing_field'
                     when json_extract_string(u.classifications,'$.{field}') is null then 'null'
                     when json_extract_string(u.classifications,'$.{field}')='' then 'empty' else 'value' end as state,
                c.{field} as source_value,c.NomeInstituicao as source_name,
                case when c.CodInst is null then 'missing_dated_cadastro' when c.{field} is null then 'null'
                     when c.{field}='' then 'empty' else 'value' end as source_state,
                c.source_file,c.source_sha256,c.source_row,c.source_url
                from units u left join cadastro c on c.CodInst=u.code and c.Data=u.period""")
        conn.execute('create table compared as '+ ' union all '.join(terms))
        conn.execute("""create table audited as select *,case
            when state='conflict' then 'projection_conflict'
            when state='value' and (source_state<>'value' or value is distinct from source_value) then 'projection_value_mismatch'
            when state='value' then 'observed_equal'
            when source_state='value' then 'recoverable_observed_source'
            when state<>source_state then 'projection_state_mismatch'
            when source_state='missing_dated_cadastro' then 'native_cadastro_absent'
            when source_state='null' then 'native_null' else 'native_empty' end as cause from compared""")
        assert conn.execute('select count(*) from audited').fetchone()[0]==count*len(FIELDS)
        queries={
            'field_coverage':"select dataset,period,field,state,source_state,cause,count(*) as unit_periods from audited group by all order by field,dataset,period,state",
            'category_coverage':"select dataset,period,field,value,count(*) as reporting_units from audited where state='value' group by all order by field,dataset,value,period",
            'missing_units':"select * from audited where cause<>'observed_equal' order by field,dataset,code,period",
            'missing_windows':"""with holes as (select *,qi-row_number() over(partition by dataset,code,field,cause order by qi) as island
                from audited where cause<>'observed_equal')
                select dataset,code,field,cause,min(period) as first_period,max(period) as last_period,
                    count(*) as quarters,max(coalesce(name,source_name)) as name,
                    string_agg(period,';' order by period) as periods
                from holes group by dataset,code,field,cause,island order by field,dataset,code,first_period""",
            'internal_category_gaps':"""with limits as (select dataset,field,value,min(qi) as first_q,max(qi) as last_q
                    from audited where state='value' group by all), dates as (select distinct dataset,period,qi from units),
                holes as (select l.dataset,l.field,l.value,d.period,d.qi from limits l join dates d
                    on l.dataset=d.dataset and d.qi between l.first_q and l.last_q
                    where not exists(select 1 from audited a where a.dataset=l.dataset and a.field=l.field and a.value=l.value and a.state='value' and a.qi=d.qi)),
                islands as (select *,qi-row_number() over(partition by dataset,field,value order by qi) as island from holes)
                select dataset,field,value,min(period) as first_period,max(period) as last_period,count(*) as quarters,
                    string_agg(period,';' order by period) as periods from islands group by dataset,field,value,island order by field,dataset,first_period""",
        }
        conn.execute('create table category_gaps as '+queries['internal_category_gaps'])
        queries['category_gap_context']="""with windows as (select *,
            cast(substr(first_period,1,4) as integer)*4+cast(substr(first_period,5,2) as integer)//3 as first_q,
            cast(substr(last_period,1,4) as integer)*4+cast(substr(last_period,5,2) as integer)//3 as last_q from category_gaps),
            anchors as (select w.*,a.code from windows w join audited a on a.dataset=w.dataset and a.field=w.field
                and a.qi=w.first_q-1 and a.state='value' and a.value=w.value),
            dates as (select distinct dataset,period,qi from units)
            select a.dataset,a.field,a.value as gap_category,a.first_period,a.last_period,a.code,d.period,
                u.code is not null as reporting_unit,c.NomeInstituicao,c.Tcb,c.Sr,c.SegmentoTb,
                c.CodConglomeradoFinanceiro,c.CodConglomeradoPrudencial,c.source_file,c.source_sha256,c.source_row
            from anchors a join dates d on d.dataset=a.dataset and d.qi between a.first_q-1 and a.last_q+1
            left join units u on u.dataset=a.dataset and u.code=a.code and u.period=d.period
            left join cadastro c on c.CodInst=a.code and c.Data=d.period order by a.dataset,a.field,a.code,d.period"""
        conn.execute("""create table sr_evidence as
            select a.dataset,a.code,a.period,'own_prudential_parent' as link_kind,p.CodInst as evidence_code,
                p.Sr as evidence_sr,p.CodConglomeradoPrudencial as evidence_parent,p.source_file,p.source_sha256,p.source_row
            from audited a join cadastro own on own.CodInst=a.code and own.Data=a.period
            join cadastro p on p.CodInst=own.CodConglomeradoPrudencial and p.Data=a.period and p.CodInst<>a.code
            where a.field='Sr' and a.state<>'value' and a.period>='201703'
            union all
            select a.dataset,a.code,a.period,case when a.dataset='financial' then 'financial_members' else 'prudential_members' end,
                m.CodInst,m.Sr,m.CodConglomeradoPrudencial,m.source_file,m.source_sha256,m.source_row
            from audited a join cadastro m on m.Data=a.period and m.CodInst<>a.code and
                ((a.dataset='financial' and m.CodConglomeradoFinanceiro=a.code) or
                 (a.dataset='capital' and m.CodConglomeradoPrudencial=a.code))
            where a.field='Sr' and a.state<>'value' and a.period>='201703'""")
        queries['sr_link_evidence']='select * from sr_evidence order by dataset,code,period,link_kind,evidence_code'
        queries['sr_link_candidates']="""select dataset,code,period,link_kind,count(*) as linked_records,
            count(evidence_sr) as records_with_sr,count(distinct evidence_sr) as distinct_sr,
            min(evidence_sr) as candidate_sr,count(distinct evidence_parent) as distinct_prudential_parents,
            count(*)-count(evidence_parent) as records_without_parent,
            case when count(distinct evidence_sr)=1 then 'one_observed_label_not_adopted'
                 when count(distinct evidence_sr)>1 then 'conflicting_labels' else 'no_observed_label' end as candidate_state,
            false as applied from sr_evidence group by all order by dataset,code,period,link_kind"""
        raw_proof=None
        if raw_cadastro:
            rawroot=Path(raw_cadastro).resolve();positions=0
            for e in parts:
                rawpath=(rawroot/e['source_file']).resolve()
                if rawroot not in rawpath.parents:raise ValueError('Raw path escapes root')
                authenticate(rawpath,e['source_sha256'])
                body=json.loads(rawpath.read_text(encoding='utf-8-sig'))
                raw=body['value']
                if '@odata.nextLink' in body or len(raw)!=e['rows']:raise ValueError('Raw cadastro count/continuation mismatch')
                expected={r['CodInst']:r for r in raw}
                if len(expected)!=len(raw):raise ValueError('Duplicate raw cadastro key')
                cur=conn.execute('select '+','.join('"'+f+'"' for f in CADASTRO_FIELDS)+' from cadastro where Data=?',[e['period']])
                for values in cur.fetchall():
                    row=dict(zip(CADASTRO_FIELDS,values));original=expected.pop(row['CodInst'])
                    if set(original)!=set(CADASTRO_FIELDS):raise ValueError('Raw cadastro schema mismatch')
                    if any(row[f]!=(None if original[f] is None else str(original[f])) for f in CADASTRO_FIELDS):
                        raise ValueError('Raw/native cadastro mismatch')
                    positions+=len(CADASTRO_FIELDS)
                if expected:raise ValueError('Raw rows lost from cadastro')
            raw_proof=dict(root=str(rawroot),periods=len(parts),field_positions=positions,all_fields_exactly_equal=True)
        summary=dict(unit_periods=count,compared_positions=count*len(FIELDS),
            causes=[dict(zip(('dataset','field','cause','positions'),r)) for r in conn.execute('select dataset,field,cause,count(*) from audited group by all order by field,dataset,cause').fetchall()],
            input_pins=dict(baseline=pin,cadastro=cadastro_pin,unit_periods=unit_entry['sha256']),
            source_parts=parts,fields=list(FIELDS),periods=main['periods'],financial_recalculation=False,
            raw_cadastro_verification=raw_proof,derived_candidates_applied=False)
        for p,guard in guards.items():
            if (p.stat().st_size,p.stat().st_mtime_ns)!=guard:raise ValueError('Input changed during diagnosis')
        output.mkdir(parents=True)
        files=[]
        for name,query in queries.items():
            conn.execute('create or replace temp table exported as '+query)
            rows=conn.execute('select count(*) from exported').fetchone()[0]
            target=output/(name+'.csv');conn.execute('copy exported to ? (header,format csv)',[str(target)])
            files.append(dict(file=target.name,rows=rows,sha256=sha(target)))
        summary.update(files=files,elapsed_seconds=perf_counter()-started,producer_sha256=sha(Path(__file__)))
        (output/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('baseline','expected-baseline-manifest-sha256','output'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--raw-cadastro',help='Optional captured cadastro root; verifies all native fields against JSON')
    args=parser.parse_args()
    result=diagnose(args.baseline,args.expected_baseline_manifest_sha256,args.output,args.raw_cadastro)
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_parts','periods','causes')},ensure_ascii=True,indent=2))

"""Validate an official individual Resumo CSV and preserve original table tokens."""
import csv
import io
import json
import os
import subprocess
import shutil
import time
from pathlib import Path
from .archive import load_body


def validate_202312_schema(state: dict) -> None:
    profile=json.loads(Path(__file__).with_name('schema-202312.json').read_text(encoding='utf-8'))
    if state.get('columns')!=profile['columns'] or state.get('report')!=profile['report']:
        raise ValueError('202312 rendered schema/report notes differ from the reviewed official baseline')
    infos={info['id']:info for info in state.get('infos',[])}
    for expected in profile['infos']:
        if infos.get(expected['id'])!=expected:
            raise ValueError('202312 schema column name/definition/unit differs from the reviewed official baseline')


def parse_portal(state: dict, csv_body: bytes, period: int) -> dict:
    if state.get('period') != period or state.get('type_id') != 1006 or state.get('type_name') != 'Instituições Individuais' or state.get('report',{}).get('n') != 'Resumo':
        raise ValueError('Portal selection does not match the authorized individual Resumo quarter')
    if not state.get('expected_areas') or state.get('loaded_areas') != state.get('expected_areas'):
        raise ValueError('Portal data shards are incomplete')
    columns, rows = state.get('columns'), state.get('rows')
    if period==202312:
        validate_202312_schema(state)
    if not isinstance(columns,list) or not isinstance(rows,list) or not rows:
        raise ValueError('Portal table is missing')
    if any(not isinstance(row,list) or len(row) != len(columns) for row in rows):
        raise ValueError('Portal row width differs from its definitions')
    if 'expected_columns' in state and [col.get('ifd') for col in columns] != state['expected_columns']:
        raise ValueError('Rendered table is stale or differs from the selected report schema')
    headers = [''.join(line['cells']).replace('\n','').split(';') for line in state.get('header_lines',[])]
    try:
        exported=list(csv.reader(io.StringIO(csv_body.decode('utf-8-sig')),delimiter=';'))
    except (UnicodeError,csv.Error) as error:
        raise ValueError('Invalid official CSV export') from error
    if not headers or exported[:len(headers)] != headers:
        raise ValueError('Official CSV header differs from selected table definitions')
    csv_rows=exported[len(headers):len(headers)+len(rows)]
    if len(csv_rows)!=len(rows) or any(len(row)!=len(columns) for row in csv_rows):
        raise ValueError('Official CSV institution rows differ from the selected table')
    infos={str(info['id']):info for info in state['infos']}
    names=[infos.get(str(col['ifd']),{}).get('n','') for col in columns]
    if any(not name for name in names): raise ValueError('A rendered column lacks official metadata')
    code_indices=[i for i,name in enumerate(names) if name=='Código']
    name_indices=[i for i,name in enumerate(names) if name=='Instituição']
    if len(code_indices)!=1 or len(name_indices)!=1:
        raise ValueError('Identifier/name columns are not unambiguous')
    code_index,name_index=code_indices[0],name_indices[0]
    metric_indices=[i for i,col in enumerate(columns) if col.get('fid') in {2,3,4,5,6,7,10,11,12,13}]
    if not metric_indices: raise ValueError('No indicator definitions in selected Resumo')
    values,cadastro,disagreements=[],[],0
    for source_index,(row,csv_row) in enumerate(zip(rows,csv_rows),start=1):
        identifier=csv_row[code_index]
        if not identifier: raise ValueError('Empty source display code')
        if identifier != str(row[code_index]): raise ValueError('CSV/table source identifier differs')
        if csv_row[name_index] != str(row[name_index]).replace(';',' '):
            raise ValueError('CSV/table institution ordering differs')
        cadastro.append({'Data':str(period),'CodInst':identifier,'NomeInstituicao':str(row[name_index])})
        for index in metric_indices:
            col=columns[index]; value=row[index]; csv_token=csv_row[index]
            if isinstance(value,str) and value.strip() in {'NA','NI','NA%','NI%','null'} and csv_token.strip()!=value.strip(): disagreements+=1
            values.append({'AnoMes':str(period),'TipoInstituicao':3,'CodInst':identifier,
                'Conta':'portal_ifd:'+str(col['ifd']),'NomeColuna':names[index],'Saldo':value,
                'NomeRelatorio':'Resumo','Grupo':'portal_table_column','_csv_token':csv_token,
                '_unit':'BRL_unformatted_portal_table' if col.get('fid') in {11,12,13} else 'source_indicator_or_count',
                '_source_body':state.get('_state_body',''),'_source_sha256':state.get('_state_sha256',''),
                '_csv_body':state.get('_csv_body',''),'_csv_sha256':state.get('_csv_sha256',''),
                '_portal_row':source_index,'_format_id':col.get('fid')})
    return {'values':values,'cadastro':cadastro,'values_complete':True,'cadastro_complete':False,'identity_columns_complete':True,
        'source_mode':'official_portal_csv_fallback','identifier_namespace':'portal_display_code_not_assumed_CNPJ',
        'csv_table_disagreements':disagreements,'diagnostics':[
            'Official CSV monetary values are formatted/rounded in R$ mil. Inventory preserves unformatted official table tokens.',
            'Portal display code is not asserted equivalent to OData CodInst or a full CNPJ.',
            'Names cover the observed table population only; this does not establish complete OData registration coverage.',
            'Table state is generated evidence, not an HTTP response; original HTTP bodies and CSV accompany it.',
            f'{disagreements} missing-token cells differ from formatted CSV; table tokens retained.']}


def accept_export(index: dict, raw: Path, period: int) -> dict:
    if index.get('period')!=period or not index.get('complete'): raise ValueError('Incomplete or wrong-quarter export')
    for manifest in index.get('manifests',[]): load_body(manifest,raw)
    sm,cm=index['state_manifest'],index['csv_manifest']
    state=json.loads(load_body(sm,raw))
    state.update({'_state_body':sm['body_path'],'_state_sha256':sm['sha256'],'_csv_body':cm['body_path'],'_csv_sha256':cm['sha256']})
    result=parse_portal(state,load_body(cm,raw),period)
    result['portal_export_index']=index
    return result


def export_portal(period: int, raw: Path) -> dict:
    if period not in {201012,202312,202412}: raise ValueError('Only explicitly approved quarters are allowed')
    script=Path(__file__).resolve().parent.parent/'scripts'/'export-portal.cjs'
    raw=Path(raw);raw.mkdir(parents=True,exist_ok=True)
    deadline=time.monotonic()+480
    failures=[]
    for attempt in range(1,3):
        remaining=deadline-time.monotonic()
        if remaining<5:break
        if shutil.disk_usage(raw).free<150*1024*1024:raise RuntimeError('150 MiB disk reserve unavailable; export not started')
        env={**os.environ,'PILOT_TIMEOUT_MS':str(int(remaining*1000)-1500),'PILOT_ATTEMPT':str(attempt)}
        try:
            completed=subprocess.run([os.environ.get('PILOT_NODE','node'),str(script),str(period),str(raw.resolve())],
                capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=remaining,check=False,env=env)
            if completed.returncode!=0:
                failures.append(completed.stderr[-4000:]);continue
            info=json.loads(completed.stdout.strip().splitlines()[-1])
            result=accept_export(json.loads(Path(info['export_index']).read_text(encoding='utf-8')),raw,period)
            result['export_attempts']=attempt
            return result
        except subprocess.TimeoutExpired:
            failures.append('Official export exceeded total 480-second deadline');break
        except (ValueError,OSError) as error:failures.append(str(error))
    raise RuntimeError('Official export incomplete after at most two attempts / 480 seconds: '+'; '.join(failures))

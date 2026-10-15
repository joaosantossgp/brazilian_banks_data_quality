"""Dated native reporting population; no financial calculations or identity guesses.

Config is exactly ``{periods: [YYYYMM], datasets: [name], inputs: {...}}``.
Inputs contain sample125, catalogue, cadastro and each selected native dataset,
each with root/expected_manifest_sha256. Dataset/type pairs are finite:
financial/2, individual/3, capital/1, segmentation/1. Segmentation is a native
namespace within the prudential perspective, never a fourth additive view.

Rows are ordered by period/dataset/native type/code (links then by company).
JSON holds complete logical rows; CSV/Parquet have the textual columns below
and the same canonical JSON payload. Consumers should read payload to retain
literal null/empty classifications, proof paths and arrays. All native units
remain present regardless of metric coverage or membership. Manifest matrices
contain all24 company rows, missing links and target presence independently.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from contextlib import ExitStack, closing
import csv
import io
import json
from pathlib import Path

import duckdb

from .ifdata_analysis import (_authenticate, _contained, _digest_file,
                              _iter_json_array, _json_unique, _period_date,
                              _read_sample, _records, _schema)
from .ifdata_cadastro import FIELDS, ORIGIN, CONTRACT as CAD_CONTRACT
from .ifdata_odata import COLUMNS, FIELDS as VALUE_FIELDS, CONTRACT as DATA_CONTRACT

CONTRACT = 'ifdata-population-v1'
POLICY = 'native-dated-membership-v2'
DATASET_TYPES = {'financial': '2', 'individual': '3', 'capital': '1', 'segmentation': '1'}
PERSPECTIVES = {'financial': 'financial', 'individual': 'individual',
                'capital': 'prudential', 'segmentation': 'prudential'}
TABLE_COLUMNS = {
    'unit_periods': ('unit_id', 'dataset', 'perspective', 'TipoInstituicao', 'code',
                     'period', 'membership', 'membership_reason', 'matrix_id',
                     'cadastro_state', 'aggregate_selection_status', 'payload'),
    'membership_links': ('link_id', 'unit_id', 'dataset', 'period', 'membership',
                          'company_id', 'relation', 'scope', 'matrix_id', 'payload'),
}
SCOPE = 'dated_native_relations_to_sample125_targets_and_named_operators'


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def partition_membership(unit_rows: list[dict]) -> dict[str, set[str]]:
    """Deduplicate contributions; contradictory membership becomes unknown."""
    states = defaultdict(set)
    for row in unit_rows:
        if (not isinstance(row, dict) or not isinstance(row.get('unit_id'), str)
                or not row['unit_id'] or row.get('membership') not in ('sample','remaining','unknown')):
            raise ValueError('Invalid unit membership row')
        states[row['unit_id']].add(row['membership'])
    result = {'total': set(states), 'sample': set(), 'remaining': set(), 'unknown': set()}
    for unit, choices in states.items():
        state = next(iter(choices)) if len(choices) == 1 else 'unknown'
        result[state].add(unit)
    return result


def _terminal(cad, code, field):
    if code is None:
        return {'state': 'null_parent', 'path': []}
    path = []
    while True:
        if code in path:
            return {'state': 'cycle', 'path': path + [code]}
        path.append(code)
        own = cad.get(code)
        if own is None:
            return {'state': 'missing_parent_cadastro', 'path': path}
        parent = own[field]
        if parent == code:
            return {'state': 'self_terminal', 'path': path}
        if parent is None:
            return {'state': 'null_terminal_unresolved', 'path': path}
        code = parent


def _classify(code, own, parent, path, targets, operators, complete, individual, operator_targets):
    if own is None:
        return 'unknown', 'missing_own_cadastro'
    direct = code in (operators if individual else targets)
    if individual and direct and len(operator_targets) > 1:
        return 'unknown', 'multiple_operator_target_proofs'
    graph_ok = path['state'] == 'self_terminal'
    if parent is not None and not graph_ok:
        return 'unknown', path['state']
    if individual and direct and parent is not None and operator_targets and parent not in operator_targets:
        return 'unknown', 'operator_target_parent_conflict'
    if direct and parent is not None and parent not in targets:
        return 'unknown', 'positive_native_parent_conflict'
    if direct:
        return 'sample', 'explicit_operator125' if individual else 'agreed_prudential_target125'
    if parent is not None and parent in targets and graph_ok:
        return 'sample', ('own_dated_financial_parent_selected125' if individual
                          else 'own_dated_prudential_parent_selected125')
    if graph_ok and any(node in targets for node in path['path']):
        return 'unknown', 'selected_ancestor_requires_scope'
    if parent is not None and graph_ok and complete:
        return 'remaining', 'explicit_other_parent_complete_matrix'
    return 'unknown', 'null_parent_not_negative' if parent is None else 'incomplete_sample_matrix'


def _proof(row):
    return ({k: row[k] for k in ('CodInst','Data', *ORIGIN)} if row is not None else None)


def _matrix(period, maps, cad, native, map_sha):
    financial, operators, operator_targets, prudential = (defaultdict(set) for _ in range(4))
    missing_f, missing_p, company_rows = [], [], []
    for row in sorted(maps, key=lambda r:r['company_cnpj14']):
        company, fcode, op = row['company_cnpj14'], row['native_target_code'], row['operator_base8']
        if fcode:
            financial[fcode].add(company)
        else:
            missing_f.append(company)
        if op:
            operators[op].add(company)
            if fcode:
                operator_targets[op].add(fcode)
        od, fd = cad.get(op), cad.get(fcode)
        pc = od['CodConglomeradoPrudencial'] if od else None
        pd = cad.get(pc)
        agrees = bool(pc and fd and pc == fd['CodConglomeradoPrudencial'] and pd)
        if agrees:
            prudential[pc].add(company)
        else:
            missing_p.append(company)
        company_rows.append(dict(company_id=company, financial_target=fcode, operator=op,
             prudential_target=pc if agrees else None,
             financial_state='admitted_target125' if fcode else 'missing_target125',
             prudential_state='agreed_dated_bridge' if agrees else 'missing_or_conflicting_dated_bridge',
             operator_cadastro=_proof(od), financial_cadastro=_proof(fd),
             prudential_cadastro=_proof(pd) if agrees else None))
    matrix = dict(period=period, financial_matrix_id='financial|'+period,
                  prudential_matrix_id='prudential|'+period, company_rows=company_rows,
                  financial_complete=not missing_f, prudential_complete=not missing_p,
                  financial_missing_companies=missing_f, prudential_missing_companies=missing_p,
                  financial_targets={k:sorted(v) for k,v in sorted(financial.items())},
                  prudential_targets={k:sorted(v) for k,v in sorted(prudential.items())},
                  map125_sha256=map_sha, scope=SCOPE,
                  target_values_presence={ds:{code:code in {u['CodInst'] for u in units}
                      for code in (financial if ds=='financial' else operators if ds=='individual' else prudential)}
                      for ds,units in sorted(native.items())})
    return matrix, financial, operators, operator_targets, prudential


def _validate_config(config):
    if not isinstance(config, dict) or set(config) != {'periods','datasets','inputs'}:
        raise ValueError('Invalid population config')
    periods, datasets, inputs = config['periods'], config['datasets'], config['inputs']
    if (not isinstance(periods,list) or not periods or any(_period_date(p) is None for p in periods)
            or len(set(periods)) != len(periods)):
        raise ValueError('Invalid or duplicate core periods')
    if (not isinstance(datasets,list) or not datasets or any(not isinstance(d,str) or d not in DATASET_TYPES for d in datasets)
            or len(set(datasets)) != len(datasets)):
        raise ValueError('Invalid or duplicate datasets')
    if not isinstance(inputs,dict) or set(inputs) != {'sample','catalogue','cadastro',*datasets}:
        raise ValueError('Missing or unknown population inputs')
    return sorted(periods), sorted(datasets)


def _metadata(manifest):
    files = manifest['files']
    if (type(manifest.get('rows')) is not int or manifest['rows'] < 0 or not isinstance(files,list)
            or any(type(e.get('rows')) is not int or e['rows'] < 0 for e in files)
            or sum(e['rows'] for e in files) != manifest['rows']):
        raise ValueError('Native inventory counts mismatch')
    if any(not isinstance(e.get('period'),(str,int)) for e in files):
        raise ValueError('Missing native part period')


def _quarter_view(conn, source, period, dataset=None):
    """One live bounded connection, authenticated explicit parts of one quarter."""
    root, manifest = source
    parts = sorted((e for e in manifest['files'] if str(e['period']) == period),key=lambda e:e['file'])
    if not parts:
        return False
    table, fields, period_field = ('ifdata',COLUMNS,'AnoMes') if dataset else ('cadastro',FIELDS+ORIGIN,'Data')
    if dataset and any(str(e.get('type')) != DATASET_TYPES[dataset] for e in parts):
        raise ValueError('Native part type mismatch')
    for part in parts:
        conn.from_parquet(str(_contained(root,part['file']))).create_view(table,replace=True)
        _schema(conn,table,fields)
        if conn.execute('select count(*) from '+table).fetchone()[0] != part['rows']:
            raise ValueError('Native part count mismatch')
    conn.from_parquet([str(_contained(root,e['file'])) for e in parts]).create_view(table,replace=True)
    _schema(conn,table,fields)
    count = conn.execute('select count(*) from '+table).fetchone()[0]
    if count != sum(e['rows'] for e in parts):
        raise ValueError('Native quarter count mismatch')
    if conn.execute('select count(*) from '+table+' where '+period_field+' is distinct from ?', [period]).fetchone()[0]:
        raise ValueError('Native part period mismatch')
    if dataset and conn.execute('select count(*) from ifdata where TipoInstituicao is distinct from ?',
                                [DATASET_TYPES[dataset]]).fetchone()[0]:
        raise ValueError('Native institution type mismatch')
    return True


class _TableWriter:
    """Stream quarter rows; avoid retaining the complete reporting history."""
    def __init__(self, output, table, stack):
        self.output, self.table, self.columns = output, table, TABLE_COLUMNS[table]
        self.count, self.max_line = 0, 2*1024*1024
        self.json = stack.enter_context((output/(table+'.json')).open('w',encoding='utf-8'))
        self.csv = stack.enter_context((output/(table+'.csv')).open('w',encoding='utf-8',newline=''))
        self.writer = csv.writer(self.csv,quoting=csv.QUOTE_NOTNULL)
        self.writer.writerow(self.columns)
        self.json.write('[')

    def append(self, row):
        payload = _canonical(row)
        self.json.write((',' if self.count else '')+'\n'+payload)
        self.writer.writerow([row.get(k) for k in self.columns[:-1]]+[payload])
        self.max_line = max(self.max_line,len(payload.encode('utf-8'))*4+4096)
        self.count += 1

    def finish(self, conn):
        self.json.write('\n]\n' if self.count else ']\n')
        self.json.close(); self.csv.close()
        columns = '{'+','.join("'"+k+"':'VARCHAR'" for k in self.columns)+'}'
        conn.execute('copy (select * from read_csv($source, header=true, auto_detect=false, columns='+columns+
                     ", delim=',', quote='\"', escape='\"', nullstr='', allow_quoted_nulls=false, parallel=false, max_line_size=$limit)) "+
                     'to $destination (format parquet, compression zstd, row_group_size 2048)',
                     dict(source=str(self.output/(self.table+'.csv')),limit=str(self.max_line),
                          destination=str(self.output/(self.table+'.parquet'))))
        return [dict(file=self.table+'.'+ext,sha256=_digest_file(self.output/(self.table+'.'+ext)),rows=self.count)
                for ext in ('json','csv','parquet')]


def build_population(config: dict, output: Path) -> dict:
    """Build deterministic, externally authenticated population in an exclusive root.

    Source authentication is once per build, not once per quarter. Reads and
    Python working sets are per quarter; only manifest diagnostics accumulate.
    Source hashes are checked again before the acceptance manifest is written.
    Failure keeps the exclusive partial directory, without an accepted manifest.
    """
    periods, datasets = _validate_config(config)
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(output)
    contracts = {'sample':None,'cadastro':CAD_CONTRACT,'catalogue':'ifdata-variable-catalog-v1',
                 **{ds:DATA_CONTRACT for ds in datasets}}
    accepted = {name:_authenticate(config['inputs'][name],contract) for name,contract in contracts.items()}
    catalogue = accepted['catalogue'][1]
    for ds in datasets:
        if catalogue.get('inputs',{}).get(ds,{}).get('manifest_sha256') != config['inputs'][ds]['expected_manifest_sha256']:
            raise ValueError('Catalogue source lineage mismatch')
    for ds in ['cadastro',*datasets]:
        _metadata(accepted[ds][1])
    maps, _, _ = _read_sample(*accepted['sample'])
    companies = {r['company_cnpj14'] for r in maps}
    if len(companies) != 24:
        raise ValueError('Sample125 must preserve all24 companies')
    by_period = defaultdict(list)
    for row in maps:
        by_period[row['period']].append(row)
    if any({r['company_cnpj14'] for r in by_period[p]} != companies for p in periods):
        raise ValueError('Incomplete all24 company matrix rows')
    map_sha = accepted['sample'][1]['files']['company-quarter-map.json']
    output.mkdir(parents=True,exist_ok=False)
    manifest = dict(contract=CONTRACT, policy=POLICY, scope=SCOPE, config=config,
                    tables={}, files=[], schemas={k:list(v) for k,v in TABLE_COLUMNS.items()},
                    matrices=[], periods=[], null_identities=[], parent_copresence=[],
                    cadastro_only=[], company_map_missing=[], aggregate_policy='technical_occurrences_no_covered_by_root',
                    read_limits=dict(memory_limit='512MiB',threads=1,working_set='one_quarter'),
                    writer=dict(format='textual_parquet',compression='zstd',row_group_size=2048,
                                preserve_insertion_order=True,threads=1))
    with ExitStack() as stack, duckdb.connect(config={'memory_limit':'512MiB','threads':1}) as conn:
        writers = {table:_TableWriter(output,table,stack) for table in TABLE_COLUMNS}
        for period in periods:
            cad = {}
            if _quarter_view(conn,accepted['cadastro'],period):
                if conn.execute("select count(*) from cadastro where CodInst is null or CodInst='' ").fetchone()[0]:
                    raise ValueError('Missing temporal cadastro key')
                if conn.execute('select count(*) from (select CodInst from cadastro group by all having count(*)>1)').fetchone()[0]:
                    raise ValueError('Duplicate temporal cadastro key; unsafe classification')
                cad = {r['CodInst']:r for r in _records(conn.execute('select * from cadastro where Data=? order by CodInst',[period]))}
            native, present = {}, {}
            for ds in datasets:
                present[ds] = _quarter_view(conn,accepted[ds],period,ds)
                if not present[ds]:
                    native[ds] = []
                    continue
                identity = ','.join(VALUE_FIELDS[:-1])
                if conn.execute('select count(*) from (select '+identity+" from ifdata where AnoMes=? and CodInst is not null and CodInst<>'' group by all having count(*)>1)",[period]).fetchone()[0]:
                    raise ValueError('Duplicate native observation key in '+ds+'/'+period)
                for row in _records(conn.execute('select * from ifdata where AnoMes=? and (CodInst is null or CodInst=?) order by TipoInstituicao,NumeroRelatorio,Conta,Grupo,source_file,source_row',[period,''])):
                    manifest['null_identities'].append(dict(dataset=ds,**row))
                native[ds] = _records(conn.execute("select TipoInstituicao,CodInst,count(*)::VARCHAR as value_rows from ifdata where AnoMes=? and CodInst is not null and CodInst<>'' group by all order by TipoInstituicao,CodInst",[period]))
            matrix, ftargets, operators, operator_targets, ptargets = _matrix(period,by_period[period],cad,native,map_sha)
            manifest['matrices'].append(matrix)
            for perspective,missing in [('financial',matrix['financial_missing_companies']),('prudential',matrix['prudential_missing_companies'])]:
                manifest['company_map_missing'].extend(dict(period=period,perspective=perspective,company_id=company,
                    reason='missing_target125' if perspective=='financial' else 'missing_or_conflicting_dated_bridge') for company in missing)
            for ds in datasets:
                codes = {r['CodInst'] for r in native[ds]}
                manifest['cadastro_only'].append(dict(dataset=ds,period=period,
                    state='diagnostic_not_reporting_population',codes=sorted(set(cad)-codes)))
                counts = Counter()
                for key in native[ds]:
                    code, ti = key['CodInst'], key['TipoInstituicao']
                    if '|' in code:
                        raise ValueError('Ambiguous native identity delimiter')
                    unit_id = '|'.join([ds,ti,code,period])
                    own, parent, path, company_ids = cad.get(code), None, None, []
                    individual = ds=='individual'
                    matrix_id = matrix['financial_matrix_id'] if ds in ('financial','individual') else matrix['prudential_matrix_id']
                    if ds=='financial':
                        membership = 'sample' if code in ftargets else 'remaining'
                        reason = 'sample125_financial_target' if membership=='sample' else 'technical_financial_complement125'
                        company_ids = sorted(ftargets.get(code,()))
                    else:
                        field = 'CodConglomeradoFinanceiro' if individual else 'CodConglomeradoPrudencial'
                        targets = ftargets if individual else ptargets
                        complete = matrix['financial_complete'] if individual else matrix['prudential_complete']
                        parent = own[field] if own else None
                        path = _terminal(cad,parent,field)
                        membership,reason = _classify(code,own,parent,path,targets,operators,complete,individual,operator_targets.get(code,set()))
                        if membership=='sample':
                            company_ids = sorted((operators.get(code,set()) if individual else targets.get(code,set())) | targets.get(parent,set()))
                    counts[membership] += 1
                    row = dict(unit_id=unit_id,dataset=ds,perspective=PERSPECTIVES[ds],TipoInstituicao=ti,
                        code=code,period=period,membership=membership,membership_reason=reason,matrix_id=matrix_id,
                        cadastro_state='observed' if own else 'missing_own_cadastro',
                        classifications={k:own[k] for k in FIELDS if k not in ('CodInst','Data')} if own else None,
                        nature_state='native_Td_literal' if own else 'unproven',
                        aggregate_selection_status='prudential_overlap_unproven' if ds in ('capital','segmentation') else 'technical_occurrence_only',
                        companies=company_ids, own_cadastro=_proof(own), native_parent=parent,
                        native_graphs={perspective:_terminal(cad,own[field] if own else None,field)
                            for perspective,field in [('financial','CodConglomeradoFinanceiro'),
                                                       ('prudential','CodConglomeradoPrudencial')]},
                        terminal=path, value_rows=key['value_rows'])
                    writers['unit_periods'].append(row)
                    link = dict(unit_id=unit_id,dataset=ds,period=period,membership=membership,
                        relation=reason,scope=SCOPE,matrix_id=matrix_id,own_cadastro=_proof(own),
                        native_parent=parent,parent_cadastro=_proof(cad.get(parent)),terminal=path,
                        path_cadastro=[_proof(cad.get(node)) for node in path['path']] if path else [],
                        map125_sha256=map_sha)
                    for company in company_ids or [None]:
                        linked = dict(link,company_id=company,
                            link_id=unit_id+'|'+(company if company is not None else '@decision'))
                        writers['membership_links'].append(linked)
                    for field in ('CodConglomeradoFinanceiro','CodConglomeradoPrudencial'):
                        native_parent = own[field] if own else None
                        if native_parent and native_parent != code and native_parent in codes:
                            manifest['parent_copresence'].append(dict(dataset=ds,period=period,code=code,
                                parent_field=field,parent_code=native_parent,own_cadastro=_proof(own),
                                terminal=_terminal(cad,native_parent,field),selection='diagnostic_only'))
                manifest['periods'].append(dict(dataset=ds,period=period,
                    population_state=('observed' if native[ds] else 'observed_empty') if present[ds] else 'source_period_not_captured',
                    observed_identified_total=len(native[ds]), sample=counts['sample'],remaining=counts['remaining'],
                    membership_unknown=counts['unknown'],matrix_id=matrix_id if native[ds] else (
                        matrix['financial_matrix_id'] if ds in ('financial','individual') else matrix['prudential_matrix_id'])))
            # Release quarter data before reading the next one.
            del native, cad
        for table,writer in writers.items():
            manifest['files'].extend(writer.finish(conn)); manifest['tables'][table] = writer.count
    # Do not accept output if an authenticated input changed during the build.
    for name,contract in contracts.items():
        _authenticate(config['inputs'][name],contract)
    manifest['config'] = dict(periods=periods,datasets=datasets,
                             inputs={k:config['inputs'][k] for k in sorted(config['inputs'])})
    (output/'manifest.json').write_text(_canonical(manifest)+'\n',encoding='utf-8')
    return manifest


def open_population(output: Path, expected_manifest_sha256: str):
    """Verify external pin, inventories, exact schemas/counts and all three formats.

    Return a caller-owned DuckDB connection exposing unit_periods and
    membership_links, both entirely VARCHAR. Verification streams records;
    use context management to close the connection after consumption.
    """
    root, manifest = _authenticate(dict(root=str(output),expected_manifest_sha256=expected_manifest_sha256),CONTRACT,True)
    if (manifest.get('policy') != POLICY or manifest.get('schemas') != {k:list(v) for k,v in TABLE_COLUMNS.items()}
            or set(manifest.get('tables',{})) != set(TABLE_COLUMNS)):
        raise ValueError('Population schema/policy mismatch')
    expected_files = {table+'.'+ext for table in TABLE_COLUMNS for ext in ('json','csv','parquet')}
    if {e['file'] for e in manifest['files']} != expected_files:
        raise ValueError('Population inventory mismatch')
    conn = duckdb.connect(config={'memory_limit':'512MiB','threads':1})
    try:
        for table,columns in TABLE_COLUMNS.items():
            conn.from_parquet(str(root/(table+'.parquet'))).create_view(table)
            _schema(conn,table,columns)
            expected_count = manifest['tables'][table]
            if type(expected_count) is not int or expected_count < 0 or any(e['rows']!=expected_count for e in manifest['files'] if e['file'].startswith(table+'.')):
                raise ValueError('Population table counts disagree')
            with (root/(table+'.csv')).open(encoding='utf-8',newline='') as stream, closing(_iter_json_array(root/(table+'.json'))) as logical:
                # Compare canonical physical CSV records. Python3.12's reader
                # does not implement QUOTE_NOTNULL null/empty distinction.
                encoded = io.StringIO(newline='')
                csv_writer = csv.writer(encoded,quoting=csv.QUOTE_NOTNULL)
                def compare_csv(values):
                    encoded.seek(0); encoded.truncate(0); csv_writer.writerow(values)
                    expected = encoded.getvalue()
                    return stream.read(len(expected)) == expected
                if not compare_csv(columns):
                    raise ValueError('Population CSV schema mismatch')
                cursor = conn.execute('select * from '+table)
                count = 0
                for batch in iter(lambda:cursor.fetchmany(256),[]):
                    for values in batch:
                        obj = next(logical,None)
                        if not compare_csv(values) or not isinstance(obj,dict) or values[-1] != _canonical(obj):
                            raise ValueError('Population formats disagree')
                        if [obj.get(k) for k in columns[:-1]] != list(values[:-1]):
                            raise ValueError('Population projection and payload disagree')
                        count += 1
                if count!=expected_count or stream.read(1) or next(logical,None) is not None:
                    raise ValueError('Population format counts disagree')
            key = 'unit_id' if table=='unit_periods' else 'link_id'
            if conn.execute('select count(*) from (select '+key+' from '+table+' group by all having count(*)>1)').fetchone()[0]:
                raise ValueError('Duplicate population identity')
        if conn.execute('select count(*) from membership_links l left join unit_periods u using(unit_id) where u.unit_id is null or l.membership is distinct from u.membership').fetchone()[0]:
            raise ValueError('Membership link reconciliation mismatch')
        return conn
    except Exception:
        conn.close()
        raise

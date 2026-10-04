"""Exact offline Parquet projection of the closed financial 202412 admission."""
from collections import Counter
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import io
import json
import os
from pathlib import Path
import re

from .financial import CONTRACT as SOURCE_CONTRACT, FIELDS, PROFILE_PATH, ROLES, SELECTION
from .inventory import classify

CONTRACT = 'ifdata-financial-parquet-202412-v1'
PART = 'parts/financial-cells-202412.parquet'
COMPANIONS = ('financial-cadastro.csv', 'financial-variables.json', 'financial-diagnostics.json')
INPUTS = ('financial-observations.csv', 'financial-cells.csv', *COMPANIONS)
OUTPUTS = (PART, 'metadata/source-manifest.json', *(f'metadata/{n}' for n in COMPANIONS))
COMMON = ('contract', 'period', 'perspective', 'perspective_id', 'report_id',
          'report_generation', 'report_version', 'report_generation_state', 'report_version_state')
CAD_FIELDS = [*COMMON, *(f'c{i}' for i in range(38)), 'source_body', 'source_sha256', 'source_pointer']
BIND_FIELDS = ('ifd', 'td', 'area', 'lid', 'fid', 'catalog_pointer', 'definition_pointer',
               'unit', 'unit_basis', 'window_start', 'window_end', 'window_basis')
HASH = re.compile(r'[0-9a-f]{64}')
NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def _json(body):
    def invalid(value):
        raise ValueError('Invalid JSON constant: ' + value)
    return json.loads(body, object_pairs_hook=_pairs, parse_constant=invalid)


def _csv(body, fields):
    reader = csv.DictReader(io.StringIO(body.decode('utf-8-sig'), newline=''))
    _require(reader.fieldnames == list(fields), 'Invalid CSV headers')
    rows = list(reader)
    _require(all(set(row) == set(fields) and all(type(v) is str for v in row.values()) for row in rows),
             'Malformed CSV row')
    return rows


def _path(root, name):
    _require(isinstance(name, str) and name and not any(c in name for c in ('\\', ':', '*', '?', '['))
             and not Path(name).is_absolute() and all(p not in ('', '.', '..') for p in name.split('/')),
             'Invalid snapshot path')
    path = root / name
    _require(path.resolve().is_relative_to(root.resolve()) and not path.is_symlink(), 'Snapshot path escapes directory')
    return path


def _files(root, entries, names):
    _require(isinstance(entries, list) and len(entries) == len(names), 'Invalid file inventory')
    result = {}
    for entry in entries:
        _require(isinstance(entry, dict) and set(entry) == {'path', 'bytes', 'sha256'}, 'Invalid file record')
        name = entry['path']
        _require(name in names and name not in result, 'Unexpected or duplicate file path')
        _require(type(entry['bytes']) is int and entry['bytes'] >= 0 and isinstance(entry['sha256'], str)
                 and HASH.fullmatch(entry['sha256']), 'Invalid file size/hash')
        body = _path(root, name).read_bytes()
        _require(len(body) == entry['bytes'] and _sha(body) == entry['sha256'], 'File size/hash mismatch: ' + name)
        result[name] = body
    return result


def _common(manifest):
    _require(isinstance(manifest, dict) and manifest.get('contract') == SOURCE_CONTRACT
             and manifest.get('accepted') is True and _dump(manifest.get('selection')) == _dump(SELECTION),
             'Unknown source contract or selection')
    expected = dict(contract=SOURCE_CONTRACT, period=202412, perspective='financial', perspective_id=1005, report_id=92)
    _require(all(_dump(manifest.get(k)) == _dump(v) for k, v in expected.items()), 'Invalid source scope')
    for key in ('report_generation', 'report_version'):
        _require(type(manifest.get(key)) is str and manifest.get(key + '_state') ==
                 ('reported_text' if manifest[key] else 'unknown'), 'Invalid generation/version state')
    _require(manifest.get('profile_sha256') == _sha(PROFILE_PATH.read_bytes().replace(b'\r\n', b'\n')),
             'Unknown admitted profile')
    sources = manifest.get('sources')
    _require(isinstance(sources, dict) and set(sources) == ROLES, 'Invalid source membership')
    for record in sources.values():
        _require(isinstance(record, dict) and isinstance(record.get('body_path'), str) and record['body_path']
                 and all(isinstance(record.get(k), str) and HASH.fullmatch(record[k])
                         for k in ('sha256', 'manifest_sha256')), 'Invalid source provenance')
    _require(isinstance(manifest.get('limitations'), list) and all(type(v) is str for v in manifest['limitations']),
             'Invalid source limitations')
    return {k: str(manifest[k]) for k in COMMON}


def _metadata(manifest, bodies):
    common = _common(manifest)
    cadastro = _csv(bodies['financial-cadastro.csv'], CAD_FIELDS)
    _require(cadastro, 'Empty financial cadaster')
    sources = manifest['sources']
    seen = set()
    for index, row in enumerate(cadastro):
        _require(all(row[k] == v for k, v in common.items()) and row['c1'] == '202412', 'Wrong cadaster scope')
        _require(re.fullmatch(r'0|[1-9][0-9]*', row['c0']) and row['c0'] not in seen,
                 'Invalid or duplicate literal cadaster key')
        seen.add(row['c0'])
        _require(row['source_pointer'] == f'/{index}' and row['source_body'] == sources['cadaster']['body_path']
                 and row['source_sha256'] == sources['cadaster']['sha256'], 'Invalid cadaster provenance')
    document = _json(bodies['financial-variables.json'])
    _require(isinstance(document, dict) and all(str(document.get(k)) == v for k, v in common.items()),
             'Wrong variable scope')
    variables = document.get('variables')
    metrics = _json(PROFILE_PATH.read_bytes())['metrics']
    _require(isinstance(variables, list) and len(variables) == len(metrics), 'Incomplete variable bindings')
    prefixes, pointers = set(), set()
    for variable, metric in zip(variables, metrics):
        _require(isinstance(variable, dict) and set(variable) == {*BIND_FIELDS, 'name', 'definition'},
                 'Invalid binding schema')
        info = metric['info']
        expected = {k: info[source] for k, source in [('ifd', 'id'), ('td', 'td'), ('area', 'a'), ('lid', 'lid')]}
        money = info['td'] == 3
        expected.update(fid=metric['fid'], name=info['n'], definition=info,
                        unit='BRL_raw_inferred' if money else 'count',
                        unit_basis='archived_formatter_divides_by_1000' if money else 'cadaster_definition',
                        window_start='2024-07-01' if info['id'] == 79718 else '', window_end='2024-12-31',
                        window_basis='report_rp_result_window' if info['id'] == 79718 else
                        'stock_at_reference_inferred' if money else 'cadaster_reference')
        _require(all(_dump(variable[k]) == _dump(v) for k, v in expected.items()), 'Binding differs from admitted profile')
        pointer = variable['catalog_pointer']
        _require(isinstance(pointer, str) and re.fullmatch(r'/[0-9]+/files/[0-9]+/trel/c/' + str(metric['position']), pointer),
                 'Invalid catalog pointer')
        prefixes.add(pointer.rsplit('/', 1)[0])
        definition = variable['definition_pointer']
        _require(isinstance(definition, str) and re.fullmatch(r'/[0-9]+', definition) and definition not in pointers,
                 'Invalid or duplicate definition pointer')
        pointers.add(definition)
    _require(len(prefixes) == 1, 'Bindings reference different reports')
    diagnostics = _json(bodies['financial-diagnostics.json'])
    _require(isinstance(diagnostics, dict) and diagnostics.get('contract') == SOURCE_CONTRACT
             and _dump(diagnostics.get('selection')) == _dump(SELECTION)
             and diagnostics.get('limitations') == manifest['limitations'], 'Invalid diagnostic scope/limits')
    return common, cadastro, variables, diagnostics


def _numbers(rows):
    values = []
    for row in rows:
        presence, raw, kind = row['presence'], row['raw_value'], row['source_kind']
        if presence != 'stored':
            _require(presence in ('entity_not_stored', 'information_not_stored') and raw == ''
                     and kind == 'not_stored' and row['value_state'] == 'unobserved_cell'
                     and row['numeric_value'] == '', 'Invalid unobserved cell')
            values.append(None)
            continue
        _require(kind in ('json_number', 'json_string', 'json_null'), 'Invalid source value kind')
        if kind == 'json_number':
            _require(NUMBER.fullmatch(raw), 'Invalid JSON number lexeme')
        elif kind == 'json_null':
            _require(raw == 'null', 'Invalid JSON null token')
        state = 'json_null' if kind == 'json_null' else classify(raw)
        _require(state != 'invalid' and row['value_state'] == state, 'Value state differs from token/type')
        number = Decimal(raw.strip()) if state in ('numeric', 'zero') else None
        _require(row['numeric_value'] == (str(number) if number is not None else ''), 'Numeric projection differs from token')
        values.append(number)
    scale = max((max(0, -n.as_tuple().exponent) for n in values if n is not None), default=0)
    integers = max((max(0, n.adjusted() + 1) for n in values if n is not None), default=0)
    width = max(1, integers + scale)
    _require(width <= 38, 'Exact DECIMAL requires more than 38 digits')
    return values, f'DECIMAL({width},{scale})'


def _rows(manifest, rows, metadata):
    common, cadastro, variables, diagnostics = metadata
    cad = {r['c0']: r for r in cadastro}
    bindings = {str(v['ifd']): v for v in variables}
    seen, entity_pointers, numeric_presence = set(), {}, {}
    for row in rows:
        _require(set(row) == set(FIELDS) and all(type(v) is str for v in row.values()), 'Invalid row schema')
        key = (row['institution_id'], row['ifd'])
        _require(key not in seen, 'duplicate financial cell')
        seen.add(key)
        _require(key[0] in cad and key[1] in bindings, 'Unknown cell occurrence/binding')
        var = bindings[key[1]]
        _require(all(row[k] == v for k, v in common.items())
                 and all(row[k] == str(var[k]) for k in BIND_FIELDS) and row['variable'] == var['name'],
                 'Cell scope or binding mismatch')
        role = 'numeric' if var['td'] == 3 else 'cadaster'
        source = manifest['sources'][role]
        _require(row['source_role'] == role and row['source_body'] == source['body_path']
                 and row['source_sha256'] == source['sha256'], 'Cell source mismatch')
        pointer, presence = row['source_pointer'], row['presence']
        if role == 'cadaster':
            _require(presence == 'stored' and row['source_kind'] == 'json_string'
                     and row['raw_value'] == cad[key[0]][f'c{var["lid"]}']
                     and pointer == cad[key[0]]['source_pointer'] + f'/c{var["lid"]}', 'Invalid cadastral quantity')
        else:
            numeric_presence.setdefault(key[0], set()).add(presence)
            if presence == 'entity_not_stored':
                _require(pointer == '/values', 'Invalid absent-entity pointer')
                continue
            pattern = r'(/values/[0-9]+)/v/[0-9]+/v' if presence == 'stored' else r'(/values/[0-9]+)/v'
            match = re.fullmatch(pattern, pointer)
            _require(match, 'Invalid numeric source pointer')
            entity_pointer = match.group(1)
            _require(key[0] not in entity_pointers or entity_pointers[key[0]] == entity_pointer,
                     'Numeric entity pointer changed across bindings')
            entity_pointers[key[0]] = entity_pointer
    _require(len(set(entity_pointers.values())) == len(entity_pointers), 'duplicate numeric entity pointer')
    _require(all('entity_not_stored' not in p or p == {'entity_not_stored'} for p in numeric_presence.values()),
             'Inconsistent entity absence across bindings')
    _require(seen == {(c, v) for c in cad for v in bindings}, 'Incomplete financial grid')
    values, decimal_type = _numbers(rows)
    counts = {'cells': len(rows), 'observations': sum(r['presence'] == 'stored' for r in rows),
              'cadaster_records': len(cadastro)}
    _require(all(type(manifest.get(k)) is int and manifest[k] == v for k, v in counts.items()), 'Source count mismatch')
    _require(diagnostics.get('cadaster_records') == len(cadastro), 'Diagnostic cadaster count mismatch')
    coverage = []
    for var in variables:
        selected = [r for r in rows if r['ifd'] == str(var['ifd'])]
        states = Counter(r['presence'] for r in selected)
        states.update(r['value_state'] for r in selected if r['presence'] == 'stored')
        coverage.append(dict(ifd=var['ifd'], lid=var['lid'], td=var['td'],
                             denominator_cadaster_records=len(cadastro), states=dict(states)))
    _require(_dump(coverage) == _dump(diagnostics.get('coverage')), 'Diagnostic coverage mismatch')
    return values, decimal_type, counts


def _connection(directories):
    import duckdb
    con = duckdb.connect(':memory:', config={'threads': 1, 'autoinstall_known_extensions': False,
                                           'autoload_known_extensions': False})
    try:
        con.execute('SET allowed_directories = ?', [[str(Path(p).resolve()) for p in directories]])
        con.execute('SET enable_external_access = false')
    except Exception:
        con.close()
        raise
    return con


def _digest(rows):
    body = json.dumps([[r[k] for k in FIELDS] for r in rows], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return _sha(body)


def _entry(root, name):
    body = _path(root, name).read_bytes()
    return dict(path=name, bytes=len(body), sha256=_sha(body))


def _write_part(rows, numbers, decimal_type, path):
    with _connection([path.parent]) as con:
        fields = ', '.join(f'"{k}" VARCHAR' for k in FIELDS)
        con.execute(f'CREATE TABLE cells ({fields}, numeric_decimal {decimal_type})')
        for start in range(0, len(rows), 4096):
            batch = rows[start:start + 4096]
            arrays = [[r[k] for r in batch] for k in FIELDS]
            arrays.append([format(n, 'f') if n is not None else None for n in numbers[start:start + 4096]])
            columns = ','.join(['unnest(?)'] * len(FIELDS) + [f'CAST(unnest(?) AS {decimal_type})'])
            con.execute('INSERT INTO cells SELECT ' + columns, arrays)
        con.execute('COPY cells TO ? (FORMAT PARQUET, COMPRESSION ZSTD)', [str(path)])
        actual = con.execute('FROM read_parquet(?, hive_partitioning=false)', [str(path)]).fetchall()
    _require(len(actual) == len(rows) and all(tuple(r[k] for k in FIELDS) + (n,) == record
             for r, n, record in zip(rows, numbers, actual)), 'Parquet round-trip differs from original')


def convert_financial(source: Path, destination: Path, *, source_manifest_sha256: str) -> dict:
    source, destination = Path(source).resolve(), Path(destination).absolute()
    body = (source / 'manifest.json').read_bytes()
    _require(isinstance(source_manifest_sha256, str) and HASH.fullmatch(source_manifest_sha256)
             and _sha(body) == source_manifest_sha256, 'Source manifest hash mismatch')
    manifest = _json(body)
    _common(manifest)
    bodies = _files(source, manifest.get('files'), INPUTS)
    metadata = _metadata(manifest, bodies)
    rows = _csv(bodies['financial-cells.csv'], FIELDS)
    numbers, decimal_type, counts = _rows(manifest, rows, metadata)
    observed = _csv(bodies['financial-observations.csv'], FIELDS)
    _require(observed == [r for r in rows if r['presence'] == 'stored'], 'Observation projection differs from stored cells')
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'parts').mkdir()
    (destination / 'metadata').mkdir()
    _write_part(rows, numbers, decimal_type, destination / PART)
    (destination / 'metadata/source-manifest.json').write_bytes(body)
    for name in COMPANIONS:
        (destination / 'metadata' / name).write_bytes(bodies[name])
    import duckdb
    result = dict(contract=CONTRACT, accepted=True, selection=dict(SELECTION),
                  created_utc=datetime.now(timezone.utc).isoformat(), adapter_version='1',
                  adapter_sha256=_sha(Path(__file__).read_bytes().replace(b'\r\n', b'\n')),
                  duckdb_version=duckdb.__version__, source_manifest_sha256=source_manifest_sha256,
                  source_files=manifest['files'], files=[_entry(destination, n) for n in OUTPUTS],
                  original_fields=list(FIELDS), decimal_type=decimal_type, row_digest=_digest(rows),
                  presence_counts=dict(Counter(r['presence'] for r in rows)),
                  value_state_counts=dict(Counter(r['value_state'] for r in rows)),
                  limitations=manifest['limitations'], **counts)
    output = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
    pending = destination / '.manifest.pending'
    with pending.open('xb') as handle:
        handle.write(output)
        handle.flush()
        os.fsync(handle.fileno())
    os.link(pending, destination / 'manifest.json')
    pending.unlink()
    return {**result, 'manifest_sha256': _sha(output)}

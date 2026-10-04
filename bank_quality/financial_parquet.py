"""Exact offline Parquet projection of closed financial202312/202412 admissions."""
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
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import duckdb

from .financial import CONTRACT as SOURCE_CONTRACT, FIELDS, PROFILE_PATH, ROLES, SELECTION, _profile_for_selection
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
    _require(isinstance(manifest, dict) and manifest.get('accepted') is True, 'Unknown source contract or selection')
    context = _profile_for_selection(manifest.get('selection'))
    expected = dict(contract=context['contract'], period=context['period'], perspective='financial', perspective_id=1005, report_id=92)
    _require(all(_dump(manifest.get(k)) == _dump(v) for k, v in expected.items()), 'Invalid source scope')
    for key in ('report_generation', 'report_version'):
        _require(type(manifest.get(key)) is str and manifest.get(key + '_state') ==
                 ('reported_text' if manifest[key] else 'unknown'), 'Invalid generation/version state')
    _require(manifest.get('profile_sha256') == _sha(context['profile_body'].replace(b'\r\n', b'\n')),
             'Unknown admitted profile')
    sources = manifest.get('sources')
    _require(isinstance(sources, dict) and set(sources) == ROLES, 'Invalid source membership')
    for record in sources.values():
        _require(isinstance(record, dict) and isinstance(record.get('body_path'), str) and record['body_path']
                 and all(isinstance(record.get(k), str) and HASH.fullmatch(record[k])
                         for k in ('sha256', 'manifest_sha256')), 'Invalid source provenance')
    for role, pin in context['profile'].get('legacy_sources', {}).items():
        record = sources[role]
        _require(record['sha256'] == pin['body_sha256'] and record['manifest_sha256'] == pin['manifest_sha256']
                 and record.get('truncation_state') == 'undeclared_legacy'
                 and record.get('capture_diagnostics') == pin['diagnostics']
                 and isinstance(record.get('context'), dict)
                 and record['context'].get('body_capture') == pin['body_capture']
                 and _sha(_dump({k: v for k, v in record.items() if k != 'indexed_manifest'}).encode('utf-8'))
                 == pin.get('provenance_sha256'),
                 'Invalid admitted legacy qualification: ' + role)
    _require(isinstance(manifest.get('limitations'), list) and all(type(v) is str for v in manifest['limitations']),
             'Invalid source limitations')
    return {k: str(manifest[k]) for k in COMMON}


def _metadata(manifest, bodies):
    common = _common(manifest)
    context = _profile_for_selection(manifest['selection'])
    period = context['period']
    cad_fields = [*COMMON, *(f'c{i}' for i in range(context['cadaster_fields'])),
                  'source_body', 'source_sha256', 'source_pointer']
    cadastro = _csv(bodies['financial-cadastro.csv'], cad_fields)
    _require(cadastro, 'Empty financial cadaster')
    sources = manifest['sources']
    seen = set()
    for index, row in enumerate(cadastro):
        _require(all(row[k] == v for k, v in common.items()) and row['c1'] == str(period), 'Wrong cadaster scope')
        _require(re.fullmatch(r'0|[1-9][0-9]*', row['c0']) and row['c0'] not in seen,
                 'Invalid or duplicate literal cadaster key')
        seen.add(row['c0'])
        _require(row['source_pointer'] == f'/{index}' and row['source_body'] == sources['cadaster']['body_path']
                 and row['source_sha256'] == sources['cadaster']['sha256'], 'Invalid cadaster provenance')
    document = _json(bodies['financial-variables.json'])
    _require(isinstance(document, dict) and all(str(document.get(k)) == v for k, v in common.items()),
             'Wrong variable scope')
    variables = document.get('variables')
    metrics = context['profile']['metrics']
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
                        window_start=f'{period // 100}-07-01' if info['id'] == 79718 else '', window_end=f'{period // 100}-12-31',
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
    _require(isinstance(diagnostics, dict) and diagnostics.get('contract') == context['contract']
             and _dump(diagnostics.get('selection')) == _dump(context['selection'])
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


def _check_original_csv(rows, source):
    # This closed admission writes UTF-8 CSV, minimal quoting, LF, and FIELDS order.
    # Reconstruct its exact bytes to validate a standalone Parquet against the
    # accepted source hashes, even if an output digest was coherently rewritten.
    entries = {entry['path']: entry for entry in source['files']}
    for name, selected in (('financial-cells.csv', rows),
                           ('financial-observations.csv', [r for r in rows if r['presence'] == 'stored'])):
        output = io.StringIO(newline='')
        writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(selected)
        body = output.getvalue().encode('utf-8')
        _require(len(body) == entries[name]['bytes'] and _sha(body) == entries[name]['sha256'],
                 'Rows differ from original admitted CSV: ' + name)


def _entry(root, name):
    body = _path(root, name).read_bytes()
    return dict(path=name, bytes=len(body), sha256=_sha(body))


def _write_part(rows, numbers, decimal_type, path):
    # Owned transient CSV avoids binding hundreds of thousands of Python objects.
    # Original text columns never match the NULL marker; only numeric_decimal may
    # be NULL. Closed schema and serial reading preserve exact row/column order.
    with tempfile.TemporaryDirectory(prefix='financial-write-', dir=path.parent) as directory:
        image = Path(directory) / 'cells.csv'
        with image.open('x', encoding='utf-8', newline='') as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow(FIELDS + ['numeric_decimal'])
            for row, number in zip(rows, numbers):
                writer.writerow([row[k] for k in FIELDS] + [format(number, 'f') if number is not None else ''])
        with _connection([directory, path.parent]) as con:
            con.execute('SET preserve_insertion_order = true')
            fields = ', '.join(f'"{k}"' for k in FIELDS)
            con.execute('CREATE TABLE cells AS SELECT ' + fields + f', CAST(numeric_decimal AS {decimal_type}) AS numeric_decimal '
                        'FROM read_csv(?, header=true, auto_detect=false, columns=?, delim=\',\', quote=\'"\', escape=\'"\', '
                        'force_not_null=?, nullstr=\'\', parallel=false, strict_mode=true)',
                        [str(image), {k: 'VARCHAR' for k in FIELDS + ['numeric_decimal']}, FIELDS])
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
    context = _profile_for_selection(manifest['selection'])
    period = context['period']
    part = f'parts/financial-cells-{period}.parquet'
    outputs = (part, 'metadata/source-manifest.json', *(f'metadata/{n}' for n in COMPANIONS))
    bodies = _files(source, manifest.get('files'), INPUTS)
    metadata = _metadata(manifest, bodies)
    rows = _csv(bodies['financial-cells.csv'], FIELDS)
    numbers, decimal_type, counts = _rows(manifest, rows, metadata)
    observed = _csv(bodies['financial-observations.csv'], FIELDS)
    _require(observed == [r for r in rows if r['presence'] == 'stored'], 'Observation projection differs from stored cells')
    _check_original_csv(rows, manifest)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'parts').mkdir()
    (destination / 'metadata').mkdir()
    _write_part(rows, numbers, decimal_type, destination / part)
    (destination / 'metadata/source-manifest.json').write_bytes(body)
    for name in COMPANIONS:
        (destination / 'metadata' / name).write_bytes(bodies[name])
    import duckdb
    result = dict(contract=f'ifdata-financial-parquet-{period}-v1', accepted=True, selection=dict(context['selection']),
                  created_utc=datetime.now(timezone.utc).isoformat(), adapter_version='3',
                  adapter_sha256=_sha(Path(__file__).read_bytes().replace(b'\r\n', b'\n')),
                  duckdb_version=duckdb.__version__, source_manifest_sha256=source_manifest_sha256,
                  source_files=manifest['files'], files=[_entry(destination, n) for n in outputs],
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


def _open_snapshot(destination, expected_hash):
    root = Path(destination).resolve()
    body = (root / 'manifest.json').read_bytes()
    _require(isinstance(expected_hash, str) and HASH.fullmatch(expected_hash) and _sha(body) == expected_hash,
             'Snapshot manifest hash mismatch')
    manifest = _json(body)
    _require(isinstance(manifest, dict), 'Unknown snapshot contract/schema/selection')
    context = _profile_for_selection(manifest.get('selection'))
    period = context['period']
    part = f'parts/financial-cells-{period}.parquet'
    outputs = (part, 'metadata/source-manifest.json', *(f'metadata/{n}' for n in COMPANIONS))
    _require(manifest.get('contract') == f'ifdata-financial-parquet-{period}-v1' and manifest.get('accepted') is True
             and manifest.get('original_fields') == FIELDS,
             'Unknown snapshot contract/schema/selection')
    bodies = _files(root, manifest.get('files'), outputs)
    source_body = bodies['metadata/source-manifest.json']
    _require(_sha(source_body) == manifest.get('source_manifest_sha256'), 'Original manifest hash mismatch')
    source = _json(source_body)
    _common(source)
    _require(_dump(source['selection']) == _dump(context['selection']), 'Source/snapshot selection mismatch')
    source_files = source.get('files')
    _require(isinstance(source_files, list) and len(source_files) == len(INPUTS)
             and _dump(source_files) == _dump(manifest.get('source_files')), 'Original file inventory mismatch')
    entries = {}
    for entry in source_files:
        _require(isinstance(entry, dict) and set(entry) == {'path', 'bytes', 'sha256'}
                 and isinstance(entry['path'], str) and entry['path'] in INPUTS and entry['path'] not in entries
                 and type(entry['bytes']) is int and entry['bytes'] >= 0
                 and isinstance(entry['sha256'], str) and HASH.fullmatch(entry['sha256']), 'Invalid original file entry')
        entries[entry['path']] = entry
    companions = {name: bodies[f'metadata/{name}'] for name in COMPANIONS}
    for name, content in companions.items():
        _require(len(content) == entries[name]['bytes'] and _sha(content) == entries[name]['sha256'],
                 'Complement differs from admitted source: ' + name)
    metadata = _metadata(source, companions)
    scratch = Path(__file__).resolve().parents[1] / '.scratch'
    scratch.mkdir(exist_ok=True)
    con = None
    try:
        # Decode precisely the verified bytes in an owned transient image.
        # Neither a source-file swap during opening nor after opening changes
        # the materialized table. Scratch stays inside this project/checkout.
        with tempfile.TemporaryDirectory(prefix='financial-parquet-read-', dir=scratch) as directory:
            image = Path(directory) / 'verified.parquet'
            image.write_bytes(bodies[part])
            con = _connection([directory])
            con.execute('CREATE TABLE financial_data AS FROM read_parquet(?, hive_partitioning=false)', [str(image)])
        description = con.execute('DESCRIBE financial_data').fetchall()
        _require([c[0] for c in description] == FIELDS + ['numeric_decimal']
                 and all(c[1] == 'VARCHAR' for c in description[:-1]), 'Parquet original schema mismatch')
        records = con.execute('FROM financial_data').fetchall()
        rows = [dict(zip(FIELDS, record[:len(FIELDS)])) for record in records]
        numbers, decimal_type, counts = _rows(source, rows, metadata)
        _check_original_csv(rows, source)
        _require(description[-1][1] == decimal_type == manifest.get('decimal_type'), 'Parquet Decimal schema mismatch')
        _require(all(number == record[-1] for number, record in zip(numbers, records)), 'Parquet Decimal values mismatch')
        _require(all(type(manifest.get(k)) is int and manifest[k] == v for k, v in counts.items())
                 and manifest.get('row_digest') == _digest(rows)
                 and manifest.get('presence_counts') == dict(Counter(r['presence'] for r in rows))
                 and manifest.get('value_state_counts') == dict(Counter(r['value_state'] for r in rows))
                 and manifest.get('limitations') == source['limitations'], 'Snapshot counts/digest/limits mismatch')
    except Exception:
        if con is not None:
            con.close()
        raise
    return con, manifest, metadata


def validate_snapshot(destination: Path, *, manifest_sha256: str) -> dict:
    con, manifest, _ = _open_snapshot(destination, manifest_sha256)
    con.close()
    return {**manifest, 'manifest_sha256': manifest_sha256}


def snapshot_connection(destination: Path, *, manifest_sha256: str) -> 'duckdb.DuckDBPyConnection':
    """Open a validated, in-memory financial snapshot. Caller closes the connection."""
    con, manifest, metadata = _open_snapshot(destination, manifest_sha256)
    try:
        cadastro = metadata[1]
        con.execute('CREATE TABLE occurrences (institution_id VARCHAR, entity_locator VARCHAR)')
        con.execute('INSERT INTO occurrences SELECT unnest(?), unnest(?)',
                    [[r['c0'] for r in cadastro], [r['source_pointer'] for r in cadastro]])
        con.execute('CREATE TABLE snapshot_identity (snapshot_id VARCHAR, source_snapshot_id VARCHAR)')
        con.execute('INSERT INTO snapshot_identity VALUES (?, ?)',
                    [manifest_sha256, manifest['source_manifest_sha256']])
        con.execute("CREATE VIEW financial_cells AS SELECT d.*, i.snapshot_id, i.source_snapshot_id, "
                    "o.entity_locator, d.catalog_pointer AS binding_locator, 'single' AS cell_locator "
                    'FROM financial_data d JOIN occurrences o USING (institution_id) CROSS JOIN snapshot_identity i')
        con.execute("CREATE VIEW financial_observations AS SELECT * FROM financial_cells WHERE presence='stored'")
    except Exception:
        con.close()
        raise
    return con

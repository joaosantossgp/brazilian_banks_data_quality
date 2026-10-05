"""Exact, offline projection of the closed four-report financial admission.

The original grade is entirely textual. Fitting bindings have local DECIMAL
types; historical v2 stores wider values as explicit exact text projections.
"""
from collections import Counter
import copy
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
from itertools import islice, zip_longest
import os
from pathlib import Path
import tempfile
from typing import TYPE_CHECKING

from . import financial_reports as admission
from .financial_parquet import HASH, _connection, _dump, _entry, _files, _json, _path, _require, _sha

if TYPE_CHECKING:
    import duckdb

CONTRACT = 'ifdata-financial-reports-parquet-202412-v1'
HISTORICAL_V2 = 'ifdata-financial-reports-historical-parquet-v2'
ENCODING_FIELDS = {'encoding', 'precision', 'scale', 'value_column', 'storage_type'}
FIELDS = admission.FIELDS
PART = 'parts/financial-cells-202412.parquet'
COMPANIONS = ('financial-cadastro.csv', 'financial-variables.json', 'financial-diagnostics.json')
KEYS = ['institution_id', 'report_id', 'catalog_pointer']
MANIFEST_FIELDS = {'contract', 'accepted', 'selection', 'created_utc', 'profile_sha256',
                   'source_manifest_sha256', 'source_files', 'original_fields', 'cells_part',
                   'decimal_type', 'numeric_bindings', 'cells', 'observations', 'cadaster_records',
                   'presence_counts', 'value_state_counts', 'limitations', 'files'}


def _authenticate(body, expected, message):
    _require(isinstance(expected, str) and HASH.fullmatch(expected) and _sha(body) == expected, message)


def _closed_inventory(root, names):
    """Enumerate only to reject extras; never discover/select snapshot inputs."""
    expected = set(names) | {'manifest.json'}
    directories = {str(Path(n).parent).replace('\\', '/') for n in names if '/' in n}
    actual = set()
    for directory, children, files in os.walk(root, followlinks=False):
        base = Path(directory)
        for child in children:
            path = base / child
            relative = path.relative_to(root).as_posix()
            _require(relative in directories and not path.is_symlink() and not path.is_junction(),
                     'Unexpected snapshot directory')
        for name in files:
            path = base / name
            relative = path.relative_to(root).as_posix()
            _require(relative in expected and not path.is_symlink(), 'Unexpected snapshot file')
            actual.add(relative)
    _require(actual == expected, 'Incomplete snapshot inventory')


def _binding_identity(node, context):
    report, column = node['report_id'], node['column_id']
    _require(type(report) is int and report in context['selection']['reports'] and type(column) is int
             and column >= 0, 'Invalid trusted numeric binding identity')
    return f'financial_numeric_r{report}_c{column}'


def _decimal_dimensions(rows):
    scale, integers = 0, 0
    for row in rows:
        if row['numeric_value']:
            number = Decimal(row['numeric_value'])
            _require(number.is_finite(), 'Nonfinite numeric projection')
            digits = number.as_tuple()
            scale = max(scale, max(0, -digits.exponent))
            integers = max(integers, max(0, len(digits.digits) + digits.exponent))
    return max(1, scale + integers), scale


def _decimal_type(rows):
    width, scale = _decimal_dimensions(rows)
    _require(width <= 38, 'Exact binding DECIMAL requires more than 38 digits')
    return f'DECIMAL({width},{scale})'


def _numeric_bindings(validated):
    count = len(validated['cadastro'])
    cells = validated['cells']
    result = []
    dimensions = []
    for position, node in enumerate(validated['variables']['variables']):
        if node['kind'] not in ('money', 'numeric', 'quantity'):
            continue
        name = _binding_identity(node, validated['context'])
        width, scale = _decimal_dimensions(islice(cells, position * count, (position + 1) * count))
        dimensions.append((width, scale))
        decimal_type = f'DECIMAL({width},{scale})' if width <= 38 else None
        result.append({'report_id': node['report_id'], 'column_id': node['column_id'],
                       'catalog_pointer': node['catalog_pointer'], 'kind': node['kind'],
                       'decimal_type': decimal_type, 'view': name, 'path': f'parts/{name}.parquet',
                       'rows': count})
    if any(width > 38 for width, _ in dimensions):
        _require('source_members' in validated['context'], 'Exact binding DECIMAL requires more than 38 digits')
        for binding, (width, scale) in zip(result, dimensions):
            wide = width > 38
            binding.update(encoding='decimal_text_v1' if wide else 'duckdb_decimal',
                           precision=width, scale=scale,
                           value_column='numeric_exact_text' if wide else 'numeric_decimal',
                           storage_type='VARCHAR' if wide else binding['decimal_type'])
    return result


def _outputs(bindings, context):
    return (context['part'], *(b['path'] for b in bindings), 'metadata/source-manifest.json',
            *(f'metadata/{name}' for name in COMPANIONS))


def _records(con, table):
    cursor = con.execute('SELECT * FROM ' + table)
    while batch := cursor.fetchmany(1024):
        yield from batch


def _assert_schema(con, table, fields, decimal_type=None, value_column=None):
    description = con.execute('DESCRIBE ' + table).fetchall()
    expected = [(name, 'VARCHAR') for name in fields]
    if decimal_type is not None or value_column is not None:
        expected.append((value_column or 'numeric_decimal', decimal_type or 'VARCHAR'))
    _require([(c[0], c[1]) for c in description] == expected, 'Parquet physical schema/type mismatch')


def _write_part(path, fields, rows, *, decimal_type=None, value_column=None):
    """Use one owned CSV and explicit VARCHAR parsing, retaining empty strings."""
    numeric_column = value_column or ('numeric_decimal' if decimal_type else None)
    columns = [*fields, *([numeric_column] if numeric_column else [])]
    with tempfile.TemporaryDirectory(prefix='financial-reports-write-', dir=path.parent) as directory:
        image = Path(directory) / 'part.csv'
        with image.open('x', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream, lineterminator='\n')
            writer.writerow(columns)
            writer.writerows(rows())
        with _connection([directory, path.parent]) as con:
            con.execute('SET preserve_insertion_order = true')
            select = ', '.join(f'"{field}"' for field in fields)
            if decimal_type:
                select += f', CAST(numeric_decimal AS {decimal_type}) AS numeric_decimal'
            elif numeric_column:
                select += ', numeric_exact_text'
            con.execute('CREATE TABLE part AS SELECT ' + select +
                        ' FROM read_csv(?, header=true, auto_detect=false, columns=?, delim=\',\', '
                        'quote=\'"\', escape=\'"\', force_not_null=?, nullstr=\'\', parallel=false, strict_mode=true)',
                        [str(image), {name: 'VARCHAR' for name in columns}, list(fields)])
            con.execute('COPY part TO ? (FORMAT PARQUET, COMPRESSION ZSTD)', [str(path)])
            con.execute('CREATE TABLE written AS FROM read_parquet(?, hive_partitioning=false)', [str(path)])
            _assert_schema(con, 'written', fields, decimal_type, value_column)
            expected = rows()
            if decimal_type:
                expected = ((*row[:-1], Decimal(row[-1]) if row[-1] else None) for row in expected)
            elif numeric_column:
                expected = ((*row[:-1], row[-1] or None) for row in expected)
            _require(all(actual == original for actual, original in
                         zip_longest(_records(con, 'written'), expected)), 'Parquet round-trip differs from admission')


def _typed_rows(cells, start, stop, *, encoding='duckdb_decimal'):
    for row in islice(cells, start, stop):
        value = row['numeric_value']
        if value and encoding == 'duckdb_decimal':
            value = format(Decimal(value), 'f')
        yield (*[row[key] for key in KEYS], value)


def _counts(validated):
    cells = validated['cells']
    return {'cells': len(cells), 'observations': len(validated['observations']),
            'cadaster_records': len(validated['cadastro']),
            'presence_counts': dict(Counter(r['presence'] for r in cells)),
            'value_state_counts': dict(Counter(r['value_state'] for r in cells))}


def convert_financial(source: Path, destination: Path, *, source_manifest_sha256: str) -> dict:
    """Convert authenticated admission bytes into a new closed snapshot."""
    source, destination = Path(source).resolve(), Path(destination).absolute()
    if destination.exists():
        raise FileExistsError('Financial destination already exists: ' + str(destination))
    source_body = _path(source, 'manifest.json').read_bytes()
    _authenticate(source_body, source_manifest_sha256, 'Source manifest hash mismatch')
    source_manifest = _json(source_body)
    _require(isinstance(source_manifest, dict), 'Invalid original manifest')
    if source_manifest.get('contract') == 'ifdata-financial-reports-historical-snapshot-v1':
        _require('profile_path' not in source_manifest, 'Caller profile override is forbidden')
    _closed_inventory(source, admission.INPUTS)
    bodies = _files(source, source_manifest.get('files'), admission.INPUTS)
    validated = admission.validate_admission(source_manifest, bodies)
    context = validated['context']
    # These authenticated CSV images are consumed by validation. Keep only the
    # original companions while projecting the materialized, validated cells.
    del bodies['financial-cells.csv'], bodies['financial-observations.csv']
    bindings = _numeric_bindings(validated)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'parts').mkdir()
    (destination / 'metadata').mkdir()
    cells = validated['cells']
    _write_part(destination / context['part'], FIELDS, lambda: (tuple(row[k] for k in FIELDS) for row in cells))
    count = len(validated['cadastro'])
    mapping = {b['catalog_pointer']: b for b in bindings}
    for position, node in enumerate(validated['variables']['variables']):
        if node['catalog_pointer'] not in mapping:
            continue
        binding = mapping[node['catalog_pointer']]
        _write_part(destination / binding['path'], KEYS,
                    lambda p=position, b=binding: _typed_rows(cells, p * count, (p + 1) * count,
                                                            encoding=b.get('encoding', 'duckdb_decimal')),
                    decimal_type=binding['decimal_type'], value_column=binding.get('value_column'))
    (destination / 'metadata/source-manifest.json').write_bytes(source_body)
    for name in COMPANIONS:
        (destination / 'metadata' / name).write_bytes(bodies[name])
    result = {'contract': context['parquet_contract'], 'accepted': True, 'selection': copy.deepcopy(context['selection']),
              'created_utc': datetime.now(timezone.utc).isoformat(),
              'profile_sha256': source_manifest['profile_sha256'], 'source_manifest_sha256': source_manifest_sha256,
              'source_files': source_manifest['files'], 'original_fields': list(FIELDS), 'cells_part': context['part'],
              'decimal_type': 'per_binding', 'numeric_bindings': bindings,
              **_counts(validated), 'limitations': list(source_manifest['limitations']),
              'files': [_entry(destination, name) for name in _outputs(bindings, context)]}
    if any(binding.get('encoding') == 'decimal_text_v1' for binding in bindings):
        result.update(contract=HISTORICAL_V2, numeric_projection='mixed_exact_v1')
    output = (_dump(result) + '\n').encode('utf-8')
    pending = destination / '.manifest.pending'
    pending.write_bytes(output)
    os.link(pending, destination / 'manifest.json')
    pending.unlink()
    return {**result, 'manifest_sha256': _sha(output)}


class _CSVHashWriter:
    """Hash and spool each CSV writer chunk without retaining another CSV image."""
    def __init__(self, stream):
        self.stream = stream
        self.hash = hashlib.sha256()
        self.bytes = 0

    def write(self, text):
        body = text.encode('utf-8')
        self.hash.update(body)
        self.bytes += len(body)
        return self.stream.write(body)


def _original_csv_images(con, directory, source):
    entries = {entry['path']: entry for entry in source['files']}
    names = ('financial-cells.csv', 'financial-observations.csv')
    with (directory / names[0]).open('xb') as all_stream, (directory / names[1]).open('xb') as stored_stream:
        sinks = [_CSVHashWriter(all_stream), _CSVHashWriter(stored_stream)]
        writers = [csv.writer(sink, lineterminator='\n') for sink in sinks]
        for writer in writers:
            writer.writerow(FIELDS)
        presence = FIELDS.index('presence')
        for row in _records(con, 'financial_data'):
            _require(all(type(value) is str for value in row), 'Null/nontext original field')
            writers[0].writerow(row)
            if row[presence] == 'stored':
                writers[1].writerow(row)
        for name, sink in zip(names, sinks):
            _require(sink.bytes == entries[name]['bytes'] and sink.hash.hexdigest() == entries[name]['sha256'],
                     'Rows differ from original admitted CSV: ' + name)
    return {name: (directory / name).read_bytes() for name in names}


def _validate_source(manifest, body, companions, context):
    _authenticate(body, manifest['source_manifest_sha256'], 'Original manifest hash mismatch')
    source = _json(body)
    _require(isinstance(source, dict) and source.get('contract') == context['contract']
             and source.get('accepted') is True, 'Unknown original source contract')
    _require(_dump(source.get('selection')) == _dump(context['selection']), 'Original source selection mismatch')
    if 'source_members' in context:
        _require('profile_path' not in source
                 and source.get('profile_sha256') == context['profile_sha256']
                 and source.get('input_index_sha256') == context['profile']['final_handoff_sha256'],
                 'Unknown historical original profile/lineage')
        admission._check_sources(source.get('sources'), context)
    _require(_dump(source.get('files')) == _dump(manifest['source_files']), 'Original file inventory mismatch')
    entries = source.get('files')
    _require(isinstance(entries, list) and len(entries) == len(admission.INPUTS), 'Invalid original file inventory')
    membership = set()
    for entry in entries:
        _require(isinstance(entry, dict) and set(entry) == {'path', 'bytes', 'sha256'}
                 and isinstance(entry['path'], str) and entry['path'] in admission.INPUTS
                 and entry['path'] not in membership and type(entry['bytes']) is int and entry['bytes'] >= 0
                 and isinstance(entry['sha256'], str) and HASH.fullmatch(entry['sha256']), 'Invalid original file record')
        membership.add(entry['path'])
        if entry['path'] in companions:
            original = companions[entry['path']]
            _require(len(original) == entry['bytes'] and _sha(original) == entry['sha256'], 'Changed admitted complement')
    return source


def _open_snapshot(destination, expected_hash, *, binding_id=None):
    root = Path(destination).resolve()
    body = _path(root, 'manifest.json').read_bytes()
    _authenticate(body, expected_hash, 'Snapshot manifest hash mismatch')
    manifest = _json(body)
    _require(isinstance(manifest, dict) and 'selection' in manifest, 'Unknown snapshot selection')
    v2 = manifest.get('contract') == HISTORICAL_V2
    context = (admission._historical_context(manifest['selection']) if manifest.get('contract') in
               ('ifdata-financial-reports-historical-parquet-v1', HISTORICAL_V2) else admission._context(manifest['selection']))
    _require(set(manifest) == MANIFEST_FIELDS | ({'numeric_projection'} if v2 else set())
             and manifest['contract'] == (HISTORICAL_V2 if v2 else context['parquet_contract'])
             and (not v2 or manifest['numeric_projection'] == 'mixed_exact_v1') and manifest['accepted'] is True
             and manifest['original_fields'] == FIELDS and manifest['cells_part'] == context['part']
             and manifest['decimal_type'] == 'per_binding'
             and manifest['profile_sha256'] == context['profile_sha256'], 'Unknown snapshot contract/schema/profile')
    # Paths and SQL identifiers come only from the installed trusted profile.
    nodes = [node for item in context['profile']['reports'] for node in item['nodes'] if node['kind'] != 'group']
    numeric_nodes = [node for node in nodes if node['kind'] in ('money', 'numeric', 'quantity')]
    if binding_id is not None:
        _require(type(binding_id) is tuple and len(binding_id) == 2 and all(type(v) is int for v in binding_id)
                 and binding_id in {(node['report_id'], node['column_id']) for node in numeric_nodes},
                 'Invalid numeric binding selector')
    trusted = [{'view': _binding_identity(node, context), 'path': f'parts/{_binding_identity(node, context)}.parquet'}
               for node in nodes if node['kind'] in ('money', 'numeric', 'quantity')]
    outputs = _outputs(trusted, context)
    _closed_inventory(root, outputs)
    bodies = _files(root, manifest['files'], outputs)
    companions = {name: bodies[f'metadata/{name}'] for name in COMPANIONS}
    source = _validate_source(manifest, bodies['metadata/source-manifest.json'], companions, context)
    if 'source_members' in context:
        numeric = manifest['numeric_bindings']
        expected = [{'report_id': node['report_id'], 'column_id': node['column_id'],
                     'catalog_pointer': node['catalog_pointer'], 'kind': node['kind'],
                     **binding, 'rows': source['cadaster_records']}
                    for node, binding in zip(numeric_nodes, trusted)]
        _require(isinstance(numeric, list) and len(numeric) == len(expected)
                 and all(isinstance(b, dict) and set(b) == {*e, 'decimal_type'} | (ENCODING_FIELDS if v2 else set())
                         and (b['decimal_type'] is None if v2 and b.get('encoding') == 'decimal_text_v1'
                              else type(b['decimal_type']) is str)
                         and (not v2 or (b['encoding'] in ('duckdb_decimal', 'decimal_text_v1')
                              and type(b['precision']) is int and b['precision'] >= 1
                              and type(b['scale']) is int and 0 <= b['scale'] <= b['precision']
                              and b['value_column'] == ('numeric_exact_text' if b['encoding'] == 'decimal_text_v1' else 'numeric_decimal')
                              and b['storage_type'] == ('VARCHAR' if b['encoding'] == 'decimal_text_v1' else b['decimal_type'])))
                         and _dump({k: b[k] for k in e}) == _dump(e) for b, e in zip(numeric, expected)),
                 'Unknown historical numeric binding membership')
    scratch = Path(__file__).resolve().parents[1] / '.scratch'
    scratch.mkdir(exist_ok=True)
    con = None
    try:
        with tempfile.TemporaryDirectory(prefix='financial-reports-read-', dir=scratch) as directory_name:
            directory = Path(directory_name)
            # Every SQL read uses an owned byte image; mutable external paths are
            # neither followed during validation nor referenced by returned views.
            for number, name in enumerate((context['part'], *(b['path'] for b in trusted))):
                (directory / f'{number}.parquet').write_bytes(bodies.pop(name))
            con = _connection([directory])
            con.execute('SET preserve_insertion_order = true')
            con.execute('CREATE TABLE financial_data AS FROM read_parquet(?, hive_partitioning=false)',
                        [str(directory / '0.parquet')])
            _assert_schema(con, 'financial_data', FIELDS)
            payloads = {**companions, **_original_csv_images(con, directory, source)}
            validated = admission.validate_admission(source, payloads)
            del payloads
            bindings = _numeric_bindings(validated)
            _require(v2 == any(b.get('encoding') == 'decimal_text_v1' for b in bindings),
                     'Historical projection contract/width mismatch')
            _require(_dump(manifest['numeric_bindings']) == _dump(bindings), 'Numeric binding map/type mismatch')
            _require(all(_dump(manifest[key]) == _dump(value) for key, value in _counts(validated).items())
                     and manifest['limitations'] == source['limitations']
                     and manifest['profile_sha256'] == source['profile_sha256'], 'Snapshot counts/provenance/limits mismatch')
            count = len(validated['cadastro'])
            positions = {node['catalog_pointer']: p for p, node in enumerate(validated['variables']['variables'])}
            for number, binding in enumerate(bindings, 1):
                name = binding['view']
                table = name + '_data'
                con.execute('CREATE TABLE ' + table + ' AS FROM read_parquet(?, hive_partitioning=false)',
                            [str(directory / f'{number}.parquet')])
                _assert_schema(con, table, KEYS, binding['decimal_type'], binding.get('value_column'))
                position = positions[binding['catalog_pointer']]
                rows = _typed_rows(validated['cells'], position * count, (position + 1) * count,
                                   encoding=binding.get('encoding', 'duckdb_decimal'))
                if binding['decimal_type'] is None:
                    expected = ((*row[:-1], row[-1] or None) for row in rows)
                else:
                    expected = ((*row[:-1], Decimal(row[-1]) if row[-1] else None) for row in rows)
                _require(all(actual == original for actual, original in
                             zip_longest(_records(con, table), expected)), 'Typed binding keys/order/Decimal mismatch')
            for binding in bindings:
                con.execute('CREATE VIEW ' + binding['view'] + ' AS SELECT * FROM ' + binding['view'] + '_data')
        return con, manifest, validated
    except Exception:
        if con is not None:
            con.close()
        raise


def validate_snapshot(destination: Path, *, manifest_sha256: str) -> dict:
    """Validate all metadata, original CSV hashes and exact physical projections."""
    con, manifest, _ = _open_snapshot(destination, manifest_sha256)
    con.close()
    return {**manifest, 'manifest_sha256': manifest_sha256}


def iter_numeric_decimals(destination: Path, *, manifest_sha256: str, binding_id=None):
    """Yield exact values from one fully validated snapshot; close on early exit.

    Wide historical values are Python Decimals, not native SQL DECIMAL scalars.
    The owned connection is opened lazily and records are read in bounded chunks.
    """
    con, manifest, _ = _open_snapshot(destination, manifest_sha256, binding_id=binding_id)
    try:
        for binding in manifest['numeric_bindings']:
            if binding_id is not None and binding_id != (binding['report_id'], binding['column_id']):
                continue
            wide = binding.get('encoding') == 'decimal_text_v1'
            for institution, report, pointer, value in _records(con, binding['view']):
                yield {'institution_id': institution, 'report_id': binding['report_id'],
                       'column_id': binding['column_id'], 'catalog_pointer': pointer,
                       'numeric_decimal': Decimal(value) if wide and value is not None else value}
    finally:
        con.close()


def snapshot_connection(destination: Path, *, manifest_sha256: str) -> 'duckdb.DuckDBPyConnection':
    """Return a verified in-memory snapshot; caller owns and closes the connection."""
    con, manifest, validated = _open_snapshot(destination, manifest_sha256)
    try:
        con.execute('CREATE TABLE occurrences (institution_id VARCHAR, entity_locator VARCHAR)')
        con.execute('INSERT INTO occurrences SELECT unnest(?), unnest(?)',
                    [[row['c0'] for row in validated['cadastro']], [row['source_pointer'] for row in validated['cadastro']]])
        con.execute('CREATE TABLE snapshot_identity (snapshot_id VARCHAR, source_snapshot_id VARCHAR)')
        con.execute('INSERT INTO snapshot_identity VALUES (?, ?)', [manifest_sha256, manifest['source_manifest_sha256']])
        con.execute("CREATE VIEW financial_cells AS SELECT d.*, i.snapshot_id, i.source_snapshot_id, "
                    "o.entity_locator, d.catalog_pointer AS binding_locator, 'single' AS cell_locator "
                    'FROM financial_data d JOIN occurrences o USING (institution_id) CROSS JOIN snapshot_identity i')
        con.execute("CREATE VIEW financial_observations AS SELECT * FROM financial_cells WHERE presence='stored'")
        con.execute('CREATE TABLE binding_data (report_id VARCHAR, column_id VARCHAR, catalog_pointer VARCHAR, '
                    'parent_pointer VARCHAR, kind VARCHAR, metadata_json VARCHAR, numeric_view VARCHAR, decimal_type VARCHAR)')
        numeric = {binding['catalog_pointer']: binding for binding in manifest['numeric_bindings']}
        for node in validated['variables']['nodes']:
            binding = numeric.get(node['catalog_pointer'], {})
            con.execute('INSERT INTO binding_data VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                        [str(node['report_id']), str(node['column_id']), node['catalog_pointer'], node['parent_pointer'],
                         node['kind'], _dump(node), binding.get('view', ''), binding.get('decimal_type', '')])
        con.execute('CREATE VIEW financial_bindings AS SELECT b.*, i.snapshot_id, i.source_snapshot_id '
                    'FROM binding_data b CROSS JOIN snapshot_identity i')
    except Exception:
        con.close()
        raise
    return con

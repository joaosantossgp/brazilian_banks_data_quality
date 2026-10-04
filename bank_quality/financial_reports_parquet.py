"""Exact, offline projection of the closed four-report financial admission.

The original grade is entirely textual. Each numeric binding has its own exact
physical DECIMAL type and view; no numeric union or global numeric cast exists.
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


def _decimal_type(rows):
    scale, integers = 0, 0
    for row in rows:
        if row['numeric_value']:
            number = Decimal(row['numeric_value'])
            _require(number.is_finite(), 'Nonfinite numeric projection')
            scale = max(scale, max(0, -number.as_tuple().exponent))
            integers = max(integers, max(0, number.adjusted() + 1))
    width = max(1, scale + integers)
    _require(width <= 38, 'Exact binding DECIMAL requires more than 38 digits')
    return f'DECIMAL({width},{scale})'


def _numeric_bindings(validated):
    count = len(validated['cadastro'])
    cells = validated['cells']
    result = []
    for position, node in enumerate(validated['variables']['variables']):
        if node['kind'] not in ('money', 'quantity'):
            continue
        name = _binding_identity(node, validated['context'])
        decimal_type = _decimal_type(islice(cells, position * count, (position + 1) * count))
        result.append({'report_id': node['report_id'], 'column_id': node['column_id'],
                       'catalog_pointer': node['catalog_pointer'], 'kind': node['kind'],
                       'decimal_type': decimal_type, 'view': name, 'path': f'parts/{name}.parquet',
                       'rows': count})
    return result


def _outputs(bindings, context):
    return (context['part'], *(b['path'] for b in bindings), 'metadata/source-manifest.json',
            *(f'metadata/{name}' for name in COMPANIONS))


def _records(con, table):
    cursor = con.execute('SELECT * FROM ' + table)
    while batch := cursor.fetchmany(1024):
        yield from batch


def _assert_schema(con, table, fields, decimal_type=None):
    description = con.execute('DESCRIBE ' + table).fetchall()
    expected = [(name, 'VARCHAR') for name in fields]
    if decimal_type is not None:
        expected.append(('numeric_decimal', decimal_type))
    _require([(c[0], c[1]) for c in description] == expected, 'Parquet physical schema/type mismatch')


def _write_part(path, fields, rows, *, decimal_type=None):
    """Use one owned CSV and explicit VARCHAR parsing, retaining empty strings."""
    columns = [*fields, *(['numeric_decimal'] if decimal_type else [])]
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
            con.execute('CREATE TABLE part AS SELECT ' + select +
                        ' FROM read_csv(?, header=true, auto_detect=false, columns=?, delim=\',\', '
                        'quote=\'"\', escape=\'"\', force_not_null=?, nullstr=\'\', parallel=false, strict_mode=true)',
                        [str(image), {name: 'VARCHAR' for name in columns}, list(fields)])
            con.execute('COPY part TO ? (FORMAT PARQUET, COMPRESSION ZSTD)', [str(path)])
            con.execute('CREATE TABLE written AS FROM read_parquet(?, hive_partitioning=false)', [str(path)])
            _assert_schema(con, 'written', fields, decimal_type)
            expected = rows()
            if decimal_type:
                expected = ((*row[:-1], Decimal(row[-1]) if row[-1] else None) for row in expected)
            _require(all(actual == original for actual, original in
                         zip_longest(_records(con, 'written'), expected)), 'Parquet round-trip differs from admission')


def _typed_rows(cells, start, stop):
    for row in islice(cells, start, stop):
        yield (*[row[key] for key in KEYS], format(Decimal(row['numeric_value']), 'f') if row['numeric_value'] else '')


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
                    lambda p=position: _typed_rows(cells, p * count, (p + 1) * count),
                    decimal_type=binding['decimal_type'])
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


def _open_snapshot(destination, expected_hash):
    root = Path(destination).resolve()
    body = _path(root, 'manifest.json').read_bytes()
    _authenticate(body, expected_hash, 'Snapshot manifest hash mismatch')
    manifest = _json(body)
    _require(isinstance(manifest, dict) and 'selection' in manifest, 'Unknown snapshot selection')
    context = admission._context(manifest['selection'])
    _require(isinstance(manifest, dict) and set(manifest) == MANIFEST_FIELDS
             and manifest['contract'] == context['parquet_contract'] and manifest['accepted'] is True
             and manifest['original_fields'] == FIELDS and manifest['cells_part'] == context['part']
             and manifest['decimal_type'] == 'per_binding'
             and manifest['profile_sha256'] == context['profile_sha256'], 'Unknown snapshot contract/schema/profile')
    # Paths and SQL identifiers come only from the installed trusted profile.
    nodes = [node for item in context['profile']['reports'] for node in item['nodes'] if node['kind'] != 'group']
    trusted = [{'view': _binding_identity(node, context), 'path': f'parts/{_binding_identity(node, context)}.parquet'}
               for node in nodes if node['kind'] in ('money', 'quantity')]
    outputs = _outputs(trusted, context)
    _closed_inventory(root, outputs)
    bodies = _files(root, manifest['files'], outputs)
    companions = {name: bodies[f'metadata/{name}'] for name in COMPANIONS}
    source = _validate_source(manifest, bodies['metadata/source-manifest.json'], companions, context)
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
                _assert_schema(con, table, KEYS, binding['decimal_type'])
                position = positions[binding['catalog_pointer']]
                expected = ((*row[:-1], Decimal(row[-1]) if row[-1] else None) for row in
                            _typed_rows(validated['cells'], position * count, (position + 1) * count))
                _require(all(actual == original for actual, original in
                             zip_longest(_records(con, table), expected)), 'Typed binding keys/order/Decimal mismatch')
                con.execute('CREATE VIEW ' + name + ' AS SELECT * FROM ' + table)
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

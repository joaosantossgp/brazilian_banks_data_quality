"""Offline, exact-token Parquet snapshots; no acquisition or financial inference."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import io
import json
import os
from pathlib import Path
import re

from .inventory import classify

CONTRACT = 'ifdata-inventory-parquet-v1'
FIELDS = ['period', 'source_row', 'institution_id', 'report', 'account', 'variable', 'group',
          'raw_value', 'value_state', 'unit', 'source_mode', 'source_body', 'source_sha256',
          'csv_token', 'csv_body', 'csv_sha256']
COMPANIONS = ['institutions.csv', 'variables.csv', 'missingness.csv', 'structural-presence.csv', 'duplicates.csv', 'inventory.json']
INPUTS = ['observations.csv', *COMPANIONS]
PERIODS = {'201012', '202312', '202412'}

def _sha(body):
    return hashlib.sha256(body).hexdigest()

def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'

def _read_inputs(source):
    bodies = {name: (source / name).read_bytes() for name in INPUTS}
    reader = csv.DictReader(io.StringIO(bodies['observations.csv'].decode('utf-8-sig'), newline=''))
    if reader.fieldnames != FIELDS:
        raise ValueError('Observation headers differ from the accepted inventory contract')
    rows = list(reader)
    if not rows or any(set(row) != set(FIELDS) or any(value is None for value in row.values()) for row in rows):
        raise ValueError('Empty or malformed observation inventory')
    quarters = json.loads(bodies['inventory.json'])['quarters']
    counts = Counter(row['period'] for row in rows)
    if set(counts) - PERIODS or set(counts) != set(quarters):
        raise ValueError('Inventory references are outside the bounded approved scope')
    if any(not quarters[period]['values_complete'] or quarters[period]['observations'] != count for period, count in counts.items()):
        raise ValueError('Inventory counts or completeness do not match observations')
    seen = set()
    for row in rows:
        if row['report'] != 'Resumo':
            raise ValueError('Observation report is outside the approved Resumo scope')
        key = (row['period'], row['source_row'])
        if not row['source_row'].isdigit() or int(row['source_row']) < 1 or key in seen:
            raise ValueError('Invalid or repeated source row locator')
        seen.add(key)
        expected = classify(row['raw_value'])
        if row['value_state'] == 'json_null' and row['raw_value'] == '':
            continue
        if row['value_state'] != expected:
            raise ValueError('Value state is inconsistent with the preserved token')
    return bodies, rows

def _numeric(row):
    return Decimal(row['raw_value']) if row['value_state'] in {'numeric', 'zero'} else None

def _decimal_type(rows):
    numbers = [number for row in rows if (number := _numeric(row)) is not None]
    scale = max((max(0, -number.as_tuple().exponent) for number in numbers), default=0)
    integers = max((max(0, number.adjusted() + 1) for number in numbers), default=0)
    width = max(1, integers + scale)
    if width > 38:
        raise ValueError('Exact DECIMAL requires more than 38 digits; refusing rounding or overflow')
    return f'DECIMAL({width},{scale})'

def _connection(directories):
    import duckdb
    connection = duckdb.connect(':memory:', config={'threads': 1,
                                                    'autoinstall_known_extensions': False,
                                                    'autoload_known_extensions': False})
    connection.execute('SET allowed_directories = ?', [[str(Path(path).resolve()) for path in directories]])
    connection.execute('SET enable_external_access = false')
    return connection

def _write_part(rows, target, decimal_type):
    # Bind column arrays, not floats; normalize numeric tokens with Python Decimal.
    with _connection([target.parent]) as connection:
        columns = ', '.join('"' + name + '" VARCHAR' for name in FIELDS)
        connection.execute(f'CREATE TABLE facts ({columns}, perspective VARCHAR, numeric_value {decimal_type})')
        for start in range(0, len(rows), 4096):
            batch = rows[start:start + 4096]
            values = [[row[name] for row in batch] for name in FIELDS]
            values.append(['individual'] * len(batch))
            values.append([format(value, 'f') if (value := _numeric(row)) is not None else None for row in batch])
            select = ','.join(['unnest(?)'] * (len(FIELDS) + 1) + [f'CAST(unnest(?) AS {decimal_type})'])
            connection.execute('INSERT INTO facts SELECT ' + select, values)
        connection.execute('COPY facts TO ? (FORMAT PARQUET, COMPRESSION ZSTD)', [str(target)])

def _check_equivalence(rows, paths):
    expected = sorted(rows, key=lambda row: (row['period'], int(row['source_row'])))
    with _connection({path.parent for path in paths}) as connection:
        actual = connection.execute('SELECT * FROM read_parquet(?, hive_partitioning=false) ORDER BY period, CAST(source_row AS BIGINT)', [[str(path) for path in paths]]).fetchall()
    if len(actual) != len(expected):
        raise ValueError('Parquet observation count differs from source')
    for source, record in zip(expected, actual):
        if tuple(source[name] for name in FIELDS) != record[:len(FIELDS)] or record[-2] != 'individual' or record[-1] != _numeric(source):
            raise ValueError('Parquet tokens, perspective or exact Decimal differ from source')

def _file_entry(destination, path):
    body = path.read_bytes()
    return {'path': path.relative_to(destination).as_posix(), 'bytes': len(body), 'sha256': _sha(body)}

def _content_digest(rows):
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: (item['period'], int(item['source_row']))):
        digest.update(json.dumps([row[name] for name in FIELDS], ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
        digest.update(b'\n')
    return digest.hexdigest()

def _job_key(hashes):
    return _sha(_json({'contract': CONTRACT, 'inputs': hashes}).encode('utf-8'))

def _snapshot_path(destination, name):
    if not isinstance(name, str) or Path(name).is_absolute() or '\\' in name or ':' in name or '..' in Path(name).parts:
        raise ValueError('Snapshot path is outside the accepted file list')
    path = destination / name
    if not path.resolve().is_relative_to(destination.resolve()):
        raise ValueError('Snapshot path escapes the accepted directory')
    return path

def _validate_manifest(destination, manifest):
    if manifest.get('contract') != CONTRACT or manifest.get('original_fields') != FIELDS or manifest.get('perspective') != 'individual':
        raise ValueError('Unknown snapshot contract or schema')
    hashes = manifest.get('source_hashes', {})
    if set(hashes) != set(INPUTS) or any(not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest) for digest in hashes.values()):
        raise ValueError('Invalid source hash manifest')
    if manifest.get('job_key') != _job_key(hashes):
        raise ValueError('Source hash job key mismatch')
    periods = manifest.get('period_counts', {})
    if not periods or set(periods) - PERIODS:
        raise ValueError('Snapshot period count is outside bounded scope')
    expected_parts = [f'parts/observations-{period}.parquet' for period in sorted(periods)]
    if manifest.get('parquet_files') != expected_parts:
        raise ValueError('Invalid or unlisted Parquet file paths')
    expected_files = set(expected_parts + ['metadata/' + name for name in COMPANIONS])
    entries = manifest.get('files', [])
    if len(entries) != len(expected_files) or {entry['path'] for entry in entries} != expected_files:
        raise ValueError('Snapshot file list is incomplete or duplicated')
    for entry in entries:
        path = _snapshot_path(destination, entry['path'])
        try:
            body = path.read_bytes()
        except OSError as error:
            raise ValueError('Snapshot file is missing or unreadable') from error
        if len(body) != entry['bytes'] or _sha(body) != entry['sha256']:
            raise ValueError('Snapshot file hash or byte size mismatch')
        if entry['path'].startswith('metadata/') and entry['sha256'] != hashes[path.name]:
            raise ValueError('Complementary inventory source hash mismatch')
    paths = [_snapshot_path(destination, name) for name in expected_parts]
    with _connection([destination]) as connection:
        result = connection.execute('SELECT * FROM read_parquet(?, hive_partitioning=false) ORDER BY period, CAST(source_row AS BIGINT)', [[str(path) for path in paths]])
        schema = [(item[0], str(item[1])) for item in result.description]
        expected_schema = [(name, 'VARCHAR') for name in FIELDS + ['perspective']] + [('numeric_value', manifest['numeric_type'])]
        if schema != expected_schema:
            raise ValueError('Parquet schema differs from the accepted contract')
        records = result.fetchall()
    rows = [dict(zip(FIELDS, record[:len(FIELDS)])) for record in records]
    if not rows or len(rows) != manifest['observations'] or dict(Counter(row['period'] for row in rows)) != periods:
        raise ValueError('Snapshot observation count differs from accepted manifest')
    if dict(Counter(row['value_state'] for row in rows)) != manifest['state_counts'] or _content_digest(rows) != manifest['content_sha256']:
        raise ValueError('Snapshot content or state count differs from accepted manifest')
    if _decimal_type(rows) != manifest['numeric_type']:
        raise ValueError('Numeric type differs from the exact source-token profile')
    if any(record[-2] != 'individual' or record[-1] != _numeric(row) for row, record in zip(rows, records)):
        raise ValueError('Snapshot Decimal or perspective differs from source tokens')
    return manifest

def validate_snapshot(destination):
    destination = Path(destination)
    try:
        manifest = json.loads((destination / 'manifest.json').read_text(encoding='utf-8'))
        return _validate_manifest(destination, manifest)
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError('Incomplete or invalid snapshot manifest; refusing acceptance') from error

def snapshot_connection(destination):
    destination = Path(destination)
    manifest = validate_snapshot(destination)
    connection = _connection([destination])
    try:
        paths = [str(_snapshot_path(destination, name)) for name in manifest['parquet_files']]
        connection.read_parquet(paths, hive_partitioning=False).create_view('observations')
        return connection
    except BaseException:
        connection.close()
        raise

def convert_inventory(source, destination, workers=1):
    """Convert a captured inventory into a new, bounded, exact snapshot."""
    import duckdb
    source, destination = Path(source), Path(destination)
    if workers not in (1, 2):
        raise ValueError('Only one or two offline workers are supported')
    bodies, rows = _read_inputs(source)
    decimal_type = _decimal_type(rows)
    source_hashes = {name: _sha(body) for name, body in bodies.items()}
    try:
        destination.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        if not (destination / 'manifest.json').is_file():
            raise ValueError('Destination is reserved, busy or incomplete; inspect and use a new destination') from None
        manifest = validate_snapshot(destination)
        if manifest['source_hashes'] != source_hashes:
            raise ValueError('Accepted destination belongs to different source inputs')
        if manifest['content_sha256'] != _content_digest(rows):
            raise ValueError('Accepted source content differs from inputs')
        return manifest
    try:
        return _publish(source, destination, workers, bodies, rows, source_hashes, decimal_type, duckdb.__version__)
    except Exception as error:
        (destination / 'failure.json').write_text(_json({'status': 'failed_not_accepted', 'error_type': type(error).__name__}), encoding='utf-8')
        raise

def _publish(source, destination, workers, bodies, rows, source_hashes, decimal_type, duckdb_version):
    (destination / 'publication.lock').write_text(_json({'job_key': _job_key(source_hashes), 'reservation': 'exclusive_destination_mkdir'}), encoding='utf-8')
    parts, metadata = destination / 'parts', destination / 'metadata'
    parts.mkdir()
    metadata.mkdir()
    paths = []
    for period in sorted({row['period'] for row in rows}):
        path = parts / f'observations-{period}.parquet'
        paths.append(path)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = [pool.submit(_write_part, [row for row in rows if row['period'] == period], path, decimal_type)
                for period, path in zip(sorted({row['period'] for row in rows}), paths)]
        for job in jobs:
            job.result()
    for name in COMPANIONS:
        (metadata / name).write_bytes(bodies[name])
    _check_equivalence(rows, paths)
    if any(_sha((source / name).read_bytes()) != digest for name, digest in source_hashes.items()):
        raise ValueError('Source inventory changed during conversion')
    manifest = {'contract': CONTRACT, 'created_utc': datetime.now(timezone.utc).isoformat(),
                'duckdb_version': duckdb_version, 'perspective': 'individual',
                'job_key': _job_key(source_hashes), 'content_sha256': _content_digest(rows),
                'original_fields': FIELDS, 'numeric_type': decimal_type,
                'source_hashes': source_hashes, 'observations': len(rows),
                'period_counts': dict(Counter(row['period'] for row in rows)),
                'state_counts': dict(Counter(row['value_state'] for row in rows)),
                'parquet_files': [path.relative_to(destination).as_posix() for path in paths],
                'files': [_file_entry(destination, path) for path in paths + [metadata / name for name in COMPANIONS]]}
    _validate_manifest(destination, manifest)
    pending = destination / 'manifest.pending.json'
    with pending.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(_json(manifest))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, destination / 'manifest.json')
    return manifest

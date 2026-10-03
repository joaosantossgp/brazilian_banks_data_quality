"""Bounded offline pilot conversion, replay and storage evidence (no acquisition)."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality.parquet import INPUTS, convert_inventory, snapshot_connection, validate_snapshot
from bank_quality.replay import replay

def hashes(directory):
    return {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in directory.rglob('*') if path.is_file()}

def sizes(directory):
    groups = Counter()
    for path in directory.rglob('*'):
        if path.is_file():
            groups[path.suffix.lower() or '<no extension>'] += path.stat().st_size
    return {'total_bytes': sum(groups.values()), 'bytes_by_extension': dict(sorted(groups.items()))}

def run(repo, output, report, resume=False, measurements=None):
    repo = repo.resolve()
    output = (output if output.is_absolute() else repo / output).resolve()
    report = (report if report.is_absolute() else repo / report).resolve()
    if not output.is_relative_to(repo):
        raise ValueError('Benchmark destination must be within this repository')
    source = repo / 'data/derived/expansion-20261001/inventory'
    collection = repo / 'data/derived/expansion-20261001/collection.json'
    document = json.loads(collection.read_text(encoding='utf-8'))
    for item in [document, *document['quarters'].values()]:
        if 'raw_directory' in item and not Path(item['raw_directory']).resolve().is_relative_to(repo):
            raise ValueError('Archived collection references a raw directory outside this repository')
    if report.exists():
        raise ValueError('Report destination exists; preserve it and select a new report')
    before_raw = hashes(repo / 'data/raw')
    before_inputs = hashes(source)
    before_derived = sizes(repo / 'data/derived')
    if resume:
        accepted = validate_snapshot(output / 'snapshot')
        if accepted['source_hashes'] != before_inputs:
            raise ValueError('Resume source inputs differ from the accepted snapshot')
    else:
        output.mkdir(parents=True, exist_ok=False)
    replay_directory = output / 'replay-verification'
    started = time.perf_counter()
    if resume:
        replay_result = json.loads((replay_directory / 'inventory.json').read_text(encoding='utf-8'))
        replay_seconds = None
    else:
        replay_result = replay(collection, replay_directory)
        replay_seconds = time.perf_counter() - started
    if any((source / name).read_bytes() != (replay_directory / name).read_bytes() for name in INPUTS):
        raise ValueError('Offline replay differs from the accepted inventory')
    replay_verification_seconds = time.perf_counter() - started
    attempts = []
    active = output / 'snapshot'
    benchmark_session = output / 'benchmark' / ('session-' + uuid.uuid4().hex[:12])
    if measurements is not None:
        if not resume or len(measurements) != 2 or {item['workers'] for item in measurements} != {1, 2}:
            raise ValueError('Recovery requires two completed runs, one per worker setting')
        for item in measurements:
            if not math.isfinite(item['seconds']) or item['seconds'] <= 0:
                raise ValueError('Invalid completed-run timing')
            destination = (repo / item['destination']).resolve()
            if not destination.is_relative_to(output):
                raise ValueError('Recovered measurement path escapes the run directory')
            manifest = validate_snapshot(destination)
            if manifest['source_hashes'] != before_inputs or manifest['content_sha256'] != item['content_sha256']:
                raise ValueError('Recovered measurements differ from accepted source inventory')
            if sizes(destination)['total_bytes'] != item['snapshot_bytes']:
                raise ValueError('Recovered snapshot size differs from measurement')
        attempts = measurements
    else:
        # One bounded observation per setting; not a statistical performance claim.
        benchmark_session.mkdir(parents=True, exist_ok=False)
        for index, workers in enumerate([1, 2]):
            destination = active if index == 0 and not resume else benchmark_session / f'run-{index + 1}-workers-{workers}'
            started = time.perf_counter()
            manifest = convert_inventory(source, destination, workers=workers)
            seconds = time.perf_counter() - started
            validate_snapshot(destination)
            if attempts and manifest['content_sha256'] != attempts[0]['content_sha256']:
                raise ValueError('Worker runs differ in source content')
            item = {'workers': workers, 'seconds': seconds, 'content_sha256': manifest['content_sha256'],
                    'snapshot_bytes': sizes(destination)['total_bytes'], 'destination': destination.relative_to(repo).as_posix()}
            attempts.append(item)
            with (benchmark_session / 'completed-runs.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(item, ensure_ascii=False) + '\n')
            print(json.dumps({'completed_run': index + 1, 'workers': workers, 'seconds': round(seconds, 4)}, ensure_ascii=True), flush=True)
    before_reuse = {path.relative_to(active).as_posix(): [hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns]
                    for path in active.rglob('*') if path.is_file()}
    started = time.perf_counter()
    reused = convert_inventory(source, active)
    reuse_seconds = time.perf_counter() - started
    after_reuse = {path.relative_to(active).as_posix(): [hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns]
                   for path in active.rglob('*') if path.is_file()}
    if before_reuse != after_reuse:
        raise ValueError('Idempotent reuse changed files or modification times')
    queries = {}
    opened = time.perf_counter()
    with snapshot_connection(active) as connection:
        connection_open_seconds = time.perf_counter() - opened
        sql_queries = {
            'states': 'SELECT period, value_state, count(*) FROM observations GROUP BY period, value_state ORDER BY period, value_state',
            'numeric_selection': "SELECT period, institution_id, account, numeric_value FROM observations WHERE period='202412' AND value_state IN ('numeric','zero') ORDER BY institution_id, account",
        }
        for name, sql in sql_queries.items():
            query_timings = []
            result = None
            for _ in range(5):
                started = time.perf_counter()
                result = connection.execute(sql).fetchall()
                query_timings.append(time.perf_counter() - started)
            queries[name] = {'sql': sql, 'seconds': query_timings, 'median_seconds': statistics.median(query_timings), 'returned_rows': len(result)}
            if name == 'states':
                queries[name]['result'] = result
    if hashes(repo / 'data/raw') != before_raw or hashes(source) != before_inputs:
        raise ValueError('Protected raw files or accepted source inventories changed')
    benchmark_roots = [path.parent for path in (output / 'benchmark').rglob('publication.lock')]
    accepted_benchmark_bytes = sum(sizes(path)['total_bytes'] for path in benchmark_roots if (path / 'manifest.json').exists())
    retained_incomplete = [{'destination': path.relative_to(repo).as_posix(), **sizes(path)}
                           for path in benchmark_roots if not (path / 'manifest.json').exists()]
    output_bytes = sizes(output)['total_bytes']
    environment_bytes = sizes(repo / '.venv')['total_bytes']
    measurements = {
        'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'offline existing pilot only',
        'active_snapshot': active.relative_to(repo).as_posix(), 'observations': reused['observations'],
        'period_counts': reused['period_counts'], 'state_counts': reused['state_counts'],
        'numeric_type': reused['numeric_type'], 'source_hashes': before_inputs,
        'content_sha256': reused['content_sha256'],
        'raw_files_preserved': len(before_raw), 'raw_and_source_hashes_unchanged': True,
        'replay': {'byte_identical_inventory_files': len(INPUTS), 'seconds': replay_seconds,
                   'reexecuted_in_this_measurement': not resume, 'verification_seconds': replay_verification_seconds,
                   'observations': sum(item['observations'] for item in replay_result['quarters'].values())},
        'idempotency': {'files_and_mtime_unchanged': True, 'seconds': reuse_seconds},
        'conversion_runs': attempts,
        'measurements_recovered_from_prior_completed_runs': measurements is not None,
        'sample_count_by_workers': {str(workers): 1 for workers in (1, 2)},
        'conversion_median_seconds': {str(workers): statistics.median(attempt['seconds'] for attempt in attempts if attempt['workers'] == workers) for workers in (1, 2)},
        'query_connection_open_and_validation_seconds': connection_open_seconds, 'queries': queries,
        'storage': {'raw_all': sizes(repo / 'data/raw'), 'existing_derived_all_before': before_derived,
                    'source_inventory': sizes(source), 'active_snapshot': sizes(active),
                    'replay_duplicate': sizes(replay_directory), 'benchmark_duplicate_snapshots': sizes(output / 'benchmark'),
                    'accepted_benchmark_duplicate_bytes': accepted_benchmark_bytes,
                    'retained_incomplete_staging': retained_incomplete,
                    'new_data_plus_project_environment_bytes': output_bytes + environment_bytes,
                    'new_output_all': sizes(output), 'project_environment': sizes(repo / '.venv')},
        'limits': ['Logical file bytes, not filesystem allocated space or peak RSS/temp use.',
                   'One conversion per worker setting, one machine; no statistical speedup or full-history extrapolation.',
                   'Queries use one validated in-memory connection; timings include fetch and warm filesystem caches.',
                   'DECIMAL preserves accepted CSV values; no claim of repairing earlier float precision in inventory generation.',
                   'Existing raw and CSV/JSON remain; benchmark/replay copies retained and consume extra space.',
                   'No .duckdb database copy, acquisition, external publication or other project access.'],
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(measurements, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'observations': measurements['observations'], 'replay_files': len(INPUTS),
                      'numeric_type': measurements['numeric_type'], 'storage': measurements['storage'],
                      'conversion_median_seconds': measurements['conversion_median_seconds']}, ensure_ascii=True), flush=True)
    return measurements

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--resume', action='store_true', help='Verify an existing accepted snapshot/replay and run new isolated measurements')
    parser.add_argument('--measurements', type=Path, help='Finalize only: JSON list of completed, validated run receipts; requires --resume')
    args = parser.parse_args()
    measurements = json.loads(args.measurements.read_text(encoding='utf-8')) if args.measurements else None
    run(args.repo, args.output, args.report, args.resume, measurements)

if __name__ == '__main__':
    main()

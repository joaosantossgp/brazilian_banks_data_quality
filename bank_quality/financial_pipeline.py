"""Offline window authoring and measured, resumable financial execution.

Profiles are candidates until an external integrator installs the exact proposal.
No network, acquisition recovery, install, review flag or numeric harmonization.
"""
from collections import Counter
import copy
import csv
from decimal import Decimal
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import time

from . import financial_report_profiles as profiles
from . import financial_reports as admission
from . import financial_reports_parquet as parquet
from . import financial_parquet as conversion
from . import windows_acquisition as native
from . import windows_financial_pipeline as contained

PLAN = 'ifdata-financial-sanitization-plan-v1'
PLAN_V2 = 'ifdata-financial-sanitization-plan-v2'
PREPARE_V1 = 'ifdata-financial-sanitization-prepare-v1'
PREPARE_V2 = 'ifdata-financial-sanitization-prepare-v2'
RESULT = 'ifdata-financial-sanitization-result-v1'
STAGE_RESULT = 'ifdata-financial-sanitization-stage-result-v1'
_CODE_ROOT = Path(__file__).resolve().parents[1]
_WINDOW = (202406, 202409, 202506, 202509, 202512, 202603, 202606)
_STAGES = ('admit', 'convert', 'query', 'replay-admit', 'replay-convert', 'replay-query', 'compare')
_RESOURCE_KEYS = {'deadline_seconds', 'min_available_physical_bytes', 'min_available_commit_bytes',
                  'min_free_disk_bytes', 'sample_interval_seconds'}


def _is_plan(doc):
    return doc.get('contract') in (PLAN, PLAN_V2)


def _historical_periods(batch):
    from . import financial_acquisition_batch as acquisition
    bundle = _read(batch['bundle'])
    _require(bundle.get('contract') == 'financial-acquisition-batch-v2'
             and bundle.get('policy_sha256') == acquisition._HISTORICAL_POLICY_SHA256,
             'Historical pipeline requires authenticated policy bundle')
    windows = [w for w in acquisition._HISTORICAL_POLICY_V1['windows']
               if w['window_id'] == bundle.get('window_id')]
    _require(len(windows) == 1, 'Historical pipeline window requires canonical policy derivation')
    window = windows[0]
    _require(bundle['acquire_periods'] == window['periods'] and bundle['scope'] == window['scope']
             and bundle['destination'] == window['destination'], 'Historical bundle window differs from policy')
    if 'window_id' in batch or 'policy_sha256' in batch:
        _require(batch.get('window_id') == window['window_id']
                 and batch.get('policy_sha256') == bundle['policy_sha256'], 'Historical plan window identity differs')
    return list(window['periods'])


def _periods(doc):
    if doc.get('contract') in (PREPARE_V2, PLAN_V2):
        return _historical_periods(doc['batch'])
    _require(doc.get('contract') in (PREPARE_V1, PLAN), 'Unsupported pipeline document')
    return list(_WINDOW)


def _authenticate_absent(names):
    for name in names:
        try:
            _path(name).lstat()
        except FileNotFoundError:
            continue
        raise IntegrityError('Historical capture halt marker present: ' + name)


class IntegrityError(ValueError):
    """An explicit trust-chain failure: halt the whole batch."""


class StageError(admission.NativeSchemaError):
    """A local reader/schema failure, after all trust checks succeeded."""
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def _global_error(error):
    code = ('integrity' if isinstance(error, IntegrityError) else
            'resource' if isinstance(error, contained.ResourceError) else 'unexpected')
    return {'code': code, 'message': type(error).__name__ + ': ' + str(error)}


def _require(value, message):
    if not value:
        raise IntegrityError(message)


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _dump(value):
    return profiles._canonical(value).encode('utf-8')


def validate_resources(value):
    if type(value) is not dict or set(value) != _RESOURCE_KEYS:
        raise ValueError('Resource policy must have exactly the five machine-specific fields')
    for key, number in value.items():
        if (type(number) not in (int, float) or not math.isfinite(number) or number <= 0
                or (key.endswith('_bytes') and type(number) is not int)):
            raise ValueError('Resource policy must be finite, positive and typed: ' + key)
    return copy.deepcopy(value)


def _path(name):
    try:
        return profiles._contained(profiles.CHECKOUT_ROOT, name)
    except ValueError as error:
        raise IntegrityError(str(error)) from error


def _name(path):
    path = Path(path).absolute()
    _require(path.is_relative_to(profiles.CHECKOUT_ROOT.absolute()), 'Path outside fixed checkout')
    name = path.relative_to(profiles.CHECKOUT_ROOT.absolute()).as_posix()
    _path(name)
    return name


def _read(ref):
    _require(type(ref) is dict and set(ref) == {'path', 'sha256'}, 'Invalid closed file reference')
    try:
        body, _ = profiles._read_hashed(_path(ref['path']), ref['sha256'])
        value = json.loads(body, object_pairs_hook=profiles.legacy._pairs,
                           parse_constant=profiles.legacy._constant)
    except (OSError, ValueError) as error:
        raise IntegrityError('Authenticated file failed: ' + str(ref.get('path'))) from error
    return value


def _ref(path):
    return {'path': _name(path), 'sha256': _sha(Path(path).read_bytes())}


def _publish(path, value):
    path = Path(path)
    _name(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(_dump(value))
        stream.flush()
        os.fsync(stream.fileno())
    return _ref(path)


def _payloads(directory, manifest):
    _require(type(manifest.get('files')) is list, 'Missing payload inventory')
    names = [e.get('path') for e in manifest['files']]
    _require(len(names) == len(set(names)), 'Duplicate payload path')
    found = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    _require(found == set(names) | {'manifest.json'}, 'Payload inventory has missing/extra files')
    values = {}
    for entry in manifest['files']:
        path = profiles._contained(directory, entry['path'])
        raw = path.read_bytes()
        _require(len(raw) == entry['bytes'] and _sha(raw) == entry['sha256'], 'Payload digest mismatch: ' + entry['path'])
        values[entry['path']] = raw
    return values


def verify_query(source: Path, destination: Path, *, source_manifest_sha256: str, manifest_sha256: str) -> dict:
    """Two serial owned images: the query connection, then the Decimal iterator."""
    source, destination = Path(source), Path(destination)
    sm = _read(_ref(source / 'manifest.json'))
    _require(_sha((source / 'manifest.json').read_bytes()) == source_manifest_sha256, 'Admission pin mismatch')
    bodies = _payloads(source, sm)
    pm = _read({'path': _name(destination / 'manifest.json'), 'sha256': manifest_sha256})
    _require(pm['source_manifest_sha256'] == source_manifest_sha256, 'Projection/admission link mismatch')
    cells_body = bodies['financial-cells.csv']
    del bodies
    state_counts = {field: Counter() for field in ('presence', 'value_state')}
    for row in admission._iter_csv_bytes(cells_body, admission.FIELDS):
        for field, counts in state_counts.items():
            counts[row[field]] += 1
    row = None  # Release the final external row before opening the owned snapshot.
    con = parquet.snapshot_connection(destination, manifest_sha256=manifest_sha256)
    try:
        schema = con.execute('DESCRIBE financial_data').fetchall()
        _require([(r[0], r[1]) for r in schema] == [(f, 'VARCHAR') for f in admission.FIELDS], 'Grade must retain all 32 VARCHAR fields')
        for table, count in (('financial_cells', sm['cells']), ('financial_observations', sm['observations']),
                             ('financial_bindings', len(json.loads((source / 'financial-variables.json').read_bytes())['nodes'])),
                             ('occurrences', sm['cadaster_records'])):
            _require(con.execute('SELECT count(*) FROM ' + table).fetchone()[0] == count, 'Query count mismatch: ' + table)
        for field, key in (('presence', 'presence_counts'), ('value_state', 'value_state_counts')):
            actual = dict(con.execute('SELECT ' + field + ',count(*) FROM financial_data GROUP BY ' + field).fetchall())
            _require(actual == dict(state_counts[field]) == pm[key], 'Query state mismatch: ' + field)
        for binding in pm['numeric_bindings']:
            table = binding['view']
            description = con.execute('DESCRIBE ' + table).fetchall()
            value_name = binding.get('value_column', 'numeric_decimal')
            storage = binding.get('storage_type', binding['decimal_type'])
            _require([(r[0], r[1]) for r in description] == [(f, 'VARCHAR') for f in parquet.KEYS] + [(value_name, storage)],
                     'Typed binding schema mismatch')
            _require(con.execute('SELECT count(*) FROM ' + table).fetchone()[0] == sm['cadaster_records'], 'Typed binding count mismatch')
    finally:
        con.close()
    bindings = {binding['catalog_pointer']: binding for binding in pm['numeric_bindings']}
    def expected_values():
        # The adapter validates binding order against the authoritative variable
        # order. The admitted grade has that same binding-major order.
        for row in admission._iter_csv_bytes(cells_body, admission.FIELDS):
            binding = bindings.get(row['catalog_pointer'])
            if binding is not None:
                yield {'institution_id': row['institution_id'], 'report_id': binding['report_id'],
                    'column_id': binding['column_id'], 'catalog_pointer': row['catalog_pointer'],
                    'numeric_decimal': Decimal(row['numeric_value']) if row['numeric_value'] else None}
    from itertools import zip_longest
    actual = parquet.iter_numeric_decimals(destination, manifest_sha256=manifest_sha256)
    checked = 0
    try:
        for got, want in zip_longest(actual, expected_values()):
            _require(got == want, 'Decimal accessor identity/order/value mismatch')
            checked += 1
    finally:
        actual.close()
    with (source / 'financial-cadastro.csv').open(encoding='utf-8-sig', newline='') as stream:
        columns = next(csv.reader(stream))[4:-3]
    return {'source_manifest_sha256': source_manifest_sha256, 'manifest_sha256': manifest_sha256,
            'query_verified': True, 'numeric_rows': checked, 'cells': sm['cells'], 'observations': sm['observations'],
            'cadaster_records': sm['cadaster_records'], 'cadaster_columns': len(columns),
            'bindings': len(pm['numeric_bindings']), 'presence_counts': pm['presence_counts'],
            'value_state_counts': pm['value_state_counts'],
            'precision_encodings': dict(Counter(b.get('encoding', 'duckdb_decimal') for b in pm['numeric_bindings']))}


def compare_replay(source: Path, replay_source: Path, destination: Path, replay_destination: Path) -> dict:
    """Normalize only execution dates and their proven direct hash derivatives."""
    sources = [Path(source), Path(replay_source)]
    projections = [Path(destination), Path(replay_destination)]
    sm = [_read(_ref(p / 'manifest.json')) for p in sources]
    sb = [_payloads(p, m) for p, m in zip(sources, sm)]
    clean = lambda value: {k: v for k, v in value.items() if k != 'created_utc'}
    _require(clean(sm[0]) == clean(sm[1]), 'Replay admission differs beyond created_utc')
    _require(sb[0] == sb[1], 'Replay admission payload bytes differ')
    pm = [_read(_ref(p / 'manifest.json')) for p in projections]
    pb = [_payloads(p, m) for p, m in zip(projections, pm)]
    for i in (0, 1):
        original = (sources[i] / 'manifest.json').read_bytes()
        _require(pb[i].get('metadata/source-manifest.json') == original
                 and pm[i]['source_manifest_sha256'] == _sha(original), 'Replay source manifest is not the exact corresponding admission')
    normalized = []
    for i in (0, 1):
        value = clean(copy.deepcopy(pm[i]))
        value['source_manifest_sha256'] = _sha(_dump(clean(sm[i])))
        image = _dump(clean(sm[i]))
        for entry in value['files']:
            if entry['path'] == 'metadata/source-manifest.json':
                entry.update(bytes=len(image), sha256=_sha(image))
        normalized.append(value)
        pb[i]['metadata/source-manifest.json'] = image
    _require(normalized[0] == normalized[1], 'Replay Parquet metadata differs')
    _require(pb[0] == pb[1], 'Replay Parquet payload bytes differ')
    return {'replay_verified': True, 'admission_files': len(sb[0]), 'parquet_files': len(pb[0]),
            'primary_admission': _ref(sources[0] / 'manifest.json'), 'replay_admission': _ref(sources[1] / 'manifest.json'),
            'primary_parquet': _ref(projections[0] / 'manifest.json'), 'replay_parquet': _ref(projections[1] / 'manifest.json')}


def _stream_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _authenticate_files(images):
    _require(type(images) is list and len({p['path'] for p in images}) == len(images), 'Duplicate integrity images')
    for image in images:
        path = _path(image['path'])
        _require(path.is_file() and _stream_sha(path) == image['sha256'], 'Integrity image changed: ' + image['path'])
        if 'bytes' in image:
            _require(path.stat().st_size == image['bytes'], 'Integrity image size changed')


def _code_pins(resources):
    names = ('financial_pipeline', 'windows_financial_pipeline', 'financial_report_profiles', 'financial_reports',
             'financial_reports_parquet', 'financial_parquet', 'financial', 'archive', 'financial_acquisition',
             'financial_acquisition_batch', 'windows_acquisition')
    return {'application': {'path': str(Path(sys.executable).resolve()), 'sha256': _stream_sha(sys.executable)},
            'modules': [{'path': 'bank_quality/' + name + '.py',
                         'sha256': _stream_sha(_CODE_ROOT / ('bank_quality/' + name + '.py'))} for name in names],
            'resources_sha256': _sha(_dump(resources))}


def _check_code(pins, resources):
    _require(pins == _code_pins(resources), 'Current Python/code/resource policy differs from external plan pins')


def _registry_name():
    return _name(profiles.PACKAGE_ROOT / 'financial-reports-registry.json')


def _source_checks(plan, *, installed):
    images = []
    source_images = plan['source_state_files']
    if plan['contract'] == PLAN_V2:
        source_images = _global_source_images(source_images, [_read(m['final_handoff']) for m in plan['members']])
    for image in source_images:
        if image['path'] == _registry_name():
            expected = plan['registry_proposed']['sha256'] if installed else plan['registry_before_sha256']
            images.append({'path': image['path'], 'sha256': expected})
        else:
            images.append(image)
    _authenticate_files(images)
    if plan['contract'] == PLAN_V2:
        _authenticate_absent(plan['source_state_absent'])
    if plan.get('accepted_supplement'):
        supplement = _read(plan['accepted_supplement'])
        _authenticate_files([ref for member in supplement['members'] for ref in member['evidence'].values()])


def _member_paths(output, period):
    base = output + '/members/' + str(period)
    tag = Path(output).name + '-' + str(period)
    return {'metadata_handoff': base + '/checkpoint-a.json', 'final_handoff': base + '/checkpoint-b.json',
            'candidate': base + '/candidate.json', 'profile': base + '/profile.json', 'summary': base + '/summary.json',
            'admission': 'data/derived/' + tag, 'parquet': 'data/curated/' + tag,
            'replay_admission': 'data/derived/' + tag + '-replay', 'replay_parquet': 'data/curated/' + tag + '-replay',
            'query': output + '/execution/queries/' + str(period) + '.json',
            'replay_query': output + '/execution/queries/' + str(period) + '-replay.json',
            'compare': output + '/execution/queries/' + str(period) + '-compare.json'}


def _validate_supplement(ref):
    if ref is None:
        return {'additional_accepted': 0, 'files': []}
    value = _read(ref)
    _require(type(value) is dict and set(value) == {'contract', 'members', 'limitations'}
             and value['contract'] == 'ifdata-financial-accepted-supplement-v1'
             and type(value['members']) is list and len(value['members']) == 1, 'Invalid accepted supplement')
    member = value['members'][0]
    selection = {'period': 202403, 'perspective': 1005, 'reports': [92, 96, 101, 98]}
    names = {'profile', 'admission', 'parquet', 'replay_admission', 'replay_parquet', 'query', 'replay_query', 'compare'}
    _require(type(member) is dict and set(member) == {'selection', 'evidence'}
             and member['selection'] == selection and set(member['evidence']) == names, 'Supplement must prove the separate native202403')
    evidence = member['evidence']
    docs = {key: _read(image) for key, image in evidence.items()}
    for key in ('profile', 'admission', 'parquet', 'replay_admission', 'replay_parquet'):
        _require(docs[key].get('selection') == selection, 'Supplement snapshot selection differs')
    for key in ('admission', 'replay_admission'):
        _require(docs[key].get('accepted') is True and docs[key]['profile_sha256'] == evidence['profile']['sha256'],
                 'Supplement installed profile/admission link differs')
    for prefix in ('', 'replay_'):
        pm, sm, query = docs[prefix + 'parquet'], docs[prefix + 'admission'], docs[prefix + 'query']
        _require(pm.get('accepted') is True and pm['source_manifest_sha256'] == evidence[prefix + 'admission']['sha256']
                 and pm['source_files'] == sm['files'] and pm['profile_sha256'] == sm['profile_sha256'], 'Supplement projection link differs')
        _require(query.get('contract') == 'root-offline-financial-gate-stage-v1'
                 and query.get('stage') == ('replay-query' if prefix else 'query')
                 and query.get('manifest_sha256') == evidence[prefix + 'parquet']['sha256']
                 and query.get('grade_columns') == 32 and query.get('grade_all_varchar') is True
                 and query.get('all_original_csvs_origins_and_decimal_rows_validated_by_adapter') is True
                 and query.get('accessor_snapshots_opened') == 1 and query.get('http_requests') == 0,
                 'Supplement query proof differs')
        for key in ('cells', 'observations', 'cadaster_records', 'presence_counts', 'value_state_counts'):
            _require(query.get(key) == pm[key], 'Supplement query count/state differs')
        expected = [{'view': b['view'], 'rows': pm['cadaster_records'], 'encoding': b.get('encoding', 'duckdb_decimal'),
                     'storage_type': b.get('storage_type', b['decimal_type'])} for b in pm['numeric_bindings']]
        _require(query.get('typed_views_checked') == expected
                 and query.get('exact_python_decimal_rows_checked') == len(expected) * pm['cadaster_records']
                 and query.get('cadaster_columns') == len(docs['profile']['cadaster_columns'])
                 and query.get('binding_nodes') == sum(len(report['nodes']) for report in docs['profile']['reports']),
                 'Supplement query typed inventory differs')
    comparison = docs['compare']
    _require(comparison.get('contract') == 'root-offline-financial-gate-stage-v1'
             and comparison.get('stage') == 'compare' and comparison.get('http_requests') == 0
             and comparison.get('all_manifest_payloads_authenticated') is True
             and comparison.get('accepted_sources_unchanged') is True
             and type(comparison.get('protected_equal')) is int and comparison['protected_equal'] > 0,
             'Supplement replay comparison is incomplete')
    for doc in (docs['query'], docs['replay_query']):
        _require(doc.get('baseline_sha256') == comparison.get('baseline_sha256')
                 and doc.get('execution_head') == comparison.get('execution_head')
                 and type(doc.get('baseline_sha256')) is str and type(doc.get('execution_head')) is str,
                 'Supplement gates have different review/execution origins')
    for key, allowed in (('admission', ['manifest.json']),
                         ('parquet', ['manifest.json', 'metadata/source-manifest.json'])):
        check = comparison.get('comparisons', {}).get(key)
        names = {e['path'] for e in docs[key]['files']}
        _require(type(check) is dict and set(check) == {'byte_equal', 'separately_validated_execution_metadata'}
                 and check['separately_validated_execution_metadata'] == allowed
                 and check['byte_equal'] == sorted(names - {'metadata/source-manifest.json'}),
                 'Supplement replay inventory differs')
    compare_replay(_path(evidence['admission']['path']).parent, _path(evidence['replay_admission']['path']).parent,
                   _path(evidence['parquet']['path']).parent, _path(evidence['replay_parquet']['path']).parent)
    parquet.validate_snapshot(_path(evidence['parquet']['path']).parent, manifest_sha256=evidence['parquet']['sha256'])
    return {'additional_accepted': 1, 'files': list(evidence.values())}


class _Journal:
    """Durable append-only records; an outdated head never authorizes a dispatch."""
    def __init__(self, root, document, *, create=False, reserved=False):
        self.root, self.document = Path(root), document
        self.path = self.root / 'journal.jsonl'
        self.head = self.root / 'head.json'
        if create:
            if reserved:
                _require({p.name for p in self.root.iterdir()} == {'claim'},
                         'Reserved execution acquired foreign contents before initialization')
            else:
                self.root.mkdir(parents=True, exist_ok=False)
            with self.path.open('xb') as stream:
                stream.flush()
                os.fsync(stream.fileno())
            self.records = []
            self.tip = '0' * 64
            self._head()
        else:
            self.records = []
            self.tip = '0' * 64
            raw = self.path.read_bytes()
            _require(not raw or raw.endswith(b'\n'), 'Partial/truncated stage journal')
            for line in raw.splitlines():
                try:
                    record = profiles._json(line)
                except ValueError as error:
                    raise IntegrityError('Corrupt stage journal') from error
                _require(type(record) is dict and set(record) == {'sequence', 'previous_hash', 'plan_sha256', 'kind', 'member', 'stage', 'data'}
                         and record['sequence'] == len(self.records) + 1 and record['previous_hash'] == self.tip
                         and record['plan_sha256'] == document['sha256']
                         and record['kind'] in ('start', 'finish', 'quarantine', 'halt'), 'Invalid stage journal chain')
                self.records.append(record)
                self.tip = _sha(line)
            _require(profiles._json(self.head.read_bytes()) == self.projection(), 'Stage head is stale or journal truncated')
            self.state()

    def projection(self):
        return {'sequence': len(self.records), 'journal_sha256': self.tip, 'plan_sha256': self.document['sha256']}

    def _head(self):
        temporary = self.root / ('head-' + str(len(self.records)) + '.pending')
        _publish(temporary, self.projection())
        image = _dump(self.projection())
        deadline = time.monotonic() + .25
        last_error = None
        for attempt in range(5):
            if attempt and time.monotonic() >= deadline:
                raise last_error
            _name(temporary)
            _name(self.head)
            _require(temporary.read_bytes() == image, 'Pending stage head changed before publication')
            if attempt and time.monotonic() >= deadline:
                raise last_error
            try:
                os.replace(temporary, self.head)
                break
            except OSError as error:
                last_error = error
                if (sys.platform != 'win32' or getattr(error, 'winerror', None) not in (5, 32)
                        or attempt == 4 or time.monotonic() >= deadline):
                    raise
                time.sleep(min(.01 * 2 ** attempt, max(0, deadline - time.monotonic())))
        _name(self.head)
        with self.head.open('r+b') as stream:
            os.fsync(stream.fileno())
            _require(stream.read() == image, 'Published stage head differs from journal projection')

    def append(self, kind, member, stage, data):
        record = {'sequence': len(self.records) + 1, 'previous_hash': self.tip,
                  'plan_sha256': self.document['sha256'], 'kind': kind, 'member': member, 'stage': stage, 'data': data}
        image = _dump(record)
        with self.path.open('ab') as stream:
            stream.write(image + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        self.records.append(record)
        self.tip = _sha(image)
        self._head()
        return record

    def state(self):
        pending, finished, quarantined = {}, {}, set()
        halted = False
        for record in self.records:
            key = (record['member'], record['stage'])
            if record['kind'] == 'start':
                _require(key not in pending and key not in finished and record['member'] not in quarantined and not halted,
                         'Duplicate or unauthorized stage start')
                pending[key] = record
            elif record['kind'] == 'finish':
                _require(key in pending and record['data']['start_sequence'] == pending[key]['sequence'], 'Unmatched stage finish')
                finished[key] = record
                del pending[key]
            elif record['kind'] == 'quarantine':
                _require(key in pending, 'Quarantine without incomplete start')
                quarantined.add(record['member'])
                del pending[key]
            else:
                halted = True
        return pending, finished, quarantined, halted


def _outputs(doc, member, stage):
    if stage == 'prepare-batch':
        return {'envelope': doc['output'] + '/batch-envelope.json',
                'registry_before': doc['output'] + '/registry-before.json',
                'accepted_inventory': doc['output'] + '/accepted-inventory.json'}
    paths = _member_paths(doc['output'], member) if not _is_plan(doc) else next(
        m['destinations'] for m in doc['members'] if m['selection']['period'] == member)
    if stage == 'prepare-member':
        return {k: paths[k] for k in ('metadata_handoff', 'final_handoff', 'candidate', 'profile', 'summary')}
    return {stage: paths[{'admit': 'admission', 'convert': 'parquet', 'query': 'query',
                         'replay-admit': 'replay_admission', 'replay-convert': 'replay_parquet',
                         'replay-query': 'replay_query', 'compare': 'compare'}[stage]]}


def _inputs(doc, member, stage, finished):
    if stage == 'prepare-batch':
        return {'bundle': doc['batch']['bundle'], 'handoff': doc['batch']['handoff']}
    if stage == 'prepare-member':
        return {'envelope': _read(finished[('batch', 'prepare-batch')]['data']['receipt'])['outputs']['envelope']}
    info = next(m for m in doc['members'] if m['selection']['period'] == member)
    inputs = {k: info[k] for k in ('metadata_handoff', 'final_handoff', 'candidate', 'profile', 'summary')}
    if stage in ('convert', 'query', 'replay-convert', 'replay-query', 'compare'):
        needed = {'convert': ['admit'], 'query': ['admit', 'convert'], 'replay-convert': ['replay-admit'],
                  'replay-query': ['replay-admit', 'replay-convert'],
                  'compare': ['admit', 'convert', 'query', 'replay-admit', 'replay-convert', 'replay-query']}[stage]
        for prior in needed:
            receipt = _read(finished[(member, prior)]['data']['receipt'])
            inputs[prior] = receipt['outputs'][prior]
    return inputs


def _native_images(handoff):
    images = []
    for source in handoff['sources']:
        manifest = _read({'path': source['manifest_path'], 'sha256': source['manifest_sha256']})
        _require(manifest.get('sha256') == source['body_sha256'], 'Native source body pin differs')
        base = _path(source['manifest_path']).parent
        path = profiles._contained(base, manifest['body_path'])
        images.append({'path': _name(path), 'sha256': source['body_sha256'], 'bytes': manifest['bytes']})
        if manifest.get('response_metadata_path'):
            images.append({'path': _name(profiles._contained(base, manifest['response_metadata_path'])),
                           'sha256': manifest['response_metadata_sha256']})
    return images


def _source_bodies(handoff):
    _authenticate_files(_native_images(handoff))


def _global_source_images(images, handoffs):
    """Keep global state checks small; native bodies are checked by their owner."""
    inventory = {image['path']: image for image in images}
    _require(len(inventory) == len(images), 'Duplicate source inventory image')
    bodies = set()
    for handoff in handoffs:
        for native_image in _native_images(handoff):
            if 'bytes' not in native_image:  # Sidecars remain global state inputs.
                continue
            expected = inventory.get(native_image['path'])
            _require(expected is not None and all(expected.get(key) == native_image[key]
                     for key in ('path', 'sha256', 'bytes')), 'Native payload inventory differs from pinned handoff')
            bodies.add(native_image['path'])
    return [image for image in images if image['path'] not in bodies]


def _bridge_source_checks(envelope):
    images = envelope['source_state_files']
    if envelope['contract'] == 'ifdata-financial-acquisition-batch-bridge-v2':
        images = _global_source_images(images, [m['final_handoff'] for m in envelope['members']])
        _authenticate_absent(envelope['source_state_absent'])
    _authenticate_files(images)


def _stage_action(spec, doc):
    member, stage, outputs = spec['member'], spec['stage'], spec['outputs']
    if stage == 'prepare-batch':
        historical = doc['contract'] == PREPARE_V2
        composer = profiles.compose_historical_acquisition_handoffs if historical else profiles.compose_batch_acquisition_handoffs
        envelope = composer(_path(doc['batch']['bundle']['path']),
            _path(doc['batch']['handoff']['path']), bundle_sha256=doc['batch']['bundle']['sha256'],
            bootstrap_sha256=doc['batch']['bootstrap_sha256'], handoff_sha256=doc['batch']['handoff']['sha256'])
        periods = _periods(doc)
        _require([m['selection']['period'] for m in envelope['members']] == periods, 'Preparation members differ from authenticated window')
        _require(not historical or doc['accepted_supplement'] is None, 'Historical preparation rejects legacy accepted supplement')
        supplement = _validate_supplement(doc['accepted_supplement'])
        refs = {'envelope': _publish(_path(outputs['envelope']), envelope)}
        registry_body = _path(_registry_name()).read_bytes()
        registry_path = _path(outputs['registry_before'])
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        with registry_path.open('xb') as stream:
            stream.write(registry_body)
            stream.flush()
            os.fsync(stream.fileno())
        refs['registry_before'] = _ref(registry_path)
        refs['accepted_inventory'] = _publish(_path(outputs['accepted_inventory']),
            {'accepted_before': 0 if historical else 3 + supplement['additional_accepted'],
             'batch_accepted_before': 0 if historical else 3,
             'batch_periods': [] if historical else [202312, 202412, 202503],
             'supplement': doc['accepted_supplement'], 'files': supplement['files']})
        return {'outputs': refs, 'artifacts': list(refs.values()), 'summary': {'members': len(periods)}}
    if stage == 'prepare-member':
        envelope = _read(spec['inputs']['envelope'])
        _bridge_source_checks(envelope)
        original = next(m for m in envelope['members'] if m['selection']['period'] == member)
        refs = {}
        for key in ('metadata_handoff', 'final_handoff'):
            _require(_sha(_dump(original[key])) == original[key + '_sha256'], 'Projected handoff pin differs')
            refs[key] = _publish(_path(outputs[key]), original[key])
        candidate = profiles.compile_metadata_candidate(_path(refs['metadata_handoff']['path']), handoff_sha256=refs['metadata_handoff']['sha256'])
        refs['candidate'] = _publish(_path(outputs['candidate']), candidate)
        frozen = profiles.freeze_profile(_path(refs['candidate']['path']), _path(refs['final_handoff']['path']),
            candidate_sha256=refs['candidate']['sha256'], final_handoff_sha256=refs['final_handoff']['sha256'])
        refs['profile'] = _publish(_path(outputs['profile']), frozen)
        nodes = [n for r in frozen['reports'] for n in r['nodes']]
        summary = {'selection': frozen['selection'], 'descriptor_sha256': frozen['descriptor_sha256'],
                   'nodes': len(nodes), 'leaves': sum(n['kind'] != 'group' for n in nodes),
                   'groups': sum(n['kind'] == 'group' for n in nodes), 'kinds': dict(Counter(n['kind'] for n in nodes)),
                   'cadastro_columns': frozen['cadaster_columns'], 'required_sources': frozen['required_sources'],
                   'missing_sources': frozen['missing_sources'], 'source_pins': frozen['source_pins'],
                   'reports': frozen['reports'], 'limitations': frozen['limitations']}
        refs['summary'] = _publish(_path(outputs['summary']), summary)
        return {'outputs': refs, 'artifacts': list(refs.values()), 'summary': {k: summary[k] for k in
            ('selection', 'descriptor_sha256', 'nodes', 'leaves', 'groups', 'kinds', 'cadastro_columns', 'required_sources')}}
    info = next(m for m in doc['members'] if m['selection']['period'] == member)
    paths = info['destinations']
    destination = _path(outputs[stage])
    if stage in ('admit', 'replay-admit'):
        result = admission.admit(_path(info['final_handoff']['path']), destination)
    elif stage in ('convert', 'replay-convert'):
        prior = 'admit' if stage == 'convert' else 'replay-admit'
        source = _path(spec['inputs'][prior]['path']).parent
        result = conversion.convert_financial(source, destination, source_manifest_sha256=spec['inputs'][prior]['sha256'])
    elif stage in ('query', 'replay-query'):
        prefix = '' if stage == 'query' else 'replay-'
        source_ref, target_ref = spec['inputs'][prefix + 'admit'], spec['inputs'][prefix + 'convert']
        result = verify_query(_path(source_ref['path']).parent, _path(target_ref['path']).parent,
                              source_manifest_sha256=source_ref['sha256'], manifest_sha256=target_ref['sha256'])
        _publish(destination, result)
    else:
        _require(_read(spec['inputs']['query']).get('query_verified') is True
                 and _read(spec['inputs']['replay-query']).get('query_verified') is True, 'Compare requires both physical query proofs')
        result = compare_replay(_path(paths['admission']), _path(paths['replay_admission']),
                                _path(paths['parquet']), _path(paths['replay_parquet']))
        _publish(destination, result)
    if destination.is_dir():
        manifest = destination / 'manifest.json'
        artifacts = [_ref(p) for p in sorted(destination.rglob('*')) if p.is_file()]
    else:
        manifest = destination
        artifacts = [_ref(destination)]
    summary_keys = ('cells', 'observations', 'cadaster_records', 'presence_counts', 'value_state_counts',
                    'numeric_rows', 'bindings', 'precision_encodings', 'query_verified', 'replay_verified')
    return {'outputs': {stage: _ref(manifest)}, 'artifacts': artifacts,
            'summary': {k: result[k] for k in summary_keys if k in result}}


def _authenticate_stage_inputs(spec, doc):
    """Recheck every physical trust input before allowing a known local failure."""
    _require(_read(spec['document']) == doc, 'Stage document changed during execution')
    _check_code(doc['code_pins'], spec['resources'])
    for ref in spec['inputs'].values():
        _read(ref)
    if _is_plan(doc):
        _verify_plan_document(doc, spec['resources'], installed=True)
        info = next(m for m in doc['members'] if m['selection']['period'] == spec['member'])
        _source_bodies(_read(info['final_handoff']))
        for prior in ('admit', 'convert', 'replay-admit', 'replay-convert'):
            if prior in spec['inputs']:
                ref = spec['inputs'][prior]
                _payloads(_path(ref['path']).parent, _read(ref))
    elif spec['stage'] == 'prepare-member':
        envelope = _read(spec['inputs']['envelope'])
        _bridge_source_checks(envelope)
        original = next(m for m in envelope['members'] if m['selection']['period'] == spec['member'])
        _source_bodies(original['final_handoff'])


def _execute_spec(spec):
    """Closed stage execution; useful independently of the OS launch boundary."""
    fields = {'contract', 'document', 'member', 'stage', 'inputs', 'outputs', 'application_sha256',
              'worker_sha256', 'resources', 'identity_path', 'log_path', 'result_path'}
    _require(type(spec) is dict and set(spec) == fields and spec['contract'] == contained.CONTRACT, 'Invalid closed CPU worker spec')
    doc = _read(spec['document'])
    _check_code(doc['code_pins'], spec['resources'])
    _require(spec['application_sha256'] == doc['code_pins']['application']['sha256']
             and spec['worker_sha256'] == next(e['sha256'] for e in doc['code_pins']['modules']
                                              if e['path'] == 'bank_quality/financial_pipeline.py'), 'CPU spec pins differ from document')
    stage, member = spec['stage'], spec['member']
    _require(stage in ('prepare-batch', 'prepare-member', *_STAGES)
             and member in ('batch', *_periods(doc)), 'Invalid CPU member/stage')
    _require((stage == 'prepare-batch') == (member == 'batch'), 'Invalid batch stage identity')
    _require(_is_plan(doc) == (stage in _STAGES), 'Stage is incompatible with the immutable document')
    journal_root = (doc['destinations']['execution'] if _is_plan(doc) else doc['output'] + '/preparation')
    journal = _Journal(_path(journal_root), spec['document'])
    pending, finished, _, halted = journal.state()
    _require(not halted and len(pending) == 1 and (member, stage) in pending, 'Worker is outside its sole pending journal stage')
    start = pending[(member, stage)]
    _require(journal.records[-1] == start and _read(start['data']['spec']) == spec, 'Worker spec differs from its exact durable start')
    stage_root = journal_root + '/stages/' + str(start['sequence']).zfill(4)
    _require(start['data']['spec']['path'] == stage_root + '/spec.json'
             and spec['identity_path'] == stage_root + '/identity.json'
             and spec['log_path'] == stage_root + '/log.json'
             and spec['result_path'] == stage_root + '/result.json', 'Worker paths are outside its exclusive journal stage')
    _require(spec['inputs'] == _inputs(doc, member, stage, finished), 'Worker inputs differ from the pinned stage predecessors')
    _require(spec['outputs'] == _outputs(doc, member, stage), 'CPU output paths differ from immutable document')
    for name in (*spec['outputs'].values(), spec['identity_path'], spec['log_path'], spec['result_path']):
        _path(name)
    if not _is_plan(doc):
        _require(set(doc) == {'contract', 'batch', 'accepted_supplement', 'code_pins', 'resources', 'output'}
                 and doc['contract'] in (PREPARE_V1, PREPARE_V2)
                 and doc['resources'] == spec['resources'], 'Unsupported closed CPU preparation document')
    _authenticate_stage_inputs(spec, doc)
    # Only parser/schema failures inside known calls are local. Unexpected errors halt.
    _publish(_path(spec['log_path']), {'contract': 'financial-sanitization-stage-log-v1',
                                    'stage': stage, 'member': member, 'document': spec['document']})
    status, code, message = 'complete', '', ''
    result = {'outputs': {}, 'artifacts': [], 'summary': {}}
    try:
        result = _stage_action(spec, doc)
    except IntegrityError as error:
        status, code, message = 'halted', 'integrity', str(error)
    except ValueError as error:
        try:
            _authenticate_stage_inputs(spec, doc)
        except Exception as trust_error:
            failure = _global_error(trust_error)
            status, code, message = 'halted', failure['code'], failure['message']
        else:
            # Aggregate source/supplement authentication has no local member.
            if stage != 'prepare-batch' and isinstance(error, admission.NativeSchemaError):
                status, code, message = 'failed', error.code if isinstance(error, StageError) else 'native_schema', str(error)
            else:
                status, code, message = 'halted', 'unexpected', type(error).__name__ + ': ' + str(error)
    except Exception as error:
        status, code, message = 'halted', 'unexpected', type(error).__name__ + ': ' + str(error)
    result = {'contract': STAGE_RESULT, 'document': spec['document'], 'member': member, 'stage': stage,
              'status': status, 'error': {'code': code, 'message': message}, **result}
    _publish(_path(spec['result_path']), result)
    return result


def _dispatch(journal, doc, member, stage, resources):
    pending, finished, _, halted = journal.state()
    _require(not halted and not pending, 'Outstanding/global halted stage prevents dispatch')
    base = _name(journal.root) + '/stages/' + str(len(journal.records) + 1).zfill(4)
    spec = {'contract': contained.CONTRACT, 'document': journal.document, 'member': member, 'stage': stage,
            'inputs': _inputs(doc, member, stage, finished), 'outputs': _outputs(doc, member, stage),
            'application_sha256': doc['code_pins']['application']['sha256'],
            'worker_sha256': next(e['sha256'] for e in doc['code_pins']['modules'] if e['path'] == 'bank_quality/financial_pipeline.py'),
            'resources': resources, 'identity_path': base + '/identity.json', 'log_path': base + '/log.json',
            'result_path': base + '/result.json'}
    for destination in spec['outputs'].values():
        _require(not _path(destination).exists(), 'Stage destination already exists: ' + destination)
    spec_ref = _publish(_path(base + '/spec.json'), spec)
    start = journal.append('start', member, stage, {'spec': spec_ref})
    def before_resume(identity):
        _publish(_path(spec['identity_path']), {'launcher': identity, 'parent': native._current_identity(),
                                               'spec': spec_ref, 'kill_on_job_close': True, 'job_handle_inherited': False})
    try:
        measurement = contained.run_contained_stage(_path(spec_ref['path']), spec_ref['sha256'],
                                                    resources=resources, before_resume=before_resume)
        _require(measurement.get('tree_extinct') is True, 'CPU stage lacks measured tree extinction')
        _require(not measurement.get('deadline_reached') and not measurement.get('guard'), 'CPU resource/deadline guard fired')
        result_ref = _ref(_path(spec['result_path']))
        result = _read(result_ref)
        _require(result.get('contract') == STAGE_RESULT and result.get('document') == journal.document
                 and result.get('member') == member and result.get('stage') == stage
                 and result.get('status') in ('complete', 'failed', 'halted'), 'Invalid physical stage result')
        _authenticate_files(result['artifacts'])
        receipt = {'contract': 'ifdata-financial-sanitization-stage-receipt-v1', 'document': journal.document,
                   'start_sequence': start['sequence'], 'spec': spec_ref, 'result': result_ref,
                   'identity': _ref(_path(spec['identity_path'])), 'log': _ref(_path(spec['log_path'])),
                   'outputs': result['outputs'], 'artifacts': result['artifacts'], 'measurement': measurement,
                   'status': result['status'], 'error': result['error'], 'summary': result['summary']}
        receipt_ref = _publish(_path(base + '/receipt.json'), receipt)
        journal.append('finish', member, stage, {'start_sequence': start['sequence'], 'receipt': receipt_ref})
        if result['status'] == 'halted':
            journal.append('halt', member, stage, result['error'])
        return receipt
    except Exception as error:
        journal.append('halt', member, stage, _global_error(error))
        return None


def _verify_plan_document(doc, resources, *, installed, verify_native=False):
    fields = {'contract', 'batch', 'source_state', 'source_state_files', 'code_pins', 'registry_before_sha256',
              'registry_proposed', 'members', 'destinations', 'limitations', 'accepted_supplement'}
    historical = type(doc) is dict and doc.get('contract') == PLAN_V2
    if historical:
        fields.add('source_state_absent')
    _require(type(doc) is dict and set(doc) == fields and _is_plan(doc), 'Invalid closed sanitization plan')
    _check_code(doc['code_pins'], resources)
    _require(type(doc['members']) is list and [m['selection']['period'] for m in doc['members']] == _periods(doc),
             'Plan must contain all ordered native selections of its authenticated window')
    output = doc['destinations']['preparation']
    _require(doc['destinations'] == {'preparation': output, 'execution': output + '/execution'}, 'Plan execution destination changed')
    proposed = _read(doc['registry_proposed'])
    before = _read({'path': output + '/registry-before.json', 'sha256': doc['registry_before_sha256']})
    _require(len(before['members']) == 66 and len({profiles._canonical(m['selection']) for m in before['members']}) == 66,
             'The first pipeline contract requires the finite 66-offer registry')
    preparation = _Journal(_path(output + '/preparation'), _ref(_path(output + '/prepare-request.json')))
    request = _read(preparation.document)
    _require(request['contract'] == (PREPARE_V2 if historical else PREPARE_V1)
             and request['batch'] == {key: doc['batch'][key] for key in ('bundle', 'handoff', 'bootstrap_sha256')}
             and request['code_pins'] == doc['code_pins']
             and request['accepted_supplement'] == doc['accepted_supplement'] and request['output'] == output,
             'Plan differs from its immutable preparation inputs')
    batch_record = preparation.state()[1].get(('batch', 'prepare-batch'))
    _require(batch_record is not None, 'Plan has no completed authenticated batch preparation')
    batch_receipt = _validate_receipt(batch_record, preparation.document, payloads=False)
    _require(batch_receipt['status'] == 'complete', 'Batch preparation did not complete')
    envelope = _read(batch_receipt['outputs']['envelope'])
    _require(envelope['contract'] == ('ifdata-financial-acquisition-batch-bridge-v2' if historical
                                     else 'ifdata-financial-acquisition-batch-bridge-v1')
             and envelope['batch'] == doc['batch'], 'Plan bridge version or batch identity differs')
    if historical:
        _require(doc['accepted_supplement'] is None
                 and doc['source_state_absent'] == envelope['source_state_absent'],
                 'Historical plan absence/supplement differs from authenticated bridge')
    inventory_ref = batch_receipt['outputs']['accepted_inventory']
    inventory = _read(inventory_ref)
    _require(type(doc['source_state']) is dict
             and set(doc['source_state']) == {'acquisition', 'accepted_before', 'accepted_inventory'}
             and doc['source_state']['acquisition'] == envelope['source_state']
             and doc['source_state_files'] == envelope['source_state_files']
             and doc['source_state']['accepted_inventory'] == inventory_ref
             and doc['source_state']['accepted_before'] == inventory['accepted_before']
             and inventory['batch_accepted_before'] == (0 if historical else 3)
             and inventory['batch_periods'] == ([] if historical else [202312, 202412, 202503])
             and inventory['accepted_before'] == (0 if historical else 4 if doc['accepted_supplement'] else 3)
             and inventory['supplement'] == doc['accepted_supplement'], 'Plan accepted inventory/source authority differs')
    expected = copy.deepcopy(before)
    native_images = {}
    for member in doc['members']:
        _require(set(member) == {'selection', 'descriptor_sha256', 'metadata_handoff', 'final_handoff', 'candidate', 'profile',
                               'summary', 'installed_profile_path', 'nodes', 'leaves', 'groups', 'kinds', 'cadastro_columns',
                               'required_sources', 'destinations'}, 'Invalid closed plan member')
        period = member['selection']['period']
        paths = _member_paths(output, period)
        _require(member['destinations'] == paths and member['installed_profile_path'] == f'financial-reports-profiles/{period}.json',
                 'Plan member paths changed')
        for key in ('metadata_handoff', 'final_handoff', 'candidate', 'profile', 'summary'):
            _require(member[key]['path'] == paths[key], 'Authoring artifact path changed')
            _read(member[key])
        profile = _read(member['profile'])
        summary = _read(member['summary'])
        _require(all(member[k] == summary[k] for k in ('selection', 'descriptor_sha256', 'nodes', 'leaves', 'groups',
                                                     'kinds', 'cadastro_columns', 'required_sources'))
                 and summary['reports'] == profile['reports'] and summary['missing_sources'] == []
                 and summary['source_pins'] == profile['source_pins'], 'Plan summary differs from its generated native profile')
        _require(profile['selection'] == member['selection'] and profile['descriptor_sha256'] == member['descriptor_sha256']
                 and profile['missing_sources'] == [], 'Generated profile/selection differs')
        matches = [m for m in expected['members'] if m['selection'] == member['selection']]
        _require(len(matches) == 1 and profiles._digest(profiles._offer_payload(matches[0])) == member['descriptor_sha256'], 'Registry proposal descriptor differs')
        matches[0].update(profile_path=member['installed_profile_path'], profile_sha256=member['profile']['sha256'])
        if installed:
            installed_path = profiles._contained(profiles.PACKAGE_ROOT, member['installed_profile_path'])
            _require(installed_path.is_file() and _stream_sha(installed_path) == member['profile']['sha256'], 'Exact generated profile is not installed')
        if verify_native:
            for image in _native_images(_read(member['final_handoff'])):
                previous = native_images.setdefault(image['path'], image)
                _require(previous == image, 'Shared native source has divergent pins')
    _require(expected == proposed, 'Registry proposal changes more than the window profile activations')
    if installed:
        _require(_stream_sha(_path(_registry_name())) == doc['registry_proposed']['sha256'], 'Proposed registry is not installed exactly')
    _source_checks(doc, installed=installed)
    if verify_native:
        _authenticate_files(list(native_images.values()))


def prepare_profiles(bundle_path: Path, handoff_path: Path, output: Path, *, bundle_sha256: str,
                     bootstrap_sha256: str, handoff_sha256: str, resources: dict,
                     accepted_supplement_path=None, accepted_supplement_sha256=None) -> dict:
    resources = validate_resources(resources)
    _require((accepted_supplement_path is None) == (accepted_supplement_sha256 is None), 'Both supplement path and external hash are required')
    output = Path(output).absolute()
    name = _name(output)
    _require(name.startswith('data/runs/') and len(name.split('/')) == 3, 'Preparation destination must be a new direct data/runs child')
    _require(not output.exists(), 'Preparation destination already exists')
    batch = {'bundle': {'path': _name(bundle_path), 'sha256': bundle_sha256},
             'handoff': {'path': _name(handoff_path), 'sha256': handoff_sha256}, 'bootstrap_sha256': bootstrap_sha256}
    for ref in (batch['bundle'], batch['handoff']):
        _read(ref)
    historical = _read(batch['bundle']).get('contract') == 'financial-acquisition-batch-v2'
    _require(not historical or accepted_supplement_path is None, 'Historical preparation rejects legacy accepted supplement')
    profiles._hash(bootstrap_sha256)
    supplement = None if accepted_supplement_path is None else {'path': _name(accepted_supplement_path), 'sha256': accepted_supplement_sha256}
    if supplement:
        _read(supplement)
    request = {'contract': PREPARE_V2 if historical else PREPARE_V1, 'batch': batch, 'accepted_supplement': supplement,
               'code_pins': _code_pins(resources), 'resources': resources, 'output': name}
    output.mkdir(parents=True, exist_ok=False)
    request_ref = _publish(output / 'prepare-request.json', request)
    journal = _Journal(output / 'preparation', request_ref, create=True)
    with native.exclusive_claim(journal.root / 'claim'):
        receipt = _dispatch(journal, request, 'batch', 'prepare-batch', resources)
        if receipt is None or receipt['status'] != 'complete':
            return {'status': 'halted', 'request': request_ref, 'plan': None}
        members = []
        periods = _periods(request)
        for period in periods:
            receipt = _dispatch(journal, request, period, 'prepare-member', resources)
            if receipt is None or receipt['status'] == 'halted':
                break
            if receipt['status'] == 'complete':
                summary = receipt['summary']
                members.append({**summary, **receipt['outputs'], 'installed_profile_path': f'financial-reports-profiles/{period}.json',
                                'destinations': _member_paths(name, period)})
        if len(members) != len(periods):
            result = {'status': 'halted' if journal.state()[3] else 'partial', 'request': request_ref,
                      'plan': None, 'profile_generated': [m['selection']['period'] for m in members]}
            _publish(output / 'prepare-result.json', result)
            return result
        envelope = _read(_ref(output / 'batch-envelope.json'))
        before = profiles._json((output / 'registry-before.json').read_bytes())
        proposed = copy.deepcopy(before)
        for member in members:
            matches = [m for m in proposed['members'] if m['selection'] == member['selection']]
            _require(len(matches) == 1, 'Proposal selection missing/duplicated')
            matches[0].update(profile_path=member['installed_profile_path'], profile_sha256=member['profile']['sha256'])
        proposed_ref = _publish(output / 'registry-proposed.json', proposed)
        accepted = _read(_ref(output / 'accepted-inventory.json'))
        plan = {'contract': PLAN_V2 if historical else PLAN, 'batch': envelope['batch'], 'source_state': {'acquisition': envelope['source_state'],
                'accepted_before': accepted['accepted_before'], 'accepted_inventory': _ref(output / 'accepted-inventory.json')},
                'source_state_files': envelope['source_state_files'], 'code_pins': request['code_pins'],
                'registry_before_sha256': _sha((output / 'registry-before.json').read_bytes()),
                'registry_proposed': proposed_ref, 'members': members,
                'destinations': {'preparation': name, 'execution': name + '/execution'},
                'limitations': envelope['limitations'] + ['Exact external profile/registry installation is required.',
                    'Software checks do not certify economic comparability or independent review.'], 'accepted_supplement': supplement}
        if historical:
            plan['source_state_absent'] = envelope['source_state_absent']
            _authenticate_files(envelope['source_state_files'])
            _authenticate_absent(envelope['source_state_absent'])
        _verify_plan_document(plan, resources, installed=False)
        plan_ref = _publish(output / 'plan.json', plan)  # Published after all window candidates and integrity checks.
        result = {'status': 'prepared', 'request': request_ref, 'plan': plan_ref, 'profile_generated': periods}
        _publish(output / 'prepare-result.json', result)
        return result


def _validate_receipt(record, document, *, payloads):
    receipt = _read(record['data']['receipt'])
    _require(receipt.get('contract') == 'ifdata-financial-sanitization-stage-receipt-v1'
             and receipt.get('document') == document and receipt['measurement'].get('tree_extinct') is True
             and not receipt['measurement'].get('deadline_reached') and not receipt['measurement'].get('guard'),
             'Stage receipt lacks authenticated extinction/result')
    result = _read(receipt['result'])
    spec = _read(receipt['spec'])
    _read(receipt['identity'])
    _read(receipt['log'])
    _require(result['document'] == document and result['member'] == record['member'] and result['stage'] == record['stage']
             and spec['document'] == document and spec['member'] == record['member'] and spec['stage'] == record['stage']
             and receipt['status'] == result['status'] and receipt['outputs'] == result['outputs']
             and receipt['artifacts'] == result['artifacts'] and receipt['summary'] == result['summary'], 'Stage receipt/result/spec differs')
    if payloads:
        _authenticate_files(receipt['artifacts'])
        for ref in receipt['outputs'].values():
            if Path(ref['path']).name == 'manifest.json':
                manifest = _read(ref)
                directory = _path(ref['path']).parent
                names = {entry['path'] for entry in manifest['files']}
                actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
                _require(actual == names | {'manifest.json'}, 'Completed stage inventory changed before resume')
    return receipt


def _score(doc, journal=None):
    finished, quarantined, halted = {}, set(), False
    if journal:
        _, finished, quarantined, halted = journal.state()
    states = []
    for member in doc['members']:
        period = member['selection']['period']
        flags = {'source_complete': True, 'profile_generated': True, 'profile_installed': False,
                 'admitted': False, 'parquet_verified': False, 'query_verified': False, 'replay_verified': False}
        path = profiles._contained(profiles.PACKAGE_ROOT, member['installed_profile_path'])
        registry = _path(_registry_name())
        flags['profile_installed'] = (path.is_file() and _stream_sha(path) == member['profile']['sha256']
                                      and registry.is_file() and _stream_sha(registry) == doc['registry_proposed']['sha256'])
        terminal, receipts, errors = '', [], []
        counts = {k: member[k] for k in ('nodes', 'leaves', 'groups', 'kinds', 'cadastro_columns', 'required_sources')}
        for stage in _STAGES:
            record = finished.get((period, stage))
            if record is None:
                continue
            receipt = _validate_receipt(record, journal.document, payloads=False)
            receipts.append(record['data']['receipt'])
            if receipt['status'] != 'complete':
                terminal = 'failed' if receipt['status'] == 'failed' else 'quarantined'
                errors.append(receipt['error'])
                continue
            milestone = {'admit': 'admitted', 'convert': 'parquet_verified', 'query': 'query_verified', 'compare': 'replay_verified'}.get(stage)
            if milestone:
                flags[milestone] = True
            counts.update(receipt['summary'])
        if period in quarantined:
            terminal = 'quarantined'
        if journal:
            for record in journal.records:
                if record['member'] in (period, 'batch') and record['kind'] == 'halt':
                    terminal = 'quarantined'
                    if record['data'] not in errors:
                        errors.append(record['data'])
        last = next((key for key in reversed(list(flags)) if flags[key]), 'source_complete')
        pending_stage = next((s for (p, s) in journal.state()[0] if p == period), None) if journal else None
        states.append({'selection': member['selection'], 'state': terminal or last, 'last_verified_milestone': last,
                       'terminal_state': terminal or None, 'incomplete_stage': pending_stage,
                       'milestones': flags, 'receipts': receipts, 'errors': errors, 'counts': counts})
    accepted = sum(s['milestones']['replay_verified'] and not s['state'] in ('failed', 'quarantined') for s in states)
    before = doc['source_state']['accepted_before']
    if doc['contract'] == PLAN_V2:
        count = len(doc['members'])
        return {'members': states, 'scoreboard': {'coverage_scope': 'authenticated_window', 'window': count,
            'window_accepted': accepted, 'window_remaining': count - accepted},
            'status': 'halted' if halted else 'complete' if accepted == count else 'partial'}
    return {'members': states, 'scoreboard': {'offered': 66, 'window': 7, 'accepted_before': before,
              'window_accepted': accepted, 'accepted_after': before + accepted, 'remaining_after': 66 - before - accepted},
            'status': 'halted' if halted else 'complete' if accepted == 7 else 'partial'}


def read_status(plan_path: Path, *, plan_sha256: str) -> dict:
    ref = {'path': _name(plan_path), 'sha256': plan_sha256}
    doc = _read(ref)
    _require(_is_plan(doc), 'Unsupported status plan')
    root = _path(doc['destinations']['execution'])
    journal = _Journal(root, ref) if root.exists() else None
    result = _score(doc, journal)
    result.update(contract='ifdata-financial-sanitization-result-v2' if doc['contract'] == PLAN_V2 else RESULT, plan=ref,
                  validation_scope='Pinned plan, small journal/receipts/results and installed profile hashes; corpus not reopened')
    return result


def run_pipeline(plan_path: Path, *, plan_sha256: str, resources: dict, resume: bool = False) -> dict:
    resources = validate_resources(resources)
    _require(type(resume) is bool, 'Resume must be an explicit boolean')
    ref = {'path': _name(plan_path), 'sha256': plan_sha256}
    doc = _read(ref)
    _verify_plan_document(doc, resources, installed=True, verify_native=True)  # Stream hashes once before any execution write.
    root = _path(doc['destinations']['execution'])
    # Reserve the directory atomically, but derive no dispatch state until the
    # exclusive claim is held. A second fresh caller cannot adopt this root.
    try:
        root.mkdir(exist_ok=False)
        created = True
    except FileExistsError:
        created = False
    with native.exclusive_claim(root / 'claim'):
        _require(resume or created, 'Existing execution requires explicit resume')
        journal = _Journal(root, ref, create=created, reserved=created)
        pending, finished, _, halted = journal.state()
        for record in finished.values():
            _validate_receipt(record, ref, payloads=True)
        if pending and not halted:
            for (member, stage), record in list(pending.items()):
                spec = _read(record['data']['spec'])
                identity_path = _path(spec['identity_path'])
                if identity_path.is_file():
                    identity = profiles._json(identity_path.read_bytes())
                    _require(identity.get('kill_on_job_close') is True and identity.get('job_handle_inherited') is False
                             and identity.get('spec') == record['data']['spec']
                             and native.identity_extinct(identity['launcher']) and native.identity_extinct(identity['parent']),
                             'Incomplete stage tree extinction is uncertain')
                else:
                    raise IntegrityError('Incomplete stage has no durable contained identity')
                journal.append('quarantine', member, stage, {'code': 'incomplete_stage', 'partial_outputs': spec['outputs'],
                               'identity': _ref(identity_path), 'extinction_basis': 'noninherited kill-on-close owner and launcher identities extinct'})
        for member in doc['members']:
            period = member['selection']['period']
            _, finished, quarantined, halted = journal.state()
            if halted:
                break
            if period in quarantined:
                continue
            if any(_read(r['data']['receipt'])['status'] != 'complete' for (p, _), r in finished.items() if p == period):
                continue
            for stage in _STAGES:
                _, finished, _, halted = journal.state()
                if (period, stage) in finished:
                    continue
                try:
                    _source_checks(doc, installed=True)
                    receipt = _dispatch(journal, doc, period, stage, resources)
                except Exception as error:
                    # An active-run trust/IO/unclassified failure must leave durable
                    # halted evidence and the already authenticated partial score.
                    journal.append('halt', period, stage, _global_error(error))
                    receipt = None
                if receipt is None or receipt['status'] != 'complete':
                    break
        result = _score(doc, journal)
        if doc['contract'] == PLAN_V2 and result['status'] == 'complete':
            try:
                _verify_plan_document(doc, resources, installed=True, verify_native=True)
            except Exception as error:
                journal.append('halt', 'batch', 'compare', _global_error(error))
                result = _score(doc, journal)
        result.update(contract='ifdata-financial-sanitization-result-v2' if doc['contract'] == PLAN_V2 else RESULT,
                      plan=ref, head=journal.projection(), resources=resources,
                      limitations=doc['limitations'],
                      measured_elapsed_seconds=sum(_read(r['data']['receipt'])['measurement']['elapsed_seconds']
                                                   for r in journal.state()[1].values()))
        path = root / ('result-' + str(len(journal.records)) + '.json')
        if path.exists():
            _require(path.read_bytes() == _dump(result), 'Existing final result projection differs')
        else:
            _publish(path, result)
        return {**result, 'manifest': _ref(path)}


def _worker_main(path, pin):
    ref = {'path': _name(path), 'sha256': pin}
    spec = _read(ref)
    identity = profiles._json(_path(spec['identity_path']).read_bytes())
    _require(identity.get('spec') == ref and identity.get('kill_on_job_close') is True
             and identity.get('job_handle_inherited') is False, 'CPU worker lacks durable contained identity')
    native.verify_worker_ancestry(identity['launcher'], identity['parent'])
    doc = _read(spec['document'])
    journal_root = doc['destinations']['execution'] if _is_plan(doc) else doc['output'] + '/preparation'
    kernel = native._kernel()
    # The coordinator owns the noninherited, exclusive OS claim while this worker runs.
    handle = kernel.CreateFileW(str(_path(journal_root + '/claim')), 0x80000000, 0, None, 3, 0x80, None)
    if handle != contained.C.c_void_p(-1).value:
        kernel.CloseHandle(handle)
        raise IntegrityError('CPU coordinator claim is not exclusively held')
    _require(contained.C.get_last_error() == 32, 'CPU coordinator claim exclusivity is uncertain')
    result = _execute_spec(spec)
    return 0 if result['status'] == 'complete' else 2 if result['status'] == 'failed' else 3


if __name__ == '__main__':
    if len(sys.argv) != 4 or sys.argv[1] != '--worker':
        raise SystemExit('Only the fixed --worker spec-path spec-sha256 interface is available')
    try:
        raise SystemExit(_worker_main(Path(sys.argv[2]), sys.argv[3]))
    except Exception as error:
        print(json.dumps({'status': 'halted', 'error': type(error).__name__ + ': ' + str(error)}), file=sys.stderr)
        raise SystemExit(3)

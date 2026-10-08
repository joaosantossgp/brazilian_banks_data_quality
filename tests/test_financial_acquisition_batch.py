"""Small synthetic fixtures; no fixture represents accepted BCB data."""
from contextlib import contextmanager
import copy
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(body):
    return hashlib.sha256(body).hexdigest()


WINDOW = [202312, 202403, 202406, 202409, 202412, 202503, 202506, 202509, 202512, 202603, 202606]
ACQUIRE = [202406, 202409, 202506, 202509, 202512, 202603, 202606]
REUSE = [202312, 202403, 202412, 202503]
SCOPE = 'financial-recent-202312-202606-v1'
CATALOG_URLS = {'old': 'https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024',
                'new': 'https://www3.bcb.gov.br/ifdata/rest/relatorios2025a2030'}


def catalog_entry(period):
    prefix = ('ifdata_2025_2030//' if period >= 202503 else 'ifdata/') + str(period) + '/'
    ids = [119, 107, 110, 118] if period >= 202503 else [92, 96, 101, 98]
    files = [{'f': prefix + f'cadastro{period}_1005.json'}, {'f': prefix + f'info{period}.json'},
             {'f': prefix + f'sel{period}.json', 'sel': [{'id': 1005}]}]
    files.extend({'f': prefix + f'dados{period}_{area}.json'} for area in (1, 2, 3, 4, 5))
    for rid in ids:
        files.append({'f': prefix + f'trel{period}_{rid}.json',
                      'trel': {'id': rid, 's': [{'id': 1004}, {'id': 1005}],
                               'annotation': {'unit': 'unknown', 'window': 'unknown'},
                               'c': [{'id': rid, 'ifd': rid, 'ip': None, 'sc': []}]}})
    return {'dt': period, 'files': files}


class RepresentativeMeasurementVersionTests(unittest.TestCase):
    def fixture(self):
        batch = importlib.import_module('bank_quality.financial_acquisition_batch')
        measurement = {'sample_count': 2,
            'peaks': {'tree_working_set_bytes': 20, 'tree_private_bytes': 30},
            'minimum_free': {'free_physical_bytes': 90, 'free_commit_bytes': 90, 'free_disk_bytes': 90},
            'measurement_scope': 'sampled_process_peaks_with_explicit_observation_gaps',
            'pending_limit_ms': 250, 'pending_poll_ms': 50,
            'observation_gaps': [{'started_clock_ns': 1000, 'ended_clock_ns': 100001000,
                'duration_ns': 100000000, 'reason': 'synthetic process birth', 'observations': 1,
                'status': 'resolved', 'machine_samples': [{'elapsed_clock_ns': 50001000,
                    'free_physical_bytes': 100, 'free_commit_bytes': 100, 'free_disk_bytes': 100,
                    'inflight_reserved_bytes': 5, 'inflight_reserved_attempt_seconds': 120}]}]}
        profile = {f'min_free_{key}_bytes': 10 for key in ('physical', 'commit', 'disk')}
        return batch, measurement, profile

    def validate(self, measurement, profile=None, contract='financial-acquisition-representative-measurement-v2'):
        batch = importlib.import_module('bank_quality.financial_acquisition_batch')
        batch._validate_representative_measurements(measurement, contract=contract, profile=profile)

    def test_version_two_accepts_resolved_or_empty_gaps(self):
        batch, measurement, profile = self.fixture()
        self.validate(measurement, profile)
        measurement['observation_gaps'] = []
        self.validate(measurement, profile)

    def test_legacy_schema_stays_closed(self):
        batch, measurement, profile = self.fixture()
        legacy = {key: measurement[key] for key in ('sample_count', 'peaks', 'minimum_free')}
        self.validate(legacy, profile, 'financial-acquisition-representative-measurement-v1')
        for value, contract in ((measurement, 'financial-acquisition-representative-measurement-v1'),
                (legacy, 'financial-acquisition-representative-measurement-v2'),
                (legacy, 'unknown')):
            with self.subTest(contract=contract), self.assertRaises(ValueError):
                self.validate(value, profile, contract)

    def test_corrupt_gap_and_measurement_fields_are_rejected(self):
        batch, measurement, profile = self.fixture()
        changes = [('measurement_scope', 'unknown'), ('pending_limit_ms', 251),
                   ('pending_poll_ms', 49), ('sample_count', True), ('extra', 1)]
        for key, value in changes:
            with self.subTest(key=key):
                altered = copy.deepcopy(measurement)
                altered[key] = value
                with self.assertRaises(ValueError):
                    self.validate(altered, profile)
        for key, value in [('status', 'expired'), ('status', 'cancelled'), ('status', 'failed'),
                ('duration_ns', 250000000), ('duration_ns', 1), ('started_clock_ns', True),
                ('ended_clock_ns', 0), ('observations', 2), ('reason', ''), ('extra', 0)]:
            with self.subTest(gap_key=key, value=value):
                altered = copy.deepcopy(measurement)
                altered['observation_gaps'][0][key] = value
                with self.assertRaises(ValueError):
                    self.validate(altered, profile)

    def test_machine_sample_clock_and_reservations_are_authenticated(self):
        batch, measurement, profile = self.fixture()
        for key, value in [('elapsed_clock_ns', 999), ('elapsed_clock_ns', 100001001),
                ('inflight_reserved_bytes', -1), ('inflight_reserved_attempt_seconds', True),
                ('free_commit_bytes', -1), ('extra', 0)]:
            with self.subTest(key=key):
                altered = copy.deepcopy(measurement)
                altered['observation_gaps'][0]['machine_samples'][0][key] = value
                with self.assertRaises(ValueError):
                    self.validate(altered, profile)

    def test_overlap_and_unordered_samples_are_rejected(self):
        batch, measurement, profile = self.fixture()
        altered = copy.deepcopy(measurement)
        altered['observation_gaps'].append(copy.deepcopy(altered['observation_gaps'][0]))
        with self.assertRaises(ValueError):
            self.validate(altered, profile)
        altered = copy.deepcopy(measurement)
        gap = altered['observation_gaps'][0]
        gap['observations'] = 2
        gap['machine_samples'].append(copy.deepcopy(gap['machine_samples'][0]))
        with self.assertRaises(ValueError):
            self.validate(altered, profile)

    def test_minimum_and_pinned_margins_include_pending_reservations(self):
        batch, measurement, profile = self.fixture()
        altered = copy.deepcopy(measurement)
        altered['minimum_free']['free_physical_bytes'] = 101
        with self.assertRaises(ValueError):
            self.validate(altered, profile)
        altered = copy.deepcopy(measurement)
        altered['observation_gaps'][0]['machine_samples'][0]['inflight_reserved_bytes'] = 95
        # Pure replay authenticates schema; the physical profile adds resource margins.
        self.validate(altered)
        with self.assertRaises(ValueError):
            self.validate(altered, profile)
        altered = copy.deepcopy(measurement)
        altered['minimum_free']['free_commit_bytes'] = 9
        with self.assertRaises(ValueError):
            self.validate(altered, profile)


class BatchCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = importlib.import_module('bank_quality.financial_acquisition_batch')
        cls.acquisition = importlib.import_module('bank_quality.financial_acquisition')

    def inject(self, module, name, value):
        injection = patch.object(module, name, value, create=True)
        injection.start()
        self.addCleanup(injection.stop)

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value if isinstance(value, bytes) else canonical(value))
        return {'path': relative, 'sha256': sha(path.read_bytes())}

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.inject(self.batch, '_ROOT', self.root)
        self.inject(self.acquisition, '_ROOT', self.root)
        @contextmanager
        def fixture_claim(path):
            path.touch(exist_ok=True)
            yield
        self.inject(self.acquisition, '_claim', fixture_claim)
        old = [{} for _ in range(95)] + [catalog_entry(p) for p in (202312, 202403, 202406, 202409, 202412)]
        new = [catalog_entry(p) for p in (202503, 202506, 202509, 202512, 202603, 202606)]
        self.catalogs = {'old': old, 'new': new}
        refs, frozen = {}, {}
        for name, entries in self.catalogs.items():
            payload = canonical(entries)
            body = self.write('data/raw/catalog/' + name + '.bin', payload)
            manifest = {'url': CATALOG_URLS[name], 'method': 'GET', 'final_url': CATALOG_URLS[name],
                        'http_status': 200, 'outcome': 'ok', 'truncated': False,
                        'body_path': name + '.bin', 'sha256': body['sha256'], 'bytes': len(payload)}
            pin = self.write('data/raw/catalog/' + name + '.json', manifest)
            refs[name] = {'source_id': 'catalog-' + name, 'role': 'catalog', 'manifest_path': pin['path'],
                          'manifest_sha256': pin['sha256'], 'body_sha256': body['sha256'],
                          'provenance_sha256': sha(canonical(manifest))}
            frozen[name] = (pin['sha256'], body['sha256'], CATALOG_URLS[name])
        self.inject(self.acquisition, '_FROZEN', frozen)
        self.index = {'contract': 'financial-acquisition-catalog-index-v1',
                      'acquisition_scope': 'issue50/financial-202403-1005-native-four',
                      'selection': {'perspective': 1005, 'reports': 'native-four'}, 'catalogs': refs}
        self.catalog_index = self.root / 'data/runs/input/catalog-index.json'
        self.write(self.catalog_index.relative_to(self.root).as_posix(), self.index)
        self.entries, self.anchors = [], {}
        for period in (202312, 202412, 202503):
            self.parquet_fixture(period)
        self.source_fixture()
        self.entries.sort(key=lambda entry: entry['period'])
        self.reuse = {'contract': 'financial-acquisition-batch-reuse-index-v1', 'scope': SCOPE,
                      'entries': self.entries}
        self.reuse_index = self.root / 'data/runs/input/reuse-index.json'
        self.inject(self.batch, '_TRUSTED_REUSE', self.anchors)
        # Preparation is pure: even an accidental execution attempt fails loudly.
        for module, name in ((self.acquisition, 'initialize_authority'), (self.acquisition, 'run_acquisition')):
            self.inject(module, name, lambda *args, **kwargs: self.fail('Preparation attempted execution'))
        archive = importlib.import_module('bank_quality.archive')
        self.inject(archive, 'fetch', lambda *args, **kwargs: self.fail('Preparation attempted HTTP'))

    def parquet_fixture(self, period):
        selection = {'period': period, 'perspective': 1005,
                     'reports': [119, 107, 110, 118] if period == 202503 else [92, 96, 101, 98]}
        origin = self.write(f'data/raw/reuse/{period}.bin', b'legacy-native-body')
        native = {'url': 'https://fixture/native', 'final_url': 'https://fixture/native', 'method': 'GET',
                  'http_status': 200, 'outcome': 'ok', 'truncated': False,
                  'body_path': f'{period}.bin', 'bytes': 18, 'sha256': origin['sha256']}
        native_pin = self.write(f'data/raw/reuse/{period}.json', native)
        ref = {'source_id': 'numeric', 'manifest_path': native_pin['path'],
               'manifest_sha256': native_pin['sha256'], 'body_sha256': origin['sha256'],
               'provenance_sha256': sha(canonical(native))}
        if period == 202312:
            sources, members = {'numeric': ref}, [ref]
            source_pins = {'manifest_sha256': native_pin['sha256'], 'body_sha256': origin['sha256'],
                           'provenance_sha256': sha(canonical(native)), 'projection_sha256': sha(canonical(ref))}
        else:
            indexed = '../../../' + native_pin['path']
            projection = {key: native[key] for key in ('url', 'final_url', 'bytes', 'sha256', 'body_path')}
            projection.update(manifest_sha256=native_pin['sha256'], source_generation_state='unknown')
            sources, members = {'numeric': {**projection, 'indexed_manifest': indexed}}, {'numeric': indexed}
            source_pins = {'manifest_sha256': native_pin['sha256'], 'body_sha256': origin['sha256'],
                           'provenance_sha256': sha(canonical(projection))}
        profile = self.write(f'bank_quality/profiles/{period}.json',
                             {'selection': selection, 'source_pins': {'numeric': source_pins}})
        source_index = self.write(f'data/runs/input/sources-{period}.json', {'selection': selection, 'sources': members})
        raw = b'native,unaltered\n'
        source_files = [{'path': 'financial-cells.csv', 'bytes': len(raw), 'sha256': sha(raw)}]
        self.write(f'data/derived/reuse-{period}/financial-cells.csv', raw)
        source_contract = ('ifdata-financial-reports-historical-snapshot-v1' if period == 202312
                           else f'ifdata-financial-reports-snapshot-{period}-v1')
        admitted = {'contract': source_contract, 'accepted': True, 'selection': selection,
                    'profile_sha256': profile['sha256'], 'input_index_sha256': source_index['sha256'],
                    'sources': sources, 'files': source_files}
        admission = self.write(f'data/derived/reuse-{period}/manifest.json', admitted)
        source_copy = self.write(f'data/curated/reuse-{period}/metadata/source-manifest.json', admitted)
        part = self.write(f'data/curated/reuse-{period}/parts/cells.parquet', b'synthetic-part')
        files = [{'path': 'metadata/source-manifest.json', 'bytes': len(canonical(admitted)), 'sha256': source_copy['sha256']},
                 {'path': 'parts/cells.parquet', 'bytes': 14, 'sha256': part['sha256']}]
        contract = ('ifdata-financial-reports-historical-parquet-v2' if period == 202312
                    else f'ifdata-financial-reports-parquet-{period}-v1')
        manifest = {'contract': contract, 'accepted': True, 'selection': selection,
                    'profile_sha256': profile['sha256'], 'source_manifest_sha256': admission['sha256'],
                    'source_files': source_files, 'files': files}
        pin = self.write(f'data/curated/reuse-{period}/manifest.json', manifest)
        entry = {'period': period, 'kind': 'accepted_parquet', 'manifest_path': pin['path'],
                 'manifest_sha256': pin['sha256'],
                 'evidence': {'profile': profile, 'admission': admission, 'source_index': source_index}}
        self.entries.append(entry)
        self.anchors[period] = {'entry': copy.deepcopy(entry), 'contract': contract, 'source_contract': source_contract,
                                'profile_sha256': profile['sha256'], 'source_manifest_sha256': admission['sha256']}

    def bounded_source(self, target, payload):
        body = canonical(payload)
        stem = target['source_id'].replace(':', '-')
        prefix = ('data/raw/source403/' if target['period'] == 202403 else 'data/raw/source' + str(target['period']) + '/') + stem
        self.write(prefix + '.bin', body)
        headers = [['Content-Length', str(len(body))]]
        metadata = {'http_status': 200, 'final_url': target['url'], 'response_headers_raw': headers}
        sidecar = self.write(prefix + '.response.json', metadata)
        manifest = {'contract': 'bounded-http-archive-v1', 'url': target['url'], 'final_url': target['url'],
                    'method': 'GET', 'http_status': 200, 'outcome': 'ok', 'truncated': False,
                    'source_complete': True, 'body_available': True, 'diagnostics': [],
                    'body_path': stem + '.bin', 'bytes': len(body), 'sha256': sha(body),
                    'completion_basis': 'content_length', 'eof_observed': False,
                    'content_length': len(body), 'bytes_observed': len(body), 'body_budget_bytes': len(body),
                    'response_metadata_path': stem + '.response.json', 'response_metadata_sha256': sidecar['sha256'],
                    'response_headers_raw': headers,
                    'context': {'period': target['period'], 'perspective': 1005, 'role': target['role']}}
        pin = self.write(prefix + '.json', manifest)
        return {**target, 'manifest_path': pin['path'], 'manifest_sha256': pin['sha256'],
                'body_sha256': sha(body), 'provenance_sha256': sha(canonical(manifest)), 'context': manifest['context']}

    def source_fixture(self):
        api = self.acquisition
        job = api.prepare_job(self.catalog_index, sha(self.catalog_index.read_bytes()), (202403,), limits=dict(api._POLICIES))
        job_pin = self.write('data/runs/source403/preparation/job.json', job)
        metadata = {}
        for target in job['targets']:
            payload = ([{'c0': '1', 'c1': '202403'}] if target['role'] == 'cadaster'
                       else [{'id': rid, 'td': 3, 'a': 1, 'lid': rid} for rid in (92, 96, 101, 98)])
            metadata[target['target_key']] = self.bounded_source(target, payload)
        resolved = api.resolve_sources(job, metadata)
        refs = dict(metadata)
        for target in resolved['numeric_targets']:
            refs[target['target_key']] = self.bounded_source(target, [{'id': rid, 'e': '1', 'v': 0} for rid in (92, 96, 101, 98)])
        bootstrap = api.initialize_authority(job)
        with api.open_authority(job, bootstrap_sha256=bootstrap) as authority:
            metadata_receipt = None
            for key, ref in refs.items():
                reservation = api.reserve_attempt(authority, authority.targets[key], session_id='fixture')
                authority.commit('finish', attempt_id=reservation['attempt_id'], target_key=key, session_id='fixture',
                                 status='source_complete', retryable=False, source_ref=ref,
                                 observed_bytes=json.loads((self.root / ref['manifest_path']).read_bytes())['bytes'],
                                 observed_attempt_seconds=1, tree_extinct=True)
                if ref['role'] == 'dictionary':
                    metadata_receipt = api._receipt(authority, 'metadata')
            receipt = api._receipt(authority, 'values')
            authority.commit('recovery')
        checkpoint_a = resolved['checkpoints'][0]
        a = self.write('data/runs/source403/metadata/checkpoint-a.json', checkpoint_a)
        projection = ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'manifest_path',
                      'manifest_sha256', 'body_sha256', 'provenance_sha256')
        b = self.write('data/runs/source403/values/checkpoint-b.json',
                       {**checkpoint_a, 'phase': 'complete', 'checkpoint_a_sha256': a['sha256'],
                        'sources': sorted([{key: ref[key] for key in projection} for ref in refs.values()], key=lambda s: s['source_id'])})
        r = self.write('data/runs/source403/values/receipt.json', receipt)
        mr = self.write('data/runs/source403/metadata/receipt.json', metadata_receipt)
        resolution = self.write('data/runs/source403/metadata/resolution.json', resolved)
        evidence = {'job_sha256': job['job_sha256'], 'bootstrap_sha256': bootstrap,
                    'receipt': r, 'metadata_receipt': mr, 'checkpoint_a': a, 'checkpoint_b': b, 'resolution': resolution}
        entry = {'period': 202403, 'kind': 'accepted_sources', 'manifest_path': job_pin['path'],
                 'manifest_sha256': job_pin['sha256'], 'evidence': evidence}
        self.entries.append(entry)
        self.anchors[202403] = {'entry': copy.deepcopy(entry)}

    def prepare(self):
        self.write(self.reuse_index.relative_to(self.root).as_posix(), self.reuse)
        return self.batch._prepare_batch(self.catalog_index, sha(self.catalog_index.read_bytes()),
                                         self.reuse_index, sha(self.reuse_index.read_bytes()))

    def test_literal_window_and_native_catalog_identity(self):
        before = {p.relative_to(self.root).as_posix(): sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        self.write(self.reuse_index.relative_to(self.root).as_posix(), self.reuse)
        before[self.reuse_index.relative_to(self.root).as_posix()] = sha(self.reuse_index.read_bytes())
        draft = self.prepare()
        self.assertEqual(draft['contract'], 'financial-acquisition-batch-draft-v1')
        self.assertEqual(draft['selection'], {'perspective': 1005, 'reports': 'native-four', 'periods': WINDOW})
        self.assertEqual(draft['acquire_periods'], ACQUIRE)
        self.assertEqual(draft['reuse_periods'], REUSE)
        self.assertIs(draft['executable'], False)
        self.assertEqual([r['period'] for r in draft['reuse']], REUSE)
        for member, period, pointer in zip(draft['members'], ACQUIRE, ['/97', '/98', '/1', '/2', '/3', '/4', '/5']):
            job = member['job']
            self.assertEqual(job['acquisition_scope'], SCOPE + '/' + str(period))
            self.assertEqual(len(job['targets']), 2)
            descriptor = job['descriptors'][0]
            self.assertEqual(descriptor['catalog']['reference_pointer'], pointer)
            expected = [92, 96, 101, 98] if period < 202500 else [119, 107, 110, 118]
            self.assertEqual(descriptor['selection']['reports'], expected)
            self.assertEqual([r['report']['id'] for r in descriptor['reports']], expected)
            self.assertEqual(descriptor['reports'][1]['report']['s'], [{'id': 1004}, {'id': 1005}])
            self.assertEqual(descriptor['reports'][0]['report']['annotation'], {'unit': 'unknown', 'window': 'unknown'})
            self.assertEqual(len(descriptor['source_offers']), 7)
            for target in job['targets']:
                prefix = 'ifdata/' if period < 202500 else 'ifdata_2025_2030//'
                self.assertTrue(target['native_file'].startswith(prefix + str(period) + '/'))
                if period > 202500:
                    self.assertIn('%2F%2F', target['url'])
            self.assertEqual(member['job_sha256'], self.acquisition._job_hash(job))
        after = {p.relative_to(self.root).as_posix(): sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_fixed_caps_and_deterministic_readonly_reverification(self):
        draft = self.prepare()
        self.assertEqual(draft['caps'], {'per_member': {'attempts': 14, 'body_bytes': 330 * 1024 * 1024,
                                                       'scheduling_seconds': 1715},
                                        'total': {'attempts': 98, 'body_bytes': 2310 * 1024 * 1024,
                                                  'scheduling_seconds': 12005}})
        self.assertEqual(self.prepare(), draft)
        self.assertEqual(self.batch._verify_draft(draft), draft)
        self.assertTrue(next(r for r in draft['reuse'] if r['period'] == 202403)['authority']['receipt_is_historical'])

    def test_index_hash_and_duplicate_json_key_rejected(self):
        self.write(self.reuse_index.relative_to(self.root).as_posix(), self.reuse)
        with self.assertRaises(ValueError):
            self.batch._prepare_batch(self.catalog_index, '0' * 64, self.reuse_index, sha(self.reuse_index.read_bytes()))
        self.reuse_index.write_bytes(b'{"contract":"a","contract":"b"}')
        with self.assertRaises(ValueError):
            self.batch._prepare_batch(self.catalog_index, sha(self.catalog_index.read_bytes()), self.reuse_index, sha(self.reuse_index.read_bytes()))

    def test_reuse_schema_and_closed_identity_rejected(self):
        original = copy.deepcopy(self.reuse)
        mutations = [lambda d: d.update(nonce='new'), lambda d: d.update(scope='other'),
                     lambda d: d['entries'].pop(), lambda d: d['entries'].append(copy.deepcopy(d['entries'][0])),
                     lambda d: d['entries'][0].update(period=True), lambda d: d['entries'][0].update(period=202609),
                     lambda d: d['entries'][0].update(manifest_sha256='0' * 64),
                     lambda d: d['entries'][0].update(manifest_path='data/curated/../escape.json'),
                     lambda d: d['entries'][0].update(extra=1)]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.reuse = copy.deepcopy(original)
                mutation(self.reuse)
                with self.assertRaises(ValueError):
                    self.prepare()

    def test_catalog_body_and_external_pin_tamper_rejected(self):
        self.index['catalogs']['new']['body_sha256'] = '0' * 64
        self.write(self.catalog_index.relative_to(self.root).as_posix(), self.index)
        with self.assertRaises(ValueError):
            self.prepare()

    def test_catalog_body_ordinary_tamper_rejected(self):
        self.write('data/raw/catalog/old.bin', b'[]')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.prepare()

    def test_authenticated_catalog_still_checks_native_structure(self):
        cases = [lambda c: c['old'][97]['files'][2].update(sel=[{'id': 1004}]),
                 lambda c: c['old'][97].update(dt=True),
                 lambda c: c['old'].append(copy.deepcopy(c['old'][97])),
                 lambda c: c['old'][97]['files'][8]['trel'].update(id=True),
                 lambda c: c['new'][1]['files'][0].update(f='ifdata_2025_2030/202506/cadastro202506_1005.json'),
                 lambda c: c['new'][1]['files'][8]['trel'].update(s=[{'id': 1004}])]
        for mutation in cases:
            with self.subTest(mutation=mutation):
                catalogs = copy.deepcopy(self.catalogs)
                mutation(catalogs)
                for name, entries in catalogs.items():
                    payload = canonical(entries)
                    body = self.write(f'data/raw/catalog/{name}.bin', payload)
                    path = self.root / f'data/raw/catalog/{name}.json'
                    manifest = json.loads(path.read_bytes())
                    manifest.update(sha256=body['sha256'], bytes=len(payload))
                    pin = self.write(f'data/raw/catalog/{name}.json', manifest)
                    self.index['catalogs'][name].update(manifest_sha256=pin['sha256'], body_sha256=body['sha256'],
                                                       provenance_sha256=sha(canonical(manifest)))
                    self.acquisition._FROZEN[name] = (pin['sha256'], body['sha256'], CATALOG_URLS[name])
                self.write(self.catalog_index.relative_to(self.root).as_posix(), self.index)
                with self.assertRaisesRegex(ValueError, 'selection|period|report|announcement'):
                    self.prepare()

    def test_catalog_index_outside_root_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            index = Path(outside) / 'index.json'
            index.write_bytes(self.catalog_index.read_bytes())
            self.write(self.reuse_index.relative_to(self.root).as_posix(), self.reuse)
            with self.assertRaises(ValueError):
                self.batch._prepare_batch(index, sha(index.read_bytes()), self.reuse_index, sha(self.reuse_index.read_bytes()))

    def test_parquet_file_tamper_rejected(self):
        self.write('data/curated/reuse-202312/parts/cells.parquet', b'tampered')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_origin_body_tamper_rejected(self):
        self.write('data/raw/reuse/202503.bin', b'tampered')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_source403_sidecar_tamper_rejected(self):
        self.write('data/raw/source403/numeric-1.response.json', b'{}')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_current403_authority_missing_never_bootstrapped(self):
        job = json.loads((self.root / self.anchors[202403]['entry']['manifest_path']).read_bytes())
        self.acquisition._authority_paths(job)[0].joinpath('head.json').unlink()
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.prepare()

    def test_draft_coherent_changes_rejected(self):
        original = self.prepare()
        mutations = [lambda d: d.update(executable=True), lambda d: d.update(nonce='fresh'),
                     lambda d: d['selection']['periods'].append(202612), lambda d: d['selection'].update(perspective=1004),
                     lambda d: d['selection']['periods'].__setitem__(0, True), lambda d: d['policies'].update(attempts=3),
                     lambda d: d['caps']['total'].update(attempts=99), lambda d: d['members'][0].update(session_root='data/runs/new'),
                     lambda d: d['members'][0]['job']['descriptors'][0]['catalog'].update(reference_pointer='/98'),
                     lambda d: d['members'][0]['job']['descriptors'][0]['selection']['reports'].__setitem__(0, 119),
                     lambda d: d['members'][0]['job']['targets'][0].update(native_file='ifdata/202406/changed.json'),
                     lambda d: d['reuse'][0].update(manifest_sha256='0' * 64)]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                draft = copy.deepcopy(original)
                mutation(draft)
                for member in draft['members']:
                    member['job']['job_sha256'] = self.acquisition._job_hash(member['job'])
                    member['job_sha256'] = member['job']['job_sha256']
                with self.assertRaises(ValueError):
                    self.batch._verify_draft(draft)

    def test_draft_reverification_checks_input_files_again(self):
        draft = self.prepare()
        self.write('data/curated/reuse-202412/parts/cells.parquet', b'changed-after-prepare')
        with self.assertRaises(ValueError):
            self.batch._verify_draft(draft)

    def trusted_manifest_mutation(self, period, mutation):
        entry = next(entry for entry in self.entries if entry['period'] == period)
        path = self.root / entry['manifest_path']
        document = json.loads(path.read_bytes())
        mutation(document)
        path.write_bytes(canonical(document))
        entry['manifest_sha256'] = sha(path.read_bytes())
        self.anchors[period]['entry'] = copy.deepcopy(entry)

    def test_null_inventory_size_rejected(self):
        self.trusted_manifest_mutation(202312, lambda d: d['files'][1].update(bytes=None))
        with self.assertRaises(ValueError):
            self.prepare()

    def test_boolean_inventory_size_rejected(self):
        self.trusted_manifest_mutation(202412, lambda d: d['files'][1].update(bytes=True))
        with self.assertRaises(ValueError):
            self.prepare()

    def test_duplicate_inventory_path_rejected(self):
        self.trusted_manifest_mutation(202503, lambda d: d['files'].append(copy.deepcopy(d['files'][1])))
        with self.assertRaises(ValueError):
            self.prepare()

    def test_escape_inventory_rejected_even_in_pinned_manifest(self):
        self.trusted_manifest_mutation(202312, lambda d: d['files'][1].update(path='../source.json'))
        with self.assertRaises(ValueError):
            self.prepare()

    def test_pinned_manifest_wrong_profile_rejected(self):
        self.trusted_manifest_mutation(202312, lambda d: d.update(profile_sha256='0' * 64))
        with self.assertRaises(ValueError):
            self.prepare()
    def test_pinned_manifest_wrong_selection_rejected(self):
        self.trusted_manifest_mutation(202412, lambda d: d['selection'].update(perspective=1004))
        with self.assertRaises(ValueError):
            self.prepare()


class BatchAuthorityTests(unittest.TestCase):
    setUpClass = BatchCompositionTests.__dict__['setUpClass']
    inject = BatchCompositionTests.inject
    write = BatchCompositionTests.write
    parquet_fixture = BatchCompositionTests.parquet_fixture
    bounded_source = BatchCompositionTests.bounded_source
    source_fixture = BatchCompositionTests.source_fixture
    prepare = BatchCompositionTests.prepare
    def setUp(self):
        initialize = self.acquisition.initialize_authority
        run = self.acquisition.run_acquisition
        BatchCompositionTests.setUp(self)
        self.inject(self.acquisition, 'initialize_authority', initialize)
        self.inject(self.acquisition, 'run_acquisition', run)
        archive = importlib.import_module('bank_quality.archive')
        self.inject(archive, 'fetch_bounded', lambda *args, **kwargs: self.fail('Unexpected HTTP'))
        self.identity = {'reviewed_commit': 'b' * 40, 'files': {name: sha(name.encode()) for name in (
            'bank_quality/financial_acquisition.py', 'bank_quality/archive.py',
            'bank_quality/windows_acquisition.py', 'scripts/acquire-financial.py',
            'bank_quality/financial_acquisition_batch.py')},
            'runtime': {'path': 'C:/fixture/python.exe', 'sha256': 'a' * 64}}
        self.inject(self.batch, '_current_code_identity', lambda: copy.deepcopy(self.identity))
        self.pins = {'contract': 'financial-acquisition-code-pins-v1', 'reviewed_commit': 'b' * 40,
                     **copy.deepcopy(self.identity), 'policy_sha256': sha(canonical(self.batch._POLICIES))}

    def initialize(self, destination='data/runs/batch-fixture'):
        draft = self.write('data/runs/input/draft.json', self.prepare())
        return self.batch._initialize_batch(self.root / draft['path'], draft['sha256'],
                                           self.root / destination, code_pins=self.pins)

    def test_new_scope_validated_by_singleton_and_standalone_blocked(self):
        job = self.prepare()['members'][0]['job']
        try:
            targets = self.acquisition._execution_job(job)
        except ValueError as error:
            self.fail('Reviewed batch member rejected by trusted scope validator: ' + str(error))
        self.assertEqual(len(targets), 7)
        with self.assertRaisesRegex(ValueError, 'coordinator'):
            self.acquisition.open_authority(job, bootstrap_sha256='0' * 64).__enter__()

    def test_explicit_offline_initialization_and_external_pins(self):
        self.assertTrue(callable(getattr(self.batch, '_initialize_batch', None)), 'Offline initialization missing')
        refs = self.initialize()
        result = self.batch._verify_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                         bootstrap_sha256=refs['bootstrap_sha256'])
        self.assertEqual(result['totals']['attempts'], 0)
        self.assertEqual(len(result['members']), 7)
        with self.assertRaises(ValueError):
            self.initialize('data/runs/second-budget')

    def test_current_code_identity_mismatch_rejected_before_writes(self):
        self.assertTrue(callable(getattr(self.batch, '_initialize_batch', None)), 'Code identity gate missing')
        self.pins['files']['bank_quality/archive.py'] = 'c' * 64
        with self.assertRaises(ValueError):
            self.initialize()
        self.assertFalse((self.root / 'data/runs/batch-fixture').exists())

    def opened(self, refs, *, recover=False):
        return self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                      refs['bootstrap_sha256'], recover=recover)

    def recover(self, refs, number=1):
        return self.batch._recover_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                         bootstrap_sha256=refs['bootstrap_sha256'],
                                         output=self.root / f'data/runs/recovery-{number}.json')

    def terminal(self, member, start, context):
        api = self.acquisition
        session = self.root / start['session']
        session.mkdir(parents=True)
        job, phase = member['job'], start['phase']
        with api._open_authority(job, member['bootstrap_sha256'], coordinator=context) as authority:
            if phase == 'metadata':
                targets = job['targets']
            else:
                refs = {t['target_key']: authority.state['sources'][t['target_key']] for t in job['targets']}
                resolved = api.resolve_sources(job, refs)
                targets = resolved['numeric_targets']
            reports = job['descriptors'][0]['selection']['reports']
            for target in targets:
                payload = ([{'c0': '1', 'c1': str(member['period'])}] if target['role'] == 'cadaster'
                           else [{'id': rid, 'td': 3, 'a': 1, 'lid': rid} for rid in reports]
                           if target['role'] == 'dictionary' else {'id': target['area'], 'values': [{'e': 1, 'v': [{'i': rid, 'v': 0} for rid in reports]}]})
                source = self.bounded_source(target, payload)
                reservation = api.reserve_attempt(authority, target, session_id=session.name)
                authority.commit('finish', attempt_id=reservation['attempt_id'], target_key=target['target_key'],
                                 session_id=session.name, status='source_complete', retryable=False,
                                 source_ref=source, observed_bytes=len(canonical(payload)), observed_attempt_seconds=1, tree_extinct=True)
            receipt = self.write(start['session'] + '/receipt.json', api._receipt(authority, session.name))
            refs = {t['target_key']: authority.state['sources'][t['target_key']] for t in job['targets']}
            resolved = api.resolve_sources(job, refs)
            checkpoint = resolved['checkpoints'][0]
            if phase == 'values':
                metadata = next(p for p in context.batch.state['finished'].values()
                                if p['period'] == member['period'] and p['phase'] == 'metadata')
                projection = ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'manifest_path',
                              'manifest_sha256', 'body_sha256', 'provenance_sha256')
                checkpoint = {**checkpoint, 'phase': 'complete',
                              'checkpoint_a_sha256': metadata['result']['checkpoint']['sha256'],
                              'sources': sorted(checkpoint['sources'] + [{key: authority.state['sources'][t['target_key']][key]
                                             for key in projection} for t in targets], key=lambda ref: ref['source_id'])}
            proof = self.write(start['session'] + ('/checkpoint-a.json' if phase == 'metadata' else '/checkpoint-b.json'), checkpoint)
        return {'contract': 'financial-acquisition-phase-result-v1', 'status': 'complete',
                'guard': '', 'error': '', 'receipt': receipt, 'checkpoint': proof}

    def test_serial_phase_callable_uses_current_member_receipts_and_summed_journals(self):
        refs = self.initialize()
        dispatched = []
        def terminal(member, start, context):
            current = json.loads((self.root / 'data/runs/batch-fixture/head.json').read_bytes())
            self.assertGreater(current['sequence'], 0)
            self.assertEqual(context.batch.records[-1]['kind'], 'phase_start')
            dispatched.append((member['period'], start['phase']))
            return self.terminal(member, start, context)
        result = self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                        bootstrap_sha256=refs['bootstrap_sha256'], phase_callable=terminal)
        self.assertEqual(result['status'], 'verified', result)
        self.assertEqual(len(dispatched), 14)
        self.assertEqual(result['totals']['attempts'], 21)  # two metadata plus one native numeric shard per member
        self.assertEqual(len(result['finished_phases']), 14)
        self.assertEqual(result, self.batch._verify_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                                        bootstrap_sha256=refs['bootstrap_sha256']))
        result2 = self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                         bootstrap_sha256=refs['bootstrap_sha256'],
                                         phase_callable=lambda *args: self.fail('Already finished phase dispatched'))
        self.assertEqual(result, result2)

    def test_crash_after_member_finish_reconciles_before_new_dispatch_idempotently(self):
        class Crash(BaseException):
            pass
        refs = self.initialize()
        def crash(member, start, context):
            self.terminal(member, start, context)
            raise Crash()
        with self.assertRaises(Crash):
            self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                   bootstrap_sha256=refs['bootstrap_sha256'], phase_callable=crash)
        recovered = self.recover(refs)
        self.assertEqual(recovered['status'], 'verified', recovered)
        self.assertEqual(recovered['totals']['attempts'], 2)
        self.assertEqual(len(recovered['finished_phases']), 1)
        self.assertEqual(recovered, self.recover(refs, 2))
        with self.opened(refs) as batch:
            self.assertEqual(batch.records[-1]['kind'], 'phase_finish')
            self.assertTrue(batch.records[-1]['recovered'])

    def test_partial_initialization_scope_binding_never_renews(self):
        original = self.acquisition._write_exclusive
        def interrupted(path, value):
            if path.name == 'bootstrap.json' and path.parent.parent.name == 'financial-acquisition-authority':
                raise OSError('fixture interruption')
            return original(path, value)
        with patch.object(self.acquisition, '_write_exclusive', interrupted):
            with self.assertRaises(OSError):
                self.initialize()
        with self.assertRaisesRegex(ValueError, 'binding'):
            self.initialize('data/runs/retry-after-partial')
        self.assertFalse((self.root / 'data/runs/retry-after-partial').exists())

    def test_missing_batch_binding_persists_halt_without_new_budget(self):
        refs = self.initialize()
        binding, _ = self.batch._batch_paths()
        binding.unlink()
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertTrue((self.root / 'data/runs/batch-fixture/halt.json').is_file())

    def test_pending_member_orphan_stays_charged_and_halts_without_dispatch(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
            start = self.batch._start_phase(batch, member, 'metadata')
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                    coordinator=self.batch._MemberContext(batch, member)) as authority:
                self.acquisition.reserve_attempt(authority, member['job']['targets'][0], session_id=Path(start['session']).name)
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['totals']['attempts'], 1)
        self.assertEqual(result['totals']['body_bytes'], 5 * 1024 * 1024)
        self.assertEqual(result['totals']['attempt_seconds'], 120)
        again = self.recover(refs, 2)
        self.assertEqual(result, again)
        self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                               bootstrap_sha256=refs['bootstrap_sha256'],
                               phase_callable=lambda *args: self.fail('Halted batch dispatched'))

    def test_partial_batch_tail_persists_halt(self):
        refs = self.initialize()
        journal = self.root / 'data/runs/batch-fixture/journal.jsonl'
        journal.write_bytes(b'{"partial":')
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(journal.read_bytes(), b'{"partial":')

    def test_two_metadata_starts_can_be_active_without_changing_singleton_claims(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            self.batch._start_phase(batch, batch.bundle['members'][0], 'metadata')
            second = self.batch._start_phase(batch, batch.bundle['members'][1], 'metadata')
            self.assertEqual(second['period'], 202409)
            with self.assertRaises(ValueError):
                self.batch._start_phase(batch, batch.bundle['members'][2], 'metadata')

    def test_live_or_unknown_worker_identity_keeps_reservation_and_halts(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
            start = self.batch._start_phase(batch, member, 'metadata')
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                    coordinator=self.batch._MemberContext(batch, member)) as authority:
                reservation = self.acquisition.reserve_attempt(authority, member['job']['targets'][0], session_id=Path(start['session']).name)
                authority.commit('identity', attempt_id=reservation['attempt_id'], target_key=reservation['target_key'],
                                 session_id=reservation['session_id'], identity={'pid': 77, 'creation_time': 8, 'contained': True})
        self.inject(self.acquisition, 'identity_extinct', lambda identity: False)
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['members'][0]['pending_attempts'], 1)
        self.assertEqual(result['totals']['attempt_seconds'], 120)

    def test_stale_empty_receipt_and_session_folder_cannot_prove_success(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
            start = self.batch._start_phase(batch, member, 'metadata')
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                    coordinator=self.batch._MemberContext(batch, member)) as authority:
                self.write(start['session'] + '/receipt.json', self.acquisition._receipt(authority, Path(start['session']).name))
            self.write(start['session'] + '/checkpoint-a.json', {})
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['totals']['attempts'], 0)

    def test_mutated_member_pin_fake_context_and_closed_context_refused(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
            context = self.batch._MemberContext(batch, member)
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=context):
                pass
            with self.assertRaises(ValueError):
                with self.acquisition._open_authority(member['job'], 'c' * 64, coordinator=context):
                    pass
            with self.assertRaises(ValueError):
                with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator={}):
                    pass
        with self.assertRaisesRegex(ValueError, 'active coordinator'):
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=context):
                pass

    def failing_terminal(self, member, start, context, guard):
        api = self.acquisition
        (self.root / start['session']).mkdir(parents=True)
        with api._open_authority(member['job'], member['bootstrap_sha256'], coordinator=context) as authority:
            authority.commit('guard_failure', target_key=member['job']['targets'][0]['target_key'],
                             session_id=Path(start['session']).name, status='source_schema_failed', guard=guard)
            receipt = self.write(start['session'] + '/receipt.json', api._receipt(authority, Path(start['session']).name))
        return {'contract': 'financial-acquisition-phase-result-v1', 'status': 'failed',
                'guard': guard, 'error': 'fixture terminal guard', 'receipt': receipt, 'checkpoint': None}

    def test_terminal_failure_halt_requires_three_members_or_two_matching_guards(self):
        refs = self.initialize()
        dispatched = []
        guards = iter(('schema', 'deadline', 'schema'))
        def phase(member, start, context):
            dispatched.append(member['period'])
            return self.failing_terminal(member, start, context, next(guards))
        result = self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                        bootstrap_sha256=refs['bootstrap_sha256'], phase_callable=phase)
        self.assertEqual(len(dispatched), 3)
        self.assertEqual(result['halt'], 'three_failed_members')

    def test_two_matching_guard_conclusions_halt_in_durable_finish_order(self):
        refs = self.initialize()
        dispatched = []
        def phase(member, start, context):
            dispatched.append(member['period'])
            return self.failing_terminal(member, start, context, 'schema')
        result = self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                        bootstrap_sha256=refs['bootstrap_sha256'], phase_callable=phase)
        self.assertEqual(len(dispatched), 2)
        self.assertEqual(result['halt'], 'consecutive_guard')

    def test_initialization_checks_current_head_but_offline_verification_accepts_later_document_head(self):
        self.pins['reviewed_commit'] = 'c' * 40
        with self.assertRaisesRegex(ValueError, 'HEAD'):
            self.initialize()
        self.pins['reviewed_commit'] = 'b' * 40
        refs = self.initialize()
        self.identity['reviewed_commit'] = 'c' * 40
        self.assertEqual(self.batch._verify_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                         bootstrap_sha256=refs['bootstrap_sha256'])['status'], 'verified')

    def test_member_boundary_rechecks_small_immutable_pins_without_reuse_corpus(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
            with patch.object(self.batch, '_verify_draft', side_effect=AssertionError('Repeated corpus verification')):
                with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                                                      coordinator=self.batch._MemberContext(batch, member)):
                    pass
            binding, _ = self.batch._batch_paths()
            document = json.loads(binding.read_bytes())
            document['bundle_sha256'] = 'c' * 64
            binding.write_bytes(canonical(document))
            with self.assertRaises(ValueError):
                with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                                                      coordinator=self.batch._MemberContext(batch, member)):
                    pass

    def test_missing_batch_head_persists_halt(self):
        refs = self.initialize()
        (self.root / 'data/runs/batch-fixture/head.json').unlink()
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertFalse((self.root / 'data/runs/batch-fixture/head.json').exists())

    def test_two_recovered_terminal_outcomes_with_unproven_order_halt(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            for index, member in enumerate(batch.bundle['members'][:2]):
                start = self.batch._start_phase(batch, member, 'metadata')
                context = self.batch._MemberContext(batch, member)
                terminal = self.terminal(member, start, context) if index == 0 else self.failing_terminal(member, start, context, 'schema')
                self.write(start['session'] + '/terminal.json', terminal)
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['halt'], 'recovered_phase_order_unprovable')
        self.assertEqual(len(result['pending_phases']), 2)
        self.assertEqual(result['totals']['attempts'], 2)
        self.assertEqual(result, self.recover(refs, 2))

    def test_new_scope_standalone_apis_and_v1_worker_refuse_before_launch(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
        api = self.acquisition
        kwargs = {'bootstrap_sha256': member['bootstrap_sha256']}
        calls = (lambda: api.initialize_authority(member['job']),
                 lambda: api.verify_authority(self.root / member['job_path'], member['job_sha256'], **kwargs),
                 lambda: api.recover_authority(self.root / member['job_path'], member['job_sha256'],
                                              output=self.root / 'data/runs/standalone-recovery.json', **kwargs),
                 lambda: api.run_acquisition(self.root / member['job_path'], member['job_sha256'],
                                            self.root / 'data/runs/standalone-session', phase='metadata', **kwargs),
                 lambda: api._worker_authorization({'job_path': member['job_path'], 'job_sha256': member['job_sha256']}))
        for index, call in enumerate(calls):
            with self.subTest(api=index), self.assertRaisesRegex(ValueError, 'coordinator'):
                call()
        self.assertFalse((self.root / 'data/runs/standalone-session').exists())
        self.assertFalse((self.root / 'data/runs/standalone-recovery.json').exists())

    def test_new_execution_jobs_reject_mutations_with_coherent_candidate_hash(self):
        original = self.prepare()['members'][0]['job']
        changes = (lambda j: j.update(version=True), lambda j: j.update(nonce='renew'),
                   lambda j: j.update(acquisition_scope=SCOPE + '/202403'),
                   lambda j: j['policies'].update(attempts=True), lambda j: j['policies'].update(attempts=1),
                   lambda j: j['descriptors'].append(copy.deepcopy(j['descriptors'][0])),
                   lambda j: j['descriptors'][0]['selection'].update(period=202409),
                   lambda j: j['targets'][0].update(url='https://fixture/arbitrary'),
                   lambda j: j['targets'].append(copy.deepcopy(j['targets'][0])))
        for change in changes:
            job = copy.deepcopy(original)
            change(job)
            job['job_sha256'] = self.acquisition._job_hash(job)
            with self.subTest(job=job['job_sha256']), self.assertRaises(ValueError):
                self.acquisition._execution_job(job)

    def test_values_start_requires_complete_metadata_barrier(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
            start = self.batch._start_phase(batch, member, 'metadata')
            terminal = self.terminal(member, start, self.batch._MemberContext(batch, member))
            batch.append('phase_finish', phase_id=start['phase_id'], result=terminal, recovered=False)
            with self.assertRaisesRegex(ValueError, 'barrier'):
                self.batch._start_phase(batch, member, 'values')

    def test_batch_head_fsync_failure_prevents_phase_callable(self):
        refs = self.initialize()
        original = self.acquisition._replace_head
        def head_failure(folder, head):
            if folder == self.root / 'data/runs/batch-fixture' and head['sequence'] > 0:
                raise OSError('fixture batch head fsync')
            return original(folder, head)
        with patch.object(self.acquisition, '_replace_head', head_failure), self.assertRaises(OSError):
            self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                   bootstrap_sha256=refs['bootstrap_sha256'],
                                   phase_callable=lambda *args: self.fail('Head durability failure dispatched'))
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['totals']['attempts'], 0)

    def test_unknown_identity_error_keeps_pending_reservation(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
            start = self.batch._start_phase(batch, member, 'metadata')
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                    coordinator=self.batch._MemberContext(batch, member)) as authority:
                reserve = self.acquisition.reserve_attempt(authority, member['job']['targets'][0], session_id=Path(start['session']).name)
                authority.commit('identity', attempt_id=reserve['attempt_id'], target_key=reserve['target_key'],
                                 session_id=reserve['session_id'], identity={'pid': 77, 'creation_time': 8, 'contained': True})
        with patch.object(self.acquisition, 'identity_extinct', side_effect=OSError('fixture access denied')):
            result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['members'][0]['pending_attempts'], 1)
        self.assertEqual(result['totals']['body_bytes'], 5 * 1024 * 1024)

    def test_new_bundle_and_code_pins_closed_schema_reject_boolean_and_extra_keys(self):
        for mutation in (lambda pins: pins.update(nonce='renew'),
                         lambda pins: pins['files'].update(extra='c' * 64),
                         lambda pins: pins['runtime'].update(sha256=True),
                         lambda pins: pins.update(reviewed_commit='not-full-head')):
            pins = copy.deepcopy(self.pins)
            mutation(pins)
            with self.subTest(pins=pins), self.assertRaises(ValueError):
                self.batch._code_identity(pins, current_head=True)

    def test_batch_journal_wrong_sequence_or_extra_key_never_repairs(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            self.batch._start_phase(batch, batch.bundle['members'][0], 'metadata')
        journal = self.root / 'data/runs/batch-fixture/journal.jsonl'
        record = json.loads(journal.read_bytes())
        record['sequence'] = True
        record['record_sha256'] = sha(canonical({key: value for key, value in record.items() if key != 'record_sha256'}))
        raw = canonical(record) + b'\n'
        journal.write_bytes(raw)
        result = self.recover(refs)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(journal.read_bytes(), raw)


    def test_active_second_metadata_can_finish_after_persisted_halt_without_corrupting_head(self):
        refs = self.initialize()
        with self.opened(refs) as batch:
            first, second = batch.bundle['members'][:2]
            self.batch._start_phase(batch, first, 'metadata')
            start = self.batch._start_phase(batch, second, 'metadata')
            terminal = self.terminal(second, start, self.batch._MemberContext(batch, second))
            batch.halt('fixture critical containment')
            batch.append('phase_finish', phase_id=start['phase_id'], result=terminal, recovered=False)
        try:
            result = self.batch._verify_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                               bootstrap_sha256=refs['bootstrap_sha256'])
        except ValueError as error:
            self.fail('Durable finish after halt corrupted ledger/head: ' + str(error))
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['halt'], 'fixture critical containment')


    def completed_metadata(self, refs):
        with self.opened(refs) as batch:
            for member in batch.bundle['members']:
                start = self.batch._start_phase(batch, member, 'metadata')
                result = self.terminal(member, start, self.batch._MemberContext(batch, member))
                self.batch._proof(batch, start, result)
                self.write(start['session'] + '/terminal.json', result)
                batch.append('phase_finish', phase_id=start['phase_id'], result=result, recovered=False)
            return copy.deepcopy(next(iter(batch.state['finished'].values()))), self.batch._totals(batch)

    def damaged_finished_proof_blocks_recovery_and_resume(self, proof_name, *, recovery_first=False):
        refs = self.initialize()
        finished, before = self.completed_metadata(refs)
        path = self.root / finished['result'][proof_name]['path']
        path.write_bytes(b'{}')
        journal = self.root / 'data/runs/batch-fixture/journal.jsonl'
        head = self.root / 'data/runs/batch-fixture/head.json'
        original_journal, original_head = journal.read_bytes(), head.read_bytes()
        if recovery_first:
            self.assertEqual(self.recover(refs, 2)['status'], 'halted')
        called = []
        def unexpected(member, start, context):
            called.append(start['phase'])
            raise AssertionError('Unproven finished phase crossed resume boundary')
        try:
            resumed = self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                              bootstrap_sha256=refs['bootstrap_sha256'], phase_callable=unexpected)
        except AssertionError as error:
            self.fail(str(error))
        self.assertEqual(resumed['status'], 'halted')
        recovered = self.recover(refs)
        self.assertEqual(recovered['status'], 'halted')
        self.assertEqual(resumed['totals'], before['totals'])
        self.assertEqual(recovered['totals'], before['totals'])
        self.assertEqual(called, [])
        self.assertEqual(path.read_bytes(), b'{}')
        self.assertEqual(journal.read_bytes(), original_journal)
        self.assertEqual(head.read_bytes(), original_head)
        self.assertTrue((self.root / 'data/runs/batch-fixture/halt.json').is_file())

    def test_finished_checkpoint_corruption_blocks_recovery_and_resume(self):
        self.damaged_finished_proof_blocks_recovery_and_resume('checkpoint')

    def test_finished_receipt_corruption_blocks_recovery_and_resume(self):
        self.damaged_finished_proof_blocks_recovery_and_resume('receipt')

    def test_finished_checkpoint_corruption_blocks_direct_recovery(self):
        self.damaged_finished_proof_blocks_recovery_and_resume('checkpoint', recovery_first=True)

    def test_finished_receipt_corruption_blocks_direct_recovery(self):
        self.damaged_finished_proof_blocks_recovery_and_resume('receipt', recovery_first=True)

    def test_valid_historical_metadata_after_values_accepted_by_recovery_and_resume(self):
        refs = self.initialize()
        completed = self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                           bootstrap_sha256=refs['bootstrap_sha256'], phase_callable=self.terminal)
        self.assertEqual(len(completed['finished_phases']), 14)
        with self.opened(refs) as batch:
            for finished in batch.state['finished'].values():
                if finished['phase'] == 'metadata':
                    member = next(m for m in batch.bundle['members'] if m['period'] == finished['period'])
                    with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                           coordinator=self.batch._MemberContext(batch, member)) as authority:
                        receipt = json.loads((self.root / finished['result']['receipt']['path']).read_bytes())
                        self.assertLess(receipt['sequence'], len(authority.records))
        self.assertEqual(completed, self.recover(refs))
        resumed = self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                         bootstrap_sha256=refs['bootstrap_sha256'],
                                         phase_callable=lambda *args: self.fail('Completed phase dispatched'))
        self.assertEqual(completed, resumed)

    def physical_job_change_refused_at_active_member_boundary(self, *, delete):
        refs = self.initialize()
        with self.opened(refs) as batch:
            member = batch.bundle['members'][0]
            path = self.root / member['job_path']
            if delete:
                path.unlink()
            else:
                path.write_bytes(b'{}')
            with patch.object(self.batch, '_verify_draft', side_effect=AssertionError('Repeated full reuse authentication')):
                with self.assertRaises((ValueError, OSError)):
                    with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                           coordinator=self.batch._MemberContext(batch, member)):
                        pass

    def test_physical_job_corruption_refused_inside_active_context(self):
        self.physical_job_change_refused_at_active_member_boundary(delete=False)

    def test_physical_job_deletion_refused_inside_active_context(self):
        self.physical_job_change_refused_at_active_member_boundary(delete=True)


if __name__ == '__main__':
    unittest.main()


class PhaseReplayDataTests(unittest.TestCase):
    inject = BatchCompositionTests.inject
    write = BatchCompositionTests.write
    parquet_fixture = BatchCompositionTests.parquet_fixture
    source_fixture = BatchCompositionTests.source_fixture
    prepare = BatchCompositionTests.prepare
    bounded_source = BatchCompositionTests.bounded_source
    initialize = BatchAuthorityTests.initialize
    terminal = BatchAuthorityTests.terminal

    @classmethod
    def setUpClass(cls):
        BatchCompositionTests.setUpClass.__func__(cls)

    def setUp(self):
        BatchAuthorityTests.setUp(self)

    def test_phase_replay_rederives_barrier_in_closed_data(self):
        refs = self.initialize()
        self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                               bootstrap_sha256=refs['bootstrap_sha256'], phase_callable=self.terminal)
        raw = (self.root / 'data/runs/batch-fixture/journal.jsonl').read_bytes()
        records = [json.loads(line) for line in raw.splitlines()]
        bundle = json.loads((self.root / refs['bundle_path']).read_bytes())
        self.assertTrue(callable(getattr(self.batch, '_replay_phase_records', None)), 'Pure phase replay missing')
        with patch.object(self.batch, '_Batch', side_effect=AssertionError('active batch')), \
             patch.object(self.batch, '_MemberContext', side_effect=AssertionError('active context')), \
             patch.object(self.batch, '_path', side_effect=AssertionError('physical IO in pure helper')):
            replay = self.batch._replay_phase_records(records, anchored_bundle={
                'bundle': bundle, 'bundle_sha256': refs['bundle_sha256'],
                'bootstrap_sha256': refs['bootstrap_sha256']})
        self.assertEqual(len(replay['state']['finished']), 14)
        self.assertEqual(replay['head'], json.loads((self.root / 'data/runs/batch-fixture/head.json').read_bytes()))
        self.assertEqual(json.loads(canonical(replay)), replay)
        before = copy.deepcopy(records)
        records[0]['bundle_sha256'] = 'f' * 64
        records[0]['record_sha256'] = sha(canonical({k: v for k, v in records[0].items() if k != 'record_sha256'}))
        with self.assertRaises(ValueError):
            self.batch._replay_phase_records(records, anchored_bundle={
                'bundle': bundle, 'bundle_sha256': refs['bundle_sha256'],
                'bootstrap_sha256': refs['bootstrap_sha256']})
        self.assertNotEqual(records, before)

    def test_phase_source_proof_joins_receipt_prefix_and_a_to_b_without_io(self):
        refs = self.initialize()
        self.batch._run_serial(self.root / refs['bundle_path'], refs['bundle_sha256'],
                               bootstrap_sha256=refs['bootstrap_sha256'], phase_callable=self.terminal)
        self.assertTrue(callable(getattr(self.batch, '_prove_phase_sources', None)), 'Pure phase sources missing')
        bundle = json.loads((self.root / refs['bundle_path']).read_bytes())
        phase = self.batch._replay_phase_records([
            json.loads(line) for line in (self.root / 'data/runs/batch-fixture/journal.jsonl').read_bytes().splitlines()],
            anchored_bundle={'bundle': bundle, 'bundle_sha256': refs['bundle_sha256'],
                             'bootstrap_sha256': refs['bootstrap_sha256']})
        member = bundle['members'][0]
        targets, policy = self.acquisition._execution_job(member['job']), self.acquisition._limits(member['job'])
        replay = self.acquisition._replay_member_records([
            json.loads(line) for line in (self.root / member['authority_path'] / 'journal.jsonl').read_bytes().splitlines()],
            job_identity=member['job_sha256'], targets=targets, policy=policy)
        member_data = {**replay, 'targets': targets, 'policy': policy}
        phases = {s['phase']: s for s in phase['state']['finished'].values() if s['period'] == member['period']}
        metadata = phases['metadata']['result']['checkpoint']
        start = phases['values']
        result = start['result']
        data = {'start': {k: v for k, v in start.items() if k != 'result'}, 'result': result,
                'receipt': self.batch._read(result['receipt']), 'checkpoint': self.batch._read(result['checkpoint']),
                'resolved': self.acquisition.resolve_sources(member['job'], {
                    t['target_key']: replay['state']['sources'][t['target_key']] for t in member['job']['targets']}),
                'metadata_checkpoint_ref': metadata, 'metadata_checkpoint': self.batch._read(metadata)}
        with patch.object(self.batch, '_path', side_effect=AssertionError('IO in pure helper')), \
             patch.object(self.batch, '_MemberContext', side_effect=AssertionError('active context')):
            proof = self.batch._prove_phase_sources(data, member_data, anchored_member=member)
        self.assertEqual(proof['checkpoint'], data['checkpoint'])
        self.assertEqual(proof['receipt_prefix']['head'], replay['head'])
        bad = copy.deepcopy(data)
        bad['checkpoint']['checkpoint_a_sha256'] = 'f' * 64
        with self.assertRaises(ValueError):
            self.batch._prove_phase_sources(bad, member_data, anchored_member=member)


class BatchSchedulerTests(unittest.TestCase):
    setUpClass = BatchAuthorityTests.__dict__['setUpClass']
    setUp = BatchAuthorityTests.setUp
    inject = BatchAuthorityTests.inject
    write = BatchAuthorityTests.write
    parquet_fixture = BatchAuthorityTests.parquet_fixture
    bounded_source = BatchAuthorityTests.bounded_source
    source_fixture = BatchAuthorityTests.source_fixture
    prepare = BatchAuthorityTests.prepare
    initialize = BatchAuthorityTests.initialize
    terminal = BatchAuthorityTests.terminal
    @unittest.skipUnless(__import__('os').name == 'nt', 'Native Windows member claims required')
    def test_parallel_scheduler_barrier_and_member_isolation(self):
        import threading
        refs = self.initialize()
        barrier = threading.Barrier(2)
        lock = threading.Lock()
        active = {'metadata': 0, 'values': 0}
        peak = dict(active)
        completed = []
        def phase(member, start, context):
            kind = start['phase']
            with lock:
                active[kind] += 1
                peak[kind] = max(peak[kind], active[kind])
                if kind == 'values':
                    self.assertEqual(len([p for p in completed if p == 'metadata']), 7)
                    self.assertEqual(active['metadata'], 0)
            if kind == 'metadata' and member['period'] in self.batch._ACQUIRE[:2]:
                barrier.wait(10)
            result = self.terminal(member, start, context)
            with lock:
                completed.append(kind)
                active[kind] -= 1
            return result
        self.assertTrue(callable(getattr(self.batch, '_run_scheduler', None)), 'Parallel scheduler missing')
        from bank_quality.windows_acquisition import exclusive_claim
        with patch.object(self.acquisition, '_claim', exclusive_claim):
            result = self.batch._run_scheduler(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=2, phase_callable=phase)
        self.assertEqual(result['status'], 'complete', result)
        self.assertEqual(result['missing_periods'], [])
        self.assertEqual(peak, {'metadata': 2, 'values': 1})

    def test_run_workers_are_strict_and_head_checked_before_dispatch(self):
        self.assertTrue(callable(getattr(self.batch, '_run_batch', None)), 'Batch run missing')
        refs = self.initialize()
        for workers in (True, 0, 3, 1.0):
            with self.assertRaises(ValueError):
                self.batch._run_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                    bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=workers)
        self.identity['reviewed_commit'] = 'c' * 40
        with self.assertRaisesRegex(ValueError, 'HEAD'):
            self.batch._run_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'])


    def test_v2_worker_uses_start_prefix_and_current_member_reservation(self):
        refs = self.initialize()
        with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as batch:
            member = batch.bundle['members'][0]
            start = self.batch._start_phase(batch, member, 'metadata')
            context = self.batch._MemberContext(batch, member)
            context.start = start
            worker_context = self.batch._transport_context(context)
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=context) as authority:
                target = member['job']['targets'][0]
                reserve = self.acquisition.reserve_attempt(authority, target, session_id=Path(start['session']).name)
                authority.commit('identity', attempt_id=reserve['attempt_id'], target_key=target['target_key'],
                    session_id=Path(start['session']).name, identity={'pid': 123, 'creation_time': 1, 'contained': True},
                    spec_path='data/runs/spec.json', spec_sha256='a' * 64)
                spec = {'contract': 'financial-acquisition-worker-v2', 'batch_context': worker_context,
                    'job_path': member['job_path'], 'job_sha256': member['job_sha256'],
                    'bootstrap_sha256': member['bootstrap_sha256'], 'attempt_id': reserve['attempt_id'],
                    'target_key': target['target_key'], 'body_budget_bytes': reserve['reserved_bytes'],
                    'parent_identity': {'pid': 456, 'creation_time': 2},
                    'output_path': start['session'] + '/attempt-' + reserve['attempt_id']}
                # A second phase and a partial new tail cannot race the pinned prefix.
                self.batch._start_phase(batch, batch.bundle['members'][1], 'metadata')
                with (batch.folder / 'journal.jsonl').open('ab') as stream:
                    stream.write(b'{"partial":')
                with patch.object(self.acquisition, 'verify_worker_ancestry'):
                    authorized, _ = self.acquisition._worker_authorization(spec)
                    self.assertEqual(authorized, member['job'])
                    bad = copy.deepcopy(spec)
                    bad['output_path'] = 'data/runs/wrong/attempt-' + reserve['attempt_id']
                    with self.assertRaises(ValueError):
                        self.acquisition._worker_authorization(bad)
                    (self.root / member['job_path']).write_bytes(b'{}')
                    with self.assertRaises(ValueError):
                        self.acquisition._worker_authorization(spec)


    failing_terminal = BatchAuthorityTests.failing_terminal

    def test_parallel_halt_allows_one_inflight_finish_but_no_new_start(self):
        import threading
        refs = self.initialize()
        first, second = self.batch._ACQUIRE[:2]
        ready = threading.Event()
        concluded = threading.Event()
        dispatched = []
        original = self.batch._Batch.append
        def append(batch, kind, **details):
            result = original(batch, kind, **details)
            if kind == 'phase_finish' and batch.halted:
                concluded.set()
            return result
        def phase(member, start, context):
            dispatched.append(member['period'])
            if member['period'] == first:
                self.assertTrue(ready.wait(5))
                return self.failing_terminal(member, start, context, 'containment')
            ready.set()
            self.assertTrue(concluded.wait(5))
            return self.terminal(member, start, context)
        with patch.object(self.batch._Batch, 'append', append):
            result = self.batch._run_scheduler(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=2, phase_callable=phase)
        self.assertEqual(sorted(dispatched), [first, second])
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['halt'], 'critical_containment')
        self.assertEqual(result['pending_phases'], [])
        self.assertEqual(len(result['finished_phases']), 2)
        self.assertEqual(len(result['missing_periods']), 7)

    def test_run_revalidates_all_finished_proofs_before_new_dispatch(self):
        refs = self.initialize()
        with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as batch:
            member = batch.bundle['members'][0]
            start = self.batch._start_phase(batch, member, 'metadata')
            result = self.terminal(member, start, self.batch._MemberContext(batch, member))
            self.batch._proof(batch, start, result)
            batch.append('phase_finish', phase_id=start['phase_id'], result=result, recovered=False)
        damaged = self.root / result['checkpoint']['path']
        damaged.write_bytes(b'{}')
        result = self.batch._run_scheduler(self.root / refs['bundle_path'], refs['bundle_sha256'],
            bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=2,
            phase_callable=lambda *args: self.fail('Dispatch crossed corrupted historical proof'))
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(damaged.read_bytes(), b'{}')

    def test_v2_thin_context_rejects_all_code_pins_without_rehashing_reuse(self):
        refs = self.initialize()
        with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as batch:
            member = batch.bundle['members'][0]
            context = self.batch._MemberContext(batch, member)
            context.start = self.batch._start_phase(batch, member, 'metadata')
            worker = self.batch._transport_context(context)
            with patch.object(self.batch, '_verify_draft', side_effect=AssertionError('Repeated full reuse authentication')):
                self.batch._worker_context(member['job'], worker)
                for name in self.identity['files']:
                    original = self.identity['files'][name]
                    self.identity['files'][name] = 'c' * 64
                    with self.assertRaisesRegex(ValueError, 'code/runtime'):
                        self.batch._worker_context(member['job'], worker)
                    self.identity['files'][name] = original
                self.identity['runtime']['sha256'] = 'c' * 64
                with self.assertRaisesRegex(ValueError, 'code/runtime'):
                    self.batch._worker_context(member['job'], worker)


    @unittest.skipUnless(__import__('os').name == 'nt', 'Native Windows coordinator claims required')
    def test_live_batch_coordinator_excludes_second_owner(self):
        from bank_quality.windows_acquisition import exclusive_claim
        refs = self.initialize()
        with patch.object(self.acquisition, '_claim', exclusive_claim):
            with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']):
                with self.assertRaises(OSError):
                    with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']):
                        self.fail('Second batch coordinator acquired live claim')

    def test_production_run_and_v2_worker_protocol_with_synthetic_transport(self):
        import shutil
        refs = self.initialize()
        specs = []
        def fetch(url, output, label, context, *, body_budget_bytes, timeout_seconds):
            spec = next(s for s in specs if s['attempt_id'] == label)
            job, target = self.acquisition._worker_authorization(spec)
            reports = job['descriptors'][0]['selection']['reports']
            payload = ([{'c0': '1', 'c1': str(context['period'])}] if target['role'] == 'cadaster'
                       else [{'id': rid, 'td': 3, 'a': 1, 'lid': rid} for rid in reports]
                       if target['role'] == 'dictionary' else {'id': target['area'], 'values': [{'e': 1, 'v': [{'i': rid, 'v': 0} for rid in reports]}]})
            source = self.bounded_source(target, payload)
            original = self.root / source['manifest_path']
            manifest = json.loads(original.read_bytes())
            manifest['body_budget_bytes'] = body_budget_bytes
            manifest['manifest_path'] = original.name
            for name in (manifest['body_path'], manifest['response_metadata_path']):
                shutil.copyfile(original.parent / name, output / name)
            (output / original.name).write_bytes(canonical(manifest))
            return manifest
        def launch(path, pin, *, deadline_seconds, before_resume, cancel_event):
            spec = json.loads(path.read_bytes())
            self.assertEqual(spec['contract'], 'financial-acquisition-worker-v2')
            self.assertFalse(cancel_event.is_set())
            specs.append(spec)
            before_resume({'pid': 123, 'creation_time': 456, 'contained': True})
            self.acquisition._worker_main(path, pin)
            return {'tree_extinct': True, 'deadline_reached': False, 'deadline_overshoot_seconds': 0,
                    'exit_code': 0, 'elapsed_seconds': 1.0}
        # This protocol roundtrip is synthetic on every host; native containment
        # is exercised separately by the Windows integration tests.
        with patch.object(self.acquisition, 'require_supported'), \
                patch.object(self.acquisition, '_current_identity', return_value={'pid': 7, 'creation_time': 9}), \
                patch('bank_quality.windows_acquisition._kernel',
                      side_effect=AssertionError('Synthetic transport must not access native Win32')), \
                patch.object(self.acquisition, 'run_contained_attempt', side_effect=launch), \
                patch.object(self.acquisition, 'verify_worker_ancestry'), \
                patch('bank_quality.archive.fetch_bounded', side_effect=fetch):
            result = self.batch._run_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=2)
        self.assertEqual(result['status'], 'complete', result)
        self.assertEqual(len(specs), 21)
        self.assertEqual(result['totals']['attempts'], 21)
        self.assertEqual(result['pending_phases'], [])
        self.assertEqual(result['missing_periods'], [])

        with self.assertRaisesRegex(ValueError, 'reservation'):
            self.acquisition._worker_authorization(specs[0])

    def test_scheduler_three_failed_members_and_guard_streak(self):
        refs = self.initialize()
        guards = iter(('schema', 'deadline', 'schema'))
        dispatched = []
        def phase(member, start, context):
            dispatched.append(member['period'])
            return self.failing_terminal(member, start, context, next(guards))
        result = self.batch._run_scheduler(self.root / refs['bundle_path'], refs['bundle_sha256'],
            bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=1, phase_callable=phase)
        self.assertEqual(len(dispatched), 3)
        self.assertEqual(result['halt'], 'three_failed_members')

    def test_scheduler_two_identical_guards_stop_dispatch(self):
        refs = self.initialize()
        dispatched = []
        def phase(member, start, context):
            dispatched.append(member['period'])
            return self.failing_terminal(member, start, context, 'schema')
        result = self.batch._run_scheduler(self.root / refs['bundle_path'], refs['bundle_sha256'],
            bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=1, phase_callable=phase)
        self.assertEqual(len(dispatched), 2)
        self.assertEqual(result['halt'], 'consecutive_guard')

    def test_partial_metadata_barrier_runs_only_authenticated_values_and_reports_missing(self):
        refs = self.initialize()
        seen = []
        def phase(member, start, context):
            seen.append((member['period'], start['phase']))
            if member['period'] == self.batch._ACQUIRE[0]:
                return self.failing_terminal(member, start, context, 'schema')
            return self.terminal(member, start, context)
        result = self.batch._run_scheduler(self.root / refs['bundle_path'], refs['bundle_sha256'],
            bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=2, phase_callable=phase)
        self.assertEqual(result['status'], 'incomplete')
        self.assertEqual(result['missing_periods'], [self.batch._ACQUIRE[0]])
        self.assertEqual([phase for _, phase in seen[:7]], ['metadata'] * 7)
        self.assertEqual(len(seen), 13)
        self.assertEqual(result['halt'], '')


    def test_dispatch_persistence_failure_cancels_inflight_and_persists_halt(self):
        refs = self.initialize()
        original = self.batch._Batch.append
        stopped = __import__('threading').Event()
        def phase(member, start, context):
            self.assertTrue(context.cancel_event.wait(5))
            stopped.set()
            raise RuntimeError('cancelled fixture phase')
        def fail(batch, kind, **details):
            record = original(batch, kind, **details)
            if kind == 'phase_start' and len(batch.inflight) == 1:
                raise OSError('fixture second dispatch persistence failed')
            return record
        with patch.object(self.batch._Batch, 'append', fail):
            with self.assertRaisesRegex(OSError, 'dispatch persistence'):
                self.batch._run_scheduler(self.root / refs['bundle_path'], refs['bundle_sha256'],
                    bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=2, phase_callable=phase)
        self.assertTrue(stopped.is_set())
        self.assertTrue((self.root / 'data/runs/batch-fixture/halt.json').is_file(),
                        'Coordinator persistence failure must persist halt before return')


class HistoricalPreparationTests(unittest.TestCase):
    def setUp(self):
        self.batch = importlib.import_module('bank_quality.financial_acquisition_batch')
        self.acquisition = importlib.import_module('bank_quality.financial_acquisition')
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for module in (self.batch, self.acquisition):
            patcher = patch.object(module, '_ROOT', self.root)
            patcher.start()
            self.addCleanup(patcher.stop)
        refs, frozen = {}, {}
        members = self.batch._HISTORICAL_POLICY_V1['members']
        for name in ('old', 'new'):
            entries = []
            if name == 'old':
                for member in members:
                    entry = catalog_entry(member['period'])
                    entry['files'] = [f for f in entry['files'] if 'trel' not in f and
                        ('dados' not in f['f'] or any(f['f'].endswith('_' + str(a) + '.json')
                            for a in member['announced_numeric_areas']))]
                    prefix = 'ifdata/' + str(member['period']) + '/'
                    entry['files'] += [{'f': prefix + f"trel{member['period']}_{rid}.json",
                        'trel': {'id': rid, 's': [{'id': 1005}],
                                 'c': [{'id': rid, 'ifd': rid, 'ip': None, 'sc': []}]}}
                        for rid in member['reports']]
                    entries.append(entry)
            body = canonical(entries)
            folder = self.root / 'data/raw/catalog'
            folder.mkdir(parents=True, exist_ok=True)
            (folder / (name + '.bin')).write_bytes(body)
            manifest = {'url': CATALOG_URLS[name], 'final_url': CATALOG_URLS[name], 'method': 'GET',
                        'http_status': 200, 'outcome': 'ok', 'truncated': False,
                        'body_path': name + '.bin', 'sha256': sha(body), 'bytes': len(body)}
            raw = canonical(manifest)
            (folder / (name + '.json')).write_bytes(raw)
            refs[name] = {'source_id': 'catalog-' + name, 'role': 'catalog',
                          'manifest_path': 'data/raw/catalog/' + name + '.json',
                          'manifest_sha256': sha(raw), 'body_sha256': sha(body), 'provenance_sha256': sha(raw)}
            frozen[name] = (sha(raw), sha(body), CATALOG_URLS[name])
        patcher = patch.object(self.acquisition, '_FROZEN', frozen)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.index = self.root / 'data/runs/catalog-index.json'
        self.index.parent.mkdir(parents=True)
        self.index.write_bytes(canonical({'contract': self.acquisition.INDEX_CONTRACT,
            'acquisition_scope': 'issue50/financial-202403-1005-native-four',
            'selection': {'perspective': 1005, 'reports': 'native-four'}, 'catalogs': refs}))

    def prepare(self, window='F1-01'):
        return self.batch.prepare_historical_batch(self.index, sha(self.index.read_bytes()), window_id=window)

    def test_prepare_all_windows_binds_exact_policy_without_authority(self):
        periods = []
        for window in self.batch._HISTORICAL_POLICY_V1['windows']:
            draft = self.prepare(window['window_id'])
            self.assertEqual(draft['contract'], 'financial-acquisition-batch-draft-v2')
            self.assertFalse(draft['executable'])
            self.assertEqual(draft['destination'], window['destination'])
            for member in draft['members']:
                job = member['job']
                self.assertEqual(job['contract'], 'financial-acquisition-job-v2')
                self.acquisition._execution_job(job)
                periods.append(member['period'])
        self.assertEqual(periods, [m['period'] for m in self.batch._HISTORICAL_POLICY_V1['members']])
        self.assertFalse((self.root / 'data/runs/financial-acquisition-authority').exists())

    def test_job_mutations_are_rejected_even_after_hash_recomputed(self):
        job = self.prepare()['members'][0]['job']
        for field, value in [('acquisition_scope', 'alternate'), ('version', True), ('member', []),
                             ('member', dict(job['member'], reports=[1, 4, 3, 5])),
                             ('policies', dict(job['policies'], attempts=3)),
                             ('targets', job['targets'] + job['targets'][:1])]:
            changed = copy.deepcopy(job)
            changed[field] = value
            changed['job_sha256'] = self.acquisition._job_hash(changed)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.acquisition._execution_job(changed)

    def initialize(self):
        draft = self.prepare()
        path = self.root / 'data/runs/draft.json'
        path.write_bytes(canonical(draft))
        @contextmanager
        def claim(path):
            path.touch(exist_ok=True)
            yield
        patcher = patch.object(self.acquisition, '_claim', claim)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch.object(self.batch, '_code_identity_v2', return_value=None)
        patcher.start()
        self.addCleanup(patcher.stop)
        return self.batch.initialize_historical_batch(path, sha(path.read_bytes()),
            self.root / draft['destination'], reviewed_code_pins={})

    def test_initialization_is_exact_new_and_verifiable_without_sources(self):
        ref = self.initialize()
        self.assertEqual(ref['scope'], self.batch._historical_window('F1-01')['scope'])
        bundle_path = self.root / ref['bundle_path']
        bundle = json.loads(bundle_path.read_bytes())
        self.assertEqual(bundle['contract'], 'financial-acquisition-batch-v2')
        result = self.batch.verify_historical_batch(bundle_path, ref['bundle_sha256'],
            bootstrap_sha256=ref['bootstrap_sha256'])
        self.assertEqual(result['totals']['attempts'], 0)
        self.assertEqual(result['missing_periods'], [201003, 201006, 201009, 201012])
        with self.assertRaises(ValueError):
            self.initialize()

    def test_initialize_rejects_other_destination_before_any_binding(self):
        draft = self.prepare()
        path = self.root / 'data/runs/draft.json'
        path.write_bytes(canonical(draft))
        with self.assertRaises(ValueError):
            self.batch.initialize_historical_batch(path, sha(path.read_bytes()),
                self.root / 'data/runs/wrong', reviewed_code_pins={})
        self.assertFalse((self.root / 'data/runs/financial-acquisition-authority').exists())

    def test_values_requires_entire_window_metadata_and_member_success(self):
        ref = self.initialize()
        bundle = json.loads((self.root / ref['bundle_path']).read_bytes())
        member = bundle['members'][0]
        record = {'contract': 'financial-acquisition-batch-ledger-v1', 'sequence': 1,
            'previous_record_sha256': '0' * 64, 'bundle_sha256': ref['bundle_sha256'],
            'bootstrap_sha256': ref['bootstrap_sha256'], 'kind': 'phase_start',
            'phase_id': '1' * 32, 'period': member['period'], 'phase': 'values',
            'session': member['session_root'] + '/values-' + '1' * 32,
            'job_sha256': member['job_sha256'], 'member_bootstrap_sha256': member['bootstrap_sha256'],
            'member_sequence': 0, 'member_record_sha256': self.acquisition._EMPTY_HASH}
        state = self.batch._ledger_state()
        with self.assertRaisesRegex(ValueError, 'barrier'):
            self.batch._apply_phase(state, record, bundle)
        state['finished'] = {str(m['period']): {'period': m['period'], 'phase': 'metadata',
            'result': {'status': 'complete'}} for m in bundle['members']}
        self.batch._apply_phase(state, record, bundle)
        self.assertIn('1' * 32, state['pending'])

    def test_historical_run_rejects_profile_concurrency_and_export_incomplete(self):
        ref = self.initialize()
        path = self.root / ref['bundle_path']
        profile = self.root / 'data/runs/resource.json'
        value = {'contract': 'financial-acquisition-resource-profile-v1', 'machine_id': 'fixture',
            'metadata_workers': 2, 'values_workers': 1, 'active_windows': 1,
            'min_free_physical_bytes': 1, 'min_free_commit_bytes': 1,
            'min_free_disk_bytes': 1, 'sampling_interval_ms': 250}
        profile.write_bytes(canonical(value))
        with self.assertRaisesRegex(ValueError, 'serial'):
            self.batch.run_historical_batch(path, ref['bundle_sha256'],
                bootstrap_sha256=ref['bootstrap_sha256'], resource_profile_path=profile,
                resource_profile_sha256=sha(profile.read_bytes()))
        output = self.root / 'data/runs/new-handoff.json'
        with self.assertRaisesRegex(ValueError, 'complete'):
            self.batch.export_historical_sources(path, ref['bundle_sha256'],
                bootstrap_sha256=ref['bootstrap_sha256'], output=output)
        self.assertFalse(output.exists())

    def test_v3_worker_binds_start_reservation_and_rejects_v2_downgrade(self):
        ref = self.initialize()
        with self.batch._open_batch(self.root / ref['bundle_path'], ref['bundle_sha256'], ref['bootstrap_sha256']) as batch:
            member = batch.bundle['members'][0]
            start = self.batch._start_phase(batch, member, 'metadata')
            context = self.batch._MemberContext(batch, member)
            context.start = start
            transport = self.batch._transport_context(context)
            self.assertEqual(transport['contract'], 'financial-acquisition-worker-context-v3')
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=context) as authority:
                target = member['job']['targets'][0]
                reserve = self.acquisition.reserve_attempt(authority, target, session_id=Path(start['session']).name)
                spec = {'contract': 'financial-acquisition-worker-v3', 'batch_context': transport,
                    'job_path': member['job_path'], 'job_sha256': member['job_sha256'],
                    'bootstrap_sha256': member['bootstrap_sha256'], 'attempt_id': reserve['attempt_id'],
                    'target_key': target['target_key'], 'body_budget_bytes': reserve['reserved_bytes'],
                    'parent_identity': {'pid': 456, 'creation_time': 2},
                    'output_path': start['session'] + '/attempt-' + reserve['attempt_id']}
                with self.assertRaisesRegex(ValueError, 'identity'):
                    self.acquisition._worker_authorization(spec)
                authority.commit('identity', attempt_id=reserve['attempt_id'], target_key=target['target_key'],
                    session_id=Path(start['session']).name, identity={'pid': 123, 'creation_time': 1, 'contained': True},
                    spec_path='data/runs/spec.json', spec_sha256=sha(canonical(spec)))
                with patch.object(self.acquisition, 'verify_worker_ancestry'):
                    bad = dict(spec, parent_identity={'pid': 455, 'creation_time': 2})
                    with self.assertRaisesRegex(ValueError, 'spec'):
                        self.acquisition._worker_authorization(bad)
                    job, selected = self.acquisition._worker_authorization(spec)
                    self.assertEqual((job, selected), (member['job'], target))
                    for changed in [dict(spec, contract='financial-acquisition-worker-v2'),
                                    dict(spec, body_budget_bytes=1)]:
                        with self.assertRaises(ValueError):
                            self.acquisition._worker_authorization(changed)

    write = BatchCompositionTests.write
    bounded_source = BatchCompositionTests.bounded_source

    def test_v3_production_roundtrip_uses_own_dictionary_subset_and_exports_receipts(self):
        self._v3_roundtrip()

    def test_unknown_terminal_monitor_error_persists_halt_and_blocks_remaining(self):
        self._v3_roundtrip(terminal_error=True)

    def test_crash_pending_cleanup_does_not_invent_monitor_halt(self):
        self._v3_roundtrip(crash_pending='cancel')

    def test_crash_pending_cleanup_preserves_concurrent_native_error(self):
        self._v3_roundtrip(crash_pending='native')

    def test_crash_pending_cleanup_preserves_expiration(self):
        self._v3_roundtrip(crash_pending='expired')

    def test_representative_crash_recovers_original_measurement_without_launch(self):
        self._v3_roundtrip(crash_checkpoint=True)

    def test_representative_crash_missing_measurement_refuses_without_launch(self):
        self._v3_roundtrip(crash_checkpoint=True, proof_damage='missing')

    def test_representative_crash_unanchored_measurement_refuses_without_launch(self):
        self._v3_roundtrip(crash_checkpoint=True, proof_damage='unanchored')

    def test_representative_crash_tampered_measurement_refuses_without_launch(self):
        self._v3_roundtrip(crash_checkpoint=True, proof_damage='tampered')

    def test_representative_resume_corrupted_metadata_receipt_rejects_before_dispatch(self):
        self._v3_roundtrip(crash_metadata=True, proof_damage='receipt')

    def test_representative_resume_corrupted_metadata_resolution_rejects_before_dispatch(self):
        self._v3_roundtrip(crash_metadata=True, proof_damage='resolution')

    def test_representative_resume_intact_completed_metadata_continues_without_renewal(self):
        self._v3_roundtrip(crash_metadata=True)

    def _v3_roundtrip(self, *, crash_checkpoint=False, crash_metadata=False, proof_damage=None, terminal_error=False, crash_pending=None):
        machine = patch('bank_quality.windows_acquisition._machine_id', return_value='fixture')
        machine.start()
        self.addCleanup(machine.stop)
        import shutil
        import threading
        refs = self.initialize()
        profile = self.root / 'data/runs/resource.json'
        value = {'contract': 'financial-acquisition-resource-profile-v1', 'machine_id': 'fixture',
            'metadata_workers': 1, 'values_workers': 1, 'active_windows': 1,
            'min_free_physical_bytes': 1, 'min_free_commit_bytes': 1,
            'min_free_disk_bytes': 1, 'sampling_interval_ms': 250}
        profile.write_bytes(canonical(value))
        specs = []
        def fetch(url, output, label, context, *, body_budget_bytes, timeout_seconds):
            spec = next(s for s in specs if s['attempt_id'] == label)
            job, target = self.acquisition._worker_authorization(spec)
            reports = job['member']['reports']
            area = job['member']['announced_numeric_areas'][-1]
            payload = ([{'c0': '1', 'c1': str(context['period'])}] if target['role'] == 'cadaster'
                else [{'id': rid, 'td': 3, 'a': area, 'lid': rid} for rid in reports]
                if target['role'] == 'dictionary' else
                {'id': area, 'values': [{'e': 1, 'v': [{'i': rid, 'v': 0} for rid in reports]}]})
            source = self.bounded_source(target, payload)
            original = self.root / source['manifest_path']
            manifest = json.loads(original.read_bytes())
            manifest['body_budget_bytes'] = body_budget_bytes
            manifest['manifest_path'] = original.name
            for name in (manifest['body_path'], manifest['response_metadata_path']):
                shutil.copyfile(original.parent / name, output / name)
            (output / original.name).write_bytes(canonical(manifest))
            return manifest
        def launch(path, pin, *, deadline_seconds, before_resume, cancel_event):
            spec = json.loads(path.read_bytes())
            self.assertEqual(spec['contract'], 'financial-acquisition-worker-v3')
            specs.append(spec)
            before_resume({'pid': 123, 'creation_time': 456, 'contained': True})
            self.acquisition._worker_main(path, pin)
            return {'tree_extinct': True, 'deadline_reached': False, 'deadline_overshoot_seconds': 0,
                    'exit_code': 0, 'elapsed_seconds': 1.0}
        sample = {'free_physical_bytes': 100, 'free_commit_bytes': 100, 'free_disk_bytes': 1024 * 1024 * 1024,
                  'processes': [], 'tree_working_set_bytes': 111, 'tree_private_bytes': 222, 'elapsed_clock': 1.0}
        with patch('bank_quality.windows_acquisition._machine_id', return_value='fixture'), \
                patch('bank_quality.windows_acquisition._current_identity', return_value={'pid': 7, 'creation_time': 9}), \
                patch('bank_quality.windows_acquisition._resource_sample', return_value=sample), \
                patch.object(self.acquisition, 'require_supported'), \
                patch.object(self.acquisition, '_current_identity', return_value={'pid': 7, 'creation_time': 9}), \
                patch.object(self.acquisition, 'run_contained_attempt', side_effect=launch), \
                patch.object(self.acquisition, 'verify_worker_ancestry'), \
                patch('bank_quality.archive.fetch_bounded', side_effect=fetch):
            with self.assertRaisesRegex(ValueError, 'representative'):
                self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                    bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                    resource_profile_sha256=sha(profile.read_bytes()), stage_mode='remaining')
            self.assertEqual(specs, [])
            if crash_pending is not None:
                import time
                from bank_quality import windows_acquisition as windows
                class Crash(BaseException):
                    pass
                enabled, pending = threading.Event(), threading.Event()
                monitors = []
                original_enter = windows._ResourceMonitor.__enter__
                original_append = self.batch._Batch.append
                def enter(monitor):
                    monitors.append(monitor)
                    return original_enter(monitor)
                def observation(*args):
                    if (monitors and enabled.is_set()
                            and threading.current_thread() is monitors[0].thread):
                        raise windows._ProcessObservationPending('synthetic pending during coordinator crash')
                    return sample
                def machine_observation(*args):
                    pending.set()
                    if not monitors[0].cancel_event.wait(2):
                        raise RuntimeError('fixture cleanup never cancelled')
                    if crash_pending == 'native':
                        raise OSError(87, 'synthetic concurrent native failure')
                    if crash_pending == 'expired':
                        time.sleep(.3)
                    return {'elapsed_clock_ns': time.perf_counter_ns(), 'free_physical_bytes': 100,
                            'free_commit_bytes': 100, 'free_disk_bytes': 1024 * 1024 * 1024}
                def append(batch, kind, **details):
                    record = original_append(batch, kind, **details)
                    if kind == 'representative_checkpoint':
                        enabled.set()
                        self.assertTrue(pending.wait(2), 'watcher did not enter pending')
                        raise Crash('synthetic coordinator crash during pending')
                    return record
                with patch.object(windows._ResourceMonitor, '__enter__', enter), \
                        patch.object(windows, '_resource_sample', side_effect=observation), \
                        patch.object(windows, '_machine_resource_sample', side_effect=machine_observation), \
                        patch.object(self.batch._Batch, 'append', append):
                    with self.assertRaisesRegex(Crash, 'synthetic coordinator crash'):
                        self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                            bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                            resource_profile_sha256=sha(profile.read_bytes()))
                self.assertFalse(monitors[0].thread.is_alive())
                marker = (self.root / refs['bundle_path']).parent / 'halt.json'
                if crash_pending == 'cancel':
                    self.assertFalse(marker.exists(), 'Cleanup invented a monitor halt')
                    self.assertEqual(monitors[0].observation_gaps[-1]['status'], 'cancelled')
                else:
                    halt = json.loads(marker.read_bytes())
                    self.assertIn('synthetic concurrent native failure' if crash_pending == 'native'
                                  else 'limit exceeded', halt['reason'])
                return
            if terminal_error:
                from bank_quality.windows_acquisition import _ResourceMonitor
                original_exit = _ResourceMonitor.__exit__
                def fail_terminal(monitor, *args):
                    with patch('bank_quality.windows_acquisition._resource_sample',
                               side_effect=TypeError('synthetic unknown terminal observation')):
                        return original_exit(monitor, *args)
                with patch.object(_ResourceMonitor, '__exit__', fail_terminal):
                    with self.assertRaisesRegex(TypeError, 'synthetic unknown terminal'):
                        self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                            bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                            resource_profile_sha256=sha(profile.read_bytes()))
                marker = self.root / refs['bundle_path']
                halt = json.loads((marker.parent / 'halt.json').read_bytes())
                self.assertIn('TypeError', halt['reason'])
                self.assertIn('synthetic unknown terminal', halt['reason'])
                previous_specs = len(specs)
                with patch.object(self.acquisition, 'run_contained_attempt',
                                  side_effect=AssertionError('Halted representative relaunched')):
                    result = self.batch.run_historical_batch(marker, refs['bundle_sha256'],
                        bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                        resource_profile_sha256=sha(profile.read_bytes()), stage_mode='remaining')
                self.assertEqual(result['status'], 'halted')
                self.assertEqual(len(specs), previous_specs)
                return
            if crash_metadata:
                class Crash(BaseException):
                    pass
                original_append = self.batch._Batch.append
                def append(batch, kind, **details):
                    record = original_append(batch, kind, **details)
                    if kind == 'phase_finish':
                        raise Crash('after first durable metadata phase_finish')
                    return record
                with patch.object(self.batch._Batch, 'append', append), self.assertRaises(Crash):
                    self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                        bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                        resource_profile_sha256=sha(profile.read_bytes()))
                self.assertEqual([s['target_key'] for s in specs], ['201003:cadaster', '201003:dictionary'])
                with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as opened:
                    self.assertFalse(opened.state['pending'])
                    self.assertEqual(len(opened.state['finished']), 1)
                    metadata = next(iter(opened.state['finished'].values()))
                    self.assertEqual((metadata['period'], metadata['phase']), (201003, 'metadata'))
                    before_totals = self.batch._totals(opened)
                    downstream = opened.bundle['members'][1]
                    downstream_journal = self.root / downstream['authority_path'] / 'journal.jsonl'
                    self.assertEqual(downstream_journal.read_bytes(), b'')
                if proof_damage is not None:
                    damaged = (self.root / metadata['result']['receipt']['path'] if proof_damage == 'receipt'
                               else self.root / metadata['session'] / 'resolution.json')
                    damaged.write_bytes(b'{}')
                    preserved = {str(p.relative_to(self.root)): sha(p.read_bytes())
                                 for p in self.root.rglob('*') if p.is_file()}
                    with patch('bank_quality.windows_acquisition._ResourceMonitor',
                               side_effect=AssertionError('Monitor started before completed proof validation')), \
                            patch.object(self.batch, '_start_phase',
                               side_effect=AssertionError('Phase dispatched before completed proof validation')), \
                            patch.object(self.acquisition, 'reserve_attempt',
                               side_effect=AssertionError('Attempt reserved before completed proof validation')), \
                            patch.object(self.acquisition, 'run_contained_attempt',
                               side_effect=AssertionError('Worker launched before completed proof validation')):
                        for stage in ('representative', 'remaining'):
                            with self.subTest(stage=stage), self.assertRaises((ValueError, OSError)):
                                options = {} if stage == 'representative' else {'stage_mode': stage}
                                self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                    bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                                    resource_profile_sha256=sha(profile.read_bytes()), **options)
                    with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as opened:
                        after_totals = self.batch._totals(opened)
                        self.assertEqual(after_totals['totals'], before_totals['totals'])
                        self.assertEqual(after_totals['finished_phases'], before_totals['finished_phases'])
                        self.assertFalse(opened.state['pending'])
                    self.assertEqual(downstream_journal.read_bytes(), b'')
                    self.assertEqual({str(p.relative_to(self.root)): sha(p.read_bytes())
                                      for p in self.root.rglob('*') if p.is_file()}, preserved)
                    return
            if crash_checkpoint:
                class Crash(BaseException):
                    pass
                original_append = self.batch._Batch.append
                def append(batch, kind, **details):
                    if kind == 'representative_measurement' and proof_damage == 'unanchored':
                        return {}  # simulate old completed candidate without the new durable anchor
                    if kind == 'representative_checkpoint':
                        raise Crash('after durable B/phase_finish')
                    record = original_append(batch, kind, **details)
                    if kind == 'phase_finish' and proof_damage == 'unanchored' and details['result']['checkpoint']['path'].endswith('/checkpoint-b.json'):
                        raise Crash('legacy completion without original measurement anchor')
                    return record
                with patch.object(self.batch._Batch, 'append', append), self.assertRaises(Crash):
                    self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                        bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                        resource_profile_sha256=sha(profile.read_bytes()))
                self.assertEqual(len(specs), 9)
                with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as opened:
                    before_totals = self.batch._totals(opened)
                    representative = next(p for p in opened.state['finished'].values()
                        if p['phase'] == 'values' and p['period'] == 201003)
                    self.assertNotIn('representative_checkpoint', opened.state)
                if proof_damage in ('missing', 'tampered'):
                    proof = self.root / representative['session'] / 'resource-measurement.json'
                    if proof_damage == 'missing':
                        proof.unlink()
                    else:
                        proof.write_bytes(b'{}')
                preserved_files = {str(p.relative_to(self.root)): sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
                resumed_sample = dict(sample, tree_working_set_bytes=777, tree_private_bytes=888)
                with patch('bank_quality.windows_acquisition._resource_sample', return_value=resumed_sample), \
                        patch.object(self.acquisition, 'run_contained_attempt', side_effect=AssertionError('Unexpected relaunch')):
                    if proof_damage is not None:
                        with self.assertRaises((ValueError, OSError)):
                            self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                                resource_profile_sha256=sha(profile.read_bytes()))
                        with self.assertRaises((ValueError, OSError)):
                            self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                                resource_profile_sha256=sha(profile.read_bytes()), stage_mode='remaining')
                        if proof_damage != 'unanchored':
                            with self.assertRaises((ValueError, OSError)):
                                self.batch.verify_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                                    bootstrap_sha256=refs['bootstrap_sha256'])
                        with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as opened:
                            self.assertNotIn('representative_checkpoint', opened.state)
                            self.assertEqual(self.batch._totals(opened)['totals'], before_totals['totals'])
                            self.assertEqual(self.batch._totals(opened)['finished_phases'], before_totals['finished_phases'])
                        self.assertEqual({str(p.relative_to(self.root)): sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}, preserved_files)
                        return
                    first = self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                        bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                        resource_profile_sha256=sha(profile.read_bytes()))
                self.assertEqual(first['representative_checkpoint']['measurements']['peaks'],
                    {'tree_working_set_bytes': 111, 'tree_private_bytes': 222})
                self.assertEqual(first['totals'], before_totals['totals'])
            first = self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                resource_profile_sha256=sha(profile.read_bytes()))
            self.assertEqual(first['status'], 'representative_checkpoint', first)
            self.assertEqual(first['totals']['attempts'], 9)
            self.assertEqual(len(specs), 9)
            self.assertEqual(first['complete_periods'], [201003])
            checkpoint = first['representative_checkpoint']
            self.assertEqual(checkpoint['resource_profile']['sha256'], sha(profile.read_bytes()))
            self.assertGreater(checkpoint['measurements']['sample_count'], 0)
            measurement = self.root / checkpoint['resource_measurement']['path']
            self.assertEqual(sha(measurement.read_bytes()), checkpoint['resource_measurement']['sha256'])
            measured = json.loads(measurement.read_bytes())
            self.assertEqual(measured['contract'], 'financial-acquisition-representative-measurement-v2')
            self.assertEqual(checkpoint['measurement_contract'], measured['contract'])
            self.assertEqual(measured['measurements']['pending_limit_ms'], 250)
            self.assertEqual(measured['measurements']['pending_poll_ms'], 50)
            self.assertEqual(measured['measurements']['observation_gaps'], [])
            self.assertEqual(measured['measurements'], checkpoint['measurements'])
            self.assertEqual(measured['phase']['period'], 201003)
            self.assertEqual(measured['resource_profile'], checkpoint['resource_profile'])
            reserved = [r for r in measured['attempt_records'] if r['kind'] == 'reserve']
            self.assertEqual(len(reserved), 1)
            self.assertEqual(reserved[0]['target_key'], '201003:numeric:3')
            with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as opened:
                original = opened.state['representative_measurement']
                finish = next(r for r in opened.records if r['kind'] == 'phase_finish' and r['phase_id'] == original['phase_id'])
                self.assertLess(original['sequence'], finish['sequence'])
                self.assertLess(finish['sequence'], checkpoint['sequence'])
            self.assertEqual(checkpoint['result']['status'], 'complete')
            self.assertTrue(checkpoint['result']['checkpoint']['path'].endswith('/checkpoint-b.json'))
            # A repeat of the default mode exposes the same checkpoint, without GET or renewal.
            repeat = self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                resource_profile_sha256=sha(profile.read_bytes()))
            self.assertEqual(repeat['representative_checkpoint'], checkpoint)
            self.assertEqual(len(specs), 9)
            original_profile = profile.read_bytes()
            profile.write_bytes(canonical(dict(value, min_free_disk_bytes=2)))
            with self.assertRaises(ValueError):
                self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                    bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                    resource_profile_sha256=sha(profile.read_bytes()), stage_mode='remaining')
            self.assertEqual(len(specs), 9)
            profile.write_bytes(original_profile)
            result = self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                resource_profile_sha256=sha(profile.read_bytes()), stage_mode='remaining')
        self.assertEqual(result['status'], 'complete', result)
        self.assertEqual(result['totals']['attempts'], 12)
        self.assertEqual([s['target_key'] for s in specs if ':numeric:' in s['target_key']],
            [f'{period}:numeric:3' for period in (201003, 201006, 201009, 201012)])
        self.assertTrue(all(':numeric:' not in s['target_key'] for s in specs[:8]))
        bundle = json.loads((self.root / refs['bundle_path']).read_bytes())
        with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as batch:
            metadata = next(p for p in batch.state['finished'].values() if p['phase'] == 'metadata')
            resolution = self.root / metadata['session'] / 'resolution.json'
        prior = resolution.read_bytes()
        resolution.write_bytes(b'{}')
        with self.assertRaises(ValueError):
            self.batch.verify_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'])
        resolution.write_bytes(prior)
        output = self.root / 'data/runs/handoff.json'
        export = self.batch.export_historical_sources(self.root / refs['bundle_path'], refs['bundle_sha256'],
            bootstrap_sha256=refs['bootstrap_sha256'], output=output)
        self.assertEqual(export['sha256'], sha(output.read_bytes()))
        for member in json.loads(output.read_bytes())['members']:
            self.assertEqual(len(member['sources']), 3)
        with self.assertRaises(ValueError):
            self.batch.export_historical_sources(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'], output=output)

    def test_legacy_run_entry_cannot_execute_historical_without_resource_gate(self):
        refs = self.initialize()
        with self.assertRaisesRegex(ValueError, 'resource'):
            self.batch._run_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                bootstrap_sha256=refs['bootstrap_sha256'], metadata_workers=2)
        result = self.batch.verify_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
            bootstrap_sha256=refs['bootstrap_sha256'])
        self.assertEqual(result['sequence'], 0)
        self.assertEqual(result['totals']['attempts'], 0)

    def test_historical_target_budget_caps_derive_from_installed_member(self):
        for window in self.batch._HISTORICAL_POLICY_V1['windows']:
            for member in self.prepare(window['window_id'])['members']:
                job = member['job']
                targets = self.acquisition._execution_job(job)
                budget = self.batch._HISTORICAL_POLICY_V1['budgets'][job['member']['budget_id']]
                self.assertEqual(len(targets) * job['policies']['attempts'], budget['attempts_max'])
                self.assertEqual(sum(self.acquisition._body_cap(t, job['policies']) for t in targets.values()),
                                 budget['body_bytes_max'])

    def test_monitor_preflight_failure_halts_before_phase_or_reservation(self):
        refs = self.initialize()
        profile = self.root / 'data/runs/resource.json'
        profile.write_bytes(canonical({'contract': 'financial-acquisition-resource-profile-v1',
            'machine_id': 'fixture', 'metadata_workers': 1, 'values_workers': 1, 'active_windows': 1,
            'min_free_physical_bytes': 1, 'min_free_commit_bytes': 1,
            'min_free_disk_bytes': 1, 'sampling_interval_ms': 250}))
        with patch('bank_quality.windows_acquisition._machine_id', return_value='fixture'), \
                patch('bank_quality.windows_acquisition._current_identity', return_value={'pid': 7, 'creation_time': 9}), \
                patch('bank_quality.windows_acquisition._resource_sample', side_effect=OSError('preflight measurement')), \
                patch.object(self.acquisition, 'run_contained_attempt', side_effect=AssertionError('Unexpected launch')):
            with self.assertRaisesRegex((RuntimeError, OSError), 'preflight measurement'):
                self.batch.run_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
                    bootstrap_sha256=refs['bootstrap_sha256'], resource_profile_path=profile,
                    resource_profile_sha256=sha(profile.read_bytes()))
        state = self.batch.verify_historical_batch(self.root / refs['bundle_path'], refs['bundle_sha256'],
            bootstrap_sha256=refs['bootstrap_sha256'])
        self.assertEqual(state['status'], 'halted')
        self.assertEqual(state['sequence'], 0)
        self.assertEqual(state['totals']['attempts'], 0)

    def test_historical_recovery_error_claims_window_before_halt(self):
        bundle = self.prepare()
        bundle['contract'] = 'financial-acquisition-batch-v2'
        seen = []
        @contextmanager
        def denied_claim(path):
            seen.append(path)
            raise OSError('historical claim unavailable')
            yield
        with patch.object(self.batch, '_immutable_batch', return_value=bundle), \
                patch.object(self.batch, '_open_batch', side_effect=OSError('historical evidence error')), \
                patch.object(self.acquisition, '_claim', denied_claim), \
                patch.object(self.batch._Batch, 'halt', side_effect=AssertionError('Halt without claim')):
            with self.assertRaisesRegex(OSError, 'claim unavailable'):
                self.batch._recover_batch(self.root / 'data/runs/bundle.json', 'a' * 64,
                    bootstrap_sha256='b' * 64, output=self.root / 'data/runs/recovery.json')
        self.assertEqual(seen, [self.batch._batch_paths(bundle['scope'])[1]])
        self.assertFalse((self.root / 'data/runs/recovery.json').exists())

    def test_historical_two_distinct_guards_halt_and_success_resets(self):
        bundle = self.prepare()
        bundle['contract'] = 'financial-acquisition-batch-v2'
        def finish(state, guard, idx):
            phase_id = str(idx) * 32
            state['pending'][phase_id] = {'period': bundle['acquire_periods'][idx], 'phase': 'metadata'}
            result = {'contract': 'financial-acquisition-phase-result-v1', 'status': 'failed' if guard else 'complete',
                      'guard': guard, 'error': 'fixture' if guard else '',
                      'receipt': {'path': 'data/runs/receipt.json', 'sha256': 'a' * 64},
                      'checkpoint': None if guard else {'path': 'data/runs/a.json', 'sha256': 'b' * 64}}
            record = {'contract': 'financial-acquisition-batch-ledger-v1', 'sequence': idx + 1,
                      'previous_record_sha256': '0' * 64, 'bundle_sha256': 'c' * 64,
                      'bootstrap_sha256': 'd' * 64, 'kind': 'phase_finish', 'phase_id': phase_id,
                      'result': result, 'recovered': False}
            self.batch._apply_phase(state, record, bundle)
        state = self.batch._ledger_state()
        finish(state, 'schema', 0)
        finish(state, 'deadline', 1)
        self.assertEqual((state['guard_streak'], state['halt']), (2, 'consecutive_guard'))
        state = self.batch._ledger_state()
        finish(state, 'schema', 0)
        finish(state, '', 1)
        finish(state, 'deadline', 2)
        self.assertEqual((state['guard_streak'], state['halt']), (1, ''))

    def test_historical_member_guard_dispatch_and_receipt_replay_preserve_legacy(self):
        refs = self.initialize()
        with self.batch._open_batch(self.root / refs['bundle_path'], refs['bundle_sha256'], refs['bootstrap_sha256']) as batch:
            member = batch.bundle['members'][0]
            context = self.batch._MemberContext(batch, member)
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=context) as authority:
                for target, guard in zip(member['job']['targets'], ('schema', 'deadline')):
                    authority.commit('guard_failure', target_key=target['target_key'], session_id='fixture',
                        status='source_schema_failed', guard=guard, diagnostic='fixture')
                self.assertEqual(authority.state['guard_streak'], 2)
                receipt = self.acquisition._receipt(authority, 'fixture')
                self.acquisition._verify_receipt(receipt, authority)
                records = copy.deepcopy(authority.records)
                replay = self.acquisition._replay_member_records(records, job_identity=member['job_sha256'],
                    targets=authority.targets, policy=authority.policies)
                self.assertEqual(replay['state']['guard_streak'], 1)
                self.assertEqual(authority.state['guard_streak'], 2)

    def test_installed_budget_adaptation_is_exact(self):
        for key, budget in self.batch._HISTORICAL_POLICY_V1['budgets'].items():
            limits = self.batch._historical_limits(key)
            self.assertEqual(limits['attempts'], budget['attempts_per_target'])
            self.assertEqual(limits['numeric_body_bytes'], budget['numeric_body_bytes_per_target'])
            self.assertEqual(limits['scheduling_seconds'], budget['scheduling_seconds_max'])
        with self.assertRaises(ValueError):
            self.batch._historical_limits('unknown')


class HistoricalContinuationPreparationTests(unittest.TestCase):
    prepare = HistoricalPreparationTests.prepare

    def setUp(self):
        HistoricalPreparationTests.setUp(self)
        self.runtime = self.root / 'data/runs/inert-runtime.bin'
        self.runtime.write_bytes(b'synthetic runtime, never executed')
        self.old_files = {}
        images = []
        for name in self.batch._CODE_FILES_V2:
            path = self.root / '.scratch/inert' / (name + '.evidence')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(('synthetic inert code: ' + name).encode())
            self.old_files[name] = sha(path.read_bytes())
            images.append({'original_path': name, 'sha256': self.old_files[name],
                           'evidence_path': path.relative_to(self.root).as_posix()})
        self.pins = {'contract': 'financial-acquisition-code-pins-v2', 'reviewed_commit': 'a' * 40,
            'files': self.old_files, 'runtime': {'path': self.runtime.relative_to(self.root).as_posix(),
            'sha256': sha(self.runtime.read_bytes())}, 'policy_sha256': self.batch._HISTORICAL_POLICY_SHA256}
        # Only this synthetic test recognizes these inert bytes; production has a
        # fixed reviewed software vector and never executes predecessor images.
        recognition = {'reviewed_commit': self.pins['reviewed_commit'], 'files': self.old_files,
                       'runtime_sha256': self.pins['runtime']['sha256']}
        for name, value in (('_CONTINUATION_PREDECESSOR_V1', recognition),):
            patcher = patch.object(self.batch, name, value, create=True)
            patcher.start()
            self.addCleanup(patcher.stop)
        @contextmanager
        def claim(path):
            path.touch(exist_ok=True)
            yield
        for module, name, value in ((self.acquisition, '_claim', claim),
                                  (self.batch, '_code_identity_v2', lambda pins: None)):
            patcher = patch.object(module, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        draft = self.prepare()
        draft_path = self.root / 'data/runs/draft.json'
        draft_path.write_bytes(canonical(draft))
        self.refs = self.batch.initialize_historical_batch(draft_path, sha(draft_path.read_bytes()),
            self.root / draft['destination'], reviewed_code_pins=self.pins)
        self.bundle = self.root / self.refs['bundle_path']
        with self.batch._open_batch(self.bundle, self.refs['bundle_sha256'], self.refs['bootstrap_sha256']) as opened:
            member = opened.bundle['members'][0]
            self.start = self.batch._start_phase(opened, member, 'metadata')
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                    coordinator=self.batch._MemberContext(opened, member)) as authority:
                receipt = self.acquisition._receipt(authority, Path(self.start['session']).name)
            self.session = self.root / self.start['session']
            self.session.mkdir(parents=True)
            (self.session / 'receipt.json').write_bytes(canonical(receipt))
            opened.halt('phase_outcome_unproven: synthetic interruption')
        embedded = json.loads(self.bundle.read_bytes())
        self.member = embedded['members'][0]
        self.member_folder, self.member_binding, self.member_claim = self.acquisition._authority_paths(self.member['job'])
        excluded = set()
        for member in embedded['members']:
            folder, binding, lock = self.acquisition._authority_paths(member['job'])
            excluded.update((binding, lock))
        core = list(self.bundle.parent.rglob('*'))
        core += list((self.root / 'data/runs/financial-acquisition-authority').rglob('*'))
        files = {p.relative_to(self.root).as_posix(): sha(p.read_bytes())
                 for p in core if p.is_file() and p not in excluded}
        self.assertEqual(len(files), 24)
        self.snapshot = {'contract': 'private-frozen-historical-monitor-stop-v1', 'head': 'a' * 40,
            'files': files, 'verification': {}, 'cause_observed': 'synthetic', 'classification': 'unproven',
            'new_authority_forbidden': True, 'budget_reset_forbidden': True, 'sources_collected': 0}
        self.snapshot_path = self.root / '.scratch/snapshot.json'
        self.snapshot_path.write_bytes(canonical(self.snapshot))
        self.images_path = self.root / '.scratch/images.json'
        self.images_path.write_bytes(canonical({'contract': 'private-inert-original-six-code-images-v1',
            'head': 'a' * 40, 'files': images, 'execution_allowed': False, 'purpose': 'synthetic inert evidence'}))
        self.current_pins = dict(self.pins, reviewed_commit='b' * 40,
                                 files={name: 'b' * 64 for name in self.old_files})
        self.destination = self.root / 'data/runs/continuation-draft'

    def call_prepare(self):
        with patch.object(self.batch, '_open_batch', side_effect=AssertionError('Executable batch opened')), \
                patch.object(self.acquisition, '_open_authority', side_effect=AssertionError('Executable authority opened')), \
                patch.object(self.acquisition, '_claim', side_effect=AssertionError('Preparation acquired claim')), \
                patch.object(self.acquisition, 'run_contained_attempt', side_effect=AssertionError('Worker launched')), \
                patch('bank_quality.archive.fetch_bounded', side_effect=AssertionError('Network invoked')):
            return self.batch.prepare_historical_continuation(self.bundle, self.refs['bundle_sha256'],
                bootstrap_sha256=self.refs['bootstrap_sha256'], snapshot_path=self.snapshot_path,
                snapshot_sha256=sha(self.snapshot_path.read_bytes()), code_images_path=self.images_path,
                code_images_sha256=sha(self.images_path.read_bytes()), current_code_pins=self.current_pins,
                destination=self.destination)

    def repin_frozen(self, path):
        name = path.relative_to(self.root).as_posix()
        if name in self.snapshot['files']:
            self.snapshot['files'][name] = sha(path.read_bytes())
            self.snapshot_path.write_bytes(canonical(self.snapshot))

    def test_closed_offline_draft_preserves_predecessor_and_additional_bindings(self):
        protected = {p: sha((self.root / p).read_bytes()) for p in self.snapshot['files']}
        result = self.call_prepare()
        self.assertEqual(result['status'], 'prepared')
        candidate = json.loads((self.root / result['path']).read_bytes())
        self.assertEqual(sha((self.root / result['path']).read_bytes()), result['sha256'])
        self.assertFalse(candidate['executable'])
        self.assertEqual(candidate['classification']['kind'], 'aborted_before_authorized_attempt')
        self.assertEqual(candidate['classification']['launch_proof']['attempt_records'], 0)
        self.assertEqual(candidate['classification']['launch_proof']['worker_identities'], [])
        self.assertEqual(candidate['current_code_pins'], self.current_pins)
        self.assertEqual(candidate['effective_totals']['totals']['attempts'], 0)
        self.assertEqual(len(candidate['classification']['authority_tails']), 4)
        self.assertNotIn(self.member_binding.relative_to(self.root).as_posix(), self.snapshot['files'])
        self.assertEqual(candidate['classification']['authority_tails'][0]['binding']['path'],
                         self.member_binding.relative_to(self.root).as_posix())
        self.assertEqual({p: sha((self.root / p).read_bytes()) for p in protected}, protected)

    def test_member_binding_drift_rejected_outside_original_snapshot(self):
        self.member_binding.write_bytes(b'{}')
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_reanchored_stale_member_head_is_not_recovered(self):
        head = self.member_folder / 'head.json'
        value = json.loads(head.read_bytes())
        value['sequence'] = 1
        head.write_bytes(canonical(value))
        self.repin_frozen(head)
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_initial_receipt_cannot_claim_a_reserved_attempt(self):
        path = self.session / 'receipt.json'
        receipt = json.loads(path.read_bytes())
        receipt['state']['attempts'] = 1
        path.write_bytes(canonical(receipt))
        self.repin_frozen(path)
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_unfrozen_worker_artifact_blocks_no_launch_classification(self):
        (self.session / 'worker-unproven.json').write_bytes(b'{}')
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_changed_inert_image_is_not_accepted_by_repinned_manifest(self):
        value = json.loads(self.images_path.read_bytes())
        path = self.root / value['files'][0]['evidence_path']
        path.write_bytes(b'unknown code, never executed')
        value['files'][0]['sha256'] = sha(path.read_bytes())
        self.images_path.write_bytes(canonical(value))
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_destination_must_be_new_without_authority_reset(self):
        self.destination.mkdir()
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_valid_durable_reservation_cannot_be_classified_from_snapshot_text(self):
        with self.batch._open_batch(self.bundle, self.refs['bundle_sha256'], self.refs['bootstrap_sha256']) as opened:
            member = opened.bundle['members'][0]
            with self.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                    coordinator=self.batch._MemberContext(opened, member)) as authority:
                self.acquisition.reserve_attempt(authority, member['job']['targets'][0],
                    session_id=Path(self.start['session']).name)
        for name in ('journal.jsonl', 'head.json'):
            self.repin_frozen(self.member_folder / name)
        self.snapshot['classification'] = 'caller claims approved zero-attempt recovery'
        self.snapshot_path.write_bytes(canonical(self.snapshot))
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_reanchored_batch_head_does_not_authorize_recovery(self):
        head = self.bundle.parent / 'head.json'
        value = json.loads(head.read_bytes())
        value['sequence'] = 2
        head.write_bytes(canonical(value))
        self.repin_frozen(head)
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_snapshot_missing_initial_receipt_is_not_a_complete_inventory(self):
        del self.snapshot['files'][(self.session / 'receipt.json').relative_to(self.root).as_posix()]
        self.snapshot_path.write_bytes(canonical(self.snapshot))
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_duplicate_image_cannot_replace_missing_original_code(self):
        value = json.loads(self.images_path.read_bytes())
        value['files'][1] = copy.deepcopy(value['files'][0])
        self.images_path.write_bytes(canonical(value))
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_empty_unproven_worker_output_directory_is_rejected(self):
        (self.session / 'attempt-unproven').mkdir()
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def test_catalog_drift_at_final_current_pin_check_is_detected(self):
        calls = []
        def code_check(pins):
            self.assertEqual(pins, self.current_pins)
            calls.append(True)
            if len(calls) == 2:
                (self.root / 'data/raw/catalog/old.bin').write_bytes(b'[]')
        with patch.object(self.batch, '_code_identity_v2', side_effect=code_check), self.assertRaises(ValueError):
            self.call_prepare()
        self.assertEqual(len(calls), 2)
        self.assertFalse(self.destination.exists())

    def test_output_cannot_be_created_inside_predecessor(self):
        self.destination = self.bundle.parent / 'new-output'
        with self.assertRaises(ValueError):
            self.call_prepare()
        self.assertFalse(self.destination.exists())

    def late_artifact(self, *, directory):
        calls = []
        def code_check(pins):
            calls.append(True)
            if len(calls) == 2:
                path = self.session / ('attempt-late' if directory else 'worker-late.json')
                if directory:
                    path.mkdir()
                else:
                    path.write_bytes(b'{}')
        with patch.object(self.batch, '_code_identity_v2', side_effect=code_check), self.assertRaises(ValueError):
            self.call_prepare()
        self.assertEqual(len(calls), 2)
        self.assertFalse(self.destination.exists())

    def test_new_worker_file_after_initial_inventory_blocks_preparation(self):
        self.late_artifact(directory=False)

    def test_new_worker_directory_after_initial_inventory_blocks_preparation(self):
        self.late_artifact(directory=True)

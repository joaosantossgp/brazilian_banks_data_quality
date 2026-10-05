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

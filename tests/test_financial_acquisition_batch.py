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
        prefix = 'data/raw/source403/' + stem
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
                    'context': {'period': 202403, 'perspective': 1005, 'role': target['role']}}
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



if __name__ == '__main__':
    unittest.main()

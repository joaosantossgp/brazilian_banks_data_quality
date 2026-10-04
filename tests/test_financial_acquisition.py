"""Offline fixtures are synthetic and never represent accepted financial data."""
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


class AcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.api = importlib.import_module('bank_quality.financial_acquisition')
        except ModuleNotFoundError:
            cls.api = None
        cls.repo = Path(__file__).resolve().parents[1]
        cls.pins = json.loads((cls.repo / '.superpowers/sdd/financial-historical-batch-design-20261004/primary-sources.json').read_text())

    def setUp(self):
        self.assertIsNotNone(self.api, 'Offline resolver interface has not been implemented')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = self.root / 'catalog-index.json'
        refs = {}
        for name, pin in self.pins.items():
            manifest = json.loads((self.repo / pin['manifest']).read_bytes(), parse_float=lambda value: {'json_number': value})
            refs[name] = {'source_id': 'catalog-' + name, 'role': 'catalog',
                          'manifest_path': pin['manifest'], 'manifest_sha256': pin['manifest_sha256'],
                          'body_sha256': pin['body_sha256'], 'provenance_sha256': sha(canonical(manifest))}
        self.document = {'contract': 'financial-acquisition-catalog-index-v1',
                         'acquisition_scope': 'issue50/financial-202403-1005-native-four',
                         'selection': {'perspective': 1005, 'reports': 'native-four'}, 'catalogs': refs}

    def prepare(self, periods=(202403,), **kwargs):
        self.index.write_bytes(canonical(self.document))
        return self.api.prepare_job(self.index, sha(self.index.read_bytes()), periods,
                                    limits=kwargs.pop('limits', {'attempts': 2, 'workers': 1}), **kwargs)

    def source(self, target, body, **changes):
        folder = self.root / 'data/raw/fixture'
        folder.mkdir(parents=True, exist_ok=True)
        stem = target['source_id'].replace('/', '-')
        payload = body if isinstance(body, bytes) else canonical(body)
        manifest = {'url': target['url'], 'method': 'GET', 'final_url': target['url'],
                    'http_status': 200, 'outcome': 'ok', 'truncated': False,
                    'retrieved_at_utc': '2026-10-04T00:00:00+00:00', 'response_headers': {},
                    'diagnostics': [], 'context': {'period': target['period'], 'perspective': 1005, 'role': target['role']},
                    'body_path': stem + '.bin', 'sha256': sha(payload), 'bytes': len(payload)}
        manifest.update(changes)
        (folder / manifest['body_path']).write_bytes(payload)
        path = folder / (stem + '.json')
        path.write_bytes(canonical(manifest))
        return {**target, 'manifest_path': path.relative_to(self.root).as_posix(),
                'manifest_sha256': sha(path.read_bytes()), 'body_sha256': sha(payload),
                'provenance_sha256': sha(canonical(manifest)), 'context': manifest['context']}

    def bounded_source(self, target, body):
        payload = canonical(body)
        folder = self.root / 'data/raw/fixture'
        folder.mkdir(parents=True, exist_ok=True)
        name = target['source_id'] + '.response.json'
        headers = [['Content-Length', str(len(payload))]]
        metadata = {'http_status': 200, 'final_url': target['url'], 'response_headers_raw': headers}
        (folder / name).write_bytes(canonical(metadata))
        return self.source(target, payload, contract='bounded-http-archive-v1', source_complete=True,
                           body_available=True, completion_basis='content_length', eof_observed=False,
                           content_length=len(payload), bytes_observed=len(payload), body_budget_bytes=len(payload),
                           response_metadata_path=name, response_metadata_sha256=sha(canonical(metadata)), response_headers_raw=headers)

    def metadata(self, job):
        descriptor = job['descriptors'][0]
        definitions = {}
        def walk(nodes):
            for node in nodes:
                definitions[node['ifd']] = {'id': node['ifd'], 'td': 2 if node['sc'] else 3,
                                           'a': 1, 'lid': -1 if node['sc'] else node['ifd']}
                walk(node['sc'])
        for report in descriptor['reports']:
            walk(report['report']['c'])
        # One attribute demonstrates a variable C schema without a 38-field rule.
        definitions[79670] = {'id': 79670, 'td': 1, 'a': 1, 'lid': 2}
        rows = [{'c0': '1', 'c1': str(descriptor['selection']['period']), 'c2': 'Fixture institution'},
                {'c0': '2', 'c1': str(descriptor['selection']['period']), 'c2': 'Missing numerical entity'}]
        refs = {}
        for target in job['targets']:
            refs[target['target_key']] = self.source(target, rows if target['role'] == 'cadaster' else list(definitions.values()))
        return refs

    def resolve(self, job, refs):
        for pin in self.pins.values():
            for key in ('manifest', 'body'):
                destination = self.root / pin[key]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((self.repo / pin[key]).read_bytes())
        with patch.object(self.api, '_ROOT', self.root):
            return self.api.resolve_sources(job, refs)

    def test_catalog_hash_changed(self):
        self.index.write_bytes(canonical(self.document))
        with self.assertRaisesRegex(ValueError, 'index hash'):
            self.api.prepare_job(self.index, '0' * 64, (202403,), limits={})

    def test_period_202609_rejected(self):
        with self.assertRaisesRegex(ValueError, '66'):
            self.prepare((202609,))

    def test_wrong_selection(self):
        self.document['selection']['perspective'] = 1006
        with self.assertRaisesRegex(ValueError, 'selection'):
            self.prepare()

    def test_multi_perspective_membership_preserved(self):
        job = self.prepare((201503,))
        active = next(r for r in job['descriptors'][0]['reports'] if r['report']['n'] == 'Ativo')
        self.assertEqual(active['report']['s'], [{'id': 1004}, {'id': 1005}])

    def test_double_slash_literal(self):
        job = self.prepare((202503,))
        self.assertTrue(all(t['native_file'].startswith('ifdata_2025_2030//202503/') for t in job['targets']))
        self.assertTrue(all('%2F%2F' in t['url'] for t in job['targets']))

    def test_sparse_shards_not_range(self):
        descriptor = self.prepare((201003,))['descriptors'][0]
        self.assertEqual([s['area'] for s in descriptor['source_offers'] if s['role'] == 'numeric'], [1, 3])

    def test_frozen_catalog_pin_cannot_be_replaced(self):
        self.document['catalogs']['old']['body_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'frozen'):
            self.prepare()

    def test_escape_or_symlink_rejected(self):
        for value in ('../escape.json', 'data/raw/../outside.json', 'C:/absolute.json', 'https://remote/x', 'data/raw\\x'):
            with self.subTest(value=value):
                self.document['catalogs']['old']['manifest_path'] = value
                with self.assertRaises(ValueError):
                    self.prepare()

    def test_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.api.validate_numeric_source(b'{"id":1,"id":1,"values":[]}', area=1, required_origins=[])

    def test_job_hash_stable_across_sessions(self):
        one = self.prepare(limits={'attempts': 2, 'workers': 1, 'session_id': 'a', 'timestamp': 'today'})
        two = self.prepare(limits={'attempts': 2, 'workers': 4, 'session_id': 'b', 'timestamp': 'tomorrow'})
        self.assertEqual(one['job_sha256'], two['job_sha256'])

    def test_reordered_periods_same_job_hash(self):
        self.assertEqual(self.prepare((202403, 201003))['job_sha256'], self.prepare((201003, 202403))['job_sha256'])

    def test_changed_limits_do_not_create_executable_authority(self):
        one, two = self.prepare(), self.prepare(limits={'attempts': 3})
        self.assertNotEqual(one['job_sha256'], two['job_sha256'])
        self.assertFalse(two['executable'])
        self.assertNotIn('bootstrap', two)

    def test_dictionary_from_other_period_rejected(self):
        job = self.prepare(); refs = self.metadata(job)
        key = next(k for k, r in refs.items() if r['role'] == 'dictionary')
        refs[key]['context']['period'] = 202412
        with self.assertRaises(ValueError):
            self.resolve(job, refs)

    def test_missing_definition_blocks(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'dictionary')
        refs[target['target_key']] = self.source(target, [])
        with self.assertRaisesRegex(ValueError, 'definition'):
            self.resolve(job, refs)

    def test_attribute_outside_cadaster_blocks(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'dictionary')
        path = self.root / refs[target['target_key']]['manifest_path']
        definitions = json.loads((path.parent / json.loads(path.read_bytes())['body_path']).read_bytes())
        next(d for d in definitions if d['id'] == 79670)['lid'] = 99
        refs[target['target_key']] = self.source(target, definitions)
        with self.assertRaisesRegex(ValueError, 'cadaster field'):
            self.resolve(job, refs)

    def test_group_has_no_numeric_origin(self):
        job = self.prepare(); result = self.resolve(job, self.metadata(job))
        groups = [n for n in result['resolutions'][0]['nodes'] if n['kind'] == 'group']
        self.assertTrue(groups)
        self.assertTrue(all(n['origin'] is None for n in groups))

    def test_unannounced_area_blocks(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'dictionary')
        path = self.root / refs[target['target_key']]['manifest_path']
        definitions = json.loads((path.parent / json.loads(path.read_bytes())['body_path']).read_bytes())
        next(d for d in definitions if d['td'] == 3)['a'] = 999
        refs[target['target_key']] = self.source(target, definitions)
        with self.assertRaisesRegex(ValueError, 'announced'):
            self.resolve(job, refs)

    def test_two_bindings_share_one_source_without_merging_occurrences(self):
        job = self.prepare(); result = self.resolve(job, self.metadata(job))
        numeric = [n for n in result['resolutions'][0]['nodes'] if n['kind'] == 'numeric']
        self.assertGreater(len(numeric), 1)
        self.assertEqual(len(result['numeric_targets']), 1)
        self.assertEqual(len({n['catalog_pointer'] for n in numeric}), len(numeric))

    def test_checkpoint_is_exact_common_source_index(self):
        job = self.prepare(); result = self.resolve(job, self.metadata(job))
        self.assertEqual(set(result['checkpoints'][0]), {'contract', 'phase', 'selection', 'descriptor_sha256', 'catalog', 'sources'})
        self.assertEqual(result['checkpoints'][0]['contract'], 'ifdata-financial-historical-sources-v1')
        self.assertIn('metadata_digest', result['resolutions'][0])

    def test_missing_or_duplicate_report(self):
        job = self.prepare((201003,)); descriptor = job['descriptors'][0]
        files = [{'f': o['native_file']} for o in descriptor['source_offers']]
        files.append({'f': 'ifdata/201003/sel201003.json', 'sel': [{'id': 1005}]})
        for item in descriptor['reports']:
            files.append({'f': f"ifdata/201003/trel201003_{item['report']['id']}.json", 'trel': item['report']})
        catalog = [{'dt': 201003, 'files': files}]
        for changed in (files[:-1], files + [files[-1]]):
            with self.subTest(length=len(changed)), self.assertRaisesRegex(ValueError, 'report'):
                self.api._descriptor([{'dt': 201003, 'files': changed}], job['catalogs']['old'], 201003)

    def test_source_manifest_and_provenance_are_independent_pins(self):
        job = self.prepare(); refs = self.metadata(job)
        key = next(iter(refs))
        refs[key]['provenance_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.resolve(job, refs)

    def test_reparse_point_is_rejected_before_read(self):
        from types import SimpleNamespace
        import stat
        with patch.object(self.api, '_ROOT', self.root), patch.object(Path, 'lstat', return_value=SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)):
            with self.assertRaisesRegex(ValueError, 'reparse'):
                self.api._local('data/raw/file.json')

    def test_incomplete_bounded_transport_cannot_validate(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'cadaster')
        rows = [{'c0': '1', 'c1': '202403', 'c2': 'Fixture'}]
        refs[target['target_key']] = self.source(target, rows, contract='bounded-http-archive-v1', source_complete=False)
        with self.assertRaisesRegex(ValueError, 'complete'):
            self.resolve(job, refs)

    def test_complete_bounded_transport_requires_authenticated_sidecar(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'cadaster')
        refs[target['target_key']] = self.bounded_source(target, [{'c0': '1', 'c1': '202403', 'c2': 'Fixture'}])
        (self.root / 'data/raw/fixture/cadaster.response.json').write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError, 'metadata hash'):
            self.resolve(job, refs)

    def test_complete_bounded_source_validates_without_transport_call(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'cadaster')
        refs[target['target_key']] = self.bounded_source(target, [{'c0': 'opaque', 'c1': '202403', 'c2': 'Fixture'}])
        self.assertTrue(self.resolve(job, refs)['source_complete'])

    def test_bounded_raw_headers_cannot_contradict_completion(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'cadaster')
        ref = self.bounded_source(target, [{'c0': 'opaque', 'c1': '202403', 'c2': 'Fixture'}])
        path = self.root / ref['manifest_path']
        manifest = json.loads(path.read_bytes())
        manifest['response_headers_raw'] = [['Content-Length', '1'], ['Content-Length', '1']]
        metadata_path = path.parent / manifest['response_metadata_path']
        metadata = json.loads(metadata_path.read_bytes())
        metadata['response_headers_raw'] = manifest['response_headers_raw']
        metadata_path.write_bytes(canonical(metadata))
        manifest['response_metadata_sha256'] = sha(metadata_path.read_bytes())
        path.write_bytes(canonical(manifest))
        refs[target['target_key']] = {**ref, 'manifest_sha256': sha(path.read_bytes()), 'provenance_sha256': sha(canonical(manifest))}
        with self.assertRaisesRegex(ValueError, 'header'):
            self.resolve(job, refs)

    def test_body_escape_rejected_even_with_matching_external_pins(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'cadaster')
        ref = refs[target['target_key']]
        path = self.root / ref['manifest_path']
        manifest = json.loads(path.read_bytes())
        manifest['body_path'] = '../escape.bin'
        path.write_bytes(canonical(manifest))
        refs[target['target_key']] = {**ref, 'manifest_sha256': sha(path.read_bytes()), 'provenance_sha256': sha(canonical(manifest))}
        with self.assertRaisesRegex(ValueError, 'escape'):
            self.resolve(job, refs)

    def test_nonuniform_cadaster_blocks(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'cadaster')
        refs[target['target_key']] = self.source(target, [{'c0': 'a', 'c1': '202403', 'c2': 'Fixture'}, {'c0': 'b', 'c1': '202403'}])
        with self.assertRaisesRegex(ValueError, 'Nonuniform'):
            self.resolve(job, refs)

    def test_all_66_frozen_descriptors_and_unannounced_excluded(self):
        members = tuple(self.api._MEMBERS)
        job = self.prepare(tuple(reversed(members)))
        self.assertEqual(len(job['descriptors']), 66)
        self.assertEqual(len(job['targets']), 132)
        self.assertEqual([d['selection']['period'] for d in job['descriptors']], sorted(members))
        self.assertNotIn(202609, members)
        self.assertNotIn(202612, members)

    def test_descriptor_matches_independent_compiler(self):
        self.assertEqual(self.prepare()['descriptors'][0]['descriptor_sha256'],
                         '346ad8010e4d97bc4e1c46280abe74cf8a6bedf458eeaabf1c0e42f866a544b2')

    def numeric(self, body, origins=None):
        return self.api.validate_numeric_source(body, area=1, required_origins=origins or [])

    def test_numeric_wrong_area(self):
        with self.assertRaisesRegex(ValueError, 'area'):
            self.numeric(b'{"id":3,"values":[]}')

    def test_duplicate_entity(self):
        with self.assertRaisesRegex(ValueError, 'entity'):
            self.numeric(b'{"id":1,"values":[{"e":1,"v":[]},{"e":1,"v":[]}]}')

    def test_duplicate_information(self):
        with self.assertRaisesRegex(ValueError, 'information'):
            self.numeric(b'{"id":1,"values":[{"e":1,"v":[{"i":2,"v":0},{"i":2,"v":1}]}]}')

    def test_noncanonical_identifier(self):
        for value in ('1.0', '1e0', '"1"', 'true', '-0'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.numeric(('{"id":1,"values":[{"e":' + value + ',"v":[]}]}').encode())

    def test_numeric_lexeme_and_string_distinct(self):
        result = self.numeric(b'{"id":1,"values":[{"e":1,"v":[{"i":2,"v":1.2300e+2},{"i":3,"v":"1.2300e+2"},{"i":4,"v":null}]}]}')
        cells = result['entities'][0]['values']
        self.assertEqual([(c['value_type'], c['value']) for c in cells], [('number', '1.2300e+2'), ('string', '1.2300e+2'), ('null', None)])

    def test_unsupported_value_shape(self):
        for value in ('true', '[]', '{}', 'NaN', 'Infinity'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.numeric(('{"id":1,"values":[{"e":1,"v":[{"i":2,"v":' + value + '}]}]}').encode())

    def test_missing_cadaster_entity_is_coverage_not_bad_schema(self):
        origins = [{'area': 1, 'lid': 2, 'cadaster_entities': ['1', '2'], 'catalog_pointer': '/report/c/0'}]
        result = self.numeric(b'{"id":1,"values":[{"e":1,"v":[]}]}', origins)
        self.assertTrue(result['source_validated'])
        self.assertEqual({m['state'] for m in result['missing']}, {'entity_not_stored', 'information_not_stored'})
        self.assertNotIn('admitted', result)

    def test_shared_foreign_entities_not_filtered(self):
        result = self.numeric(b'{"id":1,"values":[{"e":99,"v":[{"i":7,"v":0}]}]}')
        self.assertEqual(result['entities'][0]['entity'], '99')
        self.assertEqual(result['entities'][0]['values'][0]['lid'], '7')

    def test_all_origin_pointers_present(self):
        origins = [{'area': 1, 'lid': 2, 'cadaster_entities': ['1'], 'catalog_pointer': '/r1/c/0'},
                   {'area': 1, 'lid': 2, 'cadaster_entities': ['1'], 'catalog_pointer': '/r2/c/4'}]
        result = self.numeric(b'{"id":1,"values":[{"e":1,"v":[{"i":2,"v":0}]}]}', origins)
        self.assertEqual([p['catalog_pointer'] for p in result['origins']], ['/r1/c/0', '/r2/c/4'])
        self.assertTrue(all(p['cells'][0]['source_pointer'] == '/values/0/v/0/v' for p in result['origins']))


if __name__ == '__main__':
    unittest.main()

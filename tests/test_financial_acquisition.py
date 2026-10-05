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


# Fixture inventory is independent of the resolver's _MEMBERS: the boundary and
# historical report transitions below are expectations, not copied at runtime.
PERIODS = tuple(year * 100 + quarter for year in range(2010, 2026)
                for quarter in (3, 6, 9, 12)) + (202603, 202606)
CATALOG_URLS = {
    'old': 'https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024',
    'new': 'https://www3.bcb.gov.br/ifdata/rest/relatorios2025a2030',
}


def report_ids(period):
    for end, ids in ((201412, (1, 3, 4, 5)), (201812, (75, 3, 4, 5)),
                     (201909, (92, 3, 4, 91)), (202003, (92, 96, 97, 98)),
                     (202412, (92, 96, 101, 98)), (202606, (119, 107, 110, 118))):
        if period <= end:
            return ids
    raise AssertionError('Fixture period outside explicit inventory')


def catalog_entry(period):
    prefix = ('ifdata_2025_2030//' if period >= 202503 else 'ifdata/') + str(period) + '/'
    files = [{'f': prefix + f'cadastro{period}_1005.json'},
             {'f': prefix + f'info{period}.json'},
             {'f': prefix + f'dados{period}_1.json'},
             {'f': prefix + f'dados{period}_3.json'},
             {'f': prefix + f'sel{period}.json', 'sel': [{'id': 1005}]}]
    for rid, name in zip(report_ids(period), ('Resumo', 'Ativo', 'Passivo', 'DRE')):
        parent = rid * 100 + 2
        report = {'id': rid, 'n': name, 's': [{'id': 1004}, {'id': 1005}],
                  'annotation': {'unit': 'unknown', 'window': 'unknown', 'literal': 'não harmonizar'},
                  'c': [{'id': rid * 100 + 1, 'ifd': 79670, 'ip': None, 'sc': []},
                        {'id': parent, 'ifd': 80000, 'ip': None, 'sc': [
                            {'id': rid * 100 + 3, 'ifd': 80001, 'ip': parent, 'sc': []},
                            {'id': rid * 100 + 4, 'ifd': 80002, 'ip': parent, 'sc': []}]}]}
        files.append({'f': prefix + f'trel{period}_{rid}.json', 'trel': report})
    return {'dt': period, 'files': files}


class AcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = importlib.import_module('bank_quality.financial_acquisition')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = self.root / 'catalog-index.json'
        self.catalogs = {name: [catalog_entry(period) for period in PERIODS
                               if (period >= 202503) == (name == 'new')] for name in CATALOG_URLS}
        frozen = {}
        refs = {name: self.catalog_source(name, entries) for name, entries in self.catalogs.items()}
        for name, ref in refs.items():
            frozen[name] = (ref['manifest_sha256'], ref['body_sha256'], CATALOG_URLS[name])
        # Only internal trust anchors/root are injected. All authentication,
        # parsing, membership, origin and transport guards run unchanged.
        for name, value in (('_ROOT', self.root), ('_FROZEN', frozen)):
            injection = patch.object(self.api, name, value)
            injection.start()
            self.addCleanup(injection.stop)
        self.document = {'contract': 'financial-acquisition-catalog-index-v1',
                         'acquisition_scope': 'issue50/financial-202403-1005-native-four',
                         'selection': {'perspective': 1005, 'reports': 'native-four'}, 'catalogs': refs}

    def catalog_source(self, name, entries):
        folder = self.root / 'data/raw/catalog-fixture'
        folder.mkdir(parents=True, exist_ok=True)
        payload = canonical(entries)
        manifest = {'url': CATALOG_URLS[name], 'method': 'GET', 'final_url': CATALOG_URLS[name],
                    'http_status': 200, 'outcome': 'ok', 'truncated': False,
                    'retrieved_at_utc': '2026-10-04T00:00:00+00:00',
                    'response_headers': {'content-type': 'application/json'}, 'diagnostics': [],
                    'body_path': name + '.bin', 'sha256': sha(payload), 'bytes': len(payload)}
        (folder / manifest['body_path']).write_bytes(payload)
        path = folder / (name + '.json')
        path.write_bytes(canonical(manifest))
        return {'source_id': 'catalog-' + name, 'role': 'catalog',
                'manifest_path': path.relative_to(self.root).as_posix(),
                'manifest_sha256': sha(path.read_bytes()), 'body_sha256': sha(payload),
                'provenance_sha256': sha(canonical(manifest))}

    def trusted_catalog_mutation(self, name, entries):
        """A malformed authenticated catalog must still fail structural guards."""
        ref = self.catalog_source(name, entries)
        self.document['catalogs'][name] = ref
        self.api._FROZEN[name] = (ref['manifest_sha256'], ref['body_sha256'], CATALOG_URLS[name])

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

    def test_coherent_replacement_catalog_still_requires_frozen_pins(self):
        changed = copy.deepcopy(self.catalogs['old'])
        changed[-1]['files'][-1]['trel']['annotation']['literal'] = 'replacement'
        self.document['catalogs']['old'] = self.catalog_source('old', changed)
        with self.assertRaisesRegex(ValueError, 'frozen'):
            self.prepare()

    def test_missing_or_duplicate_catalog_period(self):
        for entries in (self.catalogs['old'][1:], self.catalogs['old'] + [self.catalogs['old'][0]]):
            with self.subTest(count=len(entries)):
                self.trusted_catalog_mutation('old', entries)
                with self.assertRaisesRegex(ValueError, 'catalog period'):
                    self.prepare((201003,))

    def test_report_financial_membership_is_required(self):
        changed = copy.deepcopy(self.catalogs['old'])
        changed[0]['files'][6]['trel']['s'] = [{'id': 1004}]
        self.trusted_catalog_mutation('old', changed)
        with self.assertRaisesRegex(ValueError, 'report selection'):
            self.prepare((201003,))

    def test_wrong_report_filename_blocks_even_with_trusted_catalog(self):
        changed = copy.deepcopy(self.catalogs['old'])
        changed[0]['files'][5]['f'] = 'ifdata/201003/trel201003_999.json'
        self.trusted_catalog_mutation('old', changed)
        with self.assertRaisesRegex(ValueError, 'report filename'):
            self.prepare((201003,))

    def test_source_and_selection_announcements_are_unique(self):
        for position, message in ((0, 'source announcement'), (2, 'numeric announcement'), (4, 'financial selection')):
            with self.subTest(position=position):
                changed = copy.deepcopy(self.catalogs['old'])
                changed[0]['files'].append(copy.deepcopy(changed[0]['files'][position]))
                self.trusted_catalog_mutation('old', changed)
                with self.assertRaisesRegex(ValueError, message):
                    self.prepare((201003,))

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

    def test_index_formatting_does_not_change_canonical_job_identity(self):
        job = self.prepare()
        self.index.write_text(json.dumps(self.document, indent=2), encoding='utf-8')
        reformatted = self.api.prepare_job(self.index, sha(self.index.read_bytes()), (202403,),
                                          limits={'attempts': 2, 'workers': 1})
        self.assertEqual(job, reformatted)

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
        for group in groups:
            self.assertEqual(len(group['children_pointers']), 2)
            children = [n for n in result['resolutions'][0]['nodes'] if n['parent_pointer'] == group['catalog_pointer']]
            self.assertEqual([n['catalog_pointer'] for n in children], group['children_pointers'])
            self.assertEqual([n['origin']['lid'] for n in children], [80001, 80002])

    def test_group_definition_must_match_structure(self):
        job = self.prepare(); refs = self.metadata(job)
        target = next(t for t in job['targets'] if t['role'] == 'dictionary')
        path = self.root / refs[target['target_key']]['manifest_path']
        definitions = json.loads((path.parent / json.loads(path.read_bytes())['body_path']).read_bytes())
        next(d for d in definitions if d['id'] == 80000).update(td=3, lid=80000)
        refs[target['target_key']] = self.source(target, definitions)
        with self.assertRaisesRegex(ValueError, 'structure mismatch'):
            self.resolve(job, refs)

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
        for changed in (files[:-1], files + [files[-1]]):
            with self.subTest(length=len(changed)), self.assertRaisesRegex(ValueError, 'report'):
                self.api._descriptor([{'dt': 201003, 'files': changed}], job['catalogs']['old'], 201003)

    def test_source_manifest_and_provenance_are_independent_pins(self):
        job = self.prepare(); refs = self.metadata(job)
        key = next(iter(refs))
        refs[key]['provenance_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.resolve(job, refs)

    def test_changed_manifest_context_requires_new_provenance_pin(self):
        job = self.prepare(); refs = self.metadata(job)
        key = next(iter(refs))
        path = self.root / refs[key]['manifest_path']
        manifest = json.loads(path.read_bytes())
        manifest['retrieved_at_utc'] = '2026-10-04T00:00:01+00:00'
        path.write_bytes(canonical(manifest))
        refs[key]['manifest_sha256'] = sha(path.read_bytes())
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.resolve(job, refs)

    def test_catalog_manifest_and_body_bytes_are_authenticated(self):
        ref = self.document['catalogs']['old']
        path = self.root / ref['manifest_path']
        manifest_bytes = path.read_bytes()
        path.write_bytes(manifest_bytes + b' ')
        with self.assertRaisesRegex(ValueError, 'manifest hash'):
            self.prepare()
        path.write_bytes(manifest_bytes)
        body_path = path.parent / json.loads(manifest_bytes)['body_path']
        body_path.write_bytes(body_path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'hash'):
            self.prepare()

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
        job = self.prepare(tuple(reversed(PERIODS)))
        self.assertEqual(len(job['descriptors']), 66)
        self.assertEqual(len(job['targets']), 132)
        self.assertEqual([d['selection']['period'] for d in job['descriptors']], list(PERIODS))
        for descriptor in job['descriptors']:
            period = descriptor['selection']['period']
            self.assertEqual(descriptor['selection']['reports'], list(report_ids(period)))
            self.assertEqual([r['report']['n'] for r in descriptor['reports']], ['Resumo', 'Ativo', 'Passivo', 'DRE'])
        for outsider in (202609, 202612):
            with self.subTest(period=outsider), self.assertRaisesRegex(ValueError, '66'):
                self.prepare((outsider,))

    def test_descriptor_matches_independent_compiler(self):
        # Independently assemble the expected synthetic payload without calling
        # _descriptor/_canonical or importing the private real-catalog compiler.
        entry = catalog_entry(202403)
        position = PERIODS.index(202403)
        ref = self.document['catalogs']['old']
        expected = {'selection': {'period': 202403, 'perspective': 1005, 'reports': [92, 96, 101, 98]},
                    'catalog': {key: ref[key] for key in ('manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256')},
                    'reports': [{'report': entry['files'][p]['trel'], 'catalog_pointer': f'/{position}/files/{p}/trel'}
                                for p in (5, 6, 7, 8)],
                    'source_offers': [
                        {'source_id': source_id, 'role': role, 'area': area,
                         'native_file': entry['files'][p]['f'], 'catalog_pointer': f'/{position}/files/{p}/f'}
                        for p, source_id, role, area in ((0, 'cadaster', 'cadaster', None),
                                                        (1, 'dictionary', 'dictionary', None),
                                                        (2, 'numeric:1', 'numeric', 1), (3, 'numeric:3', 'numeric', 3))]}
        expected['catalog']['reference_pointer'] = '/' + str(position)
        actual = self.prepare()['descriptors'][0]
        self.assertEqual(actual, {**expected, 'descriptor_sha256': sha(canonical(expected))})

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

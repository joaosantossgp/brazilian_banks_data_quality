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
        stem = target['source_id'].replace('/', '-').replace(':', '-')
        payload = body if isinstance(body, bytes) else canonical(body)
        manifest = {'url': target['url'], 'method': 'GET', 'final_url': target['url'],
                    'http_status': 200, 'outcome': 'ok', 'truncated': False,
                    'retrieved_at_utc': '2026-10-04T00:00:00+00:00', 'response_headers': {},
                    'diagnostics': [], 'context': {'period': target['period'], 'perspective': 1005, 'role': target['role']},
                    'body_path': stem + '.bin', 'sha256': sha(payload), 'bytes': len(payload)}
        manifest.update(contract='bounded-http-archive-v1', source_complete=True, body_available=True,
                        completion_basis='content_length', eof_observed=False, content_length=len(payload),
                        bytes_observed=len(payload), body_budget_bytes=max(1, len(payload)),
                        response_headers_raw=[['Content-Length', str(len(payload))]],
                        response_metadata_path=stem + '.response.json')
        manifest.update(changes)
        metadata = {key: manifest[key] for key in ('http_status', 'final_url', 'response_headers_raw')}
        sidecar = folder / manifest['response_metadata_path']
        sidecar.write_bytes(canonical(metadata))
        manifest['response_metadata_sha256'] = sha(sidecar.read_bytes())
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


    def test_unframed_new_and_reused_sources_rejected(self):
        job = self.prepare()
        refs = self.metadata(job)
        target = job['targets'][0]
        ref = refs[target['target_key']]
        path = self.root / ref['manifest_path']
        manifest = json.loads(path.read_bytes())
        manifest.pop('contract', None)
        manifest.update(source_complete=False, eof_observed=False, diagnostics=['framing_unverified'],
                        content_length=manifest['bytes'] + 1)
        path.write_bytes(canonical(manifest))
        ref['manifest_sha256'], ref['provenance_sha256'] = sha(path.read_bytes()), sha(canonical(manifest))
        with self.assertRaisesRegex(ValueError, 'bounded|framing|contract'):
            self.api.resolve_sources(job, refs)
        reuse = self.root / 'reuse.json'
        reuse.write_bytes(canonical({'contract': 'financial-acquisition-reuse-index-v1', 'job_sha256': job['job_sha256'],
                                     'sources': {target['target_key']: ref}}))
        with self.assertRaisesRegex(ValueError, 'bounded|framing|contract'):
            self.prepare(reuse_index=reuse, reuse_index_sha256=sha(reuse.read_bytes()))

    def test_unknown_source_contract_rejected(self):
        job = self.prepare()
        refs = self.metadata(job)
        target = job['targets'][0]
        ref = refs[target['target_key']]
        path = self.root / ref['manifest_path']
        manifest = json.loads(path.read_bytes())
        manifest['contract'] = 'unknown-completeness-v1'
        path.write_bytes(canonical(manifest))
        ref['manifest_sha256'], ref['provenance_sha256'] = sha(path.read_bytes()), sha(canonical(manifest))
        with self.assertRaisesRegex(ValueError, 'bounded|contract'):
            self.api.resolve_sources(job, refs)

    def test_new_metadata_positive_framing_cannot_be_removed_with_coherent_pins(self):
        for changes in ({'source_complete': False}, {'diagnostics': ['framing_unverified']},
                        {'content_length': 999999}, {'completion_basis': None}, {'body_available': False}):
            with self.subTest(changes=changes):
                job = self.prepare()
                refs = self.metadata(job)
                target = job['targets'][0]
                ref = refs[target['target_key']]
                path = self.root / ref['manifest_path']
                manifest = json.loads(path.read_bytes())
                manifest.update(changes)
                path.write_bytes(canonical(manifest))
                ref['manifest_sha256'], ref['provenance_sha256'] = sha(path.read_bytes()), sha(canonical(manifest))
                with self.assertRaises(ValueError):
                    self.api.resolve_sources(job, refs)

    def test_unframed_numeric_reuse_rejected(self):
        job = self.prepare()
        checkpoint = self.resolve(job, self.metadata(job))
        target = checkpoint['numeric_targets'][0]
        ref = self.source(target, {'id': target['area'], 'values': []})
        path = self.root / ref['manifest_path']
        manifest = json.loads(path.read_bytes())
        manifest.pop('contract')
        path.write_bytes(canonical(manifest))
        ref['manifest_sha256'], ref['provenance_sha256'] = sha(path.read_bytes()), sha(canonical(manifest))
        reuse = self.root / 'numeric-reuse.json'
        reuse.write_bytes(canonical({'contract': 'financial-acquisition-reuse-index-v1', 'job_sha256': job['job_sha256'],
                                     'sources': {target['target_key']: ref}}))
        with self.assertRaisesRegex(ValueError, 'bounded'):
            self.prepare(reuse_index=reuse, reuse_index_sha256=sha(reuse.read_bytes()))


    def test_new_batch_scope_prepare_is_exact_singleton_without_execution_permission(self):
        self.document['acquisition_scope'] = 'financial-recent-202312-202606-v1/202406'
        job = self.prepare((202406,))
        self.assertFalse(job['executable'])
        with self.assertRaisesRegex(ValueError, 'singleton'):
            self.prepare((202406, 202409))
        with self.assertRaisesRegex(ValueError, 'singleton'):
            self.prepare((202409,))

    def test_unknown_batch_scope_is_not_a_candidate(self):
        for scope in ('financial-recent-202312-202606-v1/202403',
                      'financial-recent-202312-202606-v1/202609',
                      'financial-recent-202312-202606-v1/202406/nonce'):
            with self.subTest(scope=scope):
                self.document['acquisition_scope'] = scope
                with self.assertRaises(ValueError):
                    self.prepare((202406,))


class AcquisitionCliTests(unittest.TestCase):
    """Actual CLI/package flow; only trust anchors/root and OS claim are fixtures."""
    catalog_source = AcquisitionTests.catalog_source
    prepare = AcquisitionTests.prepare
    metadata = AcquisitionTests.metadata
    source = AcquisitionTests.source

    def setUp(self):
        import os
        from contextlib import contextmanager
        self.api = importlib.import_module('bank_quality.financial_acquisition')
        AcquisitionTests.setUp(self)
        if os.name != 'nt':
            @contextmanager
            def model_claim(path):
                path.touch(exist_ok=True)
                yield
            claim = patch.object(self.api, '_claim', model_claim)
            claim.start()
            self.addCleanup(claim.stop)
        self.job = self.prepare(limits=dict(self.api._POLICIES))
        self.job_path = self.root / 'data/runs/preparation/job.json'
        self.job_path.parent.mkdir(parents=True)
        self.job_path.write_bytes(canonical(self.job))
        self.job_args = ['--job', str(self.job_path), '--job-sha256', self.job['job_sha256']]
        transport = patch('bank_quality.archive.fetch_bounded', side_effect=AssertionError('Unexpected GET'))
        transport.start()
        self.addCleanup(transport.stop)
        launch = patch.object(self.api, 'run_contained_attempt', side_effect=AssertionError('Unexpected launch'))
        launch.start()
        self.addCleanup(launch.stop)

    def invoke(self, *arguments):
        import importlib.util
        import io
        from contextlib import redirect_stdout, redirect_stderr
        path = Path(__file__).resolve().parents[1] / 'scripts/acquire-financial.py'
        self.assertTrue(path.is_file(), 'Thin acquisition CLI missing')
        spec = importlib.util.spec_from_file_location('acquisition_cli_test', path)
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = cli.main(list(arguments))
            except SystemExit as error:
                code = error.code
        return code, stdout.getvalue(), stderr.getvalue()

    def initialize(self):
        code, out, err = self.invoke('initialize-authority', *self.job_args)
        self.assertEqual((code, err), (0, ''))
        return json.loads(out)['bootstrap_sha256']

    def bound_args(self, pin):
        return [*self.job_args, '--bootstrap-sha256', pin]

    def snapshot(self):
        folder = self.api._authority_paths(self.job)[0]
        return {p.name: p.read_bytes() for p in folder.iterdir() if p.is_file()}

    def test_prepare_is_offline_exclusive_and_never_grants_authority(self):
        output = self.root / 'data/runs/new-preparation/job.json'
        args = ['prepare', '--catalog-index', str(self.index), '--catalog-index-sha256', sha(self.index.read_bytes()),
                '--output', str(output)]
        code, out, err = self.invoke(*args)
        self.assertEqual((code, err), (0, ''))
        prepared = json.loads(output.read_bytes())
        self.assertFalse(prepared['executable'])
        self.assertEqual(prepared['job_sha256'], self.job['job_sha256'])
        self.assertEqual(prepared['policies'], self.api._POLICIES)
        self.assertEqual(json.loads(out)['status'], 'candidate')
        self.assertFalse(self.api._authority_paths(prepared)[1].exists())
        before = output.read_bytes()
        code, out, err = self.invoke(*args)
        self.assertEqual((code, out), (2, ''))
        self.assertIn('new', err.lower())
        self.assertEqual(output.read_bytes(), before)

    def test_prepare_wrong_index_hash_and_destination_fail_without_output(self):
        for output, pin in ((self.root / 'data/runs/bad/job.json', '0' * 64),
                            (self.root / 'outside/job.json', sha(self.index.read_bytes()))):
            code, out, err = self.invoke('prepare', '--catalog-index', str(self.index), '--catalog-index-sha256', pin,
                                         '--output', str(output))
            self.assertEqual((code, out), (2, ''))
            self.assertTrue(err)
            self.assertFalse(output.exists())

    def test_explicit_initialization_cannot_reset_existing_budget(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='fixture')
        before = self.snapshot()
        code, out, err = self.invoke('initialize-authority', *self.job_args)
        self.assertEqual((code, out), (2, ''))
        self.assertIn('no reset', err)
        self.assertEqual(self.snapshot(), before)

    def test_recover_pending_is_offline_and_conservatively_charged(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='fixture')
        output = self.root / 'data/runs/recovery/receipt.json'
        code, out, err = self.invoke('recover', *self.bound_args(pin), '--output', str(output))
        self.assertEqual((code, err), (0, ''))
        receipt = json.loads(output.read_bytes())
        self.assertFalse(receipt['state']['pending'])
        self.assertEqual(receipt['state']['attempts'], 1)
        self.assertEqual(receipt['state']['body_bytes'], 5 * 1024 * 1024)
        self.assertEqual(json.loads(out)['attempt_seconds'], 120)
        self.assertEqual(self.invoke('recover', *self.bound_args(pin), '--output', str(output))[0], 2)

    def test_verify_current_authority_with_pending_is_readonly_and_private(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='private-coordination')
        before = self.snapshot()
        code, out, err = self.invoke('verify', *self.bound_args(pin))
        self.assertEqual((code, err), (0, ''))
        result = json.loads(out)
        self.assertEqual(result['status'], 'verified_pending')
        self.assertEqual(result['pending_attempts'], 1)
        self.assertEqual(result['attempts'], 1)
        for secret in ('private-coordination', 'headers', 'sources', 'targets', 'pid', 'context', 'https:', str(self.root)):
            self.assertNotIn(secret, out)
        self.assertEqual(self.snapshot(), before)

    def test_verify_api_rejects_pinned_nonobject_receipt_readonly(self):
        pin = self.initialize()
        receipt = self.root / 'data/runs/nonobject-receipt.json'
        before = self.snapshot()
        with patch('bank_quality.archive.fetch_bounded', side_effect=AssertionError('Unexpected GET')) as transport, \
                patch.object(self.api, 'run_contained_attempt', side_effect=AssertionError('Unexpected launch')) as launch:
            for raw in (b'[]', b'null', b'"receipt"', b'1', b'1.5', b'true'):
                with self.subTest(raw=raw):
                    receipt.write_bytes(raw)
                    try:
                        with self.assertRaisesRegex(ValueError, 'Receipt must be a JSON object'):
                            self.api.verify_authority(self.job_path, self.job['job_sha256'], bootstrap_sha256=pin,
                                                      receipt_path=receipt, receipt_sha256=sha(raw))
                    finally:
                        self.assertEqual(self.snapshot(), before)
                        transport.assert_not_called()
                        launch.assert_not_called()

    def test_verify_cli_rejects_pinned_nonobject_receipt_with_exit_two_readonly(self):
        pin = self.initialize()
        receipt = self.root / 'data/runs/nonobject-receipt.json'
        before = self.snapshot()
        with patch('bank_quality.archive.fetch_bounded', side_effect=AssertionError('Unexpected GET')) as transport, \
                patch.object(self.api, 'run_contained_attempt', side_effect=AssertionError('Unexpected launch')) as launch:
            for raw in (b'[]', b'null', b'"receipt"', b'1', b'1.5', b'true'):
                with self.subTest(raw=raw):
                    receipt.write_bytes(raw)
                    try:
                        code, out, err = self.invoke('verify', *self.bound_args(pin), '--receipt', str(receipt),
                                                     '--receipt-sha256', sha(raw))
                        self.assertEqual((code, out), (2, ''))
                        self.assertIn('Receipt must be a JSON object', err)
                        self.assertNotIn('Traceback', err)
                    finally:
                        self.assertEqual(self.snapshot(), before)
                        transport.assert_not_called()
                        launch.assert_not_called()

    def test_verify_cli_rejects_nonobject_job_with_exit_two_readonly(self):
        pin = self.initialize()
        before = self.snapshot()
        with patch('bank_quality.archive.fetch_bounded', side_effect=AssertionError('Unexpected GET')) as transport, \
                patch.object(self.api, 'run_contained_attempt', side_effect=AssertionError('Unexpected launch')) as launch:
            for raw in (b'[]', b'null', b'"job"', b'1', b'1.5', b'true'):
                with self.subTest(raw=raw):
                    self.job_path.write_bytes(raw)
                    try:
                        code, out, err = self.invoke('verify', '--job', str(self.job_path), '--job-sha256', sha(raw),
                                                     '--bootstrap-sha256', pin)
                        self.assertEqual((code, out), (2, ''))
                        self.assertIn('Job must be a JSON object', err)
                        self.assertNotIn('Traceback', err)
                    finally:
                        self.assertEqual(self.snapshot(), before)
                        transport.assert_not_called()
                        launch.assert_not_called()

    def test_old_receipt_verify_reports_current_expense_without_reset(self):
        pin = self.initialize()
        output = self.root / 'data/runs/old/receipt.json'
        self.assertEqual(self.invoke('recover', *self.bound_args(pin), '--output', str(output))[0], 0)
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='new')
        before = self.snapshot()
        code, out, err = self.invoke('verify', *self.bound_args(pin), '--receipt', str(output),
                                     '--receipt-sha256', sha(output.read_bytes()))
        self.assertEqual((code, err), (0, ''))
        result = json.loads(out)
        self.assertTrue(result['receipt_is_historical'])
        self.assertEqual(result['attempts'], 1)
        self.assertEqual(self.snapshot(), before)

    def test_wrong_job_bootstrap_receipt_and_missing_authority_refused(self):
        self.assertEqual(self.invoke('verify', *self.bound_args('0' * 64))[0], 2)
        self.assertFalse(self.api._authority_paths(self.job)[1].exists())
        pin = self.initialize()
        receipt = self.root / 'data/runs/receipt.json'
        self.api.recover_authority(self.job_path, self.job['job_sha256'], bootstrap_sha256=pin, output=receipt)
        for args in (['verify', '--job', str(self.job_path), '--job-sha256', '0' * 64, '--bootstrap-sha256', pin],
                     ['verify', *self.bound_args('0' * 64)],
                     ['verify', *self.bound_args(pin), '--receipt', str(receipt), '--receipt-sha256', '0' * 64]):
            before = self.snapshot()
            code, out, err = self.invoke(*args)
            self.assertEqual((code, out), (2, ''))
            self.assertIn('mismatch', err.lower())
            self.assertEqual(self.snapshot(), before)

    def test_historical_resume_new_session_keeps_spent_budget(self):
        self.job['reuse_sources'] = self.metadata(self.job)
        self.job_path.write_bytes(canonical(self.job))
        pin = self.initialize()
        old = self.root / 'data/runs/old/receipt.json'
        self.api.recover_authority(self.job_path, self.job['job_sha256'], bootstrap_sha256=pin, output=old)
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='spent')
        recovered = self.root / 'data/runs/recovered/receipt.json'
        self.api.recover_authority(self.job_path, self.job['job_sha256'], bootstrap_sha256=pin, output=recovered)
        with patch.object(self.api, 'require_supported'):
            code, out, err = self.invoke('metadata', *self.bound_args(pin), '--session', str(self.root / 'data/runs/new'),
                                         '--resume-from', str(old), '--resume-sha256', sha(old.read_bytes()))
        self.assertEqual((code, err), (0, ''))
        result = json.loads(out)
        self.assertEqual(result['attempts'], 1)
        self.assertEqual(result['body_bytes'], 5 * 1024 * 1024)
        self.assertEqual(result['attempt_seconds'], 120)

    def test_pending_authority_blocks_metadata_and_unsupported_never_falls_back(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='pending')
        session = self.root / 'data/runs/new'
        before = self.snapshot()
        with patch.object(self.api, 'require_supported'):
            code, out, err = self.invoke('metadata', *self.bound_args(pin), '--session', str(session))
        self.assertEqual((code, out), (2, ''))
        self.assertIn('offline recovery', err)
        with patch.object(self.api, 'require_supported', side_effect=RuntimeError('Unsupported fixture platform')):
            code, out, err = self.invoke('metadata', *self.bound_args(pin), '--session', str(session))
        self.assertEqual((code, out), (2, ''))
        self.assertIn('Unsupported', err)
        self.assertFalse(session.exists())
        self.assertEqual(self.snapshot(), before)

    def test_corrupt_current_head_cannot_be_repaired_by_verify(self):
        pin = self.initialize()
        head = self.api._authority_paths(self.job)[0] / 'head.json'
        head.write_bytes(b'{"sequence":999}')
        before = self.snapshot()
        code, out, err = self.invoke('verify', *self.bound_args(pin))
        self.assertEqual((code, out), (2, ''))
        self.assertIn('head', err.lower())
        self.assertEqual(self.snapshot(), before)

    def test_verify_missing_claim_file_refuses_without_recreation(self):
        pin = self.initialize()
        lock = self.api._authority_paths(self.job)[2]
        lock.unlink()
        before = self.snapshot()
        code, out, err = self.invoke('verify', *self.bound_args(pin))
        self.assertEqual((code, out), (2, ''))
        self.assertIn('claim', err.lower())
        self.assertFalse(lock.exists())
        self.assertEqual(self.snapshot(), before)

    def test_metadata_and_values_use_authenticated_reuse_and_physical_a(self):
        refs = self.metadata(self.job)
        resolved = self.api.resolve_sources(self.job, refs)
        numeric = resolved['numeric_targets'][0]
        self.job['reuse_sources'] = {**refs, numeric['target_key']: self.source(numeric, {'id': numeric['area'], 'values': []})}
        self.job_path.write_bytes(canonical(self.job))
        pin = self.initialize()
        # Platform check alone is modeled for Linux; actual auth/runner/reuse stays intact.
        with patch.object(self.api, 'require_supported'):
            a_session, b_session = self.root / 'data/runs/a', self.root / 'data/runs/b'
            code, out, err = self.invoke('metadata', *self.bound_args(pin), '--session', str(a_session))
            self.assertEqual((code, err), (0, ''))
            self.assertEqual(json.loads(out)['status'], 'metadata_complete')
            a, receipt = a_session / 'checkpoint-a.json', a_session / 'receipt.json'
            code, out, err = self.invoke('values', *self.bound_args(pin), '--session', str(b_session),
                                         '--checkpoint-a-sha256', '0' * 64, '--resume-from', str(receipt),
                                         '--resume-sha256', sha(receipt.read_bytes()))
            self.assertEqual((code, out), (2, ''))
            self.assertIn('Physical checkpoint A hash mismatch', err)
            self.assertFalse(b_session.exists())
            code, out, err = self.invoke('values', *self.bound_args(pin), '--session', str(b_session),
                                         '--checkpoint-a-sha256', sha(a.read_bytes()), '--resume-from', str(receipt),
                                         '--resume-sha256', sha(receipt.read_bytes()))
            self.assertEqual((code, err), (0, ''))
            self.assertEqual(json.loads(out)['status'], 'values_complete')
            self.assertEqual(json.loads(out)['attempts'], 0)
            b = json.loads((b_session / 'checkpoint-b.json').read_bytes())
            self.assertEqual(b['checkpoint_a_sha256'], sha(a.read_bytes()))
            self.assertEqual(self.invoke('metadata', *self.bound_args(pin), '--session', str(a_session))[0], 2)

    def test_values_before_a_and_wrong_a_fail_before_session_or_launch(self):
        pin = self.initialize()
        session = self.root / 'data/runs/refused'
        code, out, err = self.invoke('values', *self.bound_args(pin), '--session', str(session))
        self.assertEqual((code, out), (2, ''))
        self.assertFalse(session.exists())
        receipt = self.root / 'data/runs/no-a/receipt.json'
        self.api.recover_authority(self.job_path, self.job['job_sha256'], bootstrap_sha256=pin, output=receipt)
        with patch.object(self.api, 'require_supported'):
            code, out, err = self.invoke('values', *self.bound_args(pin), '--session', str(session),
                                         '--checkpoint-a-sha256', '0' * 64, '--resume-from', str(receipt),
                                         '--resume-sha256', sha(receipt.read_bytes()))
        self.assertEqual((code, out), (2, ''))
        self.assertIn('checkpoint-a.json', err)
        self.assertFalse(session.exists())

    def test_parser_rejects_unknown_phase_knobs_and_unpaired_pins(self):
        for args in ([], ['download'], ['prepare', '--url', 'https://example.test'],
                     ['metadata', *self.bound_args('0' * 64), '--session', str(self.root / 'data/runs/s'), '--workers', '2'],
                     ['verify', *self.bound_args('0' * 64), '--receipt', str(self.root / 'data/runs/receipt.json')],
                     ['metadata', *self.bound_args('0' * 64), '--session', str(self.root / 'data/runs/s'), '--resume-sha256', '0' * 64]):
            code, out, err = self.invoke(*args)
            self.assertEqual((code, out), (2, ''))
            self.assertTrue(err)
        for knob in ('--root', '--base', '--url', '--command', '--deadline-seconds'):
            code, out, err = self.invoke('verify', *self.bound_args('0' * 64), knob, 'unsafe')
            self.assertEqual((code, out), (2, ''))
            self.assertIn('unrecognized arguments', err)


    def test_batch_cli_commands_and_strict_external_arguments(self):
        for name in ('batch-prepare', 'batch-initialize', 'batch-run', 'batch-recover', 'batch-verify'):
            code, out, err = self.invoke(name, '--help')
            self.assertEqual(code, 0, err)
            self.assertIn(name, out)
            self.assertEqual(self.invoke(name)[0], 2)
        from bank_quality import financial_acquisition_batch as batch
        args = ['--bundle', str(self.job_path), '--bundle-sha256', 'a' * 64, '--bootstrap-sha256', 'b' * 64]
        with patch.object(batch, '_run_batch', return_value={'contract': 'financial-acquisition-batch-run-v1',
                'status': 'incomplete', 'missing_periods': [202406], 'private': 'never print'}) as run:
            code, out, err = self.invoke('batch-run', *args, '--metadata-workers', '2')
            self.assertEqual((code, err), (0, ''))
            self.assertEqual(run.call_args.kwargs['metadata_workers'], 2)
            self.assertNotIn('private', out)
            self.assertEqual(json.loads(out)['missing_periods'], [202406])
            self.assertEqual(self.invoke('batch-run', *args, '--metadata-workers', '3')[0], 2)
            self.assertEqual(self.invoke('batch-run', *args, '--metadata-work', '1')[0], 2)


class AuthorityTests(unittest.TestCase):
    """Pure authority model uses synthetic catalogs and a fake OS claim."""
    catalog_source = AcquisitionTests.catalog_source
    prepare = AcquisitionTests.prepare
    metadata = AcquisitionTests.metadata
    source = AcquisitionTests.source
    bounded_source = AcquisitionTests.bounded_source

    def setUp(self):
        from contextlib import nullcontext
        self.api = importlib.import_module('bank_quality.financial_acquisition')
        AcquisitionTests.setUp(self)
        self.job = self.prepare()
        # Claim behavior has separate real Windows tests, never a runner fallback.
        claim = patch.object(self.api, '_claim', lambda path: nullcontext(), create=True)
        claim.start()
        self.addCleanup(claim.stop)

    def initialize(self):
        self.assertTrue(hasattr(self.api, 'initialize_authority'), 'Explicit offline authority missing')
        return self.api.initialize_authority(self.job)

    def test_missing_authority_not_reinitialized(self):
        self.assertTrue(hasattr(self.api, 'open_authority'), 'Authority context missing')
        with self.assertRaises((ValueError, FileNotFoundError)):
            with self.api.open_authority(self.job, bootstrap_sha256='0' * 64):
                self.fail('Missing authority opened')

    def test_two_sessions_share_one_authority(self):
        pin = self.initialize()
        for position, session in enumerate(('first', 'second')):
            with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
                self.api.reserve_attempt(authority, self.job['targets'][position], session_id=session)
                self.api._recover_pending(authority)
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.assertEqual(authority.state['attempts'], 2)
            with self.assertRaisesRegex(ValueError, 'Attempt|pending'):
                self.api.reserve_attempt(authority, self.job['targets'][0], session_id='third')

    def test_orphan_reservation_charged(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')
            self.assertEqual(authority.state['body_bytes'], 5 * 1024 * 1024)
            self.assertEqual(authority.state['attempt_seconds'], 120)

    def test_partial_journal_tail_blocks_without_truncation(self):
        pin = self.initialize()
        path = self.api._authority_paths(self.job)[0] / 'journal.jsonl'
        with path.open('ab') as output:
            output.write(b'{"partial":')
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'tail'):
            with self.api.open_authority(self.job, bootstrap_sha256=pin):
                pass
        self.assertEqual(path.read_bytes(), before)

    def test_valid_old_prefix_conflicts_with_current_head(self):
        pin = self.initialize()
        folder = self.api._authority_paths(self.job)[0]
        old = (folder / 'journal.jsonl').read_bytes()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')
        (folder / 'journal.jsonl').write_bytes(old)
        with self.assertRaisesRegex(ValueError, 'head'):
            with self.api.open_authority(self.job, bootstrap_sha256=pin):
                pass

    def test_counter_underflow_or_reduced_counter_rejected(self):
        pin = self.initialize()
        folder = self.api._authority_paths(self.job)[0]
        raw = json.loads((folder / 'head.json').read_bytes())
        raw['state_sha256'] = '0' * 64
        (folder / 'head.json').write_bytes(canonical(raw))
        with self.assertRaisesRegex(ValueError, 'state|head'):
            with self.api.open_authority(self.job, bootstrap_sha256=pin):
                pass

    def test_reserve_fsync_failure_no_launch(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            with patch.object(self.api.os, 'fsync', side_effect=OSError('disk sync')):
                with self.assertRaises(OSError):
                    self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')
        with self.assertRaisesRegex(ValueError, 'head'):
            with self.api.open_authority(self.job, bootstrap_sha256=pin):
                pass

    def test_head_commit_failure_no_launch(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            with patch.object(self.api, '_replace_head', side_effect=OSError('head commit')):
                with self.assertRaises(OSError):
                    self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')

    def test_initialize_does_not_reset_budget(self):
        self.initialize()
        with self.assertRaises((ValueError, FileExistsError)):
            self.api.initialize_authority(self.job)

    def test_changed_limits_rejected_by_existing_scope_binding(self):
        self.initialize()
        changed = self.prepare(limits={'attempts': 3})
        with self.assertRaises(ValueError):
            self.api.initialize_authority(changed)

    def test_old_receipt_cannot_restore_budget(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            old = self.api._receipt(authority, 'a')
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='b')
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api._verify_receipt(old, authority)
            self.assertEqual(authority.state['attempts'], 1)
            self.assertEqual(authority.state['body_bytes'], 5 * 1024 * 1024)

    def test_recover_transport_calls_zero(self):
        pin = self.initialize()
        job_path = self.root / 'data/runs/job.json'
        job_path.parent.mkdir(parents=True, exist_ok=True)
        job_path.write_bytes(canonical(self.job))
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')
        with patch('bank_quality.archive.fetch_bounded', side_effect=AssertionError('transport called')):
            result = self.api.recover_authority(job_path, self.job['job_sha256'], bootstrap_sha256=pin,
                                                output=self.root / 'data/runs/recovery.json')
        self.assertEqual(result['state']['body_bytes'], 5 * 1024 * 1024)
        self.assertEqual(result['state']['failure_streak'], 1)

    def test_recover_live_worker_refused(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            attempt = self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')
            authority.commit('identity', attempt_id=attempt['attempt_id'], identity={'pid': 55, 'creation_time': 99, 'contained': True})
            with patch.object(self.api, 'identity_extinct', return_value=False):
                with self.assertRaisesRegex(ValueError, 'Live worker'):
                    self.api._recover_pending(authority)
            self.assertIn(attempt['attempt_id'], authority.state['pending'])

    def test_backoff_charged_once_across_resume(self):
        pin = self.initialize()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            authority.commit('backoff', attempt_id='wait', reserved_backoff_seconds=5, session_id='a')
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api._recover_pending(authority)
            self.assertEqual(authority.state['backoff_seconds'], 5)
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api._recover_pending(authority)
            self.assertEqual(authority.state['backoff_seconds'], 5)

    def test_deadline_guard_streak_not_reset_by_receipt(self):
        pin = self.initialize()
        for position in range(2):
            with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
                attempt = self.api.reserve_attempt(authority, self.job['targets'][position], session_id='a')
                authority.commit('finish', attempt_id=attempt['attempt_id'], status='deadline', retryable=False,
                                 guard='deadline', observed_bytes=attempt['reserved_bytes'], observed_attempt_seconds=120,
                                 tree_extinct=True)
                old = self.api._receipt(authority, 'a')
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api._verify_receipt(old, authority)
            self.assertEqual(authority.state.get('guard_streak'), 2)
            numeric = next(t for t in authority.targets.values() if t['role'] == 'numeric')
            with self.assertRaisesRegex(ValueError, 'guard'):
                self.api.reserve_attempt(authority, numeric, session_id='b')

    def test_run_metadata_reuse_and_complete_values_offline(self):
        self.assertTrue(hasattr(self.api, 'run_acquisition'), 'Acquisition coordinator missing')
        refs = self.metadata(self.job)
        checkpoint = self.api.resolve_sources(self.job, refs)
        numeric = checkpoint['numeric_targets'][0]
        self.job['reuse_sources'] = {**refs, numeric['target_key']: self.source(numeric, {'id': numeric['area'], 'values': []})}
        pin = self.initialize()
        job_path = self.root / 'data/runs/job.json'
        job_path.write_bytes(canonical(self.job))
        with patch.object(self.api, 'require_supported'), patch.object(self.api, 'run_contained_attempt', side_effect=AssertionError('transport launch')):
            metadata = self.api.run_acquisition(job_path, self.job['job_sha256'], self.root / 'data/runs/session-a',
                                                phase='metadata', bootstrap_sha256=pin)
            a_path = self.root / 'data/runs/session-a/checkpoint-a.json'
            a = json.loads(a_path.read_bytes())
            self.assertEqual(set(a), {'contract', 'phase', 'selection', 'descriptor_sha256', 'catalog', 'sources'})
            complete = self.api.run_acquisition(job_path, self.job['job_sha256'], self.root / 'data/runs/session-b',
                                                phase='values', bootstrap_sha256=pin, checkpoint_sha256=sha(a_path.read_bytes()),
                                                resume_from=self.root / 'data/runs/session-a/receipt.json',
                                                resume_sha256=sha((self.root / 'data/runs/session-a/receipt.json').read_bytes()))
        b = json.loads((self.root / 'data/runs/session-b/checkpoint-b.json').read_bytes())
        self.assertEqual(b['checkpoint_a_sha256'], sha(a_path.read_bytes()))
        self.assertEqual(b['phase'], 'complete')
        self.assertEqual(len(b['sources']), 3)
        self.assertEqual(complete['state']['attempts'], 0)
        self.assertEqual(metadata['state']['attempts'], 0)

    def test_values_without_physical_checkpoint_blocked_before_launch(self):
        self.assertTrue(hasattr(self.api, 'run_acquisition'), 'Acquisition coordinator missing')
        pin = self.initialize()
        job_path = self.root / 'data/runs/job.json'
        job_path.write_bytes(canonical(self.job))
        with patch.object(self.api, 'require_supported'), patch.object(self.api, 'run_contained_attempt') as launch:
            with self.assertRaisesRegex(ValueError, 'checkpoint'):
                self.api.run_acquisition(job_path, self.job['job_sha256'], self.root / 'data/runs/session-a',
                                        phase='values', bootstrap_sha256=pin)
            launch.assert_not_called()

    def test_complete_uncommitted_record_recover_preserves_charge(self):
        pin = self.initialize()
        folder = self.api._authority_paths(self.job)[0]
        old_head = (folder / 'head.json').read_bytes()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')
        (folder / 'head.json').write_bytes(old_head)
        with self.api._open_authority(self.job, pin, recover=True) as authority:
            self.api._recover_pending(authority)
            self.assertEqual(authority.state['attempts'], 1)
            self.assertEqual(authority.state['body_bytes'], 5 * 1024 * 1024)

    def test_internal_worker_standalone_has_zero_get(self):
        self.assertTrue(hasattr(self.api, '_worker_main'), 'Authenticated internal worker missing')
        pin = self.initialize()
        folder = self.root / 'data/runs'
        job_path = folder / 'job.json'
        job_path.write_bytes(canonical(self.job))
        import sys
        spec = {'contract': 'financial-acquisition-worker-v1', 'job_path': 'data/runs/job.json',
                'job_sha256': self.job['job_sha256'], 'bootstrap_sha256': pin, 'attempt_id': 'standalone',
                'target_key': self.job['targets'][0]['target_key'], 'body_budget_bytes': 5 * 1024 * 1024,
                'parent_identity': {'pid': 1, 'creation_time': 1}, 'output_path': 'data/runs/unauthorized-output',
                'application_sha256': sha(Path(sys.executable).read_bytes()), 'worker_sha256': sha(Path(self.api.__file__).read_bytes())}
        spec_path = folder / 'worker.json'
        spec_path.write_bytes(canonical(spec))
        with patch.object(self.api, 'require_supported'), patch('bank_quality.archive.fetch_bounded') as fetch:
            with self.assertRaisesRegex(ValueError, 'journal|reservation'):
                self.api._worker_main(spec_path, sha(spec_path.read_bytes()))
            fetch.assert_not_called()
        self.assertFalse((folder / 'unauthorized-output').exists())

    def test_bad_schema_guard_is_persisted(self):
        self.assertTrue(hasattr(self.api, 'run_acquisition'), 'Coordinator missing')
        refs = self.metadata(self.job)
        cadaster = next(t for t in self.job['targets'] if t['role'] == 'cadaster')
        refs[cadaster['target_key']] = self.source(cadaster, [])
        self.job['reuse_sources'] = refs
        pin = self.initialize()
        job_path = self.root / 'data/runs/job.json'
        job_path.write_bytes(canonical(self.job))
        with patch.object(self.api, 'require_supported'), patch.object(self.api, 'run_contained_attempt') as launch:
            with self.assertRaises(ValueError):
                self.api.run_acquisition(job_path, self.job['job_sha256'], self.root / 'data/runs/session-a',
                                        phase='metadata', bootstrap_sha256=pin)
            launch.assert_not_called()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            self.assertEqual(authority.state['guard'], 'schema')
            self.assertEqual(authority.state['guard_streak'], 1)
            self.assertIn(cadaster['target_key'], authority.state['failed_targets'])

    def test_run_reserve_and_head_failures_have_zero_launch(self):
        for failure in ('fsync', 'head'):
            with self.subTest(failure=failure):
                # Different root per subtest preserves all failed evidence.
                if failure == 'head':
                    self.temp2 = tempfile.TemporaryDirectory()
                    self.addCleanup(self.temp2.cleanup)
                    patcher = patch.object(self.api, '_ROOT', Path(self.temp2.name))
                    patcher.start()
                    self.addCleanup(patcher.stop)
                    # Authenticated catalog inputs remain relative to original root:
                    import shutil
                    shutil.copytree(self.root / 'data/raw', Path(self.temp2.name) / 'data/raw')
                active_root = self.api._ROOT
                pin = self.initialize()
                path = active_root / 'data/runs/job.json'
                path.write_bytes(canonical(self.job))
                fault = patch.object(self.api.os, 'fsync', side_effect=OSError('disk')) if failure == 'fsync' else \
                        patch.object(self.api, '_replace_head', side_effect=OSError('head'))
                with patch.object(self.api, 'require_supported'), patch.object(self.api, 'run_contained_attempt') as launch, fault:
                    with self.assertRaises(OSError):
                        self.api.run_acquisition(path, self.job['job_sha256'], active_root / 'data/runs/session-a',
                                                phase='metadata', bootstrap_sha256=pin)
                    launch.assert_not_called()

    def test_retry_only_transient_network_or_allowed_http(self):
        self.assertFalse(self.api._retryable({'outcome': 'network_error', 'http_status': None,
                                              'diagnostics': [{'code': 'transport_exception', 'detail': 'SSLCertVerificationError: invalid certificate'}]}))
        self.assertFalse(self.api._retryable({'outcome': 'transport_error', 'http_status': 503,
                                              'diagnostics': [{'code': 'incomplete_framing', 'detail': 'short body'}]}))
        for status in (408, 429, 500, 503, 599):
            self.assertTrue(self.api._retryable({'outcome': 'http_error', 'http_status': status,
                                                 'diagnostics': [{'code': 'http_status', 'detail': 'failed status'}]}))
        self.assertTrue(self.api._retryable({'outcome': 'network_error', 'http_status': None,
                                              'diagnostics': [{'code': 'transport_exception', 'detail': 'TimeoutError: timed out'}]}))
        self.assertFalse(self.api._retryable({'outcome': 'http_error', 'http_status': 302, 'diagnostics': []}))

    @unittest.skipUnless(__import__('os').name == 'nt', 'Real Win32 worker ancestry proof required')
    def test_live_standalone_worker_cannot_claim_own_identity(self):
        pin = self.initialize()
        import sys
        identity = self.api._current_identity()
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            attempt = self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')
            authority.commit('identity', attempt_id=attempt['attempt_id'], identity={**identity, 'contained': True})
            folder = self.root / 'data/runs'
            (folder / 'job.json').write_bytes(canonical(self.job))
            spec = {'contract': 'financial-acquisition-worker-v1', 'job_path': 'data/runs/job.json',
                    'job_sha256': self.job['job_sha256'], 'bootstrap_sha256': pin, 'attempt_id': attempt['attempt_id'],
                    'target_key': self.job['targets'][0]['target_key'], 'body_budget_bytes': attempt['reserved_bytes'],
                    'parent_identity': identity, 'output_path': 'data/runs/unauthorized-output',
                    'application_sha256': sha(Path(sys.executable).read_bytes()), 'worker_sha256': sha(Path(self.api.__file__).read_bytes())}
            spec_path = folder / 'standalone.json'
            spec_path.write_bytes(canonical(spec))
            with patch('bank_quality.archive.fetch_bounded') as fetch:
                with self.assertRaisesRegex(ValueError, 'ancestry'):
                    self.api._worker_main(spec_path, sha(spec_path.read_bytes()))
                fetch.assert_not_called()

    @unittest.skipUnless(__import__('os').name == 'nt', 'Real Win32 worker ancestry proof required')
    def test_contained_fixture_proves_current_reserve_and_launcher_ancestry(self):
        from bank_quality import windows_acquisition as windows
        import sys
        from tests import test_windows_acquisition
        pin = self.initialize()
        path = self.root / 'data/runs/job.json'
        path.write_bytes(canonical(self.job))
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority:
            attempt = self.api.reserve_attempt(authority, self.job['targets'][0], session_id='a')
            spec = {'contract': 'financial-acquisition-worker-v1', 'job_path': 'data/runs/job.json',
                    'job_sha256': self.job['job_sha256'], 'bootstrap_sha256': pin, 'attempt_id': attempt['attempt_id'],
                    'target_key': self.job['targets'][0]['target_key'], 'body_budget_bytes': attempt['reserved_bytes'],
                    'parent_identity': self.api._current_identity(), 'application_sha256': sha(Path(sys.executable).read_bytes()),
                    'worker_sha256': sha(Path(test_windows_acquisition.__file__).read_bytes()),
                    'fixture_authorization': True, 'fixture_root': str(self.root), 'fixture_frozen': self.api._FROZEN,
                    'marker': str(self.root / 'proof.json')}
            spec_path = self.root / 'data/runs/proof-worker.json'
            spec_path.write_bytes(canonical(spec))
            def before(identity):
                authority.commit('identity', attempt_id=attempt['attempt_id'], identity=identity)
            with patch.object(windows, '_WORKER_MODULE', 'tests.test_windows_acquisition'):
                result = windows.run_contained_attempt(spec_path, sha(spec_path.read_bytes()), deadline_seconds=4, before_resume=before)
            self.assertEqual(result['exit_code'], 0)
            self.assertEqual(json.loads((self.root / 'proof.json').read_bytes())['authorized_target'], self.job['targets'][0]['target_key'])
            self.assertTrue(result['tree_extinct'])

    def fake_attempt(self, spec_path, pin, *, deadline_seconds, before_resume):
        """Known fixture receipt; production parent authenticates every saved file."""
        import shutil
        spec = json.loads(spec_path.read_bytes())
        target = next(t for t in self.job['targets'] if t['target_key'] == spec['target_key'])
        before_resume({'pid': 7, 'creation_time': 9, 'contained': True})
        ref = self.bounded_source(target, {'fixture': 'entity body'})
        original = self.root / ref['manifest_path']
        manifest = json.loads(original.read_bytes())
        manifest['body_budget_bytes'] = spec['body_budget_bytes']
        if self.fake_status != 200:
            manifest.update(http_status=self.fake_status, outcome='http_error', source_complete=False,
                            diagnostics=[{'code': 'http_status', 'detail': 'HTTP ' + str(self.fake_status)}])
        sidecar = original.parent / manifest['response_metadata_path']
        metadata = json.loads(sidecar.read_bytes())
        metadata['http_status'] = self.fake_status
        sidecar.write_bytes(canonical(metadata))
        manifest['response_metadata_sha256'] = sha(sidecar.read_bytes())
        output = self.root / spec['output_path']
        output.mkdir()
        for name in (manifest['body_path'], manifest['response_metadata_path']):
            shutil.copyfile(original.parent / name, output / name)
        saved = output / original.name
        saved.write_bytes(canonical(manifest))
        (output / 'worker-receipt.json').write_bytes(canonical({'attempt_id': spec['attempt_id'], 'spec_sha256': pin,
                  'manifest_path': saved.relative_to(self.root).as_posix(), 'manifest_sha256': sha(saved.read_bytes())}))
        return {'tree_extinct': True, 'deadline_reached': False, 'deadline_overshoot_seconds': 0,
                'exit_code': 0, 'elapsed_seconds': 1.25}

    def test_attempt_observed_body_and_backend_time_replace_reservation(self):
        pin = self.initialize()
        job_path = self.root / 'data/runs/job.json'
        job_path.write_bytes(canonical(self.job))
        session = self.root / 'data/runs/attempt-model'
        session.mkdir()
        self.fake_status = 503
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority, \
                patch.object(self.api, '_current_identity', return_value={'pid': 1, 'creation_time': 2}), \
                patch.object(self.api, 'run_contained_attempt', side_effect=self.fake_attempt):
            self.assertTrue(self.api._attempt(authority, job_path, session, self.job['targets'][0]))
            body_size = len(canonical({'fixture': 'entity body'}))
            self.assertEqual(authority.state['body_bytes'], body_size)
            self.assertEqual(authority.state['attempt_seconds'], 2)
            self.assertEqual(authority.state['failures'], 1)
            self.fake_status = 200
            self.assertFalse(self.api._attempt(authority, job_path, session, self.job['targets'][0]))
            self.assertEqual(authority.state['body_bytes'], 2 * body_size)
            self.assertEqual(authority.state['attempt_seconds'], 4)
            self.assertEqual(authority.state['attempts'], 2)
            self.assertEqual(authority.state['failure_streak'], 0)
            self.assertIn(self.job['targets'][0]['target_key'], authority.state['sources'])
            self.assertEqual(len(list(session.glob('attempt-*/worker-receipt.json'))), 2)
            self.assertLess(authority.records[-3]['reserved_bytes'], 5 * 1024 * 1024)

    def test_failed_attempt_invalid_evidence_keeps_reservation_pending(self):
        self.fake_status = 503
        for position, mutation in enumerate(('missing_sidecar', 'corrupt_sidecar', 'sidecar_escape',
                                            'body_escape', 'contradictory_headers', 'forged_counter',
                                            'status_projection', 'final_url_projection', 'false_eof', 'removed_framing')):
            if position:
                self.doCleanups()
                self.setUp()
            pin = self.initialize()
            job_path = self.root / 'data/runs/job.json'
            job_path.write_bytes(canonical(self.job))
            with self.subTest(mutation=mutation):
                session = self.root / ('data/runs/' + mutation)
                session.mkdir()
                def invalid_evidence(spec_path, digest, **kwargs):
                    result = self.fake_attempt(spec_path, digest, **kwargs)
                    spec = json.loads(spec_path.read_bytes())
                    output = self.root / spec['output_path']
                    receipt_path = output / 'worker-receipt.json'
                    receipt = json.loads(receipt_path.read_bytes())
                    path = self.root / receipt['manifest_path']
                    manifest = json.loads(path.read_bytes())
                    sidecar = output / manifest['response_metadata_path']
                    if mutation == 'missing_sidecar':
                        sidecar.unlink()
                    elif mutation == 'corrupt_sidecar':
                        sidecar.write_bytes(b'corrupt')
                    elif mutation == 'sidecar_escape':
                        manifest['response_metadata_path'] = '../' + sidecar.name
                    elif mutation == 'body_escape':
                        manifest['body_path'] = '../../../raw/fixture/' + manifest['body_path']
                    elif mutation == 'contradictory_headers':
                        metadata = json.loads(sidecar.read_bytes())
                        metadata['response_headers_raw'] = [['Content-Length', '999']]
                        manifest['response_headers_raw'] = metadata['response_headers_raw']
                        sidecar.write_bytes(canonical(metadata))
                        manifest['response_metadata_sha256'] = sha(sidecar.read_bytes())
                    elif mutation == 'forged_counter':
                        manifest['content_length'] = manifest['bytes'] + 1
                    elif mutation == 'false_eof':
                        manifest.update(completion_basis='eof', eof_observed=False)
                    elif mutation == 'removed_framing':
                        manifest['completion_basis'] = None
                    else:
                        metadata = json.loads(sidecar.read_bytes())
                        metadata['http_status' if mutation == 'status_projection' else 'final_url'] = (
                            429 if mutation == 'status_projection' else 'https://invalid.example/fixture')
                        sidecar.write_bytes(canonical(metadata))
                        manifest['response_metadata_sha256'] = sha(sidecar.read_bytes())
                    path.write_bytes(canonical(manifest))
                    receipt['manifest_sha256'] = sha(path.read_bytes())
                    receipt_path.write_bytes(canonical(receipt))
                    return result
                with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority, \
                        patch.object(self.api, 'run_contained_attempt', side_effect=invalid_evidence), \
                        patch.object(self.api, '_current_identity', return_value={'pid': 7, 'creation_time': 9}):
                    with self.assertRaises((ValueError, FileNotFoundError)):
                        self.api._attempt(authority, job_path, session, self.job['targets'][0])
                    self.assertEqual(authority.state['body_bytes'], 5 * 1024 * 1024)
                    self.assertEqual(authority.state['attempt_seconds'], 120)
                    self.assertEqual(len(authority.state['pending']), 1)
                    self.assertEqual(authority.records[-1]['kind'], 'identity')
                    with patch.object(self.api, 'identity_extinct', return_value=True):
                        self.api._recover_pending(authority)
                    self.assertEqual(authority.state['body_bytes'], 5 * 1024 * 1024)
                    self.assertEqual(authority.state['attempt_seconds'], 120)
                    self.assertFalse(authority.state['pending'])

    def test_failed_partial_response_can_be_authenticated_without_eof(self):
        pin = self.initialize()
        job_path = self.root / 'data/runs/job.json'
        job_path.write_bytes(canonical(self.job))
        session = self.root / 'data/runs/partial-response'
        session.mkdir()
        self.fake_status = 503
        def partial_response(spec_path, digest, **kwargs):
            result = self.fake_attempt(spec_path, digest, **kwargs)
            output = self.root / json.loads(spec_path.read_bytes())['output_path']
            receipt_path = output / 'worker-receipt.json'
            receipt = json.loads(receipt_path.read_bytes())
            path = self.root / receipt['manifest_path']
            manifest = json.loads(path.read_bytes())
            manifest.update(completion_basis=None, eof_observed=False, content_length=manifest['bytes'] + 5)
            manifest['diagnostics'].append({'code': 'content_length_mismatch', 'detail': 'offline partial response'})
            manifest['response_headers_raw'] = [['Content-Length', str(manifest['content_length'])]]
            sidecar = output / manifest['response_metadata_path']
            metadata = json.loads(sidecar.read_bytes())
            metadata['response_headers_raw'] = manifest['response_headers_raw']
            sidecar.write_bytes(canonical(metadata))
            manifest['response_metadata_sha256'] = sha(sidecar.read_bytes())
            path.write_bytes(canonical(manifest))
            receipt['manifest_sha256'] = sha(path.read_bytes())
            receipt_path.write_bytes(canonical(receipt))
            return result
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority, \
                patch.object(self.api, 'run_contained_attempt', side_effect=partial_response), \
                patch.object(self.api, '_current_identity', return_value={'pid': 7, 'creation_time': 9}):
            self.assertFalse(self.api._attempt(authority, job_path, session, self.job['targets'][0]))
            self.assertEqual(authority.state['body_bytes'], len(canonical({'fixture': 'entity body'})))
            self.assertEqual(authority.records[-1]['status'], 'http_error')
            self.assertFalse(authority.state['pending'])
            self.assertFalse(authority.state['sources'])

    def test_no_response_connection_failure_authenticates_empty_body(self):
        from bank_quality.archive import fetch_bounded
        pin = self.initialize()
        job_path = self.root / 'data/runs/job.json'
        job_path.write_bytes(canonical(self.job))
        session = self.root / 'data/runs/no-response'
        session.mkdir()
        target = self.job['targets'][0]
        def connection_failure(spec_path, digest, **kwargs):
            spec = json.loads(spec_path.read_bytes())
            kwargs['before_resume']({'pid': 7, 'creation_time': 9, 'contained': True})
            output = self.root / spec['output_path']
            with patch('bank_quality.archive.build_opener') as opener:
                opener.return_value.open.side_effect = ConnectionRefusedError('offline fixture')
                manifest = fetch_bounded(target['url'], output, spec['attempt_id'],
                    {'period': target['period'], 'perspective': 1005, 'role': target['role']},
                    body_budget_bytes=spec['body_budget_bytes'])
            path = output / manifest['manifest_path']
            (output / 'worker-receipt.json').write_bytes(canonical({
                'attempt_id': spec['attempt_id'], 'spec_sha256': digest,
                'manifest_path': path.relative_to(self.root).as_posix(), 'manifest_sha256': sha(path.read_bytes())}))
            return {'tree_extinct': True, 'deadline_reached': False, 'deadline_overshoot_seconds': 0,
                    'exit_code': 0, 'elapsed_seconds': 1.25}
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority, \
                patch.object(self.api, 'run_contained_attempt', side_effect=connection_failure), \
                patch.object(self.api, '_current_identity', return_value={'pid': 7, 'creation_time': 9}):
            self.assertTrue(self.api._attempt(authority, job_path, session, target))
            self.assertEqual(authority.state['body_bytes'], 0)
            self.assertEqual(authority.records[-1]['status'], 'network_error')
            self.assertFalse(authority.state['pending'])

    def test_deadline_without_receipt_never_refunds_body_and_records_actual_overshoot(self):
        pin = self.initialize()
        path = self.root / 'data/runs/job.json'
        path.write_bytes(canonical(self.job))
        session = self.root / 'data/runs/deadline-model'
        session.mkdir()
        def deadline(spec_path, pin, *, deadline_seconds, before_resume):
            before_resume({'pid': 7, 'creation_time': 9, 'contained': True})
            return {'tree_extinct': True, 'deadline_reached': True, 'deadline_overshoot_seconds': .2,
                    'exit_code': 2, 'elapsed_seconds': 120.2}
        with self.api.open_authority(self.job, bootstrap_sha256=pin) as authority, \
                patch.object(self.api, '_current_identity', return_value={'pid': 1, 'creation_time': 2}), \
                patch.object(self.api, 'run_contained_attempt', side_effect=deadline):
            self.assertFalse(self.api._attempt(authority, path, session, self.job['targets'][0]))
            self.assertEqual(authority.state['body_bytes'], 5 * 1024 * 1024)
            self.assertEqual(authority.state['attempt_seconds'], 121)
            self.assertEqual(authority.state['guard'], 'deadline')
            self.assertEqual(authority.records[-1]['overshoot_microseconds'], 200000)
            self.assertFalse(authority.state['pending'])


if __name__ == '__main__':
    unittest.main()

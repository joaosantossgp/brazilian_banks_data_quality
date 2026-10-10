"""Offline profile authoring tests. Cadaster widths are synthetic, not history."""
import copy
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    from bank_quality import financial_report_profiles as profiles
except ImportError:
    profiles = None


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def sha(body):
    return hashlib.sha256(body).hexdigest()


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(profiles, 'Task1 profile authoring implementation is absent')
        self.addCleanup(patch.stopall)
        self.prepare_fixture()

    def prepare_fixture(self):
        """Give independent mutations fresh physical paths, without I/O retries."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pkg = self.root / 'bank_quality'
        self.pkg.mkdir()
        patch.object(profiles, 'CHECKOUT_ROOT', self.root).start()
        patch.object(profiles, 'PACKAGE_ROOT', self.pkg).start()
        self.selection = {'period': 201403, 'perspective': 1005, 'reports': [1, 3, 4, 5]}
        self.source_dir = self.root / 'data/raw/fixture'
        self.source_dir.mkdir(parents=True)
        self.prepare(24)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(dump(value))
        return path, sha(path.read_bytes())

    def archive(self, role, value, native_file=None, area=None):
        body = value if isinstance(value, bytes) else dump(value)
        name = role.replace(':', '-')
        body_path = self.source_dir / (name + '.bin')
        body_path.write_bytes(body)
        url = ('https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024' if role == 'catalog'
               else 'https://www3.bcb.gov.br/ifdata/index.html' if role == 'portal'
               else 'https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=' + native_file)
        manifest = {'method': 'GET', 'http_status': 200, 'outcome': 'ok', 'truncated': False,
                    'diagnostics': [], 'bytes': len(body), 'sha256': sha(body), 'body_path': body_path.name,
                    'url': url, 'final_url': url, 'retrieved_at_utc': '2026-10-04T12:00:00Z',
                    'response_headers': {'Content-Length': str(len(body))}, 'context': {'synthetic': True}}
        path = self.source_dir / (name + '.json')
        if self.selection['period'] != 202312 and role in ('cadaster', 'dictionary', 'numeric:1', 'numeric:3'):
            self.bounded_capture(path, manifest)
        path.write_bytes(dump(manifest))
        return {'source_id': role, 'role': 'numeric' if role.startswith('numeric:') else role,
                'area': area, 'native_file': native_file, 'catalog_pointer': None,
                'manifest_path': path.relative_to(self.root).as_posix(), 'manifest_sha256': sha(dump(manifest)),
                'body_sha256': sha(body), 'provenance_sha256': sha(dump(manifest))}

    def bounded_capture(self, path, manifest, basis='content_length', *, exact_cap=False):
        """Physical bounded capture evidence; no authentication results are mocked."""
        size = manifest['bytes']
        headers = ([['Transfer-Encoding', 'chunked']] if basis == 'chunked_eof' else
                   [] if basis == 'eof' else [['Content-Length', str(size)]])
        manifest.update(contract='bounded-http-archive-v1', source_complete=True,
                        body_available=True, bytes_observed=size,
                        body_budget_bytes=size if exact_cap else size + 1,
                        content_length=size if basis == 'content_length' else None,
                        eof_observed=basis != 'content_length', completion_basis=basis,
                        response_headers_raw=headers, response_headers=dict(headers))
        sidecar = {key: copy.deepcopy(manifest[key]) for key in
                   ('url', 'method', 'context', 'http_status', 'final_url', 'response_headers_raw')}
        sidecar_path = path.with_name(path.stem + '-response.json')
        sidecar_path.write_bytes(dump(sidecar))
        manifest.update(response_metadata_path=sidecar_path.name,
                        response_metadata_sha256=sha(sidecar_path.read_bytes()))

    def repin(self, source, manifest):
        path = self.root / source['manifest_path']
        path.write_bytes(dump(manifest))
        source.update(manifest_sha256=sha(path.read_bytes()), provenance_sha256=sha(dump(manifest)))

    def test_dataset_completion_reviewer_six_cases_are_refused(self):
        for target in ('cadaster', 'dictionary', 'numeric:1'):
            for mode in ('missing_completion', 'explicit_incomplete'):
                self.prepare(24)
                source = next((s for s in self.sources if s['source_id'] == target), None)
                candidate = self.compile() if source is None else None
                final = self.final() if source is None else None
                source = source or next(s for s in final['sources'] if s['source_id'] == target)
                manifest = json.loads((self.root / source['manifest_path']).read_bytes())
                for key in ('contract', 'source_complete', 'body_available', 'bytes_observed',
                            'body_budget_bytes', 'content_length', 'eof_observed', 'completion_basis',
                            'response_headers_raw', 'response_metadata_path', 'response_metadata_sha256'):
                    manifest.pop(key, None)
                manifest['response_headers'] = {'Transfer-Encoding': 'chunked'}
                if mode == 'explicit_incomplete':
                    manifest.update(contract='bounded-http-archive-v1', source_complete=False)
                self.repin(source, manifest)
                with self.subTest(target=target, mode=mode, stage='authenticate'), self.assertRaises(ValueError):
                    profiles._authenticate_source(source, self.descriptor)
                if candidate is None:
                    with self.subTest(target=target, mode=mode, stage='compile'), self.assertRaises(ValueError):
                        self.compile()
                else:
                    cp, ch = self.write('data/runs/candidate.json', candidate)
                    fp, fh = self.write('data/runs/final.json', final)
                    with self.subTest(target=target, mode=mode, stage='freeze'), self.assertRaises(ValueError):
                        profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)

    def test_positive_bounded_dataset_framing_reaches_freeze(self):
        for basis, exact_cap in (('eof', False), ('chunked_eof', False),
                                 ('content_length', False), ('content_length', True)):
            self.prepare(24)
            for source in self.sources[1:]:
                path = self.root / source['manifest_path']
                manifest = json.loads(path.read_bytes())
                self.bounded_capture(path, manifest, basis, exact_cap=exact_cap)
                self.repin(source, manifest)
            candidate = self.compile()
            final = self.final()
            for source in final['sources']:
                if source['role'] != 'numeric':
                    continue
                path = self.root / source['manifest_path']
                manifest = json.loads(path.read_bytes())
                self.bounded_capture(path, manifest, basis, exact_cap=exact_cap)
                self.repin(source, manifest)
            cp, ch = self.write('data/runs/candidate.json', candidate)
            fp, fh = self.write('data/runs/final.json', final)
            with self.subTest(basis=basis, exact_cap=exact_cap):
                result = profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)
                self.assertEqual(result['missing_sources'], [])

    def test_bounded_dataset_positive_claim_requires_physical_coherent_evidence(self):
        mutations = ('contract', 'source_complete', 'body_available', 'no_eof', 'basis',
                     'bytes', 'cap', 'bool_counter', 'length_counter', 'sidecar_missing',
                     'sidecar_corrupt', 'sidecar_escape', 'sidecar_context', 'sidecar_status',
                     'sidecar_url', 'sidecar_headers', 'duplicate_length', 'cl_te',
                     'encoding', 'terminal_mismatch', 'diagnostic', 'summary_headers')
        for mutation in mutations:
            self.prepare_fixture()
            source = self.sources[1]
            path = self.root / source['manifest_path']
            manifest = json.loads(path.read_bytes())
            self.bounded_capture(path, manifest, 'chunked_eof')
            sidecar_path = path.parent / manifest['response_metadata_path']
            sidecar = json.loads(sidecar_path.read_bytes())
            if mutation == 'contract': manifest['contract'] = 'generic-http'
            elif mutation == 'source_complete': manifest['source_complete'] = False
            elif mutation == 'body_available': manifest['body_available'] = False
            elif mutation == 'no_eof': manifest['eof_observed'] = False
            elif mutation == 'basis': manifest['completion_basis'] = None
            elif mutation == 'bytes': manifest['bytes_observed'] -= 1
            elif mutation == 'cap': manifest['body_budget_bytes'] = manifest['bytes'] - 1
            elif mutation == 'bool_counter': manifest['bytes_observed'] = True
            elif mutation == 'length_counter': manifest['content_length'] = manifest['bytes']
            elif mutation == 'sidecar_missing': sidecar_path.unlink()
            elif mutation == 'sidecar_corrupt': sidecar_path.write_bytes(b'corrupt')
            elif mutation == 'sidecar_escape': manifest['response_metadata_path'] = '../escape.json'
            elif mutation.startswith('sidecar_'):
                key = {'sidecar_context': 'context', 'sidecar_status': 'http_status',
                       'sidecar_url': 'final_url', 'sidecar_headers': 'response_headers_raw'}[mutation]
                sidecar[key] = {'tampered': True} if key == 'context' else 201 if key == 'http_status' else [] if key == 'response_headers_raw' else 'https://evil.example'
                sidecar_path.write_bytes(dump(sidecar))
                manifest['response_metadata_sha256'] = sha(sidecar_path.read_bytes())
            elif mutation in ('duplicate_length', 'cl_te', 'encoding'):
                manifest['response_headers_raw'] = ([['Content-Length', str(manifest['bytes'])]] * 2
                    if mutation == 'duplicate_length' else
                    [['Content-Length', str(manifest['bytes'])], ['Transfer-Encoding', 'chunked']]
                    if mutation == 'cl_te' else [['Transfer-Encoding', 'chunked'], ['Content-Encoding', 'gzip']])
                manifest['content_length'] = manifest['bytes'] if mutation != 'encoding' else None
                manifest['response_headers'] = dict(manifest['response_headers_raw'])
                sidecar['response_headers_raw'] = manifest['response_headers_raw']
                sidecar_path.write_bytes(dump(sidecar))
                manifest['response_metadata_sha256'] = sha(sidecar_path.read_bytes())
            elif mutation == 'terminal_mismatch': manifest['completion_basis'] = 'eof'
            elif mutation == 'diagnostic': manifest['diagnostics'] = [{'code': 'incomplete_read', 'detail': 'synthetic'}]
            elif mutation == 'summary_headers': manifest['response_headers'] = {'Content-Length': str(manifest['bytes'])}
            self.repin(source, manifest)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.compile()

    def prepare(self, width):
        period = self.selection['period']
        prefix = f'ifdata/{period}/'
        self.definitions = [{'id': 11, 'td': 1, 'a': 1, 'lid': 2, 'n': 'Opaque code'},
                            {'id': 12, 'td': 3, 'a': 1, 'lid': 7, 'n': 'Unknown unit'},
                            {'id': 13, 'td': 2, 'a': 1, 'lid': -1, 'n': 'Group'},
                            {'id': 14, 'td': 3, 'a': 3, 'lid': 7, 'n': 'Other origin'}]
        columns = [{'id': 10, 'ifd': 11, 'fid': 8, 'sc': []},
                   {'id': 20, 'ifd': 13, 'fid': 8, 'sc': [
                       {'id': 21, 'ifd': 12, 'fid': 8, 'sc': []},
                       {'id': 22, 'ifd': 14, 'fid': 8, 'sc': []}]}]
        files = [{'f': prefix + f'cadastro{period}_1005.json'}, {'f': prefix + f'info{period}.json'},
                 {'f': prefix + f'dados{period}_1.json'}, {'f': prefix + f'dados{period}_3.json'}]
        self.reports = [{'report': {'id': i, 'n': n, 's': [{'id': 1004}, {'id': 1005}],
                                      'c': copy.deepcopy(columns), 'rp': 'Opaque note', 'ratio': {'json_number': '1e-27'}},
                         'catalog_pointer': f'/0/files/{4+j}/trel'}
                        for j, (i, n) in enumerate(zip(self.selection['reports'], ['Resumo', 'Ativo', 'Passivo', 'DRE']))]
        files.extend({'f': prefix + f"trel{period}_{r['report']['id']}.json", 'trel': r['report']} for r in self.reports)
        self.catalog_value = [{'dt': period, 'files': files}]
        catalog = self.archive('catalog', dump(self.catalog_value).replace(b'{"json_number":"1e-27"}', b'1e-27'))
        offers = [{'source_id': role, 'role': 'numeric' if role.startswith('numeric:') else role,
                   'area': area, 'native_file': files[pos]['f'], 'catalog_pointer': f'/0/files/{pos}/f'}
                  for pos, role, area in [(0, 'cadaster', None), (1, 'dictionary', None),
                                          (2, 'numeric:1', 1), (3, 'numeric:3', 3)]]
        self.descriptor = {'selection': self.selection, 'catalog': {**catalog, 'reference_pointer': '/0'},
                           'reports': self.reports, 'source_offers': offers, 'profile_path': None,
                           'profile_sha256': None}
        self.registry = {'contract': 'ifdata-financial-reports-registry-v1', 'members': [self.descriptor]}
        self.install_registry()
        cadaster = [{f'c{i}': str(period) if i == 1 else 'opaque' + str(i) for i in range(width)}]
        self.sources = [catalog]
        for offer, value in zip(offers[:2], [cadaster, self.definitions]):
            self.sources.append({**self.archive(offer['source_id'], value, offer['native_file']), **offer})
        self.handoff = {'contract': 'ifdata-financial-historical-sources-v1', 'phase': 'metadata',
                        'selection': self.selection, 'descriptor_sha256': profiles.descriptor_for_selection(self.selection)['descriptor_sha256'],
                        'catalog': self.descriptor['catalog'], 'sources': self.sources}

    def install_registry(self):
        (self.pkg / 'financial-reports-registry.json').write_bytes(dump(self.registry))

    def compile(self, handoff=None):
        path, digest = self.write('data/runs/candidate-input.json', handoff or self.handoff)
        return profiles.compile_metadata_candidate(path, handoff_sha256=digest)

    def final(self):
        value = copy.deepcopy(self.handoff)
        value['phase'] = 'complete'
        value['checkpoint_a_sha256'] = sha(dump(self.handoff))
        value['sources'].append(self.archive('portal', {'formatter': 'opaque'}))
        for offer in self.descriptor['source_offers'][2:]:
            # Identical entity/lid/pointer in two origins is legitimate.
            value['sources'].append({**self.archive(offer['source_id'], {'id': offer['area'], 'values': [{'e': 1, 'v': [{'i': 7, 'v': '1e-27'}]}]},
                                                     offer['native_file'], offer['area']), **offer})
        return value

    def test_registry_rejects_noncanonical_unlisted_subset_and_profile_override(self):
        bad = [{'period': 201403.0, 'perspective': 1005, 'reports': [1, 3, 4, 5]},
               {**self.selection, 'perspective': '1005'}, {**self.selection, 'perspective': 1004},
               {**self.selection, 'reports': [3, 1, 4, 5]}, {**self.selection, 'reports': [1]},
               {**self.selection, 'period': 202609}, {**self.selection, 'period': 202612},
               {**self.selection, 'profile_path': 'other.json'}]
        for selection in bad:
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                profiles.descriptor_for_selection(selection)
        with self.assertRaises(ValueError):
            profiles.load_installed_context(self.selection)
        first = profiles.descriptor_for_selection(self.selection)
        first['reports'][0]['report']['n'] = 'mutated'
        self.assertEqual(profiles.descriptor_for_selection(self.selection)['reports'][0]['report']['n'], 'Resumo')

    def test_candidate_missing_numeric_sources_cannot_be_frozen(self):
        candidate = self.compile()
        self.assertEqual(candidate['missing_sources'], ['numeric:1', 'numeric:3', 'portal'])
        self.assertEqual(candidate['cadaster_columns'], [f'c{i}' for i in range(24)])
        node = candidate['reports'][0]['nodes'][2]
        self.assertEqual(node['origin_source_id'], 'numeric:1')
        self.assertEqual(node['unit'], 'unknown')
        self.assertEqual(node['window_basis'], 'unknown: no binding-specific evidence')
        self.assertEqual(candidate['reports'][0]['report']['ratio'], {'json_number': '1e-27'})
        candidate_path, digest = self.write('data/runs/candidate.json', candidate)
        path, hdigest = self.write('data/runs/final.json', self.handoff)
        with self.assertRaises(ValueError):
            profiles.freeze_profile(candidate_path, path, candidate_sha256=digest, final_handoff_sha256=hdigest)
        self.assertEqual(list(self.pkg.glob('financial-reports-profiles/*')), [])

    def test_freeze_complete_recompiles_preserves_origins_and_does_not_install(self):
        for mutation in ('missing_a', 'changed_a', 'invented_paired_hashes', 'candidate_pins',
                         'candidate_sources', 'complete_a', 'absolute_a', 'escape_a', 'url_a', 'backslash_a'):
            self.prepare(24)
            candidate = self.compile()
            final = self.final()
            candidate.setdefault('metadata_handoff_path', 'data/runs/candidate-input.json')
            checkpoint = self.root / 'data/runs/candidate-input.json'
            if mutation in ('missing_a', 'invented_paired_hashes'):
                checkpoint.unlink()
                if mutation == 'invented_paired_hashes':
                    candidate['metadata_handoff_sha256'] = final['checkpoint_a_sha256'] = '0' * 64
            elif mutation == 'changed_a':
                checkpoint.write_bytes(dump({**self.handoff, 'note': 'changed physical bytes'}))
            elif mutation == 'candidate_pins':
                candidate['source_pins']['cadaster']['provenance_sha256'] = '0' * 64
            elif mutation == 'candidate_sources':
                candidate['source_members'] = {}
                candidate['source_pins'] = {}
            elif mutation == 'complete_a':
                checkpoint.write_bytes(dump({**self.handoff, 'phase': 'complete'}))
                candidate['metadata_handoff_sha256'] = final['checkpoint_a_sha256'] = sha(checkpoint.read_bytes())
            else:
                candidate['metadata_handoff_path'] = {'absolute_a': checkpoint.as_posix(),
                    'escape_a': 'data/runs/../candidate-input.json', 'url_a': 'https://example.com/a',
                    'backslash_a': 'data\\runs\\candidate-input.json'}[mutation]
            cp, ch = self.write('data/runs/candidate.json', candidate)
            fp, fh = self.write('data/runs/final.json', final)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)
        for width in (24, 32, 38):
            with self.subTest(width=width):
                self.prepare(width)
                candidate = self.compile()
                cp, ch = self.write('data/runs/candidate.json', candidate)
                fp, fh = self.write('data/runs/final.json', self.final())
                artifact = profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)
                self.assertEqual(artifact['contract'], 'ifdata-financial-reports-historical-profile-v1')
                self.assertEqual(len(artifact['cadaster_columns']), width)
                self.assertEqual(artifact['reports'][0]['report']['s'], [{'id': 1004}, {'id': 1005}])
                self.assertEqual(set(artifact['source_pins']), {'catalog', 'cadaster', 'dictionary', 'numeric:1', 'numeric:3', 'portal'})
                self.assertNotIn('metadata_handoff_path', artifact)
                self.assertIsNone(profiles.descriptor_for_selection(self.selection)['profile_path'])
                candidate['reports'][0]['nodes'][2]['origin_source_id'] = 'numeric:3'
                cp, ch = self.write('data/runs/tampered.json', candidate)
                with self.assertRaises(ValueError):
                    profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)

    def test_freeze_sanitizes_private_manifest_headers_and_pins_projection(self):
        candidate = self.compile()
        cp, ch = self.write('data/runs/candidate.json', candidate)
        final = self.final()
        source = final['sources'][-1]
        path = self.root / source['manifest_path']
        manifest = json.loads(path.read_bytes())
        manifest['response_headers']['Set-Cookie'] = 'private-session-cookie'
        manifest['response_headers_raw'].append(['Set-Cookie', 'private-session-cookie'])
        sidecar_path = path.parent / manifest['response_metadata_path']
        sidecar = json.loads(sidecar_path.read_bytes())
        sidecar['response_headers_raw'] = manifest['response_headers_raw']
        sidecar_path.write_bytes(dump(sidecar))
        manifest['response_metadata_sha256'] = sha(sidecar_path.read_bytes())
        manifest['unnecessary_transport_note'] = 'private transport details'
        path.write_bytes(dump(manifest))
        source['manifest_sha256'] = source['provenance_sha256'] = sha(dump(manifest))
        fp, fh = self.write('data/runs/final.json', final)
        artifact = profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)
        self.assertNotIn(b'private-session-cookie', dump(artifact))
        self.assertNotIn(b'response_headers', dump(artifact))
        self.assertNotIn(b'private transport details', dump(artifact))
        record = artifact['source_members']['numeric:3']
        self.assertEqual(record['context'], {'synthetic': True})
        self.assertEqual(record['truncation_state'], 'observed_false')
        pin = artifact['source_pins']['numeric:3']
        self.assertEqual(pin['provenance_sha256'], source['provenance_sha256'])
        self.assertEqual(pin['projection_sha256'], sha(dump(record)))
        context = {'selection': self.selection, 'profile': artifact}
        body, observed = profiles._authenticate_installed_source(source, context)
        self.assertEqual(sha(body), pin['body_sha256'])
        self.assertEqual(observed, record)
        # A self-consistent new public projection is not proof of the original context.
        context['profile']['source_members']['numeric:3']['context'] = {'forged': True}
        context['profile']['source_pins']['numeric:3']['projection_sha256'] = sha(dump(context['profile']['source_members']['numeric:3']))
        with self.assertRaises(ValueError): profiles._authenticate_installed_source(source, context)

    def test_compile_crosschecks_native_metadata(self):
        for mutation in ('digest', 'pointer', 'url', 'area', 'context', 'escape', 'body_hash', 'source_role'):
            value = copy.deepcopy(self.handoff)
            if mutation == 'digest': value['descriptor_sha256'] = '0' * 64
            elif mutation == 'pointer': value['catalog']['reference_pointer'] = '/1'
            elif mutation == 'area': value['sources'][1]['area'] = 3
            elif mutation == 'escape': value['sources'][1]['manifest_path'] = '../fixture.json'
            elif mutation == 'body_hash': value['sources'][1]['body_sha256'] = '0' * 64
            elif mutation == 'source_role': value['sources'][1]['role'] = 'numeric'
            else:
                path = self.root / value['sources'][1]['manifest_path']
                original = path.read_bytes()
                manifest = json.loads(original)
                manifest['url' if mutation == 'url' else 'context'] = 'https://evil.example' if mutation == 'url' else {'mutated': True}
                path.write_bytes(dump(manifest))
                value['sources'][1]['manifest_sha256'] = sha(dump(manifest))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.compile(value)
            if mutation in ('url', 'context'): path.write_bytes(original)
        # Valid new hashes do not make an unsupported origin valid.
        defs = copy.deepcopy(self.definitions)
        defs[0]['lid'] = 99
        value = copy.deepcopy(self.handoff)
        offer = self.descriptor['source_offers'][1]
        value['sources'][2] = {**self.archive('dictionary', defs, offer['native_file']), **offer}
        with self.assertRaises(ValueError): self.compile(value)

    def test_paths_reject_absolute_url_backslash_and_reparse(self):
        for name in ('C:/elsewhere.json', '/elsewhere.json', 'https://example.com/a', 'data\\raw\\a.json', 'data/raw/../a.json'):
            value = copy.deepcopy(self.handoff)
            value['sources'][1]['manifest_path'] = name
            with self.subTest(name=name), self.assertRaises(ValueError): self.compile(value)

    def test_source_mutants_with_coherent_hashes_do_not_bypass_transport_and_origin(self):
        for mutation in ('double_slash', 'nonutc', 'framing', 'truncated', 'failed', 'duplicate_json', 'duplicate_numeric'):
            self.prepare(24)
            value = self.final()
            value['phase'] = 'metadata'
            source = value['sources'][-1]
            path = self.root / source['manifest_path']
            manifest = json.loads(path.read_bytes())
            if mutation == 'double_slash':
                manifest['url'] = manifest['final_url'] = manifest['url'].replace('ifdata/201403', 'ifdata//201403')
            elif mutation == 'nonutc': manifest['retrieved_at_utc'] = '2026-10-04T12:00:00-03:00'
            elif mutation == 'framing': manifest['response_headers']['Content-Length'] = '1'
            elif mutation == 'truncated': manifest['truncated'] = True
            elif mutation == 'failed': manifest['outcome'] = 'failed'
            else:
                body = (b'{"id":3,"id":3,"values":[]}' if mutation == 'duplicate_json' else
                        dump({'id': 3, 'values': [{'e': 1, 'v': [{'i': 7, 'v': 0}, {'i': 7, 'v': 0}]}]}))
                (path.parent / manifest['body_path']).write_bytes(body)
                manifest.update(bytes=len(body), sha256=sha(body))
                self.bounded_capture(path, manifest)
                source['body_sha256'] = sha(body)
            path.write_bytes(dump(manifest))
            source['manifest_sha256'] = source['provenance_sha256'] = sha(dump(manifest))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.compile(value)

    def test_report_tree_membership_and_unsupported_dictionary_origins_rejected(self):
        for mutation in ('membership', 'tree', 'definition', 'unadvertised_area'):
            self.prepare(24)
            value = copy.deepcopy(self.handoff)
            if mutation in ('membership', 'tree'):
                catalog = copy.deepcopy(self.catalog_value)
                report = catalog[0]['files'][4]['trel']
                if mutation == 'membership': report['s'] = [{'id': 1004}]
                else: report['c'][0]['ifd'] = 14
                value['sources'][0] = self.archive('catalog', catalog)
                # Catalogue raw hash is anchored by installed descriptor, independent of new handoff hashes.
            else:
                defs = copy.deepcopy(self.definitions)
                defs[1]['id' if mutation == 'definition' else 'a'] = 999
                offer = self.descriptor['source_offers'][1]
                value['sources'][2] = {**self.archive('dictionary', defs, offer['native_file']), **offer}
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.compile(value)

    def test_historical_installed_profile_rejects_binding_origin_mutation_before_runtime(self):
        candidate = self.compile()
        cp, ch = self.write('data/runs/candidate.json', candidate)
        fp, fh = self.write('data/runs/final.json', self.final())
        artifact = profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)
        path = self.pkg / 'financial-reports-profiles/201403.json'
        path.parent.mkdir()
        self.descriptor['profile_path'] = 'financial-reports-profiles/201403.json'
        path.write_bytes(dump(artifact))
        self.descriptor['profile_sha256'] = sha(dump(artifact))
        self.install_registry()
        context = profiles.load_installed_context(self.selection)
        self.assertEqual(context['cadaster_columns'], [f'c{i}' for i in range(24)])
        self.assertEqual(context['contract'], 'ifdata-financial-reports-historical-snapshot-v1')
        context['profile']['reports'][0]['nodes'][2]['origin_source_id'] = 'mutated'
        self.assertEqual(profiles.load_installed_context(self.selection)['profile']['reports'][0]['nodes'][2]['origin_source_id'], 'numeric:1')
        for mutation in ('source_id', 'cadaster', 'definition', 'metadata', 'source_map', 'unit_window'):
            changed = copy.deepcopy(artifact)
            if mutation == 'source_id': changed['reports'][0]['nodes'][2]['origin_source_id'] = 'numeric:3'
            elif mutation == 'cadaster': changed['cadaster_columns'].append('c99')
            elif mutation == 'definition': changed['reports'][0]['nodes'][2]['definition']['lid'] = 8
            elif mutation == 'metadata': changed['reports'][0]['report']['s'] = [{'id': 1004}]
            elif mutation == 'source_map': changed['source_members']['numeric:1']['area'] = 3
            else:
                changed['reports'][0]['nodes'][2]['unit'] = 'BRL'
                changed['reports'][0]['nodes'][2]['window_end'] = '2014-03-31'
            path.write_bytes(dump(changed))
            self.descriptor['profile_sha256'] = sha(dump(changed))
            self.install_registry()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                profiles.load_installed_context(self.selection)

    def test_installed_active_profile_missing_wrong_hash_and_path_override_fail(self):
        self.descriptor['profile_path'] = 'financial-reports-profiles/201403.json'
        self.descriptor['profile_sha256'] = '0' * 64
        self.install_registry()
        with self.assertRaises(ValueError): profiles.load_installed_context(self.selection)
        path = self.pkg / 'financial-reports-profiles/201403.json'
        path.parent.mkdir()
        path.write_bytes(b'{}')
        with self.assertRaises(ValueError): profiles.load_installed_context(self.selection)
        self.descriptor['profile_path'] = '../escape.json'
        self.install_registry()
        with self.assertRaises(ValueError): profiles.load_installed_context(self.selection)
        self.descriptor['descriptor_sha256'] = '0' * 64
        self.install_registry()
        with self.assertRaises(ValueError): profiles.descriptor_for_selection(self.selection)


@contextmanager
def legacy_bundle():
    """Synthetic closed312 bundle; execute actual Summary/source authentication."""
    fixture = ProfileTests('test_candidate_missing_numeric_sources_cannot_be_frozen')
    fixture.setUp()
    try:
        fixture.selection = {'period': 202312, 'perspective': 1005, 'reports': [92, 96, 101, 98]}
        fixture.prepare(32)
        fixture.definitions[-1]['a'] = 1
        offer = fixture.descriptor['source_offers'][1]
        fixture.sources[2] = {**fixture.archive('dictionary', fixture.definitions, offer['native_file']), **offer}
        fixture.sources.append(fixture.archive('portal', b'synthetic formatter'))
        offer = fixture.descriptor['source_offers'][2]
        fixture.sources.append({**fixture.archive('numeric:1', {'id': 1, 'values': [
            {'e': 1, 'v': [{'i': 7, 'v': '1e-27'}]}]}, offer['native_file'], 1), **offer})
        summary = {'contract': 'ifdata-financial-profile-202312-v1',
                   'selection': {'period': 202312, 'perspective': 1005, 'report': 92},
                   'source_baseline': {'portal_sha256': fixture.sources[3]['body_sha256']},
                   'formatter_fragments': ['synthetic formatter'], 'source_pins': {}, 'legacy_sources': {}}
        for source in fixture.sources:
            if source['role'] not in ('dictionary', 'numeric'):
                continue
            path = fixture.root / source['manifest_path']
            manifest = json.loads(path.read_bytes())
            del manifest['truncated']
            manifest['diagnostics'] = ['synthetic legacy capture: completeness undeclared']
            manifest['context']['body_capture'] = 'synthetic-original-body-capture'
            path.write_bytes(dump(manifest))
            source['manifest_sha256'] = source['provenance_sha256'] = sha(dump(manifest))
            summary['legacy_sources'][source['role']] = {
                'manifest_sha256': source['manifest_sha256'], 'body_sha256': source['body_sha256'],
                'diagnostics': manifest['diagnostics'], 'body_capture': manifest['context']['body_capture']}
        fixture.summary_path = fixture.pkg / 'financial-profile-202312.json'
        fixture.summary_path.write_bytes(dump(summary))
        patch.object(profiles.legacy, 'PROFILE_202312_PATH', fixture.summary_path).start()
        context = profiles.legacy._profile_for_selection(summary['selection'])
        for source in fixture.sources:
            _, record = profiles.legacy._source(source['role'], fixture.root / source['manifest_path'], context)
            pin = {'manifest_sha256': source['manifest_sha256'], 'body_sha256': source['body_sha256'],
                   'provenance_sha256': profiles._digest(record)}
            if source['role'] in summary['legacy_sources']:
                summary['legacy_sources'][source['role']].update(pin)
            else:
                summary['source_pins'][source['role']] = pin
        fixture.summary_path.write_bytes(dump(summary))
        fixture.registry['legacy_202312_sources'] = {s['source_id']: copy.deepcopy(s) for s in fixture.sources}
        fixture.install_registry()
        fixture.index = {'contract': 'ifdata-financial-sources-v1', 'selection': summary['selection'],
                         'sources': {s['role']: '../../raw/fixture/' + Path(s['manifest_path']).name for s in fixture.sources}}
        fixture.index_path, fixture.index_hash = fixture.write('data/runs/legacy/source-index.json', fixture.index)
        yield fixture
    finally:
        fixture.doCleanups()


@contextmanager
def acquisition_bridge(*, limits=None):
    """Synthetic claim/roots/trust anchors; physical validators stay real."""
    from bank_quality import financial_acquisition as api
    from bank_quality import financial_acquisition_batch as batch
    from tests.test_financial_acquisition import AcquisitionTests, CATALOG_URLS
    fixture = AcquisitionTests('test_catalog_hash_changed')
    fixture.api = api
    fixture.setUp()
    try:
        # Claim exclusivity has dedicated Windows tests. This single-process
        # fixture needs the durable claim file without invoking the Win32 API.
        @contextmanager
        def fixture_claim(path):
            if not path.exists():
                path.touch()
            yield
        claim = patch.object(api, '_claim', fixture_claim)
        claim.start()
        fixture.addCleanup(claim.stop)
        # Native authoring also consumes names/fid, absent from acquisition-only
        # fixtures. Add them to original fixture bodies before preparing the job.
        def columns(nodes):
            for node in nodes:
                node['fid'] = 8
                columns(node['sc'])
        for name, entries in fixture.catalogs.items():
            for entry in entries:
                for item in entry['files']:
                    if 'trel' in item:
                        columns(item['trel']['c'])
            ref = fixture.catalog_source(name, entries)
            path = fixture.root / ref['manifest_path']
            manifest = json.loads(path.read_bytes())
            manifest.update(context={'purpose': 'official source discovery'},
                            response_headers={'Content-Length': str(manifest['bytes'])})
            path.write_bytes(dump(manifest))
            ref.update(manifest_sha256=sha(path.read_bytes()), provenance_sha256=sha(dump(manifest)))
            fixture.document['catalogs'][name] = ref
            api._FROZEN[name] = (ref['manifest_sha256'], ref['body_sha256'], CATALOG_URLS[name])
        fixture.job = fixture.prepare(limits=limits or dict(api._POLICIES))
        fixture.pkg = fixture.root / 'bank_quality'
        fixture.pkg.mkdir()
        for module, name, value in ((profiles, 'CHECKOUT_ROOT', fixture.root),
                                    (profiles, 'PACKAGE_ROOT', fixture.pkg),
                                    (batch, '_ROOT', fixture.root)):
            injection = patch.object(module, name, value)
            injection.start()
            fixture.addCleanup(injection.stop)
        def write(name, value):
            path = fixture.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(dump(value))
            return {'path': name, 'sha256': sha(path.read_bytes())}
        fixture.write = write
        fixture.descriptor = copy.deepcopy(fixture.job['descriptors'][0])
        fixture.registry = {'contract': profiles.REGISTRY_CONTRACT, 'members': [fixture.descriptor]}
        acquisition_source = fixture.source
        def source(target, body):
            ref = acquisition_source(target, body)
            path = fixture.root / ref['manifest_path']
            manifest = json.loads(path.read_bytes())
            manifest['response_headers'] = dict(manifest['response_headers_raw'])
            sidecar = {k: manifest[k] for k in ('url', 'method', 'context', 'http_status', 'final_url', 'response_headers_raw')}
            sidecar_path = path.parent / manifest['response_metadata_path']
            sidecar_path.write_bytes(dump(sidecar))
            manifest['response_metadata_sha256'] = sha(sidecar_path.read_bytes())
            path.write_bytes(dump(manifest))
            ref.update(manifest_sha256=sha(path.read_bytes()), provenance_sha256=sha(dump(manifest)))
            return ref
        fixture.source = source
        metadata = fixture.metadata(fixture.job)
        dictionary = next(ref for ref in metadata.values() if ref['role'] == 'dictionary')
        path = fixture.root / dictionary['manifest_path']
        manifest = json.loads(path.read_bytes())
        definitions = json.loads((path.parent / manifest['body_path']).read_bytes())
        for definition in definitions:
            definition['n'] = 'Synthetic native definition'
            if definition['id'] == 80002:
                definition['a'] = 3
        target = next(t for t in fixture.job['targets'] if t['role'] == 'dictionary')
        metadata[target['target_key']] = fixture.source(target, definitions)
        fixture.resolved = api.resolve_sources(fixture.job, metadata)
        sources = dict(metadata)
        for target in fixture.resolved['numeric_targets']:
            sources[target['target_key']] = fixture.source(target, {'id': target['area'], 'values': [
                {'e': 1, 'v': [{'i': 80001, 'v': '1e-27'}, {'i': 80002, 'v': 0}]}]})
        fixture.bootstrap = api.initialize_authority(fixture.job)
        with api.open_authority(fixture.job, bootstrap_sha256=fixture.bootstrap) as authority:
            for key, ref in sources.items():
                reservation = api.reserve_attempt(authority, authority.targets[key], session_id='synthetic')
                authority.commit('finish', attempt_id=reservation['attempt_id'], target_key=key,
                                 session_id='synthetic', status='source_complete', retryable=False,
                                 source_ref=ref, observed_bytes=json.loads((fixture.root / ref['manifest_path']).read_bytes())['bytes'],
                                 observed_attempt_seconds=1, tree_extinct=True)
                if ref['role'] == 'dictionary':
                    metadata_receipt = api._receipt(authority, 'metadata')
            authority.commit('recovery')
            receipt = api._receipt(authority, 'values')
            authority.commit('recovery')
        a = fixture.resolved['checkpoints'][0]
        apin = write('data/runs/bridge-original/a.json', a)
        projection = ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'manifest_path',
                      'manifest_sha256', 'body_sha256', 'provenance_sha256')
        b = {**a, 'phase': 'complete', 'checkpoint_a_sha256': apin['sha256'],
             'sources': sorted([{k: ref[k] for k in projection} for ref in sources.values()], key=lambda s: s['source_id'])}
        bpin = write('data/runs/bridge-original/b.json', b)
        fixture.entry = {'period': 202403, 'kind': 'accepted_sources',
                         'manifest_path': 'data/runs/bridge-original/job.json',
                         'manifest_sha256': write('data/runs/bridge-original/job.json', fixture.job)['sha256'],
                         'evidence': {'job_sha256': fixture.job['job_sha256'], 'bootstrap_sha256': fixture.bootstrap,
                                      'checkpoint_a': apin, 'checkpoint_b': bpin,
                                      'resolution': write('data/runs/bridge-original/resolution.json', fixture.resolved),
                                      'receipt': write('data/runs/bridge-original/receipt.json', receipt),
                                      'metadata_receipt': write('data/runs/bridge-original/metadata-receipt.json', metadata_receipt)}}
        injection = patch.object(batch, '_TRUSTED_REUSE', {202403: {'entry': copy.deepcopy(fixture.entry)}})
        injection.start()
        fixture.addCleanup(injection.stop)
        portal_body = b'synthetic formatter'
        portal_dir = fixture.root / 'data/raw/portal'
        portal_dir.mkdir()
        (portal_dir / 'portal.bin').write_bytes(portal_body)
        portal_manifest = {'method': 'GET', 'http_status': 200, 'outcome': 'ok', 'truncated': False,
                           'diagnostics': [], 'bytes': len(portal_body), 'sha256': sha(portal_body), 'body_path': 'portal.bin',
                           'url': 'https://www3.bcb.gov.br/ifdata/index.html',
                           'final_url': 'https://www3.bcb.gov.br/ifdata/index.html',
                           'retrieved_at_utc': '2026-10-01T12:00:00Z',
                           'response_headers': {'Content-Length': str(len(portal_body))},
                           'context': {'purpose': 'official source discovery'}}
        pp = write('data/raw/portal/portal.json', portal_manifest)
        fixture.portal = {'source_id': 'portal', 'role': 'portal', 'area': None,
                          'native_file': None, 'catalog_pointer': None, 'manifest_path': pp['path'],
                          'manifest_sha256': pp['sha256'], 'body_sha256': sha(portal_body),
                          'provenance_sha256': sha(dump(portal_manifest))}
        fixture.registry['legacy_202312_sources'] = {'portal': fixture.portal}
        fixture.install_registry = lambda: write('bank_quality/financial-reports-registry.json', fixture.registry)
        fixture.install_registry()
        fixture.input = {'contract': 'ifdata-financial-acquisition-bridge-input-v1', 'entry': fixture.entry}
        fixture.input_pin = write('data/runs/bridge-input.json', fixture.input)
        yield fixture
    finally:
        fixture.doCleanups()


@contextmanager
def acquisition_batch_bridge():
    from test_financial_acquisition_batch import BatchAuthorityTests
    BatchAuthorityTests.setUpClass()
    f = BatchAuthorityTests('test_explicit_offline_initialization_and_external_pins')
    original_write = f.write
    def write(relative, value):
        if relative in ('data/raw/catalog/old.json', 'data/raw/catalog/new.json'):
            value.update({'diagnostics': [], 'retrieved_at_utc': '2026-10-01T12:00:00Z',
                     'response_headers': {'Content-Length': str(value['bytes'])},
                     'context': {'purpose': 'official source discovery'}})
        return original_write(relative, value)
    f.write = write
    try:
        f.setUp()
        f.pkg = f.root / 'bank_quality'
        f.pkg.mkdir(exist_ok=True)
        f.inject(profiles, 'CHECKOUT_ROOT', f.root)
        f.inject(profiles, 'PACKAGE_ROOT', f.pkg)
        for name in f.identity['files']:
            f.write(name, name.encode())
        f.refs = f.initialize()
        f.batch._run_serial(f.root / f.refs['bundle_path'], f.refs['bundle_sha256'],
                            bootstrap_sha256=f.refs['bootstrap_sha256'], phase_callable=f.terminal)
        with f.opened(f.refs) as authority:
            totals = f.batch._totals(authority)
            f.bundle = copy.deepcopy(authority.bundle)
            entries = []
            for reuse in authority.bundle['reuse']:
                entries.append({'period': reuse['period'], 'new_http_requests': 0,
                                'state': 'reused_' + reuse['kind'], 'reuse_evidence': copy.deepcopy(reuse)})
            for member in authority.bundle['members']:
                phases = {p['phase']: p['result'] for p in authority.state['finished'].values()
                          if p['period'] == member['period']}
                final = f.batch._read(phases['values']['checkpoint'])
                entries.append({'period': member['period'], 'state': 'acquired_validated_sources',
                    'selection': member['job']['descriptors'][0]['selection'],
                    'descriptor_sha256': member['job']['descriptors'][0]['descriptor_sha256'],
                    'job': {'path': member['job_path'], 'sha256': member['job_file_sha256'],
                            'canonical_sha256': member['job_sha256']},
                    'bootstrap_sha256': member['bootstrap_sha256'],
                    'metadata_receipt': phases['metadata']['receipt'], 'values_receipt': phases['values']['receipt'],
                    'checkpoint_a': phases['metadata']['checkpoint'], 'checkpoint_b': phases['values']['checkpoint'],
                    'sources': final['sources'],
                    'counters': next(c for c in totals['members'] if c['period'] == member['period']),
                    'financial_admission': False, 'parquet_admission': False})
        f.handoff = {'contract': 'financial-acquisition-batch-handoff-v1', 'scope': f.batch._SCOPE,
            'bundle': {'path': f.refs['bundle_path'], 'sha256': f.refs['bundle_sha256']},
            'bootstrap_sha256': f.refs['bootstrap_sha256'], 'entries': sorted(entries, key=lambda e: e['period']),
            'accepted_parquet_periods': [202312, 202412, 202503],
            'sources_only_periods': [202403, *f.batch._ACQUIRE], 'missing_periods': [],
            'totals': totals['totals'],
            'claim': 'native source completion; no historical financial comparability or new Parquet admission'}
        body = b'synthetic formatter'
        f.write('data/raw/portal/portal.bin', body)
        manifest = {'method': 'GET', 'http_status': 200, 'outcome': 'ok', 'truncated': False,
                    'diagnostics': [], 'bytes': len(body), 'sha256': sha(body), 'body_path': 'portal.bin',
                    'url': 'https://www3.bcb.gov.br/ifdata/index.html',
                    'final_url': 'https://www3.bcb.gov.br/ifdata/index.html',
                    'retrieved_at_utc': '2026-10-01T12:00:00Z',
                    'response_headers': {'Content-Length': str(len(body))},
                    'context': {'purpose': 'official source discovery'}}
        pin = f.write('data/raw/portal/portal.json', manifest)
        f.portal = {'source_id': 'portal', 'role': 'portal', 'area': None, 'native_file': None,
                    'catalog_pointer': None, 'manifest_path': pin['path'], 'manifest_sha256': pin['sha256'],
                    'body_sha256': sha(body), 'provenance_sha256': sha(dump(manifest))}
        f.write('bank_quality/financial-reports-registry.json', {'contract': profiles.REGISTRY_CONTRACT,
            'members': [m['job']['descriptors'][0] for m in f.bundle['members']],
            'legacy_202312_sources': {'portal': f.portal}})
        f.handoff_pin = f.write('data/runs/batch-handoff.json', f.handoff)
        yield f
    finally:
        f.doCleanups()


@contextmanager
def historical_acquisition_bridge():
    from tests.test_financial_acquisition_batch import HistoricalPreparationTests
    f = HistoricalPreparationTests('test_initialization_is_exact_new_and_verifiable_without_sources')
    try:
        f.setUp()
        # Give the synthetic official catalog the provenance required by the
        # authoring reader before capturing any jobs or descriptors.
        index = json.loads(f.index.read_bytes())
        frozen = {}
        for name, ref in index['catalogs'].items():
            path = f.root / ref['manifest_path']
            manifest = json.loads(path.read_bytes())
            body_path = path.parent / manifest['body_path']
            catalog = json.loads(body_path.read_bytes())
            for entry in catalog:
                for offer in entry['files']:
                    if 'trel' in offer:
                        for column in offer['trel']['c']:
                            column['fid'] = 8
            body_path.write_bytes(dump(catalog))
            manifest.update(bytes=len(body_path.read_bytes()), sha256=sha(body_path.read_bytes()))
            manifest.update(diagnostics=[], retrieved_at_utc='2026-10-01T12:00:00Z',
                response_headers={'Content-Length': str(manifest['bytes'])},
                context={'purpose': 'official source discovery'})
            path.write_bytes(dump(manifest))
            ref.update(manifest_sha256=sha(path.read_bytes()), provenance_sha256=sha(path.read_bytes()),
                       body_sha256=manifest['sha256'])
            frozen[name] = (ref['manifest_sha256'], ref['body_sha256'], manifest['url'])
        f.index.write_bytes(dump(index))
        patcher = patch.object(f.acquisition, '_FROZEN', frozen)
        patcher.start()
        f.addCleanup(patcher.stop)
        pins = {'contract': 'financial-acquisition-code-pins-v2', 'reviewed_commit': '1' * 40,
            'files': {name: 'a' * 64 for name in f.batch._CODE_FILES_V2},
            'runtime': {'path': '.venv/Scripts/python.exe', 'sha256': 'b' * 64},
            'policy_sha256': f.batch._HISTORICAL_POLICY_SHA256}
        initialize = f.batch.initialize_historical_batch
        bounded_source = f.bounded_source

        def named_source(target, payload):
            if target['role'] == 'dictionary':
                payload = [dict(definition, n='synthetic binding') for definition in payload]
            source = bounded_source(target, payload)
            path = f.root / source['manifest_path']
            manifest = json.loads(path.read_bytes())
            manifest.update(retrieved_at_utc='2026-10-01T12:00:00Z',
                            response_headers=dict(manifest['response_headers_raw']))
            sidecar_path = path.parent / manifest['response_metadata_path']
            sidecar = {key: manifest[key] for key in
                       ('url', 'method', 'context', 'http_status', 'final_url', 'response_headers_raw')}
            sidecar_path.write_bytes(dump(sidecar))
            manifest['response_metadata_sha256'] = sha(sidecar_path.read_bytes())
            path.write_bytes(dump(manifest))
            source.update(manifest_sha256=sha(path.read_bytes()), provenance_sha256=sha(path.read_bytes()))
            return source

        f.bounded_source = named_source
        with patch.object(f.batch, 'initialize_historical_batch',
                          side_effect=lambda *a, **kw: initialize(*a, **dict(kw, reviewed_code_pins=pins))):
            f._v3_roundtrip()
        f.pkg = f.root / 'bank_quality'
        f.pkg.mkdir(exist_ok=True)
        for name, value in (('CHECKOUT_ROOT', f.root), ('PACKAGE_ROOT', f.pkg)):
            patcher = patch.object(profiles, name, value)
            patcher.start()
            f.addCleanup(patcher.stop)
        f.bundle_path = f.root / f.batch._historical_window('F1-01')['destination'] / 'bundle.json'
        f.bundle = json.loads(f.bundle_path.read_bytes())
        f.handoff_path = f.root / 'data/runs/handoff.json'
        f.handoff = json.loads(f.handoff_path.read_bytes())
        folder = f.root / 'data/raw/portal'
        folder.mkdir(parents=True)
        body = b'synthetic formatter'
        (folder / 'portal.bin').write_bytes(body)
        manifest = {'method': 'GET', 'http_status': 200, 'outcome': 'ok', 'truncated': False,
            'diagnostics': [], 'bytes': len(body), 'sha256': sha(body), 'body_path': 'portal.bin',
            'url': 'https://www3.bcb.gov.br/ifdata/index.html',
            'final_url': 'https://www3.bcb.gov.br/ifdata/index.html',
            'retrieved_at_utc': '2026-10-01T12:00:00Z',
            'response_headers': {'Content-Length': str(len(body))},
            'context': {'purpose': 'official source discovery'}}
        (folder / 'portal.json').write_bytes(dump(manifest))
        f.portal = {'source_id': 'portal', 'role': 'portal', 'area': None, 'native_file': None,
            'catalog_pointer': None, 'manifest_path': 'data/raw/portal/portal.json',
            'manifest_sha256': sha(dump(manifest)), 'body_sha256': sha(body),
            'provenance_sha256': sha(dump(manifest))}
        registry = {'contract': profiles.REGISTRY_CONTRACT,
            'members': [member['job']['descriptors'][0] for member in f.bundle['members']],
            'legacy_202312_sources': {'portal': f.portal}}
        (f.pkg / 'financial-reports-registry.json').write_bytes(dump(registry))
        yield f
    finally:
        f.doCleanups()


class HistoricalAcquisitionBridgeTests(unittest.TestCase):
    def test_completed_historical_capture_projects_to_common_profile_authoring(self):
        with historical_acquisition_bridge() as f:
            def compose():
                return profiles.compose_historical_acquisition_handoffs(f.bundle_path, f.handoff_path,
                    bundle_sha256=sha(f.bundle_path.read_bytes()),
                    bootstrap_sha256=sha((f.bundle_path.parent / 'bootstrap.json').read_bytes()),
                    handoff_sha256=sha(f.handoff_path.read_bytes()))

            before = {p.relative_to(f.root).as_posix(): sha(p.read_bytes())
                      for p in f.root.rglob('*') if p.is_file()}
            with patch.object(f.batch, '_open_batch', side_effect=AssertionError('active authority')), \
                    patch.object(f.batch, '_code_identity_v2', side_effect=AssertionError('old executable')):
                result = compose()
            self.assertEqual(result['contract'], 'ifdata-financial-acquisition-batch-bridge-v2')
            self.assertEqual([m['selection']['period'] for m in result['members']], [201003, 201006, 201009, 201012])
            self.assertEqual(result['batch']['window_id'], 'F1-01')
            self.assertEqual(result['source_state_absent'],
                             [f.bundle['destination'] + '/halt.json'])
            for member in result['members']:
                self.assertEqual(member['metadata_handoff_sha256'], sha(dump(member['metadata_handoff'])))
                self.assertEqual(member['final_handoff']['checkpoint_a_sha256'], member['metadata_handoff_sha256'])
                self.assertEqual(member['final_handoff_sha256'], sha(dump(member['final_handoff'])))
                self.assertFalse(member['acquisition_evidence']['financial_admission'])
                self.assertFalse(member['acquisition_evidence']['parquet_admission'])
                self.assertEqual({s['source_id'] for s in member['final_handoff']['sources']},
                                 {'catalog', 'portal', 'cadaster', 'dictionary', 'numeric:3'})
            for ref in result['source_state_files']:
                raw = (f.root / ref['path']).read_bytes()
                self.assertEqual((len(raw), sha(raw)), (ref['bytes'], ref['sha256']))
            self.assertEqual(before, {p.relative_to(f.root).as_posix(): sha(p.read_bytes())
                                     for p in f.root.rglob('*') if p.is_file()})
            registry_path = f.pkg / 'financial-reports-registry.json'
            portal_path = f.root / 'data/raw/portal/portal.bin'
            original_registry, original_portal = registry_path.read_bytes(), portal_path.read_bytes()
            halt = f.bundle_path.parent / 'halt.json'
            projection = profiles._project_acquisition_handoffs
            for damage in ('descriptor', 'portal', 'late_registry', 'late_portal', 'late_halt'):
                def changed_projection(*args):
                    value = projection(*args)
                    if damage == 'late_registry':
                        registry_path.write_bytes(original_registry + b' ')
                    elif damage == 'late_portal':
                        portal_path.write_bytes(original_portal + b' ')
                    elif damage == 'late_halt':
                        halt.write_bytes(b'{}')
                    return value

                try:
                    if damage == 'descriptor':
                        registry = json.loads(original_registry)
                        registry['members'][0]['selection']['reports'].reverse()
                        registry_path.write_bytes(dump(registry))
                    elif damage == 'portal':
                        portal_path.write_bytes(original_portal + b' ')
                    with self.subTest(damage=damage), \
                            patch.object(profiles, '_project_acquisition_handoffs', side_effect=changed_projection):
                        with self.assertRaises(ValueError):
                            compose()
                finally:
                    registry_path.write_bytes(original_registry)
                    portal_path.write_bytes(original_portal)
                    if halt.exists():
                        halt.unlink()
            # Exercise the actual common compiler/freeze, not only envelope shape.
            for member in result['members']:
                folder = f.root / 'data/runs/projected' / str(member['selection']['period'])
                folder.mkdir(parents=True)
                a, b, candidate_path = folder / 'a.json', folder / 'b.json', folder / 'candidate.json'
                a.write_bytes(dump(member['metadata_handoff']))
                b.write_bytes(dump(member['final_handoff']))
                candidate = profiles.compile_metadata_candidate(a, handoff_sha256=sha(a.read_bytes()))
                candidate_path.write_bytes(dump(candidate))
                frozen = profiles.freeze_profile(candidate_path, b,
                    candidate_sha256=sha(candidate_path.read_bytes()), final_handoff_sha256=sha(b.read_bytes()))
                self.assertEqual(frozen['selection'], member['selection'])
                self.assertEqual(frozen['cadaster_columns'], ['c0', 'c1'])

    def test_bridge_projects_all_policy_windows_from_verified_proof_seam(self):
        """Dispatch coverage only; complete native capture/authoring is tested above."""
        with historical_acquisition_bridge() as f:
            proof = f.batch.verify_historical_capture(f.bundle_path, f.handoff_path,
                bundle_sha256=sha(f.bundle_path.read_bytes()),
                bootstrap_sha256=sha((f.bundle_path.parent / 'bootstrap.json').read_bytes()),
                handoff_sha256=sha(f.handoff_path.read_bytes()))
            template = proof['members'][0]
            descriptors, drafts = [], []
            for window in f.batch._HISTORICAL_POLICY_V1['windows']:
                draft = f.prepare(window['window_id'])
                drafts.append(draft)
                descriptors.extend(m['job']['descriptors'][0] for m in draft['members'])
            registry_path = f.pkg / 'financial-reports-registry.json'
            registry = json.loads(registry_path.read_bytes())
            registry['members'] = descriptors
            registry_path.write_bytes(dump(registry))
            seen = []
            for draft in drafts:
                selection_proof = copy.deepcopy(proof)
                selection_proof.update(window_id=draft['window_id'], members=[],
                                       source_state_files=[], source_state_absent=[])
                counters = []
                for member in draft['members']:
                    descriptor = member['job']['descriptors'][0]
                    captured = dict(copy.deepcopy(template), period=member['period'], selection=descriptor['selection'])
                    for key in ('checkpoint_a', 'checkpoint_b'):
                        path = f.root / 'data/runs/dispatch' / str(member['period']) / (key + '.json')
                        path.parent.mkdir(parents=True, exist_ok=True)
                        original = json.loads((f.root / template[key]['path']).read_bytes())
                        original.update(selection=descriptor['selection'], catalog=descriptor['catalog'],
                                        descriptor_sha256=descriptor['descriptor_sha256'])
                        path.write_bytes(dump(original))
                        captured[key] = {'path': path.relative_to(f.root).as_posix(), 'sha256': sha(path.read_bytes())}
                    selection_proof['members'].append(captured)
                    counters.append(dict(proof['source_state']['members'][0], period=member['period']))
                selection_proof['source_state']['members'] = counters

                def projected(originals, descriptor):
                    self.assertEqual(originals['metadata']['selection'], descriptor['selection'])
                    value = copy.deepcopy(originals)
                    value['complete']['checkpoint_a_sha256'] = sha(dump(value['metadata']))
                    return value

                with self.subTest(window=draft['window_id']), \
                        patch.object(f.batch, 'verify_historical_capture', return_value=selection_proof), \
                        patch.object(profiles, '_project_acquisition_handoffs', side_effect=projected):
                    result = profiles.compose_historical_acquisition_handoffs(f.bundle_path, f.handoff_path,
                        bundle_sha256=sha(f.bundle_path.read_bytes()),
                        bootstrap_sha256=sha((f.bundle_path.parent / 'bootstrap.json').read_bytes()),
                        handoff_sha256=sha(f.handoff_path.read_bytes()))
                    periods = [m['selection']['period'] for m in result['members']]
                    self.assertEqual(periods, draft['acquire_periods'])
                    self.assertEqual([m['selection']['reports'] for m in result['members']],
                                     [m['job']['member']['reports'] for m in draft['members']])
                    self.assertEqual(result['batch']['window_id'], draft['window_id'])
                    seen.extend(periods)
            self.assertEqual(len(seen), 55)
            self.assertEqual(len(set(seen)), 55)


class BatchAcquisitionBridgeTests(unittest.TestCase):
    snapshot = lambda self, f: {p.relative_to(f.root).as_posix(): sha(p.read_bytes())
                               for p in f.root.rglob('*') if p.is_file()}

    def compose(self, f, value=None, **overrides):
        self.assertTrue(callable(getattr(profiles, 'compose_batch_acquisition_handoffs', None)),
                        'Aggregate offline acquisition handoff composer is absent')
        pin = f.handoff_pin if value is None else f.write('data/runs/forged-handoff.json', value)
        args = {'bundle_sha256': f.refs['bundle_sha256'], 'bootstrap_sha256': f.refs['bootstrap_sha256'],
                'handoff_sha256': pin['sha256'], **overrides}
        return profiles.compose_batch_acquisition_handoffs(f.root / f.refs['bundle_path'],
                                                          f.root / pin['path'], **args)

    def test_batch_bridge_projects_all_seven_without_rewriting_originals(self):
        with acquisition_batch_bridge() as f:
            before = self.snapshot(f)
            result = self.compose(f)
            self.assertEqual(before, self.snapshot(f))
            self.assertEqual(set(result), {'contract', 'batch', 'source_state', 'source_state_files', 'members', 'limitations'})
            self.assertEqual(result['contract'], 'ifdata-financial-acquisition-batch-bridge-v1')
            self.assertEqual([m['selection']['period'] for m in result['members']], list(f.batch._ACQUIRE))
            for member in result['members']:
                period = member['selection']['period']
                evidence = next(e for e in f.handoff['entries'] if e['period'] == period)
                self.assertEqual(member['acquisition_evidence'], evidence)
                self.assertEqual(member['authority']['counters'], evidence['counters'])
                self.assertLess(member['authority']['metadata_receipt_sequence'], member['authority']['sequence'])
                self.assertEqual(member['final_handoff']['checkpoint_a_sha256'], member['metadata_handoff_sha256'])
                self.assertEqual(member['metadata_handoff_sha256'], sha(dump(member['metadata_handoff'])))
                self.assertEqual(member['final_handoff_sha256'], sha(dump(member['final_handoff'])))
                expected_reports = [119, 107, 110, 118] if period >= 202503 else [92, 96, 101, 98]
                self.assertEqual(member['selection']['reports'], expected_reports)
                sources = {s['source_id']: s for s in member['final_handoff']['sources']}
                self.assertEqual(sources['portal'], f.portal)
                descriptor = next(m['job']['descriptors'][0] for m in f.bundle['members'] if m['period'] == period)
                self.assertEqual(sources['catalog']['body_sha256'], descriptor['catalog']['body_sha256'])
                prefix = ('ifdata_2025_2030//' if period >= 202503 else 'ifdata/') + str(period) + '/'
                self.assertTrue(sources['dictionary']['native_file'].startswith(prefix))
                original = f.batch._read(evidence['checkpoint_a'])
                self.assertEqual({k: v for k, v in member['metadata_handoff'].items() if k != 'sources'},
                                 {k: v for k, v in original.items() if k != 'sources'})
            for pin in result['source_state_files']:
                body = (f.root / pin['path']).read_bytes()
                self.assertEqual((len(body), sha(body)), (pin['bytes'], pin['sha256']))

    def test_batch_bridge_refuses_forged_member_or_pending_current_authority(self):
        with acquisition_batch_bridge() as f:
            for mutation in ('selection', 'receipt', 'bootstrap', 'counter', 'sources', 'job', 'descriptor',
                             'duplicate', 'missing', 'extra', 'reuse', 'totals', 'claim'):
                with self.subTest(mutation=mutation):
                    value = copy.deepcopy(f.handoff)
                    e = value['entries'][2]
                    if mutation == 'selection': e['selection']['reports'].reverse()
                    elif mutation == 'receipt': e['metadata_receipt']['sha256'] = '0' * 64
                    elif mutation == 'bootstrap': e['bootstrap_sha256'] = '0' * 64
                    elif mutation == 'counter': e['counters']['attempts'] = 0
                    elif mutation == 'sources': e['sources'][0]['native_file'] = 'forged'
                    elif mutation == 'job': e['job']['canonical_sha256'] = '0' * 64
                    elif mutation == 'descriptor': e['descriptor_sha256'] = '0' * 64
                    elif mutation == 'duplicate': value['entries'][3] = copy.deepcopy(e)
                    elif mutation == 'missing': value['entries'].pop()
                    elif mutation == 'extra': e['extra'] = True
                    elif mutation == 'reuse': value['entries'][0]['reuse_evidence']['manifest_sha256'] = '0' * 64
                    elif mutation == 'totals': value['totals']['attempts'] = 0
                    else: value['claim'] = 'financial admission approved'
                    pin = f.write('data/runs/forged-handoff.json', value)
                    before = self.snapshot(f)
                    with self.assertRaises(ValueError): self.compose(f, value)
                    self.assertEqual(before, self.snapshot(f))
            with self.assertRaises(ValueError): self.compose(f, handoff_sha256='0' * 64)
            with f.opened(f.refs) as authority:
                member = authority.bundle['members'][0]
                with f.acquisition._open_authority(member['job'], member['bootstrap_sha256'],
                        coordinator=f.batch._MemberContext(authority, member)) as single:
                    target = next(t for t in single.targets.values() if t['role'] == 'numeric' and t['area'] == 2)
                    f.acquisition.reserve_attempt(single, target, session_id='pending-fixture')
            before = self.snapshot(f)
            with self.assertRaises(ValueError): self.compose(f)
            self.assertEqual(before, self.snapshot(f))

    def test_batch_bridge_opens_authority_once_for_all_members(self):
        with acquisition_batch_bridge() as f:
            with patch.object(f.batch, '_open_batch', wraps=f.batch._open_batch) as opened, \
                 patch.object(f.batch, '_finished_proofs', wraps=f.batch._finished_proofs) as proofs, \
                 patch.object(f.batch, '_verify_batch', side_effect=AssertionError('Second verifier')):
                self.compose(f)
            self.assertEqual(opened.call_count, 1)
            self.assertEqual(proofs.call_count, 1)
            original_open = f.batch._open_batch
            path = f.root / f.handoff_pin['path']
            body = path.read_bytes()
            @contextmanager
            def changed_between_read_and_claim(*args, **kwargs):
                with original_open(*args, **kwargs) as authority:
                    path.write_bytes(body + b' ')
                    yield authority
            with patch.object(f.batch, '_open_batch', changed_between_read_and_claim):
                with self.assertRaisesRegex(ValueError, 'handoff.*changed'):
                    self.compose(f)
            path.write_bytes(body)
            f.write(f.bundle['destination'] + '/halt.json', {
                'contract': 'financial-acquisition-batch-halt-v1', 'bundle_sha256': f.refs['bundle_sha256'],
                'bootstrap_sha256': f.refs['bootstrap_sha256'], 'reason': 'fixture_halt'})
            before = self.snapshot(f)
            with self.assertRaisesRegex(ValueError, 'halted'): self.compose(f)
            self.assertEqual(before, self.snapshot(f))
            (f.root / f.bundle['destination'] / 'halt.json').unlink()
            evidence = f.handoff['entries'][2]
            final = f.batch._read(evidence['checkpoint_b'])
            original_b = dump(final)
            final['checkpoint_a_sha256'] = '0' * 64
            f.write(evidence['checkpoint_b']['path'], final)
            before = self.snapshot(f)
            with self.assertRaisesRegex(ValueError, 'hash'): self.compose(f)
            self.assertEqual(before, self.snapshot(f))
            f.write(evidence['checkpoint_b']['path'], original_b)
            folder = f.root / f.bundle['destination']
            lines = (folder / 'journal.jsonl').read_bytes().splitlines()[:-1]
            state = f.batch._ledger_state()
            for line in lines:
                record = json.loads(line)
                record.pop('record_sha256')
                f.batch._apply_phase(state, record, f.bundle)
            f.write(f.bundle['destination'] + '/journal.jsonl', b'\n'.join(lines) + b'\n')
            f.write(f.bundle['destination'] + '/head.json', {
                'sequence': len(lines), 'record_sha256': json.loads(lines[-1])['record_sha256'],
                'state_sha256': sha(dump(state))})
            before = self.snapshot(f)
            with self.assertRaisesRegex(ValueError, 'pending'): self.compose(f)
            self.assertEqual(before, self.snapshot(f))


class AcquisitionBridgeTests(unittest.TestCase):
    def compose(self, fixture, value=None):
        self.assertTrue(callable(getattr(profiles, 'compose_acquisition_handoffs', None)),
                        'Offline acquisition handoff composer is absent')
        pin = fixture.write('data/runs/bridge-input.json', value or fixture.input)
        return profiles.compose_acquisition_handoffs(fixture.root / pin['path'], source_entry_sha256=pin['sha256'])

    def snapshot(self, fixture):
        return {p.relative_to(fixture.root).as_posix(): sha(p.read_bytes())
                for p in fixture.root.rglob('*') if p.is_file()}

    def test_native_positive_preserves_sources_counters_and_separate_links(self):
        with acquisition_bridge() as f:
            before = self.snapshot(f)
            result = self.compose(f)
            self.assertEqual(before, self.snapshot(f))
            expected_selection = {'period': 202403, 'perspective': 1005, 'reports': [92, 96, 101, 98]}
            self.assertEqual(result['selection'], expected_selection)
            self.assertEqual(result['trusted_entry'], f.entry)
            self.assertEqual(result['authority']['receipt_sequence'], 9)
            self.assertEqual(result['authority']['sequence'], 10)
            self.assertTrue(result['authority']['receipt_is_historical'])
            self.assertEqual(result['authority']['attempts'], 4)
            a, b = result['metadata_handoff'], result['final_handoff']
            catalog = {k: f.descriptor['catalog'][k] for k in
                       ('manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256')}
            catalog.update(source_id='catalog', role='catalog', area=None, native_file=None, catalog_pointer=None)
            original_a = json.loads((f.root / f.entry['evidence']['checkpoint_a']['path']).read_bytes())
            original_b = json.loads((f.root / f.entry['evidence']['checkpoint_b']['path']).read_bytes())
            self.assertEqual(a['sources'], sorted(original_a['sources'] + [catalog, f.portal], key=lambda s: s['source_id']))
            self.assertEqual(b['sources'], sorted(original_b['sources'] + [catalog, f.portal], key=lambda s: s['source_id']))
            self.assertEqual(b['checkpoint_a_sha256'], sha(dump(a)))
            self.assertNotEqual(b['checkpoint_a_sha256'], original_b['checkpoint_a_sha256'])
            self.assertEqual(result['metadata_handoff_sha256'], sha(dump(a)))
            self.assertEqual(result['final_handoff_sha256'], sha(dump(b)))
            portal_manifest = json.loads((f.root / f.portal['manifest_path']).read_bytes())
            self.assertEqual(portal_manifest['context'], {'purpose': 'official source discovery'})
            self.assertNotIn('period', portal_manifest['context'])
            ap = f.write('data/runs/projected/a.json', a)
            bp = f.write('data/runs/projected/b.json', b)
            candidate = profiles.compile_metadata_candidate(f.root / ap['path'], handoff_sha256=ap['sha256'])
            cp = f.write('data/runs/projected/candidate.json', candidate)
            frozen = profiles.freeze_profile(f.root / cp['path'], f.root / bp['path'],
                                             candidate_sha256=cp['sha256'], final_handoff_sha256=bp['sha256'])
            self.assertEqual(frozen['metadata_handoff_sha256'], result['metadata_handoff_sha256'])
            self.assertEqual(frozen['final_handoff_sha256'], result['final_handoff_sha256'])
            self.assertNotIn('trusted_entry', frozen)
            self.assertNotIn('authority', frozen)
            self.assertIsNone(profiles.descriptor_for_selection(expected_selection).get('profile_path'))

    def test_closed_input_and_anchor_reject_before_helper(self):
        from bank_quality import financial_acquisition as api
        from bank_quality import financial_acquisition_batch as batch
        with acquisition_bridge() as f:
            for mutation in ('contract', 'extra', 'alternative', 'selection'):
                value = copy.deepcopy(f.input)
                if mutation == 'contract': value['contract'] += '-unknown'
                elif mutation == 'extra': value['root'] = str(f.root)
                elif mutation == 'selection': value['entry']['period'] = 202412
                else:
                    # Coherent physical alternative retains valid job and proofs,
                    # but a caller-supplied reference cannot become an anchor.
                    alt = f.write('data/runs/alternative/job.json', f.job)
                    value['entry'].update(manifest_path=alt['path'], manifest_sha256=alt['sha256'])
                with self.subTest(mutation=mutation), patch.object(batch, '_sources403') as helper:
                    with self.assertRaises(ValueError): self.compose(f, value)
                    helper.assert_not_called()
            installed_entry = copy.deepcopy(f.entry)
            with acquisition_bridge(limits={**api._POLICIES, 'max_backoffs': 6}) as alternate:
                # Prove a different job/bootstrap/receipts is internally valid
                # while it still owns its injected fixture authority.
                self.assertEqual(batch._sources403(alternate.entry)['authority']['status'], 'verified')
                self.assertNotEqual(alternate.bootstrap, f.bootstrap)
                batch._TRUSTED_REUSE[202403]['entry'] = installed_entry
                with patch.object(batch, '_sources403') as helper:
                    with self.assertRaisesRegex(ValueError, 'trusted202403'): self.compose(alternate)
                    helper.assert_not_called()

    def test_confined_input_requires_external_physical_pin(self):
        with acquisition_bridge() as f:
            self.compose(f)
            with self.assertRaises(ValueError):
                profiles.compose_acquisition_handoffs(f.root / f.input_pin['path'], source_entry_sha256='0' * 64)
            with tempfile.TemporaryDirectory() as other:
                path = Path(other) / 'external.json'
                path.write_bytes(dump(f.input))
                with self.assertRaises(ValueError):
                    profiles.compose_acquisition_handoffs(path, source_entry_sha256=sha(path.read_bytes()))

    def test_original_and_projected_links_are_independently_checked(self):
        from bank_quality import financial_acquisition_batch as batch
        with acquisition_bridge() as f:
            result = self.compose(f)
            evidence = f.entry['evidence']
            path = f.root / evidence['checkpoint_b']['path']
            original = json.loads(path.read_bytes())
            trusted_entry = copy.deepcopy(f.entry)
            altered = {**original, 'checkpoint_a_sha256': '0' * 64}
            evidence['checkpoint_b'] = f.write(evidence['checkpoint_b']['path'], altered)
            batch._TRUSTED_REUSE[202403]['entry'] = copy.deepcopy(f.entry)
            with self.assertRaisesRegex(ValueError, 'Checkpoint B'): self.compose(f)
            f.write(trusted_entry['evidence']['checkpoint_b']['path'], original)
            f.entry['evidence'] = copy.deepcopy(trusted_entry['evidence'])
            original_a_pin = f.entry['evidence']['checkpoint_a']
            original_a = json.loads((f.root / original_a_pin['path']).read_bytes())
            f.entry['evidence']['checkpoint_a'] = f.write(original_a_pin['path'], {**original_a, 'extra': 'changed'})
            batch._TRUSTED_REUSE[202403]['entry'] = copy.deepcopy(f.entry)
            with self.assertRaisesRegex(ValueError, 'Checkpoint A'): self.compose(f)
            ap = f.write('data/runs/projected/a.json', result['metadata_handoff'])
            candidate = profiles.compile_metadata_candidate(f.root / ap['path'], handoff_sha256=ap['sha256'])
            cp = f.write('data/runs/projected/candidate.json', candidate)
            bad = {**result['final_handoff'], 'checkpoint_a_sha256': evidence['checkpoint_a']['sha256']}
            bp = f.write('data/runs/projected/b.json', bad)
            with self.assertRaisesRegex(ValueError, 'anchored'):
                profiles.freeze_profile(f.root / cp['path'], f.root / bp['path'],
                                        candidate_sha256=cp['sha256'], final_handoff_sha256=bp['sha256'])
            bp = f.write('data/runs/projected/b.json', result['final_handoff'])
            f.write(ap['path'], {**result['metadata_handoff'], 'extra': 'changed physical projected A'})
            with self.assertRaisesRegex(ValueError, 'SHA-256'):
                profiles.freeze_profile(f.root / cp['path'], f.root / bp['path'],
                                        candidate_sha256=cp['sha256'], final_handoff_sha256=bp['sha256'])

    def test_portal_and_installed_origin_guards_remain_native(self):
        with acquisition_bridge() as f:
            self.compose(f)
            path = f.root / f.portal['manifest_path']
            original = path.read_bytes()
            for mutation in ('absent', 'incomplete', 'tamper', 'origin', 'source_pin'):
                with self.subTest(mutation=mutation):
                    if mutation == 'absent':
                        f.registry['legacy_202312_sources'].pop('portal')
                    elif mutation in ('incomplete', 'tamper'):
                        manifest = json.loads(original)
                        if mutation == 'incomplete': manifest['truncated'] = True
                        else: manifest['context'] = {'period': 202403}
                        path.write_bytes(dump(manifest))
                        if mutation == 'incomplete':
                            f.portal.update(manifest_sha256=sha(path.read_bytes()), provenance_sha256=sha(path.read_bytes()))
                    elif mutation == 'origin':
                        f.descriptor['source_offers'][0]['native_file'] += '-changed'
                        f.descriptor.pop('descriptor_sha256', None)
                    else:
                        f.descriptor['catalog']['body_sha256'] = '0' * 64
                        f.descriptor.pop('descriptor_sha256', None)
                    f.install_registry()
                    with self.assertRaises(ValueError): self.compose(f)
                    path.write_bytes(original)
                    f.portal.update(manifest_sha256=sha(original), provenance_sha256=sha(original))
                    f.registry['legacy_202312_sources']['portal'] = f.portal
                    f.descriptor = copy.deepcopy(f.job['descriptors'][0])
                    f.registry['members'] = [f.descriptor]
                    f.install_registry()

    def test_receipt_prefix_pending_failed_forged_ahead_and_reset(self):
        from bank_quality import financial_acquisition as api
        from bank_quality import financial_acquisition_batch as batch
        for mutation in ('pending', 'failure', 'forged', 'ahead', 'reset'):
            with self.subTest(mutation=mutation), acquisition_bridge() as f:
                self.compose(f)
                if mutation in ('pending', 'failure'):
                    # A completed target cannot legally reserve again. Build a
                    # genuinely earlier journal prefix, then use real commits
                    # to leave the last numeric target pending/failed.
                    folder = api._authority_paths(f.job)[0]
                    records = [json.loads(line) for line in (folder / 'journal.jsonl').read_bytes().splitlines()][:6]
                    state = api._initial_state()
                    targets = api._execution_job(f.job)
                    for record in records:
                        api._apply_record(state, record, targets, api._limits(f.job))
                    (folder / 'journal.jsonl').write_bytes(b''.join(dump(r) + b'\n' for r in records))
                    api._replace_head(folder, {'sequence': 6, 'record_sha256': records[-1]['record_sha256'],
                                               'state_sha256': sha(dump(state))})
                    with api.open_authority(f.job, bootstrap_sha256=f.bootstrap) as authority:
                        target = next(t for t in authority.targets.values() if t['source_id'] == 'numeric:3')
                        reservation = api.reserve_attempt(authority, target, session_id='negative')
                        if mutation == 'failure':
                            authority.commit('finish', attempt_id=reservation['attempt_id'], target_key=target['target_key'],
                                             session_id='negative', status='failed', retryable=False,
                                             observed_bytes=0, observed_attempt_seconds=1, tree_extinct=True)
                        f.entry['evidence']['receipt'] = f.write(f.entry['evidence']['receipt']['path'],
                                                               api._receipt(authority, 'negative'))
                    batch._TRUSTED_REUSE[202403]['entry'] = copy.deepcopy(f.entry)
                elif mutation == 'reset':
                    folder = api._authority_paths(f.job)[0]
                    (folder / 'journal.jsonl').write_bytes(b'')
                else:
                    pin = f.entry['evidence']['receipt']
                    receipt = json.loads((f.root / pin['path']).read_bytes())
                    if mutation == 'ahead': receipt['sequence'] = 11
                    else: receipt['state']['body_bytes'] = 0
                    f.entry['evidence']['receipt'] = f.write(pin['path'], receipt)
                    batch._TRUSTED_REUSE[202403]['entry'] = copy.deepcopy(f.entry)
                f.write('data/runs/bridge-input.json', f.input)
                before = self.snapshot(f)
                with self.assertRaises(ValueError): self.compose(f)
                self.assertEqual(before, self.snapshot(f))


class InstalledRegistryTests(unittest.TestCase):
    def test_registry_catalog_hashes_and_all_literal_members(self):
        self.assertIsNotNone(profiles, 'Task1 profile authoring implementation is absent')
        registry = json.loads((profiles.PACKAGE_ROOT / 'financial-reports-registry.json').read_bytes())
        # Validate concrete membership against authenticated catalogs, not a count mirror.
        for member in registry['members']:
            selection = member['selection']
            descriptor = profiles.descriptor_for_selection(selection)
            self.assertEqual(descriptor['selection'], selection)
            for report in member['reports']:
                self.assertIn({'id': 1005}, report['report']['s'])
            if member.get('profile_path') is not None:
                ctx = profiles.load_installed_context(selection)
                self.assertEqual(ctx['selection'], selection)
            else:
                with self.assertRaises(ValueError): profiles.load_installed_context(selection)

    def test_legacy_202312_wrapper_authenticates_without_acquisition(self):
        self.assertIsNotNone(profiles, 'Task1 profile authoring implementation is absent')
        with legacy_bundle() as fixture:
            path = fixture.index_path
            with self.assertRaises(ValueError): profiles.wrap_legacy_202312_index(path, index_sha256='0' * 64)
            handoff = profiles.wrap_legacy_202312_index(path, index_sha256=sha(path.read_bytes()))
            self.assertEqual(handoff['selection']['reports'], [92, 96, 101, 98])
            self.assertEqual(handoff['legacy_index']['selection']['report'], 92)
            self.assertEqual(handoff['legacy_index']['body_sha256'], sha(path.read_bytes()))
            self.assertIn('numeric:1', [s['source_id'] for s in handoff['sources']])
            candidate = fixture.compile(handoff)
            self.assertEqual(len(candidate['reports']), 4)
            self.assertFalse(candidate.get('accepted', False))
            self.assertEqual(candidate['missing_sources'], [])
            for sid in ('dictionary', 'numeric:1'):
                self.assertEqual(candidate['source_members'][sid]['truncation_state'], 'undeclared_legacy')
                self.assertNotIn('truncated', candidate['source_members'][sid]['manifest'])
                self.assertEqual(candidate['source_members'][sid]['manifest']['diagnostics'],
                                 ['synthetic legacy capture: completeness undeclared'])
            final = {**handoff, 'phase': 'complete'}
            cp, ch = fixture.write('data/runs/candidate.json', candidate)
            fp, fh = fixture.write('data/runs/final.json', final)
            artifact = profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)
            self.assertEqual(artifact['contract'], profiles.PROFILE_CONTRACT)
            self.assertEqual(set(artifact['legacy_index']), {'body_sha256', 'selection'})
            self.assertNotIn('metadata_handoff_path', artifact)
            self.assertNotIn(str(fixture.root), dump(artifact).decode())
            # The exception cannot endorse an explicitly fabricated A digest.
            fp, fh = fixture.write('data/runs/forged-link.json', {**final, 'checkpoint_a_sha256': '0' * 64})
            with self.assertRaises(ValueError):
                profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)
            # A fully pinned wrapper is the sole exception to the B checkpoint link.
            fp, fh = fixture.write('data/runs/unanchored.json', {k: v for k, v in final.items() if k != 'legacy_index'})
            with self.assertRaises(ValueError):
                profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)

    def test_legacy_wrapper_rejects_rehashed_cadaster_context_and_forged_checkpoint_bypass(self):
        with legacy_bundle() as fixture:
            handoff = profiles.wrap_legacy_202312_index(fixture.index_path, index_sha256=fixture.index_hash)
            for mutation in ('selection', 'role_path', 'absolute', 'escape'):
                index = copy.deepcopy(fixture.index)
                if mutation == 'selection': index['selection']['report'] = 96
                elif mutation == 'role_path': index['sources']['cadaster'] = index['sources']['dictionary']
                elif mutation == 'absolute': index['sources']['cadaster'] = str(fixture.root / fixture.sources[1]['manifest_path'])
                else: index['sources']['cadaster'] = '../../../../outside.json'
                new_index, digest = fixture.write('data/runs/legacy/mutant-index.json', index)
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    profiles.wrap_legacy_202312_index(new_index, index_sha256=digest)
            for mutation in ('bytes', 'selection', 'flag'):
                forged = copy.deepcopy(handoff)
                if mutation == 'bytes':
                    forged['legacy_index']['body_utf8'] = dump({'selection': handoff['legacy_index']['selection']}).decode()
                    forged['legacy_index']['body_sha256'] = sha(forged['legacy_index']['body_utf8'].encode())
                elif mutation == 'selection': forged['legacy_index']['selection']['report'] = 96
                else: forged['legacy_index'] = {'approved': True}
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    fixture.compile(forged)
            # Mutating the original index after compilation defeats the exemption,
            # even with new externally supplied candidate and final hashes.
            candidate = fixture.compile(handoff)
            cp, ch = fixture.write('data/runs/candidate.json', candidate)
            fp, fh = fixture.write('data/runs/final.json', {**handoff, 'phase': 'complete'})
            fixture.index_path.write_bytes(dump({**fixture.index, 'note': 'changed original bytes'}))
            with self.assertRaises(ValueError):
                profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)

    def test_exact_legacy_pins_reject_rehashed_context_in_private_copy(self):
        with legacy_bundle() as fixture:
            for sid in ('catalog', 'cadaster', 'dictionary', 'portal', 'numeric:1'):
                for mutation in ('context', 'path', 'manifest', 'body', 'provenance', 'diagnostics', 'truncated'):
                    source = copy.deepcopy(fixture.registry['legacy_202312_sources'][sid])
                    path = fixture.root / source['manifest_path']
                    original = path.read_bytes()
                    manifest = json.loads(original)
                    body_path = path.parent / manifest['body_path']
                    original_body = body_path.read_bytes()
                    if mutation == 'path':
                        alternative = path.with_name('alternative-' + path.name)
                        alternative.write_bytes(original)
                        source['manifest_path'] = alternative.relative_to(fixture.root).as_posix()
                    elif mutation == 'provenance': source['provenance_sha256'] = '0' * 64
                    else:
                        if mutation == 'context': manifest['context']['tampered'] = True
                        elif mutation == 'manifest': manifest['retrieved_at_utc'] = '2026-10-04T13:00:00Z'
                        elif mutation == 'diagnostics': manifest['diagnostics'] = ['unreviewed diagnostics']
                        elif mutation == 'truncated': manifest['truncated'] = sid not in ('dictionary', 'numeric:1')
                        else:
                            body_path.write_bytes(original_body + b' ')
                            manifest.update(bytes=len(original_body) + 1, sha256=sha(body_path.read_bytes()))
                            source['body_sha256'] = manifest['sha256']
                        path.write_bytes(dump(manifest))
                        source['manifest_sha256'] = source['provenance_sha256'] = sha(dump(manifest))
                    try:
                        # Exact reviewed pins reject coherent new physical hashes.
                        with self.subTest(sid=sid, mutation=mutation), self.assertRaises(ValueError):
                            profiles._authenticate_source(source, fixture.descriptor)
                        if mutation not in ('path', 'provenance'):
                            with self.subTest(wrapper_sid=sid, mutation=mutation), self.assertRaises(ValueError):
                                profiles.wrap_legacy_202312_index(fixture.index_path, index_sha256=fixture.index_hash)
                    finally:
                        path.write_bytes(original)
                        body_path.write_bytes(original_body)


if __name__ == '__main__':
    unittest.main()

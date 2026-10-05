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
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pkg = self.root / 'bank_quality'
        self.pkg.mkdir()
        self.addCleanup(patch.stopall)
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
            self.prepare(24)
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

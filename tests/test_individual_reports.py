"""Synthetic behavior tests for the closed individual admission boundary."""
import copy
from contextlib import contextmanager
import csv
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_financial_reports as fixtures
from test_financial_reports import canonical, sha
from bank_quality import financial_reports as reports
from bank_quality import financial_report_profiles as profiles
from tests.test_individual_report_profiles import historical_fixture, encoded

SELECTION = {'period': 202412, 'perspective': 1006, 'reports': [93, 77, 100, 94]}


@contextmanager
def historical_admission_fixture(period, *, wide=False):
    """Install a synthetic package and archives; use real loaders/authentication.

    E's fixture supplies native public trees and finite independent capture
    policies. Only filesystem roots are redirected after installing metadata.
    """
    registry_reader = profiles._individual_registry
    selection = next(m['selection'] for m in registry_reader()['members'] if m['selection']['period'] == period)
    installed = profiles.load_individual_context(selection)['profile']
    with historical_fixture(period) as (root, member):
        def replace_body(sid, value):
            source = member['sources'][sid]
            path = root / source['manifest_path']
            manifest = json.loads(path.read_bytes())
            body = encoded(value)
            (path.parent / manifest['body_path']).write_bytes(body)
            manifest.update(bytes=len(body), sha256=sha(body))
            manifest['response_headers']['Content-Length'] = str(len(body))
            raw = encoded(manifest)
            path.write_bytes(raw)
            source.update(manifest_sha256=sha(raw), body_sha256=sha(body),
                          provenance_sha256=profiles._digest(manifest))
            member['source_policy'][sid]['bytes'] = len(body)

        source = member['sources']['cadaster']
        path = root / source['manifest_path']
        cadaster = json.loads((path.parent / json.loads(path.read_bytes())['body_path']).read_bytes())
        # Quantity bindings are numeric cadastro values, never padded columns.
        for report in installed['reports']:
            for node in report['nodes']:
                if node['kind'] == 'quantity':
                    for row in cadaster: row[f'c{node["lid"]}'] = '7'
        replace_body('cadaster', cadaster)
        if wide:
            source = member['sources']['numeric:1']
            path = root / source['manifest_path']
            numeric = json.loads((path.parent / json.loads(path.read_bytes())['body_path']).read_bytes())
            numeric['values'][0]['v'][0]['v'] = '123456789012345678901234567890123456789.0100'
            replace_body('numeric:1', numeric)
        profile = profiles.author_individual_profile(member['selection'])
        package = root / 'package'
        profile_path = package / member['profile_path']
        profile_path.parent.mkdir(parents=True)
        for name in ('individual-reports-profile-202412.json', 'financial-reports-profile-202412.json',
                     'financial-reports-registry.json'):
            (package / name).write_bytes((profiles.PACKAGE_ROOT / name).read_bytes())
        body = encoded(profile)
        profile_path.write_bytes(body)
        member['profile_sha256'] = sha(body)
        (package / 'individual-reports-registry.json').write_bytes(encoded({
            'contract': 'ifdata-individual-reports-registry-v1', 'members': [member]}))
        index = root / 'index.json'
        index.write_bytes(encoded({'contract': reports.INDIVIDUAL_INDEX_CONTRACT,
            'selection': member['selection'], 'sources': list(member['sources'].values())}))
        with patch.object(profiles, '_individual_registry', registry_reader), patch.object(profiles, 'PACKAGE_ROOT', package):
            yield root, member, index


class IndividualHistoricalAdmissionTests(unittest.TestCase):
    def test_both_epochs_admit_native_width_all_bindings_and_replay(self):
        # Missing selection propagation must reject these genuine historical archives.
        for period, width in ((201012, 28), (202312, 32)):
            with self.subTest(period=period), historical_admission_fixture(period) as (root, member, index):
                output = root / 'admission'
                try:
                    manifest = reports.admit_individual(index, output, index_sha256=sha(index.read_bytes()))
                except FileNotFoundError as exc:
                    self.fail('Historical selection incorrectly requests default 202412 archives: ' + str(exc))
                except ValueError as exc:
                    self.fail('Historical admission rejected its own installed projection: ' + str(exc))
                payload = {entry['path']: (output / entry['path']).read_bytes() for entry in manifest['files']}
                validated = reports.validate_individual_admission(manifest, payload)
                self.assertEqual(manifest['contract'], 'ifdata-individual-reports-historical-snapshot-v1')
                self.assertEqual(manifest['selection'], member['selection'])
                self.assertEqual(manifest['selection']['reports'], [76,77,78,79] if period == 201012 else [93,77,100,94])
                self.assertGreater(len([s for s in member['source_offers'] if s['role'] == 'numeric']), 1)
                self.assertEqual(sorted(s for s in manifest['sources'] if s.startswith('numeric:')), ['numeric:1'])
                self.assertEqual(len([k for k in validated['cadastro'][0] if k.startswith('c') and k[1:].isdigit()]), width)
                self.assertNotIn(f'c{width}', validated['cadastro'][0])
                self.assertEqual(manifest['cells'], 2 * len(validated['variables']['variables']))
                self.assertTrue(any(r['presence'] == 'entity_not_stored' for r in validated['cells']))
                self.assertIn('123.4500', [r['raw_value'] for r in validated['cells']])
                replay = reports.admit_individual(index, root / 'replay', index_sha256=sha(index.read_bytes()))
                self.assertEqual(manifest['files'], replay['files'])
                if period == 202312:
                    for sid in ('cadaster', 'dictionary', 'numeric:1'):
                        source = manifest['sources'][sid]
                        self.assertNotIn('truncated', source)
                        self.assertEqual(source['diagnostics'], member['source_policy'][sid]['diagnostics'])
                        self.assertIn('truncation undeclared', source['completion_evidence'])
                        self.assertNotIn('truncated=false', source['completion_evidence'])

    def test_changed_physical_archives_fail_before_destination_creation(self):
        for period in (201012, 202312):
            with self.subTest(period=period), historical_admission_fixture(period) as (root, member, index):
                path = root / member['sources']['cadaster']['manifest_path']
                manifest_body = path.read_bytes()
                body_path = path.parent / json.loads(manifest_body)['body_path']
                body = body_path.read_bytes()
                for change in ('manifest', 'body'):
                    with self.subTest(change=change):
                        if change == 'manifest': path.write_bytes(manifest_body + b' ')
                        else: body_path.write_bytes(body.replace(b'synthetic', b'forged', 1))
                        with self.assertRaises(ValueError):
                            reports.admit_individual(index, root / 'rejected', index_sha256=sha(index.read_bytes()))
                        self.assertFalse((root / 'rejected').exists())
                        path.write_bytes(manifest_body); body_path.write_bytes(body)

    def test_repin_index_cannot_rebind_selection_or_sources(self):
        for period in (201012, 202312):
            with self.subTest(period=period), historical_admission_fixture(period) as (root, member, index):
                original = json.loads(index.read_bytes())
                for change in ('financial', 'other_epoch', 'reordered', 'missing', 'body_pin', 'role'):
                    with self.subTest(change=change):
                        mutated = copy.deepcopy(original)
                        if change == 'financial': mutated['selection']['perspective'] = 1005
                        elif change == 'other_epoch': mutated['selection']['period'] = 201003
                        elif change == 'reordered': mutated['selection']['reports'].reverse()
                        elif change == 'missing': mutated['sources'] = [s for s in mutated['sources'] if s['source_id'] != 'numeric:1']
                        elif change == 'body_pin': mutated['sources'][0]['body_sha256'] = '0' * 64
                        else: mutated['sources'][0]['role'] = 'numeric'
                        index.write_bytes(encoded(mutated))
                        with self.assertRaises(ValueError):
                            reports.admit_individual(index, root / 'rejected', index_sha256=sha(index.read_bytes()))
                        self.assertFalse((root / 'rejected').exists())

    def test_repin_decoded_capture_cannot_promote_unknown_completion(self):
        with historical_admission_fixture(202312) as (root, member, index):
            source = member['sources']['cadaster']
            path = root / source['manifest_path']
            manifest = json.loads(path.read_bytes())
            manifest.update(truncated=False, diagnostics=[])
            path.write_bytes(encoded(manifest))
            original = json.loads(index.read_bytes())
            candidate = next(s for s in original['sources'] if s['source_id'] == 'cadaster')
            candidate.update(manifest_sha256=sha(path.read_bytes()), provenance_sha256=profiles._digest(manifest))
            index.write_bytes(encoded(original))
            with self.assertRaises(ValueError):
                reports.admit_individual(index, root / 'rejected', index_sha256=sha(index.read_bytes()))
            self.assertFalse((root / 'rejected').exists())


class IndividualReportsTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.FinancialReportsTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.output = self.root / 'individual'
        profile = copy.deepcopy(self.fixture.profile)
        envelope = {'contract': 'ifdata-individual-reports-snapshot-202412-v1',
                    'period': 202412, 'perspective': 'individual', 'perspective_id': 1006}
        self.members, self.records, self.descriptors, self.bodies = {}, {}, {}, {}
        for role, value in self.fixture.data.items():
            sid = 'numeric:1' if role == 'numeric' else role
            descriptor = {'source_id': sid, 'role': role, 'area': 1 if role == 'numeric' else None,
                          'manifest_path': role + '.manifest.json'}
            self.descriptors[sid] = descriptor
            manifest = json.loads((self.root / descriptor['manifest_path']).read_bytes())
            manifest['retrieved_at_utc'] = '2026-10-01T01:00:00-03:00'
            record = {**descriptor, 'native_file': role, 'catalog_pointer': None,
                      'manifest_sha256': 'fixture-manifest-pin', 'body_sha256': manifest['sha256'],
                      'provenance_sha256': 'fixture-provenance-pin', 'body_path': manifest['body_path'],
                      'source_generation_state': 'unknown', 'truncation_state': 'reported_false', 'manifest': manifest}
            self.records[sid] = record
            projected = profiles._project_source_record(record)
            projected.update(retrieved_at_original=manifest['retrieved_at_utc'],
                             retrieved_at_utc_derived='2026-10-01T04:00:00+00:00',
                             completion_evidence='Exact legacy GET/200; truncated=false; empty diagnostics; physical/manifest/Content-Length agree; Content-Encoding absent; EOF unobserved')
            self.members[sid] = projected
            self.bodies[sid] = (self.root / (role + '.bin')).read_bytes()
        for item, rid in zip(profile['reports'], SELECTION['reports']):
            item['report']['id'] = rid
            item['report']['s'] = [{'id': 1006}]
            for node in item['nodes']:
                node['report_id'] = rid
                node['origin_source_id'] = 'numeric:1' if node['kind'] == 'money' else 'cadaster'
                node['origin_kind'] = 'numeric' if node['kind'] == 'money' else 'cadaster'
                if node['kind'] == 'money': node['kind'] = 'numeric'
        catalog = copy.deepcopy(self.fixture.data['catalog'])
        for entry, item in zip(catalog[0]['files'][4:], profile['reports']): entry['trel'] = item['report']
        self.bodies['catalog'] = json.dumps(catalog).encode()
        profile.update(selection=copy.deepcopy(SELECTION), source_members=self.members,
                       source_pins={sid: {'projection_sha256': sha(canonical(record).encode())} for sid, record in self.members.items()})
        self.context = {'period': 202412, 'contract': envelope['contract'], 'envelope': envelope,
                        'selection': copy.deepcopy(SELECTION), 'profile': profile, 'profile_sha256': 'fixture-profile-pin',
                        'source_members': self.members, 'cadaster_columns': [f'c{i}' for i in range(38)],
                        'cad_csv_fields': [*envelope, *(f'c{i}' for i in range(38)), 'source_body', 'source_sha256', 'source_pointer'],
                        'limitations': ['Individual fixture; no equivalence.']}
        self.index = self.root / 'individual-index.json'
        self.index.write_text(json.dumps({'contract': 'ifdata-individual-reports-sources-v1',
                                         'selection': SELECTION, 'sources': list(self.descriptors.values())}))
        self.stack = __import__('contextlib').ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(profiles, 'load_individual_context', side_effect=self.load_context))
        self.stack.enter_context(patch.object(profiles, '_individual_sources', side_effect=lambda selection=None: copy.deepcopy(self.descriptors)))
        self.stack.enter_context(patch.object(profiles, '_authenticate_individual_source', side_effect=self.authenticate))

    def load_context(self, selection=None):
        if selection is not None and selection != SELECTION: raise ValueError('Noncanonical individual selection')
        return copy.deepcopy(self.context)

    def authenticate(self, source, selection=None):
        self.load_context(selection)
        sid = source['source_id']
        if source != self.descriptors[sid]: raise ValueError('Changed fixture source')
        return self.bodies[sid], copy.deepcopy(self.records[sid])

    def admit(self, output=None):
        return reports.admit_individual(self.index, output or self.output, index_sha256=sha(self.index.read_bytes()))

    def payload(self, manifest):
        return {entry['path']: (self.output / entry['path']).read_bytes() for entry in manifest['files']}

    def test_explicit_individual_api_has_own_names_roster_and_exact_grade(self):
        self.assertTrue(callable(getattr(reports, 'admit_individual', None)), 'Individual admission API missing')
        manifest = self.admit()
        self.assertEqual(manifest['perspective_id'], 1006)
        self.assertEqual(manifest['selection'], SELECTION)
        self.assertEqual(manifest['cells'], 84)
        self.assertEqual(manifest['observations'], 64)
        self.assertTrue(all(e['path'].startswith('individual-') for e in manifest['files']))
        accepted = reports.validate_individual_admission(manifest, self.payload(manifest))
        self.assertEqual([row['c0'] for row in accepted['cadastro']], ['111', '222', '333', '00111'])
        cells = accepted['cells']
        first = next(row for row in cells if row['report_id'] == '93' and row['ifd'] == '20' and row['institution_id'] == '111')
        self.assertEqual(first['raw_value'], '9007199254740993.0100')
        self.assertEqual(first['numeric_value'], first['raw_value'])
        self.assertEqual(first['source_pointer'], '/values/0/v/0/v')
        self.assertEqual(cells[0]['source_pointer'], '/0/c0')
        self.assertTrue(any(row['institution_id'] == '00111' and row['presence'] == 'entity_not_stored' for row in cells))
        self.assertTrue(any(row['presence'] == 'information_not_stored' for row in cells))
        self.assertEqual(len(accepted['variables']['nodes']), 24)
        self.assertEqual(sum(n['kind'] == 'group' for n in accepted['variables']['nodes']), 3)
        self.assertEqual(accepted['variables']['nodes'], reports._variables(self.context)['nodes'])

    def test_markers_empty_null_zero_and_number_lexeme_remain_distinct(self):
        for i, (token, state, kind) in enumerate([('"NA"', 'NA', 'json_string'), ('"NI"', 'NI', 'json_string'),
                ('null', 'json_null', 'json_null'), ('"null"', 'literal_null', 'json_string'),
                ('""', 'empty', 'json_string'), ('-0.00', 'zero', 'json_number'), ('1e-27', 'numeric', 'json_number')]):
            with self.subTest(token=token):
                self.bodies['numeric:1'] = ('{"id":1,"values":[{"e":111,"v":[{"i":700,"v":' + token + '}]}]}').encode()
                output = self.root / ('marker-' + str(i))
                manifest = self.admit(output)
                rows = list(csv.DictReader(io.StringIO((output / 'individual-cells.csv').read_text())))
                row = next(r for r in rows if r['report_id'] == '93' and r['ifd'] == '20' and r['institution_id'] == '111')
                self.assertEqual((row['value_state'], row['source_kind']), (state, kind))
                if token == '1e-27': self.assertEqual(row['numeric_value'], '1E-27')
        self.bodies['numeric:1'] = b'{"id":1,"values":[{"e":111,"v":[{"i":700,"v":"invalid"}]}]}'
        with self.assertRaises(ValueError): self.admit()

    def test_external_hash_and_cross_contract_scope_reject_before_writing(self):
        with self.assertRaises(ValueError): reports.admit_individual(self.index, self.output, index_sha256='0'*64)
        original = json.loads(self.index.read_bytes())
        for mutation in ('financial', 'perspective', 'reports', 'override', 'source', 'duplicate'):
            with self.subTest(mutation=mutation):
                index = copy.deepcopy(original)
                if mutation == 'financial': index['contract'] = reports.INDEX_CONTRACT
                elif mutation == 'perspective': index['selection']['perspective'] = 1005
                elif mutation == 'reports': index['selection']['reports'].reverse()
                elif mutation == 'override': index['root'] = str(self.root)
                elif mutation == 'source': index['sources'][0]['manifest_path'] = '../other.json'
                else: index['sources'].append(index['sources'][0])
                self.index.write_text(json.dumps(index))
                with self.assertRaises(ValueError): self.admit()
        self.index.write_text(json.dumps(original))
        with self.assertRaises(ValueError): reports.admit(self.index, self.output)
        self.assertFalse(self.output.exists())

    def test_projection_extras_and_digest_authenticate_independently(self):
        for field in ('retrieved_at_original', 'retrieved_at_utc_derived', 'completion_evidence', 'context'):
            with self.subTest(field=field):
                context = copy.deepcopy(self.context)
                self.context['source_members']['dictionary'][field] = 'changed'
                with self.assertRaises(ValueError): self.admit()
                self.context = context
        self.context['profile']['source_pins']['dictionary']['projection_sha256'] = '0'*64
        with self.assertRaises(ValueError): self.admit()
        self.assertFalse(self.output.exists())

    def test_reconstruction_rejects_financial_manifest_and_tampered_payload(self):
        manifest = self.admit()
        bodies = self.payload(manifest)
        self.assertEqual(len(reports.validate_individual_admission(manifest, bodies)['cells']), 84)
        with self.assertRaises(ValueError): reports.validate_admission(manifest, bodies)
        altered = copy.deepcopy(manifest); altered['contract'] = reports.CONTRACT
        with self.assertRaises(ValueError): reports.validate_individual_admission(altered, bodies)
        altered = copy.deepcopy(manifest); altered['sources']['dictionary']['completion_evidence'] = 'bounded'
        with self.assertRaises(ValueError): reports.validate_individual_admission(altered, bodies)
        changed = dict(bodies); changed['individual-cells.csv'] = changed['individual-cells.csv'].replace(b'9007199254740993.0100', b'9007199254740993.0200', 1)
        with self.assertRaises(ValueError): reports.validate_individual_admission(manifest, changed)

    def test_replay_is_byte_identical_and_existing_destination_is_preserved(self):
        first = self.admit()
        second = self.admit(self.root / 'replay')
        self.assertEqual(first['files'], second['files'])
        with self.assertRaises(FileExistsError): self.admit()

    def test_native_roster_schema_opaque_identity_and_reference_reject_mutants(self):
        original = self.bodies['cadaster']
        for mutation in ('width', 'number', 'duplicate', 'reference', 'empty'):
            with self.subTest(mutation=mutation):
                cadaster = json.loads(original)
                if mutation == 'width': del cadaster[0]['c37']
                elif mutation == 'number': cadaster[0]['c0'] = 111
                elif mutation == 'duplicate': cadaster[1]['c0'] = cadaster[0]['c0']
                elif mutation == 'reference': cadaster[0]['c1'] = '202503'
                else: cadaster[0]['c0'] = ''
                self.bodies['cadaster'] = json.dumps(cadaster).encode()
                with self.assertRaises(ValueError): self.admit()
                self.assertFalse(self.output.exists())
        self.bodies['cadaster'] = original

    def test_duplicate_numeric_keys_and_changed_definition_or_tree_reject(self):
        original = copy.deepcopy(self.bodies)
        mutations = [
            ('numeric:1', b'{"id":1,"values":[{"e":111,"v":[]},{"e":111,"v":[]}]}'),
            ('numeric:1', b'{"id":1,"values":[{"e":111,"v":[{"i":700,"v":1},{"i":700,"v":2}]}]}'),
            ('numeric:1', b'{"id":1,"values":[{"e":"111","v":[]}]}'),
            ('numeric:1', b'{"id":2,"values":[]}'),
            ('dictionary', original['dictionary'].replace(b'"Opaque"', b'"Changed"', 1)),
            ('catalog', original['catalog'].replace(b'"opaque();"', b'"execute();"', 1))]
        for sid, body in mutations:
            with self.subTest(sid=sid, body=body[:100]):
                self.bodies = copy.deepcopy(original)
                self.bodies[sid] = body
                with self.assertRaises(ValueError): self.admit()
                self.assertFalse(self.output.exists())

    def test_interrupted_writer_retains_unaccepted_diagnostics_only(self):
        write = reports.legacy._write_json
        def interrupt(path, value):
            if path.name == '.manifest.pending': raise OSError('Synthetic interruption')
            return write(path, value)
        with patch.object(reports.legacy, '_write_json', side_effect=interrupt):
            with self.assertRaises(OSError): self.admit()
        self.assertTrue((self.output / 'individual-cells.csv').exists())
        self.assertFalse((self.output / 'manifest.json').exists())

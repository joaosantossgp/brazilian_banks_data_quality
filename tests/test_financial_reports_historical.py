"""Native historical admission with authenticated small synthetic sources."""
import copy
import csv
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from bank_quality import financial, financial_reports as reports
from bank_quality import financial_report_profiles as profiles
from tests import test_financial_report_profiles as authoring


class HistoricalTests(unittest.TestCase):
    def setUp(self):
        self.fixture = authoring.ProfileTests('test_candidate_missing_numeric_sources_cannot_be_frozen')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root

    def install(self, width=24, equal=False, quantity=False):
        f = self.fixture
        f.prepare(width)
        if quantity:
            for item in f.reports:
                item['report']['c'][0]['fid'] = 2
            catalog = f.archive('catalog', authoring.dump(f.catalog_value).replace(b'{"json_number":"1e-27"}', b'1e-27'))
            f.descriptor['catalog'] = {**catalog, 'reference_pointer': '/0'}
            f.install_registry()
            f.handoff.update(catalog=f.descriptor['catalog'],
                             descriptor_sha256=profiles.descriptor_for_selection(f.selection)['descriptor_sha256'])
            f.handoff['sources'][0] = catalog
        cad = [{f'c{i}': str(f.selection['period']) if i == 1 else 'opaque' + str(i)
                for i in range(width)} for _ in range(3)]
        for row, code in zip(cad, ('1', '2', '001')):
            row['c0'] = code
            row['c2'] = '9.00' if quantity else '0009'
        offer = f.descriptor['source_offers'][0]
        f.handoff['sources'][1] = {**f.archive('cadaster', cad, offer['native_file']), **offer}
        candidate = f.compile()
        cp, ch = f.write('data/runs/candidate.json', candidate)
        final = copy.deepcopy(f.handoff)
        final.update(phase='complete', checkpoint_a_sha256=authoring.sha(authoring.dump(f.handoff)))
        final['sources'].append(f.archive('portal', b'opaque formatter'))
        for offer in f.descriptor['source_offers'][2:]:
            area = offer['area']
            body = (b'{"id":1,"values":[{"e":1,"v":[{"i":7,"v":1e-27}]},{"e":2,"v":[]}]}'
                    if area == 1 else
                    b'{"id":3,"values":[{"e":1,"v":[{"i":7,"v":1e-27}]}]}' if equal else
                    b'{"id":3,"values":[{"e":1,"v":[{"i":7,"v":"2.00"}]}]}')
            final['sources'].append({**f.archive(offer['source_id'], body, offer['native_file'], area), **offer})
        fp, fh = f.write('data/runs/final.json', final)
        artifact = profiles.freeze_profile(cp, fp, candidate_sha256=ch, final_handoff_sha256=fh)
        self.artifact, self.final = artifact, final
        self.profile_path = f.pkg / 'financial-reports-profiles/201403.json'
        self.profile_path.parent.mkdir(exist_ok=True)
        self.save_profile()
        self.index, self.digest = fp, fh
        return artifact

    def save_profile(self):
        f = self.fixture
        self.profile_path.write_bytes(authoring.dump(self.artifact))
        f.descriptor.update(profile_path='financial-reports-profiles/201403.json',
                            profile_sha256=authoring.sha(self.profile_path.read_bytes()))
        f.install_registry()

    def admit(self, name='accepted'):
        output = self.root / name
        manifest = financial.admit(self.index, output)
        bodies = {name: (output / name).read_bytes() for name in reports.INPUTS}
        return manifest, bodies, reports.validate_admission(manifest, bodies)

    def mutated_cells(self, manifest, bodies, edit):
        manifest, bodies = copy.deepcopy(manifest), dict(bodies)
        rows = list(csv.DictReader(io.StringIO(bodies['financial-cells.csv'].decode('utf-8-sig'))))
        edit(rows)
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=reports.FIELDS)
        writer.writeheader()
        writer.writerows(rows)
        body = stream.getvalue().encode('utf-8-sig')
        bodies['financial-cells.csv'] = body
        record = next(r for r in manifest['files'] if r['path'] == 'financial-cells.csv')
        record.update(bytes=len(body), sha256=authoring.sha(body))
        return manifest, bodies

    def test_historical_native_grade_keeps_variable_cadaster_and_exact_membership(self):
        for width in (24, 32, 38):
            with self.subTest(width=width):
                self.install(width)
                manifest, bodies, result = self.admit('accepted' + str(width))
                self.assertEqual(manifest['contract'], 'ifdata-financial-reports-historical-snapshot-v1')
                self.assertEqual((manifest['cells'], manifest['observations'], manifest['cadaster_records']), (36, 20, 3))
                self.assertEqual(len(reports.FIELDS), 32)
                header = next(csv.reader(io.StringIO(bodies['financial-cadastro.csv'].decode('utf-8-sig'))))
                self.assertEqual(header[4:-3], [f'c{i}' for i in range(width)])
                self.assertEqual([r['c0'] for r in result['cadastro']], ['1', '2', '001'])
                self.assertEqual(result['variables']['reports'][0]['report']['s'], [{'id': 1004}, {'id': 1005}])
                self.assertEqual(result['variables']['reports'][0]['report']['ratio'], {'json_number': '1e-27'})
                for mutation in ('missing', 'extra', 'period', 'duplicate'):
                    rows = [{k: v for k, v in row.items() if k.startswith('c') and k[1:].isdigit()}
                            for row in result['cadastro']]
                    if mutation == 'missing': rows[0].pop('c2')
                    elif mutation == 'extra': rows[0]['c999'] = ''
                    elif mutation == 'period': rows[0]['c1'] = '201403.0'
                    else: rows[1]['c0'] = rows[0]['c0']
                    with self.assertRaises(ValueError): reports._cadaster(rows, result['context'])

    def test_multishard_identity_and_absence_are_scoped(self):
        self.install()
        manifest, bodies, result = self.admit()
        rows = result['cells'][:9]
        self.assertEqual([r['presence'] for r in rows], ['stored'] * 4 + ['information_not_stored', 'entity_not_stored',
                                                                   'stored', 'entity_not_stored', 'entity_not_stored'])
        self.assertEqual((rows[3]['raw_value'], rows[3]['numeric_value']), ('1e-27', '1E-27'))
        self.assertEqual((rows[6]['raw_value'], rows[6]['numeric_value']), ('2.00', '2.00'))
        for field, value in (('raw_value', '3'), ('source_pointer', '/values/9/v/0/v')):
            bad, payloads = self.mutated_cells(manifest, bodies, lambda rows: rows[12].update({field: value}))
            with self.assertRaises(ValueError): reports.validate_admission(bad, payloads)

    def test_origin_mapping_rejects_cross_shard_swaps(self):
        self.install(equal=True)
        manifest, bodies, result = self.admit()
        rows = result['cells']
        self.assertEqual(rows[3]['raw_value'], rows[6]['raw_value'])
        self.assertEqual(rows[3]['source_pointer'], rows[6]['source_pointer'])
        for field in ('area', 'source_role', 'source_body', 'source_sha256'):
            value = rows[6][field] if field != 'source_role' else 'cadaster'
            bad, payloads = self.mutated_cells(manifest, bodies, lambda rows: rows[3].update({field: value}))
            with self.subTest(field=field), self.assertRaises(ValueError): reports.validate_admission(bad, payloads)
        for mutation in ('map', 'binding'):
            original = copy.deepcopy(self.artifact)
            if mutation == 'map': self.artifact['source_members']['numeric:3']['area'] = 1
            else: self.artifact['reports'][0]['nodes'][2]['origin_source_id'] = 'numeric:3'
            self.save_profile()
            with self.assertRaises(ValueError): profiles.load_installed_context(self.fixture.selection)
            self.artifact = original
            self.save_profile()

    def test_physical_source_is_required_but_unknown_semantics_is_preserved(self):
        self.install()
        manifest, bodies, result = self.admit()
        node = result['variables']['variables'][1]
        self.assertEqual((node['origin_kind'], node['kind'], node['unit'], node['window_end']), ('numeric', 'numeric', 'unknown', ''))
        self.assertEqual(node['unit_basis'], 'unknown: no binding-specific evidence')
        self.assertEqual(len(result['variables']['nodes']), 16)
        self.assertEqual(len(result['variables']['variables']), 12)
        self.assertEqual(result['cells'][0]['value_state'], 'text')
        self.assertEqual((result['cells'][0]['raw_value'], result['cells'][0]['numeric_value']), ('0009', ''))
        source = self.final['sources'][-1]
        (self.root / source['manifest_path']).unlink()
        with self.assertRaises((ValueError, FileNotFoundError)): self.admit('missing')
        self.assertFalse((self.root / 'missing').exists())

    def test_quantity_uses_cadaster_decimal_without_money_inference(self):
        self.install(quantity=True)
        _, _, result = self.admit()
        row = result['cells'][0]
        self.assertEqual((row['source_role'], row['raw_value'], row['numeric_value'], row['unit']),
                         ('cadaster', '9.00', '9.00', 'unknown'))
        self.assertEqual(result['variables']['variables'][0]['kind'], 'quantity')

    def test_replay_and_alternating_legacy_profiles_preserve_defaults(self):
        from tests.test_financial_reports import FinancialReportsTests
        from tests.test_financial_reports_202503 import Fixture202503
        from tests.test_financial import FinancialTests
        from tests.test_financial_202312 import Financial202312Tests
        self.install()
        report24, summary24, summary23 = FinancialReportsTests(), FinancialTests(), Financial202312Tests()
        for fixture in (report24, summary24, summary23):
            fixture.setUp()
            self.addCleanup(fixture.doCleanups)
        root25 = self.root / 'fixture25'
        root25.mkdir()
        report25 = Fixture202503(root25)
        constants = copy.deepcopy((reports.CONTRACT, reports.SELECTION, reports.ENVELOPE,
                                    reports.LIMITATIONS, financial.CONTRACT, financial.SELECTION))
        with patch.object(reports, 'PROFILE_PATH', report24.profile_path), \
                patch.object(reports, 'PROFILE_202503_PATH', report25.profile_path), \
                patch.object(financial, 'PROFILE_PATH', summary24.profile_path):
            first = None
            sequence = [(report24.index, report24.root), (self.index, self.root),
                        (report25.index, report25.root), (report24.index, report24.root),
                        (summary23.index, summary23.root), (summary24.index, summary24.root),
                        (self.index, self.root)]
            expected = ['ifdata-financial-reports-snapshot-202412-v1',
                        'ifdata-financial-reports-historical-snapshot-v1',
                        'ifdata-financial-reports-snapshot-202503-v1',
                        'ifdata-financial-reports-snapshot-202412-v1',
                        'ifdata-financial-snapshot-202312-v1', 'ifdata-financial-snapshot-202412-v1',
                        'ifdata-financial-reports-historical-snapshot-v1']
            for pos, ((index, root), contract) in enumerate(zip(sequence, expected)):
                output = root / ('alternate-' + str(pos))
                manifest = financial.admit(index, output)
                self.assertEqual(manifest['contract'], contract)
                if index == self.index:
                    payloads = {name: (output / name).read_bytes() for name in reports.INPUTS}
                    reports.validate_admission(manifest, payloads)
                    if first is None: first = payloads
                    else: self.assertEqual(payloads, first)
            self.assertEqual(reports._context()['selection'],
                             {'period': 202412, 'perspective': 1005, 'reports': [92, 96, 101, 98]})
            self.assertEqual(financial._profile_for_selection(financial.SELECTION)['period'], 202412)
        self.assertEqual((reports.CONTRACT, reports.SELECTION, reports.ENVELOPE, reports.LIMITATIONS,
                          financial.CONTRACT, financial.SELECTION), constants)

    def test_source_guards_are_closed_and_hash_is_external(self):
        self.install()
        original = self.index.read_bytes()
        self.index.write_bytes(original + b' ')
        with self.assertRaises(ValueError): financial.admit(self.index, self.root / 'wrong')
        self.index.write_bytes(original)
        for mutation in ('phase', 'subset', 'extra', 'role', 'path', 'pin', 'override'):
            value = copy.deepcopy(self.final)
            if mutation == 'phase': value['phase'] = 'metadata'
            elif mutation == 'subset': value['sources'].pop()
            elif mutation == 'extra': value['sources'].append(value['sources'][-1])
            elif mutation == 'role': value['sources'][-1]['role'] = 'cadaster'
            elif mutation == 'path': value['sources'][-1]['manifest_path'] = '../outside.json'
            elif mutation == 'pin': value['sources'][-1]['manifest_sha256'] = '0' * 64
            else: value['profile_path'] = 'injected.json'
            path, digest = self.fixture.write('data/runs/mutant.json', value)
            self.artifact['final_handoff_sha256'] = digest
            self.save_profile()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                financial.admit(path, self.root / ('bad-' + mutation))

    def test_coherent_transport_mutations_reach_original_source_guards(self):
        for mutation in ('url', 'final_url', 'utc', 'framing', 'context', 'truncated', 'body', 'provenance'):
            self.install()
            source = self.final['sources'][-1]
            path = self.root / source['manifest_path']
            manifest = json.loads(path.read_bytes())
            if mutation in ('url', 'final_url'): manifest[mutation] += '&redirect=1'
            elif mutation == 'utc': manifest['retrieved_at_utc'] = '2026-10-04T12:00:00-03:00'
            elif mutation == 'framing': manifest['response_headers']['Content-Length'] = '1'
            elif mutation == 'context': manifest['context'] = None
            elif mutation == 'truncated': manifest['truncated'] = True
            elif mutation == 'body': (path.parent / manifest['body_path']).write_bytes(b'changed')
            else: source['provenance_sha256'] = '0' * 64
            if mutation != 'body':
                path.write_bytes(authoring.dump(manifest))
                source['manifest_sha256'] = authoring.sha(path.read_bytes())
                if mutation != 'provenance': source['provenance_sha256'] = source['manifest_sha256']
                projected = self.artifact['source_members']['numeric:3']
                for key in ('url', 'final_url', 'retrieved_at_utc', 'context', 'truncated'):
                    projected[key] = manifest[key]
                for key in ('manifest_sha256', 'provenance_sha256'):
                    projected[key] = source[key]
                pins = self.artifact['source_pins']['numeric:3']
                pins.update({k: projected[k] for k in ('manifest_sha256', 'body_sha256', 'provenance_sha256')})
                pins['projection_sha256'] = authoring.sha(authoring.dump(projected))
            self.index, self.digest = self.fixture.write('data/runs/transport.json', self.final)
            self.artifact['final_handoff_sha256'] = self.digest
            self.save_profile()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.admit('transport-' + mutation)
            self.assertFalse((self.root / ('transport-' + mutation)).exists())

    def test_snapshot_lineage_rejects_self_declared_handoff_hash(self):
        self.install()
        manifest, bodies, _ = self.admit()
        wrong = copy.deepcopy(manifest)
        wrong['input_index_sha256'] = '0' * 64
        with self.assertRaises(ValueError): reports.validate_admission(wrong, bodies)

    def test_non_native_numeric_tokens_reject(self):
        with self.assertRaises(ValueError): reports._value('not-a-number', 'numeric')
        self.install()
        manifest, bodies, _ = self.admit()
        bad, payloads = self.mutated_cells(manifest, bodies, lambda rows: [
            row.update(raw_value='not-a-number', value_state='invalid', numeric_value='', source_kind='json_string')
            for row in rows if row['td'] == '3' and row['presence'] == 'stored'])
        with self.assertRaises(ValueError): reports.validate_admission(bad, payloads)

    def test_full_shard_duplicate_entities_and_localizers_reject(self):
        for mutant in ({'id': 3, 'values': [{'e': 999, 'v': []}, {'e': 999, 'v': []}]},
                       {'id': 3, 'values': [{'e': 999, 'v': [{'i': 999, 'v': 0}, {'i': 999, 'v': 0}]}]}):
            self.install()
            source = self.final['sources'][-1]
            offer = self.fixture.descriptor['source_offers'][-1]
            source.update({**self.fixture.archive('numeric:3', mutant, source['native_file'], 3), **offer})
            # A trusted installed projection is not a waiver of whole-shard schema validation.
            body, record = profiles._authenticate_source(source, profiles.descriptor_for_selection(self.fixture.selection))
            projected = profiles._project_source_record(record)
            self.artifact['source_members']['numeric:3'] = projected
            self.artifact['source_pins']['numeric:3'] = {k: projected[k] for k in ('manifest_sha256', 'body_sha256', 'provenance_sha256')}
            self.artifact['source_pins']['numeric:3']['projection_sha256'] = authoring.sha(authoring.dump(projected))
            self.index, self.digest = self.fixture.write('data/runs/duplicate.json', self.final)
            self.artifact['final_handoff_sha256'] = self.digest
            self.save_profile()
            with self.assertRaisesRegex(ValueError, 'Duplicate numeric'):
                self.admit('duplicate')
            self.assertFalse((self.root / 'duplicate').exists())

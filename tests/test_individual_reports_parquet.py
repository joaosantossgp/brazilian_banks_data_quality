"""Exact projections with separate individual contracts and public boundaries."""
import json
import copy
from decimal import Decimal
import unittest
from unittest.mock import patch

from tests import test_individual_reports as fixtures
from tests.test_financial_reports import sha
from bank_quality import financial_reports_parquet as adapter
from bank_quality import financial_reports as admission
from bank_quality import financial_report_profiles as profiles


class IndividualHistoricalParquetTests(unittest.TestCase):
    def test_native_epochs_query_without_raw_or_admission_and_replay_exactly(self):
        # A query must rely on installed metadata and snapshot companions only.
        default = profiles.load_individual_context()
        financial = profiles.load_installed_context({'period': 202412, 'perspective': 1005, 'reports': [92,96,101,98]})
        for period, width in ((201012, 28), (202312, 32)):
            with self.subTest(period=period), fixtures.historical_admission_fixture(period) as (root, member, index):
                source = root / 'admission'
                admitted = admission.admit_individual(index, source, index_sha256=sha(index.read_bytes()))
                digest = sha((source / 'manifest.json').read_bytes())
                destination = root / 'parquet'
                result = adapter.convert_individual(source, destination, source_manifest_sha256=digest)
                replay = adapter.convert_individual(source, root / 'replay', source_manifest_sha256=digest)
                self.assertEqual(result['files'], replay['files'])
                self.assertEqual(result['contract'], 'ifdata-individual-reports-historical-parquet-v1')
                self.assertEqual(result['cells_part'], f'parts/individual-cells-{period}.parquet')
                (root / 'data').rename(root / 'raw-unavailable')
                source.rename(root / 'admission-unavailable')
                self.assertEqual(adapter.validate_individual_snapshot(destination,
                    manifest_sha256=result['manifest_sha256']), result)
                with adapter.individual_snapshot_connection(destination, manifest_sha256=result['manifest_sha256']) as con:
                    fields = [row[0] for row in con.execute('describe individual_cadastro').fetchall()]
                    self.assertEqual(len([k for k in fields if k.startswith('c') and k[1:].isdigit()]), width)
                    self.assertNotIn(f'c{width}', fields)
                    self.assertEqual(con.execute('select count(*) from individual_cells').fetchone(), (admitted['cells'],))
                    self.assertNotIn('numeric_decimal', [r[0] for r in con.execute('describe individual_cells').fetchall()])
                    self.assertTrue(all(b['decimal_type'].startswith('DECIMAL(') for b in result['numeric_bindings']))
                    self.assertFalse(any('financial' in row[0] for row in con.execute('show tables').fetchall()))
                decimals = list(adapter.iter_individual_numeric_decimals(destination, manifest_sha256=result['manifest_sha256']))
                self.assertIn(Decimal('123.4500'), [r['numeric_decimal'] for r in decimals])
                self.assertTrue(any(r['numeric_decimal'] is None for r in decimals))
                self.assertEqual(profiles.load_individual_context(), default)
                self.assertEqual(profiles.load_installed_context(financial['selection']), financial)

    def test_historical_wide_binding_preserves_text_and_python_decimal_without_raw(self):
        value = '123456789012345678901234567890123456789.0100'
        with fixtures.historical_admission_fixture(202312, wide=True) as (root, _, index):
            source = root / 'admission'
            admission.admit_individual(index, source, index_sha256=sha(index.read_bytes()))
            destination = root / 'parquet'
            result = adapter.convert_individual(source, destination,
                source_manifest_sha256=sha((source / 'manifest.json').read_bytes()))
            (root / 'data').rename(root / 'raw-unavailable')
            self.assertEqual(result['contract'], 'ifdata-individual-reports-historical-parquet-v1')
            self.assertEqual(result['numeric_projection'], 'mixed_exact_v1')
            wide = next(b for b in result['numeric_bindings'] if b.get('encoding') == 'decimal_text_v1')
            self.assertEqual(wide['storage_type'], 'VARCHAR')
            with adapter.individual_snapshot_connection(destination, manifest_sha256=result['manifest_sha256']) as con:
                self.assertEqual(con.execute('select numeric_exact_text from ' + wide['view'] + " where institution_id='0'").fetchone(), (value,))
            rows = list(adapter.iter_individual_numeric_decimals(destination, manifest_sha256=result['manifest_sha256'],
                binding_id=(wide['report_id'], wide['column_id'])))
            self.assertIn(Decimal(value), [r['numeric_decimal'] for r in rows])

    def test_repinned_historical_contract_or_legacy_qualification_is_rejected(self):
        with fixtures.historical_admission_fixture(202312) as (root, _, index):
            source = root / 'admission'
            admitted = admission.admit_individual(index, source, index_sha256=sha(index.read_bytes()))
            bodies = {e['path']: (source / e['path']).read_bytes() for e in admitted['files']}
            for contract in ('ifdata-individual-reports-snapshot-202412-v1', admission.CONTRACT,
                             'ifdata-financial-reports-historical-snapshot-v1'):
                mutated = copy.deepcopy(admitted); mutated['contract'] = contract
                with self.assertRaises(ValueError): admission.validate_individual_admission(mutated, bodies)
            destination = root / 'parquet'
            result = adapter.convert_individual(source, destination,
                source_manifest_sha256=sha((source / 'manifest.json').read_bytes()))
            path = destination / 'manifest.json'; original = path.read_bytes()
            for contract in ('ifdata-individual-reports-parquet-202412-v1', adapter.CONTRACT, adapter.HISTORICAL_V2):
                manifest = json.loads(original); manifest['contract'] = contract
                path.write_text(json.dumps(manifest), encoding='utf-8')
                with self.assertRaises(ValueError): adapter.validate_individual_snapshot(destination, manifest_sha256=sha(path.read_bytes()))
            path.write_bytes(original)
            companion = destination / 'metadata/source-manifest.json'
            source_manifest = json.loads(companion.read_bytes())
            source_manifest['sources']['cadaster']['completion_evidence'] = 'bounded complete'
            companion.write_text(json.dumps(source_manifest), encoding='utf-8')
            manifest = json.loads(original)
            entry = next(e for e in manifest['files'] if e['path'] == 'metadata/source-manifest.json')
            entry.update(sha256=sha(companion.read_bytes()), bytes=len(companion.read_bytes()))
            manifest['source_manifest_sha256'] = entry['sha256']
            path.write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'provenance'):
                adapter.validate_individual_snapshot(destination, manifest_sha256=sha(path.read_bytes()))


class IndividualParquetTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.IndividualReportsTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.context.update(part='parts/individual-cells-202412.parquet',
            parquet_contract='ifdata-individual-reports-parquet-202412-v1')
        self.root = self.fixture.root
        self.source = self.fixture.output
        self.destination = self.root / 'parquet'

    def convert(self):
        self.fixture.admit()
        return adapter.convert_individual(self.source, self.destination,
            source_manifest_sha256=sha((self.source / 'manifest.json').read_bytes()))

    def rewrite_manifest(self, change):
        path = self.destination / 'manifest.json'
        manifest = json.loads(path.read_bytes()); change(manifest)
        path.write_text(json.dumps(manifest), encoding='utf-8')
        return sha(path.read_bytes())

    def test_separate_contract_views_native_roster_and_exact_local_types(self):
        result = self.convert()
        self.assertEqual(result['contract'], 'ifdata-individual-reports-parquet-202412-v1')
        self.assertEqual(adapter.validate_individual_snapshot(self.destination,
            manifest_sha256=result['manifest_sha256']), result)
        with adapter.individual_snapshot_connection(self.destination, manifest_sha256=result['manifest_sha256']) as con:
            self.assertEqual(con.execute('select count(*) from individual_cells').fetchone(), (84,))
            self.assertEqual(con.execute('select count(*) from individual_observations').fetchone(), (64,))
            self.assertEqual(con.execute('select count(*) from individual_bindings').fetchone(), (24,))
            self.assertEqual(con.execute('select count(*) from individual_cadastro').fetchone(), (4,))
            self.assertEqual(con.execute("select c0 from individual_cadastro where c0='00111'").fetchone(), ('00111',))
            self.assertNotIn('numeric_decimal', [row[0] for row in con.execute('describe individual_cells').fetchall()])
            self.assertFalse(any('financial' in row[0] for row in con.execute('show tables').fetchall()))
            for binding in result['numeric_bindings']:
                self.assertTrue(binding['view'].startswith('individual_numeric_'))
                self.assertTrue(binding['decimal_type'].startswith('DECIMAL('))
                self.assertEqual(con.execute('select count(*) from ' + binding['view']).fetchone(), (4,))

    def test_wide_binding_own_contract_and_exact_accessor(self):
        value = '123456789012345678901234567890123456789.0100'
        self.fixture.bodies['numeric:1'] = self.fixture.bodies['numeric:1'].replace(b'9007199254740993.0100', value.encode())
        result = self.convert()
        self.assertEqual(result['contract'], 'ifdata-individual-reports-parquet-202412-v1')
        self.assertEqual(result['numeric_projection'], 'mixed_exact_v1')
        wide = next(b for b in result['numeric_bindings'] if b.get('encoding') == 'decimal_text_v1')
        self.assertEqual(wide['storage_type'], 'VARCHAR')
        rows = list(adapter.iter_individual_numeric_decimals(self.destination,
            manifest_sha256=result['manifest_sha256'], binding_id=(wide['report_id'], wide['column_id'])))
        self.assertIn(Decimal(value), [r['numeric_decimal'] for r in rows])
        with adapter.individual_snapshot_connection(self.destination, manifest_sha256=result['manifest_sha256']) as con:
            self.assertEqual(con.execute('select numeric_exact_text from ' + wide['view'] + " where institution_id='111'").fetchone(), (value,))

    def test_external_hash_changed_source_and_existing_destination(self):
        self.fixture.admit()
        digest = sha((self.source / 'manifest.json').read_bytes())
        with self.assertRaises(ValueError): adapter.convert_individual(self.source, self.destination, source_manifest_sha256='0'*64)
        path = self.source / 'individual-cells.csv'; original = path.read_bytes(); path.write_bytes(b'changed')
        with self.assertRaises(ValueError): adapter.convert_individual(self.source, self.destination, source_manifest_sha256=digest)
        self.assertFalse(self.destination.exists()); path.write_bytes(original)
        adapter.convert_individual(self.source, self.destination, source_manifest_sha256=digest)
        with self.assertRaises(FileExistsError): adapter.convert_individual(self.source, self.destination, source_manifest_sha256=digest)

    def test_source_cannot_embed_profile_override(self):
        self.fixture.admit()
        path = self.source / 'manifest.json'
        manifest = json.loads(path.read_bytes()); manifest['profile_path'] = 'untrusted.json'
        path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'profile override'):
            adapter.convert_individual(self.source, self.destination, source_manifest_sha256=sha(path.read_bytes()))
        self.assertFalse(self.destination.exists())

    def test_cross_contract_manifest_and_binding_mutations_rejected(self):
        result = self.convert()
        path = self.destination / 'manifest.json'; original = path.read_bytes()
        for key, value in [('contract', adapter.CONTRACT), ('selection', {'period':202412,'perspective':1005,'reports':[92,96,101,98]}), ('cells_part','parts/financial-cells-202412.parquet')]:
            path.write_bytes(original)
            digest = self.rewrite_manifest(lambda m: m.update({key:value}))
            with self.assertRaises(ValueError): adapter.validate_individual_snapshot(self.destination, manifest_sha256=digest)
        path.write_bytes(original)
        digest = self.rewrite_manifest(lambda m: m['numeric_bindings'][0].update(decimal_type='DOUBLE'))
        with self.assertRaises(ValueError): adapter.validate_individual_snapshot(self.destination, manifest_sha256=digest)
        path.write_bytes(original)
        with self.assertRaises(ValueError): adapter.validate_snapshot(self.destination, manifest_sha256=result['manifest_sha256'])
        with self.assertRaises(ValueError): adapter.convert_financial(self.source, self.root/'financial', source_manifest_sha256=sha((self.source/'manifest.json').read_bytes()))

    def test_changed_part_rejected_before_views_and_partial_preserved(self):
        result = self.convert()
        part = self.destination / result['numeric_bindings'][0]['path']; part.write_bytes(b'changed')
        with self.assertRaises(ValueError): adapter.individual_snapshot_connection(self.destination, manifest_sha256=result['manifest_sha256'])
        with patch.object(adapter, '_write_part', side_effect=RuntimeError('interrupted')):
            with self.assertRaises(RuntimeError): adapter.convert_individual(self.source, self.root/'partial', source_manifest_sha256=sha((self.source/'manifest.json').read_bytes()))
        self.assertFalse((self.root/'partial'/'manifest.json').exists())

    def test_numeric_selector_and_no_global_projection(self):
        result = self.convert()
        for selector in [(93,99999), [93,20], (True,20)]:
            with self.assertRaises(ValueError): list(adapter.iter_individual_numeric_decimals(self.destination,
                manifest_sha256=result['manifest_sha256'], binding_id=selector))
        rows = list(adapter.iter_individual_numeric_decimals(self.destination, manifest_sha256=result['manifest_sha256']))
        self.assertTrue(rows)
        self.assertTrue(all(r['numeric_decimal'] is None or isinstance(r['numeric_decimal'],Decimal) for r in rows))

    def test_repinned_typed_part_value_and_physical_type_are_rejected(self):
        result = self.convert()
        binding = result['numeric_bindings'][0]
        part = self.destination / binding['path']
        original = part.read_bytes()
        manifest_path = self.destination / 'manifest.json'; manifest_body = manifest_path.read_bytes()
        for physical in (False, True):
            part.write_bytes(original); manifest_path.write_bytes(manifest_body)
            with adapter._connection([self.destination]) as con:
                con.execute('create table changed as from read_parquet(?)', [str(part)])
                records = con.execute('select * from changed').fetchall()
            if physical:
                adapter._write_part(part, [*adapter.KEYS, 'numeric_decimal'], lambda: iter(
                    (*row[:-1], str(row[-1]) if row[-1] is not None else '') for row in records))
            else:
                adapter._write_part(part, adapter.KEYS, lambda: iter(
                    (*row[:-1], '9' if i == 0 else str(row[-1]) if row[-1] is not None else '')
                    for i, row in enumerate(records)), decimal_type=binding['decimal_type'])
            def repin(manifest):
                entry = next(e for e in manifest['files'] if e['path'] == binding['path'])
                entry.update(bytes=len(part.read_bytes()), sha256=sha(part.read_bytes()))
            digest = self.rewrite_manifest(repin)
            with self.assertRaisesRegex(ValueError, 'schema/type|Decimal mismatch'):
                adapter.validate_individual_snapshot(self.destination, manifest_sha256=digest)

    def test_owned_images_and_source_qualifications_survive_roundtrip(self):
        result = self.convert()
        original_files = adapter._files
        def swapped(*args):
            payload = original_files(*args)
            (self.destination / result['cells_part']).write_bytes(b'changed after verification')
            return payload
        with patch.object(adapter, '_files', side_effect=swapped):
            with adapter.individual_snapshot_connection(self.destination, manifest_sha256=result['manifest_sha256']) as con:
                self.assertEqual(con.execute('select count(*) from individual_cells').fetchone(), (84,))
                metadata = json.loads(con.execute('select metadata_json from individual_bindings limit 1').fetchone()[0])
                self.assertIn('origin_source_id', metadata)
        source = json.loads((self.destination/'metadata/source-manifest.json').read_bytes())
        self.assertEqual(source['sources']['dictionary']['retrieved_at_original'], '2026-10-01T01:00:00-03:00')
        self.assertEqual(source['sources']['dictionary']['retrieved_at_utc_derived'], '2026-10-01T04:00:00+00:00')
        self.assertIn('EOF unobserved', source['sources']['dictionary']['completion_evidence'])
        self.assertEqual(result['limitations'], source['limitations'])

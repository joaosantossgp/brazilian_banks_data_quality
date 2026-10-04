"""Offline exact per-binding projection tests; no inherited reader test suite."""
from decimal import Decimal
import importlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tests import test_financial_reports as fixtures
from bank_quality import financial_reports as reader


class FinancialReportsParquetTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.FinancialReportsTests()
        self.fixture.setUp()
        self.fixture.infos[3]['ty'] = 1
        self.fixture.data['numeric'] = self.fixture.data['numeric'].replace('9007199254740993.0100', '1234567890123.0100')
        self.fixture.write_sources(); self.fixture.make_profile()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.source = self.fixture.output
        self.destination = self.root / 'parquet'
        self.profile = patch.object(reader, 'PROFILE_PATH', self.fixture.profile_path)
        self.profile.start()
        self.addCleanup(self.profile.stop)

    def module(self):
        try:
            return importlib.import_module('bank_quality.financial_reports_parquet')
        except ModuleNotFoundError:
            self.fail('Per-binding Parquet API is missing')

    def convert(self):
        self.fixture.admit()
        return self.module().convert_financial(
            self.source, self.destination,
            source_manifest_sha256=fixtures.sha((self.source / 'manifest.json').read_bytes()))

    def connection(self, manifest):
        return self.module().snapshot_connection(self.destination, manifest_sha256=manifest['manifest_sha256'])

    def test_global_precision_40_local_types_exact_and_no_global_numeric(self):
        manifest = self.convert()
        self.assertEqual(manifest['decimal_type'], 'per_binding')
        numeric = manifest['numeric_bindings']
        self.assertEqual(len(numeric), 9)
        self.assertTrue(all(int(b['decimal_type'].split('(')[1].split(',')[0]) <= 38 for b in numeric))
        with self.connection(manifest) as con:
            columns = con.execute('DESCRIBE financial_cells').fetchall()
            self.assertNotIn('numeric_decimal', [c[0] for c in columns])
            self.assertEqual([c[0] for c in columns[:32]], reader.FIELDS)
            self.assertTrue(all(c[1] == 'VARCHAR' for c in columns[:32]))
            for binding in numeric:
                expected = con.execute("SELECT institution_id, report_id, catalog_pointer, numeric_value "
                                       "FROM financial_cells WHERE report_id=? AND catalog_pointer=?",
                                       [str(binding['report_id']), binding['catalog_pointer']]).fetchall()
                actual = con.execute('FROM ' + binding['view']).fetchall()
                self.assertEqual(actual, [(*r[:3], Decimal(r[3]) if r[3] else None) for r in expected])
                self.assertEqual(con.execute('DESCRIBE ' + binding['view']).fetchall()[-1][1], binding['decimal_type'])
            code = con.execute("SELECT raw_value, numeric_value FROM financial_cells WHERE ifd='10' AND institution_id='00111' LIMIT 1").fetchone()
            self.assertEqual(code, ('00111', ''))
            self.assertEqual(con.execute('SELECT count(*) FROM financial_cells').fetchone(), (84,))
            self.assertEqual(con.execute('SELECT count(*) FROM financial_observations').fetchone(), (64,))
            self.assertEqual(con.execute('SELECT count(*) FROM financial_bindings').fetchone(), (24,))
            numbers = [Decimal(row[0]) for row in con.execute("SELECT numeric_value FROM financial_cells WHERE numeric_value<>''").fetchall()]
            self.assertEqual(max(n.adjusted() + 1 for n in numbers) + max(-n.as_tuple().exponent for n in numbers), 40)

    def test_quantity_is_numeric_attribute_code_remains_text(self):
        # The fixture profile explicitly approves a quantity; Code is an attribute.
        result = self.convert()
        quantity = next(b for b in result['numeric_bindings'] if b['kind'] == 'quantity')
        with self.connection(result) as con:
            self.assertEqual(con.execute('SELECT numeric_decimal FROM ' + quantity['view']).fetchall(), [(Decimal(2),)] * 4)
        self.assertFalse(any(b['column_id'] == 920 for b in result['numeric_bindings']))

    def test_unsupported_local_precision_rejected_without_acceptance(self):
        self.fixture.data['numeric'] = self.fixture.data['numeric'].replace('1234567890123.0100', '1' + '0' * 38)
        self.fixture.write_sources(); self.fixture.make_profile()
        self.fixture.admit()
        with self.assertRaisesRegex(ValueError, '38'):
            self.module().convert_financial(self.source, self.destination,
                source_manifest_sha256=fixtures.sha((self.source / 'manifest.json').read_bytes()))
        self.assertFalse((self.destination / 'manifest.json').exists())

    def test_tokens_and_absences_keep_text_and_null_projection(self):
        for token, state in [('"NA"', 'NA'), ('"NI"', 'NI'), ('null', 'json_null'),
                             ('"null"', 'literal_null'), ('""', 'empty'), ('"oops"', 'invalid'),
                             ('"1.20"', 'numeric'), ('0', 'zero')]:
            with self.subTest(token=token):
                self.fixture.data['numeric'] = '{"id":1,"values":[{"e":111,"v":[{"i":700,"v":' + token + '}]}]}'
                self.fixture.write_sources(); self.fixture.make_profile()
                self.source = self.root / ('source-' + state)
                self.fixture.admit(self.source)
                self.destination = self.root / ('part-' + state)
                result = self.module().convert_financial(self.source, self.destination,
                    source_manifest_sha256=fixtures.sha((self.source / 'manifest.json').read_bytes()))
                binding = next(b for b in result['numeric_bindings'] if b['column_id'] == 924)
                with self.connection(result) as con:
                    self.assertEqual(con.execute("SELECT value_state FROM financial_cells WHERE report_id='92' AND ifd='20' AND institution_id='111'").fetchone(), (state,))
                    values = con.execute('SELECT numeric_decimal FROM ' + binding['view']).fetchall()
                    self.assertEqual(values, [(Decimal('1.20') if state == 'numeric' else Decimal(0) if state == 'zero' else None,), (None,), (None,), (None,)])

    def test_hashes_new_destination_and_exact_replay(self):
        result = self.convert()
        with self.assertRaises(FileExistsError):
            self.module().convert_financial(self.source, self.destination,
                source_manifest_sha256=fixtures.sha((self.source / 'manifest.json').read_bytes()))
        with self.assertRaises(ValueError):
            self.module().validate_snapshot(self.destination, manifest_sha256='0' * 64)
        replay = self.module().convert_financial(self.source, self.root / 'replay',
            source_manifest_sha256=fixtures.sha((self.source / 'manifest.json').read_bytes()))
        self.assertEqual(result['files'], replay['files'])
        self.assertEqual(result['numeric_bindings'], replay['numeric_bindings'])

    def save_manifest(self, manifest):
        manifest.pop('manifest_sha256', None)
        for entry in manifest['files']:
            body = (self.destination / entry['path']).read_bytes()
            entry.update(bytes=len(body), sha256=fixtures.sha(body))
        body = json.dumps(manifest).encode()
        (self.destination / 'manifest.json').write_bytes(body)
        return fixtures.sha(body)

    def rewrite_part(self, part, sql):
        import duckdb
        path = self.destination / part
        with duckdb.connect() as con:
            con.execute('CREATE TABLE cells AS FROM read_parquet(?)', [str(path)])
            con.execute(sql)
            con.execute('COPY cells TO ? (FORMAT PARQUET)', [str(path)])

    def test_coherent_text_numeric_type_order_and_key_adulterations_rejected(self):
        for change in ('text', 'numeric', 'type', 'order', 'key', 'global_numeric'):
            with self.subTest(change=change):
                self.source = self.root / ('source-' + change)
                self.fixture.admit(self.source)
                self.destination = self.root / ('parquet-' + change)
                manifest = self.module().convert_financial(self.source, self.destination,
                    source_manifest_sha256=fixtures.sha((self.source / 'manifest.json').read_bytes()))
                binding = manifest['numeric_bindings'][0]
                sql = {'text': "UPDATE cells SET raw_value='1234567890123.0200', numeric_value='1234567890123.0200' WHERE raw_value='1234567890123.0100'",
                       'numeric': 'UPDATE cells SET numeric_decimal=numeric_decimal+1',
                       'type': 'ALTER TABLE cells ALTER numeric_decimal TYPE DECIMAL(38,4)',
                       'order': 'CREATE OR REPLACE TABLE cells AS SELECT * FROM cells ORDER BY institution_id DESC',
                       'key': "UPDATE cells SET institution_id='alien'",
                       'global_numeric': 'ALTER TABLE cells ADD COLUMN numeric_decimal DECIMAL(38,4)'}[change]
                self.rewrite_part(manifest['cells_part'] if change in ('text', 'order', 'global_numeric') else binding['path'], sql)
                with self.assertRaises(ValueError):
                    self.module().validate_snapshot(self.destination, manifest_sha256=self.save_manifest(manifest))

    def test_closed_inventory_missing_extra_membership_and_partial_rejected(self):
        manifest = self.convert()
        extra = self.destination / 'parts' / 'extra.parquet'
        extra.write_bytes(b'unknown')
        with self.assertRaises(ValueError): self.connection(manifest)
        extra.unlink()
        for field, value in [('decimal_type', 'DECIMAL(38,27)'), ('profile_sha256', '0' * 64),
                             ('selection', {'period': 202412, 'perspective': 1005, 'reports': [92]}),
                             ('numeric_bindings', manifest['numeric_bindings'][:-1])]:
            bad = dict(manifest); bad[field] = value
            with self.assertRaises(ValueError):
                self.module().validate_snapshot(self.destination, manifest_sha256=self.save_manifest(bad))
        self.save_manifest(manifest)
        (self.destination / manifest['numeric_bindings'][0]['path']).unlink()
        with self.assertRaises((ValueError, FileNotFoundError)):
            self.module().validate_snapshot(self.destination, manifest_sha256=fixtures.sha((self.destination / 'manifest.json').read_bytes()))

    def test_source_profile_provenance_and_metadata_mutants_rejected(self):
        manifest = self.convert()
        path = self.destination / 'metadata/source-manifest.json'
        original = path.read_bytes()
        for change in ('profile', 'source_context', 'original_csv_hash'):
            with self.subTest(change=change):
                source = json.loads(original)
                if change == 'profile': source['profile_sha256'] = '0' * 64
                elif change == 'source_context': source['sources']['numeric']['context']['perspective'] = 1005
                else: source['files'][0]['sha256'] = '0' * 64
                body = json.dumps(source).encode(); path.write_bytes(body)
                bad = dict(manifest, source_manifest_sha256=fixtures.sha(body), source_files=source['files'])
                with self.assertRaises(ValueError):
                    self.module().validate_snapshot(self.destination, manifest_sha256=self.save_manifest(bad))
        path.write_bytes(original)
        var = self.destination / 'metadata/financial-variables.json'
        document = json.loads(var.read_bytes()); document['nodes'][0]['name'] = 'adulterated'
        var.write_text(json.dumps(document))
        with self.assertRaises(ValueError):
            self.module().validate_snapshot(self.destination, manifest_sha256=self.save_manifest(manifest))

    def test_owned_verified_images_mutation_after_hash_and_load_raw_free(self):
        manifest = self.convert()
        module = self.module()
        original = module._files
        def swap(*args):
            bodies = original(*args)
            (self.destination / manifest['cells_part']).write_bytes(b'changed after verification')
            return bodies
        with patch.object(module, '_files', side_effect=swap):
            con = self.connection(manifest)
        self.addCleanup(con.close)
        for path in self.source.iterdir(): path.unlink()
        for path in self.root.glob('*.bin'): path.unlink()
        for binding in manifest['numeric_bindings']:
            (self.destination / binding['path']).write_bytes(b'changed after load')
        self.assertEqual(con.execute('SELECT count(*) FROM financial_cells').fetchone(), (84,))
        self.assertEqual(con.execute('SELECT numeric_decimal FROM ' + manifest['numeric_bindings'][0]['view']).fetchall(), [(Decimal(2),)] * 4)
        with self.assertRaises(Exception):
            con.execute('FROM read_csv(?)', [str(self.fixture.profile_path)])

    def test_returned_metadata_cannot_mutate_closed_context(self):
        self.module()
        fields = list(reader.FIELDS)
        reports = list(reader.SELECTION['reports'])
        self.addCleanup(lambda: reader.FIELDS.__setitem__(slice(None), fields))
        self.addCleanup(lambda: reader.SELECTION['reports'].__setitem__(slice(None), reports))
        manifest = self.convert()
        manifest['original_fields'].clear()
        manifest['selection']['reports'].clear()
        self.assertEqual(reader.FIELDS, fields)
        self.assertEqual(reader.SELECTION['reports'], reports)

    def test_numeric_looking_attribute_and_large_integer_preserve_kinds(self):
        self.fixture.infos[3]['ty'] = 0
        self.fixture.reports[0]['c'][3]['fid'] = 9
        self.fixture.data['numeric'] = self.fixture.data['numeric'].replace('1234567890123.0100', '9007199254740993.0100')
        self.fixture.write_sources(); self.fixture.make_profile()
        manifest = self.convert()
        self.assertEqual(len(manifest['numeric_bindings']), 8)
        with self.connection(manifest) as con:
            self.assertEqual(con.execute("SELECT raw_value,numeric_value,value_state FROM financial_cells WHERE ifd='13' LIMIT 1").fetchone(), ('0002', '', 'text'))
            view = next(b['view'] for b in manifest['numeric_bindings'] if b['column_id'] == 924)
            self.assertEqual(con.execute('SELECT numeric_decimal FROM ' + view + " WHERE institution_id='111'").fetchone(), (Decimal('9007199254740993.0100'),))

    def test_source_verified_images_and_hash_guard(self):
        self.fixture.admit()
        source_hash = fixtures.sha((self.source / 'manifest.json').read_bytes())
        module = self.module()
        with self.assertRaises(ValueError):
            module.convert_financial(self.source, self.destination, source_manifest_sha256='0' * 64)
        self.assertFalse(self.destination.exists())
        original = module._files
        def swap(*args):
            bodies = original(*args)
            (self.source / 'financial-cells.csv').write_bytes(b'changed after verification')
            return bodies
        with patch.object(module, '_files', side_effect=swap):
            manifest = module.convert_financial(self.source, self.destination, source_manifest_sha256=source_hash)
        with self.connection(manifest) as con:
            self.assertEqual(con.execute('SELECT count(*) FROM financial_cells').fetchone(), (84,))

    def test_interrupted_writer_and_untrusted_paths_never_accept(self):
        self.fixture.admit()
        module = self.module()
        with patch.object(module, '_write_part', side_effect=RuntimeError('interrupted writer')):
            with self.assertRaisesRegex(RuntimeError, 'interrupted writer'):
                module.convert_financial(self.source, self.destination,
                    source_manifest_sha256=fixtures.sha((self.source / 'manifest.json').read_bytes()))
        self.assertFalse((self.destination / 'manifest.json').exists())
        self.destination = self.root / 'safe'
        manifest = module.convert_financial(self.source, self.destination,
            source_manifest_sha256=fixtures.sha((self.source / 'manifest.json').read_bytes()))
        manifest['files'][0]['path'] = '../outside.parquet'
        body = json.dumps({k: v for k, v in manifest.items() if k != 'manifest_sha256'}).encode()
        (self.destination / 'manifest.json').write_bytes(body)
        with self.assertRaises(ValueError):
            module.validate_snapshot(self.destination, manifest_sha256=fixtures.sha(body))


if __name__ == '__main__':
    unittest.main()

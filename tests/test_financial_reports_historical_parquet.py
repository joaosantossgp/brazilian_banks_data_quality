"""Historical Parquet uses real installed profile/admission fixtures offline."""
import copy
import csv
from decimal import Decimal, localcontext
import io
import json
import unittest
from unittest.mock import patch

from bank_quality import financial, financial_parquet as public
from bank_quality import financial_reports as reader, financial_reports_parquet as adapter
from bank_quality import financial_report_profiles as profiles
from tests import test_financial_reports_historical as fixtures
from tests.test_financial_report_profiles import dump, sha


class HistoricalParquetTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.HistoricalTests('test_multishard_identity_and_absence_are_scoped')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root

    def admit(self, name='admitted'):
        manifest, bodies, validated = self.fixture.admit(name)
        source = self.root / name
        return source, manifest, bodies, validated

    def convert(self, name='parquet', source=None):
        source = source or self.admit()[0]
        destination = self.root / name
        manifest = public.convert_financial(source, destination,
            source_manifest_sha256=sha((source / 'manifest.json').read_bytes()))
        return destination, manifest

    def replace_numeric(self, token, second_token=None):
        """Re-freeze a tiny authenticated synthetic source through the real guard."""
        f = self.fixture
        source = f.final['sources'][-1]
        offer = f.fixture.descriptor['source_offers'][-1]
        values = b'{"e":1,"v":[{"i":7,"v":' + token + b'}]}'
        if second_token is not None:
            values += b',{"e":2,"v":[{"i":7,"v":' + second_token + b'}]}'
        body = b'{"id":3,"values":[' + values + b']}'
        source.update({**f.fixture.archive('numeric:3', body, source['native_file'], 3), **offer})
        _, record = profiles._authenticate_source(source, profiles.descriptor_for_selection(f.fixture.selection))
        projected = profiles._project_source_record(record)
        f.artifact['source_members']['numeric:3'] = projected
        f.artifact['source_pins']['numeric:3'] = {k: projected[k] for k in
            ('manifest_sha256', 'body_sha256', 'provenance_sha256')}
        f.artifact['source_pins']['numeric:3']['projection_sha256'] = sha(dump(projected))
        f.index, digest = f.fixture.write('data/runs/final.json', f.final)
        f.artifact['final_handoff_sha256'] = digest
        f.save_profile()

    def write_admission(self, source, manifest, bodies):
        for name, body in bodies.items():
            (source / name).write_bytes(body)
        (source / 'manifest.json').write_bytes(dump(manifest))

    def write_snapshot_manifest(self, destination, manifest):
        manifest = copy.deepcopy(manifest)
        manifest.pop('manifest_sha256', None)
        for entry in manifest['files']:
            body = (destination / entry['path']).read_bytes()
            entry.update(bytes=len(body), sha256=sha(body))
        body = dump(manifest)
        (destination / 'manifest.json').write_bytes(body)
        return sha(body)

    def test_historical_parquet_reconstructs_all_sources_and_local_decimals(self):
        self.fixture.install(width=32, equal=True, quantity=True)
        source, admission, bodies, validated = self.admit()
        destination, manifest = self.convert(source=source)
        self.assertEqual(manifest['contract'], 'ifdata-financial-reports-historical-parquet-v1')
        self.assertEqual(public.validate_snapshot(destination, manifest_sha256=manifest['manifest_sha256']), manifest)
        self.assertEqual(len(manifest['original_fields']), 32)
        self.assertEqual(len(manifest['numeric_bindings']), 12)
        # Accepted snapshot reopens without any RAW inputs or admission outputs.
        (self.root / 'data').rename(self.root / 'synthetic-inputs-unavailable')
        source.rename(self.root / 'synthetic-admission-unavailable')
        con, _, rebuilt = adapter._open_snapshot(destination, manifest['manifest_sha256'])
        con.close()
        for key in ('cells', 'observations', 'cadastro', 'variables', 'diagnostics'):
            self.assertEqual(rebuilt[key], validated[key])
        for name in adapter.COMPANIONS:
            self.assertEqual((destination / 'metadata' / name).read_bytes(), bodies[name])
        with public.snapshot_connection(destination, manifest_sha256=manifest['manifest_sha256']) as con:
            rows = con.execute('SELECT ' + ','.join(reader.FIELDS) + ' FROM financial_cells').fetchall()
            self.assertEqual(rows, [tuple(row[k] for k in reader.FIELDS) for row in validated['cells']])
            columns = con.execute('DESCRIBE financial_cells').fetchall()
            self.assertEqual([c[1] for c in columns[:32]], ['VARCHAR'] * 32)
            self.assertNotIn('numeric_decimal', [c[0] for c in columns])
            self.assertEqual(con.execute('SELECT count(*) FROM financial_bindings').fetchone(), (16,))
            for binding in manifest['numeric_bindings']:
                expected = [row for row in validated['cells'] if row['catalog_pointer'] == binding['catalog_pointer']]
                actual = con.execute('FROM ' + binding['view']).fetchall()
                self.assertEqual(actual, [(r['institution_id'], r['report_id'], r['catalog_pointer'],
                    Decimal(r['numeric_value']) if r['numeric_value'] else None) for r in expected])
                self.assertEqual(con.execute('DESCRIBE ' + binding['view']).fetchall()[-1][1], binding['decimal_type'])
            self.assertEqual(con.execute("SELECT DISTINCT unit FROM financial_cells").fetchall(), [('unknown',)])

    def test_exact_tokens_states_absences_and_numeric_looking_attribute(self):
        variants = [(b'9007199254740993.0100', '9007199254740993.0100', 'numeric'),
                    (b'-0.00', '-0.00', 'zero'), (b'0', '0', 'zero'),
                    (b'"1.20"', '1.20', 'numeric'), (b'"NA"', '', 'NA'),
                    (b'"NI"', '', 'NI'), (b'null', '', 'json_null'),
                    (b'"null"', '', 'literal_null'), (b'""', '', 'empty')]
        self.fixture.install()
        for number, (token, value, state) in enumerate(variants):
            with self.subTest(token=token):
                self.replace_numeric(token)
                source, _, _, validated = self.admit('tokens-' + str(number))
                destination, manifest = self.convert('parts-' + str(number), source)
                nodes = {n['catalog_pointer']: n for n in validated['variables']['variables']}
                binding = next(b for b in manifest['numeric_bindings'] if
                               nodes[b['catalog_pointer']]['origin_source_id'] == 'numeric:3')
                with public.snapshot_connection(destination, manifest_sha256=manifest['manifest_sha256']) as con:
                    row = con.execute("SELECT value_state,numeric_value,raw_value FROM financial_cells "
                        "WHERE catalog_pointer=? AND institution_id='1'", [binding['catalog_pointer']]).fetchone()
                    self.assertEqual(row[:2], (state, value))
                    self.assertEqual(con.execute('SELECT numeric_decimal FROM ' + binding['view'] +
                        " WHERE institution_id='1'").fetchone(), (Decimal(value) if value else None,))
                    self.assertEqual(con.execute("SELECT raw_value,numeric_value FROM financial_cells WHERE source_role='cadaster' LIMIT 1").fetchone(), ('0009', ''))
                    self.assertEqual(con.execute("SELECT DISTINCT presence FROM financial_cells WHERE area='3'").fetchall(),
                                     [('stored',), ('entity_not_stored',)])
                    if token == b'-0.00':
                        self.assertEqual(row[2], '-0.00')  # Decimal SQL zero may lose sign; authoritative text never does.

    def test_origin_mapping_rejects_cross_shard_swaps_before_sql(self):
        self.fixture.install(equal=True)
        source, manifest, bodies, validated = self.admit()
        rows = validated['cells']
        self.assertEqual(rows[3]['raw_value'], rows[6]['raw_value'])
        self.assertEqual(rows[3]['source_pointer'], rows[6]['source_pointer'])
        for field in ('area', 'source_role', 'source_body', 'source_sha256'):
            value = rows[6][field] if field != 'source_role' else 'cadaster'
            bad, payloads = self.fixture.mutated_cells(manifest, bodies, lambda rows: rows[3].update({field: value}))
            self.write_admission(source, bad, payloads)
            with self.subTest(field=field), patch.object(adapter, '_connection', side_effect=AssertionError('SQL before origin validation')):
                with self.assertRaisesRegex(ValueError, 'provenance'):
                    self.convert('bad-origin-' + field, source)
                self.assertFalse((self.root / ('bad-origin-' + field)).exists())
        self.write_admission(source, manifest, bodies)
        for mutation in ('map', 'binding'):
            original = copy.deepcopy(self.fixture.artifact)
            if mutation == 'map': self.fixture.artifact['source_members']['numeric:3']['area'] = 1
            else: self.fixture.artifact['reports'][0]['nodes'][2]['origin_source_id'] = 'numeric:3'
            self.fixture.save_profile()
            with self.subTest(mutation=mutation), patch.object(adapter, '_connection', side_effect=AssertionError('SQL before installed map')):
                with self.assertRaises(ValueError): self.convert('bad-map-' + mutation, source)
            self.fixture.artifact = original
            self.fixture.save_profile()

    def test_hash_selection_contract_and_profile_precede_sql(self):
        self.fixture.install()
        source, admitted, bodies, _ = self.admit()
        destination, manifest = self.convert(source=source)
        for public_api, path, args, key in ((public.convert_financial, source, (self.root / 'bad-hash',), 'source_manifest_sha256'),
                (public.validate_snapshot, destination, (), 'manifest_sha256'),
                (public.snapshot_connection, destination, (), 'manifest_sha256')):
            with patch.object(adapter, public_api.__name__, side_effect=AssertionError('Dispatch before hash')):
                with self.assertRaisesRegex(ValueError, 'manifest hash mismatch'): public_api(path, *args, **{key: '0' * 64})
        for field, value in (('contract', 'ifdata-financial-reports-snapshot-202412-v1'),
                ('selection', {**admitted['selection'], 'reports': admitted['selection']['reports'][:-1]}),
                ('selection', {**admitted['selection'], 'period': 201406}),
                ('profile_sha256', '0' * 64), ('profile_path', 'arbitrary.json')):
            bad = {**admitted, field: value}
            self.write_admission(source, bad, bodies)
            with self.subTest(field=field, value=value), patch.object(adapter, '_connection', side_effect=AssertionError('SQL before guard')):
                with self.assertRaises(ValueError): self.convert('bad-guard', source)
                self.assertFalse((self.root / 'bad-guard').exists())
        self.write_admission(source, admitted, bodies)
        original = (destination / 'manifest.json').read_bytes()
        for field, value in (('contract', 'ifdata-financial-reports-parquet-202412-v1'),
                ('selection', {**manifest['selection'], 'reports': manifest['selection']['reports'][:-1]}),
                ('profile_sha256', '0' * 64), ('profile_path', 'injected.json')):
            digest = self.write_snapshot_manifest(destination, {**manifest, field: value})
            with self.subTest(snapshot_field=field), patch.object(adapter, '_connection', side_effect=AssertionError('SQL before guard')):
                with self.assertRaises(ValueError): public.validate_snapshot(destination, manifest_sha256=digest)
        (destination / 'manifest.json').write_bytes(original)
        for root, name in ((source, 'extra.csv'), (destination / 'parts', 'extra.parquet'),
                           (destination / 'metadata', 'extra.json')):
            extra = root / name
            extra.write_bytes(b'extra')
            with self.subTest(extra=name), patch.object(adapter, '_connection', side_effect=AssertionError('SQL before inventory')):
                with self.assertRaises(ValueError):
                    if root == source: self.convert('bad-extra', source)
                    else: public.validate_snapshot(destination, manifest_sha256=manifest['manifest_sha256'])
            extra.unlink()

    def test_decimal_width_guard_still_rejects_without_historical_context(self):
        with self.assertRaisesRegex(ValueError, '38'):
            adapter._decimal_type([{'numeric_value': '100000000000000000000000000000000000000'}])

    def test_wide_mixed_projection_preserves_exact_text_and_python_decimals(self):
        self.fixture.install()
        variants = [b'-12345678901.12345678901234567890123456789', b'1e-40',
                    b'100000000000000000000000000000000000000.00']
        for i, token in enumerate(variants):
            with self.subTest(token=token):
                self.replace_numeric(token)
                source, _, bodies, validated = self.admit('wide-source-' + str(i))
                before = {name: sha(body) for name, body in bodies.items()}
                destination, manifest = self.convert('wide-' + str(i), source)
                self.assertEqual(manifest['contract'], 'ifdata-financial-reports-historical-parquet-v2')
                self.assertEqual(manifest['numeric_projection'], 'mixed_exact_v1')
                wide = [b for b in manifest['numeric_bindings'] if b['encoding'] == 'decimal_text_v1']
                fit = [b for b in manifest['numeric_bindings'] if b['encoding'] == 'duckdb_decimal']
                self.assertTrue(wide and fit)
                for b in manifest['numeric_bindings']:
                    self.assertEqual(set(b), {'report_id', 'column_id', 'catalog_pointer', 'kind', 'decimal_type',
                        'view', 'path', 'rows', 'encoding', 'precision', 'scale', 'value_column', 'storage_type'})
                    self.assertIs(type(b['precision']), int)
                    self.assertIs(type(b['scale']), int)
                with public.snapshot_connection(destination, manifest_sha256=manifest['manifest_sha256']) as con:
                    self.assertEqual(con.execute('SELECT ' + ','.join(reader.FIELDS) + ' FROM financial_cells').fetchall(),
                        [tuple(r[k] for k in reader.FIELDS) for r in validated['cells']])
                    for b in wide:
                        self.assertIsNone(b['decimal_type'])
                        self.assertEqual((b['value_column'], b['storage_type']), ('numeric_exact_text', 'VARCHAR'))
                        expected = [r['numeric_value'] or None for r in validated['cells'] if r['catalog_pointer'] == b['catalog_pointer']]
                        self.assertEqual(con.execute('SELECT numeric_exact_text FROM ' + b['view']).fetchall(), [(v,) for v in expected])
                        self.assertEqual(con.execute('DESCRIBE ' + b['view']).fetchall()[-1][:2], ('numeric_exact_text', 'VARCHAR'))
                with localcontext() as ctx:
                    ctx.prec = 3
                    actual = list(adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256']))
                numeric = {b['catalog_pointer']: b for b in manifest['numeric_bindings']}
                expected = [dict(institution_id=r['institution_id'], report_id=int(r['report_id']),
                    column_id=numeric[r['catalog_pointer']]['column_id'], catalog_pointer=r['catalog_pointer'],
                    numeric_decimal=Decimal(r['numeric_value']) if r['numeric_value'] else None)
                    for r in validated['cells'] if r['catalog_pointer'] in numeric]
                self.assertEqual(actual, expected)
                self.assertEqual(before, {name: sha((source / name).read_bytes()) for name in reader.INPUTS})
                replay, repeated = self.convert('wide-replay-' + str(i), source)
                self.assertEqual(manifest['files'], repeated['files'])
                self.assertEqual(manifest['numeric_bindings'], repeated['numeric_bindings'])

    def test_decimal_accessor_validates_once_and_closes_on_early_exit_and_failure(self):
        self.fixture.install()
        destination, manifest = self.convert()
        real_open = adapter._open_snapshot
        closed = []
        class OwnedConnection:
            def __init__(self, con): self.con = con
            def execute(self, *args): return self.con.execute(*args)
            def close(self):
                closed.append(True)
                self.con.close()
        def opened(*args, **kwargs):
            con, meta, validated = real_open(*args, **kwargs)
            return OwnedConnection(con), meta, validated
        with patch.object(adapter, '_open_snapshot', side_effect=opened) as spy:
            unused = adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256'])
            unused.close()
            self.assertEqual(spy.call_count, 0)
            iterator = adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256'])
            self.assertIsInstance(next(iterator)['numeric_decimal'], Decimal)
            iterator.close()
            self.assertEqual((spy.call_count, len(closed)), (1, 1))
            result = list(adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256']))
            self.assertEqual((spy.call_count, len(closed), len(result)), (2, 2, 24))
            real_records = adapter._records
            def fail_view(con, table):
                if table.endswith('_data') or table == 'financial_data':
                    return real_records(con, table)
                raise RuntimeError('iterator read failure')
            with patch.object(adapter, '_records', side_effect=fail_view):
                iterator = adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256'])
                with self.assertRaisesRegex(RuntimeError, 'iterator read failure'): next(iterator)
            self.assertEqual((spy.call_count, len(closed)), (3, 3))
        real_connection = adapter._connection
        with patch.object(adapter, '_connection', side_effect=lambda *a: OwnedConnection(real_connection(*a))):
            with patch.object(adapter, '_original_csv_images', side_effect=RuntimeError('validation failure')):
                with self.assertRaisesRegex(RuntimeError, 'validation failure'):
                    next(adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256']))
        self.assertEqual(len(closed), 4)
        b = manifest['numeric_bindings'][0]
        selected = list(adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256'],
            binding_id=(b['report_id'], b['column_id'])))
        self.assertEqual(len(selected), 3)
        self.assertEqual({r['column_id'] for r in selected}, {b['column_id']})
        for selector in ([b['report_id'], b['column_id']], (True, b['column_id']),
                         (b['report_id'], 999999), ('1', b['column_id']), (b['report_id'],)):
            with self.subTest(selector=selector), patch.object(adapter, '_connection', side_effect=AssertionError('SQL before selector guard')):
                with self.assertRaises(ValueError):
                    list(adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256'], binding_id=selector))

    def test_v2_binding_encoding_metadata_is_closed_and_recomputed_before_numeric_sql(self):
        self.fixture.install()
        self.replace_numeric(b'-12345678901.12345678901234567890123456789')
        destination, manifest = self.convert()
        original = (destination / 'manifest.json').read_bytes()
        wide_index = next(i for i, b in enumerate(manifest['numeric_bindings']) if b['encoding'] == 'decimal_text_v1')
        mutations = [('encoding', 'duckdb_decimal'), ('precision', 39), ('precision', True),
            ('scale', 28), ('scale', '29'), ('value_column', 'numeric_decimal'),
            ('storage_type', 'DECIMAL(38,29)'), ('decimal_type', 'DECIMAL(40,29)'),
            ('unknown', 'injected'), ('column_id', True)]
        real = adapter._connection
        class GuardedConnection:
            def __init__(self, con): self.con = con
            def execute(self, sql, *args):
                if 'financial_numeric_' in sql or sql.startswith('CREATE VIEW'):
                    raise AssertionError('Numeric SQL before metadata comparison')
                return self.con.execute(sql, *args)
            def close(self): self.con.close()
        for field, value in mutations:
            bad = copy.deepcopy(manifest)
            bad['numeric_bindings'][wide_index][field] = value
            digest = self.write_snapshot_manifest(destination, bad)
            with self.subTest(field=field, value=value), patch.object(adapter, '_connection', side_effect=lambda *a: GuardedConnection(real(*a))):
                with self.assertRaises(ValueError): public.validate_snapshot(destination, manifest_sha256=digest)
        for field, value in (('numeric_projection', 'other'), ('contract', 'ifdata-financial-reports-historical-parquet-v1')):
            bad = {**manifest, field: value}
            digest = self.write_snapshot_manifest(destination, bad)
            with patch.object(adapter, '_connection', side_effect=AssertionError('SQL before schema guard')):
                with self.assertRaises(ValueError): public.validate_snapshot(destination, manifest_sha256=digest)
        (destination / 'manifest.json').write_bytes(original)
        # Bad hash must still fail in the public dispatcher before the adapter.
        with patch.object(adapter, 'validate_snapshot', side_effect=AssertionError('Dispatch before hash')):
            with self.assertRaisesRegex(ValueError, 'manifest hash mismatch'):
                public.validate_snapshot(destination, manifest_sha256='0' * 64)

    def test_wide_common_width_and_zero_scale_are_measured_without_context_arithmetic(self):
        self.fixture.install()
        self.replace_numeric(b'12345678901', b'-0.12345678901234567890123456789')
        with localcontext() as ctx:
            ctx.prec = 2
            destination, manifest = self.convert()
            wide = next(b for b in manifest['numeric_bindings'] if b['encoding'] == 'decimal_text_v1')
            self.assertEqual((wide['precision'], wide['scale']), (40, 29))
            rows = list(adapter.iter_numeric_decimals(destination, manifest_sha256=manifest['manifest_sha256'],
                binding_id=(wide['report_id'], wide['column_id'])))
        self.assertEqual([r['numeric_decimal'] for r in rows],
                         [Decimal('12345678901'), Decimal('-0.12345678901234567890123456789'), None])
        self.assertEqual(adapter._decimal_dimensions([{'numeric_value': '-0.00'}, {'numeric_value': ''}]), (2, 2))
        self.assertEqual(adapter._decimal_dimensions([{'numeric_value': ''}]), (1, 0))
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            adapter._decimal_dimensions([{'numeric_value': 'NaN'}])

    def test_coherently_repinned_wide_part_tampering_rejects_before_any_views(self):
        self.fixture.install()
        self.replace_numeric(b'-12345678901.12345678901234567890123456789')
        source, _, _, validated = self.admit()
        destination, manifest = self.convert(source=source)
        wide = next(b for b in manifest['numeric_bindings'] if b['encoding'] == 'decimal_text_v1')
        originals = [tuple(r[k] for k in adapter.KEYS) + (r['numeric_value'],)
                     for r in validated['cells'] if r['catalog_pointer'] == wide['catalog_pointer']]
        real = adapter._connection
        class NoViews:
            def __init__(self, con): self.con = con
            def execute(self, sql, *args):
                if sql.startswith('CREATE VIEW'):
                    raise AssertionError('View published before all typed parts validate')
                return self.con.execute(sql, *args)
            def close(self): self.con.close()
        for mutation in ('equivalent_lexeme', 'null', 'null_text', 'key', 'order', 'duplicate', 'physical_column'):
            rows = list(originals)
            column = 'numeric_exact_text'
            if mutation == 'equivalent_lexeme': rows[0] = (*rows[0][:-1], rows[0][-1] + '0')
            elif mutation == 'null': rows[0] = (*rows[0][:-1], '')
            elif mutation == 'null_text': rows[1] = (*rows[1][:-1], 'null')
            elif mutation == 'key': rows[0] = ('other', *rows[0][1:])
            elif mutation == 'order': rows.reverse()
            elif mutation == 'duplicate': rows[1] = rows[0]
            else: column = 'numeric_decimal'
            # Write an internally consistent Parquet mutant and re-pin its file.
            adapter._write_part(destination / wide['path'], [*adapter.KEYS, column], lambda: iter(rows))
            digest = self.write_snapshot_manifest(destination, manifest)
            with self.subTest(mutation=mutation), patch.object(adapter, '_connection', side_effect=lambda *a: NoViews(real(*a))):
                with self.assertRaisesRegex(ValueError, 'schema/type|keys/order/Decimal'):
                    public.snapshot_connection(destination, manifest_sha256=digest)

    def test_v2_cannot_forge_ordinary_text_encoding_or_exist_without_wide_values(self):
        self.fixture.install()
        ordinary_source = self.admit('ordinary-source')[0]
        ordinary, v1 = self.convert('ordinary', ordinary_source)
        self.replace_numeric(b'1e-40')
        destination, v2 = self.convert('wide', self.admit('wide-source')[0])
        bindings = copy.deepcopy(v2['numeric_bindings'])
        fit = next(b for b in bindings if b['encoding'] == 'duckdb_decimal')
        fit.update(encoding='decimal_text_v1', decimal_type=None, value_column='numeric_exact_text', storage_type='VARCHAR')
        digest = self.write_snapshot_manifest(destination, {**v2, 'numeric_bindings': bindings})
        with self.assertRaisesRegex(ValueError, 'binding map/type'):
            public.validate_snapshot(destination, manifest_sha256=digest)
        # Reinstall the original fixture profile to authenticate the v1 snapshot.
        self.fixture.install()
        forged = {**v1, 'contract': adapter.HISTORICAL_V2, 'numeric_projection': 'mixed_exact_v1'}
        for binding in forged['numeric_bindings']:
            precision, scale = map(int, binding['decimal_type'][8:-1].split(','))
            binding.update(encoding='duckdb_decimal', precision=precision, scale=scale,
                           value_column='numeric_decimal', storage_type=binding['decimal_type'])
        digest = self.write_snapshot_manifest(ordinary, forged)
        with self.assertRaisesRegex(ValueError, 'contract/width'):
            public.validate_snapshot(ordinary, manifest_sha256=digest)

    def test_snapshot_source_identity_and_binding_membership_precede_sql(self):
        self.fixture.install()
        source = self.admit()[0]
        destination, manifest = self.convert(source=source)
        path = destination / 'metadata/source-manifest.json'
        original = path.read_bytes()
        admitted = json.loads(original)
        for mutation in ('profile', 'lineage', 'origin', 'override', 'subset', 'extra', 'binding'):
            bad, accepted = copy.deepcopy(manifest), copy.deepcopy(admitted)
            if mutation == 'profile': accepted['profile_sha256'] = '0' * 64
            elif mutation == 'lineage': accepted['input_index_sha256'] = '0' * 64
            elif mutation == 'origin': accepted['sources']['numeric:3']['area'] = 1
            elif mutation == 'override': accepted['profile_path'] = 'arbitrary.json'
            elif mutation == 'subset': bad['numeric_bindings'].pop()
            elif mutation == 'extra': bad['numeric_bindings'].append(bad['numeric_bindings'][0])
            else: bad['numeric_bindings'][0]['view'] = 'injected_view'
            body = dump(accepted)
            path.write_bytes(body)
            bad['source_manifest_sha256'] = sha(body)
            digest = self.write_snapshot_manifest(destination, bad)
            with self.subTest(mutation=mutation), patch.object(adapter, '_connection', side_effect=AssertionError('SQL before origin/profile/map guard')):
                with self.assertRaises(ValueError): public.validate_snapshot(destination, manifest_sha256=digest)
        path.write_bytes(original)

    def test_coherent_parquet_origin_swap_rejects_before_numeric_load_or_public_views(self):
        self.fixture.install(equal=True)
        source, original_manifest, bodies, _ = self.admit()
        for field in ('area', 'source_role', 'source_body', 'source_sha256'):
            destination, manifest = self.convert('origin-' + field, source)
            admission, payloads = self.fixture.mutated_cells(original_manifest, bodies,
                lambda rows: rows[3].update({field: rows[6][field] if field != 'source_role' else 'cadaster'}))
            # Make both stored/cells hashes coherent so the installed origin guard,
            # rather than an incidental byte mismatch, rejects the tampered image.
            rows = list(csv.DictReader(io.StringIO(payloads['financial-cells.csv'].decode('utf-8-sig'))))
            stream = io.StringIO(newline='')
            writer = csv.DictWriter(stream, fieldnames=reader.FIELDS, lineterminator='\n')
            writer.writeheader()
            writer.writerows(row for row in rows if row['presence'] == 'stored')
            payloads['financial-observations.csv'] = stream.getvalue().encode()
            for record in admission['files']:
                body = payloads[record['path']]
                record.update(bytes=len(body), sha256=sha(body))
            # Serialize the grade in exactly the original writer format.
            stream = io.StringIO(newline='')
            writer = csv.DictWriter(stream, fieldnames=reader.FIELDS, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
            payloads['financial-cells.csv'] = stream.getvalue().encode()
            record = next(r for r in admission['files'] if r['path'] == 'financial-cells.csv')
            record.update(bytes=len(payloads['financial-cells.csv']), sha256=sha(payloads['financial-cells.csv']))
            adapter._write_part(destination / manifest['cells_part'], reader.FIELDS,
                lambda: (tuple(row[k] for k in reader.FIELDS) for row in rows))
            body = dump(admission)
            (destination / 'metadata/source-manifest.json').write_bytes(body)
            manifest.update(source_manifest_sha256=sha(body), source_files=admission['files'])
            digest = self.write_snapshot_manifest(destination, manifest)
            real = adapter._connection
            statements = []
            class ObservedConnection:
                def __init__(self, con): self.con = con
                def execute(self, sql, *args):
                    statements.append(sql)
                    if 'financial_numeric_' in sql or sql.startswith('CREATE VIEW'):
                        raise AssertionError('Numeric/public SQL before origin guard')
                    return self.con.execute(sql, *args)
                def close(self): self.con.close()
            with self.subTest(field=field), patch.object(adapter, '_connection', side_effect=lambda *a: ObservedConnection(real(*a))):
                with self.assertRaisesRegex(ValueError, 'provenance'):
                    public.snapshot_connection(destination, manifest_sha256=digest)
            self.assertTrue(any('financial_data' in sql for sql in statements))
            self.assertFalse(any('financial_numeric_' in sql or sql.startswith('CREATE VIEW') for sql in statements))

    def test_owned_images_and_partial_are_preserved(self):
        self.fixture.install()
        source, _, _, _ = self.admit()
        original = adapter._files
        def swap_source(*args):
            bodies = original(*args)
            (source / 'financial-cells.csv').write_bytes(b'changed after verification')
            return bodies
        with patch.object(adapter, '_files', side_effect=swap_source):
            destination, manifest = self.convert(source=source)
        def swap_part(*args):
            bodies = original(*args)
            (destination / manifest['cells_part']).write_bytes(b'changed after hash')
            return bodies
        with patch.object(adapter, '_files', side_effect=swap_part):
            con = public.snapshot_connection(destination, manifest_sha256=manifest['manifest_sha256'])
        self.addCleanup(con.close)
        before = [con.execute('FROM ' + b['view']).fetchall() for b in manifest['numeric_bindings']]
        for b in manifest['numeric_bindings']: (destination / b['path']).write_bytes(b'changed after query')
        self.assertEqual([con.execute('FROM ' + b['view']).fetchall() for b in manifest['numeric_bindings']], before)
        self.assertEqual(con.execute('SELECT count(*) FROM financial_cells').fetchone(), (36,))
        with self.assertRaises(Exception): con.execute('FROM read_csv(?)', [str(self.fixture.profile_path)])
        with self.assertRaises(FileExistsError): adapter.convert_financial(source, destination, source_manifest_sha256='0' * 64)
        new_source = self.admit('partial-source')[0]
        writer = adapter._write_part
        calls = 0
        def interrupt(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2: raise RuntimeError('synthetic interruption')
            return writer(*args, **kwargs)
        with patch.object(adapter, '_write_part', side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, 'synthetic interruption'): self.convert('partial', new_source)
        partial = self.root / 'partial'
        self.assertTrue((partial / manifest['cells_part']).exists())
        self.assertFalse((partial / 'manifest.json').exists())
        with self.assertRaises(FileExistsError): self.convert('partial', new_source)

    def test_replay_has_identical_all_payloads_and_exact_local_types(self):
        self.fixture.install()
        source = self.admit()[0]
        first, original = self.convert('first', source)
        with public.snapshot_connection(first, manifest_sha256=original['manifest_sha256']) as con:
            rows = con.execute('FROM financial_cells').fetchall()
        replay, repeated = self.convert('replay', source)
        self.assertEqual(original['files'], repeated['files'])
        self.assertEqual(original['numeric_bindings'], repeated['numeric_bindings'])
        for record in original['files']:
            self.assertEqual((first / record['path']).read_bytes(), (replay / record['path']).read_bytes())
        with public.snapshot_connection(replay, manifest_sha256=repeated['manifest_sha256']) as con:
            repeated_rows = con.execute('FROM financial_cells').fetchall()
            # Only two execution-manifest identities differ in these public rows.
            self.assertEqual([r[:32] + r[34:] for r in rows], [r[:32] + r[34:] for r in repeated_rows])

    def test_alternating_reports_and_summary_keep_defaults(self):
        from tests.test_financial_reports_parquet import FinancialReportsParquetTests
        from tests.test_financial_reports_202503 import Fixture202503
        from tests.test_financial import FinancialTests
        from tests.test_financial_202312 import Financial202312Tests
        self.fixture.install()
        old, summary24, summary23 = FinancialReportsParquetTests(), FinancialTests(), Financial202312Tests()
        for fixture in (old, summary24, summary23):
            fixture.setUp()
            self.addCleanup(fixture.doCleanups)
        root25 = self.root / 'fixture25'
        root25.mkdir()
        newer = Fixture202503(root25)
        constants = copy.deepcopy((reader.CONTRACT, reader.SELECTION, reader.FIELDS,
                                    financial.CONTRACT, financial.SELECTION, public.CONTRACT, public.FIELDS))
        with patch.object(reader, 'PROFILE_202503_PATH', newer.profile_path), patch.object(financial, 'PROFILE_PATH', summary24.profile_path):
            sequence = [(old.fixture.index, old.root), (self.fixture.index, self.root),
                        (newer.index, newer.root), (old.fixture.index, old.root),
                        (summary23.index, summary23.root), (summary24.index, summary24.root)]
            for i, (index, root) in enumerate(sequence):
                source, destination = root / ('alternating-' + str(i)), root / ('typed-' + str(i))
                admitted = financial.admit(index, source)
                result = public.convert_financial(source, destination,
                    source_manifest_sha256=sha((source / 'manifest.json').read_bytes()))
                self.assertEqual(result['selection'], admitted['selection'])
                self.assertEqual(public.validate_snapshot(destination, manifest_sha256=result['manifest_sha256']), result)
                with public.snapshot_connection(destination, manifest_sha256=result['manifest_sha256']) as con:
                    self.assertEqual(con.execute('SELECT count(*) FROM financial_cells').fetchone(), (admitted['cells'],))
            self.assertEqual(reader._context()['period'], 202412)
        self.assertEqual((reader.CONTRACT, reader.SELECTION, reader.FIELDS, financial.CONTRACT,
                          financial.SELECTION, public.CONTRACT, public.FIELDS), constants)


if __name__ == '__main__':
    unittest.main()

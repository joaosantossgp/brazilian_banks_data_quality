"""Catalog bridge against the real offline historical adapter fixtures.

Resolution is tested separately through authenticated Catalog objects. Here a
resolved fixture isolates forwarding, exact numbers, guard failures and closure.
"""
from decimal import Decimal, localcontext
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from bank_quality import financial_catalog as catalog
from bank_quality import financial_reports_parquet as adapter
from tests import test_financial_reports_historical_parquet as historical_fixtures


class CatalogAdapterBridgeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = historical_fixtures.HistoricalParquetTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.fixture.install()
        self.fixture.replace_numeric(b'123456789012345678901234567890123456789.0000000001')
        self.destination, self.manifest = self.fixture.convert()
        self.context = object()  # Only the already-resolved bridge input is stubbed.
        self.selection = self.manifest['selection']
        self.resolved = {'selection': self.selection, 'destination': self.destination,
                         'manifest_sha256': self.manifest['manifest_sha256'],
                         'revision_id': self.manifest['manifest_sha256'],
                         'counts': {k: self.manifest[k] for k in ('cells', 'observations', 'cadaster_records')},
                         'local_health': 'metadata_verified', 'payload_validation': 'not_run'}
        self.resolver = patch.object(catalog, 'resolve_snapshot', return_value=self.resolved).start()
        self.addCleanup(patch.stopall)
        self.selector = {'period': self.selection['period'], 'perspective': self.selection['perspective']}

    def operation(self, name):
        operation = getattr(catalog, name, None)
        self.assertTrue(callable(operation), f'Missing catalog adapter bridge: {name}')
        return operation

    def test_connection_delegates_complete_snapshot_and_preserves_native_cells(self):
        operation = self.operation('snapshot_connection')
        report = self.selection['reports'][0]
        con = operation(self.context, **self.selector, report_id=report)
        try:
            self.assertEqual(con.execute('SELECT count(*) FROM financial_cells').fetchone()[0], self.manifest['cells'])
            reports = {row[0] for row in con.execute('SELECT DISTINCT report_id FROM financial_cells').fetchall()}
            self.assertEqual(reports, {str(report) for report in self.selection['reports']})
        finally:
            con.close()
        self.resolver.assert_called_once_with(self.context, **self.selector, report_id=report, revision_id=None)

    def test_decimal_accessor_preserves_wide_value_and_native_none_with_small_context(self):
        operation = self.operation('iter_numeric_decimals')
        binding = next(b for b in self.manifest['numeric_bindings'] if b['encoding'] == 'decimal_text_v1')
        with localcontext() as context:
            context.prec = 3
            rows = list(operation(self.context, **self.selector, report_id=binding['report_id'], column_id=binding['column_id']))
        self.assertTrue(any(row['numeric_decimal'] == Decimal('123456789012345678901234567890123456789.0000000001') for row in rows))
        self.assertTrue(any(row['numeric_decimal'] is None for row in rows))
        self.assertTrue(all(row['report_id'] == binding['report_id'] and row['column_id'] == binding['column_id'] for row in rows))
        fitting = next(b for b in self.manifest['numeric_bindings'] if b['encoding'] == 'duckdb_decimal')
        fitting_rows = list(operation(self.context, **self.selector, report_id=fitting['report_id'], column_id=fitting['column_id']))
        self.assertTrue(any(row['numeric_decimal'] == Decimal('1e-27') for row in fitting_rows))

    def test_accessor_rejects_unknown_binding_before_opening_duckdb(self):
        operation = self.operation('iter_numeric_decimals')
        nonnumeric = [node for report in self.fixture.fixture.artifact['reports'] for node in report['nodes']
                      if node['kind'] not in ('money', 'numeric', 'quantity')]
        self.assertTrue(any(node['kind'] == 'group' for node in nonnumeric))
        self.assertTrue(any(node['kind'] != 'group' for node in nonnumeric))
        selectors = [(self.selection['reports'][0], 999999)] + [(n['report_id'], n['column_id']) for n in nonnumeric]
        for report, column in selectors:
            with self.subTest(report=report, column=column), patch.object(adapter, '_open_snapshot', side_effect=AssertionError('SQL before binding guard')):
                with self.assertRaises(catalog.CatalogError) as caught:
                    list(operation(self.context, **self.selector, report_id=report, column_id=column))
                self.assertEqual(caught.exception.code, 'unknown_binding')

    def test_accessor_closes_owned_native_connection_on_cancellation_and_is_lazy(self):
        operation = self.operation('iter_numeric_decimals')
        binding = self.manifest['numeric_bindings'][0]
        real_open = adapter._open_snapshot
        closed = []
        class OwnedConnection:
            def __init__(self, con): self.con = con
            def execute(self, *args): return self.con.execute(*args)
            def close(self): closed.append(True); self.con.close()
        def opened(*args, **kwargs):
            con, meta, validated = real_open(*args, **kwargs)
            return OwnedConnection(con), meta, validated
        with patch.object(adapter, '_open_snapshot', side_effect=opened) as spy:
            unused = operation(self.context, **self.selector, report_id=binding['report_id'], column_id=binding['column_id'])
            unused.close()
            self.assertEqual(spy.call_count, 0)
            iterator = operation(self.context, **self.selector, report_id=binding['report_id'], column_id=binding['column_id'])
            next(iterator)
            iterator.close()
        self.assertEqual(closed, [True])

    def test_adapter_integrity_failure_is_catalog_error(self):
        operation = self.operation('snapshot_connection')
        self.resolved['manifest_sha256'] = '0' * 64
        with self.assertRaises(catalog.CatalogError) as caught:
            operation(self.context, **self.selector)
        self.assertEqual(caught.exception.code, 'integrity')

    def fixture_cli(self, command, *extra):
        args = [command, '--catalog', 'fixture.json', '--catalog-sha256', 'a' * 64,
                '--period', str(self.selection['period']), '--perspective', str(self.selection['perspective']), *extra]
        with patch.object(catalog, 'load_catalog', return_value=self.context):
            return CatalogCliTests().invoke(args)

    def test_cli_counts_bindings_cells_use_real_adapter_and_parameterized_filters(self):
        status, counts = self.fixture_cli('counts')
        self.assertEqual(status, 0)
        self.assertEqual(counts['counts'], self.resolved['counts'])
        status, bindings = self.fixture_cli('bindings')
        self.assertEqual(status, 0)
        self.assertTrue(any(row['kind'] == 'group' for row in bindings['rows']))
        status, cells = self.fixture_cli('cells', '--limit', '2')
        self.assertEqual(status, 0); self.assertEqual(len(cells['rows']), 2); self.assertTrue(cells['truncated'])
        self.assertEqual(cells['payload_validation'], 'payload_verified')
        status, injected = self.fixture_cli('cells', '--institution', "1' OR 1=1 --")
        self.assertEqual(status, 0); self.assertEqual(injected['rows'], [])
        status, filtered = self.fixture_cli('counts', '--report', str(self.selection['reports'][0]))
        self.assertEqual(status, 0)
        self.assertGreater(filtered['counts']['cells'], 0)
        self.assertLess(filtered['counts']['cells'], counts['counts']['cells'])

    def test_cli_show_uses_only_metadata_and_decimals_uses_exact_native_accessor(self):
        with patch.object(adapter, '_open_snapshot', side_effect=AssertionError('DuckDB in show')):
            status, shown = self.fixture_cli('show')
        self.assertEqual(status, 0); self.assertEqual(shown['payload_validation'], 'not_run')
        binding = next(b for b in self.manifest['numeric_bindings'] if b['encoding'] == 'decimal_text_v1')
        status, decimals = self.fixture_cli('decimals', '--report', str(binding['report_id']),
                                          '--column', str(binding['column_id']))
        self.assertEqual(status, 0)
        self.assertTrue(any(row['numeric_decimal'] == '123456789012345678901234567890123456789.0000000001' for row in decimals['rows']))
        self.assertTrue(any(row['numeric_decimal'] is None for row in decimals['rows']))


class CatalogCliTests(unittest.TestCase):
    def cli(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/query-financial.py'
        self.assertTrue(path.is_file(), 'Missing financial catalog CLI')
        spec = importlib.util.spec_from_file_location('catalog_cli_test', path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def invoke(self, args):
        output = io.StringIO()
        with redirect_stdout(output):
            status = self.cli().main(args)
        return status, json.loads(output.getvalue())

    def test_bad_arguments_hash_missing_limit_and_no_arbitrary_sql_return_json(self):
        for args in [['list'], ['cells', '--catalog', 'c.json', '--catalog-sha256', 'a' * 64,
                      '--period', '202403', '--perspective', '1005', '--limit', '10001'],
                     ['list', '--catalog', 'c.json', '--catalog-sha256', 'a' * 64, '--sql', 'DROP TABLE x']]:
            with self.subTest(args=args), patch.object(catalog, 'load_catalog', side_effect=AssertionError('Load before argument guard')):
                status, body = self.invoke(args)
                self.assertEqual(status, 2)
                self.assertEqual(body['error']['code'], 'arguments')

    def test_error_codes_do_not_echo_exception_payloads(self):
        for code, expected in [('unavailable', 2), ('ambiguous_revision', 2), ('unknown_selection', 2),
                               ('unknown_binding', 2), ('integrity', 3), ('stale_context', 3), ('missing_local_artifact', 3)]:
            with self.subTest(code=code), patch.object(catalog, 'load_catalog', side_effect=catalog.CatalogError(code, 'PRIVATE-PAYLOAD')):
                status, body = self.invoke(['list', '--catalog', 'c.json', '--catalog-sha256', 'a' * 64])
                self.assertEqual(status, expected)
                self.assertEqual(body['error']['code'], code)
                self.assertNotIn('PRIVATE-PAYLOAD', json.dumps(body))

    def test_prepare_requires_external_input_pin_and_calls_authorized_destination(self):
        expected = {'catalog': {'path': 'data/runs/new/catalog.json', 'sha256': 'b' * 64}, 'coverage': {}}
        with patch.object(catalog, 'prepare_catalog', return_value=expected) as prepare:
            status, body = self.invoke(['catalog-prepare', '--inputs', 'input.json', '--inputs-sha256', 'a' * 64,
                                       '--output', 'data/runs/financial-catalog-new'])
        self.assertEqual(status, 0); self.assertEqual(body, expected)
        prepare.assert_called_once_with(Path('input.json'), Path('data/runs/financial-catalog-new'), inputs_sha256='a' * 64)

    def test_list_global_coverage_is_not_reduced_by_filters(self):
        rows = [{'selection': {'period': period, 'perspective': 1005, 'reports': [1, 3, 4, 5]},
                 'revisions': [], 'active_revision': None, 'acceptance': 'unavailable'} for period in (201003, 201006)]
        def discovered(context, **filters):
            return [row for row in rows if filters.get('period') in (None, row['selection']['period'])]
        with patch.object(catalog, 'load_catalog', return_value=object()), patch.object(catalog, 'discover', side_effect=discovered):
            status, body = self.invoke(['list', '--catalog', 'c.json', '--catalog-sha256', 'a' * 64, '--period', '201003'])
        self.assertEqual(status, 0)
        self.assertEqual(body['coverage']['offered'], 2)
        self.assertEqual(len(body['rows']), 1)

    def test_decimals_serializes_exact_strings_null_and_closes_at_limit(self):
        closed = []
        def values(*args, **kwargs):
            try:
                yield {'numeric_decimal': Decimal('123456789012345678901234567890.000100')}
                yield {'numeric_decimal': None}
                yield {'numeric_decimal': Decimal('9')}
            finally:
                closed.append(True)
        resolved = {'selection': {'period': 202403}, 'counts': {}, 'revision_id': 'b' * 64,
                    'local_health': 'metadata_verified', 'payload_validation': 'not_run'}
        with patch.object(catalog, 'load_catalog', return_value=object()), patch.object(catalog, 'resolve_snapshot', return_value=resolved), patch.object(catalog, 'iter_numeric_decimals', side_effect=values):
            status, body = self.invoke(['decimals', '--catalog', 'c.json', '--catalog-sha256', 'a' * 64,
                                       '--period', '202403', '--perspective', '1005', '--report', '1', '--column', '7', '--limit', '2'])
        self.assertEqual(status, 0)
        self.assertEqual(body['rows'], [{'numeric_decimal': '123456789012345678901234567890.000100'}, {'numeric_decimal': None}])
        self.assertEqual(closed, [True]); self.assertTrue(body['truncated'])
        self.assertEqual(body['payload_validation'], 'payload_verified')

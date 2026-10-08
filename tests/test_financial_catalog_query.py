"""Catalog bridge against the real offline historical adapter fixtures.

Resolution is tested separately through authenticated Catalog objects. Here a
resolved fixture isolates forwarding, exact numbers, guard failures and closure.
"""
from decimal import Decimal, localcontext
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
                         'manifest_sha256': self.manifest['manifest_sha256']}
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

"""Offline snapshot contracts, using real CSV/Parquet and Decimal values."""
import csv
from decimal import Decimal
import hashlib
import importlib
import importlib.util
import os
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor
from threading import Event

FIELDS = ['period', 'source_row', 'institution_id', 'report', 'account', 'variable', 'group',
          'raw_value', 'value_state', 'unit', 'source_mode', 'source_body', 'source_sha256',
          'csv_token', 'csv_body', 'csv_sha256']
COMPANIONS = ['institutions.csv', 'variables.csv', 'missingness.csv', 'structural-presence.csv', 'duplicates.csv', 'inventory.json']

def fixture(directory, tokens=None):
    directory.mkdir()
    tokens = tokens or [('9007199254740993.01', 'numeric'), ('1.1e-18', 'numeric'),
                        ('-12.30', 'numeric'), ('-0.00', 'zero'), ('NA', 'NA'), ('NI', 'NI'),
                        ('NA%', 'NA_percent'), ('NI%', 'NI_percent'), ('', 'blank'),
                        ('', 'json_null'), ('null', 'literal_null'), ('bad', 'invalid')]
    rows = []
    for index, (token, state) in enumerate(tokens, 1):
        rows.append(dict(zip(FIELDS, ['201012', str(index), '00123456', 'Resumo', f'a{index}',
                                    'Ativo Total', 'source', token, state, 'BRL_original',
                                    'official_portal_csv_fallback', 'body.bin', 'a' * 64,
                                    'display:' + token, 'export.bin', 'b' * 64])))
    with (directory / 'observations.csv').open('w', encoding='utf-8-sig', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    for name in COMPANIONS[:-1]:
        (directory / name).write_bytes(b'original,contract\r\n"00123456",unchanged\r\n')
    (directory / 'inventory.json').write_text(json.dumps({'quarters': {'201012': {'observations': len(rows), 'values_complete': True}}}), encoding='utf-8')
    return rows

class ExactParquetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'inventory'
        self.output = self.root / 'snapshot'

    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('bank_quality.parquet'), 'Offline Parquet converter is missing')
        return importlib.import_module('bank_quality.parquet')

    def test_exact_tokens_decimals_and_complementary_inventory(self):
        # Float coercion, null conflation, ID inference or dropped columns fail this test.
        rows = fixture(self.source)
        api = self.api()
        manifest = api.convert_inventory(self.source, self.output)
        with api.snapshot_connection(self.output) as connection:
            actual = connection.execute('SELECT ' + ','.join('"' + field + '"' for field in FIELDS) + ' FROM observations ORDER BY CAST(source_row AS BIGINT)').fetchall()
            self.assertEqual(actual, [tuple(row[field] for field in FIELDS) for row in rows])
            values = connection.execute('SELECT numeric_value FROM observations ORDER BY CAST(source_row AS BIGINT)').fetchall()
            self.assertEqual([value[0] for value in values], [Decimal('9007199254740993.01'), Decimal('1.1e-18'), Decimal('-12.30'), Decimal('-0.00')] + [None] * 8)
            self.assertEqual(connection.execute('SELECT DISTINCT perspective FROM observations').fetchall(), [('individual',)])
        self.assertEqual(manifest['observations'], len(rows))
        for name in COMPANIONS:
            self.assertEqual((self.output / 'metadata' / name).read_bytes(), (self.source / name).read_bytes())
        self.assertFalse(list(self.output.rglob('*.duckdb')))

    def test_decimal_limit_rejects_instead_of_rounding(self):
        fixture(self.source, [('1' + '0' * 37, 'numeric'), ('0.1', 'numeric')])
        with self.assertRaisesRegex(ValueError, '38|DECIMAL'):
            self.api().convert_inventory(self.source, self.output)
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_state_inconsistent_with_token_rejects_acceptance(self):
        fixture(self.source, [('NI', 'zero')])
        with self.assertRaisesRegex(ValueError, 'state|token'):
            self.api().convert_inventory(self.source, self.output)
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_idempotency_preserves_every_file_and_modification_time(self):
        fixture(self.source)
        api = self.api()
        first = api.convert_inventory(self.source, self.output)
        before = {p.relative_to(self.output).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.output.rglob('*') if p.is_file()}
        self.assertEqual(first, api.convert_inventory(self.source, self.output))
        after = {p.relative_to(self.output).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.output.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_different_source_cannot_replace_accepted_snapshot(self):
        fixture(self.source)
        api = self.api()
        api.convert_inventory(self.source, self.output)
        manifest = (self.output / 'manifest.json').read_bytes()
        with (self.source / 'institutions.csv').open('ab') as handle:
            handle.write(b'another,source\r\n')
        with self.assertRaisesRegex(ValueError, 'different|source|input'):
            api.convert_inventory(self.source, self.output)
        self.assertEqual(manifest, (self.output / 'manifest.json').read_bytes())

    def test_reserved_destination_is_not_accepted_or_overwritten(self):
        fixture(self.source)
        self.output.mkdir()
        sentinel = self.output / 'publication.lock'
        sentinel.write_text('another writer', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'reserved|incomplete|busy'):
            self.api().convert_inventory(self.source, self.output)
        self.assertEqual(sentinel.read_text(encoding='utf-8'), 'another writer')
        with self.assertRaisesRegex(ValueError, 'incomplete|manifest'):
            self.api().validate_snapshot(self.output)

    def test_rename_failure_retains_staging_without_acceptance(self):
        fixture(self.source)
        api = self.api()
        with patch('os.replace', side_effect=PermissionError('Windows open-file rename failure')):
            with self.assertRaises(PermissionError):
                api.convert_inventory(self.source, self.output)
        self.assertFalse((self.output / 'manifest.json').exists())
        self.assertTrue(list(self.output.rglob('*.parquet')))
        self.assertTrue((self.output / 'failure.json').exists())
        with self.assertRaisesRegex(ValueError, 'incomplete|manifest'):
            api.validate_snapshot(self.output)

    def test_modified_parquet_rejects_read_and_reuse(self):
        fixture(self.source)
        api = self.api()
        manifest = api.convert_inventory(self.source, self.output)
        part = self.output / manifest['parquet_files'][0]
        part.write_bytes(part.read_bytes() + b'corrupt')
        with self.assertRaisesRegex(ValueError, 'hash|size'):
            api.snapshot_connection(self.output)
        with self.assertRaisesRegex(ValueError, 'hash|size'):
            api.convert_inventory(self.source, self.output)

    def test_manifest_cannot_reference_external_or_unlisted_paths(self):
        fixture(self.source)
        api = self.api()
        manifest = api.convert_inventory(self.source, self.output)
        manifest['parquet_files'] = ['../outside.parquet']
        (self.output / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'path|list|file'):
            api.snapshot_connection(self.output)

    def test_manifest_count_tampering_is_rejected(self):
        fixture(self.source)
        api = self.api()
        manifest = api.convert_inventory(self.source, self.output)
        manifest['observations'] += 1
        (self.output / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'count|content'):
            api.validate_snapshot(self.output)

    def test_two_workers_preserve_the_same_complete_content(self):
        rows = fixture(self.source)
        second = [{**row, 'period': '202412'} for row in rows]
        with (self.source / 'observations.csv').open('a', encoding='utf-8', newline='') as handle:
            csv.DictWriter(handle, fieldnames=FIELDS).writerows(second)
        summary = {'quarters': {period: {'observations': len(rows), 'values_complete': True} for period in ('201012', '202412')}}
        (self.source / 'inventory.json').write_text(json.dumps(summary), encoding='utf-8')
        api = self.api()
        one = api.convert_inventory(self.source, self.output, workers=1)
        other = self.root / 'two-workers'
        two = api.convert_inventory(self.source, other, workers=2)
        with api.snapshot_connection(self.output) as a, api.snapshot_connection(other) as b:
            sql = 'SELECT * FROM observations ORDER BY period, CAST(source_row AS BIGINT)'
            self.assertEqual(a.execute(sql).fetchall(), b.execute(sql).fetchall())
        self.assertEqual(one['source_hashes'], two['source_hashes'])

    def test_cli_converts_offline_and_reports_invalid_worker(self):
        rows = fixture(self.source)
        command = [sys.executable, '-B', '-m', 'bank_quality', 'parquet', '--inventory', str(self.source), '--output', str(self.output), '--workers', '2']
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['observations'], len(rows))
        command[-1] = '3'
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(result.returncode, 0)

    def test_input_changed_during_conversion_is_not_accepted(self):
        fixture(self.source)
        api = self.api()
        write_part = api._write_part
        def modifying_write(*args):
            write_part(*args)
            with (self.source / 'institutions.csv').open('ab') as handle:
                handle.write(b'changed,during-conversion\r\n')
        with patch.object(api, '_write_part', side_effect=modifying_write):
            with self.assertRaisesRegex(ValueError, 'changed'):
                api.convert_inventory(self.source, self.output)
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_actual_concurrent_publisher_cannot_replace_active_writer(self):
        fixture(self.source)
        api = self.api()
        entered, release = Event(), Event()
        write_part = api._write_part
        def blocked_write(*args):
            entered.set()
            if not release.wait(10):
                raise TimeoutError('Test coordinator failed to release worker')
            return write_part(*args)
        with patch.object(api, '_write_part', side_effect=blocked_write), ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(api.convert_inventory, self.source, self.output)
            try:
                self.assertTrue(entered.wait(10))
                self.assertFalse((self.output / 'manifest.json').exists())
                with self.assertRaisesRegex(ValueError, 'reserved|busy|incomplete'):
                    api.convert_inventory(self.source, self.output)
            finally:
                release.set()
            self.assertEqual(future.result(timeout=10)['observations'], 12)
        self.assertEqual(api.validate_snapshot(self.output)['observations'], 12)

    def test_numeric_boundary_and_scientific_scale_remain_exact(self):
        # Independent valid profiles, not an impossible combined width >38.
        for token in ('9' * 38, '1.1e-24'):
            with self.subTest(token=token):
                source = self.root / ('source-' + str(len(token)))
                output = self.root / ('snapshot-' + str(len(token)))
                fixture(source, [(token, 'numeric')])
                self.api().convert_inventory(source, output)
                with self.api().snapshot_connection(output) as connection:
                    self.assertEqual(connection.execute('SELECT numeric_value FROM observations').fetchone()[0], Decimal(token))

    def test_benchmark_relative_output_and_resume_preserve_snapshot(self):
        # A path representation bug must not force replay or overwrite a valid snapshot.
        self.api()
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'benchmark_parquet.py'
        specification = importlib.util.spec_from_file_location('parquet_benchmark_test', script)
        benchmark = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(benchmark)
        source = self.root / 'data/derived/expansion-20261001/inventory'
        source.parent.mkdir(parents=True)
        rows = fixture(source)
        raw = self.root / 'data/raw'
        raw.mkdir()
        (raw / 'evidence.bin').write_bytes(b'immutable archived body')
        (source.parent / 'collection.json').write_text(json.dumps({'raw_directory': str(raw), 'quarters': {'201012': {}}}), encoding='utf-8')
        def offline_replay(_collection, destination):
            shutil.copytree(source, destination)
            return {'quarters': {'201012': {'observations': len(rows)}}}
        current = Path.cwd()
        try:
            os.chdir(self.root)
            with patch.object(benchmark, 'replay', side_effect=offline_replay):
                first = benchmark.run(self.root, Path('data/curated/measured'), self.root / 'report.json')
            self.assertEqual(first['observations'], 12)
            self.assertEqual(len(first['conversion_runs']), 2)
            active = self.root / first['active_snapshot']
            before = {p.relative_to(active).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns) for p in active.rglob('*') if p.is_file()}
            with patch.object(benchmark, 'replay', side_effect=AssertionError('Resume must verify archived replay without reexecuting')):
                second = benchmark.run(self.root, Path('data/curated/measured'), self.root / 'report-resume.json', resume=True)
            after = {p.relative_to(active).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns) for p in active.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            self.assertEqual(second['replay']['byte_identical_inventory_files'], 7)
            self.assertEqual(len(second['conversion_runs']), 2)
            original_convert = benchmark.convert_inventory
            def reuse_only(source, destination, **kwargs):
                self.assertEqual(destination, active, 'Finalization must not create new conversion runs')
                return original_convert(source, destination, **kwargs)
            with patch.object(benchmark, 'convert_inventory', side_effect=reuse_only):
                finalized = benchmark.run(self.root, Path('data/curated/measured'), self.root / 'report-finalized.json', resume=True, measurements=second['conversion_runs'])
            self.assertTrue(finalized['measurements_recovered_from_prior_completed_runs'])
            self.assertEqual(finalized['conversion_runs'], second['conversion_runs'])
        finally:
            os.chdir(current)

if __name__ == '__main__':
    unittest.main()

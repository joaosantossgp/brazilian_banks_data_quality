"""Independent synthetic fixtures for the closed financial Parquet adapter."""
from collections import Counter
import copy
import csv
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bank_quality.financial import CONTRACT as SOURCE_CONTRACT, FIELDS, PROFILE_PATH, SELECTION
from bank_quality.inventory import classify
from bank_quality.financial_parquet import convert_financial


def sha(body):
    return hashlib.sha256(body).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def csv_bytes(rows, fields):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode('utf-8')


class FinancialParquetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'admitted'
        self.source.mkdir()
        self.target = self.root / 'parquet'
        self.common = dict(contract=SOURCE_CONTRACT, period=202412, perspective='financial',
                           perspective_id=1005, report_id=92, report_generation='15/04/2026',
                           report_version='1', report_generation_state='reported_text',
                           report_version_state='reported_text')
        self.sources = {role: dict(body_path=role + '.bin', sha256=sha(role.encode()),
                                  manifest_sha256=sha((role + '-capture').encode()))
                        for role in ('catalog', 'cadaster', 'dictionary', 'portal', 'numeric')}
        self.cad = []
        for index, code in enumerate(('11111', '22222', '33333')):
            self.cad.append({**self.common, **{f'c{i}': '' for i in range(38)},
                             'c0': code, 'c1': '202412', 'c16': '0', 'c17': 'NI%',
                             'source_body': 'cadaster.bin', 'source_sha256': self.sources['cadaster']['sha256'],
                             'source_pointer': f'/{index}'})
        self.variables = []
        profile = json.loads(PROFILE_PATH.read_bytes())
        for index, metric in enumerate(profile['metrics']):
            info = metric['info']
            money = info['td'] == 3
            self.variables.append(dict(ifd=info['id'], td=info['td'], area=info['a'], lid=info['lid'],
                                       fid=metric['fid'], name=info['n'], definition=copy.deepcopy(info),
                                       catalog_pointer=f'/99/files/28/trel/c/{metric["position"]}',
                                       definition_pointer=f'/{455 + index}',
                                       unit='BRL_raw_inferred' if money else 'count',
                                       unit_basis='archived_formatter_divides_by_1000' if money else 'cadaster_definition',
                                       window_start='2024-07-01' if info['id'] == 79718 else '',
                                       window_end='2024-12-31',
                                       window_basis='report_rp_result_window' if info['id'] == 79718 else
                                       'stock_at_reference_inferred' if money else 'cadaster_reference'))
        tokens = iter(('9007199254740993.0100', '1.10e-18', '-0.00', 'NA%', 'NI', 'NA',
                       None, 'null', '', '123.00', 'NI%'))
        self.cells = []
        for vi, var in enumerate(self.variables):
            for ci, cad in enumerate(self.cad):
                role = 'numeric' if var['td'] == 3 else 'cadaster'
                presence = 'entity_not_stored' if role == 'numeric' and ci == 2 else 'stored'
                if role == 'numeric' and vi == 1 and ci == 0:
                    presence = 'information_not_stored'
                raw = next(tokens) if role == 'numeric' and presence == 'stored' else cad[f'c{var["lid"]}'] if role == 'cadaster' else ''
                state = classify(raw) if presence == 'stored' else 'unobserved_cell'
                kind = 'json_null' if raw is None else 'json_number' if state in ('numeric', 'zero') and role == 'numeric' else 'json_string'
                number = str(Decimal(raw)) if state in ('numeric', 'zero') else ''
                pointer = f'/values/{ci}/v/{vi}/v' if role == 'numeric' else f'/{ci}/c{var["lid"]}'
                if presence == 'entity_not_stored':
                    pointer = '/values'
                elif presence == 'information_not_stored':
                    pointer = f'/values/{ci}/v'
                self.cells.append({**self.common, **{k: var[k] for k in
                                   ('ifd', 'td', 'area', 'lid', 'fid', 'catalog_pointer', 'definition_pointer',
                                    'unit', 'unit_basis', 'window_start', 'window_end', 'window_basis')},
                                   'institution_id': cad['c0'], 'variable': var['name'], 'presence': presence,
                                   'raw_value': 'null' if raw is None else raw, 'value_state': state,
                                   'numeric_value': number, 'source_kind': kind if presence == 'stored' else 'not_stored',
                                   'source_role': role, 'source_body': self.sources[role]['body_path'],
                                   'source_sha256': self.sources[role]['sha256'], 'source_pointer': pointer})
        self.flush()

    def flush(self, *, observations=None):
        coverage = []
        for var in self.variables:
            rows = [c for c in self.cells if c['ifd'] == var['ifd']]
            counts = Counter(c['presence'] for c in rows)
            counts.update(c['value_state'] for c in rows if c['presence'] == 'stored')
            coverage.append(dict(ifd=var['ifd'], lid=var['lid'], td=var['td'],
                                 denominator_cadaster_records=len(self.cad), states=dict(counts)))
        self.diagnostics = dict(contract=SOURCE_CONTRACT, selection=dict(SELECTION),
                                cadaster_records=len(self.cad), shared_numeric_entities=2,
                                matched_cadaster_entities=2, numeric_entities_outside_selected_cadaster=0,
                                coverage=coverage, limitations=['Synthetic test, not observed financial data.'])
        stored = [c for c in self.cells if c['presence'] == 'stored']
        bodies = {'financial-cells.csv': csv_bytes(self.cells, FIELDS),
                  'financial-observations.csv': csv_bytes(stored if observations is None else observations, FIELDS),
                  'financial-cadastro.csv': csv_bytes(self.cad, list(self.cad[0])),
                  'financial-variables.json': json_bytes({**self.common, 'variables': self.variables}),
                  'financial-diagnostics.json': json_bytes(self.diagnostics)}
        self.manifest = {**self.common, 'accepted': True, 'selection': dict(SELECTION), 'sources': self.sources,
                         'profile_sha256': sha(PROFILE_PATH.read_bytes().replace(b'\r\n', b'\n')),
                         'observations': len(stored), 'cells': len(self.cells), 'cadaster_records': len(self.cad),
                         'limitations': self.diagnostics['limitations'],
                         'files': [dict(path=n, bytes=len(b), sha256=sha(b)) for n, b in bodies.items()]}
        for name, body in bodies.items():
            (self.source / name).write_bytes(body)
        self.rehash_manifest()

    def rehash_manifest(self):
        body = json_bytes(self.manifest)
        (self.source / 'manifest.json').write_bytes(body)
        self.expected_hash = sha(body)

    def convert(self, target=None):
        return convert_financial(self.source, target or self.target,
                                 source_manifest_sha256=self.expected_hash)

    def read_part(self):
        import duckdb
        with duckdb.connect(':memory:') as con:
            result = con.execute('FROM read_parquet(?, hive_partitioning=false)',
                                 [str(self.target / 'parts/financial-cells-202412.parquet')])
            names = [c[0] for c in result.description]
            return [dict(zip(names, row)) for row in result.fetchall()]

    def test_exact_decimal_and_markers(self):
        result = self.convert()
        rows = self.read_part()
        self.assertEqual(len(rows), 24)
        self.assertEqual(result['observations'], 17)
        self.assertEqual(result['cells'], 24)
        self.assertEqual(list(rows[0]), FIELDS + ['numeric_decimal'])
        self.assertEqual(rows[0]['numeric_decimal'], Decimal('9007199254740993.0100'))
        self.assertEqual(rows[1]['numeric_decimal'], Decimal('1.10e-18'))
        self.assertIn('-0.00', [r['raw_value'] for r in rows])
        for original, row in zip(self.cells, rows):
            self.assertEqual([row[f] for f in FIELDS], [str(original[f]) for f in FIELDS])
            expected = Decimal(original['raw_value']) if original['value_state'] in ('numeric', 'zero') else None
            self.assertEqual(row['numeric_decimal'], expected)
        self.assertEqual({r['value_state'] for r in rows},
                         {'numeric', 'zero', 'NA', 'NI', 'NA_percent', 'NI_percent', 'json_null',
                          'literal_null', 'blank', 'unobserved_cell'})
        saved = json.loads((self.target / 'manifest.json').read_bytes())
        self.assertNotIn('manifest_sha256', saved)
        self.assertEqual(result['manifest_sha256'], sha((self.target / 'manifest.json').read_bytes()))

    def test_input_hash_and_semantic_guards(self):
        with self.assertRaises(ValueError):
            convert_financial(self.source, self.target, source_manifest_sha256='0' * 64)
        (self.source / 'financial-cells.csv').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.convert()
        self.assertFalse(self.target.exists())

    def test_binding_scope_and_source_guards(self):
        mutations = [('period', 202503), ('source_sha256', '0'*64), ('source_kind', 'json_null'),
                     ('unit', 'BRL_thousands'), ('window_start', '2024-01-01'),
                     ('source_pointer', '/unrelated'), ('catalog_pointer', '/bad'),
                     ('numeric_value', '1'), ('value_state', 'zero')]
        original = copy.deepcopy(self.cells)
        for field, value in mutations:
            with self.subTest(field=field):
                self.cells = copy.deepcopy(original)
                self.cells[0][field] = value
                self.flush()
                with self.assertRaises(ValueError):
                    self.convert()
        self.assertFalse(self.target.exists())

    def test_literal_keys_and_grid(self):
        self.cells.append(copy.deepcopy(self.cells[0]))
        self.flush()
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.convert()
        self.cells.pop()
        self.cells.pop()
        self.flush()
        with self.assertRaises(ValueError):
            self.convert()
        self.cad[0]['c0'] = '011111'
        self.flush()
        with self.assertRaises(ValueError):
            self.convert()

    def test_projection_and_closed_manifest(self):
        self.flush(observations=[])
        with self.assertRaises(ValueError):
            self.convert()
        self.flush()
        self.manifest['files'][0]['path'] = '../escape.csv'
        self.rehash_manifest()
        with self.assertRaises(ValueError):
            self.convert()
        self.flush()
        self.manifest['selection']['period'] = 202503
        self.rehash_manifest()
        with self.assertRaises(ValueError):
            self.convert()

    def test_precision_overflow(self):
        for token in ('1e999999', '1e-999999', '123456789012345678901234567890123456789'):
            with self.subTest(token=token):
                self.cells[0].update(raw_value=token, numeric_value=str(Decimal(token)))
                self.flush()
                with self.assertRaisesRegex(ValueError, '38'):
                    self.convert()
        self.assertFalse(self.target.exists())

    def test_new_destination_and_final_marker(self):
        self.target.mkdir()
        (self.target / 'manifest.json').write_bytes(b'protected')
        with self.assertRaises(FileExistsError):
            self.convert()
        self.assertEqual((self.target / 'manifest.json').read_bytes(), b'protected')
        other = self.root / 'interrupted'
        with patch('bank_quality.financial_parquet.os.link', side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):
                self.convert(other)
        self.assertFalse((other / 'manifest.json').exists())

    def test_destination_race(self):
        def attempt():
            try:
                return self.convert()['accepted']
            except FileExistsError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(lambda _: attempt(), range(2))), [False, True])

    def test_duplicate_json_and_variable_definition(self):
        path = self.source / 'financial-variables.json'
        body = path.read_bytes().replace(b'"variables":', b'"variables": [], "variables":', 1)
        path.write_bytes(body)
        entry = next(f for f in self.manifest['files'] if f['path'] == path.name)
        entry.update(bytes=len(body), sha256=sha(body))
        self.rehash_manifest()
        with self.assertRaises(ValueError):
            self.convert()
        self.variables[0]['definition']['n'] = 'Altered'
        self.flush()
        with self.assertRaises(ValueError):
            self.convert()


if __name__ == '__main__':
    unittest.main()

"""Independent synthetic 202312 inputs and cross-period boundary regressions."""
import copy
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bank_quality.financial as financial
import bank_quality.financial_parquet as parquet

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / 'bank_quality/financial-profile-202412.json').read_bytes())
CAPTURE = 'Intercepted official response bytes before browser fulfillment'
DIAGNOSTIC = 'Playwright stores decoded response-body bytes'


def sha(body):
    return hashlib.sha256(body).hexdigest()


class Financial202312Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.report = copy.deepcopy(BASELINE['report'])
        self.report.update(ge='14/04/2025', v='1')
        cad = []
        for code in ('11111', '22222', '33333'):
            row = {f'c{i}': '' for i in range(32)}
            row.update(c0=code, c1='202312', c16='0', c17='NI%')
            cad.append(row)
        self.data = {
            'catalog': [{'dt': 202312, 'files': [
                {'f': 'ifdata/202312/cadastro202312_1005.json'},
                {'f': 'ifdata/202312/info202312.json'},
                {'f': 'ifdata/202312/dados202312_1.json'},
                {'sel': [{'id': 1005, 'n': 'Conglomerados Financeiros e Instituições Independentes'}]},
                {'trel': self.report}]}],
            'cadaster': cad,
            'dictionary': [m['info'] for m in BASELINE['metrics']],
            'portal': BASELINE['formatter_fragments'][0],
            'numeric': '{"id":1,"values":[{"e":11111,"v":['
                '{"i":78182,"v":9007199254740993.0100},{"i":78183,"v":1.10e-18},'
                '{"i":78184,"v":-0.00},{"i":78185,"v":"NA%"},'
                '{"i":78186,"v":null},{"i":78187,"v":"NI"}]},'
                '{"e":22222,"v":[{"i":78182,"v":7}]}]}'
        }
        self.manifests = {}
        for role, value in self.data.items():
            body = value.encode('utf-8') if isinstance(value, str) else json.dumps(value).encode('utf-8')
            (self.root / (role + '.bin')).write_bytes(body)
            url = 'https://www3.bcb.gov.br/ifdata/' + (
                'rest/relatorios2000a2024' if role == 'catalog' else 'index.html' if role == 'portal' else
                'rest/arquivos?nomeArquivo=ifdata%2F202312%2F' +
                {'cadaster': 'cadastro202312_1005.json', 'dictionary': 'info202312.json', 'numeric': 'dados202312_1.json'}[role])
            manifest = dict(url=url, final_url=url, method='GET', http_status=200, outcome='ok',
                            truncated=False, diagnostics=[], bytes=len(body), sha256=sha(body),
                            body_path=role + '.bin', retrieved_at_utc='2026-10-01T03:37:24.367Z',
                            context={'synthetic': True})
            if role in ('dictionary', 'numeric'):
                del manifest['truncated']
                manifest['diagnostics'] = [DIAGNOSTIC]
                manifest['context']['body_capture'] = CAPTURE
            path = self.root / (role + '.json')
            path.write_bytes(json.dumps(manifest).encode('utf-8'))
            self.manifests[role] = path
        self.profile = copy.deepcopy(BASELINE)
        self.profile['selection']['period'] = 202312
        self.profile['report'] = self.report
        self.profile['source_baseline']['portal_sha256'] = sha((self.root / 'portal.bin').read_bytes())
        self.profile['legacy_sources'] = {
            role: dict(body_sha256=sha((self.root / (role + '.bin')).read_bytes()),
                       manifest_sha256=sha(self.manifests[role].read_bytes()),
                       diagnostics=[DIAGNOSTIC], body_capture=CAPTURE)
            for role in ('dictionary', 'numeric')}
        self.profile_path = self.root / 'synthetic-profile.json'
        self.profile_path.write_bytes(json.dumps(self.profile).encode('utf-8'))
        self.index = self.root / 'index.json'
        self.index.write_bytes(json.dumps(dict(contract='ifdata-financial-sources-v1',
            selection={'period': 202312, 'perspective': 1005, 'report': 92},
            sources={r: p.name for r, p in self.manifests.items()})).encode('utf-8'))
        self.patch = patch.object(financial, 'PROFILE_202312_PATH', self.profile_path, create=True)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def admit(self, name='admitted'):
        path = self.root / name
        return path, financial.admit(self.index, path)

    def change_manifest(self, role, **changes):
        path = self.manifests[role]
        manifest = json.loads(path.read_bytes())
        manifest.update(changes)
        path.write_bytes(json.dumps(manifest).encode('utf-8'))

    def test_admit_native_schema_precision_and_window(self):
        source, result = self.admit()
        self.assertEqual(result['contract'], 'ifdata-financial-snapshot-202312-v1')
        self.assertEqual(result['selection']['period'], 202312)
        self.assertEqual(result['cells'], 24)
        self.assertEqual(result['observations'], 13)
        with (source / 'financial-cadastro.csv').open(encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.assertIn('c31', reader.fieldnames)
            self.assertNotIn('c32', reader.fieldnames)
            self.assertTrue(all(r['c1'] == '202312' for r in reader))
        with (source / 'financial-cells.csv').open(encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        values = {(r['institution_id'], r['ifd']): r for r in rows}
        self.assertEqual(values['11111', '78182']['raw_value'], '9007199254740993.0100')
        self.assertEqual(values['11111', '78183']['raw_value'], '1.10e-18')
        self.assertEqual(values['11111', '78184']['raw_value'], '-0.00')
        income = values['11111', '79718']
        self.assertEqual((income['lid'], income['window_start'], income['window_end']),
                         ('78187', '2023-07-01', '2023-12-31'))
        self.assertEqual(values['33333', '78182']['value_state'], 'unobserved_cell')
        self.assertEqual(result['sources']['numeric']['truncation_state'], 'undeclared_legacy')
        with self.assertRaises(FileExistsError):
            financial.admit(self.index, source)
        other, _ = self.admit('replay')
        for name in ('financial-cadastro.csv', 'financial-cells.csv', 'financial-observations.csv',
                     'financial-variables.json', 'financial-diagnostics.json'):
            self.assertEqual((source / name).read_bytes(), (other / name).read_bytes())

    def test_legacy_manifest_mutations_rejected(self):
        for role in ('dictionary', 'numeric'):
            original = self.manifests[role].read_bytes()
            for changes in ({'truncated': False, 'diagnostics': []}, {'context': {}}, {'retrieved_at_utc': '2026-10-02T00:00:00Z'}):
                with self.subTest(role=role, changes=changes):
                    self.change_manifest(role, **changes)
                    with self.assertRaisesRegex(ValueError, 'legacy'):
                        self.admit()
                    self.assertFalse((self.root / 'admitted').exists())
                    self.manifests[role].write_bytes(original)

    def test_legacy_body_change_with_recomputed_manifest_rejected(self):
        p = self.root / 'numeric.bin'
        body = p.read_bytes().replace(b'9007199254740993.0100', b'9007199254740993.0200')
        p.write_bytes(body)
        self.change_manifest('numeric', bytes=len(body), sha256=sha(body))
        with self.assertRaisesRegex(ValueError, 'legacy'):
            self.admit()

    def test_cadaster_padding_and_unknown_period_rejected(self):
        p = self.root / 'cadaster.bin'
        body = json.loads(p.read_bytes())
        body[0]['c32'] = ''
        encoded = json.dumps(body).encode('utf-8')
        p.write_bytes(encoded)
        self.change_manifest('cadaster', bytes=len(encoded), sha256=sha(encoded))
        with self.assertRaisesRegex(ValueError, 'cadaster schema'):
            self.admit()
        index = json.loads(self.index.read_bytes())
        index['selection']['period'] = 202503
        self.index.write_bytes(json.dumps(index).encode('utf-8'))
        with self.assertRaisesRegex(ValueError, 'scope|selection'):
            self.admit()

    def test_parquet_query_and_cross_period_guards(self):
        source, _ = self.admit()
        target = self.root / 'parquet'
        admitted_hash = sha((source / 'manifest.json').read_bytes())
        result = parquet.convert_financial(source, target, source_manifest_sha256=admitted_hash)
        self.assertEqual(result['contract'], 'ifdata-financial-parquet-202312-v1')
        self.assertTrue((target / 'parts/financial-cells-202312.parquet').exists())
        with parquet.snapshot_connection(target, manifest_sha256=result['manifest_sha256']) as con:
            self.assertEqual(con.execute('select count(*) from financial_cells').fetchone()[0], 24)
            self.assertEqual(con.execute('select count(*) from financial_observations').fetchone()[0], 13)
            token, exact = con.execute("select raw_value,numeric_decimal from financial_cells where institution_id='11111' and ifd='78182'").fetchone()
            self.assertEqual(token, '9007199254740993.0100')
            self.assertEqual(exact, Decimal(token))
        # Coherently relabeling selection does not turn a 2023 snapshot into2024.
        path = target / 'manifest.json'
        altered = json.loads(path.read_bytes())
        altered['selection']['period'] = 202412
        body = json.dumps(altered).encode('utf-8')
        path.write_bytes(body)
        with self.assertRaisesRegex(ValueError, 'contract|selection|scope'):
            parquet.validate_snapshot(target, manifest_sha256=sha(body))
        self.assertEqual(financial.SELECTION['period'], 202412)
        self.assertEqual(parquet.PART, 'parts/financial-cells-202412.parquet')

    def test_conversion_rejects_rewritten_legacy_qualification(self):
        source, _ = self.admit()
        path = source / 'manifest.json'
        manifest = json.loads(path.read_bytes())
        manifest['sources']['numeric']['truncation_state'] = 'observed_false'
        body = json.dumps(manifest).encode('utf-8')
        path.write_bytes(body)
        with self.assertRaisesRegex(ValueError, 'legacy'):
            parquet.convert_financial(source, self.root / 'rewritten', source_manifest_sha256=sha(body))

    def test_cadaster_column_order_is_canonical(self):
        path = self.root / 'cadaster.bin'
        records = json.loads(path.read_bytes())
        encoded = json.dumps([{k: r[k] for k in reversed(r)} for r in records]).encode('utf-8')
        path.write_bytes(encoded)
        self.change_manifest('cadaster', bytes=len(encoded), sha256=sha(encoded))
        source, _ = self.admit()
        with (source / 'financial-cadastro.csv').open(encoding='utf-8') as f:
            fields = csv.DictReader(f).fieldnames
        self.assertEqual([f for f in fields if f.startswith('c') and f[1:].isdigit()],
                         [f'c{i}' for i in range(32)])

    def test_writer_preserves_empty_fields_and_csv_punctuation(self):
        row = {k: '' for k in financial.FIELDS}
        row.update(raw_value='NI%', variable='Crédito, "exterior"\nsegunda linha',
                   institution_id='000-source-text', numeric_value='')
        target = self.root / 'punctuation.parquet'
        parquet._write_part([row], [None], 'DECIMAL(1,0)', target)
        with parquet._connection([self.root]) as con:
            actual = con.execute('FROM read_parquet(?)', [str(target)]).fetchone()
        self.assertEqual(actual, tuple(row[k] for k in financial.FIELDS) + (None,))


if __name__ == '__main__':
    unittest.main()

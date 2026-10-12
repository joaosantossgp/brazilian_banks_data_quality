"""Offline import checks: exact native values, provenance and fail-closed output."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ODataImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'input'
        self.root.mkdir()
        self.output = Path(self.tmp.name) / 'output'
        self.rows = [self.row('123456789012345678901234567890123456789.000000000100'),
                     self.row('null', group=None), self.row('0', group='other')]
        self.write_package()

    def row(self, saldo, group='group'):
        row = dict(TipoInstituicao=2, CodInst='C0001', AnoMes='201003',
                   NomeRelatorio='Resumo', NumeroRelatorio='1', Grupo=group,
                   Conta='00012', NomeColuna='Valor', DescricaoColuna='Saldo', Saldo='TOKEN')
        return json.dumps(row).replace('"TOKEN"', saldo)

    def write_package(self, context='https://was-p.bcnet.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata$metadata#_IfDataValores', status='ok'):
        body = '{"@odata.context":' + json.dumps(context) + ',"value":[' + ','.join(self.rows) + ']}'
        raw = gzip.compress(body.encode())
        (self.root / 'dados').mkdir(exist_ok=True)
        (self.root / 'dados/page.json.gz').write_bytes(raw)
        self.manifest = [dict(periodo=201003, tipo=2, status=status, registros=len(self.rows),
                             coleta_utc='2026-10-11T01:02:03Z', paginas=[dict(
                                 arquivo='dados\\page.json.gz', registros=len(self.rows),
                                 bytes_gzip=len(raw), sha256_gzip=hashlib.sha256(raw).hexdigest(),
                                 url='https://olinda.bcb.gov.br/odata/Valores?$filter=AnoMes%20eq%20201003')])]
        self.save_manifest()

    def save_manifest(self):
        (self.root / 'manifesto.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def api(self):
        from bank_quality import ifdata_odata
        return ifdata_odata

    def test_exact_values_native_ids_duplicate_keys_and_provenance(self):
        api = self.api()
        summary = api.import_package(self.root, self.output, periods=[201003], types=[2], reports=[1])
        self.assertEqual(summary['rows'], 3)
        with api.open_dataset(self.output) as conn:
            rows = conn.execute('select CodInst, Conta, Grupo, Saldo, source_row, source_url from ifdata order by source_row').fetchall()
            self.assertEqual(rows[0][:5], ('C0001', '00012', 'group', '123456789012345678901234567890123456789.000000000100', '1'))
            self.assertEqual(rows[1][2:5], (None, None, '2'))
            self.assertEqual(rows[2][2:5], ('other', '0', '3'))
            self.assertEqual(rows[0][5], self.manifest[0]['paginas'][0]['url'])
            self.assertEqual(conn.execute('describe ifdata').fetchall()[9][1], 'VARCHAR')
        self.assertEqual(api.saldo_decimal(rows[0][3]).as_tuple().exponent, -12)
        self.assertIsNone(api.saldo_decimal(None))

    def test_report_selection_keeps_native_report_number(self):
        self.rows.append(self.row('7').replace('"NumeroRelatorio": "1"', '"NumeroRelatorio": "2"'))
        self.write_package()
        summary = self.api().import_package(self.root, self.output, reports=['2'])
        self.assertEqual(summary['rows'], 1)
        with self.api().open_dataset(self.output) as conn:
            self.assertEqual(conn.execute('select NumeroRelatorio, Saldo from ifdata').fetchall(), [('2', '7')])

    def test_rejects_missing_requested_period_type_and_report(self):
        cases = [dict(periods=[201003, 201006]), dict(types=[2, 3]),
                 dict(reports=['1', '999']), dict(reports=['999'])]
        for i, selection in enumerate(cases):
            with self.subTest(selection=selection):
                target = self.output / str(i)
                with self.assertRaisesRegex(ValueError, 'Incomplete selection'):
                    self.api().import_package(self.root, target, **selection)
                self.assertFalse((target / 'manifest.json').exists())

    def test_requires_requested_period_type_combinations(self):
        # Both axes exist, but (201003, 3) and (201006, 2) do not.
        raw = gzip.decompress((self.root / 'dados/page.json.gz').read_bytes())
        raw = gzip.compress(raw.replace(b'201003', b'201006')
                            .replace(b'"TipoInstituicao": 2', b'"TipoInstituicao": 3'))
        (self.root / 'dados/second.json.gz').write_bytes(raw)
        page = dict(self.manifest[0]['paginas'][0], arquivo='dados/second.json.gz',
                    bytes_gzip=len(raw), sha256_gzip=hashlib.sha256(raw).hexdigest())
        entry = dict(self.manifest[0], periodo=201006, tipo=3, paginas=[page])
        self.manifest.append(entry)
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'Incomplete selection'):
            self.api().import_package(self.root, self.output,
                                      periods=[201003, 201006], types=[2, 3])
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_report_must_be_observed_in_each_nonempty_context(self):
        raw = gzip.compress(('{"@odata.context":' + json.dumps(
            'https://was-p.bcnet.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata$metadata#_IfDataValores')
            + ',"value":[' + self.row('7').replace('201003', '201006')
            .replace('"NumeroRelatorio": "1"', '"NumeroRelatorio": "2"') + ']}').encode())
        (self.root / 'dados/second.json.gz').write_bytes(raw)
        page = dict(self.manifest[0]['paginas'][0], arquivo='dados/second.json.gz',
                    registros=1, bytes_gzip=len(raw), sha256_gzip=hashlib.sha256(raw).hexdigest())
        self.manifest.append(dict(self.manifest[0], periodo=201006, registros=1, paginas=[page]))
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'Incomplete selection'):
            self.api().import_package(self.root, self.output, reports=['1', '2'])
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_authenticated_empty_source_is_not_missing_source(self):
        self.rows = []
        self.write_package(status='sem_dados')
        result = self.api().import_package(self.root, self.output, periods=[201003], types=[2])
        self.assertEqual(result['rows'], 0)
        with self.api().open_dataset(self.output) as conn:
            self.assertEqual(conn.execute('select count(*) from ifdata').fetchone()[0], 0)
        # An empty source cannot establish whether a report ID is offered.
        target = self.output.parent / 'unknown-report'
        with self.assertRaisesRegex(ValueError, 'Incomplete selection'):
            self.api().import_package(self.root, target, reports=['999'])
        self.assertFalse((target / 'manifest.json').exists())

    def test_empty_and_nul_strings_are_not_null(self):
        self.rows = [self.row('-0.000', group=''), self.row('1e-20', group='\x00')]
        self.write_package()
        self.api().import_package(self.root, self.output)
        with self.api().open_dataset(self.output) as conn:
            self.assertEqual(conn.execute('select Grupo, Saldo from ifdata order by source_row').fetchall(),
                             [('', '-0.000'), ('\x00', '1e-20')])

    def test_native_nullable_strings_preserved_without_dropping_rows(self):
        # Captured 201909 has CodInst=null. Edm.String properties also allow
        # null in labels; preserving these rows must not invent an identity.
        row = json.loads(self.row('null'))
        for field in ('CodInst', 'NomeRelatorio', 'Grupo', 'Conta',
                      'NomeColuna', 'DescricaoColuna'):
            row[field] = None
        self.rows = [json.dumps(row), self.row('0')]
        self.write_package()
        result = self.api().import_package(self.root, self.output)
        self.assertEqual(result['rows'], 2)
        with self.api().open_dataset(self.output) as conn:
            self.assertEqual(conn.execute(
                'select CodInst, NomeRelatorio, Grupo, Conta, NomeColuna, '
                'DescricaoColuna, Saldo from ifdata where source_row=\'1\'').fetchone(),
                (None,) * 7)
            self.assertEqual(conn.execute('select count(*) from ifdata').fetchone()[0], 2)

    def test_rejects_bad_hash_counts_context_schema_and_values(self):
        cases = ['hash', 'page_count', 'entry_count', 'size', 'context', 'period', 'type', 'saldo', 'missing', 'duplicate', 'nan', 'path', 'gzip']
        for case in cases:
            with self.subTest(case=case):
                self.rows = [self.row('1')]
                if case == 'period': self.rows = [self.rows[0].replace('201003', '201006')]
                if case == 'type': self.rows = [self.rows[0].replace('"TipoInstituicao": 2', '"TipoInstituicao": 3')]
                if case == 'saldo': self.rows = [self.row('"1.25"')]
                if case == 'missing': self.rows = [self.rows[0].replace('"CodInst": "C0001", ', '')]
                if case == 'duplicate': self.rows = [self.rows[0].replace('"Saldo":', '"Saldo": 2, "Saldo":')]
                if case == 'nan': self.rows = [self.row('NaN')]
                self.write_package(context='wrong' if case == 'context' else 'https://was-p.bcnet.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata$metadata#_IfDataValores')
                page = self.manifest[0]['paginas'][0]
                if case == 'hash': page['sha256_gzip'] = '0' * 64
                if case == 'size': page['bytes_gzip'] += 1
                if case == 'page_count': page['registros'] += 1
                if case == 'entry_count': self.manifest[0]['registros'] += 1
                if case == 'path': page['arquivo'] = '..\\outside.gz'
                if case == 'gzip':
                    raw = b'not gzip'
                    (self.root / 'dados/page.json.gz').write_bytes(raw)
                    page.update(bytes_gzip=len(raw), sha256_gzip=hashlib.sha256(raw).hexdigest())
                self.save_manifest()
                target = self.output / case
                with self.assertRaises(ValueError): self.api().import_package(self.root, target)
                self.assertFalse((target / 'manifest.json').exists())

    def test_existing_output_immutable_and_tampered_parquet_rejected(self):
        api = self.api()
        api.import_package(self.root, self.output)
        before = (self.output / 'manifest.json').read_bytes()
        with self.assertRaises(FileExistsError): api.import_package(self.root, self.output)
        self.assertEqual((self.output / 'manifest.json').read_bytes(), before)
        next(self.output.glob('*.parquet')).write_bytes(b'bad')
        with self.assertRaises(ValueError): api.open_dataset(self.output)

    def test_cli_import_counts_and_read_only_query(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/import-ifdata.py'
        def run(*args):
            return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)
        result = run('import', self.root, self.output, '--periods', '201003', '--types', '2', '--reports', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        result = run('counts', self.output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('201003', result.stdout)
        result = run('query', self.output, 'select count(*) as n from ifdata')
        self.assertEqual(json.loads(result.stdout), [{'n': 3}])
        result = run('query', self.output, 'create table nope as select * from ifdata')
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()

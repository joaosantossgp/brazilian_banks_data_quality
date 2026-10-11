import csv
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys


FIELDS = ('CodInst', 'Data', 'NomeInstituicao', 'DataInicioAtividade', 'Tcb',
          'Td', 'Tc', 'SegmentoTb', 'Atividade', 'Uf', 'Municipio', 'Sr',
          'CodConglomeradoFinanceiro', 'CodConglomeradoPrudencial',
          'CnpjInstituicaoLider', 'Situacao')
CONTEXT = 'https://was-p.bcnet.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata$metadata#_IfDataCadastro'


class CadastroTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'raw'
        (self.root / 'json').mkdir(parents=True)
        self.out = Path(self.temp.name) / 'output'
        self.row = dict.fromkeys(FIELDS)
        self.row.update(CodInst='00123456', Data='202412', NomeInstituicao='',
                        DataInicioAtividade=180001, Tc=2,
                        CodConglomeradoFinanceiro='C001',
                        CnpjInstituicaoLider='00123456')
        (self.root / 'resumo.json').write_text(json.dumps(dict(download_utc='2026-10-11T18:36:14Z')), encoding='utf-8')
        self.package([self.row])

    def package(self, rows, next_link=False):
        body = {'@odata.context': CONTEXT, 'value': rows}
        if next_link:
            body['@odata.nextLink'] = 'https://example.test/next'
        raw = json.dumps(body).encode()
        (self.root / 'json/202412.json').write_bytes(raw)
        with (self.root / 'indice_periodos.csv').open('w', newline='', encoding='utf-8-sig') as stream:
            writer = csv.DictWriter(stream, fieldnames=['periodo', 'registros', 'paginas', 'status', 'url', 'sha256_json'], delimiter=';')
            writer.writeheader()
            writer.writerow(dict(periodo='202412', registros=len(rows), paginas=1,
                                 status='disponivel', url='https://example.test/cadastro',
                                 sha256_json=hashlib.sha256(raw).hexdigest()))

    def api(self):
        return importlib.import_module('bank_quality.ifdata_cadastro')

    def test_preserves_codes_null_empty_and_declared_links(self):
        api = self.api()
        result = api.import_cadastro(self.root, self.out)
        self.assertEqual(result['rows'], 1)
        with api.open_cadastro(self.out) as conn:
            row = conn.execute('select CodInst, NomeInstituicao, Atividade, DataInicioAtividade, CnpjInstituicaoLider from cadastro').fetchone()
            self.assertEqual(row, ('00123456', '', None, '180001', '00123456'))
            self.assertEqual(conn.execute('select CodInst, Data, perspectiva, CodConglomerado from vinculos').fetchall(), [('00123456', '202412', 'financeiro', 'C001')])

    def test_rejects_hash_change_and_existing_output(self):
        api = self.api()
        api.import_cadastro(self.root, self.out)
        with self.assertRaises(FileExistsError):
            api.import_cadastro(self.root, self.out)
        (self.root / 'json/202412.json').write_text('{}')
        with self.assertRaises(ValueError):
            api.import_cadastro(self.root, self.out.parent / 'bad')

    def test_rejects_wrong_reference_schema_and_continuation(self):
        api = self.api()
        for change in ('period', 'schema', 'continuation'):
            with self.subTest(change=change):
                row = self.row.copy()
                if change == 'period':
                    row['Data'] = '202503'
                if change == 'schema':
                    del row['Situacao']
                self.package([row], change == 'continuation')
                with self.assertRaises(ValueError):
                    api.import_cadastro(self.root, self.out.parent / change)

    def test_rejects_duplicate_temporal_key_before_acceptance(self):
        api = self.api()
        self.package([self.row, self.row])
        with self.assertRaises(ValueError):
            api.import_cadastro(self.root, self.out)
        self.assertFalse((self.out / 'manifest.json').exists())

    def test_reader_rejects_changed_part(self):
        api = self.api()
        result = api.import_cadastro(self.root, self.out)
        part = self.out / result['files'][0]['file']
        part.write_bytes(part.read_bytes() + b'changed')
        with self.assertRaises(ValueError):
            api.open_cadastro(self.out)

    def test_temporal_join_preserves_rows_and_reports_unmatched_null_codes(self):
        import duckdb
        from bank_quality.ifdata_odata import CONTRACT
        api = self.api()
        api.import_cadastro(self.root, self.out)
        values = self.out.parent / 'values'
        values.mkdir()
        part = values / 'part.parquet'
        with duckdb.connect() as conn:
            conn.execute('create table v(CodInst varchar, AnoMes varchar, Saldo varchar)')
            conn.executemany('insert into v values (?, ?, ?)', [
                ('00123456', '202412', '1.00'),
                ('00123456', '202503', '2.00'),
                ('missing', '202412', None),
                (None, '202412', '0')])
            conn.execute('copy v to ? (format parquet)', [str(part)])
        (values / 'manifest.json').write_text(json.dumps(dict(
            contract=CONTRACT, rows=4, files=[dict(file=part.name,
                sha256=hashlib.sha256(part.read_bytes()).hexdigest())])), encoding='utf-8')
        result = api.audit_links(self.out, {'synthetic': values})
        self.assertEqual(sum(r['registros'] for r in result['coverage']), 4)
        self.assertEqual(sum(r['com_cadastro'] for r in result['coverage']), 1)
        self.assertEqual(sum(r['sem_cadastro'] for r in result['coverage']), 3)
        self.assertEqual(sum(r['codigo_ausente'] for r in result['coverage']), 1)
        with api.open_cadastro(self.out) as conn:
            api.attach_values(conn, values)
            self.assertEqual(conn.execute('select count(*) from ifdata_cadastrado').fetchone()[0], 4)
            self.assertEqual(conn.execute('select Saldo, cadastro_encontrado from ifdata_cadastrado where AnoMes = ?', ['202503']).fetchall(), [('2.00', False)])

    def test_cli_build_utf8_query_and_reject_write(self):
        self.row['NomeInstituicao'] = 'São Paulo — instituição'
        self.package([self.row])
        script = Path(__file__).resolve().parents[1] / 'scripts/import-ifdata-cadastro.py'
        def run(*args):
            return subprocess.run([sys.executable, str(script), *map(str, args)],
                                  capture_output=True, encoding='utf-8')
        built = run('build', self.root, self.out)
        self.assertEqual(built.returncode, 0, built.stderr)
        queried = run('query', self.out, 'select NomeInstituicao from cadastro')
        self.assertEqual(queried.returncode, 0, queried.stderr)
        self.assertEqual(json.loads(queried.stdout)[0]['NomeInstituicao'], self.row['NomeInstituicao'])
        self.assertEqual(run('query', self.out, 'create table bad(a int)').returncode, 1)

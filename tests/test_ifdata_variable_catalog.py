import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import duckdb

from bank_quality.ifdata_odata import COLUMNS, CONTRACT


class VariableCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.output = self.root / 'catalog'
        rows = []
        # A disappears in June and returns; an unchanged name is reused for B.
        for period, code, description, institution, balance in [
            ('201003', 'A', 'old definition', '001', '0.0'),
            ('201003', 'A', 'old definition', None, None),
            ('201006', 'OTHER', 'other', '001', '1'),
            ('201009', 'A', 'old definition', '001', '2'),
            ('202412', 'A', 'old definition', '001', '3'),
            ('202503', 'A', 'new definition', '001', '4'),
            ('202503', 'B', 'old definition', '001', '5'),
        ]:
            name = 'Other' if code == 'OTHER' else 'Same name'
            rows.append(('2', institution, period, 'Ativo', '2', None,
                         code, name, description, balance,
                         'source.gz', 'hash', 'https://example.org', '2026-01-01',
                         str(len(rows) + 1), 'context'))
        with duckdb.connect() as conn:
            conn.execute('create table source (' + ','.join(f'"{c}" varchar' for c in COLUMNS) + ')')
            conn.executemany('insert into source values (' + ','.join('?' for _ in COLUMNS) + ')', rows)
            conn.execute('copy source to ? (format parquet)', [str(self.source / 'part.parquet')])
        part = self.source / 'part.parquet'
        self.source_hash = hashlib.sha256(part.read_bytes()).hexdigest()
        (self.source / 'manifest.json').write_text(json.dumps(dict(
            contract=CONTRACT, rows=len(rows), files=[dict(file=part.name, sha256=self.source_hash)])), encoding='utf-8')

    def build(self):
        from bank_quality.ifdata_variable_catalog import build_catalog
        return build_catalog({'financial': self.source}, self.output)

    def query(self, sql):
        from bank_quality.ifdata_variable_catalog import query_catalog
        return query_catalog(self.output, sql)

    def test_coverage_preserves_null_and_zero_and_context(self):
        self.build()
        row = self.query("select * from cobertura_variaveis where AnoMes='201003'")[0]
        self.assertEqual((row['registros'], row['com_valor'], row['sem_valor']), (2, 1, 1))
        self.assertEqual((row['codigos_distintos'], row['codigo_ausente']), (1, 1))
        self.assertIsNone(row['Grupo'])
        self.assertEqual(hashlib.sha256((self.source / 'part.parquet').read_bytes()).hexdigest(), self.source_hash)

    def test_definition_changes_gaps_and_same_name_do_not_merge_codes(self):
        self.build()
        rows = self.query("select * from catalogo_variaveis where Conta='A' order by primeira_referencia")
        self.assertEqual(len(rows), 2)
        old = rows[0]
        self.assertEqual(old['periodos_sem_registro_entre_extremos'], ['201006'])
        self.assertEqual(old['variantes_no_contexto'], 2)
        self.assertEqual(old['codigos_com_mesmo_nome'], ['A', 'B'])
        self.assertEqual(old['periodos_2025_2026'], [])
        self.assertEqual(rows[1]['periodos_2010_2024'], [])
        self.assertEqual(old['comparabilidade'], 'nao_certificada')
        self.assertTrue((self.output / 'catalogo_variaveis.csv').is_file())
        self.assertTrue((self.output / 'cobertura_variaveis.csv').is_file())

    def test_authenticates_inputs_outputs_and_refuses_overwrite(self):
        self.build()
        with self.assertRaises(FileExistsError):
            self.build()
        part = self.output / 'catalogo_variaveis.parquet'
        part.write_bytes(part.read_bytes() + b'changed')
        with self.assertRaises(ValueError):
            self.query('select count(*) from catalogo_variaveis')

    def test_invalid_input_does_not_publish_catalog_manifest(self):
        (self.source / 'part.parquet').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.build()
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_query_rejects_incomplete_or_duplicate_inventory(self):
        self.build()
        path = self.output / 'manifest.json'
        manifest = json.loads(path.read_text(encoding='utf-8'))
        files = manifest['files']
        for inventory in [[], files[1:], files + [files[0]]]:
            with self.subTest(inventory=inventory):
                manifest['files'] = inventory
                path.write_text(json.dumps(manifest), encoding='utf-8')
                with self.assertRaises(ValueError):
                    self.query('select count(*) from cobertura_variaveis')


if __name__ == '__main__':
    unittest.main()

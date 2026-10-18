"""Presentation boundary: exact pinned macro data, no financial computation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import shutil
import subprocess

import duckdb

spec = importlib.util.spec_from_file_location('explorer_export', Path(__file__).resolve().parents[1] / 'scripts/export-ifdata-explorer.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class MacroPresentationTests(unittest.TestCase):
    def row(self, **changes):
        return dict(series='unemployment', variable='4099', category='total',
                    method='official_quarter', period='201203', unit='percent',
                    status='ok', value_fraction=['123456789012345678901', '10000000000000000000'],
                    source_count=1, expected_source_count=1, source_ids=['original'], **changes)

    def package(self, root, rows):
        con = duckdb.connect()
        con.execute('create table q(payload varchar)')
        for row in rows:
            con.execute('insert into q values (?)', [json.dumps(row)])
        con.execute('copy q to ? (format parquet)', [str(root/'quarterly.parquet')])
        con.close()
        manifest = dict(contract='macro-context-v1', files=[dict(file='quarterly.parquet', rows=len(rows), sha256=exporter.math._digest_file(root/'quarterly.parquet'))])
        (root/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        return exporter.math._digest_file(root/'manifest.json')

    def test_exact_payload_and_structural_gaps(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            row = self.row()
            pin = self.package(root, [row])
            result = exporter.presentation_macro(root, pin)
            self.assertEqual(result['rows'], [row])
            self.assertEqual(result['manifest'], pin)
            self.assertEqual(result['series'][0]['unit'], 'percent')
            self.assertEqual(result['series'][0]['key'], 'unemployment|4099|total|official_quarter')
            self.assertNotIn('201003', [r['period'] for r in result['rows']])

    def test_authentication_and_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); pin = self.package(root, [self.row(), self.row()])
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                exporter.presentation_macro(root, pin)
            with self.assertRaisesRegex(ValueError, 'hash'):
                exporter.presentation_macro(root, '0'*64)
            with (root/'quarterly.parquet').open('ab') as f:
                f.write(b'x')
            with self.assertRaisesRegex(ValueError, 'hash'):
                exporter.presentation_macro(root, pin)

    def test_invalid_fraction_unit_and_period_are_rejected(self):
        for change in [dict(value_fraction=['1','0']), dict(unit='DOUBLE'), dict(period='201201'), dict(status='ok',value_fraction=None)]:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as d:
                root=Path(d);row=self.row();row.update(change);pin=self.package(root,[row])
                with self.assertRaises(ValueError):
                    exporter.presentation_macro(root,pin)

    def test_fisher_and_selic_windows_are_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            rows=[]
            for method in ['fisher_three_months','fisher_twelve_months']:
                r=self.row();r.update(series='real_policy_rate_expost',variable='Fisher_Selic_IPCA',method=method,unit='percent_period');rows.append(r)
            root=Path(d);pin=self.package(root,rows);result=exporter.presentation_macro(root,pin)
            self.assertEqual(len(result['series']),2)
            self.assertIn('12 meses',result['series'][1]['label'])

    @unittest.skipUnless(shutil.which('node'), 'Node not installed')
    def test_browser_alignment_missingness_and_percent_scale(self):
        template=Path(exporter.__file__).with_name('ifdata-explorer-template.html').read_text(encoding='utf-8')
        code=template.split('</script><script>')[1].split('(async()=>{try{const bytes')[0]
        probe='''
const assert=require('node:assert/strict');
const row={series:'unemployment',variable:'4099',category:'total',method:'official_quarter',period:'201203',status:'ok',value_fraction:['62','10']};
const points=macroWindow({rows:[row]},'unemployment|4099|total|official_quarter',['201003','201203']);
assert.equal(points[0].row,null);assert.equal(points[1].row,row);
assert.equal(macroValue(row),6.2);assert.equal(macroFormat(macroValue(row),'percent'),'6,2%');
assert.equal(macroValue({...row,status:'not_observed'}),null);
assert.deepEqual(macroWindow(null,'none',['201003']),[{period:'201003',row:null}]);
assert.equal(fracNumber(divideFraction(['3','2'],['2','1'])),0.75);
console.log('Browser alignment, gaps, native percent scale and exact fractions PASS');
'''
        result=subprocess.run(['node','-'],input=code+probe,text=True,encoding='utf-8',capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__ == '__main__':
    unittest.main()

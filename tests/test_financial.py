"""Synthetic offline admission, precision and fail-closed boundary tests."""
import csv
import copy
import hashlib
import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / 'bank_quality/financial-profile-202412.json').read_text(encoding='utf-8'))


class FinancialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'accepted'
        cadastro = []
        for code in ('11111', '22222', '33333'):
            row = {f'c{i}': '' for i in range(38)}
            row.update(c0=code, c1='202412', c2='Synthetic ' + code, c4='I', c16='0', c17='NA')
            cadastro.append(row)
        report = PROFILE['report']
        self.data = {
            'catalog': [{'dt': 202412, 'files': [
                {'f': 'ifdata/202412/cadastro202412_1005.json'},
                {'f': 'ifdata/202412/info202412.json'},
                {'f': 'ifdata/202412/dados202412_1.json'},
                {'sel': [{'id': 1005, 'n': 'Conglomerados Financeiros e Instituições Independentes'}]},
                {'trel': report}]}],
            'cadaster': cadastro,
            'dictionary': [metric['info'] for metric in PROFILE['metrics']],
            'portal': PROFILE['formatter_fragments'][0],
            'numeric': '{"id":1,"values":[{"e":11111,"v":['
                '{"i":78182,"v":9007199254740993.0100},'
                '{"i":78183,"v":0},{"i":78184,"v":-0.00},'
                '{"i":78185,"v":1.10e-18},{"i":78186,"v":null},'
                '{"i":78187,"v":"NI"}]},'
                '{"e":22222,"v":[{"i":78182,"v":1},{"i":78183,"v":2},'
                '{"i":78184,"v":3},{"i":78185,"v":4},{"i":78186,"v":""}]},'
                '{"e":99999,"v":[{"i":78182,"v":99}]}]}'
        }
        self.write_sources()
        # Synthetic portal asset only; production CLI always uses its installed profile.
        fixture_profile = copy.deepcopy(PROFILE)
        fixture_profile['source_baseline']['portal_sha256'] = hashlib.sha256((self.root / 'portal.bin').read_bytes()).hexdigest()
        self.profile_path = self.root / 'profile.json'
        self.profile_path.write_text(json.dumps(fixture_profile), encoding='utf-8')

    def write_sources(self):
        names = {'catalog': 'relatorios2000a2024', 'cadaster': 'cadastro202412_1005.json',
                 'dictionary': 'info202412.json', 'numeric': 'dados202412_1.json', 'portal': 'index.html'}
        self.manifests = {}
        for role, value in self.data.items():
            body = value.encode('utf-8') if isinstance(value, str) else json.dumps(value, ensure_ascii=False).encode('utf-8')
            filename = role + '.bin'
            (self.root / filename).write_bytes(body)
            if role == 'catalog': url = 'https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024'
            elif role == 'portal': url = 'https://www3.bcb.gov.br/ifdata/index.html'
            else: url = 'https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2F' + names[role]
            manifest = {'url': url, 'final_url': url, 'method': 'GET', 'http_status': 200,
                        'outcome': 'ok', 'truncated': False, 'diagnostics': [],
                        'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(), 'body_path': filename,
                        'retrieved_at_utc': '2026-10-03T00:00:00+00:00', 'context': {'synthetic': True}}
            path = self.root / (role + '.manifest.json')
            path.write_text(json.dumps(manifest), encoding='utf-8')
            self.manifests[role] = path
        self.index = self.root / 'index.json'
        self.index.write_text(json.dumps({'contract': 'ifdata-financial-sources-v1', 'selection': PROFILE['selection'],
                                         'sources': {role: path.name for role, path in self.manifests.items()}}), encoding='utf-8')

    def admit(self, destination=None):
        try:
            module = importlib.import_module('bank_quality.financial')
        except ModuleNotFoundError:
            self.fail('Financial admission is not implemented')
        with patch.object(module, 'PROFILE_PATH', self.profile_path, create=True):
            return module.admit(self.index, destination or self.output)

    def cli(self, destination):
        launcher = ('import sys,runpy; from pathlib import Path; sys.path.insert(0,sys.argv[1]); '
                    'import bank_quality.financial as f; f.PROFILE_PATH=Path(sys.argv[2]); '
                    'script=sys.argv[3]; sys.argv=[script]+sys.argv[4:]; '
                    'runpy.run_path(script,run_name="__main__")')
        return subprocess.run([sys.executable, '-B', '-c', launcher, str(ROOT), str(self.profile_path),
                               str(ROOT / 'scripts/admit-financial.py'), '--index', str(self.index),
                               '--output', str(destination)], cwd=self.root, text=True, capture_output=True)

    def rows(self, name):
        with (self.output / name).open(encoding='utf-8', newline='') as source:
            return list(csv.DictReader(source))

    def test_native_precision_lid_presence_and_source_types(self):
        result = self.admit()
        values = {(r['institution_id'], r['ifd']): r for r in self.rows('financial-observations.csv')}
        self.assertEqual(values['11111', '78182']['raw_value'], '9007199254740993.0100')
        self.assertEqual(values['11111', '78182']['numeric_value'], '9007199254740993.0100')
        self.assertEqual(values['11111', '78185']['raw_value'], '1.10e-18')
        self.assertEqual(values['11111', '78184']['raw_value'], '-0.00')
        self.assertEqual(values['11111', '78184']['value_state'], 'zero')
        self.assertEqual(values['11111', '79718']['lid'], '78187')
        self.assertEqual(values['11111', '79718']['value_state'], 'NI')
        self.assertEqual(values['11111', '78186']['value_state'], 'json_null')
        self.assertEqual(values['22222', '78186']['value_state'], 'blank')
        self.assertEqual(values['11111', '79704']['source_kind'], 'json_string')
        self.assertEqual(values['11111', '78182']['source_kind'], 'json_number')
        self.assertEqual(values['11111', '79718']['source_pointer'], '/values/0/v/5/v')
        self.assertNotIn(('99999', '78182'), values)
        cells = {(r['institution_id'], r['ifd']): r for r in self.rows('financial-cells.csv')}
        self.assertEqual(cells['22222', '79718']['presence'], 'information_not_stored')
        self.assertEqual(cells['33333', '78182']['presence'], 'entity_not_stored')
        self.assertEqual(cells['33333', '78182']['value_state'], 'unobserved_cell')
        self.assertEqual(result['observations'], 17)
        self.assertEqual(result['cells'], 24)
        self.assertEqual(result['perspective'], 'financial')
        self.assertEqual(result['selection'], PROFILE['selection'])
        self.assertTrue((self.output / 'manifest.json').exists())
        self.assertFalse((self.output / 'observations.csv').exists())
        self.assertFalse((self.output / 'inventory.json').exists())

    def test_replay_outputs_identical_and_existing_destination_preserved(self):
        first = self.admit()
        second_dir = self.root / 'replay'
        second = self.admit(second_dir)
        self.assertEqual(first['files'], second['files'])
        for entry in first['files']:
            self.assertEqual((self.output / entry['path']).read_bytes(), (second_dir / entry['path']).read_bytes())
        original = (self.output / 'manifest.json').read_bytes()
        with self.assertRaises(FileExistsError): self.admit()
        self.assertEqual(original, (self.output / 'manifest.json').read_bytes())

    def test_tampered_source_fails_without_acceptance(self):
        (self.root / 'numeric.bin').write_bytes(b'{}')
        with self.assertRaises(ValueError): self.admit()
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_wrong_scope_and_changed_definition_rejected(self):
        original = copy.deepcopy(self.data)
        for mutation in ('period', 'definition', 'formatter', 'reference'):
            with self.subTest(mutation=mutation):
                self.data = copy.deepcopy(original)
                self.write_sources()
                if mutation == 'period':
                    index = json.loads(self.index.read_text()); index['selection']['period'] = 202503
                    self.index.write_text(json.dumps(index))
                elif mutation == 'definition':
                    d = json.loads(json.dumps(self.data['dictionary'])); d[0]['d'] = 'changed concept'
                    self.data['dictionary'] = d; self.write_sources()
                elif mutation == 'formatter':
                    self.data['portal'] = 'changed formatter'; self.write_sources()
                else:
                    d = json.loads(json.dumps(self.data['cadaster'])); d[0]['c1'] = '202503'
                    self.data['cadaster'] = d; self.write_sources()
                with self.assertRaises(ValueError): self.admit()
                self.assertFalse((self.output / 'manifest.json').exists())

    def test_duplicate_entities_cells_json_keys_and_cadaster_rejected(self):
        original = self.data['numeric']
        for body in ('{"id":1,"id":1,"values":[]}',
                     '{"id":1,"values":[{"e":11111,"v":[]},{"e":11111,"v":[]}]}',
                     '{"id":1,"values":[{"e":11111,"v":[{"i":78182,"v":1},{"i":78182,"v":2}]}]}',
                     '{"id":1,"values":[{"e":11111,"v":[{"i":78182,"v":NaN}]}]}'):
            with self.subTest(body=body):
                self.data['numeric'] = body; self.write_sources()
                with self.assertRaises(ValueError): self.admit()
                self.assertFalse((self.output / 'manifest.json').exists())
        self.data['numeric'] = original
        self.data['cadaster'].append(self.data['cadaster'][0]); self.write_sources()
        with self.assertRaises(ValueError): self.admit()

    def test_failed_manifest_missing_input_and_path_escape_rejected(self):
        for change in ('status', 'truncated', 'missing', 'escape'):
            with self.subTest(change=change):
                self.write_sources()
                path = self.manifests['numeric']; manifest = json.loads(path.read_text())
                if change == 'status': manifest['http_status'] = 500
                elif change == 'truncated': manifest['truncated'] = True
                elif change == 'escape': manifest['body_path'] = '../outside.bin'
                else: (self.root / 'numeric.bin').unlink()
                path.write_text(json.dumps(manifest))
                with self.assertRaises((ValueError, FileNotFoundError)): self.admit()
                self.assertFalse((self.output / 'manifest.json').exists())

    def test_padding_collision_and_invalid_selected_value_rejected(self):
        self.data['cadaster'][0]['c0'] = '011111'; self.write_sources()
        with self.assertRaises(ValueError): self.admit()
        self.data['cadaster'][0]['c0'] = '11111'
        self.data['numeric'] = '{"id":1,"values":[{"e":11111,"v":[{"i":78182,"v":true}]}]}'
        self.write_sources()
        with self.assertRaises(ValueError): self.admit()

    def test_cli_from_other_directory_has_no_network_and_keeps_errors_visible(self):
        process = self.cli(self.output)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)['observations'], 17)
        again = self.cli(self.output)
        self.assertNotEqual(again.returncode, 0)
        self.assertIn('exist', again.stderr.lower())

    def test_changed_portal_with_commented_approved_fragment_is_rejected(self):
        self.data['portal'] = '/* ' + PROFILE['formatter_fragments'][0] + ' */ function getTdClass(){return value/1000000;}'
        self.write_sources()
        with self.assertRaises(ValueError): self.admit()
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_malformed_selector_has_explicit_cli_error(self):
        self.data['catalog'][0]['files'][3]['sel'] = None
        self.write_sources()
        process = self.cli(self.output)
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertIn('selector', process.stderr.lower())
        self.assertNotIn('Traceback', process.stderr)
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_partial_manifest_write_never_publishes_acceptance(self):
        module = importlib.import_module('bank_quality.financial')
        original = module._write_json
        def interrupted(path, value):
            if 'manifest' in path.name:
                path.write_text('{"accepted":true,', encoding='utf-8')
                raise OSError('synthetic interrupted write')
            return original(path, value)
        with patch.object(module, '_write_json', side_effect=interrupted):
            with self.assertRaises(OSError): self.admit()
        self.assertTrue((self.output / 'financial-observations.csv').exists())
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_returned_metadata_cannot_change_closed_scope(self):
        module = importlib.import_module('bank_quality.financial')
        self.addCleanup(importlib.reload, module)
        first = self.admit()
        first['selection']['period'] = 202503
        try:
            second = self.admit(self.root / 'second')
        except ValueError as error:
            self.fail('Returned metadata altered the closed reader scope: ' + str(error))
        self.assertEqual(second['selection']['period'], 202412)

    def test_missing_generation_explicit_and_markers_preserved(self):
        self.data['numeric'] = '{"id":1,"values":[{"e":11111,"v":[{"i":78182,"v":"null"},{"i":78183,"v":"NA"},{"i":78184,"v":"NI%"}]}]}'
        self.write_sources()
        result = self.admit()
        self.assertEqual(result.get('report_generation_state'), 'unknown')
        values = {r['ifd']: r for r in self.rows('financial-observations.csv') if r['institution_id'] == '11111'}
        self.assertEqual(values['78182']['value_state'], 'literal_null')
        self.assertEqual(values['78183']['value_state'], 'NA')
        self.assertEqual(values['78184']['value_state'], 'NI_percent')

    def test_duplicate_definition_wrong_area_and_noninteger_identifiers(self):
        original = copy.deepcopy(self.data)
        cases = ('definition', 'area', 'float_entity', 'missing_value')
        for case in cases:
            with self.subTest(case=case):
                self.data = copy.deepcopy(original)
                if case == 'definition': self.data['dictionary'].append(self.data['dictionary'][0])
                elif case == 'area': self.data['numeric'] = '{"id":2,"values":[]}'
                elif case == 'float_entity': self.data['numeric'] = '{"id":1,"values":[{"e":11111.0,"v":[]}]}'
                else: self.data['numeric'] = '{"id":1,"values":[{"e":11111,"v":[{"i":78182}]}]}'
                self.write_sources()
                with self.assertRaises(ValueError): self.admit()
                self.assertFalse((self.output / 'manifest.json').exists())


if __name__ == '__main__':
    unittest.main()

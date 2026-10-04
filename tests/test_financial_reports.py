"""Independent synthetic fixtures for the closed four-report admission."""
import copy
import csv
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SELECTION = {'period': 202412, 'perspective': 1005, 'reports': [92, 96, 101, 98]}


def sha(body):
    return hashlib.sha256(body).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


class FinancialReportsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / 'accepted'
        self.profile_path = self.root / 'profile.json'
        self.infos = [
            {'id': 10, 'td': 1, 'a': 1, 'lid': 0, 'ty': 0, 'n': 'Code', 'd': 'Opaque'},
            {'id': 11, 'td': 1, 'a': 1, 'lid': 2, 'ty': 0, 'n': 'Name', 'd': 'Literal'},
            {'id': 12, 'td': 1, 'a': 1, 'lid': 1, 'ty': 0, 'n': 'Date', 'd': 'Literal'},
            {'id': 13, 'td': 1, 'a': 1, 'lid': 16, 'ty': 0, 'n': 'Quantity', 'd': 'Count'},
            {'id': 20, 'td': 3, 'a': 1, 'lid': 700, 'ty': 1, 'n': 'Stock', 'd': '[x]-[y]'},
            {'id': 21, 'td': 3, 'a': 1, 'lid': 701, 'ty': 1, 'n': 'Income', 'd': 'Suspect = opaquely retained'},
            {'id': 22, 'td': 3, 'a': 1, 'lid': 700, 'ty': 1, 'n': 'Repeated localizer', 'd': 'No dedup'},
            {'id': 30, 'td': 2, 'a': 1, 'lid': -1, 'ty': 0, 'n': 'Group', 'd': ''}]
        def col(cid, ifd, fid, children=None):
            return {'id': cid, 'ifd': ifd, 'fid': fid, 'sc': children or [], 'nac': 'opaque();', 'nc': True}
        self.reports = []
        for rid in SELECTION['reports']:
            columns = [col(rid*10, 10, 9), col(rid*10+1, 11, 8), col(rid*10+2, 12, 14)]
            if rid == 92:
                columns.extend([col(923, 13, 2), col(924, 20, 13), col(925, 21, 13)])
            else:
                columns.append(col(rid*10+3, 30, 4, [col(rid*10+4, 22, 13), col(rid*10+5, 21, 13)]))
            self.reports.append({'id': rid, 'n': str(rid), 's': [{'id': 1005}], 'c': columns,
                                 'rp': ['Native notes; July-December'], 'ge': '15/04/2026', 'v': '1', 'cp': 'R$ mil'})
        cadastro = []
        for code in ('111', '222', '333', '00111'):
            row = {f'c{i}': '' for i in range(38)}
            row.update(c0=code, c1='202412', c2='Synthetic', c3='n4', c16='0002')
            cadastro.append(row)
        self.data = {
            'catalog': [{'dt': 202412, 'files': [
                {'f': 'ifdata/202412/cadastro202412_1005.json'},
                {'f': 'ifdata/202412/info202412.json'}, {'f': 'ifdata/202412/dados202412_1.json'},
                {'sel': [{'id': 1005, 'n': 'Conglomerados Financeiros e Instituições Independentes'}]},
                *({'trel': report} for report in self.reports)]}],
            'dictionary': self.infos, 'cadaster': cadastro, 'portal': 'formatter opaque metadata',
            'numeric': '{"id":1,"values":[{"e":111,"v":[{"i":700,"v":9007199254740993.0100},'
                       '{"i":701,"v":1e-27}]},{"e":222,"v":[{"i":700,"v":-0.00}]}]}'
        }
        self.write_sources()
        self.make_profile()

    def write_sources(self):
        self.pins = {}
        self.sources = {}
        names = {'dictionary': 'info202412.json', 'numeric': 'dados202412_1.json',
                 'cadaster': 'cadastro202412_1005.json'}
        for role, value in self.data.items():
            body = value.encode() if isinstance(value, str) else json.dumps(value, ensure_ascii=False).encode()
            (self.root / (role + '.bin')).write_bytes(body)
            url = ('https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024' if role == 'catalog' else
                   'https://www3.bcb.gov.br/ifdata/index.html' if role == 'portal' else
                   'https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata%2F202412%2F' + names[role])
            manifest = {'method': 'GET', 'url': url, 'final_url': url, 'http_status': 200, 'outcome': 'ok',
                        'truncated': False, 'diagnostics': [], 'bytes': len(body), 'sha256': sha(body),
                        'body_path': role + '.bin', 'retrieved_at_utc': '2026-10-03T00:00:00+00:00',
                        'context': {'synthetic': True, 'perspective': 1006 if role in ('dictionary', 'numeric') else 1005}}
            manifest_body = json.dumps(manifest).encode()
            (self.root / (role + '.manifest.json')).write_bytes(manifest_body)
            record = {k: manifest[k] for k in ('url', 'final_url', 'retrieved_at_utc', 'bytes', 'sha256', 'body_path', 'context')}
            record.update(manifest_sha256=sha(manifest_body), source_generation_state='unknown')
            self.sources[role] = record
            self.pins[role] = {'body_sha256': sha(body), 'manifest_sha256': sha(manifest_body),
                               'provenance_sha256': sha(canonical(record).encode())}
        self.index = self.root / 'index.json'
        self.index.write_text(json.dumps({'contract': 'ifdata-financial-reports-sources-v1', 'selection': SELECTION,
                                         'sources': {r: r + '.manifest.json' for r in self.data}}), encoding='utf-8')

    def make_profile(self):
        reports = []
        infos = {i['id']: (p, i) for p, i in enumerate(self.infos)}
        for pos, report in enumerate(self.reports):
            pointer = f'/0/files/{pos+4}/trel'
            nodes = []
            def walk(columns, base, parent=None):
                for p, column in enumerate(columns):
                    ptr = base + '/' + str(p)
                    dpos, info = infos[column['ifd']]
                    group = bool(column['sc'])
                    kind = 'group' if group else 'money' if info['td'] == 3 else 'quantity' if column['fid'] == 2 else 'attribute'
                    flow = kind == 'money' and (report['id'] == 98 or info['id'] == 21 and report['id'] == 92)
                    nodes.append({'report_id': report['id'], 'column_id': column['id'], 'ifd': info['id'],
                                  'td': info['td'], 'area': info['a'], 'lid': info['lid'], 'fid': column['fid'],
                                  'name': info['n'], 'definition': copy.deepcopy(info), 'catalog_pointer': ptr,
                                  'definition_pointer': '/' + str(dpos), 'parent_pointer': parent,
                                  'children_pointers': [ptr + '/sc/' + str(n) for n in range(len(column['sc']))],
                                  'kind': kind, 'unit': '' if group else 'BRL_raw_inferred' if kind == 'money' else 'count' if kind == 'quantity' else 'text',
                                  'unit_basis': '' if group else 'archived_formatter_divides_by_1000' if kind == 'money' else 'cadaster_definition',
                                  'window_start': '2024-07-01' if flow else '',
                                  'window_end': '' if group else '2024-12-31',
                                  'window_basis': '' if group else 'report_rp_result_window' if flow else 'stock_at_reference_inferred' if kind == 'money' else 'cadaster_reference'})
                    walk(column['sc'], ptr + '/sc', ptr)
            walk(report['c'], pointer + '/c')
            reports.append({'report': copy.deepcopy(report), 'catalog_pointer': pointer, 'nodes': nodes})
        self.profile = {'contract': 'ifdata-financial-reports-profile-202412-v1', 'selection': SELECTION,
                        'cadaster_fields': 38, 'source_pins': self.pins, 'reports': reports}
        self.save_profile()

    def save_profile(self):
        self.profile_path.write_text(json.dumps(self.profile, ensure_ascii=False), encoding='utf-8')

    def module(self):
        try:
            return importlib.import_module('bank_quality.financial_reports')
        except ModuleNotFoundError:
            self.fail('Four-report admission API is missing')

    def admit(self, output=None):
        with patch.object(self.module(), 'PROFILE_PATH', self.profile_path):
            return self.module().admit(self.index, output or self.output)

    def rows(self, name):
        with (self.output / name).open(encoding='utf-8', newline='') as source:
            return list(csv.DictReader(source))

    def test_public_admission_dispatches_only_the_closed_index(self):
        from bank_quality import financial
        with patch.object(self.module(), 'PROFILE_PATH', self.profile_path):
            result = financial.admit(self.index, self.output)
        self.assertEqual(result['contract'], self.module().CONTRACT)
        self.assertEqual(result['selection'], SELECTION)
        self.assertEqual(result['cells'], 84)
        self.assertEqual(result['files'], self.admit(self.root / 'direct')['files'])

    def test_public_admission_rejects_unknown_malformed_and_wrong_selection(self):
        from bank_quality import financial
        original = json.loads(self.index.read_bytes())
        cases = [[], {**original, 'contract': 'ifdata-financial-reports-sources-2025-v1'},
                 {**original, 'selection': {**SELECTION, 'period': 202503}},
                 {**original, 'selection': {**SELECTION, 'reports': [92]}}]
        with patch.object(self.module(), 'PROFILE_PATH', self.profile_path):
            for position, value in enumerate(cases):
                with self.subTest(value=value):
                    self.index.write_text(json.dumps(value), encoding='utf-8')
                    destination = self.root / ('rejected-' + str(position))
                    with self.assertRaises(ValueError):
                        financial.admit(self.index, destination)
                    self.assertFalse(destination.exists())

    def test_complete_grade_bindings_groups_precision_attributes_and_windows(self):
        manifest = self.admit()
        cells = self.rows('financial-cells.csv')
        values = {(r['report_id'], r['institution_id'], r['ifd']): r for r in cells}
        self.assertEqual(manifest['cells'], 84)
        self.assertEqual(manifest['observations'], 64)
        self.assertEqual(manifest['selection'], SELECTION)
        self.assertEqual(manifest['cadaster_records'], 4)
        money = values['92', '111', '20']
        self.assertEqual(money['raw_value'], '9007199254740993.0100')
        self.assertEqual(money['numeric_value'], money['raw_value'])
        self.assertEqual(values['92', '111', '21']['raw_value'], '1e-27')
        self.assertEqual(values['92', '111', '21']['numeric_value'], '1E-27')
        self.assertEqual(values['96', '222', '22']['raw_value'], '-0.00')
        self.assertEqual(values['96', '222', '22']['value_state'], 'zero')
        self.assertEqual(values['92', '111', '10']['numeric_value'], '')
        self.assertEqual(values['92', '111', '10']['value_state'], 'text')
        self.assertEqual(values['92', '111', '12']['value_state'], 'text')
        self.assertEqual(values['92', '111', '13']['raw_value'], '0002')
        self.assertEqual(values['92', '111', '13']['numeric_value'], '2')
        self.assertEqual(values['92', '00111', '20']['presence'], 'entity_not_stored')
        self.assertEqual(values['92', '222', '21']['presence'], 'information_not_stored')
        self.assertEqual(money['window_start'], '')
        self.assertEqual(values['98', '111', '22']['window_start'], '2024-07-01')
        self.assertEqual(values['92', '111', '21']['window_start'], '2024-07-01')
        self.assertEqual(values['96', '111', '21']['window_start'], '')
        self.assertEqual(values['96', '111', '22']['source_pointer'], money['source_pointer'])
        document = json.loads((self.output / 'financial-variables.json').read_text())
        self.assertEqual(len(document['nodes']), 24)
        self.assertEqual(len(document['variables']), 21)
        self.assertEqual(sum(n['kind'] == 'group' for n in document['nodes']), 3)
        self.assertNotIn('report_id', self.rows('financial-cadastro.csv')[0])
        self.assertEqual(manifest['sources']['dictionary']['context']['perspective'], 1006)

    def test_native_markers_strings_empty_null_and_invalid_are_distinct(self):
        for token, state, kind in [('"NA"', 'NA', 'json_string'), ('"NI"', 'NI', 'json_string'),
                                   ('null', 'json_null', 'json_null'), ('"null"', 'literal_null', 'json_string'),
                                   ('""', 'empty', 'json_string'), ('"oops"', 'invalid', 'json_string'),
                                   ('"1.20"', 'numeric', 'json_string'), ('0', 'zero', 'json_number')]:
            with self.subTest(token=token):
                self.data['numeric'] = '{"id":1,"values":[{"e":111,"v":[{"i":700,"v":' + token + '}]}]}'
                self.write_sources(); self.profile['source_pins'] = self.pins; self.save_profile()
                self.admit(self.root / ('result-' + state))
                with (self.root / ('result-' + state) / 'financial-cells.csv').open() as stream:
                    row = next(r for r in csv.DictReader(stream) if r['report_id'] == '92' and r['ifd'] == '20' and r['institution_id'] == '111')
                self.assertEqual(row['value_state'], state)
                self.assertEqual(row['source_kind'], kind)

    def test_replay_hashes_and_existing_destination(self):
        first = self.admit()
        second = self.admit(self.root / 'replay')
        self.assertEqual(first['files'], second['files'])
        with self.assertRaises(FileExistsError): self.admit()

    def test_returned_metadata_does_not_mutate_the_closed_context(self):
        first = self.admit()
        first['selection']['reports'].clear()
        first['limitations'].clear()
        try:
            second = self.admit(self.root / 'independent')
        except ValueError as error:
            self.fail('Returned metadata corrupted the next closed context: ' + str(error))
        self.assertEqual(second['selection'], {'period': 202412, 'perspective': 1005, 'reports': [92, 96, 101, 98]})
        self.assertTrue(second['limitations'])

    def test_provenance_projection_pin_and_missing_source(self):
        role = 'dictionary'
        path = self.root / (role + '.manifest.json')
        manifest = json.loads(path.read_text()); manifest['context']['perspective'] = 1005
        path.write_text(json.dumps(manifest))
        self.profile['source_pins'][role]['manifest_sha256'] = sha(path.read_bytes())
        self.save_profile()
        with self.assertRaises(ValueError): self.admit()
        self.write_sources(); self.profile['source_pins'] = self.pins; self.save_profile()
        (self.root / 'numeric.manifest.json').unlink()
        with self.assertRaises(FileNotFoundError): self.admit()
        self.assertFalse(self.output.exists())

    def test_interrupted_write_never_accepts_a_partial_snapshot(self):
        module = self.module()
        write = module.legacy._write_json
        def interrupt(path, value):
            if path.name == '.manifest.pending':
                raise OSError('Synthetic interrupted marker')
            return write(path, value)
        with patch.object(module.legacy, '_write_json', side_effect=interrupt):
            with self.assertRaises(OSError): self.admit()
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_installed_profile_is_metadata_only_and_has_full_official_tree(self):
        profile = json.loads((ROOT / 'bank_quality/financial-reports-profile-202412.json').read_text(encoding='utf-8'))
        nodes = [node for report in profile['reports'] for node in report['nodes']]
        self.assertEqual(len(nodes), 121)
        self.assertEqual(sum(n['kind'] == 'group' for n in nodes), 9)
        self.assertEqual(sum(n['kind'] == 'money' for n in nodes), 74)
        self.assertEqual(sum(n['kind'] == 'quantity' for n in nodes), 2)
        self.assertEqual(sum(n['kind'] == 'attribute' for n in nodes), 36)
        self.assertEqual(profile['selection'], {'period': 202412, 'perspective': 1005, 'reports': [92, 96, 101, 98]})
        for pin in profile['source_pins'].values():
            self.assertEqual(set(pin), {'body_sha256', 'manifest_sha256', 'provenance_sha256'})
        self.assertNotIn('cadaster', profile)
        self.assertNotIn('values', profile)

    def test_fractional_metadata_preserves_number_type_and_lexeme_without_float(self):
        for report in self.data['catalog'][0]['files'][4:]:
            report['trel']['cot'] = 'fixture-number-lexeme'
        self.write_sources()
        path = self.root / 'catalog.bin'
        path.write_bytes(path.read_bytes().replace(b'"fixture-number-lexeme"', b'1.2300e-2'))
        manifest_path = self.root / 'catalog.manifest.json'
        manifest = json.loads(manifest_path.read_bytes())
        manifest.update(bytes=len(path.read_bytes()), sha256=sha(path.read_bytes()))
        manifest_path.write_text(json.dumps(manifest))
        record = copy.deepcopy(self.sources['catalog'])
        record.update(bytes=manifest['bytes'], sha256=manifest['sha256'], manifest_sha256=sha(manifest_path.read_bytes()))
        self.profile['source_pins']['catalog'] = {'body_sha256': record['sha256'], 'manifest_sha256': record['manifest_sha256'],
                                                 'provenance_sha256': sha(canonical(record).encode())}
        for item in self.profile['reports']:
            item['report']['cot'] = {'json_number': '1.2300e-2'}
        self.save_profile()
        try:
            self.admit()
        except ValueError as error:
            self.fail('Native fractional metadata was lost: ' + str(error))
        document = json.loads((self.output / 'financial-variables.json').read_bytes())
        self.assertEqual(document['reports'][0]['report']['cot'], {'json_number': '1.2300e-2'})

    def test_every_source_pin_and_complete_provenance_are_checked(self):
        for role in self.data:
            for change in ('body', 'context', 'utc', 'url'):
                with self.subTest(role=role, change=change):
                    self.write_sources()
                    path = self.root / (role + '.manifest.json')
                    manifest = json.loads(path.read_text())
                    if change == 'body': (self.root / (role + '.bin')).write_bytes(b'changed')
                    elif change == 'context': manifest['context']['perspective'] = 9999
                    elif change == 'utc': manifest['retrieved_at_utc'] = '2026-10-04T00:00:00+00:00'
                    else: manifest['url'] += '&extra=1'
                    if change != 'body': path.write_text(json.dumps(manifest))
                    with self.assertRaises(ValueError): self.admit()
        self.assertFalse(self.output.exists())

    def test_index_scope_membership_and_local_paths(self):
        original = json.loads(self.index.read_text())
        for mutation in ('period', 'reports', 'missing', 'absolute', 'profile_override', 'contract'):
            with self.subTest(mutation=mutation):
                index = copy.deepcopy(original)
                if mutation == 'period': index['selection']['period'] = 202503
                elif mutation == 'reports': index['selection']['reports'].reverse()
                elif mutation == 'missing': del index['sources']['numeric']
                elif mutation == 'absolute': index['sources']['numeric'] = str((self.root / 'numeric.manifest.json').resolve())
                elif mutation == 'profile_override': index['profile'] = str(self.profile_path)
                else: index['contract'] = 'ifdata-financial-sources-v1'
                self.index.write_text(json.dumps(index))
                with self.assertRaises(ValueError): self.admit()

    def test_semantic_source_mutations_rejected_even_with_matching_fixture_pins(self):
        original = copy.deepcopy(self.data)
        for mutation in ('schema', 'reference', 'duplicate_code', 'tree', 'dictionary', 'selector', 'numeric_schema', 'duplicate_entity', 'duplicate_lid', 'duplicate_json', 'id_string'):
            with self.subTest(mutation=mutation):
                self.data = copy.deepcopy(original)
                if mutation == 'schema': del self.data['cadaster'][0]['c37']
                elif mutation == 'reference': self.data['cadaster'][0]['c1'] = '202503'
                elif mutation == 'duplicate_code': self.data['cadaster'][1]['c0'] = '111'
                elif mutation == 'tree': self.data['catalog'][0]['files'][5]['trel']['c'][3]['sc'] = []
                elif mutation == 'dictionary': self.data['dictionary'][0]['d'] = 'changed'
                elif mutation == 'selector': self.data['catalog'][0]['files'][3]['sel'] = None
                elif mutation == 'numeric_schema': self.data['numeric'] = '{"id":2,"values":[]}'
                elif mutation == 'duplicate_entity': self.data['numeric'] = '{"id":1,"values":[{"e":111,"v":[]},{"e":111,"v":[]}]}'
                elif mutation == 'duplicate_lid': self.data['numeric'] = '{"id":1,"values":[{"e":111,"v":[{"i":700,"v":0},{"i":700,"v":1}]}]}'
                elif mutation == 'duplicate_json': self.data['numeric'] = '{"id":1,"id":1,"values":[]}'
                else: self.data['numeric'] = '{"id":1,"values":[{"e":"111","v":[]}]}'
                self.write_sources(); self.profile['source_pins'] = self.pins; self.save_profile()
                with self.assertRaises(ValueError): self.admit()

    def test_validated_admission_reconstruction_and_tamper_detection(self):
        manifest = self.admit()
        bodies = {entry['path']: (self.output / entry['path']).read_bytes() for entry in manifest['files']}
        with patch.object(self.module(), 'PROFILE_PATH', self.profile_path):
            accepted = self.module().validate_admission(manifest, bodies)
            self.assertEqual(len(accepted['cells']), manifest['cells'])
            for mutation in ('provenance', 'variables', 'row', 'count', 'extra', 'cadaster'):
                with self.subTest(mutation=mutation):
                    candidate = copy.deepcopy(manifest); changed = copy.deepcopy(bodies)
                    if mutation == 'provenance': candidate['sources']['dictionary']['context']['perspective'] = 1005
                    elif mutation == 'count': candidate['observations'] += 1
                    elif mutation == 'extra': changed['extra.csv'] = b'bad'
                    elif mutation == 'variables':
                        doc = json.loads(changed['financial-variables.json']); doc['nodes'][0]['definition']['d'] = 'changed'
                        changed['financial-variables.json'] = json.dumps(doc).encode()
                    elif mutation == 'cadaster': changed['financial-cadastro.csv'] = changed['financial-cadastro.csv'].replace(b'Synthetic', b'Altered', 1)
                    else: changed['financial-cells.csv'] = changed['financial-cells.csv'].replace(b'9007199254740993.0100', b'9007199254740993.0200', 1)
                    for entry in candidate['files']:
                        entry.update(bytes=len(changed[entry['path']]), sha256=sha(changed[entry['path']]))
                    with self.assertRaises(ValueError): self.module().validate_admission(candidate, changed)

    def test_admitted_numeric_pointer_cannot_identify_two_localizers(self):
        manifest = self.admit()
        bodies = {e['path']: (self.output / e['path']).read_bytes() for e in manifest['files']}
        for name in ('financial-cells.csv', 'financial-observations.csv'):
            bodies[name] = bodies[name].replace(b'/values/0/v/1/v', b'/values/0/v/0/v')
        for entry in manifest['files']:
            entry.update(bytes=len(bodies[entry['path']]), sha256=sha(bodies[entry['path']]))
        with patch.object(self.module(), 'PROFILE_PATH', self.profile_path):
            with self.assertRaises(ValueError): self.module().validate_admission(manifest, bodies)

    def test_numeric_source_pointer_array_indexes_are_canonical(self):
        # Keep entity index 1 present with an empty information array, so its
        # nonzero absence pointer is validated independently of stored cells.
        self.data['numeric'] = self.data['numeric'].replace(
            '{"e":222,"v":[{"i":700,"v":-0.00}]}', '{"e":222,"v":[]}')
        self.write_sources(); self.profile['source_pins'] = self.pins; self.save_profile()
        manifest = self.admit()
        bodies = {e['path']: (self.output / e['path']).read_bytes() for e in manifest['files']}
        with patch.object(self.module(), 'PROFILE_PATH', self.profile_path):
            valid = self.module().validate_admission(manifest, bodies)
            self.assertTrue(any(r['source_pointer'] == '/values/0/v/0/v' for r in valid['cells']))
            self.assertTrue(any(r['source_pointer'] == '/values/0/v/1/v' for r in valid['cells']))
            self.assertTrue(any(r['source_pointer'] == '/values/1/v' for r in valid['cells']))
            for original, padded in ((b'/values/0/', b'/values/00/'),
                                     (b'/values/0/v/1/v', b'/values/0/v/01/v'),
                                     (b'/values/1/v', b'/values/01/v')):
                with self.subTest(pointer=padded):
                    changed = {name: body.replace(original, padded) for name, body in bodies.items()}
                    candidate = copy.deepcopy(manifest)
                    for entry in candidate['files']:
                        entry.update(bytes=len(changed[entry['path']]), sha256=sha(changed[entry['path']]))
                    with self.assertRaisesRegex(ValueError, 'source pointer'):
                        self.module().validate_admission(candidate, changed)


if __name__ == '__main__':
    unittest.main()

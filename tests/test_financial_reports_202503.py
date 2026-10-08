"""Independent small native202503 fixtures; no network or production corpus."""
import copy
import csv
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

from bank_quality import financial, financial_parquet, financial_reports as reader
from bank_quality import financial_reports_parquet as adapter

ROOT = Path(__file__).resolve().parents[1]
SELECTION = {'period': 202503, 'perspective': 1005, 'reports': [119, 107, 110, 118]}


def sha(body):
    return hashlib.sha256(body).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


class Fixture202503:
    def __init__(self, root):
        self.root = root
        self.profile_path = root / 'profile.json'
        self.index = root / 'index.json'
        self.definitions = [
            {'id': 10, 'td': 1, 'a': 1, 'lid': 0, 'ty': 0, 'n': 'Code', 'd': 'Opaque'},
            {'id': 11, 'td': 1, 'a': 1, 'lid': 32, 'ty': 0, 'n': 'SR2025', 'd': 'Native namespace'},
            {'id': 12, 'td': 1, 'a': 1, 'lid': 16, 'ty': 1, 'n': 'Quantity', 'd': 'Count'},
            {'id': 20, 'td': 3, 'a': 1, 'lid': 700, 'ty': 1, 'n': 'Stock', 'd': '[x]-[y]'},
            {'id': 21, 'td': 3, 'a': 1, 'lid': 701, 'ty': 1, 'n': 'Tiny', 'd': 'Opaque formula'},
            {'id': 22, 'td': 3, 'a': 1, 'lid': 702, 'ty': 1, 'n': 'Markers', 'd': 'Native'},
            {'id': 79859, 'td': 3, 'a': 1, 'lid': 141870, 'ty': 1, 'n': 'Income', 'd': 'No annualization'},
            {'id': 30, 'td': 2, 'a': 1, 'lid': -1, 'ty': 0, 'n': 'Group', 'd': ''}]
        self.reports = []
        def column(cid, ifd, fid, children=None):
            return {'id': cid, 'ifd': ifd, 'fid': fid, 'sc': children or [], 'nac': 'opaque()', 'nc': True}
        for rid in SELECTION['reports']:
            columns = [column(rid * 10, 10, 9), column(rid * 10 + 1, 11, 9)]
            if rid == 119:
                columns.append(column(rid * 10 + 2, 12, 2))
            columns.append(column(rid * 10 + 3, 30, 4,
                [column(rid * 10 + 4 + p, ifd, 13) for p, ifd in enumerate((20, 21, 22, 79859))]))
            self.reports.append({'id': rid, 'n': str(rid), 's': [{'id': 1005}], 'c': columns,
                'rp': ['Resultado janeiro–março'], 'ge': '17/04/2026', 'v': '1', 'cp': 'R$ mil',
                'cot': {'json_number': '1.2300e-2'}})
        cadastro = []
        for code in [*(str(p) for p in range(1, 10)), '001']:
            row = {f'c{i}': '' for i in range(38)}
            row.update(c0=code, c1='202503', c12='OLD', c16='0002', c32='001')
            cadastro.append(row)
        marker_tokens = ['"1.20"', '"NA"', '"NI"', 'null', '""', '"null"', '"NA%"', '"NI%"']
        numeric = '{"id":1,"values":[' + ','.join(
            '{"e":' + str(p) + ',"v":[{"i":700,"v":' + ('9007199254740993.0100' if p == 1 else '-0.00') +
            '},{"i":702,"v":' + token + '},{"i":141870,"v":12.50}' +
            (',{"i":701,"v":1e-27}' if p == 1 else '') + ']}'
            for p, token in enumerate(marker_tokens, 1)) + ']}'
        self.data = {'catalog': [{'dt': 202503, 'files': [
            *({'f': 'ifdata_2025_2030//202503/' + name} for name in
              ('cadastro202503_1005.json', 'info202503.json', 'dados202503_1.json')),
            {'sel': [{'id': 1005, 'n': 'Conglomerados Financeiros e Instituições Independentes'}]},
            *({'trel': r} for r in self.reports)]}], 'dictionary': self.definitions,
            'cadaster': cadastro, 'numeric': numeric, 'portal': 'opaque archived formatter'}
        self.write_sources()
        self.make_profile()

    def write_sources(self):
        self.pins = {}
        self.manifests = {}
        for role, value in self.data.items():
            body = value.encode() if isinstance(value, str) else json.dumps(value, ensure_ascii=False).encode()
            if role == 'catalog':
                body = body.replace(b'{"json_number": "1.2300e-2"}', b'1.2300e-2')
            (self.root / (role + '.bin')).write_bytes(body)
            filename = {'cadaster': 'cadastro202503_1005.json', 'dictionary': 'info202503.json',
                        'numeric': 'dados202503_1.json'}.get(role)
            url = ('https://www3.bcb.gov.br/ifdata/rest/relatorios2025a2030' if role == 'catalog' else
                   'https://www3.bcb.gov.br/ifdata/index.html' if role == 'portal' else
                   'https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=ifdata_2025_2030%2F%2F202503%2F' + filename)
            manifest = {'method': 'GET', 'url': url, 'final_url': url, 'http_status': 200, 'outcome': 'ok',
                'truncated': False, 'diagnostics': [], 'bytes': len(body), 'sha256': sha(body),
                'body_path': role + '.bin', 'retrieved_at_utc': '2026-10-04T00:00:00+00:00',
                'context': {'synthetic': True, 'perspective': 1006 if role in ('dictionary', 'numeric') else 1005}}
            self.save_source(role, manifest)
        self.index.write_text(json.dumps({'contract': 'ifdata-financial-reports-sources-v1', 'selection': SELECTION,
            'sources': {role: role + '.manifest.json' for role in self.data}}), encoding='utf-8')

    def save_source(self, role, manifest):
        body = json.dumps(manifest).encode()
        (self.root / (role + '.manifest.json')).write_bytes(body)
        self.manifests[role] = manifest
        record = {key: manifest[key] for key in ('url', 'final_url', 'retrieved_at_utc', 'bytes', 'sha256', 'body_path', 'context')}
        record.update(manifest_sha256=sha(body), source_generation_state='unknown')
        self.pins[role] = {'body_sha256': manifest['sha256'], 'manifest_sha256': sha(body),
                           'provenance_sha256': sha(canonical(record).encode())}

    def make_profile(self):
        infos = {info['id']: (p, info) for p, info in enumerate(self.definitions)}
        reports = []
        for p, report in enumerate(self.reports):
            pointer = f'/0/files/{p + 4}/trel'
            nodes = []
            def walk(columns, base, parent=None):
                for q, col in enumerate(columns):
                    ptr = base + '/' + str(q)
                    dpos, definition = infos[col['ifd']]
                    kind = 'group' if col['sc'] else 'money' if definition['td'] == 3 else 'quantity' if col['fid'] == 2 else 'attribute'
                    flow = kind == 'money' and (report['id'] == 118 or report['id'] == 119 and definition['id'] == 79859)
                    nodes.append({'report_id': report['id'], 'column_id': col['id'], 'ifd': definition['id'],
                        'td': definition['td'], 'area': definition['a'], 'lid': definition['lid'], 'fid': col['fid'],
                        'name': definition['n'], 'definition': copy.deepcopy(definition), 'catalog_pointer': ptr,
                        'definition_pointer': '/' + str(dpos), 'parent_pointer': parent,
                        'children_pointers': [ptr + '/sc/' + str(n) for n in range(len(col['sc']))], 'kind': kind,
                        'unit': '' if kind == 'group' else 'BRL_raw_inferred' if kind == 'money' else 'count' if kind == 'quantity' else 'text',
                        'unit_basis': '' if kind == 'group' else 'archived_formatter_divides_by_1000' if kind == 'money' else 'cadaster_definition',
                        'window_start': '2025-01-01' if flow else '',
                        'window_end': '' if kind == 'group' else '2025-03-31',
                        'window_basis': '' if kind == 'group' else 'report_rp_result_window' if flow else 'stock_at_reference_inferred' if kind == 'money' else 'cadaster_reference'})
                    walk(col['sc'], ptr + '/sc', ptr)
            walk(report['c'], pointer + '/c')
            reports.append({'report': copy.deepcopy(report), 'catalog_pointer': pointer, 'nodes': nodes})
        self.profile = {'contract': 'ifdata-financial-reports-profile-202503-v1', 'selection': SELECTION,
                        'cadaster_fields': 38, 'source_pins': copy.deepcopy(self.pins), 'reports': reports}
        self.save_profile()

    def save_profile(self):
        self.profile_path.write_text(json.dumps(self.profile, ensure_ascii=False), encoding='utf-8')


class FinancialReports202503Tests(unittest.TestCase):
    def setUp(self):
        self.prepare_fixture()

    def prepare_fixture(self):
        """Give independent mutations fresh physical paths, without I/O retries."""
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.fixture = Fixture202503(self.root)
        profile = patch.object(reader, 'PROFILE_202503_PATH', self.fixture.profile_path, create=True)
        profile.start()
        self.addCleanup(profile.stop)
        self.source = self.root / 'admission'
        self.destination = self.root / 'parquet'

    def admit(self, destination=None):
        return financial.admit(self.fixture.index, destination or self.source)

    def convert(self):
        admitted = self.admit()
        result = financial_parquet.convert_financial(self.source, self.destination,
            source_manifest_sha256=sha((self.source / 'manifest.json').read_bytes()))
        return admitted, result

    def rows(self, name):
        with (self.source / name).open(encoding='utf-8', newline='') as stream:
            return list(csv.DictReader(stream))

    def test_native_202503_grade_states_namespace_tree_and_january_march(self):
        result = self.admit()
        self.assertEqual(result['contract'], 'ifdata-financial-reports-snapshot-202503-v1')
        self.assertEqual(result['selection'], SELECTION)
        self.assertEqual((result['cells'], result['observations'], result['cadaster_records']), (250, 190, 10))
        values = {(r['report_id'], r['institution_id'], r['ifd']): r for r in self.rows('financial-cells.csv')}
        large = values['119', '1', '20']
        self.assertEqual((large['raw_value'], large['numeric_value'], large['source_kind']),
                         ('9007199254740993.0100', '9007199254740993.0100', 'json_number'))
        self.assertEqual(values['119', '1', '21']['raw_value'], '1e-27')
        self.assertEqual(values['119', '1', '21']['numeric_value'], '1E-27')
        self.assertEqual(values['119', '2', '20']['raw_value'], '-0.00')
        self.assertEqual(values['119', '2', '20']['value_state'], 'zero')
        self.assertEqual(values['119', '1', '11']['raw_value'], '001')
        self.assertEqual(values['119', '1', '11']['source_pointer'], '/0/c32')
        self.assertEqual(values['119', '1', '11']['numeric_value'], '')
        self.assertEqual(values['119', '1', '12']['numeric_value'], '2')
        for p, state in enumerate(('numeric', 'NA', 'NI', 'json_null', 'empty', 'literal_null', 'NA_percent', 'NI_percent'), 1):
            self.assertEqual(values['119', str(p), '22']['value_state'], state)
        self.assertEqual(values['119', '1', '22']['source_kind'], 'json_string')
        self.assertEqual(values['119', '9', '20']['presence'], 'entity_not_stored')
        self.assertEqual(values['119', '001', '20']['presence'], 'entity_not_stored')
        self.assertEqual(values['119', '2', '21']['presence'], 'information_not_stored')
        self.assertEqual(values['119', '1', '79859']['window_start'], '2025-01-01')
        self.assertEqual(values['118', '1', '20']['window_start'], '2025-01-01')
        self.assertEqual(values['107', '1', '79859']['window_start'], '')
        self.assertEqual(large['window_end'], '2025-03-31')
        self.assertEqual(large['source_pointer'], values['107', '1', '20']['source_pointer'])
        document = json.loads((self.source / 'financial-variables.json').read_bytes())
        self.assertEqual((len(document['nodes']), len(document['variables'])), (29, 25))
        self.assertEqual(document['reports'][0]['report']['cot'], {'json_number': '1.2300e-2'})
        child = next(n for n in document['nodes'] if n['ifd'] == 20)
        group = next(n for n in document['nodes'] if n['kind'] == 'group')
        self.assertNotEqual(child['ifd'], child['lid'])
        self.assertEqual(child['parent_pointer'], group['catalog_pointer'])
        self.assertIn(child['catalog_pointer'], group['children_pointers'])
        self.assertEqual(result['sources']['numeric']['context']['perspective'], 1006)

    def test_public_parquet_exact_local_views_and_replay(self):
        admitted, result = self.convert()
        self.assertEqual(result['contract'], 'ifdata-financial-reports-parquet-202503-v1')
        self.assertEqual(result['cells_part'], 'parts/financial-cells-202503.parquet')
        self.assertEqual(result['selection'], SELECTION)
        self.assertEqual(len(result['numeric_bindings']), 17)
        self.assertEqual(financial_parquet.validate_snapshot(self.destination, manifest_sha256=result['manifest_sha256']), result)
        with financial_parquet.snapshot_connection(self.destination, manifest_sha256=result['manifest_sha256']) as con:
            self.assertEqual(con.execute('SELECT count(*) FROM financial_cells').fetchone(), (250,))
            self.assertEqual(con.execute('SELECT count(*) FROM financial_observations').fetchone(), (190,))
            self.assertNotIn('numeric_decimal', [r[0] for r in con.execute('DESCRIBE financial_cells').fetchall()])
            for binding in result['numeric_bindings']:
                rows = con.execute('SELECT institution_id,report_id,catalog_pointer,numeric_value FROM financial_cells WHERE catalog_pointer=?', [binding['catalog_pointer']]).fetchall()
                self.assertEqual(con.execute('FROM ' + binding['view']).fetchall(),
                                 [(*r[:3], Decimal(r[3]) if r[3] else None) for r in rows])
            numbers = [Decimal(r[0]) for r in con.execute("SELECT numeric_value FROM financial_cells WHERE numeric_value<>''").fetchall()]
            self.assertGreater(max(n.adjusted() + 1 for n in numbers) + max(-n.as_tuple().exponent for n in numbers), 38)
        replay_source = self.root / 'admission-replay'
        self.assertEqual(admitted['files'], self.admit(replay_source)['files'])
        replay = financial_parquet.convert_financial(replay_source, self.root / 'parquet-replay',
            source_manifest_sha256=sha((replay_source / 'manifest.json').read_bytes()))
        # Source manifest metadata is execution-specific; projected parts remain identical.
        self.assertEqual([e for e in result['files'] if e['path'].startswith('parts/')],
                         [e for e in replay['files'] if e['path'].startswith('parts/')])

    def test_existing_clis_use_closed_selection_without_profile_arguments(self):
        results = []
        for name, args in [('admit-financial.py', ['--index', str(self.fixture.index), '--output', str(self.source)]),
                           ('convert-financial.py', ['--source', str(self.source), '--output', str(self.destination)])]:
            if name.startswith('convert'):
                args += ['--source-manifest-sha256', sha((self.source / 'manifest.json').read_bytes())]
            path = ROOT / 'scripts' / name
            output = io.StringIO()
            with patch.object(sys, 'argv', [str(path), *args]), patch.object(sys, 'path', list(sys.path)), redirect_stdout(output):
                runpy.run_path(str(path), run_name='__main__')
            results.append(json.loads(output.getvalue()))
        self.assertEqual(results[0]['contract'], 'ifdata-financial-reports-snapshot-202503-v1')
        self.assertEqual(results[1]['contract'], 'ifdata-financial-reports-parquet-202503-v1')

    def test_existing_clis_reject_index_override_and_external_hash_mismatch(self):
        original = self.fixture.index.read_bytes()
        index = json.loads(original)
        index['profile'] = str(self.fixture.profile_path)
        self.fixture.index.write_text(json.dumps(index))
        commands = [('admit-financial.py', ['--index', str(self.fixture.index), '--output', str(self.source)])]
        path = ROOT / 'scripts' / commands[0][0]
        with patch.object(sys, 'argv', [str(path), *commands[0][1]]), patch.object(sys, 'path', list(sys.path)), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error: runpy.run_path(str(path), run_name='__main__')
        self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.source.exists())
        self.fixture.index.write_bytes(original)
        self.admit()
        path = ROOT / 'scripts/convert-financial.py'
        args = ['--source', str(self.source), '--output', str(self.destination), '--source-manifest-sha256', '0' * 64]
        with patch.object(sys, 'argv', [str(path), *args]), patch.object(sys, 'path', list(sys.path)), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error: runpy.run_path(str(path), run_name='__main__')
        self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.destination.exists())

    def test_2024_source_guard_rejects_2025_namespace_and_summary_202503_stays_closed(self):
        from tests.test_financial_reports import FinancialReportsTests
        fixture = FinancialReportsTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        with patch.object(reader, 'PROFILE_PATH', fixture.profile_path):
            context = reader._context()
            self.assertEqual(context['selection'], {'period': 202412, 'perspective': 1005, 'reports': [92, 96, 101, 98]})
            for role in ('catalog', 'cadaster', 'dictionary', 'numeric'):
                path = fixture.root / (role + '.manifest.json')
                manifest = json.loads(path.read_bytes())
                manifest['url'] = manifest['url'].replace('2000a2024', '2025a2030') if role == 'catalog' else manifest['url'].replace('ifdata%2F202412%2F', 'ifdata_2025_2030%2F%2F202503%2F')
                manifest['final_url'] = manifest['url']
                path.write_text(json.dumps(manifest))
                with self.subTest(role=role), self.assertRaises(ValueError): financial._source(role, path, context)
        with self.assertRaises(ValueError): financial._profile_for_selection({'period': 202503, 'perspective': 1005, 'report': 119})

    def test_closed_selection_rejects_noncanonical_types_subsets_and_index_profile(self):
        original = json.loads(self.fixture.index.read_bytes())
        for selection in ({**SELECTION, 'period': 202503.0}, {**SELECTION, 'perspective': '1005'},
                          {**SELECTION, 'reports': [119.0, 107, 110, 118]},
                          {**SELECTION, 'reports': [119]}, {**SELECTION, 'reports': [118, 110, 107, 119]},
                          {**SELECTION, 'period': 202506}, {**SELECTION, 'report': 119}):
            self.fixture.index.write_text(json.dumps({**original, 'selection': selection}))
            with self.subTest(selection=selection), self.assertRaises(ValueError): self.admit()
        self.fixture.index.write_text(json.dumps({**original, 'profile': str(self.fixture.profile_path)}))
        with self.assertRaises(ValueError): self.admit()
        self.assertFalse(self.source.exists())

    def test_all_five_body_manifest_context_provenance_pins_reject_mutation(self):
        for role in self.fixture.data:
            for change in ('body', 'context', 'utc', 'url', 'final_url', 'hash'):
                with self.subTest(role=role, change=change):
                    self.prepare_fixture()
                    path = self.root / (role + '.manifest.json')
                    manifest = json.loads(path.read_bytes())
                    if change == 'body': (self.root / (role + '.bin')).write_bytes(b'changed')
                    elif change == 'context': manifest['context']['perspective'] = 1005 if role == 'numeric' else 9999
                    elif change == 'utc': manifest['retrieved_at_utc'] = '2026-10-05T00:00:00+00:00'
                    elif change == 'hash': manifest['sha256'] = '0' * 64
                    else: manifest[change] += '&extra=1'
                    if change != 'body':
                        path.write_text(json.dumps(manifest))
                        # Manifest pin alone cannot bypass the complete provenance pin.
                        self.fixture.profile['source_pins'][role]['manifest_sha256'] = sha(path.read_bytes())
                        self.fixture.save_profile()
                    with self.assertRaises(ValueError): self.admit()
                    self.assertFalse(self.source.exists())
        self.assertFalse(self.source.exists())

    def test_wrong_2024_namespace_or_normalized_double_slash_rejected_even_repinned(self):
        for role in ('catalog', 'cadaster', 'dictionary', 'numeric'):
            for change in ('2024', 'one_slash', 'extra_parameter'):
                if role == 'catalog' and change == 'one_slash': continue
                with self.subTest(role=role, change=change):
                    self.fixture.write_sources()
                    manifest = copy.deepcopy(self.fixture.manifests[role])
                    if role == 'catalog': manifest['url'] = manifest['url'].replace('2025a2030', '2000a2024') if change == '2024' else manifest['url'] + '?extra=1'
                    else:
                        manifest['url'] = manifest['url'].replace('ifdata_2025_2030%2F%2F', 'ifdata%2F') if change == '2024' else manifest['url'].replace('%2F%2F', '%2F') if change == 'one_slash' else manifest['url'] + '&extra=1'
                    manifest['final_url'] = manifest['url']
                    self.fixture.save_source(role, manifest)
                    self.fixture.profile['source_pins'] = copy.deepcopy(self.fixture.pins)
                    self.fixture.save_profile()
                    with self.assertRaisesRegex(ValueError, 'Wrong'): self.admit()

    def test_source_guard_requires_canonical_closed_context_and_single_query_parameter(self):
        context = reader._context(SELECTION)
        path = self.root / 'numeric.manifest.json'
        for change in ('period_float', 'profile_contract', 'selection', 'profile_selection'):
            bad = copy.deepcopy(context)
            if change == 'period_float': bad['period'] = 202503.0
            elif change == 'profile_contract': bad['profile']['contract'] = 'ifdata-financial-profile-202503-v1'
            elif change == 'selection': bad['selection']['reports'] = [119]
            else: bad['profile']['selection']['reports'] = [119]
            with self.subTest(change=change), self.assertRaises(ValueError):
                financial._source('numeric', path, bad)
        manifest = copy.deepcopy(self.fixture.manifests['numeric'])
        for suffix in ('&extra=', '&nomeArquivo=', '&bare'):
            manifest['url'] = self.fixture.manifests['numeric']['url'] + suffix
            manifest['final_url'] = manifest['url']
            self.fixture.save_source('numeric', manifest)
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                financial._source('numeric', path, context)

    def test_native_source_schema_reference_announcement_and_key_mutants_rejected(self):
        original = copy.deepcopy(self.fixture.data)
        for change in ('field', 'reference', 'duplicate_code', 'numeric_code', 'announcement', 'catalog_reference',
                       'duplicate_entity', 'duplicate_lid', 'string_id', 'duplicate_json', 'tree', 'definition'):
            self.fixture.data = copy.deepcopy(original)
            if change == 'field': del self.fixture.data['cadaster'][0]['c37']
            elif change == 'reference': self.fixture.data['cadaster'][0]['c1'] = '202412'
            elif change == 'duplicate_code': self.fixture.data['cadaster'][1]['c0'] = '1'
            elif change == 'numeric_code': self.fixture.data['cadaster'][0]['c0'] = 1
            elif change == 'announcement': self.fixture.data['catalog'][0]['files'][0]['f'] = 'ifdata_2025_2030/202503/cadastro202503_1005.json'
            elif change == 'catalog_reference': self.fixture.data['catalog'][0]['dt'] = 202412
            elif change == 'duplicate_entity': self.fixture.data['numeric'] = '{"id":1,"values":[{"e":1,"v":[]},{"e":1,"v":[]}]}'
            elif change == 'duplicate_lid': self.fixture.data['numeric'] = '{"id":1,"values":[{"e":1,"v":[{"i":700,"v":0},{"i":700,"v":1}]}]}'
            elif change == 'string_id': self.fixture.data['numeric'] = '{"id":1,"values":[{"e":"1","v":[]}]}'
            elif change == 'duplicate_json': self.fixture.data['numeric'] = '{"id":1,"id":1,"values":[]}'
            elif change == 'tree': self.fixture.data['catalog'][0]['files'][4]['trel']['c'][3]['sc'] = []
            else: self.fixture.data['dictionary'][0]['d'] = 'changed'
            self.fixture.write_sources()
            self.fixture.profile['source_pins'] = copy.deepcopy(self.fixture.pins)
            self.fixture.save_profile()
            with self.subTest(change=change), self.assertRaises(ValueError): self.admit()

    def test_coherent_202503_payload_and_binding_mutations_rejected(self):
        admitted = self.admit()
        original = {entry['path']: (self.source / entry['path']).read_bytes() for entry in admitted['files']}
        for change in ('context', 'window', 'raw', 'pointer', 'observation', 'metadata', 'count'):
            candidate, bodies = copy.deepcopy(admitted), copy.deepcopy(original)
            if change == 'context': candidate['sources']['numeric']['context']['perspective'] = 1005
            elif change == 'count': candidate['cells'] += 1
            elif change == 'metadata':
                document = json.loads(bodies['financial-variables.json'])
                document['nodes'][0]['definition']['d'] = 'changed'
                bodies['financial-variables.json'] = json.dumps(document).encode()
            elif change == 'observation': bodies['financial-observations.csv'] = bodies['financial-observations.csv'].replace(b'9007199254740993.0100', b'9007199254740993.0200')
            else:
                for name in ('financial-cells.csv', 'financial-observations.csv'):
                    before, after = {'window': (b'2025-01-01', b'2024-07-01'),
                                     'raw': (b'9007199254740993.0100', b'9007199254740993.0200'),
                                     'pointer': (b'/values/0/v/3/v', b'/values/0/v/0/v')}[change]
                    bodies[name] = bodies[name].replace(before, after, 1)
            for entry in candidate['files']:
                entry.update(bytes=len(bodies[entry['path']]), sha256=sha(bodies[entry['path']]))
            with self.subTest(change=change), self.assertRaises(ValueError): reader.validate_admission(candidate, bodies)
        converted = financial_parquet.convert_financial(self.source, self.destination,
            source_manifest_sha256=sha((self.source / 'manifest.json').read_bytes()))
        import duckdb
        binding = converted['numeric_bindings'][0]
        path = self.destination / binding['path']
        with duckdb.connect() as con:
            con.execute('CREATE TABLE mutated AS FROM read_parquet(?)', [str(path)])
            con.execute('UPDATE mutated SET numeric_decimal=numeric_decimal+1')
            con.execute('COPY mutated TO ? (FORMAT PARQUET)', [str(path)])
        mutated = copy.deepcopy(converted)
        mutated.pop('manifest_sha256')
        for entry in mutated['files']:
            body = (self.destination / entry['path']).read_bytes()
            entry.update(bytes=len(body), sha256=sha(body))
        body = json.dumps(mutated).encode()
        (self.destination / 'manifest.json').write_bytes(body)
        with self.assertRaises(ValueError): financial_parquet.validate_snapshot(self.destination, manifest_sha256=sha(body))

    def test_profile_membership_tree_and_annotation_mutants_rejected(self):
        original = copy.deepcopy(self.fixture.profile)
        for change in ('membership', 'children', 'definition', 'window', 'unit', 'kind'):
            self.fixture.profile = copy.deepcopy(original)
            item = self.fixture.profile['reports'][0]
            node = next(n for n in item['nodes'] if n['kind'] == 'money')
            if change == 'membership': self.fixture.profile['reports'].reverse()
            elif change == 'children': item['nodes'][3]['children_pointers'] = []
            elif change == 'definition': node['definition']['d'] = 'changed'
            elif change == 'window': node['window_end'] = '2024-12-31'
            elif change == 'unit': node['unit'] = 'USD'
            else: item['nodes'][1]['kind'] = 'quantity'
            self.fixture.save_profile()
            with self.subTest(change=change), self.assertRaises(ValueError): self.admit()

    def test_alternating_reports_and_summary_profiles_keep_contracts_defaults_and_windows(self):
        from tests.test_financial_reports import FinancialReportsTests
        from tests.test_financial import FinancialTests
        from tests.test_financial_202312 import Financial202312Tests
        report24, summary24, summary23 = FinancialReportsTests(), FinancialTests(), Financial202312Tests()
        for fixture in (report24, summary24, summary23):
            fixture.setUp()
            self.addCleanup(fixture.doCleanups)
        constants = copy.deepcopy((reader.CONTRACT, reader.SELECTION, reader.ENVELOPE, reader.LIMITATIONS,
                                    adapter.CONTRACT, adapter.PART, financial.CONTRACT, financial.SELECTION))
        with patch.object(reader, 'PROFILE_PATH', report24.profile_path), patch.object(financial, 'PROFILE_PATH', summary24.profile_path):
            for p, fixture in enumerate((report24, self.fixture, report24, summary24, self.fixture, summary23)):
                source, destination = fixture.root / f'alt-source-{p}', fixture.root / f'alt-parquet-{p}'
                admitted = financial.admit(fixture.index, source)
                converted = financial_parquet.convert_financial(source, destination, source_manifest_sha256=sha((source / 'manifest.json').read_bytes()))
                self.assertEqual(converted['selection'], admitted['selection'])
                self.assertEqual(financial_parquet.validate_snapshot(destination, manifest_sha256=converted['manifest_sha256']), converted)
                with financial_parquet.snapshot_connection(destination, manifest_sha256=converted['manifest_sha256']) as con:
                    self.assertEqual(con.execute('SELECT DISTINCT contract FROM financial_cells').fetchall(), [(admitted['contract'],)])
                if fixture is self.fixture:
                    admitted['selection']['reports'].clear()
                    admitted['limitations'].clear()
        self.assertEqual((reader.CONTRACT, reader.SELECTION, reader.ENVELOPE, reader.LIMITATIONS,
                          adapter.CONTRACT, adapter.PART, financial.CONTRACT, financial.SELECTION), constants)

    def test_hashes_precede_dispatch_mixed_contracts_and_selection_block_before_views(self):
        _, result = self.convert()
        for public, target, output, parameter in (
            (financial_parquet.convert_financial, self.source, self.root / 'bad', 'source_manifest_sha256'),
            (financial_parquet.validate_snapshot, self.destination, None, 'manifest_sha256'),
            (financial_parquet.snapshot_connection, self.destination, None, 'manifest_sha256')):
            with patch.object(adapter, public.__name__, side_effect=AssertionError('premature dispatch')):
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    public(*((target, output) if output else (target,)), **{parameter: '0' * 64})
        for target, public, output, parameter in (
            (self.source, financial_parquet.convert_financial, self.root / 'mixed', 'source_manifest_sha256'),
            (self.destination, financial_parquet.validate_snapshot, None, 'manifest_sha256'),
            (self.destination, financial_parquet.snapshot_connection, None, 'manifest_sha256')):
            path = target / 'manifest.json'
            original = path.read_bytes()
            for change in ('contract', 'selection', 'period_float'):
                manifest = json.loads(original)
                if change == 'contract': manifest['contract'] = manifest['contract'].replace('202503', '202412')
                elif change == 'period_float': manifest['selection']['period'] = 202503.0
                else: manifest['selection']['reports'] = [119]
                body = json.dumps(manifest).encode()
                path.write_bytes(body)
                with self.subTest(change=change, api=public.__name__), self.assertRaises(ValueError):
                    public(*((target, output) if output else (target,)), **{parameter: sha(body)})
            path.write_bytes(original)

    def test_partial_existing_extra_files_and_owned_verified_images(self):
        self.admit()
        with self.assertRaises(FileExistsError): self.admit()
        source_hash = sha((self.source / 'manifest.json').read_bytes())
        original_files = adapter._files
        def swap_source(*args):
            bodies = original_files(*args)
            (self.source / 'financial-cells.csv').write_bytes(b'changed after hash')
            return bodies
        with patch.object(adapter, '_files', side_effect=swap_source):
            result = financial_parquet.convert_financial(self.source, self.destination, source_manifest_sha256=source_hash)
        extra = self.destination / 'parts' / 'extra.parquet'
        extra.write_bytes(b'extra')
        with self.assertRaises(ValueError): financial_parquet.validate_snapshot(self.destination, manifest_sha256=result['manifest_sha256'])
        extra.unlink()
        def swap_snapshot(*args):
            bodies = original_files(*args)
            (self.destination / result['cells_part']).write_bytes(b'changed after hash')
            return bodies
        with patch.object(adapter, '_files', side_effect=swap_snapshot):
            con = financial_parquet.snapshot_connection(self.destination, manifest_sha256=result['manifest_sha256'])
        self.addCleanup(con.close)
        for path in self.root.glob('*.bin'): path.unlink()
        for binding in result['numeric_bindings']: (self.destination / binding['path']).write_bytes(b'changed after load')
        self.assertEqual(con.execute('SELECT count(*) FROM financial_cells').fetchone(), (250,))

    def test_writer_interruption_preserves_partial_without_acceptance(self):
        self.admit()
        with patch.object(adapter, '_write_part', side_effect=OSError('interrupted')):
            with self.assertRaisesRegex(OSError, 'interrupted'):
                financial_parquet.convert_financial(self.source, self.destination,
                    source_manifest_sha256=sha((self.source / 'manifest.json').read_bytes()))
        self.assertTrue(self.destination.exists())
        self.assertFalse((self.destination / 'manifest.json').exists())

    def test_installed_official_profile_metadata_counts_pins_and_annotations(self):
        profile = json.loads((ROOT / 'bank_quality/financial-reports-profile-202503.json').read_bytes())
        nodes = [node for item in profile['reports'] for node in item['nodes']]
        self.assertEqual(profile['selection'], SELECTION)
        self.assertEqual((len(nodes), sum(n['kind'] == 'group' for n in nodes), sum(n['kind'] == 'money' for n in nodes),
                          sum(n['kind'] == 'quantity' for n in nodes), sum(n['kind'] == 'attribute' for n in nodes)),
                         (158, 15, 105, 2, 36))
        self.assertEqual(len({n['lid'] for n in nodes if n['kind'] == 'money'}), 98)
        self.assertEqual(set(profile), {'contract', 'selection', 'cadaster_fields', 'source_pins', 'reports'})
        for pin in profile['source_pins'].values():
            self.assertEqual(set(pin), {'body_sha256', 'manifest_sha256', 'provenance_sha256'})
        income = next(n for n in nodes if n['report_id'] == 119 and n['ifd'] == 79859)
        self.assertEqual((income['lid'], income['window_start'], income['window_end']), (141870, '2025-01-01', '2025-03-31'))
        self.assertTrue(all(n['lid'] == 32 for n in nodes if n['ifd'] == 79867))


if __name__ == '__main__':
    unittest.main()

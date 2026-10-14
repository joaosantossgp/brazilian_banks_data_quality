"""Offline synthetic historical relationships, integrity and temporal limits."""
import csv
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import types
import duckdb

import test_cvm_metadata as cvm_fixtures
import test_cvm_corporate_metadata as corporate_fixtures
from test_cvm_corporate_metadata import csv_bytes, row
from bank_quality import ifdata_cadastro


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HistoricalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cvm_fixture = cvm_fixtures.CVMMetadataTests()
        self.cvm_fixture.setUp()
        self.cvm_fixture.rows['cad'][0]['CD_CVM'] = '001023'
        self.addCleanup(self.cvm_fixture.doCleanups)
        self.corp_fixture = corporate_fixtures.CorporateTests()
        self.corp_fixture.setUp()
        self.addCleanup(self.corp_fixture.doCleanups)
        self.native = dict.fromkeys(ifdata_cadastro.FIELDS)
        self.native.update(CodInst='00000000', NomeInstituicao='unrelated name', Td='I',
                           CodConglomeradoFinanceiro='F001', CodConglomeradoPrudencial='P001',
                           CnpjInstituicaoLider='00000000', Situacao='inativa', Tcb='B3', Tc=0)
        self.rows = [self.native, dict(self.native, CodInst='F001', Td='C', Tcb='F'),
                     dict(self.native, CodInst='P001', Td='C', Tcb='N3'),
                     dict(self.native, CodInst='XUNKNOWN', NomeInstituicao='Banco sintético')]
        self.members = {'participacao_sociedade': csv_bytes('participacao_sociedade', [])}

    def api(self):
        try:
            return importlib.import_module('bank_quality.historical_issuer_links')
        except ModuleNotFoundError:
            self.fail('Historical relationship API is not implemented')

    def packages(self):
        cv = self.cvm_fixture
        cr = cv.build(cv.fixture())
        cp = cv.root / 'output'
        corp = self.corp_fixture
        co = corp.sources(members=self.members)
        rr = corp.api.build_corporate_metadata(corp.index, corp.pin, co)
        raw = self.root / 'raw'
        (raw / 'json').mkdir(parents=True)
        (raw / 'resumo.json').write_text(json.dumps(dict(download_utc='2026-10-12T00:00:00Z')))
        with (raw / 'indice_periodos.csv').open('w', newline='', encoding='utf-8-sig') as stream:
            writer = csv.DictWriter(stream, ['periodo', 'registros', 'paginas', 'status', 'url', 'sha256_json'], delimiter=';')
            writer.writeheader()
            for year in range(2010, 2025):
                for month in ('03', '06', '09', '12'):
                    period = str(year) + month
                    payload = {'@odata.context': ifdata_cadastro.CONTEXT,
                               'value': [dict(r, Data=period) for r in self.rows]}
                    part = raw / 'json' / (period + '.json')
                    part.write_text(json.dumps(payload), encoding='utf8')
                    writer.writerow(dict(periodo=period, registros=len(self.rows), paginas='1', status='disponivel',
                                         url='https://example.test/' + period, sha256_json=sha(part)))
        cad = self.root / 'cad'
        ifdata_cadastro.import_cadastro(raw, cad)
        return cp, cr['manifest_sha256'], cad, sha(cad / 'manifest.json'), co, rr['manifest_sha256']

    def build(self):
        args = self.packages()
        out = self.root / 'links'
        receipt = self.api().build_historical_issuer_links(*args, out)
        return out, receipt, args

    def table(self, out, name):
        with duckdb.connect() as conn:
            cursor = conn.execute("select * from read_csv(?, all_varchar=true, header=true, nullstr='', allow_quoted_nulls=false)",
                                  [str(out / (name + '.csv'))])
            return [dict(zip([f[0] for f in cursor.description], values)) for values in cursor.fetchall()]

    def test_cvm_conflict_comparison_ignores_only_ascii_zero_padding(self):
        api = self.api()
        cases = [(['906', '000906'], False), (['1023', '001023'], False),
                 (['0', '000000'], False), (['1279', '19348', '019348'], True),
                 (['906', 'A00906'], True), (['906', '+906'], True),
                 (['906', '-906'], True), (['906', '906.0'], True),
                 (['906', '9.06e2'], True), (['906', ' 906'], True),
                 (['906', '906 '], True), (['906', '906\n'], True),
                 (['906', '９０６'], True), (['906', '٩٠٦'], True),
                 (['906', None, ''], False)]
        for tokens, conflict in cases:
            for ordered in (tokens, list(reversed(tokens))):
                with self.subTest(tokens=ordered):
                    records = [dict(cnpj_full='00000000000191', cvm_code=token,
                                    CD_CVM=token, identifier_conflict='false') for token in ordered]
                    before = [dict(record) for record in records]
                    api._issuer_conflicts(records)
                    self.assertEqual([r['identifier_conflict'] for r in records],
                                     [str(conflict).lower()] * len(records))
                    for original, actual in zip(before, records):
                        self.assertEqual({k: v for k, v in actual.items() if k != 'identifier_conflict'},
                                         {k: v for k, v in original.items() if k != 'identifier_conflict'})
        unknown = [dict(cnpj_full=None, cvm_code=code) for code in ('906', '1279')]
        api._issuer_conflicts(unknown)
        self.assertEqual([r['identifier_conflict'] for r in unknown], ['false', 'false'])

    def test_ascii_padded_cvm_codes_keep_native_values_and_remove_false_conflict(self):
        self.cvm_fixture.rows['cad'][0]['CD_CVM'] = '1023'
        out, result, _ = self.build()
        api = self.api()
        api.verify_historical_issuer_links(out, result['manifest_sha256'])
        records = self.table(out, 'emissores')
        self.assertEqual([r['cvm_code'] for r in records], ['1023', '001023', '001023'])
        self.assertEqual([r['CD_CVM'] for r in records], ['1023', '001023', None])
        self.assertEqual([r['Codigo_CVM'] for r in records], [None, None, '001023'])
        self.assertEqual({r['identifier_conflict'] for r in records}, {'false'})
        data = api.query_historical_issuer_links(out, result['manifest_sha256'], reference='201003')
        self.assertEqual(len(data['relacao_trimestral']), 3)
        self.assertEqual({r['evidence_state'] for r in data['relacao_trimestral']}, {'candidatura_cadastral'})
        self.assertEqual({r['cvm_codes'] for r in data['relacao_trimestral']}, {'["001023","1023"]'})
        self.assertFalse(any(r['reason'] == 'multiplos_codigos_cvm' for r in data['lacunas']))
        self.assertTrue(any(r['reason'] == 'mercado_historico_incompleto' for r in data['lacunas']))
        # Even a repinned attempt to restore the old false conflict is rejected by rederivation.
        path = out / 'emissores.csv'
        records[0]['identifier_conflict'] = 'true'
        with path.open('w', newline='', encoding='utf8') as stream:
            writer = csv.DictWriter(stream, records[0], quoting=csv.QUOTE_NOTNULL, lineterminator='\n')
            writer.writeheader()
            writer.writerows(records)
        manifest = json.loads((out / 'manifest.json').read_bytes())
        manifest['files'][path.name].update(sha256=sha(path), bytes=path.stat().st_size)
        (out / 'manifest.json').write_text(json.dumps(manifest), encoding='utf8')
        with self.assertRaises(ValueError):
            api.verify_historical_issuer_links(out, sha(out / 'manifest.json'))

    def test_native_nulls_unknown_codes_groups_and_deduplicated_classes(self):
        self.cvm_fixture.rows['valmob'] *= 2
        out, result, args = self.build()
        api = self.api()
        manifest = api.verify_historical_issuer_links(out, result['manifest_sha256'])
        self.assertEqual(len(manifest['references']), 60)
        native = self.table(out, 'cadastro')[0]
        self.assertIsNone(native['Atividade'])
        self.assertEqual(native['Tc'], '0')
        links = api.query_historical_issuer_links(out, result['manifest_sha256'], reference='201003', perspective='financeiro')
        self.assertEqual(len(links['relacao_trimestral']), 1)
        record = links['relacao_trimestral'][0]
        self.assertEqual(record['entity'], 'F001')
        self.assertEqual(record['evidence_state'], 'candidatura_cadastral')
        self.assertEqual(len(json.loads(record['instrument_support'])), 2)
        self.assertTrue(any(g['reason'] == 'codigo_individual_nao_cnpj_basico' for g in links['lacunas']))
        v = self.table(out, 'vinculos_cadastrais')[0]
        self.assertEqual(v['group_Tcb'], 'F')
        self.assertEqual(v['institution_Tcb'], 'B3')
        self.assertEqual(v['leader_scope'], 'nativo_nao_desambiguado')
        replay = api.build_historical_issuer_links(*args, self.root / 'replay')
        self.assertEqual(result['manifest_sha256'], replay['manifest_sha256'])

    def test_no_name_match_no_group_cnpj_and_conflicts_preserved(self):
        self.rows[0]['CodInst'] = '11111111'
        self.rows.append(dict(self.native, CodInst='00000000', Td='C'))
        self.cvm_fixture.rows['cad'].append(dict(self.cvm_fixture.rows['cad'][0], CD_CVM='999'))
        out, _, _ = self.build()
        self.assertEqual(self.table(out, 'relacao_trimestral'), [])
        self.assertTrue(any(r['identifier_conflict'] == 'true' for r in self.table(out, 'emissores')))

    def test_dated_controls_no_fill_missing_identifier_and_cycles(self):
        self.rows[0]['CodInst'] = '11111111'
        self.members = {'participacao_sociedade': csv_bytes('participacao_sociedade', [
            dict(row(ID_Sociedade='1', CNPJ='11.111.111/0001-00', Tipo_Sociedade='Controlada'), CNPJ_Companhia='00.000.000/0001-91'),
            row(ID_Sociedade='2', CNPJ='', Tipo_Sociedade='Controlada'),
            dict(row(ID_Sociedade='3', CNPJ='22.222.222/0001-00', Tipo_Sociedade='Controlada'), CNPJ_Companhia='22.222.222/0001-00')])}
        out, result, _ = self.build()
        api = self.api()
        dated = api.query_historical_issuer_links(out, result['manifest_sha256'], reference='201012', perspective='individual')['relacao_trimestral']
        later = api.query_historical_issuer_links(out, result['manifest_sha256'], reference='201103', perspective='individual')['relacao_trimestral']
        self.assertTrue(any(r['evidence_state'] == 'declaracao_controle_datada' for r in dated))
        self.assertTrue(all(r['evidence_state'] != 'declaracao_controle_datada' for r in later))
        reasons = {r['reason'] for r in self.table(out, 'lacunas')}
        self.assertIn('ciclo_societario', reasons)
        self.assertIn('ponta_societaria_sem_identificador', reasons)

    def test_fca_document_reference_never_annual_snapshot_or_ticker_species(self):
        vm = self.cvm_fixture.rows['valmob'][0]
        vm.update(Valor_Mobiliario='Certificados', Codigo_Negociacao='FAKE11', Mercado='Bolsa',
                  Sigla_Entidade_Administradora='CETIP', Data_Inicio_Listagem='2009-01-01', Data_Fim_Listagem='')
        out, result, _ = self.build()
        inst = self.table(out, 'instrumentos')[0]
        self.assertEqual(inst['instrument_class'], 'tipo_pendente')
        self.assertEqual(inst['b3_documentary'], 'false')
        self.assertEqual(inst['document_time_state'], 'referencia_documental_sem_snapshot')
        record = self.api().query_historical_issuer_links(out, result['manifest_sha256'], reference='201003')['relacao_trimestral'][0]
        self.assertIn('inicio_sem_fim', record['instrument_dates'])

    def test_interval_states_listing_and_trading_separate(self):
        api = self.api()
        self.assertEqual(api._interval_state('2010-01-01', '2010-12-31', '201003'), 'interior_estrito')
        self.assertEqual(api._interval_state('2010-03-31', '2010-12-31', '201003'), 'extremo_sem_inclusividade')
        self.assertEqual(api._interval_state('2010-03-31', '2010-03-31', '201003'), 'datas_coincidentes')
        self.assertEqual(api._interval_state('2011-01-01', '2010-01-01', '201003'), 'datas_conflitantes')
        self.assertEqual(api._interval_state('', '', '201003'), 'datas_ausentes')

    def test_canonical_null_lexer_matches_duckdb_multiline_escaped_quotes_and_eof(self):
        api = self.api()
        fields = ('key', 'null', 'blank', 'content')
        rows = [dict(key='0001', null=None, blank='', content='a,"quoted"\nline\r\nnext\rend'),
                dict(key='0000', null=None, blank='', content='0')]
        path = self.root / 'canonical.csv'
        with path.open('w', newline='', encoding='utf8') as stream:
            writer = csv.DictWriter(stream, fields, quoting=csv.QUOTE_NOTNULL, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        raw = path.read_bytes()
        parsed = api._parse_csv(raw, fields)
        self.assertEqual(parsed, rows)
        with duckdb.connect() as conn:
            cursor = conn.execute("select * from read_csv(?, all_varchar=true, header=true, nullstr='', allow_quoted_nulls=false)", [str(path)])
            independently_read = [dict(zip(fields, r)) for r in cursor.fetchall()]
        self.assertEqual(parsed, independently_read)
        for invalid in (raw[:-1], raw[:-3], raw + b'"unterminated', raw.replace(b'"0001"', b'0001'),
                        raw.replace(b'"0001"', b'"0001"x'), b'"key","null","blank","content"\r\n',
                        raw + b'\n', b'', b'"key","null"\n'):
            with self.subTest(invalid=invalid[-40:]), self.assertRaises(ValueError):
                api._parse_csv(invalid, fields)

    def test_integrity_external_pins_closed_inventory_and_query_validation(self):
        out, result, args = self.build()
        api = self.api()
        with self.assertRaises(ValueError):
            api.verify_historical_issuer_links(out, '0' * 64)
        with self.assertRaises(ValueError):
            api.build_historical_issuer_links(args[0], '0' * 64, *args[2:], self.root / 'bad')
        with self.assertRaises(ValueError):
            api.build_historical_issuer_links(*args, out)
        for kwargs in ({'reference': '202501'}, {'perspective': 'all'}, {'entity': ''}):
            with self.assertRaises(ValueError):
                api.query_historical_issuer_links(out, result['manifest_sha256'], **kwargs)
        empty = api.query_historical_issuer_links(out, result['manifest_sha256'], entity='NO SUCH ENTITY')
        self.assertEqual(empty['relacao_trimestral'], [])
        (out / 'extra').write_text('extra')
        with self.assertRaises(ValueError):
            api.verify_historical_issuer_links(out, result['manifest_sha256'])
        (out / 'extra').unlink()
        with (out / 'cadastro.csv').open('a') as stream:
            stream.write('tamper')
        with self.assertRaises(ValueError):
            api.query_historical_issuer_links(out, result['manifest_sha256'])

    def test_cli_query_empty_and_bad_filter(self):
        out, result, _ = self.build()
        script = Path(__file__).resolve().parents[1] / 'scripts/build-historical-issuer-links.py'
        cmd = [sys.executable, str(script), 'query', str(out), '--manifest-sha256', result['manifest_sha256']]
        good = subprocess.run(cmd + ['--entity', 'NO SUCH ENTITY'], capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)['relacao_trimestral'], [])
        bad = subprocess.run(cmd + ['--reference', '202501'], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)

    def test_unmatched_native_and_instrument_remain_queryable(self):
        self.rows[0]['CodInst'] = '11111111'
        out, result, _ = self.build()
        api = self.api()
        unmatched = api.query_historical_issuer_links(out, result['manifest_sha256'], reference='201003', entity='11111111')
        self.assertEqual(len(unmatched['cadastro']), 1)
        self.assertEqual(unmatched['relacao_trimestral'], [])
        documentary = api.query_historical_issuer_links(out, result['manifest_sha256'], entity='001023')
        self.assertEqual(len(documentary['instrumentos']), 1)
        self.assertEqual(len(documentary['emissores']), 3)

    def test_all_input_pins_tamper_and_repin_output_keys(self):
        out, result, args = self.build()
        api = self.api()
        for pin_index in (1, 3, 5):
            altered = list(args)
            altered[pin_index] = '0' * 64
            with self.assertRaises(ValueError):
                api.build_historical_issuer_links(*altered, self.root / ('wrong' + str(pin_index)))
        # Independent manifest repinning must not bypass temporal key checks.
        path = out / 'cadastro.csv'
        rows = self.table(out, 'cadastro')
        rows[1]['CodInst'] = rows[0]['CodInst']
        with path.open('w', newline='', encoding='utf8') as stream:
            writer = csv.DictWriter(stream, rows[0], quoting=csv.QUOTE_NOTNULL, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        manifest = json.loads((out / 'manifest.json').read_bytes())
        manifest['files']['cadastro.csv'].update(sha256=sha(path), bytes=path.stat().st_size)
        (out / 'manifest.json').write_text(json.dumps(manifest), encoding='utf8')
        with self.assertRaises(ValueError):
            api.verify_historical_issuer_links(out, sha(out / 'manifest.json'))

    def test_classes_literal_market_and_documentary_dates_have_equal_priority(self):
        base = self.cvm_fixture.rows['valmob'][0]
        types = ['Ações Ordinárias', 'Ações Preferenciais', 'Units', 'BDRs', 'Certificados', 'other literal']
        self.cvm_fixture.rows['valmob'] = [dict(base, Valor_Mobiliario=species, Codigo_Negociacao='SAME11',
            Mercado='Bolsa', Sigla_Entidade_Administradora='B3' if n < 4 else '',
            Data_Inicio_Listagem='2009-01-01', Data_Fim_Listagem='2011-01-01',
            Data_Inicio_Negociacao='2010-03-31', Data_Fim_Negociacao='2011-01-01') for n, species in enumerate(types)]
        out, result, _ = self.build()
        data = self.api().query_historical_issuer_links(out, result['manifest_sha256'], reference='201003', perspective='financeiro')
        self.assertEqual(len(data['relacao_trimestral']), 1)
        inst = data['instrumentos']
        self.assertEqual({r['priority'] for r in inst[:4]}, {'igual_acoes_units_bdr'})
        self.assertTrue(all(r['b3_documentary'] == 'true' for r in inst[:4]))
        self.assertEqual(inst[4]['b3_documentary'], 'false')
        dates = json.loads(data['relacao_trimestral'][0]['instrument_dates'])
        self.assertTrue(all(v == dict(listagem='interior_estrito', negociacao='extremo_sem_inclusividade') for v in dates.values()))
        self.assertTrue(any(g['reason'] == 'universo_bdr_incompleto_sem_registro_cvm' for g in data['lacunas']))

    def test_multihop_different_dates_and_controller_roles_do_not_create_simultaneity(self):
        self.rows[0]['CodInst'] = '22222222'
        first = dict(row(ID_Sociedade='1', CNPJ='11.111.111/0001-00', Tipo_Sociedade='Controlada'),
                     CNPJ_Companhia='00.000.000/0001-91')
        # A controller shareholder points from shareholder to the company.
        second = dict(row(ID_Acionista='1', Tipo_Pessoa_Acionista='PJ',
                          CPF_CNPJ_Acionista='11.111.111/0001-00', Acionista_Controlador='S',
                          Data_Composicao_Capital_Social='2010-09-30', Data_Ultima_Alteracao='2010-12-31'),
                      CNPJ_Companhia='22.222.222/0001-00')
        self.members = {'participacao_sociedade': csv_bytes('participacao_sociedade', [first]),
                        'posicao_acionaria': csv_bytes('posicao_acionaria', [second])}
        out, result, _ = self.build()
        data = self.api().query_historical_issuer_links(out, result['manifest_sha256'], reference='201012', perspective='individual')
        self.assertEqual(len(data['relacao_trimestral']), 1)
        relation = data['relacao_trimestral'][0]
        self.assertEqual(relation['issuer_full'], '00000000000191')
        self.assertEqual(relation['entity'], '22222222')
        self.assertEqual(relation['evidence_state'], 'candidatura_controle_sem_vigencia')
        path_id = json.loads(relation['control_paths'])[0]
        path = json.loads(next(r['route_json'] for r in data['caminhos_societarios'] if r['observation_id'] == path_id))
        self.assertEqual({edge['date'] for edge in path}, {'2010-09-30', '2010-12-31'})
        self.assertEqual(len(path), 2)
        declarations = self.table(out, 'societario')
        controller = next(r for r in declarations if r['control_reason'] == 'Acionista_Controlador=S')
        self.assertEqual(controller['control_date_field'], 'Data_Composicao_Capital_Social')
        self.assertEqual(controller['Data_Ultima_Alteracao'], '2010-12-31')

    def test_cadastro_missing_quarter_and_all_tampered_input_tables_rejected(self):
        args = self.packages()
        api = self.api()
        for package, filename in ((args[0], 'cadastro_atual.csv'), (args[4], 'participacao_sociedade.csv')):
            path = package / filename
            original = path.read_bytes()
            path.write_bytes(original + b'tamper')
            with self.assertRaises(ValueError):
                api.build_historical_issuer_links(*args, self.root / 'tampered')
            path.write_bytes(original)
        cad_manifest = json.loads((args[2] / 'manifest.json').read_bytes())
        part = args[2] / cad_manifest['files'][0]['file']
        original = part.read_bytes()
        part.write_bytes(original + b'tamper')
        with self.assertRaises(ValueError):
            api.build_historical_issuer_links(*args, self.root / 'tampered_cadastro')
        part.write_bytes(original)
        removed = cad_manifest['files'].pop()
        cad_manifest['rows'] -= removed['rows']
        (args[2] / 'manifest.json').write_text(json.dumps(cad_manifest), encoding='utf8')
        changed = list(args)
        changed[3] = sha(args[2] / 'manifest.json')
        with self.assertRaises(ValueError):
            api.build_historical_issuer_links(*changed, self.root / 'missing_quarter')

    def test_repin_cannot_change_technical_states_in_native_observations(self):
        out, _, _ = self.build()
        api = self.api()
        original_manifest = (out / 'manifest.json').read_bytes()
        for name, field, value in [('emissores', 'time_state', 'annual_snapshot'),
                                   ('instrumentos', 'b3_documentary', 'true')]:
            path = out / (name + '.csv')
            original = path.read_bytes()
            records = self.table(out, name)
            records[0][field] = value
            with path.open('w', newline='', encoding='utf8') as stream:
                writer = csv.DictWriter(stream, records[0], quoting=csv.QUOTE_NOTNULL, lineterminator='\n')
                writer.writeheader()
                writer.writerows(records)
            manifest = json.loads(original_manifest)
            manifest['files'][path.name].update(sha256=sha(path), bytes=path.stat().st_size)
            (out / 'manifest.json').write_text(json.dumps(manifest), encoding='utf8')
            with self.subTest(name=name), self.assertRaises(ValueError):
                api.verify_historical_issuer_links(out, sha(out / 'manifest.json'))
            path.write_bytes(original)
            (out / 'manifest.json').write_bytes(original_manifest)

    def test_unknown_cnpj_is_not_an_identity_join_key(self):
        cad = self.cvm_fixture.rows['cad'][0]
        self.cvm_fixture.rows['cad'] = [dict(cad, CNPJ_CIA=''), dict(cad, CNPJ_CIA='', CD_CVM='OTHER')]
        self.cvm_fixture.rows['geral'] = []
        self.cvm_fixture.rows['index'] = []
        out, result, _ = self.build()
        data = self.api().query_historical_issuer_links(out, result['manifest_sha256'], entity='cvm_cad:000000001')
        self.assertEqual(len(data['emissores']), 1)
        self.assertEqual(data['emissores'][0]['cvm_code'], '001023')

    def test_every_edge_inside_cyclic_component_is_unknown_including_dfs_cross_edge(self):
        self.rows[0]['CodInst'] = '22222222'
        a, b, c = '00.000.000/0001-91', '11.111.111/0001-00', '22.222.222/0001-00'
        self.members = {'participacao_sociedade': csv_bytes('participacao_sociedade', [
            dict(row(ID_Sociedade=str(n), CNPJ=child, Tipo_Sociedade='Controlada'), CNPJ_Companhia=parent)
            for n, (parent, child) in enumerate([(a, b), (b, c), (c, a), (a, c)], 1)])}
        out, result, _ = self.build()
        data = self.api().query_historical_issuer_links(out, result['manifest_sha256'], reference='201012', perspective='individual')
        self.assertTrue(data['relacao_trimestral'])
        self.assertTrue(all(r['evidence_state'] == 'candidatura_controle_sem_vigencia' for r in data['relacao_trimestral']))
        global_cycle = next(r for r in self.table(out, 'lacunas') if r['reason'] == 'ciclo_societario' and r['detail'])
        self.assertEqual(set(json.loads(global_cycle['support'])),
                         {r['observation_id'] for r in self.table(out, 'societario')})



    # Baseline is the immutable pre-normalization code, not a second hand-written
    # implementation. Execute its pure derivation only; no source acquisition.
    def oracle(self):
        module = types.ModuleType('historical_links_v1_oracle')
        source = subprocess.check_output(['git', 'show',
            '91bd20ccb205e72d47d42536eefbb529da551f16:bank_quality/historical_issuer_links.py'],
            cwd=Path(__file__).resolve().parents[1])
        exec(compile(source, '<pinned-v1-oracle>', 'exec'), module.__dict__)
        return module

    def test_v2_normalization_preserves_all_v1_semantics(self):
        a, b, c = '00.000.000/0001-91', '11.111.111/0001-00', '22.222.222/0001-00'
        self.rows[0]['CodInst'] = '22222222'
        self.members = {'participacao_sociedade': csv_bytes('participacao_sociedade', [
            dict(row(ID_Sociedade=str(n), CNPJ=child, Tipo_Sociedade='Controlada'), CNPJ_Companhia=parent)
            for n, (parent, child) in enumerate([(a, b), (b, c), (a, c)], 1)])}
        out, receipt, _ = self.build()
        api = self.api()
        manifest, tables = api._load(out, receipt['manifest_sha256'])
        self.assertEqual(manifest['contract'], 'historical-issuer-links-v2')
        self.assertEqual(len(manifest['counts']), 9)
        paths = {r['observation_id']: r for r in tables['caminhos_societarios']}
        self.assertEqual(len(paths), 2)
        for key, record in paths.items():
            self.assertEqual(key, 'caminho:' + hashlib.sha256(record['route_json'].encode('utf8')).hexdigest())
            route = json.loads(record['route_json'])
            self.assertEqual(record['issuer_full'], route[-1]['parent'])
            self.assertEqual(record['terminal_basic'], route[0]['child'][:8])
            self.assertEqual(json.loads(record['corporate_support']), sorted({s for e in route for s in e['support']}))
        oracle = self.oracle()
        native = [tables[k] for k in ('cadastro', 'emissores', 'instrumentos', 'societario')]
        # The same native observations exercise acyclic, mismatched dates and
        # cyclic graphs, across every quarter and all three perspectives.
        for scenario in ('acyclic', 'different_dates', 'circular'):
            corporate = [dict(r) for r in native[3]]
            if scenario == 'different_dates':
                corporate[0]['control_date'] = '2010-09-30'
            if scenario == 'circular':
                corporate.append(dict(corporate[0], observation_id='cycle:test', parent_full='22222222000100', child_full='00000000000191'))
            old = oracle._derive(*native[:3], corporate)
            with mock.patch.object(api, '_json_text', wraps=api._json_text) as encoded:
                new = api._derive(*native[:3], corporate)
            route_calls = [call.args[0] for call in encoded.call_args_list
                           if isinstance(call.args[0], list) and call.args[0]
                           and isinstance(call.args[0][0], dict) and 'parent' in call.args[0][0]]
            self.assertEqual(len(route_calls), len(new['caminhos_societarios']))
            old_quality, new_quality = oracle._quality(old), api._quality(new)
            self.assertEqual(new_quality.pop('contract'), 'historical-issuer-links-quality-v2')
            old_quality.pop('contract')
            new_quality['counts'].pop('caminhos_societarios.csv')
            self.assertEqual(new_quality, old_quality)
            dictionary = {r['observation_id']: json.loads(r['route_json']) for r in new.pop('caminhos_societarios')}
            for relation in new['relacao_trimestral']:
                ids = json.loads(relation['control_paths'])
                self.assertEqual(ids, sorted(set(ids)))
                expanded = sorted((dictionary[key] for key in ids), key=api._json_text)
                relation['control_paths'] = api._json_text(expanded)
            self.assertEqual(new, old, scenario)
        query = api.query_historical_issuer_links(out, receipt['manifest_sha256'], reference='201012')
        referenced = {key for r in query['relacao_trimestral'] for key in json.loads(r['control_paths'])}
        self.assertEqual({r['observation_id'] for r in query['caminhos_societarios']}, referenced)
        self.assertEqual(api.query_historical_issuer_links(out, receipt['manifest_sha256'], entity='UNKNOWN')['caminhos_societarios'], [])

    def test_writer_refuses_oversize_before_manifest(self):
        api = self.api()
        args = self.packages()
        output = self.root / 'oversize'
        prepared = api._prepare(args[0], api.cvm_reader.verify_cvm_metadata(args[0], args[1]),
                                args[2], args[4], api.corporate_reader.verify_corporate_metadata(args[4], args[5]))
        with mock.patch.object(api, '_prepare', return_value=prepared), mock.patch.object(api, 'MAX_TABLE_BYTES', 300), self.assertRaisesRegex(ValueError, 'size|limit|large'):
            api.build_historical_issuer_links(*args, output)
        self.assertFalse((output / 'manifest.json').exists())
        self.assertTrue(all(p.stat().st_size <= 300 for p in output.glob('*.csv')))


    def test_normalized_paths_reject_tamper_and_repinned_missing_extra_or_crossrefs(self):
        self.rows[0]['CodInst'] = '11111111'
        self.members = {'participacao_sociedade': csv_bytes('participacao_sociedade', [
            dict(row(ID_Sociedade='1', CNPJ='11.111.111/0001-00', Tipo_Sociedade='Controlada'), CNPJ_Companhia='00.000.000/0001-91')])}
        out, receipt, _ = self.build()
        api = self.api()
        _, tables = api._load(out, receipt['manifest_sha256'])
        original = {p.name: p.read_bytes() for p in out.iterdir()}
        cases = [('caminhos_societarios', 'id'), ('caminhos_societarios', 'issuer'),
                 ('caminhos_societarios', 'terminal'), ('caminhos_societarios', 'date'),
                 ('caminhos_societarios', 'support'), ('caminhos_societarios', 'missing'),
                 ('caminhos_societarios', 'extra'), ('relacao_trimestral', 'crossref')]
        for kind, mutation in cases:
            records = json.loads(json.dumps(tables[kind]))
            if mutation == 'missing':
                records.clear()
            elif mutation == 'extra':
                records.append(dict(records[0], observation_id='caminho:' + '0' * 64))
            elif mutation == 'crossref':
                records[0]['control_paths'] = api._json_text(['caminho:' + '0' * 64])
            elif mutation == 'date':
                route = json.loads(records[0]['route_json'])
                route[0]['date'] = '2010-09-30'
                records[0]['route_json'] = api._json_text(route)
                records[0]['observation_id'] = 'caminho:' + hashlib.sha256(records[0]['route_json'].encode('utf8')).hexdigest()
            else:
                field = dict(id='observation_id', issuer='issuer_full', terminal='terminal_basic', support='corporate_support')[mutation]
                records[0][field] = '[]' if mutation == 'support' else '0' * 14
            path = out / (kind + '.csv')
            path.write_bytes(api._csv_bytes(api.SCHEMAS[kind], records))
            with self.subTest(mutation=mutation, repin=False), self.assertRaises(ValueError):
                api.verify_historical_issuer_links(out, receipt['manifest_sha256'])
            manifest = json.loads(original['manifest.json'])
            manifest['files'][path.name].update(sha256=sha(path), bytes=path.stat().st_size, rows=len(records))
            manifest['counts'][path.name] = len(records)
            # Repin even quality/counts, so hashes and inventory alone cannot
            # explain rejection; semantic replay must reject the altered graph.
            changed_tables = dict(tables, **{kind: records})
            (out / 'quality.json').unlink()
            manifest['files']['quality.json'] = api.cvm_reader._write_json(out / 'quality.json', api._quality(changed_tables))
            (out / 'manifest.json').unlink()
            api.cvm_reader._write_json(out / 'manifest.json', manifest)
            with self.subTest(mutation=mutation, repin=True), self.assertRaises(ValueError):
                api.verify_historical_issuer_links(out, sha(out / 'manifest.json'))
            for name, raw in original.items():
                (out / name).write_bytes(raw)


    def test_stream_writer_exact_byte_budget_and_canonical_nulls(self):
        api = self.api()
        fields = ('id', 'null', 'blank', 'literal')
        records = [dict(id='0001', null=None, blank='', literal='ação,"quoted"\nline\r\n')]
        canonical = api._csv_bytes(fields, records)
        path = self.root / 'stream.csv'
        with mock.patch.object(api, 'MAX_TABLE_BYTES', len(canonical)):
            entry = api._write_csv(path, fields, records)
        self.assertEqual(path.read_bytes(), canonical)
        self.assertEqual(entry['bytes'], len(canonical))
        self.assertEqual(entry['sha256'], hashlib.sha256(canonical).hexdigest())
        self.assertEqual(api._parse_csv(path.read_bytes(), fields), records)
        with mock.patch.object(api, 'MAX_TABLE_BYTES', len(canonical) - 1), self.assertRaisesRegex(ValueError, 'size limit'):
            api._write_csv(self.root / 'too-large.csv', fields, records)
        self.assertLess((self.root / 'too-large.csv').stat().st_size, len(canonical))

class IssuerSupplementAdmissionTests(unittest.TestCase):
    """Finite curated evidence; no PDF extraction or relationship derivation."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.api = importlib.import_module('bank_quality.historical_issuer_links')
        self.index = self.root / 'index.json'
        self.text = '😀 Companhia Alfa 00.123.456/0001-00 CIK 000123 CVM 906 ALFA34 F001\n'
        self.raw = self.text.encode('utf8')
        (self.root / 'body.pdf').write_bytes(b'%PDF synthetic, manually reviewed projection')
        (self.root / 'projection.txt').write_bytes(self.raw)
        self.source = dict(alias='synthetic page 1', url='https://example.test/document',
            body_path='body.pdf', body_sha256=sha(self.root / 'body.pdf'),
            body_bytes=(self.root / 'body.pdf').stat().st_size, retrieved_at='2026-10-14T00:00:00Z',
            publication_date='2024-12-31', source_nature='issuer_document', document_state='substantive',
            projection=dict(path='projection.txt', sha256=sha(self.root / 'projection.txt'),
                            bytes=len(self.raw), representation='raw PyMuPDF page.get_text, manually reviewed',
                            body_sha256=sha(self.root / 'body.pdf'), page=1))
        self.identifiers = [dict(namespace='CNPJ14', literal='00123456000100', source_id='S', locator=self.loc()),
                            dict(namespace='CIK', literal='000123', source_id='S', locator=self.loc())]
        self.company = dict(role='company', native_name='Companhia Alfa', identifiers=self.identifiers,
                            native_payload=dict(name='Companhia Alfa', null=None, blank='', dash='-', values=['0001', None]))
        self.operator = dict(role='operator_br', native_name='Operadora Alfa', identifiers=[json.loads(json.dumps(self.identifiers[0]))],
                             native_payload={})
        self.base_claim = dict(fact_type='issuer_identity', subject_id='C', object_id=None,
            native_payload=dict(date_purpose='snapshot', percentage='50.0000000000000000000001'),
            fact_date='2024-12-31', reference='202412', time_state='document_point',
            support=[dict(source_id='S', locator=self.loc())], support_claim_ids=[],
            evidence_nature='documentary_declaration', identity_confidence='high', temporal_confidence='high',
            conflict_state='none_reported', adoption_state='observation', rationale=None)
        self.association = dict(self.base_claim, fact_type='analytical_identification', object_id='O',
            support_claim_ids=['B'], evidence_nature='analytical_inference', time_state='analytical_point',
            adoption_state='association', rationale='Reviewed analytical composition, not legal certification')
        self.value = dict(contract='historical-issuer-supplement-input-v1', sources=[self.source],
                          entities=[self.company, self.operator], claims=[self.base_claim, self.association],
                          unresolved=[dict(candidate_id='C', missing_claim_kind='temporal_coverage',
                              reason='No historical interval', evidence_needed='Dated source', support_claim_ids=['B'])])

    def loc(self, excerpt=None):
        excerpt = self.text if excerpt is None else excerpt
        start = self.text.index(excerpt)
        return dict(start=start, end=start + len(excerpt), excerpt=excerpt)

    def canonical(self, value):
        return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf8')

    def fixture(self):
        """Fresh IDs and explicit references, retaining payload order/types exactly."""
        data = json.loads(json.dumps(self.value))
        refs = {}
        for collection, field, prefix, aliases in (
                ('sources', 'source_id', 'source', ['S', 'T']),
                ('entities', 'entity_id', 'entity', ['C', 'O', 'G']),
                ('claims', 'claim_id', 'claim', ['B', 'A', 'Z']),
                ('unresolved', 'unresolved_id', 'unresolved', ['U'])):
            def replace(value):
                if isinstance(value, dict):
                    return {k: replace(v) for k, v in value.items()}
                if isinstance(value, list):
                    return [replace(v) for v in value]
                return refs.get(value, value) if isinstance(value, str) else value
            for ordinal, record in enumerate(data[collection]):
                record = replace(record)
                for key in ('identifiers', 'support'):
                    if key in record:
                        record[key].sort(key=lambda r: ((r.get('namespace', ''), r.get('literal', ''),
                            r['source_id'], r['locator']['start'], r['locator']['end'], r['locator']['excerpt'])))
                if 'support_claim_ids' in record:
                    record['support_claim_ids'].sort()
                digest = hashlib.sha256(self.canonical(record)[:-1]).hexdigest()
                record[field] = prefix + ':' + digest
                refs[aliases[ordinal]] = record[field]
                data[collection][ordinal] = record
            data[collection].sort(key=lambda r: r[field])
        return data

    def write(self, data=None, raw=None):
        self.index.write_bytes(raw if raw is not None else self.canonical(self.fixture() if data is None else data))
        return sha(self.index)

    def admit(self, data=None, raw=None):
        return self.api.validate_issuer_supplement_index(self.index, self.write(data, raw), self.root)

    def test_summary_and_authenticated_private_payload_preserve_tokens(self):
        data = self.fixture()
        result = self.admit(data)
        self.assertEqual(result, dict(contract=data['contract'], index_sha256=sha(self.index),
            counts=dict(sources=1, entities=2, claims=2, unresolved=1)))
        admitted = self.api._admit_issuer_supplement_index(self.index, sha(self.index), self.root)
        for name in ('sources', 'entities', 'claims', 'unresolved'):
            self.assertEqual(admitted[name], data[name])
        self.assertEqual(admitted['evidence'][data['sources'][0]['source_id']]['text'], self.text)
        self.assertEqual(admitted['evidence'][data['sources'][0]['source_id']]['body'], (self.root / 'body.pdf').read_bytes())
        self.assertNotIn('associations', result)

    def test_external_pin_canonical_json_duplicate_keys_and_numbers(self):
        pin = self.write()
        with self.assertRaises(ValueError):
            self.api.validate_issuer_supplement_index(self.index, '0' * 64, self.root)
        for raw in (json.dumps(self.fixture()).encode(), self.canonical(self.fixture()).rstrip(b'\n'),
                    b'{"contract":"x","contract":"x"}\n', b'{"value":NaN}\n', b'{"value":Infinity}\n'):
            with self.subTest(raw=raw[:80]), self.assertRaises(ValueError):
                self.admit(raw=raw)
        self.base_claim['native_payload']['native_metadata'] = [7, True, 0.1]
        data = self.fixture()
        self.admit(data)
        admitted = self.api._admit_issuer_supplement_index(self.index, sha(self.index), self.root)
        self.assertEqual(admitted['claims'], data['claims'])
        for number in (float('nan'), float('inf'), float('-inf')):
            self.base_claim['native_payload']['native_metadata'] = number
            with self.assertRaises(ValueError):
                self.admit()

    def test_closed_schemas_and_exact_ids(self):
        original = self.fixture()
        for collection, position in (('sources', 0), ('entities', 0), ('claims', 0), ('unresolved', 0)):
            for action in ('extra', 'missing', 'id'):
                data = json.loads(json.dumps(original))
                record = data[collection][position]
                if action == 'extra':
                    record['academic_eligibility'] = True
                elif action == 'missing':
                    record.pop(next(k for k in record if not k.endswith('_id')))
                else:
                    record[collection[:-1] + '_id' if collection != 'entities' else 'entity_id'] = 'bad'
                with self.subTest(collection=collection, action=action), self.assertRaises(ValueError):
                    self.admit(data)
        data = dict(original, weights={})
        with self.assertRaises(ValueError):
            self.admit(data)

    def test_set_lists_reject_duplicates_and_noncanonical_order(self):
        original = self.fixture()
        for collection in ('sources', 'entities', 'claims', 'unresolved'):
            data = json.loads(json.dumps(original))
            data[collection].append(data[collection][0])
            with self.subTest(collection=collection), self.assertRaises(ValueError):
                self.admit(data)
        for collection in ('entities', 'claims'):
            data = json.loads(json.dumps(original))
            data[collection].reverse()
            with self.assertRaises(ValueError):
                self.admit(data)
        self.company['identifiers'].append(dict(self.identifiers[0]))
        with self.assertRaises(ValueError):
            self.admit()

    def test_nested_set_order_and_duplicates(self):
        original = self.fixture()
        for field in ('identifiers', 'support', 'support_claim_ids'):
            data = json.loads(json.dumps(original))
            record = next(r for r in data['entities'] if r['role'] == 'company') if field == 'identifiers' else data['claims'][0]
            if not record[field]:
                record = data['claims'][1]
            record[field].append(record[field][0])
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.admit(data)
        data = json.loads(json.dumps(original))
        next(r for r in data['entities'] if r['role'] == 'company')['identifiers'].reverse()
        with self.assertRaises(ValueError):
            self.admit(data)

    def test_paths_hashes_sizes_projection_and_unicode_offsets(self):
        for field, value in (('body_path', '../outside'), ('body_path', '/absolute'),
                ('body_path', 'C:/outside'), ('body_path', 'folder\\body'), ('body_path', './body.pdf'),
                ('body_sha256', '0' * 64), ('body_bytes', 1), ('body_bytes', True)):
            old = self.source[field]
            self.source[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.admit()
            self.source[field] = old
        for field, value in (('sha256', '0' * 64), ('bytes', 1), ('body_sha256', '1' * 64),
                             ('page', 0), ('page', True), ('representation', ''), ('path', 'body.pdf')):
            old = self.source['projection'][field]
            self.source['projection'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.admit()
            self.source['projection'][field] = old
        for locator in (dict(start=1, end=len(self.text), excerpt=self.text),
                        dict(start=False, end=len(self.text), excerpt=self.text),
                        dict(start=-1, end=4, excerpt='abc'), dict(start=0, end=0, excerpt=''),
                        dict(start=0, end=len(self.text.encode()), excerpt=self.text),
                        dict(start=0, end=len(self.text), excerpt=self.text.rstrip())):
            self.base_claim['support'][0]['locator'] = locator
            with self.subTest(locator=locator), self.assertRaises(ValueError):
                self.admit()
        self.base_claim['support'][0]['locator'] = self.loc('Companhia Alfa')
        self.assertEqual(self.admit()['counts']['claims'], 2)

    def test_budget_boundaries_and_deduplicated_evidence(self):
        pin = self.write()
        with mock.patch.object(self.api, 'MAX_SUPPLEMENT_INDEX_BYTES', self.index.stat().st_size - 1), self.assertRaises(ValueError):
            self.api.validate_issuer_supplement_index(self.index, pin, self.root)
        with mock.patch.object(self.api, 'MAX_SUPPLEMENT_BODY_BYTES', self.source['body_bytes'] - 1), self.assertRaises(ValueError):
            self.admit()
        total = self.index.stat().st_size + self.source['body_bytes'] + len(self.raw)
        with mock.patch.object(self.api, 'MAX_SUPPLEMENT_EVIDENCE_BYTES', total - 1), self.assertRaises(ValueError):
            self.admit()
        # Two distinct sources can reuse the same authenticated bytes without double counting.
        data = self.fixture()
        source = dict(data['sources'][0], alias='same body different provenance')
        source.pop('source_id')
        source['source_id'] = 'source:' + hashlib.sha256(self.canonical(source)[:-1]).hexdigest()
        data['sources'].append(source)
        data['sources'].sort(key=lambda r: r['source_id'])
        self.write(data)
        total = self.index.stat().st_size + self.source['body_bytes'] + len(self.raw)
        with mock.patch.object(self.api, 'MAX_SUPPLEMENT_EVIDENCE_BYTES', total - 1), self.assertRaisesRegex(ValueError, 'budget'):
            self.admit(data)
        with mock.patch.object(self.api, 'MAX_SUPPLEMENT_EVIDENCE_BYTES', total):
            self.assertEqual(self.admit(data)['counts']['sources'], 2)
            admitted = self.api._admit_issuer_supplement_index(self.index, sha(self.index), self.root)
        first, second = (admitted['evidence'][source['source_id']] for source in data['sources'])
        self.assertIs(first['body'], second['body'])
        self.assertIs(first['projection'], second['projection'])
        self.assertIs(first['text'], second['text'])

    def test_bundle_budget_includes_index_without_any_evidence(self):
        data = dict(contract='historical-issuer-supplement-input-v1', sources=[], entities=[], claims=[], unresolved=[])
        pin = self.write(data)
        total = self.index.stat().st_size
        with mock.patch.object(self.api, 'MAX_SUPPLEMENT_EVIDENCE_BYTES', total - 1), self.assertRaisesRegex(ValueError, 'budget'):
            self.api.validate_issuer_supplement_index(self.index, pin, self.root)
        with mock.patch.object(self.api, 'MAX_SUPPLEMENT_EVIDENCE_BYTES', total):
            self.assertEqual(self.api.validate_issuer_supplement_index(self.index, pin, self.root)['counts']['sources'], 0)

    def test_source_dates_projection_optional_and_blocked_capture(self):
        for field, value in (('publication_date', '2024-02-30'), ('publication_date', ''),
                ('retrieved_at', '2024-01-01T00:00:00'), ('retrieved_at', 'invalid'),
                ('source_nature', 'search'), ('document_state', 'accepted')):
            old = self.source[field]
            self.source[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.admit()
            self.source[field] = old
        self.source['projection'] = None
        with self.assertRaises(ValueError):
            self.admit()
        self.value['claims'] = []
        self.value['unresolved'] = []
        self.company['identifiers'] = []
        self.operator['identifiers'] = []
        self.assertEqual(self.admit()['counts']['claims'], 0)

    def test_role_type_and_object_matrix(self):
        for field, value in (('subject_id', 'O'), ('object_id', 'O'), ('fact_type', 'control')):
            old = self.base_claim[field]
            self.base_claim[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.admit()
            self.base_claim[field] = old
        for fact_type in ('instrument_program', 'instrument_observation', 'bcb_membership', 'participation_declared'):
            self.base_claim['fact_type'] = fact_type
            with self.subTest(fact_type=fact_type), self.assertRaises(ValueError):
                self.admit()
        self.base_claim['fact_type'] = 'issuer_identity'
        self.base_claim['adoption_state'] = 'association'
        with self.assertRaises(ValueError):
            self.admit()

    def test_identifier_namespace_literal_and_source_proof(self):
        identifier = self.identifiers[0]
        for namespace, literal in (('TICKER', 'ALFA34'), ('CNPJ14', '00123456000101'),
                ('CNPJ14', '00.123.456/0001-00'), ('CNPJ14', '００１２３４５６０００１００'),
                ('CNPJ_BASE8', '00123457'), ('CIK', '12345678901'), ('CVM_CODE', '000999'),
                ('LEI', 'a' * 20), ('CNPJ14', ''), ('UNKNOWN', '00123456')):
            identifier['namespace'], identifier['literal'] = namespace, literal
            with self.subTest(namespace=namespace, literal=literal), self.assertRaises(ValueError):
                self.admit()
        data = self.fixture()
        next(r for r in data['entities'] if r['role'] == 'company')['identifiers'][0]['literal'] = 123
        with self.assertRaises(ValueError):
            self.admit(data)
        for namespace, literal in (('CNPJ14', '00123456000100'), ('CNPJ_BASE8', '00123456'),
                                   ('CVM_CODE', '000906'), ('CIK', '000123')):
            identifier['namespace'], identifier['literal'] = namespace, literal
            if namespace == 'CIK':
                self.company['identifiers'] = [identifier]
            self.assertEqual(self.admit()['counts']['entities'], 2)

    def test_cik_sec_url_rule_exact_host_segment_and_name_locator(self):
        self.company['identifiers'] = [dict(namespace='CIK', literal='456', source_id='S', locator=self.loc('Companhia Alfa'))]
        self.source['url'] = 'https://www.sec.gov/Archives/edgar/data/456/filing.htm'
        self.admit()
        for url in ('https://evil.test/Archives/edgar/data/456/filing.htm',
                    'https://www.sec.gov.evil.test/Archives/edgar/data/456/filing.htm',
                    'https://www.sec.gov/Archives/edgar/data/0456/filing.htm'):
            self.source['url'] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.admit()
        self.source['url'] = 'https://www.sec.gov/Archives/edgar/data/456/filing.htm'
        self.company['identifiers'][0]['locator'] = self.loc('Alfa')
        with self.assertRaises(ValueError):
            self.admit()

    def test_numeric_identifier_proof_requires_isolated_tokens(self):
        self.value['claims'] = []
        self.value['unresolved'] = []
        self.operator['identifiers'] = []
        for namespace, literal, text in (
                ('CVM_CODE', '000906', '-906'), ('CVM_CODE', '000906', '+906'),
                ('CVM_CODE', '000906', '906/12'), ('CIK', '000123', '000123/12'),
                ('CNPJ14', '00123456000100', 'X00123456000100'),
                ('CNPJ_BASE8', '00123456', 'X00123456')):
            self.text = text
            (self.root / 'projection.txt').write_bytes(text.encode('utf8'))
            self.source['projection'].update(sha256=sha(self.root / 'projection.txt'), bytes=len(text.encode('utf8')))
            self.company['identifiers'] = [dict(namespace=namespace, literal=literal, source_id='S', locator=self.loc())]
            with self.subTest(namespace=namespace, text=text), self.assertRaisesRegex(ValueError, 'source proof'):
                self.admit()

    def test_case_variant_paths_cannot_hide_alias_collisions(self):
        data = self.fixture()
        # Both paths must exist on case-sensitive hosts, regardless of source
        # ID ordering. On Windows this writes identical bytes to the same file.
        (self.root / 'BODY.PDF').write_bytes((self.root / 'body.pdf').read_bytes())
        source = dict(data['sources'][0], alias='case-variant', body_path='BODY.PDF')
        source.pop('source_id')
        source['source_id'] = 'source:' + hashlib.sha256(self.canonical(source)[:-1]).hexdigest()
        data['sources'].append(source)
        data['sources'].sort(key=lambda record: record['source_id'])
        with self.assertRaisesRegex(ValueError, 'path collision'):
            self.admit(data)

    def test_temporal_rules_confidence_and_rationale(self):
        for field, value in (('reference', '202411'), ('reference', '202512'), ('reference', 202412),
                ('fact_date', '2024-12-30'), ('fact_date', '2024-02-30'), ('time_state', 'unknown'),
                ('identity_confidence', 0.9), ('temporal_confidence', 'certain'), ('conflict_state', 'certified'),
                ('adoption_state', 'accepted')):
            old = self.base_claim[field]
            self.base_claim[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.admit()
            self.base_claim[field] = old
        for purpose in ('approval', 'publication', 'announcement', 'document_reference', None):
            self.base_claim['native_payload']['date_purpose'] = purpose
            with self.subTest(purpose=purpose), self.assertRaises(ValueError):
                self.admit()
        self.base_claim['native_payload']['date_purpose'] = 'snapshot'
        self.base_claim['fact_type'] = 'event'
        with self.assertRaises(ValueError):
            self.admit()
        self.base_claim['reference'] = None
        self.base_claim['fact_date'] = '2024-12-10'
        self.admit()
        for field, value in (('reference', None), ('rationale', ''), ('evidence_nature', 'literal_observation'),
                             ('support_claim_ids', [])):
            old = self.association[field]
            self.association[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.admit()
            self.association[field] = old

    def test_transitive_support_rejects_laundering_and_accepts_candidates(self):
        middle = dict(self.base_claim, native_payload=dict(date_purpose='snapshot', note='intermediate'), support_claim_ids=['B'])
        self.value['claims'] = [self.base_claim, middle, dict(self.association, support_claim_ids=['A'])]
        # Fixture aliases B, A are references to the first two claims, independent of list sorting.
        for field, value in (('conflict_state', 'unresolved'), ('conflict_state', 'contradicted'),
                ('adoption_state', 'candidate'), ('fact_type', 'capture_status')):
            old = self.base_claim[field]
            self.base_claim[field] = value
            if field == 'conflict_state':
                self.base_claim['rationale'] = 'Visible unresolved conflict'
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.admit()
            self.value['claims'][2]['adoption_state'] = 'candidate'
            self.assertEqual(self.admit()['counts']['claims'], 3)
            self.value['claims'][2]['adoption_state'] = 'association'
            self.base_claim[field] = old
        self.base_claim['rationale'] = None

    def test_document_states_and_operator_identifiers_control_adoptability(self):
        for state in ('blocked', 'shell', 'search_excerpt'):
            self.source['document_state'] = state
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.admit()
        self.source['document_state'] = 'substantive'
        self.operator['identifiers'] = []
        with self.assertRaises(ValueError):
            self.admit()
        self.association['adoption_state'] = 'candidate'
        self.admit()

    def test_dangling_claim_refs_self_and_cycles(self):
        original = self.fixture()
        for refs in (['claim:' + '0' * 64], [original['claims'][0]['claim_id']]):
            data = json.loads(json.dumps(original))
            data['claims'][0]['support_claim_ids'] = refs
            with self.assertRaises(ValueError):
                self.admit(data)
        data = json.loads(json.dumps(original))
        data['claims'][0]['support_claim_ids'] = [data['claims'][1]['claim_id']]
        data['claims'][1]['support_claim_ids'] = [data['claims'][0]['claim_id']]
        with self.assertRaises(ValueError):
            self.admit(data)
        self.value['unresolved'][0]['candidate_id'] = 'missing'
        with self.assertRaises(ValueError):
            self.admit()

    def test_cli_summary_and_malformed_input_exit_status(self):
        pin = self.write()
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'build-historical-issuer-links.py'
        args = [sys.executable, '-B', str(script), 'supplement-check', str(self.index),
                '--index-sha256', pin, '--evidence-root', str(self.root)]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['counts']['entities'], 2)
        args[args.index(pin)] = '0' * 64
        bad = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertNotIn('Traceback', bad.stderr)

    def test_transitive_document_state_cannot_be_laundered_by_clean_terminal(self):
        self.value['sources'].append(dict(self.source, alias='separate substantive support'))
        self.company['identifiers'] = [dict(identifier, source_id='T') for identifier in self.identifiers]
        self.operator['identifiers'] = [dict(self.operator['identifiers'][0], source_id='T')]
        self.association['support'] = [dict(source_id='T', locator=self.loc())]
        middle = dict(self.base_claim, native_payload=dict(date_purpose='snapshot', intermediate='literal'),
                      support=[dict(source_id='T', locator=self.loc())], support_claim_ids=['B'])
        terminal = dict(self.association, support_claim_ids=['A'])
        self.value['claims'] = [self.base_claim, middle, terminal]
        for state in ('blocked', 'shell', 'search_excerpt'):
            self.source['document_state'] = state
            self.base_claim['fact_type'] = 'capture_status' if state != 'search_excerpt' else 'issuer_identity'
            self.base_claim['adoption_state'] = 'observation' if state != 'search_excerpt' else 'candidate'
            with self.subTest(state=state), self.assertRaisesRegex(ValueError, 'inadmissible transitive support'):
                self.admit()
            terminal['adoption_state'] = 'candidate'
            self.assertEqual(self.admit()['counts']['claims'], 3)
            terminal['adoption_state'] = 'association'

    def test_native_membership_requires_closed_perspective_and_point(self):
        self.value['entities'].append(dict(role='bcb_unit', native_name='Native F001',
            identifiers=[dict(namespace='BCB_CODINST', literal='F001', source_id='S', locator=self.loc())], native_payload={}))
        self.base_claim.update(fact_type='bcb_membership', subject_id='O', object_id='G', evidence_nature='native_bcb')
        self.base_claim['native_payload']['perspective'] = 'financeiro'
        self.admit()
        for field, value in (('reference', None), ('time_state', 'unknown'), ('evidence_nature', 'documentary_declaration')):
            old = self.base_claim[field]
            self.base_claim[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.admit()
            self.base_claim[field] = old
        self.base_claim['native_payload']['perspective'] = 'consolidated'
        with self.assertRaises(ValueError):
            self.admit()

    def test_projection_pin_is_review_boundary_and_not_pdf_reextraction(self):
        # Synthetic PDF cannot produce this text. Declared reviewed projection is
        # the contract: byte tampering fails, an explicitly repinned review is a
        # new authenticated declaration rather than an automatic truth claim.
        (self.root / 'projection.txt').write_text('changed projection', encoding='utf8')
        with self.assertRaises(ValueError):
            self.admit()
        self.text = 'A different manually reviewed document text'
        projected = self.text.encode('utf8')
        (self.root / 'projection.txt').write_bytes(projected)
        self.source['projection'].update(sha256=sha(self.root / 'projection.txt'), bytes=len(projected))
        self.company['identifiers'] = []
        self.operator['identifiers'] = []
        self.value['claims'] = [dict(self.base_claim, support=[dict(source_id='S', locator=self.loc())])]
        self.admit()

    def test_seventeen_visible_candidates_do_not_require_associations(self):
        self.value['claims'] = []
        self.value['unresolved'] = []
        data = self.fixture()
        template = next(entity for entity in data['entities'] if entity['role'] == 'company')
        data['entities'] = []
        for ordinal in range(17):
            entity = dict(template, native_name='Candidate ' + str(ordinal), identifiers=[])
            entity.pop('entity_id')
            entity['entity_id'] = 'entity:' + hashlib.sha256(self.canonical(entity)[:-1]).hexdigest()
            data['entities'].append(entity)
        data['entities'].sort(key=lambda entity: entity['entity_id'])
        self.assertEqual(self.admit(data)['counts'], dict(sources=1, entities=17, claims=0, unresolved=0))

    def test_symlink_evidence_rejected_when_platform_supports_it(self):
        link = self.root / 'linked.txt'
        try:
            link.symlink_to(self.root / 'projection.txt')
        except OSError:
            self.skipTest('OS does not grant symlink creation')
        self.source['projection']['path'] = 'linked.txt'
        with self.assertRaisesRegex(ValueError, 'Symlink|reparse'):
            self.admit()

    def test_index_rechecked_after_evidence_authentication(self):
        pin = self.write()
        original = self.api.cvm_reader._pinned
        def mutate_index_after_projection(path, expected, limit):
            raw = original(path, expected, limit)
            if Path(path).name == 'projection.txt':
                self.index.write_bytes(self.index.read_bytes() + b' ')
            return raw
        with mock.patch.object(self.api.cvm_reader, '_pinned', side_effect=mutate_index_after_projection), self.assertRaises(ValueError):
            self.api.validate_issuer_supplement_index(self.index, pin, self.root)

class IssuerSupplementPackageTests(unittest.TestCase):
    """Exercise real tiny authenticated core and supplement packages."""
    canonical = IssuerSupplementAdmissionTests.canonical
    fixture = IssuerSupplementAdmissionTests.fixture
    write = IssuerSupplementAdmissionTests.write
    loc = IssuerSupplementAdmissionTests.loc

    def setUp(self):
        IssuerSupplementAdmissionTests.setUp(self)
        self.core_fixture = HistoricalTests()
        self.core_fixture.setUp()
        self.addCleanup(self.core_fixture.doCleanups)
        for native in self.core_fixture.rows:
            if native['CodInst'] == '00000000':
                native['CodInst'] = '00123456'
            native['CnpjInstituicaoLider'] = '00123456'
        self.core, self.core_receipt, _ = self.core_fixture.build()
        self.core_pin = self.core_receipt['manifest_sha256']
        self.output = self.root / 'supplement'

    def build_supplement(self):
        self.assertTrue(callable(getattr(self.api, 'build_issuer_supplement', None)), 'R3b supplement builder missing')
        pin = self.write()
        receipt = self.api.build_issuer_supplement(self.index, pin, self.root,
            self.core, self.core_pin, self.output)
        return receipt, pin

    def verify(self, receipt, pin):
        return self.api.verify_issuer_supplement(self.output, receipt['manifest_sha256'], pin,
            self.core, self.core_pin)

    def query(self, receipt, pin, **filters):
        return self.api.query_issuer_supplement(self.output, receipt['manifest_sha256'], pin,
            self.core, self.core_pin, **filters)

    def test_build_closed_package_replay_and_source_independence(self):
        before = {p.name: sha(p) for p in self.core.iterdir()}
        receipt, pin = self.build_supplement()
        self.assertEqual({p.name for p in self.output.iterdir()},
            {'manifest.json', 'sources.json', 'entities.json', 'claims.json',
             'relations.json', 'unresolved.json', 'quality.json', 'evidence'})
        self.assertEqual(len(list((self.output / 'evidence').iterdir())), 2)
        self.index.unlink()
        (self.root / 'body.pdf').unlink()
        (self.root / 'projection.txt').unlink()
        self.verify(receipt, pin)
        self.assertEqual(before, {p.name: sha(p) for p in self.core.iterdir()})
        result = self.query(receipt, pin)
        self.assertEqual(result['quality']['identity_certified'], False)
        self.assertEqual(result['quality']['academic_eligibility_adopted'], False)
        self.assertEqual(result['quality']['market_coverage_incomplete'], True)

    def test_punctual_native_associations_preserve_group_leader_support(self):
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin, reference='202412')
        rows = result['associations']
        self.assertEqual({(r['reference'], r['perspective'], r['entity']) for r in rows},
            {('202412', 'individual', '00123456'), ('202412', 'financeiro', 'F001'),
             ('202412', 'prudencial', 'P001')})
        self.assertTrue(all(r['academic_eligibility'] == 'not_evaluated' for r in rows))
        financial = next(r for r in result['vinculos_cadastrais'] if r['perspective'] == 'financeiro')
        self.assertEqual((financial['institution_Tcb'], financial['group_Tcb'], financial['leader_Tcb']),
                         ('B3', 'F', 'B3'))
        self.assertEqual(financial['leader_scope'], 'nativo_nao_desambiguado')
        self.assertEqual(self.query(receipt, pin, reference='201012')['associations'], [])

    def test_external_index_core_authority_cannot_be_replaced_by_output_repin(self):
        receipt, pin = self.build_supplement()
        with self.assertRaises(ValueError):
            self.verify(receipt, '0' * 64)
        with self.assertRaises(ValueError):
            self.api.verify_issuer_supplement(self.output, receipt['manifest_sha256'], pin,
                self.core, '0' * 64)
        # A fully rehashed output with altered input payload still fails external index authority.
        entities = json.loads((self.output / 'entities.json').read_bytes())
        entities[0]['native_payload']['extra'] = 'unauthorized'
        (self.output / 'entities.json').write_bytes(self.canonical(entities))
        manifest = json.loads((self.output / 'manifest.json').read_bytes())
        manifest['files']['entities.json'].update(sha256=sha(self.output / 'entities.json'),
            bytes=(self.output / 'entities.json').stat().st_size)
        (self.output / 'manifest.json').write_bytes(self.canonical(manifest))
        with self.assertRaises(ValueError):
            self.api.verify_issuer_supplement(self.output, sha(self.output / 'manifest.json'), pin,
                self.core, self.core_pin)

    def test_each_operation_authenticates_core_once(self):
        with mock.patch.object(self.api, '_load', wraps=self.api._load) as load:
            receipt, pin = self.build_supplement()
            self.assertEqual(load.call_count, 1)
        for operation in (self.verify, self.query):
            with mock.patch.object(self.api, '_load', wraps=self.api._load) as load:
                operation(receipt, pin)
                self.assertEqual(load.call_count, 1)

    def test_core_query_optional_trio_requires_all_and_preserves_core_alone(self):
        before = self.api.query_historical_issuer_links(self.core, self.core_pin, reference='202412')
        receipt, pin = self.build_supplement()
        with self.assertRaises(ValueError):
            self.api.query_historical_issuer_links(self.core, self.core_pin, supplement=self.output)
        with mock.patch.object(self.api, '_load', wraps=self.api._load) as load:
            combined = self.api.query_historical_issuer_links(self.core, self.core_pin,
                reference='202412', entity='00123456000100', supplement=self.output,
                expected_supplement_sha256=receipt['manifest_sha256'], expected_supplement_index_sha256=pin)
            self.assertEqual(load.call_count, 1)
            self.assertEqual(len(combined['suplemento']['associations']), 3)
        self.assertEqual(self.api.query_historical_issuer_links(self.core, self.core_pin, reference='202412'), before)

    def test_unknown_does_not_expand_and_candidates_remain_visible(self):
        self.association.update(reference=None, fact_date=None, time_state='unknown')
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin, reference='201003')
        self.assertEqual(result['associations'], [])
        self.assertEqual(len(result['undated_associations']), 1)
        self.assertEqual(result['undated_associations'][0]['reference'], None)
        self.assertEqual(result['cadastro'], [])

    def test_missing_native_unit_is_gap_not_name_fallback(self):
        self.operator['identifiers'] = [dict(namespace='CNPJ14', literal='00000000000191',
            source_id='S', locator=self.loc())]
        # Append explicit proof; company keeps its different identifier despite a similar name.
        self.text += '00.000.000/0001-91\n'
        (self.root / 'projection.txt').write_bytes(self.text.encode())
        self.source['projection'].update(sha256=sha(self.root / 'projection.txt'), bytes=len(self.text.encode()))
        self.operator['identifiers'][0]['locator'] = self.loc()
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin)
        self.assertEqual(result['associations'], [])
        self.assertEqual({g['reason'] for g in result['derived_unresolved']}, {'native_unit_missing'})
        self.assertEqual(len(result['entities']), 2)
        self.assertEqual(len(result['unresolved']), 1)

    def repin_file(self, relative, value):
        target = self.output / relative
        target.write_bytes(self.canonical(value))
        manifest = json.loads((self.output / 'manifest.json').read_bytes())
        manifest['files'][relative] = dict(sha256=sha(target), bytes=target.stat().st_size)
        (self.output / 'manifest.json').write_bytes(self.canonical(manifest))
        return sha(self.output / 'manifest.json')

    def test_rehashed_relations_quality_and_manifest_counts_are_replayed(self):
        receipt, pin = self.build_supplement()
        for relative in ('relations.json', 'quality.json'):
            original = (self.output / relative).read_bytes()
            original_manifest = (self.output / 'manifest.json').read_bytes()
            value = json.loads(original)
            if relative == 'relations.json':
                value['associations'][0]['entity'] = 'unapproved'
            else:
                value['identity_certified'] = True
            repin = self.repin_file(relative, value)
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                self.api.verify_issuer_supplement(self.output, repin, pin, self.core, self.core_pin)
            (self.output / relative).write_bytes(original)
            (self.output / 'manifest.json').write_bytes(original_manifest)
        manifest = json.loads((self.output / 'manifest.json').read_bytes())
        manifest['counts']['associations'] += 1
        (self.output / 'manifest.json').write_bytes(self.canonical(manifest))
        with self.assertRaises(ValueError):
            self.api.verify_issuer_supplement(self.output, sha(self.output / 'manifest.json'), pin,
                self.core, self.core_pin)

    def test_closed_inventory_rejects_extra_file_directory_and_missing_evidence(self):
        receipt, pin = self.build_supplement()
        extra = self.output / 'evidence' / 'extra.txt'
        extra.write_text('not declared')
        with self.assertRaises(ValueError):
            self.verify(receipt, pin)
        extra.unlink()
        extra.mkdir()
        with self.assertRaises(ValueError):
            self.verify(receipt, pin)
        extra.rmdir()
        next((self.output / 'evidence').iterdir()).unlink()
        with self.assertRaises(ValueError):
            self.verify(receipt, pin)

    def test_identical_source_bodies_and_projections_are_copied_once(self):
        duplicate = json.loads(json.dumps(self.source))
        duplicate['alias'] = 'same bytes, separately reviewed source'
        self.value['sources'].append(duplicate)
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin)
        self.assertEqual(len(result['sources']), 1)  # only referenced sources in query
        self.assertEqual(self.verify(receipt, pin)['counts']['sources'], 2)
        self.assertEqual(len(list((self.output / 'evidence').iterdir())), 2)

    def test_exact_selectors_and_zero_associations_keep_seventeen_companies(self):
        self.association['adoption_state'] = 'candidate'
        data = self.fixture()
        for n in range(16):
            record = dict(role='company', native_name='Candidate ' + str(n), identifiers=[], native_payload={})
            record['entity_id'] = 'entity:' + hashlib.sha256(self.canonical(record)[:-1]).hexdigest()
            data['entities'].append(record)
        data['entities'].sort(key=lambda r: r['entity_id'])
        pin = self.write(data)
        receipt = self.api.build_issuer_supplement(self.index, pin, self.root, self.core, self.core_pin, self.output)
        result = self.query(receipt, pin, reference='201012', perspective='prudencial')
        self.assertEqual(len([r for r in result['entities'] if r['role'] == 'company']), 17)
        self.assertEqual(result['associations'], [])
        self.assertEqual(result['undated_associations'], [])
        self.assertEqual(len(result['unresolved']), 1)
        for selector in ('Companhia Alfa', '00123456000100', 'CIK:123', 'CNPJ14:00.123.456/0001-00'):
            with self.subTest(selector=selector):
                self.assertEqual(self.query(receipt, pin, company=selector)['entities'], [])
        exact = self.query(receipt, pin, company='CIK:000123')
        self.assertEqual(len(exact['entities']), 2)
        self.assertEqual(len(exact['support_claims']), 2)
        self.assertEqual(exact['derived_unresolved'][0]['reason'], 'support_not_adoptable')

    def test_cli_supplement_build_verify_query_and_optional_trio(self):
        pin = self.write()
        script = Path(__file__).resolve().parents[1] / 'scripts/build-historical-issuer-links.py'
        build = subprocess.run([sys.executable, '-B', str(script), 'supplement-build', str(self.index),
            str(self.core), str(self.output), '--index-sha256', pin, '--core-sha256', self.core_pin,
            '--evidence-root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(build.returncode, 0, build.stderr)
        receipt = json.loads(build.stdout)
        common = [str(self.output), str(self.core), '--manifest-sha256', receipt['manifest_sha256'],
                  '--index-sha256', pin, '--core-sha256', self.core_pin]
        for command in ('supplement-verify', 'supplement-query'):
            child = subprocess.run([sys.executable, '-B', str(script), command, *common], capture_output=True, text=True)
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertEqual(json.loads(child.stdout)['contract'], 'historical-issuer-supplement-v1')
        child = subprocess.run([sys.executable, '-B', str(script), 'query', str(self.core),
            '--manifest-sha256', self.core_pin, '--supplement', str(self.output)], capture_output=True, text=True)
        self.assertNotEqual(child.returncode, 0)

    def test_json_writer_exact_cap_and_existing_output_are_errors(self):
        raw = self.canonical({'unicode': '😀', 'blank': '', 'null': None})
        with mock.patch.object(self.api, 'MAX_TABLE_BYTES', len(raw)):
            self.api._write_supplement_json(self.root / 'exact.json', json.loads(raw))
        self.assertEqual((self.root / 'exact.json').read_bytes(), raw)
        with mock.patch.object(self.api, 'MAX_TABLE_BYTES', len(raw) - 1), self.assertRaises(ValueError):
            self.api._write_supplement_json(self.root / 'over.json', json.loads(raw))
        self.assertFalse((self.root / 'over.json').exists())
        self.output.mkdir()
        pin = self.write()
        with self.assertRaises(ValueError):
            self.api.build_issuer_supplement(self.index, pin, self.root, self.core, self.core_pin, self.output)

    def test_replay_is_byte_identical_and_unknown_filters_do_not_guess_namespaces(self):
        receipt, pin = self.build_supplement()
        second = self.root / 'replay'
        again = self.api.build_issuer_supplement(self.index, pin, self.root, self.core, self.core_pin, second)
        self.assertEqual(again['manifest_sha256'], receipt['manifest_sha256'])
        self.assertEqual({p.relative_to(self.output).as_posix(): p.read_bytes()
                          for p in self.output.rglob('*') if p.is_file()},
                         {p.relative_to(second).as_posix(): p.read_bytes()
                          for p in second.rglob('*') if p.is_file()})
        result = self.api.query_historical_issuer_links(self.core, self.core_pin, entity='00123456',
            supplement=self.output, expected_supplement_sha256=receipt['manifest_sha256'],
            expected_supplement_index_sha256=pin)
        self.assertEqual(result['suplemento']['entities'], [])
        for filters in ({'reference': '202601'}, {'perspective': 'consolidated'}, {'company': ''}):
            with self.subTest(filters=filters), self.assertRaises(ValueError):
                self.query(receipt, pin, **filters)

    def test_candidate_deep_support_blocked_source_is_visible_without_association(self):
        blocked = json.loads(json.dumps(self.source))
        blocked.update(alias='blocked original', document_state='blocked', source_nature='regulator')
        self.value['sources'].append(blocked)
        capture = dict(self.base_claim, fact_type='capture_status', reference=None,
            fact_date=None, time_state='unknown', subject_id='O', object_id=None,
            support=[dict(source_id='T', locator=self.loc())], support_claim_ids=[],
            adoption_state='observation', native_payload=dict(http=403))
        # B -> Z -> blocked; A -> B. Candidate state must never be silently adopted.
        self.base_claim['support_claim_ids'] = ['Z']
        self.association['adoption_state'] = 'candidate'
        self.value['claims'].insert(0, capture)
        # fixture aliases are ordinal: B=capture, A=identity, Z=analytical here;
        # use an explicit topological index instead of conflating those aliases.
        self.value['claims'] = [capture, dict(self.base_claim, support_claim_ids=['B']),
                               dict(self.association, support_claim_ids=['A'])]
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin, company='CIK:000123', reference='202412')
        self.assertEqual(len(result['support_claims']), 3)
        self.assertEqual(len(result['sources']), 2)
        self.assertEqual(result['associations'], [])
        self.assertEqual(result['derived_unresolved'][0]['reason'], 'support_not_adoptable')
        self.assertEqual({s['document_state'] for s in result['sources']}, {'substantive', 'blocked'})

    def test_temporal_event_and_instrument_do_not_become_historical_market_facts(self):
        instrument = dict(role='instrument', native_name='ALFA34', identifiers=[dict(namespace='TICKER',
            literal='ALFA34', source_id='S', locator=self.loc())], native_payload=dict(kind='BDR'))
        self.value['entities'].append(instrument)
        observation = dict(self.base_claim, fact_type='instrument_observation', object_id='G',
            reference=None, fact_date='2026-10-14', time_state='document_point',
            native_payload=dict(market='current'), support_claim_ids=[])
        event = dict(self.base_claim, fact_type='event', object_id='G', reference=None,
            fact_date='2026-10-13', time_state='document_point', native_payload=dict(event='announcement'))
        self.value['claims'] = [self.base_claim, observation, event]
        self.value['unresolved'][0]['support_claim_ids'] = ['B']
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin, reference='201012')
        self.assertEqual(result['associations'], [])
        self.assertEqual(result['claims'], [])
        self.assertEqual(len(result['instrument_observations']), 1)
        self.assertEqual(result['events'][0]['fact_date'], '2026-10-13')
        self.assertEqual(result['instrument_observations'][0]['reference'], None)
        self.assertEqual(len(result['instruments']), 1)

    def test_conflicting_operator_bases_are_ambiguous_without_choosing_existing_native(self):
        self.text += '00.000.000/0001-91\n'
        (self.root / 'projection.txt').write_bytes(self.text.encode())
        self.source['projection'].update(sha256=sha(self.root / 'projection.txt'), bytes=len(self.text.encode()))
        self.operator['identifiers'].append(dict(namespace='CNPJ14', literal='00000000000191',
            source_id='S', locator=self.loc()))
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin)
        self.assertEqual(result['associations'], [])
        self.assertEqual(result['derived_unresolved'][0]['reason'], 'native_unit_ambiguous')

    def test_membership_claim_is_compared_to_native_group_same_reference(self):
        unit = dict(role='bcb_unit', native_name='declared group', identifiers=[dict(namespace='BCB_CODINST',
            literal='F001', source_id='S', locator=self.loc())], native_payload={})
        self.value['entities'].append(unit)
        membership = dict(self.base_claim, fact_type='bcb_membership', subject_id='O', object_id='G',
            evidence_nature='native_bcb', native_payload=dict(perspective='prudencial', date_purpose='native_reference'),
            support_claim_ids=[])
        self.value['claims'].append(membership)
        self.association['support_claim_ids'] = ['B', 'Z']
        # Topological order B identity, A membership, Z association.
        self.value['claims'] = [self.base_claim, membership, dict(self.association, support_claim_ids=['B', 'A'])]
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin)
        self.assertEqual(result['associations'], [])
        self.assertEqual(result['derived_unresolved'][0]['reason'], 'native_membership_mismatch')

    def test_empty_group_is_gap_and_leader_absence_is_not_filled(self):
        # Use a new authentic core, not a patched table bypass.
        self.core_fixture.temp.cleanup()
        self.core_fixture = HistoricalTests()
        self.core_fixture.setUp()
        self.addCleanup(self.core_fixture.doCleanups)
        self.core_fixture.rows[0].update(CodInst='00123456', CodConglomeradoFinanceiro='',
            CnpjInstituicaoLider='99999999')
        self.core, self.core_receipt, _ = self.core_fixture.build()
        self.core_pin = self.core_receipt['manifest_sha256']
        receipt, pin = self.build_supplement()
        result = self.query(receipt, pin)
        self.assertEqual({r['perspective'] for r in result['associations']}, {'individual', 'prudencial'})
        self.assertTrue(all(r['leader_support'] is None for r in result['associations']))
        self.assertEqual(result['derived_unresolved'][0]['reason'], 'native_group_empty')
        self.assertEqual(result['derived_unresolved'][0]['perspective'], 'financeiro')

    def test_combined_query_recognizes_formatted_cnpj_without_other_namespace_guessing(self):
        receipt, pin = self.build_supplement()
        result = self.api.query_historical_issuer_links(self.core, self.core_pin, entity='00.123.456/0001-00',
            supplement=self.output, expected_supplement_sha256=receipt['manifest_sha256'],
            expected_supplement_index_sha256=pin)
        self.assertEqual(len(result['suplemento']['associations']), 3)

    def test_unresolved_support_closure_includes_new_entity_gaps_transitively(self):
        data = self.fixture()
        original_company = next(r['entity_id'] for r in data['entities'] if r['role'] == 'company')
        entity = dict(role='company', native_name='Separately identified support company', identifiers=[], native_payload={})
        entity['entity_id'] = 'entity:' + hashlib.sha256(self.canonical(entity)[:-1]).hexdigest()
        data['entities'].append(entity)
        claim = dict(next(r for r in data['claims'] if r['fact_type'] == 'issuer_identity'))
        claim.pop('claim_id')
        claim.update(subject_id=entity['entity_id'], support_claim_ids=[], native_payload={'distinct': True, 'date_purpose': 'snapshot'})
        claim['claim_id'] = 'claim:' + hashlib.sha256(self.canonical(claim)[:-1]).hexdigest()
        data['claims'].append(claim)
        for candidate, support, reason in ((original_company, [claim['claim_id']], 'explicit support dependency'),
                                          (entity['entity_id'], [], 'gap on transitively discovered entity')):
            unresolved = dict(candidate_id=candidate, missing_claim_kind='issuer_chain', reason=reason,
                evidence_needed='Reviewed endpoint evidence', support_claim_ids=support)
            unresolved['unresolved_id'] = 'unresolved:' + hashlib.sha256(self.canonical(unresolved)[:-1]).hexdigest()
            data['unresolved'].append(unresolved)
        for name, field in (('entities', 'entity_id'), ('claims', 'claim_id'), ('unresolved', 'unresolved_id')):
            data[name].sort(key=lambda r: r[field])
        pin = self.write(data)
        receipt = self.api.build_issuer_supplement(self.index, pin, self.root, self.core, self.core_pin, self.output)
        result = self.query(receipt, pin, company='CIK:000123')
        self.assertEqual(len(result['unresolved']), 3)
        self.assertEqual(len(result['entities']), 3)

    def test_quality_counts_curated_gap_kinds_separately_from_derived_gaps(self):
        receipt, pin = self.build_supplement()
        quality = self.query(receipt, pin)['quality']
        self.assertEqual(quality.get('curated_gap_kinds'), {'temporal_coverage': 1})
        self.assertEqual(quality['gap_reasons'], {})

    def test_index_mutation_during_output_projection_leaves_no_accepted_manifest(self):
        pin = self.write()
        original = self.api._write_supplement_json
        def mutate_during_projection(path, value):
            result = original(path, value)
            if Path(path).name == 'quality.json':
                self.index.write_bytes(self.index.read_bytes() + b' ')
            return result
        with mock.patch.object(self.api, '_write_supplement_json', side_effect=mutate_during_projection), self.assertRaises(ValueError):
            self.api.build_issuer_supplement(self.index, pin, self.root, self.core, self.core_pin, self.output)
        self.assertFalse((self.output / 'manifest.json').exists())

    def test_rehashed_evidence_body_or_projection_cannot_change_external_curated_authority(self):
        receipt, pin = self.build_supplement()
        for evidence in (self.output / 'evidence').iterdir():
            original = evidence.read_bytes()
            original_manifest = (self.output / 'manifest.json').read_bytes()
            evidence.write_bytes(original + b' injected')
            manifest = json.loads(original_manifest)
            manifest['files'][evidence.relative_to(self.output).as_posix()] = dict(
                sha256=sha(evidence), bytes=evidence.stat().st_size)
            (self.output / 'manifest.json').write_bytes(self.canonical(manifest))
            with self.subTest(evidence=evidence.suffix), self.assertRaises(ValueError):
                self.api.verify_issuer_supplement(self.output, sha(self.output / 'manifest.json'), pin,
                    self.core, self.core_pin)
            evidence.write_bytes(original)
            (self.output / 'manifest.json').write_bytes(original_manifest)
        self.verify(receipt, pin)

    def test_manifest_counts_do_not_accept_json_boolean_as_integer(self):
        receipt, pin = self.build_supplement()
        manifest = json.loads((self.output / 'manifest.json').read_bytes())
        self.assertEqual(manifest['counts']['sources'], 1)
        manifest['counts']['sources'] = True
        (self.output / 'manifest.json').write_bytes(self.canonical(manifest))
        with self.assertRaises(ValueError):
            self.api.verify_issuer_supplement(self.output, sha(self.output / 'manifest.json'), pin,
                self.core, self.core_pin)

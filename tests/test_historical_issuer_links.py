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

"""Synthetic FRE admission tests: no captured personal or corporate payloads."""
import csv
import hashlib
import importlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


COMMON = 'CNPJ_Companhia Data_Referencia Versao ID_Documento Nome_Companhia'.split()
HEADERS = {
    'participacao_sociedade': COMMON + 'ID_Sociedade Razao_Social CNPJ Tipo_Sociedade Descricao_Atividades Pais_Sede UF_Sede Municipio_Sede Participacao_Emissor Possui_Registro_CVM Codigo_CVM Razao_Aquisicao_Manutencao Data_Valor_Mercado Data_Valor_Contabil Valor_Mercado Valor_Contabil'.split(),
    'posicao_acionaria': COMMON + 'ID_Acionista Acionista Tipo_Pessoa_Acionista CPF_CNPJ_Acionista ID_Acionista_Relacionado Acionista_Relacionado Tipo_Pessoa_Acionista_Relacionado CPF_CNPJ_Acionista_Relacionado Quantidade_Acao_Ordinaria_Circulacao Percentual_Acao_Ordinaria_Circulacao Quantidade_Acao_Preferencial_Circulacao Percentual_Acao_Preferencial_Circulacao Quantidade_Total_Acoes_Circulacao Percentual_Total_Acoes_Circulacao Nacionalidade Sigla_UF Residente_Exterior Representante_Legal Tipo_Pessoa_Representante_Legal CPF_CNPJ_Representante_legal Data_Composicao_Capital_Social Data_Ultima_Alteracao Acionista_Controlador Participante_Acordo_Acionistas'.split(),
    'historico_emissor': COMMON + 'Data_Constituicao_Emissor Forma_Constituicao_Emissor Sigla_Pais_Constituicao_Emissor Pais_Constituicao_Emissor Prazo_Duracao_Emissor Data_Registro_Emissor Requisicao_Registro_Emissor'.split(),
    'grupo_economico_reestruturacao': COMMON + 'Data_Operacao Descricao_Operacao Evento_Societario'.split(),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    raw = json.dumps(value).encode()
    path.write_bytes(raw)
    return sha(raw)


def row(**values):
    return dict(CNPJ_Companhia='00.000.000/0001-00', Data_Referencia='2010-12-31',
                Versao='001', ID_Documento='0002', Nome_Companhia='Synthetic Company', **values)


def csv_bytes(kind, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=';', lineterminator='\r\n')
    writer.writerow(HEADERS[kind])
    writer.writerows([[r.get(f, '') for f in HEADERS[kind]] for r in rows])
    return stream.getvalue().encode('latin1')


class CorporateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        try:
            self.api = importlib.import_module('bank_quality.cvm_corporate_metadata')
        except ModuleNotFoundError:
            self.fail('Corporate metadata API is not implemented')

    def sources(self, members=None, manifest_delta=None, extra=None):
        if members is None:
            members = {'participacao_sociedade': csv_bytes('participacao_sociedade', [row(ID_Sociedade='0007', CNPJ='00.000.000/0002-00')])}
        resources = []
        for year in range(2010, 2025):
            name = str(year)
            url = f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{year}.zip'
            body = io.BytesIO()
            with zipfile.ZipFile(body, 'w') as z:
                for kind, raw in members.items():
                    z.writestr(f'fre_cia_aberta_{kind}_{year}.csv', raw)
                if extra:
                    z.writestr(extra, b'ignored')
            raw = body.getvalue()
            (self.root / (name + '.zip')).write_bytes(raw)
            response = dict(url=url, final_url=url, method='GET', http_status=200)
            response_pin = dump(self.root / (name + '-response.json'), response)
            manifest = dict(response, outcome='ok', source_complete=True, truncated=False,
                            body_path=name + '.zip', sha256=sha(raw), bytes=len(raw), content_length=len(raw),
                            retrieved_at_utc='2026-10-12T01:00:00+00:00',
                            response_metadata_path=name + '-response.json', response_metadata_sha256=response_pin)
            manifest.update(manifest_delta or {})
            pin = dump(self.root / (name + '.json'), manifest)
            resources.append(dict(kind='fre', year=name, url=url, manifest=name + '.json', manifest_sha256=pin))
        self.index = self.root / 'index.json'
        self.index_value = dict(contract='cvm-corporate-sources-v1', resources=resources)
        self.pin = dump(self.index, self.index_value)
        return self.root / 'out'

    def build(self, **kwargs):
        output = self.sources(**kwargs)
        result = self.api.build_corporate_metadata(self.index, self.pin, output)
        return output, result, self.api.verify_corporate_metadata(output, result['manifest_sha256'])

    def test_literal_projection_provenance_and_new_destination(self):
        output, result, manifest = self.build()
        with (output / 'participacao_sociedade.csv').open(encoding='utf8', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]['ID_Sociedade'], '0007')
        self.assertEqual(rows[0]['Versao'], '001')
        self.assertEqual(rows[0]['Codigo_CVM'], '')
        self.assertEqual(rows[0]['__physical_line_start'], '2')
        self.assertEqual(rows[0]['__source_retrieved_at_utc'], '2026-10-12T01:00:00+00:00')
        self.assertNotIn('Valor_Contabil', rows[0])
        self.assertEqual(manifest['counts']['participacao_sociedade.csv'], 15)
        with self.assertRaises(ValueError):
            self.api.build_corporate_metadata(self.index, self.pin, output)
        (output / 'extra.txt').write_text('extra')
        with self.assertRaises(ValueError):
            self.api.verify_corporate_metadata(output, result['manifest_sha256'])

    def test_pj_only_and_related_pf_not_exported(self):
        pj = row(ID_Acionista='01', Tipo_Pessoa_Acionista='PJ', Acionista='Company PJ',
                 CPF_CNPJ_Acionista='00.000.000/0002-00', Tipo_Pessoa_Acionista_Relacionado='PF',
                 Acionista_Relacionado='SECRET PF', CPF_CNPJ_Acionista_Relacionado='SECRET CPF',
                 Representante_Legal='SECRET REPRESENTATIVE', Quantidade_Total_Acoes_Circulacao='SECRET AMOUNT')
        pf = row(Tipo_Pessoa_Acionista='PF', Acionista='SECRET PERSON')
        output, _, _ = self.build(members={'posicao_acionaria': csv_bytes('posicao_acionaria', [pj, pf])})
        exported = '\n'.join(p.read_text(encoding='utf8') for p in output.iterdir())
        self.assertNotIn('SECRET', exported)
        quality = json.loads((output / 'quality.json').read_text())
        self.assertEqual(quality['members'][0]['excluded_pf'], 1)
        self.assertEqual(quality['members'][0]['admitted'], 1)

    def test_entire_malformed_multiline_segment_is_quarantined(self):
        header = csv_bytes('participacao_sociedade', [])
        bad = b'"unterminated\r\nabsorbed physical line\r\n'
        output, _, _ = self.build(members={'participacao_sociedade': header + bad})
        quality = json.loads((output / 'quality.json').read_text())
        item = quality['quarantine'][0]
        self.assertEqual((item['physical_line_start'], item['physical_line_end']), (2, 3))
        self.assertEqual(item['raw_segment_sha256'], sha(bad))
        self.assertEqual(item['reason'], 'invalid_csv')
        self.assertEqual(quality['members'][0]['diagnostic_segments'], 1)
        self.assertEqual(quality['members'][0]['admitted'], 0)
        self.assertNotIn('absorbed', json.dumps(quality))

    def test_bad_width_key_date_and_future_alert_are_distinct(self):
        raw = csv_bytes('historico_emissor', [row(Data_Registro_Emissor='2099-12-31'),
                          row(Data_Registro_Emissor='not-date')]) + b'a;b\r\n'
        output, _, _ = self.build(members={'historico_emissor': raw})
        q = json.loads((output / 'quality.json').read_text())
        self.assertEqual({x['reason'] for x in q['quarantine']}, {'invalid_date', 'width_mismatch'})
        self.assertEqual(q['date_alerts'][0]['value'], '2099-12-31')
        self.assertEqual(len(q['structurally_absent']), 45)

    def test_rejects_transport_and_index_mutations(self):
        for delta in ({'truncated': True}, {'source_complete': False}, {'http_status': 206},
                      {'final_url': 'https://evil.invalid'}, {'bytes': 0},
                      {'retrieved_at_utc': '2026-10-12T01:00:00'}):
            with self.subTest(delta=delta):
                output = self.sources(manifest_delta=delta)
                with self.assertRaises(ValueError):
                    self.api.build_corporate_metadata(self.index, self.pin, output)
        output = self.sources()
        with self.assertRaises(ValueError):
            self.api.build_corporate_metadata(self.index, '0' * 64, output)
        self.index_value['resources'].pop()
        pin = dump(self.index, self.index_value)
        with self.assertRaises(ValueError):
            self.api.build_corporate_metadata(self.index, pin, output)

    def test_rejects_body_response_schema_and_unsafe_zip(self):
        for target in ('2010.zip', '2010-response.json'):
            output = self.sources()
            with (self.root / target).open('ab') as f:
                f.write(b'changed')
            with self.assertRaises(ValueError):
                self.api.build_corporate_metadata(self.index, self.pin, output)
        output = self.sources(extra='../escape')
        with self.assertRaises(ValueError):
            self.api.build_corporate_metadata(self.index, self.pin, output)
        output = self.sources(members={'historico_emissor': b'unknown;schema\r\n'})
        with self.assertRaises(ValueError):
            self.api.build_corporate_metadata(self.index, self.pin, output)

    def test_valid_multiline_replay_and_output_tamper(self):
        members = {'participacao_sociedade': csv_bytes('participacao_sociedade', [
            row(ID_Sociedade='0001', Razao_Social='Synthetic\r\nCompany', Data_Valor_Contabil='2200-12-31')])}
        output, result, manifest = self.build(members=members)
        replay = self.root / 'replay'
        repeated = self.api.build_corporate_metadata(self.index, self.pin, replay)
        self.assertEqual(result['manifest_sha256'], repeated['manifest_sha256'])
        with (output / 'participacao_sociedade.csv').open(encoding='utf8', newline='') as f:
            record = next(csv.DictReader(f))
        self.assertEqual(record['Razao_Social'], 'Synthetic\r\nCompany')
        self.assertEqual(record['__physical_line_end'], '3')
        self.assertNotIn('Data_Valor_Contabil', record)
        q = json.loads((output / 'quality.json').read_text())
        self.assertEqual(q['date_alerts'][0]['value'], '2200-12-31')
        with (output / 'participacao_sociedade.csv').open('ab') as f:
            f.write(b'changed')
        with self.assertRaises(ValueError):
            self.api.verify_corporate_metadata(output, result['manifest_sha256'])

    def test_invalid_document_keys_and_related_pj_keys_quarantined(self):
        invalid = row(ID_Sociedade='')
        invalid['CNPJ_Companhia'] = 'impossible'
        pj = row(ID_Acionista='0001', Tipo_Pessoa_Acionista='PJ', CPF_CNPJ_Acionista='00.000.000/0002-00',
                 Tipo_Pessoa_Acionista_Relacionado='PJ', CPF_CNPJ_Acionista_Relacionado='impossible')
        output, _, _ = self.build(members={
            'participacao_sociedade': csv_bytes('participacao_sociedade', [invalid]),
            'posicao_acionaria': csv_bytes('posicao_acionaria', [pj])})
        q = json.loads((output / 'quality.json').read_text())
        self.assertEqual({i['reason'] for i in q['quarantine']}, {'invalid_document_key', 'invalid_related_pj_key'})

    def test_restructuring_free_text_never_exported(self):
        output, _, _ = self.build(members={'grupo_economico_reestruturacao': csv_bytes(
            'grupo_economico_reestruturacao', [row(Descricao_Operacao='SECRET FREE TEXT', Evento_Societario='Incorporacao')])})
        self.assertNotIn('SECRET', '\n'.join(p.read_text(encoding='utf8') for p in output.iterdir()))

    def test_verify_rejects_repinned_false_source_inventory(self):
        output, _, manifest = self.build()
        manifest['sources'][0]['url'] = 'https://evil.invalid'
        new_pin = dump(output / 'manifest.json', manifest)
        with self.assertRaises(ValueError):
            self.api.verify_corporate_metadata(output, new_pin)

    def test_nonnumeric_document_key_is_quarantined(self):
        invalid = row(ID_Sociedade='001')
        invalid['Versao'] = 'not-a-version'
        output, _, manifest = self.build(members={
            'participacao_sociedade': csv_bytes('participacao_sociedade', [invalid])})
        self.assertEqual(manifest['counts']['participacao_sociedade.csv'], 0)
        q = json.loads((output / 'quality.json').read_text())
        self.assertEqual(q['quarantine'][0]['reason'], 'invalid_document_key')

    def test_participation_personal_and_malformed_identifiers_are_quarantined(self):
        rows = [row(ID_Sociedade='1', CNPJ='12345678901', Razao_Social='SECRET PERSONAL NAME'),
                row(ID_Sociedade='2', CNPJ='123.456.789-01', Razao_Social='SECRET FORMATTED CPF'),
                row(ID_Sociedade='3', CNPJ='invalid identifier', Razao_Social='SECRET MALFORMED'),
                row(ID_Sociedade='4', CNPJ='', Pais_Sede='Estados Unidos', Razao_Social='Foreign Entity'),
                row(ID_Sociedade='5', CNPJ='', Pais_Sede='Brasil', Razao_Social='Missing Identifier')]
        output, _, manifest = self.build(members={
            'participacao_sociedade': csv_bytes('participacao_sociedade', rows)})
        self.assertEqual(manifest['counts']['participacao_sociedade.csv'], 30)
        public = '\n'.join(p.read_text(encoding='utf8') for p in output.iterdir())
        self.assertNotIn('SECRET', public)
        self.assertNotIn('12345678901', public)
        self.assertNotIn('123.456.789-01', public)
        quality = json.loads((output / 'quality.json').read_text())
        self.assertEqual({q['reason'] for q in quality['quarantine']}, {'invalid_society_identifier'})
        self.assertEqual({g['country_literal'] for g in quality['identifier_gaps']}, {'Brasil', 'Estados Unidos'})
        with (output / 'participacao_sociedade.csv').open(encoding='utf8', newline='') as f:
            admitted = list(csv.DictReader(f))
        self.assertTrue(all(r['CNPJ'] == '' for r in admitted))

    def test_shareholder_pj_label_cannot_export_cpf(self):
        pj = row(ID_Acionista='1', Tipo_Pessoa_Acionista='PJ', CPF_CNPJ_Acionista='12345678901',
                 Acionista='SECRET FALSE PJ')
        output, _, manifest = self.build(members={'posicao_acionaria': csv_bytes('posicao_acionaria', [pj])})
        self.assertEqual(manifest['counts']['posicao_acionaria.csv'], 0)
        self.assertNotIn('SECRET', '\n'.join(p.read_text(encoding='utf8') for p in output.iterdir()))

    def test_verify_rejects_repinned_invalid_physical_locators(self):
        output, _, manifest = self.build()
        target = output / 'participacao_sociedade.csv'
        original = target.read_bytes()
        for field, value in (
                ('__diagnostic_segment', 'garbage'), ('__diagnostic_segment', '0'),
                ('__physical_line_start', '-10'), ('__physical_line_end', '0'),
                ('__physical_line_start', '3'), ('__raw_segment_sha256', 'not-a-hash'),
                ('__source_retrieved_at_utc', '2026-10-12T01:00:00'),
                ('__source_manifest_sha256', '0' * 64)):
            with self.subTest(field=field, value=value):
                reader = csv.DictReader(io.StringIO(original.decode('utf8'), newline=''))
                rows = list(reader)
                rows[0][field] = value
                stream = io.StringIO(newline='')
                writer = csv.DictWriter(stream, reader.fieldnames, lineterminator='\n')
                writer.writeheader()
                writer.writerows(rows)
                raw = stream.getvalue().encode('utf8')
                target.write_bytes(raw)
                manifest['files'][target.name].update(sha256=sha(raw), bytes=len(raw))
                pin = dump(output / 'manifest.json', manifest)
                with self.assertRaises(ValueError):
                    self.api.verify_corporate_metadata(output, pin)

    def test_declared_pj_with_empty_identifier_is_preserved_with_role_gap(self):
        pj = row(ID_Acionista='0001', Tipo_Pessoa_Acionista='PJ', CPF_CNPJ_Acionista='',
                 Acionista='Declared PJ', Acionista_Controlador='S',
                 Tipo_Pessoa_Acionista_Relacionado='PF', Acionista_Relacionado='SECRET PF')
        output, _, manifest = self.build(members={'posicao_acionaria': csv_bytes('posicao_acionaria', [pj])})
        self.assertEqual(manifest['counts']['posicao_acionaria.csv'], 15)
        with (output / 'posicao_acionaria.csv').open(encoding='utf8', newline='') as f:
            admitted = next(csv.DictReader(f))
        self.assertEqual(admitted['CPF_CNPJ_Acionista'], '')
        self.assertEqual(admitted['ID_Acionista'], '0001')
        self.assertEqual(admitted['Acionista_Controlador'], 'S')
        self.assertEqual(admitted['Acionista_Relacionado'], '')
        q = json.loads((output / 'quality.json').read_text())
        self.assertEqual(q['identifier_gaps'][0]['role'], 'shareholder')
        self.assertEqual(q['identifier_gaps'][0]['field'], 'CPF_CNPJ_Acionista')
        self.assertEqual(q['identifier_gaps'][0]['reason'], 'empty_source_literal')
        self.assertNotIn('Declared PJ', json.dumps(q))
        self.assertFalse(q['relationship_acceptance'])

    def test_related_pj_empty_identifier_keeps_principal_and_literal_related_fields(self):
        pj = row(ID_Acionista='0001', Tipo_Pessoa_Acionista='PJ', CPF_CNPJ_Acionista='00.000.000/0002-00',
                 Tipo_Pessoa_Acionista_Relacionado='PJ', ID_Acionista_Relacionado='0002',
                 Acionista_Relacionado='Declared Related PJ', CPF_CNPJ_Acionista_Relacionado='')
        output, _, manifest = self.build(members={'posicao_acionaria': csv_bytes('posicao_acionaria', [pj])})
        self.assertEqual(manifest['counts']['posicao_acionaria.csv'], 15)
        with (output / 'posicao_acionaria.csv').open(encoding='utf8', newline='') as f:
            admitted = next(csv.DictReader(f))
        self.assertEqual(admitted['CPF_CNPJ_Acionista'], '00.000.000/0002-00')
        self.assertEqual(admitted['Acionista_Relacionado'], 'Declared Related PJ')
        self.assertEqual(admitted['ID_Acionista_Relacionado'], '0002')
        q = json.loads((output / 'quality.json').read_text())
        self.assertEqual(q['identifier_gaps'][0]['role'], 'related_shareholder')
        self.assertEqual(q['identifier_gaps'][0]['field'], 'CPF_CNPJ_Acionista_Relacionado')

    def test_verify_requires_exact_identifier_gap_contract(self):
        output, _, manifest = self.build(members={'participacao_sociedade': csv_bytes(
            'participacao_sociedade', [row(ID_Sociedade='1', CNPJ='', Pais_Sede='Estados Unidos')])})
        qpath = output / 'quality.json'
        original = qpath.read_bytes()
        for mutation in ('missing', 'role', 'locator', 'name'):
            with self.subTest(mutation=mutation):
                q = json.loads(original)
                if mutation == 'missing':
                    q['identifier_gaps'].pop()
                elif mutation == 'role':
                    q['identifier_gaps'][0]['role'] = 'wrong-role'
                elif mutation == 'locator':
                    q['identifier_gaps'][0]['physical_line_start'] = -1
                else:
                    q['identifier_gaps'][0]['name'] = 'SHOULD NOT BE IN GAP'
                raw = json.dumps(q).encode('utf8')
                qpath.write_bytes(raw)
                manifest['files']['quality.json'].update(sha256=sha(raw), bytes=len(raw))
                pin = dump(output / 'manifest.json', manifest)
                with self.assertRaises(ValueError):
                    self.api.verify_corporate_metadata(output, pin)


if __name__ == '__main__':
    unittest.main()

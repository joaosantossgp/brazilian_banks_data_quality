"""Offline CVM metadata admission boundaries; fixtures contain no captured company data."""
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch



HEADERS = {'cad': ['CNPJ_CIA',
         'DENOM_SOCIAL',
         'DENOM_COMERC',
         'DT_REG',
         'DT_CONST',
         'DT_CANCEL',
         'MOTIVO_CANCEL',
         'SIT',
         'DT_INI_SIT',
         'CD_CVM',
         'SETOR_ATIV',
         'TP_MERC',
         'CATEG_REG',
         'DT_INI_CATEG',
         'SIT_EMISSOR',
         'DT_INI_SIT_EMISSOR',
         'CONTROLE_ACIONARIO',
         'TP_ENDER',
         'LOGRADOURO',
         'COMPL',
         'BAIRRO',
         'MUN',
         'UF',
         'PAIS',
         'CEP',
         'DDD_TEL',
         'TEL',
         'DDD_FAX',
         'FAX',
         'EMAIL',
         'TP_RESP',
         'RESP',
         'DT_INI_RESP',
         'LOGRADOURO_RESP',
         'COMPL_RESP',
         'BAIRRO_RESP',
         'MUN_RESP',
         'UF_RESP',
         'PAIS_RESP',
         'CEP_RESP',
         'DDD_TEL_RESP',
         'TEL_RESP',
         'DDD_FAX_RESP',
         'FAX_RESP',
         'EMAIL_RESP',
         'CNPJ_AUDITOR',
         'AUDITOR'],
 'index': ['CNPJ_CIA',
           'DT_REFER',
           'VERSAO',
           'DENOM_CIA',
           'CD_CVM',
           'CATEG_DOC',
           'ID_DOC',
           'DT_RECEB',
           'LINK_DOC'],
 'geral': ['CNPJ_Companhia',
           'Data_Referencia',
           'Versao',
           'ID_Documento',
           'Nome_Empresarial',
           'Data_Nome_Empresarial',
           'Nome_Empresarial_Anterior',
           'Data_Constituicao',
           'Codigo_CVM',
           'Data_Registro_CVM',
           'Categoria_Registro_CVM',
           'Data_Categoria_Registro_CVM',
           'Situacao_Registro_CVM',
           'Data_Situacao_Registro_CVM',
           'Pais_Origem',
           'Pais_Custodia_Valores_Mobiliarios',
           'Setor_Atividade',
           'Descricao_Atividade',
           'Situacao_Emissor',
           'Data_Situacao_Emissor',
           'Especie_Controle_Acionario',
           'Data_Especie_Controle_Acionario',
           'Dia_Encerramento_Exercicio_Social',
           'Mes_Encerramento_Exercicio_Social',
           'Data_Alteracao_Exercicio_Social',
           'Pagina_Web'],
 'valmob': ['CNPJ_Companhia',
            'Data_Referencia',
            'Versao',
            'ID_Documento',
            'Nome_Empresarial',
            'Valor_Mobiliario',
            'Sigla_Classe_Acao_Preferencial',
            'Classe_Acao_Preferencial',
            'Codigo_Negociacao',
            'Composicao_BDR_Unit',
            'Mercado',
            'Sigla_Entidade_Administradora',
            'Entidade_Administradora',
            'Data_Inicio_Negociacao',
            'Data_Fim_Negociacao',
            'Segmento',
            'Data_Inicio_Listagem',
            'Data_Fim_Listagem']}

def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded_csv(header, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=';', lineterminator='\n')
    writer.writerow(header)
    writer.writerows([[row.get(key, '') for key in header] for row in rows])
    return stream.getvalue().encode('latin-1')


class CVMMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        spec = importlib.util.find_spec('bank_quality.cvm_metadata')
        self.assertIsNotNone(spec, 'CVM metadata admission API missing')
        from bank_quality import cvm_metadata
        self.api = cvm_metadata
        self.rows = {
            'cad': [dict(CNPJ_CIA='00.000.000/0001-91', CD_CVM='1023', DENOM_SOCIAL='Banco sintético', SIT='ATIVO', TP_MERC='BOLSA', DT_REG='1977-07-20', RESP='private contact')],
            'index': [dict(CNPJ_CIA='00.000.000/0001-91', DT_REFER='2010-01-01', VERSAO='1', ID_DOC='9', CD_CVM='001023', CATEG_DOC='FCA', DT_RECEB='2010-05-01')],
            'geral': [dict(CNPJ_Companhia='00.000.000/0001-91', Data_Referencia='2010-01-01', Versao='1', ID_Documento='9', Codigo_CVM='001023', Descricao_Atividade='Texto; citado\nsegunda linha')],
            'valmob': [dict(CNPJ_Companhia='00.000.000/0001-91', Data_Referencia='2010-01-01', Versao='1', ID_Documento='9', Codigo_Negociacao='', Valor_Mobiliario='Ações')],
        }

    def fixture(self, *, rows=None, headers=None, zip_names=None, c1=False):
        rows = rows or self.rows
        headers = headers or HEADERS
        resources = []
        for kind in ('cad', 'fca'):
            if kind == 'cad':
                body = encoded_csv(headers['cad'], rows['cad'])
                if c1:
                    body += b'\x80'
            else:
                stream = io.BytesIO()
                with zipfile.ZipFile(stream, 'w') as archive:
                    for key, suffix in [('index', ''), ('geral', '_geral'), ('valmob', '_valor_mobiliario')]:
                        name = f'fca_cia_aberta{suffix}_2010.csv'
                        archive.writestr(name, encoded_csv(headers[key], rows[key]))
                    for name in zip_names or []:
                        archive.writestr(name, b'unsafe')
                body = stream.getvalue()
            url = ('https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv' if kind == 'cad' else 'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_2010.zip')
            response = dict(url=url, final_url=url, method='GET', http_status=200)
            response_raw = json.dumps(response).encode()
            (self.source / f'{kind}.response.json').write_bytes(response_raw)
            manifest = dict(url=url, final_url=url, method='GET', http_status=200, outcome='ok', source_complete=True, truncated=False, bytes=len(body), sha256=digest(body), body_path=f'{kind}.bin', response_metadata_path=f'{kind}.response.json', response_metadata_sha256=digest(response_raw), retrieved_at_utc='2026-10-12T17:00:00+00:00')
            (self.source / f'{kind}.bin').write_bytes(body)
            raw = json.dumps(manifest).encode()
            (self.source / f'{kind}.json').write_bytes(raw)
            resources.append(dict(kind=kind, year=None if kind == 'cad' else '2010', url=url, manifest=f'{kind}.json', manifest_sha256=digest(raw)))
        index = dict(contract='cvm-identity-sources-v1', resources=resources)
        return self.save_index(index)

    def save_index(self, index):
        path = self.source / 'source-index.json'
        raw = json.dumps(index).encode()
        path.write_bytes(raw)
        return path, digest(raw)

    def repin_manifest(self, pair, change):
        index=json.loads(pair[0].read_bytes())
        path=self.source/index['resources'][0]['manifest']
        manifest=json.loads(path.read_bytes())
        manifest.update(change)
        raw=json.dumps(manifest).encode()
        path.write_bytes(raw)
        index['resources'][0]['manifest_sha256']=digest(raw)
        return self.save_index(index)

    def build(self, pair, name='output'):
        return self.api.build_cvm_metadata(pair[0], pair[1], self.root / name)

    def read(self, name):
        with (self.root / 'output' / name).open(encoding='utf-8', newline='') as stream:
            return list(csv.DictReader(stream))

    def test_literal_projection_lineage_and_multiline(self):
        result = self.build(self.fixture())
        records = self.read('geral_fca.csv')
        self.assertEqual(records[0]['Codigo_CVM'], '001023')
        self.assertEqual(records[0]['Descricao_Atividade'], 'Texto; citado\nsegunda linha')
        self.assertEqual(records[0]['__source_row'], '1')
        self.assertEqual(records[0]['__source_year'], '2010')
        self.assertEqual(self.read('valores_mobiliarios_fca.csv')[0]['Codigo_Negociacao'], '')
        self.assertNotIn('RESP', self.read('cadastro_atual.csv')[0])
        manifest = self.api.verify_cvm_metadata(self.root / 'output', result['manifest_sha256'])
        self.assertEqual(manifest['counts']['cadastro_atual.csv'], 1)

    def test_replay_is_deterministic_and_duplicates_survive(self):
        self.rows['valmob'] *= 2
        pair = self.fixture()
        first = self.build(pair)
        second = self.build(pair, 'replay')
        self.assertEqual(first['manifest_sha256'], second['manifest_sha256'])
        records = self.read('valores_mobiliarios_fca.csv')
        self.assertEqual([x['__source_row'] for x in records], ['1', '2'])
        quality = json.loads((self.root/'output'/'quality.json').read_bytes())
        self.assertEqual(quality['tables']['valores_mobiliarios_fca.csv']['duplicate_literal_rows'], 1)

    def test_wrong_index_pin_and_source_tamper_fail(self):
        pair = self.fixture()
        with self.assertRaises(ValueError):
            self.build((pair[0], '0'*64))
        (self.source/'cad.bin').write_bytes(b'tampered')
        with self.assertRaises(ValueError):
            self.build(pair)

    def test_manifest_and_response_tamper_fail(self):
        for filename in ['cad.json', 'cad.response.json']:
            with self.subTest(filename=filename):
                pair=self.fixture()
                (self.source/filename).write_bytes(b'{}')
                with self.assertRaises(ValueError):
                    self.build(pair)

    def test_containment_and_symlink_fail(self):
        pair=self.fixture();index=json.loads(pair[0].read_bytes())
        index['resources'][0]['manifest']='../cad.json'
        with self.assertRaises(ValueError):
            self.build(self.save_index(index))
        pair=self.fixture()
        original=self.source/'cad.bin';outside=self.root/'outside.bin';outside.write_bytes(original.read_bytes());original.unlink()
        try:
            original.symlink_to(outside)
        except OSError:
            return
        with self.assertRaises(ValueError):
            self.build(pair)

    def test_existing_destination_never_overwritten(self):
        pair=self.fixture();target=self.root/'output';target.mkdir();(target/'keep').write_text('preserve')
        with self.assertRaises((ValueError, FileExistsError)):
            self.build(pair)
        self.assertEqual((target/'keep').read_text(), 'preserve')

    def test_closed_headers_c1_and_invalid_dates_fail(self):
        headers={k:list(v) for k,v in HEADERS.items()};headers['geral'][0]='unexpected'
        with self.assertRaises(ValueError):
            self.build(self.fixture(headers=headers))
        with self.assertRaises(ValueError):
            self.build(self.fixture(c1=True))
        self.rows['cad'][0]['DT_REG']='2010-02-30'
        with self.assertRaises(ValueError):
            self.build(self.fixture())

    def test_zip_traversal_and_duplicate_members_fail(self):
        for names in [['../escape.csv'], ['C:/escape.csv'], ['fca_cia_aberta_2010.csv']]:
            with self.subTest(names=names):
                with self.assertRaises(ValueError):
                    self.build(self.fixture(zip_names=names))

    def test_cnpj_conflict_is_quarantined_not_joined_by_id(self):
        self.rows['geral'][0]['CNPJ_Companhia']='00.000.000/0002-72'
        self.build(self.fixture())
        quality=json.loads((self.root/'output'/'quality.json').read_bytes())
        statuses=[x['status'] for x in quality['document_links']]
        self.assertIn('cnpj_conflict',statuses)
        self.assertEqual(self.read('geral_fca.csv')[0]['CNPJ_Companhia'],'00.000.000/0002-72')
        self.assertTrue(any(x['quarantined'] for x in quality['document_links']))

    def test_ambiguous_and_missing_index_preserved(self):
        self.rows['index'] *= 2
        self.rows['valmob'][0]['ID_Documento']='999'
        self.build(self.fixture())
        quality=json.loads((self.root/'output'/'quality.json').read_bytes())
        statuses={x['status'] for x in quality['document_links']}
        self.assertEqual(statuses, {'ambiguous','missing_index'})

    def test_output_and_manifest_tamper_fail_verify(self):
        result=self.build(self.fixture())
        with self.assertRaises(ValueError):
            self.api.verify_cvm_metadata(self.root/'output','0'*64)
        (self.root/'output'/'geral_fca.csv').write_bytes(b'bad')
        with self.assertRaises(ValueError):
            self.api.verify_cvm_metadata(self.root/'output',result['manifest_sha256'])

    def test_duplicate_resources_and_invalid_url_fail(self):
        pair=self.fixture();index=json.loads(pair[0].read_bytes());index['resources'].append(index['resources'][1])
        with self.assertRaises(ValueError):
            self.build(self.save_index(index))
        pair=self.fixture();index=json.loads(pair[0].read_bytes());index['resources'][0]['url']='https://example.com/cad.csv'
        with self.assertRaises(ValueError):
            self.build(self.save_index(index))

    def test_incomplete_transport_and_invalid_recovery_time_fail(self):
        for number, change in enumerate([{'source_complete':False}, {'truncated':True},
                       {'http_status':201}, {'final_url':'https://example.com/'},
                       {'content_length':1}, {'retrieved_at_utc':'yesterday'}]):
            with self.subTest(change=change):
                pair=self.repin_manifest(self.fixture(),change)
                with self.assertRaises(ValueError):
                    self.build(pair, 'transport-' + str(number))

    def test_zip_symlink_and_expansion_budget_fail(self):
        for member_flag in [False, True]:
            with self.subTest(symlink=member_flag):
                pair=self.fixture()
                if member_flag:
                    bodypath=self.source/'fca.bin'
                    stream=io.BytesIO()
                    with zipfile.ZipFile(io.BytesIO(bodypath.read_bytes())) as original:
                        with zipfile.ZipFile(stream,'w') as archive:
                            for item in original.infolist():
                                archive.writestr(item,original.read(item))
                            info=zipfile.ZipInfo('link.csv')
                            info.create_system=3
                            info.external_attr=0o120777 << 16
                            archive.writestr(info,b'target')
                    body=stream.getvalue();bodypath.write_bytes(body)
                    index=json.loads(pair[0].read_bytes());mp=self.source/'fca.json';m=json.loads(mp.read_bytes());m.update(bytes=len(body),sha256=digest(body));raw=json.dumps(m).encode();mp.write_bytes(raw);index['resources'][1]['manifest_sha256']=digest(raw);pair=self.save_index(index)
                    with self.assertRaises(ValueError):
                        self.build(pair)
                else:
                    with patch.object(self.api,'MAX_MEMBER_BYTES',1):
                        with self.assertRaises(ValueError):
                            self.build(pair)

    def test_reversed_declared_interval_is_reported_without_correction(self):
        self.rows['valmob'][0].update(Data_Inicio_Listagem='2010-02-01',Data_Fim_Listagem='2010-01-01')
        self.build(self.fixture())
        quality=json.loads((self.root/'output'/'quality.json').read_bytes())
        self.assertIn('date_conflicts', quality)
        self.assertEqual(len(quality['date_conflicts']),1)
        self.assertEqual(self.read('valores_mobiliarios_fca.csv')[0]['Data_Fim_Listagem'],'2010-01-01')

    def test_per_zip_and_aggregate_expansion_budgets_are_distinct(self):
        pair=self.fixture()
        with self.subTest(budget='per_zip'):
            with patch.object(self.api,'MAX_ZIP_EXPANDED_BYTES',1,create=True):
                with self.assertRaises(ValueError):
                    self.build(pair,'zip-budget')
        # Two individually permitted archives must also fit the shared budget.
        index=json.loads(pair[0].read_bytes())
        original=self.source/'fca.bin';stream=io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(original.read_bytes())) as archive:
            expanded=sum(item.file_size for item in archive.infolist())
            with zipfile.ZipFile(stream,'w') as second:
                for item in archive.infolist():
                    second.writestr(item.filename.replace('2010','2011'),archive.read(item).replace(b'2010-01-01',b'2011-01-01'))
        body=stream.getvalue();(self.source/'fca2011.bin').write_bytes(body)
        manifest=json.loads((self.source/'fca.json').read_bytes());url=manifest['url'].replace('2010','2011')
        response=json.dumps(dict(url=url,final_url=url,method='GET',http_status=200)).encode();(self.source/'fca2011.response.json').write_bytes(response)
        manifest.update(url=url,final_url=url,body_path='fca2011.bin',bytes=len(body),sha256=digest(body),response_metadata_path='fca2011.response.json',response_metadata_sha256=digest(response))
        raw=json.dumps(manifest).encode();(self.source/'fca2011.json').write_bytes(raw)
        index['resources'].append(dict(kind='fca',year='2011',url=url,manifest='fca2011.json',manifest_sha256=digest(raw)))
        pair=self.save_index(index)
        with self.subTest(budget='aggregate'):
            # CAD plus either ZIP fits; CAD plus both ZIPs does not.
            budget=(self.source/'cad.bin').stat().st_size+expanded+1
            with patch.object(self.api,'MAX_EXPANDED_BYTES',budget):
                with self.assertRaises(ValueError):
                    self.build(pair,'aggregate-budget')

    def test_incomplete_document_keys_never_match_including_duplicates(self):
        keys=[('ID_DOC','ID_Documento'),('DT_REFER','Data_Referencia'),('VERSAO','Versao')]
        for number,(index_field,structured_field) in enumerate(keys):
            for duplicate in (False,True):
                with self.subTest(field=structured_field,duplicate=duplicate):
                    rows={kind:[dict(row) for row in source] for kind,source in self.rows.items()}
                    rows['index'][0][index_field]=''
                    rows['geral'][0][structured_field]=''
                    rows['valmob'][0][structured_field]=''
                    if duplicate:
                        rows['index']*=2
                        rows['geral']*=2
                        rows['valmob']*=2
                    output='incomplete-'+str(number)+'-'+str(duplicate)
                    result=self.build(self.fixture(rows=rows),output)
                    quality=json.loads((self.root/output/'quality.json').read_bytes())
                    links=quality['document_links']
                    self.assertTrue(links)
                    self.assertEqual({link['status'] for link in links},{'incomplete_key'})
                    self.assertTrue(all(link['quarantined'] for link in links))
                    self.assertTrue(all(not link['matching_index_rows'] for link in links))
                    self.assertTrue(all(link['missing_key_components'] for link in links))
                    self.assertEqual(result['counts']['geral_fca.csv'],2 if duplicate else 1)
                    with (self.root/output/'geral_fca.csv').open(encoding='utf-8',newline='') as stream:
                        admitted=list(csv.DictReader(stream))
                    self.assertEqual(admitted[0][structured_field],'')


if __name__ == '__main__':
    unittest.main()

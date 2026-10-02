import unittest
from bank_quality.portal import parse_portal, accept_export


def state():
    return {'period':201012,'type_id':1006,'type_name':'Instituições Individuais',
        'report':{'n':'Resumo'},'expected_areas':1,'loaded_areas':1,
        'columns':[{'ifd':1,'fid':8},{'ifd':2,'fid':9},{'ifd':3,'fid':13},{'ifd':4,'fid':2}],
        'infos':[{'id':1,'n':'Instituição'},{'id':2,'n':'Código'},{'id':3,'n':'Ativo Total'},{'id':4,'n':'Número de Agências'}],
        'rows':[['BANK','00001234',1250000,'NI']],
        'cadastro':[{'c0':'1234','c1':'201012','c2':'BANK'}],
        'header_lines':[{'cells':['Instituição;','Código;','Ativo Total;','Número de Agências;']}]}


class PortalTests(unittest.TestCase):
    def test_identifier_mismatch_is_rejected(self):
        data=state()
        header=''.join(data['header_lines'][0]['cells'])
        with self.assertRaises(ValueError): parse_portal(data,(header+'\nBANK;BOGUS;1.250;0\n').encode(),201012)

    def test_underlying_asset_manifest_is_verified(self):
        from pathlib import Path
        index={'period':201012,'complete':True,'manifests':[{'body_path':'nonexistent','sha256':'bad'}]}
        with self.assertRaises(FileNotFoundError): accept_export(index,Path('.'),201012)

    def test_official_table_tokens_survive_formatted_csv(self):
        data=state()
        csv='\ufeffInstituição;Código;Ativo Total;Número de Agências;\r\nBANK;00001234;1.250;0\r\n'.encode('utf-8')
        result=parse_portal(data,csv,201012)
        self.assertEqual(result['values'][0]['Saldo'],1250000)
        self.assertEqual(result['values'][0]['_unit'],'BRL_unformatted_portal_table')
        self.assertEqual(result['values'][1]['Saldo'],'NI')
        self.assertEqual(result['values'][1]['_csv_token'],'0')
        self.assertEqual(result['values'][1]['CodInst'],'00001234')
        self.assertEqual(result['csv_table_disagreements'],1)

    def test_wrong_scope_or_incomplete_shards_rejected(self):
        for key,value in [('period',202412),('type_id',1005),('type_name','Conglomerados'),('loaded_areas',0)]:
            with self.subTest(key=key),self.assertRaises(ValueError): parse_portal({**state(),key:value},b'x',201012)

    def test_export_header_and_row_count_must_match_table(self):
        for body in ('<html>error</html>','Wrong;Header\nBANK;00001234;1.250;0\n','Instituição;Código;Ativo Total;Número de Agências;\n'):
            with self.subTest(body=body),self.assertRaises(ValueError): parse_portal(state(),body.encode(),201012)

    def test_stale_previous_report_columns_are_rejected(self):
        data=state()
        data['expected_columns']=[1,2,999,4]
        csv='\ufeffInstituição;Código;Ativo Total;Número de Agências;\r\nBANK;00001234;1.250;0\r\n'.encode()
        with self.assertRaises(ValueError): parse_portal(data,csv,201012)


if __name__=='__main__':unittest.main()

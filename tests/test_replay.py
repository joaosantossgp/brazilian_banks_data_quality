import json
import tempfile
import unittest
from pathlib import Path
from bank_quality.archive import preserve_generated
from bank_quality.replay import replay

class ReplayTests(unittest.TestCase):
    def test_odata_replay_uses_hashed_bodies_instead_of_mutable_cached_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);raw=root/'raw';quarters={}
            for period in (201012,202412):
                row={'AnoMes':str(period),'TipoInstituicao':3,'CodInst':'001','Conta':'a','NomeColuna':'Ativo','Saldo':'NI','NomeRelatorio':'Resumo'}
                manifest=preserve_generated(json.dumps({'value':[row]}).encode(),raw,str(period),'https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/fixture','test_fixture')
                manifest.update({'http_status':200,'outcome':'ok'})
                quarters[str(period)]={'values_complete':True,'values':[{**row,'Saldo':0}],'sources':{'values_odata':{'complete':True,'manifests':[manifest]}}}
            path=root/'collection.json';path.write_text(json.dumps({'periods':[201012,202412],'raw_directory':str(raw),'quarters':quarters}))
            result=replay(path,root/'derived')
            self.assertEqual(result['quarters']['201012']['value_states'],{'NI':1})
            (raw/manifest['body_path']).write_bytes(b'tampered')
            with self.assertRaises(ValueError):replay(path,root/'again')

    def test_scope_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'collection.json';path.write_text(json.dumps({'periods':[202606],'quarters':{}}))
            with self.assertRaises(ValueError):replay(path,Path(directory)/'output')

    def test_complete_flag_cannot_turn_failure_body_into_empty_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);raw=root/'raw'
            manifest=preserve_generated(b'error',raw,'failure','https://olinda.bcb.gov.br/','fixture')
            manifest.update({'http_status':500,'outcome':'http_error'})
            quarter={'values_complete':True,'values':[],'sources':{'values_odata':{'complete':True,'manifests':[manifest]}}}
            path=root/'collection.json';path.write_text(json.dumps({'periods':[201012,202412],'raw_directory':str(raw),'quarters':{'201012':quarter,'202412':quarter}}))
            with self.assertRaises(ValueError): replay(path,root/'out')

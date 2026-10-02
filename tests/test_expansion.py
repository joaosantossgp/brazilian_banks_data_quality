import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from bank_quality import ifdata
from bank_quality.portal import parse_portal, export_portal
from bank_quality.portal import validate_202312_schema
from bank_quality.replay import replay
from bank_quality.archive import preserve_generated


class ExpansionTests(unittest.TestCase):
    def test_single_202312_and_explicit_portal_without_claiming_odata_attempt(self):
        with tempfile.TemporaryDirectory() as root:
            called=[]
            def forbidden(*args,**kwargs):self.fail('Network OData must not be called in explicit portal mode')
            def portal(period,raw):
                called.append(period)
                return {'values_complete':True,'source_mode':'official_portal_csv_fallback','diagnostics':[]}
            result=ifdata.collect(Path(root),(202312,),transport=forbidden,portal_transport=portal,portal_only=True)
            self.assertEqual(called,[202312])
            self.assertEqual(result['periods'],[202312])
            self.assertEqual(result['quarters']['202312']['odata_attempt_state'],'not_attempted_this_quarter')

    def test_scope_is_validated_before_network(self):
        for periods in [(),(202312,202312),(202303,),(202503,)]:
            with self.subTest(periods=periods),self.assertRaises(ValueError):
                ifdata.collect(Path('unused'),periods,transport=lambda *a,**k:self.fail('network'))

    def test_202312_cannot_enter_unbounded_odata_path(self):
        with self.assertRaisesRegex(ValueError,'portal-only'):
            ifdata.collect(Path('unused'),(202312,),transport=lambda *a,**k:self.fail('network'))
        with self.assertRaises(ValueError):
            ifdata.collect(Path('unused'),(201012,202312,202412),portal_only=True)

    def test_schema_changes_to_definitions_and_notes_are_rejected(self):
        profile=json.loads(Path(__file__).parents[1].joinpath('bank_quality/schema-202312.json').read_text(encoding='utf-8'))
        state={k:profile[k] for k in ('columns','report','infos')}
        validate_202312_schema(state)
        for part,field in [('report','rp'),('report','cp'),('infos','d'),('infos','n')]:
            mutated=json.loads(json.dumps(state))
            (mutated[part] if part=='report' else mutated[part][0])[field]='changed'
            with self.subTest(part=part,field=field),self.assertRaises(ValueError):validate_202312_schema(mutated)

    def test_unverified_202312_schema_rejected(self):
        from test_portal import state
        data=state();data['period']=202312
        body='Instituição;Código;Ativo Total;Número de Agências;\nBANK;00001234;1.250;0\n'.encode()
        with self.assertRaisesRegex(ValueError,'202312.*schema'):
            parse_portal(data,body,202312)

    def test_three_period_replay_uses_each_raw_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);quarters={}
            for period in [201012,202312,202412]:
                raw=root/str(period)
                row={'AnoMes':str(period),'TipoInstituicao':3,'CodInst':'0','Conta':'a','NomeColuna':'Ativo','Saldo':0,'NomeRelatorio':'Resumo'}
                manifest=preserve_generated(json.dumps({'value':[row]}).encode(),raw,'test',
                    'https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/test','fixture')
                manifest.update(http_status=200,outcome='ok')
                quarters[str(period)]={'raw_directory':str(raw),'values_complete':True,
                    'sources':{'values_odata':{'complete':True,'manifests':[manifest]}}}
            path=root/'collection.json';path.write_text(json.dumps({'periods':[201012,202312,202412],
                'raw_directory':str(root),'quarters':quarters}))
            self.assertEqual(set(replay(path,root/'output')['quarters']),set(quarters))
            (raw/manifest['body_path']).write_bytes(b'changed')
            with self.assertRaises(ValueError):replay(path,root/'changed')

    def test_disk_reserve_prevents_browser_start(self):
        with tempfile.TemporaryDirectory() as root, patch('bank_quality.portal.shutil.disk_usage') as disk,patch('bank_quality.portal.subprocess.run') as run:
            disk.return_value=type('Space',(),{'free':100})()
            with self.assertRaisesRegex(RuntimeError,'reserve'):export_portal(202312,Path(root))
            run.assert_not_called()

    def test_failed_export_stops_after_two_attempts(self):
        with tempfile.TemporaryDirectory() as root, patch('bank_quality.portal.subprocess.run') as run:
            run.return_value=type('Result',(),{'returncode':1,'stderr':'failed','stdout':''})()
            with self.assertRaises(RuntimeError):export_portal(202312,Path(root))
            self.assertEqual(run.call_count,2)

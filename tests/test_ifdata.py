import json
import tempfile
import unittest
from pathlib import Path
from bank_quality.ifdata import parse_odata, validate_values, collect, safe_next_link


class IfDataTests(unittest.TestCase):
    def test_validated_fallback_can_run_when_report_discovery_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            called=[]
            def unavailable(url,raw,label,context=None,timeout=30):
                return {'outcome':'http_error','http_status':500}
            def fallback(period,raw):
                called.append(period)
                return {'values':[],'cadastro':[],'values_complete':True,'cadastro_complete':False,'source_mode':'official_portal_csv_fallback','diagnostics':['verified fixture']}
            result=collect(Path(directory),transport=unavailable,portal_transport=fallback)
            self.assertEqual(called,[201012,202412])
            self.assertTrue(all(q['values_complete'] for q in result['quarters'].values()))
            self.assertIn('cadastro_odata',result['quarters']['201012']['sources'])

    def test_odata_rows_and_continuation_are_exposed(self):
        rows, link = parse_odata(b'{"value":[{"Saldo":0}],"@odata.nextLink":"?skip=1"}')
        self.assertEqual(rows, [{'Saldo': 0}])
        self.assertEqual(link, '?skip=1')

    def test_error_html_and_wrong_json_shape_rejected(self):
        for body in (b'<html>error</html>', b'{"error":"bad"}', b'{"value":{}}', b'{"value":[1]}'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                parse_odata(body)

    def test_mismatched_period_type_or_report_rejected(self):
        row = {'AnoMes':'201012','TipoInstituicao':3,'CodInst':'00123456','Conta':'a','NomeColuna':'Ativo','Saldo':'NI','NomeRelatorio':'Resumo'}
        validate_values([row], 201012)
        for field, value in [('AnoMes','202412'),('TipoInstituicao',1),('NomeRelatorio','Ativo')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_values([{**row, field:value}],201012)

    def test_next_page_must_remain_on_official_service(self):
        base='https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/IfDataValores'
        self.assertTrue(safe_next_link('?%24skip=1000',base).startswith(base))
        for link in ('https://example.org/data','https://olinda.bcb.gov.br/other'):
            with self.assertRaises(ValueError): safe_next_link(link,base)

    def test_periods_outside_pilot_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError): collect(Path(directory),periods=(201003,))

    def test_failed_cadastro_does_not_discard_complete_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            count=[0]
            def fixture_fetch(url, raw, label, context=None, timeout=30):
                count[0]+=1
                if 'ListaDeRelatorio' in url:
                    data={'value':[{'NomeRelatorio':'Resumo','NumeroRelatorio':'1'}]}; status=200
                elif 'IfDataCadastro' in url:
                    data={'error':'fixture upstream failure'}; status=500
                else:
                    period=context['period']
                    data={'value':[{'AnoMes':str(period),'TipoInstituicao':3,'CodInst':'00123456','Conta':'1','NomeColuna':'Ativo','Saldo':0,'NomeRelatorio':'Resumo'}]}; status=200
                from bank_quality.archive import hashlib
                body=json.dumps(data).encode(); raw.mkdir(parents=True,exist_ok=True)
                path=f'fixture_{count[0]}.bin'; (raw/path).write_bytes(body)
                return {'url':url,'http_status':status,'outcome':'ok' if status==200 else 'http_error','body_path':path,'sha256':hashlib.sha256(body).hexdigest(),'context':context or {},'diagnostics':[]}
            result=collect(root,transport=fixture_fetch,allow_fallback=False)
            self.assertEqual(set(result['quarters']),{'201012','202412'})
            for quarter in result['quarters'].values():
                self.assertTrue(quarter['values_complete'])
                self.assertFalse(quarter['cadastro_complete'])
                self.assertEqual(quarter['values'][0]['CodInst'],'00123456')


if __name__=='__main__': unittest.main()

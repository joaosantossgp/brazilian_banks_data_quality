"""Exact source parsing and calendar aggregation, without live HTTP in tests."""
import gzip,json,tempfile,unittest
from pathlib import Path
from fractions import Fraction


class MacroContextTests(unittest.TestCase):
    def sample(self,token='123.4500',period='202404',variable='585'):
        header=dict(NC='Nível Territorial (Código)',D1C='Brasil (Código)',D2C='Variável (Código)',D3C='Trimestre (Código)',D4C='Setor (Código)',MC='Unidade (Código)',MN='Unidade',V='Valor')
        row=dict(NC='1',D1C='1',D2C=variable,D3C=period,D4C='90707',MC='1550',MN='Milhões de Reais',V=token)
        return json.dumps([header,row],ensure_ascii=False).encode()

    def series(self):
        return dict(key='gdp_current_brl_million',table=1846,variable='585',frequency='quarterly',classification_path='/c11255/90707',unit='BRL_million',native_units={'585':{'code':'1550','name':'Milhões de Reais'}})

    def test_exact_token_civil_quarter_and_gzip(self):
        from bank_quality.macro_context import parse_sidra
        rows=parse_sidra(gzip.compress(self.sample()),self.series())
        self.assertEqual(rows[0]['value_token'],'123.4500')
        self.assertEqual(rows[0]['value_fraction'],['2469','20'])
        self.assertEqual(rows[0]['period'],'202412')
        self.assertEqual(rows[0]['native_period'],'202404')

    def test_invalid_document_identity_duplicates_and_sentinel(self):
        from bank_quality.macro_context import parse_sidra
        for body in (b'<html>error</html>',self.sample(variable='999'),self.sample(period='202413')):
            with self.subTest(body=body),self.assertRaises(ValueError):parse_sidra(body,self.series())
        doc=json.loads(self.sample());doc.append(doc[1])
        with self.assertRaisesRegex(ValueError,'Duplicate'):parse_sidra(json.dumps(doc).encode(),self.series())
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            parse_sidra(self.sample(),dict(self.series(),variable='585,999'))
        row=parse_sidra(self.sample(token='...'),self.series())[0]
        self.assertIsNone(row['value_fraction']);self.assertEqual(row['status'],'source_sentinel')
        self.assertEqual(row['value_token'],'...')

    def test_wrong_unit_and_truncated_gzip_are_semantic_errors(self):
        from bank_quality.macro_context import parse_sidra
        doc=json.loads(self.sample());doc[1]['MC']='2';doc[1]['MN']='Percentual'
        with self.assertRaisesRegex(ValueError,'unit'):parse_sidra(json.dumps(doc).encode(),self.series())
        with self.assertRaises(ValueError):parse_sidra(b'\x1f\x8bbroken',self.series())

    def test_quarter_mean_needs_three_months_and_gdp_ttm_needs_four_quarters(self):
        from bank_quality.macro_context import quarterly_panel
        source=[dict(series='industrial_production',variable='12606',category='129314',period=p,native_period=p,
                     frequency='monthly',value_token=str(i),value_fraction=[str(i),'1'],status='ok',unit='index',source_ref='captured') for i,p in enumerate(('202401','202402','202403'),1)]
        panel=quarterly_panel(source)
        self.assertEqual(panel[0]['value_fraction'],['2','1'])
        self.assertEqual(panel[0]['method'],'mean_three_months')
        self.assertIsNone(quarterly_panel(source[:2])[0]['value_fraction'])
        gdp=[dict(source[0],series='gdp_current_brl_million',variable='585',frequency='quarterly',period=p,native_period=p,value_fraction=[str(i),'1']) for i,p in enumerate(('202303','202306','202309','202312'),1)]
        ttm=[r for r in quarterly_panel(gdp) if r['method']=='sum_four_quarters']
        self.assertEqual(next(r for r in ttm if r['period']=='202312')['value_fraction'],['10','1'])
        self.assertIsNone(next(r for r in ttm if r['period']=='202309')['value_fraction'])

    def test_capture_replay_authenticates_body_and_rejects_error_page(self):
        from unittest.mock import patch,MagicMock
        from bank_quality.macro_context import collect_context,replay_context,digest
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);profile=root/'profile.json';series=dict(self.series(),provider='IBGE_SIDRA',url_template='https://apisidra.ibge.gov.br/values/t/1846/p/{periods}')
            profile.write_text(json.dumps(dict(contract='macro-context-series-v1',series=[series],limits=[])),encoding='utf8')
            response=MagicMock();response.__enter__.return_value=response;response.status=200;response.headers={};response.read.return_value=self.sample()
            with patch('urllib.request.urlopen',return_value=response):
                collect_context(root/'raw',root/'out',profile=profile)
            replay_context(root/'raw',digest(root/'raw'/'manifest.json'),root/'replay',profile=profile)
            self.assertEqual((root/'out'/'quarterly.parquet').read_bytes(),(root/'replay'/'quarterly.parquet').read_bytes())
            (root/'raw'/'gdp_current_brl_million.body').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'hash'):
                replay_context(root/'raw',digest(root/'raw'/'manifest.json'),root/'bad',profile=profile)
            self.assertFalse((root/'bad'/'manifest.json').exists())
            response.read.return_value=b'<html>invalid request</html>'
            with patch('urllib.request.urlopen',return_value=response),self.assertRaises(ValueError):
                collect_context(root/'rawbad',root/'outbad',profile=profile)
            self.assertTrue((root/'rawbad'/'gdp_current_brl_million.receipt.json').exists())
            self.assertFalse((root/'outbad'/'manifest.json').exists())
            response.read.return_value=b'\x1f\x8bbroken'
            with patch('urllib.request.urlopen',return_value=response),self.assertRaises(ValueError):
                collect_context(root/'rawgzip',root/'outgzip',profile=profile)
            self.assertTrue((root/'rawgzip'/'gdp_current_brl_million.receipt.json').exists())
            self.assertFalse((root/'outgzip'/'manifest.json').exists())

    def test_effective_interest_compounds_and_real_rate_matches_window(self):
        from bank_quality.macro_context import interest_panel
        observations=[dict(id='m'+str(m),series='selic_effective_monthly',variable='BM12_TJOVER12',category='total',
                           period=f'2024{m:02d}',value_fraction=['1','1'],status='ok') for m in range(1,13)]
        inflation=[dict(id='ipca3',series='ipca',variable='2263',category='total',period='202412',value_fraction=['2','1'],status='ok'),
                   dict(id='ipca12',series='ipca',variable='2265',category='total',period='202412',value_fraction=['5','1'],status='ok')]
        result=interest_panel(observations,inflation)
        q=next(r for r in result if r['series']=='selic_effective_monthly' and r['period']=='202412' and r['method']=='compound_three_months')
        self.assertEqual(Fraction(*map(int,q['value_fraction'])),(Fraction(101,100)**3-1)*100)
        real=next(r for r in result if r['series']=='real_policy_rate_expost' and r['period']=='202412' and r['method']=='fisher_three_months')
        self.assertEqual(Fraction(*map(int,real['value_fraction'])),(Fraction(101,100)**3/Fraction(102,100)-1)*100)
        annual=next(r for r in result if r['series']=='real_policy_rate_expost' and r['period']=='202412' and r['method']=='fisher_twelve_months')
        self.assertEqual(Fraction(*map(int,annual['value_fraction'])),(Fraction(101,100)**12/Fraction(105,100)-1)*100)

    def test_ipea_interest_token_unit_identity_and_duplicate_guards(self):
        from bank_quality.macro_context import parse_ipea_monthly
        meta=dict(SERCODIGO='BM12_TJOVER12',PERNOME='Mensal',UNINOME='(% a.m.)',PAICODIGO='BRA',FNTNOME='Banco Central do Brasil')
        body=b'{"value":[{"SERCODIGO":"BM12_TJOVER12","VALDATA":"2024-12-01T00:00:00-03:00","VALVALOR":0.9300,"NIVNOME":"","TERCODIGO":""}]}'
        row=parse_ipea_monthly(body,meta)[0]
        self.assertEqual(row['value_token'],'0.9300');self.assertEqual(row['value_fraction'],['93','100'])
        with self.assertRaises(ValueError):parse_ipea_monthly(body,dict(meta,UNINOME='(% a.a.)'))
        doc=json.loads(body);doc['value']*=2
        with self.assertRaisesRegex(ValueError,'Duplicate'):parse_ipea_monthly(json.dumps(doc).encode(),meta)


if __name__=='__main__':unittest.main()

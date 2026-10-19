"""Causal checks for the pure temporal layer; no captured data or I/O."""
import importlib.util
import unittest
import json
from pathlib import Path
import tempfile
import hashlib
import csv
from copy import deepcopy
from datetime import date
from decimal import Inexact, InvalidOperation, ROUND_DOWN, localcontext


def observation(period, token, **changes):
    row = dict(period=period, token=token,
               unit_key=('financial', '2', '001'), definition_id='profit-v1',
               scale='BRL', window_rule='native-semester-analysis-v2',
               binding={'Conta': 'profit', 'Grupo': None, 'Descricao': 'literal'},
               sources=[{'file': 'captured.json', 'row': period, 'sha256': 'a' * 64}])
    row.update(changes)
    return row


def stock(period, token, **changes):
    return observation(period, token, definition_id='assets-v1',
                       window_rule='stock', **changes)


class AssafSensitivityTests(unittest.TestCase):
    def evaluate(self, metric, *, changes=None, horizon=None):
        from bank_quality import ifdata_analysis as api
        point=metric in ('L1','PL_DEP')
        rows={n:[observation('202403',v,definition_id=n,window_rule='stock')] for n,v in
              {'cash':'5','sight_deposits':'20','PL':'-10','deposits':'40'}.items()}
        rows.update({n:[observation(p,v,definition_id=n) for p,v in
                    zip(('202403','202406','202409','202412'),tokens)] for n,tokens in
                    {'LL':('3','6','3','6'),'RIF':('12','24','12','24')}.items()})
        rows['AT']=[observation(p,'120',definition_id='AT',window_rule='stock') for p in
                    ('202312','202403','202406','202409','202412')]
        if changes:changes(rows)
        return api.evaluate_metric(metric,dict(period='202403' if point or horizon!='ttm' else '202412',
                                               components=rows,financial_statement=True),
                                   horizon or ('point' if point else 'quarter'))

    def test_exact_sensitivities_use_native_quarters_and_stock_means(self):
        from bank_quality import ifdata_analysis as api
        from fractions import Fraction
        for metric,value in {'L1':Fraction(1,4),'PL_DEP':Fraction(-1,4),
                             'R3':Fraction(1,4),'RIF_AT':Fraction(1,10)}.items():
            with self.subTest(metric=metric):
                r=self.evaluate(metric);self.assertEqual(r['status'],'ok')
                self.assertEqual(api._rational(r['value_fraction']),value)
        self.assertIn('negative_equity',self.evaluate('PL_DEP')['flags'])
        self.assertEqual(api._rational(self.evaluate('R3',horizon='ttm')['value_fraction']),Fraction(1,4))
        self.assertEqual(api._rational(self.evaluate('RIF_AT',horizon='ttm')['value_fraction']),Fraction(2,5))

    def test_zero_null_negative_and_unknown_history_remain_distinct(self):
        def change(name,value):return lambda rows:rows[name][0].update(token=value)
        self.assertEqual(self.evaluate('L1',changes=change('sight_deposits','0'))['status'],'zero_denominator')
        self.assertEqual(self.evaluate('L1',changes=change('cash',None))['status'],'native_null')
        self.assertEqual(self.evaluate('R3',changes=change('RIF','0'))['status'],'zero_denominator')
        r=self.evaluate('R3',changes=change('RIF','-12'))
        self.assertEqual(r['value'],'-0.25');self.assertIn('negative_denominator',r['flags'])
        def no_opening(rows):rows['AT']=rows['AT'][1:]
        self.assertEqual(self.evaluate('RIF_AT',changes=no_opening)['status'],'missing_opening')
        def new_definition(rows):rows['LL'][2]['definition_id']='other-definition'
        self.assertEqual(self.evaluate('R3',changes=new_definition,horizon='ttm')['status'],'incompatible_definition')
        def wrong_window(rows):rows['RIF'][0]['window_rule']='stock'
        self.assertEqual(self.evaluate('R3',changes=wrong_window)['status'],'unverified_window')
        self.assertEqual(self.evaluate('R3',horizon='point')['status'],'invalid_horizon')


class ComplementMetricTests(unittest.TestCase):
    def setUp(self):
        from bank_quality import ifdata_analysis
        self.api=ifdata_analysis

    def point(self,metric,changes=None):
        tokens=dict(cash='5',interfinancial='10',AT='100',credit='60',deposits='40',
                    repos='10',issuances='20',loans_transfers='30',funding='100')
        tokens.update(changes or {})
        rows={name:[observation('202412',token,definition_id=name,window_rule='stock')] for name,token in tokens.items()}
        return self.api.evaluate_metric(metric,dict(period='202412',components=rows,financial_statement=True),'point')

    def test_point_complements_and_four_nonoverlapping_funding_shares(self):
        expected={'LA':'0.15','LC':'0.6','LF-DEP':'0.4','LF-OC':'0.1','LF-EM':'0.2','LF-REP':'0.3'}
        for metric,value in expected.items():
            with self.subTest(metric=metric):
                r=self.point(metric);self.assertEqual((r['status'],r['value'],r['applicability']),('ok',value,'applicable'))
        self.assertIn('not_certified_available_liquidity',self.point('LA')['limits'])
        self.assertIn('not_total_balance_sheet_funding',self.point('LF-DEP')['limits'])

    def test_funding_reconciliation_is_not_forced_and_zero_null_negative_differ(self):
        self.assertEqual(self.point('LF-DEP',{'funding':'101'})['status'],'funding_identity_mismatch')
        zero={k:'0' for k in ('funding','deposits','repos','issuances','loans_transfers')}
        self.assertEqual(self.point('LF-DEP',zero)['status'],'zero_denominator')
        self.assertEqual(self.point('LF-DEP',{'repos':None})['status'],'native_null')
        r=self.point('LA',{'AT':'-100'});self.assertEqual(r['value'],'-0.15');self.assertIn('negative_denominator',r['flags'])
        r=self.point('LC',{'credit':'0'});self.assertEqual(r['value'],'0')

    def flow(self,metric,change=None,horizon='quarter'):
        values={'RBIF':('50','110'),'provision_flow':('-2','-6'),'services':('5','15'),
                'fees':('2','6'),'personnel':('-3','-9'),'administration':('-1','-3'),'credit_income':('10','30')}
        rows={name:[observation(p,t,definition_id=name) for p,t in zip(('202409','202412'),tokens)] for name,tokens in values.items()}
        rows.update({name:[observation(p,t,definition_id=name,window_rule='stock') for p,t in zip(('202409','202412'),tokens)]
                     for name,tokens in {'AT':('100','120'),'credit':('50','60')}.items()})
        if change:change(rows)
        return self.api.evaluate_metric(metric,dict(period='202412',components=rows,financial_statement=True),horizon)

    def test_flow_complements_use_genuine_quarters_and_mean_stocks(self):
        from fractions import Fraction
        expected={'RS':Fraction(7,39),'E3':Fraction(4,55),'R4':Fraction(6,11),'R5':Fraction(4,11)}
        for metric,value in expected.items():
            with self.subTest(metric=metric):
                r=self.flow(metric);self.assertEqual(r['status'],'ok');self.assertEqual(self.api._rational(r['value_fraction']),value)
        self.assertIn('not_NIM_or_contractual_spread',self.flow('R4')['limits'])

    def test_new_formulas_preserve_guards_signs_and_missing_history(self):
        def missing_opening(rows):rows['credit']=rows['credit'][1:]
        self.assertEqual(self.flow('R5',missing_opening)['status'],'missing_opening')
        def reversal(rows):rows['personnel'][1]['token']='3';rows['administration'][1]['token']='1'
        r=self.flow('E3',reversal);self.assertEqual(r['status'],'ok');self.assertIn('signed_cost_reversal',r['flags'])
        def other_unit(rows):rows['credit_income'][-1]['unit_key']=('individual','3','001')
        self.assertEqual(self.flow('R5',other_unit)['status'],'incompatible_unit')
        def all_negative_income(rows):rows['RBIF'][-1]['token']='-100'
        r=self.flow('RS',all_negative_income);self.assertEqual(r['status'],'ok');self.assertIn('negative_denominator',r['flags'])
        def negative_numerator_and_denominator(rows):
            for name,tokens in {'RBIF':('0','-20'),'services':('0','-10'),'fees':('0','0'),'provision_flow':('0','0')}.items():
                for row,token in zip(rows[name],tokens):row['token']=token
        r=self.flow('RS',negative_numerator_and_denominator)
        self.assertEqual(self.api._rational(r['value_fraction']),self.api.Fraction(1,3))
        self.assertIn('negative_denominator',r['flags']);self.assertNotIn('non_convex_income_share',r['flags'])
        self.assertEqual(self.flow('RS',horizon='point')['status'],'invalid_horizon')
        self.assertEqual(self.flow('R5',horizon='ttm')['status'],'missing_component')


class MetricTests(unittest.TestCase):
    def setUp(self):
        from bank_quality import ifdata_analysis
        self.api = ifdata_analysis

    def metric(self, metric, tokens, horizon='point'):
        self.assertTrue(hasattr(self.api, 'evaluate_metric'), 'Metric composition missing')
        rows = {name: [observation('202412', token, definition_id=name, window_rule='stock')]
                for name, token in tokens.items()}
        return self.api.evaluate_metric(metric, dict(period='202412', components=rows,
            financial_statement=True, prudential_bridge=True), horizon)

    def test_manual_point_formulas_and_different_definitions(self):
        for metric, values, expected in [
            ('Q1', {'provision_stock':'-7','credit':'100'}, '0.07'),
            ('C1', {'PL':'20','AT':'100'}, '0.2'),
            ('C3', {'PR':'30','RWA':'100'}, '0.3'),
            ('C4', {'CP':'15','RWA':'100'}, '0.15'),
            ('L2', {'cash':'10','interfinancial':'15','sight_deposits':'50'}, '0.5'),
            ('L3', {'credit':'0','deposits':'50'}, '0')]:
            with self.subTest(metric=metric):
                result=self.metric(metric, values)
                self.assertEqual(result['value'], expected)
                self.assertEqual(result['applicability'], 'applicable')
                self.assertIsNotNone(result['numerator_fraction'])
                self.assertIsNotNone(result['denominator_fraction'])

    def test_zero_negative_denominator_and_unknown_are_separate(self):
        result=self.metric('Q1', {'provision_stock':'-7','credit':'0'})
        self.assertEqual((result['status'],result['applicability']), ('zero_denominator','unknown'))
        result=self.metric('Q1', {'provision_stock':'-7','credit':'-100'})
        self.assertEqual(result['value'], '-0.07')
        self.assertIn('negative_denominator',result['flags'])
        self.assertEqual(result['applicability'],'unknown')

    def flow_inputs(self):
        return {name: [observation('202409', a, definition_id=name),
                       observation('202412', b, definition_id=name)]
                for name,a,b in [('LL','10','40'), ('provision_flow','-2','3'),
                  ('RBIF','50','100'), ('services','10','30'), ('fees','5','15'),
                  ('personnel','-10','-30'), ('administration','-5','0')]}

    def test_quarter_cost_reversals_and_selected_income(self):
        self.assertTrue(hasattr(self.api,'evaluate_metric'), 'Metric composition missing')
        c=self.flow_inputs(); c['credit']=[stock('202409','100'),stock('202412','300')]
        c['AT']=[stock('202409','100'),stock('202412','300')]
        c['PL']=[stock('202409','10'),stock('202412','30')]
        inputs=dict(period='202412',components=c,financial_statement=True)
        for metric,wanted in [('R1','0.15'),('R2','1.5'),('Q2','-0.025'),('E2-B','0.2')]:
            result=self.api.evaluate_metric(metric,inputs,'quarter')
            self.assertEqual(result['value'],wanted, result)
        result=self.api.evaluate_metric('E2-B',inputs,'quarter')
        self.assertEqual(result['economic_representativeness'],'not_certified')
        self.assertEqual(result['denominator_fraction'],{'numerator':'75','denominator':'1'})
        c['AT']=c['AT'][1:]
        self.assertEqual(self.api.evaluate_metric('R1',inputs,'quarter')['status'],'missing_opening')

    def test_composition_rejects_perimeter_scale_and_wrong_horizon(self):
        self.assertTrue(hasattr(self.api,'evaluate_metric'), 'Metric composition missing')
        rows={'PL':[stock('202412','20')], 'AT':[stock('202412','100',unit_key=('financial','2','other'))]}
        inp=dict(period='202412',components=rows,financial_statement=True)
        self.assertEqual(self.api.evaluate_metric('C1',inp,'point')['status'],'incompatible_unit')
        rows['AT']=[stock('202412','100',scale='USD')]
        self.assertEqual(self.api.evaluate_metric('C1',inp,'point')['status'],'invalid_scale')
        self.assertEqual(self.api.evaluate_metric('C1',inp,'quarter')['status'],'invalid_horizon')

    def test_statement_applicability_needs_observed_native_context_not_only_cadastro(self):
        rows={'PL':[stock('202412',None,status='binding_missing',sources=[])], 'AT':[stock('202412','100')]}
        result=self.api.evaluate_metric('C1',dict(period='202412',financial_statement=True,components=rows),'point')
        self.assertEqual(result['applicability'],'unknown')

    def test_prudential_applicability_needs_observed_unambiguous_capital5(self):
        for metric,amount in [('C3','PR'),('C4','CP')]:
            for status in ['binding_missing','ambiguous_occurrence']:
                rows={amount:[stock('202412',None,status=status,sources=[])],
                      'RWA':[stock('202412',None,status=status,sources=[])]}
                result=self.api.evaluate_metric(metric,dict(period='202412',prudential_bridge=True,components=rows),'point')
                self.assertEqual(result['applicability'],'unknown',result)
            # Observed recognized context with native null is still the
            # prudential accounting question; only calculation is unavailable.
            rows={amount:[stock('202412',None)],'RWA':[stock('202412','100')]}
            result=self.api.evaluate_metric(metric,dict(period='202412',prudential_bridge=True,components=rows),'point')
            self.assertEqual((result['applicability'],result['status']),('applicable','native_null'))

    def test_profile_exact_dates_and_typed_null_binding_resolution(self):
        self.assertTrue(hasattr(self.api,'load_profile'), 'Finite profile missing')
        profile=self.api.load_profile()
        self.assertEqual(len(profile['contexts']),27)
        self.assertEqual(set(profile['metrics']),set(self.api.METRICS))
        self.assertIn('population_not_certified_exclusive_to_credit',profile['metrics']['Q2']['limits'])
        rwa=[x for x in profile['contexts'] if x['component']=='RWA']
        self.assertFalse(set(rwa[0]['periods']) & set(rwa[1]['periods']))
        at=next(x for x in profile['contexts'] if x['component']=='AT')
        row=dict(at['literal_context'],AnoMes='202412',CodInst='001',Saldo='100')
        result=self.api.resolve_component(profile,'AT','financial','001','202412',[row])
        self.assertEqual(result['token'],'100')
        row['Grupo']=''
        self.assertEqual(self.api.resolve_component(profile,'AT','financial','001','202412',[row])['status'],'binding_missing')
        row['Grupo']=None; row['AnoMes']='200912'
        self.assertEqual(self.api.resolve_component(profile,'AT','financial','001','200912',[row])['status'],'binding_unverified')

    def test_dependency_closure_includes_all_ttm_stock_nodes(self):
        self.assertTrue(hasattr(self.api,'dependency_periods'), 'Dependency closure missing')
        self.assertEqual(self.api.dependency_periods(['202412']),['202312','202403','202406','202409','202412'])
        with self.assertRaises(ValueError): self.api.dependency_periods(['202412','202412'])

    def test_ttm_uses_exact_sum_over_all_mean_stock_boundaries(self):
        raw=[observation('2024'+p,t) for p,t in [('03','10'),('06','25'),('09','7'),('12','18')]]
        points=[stock(p,t) for p,t in [('202312','100'),('202403','200'),('202406','200'),('202409','200'),('202412','200')]]
        inputs=dict(period='202412',financial_statement=True,components={'LL':raw,'AT':points})
        result=self.api.evaluate_metric('R1',inputs,'ttm')
        self.assertEqual(result['numerator_fraction'],{'numerator':'43','denominator':'1'})
        # 2024: first91 days mean150, remaining275 days mean200.
        self.assertEqual(result['denominator_fraction'],{'numerator':'34325','denominator':'183'})
        self.assertEqual(result['value_fraction'],{'numerator':'7869','denominator':'34325'})
        self.assertTrue(result['annual_summary'])
        del points[2]
        self.assertEqual(self.api.evaluate_metric('R1',inputs,'ttm')['status'],'missing_stock_point')

    def test_ttm_ll_break_never_bridges_definitions(self):
        flow=[observation(p,'10',definition_id='old' if p<'201903' else 'new') for p in ['201806','201809','201812','201903']]
        points=[stock(p,'100') for p in ['201803','201806','201809','201812','201903']]
        result=self.api.evaluate_metric('R1',dict(period='201903',financial_statement=True,components={'LL':flow,'AT':points}),'ttm')
        # Q2 requires March2018; supplying it makes the actual break visible.
        flow.insert(0,observation('201803','5',definition_id='old'))
        result=self.api.evaluate_metric('R1',dict(period='201903',financial_statement=True,components={'LL':flow,'AT':points}),'ttm')
        self.assertEqual(result['status'],'incompatible_definition')

    def test_literal_occurrences_need_all_native_fields_page_and_distinct_positions(self):
        profile=self.api.load_profile();at=next(c for c in profile['contexts'] if c['component']=='AT')
        row=dict(at['literal_context'],CodInst='F',AnoMes='202412',Saldo='100',source_file='page',source_sha256='a'*64,
                 source_url='https://example.invalid',source_collected_utc='2026-10-14T00:00:00Z',source_context='ctx',source_row='1')
        row.pop('dataset');second=dict(row,source_row='2')
        result=self.api.resolve_component(profile,'AT','financial','F','202412',[row,second])
        self.assertEqual(result['token'],'100');self.assertEqual(len(result['sources']),2)
        for changes in [dict(source_file='other'),dict(source_row='1'),dict(source_context='other')]:
            result=self.api.resolve_component(profile,'AT','financial','F','202412',[row,dict(second,**changes)])
            self.assertEqual(result['status'],'ambiguous_occurrence')

    def test_q2_scope_limits_and_percentage_display_are_explicit(self):
        c=self.flow_inputs();c['credit']=[stock('202409','100'),stock('202412','300')]
        result=self.api.evaluate_metric('Q2',dict(period='202412',components=c),'quarter')
        self.assertIn('population_not_certified_exclusive_to_credit',result['limits'])
        self.assertEqual(result['percentage_display'],'-2.5')
        self.assertEqual(result['ratio_unit'],'fraction')

    def test_opening_exception_is_finite_stock_context_code_and_source(self):
        profile=self.api.load_profile();self.assertIsInstance(profile['opening_release'],dict)
        exception=profile['opening_release'];entry=next(e for e in exception['finite_binding_rows'] if e['component']=='AT')
        context=next(c for c in profile['contexts'] if c['context_sha256']==entry['context_sha256'])
        row={k:v for k,v in context['literal_context'].items() if k!='dataset'}
        row.update(entry['source'],CodInst=entry['code'],AnoMes='200912',Saldo='123')
        result=self.api.resolve_component(profile,'AT','financial',entry['code'],'200912',[row])
        self.assertEqual(result['token'],'123')
        self.assertEqual(result['definition_id'],context['compatibility'])
        self.assertTrue(result['binding']['opening_exception'])
        self.assertEqual(self.api.resolve_component(profile,'LL','financial',entry['code'],'200912',[row])['status'],'binding_unverified')
        self.assertEqual(self.api.resolve_component(profile,'AT','financial','NOTWHITELISTED','200912',[dict(row,CodInst='NOTWHITELISTED')])['status'],'binding_unverified')
        self.assertEqual(self.api.resolve_component(profile,'AT','financial',entry['code'],'200912',[dict(row,source_row='999999')])['status'],'opening_source_mismatch')

    def test_opening_change_flag_and_both_dated_cadastro_rows_survive(self):
        profile=self.api.load_profile();self.assertIsInstance(profile['opening_release'],dict)
        entry=next(e for e in profile['opening_release']['finite_binding_rows'] if e['component']=='AT' and e['code']=='C0030159')
        c=next(c for c in profile['contexts'] if c['context_sha256']==entry['context_sha256'])
        row={k:v for k,v in c['literal_context'].items() if k!='dataset'}
        row.update(entry['source'],CodInst=entry['code'],AnoMes='200912',Saldo='100')
        result=self.api.resolve_component(profile,'AT','financial',entry['code'],'200912',[row])
        self.assertIn('opening_cadastro_classification_change',result['flags'])


class PackageTests(unittest.TestCase):
    def setUp(self):
        from bank_quality import ifdata_analysis
        self.api=ifdata_analysis
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def digest(self,path): return hashlib.sha256(path.read_bytes()).hexdigest()

    def native_package(self,name,rows,fields,contract):
        import duckdb
        root=self.root/name;root.mkdir()
        path=root/'part.parquet'
        with duckdb.connect() as conn:
            conn.execute('create table native ('+','.join('"'+f+'" varchar' for f in fields)+')')
            conn.executemany('insert into native values ('+','.join('?' for _ in fields)+')',[[r.get(f) for f in fields] for r in rows])
            conn.execute('copy native to ? (format parquet)',[str(path)])
        manifest=dict(contract=contract,rows=len(rows),files=[dict(file=path.name,rows=len(rows),sha256=self.digest(path))])
        (root/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        return dict(root=str(root),expected_manifest_sha256=self.digest(root/'manifest.json'))

    def fixtures(self):
        from bank_quality.ifdata_odata import COLUMNS,CONTRACT
        from bank_quality.ifdata_cadastro import FIELDS,ORIGIN,CONTRACT as CAD_CONTRACT
        from bank_quality.ifdata_variable_catalog import build_catalog
        profile=self.api.load_profile()
        rows=[];capital=[]
        for period in ['202312','202403','202406','202409','202412']:
            for c in profile['contexts']:
                if period not in c['periods']:continue
                native={k:v for k,v in c['literal_context'].items() if k!='dataset'}
                native.update(AnoMes=period,CodInst='P' if c['literal_context']['dataset']=='capital' else 'F',Saldo='100',
                  source_file='page.json',source_sha256='a'*64,source_row=str(len(rows)+len(capital)+1),
                  source_url='https://example.invalid/page',source_collected_utc='2026-10-14T00:00:00Z',source_context='literal')
                (capital if c['literal_context']['dataset']=='capital' else rows).append(native)
        f=self.native_package('financial',rows,COLUMNS,CONTRACT)
        p=self.native_package('capital',capital,COLUMNS,CONTRACT)
        cadastro=[]
        for period in ['202312','202403','202406','202409','202412']:
            for code in ['F','F2','O','P']:
                c=dict.fromkeys(FIELDS+ORIGIN)
                c.update(CodInst=code,Data=period,CodConglomeradoPrudencial='P',Tcb='TARGET' if code=='F' else 'OPERATOR',SegmentoTb=None if code=='F' else 'operator_segment',Td='C')
                cadastro.append(c)
        cad=self.native_package('cadastro',cadastro,FIELDS+ORIGIN,CAD_CONTRACT)
        cat=self.root/'catalogue';build_catalog({'financial':f['root'],'capital':p['root']},cat)
        sample=self.root/'sample';sample.mkdir()
        mappings=[dict(company_cnpj14='1',company_name_2024='One',period='202412',native_target_code='F',operator_base8='O',native_cadastro={'CodConglomeradoPrudencial':'P'}),
                  dict(company_cnpj14='2',company_name_2024='Two',period='202412',native_target_code='F2',operator_base8='O',native_cadastro={'CodConglomeradoPrudencial':'P'}),
                  dict(company_cnpj14='3',company_name_2024='Missing Company',period='202412',native_target_code=None,operator_base8=None,native_cadastro=None)]
        files={}
        for name,data in [('company-quarter-map.json',mappings),('annual-verification.json',[]),('complementary-annual-verification.json',{'rows':[]})]:
            (sample/name).write_text(json.dumps(data),encoding='utf-8');files[name]=self.digest(sample/name)
        (sample/'manifest.json').write_text(json.dumps(dict(schema=1,issue=125,files=files)),encoding='utf-8')
        return dict(periods=['202412'],profile_expected_sha256=self.digest(self.api.PROFILE_PATH),
                    inputs=dict(financial=f,capital=p,cadastro=cad,
                      catalogue=dict(root=str(cat),expected_manifest_sha256=self.digest(cat/'manifest.json')),
                      sample=dict(root=str(sample),expected_manifest_sha256=self.digest(sample/'manifest.json'))))

    def test_real_readers_build_preserves_missing_company_target_metadata_and_prudential_dedup(self):
        self.assertTrue(hasattr(self.api,'build_analysis'),'Authenticated build missing')
        config=self.fixtures();out=self.root/'analysis'
        manifest=self.api.build_analysis(config,out)
        self.assertEqual(manifest['stage'],'coverage-and-aggregation')
        self.assertEqual(manifest['dependency_periods'],['202312','202403','202406','202409','202412'])
        results=json.loads((out/'results.json').read_text(encoding='utf-8'))
        self.assertEqual(len([r for r in results if r['metric']=='C3']),1)
        maps=json.loads((out/'company_map.json').read_text(encoding='utf-8'))
        self.assertEqual(len(maps),3)
        missing=next(r for r in maps if r['company']=='3')
        self.assertEqual(missing['status'],'missing_unit')
        one=next(r for r in maps if r['company']=='1')
        self.assertIsNone(one['financial_target_cadastro']['SegmentoTb'])
        self.assertEqual(one['operator_cadastro']['SegmentoTb'],'operator_segment')
        q1=next(r for r in results if r['metric']=='Q1' and r['code']=='F')
        self.assertEqual(q1['diagnostics']['credit_identity']['residual_fraction'],{'numerator':'100','denominator':'1'})
        c3=next(r for r in results if r['metric']=='C3')
        self.assertEqual(c3['diagnostics']['published_index']['token'],'100')
        self.assertEqual(c3['diagnostics']['published_index']['scale'],'native_index_unverified')
        self.assertEqual(self.api.verify_analysis(out,self.digest(out/'manifest.json'))['tables']['company_map'],3)
        queried=self.api.query_analysis(out,self.digest(out/'manifest.json'),"select count(*) as n from results where metric='C3'")
        self.assertEqual(queried,[{'n':1}])
        for sql in ["delete from results", "select * from read_csv('https://example.invalid/x')",'select 1; select 2']:
            with self.assertRaises(Exception):self.api.query_analysis(out,self.digest(out/'manifest.json'),sql)
        with self.assertRaises(FileExistsError):self.api.build_analysis(config,out)
        (out/'extra.txt').write_text('unaccepted')
        with self.assertRaises(ValueError):self.api.verify_analysis(out,self.digest(out/'manifest.json'))

    def test_external_pins_duplicate_inventory_traversal_and_partial_outputs_fail_closed(self):
        self.assertTrue(hasattr(self.api,'build_analysis'),'Authenticated build missing')
        config=self.fixtures();config['inputs']['financial']['expected_manifest_sha256']='0'*64
        with self.assertRaises(ValueError):self.api.build_analysis(config,self.root/'badpin')
        f=Path(config['inputs']['financial']['root']);m=json.loads((f/'manifest.json').read_text())
        for change in ['duplicate','traversal','missing']:
            mm=deepcopy(m)
            if change=='duplicate':mm['files'].append(mm['files'][0])
            else:mm['files'][0]['file']='../outside.parquet' if change=='traversal' else 'missing.parquet'
            (f/'manifest.json').write_text(json.dumps(mm))
            config['inputs']['financial']['expected_manifest_sha256']=self.digest(f/'manifest.json')
            with self.assertRaises((ValueError,FileNotFoundError)):self.api.build_analysis(config,self.root/change)
            self.assertFalse((self.root/change/'manifest.json').exists())

    def test_missing_external_profile_pin_cannot_borrow_local_hash(self):
        config=self.fixtures();config['profile_expected_sha256']=None
        with self.assertRaises(ValueError):self.api.build_analysis(config,self.root/'badprofile')

    def test_opening_manifest_pin_outside_review_is_rejected(self):
        config=self.fixtures()
        config['inputs']['opening']=dict(root=str(self.root/'not-reviewed'),expected_manifest_sha256='a'*64)
        with self.assertRaisesRegex(ValueError,'Opening200912 reviewed manifest mismatch'):
            self.api.build_analysis(config,self.root/'badopening')

    def test_opening_cadastro_requires_independently_reviewed_manifest(self):
        config=self.fixtures()
        config['inputs']['opening']=dict(root=str(self.root/'reviewed-opening'),
            expected_manifest_sha256='a98b5381c9b32d0f11676d1d744e10d90176f226d2135b586ed026aa73777f7b')
        # The synthetic cadastro exists and is internally authenticated, but
        # was never part of the independent finite opening perimeter review.
        try:
            with self.assertRaisesRegex(ValueError,'Opening200912 cadastro reviewed manifest mismatch'):
                self.api.build_analysis(config,self.root/'cadastro-outside-opening-review')
        except FileNotFoundError:
            self.fail('Unreviewed cadastro reached opening I/O instead of refusing the perimeter proof')

    def test_part_count_mismatch_cannot_hide_behind_correct_total(self):
        config=self.fixtures();root=Path(config['inputs']['financial']['root'])
        manifest=json.loads((root/'manifest.json').read_text());manifest['files'][0]['rows']=0
        (root/'manifest.json').write_text(json.dumps(manifest))
        config['inputs']['financial']['expected_manifest_sha256']=self.digest(root/'manifest.json')
        with self.assertRaises(ValueError):self.api.build_analysis(config,self.root/'badpartcount')

    def test_verify_rejects_tampered_missing_and_duplicate_output_inventory(self):
        config=self.fixtures();out=self.root/'analysis';self.api.build_analysis(config,out)
        path=out/'manifest.json';raw=path.read_bytes();manifest=json.loads(raw)
        (out/'results.json').write_text('[]')
        with self.assertRaises(ValueError):self.api.verify_analysis(out,self.digest(path))
        for change in ['duplicate','missing','traversal']:
            m=deepcopy(manifest)
            if change=='duplicate':m['files'].append(m['files'][0])
            elif change=='missing':m['files'].pop()
            else:m['files'][0]['file']='../outside'
            path.write_text(json.dumps(m))
            with self.assertRaises((ValueError,FileNotFoundError)):self.api.verify_analysis(out,self.digest(path))


class TemporalTests(unittest.TestCase):
    def setUp(self):
        # Missing module is the expected first RED, expressed as an assertion.
        assert importlib.util.find_spec('bank_quality.ifdata_analysis') is not None, (
            'The pure temporal analysis module has not been implemented')
        from bank_quality import ifdata_analysis
        self.api = ifdata_analysis

    def fraction(self, result, numerator, denominator='1'):
        self.assertEqual(result['status'], 'ok', result)
        self.assertEqual(result['value_fraction'],
                         {'numerator': str(numerator), 'denominator': str(denominator)})

    def unavailable(self, result, status):
        self.assertEqual(result['status'], status, result)
        self.assertIsNone(result['value_fraction'])
        self.assertIsNone(result['value'])

    def year(self, year='2011'):
        raw = [observation(year + p, t) for p, t in
               [('03', '10'), ('06', '25'), ('09', '7'), ('12', '18')]]
        return [self.api.quarter_flow(raw[i], raw[i-1] if i else None)
                for i in range(4)], raw

    def test_semester_reset_produces_genuine_quarters_and_annual_43(self):
        quarters, raw = self.year()
        for result, wanted in zip(quarters, [10, 15, 7, 11]):
            self.fraction(result, wanted)
        self.fraction(self.api.flow_12_months(quarters, '201112'), 43)
        self.assertEqual(quarters[1]['inputs'], [raw[1], raw[0]])
        self.assertEqual(quarters[2]['inputs'], [raw[2]])
        self.assertEqual((quarters[1]['start'], quarters[1]['end']),
                         ('2011-04-01', '2011-06-30'))
        self.assertEqual(quarters[1]['unit_key'], raw[1]['unit_key'])
        self.assertEqual(quarters[1]['definition_id'], 'profit-v1')

    def test_negative_quarter_reversal_and_zero_remain_values(self):
        self.fraction(self.api.quarter_flow(observation('201106', '-5'),
                                           observation('201103', '10')), -15)
        self.fraction(self.api.quarter_flow(observation('201103', '0')), 0)

    def test_even_quarter_requires_immediate_predecessor_and_keeps_null(self):
        current = observation('201112', '18')
        self.unavailable(self.api.quarter_flow(current), 'missing_previous')
        self.unavailable(self.api.quarter_flow(current, observation('201106', '25')),
                         'invalid_previous_period')
        result = self.api.quarter_flow(current, observation('201109', None))
        self.unavailable(result, 'native_null')
        self.assertEqual(len(result['inputs']), 2)

    def test_break_and_identity_changes_never_receive_continuity_by_name(self):
        current = observation('201906', '25', definition_id='profit-201903')
        self.unavailable(self.api.quarter_flow(current, observation('201903', '10')),
                         'incompatible_definition')
        for key in [('financial', '2', '002'), ('financial', '3', '001'),
                    ('prudential', '2', '001')]:
            with self.subTest(key=key):
                self.unavailable(self.api.quarter_flow(observation('201106', '25'),
                                 observation('201103', '10', unit_key=key)),
                                 'incompatible_unit')

    def test_scale_window_and_unapproved_rule_are_guarded(self):
        for field, value, status in [('scale', 'BRL-thousand', 'incompatible_scale'),
                                     ('window_rule', 'native-semester-v1',
                                      'incompatible_window')]:
            self.unavailable(self.api.quarter_flow(observation('201106', '25'),
                             observation('201103', '10', **{field: value})), status)
        self.unavailable(self.api.quarter_flow(observation('201103', '10',
                         window_rule='unknown')), 'unverified_window')

    def test_homologated_definition_keeps_distinct_literal_bindings_and_audit(self):
        previous = observation('201103', '10', binding={'Conta': 'old', 'Grupo': ''})
        current = observation('201106', '25')
        result = self.api.quarter_flow(current, previous)
        self.fraction(result, 15)
        self.assertEqual(result['inputs'], [current, previous])
        self.assertTrue(result['compatibility'][0]['compatible'])
        changed = self.api.quarter_flow(current, dict(previous, definition_id='other'))
        self.assertFalse(changed['compatibility'][0]['compatible'])

    def test_native_missing_invalid_nonfinite_and_ambiguous_are_distinct(self):
        for token, status in [(None, 'native_null'), ('', 'invalid_empty'),
                              ('   ', 'invalid_empty'), ('NI', 'invalid_numeric'),
                              ('NA', 'invalid_numeric'), ('[70000009]', 'invalid_numeric'),
                              ('NaN', 'non_finite'), ('Infinity', 'non_finite'),
                              (0.1, 'invalid_numeric'), (True, 'invalid_numeric')]:
            with self.subTest(token=token):
                self.unavailable(self.api.quarter_flow(observation('201103', token)), status)
        row = observation('201103', '10', status='ambiguous_occurrence')
        self.unavailable(self.api.quarter_flow(row), 'ambiguous_occurrence')

    def test_native_parser_states_are_independent_of_external_decimal_traps(self):
        for trap in (True, False):
            with localcontext() as context:
                context.traps[InvalidOperation] = trap
                before = context.copy()
                for token, status in [('NI', 'invalid_numeric'), ('not-a-number', 'invalid_numeric'),
                                      ('NaN', 'non_finite'), ('sNaN', 'non_finite'),
                                      ('Infinity', 'non_finite'), ('-Infinity', 'non_finite')]:
                    with self.subTest(trap=trap, token=token):
                        self.unavailable(self.api.quarter_flow(observation('201103', token)), status)
                self.assertEqual(context.traps, before.traps)
                self.assertEqual(context.flags, before.flags)

    def test_invalid_first_row_is_rejected_before_metadata_construction(self):
        for malformed in [123, None, 'wrong', [], {}]:
            with self.subTest(first=malformed):
                self.unavailable(self.api.flow_12_months([malformed, {}, {}, {}], '201112'),
                                 'invalid_observation')
                self.unavailable(self.api.mean_stock([malformed], date(2010, 12, 31),
                                                    date(2011, 3, 31)), 'invalid_observation')

    def test_invalid_optional_flags_and_status_are_contract_states(self):
        for field, malformed in [('flags', None), ('flags', 'flag'), ('flags', [None]),
                                  ('flags', {'flag': True}), ('status', None),
                                  ('status', False), ('status', ''), ('status', [])]:
            with self.subTest(field=field, value=malformed):
                bad = observation('201103', '10', **{field: malformed})
                self.unavailable(self.api.quarter_flow(bad), 'invalid_observation')
                self.unavailable(self.api.quarter_flow(observation('201106', '25'), bad),
                                 'invalid_observation')

    def test_invalid_collections_and_derived_inputs_return_contract_states(self):
        for malformed in [None, 123, 'not-a-list', {}]:
            with self.subTest(collection=malformed):
                self.unavailable(self.api.flow_12_months(malformed, '201112'), 'invalid_observation')
                self.unavailable(self.api.mean_stock(malformed, date(2010, 12, 31),
                                                    date(2011, 3, 31)), 'invalid_observation')
        for malformed in [None, 123, 'not-a-list', [123]]:
            q, _ = self.year()
            q[0]['inputs'] = malformed
            with self.subTest(inputs=malformed):
                self.unavailable(self.api.flow_12_months(q, '201112'), 'invalid_observation')

    def test_precision_40_digits_and_fraction_do_not_depend_on_global_context(self):
        token = '1234567890123456789012345678901234567890.00000000000000000001'
        with localcontext() as ctx:
            ctx.prec = 6
            result = self.api.quarter_flow(observation('201106', token),
                        observation('201103', '1234567890123456789012345678901234567890'))
        self.fraction(result, 1, 100000000000000000000)

    def test_flow_periods_are_quarterly_in_core_only(self):
        for period in ['200912', '202503', '201101', '201113', '2011-03', '2011031', 201103]:
            with self.subTest(period=period):
                self.unavailable(self.api.quarter_flow(observation(period, '10')),
                                 'invalid_period')

    def test_ttm_crosses_year_and_preserves_all_native_dependencies(self):
        q, raw = self.year('2011')
        next_q = self.api.quarter_flow(observation('201203', '2'))
        result = self.api.flow_12_months(q[1:] + [next_q], '201203')
        self.fraction(result, 35)
        self.assertEqual((result['start'], result['end']),
                         ('2011-04-01', '2012-03-31'))
        self.assertEqual(result['inputs'], raw[1:2] + raw[:1] + raw[2:3] +
                         raw[3:] + raw[2:3] + [observation('201203', '2')])

    def test_ttm_uses_exact_fractions_never_rounded_display(self):
        q, _ = self.year()
        for result in q:
            result['value_fraction'] = {'numerator': '1', 'denominator': '3'}
            result['value'] = '0.3'  # Intentionally unusable display.
        result = self.api.flow_12_months(q, '201112')
        self.fraction(result, 4, 3)
        self.assertEqual(result['value'], '1.' + '3' * 99)

    def test_display_half_even_and_traps_are_local_to_the_calculation(self):
        # At the 100th significant digit: 2.5 ties to even 2; 3.5 ties to 4.
        with localcontext() as context:
            context.prec = 6
            context.rounding = ROUND_DOWN
            context.traps[Inexact] = True
            even = self.api.quarter_flow(observation('201103', '1.' + '0'*98 + '25'))
            odd = self.api.quarter_flow(observation('201103', '1.' + '0'*98 + '35'))
        self.assertEqual(even['value'], '1.' + '0'*98 + '2')
        self.assertEqual(odd['value'], '1.' + '0'*98 + '4')

    def test_ttm_requires_complete_ordered_disjoint_quarters_and_requested_end(self):
        q, _ = self.year()
        for quarters in [q[:3], q + q[:1], q[:2] + q[1:2] + q[3:], list(reversed(q))]:
            with self.subTest(periods=[r['period'] for r in quarters]):
                self.unavailable(self.api.flow_12_months(quarters, '201112'),
                                 'insufficient_history' if len(quarters) < 4 else 'invalid_sequence')
        broken = deepcopy(q)
        broken[1]['start'] = '2011-03-31'
        self.unavailable(self.api.flow_12_months(broken, '201112'), 'invalid_interval')
        self.unavailable(self.api.flow_12_months(q, '201109'), 'invalid_sequence')
        for end in ['201003', '201006', '201009']:
            self.unavailable(self.api.flow_12_months([], end), 'insufficient_history')

    def test_ttm_propagates_noncalculable_and_guards_definition_and_fraction(self):
        q, _ = self.year()
        q[1] = self.api.quarter_flow(observation('201106', '25'))
        self.unavailable(self.api.flow_12_months(q, '201112'), 'missing_previous')
        q, _ = self.year()
        q[2]['definition_id'] = 'other'
        self.unavailable(self.api.flow_12_months(q, '201112'), 'incompatible_definition')
        q, _ = self.year()
        q[2]['value_fraction']['denominator'] = '0'
        self.unavailable(self.api.flow_12_months(q, '201112'), 'invalid_fraction')

    def test_stock_days_are_trapezoidal_with_leap_year_and_100_digit_display(self):
        for year, numerator, denominator in [('2011', 31700, 181), ('2012', 175, 1)]:
            points = [stock(str(int(year)-1)+'12', '100'), stock(year+'03', '200'),
                      stock(year+'06', '200')]
            result = self.api.mean_stock(points, date(int(year)-1, 12, 31),
                                         date(int(year), 6, 30))
            self.fraction(result, numerator, denominator)
            self.assertEqual(result['inputs'], points)
        result = self.api.mean_stock([stock('201012', '0'), stock('201103', '300')],
                                     date(2010, 12, 31), date(2011, 3, 31))
        self.fraction(result, 150)

    def test_annual_stock_uses_five_points_and_real_91_92_day_weights(self):
        points = [stock(p, t) for p, t in [('201012', '0'), ('201103', '100'),
                  ('201106', '200'), ('201109', '300'), ('201112', '400')]]
        # Areas: 50*90 + 150*91 + 250*92 + 350*92 = 73350.
        self.fraction(self.api.mean_stock(points, date(2010, 12, 31), date(2011, 12, 31)),
                      14670, 73)

    def test_missing_opening_and_inner_stock_do_not_shorten_horizon(self):
        points = [stock('201012', '100'), stock('201103', '200'), stock('201106', '200')]
        args = (date(2010, 12, 31), date(2011, 6, 30))
        self.unavailable(self.api.mean_stock(points[1:], *args), 'missing_opening')
        self.unavailable(self.api.mean_stock(points[::2], *args), 'missing_stock_point')
        self.unavailable(self.api.mean_stock(points[:2], *args), 'missing_stock_point')

    def test_duplicate_reversed_nonquarter_and_period_mismatch_do_not_calculate(self):
        points = [stock('201012', '100'), stock('201103', '200'), stock('201106', '200')]
        args = (date(2010, 12, 31), date(2011, 6, 30))
        for malformed in [points[:1]+points, list(reversed(points)),
                          [points[0], stock('201102', '200'), points[2]]]:
            self.assertNotEqual(self.api.mean_stock(malformed, *args)['status'], 'ok')
        self.unavailable(self.api.mean_stock(points, date(2010, 12, 30), args[1]),
                         'invalid_interval')
        self.unavailable(self.api.mean_stock(points, args[0], args[0]), 'invalid_interval')

    def test_opening_200912_is_stock_only_and_does_not_enable_2009_horizon(self):
        points = [stock('200912', '100'), stock('201003', '200')]
        self.fraction(self.api.mean_stock(points, date(2009, 12, 31), date(2010, 3, 31)), 150)
        self.unavailable(self.api.mean_stock([stock('200909', '100')] + points,
                         date(2009, 9, 30), date(2010, 3, 31)), 'invalid_interval')
        self.unavailable(self.api.mean_stock([stock('202412', '100'), stock('202503', '200')],
                         date(2024, 12, 31), date(2025, 3, 31)), 'invalid_interval')

    def test_stock_compatibility_and_native_states_are_not_imputed(self):
        start, end = date(2010, 12, 31), date(2011, 3, 31)
        for changes, status in [({'definition_id': 'changed'}, 'incompatible_definition'),
                                ({'unit_key': ('financial', '2', 'other')}, 'incompatible_unit'),
                                ({'scale': 'USD'}, 'incompatible_scale'),
                                ({'window_rule': 'native-semester-analysis-v2'},
                                 'incompatible_window'), ({'token': None}, 'native_null')]:
            last = stock('201103', '200')
            last.update(changes)
            self.unavailable(self.api.mean_stock([stock('201012', '100'), last], start, end), status)

    def test_inputs_remain_unchanged_and_control_flags_survive(self):
        points = [stock('201012', '100', flags=['annual_control_not_continuous']),
                  stock('201103', '200')]
        before = deepcopy(points)
        result = self.api.mean_stock(points, date(2010, 12, 31), date(2011, 3, 31))
        self.assertEqual(points, before)
        self.assertIn('annual_control_not_continuous', result['flags'])
        points[0]['sources'][0]['file'] = 'changed-after-call'
        self.assertEqual(result['inputs'][0]['sources'][0]['file'], 'captured.json')



class CoverageTests(unittest.TestCase):
    def setUp(self):
        from bank_quality import ifdata_analysis
        self.api=ifdata_analysis

    @staticmethod
    def f(n,d=1):return {'numerator':str(n),'denominator':str(d)}

    def row(self,company,code,n,d,**changes):
        row=dict(id=company+'|'+code,company=company,company_name=company,block='principal',period='202412',metric='R1',horizon='quarter',
            dataset='financial',code=code,unit_key=['financial','2',code],financial_unit_key=['financial','2',code],
            status='ok',applicability='applicable',numerator_fraction=self.f(n),denominator_fraction=self.f(d),
            value_fraction=self.f(n,d),asset_fraction=self.f(d),target_cadastro={'Data':'202412','Tcb':'B1','Sr':None},flags=[])
        row.update(changes);return row

    def run_rows(self,rows):
        self.assertTrue(callable(getattr(self.api,'aggregate_results',None)), 'Exact coverage aggregation is missing')
        return self.api.aggregate_results(rows)

    def test_ratio_of_sums_dedup_and_exact_median_are_distinct(self):
        rows=[self.row('A','a',1,100),self.row('B','b',18,900),self.row('C','a',1,100)]
        out=self.run_rows(rows);a=out['aggregates'][0];d=out['distributions'][0]
        self.assertEqual(a['value_fraction'],self.f(19,1000))
        self.assertEqual(a['counts']['expected_companies'],3)
        self.assertEqual(a['counts']['eligible_units'],2)
        self.assertEqual(d['median_fraction'],self.f(3,200))
        self.assertEqual(a['asset_coverage']['share_of_known_fraction'],self.f(1))
        self.assertEqual(out,self.run_rows(list(reversed(rows))))

    def test_missing_large_unit_and_unknown_assets_remain_named(self):
        rows=[self.row('A','a',1,100),self.row('B','b',18,900,status='native_null',value_fraction=None)]
        a=self.run_rows(rows)['aggregates'][0]
        self.assertEqual(a['asset_coverage']['share_of_known_fraction'],self.f(1,10))
        self.assertEqual(a['lists']['missing_companies'],['B'])
        rows[1]['asset_fraction']=None
        a=self.run_rows(rows)['aggregates'][0]
        self.assertEqual(a['asset_coverage']['status'],'partial_known_assets')
        self.assertEqual(a['asset_coverage']['unknown_companies'],['B'])
        self.assertIsNone(a['asset_coverage']['share_of_total_fraction'])

    def test_unknown_calculable_is_diagnostic_and_no_eligible_is_explicit(self):
        a=self.run_rows([self.row('A','a',1,100,applicability='unknown')])['aggregates'][0]
        self.assertEqual(a['status'],'no_eligible_units')
        self.assertEqual(a['lists']['diagnostic_companies'],['A'])
        self.assertEqual(a['counts']['calculable_companies'],1)
        self.assertEqual(a['counts']['unknown_companies'],1)

    def test_prudential_dedup_is_separate_from_financial_asset_coverage(self):
        rows=[self.row('A','p',1,100,metric='C3',horizon='point',dataset='capital',unit_key=['capital','3','p'],financial_unit_key=['financial','2','a'],asset_fraction=self.f(100)),
              self.row('B','p',1,100,metric='C3',horizon='point',dataset='capital',unit_key=['capital','3','p'],financial_unit_key=['financial','2','b'],asset_fraction=self.f(900))]
        a=self.run_rows(rows)['aggregates'][0]
        self.assertEqual(a['counts']['eligible_units'],1)
        self.assertEqual(a['asset_coverage']['known_financial_units'],2)
        self.assertEqual(a['denominator_fraction'],self.f(100))

    def test_own_denominator_negative_and_zero_sum_are_preserved(self):
        rows=[self.row('A','a',2,10,metric='Q2'),self.row('B','b',3,-10,metric='Q2')]
        a=self.run_rows(rows)['aggregates'][0]
        self.assertEqual(a['status'],'zero_denominator')
        self.assertIn('non_convex_denominator_weights',a['flags'])
        rows[1]['denominator_fraction']=self.f(-5)
        a=self.run_rows(rows)['aggregates'][0]
        self.assertEqual(a['value_fraction'],self.f(1))
        rows[0]['metric']=rows[1]['metric']='R2'
        self.assertEqual(self.run_rows(rows)['aggregates'][0]['value_fraction'],self.f(1))

    def test_disagreeing_duplicate_unit_is_not_arbitrarily_selected(self):
        a=self.run_rows([self.row('A','a',1,100),self.row('B','a',2,100)])['aggregates'][0]
        self.assertEqual(a['status'],'no_eligible_units')
        self.assertEqual(a['lists']['conflicting_units'],[['financial','2','a']])

    def test_type2_manual_quantiles_n1_n2_n4_n5_n20_and_ties(self):
        for values,wanted in [([7],(7,7,7,0)),([1,3],(1,2,3,2)),([1,2,3,4],('1.5','2.5','3.5',2)),
                              ([1,2,3,4,5],(2,3,4,2)),(list(range(1,21)),('5.5','10.5','15.5',10)),([2,2,2,2],(2,2,2,0))]:
            out=self.run_rows([self.row(str(i),str(i),n,1) for i,n in enumerate(values)])['distributions'][0]
            self.assertEqual(tuple(out[k] for k in ('q1','median','q3','iqr')),tuple(map(str,wanted)))

    def test_segments_preserve_native_null_empty_and_conflict(self):
        rows=[self.row('A','a',1,10),self.row('B','b',1,10,target_cadastro={'Data':'202412','Sr':''}),
              self.row('C','a',1,10,target_cadastro={'Data':'202412','Sr':'S1'})]
        out=self.run_rows(rows)
        sr=[r for r in out['segment_coverage'] if r['field']=='Sr']
        self.assertEqual({r['category_state'] for r in sr},{'conflict','empty'})
        solo=self.run_rows(rows[:1]);sr=[r for r in solo['segment_coverage'] if r['field']=='Sr'][0]
        self.assertEqual(sr['category_state'],'null')
        rows[0]['target_cadastro']['Data']='202409'
        sr=[r for r in self.run_rows(rows[:1])['segment_coverage'] if r['field']=='Sr'][0]
        self.assertEqual(sr['category_state'],'missing_dated_cadastro')

    def test_complementary_documentary_control_never_adopts_quantity(self):
        row=self.row('A','a',1,100,block='complementary',adoption='complementary_observation_only_no_quantitative_adoption_no_backfilled_control',documentary_state='annual_filing_explicit_control_path')
        out=self.run_rows([row]);a=out['aggregates'][0]
        self.assertEqual(a['status'],'no_adopted_complementary_units')
        self.assertEqual(out['distributions'][0]['n'],0)
        self.assertEqual(a['counts']['expected_companies'],1)

    def test_expected_map_drives_coverage_and_joint_is_only_diagnostic(self):
        self.assertTrue(callable(getattr(self.api,'analysis_coverage',None)), 'Expected nominal coverage missing')
        maps=[dict(id='A|202412',company='A',company_name='A',period='202412',financial_code='a',prudential_code=None,
                   financial_target_cadastro={'Data':'202412'},prudential_target_cadastro=None,result_ids=['r']),
              dict(id='B|202412',company='B',company_name='B',period='202412',financial_code=None,prudential_code=None,
                   financial_target_cadastro=None,prudential_target_cadastro=None,result_ids=[])]
        result=self.row('A','a',1,100,id='r')
        coverage=self.api.analysis_coverage(maps,[result],[],[])
        self.assertEqual(len(coverage),28)
        b=[r for r in coverage if r['company']=='B']
        self.assertEqual(len(b),14)
        self.assertTrue(all(r['status']=='missing_unit' for r in b))
        a=self.run_rows(coverage)['aggregates']
        r1=next(r for r in a if r['metric']=='R1' and r['horizon']=='quarter')
        self.assertEqual(r1['counts']['eligible_companies'],1)
        self.assertEqual(r1['joint_coverage']['complete_companies'],[])

    def test_build_final_tables_and_replay_are_deterministic(self):
        package=PackageTests();package.setUp();self.addCleanup(package.doCleanups)
        config=package.fixtures();first=package.root/'first';second=package.root/'second'
        manifest=self.api.build_analysis(config,first)
        self.assertEqual(manifest['stage'],'coverage-and-aggregation')
        self.assertEqual(manifest['tables']['company_coverage'],42)
        self.assertIn('aggregates',manifest['tables'])
        self.api.build_analysis(config,second)
        for table in manifest['tables']:
            self.assertEqual((first/(table+'.json')).read_bytes(),(second/(table+'.json')).read_bytes())
        rows=self.api.query_analysis(first,package.digest(first/'manifest.json'),'select count(*) as n from company_coverage')
        self.assertEqual(rows,[{'n':42}])


    def test_complementary_annual_availability_preserves_nonadoption_even_with_control_evidence(self):
        self.assertTrue(callable(getattr(self.api,'analysis_coverage',None)))
        maps=[dict(id='A|202412',company='A',company_name='A',period='202412',financial_code=None,
                   prudential_code=None,financial_target_cadastro=None,result_ids=[])]
        observation=dict(period='202412',native_financial_target='F',pair_2024={'company_cnpj14':'A'},
            adoption='complementary_observation_only_no_quantitative_adoption_no_backfilled_control',
            annual_documentary_evidence={'state':'annual_filing_explicit_control_path'})
        component=dict(id='AT|financial|F|202412',component='AT',dataset='financial',code='F',period='202412',status='ok',
                       target_cadastro={'Data':'202412','Tcb':'OWN_NATIVE','Sr':None})
        rows=[r for r in self.api.analysis_coverage(maps,[],[component],[observation]) if r['block']=='complementary']
        self.assertEqual(len(rows),10)
        self.assertEqual({r['horizon'] for r in rows},{'point','ttm'})
        self.assertTrue(all(r['annual_summary'] for r in rows))
        self.assertEqual(sum('evidence' in r for r in rows),1)
        c1=next(r for r in rows if r['metric']=='C1')
        self.assertEqual(next(c for c in c1['component_availability'] if c['component']=='AT')['status'],'ok')
        self.assertEqual(c1.get('target_cadastro',{}).get('Tcb'),'OWN_NATIVE')
        self.assertTrue(all(r['status']=='observation_only_no_quantitative_adoption' for r in rows))
        observation['period']='202409';maps[0]['period']='202409'
        with self.assertRaises(ValueError):self.api.analysis_coverage(maps,[],[],[observation])

    def test_unit_counts_and_company_names_cover_missing_and_proven_not_applicable(self):
        rows=[self.row('A','a',1,100,company_name='Alpha'),self.row('B','b',18,900,status='native_null',value_fraction=None,company_name='Beta'),
              self.row('C','c',0,1,applicability='not_applicable',applicability_evidence={'source':'dated activity proof'})]
        a=self.run_rows(rows)['aggregates'][0]
        self.assertEqual(a['counts'].get('missing_units'),1)
        self.assertEqual(a['counts']['calculable_units'],2)
        self.assertEqual(a['counts']['not_applicable_units'],1)
        self.assertEqual(a['company_names']['B'],['Beta'])
        del rows[2]['applicability_evidence']
        a=self.run_rows(rows)['aggregates'][0]
        self.assertEqual(a['counts']['not_applicable_companies'],0)
        self.assertIn('C',a['lists']['unknown_companies'])

    def test_asset_wrong_currency_is_unknown_and_zero_is_known(self):
        self.assertTrue(callable(getattr(self.api,'analysis_coverage',None)))
        mapping=dict(id='A|202412',company='A',company_name='A',period='202412',financial_code='F',
            prudential_code=None,financial_target_cadastro={'Data':'202412'},result_ids=[])
        asset=stock('202412','10',scale='USD',id='asset',component='AT',dataset='financial',code='F',
                    target_cadastro={'Data':'202412'})
        rows=self.api.analysis_coverage([mapping],[],[asset],[])
        self.assertTrue(all(r['asset_fraction'] is None for r in rows))
        self.assertTrue(all(r['asset_status']=='invalid_scale' for r in rows))
        asset.update(scale='BRL',token='0')
        rows=self.api.analysis_coverage([mapping],[],[asset],[])
        self.assertTrue(all(r['asset_fraction']==self.f(0) for r in rows))


    def test_preexisting_stage2_remains_verifiable_and_queryable(self):
        package=PackageTests();package.setUp();self.addCleanup(package.doCleanups)
        config=package.fixtures();out=package.root/'final';manifest=self.api.build_analysis(config,out)
        old=package.root/'stage2';old.mkdir()
        old_tables=('components','results','company_map')
        manifest['stage']='bindings-and-calculations'
        manifest['tables']={k:v for k,v in manifest['tables'].items() if k in old_tables}
        manifest['files']=[r for r in manifest['files'] if r['file'].split('.')[0] in old_tables]
        for entry in manifest['files']:(old/entry['file']).write_bytes((out/entry['file']).read_bytes())
        (old/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        self.assertEqual(self.api.verify_analysis(old,package.digest(old/'manifest.json'))['stage'],'bindings-and-calculations')
        self.assertEqual(self.api.query_analysis(old,package.digest(old/'manifest.json'),'select count(*) as n from company_map'),[{'n':3}])



class BoundedIOTests(unittest.TestCase):
    def setUp(self):
        from bank_quality import ifdata_analysis
        self.api=ifdata_analysis
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def package(self,rows):
        out=self.root/'package';out.mkdir()
        tables=dict(components=rows,results=[],company_map=[])
        files=self.api._write_tables(out,tables)
        manifest=dict(contract=self.api.ANALYSIS_CONTRACT,stage='bindings-and-calculations',files=files,
            tables={k:len(v) for k,v in tables.items()},table_columns=list(self.api.TABLE_COLUMNS))
        self.write_manifest(out,manifest)
        return out,manifest

    def write_manifest(self,out,manifest):
        for entry in manifest['files']:
            entry['sha256']=hashlib.sha256((out/entry['file']).read_bytes()).hexdigest()
        (out/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        return hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest()

    def test_streamed_json_preserves_legacy_pretty_bytes_and_platform_newlines(self):
        out,_=self.package([{'id':'á'}])
        expected=self.root/'legacy.json'
        expected.write_text('[\n  {\n    "id": "á"\n  }\n]\n',encoding='utf-8')
        self.assertEqual((out/'components.json').read_bytes(),expected.read_bytes())

    def test_joint_diagnostic_cannot_leak_principal_companies_into_complementary_block(self):
        fixture=CoverageTests();fixture.setUp()
        rows=[fixture.row('PRINCIPAL_ONLY','p',1,100,metric=m,horizon='quarter' if m in ('R1','R2','Q2','E2-B') else 'point')
              for m in ('R1','R2','Q1','Q2','C1','C3','C4','L2','L3','E2-B')]
        rows.append(fixture.row('COMPLEMENT_ONLY','c',1,100,block='complementary'))
        aggregates=self.api.aggregate_results(rows)['aggregates']
        complementary=next(r for r in aggregates if r['block']=='complementary')
        self.assertEqual(complementary['joint_coverage']['complete_companies'],[])
        self.assertEqual(complementary['joint_coverage'].get('block'),'complementary')
        self.assertEqual(complementary['joint_coverage'].get('status'),'no_adopted_complementary_units')
        principal=next(r for r in aggregates if r['block']=='principal')
        self.assertEqual(principal['joint_coverage']['complete_companies'],['PRINCIPAL_ONLY'])
        self.assertEqual(principal['joint_coverage'].get('block'),'principal')
        self.assertEqual(principal['joint_coverage'].get('population_scope'),'all_expected_principal_companies_at_date')

    def test_writer_and_verify_python_memory_do_not_scale_with_total_payload(self):
        import tracemalloc
        blob='á\t"\n'+('x'*(512*1024))
        rows=[dict(id=str(i),period='202412',metric=None if i%2 else '',horizon='point',dataset='financial',
                   code='F',status='ok',nested={'text':blob,'exact':'12345678901234567890.12345678901234567890'}) for i in range(32)]
        out=self.root/'package';out.mkdir()
        tracemalloc.start()
        try:
            files=self.api._write_tables(out,dict(components=rows,results=[],company_map=[]))
            writer_peak=tracemalloc.get_traced_memory()[1]
        finally:tracemalloc.stop()
        with self.subTest(operation='writer'):
            self.assertLess(writer_peak,12*1024*1024,'Writer duplicated the complete payload in Python')
        manifest=dict(contract=self.api.ANALYSIS_CONTRACT,stage='bindings-and-calculations',files=files,
            tables={'components':32,'results':0,'company_map':0},table_columns=list(self.api.TABLE_COLUMNS))
        pin=self.write_manifest(out,manifest)
        tracemalloc.start()
        try:
            self.api.verify_analysis(out,pin)
            verify_peak=tracemalloc.get_traced_memory()[1]
        finally:tracemalloc.stop()
        self.assertLess(verify_peak,12*1024*1024,'Verifier materialized the complete payload in Python')
        self.assertGreater((out/'components.json').stat().st_size,16*1024*1024)

    def test_textual_io_preserves_null_empty_quotes_newline_unicode_and_exact_payload(self):
        row=dict(id='línea\t"\n',period=None,metric='',horizon='point',dataset='financial',code='',status=None,
                 nested={'null':None,'empty':'','precise':'99999999999999999999.00000000000000000001'})
        out,manifest=self.package([row]);pin=self.write_manifest(out,manifest)
        self.api.verify_analysis(out,pin)
        actual=self.api.query_analysis(out,pin,'select period,metric,code,status,payload from components')[0]
        self.assertIsNone(actual['period']);self.assertEqual(actual['metric'],'');self.assertEqual(actual['code'],'')
        self.assertIsNone(actual['status']);self.assertEqual(json.loads(actual['payload']),row)

    def test_streaming_array_rejects_truncation_trailing_garbage_duplicate_keys_and_ids(self):
        out,manifest=self.package([dict(id='one',metric=None),dict(id='two',metric='')])
        original=(out/'components.json').read_text(encoding='utf-8')
        mutations=['{}',original[:-3],original+'{}',original.replace('"id": "one"','"id": "one", "id": "duplicate"'),
                   original.replace('"two"','"one"'),original.replace('},','},,',1),'[', '[1]', '[{"id":"x"},]',
                   '\u00a0'+original,original+'\u00a0',original.replace('[','[\u2003',1)]
        for mutation in mutations:
            with self.subTest(mutation=mutation[:60]):
                (out/'components.json').write_text(mutation,encoding='utf-8')
                pin=self.write_manifest(out,manifest)
                with self.assertRaises(ValueError):self.api.verify_analysis(out,pin)
        (out/'components.json').write_text(original,encoding='utf-8')
        # A repinned CSV that interchanges null and quoted empty must still fail.
        original_csv=(out/'components.csv').read_bytes()
        (out/'components.csv').write_bytes(original_csv.replace(b'"one",,',b'"one","",',1))
        pin=self.write_manifest(out,manifest)
        with self.assertRaises(ValueError):self.api.verify_analysis(out,pin)




class UniverseTests(PackageTests):
    # Inherit fixture utilities, not the legacy test methods (removed below).
    def setUp(self):
        super().setUp()
        self.assertTrue(hasattr(self.api, 'build_universe_analysis'), 'Missing bounded universe builder')

    def universe_fixture(self):
        from bank_quality.ifdata_population import build_population
        from bank_quality.ifdata_odata import COLUMNS, CONTRACT
        from bank_quality.ifdata_variable_catalog import build_catalog
        cfg=self.fixtures()
        profile=self.api.load_universe_profile('universe-2010-2024')
        rows=[]
        for code,amount in [('I','200'),('J','0')]:
            for period in ['202312','202403','202406','202409','202412']:
                for c in profile['contexts']:
                    if c['literal_context']['dataset']!='individual' or period not in c['periods']:continue
                    r={k:v for k,v in c['literal_context'].items() if k!='dataset'}
                    r.update(AnoMes=period,CodInst=code,Saldo=amount,source_file='own.gz',source_sha256='b'*64,
                             source_row=str(len(rows)+1),source_context='literal',source_url='https://example.invalid/own',source_collected_utc='2026-10-14T00:00:00Z')
                    rows.append(r)
        cfg['inputs']['individual']=self.native_package('individual',rows,COLUMNS,CONTRACT)
        # Population requires explicit period/type in each native part. Split
        # the actual fixture rows; no fabricated population output is accepted.
        import duckdb
        for ds in ['financial','individual','capital','cadastro']:
            root=Path(cfg['inputs'][ds]['root']);m=json.loads((root/'manifest.json').read_text())
            with duckdb.connect() as con:
                con.from_parquet(str(root/'part.parquet')).create_view('source')
                m['files']=[]
                for period in ['202312','202403','202406','202409','202412']:
                    field='Data' if ds=='cadastro' else 'AnoMes'
                    target=root/(period+'.parquet')
                    con.execute('copy (select * from source where '+field+'=$period) to $target (format parquet)',dict(period=period,target=str(target)))
                    count=con.execute('select count(*) from read_parquet(?)',[str(target)]).fetchone()[0]
                    part=dict(file=target.name,rows=count,period=period,sha256=self.digest(target))
                    if ds!='cadastro':part['type']={'financial':2,'individual':3,'capital':1}[ds]
                    m['files'].append(part)
            (root/'part.parquet').unlink()
            (root/'manifest.json').write_text(json.dumps(m),encoding='utf-8')
            cfg['inputs'][ds]['expected_manifest_sha256']=self.digest(root/'manifest.json')
        cat=self.root/'universe-catalogue'
        build_catalog({ds:cfg['inputs'][ds]['root'] for ds in ['financial','individual','capital']},cat)
        cfg['inputs']['catalogue']=dict(root=str(cat),expected_manifest_sha256=self.digest(cat/'manifest.json'))
        sample=Path(cfg['inputs']['sample']['root'])
        maps=json.loads((sample/'company-quarter-map.json').read_text())
        maps.extend(dict(maps[0],company_cnpj14=str(i)) for i in range(4,25))
        (sample/'company-quarter-map.json').write_text(json.dumps(maps),encoding='utf-8')
        sm=json.loads((sample/'manifest.json').read_text());sm['files']['company-quarter-map.json']=self.digest(sample/'company-quarter-map.json')
        (sample/'manifest.json').write_text(json.dumps(sm),encoding='utf-8')
        cfg['inputs']['sample']['expected_manifest_sha256']=self.digest(sample/'manifest.json')
        pop=self.root/'population'
        build_population(dict(periods=['202412'],datasets=['financial','individual','capital'],inputs=cfg['inputs']),pop)
        return dict(periods=['202412'],datasets=['financial','individual','capital'],profile_id='universe-2010-2024',
                    profile_expected_sha256=self.digest(self.api.UNIVERSE_PROFILE_PATH),
                    population=dict(root=str(pop),expected_manifest_sha256=self.digest(pop/'manifest.json')))

    def test_universe_own_types_unknown_membership_exact_and_batch_invariance(self):
        cfg=self.universe_fixture();a=self.root/'a';b=self.root/'b'
        ma=self.api.build_universe_analysis(cfg,a,batch_size=1)
        self.api.build_universe_analysis(cfg,b,batch_size=3)
        rows=json.loads((a/'results.json').read_text())
        self.assertEqual(len(rows),38)
        self.assertEqual(len({r['id'] for r in rows}),38)
        ci=next(r for r in rows if r['code']=='I' and r['metric']=='C1')
        self.assertEqual((ci['value'],ci['applicability']),('1','applicable'))
        self.assertEqual(ci['unit_key'],['individual','3','I'])
        self.assertEqual(ci['membership'],'unknown')
        cj=next(r for r in rows if r['code']=='J' and r['metric']=='C1')
        self.assertEqual(cj['status'],'zero_denominator')
        cp=next(r for r in rows if r['metric']=='C3')
        self.assertEqual(cp['applicability'],'applicable')
        self.assertEqual(ma['stage'],'coverage-and-aggregation')
        for item in ma['files']:self.assertEqual((a/item['file']).read_bytes(),(b/item['file']).read_bytes())
        self.api.verify_universe_analysis(a,self.digest(a/'manifest.json'))
        with self.assertRaises(FileExistsError):self.api.build_universe_analysis(cfg,a)

    def test_universe_fail_closed_config_and_external_pins(self):
        cfg=self.universe_fixture()
        for key,val in [('profile_id','arbitrary.json'),('profile_expected_sha256','0'*64),('datasets',['segmentation']),('periods',['202503'])]:
            bad=deepcopy(cfg);bad[key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):self.api.build_universe_analysis(bad,self.root/'bad')
        bad=deepcopy(cfg);bad['population']['expected_manifest_sha256']='0'*64
        with self.assertRaises(ValueError):self.api.build_universe_analysis(bad,self.root/'bad')
        bad=deepcopy(cfg);bad['profile_path']='arbitrary'
        with self.assertRaises(ValueError):self.api.build_universe_analysis(bad,self.root/'bad')
        bad=deepcopy(cfg);bad['opening']=dict(root='unknown',expected_manifest_sha256='0'*64)
        with self.assertRaises((ValueError,FileNotFoundError)):self.api.build_universe_analysis(bad,self.root/'bad')

    def test_universe_verifier_rejects_coherent_dangling_reference_and_query_blocks_io(self):
        from bank_quality.ifdata_universe_analysis import Writer
        from contextlib import ExitStack
        import duckdb
        cfg=self.universe_fixture();out=self.root/'a';m=self.api.build_universe_analysis(cfg,out)
        query=self.api.query_universe_analysis(out,self.digest(out/'manifest.json'),"select count(*) as n from results where dataset='individual'")
        self.assertEqual(query,[{'n':24}])
        with self.assertRaisesRegex(ValueError,'Query row limit'):
            self.api.query_universe_analysis(out,self.digest(out/'manifest.json'),'select * from range(10001)')
        for sql in ("select * from read_csv('external.csv')",'select 1;select 2','delete from results'):
            with self.assertRaises(Exception):self.api.query_universe_analysis(out,self.digest(out/'manifest.json'),sql)
        rows=list(self.api._iter_json_array(out/'results.json'))
        first=next(r for r in rows if r['metric']=='C1')
        first['components']['AT']['inputs'][0]={'component_ref':'missing'}
        with ExitStack() as stack,duckdb.connect() as con:
            w=Writer(out,'results',stack)
            for r in rows:w.append(r)
            new=w.finish(con)
        m['files']=[e for e in m['files'] if not e['file'].startswith('results.')]+new
        (out/'manifest.json').write_text(json.dumps(m),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Unresolved component reference'):
            self.api.verify_universe_analysis(out,self.digest(out/'manifest.json'))

    def test_universe_regression_reports_unobserved_legacy_unit_nominally(self):
        cfg=self.universe_fixture();out=self.root/'u';self.api.build_universe_analysis(cfg,out)
        pm=json.loads((Path(cfg['population']['root'])/'manifest.json').read_text())
        old=dict(periods=['202412'],profile_expected_sha256=self.digest(self.api.PROFILE_PATH),inputs={k:v for k,v in pm['config']['inputs'].items() if k!='individual'})
        baseline=self.root/'baseline';self.api.build_analysis(old,baseline)
        self.assertTrue(hasattr(self.api,'compare_universe_analysis'),'Missing automated baseline comparator')
        report=self.api.compare_universe_analysis(out,self.digest(out/'manifest.json'),baseline,self.digest(baseline/'manifest.json'))
        self.assertEqual(report['matched'],14)
        self.assertEqual(report['differences'],[])
        self.assertEqual(len(report['missing_baseline_keys']),12)
        self.assertEqual({r['code'] for r in report['missing_baseline_keys']},{'F2'})
        self.assertEqual({r['cause'] for r in report['missing_baseline_keys']},{'native_unit_not_reported_in_population'})

    def test_universe_component_dependencies_are_native_and_bounded(self):
        cfg=self.universe_fixture();out=self.root/'a';self.api.build_universe_analysis(cfg,out)
        rows=list(self.api._iter_json_array(out/'results.json'))
        q=next(r for r in rows if r['code']=='I' and r['metric']=='R1' and r['horizon']=='quarter')
        resolved=self.api.resolve_universe_result(out,self.digest(out/'manifest.json'),q['id'])
        self.assertEqual(resolved['components']['LL']['inputs'][0]['unit_key'],['individual','3','I'])
        self.assertEqual({r['period'] for r in resolved['components']['AT']['inputs']},{'202409','202412'})
        self.assertEqual(resolved['components']['LL']['inputs'][0]['binding']['literal_context']['dataset'],'individual')

# Prevent duplicated legacy test execution while sharing its native fixture helpers.
for _name in list(PackageTests.__dict__):
    if _name.startswith('test_') and _name not in UniverseTests.__dict__:
        setattr(UniverseTests,_name,None)

class UniverseWriterMemoryTests(unittest.TestCase):
    def test_large_escaped_csv_is_bounded_lossless_ordered_and_deterministic(self):
        import io
        import duckdb
        from contextlib import ExitStack
        from bank_quality import ifdata_universe_analysis as universe
        from bank_quality import ifdata_analysis as analysis
        parquet_pins=[]
        with tempfile.TemporaryDirectory() as temporary:
            for replay in range(2):
                output=Path(temporary)/str(replay);output.mkdir()
                with ExitStack() as stack,duckdb.connect(config={'memory_limit':'128MiB','threads':1}) as con:
                    if replay:
                        con.execute('create view prior_native as select * from range(100000)')
                        con.execute('select sum(range) from prior_native').fetchone()
                    self.assertTrue(con.execute("select current_setting('preserve_insertion_order')").fetchone()[0])
                    writer=universe.Writer(output,'results',stack)
                    for index in range(150000):
                        writer.append(dict(id=str(index),period='202412',metric=None if index%3==0 else '',
                            horizon='point',dataset='financial',code=str(index),status='ok',
                            text='á"x\r\n'+str(index)+'z'*1200))
                    files=writer.finish(con)
                    self.assertTrue(all(entry['rows']==150000 for entry in files))
                    digest=hashlib.sha256();buffer=io.StringIO(newline='')
                    csv_writer=csv.writer(buffer,quoting=csv.QUOTE_NOTNULL)
                    csv_writer.writerow(analysis.TABLE_COLUMNS)
                    cursor=con.execute('select * from read_parquet(?)',[str(output/'results.parquet')])
                    count=0
                    for batch in iter(lambda:cursor.fetchmany(256),[]):
                        for row in batch:
                            self.assertEqual(row[0],str(count));count+=1
                            csv_writer.writerow(row)
                        digest.update(buffer.getvalue().encode('utf-8'));buffer.seek(0);buffer.truncate(0)
                    self.assertEqual(count,150000)
                    self.assertEqual(digest.hexdigest(),analysis._digest_file(output/'results.csv'))
                    parquet_pins.append(analysis._digest_file(output/'results.parquet'))
        self.assertEqual(parquet_pins[0],parquet_pins[1])


class UniverseNormalizationTests(unittest.TestCase):
    def test_normalization_preserves_ambiguous_and_null_native_tokens(self):
        from bank_quality.ifdata_universe_analysis import _compact_component,_expand_component,load_profile
        p=load_profile();c=next(c for c in p['contexts'] if c['component']=='AT' and c['literal_context']['dataset']=='individual')
        sources=[dict({k:v for k,v in c['literal_context'].items() if k!='dataset'},CodInst='X',AnoMes='202412',Saldo=token,source_row=str(i)) for i,token in enumerate([None,'','1.00','2.00'])]
        ob=stock('202412',None,unit_key=('individual','3','X'),binding=c,sources=sources)
        ob.update(id='ref',dataset='individual',code='X',status='ambiguous_occurrence')
        self.assertEqual(_expand_component(_compact_component(ob),p),ob)

    def test_opening_predicate_own_identity_flags_zero_and_missing(self):
        from bank_quality.ifdata_universe_analysis import opening_observation,load_profile
        p=load_profile();c=next(c for c in p['contexts'] if c['component']=='credit_gross' and c['literal_context']['dataset']=='individual')
        row=dict({k:v for k,v in c['literal_context'].items() if k!='dataset'},CodInst='X',AnoMes='200912',Saldo='0')
        nextrow=dict(row,AnoMes='201003')
        a=dict(CodInst='X',Td='I',CodConglomeradoFinanceiro=None,CodConglomeradoPrudencial=None,CnpjInstituicaoLider=None,Atividade='old')
        cad={('X','200912'):a,('X','201003'):dict(a,Atividade='new')}
        ob=opening_observation(p,'credit','individual','X',[row],[nextrow],cad)
        self.assertEqual((ob['token'],ob['status']),('0','ok'))
        self.assertEqual(ob['flags'],['opening_cadastro_classification_change'])
        cad[('X','201003')]['CnpjInstituicaoLider']='different'
        self.assertEqual(opening_observation(p,'credit','individual','X',[row],[nextrow],cad)['status'],'opening_identity_changed')
        self.assertEqual(opening_observation(p,'credit','individual','X',[],[nextrow],cad)['status'],'opening_occurrence_missing_or_ambiguous')
        self.assertEqual(opening_observation(p,'LL','individual','X',[row],[nextrow],cad)['status'],'opening_not_released')

class UniverseSignatureTests(unittest.TestCase):
    def test_regression_detects_changed_diagnostic_exact_residual(self):
        from bank_quality.ifdata_universe_analysis import _economic_signature
        row=dict(period='202412',metric='Q1',horizon='point',status='ok',components={},diagnostics={'credit_identity':{'status':'exact','residual_fraction':{'numerator':'0','denominator':'1'},'inputs':[]}})
        altered=deepcopy(row);altered['diagnostics']['credit_identity']['residual_fraction']['numerator']='1'
        self.assertNotEqual(_economic_signature(row),_economic_signature(altered))



class UniverseReviewFixTests(unittest.TestCase):
    setUp=PackageTests.setUp
    digest=PackageTests.digest
    native_package=PackageTests.native_package
    fixtures=PackageTests.fixtures
    universe_fixture=UniverseTests.universe_fixture

    def control(self):
        from bank_quality import ifdata_universe_analysis as u
        self.u=u
        cfg=self.universe_fixture();out=self.root/'control'
        self.manifest=u.build(cfg,out,batch_size=2,stage='unit-calculations')
        self.rows={t:list(self.api._iter_json_array(out/(t+'.json'))) for t in u.TABLES}
        self.assertEqual(u.verify(out,self.digest(out/'manifest.json'))['tables']['results'],38)
        return out

    def rewritten(self,name,change):
        from contextlib import ExitStack
        import duckdb
        target=self.root/('mutation-'+name);target.mkdir();rows=deepcopy(self.rows);change(rows)
        with ExitStack() as stack,duckdb.connect() as con:
            writers={t:self.u.Writer(target,t,stack) for t in self.u.TABLES}
            for table in writers:
                for row in rows[table]:writers[table].append(row)
            files=[entry for writer in writers.values() for entry in writer.finish(con)]
        m=deepcopy(self.manifest);m['files']=files;m['tables']={t:len(rows[t]) for t in rows}
        (target/'manifest.json').write_text(json.dumps(m,ensure_ascii=False),encoding='utf-8')
        return target

    def test_review_quarter_and_compatibility_semantics_survive_signature(self):
        out=self.control()
        row=next(r for r in self.rows['results'] if r['metric']=='R1' and r['horizon']=='ttm' and r['code']=='I')
        row=self.u.resolve_result(out,self.digest(out/'manifest.json'),row['id'])
        for change in ('status','fraction','start','flags','compatible','predicate','mismatches'):
            altered=deepcopy(row);flow=altered['components']['LL'];q=flow['quarter_results'][0]
            if change=='status':q['status']='incompatible_definition'
            elif change=='fraction':q['value_fraction']['numerator']='999999'
            elif change=='start':q['start']='2023-01-01'
            elif change=='flags':q['flags'].append('changed_sign')
            elif change=='compatible':flow['compatibility'][0]['compatible']=False
            elif change=='predicate':flow['compatibility'][0]['predicate']='different'
            else:flow['compatibility'][0]['mismatches']=['definition_id']
            with self.subTest(change=change):self.assertFalse(self.u._economic_signature(row)==self.u._economic_signature(altered),'Semantic mutation was discarded')

    def test_review_binding_reference_requires_typed_component_period_and_identity(self):
        self.control();profile=self.u.load_profile()
        financial_at=next(c['context_sha256'] for c in profile['contexts'] if c['component']=='AT' and c['literal_context']['dataset']=='financial')
        individual_pl=next(c['context_sha256'] for c in profile['contexts'] if c['component']=='PL' and c['literal_context']['dataset']=='individual')
        cases={'perspective':('binding_ref',financial_at),'component':('binding_ref',individual_pl),
               'period':('period','200812'),'definition':('definition_id','other'),'window':('window_rule','other'),
               'unit_type':('unit_key',['individual','2','I'])}
        for name,(key,value) in cases.items():
            def change(rows,key=key,value=value):
                row=next(r for r in rows['components'] if r['dataset']=='individual' and r['code']=='I' and r['component']=='AT');row[key]=value
            out=self.rewritten(name,change)
            with self.subTest(name=name),self.assertRaises(ValueError):self.u.verify(out,self.digest(out/'manifest.json'))
        def compatibility(rows):
            r=next(r for r in rows['results'] if r['metric']=='R1' and r['horizon']=='ttm' and r['code']=='I')
            r['components']['AT']['compatibility'][0]['left']['bindings'][0]={'context_ref':financial_at}
        out=self.rewritten('compatibility_ref',compatibility)
        with self.assertRaises(ValueError):self.u.verify(out,self.digest(out/'manifest.json'))
        def full_binding(rows):
            r=next(r for r in rows['results'] if r['metric']=='R1' and r['horizon']=='ttm' and r['code']=='I')
            r['components']['AT']['compatibility'][0]['left']['bindings'][0]=deepcopy(next(c for c in profile['contexts'] if c['context_sha256']==financial_at))
        out=self.rewritten('compatibility_full_binding',full_binding)
        with self.assertRaises(ValueError):self.u.verify(out,self.digest(out/'manifest.json'))

    def test_review_source_overrides_and_component_reference_kinds_are_closed(self):
        self.control()
        def source_override(rows):
            row=next(r for r in rows['components'] if r['dataset']=='individual' and r['component']=='AT' and r['sources'])
            row['sources'][0]['TipoInstituicao']='2'
        out=self.rewritten('source_type_override',source_override)
        with self.subTest(case='source_type'),self.assertRaises(ValueError):self.u.verify(out,self.digest(out/'manifest.json'))
        def wrong_component(rows):
            r=next(r for r in rows['results'] if r['metric']=='C1' and r['code']=='I')
            pl=next(o for o in rows['components'] if o['code']=='I' and o['component']=='PL' and o['period']=='202412')
            r['components']['AT']['inputs'][0]={'component_ref':pl['id']}
        out=self.rewritten('component_kind',wrong_component)
        with self.subTest(case='component_kind'),self.assertRaises(ValueError):self.u.verify(out,self.digest(out/'manifest.json'))

    def test_review_duplicate_canonical_result_is_rejected_with_any_id(self):
        self.control()
        for different in (False,True):
            def change(rows):
                r=deepcopy(rows['results'][0])
                if different:r['id']+='|duplicate'
                rows['results'].insert(1,r)
            out=self.rewritten('duplicate'+str(different),change)
            with self.subTest(different_id=different),self.assertRaises(ValueError):self.u.verify(out,self.digest(out/'manifest.json'))

    def test_review_membership_requires_exact_source_proofs_in_both_directions(self):
        self.control()
        for case in ('all','sample','nominal','scope','membership','company','unit_and_links'):
            def change(rows):
                links=rows['membership_links']
                if case=='all':links.clear()
                elif case in ('sample','nominal'):
                    links.remove(next(r for r in links if (r['membership']=='sample')==(case=='sample')))
                elif case=='scope':links[0]['scope']='unproved'
                elif case=='membership':links[0]['membership']='unknown'
                elif case=='company':links[0]['company_id']='unproved'
                else:
                    unit=next(r for r in rows['unit_periods'] if r['membership']=='sample')
                    company=unit['companies'].pop();links[:]=[r for r in links if not (r['unit_id']==unit['unit_id'] and r['company_id']==company)]
            out=self.rewritten(case,change)
            with self.subTest(case=case),self.assertRaises(ValueError):self.u.verify(out,self.digest(out/'manifest.json'))

from fractions import Fraction


class UniverseAggregationTests(unittest.TestCase):
    def setUp(self):
        from bank_quality import ifdata_analysis as api
        self.api=api

    def row(self,code,n,d,membership='sample',**extra):
        f=self.api._fraction_field
        return dict(id=code,unit_id=code,unit_key=['financial','2',code],code=code,dataset='financial',
            period='202412',metric='C1',horizon='point',membership=membership,companies=['issuer-A'] if membership=='sample' else [],
            status='ok',applicability='applicable',numerator_fraction=f(Fraction(n)),denominator_fraction=f(Fraction(d)),
            value_fraction=f(Fraction(n,d)) if d else None,flags=[],asset_fraction=f(Fraction(d)),asset_status='ok',
            target_cadastro={'Data':'202412',**{k:None for k in ('Tcb','Td','Tc','Sr','Atividade','SegmentoTb')}},**extra)

    def reduce(self,rows):
        self.assertTrue(callable(getattr(self.api,'aggregate_unit_results',None)),'Missing native-unit aggregate API')
        return self.api.aggregate_unit_results(rows)

    def test_ratio_of_sums_unknown_reconciliation_and_nominal_companies(self):
        rows=[self.row('A',1,100),self.row('B',18,900,'remaining'),self.row('C',3,30,'unknown')]
        rows[0]['companies']=['issuer-A','issuer-B']
        missing=dict(rows[0],id='missing',unit_id=None,unit_key=None,code=None,companies=['issuer-C'],
            status='missing_native_unit',value_fraction=None,numerator_fraction=None,denominator_fraction=None,asset_fraction=None)
        out=self.reduce(rows+[missing]);a={r['cohort']:r for r in out['aggregates']}
        self.assertEqual(a['total']['numerator_fraction'],self.api._fraction_field(Fraction(22)))
        self.assertEqual(a['total']['denominator_fraction'],self.api._fraction_field(Fraction(1030)))
        self.assertEqual(a['total']['counts']['expected_units'],3)
        self.assertEqual(a['sample']['counts']['expected_companies'],3)
        self.assertEqual(a['sample']['lists']['missing_companies'],['issuer-C'])
        self.assertEqual(a['sample']['asset_coverage'].get('unknown_companies'),['issuer-C'])
        self.assertEqual(a['sample']['asset_coverage']['unknown_units'],[])
        self.assertEqual(a['sample']['asset_coverage']['status'],'partial_known_assets')
        self.assertIsNone(a['sample']['asset_coverage']['share_of_total_fraction'])
        self.assertEqual(a['total']['asset_coverage']['known_asset_fraction'],self.api._fraction_field(Fraction(1030)))
        two=self.reduce(rows[:2]);total=next(r for r in two['aggregates'] if r['cohort']=='total')
        self.assertEqual(total['value_fraction'],self.api._fraction_field(Fraction(19,1000)))
        self.assertNotEqual(total['value_fraction'],self.api._fraction_field(Fraction(15,1000)))
        self.assertTrue(all(r['reconciliation']['status']=='exact' for r in out['cohort_comparisons']))

    def test_signed_denominator_empty_and_duplicate_contributor_guard(self):
        rows=[self.row('A',1,10),self.row('B',2,-10,'unknown')]
        a=next(r for r in self.reduce(rows)['aggregates'] if r['cohort']=='total')
        self.assertEqual(a['status'],'zero_denominator');self.assertIn('non_convex_denominator_weights',a['flags'])
        empty=next(r for r in self.reduce(rows)['aggregates'] if r['cohort']=='remaining')
        self.assertEqual(empty['status'],'no_eligible_units')
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.reduce(rows+[deepcopy(rows[0])])
        rows[0]['value_fraction']=self.api._fraction_field(Fraction(999))
        with self.assertRaisesRegex(ValueError,'fraction'):self.reduce(rows)

    def test_nominal_unknown_and_native_limits_survive_without_proof_invention(self):
        row=self.row('A',1,100,limits=['native_accounting_question_only'])
        row.update(applicability='not_applicable')
        a=next(r for r in self.reduce([row])['aggregates'] if r['cohort']=='total')
        self.assertEqual(a['lists']['not_applicable_units'],[])
        self.assertEqual(a['lists']['unknown_units'],['A'])
        self.assertEqual(a['limits'],['native_accounting_question_only'])
        row['applicability_evidence']={'source':'dated proof'}
        a=next(r for r in self.reduce([row])['aggregates'] if r['cohort']=='total')
        self.assertEqual(a['lists']['not_applicable_units'],['A'])
        # Even distinct codes cannot collide under one opaque native unit ID.
        other=self.row('B',1,100);other['unit_id']='A'
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.reduce([row,other])

    def test_all_axes_typed_literal_categories_and_own_date(self):
        rows=[self.row(str(i),i+1,100,'remaining') for i in range(6)]
        for row,value in zip(rows,[None,'','historical',1,'1','conflict']):
            row['target_cadastro']={'Data':'202412',**{k:value for k in ('Tcb','Td','Tc','Sr','Atividade','SegmentoTb')}}
        rows[-1]['classification_states']={k:'conflict' for k in ('Tcb','Td','Tc','Sr','Atividade','SegmentoTb')}
        rows.append(dict(self.row('missing',1,100,'unknown'),target_cadastro={'Data':'202409','Sr':'current'}))
        out=self.reduce(rows)
        for field in ('Tcb','Td','Tc','Sr','Atividade','SegmentoTb'):
            segments=[r for r in out['segment_coverage'] if r['field']==field and r['cohort']=='total']
            self.assertEqual(len(segments),7)
            self.assertEqual({r['category_state'] for r in segments},{'null','empty','value','conflict','missing_dated_cadastro'})
            self.assertFalse(any(r['category']=='current' for r in segments))

    def test_distribution_type2_and_capital_does_not_borrow_assets(self):
        rows=[self.row(str(i),i,1,'unknown') for i in range(1,5)]
        for r in rows:r.update(dataset='capital',unit_key=['capital','1',r['code']],asset_fraction=None,asset_status='own_assets_unavailable')
        out=self.reduce(rows);d=next(r for r in out['distributions'] if r['cohort']=='total')
        self.assertEqual(d['median_fraction'],self.api._fraction_field(Fraction(5,2)))
        a=next(r for r in out['aggregates'] if r['cohort']=='total')
        self.assertIsNone(a['asset_coverage']['share_of_total_fraction'])
        self.assertEqual(a['overlap']['status'],'prudential_overlap_unproven')

    def test_aggregate_projection_compares_native_identity_not_only_equal_values(self):
        from bank_quality import ifdata_universe_analysis as u
        self.assertTrue(hasattr(u,'_aggregate_signature'),'Missing nominal aggregate signature')
        old=dict(period='202412',status='ok',numerator_fraction={'numerator':'1','denominator':'1'},
            denominator_fraction={'numerator':'100','denominator':'1'},value_fraction={'numerator':'1','denominator':'100'},
            counts={'eligible_units':1},lists={'eligible_units':[['financial','2','A']]},flags=[])
        new=dict(old,lists={'eligible_units':['financial|2|A|202412']})
        self.assertEqual(u._aggregate_signature(old),u._aggregate_signature(new))
        new['lists']={'eligible_units':['financial|2|B|202412']}
        self.assertNotEqual(u._aggregate_signature(old),u._aggregate_signature(new))
        new=dict(old,flags=['non_convex_denominator_weights'])
        self.assertNotEqual(u._aggregate_signature(old),u._aggregate_signature(new))


class UniverseFinalPackageTests(UniverseTests):
    def test_public_legacy_projection_compares_aggregates_segments_and_nominal_exclusions(self):
        cfg=self.universe_fixture();out=self.root/'final';self.api.build_universe_analysis(cfg,out)
        pop=json.loads((Path(cfg['population']['root'])/'manifest.json').read_text())
        old=dict(periods=['202412'],profile_expected_sha256=self.digest(self.api.PROFILE_PATH),
            inputs={k:v for k,v in pop['config']['inputs'].items() if k!='individual'})
        baseline=self.root/'legacy';self.api.build_analysis(old,baseline)
        report=self.api.compare_universe_analysis(out,self.digest(out/'manifest.json'),baseline,self.digest(baseline/'manifest.json'))
        self.assertIn('aggregate_projection',report)
        projection=report['aggregate_projection']
        self.assertEqual(projection['status'],'exact_on_identical_native_intersection')
        self.assertGreater(projection['aggregate_groups_compared'],0)
        self.assertGreater(projection['segment_groups_compared'],0)
        self.assertTrue(projection['excluded_nominal_relations'])
        # A coherently repinned legacy aggregate is still not allowed to
        # contradict the source company/unit projection.
        tables={t:list(self.api._iter_json_array(baseline/(t+'.json'))) for t in self.api.ANALYSIS_TABLES}
        next(r for r in tables['aggregates'] if r['block']=='principal')['numerator_fraction']={'numerator':'999','denominator':'1'}
        m=json.loads((baseline/'manifest.json').read_text());m['files']=self.api._write_tables(baseline,tables)
        (baseline/'manifest.json').write_text(json.dumps(m),encoding='utf-8')
        report=self.api.compare_universe_analysis(out,self.digest(out/'manifest.json'),baseline,self.digest(baseline/'manifest.json'))
        self.assertEqual(report['status'],'different')
        self.assertTrue(report['aggregate_projection']['differences'])

    def test_final_default_has_nine_tables_nominal_matrix_and_replay_payload(self):
        cfg=self.universe_fixture();a=self.root/'final-a';b=self.root/'final-b'
        m=self.api.build_universe_analysis(cfg,a,batch_size=1)
        self.assertEqual(m['stage'],'coverage-and-aggregation')
        self.assertEqual(len(m['tables']),9)
        n=self.api.build_universe_analysis(cfg,b,batch_size=3)
        self.assertEqual(m['logical_payload_sha256'],n['logical_payload_sha256'])
        self.assertNotEqual(m['producer']['started_utc'],n['producer']['started_utc'])
        self.assertEqual(m['producer']['source_sha256'],n['producer']['source_sha256'])
        for entry in m['files']:self.assertEqual((a/entry['file']).read_bytes(),(b/entry['file']).read_bytes())
        rows=json.loads((a/'aggregates.json').read_text())
        selected=[r for r in rows if r['cohort']=='sample']
        self.assertTrue(all(r['counts']['expected_companies']==24 for r in selected))
        self.assertTrue(any(r['counts']['missing_companies'] for r in selected))
        self.api.verify_universe_analysis(a,self.digest(a/'manifest.json'))
        unit=self.root/'unit';old=self.api.build_universe_analysis(cfg,unit,stage='unit-calculations')
        self.assertEqual(len(old['tables']),4)
        self.api.verify_universe_analysis(unit,self.digest(unit/'manifest.json'))

    def test_coherently_rewritten_derived_omission_and_fraction_are_rejected(self):
        from bank_quality.ifdata_universe_analysis import Writer
        from contextlib import ExitStack
        import duckdb
        cfg=self.universe_fixture();out=self.root/'final';m=self.api.build_universe_analysis(cfg,out)
        self.assertEqual(m['stage'],'coverage-and-aggregation')
        originals={table:list(self.api._iter_json_array(out/(table+'.json'))) for table in ('aggregates','unit_coverage','cohort_comparisons')}
        for table,case in [('aggregates','omission'),('aggregates','fraction'),('unit_coverage','reference'),('cohort_comparisons','reference')]:
            rows=deepcopy(originals[table])
            if case=='omission':rows.pop()
            elif case=='fraction':rows[0]['numerator_fraction']={'numerator':'999','denominator':'1'}
            elif table=='unit_coverage':rows[0]['result_id']='unproved'
            else:rows[0]['left_aggregate_id']='unproved'
            with ExitStack() as stack,duckdb.connect() as con:
                writer=Writer(out,table,stack)
                for row in rows:writer.append(row)
                files=writer.finish(con)
            altered=deepcopy(m);altered['tables'][table]=len(rows)
            altered['files']=[e for e in m['files'] if not e['file'].startswith(table+'.')]+files
            from bank_quality.ifdata_universe_analysis import logical_payload_sha256
            altered['logical_payload_sha256']=logical_payload_sha256(altered)
            (out/'manifest.json').write_text(json.dumps(altered),encoding='utf-8')
            with self.subTest(table=table,case=case),self.assertRaisesRegex(ValueError,'Derived'):
                self.api.verify_universe_analysis(out,self.digest(out/'manifest.json'))
            with ExitStack() as stack,duckdb.connect() as con:
                writer=Writer(out,table,stack)
                for row in originals[table]:writer.append(row)
                writer.finish(con)

    def test_changed_producer_source_cannot_receive_manifest(self):
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();out=self.root/'changed'
        self.assertTrue(hasattr(u,'_check_producer'),'Missing automatic source stability guard')
        # The real checker checks raw bytes; a temporary file proves causality
        # without touching a shared production module during the test.
        source=self.root/'producer.py';source.write_text('first')
        stamp={'source_sha256':{str(source):self.digest(source)}}
        u._check_producer(stamp);source.write_text('changed')
        with self.assertRaisesRegex(ValueError,'Producer source'):u._check_producer(stamp)
        with patch.object(u,'_check_producer',side_effect=ValueError('Producer source changed')):
            with self.assertRaisesRegex(ValueError,'Producer source'):self.api.build_universe_analysis(cfg,out)
        self.assertFalse((out/'manifest.json').exists())


# Reuse only setup/build-fixture helpers; do not repeat the inherited suites.
for _name in dir(UniverseTests):
    if _name.startswith('test_') and _name not in UniverseFinalPackageTests.__dict__:
        setattr(UniverseFinalPackageTests,_name,None)


class UniversePersistenceLineageTests(unittest.TestCase):
    setUp=PackageTests.setUp
    digest=PackageTests.digest
    native_package=PackageTests.native_package
    fixtures=PackageTests.fixtures
    universe_fixture=UniverseTests.universe_fixture

    def test_derived_build_persists_wide_rows_losslessly_with_reader_budget(self):
        """Synthetic writer resource fixture; no financial population expansion."""
        import io
        import duckdb
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();out=self.root/'wide-derived'
        def row(index):
            return dict(id=str(index),period='202412',metric=None if index%3==0 else '',
                horizon='point',dataset='financial',code=str(index),status='ok',
                text='á"x\r\n'+str(index)+'z'*(280000 if index%3==0 else 20000))
        def windows(*args):
            yield {'aggregates':(row(index) for index in range(6240))}
        with patch.object(u,'_derived_windows',windows):
            manifest=u.build(cfg,out)
        self.assertEqual(manifest['tables']['aggregates'],6240)
        digest=hashlib.sha256();buffer=io.StringIO(newline='')
        csv_writer=csv.writer(buffer,quoting=csv.QUOTE_NOTNULL)
        csv_writer.writerow(self.api.TABLE_COLUMNS)
        with duckdb.connect(config={'memory_limit':'512MiB','threads':1}) as con:
            cursor=con.execute('select * from read_parquet(?)',[str(out/'aggregates.parquet')])
            count=0
            for batch in iter(lambda:cursor.fetchmany(16),[]):
                for actual in batch:
                    expected=row(count)
                    self.assertEqual(actual,tuple(expected.get(k) for k in self.api.TABLE_COLUMNS[:-1])+(u.canonical(expected),))
                    csv_writer.writerow(actual);count+=1
                digest.update(buffer.getvalue().encode('utf-8'));buffer.seek(0);buffer.truncate(0)
            self.assertEqual(count,6240)
            self.assertEqual(con.execute('select count(distinct id) from read_parquet(?)',[str(out/'aggregates.parquet')]).fetchone()[0],6240)
        self.assertEqual(digest.hexdigest(),self.digest(out/'aggregates.csv'))
        iterator=self.api._iter_json_array(out/'aggregates.json')
        try:self.assertEqual(next(iterator),row(0))
        finally:iterator.close()

    def test_comparator_accepts_only_anchored_exact_line_endings_and_raw_pins_stay_strict(self):
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();out=self.root/'universe';u.build(cfg,out)
        pop=json.loads((Path(cfg['population']['root'])/'manifest.json').read_text())
        old=dict(periods=['202412'],inputs={k:v for k,v in pop['config']['inputs'].items() if k!='individual'})
        raw=self.api.PROFILE_PATH.read_bytes();lf=raw.replace(b'\r\n',b'\n');crlf=lf.replace(b'\n',b'\r\n')
        installed=self.root/'legacy-profile.json'
        for name,content in [('lf',lf),('crlf',crlf)]:
            with self.subTest(ending=name),patch.object(self.api,'PROFILE_PATH',installed):
                installed.write_bytes(content);pin=self.digest(installed)
                self.api.load_profile(pin)
                with self.assertRaisesRegex(ValueError,'Profile hash mismatch'):
                    self.api.load_profile(hashlib.sha256(crlf if name=='lf' else lf).hexdigest())
                old['profile_expected_sha256']=pin;baseline=self.root/name
                self.api.build_analysis(old,baseline)
                report=u.compare(out,self.digest(out/'manifest.json'),baseline,self.digest(baseline/'manifest.json'))
                self.assertEqual(report['matched'],14);self.assertEqual(report['differences'],[])
        baseline=self.root/'lf';bm=json.loads((baseline/'manifest.json').read_text())
        unreviewed=deepcopy(u.load_profile());unreviewed['legacy_profile_sha256']='0'*64
        with patch.object(u,'load_profile',return_value=unreviewed):
            with self.assertRaisesRegex(ValueError,'reviewed lineage'):
                u.compare(out,self.digest(out/'manifest.json'),baseline,self.digest(baseline/'manifest.json'))
        with patch.object(self.api,'PROFILE_PATH',installed):
            installed.write_bytes(lf+b' ')
            with self.assertRaisesRegex(ValueError,'reviewed lineage'):
                u.compare(out,self.digest(out/'manifest.json'),baseline,self.digest(baseline/'manifest.json'))
        bad=deepcopy(bm);bad['inputs']['financial']['expected_manifest_sha256']='0'*64
        (baseline/'manifest.json').write_text(json.dumps(bad),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Baseline native source pins differ'):
            u.compare(out,self.digest(out/'manifest.json'),baseline,self.digest(baseline/'manifest.json'))
        for rejected in ('0'*64,hashlib.sha256(lf+b' ').hexdigest()):
            bm['profile_sha256']=rejected
            (baseline/'manifest.json').write_text(json.dumps(bm),encoding='utf-8')
            with self.subTest(baseline_pin=rejected),self.assertRaisesRegex(ValueError,'reviewed lineage'):
                u.compare(out,self.digest(out/'manifest.json'),baseline,self.digest(baseline/'manifest.json'))
        universe_raw=u.PROFILE_PATH.read_bytes();universe_lf=universe_raw.replace(b'\r\n',b'\n')
        universe_crlf=universe_lf.replace(b'\n',b'\r\n');installed=self.root/'universe-profile.json'
        with patch.object(u,'PROFILE_PATH',installed):
            for content,other in ((universe_lf,universe_crlf),(universe_crlf,universe_lf)):
                installed.write_bytes(content);u.load_profile(expected_sha256=self.digest(installed))
                with self.assertRaisesRegex(ValueError,'Universe profile hash mismatch'):
                    u.load_profile(expected_sha256=hashlib.sha256(other).hexdigest())


if __name__ == '__main__':
    unittest.main()

class UniverseBoundedQueryTests(unittest.TestCase):
    setUp=PackageTests.setUp
    digest=PackageTests.digest
    native_package=PackageTests.native_package
    fixtures=PackageTests.fixtures
    universe_fixture=UniverseTests.universe_fixture

    def test_query_authenticates_only_selected_payload_and_does_not_reverify_finances(self):
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        out=self.root/'query';m=u.build(self.universe_fixture(),out)
        pin=self.digest(out/'manifest.json')
        # An unused payload can be unavailable without making selected rows
        # claim global integrity. The finite inventory must still be present.
        (out/'components.parquet').write_bytes(b'unavailable')
        with patch.object(u,'verify',side_effect=AssertionError('full verification repeated')),patch.object(u,'_capture_payload',wraps=u._capture_payload) as capture:
            rows=u.query(out,pin,'with x as (select id from results) select count(*) as n from x')
            self.assertEqual(rows,[{'n':m['tables']['results']}])
            self.assertEqual([c.args[1]['file'] for c in capture.call_args_list],['results.parquet'])
            self.assertEqual(u.query(out,pin,'select count(*) as n from RESULTS'),rows)
            capture.reset_mock()
            self.assertEqual(u.query(out,pin,'select 1 as n'),[{'n':1}])
            capture.assert_not_called()

    def test_query_uses_captured_bytes_after_source_replacement(self):
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        out=self.root/'query';m=u.build(self.universe_fixture(),out);pin=self.digest(out/'manifest.json')
        capture=u._capture_payload
        def replace(root,entry,destination=None):
            value=capture(root,entry,destination)
            (root/entry['file']).write_bytes(b'untrusted replacement after authentication')
            return value
        with patch.object(u,'_capture_payload',side_effect=replace):
            self.assertEqual(u.query(out,pin,'select count(*) as n from results'),[{'n':m['tables']['results']}])
        with self.assertRaisesRegex(ValueError,'hash'):u.query(out,pin,'select id from results')

    def test_source_change_during_capture_is_rejected_even_with_preserved_stat(self):
        import os
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        path=self.root/'capture.parquet';path.write_bytes(b'a'*(2*1024*1024))
        entry=dict(file=path.name,sha256=self.digest(path));before=path.stat();real=hashlib.sha256
        class ChangingDigest:
            def __init__(self):self.digest=real();self.changed=False
            def update(self,block):
                self.digest.update(block)
                if not self.changed:
                    self.changed=True
                    with path.open('r+b') as f:f.seek(-1,2);f.write(b'b')
                    os.utime(path,ns=(before.st_atime_ns,before.st_mtime_ns))
            def hexdigest(self):return self.digest.hexdigest()
        with patch.object(u.hashlib,'sha256',ChangingDigest),self.assertRaisesRegex(ValueError,'hash'):
            u._capture_payload(self.root,entry,self.root/'captured.parquet')

    def test_invalid_sql_is_rejected_before_snapshot_preparation(self):
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        for sql in ('select from','select 1; select 2','drop table results','select * from forbidden',"select * from read_csv('external.csv')"):
            with self.subTest(sql=sql),patch.object(u,'_snapshot_manifest',side_effect=AssertionError('snapshot prepared')):
                with self.assertRaises(Exception) as error:u.query(self.root,'0'*64,sql)
                self.assertNotIsInstance(error.exception,AssertionError)

    def test_query_rejects_tampering_preserving_stat_and_invalid_or_external_sql(self):
        import os
        from bank_quality import ifdata_universe_analysis as u
        out=self.root/'query';u.build(self.universe_fixture(),out);pin=self.digest(out/'manifest.json')
        path=out/'results.parquet';before=path.stat();raw=path.read_bytes()
        path.write_bytes(raw[:-1]+bytes([raw[-1]^1]));os.utime(path,ns=(before.st_atime_ns,before.st_mtime_ns))
        with self.assertRaisesRegex(ValueError,'hash'):u.query(out,pin,'select id from results')
        path.write_bytes(raw)
        for sql in ('select 1; select 2','delete from results','select from','select * from forbidden',
                    "select * from read_csv('untrusted.csv')",'select * from range(10001)'):
            with self.subTest(sql=sql),self.assertRaises(Exception):u.query(out,pin,sql)


class UniverseLogicalReplayTests(unittest.TestCase):
    setUp=PackageTests.setUp
    digest=PackageTests.digest
    native_package=PackageTests.native_package
    fixtures=PackageTests.fixtures
    universe_fixture=UniverseTests.universe_fixture

    def test_cli_routes_bounded_replay_arguments_to_existing_api(self):
        import io
        from contextlib import redirect_stdout
        from unittest.mock import patch
        script=Path(self.api.__file__).resolve().parent.parent/'scripts/analyze-ifdata.py'
        spec=importlib.util.spec_from_file_location('bounded_replay_cli',script)
        cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
        argv=[str(script),'compare-universe-replay','--output','main','--expected-manifest-sha256','a'*64,
              '--replay-unit-checkpoint','replay','--expected-replay-manifest-sha256','b'*64,'--derived-source-root','original']
        with patch('sys.argv',argv),patch.object(cli,'compare_universe_replay',return_value={'status':'equal'}) as compare,redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(),0)
        compare.assert_called_once_with('main','a'*64,'replay','b'*64,'original')

    def replay_fixture(self):
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();main=self.root/'main-source';replay=self.root/'replay-source'
        # Both originals execute calculations and derived CSV writing. Admission
        # does not regenerate them and incomplete Parquet/JSON are not consumed.
        u.build(cfg,main);u.build(cfg,replay)
        outputs=[]
        for index,source in enumerate((main,replay)):
            (source/'manifest.json').unlink()
            paths,pre,end,save=UniverseCheckpointTests.receipt_fixture(self,cfg,source)
            pre['pid']+=index;end['pid']=pre['pid']
            paths['preflight'].write_text(json.dumps(pre),encoding='utf-8')
            paths['terminal'].write_text(json.dumps(end),encoding='utf-8')
            evidence,pin=save();out=self.root/('checkpoint-'+str(index))
            u.admit_universe_unit_checkpoint(cfg,source,out,evidence=evidence,expected_evidence_sha256=pin)
            outputs.append(out)
        final=self.root/'final';u.finalize_universe_analysis(outputs[0],self.digest(outputs[0]/'manifest.json'),final)
        (replay/'aggregates.json').write_bytes(b'[invalid-prefix')
        (replay/'aggregates.parquet').write_bytes(b'invalid-prefix')
        return final,outputs[1],replay

    def test_logical_replay_compares_twelve_unit_payloads_and_five_original_csvs(self):
        from bank_quality import ifdata_universe_analysis as u
        self.assertTrue(callable(getattr(self.api,'compare_universe_replay',None)),'Missing logical replay API')
        final,replay,source=self.replay_fixture()
        report=self.api.compare_universe_replay(final,self.digest(final/'manifest.json'),replay,self.digest(replay/'manifest.json'),source)
        self.assertEqual(report['status'],'equal')
        self.assertEqual(len(report['unit_physical_payloads']),12)
        self.assertEqual(len(report['derived_csv_logical_tables']),5)
        self.assertEqual(report['main_full_semantic_validation'],'required_separate_gate')
        self.assertFalse(report['financial_acceptance'])
        self.assertNotEqual(report['original_calculations']['main']['source_root'],report['original_calculations']['replay']['source_root'])

    def test_logical_replay_rejects_tampered_csv_units_config_and_original_reuse(self):
        from bank_quality import ifdata_universe_analysis as u
        self.assertTrue(callable(getattr(u,'compare_replay',None)),'Missing bounded replay comparison')
        final,replay,source=self.replay_fixture();a=self.digest(final/'manifest.json');b=self.digest(replay/'manifest.json')
        for path in (source/'aggregates.csv',replay/'results.parquet'):
            raw=path.read_bytes();path.write_bytes(raw+b' ')
            with self.subTest(path=path.name),self.assertRaisesRegex(ValueError,'hash'):
                u.compare_replay(final,a,replay,b,source)
            path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError,'source root'):u.compare_replay(final,a,replay,b,self.root/'unrelated')
        original=json.loads((replay/'manifest.json').read_bytes())
        changed=deepcopy(original);changed['config']['datasets']=['financial'];changed['logical_payload_sha256']=u.logical_payload_sha256(changed)
        (replay/'manifest.json').write_text(json.dumps(changed),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'configuration'):u.compare_replay(final,a,replay,self.digest(replay/'manifest.json'),source)
        reused=deepcopy(original);m=json.loads((final/'manifest.json').read_bytes());reused['calculation_producer']=m['calculation_producer']
        reused['unit_checkpoint']=m['unit_checkpoint']['provenance']
        (replay/'manifest.json').write_text(json.dumps(reused),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'original calculation'):u.compare_replay(final,a,replay,self.digest(replay/'manifest.json'),Path(reused['unit_checkpoint']['source_root']))


class UniverseCheckpointTests(unittest.TestCase):
    setUp=PackageTests.setUp
    digest=PackageTests.digest
    native_package=PackageTests.native_package
    fixtures=PackageTests.fixtures
    universe_fixture=UniverseTests.universe_fixture

    def test_stage_finalization_matches_full_payloads_and_preserves_units(self):
        from bank_quality import ifdata_universe_analysis as u
        self.assertTrue(hasattr(self.api,'finalize_universe_analysis'),'Missing public checkpoint finalizer')
        cfg=self.universe_fixture();unit=self.root/'unit';full=self.root/'full';final=self.root/'final'
        original=u.build(cfg,unit,batch_size=1,stage='unit-calculations')
        before={p.name:self.digest(p) for p in unit.iterdir()}
        expected=u.build(cfg,full,batch_size=3)
        actual=self.api.finalize_universe_analysis(unit,self.digest(unit/'manifest.json'),final)
        self.assertEqual(actual['logical_payload_sha256'],expected['logical_payload_sha256'])
        self.assertEqual(len(list(final.iterdir())),28)
        self.assertEqual(actual['calculation_producer'],original['producer'])
        self.assertEqual(actual['producer']['operation'],'finalize_universe_analysis')
        for entry in expected['files']:self.assertEqual(self.digest(full/entry['file']),self.digest(final/entry['file']))
        self.assertEqual(before,{p.name:self.digest(p) for p in unit.iterdir()})
        for entry in original['files']:self.assertTrue((unit/entry['file']).samefile(final/entry['file']))
        u.verify(final,self.digest(final/'manifest.json'))

    def receipt_fixture(self,cfg,source):
        import platform,sys,duckdb
        from bank_quality import ifdata_universe_analysis as u
        caller=self.root/'original-caller.py';caller.write_bytes(b'# original public build caller\n')
        config=self.root/'original-config.json';config.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        _,pop=self.api._authenticate(cfg['population'])
        inputpins={str(Path(e['root'])/'manifest.json'):e['expected_manifest_sha256'] for e in dict(pop['config']['inputs'],population=cfg['population'],**({'opening':cfg['opening']} if 'opening' in cfg else {})).values()}
        snapshots=u._producer_snapshot(cfg,'coverage-and-aggregation',2)['source_sha256']
        snapshots[str(Path(__file__).resolve())]=self.digest(Path(__file__))
        pre=dict(status='running',mode='buildverify',output=str(source),pid=123,head='a'*40,started_utc='2026-10-15T12:00:00+00:00',batch_size=2,
            source_before=snapshots,input_manifest_before=inputpins,config=str(config),config_sha256=self.digest(config),wrapper_sha256=self.digest(caller),
            process_created_utc='2026-10-15T11:59:59+00:00',actual_executable=sys.executable,
            process_command_line=f'"{sys.executable}" "{caller}" buildverify run3 2 --expected-head '+ 'a'*40,
            runtime=dict(python=platform.python_version(),executable=sys.executable,duckdb=duckdb.__version__,platform=platform.platform()))
        terminal=dict(pre,status='failed',error='in build\nwriter.finish(con)\nin finish\n_duckdb.OutOfMemoryException: Out of Memory Error',
            finished_utc='2026-10-15T12:01:00+00:00',source_after=snapshots,input_manifest_after=inputpins,
            config_sha256_after=self.digest(config),head_after=pre['head'],primary_status_after='',source_stable=True,input_manifests_stable=True)
        paths=dict(config=config,caller=caller)
        for name,value in [('preflight',pre),('terminal',terminal)]:
            paths[name]=self.root/(name+'.json');paths[name].write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
        descriptor=self.root/'evidence.json'
        def save():
            descriptor.write_text(json.dumps(dict(contract='ifdata-unit-checkpoint-evidence-v1',**{n:dict(path=str(p),sha256=self.digest(p)) for n,p in paths.items()})),encoding='utf-8')
            return descriptor,self.digest(descriptor)
        save()
        return paths,pre,terminal,save

    def test_admission_authenticates_original_receipts_and_captures_current_hashes(self):
        from bank_quality import ifdata_universe_analysis as u
        self.assertTrue(hasattr(u,'admit_universe_unit_checkpoint'),'Missing public checkpoint admission')
        cfg=self.universe_fixture();source=self.root/'failed';old=u.build(cfg,source,stage='unit-calculations')
        (source/'manifest.json').unlink()
        (source/'aggregates.json').write_text('[incomplete',encoding='utf-8')
        before={p.name:self.digest(p) for p in source.iterdir()}
        paths,pre,terminal,save=self.receipt_fixture(cfg,source);evidence,pin=save()
        output=self.root/'admitted'
        admitted=self.api.admit_universe_unit_checkpoint(cfg,source,output,evidence=evidence,expected_evidence_sha256=pin)
        self.assertEqual(admitted['files'],old['files'])
        self.assertEqual(len(list(output.iterdir())),13)
        self.assertEqual(admitted['calculation_producer']['evidence_kind'],'caller_preflight_and_failed_terminal_receipt')
        self.assertEqual(admitted['unit_checkpoint']['capture_timing'],'captured_at_checkpoint_admission')
        self.assertEqual(admitted['producer']['operation'],'admit_universe_unit_checkpoint')
        self.assertEqual(admitted['unit_checkpoint']['evidence']['config']['raw_utf8'],paths['config'].read_bytes().decode('utf-8'))
        self.assertNotEqual(admitted['producer']['config_sha256'],self.digest(paths['config']))
        u.verify(output,self.digest(output/'manifest.json'))
        final=u.finalize_universe_analysis(output,self.digest(output/'manifest.json'),self.root/'final')
        self.assertEqual(final['calculation_producer'],admitted['calculation_producer'])
        self.assertEqual(before,{p.name:self.digest(p) for p in source.iterdir()})

    def test_admission_rejects_receipt_pin_and_identity_disagreements(self):
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();source=self.root/'failed';u.build(cfg,source,stage='unit-calculations');(source/'manifest.json').unlink()
        paths,pre,end,save=self.receipt_fixture(cfg,source)
        mutations=[('status','pass'),('pid',999),('config_sha256_after','0'*64),('wrapper_sha256','0'*64),
            ('head_after','b'*40),('source_stable',False),('source_after',{}),('input_manifest_after',{}),
            ('runtime',dict(pre['runtime'],duckdb='unknown')),('output',str(self.root/'other')),('error','early source failure')]
        for index,(field,value) in enumerate(mutations):
            with self.subTest(field=field):
                bad=dict(end,**{field:value});paths['terminal'].write_text(json.dumps(bad),encoding='utf-8');evidence,pin=save()
                output=self.root/('bad-'+str(index))
                with self.assertRaises(ValueError):u.admit_universe_unit_checkpoint(cfg,source,output,evidence=evidence,expected_evidence_sha256=pin)
                self.assertFalse((output/'manifest.json').exists())
        paths['terminal'].write_text(json.dumps(end),encoding='utf-8');evidence,pin=save()
        for field in ('source_before','input_manifest_before','runtime'):
            bad=deepcopy(pre);terminal=deepcopy(end)
            if field=='source_before':
                key=next(k for k in bad[field] if k.endswith(u.PROFILE_PATH.name));bad[field][key]='0'*64;terminal['source_after']=bad[field]
            elif field=='input_manifest_before':
                key=next(iter(bad[field]));bad[field][key]='0'*64;terminal['input_manifest_after']=bad[field]
            else:bad[field]['duckdb']='unknown'
            terminal[field]=bad[field]
            paths['preflight'].write_text(json.dumps(bad),encoding='utf-8');paths['terminal'].write_text(json.dumps(terminal),encoding='utf-8');evidence,pin=save()
            with self.subTest(coherent=field),self.assertRaises(ValueError):u.admit_universe_unit_checkpoint(cfg,source,self.root/('coherent-'+field),evidence=evidence,expected_evidence_sha256=pin)
        with self.assertRaises(ValueError):u.admit_universe_unit_checkpoint(cfg,source,self.root/'badpin',evidence=evidence,expected_evidence_sha256='0'*64)

    def test_finalization_failures_leave_sources_unchanged_without_acceptance(self):
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();source=self.root/'unit';u.build(cfg,source,stage='unit-calculations')
        pin=self.digest(source/'manifest.json');before={p.name:self.digest(p) for p in source.iterdir()}
        for label,context in [('link',patch('os.link',side_effect=OSError('cross device'))),('writer',patch.object(u,'_finish_derived',side_effect=RuntimeError('injected writer failure')))]:
            output=self.root/label
            with context,self.assertRaises((OSError,RuntimeError)):u.finalize_universe_analysis(source,pin,output)
            self.assertFalse((output/'manifest.json').exists())
            self.assertEqual(before,{p.name:self.digest(p) for p in source.iterdir()})
        for output in (source,source/'nested',self.root):
            with self.assertRaises((ValueError,FileExistsError)):u.finalize_universe_analysis(source,pin,output)
        existing=self.root/'existing';existing.mkdir()
        with self.assertRaises(FileExistsError):u.finalize_universe_analysis(source,pin,existing)
        output=self.root/'mutated';original=u._finish_derived
        def mutate(*args):
            original(*args)
            with (source/'components.json').open('ab') as f:f.write(b' ')
        with patch.object(u,'_finish_derived',side_effect=mutate),self.assertRaises(ValueError):u.finalize_universe_analysis(source,pin,output)
        self.assertFalse((output/'manifest.json').exists())

    def test_admission_uses_complete_existing_verifier_and_never_repairs_prefixes(self):
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();source=self.root/'failed';u.build(cfg,source,stage='unit-calculations');(source/'manifest.json').unlink()
        paths,pre,end,save=self.receipt_fixture(cfg,source);evidence,pin=save()
        original=(source/'results.json').read_bytes()
        for index,content in enumerate((original[:-10],b'[]',original.replace(b'component_ref',b'nonexistent_ref'))):
            (source/'results.json').write_bytes(content);output=self.root/('invalid-'+str(index))
            with self.assertRaises((ValueError,json.JSONDecodeError)):u.admit_universe_unit_checkpoint(cfg,source,output,evidence=evidence,expected_evidence_sha256=pin)
            self.assertFalse((output/'manifest.json').exists())
        (source/'results.json').write_bytes(original)
        (source/'unexpected.json').write_bytes(b'[]')
        with self.assertRaises(ValueError):u.admit_universe_unit_checkpoint(cfg,source,self.root/'extra',evidence=evidence,expected_evidence_sha256=pin)

    def test_finalizer_rejects_unit_without_original_producer_or_logical_pin(self):
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();source=self.root/'unit';m=u.build(cfg,source,stage='unit-calculations')
        for index,key in enumerate(('producer','logical_payload_sha256')):
            bad=deepcopy(m);bad.pop(key)
            (source/'manifest.json').write_text(json.dumps(bad),encoding='utf-8')
            output=self.root/('missing-'+str(index))
            with self.assertRaisesRegex(ValueError,'Checkpoint producer/logical'):
                u.finalize_universe_analysis(source,self.digest(source/'manifest.json'),output)
            self.assertFalse((output/'manifest.json').exists())

    def test_writer_owns_only_derived_files_and_source_changes_block_acceptance(self):
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();source=self.root/'unit';u.build(cfg,source,stage='unit-calculations');pin=self.digest(source/'manifest.json')
        before={p.name:self.digest(p) for p in source.iterdir()};written=[];writer=u.Writer
        class ObservedWriter(writer):
            def __init__(self,output,table,stack):
                written.append(table);super().__init__(output,table,stack)
        with patch.object(u,'Writer',ObservedWriter):u.finalize_universe_analysis(source,pin,self.root/'good')
        self.assertEqual(written,['unit_coverage','aggregates','distributions','segment_coverage','cohort_comparisons'])
        state={'changed':False};digest=u.math._digest_file;finish=u._finish_derived
        def changed(path):
            if state['changed'] and Path(path).resolve()==Path(u.__file__).resolve():return '0'*64
            return digest(path)
        def complete(*args):finish(*args);state['changed']=True
        output=self.root/'source-changed'
        with patch.object(u.math,'_digest_file',side_effect=changed),patch.object(u,'_finish_derived',side_effect=complete),self.assertRaisesRegex(ValueError,'Producer source changed'):
            u.finalize_universe_analysis(source,pin,output)
        self.assertFalse((output/'manifest.json').exists())
        self.assertEqual(before,{p.name:self.digest(p) for p in source.iterdir()})

    def test_checkpoint_symlink_roots_or_unit_entries_are_rejected(self):
        import os
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();source=self.root/'unit';u.build(cfg,source,stage='unit-calculations');pin=self.digest(source/'manifest.json')
        alias=self.root/'alias'
        try:os.symlink(source,alias,target_is_directory=True)
        except OSError as error:self.skipTest('Native symlink privilege unavailable: '+str(error))
        with self.assertRaisesRegex(ValueError,'redirects'):u.finalize_universe_analysis(alias,pin,self.root/'final')
        redirected=self.root/'external-components.json';(source/'components.json').rename(redirected);os.symlink(redirected,source/'components.json')
        with self.assertRaises(ValueError):u.finalize_universe_analysis(source,pin,self.root/'final2')
        self.assertFalse((self.root/'final2/manifest.json').exists())

    def test_source_change_during_initial_verification_blocks_final_manifest(self):
        from unittest.mock import patch
        from bank_quality import ifdata_universe_analysis as u
        cfg=self.universe_fixture();source=self.root/'unit';u.build(cfg,source,stage='unit-calculations')
        pin=self.digest(source/'manifest.json');before={p.name:self.digest(p) for p in source.iterdir()}
        state={'changed':False};digest=u.math._digest_file;verify=u.verify
        def changed(path):
            if state['changed'] and Path(path).resolve()==Path(u.__file__).resolve():return '0'*64
            return digest(path)
        def verification(*args):
            state['changed']=True
            return verify(*args)
        output=self.root/'during-verify'
        with patch.object(u.math,'_digest_file',side_effect=changed),patch.object(u,'verify',side_effect=verification),self.assertRaisesRegex(ValueError,'Producer source changed'):
            u.finalize_universe_analysis(source,pin,output)
        self.assertFalse((output/'manifest.json').exists())
        self.assertEqual(before,{p.name:self.digest(p) for p in source.iterdir()})

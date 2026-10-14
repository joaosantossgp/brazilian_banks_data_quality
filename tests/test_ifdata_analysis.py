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
        self.assertEqual(manifest['stage'],'bindings-and-calculations')
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


if __name__ == '__main__':
    unittest.main()

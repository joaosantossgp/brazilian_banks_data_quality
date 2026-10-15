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
        self.assertEqual(ma['stage'],'unit-calculations')
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


if __name__ == '__main__':
    unittest.main()

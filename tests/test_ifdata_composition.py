"""Stored contributions compose exactly; company links never duplicate units."""
from contextlib import ExitStack
from copy import deepcopy
from pathlib import Path
from fractions import Fraction
import csv
import json
import tempfile
import unittest

from bank_quality import ifdata_analysis as math
from bank_quality import ifdata_universe_analysis as u


class CompositionTests(unittest.TestCase):
    def package(self,path,manifest,tables):
        import duckdb
        path.mkdir();files=[]
        with ExitStack() as stack,duckdb.connect() as conn:
            for name,rows in tables.items():
                writer=u.Writer(path,name,stack)
                for row in rows:writer.append(row)
                files.extend(writer.finish(conn))
        manifest=dict(manifest,files=files,tables={k:len(v) for k,v in tables.items()})
        (path/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        return dict(root=str(path),expected_manifest_sha256=math._digest_file(path/'manifest.json'))

    def fixture(self,root,period='202412',missing_cadastro=False,sr_status=None):
        p=period;units=[];stocks=[];coverage=[];F=math._fraction_field
        for ds,code,member in [('financial','A','remaining'),('financial','B','unknown'),('capital','P','remaining')]:
            cad=dict(Sr=None,Tcb='B1',Td='I',Tc=None,SegmentoTb=None)
            if missing_cadastro and code=='A':cad=None
            uid='|'.join((ds,u.TYPES[ds],code,p))
            unit=dict(id=uid,unit_id=uid,dataset=ds,code=code,period=p,membership=member,companies=[],classifications=cad,
                      own_cadastro=dict(CodInst=code,Data=p,NomeInstituicao=code) if cad is not None else None)
            units.append(unit)
            for metric in math.METRICS:
                if (metric in ('C3','C4'))!=(ds=='capital'):continue
                for h in (('quarter','ttm') if metric in math.FLOW_METRICS else ('point',)):
                    rid=uid+'|'+metric+'|'+h
                    coverage.append(dict(id=rid+'|coverage',result_id=rid,row_kind='native_unit',unit_id=uid,unit_key=[ds,u.TYPES[ds],code],
                        dataset=ds,code=code,period=p,metric=metric,horizon=h,membership=member,companies=[],status='ok',applicability='applicable',
                        value_fraction=F(Fraction(1,2)),numerator_fraction=F(1),denominator_fraction=F(2),flags=[],limits=['native'],annual_summary=True,
                        target_cadastro=dict(Data=p,**cad) if cad is not None else None,asset_fraction=None if ds=='capital' else F(100),asset_status='own_assets_unavailable' if ds=='capital' else 'ok'))
            if ds!='capital':
                for role,token in [('AT','100'),('credit','-20' if code=='B' else '40'),('PL',None if code=='B' else '10')]:
                    stocks.append(dict(id=uid+'|'+role,component=role,dataset=ds,code=code,period=p,analysis_period=p,token=token,
                        unit_key=[ds,u.TYPES[ds],code],definition_id=role,scale='BRL',window_rule='stock',status='ok',binding_ref='ctx',sources=[{'source_file':'native'}]))
        base=self.package(root/'base',dict(contract=u.CONTRACT,stage='coverage-and-aggregation',periods=[p]),
                          dict(unit_periods=units,unit_coverage=coverage,components=stocks))
        companies=[dict(id=str(i),company_cnpj14=f'{i:014d}',company_name_2024='Company'+str(i),cvm_code=f'{i:06d}',
                        principal_state='admitted_association' if i<32 else 'no_admitted_principal') for i in range(55)]
        members=deepcopy(units);members[0].update(membership='sample',companies=[companies[0]['company_cnpj14'],companies[1]['company_cnpj14']])
        maps=[dict(id=c['company_cnpj14']+'|'+p,period=p,company_cnpj14=c['company_cnpj14'],native_target_code='A' if i<2 else None,
                   operator_base8=None,prudential_target_code=None) for i,c in enumerate(companies)]
        membership=self.package(root/'membership',dict(contract='ifdata-updated-membership-v1',baseline_manifest_sha256=base['expected_manifest_sha256'],periods=[p],known_nominal_companies=55),
                                dict(companies=companies,company_quarter_map=maps,unit_membership=members))
        attrs=[dict(id=x['unit_id'],unit_id=x['unit_id'],dataset=x['dataset'],code=x['code'],period=p,sr_original=None,
                    sr_analitico='S3' if x['code']=='A' and (sr_status or 'derived')=='derived' and p>='201703' else None,
                    status=(sr_status or 'derived') if x['code']=='A' and p>='201703' else 'conflict' if x['code']=='B' and p>='201703' else 'before_regime' if p<'201703' else 'unknown',
                    native_cadastro=x['own_cadastro']) for x in units]
        sr=self.package(root/'sr',dict(contract='ifdata-sr-attribution-v1',baseline={'sha256':base['expected_manifest_sha256']}),dict(attributes=attrs))
        cs=dict(period=p,dataset='financial',metric='R1',horizon='ttm',code='A');patch=deepcopy(coverage[1]);patch.update(value_fraction=F(Fraction(3,2)),numerator_fraction=F(3))
        correction=self.package(root/'patch',dict(contract='ifdata-selective-analysis-v1',baseline=base,scope=cs),dict(unit_coverage=[patch]))
        correction['scope']=cs
        complement_rows=[]
        for unit in units[:2]:
            row=deepcopy(next(r for r in coverage if r['unit_id']==unit['unit_id']));row.update(metric='LA',horizon='point',id=unit['unit_id']+'|LA|point|coverage',result_id=unit['unit_id']+'|LA|point')
            complement_rows.append(row)
        scope=dict(periods=[p],datasets=['financial'],metrics=['LA'],horizons={'LA':['point']})
        complement=self.package(root/'complement',dict(contract='ifdata-complement-analysis-v1',baseline=base,scope=scope),dict(unit_coverage=complement_rows));complement['scope']=scope
        return dict(baseline=base,membership=membership,sr=sr,corrections=[correction],complements=[complement],periods=[p],datasets=['financial','capital'],complement_metrics=['LA'],
                    analytical_company_scope='admitted_associations_2024')

    def rows(self,out,table):
        import duckdb
        with duckdb.connect() as conn:return [json.loads(r[0]) for r in conn.execute('select payload from read_parquet(?)',[str(out/(table+'.parquet'))]).fetchall()]

    def rewrite(self,spec,table,change):
        import duckdb
        root=Path(spec['root']);rows=self.rows(root,table);change(rows)
        with tempfile.TemporaryDirectory() as temp,ExitStack() as stack,duckdb.connect() as conn:
            target=Path(temp);w=u.Writer(target,table,stack)
            for r in rows:w.append(r)
            files=w.finish(conn)
            for e in files:(target/e['file']).replace(root/e['file'])
        path=root/'manifest.json';manifest=json.loads(path.read_text(encoding='utf-8'))
        manifest['files']=[e for e in manifest['files'] if not e['file'].startswith(table+'.')]+files
        manifest['tables'][table]=len(rows);path.write_text(json.dumps(manifest),encoding='utf-8')
        spec['expected_manifest_sha256']=math._digest_file(path)

    def test_missing_api_red(self):
        self.assertTrue(callable(getattr(u,'compose_analysis',None)))
        self.assertTrue(callable(getattr(u,'query_composition',None)))

    def test_nominal55_native_dedup_stocks_sr_and_exact_original_values(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cfg=self.fixture(root);out=root/'out'
            with patch.object(math,'evaluate_metric',side_effect=AssertionError('Composition must not evaluate formulas')):
                m=u.compose_analysis(cfg,out)
            coverage=self.rows(out,'unit_coverage');native=[r for r in coverage if r.get('unit_id')]
            self.assertTrue(all(r['origin']['expected_manifest_sha256'] for r in native))
            a=next(r for r in native if r['code']=='A' and r['metric']=='R1' and r['horizon']=='ttm')
            self.assertEqual(math._rational(a['value_fraction']),Fraction(3,2));self.assertEqual(a['membership'],'sample')
            self.assertEqual(a['target_cadastro']['Sr'],None);self.assertEqual(a['target_cadastro']['SrAnalitico'],'S3')
            b=next(r for r in native if r['code']=='B');self.assertEqual(b['classification_states']['SrAnalitico'],'conflict')
            self.assertTrue(all(r['value_fraction']==math._fraction_field(Fraction(1,2)) for r in native if r['origin']['kind']=='baseline'))
            company=self.rows(out,'company_coverage');r1=[r for r in company if r['dataset']=='financial' and r['metric']=='R1' and r['horizon']=='ttm']
            self.assertEqual(len(r1),55);self.assertEqual(sum(r['status']=='missing_native_unit' for r in r1),53)
            ag=next(r for r in self.rows(out,'aggregates') if r['dataset']=='financial' and r['metric']=='R1' and r['horizon']=='ttm' and r['cohort']=='total')
            self.assertEqual(ag['counts']['expected_units'],2);self.assertEqual(math._rational(ag['value_fraction']),1)
            self.assertEqual(ag['representation_coverage']['credit']['known_stock_fraction'],math._fraction_field(20))
            self.assertIn('negative_stock_weights',ag['representation_coverage']['credit']['flags'])
            self.assertEqual(ag['representation_coverage']['PL']['unknown_unit_count'],1)
            self.assertFalse(ag['unit_lists_complete']);self.assertNotIn('Atividade',m['segmentation_fields'])
            self.assertEqual(len(ag['lists']['expected_companies']),32)
            self.assertEqual(sum(r['analytical_included'] for r in r1),32)
            cells=self.rows(out,'joint_cells')
            self.assertTrue(cells);self.assertTrue(all(r['cohort'] in ('sample','remaining','unknown') for r in cells))
            capital=next(r for r in self.rows(out,'representation_stocks') if r['dataset']=='capital')
            self.assertTrue(all(v['fraction'] is None and v['status']=='own_stocks_unavailable' for v in capital['stocks'].values()))
            self.assertTrue(all(p.suffix=='.parquet' or p.name=='manifest.json' for p in out.iterdir()))
            pin=math._digest_file(out/'manifest.json')
            self.assertEqual(u.query_composition(out,pin,'select count(*) as n from company_coverage')[0]['n'],len(company))
            for sql in ("select * from read_csv('external')",'delete from company_coverage','select 1; select 2'):
                with self.subTest(sql=sql),self.assertRaises(Exception):u.query_composition(out,pin,sql)

    def test_scope_collision_pin_and_missing_complement_fail_without_accepted_manifest(self):
        for kind in ('collision','scope','pin','missing_complement'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);cfg=self.fixture(root);out=root/'bad'
                if kind=='collision':cfg['corrections']*=2
                if kind=='scope':cfg['corrections'][0]['scope']['period']='202409'
                if kind=='pin':cfg['membership']['expected_manifest_sha256']='0'*64
                if kind=='missing_complement':cfg['complements']=[]
                with self.assertRaises(ValueError):u.compose_analysis(cfg,out)
                self.assertFalse((out/'manifest.json').exists())

    def test_writer_parquet_only_and_default_are_both_lossless(self):
        import duckdb
        with tempfile.TemporaryDirectory() as temp,ExitStack() as stack,duckdb.connect() as conn:
            root=Path(temp);w=u.Writer(root,'thin',stack,formats=('parquet',));row={'id':'x','value':'0.123456789012345678901','literal':None}
            w.append(row);entries=w.finish(conn)
            self.assertEqual([e['file'] for e in entries],['thin.parquet']);self.assertEqual(self.rows(root,'thin'),[row])
            self.assertEqual([p.name for p in root.iterdir()],['thin.parquet'])

    def test_identity_cadastro_sr_original_and_duplicate_guards(self):
        for kind in ('sr_original','membership_cadastro','patch_identity','patch_duplicate'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);cfg=self.fixture(root);out=root/'bad'
                if kind=='sr_original':self.rewrite(cfg['sr'],'attributes',lambda rows:rows[0].update(sr_original='S1'))
                if kind=='membership_cadastro':self.rewrite(cfg['membership'],'unit_membership',lambda rows:rows[0]['classifications'].update(Tcb='N4'))
                if kind=='patch_identity':self.rewrite(cfg['corrections'][0],'unit_coverage',lambda rows:rows[0].update(unit_id='other'))
                if kind=='patch_duplicate':self.rewrite(cfg['corrections'][0],'unit_coverage',lambda rows:rows.append(deepcopy(rows[0])))
                with self.assertRaises(ValueError):u.compose_analysis(cfg,out)
                self.assertFalse((out/'manifest.json').exists())

    def test_query_rejects_tampered_selected_payload_and_bad_manifest_pin(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cfg=self.fixture(root);out=root/'out';u.compose_analysis(cfg,out);pin=math._digest_file(out/'manifest.json')
            with self.assertRaises(ValueError):u.query_composition(out,'0'*64,'select count(*) from aggregates')
            path=out/'aggregates.parquet';path.write_bytes(path.read_bytes()+b'changed')
            with self.assertRaises(ValueError):u.query_composition(out,pin,'select count(*) from aggregates')

    def test_complement_parquet_only_retains_identical_payloads(self):
        from tests.test_ifdata_selective_analysis import ComplementProducerTests
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);base,pin=ComplementProducerTests().fixture(root,['202412']);ordinary=root/'ordinary';thin=root/'thin'
            opts=dict(periods=['202412'],datasets=['financial'],metrics=['LA','LC','LF-DEP'])
            a=u.calculate_complements(base,pin,ordinary,**opts)
            b=u.calculate_complements(base,pin,thin,formats=('parquet',),**opts)
            self.assertEqual(a['tables'],b['tables'])
            for table in ('components','results','unit_coverage'):self.assertEqual(self.rows(ordinary,table),self.rows(thin,table))
            self.assertTrue(all(p.suffix=='.parquet' or p.name in ('complement-contexts.json','manifest.json') for p in thin.iterdir()))

    def test_pre_regime_sr_is_distinct_from_native_null_through_composition(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cfg=self.fixture(root,period='201612');out=root/'out';u.compose_analysis(cfg,out)
            rows=self.rows(out,'unit_coverage');native=[r for r in rows if r.get('unit_id')]
            self.assertTrue(native)
            for row in native:
                self.assertEqual(u._category(row,'SrAnalitico'),('before_regime',None))
                self.assertEqual(u._category(row,'Sr'),('null',None))
            segments=self.rows(out,'segment_coverage')
            self.assertEqual({r['category_state'] for r in segments if r['field']=='SrAnalitico'},{'before_regime','missing_dated_cadastro'})

    def test_sr_projection_preserves_original_missing_cadastro_states(self):
        for status in ('derived','conflict'):
            with self.subTest(status=status),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);cfg=self.fixture(root,missing_cadastro=True,sr_status=status);out=root/'out';u.compose_analysis(cfg,out)
                row=next(r for r in self.rows(out,'unit_coverage') if r['code']=='A')
                for field in u.SELECTIVE_AXES:self.assertEqual(u._category(row,field),('missing_dated_cadastro',None))
                self.assertEqual(u._category(row,'SrAnalitico'),('value','S3') if status=='derived' else ('conflict',None))
                self.assertIsNone(row['asset_fraction']);self.assertEqual(row['asset_status'],'missing_dated_cadastro')
                self.assertEqual(row['value_fraction'],math._fraction_field(Fraction(1,2)))

    def test_legacy_selective_2019_coverage_id_normalizes_only_with_exact_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cfg=self.fixture(root,period='201903');out=root/'out'
            def legacy(rows):
                rows[0]['id']=rows[0].pop('result_id');rows[0].pop('row_kind')
            self.rewrite(cfg['corrections'][0],'unit_coverage',legacy)
            u.compose_analysis(cfg,out)
            row=next(r for r in self.rows(out,'unit_coverage') if r['code']=='A' and r['metric']=='R1' and r['horizon']=='ttm')
            expected='financial|2|A|201903|R1|ttm'
            self.assertEqual(row['result_id'],expected);self.assertEqual(row['row_kind'],'native_unit')
            self.assertEqual(row['origin']['coverage_id'],expected);self.assertEqual(row['origin']['result_id'],expected)
            self.assertEqual(row['value_fraction'],math._fraction_field(Fraction(3,2)))
            company=next(r for r in self.rows(out,'company_coverage') if r['company_cnpj14']=='00000000000000' and r['dataset']=='financial' and r['metric']=='R1' and r['horizon']=='ttm')
            self.assertEqual(company['result_refs'][0]['result_id'],expected)

    def test_missing_result_id_is_not_inferred_for_other_contracts_or_wrong_legacy_identity(self):
        for kind in ('complement','wrong_selective_id'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);cfg=self.fixture(root,period='201903');out=root/'bad'
                if kind=='complement':
                    def bad(rows):rows[0].pop('result_id')
                    self.rewrite(cfg['complements'][0],'unit_coverage',bad)
                else:
                    def bad(rows):rows[0].pop('result_id');rows[0]['id']='wrong-identity'
                    self.rewrite(cfg['corrections'][0],'unit_coverage',bad)
                with self.assertRaises(ValueError):u.compose_analysis(cfg,out)
                self.assertFalse((out/'manifest.json').exists())

    def test_aggregate_parses_native_fractions_once_per_row_without_mutation(self):
        from unittest.mock import patch
        rows=[];F=math._fraction_field
        for i in range(120):
            code=str(i);ds='financial';uid='financial|2|'+code+'|202412'
            rows.append(dict(id=uid,unit_id=uid,unit_key=[ds,'2',code],code=code,dataset=ds,period='202412',metric='R1',horizon='ttm',
                status='native_null' if i%13==0 else 'ok',applicability='unknown' if i%11==0 else 'applicable',
                membership=u.COHORTS[1+i%3],companies=[str(i%5)],asset_fraction=None if i%7==0 else F(-10 if i%17==0 else 100),
                numerator_fraction=F(i+1),denominator_fraction=F(-2 if i%17==0 else 2),value_fraction=F(Fraction(i+1,-2 if i%17==0 else 2)),
                target_cadastro=dict(Data='202412',Tcb='B'+str(i%3),Td='I',Tc='P',Sr=None,SrAnalitico='S'+str(1+i%5),SegmentoTb='Bank'),flags=[],limits=[]))
        before=deepcopy(rows);native_rational=math._rational;native_fraction_ids={id(v) for r in rows for k,v in r.items() if k.endswith('_fraction') and v is not None};parsed_calls=0
        def counted(value):
            nonlocal parsed_calls
            if id(value) in native_fraction_ids:parsed_calls+=1
            return native_rational(value)
        with patch.object(math,'_rational',side_effect=counted):result=u.aggregate_unit_results(rows,fields=u.COMPOSITION_AXES)
        self.assertLessEqual(parsed_calls,4*len(rows))
        self.assertEqual(rows,before)
        again=u.aggregate_unit_results(reversed(deepcopy(rows)),fields=u.COMPOSITION_AXES)
        self.assertEqual(result,again)

    def joint_fixture(self):
        F=math._fraction_field;rows=[]
        cases=[('A','B1','Bank','C','public','S1','S1','sample',1,2,100,40,10,'ok','applicable'),
               ('B','B1','Bank','I','private','S1','S1','remaining',2,4,200,80,20,'ok','applicable'),
               ('C','N1','Payment','I','public',None,'S3','sample',3,-2,-50,None,-10,'ok','applicable'),
               ('D','N1','Payment','I','public',None,'S3','unknown',None,None,70,10,None,'native_null','unknown'),
               ('E','N4','Broker','I','private',None,None,'sample',-1,2,50,0,10,'ok','applicable'),
               ('F','B1','Bank','I','private',None,None,'unknown',10,2,60,30,5,'ok','unknown')]
        for code,tcb,segment,td,tc,sr,analytic,cohort,n,d,at,credit,pl,status,app in cases:
            uid='financial|2|'+code+'|202412';cad=dict(Data='202412',Tcb=tcb,SegmentoTb=segment,Td=td,Tc=tc,Sr=sr,SrAnalitico=analytic)
            companies={'A':['0','1'],'C':['2'],'E':['3']}.get(code,[])
            stocks={k:dict(fraction=F(v) if v is not None else None,status='ok' if v is not None else 'native_null') for k,v in [('AT',at),('credit',credit),('PL',pl)]}
            row=dict(id=uid,unit_id=uid,unit_key=['financial','2',code],code=code,dataset='financial',period='202412',metric='R1',horizon='ttm',membership=cohort,companies=companies,
                status=status,applicability=app,numerator_fraction=F(n) if n is not None else None,denominator_fraction=F(d) if d is not None else None,
                value_fraction=F(Fraction(n,d)) if n is not None else None,asset_fraction=F(at),target_cadastro=cad,representation_stocks=stocks,flags=[],limits=[])
            if code=='E':row['classification_states']={'SrAnalitico':'before_regime'}
            if code=='F':row['classification_states']={'SrAnalitico':'conflict'}
            rows.append(row)
        rows.append(dict(id='nominal|4',unit_id=None,unit_key=None,code=None,dataset='financial',period='202412',metric='R1',horizon='ttm',membership='sample',companies=['4'],
            status='missing_native_unit',applicability='unknown',value_fraction=None,numerator_fraction=None,denominator_fraction=None,asset_fraction=None,target_cadastro=None,flags=[],limits=[]))
        return rows

    def test_observed_joint_cells_and_crossfilters_equal_direct_exact_reduction(self):
        rows=self.joint_fixture();before=deepcopy(rows);cells=u._composition_joint_cells(rows)
        self.assertEqual(rows,before);self.assertEqual(sum(c['source_counts']['rows'] for c in cells),len(rows))
        self.assertEqual(sum(c['source_counts']['native_units'] for c in cells),6)
        self.assertEqual(sum(c['source_counts']['nominal_companies'] for c in cells),1)
        self.assertLessEqual(len(cells),len(rows));self.assertEqual(len({c['id'] for c in cells}),len(cells))
        choices=[{}, {'Tcb':('value','B1'),'Sr':('value','S1')}, {'Tcb':('value','N1'),'Tc':('value','public')},
                 {'SegmentoTb':('value','Bank'),'Td':('value','C'),'Sr':('value','S1')},
                 {'SrAnalitico':('before_regime',None)}, {'SrAnalitico':('conflict',None)}, {'Tcb':('value','absent')}]
        for filters in choices:
            with self.subTest(filters=filters):
                selected=[c for c in cells if all((c['dimensions'][k]['state'],c['dimensions'][k]['value'])==v for k,v in filters.items())]
                direct_rows=[r for r in rows if all(u._category(r,k)==v for k,v in filters.items())]
                if not direct_rows:self.assertEqual(selected,[]);continue
                direct=u.aggregate_unit_results(direct_rows,fields=())['aggregates'];total=next(r for r in direct if r['cohort']=='total')
                for field in ('numerator_fraction','denominator_fraction'):
                    summed=sum((math._rational(c[field]) for c in selected if c[field] is not None),Fraction())
                    self.assertEqual(summed,math._rational(total[field]) if total[field] is not None else 0)
                self.assertEqual(sum(c['counts']['expected_units'] for c in selected),total['counts']['expected_units'])
                self.assertEqual(set(c for cell in selected for c in cell['lists']['expected_companies']),set(total['lists']['expected_companies']))
                values=sorted(Fraction(int(n),int(d)) for c in selected for n,d in c['distribution_sorted_fractions'])
                original=sorted(math._rational(r['value_fraction']) for r in direct_rows if u._eligible(r))
                self.assertEqual(values,original)
                for q in (Fraction(1,4),Fraction(1,2),Fraction(3,4)):
                    self.assertEqual(math._quantile2(values,q) if values else None,math._quantile2(original,q) if original else None)
                for role in ('AT','credit','PL'):
                    def stock(c):return c['asset_coverage']['known_asset_fraction'] if role=='AT' else c['representation_coverage'][role]['known_stock_fraction']
                    known=sum((math._rational(stock(c)) for c in selected),Fraction())
                    expected=sum((math._rational(r['representation_stocks'][role]['fraction']) for r in direct_rows if r.get('unit_id') and r['representation_stocks'][role]['fraction'] is not None),Fraction())
                    self.assertEqual(known,expected)
                    summaries=[c['asset_coverage'] if role=='AT' else c['representation_coverage'][role] for c in selected]
                    direct_native=[r for r in direct_rows if r.get('unit_id')]
                    expected_known=[r for r in direct_native if r['representation_stocks'][role]['fraction'] is not None]
                    self.assertEqual(sum(s['known_unit_count'] for s in summaries),len(expected_known))
                    self.assertEqual(sum(s['unknown_unit_count'] for s in summaries),len(direct_native)-len(expected_known))
                    self.assertEqual(sum(s['negative_known_unit_count'] for s in summaries),sum(math._rational(r['representation_stocks'][role]['fraction'])<0 for r in expected_known))
        a=next(c for c in cells if c['dimensions']['Tcb']['value']=='B1' and c['cohort']=='sample')
        self.assertEqual(a['counts']['expected_units'],1);self.assertEqual(a['lists']['expected_companies'],['0','1'])

    def test_analytical_sr_unknown_is_separate_from_observed_original_null(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cfg=self.fixture(root,sr_status='unknown');out=root/'out';u.compose_analysis(cfg,out)
            row=next(r for r in self.rows(out,'unit_coverage') if r['code']=='A')
            self.assertEqual(u._category(row,'SrAnalitico'),('unknown',None))
            self.assertEqual(u._category(row,'Sr'),('null',None))
            self.assertEqual(row['asset_fraction'],math._fraction_field(100))
            self.assertEqual(row['value_fraction'],math._fraction_field(Fraction(1,2)))

    def test_joint_cell_zero_summed_denominator_retains_contributions_and_distribution(self):
        rows=self.joint_fixture();second=deepcopy(rows[2]);second.update(id='financial|2|G|202412',unit_id='financial|2|G|202412',unit_key=['financial','2','G'],code='G',companies=['5'],
            numerator_fraction=math._fraction_field(1),denominator_fraction=math._fraction_field(2),value_fraction=math._fraction_field(Fraction(1,2)))
        rows.append(second);cells=u._composition_joint_cells(rows)
        cell=next(c for c in cells if c['cohort']=='sample' and c['dimensions']['Tcb']['value']=='N1')
        self.assertEqual(cell['status'],'zero_denominator');self.assertEqual(cell['numerator_fraction'],math._fraction_field(4))
        self.assertEqual(cell['denominator_fraction'],math._fraction_field(0));self.assertIsNone(cell['value_fraction'])
        self.assertEqual(cell['distribution_sorted_fractions'],[['-3','2'],['1','2']])
        self.assertEqual(cell['counts']['eligible_units'],2)

    def test_unchanged_baseline_coverage_preserves_exact_fractions(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cfg=self.fixture(root);out=root/'out'
            u.compose_analysis(cfg,out)
            rows=self.rows(out,'unit_coverage')
            unchanged=[r for r in rows if r['origin']['kind']=='baseline']
            self.assertTrue(unchanged)
            self.assertTrue(all(r['value_fraction']==math._fraction_field(Fraction(1,2)) for r in unchanged))


if __name__=='__main__':unittest.main()

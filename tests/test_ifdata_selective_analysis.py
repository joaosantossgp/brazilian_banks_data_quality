"""Finite LL bridge: preserve native data and guard the actual 2019 exception."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import csv
import hashlib
import json
import tempfile
import unittest

from bank_quality import ifdata_analysis as math
from bank_quality import ifdata_universe_analysis as universe

PERIODS=('201803','201806','201809','201812','201903')


def complement_catalogue(datasets=('financial','individual')):
    from bank_quality.ifdata_variable_catalog import DIMENSIONS
    periods=[f'{y}{q}' for y in range(2010,2025) for q in ('03','06','09','12')]
    roles=[('funding','3','78185','[41000007] + [42000006] + [43000005] + [46000002]'),
           ('repos','3','78288','[42000006]'),('issuances','3','78294','[43000005]'),
           ('loans_transfers','3','78295','[46000002]'),
           ('credit_income','4','78203','[71100001]+[71910002]+[71915007]+[71920009]+[71925004]+[71950000]+[71980001]+[81945005]+[81950007]+[81915004]'),
           ('RIF','4','78208','Somatório de Rendas de Operações de Crédito, Rendas de Operações de Arrendamento Mercantil, Rendas de Operações com TVM, Rendas de Operações com Instrumentos Financeiros Derivativos, Resultado de Operações de Câmbio e Rendas de Aplicações Compulsórias'),
           ('other_income','4','78222','[71900005]-[71910002]-[71915007]-[71920009]-[71925004]-[71930006]-[71940003]-[71945008]-[71947006]-[71950000]-[71955005]-[71960007]-[71965002]-[71970004]-[71980001]-[71990053]-[71990101][71990125]-[71990156]-[71990204]-[71990266]-[71990307]-[71990352]-[71990400]-[71990503]-[71990606]-[71990709]-[71990802]-[71990905]'),
           ('participations','4','78221','[71800002]+[71990802]+[71990905]+[71990709]+[81600003]+[81830804]+[81830907]+[81830701]')]
    rows=[]
    for ds in datasets:
        for name,report,account,description in roles:
            literal=dict(zip(DIMENSIONS,(ds,universe.TYPES[ds],report,'Passivo' if report=='3' else 'DRE',account,None,name,description)))
            rows.append(dict(literal,periodos=periods))
    return rows


class ComplementProfileTests(unittest.TestCase):
    def compile(self,rows=None):
        fn=getattr(universe,'compile_complement_profile',None)
        self.assertIsNotNone(fn,'Additive complement profile compiler is missing')
        return fn(universe.load_profile(),complement_catalogue() if rows is None else rows,['financial','individual'])

    def test_additive_profile_keeps_frozen_contexts_and_own_individual_bindings(self):
        original=universe.load_profile();profile=self.compile()
        self.assertEqual(profile['contexts'][:len(original['contexts'])],original['contexts'])
        self.assertEqual(len(profile['contexts'])-len(original['contexts']),16)
        for c in profile['contexts'][len(original['contexts']):]:
            self.assertEqual(len(c['periods']),60)
            self.assertEqual(c['literal_context']['TipoInstituicao'],universe.TYPES[c['literal_context']['dataset']])
            self.assertEqual(c['context_sha256'],hashlib.sha256(json.dumps(c['literal_context'],ensure_ascii=False,sort_keys=True).encode()).hexdigest())

    def test_compiler_rejects_ambiguous_changed_or_incomplete_literal_context(self):
        for kind in ('duplicate','description','period','perspective'):
            rows=complement_catalogue()
            if kind=='duplicate':rows.append(deepcopy(rows[0]))
            if kind=='description':rows[0]['DescricaoColuna']='other'
            if kind=='period':rows[0]['periodos']=rows[0]['periodos'][1:]
            if kind=='perspective':next(r for r in rows if r['dataset']=='individual')['TipoInstituicao']='2'
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.compile(rows)

    def test_api_rejects_unapproved_selection_before_io(self):
        fn=getattr(universe,'calculate_complements',None)
        self.assertIsNotNone(fn,'Selective complement producer is missing')
        for options in ({'metrics':['R1']},{'datasets':['capital']},{'periods':['202503']},{'periods':['202412','202412']}):
            args=dict(periods=['202412'],datasets=['financial'],metrics=['LA']);args.update(options)
            with self.subTest(options=options),self.assertRaises(ValueError):fn('missing','a'*64,'missing-output',**args)

    def test_rif_binding_is_a_flow_and_ambiguous_history_is_rejected(self):
        profile=self.compile()
        rif=[c for c in profile['contexts'] if c['component']=='intermediation_income']
        self.assertEqual(len(rif),2,'RIF must have its own authenticated binding in each perspective')
        self.assertTrue(all(c['window_rule']=='native-semester-analysis-v2' for c in rif))
        rows=complement_catalogue();rows.append(deepcopy(next(r for r in rows if r['Conta']=='78208')))
        with self.assertRaises(ValueError):self.compile(rows)

    def test_wide_income_has_two_distinct_own_flow_bindings(self):
        contexts=self.compile()['contexts']
        for name in ('other_operating_income','participation_result'):
            bindings=[c for c in contexts if c['component']==name]
            self.assertEqual(len(bindings),2)
            self.assertTrue(all(c['window_rule']=='native-semester-analysis-v2' for c in bindings))


class ComplementProducerTests(unittest.TestCase):
    def test_income_selection_keeps_adopted_denominators_separate(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);base,pin=self.fixture(root,['202312','202403','202406','202409','202412'])
            out=root/'income'
            manifest=universe.calculate_complements(base,pin,out,periods=['202412'],metrics=['E2-W','E2-WP'])
            rows=json.loads((out/'results.json').read_text(encoding='utf8'))
            self.assertEqual(manifest['tables']['results'],24)
            for metric,expected in [('E2-W',Fraction(-2,3)),('E2-WP',Fraction(-1,2))]:
                r=next(r for r in rows if r['code']=='BNDES' and r['metric']==metric and r['horizon']=='quarter')
                self.assertEqual(r['status'],'ok');self.assertEqual(math._rational(r['value_fraction']),expected)
                self.assertIn('signed_cost_reversal',r['flags'])
            self.assertEqual(math._digest_file(base/'manifest.json'),pin)

    def test_assaf_selection_preserves_native_windows_states_and_cohorts(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);base,pin=self.fixture(root,['202312','202403','202406','202409','202412'])
            out=root/'assaf'
            manifest=universe.calculate_complements(base,pin,out,periods=['202412'],
                metrics=['L1','PL_DEP','R3','RIF_AT'])
            rows=json.loads((out/'results.json').read_text(encoding='utf8'))
            pick=lambda code,metric,h:next(r for r in rows if r['code']==code and r['metric']==metric and r['horizon']==h)
            self.assertEqual(manifest['tables']['results'],36)
            self.assertEqual(math._rational(pick('BNDES','L1','point')['value_fraction']),Fraction(1,2))
            self.assertEqual(math._rational(pick('BNDES','PL_DEP','point')['value_fraction']),4)
            self.assertEqual(math._rational(pick('BNDES','R3','ttm')['value_fraction']),1)
            self.assertEqual(math._rational(pick('BNDES','RIF_AT','quarter')['value_fraction']),Fraction(7,135))
            self.assertEqual(pick('NULL','L1','point')['status'],'native_null')
            self.assertEqual(pick('ZERO','PL_DEP','point')['status'],'zero_denominator')
            self.assertEqual(pick('UNKNOWN','R3','quarter')['membership'],'unknown')
            self.assertEqual(math._digest_file(base/'manifest.json'),pin)

    def fixture(self,root,periods,dataset='financial'):
        import duckdb
        from bank_quality.ifdata_odata import COLUMNS,CONTRACT
        from bank_quality.ifdata_variable_catalog import DIMENSIONS,CONTRACT as CAT
        digest=math._digest_file;source=root/'source';source.mkdir();base=root/'base';base.mkdir();cat=root/'catalogue';cat.mkdir()
        catalogue=complement_catalogue((dataset,));profile=universe.compile_complement_profile(universe.load_profile(),catalogue,[dataset])
        contexts=[c for c in profile['contexts'] if c['literal_context']['dataset']==dataset]
        catalogue.extend(dict(c['literal_context'],periodos=c['periods']) for c in universe.load_profile()['contexts'] if c['literal_context']['dataset']==dataset)
        tokens=dict(cash='10',interfinancial='20',credit='40',deposits='10',repos='20',issuances='30',loans_transfers='40',funding='100',
                    RBIF='12',provision_flow='-2',services='2',fees='1',personnel='-2',administration='-1',credit_income='20',
                    LL='3',RIF='12',PL='40',sight_deposits='20',other_income='6',participations='3')
        codes=('BNDES','IP','COOP','UNKNOWN','NULL','ZERO');files=[];units=[]
        with duckdb.connect() as conn:
            for i,p in enumerate(periods):
                rows=[]
                for code in codes:
                    for name in set(n for metric in math.COMPLEMENT_METRICS.values() for n in metric):
                        ctx=next(c for c in contexts if c['component']==math.COMPONENT_NAMES[name] and p in c['periods'])
                        token=str(100+i*10) if name=='AT' else tokens[name]
                        if name in math.FLOW_COMPONENTS:token=str({'03':3,'06':8,'09':5,'12':12}[p[-2:]])
                        if code=='NULL' and name=='cash':token=None
                        if code=='ZERO' and name in ('funding','deposits','repos','issuances','loans_transfers'):token='0'
                        rows.append(dict({k:v for k,v in ctx['literal_context'].items() if k!='dataset'},CodInst=code,AnoMes=p,Saldo=token,source_file='native',source_sha256='a'*64,source_row=str(len(rows))))
                    cad=dict(Tcb={'BNDES':'B4','IP':'N4','COOP':'B3'}.get(code),Td='I',Tc=None,Sr=None,SegmentoTb=None)
                    units.append(dict(id=code+'|'+p,unit_id=dataset+'|'+universe.TYPES[dataset]+'|'+code+'|'+p,period=p,dataset=dataset,code=code,
                                      membership='unknown' if code=='UNKNOWN' else 'remaining',companies=[],classifications=cad,own_cadastro=dict(CodInst=code,Data=p)))
                conn.execute('create or replace table native('+','.join('"'+c+'" varchar' for c in COLUMNS)+')')
                conn.executemany('insert into native values ('+','.join('?' for _ in COLUMNS)+')',[[r.get(c) for c in COLUMNS] for r in rows])
                path=source/(p+'.parquet');conn.execute('copy native to ? (format parquet)',[str(path)])
                files.append(dict(file=path.name,period=int(p),type=int(universe.TYPES[dataset]),rows=len(rows),sha256=digest(path)))
            catfiles=[]
            catjson=cat/'fixture.json';catjson.write_text(json.dumps(catalogue),encoding='utf-8')
            for table in ('catalogo_variaveis','cobertura_variaveis'):
                for ext,fmt in (('parquet','parquet'),('csv','csv, header true')):
                    path=cat/(table+'.'+ext)
                    conn.execute('copy (select * from read_json_auto($source)) to $destination (format '+fmt+')',dict(source=str(catjson),destination=str(path)))
                    catfiles.append(dict(file=path.name,sha256=digest(path)))
            catjson.unlink()
        (source/'manifest.json').write_text(json.dumps(dict(contract=CONTRACT,files=files)),encoding='utf-8')
        inp=dict(root=str(source),expected_manifest_sha256=digest(source/'manifest.json'))
        (cat/'manifest.json').write_text(json.dumps(dict(contract=CAT,files=catfiles,inputs={dataset:dict(manifest_sha256=inp['expected_manifest_sha256'])})),encoding='utf-8')
        with (base/'unit_periods.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['period','dataset','payload']);w.writeheader()
            for u in units:w.writerow(dict(period=u['period'],dataset=dataset,payload=json.dumps(u)))
        m=dict(contract=universe.CONTRACT,stage='coverage-and-aggregation',profile_sha256=digest(universe.PROFILE_PATH),tables={'unit_periods':len(units)},
               files=[dict(file='unit_periods.csv',sha256=digest(base/'unit_periods.csv'),rows=len(units))],inputs={dataset:inp,'catalogue':dict(root=str(cat),expected_manifest_sha256=digest(cat/'manifest.json'))})
        (base/'manifest.json').write_text(json.dumps(m),encoding='utf-8')
        return base,digest(base/'manifest.json')

    def test_stock_producer_keeps_units_null_zero_exact_funding_and_compact_provenance(self):
        self.assertTrue(callable(getattr(universe,'calculate_complements',None)),'Complement producer missing')
        for ds in ('financial','individual'):
            with self.subTest(dataset=ds),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);base,pin=self.fixture(root,['202412'],ds);out=root/'out'
                metrics=['LA','LC','LF-DEP','LF-OC','LF-EM','LF-REP']
                m=universe.calculate_complements(base,pin,out,periods=['202412'],datasets=[ds],metrics=metrics)
                results=json.loads((out/'results.json').read_text(encoding='utf-8'));comp=json.loads((out/'components.json').read_text(encoding='utf-8'))
                lookup={(r['code'],r['metric']):r for r in results}
                self.assertEqual(m['tables']['results'],36);self.assertEqual(m['tables']['unit_coverage'],36)
                for code in ('BNDES','IP','COOP','UNKNOWN'):
                    self.assertEqual(math._rational(lookup[code,'LA']['value_fraction']),Fraction(3,10))
                    self.assertEqual(sum(math._rational(lookup[code,k]['value_fraction']) for k in metrics[2:]),1)
                self.assertEqual(lookup['NULL','LA']['status'],'native_null')
                self.assertEqual(lookup['ZERO','LF-DEP']['status'],'zero_denominator')
                self.assertEqual(len(comp),len({r['id'] for r in comp}));self.assertTrue(all('binding_ref' in r for r in comp))
                self.assertTrue(all('source_file' in r['sources'][0] for r in comp if r['sources']))
                self.assertEqual(math._digest_file(base/'manifest.json'),pin)
                with self.assertRaises(FileExistsError):universe.calculate_complements(base,pin,out,periods=['202412'],datasets=[ds],metrics=metrics)
                with self.assertRaises(ValueError):universe.calculate_complements(base,'0'*64,root/'bad',periods=['202412'],datasets=[ds],metrics=metrics)
                self.assertFalse((root/'bad').exists())

    def test_full_ttm_day_weighted_mean_uses_history_without_2019_ll_release(self):
        import calendar
        from datetime import date
        self.assertTrue(callable(getattr(universe,'calculate_complements',None)),'Complement producer missing')
        periods=['201712']+[f'{y}{q}' for y in (2018,2019) for q in ('03','06','09','12')]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);base,pin=self.fixture(root,periods);out=root/'out'
            universe.calculate_complements(base,pin,out,periods=periods[4:],metrics=['R4','E3','R5','RS'])
            rows=json.loads((out/'results.json').read_text(encoding='utf-8'))
            for index in range(4,len(periods)):
                p=periods[index];endpoints=[]
                for i in range(index-4,index+1):
                    y,m=int(periods[i][:4]),int(periods[i][-2:]);endpoints.append((date(y,m,calendar.monthrange(y,m)[1]),100+i*10))
                mean=sum(Fraction(a[1]+b[1],2)*(b[0]-a[0]).days for a,b in zip(endpoints,endpoints[1:]))/(endpoints[-1][0]-endpoints[0][0]).days
                expected={'R4':20/mean,'E3':-40/mean,'R5':Fraction(1,2),'RS':Fraction(1)}
                for metric,value in expected.items():
                    result=next(r for r in rows if r['code']=='BNDES' and r['period']==p and r['metric']==metric and r['horizon']=='ttm')
                    self.assertEqual(result['status'],'ok');self.assertEqual(math._rational(result['value_fraction']),value)
                quarter=next(r for r in rows if r['code']=='BNDES' and r['period']==p and r['metric']=='R5' and r['horizon']=='quarter')
                self.assertEqual(math._rational(quarter['value_fraction']),Fraction({'03':3,'06':5,'09':5,'12':7}[p[-2:]],40))
            self.assertFalse(any(r.get('profit_bridge') for r in rows))

    def test_producer_refuses_overlapping_destination_bad_source_and_catalogue_lineage(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);base,pin=self.fixture(root,['202412'])
            options=dict(periods=['202412'],metrics=['LA'])
            for out in (base/'nested',root/'source'/'nested',root/'catalogue'/'nested'):
                with self.subTest(out=out),self.assertRaises(ValueError):universe.calculate_complements(base,pin,out,**options)
                self.assertFalse(out.exists())
            part=root/'source'/'202412.parquet';old=part.read_bytes();part.write_bytes(old+b'changed')
            with self.assertRaises(ValueError):universe.calculate_complements(base,pin,root/'bad-source',**options)
            self.assertFalse((root/'bad-source').exists());part.write_bytes(old)
            path=root/'catalogue'/'manifest.json';cat=json.loads(path.read_text(encoding='utf-8'))
            cat['inputs']['financial']['manifest_sha256']='0'*64;path.write_text(json.dumps(cat),encoding='utf-8')
            mp=base/'manifest.json';main=json.loads(mp.read_text(encoding='utf-8'));main['inputs']['catalogue']['expected_manifest_sha256']=math._digest_file(path)
            mp.write_text(json.dumps(main),encoding='utf-8');pin=math._digest_file(mp)
            with self.assertRaisesRegex(ValueError,'lineage'):universe.calculate_complements(base,pin,root/'bad-lineage',**options)
            self.assertFalse((root/'bad-lineage').exists())


def fixture(kind='group',jcp='0',periods=PERIODS,dataset='financial'):
    profile=universe.load_profile();components={'LL':[],'AT':[],'PL':[]};native=[]
    for i,p in enumerate(periods):
        rows=[]
        for name,token in [('LL',['5','12','7','18','10'][i]),('AT','100'),('PL','50')]:
            ctx=next(c for c in profile['contexts'] if c['component']==name and c['literal_context']['dataset']==dataset and p in c['periods'])
            row={k:v for k,v in ctx['literal_context'].items() if k!='dataset'}
            row.update(CodInst='U',AnoMes=p,Saldo=token,source_file='native.parquet',source_sha256='a'*64,source_row=str(i))
            rows.append(row)
            components[name].append(math.resolve_component(profile,name,dataset,'U',p,rows))
        ll=deepcopy(rows[0]);ll.update(NumeroRelatorio='4',NomeRelatorio='DRE')
        capital=deepcopy(ll);capital.update(Conta='78230',DescricaoColuna='[81956001]' if p>='201903' else '[81955002]',Saldo=jcp if p=='201812' else '0')
        native.extend([ll,capital])
    cad={'Tcb':'N4' if kind=='ip' else 'B1','Td':'I' if kind=='ip' else 'C','SegmentoTb':'Instituição de Pagamento' if kind=='ip' else None}
    return components,native,cad


class ProfitBridgeTests(unittest.TestCase):
    def bridge(self,components,native,cad):
        fn=getattr(universe,'bridge_profit_201903',None)
        self.assertIsNotNone(fn,'Finite reviewed LL bridge is missing')
        return fn(components['LL'],native,cad)

    def test_individual_bridge_keeps_namespace_and_rejects_financial_evidence(self):
        components,native,cad=fixture(dataset='individual')
        ll,proof=self.bridge(components,native,cad)
        self.assertTrue(proof['released']);self.assertTrue(ll[0]['definition_id'].startswith('individual:'))
        self.assertEqual(ll[0]['unit_key'],components['LL'][0]['unit_key'])
        components['LL'][0]['binding']['literal_context']['TipoInstituicao']='2'
        self.assertFalse(self.bridge(components,native,cad)[1]['released'])
        components,native,cad=fixture('ip',dataset='individual')
        for row in native:row['TipoInstituicao']='2'
        self.assertFalse(self.bridge(components,native,cad)[1]['released'])

    def test_group_releases_only_the_two_reviewed_contexts_without_mutating_native_data(self):
        components,native,cad=fixture();before=deepcopy(components)
        baseline=math.evaluate_metric('R1',dict(period='201903',components=components,financial_statement=True),'ttm')
        self.assertEqual(baseline['status'],'incompatible_definition')
        ll,proof=self.bridge(components,native,cad)
        result=math.evaluate_metric('R1',dict(period='201903',components={**components,'LL':ll},financial_statement=True),'ttm')
        self.assertTrue(proof['released']);self.assertEqual(proof['basis'],'native_published_profit')
        self.assertEqual(result['value'],'0.35');self.assertEqual(before,components)
        self.assertEqual([o['binding'] for o in ll],[o['binding'] for o in before['LL']])
        self.assertEqual([o['token'] for o in ll],[o['token'] for o in before['LL']])

    def test_ip_requires_zero_in_every_dependency_not_just_the_last_quarter(self):
        for token,released in [('0',True),('-32012000.1',False),(None,False)]:
            with self.subTest(token=token):
                components,native,cad=fixture('ip',token);ll,proof=self.bridge(components,native,cad)
                self.assertEqual(proof['released'],released)
                self.assertEqual(ll==components['LL'],not released)

    def test_ip_absent_or_ambiguous_or_different_ll_does_not_release(self):
        for change in ('missing','duplicate','ll_different','description','unit'):
            components,native,cad=fixture('ip')
            if change=='missing':native.pop()
            if change=='duplicate':native.append(deepcopy(native[-1]))
            if change=='ll_different':native[-2]['Saldo']='999'
            if change=='description':native[-1]['DescricaoColuna']='other_account'
            if change=='unit':native[-1]['CodInst']='OTHER'
            with self.subTest(change=change):self.assertFalse(self.bridge(components,native,cad)[1]['released'])

    def test_bridge_does_not_override_other_identity_scale_and_window_guards(self):
        for field,value in [('definition_id','unreviewed'),('unit_key',('individual','2','U')),('scale','native_index_unverified'),('window_rule','unverified')]:
            components,native,cad=fixture();components['LL'][-1][field]=value
            with self.subTest(field=field):self.assertFalse(self.bridge(components,native,cad)[1]['released'])

    def test_null_and_missing_stock_survive_the_profit_bridge(self):
        components,native,cad=fixture();ll,proof=self.bridge(components,native,cad)
        components['LL']=ll;components['AT'][-1]['token']=None
        r=math.evaluate_metric('R1',dict(period='201903',components=components,financial_statement=True),'ttm')
        self.assertEqual(r['status'],'native_null')
        components['AT'].pop(0)
        r=math.evaluate_metric('R1',dict(period='201903',components=components,financial_statement=True),'ttm')
        self.assertEqual(r['status'],'missing_opening')

    def test_later_windows_use_the_actual_profit_dependencies(self):
        windows={
            '201906':('201806','201809','201812','201903','201906'),
            '201909':('201809','201812','201903','201906','201909')}
        for period,periods in windows.items():
            for kind in ('group','ip'):
                with self.subTest(period=period,kind=kind):
                    components,native,cad=fixture(kind,periods=periods)
                    original=deepcopy(components)
                    ll,proof=universe.bridge_profit_201903(components['LL'],native,cad,period=period)
                    self.assertTrue(proof['released'])
                    r=math.evaluate_metric('R1',dict(period=period,components={**components,'LL':ll},financial_statement=True),'ttm')
                    # Independent sums of genuine quarters for synthetic native semester flows.
                    expected=Fraction(17,100) if period=='201906' else Fraction(35,100)
                    self.assertEqual(math._rational(r['value_fraction']),expected)
                    self.assertEqual(components,original)
            components,native,cad=fixture('ip','-32012000.1',periods=periods)
            self.assertFalse(universe.bridge_profit_201903(components['LL'],native,cad,period=period)[1]['released'])
        # June opening is required for mean assets, but its LL is never consumed.
        components,native,cad=fixture('ip',periods=windows['201906'])
        components['LL'][0]['token']=None
        native=[r for r in native if r['AnoMes']!='201806']
        self.assertTrue(universe.bridge_profit_201903(components['LL'],native,cad,period='201906')[1]['released'])
        for field,value in [('DescricaoColuna','[81955002]'),('Saldo',None)]:
            components,native,cad=fixture('ip',periods=windows['201906'])
            native[-1][field]=value
            self.assertFalse(universe.bridge_profit_201903(components['LL'],native,cad,period='201906')[1]['released'])

    def test_roe_keeps_equity_stock_guards_and_signed_denominators(self):
        for case in ('ok','zero','negative','null','missing','different_definition'):
            components,native,cad=fixture();ll,proof=self.bridge(components,native,cad);components['LL']=ll
            if case in ('zero','negative'):
                for r in components['PL']:r['token']='0' if case=='zero' else '-50'
            if case=='null':components['PL'][0]['token']=None
            if case=='missing':components['PL'].pop(0)
            if case=='different_definition':components['PL'][0]['definition_id']='unreviewed_PL'
            r=math.evaluate_metric('R2',dict(period='201903',components=components,financial_statement=True),'ttm')
            expected={'ok':'ok','zero':'zero_denominator','negative':'ok','null':'native_null','missing':'missing_opening','different_definition':'incompatible_definition'}[case]
            with self.subTest(case=case):self.assertEqual(r['status'],expected)
            if case=='ok':self.assertEqual(r['value'],'0.7')
            if case=='negative':self.assertEqual(r['value'],'-0.7');self.assertIn('negative_denominator',r['flags'])

    def test_other_selective_targets_are_rejected_before_io(self):
        fn=getattr(universe,'recalculate_slice',None)
        self.assertIsNotNone(fn,'Selective runner is missing')
        for changes in ({'metric':'C1'},{'period':'201912'},{'dataset':'capital'},{'horizon':'quarter'}):
            options=dict(metric='R1',period='201903',dataset='financial',horizon='ttm',**{})
            options.update(changes)
            with self.subTest(changes=changes),self.assertRaisesRegex(ValueError,'reviewed selective target'):
                fn('missing','a'*64,'missing-output',**options)


class SelectiveRunTests(unittest.TestCase):
    def test_authenticated_small_run_keeps_stone_out_and_preserves_the_baseline(self):
        for period in ('201903','201906','201909'):
            for metric in ('R1','R2'):
                for dataset in ('financial','individual'):
                    with self.subTest(period=period,metric=metric,dataset=dataset):self.run_small(period,metric,dataset)

    def run_small(self,period,metric,dataset):
        periods=universe.PROFIT_BRIDGE_WINDOWS[period]
        import duckdb
        from bank_quality.ifdata_odata import COLUMNS,CONTRACT
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source';source.mkdir();base=root/'base';base.mkdir()
            digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
            rows=[];units=[]
            for code,kind,jcp in [('G','group','0'),('P','ip','0'),('S','ip','-32012000.1')]:
                comp,native,cad=fixture(kind,jcp,periods=periods,dataset=dataset)
                native.extend(r['sources'][0] for obs in comp.values() for r in obs)
                for r in native:r.update(CodInst=code);rows.append(r)
                units.append(dict(id=code,unit_id=dataset+'|'+universe.TYPES[dataset]+'|'+code+'|'+period,period=period,dataset=dataset,code=code,
                    membership='sample' if code=='G' else 'remaining',companies=['A'] if code=='G' else [],
                    classifications=cad,own_cadastro={'CodInst':code,'Data':period}))
            files=[]
            with duckdb.connect() as conn:
                for i,p in enumerate(periods):
                    selected=[r for r in rows if r['AnoMes']==p];path=source/f'part-{i}.parquet'
                    conn.execute('create or replace table native('+','.join('"'+c+'" varchar' for c in COLUMNS)+')')
                    conn.executemany('insert into native values ('+','.join('?' for _ in COLUMNS)+')',[[r.get(c) for c in COLUMNS] for r in selected])
                    conn.execute('copy native to ? (format parquet)',[str(path)])
                    files.append(dict(file=path.name,period=int(p),type=int(universe.TYPES[dataset]),rows=len(selected),sha256=digest(path)))
            (source/'manifest.json').write_text(json.dumps(dict(contract=CONTRACT,files=files)),encoding='utf-8')
            with (base/'unit_periods.csv').open('w',encoding='utf-8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['period','dataset','payload']);w.writeheader()
                for u in units:w.writerow(dict(period=period,dataset=dataset,payload=json.dumps(u)))
            manifest=dict(contract=universe.CONTRACT,stage='coverage-and-aggregation',profile_sha256=digest(universe.PROFILE_PATH),
                tables={'unit_periods':3},files=[dict(file='unit_periods.csv',sha256=digest(base/'unit_periods.csv'),rows=3)],
                inputs={dataset:dict(root=str(source),expected_manifest_sha256=digest(source/'manifest.json'))})
            (base/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8');pin=digest(base/'manifest.json')
            fn=getattr(universe,'recalculate_slice',None);self.assertIsNotNone(fn,'Selective runner is missing')
            with self.assertRaises(ValueError):fn(base,'0'*64,root/'bad-pin',period=period,metric=metric,dataset=dataset)
            self.assertFalse((root/'bad-pin').exists())
            out=root/'result';result=fn(base,pin,out,period=period,metric=metric,dataset=dataset)
            self.assertEqual(result['baseline_statuses'],{'incompatible_definition':3})
            produced=json.loads((out/'results.json').read_text(encoding='utf-8'))
            self.assertEqual({r['code']:r['status'] for r in produced},{'G':'ok','P':'ok','S':'incompatible_definition'})
            self.assertEqual(next(r for r in produced if r['code']=='G')['value'],('0.34' if period=='201906' else '0.7') if metric=='R2' else ('0.17' if period=='201906' else '0.35'))
            seg=json.loads((out/'segment_coverage.json').read_text(encoding='utf-8'))
            self.assertEqual({r['field'] for r in seg},set(universe.SELECTIVE_AXES))
            self.assertEqual(digest(base/'manifest.json'),pin)
            self.assertTrue(all(digest(out/e['file'])==e['sha256'] for e in result['files']))
            with duckdb.connect() as conn:
                self.assertEqual(conn.execute('select count(*) from read_parquet(?) where status=?',[str(out/'results.parquet'),'ok']).fetchone()[0],2)
            with self.assertRaises(FileExistsError):fn(base,pin,out,period=period,metric=metric,dataset=dataset)
            (source/files[0]['file']).write_bytes(b'corrupt')
            with self.assertRaises(ValueError):fn(base,pin,root/'bad-source',period=period,metric=metric,dataset=dataset)
            self.assertFalse((root/'bad-source'/'manifest.json').exists())


CAIXA_DATES=('202009','202012','202103','202106','202109','202112','202203','202206')


def caixa_fixture(period='202109',metric='R1'):
    periods=CAIXA_DATES[CAIXA_DATES.index(period)-4:CAIXA_DATES.index(period)+1]
    profile=universe.load_profile();names=math.METRICS[metric]
    original={name:[] for name in names};predecessor={name:[] for name in names};cad=[]
    for i,p in enumerate(periods):
        before=p<'202109'
        cad.append(dict(Data=p,CodInst='00360305',CnpjInstituicaoLider='00360305',
                        CodConglomeradoFinanceiro=None if before else 'C0051626'))
        if not before:
            for code in ('C0051626','42040639'):
                cad.append(dict(Data=p,CodInst=code,CnpjInstituicaoLider='00360305',CodConglomeradoFinanceiro='C0051626'))
        for name in names:
            context=next(c for c in profile['contexts'] if c['component']==name and c['literal_context']['dataset']=='financial' and p in c['periods'])
            token=str([5,12,7,18,10][i]) if name=='LL' else ('100' if name=='AT' else '50')
            def obs(code,available):
                row={k:v for k,v in context['literal_context'].items() if k!='dataset'}
                row.update(CodInst=code,AnoMes=p,Saldo=token,source_file='finite.parquet',source_sha256='a'*64,source_row=str(i))
                o=math.resolve_component(profile,name,'financial',code,p,[row] if available else [])
                o.update(component=name,id=code+'|'+name+'|'+p)
                return o
            original[name].append(obs('C0051626',not before))
            predecessor[name].append(obs('00360305',True))
    return original,predecessor,cad


class CaixaTransitionTests(unittest.TestCase):
    def bridge(self,original,predecessor,cad,period='202109',metric='R1',**kw):
        fn=getattr(universe,'bridge_caixa_transition',None)
        self.assertIsNotNone(fn,'Caixa reporting transition bridge is missing')
        return fn(original,predecessor,cad,period=period,metric=metric,**kw)

    def test_all_four_windows_keep_native_sources_and_exact_temporal_math(self):
        for period in CAIXA_DATES[4:]:
            for metric in ('R1','R2'):
                with self.subTest(period=period,metric=metric):
                    original,predecessor,cad=caixa_fixture(period,metric);saved=deepcopy((original,predecessor,cad))
                    before=math.evaluate_metric(metric,dict(period=period,components=original,financial_statement=True),'ttm')
                    self.assertEqual(before['status'],'binding_missing')
                    patched,proof=self.bridge(original,predecessor,cad,period,metric)
                    self.assertTrue(proof['released']);self.assertFalse(proof['constant_perimeter_certified'])
                    result=math.evaluate_metric(metric,dict(period=period,components=patched,financial_statement=True),'ttm')
                    self.assertEqual(result['status'],'ok')
                    # Independent genuine-quarter sum; constant stock fixture makes mean exact.
                    ll=patched['LL'];quarter_sum=Fraction()
                    for i in range(1,5):
                        quarter_sum+=Fraction(ll[i]['token'])-(Fraction(ll[i-1]['token']) if ll[i]['period'].endswith(('06','12')) else 0)
                    self.assertEqual(math._rational(result['value_fraction']),quarter_sum/(100 if metric=='R1' else 50))
                    for name,rows in patched.items():
                        for o in rows:
                            if o.get('reporting_transition'):
                                p=o['period'];native=next(x for x in predecessor[name] if x['period']==p)
                                self.assertEqual(o['sources'],native['sources']);self.assertEqual(o['binding'],native['binding'])
                                self.assertEqual(o['token'],native['token']);self.assertEqual(o['native_unit_key'],native['unit_key'])
                                self.assertEqual(tuple(o['unit_key']),('financial','2','C0051626'))
                    self.assertEqual((original,predecessor,cad),saved)
                    self.assertEqual(len(proof['replacements']),8 if period=='202109' else 5 if period=='202112' else 4 if period=='202203' else 1)

    def test_rejects_other_targets_and_incompatible_or_missing_predecessor(self):
        for case in ('period','metric','horizon','leader','cad_missing','cad_duplicate','new_member','prudential_conflict','source_unit','source_context','source_null','source_definition','group_preexisting'):
            original,predecessor,cad=caixa_fixture();kw={}
            if case=='period':kw['period']='202209'
            elif case=='metric':kw['metric']='C1'
            elif case=='horizon':kw['horizon']='quarter'
            elif case=='leader':cad[-1]['CnpjInstituicaoLider']='OTHER'
            elif case=='cad_missing':cad.pop()
            elif case=='cad_duplicate':cad.append(deepcopy(cad[0]))
            elif case=='new_member':cad.append(dict(cad[-1],CodInst='OTHER'))
            elif case=='prudential_conflict':cad.append(dict(cad[-1],CodInst='C0080738',CnpjInstituicaoLider='OTHER'))
            elif case=='source_unit':predecessor['AT'][0]['unit_key']=('individual','3','00360305')
            elif case=='source_context':predecessor['AT'][0]['binding']['literal_context']['Conta']='OTHER'
            elif case=='source_null':predecessor['AT'][0]['token']=None
            elif case=='source_definition':predecessor['AT'][0]['definition_id']='OTHER'
            elif case=='group_preexisting':original['AT'][0]=deepcopy(predecessor['AT'][0]);original['AT'][0]['unit_key']=('financial','2','C0051626')
            with self.subTest(case=case):
                patched,proof=self.bridge(original,predecessor,cad,**kw)
                self.assertFalse(proof['released']);self.assertEqual(patched,original)

    def test_unused_opening_profit_is_not_an_added_requirement(self):
        original,predecessor,cad=caixa_fixture('202206')
        predecessor['LL'][0]['token']=None
        patched,proof=self.bridge(original,predecessor,cad,'202206')
        self.assertTrue(proof['released']);self.assertEqual(len(proof['replacements']),1)
        self.assertIsNone(patched['LL'][0]['token'])
        self.assertEqual(math.evaluate_metric('R1',dict(period='202206',components=patched,financial_statement=True),'ttm')['status'],'ok')

    def test_transition_does_not_fill_a_null_after_the_cut(self):
        original,predecessor,cad=caixa_fixture()
        original['AT'][-1]['token']=None
        patched,proof=self.bridge(original,predecessor,cad)
        self.assertTrue(proof['released']);self.assertIsNone(patched['AT'][-1]['token'])
        self.assertEqual(math.evaluate_metric('R1',dict(period='202109',components=patched,financial_statement=True),'ttm')['status'],'native_null')

    def test_authenticated_runner_returns_only_eight_targets_and_day_weighted_stocks(self):
        import duckdb
        from datetime import date
        import calendar
        from bank_quality.ifdata_odata import COLUMNS,CONTRACT
        from bank_quality.ifdata_cadastro import FIELDS,CONTRACT as CAD_CONTRACT
        fn=getattr(universe,'recalculate_caixa_transition',None)
        self.assertIsNotNone(fn,'Caixa bounded runner is missing')
        profile=universe.load_profile();digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);base=root/'base';native=root/'native';cadroot=root/'cadastro'
            for p in (base,native,cadroot):p.mkdir()
            native_files=[];cad_files=[];units=[]
            at={};pl={};profit={}
            with duckdb.connect() as conn:
                for i,p in enumerate(CAIXA_DATES):
                    before=p<'202109';code='00360305' if before else 'C0051626';rows=[]
                    at[p]=100+7*i;pl[p]=50+3*i;profit[p]=[5,12,7,18,10,22,9,20][i]
                    for name,token in [('LL',profit[p]),('AT',at[p]),('PL',pl[p])]:
                        ctx=next(c for c in profile['contexts'] if c['component']==name and c['literal_context']['dataset']=='financial' and p in c['periods'])
                        row={k:v for k,v in ctx['literal_context'].items() if k!='dataset'}
                        row.update(CodInst=code,AnoMes=p,Saldo=str(token),source_file='raw.json',source_sha256='a'*64,source_row=str(i))
                        rows.append(row)
                    conn.execute('create or replace table n('+','.join('"'+x+'" varchar' for x in COLUMNS)+')')
                    conn.executemany('insert into n values ('+','.join('?' for _ in COLUMNS)+')',[[r.get(x) for x in COLUMNS] for r in rows])
                    part=native/(p+'.parquet');conn.execute('copy n to ? (format parquet)',[str(part)])
                    native_files.append(dict(file=part.name,period=int(p),type=2,rows=3,sha256=digest(part)))
                    cadres=[dict(Data=p,CodInst='00360305',CnpjInstituicaoLider='00360305',CodConglomeradoFinanceiro=None if before else 'C0051626')]
                    if not before:
                        cadres.extend(dict(Data=p,CodInst=k,CnpjInstituicaoLider='00360305',CodConglomeradoFinanceiro='C0051626') for k in ('C0051626','42040639','C0080738'))
                        uid='financial|2|C0051626|'+p
                        units.append(dict(id=uid,unit_id=uid,period=p,dataset='financial',code='C0051626',membership='remaining',companies=[],classifications=dict(Tcb='B1',Td='C',Tc='1'),own_cadastro=cadres[1]))
                    conn.execute('create or replace table c('+','.join('"'+x+'" varchar' for x in FIELDS)+')')
                    conn.executemany('insert into c values ('+','.join('?' for _ in FIELDS)+')',[[r.get(x) for x in FIELDS] for r in cadres])
                    part=cadroot/(p+'.parquet');conn.execute('copy c to ? (format parquet)',[str(part)])
                    cad_files.append(dict(file=part.name,period=int(p),rows=len(cadres),sha256=digest(part)))
            for directory,contract,files in ((native,CONTRACT,native_files),(cadroot,CAD_CONTRACT,cad_files)):
                (directory/'manifest.json').write_text(json.dumps(dict(contract=contract,files=files)),encoding='utf8')
            with (base/'unit_periods.csv').open('w',encoding='utf8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=['period','dataset','payload']);writer.writeheader()
                for u in units:writer.writerow(dict(period=u['period'],dataset='financial',payload=json.dumps(u)))
            m=dict(contract=universe.CONTRACT,stage='coverage-and-aggregation',profile_sha256=digest(universe.PROFILE_PATH),
                   inputs={k:dict(root=str(path),expected_manifest_sha256=digest(path/'manifest.json')) for k,path in [('financial',native),('cadastro',cadroot)]},
                   tables={'unit_periods':4},files=[dict(file='unit_periods.csv',rows=4,sha256=digest(base/'unit_periods.csv'))])
            (base/'manifest.json').write_text(json.dumps(m),encoding='utf8');pin=digest(base/'manifest.json')
            with self.assertRaises(ValueError):fn(base,'0'*64,root/'bad-pin')
            self.assertFalse((root/'bad-pin').exists())
            out=root/'result';manifest=fn(base,pin,out)
            results=json.loads((out/'results.json').read_text(encoding='utf8'))
            self.assertEqual(len(results),8);self.assertEqual({r['status'] for r in results},{'ok'})
            self.assertEqual({r['code'] for r in results},{'C0051626'})
            self.assertFalse((out/'aggregates.json').exists(),'A Caixa patch must not label Caixa alone as the system')
            self.assertEqual(sum(len(r['reporting_transition']['replacements']) for r in results),36)
            day=lambda p:date(int(p[:4]),int(p[4:]),calendar.monthrange(int(p[:4]),int(p[4:]))[1])
            for r in results:
                index=CAIXA_DATES.index(r['period']);ps=CAIXA_DATES[index-4:index+1];stocks=at if r['metric']=='R1' else pl
                numerator=sum(Fraction(profit[p])-(Fraction(profit[ps[j-1]]) if p.endswith(('06','12')) else 0) for j,p in enumerate(ps) if j)
                mean=sum(Fraction(stocks[a]+stocks[b],2)*(day(b)-day(a)).days for a,b in zip(ps,ps[1:]))/(day(ps[-1])-day(ps[0])).days
                self.assertEqual(math._rational(r['value_fraction']),numerator/mean)
            self.assertEqual(digest(base/'manifest.json'),pin)
            self.assertTrue(all(digest(out/e['file'])==e['sha256'] for e in manifest['files']))
            with self.assertRaises(FileExistsError):fn(base,pin,out)
            (cadroot/cad_files[0]['file']).write_bytes(b'corrupt')
            with self.assertRaises(ValueError):fn(base,pin,root/'bad-source')
            self.assertFalse((root/'bad-source').exists())


TERRA_DATES=('202312','202403','202406','202409','202412')

def terra_fixture(metric='R1'):
    profile=universe.compile_complement_profile(universe.load_profile(),complement_catalogue(),['financial','individual'])
    names=math.METRICS.get(metric,math.COMPLEMENT_METRICS.get(metric));original={};individual={}
    cad=[dict(Data=p,CodInst='03751794',CnpjInstituicaoLider='03751794',Td='I',CodConglomeradoFinanceiro=None,CodConglomeradoPrudencial='C0084514') for p in TERRA_DATES]
    for name in names:
        original[name]=[];individual[name]=[]
        for i,p in enumerate(TERRA_DATES):
            for ds,target in [('financial',original),('individual',individual)]:
                role=math.COMPONENT_NAMES[name]
                ctx=next(c for c in profile['contexts'] if c['component']==role and c['literal_context']['dataset']==ds and p in c['periods'])
                token=str([20,5,12,7,18][i]) if name in math.FLOW_COMPONENTS else '0' if name=='credit' else '50' if name=='PL' else '100'
                row={k:v for k,v in ctx['literal_context'].items() if k!='dataset'};row.update(CodInst='03751794',AnoMes=p,Saldo=token,source_file='fixture.parquet',source_sha256='a'*64,source_row=str(i))
                ob=math.resolve_component(profile,role,ds,'03751794',p,[row] if ds=='individual' or p=='202412' else [])
                ob.update(id=ds+'|'+name+'|'+p,component=name,dataset=ds,code='03751794',status=ob.get('status','ok'))
                target[name].append(ob)
    return profile,original,individual,cad

class TerraHistoryTests(unittest.TestCase):
    def bridge(self,profile,original,individual,cad,**kw):
        fn=getattr(universe,'bridge_terra_history',None);self.assertIsNotNone(fn,'Finite Terra history bridge missing')
        return fn(original,individual,cad,profile=profile,period=kw.pop('period','202412'),metric=kw.pop('metric','R1'),horizon=kw.pop('horizon','ttm'),**kw)

    def test_exact_quarter_and_ttm_preserve_native_identity_and_original(self):
        for horizon,expected in [('quarter',Fraction(11,100)),('ttm',Fraction(30,100))]:
            profile,original,individual,cad=terra_fixture();saved=deepcopy((original,individual,cad))
            patched,proof=self.bridge(profile,original,individual,cad,horizon=horizon)
            self.assertTrue(proof['released']);self.assertEqual(proof['rule'],'terra-individual-history-financial-202412-v1')
            result=math.evaluate_metric('R1',dict(period='202412',components=patched,financial_statement=True),horizon)
            self.assertEqual(result['status'],'ok');self.assertEqual(math._rational(result['value_fraction']),expected)
            self.assertEqual(patched['LL'][-1],original['LL'][-1]);self.assertEqual(patched['LL'][0],original['LL'][0])
            self.assertEqual(len(proof['replacements']),2 if horizon=='quarter' else 7)
            for rows in patched.values():
                for o in rows:
                    if o.get('reporting_transition'):
                        n=next(x for x in individual[o['component']] if x['period']==o['period'])
                        self.assertEqual(o['binding'],n['binding']);self.assertEqual(o['sources'],n['sources']);self.assertEqual(o['token'],n['token'])
                        self.assertEqual(o['native_unit_key'],n['unit_key']);self.assertEqual(o['native_definition_id'],n['definition_id']);self.assertEqual(tuple(o['unit_key']),('financial','2','03751794'))
            self.assertEqual((original,individual,cad),saved)

    def test_all_eight_metrics_and_zero_credit_are_not_fabricated_as_valid(self):
        for metric in ('R1','R2','Q2','E2-B','RS','E3','R4','R5'):
            for horizon in ('quarter','ttm'):
                profile,original,individual,cad=terra_fixture(metric)
                patched,proof=self.bridge(profile,original,individual,cad,metric=metric,horizon=horizon)
                self.assertTrue(proof['released'],(metric,horizon,proof))
                result=math.evaluate_metric(metric,dict(period='202412',components=patched,financial_statement=True),horizon)
                self.assertEqual(result['status'],'zero_denominator' if metric in ('Q2','R5') else 'ok')

    def test_rejects_bad_scope_cadastro_context_and_anchor_without_mutation(self):
        for case in ('period','horizon','group','leader','missing_cad','duplicate_cad','prudential','null_source','different_token','context','source_key','existing_history','anchor_null'):
            profile,original,individual,cad=terra_fixture();kw={}
            if case=='period':kw['period']='202409'
            elif case=='horizon':kw['horizon']='point'
            elif case=='group':cad[0]['CodConglomeradoFinanceiro']='COTHER'
            elif case=='leader':cad[0]['CnpjInstituicaoLider']='OTHER'
            elif case=='missing_cad':cad.pop(0)
            elif case=='duplicate_cad':cad.append(deepcopy(cad[0]))
            elif case=='prudential':cad[0]['CodConglomeradoPrudencial']='OTHER'
            elif case=='null_source':individual['AT'][0]['token']=None
            elif case=='different_token':individual['LL'][-1]['token']='999'
            elif case=='context':individual['AT'][0]['binding']['literal_context']['DescricaoColuna']='OTHER'
            elif case=='source_key':individual['AT'][0]['unit_key']=('individual','3','OTHER')
            elif case=='existing_history':original['AT'][0]['status']='ok';original['AT'][0]['token']='100'
            elif case=='anchor_null':original['LL'][-1]['token']=None
            saved=deepcopy(original);patched,proof=self.bridge(profile,original,individual,cad,**kw)
            self.assertFalse(proof['released'],case);self.assertEqual(patched,saved,case)

    def test_unused_opening_flow_is_not_a_new_requirement(self):
        profile,original,individual,cad=terra_fixture();individual['LL'][0]['token']=None
        patched,proof=self.bridge(profile,original,individual,cad)
        self.assertTrue(proof['released']);self.assertEqual(patched['LL'][0],original['LL'][0])

class TerraRunnerBoundaryTests(unittest.TestCase):
    def test_context_copy_replaces_only_selected_terra_rows_and_preserves_payloads(self):
        import duckdb
        fn=getattr(universe,'_terra_copy_context',None);self.assertIsNotNone(fn)
        with tempfile.TemporaryDirectory() as tmp,duckdb.connect() as conn:
            root=Path(tmp);base=root/'base.parquet';patch=root/'patch.parquet';out=root/'out.parquet'
            conn.execute("create table records(code varchar,dataset varchar,period varchar,metric varchar,horizon varchar,payload varchar)")
            conn.execute("insert into records values ('03751794','financial','202412','R1','ttm','old'),('OTHER','financial','202412','R1','ttm','exact other'),('03751794','financial','202409','R1','ttm','exact earlier')")
            conn.execute('copy records to $destination (format parquet)',{'destination':str(base)})
            conn.execute("copy (select code,dataset,period,metric,horizon,'new' as payload from records where payload='old') to $destination (format parquet)",{'destination':str(patch)})
            fn(conn,base,patch,out,unit_only=True)
            self.assertEqual(sorted(r[0] for r in conn.execute('select payload from read_parquet(?)',[str(out)]).fetchall()),['exact earlier','exact other','new'])

    def test_applied_origin_and_signature_describe_corrected_economic_fields(self):
        fn=getattr(universe,'_terra_applied_contribution',None);self.assertIsNotNone(fn)
        old=dict(id='old',status='binding_missing',origin={'kind':'baseline'},preservation={'signature_sha256':'old'})
        patch=deepcopy(old);patch.update(status='ok',value_fraction=math._fraction_field(Fraction(1,2)))
        row=fn(patch,Path('/patch'),'a'*64)
        self.assertEqual(row['prior_origin'],old['origin']);self.assertEqual(row['origin']['kind'],'corrections')
        self.assertEqual(row['origin']['expected_manifest_sha256'],'a'*64)
        self.assertEqual(row['preservation']['signature_sha256'],__import__('hashlib').sha256(universe._composition_result_signature(row).encode()).hexdigest())
        self.assertEqual(patch['origin'],old['origin']);self.assertEqual(patch['preservation']['signature_sha256'],'old')

    def test_nominal_gaps_only_block_when_included_in_analytical_scope(self):
        fn=getattr(universe,'_terra_require_admitted_company_coverage',None);self.assertIsNotNone(fn)
        nominal=[dict(status='missing_native_unit',analytical_included=False) for _ in range(23)]
        fn(nominal)
        with self.assertRaisesRegex(ValueError,'nominal company gaps'):
            fn(nominal+[dict(status='missing_native_unit',analytical_included=True)])
        fn([dict(status='ok',analytical_included=True)])

    def test_selective_composition_refuses_patch_from_another_composition(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);base=root/'base';base.mkdir();patch=root/'patch';patch.mkdir();out=root/'out'
            def save(path,value):
                payload=json.dumps(value).encode();(path/'manifest.json').write_bytes(payload)
                return hashlib.sha256(payload).hexdigest()
            pin=save(base,{'contract':universe.COMPOSITION_CONTRACT,'config':{}})
            pp=save(patch,{'contract':'ifdata-terra-history-analysis-v1','composition':{'root':str(base),'expected_manifest_sha256':'0'*64}})
            fn=getattr(universe,'apply_terra_history',None);self.assertIsNotNone(fn)
            with self.assertRaisesRegex(ValueError,'composition'):
                fn(base,pin,patch,pp,out)
            self.assertFalse(out.exists())

    def test_bad_composition_pin_refuses_before_output(self):
        fn=getattr(universe,'recalculate_terra_history',None);self.assertIsNotNone(fn,'Terra selective runner missing')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);base=root/'base';base.mkdir();(base/'manifest.json').write_text('{}',encoding='utf8');out=root/'out'
            with self.assertRaises(ValueError):fn(base,'0'*64,out)
            self.assertFalse(out.exists())

    def test_nested_source_destination_refuses_before_reading_or_writing(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);base=root/'composition';base.mkdir();protected=root/'membership';protected.mkdir()
            manifest={'contract':universe.COMPOSITION_CONTRACT,'config':{'membership':{'root':str(protected)}}}
            payload=json.dumps(manifest).encode();(base/'manifest.json').write_bytes(payload);out=protected/'terra-new'
            with self.assertRaisesRegex(ValueError,'overlaps source'):
                universe.recalculate_terra_history(base,hashlib.sha256(payload).hexdigest(),out)
            self.assertFalse(out.exists());self.assertEqual(list(protected.iterdir()),[])

    def test_existing_output_is_preserved(self):
        fn=getattr(universe,'recalculate_terra_history',None);self.assertIsNotNone(fn,'Terra selective runner missing')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);out=root/'out';out.mkdir();p=out/'accepted';p.write_bytes(b'keep')
            with self.assertRaises(FileExistsError):fn(root/'missing','0'*64,out)
            self.assertEqual(p.read_bytes(),b'keep')

if __name__=='__main__':unittest.main()

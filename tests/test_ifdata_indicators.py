import unittest
import json
import hashlib
import tempfile
from pathlib import Path
import duckdb
from bank_quality.ifdata_indicators import calculate, evaluate_unit

class ArithmeticTests(unittest.TestCase):
    def test_literal_components_and_precision(self):
        r=calculate('1.00','8.0')
        self.assertEqual(r['value'],'0.125')
        self.assertEqual((r['numerator'],r['denominator']),('1.00','8.0'))
        self.assertEqual(len(calculate('1','3')['value'].split('.')[1]),100)
        self.assertEqual(calculate('10000000000000000000000000001','1')['value'],'10000000000000000000000000001')
    def test_missing_invalid_and_zero_are_explicit(self):
        for n,d,status in [(None,'1','missing_component'),('NI','1','invalid_numeric'),('NaN','1','invalid_numeric'),('1','0','zero_denominator'),(0.1,'1','invalid_numeric'),(True,'1','invalid_numeric')]:
            r=calculate(n,d)
            self.assertIsNone(r['value']); self.assertEqual(r['status'],status)
    def test_sign_is_preserved_not_normalized(self):
        self.assertEqual(calculate('-3','10')['value'],'-0.3')
        r=calculate('3','-10')
        self.assertEqual(r['value'],'-0.3'); self.assertTrue(r['negative_denominator'])

def cell(report,code,value,name=None,description=None):
    definitions={'78182':'[10000007] + [20000004]', '78186':'[60000002] + [70000009]+ [80000006]',
                 '78191':'[16000001]-[16900008]', '78192':'[16900008]', '78287':'[41000007]'}
    return dict(NumeroRelatorio=report,Conta=code,Saldo=value,NomeColuna=name or code,
                DescricaoColuna=description if description is not None else definitions.get(code,'definition'),Grupo='g',CodInst='00000123',AnoMes='202412',
                TipoInstituicao='3',NomeInstituicao='Teste',Td='I',cadastro_encontrado=True,
                source_file='input.json',source_sha256='a'*64,source_row=code)

def sourced_cell(report,code,value,position,**changes):
    row=cell(report,code,value)
    row.update(NomeRelatorio={'1':'Resumo','2':'Ativo','3':'Passivo','4':'DRE','5':'Capital'}[report],
               source_url='https://example.invalid/captured-page',
               source_collected_utc='2026-10-11T15:03:27+00:00',
               source_context='https://example.invalid/$metadata#_IfDataValores',
               source_row=str(position))
    row.update(changes)
    return row

class UnitTests(unittest.TestCase):
    def test_context_signed_ratios_and_pending_flows(self):
        rows=[cell('1','78182','100'),cell('1','78186','20'),cell('1','78187','5'),
              cell('2','78191','40'),cell('2','78192','-4'),cell('3','78287','80'),
              cell('4','78226','6'),cell('4','78208','10'),cell('4','78187','5')]
        result=evaluate_unit('individual',rows)
        by={(r['indicator'],r['method']):r for r in result}
        self.assertEqual(len(result),10)
        self.assertEqual(by['pl_ativo','nativo']['value'],'0.2')
        self.assertEqual(by['credito_depositos','nativo']['value'],'0.5')
        self.assertEqual(by['provisao_credito','nativo']['value'],'-0.1')
        for indicator in ('roe','roa'):
            for method in ('abertura_fechamento','media_trimestral'):
                r=by[indicator,method]
                self.assertEqual(r['status'],'window_unproven'); self.assertIsNone(r['value'])
        self.assertTrue(all(r['unit_class']=='individual' for r in result))
    def test_duplicate_binding_rejected_and_report_kept(self):
        rows=[cell('1','78182','100'),cell('2','78182','999'),cell('1','78186','20')]
        result=evaluate_unit('individual',rows)
        self.assertEqual(next(r for r in result if r['indicator']=='pl_ativo')['value'],'0.2')
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            evaluate_unit('individual',rows+[dict(rows[0],Saldo='101')])
    def test_classification_unknown_and_independent(self):
        for td,found,want in [('C',True,'conglomerado'),('I',True,'independente'),(None,False,'desconhecido')]:
            row=cell('1','78182','100');row.update(Td=td,cadastro_encontrado=found)
            row['TipoInstituicao']='2'
            self.assertEqual(evaluate_unit('financial',[row])[0]['unit_class'],want)
    def test_native_index_variants_are_separate_versions(self):
        first=cell('5','79664','0.15',name='IB (m)')
        first['TipoInstituicao']='1'
        second=dict(first,NomeColuna='IB (n)')
        a=evaluate_unit('capital',[first])[0];b=evaluate_unit('capital',[second])[0]
        self.assertEqual(a['value'],'0.15'); self.assertEqual(a['unit'],'escala_nativa')
        self.assertNotEqual(a['version'],b['version'])
        self.assertEqual(a['perspective'],'prudencial')
    def test_rejects_context_mismatch_and_preserves_individual_perspective(self):
        with self.assertRaisesRegex(ValueError,'mismatch'):
            evaluate_unit('capital',[cell('5','79664','0.15')])
        row=cell('1','78182','100'); row['Td']='C'
        r=evaluate_unit('individual',[row])[0]
        self.assertEqual(r['unit_class'],'individual'); self.assertEqual(r['consolidation_type'],'C')
    def test_unknown_definition_null_and_absent_binding(self):
        rows=[cell('1','78182','100',description='new unproved definition'),cell('1','78186','20')]
        result=evaluate_unit('individual',rows)
        self.assertEqual(next(r for r in result if r['indicator']=='pl_ativo')['status'],'definition_unproven')
        rows=[cell('1','78182','100'),cell('1','78186',None)]
        result=evaluate_unit('individual',rows)
        self.assertEqual(next(r for r in result if r['indicator']=='pl_ativo')['status'],'null_balance')
        self.assertEqual(next(r for r in result if r['indicator']=='credito_depositos')['status'],'binding_missing')
    def test_native_semester_means_and_margin(self):
        rows=[cell('1','78182','100'),cell('1','78186','20'),
              cell('1','78187','5',description='[70000009]+[80000006]-[81956001]'),
              cell('4','78226','6',description='Somatório do Resultado Operacional e do Resultado Não Operacional'),
              cell('4','78187','5',description='[70000009]+[80000006]-[81956001]'),
              cell('4','78208','10',description='Somatório de Rendas de Operações de Crédito, Rendas de Operações de Arrendamento Mercantil, Rendas de Operações com TVM, Rendas de Operações com Instrumentos Financeiros Derivativos, Resultado de Operações de Câmbio e Rendas de Aplicações Compulsórias')]
        history={}
        for period,at,pl in [('202406','80','10'),('202409','90','16'),('202412','100','20')]:
            for code,value in [('78182',at),('78186',pl)]:
                row=cell('1',code,value);row['AnoMes']=period
                history['00000123',period,code]=row
        result=evaluate_unit('individual',rows,history=history,native_windows=True)
        by={(r['indicator'],r['method']):r for r in result}
        self.assertEqual(by['margem_liquida','nativo']['value'],'0.5')
        self.assertEqual(by['roe','abertura_fechamento']['denominator'],'15')
        self.assertNotEqual(by['roe','abertura_fechamento']['value'],by['roe','media_trimestral']['value'])
        self.assertEqual(by['roe','media_trimestral']['window_months'],6)
        self.assertEqual(by['roe','media_trimestral']['window_start'],'2024-07-01')
        self.assertEqual(by['roe','media_trimestral']['window_end'],'2024-12-31')
        self.assertIn('media_trimestral',by['roe','media_trimestral']['formula'])
        self.assertIn('202409',by['roe','media_trimestral']['formula'])
        del history['00000123','202406','78186']
        result=evaluate_unit('individual',rows,history=history,native_windows=True)
        self.assertEqual(next(r for r in result if r['indicator']=='roe')['status'],'opening_stock_missing')
    def test_unknown_td_cannot_certify_an_average(self):
        from bank_quality.ifdata_indicators import _mean_status
        row=cell('1','78182','100'); row['Td']=None
        self.assertEqual(_mean_status([row],['202412'],row,('1','78182')),'opening_perimeter_unproven')
    def test_averages_reject_regime_crossing_and_duplicate_stock(self):
        from bank_quality.ifdata_indicators import _mean_status
        opening=cell('1','140220','80');opening['AnoMes']='202412'
        current=dict(opening,AnoMes='202503')
        self.assertEqual(_mean_status([opening,current],['202412','202503'],current,('1','140220')),
                         'opening_regime_incompatible')
        opening=cell('1','78182','80');opening['AnoMes']='202406'
        ambiguous=dict(opening,ambiguous_occurrences=[opening,dict(opening,Saldo='81')])
        self.assertEqual(_mean_status([ambiguous],['202406'],opening,('1','78182')),
                         'duplicate_stock_binding')
    def test_duplicate_occurrences_can_be_retained_without_calculation(self):
        rows=[cell('1','78182','100'),cell('1','78182','101'),cell('1','78186','20')]
        r=next(r for r in evaluate_unit('individual',rows,retain_ambiguity=True) if r['indicator']=='pl_ativo')
        self.assertEqual(r['status'],'duplicate_binding');self.assertIsNone(r['value'])
        self.assertEqual(len(json.loads(r['denominator_definition'])['ambiguous_occurrences']),2)

    def test_identical_source_occurrences_calculate_once_and_keep_all_positions(self):
        asset=sourced_cell('1','78182','100.00',3)
        rows=[asset,dict(asset,source_row='1'),dict(asset,source_row='2'),
              sourced_cell('1','78186','20.00',4)]
        r=next(r for r in evaluate_unit('individual',rows) if r['indicator']=='pl_ativo')
        self.assertEqual((r['status'],r['value']),('ok','0.2'))
        component=json.loads(r['denominator_definition'])
        self.assertEqual(component['Saldo'],'100.00')
        self.assertEqual(component['source_row'],'1')
        self.assertEqual([p['source_row'] for p in component['source_occurrences']],['1','2','3'])
        self.assertEqual(rows[0],asset)
        self.assertNotIn('source_occurrences',asset)

    def test_equal_amount_is_not_enough_to_resolve_a_duplicate(self):
        asset=sourced_cell('1','78182','100.00',1)
        for changes in [{'Saldo':'100.0'},{'Saldo':'101.00'},{'Grupo':'another'},
                        {'DescricaoColuna':'another'},{'NomeColuna':'another'},
                        {'NomeInstituicao':'another'},{'source_sha256':'b'*64},
                        {'source_file':'another.json'},{'source_row':'1'},
                        {'source_row':'invalid'},{'source_url':None}]:
            with self.subTest(changes=changes):
                other=dict(asset,source_row='2');other.update(changes)
                rows=[asset,other,sourced_cell('1','78186','20',3)]
                with self.assertRaisesRegex(ValueError,'Duplicate'):
                    evaluate_unit('individual',rows)
                r=next(r for r in evaluate_unit('individual',rows,retain_ambiguity=True)
                       if r['indicator']=='pl_ativo')
                self.assertEqual(r['status'],'duplicate_binding');self.assertIsNone(r['value'])

    def test_identical_null_occurrences_remain_null_and_a_later_conflict_stays_blocked(self):
        asset=sourced_cell('1','78182','100',1)
        equity=sourced_cell('1','78186',None,3)
        r=next(r for r in evaluate_unit('individual',[asset,equity,dict(equity,source_row='4')])
               if r['indicator']=='pl_ativo')
        self.assertEqual(r['status'],'null_balance');self.assertIsNone(r['value'])
        self.assertEqual(len(json.loads(r['numerator_definition'])['source_occurrences']),2)
        rows=[asset,dict(asset,source_row='2'),dict(asset,source_row='5',Saldo='101'),
              sourced_cell('1','78186','20',6)]
        r=next(r for r in evaluate_unit('individual',rows,retain_ambiguity=True)
               if r['indicator']=='pl_ativo')
        self.assertEqual(r['status'],'duplicate_binding');self.assertIsNone(r['value'])

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); self.values=self.root/'values'; self.cadastro=self.root/'cadastro'
        from bank_quality.ifdata_odata import COLUMNS, CONTRACT
        from bank_quality.ifdata_cadastro import FIELDS, CONTRACT as CADASTRO_CONTRACT
        for ds,typ in [('financial','2'),('individual','3'),('capital','1')]:
            rows=([cell('5','79664','0.15'),cell('5','79659',None)] if ds=='capital' else
                  [cell('1','78182','100'),cell('1','78186','20'),cell('2','78191','40'),cell('2','78192','-4'),cell('3','78287','80')])
            for r in rows:r['TipoInstituicao']=typ
            self.package(self.values/ds,COLUMNS,rows,CONTRACT)
        reg=dict.fromkeys(FIELDS);reg.update(CodInst='00000123',Data='202412',Td='I',NomeInstituicao='Teste </script>')
        self.package(self.cadastro,FIELDS,[reg],CADASTRO_CONTRACT)
        self.out=self.root/'pilot'
    def package(self,root,columns,rows,contract):
        root.mkdir(parents=True)
        with duckdb.connect() as c:
            c.execute('create table t ('+','.join('"'+k+'" varchar' for k in columns)+')')
            c.executemany('insert into t values ('+','.join('?' for _ in columns)+')',[[r.get(k) for k in columns] for r in rows])
            c.execute('copy t to ? (format parquet)',[str(root/'part.parquet')])
        part=dict(file='part.parquet',sha256=hashlib.sha256((root/'part.parquet').read_bytes()).hexdigest(),rows=len(rows))
        (root/'manifest.json').write_text(json.dumps(dict(contract=contract,files=[part],rows=len(rows))),encoding='utf-8')
    def test_build_query_export_and_integrity(self):
        from bank_quality.ifdata_indicators import build_pilot, open_pilot
        manifest=build_pilot(self.values,self.cadastro,self.out,periods=['202412'])
        self.assertEqual(manifest['rows'],22)
        with open_pilot(self.out) as c:
            self.assertEqual(c.execute("select value from results where dataset='individual' and indicator='pl_ativo'").fetchone()[0],'0.2')
            self.assertEqual(c.execute('select count(*) from wide').fetchone()[0],3)
            self.assertEqual(c.execute("select n_valid from statistics where dataset='individual' and indicator='pl_ativo'").fetchone()[0],1)
        self.assertTrue((self.out/'results.csv').exists())
        html=(self.out/'painel.html').read_text(encoding='utf-8')
        self.assertNotIn('Teste </script>',html)
        self.assertIn('window_unproven',html)
        with self.assertRaises(FileExistsError):build_pilot(self.values,self.cadastro,self.out)
        (self.out/manifest['files'][0]['file']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'hash'):open_pilot(self.out)
    def test_rejects_missing_and_duplicate_periods(self):
        from bank_quality.ifdata_indicators import build_pilot
        for periods in (['202412','202412'],['199912']):
            with self.assertRaises(ValueError):build_pilot(self.values,self.cadastro,self.root/('bad'+str(len(periods))),periods)
    def test_cli_query_utf8_and_reject_write(self):
        import subprocess
        import sys
        from bank_quality.ifdata_indicators import build_pilot
        build_pilot(self.values,self.cadastro,self.out)
        command=[sys.executable,'-B',str(Path(__file__).resolve().parents[1]/'scripts/pilot-ifdata-indicators.py'),'query',str(self.out)]
        result=subprocess.run(command+["select distinct name from results"],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout.decode('utf-8')),[{'name':'Teste </script>'}])
        result=subprocess.run(command+['delete from results'],capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'single SELECT',result.stderr)
    def test_units_without_candidate_accounts_are_visible(self):
        from bank_quality.ifdata_indicators import build_pilot,open_pilot
        from bank_quality.ifdata_odata import COLUMNS, CONTRACT
        other=cell('2','999999','1');other['CodInst']='99999999'
        self.package(self.values/'individual_extra',COLUMNS,[other],CONTRACT)
        part=self.values/'individual_extra'/'part.parquet'
        target=self.values/'individual'/'extra.parquet';target.write_bytes(part.read_bytes())
        m=json.loads((self.values/'individual'/'manifest.json').read_text())
        m['files'].append(dict(file='extra.parquet',sha256=hashlib.sha256(target.read_bytes()).hexdigest(),rows=1));m['rows']+=1
        (self.values/'individual'/'manifest.json').write_text(json.dumps(m))
        build_pilot(self.values,self.cadastro,self.out)
        with open_pilot(self.out) as c:
            self.assertEqual(c.execute("select count(*) from results where code='99999999'").fetchone()[0],10)

    def test_repeated_september_stock_is_used_once_in_december_mean(self):
        from bank_quality.ifdata_indicators import build_pilot,open_pilot
        from bank_quality.ifdata_odata import COLUMNS,CONTRACT
        from bank_quality.ifdata_cadastro import FIELDS,CONTRACT as CADASTRO_CONTRACT
        rows=[]
        for period,asset,equity,copies in [('202506','80','10',1),('202509','90','16',3),('202512','100','20',1)]:
            for code,value,definition in [('140220',asset,'[1000000009] + [2000000008]'),
                                          ('140246',equity,'[6000000004]+ [7000000003]+ [8000000002]')]:
                for _ in range(copies):
                    rows.append(sourced_cell('1',code,value,len(rows)+1,AnoMes=period,DescricaoColuna=definition))
        rows.append(sourced_cell('1','141870','5',len(rows)+1,AnoMes='202512',
                                DescricaoColuna='[7000000003] + [8000000002] - [8195600001]'))
        values=self.root/'duplicate-values'
        for dataset in ('financial','capital'):
            source=self.values/dataset;target=values/dataset;target.mkdir(parents=True)
            for path in source.iterdir():(target/path.name).write_bytes(path.read_bytes())
        self.package(values/'individual',COLUMNS,rows,CONTRACT)
        cadastro=self.root/'duplicate-cadastro';register=[]
        for period in ('202506','202509','202512'):
            row=dict.fromkeys(FIELDS);row.update(CodInst='00000123',Data=period,Td='I',NomeInstituicao='Teste')
            register.append(row)
        self.package(cadastro,FIELDS,register,CADASTRO_CONTRACT)
        output=self.root/'duplicate-pilot'
        manifest=build_pilot(values,cadastro,output,periods=['202512'])
        with open_pilot(output) as conn:
            status,denominator,inputs=conn.execute("select status,denominator,mean_stock_inputs from results where indicator='roe' and method='media_trimestral'").fetchone()
        self.assertEqual(status,'ok')
        self.assertEqual(manifest['duplicate_policy'],'identical-native-rows-same-source-v1')
        self.assertTrue(denominator.startswith('15.3333333333333333333333333333'))
        september=json.loads(inputs)[1]
        self.assertEqual(september['Saldo'],'16')
        self.assertEqual(len(september['source_occurrences']),3)

if __name__=='__main__': unittest.main()

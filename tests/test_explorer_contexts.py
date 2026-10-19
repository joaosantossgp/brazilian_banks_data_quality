"""Exact descriptive context sums; no indicator construction or company inference."""
import importlib.util
from pathlib import Path
import unittest
import shutil,subprocess
SPEC=importlib.util.spec_from_file_location('contexts',Path(__file__).resolve().parents[1]/'scripts/ifdata-explorer-contexts.py')
class ContextTests(unittest.TestCase):
 def load(self):
  self.assertTrue(SPEC.origin and Path(SPEC.origin).is_file(),'Context presentation implementation absent')
  m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m);return m
 def row(self,code,token,**kw):
  return dict(AnoMes='202412',CodInst=code,NumeroRelatorio='8',NomeRelatorio='Risco',Grupo=None,Conta='AA',NomeColuna='AA',DescricaoColuna='Saldo AA',Saldo=token,**kw)
 def test_exact_null_zero_negative_and_unidentified(self):
  m=self.load();members={('202412','01'):('remaining','B1'),('202412','02'):('sample','N2'),('202412','03'):('unknown',None)}
  data=m.summarize([self.row('01','12345678901234567890.01'),self.row('02','0'),self.row('03',None),self.row(None,'999'),self.row('04','-0.01')],members,'credit')
  self.assertEqual(data['unidentified_rows'],1);self.assertEqual(data['unmatched_rows'],1)
  vals={tuple(r[:4]):r for r in data['rows']}
  self.assertEqual(vals[('202412','remaining','B1',0)][4],['1234567890123456789001','100'])
  self.assertEqual(vals[('202412','sample','N2',0)][4],['0','1'])
  self.assertIsNone(vals[('202412','unknown',None,0)][4]);self.assertEqual(vals[('202412','unknown',None,0)][6],{'native_null':1})
 def test_contexts_and_duplicates_not_coalesced(self):
  m=self.load();memb={('202412','01'):('remaining','B1')};a=self.row('01','1');b=dict(a,DescricaoColuna='Outra definição',Saldo='2')
  data=m.summarize([a,b],memb,'credit');self.assertEqual(len(data['catalog']),2)
  with self.assertRaisesRegex(ValueError,'Duplicate'):m.summarize([a,a],memb,'credit')
 def test_non_numeric_states_and_negative_preserved(self):
  m=self.load();members={('202412',str(i)):('remaining','B4') for i in range(5)}
  d=m.summarize([self.row(str(i),v) for i,v in enumerate(['','NA','NI','-2.50','0'])],members,'credit');r=d['rows'][0]
  self.assertEqual(r[4],['-5','2']);self.assertEqual(r[5],2);self.assertEqual(r[7],1);self.assertEqual(r[6],{'native_empty':1,'native_NA':1,'native_NI':1})



 def test_joint_dimensions_keep_control_and_sr_origins_separate(self):
  m=self.load();self.assertTrue(hasattr(m,'unit_dimensions'),'Dated joint dimensions absent')
  base={'period':'202412','own_cadastro':{'Data':'202412'},'classifications':{'Tcb':'B1','Tc':'1','Td':'C','SegmentoTb':'Banco','Sr':None,'SrAnalitico':'S2'},'sr_analytic_status':'derived'}
  dims=m.unit_dimensions(base);self.assertEqual(dims['Sr'],{'state':'null','value':None});self.assertEqual(dims['SrAnalitico'],{'state':'value','value':'S2'})
  other=m.unit_dimensions(dict(base,classifications=dict(base['classifications'],Tc='2')))
  data=m.summarize([self.row('01','1'),self.row('02','2')],{('202412','01'):('remaining','B1',dims),('202412','02'):('remaining','B1',other)},'credit')
  self.assertEqual(len(data['rows']),2);self.assertEqual(data['rows'][0][8],dims)
  conflict=m.unit_dimensions(dict(base,sr_analytic_status='conflict'));self.assertEqual(conflict['SrAnalitico'],{'state':'conflict','value':None})
  before=m.unit_dimensions(dict(base,sr_analytic_status='before_regime'));self.assertEqual(before['SrAnalitico']['state'],'before_regime')

 def test_dimension_interning_preserves_exact_cells(self):
  m=self.load();self.assertTrue(hasattr(m,'compact_dimensions'),'Repeated dimensions not compacted')
  dims={'Tcb':{'state':'value','value':'B1'}};data={'balance':{'rows':[['202412','sample','B1',0,['1','3'],1,{},0,dims],['202403','sample','B1',0,['2','3'],1,{},0,dims]]},'credit':{'rows':[]}}
  result=m.compact_dimensions(data);self.assertEqual(len(result['balance']['dimension_dictionary']),1)
  for r in result['balance']['rows']:self.assertEqual(result['balance']['dimension_dictionary'][r[8]],dims)
  self.assertEqual(result['balance']['rows'][0][4],['1','3'])

 def test_export_context_pin_cannot_drift_from_indicators(self):
  import tempfile,json,hashlib
  sp=importlib.util.spec_from_file_location('exporter',Path(__file__).resolve().parents[1]/'scripts/export-ifdata-explorer.py');e=importlib.util.module_from_spec(sp);sp.loader.exec_module(e)
  self.assertTrue(hasattr(e,'presentation_contexts'),'Context pin boundary absent')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'c.json';p.write_text(json.dumps({'composition_manifest':'a'*64,'dimension_scope':['Tcb','membership'],'perspective':'financial','balance':{'catalog':[],'rows':[]},'credit':{'catalog':[],'rows':[]}}));pin=hashlib.sha256(p.read_bytes()).hexdigest()
   self.assertEqual(e.presentation_contexts(p,pin,'a'*64)['perspective'],'financial')
   with self.assertRaisesRegex(ValueError,'composition'):e.presentation_contexts(p,pin,'b'*64)
   with self.assertRaisesRegex(ValueError,'hash'):e.presentation_contexts(p,'0'*64,'a'*64)

 @unittest.skipUnless(shutil.which('node'),'Node unavailable')
 def test_browser_context_filtering_and_exact_total(self):
  template=(Path(__file__).resolve().parents[1]/'scripts/ifdata-explorer-template.html').read_text(encoding='utf8')
  code=template.split('</script><script>')[1].split('(async()=>{try{const bytes')[0]
  probe="""
const assert=require('node:assert/strict');
const c={rows:[['202412','sample','B1',0,['1','10'],1,{},0],['202412','remaining','B1',0,['2','10'],1,{},0],['202412','unknown',null,0,null,0,{native_null:1},0],['202412','remaining','N1',1,['100','1'],1,{},0]]};
assert.equal(typeof contextPoints,'function');
const all=contextPoints(c,0,'','total',['202412']);
assert.deepEqual(all[0].value,['3','10']);assert.equal(all[0].known,2);assert.equal(all[0].missing,1);
const b=contextPoints(c,0,JSON.stringify(['value','B1']),'sample',['202412']);assert.deepEqual(b[0].value,['1','10']);
assert.equal(contextPoints(c,0,JSON.stringify(['unknown',null]),'total',['202412'])[0].value,null);
const j={rows:[['202412','remaining','B1',0,['1','1'],1,{},0,{Tcb:{state:'value',value:'B1'},Tc:{state:'value',value:'1'},Sr:{state:'null',value:null},SrAnalitico:{state:'value',value:'S2'}}],['202412','remaining','B1',0,['2','1'],1,{},0,{Tcb:{state:'value',value:'B1'},Tc:{state:'value',value:'2'},Sr:{state:'value',value:'S2'},SrAnalitico:{state:'value',value:'S2'}}]]};
const f={Tc:JSON.stringify(['value','1']),SrAnalitico:JSON.stringify(['value','S2'])};
assert.deepEqual(contextPoints(j,0,'','total',['202412'],f)[0].value,['1','1']);
const compact={dimension_dictionary:j.rows.map(r=>r[8]),rows:j.rows.map((r,i)=>[...r.slice(0,8),i])};assert.deepEqual(contextPoints(compact,0,'','total',['202412'],f),contextPoints(j,0,'','total',['202412'],f));
assert.equal(contextPoints(j,0,'','total',['202412'],{...f,Sr:JSON.stringify(['value','S2'])})[0].value,null);

"""
  result=subprocess.run(['node','-'],input=code+probe,text=True,encoding='utf8',capture_output=True)
  self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()

"""Presentation metadata respects authenticated contexts and observed perspectives."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import shutil
import subprocess

spec=importlib.util.spec_from_file_location('tcb_export',Path(__file__).resolve().parents[1]/'scripts/export-ifdata-explorer.py')
exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)

class TcbPresentationTests(unittest.TestCase):
    def context(self,component='AT',period='202412',dataset='financial',definition='stock'):
        literal=dict(dataset=dataset,TipoInstituicao='2',NumeroRelatorio='1',NomeRelatorio='Resumo',Conta='78182',NomeColuna='Ativo Total',DescricaoColuna='[10000007] + [20000004]',Grupo=None)
        return dict(component=component,literal_context=literal,context_sha256=hashlib.sha256(json.dumps(literal,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),periods=[period],compatibility=definition,window_rule='stock',sign_rule='native_signed_no_abs')

    def test_adopted_names_formulas_and_observed_perspective(self):
        ids={'L1','PL_DEP','R3','RIF_AT','E2-W','E2-WP','QL'}
        self.assertTrue(ids<=exporter.METRIC_INFO.keys())
        self.assertTrue(ids<=exporter.FORMULAS.keys())
        contexts=[self.context('cash'),self.context('sight_deposits')]
        result=exporter.method_catalog([({'contexts':contexts},['L1'],'a'*64)],{'L1':['financial']})
        self.assertEqual(result['L1']['datasets'],['financial'])
        self.assertEqual({c['role'] for c in result['L1']['components']},{'cash','sight_deposits'})
        self.assertTrue(result['L1']['sources'])

    def test_adequacy_classifies_conditions_without_excluding_tcb(self):
        result=exporter.method_catalog([({'contexts':[]},['QL','L1','R1'],'a'*64)],{'QL':['financial'],'L1':['financial'],'R1':['financial']})
        self.assertEqual(result['QL']['kind'],'Específico: recebíveis de arrendamento')
        self.assertEqual(result['L1']['kind'],'Condicional: financiamento por depósitos')
        self.assertEqual(result['R1']['kind'],'Comum: descrição contábil')
        self.assertIn('não se restringe a N1',result['QL']['condition'])
        self.assertNotIn('excluded_tcb',result['QL'])

    def test_context_identity_deduplication_and_definition_boundaries(self):
        old=self.context('LL','201812',definition='old');new=self.context('LL','201903',definition='new')
        result=exporter.method_catalog([({'contexts':[old,old,new]},['R3'],'a'*64)],{'R3':['financial']})
        ll=next(c for c in result['R3']['components'] if c['role']=='LL')
        self.assertEqual(len(ll['bindings']),2)
        self.assertEqual([b['periods'] for b in ll['bindings']],[['201812'],['201903']])
        self.assertEqual(ll['bindings'][0]['literal_context']['Conta'],'78182')

    def test_corrupt_literal_context_is_rejected(self):
        context=self.context();context['literal_context']['Conta']='999'
        with self.assertRaisesRegex(ValueError,'context'):
            exporter.method_catalog([({'contexts':[context]},['RIF_AT'],'a'*64)],{'RIF_AT':['financial']})

    def test_membership_retention_wrapper_preserves_terra_ancestry(self):
        terra={'contract':'ifdata-composed-analysis-v1','derivation':{'rule':'terra-individual-history-financial-202412-v1'}}
        wrapper={'contract':'ifdata-composed-analysis-v1','derivation':{'rule':'retained_accepted_membership_provenance_v1','composition':{'root':'parent','expected_manifest_sha256':'a'*64}}}
        self.assertEqual(exporter.prior_correction_derivation(wrapper,lambda root,pin:terra),terra['derivation'])
        with self.assertRaisesRegex(ValueError,'Cyclic'):
            exporter.prior_correction_derivation(wrapper,lambda root,pin:wrapper)

    def test_complement_profile_authenticates_consumed_file_and_legacy_pin(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); profile={'legacy_profile_sha256':'b'*64,'contexts':[self.context()]}
            path=root/'complement-contexts.json';path.write_text(json.dumps(profile),encoding='utf-8')
            pin=exporter.math._digest_file(path)
            manifest={'contexts_file':path.name,'profile_sha256':'c'*64,'files':[{'file':path.name,'sha256':pin}]}
            def authenticate(p,h):
                if exporter.math._digest_file(p)!=h:raise ValueError('hash')
            self.assertEqual(exporter.presentation_profile(root,manifest,authenticate,'c'*64,'b'*64),profile)
            manifest['profile_sha256']='d'*64
            with self.assertRaisesRegex(ValueError,'profile'):
                exporter.presentation_profile(root,manifest,authenticate,'c'*64,'b'*64)
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError,'hash'):
                exporter.presentation_profile(root,manifest,authenticate,'c'*64,'b'*64)

    @unittest.skipUnless(shutil.which('node'),'Node not installed')
    def test_method_card_filters_binding_date_and_perspective_and_escapes_sources(self):
        template=Path(exporter.__file__).with_name('ifdata-explorer-template.html').read_text(encoding='utf-8')
        code=template.split('</script><script>')[1].split('(async()=>{try{const bytes')[0]
        binding=self.context();binding['literal_context']['NomeColuna']='<script>danger</script>'
        other=self.context(period='201812');other['literal_context']['Conta']='OLD'
        method=dict(components=[dict(role='AT',label='Ativo total',bindings=[binding,other])],sources=[dict(label='<fonte>',url='https://example.org/?a=1&b=2')],scope_note='condicional')
        probe="const assert=require('node:assert/strict');const html=methodHTML("+json.dumps(method)+",'financial','202412');assert.ok(html.includes('&lt;script&gt;danger&lt;/script&gt;'));assert.ok(html.includes('78182'));assert.ok(!html.includes('OLD'));assert.ok(html.includes('&lt;fonte&gt;'));assert.ok(methodHTML("+json.dumps(method)+",'capital','202412').includes('Sem contexto literal'));"
        result=subprocess.run(['node','-'],input=code+probe,text=True,encoding='utf-8',capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()

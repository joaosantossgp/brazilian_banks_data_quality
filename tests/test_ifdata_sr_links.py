"""Dated SR attribution preserves observations, gaps and conflicting labels."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

from bank_quality import ifdata_cadastro as cadastro


def evidence(sr='S4',code='MEMBER',parent='PRU',period='202412',kind='financial_members'):
    return dict(dataset='financial',code='GROUP',period=period,link_kind=kind,
                evidence_code=code,evidence_sr=sr,evidence_parent=parent,
                source_file='json/'+period+'.json',source_sha256='a'*64,source_row='1')


class SrLinksTests(unittest.TestCase):
    def derive(self,original,rows,**changes):
        options=dict(dataset='financial',code='GROUP',period='202412');options.update(changes)
        self.assertTrue(hasattr(cadastro,'derive_sr_by_links'),'Dated SR helper is missing')
        return cadastro.derive_sr_by_links(original,rows,**options)

    def test_original_has_priority_and_input_is_immutable(self):
        rows=[evidence()];before=deepcopy(rows)
        result=self.derive('S1',rows)
        self.assertEqual(result['sr_original'],'S1');self.assertEqual(result['sr_analitico'],'S1')
        self.assertEqual(result['method'],'native');self.assertEqual(rows,before)

    def test_unique_label_and_parent_releases_with_null_members_explicit(self):
        rows=[evidence(),evidence(None,code='SECOND')];before=deepcopy(rows)
        result=self.derive(None,rows)
        self.assertIsNone(result['sr_original']);self.assertEqual(result['sr_vinculo'],'S4')
        self.assertEqual(result['sr_analitico'],'S4');self.assertEqual(result['method'],'dated_link')
        self.assertEqual((result['linked_records'],result['records_with_sr']),(2,1))
        self.assertEqual(result['evidence'],before);self.assertEqual(rows,before)

    def test_conflict_has_no_effective_classification(self):
        r=self.derive(None,[evidence(),evidence('S3',code='SECOND')])
        self.assertEqual(r['status'],'conflict');self.assertEqual(r['labels'],['S3','S4'])
        self.assertIsNone(r['sr_vinculo']);self.assertIsNone(r['sr_analitico'])

    def test_parent_ambiguity_and_missing_parent_do_not_release(self):
        for rows in ([evidence(),evidence(code='SECOND',parent='OTHER')],[evidence(parent=None)]):
            self.assertEqual(self.derive(None,rows)['status'],'unproven_perimeter')

    def test_no_label_and_unrecognized_labels_are_not_imputed(self):
        for rows in ([],[evidence(None)],[evidence('')]):
            r=self.derive(None,rows);self.assertEqual(r['status'],'unknown');self.assertIsNone(r['sr_analitico'])
        self.assertEqual(self.derive(None,[evidence('S6')])['status'],'unrecognized_label')

    def test_pre2017_is_not_backfilled(self):
        r=self.derive(None,[evidence(period='201612')],period='201612')
        self.assertEqual(r['status'],'before_regime');self.assertIsNone(r['sr_vinculo'])

    def test_identity_duplicate_and_unproven_source_are_rejected(self):
        for change,value in [('dataset','individual'),('period','202409'),('code','OTHER'),
                             ('link_kind','name_match'),('source_sha256',''),('evidence_code','GROUP')]:
            row=evidence();row[change]=value
            with self.subTest(change=change),self.assertRaises(ValueError):self.derive(None,[row])
        with self.assertRaises(ValueError):self.derive(None,[evidence(),evidence()])

    def test_prudential_member_must_point_to_target_group(self):
        row=evidence(parent='OTHER',kind='prudential_members');row['dataset']='capital'
        self.assertEqual(self.derive(None,[row],dataset='capital')['status'],'unproven_perimeter')
        row['evidence_parent']='GROUP'
        self.assertEqual(self.derive(None,[row],dataset='capital')['sr_vinculo'],'S4')


class SrProjectionTests(unittest.TestCase):
    def test_requested_regroup_contexts_do_not_expand_to_the_full_history(self):
        path=Path(__file__).resolve().parents[1]/'scripts/classify-ifdata-sr.py'
        spec=importlib.util.spec_from_file_location('classify_sr',path);cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
        self.assertTrue(hasattr(cli,'choose_sr_contexts'),'Selective regroup context guard missing')
        changes={('financial','201903','A'):{},('financial','201906','B'):{},('capital','201903','C'):{}}
        self.assertEqual(cli.choose_sr_contexts(changes),[('capital','201903'),('financial','201903'),('financial','201906')])
        target=[('financial','201903','R2','ttm')]
        self.assertEqual(cli.choose_sr_contexts(changes,target),[('financial','201903')])
        for bad in (target*2,[('financial','201912','R2','ttm')],[('financial','201903','made_up','ttm')]):
            with self.assertRaises(ValueError):cli.choose_sr_contexts(changes,bad)

    def test_only_new_classification_and_explanatory_flags_change(self):
        path=Path(__file__).resolve().parents[1]/'scripts/classify-ifdata-sr.py'
        spec=importlib.util.spec_from_file_location('classify_sr',path);cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
        self.assertTrue(hasattr(cli,'apply_sr_attribute'),'Analytical projection helper missing')
        row=dict(period='202412',dataset='financial',code='GROUP',unit_id='financial|2|GROUP|202412',
                 target_cadastro=dict(Data='202412',Sr=None,Tcb='B1',SegmentoTb=None),flags=[],
                 value_fraction={'numerator':'1','denominator':'10'},numerator_fraction={'numerator':'1','denominator':'1'},
                 denominator_fraction={'numerator':'10','denominator':'1'})
        attr=dict(dataset='financial',code='GROUP',period='202412',unit_id=row['unit_id'],
                  sr_analitico='S4',sr_original=None,status='derived',method='dated_link')
        original=deepcopy(row);result=cli.apply_sr_attribute(row,attr)
        self.assertEqual(row,original);self.assertIsNone(result['target_cadastro']['Sr'])
        self.assertEqual(result['target_cadastro']['SrAnalitico'],'S4')
        for k in ('value_fraction','numerator_fraction','denominator_fraction'):self.assertEqual(result[k],row[k])
        attr.update(status='conflict',sr_analitico=None)
        result=cli.apply_sr_attribute(row,attr)
        self.assertEqual(result['classification_states']['SrAnalitico'],'conflict')
        attr['period']='202409'
        with self.assertRaises(ValueError):cli.apply_sr_attribute(row,attr)


if __name__=='__main__':unittest.main()

import csv
import tempfile
import unittest
from pathlib import Path
from bank_quality.inventory import classify, inventory


def row(period, code, account, name, value):
    return {'AnoMes':str(period),'TipoInstituicao':3,'CodInst':code,'Conta':account,'NomeColuna':name,'Saldo':value,'NomeRelatorio':'Resumo','Grupo':'1'}


class InventoryTests(unittest.TestCase):
    def test_csv_formatting_evidence_survives_inventory(self):
        value=row(201012,'0','a','Agencias','NI')
        value.update({'_csv_token':'0','_csv_body':'csv.bin','_csv_sha256':'hash'})
        with tempfile.TemporaryDirectory() as directory:
            inventory({'201012':{'values_complete':True,'values':[value]}},Path(directory))
            with (Path(directory)/'observations.csv').open(encoding='utf-8-sig') as source:
                observed=next(csv.DictReader(source))
            self.assertEqual(observed['csv_token'],'0')
            self.assertEqual(observed['raw_value'],'NI')
            self.assertEqual(observed['csv_body'],'csv.bin')

    def test_missingness_states_are_not_collapsed(self):
        expected=[(None,'json_null'),('null','literal_null'),('','blank'),('NA','NA'),('NI','NI'),('NA%','NA_percent'),('NI%','NI_percent'),(0,'zero'),('0.00','zero'),('-12.5','numeric'),('unknown','invalid')]
        for value,state in expected:
            with self.subTest(value=value): self.assertEqual(classify(value),state)

    def test_structural_absence_and_unobserved_cells_separate(self):
        quarters={
            '201012':{'values_complete':True,'cadastro_complete':False,'values':[row(201012,'001','a','Ativo',0),row(201012,'002','a','Ativo','NI'),row(201012,'001','b','Agencias','NA')],'cadastro':[]},
            '202412':{'values_complete':True,'cadastro_complete':False,'values':[row(202412,'001','a','Ativo',1)],'cadastro':[]}}
        with tempfile.TemporaryDirectory() as directory:
            result=inventory(quarters,Path(directory))
            self.assertEqual(result['quarters']['201012']['unobserved_cells'],1)
            self.assertEqual(result['quarters']['201012']['institutions'],2)
            self.assertEqual(result['quarters']['202412']['structurally_absent_variables'],1)
            self.assertTrue((Path(directory)/'observations.csv').exists())
            self.assertIn('001',(Path(directory)/'institutions.csv').read_text())

    def test_incomplete_source_cannot_prove_structural_absence(self):
        quarters={'201012':{'values_complete':False,'values':[],'cadastro':[],'cadastro_complete':False},'202412':{'values_complete':True,'values':[row(202412,'001','a','Ativo',1)],'cadastro':[],'cadastro_complete':False}}
        with tempfile.TemporaryDirectory() as directory:
            result=inventory(quarters,Path(directory))
            self.assertIsNone(result['quarters']['201012']['structurally_absent_variables'])
            self.assertIsNone(result['quarters']['201012']['unobserved_cells'])

    def test_duplicates_flagged_and_labels_not_collapsed(self):
        data=[row(201012,'001','a','Ativo',1),row(201012,'001','a','Ativo',2),row(201012,'001','a','Outro',3)]
        with tempfile.TemporaryDirectory() as directory:
            result=inventory({'201012':{'values_complete':True,'values':data,'cadastro':[],'cadastro_complete':False}},Path(directory))
            self.assertEqual(result['quarters']['201012']['duplicate_extra_rows'],1)
            self.assertEqual(result['quarters']['201012']['variables'],2)
            self.assertEqual(result['quarters']['201012']['observations'],3)


if __name__=='__main__': unittest.main()

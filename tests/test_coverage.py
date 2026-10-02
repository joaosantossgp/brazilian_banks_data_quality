import unittest
from bank_quality import coverage


class CoverageTests(unittest.TestCase):
    def test_observed_match_has_limited_claims(self):
        result=coverage.audit_coverage([{'c0':'0','c1':201012,'c2':'BB'}],{'0'},201012)
        self.assertTrue(result['gate_passed'])
        self.assertEqual(result['historical_universe'],'unknown')
        self.assertEqual(result['capital_aberto_eligibility'],'not_established')
        self.assertEqual(result['odata_registration'],'unavailable_in_pilot')

    def test_anomalies_fail_gate(self):
        cases=[([{'c0':'1','c1':201012,'c2':'X'}],{'2'}),
               ([{'c0':'1','c1':201012,'c2':'X'}]*2,{'1'}),
               ([{'c0':'','c1':201012,'c2':'X'}],set()),
               ([{'c0':'1','c1':202412,'c2':'X'}],{'1'}),
               ([{'c0':'1','c1':201012,'c2':''}],{'1'}),([],set())]
        for cadastro,ids in cases:
            with self.subTest(cadastro=cadastro):
                self.assertFalse(coverage.audit_coverage(cadastro,ids,201012)['gate_passed'])

    def test_official_flow_windows_are_not_standalone_quarters(self):
        for period,window in [(202303,('2023-01-01','2023-03-31')),(202306,('2023-01-01','2023-06-30')),
                              (202309,('2023-07-01','2023-09-30')),(202312,('2023-07-01','2023-12-31'))]:
            self.assertEqual(coverage.reporting_window(period),window)
        with self.assertRaises(ValueError):coverage.reporting_window(202310)

    def test_absence_at_direct_key_does_not_establish_financial_missingness(self):
        self.assertEqual(coverage.cell_evidence(False,'NI')['financial_missingness'],'unknown')
        self.assertEqual(coverage.cell_evidence(False,0)['portal_value_state'],'zero')
        self.assertEqual(coverage.cell_evidence(True,None)['portal_value_state'],'json_null')

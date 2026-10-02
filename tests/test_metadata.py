import unittest
from bank_quality.metadata import temporal_registration, historical_listing


class MetadataTests(unittest.TestCase):
    def test_earlier_registration_event_does_not_assert_historical_active_state(self):
        result=temporal_registration({'DT_REG':'1977-07-20','SIT':'ATIVO','DT_CANCEL':'','DT_INI_SIT':'1977-07-20'},'2010-12-31')
        self.assertEqual(result['registration_event_relation'],'on_or_before_reference')
        self.assertEqual(result['historical_registration_state'],'unknown')

    def test_later_event_does_not_prove_registration_at_earlier_reference(self):
        result=temporal_registration({'DT_REG':'2015-01-01','SIT':'ATIVO'},'2010-12-31')
        self.assertEqual(result['registration_event_relation'],'after_reference')
        self.assertEqual(result['historical_registration_state'],'unknown')

    def test_current_b3_listing_does_not_prove_historical_equity_listing(self):
        result=historical_listing({'current_ticker':'BBAS3','current_listing':'observed'},'2010-12-31')
        self.assertEqual(result['historical_equity_listing_state'],'unknown')




class IdentityEvidenceTests(unittest.TestCase):
    """Reject tempting joins; accept only supplied, dated primary identity proof."""

    def setUp(self):
        self.issuer = {'name': 'BANCO BRADESCO S.A.', 'cvm_code': '906',
                       'cnpj': '60.746.948/0001-12', 'SIT': 'ATIVO', 'DT_REG': '1977-07-20'}
        self.entity = {'name': 'BANCO BRADESCO S.A.', 'source_namespace': 'IFDATA_REST_CADASTRO_1006',
                       'source_code': '60746948', 'reference_date': '2024-12-31',
                       'cnpj': '60746948000112'}
        # Synthetic evidence metadata: fixtures do not assert a real-world relationship.
        self.proof = {'kind': 'same_legal_entity', 'issuer_cnpj': '60746948000112',
                      'reporting_entity_cnpj': '60746948000112',
                      'source_namespace': self.entity['source_namespace'],
                      'source_code': self.entity['source_code'],
                      'valid_from': '2024-01-01', 'valid_to': '2024-12-31',
                      'source': {'primary': True, 'url': 'https://www.bcb.gov.br/identity-fixture',
                                 'sha256': 'a' * 64, 'retrieved_at_utc': '2026-10-01T00:00:00+00:00',
                                 'locator': 'Synthetic exact-identity assertion'}}

    def evidence(self, issuer=None, entity=None, proof=None):
        from bank_quality import metadata
        self.assertTrue(callable(getattr(metadata, 'identity_evidence', None)), 'identity_evidence API missing')
        return metadata.identity_evidence(issuer or self.issuer, entity or self.entity, proof)

    def test_identical_names_and_current_status_leave_relationship_unknown(self):
        result = self.evidence()
        self.assertEqual(result['relationship_state'], 'unknown')
        self.assertEqual(result['issuer'], self.issuer)
        self.assertEqual(result['reporting_entity'], self.entity)

    def test_truncated_cnpj_is_not_completed_from_issuer_identity(self):
        entity = dict(self.entity, cnpj='60746948')
        result = self.evidence(entity=entity, proof=self.proof)
        self.assertEqual(result['relationship_state'], 'unknown')
        self.assertEqual(result['reporting_entity']['cnpj'], '60746948')

    def test_numeric_cnpj_with_lost_leading_zero_is_not_padded(self):
        issuer = dict(self.issuer, cnpj=191)
        entity = dict(self.entity, cnpj='00000000000191', source_code='0')
        proof = dict(self.proof, issuer_cnpj='00000000000191', reporting_entity_cnpj='00000000000191', source_code='0')
        self.assertEqual(self.evidence(issuer, entity, proof)['relationship_state'], 'unknown')

    def test_full_identity_and_primary_interval_support_known_relationship(self):
        result = self.evidence(proof=self.proof)
        self.assertEqual(result['relationship_state'], 'known')
        self.assertEqual(result['relationship_kind'], 'same_legal_entity')
        self.assertEqual(result['relationship_evidence'], self.proof)

    def test_missing_source_or_interval_does_not_confirm_relationship(self):
        for field in ('source', 'valid_from', 'valid_to'):
            with self.subTest(field=field):
                proof = dict(self.proof)
                del proof[field]
                self.assertEqual(self.evidence(proof=proof)['relationship_state'], 'unknown')

    def test_source_requires_primary_url_hash_retrieval_and_locator(self):
        for field in ('url', 'sha256', 'retrieved_at_utc', 'locator'):
            with self.subTest(field=field):
                source = dict(self.proof['source'])
                del source[field]
                self.assertEqual(self.evidence(proof=dict(self.proof, source=source))['relationship_state'], 'unknown')
        source = dict(self.proof['source'], primary=False)
        self.assertEqual(self.evidence(proof=dict(self.proof, source=source))['relationship_state'], 'unknown')

    def test_different_source_namespace_or_code_does_not_confirm_relationship(self):
        for field in ('source_namespace', 'source_code'):
            with self.subTest(field=field):
                proof = dict(self.proof, **{field: 'other'})
                self.assertEqual(self.evidence(proof=proof)['relationship_state'], 'unknown')

    def test_interval_must_cover_reference_date_and_be_valid(self):
        for start, end in (('2025-01-01', '2025-12-31'), ('2024-12-31', '2024-01-01'), ('bad', '2024-12-31')):
            with self.subTest(start=start, end=end):
                proof = dict(self.proof, valid_from=start, valid_to=end)
                self.assertEqual(self.evidence(proof=proof)['relationship_state'], 'unknown')

    def test_point_evidence_supports_only_its_exact_date(self):
        proof = {k: v for k, v in self.proof.items() if k not in ('valid_from', 'valid_to')}
        proof['evidence_date'] = '2024-12-31'
        self.assertEqual(self.evidence(proof=proof)['relationship_state'], 'known')
        entity = dict(self.entity, reference_date='2010-12-31')
        self.assertEqual(self.evidence(entity=entity, proof=proof)['relationship_state'], 'unknown')

    def test_registration_and_listing_events_do_not_supply_relationship_interval(self):
        proof = {k: v for k, v in self.proof.items() if k not in ('valid_from', 'valid_to')}
        proof.update(DT_REG='1977-07-20', dateListing='26/11/1946')
        result = self.evidence(proof=proof)
        self.assertEqual(result['relationship_state'], 'unknown')
        self.assertEqual(result['historical_registration_state'], 'unknown')
        self.assertEqual(result['historical_equity_listing_state'], 'unknown')

    def test_known_identity_does_not_assert_historical_registration_or_listing(self):
        result = self.evidence(proof=self.proof)
        self.assertEqual(result['historical_registration_state'], 'unknown')
        self.assertEqual(result['historical_equity_listing_state'], 'unknown')

    def test_control_requires_both_exact_legal_identities_without_relabeling_bank_as_holding(self):
        issuer = dict(self.issuer, cnpj='60872504000123', cvm_code='19348', name='ITAU UNIBANCO HOLDING S.A.')
        entity = dict(self.entity, cnpj='60701190000104', source_code='60701190', name='ITAU UNIBANCO S.A.')
        proof = dict(self.proof, kind='controls', issuer_cnpj=issuer['cnpj'], reporting_entity_cnpj=entity['cnpj'], source_code=entity['source_code'])
        result = self.evidence(issuer, entity, proof)
        self.assertEqual(result['relationship_state'], 'known')
        self.assertEqual(result['issuer']['cnpj'], issuer['cnpj'])
        self.assertEqual(result['reporting_entity']['cnpj'], entity['cnpj'])
        proof['kind'] = 'same_legal_entity'
        self.assertEqual(self.evidence(issuer, entity, proof)['relationship_state'], 'unknown')

    def test_claimed_identities_must_match_both_input_records(self):
        for field in ('issuer_cnpj', 'reporting_entity_cnpj'):
            with self.subTest(field=field):
                proof = dict(self.proof, **{field: '60872504000123'})
                self.assertEqual(self.evidence(proof=proof)['relationship_state'], 'unknown')

if __name__=='__main__':unittest.main()


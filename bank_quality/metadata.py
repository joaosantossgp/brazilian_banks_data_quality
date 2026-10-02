"""Temporal metadata evidence without current-status survivorship assumptions."""
from datetime import date


def temporal_registration(row: dict, reference_date: str) -> dict:
    try:
        event=date.fromisoformat(row.get('DT_REG',''))
        relation='on_or_before_reference' if event<=date.fromisoformat(reference_date) else 'after_reference'
    except (ValueError,TypeError): relation='unknown'
    return {'registration_event_relation':relation,'observed_registration_event':row.get('DT_REG',''),
        'historical_registration_state':'unknown','current_registration_status':row.get('SIT','unknown'),
        'observed_cancellation_event':row.get('DT_CANCEL',''),
        'limitation':'Current cadastro is a latest-business-day snapshot, not a historical registration panel. A registration event date does not prove uninterrupted active status.'}


def historical_listing(current_evidence: dict, reference_date: str) -> dict:
    return {'historical_equity_listing_state':'unknown','reference_date':reference_date,
        'current_equity_evidence':current_evidence,
        'limitation':'Current B3 listing metadata alone cannot establish equity listing at this historical reference date.'}


def identity_evidence(issuer: dict, reporting_entity: dict, relationship: dict | None) -> dict:
    """Validate supplied primary relationship evidence, without making a financial join.

    `cnpj` must be an observed full textual CNPJ, never a padded display code.
    A relationship identifies both legal entities and the exact IF.data namespace/code.
    `source` requires a primary official URL, archived SHA-256, UTC retrieval and locator.
    Its scope is either one `evidence_date` or a closed `valid_from`/`valid_to` interval.
    Callers must verify the body/hash and that its located text states the relationship;
    this pure API validates metadata, not the document's meaning or historical listing.
    """
    from copy import deepcopy
    from datetime import datetime, timezone
    import re
    from urllib.parse import urlsplit

    def full_cnpj(value):
        if not isinstance(value, str):
            return None
        if re.fullmatch(r'[0-9]{14}', value):
            return value
        if re.fullmatch(r'[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}', value):
            return re.sub(r'[^0-9]', '', value)
        return None

    def iso_date(value):
        try:
            return date.fromisoformat(value) if isinstance(value, str) else None
        except ValueError:
            return None

    reasons = []
    proof = relationship if isinstance(relationship, dict) else {}
    issuer_cnpj = full_cnpj(issuer.get('cnpj'))
    entity_cnpj = full_cnpj(reporting_entity.get('cnpj'))
    if not issuer_cnpj or not entity_cnpj:
        reasons.append('full_textual_legal_identities_required')
    if (not issuer_cnpj or not entity_cnpj or
            full_cnpj(proof.get('issuer_cnpj')) != issuer_cnpj or
            full_cnpj(proof.get('reporting_entity_cnpj')) != entity_cnpj):
        reasons.append('relationship_legal_identities_not_matched')
    for field in ('source_namespace', 'source_code'):
        value = reporting_entity.get(field)
        if not isinstance(value, str) or not value.strip() or proof.get(field) != value:
            reasons.append('relationship_' + field + '_not_matched')
    kind = proof.get('kind')
    if kind not in ('same_legal_entity', 'controls', 'member_of_conglomerate'):
        reasons.append('explicit_relationship_kind_required')
    elif kind == 'same_legal_entity' and issuer_cnpj != entity_cnpj:
        reasons.append('same_legal_entity_requires_equal_full_cnpj')

    source = proof.get('source')
    source = source if isinstance(source, dict) else {}
    if source.get('primary') is not True:
        reasons.append('primary_source_required')
    try:
        parsed_url = urlsplit(source.get('url', ''))
        host = parsed_url.hostname or ''
        official = any(host == domain or host.endswith('.' + domain)
                       for domain in ('bcb.gov.br', 'cvm.gov.br', 'b3.com.br'))
        valid_url = parsed_url.scheme == 'https' and official
    except (ValueError, TypeError):
        valid_url = False
    if not valid_url:
        reasons.append('official_primary_source_url_required')
    if not isinstance(source.get('sha256'), str) or not re.fullmatch(r'[0-9a-fA-F]{64}', source['sha256']):
        reasons.append('archived_source_sha256_required')
    try:
        retrieved = datetime.fromisoformat(source.get('retrieved_at_utc', ''))
        if retrieved.tzinfo is None or retrieved.utcoffset() != timezone.utc.utcoffset(retrieved):
            raise ValueError('UTC retrieval required')
    except (ValueError, TypeError):
        reasons.append('source_utc_retrieval_required')
    if not isinstance(source.get('locator'), str) or not source['locator'].strip():
        reasons.append('source_relationship_locator_required')

    reference = iso_date(reporting_entity.get('reference_date'))
    evidence_date = iso_date(proof.get('evidence_date'))
    start, end = iso_date(proof.get('valid_from')), iso_date(proof.get('valid_to'))
    has_point = 'evidence_date' in proof
    has_interval = 'valid_from' in proof or 'valid_to' in proof
    if has_point and not has_interval:
        covers_reference = reference is not None and evidence_date == reference
    elif has_interval and not has_point:
        covers_reference = reference is not None and start is not None and end is not None and start <= reference <= end
    else:
        covers_reference = False
    if not covers_reference:
        reasons.append('explicit_evidence_scope_covering_reference_required')

    return {'issuer': deepcopy(issuer), 'reporting_entity': deepcopy(reporting_entity),
            'relationship_evidence': deepcopy(relationship),
            'relationship_state': 'unknown' if reasons else 'known',
            'relationship_kind': 'unknown' if reasons else kind,
            'reference_date': reporting_entity.get('reference_date'),
            'unknown_reasons': reasons,
            'historical_registration_state': 'unknown',
            'historical_equity_listing_state': 'unknown',
            'limitation': 'Supplied exact identity and relationship metadata do not establish historical registration, equity listing, consolidation equivalence or a financial join.'}

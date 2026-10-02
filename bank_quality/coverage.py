"""Source-specific observed coverage and official accumulated result windows."""
from calendar import monthrange
from collections import Counter
from .inventory import classify


def audit_coverage(cadastro: list[dict], table_ids: set[str], period: int, odata_state: str='unavailable_in_pilot') -> dict:
    ids=[row.get('c0') for row in cadastro]
    valid=[identifier for identifier in ids if isinstance(identifier,str) and identifier.strip()]
    counts=Counter(valid)
    result={'period':period,'source':'official_portal_REST_cadastro_vs_rendered_Resumo',
        'raw_rows':len(cadastro),'distinct_identifiers':len(counts),'observed_table_identifiers':len(table_ids),
        'duplicates':sorted(identifier for identifier,count in counts.items() if count>1),
        'empty_or_nontext_identifiers':len(ids)-len(valid),
        'empty_names':sum(not isinstance(row.get('c2'),str) or not row['c2'].strip() for row in cadastro),
        'wrong_period_rows':sum(str(row.get('c1'))!=str(period) for row in cadastro),
        'table_only':sorted(table_ids-set(valid)),'cadastro_only':sorted(set(valid)-table_ids),
        'odata_registration':odata_state,'historical_universe':'unknown',
        'capital_aberto_eligibility':'not_established',
        'coverage_claim':'Only equality of identifiers in the two retrieved official snapshots'}
    result['gate_passed']=bool(cadastro and table_ids) and not any(result[key] for key in
        ('duplicates','empty_or_nontext_identifiers','empty_names','wrong_period_rows','table_only','cadastro_only'))
    return result


def reporting_window(period: int) -> tuple[str,str]:
    year,month=divmod(period,100)
    if year<1900 or month not in (3,6,9,12):raise ValueError('Not a quarterly reference date')
    return (f'{year:04d}-{1 if month<=6 else 7:02d}-01',f'{year:04d}-{month:02d}-{monthrange(year,month)[1]}')


def cell_evidence(direct_key_present: bool, portal_value) -> dict:
    return {'direct_key_state':'present' if direct_key_present else 'not_stored_at_direct_key',
        'portal_value_state':classify(portal_value),'financial_missingness':'unknown',
        'limitation':'Computed/cadastral/marker mechanism requires its own official definition; no zero/null inference'}

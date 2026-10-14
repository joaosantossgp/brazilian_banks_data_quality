"""Pure, exact temporal calculations for the approved 2010–2024 analysis.

Definition groups and temporal rules must be assigned by a verified profile.
This module does not infer identities, read sources, or evaluate COSIF text.
All monetary arithmetic uses Fraction; Decimal is only an input parser/display.
"""
from __future__ import annotations

import calendar
import re
from copy import deepcopy
from datetime import date, timedelta
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from typing import NotRequired, TypedDict
import hashlib
import json
from pathlib import Path
import csv
import io
from datetime import datetime, timezone


class Observation(TypedDict):
    period: str
    token: str | None
    unit_key: tuple[str, str, str]
    definition_id: str
    scale: str
    window_rule: str
    binding: dict
    sources: list
    status: NotRequired[str]
    flags: NotRequired[list[str]]


class RationalValue(TypedDict):
    numerator: str
    denominator: str


class TemporalResult(TypedDict):
    status: str
    value_fraction: RationalValue | None
    value: str | None
    inputs: list[Observation]
    flags: list[str]
    method: str
    compatibility: list[dict]
    period: NotRequired[str]
    start: NotRequired[str]
    end: NotRequired[str]
    unit_key: NotRequired[tuple[str, str, str]]
    definition_id: NotRequired[str]
    scale: NotRequired[str]
    window_rule: NotRequired[str]
    quarter_results: NotRequired[list[TemporalResult]]


_FLOW_RULES = {'native-semester-v1', 'native-semester-analysis-v2'}
_IDENTITY_FIELDS = ('unit_key', 'definition_id', 'scale', 'window_rule')
_INCOMPATIBLE = ('incompatible_unit', 'incompatible_definition',
                 'incompatible_scale', 'incompatible_window')
_NUMERIC = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z')


def _period_date(period: object, *, opening: bool = False) -> date | None:
    if not isinstance(period, str) or not re.fullmatch(r'[0-9]{6}', period):
        return None
    year, month = int(period[:4]), int(period[4:])
    if period == '200912' and opening:
        return date(2009, 12, 31)
    if not 2010 <= year <= 2024 or month not in (3, 6, 9, 12):
        return None
    return date(year, month, calendar.monthrange(year, month)[1])


def _quarter_start(end: date) -> date:
    return date(end.year, end.month - 2, 1)


def _previous_quarter(end: date) -> date:
    return _quarter_start(end) - timedelta(days=1)


def _contract_status(row: dict, *, native: bool = True) -> str | None:
    if not isinstance(row, dict):
        return 'invalid_observation'
    if (('status' in row and (not isinstance(row['status'], str) or not row['status'])) or
            ('flags' in row and (not isinstance(row['flags'], list) or
                                any(not isinstance(flag, str) for flag in row['flags'])))):
        return 'invalid_observation'
    required = (*_IDENTITY_FIELDS, 'period') + (('binding', 'sources') if native else ())
    if any(key not in row for key in required):
        return 'invalid_observation'
    key = row['unit_key']
    if (not isinstance(key, (tuple, list)) or len(key) != 3 or
            any(not isinstance(part, (str, int)) or isinstance(part, bool) or
                part == '' for part in key)):
        return 'invalid_observation'
    if (any(not isinstance(row[field], str) or not row[field]
            for field in ('definition_id', 'scale', 'window_rule')) or
            (native and (not isinstance(row['binding'], dict) or
                         not isinstance(row['sources'], list)))):
        return 'invalid_observation'
    if not native and (not isinstance(row.get('inputs'), list) or
                       any(_contract_status(item) for item in row['inputs'])):
        return 'invalid_observation'
    return None


def _native_value(row: dict) -> tuple[Fraction | None, str | None]:
    if row.get('status', 'ok') != 'ok':
        return None, row['status']
    if 'token' not in row:
        return None, 'invalid_observation'
    token = row['token']
    if token is None:
        return None, 'native_null'
    if not isinstance(token, str):
        return None, 'invalid_numeric'
    if not token.strip():
        return None, 'invalid_empty'
    try:
        # A malformed lexeme must not become NaN because the caller disabled
        # InvalidOperation. Parsing must also leave the caller's flags intact.
        with localcontext(Context()) as context:
            context.traps[InvalidOperation] = True
            decimal = Decimal(token, context=context)
    except InvalidOperation:
        return None, 'invalid_numeric'
    if not decimal.is_finite():
        return None, 'non_finite'
    if not _NUMERIC.fullmatch(token):
        return None, 'invalid_numeric'
    return Fraction(decimal), None


def _compatibility(left: dict, right: dict) -> tuple[str | None, dict]:
    mismatches = [field for field in _IDENTITY_FIELDS if left[field] != right[field]]
    audit = {
        'left': deepcopy({key: left[key] for key in (*_IDENTITY_FIELDS, 'period')}),
        'right': deepcopy({key: right[key] for key in (*_IDENTITY_FIELDS, 'period')}),
        'compatible': not mismatches, 'mismatches': mismatches,
        'predicate': 'native-unit-definition-scale-window-v1',
    }
    for label, row in [('left', left), ('right', right)]:
        audit[label]['bindings'] = deepcopy([row['binding']] if 'binding' in row else
                                           [item['binding'] for item in row.get('inputs', [])])
    status = next((_INCOMPATIBLE[_IDENTITY_FIELDS.index(field)] for field in mismatches), None)
    return status, audit


def _result(method: str, inputs: list[Observation], identity: dict | None = None,
            *, period: str | None = None, start: date | None = None,
            end: date | None = None) -> TemporalResult:
    result: TemporalResult = {
        'status': 'ok', 'value_fraction': None, 'value': None,
        'inputs': deepcopy(inputs), 'flags': [], 'method': method, 'compatibility': [],
    }
    for row in inputs:
        if isinstance(row, dict):
            flags = row.get('flags', [])
            if not isinstance(flags, list) or any(not isinstance(flag, str) for flag in flags):
                continue
            for flag in flags:
                if flag not in result['flags']:
                    result['flags'].append(flag)
    if isinstance(identity, dict):
        for key in _IDENTITY_FIELDS:
            if key in identity:
                result[key] = deepcopy(identity[key])
    if period is not None:
        result['period'] = period
    if start is not None:
        result['start'] = start.isoformat()
    if end is not None:
        result['end'] = end.isoformat()
    return result


def _unavailable(result: TemporalResult, status: str) -> TemporalResult:
    result['status'] = status
    return result


def _valued(result: TemporalResult, value: Fraction) -> TemporalResult:
    result['value_fraction'] = {'numerator': str(value.numerator),
                                'denominator': str(value.denominator)}
    with localcontext(Context(prec=100, rounding=ROUND_HALF_EVEN)):
        result['value'] = str(Decimal(value.numerator) / Decimal(value.denominator))
    return result


def quarter_flow(current: Observation, previous: Observation | None = None) -> TemporalResult:
    """Reconstruct one genuine quarter from a verified native semester flow.

    Q1/Q3 use only current; Q2/Q4 require the immediately preceding report in
    the same semester. A supplied irrelevant predecessor is not an input to
    a reset quarter. All native dependencies of a difference are retained.
    """
    status = _contract_status(current)
    if status:
        return _unavailable(_result('quarter_flow', [current]), status)
    end = _period_date(current['period'])
    inputs = [current]
    if end is not None and end.month in (6, 12) and previous is not None:
        inputs.append(previous)
    result = _result('quarter_flow', inputs, current, period=current['period'],
                     start=_quarter_start(end) if end else None, end=end)
    if end is None:
        return _unavailable(result, 'invalid_period')
    if end.month in (6, 12):
        if previous is None:
            return _unavailable(result, 'missing_previous')
        status = _contract_status(previous)
        if status:
            return _unavailable(result, status)
        if _period_date(previous['period']) != _previous_quarter(end):
            return _unavailable(result, 'invalid_previous_period')
        status, audit = _compatibility(current, previous)
        result['compatibility'].append(audit)
        if status:
            return _unavailable(result, status)
    if current['window_rule'] not in _FLOW_RULES:
        return _unavailable(result, 'unverified_window')
    if current['scale'] != 'BRL':
        return _unavailable(result, 'invalid_scale')
    value, status = _native_value(current)
    if status:
        return _unavailable(result, status)
    if end.month in (6, 12):
        previous_value, status = _native_value(previous)
        if status:
            return _unavailable(result, status)
        value -= previous_value
    return _valued(result, value)


def flow_12_months(quarters: list[TemporalResult], end_period: str) -> TemporalResult:
    """Sum four consecutive, disjoint genuine quarters using exact fractions.

    Preserve native inputs and quarter derivations, including their intervals,
    compatibility proofs, literal bindings and unrounded intermediate values.
    """
    if not isinstance(quarters, list):
        return _unavailable(_result('flow_12_months', [quarters]), 'invalid_observation')
    # Validate the containers before flattening inputs or consuming metadata.
    if any(_contract_status(quarter, native=False) for quarter in quarters):
        return _unavailable(_result('flow_12_months', quarters), 'invalid_observation')
    inputs = [row for quarter in quarters for row in quarter['inputs']]
    result = _result('flow_12_months', inputs, quarters[0] if quarters else None,
                     period=end_period)
    result['quarter_results'] = deepcopy(quarters)
    end = _period_date(end_period)
    if end is None:
        return _unavailable(result, 'invalid_period')
    if end_period < '201012' or len(quarters) < 4:
        return _unavailable(result, 'insufficient_history')
    if len(quarters) != 4:
        return _unavailable(result, 'invalid_sequence')
    expected_ends = [end]
    for _ in range(3):
        expected_ends.insert(0, _previous_quarter(expected_ends[0]))
    result['start'] = _quarter_start(expected_ends[0]).isoformat()
    result['end'] = end.isoformat()
    total = Fraction(0)
    for index, (quarter, expected_end) in enumerate(zip(quarters, expected_ends)):
        if quarter['period'] != expected_end.strftime('%Y%m'):
            return _unavailable(result, 'invalid_sequence')
        if (quarter.get('start') != _quarter_start(expected_end).isoformat() or
                quarter.get('end') != expected_end.isoformat()):
            return _unavailable(result, 'invalid_interval')
        if index:
            status, audit = _compatibility(quarters[0], quarter)
            result['compatibility'].append(audit)
            if status:
                return _unavailable(result, status)
        if quarter['window_rule'] not in _FLOW_RULES:
            return _unavailable(result, 'unverified_window')
        if quarter['scale'] != 'BRL':
            return _unavailable(result, 'invalid_scale')
        if quarter.get('status') != 'ok':
            return _unavailable(result, quarter.get('status', 'invalid_observation'))
        fraction = quarter.get('value_fraction')
        if (not isinstance(fraction, dict) or
                any(not isinstance(fraction.get(key), str) or
                    not re.fullmatch(r'-?[0-9]+', fraction[key])
                    for key in ('numerator', 'denominator'))):
            return _unavailable(result, 'invalid_fraction')
        numerator, denominator = int(fraction['numerator']), int(fraction['denominator'])
        if denominator <= 0:
            return _unavailable(result, 'invalid_fraction')
        total += Fraction(numerator, denominator)
    return _valued(result, total)


def mean_stock(points: list[Observation], start: date, end: date) -> TemporalResult:
    """Trapezoidal stock mean over every quarter boundary, weighted by days.

    Opening 200912 is permitted only as the first boundary of a horizon
    opening in 2010. Missing, reordered or incompatible points never shorten
    the horizon, and are never filled by interpolation across a missing node.
    """
    if not isinstance(points, list):
        return _unavailable(_result('mean_stock_trapezoidal_days', [points]), 'invalid_observation')
    if any(_contract_status(point) for point in points):
        return _unavailable(_result('mean_stock_trapezoidal_days', points), 'invalid_observation')
    result = _result('mean_stock_trapezoidal_days', points, points[0] if points else None)
    if (type(start) is not date or type(end) is not date or start >= end or
            _period_date(start.strftime('%Y%m'), opening=True) != start or
            _period_date(end.strftime('%Y%m')) != end):
        return _unavailable(result, 'invalid_interval')
    result['start'], result['end'], result['period'] = start.isoformat(), end.isoformat(), end.strftime('%Y%m')
    expected = [end]
    while expected[0] > start:
        expected.insert(0, _previous_quarter(expected[0]))
    if expected[0] != start:
        return _unavailable(result, 'invalid_interval')
    dates = []
    for point in points:
        point_date = _period_date(point['period'], opening=True)
        if point_date is None:
            return _unavailable(result, 'invalid_period')
        dates.append(point_date)
    if any(right <= left for left, right in zip(dates, dates[1:])):
        return _unavailable(result, 'invalid_sequence')
    if any(day < start or day > end for day in dates):
        return _unavailable(result, 'invalid_interval')
    if not dates or dates[0] != start:
        return _unavailable(result, 'missing_opening')
    if dates != expected:
        return _unavailable(result, 'missing_stock_point')
    values = []
    for index, point in enumerate(points):
        if index:
            status, audit = _compatibility(points[0], point)
            result['compatibility'].append(audit)
            if status:
                return _unavailable(result, status)
        if point['window_rule'] != 'stock':
            return _unavailable(result, 'incompatible_window')
        if point['scale'] != 'BRL':
            return _unavailable(result, 'invalid_scale')
        value, status = _native_value(point)
        if status:
            return _unavailable(result, status)
        values.append(value)
    area = sum(((values[i-1] + values[i]) / 2 * (dates[i] - dates[i-1]).days
                for i in range(1, len(values))), Fraction(0))
    return _valued(result, area / (end - start).days)


PROFILE_PATH = Path(__file__).with_name('ifdata-analysis-profile-2010-2024.json')
METRICS = {
    'R1': ('LL', 'AT'), 'R2': ('LL', 'PL'),
    'Q1': ('provision_stock', 'credit'), 'Q2': ('provision_flow', 'credit'),
    'C1': ('PL', 'AT'), 'C3': ('PR', 'RWA'), 'C4': ('CP', 'RWA'),
    'L2': ('cash', 'interfinancial', 'sight_deposits'),
    'L3': ('credit', 'deposits'),
    'E2-B': ('personnel', 'administration', 'RBIF', 'provision_flow', 'services', 'fees'),
}
FLOW_COMPONENTS = {'LL', 'provision_flow', 'RBIF', 'services', 'fees', 'personnel', 'administration'}
FLOW_METRICS = {'R1', 'R2', 'Q2', 'E2-B'}
# Public names are deliberately independent of native account numbers.
COMPONENT_NAMES = {
    'AT':'AT', 'PL':'PL', 'LL':'LL', 'credit':'credit_gross',
    'provision_stock':'credit_provision_signed', 'cash':'cash',
    'interfinancial':'interfinancial', 'sight_deposits':'sight_deposits',
    'deposits':'deposits', 'provision_flow':'provision_result_signed',
    'RBIF':'intermediation_result', 'services':'services', 'fees':'tariffs',
    'personnel':'personnel_signed', 'administration':'admin_signed',
    'PR':'PR', 'RWA':'RWA', 'CP':'CP',
}


def load_profile(expected_sha256=None):
    """Read the installed finite profile; caller pins its bytes for a build."""
    raw=PROFILE_PATH.read_bytes()
    if expected_sha256 is not None and hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('Profile hash mismatch')
    profile=json.loads(raw)
    if profile.get('contract')!='ifdata-analysis-profile-2010-2024-v1':
        raise ValueError('Profile contract mismatch')
    for context in profile['contexts']:
        digest=hashlib.sha256(json.dumps(context['literal_context'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        if digest!=context['context_sha256'] or len(set(context['periods']))!=len(context['periods']):
            raise ValueError('Invalid literal profile context')
    return profile


def dependency_periods(periods):
    """Close flow and mean-stock dependencies, independently of output selection."""
    if (not isinstance(periods,list) or not periods or
        any(_period_date(p) is None for p in periods) or len(set(periods))!=len(periods)):
        raise ValueError('Invalid or duplicate output periods')
    needed=set()
    for period in periods:
        end=_period_date(period)
        for _ in range(5):
            p=end.strftime('%Y%m')
            if p>='200912': needed.add(p)
            end=_previous_quarter(end)
    return sorted(needed)


def resolve_component(profile, component, dataset, code, period, rows):
    """Resolve typed complete native bindings before attaching any cadastro."""
    from .ifdata_indicators import _coalesce_exact_occurrences
    contexts=[c for c in profile['contexts'] if c['component']==component
              and c['literal_context']['dataset']==dataset and period in c['periods']]
    opening=None
    if period=='200912' and dataset=='financial' and profile.get('opening_release'):
        opening=next((e for e in profile['opening_release']['finite_binding_rows']
                      if e['component']==component and e['code']==code and e['period']==period and e['stock_only']),None)
        if opening:
            contexts=[c for c in profile['contexts'] if c['context_sha256']==opening['context_sha256']
                      and c['component']==component and c['window_rule']=='stock']
    identity=dict(period=period,token=None,unit_key=(dataset,'1' if dataset=='capital' else '2',code),
                  definition_id=component,scale='BRL',window_rule='stock',binding={},sources=[])
    if len(contexts)!=1:
        return dict(identity,status='binding_unverified' if not contexts else 'ambiguous_binding')
    context=contexts[0]; literal=context['literal_context']
    identity.update(definition_id=context['compatibility'],window_rule=context['window_rule'],
                    binding=deepcopy(context),scale='native_index_unverified' if 'diagnostic' in component else 'BRL')
    if opening:
        identity['binding']['opening_exception']=deepcopy(opening)
        identity['flags']=['opening_cadastro_classification_change'] if any(c['code']==code for c in profile['opening_release']['cadastro_classification_changes']) else []
    matches=[row for row in rows if row.get('CodInst')==code and row.get('AnoMes')==period
             and all(type(row.get(k)) is type(v) and row.get(k)==v
                     for k,v in literal.items() if k!='dataset')]
    if not matches:return dict(identity,status='binding_missing')
    if opening and any(any(type(row.get(k)) is not type(v) or row.get(k)!=v for k,v in opening['source'].items()) for row in matches):
        return dict(identity,status='opening_source_mismatch',sources=deepcopy(matches))
    resolved=matches[0]
    for row in matches[1:]:
        merged=_coalesce_exact_occurrences(resolved,row)
        if merged is None:return dict(identity,status='ambiguous_occurrence',sources=deepcopy(matches))
        resolved=merged
    return dict(identity,token=resolved['Saldo'],sources=deepcopy(resolved.get('source_occurrences',[resolved])))


def _fraction_field(value):
    return {'numerator':str(value.numerator),'denominator':str(value.denominator)}


def _temporal_component(name, observations, period, horizon):
    by_period={row['period']:row for row in observations}
    if len(by_period)!=len(observations):
        return _unavailable(_result('component',observations),'ambiguous_occurrence')
    end=_period_date(period)
    if name in FLOW_COMPONENTS:
        ends=[end]
        if horizon=='ttm':
            for _ in range(3):ends.insert(0,_previous_quarter(ends[0]))
            if ends[0].year<2010:
                return _unavailable(_result('flow_12_months',observations),'insufficient_history')
        quarters=[]
        for day in ends:
            current=by_period.get(day.strftime('%Y%m'))
            if current is None:return _unavailable(_result('component',observations),'missing_component')
            quarters.append(quarter_flow(current,by_period.get(_previous_quarter(day).strftime('%Y%m'))))
        return flow_12_months(quarters,period) if horizon=='ttm' else quarters[0]
    if horizon in ('quarter','ttm'):
        start=end
        for _ in range(4 if horizon=='ttm' else 1):start=_previous_quarter(start)
        points=[row for row in observations if start.strftime('%Y%m')<=row['period']<=period]
        return mean_stock(points,start,end)
    current=by_period.get(period)
    if current is None:return _unavailable(_result('point',observations),'missing_component')
    result=_result('point',[current],current,period=period,end=end)
    status=_contract_status(current)
    if status:return _unavailable(result,status)
    if current['window_rule']!='stock':return _unavailable(result,'incompatible_window')
    if current['scale']!='BRL':return _unavailable(result,'invalid_scale')
    value,status=_native_value(current)
    return _unavailable(result,status) if status else _valued(result,value)


def evaluate_metric(metric, inputs, horizon):
    """Compose finite formulas from resolved Observation lists per component.

    inputs={period, components:{name:[Observation,...]}, financial_statement:
    bool, prudential_bridge:bool}. Temporal compatibility is checked within
    each component; across concepts only native unit/scale/end/window match.
    """
    result=dict(metric=metric,horizon=horizon,status='ok',value=None,value_fraction=None,
                numerator_fraction=None,denominator_fraction=None,flags=[],components={},
                ratio_unit='fraction',percentage_display=None,
                limits=(['population_not_certified_exclusive_to_credit','not_NPL_or_REF'] if metric=='Q2' else
                        ['selected_income_only','economic_representativeness_not_certified'] if metric=='E2-B' else
                        ['native_prudential_perimeter_only','published_index_scale_unverified'] if metric in ('C3','C4') else
                        ['native_accounting_question_only']),
                applicability='unknown',economic_representativeness='not_certified' if metric=='E2-B' else 'native_accounting_question')
    if metric not in METRICS:return dict(result,status='unknown_metric')
    if horizon not in (('quarter','ttm') if metric in FLOW_METRICS else ('point',)):
        return dict(result,status='invalid_horizon')
    if not isinstance(inputs,dict) or _period_date(inputs.get('period')) is None:
        return dict(result,status='invalid_period')
    period=inputs['period'];result['period']=period
    result['annual_summary']=period.endswith('12') and horizon in ('point','ttm')
    components=inputs.get('components',{})
    for name in METRICS[metric]:
        rows=components.get(name,[])
        if not isinstance(rows,list) or any(_contract_status(r) for r in rows):
            return dict(result,status='invalid_observation')
        result['components'][name]=_temporal_component(name,rows,period,horizon)
    # Applicability refers to the reporting question, independently of calculation.
    if metric in ('C3','C4'):
        if inputs.get('prudential_bridge') and period>='201503' and all(
                any(r['period']==period and r.get('binding') and r.get('sources')
                    and r.get('status','ok') not in ('binding_missing','binding_unverified','ambiguous_binding','ambiguous_occurrence')
                    for r in components.get(name,[])) for name in METRICS[metric]):
            result['applicability']='applicable'
    elif metric in ('R1','R2','C1','E2-B'):
        if inputs.get('financial_statement') and all(
                any(r['period']==period and r.get('binding') and r.get('sources')
                    and r.get('status','ok') not in ('binding_missing','binding_unverified','ambiguous_binding','ambiguous_occurrence')
                    for r in components.get(name,[])) for name in METRICS[metric]):
            result['applicability']='applicable'
    else:
        activity='credit' if metric in ('Q1','Q2') else 'sight_deposits' if metric=='L2' else 'deposits'
        row=next((r for r in components.get(activity,[]) if r['period']==period),None)
        value,status=_native_value(row) if row else (None,'missing')
        if status is None and value>0:
            credit=next((r for r in components.get('credit',[]) if r['period']==period),None)
            if metric!='L3' or (credit is not None and _native_value(credit)[1] is None):
                result['applicability']='applicable'
    failed=next((r['status'] for r in result['components'].values() if r['status']!='ok'),None)
    if failed:return dict(result,status=failed)
    derived=list(result['components'].values())
    if any(r['unit_key']!=derived[0]['unit_key'] for r in derived):return dict(result,status='incompatible_unit')
    if any(r['scale']!=derived[0]['scale'] for r in derived):return dict(result,status='incompatible_scale')
    values={name:Fraction(int(r['value_fraction']['numerator']),int(r['value_fraction']['denominator'])) for name,r in result['components'].items()}
    if metric=='E2-B':
        numerator=-(values['personnel']+values['administration'])
        denominator=values['RBIF']-values['provision_flow']+values['services']+values['fees']
    elif metric=='L2': numerator=values['cash']+values['interfinancial'];denominator=values['sight_deposits']
    else:
        a,b=METRICS[metric];numerator=values[a]*(-1 if metric in ('Q1','Q2') else 1);denominator=values[b]
    result['numerator_fraction']=_fraction_field(numerator);result['denominator_fraction']=_fraction_field(denominator)
    if denominator==0:return dict(result,status='zero_denominator')
    if denominator<0:result['flags'].append('negative_denominator')
    if metric in ('Q2','E2-B') and numerator<0:result['flags'].append('signed_cost_reversal')
    for r in derived:result['flags']=sorted(set(result['flags']+r['flags']))
    result=_valued(result,numerator/denominator)
    result['percentage_display']=_valued({},numerator/denominator*100)['value']
    return result


ANALYSIS_CONTRACT='ifdata-monograph-analysis-2010-2024-v1'
ANALYSIS_TABLES=('components','results','company_map')
TABLE_COLUMNS=('id','period','metric','horizon','dataset','code','status','payload')


def _digest_file(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def _json_unique(raw):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value:raise ValueError('Duplicate JSON key')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs)


def _contained(root,name):
    if not isinstance(name,str) or not name or '\\' in name or ':' in name:
        raise ValueError('Invalid inventory path')
    path=(root/name).resolve()
    if Path(name).is_absolute() or '..' in Path(name).parts or not path.is_relative_to(root) or path==root:
        raise ValueError('Inventory path outside root')
    return path


def _authenticate(descriptor,contract=None,strict_inventory=False):
    if not isinstance(descriptor,dict) or set(descriptor)!={'root','expected_manifest_sha256'}:
        raise ValueError('Explicit root and external manifest pin required')
    pin=descriptor['expected_manifest_sha256']
    if not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{64}',pin):raise ValueError('Invalid external pin')
    root=Path(descriptor['root']).resolve();path=root/'manifest.json'
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Manifest external pin mismatch')
    manifest=_json_unique(raw)
    if not isinstance(manifest,dict) or (contract is not None and manifest.get('contract')!=contract):
        raise ValueError('Input contract mismatch')
    files=manifest.get('files')
    if isinstance(files,dict):files=[dict(file=k,sha256=v) for k,v in files.items()]
    if not isinstance(files,list) or not files:raise ValueError('Missing input inventory')
    seen=set()
    for entry in files:
        if not isinstance(entry,dict) or not isinstance(entry.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',entry['sha256']):
            raise ValueError('Invalid inventory item')
        path=_contained(root,entry.get('file'));name=path.relative_to(root).as_posix()
        if name in seen:raise ValueError('Duplicate inventory file')
        seen.add(name)
        if _digest_file(path)!=entry['sha256']:raise ValueError('Input file hash mismatch')
    if strict_inventory:
        actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        if actual!=seen|{'manifest.json'}:raise ValueError('Unlisted input file')
    return root,manifest


def _schema(conn,table,fields):
    schema=conn.execute('describe '+table).fetchall()
    if [r[0] for r in schema]!=list(fields) or any(r[1]!='VARCHAR' for r in schema):
        raise ValueError('Native textual schema mismatch')


def _part_counts(root,manifest):
    """Check each native part, independently of the existing reader's total."""
    import duckdb
    if type(manifest.get('rows')) is not int or manifest['rows']<0:
        raise ValueError('Invalid native total count')
    with duckdb.connect() as conn:
        for item in manifest['files']:
            if type(item.get('rows')) is not int or item['rows']<0:
                raise ValueError('Invalid native part count')
            count=conn.execute('select count(*) from read_parquet(?)',[str(_contained(root,item['file']))]).fetchone()[0]
            if count!=item['rows']:raise ValueError('Native part count mismatch')
    if sum(item['rows'] for item in manifest['files'])!=manifest['rows']:
        raise ValueError('Native part counts disagree with total')


def _records(cursor):
    fields=[c[0] for c in cursor.description]
    return [dict(zip(fields,row)) for row in cursor.fetchall()]


def _read_sample(root,manifest):
    required={'company-quarter-map.json','annual-verification.json','complementary-annual-verification.json'}
    if manifest.get('schema')!=1 or manifest.get('issue')!=125 or not required<=set(manifest['files']):
        raise ValueError('Not a fixed sample125 package')
    rows=_json_unique((root/'company-quarter-map.json').read_bytes())
    annual=_json_unique((root/'annual-verification.json').read_bytes())
    complementary=_json_unique((root/'complementary-annual-verification.json').read_bytes())
    if not isinstance(rows,list) or not isinstance(annual,list) or not isinstance(complementary,dict) or not isinstance(complementary.get('rows'),list):
        raise ValueError('Sample schema mismatch')
    keys=set()
    for row in rows:
        needed=('company_cnpj14','company_name_2024','period','native_target_code','operator_base8','native_cadastro')
        if not isinstance(row,dict) or any(k not in row for k in needed):raise ValueError('Sample mapping schema mismatch')
        if (any(not isinstance(row[k],str) or not row[k] for k in needed[:3]) or _period_date(row['period']) is None
            or any(row[k] is not None and (not isinstance(row[k],str) or not row[k]) for k in ('native_target_code','operator_base8'))
            or row['native_cadastro'] is not None and not isinstance(row['native_cadastro'],dict)):
            raise ValueError('Invalid sample typed field')
        key=row['company_cnpj14'],row['period']
        if key in keys:raise ValueError('Duplicate company-quarter')
        keys.add(key)
    return rows,annual,complementary['rows']


def _write_tables(output,tables):
    import duckdb
    files=[]
    for table in ANALYSIS_TABLES:
        rows=tables[table]
        json_path=output/(table+'.json')
        json_path.write_text(json.dumps(rows,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        csv_path=output/(table+'.csv')
        with csv_path.open('w',newline='',encoding='utf-8') as stream:
            writer=csv.writer(stream,quoting=csv.QUOTE_NOTNULL);writer.writerow(TABLE_COLUMNS)
            for row in rows:
                writer.writerow([row.get(k) for k in TABLE_COLUMNS[:-1]]+
                                [json.dumps(row,ensure_ascii=False,sort_keys=True)])
        with duckdb.connect() as conn:
            conn.execute('create table rows ('+','.join(k+' varchar' for k in TABLE_COLUMNS)+')')
            if rows:
                conn.executemany('insert into rows values ('+','.join('?' for _ in TABLE_COLUMNS)+')',
                  [[row.get(k) for k in TABLE_COLUMNS[:-1]]+[json.dumps(row,ensure_ascii=False,sort_keys=True)] for row in rows])
            conn.execute('copy rows to ? (format parquet, compression zstd)',[str(output/(table+'.parquet'))])
        for ext in ('json','csv','parquet'):
            path=output/(table+'.'+ext);files.append(dict(file=path.name,sha256=_digest_file(path),rows=len(rows)))
    return files


def build_analysis(config,output):
    """Build stage2 in a new directory using externally pinned accepted readers.

    config={periods:[YYYYMM],profile_expected_sha256,inputs:{sample,catalogue,
    cadastro,financial,capital,[opening]}}. Each input has root and external
    expected_manifest_sha256. Opening is refused until separately released.
    """
    from .ifdata_odata import open_dataset,COLUMNS,CONTRACT as DATA_CONTRACT
    from .ifdata_cadastro import open_cadastro,FIELDS,ORIGIN,CONTRACT as CAD_CONTRACT
    from .ifdata_variable_catalog import query_catalog,CONTRACT as CATALOG_CONTRACT
    output=Path(output).resolve()
    if output.exists():raise FileExistsError(output)
    if not isinstance(config,dict) or set(config)!={'periods','profile_expected_sha256','inputs'}:
        raise ValueError('Invalid analysis config')
    pin=config['profile_expected_sha256']
    if not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{64}',pin):raise ValueError('External profile pin required')
    dependencies=dependency_periods(config['periods']);profile=load_profile(pin)
    inputs=config['inputs']
    if not isinstance(inputs,dict) or set(inputs)-{'sample','catalogue','cadastro','financial','capital','opening'} or not {'sample','catalogue','cadastro','financial','capital'}<=set(inputs):
        raise ValueError('Missing or unknown analysis inputs')
    contracts={'sample':None,'catalogue':CATALOG_CONTRACT,'cadastro':CAD_CONTRACT,'financial':DATA_CONTRACT,'capital':DATA_CONTRACT}
    if inputs.get('opening') is not None:
        opening=profile.get('opening_release')
        if not opening or inputs['opening'].get('expected_manifest_sha256')!=opening['source_output_manifest_sha256']:
            raise ValueError('Opening200912 reviewed manifest mismatch')
        # The finite exception reviewed these exact dated own-target cadastro
        # pairs. Mere presence of a differently pinned cadastro cannot extend
        # that perimeter proof; a future snapshot requires renewed review.
        cadastro_proof=profile.get('opening_cadastro_proof')
        if (not cadastro_proof or inputs['cadastro'].get('expected_manifest_sha256')!=
                cadastro_proof['expected_manifest_sha256']):
            raise ValueError('Opening200912 cadastro reviewed manifest mismatch')
        contracts['opening']=DATA_CONTRACT
    accepted={name:_authenticate(inputs[name],contract) for name,contract in contracts.items()}
    for name in ('financial','capital','cadastro','opening'):
        if name in accepted:_part_counts(*accepted[name])
    sample,annual,complementary=_read_sample(*accepted['sample'])
    catalogue=query_catalog(accepted['catalogue'][0],'select * from catalogo_variaveis')
    # Verify every actual selected native context against both independent
    # profile and supplied catalogue; no interval min/max or account fallback.
    catalog_keys={json.dumps({k:r[k] for k in c['literal_context']},sort_keys=True,ensure_ascii=False):
                  set(str(p) for p in r['periodos'])
                  for c in profile['contexts'] for r in catalogue
                  if all(type(r.get(k)) is type(v) and r.get(k)==v for k,v in c['literal_context'].items())}
    selected=[r for r in sample if r['period'] in config['periods']]
    if not selected:raise ValueError('Requested periods have no sample mappings')
    # Close dependencies for each unit at its output date; a new native code
    # never receives its predecessor's observations merely by company name.
    financial_codes=sorted({r['native_target_code'] for r in selected if r['native_target_code']})
    operator_codes=sorted({r['operator_base8'] for r in selected if r['operator_base8']})
    with open_cadastro(accepted['cadastro'][0]) as conn:
        _schema(conn,'cadastro',FIELDS+ORIGIN)
        targets=_records(conn.execute('select * from cadastro where Data in (select unnest(?)) and CodInst in (select unnest(?))',[dependencies,financial_codes+operator_codes]))
        cadre={(r['CodInst'],r['Data']):r for r in targets}
        prudential_codes=sorted({r['CodConglomeradoPrudencial'] for r in targets if r['CodConglomeradoPrudencial']})
        prudential=_records(conn.execute('select * from cadastro where Data in (select unnest(?)) and CodInst in (select unnest(?))',[dependencies,prudential_codes]))
        cadre.update({(r['CodInst'],r['Data']):r for r in prudential})
    native={}
    for dataset,codes in [('financial',financial_codes),('capital',prudential_codes)]:
        accounts=sorted({c['literal_context']['Conta'] for c in profile['contexts'] if c['literal_context']['dataset']==dataset})
        with open_dataset(accepted[dataset][0]) as conn:
            _schema(conn,'ifdata',COLUMNS)
            native[dataset]=_records(conn.execute('select * from ifdata where AnoMes in (select unnest(?)) and CodInst in (select unnest(?)) and Conta in (select unnest(?)) order by AnoMes,CodInst,NumeroRelatorio,Conta,source_file,source_row',[dependencies,codes,accounts]))
    if 'opening' in accepted and '200912' in dependencies:
        opening=profile['opening_release'];codes=sorted(set(financial_codes)&set(opening['unit_codes']))
        accounts=sorted({c['literal_context']['Conta'] for c in profile['contexts'] if c['component'] in opening['components']})
        with open_dataset(accepted['opening'][0]) as conn:
            _schema(conn,'ifdata',COLUMNS)
            native['financial'].extend(_records(conn.execute("select * from ifdata where AnoMes='200912' and TipoInstituicao='2' and CodInst in (select unnest(?)) and Conta in (select unnest(?)) order by CodInst,NumeroRelatorio,Conta,source_row",[codes,accounts])))
    index={}
    for dataset,rows in native.items():
        for row in rows:index.setdefault((dataset,row['CodInst'],row['AnoMes']),[]).append(row)
    component_cache={}
    def component(name,dataset,code,period):
        key=name,dataset,code,period
        if key not in component_cache:
            result=resolve_component(profile,COMPONENT_NAMES.get(name,name),dataset,code,period,index.get((dataset,code,period),[]))
            binding=result['binding']
            if binding and period!='200912':
                literal=binding['literal_context'];catkey=json.dumps(literal,sort_keys=True,ensure_ascii=False)
                if period not in catalog_keys.get(catkey,set()):
                    result.update(status='catalogue_context_missing',token=None)
            result['target_cadastro']=deepcopy(cadre.get((code,period)))
            if period=='200912' and binding:
                result['comparison_cadastro_201003']=deepcopy(cadre.get((code,'201003')))
                if result['target_cadastro'] is None or result['comparison_cadastro_201003'] is None:
                    result.update(status='opening_cadastro_missing',token=None)
            result.update(id='|'.join(key),component=name,dataset=dataset,code=code,status=result.get('status','ok'))
            component_cache[key]=result
        return deepcopy(component_cache[key])
    results={};maps=[]
    annual_index={(r['company_cnpj14'],r['period']):r for r in annual}
    for row in sorted(selected,key=lambda r:(r['period'],r['company_cnpj14'])):
        period=row['period'];fcode=row['native_target_code'];operator=cadre.get((row['operator_base8'],period))
        target=cadre.get((fcode,period));pcode=operator.get('CodConglomeradoPrudencial') if operator else None
        # A bridge disagreement is preserved as an explicit conflict, never
        # resolved by copying the operator's classifications to the target.
        bridge_conflict=bool(target and operator and target.get('CodConglomeradoPrudencial')!=pcode)
        mapping=dict(id=row['company_cnpj14']+'|'+period,company=row['company_cnpj14'],company_name=row['company_name_2024'],period=period,
                     financial_code=fcode,prudential_code=pcode,operator_code=row['operator_base8'],
                     financial_target_cadastro=target,operator_cadastro=operator,prudential_target_cadastro=cadre.get((pcode,period)),
                     annual_evidence=annual_index.get((row['company_cnpj14'],period)),
                     continuous_issuer_control='unknown',status='missing_unit' if not fcode else 'bridge_conflict' if bridge_conflict else 'mapped',result_ids=[])
        for metric,names in METRICS.items():
            dataset='capital' if metric in ('C3','C4') else 'financial';code=pcode if dataset=='capital' else fcode
            for horizon in (('quarter','ttm') if metric in FLOW_METRICS else ('point',)):
                if not code or (dataset=='capital' and (bridge_conflict or not cadre.get((code,period)))):
                    mapping.setdefault('unavailable',[]).append(dict(metric=metric,horizon=horizon,status='bridge_conflict' if bridge_conflict and dataset=='capital' else 'missing_unit'))
                    continue
                key=(dataset,code,period,metric,horizon);identifier='|'.join(key)
                if key not in results:
                    data={name:[component(name,dataset,code,p) for p in dependencies if p>='201003' or
                                (p=='200912' and 'opening' in accepted and name in ('AT','PL','credit'))] for name in names}
                    evaluated=evaluate_metric(metric,dict(period=period,components=data,financial_statement=target is not None,
                                                        prudential_bridge=dataset=='capital' and not bridge_conflict),horizon)
                    evaluated.update(id=identifier,dataset=dataset,code=code,
                                     target_cadastro=cadre.get((code,period)),companies=[],diagnostics={})
                    if metric=='Q1':
                        net=component('credit_net_diagnostic',dataset,code,period)
                        gross=component('credit',dataset,code,period)
                        provision=component('provision_stock',dataset,code,period)
                        parsed=[_native_value(c) for c in (gross,provision,net)]
                        diagnostic=dict(inputs=[gross,provision,net],status='unavailable',residual_fraction=None)
                        if all(status is None for _,status in parsed):
                            residual=parsed[0][0]+parsed[1][0]-parsed[2][0]
                            diagnostic.update(status='exact' if residual==0 else 'native_residual',residual_fraction=_fraction_field(residual))
                        evaluated['diagnostics']['credit_identity']=diagnostic
                    if metric in ('C3','C4'):
                        name='IB_published_diagnostic' if metric=='C3' else 'ICP_published_diagnostic'
                        evaluated['diagnostics']['published_index']=component(name,dataset,code,period)
                        evaluated['diagnostics']['scale_comparison']='unverified_no_conversion_or_equality_imposed'
                    results[key]=evaluated
                results[key]['companies'].append(row['company_cnpj14']);mapping['result_ids'].append(identifier)
        mapping['result_ids']=sorted(mapping['result_ids']);maps.append(mapping)
    output.mkdir(parents=True,exist_ok=False)
    tables=dict(components=sorted(component_cache.values(),key=lambda r:r['id']),results=sorted(results.values(),key=lambda r:r['id']),company_map=maps)
    for r in tables['results']:r['companies']=sorted(set(r['companies']))
    files=_write_tables(output,tables)
    # Detect persistent source mutation during the bounded read before accepting.
    for name,contract in contracts.items():_authenticate(inputs[name],contract)
    manifest=dict(contract=ANALYSIS_CONTRACT,stage='bindings-and-calculations',created_utc=datetime.now(timezone.utc).isoformat(),
      periods=sorted(config['periods']),dependency_periods=dependencies,profile_sha256=config['profile_expected_sha256'],inputs=deepcopy(inputs),
      files=files,tables={k:len(v) for k,v in tables.items()},table_columns=list(TABLE_COLUMNS),
      complementary_rows_available=len(complementary),complementary_execution='reserved_for_stage3',precision=100,
      limitations=['No aggregates/distributions at stage2','No continuous historical issuer control certified',
                   'E2-B selected income proxy, economic representativeness not certified',
                   'Q2 provision result scope not certified exclusive to gross credit',
                   'Opening200912 finite reviewed stocks only; absent input remains missing_opening'])
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return manifest


def verify_analysis(output,expected_manifest_sha256):
    """Authenticate the complete immutable stage2 package, schemas and counts."""
    import duckdb
    root,manifest=_authenticate(dict(root=str(output),expected_manifest_sha256=expected_manifest_sha256),ANALYSIS_CONTRACT,True)
    expected={table+'.'+ext for table in ANALYSIS_TABLES for ext in ('json','csv','parquet')}
    if ({item['file'] for item in manifest['files']}!=expected or manifest.get('stage')!='bindings-and-calculations'
        or manifest.get('table_columns')!=list(TABLE_COLUMNS) or set(manifest.get('tables',{}))!=set(ANALYSIS_TABLES)):
        raise ValueError('Incomplete analysis contract/inventory')
    with duckdb.connect() as conn:
        for table in ANALYSIS_TABLES:
            rows=_json_unique((root/(table+'.json')).read_bytes())
            if not isinstance(rows,list) or len(rows)!=manifest['tables'][table] or any(not isinstance(r,dict) or not isinstance(r.get('id'),str) for r in rows):
                raise ValueError('Output schema/count mismatch')
            if len({r['id'] for r in rows})!=len(rows):raise ValueError('Duplicate output identity')
            conn.from_parquet(str(root/(table+'.parquet'))).create_view('checked',replace=True)
            _schema(conn,'checked',TABLE_COLUMNS)
            parquet=_records(conn.execute('select * from checked'))
            expected_rows=[{**{k:r.get(k) for k in TABLE_COLUMNS[:-1]},'payload':json.dumps(r,ensure_ascii=False,sort_keys=True)} for r in rows]
            # Python3.12 QUOTE_NOTNULL preserves the distinction when writing
            # but its reader does not restore None. Compare canonical CSV bytes
            # so unquoted null and quoted empty remain distinguishable.
            stream=io.StringIO(newline='');writer=csv.writer(stream,quoting=csv.QUOTE_NOTNULL)
            writer.writerow(TABLE_COLUMNS)
            writer.writerows([[r[k] for k in TABLE_COLUMNS] for r in expected_rows])
            if parquet!=expected_rows or (root/(table+'.csv')).read_bytes()!=stream.getvalue().encode('utf-8'):
                raise ValueError('Output representations disagree')
            if any(item['rows']!=len(rows) for item in manifest['files'] if item['file'].startswith(table+'.')):
                raise ValueError('Output part count mismatch')
    return manifest


def query_analysis(output,expected_manifest_sha256,sql):
    """One SELECT over verified materialized result tables, with no external I/O."""
    import duckdb
    verify_analysis(output,expected_manifest_sha256)
    root=Path(output).resolve()
    with duckdb.connect(config={'autoload_known_extensions':False,'autoinstall_known_extensions':False}) as conn:
        for table in ANALYSIS_TABLES:
            conn.execute('create table '+table+' as select * from read_parquet(?)',[str(root/(table+'.parquet'))])
        conn.execute('set enable_external_access=false')
        statements=conn.extract_statements(sql)
        if len(statements)!=1 or statements[0].type!=duckdb.StatementType.SELECT:
            raise ValueError('Query must be one SELECT')
        return _records(conn.execute(sql))

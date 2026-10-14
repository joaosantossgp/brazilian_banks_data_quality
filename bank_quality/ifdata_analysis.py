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

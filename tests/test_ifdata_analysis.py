"""Causal checks for the pure temporal layer; no captured data or I/O."""
import importlib.util
import unittest
from copy import deepcopy
from datetime import date
from decimal import Inexact, InvalidOperation, ROUND_DOWN, localcontext


def observation(period, token, **changes):
    row = dict(period=period, token=token,
               unit_key=('financial', '2', '001'), definition_id='profit-v1',
               scale='BRL', window_rule='native-semester-analysis-v2',
               binding={'Conta': 'profit', 'Grupo': None, 'Descricao': 'literal'},
               sources=[{'file': 'captured.json', 'row': period, 'sha256': 'a' * 64}])
    row.update(changes)
    return row


def stock(period, token, **changes):
    return observation(period, token, definition_id='assets-v1',
                       window_rule='stock', **changes)


class TemporalTests(unittest.TestCase):
    def setUp(self):
        # Missing module is the expected first RED, expressed as an assertion.
        assert importlib.util.find_spec('bank_quality.ifdata_analysis') is not None, (
            'The pure temporal analysis module has not been implemented')
        from bank_quality import ifdata_analysis
        self.api = ifdata_analysis

    def fraction(self, result, numerator, denominator='1'):
        self.assertEqual(result['status'], 'ok', result)
        self.assertEqual(result['value_fraction'],
                         {'numerator': str(numerator), 'denominator': str(denominator)})

    def unavailable(self, result, status):
        self.assertEqual(result['status'], status, result)
        self.assertIsNone(result['value_fraction'])
        self.assertIsNone(result['value'])

    def year(self, year='2011'):
        raw = [observation(year + p, t) for p, t in
               [('03', '10'), ('06', '25'), ('09', '7'), ('12', '18')]]
        return [self.api.quarter_flow(raw[i], raw[i-1] if i else None)
                for i in range(4)], raw

    def test_semester_reset_produces_genuine_quarters_and_annual_43(self):
        quarters, raw = self.year()
        for result, wanted in zip(quarters, [10, 15, 7, 11]):
            self.fraction(result, wanted)
        self.fraction(self.api.flow_12_months(quarters, '201112'), 43)
        self.assertEqual(quarters[1]['inputs'], [raw[1], raw[0]])
        self.assertEqual(quarters[2]['inputs'], [raw[2]])
        self.assertEqual((quarters[1]['start'], quarters[1]['end']),
                         ('2011-04-01', '2011-06-30'))
        self.assertEqual(quarters[1]['unit_key'], raw[1]['unit_key'])
        self.assertEqual(quarters[1]['definition_id'], 'profit-v1')

    def test_negative_quarter_reversal_and_zero_remain_values(self):
        self.fraction(self.api.quarter_flow(observation('201106', '-5'),
                                           observation('201103', '10')), -15)
        self.fraction(self.api.quarter_flow(observation('201103', '0')), 0)

    def test_even_quarter_requires_immediate_predecessor_and_keeps_null(self):
        current = observation('201112', '18')
        self.unavailable(self.api.quarter_flow(current), 'missing_previous')
        self.unavailable(self.api.quarter_flow(current, observation('201106', '25')),
                         'invalid_previous_period')
        result = self.api.quarter_flow(current, observation('201109', None))
        self.unavailable(result, 'native_null')
        self.assertEqual(len(result['inputs']), 2)

    def test_break_and_identity_changes_never_receive_continuity_by_name(self):
        current = observation('201906', '25', definition_id='profit-201903')
        self.unavailable(self.api.quarter_flow(current, observation('201903', '10')),
                         'incompatible_definition')
        for key in [('financial', '2', '002'), ('financial', '3', '001'),
                    ('prudential', '2', '001')]:
            with self.subTest(key=key):
                self.unavailable(self.api.quarter_flow(observation('201106', '25'),
                                 observation('201103', '10', unit_key=key)),
                                 'incompatible_unit')

    def test_scale_window_and_unapproved_rule_are_guarded(self):
        for field, value, status in [('scale', 'BRL-thousand', 'incompatible_scale'),
                                     ('window_rule', 'native-semester-v1',
                                      'incompatible_window')]:
            self.unavailable(self.api.quarter_flow(observation('201106', '25'),
                             observation('201103', '10', **{field: value})), status)
        self.unavailable(self.api.quarter_flow(observation('201103', '10',
                         window_rule='unknown')), 'unverified_window')

    def test_homologated_definition_keeps_distinct_literal_bindings_and_audit(self):
        previous = observation('201103', '10', binding={'Conta': 'old', 'Grupo': ''})
        current = observation('201106', '25')
        result = self.api.quarter_flow(current, previous)
        self.fraction(result, 15)
        self.assertEqual(result['inputs'], [current, previous])
        self.assertTrue(result['compatibility'][0]['compatible'])
        changed = self.api.quarter_flow(current, dict(previous, definition_id='other'))
        self.assertFalse(changed['compatibility'][0]['compatible'])

    def test_native_missing_invalid_nonfinite_and_ambiguous_are_distinct(self):
        for token, status in [(None, 'native_null'), ('', 'invalid_empty'),
                              ('   ', 'invalid_empty'), ('NI', 'invalid_numeric'),
                              ('NA', 'invalid_numeric'), ('[70000009]', 'invalid_numeric'),
                              ('NaN', 'non_finite'), ('Infinity', 'non_finite'),
                              (0.1, 'invalid_numeric'), (True, 'invalid_numeric')]:
            with self.subTest(token=token):
                self.unavailable(self.api.quarter_flow(observation('201103', token)), status)
        row = observation('201103', '10', status='ambiguous_occurrence')
        self.unavailable(self.api.quarter_flow(row), 'ambiguous_occurrence')

    def test_native_parser_states_are_independent_of_external_decimal_traps(self):
        for trap in (True, False):
            with localcontext() as context:
                context.traps[InvalidOperation] = trap
                before = context.copy()
                for token, status in [('NI', 'invalid_numeric'), ('not-a-number', 'invalid_numeric'),
                                      ('NaN', 'non_finite'), ('sNaN', 'non_finite'),
                                      ('Infinity', 'non_finite'), ('-Infinity', 'non_finite')]:
                    with self.subTest(trap=trap, token=token):
                        self.unavailable(self.api.quarter_flow(observation('201103', token)), status)
                self.assertEqual(context.traps, before.traps)
                self.assertEqual(context.flags, before.flags)

    def test_invalid_first_row_is_rejected_before_metadata_construction(self):
        for malformed in [123, None, 'wrong', [], {}]:
            with self.subTest(first=malformed):
                self.unavailable(self.api.flow_12_months([malformed, {}, {}, {}], '201112'),
                                 'invalid_observation')
                self.unavailable(self.api.mean_stock([malformed], date(2010, 12, 31),
                                                    date(2011, 3, 31)), 'invalid_observation')

    def test_invalid_optional_flags_and_status_are_contract_states(self):
        for field, malformed in [('flags', None), ('flags', 'flag'), ('flags', [None]),
                                  ('flags', {'flag': True}), ('status', None),
                                  ('status', False), ('status', ''), ('status', [])]:
            with self.subTest(field=field, value=malformed):
                bad = observation('201103', '10', **{field: malformed})
                self.unavailable(self.api.quarter_flow(bad), 'invalid_observation')
                self.unavailable(self.api.quarter_flow(observation('201106', '25'), bad),
                                 'invalid_observation')

    def test_invalid_collections_and_derived_inputs_return_contract_states(self):
        for malformed in [None, 123, 'not-a-list', {}]:
            with self.subTest(collection=malformed):
                self.unavailable(self.api.flow_12_months(malformed, '201112'), 'invalid_observation')
                self.unavailable(self.api.mean_stock(malformed, date(2010, 12, 31),
                                                    date(2011, 3, 31)), 'invalid_observation')
        for malformed in [None, 123, 'not-a-list', [123]]:
            q, _ = self.year()
            q[0]['inputs'] = malformed
            with self.subTest(inputs=malformed):
                self.unavailable(self.api.flow_12_months(q, '201112'), 'invalid_observation')

    def test_precision_40_digits_and_fraction_do_not_depend_on_global_context(self):
        token = '1234567890123456789012345678901234567890.00000000000000000001'
        with localcontext() as ctx:
            ctx.prec = 6
            result = self.api.quarter_flow(observation('201106', token),
                        observation('201103', '1234567890123456789012345678901234567890'))
        self.fraction(result, 1, 100000000000000000000)

    def test_flow_periods_are_quarterly_in_core_only(self):
        for period in ['200912', '202503', '201101', '201113', '2011-03', '2011031', 201103]:
            with self.subTest(period=period):
                self.unavailable(self.api.quarter_flow(observation(period, '10')),
                                 'invalid_period')

    def test_ttm_crosses_year_and_preserves_all_native_dependencies(self):
        q, raw = self.year('2011')
        next_q = self.api.quarter_flow(observation('201203', '2'))
        result = self.api.flow_12_months(q[1:] + [next_q], '201203')
        self.fraction(result, 35)
        self.assertEqual((result['start'], result['end']),
                         ('2011-04-01', '2012-03-31'))
        self.assertEqual(result['inputs'], raw[1:2] + raw[:1] + raw[2:3] +
                         raw[3:] + raw[2:3] + [observation('201203', '2')])

    def test_ttm_uses_exact_fractions_never_rounded_display(self):
        q, _ = self.year()
        for result in q:
            result['value_fraction'] = {'numerator': '1', 'denominator': '3'}
            result['value'] = '0.3'  # Intentionally unusable display.
        result = self.api.flow_12_months(q, '201112')
        self.fraction(result, 4, 3)
        self.assertEqual(result['value'], '1.' + '3' * 99)

    def test_display_half_even_and_traps_are_local_to_the_calculation(self):
        # At the 100th significant digit: 2.5 ties to even 2; 3.5 ties to 4.
        with localcontext() as context:
            context.prec = 6
            context.rounding = ROUND_DOWN
            context.traps[Inexact] = True
            even = self.api.quarter_flow(observation('201103', '1.' + '0'*98 + '25'))
            odd = self.api.quarter_flow(observation('201103', '1.' + '0'*98 + '35'))
        self.assertEqual(even['value'], '1.' + '0'*98 + '2')
        self.assertEqual(odd['value'], '1.' + '0'*98 + '4')

    def test_ttm_requires_complete_ordered_disjoint_quarters_and_requested_end(self):
        q, _ = self.year()
        for quarters in [q[:3], q + q[:1], q[:2] + q[1:2] + q[3:], list(reversed(q))]:
            with self.subTest(periods=[r['period'] for r in quarters]):
                self.unavailable(self.api.flow_12_months(quarters, '201112'),
                                 'insufficient_history' if len(quarters) < 4 else 'invalid_sequence')
        broken = deepcopy(q)
        broken[1]['start'] = '2011-03-31'
        self.unavailable(self.api.flow_12_months(broken, '201112'), 'invalid_interval')
        self.unavailable(self.api.flow_12_months(q, '201109'), 'invalid_sequence')
        for end in ['201003', '201006', '201009']:
            self.unavailable(self.api.flow_12_months([], end), 'insufficient_history')

    def test_ttm_propagates_noncalculable_and_guards_definition_and_fraction(self):
        q, _ = self.year()
        q[1] = self.api.quarter_flow(observation('201106', '25'))
        self.unavailable(self.api.flow_12_months(q, '201112'), 'missing_previous')
        q, _ = self.year()
        q[2]['definition_id'] = 'other'
        self.unavailable(self.api.flow_12_months(q, '201112'), 'incompatible_definition')
        q, _ = self.year()
        q[2]['value_fraction']['denominator'] = '0'
        self.unavailable(self.api.flow_12_months(q, '201112'), 'invalid_fraction')

    def test_stock_days_are_trapezoidal_with_leap_year_and_100_digit_display(self):
        for year, numerator, denominator in [('2011', 31700, 181), ('2012', 175, 1)]:
            points = [stock(str(int(year)-1)+'12', '100'), stock(year+'03', '200'),
                      stock(year+'06', '200')]
            result = self.api.mean_stock(points, date(int(year)-1, 12, 31),
                                         date(int(year), 6, 30))
            self.fraction(result, numerator, denominator)
            self.assertEqual(result['inputs'], points)
        result = self.api.mean_stock([stock('201012', '0'), stock('201103', '300')],
                                     date(2010, 12, 31), date(2011, 3, 31))
        self.fraction(result, 150)

    def test_annual_stock_uses_five_points_and_real_91_92_day_weights(self):
        points = [stock(p, t) for p, t in [('201012', '0'), ('201103', '100'),
                  ('201106', '200'), ('201109', '300'), ('201112', '400')]]
        # Areas: 50*90 + 150*91 + 250*92 + 350*92 = 73350.
        self.fraction(self.api.mean_stock(points, date(2010, 12, 31), date(2011, 12, 31)),
                      14670, 73)

    def test_missing_opening_and_inner_stock_do_not_shorten_horizon(self):
        points = [stock('201012', '100'), stock('201103', '200'), stock('201106', '200')]
        args = (date(2010, 12, 31), date(2011, 6, 30))
        self.unavailable(self.api.mean_stock(points[1:], *args), 'missing_opening')
        self.unavailable(self.api.mean_stock(points[::2], *args), 'missing_stock_point')
        self.unavailable(self.api.mean_stock(points[:2], *args), 'missing_stock_point')

    def test_duplicate_reversed_nonquarter_and_period_mismatch_do_not_calculate(self):
        points = [stock('201012', '100'), stock('201103', '200'), stock('201106', '200')]
        args = (date(2010, 12, 31), date(2011, 6, 30))
        for malformed in [points[:1]+points, list(reversed(points)),
                          [points[0], stock('201102', '200'), points[2]]]:
            self.assertNotEqual(self.api.mean_stock(malformed, *args)['status'], 'ok')
        self.unavailable(self.api.mean_stock(points, date(2010, 12, 30), args[1]),
                         'invalid_interval')
        self.unavailable(self.api.mean_stock(points, args[0], args[0]), 'invalid_interval')

    def test_opening_200912_is_stock_only_and_does_not_enable_2009_horizon(self):
        points = [stock('200912', '100'), stock('201003', '200')]
        self.fraction(self.api.mean_stock(points, date(2009, 12, 31), date(2010, 3, 31)), 150)
        self.unavailable(self.api.mean_stock([stock('200909', '100')] + points,
                         date(2009, 9, 30), date(2010, 3, 31)), 'invalid_interval')
        self.unavailable(self.api.mean_stock([stock('202412', '100'), stock('202503', '200')],
                         date(2024, 12, 31), date(2025, 3, 31)), 'invalid_interval')

    def test_stock_compatibility_and_native_states_are_not_imputed(self):
        start, end = date(2010, 12, 31), date(2011, 3, 31)
        for changes, status in [({'definition_id': 'changed'}, 'incompatible_definition'),
                                ({'unit_key': ('financial', '2', 'other')}, 'incompatible_unit'),
                                ({'scale': 'USD'}, 'incompatible_scale'),
                                ({'window_rule': 'native-semester-analysis-v2'},
                                 'incompatible_window'), ({'token': None}, 'native_null')]:
            last = stock('201103', '200')
            last.update(changes)
            self.unavailable(self.api.mean_stock([stock('201012', '100'), last], start, end), status)

    def test_inputs_remain_unchanged_and_control_flags_survive(self):
        points = [stock('201012', '100', flags=['annual_control_not_continuous']),
                  stock('201103', '200')]
        before = deepcopy(points)
        result = self.api.mean_stock(points, date(2010, 12, 31), date(2011, 3, 31))
        self.assertEqual(points, before)
        self.assertIn('annual_control_not_continuous', result['flags'])
        points[0]['sources'][0]['file'] = 'changed-after-call'
        self.assertEqual(result['inputs'][0]['sources'][0]['file'], 'captured.json')


if __name__ == '__main__':
    unittest.main()

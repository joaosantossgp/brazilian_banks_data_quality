"""Offline causal checks; all admissions/projections use the real reader."""
import copy
import hashlib
import importlib
import json
import io
from pathlib import Path
import unittest
import weakref
import tempfile
from unittest.mock import patch
from contextlib import contextmanager
from contextlib import redirect_stdout
import test_financial_acquisition_batch as batch_fixtures

import test_financial_report_profiles as fixtures
from test_financial_report_profiles import profiles, dump, sha
from bank_quality import financial_reports as reader
from bank_quality import financial_parquet as dispatch


RESOURCES = {'deadline_seconds': 30, 'min_available_physical_bytes': 1,
             'min_available_commit_bytes': 1, 'min_free_disk_bytes': 1,
             'sample_interval_seconds': .01}


class JournalHeadRecoveryTests(unittest.TestCase):
    def test_sleep_overshoot_does_not_schedule_another_replace(self):
        from bank_quality import financial_pipeline as api
        with tempfile.TemporaryDirectory(dir=profiles.CHECKOUT_ROOT / '.scratch') as folder:
            journal = api._Journal(Path(folder) / 'run', {'sha256': 'a' * 64}, create=True)
            clock = [0.0]
            error = PermissionError('synthetic transient denial')
            error.winerror = 5
            def sleep(delay):
                clock[0] = 1.0
            with patch.object(api.sys, 'platform', 'win32'), patch.object(api.time, 'monotonic', side_effect=lambda: clock[0]), patch.object(api.time, 'sleep', side_effect=sleep), patch.object(api.os, 'replace', side_effect=error) as replacement:
                with self.assertRaises(PermissionError) as caught:
                    journal.append('start', 201003, 'admit', {})
            self.assertIs(caught.exception, error)
            self.assertEqual(replacement.call_count, 1)

    def test_other_errors_and_non_windows_are_not_retried(self):
        from bank_quality import financial_pipeline as api
        for platform, code in [('win32', 87), ('linux', 5)]:
            with self.subTest(platform=platform, code=code), tempfile.TemporaryDirectory(dir=profiles.CHECKOUT_ROOT / '.scratch') as folder:
                journal = api._Journal(Path(folder) / 'run', {'sha256': 'a' * 64}, create=True)
                error = PermissionError('synthetic unsupported error')
                error.winerror = code
                with patch.object(api.sys, 'platform', platform), patch.object(api.os, 'replace', side_effect=error) as replace:
                    with self.assertRaises(PermissionError):
                        journal.append('start', 201003, 'admit', {})
                self.assertEqual(replace.call_count, 1)

    def test_changed_pending_is_rejected_before_retry(self):
        from bank_quality import financial_pipeline as api
        with tempfile.TemporaryDirectory(dir=profiles.CHECKOUT_ROOT / '.scratch') as folder:
            journal = api._Journal(Path(folder) / 'run', {'sha256': 'a' * 64}, create=True)
            previous = journal.head.read_bytes()
            def replace(source, target):
                source.write_bytes(b'changed')
                error = PermissionError('synthetic transient denial')
                error.winerror = 5
                raise error
            with patch.object(api.sys, 'platform', 'win32'), patch.object(api.os, 'replace', side_effect=replace) as replacement:
                with self.assertRaises(api.IntegrityError):
                    journal.append('start', 201003, 'admit', {})
            self.assertEqual(replacement.call_count, 1)
            self.assertEqual(journal.head.read_bytes(), previous)

    def test_transient_windows_denial_recovers_without_rewriting_journal(self):
        from bank_quality import financial_pipeline as api
        with tempfile.TemporaryDirectory(dir=profiles.CHECKOUT_ROOT / '.scratch') as folder:
            root = Path(folder) / 'run'
            journal = api._Journal(root, {'sha256': 'a' * 64}, create=True)
            original = api.os.replace
            calls = []
            def replace(source, target):
                calls.append((source, target))
                if len(calls) == 1:
                    error = PermissionError('synthetic transient denial')
                    error.winerror = 5
                    raise error
                return original(source, target)
            with patch.object(api.sys, 'platform', 'win32'), patch.object(api.os, 'replace', replace):
                journal.append('start', 201003, 'admit', {})
            self.assertEqual(len(calls), 2)
            self.assertEqual(len(journal.path.read_bytes().splitlines()), 1)
            self.assertEqual(json.loads(journal.head.read_bytes()), journal.projection())

    def test_persistent_denial_keeps_previous_head_and_pending(self):
        from bank_quality import financial_pipeline as api
        with tempfile.TemporaryDirectory(dir=profiles.CHECKOUT_ROOT / '.scratch') as folder:
            journal = api._Journal(Path(folder) / 'run', {'sha256': 'a' * 64}, create=True)
            previous = journal.head.read_bytes()
            error = PermissionError('synthetic persistent denial')
            error.winerror = 32
            with patch.object(api.sys, 'platform', 'win32'), patch.object(api.os, 'replace', side_effect=error) as replace:
                with self.assertRaises(PermissionError):
                    journal.append('start', 201003, 'admit', {})
            self.assertEqual(replace.call_count, 5)
            self.assertEqual(journal.head.read_bytes(), previous)
            self.assertTrue((journal.root / 'head-1.pending').is_file())
            self.assertEqual(len(journal.path.read_bytes().splitlines()), 1)


@contextmanager
def batch_fixture():
    """Enrich the existing physical acquisition fixture; do not fake acceptance."""
    original_catalog = batch_fixtures.catalog_entry
    original_source = batch_fixtures.BatchCompositionTests.bounded_source
    def catalog(period):
        value = original_catalog(period)
        for entry in value['files']:
            if 'trel' in entry:
                entry['trel']['c'][0]['fid'] = 8
        return value
    def source(f, target, payload):
        if target['role'] == 'dictionary':
            payload = [{**row, 'n': 'Synthetic native binding'} for row in payload]
        result = original_source(f, target, payload)
        manifest_path = f.root / result['manifest_path']
        manifest = json.loads(manifest_path.read_bytes())
        manifest.update(retrieved_at_utc='2026-10-01T12:00:00Z',
                        response_headers=dict(manifest['response_headers_raw']))
        sidecar_path = manifest_path.parent / manifest['response_metadata_path']
        sidecar = {k: manifest[k] for k in ('url', 'method', 'context', 'http_status', 'final_url', 'response_headers_raw')}
        sidecar_path.write_bytes(dump(sidecar))
        manifest['response_metadata_sha256'] = sha(sidecar_path.read_bytes())
        manifest_path.write_bytes(dump(manifest))
        result.update(manifest_sha256=sha(manifest_path.read_bytes()), provenance_sha256=sha(dump(manifest)))
        return result
    @contextmanager
    def claim(path):
        path.touch(exist_ok=True)
        yield
    with patch.object(batch_fixtures, 'catalog_entry', catalog), \
            patch.object(batch_fixtures.BatchCompositionTests, 'bounded_source', source), \
            patch.object(batch_fixtures.BatchAuthorityTests, 'bounded_source', source), \
            fixtures.acquisition_batch_bridge() as f, \
            patch('bank_quality.windows_acquisition.exclusive_claim', claim), \
            patch('bank_quality.windows_acquisition._current_identity', return_value={'pid': 999999998, 'creation_time': 1}):
        registry_path = f.pkg / 'financial-reports-registry.json'
        registry = json.loads(registry_path.read_bytes())
        offered = [year * 100 + quarter for year in range(2010, 2027) for quarter in (3, 6, 9, 12)
                   if year * 100 + quarter <= 202606 and year * 100 + quarter not in batch_fixtures.ACQUIRE]
        for period in offered:
            sentinel = copy.deepcopy(registry['members'][0])
            sentinel['selection']['period'] = period
            sentinel['limitations'] = ['Inactive synthetic preservation sentinel; not native historical evidence']
            registry['members'].append(sentinel)
        registry_path.write_bytes(dump(registry))
        yield f


def offline_launch(api, spec_path, spec_hash, *, resources, before_resume):
    """Replace OS spawning only; stage parsing, authoring, reader and output are real."""
    spec = api._read({'path': api._name(spec_path), 'sha256': spec_hash})
    before_resume({'pid': 999999999, 'creation_time': 1, 'contained': True})
    api._execute_spec(spec)
    return {'tree_extinct': True, 'deadline_reached': False, 'elapsed_seconds': .001,
            'guard': '', 'exit_code': 0, 'resources': resources,
            'observed_identities': [{'pid': 999999999, 'creation_time': 1}]}


class HistoricalPipelineTests(unittest.TestCase):
    def test_batch_integrity_halt_quarantines_completed_window(self):
        api = importlib.import_module('bank_quality.financial_pipeline')
        with tempfile.TemporaryDirectory() as folder, patch.object(profiles, 'CHECKOUT_ROOT', Path(folder)), \
                patch.object(profiles, 'PACKAGE_ROOT', Path(folder) / 'bank_quality'):
            member = {'selection': {'period': 201003}, 'installed_profile_path': 'absent.json',
                      'profile': {'sha256': 'a' * 64}, **{key: 0 for key in
                      ('nodes', 'leaves', 'groups', 'kinds', 'cadastro_columns', 'required_sources')}}
            doc = {'contract': api.PLAN_V2, 'members': [member],
                   'source_state': {'accepted_before': 0}, 'registry_proposed': {'sha256': 'b' * 64}}
            journal = api._Journal(Path(folder) / 'run', {'sha256': 'c' * 64}, create=True)
            journal.append('start', 201003, 'compare', {'spec': {'sha256': 'd' * 64}})
            journal.append('finish', 201003, 'compare', {'start_sequence': 1,
                           'receipt': {'path': 'receipt.json', 'sha256': 'e' * 64}})
            with patch.object(api, '_validate_receipt', return_value={'status': 'complete', 'summary': {}}):
                self.assertEqual(api._score(doc, journal)['scoreboard']['window_accepted'], 1)
                journal.append('halt', 'batch', 'compare', {'code': 'integrity', 'message': 'changed bundle'})
                result = api._score(doc, journal)
            self.assertEqual(result['status'], 'halted')
            self.assertEqual(result['scoreboard']['window_accepted'], 0)
            self.assertEqual(result['members'][0]['terminal_state'], 'quarantined')
            self.assertEqual(result['members'][0]['errors'][0]['message'], 'changed bundle')

    def test_final_integrity_failure_prevents_complete_result(self):
        api = importlib.import_module('bank_quality.financial_pipeline')

        @contextmanager
        def claim(path):
            path.touch(exist_ok=True)
            yield

        with tempfile.TemporaryDirectory() as folder, patch.object(profiles, 'CHECKOUT_ROOT', Path(folder)):
            root = Path(folder)
            document = {'contract': api.PLAN_V2, 'destinations': {'execution': 'data/runs/final-gate'},
                        'members': [], 'limitations': [], 'source_state': {'accepted_before': 0},
                        'batch': {'bundle': {'path': 'missing-bundle.json', 'sha256': 'f' * 64}}}
            (root / 'data/runs').mkdir(parents=True)
            path = root / 'plan.json'
            path.write_bytes(dump(document))
            # Isolate the closure boundary; payload integrity itself is exercised
            # by the causal owner/sibling corruption test below.
            with patch.object(api, '_verify_plan_document',
                    side_effect=[None, api.IntegrityError('changed completed sibling body')]) as validation, \
                    patch.object(api.native, 'exclusive_claim', claim):
                result = api.run_pipeline(path, plan_sha256=sha(path.read_bytes()), resources=RESOURCES)
            self.assertEqual(result['status'], 'halted')
            self.assertEqual(result['scoreboard']['window_accepted'], 0)
            self.assertEqual(api.read_status(path, plan_sha256=sha(path.read_bytes()))['status'], 'halted')
            self.assertEqual(validation.call_count, 2)
            self.assertTrue(all(call.kwargs['verify_native'] is True for call in validation.call_args_list))
            records = [json.loads(line) for line in (root / 'data/runs/final-gate/journal.jsonl').read_bytes().splitlines()]
            self.assertEqual(records[-1]['kind'], 'halt')
            self.assertEqual(records[-1]['data']['code'], 'integrity')
            self.assertIn('changed completed sibling body', records[-1]['data']['message'])

    def test_global_checks_derive_payloads_without_reopening_sibling_bodies(self):
        api = importlib.import_module('bank_quality.financial_pipeline')
        with tempfile.TemporaryDirectory() as folder, patch.object(profiles, 'CHECKOUT_ROOT', Path(folder)):
            root = Path(folder)
            images, handoffs = [], []
            for period in (201003, 201006):
                parent = root / 'data/raw' / str(period)
                parent.mkdir(parents=True)
                body = parent / 'body.json'
                body.write_bytes(dump({'native': period}))
                manifest = parent / 'manifest.json'
                manifest.write_bytes(dump({'body_path': body.name, 'sha256': sha(body.read_bytes()),
                                          'bytes': len(body.read_bytes())}))
                handoffs.append({'sources': [{'manifest_path': api._name(manifest),
                    'manifest_sha256': sha(manifest.read_bytes()), 'body_sha256': sha(body.read_bytes())}]})
                images.extend({'path': api._name(path), 'sha256': sha(path.read_bytes()), 'bytes': len(path.read_bytes())}
                              for path in (body, manifest))
            journal = root / 'data/journal.jsonl'
            journal.write_bytes(b'{}\n')
            images.append({'path': api._name(journal), 'sha256': sha(journal.read_bytes()), 'bytes': 3})
            small = api._global_source_images(images, handoffs)
            self.assertEqual({image['path'] for image in small},
                             {'data/raw/201003/manifest.json', 'data/raw/201006/manifest.json', 'data/journal.jsonl'})
            opened = []
            original = api._stream_sha

            def observed(path):
                opened.append(api._name(path))
                return original(path)

            with patch.object(api, '_stream_sha', side_effect=observed):
                api._authenticate_files(small)
                api._source_bodies(handoffs[0])
            self.assertIn('data/raw/201003/body.json', opened)
            self.assertNotIn('data/raw/201006/body.json', opened)
            self.assertIn('data/journal.jsonl', opened)
            changed = copy.deepcopy(images)
            changed[0]['sha256'] = 'f' * 64
            with self.assertRaisesRegex(api.IntegrityError, 'payload inventory'):
                api._global_source_images(changed, handoffs)
            (root / 'data/raw/201003/body.json').write_bytes(b'changed')
            with self.assertRaises(api.IntegrityError):
                api._source_bodies(handoffs[0])
            (root / 'data/raw/201006/body.json').write_bytes(b'changed sibling')
            with self.assertRaises(api.IntegrityError):
                api._authenticate_files(images)

    def test_historical_window_reuses_preparation_and_all_seven_stages(self):
        api = importlib.import_module('bank_quality.financial_pipeline')

        @contextmanager
        def claim(path):
            path.touch(exist_ok=True)
            yield

        with fixtures.historical_acquisition_bridge() as f, \
                patch('bank_quality.windows_acquisition.exclusive_claim', claim), \
                patch('bank_quality.windows_acquisition._current_identity',
                      return_value={'pid': 999999998, 'creation_time': 1}), \
                patch.object(api.contained, 'run_contained_stage',
                             lambda *a, **kw: offline_launch(api, *a, **kw)):
            registry_path = f.pkg / 'financial-reports-registry.json'
            registry = json.loads(registry_path.read_bytes())
            selected = {m['selection']['period'] for m in registry['members']}
            for year in range(2010, 2027):
                for quarter in (3, 6, 9, 12):
                    period = year * 100 + quarter
                    if period <= 202606 and period not in selected:
                        sentinel = copy.deepcopy(registry['members'][0])
                        sentinel['selection']['period'] = period
                        sentinel['limitations'] = ['Inactive preservation sentinel; not accepted native data']
                        registry['members'].append(sentinel)
            registry_path.write_bytes(dump(registry))
            before = registry_path.read_bytes()
            output = f.root / 'data/runs/historical-pipeline'
            with self.assertRaisesRegex(api.IntegrityError, 'rejects legacy accepted supplement'):
                api.prepare_profiles(f.bundle_path, f.handoff_path, output,
                    bundle_sha256=sha(f.bundle_path.read_bytes()),
                    bootstrap_sha256=sha((f.bundle_path.parent / 'bootstrap.json').read_bytes()),
                    handoff_sha256=sha(f.handoff_path.read_bytes()), resources=RESOURCES,
                    accepted_supplement_path=f.handoff_path,
                    accepted_supplement_sha256=sha(f.handoff_path.read_bytes()))
            self.assertFalse(output.exists())
            original_bundle = json.loads(f.bundle_path.read_bytes())
            forged_bundle = f.root / 'data/runs/forged-window.json'
            for mutation in ({'window_id': 'F1-01-R1'}, {'acquire_periods': [201003, 202606]},
                             {'policy_sha256': 'f' * 64}):
                forged_bundle.write_bytes(dump(dict(original_bundle, **mutation)))
                with self.subTest(bundle=mutation), self.assertRaises(api.IntegrityError):
                    api._periods({'contract': api.PREPARE_V2,
                        'batch': {'bundle': {'path': api._name(forged_bundle),
                                             'sha256': sha(forged_bundle.read_bytes())}}})
            result = api.prepare_profiles(f.bundle_path, f.handoff_path, output,
                bundle_sha256=sha(f.bundle_path.read_bytes()),
                bootstrap_sha256=sha((f.bundle_path.parent / 'bootstrap.json').read_bytes()),
                handoff_sha256=sha(f.handoff_path.read_bytes()), resources=RESOURCES)
            self.assertEqual(result['status'], 'prepared', result)
            plan_path = f.root / result['plan']['path']
            plan = json.loads(plan_path.read_bytes())
            self.assertEqual(plan['contract'], 'ifdata-financial-sanitization-plan-v2')
            self.assertEqual(result['profile_generated'], [201003, 201006, 201009, 201012])
            self.assertEqual(registry_path.read_bytes(), before)
            for mutation in ({'contract': api.PLAN}, {'members': plan['members'][:-1]},
                             {'members': plan['members'] + [plan['members'][0]]},
                             {'members': [dict(plan['members'][0], selection={
                                 **plan['members'][0]['selection'], 'period': 202606})] + plan['members'][1:]}):
                with self.subTest(plan=list(mutation)), self.assertRaises(api.IntegrityError):
                    api._verify_plan_document(dict(plan, **mutation), RESOURCES, installed=False)
            spec_path = next(path for path in (output / 'preparation/stages').glob('*/spec.json')
                             if json.loads(path.read_bytes())['member'] != 'batch')
            spec = json.loads(spec_path.read_bytes())
            with self.assertRaisesRegex(api.IntegrityError, 'Invalid CPU member/stage'):
                api._execute_spec(dict(spec, member=202606))
            halt = f.bundle_path.parent / 'halt.json'
            try:
                halt.write_bytes(b'{}')
                with self.assertRaisesRegex(api.IntegrityError, 'halt marker'):
                    api._verify_plan_document(plan, RESOURCES, installed=False)
            finally:
                halt.unlink()
            for member in plan['members']:
                target = f.pkg / member['installed_profile_path']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((f.root / member['profile']['path']).read_bytes())
            registry_path.write_bytes((f.root / plan['registry_proposed']['path']).read_bytes())
            run = api.run_pipeline(plan_path, plan_sha256=result['plan']['sha256'], resources=RESOURCES)
            self.assertEqual(run['status'], 'complete', run)
            self.assertEqual(run['scoreboard'], {'coverage_scope': 'authenticated_window',
                'window': 4, 'window_accepted': 4, 'window_remaining': 0})
            self.assertTrue(all(m['milestones']['replay_verified'] for m in run['members']))
            self.assertEqual(len(run['members']), 4)
            status = api.read_status(plan_path, plan_sha256=result['plan']['sha256'])
            self.assertEqual(status['scoreboard'], run['scoreboard'])


class PipelineTests(unittest.TestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('bank_quality.financial_pipeline'),
                             'Offline pipeline coordinator is absent')
        return importlib.import_module('bank_quality.financial_pipeline')

    def fixture(self, *, period=201403, quantity=False):
        f = fixtures.ProfileTests('test_freeze_complete_recompiles_preserves_origins_and_does_not_install')
        f.setUp()
        self.addCleanup(f.doCleanups)
        if period != 201403:
            f.selection = {'period': period, 'perspective': 1005, 'reports': [92, 96, 101, 98]}
            f.prepare(24)
        if quantity:
            for item in f.reports:
                item['report']['c'][0]['fid'] = 2
            catalog = f.archive('catalog', dump(f.catalog_value).replace(b'{"json_number":"1e-27"}', b'1e-27'))
            f.descriptor['catalog'] = {**catalog, 'reference_pointer': '/0'}
            f.handoff['catalog'] = f.descriptor['catalog']
            f.handoff['sources'][0] = catalog
            f.install_registry()
            f.handoff['descriptor_sha256'] = profiles.descriptor_for_selection(f.selection)['descriptor_sha256']
        offer = f.descriptor['source_offers'][0]
        rows = [{f'c{i}': str(f.selection['period']) if i == 1 else str(entity) if i == 0
                 else '3' if quantity and i == 2 else 'opaque' + str(i) for i in range(24)} for entity in range(1, 7)]
        f.handoff['sources'][1] = {**f.archive('cadaster', rows, offer['native_file']), **offer}
        final = f.final()
        for position, area in ((4, 1), (5, 3)):
            offer = f.descriptor['source_offers'][2 if area == 1 else 3]
            value = {'id': area, 'values': [{'e': entity, 'v': [{'i': 7, 'v': value}]}
                      for entity, value in enumerate(['1234567890123.123456789012345678901234567',
                                                     None, '0', 'NA', 'NI', ''], 1)]}
            if area == 3:
                value['values'][-1]['v'] = []
            body = dump(value)
            if area == 1:
                body = body.replace(b'"v":"1234567890123.123456789012345678901234567"',
                                    b'"v":1234567890123.123456789012345678901234567')
            final['sources'][position] = {**f.archive(offer['source_id'], body, offer['native_file'], area), **offer}
        ap, ah = f.write('data/runs/a.json', f.handoff)
        candidate = profiles.compile_metadata_candidate(ap, handoff_sha256=ah)
        cp, ch = f.write('data/runs/candidate.json', candidate)
        bp, bh = f.write('data/runs/b.json', final)
        profile = profiles.freeze_profile(cp, bp, candidate_sha256=ch, final_handoff_sha256=bh)
        pp, ph = f.write(f'bank_quality/financial-reports-profiles/{period}.json', profile)
        f.registry['members'][0].update(profile_path=f'financial-reports-profiles/{period}.json', profile_sha256=ph)
        f.install_registry()
        return f, bp

    def test_resource_policy_is_closed_typed_and_finite_before_writes(self):
        api = self.api()
        for changes in ({'workers': 2}, {'deadline_seconds': True}, {'sample_interval_seconds': float('nan')},
                        {'min_free_disk_bytes': 1.5}, {'min_available_commit_bytes': 0}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                api.validate_resources({**RESOURCES, **changes})
        self.assertEqual(api.validate_resources(RESOURCES), RESOURCES)

    def test_pipeline_validates_all_values_and_replay_before_accepting(self):
        api = self.api()
        f, index = self.fixture()
        admissions, snapshots = [], []
        for name in ('primary', 'replay'):
            admitted = f.root / ('data/derived/' + name)
            projected = f.root / ('data/curated/' + name)
            source = reader.admit(index, admitted)
            result = dispatch.convert_financial(admitted, projected,
                                               source_manifest_sha256=sha((admitted / 'manifest.json').read_bytes()))
            query = api.verify_query(admitted, projected,
                                     source_manifest_sha256=sha((admitted / 'manifest.json').read_bytes()),
                                     manifest_sha256=result['manifest_sha256'])
            self.assertEqual(query['numeric_rows'], 48)
            self.assertEqual(query['cells'], 72)
            self.assertEqual(query['observations'], 68)
            self.assertEqual(query['cadaster_records'], 6)
            self.assertEqual(query['cadaster_columns'], 24)
            self.assertEqual(query['precision_encodings'], {'decimal_text_v1': 8})
            admissions.append(admitted)
            snapshots.append(projected)
        verified = api.compare_replay(*admissions, *snapshots)
        self.assertTrue(verified['replay_verified'])
        metadata = snapshots[1] / 'metadata/financial-diagnostics.json'
        metadata.write_bytes(metadata.read_bytes() + b' ')
        with self.assertRaises(api.IntegrityError):
            api.compare_replay(*admissions, *snapshots)

    def test_query_rejects_altered_csv_even_with_unchanged_snapshot(self):
        api = self.api()
        f, index = self.fixture()
        admitted = f.root / 'data/derived/primary'
        projected = f.root / 'data/curated/primary'
        reader.admit(index, admitted)
        source_pin = sha((admitted / 'manifest.json').read_bytes())
        result = dispatch.convert_financial(admitted, projected, source_manifest_sha256=source_pin)
        (admitted / 'financial-cells.csv').write_bytes(b'tampered')
        with self.assertRaises(api.IntegrityError):
            api.verify_query(admitted, projected, source_manifest_sha256=source_pin,
                             manifest_sha256=result['manifest_sha256'])

    def prepare(self, api, f):
        output = f.root / 'data/runs/pipeline-fixture'
        with patch.object(api.contained, 'run_contained_stage', lambda *a, **kw: offline_launch(api, *a, **kw)):
            result = api.prepare_profiles(f.root / f.refs['bundle_path'], f.root / f.handoff_pin['path'], output,
                bundle_sha256=f.refs['bundle_sha256'], bootstrap_sha256=f.refs['bootstrap_sha256'],
                handoff_sha256=f.handoff_pin['sha256'], resources=RESOURCES)
        self.assertEqual(result['status'], 'prepared', result)
        plan = f.root / result['plan']['path']
        return plan, result['plan']['sha256']

    def install(self, api, f, plan):
        value = json.loads(plan.read_bytes())
        for member in value['members']:
            path = f.pkg / member['installed_profile_path']
            path.parent.mkdir(exist_ok=True)
            path.write_bytes((f.root / member['profile']['path']).read_bytes())
        (f.pkg / 'financial-reports-registry.json').write_bytes((f.root / value['registry_proposed']['path']).read_bytes())

    def test_prepare_writes_seven_profiles_and_one_uninstalled_registry_proposal(self):
        api = self.api()
        with batch_fixture() as f:
            registry = (f.pkg / 'financial-reports-registry.json').read_bytes()
            plan, pin = self.prepare(api, f)
            value = json.loads(plan.read_bytes())
            self.assertEqual([m['selection']['period'] for m in value['members']],
                             [202406, 202409, 202506, 202509, 202512, 202603, 202606])
            self.assertEqual((f.pkg / 'financial-reports-registry.json').read_bytes(), registry)
            self.assertEqual(sha(plan.read_bytes()), pin)
            proposed = json.loads((f.root / value['registry_proposed']['path']).read_bytes())
            self.assertEqual(len(proposed['members']), 66)
            before = json.loads(registry)
            untouched = lambda doc: [m for m in doc['members'] if m['selection']['period'] not in batch_fixtures.ACQUIRE]
            self.assertEqual(untouched(proposed), untouched(before))
            for member in value['members']:
                profile = json.loads((f.root / member['profile']['path']).read_bytes())
                self.assertEqual(profile['missing_sources'], [])
                self.assertEqual(len(profile['reports']), 4)
                self.assertEqual(set(profile['source_pins']), set(profile['required_sources']))
                self.assertFalse((f.pkg / member['installed_profile_path']).exists())
            self.assertEqual(api.read_status(plan, plan_sha256=pin)['scoreboard']['accepted_before'], 3)

    def test_run_refuses_unreviewed_installation_or_changed_global_pin(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            with patch.object(api.contained, 'run_contained_stage', side_effect=AssertionError('dispatched')):
                with self.assertRaises(api.IntegrityError):
                    api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
                self.install(api, f, plan)
                with self.assertRaises(api.IntegrityError):
                    api.run_pipeline(plan, plan_sha256='0' * 64, resources=RESOURCES)
                registry = f.pkg / 'financial-reports-registry.json'
                registry.write_bytes(registry.read_bytes() + b' ')
                with self.assertRaises(api.IntegrityError):
                    api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)

    def test_resume_skips_verified_stages_and_quarantines_partial_outputs(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            with patch.object(api.contained, 'run_contained_stage', lambda *a, **kw: offline_launch(api, *a, **kw)):
                result = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
            self.assertEqual(result['status'], 'complete', result)
            self.assertEqual(result['scoreboard']['window_accepted'], 7)
            with patch.object(api.contained, 'run_contained_stage', side_effect=AssertionError('verified stage redispatched')):
                resumed = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES, resume=True)
            self.assertEqual(resumed['scoreboard']['window_accepted'], 7)
            doc = json.loads(plan.read_bytes())
            extra = f.root / doc['members'][0]['destinations']['admission'] / 'extra.json'
            extra.write_bytes(b'{}')
            with self.assertRaises(api.IntegrityError):
                api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES, resume=True)
            extra.unlink()
            journal = f.root / doc['destinations']['execution'] / 'journal.jsonl'
            original = journal.read_bytes()
            journal.write_bytes(original[:-1])
            with self.assertRaises(api.IntegrityError):
                api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES, resume=True)
            journal.write_bytes(original)
            head = f.root / json.loads(plan.read_bytes())['destinations']['execution'] / 'head.json'
            head.write_bytes(b'{}')
            with self.assertRaises(api.IntegrityError):
                api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES, resume=True)

    def test_incomplete_member_is_quarantined_without_deleting_its_partial_output(self):
        api = self.api()
        class Interrupted(BaseException):
            pass
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            def interrupted(spec_path, spec_hash, *, resources, before_resume):
                spec = api._read({'path': api._name(spec_path), 'sha256': spec_hash})
                before_resume({'pid': 999999999, 'creation_time': 1, 'contained': True})
                partial = f.root / spec['outputs']['admit']
                partial.mkdir(parents=True)
                (partial / 'partial.csv').write_bytes(b'preserved')
                raise Interrupted()
            with patch.object(api.contained, 'run_contained_stage', interrupted), self.assertRaises(Interrupted):
                api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
            doc = json.loads(plan.read_bytes())
            partial = f.root / doc['members'][0]['destinations']['admission'] / 'partial.csv'
            with patch.object(api.native, 'identity_extinct', return_value=True), \
                    patch.object(api.contained, 'run_contained_stage', lambda *a, **kw: offline_launch(api, *a, **kw)):
                resumed = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES, resume=True)
            self.assertEqual(partial.read_bytes(), b'preserved')
            self.assertEqual(resumed['status'], 'partial')
            self.assertEqual(resumed['scoreboard']['window_accepted'], 6)
            self.assertEqual(resumed['members'][0]['state'], 'quarantined')
            self.assertFalse(resumed['members'][0]['milestones']['replay_verified'])

    def test_adapter_value_errors_are_global_and_stop_after_convert(self):
        api = self.api()
        for mode in ('payload_hash', 'unknown'):
            with self.subTest(mode=mode), batch_fixture() as f:
                plan, pin = self.prepare(api, f)
                self.install(api, f, plan)
                convert = api.conversion.convert_financial
                dispatched, adapter_errors = [], []
                def conversion(source, destination, **kwargs):
                    if mode == 'unknown':
                        raise ValueError('unclassified adapter failure')
                    cells = source / 'financial-cells.csv'
                    cells.write_bytes(cells.read_bytes() + b' ')
                    try:
                        return convert(source, destination, **kwargs)
                    except ValueError as error:
                        adapter_errors.append(error)
                        raise
                def launch(*args, **kwargs):
                    spec = api._read({'path': api._name(args[0]), 'sha256': args[1]})
                    dispatched.append((spec['member'], spec['stage']))
                    if spec['member'] != 202406:
                        raise api.contained.ResourceError('test stops unexpected dispatch')
                    return offline_launch(api, *args, **kwargs)
                with patch.object(api.conversion, 'convert_financial', conversion), \
                        patch.object(api.contained, 'run_contained_stage', launch):
                    result = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
                self.assertEqual(dispatched, [(202406, 'admit'), (202406, 'convert')])
                self.assertEqual(result['status'], 'halted')
                self.assertEqual(result['scoreboard']['window_accepted'], 0)
                self.assertTrue(result['members'][0]['milestones']['admitted'])
                self.assertEqual(result['members'][0]['state'], 'quarantined')
                if mode == 'payload_hash':
                    self.assertEqual(len(adapter_errors), 1, 'The real adapter did not reject its physical input')
                    self.assertEqual(result['members'][0]['errors'][0]['code'], 'integrity')
                else:
                    self.assertEqual(result['members'][0]['errors'][0]['code'], 'unexpected')

    def test_serialized_previous_owner_halt_is_loaded_inside_claim(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            doc = json.loads(plan.read_bytes())
            root = f.root / doc['destinations']['execution']
            ref = {'path': api._name(plan), 'sha256': pin}
            api._Journal(root, ref, create=True)
            @contextmanager
            def claim(path):
                previous = api._Journal(root, ref)
                previous.append('halt', 202406, 'admit', {'code': 'integrity', 'message': 'previous owner halted'})
                yield
            dispatched = []
            def launch(*args, **kwargs):
                dispatched.append(True)
                raise api.contained.ResourceError('test stops unexpected dispatch')
            with patch.object(api.native, 'exclusive_claim', claim), \
                    patch.object(api.contained, 'run_contained_stage', launch):
                result = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES, resume=True)
            self.assertEqual(dispatched, [], 'Caller dispatched using journal state read before claim')
            journal = api._Journal(root, ref)
            self.assertEqual([(r['sequence'], r['kind']) for r in journal.records], [(1, 'halt')])
            self.assertEqual(result['status'], 'halted')

    def test_real_native_value_validation_is_local_after_reauthentication(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            native_value, dispatched, native_errors = api.admission._value, [], []
            first = True
            def malformed_native_value(value, kind):
                nonlocal first
                if first:
                    first = False
                    value = True
                try:
                    return native_value(value, kind)
                except ValueError as error:
                    native_errors.append(error)
                    raise
            def launch(*args, **kwargs):
                spec = api._read({'path': api._name(args[0]), 'sha256': args[1]})
                dispatched.append((spec['member'], spec['stage']))
                if spec['member'] == 202409 and spec['stage'] == 'convert':
                    raise api.contained.ResourceError('test stops after proving local continuation')
                return offline_launch(api, *args, **kwargs)
            with patch.object(api.admission, '_value', malformed_native_value), \
                    patch.object(api.contained, 'run_contained_stage', launch):
                result = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
            self.assertEqual(len(native_errors), 1)
            self.assertEqual(type(native_errors[0]).__name__, 'NativeSchemaError')
            self.assertEqual(dispatched, [(202406, 'admit'), (202409, 'admit'), (202409, 'convert')])
            self.assertEqual(result['members'][0]['state'], 'failed')
            self.assertEqual(result['members'][0]['errors'][0]['code'], 'native_schema')
            self.assertTrue(result['members'][1]['milestones']['admitted'])
            self.assertEqual(result['scoreboard']['window_accepted'], 0)

    def test_typed_native_failure_rechecks_derived_parquet_payloads(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            connect, dispatched = api.parquet.snapshot_connection, []
            def tampered_snapshot(destination, **kwargs):
                metadata = destination / 'metadata/financial-diagnostics.json'
                metadata.write_bytes(metadata.read_bytes() + b' ')
                return api.admission._value(True, 'numeric')
            def launch(*args, **kwargs):
                spec = api._read({'path': api._name(args[0]), 'sha256': args[1]})
                dispatched.append((spec['member'], spec['stage']))
                if spec['member'] != 202406:
                    raise api.contained.ResourceError('test stops unexpected dispatch')
                return offline_launch(api, *args, **kwargs)
            with patch.object(api.parquet, 'snapshot_connection', tampered_snapshot), \
                    patch.object(api.contained, 'run_contained_stage', launch):
                result = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
            self.assertEqual(dispatched, [(202406, 'admit'), (202406, 'convert'), (202406, 'query')])
            self.assertEqual(result['status'], 'halted')
            self.assertEqual(result['members'][0]['errors'][0]['code'], 'integrity')
            self.assertTrue(result['members'][0]['milestones']['parquet_verified'])
            self.assertEqual(result['members'][0]['state'], 'quarantined')

    def test_fresh_execution_does_not_adopt_foreign_journal_before_claim(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            doc = json.loads(plan.read_bytes())
            root = f.root / doc['destinations']['execution']
            ref = {'path': api._name(plan), 'sha256': pin}
            @contextmanager
            def claim(path):
                path.touch(exist_ok=True)
                if (root / 'journal.jsonl').exists():
                    previous = api._Journal(root, ref)
                else:
                    previous = api._Journal(root, ref, create=True, reserved=True)
                previous.append('halt', 202406, 'admit', {'code': 'integrity', 'message': 'foreign owner committed'})
                yield
            with patch.object(api.native, 'exclusive_claim', claim), \
                    patch.object(api.contained, 'run_contained_stage', side_effect=AssertionError('fresh caller dispatched')):
                with self.assertRaises(api.IntegrityError):
                    api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
            journal = api._Journal(root, ref)
            self.assertEqual([(r['sequence'], r['kind']) for r in journal.records], [(1, 'halt')])
            self.assertFalse(list(root.glob('result-*')), 'Fresh caller accepted the pre-existing journal')

    def test_reader_typed_schema_boundary_preserves_context_failures(self):
        api = self.api()
        for value in (True, [], {}, 'invalid numeric token'):
            with self.subTest(value=value), self.assertRaises(ValueError) as caught:
                api.admission._value(value, 'numeric')
            self.assertEqual(type(caught.exception).__name__, 'NativeSchemaError')
        with self.assertRaises(ValueError) as caught:
            api.admission._cadaster([{'c0': '1', 'c1': 'wrong period'}],
                                   {'period': 202406, 'cadaster_columns': ['c0', 'c1']})
        self.assertIs(type(caught.exception), ValueError, 'Reference mismatch must remain unclassified/global')

    def test_batch_preparation_failure_is_global_even_when_native_typed(self):
        api = self.api()
        with batch_fixture() as f:
            output = f.root / 'data/runs/typed-batch-failure'
            dispatched = []
            def action(spec, doc):
                return api.admission._value(True, 'numeric')
            def launch(*args, **kwargs):
                spec = api._read({'path': api._name(args[0]), 'sha256': args[1]})
                dispatched.append((spec['member'], spec['stage']))
                return offline_launch(api, *args, **kwargs)
            with patch.object(api, '_stage_action', action), \
                    patch.object(api.contained, 'run_contained_stage', launch):
                result = api.prepare_profiles(f.root / f.refs['bundle_path'], f.root / f.handoff_pin['path'], output,
                    bundle_sha256=f.refs['bundle_sha256'], bootstrap_sha256=f.refs['bootstrap_sha256'],
                    handoff_sha256=f.handoff_pin['sha256'], resources=RESOURCES)
            self.assertEqual(result['status'], 'halted')
            self.assertEqual(dispatched, [('batch', 'prepare-batch')])
            request = api._ref(output / 'prepare-request.json')
            journal = api._Journal(output / 'preparation', request)
            self.assertTrue(journal.state()[3], 'Aggregate preparation failure was recorded as local')
            receipt = api._read(journal.state()[1][('batch', 'prepare-batch')]['data']['receipt'])
            self.assertEqual(receipt['status'], 'halted')
            self.assertFalse((output / 'plan.json').exists())

    def test_member_schema_failure_continues_but_integrity_or_resource_failure_halts(self):
        api = self.api()
        for mode in ('local', 'integrity', 'resource'):
            with self.subTest(mode=mode), batch_fixture() as f:
                plan, pin = self.prepare(api, f)
                self.install(api, f, plan)
                action = api._stage_action
                dispatched = []
                def execute(spec, doc):
                    if spec['member'] == 202406 and spec['stage'] == 'admit':
                        if mode == 'local':
                            raise api.StageError('fixture_schema', 'known native schema mismatch')
                        if mode == 'integrity':
                            raise api.IntegrityError('authenticated origin changed')
                    return action(spec, doc)
                def launch(*args, **kwargs):
                    spec = api._read({'path': api._name(args[0]), 'sha256': args[1]})
                    dispatched.append((spec['member'], spec['stage']))
                    if mode == 'resource':
                        raise api.contained.ResourceError('machine resource guard')
                    return offline_launch(api, *args, **kwargs)
                with patch.object(api, '_stage_action', execute), patch.object(api.contained, 'run_contained_stage', launch):
                    result = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
                if mode == 'local':
                    self.assertEqual(result['status'], 'partial')
                    self.assertEqual(result['scoreboard']['window_accepted'], 6)
                    self.assertEqual(result['members'][0]['state'], 'failed')
                else:
                    self.assertEqual(result['status'], 'halted')
                    self.assertEqual(dispatched, [(202406, 'admit')])
                    self.assertEqual(result['scoreboard']['window_accepted'], 0)

    def test_cli_prepare_run_status_and_exit_codes_are_offline(self):
        api = self.api()
        path = Path(api.__file__).parents[1] / 'scripts/run-financial-pipeline.py'
        self.assertTrue(path.is_file(), 'Thin prepare/run/status CLI is absent')
        spec = importlib.util.spec_from_file_location('financial_pipeline_cli', path)
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        with batch_fixture() as f:
            resource_file = f.root / 'data/runs/resources.json'
            resource_file.write_bytes(dump(RESOURCES))
            policy_args = ['--resources', str(resource_file), '--resources-sha256', sha(resource_file.read_bytes())]
            output = f.root / 'data/runs/cli-fixture'
            stream = io.StringIO()
            with patch.object(api.contained, 'run_contained_stage', lambda *a, **kw: offline_launch(api, *a, **kw)), redirect_stdout(stream):
                code = cli.main(['prepare', '--bundle', str(f.root / f.refs['bundle_path']),
                    '--bundle-sha256', f.refs['bundle_sha256'], '--bootstrap-sha256', f.refs['bootstrap_sha256'],
                    '--handoff', str(f.root / f.handoff_pin['path']), '--handoff-sha256', f.handoff_pin['sha256'],
                    '--output', str(output), *policy_args])
            self.assertEqual(code, 0)
            result = json.loads(stream.getvalue())
            plan = f.root / result['plan']['path']
            plan_args = ['--plan', str(plan), '--plan-sha256', result['plan']['sha256']]
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(['run', *plan_args, *policy_args]), 3)
                self.assertEqual(cli.main(['status', *plan_args]), 2)
            self.install(api, f, plan)
            with patch.object(api.contained, 'run_contained_stage', lambda *a, **kw: offline_launch(api, *a, **kw)), redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(['run', *plan_args, *policy_args]), 0)
                self.assertEqual(cli.main(['status', *plan_args]), 0)

    def test_accepted_supplement_requires_linked_query_replay_inventories(self):
        api = self.api()
        f, index = self.fixture(period=202403)
        refs, admissions, snapshots = {}, [], []
        profile = f.pkg / 'financial-reports-profiles/202403.json'
        refs['profile'] = api._ref(profile)
        for prefix in ('', 'replay_'):
            source = f.root / ('data/derived/' + prefix + 'supplement')
            target = f.root / ('data/curated/' + prefix + 'supplement')
            reader.admit(index, source)
            refs[prefix + 'admission'] = api._ref(source / 'manifest.json')
            result = dispatch.convert_financial(source, target, source_manifest_sha256=refs[prefix + 'admission']['sha256'])
            refs[prefix + 'parquet'] = api._ref(target / 'manifest.json')
            query = api.verify_query(source, target, source_manifest_sha256=refs[prefix + 'admission']['sha256'],
                                     manifest_sha256=refs[prefix + 'parquet']['sha256'])
            query.update(contract='root-offline-financial-gate-stage-v1', stage='query' if not prefix else 'replay-query',
                baseline_sha256='a' * 64, execution_head='b' * 40, grade_columns=32, grade_all_varchar=True,
                all_original_csvs_origins_and_decimal_rows_validated_by_adapter=True, accessor_snapshots_opened=1,
                binding_nodes=16, http_requests=0, exact_python_decimal_rows_checked=48,
                typed_views_checked=[{'view': b['view'], 'rows': 6, 'encoding': 'decimal_text_v1', 'storage_type': 'VARCHAR'}
                                     for b in result['numeric_bindings']])
            refs[prefix + 'query'] = api._publish(f.root / ('data/runs/' + prefix + 'query.json'), query)
            admissions.append(source)
            snapshots.append(target)
        comparison = {'contract': 'root-offline-financial-gate-stage-v1', 'stage': 'compare',
            'baseline_sha256': 'a' * 64, 'execution_head': 'b' * 40, 'http_requests': 0,
            'all_manifest_payloads_authenticated': True, 'accepted_sources_unchanged': True, 'protected_equal': 1,
            'comparisons': {key: {'byte_equal': sorted(e['path'] for e in json.loads((directory / 'manifest.json').read_bytes())['files']
                                                      if e['path'] != 'metadata/source-manifest.json'),
                'separately_validated_execution_metadata': ['manifest.json'] if key == 'admission' else
                                                          ['manifest.json', 'metadata/source-manifest.json']}
                for key, directory in (('admission', admissions[0]), ('parquet', snapshots[0]))}}
        refs['compare'] = api._publish(f.root / 'data/runs/compare.json', comparison)
        supplemental = {'contract': 'ifdata-financial-accepted-supplement-v1',
            'members': [{'selection': f.selection, 'evidence': refs}], 'limitations': ['Synthetic sources; not BCB acceptance']}
        ref = api._publish(f.root / 'data/runs/supplement.json', supplemental)
        self.assertEqual(api._validate_supplement(ref)['additional_accepted'], 1)
        comparison['comparisons']['admission']['byte_equal'].pop()
        refs['compare'] = api._publish(f.root / 'data/runs/compare-forged.json', comparison)
        forged = api._publish(f.root / 'data/runs/supplement-forged.json', supplemental)
        with self.assertRaises(api.IntegrityError):
            api._validate_supplement(forged)

    def test_worker_refuses_unjournaled_log_and_result_paths_before_writing(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            rogue = f.root / 'data/runs/rogue-log.json'
            def forged(spec_path, spec_hash, *, resources, before_resume):
                spec = api._read({'path': api._name(spec_path), 'sha256': spec_hash})
                before_resume({'pid': 999999999, 'creation_time': 1, 'contained': True})
                spec['log_path'] = api._name(rogue)
                return api._execute_spec(spec)
            with patch.object(api.contained, 'run_contained_stage', forged):
                result = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
            self.assertEqual(result['status'], 'halted')
            self.assertFalse(rogue.exists(), 'Forged stage wrote outside its journal ownership')

    def test_changed_native_body_halts_before_execution_claim_is_created(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            doc = json.loads(plan.read_bytes())
            final = json.loads((f.root / doc['members'][0]['final_handoff']['path']).read_bytes())
            source = next(s for s in final['sources'] if s['role'] == 'numeric')
            manifest = json.loads((f.root / source['manifest_path']).read_bytes())
            body = (f.root / source['manifest_path']).parent / manifest['body_path']
            body.write_bytes(body.read_bytes() + b' ')
            with patch.object(api.contained, 'run_contained_stage', side_effect=AssertionError('dispatched')):
                with self.assertRaises(api.IntegrityError):
                    api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
            self.assertFalse((f.root / doc['destinations']['execution']).exists())

    def test_query_checks_quantities_with_one_connection_and_one_accessor_open(self):
        api = self.api()
        f, index = self.fixture(quantity=True)
        source, target = f.root / 'data/derived/quantity', f.root / 'data/curated/quantity'
        reader.admit(index, source)
        source_pin = sha((source / 'manifest.json').read_bytes())
        result = dispatch.convert_financial(source, target, source_manifest_sha256=source_pin)
        with patch.object(api.parquet, 'snapshot_connection', wraps=api.parquet.snapshot_connection) as connection, \
                patch.object(api.parquet, 'iter_numeric_decimals', wraps=api.parquet.iter_numeric_decimals) as accessor:
            query = api.verify_query(source, target, source_manifest_sha256=source_pin,
                                     manifest_sha256=result['manifest_sha256'])
        self.assertEqual(query['numeric_rows'], 72)
        self.assertEqual(query['bindings'], 12)
        self.assertEqual(query['precision_encodings'], {'decimal_text_v1': 8, 'duckdb_decimal': 4})
        self.assertEqual(connection.call_count, 1)
        self.assertEqual(accessor.call_count, 1)

    def test_query_releases_external_csv_rows_before_each_owned_snapshot(self):
        api = self.api()
        f, index = self.fixture(quantity=True)
        source, target = f.root / 'data/derived/lifetime', f.root / 'data/curated/lifetime'
        reader.admit(index, source)
        source_pin = sha((source / 'manifest.json').read_bytes())
        result = dispatch.convert_financial(source, target, source_manifest_sha256=source_pin)
        original_csv = reader._iter_csv_bytes
        original_connection = api.parquet.snapshot_connection
        original_accessor = api.parquet.iter_numeric_decimals
        alive = weakref.WeakValueDictionary()
        tracking = {'enabled': True}
        boundaries = []

        class TrackedRow(dict):
            pass

        def tracked_csv(*args, **kwargs):
            for row in original_csv(*args, **kwargs):
                if tracking['enabled']:
                    row = TrackedRow(row)
                    alive[id(row)] = row
                yield row

        def connection(*args, **kwargs):
            boundaries.append('connection')
            self.assertLessEqual(len(alive), 1, 'Query retains a complete external grade during snapshot materialization')
            tracking['enabled'] = False
            try:
                return original_connection(*args, **kwargs)
            finally:
                tracking['enabled'] = True

        def accessor(*args, **kwargs):
            boundaries.append('accessor')
            self.assertLessEqual(len(alive), 1, 'Query retains a complete external grade during Decimal accessor materialization')
            tracking['enabled'] = False
            try:
                yield from original_accessor(*args, **kwargs)
            finally:
                tracking['enabled'] = True

        with patch.object(reader, '_iter_csv_bytes', side_effect=tracked_csv), \
                patch.object(api.parquet, 'snapshot_connection', side_effect=connection), \
                patch.object(api.parquet, 'iter_numeric_decimals', side_effect=accessor):
            query = api.verify_query(source, target, source_manifest_sha256=source_pin,
                                     manifest_sha256=result['manifest_sha256'])
        self.assertEqual(query['numeric_rows'], 72)
        self.assertEqual(query['precision_encodings'], {'decimal_text_v1': 8, 'duckdb_decimal': 4})
        self.assertEqual(boundaries, ['connection', 'accessor'])

    def test_active_source_pin_change_halts_with_a_preserved_partial_scoreboard(self):
        api = self.api()
        with batch_fixture() as f:
            plan, pin = self.prepare(api, f)
            self.install(api, f, plan)
            doc = json.loads(plan.read_bytes())
            image = next(p for p in doc['source_state_files'] if p['path'].endswith('/head.json'))
            dispatched = []
            def changed(*args, **kwargs):
                result = offline_launch(api, *args, **kwargs)
                spec = api._read({'path': api._name(args[0]), 'sha256': args[1]})
                dispatched.append((spec['member'], spec['stage']))
                head = f.root / image['path']
                head.write_bytes(head.read_bytes() + b' ')
                return result
            try:
                with patch.object(api.contained, 'run_contained_stage', changed):
                    result = api.run_pipeline(plan, plan_sha256=pin, resources=RESOURCES)
            except api.IntegrityError:
                self.fail('Active integrity failure escaped without a durable halted scoreboard')
            self.assertEqual(result['status'], 'halted')
            self.assertEqual(dispatched, [(202406, 'admit')])
            self.assertEqual(result['scoreboard']['window_accepted'], 0)
            self.assertEqual(result['members'][0]['state'], 'quarantined')
            self.assertTrue(result['members'][0]['milestones']['admitted'])
            self.assertEqual(result['members'][0]['errors'][0]['code'], 'integrity')
            self.assertTrue((f.root / result['manifest']['path']).is_file())

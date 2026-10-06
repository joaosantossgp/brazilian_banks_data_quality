"""Physical synthetic captures prove capabilities and pins, never accepted BCB data."""
import copy
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from tests import test_financial_acquisition_batch as fixtures

canonical, sha = fixtures.canonical, fixtures.sha


class CurrentIdentityTests(unittest.TestCase):
    def setUp(self):
        self.batch = importlib.import_module('bank_quality.financial_acquisition_batch')
        self.api = importlib.import_module('bank_quality.financial_acquisition')
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for module in (self.batch, self.api):
            injected = patch.object(module, '_ROOT', self.root)
            injected.start()
            self.addCleanup(injected.stop)
        self.files = self.batch._CODE_FILES + ('bank_quality/financial_acquisition_compat.py',)
        for name in self.files:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
        head = patch('subprocess.check_output', return_value='b' * 40)
        head.start()
        self.addCleanup(head.stop)
        self.pins = {'contract': 'financial-acquisition-code-pins-v2', 'reviewed_commit': 'b' * 40,
                     'files': {name: sha((self.root / name).read_bytes()) for name in self.files},
                     'runtime': {'path': str(Path(sys.executable).resolve()),
                                 'sha256': sha(Path(sys.executable).read_bytes())},
                     'policy_sha256': '16949510b28c525348590a10d93fcacfe25114815c08fc0e2b5df4e98eb31663'}

    def test_installed_finite_policy_has_exact_digest_and_native_schema(self):
        self.assertTrue(hasattr(self.batch, '_HISTORICAL_POLICY_V1'), 'Installed policy missing')
        policy = self.batch._HISTORICAL_POLICY_V1
        self.assertEqual(sha(canonical(policy)), self.pins['policy_sha256'])
        self.assertEqual(len(policy['members']), 55)
        self.assertEqual(len(policy['windows']), 16)
        self.assertEqual(policy['members'][0]['period'], 201003)
        self.assertEqual(policy['members'][-1]['period'], 202309)
        self.batch._historical_policy(policy)
        for value in (True, 55.0, '55'):
            bad = copy.deepcopy(policy)
            bad['aggregate_caps']['members'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.batch._historical_policy(bad)

    def test_six_physical_pins_gate_before_compat_import(self):
        self.assertTrue(callable(getattr(self.batch, '_code_identity_v2', None)), 'Six pin gate missing')
        self.batch._code_identity_v2(self.pins)
        self.assertEqual(len(self.batch._CODE_FILES), 5)
        for name in self.files:
            path = self.root / name
            before = path.read_bytes()
            path.write_bytes(before + b'changed')
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.batch._code_identity_v2(self.pins)
            path.write_bytes(before)
        for change in ('missing', 'extra', 'head', 'policy', 'runtime'):
            bad = copy.deepcopy(self.pins)
            if change == 'missing':
                bad['files'].pop(self.files[-1])
            elif change == 'extra':
                bad['files']['other.py'] = 'f' * 64
            elif change == 'head':
                bad['reviewed_commit'] = 'c' * 40
            elif change == 'policy':
                bad['policy_sha256'] = 'f' * 64
            else:
                bad['runtime']['sha256'] = 'f' * 64
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.batch._code_identity_v2(bad)
        pins = self.root / 'data/runs/current/code-pins.json'
        pins.parent.mkdir(parents=True)
        bad = copy.deepcopy(self.pins)
        bad['files'].pop(self.files[-1])
        pins.write_bytes(canonical(bad))
        with patch('importlib.import_module', side_effect=AssertionError('compat imported before physical gate')):
            with self.assertRaises(ValueError):
                self.batch.verify_legacy54_sources(current_code_pins_path=pins,
                                                   current_code_pins_sha256=sha(pins.read_bytes()))

    def test_current_manifest_duplicate_keys_floats_and_non_native_data_are_rejected(self):
        pins = self.root / 'data/runs/current/code-pins.json'
        pins.parent.mkdir(parents=True)
        bodies = [canonical(self.pins)[:-1] + b',"contract":"financial-acquisition-code-pins-v2"}',
                  canonical({**self.pins, 'reviewed_commit': 1.0}), b'{"contract":NaN}']
        for body in bodies:
            pins.write_bytes(body)
            with self.subTest(body=body[:30]), self.assertRaises(ValueError):
                self.batch._verified_current_code_pins(pins, sha(body))
        for value in (lambda: None, Path('file'), type('Counter', (int,), {})(1)):
            with self.subTest(value=type(value)), self.assertRaises(ValueError):
                self.api._closed_data({'value': value})
        for escaped in (self.root.parent / 'outside.json', self.root / 'data/runs/../outside.json'):
            with self.subTest(path=escaped), self.assertRaises(ValueError):
                self.batch._verified_current_code_pins(escaped, 'f' * 64)


class InstalledAnchorTests(unittest.TestCase):
    def test_literal_anchor_and_index_match_the_reviewed_five_pin_identity(self):
        module = importlib.import_module('bank_quality.financial_acquisition_compat')
        anchor = module._LEGACY54_ANCHOR
        self.assertEqual(anchor['bundle_sha256'], '557e4fbc22b552c4ec3179d39560c17d6c0ea8ec4102c971f602705a1a25c890')
        self.assertEqual(anchor['bootstrap_sha256'], 'ac04474c43a17920e30597724e922c8a1f36c6b3999d6bc2b462b443dfb04bd3')
        self.assertEqual(anchor['runtime_sha256'], '2204195cec25879507d958a8b6949add67091244b8b4da9cf3672f993548fa49')
        self.assertEqual(anchor['runtime_recorded_path'],
            r'C:\Users\jadaojoao\Documents\Projects\brazilian_banks_data_quality\.venv\Scripts\python.exe')
        self.assertEqual(anchor['runtime_evidence_path'], '.scratch/ifdata-resume-20261006/evidence-only/python.exe')
        self.assertEqual(sha(canonical(anchor['policy'])), '0e06747d8ebf98bbddf1f03ed32cab2cc5942ad9aa805d50282b59a04f3919ec')
        index = {'contract': 'financial-acquisition-executed-code-index-v1', 'executed_commit': anchor['executed_commit'],
                 'files': anchor['files'], 'runtime_sha256': anchor['runtime_sha256'], 'policy_sha256': anchor['policy_sha256']}
        self.assertEqual(sha(canonical(index)), 'e00e0b0a94e1ca8afa09ca0ce210ce8573228b48a6c92ef1cfa72814857ca828')
        self.assertEqual(len(anchor['files']), 5)


class LegacyReadOnlyTests(unittest.TestCase):
    inject = fixtures.BatchCompositionTests.inject
    write = fixtures.BatchCompositionTests.write
    parquet_fixture = fixtures.BatchCompositionTests.parquet_fixture
    source_fixture = fixtures.BatchCompositionTests.source_fixture
    prepare = fixtures.BatchCompositionTests.prepare
    bounded_source = fixtures.BatchCompositionTests.bounded_source
    initialize = fixtures.BatchAuthorityTests.initialize
    terminal = fixtures.BatchAuthorityTests.terminal

    @classmethod
    def setUpClass(cls):
        fixtures.BatchCompositionTests.setUpClass.__func__(cls)

    def setUp(self):
        self.original_current_identity = self.batch._current_code_identity
        fixtures.BatchAuthorityTests.setUp(self)
        self.compat = (importlib.import_module('bank_quality.financial_acquisition_compat')
                       if importlib.util.find_spec('bank_quality.financial_acquisition_compat') else None)
        executed = '5c0257789a3a6f54f8fbe98f95cef4eb4a68cf75'
        archive_root = 'data/runs/financial-acquisition-executed-code/' + executed
        for name in self.batch._CODE_FILES:
            self.write(archive_root + '/' + name, name.encode())
        runtime = self.write('.scratch/ifdata-resume-20261006/evidence-only/python.exe', b'inert historical runtime bytes')
        legacy_runtime = {'path': r'C:\historical-host\original-checkout\.venv\Scripts\python.exe',
                          'sha256': runtime['sha256']}
        self.identity.update(reviewed_commit=executed, runtime=legacy_runtime)
        self.pins.update(reviewed_commit=executed, runtime=legacy_runtime)
        self.refs = self.initialize(self.batch._RUN)
        original_reserve = self.acquisition.reserve_attempt
        retried = False
        def physical_reserve(authority, target, *, session_id):
            nonlocal retried
            if not retried:
                retried = True
                first = original_reserve(authority, target, session_id=session_id)
                authority.commit('identity', attempt_id=first['attempt_id'], identity={
                    'pid': 123, 'creation_time': 456, 'contained': True})
                authority.commit('finish', attempt_id=first['attempt_id'], status='http_503', retryable=True,
                                 source_ref=None, observed_bytes=3, observed_attempt_seconds=1, tree_extinct=True)
                authority.commit('backoff', attempt_id='fixture-backoff', reserved_backoff_seconds=5)
                authority.commit('backoff_finish', attempt_id='fixture-backoff', observed_backoff_seconds=3)
                authority.commit('backoff', attempt_id='fixture-orphan-backoff', reserved_backoff_seconds=5)
                authority.commit('backoff_orphan', attempt_id='fixture-orphan-backoff')
            reservation = original_reserve(authority, target, session_id=session_id)
            authority.commit('identity', attempt_id=reservation['attempt_id'], identity={
                'pid': 123, 'creation_time': 456, 'contained': True})
            return reservation
        with patch.object(self.acquisition, 'reserve_attempt', physical_reserve):
            self.expected_totals = self.batch._run_serial(self.root / self.refs['bundle_path'],
                self.refs['bundle_sha256'], bootstrap_sha256=self.refs['bootstrap_sha256'], phase_callable=self.terminal)
        index = {'contract': 'financial-acquisition-executed-code-index-v1', 'executed_commit': executed,
                 'files': self.pins['files'], 'runtime_sha256': runtime['sha256'],
                 'policy_sha256': self.pins['policy_sha256']}
        index_ref = self.write(archive_root + '/index.json', index)
        self.anchor = {'anchor_id': 'recent54-executed-5c025778', 'executed_commit': executed,
                       'bundle_path': self.refs['bundle_path'], 'bundle_sha256': self.refs['bundle_sha256'],
                       'bootstrap_path': self.batch._RUN + '/bootstrap.json',
                       'bootstrap_sha256': self.refs['bootstrap_sha256'], 'scope': self.batch._SCOPE,
                       'policy': copy.deepcopy(self.batch._POLICIES), 'policy_sha256': self.pins['policy_sha256'],
                       'runtime_recorded_path': legacy_runtime['path'], 'runtime_evidence_path': runtime['path'],
                       'runtime_sha256': runtime['sha256'],
                       'files': copy.deepcopy(self.pins['files']), 'archive_root': archive_root,
                       'executed_code_index_path': index_ref['path'], 'executed_code_index_sha256': index_ref['sha256']}
        if self.compat:
            self.inject(self.compat, '_LEGACY54_ANCHOR', self.anchor)
        self.inject(self.batch, '_current_code_identity', self.original_current_identity)
        for name in self.batch._CODE_FILES + ('bank_quality/financial_acquisition_compat.py',):
            origin = Path(__file__).resolve().parents[1] / name
            self.write(name, origin.read_bytes() if origin.exists() else b'compat absent')
        self.current_pins = {'contract': 'financial-acquisition-code-pins-v2', 'reviewed_commit': 'b' * 40,
            'files': {name: sha((self.root / name).read_bytes())
                      for name in self.batch._CODE_FILES + ('bank_quality/financial_acquisition_compat.py',)},
            'runtime': {'path': str(Path(sys.executable).resolve()), 'sha256': sha(Path(sys.executable).read_bytes())},
            'policy_sha256': '16949510b28c525348590a10d93fcacfe25114815c08fc0e2b5df4e98eb31663'}
        self.current = self.write('data/runs/current/code-pins.json', self.current_pins)
        self.inject(importlib.import_module('subprocess'), 'check_output', lambda *args, **kwargs: 'b' * 40)

    def prove(self):
        self.assertIsNotNone(self.compat, 'Read-only compatibility module missing')
        return self.batch.verify_legacy54_sources(current_code_pins_path=self.root / self.current['path'],
                                                 current_code_pins_sha256=self.current['sha256'])

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}

    def no_capabilities(self):
        stack = ExitStack()
        for module, names in ((self.acquisition, ('_Authority', '_open_authority', '_claim', '_write_exclusive',
                '_replace_head', 'reserve_attempt', '_recover_pending', '_worker_authorization', 'run_acquisition')),
                (self.batch, ('_Batch', '_MemberContext', '_open_batch', '_verify_batch', '_proof', '_totals',
                             '_sources403', '_run_batch', '_recover_batch')),
                (importlib.import_module('bank_quality.archive'), ('fetch', 'fetch_bounded'))):
            for name in names:
                stack.enter_context(patch.object(module, name, side_effect=AssertionError('Capability used: ' + name)))
        original_open = Path.open
        def readonly(path, mode='r', *args, **kwargs):
            self.assertFalse(any(flag in mode for flag in 'wax+'), 'Write mode in legacy proof: ' + mode)
            self.assertNotEqual(str(path), self.anchor['runtime_recorded_path'], 'Historical address opened')
            return original_open(path, mode, *args, **kwargs)
        stack.enter_context(patch.object(Path, 'open', readonly))
        stack.enter_context(patch('subprocess.Popen', side_effect=AssertionError('Process launched')))
        stack.enter_context(patch('tempfile.TemporaryDirectory', side_effect=AssertionError('Temporary directory created')))
        return stack

    def test_completed_physical_fixture_reconstructs_native_handoff_without_capabilities(self):
        before = self.snapshot()
        with self.no_capabilities():
            proof = self.prove()
            handoff = self.batch.reconstruct_legacy54_handoff(current_code_pins_path=self.root / self.current['path'],
                                                             current_code_pins_sha256=self.current['sha256'])
        self.assertEqual(set(proof), {'contract', 'anchor_id', 'bundle_sha256', 'bootstrap_sha256',
            'executed_code_index_sha256', 'current_code_identity_sha256', 'selections', 'member_prefixes',
            'phase_prefix', 'source_refs', 'handoff_sha256'})
        self.assertEqual(set(handoff), {'contract', 'anchor_id', 'handoff', 'handoff_sha256'})
        self.assertEqual(proof['handoff_sha256'], handoff['handoff_sha256'])
        self.assertEqual(sha(canonical(handoff['handoff'])), handoff['handoff_sha256'])
        self.assertEqual(handoff['handoff']['totals'], self.expected_totals['totals'])
        self.assertEqual(handoff['handoff']['totals']['attempts'], 22)
        self.assertEqual(handoff['handoff']['totals']['backoff_seconds'], 8)
        self.assertEqual(len(handoff['handoff']['entries']), 11)
        self.assertEqual(handoff['handoff']['accepted_parquet_periods'], [202312, 202412, 202503])
        self.assertEqual(before, self.snapshot())
        self.acquisition._closed_data(proof)
        self.acquisition._closed_data(handoff)
        for data in (proof, json.loads(canonical(proof)), handoff):
            with self.assertRaises(ValueError):
                self.acquisition.reserve_attempt(data, {'target_key': 'ignored'}, session_id='attempt')
            try:
                self.acquisition._worker_authorization(data)
            except Exception as error:
                self.assertIsInstance(error, ValueError)
            else:
                self.fail('Read-only data accepted as worker authorization')
            with self.assertRaises(ValueError):
                self.acquisition.initialize_authority(data)
            with self.assertRaises(ValueError):
                with self.acquisition._open_authority(data, self.anchor['bootstrap_sha256']):
                    self.fail('Read-only data opened as an authority')
        with patch.object(self.acquisition, '_claim', side_effect=AssertionError('Execution claim created')):
            with self.assertRaises(ValueError):
                with self.batch._open_batch(self.root / self.refs['bundle_path'], self.refs['bundle_sha256'],
                                            self.refs['bootstrap_sha256']):
                    self.fail('Historical executed identity accepted as current execution')
        self.assertEqual(before, self.snapshot())

    def test_migrated_runtime_proof_uses_inert_bytes_without_current_runtime_fallback(self):
        self.assertNotEqual(self.anchor['runtime_recorded_path'], self.current_pins['runtime']['path'])
        self.assertNotEqual(self.anchor['runtime_sha256'], self.current_pins['runtime']['sha256'])
        self.assertFalse((self.root / '.venv/Scripts/python.exe').exists())
        before = self.snapshot()
        with self.no_capabilities():
            try:
                proof = self.prove()
            except (KeyError, OSError, ValueError) as error:
                self.fail('Migrated capture rejected despite authenticated inert evidence: ' + str(error))
        self.assertEqual(proof['bundle_sha256'], self.refs['bundle_sha256'])
        self.assertEqual(before, self.snapshot())
        evidence = self.root / self.anchor['runtime_evidence_path']
        evidence.write_bytes(Path(sys.executable).read_bytes())
        before = self.snapshot()
        with self.no_capabilities(), self.assertRaisesRegex(ValueError, 'anchored file hash'):
            self.prove()
        self.assertEqual(before, self.snapshot())

    def test_migrated_runtime_literal_rejects_even_a_rehashed_bundle_with_current_address(self):
        path = self.root / self.anchor['bundle_path']
        bundle = json.loads(path.read_bytes())
        bundle['code_pins']['runtime']['path'] = self.current_pins['runtime']['path']
        path.write_bytes(canonical(bundle))
        self.anchor['bundle_sha256'] = sha(path.read_bytes())
        before = self.snapshot()
        with self.no_capabilities(), self.assertRaisesRegex(ValueError, 'five executed pins'):
            self.prove()
        self.assertEqual(before, self.snapshot())

    def test_migrated_evidence_reparse_ancestor_and_escaping_paths_are_refused(self):
        from types import SimpleNamespace
        ancestor = (self.root / self.anchor['runtime_evidence_path']).parent
        original_lstat = Path.lstat
        def reparse(path, *args, **kwargs):
            info = original_lstat(path, *args, **kwargs)
            return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400) if path == ancestor else info
        before = self.snapshot()
        with patch.object(Path, 'lstat', reparse), self.no_capabilities(), self.assertRaisesRegex(ValueError, 'reparse'):
            self.prove()
        self.assertEqual(before, self.snapshot())
        for name in ('../python.exe', '/python.exe', 'C:/outside/python.exe', '//server/share/python.exe'):
            self.anchor['runtime_evidence_path'] = name
            with self.subTest(path=name), self.no_capabilities(), self.assertRaisesRegex(ValueError, 'Path escape'):
                self.prove()
        self.assertEqual(before, self.snapshot())

    def test_migrated_proof_keeps_current_runtime_bytes_gate_before_import(self):
        runtime = self.write('.scratch/current-runtime/python.exe', b'current runtime fixture')
        self.current_pins['runtime'] = {'path': str((self.root / runtime['path']).resolve()), 'sha256': runtime['sha256']}
        self.current = self.write(self.current['path'], self.current_pins)
        with patch.object(sys, 'executable', self.current_pins['runtime']['path']):
            with self.no_capabilities():
                self.prove()
            (self.root / runtime['path']).write_bytes(b'changed current runtime bytes')
            before = self.snapshot()
            with self.no_capabilities(), patch('importlib.import_module', side_effect=AssertionError('compat imported')):
                with self.assertRaisesRegex(ValueError, 'Current code/runtime/HEAD'):
                    self.prove()
            self.assertEqual(before, self.snapshot())

    def test_lagging_head_partial_tail_and_pending_are_refused_without_repair(self):
        self.assertIsNotNone(self.compat, 'Read-only compatibility module missing')
        bundle = json.loads((self.root / self.refs['bundle_path']).read_bytes())
        member = bundle['members'][0]
        for mode in ('phase_head', 'member_head', 'partial_tail', 'pending'):
            journal = self.root / (member['authority_path'] if mode in ('member_head', 'pending') else self.batch._RUN) / 'journal.jsonl'
            head = journal.parent / 'head.json'
            saved = journal.read_bytes(), head.read_bytes()
            records = [json.loads(line) for line in saved[0].splitlines()]
            if mode == 'partial_tail':
                journal.write_bytes(saved[0] + b'{"partial":')
            elif mode == 'pending':
                last = next(i for i, record in reversed(list(enumerate(records))) if record['kind'] == 'reserve')
                records = records[:last + 1]
                journal.write_bytes(b''.join(canonical(record) + b'\n' for record in records))
                replay = self.acquisition._replay_member_records(records, job_identity=member['job_sha256'],
                    targets=self.acquisition._execution_job(member['job']), policy=self.acquisition._limits(member['job']))
                head.write_bytes(canonical(replay['head']))
            else:
                head.write_bytes(canonical({'sequence': 0, 'record_sha256': '0' * 64,
                    'state_sha256': sha(canonical(self.acquisition._initial_state() if mode == 'member_head' else self.batch._ledger_state()))}))
            before = self.snapshot()
            with self.subTest(mode=mode), self.no_capabilities(), self.assertRaises(ValueError):
                self.prove()
            self.assertEqual(before, self.snapshot())
            journal.write_bytes(saved[0])
            head.write_bytes(saved[1])

    def test_installed_anchor_cannot_be_replaced_by_rehashed_index_or_changed_sources(self):
        self.assertIsNotNone(self.compat, 'Read-only compatibility module missing')
        paths = (self.anchor['executed_code_index_path'], self.anchor['bundle_path'], self.anchor['bootstrap_path'],
                 self.anchor['archive_root'] + '/' + self.batch._CODE_FILES[0], self.anchor['runtime_evidence_path'])
        for name in paths:
            path = self.root / name
            raw = path.read_bytes()
            path.write_bytes(raw + b'changed')
            before = self.snapshot()
            with self.subTest(path=name), self.no_capabilities(), self.assertRaises(ValueError):
                self.prove()
            self.assertEqual(before, self.snapshot())
            path.write_bytes(raw)
        compat_path = self.root / 'bank_quality/financial_acquisition_compat.py'
        compat_path.write_bytes(compat_path.read_bytes() + b'changed')
        with self.no_capabilities(), self.assertRaises(ValueError):
            self.prove()

    def test_rehashed_receipt_and_phase_chain_still_require_member_prefix_equivalence(self):
        self.assertIsNotNone(self.compat, 'Read-only compatibility module missing')
        journal_path = self.root / self.batch._RUN / 'journal.jsonl'
        records = [json.loads(line) for line in journal_path.read_bytes().splitlines()]
        record = next(item for item in records if item['kind'] == 'phase_finish')
        ref = record['result']['receipt']
        receipt = json.loads((self.root / ref['path']).read_bytes())
        receipt['state']['attempts'] = 0
        receipt['state_sha256'] = sha(canonical(receipt['state']))
        ref['sha256'] = self.write(ref['path'], receipt)['sha256']
        previous = '0' * 64
        for record in records:
            record['previous_record_sha256'] = previous
            record['record_sha256'] = sha(canonical({key: value for key, value in record.items() if key != 'record_sha256'}))
            previous = record['record_sha256']
        journal_path.write_bytes(b''.join(canonical(record) + b'\n' for record in records))
        bundle = json.loads((self.root / self.refs['bundle_path']).read_bytes())
        phase = self.batch._replay_phase_records(records, anchored_bundle={'bundle': bundle,
            'bundle_sha256': self.refs['bundle_sha256'], 'bootstrap_sha256': self.refs['bootstrap_sha256']})
        (journal_path.parent / 'head.json').write_bytes(canonical(phase['head']))
        before = self.snapshot()
        with self.no_capabilities(), self.assertRaisesRegex(ValueError, 'prefix'):
            self.prove()
        self.assertEqual(before, self.snapshot())

    def test_read_set_detects_a_head_changed_after_initial_validation(self):
        self.assertIsNotNone(self.compat, 'Read-only compatibility module missing')
        head = self.root / self.batch._RUN / 'head.json'
        old = head.read_bytes()
        original_source = self.compat._source
        changed = False
        def changing_source(ref, target, reads):
            nonlocal changed
            result = original_source(ref, target, reads)
            if target['period'] != 202403 and not changed:
                changed = True
                head.write_bytes(old + b' ')
            return result
        before = self.snapshot()
        # The only writer is this test injector, outside the compatibility module.
        with patch.object(self.compat, '_source', changing_source), self.assertRaises(ValueError):
            self.prove()
        after = self.snapshot()
        head_name = head.relative_to(self.root).as_posix()
        self.assertEqual({name for name in after if after[name] != before.get(name)}, {head_name})

    def test_reparse_archive_ancestor_and_rehashed_index_inventory_are_refused(self):
        self.assertIsNotNone(self.compat, 'Read-only compatibility module missing')
        from types import SimpleNamespace
        archive = self.root / self.anchor['archive_root']
        original_lstat = Path.lstat
        def reparse(path, *args, **kwargs):
            info = original_lstat(path, *args, **kwargs)
            return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400) if path == archive else info
        before = self.snapshot()
        with patch.object(Path, 'lstat', reparse), self.no_capabilities(), self.assertRaisesRegex(ValueError, 'reparse'):
            self.prove()
        self.assertEqual(before, self.snapshot())
        index_path = self.root / self.anchor['executed_code_index_path']
        index = json.loads(index_path.read_bytes())
        index['files'].pop(self.batch._CODE_FILES[0])
        index_path.write_bytes(canonical(index))
        with self.no_capabilities(), self.assertRaises(ValueError):
            self.prove()

    def test_source_and_sidecar_changes_are_refused_without_get_or_repair(self):
        self.assertIsNotNone(self.compat, 'Read-only compatibility module missing')
        paths = ['data/raw/source202406/cadaster.bin', 'data/raw/source202406/cadaster.response.json',
                 self.entries[0]['manifest_path']]
        for name in paths:
            path = self.root / name
            raw = path.read_bytes()
            path.write_bytes(raw + b'changed')
            before = self.snapshot()
            with self.subTest(path=name), self.no_capabilities(), self.assertRaises(ValueError):
                self.prove()
            self.assertEqual(before, self.snapshot())
            path.write_bytes(raw)


if __name__ == '__main__':
    unittest.main()

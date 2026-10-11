"""Synthetic SQLite stores only; success here never means financial admission."""
import importlib
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor


class AttemptStoreTests(unittest.TestCase):
    def setUp(self):
        self.Store = importlib.import_module('bank_quality.financial_acquisition_store').AttemptStore
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'attempts.sqlite'
        self.limits = {'attempts': 3, 'body_bytes': 100, 'attempt_ms': 1000}
        self.zero = {'attempts': 0, 'body_bytes': 0, 'attempt_ms': 0}

    def create(self, **kwargs):
        store = self.Store.create(self.path, scope='synthetic/run',
                                  limits=kwargs.get('limits', self.limits),
                                  carried_usage=kwargs.get('carried_usage', self.zero))
        self.addCleanup(store.close)
        return store

    def test_reservation_survives_reopen_with_same_identity_and_full_cost(self):
        store = self.create()
        attempt = store.reserve('C', body_budget_bytes=60, deadline_ms=700)
        store.close()
        with self.Store.open(self.path, scope='synthetic/run') as reopened:
            state = reopened.snapshot()
            self.assertEqual(state['usage'], {'attempts': 1, 'body_bytes': 60, 'attempt_ms': 700})
            self.assertEqual(state['attempts'][0]['attempt_id'], attempt)
            self.assertEqual(state['attempts'][0]['outcome'], 'pending')
            self.assertIsNone(state['attempts'][0]['result'])
            with self.assertRaises(ValueError):
                reopened.reserve('D', body_budget_bytes=41, deadline_ms=1)
            self.assertEqual(len(reopened.snapshot()['attempts']), 1)

    def test_bind_worker_is_durable_single_use_and_preserves_full_reservation(self):
        store = self.create()
        attempt = store.reserve('C', body_budget_bytes=60, deadline_ms=700)
        identity = {'pid': 12, 'creation_time': 34, 'contained': True}
        store.bind_worker(attempt, spec_sha256='a' * 64, launcher_identity=identity)
        with self.Store.open(self.path, scope='synthetic/run') as reopened:
            state = reopened.snapshot()
            row = state['attempts'][0]
            self.assertEqual(row['spec_sha256'], 'a' * 64)
            self.assertEqual(row['launcher_identity'], identity)
            self.assertEqual(row['outcome'], 'pending')
            self.assertEqual(state['usage'], {'attempts': 1, 'body_bytes': 60, 'attempt_ms': 700})
            with self.assertRaises(ValueError):
                reopened.bind_worker(attempt, spec_sha256='a' * 64, launcher_identity=identity)
            with self.assertRaises(ValueError):
                reopened.reserve('C', body_budget_bytes=1, deadline_ms=1)

    def test_invalid_binding_never_writes_either_field(self):
        store = self.create()
        attempt = store.reserve('C', body_budget_bytes=10, deadline_ms=100)
        pending = store.snapshot()
        identity = {'pid': 12, 'creation_time': 34, 'contained': True}
        invalid = [('absent', 'a' * 64, identity), (attempt, 'A' * 64, identity),
                   (attempt, 'a' * 63, identity)]
        invalid += [(attempt, 'a' * 64, changed) for changed in (
            dict(identity, pid=True), dict(identity, creation_time=0),
            dict(identity, contained=1), dict(identity, extra=0), None)]
        for target, pin, launcher in invalid:
            with self.subTest(target=target, pin=pin, launcher=launcher), self.assertRaises(ValueError):
                store.bind_worker(target, spec_sha256=pin, launcher_identity=launcher)
            self.assertEqual(store.snapshot(), pending)
        store.finish(attempt, observed_bytes=0, elapsed_ms=0, outcome='failure', result=None)
        finished = store.snapshot()
        with self.assertRaises(ValueError):
            store.bind_worker(attempt, spec_sha256='a' * 64, launcher_identity=identity)
        self.assertEqual(store.snapshot(), finished)

    def test_binding_crash_before_commit_rolls_back_both_fields(self):
        store = self.create()
        attempt = store.reserve('C', body_budget_bytes=10, deadline_ms=100)
        script = '''import os, sys
from bank_quality.financial_acquisition_store import AttemptStore
store = AttemptStore.open(sys.argv[1], scope='synthetic/run')
store._connection.set_trace_callback(lambda sql: os._exit(71) if sql == 'COMMIT' else None)
store.bind_worker(sys.argv[2], spec_sha256='a'*64,
                  launcher_identity={'pid': 12, 'creation_time': 34, 'contained': True})
'''
        result = subprocess.run([sys.executable, '-c', script, str(self.path), attempt], capture_output=True)
        self.assertEqual(result.returncode, 71, result.stderr.decode())
        with self.Store.open(self.path, scope='synthetic/run') as reopened:
            row = reopened.snapshot()['attempts'][0]
            self.assertIsNone(row['spec_sha256'])
            self.assertIsNone(row['launcher_identity'])
            self.assertEqual(row['outcome'], 'pending')

    def test_explicit_carry_consumes_all_three_limits_without_new_rows(self):
        for field in ('attempts', 'body_bytes', 'attempt_ms'):
            with self.subTest(field=field):
                self.path = Path(self.temp.name) / (field + '.sqlite')
                carry = dict(self.zero, **{field: self.limits[field]})
                store = self.create(carried_usage=carry)
                with self.assertRaises(ValueError):
                    store.reserve('C', body_budget_bytes=1, deadline_ms=1)
                self.assertEqual(store.snapshot()['usage'], carry)
                self.assertEqual(store.snapshot()['attempts'], [])

    def test_pending_target_and_success_are_not_repeated_but_failure_can_retry(self):
        store = self.create()
        first = store.reserve('C', body_budget_bytes=30, deadline_ms=300)
        with self.assertRaises(ValueError):
            store.reserve('C', body_budget_bytes=1, deadline_ms=1)
        store.finish(first, observed_bytes=10, elapsed_ms=20, outcome='failure', result={'error': 'synthetic'})
        second = store.reserve('C', body_budget_bytes=30, deadline_ms=300)
        self.assertNotEqual(first, second)
        store.finish(second, observed_bytes=15, elapsed_ms=30, outcome='success', result={'artifact': 'synthetic.bin'})
        with self.assertRaises(ValueError):
            store.finish(second, observed_bytes=15, elapsed_ms=30, outcome='success', result={'artifact': 'synthetic.bin'})
        with self.assertRaises(ValueError):
            store.reserve('C', body_budget_bytes=1, deadline_ms=1)
        self.assertEqual(store.snapshot()['usage'], {'attempts': 2, 'body_bytes': 25, 'attempt_ms': 50})
        self.assertEqual(store.snapshot()['attempts'][1]['result'], {'artifact': 'synthetic.bin'})

    def test_time_overshoot_remains_real_and_blocks_later_reservations(self):
        store = self.create()
        attempt = store.reserve('C', body_budget_bytes=50, deadline_ms=100)
        store.finish(attempt, observed_bytes=1, elapsed_ms=1001, outcome='failure', result=None)
        self.assertEqual(store.snapshot()['usage'], {'attempts': 1, 'body_bytes': 1, 'attempt_ms': 1001})
        with self.assertRaises(ValueError):
            store.reserve('D', body_budget_bytes=1, deadline_ms=1)
        self.assertEqual(len(store.snapshot()['attempts']), 1)

    def test_invalid_configuration_does_not_create_a_file(self):
        invalid = [dict(self.zero, attempts=True), dict(self.zero, body_bytes=-1),
                   {'attempts': 0, 'body_bytes': 0}, dict(self.zero, extra=0)]
        for carry in invalid:
            with self.subTest(carry=carry), self.assertRaises(ValueError):
                self.create(carried_usage=carry)
            self.assertFalse(self.path.exists())
        with self.assertRaises(TypeError):
            self.Store.create(self.path, scope='synthetic/run', limits=self.limits)
        for limits in (dict(self.limits, attempts=0), dict(self.limits, attempt_ms=1.5)):
            with self.subTest(limits=limits), self.assertRaises(ValueError):
                self.create(limits=limits)
            self.assertFalse(self.path.exists())
        with self.assertRaises(ValueError):
            self.Store.create(self.path, scope='', limits=self.limits, carried_usage=self.zero)
        self.assertFalse(self.path.exists())

    def test_invalid_reservation_and_finish_leave_no_partial_write(self):
        store = self.create()
        for target, body, deadline in [('', 1, 1), ('C', True, 1), ('C', -1, 1),
                                        ('C', 1, 0), ('C', 1, 1.1)]:
            with self.subTest(target=target, body=body, deadline=deadline), self.assertRaises(ValueError):
                store.reserve(target, body_budget_bytes=body, deadline_ms=deadline)
            self.assertEqual(store.snapshot()['attempts'], [])
        attempt = store.reserve('C', body_budget_bytes=10, deadline_ms=100)
        pending = store.snapshot()
        invalid = [{'observed_bytes': 11}, {'observed_bytes': True}, {'elapsed_ms': -1},
                   {'elapsed_ms': True}, {'outcome': 'unknown'},
                   {'result': {'nested': [float('nan')]}}, {'result': object()},
                   {'attempt_id': 'absent'}]
        for mutation in invalid:
            args = dict(attempt_id=attempt, observed_bytes=1, elapsed_ms=1,
                        outcome='success', result={'synthetic': True})
            args.update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                store.finish(**args)
            self.assertEqual(store.snapshot(), pending)

    def test_open_is_existing_only_and_scope_and_create_are_exclusive(self):
        with self.assertRaises(FileNotFoundError):
            self.Store.open(self.path, scope='synthetic/run')
        self.assertFalse(self.path.exists())
        store = self.create()
        before = store.snapshot()
        with self.assertRaises(FileExistsError):
            self.create()
        with self.assertRaises(ValueError):
            self.Store.open(self.path, scope='different')
        self.assertEqual(store.snapshot(), before)
        empty = self.path.with_name('empty.sqlite')
        empty.touch()
        with self.assertRaises(ValueError):
            self.Store.open(empty, scope='synthetic/run')
        with closing(sqlite3.connect(empty)) as conn:
            self.assertEqual(conn.execute('SELECT name FROM sqlite_master').fetchall(), [])

    def test_external_orphan_does_not_resolve_pending_attempt(self):
        store = self.create()
        attempt = store.reserve('C', body_budget_bytes=10, deadline_ms=100)
        self.path.with_name('orphan.bin').write_bytes(b'synthetic')
        store.close()
        with self.Store.open(self.path, scope='synthetic/run') as reopened:
            state = reopened.snapshot()
            self.assertEqual(state['usage'], {'attempts': 1, 'body_bytes': 10, 'attempt_ms': 100})
            self.assertEqual(state['attempts'][0]['attempt_id'], attempt)
            self.assertEqual(state['attempts'][0]['outcome'], 'pending')

    def test_symlink_file_and_ancestor_are_refused(self):
        store = self.create()
        store.close()
        alias = self.path.with_name('alias.sqlite')
        try:
            alias.symlink_to(self.path)
        except OSError as exc:
            self.skipTest('Host cannot create synthetic symlink: ' + str(exc))
        with self.assertRaises(ValueError):
            self.Store.open(alias, scope='synthetic/run')
        directory_alias = self.path.parent / 'linked'
        directory_alias.symlink_to(self.path.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.Store.open(directory_alias / self.path.name, scope='synthetic/run')
        with self.assertRaises(ValueError):
            self.Store.create(directory_alias / 'new.sqlite', scope='synthetic/run',
                              limits=self.limits, carried_usage=self.zero)

    def test_hardlink_alias_is_refused(self):
        store = self.create()
        store.close()
        alias = self.path.with_name('alias.sqlite')
        os.link(self.path, alias)
        with self.assertRaises(ValueError):
            self.Store.open(alias, scope='synthetic/run')

    def child(self, code):
        return subprocess.run([sys.executable, '-B', '-c', code, str(self.path)],
                              capture_output=True, text=True, timeout=15)

    def test_abrupt_exit_before_reservation_commit_rolls_back(self):
        store = self.create()
        first = store.reserve('existing', body_budget_bytes=2, deadline_ms=3)
        before = store.snapshot()
        store.close()
        child = self.child('''
import os, sys
from bank_quality.financial_acquisition_store import AttemptStore
store = AttemptStore.open(sys.argv[1], scope='synthetic/run')
def before_commit(sql):
    if sql == 'COMMIT':
        os._exit(23)
store._connection.set_trace_callback(before_commit)
store.reserve('interrupted', body_budget_bytes=10, deadline_ms=100)
''')
        self.assertEqual(child.returncode, 23, child.stderr)
        with self.Store.open(self.path, scope='synthetic/run') as reopened:
            self.assertEqual(reopened.snapshot(), before)
            self.assertEqual(reopened.snapshot()['attempts'][0]['attempt_id'], first)

    def test_abrupt_exit_after_reservation_preserves_pending_and_identity(self):
        self.create().close()
        child = self.child('''
import os, sys
from bank_quality.financial_acquisition_store import AttemptStore
store = AttemptStore.open(sys.argv[1], scope='synthetic/run')
attempt = store.reserve('C', body_budget_bytes=10, deadline_ms=100)
print(attempt, flush=True)
os._exit(24)
''')
        self.assertEqual(child.returncode, 24, child.stderr)
        with self.Store.open(self.path, scope='synthetic/run') as reopened:
            state = reopened.snapshot()
            self.assertEqual(state['attempts'][0]['attempt_id'], child.stdout.strip())
            self.assertEqual(state['attempts'][0]['outcome'], 'pending')
            self.assertEqual(state['usage'], {'attempts': 1, 'body_bytes': 10, 'attempt_ms': 100})

    def test_two_connections_competing_for_last_budget_only_reserve_once(self):
        self.create(limits={'attempts': 1, 'body_bytes': 10, 'attempt_ms': 100}).close()
        barrier = threading.Barrier(2)

        def writer(target):
            with self.Store.open(self.path, scope='synthetic/run') as store:
                barrier.wait(timeout=5)
                try:
                    return ('reserved', store.reserve(target, body_budget_bytes=10, deadline_ms=100))
                except ValueError:
                    return ('refused', None)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(writer, ('C', 'D')))
        self.assertEqual(sorted(result[0] for result in results), ['refused', 'reserved'])
        with self.Store.open(self.path, scope='synthetic/run') as reopened:
            state = reopened.snapshot()
            self.assertEqual(len(state['attempts']), 1)
            self.assertEqual(state['usage'], {'attempts': 1, 'body_bytes': 10, 'attempt_ms': 100})

    def test_connection_uses_full_synchronous_for_each_open(self):
        store = self.create()
        self.assertEqual(store._connection.execute('PRAGMA synchronous').fetchone()[0], 2)
        store.close()
        with self.Store.open(self.path, scope='synthetic/run') as reopened:
            self.assertEqual(reopened._connection.execute('PRAGMA synchronous').fetchone()[0], 2)

    def test_finite_serializable_result_is_stored_without_extra_key_or_unicode_rules(self):
        store = self.create()
        attempt = store.reserve('C', body_budget_bytes=1, deadline_ms=1)
        try:
            store.finish(attempt, observed_bytes=0, elapsed_ms=0, outcome='success',
                         result={'synthetic': '\ud800', 2: ['ok']})
        except (ValueError, UnicodeError) as exc:
            self.fail('Finite JSON-serializable result was refused: ' + str(exc))
        self.assertEqual(store.snapshot()['attempts'][0]['result'],
                         {'synthetic': '\ud800', '2': ['ok']})

    @unittest.skipUnless(os.name == 'nt', 'Windows reparse-point check')
    def test_windows_junction_ancestor_is_refused_without_elevation(self):
        store = self.create()
        store.close()
        alias = self.path.parent / 'junction'
        created = subprocess.run(['cmd', '/c', 'mklink', '/J', str(alias), str(self.path.parent)],
                                 capture_output=True, text=True, timeout=5)
        self.assertEqual(created.returncode, 0, created.stderr)
        with self.assertRaises(ValueError):
            self.Store.open(alias / self.path.name, scope='synthetic/run')
        with self.assertRaises(ValueError):
            self.Store.create(alias / 'new.sqlite', scope='synthetic/run', limits=self.limits,
                              carried_usage=self.zero)


if __name__ == '__main__':
    unittest.main()

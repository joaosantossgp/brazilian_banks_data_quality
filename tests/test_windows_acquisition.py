"""Windows containment integration tests use only a known local fixture worker."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import threading
import time
import unittest
import uuid
from unittest.mock import patch, Mock


class WindowsAcquisitionTests(unittest.TestCase):
    def test_resource_tree_excludes_stale_parent_pid_and_its_branch(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        coordinator = {'pid': 10, 'creation_time': 100}
        parents = {10: 1, 20: 10, 30: 20, 40: 10, 50: 40}
        identities = {10: coordinator,
                      20: {'pid': 20, 'creation_time': 110},
                      30: {'pid': 30, 'creation_time': 120},
                      40: {'pid': 40, 'creation_time': 5},
                      50: {'pid': 50, 'creation_time': 130}}
        self.assertEqual(api._owned_process_ids(coordinator, parents, identities, observed_before=1000), {10, 20, 30})

    def test_resource_tree_rejects_changed_coordinator_identity(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        with self.assertRaisesRegex(RuntimeError, 'Coordinator'):
            api._owned_process_ids({'pid': 10, 'creation_time': 100}, {10: 1},
                                   {10: {'pid': 10, 'creation_time': 101}}, observed_before=1000)

    def test_resource_tree_rejects_pid_recycled_after_snapshot(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        coordinator = {'pid': 10, 'creation_time': 100}
        with self.assertRaisesRegex(RuntimeError, 'snapshot'):
            api._owned_process_ids(coordinator, {10: 1, 20: 10},
                                   {10: coordinator, 20: {'pid': 20, 'creation_time': 110}},
                                   observed_before=105)

    def test_resource_sample_never_measures_stale_pid_branch(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        coordinator = {'pid': 10, 'creation_time': 100}
        parents = {10: 1, 20: 10, 30: 20, 40: 10, 50: 40}
        identities = {pid: {'pid': pid, 'creation_time': born} for pid, born in
                      [(10, 100), (20, 110), (30, 120), (40, 5), (50, 130)]}
        entries = iter(parents.items())
        kernel, psapi = Mock(), Mock()
        def enumerate_processes(snapshot, pointer):
            try:
                pid, parent = next(entries)
            except StopIteration:
                return False
            pointer._obj.th32ProcessID, pointer._obj.th32ParentProcessID = pid, parent
            return True
        kernel.CreateToolhelp32Snapshot.return_value = 77
        def snapshot_time(pointer):
            pointer._obj.dwLowDateTime = 1000
            pointer._obj.dwHighDateTime = 0
        kernel.GetSystemTimeAsFileTime.side_effect = snapshot_time
        kernel.Process32FirstW.side_effect = enumerate_processes
        kernel.Process32NextW.side_effect = enumerate_processes
        kernel.OpenProcess.side_effect = lambda access, inherit, pid: pid
        def process_memory(handle, pointer, size):
            pointer._obj.working_set, pointer._obj.private_bytes = handle * 2, handle * 3
            return True
        psapi.GetProcessMemoryInfo.side_effect = process_memory
        with patch.object(api, '_kernel', return_value=kernel), \
                patch.object(api, '_identity', side_effect=lambda k, h, pid: identities[pid]), \
                patch.object(api.C, 'WinDLL', return_value=psapi, create=True), \
                patch.object(api.C, 'get_last_error', return_value=18, create=True):
            result = api._resource_sample(Path('.'), coordinator)
        self.assertEqual([call.args[0] for call in psapi.GetProcessMemoryInfo.call_args_list], [10, 20, 30])
        self.assertEqual(result['tree_working_set_bytes'], 120)
        self.assertEqual(result['tree_private_bytes'], 180)
        self.assertEqual({call.args[0] for call in kernel.CloseHandle.call_args_list}, {77, 10, 20, 30, 40, 50})

        for failure in ('identity', 'memory', 'recycled'):
            with self.subTest(failure=failure):
                entries = iter(parents.items())
                kernel.CloseHandle.reset_mock()
                psapi.GetProcessMemoryInfo.reset_mock()
                def identify(k, handle, pid):
                    if failure == 'identity' and pid == 30:
                        raise OSError('identity fixture')
                    if failure == 'recycled' and pid == 20:
                        return {'pid': pid, 'creation_time': 1001}
                    return identities[pid]
                psapi.GetProcessMemoryInfo.side_effect = (
                    OSError('memory fixture') if failure == 'memory' else process_memory)
                expected_error = RuntimeError if failure == 'recycled' else OSError
                with patch.object(api, '_kernel', return_value=kernel), \
                        patch.object(api, '_identity', side_effect=identify), \
                        patch.object(api.C, 'WinDLL', return_value=psapi, create=True), \
                        patch.object(api.C, 'get_last_error', return_value=18, create=True), \
                        self.assertRaises(expected_error):
                    api._resource_sample(Path('.'), coordinator)
                expected_handles = [77, 10, 20, 30] if failure == 'identity' else [77, 10, 20, 30, 40, 50]
                self.assertEqual([call.args[0] for call in kernel.CloseHandle.call_args_list], expected_handles)
                self.assertEqual([call.args[0] for call in psapi.GetProcessMemoryInfo.call_args_list],
                                 [10] if failure == 'memory' else [])

    def test_resource_profile_is_closed_serial_and_machine_specific(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        profile = {'contract': 'financial-acquisition-resource-profile-v1', 'machine_id': 'fixture',
            'metadata_workers': 1, 'values_workers': 1, 'active_windows': 1,
            'min_free_physical_bytes': 1, 'min_free_commit_bytes': 1,
            'min_free_disk_bytes': 1, 'sampling_interval_ms': 250}
        with patch.object(api, '_machine_id', return_value='fixture'):
            self.assertEqual(api._resource_profile(profile), profile)
            for key, value in [('machine_id', 'other'), ('metadata_workers', 2),
                               ('values_workers', True), ('sampling_interval_ms', 0)]:
                with self.subTest(key=key), self.assertRaises(ValueError):
                    api._resource_profile(dict(profile, **{key: value}))


    def test_monitor_keeps_bounded_samples_and_sets_cancel_on_measurement_failure(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        profile = {'contract': 'financial-acquisition-resource-profile-v1', 'machine_id': 'fixture',
            'metadata_workers': 1, 'values_workers': 1, 'active_windows': 1,
            'min_free_physical_bytes': 1, 'min_free_commit_bytes': 1,
            'min_free_disk_bytes': 1, 'sampling_interval_ms': 250}
        sample = {'free_physical_bytes': 100, 'free_commit_bytes': 100, 'free_disk_bytes': 100,
                  'processes': [], 'tree_working_set_bytes': 2, 'tree_private_bytes': 3, 'elapsed_clock': 1.0}
        cancelled = threading.Event()
        with patch.object(api, '_machine_id', return_value='fixture'), \
                patch.object(api, '_current_identity', return_value={'pid': 7, 'creation_time': 9}), \
                patch.object(api, '_resource_sample', return_value=sample):
            monitor = api._ResourceMonitor(profile, Path('.'), cancelled)
            for _ in range(130):
                monitor.sample()
            self.assertLessEqual(len(monitor.samples), 128)
            self.assertEqual(monitor.sample_count, 130)
            self.assertEqual(monitor.peaks['tree_private_bytes'], 3)
            with patch.object(api, '_resource_sample', side_effect=OSError('measurement fixture')):
                monitor.thread.start()
                self.assertTrue(cancelled.wait(2))
                monitor.stop.set()
                monitor.thread.join(2)
                self.assertIn('measurement fixture', monitor.error)

    def test_monitor_accounts_reserved_body_before_launch_without_refund(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        profile = {'contract': 'financial-acquisition-resource-profile-v1', 'machine_id': 'fixture',
            'metadata_workers': 1, 'values_workers': 1, 'active_windows': 1,
            'min_free_physical_bytes': 1, 'min_free_commit_bytes': 1,
            'min_free_disk_bytes': 1, 'sampling_interval_ms': 250}
        sample = {'free_physical_bytes': 100, 'free_commit_bytes': 100, 'free_disk_bytes': 10,
                  'processes': [], 'tree_working_set_bytes': 2, 'tree_private_bytes': 3, 'elapsed_clock': 1.0}
        with patch.object(api, '_machine_id', return_value='fixture'), \
                patch.object(api, '_current_identity', return_value={'pid': 7, 'creation_time': 9}), \
                patch.object(api, '_resource_sample', return_value=sample):
            monitor = api._ResourceMonitor(profile, Path('.'), threading.Event())
            monitor.reserve({'attempt_id': 'a' * 32, 'reserved_bytes': 10, 'reserved_attempt_seconds': 120})
            with self.assertRaisesRegex(RuntimeError, 'disk'):
                monitor.sample()
            self.assertEqual(monitor.reservations['a' * 32]['reserved_bytes'], 10)
            monitor.finish('a' * 32)
            monitor.sample()
            self.assertEqual(monitor.samples[-1]['inflight_reserved_bytes'], 0)

    def test_worker_marker_is_unobservable_during_partial_write(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            marker = root / 'worker.json'
            spec = root / 'spec.json'
            spec.write_text(json.dumps({'marker': str(marker)}))
            partial = threading.Event()
            release = threading.Event()
            errors = []
            original_open = Path.open

            class SlowWriter:
                def __init__(self, stream):
                    self.stream = stream

                def __enter__(self):
                    self.stream.__enter__()
                    return self

                def __exit__(self, *args):
                    return self.stream.__exit__(*args)

                def write(self, payload):
                    split = len(payload) // 2
                    self.stream.write(payload[:split])
                    self.stream.flush()
                    partial.set()
                    if not release.wait(5):
                        raise RuntimeError('Partial-write fixture was not released')
                    self.stream.write(payload[split:])
                    return len(payload)

                def flush(self):
                    self.stream.flush()

            def slow_open(path, mode='r', *args, **kwargs):
                stream = original_open(path, mode, *args, **kwargs)
                if path.parent == root and any(flag in mode for flag in ('w', 'x')):
                    return SlowWriter(stream)
                return stream

            def publish():
                try:
                    _fixture_worker()
                except Exception as error:
                    errors.append(error)

            with patch.object(Path, 'open', slow_open), \
                    patch.object(sys, 'argv', [__file__, str(spec)]), \
                    patch.object(api, '_current_identity', return_value={'pid': 123, 'creation_time': 456}):
                writer = threading.Thread(target=publish)
                writer.start()
                try:
                    self.assertTrue(partial.wait(5), 'Writer did not reach its partial-write boundary')
                    self.assertFalse(marker.exists(), 'Partial JSON was published as a complete marker')
                finally:
                    release.set()
                    writer.join(timeout=5)
            self.assertFalse(writer.is_alive())
            self.assertEqual(errors, [])
            self.assertEqual(self.wait_file(marker), {'worker': {'pid': 123, 'creation_time': 456}})

    def spec(self, root, **changes):
        spec = root / 'spec.json'
        spec.write_text(json.dumps({'contract': 'financial-acquisition-worker-v1', 'marker': str(root / 'worker.json'),
                                   'application_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                                   'worker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), **changes}))
        return spec, hashlib.sha256(spec.read_bytes()).hexdigest()

    def wait_file(self, path, timeout=8):
        stop = time.monotonic() + timeout
        while not path.exists():
            if time.monotonic() >= stop:
                self.fail('Fixture marker timeout: ' + str(path))
            time.sleep(.01)
        return json.loads(path.read_bytes())

    def assert_extinct(self, identity):
        api = importlib.import_module('bank_quality.windows_acquisition')
        stop = time.monotonic() + 5
        while not api.identity_extinct(identity):
            if time.monotonic() >= stop:
                self.fail('Owned fixture survived: ' + str(identity))
            time.sleep(.01)

    def test_platform_unsupported_before_launch(self):
        self.assertIsNotNone(importlib.util.find_spec('bank_quality.windows_acquisition'), 'Windows helper missing')
        api = importlib.import_module('bank_quality.windows_acquisition')
        with patch.object(api.os, 'name', 'posix'):
            with self.assertRaisesRegex(RuntimeError, 'Windows'):
                api.run_contained_attempt(Path('missing'), '0' * 64, deadline_seconds=1,
                                          before_resume=lambda identity: self.fail('callback'))

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_identity_commit_callback_before_resume(self):
        self.assertIsNotNone(importlib.util.find_spec('bank_quality.windows_acquisition'), 'Windows helper missing')
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            marker = root / 'worker.json'
            spec = root / 'spec.json'
            spec.write_text(json.dumps({'contract': 'financial-acquisition-worker-v1', 'marker': str(marker),
                                        'application_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                                        'worker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}))
            identities = []
            def before(identity):
                self.assertFalse(marker.exists())
                self.assertGreater(identity['pid'], 0)
                self.assertGreater(identity['creation_time'], 0)
                self.assertTrue(identity['contained'])
                identities.append(identity)
            with patch.object(api, '_WORKER_MODULE', 'tests.test_windows_acquisition'):
                result = api.run_contained_attempt(spec, hashlib.sha256(spec.read_bytes()).hexdigest(),
                                                   deadline_seconds=5, before_resume=before)
            self.assertTrue(marker.exists())
            self.assertEqual(len(identities), 1)
            self.assertTrue(result['tree_extinct'])
            self.assertEqual(result['exit_code'], 0)

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_identity_commit_failure_kills_suspended_worker_without_get(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec, pin = self.spec(root)
            captured = []
            def failure(identity):
                captured.append(identity)
                raise OSError('durable PID commit failed')
            with patch.object(api, '_WORKER_MODULE', 'tests.test_windows_acquisition'):
                with self.assertRaisesRegex(OSError, 'durable PID'):
                    api.run_contained_attempt(spec, pin, deadline_seconds=3, before_resume=failure)
            self.assertFalse((root / 'worker.json').exists())
            self.assert_extinct(captured[0])

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_cancellation_extinguishes_two_active_trees(self):
        from concurrent.futures import ThreadPoolExecutor
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            roots = [Path(temp) / str(i) for i in range(2)]
            for root in roots:
                root.mkdir()
            specs = [self.spec(root, spawn_child=True, sleep_seconds=20) for root in roots]
            cancel = threading.Event()
            with patch.object(api, '_WORKER_MODULE', 'tests.test_windows_acquisition'), ThreadPoolExecutor(2) as pool:
                futures = [pool.submit(api.run_contained_attempt, spec, pin, deadline_seconds=5,
                    before_resume=lambda identity: None, cancel_event=cancel) for spec, pin in specs]
                try:
                    markers = [self.wait_file(root / 'worker.json') for root in roots]
                finally:
                    cancel.set()
                for future in futures:
                    self.assertTrue(future.result()['tree_extinct'])
            for marker in markers:
                self.assert_extinct(marker['worker'])
                self.assert_extinct(marker['child'])

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_deadline_kills_owned_tree(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec, pin = self.spec(root, spawn_child=True, sleep_seconds=20)
            with patch.object(api, '_WORKER_MODULE', 'tests.test_windows_acquisition'):
                result = api.run_contained_attempt(spec, pin, deadline_seconds=1.5, before_resume=lambda identity: None)
            marker = self.wait_file(root / 'worker.json')
            self.assertTrue(result['deadline_reached'])
            self.assertTrue(result['tree_extinct'])
            self.assertLessEqual(result['elapsed_seconds'], 1.5)
            self.assertEqual(result['deadline_overshoot_seconds'], 0)
            self.assert_extinct(marker['worker'])
            self.assert_extinct(marker['child'])
            self.assertFalse(result['job_handle_inherited'])

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_parent_crash_after_creation_before_resume(self):
        self.crash_case('before')

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_parent_crash_after_resume_kills_launcher_and_grandchild(self):
        self.crash_case('after')

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_parent_crash_extinguishes_two_active_worker_trees(self):
        with tempfile.TemporaryDirectory() as temp:
            roots = [Path(temp) / str(i) for i in range(2)]
            for root in roots:
                root.mkdir()
                self.spec(root, spawn_child=True, sleep_seconds=20)
            supervisor = subprocess.Popen([sys.executable, '-B', '-m', 'tests.test_windows_acquisition',
                'supervisor2', temp], creationflags=subprocess.CREATE_NO_WINDOW)
            self.addCleanup(lambda: supervisor.kill() if supervisor.poll() is None else None)
            markers = [self.wait_file(root / 'worker.json') for root in roots]
            self.assertEqual(supervisor.wait(timeout=10), 73)
            for root, marker in zip(roots, markers):
                self.assert_extinct(self.wait_file(root / 'identity.json'))
                self.assert_extinct(marker['worker'])
                self.assert_extinct(marker['child'])

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_callback_failure_cancels_other_active_tree(self):
        from concurrent.futures import ThreadPoolExecutor
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            roots = [Path(temp) / str(i) for i in range(2)]
            for root in roots:
                root.mkdir()
            specs = [self.spec(root, spawn_child=True, sleep_seconds=20) for root in roots]
            cancel, identities = threading.Event(), []
            def fail(identity):
                identities.append(identity)
                raise OSError('fixture persistence failure')
            with patch.object(api, '_WORKER_MODULE', 'tests.test_windows_acquisition'), ThreadPoolExecutor(1) as pool:
                future = pool.submit(api.run_contained_attempt, *specs[0], deadline_seconds=5,
                    before_resume=lambda identity: None, cancel_event=cancel)
                marker = self.wait_file(roots[0] / 'worker.json')
                try:
                    with self.assertRaisesRegex(OSError, 'persistence'):
                        api.run_contained_attempt(*specs[1], deadline_seconds=5, before_resume=fail, cancel_event=cancel)
                finally:
                    cancel.set()
                self.assertTrue(future.result()['tree_extinct'])
            self.assertFalse((roots[1] / 'worker.json').exists())
            self.assert_extinct(identities[0])
            self.assert_extinct(marker['worker'])
            self.assert_extinct(marker['child'])

    def crash_case(self, phase):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec, pin = self.spec(root, spawn_child=True, sleep_seconds=20)
            supervisor = subprocess.Popen([sys.executable, '-B', '-m', 'tests.test_windows_acquisition',
                                           'supervisor', str(spec), pin, phase], creationflags=subprocess.CREATE_NO_WINDOW)
            self.addCleanup(lambda: supervisor.kill() if supervisor.poll() is None else None)
            identity = self.wait_file(root / 'identity.json')
            self.assertEqual(supervisor.wait(timeout=8), 73)
            self.assert_extinct(identity)
            if phase == 'before':
                self.assertFalse((root / 'worker.json').exists())
            else:
                marker = self.wait_file(root / 'worker.json')
                self.assert_extinct(marker['worker'])
                self.assert_extinct(marker['child'])

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_claim_excludes_second_process_and_releases_after_crash(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock = root / 'scope.lock'
            owner = subprocess.Popen([sys.executable, '-B', '-m', 'tests.test_windows_acquisition', 'claim', str(root)],
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            self.addCleanup(lambda: owner.kill() if owner.poll() is None else None)
            self.wait_file(root / 'claim.json')
            with self.assertRaises(OSError):
                with api.exclusive_claim(lock):
                    self.fail('Second owner acquired live claim')
            (root / 'crash').write_text('exit owning interpreter')
            self.assertEqual(owner.wait(timeout=5), 73)
            with api.exclusive_claim(lock):
                self.assertEqual((root / 'reserve.json').read_text(), 'durable original reserve')

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_job_list_failure_no_process_or_get(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec, pin = self.spec(root)
            kernel = api._kernel()
            with patch.object(api, '_WORKER_MODULE', 'tests.test_windows_acquisition'), \
                    patch.object(api, '_kernel', return_value=kernel), patch.object(kernel, 'UpdateProcThreadAttribute', return_value=0), \
                    patch.object(kernel, 'CreateProcessW', side_effect=AssertionError('created uncontained')):
                with self.assertRaises(OSError):
                    api.run_contained_attempt(spec, pin, deadline_seconds=2, before_resume=lambda identity: self.fail('callback'))
            self.assertFalse((root / 'worker.json').exists())

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_resume_failure_kills_suspended_worker(self):
        api = importlib.import_module('bank_quality.windows_acquisition')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec, pin = self.spec(root)
            kernel = api._kernel()
            identities = []
            with patch.object(api, '_WORKER_MODULE', 'tests.test_windows_acquisition'), \
                    patch.object(api, '_kernel', return_value=kernel), patch.object(kernel, 'ResumeThread', return_value=0xFFFFFFFF):
                with self.assertRaises(OSError):
                    api.run_contained_attempt(spec, pin, deadline_seconds=2, before_resume=identities.append)
            self.assertFalse((root / 'worker.json').exists())
            self.assert_extinct(identities[0])


def _publish_json(path, value):
    """Publish a complete handshake marker before readers can observe its path."""
    payload = json.dumps(value)
    temporary = path.with_name('.' + path.name + '.' + uuid.uuid4().hex + '.tmp')
    with temporary.open('x', encoding='utf-8') as stream:
        stream.write(payload)
        stream.flush()
    os.replace(temporary, path)


def _fixture_worker():
    from bank_quality import windows_acquisition as api
    spec = json.loads(Path(sys.argv[1]).read_bytes())
    if spec.get('fixture_authorization'):
        from bank_quality import financial_acquisition as financial
        financial._ROOT = Path(spec['fixture_root'])
        financial._FROZEN = {key: tuple(value) for key, value in spec['fixture_frozen'].items()}
        _, target = financial._worker_authorization(spec)
        _publish_json(Path(spec['marker']), {'authorized_target': target['target_key']})
        return
    if spec.get('spawn_child'):
        child = subprocess.Popen([sys.executable, '-B', '-m', 'tests.test_windows_acquisition', 'child', spec['marker'] + '.child'],
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        stop = time.monotonic() + 5
        while not Path(spec['marker'] + '.child').exists():
            if time.monotonic() >= stop:
                raise RuntimeError('Child fixture marker timeout')
            time.sleep(.005)
        marker = {'worker': api._current_identity(), 'child': json.loads(Path(spec['marker'] + '.child').read_bytes())}
    else:
        marker = {'worker': api._current_identity()}
    _publish_json(Path(spec['marker']), marker)
    if spec.get('local_http'):
        from bank_quality.archive import fetch_bounded
        import urllib.parse
        url = spec['local_http']
        if urllib.parse.urlsplit(url).hostname != '127.0.0.1':
            raise ValueError('Diagnostic fixture only permits loopback')
        output = Path(spec['marker']).parent / 'http'
        output.mkdir()
        result = fetch_bounded(url, output, 'fixture', {'diagnostic': True},
                               body_budget_bytes=5 * 1024 * 1024, timeout_seconds=3)
        if not result.get('source_complete'):
            raise RuntimeError('Local HTTP fixture failed')
    time.sleep(spec.get('sleep_seconds', 0))


def _resource_diagnostic(workers):
    """Measured synthetic loopback load; not an acceptance benchmark for BCB bodies."""
    from concurrent.futures import ThreadPoolExecutor
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import ctypes as C
    from ctypes import wintypes as W
    import shutil
    from bank_quality import windows_acquisition as api
    class Memory(C.Structure):
        _fields_ = [('length', W.DWORD), ('load', W.DWORD)] + [(n, C.c_uint64) for n in (
            'physical_total', 'physical_free', 'page_total', 'page_free', 'virtual_total', 'virtual_free', 'extended')]
    class ProcessMemory(C.Structure):
        _fields_ = [('cb', W.DWORD), ('faults', W.DWORD)] + [(n, C.c_size_t) for n in (
            'peak_ws', 'ws', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'page', 'peak_page', 'private')]
    psapi = C.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [W.HANDLE, C.c_void_p, W.DWORD]
    kernel = api._kernel()
    def system():
        value = Memory()
        value.length = C.sizeof(value)
        api._checked(kernel.GlobalMemoryStatusEx(C.byref(value)), 'GlobalMemoryStatusEx')
        return {n: getattr(value, n) for n in ('physical_total', 'physical_free', 'page_total', 'page_free')}
    def sample():
        handle = kernel.CreateToolhelp32Snapshot(2, 0)
        entries = {}
        try:
            row = api._PROCESSENTRY()
            row.dwSize = C.sizeof(row)
            found = kernel.Process32FirstW(handle, C.byref(row))
            while found:
                entries[row.th32ProcessID] = row.th32ParentProcessID
                found = kernel.Process32NextW(handle, C.byref(row))
        finally:
            kernel.CloseHandle(handle)
        tree = {os.getpid()}
        while True:
            more = {pid for pid, parent in entries.items() if parent in tree}
            if more <= tree:
                break
            tree |= more
        ws = private = 0
        for pid in tree:
            handle = kernel.OpenProcess(0x1000 | 0x10, False, pid)
            if not handle:
                continue  # process may already have exited; stable samples include marked active trees
            try:
                value = ProcessMemory()
                value.cb = C.sizeof(value)
                if psapi.GetProcessMemoryInfo(handle, C.byref(value), C.sizeof(value)):
                    ws += value.ws
                    private += value.private
            finally:
                kernel.CloseHandle(handle)
        return {'ws_bytes': ws, 'private_commit_bytes': private, 'processes': len(tree), **system()}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b'x' * (1024 * 1024)
            self.send_response(200)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            for offset in range(0, len(body), 65536):
                self.wfile.write(body[offset:offset + 65536])
                self.wfile.flush()
                time.sleep(.015)
        def log_message(self, *args):
            pass
    case = WindowsAcquisitionTests()
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        baseline = sample()
        disk_before = shutil.disk_usage(root).free
        roots = [root / str(i) for i in range(workers)]
        for path in roots:
            path.mkdir()
        specs = [case.spec(path, spawn_child=True, sleep_seconds=.5,
                  local_http='http://127.0.0.1:' + str(server.server_port) + '/fixture') for path in roots]
        cancelled = threading.Event()
        samples, results = [], []
        began = time.monotonic()
        try:
            with patch.object(api, '_WORKER_MODULE', 'tests.test_windows_acquisition'), ThreadPoolExecutor(workers) as pool:
                futures = [pool.submit(api.run_contained_attempt, spec, pin, deadline_seconds=3,
                    before_resume=lambda identity: None, cancel_event=cancelled) for spec, pin in specs]
                # Fixture grandchildren deliberately remain alive: prove the full-tree deadline.
                while not all(f.done() for f in futures):
                    samples.append(sample())
                    time.sleep(.02)
                results = [f.result() for f in futures]
        finally:
            cancelled.set()
            server.shutdown()
            server.server_close()
        elapsed = time.monotonic() - began
        for path in roots:
            marker = case.wait_file(path / 'worker.json')
            case.assert_extinct(marker['worker'])
            case.assert_extinct(marker['child'])
        size = sum(path.stat().st_size for path in root.rglob('*') if path.is_file())
        return {'workers': workers, 'baseline': baseline, 'samples': len(samples),
            'peak_tree_ws_bytes': max(s['ws_bytes'] for s in samples),
            'peak_tree_private_commit_bytes': max(s['private_commit_bytes'] for s in samples),
            'peak_tree_processes': max(s['processes'] for s in samples),
            'minimum_physical_free_bytes': min(s['physical_free'] for s in samples),
            'minimum_commit_available_bytes': min(s['page_free'] for s in samples),
            'disk_free_before_bytes': disk_before, 'artifact_bytes': size,
            'payload_bytes': workers * 1024 * 1024, 'artifact_overhead_bytes': size - workers * 1024 * 1024,
            'elapsed_seconds_including_shutdown': elapsed, 'results': results,
            'all_worker_and_descendant_identities_extinct': True,
            'scope': 'loopback 1 MiB response per worker; whole coordinator and descendant tree sampled; not BCB acceptance'}


if __name__ == '__main__':
    if sys.argv[1] == 'child':
        from bank_quality.windows_acquisition import _current_identity
        _publish_json(Path(sys.argv[2]), _current_identity())
        time.sleep(20)
    elif sys.argv[1] == 'claim':
        from bank_quality.windows_acquisition import exclusive_claim, _current_identity
        root = Path(sys.argv[2])
        with exclusive_claim(root / 'scope.lock'):
            (root / 'reserve.json').write_text('durable original reserve')
            _publish_json(root / 'claim.json', _current_identity())
            stop = time.monotonic() + 20
            while not (root / 'crash').exists() and time.monotonic() < stop:
                time.sleep(.005)
            os._exit(73)
    elif sys.argv[1] == 'supervisor2':
        from concurrent.futures import ThreadPoolExecutor
        from bank_quality import windows_acquisition as api
        api._WORKER_MODULE = 'tests.test_windows_acquisition'
        roots = [Path(sys.argv[2]) / str(i) for i in range(2)]
        with ThreadPoolExecutor(2) as pool:
            for root in roots:
                spec = root / 'spec.json'
                pool.submit(api.run_contained_attempt, spec, hashlib.sha256(spec.read_bytes()).hexdigest(),
                    deadline_seconds=10, before_resume=lambda identity, root=root: _publish_json(root / 'identity.json', identity))
            stop = time.monotonic() + 8
            while not all((root / 'worker.json').exists() for root in roots):
                if time.monotonic() >= stop:
                    raise RuntimeError('Two active tree markers missing')
                time.sleep(.005)
            os._exit(73)
    elif sys.argv[1] == 'supervisor':
        from bank_quality import windows_acquisition as api
        import threading
        spec = Path(sys.argv[2])
        phase = sys.argv[4]
        api._WORKER_MODULE = 'tests.test_windows_acquisition'
        def crash_after_marker():
            while not (spec.parent / 'worker.json').exists():
                time.sleep(.005)
            os._exit(73)
        def commit(identity):
            _publish_json(spec.parent / 'identity.json', identity)
            if phase == 'before':
                os._exit(73)
            threading.Thread(target=crash_after_marker, daemon=True).start()
        api.run_contained_attempt(spec, sys.argv[3], deadline_seconds=10, before_resume=commit)
    else:
        _fixture_worker()

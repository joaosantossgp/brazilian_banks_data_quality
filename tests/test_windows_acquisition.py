"""Windows containment integration tests use only a known local fixture worker."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch


class WindowsAcquisitionTests(unittest.TestCase):
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


def _fixture_worker():
    from bank_quality import windows_acquisition as api
    spec = json.loads(Path(sys.argv[1]).read_bytes())
    if spec.get('fixture_authorization'):
        from bank_quality import financial_acquisition as financial
        financial._ROOT = Path(spec['fixture_root'])
        financial._FROZEN = {key: tuple(value) for key, value in spec['fixture_frozen'].items()}
        _, target = financial._worker_authorization(spec)
        Path(spec['marker']).write_text(json.dumps({'authorized_target': target['target_key']}))
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
    Path(spec['marker']).write_text(json.dumps(marker))
    time.sleep(spec.get('sleep_seconds', 0))


if __name__ == '__main__':
    if sys.argv[1] == 'child':
        from bank_quality.windows_acquisition import _current_identity
        Path(sys.argv[2]).write_text(json.dumps(_current_identity()))
        time.sleep(20)
    elif sys.argv[1] == 'claim':
        from bank_quality.windows_acquisition import exclusive_claim, _current_identity
        root = Path(sys.argv[2])
        with exclusive_claim(root / 'scope.lock'):
            (root / 'reserve.json').write_text('durable original reserve')
            (root / 'claim.json').write_text(json.dumps(_current_identity()))
            stop = time.monotonic() + 20
            while not (root / 'crash').exists() and time.monotonic() < stop:
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
            (spec.parent / 'identity.json').write_text(json.dumps(identity))
            if phase == 'before':
                os._exit(73)
            threading.Thread(target=crash_after_marker, daemon=True).start()
        api.run_contained_attempt(spec, sys.argv[3], deadline_seconds=10, before_resume=commit)
    else:
        _fixture_worker()

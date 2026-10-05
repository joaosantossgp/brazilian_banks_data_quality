import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from test_financial_pipeline import RESOURCES


class WindowsPipelineTests(unittest.TestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('bank_quality.windows_financial_pipeline'),
                             'Fixed contained CPU launcher is absent')
        return importlib.import_module('bank_quality.windows_financial_pipeline')

    def test_pipeline_launcher_keeps_acquisition_worker_and_120s_contract(self):
        api = self.api()
        from bank_quality import windows_acquisition as old
        # Input validation is platform-independent; native containment is tested below.
        with patch.object(old, 'require_supported'), self.assertRaises(ValueError):
            old.run_contained_attempt(Path('missing'), '0' * 64, deadline_seconds=121,
                                       before_resume=lambda value: self.fail('Unexpected launch'))
        with tempfile.TemporaryDirectory() as temp:
            spec = Path(temp) / 'spec.json'
            spec.write_text(json.dumps({'contract': 'financial-acquisition-worker-v1'}))
            with patch.object(old, 'require_supported'), self.assertRaises(ValueError):
                api.run_contained_stage(spec, hashlib.sha256(spec.read_bytes()).hexdigest(),
                                         resources=RESOURCES, before_resume=lambda value: self.fail('Unexpected launch'))

    @unittest.skipUnless(os.name == 'nt', 'Real Win32 API host required')
    def test_pipeline_worker_is_born_contained_and_descendants_are_extinct_on_guard(self):
        api = self.api()
        from bank_quality import financial_pipeline as pipeline
        from bank_quality import windows_acquisition as old
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = root / 'spec.json'
            spec.write_text(json.dumps({'contract': api.CONTRACT,
                'application_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                'worker_sha256': hashlib.sha256(Path(pipeline.__file__).read_bytes()).hexdigest()}))
            identities = []
            def callback(identity):
                self.assertTrue(identity['contained'])
                identities.append(identity)
                raise OSError('durable callback failed')
            with self.assertRaisesRegex(OSError, 'durable callback'):
                api.run_contained_stage(spec, hashlib.sha256(spec.read_bytes()).hexdigest(),
                                         resources=RESOURCES, before_resume=callback)
            self.assertTrue(old.identity_extinct(identities[0]))
            measured = api.run_contained_stage(spec, hashlib.sha256(spec.read_bytes()).hexdigest(),
                                               resources=RESOURCES, before_resume=identities.append)
            self.assertTrue(measured['tree_extinct'])
            self.assertGreaterEqual(measured['peak_tree_processes'], 1)
            self.assertTrue(all(old.identity_extinct(value) for value in measured['observed_identities']))
            sampler = api._sample
            samples = []
            def failed_measurement(*args):
                samples.append(1)
                if len(samples) == 2:
                    raise OSError('measurement failed after birth')
                return sampler(*args)
            with patch.object(api, '_sample', failed_measurement):
                with self.assertRaisesRegex(api.ResourceError, 'measurement'):
                    api.run_contained_stage(spec, hashlib.sha256(spec.read_bytes()).hexdigest(),
                                             resources=RESOURCES, before_resume=identities.append)
            self.assertTrue(old.identity_extinct(identities[-1]))
            def delayed(identity):
                identities.append(identity)
                time.sleep(.01)
            kernel = api.native._kernel()
            resumed = []
            class Proxy:
                def __getattr__(self, name):
                    if name == 'ResumeThread':
                        def resume(handle):
                            resumed.append(handle)
                            return kernel.ResumeThread(handle)
                        return resume
                    return getattr(kernel, name)
            with patch.object(api.native, '_kernel', return_value=Proxy()):
                timeout = api.run_contained_stage(spec, hashlib.sha256(spec.read_bytes()).hexdigest(),
                    resources={**RESOURCES, 'deadline_seconds': .002}, before_resume=delayed)
            self.assertEqual(resumed, [], 'Expired worker was resumed after the durable callback')
            self.assertTrue(timeout['deadline_reached'])
            self.assertTrue(timeout['tree_extinct'])
            self.assertTrue(old.identity_extinct(identities[-1]))

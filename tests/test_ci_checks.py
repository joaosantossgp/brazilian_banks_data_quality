"""Exercise the CI selector with actual Git diffs, including deletion/rename boundaries."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import io
import copy
import os

spec = importlib.util.spec_from_file_location('ci_checks', Path(__file__).parents[1] / 'scripts/check-ci.py')
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        self.write('README.md', '# Original\n')
        self.write('scripts/source.py', 'print(1)\n')
        self.commit()
        self.base = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True)

    def write(self, name, content):
        p = self.repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')

    def route(self):
        self.commit()
        return ci.inspect_diff(self.repo, self.base, self.git('rev-parse', 'HEAD').strip())

    def test_documentation_with_spaces_and_deleted_markdown(self):
        self.write('docs/a space.md', '# New\n')
        (self.repo / 'README.md').unlink()
        self.assertTrue(self.route()[0])

    def test_mixed_change_requires_software(self):
        self.write('README.md', '# Edited\n')
        self.write('scripts/source.py', 'print(2)\n')
        self.assertFalse(self.route()[0])

    def test_rename_code_to_documentation_cannot_hide_deletion(self):
        self.git('mv', 'scripts/source.py', 'docs.md')
        self.assertFalse(self.route()[0])

    def test_unknown_format_and_workflow_require_software(self):
        self.write('docs/config.json', '{}')
        self.write('.github/workflows/ci.yml', 'name: CI')
        self.assertFalse(self.route()[0])

    def test_executable_markdown_requires_software(self):
        self.write('docs/run.md', '# Looks like text\n')
        self.git('add', '.')
        self.git('update-index', '--chmod=+x', 'docs/run.md')
        self.git('commit', '-qm', 'executable')
        self.assertFalse(ci.inspect_diff(self.repo, self.base, self.git('rev-parse', 'HEAD').strip())[0])

    def test_invalid_or_empty_history_never_selects_documentation(self):
        with self.assertRaises(ValueError):
            ci.inspect_diff(self.repo, '0' * 40, self.base)
        self.assertFalse(ci.inspect_diff(self.repo, self.base, self.base)[0])

    def test_changed_document_has_real_local_link_validation(self):
        self.write('docs/note.md', '[ok](../README.md#original)\n[missing](absent.md)\n')
        _, changed = self.route()
        with self.assertRaisesRegex(ValueError, 'absent.md'):
            ci.check_documents(self.repo, changed)
        self.write('docs/note.md', '[ok](../README.md#original)\n[web](https://example.invalid)\n')
        ci.check_documents(self.repo, changed)

    def test_invalid_utf8_and_svg_are_rejected(self):
        p = self.repo / 'README.md'
        p.write_bytes(b'\xff')
        with self.assertRaises(UnicodeError):
            ci.check_documents(self.repo, ['README.md'])
        self.write('docs/broken.svg', '<svg>')
        with self.assertRaises(Exception):
            ci.check_documents(self.repo, ['docs/broken.svg'])

    def test_deleted_image_breaking_unchanged_document_is_rejected(self):
        self.write('docs/icon.svg', '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.write('README.md', '![image](docs/icon.svg)\n')
        self.commit()
        base = self.git('rev-parse', 'HEAD').strip()
        (self.repo / 'docs/icon.svg').unlink()
        self.commit()
        docs_only, changed = ci.inspect_diff(self.repo, base, self.git('rev-parse', 'HEAD').strip())
        self.assertTrue(docs_only)
        with self.assertRaisesRegex(ValueError, 'icon.svg'):
            ci.check_documents(self.repo, changed)

    def test_truncated_png_rejected(self):
        p = self.repo / 'docs/image.png'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'\x89PNG\r\n\x1a\n')
        with self.assertRaisesRegex(ValueError, 'PNG'):
            ci.check_documents(self.repo, ['docs/image.png'])

    def test_unavailable_diff_selects_full_tests_without_hiding_document_errors(self):
        with patch('sys.argv', ['check-ci.py', '--base', '0' * 40, '--head', self.base]), patch('sys.stdout', new_callable=io.StringIO) as output:
            ci.main()
        self.assertIn('docs_only=false', output.getvalue())
        with patch('sys.argv', ['check-ci.py', '--base', self.base, '--head', self.base]), patch.object(ci, 'inspect_diff', return_value=(True, ['README.md'])), patch.object(ci, 'check_documents', side_effect=ValueError('broken document')):
            with self.assertRaisesRegex(ValueError, 'broken document'):
                ci.main()

    def test_software_signature_preserves_docs_but_detects_all_other_changes(self):
        before = ci.software_signature(self.repo)
        self.write('README.md', '# Changed\n')
        self.write('docs/new.svg', '<svg/>')
        self.commit()
        self.assertEqual(before, ci.software_signature(self.repo))
        for path in ['scripts/source.py', 'tests/test_x.py', 'requirements.txt', '.github/workflows/ci.yml']:
            self.write(path, 'changed\n')
            self.commit()
            after = ci.software_signature(self.repo)
            self.assertNotEqual(before, after, path)
            before = after
        self.git('mv', 'scripts/source.py', 'docs/source.md')
        self.commit()
        self.assertNotEqual(before, ci.software_signature(self.repo))

    def test_software_signature_includes_executable_docs_and_merge_base_advances(self):
        before = ci.software_signature(self.repo)
        self.git('update-index', '--chmod=+x', 'README.md')
        self.git('commit', '-qm', 'mode')
        executable = ci.software_signature(self.repo)
        self.assertNotEqual(before, executable)
        self.git('checkout', '-qb', 'base-advance')
        self.write('scripts/base.py', 'base change\n')
        self.commit()
        self.assertNotEqual(executable, ci.software_signature(self.repo))

    def test_missing_signature_runs_full_tests(self):
        with patch('sys.argv', ['check-ci.py', '--base', self.base, '--head', self.base]), \
                patch.object(ci, 'inspect_diff', return_value=(False, ['scripts/source.py'])), \
                patch.object(ci, 'software_signature', side_effect=OSError('unavailable')), \
                patch('sys.stdout', new_callable=io.StringIO) as output:
            ci.main()
        self.assertIn('run_software=true', output.getvalue())

    def test_mixed_pr_reuses_software_without_skipping_document_checks(self):
        url='https://github.com/owner/repo/actions/runs/123'
        with patch('sys.argv', ['check-ci.py', '--base', self.base, '--head', self.base]), \
                patch.object(ci, 'inspect_diff', return_value=(False, ['README.md'])), \
                patch.object(ci, 'software_signature', return_value='a'*64), \
                patch.object(ci, 'reusable_run', return_value=url), \
                patch.object(ci, 'check_documents') as documents, \
                patch.object(ci.subprocess, 'run'), \
                patch.dict(os.environ, {'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':'owner/repo'}), \
                patch('sys.stdout', new_callable=io.StringIO) as output:
            ci.main()
        documents.assert_called_once()
        self.assertIn('docs_only=false', output.getvalue())
        self.assertIn('run_software=false', output.getvalue())
        self.assertIn('reused_run='+url, output.getvalue())


class ReuseTests(unittest.TestCase):
    def setUp(self):
        self.repo = 'owner/repo'
        self.signature = 'a' * 64
        self.run = dict(id=123, status='completed', conclusion='success', event='pull_request',
                        path='.github/workflows/ci.yml', run_attempt=1,
                        repository={'full_name': self.repo}, head_repository={'full_name': self.repo})
        self.jobs = [dict(name=name, status='completed', conclusion='success',
                          steps=[dict(name='Validated software tree ' + self.signature,
                                      status='completed', conclusion='success')])
                     for name in ['Offline tests', 'Windows native offline tests']]

    def reuse(self, run=None, jobs=None):
        run = self.run if run is None else run
        jobs = self.jobs if jobs is None else jobs
        def fetch(path):
            if '/workflows/ci.yml/runs?' in path:
                return {'workflow_runs': [run]}
            self.assertIn('/runs/123/attempts/1/jobs?', path)
            return {'jobs': jobs}
        return ci.reusable_run(self.repo, self.signature, '456', fetch)

    def test_reuse_requires_successful_actual_tests_on_identical_software(self):
        self.assertEqual('https://github.com/owner/repo/actions/runs/123', self.reuse())
        for status in ['failure', 'cancelled', 'skipped', None]:
            with self.subTest(status=status):
                jobs = copy.deepcopy(self.jobs)
                jobs[0]['conclusion'] = status
                self.assertIsNone(self.reuse(jobs=jobs))
        jobs = copy.deepcopy(self.jobs)
        jobs[0]['steps'][0]['name'] = 'Validated software tree ' + 'b' * 64
        self.assertIsNone(self.reuse(jobs=jobs))
        self.assertIsNone(self.reuse(jobs=[]))  # A docs-only successful run is not test evidence.
        self.assertIsNone(self.reuse(jobs=self.jobs[:1]))

    def test_rejects_forks_wrong_workflow_current_run_and_incomplete_marker(self):
        for key, value in [('id',456), ('conclusion','failure'), ('status','in_progress'),
                           ('path','.github/workflows/other.yml'), ('event','workflow_dispatch'),
                           ('head_repository',{'full_name':'fork/repo'})]:
            run = copy.deepcopy(self.run); run[key] = value
            with self.subTest(key=key):
                self.assertIsNone(self.reuse(run=run))
        jobs=copy.deepcopy(self.jobs); jobs[0]['steps'][0]['conclusion']='skipped'
        self.assertIsNone(self.reuse(jobs=jobs))

    def test_api_failure_or_bad_response_requires_fresh_tests(self):
        def unavailable(path): raise OSError('unavailable')
        self.assertIsNone(ci.reusable_run(self.repo, self.signature, '456', unavailable))
        self.assertIsNone(ci.reusable_run(self.repo, self.signature, '456', lambda path: {}))
        run=copy.deepcopy(self.run); run['repository']['full_name']=None
        self.assertIsNone(self.reuse(run=run))

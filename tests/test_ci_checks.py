"""Exercise the CI selector with actual Git diffs, including deletion/rename boundaries."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import io

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

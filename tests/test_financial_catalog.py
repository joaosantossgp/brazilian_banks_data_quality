"""Synthetic adversarial inputs for the catalog's metadata boundary."""
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from bank_quality import financial_catalog as catalog


class CatalogMetadataBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='catalog61-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / 'input.json'
        self.raw = b'{"selection":{"period":202312},"absence":null}'
        self.path.write_bytes(self.raw)
        self.ref = {'path': 'input.json', 'sha256': hashlib.sha256(self.raw).hexdigest()}

    def invalid(self, operation):
        with self.assertRaises(catalog.CatalogError) as ctx:
            operation()
        self.assertEqual(ctx.exception.code, 'integrity')

    def test_authenticated_bytes_and_json_are_captured(self):
        image = catalog._read_reference(self.root, self.ref)
        self.assertEqual(image.raw, self.raw)
        self.assertEqual(image.document(), {'selection': {'period': 202312}, 'absence': None})
        self.path.write_bytes(b'{"changed":true}')
        self.assertEqual(image.document()['selection']['period'], 202312)
        self.assertEqual(image.raw, self.raw)

    def test_missing_invalid_or_wrong_external_hash(self):
        for pin in [None, '', True, 123, 'x' * 64, 'a' * 63, 'A' * 64, '0' * 64]:
            with self.subTest(pin=pin):
                self.invalid(lambda: catalog._read_reference(self.root, {'path': 'input.json', 'sha256': pin}))
        self.invalid(lambda: catalog._read_reference(self.root, {'path': 'input.json'}))

    def test_references_have_exact_fields(self):
        self.invalid(lambda: catalog._read_reference(self.root, {**self.ref, 'accepted': True}))
        self.invalid(lambda: catalog._read_reference(self.root, []))

    def test_duplicate_keys_rejected_at_every_depth(self):
        for raw in [b'{"a":1,"a":2}', b'{"a":{"period":1,"period":2}}',
                    b'{"a":1,"\\u0061":2}', b'[{"a":1,"a":1}]']:
            with self.subTest(raw=raw):
                self.invalid(lambda: catalog._json_bytes(raw))

    def test_nonfinite_invalid_utf8_and_nonjson_rejected(self):
        for raw in [b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
                    b'{"x":1e999}', b'\xff', b'{}trailing', b'']:
            with self.subTest(raw=raw):
                self.invalid(lambda: catalog._json_bytes(raw))

    def test_path_escape_and_noncanonical_forms_rejected(self):
        for path in ['../input.json', '/input.json', 'C:/input.json', 'C:input.json',
                     '//server/input.json', 'x\\input.json', './input.json',
                     'x//input.json', 'x/../input.json', 'input.json/',
                     'input.json:stream', '', None, 'a\x00b', 'input.json. ',
                     'CON', 'nul.json']:
            with self.subTest(path=path):
                self.invalid(lambda: catalog._contained_path(self.root, path))

    def test_missing_reference_is_integrity_error(self):
        self.path.unlink()
        self.invalid(lambda: catalog._read_reference(self.root, self.ref))

    def test_metadata_size_is_bounded_before_capture(self):
        self.invalid(lambda: catalog._read_reference(self.root, self.ref, max_bytes=4))

    def test_symlink_file_and_directory_rejected(self):
        alias = self.root / 'alias.json'
        try:
            alias.symlink_to(self.path)
        except OSError as exc:
            self.skipTest(f'Symlink creation unavailable: {exc.winerror if hasattr(exc, "winerror") else exc.errno}')
        self.invalid(lambda: catalog._contained_path(self.root, 'alias.json'))
        directory = self.root / 'nested'
        directory.symlink_to(self.root, target_is_directory=True)
        self.invalid(lambda: catalog._contained_path(self.root, 'nested/input.json'))

    def test_root_link_rejected(self):
        inside = self.root / 'inside'
        inside.mkdir()
        (inside / 'input.json').write_bytes(self.raw)
        alias = self.root / 'root-link'
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except OSError:
            self.skipTest('Symlink creation unavailable')
        self.invalid(lambda: catalog._contained_path(alias, 'input.json'))
        self.invalid(lambda: catalog._contained_path(alias / 'inside', 'input.json'))

    @unittest.skipUnless(os.name == 'nt', 'Windows junction semantics')
    def test_windows_junction_directory_and_root_rejected(self):
        inside = self.root / 'inside'
        inside.mkdir()
        (inside / 'input.json').write_bytes(self.raw)
        alias = self.root / 'junction'
        result = subprocess.run(['cmd.exe', '/c', 'mklink', '/J', str(alias), str(self.root)],
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, 'Junction fixture creation failed')
        try:
            self.invalid(lambda: catalog._contained_path(self.root, 'junction/input.json'))
            self.invalid(lambda: catalog._contained_path(alias, 'input.json'))
            self.invalid(lambda: catalog._contained_path(alias / 'inside', 'input.json'))
        finally:
            # rmdir removes the junction itself, never recursively its target.
            alias.rmdir()
        self.assertEqual(self.path.read_bytes(), self.raw)

    def test_schema_and_integer_checks_do_not_coerce(self):
        catalog._fields({'a': 1}, ('a',))
        catalog._positive_integer(1)
        for value in [True, False, 0, -1, '1', 1.0, None]:
            self.invalid(lambda: catalog._positive_integer(value))
        for value in [{'a': 1, 'b': 2}, {}, [], None]:
            self.invalid(lambda: catalog._fields(value, ('a',)))

    def test_canonical_output_deterministic_and_strict(self):
        a = catalog._canonical({'z': None, 'a': 'é'})
        b = catalog._canonical({'a': 'é', 'z': None})
        self.assertEqual(a, b)
        self.assertEqual(a, b'{"a":"\xc3\xa9","z":null}\n')
        self.invalid(lambda: catalog._canonical({'a': float('nan')}))
        self.invalid(lambda: catalog._canonical({'a': float('inf')}))
        self.invalid(lambda: catalog._canonical({1: 'numeric key', '1': 'string key'}))


if __name__ == '__main__':
    unittest.main()

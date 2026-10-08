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


class CatalogAuthorityBoundaryTests(unittest.TestCase):
    def test_native_profile_hash_policy_is_local_to_profiles(self):
        with tempfile.TemporaryDirectory(prefix='catalog61-profile-') as folder:
            root = Path(folder); name = 'bank_quality/financial-reports-profiles/202406.json'
            target = root / name; target.parent.mkdir(parents=True)
            lf = b'{"selection":{"period":202406}}\n'
            reference = {'path': name, 'sha256': hashlib.sha256(lf).hexdigest(),
                         'hash_policy': 'installed_profile_native_lf'}
            for raw in (lf, lf.replace(b'\n', b'\r\n')):
                target.write_bytes(raw)
                self.assertEqual(catalog._native_profile_image(root, reference).raw, raw)
            reference['path'] = 'data/curated/manifest.json'
            with self.assertRaises(catalog.CatalogError):
                catalog._native_profile_image(root, reference)

    def test_supplement_and_pipeline_require_their_exact_authority_pins(self):
        with tempfile.TemporaryDirectory(prefix='catalog61-gate-pin-') as folder:
            for kind, parser in [('accepted_supplement403_v1', '_validate_supplement_gate'),
                                  ('pipeline57_v1', '_validate_pipeline_gate')]:
                value = self.gate()
                if kind == 'accepted_supplement403_v1':
                    value['selection']['period'] = 202403
                    value['proof'] = {'kind': kind, 'supplement': value['admission']}
                with self.subTest(kind=kind), self.assertRaises(catalog.CatalogError) as ctx:
                    getattr(catalog, parser)(Path(folder), value)
                self.assertEqual(ctx.exception.code, 'integrity')
                self.assertIn('authority pin', str(ctx.exception))

    def test_trusted_code_images_are_finite_and_physical(self):
        source = Path(__file__).resolve().parents[1] / 'bank_quality/financial_acquisition_batch.py'
        lf = source.read_bytes().replace(b'\r\n', b'\n')
        with tempfile.TemporaryDirectory(prefix='catalog61-code-image-') as folder:
            root = Path(folder); target = root / 'bank_quality/financial_acquisition_batch.py'
            target.parent.mkdir()
            for raw in (lf, lf.replace(b'\n', b'\r\n')):
                target.write_bytes(raw)
                ref = {'path': 'bank_quality/financial_acquisition_batch.py', 'sha256': hashlib.sha256(raw).hexdigest()}
                image = catalog._trusted_code_image(root, ref)
                self.assertEqual(image.raw, raw)
            changed = lf + b'\n# changed image\n'
            target.write_bytes(changed)
            with self.assertRaises(catalog.CatalogError):
                catalog._trusted_code_image(root, {'path': 'bank_quality/financial_acquisition_batch.py',
                                                   'sha256': hashlib.sha256(changed).hexdigest()})

    def gate(self):
        ref = {'path': 'data/runs/example.json', 'sha256': 'a' * 64}
        return {'contract': 'ifdata-financial-catalog-gate-v1',
                'selection': {'period': 202312, 'perspective': 1005, 'reports': [92, 96, 101, 98]},
                'revision': 'a' * 64, 'profile': {**ref, 'hash_policy': 'installed_profile_native_lf'},
                'admission': ref.copy(), 'parquet': ref.copy(),
                'proof': {'kind': 'pipeline57_v1', 'plan': ref.copy(), 'result': ref.copy(), 'head': ref.copy(),
                          'receipts': {s: ref.copy() for s in ('admit', 'convert', 'query', 'replay-admit',
                                                               'replay-convert', 'replay-query', 'compare')}},
                'limitations': []}

    def reject(self, value):
        with self.assertRaises(catalog.CatalogError) as ctx:
            catalog._handoff_shape(value)
        self.assertEqual(ctx.exception.code, 'integrity')

    def test_caller_boolean_is_not_authority(self):
        value = self.gate(); value['proof'] = {'kind': 'caller_boolean', 'accepted': True}; self.reject(value)

    def test_valid_handoff_shape_is_not_an_acceptance_flag(self):
        value = self.gate()
        self.assertIsNone(catalog._handoff_shape(value))
        self.assertNotIn('acceptance', value)

    def test_selection_does_not_coerce_or_deduplicate(self):
        for selection in [None, [], {'period': True, 'perspective': 1005, 'reports': [92, 96, 101, 98]},
                          {'period': 202312, 'perspective': True, 'reports': [92, 96, 101, 98]},
                          {'period': 202312, 'perspective': 1005, 'reports': [92, 92, 101, 98]},
                          {'period': 202312, 'perspective': 1005, 'reports': [92, 96, 101]},
                          {'period': 202312, 'perspective': 1005, 'reports': [92, 96, 101, True]}]:
            with self.subTest(selection=selection):
                value = self.gate(); value['selection'] = selection
                self.reject(value)

    def test_closed_handoff_rejects_extra_fields_and_revision_drift(self):
        value = self.gate(); value['accepted'] = True; self.reject(value)
        value = self.gate(); value['revision'] = 'b' * 64; self.reject(value)

    def test_unknown_future_type_does_not_expand_historical_authority(self):
        for kind in ['pipeline60_v1', 'standalone_v1', None, True]:
            value = self.gate(); value['proof'] = {'kind': kind}; self.reject(value)

    def test_proof_references_and_receipt_map_have_closed_shape(self):
        for reference in [None, [], {}, {'path': 'x', 'sha256': 'a' * 64, 'accepted': True}]:
            value = self.gate(); value['proof']['head'] = reference; self.reject(value)
        for receipts in [{}, [], {**self.gate()['proof']['receipts'], 'fake-stage': {}}]:
            value = self.gate(); value['proof']['receipts'] = receipts; self.reject(value)

    def test_historical_anchor_requires_trusted_base_before_reading_paths(self):
        with tempfile.TemporaryDirectory(prefix='catalog61-authority-') as folder:
            value = self.gate()
            value['proof'] = {'kind': 'installed_historical_anchor_v1', 'trusted_base_sha': '0' * 40,
                              'trusted_code': value['admission'], 'transport': value['admission'],
                              'ledger': value['admission'], 'replay_admission': value['admission'],
                              'replay_parquet': value['admission'], 'stage_evidence': {}}
            with self.assertRaises(catalog.CatalogError) as ctx:
                catalog._validate_historical_gate(Path(folder), value)
            self.assertEqual(ctx.exception.code, 'integrity')
            self.assertIn('trusted base', str(ctx.exception))

    def test_historical_type_never_accepts_202403(self):
        with tempfile.TemporaryDirectory(prefix='catalog61-authority-') as folder:
            value = self.gate(); value['selection']['period'] = 202403
            value['proof'] = {'kind': 'installed_historical_anchor_v1', 'trusted_base_sha': catalog._TRUSTED_BASE,
                              'trusted_code': value['admission'], 'transport': value['admission'],
                              'ledger': value['admission'], 'replay_admission': value['admission'],
                              'replay_parquet': value['admission'], 'stage_evidence': {}}
            with self.assertRaises(catalog.CatalogError) as ctx:
                catalog._validate_historical_gate(Path(folder), value)
            self.assertEqual(ctx.exception.code, 'integrity')
            self.assertIn('three historical', str(ctx.exception))


class CatalogInputAndRegistryTests(unittest.TestCase):
    def registry(self):
        # A synthetic offer is not an accepted financial snapshot.
        members = []
        periods = [year * 100 + month for year in range(2010, 2027)
                   for month in (3, 6, 9, 12) if year * 100 + month <= 202606]
        for period in periods:
            selection = {'period': period, 'perspective': 1005, 'reports': [1, 3, 4, 5]}
            member = {'selection': selection, 'catalog': {}, 'source_offers': [],
                      'reports': [{'report': {'id': report, 'n': f'Native {report}'},
                                   'catalog_pointer': f'/reports/{index}'}
                                  for index, report in enumerate(selection['reports'])],
                      'profile_path': None, 'profile_sha256': None}
            payload = {key: member[key] for key in ('selection', 'catalog', 'reports', 'source_offers')}
            member['descriptor_sha256'] = hashlib.sha256(catalog._canonical(payload)[:-1]).hexdigest()
            members.append(member)
        return {'contract': 'ifdata-financial-reports-registry-v1', 'members': members,
                'legacy_202312_sources': {}}

    def inputs(self):
        return {'contract': 'ifdata-financial-catalog-inputs-v1',
                'registry': {'path': 'bank_quality/financial-reports-registry.json', 'sha256': 'a' * 64},
                'gates': [], 'active_revisions': [], 'parent_catalog': None}

    def operation(self, name):
        operation = getattr(catalog, name, None)
        self.assertTrue(callable(operation), f'Missing catalog behavior: {name}')
        return operation

    def rejects(self, operation, value):
        with self.assertRaises(catalog.CatalogError) as ctx:
            operation(value)
        self.assertEqual(ctx.exception.code, 'integrity')

    def test_registry_freezes_66_offers_without_inventing_acceptance(self):
        operation = self.operation('_registry_entries')
        registry = self.registry()
        entries = operation(registry)
        self.assertEqual(len(entries), 66)
        self.assertEqual(entries[0]['selection']['period'], 201003)
        self.assertEqual(entries[-1]['selection']['period'], 202606)
        self.assertTrue(all(e['revisions'] == [] and e['active_revision'] is None for e in entries))
        self.assertEqual(entries[0]['reports'][0],
                         {'report_id': 1, 'native_name': 'Native 1', 'catalog_pointer': '/reports/0'})
        registry['members'][0]['selection']['reports'][0] = 999
        self.assertEqual(entries[0]['selection']['reports'], [1, 3, 4, 5])

    def test_registry_rejects_duplicates_missing_offer_extra_period_and_descriptor_drift(self):
        operation = self.operation('_registry_entries')
        registry = self.registry(); registry['members'][-1] = registry['members'][0]
        self.rejects(operation, registry)
        registry = self.registry(); registry['members'].pop()
        self.rejects(operation, registry)
        registry = self.registry(); registry['members'][-1]['selection']['period'] = 202609
        self.rejects(operation, registry)
        registry = self.registry(); registry['members'][0]['reports'][0]['report']['n'] = 'Altered'
        self.rejects(operation, registry)

    def test_registry_native_report_order_must_match_selection_even_with_recomputed_pin(self):
        operation = self.operation('_registry_entries')
        registry = self.registry(); member = registry['members'][0]
        member['reports'].reverse()
        payload = {key: member[key] for key in ('selection', 'catalog', 'reports', 'source_offers')}
        member['descriptor_sha256'] = hashlib.sha256(catalog._canonical(payload)[:-1]).hexdigest()
        self.rejects(operation, registry)

    def test_inputs_reject_duplicate_gate_path_pin_and_active_selection_before_normalizing(self):
        operation = self.operation('_catalog_inputs_shape')
        for second in [{'path': 'data/runs/gate.json', 'sha256': 'c' * 64},
                       {'path': 'data/runs/alias.json', 'sha256': 'b' * 64}]:
            value = self.inputs()
            value['gates'] = [{'path': 'data/runs/gate.json', 'sha256': 'b' * 64}, second]
            self.rejects(operation, value)
        value = self.inputs()
        choice = {'selection': self.registry()['members'][0]['selection'], 'revision_id': None}
        value['active_revisions'] = [choice, choice.copy()]
        self.rejects(operation, value)

    def test_inputs_closed_schema_hash_and_explicit_null_choice(self):
        operation = self.operation('_catalog_inputs_shape')
        value = self.inputs()
        value['active_revisions'] = [{'selection': self.registry()['members'][0]['selection'],
                                      'revision_id': None}]
        self.assertIsNone(operation(value))
        for change in [('accepted', True), ('contract', 'unknown'), ('gates', {}), ('active_revisions', None)]:
            value = self.inputs(); value[change[0]] = change[1]
            self.rejects(operation, value)
        value = self.inputs(); value['registry']['sha256'] = None
        self.rejects(operation, value)

    def test_explicit_revision_choices_require_offered_selection_and_available_revision(self):
        operation = self.operation('_apply_active_revisions')
        entries = self.operation('_registry_entries')(self.registry())
        selection = entries[0]['selection']
        entries[0]['revisions'] = [{'revision_id': 'b' * 64, 'acceptance': 'verified'},
                                   {'revision_id': 'c' * 64, 'acceptance': 'verified'}]
        operation(entries, [{'selection': selection, 'revision_id': 'c' * 64}])
        self.assertEqual(entries[0]['active_revision'], 'c' * 64)
        operation(entries, [{'selection': selection, 'revision_id': None}])
        self.assertIsNone(entries[0]['active_revision'])
        for choice in [{'selection': selection, 'revision_id': 'd' * 64},
                       {'selection': {**selection, 'period': 200912}, 'revision_id': None}]:
            with self.assertRaises(catalog.CatalogError) as ctx:
                operation(entries, [choice])
            self.assertEqual(ctx.exception.code, 'integrity')

    def test_missing_active_choice_does_not_choose_latest_or_erase_acceptance(self):
        operation = self.operation('_apply_active_revisions')
        entries = self.operation('_registry_entries')(self.registry())
        entries[0]['revisions'] = [{'revision_id': 'b' * 64, 'acceptance': 'verified'},
                                   {'revision_id': 'c' * 64, 'acceptance': 'verified'}]
        operation(entries, [])
        self.assertIsNone(entries[0]['active_revision'])
        self.assertEqual(len(entries[0]['revisions']), 2)


if __name__ == '__main__':
    unittest.main()

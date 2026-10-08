"""Synthetic adversarial inputs for the catalog's metadata boundary."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_preparation_scope_captures_each_metadata_path_once_without_leaking_between_commands(self):
        operation = getattr(catalog, '_capture_scope', None)
        self.assertTrue(callable(operation), 'Missing bounded preparation capture scope')
        with operation():
            first = catalog._read_reference(self.root, self.ref)
            self.path.write_bytes(b'{"changed":true}')
            second = catalog._read_reference(self.root, self.ref)
            self.assertIs(first, second)
            self.assertEqual(second.raw, self.raw)
            with self.assertRaises(catalog.CatalogError):
                catalog._read_reference(self.root, {**self.ref, 'sha256': hashlib.sha256(self.path.read_bytes()).hexdigest()})
        with self.assertRaises(catalog.CatalogError):
            catalog._read_reference(self.root, self.ref)

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

    def test_original_provenance_refs_are_lexically_canonical_without_reading_external_files(self):
        for name in ('../escape.json', 'C:/outside.json', 'data\\runs\\x.json',
                     'data/runs/AUX.json', 'data/runs/../x.json', 'data//runs/x.json'):
            value = self.gate(); value['admission']['path'] = name
            with self.subTest(path=name):
                self.reject(value)

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


class CatalogJournalProjectionTests(unittest.TestCase):
    def test_pipeline_journal_authority_uses_a_canonical_local_path(self):
        with tempfile.TemporaryDirectory(prefix='catalog61-journal-path-') as folder:
            path = catalog._contained_path(Path(folder), catalog._PIPELINE57_JOURNAL['path'])
            self.assertEqual(path.name, 'journal.jsonl')

    def journal(self):
        records = []
        tip = '0' * 64
        for stage in catalog._STAGES:
            for kind in ('start', 'finish'):
                sequence = len(records) + 1
                data = ({'spec': {'path': f'data/runs/stages/{stage}/spec.json', 'sha256': 'a' * 64}}
                        if kind == 'start' else
                        {'start_sequence': sequence - 1,
                         'receipt': {'path': f'data/runs/stages/{stage}/receipt.json', 'sha256': 'b' * 64}})
                record = {'sequence': sequence, 'previous_hash': tip, 'plan_sha256': 'c' * 64,
                          'kind': kind, 'member': 202406, 'stage': stage, 'data': data}
                raw = catalog._canonical(record)
                tip = hashlib.sha256(raw[:-1]).hexdigest()
                records.append(raw)
        raw = b''.join(records)
        image = catalog._PinnedImage('data/runs/execution/journal.jsonl', hashlib.sha256(raw).hexdigest(), raw)
        head = {'sequence': 14, 'journal_sha256': tip, 'plan_sha256': 'c' * 64}
        receipts = {stage: {'path': f'data/runs/stages/{stage}/receipt.json', 'sha256': 'b' * 64}
                    for stage in catalog._STAGES}
        return image, head, receipts

    def operation(self):
        operation = getattr(catalog, '_journal_projection', None)
        self.assertTrue(callable(operation), 'Missing frozen journal authority behavior')
        def check(image, head, member, receipts, *, specs=None):
            expected = specs if specs is not None else {
                stage: {'path': f'data/runs/stages/{stage}/spec.json', 'sha256': 'a' * 64}
                for stage in catalog._STAGES}
            return operation(image, head, member, receipts, specs=expected)
        return check

    def test_journal_projection_preserves_physical_pin_chain_and_member_finish_links(self):
        operation = self.operation()
        image, head, receipts = self.journal()
        projection = operation(image, head, 202406, receipts)
        self.assertEqual(projection['journal'], {'path': image.path, 'sha256': image.sha256, 'bytes': len(image.raw)})
        self.assertEqual(projection['head'], head)
        self.assertEqual(len(projection['finishes']), 7)
        self.assertEqual([f['stage'] for f in projection['finishes']], list(catalog._STAGES))
        self.assertEqual(projection['finishes'][0]['receipt'], receipts['admit'])
        self.assertNotIn('records', projection)

    def test_journal_projection_rejects_partial_chain_stale_head_and_wrong_member_receipt(self):
        operation = self.operation()
        image, head, receipts = self.journal()
        for raw, candidate_head, member, refs in [
            (image.raw[:-1], head, 202406, receipts),
            (image.raw, {**head, 'sequence': True}, 202406, receipts),
            (image.raw, {**head, 'journal_sha256': 'd' * 64}, 202406, receipts),
            (image.raw, head, 202409, receipts),
            (image.raw, head, 202406, {**receipts, 'compare': {'path': 'data/runs/other.json', 'sha256': 'b' * 64}}),
        ]:
            with self.subTest(member=member, bytes=len(raw)), self.assertRaises(catalog.CatalogError) as ctx:
                operation(catalog._PinnedImage(image.path, hashlib.sha256(raw).hexdigest(), raw),
                          candidate_head, member, refs)
            self.assertEqual(ctx.exception.code, 'integrity')

    def test_journal_projection_rejects_forged_image_pin_and_invalid_causality(self):
        operation = self.operation()
        image, head, receipts = self.journal()
        with self.assertRaises(catalog.CatalogError):
            operation(catalog._PinnedImage(image.path, 'd' * 64, image.raw), head, 202406, receipts)
        records = [catalog._json_bytes(line) for line in image.raw.splitlines()]
        records[1]['data']['start_sequence'] = True
        tip = '0' * 64; lines = []
        for record in records:
            record['previous_hash'] = tip
            raw = catalog._canonical(record); lines.append(raw)
            tip = hashlib.sha256(raw[:-1]).hexdigest()
        raw = b''.join(lines)
        with self.assertRaises(catalog.CatalogError):
            operation(catalog._PinnedImage(image.path, hashlib.sha256(raw).hexdigest(), raw),
                      {**head, 'journal_sha256': tip}, 202406, receipts)

    def test_journal_start_spec_must_match_the_authenticated_receipt_spec(self):
        operation = self.operation()
        image, head, receipts = self.journal()
        specs = {stage: {'path': f'data/runs/stages/{stage}/spec.json', 'sha256': 'a' * 64}
                 for stage in catalog._STAGES}
        specs['admit'] = {**specs['admit'], 'sha256': 'd' * 64}
        with self.assertRaises(catalog.CatalogError) as ctx:
            operation(image, head, 202406, receipts, specs=specs)
        self.assertIn('spec', str(ctx.exception))

    def test_journal_rechained_complete_pairs_still_require_pipeline_stage_order(self):
        operation = self.operation()
        image, head, receipts = self.journal()
        records = [catalog._json_bytes(line) for line in image.raw.splitlines()]
        # Preserve valid start/finish pairs and recompute every chain field.
        records = records[-2:] + records[:-2]
        tip = '0' * 64; lines = []
        for index, record in enumerate(records, 1):
            record['sequence'] = index; record['previous_hash'] = tip
            if record['kind'] == 'finish':
                record['data']['start_sequence'] = index - 1
            raw = catalog._canonical(record); lines.append(raw)
            tip = hashlib.sha256(raw[:-1]).hexdigest()
        raw = b''.join(lines)
        with self.assertRaises(catalog.CatalogError) as ctx:
            operation(catalog._PinnedImage(image.path, hashlib.sha256(raw).hexdigest(), raw),
                      {**head, 'journal_sha256': tip}, 202406, receipts)
        self.assertIn('order', str(ctx.exception))


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

    def test_explicit_null_choice_is_only_for_no_acceptance_or_ambiguity(self):
        entries = catalog._registry_entries(self.registry())
        entries[0]['revisions'] = [{'revision_id': 'b' * 64, 'acceptance': 'verified'}]
        with self.assertRaises(catalog.CatalogError):
            catalog._apply_active_revisions(entries, [{'selection': entries[0]['selection'], 'revision_id': None}])


class CatalogPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='catalog61-persistence-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.addCleanup(patch.stopall)
        patch.object(catalog, '_CHECKOUT_ROOT', self.root, create=True).start()
        (self.root / 'bank_quality').mkdir()
        (self.root / '.scratch').mkdir()
        (self.root / 'data/runs').mkdir(parents=True)
        registry = CatalogInputAndRegistryTests().registry()
        path = self.root / 'bank_quality/financial-reports-registry.json'
        path.write_bytes(catalog._canonical(registry))
        inputs = CatalogInputAndRegistryTests().inputs()
        inputs['registry']['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.inputs_path = self.root / '.scratch/catalog61-test-inputs.json'
        self.inputs_path.write_bytes(catalog._canonical(inputs))
        self.inputs_pin = hashlib.sha256(self.inputs_path.read_bytes()).hexdigest()
        self.output = self.root / 'data/runs/financial-catalog-test-one'

    def operation(self, name):
        operation = getattr(catalog, name, None)
        self.assertTrue(callable(operation), f'Missing persistent catalog behavior: {name}')
        return operation

    def prepare(self, destination=None):
        return self.operation('prepare_catalog')(self.inputs_path, destination or self.output,
                                                 inputs_sha256=self.inputs_pin)

    def load(self, result):
        return self.operation('load_catalog')(self.root / result['catalog']['path'],
                                              catalog_sha256=result['catalog']['sha256'])

    def test_catalog_is_deterministic_and_keeps_offers_distinct_from_acceptance(self):
        first = self.prepare()
        second = self.prepare(self.root / 'data/runs/financial-catalog-test-two')
        self.assertEqual(first['catalog']['sha256'], second['catalog']['sha256'])
        self.assertEqual(first['coverage'], {'offered': 66, 'accepted': 0, 'unavailable': 66, 'revision_count': 0})
        context = self.load(first)
        rows = self.operation('discover')(context)
        self.assertEqual(len(rows), 66)
        self.assertTrue(all(row['acceptance'] == 'unavailable' and row['counts'] is None for row in rows))
        self.assertEqual(context.sha256, first['catalog']['sha256'])

    def test_relative_api_paths_are_anchored_to_checkout_not_process_working_directory(self):
        result = self.operation('prepare_catalog')(Path('.scratch/catalog61-test-inputs.json'),
                       Path('data/runs/financial-catalog-relative'), inputs_sha256=self.inputs_pin)
        self.assertEqual(len(self.operation('discover')(self.operation('load_catalog')(
                         Path(result['catalog']['path']), catalog_sha256=result['catalog']['sha256']))), 66)

    def test_catalog_survives_removal_of_external_inputs_and_registry(self):
        result = self.prepare()
        self.inputs_path.unlink()
        (self.root / 'bank_quality/financial-reports-registry.json').unlink()
        rows = self.operation('discover')(self.load(result))
        self.assertEqual(len(rows), 66)

    def test_existing_output_and_invalid_input_pin_preserve_original_files(self):
        operation = self.operation('prepare_catalog')
        self.output.mkdir(); marker = self.output / 'keep.txt'; marker.write_bytes(b'preserve')
        for pin in (self.inputs_pin, None, '0' * 64):
            with self.subTest(pin=pin), self.assertRaises(catalog.CatalogError):
                operation(self.inputs_path, self.output, inputs_sha256=pin)
        self.assertEqual(marker.read_bytes(), b'preserve')
        self.assertEqual(sorted(p.name for p in self.output.iterdir()), ['keep.txt'])

    def test_catalog_and_companion_tampering_missing_or_extra_file_are_global_integrity_errors(self):
        result = self.prepare()
        operation = self.operation('load_catalog')
        path = self.root / result['catalog']['path']
        raw = path.read_bytes(); document = catalog._json_bytes(raw)
        companion = self.output / document['files'][0]['path']
        saved = companion.read_bytes()
        companion.write_bytes(saved + b' ')
        with self.assertRaises(catalog.CatalogError):
            self.load(result)
        companion.unlink()
        with self.assertRaises(catalog.CatalogError):
            self.load(result)
        companion.write_bytes(saved)
        extra = self.output / 'unexpected.json'; extra.write_bytes(b'{}')
        with self.assertRaises(catalog.CatalogError):
            self.load(result)
        extra.unlink()
        with self.assertRaises(catalog.CatalogError):
            operation(path, catalog_sha256='0' * 64)
        self.load(result)

    def test_recomputed_catalog_pin_does_not_hide_invalid_frozen_schema_or_counts(self):
        result = self.prepare(); path = self.root / result['catalog']['path']; raw = path.read_bytes()
        for field, value in [('coverage', {'offered': 66, 'accepted': True, 'unavailable': 65, 'revision_count': 0}),
                             ('entries', []), ('accepted', True)]:
            document = catalog._json_bytes(raw); document[field] = value
            changed = catalog._canonical(document); path.write_bytes(changed)
            with self.subTest(field=field), self.assertRaises(catalog.CatalogError):
                self.operation('load_catalog')(path, catalog_sha256=hashlib.sha256(changed).hexdigest())
        document = catalog._json_bytes(raw); document['files'][0]['path'] = None
        changed = catalog._canonical(document); path.write_bytes(changed)
        with self.assertRaises(catalog.CatalogError):
            self.operation('load_catalog')(path, catalog_sha256=hashlib.sha256(changed).hexdigest())

    def test_list_is_metadata_only_in_a_fresh_python_process(self):
        result = self.prepare()
        script = '''
import sys
from pathlib import Path
from bank_quality import financial_catalog as c
c._CHECKOUT_ROOT = Path(sys.argv[1])
assert 'duckdb' not in sys.modules
context = c.load_catalog(Path(sys.argv[2]), catalog_sha256=sys.argv[3])
assert len(c.discover(context)) == 66
assert 'duckdb' not in sys.modules
assert 'bank_quality.financial_pipeline' not in sys.modules
assert 'bank_quality.financial_acquisition' not in sys.modules
'''
        completed = subprocess.run([sys.executable, '-B', '-c', script, str(self.root),
                                    str(self.root / result['catalog']['path']), result['catalog']['sha256']],
                                   cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_frozen_context_cannot_be_forged_and_returned_rows_are_independent(self):
        result = self.prepare(); context = self.load(result)
        operation = self.operation('discover')
        rows = operation(context); rows[0]['selection']['reports'][0] = 999
        self.assertEqual(operation(context)[0]['selection']['reports'][0], 1)
        forged = self.operation('Catalog')(path=context.path, sha256=context.sha256)
        for value in ({'path': context.path, 'sha256': context.sha256}, forged):
            with self.assertRaises(catalog.CatalogError):
                operation(value)

    def test_discovery_filters_metadata_without_inventing_population_zero(self):
        context = self.load(self.prepare()); operation = self.operation('discover')
        self.assertEqual(len(operation(context, period=201003, perspective=1005, report_id=1)), 1)
        self.assertEqual(operation(context, period=200912), [])
        self.assertEqual(operation(context, report_id=999), [])
        with self.assertRaises(catalog.CatalogError):
            operation(context, period=True)

    def test_parent_is_pinned_preserved_and_not_required_for_loading_child(self):
        first = self.prepare(); before = (self.root / first['catalog']['path']).read_bytes()
        value = catalog._json_bytes(self.inputs_path.read_bytes()); value['parent_catalog'] = first['catalog']
        self.inputs_path.write_bytes(catalog._canonical(value))
        self.inputs_pin = hashlib.sha256(self.inputs_path.read_bytes()).hexdigest()
        second = self.prepare(self.root / 'data/runs/financial-catalog-test-two')
        self.assertEqual((self.root / first['catalog']['path']).read_bytes(), before)
        (self.root / first['catalog']['path']).unlink()
        self.assertEqual(len(self.operation('discover')(self.load(second))), 66)

    def test_freeze_deduplicates_identical_captures_but_rejects_conflicting_bytes(self):
        # Synthetic post-validation state tests copying, not the public acceptance boundary.
        gate = CatalogAuthorityBoundaryTests().gate()
        projection = {'cells': 1, 'observations': 1, 'cadaster_records': 1,
                      'presence_counts': {'stored': 1}, 'value_state_counts': {'numeric': 1},
                      'numeric_bindings': [{'encoding': 'decimal_text_v1'}]}
        images = []
        for field in ('profile', 'admission', 'parquet'):
            raw = catalog._canonical(projection if field == 'parquet' else {})
            image = catalog._PinnedImage(f'data/runs/{field}.json', hashlib.sha256(raw).hexdigest(), raw)
            images.append(image)
            gate[field] = {'path': image.path, 'sha256': image.sha256}
        gate['profile']['hash_policy'] = 'installed_profile_native_lf'
        gate['revision'] = gate['parquet']['sha256']
        gate_raw = catalog._canonical(gate)
        gate_image = catalog._PinnedImage('.scratch/catalog61-gate.json', hashlib.sha256(gate_raw).hexdigest(), gate_raw)
        verified = {'acceptance': 'verified', 'historical_stages': {'state': 'available'},
                    'parquet_metadata': projection, 'captured_images': tuple(images + [images[0]])}
        store = {}; revision = catalog._freeze_revision(gate_image, gate, verified, store)
        fragment = catalog._json_bytes(store[revision['proof']['path']])
        self.assertEqual(len(fragment['dependencies']), 4)
        self.assertEqual(revision['precision_encodings'], ['decimal_text_v1'])
        changed = catalog._PinnedImage(images[0].path, 'd' * 64, b'{} ')
        verified['captured_images'] = tuple(images + [changed])
        with self.assertRaises(catalog.CatalogError):
            catalog._freeze_revision(gate_image, gate, verified, {})

    def accepted_state(self, snapshot_files=None, *, cells=1, gate_path='.scratch/catalog61-test.json'):
        # Manufactured frozen post-validation state: it does not bypass or exercise a real authority parser.
        registry = CatalogInputAndRegistryTests().registry()
        entries = catalog._registry_entries(registry)
        entry = next(e for e in entries if e['selection']['period'] == 202403)
        selection = entry['selection']
        def image(path, value):
            raw = catalog._canonical(value)
            return catalog._PinnedImage(path, hashlib.sha256(raw).hexdigest(), raw)
        profile = image('bank_quality/financial-reports-profiles/202403.json', {'selection': selection})
        admission = image('data/derived/test/manifest.json', {'selection': selection, 'accepted': True,
                          'profile_sha256': profile.sha256, 'files': []})
        parquet = image('data/curated/test/manifest.json', {'selection': selection, 'accepted': True,
                        'profile_sha256': profile.sha256, 'source_manifest_sha256': admission.sha256,
                        'source_files': [], 'cells': cells, 'observations': 1, 'cadaster_records': 1,
                        'presence_counts': {'stored': 1}, 'value_state_counts': {'numeric': 1}, 'numeric_bindings': [],
                        'files': [] if snapshot_files is None else snapshot_files})
        ref = lambda captured: {'path': captured.path, 'sha256': captured.sha256}
        gate = {'contract': 'ifdata-financial-catalog-gate-v1', 'selection': selection, 'revision': parquet.sha256,
                'profile': {**ref(profile), 'hash_policy': 'installed_profile_native_lf'},
                'admission': ref(admission), 'parquet': ref(parquet),
                'proof': {'kind': 'accepted_supplement403_v1', 'supplement': catalog._SUPPLEMENT403}, 'limitations': []}
        gate_image = image(gate_path, gate)
        verified = {'acceptance': 'verified', 'historical_stages': {'state': 'available', 'kind': 'accepted_supplement403_v1'},
                    'parquet_metadata': parquet.document(), 'captured_images': (profile, admission, parquet)}
        store = {}; revision = catalog._freeze_revision(gate_image, gate, verified, store)
        entry['revisions'] = [revision]; entry['active_revision'] = parquet.sha256
        # Synthetic attestation of the already-validated finite supplement, with no original bytes available.
        fragment = catalog._json_bytes(store[revision['proof']['path']])
        fragment['dependencies'].append({**catalog._SUPPLEMENT403, 'bytes': 1})
        fragment['dependencies'].sort(key=lambda dep: dep['path'])
        store.pop(revision['proof']['path'])
        revision['proof'] = catalog._put_image(store, revision['proof']['path'], catalog._canonical(fragment))
        inputs = CatalogInputAndRegistryTests().inputs()
        inputs['registry']['sha256'] = hashlib.sha256(catalog._canonical(registry)).hexdigest()
        inputs['gates'] = [ref(gate_image)]
        inputs['active_revisions'] = [{'selection': selection, 'revision_id': parquet.sha256}]
        document = {'contract': 'ifdata-financial-catalog-v1',
                    'inputs': catalog._put_image(store, 'metadata/inputs.json', catalog._canonical(inputs)),
                    'registry': catalog._put_image(store, 'metadata/registry.json', catalog._canonical(registry)),
                    'parent_catalog': None, 'entries': entries, 'coverage': catalog._coverage(entries),
                    'files': [], 'limitations': []}
        return document, store, entry, revision

    def resolution_context(self, snapshot_files=None):
        document, store, entry, revision = self.accepted_state(snapshot_files)
        registry = catalog._json_bytes(store[document['registry']['path']])
        member = next(m for m in registry['members'] if m['selection'] == entry['selection'])
        member['profile_path'] = revision['profile']['path'].removeprefix('bank_quality/')
        member['profile_sha256'] = revision['profile']['sha256']
        registry_raw = catalog._canonical(registry)
        store[document['registry']['path']] = registry_raw
        document['registry']['sha256'] = hashlib.sha256(registry_raw).hexdigest()
        inputs = catalog._json_bytes(store[document['inputs']['path']])
        inputs['registry']['sha256'] = document['registry']['sha256']
        store[document['inputs']['path']] = catalog._canonical(inputs)
        document['inputs']['sha256'] = hashlib.sha256(store[document['inputs']['path']]).hexdigest()
        (self.root / 'bank_quality/financial-reports-registry.json').write_bytes(registry_raw)
        fragment = catalog._json_bytes(store[revision['proof']['path']])
        for key in ('profile', 'parquet'):
            original = revision[key]
            path = self.root / original['path']; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(store[fragment[key]['image']['path']])
        path, pin = self.persist_state(document, store, 'financial-catalog-resolution')
        return catalog.load_catalog(path, catalog_sha256=pin), entry, revision

    def resolve_error(self, context, expected, **selector):
        operation = self.operation('resolve_snapshot')
        with self.assertRaises(catalog.CatalogError) as caught:
            operation(context, period=selector.pop('period', 202403),
                      perspective=selector.pop('perspective', 1005), **selector)
        self.assertEqual(caught.exception.code, expected)

    def test_resolution_selects_full_snapshot_and_explicit_revision(self):
        context, entry, revision = self.resolution_context()
        operation = self.operation('resolve_snapshot')
        resolved = operation(context, period=202403, perspective=1005, report_id=3)
        self.assertEqual(resolved['selection'], entry['selection'])
        self.assertEqual(resolved['revision_id'], revision['revision_id'])
        self.assertEqual(resolved['manifest_sha256'], revision['parquet']['sha256'])
        self.assertEqual(resolved['destination'], self.root / 'data/curated/test')
        self.assertEqual(resolved['local_health'], 'metadata_verified')
        self.assertEqual(resolved['payload_validation'], 'not_run')
        self.assertFalse(resolved['registry_drift'])
        self.assertEqual(operation(context, period=202403, perspective=1005,
                                   revision_id=revision['revision_id'])['revision_id'], revision['revision_id'])

    def test_resolution_distinguishes_offer_absence_unknown_and_bad_revision(self):
        context, _, _ = self.resolution_context()
        self.resolve_error(context, 'unknown_selection', period=190003)
        self.resolve_error(context, 'unknown_selection', perspective=999)
        self.resolve_error(context, 'unknown_selection', report_id=999)
        self.resolve_error(context, 'unavailable', period=201003)
        self.resolve_error(context, 'unknown_selection', revision_id='a' * 64)
        self.resolve_error(context, 'integrity', report_id=True)
        self.resolve_error(context, 'integrity', revision_id='invalid')

    def test_resolution_blocks_manifest_changes_missing_and_profile_drift(self):
        context, _, revision = self.resolution_context()
        manifest = self.root / revision['parquet']['path']
        original = manifest.read_bytes(); manifest.write_bytes(b'{}')
        self.resolve_error(context, 'integrity')
        manifest.unlink(); self.resolve_error(context, 'missing_local_artifact')
        manifest.write_bytes(original)
        (self.root / revision['profile']['path']).write_bytes(b'{}')
        self.resolve_error(context, 'stale_context')
        self.assertEqual(catalog.discover(context, period=202403)[0]['acceptance'], 'verified')

    def test_resolution_only_target_member_drift_blocks_and_original_admission_not_required(self):
        context, _, revision = self.resolution_context()
        operation = self.operation('resolve_snapshot')
        path = self.root / 'bank_quality/financial-reports-registry.json'
        registry = catalog._json_bytes(path.read_bytes())
        registry['members'][0]['catalog'] = {'unrelated': 'changed'}
        payload = {k: registry['members'][0][k] for k in ('selection', 'catalog', 'reports', 'source_offers')}
        registry['members'][0]['descriptor_sha256'] = hashlib.sha256(catalog._canonical(payload)[:-1]).hexdigest()
        path.write_bytes(catalog._canonical(registry))
        resolved = operation(context, period=202403, perspective=1005)
        self.assertEqual(resolved['revision_id'], revision['revision_id'])
        self.assertTrue(resolved['registry_drift'])
        member = next(m for m in registry['members'] if m['selection']['period'] == 202403)
        member['profile_sha256'] = 'a' * 64
        path.write_bytes(catalog._canonical(registry))
        self.resolve_error(context, 'stale_context')

    def test_resolution_checks_declared_presence_and_metadata_hash_without_reading_payload(self):
        metadata = b'{"embedded":true}'
        payload = b'opaque synthetic payload'
        files = [{'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                 for name, raw in [('metadata/source-manifest.json', metadata), ('parts/cells.parquet', payload)]]
        context, _, revision = self.resolution_context(files)
        destination = (self.root / revision['parquet']['path']).parent
        for ref, raw in zip(files, (metadata, payload)):
            path = destination / ref['path']; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        operation = self.operation('resolve_snapshot')
        self.assertEqual(operation(context, period=202403, perspective=1005)['local_health'], 'metadata_verified')
        part = destination / 'parts/cells.parquet'
        part.write_bytes(b'x' * len(payload))
        self.assertEqual(operation(context, period=202403, perspective=1005)['payload_validation'], 'not_run')
        part.unlink(); self.resolve_error(context, 'missing_local_artifact')
        part.write_bytes(payload)
        (destination / files[0]['path']).write_bytes(b'x' * len(metadata))
        self.resolve_error(context, 'integrity')

    def test_resolution_rejects_snapshot_inventory_extras(self):
        context, _, revision = self.resolution_context()
        destination = (self.root / revision['parquet']['path']).parent
        (destination / 'extra.json').write_bytes(b'{}')
        self.resolve_error(context, 'integrity')

    def test_resolution_keeps_multiple_revisions_ambiguous_without_automatic_latest(self):
        self.resolution_context()  # Install matching current registry/profile/first manifest.
        document, store, entry, first = self.accepted_state()
        second_document, second_store, _, second = self.accepted_state(cells=2, gate_path='.scratch/catalog61-second.json')
        for name, raw in second_store.items():
            if name.startswith('metadata/revisions/'):
                store[name] = raw
        entry['revisions'] = sorted([first, second], key=lambda r: r['revision_id'])
        entry['active_revision'] = None
        inputs = catalog._json_bytes(store[document['inputs']['path']])
        other_inputs = catalog._json_bytes(second_store[second_document['inputs']['path']])
        inputs['gates'] += other_inputs['gates']
        inputs['active_revisions'] = [{'selection': entry['selection'], 'revision_id': None}]
        store[document['inputs']['path']] = catalog._canonical(inputs)
        document['inputs']['sha256'] = hashlib.sha256(store[document['inputs']['path']]).hexdigest()
        document['coverage'] = catalog._coverage(document['entries'])
        path, pin = self.persist_state(document, store, 'financial-catalog-two-revisions')
        context = catalog.load_catalog(path, catalog_sha256=pin)
        self.resolve_error(context, 'ambiguous_revision')
        selected = self.operation('resolve_snapshot')(context, period=202403, perspective=1005,
                                                      revision_id=first['revision_id'])
        self.assertEqual(selected['revision_id'], first['revision_id'])
        self.assertEqual(catalog.discover(context, period=202403)[0]['query_selection'], 'ambiguous_revision')

    def mutate_fragment(self, store, revision, change):
        name = revision['proof']['path']; fragment = catalog._json_bytes(store[name]); change(fragment)
        store.pop(name)
        revision['proof'] = catalog._put_image(store, name, catalog._canonical(fragment))

    def persist_state(self, document, store, name):
        # Write only synthetic metadata into this test's exclusive temporary checkout.
        destination = self.root / 'data/runs' / name; destination.mkdir()
        for relative, raw in store.items():
            path = destination / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        document['files'] = [{'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                             for path, raw in sorted(store.items())]
        raw = catalog._canonical(document); path = destination / 'catalog.json'; path.write_bytes(raw)
        return path, hashlib.sha256(raw).hexdigest()

    def test_load_with_a_post_validation_revision_keeps_acceptance_and_rejects_internal_inconsistency(self):
        document, store, entry, revision = self.accepted_state()
        path, pin = self.persist_state(document, store, 'financial-catalog-synthetic-accepted')
        context = catalog.load_catalog(path, catalog_sha256=pin)
        rows = catalog.discover(context, period=202403)
        self.assertEqual(rows[0]['acceptance'], 'verified')
        self.assertEqual(rows[0]['query_selection'], 'selected')
        self.assertEqual(rows[0]['local_health'], 'not_checked')
        self.assertEqual(rows[0]['counts']['cells'], 1)
        document, store, entry, revision = self.accepted_state()
        self.mutate_fragment(store, revision, lambda fragment: fragment.update(counts={**fragment['counts'], 'cells': 999}))
        path, pin = self.persist_state(document, store, 'financial-catalog-synthetic-inconsistent')
        with self.assertRaises(catalog.CatalogError):
            catalog.load_catalog(path, catalog_sha256=pin)

    def test_parent_revision_origins_are_frozen_and_cannot_be_reassigned(self):
        document, store, entry, revision = self.accepted_state()
        path, pin = self.persist_state(document, store, 'financial-catalog-synthetic-parent')
        inputs = catalog._json_bytes(self.inputs_path.read_bytes())
        inputs['parent_catalog'] = {'path': path.relative_to(self.root).as_posix(), 'sha256': pin}
        self.inputs_path.write_bytes(catalog._canonical(inputs)); self.inputs_pin = hashlib.sha256(self.inputs_path.read_bytes()).hexdigest()
        child = self.prepare(); path.unlink()
        rows = catalog.discover(self.load(child), period=202403)
        self.assertEqual(rows[0]['acceptance'], 'verified')
        child_path = self.root / child['catalog']['path']; child_doc = catalog._json_bytes(child_path.read_bytes())
        origin_path = self.output / 'metadata/parent.json'; origins = catalog._json_bytes(origin_path.read_bytes())
        origins['entries'][0]['revisions'][0]['gate_original']['sha256'] = 'd' * 64
        raw = catalog._canonical(origins); origin_path.write_bytes(raw)
        for ref in child_doc['files']:
            if ref['path'] == 'metadata/parent.json':
                ref.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        raw = catalog._canonical(child_doc); child_path.write_bytes(raw)
        with self.assertRaises(catalog.CatalogError):
            catalog.load_catalog(child_path, catalog_sha256=hashlib.sha256(raw).hexdigest())

    def test_frozen_authority_requires_dependency_links_and_gate_origin_from_inputs(self):
        document, store, entry, revision = self.accepted_state()
        catalog._frozen_document(document, store)
        self.mutate_fragment(store, revision, lambda fragment: fragment.update(dependencies=[]))
        with self.assertRaises(catalog.CatalogError):
            catalog._frozen_document(document, store)
        document, store, entry, revision = self.accepted_state()
        self.mutate_fragment(store, revision, lambda fragment: fragment.update(
                             gate_original={'path': '.scratch/catalog61-other.json', 'sha256': 'd' * 64}))
        with self.assertRaises(catalog.CatalogError):
            catalog._frozen_document(document, store)

    def test_frozen_registry_and_active_choice_must_match_pinned_inputs(self):
        for mismatch in ('registry', 'active'):
            document, store, entry, revision = self.accepted_state()
            inputs = catalog._json_bytes(store['metadata/inputs.json'])
            if mismatch == 'registry':
                inputs['registry']['sha256'] = 'd' * 64
            else:
                inputs['active_revisions'][0]['revision_id'] = None
            store.pop('metadata/inputs.json')
            document['inputs'] = catalog._put_image(store, 'metadata/inputs.json', catalog._canonical(inputs))
            with self.subTest(mismatch=mismatch), self.assertRaises(catalog.CatalogError):
                catalog._frozen_document(document, store)

    def test_canonical_gate_cannot_change_semantics_while_retaining_original_input_pin(self):
        document, store, entry, revision = self.accepted_state()
        fragment = catalog._json_bytes(store[revision['proof']['path']])
        gate_path = fragment['gate']['path']; gate = catalog._json_bytes(store[gate_path])
        gate['limitations'] = ['Changed after authentication']
        store.pop(gate_path); gate_ref = catalog._put_image(store, gate_path, catalog._canonical(gate))
        revision['limitations'] = gate['limitations']
        self.mutate_fragment(store, revision, lambda value: value.update(gate=gate_ref, limitations=gate['limitations']))
        with self.assertRaises(catalog.CatalogError):
            catalog._frozen_document(document, store)


if __name__ == '__main__':
    unittest.main()

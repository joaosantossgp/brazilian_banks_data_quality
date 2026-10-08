"""Financial catalog metadata boundary and finite snapshot authorities.

Construction and discovery freeze authenticated metadata; querying is added in
a subsequent checkpoint. Handoff shape and offers never authorize a snapshot.
"""
from dataclasses import dataclass
from contextlib import contextmanager
from contextvars import ContextVar
import ast
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import weakref


_MAX_METADATA_BYTES = 32 * 1024 * 1024
_HASH = re.compile(r'[0-9a-f]{64}\Z')
_RESERVED = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)),
             *(f'lpt{i}' for i in range(1, 10))}


class CatalogError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def _require(condition, message):
    if not condition:
        raise CatalogError('integrity', message)


def _fields(value, names):
    _require(type(value) is dict and set(value) == set(names), 'Unexpected metadata fields')


def _positive_integer(value):
    _require(type(value) is int and value > 0, 'Expected a positive integer')
    return value


def _hash(value):
    _require(type(value) is str and _HASH.fullmatch(value) is not None, 'Invalid external SHA-256')
    return value


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def _float(token):
    value = float(token)
    _require(math.isfinite(value), 'Nonfinite JSON number')
    return value


def _constant(token):
    raise CatalogError('integrity', 'Nonfinite JSON constant')


def _json_bytes(raw):
    _require(type(raw) is bytes, 'Expected captured JSON bytes')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                          parse_constant=_constant, parse_float=_float)
    except CatalogError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise CatalogError('integrity', 'Invalid UTF-8 JSON metadata') from exc


def _string_keys(value):
    if type(value) is dict:
        _require(all(type(k) is str for k in value), 'JSON object keys must be strings')
        for item in value.values():
            _string_keys(item)
    elif type(value) in (list, tuple):
        for item in value:
            _string_keys(item)


def _canonical(value):
    try:
        _string_keys(value)
        return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                           ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
    except CatalogError:
        raise
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise CatalogError('integrity', 'Metadata cannot be serialized canonically') from exc


def _plain_path(path):
    """Reject all Windows reparse kinds as well as portable symbolic links."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return
    _require(not stat.S_ISLNK(metadata.st_mode)
             and not getattr(metadata, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
             'Metadata path contains a link or reparse point')


def _relative_path_shape(relative):
    _require(type(relative) is str and relative, 'Expected a relative metadata path')
    _require(not any(ord(c) < 32 or c in '\\:<>"|?*' for c in relative), 'Noncanonical metadata path')
    p = PurePosixPath(relative)
    _require(not p.is_absolute() and p.as_posix() == relative
             and all(part not in ('.', '..') for part in p.parts), 'Metadata path escapes its root')
    _require(all(not part.endswith((' ', '.')) and part.split('.')[0].lower() not in _RESERVED
                 for part in p.parts), 'Windows metadata path alias')
    return p


def _contained_path(root, relative):
    p = _relative_path_shape(relative)
    try:
        anchor = Path(root).absolute()
        # Root itself can be plain while an ancestor redirects it via reparse.
        for ancestor in (anchor, *anchor.parents):
            _plain_path(ancestor)
        _require(anchor.is_dir(), 'Metadata root does not exist')
        target = anchor.joinpath(*p.parts)
        _require(target.resolve().is_relative_to(anchor.resolve()), 'Metadata path escapes its root')
        cursor = anchor
        for part in p.parts:
            cursor = cursor / part
            _plain_path(cursor)
        return target
    except CatalogError:
        raise
    except (OSError, ValueError, RuntimeError) as exc:
        raise CatalogError('integrity', 'Metadata path cannot be resolved safely') from exc


@dataclass(frozen=True)
class _PinnedImage:
    path: str
    sha256: str
    raw: bytes

    def document(self):
        # Reconstruct so mutable dictionaries cannot change the captured image.
        return _json_bytes(self.raw)


_CAPTURE_IMAGES = ContextVar('financial_catalog_capture_images', default=None)


@contextmanager
def _capture_scope():
    token = _CAPTURE_IMAGES.set({})
    try:
        yield
    finally:
        _CAPTURE_IMAGES.reset(token)


def _read_reference(root, reference, *, max_bytes=_MAX_METADATA_BYTES, json_required=True, native_profile=False):
    _fields(reference, ('path', 'sha256'))
    pin = _hash(reference['sha256'])
    _positive_integer(max_bytes)
    path = _contained_path(root, reference['path'])
    cache = _CAPTURE_IMAGES.get()
    cached = cache.get(str(path)) if cache is not None else None
    try:
        if cached is not None:
            raw = cached.raw
            _require(len(raw) <= max_bytes, 'Captured metadata exceeds its requested size limit')
        else:
            with path.open('rb') as stream:
                opened = os.fstat(stream.fileno())
                _require(stat.S_ISREG(opened.st_mode), 'Metadata reference is not a regular file')
                _require(opened.st_size <= max_bytes, 'Metadata reference exceeds its size limit')
                raw = stream.read(max_bytes + 1)
                _require(len(raw) <= max_bytes, 'Metadata reference grew beyond its size limit')
                current = _contained_path(root, reference['path']).stat()
                _require(os.path.samestat(opened, current), 'Metadata reference changed identity during capture')
    except CatalogError:
        raise
    except OSError as exc:
        raise CatalogError('integrity', 'Metadata reference cannot be captured') from exc
    physical = hashlib.sha256(raw).hexdigest()
    if native_profile:
        _require(reference['path'].startswith(('bank_quality/financial-reports-profile-',
                                              'bank_quality/financial-reports-profiles/'))
                 and reference['path'].endswith('.json'), 'Native profile policy used outside installed profiles')
    digest = hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() if native_profile else physical
    _require(digest == pin, 'Metadata reference SHA-256 mismatch')
    if json_required:
        _json_bytes(raw)
    image = cached if cached is not None else _PinnedImage(reference['path'], physical, raw)
    if cache is not None:
        cache[str(path)] = image
    return image


_TRUSTED_BASE = 'c7455f06ff2dc52a7958e300b19df01bca9b92c7'
_TRUSTED_CODE = {'path': 'bank_quality/financial_acquisition_batch.py',
                 'sha256': '176961e269879589ed45f6ef37b6ca670729649564ee24f0a4f611725e34448c'}
_TRUSTED_CODE_LF = '6c0d5e5ec5a605792a76491b10fe0a393d37972f5f8dd64d900b8291d03c2e2d'
_TRANSPORT_PIN = '28d2cd92e3f6caff4b59c36db1b18c7a25658c6dee9d26ffe875b1275a5d515e'
_STAGES = ('admit', 'convert', 'query', 'replay-admit', 'replay-convert', 'replay-query', 'compare')
_PROOF_FIELDS = {
    'installed_historical_anchor_v1': ('kind', 'trusted_base_sha', 'trusted_code', 'transport', 'ledger',
                                      'replay_admission', 'replay_parquet', 'stage_evidence'),
    'accepted_supplement403_v1': ('kind', 'supplement'),
    'pipeline57_v1': ('kind', 'plan', 'result', 'head', 'receipts'),
}


def _reference_shape(value):
    _fields(value, ('path', 'sha256'))
    _hash(value['sha256'])
    _relative_path_shape(value['path'])


def _selection_shape(selection):
    _fields(selection, ('period', 'perspective', 'reports'))
    _positive_integer(selection['period'])
    _require(_positive_integer(selection['perspective']) == 1005, 'Unsupported financial perspective')
    reports = selection['reports']
    _require(type(reports) is list and len(reports) == 4, 'Selection must contain four native reports')
    for report in reports:
        _positive_integer(report)
    _require(len(set(reports)) == len(reports), 'Duplicate native report')


def _selection_key(selection):
    _selection_shape(selection)
    return (selection['period'], selection['perspective'], tuple(selection['reports']))


def _active_choices_shape(choices):
    _require(type(choices) is list, 'Active revision choices must be a list')
    selections = set()
    for choice in choices:
        _fields(choice, ('selection', 'revision_id'))
        key = _selection_key(choice['selection'])
        _require(key not in selections, 'Duplicate active selection')
        selections.add(key)
        if choice['revision_id'] is not None:
            _hash(choice['revision_id'])


def _catalog_inputs_shape(value):
    """Validate explicit inputs before deduplication or normalization can hide conflicts."""
    _fields(value, ('contract', 'registry', 'gates', 'active_revisions', 'parent_catalog'))
    _require(value['contract'] == 'ifdata-financial-catalog-inputs-v1', 'Unknown catalog inputs contract')
    _reference_shape(value['registry'])
    _require(value['registry']['path'] == 'bank_quality/financial-reports-registry.json',
             'Catalog registry must be the installed finite offer registry')
    if value['parent_catalog'] is not None:
        _reference_shape(value['parent_catalog'])
    _require(type(value['gates']) is list, 'Catalog gates must be a list')
    paths, pins = set(), set()
    for ref in value['gates']:
        _reference_shape(ref)
        _require(ref['path'] not in paths and ref['sha256'] not in pins, 'Duplicate catalog gate reference')
        paths.add(ref['path']); pins.add(ref['sha256'])
    _active_choices_shape(value['active_revisions'])


_OFFERED_PERIODS = tuple(year * 100 + month for year in range(2010, 2027)
                       for month in (3, 6, 9, 12) if year * 100 + month <= 202606)


def _registry_entries(value):
    """Freeze metadata for the authorized 66 offers; never derive acceptance from a profile."""
    _fields(value, ('contract', 'members', 'legacy_202312_sources'))
    _require(value['contract'] == 'ifdata-financial-reports-registry-v1'
             and type(value['members']) is list and len(value['members']) == len(_OFFERED_PERIODS)
             and type(value['legacy_202312_sources']) is dict, 'Invalid finite registry')
    entries, periods = [], set()
    for member in value['members']:
        _fields(member, ('selection', 'catalog', 'reports', 'source_offers',
                         'profile_path', 'profile_sha256', 'descriptor_sha256'))
        selection = member['selection']
        _selection_shape(selection)
        _require(selection['period'] not in periods, 'Duplicate offered period')
        periods.add(selection['period'])
        _require(type(member['catalog']) is dict and type(member['source_offers']) is list
                 and all(type(source) is dict for source in member['source_offers']), 'Invalid native offer metadata')
        reports = member['reports']
        _require(type(reports) is list and len(reports) == 4, 'Invalid native report metadata')
        projected = []
        for report_id, item in zip(selection['reports'], reports):
            _fields(item, ('report', 'catalog_pointer'))
            report = item['report']
            _require(type(report) is dict and type(report.get('id')) is int and report['id'] == report_id
                     and type(report.get('n')) is str and report['n']
                     and type(item['catalog_pointer']) is str and item['catalog_pointer'].startswith('/'),
                     'Native reports differ from their ordered selection')
            projected.append({'report_id': report_id, 'native_name': report['n'],
                              'catalog_pointer': item['catalog_pointer']})
        # Match the installed descriptor API: canonical compact UTF-8 without newline.
        payload = {key: member[key] for key in ('selection', 'catalog', 'reports', 'source_offers')}
        pin = _hash(member['descriptor_sha256'])
        _require(hashlib.sha256(_canonical(payload)[:-1]).hexdigest() == pin, 'Native descriptor digest mismatch')
        if member['profile_path'] is None:
            _require(member['profile_sha256'] is None, 'Inactive offer has an unmatched profile pin')
        else:
            expected = (f'financial-reports-profile-{selection["period"]}.json'
                        if selection['period'] in (202412, 202503)
                        else f'financial-reports-profiles/{selection["period"]}.json')
            _require(member['profile_path'] == expected, 'Offer profile path is not its installed native path')
            _hash(member['profile_sha256'])
        entries.append({'selection': _json_bytes(_canonical(selection)), 'descriptor_sha256': pin,
                        'reports': projected, 'revisions': [], 'active_revision': None, 'limitations': []})
    _require(periods == set(_OFFERED_PERIODS), 'Registry differs from the authorized 66 periods')
    return sorted(entries, key=lambda entry: _selection_key(entry['selection']))


def _apply_active_revisions(entries, choices):
    """Apply only explicit choices, preserving acceptance when choice is absent or null."""
    _active_choices_shape(choices)
    by_selection = {_selection_key(entry['selection']): entry for entry in entries}
    _require(len(by_selection) == len(entries), 'Duplicate catalog selection')
    updates = []
    for choice in choices:
        key = _selection_key(choice['selection'])
        _require(key in by_selection, 'Active revision selection is not offered')
        entry, pin = by_selection[key], choice['revision_id']
        if pin is not None:
            verified = [revision for revision in entry['revisions']
                        if revision['revision_id'] == pin and revision['acceptance'] == 'verified']
            _require(len(verified) == 1, 'Active revision is not a unique verified revision')
        else:
            _require(sum(r['acceptance'] == 'verified' for r in entry['revisions']) != 1,
                     'Explicit null choice requires no acceptance or ambiguous revisions')
        updates.append((entry, pin))
    # Invalid choices must not leave partially applied active selections.
    for entry, pin in updates:
        entry['active_revision'] = pin


def _handoff_shape(value):
    _fields(value, ('contract', 'selection', 'revision', 'profile', 'admission', 'parquet', 'proof', 'limitations'))
    _require(value['contract'] == 'ifdata-financial-catalog-gate-v1', 'Unsupported catalog handoff')
    _selection_shape(value['selection'])
    for key in ('admission', 'parquet'):
        _reference_shape(value[key])
    _hash(value['revision'])
    _require(value['revision'] == value['parquet']['sha256'], 'Revision differs from Parquet manifest')
    _fields(value['profile'], ('path', 'sha256', 'hash_policy'))
    _reference_shape({k: value['profile'][k] for k in ('path', 'sha256')})
    _require(value['profile']['hash_policy'] == 'installed_profile_native_lf', 'Unsupported profile hash policy')
    proof = value['proof']
    _require(type(proof) is dict and type(proof.get('kind')) is str
             and proof['kind'] in _PROOF_FIELDS, 'Unknown catalog authority type')
    _fields(proof, _PROOF_FIELDS[proof['kind']])
    if proof['kind'] == 'pipeline57_v1':
        for key in ('plan', 'result', 'head'):
            _reference_shape(proof[key])
        _fields(proof['receipts'], _STAGES)
        for receipt in proof['receipts'].values():
            _reference_shape(receipt)
    elif proof['kind'] == 'accepted_supplement403_v1':
        _reference_shape(proof['supplement'])
    else:
        for key in ('trusted_code', 'transport', 'ledger', 'replay_admission', 'replay_parquet'):
            _reference_shape(proof[key])
    _require(type(value['limitations']) is list and all(type(x) is str for x in value['limitations']),
             'Invalid handoff limitations')
    # Syntax alone never sets acceptance. Each kind requires its authority parser.


def _trusted_code_image(root, reference):
    _reference_shape(reference)
    _require(reference['path'] == _TRUSTED_CODE['path']
             and reference['sha256'] in (_TRUSTED_CODE['sha256'], _TRUSTED_CODE_LF),
             'Historical code image is not the trusted authority')
    image = _read_reference(root, reference, json_required=False)
    _require(hashlib.sha256(image.raw.replace(b'\r\n', b'\n')).hexdigest() == _TRUSTED_CODE_LF,
             'Historical code image differs from the trusted Git base')
    return image


def _native_profile_image(root, reference):
    _fields(reference, ('path', 'sha256', 'hash_policy'))
    _require(reference['hash_policy'] == 'installed_profile_native_lf', 'Unsupported profile hash policy')
    _require(type(reference['path']) is str
             and reference['path'].startswith(('bank_quality/financial-reports-profile-',
                                               'bank_quality/financial-reports-profiles/')),
             'Native profile policy used outside installed profiles')
    return _read_reference(root, {k: reference[k] for k in ('path', 'sha256')}, native_profile=True)


def _validate_historical_gate(root, gate):
    """Verify the three installed anchors without executing archived code."""
    _handoff_shape(gate)
    proof, selection = gate['proof'], gate['selection']
    _require(proof['kind'] == 'installed_historical_anchor_v1', 'Wrong historical authority type')
    _require(proof['trusted_base_sha'] == _TRUSTED_BASE, 'Wrong trusted base for historical authority')
    _require(selection['period'] in (202312, 202412, 202503), 'Only three historical anchors are authorized')
    code = _trusted_code_image(root, proof['trusted_code'])
    try:
        tree = ast.parse(code.raw.decode('utf-8'))
        loops = [n for n in tree.body if isinstance(n, ast.For) and isinstance(n.iter, ast.Tuple)
                 and isinstance(n.target, ast.Tuple) and len(n.target.elts) == 10]
        _require(len(loops) == 1, 'Historical anchor table is ambiguous')
        rows = ast.literal_eval(loops[0].iter)
    except (SyntaxError, UnicodeError, ValueError) as exc:
        raise CatalogError('integrity', 'Invalid trusted anchor table') from exc
    _require(tuple(r[0] for r in rows) == (202312, 202412, 202503), 'Historical table was expanded')
    row = next(r for r in rows if r[0] == selection['period'])
    period, snapshot, manifest_pin, admission, source_pin, profile_name, physical_pin, native_pin, index_name, index_pin = row
    expected_selection = {'period': period, 'perspective': 1005,
                          'reports': [119, 107, 110, 118] if period == 202503 else [92, 96, 101, 98]}
    _require(selection == expected_selection, 'Historical native selection differs')
    expected_parquet = {'path': f'data/curated/{snapshot}/manifest.json', 'sha256': manifest_pin}
    expected_admission = {'path': f'data/derived/{admission}/manifest.json', 'sha256': source_pin}
    _require(gate['parquet'] == expected_parquet and gate['admission'] == expected_admission,
             'Historical primary pins differ')
    _require(gate['profile'] == {'path': 'bank_quality/' + profile_name, 'sha256': native_pin,
                                 'hash_policy': 'installed_profile_native_lf'}, 'Historical profile differs')
    images = [code]
    def capture(ref):
        image = _read_reference(root, ref)
        images.append(image)
        return image.document()
    transport = capture(proof['transport'])
    _require(proof['transport']['sha256'] == _TRANSPORT_PIN, 'Wrong migration transport authority')
    _require(type(transport.get('files')) is dict, 'Invalid transport inventory')
    def transported(ref):
        doc = capture(ref)
        item = transport['files'].get(ref['path'])
        _require(type(item) is dict and item.get('sha256') == ref['sha256']
                 and item.get('bytes') == len(images[-1].raw), 'Historical transport link differs')
        return doc
    pq, adm = transported(gate['parquet']), transported(gate['admission'])
    pimage = _read_reference(root, {'path': 'bank_quality/' + profile_name, 'sha256': physical_pin})
    images.append(pimage)
    _require(hashlib.sha256(pimage.raw.replace(b'\r\n', b'\n')).hexdigest() == native_pin, 'Native profile differs')
    profile = pimage.document()
    index = capture({'path': index_name, 'sha256': index_pin})
    _require(all(d.get('selection') == selection for d in (pq, adm, profile, index)), 'Historical lineage selection differs')
    _require(pq.get('accepted') is True and adm.get('accepted') is True, 'Historical snapshot not accepted')
    _require(pq.get('contract') == ('ifdata-financial-reports-historical-parquet-v2' if period == 202312
                                  else f'ifdata-financial-reports-parquet-{period}-v1'), 'Historical Parquet contract differs')
    _require(adm.get('contract') == ('ifdata-financial-reports-historical-snapshot-v1' if period == 202312
                                   else f'ifdata-financial-reports-snapshot-{period}-v1'), 'Historical admission contract differs')
    _require(pq.get('profile_sha256') == adm.get('profile_sha256') == native_pin
             and pq.get('source_manifest_sha256') == source_pin and pq.get('source_files') == adm.get('files')
             and adm.get('input_index_sha256') == index_pin, 'Historical cross-pins differ')
    embedded = transported({'path': expected_parquet['path'].rsplit('/', 1)[0] + '/metadata/source-manifest.json',
                            'sha256': source_pin})
    _require(embedded == adm, 'Historical embedded admission differs')
    for key, prefix in (('replay_admission', 'data/derived/' + admission),
                        ('replay_parquet', 'data/curated/' + snapshot)):
        _require(proof[key]['path'] == prefix + '-replay/manifest.json', 'Historical replay path differs')
    ra, rp = transported(proof['replay_admission']), transported(proof['replay_parquet'])
    _require(ra.get('accepted') is True and rp.get('accepted') is True and ra.get('selection') == rp.get('selection') == selection
             and rp.get('source_manifest_sha256') == proof['replay_admission']['sha256']
             and rp.get('source_files') == ra.get('files'), 'Historical replay lineage differs')
    ledger_name = ('docs/engineering/financial-historical-admission-20261004.md' if period == 202312
                   else f'docs/engineering/financial-four-reports-{period}-execution-20261004.md')
    _require(proof['ledger']['path'] == ledger_name, 'Historical ledger path differs')
    ledger = _read_reference(root, proof['ledger'], json_required=False)
    images.append(ledger)
    record = transport['files'].get(ledger_name)
    _require(type(record) is dict and record.get('sha256') == ledger.sha256, 'Historical ledger pin differs')
    stage = proof['stage_evidence']
    _fields(stage, ('state', 'schema', 'query', 'replay_query', 'compare'))
    if period != 202312:
        _require(stage == {'state': 'absent_from_transport', 'schema': None, 'query': None,
                           'replay_query': None, 'compare': None}, 'Unavailable stages cannot acquire flags')
    else:
        _require(stage['state'] == 'available' and stage['schema'] == 'legacy202312_exact_metadata_v1',
                 'Historical202312 stage schema differs')
        for key, file, pin in (('query', 'gate-query.json', '3d9209ab975ae605d66fcb5e1520fd54eb3e52558ad7ab586ba0174fc4374d1c'),
                               ('replay_query', 'gate-replay-query.json', 'f96c6fb8aeb8df6c45f240ee1e4296040c723eb9a8fbff9ecb88433b63c8cf31'),
                               ('compare', 'gate-compare.json', '839b24bd4d256ad33d783101fa23b9083005e6f1b35d5a7aa3ed30761c94bd7a')):
            expected = {'path': 'data/runs/financial-historical-admission-202312-20261004/' + file, 'sha256': pin}
            _require(stage[key] == expected, 'Historical202312 stage pin differs')
            doc = transported(stage[key])
            if key != 'compare':
                _fields(doc, ('stage', 'manifest_sha256', 'grade_columns', 'grade_all_varchar', 'cells',
                              'observations', 'binding_nodes', 'cadaster_records', 'presence_counts',
                              'value_state_counts', 'typed_views_checked',
                              'all_original_csvs_origins_and_decimal_rows_validated_by_adapter',
                              'exact_python_decimal_rows_checked', 'accessor_snapshots_opened', 'wide_text_bindings'))
                projection = pq if key == 'query' else rp
                _require(doc.get('manifest_sha256') == (manifest_pin if key == 'query' else proof['replay_parquet']['sha256'])
                         and doc.get('stage') == ('query' if key == 'query' else 'replay-query'), 'Historical query link differs')
                for field in ('cells', 'observations', 'cadaster_records', 'presence_counts', 'value_state_counts'):
                    _require(doc.get(field) == projection.get(field), 'Historical query counts differ')
                bindings = projection['numeric_bindings']
                _require(doc['grade_columns'] == 32 and doc['grade_all_varchar'] is True
                         and doc['all_original_csvs_origins_and_decimal_rows_validated_by_adapter'] is True
                         and doc['accessor_snapshots_opened'] == 1
                         and doc['binding_nodes'] == sum(len(r['nodes']) for r in profile['reports'])
                         and doc['exact_python_decimal_rows_checked'] == len(bindings) * projection['cadaster_records']
                         and doc['wide_text_bindings'] == sum(b['encoding'] == 'decimal_text_v1' for b in bindings),
                         'Historical query typed coverage differs')
                _require(type(doc['typed_views_checked']) is list and len(doc['typed_views_checked']) == len(bindings),
                         'Historical typed views differ')
                for view, binding in zip(doc['typed_views_checked'], bindings):
                    _fields(view, ('view', 'type', 'encoding', 'rows', 'nonnull_sample_present'))
                    _require(view['view'] == binding['view'] and view['type'] == binding['storage_type']
                             and view['encoding'] == binding['encoding'] and view['rows'] == binding['rows']
                             and type(view['nonnull_sample_present']) is bool, 'Historical typed view differs')
            else:
                _fields(doc, ('stage', 'comparisons', 'protected_equal', 'http_requests', 'accepted_sources_unchanged'))
                _require(doc.get('stage') == 'compare' and doc.get('http_requests') == 0
                         and doc.get('accepted_sources_unchanged') is True, 'Historical comparison differs')
                _positive_integer(doc['protected_equal'])
                _fields(doc['comparisons'], ('admission', 'parquet'))
                for name, manifest, excluded in (('admission', adm, ['manifest.json']),
                                                 ('parquet', pq, ['manifest.json', 'metadata/source-manifest.json'])):
                    check = doc['comparisons'][name]
                    _fields(check, ('byte_equal', 'excluded_execution_metadata'))
                    _require(check['excluded_execution_metadata'] == excluded
                             and check['byte_equal'] == sorted(r['path'] for r in manifest['files']
                                                              if r['path'] != 'metadata/source-manifest.json'),
                             'Historical comparison inventory differs')
    return {'acceptance': 'verified', 'historical_stages': stage.copy(), 'parquet_metadata': pq,
            'profile_metadata': profile, 'captured_images': tuple(images)}


_SUPPLEMENT403 = {'path': 'data/runs/financial-batch-sanitization-inputs-20261005/accepted-supplement.json',
                  'sha256': 'a4295c26925be5ef771f3fea8cd8a52b37bf03ed89cade32ed188e1a4409c2e2'}
_PIPELINE57_ROOT = 'data/runs/financial-batch-sanitization-202312-202606-20261005-attempt2/'
_PIPELINE57_PLAN = {'path': _PIPELINE57_ROOT + 'plan.json',
                    'sha256': '86d6432c3238699947b4c5d1dc63d367848ec225eb80fb30cf94234a736569f5'}
_PIPELINE57_RESULT = {'path': _PIPELINE57_ROOT + 'execution/result-98.json',
                      'sha256': '438d084a331d9e43d902244060caf922e38d8a65b8f0eab19fb3735958a91485'}
_PIPELINE57_HEAD = {'path': _PIPELINE57_ROOT + 'execution/head.json',
                    'sha256': '70c952d05c99df09123de6b78b5b008b93ccfa02f7b5befb2752caf39ddd9da6'}


def _projection_links(admission, parquet, admission_ref, selection, profile_pin):
    _require(admission.get('selection') == parquet.get('selection') == selection
             and admission.get('accepted') is True and parquet.get('accepted') is True,
             'Snapshot selection/acceptance differs')
    _require(admission.get('profile_sha256') == parquet.get('profile_sha256') == profile_pin
             and parquet.get('source_manifest_sha256') == admission_ref['sha256']
             and parquet.get('source_files') == admission.get('files'), 'Snapshot cross-pins differ')


def _validate_supplement_gate(root, gate):
    _handoff_shape(gate)
    proof = gate['proof']
    _require(proof['kind'] == 'accepted_supplement403_v1'
             and proof['supplement'] == _SUPPLEMENT403, 'Wrong supplement authority pin')
    images = []
    def capture(ref):
        image = _read_reference(root, ref); images.append(image)
        return image.document()
    supplement = capture(proof['supplement'])
    _fields(supplement, ('contract', 'members', 'limitations'))
    _require(supplement['contract'] == 'ifdata-financial-accepted-supplement-v1'
             and type(supplement['members']) is list and len(supplement['members']) == 1,
             'Unsupported supplement metadata')
    member = supplement['members'][0]
    _fields(member, ('selection', 'evidence'))
    expected = {'period': 202403, 'perspective': 1005, 'reports': [92, 96, 101, 98]}
    _require(member['selection'] == gate['selection'] == expected, 'Supplement native selection differs')
    refs = member['evidence']
    _fields(refs, ('profile', 'admission', 'parquet', 'replay_admission', 'replay_parquet', 'query', 'replay_query', 'compare'))
    _require(gate['admission'] == refs['admission'] and gate['parquet'] == refs['parquet']
             and gate['profile'] == {**refs['profile'], 'hash_policy': 'installed_profile_native_lf'},
             'Supplement handoff refs differ')
    docs = {key: capture(image) for key, image in refs.items()}
    native = _native_profile_image(root, gate['profile']); images.append(native)
    _require(native.document() == docs['profile'] and docs['profile']['selection'] == expected,
             'Supplement installed profile differs')
    for prefix in ('', 'replay_'):
        admission, parquet, query = (docs[prefix + key] for key in ('admission', 'parquet', 'query'))
        _projection_links(admission, parquet, refs[prefix + 'admission'], expected, gate['profile']['sha256'])
        _fields(query, ('accessor_snapshots_opened', 'all_original_csvs_origins_and_decimal_rows_validated_by_adapter',
                        'baseline_sha256', 'binding_nodes', 'cadaster_columns', 'cadaster_records', 'cells', 'contract',
                        'exact_python_decimal_rows_checked', 'execution_head', 'grade_all_varchar', 'grade_columns',
                        'http_requests', 'manifest_sha256', 'observations', 'presence_counts', 'stage',
                        'typed_views_checked', 'value_state_counts', 'wide_text_bindings'))
        _require(query['contract'] == 'root-offline-financial-gate-stage-v1'
                 and query['stage'] == ('replay-query' if prefix else 'query')
                 and query['manifest_sha256'] == refs[prefix + 'parquet']['sha256']
                 and query['grade_columns'] == 32 and query['grade_all_varchar'] is True
                 and query['all_original_csvs_origins_and_decimal_rows_validated_by_adapter'] is True
                 and query['accessor_snapshots_opened'] == 1 and query['http_requests'] == 0,
                 'Supplement query evidence differs')
        for field in ('cells', 'observations', 'cadaster_records', 'presence_counts', 'value_state_counts'):
            _require(query[field] == parquet[field], 'Supplement query counts differ')
        bindings = parquet['numeric_bindings']
        expected_views = [{'view': b['view'], 'rows': parquet['cadaster_records'],
                           'encoding': b.get('encoding', 'duckdb_decimal'),
                           'storage_type': b.get('storage_type', b['decimal_type'])} for b in bindings]
        _require(query['typed_views_checked'] == expected_views
                 and query['exact_python_decimal_rows_checked'] == len(bindings) * parquet['cadaster_records']
                 and query['binding_nodes'] == sum(len(r['nodes']) for r in docs['profile']['reports'])
                 and query['cadaster_columns'] == len(docs['profile']['cadaster_columns']),
                 'Supplement accessor/typed coverage differs')
    comparison = docs['compare']
    _fields(comparison, ('accepted_sources_unchanged', 'all_manifest_payloads_authenticated', 'baseline_sha256',
                         'comparisons', 'contract', 'execution_head', 'http_requests', 'protected_equal', 'stage'))
    _require(comparison['contract'] == 'root-offline-financial-gate-stage-v1'
             and comparison['stage'] == 'compare' and comparison['http_requests'] == 0
             and comparison['all_manifest_payloads_authenticated'] is True
             and comparison['accepted_sources_unchanged'] is True, 'Supplement comparison evidence differs')
    _positive_integer(comparison['protected_equal'])
    for key in ('baseline_sha256', 'execution_head'):
        _require(type(comparison[key]) is str and comparison[key]
                 and comparison[key] == docs['query'][key] == docs['replay_query'][key], 'Supplement execution origin differs')
    _fields(comparison['comparisons'], ('admission', 'parquet'))
    for kind, excluded in (('admission', ['manifest.json']), ('parquet', ['manifest.json', 'metadata/source-manifest.json'])):
        check = comparison['comparisons'][kind]
        _fields(check, ('byte_equal', 'separately_validated_execution_metadata'))
        _require(check['separately_validated_execution_metadata'] == excluded
                 and check['byte_equal'] == sorted(r['path'] for r in docs[kind]['files']
                                                  if r['path'] != 'metadata/source-manifest.json'),
                 'Supplement comparison inventory differs')
    return {'acceptance': 'verified', 'historical_stages': {'state': 'available', 'kind': proof['kind']},
            'parquet_metadata': docs['parquet'], 'profile_metadata': docs['profile'], 'captured_images': tuple(images)}


def _journal_projection(image, head, member, receipts, *, specs):
    """Validate the captured full chain; freeze only member finish links and original pins."""
    _require(type(image) is _PinnedImage and type(image.raw) is bytes, 'Expected captured journal bytes')
    _require(hashlib.sha256(image.raw).hexdigest() == _hash(image.sha256), 'Captured journal SHA-256 differs')
    _fields(head, ('sequence', 'journal_sha256', 'plan_sha256'))
    _positive_integer(head['sequence']); _hash(head['journal_sha256']); _hash(head['plan_sha256'])
    _positive_integer(member)
    _fields(receipts, _STAGES)
    _fields(specs, _STAGES)
    for ref in (*receipts.values(), *specs.values()):
        _reference_shape(ref)
    _require(image.raw and image.raw.endswith(b'\n'), 'Journal is empty or truncated')
    pending, finished, selected = {}, set(), {}
    tip = '0' * 64
    lines = image.raw.splitlines()
    for sequence, line in enumerate(lines, 1):
        record = _json_bytes(line)
        _fields(record, ('sequence', 'previous_hash', 'plan_sha256', 'kind', 'member', 'stage', 'data'))
        _require(type(record['sequence']) is int and record['sequence'] == sequence
                 and record['previous_hash'] == tip and record['plan_sha256'] == head['plan_sha256'],
                 'Journal chain, sequence or plan differs')
        _positive_integer(record['member'])
        _require(type(record['stage']) is str and record['stage'] in _STAGES
                 and type(record['kind']) is str and record['kind'] in ('start', 'finish'),
                 'Journal contains an unsupported or non-complete stage')
        key = (record['member'], record['stage'])
        data = record['data']
        line_pin = hashlib.sha256(line).hexdigest()
        if record['kind'] == 'start':
            _fields(data, ('spec',)); _reference_shape(data['spec'])
            if record['member'] == member:
                _require(data['spec'] == specs[record['stage']], 'Journal start spec differs from receipt spec')
            _require(key not in pending and key not in finished and not pending,
                     'Journal stage is duplicate or concurrent')
            next_stage = sum(1 for period, _ in finished if period == record['member'])
            _require(next_stage < len(_STAGES) and record['stage'] == _STAGES[next_stage],
                     'Journal stage order differs from pipeline protocol')
            pending[key] = (sequence, data['spec'])
        else:
            _fields(data, ('start_sequence', 'receipt')); _reference_shape(data['receipt'])
            _positive_integer(data['start_sequence'])
            _require(key in pending and pending[key][0] == data['start_sequence'],
                     'Journal finish has no matching start')
            start_sequence, spec = pending.pop(key)
            finished.add(key)
            if record['member'] == member:
                _require(data['receipt'] == receipts[record['stage']], 'Journal finish receipt differs from member')
                selected[record['stage']] = {'stage': record['stage'], 'sequence': sequence,
                                            'record_sha256': line_pin, 'start_sequence': start_sequence,
                                            'spec': spec, 'receipt': data['receipt']}
        tip = line_pin
    _require(not pending and len(lines) == head['sequence'] and tip == head['journal_sha256']
             and set(selected) == set(_STAGES), 'Journal head or complete member coverage differs')
    return {'journal': {'path': image.path, 'sha256': image.sha256, 'bytes': len(image.raw)},
            'head': _json_bytes(_canonical(head)), 'member': member,
            'finishes': [selected[stage] for stage in _STAGES]}


_PIPELINE57_JOURNAL = {'path': _PIPELINE57_ROOT + 'execution/journal.jsonl',
                       'sha256': 'b14d7051fc54dd95b3f10743fdf1f688ae15335beb30c7e94086532f6bb25c7d'}


def _validate_pipeline_gate(root, gate):
    _handoff_shape(gate)
    proof = gate['proof']
    _require(proof['kind'] == 'pipeline57_v1' and proof['plan'] == _PIPELINE57_PLAN
             and proof['result'] == _PIPELINE57_RESULT and proof['head'] == _PIPELINE57_HEAD,
             'Wrong pipeline57 authority pin')
    images = []
    def capture(ref):
        image = _read_reference(root, ref); images.append(image)
        return image.document()
    plan, result, head = (capture(proof[key]) for key in ('plan', 'result', 'head'))
    _require(result.get('contract') == 'ifdata-financial-sanitization-result-v1' and result.get('status') == 'complete'
             and result.get('plan') == proof['plan'] and result.get('head') == head
             and head.get('plan_sha256') == proof['plan']['sha256'], 'Pipeline result/head differs')
    selected = [m for m in plan['members'] if m['selection'] == gate['selection']]
    completed = [m for m in result['members'] if m['selection'] == gate['selection']]
    _require(len(selected) == len(completed) == 1, 'Pipeline member is missing or duplicated')
    member, state = selected[0], completed[0]
    _require(state['state'] == 'replay_verified' and state['terminal_state'] is None
             and state['incomplete_stage'] is None and state['errors'] == []
             and all(state['milestones'][key] is True for key in ('admitted', 'parquet_verified', 'query_verified', 'replay_verified')),
             'Pipeline member lacks complete milestones')
    _require([proof['receipts'][s] for s in _STAGES] == state['receipts'], 'Pipeline receipt/member bindings differ')
    outputs, spec_refs = {}, {}
    for stage in _STAGES:
        receipt = capture(proof['receipts'][stage])
        _require(receipt.get('contract') == 'ifdata-financial-sanitization-stage-receipt-v1'
                 and receipt.get('status') == 'complete' and receipt.get('document') == proof['plan']
                 and receipt['measurement']['tree_extinct'] is True
                 and receipt['measurement']['deadline_reached'] is False and not receipt['measurement']['guard'],
                 'Pipeline receipt incomplete or resource guard failed')
        spec, execution = capture(receipt['spec']), capture(receipt['result'])
        spec_refs[stage] = receipt['spec']
        capture(receipt['identity']); capture(receipt['log'])
        for record in (spec, execution):
            _require(record['document'] == proof['plan'] and record['member'] == gate['selection']['period']
                     and record['stage'] == stage, 'Pipeline stage identity differs')
        _require(execution['status'] == receipt['status'] and execution['outputs'] == receipt['outputs']
                 and execution['artifacts'] == receipt['artifacts'] and execution['summary'] == receipt['summary'],
                 'Pipeline stage receipt/result differs')
        _require(set(receipt['outputs']) == {stage}, 'Pipeline stage outputs differ')
        outputs[stage] = receipt['outputs'][stage]
    _require(gate['admission'] == outputs['admit'] and gate['parquet'] == outputs['convert'], 'Pipeline handoff outputs differ')
    expected_profile = {'path': 'bank_quality/' + member['installed_profile_path'],
                        'sha256': member['profile']['sha256'], 'hash_policy': 'installed_profile_native_lf'}
    _require(gate['profile'] == expected_profile, 'Pipeline installed profile reference differs')
    profile = _native_profile_image(root, gate['profile']); images.append(profile)
    profile_doc = profile.document()
    _require(profile_doc['selection'] == gate['selection'], 'Pipeline profile selection differs')
    handoff = capture(member['final_handoff'])
    docs = {stage: capture(image) for stage, image in outputs.items()}
    for prefix in ('', 'replay-'):
        admission, parquet, query = (docs[prefix + stage] for stage in ('admit', 'convert', 'query'))
        _projection_links(admission, parquet, outputs[prefix + 'admit'], gate['selection'], gate['profile']['sha256'])
        _require(admission['input_index_sha256'] == member['final_handoff']['sha256']
                 and handoff['selection'] == gate['selection'], 'Pipeline source-index lineage differs')
        _fields(query, ('bindings', 'cadaster_columns', 'cadaster_records', 'cells', 'manifest_sha256', 'numeric_rows',
                        'observations', 'precision_encodings', 'presence_counts', 'query_verified',
                        'source_manifest_sha256', 'value_state_counts'))
        _require(query['query_verified'] is True and query['manifest_sha256'] == outputs[prefix + 'convert']['sha256']
                 and query['source_manifest_sha256'] == outputs[prefix + 'admit']['sha256'], 'Pipeline query links differ')
        for field in ('cells', 'observations', 'cadaster_records', 'presence_counts', 'value_state_counts'):
            _require(query[field] == parquet[field], 'Pipeline query counts differ')
        bindings = parquet['numeric_bindings']
        _require(query['bindings'] == len(bindings) and query['numeric_rows'] == len(bindings) * parquet['cadaster_records']
                 and query['cadaster_columns'] == len(profile_doc['cadaster_columns']), 'Pipeline accessor coverage differs')
    comparison = docs['compare']
    _fields(comparison, ('admission_files', 'parquet_files', 'primary_admission', 'primary_parquet',
                         'replay_admission', 'replay_parquet', 'replay_verified'))
    _require(comparison['replay_verified'] is True and comparison['primary_admission'] == outputs['admit']
             and comparison['primary_parquet'] == outputs['convert'] and comparison['replay_admission'] == outputs['replay-admit']
             and comparison['replay_parquet'] == outputs['replay-convert'], 'Pipeline comparison links differ')
    # Capture the original journal under its finite external pin before freezing a projection.
    journal = _read_reference(root, _PIPELINE57_JOURNAL, json_required=False)
    journal_authority = _journal_projection(journal, head, gate['selection']['period'], proof['receipts'],
                                            specs=spec_refs)
    images.append(journal)
    # Also retain the existing read-only API's full protocol/status checks.
    _require(Path(root).resolve() == Path(__file__).resolve().parents[1], 'Pipeline status requires the authorized checkout')
    from .financial_pipeline import read_status
    try:
        status = read_status(_contained_path(root, proof['plan']['path']), plan_sha256=proof['plan']['sha256'])
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise CatalogError('integrity', 'Pipeline journal/status cannot be authenticated') from exc
    current = [m for m in status['members'] if m['selection'] == gate['selection']]
    _require(status['status'] == 'complete' and len(current) == 1 and current[0]['receipts'] == state['receipts']
             and current[0]['state'] == 'replay_verified', 'Pipeline journal/status differs')
    return {'acceptance': 'verified', 'historical_stages': {'state': 'available', 'kind': proof['kind']},
            'parquet_metadata': docs['convert'], 'profile_metadata': profile_doc,
            'journal_authority': journal_authority, 'captured_images': tuple(images)}


_CHECKOUT_ROOT = Path(__file__).resolve().parents[1]
_COUNT_FIELDS = ('cells', 'observations', 'cadaster_records', 'presence_counts', 'value_state_counts')
_CATALOG_CONTEXTS = weakref.WeakKeyDictionary()


@dataclass(frozen=True, eq=False)
class Catalog:
    path: Path
    sha256: str


@dataclass(frozen=True)
class _CatalogState:
    root: Path
    raw: bytes
    images: tuple


def _context(catalog):
    _require(type(catalog) is Catalog and catalog in _CATALOG_CONTEXTS,
             'Expected an authenticated catalog context produced by load_catalog')
    return _CATALOG_CONTEXTS[catalog]


def _checkout_path(root, path):
    try:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = Path(root) / candidate
        relative = candidate.absolute().relative_to(Path(root).absolute()).as_posix()
    except (TypeError, ValueError, OSError) as exc:
        raise CatalogError('integrity', 'Catalog path is outside its fixed checkout') from exc
    return _contained_path(root, relative), relative


def _catalog_destination(root, path):
    destination, relative = _checkout_path(root, path)
    parts = PurePosixPath(relative).parts
    _require(len(parts) == 3 and parts[:2] == ('data', 'runs')
             and parts[2].startswith('financial-catalog-') and len(parts[2]) > len('financial-catalog-'),
             'Catalog destination must be a new financial-catalog run')
    return destination, relative


def _coverage(entries):
    accepted = sum(any(r['acceptance'] == 'verified' for r in e['revisions']) for e in entries)
    return {'offered': len(entries), 'accepted': accepted, 'unavailable': len(entries) - accepted,
            'revision_count': sum(len(e['revisions']) for e in entries)}


def _counts(document):
    result = {field: document.get(field) for field in _COUNT_FIELDS}
    for field in _COUNT_FIELDS[:3]:
        _require(type(result[field]) is int and result[field] >= 0, 'Invalid financial metadata count')
    for field in _COUNT_FIELDS[3:]:
        _require(type(result[field]) is dict and all(type(k) is str and type(v) is int and v >= 0
                                                   for k, v in result[field].items()), 'Invalid native state counts')
    return result


def _encodings(document):
    bindings = document.get('numeric_bindings')
    _require(type(bindings) is list and all(type(b) is dict for b in bindings), 'Invalid binding metadata')
    values = [b.get('encoding', 'duckdb_decimal') for b in bindings]
    _require(all(type(e) is str and e in ('duckdb_decimal', 'decimal_text_v1') for e in values),
             'Unknown native precision encoding')
    return sorted(set(values))


def _put_image(store, name, raw):
    _require(type(raw) is bytes, 'Companion must use captured bytes')
    _require(name not in store or store[name] == raw, 'Conflicting frozen companion')
    store[name] = raw
    return {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}


def _freeze_revision(gate_image, gate, verified, store):
    """Only the builder supplies the result of a finite authority parser here."""
    _require(verified['acceptance'] == 'verified', 'Unverified authority cannot produce a revision')
    images = {gate_image.path: gate_image}
    for image in verified['captured_images']:
        _require(type(image) is _PinnedImage and hashlib.sha256(image.raw).hexdigest() == image.sha256,
                 'Captured authority bytes differ from their physical pin')
        _require(image.path not in images or images[image.path] == image, 'Conflicting captured authority path')
        images[image.path] = image
    revision = gate['revision']; prefix = 'metadata/revisions/' + revision + '/'
    gate_ref = _put_image(store, prefix + 'gate.json', _canonical(gate))
    original_gate_ref = _put_image(store, prefix + 'gate-original.json', gate_image.raw)
    def freeze_manifest(name):
        original = gate[name]
        _require(original['path'] in images, 'Authority did not capture required metadata')
        image = images[original['path']]
        if name == 'profile':
            _require(hashlib.sha256(image.raw.replace(b'\r\n', b'\n')).hexdigest() == original['sha256'],
                     'Frozen native profile differs')
        else:
            _require(image.sha256 == original['sha256'], 'Frozen manifest pin differs')
        return {'original': original, 'image': _put_image(store, prefix + name + '.json', image.raw)}
    profile, admission, parquet = (freeze_manifest(name) for name in ('profile', 'admission', 'parquet'))
    counts = _counts(verified['parquet_metadata']); encodings = _encodings(verified['parquet_metadata'])
    fragment = {'contract': 'catalog-authority-fragment-v1', 'kind': gate['proof']['kind'],
                'gate_original': {'path': gate_image.path, 'sha256': gate_image.sha256},
                'gate': gate_ref, 'gate_image': original_gate_ref,
                'selection': gate['selection'], 'revision': revision, 'profile': profile,
                'admission': admission, 'parquet': parquet, 'historical_stages': verified['historical_stages'],
                'counts': counts, 'precision_encodings': encodings,
                'dependencies': [{'path': image.path, 'sha256': image.sha256, 'bytes': len(image.raw)}
                                 for image in sorted(images.values(), key=lambda image: image.path)],
                'journal': verified.get('journal_authority'), 'limitations': gate['limitations']}
    proof = _put_image(store, prefix + 'authority.json', _canonical(fragment))
    return {'revision_id': revision, 'profile': gate['profile'], 'admission': gate['admission'],
            'parquet': gate['parquet'], 'proof': proof, 'acceptance': 'verified',
            'historical_stages': verified['historical_stages'], 'counts': counts,
            'precision_encodings': encodings, 'limitations': gate['limitations']}


def _frozen_document(document, store):
    """Authenticate frozen structure and cross-links, without reopening original authority files."""
    _fields(document, ('contract', 'inputs', 'registry', 'parent_catalog', 'entries', 'coverage', 'files', 'limitations'))
    _require(document['contract'] == 'ifdata-financial-catalog-v1', 'Unsupported catalog contract')
    _require(type(document['limitations']) is list and all(type(v) is str for v in document['limitations']),
             'Invalid catalog limitations')
    used = set()
    def read(ref):
        _reference_shape(ref)
        _require(ref['path'] in store and hashlib.sha256(store[ref['path']]).hexdigest() == ref['sha256'],
                 'Frozen metadata link differs')
        used.add(ref['path'])
        return _json_bytes(store[ref['path']])
    inputs = read(document['inputs']); _catalog_inputs_shape(inputs)
    _require(document['parent_catalog'] == inputs['parent_catalog'], 'Frozen parent differs from explicit input')
    _require(document['registry']['sha256'] == inputs['registry']['sha256'], 'Frozen registry differs from pinned input')
    baseline = _registry_entries(read(document['registry']))
    incoming = {(ref['path'], ref['sha256']) for ref in inputs['gates']}
    incoming_seen, inherited_seen, inherited = set(), set(), {}
    if document['parent_catalog'] is not None:
        name = 'metadata/parent.json'
        _require(name in store, 'Parent provenance companion is missing')
        parent = read({'path': name, 'sha256': hashlib.sha256(store[name]).hexdigest()})
        _fields(parent, ('contract', 'parent_catalog', 'entries'))
        _require(parent['contract'] == 'catalog-parent-origins-v1' and parent['parent_catalog'] == document['parent_catalog']
                 and type(parent['entries']) is list, 'Frozen parent provenance differs')
        descriptors = {_selection_key(entry['selection']): entry['descriptor_sha256'] for entry in baseline}
        parent_selections = set()
        for parent_entry in parent['entries']:
            _fields(parent_entry, ('selection', 'descriptor_sha256', 'revisions'))
            key = _selection_key(parent_entry['selection'])
            _require(key in descriptors and key not in parent_selections
                     and parent_entry['descriptor_sha256'] == descriptors[key]
                     and type(parent_entry['revisions']) is list, 'Parent offer provenance differs')
            parent_selections.add(key)
            for revision in parent_entry['revisions']:
                _fields(revision, ('revision_id', 'proof', 'gate_original'))
                _hash(revision['revision_id']); _reference_shape(revision['proof']); _reference_shape(revision['gate_original'])
                origin_key = (key, revision['revision_id'])
                _require(origin_key not in inherited, 'Duplicate inherited revision origin')
                inherited[origin_key] = revision
    entries = document['entries']
    _require(type(entries) is list and len(entries) == len(baseline), 'Catalog offer inventory differs')
    revision_pins = set()
    for entry, offer in zip(entries, baseline):
        _fields(entry, ('selection', 'descriptor_sha256', 'reports', 'revisions', 'active_revision', 'limitations'))
        for field in ('selection', 'descriptor_sha256', 'reports'):
            _require(entry[field] == offer[field], 'Frozen offer differs from its native registry')
        _require(type(entry['limitations']) is list and all(type(v) is str for v in entry['limitations'])
                 and type(entry['revisions']) is list, 'Invalid entry metadata')
        local_pins = []
        for revision in entry['revisions']:
            _fields(revision, ('revision_id', 'profile', 'admission', 'parquet', 'proof', 'acceptance',
                              'historical_stages', 'counts', 'precision_encodings', 'limitations'))
            pin = _hash(revision['revision_id'])
            _require(pin not in revision_pins and revision['acceptance'] == 'verified', 'Duplicate or unverified revision')
            revision_pins.add(pin); local_pins.append(pin)
            fragment = read(revision['proof'])
            _fields(fragment, ('contract', 'kind', 'gate_original', 'gate', 'gate_image', 'selection', 'revision', 'profile',
                               'admission', 'parquet', 'historical_stages', 'counts', 'precision_encodings',
                               'dependencies', 'journal', 'limitations'))
            _require(fragment['contract'] == 'catalog-authority-fragment-v1', 'Unsupported frozen authority')
            _reference_shape(fragment['gate_original'])
            original = (fragment['gate_original']['path'], fragment['gate_original']['sha256'])
            origin_key = (_selection_key(entry['selection']), pin)
            if original in incoming:
                _require(origin_key not in inherited and original not in incoming_seen, 'Duplicate new gate origin')
                incoming_seen.add(original)
            else:
                _require(origin_key in inherited and inherited[origin_key]['proof'] == revision['proof']
                         and inherited[origin_key]['gate_original'] == fragment['gate_original'],
                         'Frozen gate origin is neither a pinned input nor an inherited parent revision')
                inherited_seen.add(origin_key)
            gate = read(fragment['gate']); _handoff_shape(gate)
            original_gate = read(fragment['gate_image'])
            _require(fragment['gate_image']['sha256'] == fragment['gate_original']['sha256']
                     and original_gate == gate and store[fragment['gate']['path']] == _canonical(original_gate),
                     'Frozen canonical gate differs from its captured original')
            _require(fragment['kind'] == gate['proof']['kind'] and fragment['selection'] == entry['selection'] == gate['selection']
                     and fragment['revision'] == pin == gate['revision'], 'Frozen authority selection/revision differs')
            kind, period = fragment['kind'], gate['selection']['period']
            if kind == 'installed_historical_anchor_v1':
                _require(period in (202312, 202412, 202503) and gate['proof']['trusted_base_sha'] == _TRUSTED_BASE
                         and gate['proof']['transport']['sha256'] == _TRANSPORT_PIN
                         and fragment['historical_stages'] == gate['proof']['stage_evidence'],
                         'Frozen historical authority differs')
                _require(fragment['journal'] is None, 'Historical authority cannot invent a pipeline journal')
            elif kind == 'accepted_supplement403_v1':
                _require(period == 202403 and gate['proof']['supplement'] == _SUPPLEMENT403
                         and fragment['journal'] is None, 'Frozen supplement authority differs')
            else:
                _require(period in (202406, 202409, 202506, 202509, 202512, 202603, 202606)
                         and all(gate['proof'][k] == ref for k, ref in
                                 (('plan', _PIPELINE57_PLAN), ('result', _PIPELINE57_RESULT), ('head', _PIPELINE57_HEAD))),
                         'Frozen pipeline57 authority differs')
                journal = fragment['journal']
                _fields(journal, ('journal', 'head', 'member', 'finishes'))
                _fields(journal['journal'], ('path', 'sha256', 'bytes'))
                _require({k: journal['journal'][k] for k in ('path', 'sha256')} == _PIPELINE57_JOURNAL
                         and type(journal['journal']['bytes']) is int and journal['journal']['bytes'] > 0,
                         'Frozen original journal pin differs')
                _fields(journal['head'], ('sequence', 'journal_sha256', 'plan_sha256'))
                _require(type(journal['head']['sequence']) is int and journal['head']['sequence'] == 98
                         and journal['head']['plan_sha256'] == _PIPELINE57_PLAN['sha256']
                         and type(journal['member']) is int and journal['member'] == period,
                         'Frozen journal head/member differs')
                _hash(journal['head']['journal_sha256'])
                _require(type(journal['finishes']) is list and len(journal['finishes']) == len(_STAGES),
                         'Frozen member lacks seven finishes')
                last = 0
                for stage, finish in zip(_STAGES, journal['finishes']):
                    _fields(finish, ('stage', 'sequence', 'record_sha256', 'start_sequence', 'spec', 'receipt'))
                    _positive_integer(finish['sequence']); _positive_integer(finish['start_sequence'])
                    _hash(finish['record_sha256']); _reference_shape(finish['spec']); _reference_shape(finish['receipt'])
                    _require(finish['stage'] == stage and last < finish['start_sequence'] < finish['sequence'] <= 98
                             and finish['receipt'] == gate['proof']['receipts'][stage], 'Frozen stage links/order differ')
                    last = finish['sequence']
            if kind != 'installed_historical_anchor_v1':
                _require(fragment['historical_stages'] == {'state': 'available', 'kind': kind},
                         'Frozen stage availability differs')
            for field in ('profile', 'admission', 'parquet'):
                _fields(fragment[field], ('original', 'image'))
                _require(fragment[field]['original'] == gate[field] == revision[field], 'Frozen original reference differs')
            profile = read(fragment['profile']['image'])
            _require(profile.get('selection') == gate['selection']
                     and hashlib.sha256(store[fragment['profile']['image']['path']].replace(b'\r\n', b'\n')).hexdigest()
                     == gate['profile']['sha256'], 'Frozen profile selection/native pin differs')
            admission, parquet = (read(fragment[field]['image']) for field in ('admission', 'parquet'))
            for field in ('admission', 'parquet'):
                _require(fragment[field]['image']['sha256'] == gate[field]['sha256'], 'Frozen physical manifest differs')
            _projection_links(admission, parquet, gate['admission'], gate['selection'], gate['profile']['sha256'])
            _require(gate['parquet']['sha256'] == pin, 'Frozen Parquet revision differs')
            for field, expected in (('counts', _counts(parquet)), ('precision_encodings', _encodings(parquet)),
                                    ('historical_stages', fragment['historical_stages']), ('limitations', gate['limitations'])):
                _require(fragment[field] == revision[field] == expected, 'Frozen revision metadata differs')
            dependencies = fragment['dependencies']
            _require(type(dependencies) is list, 'Invalid authority dependency inventory')
            seen = set()
            for dep in dependencies:
                _fields(dep, ('path', 'sha256', 'bytes')); _reference_shape({k: dep[k] for k in ('path', 'sha256')})
                _require(type(dep['bytes']) is int and dep['bytes'] >= 0 and dep['path'] not in seen,
                         'Duplicate or invalid authority dependency')
                seen.add(dep['path'])
            _require([d['path'] for d in dependencies] == sorted(seen), 'Authority dependencies are not deterministic')
            by_path = {dep['path']: dep for dep in dependencies}
            required = [fragment['gate_original'], gate['admission'], gate['parquet'],
                        {'path': gate['profile']['path'], 'sha256': fragment['profile']['image']['sha256']}]
            proof = gate['proof']
            if kind == 'installed_historical_anchor_v1':
                required.extend(proof[field] for field in ('trusted_code', 'transport', 'ledger', 'replay_admission', 'replay_parquet'))
                if proof['stage_evidence']['state'] == 'available':
                    required.extend(proof['stage_evidence'][field] for field in ('query', 'replay_query', 'compare'))
            elif kind == 'accepted_supplement403_v1':
                required.append(proof['supplement'])
            else:
                required.extend(proof[field] for field in ('plan', 'result', 'head'))
                required.extend(proof['receipts'].values())
                required.append(_PIPELINE57_JOURNAL)
                required.extend(finish['spec'] for finish in fragment['journal']['finishes'])
            for ref in required:
                _require(ref['path'] in by_path and by_path[ref['path']]['sha256'] == ref['sha256']
                         and by_path[ref['path']]['bytes'] > 0, 'Frozen authority dependency link is missing or differs')
            for field in ('profile', 'admission', 'parquet'):
                _require(by_path[gate[field]['path']]['bytes'] == len(store[fragment[field]['image']['path']]),
                         'Frozen physical dependency byte count differs')
            _require(by_path[fragment['gate_original']['path']]['bytes'] == len(store[fragment['gate_image']['path']]),
                     'Frozen original gate byte count differs')
            if kind == 'pipeline57_v1':
                _require(by_path[_PIPELINE57_JOURNAL['path']]['bytes'] == fragment['journal']['journal']['bytes'],
                         'Frozen journal dependency byte count differs')
        _require(local_pins == sorted(local_pins), 'Catalog revisions are not ordered')
        if entry['active_revision'] is not None:
            _require(_hash(entry['active_revision']) in local_pins, 'Active catalog revision is absent')
    choices_checked = _json_bytes(_canonical(entries))
    _apply_active_revisions(choices_checked, inputs['active_revisions'])
    _require(all(original['active_revision'] == checked['active_revision']
                 for original, checked in zip(entries, choices_checked)), 'Catalog active choice differs from explicit input')
    _fields(document['coverage'], ('offered', 'accepted', 'unavailable', 'revision_count'))
    _require(all(type(v) is int and v >= 0 for v in document['coverage'].values())
             and document['coverage'] == _coverage(entries), 'Catalog coverage differs from verified revisions')
    _require(incoming_seen == incoming and inherited_seen == set(inherited), 'Catalog dropped a new or inherited accepted gate')
    _require(used == set(store), 'Catalog has unreferenced companions')


def _prepare_catalog(inputs_path: Path, destination: Path, *, inputs_sha256: str) -> dict:
    root = _CHECKOUT_ROOT
    output, output_name = _catalog_destination(root, destination)
    _require(not output.exists(), 'Catalog output already exists')
    _, input_name = _checkout_path(root, inputs_path)
    image = _read_reference(root, {'path': input_name, 'sha256': inputs_sha256})
    inputs = image.document(); _catalog_inputs_shape(inputs)
    registry = _read_reference(root, inputs['registry']); entries = _registry_entries(registry.document())
    store = {}
    input_ref = _put_image(store, 'metadata/inputs.json', image.raw)
    registry_ref = _put_image(store, 'metadata/registry.json', registry.raw)
    by_selection = {_selection_key(entry['selection']): entry for entry in entries}
    if inputs['parent_catalog'] is not None:
        parent_ref = inputs['parent_catalog']
        parent = load_catalog(_contained_path(root, parent_ref['path']), catalog_sha256=parent_ref['sha256'])
        state = _context(parent)
        parent_origins = []
        parent_images = {companion.path: companion.raw for companion in state.images}
        for parent_entry in _json_bytes(state.raw)['entries']:
            key = _selection_key(parent_entry['selection'])
            _require(key in by_selection and by_selection[key]['descriptor_sha256'] == parent_entry['descriptor_sha256'],
                     'Parent offer descriptor differs; reconcile context before updating catalog')
            by_selection[key]['revisions'] = parent_entry['revisions']
            by_selection[key]['active_revision'] = parent_entry['active_revision']
            if parent_entry['revisions']:
                origins = []
                for revision in parent_entry['revisions']:
                    fragment = _json_bytes(parent_images[revision['proof']['path']])
                    origins.append({'revision_id': revision['revision_id'], 'proof': revision['proof'],
                                    'gate_original': fragment['gate_original']})
                parent_origins.append({'selection': parent_entry['selection'],
                                       'descriptor_sha256': parent_entry['descriptor_sha256'], 'revisions': origins})
        for companion in state.images:
            if companion.path not in ('metadata/inputs.json', 'metadata/registry.json', 'metadata/parent.json'):
                _put_image(store, companion.path, companion.raw)
        _put_image(store, 'metadata/parent.json', _canonical({'contract': 'catalog-parent-origins-v1',
                   'parent_catalog': parent_ref, 'entries': parent_origins}))
    validators = {'installed_historical_anchor_v1': _validate_historical_gate,
                  'accepted_supplement403_v1': _validate_supplement_gate, 'pipeline57_v1': _validate_pipeline_gate}
    for ref in sorted(inputs['gates'], key=lambda r: (r['path'], r['sha256'])):
        _require(ref['path'].startswith(('data/runs/', '.scratch/catalog61-',
                                        '.scratch/migration-snapshot-ifdata-11-20261006/')),
                 'Catalog gate is outside authorized metadata destinations')
        gate_image = _read_reference(root, ref); gate = gate_image.document(); _handoff_shape(gate)
        key = _selection_key(gate['selection']); _require(key in by_selection, 'Gate selection is not offered')
        entry = by_selection[key]
        _require(gate['admission']['path'].startswith('data/derived/')
                 and gate['parquet']['path'].startswith('data/curated/'), 'Gate manifest destination is not native')
        _require(not any(r['revision_id'] == gate['revision'] for r in entry['revisions']), 'Duplicate accepted revision')
        verified = validators[gate['proof']['kind']](root, gate)
        entry['revisions'].append(_freeze_revision(gate_image, gate, verified, store))
    for entry in entries:
        entry['revisions'].sort(key=lambda revision: revision['revision_id'])
    _apply_active_revisions(entries, inputs['active_revisions'])
    files = [{'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
             for name, raw in sorted(store.items())]
    document = {'contract': 'ifdata-financial-catalog-v1', 'inputs': input_ref, 'registry': registry_ref,
                'parent_catalog': inputs['parent_catalog'], 'entries': entries, 'coverage': _coverage(entries),
                'files': files, 'limitations': ['Historical acceptance is distinct from current payload health.',
                                               'No economic comparability or academic sample is inferred.']}
    _frozen_document(document, store)
    raw = _canonical(document)
    try:
        output.mkdir(exist_ok=False)
        for name, content in sorted(store.items()):
            path = _contained_path(output, name); path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(content); stream.flush(); os.fsync(stream.fileno())
        # Completion marker last. Failure preserves an unaccepted directory for diagnosis.
        with (output / 'catalog.json').open('xb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    except OSError as exc:
        raise CatalogError('integrity', 'Catalog publication failed; partial destination is not accepted') from exc
    return {'catalog': {'path': output_name + '/catalog.json', 'sha256': hashlib.sha256(raw).hexdigest()},
            'coverage': document['coverage']}


def prepare_catalog(inputs_path: Path, destination: Path, *, inputs_sha256: str) -> dict:
    with _capture_scope():
        return _prepare_catalog(inputs_path, destination, inputs_sha256=inputs_sha256)


def load_catalog(path: Path, *, catalog_sha256: str) -> Catalog:
    root = _CHECKOUT_ROOT
    target, name = _checkout_path(root, path)
    _require(target.name == 'catalog.json', 'Expected catalog completion marker')
    _catalog_destination(root, target.parent)
    image = _read_reference(root, {'path': name, 'sha256': catalog_sha256})
    document = image.document()
    _require(type(document) is dict and type(document.get('files')) is list, 'Invalid catalog companion inventory')
    store, images = {}, []
    for ref in document['files']:
        _fields(ref, ('path', 'bytes', 'sha256'))
        _reference_shape({k: ref[k] for k in ('path', 'sha256')})
        _require(type(ref['bytes']) is int and 0 <= ref['bytes'] <= _MAX_METADATA_BYTES,
                 'Invalid companion byte count')
        _require(ref['path'] not in store and ref['path'].startswith('metadata/'), 'Duplicate or foreign companion path')
        companion = _read_reference(target.parent, {k: ref[k] for k in ('path', 'sha256')})
        _require(len(companion.raw) == ref['bytes'], 'Companion byte count differs')
        store[companion.path] = companion.raw; images.append(companion)
    _require([r['path'] for r in document['files']] == sorted(store), 'Companion inventory is not ordered')
    expected_files = set(store) | {'catalog.json'}
    expected_dirs = {parent.as_posix() for name in store for parent in PurePosixPath(name).parents
                     if parent.as_posix() != '.'}
    actual_files = set(); pending = [target.parent]
    try:
        while pending:
            directory = pending.pop()
            for candidate in directory.iterdir():
                relative = candidate.relative_to(target.parent).as_posix()
                checked = _contained_path(target.parent, relative)
                if checked.is_dir():
                    _require(relative in expected_dirs, 'Unexpected catalog directory')
                    pending.append(checked)
                else:
                    _require(checked.is_file(), 'Nonregular catalog artifact')
                    actual_files.add(relative)
    except OSError as exc:
        raise CatalogError('integrity', 'Catalog inventory cannot be checked') from exc
    _require(actual_files == expected_files, 'Catalog physical inventory differs')
    _frozen_document(document, store)
    context = Catalog(target, image.sha256)
    _CATALOG_CONTEXTS[context] = _CatalogState(root, image.raw, tuple(images))
    return context


def discover(catalog: Catalog, *, period=None, perspective=None, report_id=None) -> list[dict]:
    state = _context(catalog)
    for value in (period, perspective, report_id):
        if value is not None:
            _positive_integer(value)
    rows = []
    for entry in _json_bytes(state.raw)['entries']:
        selection = entry['selection']
        if ((period is not None and selection['period'] != period)
                or (perspective is not None and selection['perspective'] != perspective)
                or (report_id is not None and report_id not in selection['reports'])):
            continue
        verified = [r for r in entry['revisions'] if r['acceptance'] == 'verified']
        chosen = ([r for r in verified if r['revision_id'] == entry['active_revision']]
                  if entry['active_revision'] is not None else verified)
        row = {**entry, 'acceptance': 'verified' if verified else 'unavailable',
               'query_selection': ('no_accepted_revision' if not verified else
                                   'selected' if len(chosen) == 1 else 'ambiguous_revision'),
               'historical_stages': [{'revision_id': r['revision_id'], **r['historical_stages']} for r in verified],
               'counts': chosen[0]['counts'] if len(chosen) == 1 else None,
               'local_health': 'not_checked' if verified else 'unavailable',
               'payload_validation': 'not_run'}
        rows.append(row)
    return rows


def _present_file(root, relative):
    path = _contained_path(root, relative)
    try:
        info = path.stat()
    except FileNotFoundError as exc:
        raise CatalogError('missing_local_artifact', 'Required local snapshot artifact is absent') from exc
    except OSError as exc:
        raise CatalogError('integrity', 'Local snapshot artifact cannot be inspected') from exc
    _require(stat.S_ISREG(info.st_mode), 'Local snapshot artifact is not a regular file')
    return path, info


def _current_registry(root):
    relative = 'bank_quality/financial-reports-registry.json'
    path, _ = _present_file(root, relative)
    try:
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            _require(stat.S_ISREG(opened.st_mode) and opened.st_size <= _MAX_METADATA_BYTES,
                     'Current registry exceeds its metadata boundary')
            raw = stream.read(_MAX_METADATA_BYTES + 1)
        _require(len(raw) <= _MAX_METADATA_BYTES and os.path.samestat(opened, _contained_path(root, relative).stat()),
                 'Current registry changed identity during capture')
    except OSError as exc:
        raise CatalogError('integrity', 'Current registry cannot be captured') from exc
    value = _json_bytes(raw)
    return value, _registry_entries(value), hashlib.sha256(raw).hexdigest()


def resolve_snapshot(catalog: Catalog, *, period: int, perspective: int,
                     report_id: int | None = None, revision_id: str | None = None) -> dict:
    """Resolve one accepted revision and inspect local metadata, without opening payloads."""
    state = _context(catalog)
    _positive_integer(period); _positive_integer(perspective)
    if report_id is not None:
        _positive_integer(report_id)
    if revision_id is not None:
        _hash(revision_id)
    rows = discover(catalog, period=period, perspective=perspective, report_id=report_id)
    if len(rows) != 1:
        raise CatalogError('unknown_selection', 'Selection or native report is not offered')
    entry = rows[0]
    verified = [r for r in entry['revisions'] if r['acceptance'] == 'verified']
    if not verified:
        raise CatalogError('unavailable', 'Offered selection has no accepted revision')
    choice = revision_id if revision_id is not None else entry['active_revision']
    candidates = [r for r in verified if choice is None or r['revision_id'] == choice]
    if not candidates:
        raise CatalogError('unknown_selection', 'Requested revision is not accepted for this selection')
    if len(candidates) != 1:
        raise CatalogError('ambiguous_revision', 'Selection requires an explicit accepted revision')
    revision = candidates[0]
    registry, current_entries, registry_pin = _current_registry(state.root)
    current = next((e for e in current_entries if e['selection'] == entry['selection']), None)
    member = next((m for m in registry['members'] if m['selection'] == entry['selection']), None)
    if (current is None or member is None or current['descriptor_sha256'] != entry['descriptor_sha256']
            or current['reports'] != entry['reports']
            or member['profile_path'] != revision['profile']['path'].removeprefix('bank_quality/')
            or member['profile_sha256'] != revision['profile']['sha256']):
        raise CatalogError('stale_context', 'Installed selection or profile differs from the frozen catalog')
    _present_file(state.root, revision['profile']['path'])
    try:
        _native_profile_image(state.root, revision['profile'])
    except CatalogError as exc:
        raise CatalogError('stale_context', 'Installed native profile differs from its accepted pin') from exc
    manifest_ref = revision['parquet']
    target, _ = _present_file(state.root, manifest_ref['path'])
    manifest = _read_reference(state.root, manifest_ref).document()
    _require(manifest.get('selection') == entry['selection'] and manifest.get('accepted') is True
             and manifest.get('profile_sha256') == revision['profile']['sha256'],
             'Snapshot manifest differs from the accepted selection/profile')
    _require(type(manifest.get('files')) is list, 'Snapshot file inventory is absent')
    files = set()
    for ref in manifest['files']:
        _fields(ref, ('path', 'bytes', 'sha256'))
        _reference_shape({k: ref[k] for k in ('path', 'sha256')})
        _require(type(ref['bytes']) is int and ref['bytes'] >= 0 and ref['path'] not in files,
                 'Invalid snapshot file inventory')
        _require(ref['path'].startswith(('metadata/', 'parts/')), 'Foreign snapshot file role')
        files.add(ref['path'])
        _, info = _present_file(target.parent, ref['path'])
        _require(info.st_size == ref['bytes'], 'Snapshot file size differs from its pinned inventory')
        if ref['path'].startswith('metadata/'):
            image = _read_reference(target.parent, {k: ref[k] for k in ('path', 'sha256')}, json_required=False)
            _require(len(image.raw) == ref['bytes'], 'Snapshot metadata byte count differs')
    expected_dirs = {parent.as_posix() for name in files for parent in PurePosixPath(name).parents
                     if parent.as_posix() != '.'}
    actual = set(); pending = [target.parent]
    try:
        while pending:
            directory = pending.pop()
            for candidate in directory.iterdir():
                relative = candidate.relative_to(target.parent).as_posix()
                checked = _contained_path(target.parent, relative)
                if checked.is_dir():
                    _require(relative in expected_dirs, 'Unexpected snapshot directory')
                    pending.append(checked)
                else:
                    _require(checked.is_file(), 'Nonregular snapshot artifact')
                    actual.add(relative)
    except OSError as exc:
        raise CatalogError('integrity', 'Snapshot inventory cannot be inspected') from exc
    _require(actual == files | {'manifest.json'}, 'Snapshot physical inventory differs')
    return {'selection': entry['selection'], 'revision_id': revision['revision_id'],
            'report_id': report_id, 'destination': target.parent, 'manifest_sha256': manifest_ref['sha256'],
            'profile': revision['profile'], 'acceptance': 'verified',
            'current_registry_sha256': registry_pin,
            'registry_drift': registry_pin != _json_bytes(state.raw)['registry']['sha256'],
            'historical_stages': revision['historical_stages'], 'counts': revision['counts'],
            'local_health': 'metadata_verified', 'payload_validation': 'not_run'}


def snapshot_connection(catalog: Catalog, *, period: int, perspective: int,
                        report_id: int | None = None, revision_id: str | None = None):
    """Open the complete native snapshot; the caller owns and closes its connection."""
    resolved = resolve_snapshot(catalog, period=period, perspective=perspective,
                                report_id=report_id, revision_id=revision_id)
    from . import financial_reports_parquet as adapter
    try:
        return adapter.snapshot_connection(resolved['destination'], manifest_sha256=resolved['manifest_sha256'])
    except (ValueError, OSError) as exc:
        raise CatalogError('integrity', 'Native snapshot validation or opening failed') from exc


def iter_numeric_decimals(catalog: Catalog, *, period: int, perspective: int,
                         report_id: int, column_id: int, revision_id: str | None = None):
    """Yield exact native Decimal values lazily and close the owned iterator on abandonment."""
    _require(type(column_id) is int and column_id >= 0, 'Expected a nonnegative native column ID')
    resolved = resolve_snapshot(catalog, period=period, perspective=perspective,
                                report_id=report_id, revision_id=revision_id)
    manifest = _read_reference(resolved['destination'],
                               {'path': 'manifest.json', 'sha256': resolved['manifest_sha256']}).document()
    bindings = manifest.get('numeric_bindings')
    _require(type(bindings) is list, 'Native numeric binding inventory is absent')
    selected = [b for b in bindings if b.get('report_id') == report_id and b.get('column_id') == column_id]
    if not selected:
        raise CatalogError('unknown_binding', 'Requested native column is not a numeric leaf binding')
    _require(len(selected) == 1, 'Duplicate native numeric binding')
    from . import financial_reports_parquet as adapter
    iterator = adapter.iter_numeric_decimals(resolved['destination'],
                                             manifest_sha256=resolved['manifest_sha256'],
                                             binding_id=(report_id, column_id))
    try:
        yield from iterator
    except (ValueError, OSError) as exc:
        raise CatalogError('integrity', 'Native Decimal snapshot validation or reading failed') from exc
    finally:
        iterator.close()

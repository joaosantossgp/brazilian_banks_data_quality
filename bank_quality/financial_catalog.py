"""Financial catalog metadata boundary and finite historical anchors.

Supplement/pipeline authority, construction and querying are added in subsequent
reviewed checkpoints. Handoff shape alone never authorizes a snapshot.
"""
from dataclasses import dataclass
import ast
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat


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


def _contained_path(root, relative):
    _require(type(relative) is str and relative, 'Expected a relative metadata path')
    _require(not any(ord(c) < 32 or c in '\\:<>"|?*' for c in relative), 'Noncanonical metadata path')
    p = PurePosixPath(relative)
    _require(not p.is_absolute() and p.as_posix() == relative
             and all(part not in ('.', '..') for part in p.parts), 'Metadata path escapes its root')
    _require(all(not part.endswith((' ', '.')) and part.split('.')[0].lower() not in _RESERVED
                 for part in p.parts), 'Windows metadata path alias')
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


def _read_reference(root, reference, *, max_bytes=_MAX_METADATA_BYTES, json_required=True):
    _fields(reference, ('path', 'sha256'))
    pin = _hash(reference['sha256'])
    _positive_integer(max_bytes)
    path = _contained_path(root, reference['path'])
    try:
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
    _require(hashlib.sha256(raw).hexdigest() == pin, 'Metadata reference SHA-256 mismatch')
    if json_required:
        _json_bytes(raw)
    return _PinnedImage(reference['path'], pin, raw)


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
    _require(type(value['path']) is str and value['path'], 'Missing reference path')


def _selection_shape(selection):
    _fields(selection, ('period', 'perspective', 'reports'))
    _positive_integer(selection['period'])
    _require(_positive_integer(selection['perspective']) == 1005, 'Unsupported financial perspective')
    reports = selection['reports']
    _require(type(reports) is list and len(reports) == 4, 'Selection must contain four native reports')
    for report in reports:
        _positive_integer(report)
    _require(len(set(reports)) == len(reports), 'Duplicate native report')


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

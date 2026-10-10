"""Finite native-window draft, offline authority initialization and phase ledger.

The private draft is a candidate. Task2 must authenticate it again before any
explicit initialization. Accepted Parquet and accepted acquisition sources keep
their distinct contracts; file authentication here is not financial admission.
"""
import copy
import hashlib
import json
from pathlib import Path
import stat

from . import financial_acquisition as acquisition


_ROOT = Path(__file__).resolve().parents[1]
_SCOPE = 'financial-recent-202312-202606-v1'
_WINDOW = (202312, 202403, 202406, 202409, 202412, 202503, 202506, 202509, 202512, 202603, 202606)
_ACQUIRE = (202406, 202409, 202506, 202509, 202512, 202603, 202606)
_REUSE = (202312, 202403, 202412, 202503)
_RUN = 'data/runs/financial-historical-acquisition-202312-202606-20261005'
_POLICIES = {'attempts': 2, 'metadata_body_bytes': 5 * 1024 * 1024,
             'numeric_body_bytes': 64 * 1024 * 1024, 'timeout_seconds': 30,
             'deadline_seconds': 120, 'max_backoff_seconds': 5, 'max_backoffs': 7,
             'attempt_seconds': 1680, 'backoff_seconds': 35, 'scheduling_seconds': 1715,
             'max_failed_targets': 3, 'max_guard_streak': 2}
_CAPS = {'per_member': {'attempts': 14, 'body_bytes': 330 * 1024 * 1024, 'scheduling_seconds': 1715},
         'total': {'attempts': 98, 'body_bytes': 2310 * 1024 * 1024, 'scheduling_seconds': 12005}}
_require = acquisition._require
_canonical = acquisition._canonical
_sha = acquisition._sha
_json = acquisition._json



def _reference(path, pin):
    return {'path': path, 'sha256': pin}


# Physical accepted manifests are authority, rather than caller-provided hashes.
# Additional pinned refs are read-only lineage; they cannot install a new profile.
_TRUSTED_REUSE = {}
for _period, _snapshot, _manifest_pin, _admission, _source_pin, _profile, _profile_file_pin, _profile_pin, _index, _index_pin in (
    (202312, 'financial-historical-202312-20261004',
     'facbc0b6a1d06c10879caa6744e9bb573b29b827dd81d45753477b12ca45d8e6',
     'financial-historical-202312-20261004', 'ff8ac90885cf4fe65db9bc611eced3fde6084c23fed124b8616e285d01f3863a',
     'financial-reports-profiles/202312.json', 'a1c5b859b62729934e65478133050c77a1832d500ad334199f910fc40903f1e7',
     '3dd39242b3e555809a369d57789b8fee15d0410561ea03fcccf7bba80a852435',
     'data/runs/financial-historical-admission-202312-20261004/checkpoint-b.json',
     '7305bf01dc2af403d71a86cca49adfa9203e6118b5faf34881c5d934182f68e7'),
    (202412, 'financial-four-reports-202412-20261004-run2',
     'c9d58a9a6cd105fa1b73b711ba167e6a8909e56e695f16e414e96e6e0e14cd41',
     'financial-four-reports-202412-20261004', '1ba10d6b124645199d9f838c4494696a2d5fb09d0540a124ebd0ca41abfb30bc',
     'financial-reports-profile-202412.json', 'b0c3bf4911ba3919aaacc3ed3cd68b3773c8ce616b16dde8de9b6413ef87f9f8',
     'e2423c9299caae81b02c7c95c6a57903457bb90fadccfe50f50f2e62b28c35ab',
     '.superpowers/sdd/financial-four-reports-implementation-20261004/source-index.json',
     '32daa773024935273660b0ff1af0513173304aed3e21c2fd4da25cea8869a085'),
    (202503, 'financial-four-reports-202503-20261004-run2',
     '64d09fbaf7a40ff279cfc23e3fc002b671979585b22425c561af9138af013d6e',
     'financial-four-reports-202503-20261004', 'b9df726f6e137cbf35d994d0733867412c80f3bcfcad092a99591130d3e755f5',
     'financial-reports-profile-202503.json', '2d282e5f469e8d8eddb54e5ad6e0e2e9d15568715d03f12e13310f376a57ef62',
     'fc8a3007d656af499c762b1128743e24b30c843d523d99a15106d399c4e09ded',
     '.superpowers/sdd/financial-four-reports-202503-20261004/source-index-real.json',
     'd32a599662663982dc848d12fe658fa50b3cc1a67b7b5bb80d5576786eb295e1'),
):
    _TRUSTED_REUSE[_period] = {
        'entry': {'period': _period, 'kind': 'accepted_parquet',
                  'manifest_path': f'data/curated/{_snapshot}/manifest.json', 'manifest_sha256': _manifest_pin,
                  'evidence': {'admission': _reference(f'data/derived/{_admission}/manifest.json', _source_pin),
                               'profile': _reference('bank_quality/' + _profile, _profile_file_pin),
                               'source_index': _reference(_index, _index_pin)}},
        'contract': ('ifdata-financial-reports-historical-parquet-v2' if _period == 202312
                     else f'ifdata-financial-reports-parquet-{_period}-v1'),
        'source_contract': ('ifdata-financial-reports-historical-snapshot-v1' if _period == 202312
                            else f'ifdata-financial-reports-snapshot-{_period}-v1'),
        'profile_sha256': _profile_pin, 'source_manifest_sha256': _source_pin}
_SOURCE403 = 'data/runs/financial-historical-acquisition-202403-20261004/'
_TRUSTED_REUSE[202403] = {'entry': {
    'period': 202403, 'kind': 'accepted_sources', 'manifest_path': _SOURCE403 + 'preparation/job.json',
    'manifest_sha256': '43f775d20a4dd9cf686f975c2232a39b26a3f9afb23ff9732e920c5bb9296ed5',
    'evidence': {
        'job_sha256': 'b16a582e865f6de1f097820f67fa9b063b5be9fe5ddf0be8dc617415f864c4de',
        'bootstrap_sha256': '026d372570fff21a53d3b59fbf9acf1a164adb377e810811965d80e3251a5a9c',
        'receipt': _reference(_SOURCE403 + 'values-real-01/receipt.json',
                              '9f380fb46aa7455b5156e739c885d2c5041a12a13c22c22f36229e69ecfaf429'),
        'metadata_receipt': _reference(_SOURCE403 + 'metadata-real-01/receipt.json',
                                       '3357ff2d3719a2a4c51f61d299947adf856e949124afb83f3c7c5f06b6994536'),
        'checkpoint_a': _reference(_SOURCE403 + 'metadata-real-01/checkpoint-a.json',
                                  '51993dc1e9e8a0edd7361b6f297566fbf5a53a0c1feb4bf90fca77a3f9c124f0'),
        'checkpoint_b': _reference(_SOURCE403 + 'values-real-01/checkpoint-b.json',
                                  'f30878c4e4cdcae135913351652a707bc0398bbde006f42a283fac8a2f009373'),
        'resolution': _reference(_SOURCE403 + 'metadata-real-01/resolution.json',
                                 '3bd8f85be78768579645579ec75b9760d94fa71a21e26fc8719ceef1d2331b21')}}}


def _same(actual, expected, message):
    # Canonical bytes distinguish bool from int and reject NaN/unknown shapes.
    _require(_canonical(actual) == _canonical(expected), message)


def _relative_name(name):
    _require(type(name) is str and name and '\\' not in name and ':' not in name
             and all(p not in ('', '.', '..') for p in name.split('/')), 'Path escape or absolute path')
    return name


def _path(name):
    """Authenticate every ancestor without resolving a symlink/reparse first."""
    _relative_name(name)
    current = _ROOT
    for part in name.split('/'):
        current = current / part
        info = current.lstat()
        _require(not stat.S_ISLNK(info.st_mode) and not (getattr(info, 'st_file_attributes', 0) & 0x400),
                 'Symlink/reparse path forbidden')
    _require(current.is_file() and current.resolve().is_relative_to(_ROOT.resolve()), 'Path escape/non-file')
    return current


def _file(path, pin, size=None):
    acquisition._digest(pin)
    _require(size is None or type(size) is int and size >= 0, 'Invalid file size')
    digest, count = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for body in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(body)
            count += len(body)
    _require(digest.hexdigest() == pin and (size is None or count == size), 'File bytes/hash mismatch: ' + path.name)


def _read(ref):
    _require(type(ref) is dict and set(ref) == {'path', 'sha256'}, 'Invalid pinned file reference')
    path = _path(ref['path'])
    raw = path.read_bytes()
    _require(_sha(raw) == acquisition._digest(ref['sha256']), 'Pinned metadata hash mismatch')
    return _json(raw)


def _files(parent, entries):
    _require(type(entries) is list and entries, 'File inventory required')
    names = set()
    for entry in entries:
        _require(type(entry) is dict and set(entry) == {'path', 'bytes', 'sha256'}
                 and type(entry['path']) is str and entry['path'] not in names
                 and type(entry['bytes']) is int and entry['bytes'] >= 0, 'Duplicate/invalid file record')
        names.add(entry['path'])
        path = _path(parent + '/' + entry['path'])
        _file(path, entry['sha256'], entry['bytes'])
    return names


def _selection(period):
    return {'period': period, 'perspective': 1005,
            'reports': [119, 107, 110, 118] if period >= 202503 else [92, 96, 101, 98]}


def _legacy_bytes(value):
    # Legacy projected provenance encodes fractional JSON lexemes as strings.
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def _original_sources(source, profile, index):
    """Check native lineage and streaming bodies, preserving legacy contracts."""
    sources, pins, members = source.get('sources'), profile.get('source_pins'), index.get('sources')
    _require(type(sources) is dict and type(pins) is dict and set(sources) == set(pins) and sources,
             'Source/profile membership mismatch')
    historical = type(members) is list
    if historical:
        _require(all(type(ref) is dict and type(ref.get('source_id')) is str for ref in members), 'Invalid source members')
        by_id = {ref['source_id']: ref for ref in members}
        _require(len(by_id) == len(members) and set(by_id) == set(sources), 'Duplicate/incomplete source members')
    else:
        _require(type(members) is dict and set(members) == set(sources), 'Source index membership mismatch')
    for sid, record in sources.items():
        _require(type(record) is dict and type(pins[sid]) is dict, 'Invalid source provenance')
        pin = pins[sid]
        if historical:
            ref = by_id[sid]
            name = ref.get('manifest_path')
            _require(record.get('manifest_path') == name and record.get('body_sha256') == pin.get('body_sha256')
                     and ref.get('body_sha256') == pin.get('body_sha256')
                     and ref.get('provenance_sha256') == pin.get('provenance_sha256'), 'Historical source pin mismatch')
            if 'projection_sha256' in pin:
                _require(_sha(_legacy_bytes(record)) == pin['projection_sha256'], 'Historical source projection mismatch')
        else:
            indexed = record.get('indexed_manifest')
            _require(type(indexed) is str and indexed.startswith('../../../data/') and members[sid] == indexed,
                     'Legacy indexed source path mismatch')
            name = indexed[len('../../../'):]
            _require(record.get('sha256') == pin.get('body_sha256'), 'Legacy source body pin mismatch')
            projection = {key: value for key, value in record.items() if key != 'indexed_manifest'}
            _require(_sha(_legacy_bytes(projection)) == pin.get('provenance_sha256'), 'Legacy source provenance mismatch')
        _require(record.get('manifest_sha256') == pin.get('manifest_sha256'), 'Source manifest cross-pin mismatch')
        path = _path(name)
        manifest = _read(_reference(name, pin['manifest_sha256']))
        _require(type(manifest) is dict and manifest.get('sha256') == pin['body_sha256'], 'Source manifest/body cross-pin mismatch')
        if historical:
            _require(_sha(_canonical(manifest)) == pin['provenance_sha256'], 'Historical source provenance mismatch')
        body_name = manifest.get('body_path')
        _require(type(body_name) is str and type(manifest.get('bytes')) is int and manifest['bytes'] >= 0,
                 'Source body path/size required')
        body_path = _path(path.parent.relative_to(_ROOT).as_posix() + '/' + body_name)
        _file(body_path, pin['body_sha256'], manifest.get('bytes'))
        if 'response_metadata_path' in manifest and manifest['response_metadata_path'] is not None:
            acquisition._response_evidence(manifest, path)


def _parquet(entry, anchor):
    manifest = _read(_reference(entry['manifest_path'], entry['manifest_sha256']))
    _require(type(manifest) is dict and manifest.get('accepted') is True
             and manifest.get('contract') == anchor['contract'], 'Wrong accepted Parquet contract')
    selection = _selection(entry['period'])
    _same(manifest.get('selection'), selection, 'Parquet selection mismatch')
    _require(manifest.get('profile_sha256') == anchor['profile_sha256']
             and manifest.get('source_manifest_sha256') == anchor['source_manifest_sha256'], 'Parquet profile/source mismatch')
    parent = entry['manifest_path'].rsplit('/', 1)[0]
    names = _files(parent, manifest.get('files'))
    _require('metadata/source-manifest.json' in names, 'Original source manifest missing')
    source = _read(_reference(parent + '/metadata/source-manifest.json', anchor['source_manifest_sha256']))
    evidence = entry['evidence']
    _same(_read(evidence['admission']), source, 'Admission differs from copied source manifest')
    _require(type(source) is dict and source.get('accepted') is True and source.get('contract') == anchor['source_contract']
             and source.get('profile_sha256') == anchor['profile_sha256'], 'Source contract/profile mismatch')
    _same(source.get('selection'), selection, 'Source selection mismatch')
    _same(source.get('files'), manifest.get('source_files'), 'Source inventory cross-pin mismatch')
    _files(evidence['admission']['path'].rsplit('/', 1)[0], source['files'])
    profile_path = _path(evidence['profile']['path'])
    profile_raw = profile_path.read_bytes()
    _require(_sha(profile_raw) == acquisition._digest(evidence['profile']['sha256']), 'Physical profile hash mismatch')
    profile_body = profile_raw.replace(b'\r\n', b'\n')
    _require(_sha(profile_body) == anchor['profile_sha256'], 'Installed profile mismatch')
    profile, index = _json(profile_body), _read(evidence['source_index'])
    _require(type(profile) is dict and type(index) is dict, 'Profile/source index must be objects')
    _same(profile.get('selection'), selection, 'Profile selection mismatch')
    _same(index.get('selection'), selection, 'Source index selection mismatch')
    _require(source.get('input_index_sha256') == evidence['source_index']['sha256'], 'Input index lineage mismatch')
    if 'final_handoff_sha256' in profile:
        _require(profile['final_handoff_sha256'] == evidence['source_index']['sha256'], 'Historical handoff pin mismatch')
    _original_sources(source, profile, index)
    return {**copy.deepcopy(entry), 'contract': manifest['contract'], 'profile_sha256': anchor['profile_sha256'],
            'source_manifest_sha256': anchor['source_manifest_sha256'], 'checked_files': len(names)}


def _sources403(entry):
    evidence = entry['evidence']
    job = _read(_reference(entry['manifest_path'], entry['manifest_sha256']))
    _same(job['descriptors'][0]['selection'], _selection(202403), 'Reuse job selection mismatch')
    checked = {}
    for name in ('receipt', 'metadata_receipt', 'checkpoint_a', 'checkpoint_b', 'resolution'):
        checked[name] = _read(evidence[name])
    authority = acquisition.verify_authority(
        _path(entry['manifest_path']), evidence['job_sha256'], bootstrap_sha256=evidence['bootstrap_sha256'],
        receipt_path=_path(evidence['receipt']['path']), receipt_sha256=evidence['receipt']['sha256'])
    metadata_authority = acquisition.verify_authority(
        _path(entry['manifest_path']), evidence['job_sha256'], bootstrap_sha256=evidence['bootstrap_sha256'],
        receipt_path=_path(evidence['metadata_receipt']['path']), receipt_sha256=evidence['metadata_receipt']['sha256'])
    _require(authority['status'] == metadata_authority['status'] == 'verified'
             and authority['pending_attempts'] == 0 and authority['failures'] == 0, 'Reuse authority incomplete/pending/failed')
    receipt_sources = checked['receipt']['state']['sources']
    metadata = {target['target_key']: receipt_sources[target['target_key']] for target in job['targets']}
    resolved = acquisition.resolve_sources(job, metadata)
    _same(checked['checkpoint_a'], resolved['checkpoints'][0], 'Checkpoint A differs from native sources')
    _same(checked['resolution'], resolved, 'Resolution differs from native dictionary')
    _same(checked['metadata_receipt']['state']['sources'], metadata, 'Metadata receipt source mismatch')
    expected_targets = {t['target_key']: t for t in job['targets'] + resolved['numeric_targets']}
    _require(set(receipt_sources) == set(expected_targets), 'Complete reuse source set mismatch')
    projection = ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'manifest_path',
                  'manifest_sha256', 'body_sha256', 'provenance_sha256')
    for key, ref in receipt_sources.items():
        acquisition._authenticated(ref, expected=expected_targets[key])
    complete = {**checked['checkpoint_a'], 'phase': 'complete',
                'checkpoint_a_sha256': evidence['checkpoint_a']['sha256'],
                'sources': sorted([{key: ref[key] for key in projection} for ref in receipt_sources.values()], key=lambda ref: ref['source_id'])}
    _same(checked['checkpoint_b'], complete, 'Checkpoint B differs from receipt/native source set')
    return {**copy.deepcopy(entry), 'contract': acquisition.SOURCES_CONTRACT, 'authority': authority,
            'not_financial_admission': True}


def _reuse(entries):
    _require(type(entries) is list and len(entries) == 4, 'Exactly four reuse entries required')
    by_period = {}
    for entry in entries:
        _require(type(entry) is dict and set(entry) == {'period', 'kind', 'manifest_path', 'manifest_sha256', 'evidence'}
                 and type(entry['period']) is int and entry['period'] in _REUSE and entry['period'] not in by_period,
                 'Invalid/duplicate reuse entry')
        anchor = _TRUSTED_REUSE[entry['period']]
        _same(entry, anchor['entry'], 'Reuse differs from trusted accepted reference')
        by_period[entry['period']] = (_sources403(entry) if entry['period'] == 202403 else _parquet(entry, anchor))
    _require(set(by_period) == set(_REUSE), 'Closed reuse set required')
    return [by_period[p] for p in _REUSE]


def _compile(refs, entries):
    catalogs = acquisition._catalogs(refs)
    descriptors = {p: acquisition._descriptor(catalogs['new' if p >= 202503 else 'old'],
                                              refs['new' if p >= 202503 else 'old'], p) for p in _WINDOW}
    members = []
    for period in _ACQUIRE:
        descriptor = descriptors[period]
        _require(len(descriptor['source_offers']) == 7, 'Seven native announced files required')
        targets = sorted((acquisition._target(offer, period) for offer in descriptor['source_offers']
                          if offer['role'] != 'numeric'), key=lambda target: target['target_key'])
        job = {'contract': acquisition.JOB_CONTRACT, 'version': 1, 'acquisition_scope': _SCOPE + '/' + str(period),
               'catalogs': copy.deepcopy(refs), 'descriptors': [descriptor], 'policies': dict(_POLICIES), 'targets': targets}
        job['job_sha256'] = acquisition._job_hash(job)
        job['executable'] = False
        members.append({'period': period, 'job': job, 'job_sha256': job['job_sha256'],
                        'session_root': _RUN + f'/members/{period}/sessions'})
    return {'contract': 'financial-acquisition-batch-draft-v1', 'scope': _SCOPE,
            'selection': {'perspective': 1005, 'reports': 'native-four', 'periods': list(_WINDOW)},
            'acquire_periods': list(_ACQUIRE), 'reuse_periods': list(_REUSE), 'catalogs': copy.deepcopy(refs),
            'members': members, 'reuse': _reuse(entries), 'policies': dict(_POLICIES),
            'caps': copy.deepcopy(_CAPS), 'executable': False}


def _prepare_batch(catalog_index: Path, catalog_index_sha256: str,
                   reuse_index: Path, reuse_index_sha256: str) -> dict:
    """Compile the fixed window offline without outputs, bootstrap or HTTP."""
    # Reuse the existing strict compiler, including source/catalog authentication.
    catalog_path = _path(Path(catalog_index).absolute().relative_to(_ROOT.absolute()).as_posix())
    job = acquisition.prepare_job(catalog_path, catalog_index_sha256, _WINDOW, limits=dict(_POLICIES))
    path = _path(Path(reuse_index).absolute().relative_to(_ROOT.absolute()).as_posix())
    _file(path, reuse_index_sha256)
    index = _json(path.read_bytes())
    _require(type(index) is dict and set(index) == {'contract', 'scope', 'entries'}
             and index['contract'] == 'financial-acquisition-batch-reuse-index-v1'
             and index['scope'] == _SCOPE, 'Invalid closed batch reuse index')
    return _compile(job['catalogs'], index['entries'])


def _verify_draft(draft: dict) -> dict:
    if type(draft) is dict and draft.get('contract') == 'financial-acquisition-batch-draft-v2':
        expected = _compile_historical(draft.get('catalogs'), draft.get('window_id'))
        _same(draft, expected, 'Historical draft differs from installed policy/window')
        return expected
    """Reconstruct trusted identity and reauthenticate every reuse; no new balance."""
    fields = {'contract', 'scope', 'selection', 'acquire_periods', 'reuse_periods', 'catalogs',
              'members', 'reuse', 'policies', 'caps', 'executable'}
    _require(type(draft) is dict and set(draft) == fields and type(draft.get('reuse')) is list,
             'Invalid draft schema')
    entry_fields = ('period', 'kind', 'manifest_path', 'manifest_sha256', 'evidence')
    _require(all(type(entry) is dict and set(entry_fields) <= set(entry) for entry in draft['reuse']), 'Invalid draft reuse')
    entries = [{key: entry[key] for key in entry_fields} for entry in draft['reuse']]
    expected = _compile(draft['catalogs'], entries)
    _same(draft, expected, 'Draft differs from reconstructed trusted identity')
    return expected

# The batch is a phase ledger, never a second attempt/budget authority.
from contextlib import contextmanager
import os
import re
import sys
import uuid

_CODE_FILES = ('bank_quality/financial_acquisition.py', 'bank_quality/archive.py',
               'bank_quality/windows_acquisition.py', 'scripts/acquire-financial.py',
               'bank_quality/financial_acquisition_batch.py')
_COUNTERS = ('attempts', 'body_bytes', 'attempt_seconds', 'backoff_seconds', 'backoffs', 'failures')
_CODE_FILES_V2 = _CODE_FILES + ('bank_quality/financial_acquisition_compat.py',)
_HISTORICAL_POLICY_SHA256 = '16949510b28c525348590a10d93fcacfe25114815c08fc0e2b5df4e98eb31663'
_HISTORICAL_POLICY_V1 = {'aggregate_caps': {'announced_targets_max': 288,
                    'attempts_max': 576,
                    'body_bytes_max': 12522094592,
                    'members': 55,
                    'scheduling_seconds_max': 70560,
                    'windows': 16},
 'batch_contract': 'financial-acquisition-batch-v2',
 'budgets': {'n2': {'attempt_seconds_max': 960,
                    'attempts_max': 8,
                    'attempts_per_target': 2,
                    'backoff_seconds_max': 20,
                    'body_bytes_max': 144703488,
                    'deadline_seconds': 120,
                    'max_backoff_seconds': 5,
                    'max_backoffs': 4,
                    'max_failed_targets': 3,
                    'max_guard_streak': 2,
                    'metadata_body_bytes_per_target': 5242880,
                    'numeric_body_bytes_per_target': 67108864,
                    'scheduling_seconds_max': 980,
                    'target_count_max': 4,
                    'timeout_seconds': 30},
             'n3': {'attempt_seconds_max': 1200,
                    'attempts_max': 10,
                    'attempts_per_target': 2,
                    'backoff_seconds_max': 25,
                    'body_bytes_max': 211812352,
                    'deadline_seconds': 120,
                    'max_backoff_seconds': 5,
                    'max_backoffs': 5,
                    'max_failed_targets': 3,
                    'max_guard_streak': 2,
                    'metadata_body_bytes_per_target': 5242880,
                    'numeric_body_bytes_per_target': 67108864,
                    'scheduling_seconds_max': 1225,
                    'target_count_max': 5,
                    'timeout_seconds': 30},
             'n4': {'attempt_seconds_max': 1440,
                    'attempts_max': 12,
                    'attempts_per_target': 2,
                    'backoff_seconds_max': 30,
                    'body_bytes_max': 278921216,
                    'deadline_seconds': 120,
                    'max_backoff_seconds': 5,
                    'max_backoffs': 6,
                    'max_failed_targets': 3,
                    'max_guard_streak': 2,
                    'metadata_body_bytes_per_target': 5242880,
                    'numeric_body_bytes_per_target': 67108864,
                    'scheduling_seconds_max': 1470,
                    'target_count_max': 6,
                    'timeout_seconds': 30},
             'n5': {'attempt_seconds_max': 1680,
                    'attempts_max': 14,
                    'attempts_per_target': 2,
                    'backoff_seconds_max': 35,
                    'body_bytes_max': 346030080,
                    'deadline_seconds': 120,
                    'max_backoff_seconds': 5,
                    'max_backoffs': 7,
                    'max_failed_targets': 3,
                    'max_guard_streak': 2,
                    'metadata_body_bytes_per_target': 5242880,
                    'numeric_body_bytes_per_target': 67108864,
                    'scheduling_seconds_max': 1715,
                    'target_count_max': 7,
                    'timeout_seconds': 30}},
 'contract': 'financial-historical-acquisition-policy-v1',
 'endpoints': {'catalog_mode': 'read-authenticated-installed-old-and-new-no-get',
               'old_catalog': {'body_sha256': '2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07',
                               'manifest_path': 'data/raw/financial-cadaster-202412-20261003/20261003T204148892567Z_catalog_metadata_202412_8f64be16714a446387225826f4cc6241.json',
                               'manifest_sha256': 'b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7',
                               'provenance_sha256': '8b134324f4830d8a293a3a3e3cad5de351f7765a9a8b63ac6bfce872b4bfceef'},
               'prefix': 'ifdata/',
               'roles': {'cadaster': 'cadastro{period}_1005.json',
                         'dictionary': 'info{period}.json',
                         'numeric': 'dados{period}_{area}.json'},
               'selected_catalog': 'old',
               'source_api': 'https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo=',
               'url_encoding': 'percent-encode-native-file-safe-empty'},
 'execution_rules': {'archive_execution_allowed': False,
                     'budget_identity_excludes': ['workers', 'machine_resources', 'session_id', 'timestamp'],
                     'destination_override_allowed': False,
                     'halt_failed_members': 3,
                     'halt_guard_streak': 2,
                     'halt_guards_immediate': ['persistence', 'containment', 'monitor_failure'],
                     'higher_concurrency': 'requires-reviewed-aggregate-monitor-and-machine-diagnostic',
                     'initial_active_windows': 1,
                     'initial_metadata_workers': 1,
                     'initial_values_workers': 1,
                     'legacy54_proof': 'read-only-installed-anchor-no-active-context-no-get',
                     'numeric_resolution': 'own-dictionary-all-report-nodes-announced-area-only',
                     'pending_recovery': 'current-code-explicit-conservative-no-refund',
                     'phase_order': ['metadata', 'values'],
                     'receipt_proof': 'current-journal-prefix-counters-a-to-b',
                     'scope_binding': 'exclusive-once-no-reset-or-rebind',
                     'selection_mode': 'installed-exact-member-and-report-order',
                     'single_writer_per_member': True,
                     'single_writer_per_window_ledger': True,
                     'values_barrier': 'all-window-metadata-terminal-and-own-metadata-complete'},
 'job_contract': 'financial-acquisition-job-v2',
 'members': [{'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201003,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201003',
              'window_id': 'F1-01'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201006,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201006',
              'window_id': 'F1-01'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201009,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201009',
              'window_id': 'F1-01'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201012,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201012',
              'window_id': 'F1-01'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201103,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201103',
              'window_id': 'F1-02'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201106,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201106',
              'window_id': 'F1-02'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201109,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201109',
              'window_id': 'F1-02'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201112,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201112',
              'window_id': 'F1-02'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201203,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201203',
              'window_id': 'F1-03'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201206,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201206',
              'window_id': 'F1-03'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201209,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201209',
              'window_id': 'F1-03'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201212,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201212',
              'window_id': 'F1-03'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201303,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201303',
              'window_id': 'F1-04'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201306,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201306',
              'window_id': 'F1-04'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201309,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201309',
              'window_id': 'F1-04'},
             {'announced_numeric_areas': [1, 3],
              'budget_id': 'n2',
              'family': 'F1',
              'period': 201312,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201312',
              'window_id': 'F1-04'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F2',
              'period': 201403,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201403',
              'window_id': 'F2-01'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F2',
              'period': 201406,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201406',
              'window_id': 'F2-01'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F2',
              'period': 201409,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201409',
              'window_id': 'F2-01'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F2',
              'period': 201412,
              'perspective': 1005,
              'reports': [1, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201412',
              'window_id': 'F2-01'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201503,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201503',
              'window_id': 'F3-01'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201506,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201506',
              'window_id': 'F3-01'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201509,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201509',
              'window_id': 'F3-01'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201512,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201512',
              'window_id': 'F3-01'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201603,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201603',
              'window_id': 'F3-02'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201606,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201606',
              'window_id': 'F3-02'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201609,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201609',
              'window_id': 'F3-02'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201612,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201612',
              'window_id': 'F3-02'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201703,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201703',
              'window_id': 'F3-03'},
             {'announced_numeric_areas': [1, 3, 4],
              'budget_id': 'n3',
              'family': 'F3',
              'period': 201706,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201706',
              'window_id': 'F3-03'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F4',
              'period': 201709,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201709',
              'window_id': 'F4-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F4',
              'period': 201712,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201712',
              'window_id': 'F4-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F4',
              'period': 201803,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201803',
              'window_id': 'F4-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F4',
              'period': 201806,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201806',
              'window_id': 'F4-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F4',
              'period': 201809,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201809',
              'window_id': 'F4-02'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F4',
              'period': 201812,
              'perspective': 1005,
              'reports': [75, 3, 4, 5],
              'scope': 'financial-historical-201003-202309-v1/201812',
              'window_id': 'F4-02'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F5',
              'period': 201903,
              'perspective': 1005,
              'reports': [92, 3, 4, 91],
              'scope': 'financial-historical-201003-202309-v1/201903',
              'window_id': 'F5-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F5',
              'period': 201906,
              'perspective': 1005,
              'reports': [92, 3, 4, 91],
              'scope': 'financial-historical-201003-202309-v1/201906',
              'window_id': 'F5-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F5',
              'period': 201909,
              'perspective': 1005,
              'reports': [92, 3, 4, 91],
              'scope': 'financial-historical-201003-202309-v1/201909',
              'window_id': 'F5-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F6',
              'period': 201912,
              'perspective': 1005,
              'reports': [92, 96, 97, 98],
              'scope': 'financial-historical-201003-202309-v1/201912',
              'window_id': 'F6-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F6',
              'period': 202003,
              'perspective': 1005,
              'reports': [92, 96, 97, 98],
              'scope': 'financial-historical-201003-202309-v1/202003',
              'window_id': 'F6-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202006,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202006',
              'window_id': 'F7-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202009,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202009',
              'window_id': 'F7-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202012,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202012',
              'window_id': 'F7-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202103,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202103',
              'window_id': 'F7-01'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202106,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202106',
              'window_id': 'F7-02'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202109,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202109',
              'window_id': 'F7-02'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202112,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202112',
              'window_id': 'F7-02'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202203,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202203',
              'window_id': 'F7-02'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202206,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202206',
              'window_id': 'F7-03'},
             {'announced_numeric_areas': [1, 2, 3, 4],
              'budget_id': 'n4',
              'family': 'F7',
              'period': 202209,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202209',
              'window_id': 'F7-03'},
             {'announced_numeric_areas': [1, 2, 3, 4, 5],
              'budget_id': 'n5',
              'family': 'F8',
              'period': 202212,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202212',
              'window_id': 'F8-01'},
             {'announced_numeric_areas': [1, 2, 3, 4, 5],
              'budget_id': 'n5',
              'family': 'F8',
              'period': 202303,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202303',
              'window_id': 'F8-01'},
             {'announced_numeric_areas': [1, 2, 3, 4, 5],
              'budget_id': 'n5',
              'family': 'F8',
              'period': 202306,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202306',
              'window_id': 'F8-01'},
             {'announced_numeric_areas': [1, 2, 3, 4, 5],
              'budget_id': 'n5',
              'family': 'F8',
              'period': 202309,
              'perspective': 1005,
              'reports': [92, 96, 101, 98],
              'scope': 'financial-historical-201003-202309-v1/202309',
              'window_id': 'F8-01'}],
 'sources_contract': 'ifdata-financial-historical-sources-v1',
 'windows': [{'destination': 'data/runs/financial-historical-acquisition-201003-201012-20261005',
              'periods': [201003, 201006, 201009, 201012],
              'scope': 'financial-historical-201003-202309-v1/F1-01',
              'window_id': 'F1-01'},
             {'destination': 'data/runs/financial-historical-acquisition-201103-201112-20261005',
              'periods': [201103, 201106, 201109, 201112],
              'scope': 'financial-historical-201003-202309-v1/F1-02',
              'window_id': 'F1-02'},
             {'destination': 'data/runs/financial-historical-acquisition-201203-201212-20261005',
              'periods': [201203, 201206, 201209, 201212],
              'scope': 'financial-historical-201003-202309-v1/F1-03',
              'window_id': 'F1-03'},
             {'destination': 'data/runs/financial-historical-acquisition-201303-201312-20261005',
              'periods': [201303, 201306, 201309, 201312],
              'scope': 'financial-historical-201003-202309-v1/F1-04',
              'window_id': 'F1-04'},
             {'destination': 'data/runs/financial-historical-acquisition-201403-201412-20261005',
              'periods': [201403, 201406, 201409, 201412],
              'scope': 'financial-historical-201003-202309-v1/F2-01',
              'window_id': 'F2-01'},
             {'destination': 'data/runs/financial-historical-acquisition-201503-201512-20261005',
              'periods': [201503, 201506, 201509, 201512],
              'scope': 'financial-historical-201003-202309-v1/F3-01',
              'window_id': 'F3-01'},
             {'destination': 'data/runs/financial-historical-acquisition-201603-201612-20261005',
              'periods': [201603, 201606, 201609, 201612],
              'scope': 'financial-historical-201003-202309-v1/F3-02',
              'window_id': 'F3-02'},
             {'destination': 'data/runs/financial-historical-acquisition-201703-201706-20261005',
              'periods': [201703, 201706],
              'scope': 'financial-historical-201003-202309-v1/F3-03',
              'window_id': 'F3-03'},
             {'destination': 'data/runs/financial-historical-acquisition-201709-201806-20261005',
              'periods': [201709, 201712, 201803, 201806],
              'scope': 'financial-historical-201003-202309-v1/F4-01',
              'window_id': 'F4-01'},
             {'destination': 'data/runs/financial-historical-acquisition-201809-201812-20261005',
              'periods': [201809, 201812],
              'scope': 'financial-historical-201003-202309-v1/F4-02',
              'window_id': 'F4-02'},
             {'destination': 'data/runs/financial-historical-acquisition-201903-201909-20261005',
              'periods': [201903, 201906, 201909],
              'scope': 'financial-historical-201003-202309-v1/F5-01',
              'window_id': 'F5-01'},
             {'destination': 'data/runs/financial-historical-acquisition-201912-202003-20261005',
              'periods': [201912, 202003],
              'scope': 'financial-historical-201003-202309-v1/F6-01',
              'window_id': 'F6-01'},
             {'destination': 'data/runs/financial-historical-acquisition-202006-202103-20261005',
              'periods': [202006, 202009, 202012, 202103],
              'scope': 'financial-historical-201003-202309-v1/F7-01',
              'window_id': 'F7-01'},
             {'destination': 'data/runs/financial-historical-acquisition-202106-202203-20261005',
              'periods': [202106, 202109, 202112, 202203],
              'scope': 'financial-historical-201003-202309-v1/F7-02',
              'window_id': 'F7-02'},
             {'destination': 'data/runs/financial-historical-acquisition-202206-202209-20261005',
              'periods': [202206, 202209],
              'scope': 'financial-historical-201003-202309-v1/F7-03',
              'window_id': 'F7-03'},
             {'destination': 'data/runs/financial-historical-acquisition-202212-202309-20261005',
              'periods': [202212, 202303, 202306, 202309],
              'scope': 'financial-historical-201003-202309-v1/F8-01',
              'window_id': 'F8-01'}],
 'worker_contract': 'financial-acquisition-worker-v3'}




def _historical_window(window_id):
    policy = _historical_policy(_HISTORICAL_POLICY_V1)
    matches = [w for w in policy['windows'] if type(window_id) is str and w['window_id'] == window_id]
    _require(len(matches) == 1, 'Installed historical window required')
    return matches[0]


def _historical_member(period):
    policy = _historical_policy(_HISTORICAL_POLICY_V1)
    matches = [m for m in policy['members'] if type(period) is int and m['period'] == period]
    _require(len(matches) == 1, 'Installed historical member required')
    return matches[0]


def _historical_limits(budget_id):
    budgets = _historical_policy(_HISTORICAL_POLICY_V1)['budgets']
    _require(type(budget_id) is str and budget_id in budgets, 'Installed historical budget required')
    budget = budgets[budget_id]
    aliases = {'attempts': 'attempts_per_target', 'metadata_body_bytes': 'metadata_body_bytes_per_target',
               'numeric_body_bytes': 'numeric_body_bytes_per_target', 'attempt_seconds': 'attempt_seconds_max',
               'backoff_seconds': 'backoff_seconds_max', 'scheduling_seconds': 'scheduling_seconds_max'}
    return {key: budget[aliases.get(key, key)] for key in _POLICIES}


def _compile_historical(refs, window_id):
    window = _historical_window(window_id)
    catalogs = acquisition._catalogs(refs)
    members = []
    for period in window['periods']:
        installed = _historical_member(period)
        descriptor = acquisition._descriptor(catalogs['old'], refs['old'], period)
        _same(descriptor['selection'], {key: installed[key] for key in ('period', 'perspective', 'reports')},
              'Historical report order/selection differs')
        _same([o['area'] for o in descriptor['source_offers'] if o['role'] == 'numeric'],
              installed['announced_numeric_areas'], 'Historical announced areas differ')
        targets = sorted((acquisition._target(o, period) for o in descriptor['source_offers']
                          if o['role'] != 'numeric'), key=lambda t: t['target_key'])
        job = {'contract': 'financial-acquisition-job-v2', 'version': 2,
               'acquisition_scope': installed['scope'], 'catalogs': copy.deepcopy(refs),
               'descriptors': [descriptor], 'policies': _historical_limits(installed['budget_id']),
               'targets': targets, 'member': installed, 'policy_sha256': _HISTORICAL_POLICY_SHA256}
        job['job_sha256'] = acquisition._job_hash(job)
        job['executable'] = False
        members.append({'period': period, 'job': job, 'job_sha256': job['job_sha256'],
                        'session_root': window['destination'] + f'/members/{period}/sessions'})
    return {'contract': 'financial-acquisition-batch-draft-v2', 'scope': window['scope'],
            'window_id': window_id, 'destination': window['destination'],
            'policy_sha256': _HISTORICAL_POLICY_SHA256, 'catalogs': copy.deepcopy(refs),
            'members': members, 'acquire_periods': window['periods'], 'reuse_periods': [], 'reuse': [],
            'selection': {'perspective': 1005, 'reports': 'native-four', 'periods': window['periods']},
            'policies': {'max_guard_streak': 2},
            'caps': {'per_member': {}, 'total': {
                'attempts': sum(_HISTORICAL_POLICY_V1['budgets'][m['job']['member']['budget_id']]['attempts_max'] for m in members),
                'body_bytes': sum(_HISTORICAL_POLICY_V1['budgets'][m['job']['member']['budget_id']]['body_bytes_max'] for m in members),
                'scheduling_seconds': sum(m['job']['policies']['scheduling_seconds'] for m in members)}},
            'executable': False}


def prepare_historical_batch(catalog_index, catalog_index_sha256, *, window_id):
    path = _path(Path(catalog_index).absolute().relative_to(_ROOT.absolute()).as_posix())
    _file(path, acquisition._digest(catalog_index_sha256))
    index = _json(path.read_bytes())
    _require(type(index) is dict and set(index) == {'contract', 'acquisition_scope', 'selection', 'catalogs'}
             and index['contract'] == acquisition.INDEX_CONTRACT, 'Invalid catalog index schema')
    _same(index['selection'], {'perspective': 1005, 'reports': 'native-four'}, 'Wrong financial selection')
    return _compile_historical(index['catalogs'], window_id)


def _verify_historical_job(job):
    _require(type(job) is dict and set(job) == {'contract', 'version', 'acquisition_scope', 'catalogs',
        'descriptors', 'policies', 'targets', 'member', 'policy_sha256', 'job_sha256', 'executable'}
        and job['contract'] == 'financial-acquisition-job-v2' and type(job['version']) is int
        and job['version'] == 2 and job['executable'] is False and type(job['member']) is dict,
        'Invalid closed historical job')
    installed = _historical_member(job['member'].get('period'))
    expected = next(m['job'] for m in _compile_historical(job['catalogs'], installed['window_id'])['members']
                    if m['period'] == installed['period'])
    _same(job, expected, 'Historical job differs from installed selection/scope/budget/descriptor')
    budget = _HISTORICAL_POLICY_V1['budgets'][installed['budget_id']]
    offers = job['descriptors'][0]['source_offers']
    _require(len(offers) == budget['target_count_max'], 'Historical target cap differs')
    return {t['target_key']: t for t in (acquisition._target(o, installed['period']) for o in offers)}


def _current_code_identity():
    import subprocess
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=_ROOT, text=True).strip()
    return {'reviewed_commit': head, 'files': {name: _sha(_path(name).read_bytes()) for name in _CODE_FILES},
            'runtime': {'path': str(Path(sys.executable).resolve()), 'sha256': _sha(Path(sys.executable).read_bytes())}}


def _code_identity(pins, *, current_head=False):
    _require(type(pins) is dict and set(pins) == {'contract', 'reviewed_commit', 'files', 'runtime', 'policy_sha256'}
             and pins['contract'] == 'financial-acquisition-code-pins-v1', 'Invalid closed code pins')
    _require(type(pins['reviewed_commit']) is str and re.fullmatch('[0-9a-f]{40}', pins['reviewed_commit']),
             'Full reviewed commit identity required')
    _require(type(pins['files']) is dict and set(pins['files']) == set(_CODE_FILES), 'Closed reviewed code inventory required')
    for pin in pins['files'].values():
        acquisition._digest(pin)
    _require(type(pins['runtime']) is dict and set(pins['runtime']) == {'path', 'sha256'}
             and type(pins['runtime']['path']) is str and pins['runtime']['path'], 'Invalid pinned runtime')
    acquisition._digest(pins['runtime']['sha256'])
    _require(acquisition._digest(pins['policy_sha256']) == _sha(_canonical(_POLICIES)), 'Policy identity mismatch')
    identity = _current_code_identity()
    _same({'files': pins['files'], 'runtime': pins['runtime']},
          {key: identity[key] for key in ('files', 'runtime')}, 'Current code/runtime differs from reviewed pins')
    if current_head:
        _require(pins['reviewed_commit'] == identity['reviewed_commit'], 'Current HEAD differs from reviewed full commit')


def _historical_policy(value):
    """Only the reviewed finite literal; no runtime resource or policy override."""
    acquisition._closed_data(value)
    _require(_sha(_canonical(_HISTORICAL_POLICY_V1)) == _HISTORICAL_POLICY_SHA256
             and _canonical(value) == _canonical(_HISTORICAL_POLICY_V1), 'Historical installed policy differs')
    return copy.deepcopy(value)


def _current_code_identity_v2():
    identity = _current_code_identity()
    identity['files']['bank_quality/financial_acquisition_compat.py'] = _sha(
        _path('bank_quality/financial_acquisition_compat.py').read_bytes())
    return identity


def _code_identity_v2(pins):
    acquisition._closed_data(pins)
    _require(type(pins) is dict and set(pins) == {'contract', 'reviewed_commit', 'files', 'runtime', 'policy_sha256'}
             and pins['contract'] == 'financial-acquisition-code-pins-v2', 'Invalid closed v2 code pins')
    _require(type(pins['reviewed_commit']) is str and re.fullmatch('[0-9a-f]{40}', pins['reviewed_commit']),
             'Full reviewed commit identity required')
    _require(type(pins['files']) is dict and set(pins['files']) == set(_CODE_FILES_V2),
             'Closed six file reviewed code inventory required')
    for pin in pins['files'].values():
        acquisition._digest(pin)
    _require(type(pins['runtime']) is dict and set(pins['runtime']) == {'path', 'sha256'}
             and type(pins['runtime']['path']) is str and pins['runtime']['path'], 'Invalid pinned runtime')
    acquisition._digest(pins['runtime']['sha256'])
    _historical_policy(_HISTORICAL_POLICY_V1)
    _require(acquisition._digest(pins['policy_sha256']) == _HISTORICAL_POLICY_SHA256, 'Policy identity mismatch')
    _same({key: pins[key] for key in ('reviewed_commit', 'files', 'runtime')},
          _current_code_identity_v2(), 'Current code/runtime/HEAD differs from reviewed six pins')


def _verified_current_code_pins(path, pin):
    name = Path(path).absolute().relative_to(_ROOT.absolute()).as_posix()
    _require(name.startswith('data/runs/'), 'Current code pins outside approved runs')
    pins = _read(_reference(name, acquisition._digest(pin)))
    _code_identity_v2(pins)
    return pins


def verify_legacy54_sources(*, current_code_pins_path, current_code_pins_sha256):
    """CLI seam: authenticate all six current bytes before importing compat."""
    _verified_current_code_pins(current_code_pins_path, current_code_pins_sha256)
    from importlib import import_module
    compat = import_module('bank_quality.financial_acquisition_compat')
    return compat.verify_legacy54_sources(current_code_pins_path=current_code_pins_path,
                                          current_code_pins_sha256=current_code_pins_sha256)


def reconstruct_legacy54_handoff(*, current_code_pins_path, current_code_pins_sha256):
    _verified_current_code_pins(current_code_pins_path, current_code_pins_sha256)
    from importlib import import_module
    compat = import_module('bank_quality.financial_acquisition_compat')
    return compat.reconstruct_legacy54_handoff(current_code_pins_path=current_code_pins_path,
                                             current_code_pins_sha256=current_code_pins_sha256)


def _batch_paths(scope=_SCOPE):
    base = acquisition._safe_destination(_ROOT / 'data/runs/financial-acquisition-authority')
    stem = 'batch-scope-' + _sha(scope.encode())
    return base / (stem + '.binding.json'), base / (stem + '.lock')


def _member_bootstrap(job):
    return {'contract': 'financial-acquisition-authority-v1', 'acquisition_scope': job['acquisition_scope'],
            'job_sha256': job['job_sha256'], 'policies': acquisition._limits(job),
            'targets': acquisition._execution_job(job)}


def _build_bundle(draft, destination, pins):
    members = []
    for member in draft['members']:
        job = member['job']
        folder, _, _ = acquisition._authority_paths(job)
        name = destination + '/members/' + str(member['period']) + '/job.json'
        members.append({**copy.deepcopy(member), 'job_path': name,
                        'job_file_sha256': _sha(_canonical(job)),
                        'authority_path': folder.relative_to(_ROOT).as_posix(),
                        'bootstrap_sha256': _sha(_canonical(_member_bootstrap(job)))})
    return {**copy.deepcopy(draft), 'contract': ('financial-acquisition-batch-v2' if draft['contract'].endswith('-v2') else 'financial-acquisition-batch-v1'), 'members': members,
            'destination': destination, 'code_pins': copy.deepcopy(pins), 'executable': True}


def _batch_bootstrap(bundle, pin):
    return {'contract': 'financial-acquisition-batch-bootstrap-v1', 'scope': bundle['scope'],
            'bundle_sha256': pin, 'destination': bundle['destination'],
            'members': [{key: m[key] for key in ('period', 'job_sha256', 'job_file_sha256',
                                                 'job_path', 'authority_path', 'bootstrap_sha256')} for m in bundle['members']],
            'policies': bundle['policies'], 'caps': bundle['caps'], 'code_pins': bundle['code_pins']}


def _binding(bundle, pin, bootstrap_pin):
    return {'contract': 'financial-acquisition-batch-binding-v1', 'scope': bundle['scope'],
            'bundle_path': bundle['destination'] + '/bundle.json', 'bundle_sha256': pin,
            'bootstrap_sha256': bootstrap_pin}


def _immutable_batch(bundle_path, bundle_pin, bootstrap_pin, *, require_binding=True):
    path = _path(Path(bundle_path).absolute().relative_to(_ROOT.absolute()).as_posix())
    _file(path, bundle_pin)
    bundle = _json(path.read_bytes())
    fields = {'contract', 'scope', 'selection', 'acquire_periods', 'reuse_periods', 'catalogs', 'members',
              'reuse', 'policies', 'caps', 'executable', 'destination', 'code_pins'}
    _require(type(bundle) is dict, 'Invalid bundle schema')
    if bundle.get('contract') == 'financial-acquisition-batch-v2':
        fields |= {'window_id', 'policy_sha256'}
    _require(set(bundle) == fields and type(bundle['members']) is list, 'Invalid bundle schema')
    historical = bundle.get('contract') == 'financial-acquisition-batch-v2'
    if historical:
        fields |= {'window_id', 'policy_sha256'}
    member_fields = {'period', 'job', 'job_sha256', 'session_root', 'job_path', 'job_file_sha256', 'authority_path', 'bootstrap_sha256'}
    _require(all(type(m) is dict and set(m) == member_fields for m in bundle['members']), 'Invalid bundle member schema')
    _bundle_code_identity(bundle)
    draft = {key: copy.deepcopy(bundle[key]) for key in fields - ({'code_pins'} if historical else {'destination', 'code_pins'})}
    draft.update(contract='financial-acquisition-batch-draft-v2' if historical else 'financial-acquisition-batch-draft-v1', executable=False,
                 members=[{key: m[key] for key in ('period', 'job', 'job_sha256', 'session_root')} for m in bundle['members']])
    draft = _verify_draft(draft)
    destination = acquisition._safe_destination(_ROOT / bundle['destination'])
    _require(destination.relative_to(_ROOT).as_posix() == bundle['destination']
             and path == destination / 'bundle.json', 'Bundle destination/path differs')
    _same(bundle, _build_bundle(draft, bundle['destination'], bundle['code_pins']), 'Bundle differs from closed draft/bindings')
    bootstrap = _batch_bootstrap(bundle, bundle_pin)
    _file(destination / 'bootstrap.json', bootstrap_pin)
    _same(_json((destination / 'bootstrap.json').read_bytes()), bootstrap, 'Batch bootstrap identity mismatch')
    binding, _ = _batch_paths(bundle['scope'])
    if require_binding:
        _same(_json(_path(binding.relative_to(_ROOT).as_posix()).read_bytes()), _binding(bundle, bundle_pin, bootstrap_pin),
              'Immutable batch scope binding mismatch')
    for member in bundle['members']:
        _file(_path(member['job_path']), member['job_file_sha256'])
        _same(_json(_path(member['job_path']).read_bytes()), member['job'], 'Member physical/canonical job mismatch')
    return bundle


class _MemberContext:
    def __init__(self, batch, member):
        self.batch, self.member = batch, member


def _authorize_member(job, context):
    _require(type(context) is _MemberContext and context.batch.active, 'Authenticated active coordinator member context required')
    batch = context.batch
    _require(context.member in batch.bundle['members'] and _canonical(job) == _canonical(context.member['job']),
             'Coordinator member identity mismatch')
    # Validate immutable bytes again at the supported singleton boundary. No global
    # mutable head is passed to workers; the member journal remains authoritative.
    _bound_bytes(batch)
    member_path = _path(context.member['job_path'])
    _file(member_path, context.member['job_file_sha256'])
    _same(_json(member_path.read_bytes()), context.member['job'], 'Active physical member job differs from embedded identity')


def _bound_bytes(batch):
    """Small immutable recheck inside one authenticated active batch claim."""
    _bundle_code_identity(batch.bundle)
    path = _path(batch.binding['bundle_path'])
    _file(path, batch.pin)
    _same(_json(path.read_bytes()), batch.bundle, 'Active bundle bytes changed')
    bootstrap_path = _path(batch.bundle['destination'] + '/bootstrap.json')
    _file(bootstrap_path, batch.bootstrap_pin)
    _same(_json(bootstrap_path.read_bytes()), _batch_bootstrap(batch.bundle, batch.pin), 'Active bootstrap changed')
    binding, _ = _batch_paths(batch.bundle['scope'])
    _same(_json(_path(binding.relative_to(_ROOT).as_posix()).read_bytes()), batch.binding, 'Immutable batch scope binding mismatch')


def _initialize_batch(draft_path: Path, draft_sha256: str, destination: Path, *, code_pins: dict) -> dict:
    path = _path(Path(draft_path).absolute().relative_to(_ROOT.absolute()).as_posix())
    _file(path, draft_sha256)
    draft = _verify_draft(_json(path.read_bytes()))
    historical = draft['contract'] == 'financial-acquisition-batch-draft-v2'
    if historical:
        expected_destination = acquisition._safe_destination(_ROOT / draft['destination'])
        _require(acquisition._safe_destination(destination) == expected_destination, 'Historical destination must exactly match installed window')
        _code_identity_v2(code_pins)
    else:
        _code_identity(code_pins, current_head=True)
    destination = acquisition._safe_destination(destination)
    _require(not destination.exists(), 'Batch destination must be new')
    name = destination.relative_to(_ROOT).as_posix()
    bundle = _build_bundle(draft, name, code_pins)
    pin = _sha(_canonical(bundle))
    bootstrap = _batch_bootstrap(bundle, pin)
    bootstrap_pin = _sha(_canonical(bootstrap))
    binding_path, lock = _batch_paths(bundle['scope'])
    lock.parent.mkdir(parents=True, exist_ok=True)
    with acquisition._claim(lock):
        _require(not binding_path.exists(), 'Batch scope binding already exists; no reset/rebinding')
        # Reserve the scope before any member bootstrap. Even interrupted/partial
        # initialization cannot renew it with different paths, code or policies.
        binding = _binding(bundle, pin, bootstrap_pin)
        acquisition._write_exclusive(binding_path, binding)
        destination.mkdir(parents=True, exist_ok=False)
        acquisition._write_exclusive(destination / 'bundle.json', bundle)
        acquisition._write_exclusive(destination / 'bootstrap.json', bootstrap)
        for member in bundle['members']:
            member_path = _ROOT / member['job_path']
            member_path.parent.mkdir(parents=True, exist_ok=False)
            acquisition._write_exclusive(member_path, member['job'])
        with (destination / 'journal.jsonl').open('xb') as output:
            output.flush()
            os.fsync(output.fileno())
        batch = _Batch(bundle, pin, bootstrap_pin, [], _ledger_state())
        try:
            acquisition._replace_head(destination, batch.head())
            for member in bundle['members']:
                actual = acquisition._initialize_authority(member['job'], coordinator=_MemberContext(batch, member))
                _require(actual == member['bootstrap_sha256'], 'Actual member bootstrap differs from predicted immutable bytes')
        finally:
            batch.active = False
    return {**binding, 'contract': 'financial-acquisition-batch-initialization-v1', 'status': 'initialized'}


def _ledger_state():
    return {'pending': {}, 'finished': {}, 'guard': '', 'guard_streak': 0, 'halt': ''}


def _apply_phase(state, record, bundle):
    base = {'contract', 'sequence', 'previous_record_sha256', 'bundle_sha256', 'bootstrap_sha256', 'kind'}
    kind = record.get('kind')
    fields = ({'phase_id', 'period', 'phase', 'session', 'job_sha256', 'member_bootstrap_sha256', 'member_sequence', 'member_record_sha256'}
              if kind == 'phase_start' else {'phase_id', 'result', 'recovered'} if kind == 'phase_finish' else
              {'phase_id', 'resource_measurement'} if kind == 'representative_measurement' else
              {'representative_period', 'phase_id', 'resource_profile', 'resource_measurement', 'measurements', 'result'} if kind == 'representative_checkpoint' else {'reason'})
    _require(type(record) is dict and set(record) == base | fields and record['contract'] == 'financial-acquisition-batch-ledger-v1'
             and type(record['sequence']) is int and record['sequence'] > 0 and kind in (('phase_start', 'phase_finish', 'halt', 'representative_measurement', 'representative_checkpoint')
                 if bundle['contract'] == 'financial-acquisition-batch-v2' else ('phase_start', 'phase_finish', 'halt')),
             'Invalid closed phase record')
    if kind == 'phase_start':
        _require(not state['halt'] and type(record['period']) is int and record['period'] in bundle['acquire_periods']
                 and record['phase'] in ('metadata', 'values'), 'Phase outside fixed window/phase')
        member = next(m for m in bundle['members'] if m['period'] == record['period'])
        _require(record['job_sha256'] == member['job_sha256'] and record['member_bootstrap_sha256'] == member['bootstrap_sha256']
                 and type(record['phase_id']) is str and re.fullmatch('[0-9a-f]{32}', record['phase_id'])
                 and type(record['member_sequence']) is int and record['member_sequence'] >= 0, 'Phase member/start identity differs')
        acquisition._digest(record['member_record_sha256'])
        session = member['session_root'] + '/' + record['phase'] + '-' + record['phase_id']
        _require(record['session'] == session and record['phase_id'] not in state['pending']
                 and record['phase_id'] not in state['finished'], 'Phase session/id differs')
        previous = list(state['pending'].values()) + list(state['finished'].values())
        _require(not any(p['period'] == record['period'] and p['phase'] == record['phase'] for p in previous), 'Duplicate member phase')
        if record['phase'] == 'values':
            if bundle['contract'] == 'financial-acquisition-batch-v2' and record['period'] != bundle['acquire_periods'][0]:
                _require('representative_checkpoint' in state, 'Remaining values require durable representative checkpoint')
            _require({p['period'] for p in state['finished'].values() if p['phase'] == 'metadata'} == set(bundle['acquire_periods']),
                     'Values require terminal metadata barrier for seven members')
            _require(any(p['period'] == record['period'] and p['phase'] == 'metadata' and p['result']['status'] == 'complete'
                         for p in state['finished'].values()) and not state['pending'], 'Values require completed metadata and serial values')
        else:
            _require(not any(p['phase'] == 'values' for p in state['pending'].values()) and len(state['pending']) < (1 if bundle['contract'] == 'financial-acquisition-batch-v2' else 2),
                     'Metadata concurrency exceeds approved two slots')
        state['pending'][record['phase_id']] = copy.deepcopy(record)
    elif kind == 'phase_finish':
        _require(record['phase_id'] in state['pending'] and type(record['recovered']) is bool, 'Unknown phase conclusion')
        result = record['result']
        _result_schema(result)
        start = state['pending'].pop(record['phase_id'])
        state['finished'][record['phase_id']] = {**start, 'result': copy.deepcopy(result)}
        guard = result['guard'] if result['guard'] in ('integrity', 'schema', 'deadline') else ''
        state['guard_streak'] = acquisition._next_guard_streak(state, guard,
            job_contract='financial-acquisition-job-v2' if bundle['contract'] == 'financial-acquisition-batch-v2' else acquisition.JOB_CONTRACT)
        state['guard'] = guard
        if state['guard_streak'] >= bundle['policies']['max_guard_streak']:
            state['halt'] = 'consecutive_guard'
        failed = {p['period'] for p in state['finished'].values() if p['result']['status'] == 'failed'}
        if len(failed) >= 3:
            state['halt'] = state['halt'] or 'three_failed_members'
        if result['guard'] in ('persistence', 'containment', 'monitor_failure'):
            state['halt'] = state['halt'] or 'critical_' + result['guard']
    elif kind == 'representative_measurement':
        start = state['pending'].get(record['phase_id'])
        _require(not state['halt'] and 'representative_measurement' not in state and start is not None
                 and start['phase'] == 'values' and start['period'] == bundle['acquire_periods'][0],
                 'Original representative measurement requires pending representative values')
        ref = record['resource_measurement']
        _require(type(ref) is dict and set(ref) == {'path', 'sha256'}
                 and ref['path'] == start['session'] + '/resource-measurement.json',
                 'Original representative measurement outside exact phase')
        acquisition._digest(ref['sha256'])
        state['representative_measurement'] = copy.deepcopy(record)
    elif kind == 'representative_checkpoint':
        period = bundle['acquire_periods'][0]
        _require(not state['halt'] and not state['pending'] and 'representative_checkpoint' not in state
                 and type(record['representative_period']) is int and record['representative_period'] == period,
                 'Invalid representative checkpoint boundary')
        terminal = state['finished'].get(record['phase_id'])
        _require(terminal is not None and terminal['period'] == period and terminal['phase'] == 'values'
                 and terminal['result']['status'] == 'complete', 'Representative values must be complete before checkpoint')
        original = state.get('representative_measurement')
        _require(original is not None and original['phase_id'] == record['phase_id'],
                 'Original representative measurement missing before checkpoint')
        _same(record['resource_measurement'], original['resource_measurement'], 'Representative measurement anchor differs')
        _same(record['result'], terminal['result'], 'Representative checkpoint receipt/B differs from terminal proof')
        ref = record['resource_profile']
        _require(type(ref) is dict and set(ref) == {'path', 'sha256'}, 'Invalid representative resource profile reference')
        _relative_name(ref['path'])
        acquisition._digest(ref['sha256'])
        measurements = record['measurements']
        acquisition._closed_data(measurements)
        _require(type(measurements) is dict and set(measurements) == {'sample_count', 'peaks', 'minimum_free'}
                 and type(measurements['sample_count']) is int and measurements['sample_count'] > 0,
                 'Measured representative checkpoint required')
        for key, fields in (('peaks', {'tree_working_set_bytes', 'tree_private_bytes'}),
                            ('minimum_free', {'free_physical_bytes', 'free_commit_bytes', 'free_disk_bytes'})):
            _require(type(measurements[key]) is dict and set(measurements[key]) == fields
                     and all(type(v) is int and v >= 0 for v in measurements[key].values()), 'Invalid representative measurements')
        state['representative_checkpoint'] = copy.deepcopy(record)
    else:
        _require(type(record['reason']) is str and record['reason'], 'Halt reason required')
        state['halt'] = state['halt'] or record['reason']


def _replay_phase_records(records, *, anchored_bundle):
    """Recompute the finite v1 ledger in memory, without a batch context."""
    acquisition._closed_data(records)
    acquisition._closed_data(anchored_bundle)
    _require(type(records) is list and type(anchored_bundle) is dict
             and set(anchored_bundle) == {'bundle', 'bundle_sha256', 'bootstrap_sha256'},
             'Invalid phase replay data')
    bundle = anchored_bundle['bundle']
    for key in ('bundle_sha256', 'bootstrap_sha256'):
        acquisition._digest(anchored_bundle[key])
    state, checked, states = _ledger_state(), [], [_ledger_state()]
    for raw in records:
        _require(type(raw) is dict and 'record_sha256' in raw, 'Invalid phase journal record')
        record = copy.deepcopy(raw)
        pin = record.pop('record_sha256')
        _require(pin == _sha(_canonical(record)) and type(record.get('sequence')) is int
                 and record['sequence'] == len(checked) + 1 and record['previous_record_sha256'] ==
                 (checked[-1]['record_sha256'] if checked else acquisition._EMPTY_HASH)
                 and record['bundle_sha256'] == anchored_bundle['bundle_sha256']
                 and record['bootstrap_sha256'] == anchored_bundle['bootstrap_sha256'], 'Batch journal chain/pins mismatch')
        _apply_phase(state, record, bundle)
        record['record_sha256'] = pin
        checked.append(record)
        states.append(copy.deepcopy(state))
    return {'records': checked, 'state': state, 'states': states,
            'head': {'sequence': len(checked),
                     'record_sha256': checked[-1]['record_sha256'] if checked else acquisition._EMPTY_HASH,
                     'state_sha256': _sha(_canonical(state))}}


class _Batch:
    def __init__(self, bundle, pin, bootstrap_pin, records, state):
        self.bundle, self.pin, self.bootstrap_pin = bundle, pin, bootstrap_pin
        self.records, self.state, self.active = records, state, True
        self.inflight = set()
        self.halt_reason = ''
        self.binding = _binding(bundle, pin, bootstrap_pin)
        self.folder = _ROOT / bundle['destination']

    @property
    def halted(self):
        return self.halt_reason or self.state['halt']

    def head(self):
        return {'sequence': len(self.records), 'record_sha256': self.records[-1]['record_sha256'] if self.records else acquisition._EMPTY_HASH,
                'state_sha256': _sha(_canonical(self.state))}

    def append(self, kind, **details):
        _require(self.active, 'Batch claim closed')
        record = {'contract': 'financial-acquisition-batch-ledger-v1', 'sequence': len(self.records) + 1,
                  'previous_record_sha256': self.head()['record_sha256'], 'bundle_sha256': self.pin,
                  'bootstrap_sha256': self.bootstrap_pin, 'kind': kind, **details}
        state = copy.deepcopy(self.state)
        _apply_phase(state, record, self.bundle)
        record['record_sha256'] = _sha(_canonical(record))
        with acquisition._safe_destination(self.folder / 'journal.jsonl').open('ab') as output:
            output.write(_canonical(record) + b'\n')
            output.flush()
            os.fsync(output.fileno())
        self.records.append(record)
        self.state = state
        acquisition._replace_head(self.folder, self.head())
        _require((self.folder / 'journal.jsonl').read_bytes().endswith(_canonical(record) + b'\n')
                 and _json((self.folder / 'head.json').read_bytes()) == self.head(), 'Durable phase append/head mismatch')
        return record

    def halt(self, reason):
        marker = self.folder / 'halt.json'
        expected = {'contract': 'financial-acquisition-batch-halt-v1', 'bundle_sha256': self.pin,
                    'bootstrap_sha256': self.bootstrap_pin, 'reason': reason}
        if marker.exists():
            previous = _json(_path(marker.relative_to(_ROOT).as_posix()).read_bytes())
            _require(set(previous) == set(expected) and previous['contract'] == expected['contract']
                     and previous['bundle_sha256'] == self.pin and previous['bootstrap_sha256'] == self.bootstrap_pin
                     and type(previous['reason']) is str and previous['reason'], 'Invalid persisted batch halt')
            reason = previous['reason']
        else:
            acquisition._write_exclusive(marker, expected)
        self.halt_reason = reason
        return reason


@contextmanager
def _open_batch(bundle_path, bundle_sha256, bootstrap_sha256, *, recover=False):
    bundle = _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256)
    binding, lock = _batch_paths(bundle['scope'])
    _require(lock.is_file(), 'Existing batch claim file required')
    with acquisition._claim(lock):
        # Repeat after claim acquisition to close the supported writer boundary.
        checked = _Batch(bundle, bundle_sha256, bootstrap_sha256, [], _ledger_state())
        _bound_bytes(checked)
        checked.active = False
        folder = _ROOT / bundle['destination']
        raw = _path((folder / 'journal.jsonl').relative_to(_ROOT).as_posix()).read_bytes()
        _require(not raw or raw.endswith(b'\n'), 'Partial batch journal tail; never truncate')
        replay = _replay_phase_records([_json(line) for line in raw.splitlines()], anchored_bundle={
            'bundle': bundle, 'bundle_sha256': bundle_sha256, 'bootstrap_sha256': bootstrap_sha256})
        records, state = replay['records'], replay['state']
        heads = [{'sequence': seq, 'record_sha256': records[seq - 1]['record_sha256'] if seq else acquisition._EMPTY_HASH,
                  'state_sha256': _sha(_canonical(item))} for seq, item in enumerate(replay['states'])]
        head = _json(_path((folder / 'head.json').relative_to(_ROOT).as_posix()).read_bytes())
        seq = head.get('sequence')
        _require(type(seq) is int and 0 <= seq < len(heads) and head == heads[seq], 'Batch head missing/invalid')
        _require(recover or seq == len(records), 'Batch head lags journal; recover offline')
        if recover and seq != len(records):
            acquisition._replace_head(folder, heads[-1])
        batch = _Batch(bundle, bundle_sha256, bootstrap_sha256, records, state)
        try:
            if (folder / 'halt.json').exists():
                batch.halt('previous_halt')
            yield batch
        finally:
            batch.active = False


def _result_schema(result):
    _require(type(result) is dict and set(result) == {'contract', 'status', 'guard', 'receipt', 'checkpoint', 'error'}
             and result['contract'] == 'financial-acquisition-phase-result-v1'
             and result['status'] in ('complete', 'failed') and type(result['guard']) is str
             and type(result['error']) is str, 'Invalid terminal phase result')
    for ref in (result['receipt'], result['checkpoint']):
        _require(ref is None or type(ref) is dict and set(ref) == {'path', 'sha256'}, 'Invalid terminal proof ref')
        if ref is not None:
            _relative_name(ref['path'])
            acquisition._digest(ref['sha256'])
    _require(result['receipt'] is not None and ((result['status'] == 'complete' and result['checkpoint'] is not None
             and not result['guard'] and not result['error']) or (result['status'] == 'failed' and result['checkpoint'] is None
             and result['error'])), 'Terminal phase status/proofs inconsistent')


def _prove_phase_sources(phase_data, member_state_data, *, anchored_member):
    """Join already authenticated native sources and receipts in memory only."""
    for value in (phase_data, member_state_data, anchored_member):
        acquisition._closed_data(value)
    _require(type(phase_data) is dict and set(phase_data) == {
        'start', 'result', 'receipt', 'checkpoint', 'resolved', 'metadata_checkpoint_ref', 'metadata_checkpoint'},
        'Invalid closed phase source data')
    start, result, member = phase_data['start'], phase_data['result'], anchored_member
    _result_schema(result)
    _require(start['period'] == member['period'] and start['job_sha256'] == member['job_sha256']
             and start['member_bootstrap_sha256'] == member['bootstrap_sha256'], 'Phase source member identity differs')
    records = member_state_data['records']
    prefix = acquisition._prove_receipt_prefix(phase_data['receipt'], records, identity={
        'job_sha256': member['job_sha256'], 'bootstrap_sha256': member['bootstrap_sha256'],
        'targets': member_state_data['targets'], 'policy': member_state_data['policy']}, job_contract=member['job']['contract'])
    sequence = start['member_sequence']
    _require(type(sequence) is int and 0 <= sequence < prefix['head']['sequence']
             and start['member_record_sha256'] == (records[sequence - 1]['record_sha256'] if sequence else acquisition._EMPTY_HASH)
             and not prefix['state']['pending'] and prefix['session_id'] == Path(start['session']).name
             and result['receipt']['path'] == start['session'] + '/receipt.json',
             'Phase receipt/start prefix is stale, pending, or outside exact session')
    if result['status'] == 'failed':
        _require(prefix['state']['failures'] > member_state_data['states'][sequence]['failures']
                 and result['guard'] == prefix['state']['guard'], 'Failed phase lacks member failure/guard evidence')
        return {'receipt_prefix': prefix, 'checkpoint': None, 'source_refs': []}
    resolved = phase_data['resolved']
    _require(type(resolved) is dict and resolved['job_sha256'] == member['job_sha256']
             and resolved['source_complete'] is True and resolved['source_validated'] is True
             and resolved['origin_resolved'] is True and len(resolved['checkpoints']) == 1,
             'Authenticated native resolution incomplete')
    a = resolved['checkpoints'][0]
    metadata_keys = {t['target_key'] for t in member['job']['targets']}
    sources = prefix['state']['sources']
    _require(metadata_keys <= set(sources), 'Metadata source proof incomplete')
    projection = ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'manifest_path',
                  'manifest_sha256', 'body_sha256', 'provenance_sha256')
    _same(a['selection'], member['job']['descriptors'][0]['selection'], 'Checkpoint selection differs')
    _same(a['sources'], sorted([{key: sources[t][key] for key in projection} for t in metadata_keys],
                              key=lambda ref: ref['source_id']), 'Metadata resolution/source set differs')
    if start['phase'] == 'metadata':
        _require(result['checkpoint']['path'] == start['session'] + '/checkpoint-a.json', 'Checkpoint A outside phase session')
        expected = a
    else:
        _require(start['phase'] == 'values' and result['checkpoint']['path'] == start['session'] + '/checkpoint-b.json',
                 'Checkpoint B outside phase session')
        _same(phase_data['metadata_checkpoint'], a, 'Metadata checkpoint changed before values')
        targets = resolved['numeric_targets']
        _require(set(sources) == metadata_keys | {t['target_key'] for t in targets}, 'Numeric source proof incomplete/extra')
        expected = {**a, 'phase': 'complete', 'checkpoint_a_sha256': phase_data['metadata_checkpoint_ref']['sha256'],
                    'sources': sorted([{key: ref[key] for key in projection} for ref in sources.values()],
                                      key=lambda ref: ref['source_id'])}
    _same(phase_data['checkpoint'], expected, 'Checkpoint differs from native accepted sources')
    return {'receipt_prefix': prefix, 'checkpoint': copy.deepcopy(expected), 'source_refs': copy.deepcopy(expected['sources'])}


def _proof(batch, start, result, *, current=True):
    _result_schema(result)
    member = next(m for m in batch.bundle['members'] if m['period'] == start['period'])
    context = _MemberContext(batch, member)
    with acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=context) as authority:
        receipt = _read(result['receipt'])
        acquisition._verify_receipt(receipt, authority)
        _require((not current or receipt['sequence'] == len(authority.records) and not authority.state['pending'])
                 and receipt['session_id'] == Path(start['session']).name and not receipt['state']['pending']
                 and receipt['sequence'] > start['member_sequence'],
                 'Phase receipt is stale, pending, or lacks terminal progress')
        _require(result['receipt']['path'] == start['session'] + '/receipt.json', 'Receipt outside exact phase session')
        _require(start['member_sequence'] <= len(authority.records) and start['member_record_sha256'] ==
                 (authority.records[start['member_sequence'] - 1]['record_sha256'] if start['member_sequence'] else acquisition._EMPTY_HASH),
                 'Phase start member head differs from journal prefix')
        proof_state = receipt['state']
        if result['status'] == 'failed':
            prior = acquisition._initial_state()
            for record in authority.records[:start['member_sequence']]:
                acquisition._apply_record(prior, record, authority.targets, authority.policies, job_contract=member['job']['contract'])
            _require(proof_state['failures'] > prior['failures'] and result['guard'] == proof_state['guard'],
                     'Failed phase lacks current member failure/guard evidence')
            return
        refs = {t['target_key']: proof_state['sources'][t['target_key']] for t in member['job']['targets']
                if t['target_key'] in proof_state['sources']}
        _require(len(refs) == 2, 'Metadata source proof incomplete')
        cadaster = next(t for t in member['job']['targets'] if t['role'] == 'cadaster')
        body, _ = acquisition._authenticated(refs[cadaster['target_key']], expected=cadaster)
        acquisition._cadaster(body, member['period'])
        resolved = acquisition.resolve_sources(member['job'], refs)
        checkpoint = _read(result['checkpoint'])
        if start['phase'] == 'metadata':
            _require(result['checkpoint']['path'] == start['session'] + '/checkpoint-a.json', 'Checkpoint A outside phase session')
            _same(checkpoint, resolved['checkpoints'][0], 'Checkpoint A differs from current native sources')
            if batch.bundle['contract'] == 'financial-acquisition-batch-v2':
                raw = _path(start['session'] + '/resolution.json').read_bytes()
                _require(raw == _canonical(resolved), 'Historical physical resolution differs from own native dictionary')
        else:
            metadata = next(p for p in batch.state['finished'].values() if p['period'] == member['period'] and p['phase'] == 'metadata')
            a = metadata['result']['checkpoint']
            _same(_read(a), resolved['checkpoints'][0], 'Metadata checkpoint changed before values')
            for target in resolved['numeric_targets']:
                _require(target['target_key'] in proof_state['sources'], 'Numeric source proof incomplete')
                body, _ = acquisition._authenticated(proof_state['sources'][target['target_key']], expected=target)
                origins = [n['origin'] for r in resolved['resolutions'] for n in r['nodes']
                           if n['kind'] == 'numeric' and n['origin']['area'] == target['area']]
                acquisition.validate_numeric_source(body, area=target['area'], required_origins=origins)
            projection = ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'manifest_path',
                          'manifest_sha256', 'body_sha256', 'provenance_sha256')
            expected = {**resolved['checkpoints'][0], 'phase': 'complete', 'checkpoint_a_sha256': a['sha256'],
                        'sources': sorted(resolved['checkpoints'][0]['sources'] +
                          [{key: proof_state['sources'][t['target_key']][key] for key in projection}
                           for t in resolved['numeric_targets']], key=lambda ref: ref['source_id'])}
            _require(result['checkpoint']['path'] == start['session'] + '/checkpoint-b.json', 'Checkpoint B outside phase session')
            _same(checkpoint, expected, 'Checkpoint B differs from native accepted sources')


def _totals(batch):
    members = []
    for member in batch.bundle['members']:
        with acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=_MemberContext(batch, member)) as authority:
            members.append({'period': member['period'], 'sequence': len(authority.records),
                            'pending_attempts': len(authority.state['pending']), **{key: authority.state[key] for key in _COUNTERS}})
    return {'contract': 'financial-acquisition-batch-state-v1', 'status': 'halted' if batch.halted else
            'pending' if batch.state['pending'] else 'verified', 'halt': batch.halted,
            'bundle_sha256': batch.pin, 'bootstrap_sha256': batch.bootstrap_pin, 'sequence': len(batch.records),
            'members': members, 'totals': {key: sum(m[key] for m in members) for key in _COUNTERS},
            'pending_phases': list(batch.state['pending']), 'finished_phases': list(batch.state['finished'])}


def _finished_proofs(batch):
    for start in batch.state['finished'].values():
        _proof(batch, start, start['result'], current=False)
    original = batch.state.get('representative_measurement')
    if original is not None and original['phase_id'] in batch.state['finished']:
        _original_representative_measurement(batch, batch.state['finished'][original['phase_id']])
    if 'representative_checkpoint' in batch.state:
        _verify_representative_checkpoint(batch)


def _verify_batch(bundle_path: Path, bundle_sha256: str, *, bootstrap_sha256: str) -> dict:
    with _open_batch(bundle_path, bundle_sha256, bootstrap_sha256) as batch:
        _finished_proofs(batch)
        return _totals(batch)


def _reconcile(batch):
    try:
        _finished_proofs(batch)
    except (ValueError, OSError, KeyError) as error:
        batch.halt('finished_phase_unproven: ' + str(error))
        return
    unfinished = list(batch.state['pending'].values())
    if not unfinished or batch.halted:
        return
    results = []
    for start in unfinished:
        member = next(m for m in batch.bundle['members'] if m['period'] == start['period'])
        context = _MemberContext(batch, member)
        try:
            with acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=context, recover=True) as authority:
                if authority.state['pending']:
                    acquisition._recover_pending(authority)  # retained orphan reservations; no refund
                    raise ValueError('Unfinished member attempt; terminal phase outcome unproven')
            terminal = _ROOT / start['session'] / 'terminal.json'
            if terminal.exists():
                result = _json(_path(terminal.relative_to(_ROOT).as_posix()).read_bytes())
            else:
                receipt = _ROOT / start['session'] / 'receipt.json'
                checkpoint = _ROOT / start['session'] / ('checkpoint-a.json' if start['phase'] == 'metadata' else 'checkpoint-b.json')
                result = {'contract': 'financial-acquisition-phase-result-v1', 'status': 'complete', 'guard': '', 'error': '',
                          'receipt': _reference(receipt.relative_to(_ROOT).as_posix(), _sha(_path(receipt.relative_to(_ROOT).as_posix()).read_bytes())),
                          'checkpoint': _reference(checkpoint.relative_to(_ROOT).as_posix(), _sha(_path(checkpoint.relative_to(_ROOT).as_posix()).read_bytes()))}
            _proof(batch, start, result)
            results.append((start, result))
        except (ValueError, OSError, KeyError) as error:
            batch.halt('recovery_unproven: ' + str(error))
            return
    if len(unfinished) > 1 and any(result['status'] != 'complete' for _, result in results):
        batch.halt('recovered_phase_order_unprovable')
        return
    for start, result in results:
        terminal = _ROOT / start['session'] / 'terminal.json'
        if not terminal.exists():
            acquisition._write_exclusive(terminal, result)
        batch.append('phase_finish', phase_id=start['phase_id'], result=result, recovered=True)


def _recover_batch(bundle_path: Path, bundle_sha256: str, *, bootstrap_sha256: str, output: Path) -> dict:
    destination = acquisition._safe_destination(output)
    _require(not destination.exists(), 'Recovery output must be new')
    # Immutable authentication happens before any recovery write. If valid immutable
    # binding exists but mutable evidence is damaged, persist a separate halt marker.
    bundle = _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256, require_binding=False)
    try:
        with _open_batch(bundle_path, bundle_sha256, bootstrap_sha256, recover=True) as batch:
            _reconcile(batch)
            result = _totals(batch)
    except (ValueError, OSError, KeyError) as error:
        _, lock = _batch_paths(bundle['scope'])
        with acquisition._claim(lock):
            _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256, require_binding=False)
            batch = _Batch(bundle, bundle_sha256, bootstrap_sha256, [], _ledger_state())
            try:
                reason = batch.halt('mutable_evidence_unproven: ' + str(error))
                result = {'contract': 'financial-acquisition-batch-recovery-v1', 'status': 'halted', 'halt': reason,
                          'bundle_sha256': bundle_sha256, 'bootstrap_sha256': bootstrap_sha256}
            finally:
                batch.active = False
    destination.parent.mkdir(parents=True, exist_ok=True)
    acquisition._write_exclusive(destination, result)
    return result


def _start_phase(batch, member, phase):
    _require(not batch.halted and set(batch.state['pending']) <= batch.inflight,
             'Reconcile all unfinished starts before dispatch')
    with acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=_MemberContext(batch, member)) as authority:
        _require(not authority.state['pending'], 'Member pending reservations block phase dispatch')
        identity = uuid.uuid4().hex
        start = batch.append('phase_start', phase_id=identity, period=member['period'], phase=phase,
                            session=member['session_root'] + '/' + phase + '-' + identity,
                            job_sha256=member['job_sha256'], member_bootstrap_sha256=member['bootstrap_sha256'],
                            member_sequence=len(authority.records), member_record_sha256=authority.records[-1]['record_sha256']
                            if authority.records else acquisition._EMPTY_HASH)
        batch.inflight.add(identity)
        return start


def _run_serial(bundle_path: Path, bundle_sha256: str, *, bootstrap_sha256: str, phase_callable) -> dict:
    """Offline test seam; Task3 supplies a contained terminal phase executor."""
    _require(callable(phase_callable), 'Terminal phase callable required')
    _require(_immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256)['contract'] == 'financial-acquisition-batch-v1',
             'Historical execution requires current resource gate and fixed executor')
    with _open_batch(bundle_path, bundle_sha256, bootstrap_sha256, recover=True) as batch:
        _reconcile(batch)
        if batch.halted:
            return _totals(batch)
        for phase in ('metadata', 'values'):
            for member in batch.bundle['members']:
                if any(p['period'] == member['period'] and p['phase'] == phase for p in batch.state['finished'].values()):
                    continue
                if phase == 'values' and not any(p['period'] == member['period'] and p['phase'] == 'metadata'
                         and p['result']['status'] == 'complete' for p in batch.state['finished'].values()):
                    continue
                start = _start_phase(batch, member, phase)
                try:
                    result = phase_callable(copy.deepcopy(member), copy.deepcopy(start), _MemberContext(batch, member))
                    _proof(batch, start, result)
                    acquisition._write_exclusive(_ROOT / start['session'] / 'terminal.json', result)
                    batch.append('phase_finish', phase_id=start['phase_id'], result=result, recovered=False)
                except (ValueError, OSError, KeyError) as error:
                    batch.halt('phase_outcome_unproven: ' + str(error))
                if batch.halted:
                    return _totals(batch)
        return _totals(batch)



def _worker_context(job, context):
    """Read only immutable pins and the committed start prefix, never live batch head."""
    _require(type(context) is dict and set(context) == {'contract', 'bundle_path', 'bundle_sha256',
             'bootstrap_sha256', 'period', 'start_sequence', 'start_sha256'}
             and context['contract'] in ('financial-acquisition-worker-context-v2', 'financial-acquisition-worker-context-v3'), 'Invalid worker batch context')
    for key in ('bundle_sha256', 'bootstrap_sha256', 'start_sha256'):
        acquisition._digest(context[key])
    _require(type(context['period']) is int and context['period'] in (_ACQUIRE if context['contract'].endswith('-v2') else [m['period'] for m in _HISTORICAL_POLICY_V1['members']])
             and type(context['start_sequence']) is int and context['start_sequence'] > 0, 'Invalid worker start identity')
    path = _path(context['bundle_path'])
    raw = path.read_bytes()
    _require(_sha(raw) == context['bundle_sha256'], 'Worker bundle physical pin mismatch')
    bundle = _json(raw)
    _require((bundle.get('contract') == 'financial-acquisition-batch-v2') == context['contract'].endswith('-v3'), 'Worker version differs from bundle')
    batch = _Batch(bundle, context['bundle_sha256'], context['bootstrap_sha256'], [], _ledger_state())
    _require(context['bundle_path'] == batch.binding['bundle_path'], 'Worker bundle path differs')
    _bound_bytes(batch)
    _bundle_code_identity(bundle, current_head=True)
    member = next(m for m in bundle['members'] if m['period'] == context['period'])
    _authorize_member(job, _MemberContext(batch, member))
    previous, state, start = acquisition._EMPTY_HASH, _ledger_state(), None
    with _path(bundle['destination'] + '/journal.jsonl').open('rb') as stream:
        for sequence in range(1, context['start_sequence'] + 1):
            line = stream.readline()
            _require(line.endswith(b'\n'), 'Worker start prefix missing or partial')
            record = _json(line)
            pin = record.pop('record_sha256')
            _require(pin == _sha(_canonical(record)) and record['sequence'] == sequence
                     and record['previous_record_sha256'] == previous and record['bundle_sha256'] == batch.pin
                     and record['bootstrap_sha256'] == batch.bootstrap_pin, 'Worker start prefix integrity failure')
            _apply_phase(state, record, bundle)
            previous, start = pin, record
    _require(previous == context['start_sha256'] and start['kind'] == 'phase_start'
             and start['period'] == member['period'] and start['job_sha256'] == job['job_sha256'],
             'Worker phase start pin/member mismatch')
    return member, start


def _transport_context(context):
    _authorize_member(context.member['job'], context)
    start = context.start
    return {'contract': ('financial-acquisition-worker-context-v3' if context.batch.bundle['contract'] == 'financial-acquisition-batch-v2' else 'financial-acquisition-worker-context-v2'),
            'bundle_path': context.batch.binding['bundle_path'], 'bundle_sha256': context.batch.pin,
            'bootstrap_sha256': context.batch.bootstrap_pin, 'period': context.member['period'],
            'start_sequence': start['sequence'], 'start_sha256': start['record_sha256']}


def _run_phase(member, start, context):
    metadata = None if start['phase'] == 'metadata' else next(
        p for p in context.batch.state['finished'].values()
        if p['period'] == member['period'] and p['phase'] == 'metadata')
    kwargs = {} if start['phase'] == 'metadata' else {
        'resume_from': _path(metadata['result']['receipt']['path']),
        'resume_sha256': metadata['result']['receipt']['sha256'],
        'checkpoint_sha256': metadata['result']['checkpoint']['sha256']}
    error = ''
    try:
        acquisition._run_acquisition(_path(member['job_path']), member['job_sha256'], _ROOT / start['session'],
            phase=start['phase'], bootstrap_sha256=member['bootstrap_sha256'], coordinator=context, **kwargs)
    except (ValueError, OSError, RuntimeError) as failure:
        error = type(failure).__name__ + ': ' + str(failure)
    receipt_path = _path(start['session'] + '/receipt.json')
    receipt = _json(receipt_path.read_bytes())
    def ref(path):
        return {'path': path.relative_to(_ROOT).as_posix(), 'sha256': _sha(path.read_bytes())}
    checkpoint = _ROOT / start['session'] / ('checkpoint-a.json' if start['phase'] == 'metadata' else 'checkpoint-b.json')
    return {'contract': 'financial-acquisition-phase-result-v1', 'status': 'failed' if error else 'complete',
            'guard': receipt['state']['guard'] if error else '', 'error': error, 'receipt': ref(receipt_path),
            'checkpoint': None if error else ref(checkpoint)}


def _run_summary(batch):
    result = _totals(batch)
    complete = {p['period'] for p in batch.state['finished'].values()
                if p['phase'] == 'values' and p['result']['status'] == 'complete'}
    missing = sorted(set(batch.bundle['acquire_periods']) - complete)
    return {**result, 'contract': 'financial-acquisition-batch-run-v1',
            'status': 'halted' if batch.halted else 'incomplete' if missing else 'complete',
            'missing_periods': missing, 'complete_periods': sorted(complete),
            **({'representative_checkpoint': copy.deepcopy(batch.state['representative_checkpoint'])}
               if 'representative_checkpoint' in batch.state else {})}


def _run_scheduler(bundle_path, bundle_sha256, *, bootstrap_sha256, metadata_workers, phase_callable, resource_profile=None, resource_profile_ref=None, stage_mode=None):
    from concurrent.futures import ThreadPoolExecutor
    from queue import Queue
    from threading import Event
    _require(type(metadata_workers) is int and metadata_workers in (1, 2), 'Metadata workers must be 1 or 2')
    candidate = _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256)
    if candidate['contract'] == 'financial-acquisition-batch-v2':
        _require(resource_profile is not None and metadata_workers == 1 and phase_callable is _run_phase
                 and type(stage_mode) is str and stage_mode in ('representative', 'remaining')
                 and type(resource_profile_ref) is dict,
                 'Historical execution requires current serial resource gate and fixed executor')
    else:
        _require(resource_profile is None and stage_mode is None, 'Historical resource profile cannot authorize legacy batch')
    with _open_batch(bundle_path, bundle_sha256, bootstrap_sha256, recover=resource_profile is None) as batch:
        if resource_profile is None:
            _reconcile(batch)
        else:
            _require(not batch.state['pending'], 'Historical pending phases require explicit conservative recovery')
            _finished_proofs(batch)
        if batch.halted:
            return _run_summary(batch)
        _bundle_code_identity(batch.bundle, current_head=True)
        representative = next((p for p in batch.state['finished'].values() if p['phase'] == 'values'
            and p['period'] == batch.bundle['acquire_periods'][0] and p['result']['status'] == 'complete'), None)
        if stage_mode is not None and representative is not None:
            _original_representative_measurement(batch, representative, resource_profile_ref=resource_profile_ref)
        if stage_mode == 'remaining':
            _verify_representative_checkpoint(batch, resource_profile_ref=resource_profile_ref)
        cancelled, completed = Event(), Queue()
        pool = ThreadPoolExecutor(max_workers=metadata_workers)
        monitor = None
        try:
            if resource_profile is not None:
                from .windows_acquisition import _ResourceMonitor
                monitor = _ResourceMonitor(resource_profile, batch.folder, cancelled)
                monitor.__enter__()
            for phase in ('metadata', 'values'):
                candidates = [m for m in batch.bundle['members']
                    if not any(p['period'] == m['period'] and p['phase'] == phase for p in batch.state['finished'].values())
                    and (phase == 'metadata' or any(p['period'] == m['period'] and p['phase'] == 'metadata'
                        and p['result']['status'] == 'complete' for p in batch.state['finished'].values()))]
                if stage_mode == 'representative' and phase == 'values':
                    candidates = [m for m in candidates if m['period'] == batch.bundle['acquire_periods'][0]]
                active = {}
                while active or candidates and not batch.halted:
                    while candidates and not batch.halted and not cancelled.is_set() and len(active) < (metadata_workers if phase == 'metadata' else 1):
                        member = candidates.pop(0)
                        start = _start_phase(batch, member, phase)
                        context = _MemberContext(batch, member)
                        context.start, context.cancel_event = copy.deepcopy(start), cancelled
                        context.monitor = monitor
                        future = pool.submit(phase_callable, copy.deepcopy(member), copy.deepcopy(start), context)
                        active[future] = start
                        future.add_done_callback(completed.put)
                    if monitor is not None and monitor.error:
                        batch.halt('critical_monitor_failure: ' + monitor.error)
                    if not active:
                        break
                    future = completed.get()
                    start = active.pop(future)
                    try:
                        result = future.result()
                        _proof(batch, start, result)
                        acquisition._write_exclusive(_ROOT / start['session'] / 'terminal.json', result)
                        if stage_mode is not None and start['phase'] == 'values' and start['period'] == batch.bundle['acquire_periods'][0] and result['status'] == 'complete':
                            monitor.sample()
                            measurement = {**_representative_measurement_identity(batch, start, result),
                                'resource_profile': copy.deepcopy(resource_profile_ref),
                                'measurements': {'sample_count': monitor.sample_count, 'peaks': dict(monitor.peaks),
                                                 'minimum_free': dict(monitor.minimum_free)}}
                            path = _ROOT / start['session'] / 'resource-measurement.json'
                            acquisition._write_exclusive(path, measurement)
                            ref = {'path': path.relative_to(_ROOT).as_posix(), 'sha256': _sha(path.read_bytes())}
                            batch.append('representative_measurement', phase_id=start['phase_id'], resource_measurement=ref)
                        batch.append('phase_finish', phase_id=start['phase_id'], result=result, recovered=False)
                    except (ValueError, OSError, RuntimeError) as error:
                        batch.halt('phase_outcome_unproven: ' + str(error))
                        cancelled.set()
                if batch.halted:
                    break
            # Reauthenticate outer immutable inputs/reuse and all native completed proofs.
            _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256)
            _finished_proofs(batch)
            if stage_mode == 'representative' and not batch.halted:
                representative = batch.bundle['acquire_periods'][0]
                values = next((p for p in batch.state['finished'].values() if p['phase'] == 'values'
                               and p['period'] == representative and p['result']['status'] == 'complete'), None)
                if values is not None and 'representative_checkpoint' not in batch.state:
                    original = _original_representative_measurement(batch, values, resource_profile_ref=resource_profile_ref)
                    batch.append('representative_checkpoint', representative_period=representative,
                        phase_id=values['phase_id'], result=copy.deepcopy(values['result']),
                        resource_measurement=copy.deepcopy(batch.state['representative_measurement']['resource_measurement']),
                        resource_profile=copy.deepcopy(original['resource_profile']), measurements=copy.deepcopy(original['measurements']))
                if 'representative_checkpoint' in batch.state:
                    _verify_representative_checkpoint(batch, resource_profile_ref=resource_profile_ref)
            result = _run_summary(batch)
            if stage_mode is not None:
                result['stage_mode'] = stage_mode
                if stage_mode == 'representative' and 'representative_checkpoint' in batch.state and not batch.halted:
                    result['status'] = 'representative_checkpoint'
            if monitor is not None:
                result['resource_samples'] = copy.deepcopy(monitor.samples)
                result['resource_sample_count'] = monitor.sample_count
                result['resource_peaks'] = dict(monitor.peaks)
                result['resource_minimum_free'] = dict(monitor.minimum_free)
            return result
        except (ValueError, OSError, RuntimeError) as error:
            cancelled.set()
            batch.halt(('critical_monitor_failure: ' if monitor is not None and monitor.error else 'coordinator_failure: ') + str(error))
            raise
        finally:
            cancelled.set()
            pool.shutdown(wait=True, cancel_futures=True)
            if monitor is not None:
                if monitor.error:
                    batch.halt('critical_monitor_failure: ' + monitor.error)
                monitor.__exit__(None, None, None)


def _run_batch(bundle_path: Path, bundle_sha256: str, *, bootstrap_sha256: str, metadata_workers: int = 1) -> dict:
    return _run_scheduler(bundle_path, bundle_sha256, bootstrap_sha256=bootstrap_sha256,
                          metadata_workers=metadata_workers, phase_callable=_run_phase)


def _bundle_code_identity(bundle, *, current_head=False):
    if bundle.get('contract') == 'financial-acquisition-batch-v2':
        _code_identity_v2(bundle['code_pins'])
    else:
        _code_identity(bundle['code_pins'], current_head=current_head)


def initialize_historical_batch(draft_path, draft_sha256, destination, *, reviewed_code_pins):
    path = _path(Path(draft_path).absolute().relative_to(_ROOT.absolute()).as_posix())
    _file(path, acquisition._digest(draft_sha256))
    _require(_json(path.read_bytes()).get('contract') == 'financial-acquisition-batch-draft-v2',
             'Historical draft v2 required')
    return _initialize_batch(draft_path, draft_sha256, destination, code_pins=reviewed_code_pins)


def verify_historical_batch(bundle_path, bundle_sha256, *, bootstrap_sha256):
    bundle = _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256)
    _require(bundle['contract'] == 'financial-acquisition-batch-v2', 'Historical bundle v2 required')
    with _open_batch(bundle_path, bundle_sha256, bootstrap_sha256) as batch:
        _finished_proofs(batch)
        return _run_summary(batch)


def run_historical_batch(bundle_path, bundle_sha256, *, bootstrap_sha256,
                         resource_profile_path, resource_profile_sha256, stage_mode='representative'):
    _require(type(stage_mode) is str and stage_mode in ('representative', 'remaining'), 'Closed historical stage mode required')
    from .windows_acquisition import _resource_profile
    name = Path(resource_profile_path).absolute().relative_to(_ROOT.absolute()).as_posix()
    _require(name.startswith('data/runs/'), 'Resource profile outside approved runs')
    profile = _resource_profile(_read(_reference(name, acquisition._digest(resource_profile_sha256))))
    bundle = _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256)
    _require(bundle['contract'] == 'financial-acquisition-batch-v2', 'Historical bundle v2 required')
    global_lock = acquisition._safe_destination(_ROOT / 'data/runs/financial-acquisition-authority/historical-active-window.lock')
    with acquisition._claim(global_lock):
        return _run_scheduler(bundle_path, bundle_sha256, bootstrap_sha256=bootstrap_sha256,
                              metadata_workers=1, phase_callable=_run_phase, resource_profile=profile,
                              resource_profile_ref=_reference(name, resource_profile_sha256), stage_mode=stage_mode)


def export_historical_sources(bundle_path, bundle_sha256, *, bootstrap_sha256, output):
    bundle = _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256)
    _require(bundle['contract'] == 'financial-acquisition-batch-v2', 'Historical bundle v2 required')
    output = acquisition._safe_destination(output)
    _require(not output.exists(), 'Historical export destination must be new')
    with _open_batch(bundle_path, bundle_sha256, bootstrap_sha256) as batch:
        _finished_proofs(batch)
        summary = _run_summary(batch)
        _require(summary['status'] == 'complete' and not batch.state['pending']
                 and all(m['pending_attempts'] == 0 for m in summary['members']), 'Historical sources must be complete')
        members = []
        for member in bundle['members']:
            phases = {p['phase']: p for p in batch.state['finished'].values() if p['period'] == member['period']}
            a, b = phases['metadata']['result'], phases['values']['result']
            checkpoint = _read(b['checkpoint'])
            members.append({'period': member['period'], 'selection': member['job']['descriptors'][0]['selection'],
                'job_path': member['job_path'], 'job_file_sha256': member['job_file_sha256'],
                'job_sha256': member['job_sha256'], 'bootstrap_sha256': member['bootstrap_sha256'],
                'checkpoint_a': a['checkpoint'], 'checkpoint_b': b['checkpoint'],
                'metadata_receipt': a['receipt'], 'receipt': b['receipt'],
                'resolution': _reference(phases['metadata']['session'] + '/resolution.json',
                    _sha(_path(phases['metadata']['session'] + '/resolution.json').read_bytes())),
                'sources': checkpoint['sources'], 'phases': copy.deepcopy(phases)})
        handoff = {'contract': acquisition.SOURCES_CONTRACT, 'phase': 'complete',
            'scope': bundle['scope'], 'window_id': bundle['window_id'],
            'policy_sha256': bundle['policy_sha256'], 'members': members,
            'execution': {'bundle': batch.binding, 'head': batch.head(), 'summary': summary,
                          'code_pins': bundle['code_pins']}}
        output.parent.mkdir(parents=True, exist_ok=True)
        acquisition._write_exclusive(output, handoff)
        return {'status': 'exported', 'path': output.relative_to(_ROOT).as_posix(),
                'sha256': _sha(output.read_bytes()), 'periods': bundle['acquire_periods']}


def _representative_measurement_identity(batch, start, result):
    member = next(m for m in batch.bundle['members'] if m['period'] == start['period'])
    with acquisition._open_authority(member['job'], member['bootstrap_sha256'], coordinator=_MemberContext(batch, member)) as authority:
        receipt = _read(result['receipt'])
        acquisition._verify_receipt(receipt, authority)
        records = authority.records[start['member_sequence']:receipt['sequence']]
        attempts = [copy.deepcopy(r) for r in records if r['kind'] in ('reserve', 'identity', 'finish')]
        reserved = {r['attempt_id'] for r in attempts if r['kind'] == 'reserve'}
        _require(reserved and reserved == {r['attempt_id'] for r in attempts if r['kind'] == 'identity'}
                 and reserved == {r['attempt_id'] for r in attempts if r['kind'] == 'finish'}
                 and all(r['session_id'] == Path(start['session']).name for r in attempts)
                 and all(r['tree_extinct'] is True for r in attempts if r['kind'] == 'finish'),
                 'Original representative measurement lacks authenticated reservation/worker/extinction proof')
    return {'contract': 'financial-acquisition-representative-measurement-v1',
        'bundle_sha256': batch.pin, 'bootstrap_sha256': batch.bootstrap_pin,
        'code_pins': copy.deepcopy(batch.bundle['code_pins']),
        'phase': {key: start[key] for key in ('phase_id', 'period', 'phase', 'session', 'job_sha256',
            'member_bootstrap_sha256', 'member_sequence', 'member_record_sha256')},
        'result': copy.deepcopy(result), 'attempt_records': attempts}


def _original_representative_measurement(batch, terminal, *, resource_profile_ref=None):
    anchor = batch.state.get('representative_measurement')
    _require(anchor is not None and anchor['phase_id'] == terminal['phase_id'],
             'Original representative measurement missing; capacity/remaining unavailable without reGET')
    proof = _read(anchor['resource_measurement'])
    expected = _representative_measurement_identity(batch, terminal, terminal['result'])
    _require(type(proof) is dict and set(proof) == set(expected) | {'resource_profile', 'measurements'},
             'Invalid closed original representative measurement')
    _same({key: proof[key] for key in expected}, expected, 'Original representative phase/reservation/pins differ')
    from .windows_acquisition import _resource_profile
    profile = _resource_profile(_read(proof['resource_profile']))
    measurements = proof['measurements']
    _require(type(measurements) is dict and set(measurements) == {'sample_count', 'peaks', 'minimum_free'}
             and type(measurements['sample_count']) is int and measurements['sample_count'] > 0,
             'Original representative sample count missing')
    for key, fields in (('peaks', {'tree_working_set_bytes', 'tree_private_bytes'}),
                        ('minimum_free', {'free_physical_bytes', 'free_commit_bytes', 'free_disk_bytes'})):
        _require(type(measurements[key]) is dict and set(measurements[key]) == fields
                 and all(type(v) is int and v >= 0 for v in measurements[key].values()), 'Invalid original representative measurements')
    for key in ('physical', 'commit', 'disk'):
        _require(measurements['minimum_free']['free_' + key + '_bytes'] >= profile['min_free_' + key + '_bytes'],
                 'Original representative measurement below pinned resource margin')
    if resource_profile_ref is not None:
        _same(resource_profile_ref, proof['resource_profile'], 'Resource profile must match original representative measurement')
    return copy.deepcopy(proof)


def _verify_representative_checkpoint(batch, *, resource_profile_ref=None):
    checkpoint = batch.state.get('representative_checkpoint')
    _require(batch.bundle['contract'] == 'financial-acquisition-batch-v2' and checkpoint is not None,
             'Remaining execution requires completed authenticated representative checkpoint')
    terminal = batch.state['finished'].get(checkpoint['phase_id'])
    _require(terminal is not None and terminal['period'] == batch.bundle['acquire_periods'][0]
             and terminal['phase'] == 'values' and terminal['result']['status'] == 'complete',
             'Representative checkpoint terminal proof missing')
    original = _original_representative_measurement(batch, terminal, resource_profile_ref=resource_profile_ref)
    _same(checkpoint['resource_measurement'], batch.state['representative_measurement']['resource_measurement'], 'Representative original measurement reference differs')
    _same(checkpoint['measurements'], original['measurements'], 'Representative checkpoint differs from original measurements')
    _same(checkpoint['resource_profile'], original['resource_profile'], 'Representative checkpoint differs from original profile')
    from .windows_acquisition import _resource_profile
    profile = _resource_profile(_read(checkpoint['resource_profile']))
    for key in ('physical', 'commit', 'disk'):
        _require(checkpoint['measurements']['minimum_free']['free_' + key + '_bytes'] >= profile['min_free_' + key + '_bytes'],
                 'Representative measurement below pinned resource margin')
    if resource_profile_ref is not None:
        _same(resource_profile_ref, checkpoint['resource_profile'], 'Remaining resource profile must match reviewed representative checkpoint')
    return copy.deepcopy(checkpoint)

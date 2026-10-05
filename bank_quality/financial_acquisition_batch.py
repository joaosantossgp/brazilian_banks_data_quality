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


def _path(name):
    """Authenticate every ancestor without resolving a symlink/reparse first."""
    _require(type(name) is str and name and '\\' not in name and ':' not in name
             and all(p not in ('', '.', '..') for p in name.split('/')), 'Path escape or absolute path')
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


def _batch_paths():
    base = acquisition._safe_destination(_ROOT / 'data/runs/financial-acquisition-authority')
    stem = 'batch-scope-' + _sha(_SCOPE.encode())
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
    return {**copy.deepcopy(draft), 'contract': 'financial-acquisition-batch-v1', 'members': members,
            'destination': destination, 'code_pins': copy.deepcopy(pins), 'executable': True}


def _batch_bootstrap(bundle, pin):
    return {'contract': 'financial-acquisition-batch-bootstrap-v1', 'scope': _SCOPE,
            'bundle_sha256': pin, 'destination': bundle['destination'],
            'members': [{key: m[key] for key in ('period', 'job_sha256', 'job_file_sha256',
                                                 'job_path', 'authority_path', 'bootstrap_sha256')} for m in bundle['members']],
            'policies': bundle['policies'], 'caps': bundle['caps'], 'code_pins': bundle['code_pins']}


def _binding(bundle, pin, bootstrap_pin):
    return {'contract': 'financial-acquisition-batch-binding-v1', 'scope': _SCOPE,
            'bundle_path': bundle['destination'] + '/bundle.json', 'bundle_sha256': pin,
            'bootstrap_sha256': bootstrap_pin}


def _immutable_batch(bundle_path, bundle_pin, bootstrap_pin, *, require_binding=True):
    path = _path(Path(bundle_path).absolute().relative_to(_ROOT.absolute()).as_posix())
    _file(path, bundle_pin)
    bundle = _json(path.read_bytes())
    fields = {'contract', 'scope', 'selection', 'acquire_periods', 'reuse_periods', 'catalogs', 'members',
              'reuse', 'policies', 'caps', 'executable', 'destination', 'code_pins'}
    _require(type(bundle) is dict and set(bundle) == fields and type(bundle['members']) is list, 'Invalid bundle schema')
    member_fields = {'period', 'job', 'job_sha256', 'session_root', 'job_path', 'job_file_sha256', 'authority_path', 'bootstrap_sha256'}
    _require(all(type(m) is dict and set(m) == member_fields for m in bundle['members']), 'Invalid bundle member schema')
    _code_identity(bundle['code_pins'])
    draft = {key: copy.deepcopy(bundle[key]) for key in fields - {'destination', 'code_pins'}}
    draft.update(contract='financial-acquisition-batch-draft-v1', executable=False,
                 members=[{key: m[key] for key in ('period', 'job', 'job_sha256', 'session_root')} for m in bundle['members']])
    draft = _verify_draft(draft)
    destination = acquisition._safe_destination(_ROOT / bundle['destination'])
    _require(destination.relative_to(_ROOT).as_posix() == bundle['destination']
             and path == destination / 'bundle.json', 'Bundle destination/path differs')
    _same(bundle, _build_bundle(draft, bundle['destination'], bundle['code_pins']), 'Bundle differs from closed draft/bindings')
    bootstrap = _batch_bootstrap(bundle, bundle_pin)
    _file(destination / 'bootstrap.json', bootstrap_pin)
    _same(_json((destination / 'bootstrap.json').read_bytes()), bootstrap, 'Batch bootstrap identity mismatch')
    binding, _ = _batch_paths()
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
    _code_identity(batch.bundle['code_pins'])
    path = _path(batch.binding['bundle_path'])
    _file(path, batch.pin)
    _same(_json(path.read_bytes()), batch.bundle, 'Active bundle bytes changed')
    bootstrap_path = _path(batch.bundle['destination'] + '/bootstrap.json')
    _file(bootstrap_path, batch.bootstrap_pin)
    _same(_json(bootstrap_path.read_bytes()), _batch_bootstrap(batch.bundle, batch.pin), 'Active bootstrap changed')
    binding, _ = _batch_paths()
    _same(_json(_path(binding.relative_to(_ROOT).as_posix()).read_bytes()), batch.binding, 'Immutable batch scope binding mismatch')


def _initialize_batch(draft_path: Path, draft_sha256: str, destination: Path, *, code_pins: dict) -> dict:
    path = _path(Path(draft_path).absolute().relative_to(_ROOT.absolute()).as_posix())
    _file(path, draft_sha256)
    draft = _verify_draft(_json(path.read_bytes()))
    _code_identity(code_pins, current_head=True)
    destination = acquisition._safe_destination(destination)
    _require(not destination.exists(), 'Batch destination must be new')
    name = destination.relative_to(_ROOT).as_posix()
    bundle = _build_bundle(draft, name, code_pins)
    pin = _sha(_canonical(bundle))
    bootstrap = _batch_bootstrap(bundle, pin)
    bootstrap_pin = _sha(_canonical(bootstrap))
    binding_path, lock = _batch_paths()
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
              if kind == 'phase_start' else {'phase_id', 'result', 'recovered'} if kind == 'phase_finish' else {'reason'})
    _require(type(record) is dict and set(record) == base | fields and record['contract'] == 'financial-acquisition-batch-ledger-v1'
             and type(record['sequence']) is int and record['sequence'] > 0 and kind in ('phase_start', 'phase_finish', 'halt'),
             'Invalid closed phase record')
    if kind == 'phase_start':
        _require(not state['halt'] and type(record['period']) is int and record['period'] in _ACQUIRE
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
            _require({p['period'] for p in state['finished'].values() if p['phase'] == 'metadata'} == set(_ACQUIRE),
                     'Values require terminal metadata barrier for seven members')
            _require(any(p['period'] == record['period'] and p['phase'] == 'metadata' and p['result']['status'] == 'complete'
                         for p in state['finished'].values()) and not state['pending'], 'Values require completed metadata and serial values')
        else:
            _require(not any(p['phase'] == 'values' for p in state['pending'].values()) and len(state['pending']) < 2,
                     'Metadata concurrency exceeds approved two slots')
        state['pending'][record['phase_id']] = copy.deepcopy(record)
    elif kind == 'phase_finish':
        _require(record['phase_id'] in state['pending'] and type(record['recovered']) is bool, 'Unknown phase conclusion')
        result = record['result']
        _result_schema(result)
        start = state['pending'].pop(record['phase_id'])
        state['finished'][record['phase_id']] = {**start, 'result': copy.deepcopy(result)}
        guard = result['guard'] if result['guard'] in ('integrity', 'schema', 'deadline') else ''
        state['guard_streak'] = (state['guard_streak'] + 1 if guard == state['guard'] else 1) if guard else 0
        state['guard'] = guard
        if state['guard_streak'] >= bundle['policies']['max_guard_streak']:
            state['halt'] = 'consecutive_guard'
        failed = {p['period'] for p in state['finished'].values() if p['result']['status'] == 'failed'}
        if len(failed) >= 3:
            state['halt'] = state['halt'] or 'three_failed_members'
        if result['guard'] in ('persistence', 'containment'):
            state['halt'] = state['halt'] or 'critical_' + result['guard']
    else:
        _require(type(record['reason']) is str and record['reason'], 'Halt reason required')
        state['halt'] = state['halt'] or record['reason']


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
    binding, lock = _batch_paths()
    _require(lock.is_file(), 'Existing batch claim file required')
    with acquisition._claim(lock):
        # Repeat after claim acquisition to close the supported writer boundary.
        checked = _Batch(bundle, bundle_sha256, bootstrap_sha256, [], _ledger_state())
        _bound_bytes(checked)
        checked.active = False
        folder = _ROOT / bundle['destination']
        raw = _path((folder / 'journal.jsonl').relative_to(_ROOT).as_posix()).read_bytes()
        _require(not raw or raw.endswith(b'\n'), 'Partial batch journal tail; never truncate')
        records, state, heads = [], _ledger_state(), []
        initial = {'sequence': 0, 'record_sha256': acquisition._EMPTY_HASH, 'state_sha256': _sha(_canonical(state))}
        heads.append(initial)
        for line in raw.splitlines():
            record = _json(line)
            _require(type(record) is dict and 'record_sha256' in record, 'Invalid phase journal record')
            pin = record.pop('record_sha256')
            _require(pin == _sha(_canonical(record)) and type(record.get('sequence')) is int and record['sequence'] == len(records) + 1
                     and record['previous_record_sha256'] == heads[-1]['record_sha256']
                     and record['bundle_sha256'] == bundle_sha256 and record['bootstrap_sha256'] == bootstrap_sha256,
                     'Batch journal chain/pins mismatch')
            _apply_phase(state, record, bundle)
            record['record_sha256'] = pin
            records.append(record)
            heads.append({'sequence': len(records), 'record_sha256': pin, 'state_sha256': _sha(_canonical(state))})
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
            _path(ref['path'])
            acquisition._digest(ref['sha256'])
    _require(result['receipt'] is not None and ((result['status'] == 'complete' and result['checkpoint'] is not None
             and not result['guard'] and not result['error']) or (result['status'] == 'failed' and result['checkpoint'] is None
             and result['error'])), 'Terminal phase status/proofs inconsistent')


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
                acquisition._apply_record(prior, record, authority.targets, authority.policies)
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
        _, lock = _batch_paths()
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
             and context['contract'] == 'financial-acquisition-worker-context-v2', 'Invalid worker batch context')
    for key in ('bundle_sha256', 'bootstrap_sha256', 'start_sha256'):
        acquisition._digest(context[key])
    _require(type(context['period']) is int and context['period'] in _ACQUIRE
             and type(context['start_sequence']) is int and context['start_sequence'] > 0, 'Invalid worker start identity')
    path = _path(context['bundle_path'])
    raw = path.read_bytes()
    _require(_sha(raw) == context['bundle_sha256'], 'Worker bundle physical pin mismatch')
    bundle = _json(raw)
    batch = _Batch(bundle, context['bundle_sha256'], context['bootstrap_sha256'], [], _ledger_state())
    _require(context['bundle_path'] == batch.binding['bundle_path'], 'Worker bundle path differs')
    _bound_bytes(batch)
    _code_identity(bundle['code_pins'], current_head=True)
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
    return {'contract': 'financial-acquisition-worker-context-v2',
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
    missing = sorted(set(_ACQUIRE) - complete)
    return {**result, 'contract': 'financial-acquisition-batch-run-v1',
            'status': 'halted' if batch.halted else 'incomplete' if missing else 'complete',
            'missing_periods': missing, 'complete_periods': sorted(complete)}


def _run_scheduler(bundle_path, bundle_sha256, *, bootstrap_sha256, metadata_workers, phase_callable):
    from concurrent.futures import ThreadPoolExecutor
    from queue import Queue
    from threading import Event
    _require(type(metadata_workers) is int and metadata_workers in (1, 2), 'Metadata workers must be 1 or 2')
    with _open_batch(bundle_path, bundle_sha256, bootstrap_sha256, recover=True) as batch:
        _reconcile(batch)
        if batch.halted:
            return _run_summary(batch)
        _code_identity(batch.bundle['code_pins'], current_head=True)
        cancelled, completed = Event(), Queue()
        pool = ThreadPoolExecutor(max_workers=metadata_workers)
        try:
            for phase in ('metadata', 'values'):
                candidates = [m for m in batch.bundle['members']
                    if not any(p['period'] == m['period'] and p['phase'] == phase for p in batch.state['finished'].values())
                    and (phase == 'metadata' or any(p['period'] == m['period'] and p['phase'] == 'metadata'
                        and p['result']['status'] == 'complete' for p in batch.state['finished'].values()))]
                active = {}
                while active or candidates and not batch.halted:
                    while candidates and not batch.halted and len(active) < (metadata_workers if phase == 'metadata' else 1):
                        member = candidates.pop(0)
                        start = _start_phase(batch, member, phase)
                        context = _MemberContext(batch, member)
                        context.start, context.cancel_event = copy.deepcopy(start), cancelled
                        future = pool.submit(phase_callable, copy.deepcopy(member), copy.deepcopy(start), context)
                        active[future] = start
                        future.add_done_callback(completed.put)
                    if not active:
                        break
                    future = completed.get()
                    start = active.pop(future)
                    try:
                        result = future.result()
                        _proof(batch, start, result)
                        acquisition._write_exclusive(_ROOT / start['session'] / 'terminal.json', result)
                        batch.append('phase_finish', phase_id=start['phase_id'], result=result, recovered=False)
                    except (ValueError, OSError, RuntimeError) as error:
                        batch.halt('phase_outcome_unproven: ' + str(error))
                        cancelled.set()
                if batch.halted:
                    break
            # Reauthenticate outer immutable inputs/reuse and all native completed proofs.
            _immutable_batch(bundle_path, bundle_sha256, bootstrap_sha256)
            _finished_proofs(batch)
            return _run_summary(batch)
        except (ValueError, OSError, RuntimeError) as error:
            cancelled.set()
            batch.halt('coordinator_failure: ' + str(error))
            raise
        finally:
            cancelled.set()
            pool.shutdown(wait=True, cancel_futures=True)


def _run_batch(bundle_path: Path, bundle_sha256: str, *, bootstrap_sha256: str, metadata_workers: int = 1) -> dict:
    return _run_scheduler(bundle_path, bundle_sha256, bootstrap_sha256=bootstrap_sha256,
                          metadata_workers=metadata_workers, phase_callable=_run_phase)

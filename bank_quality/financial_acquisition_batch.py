"""Pure offline composition of one finite native window, never a GET authority.

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

"""Read-only proof of the one completed Issue54 capture, never execution authority.

The installed anchor authenticates historical bytes. Current six-file pins must
be checked by the batch entrypoint before importing this module and are checked
again here. No archived code is imported, and no claim, repair or writer is used.
"""
import copy
import hashlib
from pathlib import Path

from . import financial_acquisition as acquisition
from . import financial_acquisition_batch as batch


_LEGACY54_ANCHOR = {
    'anchor_id': 'recent54-executed-5c025778',
    'executed_commit': '5c0257789a3a6f54f8fbe98f95cef4eb4a68cf75',
    'bundle_path': 'data/runs/financial-historical-acquisition-202312-202606-20261005/bundle.json',
    'bundle_sha256': '557e4fbc22b552c4ec3179d39560c17d6c0ea8ec4102c971f602705a1a25c890',
    'bootstrap_path': 'data/runs/financial-historical-acquisition-202312-202606-20261005/bootstrap.json',
    'bootstrap_sha256': 'ac04474c43a17920e30597724e922c8a1f36c6b3999d6bc2b462b443dfb04bd3',
    'scope': 'financial-recent-202312-202606-v1',
    'policy': {'attempts': 2, 'metadata_body_bytes': 5242880, 'numeric_body_bytes': 67108864,
               'timeout_seconds': 30, 'deadline_seconds': 120, 'max_backoff_seconds': 5,
               'max_backoffs': 7, 'attempt_seconds': 1680, 'backoff_seconds': 35,
               'scheduling_seconds': 1715, 'max_failed_targets': 3, 'max_guard_streak': 2},
    'policy_sha256': '0e06747d8ebf98bbddf1f03ed32cab2cc5942ad9aa805d50282b59a04f3919ec',
    # The original address is provenance only; these transported bytes are inert.
    'runtime_recorded_path': r'C:\Users\jadaojoao\Documents\Projects\brazilian_banks_data_quality\.venv\Scripts\python.exe',
    'runtime_evidence_path': '.scratch/ifdata-resume-20261006/evidence-only/python.exe',
    'runtime_sha256': '2204195cec25879507d958a8b6949add67091244b8b4da9cf3672f993548fa49',
    'files': {
        'bank_quality/financial_acquisition.py': 'f1fda40ee6c4ab3c6f51570a4dea8fa2fd8ef22ceef056d3ecce4cb0d45aa9da',
        'bank_quality/archive.py': '41331b6a6b17db61819f23cedc820e66839515345058c7b939d05221e5cef8a4',
        'bank_quality/windows_acquisition.py': '5e96531d21952945fa9c4bb3a7e2e5445d4fa8314554cfc10ffa62a19899d543',
        'scripts/acquire-financial.py': 'ba54fd6b03b7264557d7f5b7e086581a68b6222473f8562917fe3f9ea619f8fb',
        'bank_quality/financial_acquisition_batch.py': 'ad5d876235f9489d5fc2f7b52595198b18dd97b949d35f1a2efad9014e11b497',
    },
    'archive_root': 'data/runs/financial-acquisition-executed-code/5c0257789a3a6f54f8fbe98f95cef4eb4a68cf75',
    'executed_code_index_path': 'data/runs/financial-acquisition-executed-code/5c0257789a3a6f54f8fbe98f95cef4eb4a68cf75/index.json',
    'executed_code_index_sha256': 'e00e0b0a94e1ca8afa09ca0ce210ce8573228b48a6c92ef1cfa72814857ca828',
}


def _observe(name, reads, *, pin=None, size=None):
    """Hash a regular contained file, retaining its initial identity for recheck."""
    path = batch._path(name)
    before = path.stat()
    digest, count = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
            count += len(block)
    after = path.stat()
    fingerprint = (digest.hexdigest(), count, after.st_mtime_ns, after.st_ino)
    acquisition._require((before.st_mtime_ns, before.st_ino, before.st_size) ==
                         (after.st_mtime_ns, after.st_ino, after.st_size), 'Legacy source changed during read')
    acquisition._require(pin is None or fingerprint[0] == acquisition._digest(pin), 'Legacy anchored file hash mismatch: ' + name)
    acquisition._require(size is None or type(size) is int and count == size, 'Legacy file size mismatch')
    acquisition._require(name not in reads or reads[name] == fingerprint, 'Legacy source changed during read: ' + name)
    reads[name] = fingerprint
    return path


def _read(ref, reads):
    acquisition._require(type(ref) is dict and set(ref) == {'path', 'sha256'}, 'Invalid legacy file reference')
    path = _observe(ref['path'], reads, pin=ref['sha256'])
    raw = path.read_bytes()
    acquisition._require(acquisition._sha(raw) == ref['sha256'], 'Legacy source changed during read')
    return acquisition._json(raw)


def _json_file(name, reads):
    path = _observe(name, reads)
    return _read(batch._reference(name, reads[name][0]), reads)


def _inventory(parent, entries, reads):
    acquisition._require(type(entries) is list and entries, 'Legacy inventory missing')
    names = set()
    for item in entries:
        acquisition._require(type(item) is dict and set(item) == {'path', 'sha256', 'bytes'}
                             and item['path'] not in names, 'Invalid/duplicate legacy inventory')
        _observe(parent + '/' + item['path'], reads, pin=item['sha256'], size=item['bytes'])
        names.add(item['path'])
    return names


def _source_files(ref, reads):
    manifest = _read(batch._reference(ref['manifest_path'], ref['manifest_sha256']), reads)
    parent = ref['manifest_path'].rsplit('/', 1)[0]
    _observe(parent + '/' + manifest['body_path'], reads, pin=ref['body_sha256'], size=manifest['bytes'])
    if manifest.get('response_metadata_path') is not None:
        _observe(parent + '/' + manifest['response_metadata_path'], reads, pin=manifest['response_metadata_sha256'])


def _source(ref, target, reads):
    _source_files(ref, reads)
    return acquisition._authenticated(ref, expected=target)


def _parquet(entry, anchor, reads):
    """Authenticate accepted bytes and lineage, without any reader or adapter."""
    manifest = _read(batch._reference(entry['manifest_path'], entry['manifest_sha256']), reads)
    _inventory(entry['manifest_path'].rsplit('/', 1)[0], manifest['files'], reads)
    evidence = entry['evidence']
    source = _read(evidence['admission'], reads)
    _inventory(evidence['admission']['path'].rsplit('/', 1)[0], source['files'], reads)
    for ref in evidence.values():
        _read(ref, reads)
    profile = _read(evidence['profile'], reads)
    index = _read(evidence['source_index'], reads)
    sources = source['sources']
    historical = type(index['sources']) is list
    indexed = {ref['source_id']: ref for ref in index['sources']} if historical else index['sources']
    for sid, record in sources.items():
        pin = profile['source_pins'][sid]
        name = indexed[sid]['manifest_path'] if historical else indexed[sid][len('../../../'):]
        _source_files({'manifest_path': name, 'manifest_sha256': pin['manifest_sha256'],
                       'body_sha256': pin['body_sha256']}, reads)
    return batch._parquet(entry, anchor)


def _member(job, bootstrap_pin, reads):
    """Read bindings/journal/head without opening an authority or taking a lock."""
    targets = acquisition._execution_job(job)
    folder, binding, _ = acquisition._authority_paths(job)
    folder_name = folder.relative_to(batch._ROOT).as_posix()
    binding_name = binding.relative_to(batch._ROOT).as_posix()
    expected_binding = {'acquisition_scope': job['acquisition_scope'], 'job_sha256': job['job_sha256'],
                        'bootstrap_sha256': bootstrap_pin}
    batch._same(_json_file(binding_name, reads), expected_binding, 'Legacy member binding mismatch')
    policy = acquisition._limits(job)
    expected_bootstrap = {'contract': 'financial-acquisition-authority-v1', 'acquisition_scope': job['acquisition_scope'],
                          'job_sha256': job['job_sha256'], 'policies': policy, 'targets': targets}
    bootstrap = _read(batch._reference(folder_name + '/bootstrap.json', bootstrap_pin), reads)
    batch._same(bootstrap, expected_bootstrap, 'Legacy member bootstrap mismatch')
    journal = _observe(folder_name + '/journal.jsonl', reads).read_bytes()
    acquisition._require(not journal or journal.endswith(b'\n'), 'Partial legacy member journal tail')
    acquisition._require(acquisition._sha(journal) == reads[folder_name + '/journal.jsonl'][0], 'Legacy journal changed during read')
    replay = acquisition._replay_member_records([acquisition._json(line) for line in journal.splitlines()],
        job_identity=job['job_sha256'], targets=targets, policy=policy)
    batch._same(_json_file(folder_name + '/head.json', reads), replay['head'], 'Legacy member head lags/differs from journal')
    acquisition._require(not replay['state']['pending'], 'Pending legacy member attempt requires current explicit recovery')
    for key, ref in replay['state']['sources'].items():
        acquisition._require(key in targets, 'Legacy source target outside job')
        _source(ref, targets[key], reads)
    return {**replay, 'targets': targets, 'policy': policy}


def _sources403(entry, reads):
    evidence = entry['evidence']
    job = _read(batch._reference(entry['manifest_path'], entry['manifest_sha256']), reads)
    acquisition._require(job['job_sha256'] == evidence['job_sha256'], 'Legacy403 job mismatch')
    batch._same(job['descriptors'][0]['selection'], batch._selection(202403), 'Legacy403 selection mismatch')
    replay = _member(job, evidence['bootstrap_sha256'], reads)
    checked = {key: _read(evidence[key], reads) for key in ('receipt', 'metadata_receipt', 'checkpoint_a', 'checkpoint_b', 'resolution')}
    identity = {'job_sha256': job['job_sha256'], 'bootstrap_sha256': evidence['bootstrap_sha256'],
                'targets': replay['targets'], 'policy': replay['policy']}
    for key in ('receipt', 'metadata_receipt'):
        acquisition._prove_receipt_prefix(checked[key], replay['records'], identity=identity)
    acquisition._require(replay['state']['failures'] == 0, 'Legacy403 source authority failed')
    sources = checked['receipt']['state']['sources']
    metadata = {t['target_key']: sources[t['target_key']] for t in job['targets']}
    resolved = acquisition.resolve_sources(job, metadata)
    batch._same(checked['metadata_receipt']['state']['sources'], metadata, 'Legacy403 metadata prefix source mismatch')
    batch._same(checked['checkpoint_a'], resolved['checkpoints'][0], 'Legacy403 checkpoint A mismatch')
    batch._same(checked['resolution'], resolved, 'Legacy403 resolution mismatch')
    expected_targets = {t['target_key']: t for t in job['targets'] + resolved['numeric_targets']}
    acquisition._require(set(sources) == set(expected_targets), 'Legacy403 source set mismatch')
    projection = ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'manifest_path',
                  'manifest_sha256', 'body_sha256', 'provenance_sha256')
    for key, ref in sources.items():
        _source(ref, expected_targets[key], reads)
    complete = {**checked['checkpoint_a'], 'phase': 'complete', 'checkpoint_a_sha256': evidence['checkpoint_a']['sha256'],
                'sources': sorted([{key: ref[key] for key in projection} for ref in sources.values()], key=lambda ref: ref['source_id'])}
    batch._same(checked['checkpoint_b'], complete, 'Legacy403 A to B mismatch')
    authority = {'status': 'verified', 'job_sha256': job['job_sha256'], 'bootstrap_sha256': evidence['bootstrap_sha256'],
                 **replay['head'], 'pending_attempts': 0, **{key: replay['state'][key] for key in batch._COUNTERS},
                 'receipt_sha256': evidence['receipt']['sha256'], 'receipt_sequence': checked['receipt']['sequence'],
                 'receipt_is_historical': checked['receipt']['sequence'] != replay['head']['sequence']}
    return {**copy.deepcopy(entry), 'contract': acquisition.SOURCES_CONTRACT, 'authority': authority,
            'not_financial_admission': True}


def _anchored_bundle(reads):
    anchor = _LEGACY54_ANCHOR
    acquisition._closed_data(anchor)
    acquisition._require(set(anchor['files']) == set(batch._CODE_FILES)
                         and acquisition._sha(acquisition._canonical(anchor['policy'])) == anchor['policy_sha256'],
                         'Installed legacy anchor inventory/policy mismatch')
    index = _read(batch._reference(anchor['executed_code_index_path'], anchor['executed_code_index_sha256']), reads)
    batch._same(index, {'contract': 'financial-acquisition-executed-code-index-v1',
                       'executed_commit': anchor['executed_commit'], 'files': anchor['files'],
                       'runtime_sha256': anchor['runtime_sha256'], 'policy_sha256': anchor['policy_sha256']},
                'Installed executed code index mismatch')
    for name, pin in anchor['files'].items():
        _observe(anchor['archive_root'] + '/' + name, reads, pin=pin)
    _observe(anchor['runtime_evidence_path'], reads, pin=anchor['runtime_sha256'])
    bundle = _read(batch._reference(anchor['bundle_path'], anchor['bundle_sha256']), reads)
    legacy_pins = {'contract': 'financial-acquisition-code-pins-v1', 'reviewed_commit': anchor['executed_commit'],
                   'files': anchor['files'], 'runtime': {'path': anchor['runtime_recorded_path'],
                   'sha256': anchor['runtime_sha256']}, 'policy_sha256': anchor['policy_sha256']}
    batch._same(bundle['code_pins'], legacy_pins, 'Legacy five executed pins differ from installed anchor')
    batch._same(bundle['policies'], anchor['policy'], 'Legacy policy differs from installed anchor')
    acquisition._require(bundle['contract'] == 'financial-acquisition-batch-v1' and bundle['scope'] == anchor['scope']
                         and bundle['destination'] + '/bundle.json' == anchor['bundle_path']
                         and bundle['executable'] is True, 'Legacy bundle scope/destination mismatch')
    batch._same(bundle['selection'], {'periods': list(batch._WINDOW), 'perspective': 1005, 'reports': 'native-four'},
                'Legacy bundle selection mismatch')
    batch._same(bundle['acquire_periods'], list(batch._ACQUIRE), 'Legacy acquired periods mismatch')
    batch._same(bundle['reuse_periods'], list(batch._REUSE), 'Legacy reused periods mismatch')
    batch._same(bundle['caps'], batch._CAPS, 'Legacy caps mismatch')
    bootstrap = _read(batch._reference(anchor['bootstrap_path'], anchor['bootstrap_sha256']), reads)
    batch._same(bootstrap, batch._batch_bootstrap(bundle, anchor['bundle_sha256']), 'Legacy batch bootstrap mismatch')
    binding, _ = batch._batch_paths()
    batch._same(_json_file(binding.relative_to(batch._ROOT).as_posix(), reads),
                batch._binding(bundle, anchor['bundle_sha256'], anchor['bootstrap_sha256']), 'Legacy batch binding mismatch')
    for ref in bundle['catalogs'].values():
        _source_files(ref, reads)
    acquisition._catalogs(bundle['catalogs'])
    entries = []
    for stored in bundle['reuse']:
        trusted = batch._TRUSTED_REUSE[stored['period']]
        entry = trusted['entry']
        checked = _sources403(entry, reads) if stored['period'] == 202403 else _parquet(entry, trusted, reads)
        batch._same(stored, checked, 'Legacy reused evidence changed')
        entries.append({'period': stored['period'], 'state': 'reused_' + stored['kind'],
                        'new_http_requests': 0, 'reuse_evidence': copy.deepcopy(checked)})
    return bundle, entries


def _completed_capture(current_code_pins_path, current_code_pins_sha256):
    batch._verified_current_code_pins(current_code_pins_path, current_code_pins_sha256)
    reads = {}
    current_name = Path(current_code_pins_path).absolute().relative_to(batch._ROOT.absolute()).as_posix()
    _read(batch._reference(current_name, current_code_pins_sha256), reads)
    bundle, entries = _anchored_bundle(reads)
    anchor = _LEGACY54_ANCHOR
    journal_name = bundle['destination'] + '/journal.jsonl'
    journal = _observe(journal_name, reads).read_bytes()
    acquisition._require(not journal or journal.endswith(b'\n'), 'Partial legacy phase journal tail')
    acquisition._require(acquisition._sha(journal) == reads[journal_name][0], 'Legacy phase journal changed during read')
    phase = batch._replay_phase_records([acquisition._json(line) for line in journal.splitlines()], anchored_bundle={
        'bundle': bundle, 'bundle_sha256': anchor['bundle_sha256'], 'bootstrap_sha256': anchor['bootstrap_sha256']})
    batch._same(_json_file(bundle['destination'] + '/head.json', reads), phase['head'], 'Legacy phase head lags/differs from journal')
    acquisition._require(not phase['state']['pending'] and not phase['state']['halt']
                         and not (batch._ROOT / bundle['destination'] / 'halt.json').exists(), 'Legacy capture is pending/halted')
    prefixes, counters = [], []
    for member in bundle['members']:
        job = _read(batch._reference(member['job_path'], member['job_file_sha256']), reads)
        batch._same(job, member['job'], 'Legacy member physical job differs')
        acquisition._require(job['job_sha256'] == member['job_sha256'], 'Legacy canonical job mismatch')
        replay = _member(job, member['bootstrap_sha256'], reads)
        finished = {s['phase']: s for s in phase['state']['finished'].values() if s['period'] == member['period']}
        acquisition._require(set(finished) == {'metadata', 'values'}
                             and all(s['result']['status'] == 'complete' for s in finished.values()), 'Legacy capture lacks completed A/B phases')
        metadata_sources = {t['target_key']: replay['state']['sources'][t['target_key']] for t in job['targets']}
        resolved = acquisition.resolve_sources(job, metadata_sources)
        for target in resolved['numeric_targets']:
            body, _ = _source(replay['state']['sources'][target['target_key']], target, reads)
            origins = [node['origin'] for resolution in resolved['resolutions'] for node in resolution['nodes']
                       if node['kind'] == 'numeric' and node['origin']['area'] == target['area']]
            acquisition.validate_numeric_source(body, area=target['area'], required_origins=origins)
        a_ref = finished['metadata']['result']['checkpoint']
        a = _read(a_ref, reads)
        proofs = {}
        for name in ('metadata', 'values'):
            start = finished[name]
            result = start['result']
            proofs[name] = batch._prove_phase_sources({
                'start': {key: value for key, value in start.items() if key != 'result'}, 'result': result,
                'receipt': _read(result['receipt'], reads), 'checkpoint': _read(result['checkpoint'], reads),
                'resolved': resolved, 'metadata_checkpoint_ref': a_ref, 'metadata_checkpoint': a}, replay, anchored_member=member)
        batch._same(proofs['values']['receipt_prefix']['head'], replay['head'], 'Legacy values receipt is not the current member head')
        count = {'period': member['period'], **{key: replay['state'][key] for key in batch._COUNTERS},
                 'sequence': replay['head']['sequence'], 'pending_attempts': 0}
        b = proofs['values']['checkpoint']
        entries.append({'period': member['period'], 'state': 'acquired_validated_sources',
            'job': {'path': member['job_path'], 'sha256': member['job_file_sha256'], 'canonical_sha256': member['job_sha256']},
            'bootstrap_sha256': member['bootstrap_sha256'], 'checkpoint_a': copy.deepcopy(a_ref),
            'checkpoint_b': copy.deepcopy(finished['values']['result']['checkpoint']),
            'metadata_receipt': copy.deepcopy(finished['metadata']['result']['receipt']),
            'values_receipt': copy.deepcopy(finished['values']['result']['receipt']), 'selection': copy.deepcopy(b['selection']),
            'descriptor_sha256': b['descriptor_sha256'], 'sources': copy.deepcopy(b['sources']), 'counters': count,
            'financial_admission': False, 'parquet_admission': False})
        prefixes.append({'period': member['period'], 'head': copy.deepcopy(replay['head']),
                         'metadata': proofs['metadata']['receipt_prefix']['head'], 'values': proofs['values']['receipt_prefix']['head'],
                         'counters': copy.deepcopy(count)})
        counters.append(count)
    entries.sort(key=lambda entry: entry['period'])
    batch._same([entry['period'] for entry in entries], list(batch._WINDOW), 'Legacy handoff membership incomplete/duplicate')
    handoff = {'contract': 'financial-acquisition-batch-handoff-v1', 'scope': anchor['scope'],
        'bundle': batch._reference(anchor['bundle_path'], anchor['bundle_sha256']), 'bootstrap_sha256': anchor['bootstrap_sha256'],
        'entries': entries, 'accepted_parquet_periods': [202312, 202412, 202503],
        'sources_only_periods': [202403, *batch._ACQUIRE], 'missing_periods': [],
        'totals': {key: sum(count[key] for count in counters) for key in batch._COUNTERS},
        'claim': 'native source completion; no historical financial comparability or new Parquet admission'}
    acquisition._closed_data(handoff)
    for name, fingerprint in list(reads.items()):
        _observe(name, reads, pin=fingerprint[0], size=fingerprint[1])
    batch._verified_current_code_pins(current_code_pins_path, current_code_pins_sha256)
    digest = acquisition._sha(acquisition._canonical(handoff))
    proof = {'contract': 'financial-acquisition-legacy54-proof-v1', 'anchor_id': anchor['anchor_id'],
        'bundle_sha256': anchor['bundle_sha256'], 'bootstrap_sha256': anchor['bootstrap_sha256'],
        'executed_code_index_sha256': anchor['executed_code_index_sha256'],
        'current_code_identity_sha256': current_code_pins_sha256,
        'selections': [batch._selection(entry['period']) for entry in entries], 'member_prefixes': prefixes,
        'phase_prefix': copy.deepcopy(phase['head']),
        'source_refs': [batch._reference(name, fingerprint[0]) for name, fingerprint in sorted(reads.items())
                        if name.startswith('data/')], 'handoff_sha256': digest}
    acquisition._closed_data(proof)
    return proof, {'contract': 'financial-acquisition-legacy54-handoff-v1', 'anchor_id': anchor['anchor_id'],
                   'handoff': handoff, 'handoff_sha256': digest}


def verify_legacy54_sources(*, current_code_pins_path, current_code_pins_sha256):
    return _completed_capture(current_code_pins_path, current_code_pins_sha256)[0]


def reconstruct_legacy54_handoff(*, current_code_pins_path, current_code_pins_sha256):
    return _completed_capture(current_code_pins_path, current_code_pins_sha256)[1]

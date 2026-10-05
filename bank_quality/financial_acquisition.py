"""Finite authenticated resolution and local acquisition authority; no admission.

Catalog indexes use financial-acquisition-catalog-index-v1 and pinned O/N captures.
Source provenance hashes cover the complete manifest with fractional JSON numbers
represented as {json_number: lexical_token}, as in the existing financial reader.
"""
import hashlib
from contextlib import contextmanager
import copy
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import time
import uuid
from urllib.parse import quote

from .archive import load_body
from .windows_acquisition import (exclusive_claim as _claim, identity_extinct, require_supported,
                                  run_contained_attempt, _current_identity, verify_worker_ancestry)


_ROOT = Path(__file__).resolve().parents[1]
INDEX_CONTRACT = 'financial-acquisition-catalog-index-v1'
JOB_CONTRACT = 'financial-acquisition-job-v1'
SOURCES_CONTRACT = 'ifdata-financial-historical-sources-v1'
_API = 'https://www3.bcb.gov.br/ifdata/rest/arquivos?nomeArquivo='
_FROZEN = {
    'old': ('b6ead0180a1622fa27766d55bc63520a0d35e6202a4e35075b615b4a235447c7',
            '2428b8a436e142682cd63eb6155717f58f2524582dcca427654032f45f6acf07',
            'https://www3.bcb.gov.br/ifdata/rest/relatorios2000a2024'),
    'new': ('8ab9f7f82eed8d7103525d3fb7c64e4d5150fd17a6caf6f07a6df00bc7b3bf12',
            'b8977d383e4ea51f56ed391571aca7af1c109b83b9c17ceef8b926841d658206',
            'https://www3.bcb.gov.br/ifdata/rest/relatorios2025a2030'),
}
# Explicit members/IDs from Issue 47's frozen inventory, not a latest calendar.
_MEMBERS = {
    201003:(1,3,4,5), 201006:(1,3,4,5), 201009:(1,3,4,5), 201012:(1,3,4,5),
    201103:(1,3,4,5), 201106:(1,3,4,5), 201109:(1,3,4,5), 201112:(1,3,4,5),
    201203:(1,3,4,5), 201206:(1,3,4,5), 201209:(1,3,4,5), 201212:(1,3,4,5),
    201303:(1,3,4,5), 201306:(1,3,4,5), 201309:(1,3,4,5), 201312:(1,3,4,5),
    201403:(1,3,4,5), 201406:(1,3,4,5), 201409:(1,3,4,5), 201412:(1,3,4,5),
    201503:(75,3,4,5), 201506:(75,3,4,5), 201509:(75,3,4,5), 201512:(75,3,4,5),
    201603:(75,3,4,5), 201606:(75,3,4,5), 201609:(75,3,4,5), 201612:(75,3,4,5),
    201703:(75,3,4,5), 201706:(75,3,4,5), 201709:(75,3,4,5), 201712:(75,3,4,5),
    201803:(75,3,4,5), 201806:(75,3,4,5), 201809:(75,3,4,5), 201812:(75,3,4,5),
    201903:(92,3,4,91), 201906:(92,3,4,91), 201909:(92,3,4,91),
    201912:(92,96,97,98), 202003:(92,96,97,98),
    202006:(92,96,101,98), 202009:(92,96,101,98), 202012:(92,96,101,98),
    202103:(92,96,101,98), 202106:(92,96,101,98), 202109:(92,96,101,98), 202112:(92,96,101,98),
    202203:(92,96,101,98), 202206:(92,96,101,98), 202209:(92,96,101,98), 202212:(92,96,101,98),
    202303:(92,96,101,98), 202306:(92,96,101,98), 202309:(92,96,101,98), 202312:(92,96,101,98),
    202403:(92,96,101,98), 202406:(92,96,101,98), 202409:(92,96,101,98), 202412:(92,96,101,98),
    202503:(119,107,110,118), 202506:(119,107,110,118), 202509:(119,107,110,118),
    202512:(119,107,110,118), 202603:(119,107,110,118), 202606:(119,107,110,118),
}


class _Number(str):
    """An uncoerced JSON number, distinguished from a JSON string."""


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _native(value):
    if isinstance(value, _Number):
        return {'json_number': str(value)}
    if isinstance(value, list):
        return [_native(item) for item in value]
    if isinstance(value, dict):
        return {key: _native(item) for key, item in value.items()}
    return value


def _canonical(value):
    return json.dumps(_native(value), ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def _json(body, *, numeric=False):
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError('Unsupported JSON constant: ' + value)
    return json.loads(body.decode('utf-8'), object_pairs_hook=pairs,
                      parse_float=_Number, parse_int=_Number if numeric else int,
                      parse_constant=constant)


def _digest(value):
    _require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'Invalid SHA-256 pin')
    return value


def _local(name):
    """Only regular files below the package's approved raw/runs roots."""
    _require(type(name) is str and name and '\\' not in name and ':' not in name,
             'Source path must be relative and contained')
    parts = name.split('/')
    _require(len(parts) >= 3 and parts[:2] in (['data', 'raw'], ['data', 'runs'])
             and all(p not in ('', '.', '..') for p in parts), 'Source path escape or unapproved root')
    current = _ROOT
    for part in parts:
        current = current / part
        info = current.lstat()
        _require(not stat.S_ISLNK(info.st_mode)
                 and not (getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)),
                 'Source symlink/reparse point is forbidden')
    _require(current.resolve().is_relative_to(_ROOT.resolve()) and current.is_file(), 'Source path escape/non-file')
    return current


def _saved_body(manifest, path, pin):
    _require(manifest.get('sha256') == _digest(pin), 'Source body pin mismatch')
    name = manifest.get('body_path')
    _require(type(name) is str and name and '\\' not in name and ':' not in name
             and all(p not in ('', '.', '..') for p in name.split('/')), 'Body path escape')
    body_path = _local((path.parent.relative_to(_ROOT) / PurePosixPath(name)).as_posix())
    body = load_body(manifest, path.parent)
    _require(_sha(body) == pin and type(manifest.get('bytes')) is int
             and len(body) == manifest['bytes'], 'Source body size/hash mismatch')
    _require(body_path.is_file(), 'Source body missing')
    return body


def _response_evidence(manifest, path):
    sidecar_name = manifest.get('response_metadata_path')
    _require(type(sidecar_name) is str and sidecar_name and '\\' not in sidecar_name and ':' not in sidecar_name
             and all(p not in ('', '.', '..') for p in sidecar_name.split('/')), 'Response metadata path escape')
    sidecar_path = _local((path.parent.relative_to(_ROOT) / PurePosixPath(sidecar_name)).as_posix())
    sidecar_body = sidecar_path.read_bytes()
    _require(_sha(sidecar_body) == _digest(manifest.get('response_metadata_sha256')), 'Response metadata hash mismatch')
    sidecar = _json(sidecar_body)
    _require(isinstance(sidecar, dict) and all(sidecar.get(key) == manifest.get(key)
             for key in ('http_status', 'final_url', 'response_headers_raw')), 'Response metadata projection mismatch')
    _require(all(sidecar[key] == manifest.get(key) for key in
             ('url', 'method', 'context', 'started_at_utc') if key in sidecar), 'Response metadata context mismatch')
    raw_headers = manifest.get('response_headers_raw')
    _require(isinstance(raw_headers, list) and all(isinstance(pair, list) and len(pair) == 2
             and all(type(value) is str for value in pair) for pair in raw_headers), 'Invalid raw response headers')
    headers = {}
    for name, value in raw_headers:
        headers.setdefault(name.lower(), []).append(value.strip())
    return headers


def _failed_attempt_evidence(manifest, path):
    """Authenticate a failed outcome without claiming successful source framing."""
    diagnostics = manifest.get('diagnostics')
    _require(isinstance(diagnostics, list) and all(isinstance(item, dict)
             and type(item.get('code')) is str and type(item.get('detail')) is str for item in diagnostics),
             'Invalid attempt diagnostics')
    codes = {item['code'] for item in diagnostics}
    _require(manifest.get('source_complete') is False and diagnostics
             and type(manifest.get('truncated')) is bool and type(manifest.get('eof_observed')) is bool,
             'Inconsistent failed attempt outcome')
    status = manifest.get('http_status')
    outcome = manifest.get('outcome')
    if status is None:
        _require(outcome in {'network_error', 'transport_error'}
                 and codes <= {'transport_exception', 'response_headers_error'}
                 and manifest.get('response_metadata_path') is None and manifest.get('response_metadata_sha256') is None
                 and manifest.get('final_url') is None and manifest.get('response_headers_raw') == []
                 and manifest.get('content_length') is None and manifest.get('bytes_observed') == 0
                 and manifest.get('completion_basis') is None and manifest['eof_observed'] is False
                 and manifest['truncated'] is False, 'Inconsistent no-response attempt evidence')
        return
    _require(type(status) is int and 100 <= status <= 599
             and outcome in {'http_error', 'transport_error', 'storage_error'}, 'Invalid failed response status/outcome')
    _require(outcome != 'http_error' or (status != 200 and 'http_status' in codes), 'HTTP error status evidence mismatch')
    headers = _response_evidence(manifest, path)
    lengths, transfers, encodings = (headers.get(key, []) for key in
                                    ('content-length', 'transfer-encoding', 'content-encoding'))
    length = manifest.get('content_length')
    valid_length = len(lengths) == 1 and re.fullmatch('[0-9]+', lengths[0])
    _require(length is None or (type(length) is int and length >= 0), 'Invalid attempt Content-Length counter')
    _require((valid_length and length == int(lengths[0]))
             or (not lengths and length is None)
             or (lengths and not valid_length and length is None and 'invalid_content_length' in codes),
             'Invalid Content-Length header evidence')
    _require(not transfers or (not lengths and transfers == ['chunked']) or 'ambiguous_framing' in codes,
             'Ambiguous framing headers without diagnostic')
    _require(not encodings or encodings == ['identity'] or 'unexpected_content_encoding' in codes,
             'Unexpected Content-Encoding headers without diagnostic')
    _require(type(manifest.get('final_url')) is str
             and (manifest['final_url'] == manifest['url'] or 'final_url_mismatch' in codes), 'Attempt final URL mismatch')
    basis = manifest.get('completion_basis')
    _require(basis in {None, 'eof', 'chunked_eof', 'content_length'}, 'Invalid attempt completion basis')
    _require(basis is not None or bool(codes & {'incomplete_read', 'read_exceeded_budget', 'body_budget_exhausted',
             'content_length_mismatch', 'transport_exception', 'framing_error', 'storage_error'}),
             'Attempt missing framing without failure diagnostic')
    _require(basis is None or (not manifest['truncated'] and
             ((basis == 'content_length' and not transfers and length == manifest['bytes_observed'])
              or (basis in {'eof', 'chunked_eof'} and manifest['eof_observed'] is True
                  and (basis == 'chunked_eof') == (transfers == ['chunked'])))), 'Attempt framing counters mismatch')
    _require(not manifest['eof_observed'] or basis in {'eof', 'chunked_eof'}, 'Attempt EOF counter mismatch')
    _require(not manifest['truncated'] or (basis is None and manifest['bytes_observed'] == manifest['body_budget_bytes']
             and 'body_budget_exhausted' in codes), 'Attempt truncation counter mismatch')
    _require(length is None or length == manifest['bytes_observed'] or bool(codes &
             {'content_length_mismatch', 'transport_exception', 'framing_error', 'storage_error'}),
             'Attempt Content-Length mismatch without diagnostic')


def _authenticated(ref, *, expected=None, frozen=None):
    _require(isinstance(ref, dict), 'Source reference must be an object')
    required = {'source_id', 'role', 'manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256'}
    _require(required <= set(ref), 'Source reference requires external manifest/body/provenance pins')
    for key in ('manifest_sha256', 'body_sha256', 'provenance_sha256'):
        _digest(ref[key])
    if frozen:
        _require((ref['manifest_sha256'], ref['body_sha256']) == _FROZEN[frozen][:2], 'Changed frozen catalog pins')
    path = _local(ref['manifest_path'])
    raw = path.read_bytes()
    _require(_sha(raw) == ref['manifest_sha256'], 'Source manifest hash mismatch')
    manifest = _json(raw)
    _require(isinstance(manifest, dict) and _sha(_canonical(manifest)) == ref['provenance_sha256'],
             'Source provenance hash mismatch')
    _require(manifest.get('http_status') == 200 and manifest.get('outcome') == 'ok'
             and manifest.get('truncated') is False, 'Source is not complete')
    # Frozen O/N have exact preexisting physical pins. New C/D/N never inherit
    # legacy completeness merely from an ok flag, coherent hashes or their role.
    _require(frozen is not None or manifest.get('contract') == 'bounded-http-archive-v1',
             'Nonfrozen source requires bounded transport contract and positive framing')
    if manifest.get('contract') == 'bounded-http-archive-v1':
        _require(manifest.get('source_complete') is True and manifest.get('body_available') is True
                 and manifest.get('diagnostics') == []
                 and manifest.get('completion_basis') in {'eof', 'chunked_eof', 'content_length'},
                 'Bounded source is not complete')
        _require(manifest['completion_basis'] == 'content_length' or manifest.get('eof_observed') is True,
                 'Bounded source lacks positive EOF evidence')
        _require(type(manifest.get('bytes_observed')) is int and manifest['bytes_observed'] == manifest.get('bytes')
                 and type(manifest.get('body_budget_bytes')) is int
                 and 0 <= manifest['bytes_observed'] <= manifest['body_budget_bytes'], 'Bounded source byte counters invalid')
        length = manifest.get('content_length')
        _require(length is None or (type(length) is int and length >= 0 and length == manifest['bytes_observed']),
                 'Bounded source Content-Length mismatch')
        _require(manifest['completion_basis'] != 'content_length' or length is not None, 'Missing completion framing')
        headers = _response_evidence(manifest, path)
        lengths = headers.get('content-length', [])
        transfers = headers.get('transfer-encoding', [])
        encodings = headers.get('content-encoding', [])
        _require(not lengths or (len(lengths) == 1 and re.fullmatch('[0-9]+', lengths[0])
                 and int(lengths[0]) == length), 'Invalid Content-Length header evidence')
        _require(lengths or length is None, 'Content-Length header missing')
        _require(not transfers or (not lengths and transfers == ['chunked']), 'Ambiguous framing headers')
        _require(not encodings or encodings == ['identity'], 'Unexpected Content-Encoding headers')
        _require((manifest['completion_basis'] == 'chunked_eof') == bool(transfers), 'Completion basis/header mismatch')
    body = _saved_body(manifest, path, ref['body_sha256'])
    url = _FROZEN[frozen][2] if frozen else expected['url']
    _require(manifest.get('url') == url and manifest.get('final_url') == url
             and manifest.get('method') == 'GET', 'Source URL/method mismatch')
    if expected:
        for key in ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'period', 'perspective', 'target_key', 'url'):
            _require(ref.get(key) == expected.get(key), 'Source context/target mismatch: ' + key)
        context = manifest.get('context')
        _require(isinstance(context, dict) and ref.get('context') == _native(context)
                 and type(context.get('period')) is int and context['period'] == expected['period']
                 and type(context.get('perspective')) is int and context['perspective'] == 1005
                 and context.get('role') == expected['role'], 'Source period/perspective/role mismatch')
    return body, manifest


def _catalogs(refs):
    _require(isinstance(refs, dict) and set(refs) == {'old', 'new'}, 'Both frozen O/N catalogs required')
    result = {}
    for name, ref in refs.items():
        _require(set(ref) == {'source_id', 'role', 'manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256'}
                 and ref['role'] == 'catalog' and ref['source_id'] == 'catalog-' + name, 'Invalid catalog reference schema')
        body, _ = _authenticated(ref, frozen=name)
        catalog = _json(body)
        _require(isinstance(catalog, list), 'Catalog must be an array')
        result[name] = catalog
    return result


def _descriptor(catalog, ref, period):
    matches = [(p, entry) for p, entry in enumerate(catalog)
               if isinstance(entry, dict) and type(entry.get('dt')) is int and entry['dt'] == period]
    _require(len(matches) == 1, 'Missing or duplicate catalog period')
    position, entry = matches[0]
    files = entry.get('files')
    _require(isinstance(files, list) and all(isinstance(f, dict) and type(f.get('f')) is str for f in files), 'Invalid catalog files')
    prefix = ('ifdata_2025_2030//' if period >= 202503 else 'ifdata/') + str(period) + '/'
    selectors = [s for f in files for s in f.get('sel', []) if isinstance(s, dict) and s.get('id') == 1005]
    _require(len(selectors) == 1 and type(selectors[0]['id']) is int, 'Missing or duplicate financial selection')
    offers = []
    for role, leaf in [('cadaster', f'cadastro{period}_1005.json'), ('dictionary', f'info{period}.json')]:
        found = [p for p, f in enumerate(files) if f['f'] == prefix + leaf]
        _require(len(found) == 1, 'Missing or duplicate source announcement')
        offers.append({'source_id': role, 'role': role, 'area': None, 'native_file': prefix + leaf,
                       'catalog_pointer': f'/{position}/files/{found[0]}/f'})
    shards = {}
    for p, item in enumerate(files):
        match = re.fullmatch(re.escape(prefix + f'dados{period}_') + r'([1-9][0-9]*)\.json', item['f'])
        if match:
            area = int(match[1])
            _require(area not in shards, 'Duplicate numeric announcement')
            shards[area] = {'source_id': 'numeric:' + str(area), 'role': 'numeric', 'area': area,
                            'native_file': item['f'], 'catalog_pointer': f'/{position}/files/{p}/f'}
    offers.extend(shards[a] for a in sorted(shards))
    reports = []
    for rid in _MEMBERS[period]:
        found = [(p, f['trel']) for p, f in enumerate(files) if isinstance(f.get('trel'), dict)
                 and type(f['trel'].get('id')) is int and f['trel']['id'] == rid]
        _require(len(found) == 1, 'Missing or duplicate financial report')
        p, report = found[0]
        _require(isinstance(report.get('s'), list) and {'id': 1005} in report['s'], 'Wrong report selection')
        _require(files[p]['f'] == prefix + f'trel{period}_{rid}.json', 'Wrong report filename')
        reports.append({'report': _native(report), 'catalog_pointer': f'/{position}/files/{p}/trel'})
    descriptor = {'selection': {'period': period, 'perspective': 1005, 'reports': list(_MEMBERS[period])},
                  'catalog': {**{key: ref[key] for key in ('manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256')},
                              'reference_pointer': '/' + str(position)}, 'reports': reports, 'source_offers': offers}
    return {**descriptor, 'descriptor_sha256': _sha(_canonical(descriptor))}


def _target(offer, period):
    return {**offer, 'period': period, 'perspective': 1005,
            'target_key': f'{period}:' + offer['source_id'], 'url': _API + quote(offer['native_file'], safe='')}


def _job_hash(job):
    return _sha(_canonical({key: value for key, value in job.items() if key not in {'job_sha256', 'executable', 'reuse_sources'}}))


def prepare_job(catalog_index: Path, catalog_index_sha256: str, periods: tuple[int, ...], *,
                limits: dict, reuse_index: Path | None = None, reuse_index_sha256: str | None = None) -> dict:
    """Construct an offline candidate; preparation never grants a GET or budget."""
    raw = Path(catalog_index).read_bytes()
    _require(_sha(raw) == _digest(catalog_index_sha256), 'Catalog index hash mismatch')
    index = _json(raw)
    _require(isinstance(index, dict) and set(index) == {'contract', 'acquisition_scope', 'selection', 'catalogs'}
             and index['contract'] == INDEX_CONTRACT, 'Invalid catalog index schema')
    _require(index['selection'] == {'perspective': 1005, 'reports': 'native-four'}, 'Wrong closed financial selection')
    from . import financial_acquisition_batch as batch
    scopes = {batch._SCOPE + '/' + str(p): p for p in batch._ACQUIRE}
    _require(type(index['acquisition_scope']) is str and (index['acquisition_scope'].startswith('issue50/')
                  or index['acquisition_scope'] in scopes)
             and len(index['acquisition_scope']) > 8, 'Invalid acquisition_scope')
    _require(isinstance(periods, tuple) and periods and all(type(p) is int and p in _MEMBERS for p in periods)
             and len(set(periods)) == len(periods), 'Select an explicit unique subset of the frozen 66 periods')
    if index['acquisition_scope'] in scopes:
        _require(periods == (scopes[index['acquisition_scope']],), 'New scope requires exact matching singleton period')
    _require(isinstance(limits, dict), 'Limits must be an object')
    # Execution logistics never alter the identity of a candidate's finite budget.
    policies = {key: _native(value) for key, value in limits.items()
                if key not in {'workers', 'worker_count', 'session_id', 'execution_id', 'timestamp', 'destination', 'temporary_destination'}}
    _canonical(policies)
    catalogs = _catalogs(index['catalogs'])
    descriptors = []
    for period in sorted(periods):
        name = 'new' if period >= 202503 else 'old'
        descriptors.append(_descriptor(catalogs[name], index['catalogs'][name], period))
    targets = sorted((_target(offer, d['selection']['period']) for d in descriptors
                      for offer in d['source_offers'] if offer['role'] != 'numeric'), key=lambda t: t['target_key'])
    job = {'contract': JOB_CONTRACT, 'version': 1, 'acquisition_scope': index['acquisition_scope'],
           'catalogs': index['catalogs'], 'descriptors': descriptors, 'policies': policies, 'targets': targets}
    job['job_sha256'] = _job_hash(job)
    job['executable'] = False
    _require((reuse_index is None) == (reuse_index_sha256 is None), 'Reuse index requires its external hash')
    if reuse_index is not None:
        reuse_raw = Path(reuse_index).read_bytes()
        _require(_sha(reuse_raw) == _digest(reuse_index_sha256), 'Reuse index hash mismatch')
        reuse = _json(reuse_raw)
        _require(isinstance(reuse, dict) and set(reuse) == {'contract', 'job_sha256', 'sources'}
                 and reuse['contract'] == 'financial-acquisition-reuse-index-v1' and reuse['job_sha256'] == job['job_sha256']
                 and isinstance(reuse['sources'], dict), 'Invalid reuse index')
        by_key = {t['target_key']: t for d in descriptors for t in (_target(o, d['selection']['period']) for o in d['source_offers'])}
        for key, ref in reuse['sources'].items():
            _require(key in by_key, 'Reuse source outside job')
            _authenticated(ref, expected=by_key[key])
        job['reuse_sources'] = _native(reuse['sources'])
    return job


def _cadaster(body, period):
    rows = _json(body)
    _require(isinstance(rows, list) and rows, 'Cadaster must contain a nonempty array')
    fields, entities = None, []
    for row in rows:
        _require(isinstance(row, dict) and {'c0', 'c1'} <= set(row)
                 and all(re.fullmatch(r'c(?:0|[1-9][0-9]*)', key) and type(value) is str for key, value in row.items()),
                 'Invalid native cadaster schema/types')
        if fields is None:
            fields = set(row)
        _require(set(row) == fields, 'Nonuniform native cadaster schema')
        _require(row['c0'] and row['c0'] not in entities, 'Empty or duplicate opaque cadaster entity')
        _require(row['c1'] == str(period), 'Wrong cadaster period')
        entities.append(row['c0'])
    return rows, sorted(fields, key=lambda field: int(field[1:])), entities


def _definitions(body):
    values = _json(body)
    _require(isinstance(values, list), 'Dictionary must be an array')
    definitions = {}
    for p, item in enumerate(values):
        _require(isinstance(item, dict) and type(item.get('id')) is int and item['id'] not in definitions
                 and type(item.get('td')) is int and item['td'] in {1, 2, 3}
                 and type(item.get('a')) is int and item['a'] > 0 and type(item.get('lid')) is int,
                 'Unsupported or duplicate dictionary definition')
        _require((item['td'] == 2 and item['lid'] == -1) or (item['td'] != 2 and item['lid'] >= 0),
                 'Unsupported definition localizer')
        definitions[item['id']] = (p, item)
    return definitions


def _walk(columns, base, parent=None):
    _require(isinstance(columns, list), 'Invalid report children schema')
    seen = set()
    for p, column in enumerate(columns):
        _require(isinstance(column, dict) and type(column.get('id')) is int and column['id'] not in seen
                 and type(column.get('ifd')) is int and isinstance(column.get('sc'), list)
                 and column.get('ip') == (parent['id'] if parent else None), 'Invalid report node/parent')
        seen.add(column['id'])
        pointer = base + '/' + str(p)
        yield column, pointer, parent['pointer'] if parent else None
        yield from _walk(column['sc'], pointer + '/sc', {'id': column['id'], 'pointer': pointer})


def resolve_sources(job: dict, metadata_sources: dict) -> dict:
    """Authenticate checkpoint A and resolve only actually announced numeric areas."""
    _require(isinstance(job, dict) and job.get('contract') == JOB_CONTRACT
             and job.get('job_sha256') == _job_hash(job), 'Changed candidate job hash/schema')
    catalogs = _catalogs(job['catalogs'])
    _require(isinstance(metadata_sources, dict) and set(metadata_sources) == {t['target_key'] for t in job['targets']},
             'Exact metadata source set required')
    checkpoints, resolutions, numeric_targets = [], [], []
    for descriptor in job['descriptors']:
        period = descriptor['selection']['period']
        _require(type(period) is int and period in _MEMBERS, 'Period outside frozen 66')
        name = 'new' if period >= 202503 else 'old'
        authentic = _descriptor(catalogs[name], job['catalogs'][name], period)
        _require(descriptor == authentic, 'Descriptor differs from frozen catalog')
        sources, bodies = [], {}
        for role in ('cadaster', 'dictionary'):
            offer = next(o for o in descriptor['source_offers'] if o['role'] == role)
            target = _target(offer, period)
            ref = metadata_sources[target['target_key']]
            body, _ = _authenticated(ref, expected=target)
            bodies[role] = body
            sources.append({key: ref[key] for key in ('source_id', 'role', 'area', 'native_file', 'catalog_pointer',
                                                    'manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256')})
        _, fields, entities = _cadaster(bodies['cadaster'], period)
        definitions = _definitions(bodies['dictionary'])
        areas = {o['area']: o for o in descriptor['source_offers'] if o['role'] == 'numeric'}
        nodes, needed_areas = [], set()
        for report in descriptor['reports']:
            report_nodes = set()
            for node, pointer, parent in _walk(report['report']['c'], report['catalog_pointer'] + '/c'):
                _require(node['id'] not in report_nodes, 'Duplicate report occurrence ID')
                report_nodes.add(node['id'])
                _require(node['ifd'] in definitions, 'Selected definition missing')
                p, definition = definitions[node['ifd']]
                group = bool(node['sc'])
                _require(group == (definition['td'] == 2), 'Group/definition structure mismatch')
                origin, kind = None, 'group'
                if definition['td'] == 1:
                    field = 'c' + str(definition['lid'])
                    _require(field in fields, 'Attribute points outside cadaster field schema')
                    kind, origin = 'attribute', {'source_id': 'cadaster', 'field': field}
                elif definition['td'] == 3:
                    _require(definition['a'] in areas, 'Numeric area is not announced')
                    kind = 'numeric'
                    needed_areas.add(definition['a'])
                    origin = {'source_id': areas[definition['a']]['source_id'], 'area': definition['a'],
                              'lid': definition['lid'], 'cadaster_entities': entities, 'catalog_pointer': pointer}
                nodes.append({'report_id': report['report']['id'], 'catalog_pointer': pointer,
                              'parent_pointer': parent, 'children_pointers': [pointer + '/sc/' + str(p) for p in range(len(node['sc']))],
                              'node': node, 'definition': _native(definition), 'definition_pointer': '/' + str(p),
                              'kind': kind, 'origin': origin})
        checkpoint = {'contract': SOURCES_CONTRACT, 'phase': 'metadata', 'selection': descriptor['selection'],
                      'descriptor_sha256': descriptor['descriptor_sha256'], 'catalog': descriptor['catalog'],
                      'sources': sorted(sources, key=lambda ref: ref['source_id'])}
        checkpoints.append(checkpoint)
        resolutions.append({'selection': descriptor['selection'], 'metadata_digest': _sha(_canonical(checkpoint)),
                            'nodes': nodes, 'cadaster_fields': fields, 'cadaster_entities': entities,
                            'source_complete': True, 'source_validated': True, 'origin_resolved': True})
        numeric_targets.extend(_target(areas[area], period) for area in sorted(needed_areas))
    return {'job_sha256': job['job_sha256'], 'checkpoints': checkpoints, 'resolutions': resolutions,
            'numeric_targets': sorted(numeric_targets, key=lambda t: (t['period'], t['area'])),
            'source_complete': True, 'source_validated': True, 'origin_resolved': True}


def _identifier(value):
    _require(isinstance(value, _Number) and re.fullmatch(r'(?:0|[1-9][0-9]*)', value),
             'Noncanonical integer identifier')
    return str(value)


def validate_numeric_source(body: bytes, *, area: int, required_origins: list[dict]) -> dict:
    """Physical N validation, preserving foreign entities, lexical values and gaps."""
    _require(type(area) is int and area > 0, 'Invalid numeric area')
    numeric = _json(body, numeric=True)
    _require(isinstance(numeric, dict) and set(numeric) == {'id', 'values'}
             and _identifier(numeric['id']) == str(area) and isinstance(numeric['values'], list), 'Wrong numeric area/schema')
    entities, lookup = [], {}
    for p, entry in enumerate(numeric['values']):
        _require(isinstance(entry, dict) and set(entry) == {'e', 'v'} and isinstance(entry['v'], list), 'Invalid numeric entity schema')
        entity = _identifier(entry['e'])
        _require(entity not in lookup, 'Duplicate numeric entity')
        cells, values = [], {}
        for q, cell in enumerate(entry['v']):
            _require(isinstance(cell, dict) and set(cell) == {'i', 'v'}, 'Invalid numeric information schema')
            lid = _identifier(cell['i'])
            _require(lid not in values, 'Duplicate numeric information')
            value = cell['v']
            _require(value is None or type(value) is str or isinstance(value, _Number), 'Unsupported numeric value shape')
            kind = 'number' if isinstance(value, _Number) else 'null' if value is None else 'string'
            item = {'lid': lid, 'value_type': kind, 'value': str(value) if kind == 'number' else value,
                    'source_pointer': f'/values/{p}/v/{q}/v'}
            cells.append(item)
            values[lid] = item
        record = {'entity': entity, 'source_pointer': f'/values/{p}', 'values': cells}
        entities.append(record)
        lookup[entity] = (record, values)
    _require(isinstance(required_origins, list), 'Required origins must be an array')
    origins, missing = [], []
    for origin in required_origins:
        _require(isinstance(origin, dict) and type(origin.get('area')) is int and origin['area'] == area
                 and type(origin.get('lid')) is int and origin['lid'] >= 0
                 and type(origin.get('catalog_pointer')) is str and origin['catalog_pointer'].startswith('/')
                 and isinstance(origin.get('cadaster_entities'), list)
                 and all(type(e) is str and e for e in origin['cadaster_entities']), 'Invalid required numeric origin')
        cells = []
        for entity in origin['cadaster_entities']:
            found = lookup.get(entity)
            cell = found[1].get(str(origin['lid'])) if found else None
            if cell:
                cells.append({'entity': entity, **cell})
            else:
                gap = {'catalog_pointer': origin['catalog_pointer'], 'entity': entity, 'lid': str(origin['lid']),
                       'state': 'entity_not_stored' if found is None else 'information_not_stored',
                       'source_pointer': '/values' if found is None else found[0]['source_pointer'] + '/v'}
                missing.append(gap)
        origins.append({**origin, 'cells': cells})
    # Completeness is a transport claim and cannot be inferred from valid JSON bytes.
    return {'area': area, 'body_sha256': _sha(body), 'source_validated': True,
            'entities': entities, 'origins': origins, 'missing': missing}


# The legacy scope remains public; seven exact recent singletons require the
# active batch coordinator. Candidates and session receipts never grant budget.
_SCOPE = 'issue50/financial-202403-1005-native-four'
_POLICIES = {'attempts': 2, 'metadata_body_bytes': 5 * 1024 * 1024,
             'numeric_body_bytes': 64 * 1024 * 1024, 'timeout_seconds': 30,
             'deadline_seconds': 120, 'max_backoff_seconds': 5,
             'max_backoffs': 7, 'attempt_seconds': 1680, 'backoff_seconds': 35,
             'scheduling_seconds': 1715, 'max_failed_targets': 3, 'max_guard_streak': 2}
_EMPTY_HASH = '0' * 64


def _execution_job(job):
    _require(isinstance(job, dict) and job.get('contract') == JOB_CONTRACT
             and job.get('job_sha256') == _job_hash(job), 'Job hash/schema mismatch')
    scope = job.get('acquisition_scope')
    from . import financial_acquisition_batch as batch
    scopes = {batch._SCOPE + '/' + str(p): p for p in batch._ACQUIRE}
    period = 202403 if scope == _SCOPE else scopes.get(scope)
    _require(period is not None and len(job.get('descriptors', [])) == 1, 'Execution outside fixed acquisition scopes')
    _require(isinstance(job.get('policies'), dict) and all(key in _POLICIES and type(value) is int
             and 0 < value <= _POLICIES[key] for key, value in job['policies'].items()), 'Execution policies exceed fixed caps')
    if scope != _SCOPE:
        _require(set(job) == {'contract', 'version', 'acquisition_scope', 'catalogs', 'descriptors',
                             'policies', 'targets', 'job_sha256', 'executable'}
                 and type(job['version']) is int and job['version'] == 1 and job['executable'] is False,
                 'Closed batch member job schema required')
        _require(_canonical(job['policies']) == _canonical(batch._POLICIES), 'Closed batch policies differ')
    catalogs = _catalogs(job['catalogs'])
    name = 'new' if period >= 202503 else 'old'
    descriptor = _descriptor(catalogs[name], job['catalogs'][name], period)
    _require(_canonical(job['descriptors'][0]) == _canonical(descriptor), 'Execution descriptor differs from frozen catalog')
    expected = sorted((_target(o, period) for o in descriptor['source_offers'] if o['role'] != 'numeric'),
                      key=lambda t: t['target_key'])
    _require(_canonical(job['targets']) == _canonical(expected), 'Execution target set differs from descriptor')
    _require(len(descriptor['source_offers']) <= 7 and (scope == _SCOPE or len(descriptor['source_offers']) == 7),
             'Execution exceeds seven-file bound')
    return {t['target_key']: t for t in (_target(o, period) for o in descriptor['source_offers'])}


def _coordinator_gate(job, context):
    _require(type(job) is dict, 'Job must be an object')
    if job.get('acquisition_scope') != _SCOPE:
        from .financial_acquisition_batch import _authorize_member
        _authorize_member(job, context)


def _safe_destination(path):
    """Validate each existing ancestor before creating operational paths."""
    path = Path(path).absolute()
    _require(path.is_relative_to(_ROOT.absolute()), 'Destination outside package root')
    relative = path.relative_to(_ROOT.absolute())
    _require(len(relative.parts) >= 3 and relative.parts[:2] == ('data', 'runs')
             and all(p not in ('.', '..') and ':' not in p for p in relative.parts), 'Destination outside approved runs')
    current = _ROOT
    for part in relative.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            info = current.lstat()
            _require(not stat.S_ISLNK(info.st_mode) and not (getattr(info, 'st_file_attributes', 0) & 0x400),
                     'Destination symlink/reparse point forbidden')
    return path


def _authority_paths(job):
    base = _safe_destination(_ROOT / 'data/runs/financial-acquisition-authority')
    scope = _sha(job['acquisition_scope'].encode())
    return base / job['job_sha256'], base / ('scope-' + scope + '.binding.json'), base / ('scope-' + scope + '.lock')


def _write_exclusive(path, value):
    path = _safe_destination(path)
    with path.open('xb') as output:
        output.write(_canonical(value))
        output.flush()
        os.fsync(output.fileno())
    _require(path.read_bytes() == _canonical(value), 'Durable write verification failed')


def _replace_head(folder, head):
    _safe_destination(folder / 'head.json')
    temporary = folder / ('head-' + uuid.uuid4().hex + '.tmp')
    _write_exclusive(temporary, head)
    os.replace(temporary, folder / 'head.json')
    with (folder / 'head.json').open('r+b') as output:
        os.fsync(output.fileno())
    _require((folder / 'head.json').read_bytes() == _canonical(head), 'Head durability verification failed')


def _initial_state():
    return {'attempts': 0, 'body_bytes': 0, 'attempt_seconds': 0, 'backoff_seconds': 0,
            'backoffs': 0, 'failures': 0, 'failure_streak': 0, 'guard': '', 'guard_streak': 0,
            'failed_targets': [], 'targets': {}, 'pending': {}, 'sources': {}}


def _limits(job):
    return {**_POLICIES, **job['policies']}


def _body_cap(target, policies=None):
    policies = policies or _POLICIES
    return policies['numeric_body_bytes'] if target['role'] == 'numeric' else policies['metadata_body_bytes']


def _apply_record(state, record, targets, policies=None):
    """Recompute transitions, never trust persisted cumulative counter fields."""
    policies = policies or _POLICIES
    kind, attempt = record['kind'], record['attempt_id']
    for key in ('attempt_delta', 'reserved_bytes', 'reserved_attempt_seconds', 'reserved_backoff_seconds'):
        _require(type(record[key]) is int and record[key] >= 0, 'Counter underflow/type invalid')
    if kind != 'reserve':
        _require(record['attempt_delta'] == record['reserved_bytes'] == record['reserved_attempt_seconds'] == 0,
                 'Unexpected reservation counters on non-reserve record')
    if kind != 'backoff':
        _require(record['reserved_backoff_seconds'] == 0, 'Unexpected backoff reservation counters')
    if kind == 'reserve':
        key = record['target_key']
        _require(key in targets and attempt not in state['pending'] and not state['pending'], 'Invalid or pending attempt')
        target = state['targets'].setdefault(key, {'attempts': 0, 'body_bytes': 0, 'retryable': True})
        _require(record['attempt_delta'] == 1 and target['attempts'] < policies['attempts'] and target['retryable']
                 and key not in state['sources'] and len(state['failed_targets']) < policies['max_failed_targets']
                 and state['guard_streak'] < policies['max_guard_streak'], 'Attempt/failure guard exhausted')
        budget = _body_cap(targets[key], policies) - target['body_bytes']
        _require(budget > 0 and record['reserved_bytes'] == budget and record['reserved_attempt_seconds'] == policies['deadline_seconds']
                 and record['reserved_backoff_seconds'] == 0, 'Reservation counter reduced or inflated')
        _require(state['attempts'] < 14 and state['attempt_seconds'] + policies['deadline_seconds'] <= policies['attempt_seconds']
                 and state['attempt_seconds'] + state['backoff_seconds'] + policies['deadline_seconds'] <= policies['scheduling_seconds'],
                 'Scheduling/attempt budget exhausted')
        _require(state['body_bytes'] + budget <= 2 * policies['metadata_body_bytes'] + 5 * policies['numeric_body_bytes'],
                 'Aggregate body budget exhausted')
        target['attempts'] += 1
        target['body_bytes'] += budget
        state['attempts'] += 1
        state['body_bytes'] += budget
        state['attempt_seconds'] += policies['deadline_seconds']
        state['pending'][attempt] = copy.deepcopy(record)
    elif kind == 'identity':
        _require(attempt in state['pending'] and state['pending'][attempt]['kind'] == 'reserve'
                 and 'identity' not in state['pending'][attempt], 'Unknown/duplicate worker identity')
        identity = record['identity']
        _require(type(identity.get('pid')) is int and identity['pid'] > 0
                 and type(identity.get('creation_time')) is int and identity['creation_time'] > 0
                 and identity.get('contained') is True, 'Invalid worker identity')
        state['pending'][attempt]['identity'] = identity
    elif kind in ('finish', 'orphan'):
        _require(attempt in state['pending'] and state['pending'][attempt]['kind'] == 'reserve', 'Unknown attempt conclusion')
        reservation = state['pending'].pop(attempt)
        key, target = reservation['target_key'], state['targets'][reservation['target_key']]
        if kind == 'finish':
            _require(record.get('tree_extinct') is True, 'Conclusion requires verified owned tree extinction')
            observed, elapsed = record['observed_bytes'], record['observed_attempt_seconds']
            _require(type(observed) is int and 0 <= observed <= reservation['reserved_bytes']
                     and type(elapsed) is int and elapsed >= 0, 'Invalid observed counters')
            state['body_bytes'] += observed - reservation['reserved_bytes']
            target['body_bytes'] += observed - reservation['reserved_bytes']
            state['attempt_seconds'] += elapsed - reservation['reserved_attempt_seconds']
        success = record['status'] == 'source_complete'
        _require(kind != 'orphan' or not success, 'Orphan cannot accept source')
        target['retryable'] = record['retryable'] is True and not success
        if success:
            _require(isinstance(record['source_ref'], dict), 'Source conclusion missing reference')
            state['sources'][key] = record['source_ref']
            state['failure_streak'] = 0
        else:
            state['failures'] += 1
            state['failure_streak'] += 1
            if not target['retryable'] and key not in state['failed_targets']:
                state['failed_targets'].append(key)
        guard = record.get('guard', '')
        _require(type(guard) is str, 'Invalid guard classification')
        state['guard_streak'] = (state['guard_streak'] + 1 if state['guard'] == guard else 1) if guard else 0
        state['guard'] = guard
    elif kind == 'backoff':
        _require(not state['pending'] and attempt not in state['pending'] and record['reserved_backoff_seconds'] == policies['max_backoff_seconds']
                 and state['backoffs'] < policies['max_backoffs']
                 and state['backoff_seconds'] + policies['max_backoff_seconds'] <= policies['backoff_seconds']
                 and state['attempt_seconds'] + state['backoff_seconds'] + policies['max_backoff_seconds'] <= policies['scheduling_seconds'],
                 'Backoff budget exhausted or pending')
        state['backoffs'] += 1
        state['backoff_seconds'] += policies['max_backoff_seconds']
        state['pending'][attempt] = copy.deepcopy(record)
    elif kind == 'backoff_finish':
        _require(attempt in state['pending'] and state['pending'][attempt]['kind'] == 'backoff', 'Unknown backoff')
        observed = record['observed_backoff_seconds']
        _require(type(observed) is int and observed >= 0, 'Backoff observed counter invalid')
        state['backoff_seconds'] += observed - policies['max_backoff_seconds']
        state['pending'].pop(attempt)
    elif kind == 'backoff_orphan':
        _require(attempt in state['pending'] and state['pending'][attempt]['kind'] == 'backoff', 'Unknown orphan backoff')
        state['pending'].pop(attempt)  # full reservation remains charged
    elif kind == 'reuse':
        key = record['target_key']
        _require(key in targets and key not in state['sources'] and not state['pending'], 'Invalid reused source')
        state['sources'][key] = record['source_ref']
    elif kind == 'guard_failure':
        key, guard = record['target_key'], record['guard']
        _require(key in targets and not state['pending'] and type(guard) is str and guard, 'Invalid source validation guard')
        state['failures'] += 1
        state['failure_streak'] += 1
        if key not in state['failed_targets']:
            state['failed_targets'].append(key)
        state['guard_streak'] = state['guard_streak'] + 1 if state['guard'] == guard else 1
        state['guard'] = guard
    elif kind != 'recovery':
        raise ValueError('Unknown authority journal transition')
    _require(record['failure_count'] == state['failures'] and record['failure_streak'] == state['failure_streak'],
             'Failure counters disagree with transitions')


class _Authority:
    """One claim owner and journal writer; instances never escape their context."""
    def __init__(self, job, folder, bootstrap_sha256, records, state, targets):
        self.job, self.folder, self.bootstrap_sha256 = job, folder, bootstrap_sha256
        self.records, self.state, self.targets, self.active = records, state, targets, True
        self.policies = _limits(job)

    def commit(self, kind, *, attempt_id='', target_key='', session_id='', **details):
        _require(self.active, 'Authority claim is closed')
        record = {'sequence': len(self.records) + 1, 'previous_record_sha256': self.records[-1]['record_sha256'] if self.records else _EMPTY_HASH,
                  'kind': kind, 'job_sha256': self.job['job_sha256'], 'attempt_id': attempt_id,
                  'target_key': target_key, 'session_id': session_id, 'attempt_delta': 0,
                  'reserved_bytes': 0, 'observed_bytes': None, 'reserved_attempt_seconds': 0,
                  'observed_attempt_seconds': None, 'reserved_backoff_seconds': 0,
                  'observed_backoff_seconds': None, 'failure_count': self.state['failures'],
                  'failure_streak': self.state['failure_streak'], **details}
        candidate = copy.deepcopy(self.state)
        if kind in ('finish', 'orphan', 'guard_failure'):
            record['failure_count'] += record['status'] != 'source_complete'
            record['failure_streak'] = 0 if record['status'] == 'source_complete' else record['failure_streak'] + 1
        _apply_record(candidate, record, self.targets, self.policies)
        record['record_sha256'] = _sha(_canonical(record))
        with _safe_destination(self.folder / 'journal.jsonl').open('ab') as output:
            output.write(_canonical(record) + b'\n')
            output.flush()
            os.fsync(output.fileno())
        head = {'sequence': record['sequence'], 'record_sha256': record['record_sha256'],
                'state_sha256': _sha(_canonical(candidate))}
        _replace_head(self.folder, head)
        # Verify physical append and head before permitting any child creation.
        _require((self.folder / 'journal.jsonl').read_bytes().endswith(_canonical(record) + b'\n'), 'Journal commit verification failed')
        self.records.append(record)
        self.state = candidate
        return record


def initialize_authority(job: dict) -> str:
    _coordinator_gate(job, None)
    return _initialize_authority(job)


def _initialize_authority(job: dict, *, coordinator=None) -> str:
    """Explicit offline, exclusive bootstrap; never resets/rebinds an existing scope."""
    targets = _execution_job(job)
    _coordinator_gate(job, coordinator)
    folder, binding_path, lock = _authority_paths(job)
    lock.parent.mkdir(parents=True, exist_ok=True)
    with _claim(lock):
        _require(not binding_path.exists(), 'Scope binding already exists; no reset/rebinding')
        _safe_destination(folder).mkdir(exist_ok=False)
        bootstrap = {'contract': 'financial-acquisition-authority-v1', 'acquisition_scope': job['acquisition_scope'],
                     'job_sha256': job['job_sha256'], 'policies': _limits(job), 'targets': targets}
        pin = _sha(_canonical(bootstrap))
        _write_exclusive(folder / 'bootstrap.json', bootstrap)
        with (folder / 'journal.jsonl').open('xb') as output:
            output.flush()
            os.fsync(output.fileno())
        _replace_head(folder, {'sequence': 0, 'record_sha256': _EMPTY_HASH, 'state_sha256': _sha(_canonical(_initial_state()))})
        _write_exclusive(binding_path, {'acquisition_scope': job['acquisition_scope'], 'job_sha256': job['job_sha256'], 'bootstrap_sha256': pin})
        return pin


@contextmanager
def _open_authority(job, bootstrap_sha256, *, recover=False, coordinator=None):
    targets = _execution_job(job)
    _coordinator_gate(job, coordinator)
    folder, binding_path, lock = _authority_paths(job)
    _require(binding_path.is_file() and folder.is_dir(), 'Acquisition authority missing; explicit initialization required')
    for path in (folder, binding_path, lock, folder / 'bootstrap.json', folder / 'journal.jsonl', folder / 'head.json'):
        _safe_destination(path)
    with _claim(lock):
        binding = _json(binding_path.read_bytes())
        _require(binding == {'acquisition_scope': job['acquisition_scope'], 'job_sha256': job['job_sha256'],
                             'bootstrap_sha256': _digest(bootstrap_sha256)}, 'Scope job/bootstrap binding mismatch')
        raw = (folder / 'bootstrap.json').read_bytes()
        _require(_sha(raw) == bootstrap_sha256, 'Bootstrap hash mismatch')
        bootstrap = _json(raw)
        _require(bootstrap == {'contract': 'financial-acquisition-authority-v1', 'acquisition_scope': job['acquisition_scope'],
                              'job_sha256': job['job_sha256'], 'policies': _limits(job), 'targets': targets}, 'Bootstrap contract mismatch')
        journal = (folder / 'journal.jsonl').read_bytes()
        _require(not journal or journal.endswith(b'\n'), 'Partial journal tail blocks; never truncate')
        state, records, states = _initial_state(), [], [_initial_state()]
        for line in journal.splitlines():
            record = _json(line)
            pin = record.pop('record_sha256')
            _require(pin == _sha(_canonical(record)) and record['sequence'] == len(records) + 1
                     and record['job_sha256'] == job['job_sha256'] and record['previous_record_sha256'] ==
                     (records[-1]['record_sha256'] if records else _EMPTY_HASH), 'Journal chain integrity failure')
            _apply_record(state, record, targets, _limits(job))
            record['record_sha256'] = pin
            records.append(record)
            states.append(copy.deepcopy(state))
        head = _json((folder / 'head.json').read_bytes())
        sequence = head.get('sequence')
        _require(type(sequence) is int and 0 <= sequence <= len(records), 'Authority head ahead/invalid')
        _require(head == {'sequence': sequence, 'record_sha256': records[sequence - 1]['record_sha256'] if sequence else _EMPTY_HASH,
                          'state_sha256': _sha(_canonical(states[sequence]))}, 'Authority head/state digest mismatch')
        _require(recover or sequence == len(records), 'Authority head conflicts with complete journal tail; recover offline')
        if recover:
            for pending in state['pending'].values():
                if 'identity' in pending:
                    _require(identity_extinct(pending['identity']), 'Live worker blocks recovery before source reads')
        # Current accepted sources must still be physically authenticated.
        for key, ref in state['sources'].items():
            _authenticated(ref, expected=targets[key])
        authority = _Authority(job, folder, bootstrap_sha256, records, state, targets)
        try:
            if recover and sequence != len(records):
                _replace_head(folder, {'sequence': len(records), 'record_sha256': records[-1]['record_sha256'],
                                       'state_sha256': _sha(_canonical(state))})
            yield authority
        finally:
            authority.active = False


def open_authority(job: dict, *, bootstrap_sha256: str):
    return _open_authority(job, bootstrap_sha256)


def reserve_attempt(authority, target: dict, *, session_id: str) -> dict:
    _require(type(session_id) is str and re.fullmatch('[A-Za-z0-9_-]{1,80}', session_id), 'Invalid session ID')
    key = target.get('target_key')
    _require(key in authority.targets and target == authority.targets[key], 'Attempt target outside fixed job')
    used = authority.state['targets'].get(key, {}).get('body_bytes', 0)
    return authority.commit('reserve', attempt_id=uuid.uuid4().hex, target_key=key, session_id=session_id,
                            attempt_delta=1, reserved_bytes=_body_cap(target, authority.policies) - used,
                            reserved_attempt_seconds=authority.policies['deadline_seconds'])


def _receipt(authority, session_id):
    return {'contract': 'financial-acquisition-receipt-v1', 'job_sha256': authority.job['job_sha256'],
            'bootstrap_sha256': authority.bootstrap_sha256, 'sequence': len(authority.records),
            'record_sha256': authority.records[-1]['record_sha256'] if authority.records else _EMPTY_HASH,
            'state_sha256': _sha(_canonical(authority.state)), 'state': copy.deepcopy(authority.state), 'session_id': session_id}


def _verify_receipt(receipt, authority):
    _require(type(receipt) is dict, 'Receipt must be a JSON object')
    _require(receipt.get('contract') == 'financial-acquisition-receipt-v1' and receipt.get('job_sha256') == authority.job['job_sha256']
             and receipt.get('bootstrap_sha256') == authority.bootstrap_sha256, 'Receipt authority mismatch')
    sequence = receipt.get('sequence')
    _require(type(sequence) is int and 0 <= sequence <= len(authority.records), 'Receipt is ahead of current authority')
    state = _initial_state()
    for record in authority.records[:sequence]:
        _apply_record(state, record, authority.targets, authority.policies)
    _require(receipt.get('record_sha256') == (authority.records[sequence - 1]['record_sha256'] if sequence else _EMPTY_HASH)
             and receipt.get('state_sha256') == _sha(_canonical(state)) and receipt.get('state') == state, 'Receipt does not match journal prefix')


def _recover_pending(authority):
    # No body is opened before every durable identity is proved extinct. Job handle
    # is parent-only: releasing claim after parent crash closes it and kills tree.
    for pending in authority.state['pending'].values():
        if 'identity' in pending:
            _require(identity_extinct(pending['identity']), 'Live worker blocks offline recovery')
    for attempt, pending in list(authority.state['pending'].items()):
        authority.commit('backoff_orphan' if pending['kind'] == 'backoff' else 'orphan',
                         attempt_id=attempt, target_key=pending['target_key'], session_id=pending['session_id'],
                         status='orphan_charged', retryable=False)
    authority.commit('recovery')


def _load_job(path, pin):
    path = _local(Path(path).absolute().relative_to(_ROOT.absolute()).as_posix())
    job = _json(path.read_bytes())
    _require(type(job) is dict, 'Job must be a JSON object')
    _require(job.get('job_sha256') == _digest(pin) == _job_hash(job), 'External job hash mismatch')
    _execution_job(job)
    return job


def recover_authority(job_path: Path, job_sha256: str, *, bootstrap_sha256: str, output: Path) -> dict:
    job = _load_job(job_path, job_sha256)
    destination = _safe_destination(output)
    _require(not destination.exists(), 'Recovery receipt destination must be new')
    with _open_authority(job, bootstrap_sha256, recover=True) as authority:
        _recover_pending(authority)
        receipt = _receipt(authority, 'recovery-' + uuid.uuid4().hex)
        destination.parent.mkdir(parents=True, exist_ok=True)
        _write_exclusive(destination, receipt)
        return receipt


def verify_authority(job_path: Path, job_sha256: str, *, bootstrap_sha256: str,
                     receipt_path: Path | None = None, receipt_sha256: str | None = None) -> dict:
    """Authenticate the current authority and optional receipt offline, without recovery."""
    job = _load_job(job_path, job_sha256)
    _require((receipt_path is None) == (receipt_sha256 is None), 'Receipt requires external pin')
    _require(_authority_paths(job)[2].is_file(), 'Existing authority claim file required for readonly verification')
    with open_authority(job, bootstrap_sha256=bootstrap_sha256) as authority:
        receipt = None
        if receipt_path is not None:
            path = _local(Path(receipt_path).absolute().relative_to(_ROOT.absolute()).as_posix())
            raw = path.read_bytes()
            _require(_sha(raw) == _digest(receipt_sha256), 'Receipt hash mismatch')
            receipt = _json(raw)
            _verify_receipt(receipt, authority)
        state = authority.state
        result = {'status': 'verified_pending' if state['pending'] else 'verified',
                  'job_sha256': job_sha256, 'bootstrap_sha256': bootstrap_sha256,
                  'sequence': len(authority.records),
                  'record_sha256': authority.records[-1]['record_sha256'] if authority.records else _EMPTY_HASH,
                  'state_sha256': _sha(_canonical(state)), 'pending_attempts': len(state['pending'])}
        result.update({key: state[key] for key in ('attempts', 'body_bytes', 'attempt_seconds',
                                                  'backoff_seconds', 'backoffs', 'failures')})
        if receipt is not None:
            result.update(receipt_sha256=receipt_sha256, receipt_sequence=receipt['sequence'],
                          receipt_is_historical=receipt['sequence'] != len(authority.records))
        return result


def _worker_authorization(spec):
    """Read-only current authority proof while its sole writer holds the claim."""
    job = _load_job(_ROOT / spec['job_path'], spec['job_sha256'])
    targets = _execution_job(job)
    _coordinator_gate(job, None)  # v1 workers cannot execute a batch member.
    folder, binding_path, _ = _authority_paths(job)
    binding = _json(_local(binding_path.relative_to(_ROOT).as_posix()).read_bytes())
    _require(binding == {'acquisition_scope': job['acquisition_scope'], 'job_sha256': job['job_sha256'],
                         'bootstrap_sha256': spec['bootstrap_sha256']}, 'Worker scope/bootstrap binding mismatch')
    _require(_sha(_local((folder / 'bootstrap.json').relative_to(_ROOT).as_posix()).read_bytes()) == spec['bootstrap_sha256'],
             'Worker bootstrap hash mismatch')
    raw = _local((folder / 'journal.jsonl').relative_to(_ROOT).as_posix()).read_bytes()
    _require(raw.endswith(b'\n'), 'Worker journal partial/missing')
    state, previous, sequence = _initial_state(), _EMPTY_HASH, 0
    for line in raw.splitlines():
        record = _json(line)
        pin = record.pop('record_sha256')
        sequence += 1
        _require(pin == _sha(_canonical(record)) and record['sequence'] == sequence
                 and record['previous_record_sha256'] == previous and record['job_sha256'] == job['job_sha256'], 'Worker journal integrity failure')
        _apply_record(state, record, targets, _limits(job))
        previous = pin
    head = _json(_local((folder / 'head.json').relative_to(_ROOT).as_posix()).read_bytes())
    _require(head == {'sequence': sequence, 'record_sha256': previous, 'state_sha256': _sha(_canonical(state))}, 'Worker authority head mismatch')
    pending = state['pending'].get(spec['attempt_id'])
    _require(pending and pending['kind'] == 'reserve' and pending['target_key'] == spec['target_key']
             and pending['reserved_bytes'] == spec['body_budget_bytes'] and 'identity' in pending, 'Worker lacks current durable reservation/identity')
    verify_worker_ancestry(pending['identity'], spec['parent_identity'])
    return job, targets[spec['target_key']]


def _worker_main(spec_path, spec_sha256):
    """Internal known worker: standalone invocation cannot bypass reservation."""
    require_supported()
    path = _local(Path(spec_path).absolute().relative_to(_ROOT.absolute()).as_posix())
    raw = path.read_bytes()
    _require(_sha(raw) == _digest(spec_sha256), 'Worker spec hash mismatch')
    spec = _json(raw)
    _require(set(spec) == {'contract', 'job_path', 'job_sha256', 'bootstrap_sha256', 'attempt_id', 'target_key',
                          'body_budget_bytes', 'parent_identity', 'application_sha256', 'worker_sha256', 'output_path'}
             and spec['contract'] == 'financial-acquisition-worker-v1'
             and spec['worker_sha256'] == _sha(Path(__file__).read_bytes())
             and spec['application_sha256'] == _sha(Path(sys.executable).read_bytes()), 'Worker contract/runtime pin mismatch')
    job, target = _worker_authorization(spec)
    destination = _safe_destination(_ROOT / spec['output_path'])
    _require(not destination.exists(), 'Worker destination must be new')
    destination.mkdir()
    # Imported only after all authorization checks; this is the sole request site.
    from .archive import fetch_bounded
    manifest = fetch_bounded(target['url'], destination, spec['attempt_id'],
                             {'period': target['period'], 'perspective': 1005, 'role': target['role']},
                             body_budget_bytes=spec['body_budget_bytes'], timeout_seconds=_limits(job)['timeout_seconds'])
    manifest_path = destination / manifest['manifest_path']
    for name in (manifest['body_path'], manifest['manifest_path'], manifest.get('response_metadata_path')):
        if name:
            with _safe_destination(destination / name).open('r+b') as saved:
                os.fsync(saved.fileno())
    _write_exclusive(destination / 'worker-receipt.json', {'attempt_id': spec['attempt_id'],
                     'spec_sha256': spec_sha256, 'manifest_path': manifest_path.relative_to(_ROOT).as_posix(),
                     'manifest_sha256': _sha(manifest_path.read_bytes())})


def _retryable(manifest):
    diagnostics = manifest.get('diagnostics', [])
    if not isinstance(diagnostics, list):
        return False
    codes = {item.get('code') for item in diagnostics if isinstance(item, dict)}
    status = manifest.get('http_status')
    if manifest.get('outcome') == 'http_error' and codes <= {'http_status'}:
        return status in (408, 429) or (type(status) is int and 500 <= status <= 599)
    # The transport preserves a typed code and exception text. Unknown errors are
    # deliberately nonretryable; certificate/configuration failures are excluded.
    if manifest.get('outcome') == 'network_error' and codes == {'transport_exception'}:
        details = ' '.join(item.get('detail', '') for item in diagnostics)
        return any(token in details for token in ('TimeoutError', 'timed out', 'ConnectionResetError',
                                                   'ConnectionAbortedError', 'ConnectionRefusedError',
                                                   'Temporary failure in name resolution'))
    return False


def _attempt(authority, job_path, session, target):
    reservation = reserve_attempt(authority, target, session_id=session.name)
    attempt = reservation['attempt_id']
    spec_path = session / ('worker-' + attempt + '.json')
    output = session / ('attempt-' + attempt)
    spec = {'contract': 'financial-acquisition-worker-v1', 'job_path': Path(job_path).absolute().relative_to(_ROOT.absolute()).as_posix(),
            'job_sha256': authority.job['job_sha256'], 'bootstrap_sha256': authority.bootstrap_sha256,
            'attempt_id': attempt, 'target_key': target['target_key'], 'body_budget_bytes': reservation['reserved_bytes'],
            'parent_identity': _current_identity(), 'worker_sha256': _sha(Path(__file__).read_bytes()),
            'application_sha256': _sha(Path(sys.executable).read_bytes()), 'output_path': output.relative_to(_ROOT).as_posix()}
    _write_exclusive(spec_path, spec)
    spec_pin = _sha(spec_path.read_bytes())
    def before_resume(identity):
        authority.commit('identity', attempt_id=attempt, target_key=target['target_key'], session_id=session.name, identity=identity,
                         spec_path=spec_path.relative_to(_ROOT).as_posix(), spec_sha256=spec_pin)
    result = run_contained_attempt(spec_path, spec_pin, deadline_seconds=authority.policies['deadline_seconds'], before_resume=before_resume)
    _require(result['tree_extinct'], 'Worker tree extinction not verified')
    observed, status, retryable, source, guard = reservation['reserved_bytes'], 'worker_failed', False, None, 'containment'
    evidence = {}
    # A missing/inconclusive receipt never proves zero bytes and never refunds.
    if result['deadline_reached'] or result['deadline_overshoot_seconds'] > 0:
        status, guard = 'deadline', 'deadline'
    elif result['exit_code'] == 0:
        receipt_path = _local((output / 'worker-receipt.json').relative_to(_ROOT).as_posix())
        receipt = _json(receipt_path.read_bytes())
        _require(receipt['attempt_id'] == attempt and receipt['spec_sha256'] == spec_pin, 'Worker receipt mismatch')
        manifest_path = _local(receipt['manifest_path'])
        _require(manifest_path.parent == output, 'Worker manifest outside immutable attempt directory')
        manifest_raw = manifest_path.read_bytes()
        _require(_sha(manifest_raw) == _digest(receipt['manifest_sha256']), 'Attempt manifest hash mismatch')
        manifest = _json(manifest_raw)
        evidence = {'worker_receipt_path': receipt_path.relative_to(_ROOT).as_posix(),
                    'worker_receipt_sha256': _sha(receipt_path.read_bytes()), 'manifest_path': receipt['manifest_path'],
                    'manifest_sha256': receipt['manifest_sha256']}
        _require(manifest.get('contract') == 'bounded-http-archive-v1' and manifest.get('url') == target['url']
                 and manifest.get('method') == 'GET'
                 and manifest.get('context') == {'period': target['period'], 'perspective': 1005, 'role': target['role']}
                 and manifest.get('body_budget_bytes') == reservation['reserved_bytes'], 'Attempt manifest context mismatch')
        bytes_seen = manifest.get('bytes_observed')
        _require(type(bytes_seen) is int and 0 <= bytes_seen <= reservation['reserved_bytes'], 'Attempt observed body counter invalid')
        # Validate saved body and sidecar even for a failed request before refund.
        _require(manifest.get('body_available') is True and manifest.get('bytes') == bytes_seen,
                 'Inconclusive stored byte count')
        body = _saved_body(manifest, manifest_path, manifest.get('sha256'))
        _require(len(body) == bytes_seen, 'Attempt body byte count mismatch')
        observed = bytes_seen
        source = {**target, 'manifest_path': receipt['manifest_path'], 'manifest_sha256': receipt['manifest_sha256'],
                  'body_sha256': manifest['sha256'], 'provenance_sha256': _sha(_canonical(manifest)), 'context': _native(manifest['context'])}
        if manifest.get('source_complete') is True and manifest.get('outcome') == 'ok':
            _authenticated(source, expected=target)
            status, guard = 'source_complete', ''
        else:
            _failed_attempt_evidence(manifest, manifest_path)
            source = None
            status, retryable = manifest.get('outcome', 'transport_error'), _retryable(manifest)
            guard = '' if retryable else 'transport'
    used_attempts = authority.state['targets'][target['target_key']]['attempts']
    retryable = retryable and used_attempts < authority.policies['attempts'] and observed < reservation['reserved_bytes']
    authority.commit('finish', attempt_id=attempt, target_key=target['target_key'], session_id=session.name,
                     observed_bytes=observed, observed_attempt_seconds=math.ceil(result['elapsed_seconds']),
                     actual_elapsed_microseconds=math.ceil(result['elapsed_seconds'] * 1000000),
                     overshoot_microseconds=math.ceil(result['deadline_overshoot_seconds'] * 1000000),
                     status=status, retryable=retryable, source_ref=source, guard=guard, attempt_evidence=evidence,
                     tree_extinct=True, worker_exit_code=result['exit_code'], deadline_reached=result['deadline_reached'])
    return retryable


def _obtain(authority, job_path, session, target):
    key = target['target_key']
    if key in authority.state['sources']:
        return
    reused = authority.job.get('reuse_sources', {}).get(key)
    if reused:
        _authenticated(reused, expected=target)
        authority.commit('reuse', target_key=key, session_id=session.name, source_ref=reused)
        return
    while key not in authority.state['sources']:
        if not _attempt(authority, job_path, session, target):
            break
        backoff = authority.commit('backoff', attempt_id=uuid.uuid4().hex, target_key=key,
                                   session_id=session.name, reserved_backoff_seconds=authority.policies['max_backoff_seconds'])
        began = time.monotonic()
        time.sleep(max(0, authority.policies['max_backoff_seconds'] - .05))
        elapsed = time.monotonic() - began
        authority.commit('backoff_finish', attempt_id=backoff['attempt_id'], target_key=key,
                         session_id=session.name, observed_backoff_seconds=math.ceil(elapsed),
                         actual_elapsed_microseconds=math.ceil(elapsed * 1000000))


def _run_acquisition(job_path: Path, job_sha256: str, session: Path, *, phase: str, bootstrap_sha256: str,
                     coordinator=None,
                    checkpoint_sha256: str | None = None, resume_from: Path | None = None,
                    resume_sha256: str | None = None) -> dict:
    require_supported()
    job = _load_job(job_path, job_sha256)
    _require(phase in ('metadata', 'values'), 'Unknown acquisition phase')
    _require((resume_from is None) == (resume_sha256 is None), 'Resume receipt requires external pin')
    _require(phase != 'values' or checkpoint_sha256 is not None, 'Values require physical checkpoint A pin')
    session = _safe_destination(session)
    _require(re.fullmatch('[A-Za-z0-9_-]{1,80}', session.name) and not session.exists(), 'Session destination must be new with safe ID')
    _coordinator_gate(job, coordinator)
    with _open_authority(job, bootstrap_sha256, coordinator=coordinator) as authority:
        _require(not authority.state['pending'], 'Pending attempt requires offline recovery before any new launch')
        if resume_from is not None:
            raw = _local(Path(resume_from).absolute().relative_to(_ROOT.absolute()).as_posix()).read_bytes()
            _require(_sha(raw) == _digest(resume_sha256), 'Resume receipt hash mismatch')
            _verify_receipt(_json(raw), authority)
        checkpoint = None
        if phase == 'values':
            _require(resume_from is not None, 'Values require checkpoint A receipt location')
            a_path = _local((Path(resume_from).absolute().parent / 'checkpoint-a.json').relative_to(_ROOT.absolute()).as_posix())
            raw = a_path.read_bytes()
            _require(_sha(raw) == _digest(checkpoint_sha256), 'Physical checkpoint A hash mismatch')
            checkpoint = _json(raw)
            refs = {target['target_key']: authority.state['sources'][target['target_key']] for target in job['targets']
                    if target['target_key'] in authority.state['sources']}
            resolved = resolve_sources(job, refs)
            _require(checkpoint == resolved['checkpoints'][0], 'Checkpoint A differs from revalidated physical sources')
            _require(all(authority.state['sources'].get(key) == ref for key, ref in refs.items()), 'Checkpoint sources differ from current authority')
        session.mkdir(parents=True)
        try:
            if phase == 'metadata':
                for target in job['targets']:
                    _obtain(authority, job_path, session, target)
                refs = {t['target_key']: authority.state['sources'][t['target_key']] for t in job['targets'] if t['target_key'] in authority.state['sources']}
                _require(len(refs) == len(job['targets']), 'Metadata source set incomplete; no checkpoint acceptance')
                failed_key = next(t['target_key'] for t in job['targets'] if t['role'] == 'cadaster')
                try:
                    body, _ = _authenticated(refs[failed_key], expected=authority.targets[failed_key])
                    _cadaster(body, job['descriptors'][0]['selection']['period'])
                    failed_key = next(t['target_key'] for t in job['targets'] if t['role'] == 'dictionary')
                    resolved = resolve_sources(job, refs)
                except ValueError as error:
                    authority.commit('guard_failure', target_key=failed_key, session_id=session.name,
                                     status='source_schema_failed', guard='schema', diagnostic=str(error))
                    raise
                _write_exclusive(session / 'checkpoint-a.json', resolved['checkpoints'][0])
                _write_exclusive(session / 'resolution.json', resolved)
            else:
                for target in resolved['numeric_targets']:
                    _obtain(authority, job_path, session, target)
                    _require(target['target_key'] in authority.state['sources'], 'Numeric source missing; no complete acceptance')
                    body, _ = _authenticated(authority.state['sources'][target['target_key']], expected=target)
                    origins = [n['origin'] for r in resolved['resolutions'] for n in r['nodes']
                               if n['kind'] == 'numeric' and n['origin']['area'] == target['area']]
                    try:
                        validation = validate_numeric_source(body, area=target['area'], required_origins=origins)
                    except ValueError as error:
                        authority.commit('guard_failure', target_key=target['target_key'], session_id=session.name,
                                         status='source_schema_failed', guard='schema', diagnostic=str(error))
                        raise
                    _write_exclusive(session / ('numeric-' + str(target['area']) + '-validation.json'), validation)
                complete = {**checkpoint, 'phase': 'complete', 'checkpoint_a_sha256': checkpoint_sha256,
                            'sources': sorted(checkpoint['sources'] + [{key: authority.state['sources'][t['target_key']][key]
                                               for key in ('source_id', 'role', 'area', 'native_file', 'catalog_pointer',
                                                           'manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256')}
                                              for t in resolved['numeric_targets']],
                                              key=lambda ref: ref['source_id'])}
                _write_exclusive(session / 'checkpoint-b.json', complete)
        finally:
            _write_exclusive(session / 'receipt.json', _receipt(authority, session.name))
        return _receipt(authority, session.name)


def run_acquisition(job_path: Path, job_sha256: str, session: Path, *, phase: str, bootstrap_sha256: str,
                    checkpoint_sha256: str | None = None, resume_from: Path | None = None,
                    resume_sha256: str | None = None) -> dict:
    job = _load_job(job_path, job_sha256)
    _coordinator_gate(job, None)
    return _run_acquisition(job_path, job_sha256, session, phase=phase, bootstrap_sha256=bootstrap_sha256,
                            checkpoint_sha256=checkpoint_sha256, resume_from=resume_from, resume_sha256=resume_sha256)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Internal contained worker requires authenticated spec and SHA-256')
    _worker_main(Path(sys.argv[1]), sys.argv[2])

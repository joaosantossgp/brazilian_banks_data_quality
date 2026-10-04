"""Finite, authenticated offline source resolution; no acquisition authority/admission.

Catalog indexes use financial-acquisition-catalog-index-v1 and pinned O/N captures.
Source provenance hashes cover the complete manifest with fractional JSON numbers
represented as {json_number: lexical_token}, as in the existing financial reader.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import quote

from .archive import load_body


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
        sidecar_name = manifest.get('response_metadata_path')
        _require(type(sidecar_name) is str and sidecar_name and '\\' not in sidecar_name and ':' not in sidecar_name
                 and all(p not in ('', '.', '..') for p in sidecar_name.split('/')), 'Response metadata path escape')
        sidecar_path = _local((path.parent.relative_to(_ROOT) / PurePosixPath(sidecar_name)).as_posix())
        sidecar_body = sidecar_path.read_bytes()
        _require(_sha(sidecar_body) == _digest(manifest.get('response_metadata_sha256')), 'Response metadata hash mismatch')
        sidecar = _json(sidecar_body)
        _require(isinstance(sidecar, dict) and all(sidecar.get(key) == manifest.get(key)
                 for key in ('http_status', 'final_url', 'response_headers_raw')), 'Response metadata projection mismatch')
        raw_headers = manifest.get('response_headers_raw')
        _require(isinstance(raw_headers, list) and all(isinstance(pair, list) and len(pair) == 2
                 and all(type(value) is str for value in pair) for pair in raw_headers), 'Invalid raw response headers')
        headers = {}
        for name, value in raw_headers:
            headers.setdefault(name.lower(), []).append(value.strip())
        lengths = headers.get('content-length', [])
        transfers = headers.get('transfer-encoding', [])
        encodings = headers.get('content-encoding', [])
        _require(not lengths or (len(lengths) == 1 and re.fullmatch('[0-9]+', lengths[0])
                 and int(lengths[0]) == length), 'Invalid Content-Length header evidence')
        _require(lengths or length is None, 'Content-Length header missing')
        _require(not transfers or (not lengths and transfers == ['chunked']), 'Ambiguous framing headers')
        _require(not encodings or encodings == ['identity'], 'Unexpected Content-Encoding headers')
        _require((manifest['completion_basis'] == 'chunked_eof') == bool(transfers), 'Completion basis/header mismatch')
    _require(manifest.get('sha256') == ref['body_sha256'], 'Source body pin mismatch')
    name = manifest.get('body_path')
    _require(type(name) is str and name and '\\' not in name and ':' not in name
             and all(p not in ('', '.', '..') for p in name.split('/')), 'Body path escape')
    body_path = _local((path.parent.relative_to(_ROOT) / PurePosixPath(name)).as_posix())
    body = load_body(manifest, path.parent)
    _require(_sha(body) == ref['body_sha256'] and type(manifest.get('bytes')) is int
             and len(body) == manifest['bytes'], 'Source body size/hash mismatch')
    _require(body_path.is_file(), 'Source body missing')
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
    _require(type(index['acquisition_scope']) is str and index['acquisition_scope'].startswith('issue50/')
             and len(index['acquisition_scope']) > 8, 'Invalid acquisition_scope')
    _require(isinstance(periods, tuple) and periods and all(type(p) is int and p in _MEMBERS for p in periods)
             and len(set(periods)) == len(periods), 'Select an explicit unique subset of the frozen 66 periods')
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

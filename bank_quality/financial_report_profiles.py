"""Finite installed offer registry and explicit offline profile authoring.

Catalog offers are not admitted sources. Authoring returns artifacts and never
writes the installed package or activates a selection. Source contexts remain
those of the original archived requests, including the two exact legacy pins.
"""
import copy
from datetime import datetime, timedelta
import hashlib
from pathlib import Path, PurePosixPath
import re
from urllib.parse import parse_qsl, urlsplit

from . import financial as legacy
from . import financial_reports as reports

PACKAGE_ROOT = Path(__file__).resolve().parent
CHECKOUT_ROOT = PACKAGE_ROOT.parent
REGISTRY_CONTRACT = 'ifdata-financial-reports-registry-v1'
SOURCES_CONTRACT = 'ifdata-financial-historical-sources-v1'
CANDIDATE_CONTRACT = 'ifdata-financial-reports-historical-candidate-v1'
PROFILE_CONTRACT = 'ifdata-financial-reports-historical-profile-v1'
SNAPSHOT_CONTRACT = 'ifdata-financial-reports-historical-snapshot-v1'
PARQUET_CONTRACT = 'ifdata-financial-reports-historical-parquet-v1'
_require = legacy._require
_json = legacy._json
_canonical = legacy._canonical
_native = reports._metadata_native


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _digest(value):
    return _sha(_canonical(value).encode('utf-8'))


def _same(actual, expected, message):
    _require(_canonical(actual) == _canonical(expected), message)


def _hash(value):
    _require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'Invalid SHA-256')
    return value


def _reparse(path):
    """Reject symlinks and Windows junctions before following any component."""
    _require(not path.is_symlink(), 'Symlink source path is forbidden')
    if path.exists():
        _require(not getattr(path.lstat(), 'st_file_attributes', 0) & 0x400,
                 'Reparse-point source path is forbidden')


def _contained(root, name, *, source=False):
    _require(type(name) is str and name and '\\' not in name and ':' not in name,
             'Path must be a canonical relative local path')
    parts = PurePosixPath(name).parts
    _require(not name.startswith('/') and all(p not in ('.', '..') for p in parts)
             and '/'.join(parts) == name, 'Path is absolute or escapes its anchor')
    if source:
        _require(len(parts) >= 3 and parts[:2] in (('data', 'raw'), ('data', 'runs')),
                 'Source path is outside data/raw or data/runs')
    current = root
    _reparse(current)
    for part in parts:
        current = current / part
        _reparse(current)
    _require(current.resolve().is_relative_to(root.resolve()), 'Path escapes fixed root')
    return current


def _read_hashed(path, digest):
    body = Path(path).read_bytes()
    _require(_sha(body) == _hash(digest), 'External SHA-256 mismatch')
    return body, _json(body)


def _offer_payload(member):
    return {key: member[key] for key in ('selection', 'catalog', 'reports', 'source_offers')}


def _registry():
    value = _json(_contained(PACKAGE_ROOT, 'financial-reports-registry.json').read_bytes())
    _require(isinstance(value, dict) and value.get('contract') == REGISTRY_CONTRACT
             and isinstance(value.get('members'), list), 'Invalid installed registry')
    return value


def descriptor_for_selection(selection: dict) -> dict:
    """Accept only the canonical, ordered selection installed by the integrator."""
    _require(isinstance(selection, dict) and set(selection) == {'period', 'perspective', 'reports'}
             and type(selection['period']) is int and type(selection['perspective']) is int
             and selection['perspective'] == 1005 and isinstance(selection['reports'], list)
             and len(selection['reports']) == 4 and all(type(n) is int for n in selection['reports'])
             and len(set(selection['reports'])) == 4, 'Noncanonical financial selection')
    registry = _registry()
    matches = [m for m in registry['members'] if _canonical(m.get('selection')) == _canonical(selection)]
    _require(len(matches) == 1, 'Selection is not a unique installed offer')
    member = copy.deepcopy(matches[0])
    digest = _digest(_offer_payload(member))
    if 'descriptor_sha256' in member:
        _require(member['descriptor_sha256'] == digest, 'Installed descriptor digest mismatch')
    member['descriptor_sha256'] = digest
    return member


def load_installed_context(selection: dict) -> dict:
    descriptor = descriptor_for_selection(selection)
    name, digest = descriptor.get('profile_path'), descriptor.get('profile_sha256')
    _require(type(name) is str and type(digest) is str, 'Installed active profile is absent')
    period = selection['period']
    allowed = (f'financial-reports-profile-{period}.json' if period in (202412, 202503)
               else f'financial-reports-profiles/{period}.json')
    _require(name == allowed, 'Installed profile path is outside permitted package artifacts')
    profile_path = _contained(PACKAGE_ROOT, name)
    _require(profile_path.is_file(), 'Installed active profile file is absent')
    body = profile_path.read_bytes()
    _require(_sha(body.replace(b'\r\n', b'\n')) == _hash(digest), 'Installed profile SHA-256 mismatch')
    if period in (202412, 202503):
        profile = _json(body)
        _require(profile.get('contract') == f'ifdata-financial-reports-profile-{period}-v1',
                 'Legacy installed contract mismatch')
        _same(profile.get('selection'), selection, 'Legacy installed selection mismatch')
        # Keep the original context and annotations; the reviewed old files are immutable.
        return reports._context(selection)
    profile = _json(body)
    _require(profile.get('contract') == PROFILE_CONTRACT
             and profile.get('descriptor_sha256') == descriptor['descriptor_sha256'],
             'Installed historical profile mismatch')
    _same(profile.get('selection'), selection, 'Installed historical selection mismatch')
    _same([r['report']['id'] for r in profile['reports']], selection['reports'], 'Installed reports mismatch')
    _require(profile.get('missing_sources') == [] and set(profile.get('source_pins', {})) == set(profile['required_sources']),
             'Installed historical sources are incomplete')
    _validate_installed_profile(profile, descriptor)
    envelope = {'contract': SNAPSHOT_CONTRACT, 'period': period, 'perspective': 'financial', 'perspective_id': 1005}
    return {'period': period, 'selection': copy.deepcopy(selection), 'contract': SNAPSHOT_CONTRACT,
            'envelope': envelope, 'part': f'parts/financial-cells-{period}.parquet',
            'parquet_contract': PARQUET_CONTRACT, 'profile': profile, 'profile_body': body,
            'profile_sha256': digest, 'cadaster_columns': profile['cadaster_columns'],
            'cad_csv_fields': profile['cad_csv_fields'], 'source_members': profile['source_members'],
            'limitations': profile['limitations']}


def _validate_installed_profile(profile, descriptor):
    columns = profile.get('cadaster_columns')
    _require(isinstance(columns, list) and len(columns) >= 2 and columns == [f'c{i}' for i in range(len(columns))],
             'Installed native cadaster columns invalid')
    _same(profile.get('cad_csv_fields'), ['contract', 'period', 'perspective', 'perspective_id', *columns,
                                        'source_body', 'source_sha256', 'source_pointer'], 'Installed cadaster CSV schema mismatch')
    offers = {s['source_id']: s for s in descriptor['source_offers']}
    required = {'catalog', 'cadaster', 'dictionary', 'portal'}
    _require(len(profile['reports']) == len(descriptor['reports']), 'Installed report tree incomplete')
    for item, expected in zip(profile['reports'], descriptor['reports']):
        _same(item['report'], expected['report'], 'Installed report differs from native offer')
        _same(item['catalog_pointer'], expected['catalog_pointer'], 'Installed report pointer differs')
        tree = list(reports._walk(item['report']['c'], item['catalog_pointer'] + '/c'))
        _require(len(tree) == len(item['nodes']), 'Installed binding tree incomplete')
        for (column, pointer, parent), node in zip(tree, item['nodes']):
            association = {'report_id': item['report']['id'], 'column_id': column['id'], 'ifd': column['ifd'], 'fid': column['fid'],
                           'catalog_pointer': pointer, 'parent_pointer': parent,
                           'children_pointers': [pointer + '/sc/' + str(i) for i in range(len(column['sc']))]}
            _same({k: node.get(k) for k in association}, association, 'Installed node differs from native tree')
            definition = node.get('definition')
            _require(isinstance(definition, dict) and all(type(definition.get(k)) is int for k in ('id', 'td', 'a', 'lid')),
                     'Installed binding definition invalid')
            association = {'ifd': definition['id'], 'td': definition['td'], 'area': definition['a'], 'lid': definition['lid'], 'name': definition.get('n')}
            _same({k: node.get(k) for k in association}, association, 'Installed definition association differs')
            group = bool(column['sc'])
            if group:
                _require(node['td'] == 2 and node['lid'] == -1, 'Installed group origin invalid')
                origin, sid, kind = 'group', None, 'group'
            elif node['td'] == 1:
                _require(f"c{node['lid']}" in columns, 'Installed cadaster localizer absent')
                origin, sid, kind = 'cadaster', 'cadaster', 'quantity' if column['fid'] == 2 else 'attribute'
            else:
                _require(node['td'] == 3 and node['lid'] >= 0 and type(node['area']) is int and node['area'] > 0,
                         'Installed numeric origin invalid')
                origin, sid, kind = 'numeric', f"numeric:{node['area']}", 'numeric'
                _require(sid in offers, 'Installed numeric origin unadvertised')
                required.add(sid)
            _same([node.get('origin_kind'), node.get('origin_source_id'), node.get('kind')], [origin, sid, kind],
                  'Installed binding origin mismatch')
            expected_annotations = {'unit': '' if group else 'unknown',
                                    'unit_basis': '' if group else 'unknown: no binding-specific evidence',
                                    'window_start': '', 'window_end': '',
                                    'window_basis': '' if group else 'unknown: no binding-specific evidence'}
            _same({k: node.get(k) for k in expected_annotations}, expected_annotations,
                  'Unreviewed installed unit/window interpretation')
    _same(profile['required_sources'], sorted(required), 'Installed required members differ')
    members = profile.get('source_members')
    _require(isinstance(members, dict) and set(members) == required, 'Installed source map incomplete/extra')
    paths = set()
    for sid, record in members.items():
        role = 'numeric' if sid.startswith('numeric:') else sid
        area = int(sid.split(':')[1]) if role == 'numeric' else None
        _same([record.get('source_id'), record.get('role'), record.get('area')], [sid, role, area], 'Installed source map origin ambiguous')
        if sid in offers:
            _same({k: record.get(k) for k in offers[sid]}, offers[sid], 'Installed source differs from advertisement')
        _require(record.get('manifest_path') not in paths, 'Installed source manifests ambiguous')
        paths.add(record.get('manifest_path'))
        pin = profile['source_pins'][sid]
        _same({k: record.get(k) for k in ('manifest_sha256', 'body_sha256', 'provenance_sha256')},
              {k: pin.get(k) for k in ('manifest_sha256', 'body_sha256', 'provenance_sha256')},
              'Installed source pins differ from map')
        _require('manifest' not in record and 'response_headers' not in record
                 and _digest(record) == pin.get('projection_sha256'), 'Installed source projection mismatch')


def _pointer(value, pointer):
    _require(type(pointer) is str and pointer.startswith('/'), 'Invalid catalog pointer')
    for part in pointer[1:].split('/'):
        if isinstance(value, list):
            _require(re.fullmatch('0|[1-9][0-9]*', part) is not None and int(part) < len(value), 'Catalog pointer missing')
            value = value[int(part)]
        else:
            _require(isinstance(value, dict) and part in value, 'Catalog pointer missing')
            value = value[part]
    return value


def _bounded_source_completion(manifest, path):
    """Revalidate the archive contract for new/reused C/D/N, not JSON alone."""
    _require(manifest.get('contract') == 'bounded-http-archive-v1'
             and manifest.get('source_complete') is True and manifest.get('body_available') is True
             and manifest.get('truncated') is False and manifest.get('diagnostics') == [],
             'Dataset requires a complete bounded capture')
    observed, budget, length = (manifest.get(key) for key in
                                ('bytes_observed', 'body_budget_bytes', 'content_length'))
    basis, eof = manifest.get('completion_basis'), manifest.get('eof_observed')
    _require(type(observed) is int and observed == manifest.get('bytes')
             and type(budget) is int and 0 < observed <= budget,
             'Bounded source byte counters invalid')
    _require(length is None or (type(length) is int and length >= 0 and length == observed),
             'Bounded source Content-Length mismatch')
    _require(type(eof) is bool and basis in ('eof', 'chunked_eof', 'content_length')
             and ((basis == 'content_length' and length is not None and eof is False)
                  or (basis in ('eof', 'chunked_eof') and eof is True and observed < budget)),
             'Bounded source lacks coherent terminal framing')
    sidecar_path = _contained(path.parent, manifest.get('response_metadata_path'))
    _require(sidecar_path.is_file(), 'Response metadata is missing')
    _, sidecar = _read_hashed(sidecar_path, manifest.get('response_metadata_sha256'))
    evidence_keys = ('url', 'method', 'context', 'http_status', 'final_url', 'response_headers_raw')
    _require(isinstance(sidecar, dict) and all(key in sidecar for key in evidence_keys),
             'Response metadata evidence missing')
    for key in evidence_keys + ('started_at_utc',):
        _same(sidecar.get(key), manifest.get(key), 'Response metadata projection/context mismatch: ' + key)
    raw = manifest.get('response_headers_raw')
    _require(isinstance(raw, list) and all(isinstance(pair, list) and len(pair) == 2
             and all(type(value) is str for value in pair) for pair in raw), 'Invalid raw response headers')
    _same(manifest.get('response_headers'), dict(raw), 'Response header projection mismatch')
    headers = {}
    for name, value in raw:
        headers.setdefault(name.lower(), []).append(value.strip())
    lengths, transfers, encodings = (headers.get(key, []) for key in
                                    ('content-length', 'transfer-encoding', 'content-encoding'))
    _require((not lengths and length is None)
             or (len(lengths) == 1 and re.fullmatch('[0-9]+', lengths[0])
                 and int(lengths[0]) == length), 'Invalid Content-Length header evidence')
    _require(not transfers or (not lengths and transfers == ['chunked']), 'Ambiguous framing headers')
    _require(not encodings or encodings == ['identity'], 'Unexpected Content-Encoding headers')
    _require((basis == 'chunked_eof') == bool(transfers), 'Completion basis/header mismatch')


def _authenticate_source(source, descriptor):
    _require(isinstance(source, dict), 'Invalid source member')
    role, sid, area = source.get('role'), source.get('source_id'), source.get('area')
    _require(role in ('catalog', 'cadaster', 'dictionary', 'portal', 'numeric')
             and sid == (f'numeric:{area}' if role == 'numeric' else role)
             and ((role == 'numeric' and type(area) is int and area > 0) or (role != 'numeric' and area is None)),
             'Wrong source identity, role or area')
    if descriptor['selection']['period'] == 202312:
        _authenticate_legacy_member(source)
    path = _contained(CHECKOUT_ROOT, source.get('manifest_path'), source=True)
    manifest_body, manifest = _read_hashed(path, source.get('manifest_sha256'))
    _require(_digest(_native(manifest)) == _hash(source.get('provenance_sha256')), 'Source provenance differs')
    _require(isinstance(manifest, dict) and manifest.get('method') == 'GET'
             and type(manifest.get('http_status')) is int and manifest['http_status'] == 200
             and manifest.get('outcome') == 'ok', 'Source manifest failed or incomplete')
    legacy_exception = None
    if descriptor['selection']['period'] == 202312 and role in ('dictionary', 'numeric') and area in (None, 1):
        legacy_profile = _json(_contained(PACKAGE_ROOT, 'financial-profile-202312.json').read_bytes())
        legacy_exception = legacy_profile['legacy_sources'][role]
        if source['manifest_sha256'] != legacy_exception['manifest_sha256']:
            legacy_exception = None
    if legacy_exception:
        _require(manifest.get('sha256') == legacy_exception['body_sha256'] and 'truncated' not in manifest
                 and manifest.get('diagnostics') == legacy_exception['diagnostics']
                 and isinstance(manifest.get('context'), dict)
                 and manifest['context'].get('body_capture') == legacy_exception['body_capture'], 'Unreviewed legacy exception')
    else:
        _require(manifest.get('truncated') is False and manifest.get('diagnostics') == [], 'Source completeness is not proven')
    _require(isinstance(manifest.get('context'), dict), 'Source context missing')
    utc = manifest.get('retrieved_at_utc')
    try:
        valid_utc = type(utc) is str and datetime.fromisoformat(utc).utcoffset() == timedelta(0)
    except ValueError:
        valid_utc = False
    _require(valid_utc, 'Source retrieval must be UTC')
    for key in ('url', 'final_url'):
        _require(type(manifest.get(key)) is str, 'Missing source URL')
        url = urlsplit(manifest[key])
        _require(url.scheme == 'https' and url.netloc == 'www3.bcb.gov.br' and not url.fragment,
                 'Source URL is outside official endpoint')
        if role == 'catalog':
            expected = '/ifdata/rest/relatorios2000a2024' if descriptor['selection']['period'] < 202500 else '/ifdata/rest/relatorios2025a2030'
            _require(url.path == expected and not url.query, 'Wrong catalog URL')
        elif role == 'portal':
            _require(url.path == '/ifdata/index.html' and not url.query, 'Wrong portal URL')
        else:
            _require(url.path == '/ifdata/rest/arquivos' and parse_qsl(url.query, keep_blank_values=True) ==
                     [('nomeArquivo', source.get('native_file'))], 'Wrong literal advertised source URL')
    _require(type(manifest.get('bytes')) is int and 0 < manifest['bytes'] <= 64 * 1024 * 1024, 'Source byte bound exceeded')
    body_path = _contained(path.parent, manifest.get('body_path'))
    body = body_path.read_bytes()
    _require(len(body) == manifest['bytes'] and _sha(body) == manifest.get('sha256') == _hash(source.get('body_sha256')),
             'Source body integrity mismatch')
    if descriptor['selection']['period'] != 202312 and role in ('cadaster', 'dictionary', 'numeric'):
        _bounded_source_completion(manifest, path)
    headers = manifest.get('response_headers')
    _require(isinstance(headers, dict), 'Source framing evidence missing')
    folded = {k.lower(): v for k, v in headers.items()}
    if not legacy_exception and (descriptor['selection']['period'] == 202312 or role in ('catalog', 'portal')):
        encoding = folded.get('content-encoding', 'identity').lower()
        _require(encoding in ('', 'identity'), 'Encoded body requires an explicit reviewed capture contract')
        if 'content-length' in folded:
            length = folded['content-length']
            _require(type(length) is str and re.fullmatch('[0-9]+', length) and int(length) == len(body), 'Source framing length mismatch')
        else:
            _require(folded.get('transfer-encoding', '').lower() == 'chunked', 'Source framing length/transfer evidence missing')
    record = {**copy.deepcopy(source), 'manifest': _native(manifest), 'body_path': manifest['body_path'],
              'source_generation_state': 'unknown', 'truncation_state': 'undeclared_legacy' if legacy_exception else 'observed_false'}
    return body, record


def _authenticate_legacy_member(source):
    """Five exact archived sources, independent of caller-supplied new hashes."""
    pins = _registry().get('legacy_202312_sources')
    _require(isinstance(pins, dict) and set(pins) == {'catalog', 'cadaster', 'dictionary', 'portal', 'numeric:1'},
             'Reviewed legacy five-source pins are absent')
    sid = source.get('source_id')
    _require(sid in pins, 'Legacy source is outside reviewed five-source bundle')
    _same({k: source.get(k) for k in pins[sid]}, pins[sid], 'Legacy source/context/path differs from exact reviewed pins')
    path = _contained(CHECKOUT_ROOT, source['manifest_path'], source=True)
    _read_hashed(path, pins[sid]['manifest_sha256'])


def _project_source_record(record):
    """Minimal installable projection; entire original manifest remains private."""
    manifest = record['manifest']
    result = {k: record[k] for k in ('source_id', 'role', 'area', 'native_file', 'catalog_pointer', 'manifest_path',
                                    'manifest_sha256', 'body_sha256', 'provenance_sha256', 'body_path',
                                    'source_generation_state', 'truncation_state')}
    result.update({k: copy.deepcopy(manifest[k]) for k in ('url', 'final_url', 'retrieved_at_utc', 'bytes', 'context',
                                                         'method', 'http_status', 'outcome', 'diagnostics')})
    if 'truncated' in manifest:
        result['truncated'] = manifest['truncated']
    return result


def _authenticate_installed_source(source, context):
    """Admission authenticates original bytes before confronting public projection.

    Accepted-snapshot queries use installed metadata and their authenticated
    companions, without depending on the external archive at query time.
    """
    descriptor = descriptor_for_selection(context['selection'])
    body, record = _authenticate_source(source, descriptor)
    sid = record['source_id']
    expected = context['profile']['source_members'].get(sid)
    _require(expected is not None, 'Source is not a required installed member')
    projected = _project_source_record(record)
    _same(projected, expected, 'Authenticated original source differs from installed projection')
    _require(_digest(projected) == context['profile']['source_pins'][sid]['projection_sha256'],
             'Authenticated original projection pin differs')
    return body, projected


def _validate_numeric(body, area):
    data = _json(body, numeric=True)
    _require(isinstance(data, dict) and legacy._number_id(data.get('id')) == str(area)
             and isinstance(data.get('values'), list), 'Invalid numeric shard schema')
    entities = set()
    for entity in data['values']:
        _require(isinstance(entity, dict) and isinstance(entity.get('v'), list), 'Invalid numeric entity schema')
        code = legacy._number_id(entity.get('e'))
        _require(code not in entities, 'Duplicate numeric entity')
        entities.add(code)
        localizers = set()
        for cell in entity['v']:
            _require(isinstance(cell, dict) and 'v' in cell, 'Invalid numeric cell schema')
            lid = legacy._number_id(cell.get('i'))
            _require(lid not in localizers, 'Duplicate numeric localizer')
            localizers.add(lid)
            legacy._value(cell['v'])


def _compile(handoff, handoff_sha256):
    _require(isinstance(handoff, dict) and handoff.get('contract') == SOURCES_CONTRACT
             and handoff.get('phase') in ('metadata', 'complete'), 'Invalid historical handoff contract/phase')
    _require(not any(k in handoff for k in ('root', 'base', 'profile_path', 'profile_sha256', 'accepted')), 'Caller override is forbidden')
    descriptor = descriptor_for_selection(handoff.get('selection'))
    _require(handoff.get('descriptor_sha256') == descriptor['descriptor_sha256'], 'Handoff descriptor mismatch')
    _same(handoff.get('catalog'), descriptor['catalog'], 'Handoff catalog pins/pointer mismatch')
    source_list = handoff.get('sources')
    _require(isinstance(source_list, list), 'Handoff sources must be ordered explicit members')
    members, bodies = {}, {}
    offers = {s['source_id']: s for s in descriptor['source_offers']}
    paths = set()
    for source in source_list:
        sid = source.get('source_id')
        _require(sid not in members and source.get('manifest_path') not in paths, 'Duplicate source ID or manifest')
        paths.add(source.get('manifest_path'))
        _require(sid in offers or sid in ('catalog', 'portal'), 'Unadvertised source member')
        if sid in offers:
            _same({k: source.get(k) for k in offers[sid]}, offers[sid], 'Source does not match native advertisement')
        if sid == 'catalog':
            _same({k: source.get(k) for k in ('manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256')},
                  {k: descriptor['catalog'][k] for k in ('manifest_path', 'manifest_sha256', 'body_sha256', 'provenance_sha256')}, 'Catalog source differs from installed pins')
        bodies[sid], members[sid] = _authenticate_source(source, descriptor)
    _require(all(s in members for s in ('catalog', 'cadaster', 'dictionary')), 'C/D/O metadata sources missing')
    catalog = _json(bodies['catalog'])
    entry = _pointer(catalog, descriptor['catalog']['reference_pointer'])
    _require(type(entry.get('dt')) is int and entry['dt'] == descriptor['selection']['period'], 'Catalog reference mismatch')
    for offer in offers.values():
        _same(_pointer(catalog, offer['catalog_pointer']), offer['native_file'], 'Native source advertisement mismatch')
    cadaster = _json(bodies['cadaster'])
    _require(isinstance(cadaster, list) and cadaster and isinstance(cadaster[0], dict), 'Missing native cadaster')
    columns = sorted(cadaster[0], key=lambda k: int(k[1:]) if re.fullmatch('c[0-9]+', k) else -1)
    _require(columns == [f'c{i}' for i in range(len(columns))] and len(columns) >= 2, 'Invalid native cadaster fields')
    codes = set()
    for row in cadaster:
        _require(isinstance(row, dict) and set(row) == set(columns) and all(type(v) is str for v in row.values())
                 and row['c0'] and row['c1'] == str(descriptor['selection']['period']) and row['c0'] not in codes,
                 'Native cadaster schema/reference/identity mismatch')
        codes.add(row['c0'])
    definitions = _json(bodies['dictionary'])
    _require(isinstance(definitions, list), 'Dictionary must be native array')
    infos = {}
    for position, info in enumerate(definitions):
        _require(isinstance(info, dict) and type(info.get('id')) is int and info['id'] not in infos, 'Invalid dictionary identity')
        infos[info['id']] = (position, info)
    compiled, required = [], {'catalog', 'cadaster', 'dictionary', 'portal'}
    for expected in descriptor['reports']:
        native_report = _pointer(catalog, expected['catalog_pointer'])
        _same(_native(native_report), expected['report'], 'Native report metadata/tree differs from installed offer')
        perspectives = native_report.get('s')
        _require(isinstance(perspectives, list) and all(isinstance(p, dict) and type(p.get('id')) is int for p in perspectives)
                 and len({p['id'] for p in perspectives}) == len(perspectives)
                 and sum(p['id'] == 1005 for p in perspectives) == 1, 'Native financial report membership invalid')
        nodes, ids = [], set()
        for column, pointer, parent in reports._walk(native_report['c'], expected['catalog_pointer'] + '/c'):
            _require(column['id'] not in ids and column['ifd'] in infos, 'Duplicate column or missing definition')
            ids.add(column['id'])
            position, info = infos[column['ifd']]
            _require(all(type(info.get(k)) is int for k in ('td', 'a', 'lid')) and type(info.get('n')) is str, 'Invalid binding definition')
            group = bool(column['sc'])
            if group:
                _require(info['td'] == 2 and info['lid'] == -1, 'Unsupported native group origin')
                origin, sid, kind = 'group', None, 'group'
            elif info['td'] == 1:
                _require(f"c{info['lid']}" in columns, 'Binding refers to absent cadaster field')
                origin, sid = 'cadaster', 'cadaster'
                kind = 'quantity' if column['fid'] == 2 else 'attribute'
            else:
                _require(info['td'] == 3 and info['lid'] >= 0 and info['a'] > 0, 'Unsupported native leaf origin')
                origin, sid, kind = 'numeric', f"numeric:{info['a']}", 'numeric'
                _require(sid in offers, 'Numeric origin is not advertised')
                required.add(sid)
            nodes.append({'report_id': native_report['id'], 'column_id': column['id'], 'ifd': column['ifd'],
                          'fid': column['fid'], 'td': info['td'], 'area': info['a'], 'lid': info['lid'], 'name': info['n'],
                          'catalog_pointer': pointer, 'parent_pointer': parent,
                          'children_pointers': [pointer + '/sc/' + str(n) for n in range(len(column['sc']))],
                          'definition': _native(info), 'definition_pointer': '/' + str(position),
                          'origin_kind': origin, 'origin_source_id': sid, 'kind': kind,
                          'unit': '' if group else 'unknown', 'unit_basis': '' if group else 'unknown: no binding-specific evidence',
                          'window_start': '', 'window_end': '', 'window_basis': '' if group else 'unknown: no binding-specific evidence'})
        compiled.append({'report': _native(native_report), 'catalog_pointer': expected['catalog_pointer'], 'nodes': nodes})
    for sid in members:
        if sid.startswith('numeric:'):
            _require(sid in required, 'Unrequired numeric source in handoff')
            _validate_numeric(bodies[sid], members[sid]['area'])
    if 'legacy_index' in handoff:
        original = handoff['legacy_index']
        body = original.get('body_utf8', '').encode('utf-8')
        _require(_sha(body) == original.get('body_sha256'), 'Legacy index bytes/hash mismatch')
        _same(_json(body).get('selection'), {'period': 202312, 'perspective': 1005, 'report': 92}, 'Legacy index original selection mismatch')
        _require(descriptor['selection']['period'] == 202312, 'Legacy wrapper is restricted to202312')
        replay = wrap_legacy_202312_index(Path(original['index_path']), index_sha256=original['body_sha256'])
        _same(original, replay['legacy_index'], 'Legacy wrapper original index differs')
        _same(source_list, replay['sources'], 'Legacy wrapper must retain all original source members')
    return {'contract': CANDIDATE_CONTRACT, 'selection': descriptor['selection'], 'descriptor_sha256': descriptor['descriptor_sha256'],
            'catalog': descriptor['catalog'], 'reports': compiled, 'cadaster_columns': columns,
            'cad_csv_fields': ['contract', 'period', 'perspective', 'perspective_id', *columns, 'source_body', 'source_sha256', 'source_pointer'],
            'required_sources': sorted(required), 'missing_sources': sorted(required - members.keys()),
            'source_members': members, 'source_pins': {sid: {key: members[sid][key] for key in
                                                     ('manifest_sha256', 'body_sha256', 'provenance_sha256')} for sid in members},
            'metadata_handoff_sha256': handoff_sha256, 'legacy_index': copy.deepcopy(handoff.get('legacy_index')),
            'limitations': ['Native metadata and source correspondence only; no harmonization or academic eligibility.',
                            'Units and windows unknown without binding-specific evidence; no scaling or annualization.',
                            'Catalog offer, candidate and frozen artifact do not activate admission.']}


def compile_metadata_candidate(handoff_path: Path, *, handoff_sha256: str) -> dict:
    """Capture a physical metadata checkpoint inside the internally fixed root."""
    original = Path(handoff_path).absolute()
    root = CHECKOUT_ROOT.absolute()
    _require(original.is_relative_to(root), 'Metadata checkpoint is outside fixed root')
    name = original.relative_to(root).as_posix()
    path = _contained(CHECKOUT_ROOT, name)
    _require(path.is_file(), 'Physical metadata checkpoint is absent')
    _, handoff = _read_hashed(path, handoff_sha256)
    _require(handoff.get('phase') == 'metadata', 'Checkpoint A requires metadata phase')
    candidate = _compile(handoff, handoff_sha256)
    candidate['metadata_handoff_path'] = name
    return candidate


def freeze_profile(candidate_path: Path, final_handoff_path: Path, *, candidate_sha256: str, final_handoff_sha256: str) -> dict:
    _, candidate = _read_hashed(candidate_path, candidate_sha256)
    _, final = _read_hashed(final_handoff_path, final_handoff_sha256)
    _require(candidate.get('contract') == CANDIDATE_CONTRACT and final.get('phase') == 'complete', 'Freeze requires candidate and complete final handoff')
    checkpoint = _contained(CHECKOUT_ROOT, candidate.get('metadata_handoff_path'))
    original = compile_metadata_candidate(checkpoint, handoff_sha256=candidate.get('metadata_handoff_sha256'))
    _same(candidate, original, 'Candidate differs from physically authenticated checkpoint A')
    # The legacy wrapper has no acquisition checkpoint link. Its original index
    # and all five exact installed source pins are reauthenticated by _compile.
    _require(final.get('checkpoint_a_sha256') == original['metadata_handoff_sha256'] or
             ('checkpoint_a_sha256' not in final and original.get('legacy_index') is not None
              and final.get('legacy_index') == original['legacy_index']),
             'Final handoff is not anchored to metadata checkpoint')
    compiled = _compile(final, final_handoff_sha256)
    _require(compiled['missing_sources'] == [], 'Freeze requires complete authenticated numeric and portal sources')
    for key in ('selection', 'descriptor_sha256', 'catalog', 'reports', 'cadaster_columns', 'cad_csv_fields', 'required_sources', 'legacy_index', 'limitations'):
        _same(candidate.get(key), compiled.get(key), 'Candidate differs from authenticated native metadata: ' + key)
    for sid, record in candidate['source_members'].items():
        _same(record, compiled['source_members'].get(sid), 'Final source differs from original metadata source')
    compiled['contract'] = PROFILE_CONTRACT
    compiled['metadata_handoff_sha256'] = candidate['metadata_handoff_sha256']
    compiled['final_handoff_sha256'] = final_handoff_sha256
    for sid, record in compiled['source_members'].items():
        projected = _project_source_record(record)
        compiled['source_members'][sid] = projected
        compiled['source_pins'][sid]['projection_sha256'] = _digest(projected)
    if compiled.get('legacy_index'):
        original = compiled['legacy_index']
        compiled['legacy_index'] = {k: original[k] for k in ('body_sha256', 'selection')}
    return compiled


def wrap_legacy_202312_index(index_path: Path, *, index_sha256: str) -> dict:
    body, index = _read_hashed(index_path, index_sha256)
    _same(index.get('selection'), {'period': 202312, 'perspective': 1005, 'report': 92}, 'Wrong legacy Summary selection')
    _require(index.get('contract') == 'ifdata-financial-sources-v1' and isinstance(index.get('sources'), dict)
             and set(index['sources']) == legacy.ROLES, 'Wrong legacy five-source index')
    selection = {'period': 202312, 'perspective': 1005, 'reports': [92, 96, 101, 98]}
    descriptor = descriptor_for_selection(selection)
    context = legacy._profile_for_selection(index['selection'])
    profile = context['profile']
    source_list = []
    offers = {s['source_id']: s for s in descriptor['source_offers']}
    pinned = _registry().get('legacy_202312_sources')
    _require(isinstance(pinned, dict) and set(pinned) == {'catalog', 'cadaster', 'dictionary', 'portal', 'numeric:1'},
             'Reviewed legacy five-source pins are absent')
    for role in ('catalog', 'cadaster', 'dictionary', 'portal', 'numeric'):
        name = index['sources'][role]
        _require(type(name) is str and not Path(name).is_absolute() and ':' not in name, 'Invalid legacy indexed path')
        unresolved = Path(index_path).absolute().parent / name
        for component in (unresolved, *unresolved.parents):
            _reparse(component)
        original = unresolved.resolve()
        _require(original.is_relative_to(CHECKOUT_ROOT.resolve()), 'Legacy path escapes actual checkout')
        anchored = original.relative_to(CHECKOUT_ROOT.resolve()).as_posix()
        path = _contained(CHECKOUT_ROOT, anchored, source=True)
        source_body, record = legacy._source(role, path, context)
        pin = profile.get('source_pins', {}).get(role) or profile.get('legacy_sources', {}).get(role)
        # Summary pins constrain all originally reviewed source contexts, not just D/N.
        if pin is not None:
            _require(record['sha256'] == pin['body_sha256'] and record['manifest_sha256'] == pin['manifest_sha256'], 'Legacy source pins mismatch')
            _require(_digest(record) == pin['provenance_sha256'], 'Legacy source context/provenance mismatch')
        if role == 'portal':
            _require(record['sha256'] == profile['source_baseline']['portal_sha256']
                     and all(fragment in source_body.decode('utf-8') for fragment in profile['formatter_fragments']), 'Legacy portal baseline mismatch')
        sid = 'numeric:1' if role == 'numeric' else role
        manifest = _json(path.read_bytes())
        member = {'source_id': sid, 'role': role, 'area': 1 if role == 'numeric' else None,
                            'native_file': offers[sid]['native_file'] if sid in offers else None,
                            'catalog_pointer': offers[sid]['catalog_pointer'] if sid in offers else None,
                            'manifest_path': anchored, 'manifest_sha256': _sha(path.read_bytes()),
                            'body_sha256': record['sha256'], 'provenance_sha256': _digest(_native(manifest))}
        _same(member, pinned[sid], 'Legacy source differs from reviewed original source/context/path')
        source_list.append(member)
    return {'contract': SOURCES_CONTRACT, 'phase': 'metadata', 'selection': selection,
            'descriptor_sha256': descriptor['descriptor_sha256'], 'catalog': descriptor['catalog'], 'sources': source_list,
            'legacy_index': {'body_utf8': body.decode('utf-8'), 'body_sha256': index_sha256,
                             'selection': copy.deepcopy(index['selection']), 'index_path': str(Path(index_path).resolve())}}

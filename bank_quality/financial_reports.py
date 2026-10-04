"""Closed offline admission of the four native financial reports in202412/202503.

The installed profile is trusted metadata. An index selects only local archived
manifests; it cannot select a profile, period, perspective or report subset.
"""
from collections import Counter
import copy
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import io
from itertools import zip_longest
import os
from pathlib import Path
import re

from . import financial as legacy
from .inventory import classify

CONTRACT = 'ifdata-financial-reports-snapshot-202412-v1'
INDEX_CONTRACT = 'ifdata-financial-reports-sources-v1'
PROFILE_CONTRACT = 'ifdata-financial-reports-profile-202412-v1'
SELECTION = {'period': 202412, 'perspective': 1005, 'reports': [92, 96, 101, 98]}
PROFILE_PATH = Path(__file__).with_name('financial-reports-profile-202412.json')
PROFILE_202503_PATH = Path(__file__).with_name('financial-reports-profile-202503.json')
FIELDS = legacy.FIELDS
ROLES = legacy.ROLES
INPUTS = ('financial-observations.csv', 'financial-cells.csv', 'financial-cadastro.csv',
          'financial-variables.json', 'financial-diagnostics.json')
ENVELOPE = {'contract': CONTRACT, 'period': 202412, 'perspective': 'financial', 'perspective_id': 1005}
CAD_FIELDS = [*ENVELOPE, *(f'c{i}' for i in range(38)), 'source_body', 'source_sha256', 'source_pointer']
BIND_FIELDS = ('ifd', 'td', 'area', 'lid', 'fid', 'catalog_pointer', 'definition_pointer',
               'unit', 'unit_basis', 'window_start', 'window_end', 'window_basis')
LIMITATIONS = [
    'Native source-key correspondence only; no legal, issuer or academic eligibility.',
    'Raw BRL unit and stock window are inferred; income is July-December, not annual.',
    'Non-simultaneous source retrieval; shared source contexts remain unchanged.',
    'Unstored cells are neither source NI nor zero; no imputation or aggregation.',
    'Opaque formulas, flags and formatter metadata are preserved, never executed.',
    'No historical, prudential, individual or 2025 equivalence is certified.']
_require = legacy._require
_json = legacy._json
_canonical = legacy._canonical


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _same(actual, expected, message):
    _require(_canonical(actual) == _canonical(expected), message)


def _metadata_native(value):
    """Tag non-integer JSON numbers so opaque metadata never passes through float.

    Structural integer IDs stay integers. The original JSON source and pointer
    remain authoritative; a number tag is distinct from an ordinary string.
    """
    if isinstance(value, legacy.NumberLexeme):
        return {'json_number': str(value)}
    if isinstance(value, dict):
        return {k: _metadata_native(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_metadata_native(v) for v in value]
    return value


def _walk(columns, base, parent=None):
    _require(isinstance(columns, list), 'Invalid report column tree')
    for position, column in enumerate(columns):
        _require(isinstance(column, dict) and type(column.get('id')) is int
                 and type(column.get('ifd')) is int and type(column.get('fid')) is int
                 and isinstance(column.get('sc'), list), 'Invalid report column')
        pointer = base + '/' + str(position)
        yield column, pointer, parent
        yield from _walk(column['sc'], pointer + '/sc', pointer)


def _annotations(kind, flow):
    """Closed202503 interpretation; native definitions/formulas remain opaque."""
    return {'unit': '' if kind == 'group' else 'BRL_raw_inferred' if kind == 'money' else 'count' if kind == 'quantity' else 'text',
            'unit_basis': '' if kind == 'group' else 'archived_formatter_divides_by_1000' if kind == 'money' else 'cadaster_definition',
            'window_start': '2025-01-01' if flow else '',
            'window_end': '' if kind == 'group' else '2025-03-31',
            'window_basis': '' if kind == 'group' else 'report_rp_result_window' if flow else 'stock_at_reference_inferred' if kind == 'money' else 'cadaster_reference'}


def _context(selection=None):
    """Load the installed closed profile without mutable legacy globals."""
    selection = copy.deepcopy(SELECTION if selection is None else selection)
    _require(isinstance(selection, dict) and type(selection.get('period')) is int
             and selection['period'] in (202412, 202503), 'Wrong closed financial selection')
    period = selection['period']
    expected = {'period': period, 'perspective': 1005,
                'reports': [92, 96, 101, 98] if period == 202412 else [119, 107, 110, 118]}
    _same(selection, expected, 'Wrong closed financial selection')
    contract = f'ifdata-financial-reports-snapshot-{period}-v1'
    envelope = {'contract': contract, 'period': period, 'perspective': 'financial', 'perspective_id': 1005}
    limitations = list(LIMITATIONS)
    if period == 202503:
        limitations[1] = 'Raw BRL unit and stock window are inferred; income is January-March, not annual.'
        limitations[-1] = 'No historical, prudential, individual or cross-regime 2024/2025 equivalence is certified.'
    body = (PROFILE_PATH if period == 202412 else PROFILE_202503_PATH).read_bytes()
    profile = _json(body)
    _require(isinstance(profile, dict) and profile.get('contract') == f'ifdata-financial-reports-profile-{period}-v1',
             'Invalid installed four-report profile')
    _same(profile.get('selection'), expected, 'Invalid installed profile selection')
    _require(profile.get('cadaster_fields') == 38 and set(profile.get('source_pins', {})) == ROLES,
             'Incomplete installed profile')
    reports = profile.get('reports')
    _require(isinstance(reports, list) and _canonical([r['report']['id'] for r in reports]) == _canonical(expected['reports']),
             'Invalid installed report membership')
    for item in reports:
        report, nodes, pointer = item['report'], item['nodes'], item['catalog_pointer']
        _require(isinstance(nodes, list) and type(pointer) is str, 'Invalid installed report metadata')
        _same(report.get('s'), [{'id': 1005}], 'Wrong installed report perspective')
        columns = list(_walk(report['c'], pointer + '/c'))
        _require(len(columns) == len(nodes), 'Incomplete installed binding tree')
        ids = set()
        for (column, ptr, parent), node in zip(columns, nodes):
            _require(column['id'] not in ids, 'Duplicate report column identifier')
            ids.add(column['id'])
            binding_expected = {'report_id': report['id'], 'column_id': column['id'], 'ifd': column['ifd'],
                        'fid': column['fid'], 'catalog_pointer': ptr, 'parent_pointer': parent,
                        'children_pointers': [ptr + '/sc/' + str(n) for n in range(len(column['sc']))]}
            _require(all(_canonical(node.get(k)) == _canonical(v) for k, v in binding_expected.items()),
                     'Installed binding differs from report tree')
            definition = node['definition']
            for key, source in (('ifd', 'id'), ('td', 'td'), ('area', 'a'), ('lid', 'lid')):
                _require(type(definition.get(source)) is int and node[key] == definition[source],
                         'Invalid installed definition association')
            _require(node['name'] == definition['n'] and node['area'] == 1, 'Invalid installed definition')
            group = bool(column['sc'])
            _require((group and node['kind'] == 'group' and node['td'] == 2 and node['lid'] == -1)
                     or (not group and node['kind'] in ('attribute', 'quantity') and node['td'] == 1
                         and 0 <= node['lid'] < 38)
                     or (not group and node['kind'] == 'money' and node['td'] == 3 and node['lid'] >= 0),
                     'Unsupported installed binding origin')
            if period == 202503:
                kind = 'group' if group else 'money' if node['td'] == 3 else 'quantity' if column['fid'] == 2 else 'attribute'
                _require(node['kind'] == kind, 'Invalid installed kind annotation')
                flow = kind == 'money' and (report['id'] == 118 or report['id'] == 119 and node['ifd'] == 79859)
                annotations = _annotations(kind, flow)
                _same({k: node.get(k) for k in annotations}, annotations, 'Invalid installed unit/window annotations')
    return {'period': period, 'selection': expected, 'contract': contract, 'envelope': envelope,
            'part': f'parts/financial-cells-{period}.parquet',
            'parquet_contract': f'ifdata-financial-reports-parquet-{period}-v1',
            'catalog_prefix': f'ifdata/{period}/' if period == 202412 else 'ifdata_2025_2030//202503/',
            'limitations': limitations, 'profile': profile, 'profile_body': body,
            'profile_sha256': _sha(body.replace(b'\r\n', b'\n'))}


def _check_sources(sources, context):
    _require(isinstance(sources, dict) and set(sources) == ROLES, 'Incomplete source provenance')
    for role, record in sources.items():
        _require(isinstance(record, dict) and set(record) == {'url', 'final_url', 'retrieved_at_utc',
                 'bytes', 'sha256', 'body_path', 'context', 'manifest_sha256',
                 'source_generation_state', 'indexed_manifest'}, 'Invalid source provenance fields')
        name = record['indexed_manifest']
        _require(type(name) is str and name and not Path(name).is_absolute()
                 and not re.match(r'^[A-Za-z]:', name), 'Indexed manifest must be relative local path')
        pin = context['profile']['source_pins'][role]
        projection = {k: v for k, v in record.items() if k != 'indexed_manifest'}
        _require(record['sha256'] == pin['body_sha256'] and record['manifest_sha256'] == pin['manifest_sha256']
                 and _sha(_canonical(projection).encode('utf-8')) == pin['provenance_sha256'],
                 'Source differs from reviewed provenance: ' + role)


def _variables(context):
    reports = context['profile']['reports']
    nodes = [node for item in reports for node in item['nodes']]
    return {**context['envelope'], 'selection': copy.deepcopy(context['selection']), 'reports': [
        {'report': item['report'], 'catalog_pointer': item['catalog_pointer']} for item in reports],
        'nodes': nodes, 'variables': [node for node in nodes if node['kind'] != 'group']}


def _cadaster(cadastro, context):
    _require(isinstance(cadastro, list) and cadastro, 'Empty or missing financial cadaster')
    seen = set()
    for row in cadastro:
        _require(isinstance(row, dict) and set(row) == {f'c{i}' for i in range(38)}
                 and all(type(v) is str for v in row.values()), 'Unexpected native38 cadaster schema')
        _require(row['c1'] == str(context['period']) and row['c0'] and row['c0'] not in seen,
                 'Wrong reference, empty or duplicate opaque cadaster identifier')
        seen.add(row['c0'])


def _value(value, kind):
    if isinstance(value, legacy.NumberLexeme):
        raw, source_kind = str(value), 'json_number'
    elif type(value) is str:
        raw, source_kind = value, 'json_string'
    elif value is None:
        raw, source_kind = 'null', 'json_null'
    else:
        raise ValueError('Unsupported native cell type')
    state = classify(None if value is None else raw)
    if state == 'blank':
        state = 'empty'
    if kind == 'attribute':
        state = 'empty' if raw.strip() == '' else 'text'
    number = str(Decimal(raw.strip())) if kind != 'attribute' and state in ('numeric', 'zero') else ''
    return raw, source_kind, state, number


def _base(node, report, code, sources, context):
    role = 'numeric' if node['kind'] == 'money' else 'cadaster'
    return {**context['envelope'], 'report_id': report['id'], 'institution_id': code,
            **{k: node[k] for k in BIND_FIELDS}, 'variable': node['name'],
            'source_role': role, 'source_body': sources[role]['body_path'],
            'source_sha256': sources[role]['sha256'], 'report_generation': report.get('ge', ''),
            'report_version': report.get('v', ''),
            'report_generation_state': 'reported_text' if report.get('ge') else 'unknown',
            'report_version_state': 'reported_text' if report.get('v') else 'unknown'}


def _diagnostics(cadastro, variables, cells, context):
    coverage = []
    offset = 0
    for node in variables:
        states = Counter()
        for row in cells[offset:offset + len(cadastro)]:
            states[row['presence']] += 1
            if row['presence'] == 'stored':
                states[row['value_state']] += 1
        offset += len(cadastro)
        coverage.append({'report_id': node['report_id'], 'catalog_pointer': node['catalog_pointer'],
                         'ifd': node['ifd'], 'lid': node['lid'], 'td': node['td'],
                         'denominator_cadaster_records': len(cadastro), 'states': dict(states)})
    return {**context['envelope'], 'selection': copy.deepcopy(context['selection']), 'cadaster_records': len(cadastro),
            'coverage': coverage, 'limitations': list(context['limitations'])}


def _read(index_path):
    path = Path(index_path).resolve()
    index_body = path.read_bytes()
    index = _json(index_body)
    _require(isinstance(index, dict) and set(index) <= {'contract', 'selection', 'sources', 'code_revision'}
             and index.get('contract') == INDEX_CONTRACT, 'Wrong four-report source index')
    _require('selection' in index, 'Wrong closed financial selection')
    context = _context(index['selection'])
    _require(isinstance(index.get('sources'), dict) and set(index['sources']) == ROLES,
             'Explicit index of all five sources required')
    bodies, sources, paths = {}, {}, set()
    for role in sorted(ROLES):
        name = index['sources'][role]
        _require(type(name) is str and name and not Path(name).is_absolute()
                 and not re.match(r'^[A-Za-z]:|^[a-zA-Z]+://', name), 'Indexed manifest must be relative local path')
        source_path = (path.parent / name).resolve()
        _require(source_path not in paths, 'Two roles share a manifest')
        paths.add(source_path)
        pin = context['profile']['source_pins'][role]
        _require(_sha(source_path.read_bytes()) == pin['manifest_sha256'], 'Changed reviewed source manifest: ' + role)
        bodies[role], sources[role] = legacy._source(role, source_path, context)
        sources[role]['indexed_manifest'] = name
    _check_sources(sources, context)
    bodies['portal'].decode('utf-8')
    catalog = _json(bodies.pop('catalog'))
    _require(isinstance(catalog, list), 'Catalog is not an array')
    references = [(p, item) for p, item in enumerate(catalog)
                  if isinstance(item, dict) and type(item.get('dt')) is int and item['dt'] == context['period']]
    _require(len(references) == 1, 'Missing or duplicate selected catalog reference')
    position, entry = references[0]
    files = entry.get('files')
    _require(isinstance(files, list) and all(isinstance(f, dict) for f in files), 'Invalid catalog files')
    period = context['period']
    for name in (f'cadastro{period}_1005.json', f'info{period}.json', f'dados{period}_1.json'):
        _require(sum(f.get('f') == context['catalog_prefix'] + name for f in files) == 1, 'Missing or duplicate input announcement')
    selectors = []
    for item in files:
        selectors_in_file = item.get('sel', [])
        _require(isinstance(selectors_in_file, list) and all(isinstance(s, dict) for s in selectors_in_file), 'Invalid selectors')
        selectors.extend(s for s in selectors_in_file if type(s.get('id')) is int and s['id'] == 1005)
    _require(len(selectors) == 1 and selectors[0].get('n') == 'Conglomerados Financeiros e Instituições Independentes',
             'Wrong financial selector')
    for item in context['profile']['reports']:
        rid = item['report']['id']
        matches = [(p, f['trel']) for p, f in enumerate(files) if isinstance(f.get('trel'), dict)
                   and type(f['trel'].get('id')) is int and f['trel']['id'] == rid]
        _require(len(matches) == 1, 'Missing or duplicate financial report')
        p, report = matches[0]
        _same(_metadata_native(report), item['report'], 'Report tree/notes differ from reviewed profile')
        _require(item['catalog_pointer'] == f'/{position}/files/{p}/trel', 'Wrong report source pointer')
        _require(all(type(report.get(k, '')) is str for k in ('ge', 'v')), 'Invalid report vintage text')
    del catalog, files, entry, references
    dictionary = _json(bodies.pop('dictionary'))
    _require(isinstance(dictionary, list), 'Dictionary is not an array')
    infos = {}
    for p, info in enumerate(dictionary):
        _require(isinstance(info, dict) and type(info.get('id')) is int and info['id'] not in infos,
                 'Invalid or duplicate information definition')
        infos[info['id']] = (p, info)
    document = _variables(context)
    for node in document['nodes']:
        _require(node['ifd'] in infos, 'Selected definition missing')
        p, info = infos[node['ifd']]
        _same(_metadata_native(info), node['definition'], 'Definition differs from reviewed profile')
        _require(node['definition_pointer'] == '/' + str(p), 'Wrong definition source pointer')
    del dictionary, infos
    cadastro = _json(bodies.pop('cadaster'))
    _cadaster(cadastro, context)
    numeric = _json(bodies.pop('numeric'), numeric=True)
    _require(isinstance(numeric, dict) and set(numeric) == {'id', 'values'}
             and legacy._number_id(numeric['id']) == '1' and isinstance(numeric['values'], list), 'Invalid numeric area schema')
    entities = {}
    needed = {str(n['lid']) for n in document['variables'] if n['kind'] == 'money'}
    for p, entity in enumerate(numeric['values']):
        _require(isinstance(entity, dict) and set(entity) == {'e', 'v'} and isinstance(entity['v'], list), 'Invalid numeric entity')
        code = legacy._number_id(entity['e'])
        _require(code not in entities, 'Duplicate numeric entity')
        values, seen = {}, set()
        for q, cell in enumerate(entity['v']):
            _require(isinstance(cell, dict) and set(cell) == {'i', 'v'}, 'Invalid numeric cell')
            lid = legacy._number_id(cell['i'])
            _require(lid not in seen, 'Duplicate numeric information localizer')
            seen.add(lid)
            if lid in needed:
                values[lid] = (cell['v'], f'/values/{p}/v/{q}/v')
        entities[code] = (values, f'/values/{p}')
    del numeric, bodies
    cells, observations = [], []
    reports = {item['report']['id']: item['report'] for item in context['profile']['reports']}
    for node in document['variables']:
        for p, cad in enumerate(cadastro):
            row = _base(node, reports[node['report_id']], cad['c0'], sources, context)
            presence, pointer, value = 'stored', f'/{p}/c{node["lid"]}', None
            if node['kind'] != 'money':
                value = cad[f'c{node["lid"]}']
            else:
                entity = entities.get(cad['c0'])
                if entity is None:
                    presence, pointer = 'entity_not_stored', '/values'
                elif str(node['lid']) not in entity[0]:
                    presence, pointer = 'information_not_stored', entity[1] + '/v'
                else:
                    value, pointer = entity[0][str(node['lid'])]
            raw, kind, state, number = (_value(value, node['kind']) if presence == 'stored' else
                                        ('', 'not_stored', 'unobserved_cell', ''))
            row.update(presence=presence, source_pointer=pointer, raw_value=raw, source_kind=kind,
                       value_state=state, numeric_value=number)
            cells.append(row)
            if presence == 'stored':
                observations.append(row)
    diagnostics = _diagnostics(cadastro, document['variables'], cells, context)
    diagnostics['nodes'] = len(document['nodes'])
    provenance = {'input_index_sha256': _sha(index_body), 'profile_sha256': context['profile_sha256'],
                  'reader_version': '1', 'reader_source_sha256': _sha(Path(__file__).read_bytes().replace(b'\r\n', b'\n')),
                  'code_revision': index.get('code_revision', 'unknown')}
    return dict(context['envelope']), observations, cells, cadastro, document, diagnostics, sources, provenance


def admit(index_path: Path, output: Path) -> dict:
    """Validate reviewed bytes, write a new destination and accept last."""
    output = Path(output)
    if output.exists():
        raise FileExistsError('Financial destination already exists: ' + str(output))
    envelope, observations, cells, cadastro, document, diagnostics, sources, provenance = _read(index_path)
    output.mkdir(parents=True, exist_ok=False)
    legacy._csv(output / INPUTS[0], observations, FIELDS)
    legacy._csv(output / INPUTS[1], cells, FIELDS)
    legacy._csv(output / INPUTS[2], (
        {**envelope, **cad, 'source_body': sources['cadaster']['body_path'],
         'source_sha256': sources['cadaster']['sha256'], 'source_pointer': '/' + str(p)}
        for p, cad in enumerate(cadastro)), CAD_FIELDS)
    legacy._write_json(output / INPUTS[3], document)
    legacy._write_json(output / INPUTS[4], diagnostics)
    files = []
    for name in INPUTS:
        body = (output / name).read_bytes()
        files.append({'path': name, 'bytes': len(body), 'sha256': _sha(body)})
    manifest = {**envelope, 'selection': copy.deepcopy(document['selection']), 'accepted': True,
                'created_utc': datetime.now(timezone.utc).isoformat(), **provenance, 'sources': sources,
                'observations': len(observations), 'cells': len(cells), 'cadaster_records': len(cadastro),
                'files': files, 'limitations': list(diagnostics['limitations'])}
    pending = output / '.manifest.pending'
    legacy._write_json(pending, manifest)
    os.link(pending, output / 'manifest.json')
    pending.unlink()
    return manifest


def _iter_csv_bytes(body, fields):
    with io.TextIOWrapper(io.BytesIO(body), encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        _require(reader.fieldnames == list(fields), 'Invalid admitted CSV headers')
        for row in reader:
            _require(set(row) == set(fields) and all(type(v) is str for v in row.values()), 'Malformed admitted CSV row')
            yield row


def _csv_bytes(body, fields):
    return list(_iter_csv_bytes(body, fields))


def validate_admission(manifest, bodies):
    """Reconstruct an admission from explicit verified payload bytes.

    Callers must authenticate manifest bytes by an external SHA-256 first. This
    helper verifies payload hashes, metadata, ordered grade, shared native keys,
    states, lexemes, Decimal and observation/coverage reconstruction, offline.
    """
    _require(isinstance(manifest, dict) and manifest.get('accepted') is True, 'Unaccepted financial admission')
    _require('selection' in manifest, 'Wrong admission selection')
    context = _context(manifest['selection'])
    _same({k: manifest.get(k) for k in ENVELOPE}, context['envelope'], 'Wrong admission scope')
    _require(manifest.get('profile_sha256') == context['profile_sha256'], 'Unknown admitted profile')
    _check_sources(manifest.get('sources'), context)
    _same(manifest.get('limitations'), context['limitations'], 'Changed admission qualifications')
    _require(isinstance(bodies, dict) and set(bodies) == set(INPUTS), 'Invalid explicit payload membership')
    files = manifest.get('files')
    _require(isinstance(files, list) and len(files) == len(INPUTS), 'Invalid payload inventory')
    seen = set()
    for entry in files:
        _require(isinstance(entry, dict) and set(entry) == {'path', 'bytes', 'sha256'}
                 and entry['path'] in INPUTS and entry['path'] not in seen, 'Invalid payload record')
        seen.add(entry['path'])
        body = bodies[entry['path']]
        _require(type(body) is bytes and type(entry['bytes']) is int and len(body) == entry['bytes']
                 and _sha(body) == entry['sha256'], 'Payload size/hash mismatch')
    document = _json(bodies['financial-variables.json'])
    _same(document, _variables(context), 'Variable metadata differs from installed profile')
    cad_rows = _csv_bytes(bodies['financial-cadastro.csv'], CAD_FIELDS)
    cadastro = [{f'c{i}': row[f'c{i}'] for i in range(38)} for row in cad_rows]
    _cadaster(cadastro, context)
    for p, row in enumerate(cad_rows):
        expected = {**{k: str(v) for k, v in context['envelope'].items()}, **cadastro[p],
                    'source_body': manifest['sources']['cadaster']['body_path'],
                    'source_sha256': manifest['sources']['cadaster']['sha256'], 'source_pointer': '/' + str(p)}
        _same(row, expected, 'Wrong admitted cadaster provenance/scope')
    cells = _csv_bytes(bodies['financial-cells.csv'], FIELDS)
    _require(len(cells) == len(cadastro) * len(document['variables']), 'Incomplete admitted grade')
    reports = {item['report']['id']: item['report'] for item in context['profile']['reports']}
    originals, entity_presence, pointer_keys, entity_codes = {}, {}, {}, {}
    offset = 0
    for node in document['variables']:
        for p, cad in enumerate(cadastro):
            row = cells[offset]
            offset += 1
            expected = {k: str(v) for k, v in _base(node, reports[node['report_id']], cad['c0'], manifest['sources'], context).items()}
            _require(all(row[k] == v for k, v in expected.items()), 'Admitted grade binding/scope/provenance mismatch')
            if node['kind'] != 'money':
                raw, kind, state, number = _value(cad[f'c{node["lid"]}'], node['kind'])
                token = {'presence': 'stored', 'source_pointer': f'/{p}/c{node["lid"]}',
                         'raw_value': raw, 'source_kind': kind, 'value_state': state, 'numeric_value': number}
            elif row['presence'] == 'stored':
                _require(re.fullmatch(r'/values/(?:0|[1-9][0-9]*)/v/(?:0|[1-9][0-9]*)/v', row['source_pointer']) is not None,
                         'Invalid stored numeric source pointer')
                kind, raw = row['source_kind'], row['raw_value']
                _require(kind in ('json_number', 'json_string', 'json_null'), 'Invalid numeric source type')
                if kind == 'json_number':
                    _require(re.fullmatch(r'-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?', raw) is not None,
                             'Invalid JSON number lexeme')
                    value = legacy.NumberLexeme(raw)
                elif kind == 'json_null':
                    _require(raw == 'null', 'Invalid null token')
                    value = None
                else:
                    value = raw
                raw, kind, state, number = _value(value, node['kind'])
                token = {'presence': 'stored', 'source_pointer': row['source_pointer'],
                         'raw_value': raw, 'source_kind': kind, 'value_state': state, 'numeric_value': number}
            else:
                _require(row['presence'] in ('entity_not_stored', 'information_not_stored'), 'Invalid cell presence')
                pointer = row['source_pointer']
                _require(pointer == '/values' if row['presence'] == 'entity_not_stored' else
                         re.fullmatch(r'/values/(?:0|[1-9][0-9]*)/v', pointer) is not None, 'Invalid absence source pointer')
                token = {'presence': row['presence'], 'source_pointer': pointer, 'raw_value': '',
                         'source_kind': 'not_stored', 'value_state': 'unobserved_cell', 'numeric_value': ''}
            _require(all(row[k] == v for k, v in token.items()), 'Invalid native token/state/Decimal')
            if node['kind'] == 'money':
                key = (cad['c0'], node['lid'])
                _require(key not in originals or originals[key] == token, 'Divergent repeated native source key')
                originals[key] = token
                entity = None if row['presence'] == 'entity_not_stored' else row['source_pointer'].split('/')[2]
                _require(cad['c0'] not in entity_presence or entity_presence[cad['c0']] == entity,
                         'Divergent numeric entity source pointer')
                entity_presence[cad['c0']] = entity
                if entity is not None:
                    _require(entity not in entity_codes or entity_codes[entity] == cad['c0'],
                             'Numeric entity pointer identifies two cadaster codes')
                    entity_codes[entity] = cad['c0']
                if row['presence'] == 'stored':
                    pointer = row['source_pointer']
                    _require(pointer not in pointer_keys or pointer_keys[pointer] == key,
                             'Numeric cell pointer identifies two native keys')
                    pointer_keys[pointer] = key
    # Validate observations in order without keeping another full grade of dicts
    # or serializing two giant JSON strings for comparison. Returned observations
    # share the already validated cell dictionaries, as in admission generation.
    observations = [row for row in cells if row['presence'] == 'stored']
    for actual, expected in zip_longest(_iter_csv_bytes(bodies['financial-observations.csv'], FIELDS), observations):
        _require(actual == expected, 'Observation reconstruction differs')
    for key, count in (('cells', len(cells)), ('observations', len(observations)), ('cadaster_records', len(cadastro))):
        _require(type(manifest.get(key)) is int and manifest[key] == count, 'Invalid admitted count: ' + key)
    diagnostics = _json(bodies['financial-diagnostics.json'])
    expected_diagnostics = _diagnostics(cadastro, document['variables'], cells, context)
    expected_diagnostics['nodes'] = len(document['nodes'])
    _same(diagnostics, expected_diagnostics, 'Coverage/diagnostic reconstruction differs')
    return {'envelope': dict(context['envelope']), 'context': context, 'cadastro': cad_rows, 'cells': cells, 'observations': observations,
            'variables': document, 'diagnostics': diagnostics, 'sources': manifest['sources'],
            'profile': context['profile']}

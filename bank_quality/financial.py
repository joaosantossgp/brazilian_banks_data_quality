"""Closed, offline financial Resumo profiles; never uses individual defaults."""
import csv
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from .archive import load_body
from .inventory import classify

CONTRACT = 'ifdata-financial-snapshot-202412-v1'
SELECTION = {'period': 202412, 'perspective': 1005, 'report': 92}
ROLES = {'catalog', 'cadaster', 'dictionary', 'portal', 'numeric'}
PROFILE_PATH = Path(__file__).with_name('financial-profile-202412.json')
PROFILE_202312_PATH = Path(__file__).with_name('financial-profile-202312.json')
FIELDS = ['contract', 'period', 'perspective', 'perspective_id', 'report_id', 'institution_id',
          'ifd', 'td', 'area', 'lid', 'fid', 'variable', 'presence', 'value_state', 'raw_value',
          'numeric_value', 'source_kind', 'source_role', 'source_body', 'source_sha256',
          'source_pointer', 'catalog_pointer', 'definition_pointer', 'unit', 'unit_basis',
          'window_start', 'window_end', 'window_basis', 'report_generation', 'report_version',
          'report_generation_state', 'report_version_state']


class NumberLexeme(str):
    """JSON number's original text, distinct from a JSON string."""


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'Duplicate JSON object key: ' + key)
        result[key] = value
    return result


def _constant(value):
    raise ValueError('Nonstandard JSON numeric constant: ' + value)


def _json(body, numeric=False):
    return json.loads(body, object_pairs_hook=_pairs, parse_constant=_constant,
                      parse_float=NumberLexeme, parse_int=NumberLexeme if numeric else int)


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _profile_for_selection(selection):
    _require(isinstance(selection, dict) and type(selection.get('period')) is int
             and selection['period'] in (202312, 202412), 'Wrong financial source scope')
    period = selection['period']
    expected = {'period': period, 'perspective': 1005, 'report': 92}
    _require(_canonical(selection) == _canonical(expected), 'Wrong financial source scope')
    path = PROFILE_202312_PATH if period == 202312 else PROFILE_PATH
    body = path.read_bytes()
    profile = _json(body)
    _require(_canonical(profile['selection']) == _canonical(expected), 'Invalid installed financial profile')
    return {'period': period, 'selection': expected, 'contract': f'ifdata-financial-snapshot-{period}-v1',
            'profile_path': path, 'profile_body': body, 'profile': profile,
            'cadaster_fields': 32 if period == 202312 else 38}


def _source(role, manifest_path, context):
    path = Path(manifest_path).resolve()
    manifest_body = path.read_bytes()
    manifest = _json(manifest_body)
    _require(isinstance(manifest, dict), 'Source manifest is not an object')
    _require(manifest.get('method') == 'GET' and type(manifest.get('http_status')) is int
             and manifest['http_status'] == 200 and manifest.get('outcome') == 'ok',
             'Source manifest is incomplete or failed: ' + role)
    legacy = context['profile'].get('legacy_sources', {}).get(role)
    if legacy is not None:
        _require(context['period'] == 202312 and role in ('dictionary', 'numeric')
                 and hashlib.sha256(manifest_body).hexdigest() == legacy['manifest_sha256']
                 and manifest.get('sha256') == legacy['body_sha256']
                 and 'truncated' not in manifest and manifest.get('diagnostics') == legacy['diagnostics']
                 and isinstance(manifest.get('context'), dict)
                 and manifest['context'].get('body_capture') == legacy['body_capture'],
                 'Unreviewed legacy source manifest: ' + role)
    else:
        _require(manifest.get('truncated') is False and manifest.get('diagnostics') == [],
                 'Source manifest is incomplete or failed: ' + role)
    _require(type(manifest.get('bytes')) is int and 0 < manifest['bytes'] <= 64 * 1024 * 1024,
             'Source size is outside the archived-body bound')
    _require(isinstance(manifest.get('sha256'), str) and re.fullmatch('[0-9a-f]{64}', manifest['sha256']),
             'Invalid source SHA-256')
    body_name = manifest.get('body_path')
    _require(isinstance(body_name, str) and body_name and not Path(body_name).is_absolute(),
             'Invalid archive body path')
    body_path = (path.parent / body_name).resolve()
    _require(body_path.is_relative_to(path.parent), 'Archive body path escapes its directory')
    recovered = manifest.get('retrieved_at_utc')
    _require(isinstance(recovered, str) and datetime.fromisoformat(recovered).utcoffset() == timedelta(0),
             'Source retrieval time must be UTC')
    for key in ('url', 'final_url'):
        _require(isinstance(manifest.get(key), str), 'Source URL is missing')
        url = urlsplit(manifest[key])
        _require(url.scheme == 'https' and url.netloc == 'www3.bcb.gov.br' and not url.fragment,
                 'Source is outside the official IF.data endpoint')
        if role == 'catalog':
            _require(url.path == '/ifdata/rest/relatorios2000a2024' and not url.query, 'Wrong catalog source')
        elif role == 'portal':
            _require(url.path == '/ifdata/index.html' and not url.query, 'Wrong archived portal source')
        else:
            period = context['period']
            filename = {'cadaster': f'cadastro{period}_1005.json', 'dictionary': f'info{period}.json',
                        'numeric': f'dados{period}_1.json'}[role]
            _require(url.path == '/ifdata/rest/arquivos' and parse_qsl(url.query) ==
                     [('nomeArquivo', f'ifdata/{period}/' + filename)], 'Wrong selected source file: ' + role)
    body = load_body(manifest, path.parent)
    _require(len(body) == manifest['bytes'], 'Archived source size differs from manifest')
    _require(isinstance(manifest.get('context', {}), dict), 'Invalid source context')
    record = {key: manifest.get(key) for key in
              ('url', 'final_url', 'retrieved_at_utc', 'bytes', 'sha256', 'body_path', 'context')}
    record['manifest_sha256'] = hashlib.sha256(manifest_body).hexdigest()
    record['source_generation_state'] = 'unknown'
    if context['period'] == 202312:
        record['truncation_state'] = 'undeclared_legacy' if legacy is not None else 'observed_false'
        record['capture_diagnostics'] = manifest['diagnostics']
    return body, record


def _number_id(value):
    _require(isinstance(value, NumberLexeme) and re.fullmatch(r'0|[1-9]\d*', value),
             'Numeric entity/information identifier must be an integer lexeme')
    return str(value)


def _value(value):
    if isinstance(value, NumberLexeme):
        raw, kind = str(value), 'json_number'
    elif isinstance(value, str):
        raw, kind = value, 'json_string'
    elif value is None:
        raw, kind = 'null', 'json_null'
    else:
        raise ValueError('Invalid selected source value type')
    state = classify(None if value is None else raw)
    _require(state != 'invalid', 'Invalid selected numeric token; source retained for diagnosis')
    number = str(Decimal(raw.strip())) if state in ('numeric', 'zero') else ''
    return raw, kind, state, number


def _read(index_path):
    path = Path(index_path).resolve()
    index_body = path.read_bytes()
    index = _json(index_body)
    _require(isinstance(index, dict) and index.get('contract') == 'ifdata-financial-sources-v1',
             'Wrong financial source scope')
    context = _profile_for_selection(index.get('selection'))
    period, profile_body, profile = context['period'], context['profile_body'], context['profile']
    _require(isinstance(index.get('sources'), dict) and set(index['sources']) == ROLES,
             'An explicit index of all five financial sources is required')
    bodies, sources = {}, {}
    source_paths = []
    for role in sorted(ROLES):
        name = index['sources'][role]
        _require(isinstance(name, str) and name, 'Invalid indexed source path')
        source_path = (path.parent / name).resolve()
        _require(source_path not in source_paths, 'Two source roles share a manifest')
        source_paths.append(source_path)
        bodies[role], sources[role] = _source(role, source_path, context)
        sources[role]['indexed_manifest'] = name
    portal = bodies['portal'].decode('utf-8')
    _require(sources['portal']['sha256'] == profile['source_baseline']['portal_sha256'],
             'Archived portal body differs from the reviewed profile baseline')
    _require(all(fragment in portal for fragment in profile['formatter_fragments']),
             'Archived monetary formatter differs from the reviewed profile')
    catalog = _json(bodies['catalog'])
    _require(isinstance(catalog, list), 'Catalog is not an array')
    entries = [(i, entry) for i, entry in enumerate(catalog) if isinstance(entry, dict) and
               type(entry.get('dt')) is int and entry['dt'] == period]
    _require(len(entries) == 1, 'Selected catalog reference is missing or duplicated')
    position, entry = entries[0]
    files = entry.get('files')
    _require(isinstance(files, list) and all(isinstance(item, dict) for item in files), 'Invalid selected catalog files')
    for name in (f'cadastro{period}_1005.json', f'info{period}.json', f'dados{period}_1.json'):
        _require(sum(item.get('f') == f'ifdata/{period}/' + name for item in files) == 1,
                 'Selected input file is missing or duplicated in the official catalog')
    selectors = []
    for item in files:
        group = item.get('sel', [])
        _require(isinstance(group, list) and all(isinstance(selector, dict) for selector in group),
                 'Invalid selected catalog selector array')
        selectors.extend(selector for selector in group
                         if type(selector.get('id')) is int and selector['id'] == 1005)
    _require(len(selectors) == 1 and selectors[0].get('n') ==
             'Conglomerados Financeiros e Instituições Independentes', 'Wrong financial selector')
    reports = [(i, item['trel']) for i, item in enumerate(files) if isinstance(item.get('trel'), dict)
               and type(item['trel'].get('id')) is int and item['trel']['id'] == 92]
    _require(len(reports) == 1, 'Financial Resumo report is missing or duplicated')
    report_position, report = reports[0]
    _require(_canonical({key: report.get(key) for key in profile['report']}) == _canonical(profile['report']),
             'Report schema/notes differ from the reviewed financial profile')
    _require(all(type(report.get(key, '')) is str for key in ('ge', 'v')), 'Invalid report generation/version text')
    report_pointer = f'/{position}/files/{report_position}/trel'
    dictionary = _json(bodies['dictionary'])
    _require(isinstance(dictionary, list), 'Information dictionary is not an array')
    infos = {}
    for i, info in enumerate(dictionary):
        _require(isinstance(info, dict) and type(info.get('id')) is int and info['id'] not in infos,
                 'Invalid or duplicate information definition')
        infos[info['id']] = (i, info)
    variables = []
    for metric in profile['metrics']:
        expected = metric['info']
        _require(expected['id'] in infos, 'Selected information definition is missing')
        info_position, info = infos[expected['id']]
        _require(_canonical(info) == _canonical(expected), 'Selected definition differs from reviewed profile')
        is_money = info['td'] == 3
        variables.append({'ifd': info['id'], 'td': info['td'], 'area': info['a'], 'lid': info['lid'],
                          'fid': metric['fid'], 'name': info['n'], 'definition': info,
                          'catalog_pointer': report_pointer + '/c/' + str(metric['position']),
                          'definition_pointer': '/' + str(info_position),
                          'unit': 'BRL_raw_inferred' if is_money else 'count',
                          'unit_basis': 'archived_formatter_divides_by_1000' if is_money else 'cadaster_definition',
                          'window_start': f'{period // 100}-07-01' if info['id'] == 79718 else '',
                          'window_end': f'{period // 100}-12-31',
                          'window_basis': 'report_rp_result_window' if info['id'] == 79718 else
                                          'stock_at_reference_inferred' if is_money else 'cadaster_reference'})
    cadastro = _json(bodies['cadaster'])
    _require(isinstance(cadastro, list) and cadastro, 'Financial cadaster is empty or missing')
    cadastro_ids = set()
    for row in cadastro:
        _require(isinstance(row, dict) and set(row) == {f'c{i}' for i in range(context['cadaster_fields'])}
                 and all(type(v) is str for v in row.values()), 'Unexpected financial cadaster schema')
        code = row['c0']
        _require(row['c1'] == str(period) and re.fullmatch(r'0|[1-9]\d*', code)
                 and code not in cadastro_ids, 'Wrong reference, padded or duplicate cadaster identifier')
        cadastro_ids.add(code)
    numeric = _json(bodies['numeric'], numeric=True)
    _require(isinstance(numeric, dict) and _number_id(numeric.get('id')) == '1'
             and isinstance(numeric.get('values'), list), 'Unexpected numeric-area schema')
    entities = {}
    for i, row in enumerate(numeric['values']):
        _require(isinstance(row, dict) and isinstance(row.get('v'), list), 'Invalid numeric entity')
        code = _number_id(row.get('e'))
        _require(code not in entities, 'Duplicate numeric entity')
        entries = {}
        for j, cell in enumerate(row['v']):
            _require(isinstance(cell, dict) and 'v' in cell, 'Invalid numeric cell')
            lid = _number_id(cell.get('i'))
            _require(lid not in entries, 'Duplicate numeric information localizer')
            entries[lid] = (cell['v'], f'/values/{i}/v/{j}/v')
        entities[code] = (entries, f'/values/{i}')
    cells, observations, coverage = [], [], []
    common = {'contract': context['contract'], 'period': period, 'perspective': 'financial',
              'perspective_id': 1005, 'report_id': 92, 'report_generation': report.get('ge', ''),
              'report_version': report.get('v', ''),
              'report_generation_state': 'reported_text' if report.get('ge') else 'unknown',
              'report_version_state': 'reported_text' if report.get('v') else 'unknown'}
    for variable in variables:
        states = Counter()
        for i, cad in enumerate(cadastro):
            role = 'numeric' if variable['td'] == 3 else 'cadaster'
            entity = entities.get(cad['c0'])
            presence, value, pointer = 'stored', None, f'/{i}/c{variable["lid"]}'
            if role == 'cadaster':
                value = cad[f'c{variable["lid"]}']
            elif entity is None:
                presence, pointer = 'entity_not_stored', '/values'
            elif str(variable['lid']) not in entity[0]:
                presence, pointer = 'information_not_stored', entity[1] + '/v'
            else:
                value, pointer = entity[0][str(variable['lid'])]
            raw, kind, state, number = _value(value) if presence == 'stored' else ('', 'not_stored', 'unobserved_cell', '')
            cell = {**common, **{key: variable[key] for key in
                    ('ifd', 'td', 'area', 'lid', 'fid', 'catalog_pointer', 'definition_pointer',
                     'unit', 'unit_basis', 'window_start', 'window_end', 'window_basis')},
                    'institution_id': cad['c0'], 'variable': variable['name'], 'presence': presence,
                    'value_state': state, 'raw_value': raw, 'numeric_value': number, 'source_kind': kind,
                    'source_role': role, 'source_body': sources[role]['body_path'],
                    'source_sha256': sources[role]['sha256'], 'source_pointer': pointer}
            cells.append(cell)
            states[presence] += 1
            if presence == 'stored':
                observations.append(cell)
                states[state] += 1
        coverage.append({'ifd': variable['ifd'], 'lid': variable['lid'], 'td': variable['td'],
                         'denominator_cadaster_records': len(cadastro), 'states': dict(states)})
    diagnostics = {'contract': context['contract'], 'selection': dict(context['selection']), 'cadaster_records': len(cadastro),
                   'shared_numeric_entities': len(entities), 'matched_cadaster_entities': len(cadastro_ids & entities.keys()),
                   'numeric_entities_outside_selected_cadaster': len(entities.keys() - cadastro_ids),
                   'coverage': coverage,
                   'limitations': ['Source-key correspondence only; no academic/legal eligibility or historical universe.',
                                   'Non-simultaneous retrieval; source generation of cadaster/dictionary/numeric unknown.',
                                   'Unstored direct keys are not source NI, zero or economic missingness.',
                                   'Raw BRL inferred from formatter; income July-December, not annual.',
                                   'No exclusion of n4, empty TD, segment42 or undocumented c9.',
                                   'Financial technical admission does not validate economic correctness or 2025 comparability.']}
    if period == 202312:
        diagnostics['limitations'].append('Reviewed legacy dictionary/numeric decoded bodies; truncation flag undeclared, not observed false.')
    return common, observations, cells, cadastro, variables, diagnostics, sources, {
        'input_index_sha256': hashlib.sha256(index_body).hexdigest(),
        'profile_sha256': hashlib.sha256(profile_body.replace(b'\r\n', b'\n')).hexdigest(),
        'reader_version': '2', 'reader_source_sha256': hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
        'code_revision': index.get('code_revision', 'unknown')}


def _csv(path, rows, fields):
    with path.open('x', encoding='utf-8', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction='raise', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())


def admit(index_path: Path, output: Path) -> dict:
    """Validate explicit archived inputs, reserve a fresh destination, accept last."""
    output = Path(output)
    if output.exists():
        raise FileExistsError('Financial destination already exists: ' + str(output))
    common, observations, cells, cadastro, variables, diagnostics, sources, provenance = _read(index_path)
    output.mkdir(parents=True, exist_ok=False)
    _csv(output / 'financial-observations.csv', observations, FIELDS)
    _csv(output / 'financial-cells.csv', cells, FIELDS)
    cad_rows = [{**common, **cad, 'source_body': sources['cadaster']['body_path'],
                 'source_sha256': sources['cadaster']['sha256'], 'source_pointer': '/' + str(i)}
                for i, cad in enumerate(cadastro)]
    cadaster_fields = 32 if common['period'] == 202312 else 38
    _csv(output / 'financial-cadastro.csv', cad_rows, list(common) + [f'c{i}' for i in range(cadaster_fields)]
         + ['source_body', 'source_sha256', 'source_pointer'])
    _write_json(output / 'financial-variables.json', {**common, 'variables': variables})
    _write_json(output / 'financial-diagnostics.json', diagnostics)
    files = []
    for name in ('financial-observations.csv', 'financial-cells.csv', 'financial-cadastro.csv',
                 'financial-variables.json', 'financial-diagnostics.json'):
        body = (output / name).read_bytes()
        files.append({'path': name, 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()})
    manifest = {**common, 'selection': {'period': common['period'], 'perspective': 1005, 'report': 92}, 'accepted': True,
                'created_utc': datetime.now(timezone.utc).isoformat(), **provenance,
                'sources': sources, 'observations': len(observations), 'cells': len(cells),
                'cadaster_records': len(cadastro), 'files': files, 'limitations': diagnostics['limitations']}
    pending = output / '.manifest.pending'
    _write_json(pending, manifest)
    # Hard-link creation publishes the complete marker atomically and never replaces
    # an existing marker. Interrupted writes leave only diagnostic partial outputs.
    os.link(pending, output / 'manifest.json')
    pending.unlink()
    return manifest

"""Pinned offline historical metadata relationships, without academic eligibility.

Basic CNPJ concordance is a candidate, never universal legal identity. Document
dates are points of evidence, not intervals. No network or temporal filling.
"""
import calendar
from collections import Counter, defaultdict
import csv
from datetime import date
import io
import hashlib
import json
from pathlib import Path
import re
import tempfile

from bank_quality import cvm_metadata as cvm_reader
from bank_quality import cvm_corporate_metadata as corporate_reader
from bank_quality import ifdata_cadastro as cadastro_reader


CONTRACT = 'historical-issuer-links-v2'
REFERENCES = tuple(f'{year}{month}' for year in range(2010, 2025) for month in ('03', '06', '09', '12'))
PERSPECTIVES = ('individual', 'financeiro', 'prudencial')
STATES = ('candidatura_cadastral', 'conflito_identificador',
          'declaracao_controle_datada', 'candidatura_controle_sem_vigencia')
NATIVE_ISSUER = tuple(dict.fromkeys([*cvm_reader.CAD_FIELDS, *cvm_reader.HEADERS['index'],
                                   *cvm_reader.HEADERS['geral'], *cvm_reader.LINEAGE]))
NATIVE_CORPORATE = tuple(dict.fromkeys([field for fields in corporate_reader.FIELDS.values()
                                       for field in fields] + list(corporate_reader.LINEAGE)))
ATTRIBUTES = ('Tcb', 'Td', 'Tc', 'SegmentoTb', 'Atividade', 'Sr', 'Situacao')
SCHEMAS = {
    'cadastro': ('observation_id', *cadastro_reader.FIELDS, *cadastro_reader.ORIGIN),
    'emissores': ('observation_id', 'source_table', 'cnpj_full', 'cnpj_basic', 'cvm_code',
                 'identifier_conflict', 'time_state', *NATIVE_ISSUER),
    'instrumentos': ('observation_id', 'cnpj_full', 'cnpj_basic', 'instrument_class',
                     'priority', 'b3_documentary', 'document_time_state',
                     *cvm_reader.HEADERS['valmob'], *cvm_reader.LINEAGE),
    'societario': ('observation_id', 'source_table', 'parent_full', 'child_full',
                   'control_reason', 'control_date', 'control_date_field', *NATIVE_CORPORATE),
    'vinculos_cadastrais': ('observation_id', 'reference', 'institution', 'perspective', 'entity',
                           'cadastro_support', 'group_support', 'leader_support', 'leader_scope',
                           'CnpjInstituicaoLider',
                           *(prefix + field for prefix in ('institution_', 'group_', 'leader_') for field in ATTRIBUTES)),
    'relacao_trimestral': ('observation_id', 'reference', 'issuer_full', 'issuer_basic', 'cvm_codes',
                          'perspective', 'entity', 'evidence_state', 'institution_ids',
                          'cadastro_support', 'issuer_support', 'corporate_support',
                          'instrument_support', 'instrument_dates', 'control_paths', 'market_state'),
    'caminhos_societarios': ('observation_id', 'issuer_full', 'terminal_basic', 'route_json', 'corporate_support'),
    'cobertura': ('observation_id', 'reference', 'cadastro_rows', 'individual_rows',
                  'relationship_rows', 'states', 'gap_rows', 'market_state'),
    'lacunas': ('observation_id', 'reference', 'entity', 'perspective', 'reason', 'support', 'detail'),
}
MARKET_STATE = 'cobertura_documental_incompleta_sem_negociacao_observada'
MAX_TABLE_BYTES = 1024 * 1024 * 1024


def _json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _full(value):
    return cvm_reader._cnpj(value) if isinstance(value, str) else None


def _date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value) if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value) else None
    except ValueError:
        return None


def _quarter(reference):
    return date(int(reference[:4]), int(reference[4:]), calendar.monthrange(int(reference[:4]), int(reference[4:]))[1])


def _interval_state(start, end, reference):
    """Classify declared dates without inventing inclusivity or an open end."""
    first, last, quarter = _date(start), _date(end), _quarter(reference)
    if (start and first is None) or (end and last is None):
        return 'data_invalida'
    if not first and not last:
        return 'datas_ausentes'
    if first and not last:
        return 'inicio_sem_fim'
    if last and not first:
        return 'fim_sem_inicio'
    if first > last:
        return 'datas_conflitantes'
    if first == last:
        return 'datas_coincidentes'
    if quarter in (first, last):
        return 'extremo_sem_inclusividade'
    return 'interior_estrito' if first < quarter < last else 'fora_intervalo_declarado'


def _instrument_class(value):
    return {'Ações Ordinárias': 'acao_ordinaria', 'Ações Preferenciais': 'acao_preferencial',
            'Units': 'unit', 'BDRs': 'bdr'}.get(value, 'tipo_pendente' if value and 'certificado' in value.casefold() else 'outro_tipo_literal')


def _read_input(root, manifest, name):
    raw = cvm_reader._pinned(cvm_reader._contained(root, name), manifest['files'][name]['sha256'], MAX_TABLE_BYTES)
    return list(csv.DictReader(io.StringIO(raw.decode('utf8'), newline=''), strict=True))


def _observation(kind, ordinal):
    return f'{kind}:{ordinal:09d}'


def _project_native(row, fields):
    return {field: row.get(field) for field in fields}


def _issuer_observation(kind, row, n):
    full = _full(row.get('CNPJ_CIA', row.get('CNPJ_Companhia')))
    return dict(observation_id=_observation('cvm_' + kind, n), source_table=cvm_reader.TABLES[kind],
        cnpj_full=full, cnpj_basic=full[:8] if full else None,
        cvm_code=row.get('CD_CVM', row.get('Codigo_CVM')), identifier_conflict='false',
        time_state='cadastro_corrente_sem_vigencia_historica' if kind == 'cad' else 'referencia_documental_sem_snapshot',
        **_project_native(row, NATIVE_ISSUER))


def _issuer_conflicts(issuer):
    codes = defaultdict(set)
    for row in issuer:
        if row['cnpj_full'] and row['cvm_code']:
            code = row['cvm_code']
            # Compare the CAD numeric domain with the FCA numeric character domain.
            # Normalize the comparison key alone; native observations stay literal.
            key = code
            if isinstance(code, str) and re.fullmatch(r'[0-9]+', code):
                key = code.lstrip('0') or '0'
            codes[row['cnpj_full']].add(key)
    for row in issuer:
        row['identifier_conflict'] = str(len(codes[row['cnpj_full']]) > 1).lower()


def _instrument_observation(row, n):
    full = _full(row['CNPJ_Companhia'])
    species = _instrument_class(row['Valor_Mobiliario'])
    b3 = row['Mercado'] == 'Bolsa' and any(row[field] in ('B3', 'BM&FBOVESPA', 'BM&FBovespa',
             'B3 S.A. - Brasil, Bolsa, Balcão', 'BM&FBOVESPA S.A. - Bolsa de Valores, Mercadorias e Futuros')
             for field in ('Sigla_Entidade_Administradora', 'Entidade_Administradora'))
    return dict(observation_id=_observation('instrumento', n), cnpj_full=full,
        cnpj_basic=full[:8] if full else None, instrument_class=species,
        priority='igual_acoes_units_bdr' if species in ('acao_ordinaria', 'acao_preferencial', 'unit', 'bdr') else 'consultavel',
        b3_documentary=str(b3).lower(), document_time_state='referencia_documental_sem_snapshot', **row)


def _corporate_observation(kind, row, n):
    parent, child, reason, when, when_field = None, None, None, None, None
    if kind == 'participacao_sociedade':
        parent, child = _full(row['CNPJ_Companhia']), _full(row['CNPJ'])
        if row['Tipo_Sociedade'] == 'Controlada':
            reason, when, when_field = 'Tipo_Sociedade=Controlada', row['Data_Referencia'], 'Data_Referencia'
    elif kind == 'posicao_acionaria':
        parent, child = _full(row['CPF_CNPJ_Acionista']), _full(row['CNPJ_Companhia'])
        if row['Acionista_Controlador'] == 'S':
            reason, when, when_field = 'Acionista_Controlador=S', row['Data_Composicao_Capital_Social'], 'Data_Composicao_Capital_Social'
    return dict(observation_id=_observation('fre_' + kind, n), source_table=corporate_reader.TABLES[kind],
        parent_full=parent, child_full=child, control_reason=reason,
        control_date=when if _date(when) else None, control_date_field=when_field,
        **_project_native(row, NATIVE_CORPORATE))


def _derive(cad, issuer, instruments, corporate):
    """Derive finite relationships from authenticated observations (also replayed by verifier)."""
    tables = dict(cadastro=cad, emissores=issuer, instrumentos=instruments, societario=corporate,
                  vinculos_cadastrais=[], relacao_trimestral=[], caminhos_societarios=[], cobertura=[], lacunas=[])
    gaps = tables['lacunas']

    def gap(reason, support, reference=None, entity=None, perspective=None, detail=None):
        gaps.append(dict(observation_id=_observation('lacuna', len(gaps) + 1), reference=reference,
                         entity=entity, perspective=perspective, reason=reason,
                         support=_json_text(sorted(set(support))), detail=detail))

    by_full, by_basic, inst_by_full = defaultdict(list), defaultdict(set), defaultdict(list)
    for r in issuer:
        if r['cnpj_full']:
            by_full[r['cnpj_full']].append(r)
            by_basic[r['cnpj_basic']].add(r['cnpj_full'])
        else:
            gap('emissor_sem_cnpj_completo', [r['observation_id']])
    for full, observations in sorted(by_full.items()):
        if any(r['identifier_conflict'] == 'true' for r in observations):
            gap('multiplos_codigos_cvm', [r['observation_id'] for r in observations], entity=full)
    for basic, fulls in sorted(by_basic.items()):
        if len(fulls) > 1:
            gap('colisao_cnpj_basico', [r['observation_id'] for f in sorted(fulls) for r in by_full[f]], entity=basic)
    for r in instruments:
        if r['cnpj_full']:
            inst_by_full[r['cnpj_full']].append(r)
        gap('instrumento_sem_certificacao_historica_b3', [r['observation_id']], entity=r['cnpj_full'],
            detail=r['instrument_class'])
    gap('universo_bdr_incompleto_sem_registro_cvm', [], detail='BDR nivel I dispensado exige fontes complementares; fatia 4')
    gap('mercado_historico_incompleto', [], detail='COTAHIST nao obtido (403); BDI nao certifica 60 referencias')

    # Preserve every observation but group identical directed/date claims for traversal.
    edges = {}
    for r in corporate:
        if not r['control_reason']:
            continue
        if not r['parent_full'] or not r['child_full']:
            gap('ponta_societaria_sem_identificador', [r['observation_id']], entity=r['parent_full'])
            continue
        key = (r['parent_full'], r['child_full'], r['control_date'], r['control_reason'])
        edges.setdefault(key, []).append(r['observation_id'])
    incoming = defaultdict(list)
    for (parent, child, when, reason), supports in sorted(edges.items(), key=lambda x: _json_text(x[0])):
        incoming[child[:8]].append(dict(parent=parent, child=child, date=when, reason=reason, support=sorted(supports)))
    # An edge belongs to a directed cycle iff its endpoints share a strongly
    # connected component (including self-loops). Two iterative DFS passes
    # classify every internal edge, not only DFS backedges and tree paths.
    outgoing, reverse = defaultdict(set), defaultdict(set)
    for child_edges in incoming.values():
        for edge in child_edges:
            outgoing[edge['parent']].add(edge['child'])
            reverse[edge['child']].add(edge['parent'])
    adjacency = {node: tuple(sorted(children)) for node, children in outgoing.items()}
    visited, finished = set(), []
    for origin in sorted(set(outgoing) | set(reverse)):
        if origin in visited:
            continue
        visited.add(origin)
        stack = [(origin, iter(adjacency.get(origin, ())))]
        while stack:
            child = next(stack[-1][1], None)
            if child is None:
                finished.append(stack[-1][0])
                stack.pop()
            elif child not in visited:
                visited.add(child)
                stack.append((child, iter(adjacency.get(child, ()))))
    components = {}
    for origin in reversed(finished):
        if origin in components:
            continue
        components[origin] = origin
        pending = [origin]
        while pending:
            node = pending.pop()
            for parent in reverse.get(node, ()):
                if parent not in components:
                    components[parent] = origin
                    pending.append(parent)
    cyclic_support = {support for child_edges in incoming.values() for edge in child_edges
                      if components[edge['parent']] == components[edge['child']]
                      for support in edge['support']}
    if cyclic_support:
        gap('ciclo_societario', sorted(cyclic_support), detail='Ciclo por identificadores completos; nao confirma controle')
    paths_cache = {}
    path_records = {}

    def paths(basic):
        if basic in paths_cache:
            return paths_cache[basic]
        found, cycles = [], set()
        stack = [(basic, (), (basic,), None)]
        while stack:
            current, route, visited, exact_child = stack.pop()
            for edge in incoming.get(current, []):
                # A multihop junction requires the complete identifier; basic-only
                # concordance at the terminal BCB institution remains candidacy.
                if exact_child is not None and edge['child'] != exact_child:
                    continue
                parent_basic = edge['parent'][:8]
                if parent_basic in visited:
                    cycles.update(edge['support'])
                    continue
                next_route = route + (edge,)
                if edge['parent'] in by_full:
                    # Intern the complete ordered route once, before quarters and
                    # perspectives reference it. Never materialize it per relation.
                    route_json = _json_text(list(next_route))
                    path_id = 'caminho:' + hashlib.sha256(route_json.encode('utf8')).hexdigest()
                    if path_id not in path_records:
                        path_records[path_id] = dict(observation_id=path_id,
                            issuer_full=next_route[-1]['parent'], terminal_basic=next_route[0]['child'][:8],
                            route_json=route_json,
                            corporate_support=_json_text(sorted({s for e in next_route for s in e['support']})))
                    found.append((edge['parent'], next_route, path_id))
                stack.append((parent_basic, next_route, visited + (parent_basic,), edge['parent']))
        if cycles:
            gap('ciclo_societario', sorted(cycles), entity=basic)
        paths_cache[basic] = found
        return found

    cad_index = {(r['Data'], r['CodInst']): r for r in cad}
    associations = {}
    for row in cad:
        reference, code = row['Data'], row['CodInst']
        if row['Td'] != 'I':
            continue
        eligible = bool(re.fullmatch(r'[0-9]{8}', code or ''))
        if not eligible:
            gap('codigo_individual_nao_cnpj_basico', [row['observation_id']], reference, code, 'individual')
        targets = [('individual', code)]
        for perspective, field in [('financeiro', 'CodConglomeradoFinanceiro'), ('prudencial', 'CodConglomeradoPrudencial')]:
            group_code = row[field]
            if group_code is None:
                continue
            group = cad_index.get((reference, group_code)) if group_code else None
            if group is not None and group['Td'] != 'C':
                group = None
            leader_code = row['CnpjInstituicaoLider']
            leader = cad_index.get((reference, leader_code)) if re.fullmatch('[0-9]{8}', leader_code or '') else None
            if leader is not None and leader['Td'] != 'I':
                leader = None
            v = dict(observation_id=_observation('vinculo', len(tables['vinculos_cadastrais']) + 1),
                     reference=reference, institution=code, perspective=perspective, entity=group_code,
                     cadastro_support=row['observation_id'], group_support=group['observation_id'] if group else None,
                     leader_support=leader['observation_id'] if leader else None, leader_scope='nativo_nao_desambiguado',
                     CnpjInstituicaoLider=row['CnpjInstituicaoLider'])
            for prefix, native in [('institution_', row), ('group_', group), ('leader_', leader)]:
                v.update({prefix + f: native.get(f) if native else None for f in ATTRIBUTES})
            tables['vinculos_cadastrais'].append(v)
            if group_code:
                targets.append((perspective, group_code))
            else:
                gap('codigo_grupo_vazio', [row['observation_id']], reference, code, perspective)
            if group is None:
                gap('atributos_grupo_ausentes', [row['observation_id']], reference, group_code, perspective)
        if not eligible:
            continue
        candidates = [(full, (), None) for full in sorted(by_basic.get(code, set()))] + paths(code)
        if not candidates:
            gap('sem_correspondencia_cvm_nao_prova_companhia_fechada', [row['observation_id']], reference, code, 'individual')
        for full, route, path_id in candidates:
            conflict = len(by_basic[full[:8]]) > 1 or any(r['identifier_conflict'] == 'true' for r in by_full[full])
            dates = {edge['date'] for edge in route}
            simultaneous = (bool(route) and dates == {_quarter(reference).isoformat()}
                            and not any(s in cyclic_support for e in route for s in e['support']))
            state = ('conflito_identificador' if conflict else
                     'declaracao_controle_datada' if simultaneous else
                     'candidatura_controle_sem_vigencia' if route else 'candidatura_cadastral')
            for perspective, entity in targets:
                key = (reference, full, perspective, entity, state)
                a = associations.setdefault(key, dict(institution_ids=set(), cadastro_support=set(), corporate_support=set(), control_paths=set()))
                a['institution_ids'].add(code)
                a['cadastro_support'].add(row['observation_id'])
                a['corporate_support'].update(s for edge in route for s in edge['support'])
                if route:
                    a['control_paths'].add(path_id)
    for key, a in sorted(associations.items()):
        reference, full, perspective, entity, state = key
        observations, inst = by_full[full], inst_by_full[full]
        dates = {r['observation_id']: {kind.lower(): _interval_state(r['Data_Inicio_' + kind], r['Data_Fim_' + kind], reference)
                                     for kind in ('Listagem', 'Negociacao')} for r in inst}
        r = dict(observation_id=_observation('relacao', len(tables['relacao_trimestral']) + 1),
                 reference=reference, issuer_full=full, issuer_basic=full[:8], perspective=perspective, entity=entity,
                 evidence_state=state, cvm_codes=_json_text(sorted({r['cvm_code'] for r in observations if r['cvm_code']})),
                 issuer_support=_json_text(sorted(r['observation_id'] for r in observations)),
                 instrument_support=_json_text(sorted(r['observation_id'] for r in inst)),
                 instrument_dates=_json_text(dates), market_state=MARKET_STATE)
        r.update({k: _json_text(sorted(v)) for k, v in a.items()})
        tables['relacao_trimestral'].append(r)
    tables['caminhos_societarios'] = [path_records[key] for key in sorted(path_records)]
    for reference in REFERENCES:
        native = [r for r in cad if r['Data'] == reference]
        related = [r for r in tables['relacao_trimestral'] if r['reference'] == reference]
        tables['cobertura'].append(dict(observation_id='cobertura:' + reference, reference=reference,
            cadastro_rows=str(len(native)), individual_rows=str(sum(r['Td'] == 'I' for r in native)),
            relationship_rows=str(len(related)), states=_json_text(dict(Counter(r['evidence_state'] for r in related))),
            gap_rows=str(sum(r['reference'] == reference for r in gaps)), market_state=MARKET_STATE))
    return tables


def _prepare(cvm, cvm_manifest, cadastro, corporate, corporate_manifest):
    with cadastro_reader.open_cadastro(cadastro) as conn:
        cursor = conn.execute('select * from cadastro where Data >= ? and Data <= ? order by Data, CodInst', ['201003', '202412'])
        fields = tuple(d[0] for d in cursor.description)
        if fields != cadastro_reader.FIELDS + cadastro_reader.ORIGIN:
            raise ValueError('Unexpected native cadastro schema')
        cad = [dict(observation_id=_observation('cadastro', n), **dict(zip(fields, values)))
               for n, values in enumerate(cursor.fetchall(), 1)]
    if {r['Data'] for r in cad} != set(REFERENCES):
        raise ValueError('Cadastro must contain all 60 quarterly references')
    issuer = []
    for kind in ('cad', 'index', 'geral'):
        for n, row in enumerate(_read_input(cvm, cvm_manifest, cvm_reader.TABLES[kind]), 1):
            issuer.append(_issuer_observation(kind, row, n))
    _issuer_conflicts(issuer)
    instruments = []
    for n, row in enumerate(_read_input(cvm, cvm_manifest, cvm_reader.TABLES['valmob']), 1):
        instruments.append(_instrument_observation(row, n))
    corporate_rows = []
    for kind, name in corporate_reader.TABLES.items():
        for n, row in enumerate(_read_input(corporate, corporate_manifest, name), 1):
            corporate_rows.append(_corporate_observation(kind, row, n))
    return _derive(cad, issuer, instruments, corporate_rows)


def _csv_bytes(fields, rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fields, quoting=csv.QUOTE_NOTNULL, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf8')


def _write_csv(path, fields, rows):
    """Stream canonical UTF-8 CSV; count bytes before each write, including header."""
    digest, size = hashlib.sha256(), 0
    with path.open('wb') as stream:
        class Sink:
            def write(self, text):
                nonlocal size
                raw = text.encode('utf8')
                if size + len(raw) > MAX_TABLE_BYTES:
                    raise ValueError('Historical CSV size limit exceeded: ' + path.name)
                stream.write(raw)
                digest.update(raw)
                size += len(raw)
                return len(text)
        writer = csv.DictWriter(Sink(), fields, quoting=csv.QUOTE_NOTNULL, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    return dict(sha256=digest.hexdigest(), bytes=size, rows=len(rows), headers=list(fields), key=['observation_id'])


def _parse_csv(raw, fields):
    """Read canonical QUOTE_NOTNULL on Python 3.12 as well as newer runtimes.

    Python 3.12 exposes the writer constant but its CSV reader does not yet
    preserve unquoted nulls. The finite output grammar quotes every non-null
    field; this lexer retains that distinction, including multiline strings.
    """
    text = raw.decode('utf8')
    token = re.compile(r'(?:"((?:[^"]|"")*)"|)(,|\n)')
    position, record, rows = 0, [], []
    while position < len(text):
        match = token.match(text, position)
        if match is None:
            raise ValueError('Noncanonical CSV/null encoding')
        value = match.group(1)
        record.append(value.replace('""', '"') if value is not None else None)
        position = match.end()
        if match.group(2) == '\n':
            if len(record) != len(fields):
                raise ValueError('Historical CSV width mismatch')
            if not rows:
                if record != list(fields):
                    raise ValueError('Historical CSV header mismatch')
                rows.append(None)
            else:
                rows.append(dict(zip(fields, record)))
            record = []
    if record or not rows:
        raise ValueError('Incomplete historical CSV')
    return rows[1:]


def _quality(tables):
    return dict(contract='historical-issuer-links-quality-v2', market_state=MARKET_STATE,
                references=list(REFERENCES), legal_identity_certified=False, academic_eligibility_adopted=False,
                counts={kind + '.csv': len(rows) for kind, rows in tables.items()},
                relationship_states=dict(Counter(r['evidence_state'] for r in tables['relacao_trimestral'])),
                gap_reasons=dict(Counter(r['reason'] for r in tables['lacunas'])))


def _validate_observations(tables):
    """Recompute technical columns from literal fields, independently of hashes."""
    issuer = []
    for kind in ('cad', 'index', 'geral'):
        fields = (*cvm_reader.CAD_FIELDS, *cvm_reader.LINEAGE) if kind == 'cad' else (*cvm_reader.HEADERS[kind], *cvm_reader.LINEAGE)
        rows = [r for r in tables['emissores'] if r['source_table'] == cvm_reader.TABLES[kind]]
        issuer.extend(_issuer_observation(kind, {f: r[f] for f in fields}, n) for n, r in enumerate(rows, 1))
    _issuer_conflicts(issuer)
    if issuer != tables['emissores']:
        raise ValueError('Issuer native/technical projection mismatch')
    fields = (*cvm_reader.HEADERS['valmob'], *cvm_reader.LINEAGE)
    instruments = [_instrument_observation({f: r[f] for f in fields}, n)
                   for n, r in enumerate(tables['instrumentos'], 1)]
    if instruments != tables['instrumentos']:
        raise ValueError('Instrument native/technical projection mismatch')
    corporate = []
    for kind, name in corporate_reader.TABLES.items():
        fields = (*corporate_reader.FIELDS[kind], *corporate_reader.LINEAGE)
        rows = [r for r in tables['societario'] if r['source_table'] == name]
        corporate.extend(_corporate_observation(kind, {f: r[f] for f in fields}, n) for n, r in enumerate(rows, 1))
    if corporate != tables['societario']:
        raise ValueError('Corporate native/technical projection mismatch')
    cad = tables['cadastro']
    if (cad != sorted(cad, key=lambda r: (r['Data'], r['CodInst']))
            or any(r['observation_id'] != _observation('cadastro', n) for n, r in enumerate(cad, 1))):
        raise ValueError('Native cadastro order/observation key mismatch')


def build_historical_issuer_links(cvm, expected_cvm_sha256, cadastro, expected_cadastro_sha256,
                                  corporate, expected_corporate_sha256, output):
    """Build a deterministic new package from three authenticated offline packages."""
    output = cvm_reader._plain_path(output)
    if output.exists():
        raise ValueError('Output destination must be new')
    cvm, cadastro, corporate = map(cvm_reader._plain_path, (cvm, cadastro, corporate))
    cvm_manifest = cvm_reader.verify_cvm_metadata(cvm, expected_cvm_sha256)
    cvm_reader._pinned(cadastro / 'manifest.json', expected_cadastro_sha256)
    corporate_manifest = corporate_reader.verify_corporate_metadata(corporate, expected_corporate_sha256)
    tables = _prepare(cvm, cvm_manifest, cadastro, corporate, corporate_manifest)
    cvm_reader._pinned(cadastro / 'manifest.json', expected_cadastro_sha256)
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    for kind, fields in SCHEMAS.items():
        files[kind + '.csv'] = _write_csv(output / (kind + '.csv'), fields, tables[kind])
    files['quality.json'] = cvm_reader._write_json(output / 'quality.json', _quality(tables))
    manifest = dict(contract=CONTRACT, references=list(REFERENCES), output_encoding='utf-8', csv_quoting='QUOTE_NOTNULL',
                    sources=dict(cvm=expected_cvm_sha256, cadastro=expected_cadastro_sha256, corporate=expected_corporate_sha256),
                    files=files, counts={kind + '.csv': len(rows) for kind, rows in tables.items()})
    receipt = cvm_reader._write_json(output / 'manifest.json', manifest)
    return dict(manifest=str(output / 'manifest.json'), manifest_sha256=receipt['sha256'], counts=manifest['counts'])


def _load(output, expected_manifest_sha256):
    output = cvm_reader._plain_path(output)
    manifest = cvm_reader._json(cvm_reader._pinned(output / 'manifest.json', expected_manifest_sha256))
    expected = {kind + '.csv' for kind in SCHEMAS} | {'quality.json'}
    if (set(manifest) != {'contract', 'references', 'output_encoding', 'csv_quoting', 'sources', 'files', 'counts'}
            or manifest['contract'] != CONTRACT or manifest['references'] != list(REFERENCES)
            or manifest['output_encoding'] != 'utf-8' or manifest['csv_quoting'] != 'QUOTE_NOTNULL'
            or set(manifest['files']) != expected or set(manifest['counts']) != expected - {'quality.json'}
            or set(manifest['sources']) != {'cvm', 'cadastro', 'corporate'}
            or any(not isinstance(p, str) or not re.fullmatch('[0-9a-f]{64}', p) for p in manifest['sources'].values())
            or {p.name for p in output.iterdir()} != expected | {'manifest.json'}):
        raise ValueError('Invalid closed historical manifest/inventory')
    tables = {}
    for kind, fields in SCHEMAS.items():
        name, entry = kind + '.csv', manifest['files'][kind + '.csv']
        raw = cvm_reader._pinned(cvm_reader._contained(output, name), entry['sha256'], MAX_TABLE_BYTES)
        try:
            rows = _parse_csv(raw, fields)
            if _csv_bytes(fields, rows) != raw:
                raise ValueError('Noncanonical CSV/null encoding')
        except (UnicodeError, csv.Error, TypeError) as error:
            raise ValueError('Invalid historical CSV') from error
        if (entry != dict(sha256=cvm_reader._sha(raw), bytes=len(raw), rows=len(rows), headers=list(fields), key=['observation_id'])
                or manifest['counts'][name] != len(rows)
                or any(not r['observation_id'] for r in rows)
                or len({r['observation_id'] for r in rows}) != len(rows)):
            raise ValueError('Historical schema/count/key mismatch')
        tables[kind] = rows
    cad = tables['cadastro']
    if ({r['Data'] for r in cad} != set(REFERENCES)
            or any(not r['CodInst'] for r in cad)
            or len({(r['Data'], r['CodInst']) for r in cad}) != len(cad)):
        raise ValueError('Invalid native temporal cadastro keys/coverage')
    _validate_observations(tables)
    rebuilt = _derive(cad, tables['emissores'], tables['instrumentos'], tables['societario'])
    for kind in ('vinculos_cadastrais', 'relacao_trimestral', 'caminhos_societarios', 'cobertura', 'lacunas'):
        if tables[kind] != rebuilt[kind]:
            raise ValueError('Historical relationship/coverage replay mismatch: ' + kind)
    entry = manifest['files']['quality.json']
    raw = cvm_reader._pinned(cvm_reader._contained(output, 'quality.json'), entry['sha256'], MAX_TABLE_BYTES)
    if (entry != dict(sha256=cvm_reader._sha(raw), bytes=len(raw))
            or cvm_reader._json(raw) != _quality(tables)):
        raise ValueError('Historical quality mismatch')
    return manifest, tables


def verify_historical_issuer_links(output, expected_manifest_sha256):
    """Authenticate bytes, finite schemas, keys and deterministic derived tables."""
    return _load(output, expected_manifest_sha256)[0]


def query_historical_issuer_links(output, expected_manifest_sha256, *, reference=None, entity=None, perspective=None,
                                  supplement=None, expected_supplement_sha256=None,
                                  expected_supplement_index_sha256=None):
    """Return JSON-ready observations, sources, states and relevant gaps; no sums."""
    if reference is not None and reference not in REFERENCES:
        raise ValueError('Reference must be one of the 60 native AAAAMM quarters')
    if perspective is not None and perspective not in PERSPECTIVES:
        raise ValueError('Invalid perspective')
    if entity is not None and (not isinstance(entity, str) or not entity):
        raise ValueError('Entity must be a nonempty literal identifier')
    trio = (supplement, expected_supplement_sha256, expected_supplement_index_sha256)
    if any(item is not None for item in trio) and not all(item is not None for item in trio):
        raise ValueError('Supplement path, manifest pin and external index pin are required together')
    manifest, tables = _load(output, expected_manifest_sha256)
    result = _query_historical_tables(manifest, tables, reference, entity, perspective)
    if supplement is not None:
        selector = entity
        if _full(entity) is not None:
            selector = 'CNPJ14:' + _full(entity)
        admitted, derived, quality, package = _load_issuer_supplement(supplement,
            expected_supplement_sha256, expected_supplement_index_sha256,
            expected_manifest_sha256, tables)
        result['suplemento'] = _query_issuer_supplement(admitted, derived, quality, package,
            tables, selector, reference, perspective)
    return result


def _query_historical_tables(manifest, tables, reference, entity, perspective):
    """Reuse one authenticated image; this helper is not an input API."""
    entity_full = _full(entity)
    matching = {r['cnpj_full'] for r in tables['emissores'] if r['cnpj_full'] and entity is not None and entity in
                (r['observation_id'], r['cnpj_full'], r['cnpj_basic'], r['cvm_code'])}
    if entity_full:
        matching.add(entity_full)
    relationships = [r for r in tables['relacao_trimestral']
        if (reference is None or r['reference'] == reference)
        and (perspective is None or r['perspective'] == perspective)
        and (entity is None or entity in (r['observation_id'], r['entity'], r['issuer_full'], r['issuer_basic'])
             or r['issuer_full'] in matching or entity in json.loads(r['institution_ids']))]
    supports = {key: {s for r in relationships for s in json.loads(r[key])}
                for key in ('issuer_support', 'instrument_support', 'corporate_support', 'cadastro_support')}
    gaps = [r for r in tables['lacunas'] if (reference is None or r['reference'] in (None, reference))
            and (perspective is None or r['perspective'] in (None, perspective, 'individual'))
            and (entity is None or r['entity'] in (entity, entity_full) or r['entity'] in matching)]
    result = dict(contract=CONTRACT, sources=manifest['sources'], market_state=MARKET_STATE,
                  relacao_trimestral=relationships, lacunas=gaps,
                  cobertura=[r for r in tables['cobertura'] if reference is None or r['reference'] == reference])
    path_ids = {key for r in relationships for key in json.loads(r['control_paths'])}
    result['caminhos_societarios'] = [r for r in tables['caminhos_societarios'] if r['observation_id'] in path_ids]
    result['emissores'] = [r for r in tables['emissores'] if entity is None or r['observation_id'] in supports['issuer_support']
                           or r['cnpj_full'] in matching or r['observation_id'] == entity]
    result['instrumentos'] = [r for r in tables['instrumentos'] if entity is None or r['observation_id'] in supports['instrument_support']
                              or r['cnpj_full'] in matching or r['observation_id'] == entity]
    result['societario'] = [r for r in tables['societario'] if entity is None or r['observation_id'] in supports['corporate_support']
                            or r['parent_full'] in matching or r['child_full'] in matching or r['observation_id'] == entity]
    result['cadastro'] = [r for r in tables['cadastro'] if (reference is None or r['Data'] == reference)
                          and (entity is None or r['observation_id'] in supports['cadastro_support']
                               or entity in (r['observation_id'], r['CodInst']))]
    result['vinculos_cadastrais'] = [r for r in tables['vinculos_cadastrais'] if r['cadastro_support'] in supports['cadastro_support']
                                    and (perspective is None or r['perspective'] == perspective)]
    return result

# The supplement is a separate, finite input contract; none of the v2 tables change.
SUPPLEMENT_INPUT_CONTRACT = 'historical-issuer-supplement-input-v1'
MAX_SUPPLEMENT_INDEX_BYTES = 4 * 1024 * 1024
MAX_SUPPLEMENT_BODY_BYTES = 16 * 1024 * 1024
MAX_SUPPLEMENT_EVIDENCE_BYTES = 256 * 1024 * 1024  # Total bundle, including canonical index.
_SUPPLEMENT_FIELDS = {
    'sources': 'source_id alias url body_path body_sha256 body_bytes retrieved_at publication_date source_nature document_state projection',
    'entities': 'entity_id role native_name identifiers native_payload',
    'claims': 'claim_id fact_type subject_id object_id native_payload fact_date reference time_state support support_claim_ids evidence_nature identity_confidence temporal_confidence conflict_state adoption_state rationale',
    'unresolved': 'unresolved_id candidate_id missing_claim_kind reason evidence_needed support_claim_ids',
}
_SUPPLEMENT_IDS = {'sources': 'source', 'entities': 'entity', 'claims': 'claim', 'unresolved': 'unresolved'}
_SUPPLEMENT_NAMESPACES = {
    'company': {'CIK', 'CNPJ14', 'CNPJ_BASE8', 'CVM_CODE', 'LEI'},
    'operator_br': {'CNPJ14', 'CNPJ_BASE8', 'BCB_CODINST', 'LEI'},
    'intermediary': {'CIK', 'CNPJ14', 'CNPJ_BASE8', 'LEI'},
    'instrument': {'PROGRAM_ID', 'TICKER'}, 'bcb_unit': {'BCB_CODINST'},
}
_SUPPLEMENT_FACTS = {'issuer_identity', 'instrument_program', 'instrument_observation',
    'participation_declared', 'bcb_membership', 'analytical_identification', 'event', 'capture_status'}


def _supplement_require(condition, message):
    if not condition:
        raise ValueError('Issuer supplement: ' + message)


def _supplement_schema(record, fields, name):
    _supplement_require(isinstance(record, dict) and set(record) == set(fields.split()), 'invalid ' + name + ' schema')


def _supplement_string(value, name, nullable=False):
    _supplement_require((nullable and value is None) or (isinstance(value, str) and bool(value)), 'invalid ' + name)


def _supplement_enum(value, choices, name):
    _supplement_require(isinstance(value, str) and value in choices, 'invalid ' + name)


def _supplement_sorted(values, key, name):
    _supplement_require(isinstance(values, list), name + ' must be an array')
    keys = [key(value) for value in values]
    _supplement_require(len(set(keys)) == len(keys), 'duplicate ' + name)
    _supplement_require(keys == sorted(keys), 'noncanonical order: ' + name)


def _supplement_payload(value):
    """Keep opaque native JSON integral, without coercing any numerical token.

    Structured identifiers are separately required to be strings. Native JSON
    integers/booleans/finite numbers remain native, not new financial measures.
    """
    import math
    if isinstance(value, dict):
        for member in value.values():
            _supplement_payload(member)
    elif isinstance(value, list):
        for member in value:
            _supplement_payload(member)
    else:
        _supplement_require(value is None or isinstance(value, (str, int, float, bool)), 'invalid native JSON value')
        _supplement_require(not isinstance(value, float) or math.isfinite(value), 'nonfinite native JSON value')


def _supplement_locator(locator, source_id, evidence):
    _supplement_schema(locator, 'start end excerpt', 'locator')
    _supplement_require(source_id in evidence and evidence[source_id]['text'] is not None, 'locator requires a pinned projection')
    start, end, excerpt = locator['start'], locator['end'], locator['excerpt']
    text = evidence[source_id]['text']
    _supplement_require(type(start) is int and type(end) is int and isinstance(excerpt, str)
        and 0 <= start < end <= len(text) and text[start:end] == excerpt, 'Unicode locator/excerpt mismatch')
    return excerpt


def _supplement_support_key(record):
    locator = record['locator']
    return (record['source_id'], locator['start'], locator['end'], locator['excerpt'])


def _supplement_identifier(identifier, entity, sources, evidence):
    from urllib.parse import urlsplit
    _supplement_schema(identifier, 'namespace literal source_id locator', 'identifier')
    namespace, literal = identifier['namespace'], identifier['literal']
    _supplement_enum(namespace, _SUPPLEMENT_NAMESPACES[entity['role']], 'identifier namespace for role')
    _supplement_string(literal, 'identifier literal')
    source_id = identifier['source_id']
    _supplement_require(isinstance(source_id, str) and source_id in sources, 'unknown identifier source')
    excerpt = _supplement_locator(identifier['locator'], source_id, evidence)
    patterns = {'CNPJ14': r'[0-9]{14}', 'CNPJ_BASE8': r'[0-9]{8}',
                'CIK': r'[0-9]{1,10}', 'CVM_CODE': r'[0-9]{1,7}', 'LEI': r'[A-Z0-9]{20}'}
    if namespace in patterns:
        _supplement_require(re.fullmatch(patterns[namespace], literal) is not None, 'invalid ' + namespace + ' literal')
    # Only the source's exact CNPJ punctuation can be removed; no digit completion.
    cnpjs = [re.sub(r'[./-]', '', token) for token in re.findall(
        r'(?<![\w./+-])(?:[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}|[0-9]{14})(?![\w./+-])', excerpt)]
    if namespace == 'CNPJ14':
        matches = literal in cnpjs
    elif namespace == 'CNPJ_BASE8':
        matches = any(value[:8] == literal for value in cnpjs) or re.search(r'(?<![\w./+-])' + literal + r'(?![\w./+-])', excerpt) is not None
    elif namespace == 'CVM_CODE':
        matches = any((value.lstrip('0') or '0') == (literal.lstrip('0') or '0')
                      for value in re.findall(r'(?<![\w./+-])[0-9]+(?![\w./+-])', excerpt))
    elif namespace == 'CIK':
        url = urlsplit(sources[source_id]['url'])
        sec = url.scheme == 'https' and url.netloc in ('www.sec.gov', 'sec.gov') and ('/Archives/edgar/data/' + literal + '/') in url.path
        matches = re.search(r'(?<![\w./+-])' + literal + r'(?![\w./+-])', excerpt) is not None or (sec and entity['native_name'] in excerpt)
    else:
        matches = literal in excerpt
    _supplement_require(matches, 'identifier literal lacks exact source proof: ' + namespace)


def _admit_issuer_supplement_index(index, expected_index_sha256, evidence_root):
    """Authenticate R3a only; no core loading, PDF extraction or associations.

    Returns contract/index_sha256, the four original canonical lists, and
    evidence[source_id] = {body: bytes, projection: bytes|None, text: str|None}.
    A projection is a manually reviewed declaration pinned to its source body;
    matching hashes/offsets do not certify extraction or the claim's truth.
    """
    from datetime import datetime
    index = cvm_reader._plain_path(index)
    raw = cvm_reader._pinned(index, expected_index_sha256, MAX_SUPPLEMENT_INDEX_BYTES)
    _supplement_require(len(raw) <= MAX_SUPPLEMENT_EVIDENCE_BYTES, 'total bundle byte budget exceeded')
    value = cvm_reader._json(raw)
    _supplement_schema(value, 'contract sources entities claims unresolved', 'index')
    _supplement_require(value['contract'] == SUPPLEMENT_INPUT_CONTRACT, 'unsupported input contract')
    # Check canonical bytes, including exactly one final LF, without rewriting input.
    _supplement_require(raw == (_json_text(value) + '\n').encode('utf8'), 'noncanonical JSON bytes')
    root = cvm_reader._plain_path(evidence_root)
    _supplement_require(root.is_dir(), 'evidence_root must be a directory')
    by_kind = {}
    for collection, fields in _SUPPLEMENT_FIELDS.items():
        _supplement_require(isinstance(value[collection], list), collection + ' must be an array')
        field = _SUPPLEMENT_IDS[collection] + '_id'
        for record in value[collection]:
            _supplement_schema(record, fields, collection)
            _supplement_string(record[field], field)
        _supplement_sorted(value[collection], lambda record: record[field], collection)
        by_kind[collection] = {record[field]: record for record in value[collection]}
    sources, entities, claims = (by_kind[name] for name in ('sources', 'entities', 'claims'))
    evidence, paths, unique_bytes, blobs, texts = {}, {}, {}, {}, {}

    def pinned_file(relative, digest, size, kind):
        _supplement_require(type(size) is int and size >= 0, 'invalid evidence byte count')
        path = cvm_reader._contained(root, relative)
        _supplement_require(path.relative_to(root).as_posix() == relative, 'noncanonical evidence path')
        key = str(path).casefold()
        descriptor = (relative, kind, digest, size)
        _supplement_require(key not in paths or paths[key] == descriptor, 'evidence path collision')
        paths[key] = descriptor
        limit = MAX_SUPPLEMENT_BODY_BYTES if kind == 'body' else MAX_SUPPLEMENT_EVIDENCE_BYTES
        body = cvm_reader._pinned(path, digest, limit)
        _supplement_require(len(body) == size, 'evidence byte count mismatch')
        unique_bytes[(kind, digest)] = size
        _supplement_require(len(raw) + sum(unique_bytes.values()) <= MAX_SUPPLEMENT_EVIDENCE_BYTES, 'total bundle byte budget exceeded')
        # Authenticate every declared path, but retain a single byte image for
        # aliases/pages sharing a hash, as required by the unique-byte budget.
        return blobs.setdefault((kind, digest), body)

    for source_id, source in sources.items():
        for field in ('alias', 'url'):
            _supplement_string(source[field], 'source ' + field)
        _supplement_enum(source['source_nature'], ('regulator', 'issuer_document', 'official_news', 'research_evidence', 'accepted_dossier'), 'source_nature')
        _supplement_enum(source['document_state'], ('substantive', 'blocked', 'shell', 'search_excerpt'), 'document_state')
        publication = source['publication_date']
        _supplement_require(publication is None or (isinstance(publication, str) and _date(publication) is not None), 'invalid publication_date')
        retrieved = source['retrieved_at']
        if retrieved is not None:
            _supplement_require(isinstance(retrieved, str) and re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T', retrieved) is not None, 'invalid retrieved_at')
            try:
                instant = datetime.fromisoformat(retrieved)
            except ValueError as error:
                raise ValueError('Issuer supplement: invalid retrieved_at') from error
            _supplement_require(instant.utcoffset() is not None, 'retrieved_at must include timezone')
        body = pinned_file(source['body_path'], source['body_sha256'], source['body_bytes'], 'body')
        projection, text = None, None
        if source['projection'] is not None:
            projected = source['projection']
            _supplement_schema(projected, 'path sha256 bytes representation body_sha256 page', 'projection')
            _supplement_string(projected['representation'], 'projection representation')
            _supplement_require(projected['body_sha256'] == source['body_sha256'], 'projection body pin mismatch')
            _supplement_require(projected['page'] is None or (type(projected['page']) is int and projected['page'] >= 1), 'invalid physical page')
            projection = pinned_file(projected['path'], projected['sha256'], projected['bytes'], 'projection')
            try:
                if projected['sha256'] not in texts:
                    texts[projected['sha256']] = projection.decode('utf8')
                text = texts[projected['sha256']]
            except UnicodeError as error:
                raise ValueError('Issuer supplement: projection must be UTF-8') from error
        evidence[source_id] = dict(body=body, projection=projection, text=text)
    for entity in entities.values():
        _supplement_enum(entity['role'], _SUPPLEMENT_NAMESPACES, 'entity role')
        _supplement_string(entity['native_name'], 'native_name')
        _supplement_require(isinstance(entity['native_payload'], dict), 'native_payload must be an object')
        _supplement_payload(entity['native_payload'])
        _supplement_require(isinstance(entity['identifiers'], list), 'identifiers must be an array')
        for identifier in entity['identifiers']:
            _supplement_identifier(identifier, entity, sources, evidence)
        _supplement_sorted(entity['identifiers'], lambda item: (item['namespace'], item['literal'], *_supplement_support_key(item)), 'identifiers')
    roles = set(_SUPPLEMENT_NAMESPACES)
    parties = {'company', 'operator_br', 'intermediary'}
    matrix = {'issuer_identity': ({'company'}, {None}),
        'instrument_program': ({'company'}, {'instrument'}), 'instrument_observation': ({'company'}, {'instrument'}),
        'participation_declared': (parties, parties), 'bcb_membership': ({'operator_br'}, {'bcb_unit'}),
        'analytical_identification': ({'company'}, {'operator_br'}), 'event': (roles, roles | {None}),
        'capture_status': (roles, {None})}
    for claim_id, claim in claims.items():
        kind = claim['fact_type']
        _supplement_enum(kind, _SUPPLEMENT_FACTS, 'fact_type')
        subject, obj = claim['subject_id'], claim['object_id']
        _supplement_require(isinstance(subject, str) and subject in entities, 'unknown claim subject')
        _supplement_require(obj is None or (isinstance(obj, str) and obj in entities), 'unknown claim object')
        _supplement_require(entities[subject]['role'] in matrix[kind][0]
            and (entities[obj]['role'] if obj is not None else None) in matrix[kind][1], 'fact type/role/object mismatch')
        _supplement_require(isinstance(claim['native_payload'], dict), 'native_payload must be an object')
        _supplement_payload(claim['native_payload'])
        _supplement_enum(claim['time_state'], ('document_point', 'analytical_point', 'unknown'), 'time_state')
        _supplement_enum(claim['evidence_nature'], ('literal_observation', 'documentary_declaration', 'analytical_inference', 'native_bcb'), 'evidence_nature')
        for field in ('identity_confidence', 'temporal_confidence'):
            _supplement_enum(claim[field], ('high', 'medium', 'low', 'unknown'), field)
        _supplement_enum(claim['conflict_state'], ('none_reported', 'unresolved', 'contradicted'), 'conflict_state')
        _supplement_enum(claim['adoption_state'], ('observation', 'candidate', 'association'), 'adoption_state')
        rationale = claim['rationale']
        _supplement_require(rationale is None or isinstance(rationale, str), 'invalid rationale')
        if claim['evidence_nature'] == 'analytical_inference' or claim['adoption_state'] == 'association' or claim['conflict_state'] != 'none_reported':
            _supplement_require(isinstance(rationale, str) and bool(rationale.strip()), 'rationale required')
        reference, fact_date, time_state = claim['reference'], claim['fact_date'], claim['time_state']
        _supplement_require(reference is None or (isinstance(reference, str) and reference in REFERENCES), 'invalid reference')
        _supplement_require(fact_date is None or (isinstance(fact_date, str) and _date(fact_date) is not None), 'invalid fact_date')
        if time_state == 'unknown':
            _supplement_require(reference is None, 'unknown time cannot have reference')
        if time_state == 'document_point' and reference is not None:
            _supplement_require(fact_date == _quarter(reference).isoformat()
                and claim['native_payload'].get('date_purpose') in ('snapshot', 'declared_as_of', 'native_reference'), 'reference requires declared quarter snapshot')
        if time_state == 'analytical_point':
            _supplement_require(reference is not None and claim['evidence_nature'] == 'analytical_inference'
                and isinstance(rationale, str) and bool(rationale.strip()), 'analytical point requires reference/inference/rationale')
        if kind == 'event':
            _supplement_require(reference is None, 'event cannot have quarter reference')
        if kind == 'bcb_membership':
            _supplement_require(reference is not None and time_state == 'document_point'
                and claim['evidence_nature'] == 'native_bcb' and claim['native_payload'].get('perspective') in PERSPECTIVES, 'invalid native BCB membership')
        _supplement_require(isinstance(claim['support'], list) and bool(claim['support']), 'textual support required')
        for support in claim['support']:
            _supplement_schema(support, 'source_id locator', 'support')
            source_id = support['source_id']
            _supplement_require(isinstance(source_id, str) and source_id in sources, 'unknown support source')
            _supplement_locator(support['locator'], source_id, evidence)
            state = sources[source_id]['document_state']
            _supplement_require(state not in ('blocked', 'shell') or kind == 'capture_status', 'blocked/shell only supports capture_status')
            _supplement_require(state != 'search_excerpt' or claim['adoption_state'] == 'candidate'
                or (claim['adoption_state'] == 'observation' and claim['evidence_nature'] == 'literal_observation'), 'search_excerpt only supports auxiliary observation/candidate')
        _supplement_sorted(claim['support'], _supplement_support_key, 'support')
        dependencies = claim['support_claim_ids']
        _supplement_require(isinstance(dependencies, list) and all(isinstance(item, str) and item in claims for item in dependencies), 'unknown support claim')
        _supplement_sorted(dependencies, lambda item: item, 'support_claim_ids')
        _supplement_require(claim_id not in dependencies, 'self support claim')
        if claim['adoption_state'] == 'association':
            _supplement_require(kind == 'analytical_identification' and bool(dependencies)
                and (reference is not None or time_state == 'unknown'), 'invalid association declaration')
            _supplement_require(any(item['namespace'] in ('CNPJ14', 'CNPJ_BASE8') for item in entities[obj]['identifiers']), 'association operator requires CNPJ identifier')
            for entity_id in (subject, obj):
                identifiers = entities[entity_id]['identifiers']
                _supplement_require(bool(identifiers) and all(sources[item['source_id']]['document_state'] == 'substantive'
                    for item in identifiers), 'association endpoints require substantive identifier support')
    # Kahn traversal validates the entire DAG and propagates admissibility once,
    # avoiding recursion limits and quadratic expansion of shared support paths.
    pending = {claim_id: len(claim['support_claim_ids']) for claim_id, claim in claims.items()}
    dependants = defaultdict(list)
    for claim_id, claim in claims.items():
        for dependency in claim['support_claim_ids']:
            dependants[dependency].append(claim_id)
    ready = [claim_id for claim_id, count in pending.items() if count == 0]
    admissible = {}
    while ready:
        claim_id = ready.pop()
        claim = claims[claim_id]
        admissible[claim_id] = (claim['conflict_state'] == 'none_reported' and claim['fact_type'] != 'capture_status'
            and claim['adoption_state'] != 'candidate'
            and all(sources[item['source_id']]['document_state'] == 'substantive' for item in claim['support'])
            and all(admissible[item] for item in claim['support_claim_ids']))
        _supplement_require(claim['adoption_state'] != 'association' or admissible[claim_id], 'association has inadmissible transitive support')
        for dependant in dependants[claim_id]:
            pending[dependant] -= 1
            if pending[dependant] == 0:
                ready.append(dependant)
    _supplement_require(len(admissible) == len(claims), 'cyclic support claims')
    for unresolved in value['unresolved']:
        _supplement_require(isinstance(unresolved['candidate_id'], str) and unresolved['candidate_id'] in entities, 'unknown unresolved candidate')
        _supplement_enum(unresolved['missing_claim_kind'], _SUPPLEMENT_FACTS | {'temporal_coverage', 'identifier', 'issuer_chain', 'market_coverage'}, 'missing_claim_kind')
        for field in ('reason', 'evidence_needed'):
            _supplement_string(unresolved[field], field)
        dependencies = unresolved['support_claim_ids']
        _supplement_require(isinstance(dependencies, list) and all(isinstance(item, str) and item in claims for item in dependencies), 'unknown unresolved support claim')
        _supplement_sorted(dependencies, lambda item: item, 'unresolved support_claim_ids')
    for collection, prefix in _SUPPLEMENT_IDS.items():
        field = prefix + '_id'
        for record in value[collection]:
            payload = {key: item for key, item in record.items() if key != field}
            expected = prefix + ':' + hashlib.sha256(_json_text(payload).encode('utf8')).hexdigest()
            _supplement_require(record[field] == expected, 'content ID mismatch: ' + field)
    # Recheck external authority after all local evidence has been authenticated.
    _supplement_require(cvm_reader._pinned(index, expected_index_sha256, MAX_SUPPLEMENT_INDEX_BYTES) == raw, 'index changed during admission')
    return dict(value, index_sha256=expected_index_sha256, evidence=evidence)


def validate_issuer_supplement_index(index, expected_index_sha256, evidence_root):
    """Return R3a integrity counts, not acceptance of data or derived associations."""
    admitted = _admit_issuer_supplement_index(index, expected_index_sha256, evidence_root)
    return dict(contract=admitted['contract'], index_sha256=admitted['index_sha256'],
                counts={name: len(admitted[name]) for name in _SUPPLEMENT_IDS})


SUPPLEMENT_CONTRACT = 'historical-issuer-supplement-v1'


def _supplement_id(prefix, record):
    return prefix + ':' + hashlib.sha256(_json_text(record).encode('utf8')).hexdigest()


def _supplement_closure(claims, seeds):
    closure, pending = set(), list(seeds)
    while pending:
        claim_id = pending.pop()
        if claim_id not in closure:
            closure.add(claim_id)
            pending.extend(claims[claim_id]['support_claim_ids'])
    return closure


def _derive_issuer_supplement(admitted, tables):
    """Only explicit curated adoption and native point-in-time CNPJ concordance."""
    entities = {r['entity_id']: r for r in admitted['entities']}
    claims = {r['claim_id']: r for r in admitted['claims']}
    result = dict(associations=[], undated_associations=[], derived_unresolved=[])
    native = defaultdict(list)
    for row in tables['cadastro']:
        if row['Td'] == 'I':
            native[(row['Data'], row['CodInst'])].append(row)
    memberships = defaultdict(list)
    for row in tables['vinculos_cadastrais']:
        memberships[(row['reference'], row['institution'])].append(row)

    def gap(claim, reason, supports, perspective=None):
        record = dict(candidate_id=claim['subject_id'], association_claim_id=claim['claim_id'],
            reference=claim['reference'], perspective=perspective, reason=reason,
            support_claim_ids=sorted(supports))
        record['observation_id'] = _supplement_id('derived-gap', record)
        result['derived_unresolved'].append(record)

    for claim in admitted['claims']:
        if claim['fact_type'] != 'analytical_identification':
            continue
        closure = _supplement_closure(claims, [claim['claim_id']])
        supports = closure - {claim['claim_id']}
        if claim['adoption_state'] != 'association':
            if claim['adoption_state'] == 'candidate':
                gap(claim, 'support_not_adoptable', closure)
            continue
        operator = entities[claim['object_id']]
        bases = {item['literal'][:8] for item in operator['identifiers']
                 if item['namespace'] in ('CNPJ14', 'CNPJ_BASE8')}
        instruments = sorted(r['claim_id'] for r in admitted['claims']
            if r['subject_id'] == claim['subject_id']
            and r['fact_type'] in ('instrument_program', 'instrument_observation'))
        record = dict(company_id=claim['subject_id'], operator_id=claim['object_id'],
            reference=claim['reference'], perspective=None, entity=None,
            association_claim_id=claim['claim_id'], instrument_claim_ids=instruments,
            support_claim_ids=sorted(supports), cadastro_support=None, group_support=None,
            leader_support=None, time_state=claim['time_state'], evidence_nature=claim['evidence_nature'],
            identity_confidence=claim['identity_confidence'], temporal_confidence=claim['temporal_confidence'],
            conflict_state=claim['conflict_state'], academic_eligibility='not_evaluated')
        if claim['time_state'] == 'unknown':
            # The operator and its pinned identifiers remain available through operator_id.
            record['observation_id'] = _supplement_id('association', record)
            result['undated_associations'].append(record)
            continue
        if len(bases) != 1:
            gap(claim, 'native_unit_ambiguous', closure)
            continue
        base = next(iter(bases))
        rows = native.get((claim['reference'], base), [])
        if not rows:
            gap(claim, 'native_unit_missing', closure)
            continue
        if len(rows) != 1:
            gap(claim, 'native_unit_ambiguous', closure)
            continue
        row = rows[0]
        links = memberships.get((claim['reference'], base), [])
        targets = [('individual', base, None)] + [(v['perspective'], v['entity'], v) for v in links]
        explicit_codes = {i['literal'] for i in operator['identifiers'] if i['namespace'] == 'BCB_CODINST'}
        mismatch = bool(explicit_codes - {base})
        for key in supports:
            member = claims[key]
            if member['fact_type'] != 'bcb_membership':
                continue
            codes = {i['literal'] for i in entities[member['object_id']]['identifiers']
                     if i['namespace'] == 'BCB_CODINST'}
            expected = {target for perspective, target, _ in targets
                        if perspective == member['native_payload']['perspective'] and target}
            if (member['subject_id'] != claim['object_id'] or member['reference'] != claim['reference']
                    or len(codes) != 1 or codes != expected):
                mismatch = True
        if mismatch:
            gap(claim, 'native_membership_mismatch', closure)
            continue
        for perspective, target, link in targets:
            if not target:
                gap(claim, 'native_group_empty', closure, perspective)
                continue
            relation = dict(record, perspective=perspective, entity=target,
                cadastro_support=row['observation_id'],
                group_support=link['group_support'] if link else None,
                leader_support=link['leader_support'] if link else None)
            relation['observation_id'] = _supplement_id('association', relation)
            result['associations'].append(relation)
    for rows in result.values():
        rows.sort(key=lambda row: row['observation_id'])
    return result


def _supplement_quality(admitted, derived):
    return dict(identity_certified=False, academic_eligibility_adopted=False,
        market_coverage_incomplete=True,
        counts={**{name: len(admitted[name]) for name in _SUPPLEMENT_IDS},
                **{name: len(rows) for name, rows in derived.items()}},
        source_natures=dict(sorted(Counter(r['source_nature'] for r in admitted['sources']).items())),
        claim_states={field: dict(sorted(Counter(r[field] for r in admitted['claims']).items()))
                      for field in ('evidence_nature', 'identity_confidence', 'temporal_confidence', 'time_state')},
        gap_reasons=dict(sorted(Counter(r['reason'] for r in derived['derived_unresolved']).items())),
        curated_gap_kinds=dict(sorted(Counter(r['missing_claim_kind'] for r in admitted['unresolved']).items())))


def _supplement_evidence_names(sources):
    return {r['source_id']: dict(body='evidence/' + r['body_sha256'] + '.body',
        projection='evidence/' + r['projection']['sha256'] + '.txt' if r['projection'] is not None else None)
        for r in sources}


def _write_supplement_json(path, value):
    raw = (_json_text(value) + '\n').encode('utf8')
    _supplement_require(len(raw) <= MAX_TABLE_BYTES, 'JSON byte budget exceeded')
    with path.open('xb') as stream:
        stream.write(raw)
    return dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def build_issuer_supplement(index, expected_index_sha256, evidence_root, core, expected_core_sha256, output):
    """Build a separate immutable package; no network or original-file changes."""
    output = cvm_reader._plain_path(output)
    _supplement_require(not output.exists(), 'output destination must be new')
    admitted = _admit_issuer_supplement_index(index, expected_index_sha256, evidence_root)
    _, tables = _load(core, expected_core_sha256)
    derived = _derive_issuer_supplement(admitted, tables)
    quality = _supplement_quality(admitted, derived)
    # Admission rechecks the authority; also recheck after the potentially long core load.
    expected_index = (_json_text({name: admitted[name] for name in ('contract', *_SUPPLEMENT_IDS)}) + '\n').encode('utf8')
    _supplement_require(cvm_reader._pinned(index, expected_index_sha256, MAX_SUPPLEMENT_INDEX_BYTES) == expected_index,
                        'index changed during projection')
    output.mkdir(parents=True, exist_ok=False)
    (output / 'evidence').mkdir()
    files, names = {}, _supplement_evidence_names(admitted['sources'])
    for source_id, mapping in names.items():
        for kind, relative in mapping.items():
            if relative is not None and relative not in files:
                raw = admitted['evidence'][source_id][kind]
                with (output / relative).open('xb') as stream:
                    stream.write(raw)
                files[relative] = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    for name in _SUPPLEMENT_IDS:
        files[name + '.json'] = _write_supplement_json(output / (name + '.json'), admitted[name])
    files['relations.json'] = _write_supplement_json(output / 'relations.json', derived)
    files['quality.json'] = _write_supplement_json(output / 'quality.json', quality)
    manifest = dict(contract=SUPPLEMENT_CONTRACT, index_sha256=expected_index_sha256,
        core_sha256=expected_core_sha256, evidence=names, files=files, counts=quality['counts'])
    _supplement_require(cvm_reader._pinned(index, expected_index_sha256, MAX_SUPPLEMENT_INDEX_BYTES) == expected_index,
                        'index changed during output projection')
    receipt = _write_supplement_json(output / 'manifest.json', manifest)
    return dict(manifest=str(output / 'manifest.json'), manifest_sha256=receipt['sha256'], counts=manifest['counts'])


def _load_issuer_supplement(output, expected_manifest_sha256, expected_index_sha256, expected_core_sha256, tables):
    """Authenticate package and replay against an already authenticated private core image."""
    output = cvm_reader._plain_path(output)
    raw_manifest = cvm_reader._pinned(output / 'manifest.json', expected_manifest_sha256, MAX_TABLE_BYTES)
    manifest = cvm_reader._json(raw_manifest)
    _supplement_schema(manifest, 'contract index_sha256 core_sha256 evidence files counts', 'manifest')
    _supplement_require(manifest['contract'] == SUPPLEMENT_CONTRACT
        and manifest['index_sha256'] == expected_index_sha256
        and manifest['core_sha256'] == expected_core_sha256, 'external index/core pin mismatch')
    _supplement_require(raw_manifest == (_json_text(manifest) + '\n').encode('utf8'), 'noncanonical manifest')
    _supplement_require(isinstance(manifest['files'], dict), 'invalid file inventory')
    blobs = {}
    for relative, entry in manifest['files'].items():
        _supplement_schema(entry, 'sha256 bytes', 'file entry')
        path = cvm_reader._contained(output, relative)
        _supplement_require(path.relative_to(output).as_posix() == relative, 'noncanonical output path')
        _supplement_require(type(entry['bytes']) is int and entry['bytes'] >= 0, 'invalid file size')
        limit = (MAX_SUPPLEMENT_BODY_BYTES if relative.endswith('.body') else
                 MAX_SUPPLEMENT_EVIDENCE_BYTES if relative.endswith('.txt') else MAX_TABLE_BYTES)
        raw = cvm_reader._pinned(path, entry['sha256'], limit)
        _supplement_require(len(raw) == entry['bytes'], 'file byte count mismatch')
        blobs[relative] = raw
    # Inspect every directory too: extra empty directories and reparse points are errors.
    inventory = set()
    for path in output.rglob('*'):
        cvm_reader._plain_path(path)
        relative = path.relative_to(output).as_posix()
        if path.is_dir():
            _supplement_require(relative == 'evidence', 'unexpected output directory')
        elif path.is_file():
            inventory.add(relative)
        else:
            raise ValueError('Issuer supplement: nonregular inventory entry')
    _supplement_require(inventory == set(blobs) | {'manifest.json'}
        and (output / 'evidence').is_dir(), 'closed file inventory mismatch')
    value = dict(contract=SUPPLEMENT_INPUT_CONTRACT)
    for name in _SUPPLEMENT_IDS:
        raw = blobs.get(name + '.json')
        _supplement_require(raw is not None, 'missing curated table')
        value[name] = cvm_reader._json(raw)
        _supplement_require(raw == (_json_text(value[name]) + '\n').encode('utf8'), 'noncanonical curated table')
    index_raw = (_json_text(value) + '\n').encode('utf8')
    _supplement_require(hashlib.sha256(index_raw).hexdigest() == expected_index_sha256,
                        'reconstructed external index pin mismatch')
    mapping = _supplement_evidence_names(value['sources'])
    expected_files = {name + '.json' for name in _SUPPLEMENT_IDS} | {'relations.json', 'quality.json'}
    expected_files.update(relative for entry in mapping.values() for relative in entry.values() if relative is not None)
    _supplement_require(set(blobs) == expected_files and manifest['evidence'] == mapping, 'closed evidence inventory mismatch')
    # The original four lists retain their input paths and IDs. Materialize only
    # authenticated bytes in a private temporary image to reuse R3a unchanged.
    with tempfile.TemporaryDirectory(prefix='issuer-supplement-') as temporary:
        root = Path(temporary)
        evidence_root = root / 'inputs'
        evidence_root.mkdir()
        index = root / 'index.json'
        index.write_bytes(index_raw)
        written = {}
        for source in value['sources']:
            source_id = source['source_id']
            for kind, declared in (('body', source['body_path']),
                    ('projection', source['projection']['path'] if source['projection'] is not None else None)):
                if declared is None:
                    continue
                raw = blobs[mapping[source_id][kind]]
                path = cvm_reader._contained(evidence_root, declared)
                key = str(path).casefold()
                _supplement_require(key not in written or written[key] == raw, 'conflicting reconstructed evidence path')
                if key not in written:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(raw)
                    written[key] = raw
        admitted = _admit_issuer_supplement_index(index, expected_index_sha256, evidence_root)
    derived = _derive_issuer_supplement(admitted, tables)
    quality = _supplement_quality(admitted, derived)
    for name, expected in (('relations', derived), ('quality', quality)):
        _supplement_require(blobs[name + '.json'] == (_json_text(expected) + '\n').encode('utf8'),
                            'derived replay mismatch: ' + name)
    # JSON booleans/floats cannot substitute for integer counts (True == 1 in Python).
    _supplement_require(_json_text(manifest['counts']) == _json_text(quality['counts']), 'manifest count mismatch')
    cvm_reader._pinned(output / 'manifest.json', expected_manifest_sha256, MAX_TABLE_BYTES)
    return admitted, derived, quality, manifest


def verify_issuer_supplement(output, expected_manifest_sha256, expected_index_sha256, core, expected_core_sha256):
    """Verify external authorities, complete inventory and native semantic replay."""
    _, tables = _load(core, expected_core_sha256)
    return _load_issuer_supplement(output, expected_manifest_sha256, expected_index_sha256,
                                  expected_core_sha256, tables)[3]


def _query_issuer_supplement(admitted, derived, quality, manifest, tables, company, reference, perspective):
    entities = {r['entity_id']: r for r in admitted['entities']}
    claims = {r['claim_id']: r for r in admitted['claims']}
    if company is None:
        selected = set(entities)
        seeds = set(claims)
    else:
        selected = {r['entity_id'] for r in admitted['entities'] if r['entity_id'] == company
            or any(i['namespace'] + ':' + i['literal'] == company for i in r['identifiers'])}
        seeds = {r['claim_id'] for r in admitted['claims'] if r['subject_id'] in selected or r['object_id'] in selected}
        # Include explicit dependent composites, without inventing graph edges.
        changed = True
        while changed:
            additions = {r['claim_id'] for r in admitted['claims'] if set(r['support_claim_ids']) & seeds} - seeds
            changed = bool(additions)
            seeds.update(additions)
    closure = _supplement_closure(claims, seeds)
    selected.update(entity for key in closure for entity in (claims[key]['subject_id'], claims[key]['object_id']) if entity is not None)
    # A gap can explicitly introduce support on another endpoint. Include gaps
    # on that endpoint too, until the finite curated dependency closure settles.
    while True:
        previous = (len(closure), len(selected))
        unresolved = [r for r in admitted['unresolved'] if r['candidate_id'] in selected
                      or bool(set(r['support_claim_ids']) & closure)]
        closure |= _supplement_closure(claims, [key for row in unresolved for key in row['support_claim_ids']])
        selected.update(r['candidate_id'] for r in unresolved)
        selected.update(entity for key in closure for entity in (claims[key]['subject_id'], claims[key]['object_id']) if entity is not None)
        if previous == (len(closure), len(selected)):
            break
    relevant = [claims[key] for key in sorted(closure)]
    dated = [r for r in relevant if r['reference'] is not None and (reference is None or r['reference'] == reference)]
    events = [r for r in relevant if r['fact_type'] == 'event']
    undated = [r for r in relevant if r['reference'] is None and r['fact_type'] != 'event']
    associations = [r for r in derived['associations'] if r['association_claim_id'] in closure
        and (reference is None or r['reference'] == reference) and (perspective is None or r['perspective'] == perspective)]
    unknown = [r for r in derived['undated_associations'] if r['association_claim_id'] in closure]
    gaps = [r for r in derived['derived_unresolved'] if r['association_claim_id'] in closure
        and (reference is None or r['reference'] in (None, reference))
        and (perspective is None or r['perspective'] in (None, perspective))]
    # Preserve all support claims even when their own date differs from a filtered point.
    source_ids = {support['source_id'] for r in relevant for support in r['support']}
    source_ids.update(i['source_id'] for key in selected for i in entities[key]['identifiers'])
    native_ids = {r[field] for r in associations for field in ('cadastro_support', 'group_support', 'leader_support') if r[field] is not None}
    native_rows = [r for r in tables['cadastro'] if r['observation_id'] in native_ids]
    native_links = [r for r in tables['vinculos_cadastrais'] if any(
        r['cadastro_support'] == relation['cadastro_support'] and r['perspective'] == relation['perspective']
        and r['entity'] == relation['entity'] for relation in associations)]
    return dict(contract=SUPPLEMENT_CONTRACT, index_sha256=manifest['index_sha256'], core_sha256=manifest['core_sha256'],
        entities=[entities[key] for key in sorted(selected)], claims=dated, events=events, undated_claims=undated,
        support_claims=relevant, instrument_observations=[r for r in relevant
            if r['fact_type'] in ('instrument_program', 'instrument_observation')],
        instruments=[entities[key] for key in sorted(selected) if entities[key]['role'] == 'instrument'],
        associations=associations, undated_associations=unknown, unresolved=unresolved, derived_unresolved=gaps,
        sources=[r for r in admitted['sources'] if r['source_id'] in source_ids],
        evidence={key: manifest['evidence'][key] for key in sorted(source_ids)},
        cadastro=native_rows, vinculos_cadastrais=native_links, quality=quality)


def query_issuer_supplement(output, expected_manifest_sha256, expected_index_sha256, core, expected_core_sha256,
                           *, company=None, reference=None, perspective=None):
    """Exact entity/namespace selection; undated observations never acquire a quarter."""
    _supplement_require(reference is None or reference in REFERENCES, 'invalid reference')
    _supplement_require(perspective is None or perspective in PERSPECTIVES, 'invalid perspective')
    _supplement_require(company is None or (isinstance(company, str) and bool(company)), 'invalid company selector')
    _, tables = _load(core, expected_core_sha256)
    admitted, derived, quality, manifest = _load_issuer_supplement(output, expected_manifest_sha256,
        expected_index_sha256, expected_core_sha256, tables)
    return _query_issuer_supplement(admitted, derived, quality, manifest, tables, company, reference, perspective)

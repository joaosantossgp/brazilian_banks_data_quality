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


def query_historical_issuer_links(output, expected_manifest_sha256, *, reference=None, entity=None, perspective=None):
    """Return JSON-ready observations, sources, states and relevant gaps; no sums."""
    if reference is not None and reference not in REFERENCES:
        raise ValueError('Reference must be one of the 60 native AAAAMM quarters')
    if perspective is not None and perspective not in PERSPECTIVES:
        raise ValueError('Invalid perspective')
    if entity is not None and (not isinstance(entity, str) or not entity):
        raise ValueError('Entity must be a nonempty literal identifier')
    manifest, tables = _load(output, expected_manifest_sha256)
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

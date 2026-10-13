"""Authenticated offline FRE observations; no temporal or legal inference.

Permissive CSV framing only locates byte segments. Every admitted segment is
independently parsed strictly. A diagnostic ordinal is not a native record ID:
malformed quotes may absorb several physical lines, all quarantined together.
"""
import csv
import io
import re
import stat
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath

from bank_quality.cvm_metadata import (
    _contained, _json, _pinned, _plain_path, _sha, _write_json, _cnpj,
)


COMMON = ('CNPJ_Companhia', 'Data_Referencia', 'Versao', 'ID_Documento', 'Nome_Companhia')
HEADERS = {
    'participacao_sociedade': COMMON + tuple('ID_Sociedade Razao_Social CNPJ Tipo_Sociedade Descricao_Atividades Pais_Sede UF_Sede Municipio_Sede Participacao_Emissor Possui_Registro_CVM Codigo_CVM Razao_Aquisicao_Manutencao Data_Valor_Mercado Data_Valor_Contabil Valor_Mercado Valor_Contabil'.split()),
    'posicao_acionaria': COMMON + tuple('ID_Acionista Acionista Tipo_Pessoa_Acionista CPF_CNPJ_Acionista ID_Acionista_Relacionado Acionista_Relacionado Tipo_Pessoa_Acionista_Relacionado CPF_CNPJ_Acionista_Relacionado Quantidade_Acao_Ordinaria_Circulacao Percentual_Acao_Ordinaria_Circulacao Quantidade_Acao_Preferencial_Circulacao Percentual_Acao_Preferencial_Circulacao Quantidade_Total_Acoes_Circulacao Percentual_Total_Acoes_Circulacao Nacionalidade Sigla_UF Residente_Exterior Representante_Legal Tipo_Pessoa_Representante_Legal CPF_CNPJ_Representante_legal Data_Composicao_Capital_Social Data_Ultima_Alteracao Acionista_Controlador Participante_Acordo_Acionistas'.split()),
    'historico_emissor': COMMON + tuple('Data_Constituicao_Emissor Forma_Constituicao_Emissor Sigla_Pais_Constituicao_Emissor Pais_Constituicao_Emissor Prazo_Duracao_Emissor Data_Registro_Emissor Requisicao_Registro_Emissor'.split()),
    'grupo_economico_reestruturacao': COMMON + ('Data_Operacao', 'Descricao_Operacao', 'Evento_Societario'),
}
RELATED = tuple('ID_Acionista_Relacionado Acionista_Relacionado Tipo_Pessoa_Acionista_Relacionado CPF_CNPJ_Acionista_Relacionado'.split())
FIELDS = {
    'participacao_sociedade': HEADERS['participacao_sociedade'][:17],
    'posicao_acionaria': COMMON + tuple('ID_Acionista Acionista Tipo_Pessoa_Acionista CPF_CNPJ_Acionista'.split()) + RELATED + tuple('Data_Composicao_Capital_Social Data_Ultima_Alteracao Acionista_Controlador Participante_Acordo_Acionistas'.split()),
    'historico_emissor': HEADERS['historico_emissor'],
    'grupo_economico_reestruturacao': COMMON + ('Data_Operacao', 'Evento_Societario'),
}
LINEAGE = ('__source_kind', '__source_year', '__source_url', '__source_sha256',
           '__source_manifest_sha256', '__source_retrieved_at_utc', '__source_member',
           '__diagnostic_segment', '__physical_line_start', '__physical_line_end',
           '__raw_segment_sha256')
TABLES = {kind: kind + '.csv' for kind in HEADERS}
YEARS = tuple(str(year) for year in range(2010, 2025))
MAX_BODY_BYTES = 16 * 1024 * 1024
MAX_MEMBER_BYTES = 64 * 1024 * 1024
MAX_ZIP_BYTES = 256 * 1024 * 1024
MAX_FIELD_CHARS = 128 * 1024
OUTPUT_CONTRACT = 'cvm-corporate-metadata-v1'


def _url(year):
    return f'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{year}.zip'


def _sources(index_path, expected):
    index_path = _plain_path(index_path)
    index = _json(_pinned(index_path, expected))
    if (not isinstance(index, dict) or set(index) != {'contract', 'resources'}
            or index['contract'] != 'cvm-corporate-sources-v1'
            or not isinstance(index['resources'], list) or len(index['resources']) != 15):
        raise ValueError('Invalid closed FRE index')
    seen = set()
    for entry in index['resources']:
        if (not isinstance(entry, dict)
                or set(entry) != {'kind', 'year', 'url', 'manifest', 'manifest_sha256'}
                or entry['kind'] != 'fre' or entry['year'] not in YEARS
                or entry['year'] in seen or entry['url'] != _url(entry['year'])):
            raise ValueError('Invalid FRE resource or URL')
        seen.add(entry['year'])
    for entry in sorted(index['resources'], key=lambda x: x['year']):
        path = _contained(index_path.parent, entry['manifest'])
        manifest = _json(_pinned(path, entry['manifest_sha256']))
        if (not isinstance(manifest, dict) or manifest.get('method') != 'GET'
                or type(manifest.get('http_status')) is not int or manifest['http_status'] != 200
                or manifest.get('outcome') != 'ok' or manifest.get('source_complete') is not True
                or manifest.get('truncated') is not False or manifest.get('url') != entry['url']
                or manifest.get('final_url') != entry['url']):
            raise ValueError('Source is not a complete official GET')
        recovered = manifest.get('retrieved_at_utc')
        if not isinstance(recovered, str):
            raise ValueError('UTC recovery timestamp required')
        if datetime.fromisoformat(recovered).utcoffset() != timedelta(0):
            raise ValueError('UTC recovery timestamp required')
        response_path = _contained(path.parent, manifest.get('response_metadata_path'))
        response = _json(_pinned(response_path, manifest.get('response_metadata_sha256')))
        if (not isinstance(response, dict) or any(response.get(k) != manifest[k]
                for k in ('url', 'final_url', 'method', 'http_status'))):
            raise ValueError('Response differs from source receipt')
        raw = _pinned(_contained(path.parent, manifest.get('body_path')),
                      manifest.get('sha256'), MAX_BODY_BYTES)
        if (type(manifest.get('bytes')) is not int or manifest['bytes'] != len(raw)
                or (manifest.get('content_length') is not None
                    and (type(manifest['content_length']) is not int
                         or manifest['content_length'] != len(raw)))):
            raise ValueError('Source byte count mismatch')
        yield entry, manifest, raw


def _members(raw, year):
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)) or sum(i.file_size for i in infos) > MAX_ZIP_BYTES:
                raise ValueError('Duplicate ZIP member or expanded budget exceeded')
            for info in infos:
                name = info.filename
                if (info.file_size > MAX_MEMBER_BYTES or info.flag_bits & 1
                        or stat.S_ISLNK(info.external_attr >> 16)
                        or PurePosixPath(name).is_absolute() or ':' in name or '\\' in name
                        or '..' in PurePosixPath(name).parts):
                    raise ValueError('Unsafe ZIP member')
            if archive.testzip() is not None:
                raise ValueError('ZIP CRC mismatch')
            return [(kind, f'fre_cia_aberta_{kind}_{year}.csv',
                     archive.read(f'fre_cia_aberta_{kind}_{year}.csv')
                     if f'fre_cia_aberta_{kind}_{year}.csv' in names else None)
                    for kind in HEADERS]
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
        raise ValueError('Invalid FRE ZIP') from error


class _PhysicalLines:
    """Retain precisely the bytes consumed by csv.reader, including CRLF."""
    def __init__(self, raw):
        self.stream = io.StringIO(raw.decode('latin1'), newline='')
        self.line = 0
        self.consumed = []

    def __iter__(self):
        return self

    def __next__(self):
        text = next(self.stream)
        self.line += 1
        self.consumed.append(text.encode('latin1'))
        return text


def _segments(raw, kind):
    lines = _PhysicalLines(raw)
    reader = csv.reader(lines, delimiter=';', quotechar='"', doublequote=True, strict=False)
    try:
        header = next(reader, None)
        header_raw = b''.join(lines.consumed)
        strict_header = list(csv.reader(io.StringIO(header_raw.decode('latin1'), newline=''),
                                       delimiter=';', strict=True))
        if header != list(HEADERS[kind]) or strict_header != [header]:
            raise ValueError('Closed FRE header mismatch')
        ordinal = 0
        while True:
            lines.consumed = []
            start = lines.line + 1
            try:
                next(reader)
            except StopIteration:
                break
            ordinal += 1
            yield ordinal, start, lines.line, b''.join(lines.consumed)
    except csv.Error as error:
        # No permissive recovery after framing failure: population is unknown.
        raise ValueError('FRE segment framing failed') from error


def _strict_record(raw, kind):
    try:
        rows = list(csv.reader(io.StringIO(raw.decode('latin1'), newline=''),
                               delimiter=';', quotechar='"', doublequote=True, strict=True))
    except csv.Error:
        return None, 'invalid_csv'
    if len(rows) != 1 or len(rows[0]) != len(HEADERS[kind]):
        return None, 'width_mismatch'
    values = rows[0]
    if any(len(value) > MAX_FIELD_CHARS for value in values):
        return None, 'field_budget'
    if any(0x80 <= value <= 0x9f for value in raw):
        return None, 'unreviewed_c1_encoding'
    row = dict(zip(HEADERS[kind], values))
    if (_cnpj(row['CNPJ_Companhia']) is None
            or not row['Data_Referencia']
            or any(re.fullmatch(r'[0-9]+', row[key]) is None for key in ('Versao', 'ID_Documento'))):
        return None, 'invalid_document_key'
    if kind == 'participacao_sociedade' and not row['ID_Sociedade'].strip():
        return None, 'invalid_society_key'
    for key, value in row.items():
        if key.startswith('Data_') and value:
            try:
                if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) is None:
                    return None, 'invalid_date'
                date.fromisoformat(value)
            except ValueError:
                return None, 'invalid_date'
    return row, None


def build_corporate_metadata(index_path: str | Path, expected_index_sha256: str,
                             output: str | Path) -> dict:
    """Project 15 authenticated FRE years into a new, closed textual package."""
    output = _plain_path(output)
    if output.exists():
        raise ValueError('Output destination must be new')
    records = {kind: [] for kind in HEADERS}
    sources = []
    quality = {'contract': 'cvm-corporate-quality-v1', 'members': [], 'quarantine': [],
               'structurally_absent': [], 'date_alerts': [],
               'ordinal_semantics': 'diagnostic segment, not native row identity; malformed quotes may absorb physical lines',
               'relationship_acceptance': False}
    for entry, manifest, raw in _sources(index_path, expected_index_sha256):
        source = dict(kind='fre', year=entry['year'], url=entry['url'],
                      body_sha256=manifest['sha256'], manifest_sha256=entry['manifest_sha256'],
                      retrieved_at_utc=manifest['retrieved_at_utc'], bytes=len(raw))
        sources.append(source)
        for kind, member, body in _members(raw, entry['year']):
            pointer = dict(year=entry['year'], member=member, source_sha256=manifest['sha256'],
                           source_manifest_sha256=entry['manifest_sha256'], url=entry['url'],
                           retrieved_at_utc=manifest['retrieved_at_utc'])
            if body is None:
                quality['structurally_absent'].append(pointer)
                continue
            counts = dict(pointer, diagnostic_segments=0, admitted=0, admitted_pj=0,
                          excluded_pf=0, excluded_unknown_person_type=0, quarantined_segments=0)
            quality['members'].append(counts)
            for ordinal, start, end, segment in _segments(body, kind):
                counts['diagnostic_segments'] += 1
                locator = dict(pointer, diagnostic_segment=ordinal, physical_line_start=start,
                               physical_line_end=end, raw_segment_sha256=_sha(segment))
                row, problem = _strict_record(segment, kind)
                if problem:
                    counts['quarantined_segments'] += 1
                    quality['quarantine'].append(dict(locator, reason=problem))
                    continue
                if kind == 'posicao_acionaria':
                    person = row['Tipo_Pessoa_Acionista']
                    if person != 'PJ':
                        counts['excluded_pf' if person == 'PF' else 'excluded_unknown_person_type'] += 1
                        continue
                    if not row['ID_Acionista'].strip() or _cnpj(row['CPF_CNPJ_Acionista']) is None:
                        counts['quarantined_segments'] += 1
                        quality['quarantine'].append(dict(locator, reason='invalid_pj_key'))
                        continue
                    if row['Tipo_Pessoa_Acionista_Relacionado'] != 'PJ':
                        for field in RELATED:
                            row[field] = ''
                    elif _cnpj(row['CPF_CNPJ_Acionista_Relacionado']) is None:
                        counts['quarantined_segments'] += 1
                        quality['quarantine'].append(dict(locator, reason='invalid_related_pj_key'))
                        continue
                    counts['admitted_pj'] += 1
                for field, value in row.items():
                    if field.startswith('Data_') and value and value > '2024-12-31':
                        quality['date_alerts'].append(dict(locator, field=field, value=value,
                            status='after_historical_window_not_current_fact'))
                projected = {field: row[field] for field in FIELDS[kind]}
                projected.update(dict(zip(LINEAGE, ['fre', entry['year'], entry['url'],
                    manifest['sha256'], entry['manifest_sha256'], manifest['retrieved_at_utc'],
                    member, str(ordinal), str(start), str(end), _sha(segment)])))
                records[kind].append(projected)
                counts['admitted'] += 1
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    for kind, name in TABLES.items():
        fields = [*FIELDS[kind], *LINEAGE]
        with (output / name).open('x', encoding='utf8', newline='') as stream:
            writer = csv.DictWriter(stream, fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(records[kind])
        raw = (output / name).read_bytes()
        files[name] = dict(sha256=_sha(raw), bytes=len(raw), headers=fields, rows=len(records[kind]))
    files['quality.json'] = _write_json(output / 'quality.json', quality)
    manifest = dict(contract=OUTPUT_CONTRACT, source_index_sha256=expected_index_sha256,
                    sources=sources, files=files, counts={TABLES[k]: len(v) for k, v in records.items()},
                    source_headers={k: list(v) for k, v in HEADERS.items()}, lineage_fields=list(LINEAGE),
                    coverage_years=list(YEARS), output_encoding='utf-8', relationship_acceptance=False,
                    profile='latin1;semicolon;doublequote;permissive-framing-only;strict-segment-admission',
                    limits=dict(body_bytes=MAX_BODY_BYTES, member_bytes=MAX_MEMBER_BYTES,
                                zip_expanded_bytes=MAX_ZIP_BYTES, field_characters=MAX_FIELD_CHARS))
    receipt = _write_json(output / 'manifest.json', manifest)
    return dict(manifest=str(output / 'manifest.json'), manifest_sha256=receipt['sha256'], counts=manifest['counts'])


def verify_corporate_metadata(output: str | Path, expected_manifest_sha256: str) -> dict:
    """Authenticate the external manifest pin, exact inventory, schemas and counts."""
    output = _plain_path(output)
    manifest = _json(_pinned(output / 'manifest.json', expected_manifest_sha256, 16 * 1024 * 1024))
    expected = {*TABLES.values(), 'quality.json'}
    if (not isinstance(manifest, dict) or manifest.get('contract') != OUTPUT_CONTRACT
            or not isinstance(manifest.get('files'), dict) or set(manifest['files']) != expected
            or set(manifest.get('counts', {})) != set(TABLES.values())
            or set(p.name for p in output.iterdir()) != expected | {'manifest.json'}
            or manifest.get('coverage_years') != list(YEARS)
            or manifest.get('source_headers') != {k: list(v) for k, v in HEADERS.items()}):
        raise ValueError('Invalid closed corporate manifest or inventory')
    sources = manifest.get('sources')
    if (not isinstance(sources, list) or len(sources) != len(YEARS)
            or [s.get('year') for s in sources if isinstance(s, dict)] != list(YEARS)
            or manifest.get('lineage_fields') != list(LINEAGE)
            or manifest.get('relationship_acceptance') is not False
            or not isinstance(manifest.get('source_index_sha256'), str)
            or re.fullmatch(r'[0-9a-f]{64}', manifest['source_index_sha256']) is None):
        raise ValueError('Invalid corporate source inventory')
    by_year = {}
    for source in sources:
        if (set(source) != {'kind', 'year', 'url', 'body_sha256', 'manifest_sha256',
                            'retrieved_at_utc', 'bytes'}
                or source['kind'] != 'fre' or source['url'] != _url(source['year'])
                or type(source['bytes']) is not int or not 0 < source['bytes'] <= MAX_BODY_BYTES
                or any(not isinstance(source[key], str)
                       or re.fullmatch(r'[0-9a-f]{64}', source[key]) is None
                       for key in ('body_sha256', 'manifest_sha256'))
                or not isinstance(source['retrieved_at_utc'], str)
                or datetime.fromisoformat(source['retrieved_at_utc']).utcoffset() != timedelta(0)):
            raise ValueError('Invalid corporate source descriptor')
        by_year[source['year']] = source
    for kind, name in TABLES.items():
        item = manifest['files'][name]
        raw = _pinned(_contained(output, name), item.get('sha256'), 256 * 1024 * 1024)
        fields = [*FIELDS[kind], *LINEAGE]
        try:
            reader = csv.reader(io.StringIO(raw.decode('utf8'), newline=''), strict=True)
            if next(reader, None) != fields or item.get('headers') != fields:
                raise ValueError('Output header mismatch')
            count = 0
            for count, row in enumerate(reader, 1):
                if len(row) != len(fields):
                    raise ValueError('Output width mismatch')
                record = dict(zip(fields, row))
                source = by_year.get(record['__source_year'])
                if (source is None or record['__source_kind'] != 'fre'
                        or record['__source_member'] != f'fre_cia_aberta_{kind}_{source["year"]}.csv'
                        or any(record[column] != source[key] for column, key in (
                            ('__source_url', 'url'), ('__source_sha256', 'body_sha256'),
                            ('__source_manifest_sha256', 'manifest_sha256'),
                            ('__source_retrieved_at_utc', 'retrieved_at_utc')))):
                    raise ValueError('Output lineage differs from source inventory')
        except (UnicodeError, csv.Error) as error:
            raise ValueError('Invalid output CSV') from error
        if (len(raw) != item.get('bytes') or count != item.get('rows')
                or count != manifest['counts'][name]):
            raise ValueError('Output length or count mismatch')
    item = manifest['files']['quality.json']
    raw = _pinned(output / 'quality.json', item.get('sha256'), 256 * 1024 * 1024)
    quality = _json(raw)
    if len(raw) != item.get('bytes') or quality.get('contract') != 'cvm-corporate-quality-v1':
        raise ValueError('Invalid corporate quality evidence')
    for kind, name in TABLES.items():
        members = [m for m in quality['members'] if m['member'].startswith('fre_cia_aberta_' + kind + '_')]
        if sum(m['admitted'] for m in members) != manifest['counts'][name]:
            raise ValueError('Quality count mismatch')
        for m in members:
            if m['diagnostic_segments'] != sum(m[k] for k in (
                    'admitted', 'excluded_pf', 'excluded_unknown_person_type', 'quarantined_segments')):
                raise ValueError('Segment accounting mismatch')
    return manifest

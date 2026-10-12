"""Offline, literal CVM metadata snapshots; no identity or eligibility inference."""

import csv
import hashlib
import io
import json
import re
import stat
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath, PureWindowsPath


HEADERS = {'cad': ['CNPJ_CIA',
         'DENOM_SOCIAL',
         'DENOM_COMERC',
         'DT_REG',
         'DT_CONST',
         'DT_CANCEL',
         'MOTIVO_CANCEL',
         'SIT',
         'DT_INI_SIT',
         'CD_CVM',
         'SETOR_ATIV',
         'TP_MERC',
         'CATEG_REG',
         'DT_INI_CATEG',
         'SIT_EMISSOR',
         'DT_INI_SIT_EMISSOR',
         'CONTROLE_ACIONARIO',
         'TP_ENDER',
         'LOGRADOURO',
         'COMPL',
         'BAIRRO',
         'MUN',
         'UF',
         'PAIS',
         'CEP',
         'DDD_TEL',
         'TEL',
         'DDD_FAX',
         'FAX',
         'EMAIL',
         'TP_RESP',
         'RESP',
         'DT_INI_RESP',
         'LOGRADOURO_RESP',
         'COMPL_RESP',
         'BAIRRO_RESP',
         'MUN_RESP',
         'UF_RESP',
         'PAIS_RESP',
         'CEP_RESP',
         'DDD_TEL_RESP',
         'TEL_RESP',
         'DDD_FAX_RESP',
         'FAX_RESP',
         'EMAIL_RESP',
         'CNPJ_AUDITOR',
         'AUDITOR'],
 'index': ['CNPJ_CIA',
           'DT_REFER',
           'VERSAO',
           'DENOM_CIA',
           'CD_CVM',
           'CATEG_DOC',
           'ID_DOC',
           'DT_RECEB',
           'LINK_DOC'],
 'geral': ['CNPJ_Companhia',
           'Data_Referencia',
           'Versao',
           'ID_Documento',
           'Nome_Empresarial',
           'Data_Nome_Empresarial',
           'Nome_Empresarial_Anterior',
           'Data_Constituicao',
           'Codigo_CVM',
           'Data_Registro_CVM',
           'Categoria_Registro_CVM',
           'Data_Categoria_Registro_CVM',
           'Situacao_Registro_CVM',
           'Data_Situacao_Registro_CVM',
           'Pais_Origem',
           'Pais_Custodia_Valores_Mobiliarios',
           'Setor_Atividade',
           'Descricao_Atividade',
           'Situacao_Emissor',
           'Data_Situacao_Emissor',
           'Especie_Controle_Acionario',
           'Data_Especie_Controle_Acionario',
           'Dia_Encerramento_Exercicio_Social',
           'Mes_Encerramento_Exercicio_Social',
           'Data_Alteracao_Exercicio_Social',
           'Pagina_Web'],
 'valmob': ['CNPJ_Companhia',
            'Data_Referencia',
            'Versao',
            'ID_Documento',
            'Nome_Empresarial',
            'Valor_Mobiliario',
            'Sigla_Classe_Acao_Preferencial',
            'Classe_Acao_Preferencial',
            'Codigo_Negociacao',
            'Composicao_BDR_Unit',
            'Mercado',
            'Sigla_Entidade_Administradora',
            'Entidade_Administradora',
            'Data_Inicio_Negociacao',
            'Data_Fim_Negociacao',
            'Segmento',
            'Data_Inicio_Listagem',
            'Data_Fim_Listagem']}

CAD_FIELDS = (
    'CD_CVM', 'CNPJ_CIA', 'DENOM_SOCIAL', 'DENOM_COMERC', 'DT_REG',
    'DT_CONST', 'DT_CANCEL', 'MOTIVO_CANCEL', 'SIT', 'DT_INI_SIT',
    'SIT_EMISSOR', 'DT_INI_SIT_EMISSOR', 'CATEG_REG', 'DT_INI_CATEG',
    'SETOR_ATIV', 'CONTROLE_ACIONARIO', 'TP_MERC', 'PAIS',
)
LINEAGE = ('__source_kind', '__source_year', '__source_url', '__source_sha256',
           '__source_manifest_sha256', '__source_member', '__source_row')
TABLES = {'cad': 'cadastro_atual.csv', 'index': 'documentos_fca.csv',
          'geral': 'geral_fca.csv', 'valmob': 'valores_mobiliarios_fca.csv'}
SOURCE_CONTRACT = 'cvm-identity-sources-v1'
OUTPUT_CONTRACT = 'cvm-identity-metadata-v1'
BASE_URL = 'https://dados.cvm.gov.br/dados/CIA_ABERTA/'
MAX_BODY_BYTES = 8 * 1024 * 1024
MAX_MEMBER_BYTES = 64 * 1024 * 1024
MAX_ZIP_EXPANDED_BYTES = 64 * 1024 * 1024
MAX_EXPANDED_BYTES = 256 * 1024 * 1024
MAX_FIELD_CHARS = 128 * 1024


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def _json(raw):
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError('Invalid UTF-8 JSON') from error


def _plain_path(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            attributes = item.lstat()
            if (stat.S_ISLNK(attributes.st_mode)
                    or getattr(attributes, 'st_file_attributes', 0) & 0x400):
                raise ValueError('Symlink or reparse point is forbidden: ' + str(item))
    return path


def _contained(root, relative):
    if (not isinstance(relative, str) or not relative or '\\' in relative
            or ':' in relative or PureWindowsPath(relative).is_absolute()
            or PurePosixPath(relative).is_absolute()
            or '..' in PurePosixPath(relative).parts):
        raise ValueError('Expected contained relative path')
    root = _plain_path(root)
    path = _plain_path(root / relative)
    if not path.is_relative_to(root):
        raise ValueError('Path escapes source root')
    return path


def _pinned(path, expected, limit=2 * 1024 * 1024):
    if not isinstance(expected, str) or re.fullmatch(r'[0-9a-f]{64}', expected) is None:
        raise ValueError('External SHA-256 required')
    path = _plain_path(path)
    if not path.is_file() or path.stat().st_size > limit:
        raise ValueError('Missing file or byte budget exceeded: ' + str(path))
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit or _sha(raw) != expected:
        raise ValueError('Pinned file hash or byte budget mismatch: ' + str(path))
    return raw


def _url(kind, year):
    if kind == 'cad' and year is None:
        return BASE_URL + 'CAD/DADOS/cad_cia_aberta.csv'
    if kind == 'fca' and isinstance(year, str) and year in {str(y) for y in range(2010, 2025)}:
        return BASE_URL + f'DOC/FCA/DADOS/fca_cia_aberta_{year}.zip'
    raise ValueError('Unsupported source family or year')


def _sources(index_path, expected):
    index_path = _plain_path(index_path)
    index = _json(_pinned(index_path, expected))
    if (not isinstance(index, dict) or set(index) != {'contract', 'resources'}
            or index['contract'] != SOURCE_CONTRACT
            or not isinstance(index['resources'], list)
            or not 1 <= len(index['resources']) <= 16):
        raise ValueError('Invalid source-index contract')
    seen = set()
    for entry in index['resources']:
        if not isinstance(entry, dict) or set(entry) != {'kind', 'year', 'url', 'manifest', 'manifest_sha256'}:
            raise ValueError('Invalid resource descriptor')
        url = _url(entry['kind'], entry['year'])
        key = (entry['kind'], entry['year'])
        if entry['url'] != url or key in seen:
            raise ValueError('Unexpected URL or duplicate resource')
        seen.add(key)
    if ('cad', None) not in seen:
        raise ValueError('Exactly one CAD snapshot required')
    for entry in sorted(index['resources'], key=lambda e: (e['kind'], e['year'] or '')):
        manifest_path = _contained(index_path.parent, entry['manifest'])
        manifest = _json(_pinned(manifest_path, entry['manifest_sha256']))
        if (not isinstance(manifest, dict)
                or manifest.get('method') != 'GET'
                or type(manifest.get('http_status')) is not int
                or manifest['http_status'] != 200
                or manifest.get('outcome') != 'ok'
                or manifest.get('source_complete') is not True
                or manifest.get('truncated') is not False
                or manifest.get('url') != entry['url']
                or manifest.get('final_url') != entry['url']):
            raise ValueError('Source is not a complete official GET')
        body_path = _contained(manifest_path.parent, manifest.get('body_path'))
        raw = _pinned(body_path, manifest.get('sha256'), MAX_BODY_BYTES)
        if type(manifest.get('bytes')) is not int or manifest['bytes'] != len(raw):
            raise ValueError('Archived byte count mismatch')
        if (manifest.get('content_length') is not None
                and (type(manifest['content_length']) is not int
                     or manifest['content_length'] != len(raw))):
            raise ValueError('Content-Length differs from archived body')
        recovered = manifest.get('retrieved_at_utc')
        if not isinstance(recovered, str):
            raise ValueError('UTC recovery timestamp required')
        recovered_time = datetime.fromisoformat(recovered)
        if recovered_time.utcoffset() != timedelta(0):
            raise ValueError('UTC recovery timestamp required')
        response_path = _contained(manifest_path.parent, manifest.get('response_metadata_path'))
        response = _json(_pinned(response_path, manifest.get('response_metadata_sha256')))
        if (not isinstance(response, dict)
                or any(response.get(key) != manifest[key]
                       for key in ('url', 'final_url', 'method', 'http_status'))):
            raise ValueError('Response metadata differs from manifest')
        yield entry, manifest, raw


def _csv_rows(raw, kind):
    if any(0x80 <= value <= 0x9f for value in raw):
        raise ValueError('C1 bytes require encoding profile review')
    try:
        reader = csv.reader(io.StringIO(raw.decode('latin-1'), newline=''),
                            delimiter=';', quotechar='"', strict=True)
        header = next(reader, None)
        if header != HEADERS[kind]:
            raise ValueError('Closed CVM header mismatch: ' + kind)
        for ordinal, values in enumerate(reader, 1):
            if len(values) != len(header):
                raise ValueError('CSV row width mismatch')
            record = dict(zip(header, values))
            for field, value in record.items():
                if len(value) > MAX_FIELD_CHARS:
                    raise ValueError('CSV field exceeds closed 128 KiB profile')
                if value and (field.startswith('Data_') or field.startswith('DT_')):
                    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) is None:
                        raise ValueError('Invalid literal date: ' + field)
                    date.fromisoformat(value)
            yield ordinal, record
    except (csv.Error, UnicodeError) as error:
        raise ValueError('Invalid strict CVM CSV') from error


def _members(raw, year, remaining_expanded_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            if len(names) != len(set(names)):
                raise ValueError('Duplicate ZIP member')
            expanded_bytes = sum(item.file_size for item in infos)
            if (expanded_bytes > MAX_ZIP_EXPANDED_BYTES
                    or expanded_bytes > remaining_expanded_bytes):
                raise ValueError('ZIP expanded budget exceeded')
            for item in infos:
                name = item.filename
                if (item.file_size > MAX_MEMBER_BYTES or item.flag_bits & 1
                        or stat.S_ISLNK(item.external_attr >> 16)
                        or PurePosixPath(name).is_absolute() or ':' in name
                        or '\\' in name or '..' in PurePosixPath(name).parts):
                    raise ValueError('Unsafe ZIP member or member budget exceeded')
            expected = [(kind, f'fca_cia_aberta{suffix}_{year}.csv') for kind, suffix in
                        [('index', ''), ('geral', '_geral'), ('valmob', '_valor_mobiliario')]]
            if any(name not in names for _, name in expected):
                raise ValueError('Expected FCA member missing')
            if archive.testzip() is not None:
                raise ValueError('ZIP CRC failure')
            return ([(kind, name, archive.read(name)) for kind, name in expected], expanded_bytes)
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
        raise ValueError('Invalid or unsupported FCA ZIP') from error


def _cnpj(raw):
    normalized = re.sub(r'[./-]', '', raw)
    return normalized if re.fullmatch(r'[0-9]{14}', normalized) else None


def _doc_key(row, kind):
    fields = ('CNPJ_CIA', 'DT_REFER', 'VERSAO', 'ID_DOC') if kind == 'index' else (
        'CNPJ_Companhia', 'Data_Referencia', 'Versao', 'ID_Documento')
    return (_cnpj(row[fields[0]]), *(row[field] for field in fields[1:]))


def _missing_key_components(key):
    names = ('normalized_cnpj', 'reference', 'version', 'document_id')
    return [name for name, value in zip(names, key) if value is None or not value.strip()]


def _quality(records):
    tables = {}
    for kind, rows in records.items():
        fields = CAD_FIELDS if kind == 'cad' else HEADERS[kind]
        literals = Counter(tuple(row[key] for key in fields) for row in rows)
        tables[TABLES[kind]] = {
            'rows': len(rows), 'distinct_literal_rows': len(literals),
            'duplicate_literal_rows': sum(count - 1 for count in literals.values()),
        }
    cad = records['cad']
    tables[TABLES['cad']]['distinct_cnpjs'] = len({row['CNPJ_CIA'] for row in cad})
    tables[TABLES['cad']]['distinct_cnpj_cvm_pairs'] = len({(row['CNPJ_CIA'], row['CD_CVM']) for row in cad})
    tables[TABLES['cad']]['distinct_cnpj_cvm_market'] = len({(row['CNPJ_CIA'], row['CD_CVM'], row['TP_MERC']) for row in cad})
    exact = defaultdict(list)
    document = defaultdict(list)
    incomplete_index_keys = []
    for row in records['index']:
        key = _doc_key(row, 'index')
        year = row['__source_year']
        missing = _missing_key_components(key)
        if missing:
            incomplete_index_keys.append({
                'year': year, 'source_sha256': row['__source_sha256'],
                'member': row['__source_member'], 'source_row': row['__source_row'],
                'status': 'incomplete_key', 'quarantined': True,
                'missing_key_components': missing})
            continue
        exact[(year, *key)].append(row)
        document[(year, *key[1:])].append(row)
    ledger = []
    date_conflicts = []
    for kind in ('geral', 'valmob'):
        for row in records[kind]:
            key = _doc_key(row, kind)
            year = row['__source_year']
            missing = _missing_key_components(key)
            matches = exact[(year, *key)] if not missing else []
            other = document[(year, *key[1:])] if not missing else []
            if missing:
                status = 'incomplete_key'
            elif len(matches) > 1:
                status = 'ambiguous'
            elif len(matches) == 1:
                # Diverging declarations of the same document remain a conflict.
                status = ('cnpj_conflict' if any(_doc_key(item, 'index')[0] != key[0]
                                                for item in other) else 'matched')
            elif key[0] is not None and other:
                status = 'cnpj_conflict'
            else:
                status = 'missing_index'
            reversed_fields = []
            if kind == 'valmob':
                for field in ('Listagem', 'Negociacao'):
                    start, end = row['Data_Inicio_' + field], row['Data_Fim_' + field]
                    if start and end and end < start:
                        reversed_fields.append(field)
                        date_conflicts.append({
                            'table': TABLES[kind], 'year': year,
                            'source_sha256': row['__source_sha256'],
                            'member': row['__source_member'], 'source_row': row['__source_row'],
                            'interval': field, 'start': start, 'end': end,
                            'status': 'end_before_start', 'quarantined': True})
            ledger.append({
                'table': TABLES[kind], 'year': year,
                'source_sha256': row['__source_sha256'],
                'member': row['__source_member'], 'source_row': row['__source_row'],
                'cnpj': key[0], 'reference': key[1], 'version': key[2], 'document_id': key[3],
                'status': status, 'quarantined': status != 'matched' or bool(reversed_fields),
                'missing_key_components': missing,
                'reversed_intervals': reversed_fields,
                'matching_index_rows': [item['__source_row'] for item in matches],
                'document_index_cnpjs': sorted({item['CNPJ_CIA'] for item in other}),
            })
    return {'contract': 'cvm-identity-quality-v1', 'tables': tables,
            'document_link_counts': dict(sorted(Counter(item['status'] for item in ledger).items())),
            'document_links': ledger, 'date_conflicts': date_conflicts,
            'incomplete_index_keys': incomplete_index_keys,
            'limits': ['Literal source observations only; no legal identity or eligibility accepted.',
                       'Quarantined rows cannot be used for relational joins.',
                       'Document reference is not a closed validity interval.',
                       'Current cadastro does not prove historical status.']}


def _write_json(path, content):
    raw = (json.dumps(content, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as stream:
        stream.write(raw)
    return {'sha256': _sha(raw), 'bytes': len(raw)}


def build_cvm_metadata(index_path: str | Path, expected_index_sha256: str,
                       output: str | Path) -> dict:
    """Build a new literal metadata snapshot from authenticated offline sources."""
    output = _plain_path(output)
    if output.exists():
        raise ValueError('Output destination must be new')
    records = {kind: [] for kind in TABLES}
    source_inventory = []
    expanded_bytes = 0
    for entry, manifest, raw in _sources(index_path, expected_index_sha256):
        source_inventory.append({'kind': entry['kind'], 'year': entry['year'],
                                 'url': entry['url'], 'manifest_sha256': entry['manifest_sha256'],
                                 'body_sha256': manifest['sha256'], 'bytes': len(raw),
                                 'retrieved_at_utc': manifest['retrieved_at_utc']})
        if entry['kind'] == 'cad':
            expanded_bytes += len(raw)
            payloads = [('cad', 'cad_cia_aberta.csv', raw)]
            if expanded_bytes > MAX_EXPANDED_BYTES:
                raise ValueError('Aggregate expanded budget exceeded')
        else:
            payloads, source_expanded = _members(raw, entry['year'],
                                                 MAX_EXPANDED_BYTES - expanded_bytes)
            expanded_bytes += source_expanded
        for kind, member, body in payloads:
            for ordinal, row in _csv_rows(body, kind):
                fields = CAD_FIELDS if kind == 'cad' else HEADERS[kind]
                projected = {field: row[field] for field in fields}
                projected.update(dict(zip(LINEAGE, [entry['kind'], entry['year'] or '',
                    entry['url'], manifest['sha256'], entry['manifest_sha256'], member, str(ordinal)])))
                records[kind].append(projected)
    quality = _quality(records)
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    counts = {}
    for kind, name in TABLES.items():
        fields = [*(CAD_FIELDS if kind == 'cad' else HEADERS[kind]), *LINEAGE]
        with (output / name).open('x', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(records[kind])
        raw = (output / name).read_bytes()
        files[name] = {'sha256': _sha(raw), 'bytes': len(raw), 'headers': fields,
                       'rows': len(records[kind])}
        counts[name] = len(records[kind])
    files['quality.json'] = _write_json(output / 'quality.json', quality)
    manifest = {'contract': OUTPUT_CONTRACT, 'source_index_sha256': expected_index_sha256,
                'sources': source_inventory, 'files': files, 'counts': counts,
                'profile': 'latin-1-no-C1;semicolon;strict-double-quote',
                'limits': {'body_bytes': MAX_BODY_BYTES, 'zip_expanded_bytes': MAX_ZIP_EXPANDED_BYTES,
                           'aggregate_expanded_bytes': MAX_EXPANDED_BYTES,
                           'field_characters': MAX_FIELD_CHARS},
                'output_encoding': 'utf-8', 'lineage_fields': list(LINEAGE),
                'relationship_acceptance': False, 'eligibility_acceptance': False,
                'coverage': {'cad': 1, 'fca_years': [s['year'] for s in source_inventory if s['kind'] == 'fca']}}
    receipt = _write_json(output / 'manifest.json', manifest)
    return {'manifest': str(output / 'manifest.json'), 'manifest_sha256': receipt['sha256'],
            'counts': counts}


def verify_cvm_metadata(output: str | Path, expected_manifest_sha256: str) -> dict:
    """Authenticate a closed output inventory and verify textual table counts/schema."""
    output = _plain_path(output)
    manifest = _json(_pinned(output / 'manifest.json', expected_manifest_sha256))
    expected_files = {*TABLES.values(), 'quality.json'}
    if (not isinstance(manifest, dict) or manifest.get('contract') != OUTPUT_CONTRACT
            or not isinstance(manifest.get('files'), dict)
            or set(manifest['files']) != expected_files
            or set(manifest.get('counts', {})) != set(TABLES.values())):
        raise ValueError('Invalid CVM metadata manifest')
    for kind, name in TABLES.items():
        item = manifest['files'][name]
        raw = _pinned(_contained(output, name), item.get('sha256'), 256 * 1024 * 1024)
        fields = [*(CAD_FIELDS if kind == 'cad' else HEADERS[kind]), *LINEAGE]
        try:
            reader = csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True)
            if next(reader, None) != fields or item.get('headers') != fields:
                raise ValueError('Output header mismatch')
            count = 0
            for count, row in enumerate(reader, 1):
                if len(row) != len(fields):
                    raise ValueError('Output CSV width mismatch')
        except (UnicodeError, csv.Error) as error:
            raise ValueError('Invalid output CSV') from error
        if (len(raw) != item.get('bytes') or count != item.get('rows')
                or count != manifest['counts'][name]):
            raise ValueError('Output count/length mismatch')
    item = manifest['files']['quality.json']
    raw = _pinned(output / 'quality.json', item.get('sha256'), 256 * 1024 * 1024)
    quality = _json(raw)
    if len(raw) != item.get('bytes') or quality.get('contract') != 'cvm-identity-quality-v1':
        raise ValueError('Quality evidence mismatch')
    return manifest


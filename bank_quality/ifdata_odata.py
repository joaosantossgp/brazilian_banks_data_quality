"""Import captured IF.data OData pages without changing native IDs or balances.

Each page is authenticated, parsed and converted separately. Saldo is VARCHAR:
its JSON number token is authoritative, including trailing zeros and exponents.
An output becomes readable only after its final manifest has been written.
"""
import csv
from datetime import datetime, timezone
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import tempfile

import duckdb

FIELDS = ('TipoInstituicao', 'CodInst', 'AnoMes', 'NomeRelatorio',
          'NumeroRelatorio', 'Grupo', 'Conta', 'NomeColuna', 'DescricaoColuna', 'Saldo')
PROVENANCE = ('source_file', 'source_sha256', 'source_url', 'source_collected_utc',
              'source_row', 'source_context')
COLUMNS = FIELDS + PROVENANCE
CONTEXT = 'https://was-p.bcnet.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata$metadata#_IfDataValores'
CONTRACT = 'ifdata-odata-parquet-v1'


class _Number(str):
    """Distinguish a JSON number lexeme from a JSON string."""


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def _json(raw, *, numbers=False):
    def invalid(value):
        raise ValueError(f'Invalid JSON number: {value}')
    options = dict(object_pairs_hook=_object, parse_constant=invalid)
    if numbers:
        options.update(parse_int=_Number, parse_float=_Number)
    return json.loads(raw, **options)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _path(root, name):
    if not isinstance(name, str) or not name:
        raise ValueError('Missing file path')
    path = (root / name.replace('\\', '/')).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'File outside package: {name}')
    return path


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError('Invalid manifest count')
    return value


def _selection(values):
    return None if values is None else {str(v) for v in values}


def saldo_decimal(value):
    """Return the exact balance without selecting a shared DECIMAL precision."""
    return None if value is None else Decimal(value)


def _rows(raw, entry, page, reports):
    try:
        body = _json(gzip.decompress(raw), numbers=True)
    except (OSError, EOFError, UnicodeError) as exc:
        raise ValueError('Invalid gzip/UTF-8 page') from exc
    if not isinstance(body, dict) or body.get('@odata.context') != CONTEXT:
        raise ValueError('Unexpected OData context')
    values = body.get('value')
    if not isinstance(values, list) or len(values) != _count(page['registros']):
        raise ValueError('Page record count mismatch')
    # The supplied manifest describes complete pages; never silently omit continuation.
    if '@odata.nextLink' in body:
        raise ValueError('Unexpected unaccounted OData continuation')
    for index, row in enumerate(values, 1):
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise ValueError(f'Unexpected row schema at row {index}')
        for field in FIELDS[1:-1]:
            if row[field] is None and field == 'Grupo':
                continue
            if type(row[field]) is not str:
                raise ValueError(f'Invalid {field} at row {index}')
        if not isinstance(row['TipoInstituicao'], _Number) or not re.fullmatch(r'[1-9][0-9]*', row['TipoInstituicao']):
            raise ValueError('Invalid institution type')
        if row['TipoInstituicao'] != str(entry['tipo']) or row['AnoMes'] != str(entry['periodo']):
            raise ValueError('Period/type mismatch')
        if not re.fullmatch(r'[0-9]+', row['NumeroRelatorio']):
            raise ValueError('Invalid native report number')
        if row['Saldo'] is not None and not isinstance(row['Saldo'], _Number):
            raise ValueError('Saldo must be a JSON number or null')
        if reports is None or row['NumeroRelatorio'] in reports:
            yield [row[k] for k in FIELDS] + [page['arquivo'], page['sha256_gzip'],
                  page['url'], entry['coleta_utc'], str(index), body['@odata.context']]


def import_package(root, output, periods=None, types=None, reports=None):
    """Convert selected captured pages into a new immutable output directory.

    Failure leaves an unaccepted partial directory. Choose a new destination to
    retry. Filters select native OData IDs, never portal report IDs or joins.
    """
    root, output = Path(root).resolve(), Path(output).resolve()
    periods, types, reports = map(_selection, (periods, types, reports))
    source = (root / 'manifesto.json').read_bytes()
    entries = _json(source.decode('utf-8-sig'))
    if not isinstance(entries, list):
        raise ValueError('manifesto.json must contain a list')
    output.mkdir(parents=True, exist_ok=False)
    result = dict(contract=CONTRACT, source_manifest_sha256=_digest(source),
                  imported_utc=datetime.now(timezone.utc).isoformat(), rows=0, files=[],
                  selection=dict(periods=sorted(periods) if periods is not None else None,
                                 types=sorted(types) if types is not None else None,
                                 reports=sorted(reports) if reports is not None else None))
    seen = set()
    with duckdb.connect() as conn:
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError('Invalid manifest entry')
            if periods is not None and str(entry.get('periodo')) not in periods:
                continue
            if types is not None and str(entry.get('tipo')) not in types:
                continue
            if type(entry.get('periodo')) is not int or not re.fullmatch(r'[0-9]{4}(03|06|09|12)', str(entry['periodo'])):
                raise ValueError('Invalid manifest period')
            if type(entry.get('tipo')) is not int or entry['tipo'] not in (1, 2, 3, 4):
                raise ValueError('Invalid manifest type')
            pages = entry.get('paginas')
            if entry.get('status') not in ('ok', 'sem_dados') or not isinstance(pages, list) or not pages:
                raise ValueError('Incomplete manifest entry')
            count = _count(entry.get('registros'))
            if (entry['status'] == 'sem_dados') != (count == 0):
                raise ValueError('Status/count mismatch')
            stamp = entry.get('coleta_utc')
            try:
                parsed_stamp = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
            except (AttributeError, TypeError, ValueError) as exc:
                raise ValueError('Invalid collection timestamp') from exc
            if parsed_stamp.utcoffset() is None or parsed_stamp.utcoffset().total_seconds() != 0:
                raise ValueError('Collection timestamp must be UTC')
            if sum(_count(p.get('registros')) for p in pages) != count:
                raise ValueError('Entry record count mismatch')
            for page in pages:
                path = _path(root, page['arquivo'])
                if path in seen:
                    raise ValueError('Duplicate source page')
                seen.add(path)
                if not isinstance(page.get('url'), str) or not page['url'].startswith('https://'):
                    raise ValueError('Missing source URL')
                raw = path.read_bytes()
                if len(raw) != _count(page['bytes_gzip']) or _digest(raw) != page['sha256_gzip']:
                    raise ValueError(f'Compressed page hash/size mismatch: {path.name}')
                target = output / f'part-{len(result["files"]):05d}.parquet'
                with tempfile.TemporaryDirectory(dir=output) as temporary:
                    csv_path = Path(temporary) / 'rows.csv'
                    written = 0
                    with csv_path.open('w', encoding='utf-8', newline='') as stream:
                        writer = csv.writer(stream, quoting=csv.QUOTE_NOTNULL)
                        writer.writerow(COLUMNS)
                        for row in _rows(raw, entry, page, reports):
                            # Python 3.12 quotes every string, including empty
                            # strings, and writes only None as unquoted empty.
                            writer.writerow(row)
                            written += 1
                    del raw
                    conn.execute('create or replace temp table page as select * from read_csv(?, all_varchar=true, header=true, nullstr=?, allow_quoted_nulls=false)',
                                 [str(csv_path), ''])
                    conn.execute('copy page to ? (format parquet, compression zstd)', [str(target)])
                result['rows'] += written
                result['files'].append(dict(file=target.name, sha256=_digest(target.read_bytes()),
                                            rows=written, source_file=page['arquivo'],
                                            source_sha256=page['sha256_gzip'], source_rows=page['registros'],
                                            period=entry['periodo'], type=entry['tipo']))
    if not result['files']:
        raise ValueError('No source pages matched the selection')
    (output / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def open_dataset(output):
    """Authenticate all output parts and expose their literal fields as ifdata."""
    output = Path(output).resolve()
    manifest = _json((output / 'manifest.json').read_bytes())
    if manifest.get('contract') != CONTRACT or not manifest.get('files'):
        raise ValueError('Not an accepted IF.data OData dataset')
    paths = []
    for part in manifest['files']:
        path = _path(output, part['file'])
        if _digest(path.read_bytes()) != part['sha256']:
            raise ValueError(f'Parquet hash mismatch: {path.name}')
        paths.append(str(path))
    conn = duckdb.connect()
    try:
        conn.from_parquet(paths).create_view('ifdata')
        if conn.execute('select count(*) from ifdata').fetchone()[0] != manifest['rows']:
            raise ValueError('Dataset count mismatch')
        return conn
    except Exception:
        conn.close()
        raise


def query_dataset(output, sql):
    """Execute one SELECT and return JSON-friendly records; no write statements."""
    with open_dataset(output) as conn:
        statements = conn.extract_statements(sql)
        if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
            raise ValueError('Query must be a single SELECT statement')
        cursor = conn.execute(sql)
        names = [column[0] for column in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

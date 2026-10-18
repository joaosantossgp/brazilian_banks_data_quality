"""Native temporal IF.data cadastro and explicitly declared conglomerate links."""
import csv
from datetime import datetime
import json
from pathlib import Path
import re
import tempfile

import duckdb

from bank_quality.ifdata_odata import _json, _Number, _digest, _path, open_dataset

FIELDS = ('CodInst', 'Data', 'NomeInstituicao', 'DataInicioAtividade', 'Tcb',
          'Td', 'Tc', 'SegmentoTb', 'Atividade', 'Uf', 'Municipio', 'Sr',
          'CodConglomeradoFinanceiro', 'CodConglomeradoPrudencial',
          'CnpjInstituicaoLider', 'Situacao')
ORIGIN = ('source_file', 'source_sha256', 'source_url', 'source_collected_utc', 'source_row')
CONTEXT = 'https://was-p.bcnet.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata$metadata#_IfDataCadastro'
CONTRACT = 'ifdata-cadastro-parquet-v1'


def derive_sr_by_links(original,evidence,*,dataset,code,period):
    """Separate analytical SR from its native observation; never impute by time.

    Evidence must come from authenticated, dated declared links. A unique label
    among observed members is sufficient; missing labels remain in the proof.
    This is a derived attribute, not an official classification recovered for
    the target. Financial and prudential units remain separate contributors.
    """
    from copy import deepcopy
    if dataset not in ('financial','capital','individual') or not re.fullmatch(r'\d{4}(03|06|09|12)',period):
        raise ValueError('Invalid SR attribution context')
    result=dict(sr_original=original,sr_vinculo=None,sr_analitico=original,
                method='native' if original not in (None,'') else 'none',
                status='native' if original not in (None,'') else 'unknown',
                labels=[],prudential_parents=[],linked_records=len(evidence),records_with_sr=0,evidence=deepcopy(evidence))
    allowed={'own_prudential_parent'}
    if dataset=='financial':allowed.add('financial_members')
    if dataset=='capital':allowed.add('prudential_members')
    seen=set()
    for row in evidence:
        key=(row.get('link_kind'),row.get('evidence_code'))
        if (any(row.get(k)!=v for k,v in dict(dataset=dataset,code=code,period=period).items())
            or row.get('link_kind') not in allowed or not row.get('evidence_code') or row['evidence_code']==code
            or key in seen or not row.get('source_file') or not row.get('source_row')
            or not re.fullmatch('[0-9a-f]{64}',row.get('source_sha256',''))):
            raise ValueError('Ambiguous, undated or unproven SR evidence')
        seen.add(key)
    labels=sorted({r['evidence_sr'] for r in evidence if r.get('evidence_sr') not in (None,'')})
    parents=sorted({r['evidence_parent'] for r in evidence if r.get('evidence_parent') not in (None,'')})
    result.update(labels=labels,prudential_parents=parents,
                  records_with_sr=sum(r.get('evidence_sr') not in (None,'') for r in evidence))
    if original not in (None,''):return result
    if period<'201703':result['status']='before_regime';return result
    if not labels:return result
    if any(label not in ('S1','S2','S3','S4','S5') for label in labels):result['status']='unrecognized_label';return result
    if len(labels)>1:result['status']='conflict';return result
    if (len(parents)!=1 or any(r.get('evidence_parent') in (None,'') for r in evidence)
        or any(r['link_kind']=='prudential_members' and r['evidence_parent']!=code for r in evidence)):
        result['status']='unproven_perimeter';return result
    result.update(sr_vinculo=labels[0],sr_analitico=labels[0],method='dated_link',status='derived')
    return result


def _unique(conn):
    if conn.execute('select count(*) from cadastro where CodInst is null or CodInst = ? or Data is null', ['']).fetchone()[0]:
        raise ValueError('Missing temporal cadastro key')
    if conn.execute('select count(*) from (select Data, CodInst from cadastro group by all having count(*) > 1)').fetchone()[0]:
        raise ValueError('Duplicate temporal cadastro key; unsafe join')


def import_cadastro(root, output, periods=None):
    """Authenticate captured JSONs and preserve literal fields in a new output."""
    root, output = Path(root).resolve(), Path(output).resolve()
    index_raw = (root / 'indice_periodos.csv').read_bytes()
    summary_raw = (root / 'resumo.json').read_bytes()
    stamp = _json(summary_raw)['download_utc']
    parsed = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError('Collection timestamp must be UTC')
    with (root / 'indice_periodos.csv').open(encoding='utf-8-sig', newline='') as stream:
        entries = list(csv.DictReader(stream, delimiter=';'))
    selected = None if periods is None else {str(p) for p in periods}
    if selected is not None and (not selected or not selected <= {e['periodo'] for e in entries}):
        raise ValueError('Requested periods missing from index')
    output.mkdir(parents=True, exist_ok=False)
    result = dict(contract=CONTRACT, rows=0, files=[], empty_periods=[],
                  index_sha256=_digest(index_raw), summary_sha256=_digest(summary_raw),
                  source_collected_utc=stamp)
    seen = set()
    with duckdb.connect() as conn:
        for entry in entries:
            period = entry['periodo']
            if not re.fullmatch(r'[0-9]{4}(03|06|09|12)', period) or period in seen:
                raise ValueError('Invalid/duplicate index period')
            seen.add(period)
            if selected is not None and period not in selected:
                continue
            if not re.fullmatch(r'[0-9]+', entry['registros']) or entry['paginas'] != '1':
                raise ValueError('Invalid index count or unsupported pagination')
            count = int(entry['registros'])
            if entry['status'] == 'vazio' and count == 0 and not entry['sha256_json']:
                # A declared empty query without a captured body is not a dataset part.
                result['empty_periods'].append(period)
                continue
            if entry['status'] != 'disponivel' or not entry['url'].startswith('https://'):
                raise ValueError('Unavailable or malformed source entry')
            name = f'json/{period}.json'
            raw = (root / name).read_bytes()
            if _digest(raw) != entry['sha256_json']:
                raise ValueError(f'Source hash mismatch: {period}')
            body = _json(raw.decode('utf-8-sig'), numbers=True)
            if not isinstance(body, dict) or body.get('@odata.context') != CONTEXT or '@odata.nextLink' in body:
                raise ValueError('Unexpected context or unaccounted continuation')
            rows = body.get('value')
            if not isinstance(rows, list) or len(rows) != count:
                raise ValueError('Source count mismatch')
            target = output / f'cadastro-{period}.parquet'
            with tempfile.TemporaryDirectory(dir=output) as temporary:
                stage = Path(temporary) / 'rows.csv'
                with stage.open('w', newline='', encoding='utf-8') as stream:
                    writer = csv.writer(stream, quoting=csv.QUOTE_NOTNULL)
                    writer.writerow(FIELDS + ORIGIN)
                    for number, row in enumerate(rows, 1):
                        if not isinstance(row, dict) or set(row) != set(FIELDS) or row['Data'] != period:
                            raise ValueError('Unexpected cadastro schema/reference')
                        for field in FIELDS:
                            value = row[field]
                            if value is None:
                                continue
                            if field in ('DataInicioAtividade', 'Tc'):
                                if not isinstance(value, _Number) or not re.fullmatch(r'-?[0-9]+', value):
                                    raise ValueError(f'Invalid integer field: {field}')
                            elif type(value) is not str:
                                raise ValueError(f'Invalid string field: {field}')
                        writer.writerow([row[f] for f in FIELDS] + [name, entry['sha256_json'], entry['url'], stamp, str(number)])
                conn.execute('create or replace temp table page as select * from read_csv(?, all_varchar=true, header=true, nullstr=?, allow_quoted_nulls=false)', [str(stage), ''])
                conn.execute('copy page to ? (format parquet, compression zstd)', [str(target)])
            result['rows'] += count
            result['files'].append(dict(file=target.name, sha256=_digest(target.read_bytes()),
                                        rows=count, period=period, source_file=name,
                                        source_sha256=entry['sha256_json']))
        if not result['files']:
            raise ValueError('No captured cadastro rows selected')
        conn.from_parquet([str(output / f['file']) for f in result['files']]).create_view('cadastro')
        _unique(conn)
    (output / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def open_cadastro(output):
    """Expose cadastro and declared temporal links, without identity inference."""
    output = Path(output).resolve()
    manifest = _json((output / 'manifest.json').read_bytes())
    if manifest.get('contract') != CONTRACT or not manifest.get('files'):
        raise ValueError('Not an accepted cadastro dataset')
    paths = []
    for part in manifest['files']:
        path = _path(output, part['file'])
        if path in paths or _digest(path.read_bytes()) != part['sha256']:
            raise ValueError('Changed or duplicate cadastro part')
        paths.append(path)
    conn = duckdb.connect()
    try:
        conn.from_parquet([str(p) for p in paths]).create_view('cadastro')
        if conn.execute('select count(*) from cadastro').fetchone()[0] != manifest['rows']:
            raise ValueError('Cadastro count mismatch')
        _unique(conn)
        conn.execute('''create view vinculos as
            select CodInst, Data, 'financeiro' as perspectiva,
                   CodConglomeradoFinanceiro as CodConglomerado, CnpjInstituicaoLider
            from cadastro where CodConglomeradoFinanceiro is not null
            union all
            select CodInst, Data, 'prudencial', CodConglomeradoPrudencial, CnpjInstituicaoLider
            from cadastro where CodConglomeradoPrudencial is not null''')
        return conn
    except Exception:
        conn.close()
        raise


def attach_values(conn, output):
    """Attach authenticated values and a row-preserving code/reference join."""
    output = Path(output).resolve()
    with open_dataset(output):
        manifest = _json((output / 'manifest.json').read_bytes())
        paths = [str(_path(output, p['file'])) for p in manifest['files']]
        conn.from_parquet(paths).create_view('ifdata', replace=True)
    _unique(conn)
    conn.execute('''create or replace view ifdata_cadastrado as
        select v.*, c.CodInst is not null as cadastro_encontrado,
               c.NomeInstituicao, c.Td, c.Situacao,
               c.CodConglomeradoFinanceiro, c.CodConglomeradoPrudencial,
               c.CnpjInstituicaoLider
        from ifdata v left join cadastro c
          on v.CodInst = c.CodInst and v.AnoMes = c.Data''')


def _records(cursor):
    names = [c[0] for c in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def audit_links(cadastro, datasets):
    """Measure temporal joins and unresolved native links without filling them."""
    result = dict(coverage=[], unmatched=[], declared_links=[])
    with open_cadastro(cadastro) as conn:
        result['cadastro'] = _records(conn.execute('''select count(*) as registros,
            count(distinct CodInst) as codigos_distintos, count(distinct Data) as periodos,
            min(Data) as primeira_referencia, max(Data) as ultima_referencia from cadastro'''))[0]
        result['declared_links'] = _records(conn.execute('''select v.perspectiva, v.Data,
            count(*) as vinculos, count(c.CodInst) as destino_presente,
            count(*) filter(where c.CodInst is null) as destino_nao_encontrado
            from vinculos v left join cadastro c
              on v.CodConglomerado = c.CodInst and v.Data = c.Data
            group by all order by v.perspectiva, v.Data'''))
        for name, output in datasets.items():
            attach_values(conn, output)
            coverage = _records(conn.execute('''select AnoMes,
                count(*) as registros,
                count(*) filter(where cadastro_encontrado) as com_cadastro,
                count(*) filter(where not cadastro_encontrado) as sem_cadastro,
                count(*) filter(where CodInst is null) as codigo_ausente,
                count(distinct CodInst) as codigos_distintos,
                count(distinct CodInst) filter(where not cadastro_encontrado) as codigos_sem_cadastro
                from ifdata_cadastrado group by all order by AnoMes'''))
            if sum(row['registros'] for row in coverage) != conn.execute('select count(*) from ifdata').fetchone()[0]:
                raise ValueError('Temporal join changed the value row count')
            unmatched = _records(conn.execute('''select AnoMes, CodInst, count(*) as registros
                from ifdata_cadastrado where not cadastro_encontrado
                group by all order by AnoMes, CodInst'''))
            result['coverage'].extend(dict(dataset=name, **row) for row in coverage)
            result['unmatched'].extend(dict(dataset=name, **row) for row in unmatched)
    return result

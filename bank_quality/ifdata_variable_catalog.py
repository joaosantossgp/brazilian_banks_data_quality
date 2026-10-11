"""Observed variable definitions and quarterly coverage, without harmonization."""
import hashlib
import json
from pathlib import Path
import tempfile

import duckdb

from bank_quality.ifdata_odata import open_dataset


CONTRACT = 'ifdata-variable-catalog-v1'
DIMENSIONS = ('dataset', 'TipoInstituicao', 'NumeroRelatorio', 'NomeRelatorio',
              'Conta', 'Grupo', 'NomeColuna', 'DescricaoColuna')
TABLES = ('catalogo_variaveis', 'cobertura_variaveis')


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_catalog(datasets, output):
    """Aggregate accepted datasets into a new catalog; never edit inputs."""
    if not datasets or any(not isinstance(name, str) or not name for name in datasets):
        raise ValueError('Provide named accepted datasets')
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    result = dict(contract=CONTRACT, inputs={}, files=[], tables={})
    native = ', '.join(DIMENSIONS[1:])
    dimensions = ', '.join(DIMENSIONS)
    context = 'dataset, TipoInstituicao, NumeroRelatorio, Conta, Grupo'
    with tempfile.TemporaryDirectory(dir=output) as temporary, duckdb.connect() as conn:
        stages, periods = [], []
        for number, (name, source) in enumerate(datasets.items()):
            source = Path(source).resolve()
            with open_dataset(source) as data:
                periods.extend((name, row[0]) for row in data.execute('select distinct AnoMes from ifdata').fetchall())
                stage = str(Path(temporary) / f'{number}.parquet')
                data.execute(f'''copy (
                    select $1 as dataset, {native}, AnoMes,
                           count(*) as registros, count(Saldo) as com_valor,
                           count(*) filter (where Saldo is null) as sem_valor,
                           count(distinct CodInst) as codigos_distintos,
                           count(*) filter (where CodInst is null) as codigo_ausente
                    from ifdata group by all
                ) to $2 (format parquet, compression zstd)''', [name, stage])
                stages.append(stage)
            result['inputs'][name] = dict(manifest_sha256=_hash(source / 'manifest.json'))
        conn.execute('create table periodos(dataset varchar, AnoMes varchar)')
        conn.executemany('insert into periodos values (?, ?)', periods)
        conn.from_parquet(stages).create_view('cobertura_variaveis')
        conn.execute(f'''create temp table catalogo_variaveis as
            with aggregated as (
                select {dimensions}, min(AnoMes) as primeira_referencia,
                       max(AnoMes) as ultima_referencia,
                       list_sort(list(AnoMes)) as periodos,
                       count(*) as numero_referencias,
                       cast(sum(registros) as bigint) as registros,
                       cast(sum(com_valor) as bigint) as com_valor,
                       cast(sum(sem_valor) as bigint) as sem_valor,
                       cast(sum(codigo_ausente) as bigint) as codigo_ausente
                from cobertura_variaveis group by all
            )
            select *,
                coalesce((select list(p.AnoMes order by p.AnoMes) from periodos p
                          where p.dataset = a.dataset
                            and p.AnoMes between a.primeira_referencia and a.ultima_referencia
                            and not list_contains(a.periodos, p.AnoMes)), []::varchar[])
                    as periodos_sem_registro_entre_extremos,
                list_filter(periodos, p -> p between '201003' and '202412') as periodos_2010_2024,
                list_filter(periodos, p -> p between '202503' and '202606') as periodos_2025_2026,
                count(*) over (partition by {context}) as variantes_no_contexto,
                list_sort(list(distinct Conta) over (partition by dataset, TipoInstituicao,
                           NumeroRelatorio, Grupo, NomeColuna)) as codigos_com_mesmo_nome,
                (min(primeira_referencia) over (partition by {context}) < '202501'
                 and max(ultima_referencia) over (partition by {context}) >= '202501') as atravessa_2025,
                'nao_certificada' as comparabilidade
            from aggregated a''')
        for table in TABLES:
            result['tables'][table] = conn.execute(f'select count(*) from {table}').fetchone()[0]
            for extension, options in [('parquet', 'format parquet, compression zstd'),
                                       ('csv', 'format csv, header true')]:
                path = output / f'{table}.{extension}'
                conn.execute(f'copy (select * from {table} order by {dimensions}'
                             + (', AnoMes' if table == 'cobertura_variaveis' else ', primeira_referencia')
                             + f') to ? ({options})', [str(path)])
                result['files'].append(dict(file=path.name, sha256=_hash(path)))
    (output / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def query_catalog(output, sql):
    """Query both catalog tables using one SELECT; authenticate stored files."""
    output = Path(output).resolve()
    manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('contract') != CONTRACT:
        raise ValueError('Not an IF.data variable catalog')
    files = manifest.get('files')
    expected = {f'{table}.{extension}' for table in TABLES for extension in ('parquet', 'csv')}
    if (not isinstance(files, list) or len(files) != len(expected)
            or any(not isinstance(item, dict) for item in files)
            or {item.get('file') for item in files} != expected):
        raise ValueError('Incomplete or duplicate catalog inventory')
    for item in files:
        path = (output / item['file']).resolve()
        if not path.is_relative_to(output) or _hash(path) != item['sha256']:
            raise ValueError('Catalog file hash/path mismatch')
    with duckdb.connect() as conn:
        for table in TABLES:
            conn.from_parquet(str(output / f'{table}.parquet')).create_view(table)
        statements = conn.extract_statements(sql)
        if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
            raise ValueError('Query must be a single SELECT statement')
        cursor = conn.execute(sql)
        names = [column[0] for column in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]

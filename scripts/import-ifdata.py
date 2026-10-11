"""Import a captured IF.data package, inspect counts or run a SELECT."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality.ifdata_odata import import_package, query_dataset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    importer = commands.add_parser('import', help='Convert captured JSON/gzip to a new Parquet folder')
    importer.add_argument('root', help='Folder containing manifesto.json and dados/')
    importer.add_argument('output', help='New output folder')
    for name in ('periods', 'types', 'reports'):
        importer.add_argument('--' + name, nargs='+', help='Native IDs, separated by spaces')
    for command in ('counts', 'query'):
        child = commands.add_parser(command)
        child.add_argument('output', help='Accepted Parquet folder')
        if command == 'query': child.add_argument('sql', help='One SELECT statement')
    args = parser.parse_args()
    try:
        if args.command == 'import':
            result = import_package(args.root, args.output, args.periods, args.types, args.reports)
        else:
            sql = args.sql if args.command == 'query' else (
                'select AnoMes, TipoInstituicao, NumeroRelatorio, count(*) as rows, '
                'count(*) filter (where Saldo is null) as null_balances from ifdata '
                'group by all order by AnoMes, TipoInstituicao, NumeroRelatorio')
            result = query_dataset(args.output, sql)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f'Import/query failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

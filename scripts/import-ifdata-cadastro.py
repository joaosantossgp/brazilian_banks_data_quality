"""Import, query and inspect temporal links in captured IF.data cadastro."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import duckdb
from bank_quality.ifdata_cadastro import import_cadastro, open_cadastro, attach_values, audit_links, _records


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build')
    build.add_argument('source')
    build.add_argument('output')
    build.add_argument('--periods', nargs='+')
    query = commands.add_parser('query')
    query.add_argument('cadastro')
    query.add_argument('sql')
    query.add_argument('--values')
    audit = commands.add_parser('audit')
    audit.add_argument('cadastro')
    audit.add_argument('values_root')
    args = parser.parse_args()
    try:
        if args.command == 'build':
            result = import_cadastro(args.source, args.output, args.periods)
        elif args.command == 'audit':
            result = audit_links(args.cadastro, {name: Path(args.values_root) / name
                for name in ('financial', 'individual', 'capital', 'segmentation')})
        else:
            with open_cadastro(args.cadastro) as conn:
                if args.values:
                    attach_values(conn, args.values)
                statements = conn.extract_statements(args.sql)
                if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
                    raise ValueError('Query must be a single SELECT statement')
                result = _records(conn.execute(args.sql))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, duckdb.Error) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

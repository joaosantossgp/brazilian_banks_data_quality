"""Build or query the observed temporal IF.data variable catalog."""
import argparse
import json
from pathlib import Path
import sys

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality.ifdata_variable_catalog import build_catalog, query_catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build')
    build.add_argument('base', type=Path, help='Folder with accepted dataset subfolders')
    build.add_argument('output', type=Path, help='New output folder')
    build.add_argument('--datasets', nargs='+', choices=['financial', 'individual', 'capital', 'segmentation'],
                       default=['financial', 'individual', 'capital', 'segmentation'])
    query = commands.add_parser('query')
    query.add_argument('output', type=Path)
    query.add_argument('sql', help='One SELECT using catalogo_variaveis or cobertura_variaveis')
    args = parser.parse_args()
    try:
        result = (build_catalog({name: args.base / name for name in args.datasets}, args.output)
                  if args.command == 'build' else query_catalog(args.output, args.sql))
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0
    except (ValueError, OSError, KeyError, duckdb.Error) as exc:
        print(f'Catalog failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

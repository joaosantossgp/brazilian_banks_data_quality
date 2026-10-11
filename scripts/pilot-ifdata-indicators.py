"""Build and query the local exploratory IF.data indicator base."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import duckdb
from bank_quality.ifdata_indicators import build_pilot,open_pilot
from bank_quality.ifdata_cadastro import _records

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description=__doc__)
    commands=p.add_subparsers(dest='command',required=True)
    b=commands.add_parser('build');b.add_argument('values_root');b.add_argument('cadastro');b.add_argument('output')
    b.add_argument('--periods',nargs='+');b.add_argument('--opening-root')
    q=commands.add_parser('query');q.add_argument('output');q.add_argument('sql')
    args=p.parse_args()
    try:
        if args.command=='build':
            result=build_pilot(args.values_root,args.cadastro,args.output,args.periods,args.opening_root)
        else:
            with open_pilot(args.output) as conn:
                statements=conn.extract_statements(args.sql)
                if len(statements)!=1 or statements[0].type!=duckdb.StatementType.SELECT:
                    raise ValueError('Query must be a single SELECT statement')
                result=_records(conn.execute(args.sql))
        print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
        return 0
    except (ValueError,OSError,KeyError,duckdb.Error) as exc:
        print(str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())

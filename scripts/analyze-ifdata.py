"""Thin command line interface for the pinned monograph analysis package."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bank_quality.ifdata_analysis import build_analysis,verify_analysis,query_analysis


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    build=commands.add_parser('build');build.add_argument('--config',required=True);build.add_argument('--output',required=True)
    for name in ('verify','query'):
        sub=commands.add_parser(name);sub.add_argument('--output',required=True);sub.add_argument('--expected-manifest-sha256',required=True)
        if name=='query':sub.add_argument('--sql',required=True)
    args=parser.parse_args()
    if args.command=='build':result=build_analysis(json.loads(Path(args.config).read_text(encoding='utf-8')),args.output)
    elif args.command=='verify':result=verify_analysis(args.output,args.expected_manifest_sha256)
    else:result=query_analysis(args.output,args.expected_manifest_sha256,args.sql)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

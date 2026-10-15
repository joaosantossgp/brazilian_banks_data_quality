"""Thin command line interfaces for the pinned IF.data analysis contracts."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bank_quality.ifdata_analysis import (build_analysis,verify_analysis,query_analysis,
    build_universe_analysis,prepare_universe_opening,verify_universe_analysis,
    query_universe_analysis,compare_universe_analysis,resolve_universe_result)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ('build','build-universe'):
        sub=commands.add_parser(name);sub.add_argument('--config',required=True);sub.add_argument('--output',required=True)
        if name=='build-universe':
            sub.add_argument('--batch-size',type=int,default=32)
            sub.add_argument('--stage',choices=('unit-calculations','coverage-and-aggregation'),default='coverage-and-aggregation')
    opening=commands.add_parser('prepare-universe-opening')
    for option in ('raw-root','output','profile-id','profile-expected-sha256'):opening.add_argument('--'+option,required=True)
    for name in ('verify','query','verify-universe','query-universe','compare-universe','resolve-universe'):
        sub=commands.add_parser(name);sub.add_argument('--output',required=True);sub.add_argument('--expected-manifest-sha256',required=True)
        if name in ('query','query-universe'):sub.add_argument('--sql',required=True)
        if name=='compare-universe':sub.add_argument('--baseline',required=True);sub.add_argument('--baseline-manifest-sha256',required=True)
        if name=='resolve-universe':sub.add_argument('--result-id',required=True)
    args=parser.parse_args()
    if args.command in ('build','build-universe'):
        cfg=json.loads(Path(args.config).read_text(encoding='utf-8'))
        result=build_analysis(cfg,args.output) if args.command=='build' else build_universe_analysis(cfg,args.output,batch_size=args.batch_size,stage=args.stage)
    elif args.command=='prepare-universe-opening':result=prepare_universe_opening(args.raw_root,args.output,args.profile_id,args.profile_expected_sha256)
    elif args.command in ('verify','verify-universe'):
        result=(verify_analysis if args.command=='verify' else verify_universe_analysis)(args.output,args.expected_manifest_sha256)
    elif args.command in ('query','query-universe'):
        result=(query_analysis if args.command=='query' else query_universe_analysis)(args.output,args.expected_manifest_sha256,args.sql)
    elif args.command=='resolve-universe':result=resolve_universe_result(args.output,args.expected_manifest_sha256,args.result_id)
    else:result=compare_universe_analysis(args.output,args.expected_manifest_sha256,args.baseline,args.baseline_manifest_sha256)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if args.command=='compare-universe' and result['status']=='different':return 1
    return 0


if __name__=='__main__':sys.exit(main())

import argparse
import json
from pathlib import Path
from .replay import replay
from .ifdata import collect

def main():
    parser=argparse.ArgumentParser(description='Bounded IF.data pilot: 201012 + 202412, individual Resumo')
    commands=parser.add_subparsers(dest='command',required=True)
    offline=commands.add_parser('replay',help='Verify raw hashes and rebuild inventories without network')
    offline.add_argument('--collection',type=Path,required=True)
    offline.add_argument('--output',type=Path,required=True)
    pilot=commands.add_parser('collect',help='Collect the two approved quarters into a NEW run directory')
    pilot.add_argument('--run',type=Path,required=True)
    pilot.add_argument('--no-fallback',action='store_true')
    pilot.add_argument('--periods',type=int,nargs='+',default=[201012,202412],help='Explicit allowlist: 201012 202312 202412')
    pilot.add_argument('--portal-only',action='store_true',help='Official portal fallback with no new OData availability claim')
    args=parser.parse_args()
    if args.command=='replay': result=replay(args.collection,args.output)
    else:
        args.run.mkdir(parents=True,exist_ok=False)
        result=collect(args.run,tuple(args.periods),allow_fallback=not args.no_fallback,portal_only=args.portal_only)
        (args.run/'collection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        if not all(q['values_complete'] for q in result['quarters'].values()):
            print(json.dumps({'complete':False,'collection':str(args.run/'collection.json'),'diagnostics':{p:q['diagnostics'] for p,q in result['quarters'].items()}},ensure_ascii=False))
            return 2
        result=replay(args.run/'collection.json',args.run/'inventory')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())

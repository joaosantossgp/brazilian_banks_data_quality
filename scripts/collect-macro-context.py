"""Collect or replay the finite official macro context, without financial evaluation."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bank_quality.macro_context import collect_context,replay_context,add_interest_context

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw')
    parser.add_argument('--output',required=True)
    parser.add_argument('--capture-pin',help='Replay existing captures under this manifest pin; no HTTP')
    for name in ('context','context-pin','interest-evidence','interest-evidence-pin'):
        parser.add_argument('--'+name)
    args=parser.parse_args()
    interest=[args.context,args.context_pin,args.interest_evidence,args.interest_evidence_pin]
    if any(interest):
        if not all(interest) or args.raw or args.capture_pin:parser.error('Interest extension requires its four inputs, without capture arguments')
        result=add_interest_context(*interest,args.output)
    else:
        if not args.raw:parser.error('--raw is required for collection or replay')
        result=(replay_context(args.raw,args.capture_pin,args.output) if args.capture_pin else collect_context(args.raw,args.output))
    print(json.dumps(dict(contract=result['contract'],tables=result['tables'],coverage=result['coverage']),ensure_ascii=True))

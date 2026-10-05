"""Explicit offline prepare/run/status entry; no install/accept/network options."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality import financial_pipeline as pipeline


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare')
    for name in ('bundle', 'handoff', 'output'):
        prepare.add_argument('--' + name, type=Path, required=True)
    for name in ('bundle-sha256', 'bootstrap-sha256', 'handoff-sha256'):
        prepare.add_argument('--' + name, required=True)
    prepare.add_argument('--accepted-supplement', type=Path)
    prepare.add_argument('--accepted-supplement-sha256')
    run = commands.add_parser('run')
    run.add_argument('--resume', action='store_true')
    status = commands.add_parser('status')
    for command in (run, status):
        command.add_argument('--plan', type=Path, required=True)
        command.add_argument('--plan-sha256', required=True)
    for command in (prepare, run):
        command.add_argument('--resources', type=Path, required=True)
        command.add_argument('--resources-sha256', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command != 'status':
            raw = args.resources.read_bytes()
            if hashlib.sha256(raw).hexdigest() != args.resources_sha256:
                raise pipeline.IntegrityError('External resource-file SHA-256 mismatch')
            resources = json.loads(raw, object_pairs_hook=pipeline.profiles.legacy._pairs,
                                   parse_constant=pipeline.profiles.legacy._constant)
            pipeline.validate_resources(resources)
        if args.command == 'prepare':
            result = pipeline.prepare_profiles(args.bundle, args.handoff, args.output,
                bundle_sha256=args.bundle_sha256, bootstrap_sha256=args.bootstrap_sha256,
                handoff_sha256=args.handoff_sha256, resources=resources,
                accepted_supplement_path=args.accepted_supplement,
                accepted_supplement_sha256=args.accepted_supplement_sha256)
        elif args.command == 'run':
            result = pipeline.run_pipeline(args.plan, plan_sha256=args.plan_sha256,
                                           resources=resources, resume=args.resume)
        else:
            result = pipeline.read_status(args.plan, plan_sha256=args.plan_sha256)
        code = 0 if result['status'] in ('complete', 'prepared') else 3 if result['status'] == 'halted' else 2
    except Exception as error:
        result = {'status': 'halted', 'error': {'code': type(error).__name__, 'message': str(error)}}
        code = 3
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())

"""Acquire the closed 202403 financial job; prepare/recover/verify are offline."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality import financial_acquisition as acquisition


def _job_arguments(parser, *, bootstrap=False):
    parser.add_argument('--job', type=Path, required=True)
    parser.add_argument('--job-sha256', required=True, help='Externally approved canonical job hash')
    if bootstrap:
        parser.add_argument('--bootstrap-sha256', required=True, help='External immutable authority hash')


def _receipt_summary(receipt, status):
    result = {key: receipt[key] for key in ('job_sha256', 'bootstrap_sha256', 'sequence',
                                           'record_sha256', 'state_sha256')}
    result.update(status=status, receipt_sha256=acquisition._sha(acquisition._canonical(receipt)),
                  pending_attempts=len(receipt['state']['pending']))
    result.update({key: receipt['state'][key] for key in ('attempts', 'body_bytes', 'attempt_seconds',
                                                        'backoff_seconds', 'backoffs', 'failures')})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest='command', required=True, parser_class=argparse.ArgumentParser)
    prepare = commands.add_parser('prepare', help='Write a new offline candidate; grants no authority', allow_abbrev=False)
    prepare.add_argument('--catalog-index', type=Path, required=True)
    prepare.add_argument('--catalog-index-sha256', required=True)
    prepare.add_argument('--reuse-index', type=Path)
    prepare.add_argument('--reuse-index-sha256')
    prepare.add_argument('--output', type=Path, required=True, help='New job file inside approved data/runs')
    initialize = commands.add_parser('initialize-authority', help='Explicit exclusive offline bootstrap; cannot reset', allow_abbrev=False)
    _job_arguments(initialize)
    for name in ('metadata', 'values'):
        phase = commands.add_parser(name, help='Run the fixed single-worker phase under current authority', allow_abbrev=False)
        _job_arguments(phase, bootstrap=True)
        phase.add_argument('--session', type=Path, required=True, help='New session directory inside data/runs')
        phase.add_argument('--resume-from', type=Path, required=name == 'values')
        phase.add_argument('--resume-sha256', required=name == 'values')
        if name == 'values':
            phase.add_argument('--checkpoint-a-sha256', required=True, help='Physical A beside externally pinned metadata receipt')
    recover = commands.add_parser('recover', help='Offline conservative reconciliation to a new receipt', allow_abbrev=False)
    _job_arguments(recover, bootstrap=True)
    recover.add_argument('--output', type=Path, required=True, help='New receipt file inside approved data/runs')
    verify = commands.add_parser('verify', help='Offline current authority and optional receipt verification', allow_abbrev=False)
    _job_arguments(verify, bootstrap=True)
    verify.add_argument('--receipt', type=Path)
    verify.add_argument('--receipt-sha256')
    args = parser.parse_args(argv)
    for path_name, hash_name in (('reuse_index', 'reuse_index_sha256'), ('resume_from', 'resume_sha256'),
                                 ('receipt', 'receipt_sha256')):
        if (getattr(args, path_name, None) is None) != (getattr(args, hash_name, None) is None):
            parser.error(path_name.replace('_', '-') + ' requires its external SHA-256')
    try:
        if args.command == 'prepare':
            destination = acquisition._safe_destination(args.output)
            acquisition._require(not destination.exists(), 'Candidate destination must be new')
            job = acquisition.prepare_job(args.catalog_index, args.catalog_index_sha256, (202403,),
                                          limits=dict(acquisition._POLICIES), reuse_index=args.reuse_index,
                                          reuse_index_sha256=args.reuse_index_sha256)
            destination.parent.mkdir(parents=True, exist_ok=True)
            acquisition._write_exclusive(destination, job)
            result = {'status': 'candidate', 'job_sha256': job['job_sha256'], 'executable': False}
        elif args.command == 'initialize-authority':
            job = acquisition._load_job(args.job, args.job_sha256)
            pin = acquisition.initialize_authority(job)
            result = {'status': 'initialized', 'job_sha256': args.job_sha256, 'bootstrap_sha256': pin}
        elif args.command == 'verify':
            result = acquisition.verify_authority(args.job, args.job_sha256, bootstrap_sha256=args.bootstrap_sha256,
                                                  receipt_path=args.receipt, receipt_sha256=args.receipt_sha256)
        elif args.command == 'recover':
            receipt = acquisition.recover_authority(args.job, args.job_sha256,
                                                    bootstrap_sha256=args.bootstrap_sha256, output=args.output)
            result = _receipt_summary(receipt, 'recovered')
        else:
            receipt = acquisition.run_acquisition(args.job, args.job_sha256, args.session, phase=args.command,
                                                  bootstrap_sha256=args.bootstrap_sha256,
                                                  checkpoint_sha256=getattr(args, 'checkpoint_a_sha256', None),
                                                  resume_from=args.resume_from, resume_sha256=args.resume_sha256)
            result = _receipt_summary(receipt, args.command + '_complete')
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(2, 'Financial acquisition failed: ' + str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

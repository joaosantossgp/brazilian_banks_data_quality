"""Build, verify or query pinned offline v2 historical relationships (nine CSV)."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality.historical_issuer_links import (
    build_historical_issuer_links, verify_historical_issuer_links, query_historical_issuer_links,
    validate_issuer_supplement_index,
    build_issuer_supplement, verify_issuer_supplement, query_issuer_supplement,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build')
    for name in ('cvm', 'cadastro', 'corporate', 'output'):
        build.add_argument(name)
    for name in ('cvm', 'cadastro', 'corporate'):
        build.add_argument('--' + name + '-sha256', required=True)
    check = commands.add_parser('supplement-check')
    check.add_argument('index')
    check.add_argument('--index-sha256', required=True)
    check.add_argument('--evidence-root', required=True)
    supplement_build = commands.add_parser('supplement-build')
    for name in ('index', 'core', 'output'):
        supplement_build.add_argument(name)
    for name in ('index-sha256', 'core-sha256', 'evidence-root'):
        supplement_build.add_argument('--' + name, required=True)
    for name in ('supplement-verify', 'supplement-query'):
        command = commands.add_parser(name)
        for positional in ('output', 'core'):
            command.add_argument(positional)
        for pin in ('manifest-sha256', 'index-sha256', 'core-sha256'):
            command.add_argument('--' + pin, required=True)
        if name == 'supplement-query':
            for filter_name in ('company', 'reference', 'perspective'):
                command.add_argument('--' + filter_name)
    for name in ('verify', 'query'):
        command = commands.add_parser(name)
        command.add_argument('output')
        command.add_argument('--manifest-sha256', required=True)
        if name == 'query':
            for filter_name in ('reference', 'entity', 'perspective'):
                command.add_argument('--' + filter_name)
            for option in ('supplement', 'supplement-sha256', 'supplement-index-sha256'):
                command.add_argument('--' + option)
    args = parser.parse_args()
    try:
        if args.command == 'supplement-check':
            result = validate_issuer_supplement_index(args.index, args.index_sha256, args.evidence_root)
        elif args.command == 'supplement-build':
            result = build_issuer_supplement(args.index, args.index_sha256, args.evidence_root,
                args.core, args.core_sha256, args.output)
        elif args.command == 'supplement-verify':
            result = verify_issuer_supplement(args.output, args.manifest_sha256, args.index_sha256,
                args.core, args.core_sha256)
        elif args.command == 'supplement-query':
            result = query_issuer_supplement(args.output, args.manifest_sha256, args.index_sha256,
                args.core, args.core_sha256, company=args.company, reference=args.reference,
                perspective=args.perspective)
        elif args.command == 'build':
            result = build_historical_issuer_links(args.cvm, args.cvm_sha256, args.cadastro,
                args.cadastro_sha256, args.corporate, args.corporate_sha256, args.output)
        elif args.command == 'verify':
            result = verify_historical_issuer_links(args.output, args.manifest_sha256)
        else:
            result = query_historical_issuer_links(args.output, args.manifest_sha256,
                reference=args.reference, entity=args.entity, perspective=args.perspective,
                supplement=args.supplement, expected_supplement_sha256=args.supplement_sha256,
                expected_supplement_index_sha256=args.supplement_index_sha256)
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

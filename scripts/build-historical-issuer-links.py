"""Build, verify or query pinned offline historical issuer relationships."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality.historical_issuer_links import (
    build_historical_issuer_links, verify_historical_issuer_links, query_historical_issuer_links,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build')
    for name in ('cvm', 'cadastro', 'corporate', 'output'):
        build.add_argument(name)
    for name in ('cvm', 'cadastro', 'corporate'):
        build.add_argument('--' + name + '-sha256', required=True)
    for name in ('verify', 'query'):
        command = commands.add_parser(name)
        command.add_argument('output')
        command.add_argument('--manifest-sha256', required=True)
        if name == 'query':
            for filter_name in ('reference', 'entity', 'perspective'):
                command.add_argument('--' + filter_name)
    args = parser.parse_args()
    try:
        if args.command == 'build':
            result = build_historical_issuer_links(args.cvm, args.cvm_sha256, args.cadastro,
                args.cadastro_sha256, args.corporate, args.corporate_sha256, args.output)
        elif args.command == 'verify':
            result = verify_historical_issuer_links(args.output, args.manifest_sha256)
        else:
            result = query_historical_issuer_links(args.output, args.manifest_sha256,
                reference=args.reference, entity=args.entity, perspective=args.perspective)
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

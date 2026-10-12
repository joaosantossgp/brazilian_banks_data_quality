"""Build or verify authenticated offline CVM metadata snapshots."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bank_quality.cvm_metadata import build_cvm_metadata, verify_cvm_metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build')
    build.add_argument('source_index')
    build.add_argument('output')
    build.add_argument('--index-sha256', required=True)
    verify = commands.add_parser('verify')
    verify.add_argument('output')
    verify.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'build':
            result = build_cvm_metadata(args.source_index, args.index_sha256, args.output)
        else:
            result = verify_cvm_metadata(args.output, args.manifest_sha256)
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

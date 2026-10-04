"""Convert the admitted financial 202412 snapshot offline to a new Parquet directory."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality.financial_parquet import convert_financial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Accepted financial admission directory')
    parser.add_argument('--source-manifest-sha256', required=True, help='Externally verified input manifest SHA-256')
    parser.add_argument('--output', type=Path, required=True, help='New financial Parquet directory')
    args = parser.parse_args()
    try:
        result = convert_financial(args.source, args.output, source_manifest_sha256=args.source_manifest_sha256)
    except (ValueError, OSError) as error:
        parser.exit(2, 'Financial conversion failed: ' + str(error) + '\n')
    print(json.dumps({k: result[k] for k in ('contract', 'selection', 'observations', 'cells',
                                          'cadaster_records', 'decimal_type', 'manifest_sha256')}, ensure_ascii=False))


if __name__ == '__main__':
    main()

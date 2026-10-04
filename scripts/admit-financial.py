"""Admit a closed 202312 or202412 financial snapshot from existing local archives."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality.financial import admit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, required=True, help='Explicit five-source archive index')
    parser.add_argument('--output', type=Path, required=True, help='New financial output directory')
    args = parser.parse_args()
    try:
        result = admit(args.index, args.output)
    except (ValueError, OSError) as error:
        parser.exit(2, 'Financial admission failed: ' + str(error) + '\n')
    print(json.dumps({key: result[key] for key in ('contract', 'selection', 'observations', 'cells', 'cadaster_records')}, ensure_ascii=False))


if __name__ == '__main__':
    main()

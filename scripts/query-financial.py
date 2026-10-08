"""Discover and query authenticated local IF.data financial snapshots."""
import argparse
from contextlib import closing
from decimal import Decimal
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bank_quality import financial_catalog as catalog


class ArgumentFailure(ValueError):
    pass


class JsonParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentFailure('Invalid or missing command arguments')


def positive(value):
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError('Expected positive integer')
    return result


def column(value):
    result = int(value)
    if result < 0:
        raise argparse.ArgumentTypeError('Expected nonnegative integer')
    return result


def limit(value):
    result = positive(value)
    if result > 10000:
        raise argparse.ArgumentTypeError('Maximum limit is 10000')
    return result


def parser():
    root = JsonParser(description=__doc__, allow_abbrev=False)
    commands = root.add_subparsers(dest='command', required=True, parser_class=JsonParser)
    prepare = commands.add_parser('catalog-prepare', allow_abbrev=False)
    prepare.add_argument('--inputs', type=Path, required=True)
    prepare.add_argument('--inputs-sha256', required=True)
    prepare.add_argument('--output', type=Path, required=True)
    for name in ('list', 'show', 'counts', 'bindings', 'cells', 'decimals'):
        command = commands.add_parser(name, allow_abbrev=False)
        command.add_argument('--catalog', type=Path, required=True)
        command.add_argument('--catalog-sha256', required=True)
        command.add_argument('--period', type=positive, required=name != 'list')
        command.add_argument('--perspective', type=positive, required=name != 'list')
        command.add_argument('--report', type=positive, required=name == 'decimals')
        if name != 'list':
            command.add_argument('--revision')
        if name in ('cells', 'decimals'):
            command.add_argument('--limit', type=limit, default=100)
        if name == 'cells':
            command.add_argument('--institution')
        if name == 'decimals':
            command.add_argument('--column', type=column, required=True)
    return root


def json_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError('Unsupported JSON result type')


def rows(cursor):
    names = [field[0] for field in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def execute(args):
    if args.command == 'catalog-prepare':
        return catalog.prepare_catalog(args.inputs, args.output, inputs_sha256=args.inputs_sha256)
    context = catalog.load_catalog(args.catalog, catalog_sha256=args.catalog_sha256)
    if args.command == 'list':
        all_rows = catalog.discover(context)
        return {'coverage': catalog._coverage(all_rows),
                'rows': catalog.discover(context, period=args.period, perspective=args.perspective, report_id=args.report)}
    selector = {'period': args.period, 'perspective': args.perspective,
                'report_id': args.report, 'revision_id': args.revision}
    resolved = catalog.resolve_snapshot(context, **selector)
    if args.command == 'show':
        return resolved
    result = {'selection': resolved['selection'], 'revision_id': resolved['revision_id'],
              'native_counts': resolved['counts'], 'local_health': 'payload_verified', 'payload_validation': 'payload_verified'}
    if args.command == 'decimals':
        with closing(catalog.iter_numeric_decimals(context, **selector, column_id=args.column)) as iterator:
            selected = []
            for row in iterator:
                selected.append(row)
                if len(selected) > args.limit:
                    break
            result.update(rows=selected[:args.limit], limit=args.limit, truncated=len(selected) > args.limit)
        return result
    clauses, parameters = [], []
    if args.report is not None:
        clauses.append('report_id = ?'); parameters.append(str(args.report))
    if args.command == 'cells' and args.institution is not None:
        clauses.append('institution_id = ?'); parameters.append(args.institution)
    where = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
    with closing(catalog.snapshot_connection(context, **selector)) as connection:
        if args.command == 'counts':
            values = connection.execute("SELECT count(*), count(*) FILTER (WHERE presence = 'stored'), "
                                        'count(DISTINCT institution_id) FROM financial_cells' + where, parameters).fetchone()
            result['counts'] = dict(zip(('cells', 'observations', 'cadaster_records'), values))
        elif args.command == 'bindings':
            result['rows'] = rows(connection.execute('SELECT * FROM financial_bindings' + where +
                                                    ' ORDER BY report_id, catalog_pointer', parameters))
        elif args.command == 'cells':
            selected = rows(connection.execute('SELECT * FROM financial_cells' + where +
                                               ' ORDER BY institution_id, report_id, catalog_pointer LIMIT ?',
                                               [*parameters, args.limit + 1]))
            result.update(rows=selected[:args.limit], limit=args.limit, truncated=len(selected) > args.limit)
    return result


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        result = execute(args)
        output = json.dumps(result, ensure_ascii=False, allow_nan=False, default=json_value)
        status = 0
    except ArgumentFailure:
        output = json.dumps({'error': {'code': 'arguments', 'message': 'Invalid or missing command arguments'}})
        status = 2
    except catalog.CatalogError as exc:
        status = 2 if exc.code in ('unavailable', 'ambiguous_revision', 'unknown_selection', 'unknown_binding') else 3
        output = json.dumps({'error': {'code': exc.code, 'message': 'Financial catalog command could not be completed'}})
    except Exception:
        status = 3
        output = json.dumps({'error': {'code': 'unexpected', 'message': 'Financial catalog command failed'}})
    print(output)
    return status


if __name__ == '__main__':
    raise SystemExit(main())

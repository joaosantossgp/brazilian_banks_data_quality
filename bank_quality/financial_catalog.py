"""Financial catalog metadata boundary.

Catalog authority, construction and querying are added in subsequent reviewed
checkpoints. These primitives never authorize a snapshot from metadata alone.
"""
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat


_MAX_METADATA_BYTES = 32 * 1024 * 1024
_HASH = re.compile(r'[0-9a-f]{64}\Z')
_RESERVED = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)),
             *(f'lpt{i}' for i in range(1, 10))}


class CatalogError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def _require(condition, message):
    if not condition:
        raise CatalogError('integrity', message)


def _fields(value, names):
    _require(type(value) is dict and set(value) == set(names), 'Unexpected metadata fields')


def _positive_integer(value):
    _require(type(value) is int and value > 0, 'Expected a positive integer')
    return value


def _hash(value):
    _require(type(value) is str and _HASH.fullmatch(value) is not None, 'Invalid external SHA-256')
    return value


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def _float(token):
    value = float(token)
    _require(math.isfinite(value), 'Nonfinite JSON number')
    return value


def _constant(token):
    raise CatalogError('integrity', 'Nonfinite JSON constant')


def _json_bytes(raw):
    _require(type(raw) is bytes, 'Expected captured JSON bytes')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                          parse_constant=_constant, parse_float=_float)
    except CatalogError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise CatalogError('integrity', 'Invalid UTF-8 JSON metadata') from exc


def _string_keys(value):
    if type(value) is dict:
        _require(all(type(k) is str for k in value), 'JSON object keys must be strings')
        for item in value.values():
            _string_keys(item)
    elif type(value) in (list, tuple):
        for item in value:
            _string_keys(item)


def _canonical(value):
    try:
        _string_keys(value)
        return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                           ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
    except CatalogError:
        raise
    except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
        raise CatalogError('integrity', 'Metadata cannot be serialized canonically') from exc


def _plain_path(path):
    """Reject all Windows reparse kinds as well as portable symbolic links."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return
    _require(not stat.S_ISLNK(metadata.st_mode)
             and not getattr(metadata, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
             'Metadata path contains a link or reparse point')


def _contained_path(root, relative):
    _require(type(relative) is str and relative, 'Expected a relative metadata path')
    _require(not any(ord(c) < 32 or c in '\\:<>"|?*' for c in relative), 'Noncanonical metadata path')
    p = PurePosixPath(relative)
    _require(not p.is_absolute() and p.as_posix() == relative
             and all(part not in ('.', '..') for part in p.parts), 'Metadata path escapes its root')
    _require(all(not part.endswith((' ', '.')) and part.split('.')[0].lower() not in _RESERVED
                 for part in p.parts), 'Windows metadata path alias')
    try:
        anchor = Path(root).absolute()
        # Root itself can be plain while an ancestor redirects it via reparse.
        for ancestor in (anchor, *anchor.parents):
            _plain_path(ancestor)
        _require(anchor.is_dir(), 'Metadata root does not exist')
        target = anchor.joinpath(*p.parts)
        _require(target.resolve().is_relative_to(anchor.resolve()), 'Metadata path escapes its root')
        cursor = anchor
        for part in p.parts:
            cursor = cursor / part
            _plain_path(cursor)
        return target
    except CatalogError:
        raise
    except (OSError, ValueError, RuntimeError) as exc:
        raise CatalogError('integrity', 'Metadata path cannot be resolved safely') from exc


@dataclass(frozen=True)
class _PinnedImage:
    path: str
    sha256: str
    raw: bytes

    def document(self):
        # Reconstruct so mutable dictionaries cannot change the captured image.
        return _json_bytes(self.raw)


def _read_reference(root, reference, *, max_bytes=_MAX_METADATA_BYTES):
    _fields(reference, ('path', 'sha256'))
    pin = _hash(reference['sha256'])
    _positive_integer(max_bytes)
    path = _contained_path(root, reference['path'])
    try:
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            _require(stat.S_ISREG(opened.st_mode), 'Metadata reference is not a regular file')
            _require(opened.st_size <= max_bytes, 'Metadata reference exceeds its size limit')
            raw = stream.read(max_bytes + 1)
            _require(len(raw) <= max_bytes, 'Metadata reference grew beyond its size limit')
            current = _contained_path(root, reference['path']).stat()
            _require(os.path.samestat(opened, current), 'Metadata reference changed identity during capture')
    except CatalogError:
        raise
    except OSError as exc:
        raise CatalogError('integrity', 'Metadata reference cannot be captured') from exc
    _require(hashlib.sha256(raw).hexdigest() == pin, 'Metadata reference SHA-256 mismatch')
    _json_bytes(raw)
    return _PinnedImage(reference['path'], pin, raw)

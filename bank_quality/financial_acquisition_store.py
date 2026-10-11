"""Small transactional operational ledger; no HTTP, worker or data admission.

Pending attempts retain their full reservations after restart. The caller alone
proves worker extinction and external artifacts before finishing an attempt.
SQLite transactions do not cover those artifacts. Use one connection per thread.
"""
from contextlib import contextmanager
import json
import os
import re
from pathlib import Path
import sqlite3
import stat
import uuid


_FIELDS = ('attempts', 'body_bytes', 'attempt_ms')


def _identifier(value):
    if type(value) is not str or not value.strip() or '\x00' in value:
        raise ValueError('Expected a nonempty textual identifier')
    return value


def _integer(value, *, positive=False):
    if type(value) is not int or value < int(positive) or value > 2**63 - 1:
        raise ValueError('Expected a nonnegative SQLite integer (positive for limits/deadline)')
    return value


def _budget(value, *, positive=False):
    if type(value) is not dict or set(value) != set(_FIELDS):
        raise ValueError('Budget must contain exactly attempts, body_bytes and attempt_ms')
    return {key: _integer(value[key], positive=positive) for key in _FIELDS}


def _json(value):
    try:
        return json.dumps(value, allow_nan=False, separators=(',', ':'))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError('Result must be finite JSON serializable data') from exc


def _path(value):
    # Existing acquisition helpers enforce data/runs or authenticated relative
    # files. This caller-chosen database also serves temporary offline tests;
    # apply their lstat/reparse check locally without changing those contracts.
    path = Path(value)
    if '..' in path.parts:
        raise ValueError('Parent traversal is forbidden')
    path = path.absolute()
    for current in (*reversed(path.parents), path):
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Database symlink/reparse path is forbidden')
        if current == path and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
            raise ValueError('Database must be a regular file without hardlink aliases')
    return path


class AttemptStore:
    """Explicit connection with short transactions and immutable run config.

    Identifiers are opaque text. Integer values fit signed SQLite int64. Paths
    require existing parent directories. A failed initialization leaves its new
    file for diagnosis; open never repairs or initializes it. Filesystem races
    against an adversarial process replacing paths are outside this component.
    """

    def __init__(self, connection):
        self._connection = connection

    @staticmethod
    def _connect(path):
        for suffix in ('-journal', '-wal', '-shm'):
            _path(str(path) + suffix)
        connection = sqlite3.connect(path.as_uri() + '?mode=rw', uri=True,
                                     isolation_level=None, timeout=5.0)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute('PRAGMA synchronous=FULL')
            if connection.execute('PRAGMA journal_mode').fetchone()[0] != 'delete':
                raise ValueError('Attempt store requires DELETE journal mode')
            return connection
        except BaseException:
            connection.close()
            raise

    @classmethod
    def create(cls, path, *, scope, limits, carried_usage):
        scope = _identifier(scope)
        limits = _budget(limits, positive=True)
        carried_usage = _budget(carried_usage)
        path = _path(path)
        for suffix in ('-journal', '-wal', '-shm'):
            sidecar = _path(str(path) + suffix)
            if sidecar.exists():
                raise FileExistsError('New store has an existing SQLite companion')
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
        store = cls(cls._connect(path))
        try:
            with store._transaction(write=True):
                store._connection.execute('''CREATE TABLE run_config (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    scope TEXT NOT NULL, limits_json TEXT NOT NULL,
                    carried_usage_json TEXT NOT NULL)''')
                store._connection.execute('''CREATE TABLE attempts (
                    attempt_id TEXT PRIMARY KEY, target TEXT NOT NULL,
                    body_budget_bytes INTEGER NOT NULL, deadline_ms INTEGER NOT NULL,
                    outcome TEXT NOT NULL CHECK(outcome IN ('pending','success','failure')),
                    observed_bytes INTEGER, elapsed_ms INTEGER, result_json TEXT,
                    spec_sha256 TEXT, launcher_identity_json TEXT)''')
                store._connection.execute('INSERT INTO run_config VALUES (1, ?, ?, ?)',
                                          (scope, _json(limits), _json(carried_usage)))
            return store
        except BaseException:
            store.close()
            raise

    @classmethod
    def open(cls, path, *, scope):
        scope = _identifier(scope)
        path = _path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        store = cls(cls._connect(path))
        try:
            state = store.snapshot()
            if state['scope'] != scope:
                raise ValueError('Attempt store scope differs')
            return store
        except BaseException:
            store.close()
            raise

    @contextmanager
    def _transaction(self, *, write=False):
        self._connection.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
        try:
            yield
            self._connection.execute('COMMIT')
        except BaseException:
            if self._connection.in_transaction:
                self._connection.execute('ROLLBACK')
            raise

    def _state(self):
        try:
            config = self._connection.execute('SELECT * FROM run_config').fetchall()
            rows = self._connection.execute('SELECT * FROM attempts ORDER BY rowid').fetchall()
            if len(config) != 1 or config[0]['singleton'] != 1:
                raise ValueError('Missing or invalid attempt store configuration')
            config = config[0]
            limits = _budget(json.loads(config['limits_json']), positive=True)
            carry = _budget(json.loads(config['carried_usage_json']))
            scope = _identifier(config['scope'])
        except (sqlite3.DatabaseError, KeyError, json.JSONDecodeError) as exc:
            raise ValueError('Missing or invalid attempt store schema/configuration') from exc
        usage = dict(carry)
        attempts = []
        for row in rows:
            attempt = dict(row)
            result = attempt.pop('result_json')
            launcher = attempt.pop('launcher_identity_json')
            attempt['launcher_identity'] = json.loads(launcher) if launcher is not None else None
            attempt['result'] = json.loads(result) if result is not None else None
            attempts.append(attempt)
            pending = attempt['outcome'] == 'pending'
            usage['attempts'] += 1
            usage['body_bytes'] += attempt['body_budget_bytes'] if pending else attempt['observed_bytes']
            usage['attempt_ms'] += attempt['deadline_ms'] if pending else attempt['elapsed_ms']
        return {'scope': scope, 'limits': limits, 'carried_usage': carry,
                'usage': usage, 'attempts': attempts}

    def reserve(self, target, *, body_budget_bytes, deadline_ms):
        target = _identifier(target)
        body_budget_bytes = _integer(body_budget_bytes)
        deadline_ms = _integer(deadline_ms, positive=True)
        with self._transaction(write=True):
            state = self._state()
            if any(row['target'] == target and row['outcome'] in ('pending', 'success')
                   for row in state['attempts']):
                raise ValueError('Target has a pending attempt or prior success')
            requested = {'attempts': 1, 'body_bytes': body_budget_bytes, 'attempt_ms': deadline_ms}
            if any(state['usage'][key] + requested[key] > state['limits'][key] for key in _FIELDS):
                raise ValueError('Attempt reservation exceeds run limits')
            attempt_id = uuid.uuid4().hex
            self._connection.execute('''INSERT INTO attempts
                (attempt_id, target, body_budget_bytes, deadline_ms, outcome)
                VALUES (?, ?, ?, ?, 'pending')''',
                (attempt_id, target, body_budget_bytes, deadline_ms))
        return attempt_id

    def bind_worker(self, attempt_id, *, spec_sha256, launcher_identity):
        """Commit the sole Native launcher binding before its suspended resume."""
        attempt_id = _identifier(attempt_id)
        if type(spec_sha256) is not str or not re.fullmatch('[0-9a-f]{64}', spec_sha256):
            raise ValueError('Expected a closed SHA-256 pin')
        if (type(launcher_identity) is not dict
                or set(launcher_identity) != {'pid', 'creation_time', 'contained'}
                or type(launcher_identity['pid']) is not int or launcher_identity['pid'] <= 0
                or type(launcher_identity['creation_time']) is not int or launcher_identity['creation_time'] <= 0
                or launcher_identity['contained'] is not True):
            raise ValueError('Expected a contained Native launcher identity')
        identity_json = _json(launcher_identity)
        with self._transaction(write=True):
            row = self._connection.execute('SELECT * FROM attempts WHERE attempt_id=?',
                                           (attempt_id,)).fetchone()
            if (row is None or row['outcome'] != 'pending' or row['spec_sha256'] is not None
                    or row['launcher_identity_json'] is not None):
                raise ValueError('Attempt is absent, finished or already bound')
            self._connection.execute('''UPDATE attempts SET spec_sha256=?, launcher_identity_json=?
                WHERE attempt_id=?''', (spec_sha256, identity_json, attempt_id))

    def finish(self, attempt_id, *, observed_bytes, elapsed_ms, outcome, result):
        attempt_id = _identifier(attempt_id)
        observed_bytes = _integer(observed_bytes)
        elapsed_ms = _integer(elapsed_ms)
        if outcome not in ('success', 'failure'):
            raise ValueError('Outcome must be success or failure')
        result_json = _json(result)
        with self._transaction(write=True):
            row = self._connection.execute('SELECT * FROM attempts WHERE attempt_id=?',
                                           (attempt_id,)).fetchone()
            if row is None or row['outcome'] != 'pending':
                raise ValueError('Attempt is absent or already finished')
            if observed_bytes > row['body_budget_bytes']:
                raise ValueError('Observed bytes exceed reservation')
            self._connection.execute('''UPDATE attempts SET
                observed_bytes=?, elapsed_ms=?, outcome=?, result_json=? WHERE attempt_id=?''',
                (observed_bytes, elapsed_ms, outcome, result_json, attempt_id))

    def snapshot(self):
        with self._transaction():
            return self._state()

    def close(self):
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

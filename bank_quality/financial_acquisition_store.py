"""Small transactional operational ledger; no HTTP, worker or data admission.

Pending attempts retain their full reservations after restart. The caller alone
proves worker extinction and external artifacts before finishing an attempt.
SQLite transactions do not cover those artifacts. Use one connection per thread.
"""
from contextlib import contextmanager
import json
import copy
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

    def __init__(self, connection, path):
        self._connection = connection
        self._path = path

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
    def create(cls, path, *, scope, limits, carried_usage, operational_context=None):
        scope = _identifier(scope)
        limits = _budget(limits, positive=True)
        carried_usage = _budget(carried_usage)
        path = _path(path)
        if operational_context is not None:
            from .financial_acquisition_batch import _transactional_member_context
            config = _transactional_member_context(operational_context, path=path, scope=scope, limits=limits)
            expected = {'attempts': config['carry']['attempts'], 'body_bytes': config['carry']['body_bytes'],
                        'attempt_ms': config['carry']['attempt_seconds'] * 1000}
            if carried_usage != expected:
                raise ValueError('Operational carry totals differ')
        for suffix in ('-journal', '-wal', '-shm'):
            sidecar = _path(str(path) + suffix)
            if sidecar.exists():
                raise FileExistsError('New store has an existing SQLite companion')
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
        store = cls(cls._connect(path), path)
        try:
            with store._transaction(write=True):
                store._connection.execute('''CREATE TABLE run_config (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    scope TEXT NOT NULL, limits_json TEXT NOT NULL,
                    carried_usage_json TEXT NOT NULL, operational_context_json TEXT, halt_reason TEXT)''')
                store._connection.execute('''CREATE TABLE attempts (
                    attempt_id TEXT PRIMARY KEY, target TEXT NOT NULL,
                    body_budget_bytes INTEGER NOT NULL, deadline_ms INTEGER NOT NULL,
                    outcome TEXT NOT NULL CHECK(outcome IN ('pending','success','failure')),
                    observed_bytes INTEGER, elapsed_ms INTEGER, result_json TEXT,
                    spec_sha256 TEXT, launcher_identity_json TEXT, native_result_sha256 TEXT,
                    kind TEXT NOT NULL DEFAULT 'request' CHECK(kind IN ('request','backoff')))''')
                store._connection.execute('INSERT INTO run_config VALUES (1, ?, ?, ?, ?, NULL)',
                                          (scope, _json(limits), _json(carried_usage),
                                           _json(operational_context) if operational_context is not None else None))
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
        store = cls(cls._connect(path), path)
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
            if set(config.keys()) != {'singleton', 'scope', 'limits_json', 'carried_usage_json', 'operational_context_json', 'halt_reason'}:
                raise ValueError('Unsupported attempt store configuration schema')
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
            if attempt['kind'] == 'backoff':
                continue
            usage['attempts'] += 1
            usage['body_bytes'] += attempt['body_budget_bytes'] if pending else attempt['observed_bytes']
            usage['attempt_ms'] += attempt['deadline_ms'] if pending else attempt['elapsed_ms']
        state = {'scope': scope, 'limits': limits, 'carried_usage': carry,
                 'usage': usage, 'attempts': attempts}
        context = config['operational_context_json']
        if context is not None:
            from .financial_acquisition_batch import _transactional_member_context
            context = json.loads(context)
            derived = _transactional_member_context(context, path=self._path, scope=scope, limits=limits)
            if carry != {'attempts': derived['carry']['attempts'], 'body_bytes': derived['carry']['body_bytes'],
                         'attempt_ms': derived['carry']['attempt_seconds'] * 1000}:
                raise ValueError('Operational carried totals differ from pinned context')
            state.update(operational_context=context, halt=config['halt_reason'],
                         operational_state=_reduce_attempts(attempts, derived), _derived=derived)
        return state

    def reserve(self, target, *, body_budget_bytes, deadline_ms):
        target = _identifier(target)
        body_budget_bytes = _integer(body_budget_bytes)
        deadline_ms = _integer(deadline_ms, positive=True)
        with self._transaction(write=True):
            state = self._state()
            if 'operational_context' in state:
                raise ValueError('Operational store requires reserve_request')
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
            if (row is None or row['kind'] != 'request' or row['outcome'] != 'pending' or row['spec_sha256'] is not None
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
            state = self._state()
            row = self._connection.execute('SELECT * FROM attempts WHERE attempt_id=?',
                                           (attempt_id,)).fetchone()
            if row is None or row['kind'] != 'request' or row['outcome'] != 'pending':
                raise ValueError('Attempt is absent or already finished')
            if 'operational_context' in state:
                _request_result(result, outcome)
                if 'observed_bytes' in result:
                    if row['spec_sha256'] is None or row['native_result_sha256'] is None:
                        raise ValueError('Physical conclusion requires pinned spec and Native completion')
                    if (result['observed_bytes'] != observed_bytes
                            or result['observed_attempt_seconds'] != (elapsed_ms + 999) // 1000):
                        raise ValueError('Physical conclusion counters differ')
            if observed_bytes > row['body_budget_bytes']:
                raise ValueError('Observed bytes exceed reservation')
            self._connection.execute('''UPDATE attempts SET
                observed_bytes=?, elapsed_ms=?, outcome=?, result_json=? WHERE attempt_id=?''',
                (observed_bytes, elapsed_ms, outcome, result_json, attempt_id))

    def bind_native_result(self, attempt_id, pin):
        """Pin the exclusive Native completion file before a resumable finish."""
        if type(pin) is not str or not re.fullmatch('[0-9a-f]{64}', pin):
            raise ValueError('Native completion requires SHA-256')
        with self._transaction(write=True):
            row = self._connection.execute('SELECT * FROM attempts WHERE attempt_id=?',
                                           (_identifier(attempt_id),)).fetchone()
            if (row is None or row['kind'] != 'request' or row['outcome'] != 'pending'
                    or row['spec_sha256'] is None or row['native_result_sha256'] is not None):
                raise ValueError('Native completion requires a bound pending request')
            self._connection.execute('UPDATE attempts SET native_result_sha256=? WHERE attempt_id=?', (pin, attempt_id))

    def reserve_request(self, target):
        return self._reserve_operational(target, 'request')

    def reserve_backoff(self, target):
        return self._reserve_operational(target, 'backoff')

    def _reserve_operational(self, target, kind):
        target = _identifier(target)
        with self._transaction(write=True):
            state = self._state()
            if 'operational_context' not in state or state['halt'] is not None:
                raise ValueError('Operational context missing or halted')
            derived, current = state['_derived'], state['operational_state']
            if target not in derived['targets']:
                raise ValueError('Target outside installed member')
            policy = derived['policies']
            if kind == 'backoff':
                previous = state['attempts'][-1] if state['attempts'] else None
                if (not previous or previous['kind'] != 'request' or previous['target'] != target
                        or previous['outcome'] != 'failure' or not previous['result']['retryable']):
                    raise ValueError('Backoff requires immediately preceding retryable request failure')
                body, deadline = 0, policy['max_backoff_seconds'] * 1000
            else:
                requests = [r for r in state['attempts'] if r['kind'] == 'request' and r['target'] == target]
                if requests and requests[-1]['outcome'] == 'failure' and requests[-1]['result']['retryable']:
                    last = state['attempts'][-1]
                    if last['kind'] != 'backoff' or last['target'] != target or last['outcome'] != 'success':
                        raise ValueError('Retry requires its durable completed backoff')
                from .financial_acquisition import _body_cap
                body = _body_cap(derived['targets'][target], policy) - current['targets'].get(target, {}).get('body_bytes', 0)
                deadline = policy['deadline_seconds'] * 1000
            attempt_id = uuid.uuid4().hex
            candidate = dict(attempt_id=attempt_id, target=target, kind=kind,
                body_budget_bytes=body, deadline_ms=deadline, outcome='pending',
                observed_bytes=None, elapsed_ms=None, result=None, launcher_identity=None)
            _reduce_attempts(state['attempts'] + [candidate], derived)
            self._connection.execute('''INSERT INTO attempts
                (attempt_id,target,body_budget_bytes,deadline_ms,outcome,kind)
                VALUES (?,?,?,?,'pending',?)''', (attempt_id, target, body, deadline, kind))
        return attempt_id

    def finish_backoff(self, attempt_id, *, elapsed_ms):
        attempt_id, elapsed_ms = _identifier(attempt_id), _integer(elapsed_ms)
        with self._transaction(write=True):
            state = self._state()
            row = next((r for r in state['attempts'] if r['attempt_id'] == attempt_id), None)
            if ('operational_context' not in state or not row or row['kind'] != 'backoff'
                    or row['outcome'] != 'pending'):
                raise ValueError('Unknown or completed operational backoff')
            self._connection.execute('''UPDATE attempts SET outcome='success', observed_bytes=0,
                elapsed_ms=?, result_json='null' WHERE attempt_id=?''', (elapsed_ms, attempt_id))

    def halt(self, reason):
        reason = _identifier(reason)
        with self._transaction(write=True):
            state = self._state()
            if 'operational_context' not in state:
                raise ValueError('Halt requires operational context')
            self._connection.execute('UPDATE run_config SET halt_reason=COALESCE(halt_reason,?) WHERE singleton=1', (reason,))

    def snapshot(self):
        with self._transaction():
            state = self._state()
            state.pop('_derived', None)
            return state

    def close(self):
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _request_result(result, outcome):
    minimal = {'status', 'retryable', 'guard', 'source_ref', 'tree_extinct'}
    physical = minimal | {'observed_bytes', 'observed_attempt_seconds', 'actual_elapsed_microseconds',
                          'overshoot_microseconds', 'attempt_evidence', 'worker_exit_code', 'deadline_reached'}
    if (type(result) is not dict or set(result) not in (minimal, physical)
            or type(result['status']) is not str or not result['status']
            or type(result['retryable']) is not bool or type(result['guard']) is not str
            or result['tree_extinct'] is not True
            or (result['status'] == 'source_complete') != (outcome == 'success')
            or (outcome == 'success' and (type(result['source_ref']) is not dict or result['retryable']))
            or (outcome == 'failure' and result['source_ref'] is not None)):
        raise ValueError('Invalid closed request conclusion')
    if set(result) == physical:
        for name in ('observed_bytes', 'observed_attempt_seconds', 'actual_elapsed_microseconds', 'overshoot_microseconds'):
            _integer(result[name])
        if (type(result['deadline_reached']) is not bool or type(result['worker_exit_code']) is not int
                or type(result['attempt_evidence']) is not dict):
            raise ValueError('Invalid physical evidence fields')


def _reduce_attempts(rows, config):
    """Project SQL rows into ephemeral pure transitions, without journal identity."""
    from .financial_acquisition import _apply_record
    state = copy.deepcopy(config['carry'])
    policy, targets = config['policies'], config['targets']
    def apply(kind, row, **fields):
        record = {'kind': kind, 'attempt_id': row['attempt_id'], 'target_key': row['target'],
                  'attempt_delta': 0, 'reserved_bytes': 0, 'reserved_attempt_seconds': 0,
                  'reserved_backoff_seconds': 0, 'failure_count': state['failures'],
                  'failure_streak': state['failure_streak'], **fields}
        if kind == 'finish':
            if record['status'] == 'source_complete':
                record['failure_streak'] = 0
            else:
                record['failure_count'] += 1
                record['failure_streak'] += 1
        _apply_record(state, record, targets, policy, job_contract='financial-acquisition-job-v2')
    for row in rows:
        if row['kind'] == 'request':
            apply('reserve', row, attempt_delta=1, reserved_bytes=row['body_budget_bytes'],
                  reserved_attempt_seconds=(row['deadline_ms'] + 999) // 1000)
            if row['launcher_identity'] is not None:
                apply('identity', row, identity=row['launcher_identity'])
            if row['outcome'] != 'pending':
                _request_result(row['result'], row['outcome'])
                apply('finish', row, **{**row['result'], 'observed_bytes': row['observed_bytes'],
                      'observed_attempt_seconds': (row['elapsed_ms'] + 999) // 1000})
        elif row['kind'] == 'backoff':
            apply('backoff', row, reserved_backoff_seconds=(row['deadline_ms'] + 999) // 1000)
            if row['outcome'] != 'pending':
                apply('backoff_finish', row, observed_backoff_seconds=(row['elapsed_ms'] + 999) // 1000)
        else:
            raise ValueError('Unknown SQL attempt kind')
    return state

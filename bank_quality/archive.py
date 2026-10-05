"""Immutable acquisition evidence. Interpretation happens only after archiving."""

import hashlib
import json
import math
import re
import time
import uuid
from datetime import datetime, timezone
from http.client import HTTPConnection, HTTPException, HTTPResponse, HTTPSConnection, IncompleteRead
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qsl, urlsplit
from urllib.request import HTTPHandler, HTTPRedirectHandler, HTTPSHandler, Request, build_opener, urlopen

MAX_BYTES = 64 * 1024 * 1024


class _NoRedirect(HTTPRedirectHandler):
    def http_error_302(self, request, response, code, message, headers):
        raise HTTPError(request.full_url, code, message, headers, response)

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


class _ArchiveWriteError(OSError):
    pass


class _StrictHTTPResponse(HTTPResponse):
    """Fail closed where CPython's chunk parser tolerates missing framing.

    Localized to the opt-in transport, with the stdlib header limits mirrored
    for chunk lines/trailers (64 KiB per line, 100 trailer fields).
    """
    def _read_next_chunk_size(self):
        line = self.fp.readline(65537)
        if len(line) > 65536 or not re.fullmatch(rb'[0-9a-fA-F]+(?:;[^\r\n]*)?\r\n', line):
            raise IncompleteRead(b'')
        return int(line.split(b';', 1)[0].strip(), 16)

    def _read_and_discard_trailer(self):
        for _ in range(101):
            line = self.fp.readline(65537)
            if line == b'\r\n':
                return
            if (len(line) > 65536 or not line.endswith(b'\r\n')
                    or b':' not in line):
                raise IncompleteRead(b'')
        raise IncompleteRead(b'')

    def _get_chunk_left(self):
        chunk_left = self.chunk_left
        if not chunk_left:
            if chunk_left is not None:
                try:
                    delimiter = self._safe_read(2)
                except IncompleteRead:
                    # Framing bytes are not entity bytes in partial evidence.
                    raise IncompleteRead(b'') from None
                if delimiter != b'\r\n':
                    raise IncompleteRead(b'')
            chunk_left = self._read_next_chunk_size()
            if chunk_left == 0:
                self._read_and_discard_trailer()
                self._close_conn()
                chunk_left = None
            self.chunk_left = chunk_left
        return chunk_left


class _BoundedHTTPConnection(HTTPConnection):
    response_class = _StrictHTTPResponse


class _BoundedHTTPSConnection(HTTPSConnection):
    response_class = _StrictHTTPResponse


class _BoundedHTTPHandler(HTTPHandler):
    def http_open(self, request):
        return self.do_open(_BoundedHTTPConnection, request)


class _BoundedHTTPSHandler(HTTPSHandler):
    def https_open(self, request):
        return self.do_open(_BoundedHTTPSConnection, request, context=self._context)


def _bounded_framing_finished(response, content_length, observed):
    # HTTPError wraps HTTPResponse; its own close state is not framing proof.
    framed = response.fp if isinstance(response, HTTPError) else response
    return (content_length is not None and observed == content_length
            and getattr(framed, 'length', None) == 0
            and callable(getattr(framed, 'isclosed', None)) and framed.isclosed())


def fetch_bounded(url: str, root: Path, label: str, context: dict, *,
                  body_budget_bytes: int, timeout_seconds: float = 30) -> dict:
    """Archive an opt-in bounded attempt without accepting incomplete framing.

    The cap covers response entity bytes, not headers or HTTP framing bytes.
    Socket timeout is not a process deadline. Exact-cap EOF cannot be probed;
    only completed, coherent Content-Length framing can prove that boundary.
    """
    if (type(body_budget_bytes) is not int or body_budget_bytes <= 0
            or not isinstance(timeout_seconds, (int, float))
            or isinstance(timeout_seconds, bool) or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0):
        raise ValueError('Positive integer body budget and finite positive timeout required')
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    timer = time.monotonic()
    safe_label = re.sub(r'[^a-zA-Z0-9_-]', '_', label)[:100]
    stem = f'{started.strftime("%Y%m%dT%H%M%S%fZ")}_{safe_label}_{uuid.uuid4().hex}'
    item = {
        'contract': 'bounded-http-archive-v1', 'url': url, 'method': 'GET',
        'final_url': None,
        'query_parameters': [list(pair) for pair in parse_qsl(urlsplit(url).query, keep_blank_values=True)],
        'context': context, 'started_at_utc': started.isoformat(),
        'http_status': None, 'response_headers_raw': [], 'response_headers': {},
        'diagnostics': [], 'outcome': 'network_error', 'source_complete': False,
        'truncated': False, 'eof_observed': False, 'completion_basis': None,
        'content_length': None, 'body_budget_bytes': body_budget_bytes,
        'bytes_observed': 0, 'bytes': 0, 'sha256': hashlib.sha256(b'').hexdigest(),
        'body_path': stem + '.bin', 'manifest_path': stem + '.json',
        'response_metadata_path': None, 'response_metadata_sha256': None,
        'body_available': False,
    }
    digest = hashlib.sha256()

    def diagnostic(code, detail):
        item['diagnostics'].append({'code': code, 'detail': detail})

    def store(output, body):
        item['bytes_observed'] += len(body)
        try:
            written = output.write(body)
        except OSError as error:
            raise _ArchiveWriteError(str(error)) from error
        digest.update(body[:written])
        item['bytes'] += written
        if written != len(body):
            raise _ArchiveWriteError('Short body file write')

    try:
        with (root / item['body_path']).open('xb') as output:
            item['body_available'] = True
            request = Request(url, headers={'User-Agent': 'BrazilianBanksDataQualityPilot/0.1',
                                            'Accept-Encoding': 'identity'})
            try:
                try:
                    response = build_opener(_NoRedirect(), _BoundedHTTPHandler(),
                                            _BoundedHTTPSHandler()).open(request, timeout=timeout_seconds)
                except HTTPError as error:
                    response = error
                with response:
                    item['http_status'] = response.status
                    item['final_url'] = response.geturl()
                    raw_items = getattr(response.headers, 'raw_items', response.headers.items)
                    item['response_headers_raw'] = [list(pair) for pair in raw_items()]
                    # Preserve the original header list before projection or body reading.
                    metadata_path = stem + '.response.json'
                    metadata = {key: item[key] for key in (
                        'url', 'method', 'final_url', 'context', 'started_at_utc',
                        'http_status', 'response_headers_raw')}
                    try:
                        with (root / metadata_path).open('x', encoding='utf-8') as metadata_file:
                            json.dump(metadata, metadata_file, ensure_ascii=False, indent=2)
                        metadata_digest = hashlib.sha256()
                        with (root / metadata_path).open('rb') as metadata_file:
                            for chunk in iter(lambda: metadata_file.read(64 * 1024), b''):
                                metadata_digest.update(chunk)
                    except OSError as error:
                        raise _ArchiveWriteError(str(error)) from error
                    item['response_metadata_path'] = metadata_path
                    item['response_metadata_sha256'] = metadata_digest.hexdigest()
                    item['response_headers'] = dict(item['response_headers_raw'])
                    headers = {}
                    for name, value in item['response_headers_raw']:
                        headers.setdefault(name.lower(), []).append(value.strip())
                    lengths = headers.get('content-length', [])
                    if lengths:
                        if len(lengths) != 1 or not re.fullmatch(r'[0-9]+', lengths[0]):
                            diagnostic('invalid_content_length', 'Content-Length must be unique and unsigned decimal')
                        else:
                            item['content_length'] = int(lengths[0])
                    transfers = headers.get('transfer-encoding', [])
                    if transfers and (lengths or transfers != ['chunked']):
                        diagnostic('ambiguous_framing', 'Unsupported or conflicting Transfer-Encoding/Content-Length')
                    encodings = headers.get('content-encoding', [])
                    if encodings and encodings != ['identity']:
                        diagnostic('unexpected_content_encoding', 'Only identity Content-Encoding is supported')
                    if item['final_url'] != url:
                        diagnostic('final_url_mismatch', 'Final URL differs from requested URL')
                    if response.status != 200:
                        diagnostic('http_status', f'HTTP {response.status}; body preserved without acceptance')
                    while item['bytes_observed'] < body_budget_bytes:
                        remaining = body_budget_bytes - item['bytes_observed']
                        amount = min(64 * 1024, remaining)
                        try:
                            body = response.read(amount)
                        except IncompleteRead as error:
                            # CPython 3.12 chunked reads put the failing chunk's
                            # partial bytes in the cause, previous chunks in partial.
                            partials = []
                            current = error
                            while isinstance(current, IncompleteRead):
                                partials.append(current.partial)
                                current = current.__cause__
                            body = b''.join(partials)
                            if len(body) > remaining:
                                diagnostic('read_exceeded_budget', 'Response surfaced more bytes than requested')
                                body = body[:remaining]
                            store(output, body)
                            diagnostic('incomplete_read', str(error))
                            break
                        if len(body) > amount:
                            diagnostic('read_exceeded_budget', 'Response surfaced more bytes than requested')
                            store(output, body[:remaining])
                            break
                        if not body:
                            item['eof_observed'] = True
                            item['completion_basis'] = 'chunked_eof' if transfers == ['chunked'] else 'eof'
                            break
                        store(output, body)
                        if not transfers and _bounded_framing_finished(response, item['content_length'], item['bytes_observed']):
                            item['completion_basis'] = 'content_length'
                            break
                    if (item['bytes_observed'] == body_budget_bytes
                            and item['completion_basis'] is None):
                        item['truncated'] = True
                        diagnostic('body_budget_exhausted', 'Budget reached without proven EOF/framing completion')
                    if (item['content_length'] is not None
                            and item['bytes_observed'] != item['content_length']):
                        diagnostic('content_length_mismatch', 'Observed body bytes differ from declared Content-Length')
                    if item['completion_basis'] is None and not item['diagnostics']:
                        diagnostic('incomplete_framing', 'No positive framing completion evidence')
                    item['source_complete'] = item['completion_basis'] is not None and not item['diagnostics']
                    item['outcome'] = ('http_error' if response.status != 200 else
                                       'ok' if item['source_complete'] else 'transport_error')
            except _ArchiveWriteError:
                raise
            except HTTPException as error:
                item['source_complete'] = False
                item['outcome'] = 'transport_error'
                code = 'response_headers_error' if item['http_status'] is None else 'framing_error'
                diagnostic(code, f'{type(error).__name__}: {error}')
            except Exception as error:
                item['source_complete'] = False
                item['outcome'] = 'network_error' if item['http_status'] is None else 'transport_error'
                diagnostic('transport_exception', f'{type(error).__name__}: {error}')
    except OSError as error:
        item['source_complete'] = False
        item['outcome'] = 'storage_error'
        diagnostic('storage_error', f'{type(error).__name__}: {error}')
        # A failed/partial write may have changed the file. Authenticate only
        # bytes actually readable after close, never claim the intended digest.
        try:
            digest = hashlib.sha256()
            item['bytes'] = 0
            with (root / item['body_path']).open('rb') as saved:
                for body in iter(lambda: saved.read(64 * 1024), b''):
                    digest.update(body)
                    item['bytes'] += len(body)
            item['body_available'] = True
        except OSError:
            item['body_available'] = False
            item['sha256'] = None
    if item['body_available']:
        item['sha256'] = digest.hexdigest()
    item['retrieved_at_utc'] = datetime.now(timezone.utc).isoformat()
    item['elapsed_seconds'] = round(time.monotonic() - timer, 6)
    # Failure here raises: an attempt without a durable manifest is never ok.
    with (root / item['manifest_path']).open('x', encoding='utf-8') as manifest:
        json.dump(item, manifest, ensure_ascii=False, indent=2)
    return item


def fetch(url: str, root: Path, label: str, context: dict | None = None,
          timeout: float = 30) -> dict:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    timer = time.monotonic()
    item = {
        'url': url, 'method': 'GET', 'final_url': None,
        'query_parameters': [list(pair) for pair in parse_qsl(urlsplit(url).query, keep_blank_values=True)],
        'context': context or {}, 'started_at_utc': started.isoformat(),
        'http_status': None, 'response_headers': {}, 'diagnostics': [],
        'outcome': 'network_error', 'truncated': False,
    }
    body = b''
    try:
        request = Request(url, headers={'User-Agent': 'BrazilianBanksDataQualityPilot/0.1',
                                        'Accept-Encoding': 'identity'})
        try:
            response = urlopen(request, timeout=timeout)
        except HTTPError as error:
            response = error
        with response:
            item['http_status'] = response.status
            item['final_url'] = response.geturl()
            item['response_headers'] = dict(response.headers.items())
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                item['truncated'] = True
                item['diagnostics'].append('Response exceeded 64 MiB; truncated body is NOT an accepted dataset.')
            item['outcome'] = ('ok' if response.status == 200 and not item['truncated'] else 'http_error')
            if response.status != 200:
                item['diagnostics'].append(f'HTTP {response.status}; body retained without dataset acceptance.')
    except Exception as error:
        item['diagnostics'].append(f'{type(error).__name__}: {error}')
    item['retrieved_at_utc'] = datetime.now(timezone.utc).isoformat()
    item['elapsed_seconds'] = round(time.monotonic() - timer, 6)
    item['bytes'] = len(body)
    item['sha256'] = hashlib.sha256(body).hexdigest()
    safe_label = re.sub(r'[^a-zA-Z0-9_-]', '_', label)[:100]
    stem = f'{started.strftime("%Y%m%dT%H%M%S%fZ")}_{safe_label}_{uuid.uuid4().hex}'
    item['body_path'] = stem + '.bin'
    item['manifest_path'] = stem + '.json'
    with (root / item['body_path']).open('xb') as output:
        output.write(body)
    with (root / item['manifest_path']).open('x', encoding='utf-8') as output:
        json.dump(item, output, ensure_ascii=False, indent=2)
    return item


def load_body(manifest: dict, root: Path) -> bytes:
    body = (Path(root) / manifest['body_path']).read_bytes()
    if hashlib.sha256(body).hexdigest() != manifest['sha256']:
        raise ValueError('Archived body hash mismatch: ' + manifest['body_path'])
    return body


def preserve_generated(body: bytes, root: Path, label: str, source_url: str,
                       kind: str, context: dict | None = None) -> dict:
    """Archive browser-generated evidence without inventing an HTTP response."""
    root=Path(root); root.mkdir(parents=True,exist_ok=True)
    now=datetime.now(timezone.utc).isoformat()
    stem=re.sub(r'[^a-zA-Z0-9_-]','_',label)[:100]+'_'+uuid.uuid4().hex
    item={'url':source_url,'final_url':source_url,'method':'browser_export',
          'query_parameters':[list(p) for p in parse_qsl(urlsplit(source_url).query,keep_blank_values=True)],
          'context':context or {},'retrieved_at_utc':now,'http_status':None,'response_headers':{},
          'kind':kind,'outcome':'generated_evidence','diagnostics':['Generated by the official portal; not an HTTP response.'],
          'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'body_path':stem+'.bin','manifest_path':stem+'.json'}
    with (root/item['body_path']).open('xb') as out: out.write(body)
    with (root/item['manifest_path']).open('x',encoding='utf-8') as out: json.dump(item,out,ensure_ascii=False,indent=2)
    return item

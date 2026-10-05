import hashlib
import json
import tempfile
import threading
import unittest
from email.message import Message
from http.client import IncompleteRead
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from bank_quality import archive
from bank_quality.archive import fetch, load_body


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'NA;NI;null;0\r\n' if not self.path.startswith('/error') else b'{"error":"upstream"}'
        self.send_response(500 if self.path.startswith('/error') else 200)
        self.send_header('Content-Type', 'text/csv')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class ArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_exact_bytes_hash_parameters_and_endpoint_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            url = self.base + '/data?@AnoMes=201012&$format=json'
            item = fetch(url, root, 'cadastro', {'period': 201012})
            self.assertEqual(load_body(item, root), b'NA;NI;null;0\r\n')
            self.assertEqual(item['sha256'], hashlib.sha256(b'NA;NI;null;0\r\n').hexdigest())
            self.assertEqual(item['url'], url)
            self.assertEqual(item['query_parameters'], [['@AnoMes', '201012'], ['$format', 'json']])
            self.assertEqual(item['context']['period'], 201012)
            self.assertEqual(item['http_status'], 200)
            self.assertTrue(item['retrieved_at_utc'].endswith('+00:00'))
            self.assertEqual(json.loads((root / item['manifest_path']).read_text())['sha256'], item['sha256'])

    def test_failure_body_is_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = fetch(self.base + '/error', root, 'failure')
            self.assertEqual(item['http_status'], 500)
            self.assertEqual(item['outcome'], 'http_error')
            self.assertEqual(load_body(item, root), b'{"error":"upstream"}')

    def test_repeated_request_cannot_overwrite_first_body(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = fetch(self.base, root, 'same')
            second = fetch(self.base, root, 'same')
            self.assertNotEqual(first['body_path'], second['body_path'])
            self.assertEqual(load_body(first, root), load_body(second, root))

    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = fetch(self.base, root, 'tamper')
            (root / item['body_path']).write_bytes(b'changed')
            with self.assertRaises(ValueError):
                load_body(item, root)

    def test_generated_export_is_labeled_and_has_no_invented_http_status(self):
        from bank_quality.archive import preserve_generated
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            item=preserve_generated(b'official csv bytes',root,'csv','https://www3.bcb.gov.br/ifdata/index2024.html',
                                    'official_portal_csv',{'period':201012})
            self.assertIsNone(item['http_status'])
            self.assertEqual(item['kind'],'official_portal_csv')
            self.assertEqual(load_body(item,root),b'official csv bytes')


class BoundedHandler(BaseHTTPRequestHandler):
    targets = 0

    def do_GET(self):
        if self.path == '/target':
            type(self).targets += 1
        body = b'{"a":1}'
        self.send_response(302 if self.path == '/redirect' else 503 if self.path == '/failure' else 200)
        if self.path == '/redirect':
            self.send_header('Location', '/target')
        if self.path == '/short':
            self.send_header('Content-Length', str(len(body) + 10))
        elif self.path == '/duplicate':
            self.send_header('Content-Length', str(len(body)))
            self.send_header('content-length', str(len(body)))
        elif self.path == '/invalid':
            self.send_header('Content-Length', 'invalid')
        elif self.path.startswith('/chunked') or self.path == '/ambiguous':
            self.send_header('Transfer-Encoding', 'chunked')
            if self.path == '/ambiguous':
                self.send_header('Content-Length', str(len(body)))
        elif self.path != '/no-length':
            self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Duplicate', 'first')
        self.send_header('X-Duplicate', 'second')
        if self.path == '/headers-many':
            for index in range(101):
                self.send_header(f'X-{index}', 'fixture')
        if self.path == '/encoding':
            self.send_header('Content-Encoding', 'gzip')
        self.end_headers()
        if self.path in ('/chunked', '/ambiguous'):
            self.wfile.write(b'7\r\n' + body + b'\r\n0\r\n\r\n')
        elif self.path == '/chunked-short':
            self.wfile.write(b'7\r\n' + body + b'\r\n')
        elif self.path == '/chunked-trailer-short':
            self.wfile.write(b'7\r\n' + body + b'\r\n0\r\n')
        elif self.path == '/chunked-delimiter-bad':
            self.wfile.write(b'7\r\n' + body + b'XX0\r\n\r\n')
        elif self.path == '/chunked-delimiter-short':
            self.wfile.write(b'7\r\n' + body + b'\r')
        elif self.path == '/chunked-size-lf':
            self.wfile.write(b'7\n' + body + b'\r\n0\r\n\r\n')
        elif self.path == '/chunked-trailer-many':
            self.wfile.write(b'7\r\n' + body + b'\r\n0\r\n' + b'X: 1\r\n' * 101 + b'\r\n')
        elif self.path == '/chunked-trailer-long':
            self.wfile.write(b'7\r\n' + body + b'\r\n0\r\nX: ' + b'a' * 65536 + b'\r\n\r\n')
        else:
            self.wfile.write(body)

    def log_message(self, *args):
        pass


class FakeBoundedResponse:
    status = 200

    def __init__(self, reads, headers=(), *, length=None, closed=False):
        self.headers = Message()
        for name, value in headers:
            self.headers[name] = value
        self.reads = iter(reads)
        self.requests = []
        self.length = length
        self.closed = closed

    def geturl(self):
        return 'http://127.0.0.1/fake'

    def read(self, amount):
        self.requests.append(amount)
        value = next(self.reads)
        if isinstance(value, Exception):
            raise value
        return value

    def isclosed(self):
        return self.closed

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class BoundedArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), BoundedHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def fetch(self, path='/complete', budget=100):
        self.assertTrue(callable(getattr(archive, 'fetch_bounded', None)),
                        'opt-in fetch_bounded transport is missing')
        return archive.fetch_bounded(self.base + path, self.root, 'bounded',
                                     {'period': 202403}, body_budget_bytes=budget)

    def fake_fetch(self, response, budget=100):
        self.assertTrue(callable(getattr(archive, 'fetch_bounded', None)),
                        'opt-in fetch_bounded transport is missing')
        with patch('bank_quality.archive.build_opener') as opener:
            opener.return_value.open.return_value = response
            item = archive.fetch_bounded(response.geturl(), self.root, 'fake', {},
                                         body_budget_bytes=budget)
        return item

    def test_complete_body(self):
        item = self.fetch()
        self.assertEqual(item['outcome'], 'ok')
        self.assertTrue(item['source_complete'])
        self.assertEqual(load_body(item, self.root), b'{"a":1}')
        self.assertEqual(item['bytes_observed'], 7)
        self.assertEqual(item['response_headers_raw'][-2:],
                         [['X-Duplicate', 'first'], ['X-Duplicate', 'second']])
        metadata = json.loads((self.root / item['response_metadata_path']).read_text())
        self.assertEqual(metadata['response_headers_raw'], item['response_headers_raw'])
        self.assertIn('response_metadata_sha256', item)
        self.assertEqual(item['response_metadata_sha256'], hashlib.sha256(
            (self.root / item['response_metadata_path']).read_bytes()).hexdigest())

    def test_valid_json_shorter_than_content_length(self):
        item = self.fetch('/short')
        self.assertEqual(json.loads(load_body(item, self.root)), {'a': 1})
        self.assertFalse(item['source_complete'])
        self.assertEqual(item['outcome'], 'transport_error')
        self.assertIn('content_length_mismatch', [d['code'] for d in item['diagnostics']])

    def test_response_metadata_is_exclusive_and_authenticated(self):
        first = self.fetch()
        saved = (self.root / first['response_metadata_path']).read_bytes()
        second = self.fetch()
        self.assertNotEqual(first['response_metadata_path'], second['response_metadata_path'])
        self.assertEqual((self.root / first['response_metadata_path']).read_bytes(), saved)
        self.assertEqual(first['response_metadata_sha256'], hashlib.sha256(saved).hexdigest())
        self.assertFalse(Path(first['response_metadata_path']).is_absolute())

    def test_response_header_limit_diagnostic(self):
        item = self.fetch('/headers-many')
        self.assertFalse(item['source_complete'])
        self.assertIsNone(item['response_metadata_path'])
        self.assertEqual(item['bytes_observed'], 0)
        self.assertIn('response_headers_error', [d['code'] for d in item['diagnostics']])

    def test_duplicate_or_invalid_content_length(self):
        for path in ('/duplicate', '/invalid'):
            with self.subTest(path=path):
                item = self.fetch(path)
                self.assertFalse(item['source_complete'])
                self.assertEqual(load_body(item, self.root), b'{"a":1}')
                self.assertIn('invalid_content_length', [d['code'] for d in item['diagnostics']])

    def test_missing_length_requires_eof(self):
        item = self.fetch('/no-length')
        self.assertEqual(item['outcome'], 'ok')
        self.assertTrue(item['eof_observed'])
        self.assertEqual(item['completion_basis'], 'eof')
        self.assertIsNone(item['content_length'])

    def test_chunked_complete(self):
        item = self.fetch('/chunked')
        self.assertEqual(item['outcome'], 'ok')
        self.assertTrue(item['eof_observed'])
        self.assertEqual(item['completion_basis'], 'chunked_eof')

    def test_chunked_incomplete(self):
        item = self.fetch('/chunked-short')
        self.assertFalse(item['source_complete'])
        self.assertEqual(load_body(item, self.root), b'{"a":1}')
        self.assertIn('incomplete_read', [d['code'] for d in item['diagnostics']])

    def test_chunked_trailer_incomplete(self):
        item = self.fetch('/chunked-trailer-short')
        self.assertFalse(item['source_complete'])
        self.assertEqual(load_body(item, self.root), b'{"a":1}')

    def test_chunked_delimiter_malformed(self):
        item = self.fetch('/chunked-delimiter-bad')
        self.assertFalse(item['source_complete'])
        self.assertEqual(load_body(item, self.root), b'{"a":1}')

    def test_partial_chunk_delimiter_not_body(self):
        item = self.fetch('/chunked-delimiter-short')
        self.assertFalse(item['source_complete'])
        self.assertEqual(load_body(item, self.root), b'{"a":1}')

    def test_chunked_size_requires_crlf(self):
        item = self.fetch('/chunked-size-lf')
        self.assertFalse(item['source_complete'])

    def test_chunked_trailer_count_and_line_bounded(self):
        for path in ('/chunked-trailer-many', '/chunked-trailer-long'):
            with self.subTest(path=path):
                item = self.fetch(path)
                self.assertFalse(item['source_complete'])

    def test_partial_chunk_body_preserved(self):
        # A malformed chunk can fail inside the current chunk, before it joins
        # HTTPResponse's completed-chunk buffer.
        response = FakeBoundedResponse([IncompleteRead(b'123', 4)])
        item = self.fake_fetch(response, budget=7)
        self.assertEqual(load_body(item, self.root), b'123')
        self.assertEqual(item['outcome'], 'transport_error')

    def test_cap_without_eof_rejected(self):
        for path in ('/no-length', '/chunked'):
            with self.subTest(path=path):
                item = self.fetch(path, budget=7)
                self.assertFalse(item['source_complete'])
                self.assertFalse(item['eof_observed'])
                self.assertEqual(item['bytes'], 7)
                self.assertIn('body_budget_exhausted', [d['code'] for d in item['diagnostics']])

    def test_exact_cap_content_length_with_framing_complete(self):
        item = self.fetch(budget=7)
        self.assertEqual(item['outcome'], 'ok')
        self.assertFalse(item['eof_observed'])
        self.assertEqual(item['completion_basis'], 'content_length')

    def test_exact_cap_content_length_without_framing_rejected(self):
        response = FakeBoundedResponse([b'123'], [('Content-Length', '3')], length=0)
        item = self.fake_fetch(response, budget=3)
        self.assertFalse(item['source_complete'])
        self.assertEqual(response.requests, [3])

    def test_no_read_beyond_cap(self):
        response = FakeBoundedResponse([b'123'])
        item = self.fake_fetch(response, budget=3)
        self.assertEqual(response.requests, [3])
        self.assertEqual(load_body(item, self.root), b'123')
        self.assertTrue(item['truncated'])

    def test_redirect_target_never_contacted(self):
        before = BoundedHandler.targets
        item = self.fetch('/redirect')
        self.assertEqual(BoundedHandler.targets, before)
        self.assertEqual(item['http_status'], 302)
        self.assertEqual(item['outcome'], 'http_error')
        self.assertEqual(load_body(item, self.root), b'{"a":1}')

    def test_http_failure_preserved(self):
        item = self.fetch('/failure')
        self.assertEqual(item['http_status'], 503)
        self.assertEqual(item['outcome'], 'http_error')
        self.assertEqual(load_body(item, self.root), b'{"a":1}')

    def test_unexpected_encoding(self):
        item = self.fetch('/encoding')
        self.assertEqual(item['outcome'], 'transport_error')
        self.assertEqual(load_body(item, self.root), b'{"a":1}')
        self.assertIn('unexpected_content_encoding', [d['code'] for d in item['diagnostics']])

    def test_ambiguous_length_transfer_encoding(self):
        item = self.fetch('/ambiguous')
        self.assertFalse(item['source_complete'])
        self.assertIn('ambiguous_framing', [d['code'] for d in item['diagnostics']])

    def test_incomplete_read_partial_preserved(self):
        response = FakeBoundedResponse([IncompleteRead(b'partial', 10)])
        item = self.fake_fetch(response)
        self.assertEqual(load_body(item, self.root), b'partial')
        self.assertEqual(item['bytes_observed'], 7)
        self.assertEqual(item['outcome'], 'transport_error')

    def test_incomplete_chunk_partial_cause_preserved(self):
        error = IncompleteRead(b'first')
        error.__cause__ = IncompleteRead(b'next', 10)
        item = self.fake_fetch(FakeBoundedResponse([error]))
        self.assertEqual(load_body(item, self.root), b'firstnext')

    def test_write_failure_not_ok(self):
        original_open = Path.open

        def failing_open(path, mode='r', *args, **kwargs):
            if mode == 'xb':
                raise OSError('disk fixture failure')
            return original_open(path, mode, *args, **kwargs)

        self.assertTrue(callable(getattr(archive, 'fetch_bounded', None)),
                        'opt-in fetch_bounded transport is missing')
        with patch.object(Path, 'open', failing_open):
            item = self.fetch()
        self.assertEqual(item['outcome'], 'storage_error')
        self.assertFalse(item['source_complete'])
        self.assertIn('storage_error', [d['code'] for d in item['diagnostics']])

    def test_partial_write_hashes_only_persisted_bytes(self):
        original_open = Path.open

        class PartialWriteFile:
            def __init__(self, file):
                self.file = file

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.file.close()

            def write(self, body):
                self.file.write(body[:2])
                raise OSError('partial write fixture')

        def partial_open(path, mode='r', *args, **kwargs):
            file = original_open(path, mode, *args, **kwargs)
            return PartialWriteFile(file) if mode == 'xb' else file

        with patch.object(Path, 'open', partial_open):
            item = self.fetch()
        self.assertEqual(item['outcome'], 'storage_error')
        self.assertFalse(item['source_complete'])
        self.assertEqual(item['bytes_observed'], 7)
        self.assertEqual(item['bytes'], 2)
        self.assertEqual(load_body(item, self.root), b'{"')


if __name__ == '__main__':
    unittest.main()

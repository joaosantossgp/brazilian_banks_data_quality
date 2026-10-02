import hashlib
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

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


if __name__ == '__main__':
    unittest.main()

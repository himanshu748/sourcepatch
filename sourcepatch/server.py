"""Loopback-only HTTP UI; no accounts, persistent storage, or source-file writes."""
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading

from .engine import analyze, export_review, discover, verify_candidate
from .fixtures import SAMPLE

ROOT = Path(__file__).resolve().parent.parent
MAX_BODY = 800_000


def make_server(port=8765, mode='fixture', search=None, process_search_budget=8):
    if mode not in ('fixture', 'live') or mode == 'live' and not callable(search):
        raise ValueError('Live server requires an explicit search provider.')
    if type(process_search_budget) is not int or not 1 <= process_search_budget <= 8:
        raise ValueError('Search budget must be an integer from 1 through 8.')
    sessions = OrderedDict()
    session_lock = threading.Lock()
    analysis_gate = threading.BoundedSemaphore(1)
    verification_calls = 0

    class Handler(BaseHTTPRequestHandler):
        server_version = 'SourcePatch/0.1'
        sys_version = ''

        def log_message(self, *_args):
            pass

        def _allowed(self):
            origins = {f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'}
            hosts = {origin.removeprefix('http://') for origin in origins}
            if (self.headers.get('Host') not in hosts
                    or self.headers.get('Origin') is not None and self.headers.get('Origin') not in origins
                    or self.headers.get('Sec-Fetch-Site') == 'cross-site'):
                self._json(403, {'error': 'Only this local workbench may access the server.'})
                return False
            return True

        def _send(self, status, data, content_type):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'; connect-src 'self'; img-src 'self' data:")
            self.end_headers()
            self.wfile.write(data)

        def _json(self, status, value):
            self._send(status, json.dumps(value, ensure_ascii=False).encode('utf-8'), 'application/json; charset=utf-8')

        def do_GET(self):
            if not self._allowed():
                return
            if self.path == '/api/config':
                self._json(200, {'mode': mode, 'sample': SAMPLE, 'max_source': 200_000,
                                 'search_budget': 8, 'process_search_budget': process_search_budget,
                                 'evidence_version': 2, 'verification_budget': 20, 'process_verification_budget': 64})
                return
            files = {'/': ('index.html', 'text/html'), '/style.css': ('style.css', 'text/css'), '/app.js': ('app.js', 'application/javascript')}
            if self.path not in files:
                self._json(404, {'error': 'Page not found.'})
                return
            name, mime = files[self.path]
            self._send(200, (ROOT / 'web' / name).read_bytes(), mime + '; charset=utf-8')

        def do_OPTIONS(self):
            self._json(405, {'error': 'Cross-origin API access is not supported.'})

        def do_POST(self):
            if not self._allowed():
                return
            if self.path not in ('/api/analyze', '/api/export', '/api/discover', '/api/candidates/verify'):
                self._json(404, {'error': 'Endpoint not found.'})
                return
            if self.headers.get('Content-Type', '').split(';')[0].strip().lower() != 'application/json':
                self._json(415, {'error': 'Send application/json.'})
                return
            try:
                raw_length = self.headers.get('Content-Length', '')
                if not raw_length.isdigit():
                    raise ValueError('A valid Content-Length is required.')
                length = int(raw_length)
                if length > MAX_BODY:
                    self._json(413, {'error': 'Document request is too large.'})
                    return
                self.connection.settimeout(5)
                data = json.loads(self.rfile.read(length).decode('utf-8'))
                if not isinstance(data, dict):
                    raise ValueError('Expected a JSON object.')
                if not analysis_gate.acquire(blocking=False):
                    self._json(429, {'error': 'An inspection is already running. Wait for it to finish.'})
                    return
                try:
                    self._operation(data)
                finally:
                    analysis_gate.release()
            except (ValueError, UnicodeError) as error:
                self._json(400, {'error': str(error) if not isinstance(error, json.JSONDecodeError) else 'Invalid JSON request.'})
            except (OSError, TimeoutError):
                self._json(408, {'error': 'Request timed out. Try again.'})

        def _operation(self, data):
            nonlocal verification_calls
            if self.path == '/api/analyze':
                source = data.get('source')
                if not isinstance(source, str) or len(source) > 200_000:
                    raise ValueError('Markdown must be text of at most 200,000 characters.')
                result = analyze(source, mode=mode, search=search)
                aid = secrets.token_hex(16)
                with session_lock:
                    sessions[aid] = (source, result)
                    while len(sessions) > 8:
                        sessions.popitem(last=False)
            else:
                aid = data.get('analysis_id')
                if not isinstance(aid, str) or len(aid) > 64:
                    raise ValueError('A valid analysis ID is required.')
                with session_lock:
                    session = sessions.get(aid)
                if session is None:
                    self._json(409, {'error': 'Analysis expired or is missing. Inspect the document again.'})
                    return
                source, result = session
                if self.path == '/api/export':
                    self._json(200, export_review(source, result, data.get('decisions')))
                    return
                fields = {'analysis_id', 'citation_id', 'strategy' if self.path == '/api/discover' else 'candidate_id'}
                if set(data) != fields:
                    raise ValueError('Send only the required analysis, citation and strategy/candidate IDs; URLs are not accepted.')
                if self.path == '/api/discover':
                    discover(result, data['citation_id'], data['strategy'], search=search)
                else:
                    existing = next((candidate for citation in result['citations'] if citation['id'] == data['citation_id']
                                     for candidate in citation['candidates'] if candidate['id'] == data['candidate_id']), None)
                    if existing is None:
                        raise ValueError('Only candidates already in this server-owned analysis can be inspected.')
                    if not existing.get('evidence'):
                        if verification_calls >= 64:
                            self._json(429, {'error': 'Process candidate inspection budget reached (64). No request made.'})
                            return
                        verification_calls += 1
                    verify_candidate(result, data['citation_id'], data['candidate_id'])
            self._json(200, {**result, 'analysis_id': aid})

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)

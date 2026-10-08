import http.client
import json
import threading
import unittest
from sourcepatch.server import make_server
from sourcepatch.fixtures import SAMPLE

class V2ServerTests(unittest.TestCase):
    def setUp(self):
        self.server = make_server(port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
    def post(self, path, data):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        conn.request('POST', path, json.dumps(data), {'Content-Type': 'application/json'})
        response = conn.getresponse(); status = response.status; data = json.loads(response.read()); conn.close()
        return status, data
    def test_full_roundtrip_only_stored_ids(self):
        _, a = self.post('/api/analyze', {'source': SAMPLE})
        c = a['citations'][0]; candidate = c['candidates'][0]
        request = {'analysis_id': a['analysis_id'], 'citation_id': c['id'], 'candidate_id': candidate['id']}
        self.assertEqual(self.post('/api/candidates/verify', {**request, 'url': 'http://127.0.0.1/'})[0], 400)
        status, verified = self.post('/api/candidates/verify', request)
        self.assertEqual(status, 200)
        self.assertEqual(verified['citations'][0]['candidates'][0]['evidence']['state'], 'related')
        status, out = self.post('/api/export', {'analysis_id': a['analysis_id'], 'decisions': {c['id']: candidate['url']}})
        self.assertEqual(status, 200)
        self.assertEqual(out['markdown'], SAMPLE.replace(c['url'], candidate['url']))
        status, discovered = self.post('/api/discover', {'analysis_id': a['analysis_id'], 'citation_id': c['id'], 'strategy': 'broad'})
        self.assertEqual(status, 200)
        self.assertEqual(len(discovered['citations'][0]['search_history']), 2)
    def test_stale_sessions_forged_candidates_and_validation(self):
        _, a = self.post('/api/analyze', {'source': SAMPLE})
        request = {'analysis_id': a['analysis_id'], 'citation_id': a['citations'][0]['id'], 'candidate_id': 'forged'}
        self.assertEqual(self.post('/api/candidates/verify', request)[0], 400)
        for _ in range(8): self.post('/api/analyze', {'source': ''})
        self.assertEqual(self.post('/api/candidates/verify', request)[0], 409)
        self.assertEqual(self.post('/api/discover', {'analysis_id': 'stale', 'citation_id': 'x', 'strategy': 'broad'})[0], 409)
        self.assertEqual(self.post('/api/discover', {'analysis_id': []})[0], 400)
    def test_gate_blocks_mutation_and_export_during_network_work(self):
        # Membership + source ownership are tested through HTTP above; gate contention
        # is covered separately with a controlled delayed provider.
        entered = threading.Event(); release = threading.Event()
        def provider(q): entered.set(); release.wait(2); return []
        from unittest.mock import patch
        other = make_server(port=0, mode='live', search=provider)
        worker = threading.Thread(target=other.serve_forever, daemon=True); worker.start()
        def call():
            c = http.client.HTTPConnection('127.0.0.1', other.server_port, timeout=4)
            c.request('POST', '/api/analyze', json.dumps({'source': '[Topic](https://example.org/old)'}), {'Content-Type': 'application/json'})
            c.getresponse().read(); c.close()
        try:
            with patch('sourcepatch.engine.check_url', return_value={'state': 'broken', 'status': 404}):
                task = threading.Thread(target=call); task.start(); self.assertTrue(entered.wait(1))
                c = http.client.HTTPConnection('127.0.0.1', other.server_port, timeout=3)
                c.request('POST', '/api/export', '{}', {'Content-Type': 'application/json'})
                response = c.getresponse(); self.assertEqual(response.status, 429); response.read(); c.close()
                release.set(); task.join()
        finally:
            release.set(); other.shutdown(); other.server_close(); worker.join()

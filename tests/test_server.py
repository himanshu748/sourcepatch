import http.client
import json
import threading
import unittest
from sourcepatch.server import make_server
from sourcepatch.fixtures import SAMPLE

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=make_server(port=0);cls.port=cls.server.server_port;cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,path='/',body=None,headers=None,method=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3);h={'Content-Type':'application/json',**(headers or {})};data=json.dumps(body) if body is not None else None
        conn.request(method or ('POST' if body is not None else 'GET'),path,data,h);response=conn.getresponse();raw=response.read();result=(response.status,dict(response.getheaders()),raw);conn.close();return result
    def test_config_safe_mode_and_sample(self):
        status,headers,raw=self.request('/api/config');self.assertEqual(status,200);data=json.loads(raw)
        self.assertEqual(data['mode'],'fixture');self.assertIn('field guide',data['sample']);self.assertNotIn('api_key',raw.decode());self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertEqual(data['search_budget'],8);self.assertEqual(data['process_search_budget'],8)
    def test_live_config_reports_lower_process_budget_without_searching(self):
        from unittest.mock import Mock
        search = Mock()
        server = make_server(port=0, mode='live', search=search, process_search_budget=1)
        worker = threading.Thread(target=server.handle_request, daemon=True)
        worker.start()
        try:
            connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
            connection.request('GET', '/api/config')
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            config = json.loads(response.read())
            connection.close()
            self.assertEqual(config['process_search_budget'], 1)
            self.assertEqual(config['search_budget'], 8)
            search.assert_not_called()
        finally:
            server.server_close()
            worker.join(timeout=3)
    def test_html_security_headers_and_assets(self):
        status,headers,raw=self.request();self.assertEqual(status,200);self.assertIn('SourcePatch',raw.decode());self.assertIn("script-src 'self'",headers['Content-Security-Policy']);self.assertEqual(headers['X-Content-Type-Options'],'nosniff');self.assertEqual(self.request('/../README.md')[0],404);self.assertEqual(self.request('/sourcepatch/network.py')[0],404)
    def test_foreign_host_origin_and_fetch_site_rejected(self):
        for header in [{'Host':'evil.example'},{'Origin':'https://evil.example'},{'Sec-Fetch-Site':'cross-site'}]:
            with self.subTest(header=header):self.assertEqual(self.request('/api/config',headers=header)[0],403)
    def test_bounded_json_input(self):
        self.assertEqual(self.request('/api/analyze',{'source':'x'*200001})[0],400);self.assertEqual(self.request('/api/analyze',{'source':None})[0],400);self.assertEqual(self.request('/api/analyze',[])[0],400)
        self.assertEqual(self.request('/api/analyze',{'source':''},headers={'Content-Type':'text/plain'})[0],415);self.assertEqual(self.request('/api/analyze',{},headers={'Content-Length':'999999'})[0],413);self.assertEqual(self.request('/api/analyze',method='OPTIONS')[0],405)
    def test_roundtrip_analysis_export_uses_server_source(self):
        status,_,raw=self.request('/api/analyze',{'source':SAMPLE});self.assertEqual(status,200);a=json.loads(raw);c=a['citations'][0]
        status,_,raw=self.request('/api/export',{'analysis_id':a['analysis_id'],'decisions':{c['id']:c['candidates'][0]['url']},'source':'EVIL'});self.assertEqual(status,200);out=json.loads(raw)
        self.assertIn('# A field guide',out['markdown']);self.assertIn('--- a/guide.md',out['diff']);self.assertNotIn('EVIL',out['markdown']);self.assertEqual(len(out['provenance']['changes']),1)
    def test_unknown_session_and_forged_decision(self):
        self.assertEqual(self.request('/api/export',{'analysis_id':'no','decisions':{}})[0],409);_,_,raw=self.request('/api/analyze',{'source':SAMPLE});a=json.loads(raw)
        self.assertEqual(self.request('/api/export',{'analysis_id':a['analysis_id'],'decisions':{'fake':'https://example.org'}})[0],400)
    def test_empty_input_and_escaped_text(self):
        status,_,raw=self.request('/api/analyze',{'source':'<script>alert(1)</script>'});self.assertEqual(status,200);self.assertEqual(json.loads(raw)['citations'],[])

if __name__=='__main__':unittest.main()

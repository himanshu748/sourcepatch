import json
import socket
import unittest
from unittest.mock import patch
from sourcepatch.network import NetworkError, FetchResult, validate_url, resolve_public, safe_get, check_url, SerpApiSearch

class URLTests(unittest.TestCase):
    def test_public_http_https(self):
        self.assertEqual(validate_url('https://docs.python.org/3/').hostname,'docs.python.org')
        self.assertEqual(validate_url('http://example.org/a').port,None)
    def test_forbidden_targets(self):
        bad=['file:///etc/passwd','ftp://example.org/a','https://localhost/','http://127.0.0.1','http://127.1','http://2130706433','http://0x7f000001','http://0177.0.0.1','http://10.0.0.1','http://169.254.169.254','http://192.168.0.1','http://100.64.0.1','http://[::1]','http://[::ffff:127.0.0.1]','http://[fe80::1%25eth0]','https://example.org:22','http://user:password@example.org','https://example.org\\@evil.org','https://example.org/\nheader','https://example.org/<script>','https://example.org"/a','https://example.org:bad','https://','https://foo.local','https://a.internal','https://a.test','https://a.invalid','http://255.255.255.255','http://[::]','https://example.org./']
        for url in bad:
            with self.subTest(url=url),self.assertRaises(NetworkError):validate_url(url)
    def test_invalid_type_length_and_dns_label(self):
        for url in [None,23,'https://'+'a'*300+'.org','https://exa_mple.org','https://example.org/'+'x'*4096]:
            with self.subTest(url=url),self.assertRaises(NetworkError):validate_url(url)
    def test_dns_rejects_mixed_private_public(self):
        rows=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('93.184.216.34',443)),(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',443))]
        with patch('sourcepatch.network.socket.getaddrinfo',return_value=rows):
            with self.assertRaises(NetworkError):resolve_public('example.org',443)
    def test_dns_public_results(self):
        rows=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('93.184.216.34',443))]
        with patch('sourcepatch.network.socket.getaddrinfo',return_value=rows):self.assertEqual(resolve_public('example.org',443),['93.184.216.34'])
    def test_redirect_to_private_is_never_requested(self):
        with patch('sourcepatch.network.resolve_public',return_value=['93.184.216.34']),patch('sourcepatch.network._request_once',return_value=(302,{'location':'http://127.0.0.1/'},b'',False)) as request:
            with self.assertRaises(NetworkError):safe_get('https://example.org/')
            self.assertEqual(request.call_count,1)
    def test_redirect_limit(self):
        with patch('sourcepatch.network.resolve_public',return_value=['93.184.216.34']),patch('sourcepatch.network._request_once',return_value=(302,{'location':'/again'},b'',False)) as request:
            with self.assertRaises(NetworkError):safe_get('https://example.org/',max_redirects=2)
            self.assertEqual(request.call_count,3)
    def test_pinned_address_and_bounds_passed(self):
        with patch('sourcepatch.network.resolve_public',return_value=['93.184.216.34']),patch('sourcepatch.network._request_once',return_value=(200,{},b'ok',False)) as request:
            result=safe_get('https://example.org/a#frag',max_bytes=12)
            self.assertEqual(result.status,200);self.assertEqual(request.call_args.args[1],'93.184.216.34')
            self.assertEqual(request.call_args.kwargs['max_bytes'],12);self.assertNotIn('#',request.call_args.args[0])
    def test_check_status_and_error_categories(self):
        for status,expected in [(200,'healthy'),(404,'broken'),(410,'broken'),(403,'uncertain'),(500,'uncertain')]:
            with self.subTest(status=status),patch('sourcepatch.network.safe_get',return_value=FetchResult(status,'https://example.org',b'')):self.assertEqual(check_url('https://example.org')['state'],expected)
        self.assertEqual(check_url('http://127.0.0.1')['state'],'blocked')

class SerpApiTests(unittest.TestCase):
    def test_search_parameters_and_results(self):
        seen=[]
        def fetch(url,**kwargs):
            seen.append(url);return FetchResult(200,url,json.dumps({'organic_results':[{'title':'Guide','link':'https://example.org/g','snippet':'text'}]}).encode())
        search=SerpApiSearch('fake-test-key',fetch=fetch)
        self.assertEqual(search.search('site:example.org test')[0]['title'],'Guide')
        from urllib.parse import urlsplit,parse_qs
        parts=urlsplit(seen[0]);params=parse_qs(parts.query)
        self.assertEqual(parts.netloc,'serpapi.com');self.assertEqual(params['engine'],['google']);self.assertEqual(params['q'],['site:example.org test']);self.assertEqual(params['api_key'],['fake-test-key']);self.assertNotIn('fake-test-key',repr(search))
    def test_invalid_and_error_responses_sanitized(self):
        cases=[(200,b'not json'),(403,b'fake-secret'),(200,b'{"error":"fake-secret"}'),(200,b'[]'),(200,b'{"organic_results": "bad"}')]
        for status,body in cases:
            with self.subTest(body=body):
                search=SerpApiSearch('fake-secret',fetch=lambda url,**kw:FetchResult(status,url,body))
                with self.assertRaises(NetworkError) as error:search.search('query')
                self.assertNotIn('fake-secret',str(error.exception))
    def test_key_validation(self):
        for key in ['',None,'a\nb']:
            with self.subTest(key=key),self.assertRaises(ValueError):SerpApiSearch(key)
    def test_result_shape_and_budget_filter(self):
        data={'organic_results':[{}, {'title':'bad','link':'file:///etc/passwd'}, {'title':'ok','link':'https://example.org'}]*10}
        search=SerpApiSearch('fake',fetch=lambda url,**kw:FetchResult(200,url,json.dumps(data).encode()))
        self.assertLessEqual(len(search.search('query')),5)
        self.assertTrue(all(r['link'].startswith('https://') for r in search.search('query')))
    def test_fetch_exception_never_leaks_key(self):
        def fetch(url,**kw):raise RuntimeError(url)
        with self.assertRaises(NetworkError) as error:SerpApiSearch('fake-secret',fetch=fetch).search('query')
        self.assertNotIn('fake-secret',str(error.exception))
    def test_truncated_response_rejected(self):
        def fetch(url,**kw):return FetchResult(200,url,b'{}',True)
        with self.assertRaises(NetworkError):SerpApiSearch('fake',fetch=fetch).search('query')

class DeadlineRegressionTests(unittest.TestCase):
    def test_close_response_cannot_extend_absolute_body_deadline(self):
        import http.client,socketserver,threading,time
        from sourcepatch.network import _request_once
        class SlowBody(socketserver.BaseRequestHandler):
            def handle(self):
                self.request.recv(4096);self.request.sendall(b'HTTP/1.0 200 OK\r\nContent-Length: 3\r\nConnection: close\r\n\r\na')
                for chunk in (b'b',b'c'):
                    time.sleep(0.15)
                    try:self.request.sendall(chunk)
                    except OSError:break
        server=socketserver.TCPServer(('127.0.0.1',0),SlowBody);worker=threading.Thread(target=server.handle_request,daemon=True);worker.start()
        def local_connection(host,port,address,timeout):return http.client.HTTPConnection('127.0.0.1',server.server_address[1],timeout=timeout)
        started=time.monotonic()
        try:
            with patch('sourcepatch.network._PinnedHTTP',side_effect=local_connection):
                try:_request_once('http://example.org/','93.184.216.34',deadline=started+0.20,max_bytes=10)
                except (NetworkError,OSError):pass
            self.assertLess(time.monotonic()-started,0.27,'body reads must share one absolute deadline')
        finally:server.server_close();worker.join(timeout=1)

class ResponseCleanupTests(unittest.TestCase):
    def test_detached_http_response_is_explicitly_closed(self):
        import io,http.client,time
        from sourcepatch.network import _request_once
        class Transport:
            def __init__(self,payload):self.file=io.BytesIO(payload)
            def makefile(self,*args):return self.file
            def settimeout(self,*args):pass
            def shutdown(self,*args):pass
        for payload in [b'HTTP/1.0 302 Found\r\nLocation: /new\r\n\r\n',b'HTTP/1.0 200 OK\r\nContent-Length: 10\r\n\r\n0123456789']:
            transport=Transport(payload);response=http.client.HTTPResponse(transport)
            class Connection:
                sock=transport
                def connect(self):pass
                def request(self,*args,**kwargs):pass
                def getresponse(self):response.begin();return response
                def close(self):pass
            with patch('sourcepatch.network._PinnedHTTP',return_value=Connection()):_request_once('http://example.org/','93.184.216.34',deadline=time.monotonic()+1,max_bytes=2)
            self.assertTrue(response.isclosed(),'the response owns a detached socket file and must be closed explicitly')

if __name__=='__main__':unittest.main()

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
    def test_response_receipt_is_allowlisted_and_cache_copies_are_isolated(self):
        import hashlib
        search_id = '61afb3ace7d08a685b3bcbb1'
        body = json.dumps({'search_metadata': {'id': search_id, 'status': 'Success',
                           'json_endpoint': 'https://serpapi.com/?api_key=fake-secret',
                           'unexpected': {'api_key': 'fake-secret'}},
                           'organic_results': [{'title': 'Guide', 'link': 'https://example.org/g'}]}).encode()
        provider = SerpApiSearch('fake-secret', fetch=lambda url, **kw: FetchResult(200, url, body), max_searches=1)
        first = provider.search('query')
        self.assertIsInstance(first, list)
        self.assertEqual(first.evidence['search_id'], search_id)
        self.assertEqual(first.evidence['provider_status'], 'Success')
        self.assertEqual(first.evidence['response_sha256'], hashlib.sha256(body).hexdigest())
        self.assertFalse(first.evidence['cache_hit'])
        first.evidence['search_id'] = 'caller mutation'
        cached = provider.search('query')
        self.assertTrue(cached.evidence['cache_hit'])
        self.assertEqual(cached.evidence['search_id'], search_id)
        cached.evidence.clear()
        self.assertEqual(provider.search('query').evidence['search_id'], search_id)
        self.assertEqual(provider.search_calls, 1)
        serialized = json.dumps(provider.search('query').evidence)
        self.assertNotIn('fake-secret', serialized)
        self.assertNotIn('https://', serialized)
        self.assertNotIn('unexpected', serialized)

    def test_receipt_omits_malformed_ids_and_never_accepts_incomplete_searches(self):
        for search_id in ['https://serpapi.com/?api_key=fake-secret', 'x' * 500, None, 42]:
            with self.subTest(search_id=search_id):
                body = json.dumps({'search_metadata': {'id': search_id, 'status': 'Success'}}).encode()
                provider = SerpApiSearch('fake-secret', fetch=lambda url, **kw: FetchResult(200, url, body))
                self.assertNotIn('search_id', provider.search('query').evidence)
        for status in ['Processing', 'Error', 'fake-secret', None, {'key': 'fake-secret'}]:
            with self.subTest(status=status):
                body = json.dumps({'search_metadata': {'status': status}}).encode()
                provider = SerpApiSearch('fake-secret', fetch=lambda url, **kw: FetchResult(200, url, body), max_searches=1)
                with self.assertRaises(NetworkError) as error:
                    provider.search('query')
                self.assertNotIn('fake-secret', str(error.exception))
                self.assertEqual(provider._cache, {})
                self.assertEqual(provider.search_calls, 1)

    def test_receipt_does_not_invent_missing_provider_metadata(self):
        provider = SerpApiSearch('fake', fetch=lambda url, **kw: FetchResult(200, url, b'{}'))
        rows = provider.search('query')
        self.assertEqual(rows, [])
        self.assertEqual(rows.evidence['result_count'], 0)
        self.assertNotIn('search_id', rows.evidence)
        self.assertNotIn('provider_status', rows.evidence)

    def test_search_budget_validation(self):
        for budget in [0, -1, 9, 1.0, True, '1', None]:
            with self.subTest(budget=budget), self.assertRaisesRegex(ValueError, 'integer from 1 through 8'):
                SerpApiSearch('fake-test-key', max_searches=budget)

    def test_configured_budget_counts_fetches_and_serves_isolated_cache_after_exhaustion(self):
        for budget in [1, 8]:
            with self.subTest(budget=budget):
                seen = []
                def fetch(url, **kwargs):
                    seen.append(url)
                    return FetchResult(200, url, b'{"organic_results":[{"title":"Guide","link":"https://example.org/g"}]}')
                search = SerpApiSearch('fake-test-key', fetch=fetch, max_searches=budget)
                first = search.search('query 0')
                first[0]['title'] = 'changed by caller'
                first.append({'title': 'extra'})
                for index in range(1, budget):
                    search.search(f'query {index}')
                with self.assertRaisesRegex(NetworkError, f'{budget}-search budget'):
                    search.search('over budget')
                cached = search.search('query 0')
                self.assertEqual(len(cached), 1)
                self.assertEqual(cached[0]['title'], 'Guide')
                cached.clear()
                self.assertEqual(search.search('query 0')[0]['title'], 'Guide')
                self.assertEqual(len(seen), budget)
                self.assertEqual(search.search_calls, budget)

    def test_failed_fetch_consumes_allowance_without_retry_or_cache(self):
        seen = []
        def fetch(url, **kwargs):
            seen.append(url)
            raise OSError('provider unavailable')
        search = SerpApiSearch('fake-test-key', fetch=fetch, max_searches=1)
        with self.assertRaisesRegex(NetworkError, 'Search request failed'):
            search.search('query')
        with self.assertRaisesRegex(NetworkError, '1-search budget'):
            search.search('query')
        self.assertEqual(len(seen), 1)
        self.assertEqual(search.search_calls, 1)

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

class CompleteResponseTests(unittest.TestCase):
    def fetch_response(self, payload, max_bytes=4096):
        """Exercise real socket/HTTPResponse cleanup against one controlled peer."""
        import http.client
        import socketserver
        import threading
        class CompleteBody(socketserver.BaseRequestHandler):
            def handle(self):
                self.request.recv(4096)
                self.request.sendall(payload)
        with socketserver.TCPServer(('127.0.0.1', 0), CompleteBody) as server:
            worker = threading.Thread(target=server.handle_request, daemon=True)
            worker.start()
            def local_connection(host, port, address, timeout):
                return http.client.HTTPConnection('127.0.0.1', server.server_address[1], timeout=timeout)
            try:
                with patch('sourcepatch.network.resolve_public', return_value=['93.184.216.34']), \
                     patch('sourcepatch.network._PinnedHTTP', side_effect=local_connection):
                    return safe_get('http://example.org/api', timeout=1, max_bytes=max_bytes)
            finally:
                worker.join(timeout=1)

    def test_complete_http10_json_body_is_not_a_transport_error(self):
        body = b'{"plan_monthly_price":0,"plan_searches_left":239}'
        response = self.fetch_response(b'HTTP/1.0 200 OK\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body)
        self.assertEqual((response.status, response.body, response.truncated), (200, body, False))

    def test_complete_http11_close_json_body_preserves_error_status(self):
        body = b'{"error":"Invalid API key"}'
        response = self.fetch_response(b'HTTP/1.1 401 Unauthorized\r\nConnection: close\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body)
        self.assertEqual((response.status, response.body, response.truncated), (401, body, False))

    def test_complete_chunked_close_body_is_read_without_closed_socket_access(self):
        response = self.fetch_response(b'HTTP/1.1 200 OK\r\nConnection: close\r\nTransfer-Encoding: chunked\r\n\r\n2\r\n{}\r\n0\r\n\r\n')
        self.assertEqual((response.status, response.body, response.truncated), (200, b'{}', False))

    def test_complete_response_at_and_beyond_byte_limit_keeps_truncation_contract(self):
        for body, expected, truncated in [(b'ab', b'ab', False), (b'abc', b'ab', True)]:
            with self.subTest(body=body):
                response = self.fetch_response(b'HTTP/1.0 200 OK\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body, max_bytes=2)
                self.assertEqual((response.body, response.truncated), (expected, truncated))


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

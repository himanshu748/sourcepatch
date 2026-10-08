import json
import unittest
from urllib.parse import parse_qs, urlsplit
from sourcepatch.network import FetchResult, SerpApiSearch, NetworkError

class DiscoveryTests(unittest.TestCase):
    def test_engine_parameter_cache_separation_and_normalization(self):
        calls = []
        def fetch(url, **kw):
            calls.append(parse_qs(urlsplit(url).query))
            return FetchResult(200, url, b'{"search_metadata":{"status":"Success"},"organic_results":[]}')
        provider = SerpApiSearch('fake-key', fetch=fetch)
        provider.search('  citation   topic ')
        self.assertTrue(provider.search('citation topic').evidence['cache_hit'])
        scholar = provider.search('citation topic', engine='google_scholar')
        self.assertFalse(scholar.evidence['cache_hit'])
        self.assertEqual(scholar.evidence['engine'], 'google_scholar')
        self.assertEqual(scholar.evidence['query'], 'citation topic')
        self.assertEqual(len(calls), 2)
        self.assertNotIn('gl', calls[1])
        with self.assertRaises(NetworkError): provider.search('x', engine='bing')
        self.assertEqual(provider.search_calls, 2)

    def test_scholar_results_and_credential_echo_are_sanitized(self):
        payload = {'search_metadata': {'status': 'Success'}, 'organic_results': [
            {'title': 'A paper', 'link': 'https://arxiv.org/abs/1706.03762', 'snippet': 'Attention models', 'publication_info': {'summary': 'Authors - 2017'}},
            {'title': 'fake-secret', 'link': 'https://example.org/?token=fake-secret'}]}
        provider = SerpApiSearch('fake-secret', fetch=lambda url, **kw: FetchResult(200, url, json.dumps(payload).encode()))
        rows = provider.search('Attention models', engine='google_scholar')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['publication'], 'Authors - 2017')
        self.assertNotIn('fake-secret', json.dumps(rows))

    def test_failed_attempt_has_sanitized_receipt_and_no_cache(self):
        provider = SerpApiSearch('fake-key', fetch=lambda url, **kw: FetchResult(429, url, b'fake-key'), max_searches=1)
        with self.assertRaises(NetworkError): provider.search('citation topic')
        self.assertEqual(provider.last_receipt['completion_status'], 'failed')
        self.assertEqual(provider.last_receipt['response_status'], 429)
        self.assertNotIn('fake-key', json.dumps(provider.last_receipt))
        self.assertEqual(provider._cache, {})

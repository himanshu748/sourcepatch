"""Authored HTML and controlled transports; no public network requests."""
import hashlib
import json
import unittest
from unittest.mock import Mock, patch
from sourcepatch.evidence import identifiers, inspect_candidate
from sourcepatch.network import FetchResult, NetworkError


class EvidenceTests(unittest.TestCase):
    citation = {'label': 'Python pathlib filesystem paths',
                'url': 'https://docs.python.org/old',
                'context': 'Use Python pathlib filesystem paths to manage directories.'}

    def inspect(self, html, url='https://docs.python.org/new', **kwargs):
        result = FetchResult(200, url.split('#')[0], html.encode(), **kwargs)
        fetch = Mock(return_value=result)
        evidence = inspect_candidate(self.citation, {'url': url}, fetch=fetch)
        return evidence, fetch

    def test_extract_title_headings_relevant_excerpt_hash_and_bounds(self):
        html = '<title>Python pathlib</title><h1 id="paths">Filesystem paths</h1><p>Python pathlib filesystem paths manage directories.</p><script>secret script</script><style>secret style</style>'
        e, fetch = self.inspect(html)
        self.assertEqual(e['title'], 'Python pathlib')
        self.assertIn('Filesystem paths', e['headings'])
        self.assertEqual(e['content_sha256'], hashlib.sha256(html.encode()).hexdigest())
        self.assertEqual(e['state'], 'related')
        self.assertNotIn('secret', json.dumps(e))
        self.assertLessEqual(sum(map(len, e['excerpts'])), 720)
        self.assertEqual(fetch.call_args.kwargs, {'timeout': 8, 'max_bytes': 524288, 'max_redirects': 3})

    def test_http200_irrelevant_is_insufficient(self):
        e, _ = self.inspect('<title>Casino</title><h1>Welcome</h1><p>Buy shoes and win cash today.</p>')
        self.assertEqual(e['state'], 'insufficient')
        self.assertIn('CONTENT_UNRELATED', e['reason_codes'])

    def test_anchor_found_missing_and_truncated_unknown(self):
        html = '<title>Python pathlib</title><h1 id="paths">Filesystem paths</h1><p>Python pathlib filesystem paths manage directories.</p>'
        self.assertEqual(self.inspect(html, url='https://docs.python.org/new#paths')[0]['anchor']['state'], 'found')
        e, _ = self.inspect(html, url='https://docs.python.org/new#absent')
        self.assertEqual(e['anchor']['state'], 'missing')
        self.assertEqual(e['state'], 'insufficient')
        e, _ = self.inspect(html, url='https://docs.python.org/new#absent', truncated=True)
        self.assertEqual(e['anchor']['state'], 'unknown')
        self.assertEqual(e['state'], 'inconclusive')

    def test_cross_domain_and_hidden_content(self):
        e, _ = self.inspect('<title>Python pathlib</title><p hidden>filesystem paths manage directories</p><p>unrelated furniture sale</p>', url='https://elsewhere.org/new')
        self.assertIn('CROSS_DOMAIN', e['reason_codes'])
        self.assertNotEqual(e['state'], 'related')

    def test_empty_unsupported_and_error_are_inconclusive(self):
        for body in ['', '%PDF-1.7 bytes', '<script>Python pathlib filesystem paths</script>']:
            self.assertEqual(self.inspect(body)[0]['state'], 'inconclusive')
        fetch = Mock(side_effect=NetworkError('blocked'))
        e = inspect_candidate(self.citation, {'url': 'https://example.org/new'}, fetch=fetch)
        self.assertEqual(e['state'], 'inconclusive')
        self.assertFalse(e['retrieval']['observed'])

    def test_private_ip_and_redirect_use_existing_policy(self):
        for url in ['http://127.0.0.1/', 'http://169.254.169.254/']:
            e = inspect_candidate(self.citation, {'url': url})
            self.assertEqual(e['state'], 'inconclusive')
        with patch('sourcepatch.network.resolve_public', return_value=['93.184.216.34']), patch('sourcepatch.network._request_once', return_value=(302, {'location': 'http://127.0.0.1/'}, b'', False)) as request:
            e = inspect_candidate(self.citation, {'url': 'https://example.org/'})
            self.assertEqual(e['state'], 'inconclusive')
            self.assertEqual(request.call_count, 1)

    def test_identifier_mismatch_does_not_claim_equivalence(self):
        citation = {**self.citation, 'url': 'https://example.org/106106183'}
        e = inspect_candidate(citation, {'url': 'https://example.org/999999999'}, fetch=lambda *a, **kw: FetchResult(200, 'https://example.org/999999999', b'<h1>Python pathlib</h1><p>Python pathlib filesystem paths manage directories.</p>'))
        self.assertEqual(e['state'], 'insufficient')
        self.assertIn('IDENTIFIER_MISMATCH', e['reason_codes'])

    def test_doi_sentence_punctuation_does_not_reject_matching_page(self):
        citation = {'label': 'Graph learning methods',
                    'url': 'https://example.org/10.1234/foo',
                    'context': 'Graph learning methods improve research results.'}
        for ending in ('', '.', ',', ';', ':', '!', '?', ').', '],', '\".', '\u201d.', '}):'):
            with self.subTest(ending=ending):
                html = ('<h1>Graph learning methods</h1><p>Graph learning methods '
                        'improve research results. DOI 10.1234/foo' + ending + '</p>')
                e = inspect_candidate(citation, {'url': 'https://example.org/paper'},
                                      fetch=lambda *a, **kw: FetchResult(200, 'https://example.org/paper', html.encode()))
                self.assertEqual(e['relevance']['identifier'], 'match')
                self.assertEqual(e['state'], 'related')

    def test_doi_normalization_preserves_internal_and_balanced_suffix_punctuation(self):
        for doi in ('10.1234/foo.bar-baz;part:2', '10.1234/foo(bar)', '10.1234/foo[bar]', '10.1234/foo{bar}'):
            with self.subTest(doi=doi):
                self.assertEqual(identifiers('DOI (' + doi + ').'), {doi})
        self.assertEqual(identifiers('arXiv 2401.12345v2 and resource 106106183'),
                         {'2401.12345v2', '106106183'})

class ConservativeExtractionTests(unittest.TestCase):
    citation = EvidenceTests.citation
    inspect = EvidenceTests.inspect
    def test_matching_heading_alone_does_not_establish_content_relevance(self):
        e, _ = self.inspect('<title>Python pathlib</title><h1>Python pathlib filesystem paths</h1><p>Shop furniture and shoes online, sale ends tomorrow.</p>')
        self.assertEqual(e['state'], 'insufficient')

    def test_deeply_nested_html_is_bounded_and_inconclusive(self):
        e, _ = self.inspect('<div>' * 1000 + 'Python pathlib filesystem paths')
        self.assertEqual(e['state'], 'inconclusive')
        self.assertIn('EXTRACTION_FAILED', e['reason_codes'])

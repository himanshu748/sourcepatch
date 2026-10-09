import json
import unittest
from unittest.mock import Mock, patch
from sourcepatch.engine import analyze, discover, verify_candidate, export_review
from sourcepatch.fixtures import SAMPLE
from sourcepatch.network import FetchResult, SerpApiSearch

class V2Tests(unittest.TestCase):
    def test_fixture_verification_no_network_and_provenance(self):
        analysis = analyze(SAMPLE)
        c = analysis['citations'][0]
        candidate = c['candidates'][0]
        with patch('sourcepatch.evidence.safe_get', side_effect=AssertionError('network')):
            verify_candidate(analysis, c['id'], candidate['id'])
        self.assertEqual(candidate['evidence']['origin'], 'authored_fixture')
        self.assertEqual(candidate['evidence']['state'], 'related')
        self.assertFalse(candidate['page_verified'])
        out = export_review(SAMPLE, analysis, {c['id']: candidate['url']})
        self.assertEqual(out['markdown'], SAMPLE.replace(c['url'], candidate['url']))
        report = json.loads(json.dumps(out['provenance']))
        self.assertEqual(report['changes'][0]['candidate']['evidence']['version'], 'lexical-evidence-2.1')
        self.assertEqual(len(report['search_history']), 3)

    def test_additional_discovery_explicit_bounded_and_identifiers(self):
        provider = Mock(return_value=[])
        analysis = analyze('[Paper 1706.03762](https://arxiv.org/old/1706.03762)', mode='live', search=provider,
                           checker=lambda u: {'state': 'broken', 'status': 404})
        cid = analysis['citations'][0]['id']
        self.assertEqual(provider.call_count, 1)
        discover(analysis, cid, 'scholar', search=provider)
        self.assertEqual(provider.call_args.kwargs, {'engine': 'google_scholar'})
        discover(analysis, cid, 'identifier', search=provider)
        self.assertIn('"1706.03762"', provider.call_args.args[0])
        self.assertNotIn('site:', provider.call_args.args[0])
        with self.assertRaises(ValueError): discover(analysis, cid, 'arbitrary', search=provider)
        for _ in range(5): discover(analysis, cid, 'broad', search=provider)
        with self.assertRaises(ValueError): discover(analysis, cid, 'broad', search=provider)
        self.assertEqual(provider.call_count, 8)

    def test_verification_membership_cache_and_abstention(self):
        analysis = analyze(SAMPLE)
        c = analysis['citations'][0]
        candidate = c['candidates'][0]
        with self.assertRaises(ValueError): verify_candidate(analysis, c['id'], 'https://example.org')
        # Controlled live transport, not a live provider result.
        analysis['mode'] = 'live'
        fetch = Mock(return_value=FetchResult(200, candidate['url'], b'<title>Shoes</title><p>Shop new shoes and furniture online today.</p>'))
        verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch)
        verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(candidate['evidence']['state'], 'insufficient')
        with self.assertRaisesRegex(ValueError, 'INSUFFICIENT EVIDENCE'):
            export_review(SAMPLE, analysis, {c['id']: candidate['url']})
        self.assertEqual(export_review(SAMPLE, analysis, {})['markdown'], SAMPLE)

    def test_explicit_transport_retry_preserves_failure_and_enforces_cap(self):
        from sourcepatch.network import NetworkError
        analysis = analyze(SAMPLE)
        analysis['mode'] = 'live'
        c = analysis['citations'][0]; candidate = c['candidates'][0]
        fetch = Mock(side_effect=NetworkError('temporary failure'))
        verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch)
        verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch)
        self.assertEqual(fetch.call_count, 1)
        failed = candidate['evidence']
        for _ in range(2):
            verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch, retry=True)
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(candidate['evidence_history'][0], failed)
        self.assertEqual(analysis['verification_attempts'], 3)
        with self.assertRaisesRegex(ValueError, 'retry budget'):
            verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch, retry=True)
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(len(candidate['evidence_history']), 2)
        self.assertEqual(len(export_review(SAMPLE, analysis, {})['provenance']['candidate_observations'][0]['evidence_history']), 2)

    def test_explicit_retry_can_recover_transport_without_erasing_failure(self):
        from sourcepatch.network import NetworkError
        analysis = analyze(SAMPLE); analysis['mode'] = 'live'
        c = analysis['citations'][0]; candidate = c['candidates'][0]
        fetch = Mock(side_effect=[NetworkError('temporary failure'), FetchResult(200, candidate['url'], b'<title>Python pathlib</title><h1>Python pathlib</h1><p>Python pathlib provides filesystem operations for readable files and directories.</p>')])
        verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch)
        verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch, retry=True)
        self.assertEqual(candidate['evidence']['state'], 'related')
        self.assertFalse(candidate['evidence_history'][0]['retrieval']['observed'])
        self.assertNotIn('RETRIEVAL_FAILED', candidate['reason_codes'])
        with self.assertRaisesRegex(ValueError, 'Only a failed transport'):
            verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch, retry=True)

    def test_no_candidates_and_unknown_citation_fail_closed(self):
        a = analyze('[Missing](https://example.org/missing)')
        with self.assertRaises(ValueError): verify_candidate(a, a['citations'][0]['id'], 'missing')
        with self.assertRaises(ValueError): discover(a, 'missing', 'broad')

class RankingReviewTests(unittest.TestCase):
    def test_evidence_group_sort_does_not_invent_close_score_ambiguity(self):
        from sourcepatch.engine import _sort_candidates
        citation = {'candidates': [
            {'url':'https://example.org/related','score':50,'evidence':{'state':'related'}},
            {'url':'https://example.org/uninspected','score':95,'evidence':None}],
            'discovery_ambiguous':False}
        _sort_candidates(citation)
        self.assertEqual(citation['candidates'][0]['evidence']['state'],'related')
        self.assertFalse(citation['ambiguous'])

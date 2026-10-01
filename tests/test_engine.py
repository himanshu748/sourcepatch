import unittest
from sourcepatch.engine import analyze, export_review
from sourcepatch.fixtures import SAMPLE

class EngineTests(unittest.TestCase):
    def test_sample_is_deterministic_honest_and_complete(self):
        a=analyze(SAMPLE);self.assertEqual(a,analyze(SAMPLE));self.assertEqual(a['mode'],'fixture');self.assertFalse(a['live_verified']);self.assertEqual(len(a['citations']),5)
        self.assertEqual(a['summary']['broken'],3);self.assertEqual(a['summary']['healthy'],1);self.assertEqual(a['summary']['blocked'],1);self.assertTrue(all(not c['check']['verified'] for c in a['citations']))
    def test_duplicates_get_one_decision_and_all_spans(self):
        a=analyze(SAMPLE);c=a['citations'][0];self.assertEqual(c['occurrences'],2)
        out=export_review(SAMPLE,a,{c['id']:c['candidates'][0]['url']})
        self.assertEqual(out['markdown'].count(c['url']),0);self.assertEqual(out['markdown'].count(c['candidates'][0]['url']),2);self.assertEqual(len(out['provenance']['changes']),1);self.assertIn('synthetic',out['provenance']['notice'].lower())
    def test_no_implicit_approval(self):
        a=analyze(SAMPLE);out=export_review(SAMPLE,a,{})
        self.assertEqual(out['markdown'],SAMPLE);self.assertEqual(out['diff'],'');self.assertEqual(out['provenance']['changes'],[])
    def test_ambiguity_and_same_publisher_ranking(self):
        a=analyze(SAMPLE);self.assertTrue(a['citations'][0]['candidates'][0]['same_host'])
        mdn=next(c for c in a['citations'] if 'mozilla' in c['url']);self.assertTrue(mdn['ambiguous']);self.assertTrue(all('score' in c and 'reasons' in c for c in mdn['candidates']))
    def test_forged_unknown_and_stale_decisions_rejected(self):
        a=analyze(SAMPLE);cid=a['citations'][0]['id']
        for source,decisions in [(SAMPLE+'\n',{}),(SAMPLE,{'fake':'https://example.org'}),(SAMPLE,{cid:'https://example.org/unknown'})]:
            with self.subTest(decisions=decisions),self.assertRaises(ValueError):export_review(source,a,decisions)
    def test_arbitrary_fixture_document_makes_no_network(self):
        def fail(*a,**k):raise AssertionError('network requested')
        a=analyze('[New](https://example.org/a)',checker=fail,search=fail)
        self.assertEqual(a['citations'][0]['check']['state'],'unavailable');self.assertEqual(a['citations'][0]['candidates'],[])
    def test_live_only_searches_broken_with_query_budget(self):
        seen=[]
        def checker(url):return {'state':'broken','status':404,'verified':True,'detail':'observed'}
        def search(q):seen.append(q);return [{'title':'Docs','link':'https://example.org/new','snippet':''}]
        source='\n'.join(f'[Doc {i}](https://example.org/old/{i})' for i in range(20));a=analyze(source,mode='live',search=search,checker=checker)
        self.assertEqual(len(seen),8);self.assertTrue(all(q.startswith('site:example.org ') for q in seen));self.assertIn('budget',a['citations'][8]['search_note'].lower());self.assertFalse(a['live_verified'])
    def test_live_requires_explicit_search_and_checks_blocked_first(self):
        with self.assertRaises(ValueError):analyze(SAMPLE,mode='live')
        def fail(*a,**k):raise AssertionError('unsafe call')
        a=analyze('[no](http://127.0.0.1)',mode='live',search=fail,checker=fail);self.assertEqual(a['citations'][0]['check']['state'],'blocked')
    def test_search_failure_not_fabricated_as_results(self):
        def bad(q):raise ValueError('upstream error')
        a=analyze('[Doc](https://example.org/old)',mode='live',search=bad,checker=lambda u:{'state':'broken','status':404,'verified':True,'detail':''})
        self.assertEqual(a['citations'][0]['candidates'],[]);self.assertIn('failed',a['citations'][0]['search_note'].lower())
    def test_anchor_preserved_with_warning(self):
        source='[Python pathlib](https://docs.python.org/3/library/pathlib-old.html#paths)';a=analyze(source);c=a['citations'][0]
        self.assertIn('anchor',c['candidates'][0]['warning'].lower());out=export_review(source,a,{c['id']:c['candidates'][0]['url']});self.assertIn('pathlib.html#paths',out['markdown'])
    def test_max_citations_and_modes(self):
        text=' '.join(f'[x](https://example.org/{i})' for i in range(61))
        with self.assertRaises(ValueError):analyze(text)
        with self.assertRaises(ValueError):analyze(SAMPLE,mode='magic')
    def test_untrusted_results_filter_invalid_markup_and_self_links(self):
        a=analyze('[Doc](https://example.org/old)',mode='live',checker=lambda u:{'state':'broken','status':404,'verified':True,'detail':''},search=lambda q:[{'title':'evil','link':'javascript:alert(1)'},{'title':'self','link':'https://example.org/old'},{'title':'okay','link':'https://example.org/new','snippet':'<script>evil</script>'}])
        self.assertEqual(len(a['citations'][0]['candidates']),1);self.assertEqual(a['citations'][0]['candidates'][0]['url'],'https://example.org/new')

class DiffLineRegressionTests(unittest.TestCase):
    def test_unicode_separators_and_carriage_return_are_content_not_diff_lines(self):
        for separator in ['\u2028','\u2029','\r']:
            source='Before'+separator+'[Python pathlib](https://docs.python.org/3/library/pathlib-old.html)'+separator+'After';a=analyze(source);c=a['citations'][0]
            out=export_review(source,a,{c['id']:c['candidates'][0]['url']})
            expected='--- a/guide.md\n+++ b/guide.md\n@@ -1 +1 @@\n-'+source+'\n\\ No newline at end of file\n+'+out['markdown']+'\n\\ No newline at end of file\n'
            self.assertEqual(out['diff'],expected)

if __name__=='__main__':unittest.main()

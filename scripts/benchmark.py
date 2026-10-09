"""Offline authored/recorded corpus. Never calls a network/provider or auto-approves in the app."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sourcepatch.engine import analyze, verify_candidate, export_review
from sourcepatch.network import FetchResult

ROOT = Path(__file__).resolve().parent.parent

def run():
    raw = (ROOT / 'benchmarks/cases.json').read_bytes()
    cases = json.loads(raw)
    results = []
    for case in cases:
        searches = []
        def search(query):
            searches.append(query)
            return [{k:v for k,v in r.items() if k != 'html'} for r in case['results']]
        analysis = analyze(case['source'], mode='live', search=search,
                           checker=lambda url: {'state':'broken','status':404,'verified':False,'detail':'Controlled benchmark status, not a current HTTP observation.'})
        c = analysis['citations'][0]
        urls = [x['url'] for x in c['candidates']]
        gold = case['gold_url']
        recall = int(gold in urls[:5]) if gold else None
        rr_before = 1 / (urls.index(gold)+1) if gold in urls else 0 if gold else None
        for candidate in list(c['candidates']):
            record = next(r for r in case['results'] if r['link'].split('#')[0] == candidate['url'].split('#')[0])
            def fetch(url, **kw):
                return FetchResult(200, url.split('#')[0], record['html'].encode(), content_type='text/html')
            verify_candidate(analysis, c['id'], candidate['id'], fetch=fetch)
            candidate['evidence']['origin'] = 'authored_benchmark_html' if case['origin'] == 'authored_test_case' else 'no_page_evidence_in_historical_record'
        ranked = [x['url'] for x in c['candidates']]
        related = [x for x in c['candidates'] if x['evidence']['state'] == 'related']
        abstains = not related or c['ambiguous']
        # Explicit simulated reviewer uses corpus gold; never changes actual source files.
        decisions = {c['id']:gold} if gold and not case['expected_abstain'] and gold in [x['url'] for x in related] else {c['id']:None}
        out = export_review(case['source'], analysis, decisions)
        expected = case['source'].replace(c['url'],gold) if gold and not case['expected_abstain'] else case['source']
        results.append({'id':case['id'],'origin':case['origin'],'recall_at_5':recall,
                        'reciprocal_rank_before':rr_before,'reciprocal_rank_after':1/(ranked.index(gold)+1) if gold in ranked else 0 if gold else None,
                        'abstains':abstains,'expected_abstain':case['expected_abstain'],
                        'abstention_correct':abstains == case['expected_abstain'],
                        'patch_correct':out['markdown']==expected,
                        'controlled_search_calls':len(searches),'candidate_count':len(c['candidates']),
                        'readable_evidence':sum(bool(x['evidence']['excerpts']) for x in c['candidates']),
                        'source_sha256':hashlib.sha256(case['source'].encode()).hexdigest()})
    def metric(key):
        values=[r[key] for r in results if r[key] is not None]
        return {'value':round(sum(values)/len(values),4),'numerator':sum(values),'denominator':len(values)}
    return {'benchmark_version':'1','corpus_sha256':hashlib.sha256(raw).hexdigest(),
            'scope':'12 authored cases plus 1 historical public NPTEL retrieval miss. Controlled responses; zero live calls. Not an estimate of real-world accuracy.',
            'candidate_recall_at_5':metric('recall_at_5'), 'ranking_mrr_before':metric('reciprocal_rank_before'),
            'ranking_mrr_after':metric('reciprocal_rank_after'), 'abstention_correctness':metric('abstention_correct'),
            'patch_correctness_simulated_review':metric('patch_correct'),
            'search_efficiency':{'controlled_calls':sum(r['controlled_search_calls'] for r in results),'real_provider_calls':0,'cases':len(cases)},
            'evidence_availability':{'readable_candidates':sum(r['readable_evidence'] for r in results),'total_candidates':sum(r['candidate_count'] for r in results)},
            'cases':results}

if __name__ == '__main__':
    print(json.dumps(run(),indent=2))

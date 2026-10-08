"""Deterministic evidence ranking and explicit, source-checked review exports."""
from collections import Counter
from dataclasses import asdict
from types import SimpleNamespace
from datetime import datetime, timezone
import difflib
import hashlib
import re
from urllib.parse import unquote, urlsplit, urlunsplit

from .fixtures import FIXTURE_DATE, fixture_check, fixture_results, fixture_page
from .evidence import inspect_candidate, identifiers, VERSION
from .markdown import parse_markdown, apply_replacements
from .network import NetworkError, SearchBudgetError, SearchResults, check_url, validate_url

MAX_CITATIONS = 60
MAX_SEARCHES = 8


def _digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _tokens(text):
    return set(re.findall(r'[^\W_]+', text.casefold(), re.UNICODE)) - {'a', 'an', 'the', 'to', 'of', 'and', 'in', 'for', 'https', 'http', 'www'}


def _topic_words(citation):
    """Prefer a descriptive label; generic labels need the URL's topic instead."""
    words = re.findall(r'[^\W_]+', citation.label, re.UNICODE)
    generic = {'here', 'click', 'read', 'more', 'link', 'source', 'reference', 'documentation',
               'docs', 'manual', 'website', 'article', 'page', 'this', 'see', 'the', 'a', 'an'}
    if citation.label != citation.url and any(word.casefold() not in generic for word in words):
        return words[:14]
    path = unquote(urlsplit(citation.url).path)
    path = re.sub(r'\.(?:html?|md|pdf|php|aspx?)$', '', path, flags=re.I)
    segments = [part for part in path.split('/') if part and part.casefold() not in {'index', 'docs', 'documentation'}]
    return re.findall(r'[^\W_]+', ' '.join(segments[-2:]), re.UNICODE)[:14]


def _query(citation):
    parts = urlsplit(citation.url)
    words = _topic_words(citation)
    # Broaden only the conventional www prefix, never guess a registrable
    # domain. Discovery scope does not establish publisher identity.
    host = parts.hostname.removeprefix('www.')
    # Preserve one bounded resource identifier even with a descriptive label.
    # Only full numeric path segments qualify; never use query/fragment data.
    identifiers = [part for part in unquote(parts.path).split('/')
                   if re.fullmatch(r'[0-9]{6,20}', part)]
    identifier = identifiers[-1] if identifiers else None
    suffix = f' "{identifier}"' if identifier else ''
    words = [word for word in words if word != identifier]
    query = 'site:' + host + ' ' + ' '.join(words[:14])
    return query[:500 - len(suffix)].rstrip() + suffix


def _rank(citation, rows):
    old = urlsplit(citation.url)
    label_tokens = _tokens(' '.join(_topic_words(citation)))
    context_tokens = _tokens(citation.context)
    candidates, seen = [], set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('link'), str):
            continue
        try:
            parts = validate_url(row['link'])
        except NetworkError:
            continue
        base = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ''))
        old_base = urlunsplit((old.scheme, old.netloc, old.path, old.query, ''))
        if base == old_base or base in seen:
            continue
        seen.add(base)
        url = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, parts.fragment or old.fragment))
        title = str(row.get('title', 'Untitled result'))[:240]
        snippet = str(row.get('snippet', ''))[:600]
        same = parts.hostname.casefold() == old.hostname.casefold()
        overlap = len(label_tokens & _tokens(title)) / max(1, len(label_tokens))
        context_overlap = len(context_tokens & _tokens(title + ' ' + snippet)) / max(1, len(context_tokens))
        score = round((45 if same else 0) + 40 * overlap + 15 * context_overlap)
        reasons = [('Same hostname as the original' if same else 'Different hostname; verify publisher identity'),
                   f'{round(overlap * 100)}% of citation-topic words appear in the result title',
                   'Search result only; page meaning has not been verified']
        candidates.append({'url': url, 'title': title, 'snippet': snippet, 'score': score,
                           'same_host': same, 'reasons': reasons,
                           'warning': 'Anchor retained or supplied; confirm it exists on the replacement page.' if old.fragment or parts.fragment else '',
                           'page_verified': False, 'id': _digest(url)[:16], 'discovery_score': score,
                           'reason_codes': ['SAME_HOST' if same else 'CROSS_DOMAIN', 'SEARCH_TITLE_OVERLAP'],
                           'publication': str(row.get('publication', ''))[:240], 'evidence': None, 'search_sources': []})
    return sorted(candidates, key=lambda c: (-c['score'], c['url']))[:5]


def analyze(source: str, mode='fixture', search=None, checker=None) -> dict:
    if mode not in ('fixture', 'live'):
        raise ValueError('Choose fixture or live mode.')
    if mode == 'live' and not callable(search):
        raise ValueError('Live mode requires an explicit search provider with an existing key.')
    citations = parse_markdown(source)
    if len(citations) > MAX_CITATIONS:
        raise ValueError('This local workbench supports at most 60 distinct citations per document.')
    output, searches = [], 0
    for citation in citations:
        item = asdict(citation)
        item['query'] = ''
        item['search_evidence'] = None
        item['search_note'] = ''
        item['candidates'] = []
        item['ambiguous'] = False
        item['search_history'] = []
        try:
            validate_url(citation.url)
        except NetworkError as error:
            check = {'state': 'blocked', 'status': None, 'verified': False, 'detail': str(error)}
        else:
            check = fixture_check(citation.url) if mode == 'fixture' else (checker or check_url)(citation.url)
        item['check'] = check
        if check['state'] == 'broken':
            if searches >= MAX_SEARCHES:
                item['search_note'] = 'Search budget reached: at most eight queries per analysis.'
            else:
                searches += 1
                item['query'] = _query(citation)
                try:
                    rows = fixture_results(citation.url) if mode == 'fixture' else search(item['query'])
                    if mode == 'live' and isinstance(rows, SearchResults):
                        item['search_evidence'] = dict(rows.evidence)
                    item['candidates'] = _rank(citation, rows)
                    item['search_note'] = ('Authored synthetic search results; no API request made.' if mode == 'fixture'
                                           else 'SerpApi Google Search results; candidate pages have not been fetched.')
                except SearchBudgetError as error:
                    item['search_note'] = str(error)
                except Exception:
                    item['search_note'] = 'Search failed. No replacement has been invented; check your connection, key and search budget.'
                entry = {'strategy': 'publisher', 'engine': 'google', 'query': item['query'],
                         'origin': 'authored_fixture' if mode == 'fixture' else 'live_provider',
                         'receipt': item['search_evidence'], 'note': item['search_note'],
                         'candidate_count': len(item['candidates'])}
                if item['search_evidence'] is None and mode == 'live':
                    provider = getattr(search, '__self__', None)
                    receipt = getattr(provider, 'last_receipt', None)
                    if isinstance(receipt, dict) and receipt.get('query') == item['query']:
                        entry['receipt'] = dict(receipt)
                item['search_history'].append(entry)
                for candidate in item['candidates']:
                    candidate['search_sources'].append(entry)
                ranked = item['candidates']
                item['ambiguous'] = len(ranked) > 1 and abs(ranked[0]['score'] - ranked[1]['score']) <= 8
        item['discovery_ambiguous'] = item['ambiguous']
        output.append(item)
    counts = Counter(c['check']['state'] for c in output)
    return {'version': 2, 'evidence_version': VERSION, 'verification_attempts': 0, 'mode': mode, 'live_verified': False,
            'notice': ('Synthetic fixture demonstration. Statuses and search results are authored sample data, not live verified.'
                       if mode == 'fixture' else 'Live HTTP observations and SerpApi search. Search ranking does not establish factual equivalence.'),
            'source_hash': _digest(source), 'citations': output,
            'analyzed_at': FIXTURE_DATE if mode == 'fixture' else datetime.now(timezone.utc).isoformat(),
            'summary': {'total': len(output), 'broken': counts['broken'], 'healthy': counts['healthy'],
                        'blocked': counts['blocked'], 'uncertain': counts['uncertain'], 'unavailable': counts['unavailable'],
                        'searches': searches, 'search_budget': MAX_SEARCHES}}


def _unified_diff(before, after):
    def lf_lines(text):
        parts = text.split('\n')
        return [line + '\n' for line in parts[:-1]] + ([parts[-1]] if parts[-1] else [])
    lines = difflib.unified_diff(lf_lines(before), lf_lines(after),
                                fromfile='a/guide.md', tofile='b/guide.md', lineterm='\n')
    output = []
    for line in lines:
        if line.endswith('\n'):
            output.append(line)
        else:
            output.append(line + '\n\\ No newline at end of file\n')
    return ''.join(output)


def export_review(source: str, analysis: dict, decisions: dict[str, str | None], *, require_evidence=False) -> dict:
    if analysis.get('source_hash') != _digest(source):
        raise ValueError('The source changed. Analyze it again before exporting.')
    if not isinstance(decisions, dict) or len(decisions) > MAX_CITATIONS:
        raise ValueError('Decisions must be a bounded mapping of citation IDs to approved URLs.')
    by_id = {c['id']: c for c in analysis['citations']}
    changes, replacements, skipped = [], {}, []
    for cid, choice in decisions.items():
        if cid not in by_id:
            raise ValueError('A decision refers to an unknown citation. Analyze again.')
        citation = by_id[cid]
        if choice is None:
            skipped.append(cid)
            continue
        if not isinstance(choice, str):
            raise ValueError('An approved replacement must be a candidate URL.')
        candidate = next((c for c in citation['candidates'] if c['url'] == choice), None)
        if candidate is None:
            raise ValueError('Only candidates shown in this analysis may be approved.')
        if require_evidence and not candidate.get('evidence'):
            raise ValueError('Inspect candidate page evidence before approving a replacement.')
        if candidate.get('evidence') and candidate['evidence']['state'] != 'related':
            raise ValueError('INSUFFICIENT EVIDENCE. LEAVE CITATION UNCHANGED.')
        validate_url(choice)
        replacements[cid] = choice
        changes.append({'citation_id': cid, 'label': citation['label'], 'original_url': citation['url'],
                        'replacement_url': choice, 'approved_by_user': True, 'occurrences': citation['occurrences'],
                        'destination_spans': len(citation['spans']), 'query': citation['query'],
                        'search_evidence': citation.get('search_evidence'),
                        'search_history': citation.get('search_history', []),
                        'approval': {'explicit': True, 'method': 'review_decision', 'identity_authenticated': False},
                        'original_check': citation['check'], 'candidate': candidate, 'ambiguous': citation['ambiguous']})
    patched = apply_replacements(source, replacements)
    provenance = {'tool': 'SourcePatch', 'version': '2.0.0', 'heuristic_version': VERSION, 'mode': analysis['mode'], 'notice': analysis['notice'],
                  'analyzed_at': analysis['analyzed_at'], 'source_sha256': _digest(source), 'output_sha256': _digest(patched),
                  'changes': changes, 'skipped': skipped,
                  'search_history': [{'citation_id': c['id'], **entry} for c in analysis['citations'] for entry in c.get('search_history', [])],
                  'candidate_observations': [{'citation_id': c['id'], 'candidate_id': candidate['id'], 'evidence': candidate['evidence'], 'evidence_history': candidate.get('evidence_history', [])}
                                             for c in analysis['citations'] for candidate in c['candidates'] if candidate.get('evidence')],
                  'unreviewed': [c['id'] for c in analysis['citations'] if c['candidates'] and c['id'] not in decisions],
                  'limitations': ['Ranking scores are heuristics, not probabilities.', 'Page inspection is bounded lexical evidence, not semantic equivalence or factual support.',
                                  'Uninspected legacy approvals have no page evidence; review them independently.',
                                  'HTML only; no JavaScript execution, PDFs, OCR or full CommonMark support.',
                                  'The input document has not been modified. Review and apply the exported patch yourself.']}
    return {'markdown': patched, 'diff': _unified_diff(source, patched), 'provenance': provenance}

STRATEGIES = {'publisher': 'google', 'broad': 'google', 'identifier': 'google', 'scholar': 'google_scholar'}
MAX_VERIFICATIONS = 20


def _citation(analysis, cid):
    if not isinstance(cid, str):
        raise ValueError('A citation ID from this analysis is required.')
    citation = next((c for c in analysis['citations'] if c['id'] == cid), None)
    if citation is None:
        raise ValueError('Unknown citation ID.')
    return citation


def _strategy_query(citation, strategy):
    view = SimpleNamespace(**citation)
    if strategy == 'publisher':
        return _query(view)
    topic = ' '.join(_topic_words(view))
    if strategy == 'identifier':
        ids = sorted(identifiers(urlsplit(citation['url']).path + ' ' + citation['label']))
        if not ids:
            raise ValueError('No supported DOI, arXiv or numeric resource identifier was found.')
        return (' '.join('"' + i.replace('"', '') + '"' for i in ids[:3]) + ' ' + topic)[:500]
    return topic[:500] or urlsplit(citation['url']).hostname


def _sort_candidates(citation):
    citation['candidates'].sort(key=lambda c: (0 if (c.get('evidence') or {}).get('state') == 'related' else 1 if not c.get('evidence') else 2, -c['score'], c['url']))
    ranked = citation['candidates']
    citation['ambiguous'] = len(ranked) > 1 and abs(ranked[0]['score'] - ranked[1]['score']) <= 8
    inspected = [c for c in ranked if c.get('evidence')]
    if len(inspected) < len(ranked):
        citation['ambiguous'] = citation['ambiguous'] or citation.get('discovery_ambiguous', False)
    citation['recommendation'] = ('INSUFFICIENT EVIDENCE. LEAVE CITATION UNCHANGED.'
                                  if not ranked or inspected and not any(c['evidence']['state'] == 'related' for c in inspected)
                                  else 'Review content and publisher identity before explicit approval.')


def discover(analysis, citation_id, strategy, search=None):
    citation = _citation(analysis, citation_id)
    if not isinstance(strategy, str) or strategy not in STRATEGIES:
        raise ValueError('Choose publisher, broad, identifier or scholar search.')
    if citation['check']['state'] != 'broken':
        raise ValueError('Additional discovery is limited to observed broken citations.')
    if analysis['summary']['searches'] >= MAX_SEARCHES:
        raise ValueError('Search budget reached: at most eight queries per analysis.')
    query = _strategy_query(citation, strategy)
    engine = STRATEGIES[strategy]
    analysis['summary']['searches'] += 1
    entry = {'strategy': strategy, 'engine': engine, 'query': query, 'receipt': None,
             'origin': 'authored_fixture' if analysis['mode'] == 'fixture' else 'live_provider',
             'candidate_count': 0, 'note': ''}
    try:
        if analysis['mode'] == 'fixture':
            rows = fixture_results(citation['url']) if strategy == 'publisher' else []
            entry['note'] = 'Authored offline fixture; no provider request. Additional strategies have no authored results.'
        else:
            if not callable(search):
                raise ValueError('Live discovery requires the configured provider.')
            rows = search(query) if engine == 'google' else search(query, engine=engine)
            entry['note'] = 'Live provider discovery; page content requires separate inspection.'
            if isinstance(rows, SearchResults):
                entry['receipt'] = dict(rows.evidence)
        candidates = _rank(SimpleNamespace(**citation), rows)
        entry['candidate_count'] = len(candidates)
        by_url = {c['url']: c for c in citation['candidates']}
        for candidate in candidates:
            if candidate['url'] in by_url:
                by_url[candidate['url']]['search_sources'].append(entry)
            elif len(citation['candidates']) < 20:
                candidate['search_sources'] = [entry]
                citation['candidates'].append(candidate)
    except Exception as error:
        entry['note'] = str(error) if isinstance(error, SearchBudgetError) else 'Search failed; no results invented and no automatic retry made.'
        provider = getattr(search, '__self__', None)
        receipt = getattr(provider, 'last_receipt', None)
        if isinstance(receipt, dict) and receipt.get('query') == query and receipt.get('engine') == engine:
            entry['receipt'] = dict(receipt)
    citation['search_history'].append(entry)
    _sort_candidates(citation)
    return analysis


def verify_candidate(analysis, citation_id, candidate_id, fetch=None, *, retry=False):
    citation = _citation(analysis, citation_id)
    if not isinstance(candidate_id, str):
        raise ValueError('A candidate ID from this analysis is required.')
    candidate = next((c for c in citation['candidates'] if c['id'] == candidate_id), None)
    if candidate is None:
        raise ValueError('Only candidates already in this server-owned analysis can be inspected.')
    if type(retry) is not bool:
        raise ValueError('retry must be a boolean.')
    previous = candidate.get('evidence')
    if retry:
        if not previous or previous['retrieval']['observed']:
            raise ValueError('Only a failed transport observation can be retried.')
        if len(candidate.get('evidence_history', [])) >= 2:
            raise ValueError('Candidate retry budget reached: three total attempts.')
    elif previous:
        return analysis  # Repeated ordinary inspections reuse their observation.
    if analysis['verification_attempts'] >= MAX_VERIFICATIONS:
        raise ValueError('Candidate inspection budget reached: twenty attempts per analysis.')
    analysis['verification_attempts'] += 1
    fixture = analysis['mode'] == 'fixture'
    evidence = inspect_candidate(citation, candidate, fetch=fixture_page if fixture else fetch,
                                 origin='authored_fixture' if fixture else 'direct_page')
    if fixture:
        evidence['retrieval']['retrieved_at'] = FIXTURE_DATE
    if previous:
        candidate.setdefault('evidence_history', []).append(previous)
    candidate['evidence'] = evidence
    # Preserve the legacy no-semantic-verification flag; transport is separate.
    candidate['page_verified'] = False
    candidate['page_inspected'] = not fixture and evidence['retrieval']['observed']
    r = evidence['relevance']
    if evidence['state'] == 'related':
        score = (candidate['discovery_score'] * 0.35 + 25 * r['topic_overlap'] +
                 15 * r['context_overlap'] + 10 * r['title_overlap'] + 10 * r['heading_overlap'] +
                 (3 if r['identifier'] == 'match' else 0) + (2 if evidence['anchor']['state'] == 'found' else 0))
        candidate['score'] = min(100, round(score))
    else:
        candidate['score'] = min(25, round(candidate['discovery_score'] * 0.2))
    candidate['reason_codes'] = list(dict.fromkeys([code for code in candidate['reason_codes'] if not previous or code not in previous['reason_codes']] + evidence['reason_codes']))
    candidate['reasons'] = candidate['reasons'][:2] + [
        f"Inspected content: {evidence['state']}. Lexical evidence only; human review required."]
    _sort_candidates(citation)
    return analysis

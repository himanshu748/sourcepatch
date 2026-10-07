"""Deterministic evidence ranking and explicit, source-checked review exports."""
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import difflib
import hashlib
import re
from urllib.parse import unquote, urlsplit, urlunsplit

from .fixtures import FIXTURE_DATE, fixture_check, fixture_results
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
    return ('site:' + host + ' ' + ' '.join(words[:14]))[:500]


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
                           'page_verified': False})
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
                ranked = item['candidates']
                item['ambiguous'] = len(ranked) > 1 and ranked[0]['score'] - ranked[1]['score'] <= 8
        output.append(item)
    counts = Counter(c['check']['state'] for c in output)
    return {'version': 1, 'mode': mode, 'live_verified': False,
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


def export_review(source: str, analysis: dict, decisions: dict[str, str | None]) -> dict:
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
        validate_url(choice)
        replacements[cid] = choice
        changes.append({'citation_id': cid, 'label': citation['label'], 'original_url': citation['url'],
                        'replacement_url': choice, 'approved_by_user': True, 'occurrences': citation['occurrences'],
                        'destination_spans': len(citation['spans']), 'query': citation['query'],
                        'search_evidence': citation.get('search_evidence'),
                        'original_check': citation['check'], 'candidate': candidate, 'ambiguous': citation['ambiguous']})
    patched = apply_replacements(source, replacements)
    provenance = {'tool': 'SourcePatch', 'version': '0.1.0', 'mode': analysis['mode'], 'notice': analysis['notice'],
                  'analyzed_at': analysis['analyzed_at'], 'source_sha256': _digest(source), 'output_sha256': _digest(patched),
                  'changes': changes, 'skipped': skipped,
                  'unreviewed': [c['id'] for c in analysis['citations'] if c['candidates'] and c['id'] not in decisions],
                  'limitations': ['Ranking scores are heuristics, not probabilities.', 'Candidate page contents and fragment anchors are not verified.',
                                  'The input document has not been modified. Review and apply the exported patch yourself.']}
    return {'markdown': patched, 'diff': _unified_diff(source, patched), 'provenance': provenance}

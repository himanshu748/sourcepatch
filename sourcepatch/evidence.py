"""Bounded, non-executing page observations; lexical relevance is not truth."""
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import re
from urllib.parse import unquote, urlsplit

from .network import NetworkError, safe_get, validate_url

VERSION = 'lexical-evidence-2.0'
MAX_BYTES = 524_288
STOP = {'a', 'an', 'the', 'to', 'of', 'and', 'in', 'for', 'is', 'it', 'on', 'with',
        'this', 'that', 'use', 'see', 'read', 'here', 'https', 'http', 'www'}


def tokens(text):
    text = re.sub(r'https?://[^\s)]+', ' ', text)
    return set(re.findall(r'[^\W_]+', text.casefold(), re.UNICODE)) - STOP


def identifiers(text):
    """Conservative DOI, arXiv and numeric resource identifiers; never query secrets."""
    text = unquote(text).casefold()
    return set(re.findall(r'10\.\d{4,9}/[^\s?#<>]+|\b\d{4}\.\d{4,5}(?:v\d+)?\b|(?<![\w.])\d{6,20}(?![\w.])', text))


def clean(text):
    return ' '.join(text.split())


class PageText(HTMLParser):
    """At most 64k text characters and bounded metadata retained transiently."""
    OMIT = {'script', 'style', 'noscript', 'template', 'svg', 'nav', 'footer', 'header'}
    BLOCK = {'p', 'div', 'section', 'article', 'li', 'br', 'tr', 'blockquote', 'pre'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.title = []
        self.headings = []
        self.current_heading = []
        self.blocks = []
        self.current = []
        self.anchors = set()
        self.remaining = 64_000
        self.text_truncated = False
        self.has_html = False

    def flush(self):
        value = clean(' '.join(self.current))
        if value:
            self.blocks.append(value)
        self.current = []

    def handle_starttag(self, tag, attrs):
        self.has_html = True
        if len(self.stack) >= 256:
            raise ValueError('HTML nesting exceeds extraction limit.')
        attrs = dict(attrs)
        hidden = bool(self.stack and self.stack[-1][1]) or tag in self.OMIT or 'hidden' in attrs or attrs.get('aria-hidden', '').lower() == 'true'
        if not hidden:
            for key in ('id', 'name'):
                if attrs.get(key) and len(self.anchors) < 4096:
                    self.anchors.add(attrs[key][:512])
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, hidden))
        if tag in self.BLOCK or tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.flush()
        if tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.current_heading = []

    def handle_endtag(self, tag):
        if tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            heading = clean(' '.join(self.current_heading))[:120]
            if heading and len(self.headings) < 12:
                self.headings.append(heading)
            self.current_heading = []
        if tag in self.BLOCK or tag.startswith('h'):
            self.flush()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1][1]:
            return
        if len(data) > self.remaining:
            self.text_truncated = True
        data = data[:self.remaining]
        self.remaining -= len(data)
        if not data.strip():
            return
        tags = {tag for tag, _ in self.stack}
        if 'title' in tags:
            self.title.append(data)
            return
        if tags & {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.current_heading.append(data)
            return
        self.current.append(data)


def inspect_candidate(citation, candidate, fetch=None, *, origin='direct_page'):
    """Call only for a server-owned candidate. Does not accept browser URL input."""
    url = candidate['url']
    fragment = unquote(urlsplit(url).fragment)
    evidence = {'version': VERSION, 'origin': origin, 'state': 'inconclusive',
                'title': '', 'headings': [], 'excerpts': [], 'content_sha256': None,
                'anchor': {'fragment': fragment, 'state': 'unknown' if fragment else 'not_requested'},
                'retrieval': {'observed': False, 'requested_url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat()},
                'reason_codes': [], 'warnings': ['Lexical overlap does not establish factual support or semantic equivalence.',
                             'INSUFFICIENT EVIDENCE. LEAVE CITATION UNCHANGED.'],
                'relevance': {}}
    try:
        validate_url(url)
        result = (fetch or safe_get)(url, timeout=8, max_bytes=MAX_BYTES, max_redirects=3)
    except Exception:
        evidence['reason_codes'].append('RETRIEVAL_FAILED')
        evidence['warnings'].append('Page retrieval failed or was blocked by network policy; no evidence invented.')
        return evidence
    evidence['retrieval'].update(observed=True, status=result.status, final_url=result.url,
                                 bytes=len(result.body), truncated=result.truncated,
                                 content_type=getattr(result, 'content_type', ''))
    evidence['content_sha256'] = hashlib.sha256(result.body).hexdigest()
    if urlsplit(result.url).hostname != urlsplit(citation['url']).hostname:
        evidence['reason_codes'].append('CROSS_DOMAIN')
        evidence['warnings'].append('Different hostname; verify publisher identity, including redirects.')
    if not 200 <= result.status < 300:
        evidence['reason_codes'].append('HTTP_UNAVAILABLE')
        return evidence
    content_type = getattr(result, 'content_type', '').lower()
    if (content_type and not any(t in content_type for t in ('text/html', 'application/xhtml+xml'))) or result.body.lstrip().startswith(b'%PDF'):
        evidence['reason_codes'].append('UNSUPPORTED_CONTENT')
        return evidence
    charset = re.search(r'charset=["\x27]?([\w-]+)', content_type)
    try:
        html = result.body.decode(charset[1] if charset else 'utf-8', errors='replace')
    except LookupError:
        evidence['reason_codes'].append('UNSUPPORTED_ENCODING')
        return evidence
    parser = PageText()
    try:
        parser.feed(html)
        parser.close()
        parser.flush()
    except Exception:
        evidence['reason_codes'].append('EXTRACTION_FAILED')
        return evidence
    evidence['title'] = clean(' '.join(parser.title))[:240]
    evidence['headings'] = parser.headings
    if fragment:
        evidence['anchor']['state'] = ('found' if fragment in parser.anchors else
                                      'unknown' if result.truncated or ':~:text=' in fragment else 'missing')
        evidence['reason_codes'].append('ANCHOR_' + evidence['anchor']['state'].upper())
    # Exclude the original destination so URL tokens do not masquerade as context.
    label = citation['label']
    if label == citation['url'] or not tokens(label) - {'docs', 'documentation', 'link', 'source'}:
        label = unquote(urlsplit(citation['url']).path)
    topic = tokens(label)
    context = tokens(citation['context'].replace(citation['url'], ''))
    ranked_blocks = sorted(enumerate(parser.blocks), key=lambda pair: (-len(tokens(pair[1]) & (topic | context)), pair[0]))
    excerpts = []
    for _, block in ranked_blocks:
        if not tokens(block) & (topic | context):
            continue
        # Select a local window around the first relevant term, bounded to 240 chars.
        matches = list(re.finditer(r'[^\W_]+', block, re.UNICODE))
        start = next((max(0, m.start() - 60) for m in matches if m[0].casefold() in topic | context), 0)
        excerpt = block[start:start + 240]
        if excerpt not in excerpts:
            excerpts.append(excerpt)
        if len(excerpts) == 3:
            break
    evidence['excerpts'] = excerpts
    body_tokens = tokens(' '.join(parser.blocks))
    body_overlap = len(topic & body_tokens) / max(1, len(topic))
    heading_overlap = len(topic & tokens(' '.join(parser.headings))) / max(1, len(topic))
    title_overlap = len(topic & tokens(evidence['title'])) / max(1, len(topic))
    context_overlap = len(context & body_tokens) / max(1, len(context))
    old_ids = identifiers(urlsplit(citation['url']).path + ' ' + citation['label'])
    new_ids = identifiers(urlsplit(result.url).path + ' ' + ' '.join(parser.blocks) + ' ' + evidence['title'])
    identity = 'not_requested' if not old_ids else 'match' if old_ids & new_ids else 'mismatch' if new_ids else 'unobserved'
    evidence['relevance'] = {'topic_overlap': round(body_overlap, 3), 'context_overlap': round(context_overlap, 3),
                             'title_overlap': round(title_overlap, 3), 'heading_overlap': round(heading_overlap, 3),
                             'identifier': identity}
    if old_ids:
        evidence['reason_codes'].append('IDENTIFIER_' + identity.upper())
    if result.truncated or parser.text_truncated:
        evidence['reason_codes'].append('TRUNCATED_CONTENT')
        evidence['warnings'].append('Only a bounded prefix was inspected; absent content may occur beyond the limit.')
    elif not parser.has_html or len(body_tokens) < 3:
        evidence['reason_codes'].append('NO_READABLE_CONTENT')
    elif '\ufffd' in html:
        evidence['reason_codes'].append('DECODING_LOSS')
    elif (body_overlap >= 0.5 and len(topic & body_tokens) >= min(2, len(topic))
          and context_overlap >= 0.2 and identity not in ('mismatch', 'unobserved')
          and evidence['anchor']['state'] in ('found', 'not_requested')):
        evidence['state'] = 'related'
        evidence['reason_codes'].append('CONTENT_TOPIC_OVERLAP')
    else:
        evidence['state'] = 'insufficient'
        evidence['reason_codes'].append('CONTENT_UNRELATED' if body_overlap < 0.2 else 'CONTENT_INSUFFICIENT')
    if evidence['state'] == 'related':
        evidence['warnings'].remove('INSUFFICIENT EVIDENCE. LEAVE CITATION UNCHANGED.')
    return evidence

"""Conservative Markdown scanning that never serializes the source document.

This is deliberately not a complete CommonMark implementation. Unsupported
constructs are left untouched. Spans refer to Python Unicode string offsets.
"""
from bisect import bisect_right
from dataclasses import dataclass, field
import hashlib
import re
from urllib.parse import quote

MAX_SOURCE = 200_000


@dataclass(frozen=True)
class Span:
    start: int
    end: int


@dataclass
class Citation:
    id: str
    url: str
    label: str
    context: str
    spans: list[Span] = field(default_factory=list)
    occurrences: int = 0


def _escaped(text, pos):
    n = 0
    while pos > 0 and text[pos - 1] == '\\':
        pos -= 1
        n += 1
    return n % 2 == 1


def _mask_source(source):
    """Replace excluded syntax with spaces without changing source offsets."""
    masked = list(source)

    def blank(start, end):
        for i in range(start, end):
            if masked[i] not in '\r\n':
                masked[i] = ' '

    fence = None
    offset = 0
    for line in source.splitlines(keepends=True):
        m = re.match(r'^ {0,3}(?:(?:>[ \t]?|(?:[-+*]|[0-9]+[.)])[ \t]+)[ \t]*)*(`{3,}|~{3,})(.*)', line)
        if fence:
            blank(offset, offset + len(line))
            if m and m[1][0] == fence[0] and len(m[1]) >= fence[1] and not m[2].strip():
                fence = None
        elif m:
            fence = (m[1][0], len(m[1]))
            blank(offset, offset + len(line))
        elif line.startswith(('    ', '\t')) or re.match(r'^(?: {0,3}> ?)+[ \t]{4}', line):
            blank(offset, offset + len(line))
        offset += len(line)
    # HTML blocks/comments are not Markdown citation inputs.
    current = ''.join(masked)
    for m in re.finditer(r'<!--.*?(?:-->|\Z)|<(script|style|pre|code|textarea|div|table|section|article|aside|p|details|summary|ul|ol|li|blockquote|form|iframe)\b[^>]*>.*?(?:</\1\s*>|\Z)', current, re.I | re.S):
        blank(m.start(), m.end())
    current = ''.join(masked)
    for m in re.finditer(r'<!\[CDATA\[.*?(?:\]\]>|\Z)|<\?.*?(?:\?>|\Z)|<![A-Z].*?(?:>|\Z)', current, re.S):
        blank(m.start(), m.end())
    current = ''.join(masked)
    covered_until = -1
    for m in re.finditer(r'^ {0,3}</?[A-Za-z][\w-]*(?:[ \t][^>\n]*)?/?>[ \t]*$', current, re.M):
        if m.start() < covered_until:
            continue
        ending = re.search(r'\n[ \t]*\r?\n', current[m.end():])
        covered_until = m.end() + ending.end() if ending else len(current)
        blank(m.start(), covered_until)
    current = ''.join(masked)
    for m in re.finditer(r'</?[A-Za-z][\w-]*(?:\s[^<>]*?)?/?>', current, re.S):
        blank(m.start(), m.end())
    current = ''.join(masked)
    i = 0
    while i < len(current):
        if current[i] == '`' and not _escaped(current, i):
            j = i
            while j < len(current) and current[j] == '`':
                j += 1
            run = current[i:j]
            closing = re.search(r'(?<!`)' + re.escape(run) + r'(?!`)', current[j:])
            if closing:
                end = j + closing.end()
                blank(i, end)
                i = end
                continue
            i = j
        else:
            i += 1
    return ''.join(masked)


def _label_id(label):
    return ' '.join(label.split()).casefold()


def _bracket_pairs(text):
    """Match square brackets once, in linear work, including malformed input."""
    stack, pairs = [], {}
    escaped = False
    for i, ch in enumerate(text):
        if escaped:
            escaped = False
        elif ch == '\\':
            escaped = True
        elif ch == '[':
            stack.append(i)
        elif ch == ']' and stack:
            start = stack.pop()
            if i - start <= 4000:
                pairs[start] = i
    return pairs


def _destination(text, start, inline):
    """Return destination span and syntax end, or None for unsupported syntax."""
    i = start
    limit = min(len(text), start + 4097)
    while i < limit and text[i] in ' \t':
        i += 1
    if i >= len(text):
        return None
    if text[i] == '<':
        begin = i + 1
        end = text.find('>', begin, limit)
        if end < 0 or any(c.isspace() for c in text[begin:end]):
            return None
        finish = end + 1
    else:
        begin = i
        depth = 0
        absolute_http = text[begin:begin + 8].lower().startswith(('https://', 'http://'))
        while i < limit:
            ch = text[i]
            if not absolute_http and ch in '[]':
                return None
            if ch.isspace() or ch == '<':
                break
            if ch == '(' and not _escaped(text, i):
                depth += 1
            elif ch == ')' and not _escaped(text, i):
                if depth == 0:
                    break
                depth -= 1
            i += 1
        if depth or i == begin or i == limit and limit < len(text):
            return None
        end, finish = i, i
    if inline:
        tail = text[finish:finish + 2000]
        m = re.match(r'''[ \t]*(?:(?:"(?:\\.|[^"\r\n])*"|'(?:\\.|[^'\r\n])*')[ \t]*)?\)''', tail)
        if not m:
            return None
        finish += m.end()
    else:
        tail = text[finish:finish + 2000].split('\n', 1)[0].rstrip('\r')
        if tail.strip() and not re.fullmatch(r'''[ \t]+(?:"(?:\\.|[^"\r\n])*"|'(?:\\.|[^'\r\n])*')[ \t]*''', tail):
            return None
    return Span(begin, end), finish


def parse_markdown(source: str) -> list[Citation]:
    if not isinstance(source, str) or len(source) > MAX_SOURCE:
        raise ValueError('Markdown must be text of at most 200,000 characters.')
    text = _mask_source(source)
    definitions = {}
    definition_ranges = []
    for m in re.finditer(r'^ {0,3}\[([^\]\n]+)\]:[ \t]*', text, re.M):
        dest = _destination(text, m.end(), False)
        if dest:
            span, _ = dest
            label = _label_id(m[1])
            definitions.setdefault(label, span)
            line_end = text.find('\n', m.end())
            definition_ranges.append((m.start(), len(text) if line_end < 0 else line_end))
    chars = list(text)
    for start, end in definition_ranges:
        chars[start:end] = ' ' * (end - start)
    text = ''.join(chars)
    matches = []
    brackets = _bracket_pairs(text)
    image_refs = set()
    consumed = []
    autolinks = list(re.finditer(r'<(https?://[^\s<>]+)>', text, re.I))
    autolink_starts = [m.start() for m in autolinks]
    # Images may be nested inside a link label, consumed by the outer scanner.
    for image in re.finditer(r'!\[', text):
        if _escaped(text, image.start()):
            continue
        image_end = brackets.get(image.start() + 1)
        if image_end is None:
            continue
        ref = _label_id(text[image.start() + 2:image_end])
        after_image = image_end + 1
        if after_image < len(text) and text[after_image] == '[':
            ref_end = brackets.get(after_image)
            if ref_end is not None:
                ref = _label_id(text[after_image + 1:ref_end] or ref)
        elif after_image < len(text) and text[after_image] == '(':
            continue
        if ref in definitions:
            image_refs.add(ref)
    i = 0
    while i < len(text):
        if text[i] != '[' or _escaped(text, i):
            i += 1
            continue
        interval = bisect_right(autolink_starts, i) - 1
        if interval >= 0 and autolinks[interval].start() < i < autolinks[interval].end():
            i = autolinks[interval].end()
            continue
        end = brackets.get(i)
        if end is None:
            i += 1
            continue
        label = source[i + 1:end]
        is_image = i > 0 and text[i - 1] == '!' and not _escaped(text, i - 1)
        after = end + 1
        if after < len(text) and text[after] == '(':
            dest = _destination(text, after + 1, True)
            if dest:
                consumed.append((i, dest[1]))
                if not is_image:
                    matches.append((dest[0], label, i, None))
                i = dest[1]
                continue
        ref = _label_id(label)
        if after < len(text) and text[after] == '[':
            ref_end = brackets.get(after)
            if ref_end is not None:
                ref = _label_id(text[after + 1:ref_end] or label)
                after = ref_end + 1
        if ref in definitions:
            consumed.append((i, after))
            if is_image:
                image_refs.add(ref)
            else:
                matches.append((definitions[ref], label, i, ref))
        i = after
    used = consumed
    used_starts = [start for start, _ in used]
    for m in autolinks:
        interval = bisect_right(used_starts, m.start() + 1) - 1
        inside = interval >= 0 and used[interval][0] <= m.start() + 1 < used[interval][1]
        if not _escaped(text, m.start()) and not inside:
            matches.append((Span(m.start() + 1, m.end() - 1), m[1], m.start(), None))
    citations = {}
    span_sets = {}
    for span, label, position, ref in sorted(matches, key=lambda item: item[2]):
        if ref in image_refs:
            continue
        url = source[span.start:span.end]
        if not re.match(r'^https?://', url, re.I):
            continue
        if '\\' in url:
            continue
        cid = hashlib.sha256(url.encode()).hexdigest()[:16]
        if cid not in citations:
            line_start = source.rfind('\n', 0, position) + 1
            line_end = source.find('\n', position)
            context = source[line_start:len(source) if line_end < 0 else line_end].strip()[:240]
            display_label = re.sub(r'\\([\[\]\\])', r'\1', label).strip()
            citations[cid] = Citation(cid, url, display_label or url, context)
            span_sets[cid] = set()
        c = citations[cid]
        if span not in span_sets[cid]:
            c.spans.append(span)
            span_sets[cid].add(span)
        c.occurrences += 1
    return list(citations.values())


def apply_replacements(source: str, replacements: dict[str, str]) -> str:
    changes = []
    for citation in parse_markdown(source):
        if citation.id not in replacements:
            continue
        replacement = quote(replacements[citation.id], safe=':/?#[]@!$&*+,;=%~._-')
        changes.extend((span.start, span.end, replacement) for span in citation.spans)
    ordered = sorted(changes)
    if any(left[1] > right[0] for left, right in zip(ordered, ordered[1:])):
        raise ValueError('Unsupported overlapping citation spans; no patch was generated.')
    for start, end, replacement in sorted(changes, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source

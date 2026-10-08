# Security and privacy

SourcePatch is a single-user local prototype. Keep it on loopback. Do not expose it through a public tunnel or reverse proxy without a separate security design and review.

## Source and review boundary

Markdown is capped at 200,000 characters and 60 distinct citations. It is displayed using DOM textContent, never executed as HTML. Exact source spans identify eligible replacements. Destination encoding prevents closing Markdown syntax. The server retains the source with a random analysis ID and checks its SHA-256 before export. Browser-supplied source content cannot replace the stored analysis input.

This is a conservative Markdown subset, not a full CommonMark parser. Complex constructs may be skipped. Images sharing a reference definition with text are protected; overlapping destination spans fail closed. No source file is overwritten. Always review the exported diff.

## Network boundary

Fixture mode makes no network or DNS requests. Live requests allow only absolute HTTP(S) URLs on default ports, without URL credentials, unsafe characters, scoped IPs, ambiguous numeric hosts or local-name suffixes. IP literals and every DNS answer must be globally routable and not reserved, multicast, private or transition-encoded. Connections are pinned to validated addresses; HTTPS uses hostname-verified TLS/SNI.

Every redirect is revalidated. Link checks allow up to three redirects; the credential-bearing SerpApi request allows none. No environment proxy, cookie or authorization header is forwarded to cited sites. DNS uses bounded daemon workers, a caller deadline and at most four outstanding workers; a stuck OS lookup can continue in a daemon thread but cannot indefinitely block the request.

Link checks use a five-second total deadline and read at most 4,096 bytes. SerpApi uses ten seconds and at most 262,144 bytes; truncated API output is rejected. Connection/TLS timeouts, remaining per-read time and a transport-shutdown watchdog bound slow responses, including detached HTTP/1.0 transports. Responses are explicitly closed. Candidate inspection reuses this transport with an eight-second deadline, three redirects and a 524,288-byte cap. HTML is parsed without executing scripts; unsupported, truncated or unreadable content is inconclusive. Full page bodies are not persisted.

These are defense-in-depth controls, not formal certification or a replacement for an egress firewall. They cannot protect a compromised machine or unsafe deployment.

## Local server

The server binds to 127.0.0.1. Host must match its loopback host/port; foreign Origin and cross-site requests are rejected. API writes require JSON. Only three static assets are served. Responses use CSP, frame denial, no-referrer, no-store and nosniff; no CORS. Analyze, discover, candidate inspection and export share one operation gate; contention returns 429. Only eight recent analyses remain in memory. New discovery and verification routes require stored analysis/citation/candidate IDs and reject extra fields, including target URLs. Twenty inspection attempts per analysis and sixty-four per process bound page fetches. Repeated inspection returns the stored observation, including failures.

Local processes are not separately authenticated. Anyone controlling the OS account, browser or process memory can access local data. OS swap, downloaded reports and terminal history lie outside application guarantees.

## Credentials and private data

Only an existing SerpApi key can be entered, through an interactive no-echo terminal prompt. Echo failure/noninteractive input is rejected. Keys are not taken from command arguments or environment files, saved, logged, sent to the browser or exported. The API requires the key in its HTTPS query; process memory and external debug traces can therefore contain it.

Live mode transmits citation URLs and generated label/hostname queries. Never paste secrets or confidential documents. Reports contain original/replacement URLs, labels and queries; review before sharing. Search results are untrusted, and rankings do not establish equivalent meaning. No telemetry or runtime model calls occur.

## Reporting

Report security findings privately to the repository owner through the channel where you received this code. Do not include real keys or private documents in public reports.

## Evidence is untrusted content

Page titles, headings and excerpts render as literal textContent. At most 64,000 text characters are processed, nesting is capped at 256, and only three excerpts of 240 characters are exported. Inline CSS visibility is not fully interpreted; text extraction is an approximation, not a browser rendering proof. Matching words or identifiers may be misleading. Publisher identity, factual support and semantic equivalence require review. An inspected insufficient/inconclusive candidate is rejected by export; legacy uninspected manual approvals remain accepted with explicit limitations.

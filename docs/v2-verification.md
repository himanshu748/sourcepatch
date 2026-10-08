# V2 verification — October 8, 2026

## Baseline preservation

Work starts at submitted GitHub revision `34ab8ee190d3e5d537b5ce195e8d07b6f8749333`, preserved as local branch `preserve/submitted-2026-10-08`. V2 lives on `sourcepatch-v2`; the existing hosted repository and portal entry were not replaced. All original 88 Python tests remain unchanged.

The host's default `/usr/bin/python3` is 3.9, below the project's existing 3.11 minimum. Its initial import failures are retained as an unsupported-runtime diagnostic. The supported baseline on Homebrew Python **3.13.15** passes 88 tests; all original UI modes pass. [Baseline log](evidence/v2/baseline-python.txt).

## Final executed checks

| Check | Result | Evidence |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | 110 pass, 8.883 seconds | [Python log](evidence/v2/python-tests.txt) |
| `python3 -m compileall -q sourcepatch` | pass | command executed with supported Python; no diagnostics |
| `node --check web/app.js` | pass | command completed with no syntax diagnostics |
| `node scripts/check-ui.mjs` | 28 original assertions pass | [normal](evidence/v2/ui-normal.txt) |
| `node scripts/check-ui.mjs --delayed-config` | 32 original assertions pass | [delayed](evidence/v2/ui-delayed.txt) |
| `node scripts/check-ui.mjs --live-config` | 10 mocked live assertions pass | [mocked receipts](evidence/v2/ui-live-mock.txt) |
| `node scripts/check-ui.mjs --v2` | 28 original + 12 new assertions pass | [V2](evidence/v2/ui-v2.txt) |
| `python3 scripts/benchmark.py` | 13-case reproducible report generated | [results](evidence/v2/benchmark.json), [methodology](benchmark.md) |
| Real browser at 1440×1000 and 390×844 | focused workflow passed | [browser receipt](evidence/v2/browser-receipt.json) |

The new cases include an evidence-group ordering regression that prevents far-apart scores from being mislabeled close matches, plus bounded extraction, irrelevant HTTP-200 content, heading-only false relevance, HTML nesting, missing anchors, private addresses and unsafe redirects, content hashes, identifier mismatch, normalized engine caching, Scholar parsing, sanitized failed receipts, explicit discovery budgets, candidate membership, stale analyses, operation concurrency, abstention, exact duplicate replacement, provenance and account allowance preflight.

During development one run found a short irrelevant-body categorization error; the body-content rule was corrected without changing the test. The same run hit the existing 270ms transport deadline assertion under host load (354ms). No deadline or test threshold was weakened. The focused network suite then passed in 0.779 seconds and the final complete suite passed. [Retained development failure log](evidence/v2/pre-final-failures.txt).

## Browser evidence

Executed against the actual local server and app.js, not recreated screenshots: select candidate, inspect authored page, read evidence, explicitly approve, preview duplicate URL-only patch, download provenance, inspect an unavailable candidate, observe disabled approval and exact abstention message, skip to an empty patch, and edit source to invalidate decisions. The downloaded provenance's input/output hashes were independently checked against the expected two destination changes. [Actual fixture provenance](evidence/v2/browser-fixture-provenance.json) is annotated as agent-operated test review.

At 390px, document scroll width equals viewport width (390). A keyboard Tab check observed a solid 3px focus outline. No browser error logs were observed. The loaded reduced-motion CSS disables transitions/animations; the DOM harness exercises the reduced-motion scroll branch. The real browser preference was false and dynamic reduced-motion emulation was unavailable. Full keyboard traversal, assistive-technology testing and measured contrast certification remain outstanding.

## Live evidence boundaries

A new direct public-page request through V2 `safe_get` returned HTTP 200 and 268,011 bytes for the Python pathlib candidate already present in the October 7 real provider analysis. V2 extracted its title, headings, short body excerpts and hash, yielding lexical state `related`. [Fresh-page evidence](evidence/v2/historical-search-fresh-page.json) retains the original search receipt and the new page timestamp separately. It includes no new approval or patch and does not prove semantic equivalence.

The subsequent authenticated dashboard visit recovered the existing key through a clipboard-to-process handoff, cleared the clipboard, and checked the Account API: Active Free Plan, price 0, 231 searches remaining. One fresh V2 SerpApi request returned five candidates but missed the canonical Python page. The selected candidate exceeded the page-size bound, so inspection was inconclusive and approval was disabled. Skipping exported zero changes with identical source/output hashes. [Fresh live receipt and abstention proof](evidence/v2/live/README.md), [actual provenance](evidence/v2/live/provenance.json). This is a successful provider/inspection/abstention flow, not a successful repair. No additional search was made. Scholar remains covered by controlled tests only.

`python3 scripts/live-proof.py` provides a reproducible no-echo account preflight and one-attempt server. It checks current active allowance before search, never purchases credits, and refuses to proceed on unknown/inactive/zero allowance. A real V2 recording remains pending; [the 2:40 storyboard](demo-script.md) is prepared.

## Publication and submission

GitHub CLI reported that the configured `himanshu748` keyring token is invalid. V2 is delivered locally with its baseline branch and reviewable changes; no push or PR creation is claimed. The existing public V1 repository/demo remain unchanged.

The official [tracks/checklist](https://serpapi.github.io/serpapi-india-hackathon-2026/) and [submission landing page](https://serpapi.github.io/serpapi-india-hackathon-2026/submit.html) were checked. Knowledge & Public Interest exists; the deadline is October 10, 2026, 11:59 PM IST. Authenticated existing-entry fields were not reverified. No portal modification or duplicate submission occurred.

## Product limitations

Lexical overlap can miss paraphrases and can be fooled by on-topic but misleading text. HTML extraction does not execute JavaScript, parse PDFs, perform OCR or fully model CSS visibility. Publisher consistency is a hostname clue, not verified publisher identity. The parser remains a conservative Markdown subset. Truncated/unsupported content stays inconclusive. To preserve old clients and tests, explicit uninspected approvals remain supported and labeled unverified; inspected insufficient evidence blocks export. Approval markers record an explicit client decision, not authenticated human identity. No formal security certification is claimed.

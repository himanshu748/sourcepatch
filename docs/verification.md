# Verification record

Reconstructed build: October 1, 2026. This document distinguishes executed checks from work still outstanding.

## Executed checks

- 80 Python unittest cases pass on October 7 after the complete-response transport fix, including controlled-loopback transport tests; the original reconstructed suite had 61 cases
- 28 normal, 32 delayed-configuration and 10 mocked live-receipt DOM-contract assertions pass against the actual app.js
- Python compilation and JavaScript syntax checks pass
- One actual HTTP 404 → uncached SerpApi Success response → explicit agent-operated UI approval → URL-only export was verified October 7 for an authored typo; broader real-document performance remains unmeasured
- The regenerated synthetic patch passes GNU patch dry-run and produces the same bytes as the exported patched Markdown
- Credential/private-reference scans are performed before packaging

Current command output is retained in evidence/. Historical pre-recovery logs were lost and have not been recreated or presented as original evidence. This is a reconstructed snapshot, not a byte-identical recovery of the earlier archive.

## Covered behavior

- Inline/reference spans, duplicate grouping, image/code/HTML exclusions and exact surrounding source preservation
- Nested image references, overlapping-looking autolinks, list/blockquote fences and unclosed HTML
- Bounded delimiter work on malformed and repeated input
- Unsafe scheme, credentials, port, IP, DNS and redirect rejection
- IP-pinned requests, absolute response deadlines and explicit detached-response cleanup
- Fixture mode makes no network calls; ambiguous candidates and explicit decisions
- Stale source/unknown candidate rejection and export against server-owned input
- Local API body limits, Host/Origin policy and JSON-only requests
- No-echo key entry and refusal of noninteractive fallback
- UI configuration race, literal hostile labels, undo, rescan invalidation and empty states
- Valid unified diffs with LF, CRLF, Unicode separators and lone carriage returns
- Hypothetical demo approvals explicitly labeled as such

## Remaining verification

- Broader real-document citation repair, cross-domain relocation and automated candidate meaning/anchor verification
- No complete keyboard, screen-reader or measured contrast verification
- No formal security certification
- Organizer eligibility has not been established; the existing portal entry remains **SUBMITTED** and was updated October 7 with the real SerpApi demo

The earlier build environment rejected local browser access. Subsequent rendered fixture-browser QA on October 4 is recorded below; it does not establish live integration or a complete accessibility audit.

## October 4 fixture-browser evidence

The workspace receipt `sourcepatch-demo/browser-receipt.json` records seven checks against the public main snapshot at `http://127.0.0.1:8766`: visible synthetic-fixture disclosure and five destinations; explicit approval and URL-only preview with source unchanged; three completed downloads with fixture provenance; skip and undo; source-edit invalidation; no horizontal overflow at 390×844; and no page errors or external requests. A focused anchor had a solid outline; complete keyboard order was not audited.

Screenshots and a labeled fixture recording exist in the workspace. The recording metadata reports H.264, 1440×1000, 25 fps and 44.28 seconds. The video demonstrates authored fixtures and is not proof of a live SerpApi request. The separate landing added later includes the labelled fixture recording and its own dated captures; this historical browser receipt does not certify later source changes.

October 4 regression-suite execution was initially rejected by automatic approval review under the original read-only scope. The user later explicitly approved the offline command. The October 1 checked-in test logs remain historical evidence.

## October 4 local search-budget change

The local branch adds `--max-searches` (integer 1–8, default 8), counts attempted provider calls before fetching, retains cache hits after exhaustion, and discloses the configured process allowance in the CLI, browser configuration and exhaustion notice. The separate eight-query analysis cap and `live_verified: false` remain unchanged.

After explicit execution approval, the final edited suite passed **68 Python tests** in 23.601 seconds with mocked search responses, fake keys and controlled loopback transports. The complete output is retained in [search-budget-python-tests.txt](evidence/search-budget-python-tests.txt). These tests establish offline behavior only; no real SerpApi key, provider request or live citation repair was verified.

The real `web/app.js` also passed **28 normal**, **32 delayed-configuration**, and **4 mocked live-configuration DOM-contract assertions**. Outputs are retained in [normal](evidence/search-budget-ui-contract.txt), [delayed](evidence/search-budget-ui-delayed.txt), and [configured-budget](evidence/search-budget-ui-budget.txt) evidence logs. The last mode checks the one-call disclosure and confirms live mode waits for explicit inspection; it makes no provider request. Python compilation, JavaScript syntax and `git diff --check` passed. These harness checks do not establish browser layout, accessibility or live integration.

The first sandbox baseline run executed 54 tests with four errors: two existing five-second CLI subprocess startup timeouts and two denied loopback binds. The first edited run had the same environment restrictions and two additional invalid-argument subcase startup timeouts. With controlled-loopback permission, the unchanged baseline ran all 61 cases: 59 passed and two existing CLI subprocess starts exceeded five seconds. A serial CLI-only baseline retry repeated those two timeouts. The edited branch increases only the CLI test supervisor allowance from five to 30 seconds; it makes no product or network deadline change. Invalid-budget tests exercise the actual CLI parser in-process and assert that terminal, key-input and server work are never reached. Original and retry logs are preserved separately in the workspace.

## October 7 topic discovery and response receipts

The local branch improves generic-label/autolink discovery by using decoded URL path topics, without query strings or fragments. The same topic guides ranking. Descriptive labels retain their existing queries. Search remains scoped to the original hostname; this does not solve cross-domain migrations.

The SerpApi adapter returns an isolated, list-compatible response receipt: fixed provider/engine, observed HTTP status, local retrieval time, response SHA256, eligible-result count and cache use, plus an optional strictly validated search ID and completed provider status. Raw metadata, request URLs and credentials are excluded. Processing/error statuses are rejected without creating a successful cache entry. The UI exposes receipt/query details even for empty candidate lists; approved changes carry the receipt into provenance. Cache use keeps the original response timestamp and consumes no new allowance. Candidate meaning and anchors remain unverified; `live_verified` remains false.

The full suite passed **76 tests in 1.605 seconds** using Python 3.12 with controlled loopback permission. Output is retained in [finish-python-tests-2026-10-07.txt](evidence/finish-python-tests-2026-10-07.txt). The real app.js passed **28 normal**, **32 delayed** and **10 mocked live-receipt DOM assertions**, retained in [normal](evidence/finish-ui-contract-2026-10-07.txt), [delayed](evidence/finish-ui-delayed-2026-10-07.txt) and [receipt](evidence/finish-ui-live-receipts-2026-10-07.txt) logs. Compilation, JavaScript syntax and whitespace checks passed. These tests made no provider request and establish no live end-to-end repair or new rendered-browser check.

An initial invocation resolved `python3` to the system Python 3.9 and failed import; the README requires Python 3.11+. The subsequent Python 3.12 engine tests all passed, while the sandboxed network subset encountered its existing controlled-loopback bind restriction. The authorized full-suite execution above passed every case. These environment failures were not product failures or successful checks.

## October 7 complete-response transport fix

The public revision `8378fa9a6801b370780f1789f585741b2b90458a` could report a network failure after successfully receiving a complete short body. Python's HTTP response closes its detached socket when the declared Content-Length has been read; the old loop then tried to update that released socket's timeout. Real controlled-loopback regressions reproduced `OSError` errno 9 for HTTP/1.0 JSON, HTTP/1.1 JSON with `Connection: close`, and a body exactly at the byte cap. The fixed loop stops when the response is closed, preserving the complete body and original HTTP status.

Four new regression cases cover those responses, chunked connection closure, and exact/beyond-cap truncation. The full **80-test suite passed in 1.584 seconds**, including the existing absolute-deadline and detached-response cleanup tests. Python syntax and `git diff --check` passed. Pinned connections, hostname-verified TLS, public-address validation, redirect rules, byte limits and absolute deadlines retain their existing behavior. See the [receipt](evidence/transport-fix-receipt-2026-10-07.json), [pre-fix failures](evidence/transport-before-fix-2026-10-07.txt), [safe errno diagnostic](evidence/transport-error-category-2026-10-07.txt) and [full passing suite](evidence/transport-python-tests-2026-10-07.txt).

These checks use actual local sockets and controlled bodies; they make no external provider request and use no credential. Earlier failed live setup did not establish a successful authenticated account check, SerpApi search or completed repair. A subsequent successful run is recorded below.

## October 7 real SerpApi workflow

Source revision `df1750ae860fbd89043a054dcb8daf0dd4df9616` completed one actual live workflow. At 07:11:19 UTC the secure local launcher reported an active zero-price Free Plan with 239 of 250 monthly searches remaining. The dedicated process had a one-attempt search cap. The input explicitly declares its citation URL intentionally mistyped; no historical migration is claimed.

The application's HTTP check observed 404 for `https://docs.python.org/3/library/pathlib/index.html`. At 07:13:42 UTC the query `site:docs.python.org pathlib Object oriented filesystem paths` returned a real SerpApi HTTP 200 / Success response, search ID `6ac5f1252efef8e34fbc26b4`, five eligible results and `cache_hit: false`. The leading candidate was `https://docs.python.org/3/library/pathlib.html`. An OpenAI Codex agent opened the official documentation independently, reviewed the filesystem-class context, and approved the URL through the actual local UI under the user's explicit authorization. Personal participant semantic review is not claimed.

The retained [receipt](evidence/live-repair-receipt-2026-10-07.json), [analysis](live-output/analysis.json), [input](live-output/guide.md), [diff](live-output/sourcepatch.diff), [patched Markdown](live-output/guide.patched.md) and [provenance](live-output/provenance.json) document the run. The public provenance adds an operator annotation explaining the exported `approved_by_user: true` field; the original capture is preserved locally. Independent checks confirmed exactly one destination span changes, source/output hashes match, patch dry-run succeeds and application to a separate copy yields byte-identical exported Markdown. Prose and code remain unchanged.

This demonstrates one controlled authored-typo status/search/review/export path. It does not measure broad real-document accuracy or establish organizer eligibility. The application does not automatically verify candidate content or anchors; `live_verified` and `page_verified` remain false. No remaining-quota value after the search was measured, and no second search or automatic retry occurred. The [real recording](https://youtu.be/D5dKt3ehCIk) is published unlisted (109.916667 seconds, H.264, 1680×996). It was captured natively, cropped to browser content and trimmed; search results were not recreated. YouTube confirmed publication and anonymous oEmbed returned HTTP 200. The existing portal entry was updated with this video and verified after reload as SUBMITTED, retaining its original entry identity.

## Manual checklist

- [ ] Open the app at about 1440×1000 and 390×844; verify readable layout, fixture labeling and no page-level overflow
- [ ] Tab through controls and confirm focus visibility and control order
- [ ] Approve pathlib and verify both destinations change with one decision
- [ ] Inspect ambiguity, skip, undo and choose a candidate
- [ ] Preview and inspect all three downloads
- [ ] Edit source after approval; verify old decisions and exports clear
- [ ] Test empty, malformed, non-fixture and hostile-label inputs
- [ ] Check repeated clicks, delayed startup and browser console/network output
- [x] Verify one authored public citation workflow in live mode with an existing key; broader document validation remains outstanding
- [x] Capture the real workflow in an under-three-minute recording; publish the [1:50 demo](https://youtu.be/D5dKt3ehCIk)

## Reproduce

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q sourcepatch
node --check web/app.js
node scripts/check-ui.mjs
node scripts/check-ui.mjs --delayed-config
cd docs/demo-output
patch --dry-run guide.md sourcepatch.diff
```

## Independent recovery review

A separate fresh review found no blocker in the tested offline scope. It reran all 61 Python tests, both DOM modes and the original critical reproduction cases. Additional checks confirmed exact patch application for LF/CRLF/Unicode/lone-CR inputs, watchdog shutdown, response cleanup, forbidden redirects and DNS answers, credential redaction, and rejection of stale in-flight UI export responses. This does not establish byte-identical recovery, live integration or rendered browser correctness.

## October 7 rendered browser check

The updated app passed a focused real Chromium check at 1440px desktop and 390px mobile: approval and provenance download preserve the source, source edits clear stale decisions, fixture provenance has no live search receipt, mobile has no page overflow, and no page errors or external requests occurred. See [receipt](evidence/finish-browser-browser-receipt.json), [desktop](evidence/finish-browser-desktop.png) and [mobile](evidence/finish-browser-mobile.png). These are fixture checks; the later real SerpApi workflow above is separate evidence. The owned browser and server were preserved.

# Verification record

Reconstructed build: October 1, 2026. This document distinguishes executed checks from work still outstanding.

## Executed checks

- 61 reconstructed Python unittest cases pass, including controlled-loopback transport tests
- 28 normal and 32 delayed-configuration DOM-contract assertions pass against the actual app.js
- Python compilation and JavaScript syntax checks pass
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

## Not verified

- No real SerpApi key or successful live end-to-end request
- No complete keyboard, screen-reader or measured contrast verification
- No formal security certification
- No final hackathon submission; an authenticated draft was saved October 4, 2026

The earlier build environment rejected local browser access. Subsequent rendered fixture-browser QA on October 4 is recorded below; it does not establish live integration or a complete accessibility audit.

## October 4 fixture-browser evidence

The workspace receipt `sourcepatch-demo/browser-receipt.json` records seven checks against the public main snapshot at `http://127.0.0.1:8766`: visible synthetic-fixture disclosure and five destinations; explicit approval and URL-only preview with source unchanged; three completed downloads with fixture provenance; skip and undo; source-edit invalidation; no horizontal overflow at 390×844; and no page errors or external requests. A focused anchor had a solid outline; complete keyboard order was not audited.

Screenshots and a labeled fixture recording exist in the workspace. The recording metadata reports H.264, 1440×1000, 25 fps and 44.28 seconds. The video demonstrates authored fixtures and is not proof of a live SerpApi request. These workspace artifacts are not included in this source snapshot.

October 4 regression-suite execution was initially rejected by automatic approval review under the original read-only scope. The user later explicitly approved the offline command. The October 1 checked-in test logs remain historical evidence.

## October 4 local search-budget change

The local branch adds `--max-searches` (integer 1–8, default 8), counts attempted provider calls before fetching, retains cache hits after exhaustion, and discloses the configured process allowance in the CLI, browser configuration and exhaustion notice. The separate eight-query analysis cap and `live_verified: false` remain unchanged.

After explicit execution approval, the final edited suite passed **68 Python tests** in 23.601 seconds with mocked search responses, fake keys and controlled loopback transports. The complete output is retained in [search-budget-python-tests.txt](evidence/search-budget-python-tests.txt). These tests establish offline behavior only; no real SerpApi key, provider request or live citation repair was verified.

The real `web/app.js` also passed **28 normal**, **32 delayed-configuration**, and **4 mocked live-configuration DOM-contract assertions**. Outputs are retained in [normal](evidence/search-budget-ui-contract.txt), [delayed](evidence/search-budget-ui-delayed.txt), and [configured-budget](evidence/search-budget-ui-budget.txt) evidence logs. The last mode checks the one-call disclosure and confirms live mode waits for explicit inspection; it makes no provider request. Python compilation, JavaScript syntax and `git diff --check` passed. These harness checks do not establish browser layout, accessibility or live integration.

The first sandbox baseline run executed 54 tests with four errors: two existing five-second CLI subprocess startup timeouts and two denied loopback binds. The first edited run had the same environment restrictions and two additional invalid-argument subcase startup timeouts. With controlled-loopback permission, the unchanged baseline ran all 61 cases: 59 passed and two existing CLI subprocess starts exceeded five seconds. A serial CLI-only baseline retry repeated those two timeouts. The edited branch increases only the CLI test supervisor allowance from five to 30 seconds; it makes no product or network deadline change. Invalid-budget tests exercise the actual CLI parser in-process and assert that terminal, key-input and server work are never reached. Original and retry logs are preserved separately in the workspace.

## Manual checklist

- [ ] Open the app at about 1440×1000 and 390×844; verify readable layout, fixture labeling and no page-level overflow
- [ ] Tab through controls and confirm focus visibility and control order
- [ ] Approve pathlib and verify both destinations change with one decision
- [ ] Inspect ambiguity, skip, undo and choose a candidate
- [ ] Preview and inspect all three downloads
- [ ] Edit source after approval; verify old decisions and exports clear
- [ ] Test empty, malformed, non-fixture and hostile-label inputs
- [ ] Check repeated clicks, delayed startup and browser console/network output
- [ ] Verify one real public citation in live mode with an existing key
- [ ] Capture honest screenshots and an under-three-minute screen recording

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

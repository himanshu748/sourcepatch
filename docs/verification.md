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
- No rendered browser, mobile, keyboard, screen-reader or measured contrast verification
- No screenshots or screen recording; none are fabricated
- No formal security certification
- No hackathon registration or submission

The earlier build environment rejected local browser access and could not launch its browser runner. DOM simulation is not evidence of actual rendering or layout. These checks remain required.

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

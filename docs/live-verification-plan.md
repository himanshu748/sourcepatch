# Pending live verification

Status: procedure only. No real credential was read and no API call was made during this review.

## Preconditions

- Offline regression execution was explicitly approved on October 4 after a rejection under the original read-only scope. This does not authorize a live provider request; obtain separate live permission before following this procedure. This document is not authorization.
- The participant must confirm that an existing SerpApi account has at least one unused free search and that using it is permitted. A credit-consuming request cannot be represented as guaranteed free without that confirmation. No account creation, upgrade, purchase or persistent credential is needed.
- Use one public, non-confidential citation and confirm its URL currently returns HTTP 404 or 410 before the SerpApi run. Choose a meaningful moved/deleted documentation link with a descriptive label; a manufactured random nonexistent URL would demonstrate transport but provide weak citation-repair evidence.

## One-call procedure, after authorization

1. Run the offline regressions first and inspect failures before starting live mode.
2. Start a dedicated live process with `python3 -m sourcepatch --mode live --max-searches 1` in an interactive terminal, on an unused loopback port. Enter the existing key only at the hidden prompt; do not put it in shell arguments, environment files, screenshots or logs.
3. Replace the default sample with a Markdown document containing exactly the single prechecked broken citation. Do not inspect the default sample: it may trigger several searches.
4. Inspect once. Capture the mode, observed 404/410, generated public query, and returned candidate titles/URLs. A search failure or empty results is evidence of an attempt, not successful citation repair. Do not retry or restart to spend more allowance.
5. If a suitable candidate exists, review the destination independently, approve explicitly, preview and download the URL-only diff and provenance. Candidate meaning and anchors are not verified by the application.
6. Keep a sanitized receipt with timestamp, source revision/snapshot, citation, observed status, query, candidate evidence, approval and export hashes, and account allowance before/after. Do not store raw SerpApi request URLs: their query strings contain the key. Do not collect unrestricted browser or terminal traces during key entry.
7. Leave the dedicated process running and report its port and session identifier so the user can manage it, honoring this session's instruction not to stop processes. Keep the fixture recording labeled; add separate live evidence instead of implying it already demonstrates live integration.

## Source boundaries and improvement plan

`sourcepatch/network.py` confines the key to the provider instance and constructs a Google Search request to SerpApi over HTTPS. It disables redirects, caps response size, filters candidate URLs, caches successful query responses, and counts attempts before fetching. A lock serializes searches. There are no automatic retries. The default process allowance is eight attempted calls; `--max-searches 1` lowers it to one attempted call for the dedicated verification process.

`sourcepatch/engine.py` searches only citations marked broken after a status check; the built-in checker marks only HTTP 404/410 broken. The analysis budget is eight queries, separate from the configurable provider process allowance. `live_verified` remains false in all modes; external evidence should establish verification rather than changing this flag merely because mode is live.

Local implementation now exposes a validated `--max-searches` process limit (default eight, range one through eight), passes it to `SerpApiSearch`, and derives the exhaustion message and browser disclosure from the configured allowance. Dedicated offline tests cover argument validation and propagation, exhaustion, failed-call accounting, cache request counts and returned-cache isolation. This local change does not establish a real SerpApi request or live citation repair.

Failed queries currently consume allowance but are not cached. A later manual rescan can repeat the failed query; the operator should not rescan during the one-call procedure. Consider a separate explicit retry policy only after assessing its user-facing semantics.

## Static test review

Existing `tests/test_network.py` covers request parameters, successful response parsing, malformed and service-error responses, key validation, invalid result filtering, exception sanitization and truncated bodies. `tests/test_engine.py` covers the eight-query analysis cap and unsafe-target short-circuiting. Added regressions cover the lower process cap and its citation notice, repeated-query fetch count, cached-result mutation isolation, and CLI/config propagation. See `verification.md` for actual execution results and limits; authoring these tests alone is not execution evidence.

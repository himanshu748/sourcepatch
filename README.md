# SourcePatch V2

**Keep the knowledge. Recover the evidence.**

A local workbench for recovering broken Markdown citations. Discover candidates with SerpApi, inspect bounded page evidence, review uncertainty, and explicitly approve a URL-only patch with provenance. Your source file is never overwritten.

V2 extends the existing submitted project; it is not a new repository or duplicate submission. The submitted V1 revision is `34ab8ee190d3e5d537b5ce195e8d07b6f8749333`. The existing [1:50 real SerpApi demo](https://youtu.be/D5dKt3ehCIk) demonstrates V1; it does not demonstrate V2 page inspection.

## Run locally

Python **3.11+**, no application dependencies or build step:

```sh
python3 --version
python3 -m sourcepatch --port 8772
```

Open **http://127.0.0.1:8772**. macOS `/usr/bin/python3` may be 3.9; use an installed supported Python. In this verification environment:

```sh
export PATH="/opt/homebrew/opt/python@3.13/libexec/bin:$PATH"
```

1. Choose the **Python pathlib** candidate.
2. Click **Inspect authored page fixture**. Read original context, page title/headings, bounded excerpts, content hash, anchor observation and heuristic reasons.
3. Approve explicitly and preview the patch. Both duplicate destinations change while surrounding Markdown remains intact.
4. Inspect the MDN alternatives, compare ambiguity, or skip. Inspect the third-party pathlib candidate to see an unavailable fixture and **INSUFFICIENT EVIDENCE. LEAVE CITATION UNCHANGED.**
5. Export Markdown, unified diff and provenance JSON. Skips can also be exported as an empty patch with evidence.

**Fixture mode is entirely authored and offline.** HTTP statuses, search rows and page HTML in that mode are not real observations. Arbitrary pasted documents receive no invented fixture results.

## What V2 adds

- **Candidate content inspection:** safe public URL retrieval through the existing pinned transport; HTML title/headings, bounded body excerpts, fragment observation and SHA256. No JavaScript execution or stored full pages.
- **Explicit search strategies:** publisher-scoped Google, cross-domain Google, identifier-focused Google and optional Google Scholar. Additional strategies require a button click; no automatic credit-consuming retry.
- **Evidence-aware ranking:** deterministic publisher/topic/context/title/heading/content/identifier/anchor signals, structured reason codes and ambiguity warnings. Scores are heuristics, not probabilities.
- **Safe abstention:** empty, irrelevant, missing-anchor, blocked, truncated and unsupported responses remain insufficient/inconclusive. HTTP 200 alone is not relevant evidence. Once inspected, an insufficient candidate cannot be exported as a repair.
- **Review workbench:** document editor, citation queue, strategy history, source metadata, original context, page evidence, warnings, approval, preview and downloads in the existing dependency-free UI.
- **Extended provenance:** candidate-specific search receipts, strategy history, page observations, hashes, excerpts, anchors, heuristic version, explicit decisions and limitations, including skipped-candidate evidence.

For API compatibility, an explicit legacy approval without page inspection remains possible and is labeled unverified. No score or content verdict automatically approves a replacement. A related verdict means observed lexical overlap; it does **not** prove factual support, publisher identity or semantic equivalence.

## Live mode and credit safety

For a one-search verification session with an account-allowance preflight:

```sh
python3 scripts/live-proof.py
```

Enter an existing key at the hidden terminal prompt. The script checks active allowance before starting the live workbench on **127.0.0.1:8773**, capped at **one attempted provider search**. It does not create accounts, buy credits or upgrade plans. Use public, non-confidential Markdown. Download the actual provenance after review; never relabel fixture output as live.

The existing CLI remains available:

```sh
python3 -m sourcepatch --mode live --max-searches 1
```

This legacy CLI asks for a key but expects you to check allowance yourself; prefer the preflight launcher for proof runs. Keys remain in process memory, are sent only to SerpApi over HTTPS, and are excluded from browser data, receipts and errors. No browser key field or credential file is introduced.

Limits: 1–8 attempted SerpApi calls per process; failed calls count, successful cache hits do not. Eight discovery requests per analysis; sixty distinct citations; 200,000 source characters. Page inspection: twenty candidates per analysis, sixty-four per process, eight seconds and 524,288 bytes per fetch. Results are cached within the analysis, including failed observations, with no implicit retry.

## Executed evidence and limits

- **V1 live search proof, October 7:** real HTTP 404 → SerpApi Success → agent-operated explicit review → URL-only export for an authored Python URL typo. [Original receipt](docs/evidence/live-repair-receipt-2026-10-07.json). Two real NPTEL searches missed the canonical course and were skipped; [failure receipt](docs/evidence/nptel-failure-receipt-2026-10-07.json).
- **V2 direct-page proof, October 8:** a fresh bounded fetch of the candidate from the historical Python search produced title, headings, excerpts and a response hash. [Evidence](docs/evidence/v2/historical-search-fresh-page.json). This reuses historical discovery; it is **not a new SerpApi search or new full live workflow**.
- **V2 offline checks:** original tests retained, new extraction/provider/API/abstention tests, original DOM modes plus V2 DOM assertions, and focused rendered desktop/390px checks. See the [current verification report](docs/v2-verification.md).
- **Benchmark:** 12 authored cases plus one historical public retrieval miss, with per-case results and explicit denominators. [Methodology](docs/benchmark.md), [results](docs/evidence/v2/benchmark.json). No representative production accuracy claim.

A new V2 end-to-end provider proof is pending: no key was present in the checked environment and the inspected SerpApi browser session was signed out. No new provider request, account purchase or quota use is claimed. PDFs, JavaScript-rendered text, OCR, full CommonMark, semantic entailment and broad accessibility certification are outside scope.

## Checks

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q sourcepatch
node --check web/app.js
node scripts/check-ui.mjs
node scripts/check-ui.mjs --delayed-config
node scripts/check-ui.mjs --live-config
node scripts/check-ui.mjs --v2
python3 scripts/benchmark.py
```

The DOM harness needs `python` as well as `python3` on PATH. It uses a small DOM model and does not itself verify rendered layout. Python tests use controlled responses/loopback peers and no public provider calls.

## Architecture and security

Markdown spans → bounded HTTP check → SerpApi discovery → explicit candidate inspection → bounded lexical evidence → human decision → URL-only patch/provenance.

Read [architecture/API/scoring](docs/architecture.md) and [security boundaries](SECURITY.md). Existing `GET /api/config`, `POST /api/analyze` and `POST /api/export` remain. New `/api/discover` and `/api/candidates/verify` accept server-owned IDs only, never a browser-submitted target URL. The local server binds to loopback with strict Host/Origin checks, CSP, no CORS and serialized operations.

Markdown support is conservative: inline, reference and autolinks; duplicate grouping; titles and surrounding formatting preserved; code/images/raw HTML excluded. Unsupported or overlapping syntax stays untouched. Always inspect the diff.

## Hackathon materials

Official deadline: **October 10, 2026, 11:59 PM IST**. Recommended V2 track: **Knowledge & Public Interest**, verified against the [official site](https://serpapi.github.io/serpapi-india-hackathon-2026/). Historical submitted track: Open Innovation. The portal was not modified during V2 development.

[Proposed entry update](docs/entry-draft.md) · [Under-three-minute storyboard](docs/demo-script.md) · [AI disclosure](AI_ASSISTANCE.md) · [baseline/plan](docs/v2-plan.md) · [historical verification](docs/verification.md) · [MIT license](LICENSE)

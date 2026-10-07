# SourcePatch

**Keep the knowledge. Repair the references.**

A local-first workbench for finding likely new homes for broken Markdown citations. Inspect the evidence, approve a replacement yourself, and export a URL-only patch with a provenance report. Your source file is never changed by the application.

> **Prototype status:** one real SerpApi workflow was verified October 7, 2026: an authored typo returned HTTP 404, actual Google Search results identified the canonical Python documentation page, and an explicit UI approval produced a URL-only patch and provenance. The default offline workflow and earlier 44.28-second recording use labeled synthetic fixtures. The existing submitted portal entry was updated October 7 with the [real SerpApi demo](https://youtu.be/D5dKt3ehCIk) (1 minute 50 seconds). Organizer eligibility has not been established.
>
> **Recovery note:** this snapshot was reconstructed on October 1, 2026 after loss of the original build filesystem. It was revalidated; byte-identical recovery of the earlier archive is not claimed. See [RECOVERY.md](RECOVERY.md).

## Run in 30 seconds

Python **3.11 or newer**. No packages, account, API key, cloud hosting or payment are needed for the fixture demo.

```sh
python3 -m sourcepatch
```

Open **http://127.0.0.1:8765**. If the port is busy, use `python3 -m sourcepatch --port 8766`.

1. Inspect the **Python pathlib** citation. Its authored fixture status is 404
2. Select `pathlib.html`, then choose **Approve replacement**
3. Inspect **Abort a fetch request**. Its close matches are marked ambiguous; decide based on meaning or skip
4. Choose **Preview patch** and download the unified diff, patched Markdown or provenance JSON
5. Edit the source. Old decisions are cleared; a new inspection is required

The sample has five distinct citation destinations and six references. Three are marked broken in the fixture, one reachable and one unsafe local address blocked before any request. **These statuses and search results are authored examples, not saved live responses.** Other pasted URLs receive “No fixture,” never invented evidence.

## Why this exists

A dead URL does not tell you which replacement preserves the author's intent. SourcePatch combines discovery with careful review:

- **SerpApi discovery:** live mode uses Google Search to find candidate pages for HTTP 404/410 citations
- **Visible evidence:** exact hostname, title overlap, context overlap and close-score ambiguity are shown as heuristics
- **Small changes:** exact Markdown destination spans are replaced; surrounding source formatting stays intact
- **Explicit decisions:** no candidate is automatically approved, regardless of score
- **A paper trail:** status observation, query, candidate evidence, uncertainty, approvals and content hashes accompany the patch

Descriptive citation labels guide search. For generic labels such as “here” and bare URL citations, the last two meaningful URL path segments supply the topic instead; URL query strings and fragments are excluded. Discovery scopes search to the original hostname with a leading `www.` removed, allowing results from successor subdomains. Other subdomains stay scoped exactly; this version can miss moves outside that scope. A broader search scope does not establish publisher identity, and different-host results retain their warning.

A matching hostname is not proof of publisher identity. Search results do not establish equivalent meaning. Candidate pages and anchors are not fetched or verified by this prototype.

## Live mode with an existing key

```sh
python3 -m sourcepatch --mode live
# For a dedicated verification process limited to one attempted provider call:
python3 -m sourcepatch --mode live --max-searches 1
```

Use an interactive terminal and enter your existing SerpApi key at the no-echo prompt. There is no browser key field, key argument, saved configuration or credential-generation step. The app refuses echoed-input fallback.

Live mode sends citation URLs to their public hosts and generated label/hostname queries to [SerpApi Google Search](https://serpapi.com/search-api). **Use public, non-confidential documents.** The key is sent only to SerpApi over HTTPS and retained only in process memory; it is not logged, reported or sent to the browser.

- At most **8 attempted SerpApi calls per process** by default; `--max-searches` accepts integers **1 through 8**. Successful cache hits use no allowance, while failed calls consume allowance. There are no automatic retries. The browser displays the configured process cap; the analysis query cap below remains separate.
- At most **8 broken-citation queries per analysis**, **60 distinct citations** and **200,000 source characters**
- Only HTTP 404/410 trigger search; timeouts, 403s and server errors remain uncertain
- No account creation, credit purchase, plan upgrade or subscription action
- Requests can consume your existing credits; check your allowance before use

**One real live workflow was verified on October 7.** The secure local account preflight reported an active zero-price Free Plan with 239 of 250 monthly searches remaining before the run. A dedicated one-search process observed HTTP 404 for an intentionally mistyped `pathlib` URL, received a successful uncached SerpApi response with five candidates, and exported the canonical documentation replacement after explicit approval. [Live receipt](docs/evidence/live-repair-receipt-2026-10-07.json), [input](docs/live-output/guide.md), [diff](docs/live-output/sourcepatch.diff), [patched Markdown](docs/live-output/guide.patched.md) and [provenance](docs/live-output/provenance.json) retain the evidence and hashes.

This controlled authored-typo run establishes the actual status/search/review/export path. Broader real-document performance has not been measured. An OpenAI Codex agent opened the official documentation and approved through the UI under the participant's authorization; personal participant semantic review is not claimed. Candidate meaning and anchors remain outside automatic verification, and the application's `live_verified`/`page_verified` fields remain false. The earlier complete-response transport failure is fixed and covered by real loopback regressions. Offline tests still use fake credentials and controlled responses.

The live adapter attaches a sanitized response receipt to its results: local retrieval time, response hash, accepted-result count, cache use, and an optional provider search ID. Open **Inspect search query & evidence source** to review it, including when no candidate is returned. Approved changes carry the receipt into provenance JSON. A cache hit keeps the original retrieval time and makes no new provider request. Receipts establish what was returned; they do not verify candidate meaning, and mocked receipts in tests are not live-use proof.

## Markdown support

Supported conservatively: inline links (including nested space-indented list items), optional quoted titles, angle destinations, balanced URL parentheses, full/collapsed/shortcut references, HTTP(S) autolinks and duplicate grouping. List indentation is measured relative to the enclosing item's content; actual indented code and nested fenced code remain excluded. Mixed tab/list containers and complex block syntax are not fully supported. First reference definition wins. Existing anchors are retained when a candidate has none, with a warning.

Code, images, raw HTML, relative/mail links and local anchors are excluded. Definitions shared with an image are protected even if text uses them too. Unused definitions, malformed constructs and escaped destinations remain untouched. This is **not a full CommonMark parser**; complex unsupported constructs can be skipped. Review every diff before applying it. The original file is never overwritten.

## Safety boundaries

See [SECURITY.md](SECURITY.md): loopback binding, strict Host/Origin policy, CSP, no CORS, default HTTP(S) ports only, no URL credentials, public-only DNS/IP validation, pinned connections with hostname-verified TLS, redirect/byte/time limits and explicit source-hash checked exports. No runtime LLM, telemetry, cookies or persistent document storage.

This is a single-user local prototype, not an internet-facing service or a certified security proxy.

## Tests

The current offline suite has **86 Python tests**, including nested lists/code exclusions, bounded discovery scope, complete HTTP/1.0 and HTTP/1.1 responses, chunked bodies and byte-limit handling. The UI harness has 28 normal, 32 delayed-startup and 10 mocked live-receipt assertions. See [citation regression evidence](docs/evidence/public-citations-receipt-2026-10-07.json) and [transport regression evidence](docs/evidence/transport-fix-receipt-2026-10-07.json); these checks make no provider request.

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q sourcepatch
node --check web/app.js
node scripts/check-ui.mjs
node scripts/check-ui.mjs --delayed-config
node scripts/check-ui.mjs --live-config
```

The Python suite uses no external network; one regression uses a controlled loopback server. The optional Node harness executes real app.js with a small DOM model. **It does not verify browser rendering, CSS, layout or real keyboard behavior.** Python must also be available as `python` for the Node harness.

See [verification](docs/verification.md) for current evidence and outstanding checks.

## Reproducible fixture artifacts

```sh
python3 -m sourcepatch --demo-export /tmp/sourcepatch-demo
```

The directory must not exist. Outputs include the original sample, a patched copy, a diff and synthetic provenance. The approval is explicitly **hypothetical**, not an actual person's decision. Checked-in [diff](docs/demo-output/sourcepatch.diff) and [report](docs/demo-output/provenance.json) demonstrate the format.

## Architecture

Markdown spans → bounded status check → SerpApi discovery for 404/410 → deterministic ranking → human approval → URL-only diff and provenance.

- `markdown.py`: conservative source spans and replacement
- `network.py`: URL/DNS/redirect policy, bounded transport and SerpApi adapter
- `engine.py`: analysis, ranking, decisions and exports
- `server.py`: loopback HTTP API and memory-only sessions
- `web/`: dependency-free review interface

## Hackathon entry

Prepared as a new prototype for the [SerpApi India Hackathon 2026](https://serpapi.github.io/serpapi-india-hackathon-2026/index.html), track **Open Innovation**. See the [entry notes](docs/entry-draft.md), [demo script](docs/demo-script.md) and [AI disclosure](AI_ASSISTANCE.md). The portal displayed **SUBMITTED** on October 7, 2026. The existing entry now links to the [real SerpApi demo](https://youtu.be/D5dKt3ehCIk) (1:50), showing the actual provider response and approved URL-only export. Its SUBMITTED status and new demo URL were verified after reloading the portal. Organizer eligibility remains unconfirmed.

[Contributing](CONTRIBUTING.md) · [MIT license](LICENSE)

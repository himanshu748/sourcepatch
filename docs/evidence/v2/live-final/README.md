# Real V2 review and export — October 8, 2026

The browser recording executes the local V2 application in live mode. The input deliberately contains a mistyped URL; no organic historical migration is claimed. All HTTP status observations, SerpApi results and candidate content in this directory are actual network observations.

- `01-analyze.json`: public original returned HTTP 404; publisher-scoped Google request succeeded. Its results included other domains; the query is an intention, not a publisher guarantee.
- `02-discover.json`: explicitly requested broad Google query `Python pathlib`, successful provider receipt. No fixture fallback or hand-inserted candidate.
- `03-verify.json`: ETH Zürich teaching page fetched directly, HTTP 200, 44,583 bytes, not truncated. SHA256 `164d4a30263303ddcc030639b5b51ed774d6c54d111dff53d1cdbb1e1027f116`. Lexical state related, score 54/100; not a probability.
- `04-export.json`: actual browser approval and strict-evidence export. Two URL destinations changed and the rest of the document remained byte-for-byte identical. Source and output hashes, timestamps and search IDs are in provenance.

The operator independently read the ETH D-PHYS page and reviewed its explanation of filesystem paths, Path objects and methods against the sample's introductory purpose. The selected page is an alternative educational source, not the original Python reference manual. Approval was operated by Codex, not authenticated participant review. The legacy `approved_by_user` field records the explicit client action; `identity_authenticated` is false.

## Attempts and budgets

Earlier runs are retained in `../live-complete` (first publisher transport failure, successful broad discovery and successful ETH fetch) and `../live-recording` (successful searches, failed candidate fetch, no approval). The initial one-search abstention remains in `../live`. None was rewritten as a success.

The completion work was capped at eight total attempted searches across process restarts: caps 8 → 6 → 4, subtracting two used attempts each time. Six attempts were actually made; no purchases, upgrades or new credentials. A zero-price active Free Plan allowance was checked before each attempted search. The final process had four-attempt cap and made two. SerpApi may serve cached results: fresh HTTP request time does not prove freshly crawled Google data. Failed key handoff/account preflight sessions made no searches.

A transient page-fetch failure exposed the need for explicit retries. The final product allows two retries only when no HTTP response was observed, preserves prior evidence, and maintains twenty per-analysis/sixty-four per-process page budgets. The final recorded page fetch succeeded on its first attempt; retry recovery is verified with controlled tests, not misrepresented as occurring in this recording.

## Reproduction

Run `python3 -m sourcepatch --mode live --max-searches 4` with an existing key after checking allowance. Inspect the live sample, explicitly request Cross-domain search, and inspect a relevant returned candidate. Review the actual result; do not assume the same result will recur. Approve only if it fits your intended citation. The downloadable source includes the offline fixtures for deterministic regression checks.

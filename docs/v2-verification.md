# V2 verification — October 8, 2026

The submitted V1 revision `34ab8ee190d3e5d537b5ce195e8d07b6f8749333` is preserved as `preserve/submitted-2026-10-08`. V2 extends the existing repository on `sourcepatch-v2`. The original 88 Python tests remain; all tests run without public provider calls.

## Current checks

- Python 3.13.15: full suite 114 tests passed in 4.516 seconds ([log](evidence/v2/completion-python.txt)). Compilation and JavaScript syntax passed.
- DOM harness: original 28 assertions, delayed configuration 32, mocked live configuration 10, V2 19 additional. These exercise actual app.js against a minimal DOM; they are not browser layout tests.
- The real native browser completed live source inspection, publisher/broad discovery, candidate content inspection, explicit approval and strict export. The exported Markdown was independently equal to replacing only the two original destination strings. No prose changed.
- Earlier fixture browser checks at 1440×1000 and 390×844 remain in `evidence/v2/browser-receipt.json`. The current landing was rendered at 390×844 with scroll width exactly 390; filtering matched one Python record and the empty state worked. Screenshot: `evidence/v2/completion-mobile.png`. Viewport override was reset.
- The static validator checks local assets/anchors, fixture equality, exact live dataset/export equality, safe rendering and a core gzip payload under 20KB.
- GitHub Actions configuration runs Python 3.11 and 3.13 suites plus compile, JS, UI and static checks. Hosted status must be read from the actual run; configuration alone is not a passing CI claim.

## Actual live proof

See [complete live run](evidence/v2/live-final/README.md). Real 404 → two successful SerpApi HTTP requests → actual ETH page HTTP 200, 44,583 bytes, no truncation → explicit agent-operated approval → exact two-destination patch. The search results and page content were not authored. The input typo was deliberately authored, and the replacement is an alternative educational source, not the canonical Python manual or proof of recovering an organic migration.

The first attempted publisher search failed (`live-complete`), a subsequent page fetch failed (`live-recording`), and an earlier oversized candidate caused safe abstention (`live`). All are retained. Six completion-search attempts were used within an eight-attempt cap spanning restarts; allowance and zero-price Free Plan were checked before each attempt. No purchases or new credentials. Scholar remains controlled-test coverage, not fresh live proof.

The transport failure prompted explicit retries: only no-response failures, maximum three candidate attempts, twenty per analysis and sixty-four per process. No automatic retry. Tests verify retained failure history for approved and skipped candidates, successful recovery, retry cap, API validation and observed-response rejection. The final filmed fetch succeeded first try; the retry fix is not falsely credited for that success.

## Review boundaries

The V2 UI blocks approval before page inspection and requests strict evidence validation at export. Legacy API callers can still explicitly approve uninspected candidates for compatibility; those remain labelled unverified. Related lexical content does not prove semantic equivalence or factual support. The approval marker is a client action, not authenticated human identity.

HTML only, bounded extraction, no runtime LLM, no JavaScript rendering, PDFs or OCR, conservative Markdown subset. Network pinning, private-address rejection, redirect/body/time budgets and source ownership remain enforced. No formal security or accessibility certification is claimed. The authored/recorded 13-case benchmark is a small regression set, not production accuracy.

## Publication

Public landing: https://sourcepatch.pages.dev/ . The refreshed site leads with recorded live evidence and the 100-second live recording; offline fixtures are separate. The local API and credential are not exposed. See release/deployment receipts for exact hosted hashes and playback verification.

The existing hackathon portal entry and V1 video are unchanged. The updated description and video link are prepared in `entry-draft.md`. Official deadline checked October 8: October 10, 2026, 23:59 IST. No duplicate submission.

# V2 screen-recording storyboard — 2 minutes 40 seconds

The original shooting plan below was superseded by the completed 95-second [V2 fixture screen recording](https://sourcepatch.pages.dev/#demo). Its actual transcript is in landing/docs/demo-script.md. The historical submitted [V1 recording](https://youtu.be/D5dKt3ehCIk) remains unchanged.

| Time | Show | Explain |
|---|---|---|
| 0:00–0:15 | Local workbench, visible mode banner and public Markdown | Recover citation evidence; no silent edits. If offline, say authored fixture immediately. |
| 0:15–0:35 | Inspect the document; original context and HTTP observation | A broken destination is an observation, not a license to change the claim. |
| 0:35–0:55 | Candidate list and expanded strategy history/receipt | SerpApi discovers candidates; engine, query, completion, timestamp and hash identify the response. |
| 0:55–1:30 | Select one candidate and click Inspect candidate page | A separate bounded public-page fetch yields title/headings/excerpts/hash and anchor state. Distinguish this from the search snippet. |
| 1:30–1:50 | Relevance reasons and warnings | Lexical overlap is a clue, not semantic equivalence. Human review remains necessary. |
| 1:50–2:10 | Insufficient or ambiguous example, explicitly skipped | Leave the citation unchanged when evidence is weak. Label any switch to fixtures prominently. |
| 2:10–2:30 | Explicit approval, URL-only patch and duplicate spans | Only selected destinations change; source prose/code remains untouched. |
| 2:30–2:40 | Download provenance JSON | Reviewable search/page evidence, source/output hashes and explicit decisions. |

## Reproduce the offline vertical slice

Run `python3 -m sourcepatch --port 8772`. Select the first pathlib candidate → Inspect authored page fixture → review evidence → Approve replacement → Preview patch → download all three artifacts. Select the third-party candidate and inspect to demonstrate inconclusive missing-fixture evidence and disabled approval. Original source remains intact.

## Reproduce a new live proof

Run `python3 scripts/live-proof.py` in an interactive terminal. Enter an existing authorized key at the hidden prompt; an account-allowance check runs before the one-attempt server starts. Never record this key step. Open port 8773 and replace the sample with:

```md
This demonstration intentionally uses a mistyped URL; it is not a historical migration.
Use [pathlib Object oriented filesystem paths](https://docs.python.org/3/library/pathlib/index.html) to work with filesystem classes.
```

Inspect once. If the HTTP observation is not 404/410, or the real provider does not return a useful candidate, show that outcome and stop; never insert an authored result. If a candidate is discovered, inspect its page, review the original context, publisher, excerpts and warnings, then explicitly approve or skip. Download provenance, Markdown and diff. Record actual UI activity and distinguish agent-operated review from personal participant review.

The strict one-search session does not demonstrate multiple live strategies. Use a clearly labeled offline segment for strategy controls, or separately budget/authorize any future multi-search session after another allowance check. No automatic retries or plan changes.

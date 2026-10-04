# SourcePatch fixture walkthrough

The landing page includes an existing 44.28-second screen recording of the local fixture workflow, created October 4, 2026. Its persistent label says: “FIXTURE DEMO | Authored examples | Live SerpApi verification is pending.” The recording has no audio. It is not evidence of a live SerpApi request.

## What the fixture workflow demonstrates

1. Inspect the five citation destinations. Their statuses and search results are authored synthetic examples.
2. Review Python pathlib. Compare the original URL with the candidate destination, its matching hostname and title evidence. Scores are heuristics; meaning still requires human review.
3. Explicitly approve the pathlib candidate in the local workbench. One decision covers its two Markdown references.
4. Preview the URL-only diff, then export a diff, patched Markdown and provenance report. The original source remains unchanged.
5. Inspect the two equally ranked fetch-cancellation candidates. The workbench exposes the ambiguity; the reviewer can skip and undo a decision.
6. Edit the source after a review. The workbench invalidates old decisions and requires another inspection.

The page’s read-only explorer also shows a reachable fixture and a private address blocked before any network request. It cannot approve replacements; run the local application for that workflow.

## Evidence boundaries

- The video demonstrates deterministic fixtures, not saved live HTTP or search responses.
- Candidate pages and fragment anchors are not fetched or verified.
- The downloadable sample patch has a hypothetical authored approval, not an actual person’s decision.
- No public deployment, publicly hosted video URL, or final hackathon submission is claimed by this local landing deliverable.
- Live proof still requires an existing securely entered key, confirmed free allowance, a meaningful end-to-end result and a publicly accessible live demonstration.

This walkthrough adapts the original repository’s `docs/demo-script.md` shooting plan to the existing recording and its recorded browser receipt. The original document is unchanged.

# Reproducible V2 benchmark

Run `python3 scripts/benchmark.py`. The corpus and gold labels are in `benchmarks/cases.json`; output includes the corpus SHA256 and per-case outcomes. No dependencies or internet are required. The checked result is `docs/evidence/v2/benchmark.json`.

Twelve cases are authored tests, covering ordinary failures, documentation moves, domain migrations, academic identifiers, ambiguity, missing anchors, HTTP-200 irrelevant pages, no candidates, duplicates, unsafe URLs, unavailable content and identifier mismatch. URLs pointing at real publishers in authored cases do **not** make their HTML or status real observations.

The thirteenth case replays the actual October 7 NPTEL discovery miss from the retained provider analysis. Its gold destination was established in the original evidence record. Its candidate HTML is unavailable; that absence is intentionally inconclusive. This is a historical replay, not a fresh provider search.

## Metrics

- Candidate Recall@5: cases with a known gold destination whose gold appears among the first five, divided by all cases with a gold destination (6). It measures this supplied corpus only, not production SerpApi recall.
- Ranking quality: mean reciprocal rank of the gold destination, before/after content inspection, with absent gold scored zero; same six-case denominator.
- Abstention correctness: no related candidate or unresolved ambiguity compared with the explicitly authored expected-abstain label, across all thirteen cases. This benchmark policy does not automatically decide in the application.
- Patch correctness: a **simulated reviewer** selects a supplied eligible gold URL or explicitly skips. Exact output bytes must equal only the approved destination replacement; all other source bytes are unchanged. No human evaluation is claimed.
- Search efficiency: controlled discovery callback counts and actual provider-call count, reported separately. This runner makes zero provider calls.
- Evidence availability: candidates with relevant readable excerpts / total candidates. This is not a measure of full-page availability or truth.

The initial measured result is 5/6 Recall@5, 0.8333 MRR before and after, 13/13 abstention outcomes, 13/13 patch outputs, 12 controlled searches and 9/17 candidates with readable relevant excerpts. These are small regression-corpus results, not a representative real-document accuracy estimate. They show no measured ranking improvement on this corpus. Inspect the per-case JSON rather than treating the aggregate as a product guarantee.

Missing evaluation: a larger independently labeled corpus, blind human review, current cross-domain provider retrieval and Scholar end-to-end proof. Lexical relevance can miss paraphrases and can be fooled by misleading text containing topic words.

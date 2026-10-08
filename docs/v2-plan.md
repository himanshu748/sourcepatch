# V2 baseline and implementation plan — October 8, 2026

Submitted baseline: `34ab8ee190d3e5d537b5ce195e8d07b6f8749333`, preserved locally as `preserve/submitted-2026-10-08`. Work proceeds on `sourcepatch-v2` in a clone of the existing repository; no new hosted repository or portal entry.

The initial system `python3` is macOS Python 3.9, below the documented Python 3.11 minimum. Its import failures are an environment mismatch, retained separately. Supported-runtime baseline uses installed Homebrew Python 3.13.15. Existing tests are retained unchanged.

## Contracts and boundaries

`GET /api/config` returns mode, sample and limits. `POST /api/analyze` accepts source and returns a server-owned analysis ID. `POST /api/export` accepts that ID and explicit decisions, retrieving source only from the server. Eight memory-only analyses; one bounded network operation at a time. Preserve these contracts, source spans, source hashes and no implicit approval.

Reuse `safe_get` unchanged in its DNS/public-IP, pinned socket, hostname-verified TLS, redirect, timeout and credential-isolation policy. Add response content type as optional metadata. Candidate verification accepts only citation/candidate IDs found in a stored analysis, never a URL. Bound per-analysis and per-process candidate retrievals. Fixture mode remains network-free.

## Work sequence

1. Add extraction/security regression tests, bounded HTML evidence extraction and explicit inconclusive outcomes.
2. Extend the provider with allowlisted engines, normalized parameter cache keys, sanitized receipts and unchanged attempted-call accounting.
3. Add explicit discovery strategies, stable candidate IDs, evidence-aware deterministic ranking, retained ambiguity and provenance.
4. Add serialized, validated discover/verify endpoints and integrate them into the existing dependency-free UI.
5. Run all original and new checks, a labeled authored benchmark, desktop/mobile browser checks, and a live workflow only if an existing key and current allowance are available.
6. Update architecture, evidence, demo storyboard and proposed entry copy. Do not modify the submission portal.

Content relevance is lexical evidence, not factual verification or semantic equivalence. An inspected candidate with inconclusive/irrelevant content or a missing anchor cannot be exported as a repair. Legacy uninspected approvals remain compatible and are explicitly labeled unverified. No scores are calibrated probabilities.

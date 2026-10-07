# Hackathon entry notes: SourcePatch

**Portal entry submitted October 7, 2026; organizer eligibility has not been established.** The portal status was checked after submission and displayed **SUBMITTED**. The initial 44.28-second submission demonstration used synthetic sample data; its link has now been replaced by the real recording. A separate real SerpApi workflow was verified later October 7, with a provider receipt and URL-only export for one authored typo; see [live evidence](evidence/live-repair-receipt-2026-10-07.json). The public [real SerpApi demo](https://youtu.be/D5dKt3ehCIk) is 1:50. The existing entry remains SUBMITTED and its new demo link persisted after a portal reload. Participant details and the submission receipt are retained outside public documentation.

## Proposed fields

- Project: SourcePatch
- Tagline: Human-reviewed citation repair, with a paper trail
- Track: Open Innovation
- New project: Yes; development began September 30, 2026
- Community source: Confirm with the participant; do not invent partner affiliation

## Description

Documentation often outlives the pages it cites. SourcePatch helps maintainers find likely replacements without silently changing the meaning of a guide. Paste public Markdown, inspect broken external citations, compare ranked candidate pages, approve a destination and export a small diff with evidence.

The local Python workbench preserves surrounding Markdown instead of reformatting the document. It groups duplicate citations, protects code and image destinations, flags ambiguous matches, blocks unsafe network targets and produces a provenance report linking each approved change to its status observation and search query. There is no runtime LLM and no automatic repair threshold.

The default demonstration is offline and explicitly synthetic. The live adapter and safety boundary have offline tests. One actual status/search/approval/export run has now been verified using an intentionally mistyped public Python documentation citation. The submitted entry now links to the actual recorded workflow.

## Meaningful SerpApi usage

Implemented live adapter: Google Search with `engine=google` and a query combining the original hostname and citation label, with URL path topics for generic labels and autolinks. Search supplies the replacement candidates. Ranking considers exact hostname, topic overlap and surrounding context, followed by human review. The adapter parses organic results, limits attempted provider calls to a configurable one through eight per process, caches successful queries, rejects malformed/error/incomplete responses and keeps the key out of reports. Approved changes include a sanitized response receipt with timestamp, response hash, cache use and optional provider search ID. Search remains scoped to the original hostname; cross-domain migration is a documented limitation.

**Executed live evidence:** October 7 at 07:13:42 UTC, Google Search query `site:docs.python.org pathlib Object oriented filesystem paths` returned a real SerpApi HTTP 200 / Success response, search ID `6ac5f1252efef8e34fbc26b4`, with five eligible results and no cache hit. The application observed HTTP 404 for the authored typo `https://docs.python.org/3/library/pathlib/index.html`. An OpenAI Codex agent opened the official Python documentation, approved `https://docs.python.org/3/library/pathlib.html` in the actual UI under user authorization, and exported the patch/provenance. Personal participant semantic review is not claimed. The retained [diff](live-output/sourcepatch.diff) changes exactly one destination span; surrounding prose and code remain unchanged. This is one controlled authored typo, not a broad real-document benchmark or an organizer eligibility determination.

## AI tools

OpenAI coding assistance contributed design, implementation, synthetic fixtures, tests, review, documentation and recovery. No model is used at runtime. See AI_ASSISTANCE.md.

## Submission and remaining verification

- [ ] Confirm participant age 18+, India residency and all other eligibility conditions
- [x] Participant explicitly reviewed and accepted the official Rules and Terms & Conditions
- [x] Required contact, occupation and experience fields supplied in the portal; values omitted here
- [x] Publish a public source repository: [himanshu748/sourcepatch](https://github.com/himanshu748/sourcepatch), reviewed implementation `d5048d7461bd168254a43da76d03babb77723846` and rendered-browser evidence `c758d0d19db88ec8867748514cd785ed8f433309` published October 7
- [x] Review and publish the transport-fixed source snapshot after 80 Python tests, 70 DOM assertions and focused fixture-browser checks
- [x] Securely verify an active free allowance and one real public citation workflow end to end; [receipt](evidence/live-repair-receipt-2026-10-07.json)
- [x] Complete rendered fixture desktop/mobile checks; see [verification](verification.md) for their scope
- [ ] Complete the remaining keyboard/accessibility checks and broader real-document validation
- [x] Record an explicitly labeled fixture demonstration under three minutes (44.28 seconds, included in `landing/assets/`)
- [x] Record the real live workflow and supply the accessible [1:50 demonstration](https://youtu.be/D5dKt3ehCIk)
- [x] Verify public repository and unlisted demo accessibility; YouTube publication confirmed and anonymous oEmbed returned HTTP 200
- [x] Complete the official website form and verify its **SUBMITTED** status on October 7

## Official references checked September 30, 2026

- [Rules](https://serpapi.github.io/serpapi-india-hackathon-2026/rules.html): October 10, 2026 at 23:59 IST deadline; public GitHub repository; publicly accessible screen recording under three minutes; meaningful SerpApi usage; AI disclosure
- [Terms](https://serpapi.github.io/serpapi-india-hackathon-2026/terms.html): ownership remains with participants, but submission grants ongoing administrative/promotional licensing and includes indemnity and individual arbitration provisions
- [Submission dashboard](https://serpapi.github.io/serpapi-india-hackathon-2026/submit.html)
- [SerpApi documentation](https://serpapi.com/search-api)

Recheck the governing rules before submitting. This draft makes no claim of eligibility, acceptance or award likelihood.

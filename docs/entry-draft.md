# Hackathon entry notes: SourcePatch

**Portal entry submitted October 7, 2026; organizer eligibility has not been established.** The portal status was checked after submission and displayed **SUBMITTED**. The public repository includes a labeled 44.28-second fixture recording, tested product improvements and October 7 desktop/mobile evidence. The submitted demonstration explicitly uses synthetic sample data. Successful real SerpApi verification and a live demonstration remain pending; fixture evidence cannot establish working live integration. Participant details and the submission receipt are retained outside public documentation.

## Proposed fields

- Project: SourcePatch
- Tagline: Human-reviewed citation repair, with a paper trail
- Track: Open Innovation
- New project: Yes; development began September 30, 2026
- Community source: Confirm with the participant; do not invent partner affiliation

## Description

Documentation often outlives the pages it cites. SourcePatch helps maintainers find likely replacements without silently changing the meaning of a guide. Paste public Markdown, inspect broken external citations, compare ranked candidate pages, approve a destination and export a small diff with evidence.

The local Python workbench preserves surrounding Markdown instead of reformatting the document. It groups duplicate citations, protects code and image destinations, flags ambiguous matches, blocks unsafe network targets and produces a provenance report linking each approved change to its status observation and search query. There is no runtime LLM and no automatic repair threshold.

The default demonstration is offline and explicitly synthetic. The live adapter and safety boundary have offline tests. A real SerpApi run is still necessary before claiming working live search in a submitted demonstration.

## Meaningful SerpApi usage

Implemented live adapter: Google Search with `engine=google` and a query combining the original hostname and citation label, with URL path topics for generic labels and autolinks. Search supplies the replacement candidates. Ranking considers exact hostname, topic overlap and surrounding context, followed by human review. The adapter parses organic results, limits attempted provider calls to a configurable one through eight per process, caches successful queries, rejects malformed/error/incomplete responses and keeps the key out of reports. Approved changes include a sanitized response receipt with timestamp, response hash, cache use and optional provider search ID. Search remains scoped to the original hostname; cross-domain migration is a documented limitation.

**Evidence limit:** no real API request was performed. Fixture behavior and offline contract tests do not establish meaningful live usage for eligibility.

## AI tools

OpenAI coding assistance contributed design, implementation, synthetic fixtures, tests, review, documentation and recovery. No model is used at runtime. See AI_ASSISTANCE.md.

## Submission and remaining verification

- [ ] Confirm participant age 18+, India residency and all other eligibility conditions
- [x] Participant explicitly reviewed and accepted the official Rules and Terms & Conditions
- [x] Required contact, occupation and experience fields supplied in the portal; values omitted here
- [x] Publish a public source repository: [himanshu748/sourcepatch](https://github.com/himanshu748/sourcepatch), reviewed implementation `d5048d7461bd168254a43da76d03babb77723846` and rendered-browser evidence `c758d0d19db88ec8867748514cd785ed8f433309` published October 7
- [x] Review and publish the newer source snapshot after 76 Python tests, 70 DOM assertions and focused rendered-browser checks
- [ ] Supply an existing SerpApi key securely and verify a real public citation end to end
- [x] Complete rendered fixture desktop/mobile checks; see [verification](verification.md) for their scope
- [ ] Complete the remaining keyboard/accessibility checks and real live workflow checks
- [x] Record an explicitly labeled fixture demonstration under three minutes (44.28 seconds, included in `landing/assets/`)
- [ ] Record the real live workflow and supply an accessible demonstration link under three minutes
- [ ] Verify repository and demo links open without requesting access
- [x] Complete the official website form and verify its **SUBMITTED** status on October 7

## Official references checked September 30, 2026

- [Rules](https://serpapi.github.io/serpapi-india-hackathon-2026/rules.html): October 10, 2026 at 23:59 IST deadline; public GitHub repository; publicly accessible screen recording under three minutes; meaningful SerpApi usage; AI disclosure
- [Terms](https://serpapi.github.io/serpapi-india-hackathon-2026/terms.html): ownership remains with participants, but submission grants ongoing administrative/promotional licensing and includes indemnity and individual arbitration provisions
- [Submission dashboard](https://serpapi.github.io/serpapi-india-hackathon-2026/submit.html)
- [SerpApi documentation](https://serpapi.com/search-api)

Recheck the governing rules before submitting. This draft makes no claim of eligibility, acceptance or award likelihood.

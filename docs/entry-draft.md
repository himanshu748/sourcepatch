# Hackathon entry draft: SourcePatch

**Not submitted or submission-ready.** Live SerpApi verification, browser QA, a public source release and an accessible screen recording remain required. No hackathon registration, account creation or terms acceptance was performed as part of this build.

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

Intended live integration: Google Search with `engine=google` and a query combining the original hostname and citation label. Search supplies the replacement candidates. Ranking considers exact hostname, title overlap and surrounding context, followed by human review. The adapter parses organic results, caps the process at eight requests, caches repeated queries, handles malformed/error responses and keeps the key out of reports.

**Evidence limit:** no real API request was performed. Fixture behavior and offline contract tests do not establish meaningful live usage for eligibility.

## AI tools

OpenAI coding assistance contributed design, implementation, synthetic fixtures, tests, review, documentation and recovery. No model is used at runtime. See AI_ASSISTANCE.md.

## Before submission

- [ ] Confirm participant age 18+, India residency and all other eligibility conditions
- [ ] Review and approve the official Rules and Terms & Conditions
- [ ] Confirm form details: name, email, mobile number, occupation and experience
- [ ] Review and publish the new source snapshot
- [ ] Supply an existing SerpApi key securely and verify a real public citation end to end
- [ ] Complete manual desktop/mobile/keyboard checks
- [ ] Record an honest screen demonstration under three minutes
- [ ] Verify repository and demo links open without requesting access
- [ ] Complete the official website form before the current deadline and verify it is submitted, not a draft

## Official references checked September 30, 2026

- [Rules](https://serpapi.github.io/serpapi-india-hackathon-2026/rules.html): October 10, 2026 at 23:59 IST deadline; public GitHub repository; publicly accessible screen recording under three minutes; meaningful SerpApi usage; AI disclosure
- [Terms](https://serpapi.github.io/serpapi-india-hackathon-2026/terms.html): ownership remains with participants, but submission grants ongoing administrative/promotional licensing and includes indemnity and individual arbitration provisions
- [Submission dashboard](https://serpapi.github.io/serpapi-india-hackathon-2026/submit.html)
- [SerpApi documentation](https://serpapi.com/search-api)

Recheck the governing rules before submitting. This draft makes no claim of eligibility, acceptance or award likelihood.

# SourcePatch landing verification

Dedicated static landing built on `5412ff98a0ce7c82b54ef124e941d49449952698`, branch `improve/sourcepatch-landing-20261004`. Its design inherits the existing editorial desk; the application remains unchanged. All 42 original tracked files were checked against baseline bytes, including `sourcepatch/`, `web/`, `tests/`, PRODUCT.md and DESIGN.md.

## Executed checks

| Requirement / evidence criterion | Status | Supporting evidence and scope |
| --- | --- | --- |
| Product purpose and clear action | Passed | Desktop/mobile first-viewport captures show the product promise, fixture CTA, real original/candidate URLs and repository CTA. |
| Distinct product-grounded design | Passed at implementation scope | Editorial typography and forest/paper desk grammar; actual source-evidence comparison and citation ledger. Parent independent design review is separate. |
| Honest fixture/live distinction | Passed | Browser disclosure assertions; complete fixture dataset exactly equals `analyze(SAMPLE, mode='fixture')`; all `verified` flags and `live_verified` remain false. |
| Interactive evidence | Passed | Browser search, hostile/no-match recovery, keyboard selection, exact discovery query, tied 91/100 scores, healthy and blocked states. |
| URL-only change and provenance | Passed for synthetic sample | Self-contained links return HTTP 200; exact copied diff/report/Markdown bytes; report retains `approved_by_user: false` and hypothetical approval. No approval is performed by the landing. |
| Responsive desktop/mobile | Passed | 1440×1000 and 390×844 screenshots; no document-level horizontal overflow at either width. |
| Keyboard and reduced motion | Passed at tested scope | Keyboard search/selection, 3px solid focus, semantic controls, skip link and reduced-motion `scroll-behavior: auto`. |
| JavaScript-free fallback | Passed | Rendered no-JavaScript context retains the Python example, candidate evidence, fixture disclosures, navigation and artifact links. |
| Palette contrast | Passed for measured pairs | Eight text/status color pairings measure 5.70–13.05:1 in `content-integrity.json`. Not a complete accessibility certification. |
| Portable static build | Passed | All local assets and anchors resolve; no duplicate IDs; no framework, installs or build dependencies; core payload 12,660 gzip bytes. |
| Real media with provenance | Passed locally | MP4/poster match existing workspace assets; ffprobe confirms H.264 1440×1000, 25fps, 44.28 seconds, no audio. No autoplay, `preload="none"`; written walkthrough included. |
| Browser/runtime integrity | Passed | Zero page errors and zero external requests. Local clone command copies correctly. |
| Application preservation | Passed | All 42 original tracked files byte-identical to baseline. Existing 68 Python / 64 DOM assertions were not rerun for this isolated static addition. |
| Meaningful live SerpApi proof | Not run | No key or provider call used. Confirmed free allowance, secure key and meaningful live end-to-end verification remain outstanding. |
| Public landing/video access | Not run | Local-only deliverable; no push, deployment or invented public asset URL. |
| Eligibility/legal/final submission | Not run | Existing draft is not a final submission. Participant declarations, legal fields and public live demonstration remain unresolved. |
| Complete screen-reader audit | Not run | Tested keyboard and static fallback do not establish full assistive-technology coverage. |
| Impeccable launcher/detector | Not run | Launcher path unavailable, exit 127. Existing PRODUCT.md/DESIGN.md and skill references read directly; no installs or downloads. |

The mapping above describes the landing deliverable and evidence scope; it is not an official hackathon score or claim of eligibility.

Source/code whitespace checks pass when excluding the byte-identical copied `landing/demo-output/sourcepatch.diff`. A default `git diff --check` over that artifact flags three context-blank lines: a unified diff intentionally stores a single space as the context prefix. Those bytes are preserved to keep the real sample valid and identical to the baseline artifact, rather than stripping its patch syntax.

## Skill and context evidence

Actual Impeccable resources read via `skills.read`:

- [SKILL.md](skill://plugins_6a5028ae047081918e3dfde753112690/impeccable/SKILL.md)
- [reference/new-work.md](skill://plugins_6a5028ae047081918e3dfde753112690/impeccable/reference/new-work.md)
- [reference/craft-floor.md](skill://plugins_6a5028ae047081918e3dfde753112690/impeccable/reference/craft-floor.md)

Attempted context command: `.codex/skills/impeccable/scripts/impeccable context --target landing/index.html`, from the task-4 workspace. It returned exit 127, “no such file or directory.” The launcher did not run successfully; the detector was not run. No replacement launcher was installed or downloaded.

Project context read directly: existing `PRODUCT.md`, `DESIGN.md`, `README.md`, `docs/verification.md`, `sourcepatch/fixtures.py`, `sourcepatch/engine.py`, `examples/field-guide.md`, `docs/demo-output/sourcepatch.diff`, `docs/demo-output/provenance.json` and the task-4 fixture-browser/video receipts. The ancestor/project AGENTS search found no applicable AGENTS.md. `docs/landing-surface.md` records this new Persuade surface inside the inherited world; original PRODUCT.md and DESIGN.md remain byte-identical.

The parent requested a fresh independent reviewer after packaging. That review is pending and is not represented as a completed skill review.

## Bounded inspection

One completed browser inspection batch captured desktop and mobile first viewports and full pages. Every screenshot was opened and checked for valid content. No material render defect required a fix, and no second inspection was run.

Two initial environment attempts produced no screenshots: sandboxed Chromium exited SIGABRT; the first sandboxed loopback bind was denied and the corresponding browser attempt received connection refused. Once execution permissions were granted, the same local-only script completed. Logs preserve those environment failures separately from the successful run.

| Execution attempt | Status | Outcome |
| --- | --- | --- |
| Default-sandbox Chromium / loopback preview | Failed | SIGABRT / denied loopback bind; no capture produced. |
| First authorized browser launch before the server was available | Failed | Connection refused; no capture produced. |
| Authorized local-only browser batch with server running | Passed | Complete desktop/mobile checks and four valid captures. |
| Impeccable detector | Not run | Launcher unavailable. |

## Evidence files

- `static-build.json`: static references, deterministic engine equality, payload and asset hashes.
- `content-integrity.json`: baseline preservation, source asset identity and measured contrast.
- `browser-receipt.json` and `browser-check-final.log`: successful rendered fixture checks.
- `desktop-first-viewport.png`, `mobile-first-viewport.png`, `desktop.png`, `mobile.png`: inspected captures.
- `video-metadata.json`: actual shipped MP4 metadata.
- `check-browser.cjs`: reproducible local-only browser check, using the already installed Playwright/Chromium paths in this execution environment.

Reproduce the static check with Python 3.11+: `python3 landing/check-static.py`. Serve `landing/` on loopback port 8784, then run `node docs/landing-evidence/check-browser.cjs` in the same prepared environment. It blocks external requests; it never runs a provider request, changes a document or submits a project.

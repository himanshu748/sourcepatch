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
| Portable static build | Passed | All local assets and anchors resolve; no duplicate IDs; no framework, installs or build dependencies; repaired core payload 12,633 gzip bytes (`static-build-confirmation.json`). |
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

The parent obtained a fresh independent review after initial packaging. It requested larger meaningful evidence/disclosure text and the missing six-block direction contract. The same reviewer's repair verdict is pending; a self-check is not represented as that verdict.

The repair also used the completely read [Frontend Testing and Debugging skill](skill://plugins~Plugin_d0e159446ee48191b94ce1960780cc3c/frontend-testing-debugging/SKILL.md). Browser availability: **Absent**. Browser/IAB tools and the Browser skill are not present in this Mac session, so the existing installed Playwright/Chromium fallback is retained. No dependency or browser install was performed. Target flow: landing loads → select a fixture citation → evidence, caveats and disclosures stay readable on desktop/mobile.

## Bounded inspection

The initial completed browser inspection batch captured desktop and mobile first viewports and full pages. Every screenshot was opened and checked for valid content. The initial self-inspection did not identify a material render defect; the subsequent fresh review found the legibility and documentation gaps described above. One repair batch raises meaningful text to at least 14px (titles/snippets/notices 15px), permits wrapping, and records the actual inherited/code-led direction contract. The original screenshots and receipts are preserved. The sole coordinated confirmation batch passed, producing six valid, opened captures in `confirmation/`, including desktop/mobile evidence panes at viewing size. No further UI edit or browser rerun followed.

## Repair confirmation

| Required check | Status | Evidence |
| --- | --- | --- |
| Page identity / nonblank / framework overlay | Passed | Correct URL/title, meaningful heading/body and no framework error overlay. |
| Readable evidence and disclosures | Passed at measured scope | Minimum 14px across sampled meaningful text at 1440px and 390px; titles/snippets/notices 15px; zero sampled horizontal clipping and no document overflow. |
| Existing interactions | Passed | Search → keyboard select fetch → exact tied scores/query; no-match recovery; healthy/blocked states; mobile pandas selection; accurate clipboard command and real asset responses. |
| Console health | Passed | Zero page errors, console errors/warnings or external requests. |
| No-JavaScript and reduced motion | Passed | Static evidence/links retained; reduced-motion scroll behavior is auto. |
| Screenshot evidence | Passed | Six confirmation captures opened and valid; original captures retained. |
| Direction contract | Recorded | Six required blocks and actual-brief QUALITY BAR in `docs/landing-surface.md`; honest unavailable launcher/code-led fallback; no invented concept evidence. |
| Preserve every process | Failed | Executed harness closed its owned test contexts, Chromium and Playwright driver after the pass. The existing preview server and pre-existing processes were preserved. No claim that every process was preserved. |
| Future harness retention | Source repair only; not run | Explicit context/browser closes removed, references retained with an idle interval. Per parent instruction this script-only repair was not executed again; completed test evidence is unchanged. |
| Same reviewer's repair verdict | Not run / pending | Updated evidence is forwarded for disposition on the two findings only. |

The owned test-browser closure violated the repeated process-preservation instruction. The final script differs from the tested script only in lifecycle retention. The retained-process behavior is unexecuted; the existing passing confirmation remains evidence for the page and typography, not for the corrected lifecycle behavior.

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
- `confirmation/browser-receipt.json`, `browser-check-confirmation.log`, and six `confirmation/*.png` captures: repaired-page confirmation. These executed receipts were not retroactively edited after the process-retention repair.
- `static-build-confirmation.json`: static fixture/asset equality and 12,633-byte compressed core for the repaired page.

Reproduce the static check with Python 3.11+: `python3 landing/check-static.py`. Serve `landing/` on loopback port 8784, then run `node docs/landing-evidence/check-browser.cjs` in the same prepared environment. It blocks external requests; it never runs a provider request, changes a document or submits a project.

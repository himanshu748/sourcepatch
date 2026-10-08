# SourcePatch public build

The static landing at https://sourcepatch.pages.dev/ leads with a recorded real SerpApi workflow. `assets/live-data.js` exactly copies the sanitized `docs/evidence/v2/live-final/03-verify.json`. The three download artifacts in `demo-output/` exactly copy the actual browser export. A deliberate input typo is disclosed; the ETH page is an alternative educational source, not a recovered original.

The public site performs no fresh search, approval, provider transport or persistence. The full dependency-free Python workbench runs locally with an existing key. The source ZIP excludes Git metadata and landing assets. Python 3.11+ is required.

`assets/sourcepatch-v2-demo.mp4` is a 100-second real browser recording with synthetic narration and captions, cropped to application content. Mode and timestamp labels are persistent. `docs/demo-script.md` contains the transcript.

`fixture.html`, `fixture.js`, `assets/fixture-data.js` and `fixture-output/` preserve the separate labelled offline regression example. Its 95-second video, caption file and poster retain their own fixture labels. Historical media assets remain available.

Serve locally with `python3 -m http.server 8784 --bind 127.0.0.1 --directory landing`. Validate assets, exact evidence equality and the small compressed payload with `python3 landing/check-static.py`. No external fonts, analytics, trackers, runtime libraries or automatic video playback.

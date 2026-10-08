# SourcePatch landing

Dependency-free, static landing page, separate from the local application in `web/`. The October 4 landing implementation preserved the application bytes. Its fixture dataset and provenance copies were refreshed October 7 to match the improved local analysis engine; the recording remains the original explicitly labeled fixture walkthrough.

Serve the self-contained landing directory:

```sh
python3 -m http.server 8784 --bind 127.0.0.1 --directory landing
```

Open `http://127.0.0.1:8784/`. This host is only a static preview. To run the actual fixture workbench, follow the repository README.

The landing uses the established SourcePatch palette and Georgia/system typography. Its fixture explorer is read-only. It filters and displays `assets/fixture-data.js`, generated from the existing `sourcepatch.engine.analyze(SAMPLE)` in fixture mode. The complete authored dataset identifies `mode: fixture` and `live_verified: false`. JavaScript-disabled visitors retain a complete Python pathlib example and the real artifact links.

## Asset provenance

- `assets/sourcepatch-fixture-labelled.mp4`: copied from the existing task-4 `sourcepatch-demo/sourcepatch-fixture-labelled.mp4`, created October 4, 2026. The fixture disclaimer is burned into the video. H.264, 1440×1000, 25 fps, 44.28 seconds, no audio. This demonstrates synthetic data; it is not live SerpApi proof.
- `assets/fixture-video-poster.png`: the existing `sourcepatch-demo/labelled-thumb.png`, a frame from that labelled recording. No generated image, stock image, or remote asset.
- `assets/favicon.svg` and small interface icons: authored vector geometry in the established forest/paper palette.
- The `demo-output/` sample artifacts are byte-identical copies of the actual checked-in files in the repository’s `docs/demo-output/` directory. `docs/demo-script.md` adapts the old shooting plan into a current fixture walkthrough; the original script remains unchanged. Both are included so the landing remains portable. They do not invent public video or deployment URLs.

The landing performs no provider requests and uses no external dependencies, fonts, cookies, analytics, local storage, account flow, or automatic video playback. One controlled real SerpApi workflow is now verified; the existing portal entry remains submitted with the [real demo](https://youtu.be/D5dKt3ehCIk). The embedded fixture walkthrough remains explicitly synthetic. See the main README for evidence and limitations.

## October 8 V2 publication

Public landing: https://sourcepatch.pages.dev/ . The main embedded video is now `assets/sourcepatch-v2-demo.mp4`: 95 seconds, H.264/AAC, 1920x1200 at 30 fps, actual native Comet window recording cropped to browser content. Persistent fixture label and summary captions were composited; synthetic Samantha narration was added after capture. Search/page results were not recreated. This is authored fixture data, not a live-provider recording. The old 44-second video remains a historical asset.

V2 source download is a runnable ZIP of the existing repository application, tests and documentation. It excludes Git metadata and the landing directory. The website only exposes static files and never handles the SerpApi key. Fresh live search and abstention provenance is linked separately.

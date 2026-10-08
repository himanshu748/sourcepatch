"""Validate the dependency-free landing against local assets and real fixtures."""
from html.parser import HTMLParser
import gzip
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
LANDING = ROOT / "landing"
sys.path.insert(0, str(ROOT))
from sourcepatch.engine import analyze
from sourcepatch.fixtures import SAMPLE


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for attr in ("href", "src", "poster"):
            if attr in attrs:
                self.refs.append(attrs[attr])


def main():
    html = (LANDING / "index.html").read_text()
    refs = References()
    refs.feed(html)
    assert len(refs.ids) == len(set(refs.ids)), "Duplicate HTML IDs"
    for ref in refs.refs:
        parts = urlsplit(ref)
        if parts.scheme:
            assert parts.scheme == "https", f"Unexpected external scheme: {ref}"
            assert parts.hostname in {"github.com", "youtu.be"}, f"Unexpected external link: {ref}"
        elif parts.path:
            target = (LANDING / parts.path).resolve()
            assert target.is_relative_to(ROOT), f"Reference escapes repository: {ref}"
            assert target.is_file(), f"Missing local asset: {ref}"
        elif parts.fragment:
            assert parts.fragment in refs.ids, f"Missing anchor: {ref}"

    data_file = LANDING / "assets/fixture-data.js"
    encoded = data_file.read_text().split("window.SOURCEPATCH_FIXTURE = ", 1)[1].strip().removesuffix(";")
    dataset = json.loads(encoded)
    assert dataset == analyze(SAMPLE, mode="fixture"), "Fixture data drifted from engine"
    assert dataset["live_verified"] is False
    assert all(c["check"]["verified"] is False for c in dataset["citations"])
    assert len(dataset["citations"]) == 5

    files = [LANDING / name for name in ("index.html", "style.css", "landing.js", "assets/fixture-data.js", "assets/favicon.svg")]
    payload = sum(len(gzip.compress(p.read_bytes())) for p in files)
    assert payload < 20000, f"Core compressed payload exceeds 20 KB: {payload}"
    js = (LANDING / "landing.js").read_text()
    for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "innerHTML"):
        assert forbidden not in js, f"Unexpected operation: {forbidden}"

    print(json.dumps({
        "status": "passed",
        "checks": ["Local assets and anchors exist", "External links restricted to the repository and existing demo", "No duplicate HTML IDs", "Full fixture data exactly matches the real analysis engine", "All evidence remains unverified", "Five fixture destinations", "Core compressed payload under 20 KB", "No provider transport, persistence, or HTML injection APIs"],
        "core_gzip_bytes": payload,
        "asset_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (LANDING / "assets").iterdir() if p.is_file()},
    }, indent=2))


if __name__ == "__main__":
    main()

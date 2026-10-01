"""Run `python -m sourcepatch` for the local fixture workbench."""
import argparse
import getpass
import json
import sys
import warnings
from pathlib import Path

from .engine import analyze, export_review
from .fixtures import SAMPLE
from .network import SerpApiSearch
from .server import make_server


def main():
    parser = argparse.ArgumentParser(description='SourcePatch: a local Markdown citation-repair workbench.')
    parser.add_argument('--mode', choices=['fixture', 'live'], default='fixture')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--demo-export', type=Path, metavar='NEW_DIRECTORY', help='Write a labeled fixture patch and report, then exit.')
    args = parser.parse_args()
    if args.demo_export:
        if args.mode != 'fixture':
            parser.error('--demo-export is fixture-only')
        args.demo_export.mkdir(parents=True, exist_ok=False)
        a = analyze(SAMPLE)
        first = a['citations'][0]
        out = export_review(SAMPLE, a, {first['id']: first['candidates'][0]['url']})
        out['provenance']['approval_context'] = 'Authored demo scenario: hypothetical approval; not an actual reviewer decision.'
        for change in out['provenance']['changes']:
            change['approved_by_user'] = False
            change['approval_context'] = 'Hypothetical authored fixture approval.'
        for name, data in [('guide.md', SAMPLE), ('guide.patched.md', out['markdown']), ('sourcepatch.diff', out['diff']),
                           ('provenance.json', json.dumps(out['provenance'], indent=2, ensure_ascii=False))]:
            (args.demo_export / name).write_text(data, encoding='utf-8', newline='')
        print(f'Wrote synthetic fixture evidence to {args.demo_export}. No live requests were made.')
        return
    provider = None
    if args.mode == 'live':
        if not sys.stdin.isatty():
            parser.error('Live mode requires an interactive terminal for no-echo key input.')
        print('Live mode sends citation URLs to their sites and generated title/site queries to SerpApi.')
        print('Use an existing key with available credits. At most eight searches per process; no paid plan is created.')
        print('Do not paste confidential documents. Your key is kept only in this process and is never logged or saved.')
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', getpass.GetPassWarning)
                key = getpass.getpass('Existing SerpApi key (hidden): ')
            provider = SerpApiSearch(key)
            del key
        except (getpass.GetPassWarning, EOFError, ValueError):
            parser.error('A valid existing key and an interactive terminal with no-echo input are required.')
    server = make_server(port=args.port, mode=args.mode, search=provider.search if provider else None)
    print(f'SourcePatch: http://127.0.0.1:{server.server_port} ({args.mode} mode)')
    print('Fixture data is synthetic and not live verified.' if args.mode == 'fixture' else 'Live network mode enabled; candidate meaning and anchors remain unverified.')
    print('Press Ctrl+C to stop. Documents and decisions are stored in memory only.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

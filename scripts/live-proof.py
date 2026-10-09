"""No-echo allowance preflight, then a one-attempt local workbench. No saved key."""
from datetime import datetime, timezone
import getpass
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlencode
import warnings
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sourcepatch.network import NetworkError, SerpApiSearch, safe_get
from sourcepatch.server import make_server


def allowance(key, fetch=safe_get):
    try:
        result = fetch('https://serpapi.com/account.json?' + urlencode({'api_key':key}),
                       timeout=10, max_bytes=32768, max_redirects=0)
        if result.status != 200 or result.truncated:
            raise ValueError()
        data = json.loads(result.body)
        left = data.get('plan_searches_left')
        if data.get('account_status') != 'Active' or type(left) is not int or left < 1:
            raise ValueError()
        return {'checked_at':datetime.now(timezone.utc).isoformat(),'account_status':'Active',
                'plan_searches_left':left,'response_sha256':hashlib.sha256(result.body).hexdigest(),
                'attempted_search_cap':1}
    except Exception:
        raise NetworkError('Current active allowance could not be verified. No search started; no automatic retry.') from None


def main():
    if not sys.stdin.isatty():
        raise NetworkError('An interactive terminal is required for hidden key entry.')
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        key = getpass.getpass('Existing SerpApi key (hidden): ')
    provider = SerpApiSearch(key, max_searches=1)
    receipt = allowance(key)
    del key
    print(json.dumps(receipt, indent=2))
    server = make_server(port=8773, mode='live', search=provider.search, process_search_budget=1)
    print('Open http://127.0.0.1:8773. Paste one public broken citation and inspect once.')
    print('Select the discovered candidate, inspect its page, review, explicitly approve, then download provenance and patch.')
    print('The key and documents remain in memory. No purchase, upgrade, automatic retry or fixture fallback.')
    try:
        server.serve_forever()
    finally:
        server.server_close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        print('Live proof stopped safely. Check your terminal, existing key, allowance and port 8773. No automatic retry.', file=sys.stderr)
        sys.exit(1)

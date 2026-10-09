"""Authored synthetic fixtures. They are NOT saved live search or HTTP responses."""
from pathlib import Path

SAMPLE = (Path(__file__).resolve().parent.parent / 'examples' / 'field-guide.md').read_text(encoding='utf-8')
FIXTURE_DATE = '2026-09-30T00:00:00Z'
ROWS = {
    'https://docs.python.org/3/library/pathlib-old.html': {
        'status': 404,
        'results': [
            {'title': 'pathlib — Object-oriented filesystem paths — Python documentation', 'link': 'https://docs.python.org/3/library/pathlib.html', 'snippet': 'Path objects represent filesystem paths. The pathlib module offers classes for working with directories and files.'},
            {'title': 'Python file and directory access', 'link': 'https://docs.python.org/3/library/filesys.html', 'snippet': 'Overview of standard-library tools for working with files and directories.'},
            {'title': 'A tutorial on filesystem paths', 'link': 'https://realpython.com/python-pathlib/', 'snippet': 'A third-party introduction to pathlib and path objects.'},
        ],
    },
    'https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/abort-old': {
        'status': 404,
        'results': [
            {'title': 'Abort a fetch request: AbortController', 'link': 'https://developer.mozilla.org/en-US/docs/Web/API/AbortController', 'snippet': 'The AbortController interface lets you abort a fetch request using a controller and its signal.'},
            {'title': 'Abort a fetch request: AbortSignal', 'link': 'https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal', 'snippet': 'An AbortSignal object communicates with a request and lets you abort a fetch operation.'},
        ],
    },
    'https://pandas.pydata.org/docs/old/reference/frame.html': {
        'status': 410,
        'results': [
            {'title': 'pandas DataFrame — pandas documentation', 'link': 'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html', 'snippet': 'Two-dimensional, size-mutable, potentially heterogeneous tabular data.'},
            {'title': 'pandas Series — pandas documentation', 'link': 'https://pandas.pydata.org/docs/reference/api/pandas.Series.html', 'snippet': 'A one-dimensional labeled array capable of holding any data type.'},
        ],
    },
    'https://docs.python.org/3/library/dataclasses.html': {'status': 200, 'results': []},
}


def fixture_check(url):
    record = ROWS.get(url.split('#', 1)[0])
    if not record:
        return {'state': 'unavailable', 'status': None, 'verified': False,
                'detail': 'No authored fixture for this URL. No network request was made.'}
    status = record['status']
    return {'state': 'healthy' if status == 200 else 'broken', 'status': status,
            'verified': False, 'detail': 'Synthetic fixture status. Not a live HTTP observation.'}


def fixture_results(url):
    return [dict(row) for row in ROWS.get(url.split('#', 1)[0], {}).get('results', [])]

# Authored HTML, not downloaded or reconstructed provider/page responses.
PAGE_FIXTURES = {
    'https://docs.python.org/3/library/pathlib.html': '<title>Python pathlib — filesystem paths</title><h1 id="paths">Python pathlib filesystem paths</h1><p>Python pathlib Path objects represent filesystem paths and work with directories and files.</p>',
    'https://docs.python.org/3/library/filesys.html': '<title>File and directory access</title><h1>File tools</h1><p>The standard library provides modules for working with files and directories.</p>',
    'https://developer.mozilla.org/en-US/docs/Web/API/AbortController': '<title>Abort a fetch request: AbortController</title><h1>Abort a fetch request</h1><p>AbortController can abort a fetch request using a controller and its signal.</p>',
    'https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal': '<title>Abort a fetch request: AbortSignal</title><h1>Abort a fetch request</h1><p>AbortSignal communicates with a fetch request to abort a fetch operation.</p>',
    'https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html': '<title>pandas DataFrame</title><h1>pandas DataFrame reference</h1><p>A pandas DataFrame is a two-dimensional tabular data structure for rows and columns.</p>',
    'https://pandas.pydata.org/docs/reference/api/pandas.Series.html': '<title>pandas Series</title><h1>Series</h1><p>A Series is a one-dimensional labeled array holding data of any type.</p>',
}


def fixture_page(url, **_limits):
    from .network import FetchResult, NetworkError
    base = url.split('#', 1)[0]
    if base not in PAGE_FIXTURES:
        raise NetworkError('No authored page fixture for this candidate.')
    return FetchResult(200, base, PAGE_FIXTURES[base].encode(), content_type='text/html; charset=utf-8')

# Input only: all statuses, discovery and page observations are fetched in live mode.
LIVE_SAMPLE = '''# A public citation review

This example deliberately mistypes a documentation URL. It is not a historical migration.

Use [Python pathlib](https://docs.python.org/3/library/pathlib/index.html) for filesystem paths, files and directories.
Keep the [Python pathlib reference](https://docs.python.org/3/library/pathlib/index.html) nearby while writing scripts.
'''

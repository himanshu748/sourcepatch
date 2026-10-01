"""Bounded HTTP fetching with public-address validation and pinned connections.

No proxy/environment credentials, cookies, or automatic redirects are used.
This is defense in depth for a local tool, not a replacement for an egress firewall.
"""
from dataclasses import dataclass
import http.client
import ipaddress
import json
import queue
import re
import socket
import ssl
import threading
import time
from urllib.parse import quote, urlencode, urljoin, urlsplit, urlunsplit


class NetworkError(ValueError):
    """A safe-to-display error that never embeds credentials or response bodies."""


@dataclass
class FetchResult:
    status: int
    url: str
    body: bytes
    truncated: bool = False


def _public_ip(value):
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    if not ip.is_global or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return False
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped or ip.sixtofour or ip.teredo:
            return False
    return True


def validate_url(url: str):
    if not isinstance(url, str) or not 1 <= len(url) <= 4096:
        raise NetworkError('URL must be text of at most 4,096 characters.')
    if any(ord(c) <= 32 or ord(c) == 127 or c in '\\<>"\'' for c in url):
        raise NetworkError('URL contains unsafe characters.')
    try:
        parts = urlsplit(url)
        host = parts.hostname
        port = parts.port
        if parts.scheme not in ('https', 'http') or not host:
            raise NetworkError('Only absolute HTTP and HTTPS URLs are supported.')
        if parts.username is not None or parts.password is not None:
            raise NetworkError('URLs containing credentials are blocked.')
        if port not in (None, 443 if parts.scheme == 'https' else 80):
            raise NetworkError('Only the default HTTP or HTTPS port is allowed.')
        if '%' in host or host.endswith('.'):
            raise NetworkError('Scoped or ambiguous hostnames are blocked.')
        host = host.encode('idna').decode('ascii').lower()
        try:
            ipaddress.ip_address(host)
        except ValueError:
            if (len(host) > 253 or '.' not in host or re.fullmatch(r'[0-9.]+', host)
                    or host.endswith(('.local', '.localhost', '.internal', '.invalid', '.test', '.example'))
                    or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in host.split('.'))):
                raise NetworkError('Local, malformed, or ambiguous hostnames are blocked.')
        else:
            if not _public_ip(host):
                raise NetworkError('Private, reserved, or non-public network targets are blocked.')
        return parts
    except (ValueError, UnicodeError) as error:
        if isinstance(error, NetworkError):
            raise
        raise NetworkError('Malformed URL.') from None


_DNS_SLOTS = threading.BoundedSemaphore(4)


def resolve_public(host: str, port: int, timeout: float = 5) -> list[str]:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not _public_ip(host):
            raise NetworkError('Non-public network target blocked.')
        return [host]
    if not _DNS_SLOTS.acquire(blocking=False):
        raise NetworkError('DNS resolver is busy. Try again later.')
    results = queue.Queue(maxsize=1)

    def lookup():
        try:
            results.put(socket.getaddrinfo(host, port, type=socket.SOCK_STREAM))
        except Exception:
            results.put(None)
        finally:
            _DNS_SLOTS.release()

    threading.Thread(target=lookup, daemon=True).start()
    try:
        rows = results.get(timeout=max(0.01, timeout))
    except queue.Empty:
        raise NetworkError('DNS resolution timed out.') from None
    if not rows:
        raise NetworkError('Could not resolve the hostname.')
    addresses = list(dict.fromkeys(row[4][0] for row in rows))
    if not all(_public_ip(ip) for ip in addresses):
        raise NetworkError('DNS returned a non-public address; request blocked.')
    return addresses


class _PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout)
        self.address = address
        self.deadline = time.monotonic() + timeout

    def connect(self):
        self.sock = socket.create_connection((self.address, self.port), self.timeout)


class _PinnedHTTPS(_PinnedHTTP):
    def connect(self):
        raw = socket.create_connection((self.address, self.port), self.timeout)
        try:
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise NetworkError('TLS connection timed out.')
            raw.settimeout(remaining)
            self.sock = ssl.create_default_context().wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


def _request_once(url, address, *, deadline, max_bytes):
    parts = validate_url(url)
    host = parts.hostname.encode('idna').decode('ascii')
    port = parts.port or (443 if parts.scheme == 'https' else 80)
    timeout = max(0.01, deadline - time.monotonic())
    cls = _PinnedHTTPS if parts.scheme == 'https' else _PinnedHTTP
    conn = cls(host, port, address, timeout)
    path = quote(urlunsplit(('', '', parts.path or '/', parts.query, '')), safe='/%?:@!$&()*+,;=-._~[]')
    timer = None
    response = None
    try:
        conn.connect()
        transport = conn.sock
        # HTTP/1.0 may detach conn.sock into response.fp. Retain the transport.
        def expire():
            try:
                transport.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise NetworkError('Request timed out.')
        timer = threading.Timer(remaining, expire)
        timer.daemon = True
        timer.start()
        conn.request('GET', path, headers={'User-Agent': 'SourcePatch/0.1 (local citation review)',
                                         'Accept': 'application/json,text/html;q=0.9,*/*;q=0.5',
                                         'Accept-Encoding': 'identity', 'Connection': 'close'})
        response = conn.getresponse()
        headers = {k.lower(): v for k, v in response.getheaders()}
        if response.status in (301, 302, 303, 307, 308):
            return response.status, headers, b'', False
        body = bytearray()
        while len(body) <= max_bytes:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise NetworkError('Request timed out.')
            transport.settimeout(remaining)
            chunk = response.read1(min(16_384, max_bytes + 1 - len(body)))
            if not chunk:
                break
            body.extend(chunk)
        if time.monotonic() >= deadline:
            raise NetworkError('Request timed out.')
        return response.status, headers, bytes(body[:max_bytes]), len(body) > max_bytes
    finally:
        if timer:
            timer.cancel()
        if response is not None:
            response.close()
        conn.close()


def safe_get(url: str, timeout: float = 5, max_bytes: int = 262_144, max_redirects: int = 3) -> FetchResult:
    if not 0 < timeout <= 15 or not 0 < max_bytes <= 1_048_576 or not 0 <= max_redirects <= 5:
        raise NetworkError('Invalid network request limits.')
    deadline = time.monotonic() + timeout
    try:
        for hop in range(max_redirects + 1):
            parts = validate_url(url)
            url = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ''))
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise NetworkError('Request timed out.')
            host = parts.hostname.encode('idna').decode('ascii')
            addresses = resolve_public(host, parts.port or (443 if parts.scheme == 'https' else 80), remaining)
            status, headers, body, truncated = _request_once(url, addresses[0], deadline=deadline, max_bytes=max_bytes)
            if status in (301, 302, 303, 307, 308):
                if hop == max_redirects or not headers.get('location'):
                    raise NetworkError('Redirect limit reached or redirect destination missing.')
                url = urljoin(url, headers['location'])
                continue
            return FetchResult(status, url, body, truncated)
    except NetworkError:
        raise
    except (OSError, ValueError, http.client.HTTPException):
        raise NetworkError('Network request failed or timed out.') from None
    raise NetworkError('Request could not be completed.')


def check_url(url: str) -> dict:
    try:
        validate_url(url)
    except NetworkError as error:
        return {'state': 'blocked', 'status': None, 'detail': str(error), 'verified': False}
    try:
        result = safe_get(url, max_bytes=4096)
        state = 'healthy' if 200 <= result.status < 300 else 'broken' if result.status in (404, 410) else 'uncertain'
        return {'state': state, 'status': result.status, 'final_url': result.url,
                'detail': 'HTTP response observed; page meaning and anchors were not verified.', 'verified': True}
    except NetworkError as error:
        return {'state': 'uncertain', 'status': None, 'detail': str(error), 'verified': False}


class SerpApiSearch:
    """Google Search results; key stays in memory and is excluded from repr/logs."""
    def __init__(self, key: str, fetch=safe_get, max_searches: int = 8):
        if not isinstance(key, str) or not key.strip() or len(key) > 512 or any(c.isspace() for c in key):
            raise ValueError('A valid existing SerpApi key is required.')
        self._key = key
        self._fetch = fetch
        self._cache = {}
        self.max_searches = max_searches
        self.search_calls = 0
        self._lock = threading.Lock()

    def search(self, query: str) -> list[dict]:
        if not isinstance(query, str) or not query.strip() or len(query) > 500:
            raise NetworkError('Search query must contain 1–500 characters.')
        with self._lock:
            if query in self._cache:
                return [dict(row) for row in self._cache[query]]
            if self.search_calls >= self.max_searches:
                raise NetworkError('This process reached its eight-search budget. Restart only when you intend to use more credits.')
            self.search_calls += 1
            params = urlencode({'engine': 'google', 'q': query, 'api_key': self._key, 'hl': 'en', 'gl': 'in'})
            try:
                result = self._fetch('https://serpapi.com/search.json?' + params, timeout=10, max_bytes=262_144, max_redirects=0)
                if result.status != 200 or result.truncated:
                    raise NetworkError('Search service did not return a complete successful response.')
                data = json.loads(result.body)
                if not isinstance(data, dict) or data.get('error'):
                    raise NetworkError('Search service returned an error. Check your account and remaining credits.')
                rows = data.get('organic_results', [])
                if not isinstance(rows, list):
                    raise NetworkError('Search service returned an unexpected response format.')
                output = []
                seen = set()
                for row in rows:
                    if not isinstance(row, dict) or not isinstance(row.get('link'), str):
                        continue
                    try:
                        validate_url(row['link'])
                    except NetworkError:
                        continue
                    if row['link'] in seen:
                        continue
                    seen.add(row['link'])
                    output.append({'title': str(row.get('title', 'Untitled result'))[:240],
                                   'link': row['link'], 'snippet': str(row.get('snippet', ''))[:600]})
                    if len(output) == 5:
                        break
                self._cache[query] = output
                return [dict(row) for row in output]
            except NetworkError:
                raise
            except Exception:
                raise NetworkError('Search request failed. Check connectivity and your existing key.') from None

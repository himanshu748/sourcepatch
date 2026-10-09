"""Generate the authored demo narration with Deepgram; no stored/logged key.

Run from an interactive terminal. Output WAVs and sanitized receipts are local.
No fallback voice, automatic retries, purchases, or credential creation.
"""
import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
import warnings
import wave

ROOT = Path(__file__).resolve().parent.parent
URL = 'https://api.deepgram.com/v1/speak?model=aura-2-thalia-en&encoding=linear16&container=wav&sample_rate=24000'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.media-work/deepgram')
    args = parser.parse_args()
    segments = json.loads((ROOT / 'docs/evidence/v2/live-narration.json').read_text())
    if len(segments) != 6 or sum(len(s['text']) for s in segments) > 3000:
        raise ValueError('Narration must have six segments and at most 3000 characters.')
    if not sys.stdin.isatty():
        raise ValueError('Use an interactive terminal for hidden key entry.')
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        key = getpass.getpass('Existing Deepgram API key (hidden, not saved): ').strip()
    if not key or any(c.isspace() for c in key):
        raise ValueError('Invalid key input.')
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = {'provider': 'Deepgram', 'model': 'aura-2-thalia-en',
               'generated_at': datetime.now(timezone.utc).isoformat(), 'segments': []}
    for i, segment in enumerate(segments):
        path = args.output / f'voice-{i}.wav'
        if path.exists():
            raise ValueError('Output already exists; choose a new directory to avoid overwriting or duplicate requests.')
        payload = json.dumps({'text': segment['text']}).encode()
        request = urllib.request.Request(URL, data=payload, method='POST', headers={
            'Authorization': 'Token ' + key, 'Content-Type': 'application/json', 'User-Agent': 'SourcePatch-Demo/2.0'})
        with urllib.request.urlopen(request, timeout=45) as response:
            audio = response.read(5_000_001)
            if response.status != 200 or len(audio) > 5_000_000 or audio[:4] != b'RIFF':
                raise ValueError('Expected bounded WAV response.')
            request_id = response.headers.get('dg-request-id')
        path.write_bytes(audio)
        with wave.open(str(path)) as wav:
            # Streaming WAV headers may advertise an unknown frame count.
            # Measure the bounded decoded payload rather than trusting that sentinel.
            frame_bytes = wav.getsampwidth() * wav.getnchannels()
            pcm = wav.readframes(5_000_000 // frame_bytes)
            duration = len(pcm) / frame_bytes / wav.getframerate()
        receipt['segments'].append({'index': i, 'characters': len(segment['text']),
            'text_sha256': hashlib.sha256(segment['text'].encode()).hexdigest(),
            'audio_sha256': hashlib.sha256(audio).hexdigest(), 'duration_seconds': duration,
            'request_id': request_id, 'status': 200})
        (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(f'Deepgram segment {i + 1}/6 generated ({duration:.2f}s).', flush=True)
    del key
    print(f'Audio and sanitized receipt saved in {args.output}.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Stopped. No automatic retry.', file=sys.stderr)
        sys.exit(1)
    except Exception:
        print('Deepgram generation stopped safely. Check your existing key, allowance, connection and output directory. No key/error payload printed; no fallback voice or automatic retry.', file=sys.stderr)
        sys.exit(1)

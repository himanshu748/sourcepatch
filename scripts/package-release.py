"""Package tracked/public source files; never copy ignored credentials or Git state."""
import hashlib
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent.parent
names = sorted(set(subprocess.check_output(
    ['git', 'ls-files', '-co', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')) - {''})
target = ROOT / 'landing/downloads/sourcepatch-v2.zip'
target.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name in names:
        if name.startswith('landing/') or name == 'SHA256SUMS.txt':
            continue
        path = ROOT / name
        if path.is_file() and not path.is_symlink():
            info = zipfile.ZipInfo('sourcepatch-v2/' + name, date_time=(2026, 10, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
# Include the newly generated download even on the first run.
names = sorted(set(names) | {'landing/downloads/sourcepatch-v2.zip'})
lines = []
for name in names:
    path = ROOT / name
    if name != 'SHA256SUMS.txt' and path.is_file() and not path.is_symlink():
        lines.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}')
(ROOT / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n')
print(f'Packaged {target.stat().st_size} bytes; {len(lines)} manifest entries.')

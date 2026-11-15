"""Harness init checks.

base:    run on the UNMOUNTED licensed image. Every modified path must match the base sha256
         in the overlay manifest and every newly added path must be absent, so a wrong base
         image fails before any overlay is used.
overlay: run with the overlay mounted. Every path must equal its overlay sha256.

Usage: verify_overlay.py base|overlay <manifest> <app-root>"""

import hashlib
import json
import sys
from pathlib import Path

mode = sys.argv[1]
manifest = json.loads(Path(sys.argv[2]).read_text())
root = Path(sys.argv[3])
bad = []
for e in manifest['files']:
    p = root / e['path']
    if mode == 'overlay':
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != e['overlay_sha256']:
            bad.append(f'{e["path"]}: mounted file differs from overlay')
    elif e['base_sha256'] is None:
        if p.exists():
            bad.append(f'{e["path"]}: expected absent (new file) but present')
    elif not p.is_file():
        bad.append(f'{e["path"]}: missing in image')
    elif hashlib.sha256(p.read_bytes()).hexdigest() != e['base_sha256']:
        bad.append(f'{e["path"]}: sha256 differs from base {manifest["base_commit"]}')
if bad:
    print(f'OVERLAY {mode.upper()} MISMATCH - refusing to start:', *bad, sep='\n  ')
    sys.exit(1)
print(f'overlay {mode} verified: {len(manifest["files"])} paths vs {manifest["base_commit"]}')

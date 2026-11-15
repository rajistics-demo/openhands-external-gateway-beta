"""Bake-time overlay installer. Runs once, at image build, against the official
pinned base image's own /app tree. No runtime ConfigMap/overlay mount is used.

Guards (both required, in order):
  1. "base"    - every path the overlay will touch must already match its reviewed
                 base sha256 (or, for a brand-new path, must not yet exist). This
                 fails the build immediately if the wrong base image was pulled.
  2. "overlay" - after copying, every path must match its reviewed overlay sha256
                 exactly. This fails the build if a copy went to the wrong place
                 or picked up the wrong file.

Usage: install_overlay.py <manifest.json> <overlay-dir> <app-root>
"""

import hashlib
import json
import shutil
import sys
from pathlib import Path

# Must match the official image's own convention (containers/app/Dockerfile:
# `chown -R openhands:openhands /app && chmod -R 770 /app`). Applied per-path below
# instead of as a second `-R` pass over the whole (already-correctly-owned) /app tree,
# which measured ~231s on a reviewed build and touches nothing this installer didn't
# itself create or write.
_OWNER_USER = 'openhands'
_OWNER_GROUP = 'openhands'
_OWNER_MODE = 0o770


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def own(path: Path) -> None:
    try:
        shutil.chown(path, user=_OWNER_USER, group=_OWNER_GROUP)
        path.chmod(_OWNER_MODE)
    except (LookupError, PermissionError) as e:
        # LookupError: the 'openhands' user/group doesn't exist in this environment
        # (e.g. running install_overlay.py's guard logic directly on a dev host to
        # test the manifest, outside the real build). PermissionError: not root.
        # Either way this is a real Docker build running as root against the
        # official base image, so fail loudly there instead of silently shipping
        # wrong ownership; only warn when it looks like an out-of-container test run.
        print(f'warning: could not set ownership/mode on {path}: {e}', file=sys.stderr)


def guard(mode: str, manifest: dict, root: Path) -> None:
    bad = []
    for e in manifest['files']:
        p = root / e['path']
        if mode == 'overlay':
            if not p.is_file() or sha256(p) != e['overlay_sha256']:
                bad.append(f'{e["path"]}: does not match reviewed overlay hash')
        elif e['base_sha256'] is None:
            if p.exists():
                bad.append(f'{e["path"]}: expected absent (new file) but present')
        elif not p.is_file():
            bad.append(f'{e["path"]}: missing from base image')
        elif sha256(p) != e['base_sha256']:
            bad.append(
                f'{e["path"]}: sha256 differs from reviewed base '
                f'{manifest["base_commit"]}'
            )
    if bad:
        print(f'OVERLAY {mode.upper()} MISMATCH - refusing to build:', *bad, sep='\n  ')
        sys.exit(1)
    print(f'overlay {mode} verified: {len(manifest["files"])} paths')


def main(manifest_path: Path, overlay_dir: Path, app_root: Path) -> None:
    manifest = json.loads(manifest_path.read_text())
    guard('base', manifest, app_root)
    new_dirs: set[Path] = set()
    for e in manifest['files']:
        src = overlay_dir / e['key']
        dst = app_root / e['path']
        parent = dst.parent
        # Only directories this installer itself creates get re-owned below; any
        # directory that already existed in the base image keeps its base ownership
        # untouched, exactly like the file-level overlay/base guards above.
        existing = parent
        created = []
        while not existing.exists():
            created.append(existing)
            existing = existing.parent
        parent.mkdir(parents=True, exist_ok=True)
        new_dirs.update(created)
        shutil.copyfile(src, dst)
        own(dst)
    for d in sorted(new_dirs, key=lambda p: len(p.parts)):
        own(d)
    guard('overlay', manifest, app_root)


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))

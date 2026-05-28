"""Scope SVG element IDs per-file to prevent cross-document collisions.

Each SVG in Assets/SVG gets all its local IDs prefixed with the basename
(e.g. AR.svg -> ids become "AR_linearGradient-1", "AR_FlagBackground", ...).
References inside url(#...), href="#...", and xlink:href="#..." are
updated to match.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SVG_DIR = Path(__file__).resolve().parent.parent / "Assets" / "SVG"

ID_ATTR_RE = re.compile(r'\bid="([^"]+)"')
URL_REF_RE = re.compile(r'url\(#([^)]+)\)')
HREF_REF_RE = re.compile(r'\b(?:xlink:href|href)="#([^"]+)"')


def scope_file(path: Path) -> tuple[int, int]:
    """Return (ids_renamed, refs_rewritten)."""
    prefix = path.stem + "_"
    text = path.read_text(encoding="utf-8")

    ids = set(ID_ATTR_RE.findall(text))
    if not ids:
        return (0, 0)

    # Skip if every id is already prefixed (idempotent re-run).
    if all(i.startswith(prefix) for i in ids):
        return (0, 0)

    refs_rewritten = 0

    def rename_id(match: re.Match[str]) -> str:
        return f'id="{prefix}{match.group(1)}"'

    def rename_url(match: re.Match[str]) -> str:
        nonlocal refs_rewritten
        target = match.group(1)
        if target in ids:
            refs_rewritten += 1
            return f'url(#{prefix}{target})'
        return match.group(0)

    def rename_href(match: re.Match[str]) -> str:
        nonlocal refs_rewritten
        target = match.group(1)
        if target in ids:
            refs_rewritten += 1
            # Reconstruct preserving xlink:href vs href.
            attr = match.group(0).split('=')[0]
            return f'{attr}="#{prefix}{target}"'
        return match.group(0)

    new_text = ID_ATTR_RE.sub(rename_id, text)
    new_text = URL_REF_RE.sub(rename_url, new_text)
    new_text = HREF_REF_RE.sub(rename_href, new_text)

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")

    return (len(ids), refs_rewritten)


def main() -> int:
    if not SVG_DIR.is_dir():
        print(f"SVG dir not found: {SVG_DIR}", file=sys.stderr)
        return 1
    files = sorted(SVG_DIR.glob("*.svg"))
    total_ids = total_refs = touched = 0
    for f in files:
        ids, refs = scope_file(f)
        if ids:
            touched += 1
            total_ids += ids
            total_refs += refs
    print(f"Scoped {touched}/{len(files)} files; renamed {total_ids} ids, rewrote {total_refs} refs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

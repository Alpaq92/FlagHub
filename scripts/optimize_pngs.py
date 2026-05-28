"""Losslessly compress every PNG in the repo with oxipng level 6.

Touches:
  - Assets/PNG/*.png
  - Sources/FlagKit/FlagKit.xcassets/**/*.png
  - header.png

oxipng is a pure-Rust reimplementation of OptiPNG; level 6 (max) is
slower than the default but produces the smallest lossless output.
The optimization is idempotent: running again on an already-optimised
PNG either yields zero change or a tiny further saving.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import oxipng
except ImportError:
    print("oxipng (pyoxipng) is not installed. Run: pip install pyoxipng", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

TARGETS: list[Path] = []
TARGETS.extend(sorted((ROOT / "Assets" / "PNG").glob("*.png")))
TARGETS.extend(sorted((ROOT / "Sources" / "FlagKit" / "FlagKit.xcassets").rglob("*.png")))
header = ROOT / "header.png"
if header.exists():
    TARGETS.append(header)


def main() -> int:
    total_before = total_after = 0
    touched = 0
    for path in TARGETS:
        before = path.stat().st_size
        try:
            oxipng.optimize(str(path), level=6)
        except Exception as exc:
            print(f"skip {path.name}: {exc}", file=sys.stderr)
            continue
        after = path.stat().st_size
        total_before += before
        total_after += after
        if after < before:
            touched += 1
    pct = (1 - total_after / total_before) * 100 if total_before else 0
    print(f"Optimised {touched}/{len(TARGETS)} PNGs.")
    print(f"Total: {total_before/1024:.1f} KiB -> {total_after/1024:.1f} KiB "
          f"(saved {(total_before-total_after)/1024:.1f} KiB, {pct:.1f}%).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

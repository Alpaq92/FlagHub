"""Prepend a standard attribution/license comment to each flag SVG.

Format inserted directly after the <?xml ... ?> declaration:

    <!--
      Flag: AR - Argentina
      Source: FlagKit by Bowtie (https://github.com/madebybowtie/FlagKit)
      License: MIT
    -->

Country names are read from Assets/Flags.md. Idempotent: re-running
detects the marker token and leaves files untouched.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG_DIR = ROOT / "Assets" / "SVG"
FLAGS_MD = ROOT / "Assets" / "Flags.md"

MARKER = "Source: FlagHub"

ROW_RE = re.compile(r"\|\s*<img[^>]+>\s*\|\s*([A-Z]{2,3})\s*\|\s*([^|\n]+)")
XML_DECL_RE = re.compile(r'(<\?xml[^?]*\?>)\s*\n')


def load_names() -> dict[str, str]:
    text = FLAGS_MD.read_text(encoding="utf-8")
    names: dict[str, str] = {}
    for m in ROW_RE.finditer(text):
        code, name = m.group(1), m.group(2).strip()
        names[code] = name
    return names


def attribution_block(code: str, name: str | None) -> str:
    display = f"{code} - {name}" if name else code
    return (
        "<!--\n"
        f"  Flag: {display}\n"
        f"  {MARKER} (fork of FlagKit by Bowtie)\n"
        "  Upstream: https://github.com/madebybowtie/FlagKit\n"
        "  License: MIT\n"
        "-->\n"
    )


def process_file(path: Path, names: dict[str, str]) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    code = path.stem
    block = attribution_block(code, names.get(code))
    new_text, n = XML_DECL_RE.subn(lambda m: m.group(1) + "\n" + block, text, count=1)
    if n == 0:
        new_text = block + text
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    if not SVG_DIR.is_dir():
        print(f"SVG dir not found: {SVG_DIR}", file=sys.stderr)
        return 1
    names = load_names()
    files = sorted(SVG_DIR.glob("*.svg"))
    touched = 0
    missing_names: list[str] = []
    for f in files:
        if process_file(f, names):
            touched += 1
        if f.stem not in names:
            missing_names.append(f.stem)
    print(f"Annotated {touched}/{len(files)} SVGs.")
    if missing_names:
        print(f"Note: no display name found in Flags.md for: {', '.join(missing_names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

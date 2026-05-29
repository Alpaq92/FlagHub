"""
Port the five missing flags (AQ, BQ, DG, EH, IC) from
murgupluoglu/flagkit-android (MIT) into FlagHub.

Pipeline per code:

  1. Read scripts/vd_src/<code>_flag.xml (Android VectorDrawable XML).
  2. Convert to SVG (paths, groups, clip-paths, fill rules, alpha,
     stroke attrs, group transforms — all the attributes the five
     source files actually use).
  3. Prepend FlagHub's standard MIT attribution comment, noting the
     glyph origin as flagkit-android.
  4. Write to Assets/SVG/<CODE>.svg.
  5. Rasterise to Assets/PNG/<CODE>.png (21x15), <CODE>@2x.png (42x30),
     <CODE>@3x.png (63x45) via PyMuPDF (fitz).
  6. Copy the rasters into Sources/FlagHub/FlagHub.xcassets/
     <CODE>.imageset/, write a Contents.json that matches the
     existing imageset schema.

Then patches Sources/FlagHub/FlagCodes.swift to insert the new codes
into supportedCountryCodes (alphabetic position), and Assets/Flags.md
to add the country-name rows.

Run: `python scripts/port_flags_from_android.py`
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
VD_SRC = ROOT / "scripts" / "vd_src"
SVG_DIR = ROOT / "Assets" / "SVG"
PNG_DIR = ROOT / "Assets" / "PNG"
XCASSETS = ROOT / "Sources" / "FlagHub" / "FlagHub.xcassets"

ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
AAPT_NS = "{http://schemas.android.com/aapt}"

# Code -> human-readable country name (for the SVG attribution comment
# and Flags.md). All five are non-sovereign territories.
COUNTRY_NAMES = {
    "AQ": "Antarctica",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "DG": "Diego Garcia (BIOT)",
    "EH": "Western Sahara",
    "IC": "Canary Islands",
}

# Standard attribution header, mirroring the format used by
# scripts/add_svg_attribution.py.
ATTRIBUTION = """<?xml version="1.0" encoding="UTF-8"?>
<!--
  Flag: {code} - {name}
  Source: FlagHub (fork of FlagKit by Bowtie)
  Upstream: https://github.com/madebybowtie/FlagKit
  Glyph: ported from murgupluoglu/flagkit-android
         (MIT, https://github.com/murgupluoglu/flagkit-android)
  License: MIT
-->
"""


# --------------------------------------------------------------------------
# VectorDrawable -> SVG
# --------------------------------------------------------------------------

def _strip_dp(value: str) -> str:
    """'21dp' -> '21'.  Pass numeric values through unchanged."""
    return value[:-2] if value.endswith("dp") else value


def _path_attrs(elem: ET.Element) -> dict[str, str]:
    """Translate android:* attrs on a <path> element into SVG attrs."""
    out: dict[str, str] = {}
    d = elem.get(ANDROID_NS + "pathData")
    if d:
        out["d"] = d
    fill = elem.get(ANDROID_NS + "fillColor")
    out["fill"] = fill if fill else "none"
    fill_type = elem.get(ANDROID_NS + "fillType")
    if fill_type and fill_type.lower() == "evenodd":
        out["fill-rule"] = "evenodd"
    fill_alpha = elem.get(ANDROID_NS + "fillAlpha")
    if fill_alpha:
        out["fill-opacity"] = fill_alpha
    stroke = elem.get(ANDROID_NS + "strokeColor")
    if stroke and stroke.lower() != "#00000000":
        out["stroke"] = stroke
        sw = elem.get(ANDROID_NS + "strokeWidth")
        if sw:
            out["stroke-width"] = sw
        sa = elem.get(ANDROID_NS + "strokeAlpha")
        if sa:
            out["stroke-opacity"] = sa
        for vd_attr, svg_attr in (("strokeLineCap", "stroke-linecap"),
                                  ("strokeLineJoin", "stroke-linejoin"),
                                  ("strokeMiterLimit", "stroke-miterlimit")):
            v = elem.get(ANDROID_NS + vd_attr)
            if v:
                out[svg_attr] = v
    return out


def _group_transform(elem: ET.Element) -> str | None:
    """Build an SVG transform= string from a <group>'s android:* attrs.
    VectorDrawable applies transforms in this order: translate, then
    rotate (around pivot), then scale (around pivot). We emit them
    in that visual order."""
    tx = elem.get(ANDROID_NS + "translateX")
    ty = elem.get(ANDROID_NS + "translateY")
    rot = elem.get(ANDROID_NS + "rotation")
    sx = elem.get(ANDROID_NS + "scaleX")
    sy = elem.get(ANDROID_NS + "scaleY")
    px = elem.get(ANDROID_NS + "pivotX") or "0"
    py = elem.get(ANDROID_NS + "pivotY") or "0"
    parts = []
    if tx or ty:
        parts.append(f"translate({tx or '0'} {ty or '0'})")
    if rot:
        parts.append(f"rotate({rot} {px} {py})")
    if sx or sy:
        parts.append(f"translate({px} {py}) scale({sx or '1'} {sy or '1'}) translate(-{px} -{py})")
    return " ".join(parts) if parts else None


def _emit_path(attrs: dict[str, str]) -> str:
    """Render an SVG <path> element from translated attributes."""
    if "d" not in attrs:
        return ""
    parts = [f'  <path d="{attrs["d"]}"']
    for k in ("fill", "fill-rule", "fill-opacity",
              "stroke", "stroke-width", "stroke-opacity",
              "stroke-linecap", "stroke-linejoin", "stroke-miterlimit"):
        if k in attrs:
            parts.append(f'{k}="{attrs[k]}"')
    parts.append("/>")
    return " ".join(parts) + "\n"


def _walk(elem: ET.Element, clip_counter: list[int], out: list[str]) -> None:
    """Recursively translate a VectorDrawable subtree to SVG fragments.

    Side-effect: appends SVG strings to `out`. `clip_counter` is a
    1-element list used as a mutable counter for unique clipPath ids."""
    for child in elem:
        tag = child.tag.split("}")[-1]
        if tag == "group":
            transform = _group_transform(child)
            # Hoist any clip-path defs at this level into <defs> via
            # an inline <clipPath> reference applied to the group.
            clip_ids: list[str] = []
            for sub in list(child):
                if sub.tag.split("}")[-1] == "clip-path":
                    d = sub.get(ANDROID_NS + "pathData")
                    if d:
                        clip_counter[0] += 1
                        cid = f"clip{clip_counter[0]}"
                        out.append(
                            f'  <defs><clipPath id="{cid}"><path d="{d}"/></clipPath></defs>\n'
                        )
                        clip_ids.append(cid)
            g_open = "  <g"
            if transform:
                g_open += f' transform="{transform}"'
            if clip_ids:
                # SVG only supports one clip-path per element; for
                # multiple, nest. None of the five sources need that.
                g_open += f' clip-path="url(#{clip_ids[0]})"'
            g_open += ">\n"
            out.append(g_open)
            _walk(child, clip_counter, out)
            out.append("  </g>\n")
        elif tag == "path":
            out.append(_emit_path(_path_attrs(child)))
        elif tag == "clip-path":
            # Top-level clip-path (rare) — apply to wrapper group at end.
            pass


def convert_vd_to_svg(code: str, xml_text: str) -> str:
    """Convert a VectorDrawable XML string to an SVG string."""
    root = ET.fromstring(xml_text)
    vw = _strip_dp(root.get(ANDROID_NS + "viewportWidth") or "21")
    vh = _strip_dp(root.get(ANDROID_NS + "viewportHeight") or "15")
    body: list[str] = []
    _walk(root, [0], body)

    attribution = ATTRIBUTION.format(code=code, name=COUNTRY_NAMES[code])
    return (
        attribution
        + f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{vw}" height="{vh}" viewBox="0 0 {vw} {vh}">\n'
        + "".join(body)
        + "</svg>\n"
    )


# --------------------------------------------------------------------------
# SVG -> PNG (1x, 2x, 3x)
# --------------------------------------------------------------------------

def rasterise(svg_text: str, base_w: int, base_h: int) -> dict[int, Image.Image]:
    """Render the SVG via fitz at 1x/2x/3x and return PIL Images."""
    out: dict[int, Image.Image] = {}
    # fitz wants bytes; render at 3x then downsample for 2x and 1x
    # to keep AA consistent across scales.
    doc = fitz.open(stream=svg_text.encode("utf-8"), filetype="svg")
    page = doc[0]
    # Render at exactly 3x scale relative to the viewBox units. The
    # viewBox is base_w x base_h, so 3x pixmap is 3*base_w x 3*base_h.
    zoom = 3.0
    pix = page.get_pixmap(
        matrix=fitz.Matrix(zoom * base_w / page.rect.width,
                           zoom * base_h / page.rect.height),
        alpha=True,
    )
    big = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    # If fitz off-by-one, snap.
    target3 = (base_w * 3, base_h * 3)
    if big.size != target3:
        big = big.resize(target3, Image.LANCZOS)
    out[3] = big
    out[2] = big.resize((base_w * 2, base_h * 2), Image.LANCZOS)
    out[1] = big.resize((base_w, base_h), Image.LANCZOS)
    return out


# --------------------------------------------------------------------------
# xcassets imageset
# --------------------------------------------------------------------------

CONTENTS_JSON_TEMPLATE = {
    "images": [
        {"idiom": "universal", "scale": "1x"},
        {"filename": "{code}@2x.png", "idiom": "universal", "scale": "2x"},
        {"filename": "{code}@3x.png", "idiom": "universal", "scale": "3x"},
    ],
    "info": {"author": "xcode", "version": 1},
}


def write_imageset(code: str, rasters: dict[int, Image.Image]) -> None:
    imgset = XCASSETS / f"{code}.imageset"
    imgset.mkdir(parents=True, exist_ok=True)
    # The @1x is NOT included as a file (matching JP / US / others — only @2x and @3x have filenames).
    rasters[2].save(imgset / f"{code}@2x.png", optimize=True)
    rasters[3].save(imgset / f"{code}@3x.png", optimize=True)
    contents = json.loads(json.dumps(CONTENTS_JSON_TEMPLATE).replace("{code}", code))
    with open(imgset / "Contents.json", "w", encoding="utf-8") as f:
        json.dump(contents, f, indent=2)
        f.write("\n")


# --------------------------------------------------------------------------
# FlagCodes.swift patch
# --------------------------------------------------------------------------

def patch_flagcodes(codes: list[str]) -> None:
    """Insert new codes into the supportedCountryCodes array, keeping
    the array alphabetically sorted as it already is."""
    fc = ROOT / "Sources" / "FlagHub" / "FlagCodes.swift"
    text = fc.read_text(encoding="utf-8")
    # Capture every existing "AA" entry within the array literal.
    m = re.search(
        r'public static let supportedCountryCodes:\s*\[String\]\s*=\s*\[(.*?)\]',
        text, re.DOTALL,
    )
    if not m:
        raise RuntimeError("Could not locate supportedCountryCodes literal")
    body = m.group(1)
    existing = re.findall(r'"([^"]+)"', body)
    merged = sorted(set(existing) | set(codes))
    # Re-emit as 10-per-line, 4-space indent, preserving the style.
    lines = []
    for i in range(0, len(merged), 10):
        chunk = ", ".join(f'"{c}"' for c in merged[i:i + 10])
        lines.append("        " + chunk + ",")
    if lines:
        # last line shouldn't have trailing comma
        lines[-1] = lines[-1].rstrip(",")
    new_body = "\n" + "\n".join(lines) + "\n    "
    new_text = text[:m.start(1)] + new_body + text[m.end(1):]
    fc.write_text(new_text, encoding="utf-8")
    print(f"  FlagCodes.swift: total codes {len(merged)} (was {len(existing)})")


# --------------------------------------------------------------------------
# Flags.md patch (append rows in alphabetic position)
# --------------------------------------------------------------------------

def patch_flags_md(codes: list[str]) -> None:
    """Insert new rows in alphabetic position, matching the existing
    `<img src='PNG/<CODE>@2x.png?raw=true'…> | <CODE> | <Name>` format.
    Leaves the trailing WW row in place."""
    md = ROOT / "Assets" / "Flags.md"
    if not md.exists():
        print(f"  WARNING: {md} not found, skipping")
        return
    lines = md.read_text(encoding="utf-8").splitlines(keepends=True)
    code_re = re.compile(r">\s*\|\s*([A-Z]{2,4})\s*\|")
    for code in codes:
        if any(f"| {code} |" in ln and "<img" in ln for ln in lines):
            continue
        row = (
            f"| <img src='PNG/{code}@2x.png?raw=true' width='21' height='15'>"
            f" | {code} | {COUNTRY_NAMES[code]}\n"
        )
        inserted = False
        for i, ln in enumerate(lines):
            m = code_re.search(ln)
            if m and m.group(1) != "WW" and m.group(1) > code:
                lines.insert(i, row)
                inserted = True
                break
        if not inserted:
            for i, ln in enumerate(lines):
                if code_re.search(ln) and "WW" in ln:
                    lines.insert(i, row)
                    break
    md.write_text("".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    codes = sorted(COUNTRY_NAMES.keys())
    print(f"Porting {len(codes)} flags: {', '.join(codes)}")
    for code in codes:
        src = VD_SRC / f"{code.lower()}_flag.xml"
        if not src.exists():
            print(f"  {code}: source missing at {src}", file=sys.stderr)
            continue
        xml_text = src.read_text(encoding="utf-8")
        svg_text = convert_vd_to_svg(code, xml_text)
        (SVG_DIR / f"{code}.svg").write_text(svg_text, encoding="utf-8")
        rasters = rasterise(svg_text, base_w=21, base_h=15)
        # Assets/PNG copies — match upstream's pattern of shipping
        # 1x/2x/3x.
        rasters[1].save(PNG_DIR / f"{code}.png", optimize=True)
        rasters[2].save(PNG_DIR / f"{code}@2x.png", optimize=True)
        rasters[3].save(PNG_DIR / f"{code}@3x.png", optimize=True)
        write_imageset(code, rasters)
        print(f"  {code}: svg + 1x/2x/3x rasters + imageset OK")

    print("Patching FlagCodes.swift…")
    patch_flagcodes(codes)
    print("Patching Assets/Flags.md…")
    patch_flags_md(codes)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

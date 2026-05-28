"""
Generate FlagHub's title banner (header.png at repo root).

Minimal pipeline: take the upstream `madebybowtie/FlagKit/Header.png`
(committed at scripts/header_source.png), wipe the FLAGKIT 2.0 text
band to transparent, and render "FlagHub 3.0" in its place. Nothing
else — dimensions, flag artwork, transparency, alignment all match
upstream.

Deps: Pillow, numpy. Fonts: Segoe UI Bold + Light (Windows defaults).

Run: `python scripts/generate_header.py`
"""

from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "header_source.png")
OUT = os.path.normpath(os.path.join(HERE, "..", "header.png"))

TEXT_COLOR = (15, 15, 15, 255)

BOLD_CANDIDATES = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
]
LIGHT_CANDIDATES = [
    r"C:\Windows\Fonts\segoeuil.ttf",
    r"C:\Windows\Fonts\ariali.ttf",
    r"C:\Windows\Fonts\calibril.ttf",
]


def load_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main() -> int:
    if not os.path.exists(SRC):
        print(f"Missing source image at {SRC}", file=sys.stderr)
        return 1

    src = Image.open(SRC).convert("RGBA")
    arr = np.array(src)
    H, W, _ = arr.shape
    print(f"upstream {W}x{H}")

    # ---- Locate text band: rows above the first all-transparent strip --
    opaque = arr[..., 3] > 0
    row_has = opaque.any(axis=1)
    text_end = None
    in_content = False
    for y, h_ in enumerate(row_has):
        if h_:
            in_content = True
        elif in_content:
            text_end = y
            break
    if text_end is None:
        print("Could not isolate text band", file=sys.stderr)
        return 1

    text_rows = opaque[:text_end]
    xs_t = np.where(text_rows.any(axis=0))[0]
    ys_t = np.where(text_rows.any(axis=1))[0]
    text_x0, text_x1 = int(xs_t.min()), int(xs_t.max())
    text_y0, text_y1 = int(ys_t.min()), int(ys_t.max())
    text_height = text_y1 - text_y0
    text_cx = (text_x0 + text_x1) // 2
    print(f"text band y={text_y0}-{text_y1} (h={text_height}), x={text_x0}-{text_x1}")

    # ---- Wipe old text pixels (alpha=0) --------------------------------
    arr[:text_end + 5, :, :] = 0
    img = Image.fromarray(arr, "RGBA")

    # ---- Render "FlagHub 3.0" centred on the old text band -------------
    font_px = int(text_height / 0.72)
    bold = load_font(BOLD_CANDIDATES, font_px)
    light = load_font(LIGHT_CANDIDATES, font_px)
    bold_text = "FlagHub"
    light_text = "3.0"
    inter_gap = int(font_px * 0.22)

    draw = ImageDraw.Draw(img)
    bb_b = draw.textbbox((0, 0), bold_text, font=bold)
    bb_l = draw.textbbox((0, 0), light_text, font=light)
    bw = bb_b[2] - bb_b[0]
    lw = bb_l[2] - bb_l[0]
    total_w = bw + inter_gap + lw

    baseline_y = text_y1 + 4
    start_x = text_cx - total_w // 2
    draw.text((start_x - bb_b[0], baseline_y - bb_b[3]),
              bold_text, font=bold, fill=TEXT_COLOR)
    draw.text((start_x + bw + inter_gap - bb_l[0], baseline_y - bb_l[3]),
              light_text, font=light, fill=TEXT_COLOR)

    # ---- Crop to content bbox with breathing-room margin ----------------
    # Re-detect the bbox now that the new text is in place; the rendered
    # "FlagHub 3.0" can have slightly different extents than the wiped
    # FLAGKIT 2.0, so we measure after, not before.
    final_arr = np.array(img)
    final_opaque = final_arr[..., 3] > 0
    ys2, xs2 = np.where(final_opaque)
    cy0, cy1 = int(ys2.min()), int(ys2.max())
    cx0, cx1 = int(xs2.min()), int(xs2.max())
    content_w = cx1 - cx0
    content_h = cy1 - cy0
    margin_x = int(content_w * 0.06)
    margin_y = int(content_h * 0.12)
    crop_box = (
        max(0, cx0 - margin_x), max(0, cy0 - margin_y),
        min(W, cx1 + margin_x + 1), min(H, cy1 + margin_y + 1),
    )
    img = img.crop(crop_box)
    print(f"cropped to {img.size[0]}x{img.size[1]} "
          f"(margin {margin_x}px x / {margin_y}px y)")

    img.save(OUT, optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

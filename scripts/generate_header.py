"""
Generate FlagHub's title banners (header-light.png + header-dark.png at repo root).

Minimal pipeline: take the upstream `madebybowtie/FlagKit/Header.png`
(committed at scripts/header_source.png), wipe the FLAGKIT 2.0 text
band to transparent, render "FlagHub 3.0" in two colour variants (one
for light-theme readers, one for dark-theme readers), crop to content
bbox + a small margin, save both.

The two variants share geometry exactly so a GitHub `<picture>` element
with `prefers-color-scheme` can swap one for the other without any
layout shift.

Text is positioned using PIL's `anchor="ls"` (left-baseline) so the
bold "FlagHub" and light "3.0" share a true baseline regardless of
which run has descenders.

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
OUT_LIGHT = os.path.normpath(os.path.join(HERE, "..", "header-light.png"))
OUT_DARK = os.path.normpath(os.path.join(HERE, "..", "header-dark.png"))

# Light-theme banner uses near-black; dark-theme uses near-white.
COLOR_LIGHT = (15, 15, 15, 255)
COLOR_DARK = (240, 240, 240, 255)

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


def render(src_arr, text_color):
    """Take a copy of the upstream array, swap the text, return cropped PIL."""
    arr = src_arr.copy()
    H, W, _ = arr.shape

    # Locate text band: rows above the first all-transparent strip.
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
        raise RuntimeError("Could not isolate text band")

    text_rows = opaque[:text_end]
    xs_t = np.where(text_rows.any(axis=0))[0]
    ys_t = np.where(text_rows.any(axis=1))[0]
    text_x0, text_x1 = int(xs_t.min()), int(xs_t.max())
    text_y0, text_y1 = int(ys_t.min()), int(ys_t.max())
    text_height = text_y1 - text_y0
    text_cx = (text_x0 + text_x1) // 2

    # Wipe the original text pixels to alpha=0.
    arr[:text_end + 5, :, :] = 0
    img = Image.fromarray(arr, "RGBA")

    # Render new text. Size font so the cap height matches the original
    # text band height (Segoe UI cap ≈ 0.72 of point size).
    font_px = int(text_height / 0.72)
    bold = load_font(BOLD_CANDIDATES, font_px)
    light = load_font(LIGHT_CANDIDATES, font_px)
    bold_text = "FlagHub"
    light_text = "3.0"
    inter_gap = int(font_px * 0.22)

    draw = ImageDraw.Draw(img)
    # Use anchor="ls" (left, baseline) so widths measure from the same
    # reference point as the placement we'll use below.
    bb_b = draw.textbbox((0, 0), bold_text, font=bold, anchor="ls")
    bb_l = draw.textbbox((0, 0), light_text, font=light, anchor="ls")
    bw = bb_b[2] - bb_b[0]
    lw = bb_l[2] - bb_l[0]
    total_w = bw + inter_gap + lw

    # The original text sat with its visual baseline near text_y1; nudge a
    # couple of pixels up so descenders don't quite touch the wipe edge.
    baseline_y = text_y1 - 2
    start_x = text_cx - total_w // 2

    draw.text((start_x, baseline_y), bold_text,
              font=bold, anchor="ls", fill=text_color)
    draw.text((start_x + bw + inter_gap, baseline_y), light_text,
              font=light, anchor="ls", fill=text_color)

    # Crop to content bbox + breathing-room margin.
    final = np.array(img)
    opaque_final = final[..., 3] > 0
    ys2, xs2 = np.where(opaque_final)
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
    return img.crop(crop_box), (text_y0, text_y1, text_x0, text_x1)


def main() -> int:
    if not os.path.exists(SRC):
        print(f"Missing source image at {SRC}", file=sys.stderr)
        return 1

    src = Image.open(SRC).convert("RGBA")
    src_arr = np.array(src)
    print(f"upstream {src.size[0]}x{src.size[1]}")

    for path, color, label in (
        (OUT_LIGHT, COLOR_LIGHT, "light-theme"),
        (OUT_DARK, COLOR_DARK, "dark-theme"),
    ):
        out_img, meta = render(src_arr, color)
        out_img.save(path, optimize=True)
        ty0, ty1, tx0, tx1 = meta
        print(f"  {label}: {out_img.size[0]}x{out_img.size[1]}, "
              f"text band y={ty0}-{ty1} x={tx0}-{tx1} -> {path} "
              f"({os.path.getsize(path)/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Generate FlagHub's liquid-glass globe icon (icon.png at repo root).

The icon is a translucent blue squircle in the iOS 26 "Liquid Glass"
style — vertical gradient body, glossy top sheen, edge refraction along
top-left, soft inner shadow at bottom-right — with the Lucide `earth`
glyph rendered in white over the top.

Rendered at 4x supersample (4096x4096) and downsampled with LANCZOS to
1024x1024 for clean anti-aliasing on the squircle and stroked paths.

Deps: Pillow, numpy, PyMuPDF (fitz). All present in the existing
scripts/ environment.

Run: `python scripts/generate_icon.py`
"""

from __future__ import annotations

import io
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

# ----- Output geometry ----------------------------------------------------
OUT_SIZE = 1024            # final icon edge, px
SUPERSAMPLE = 4
S = OUT_SIZE * SUPERSAMPLE  # 4096
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.normpath(os.path.join(HERE, "..", "icon.png"))

# ----- Liquid-glass palette -----------------------------------------------
GLASS_TOP = (130, 190, 255)     # bright cyan-blue
GLASS_BOT = (45, 95, 205)       # deep royal blue
GLASS_ALPHA = 240
SHEEN_ALPHA = 95                # top glossy highlight
EDGE_ALPHA = 200                # refractive top-left ring
INNER_SHADOW_ALPHA = 80         # bottom-right inner shadow
SHADOW_TINT = (0, 25, 70)
STROKE_ALPHA = 248              # globe lines

CORNER_RADIUS_FRAC = 0.22       # rounded-square ~ Apple icon

# ----- Lucide `earth` (https://lucide.dev/icons/earth) --------------------
# A four-stroke composition: outer circle plus three right-angle paths with
# 2-unit corner radii suggesting meridian/parallel intersections. White
# stroke renders cleanly over the blue glass; line-cap/join "round" keeps
# the corners soft to match the squircle.
LUCIDE_EARTH_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
     fill="none" stroke="white" stroke-width="2.2"
     stroke-linecap="round" stroke-linejoin="round">
  <path d="M21.54 15H17a2 2 0 0 0-2 2v4.54"/>
  <path d="M7 3.34V5a3 3 0 0 0 3 3a2 2 0 0 1 2 2c0 1.1.9 2 2 2a2 2 0 0 0 2-2c0-1.1.9-2 2-2h3.17"/>
  <path d="M11 21.95V18a2 2 0 0 0-2-2a2 2 0 0 1-2-2v-1a2 2 0 0 0-2-2H2.05"/>
  <circle cx="12" cy="12" r="10"/>
</svg>"""


# --------------------------------------------------------------------------
# Building blocks
# --------------------------------------------------------------------------

def squircle_mask(size: int, radius: int) -> Image.Image:
    """Return an L-mode mask filled with a rounded square (Apple-style)."""
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=radius, fill=255
    )
    return m


def vertical_gradient_rgba(size: int, top, bot, alpha: int) -> Image.Image:
    """Top→bottom linear gradient as an RGBA image (vectorised)."""
    ts = np.linspace(0.0, 1.0, size, dtype=np.float32).reshape(-1, 1)
    arr = np.empty((size, size, 4), dtype=np.uint8)
    arr[..., 0] = (top[0] * (1 - ts) + bot[0] * ts).astype(np.uint8)
    arr[..., 1] = (top[1] * (1 - ts) + bot[1] * ts).astype(np.uint8)
    arr[..., 2] = (top[2] * (1 - ts) + bot[2] * ts).astype(np.uint8)
    arr[..., 3] = alpha
    return Image.fromarray(arr, "RGBA")


def diagonal_falloff(size: int, *, from_top_left: bool) -> np.ndarray:
    """Return a [0,1] float32 falloff weight, brightest at one corner."""
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    t = (x + y) / (1.5 * size)
    return np.clip(1.0 - t, 0.0, 1.0) if from_top_left else np.clip(t, 0.0, 1.0)


def render_lucide_earth(target_size: int) -> Image.Image:
    """Rasterise the Lucide earth SVG to a transparent RGBA at target_size."""
    try:
        import fitz  # PyMuPDF
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("PyMuPDF (fitz) required for SVG rendering") from e

    doc = fitz.open(stream=LUCIDE_EARTH_SVG.encode("utf-8"), filetype="svg")
    page = doc[0]
    zoom = target_size / max(page.rect.width, page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=True)
    img = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    # Snap to exact square in case fitz rounds down by one px
    if img.size != (target_size, target_size):
        img = img.resize((target_size, target_size), Image.LANCZOS)
    return img


# --------------------------------------------------------------------------
# Compositor
# --------------------------------------------------------------------------

def build_icon() -> Image.Image:
    radius = int(S * CORNER_RADIUS_FRAC)
    outer_mask = squircle_mask(S, radius)

    # 1. Glass body — blue vertical gradient inside the squircle.
    base = Image.new("RGBA", (S, S), 0)
    base.paste(vertical_gradient_rgba(S, GLASS_TOP, GLASS_BOT, GLASS_ALPHA),
               (0, 0), outer_mask)

    # 2. Top sheen — a soft vertical white→transparent ramp confined to the
    # upper third. Pure gradient (no blurred ellipse) avoids the V-shaped
    # valley you get when a blurred shape's boundary clips against the
    # squircle's curve.
    ramp = np.zeros((S, S, 4), dtype=np.uint8)
    ramp[..., :3] = 255
    ys = np.arange(S, dtype=np.float32)
    # Smooth ease-out from 1 at y=0 to 0 around y = 0.45*S, gentle past that.
    t = np.clip(ys / (S * 0.45), 0.0, 1.0)
    eased = (1.0 - t) ** 2  # quadratic ease-out
    ramp[..., 3] = (eased * SHEEN_ALPHA).astype(np.uint8)[:, None]
    sheen = Image.fromarray(ramp, "RGBA")
    sheen_masked = Image.new("RGBA", (S, S), 0)
    sheen_masked.paste(sheen, (0, 0), outer_mask)
    base = Image.alpha_composite(base, sheen_masked)

    # 2b. Meniscus arc — a thin, bright curve hugging the inside of the
    # top edge, the way light catches the lip of a glass dome. Drawn as
    # an arc, blurred just enough to be soft but not blobby.
    arc = Image.new("RGBA", (S, S), 0)
    arc_pad = int(S * 0.08)
    arc_top = int(S * 0.04)
    arc_bot = int(S * 0.36)
    ImageDraw.Draw(arc).arc(
        (arc_pad, arc_top, S - arc_pad, arc_bot),
        start=200, end=340,
        fill=(255, 255, 255, 115),
        width=int(S * 0.005),
    )
    arc = arc.filter(ImageFilter.GaussianBlur(radius=S // 170))
    arc_masked = Image.new("RGBA", (S, S), 0)
    arc_masked.paste(arc, (0, 0), outer_mask)
    base = Image.alpha_composite(base, arc_masked)

    # 3. Edge refraction — bright ring along the top-left edge.
    inner_radius_edge = max(2, radius - int(S * 0.022))
    inner_mask_edge = squircle_mask(S, inner_radius_edge)
    edge_ring = ImageChops.subtract(outer_mask, inner_mask_edge)
    falloff_tl = diagonal_falloff(S, from_top_left=True)
    edge_arr = np.array(edge_ring, dtype=np.float32) / 255.0
    edge_alpha = (edge_arr * falloff_tl * EDGE_ALPHA).clip(0, 255).astype(np.uint8)
    edge_layer = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    edge_out = Image.new("RGBA", (S, S), 0)
    edge_out.paste(edge_layer, (0, 0), Image.fromarray(edge_alpha, "L"))
    edge_out = edge_out.filter(ImageFilter.GaussianBlur(radius=max(1, S // 500)))
    base = Image.alpha_composite(base, edge_out)

    # 4. Inner shadow — darker ring at the bottom-right edge.
    inner_radius_sh = max(2, radius - int(S * 0.018))
    inner_mask_sh = squircle_mask(S, inner_radius_sh)
    shadow_ring = ImageChops.subtract(outer_mask, inner_mask_sh)
    falloff_br = diagonal_falloff(S, from_top_left=False)
    shadow_arr = np.array(shadow_ring, dtype=np.float32) / 255.0
    shadow_alpha = (shadow_arr * falloff_br * INNER_SHADOW_ALPHA).clip(0, 255).astype(np.uint8)
    shadow_layer = Image.new("RGBA", (S, S), (*SHADOW_TINT, 255))
    shadow_out = Image.new("RGBA", (S, S), 0)
    shadow_out.paste(shadow_layer, (0, 0), Image.fromarray(shadow_alpha, "L"))
    shadow_out = shadow_out.filter(ImageFilter.GaussianBlur(radius=max(1, S // 350)))
    base = Image.alpha_composite(base, shadow_out)

    # 5. Lucide earth glyph — soft glow underlayer + crisp white strokes.
    glyph_size = int(S * 0.62)
    glyph = render_lucide_earth(glyph_size)
    gx = (S - glyph_size) // 2
    gy = (S - glyph_size) // 2

    # Subtle outer glow so the glyph reads against the lighter sheen.
    glow = glyph.filter(ImageFilter.GaussianBlur(radius=S // 80))
    glow_canvas = Image.new("RGBA", (S, S), 0)
    glow_canvas.paste(glow, (gx, gy), glow)
    base = Image.alpha_composite(base, glow_canvas)

    glyph_canvas = Image.new("RGBA", (S, S), 0)
    glyph_canvas.paste(glyph, (gx, gy), glyph)
    # Boost stroke alpha for crisper read at small sizes.
    if STROKE_ALPHA < 255:
        r, g, b, a = glyph_canvas.split()
        a = a.point(lambda v: int(v * STROKE_ALPHA / 255))
        glyph_canvas = Image.merge("RGBA", (r, g, b, a))
    base = Image.alpha_composite(base, glyph_canvas)

    return base


def main() -> int:
    print(f"Rendering at {S}x{S}, downscaling to {OUT_SIZE}x{OUT_SIZE}…")
    big = build_icon()
    final = big.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
    final.save(OUT_PATH, optimize=True)
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"Wrote {OUT_PATH} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

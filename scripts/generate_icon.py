"""
Generate FlagHub's globe icon (icon.png at repo root).

Visual: a white round plate with a soft vertical gradient (white at top,
faint cool grey at bottom) and a subtle inner shadow at the bottom edge,
overlaid with the royal-blue wireframe globe glyph from icones.pro
(scripts/globe_source.png — licensed for use per icones.pro/en/icon-license/).

Rendered at 4x supersample (4096x4096) and downsampled with LANCZOS to
1024x1024 for clean anti-aliasing.

Deps: Pillow, numpy.

Run: `python scripts/generate_icon.py`
"""

from __future__ import annotations

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
GLOBE_SRC = os.path.join(HERE, "globe_source.png")

# ----- Plate palette (white → faint cool grey gradient) -------------------
PLATE_TOP = (255, 255, 255)
PLATE_BOT = (228, 234, 242)
PLATE_ALPHA = 255
ARC_ALPHA = 70                  # very subtle meniscus arc
EDGE_ALPHA = 120                # gentle refractive top-left ring
INNER_SHADOW_ALPHA = 65         # soft bottom-right inner shadow
SHADOW_TINT = (60, 80, 110)

# Plate radius (fraction of canvas) and globe size (fraction of plate).
PLATE_RADIUS_FRAC = 0.49
GLOBE_SIZE_FRAC = 0.78          # globe glyph occupies 78% of plate diameter


# --------------------------------------------------------------------------
# Building blocks
# --------------------------------------------------------------------------

def circle_mask(size: int, radius: int) -> Image.Image:
    """Centred filled circle as an L-mode mask."""
    m = Image.new("L", (size, size), 0)
    cx = cy = size // 2
    ImageDraw.Draw(m).ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius), fill=255
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


def load_globe(target_size: int) -> Image.Image:
    """Load the icones.pro wireframe globe PNG, resized to target_size."""
    if not os.path.exists(GLOBE_SRC):
        raise RuntimeError(
            f"Missing globe source PNG at {GLOBE_SRC}. "
            "Re-fetch from https://icones.pro/en/blue-globe-icon-png-symbol/"
        )
    img = Image.open(GLOBE_SRC).convert("RGBA")
    if img.size != (target_size, target_size):
        img = img.resize((target_size, target_size), Image.LANCZOS)
    return img


# --------------------------------------------------------------------------
# Compositor
# --------------------------------------------------------------------------

def build_icon() -> Image.Image:
    plate_radius = int(S * PLATE_RADIUS_FRAC)
    plate_mask = circle_mask(S, plate_radius)

    # 1. Plate body — white → faint cool grey vertical gradient inside disc.
    base = Image.new("RGBA", (S, S), 0)
    base.paste(
        vertical_gradient_rgba(S, PLATE_TOP, PLATE_BOT, PLATE_ALPHA),
        (0, 0), plate_mask,
    )

    # 2. Meniscus arc — very faint bright curve along the top edge.
    arc = Image.new("RGBA", (S, S), 0)
    cx = cy = S // 2
    arc_r = int(plate_radius * 0.92)
    ImageDraw.Draw(arc).arc(
        (cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r),
        start=205, end=335,
        fill=(255, 255, 255, ARC_ALPHA),
        width=int(S * 0.004),
    )
    arc = arc.filter(ImageFilter.GaussianBlur(radius=S // 180))
    arc_masked = Image.new("RGBA", (S, S), 0)
    arc_masked.paste(arc, (0, 0), plate_mask)
    base = Image.alpha_composite(base, arc_masked)

    # 3. Edge refraction — gentle bright ring along the top-left edge.
    inner_r_edge = max(2, plate_radius - int(S * 0.018))
    inner_mask_edge = circle_mask(S, inner_r_edge)
    edge_ring = ImageChops.subtract(plate_mask, inner_mask_edge)
    falloff_tl = diagonal_falloff(S, from_top_left=True)
    edge_arr = np.array(edge_ring, dtype=np.float32) / 255.0
    edge_alpha = (edge_arr * falloff_tl * EDGE_ALPHA).clip(0, 255).astype(np.uint8)
    edge_layer = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    edge_out = Image.new("RGBA", (S, S), 0)
    edge_out.paste(edge_layer, (0, 0), Image.fromarray(edge_alpha, "L"))
    edge_out = edge_out.filter(ImageFilter.GaussianBlur(radius=max(1, S // 500)))
    base = Image.alpha_composite(base, edge_out)

    # 4. Inner shadow — soft darker ring at the bottom-right edge giving
    # the plate volume without being heavy.
    inner_r_sh = max(2, plate_radius - int(S * 0.016))
    inner_mask_sh = circle_mask(S, inner_r_sh)
    shadow_ring = ImageChops.subtract(plate_mask, inner_mask_sh)
    falloff_br = diagonal_falloff(S, from_top_left=False)
    shadow_arr = np.array(shadow_ring, dtype=np.float32) / 255.0
    shadow_alpha = (shadow_arr * falloff_br * INNER_SHADOW_ALPHA).clip(0, 255).astype(np.uint8)
    shadow_layer = Image.new("RGBA", (S, S), (*SHADOW_TINT, 255))
    shadow_out = Image.new("RGBA", (S, S), 0)
    shadow_out.paste(shadow_layer, (0, 0), Image.fromarray(shadow_alpha, "L"))
    shadow_out = shadow_out.filter(ImageFilter.GaussianBlur(radius=max(1, S // 350)))
    base = Image.alpha_composite(base, shadow_out)

    # 5. Globe glyph with depth treatment so it doesn't read as a flat
    # sticker against the glossy plate:
    #   a) a soft dark drop-shadow behind the glyph (offset down-right)
    #      makes it appear to float above the plate;
    #   b) the wireframe strokes are recoloured with a vertical blue
    #      gradient (brighter royal blue at top, deeper navy at bottom)
    #      to imply light falling on a sphere.
    glyph_size = int(plate_radius * 2 * GLOBE_SIZE_FRAC)
    glyph = load_globe(glyph_size)
    gx = (S - glyph_size) // 2
    gy = (S - glyph_size) // 2
    _, _, _, glyph_alpha = glyph.split()

    # 5a. Drop shadow. CRITICAL: paste the source onto the full S×S
    # canvas *before* blurring, otherwise the gaussian gets clipped by
    # the glyph_size bounding box and leaves visible rectangular edges
    # around the shadow.
    shadow_color = (15, 30, 75)
    shadow_fill = Image.new("RGBA", (glyph_size, glyph_size), (*shadow_color, 255))
    shadow_src = Image.new("RGBA", (glyph_size, glyph_size), 0)
    shadow_src.paste(shadow_fill, (0, 0), glyph_alpha)
    sh_arr = np.array(shadow_src)
    sh_arr[:, :, 3] = (sh_arr[:, :, 3].astype(np.float32) * 0.45).astype(np.uint8)
    shadow_src = Image.fromarray(sh_arr, "RGBA")

    shadow_canvas = Image.new("RGBA", (S, S), 0)
    shadow_canvas.paste(
        shadow_src,
        (gx + int(S * 0.004), gy + int(S * 0.012)),
        shadow_src,
    )
    shadow_canvas = shadow_canvas.filter(
        ImageFilter.GaussianBlur(radius=glyph_size // 22)
    )
    base = Image.alpha_composite(base, shadow_canvas)

    # 5b. Recolour the wireframe with a vertical gradient.
    GLOBE_TOP = (52, 70, 245)       # bright royal blue
    GLOBE_BOT = (10, 18, 130)       # deep navy
    grad = vertical_gradient_rgba(glyph_size, GLOBE_TOP, GLOBE_BOT, 255)
    recoloured = Image.new("RGBA", (glyph_size, glyph_size), 0)
    recoloured.paste(grad, (0, 0), glyph_alpha)

    glyph_canvas = Image.new("RGBA", (S, S), 0)
    glyph_canvas.paste(recoloured, (gx, gy), recoloured)
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

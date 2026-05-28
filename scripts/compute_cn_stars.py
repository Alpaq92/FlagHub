"""Compute spec-correct star polygon points for the CN flag.

Per the official 1949 construction sheet, the canton is a 15x10 grid:
  - big star: center (5,5), outer radius 3
  - small stars: centers (10,2), (12,4), (12,7), (10,9); outer radius 1
  - each small star is rotated so that one of its five outer points
    aims at the centre of the big star (5,5)

FlagKit uses a 21x15 canvas. The official 30x20 canton maps to the
upper-left 10.5x7.5 of the flag (scale 0.7 per unit). Print the polygon
'points' attribute for each star at FlagKit scale.
"""

import math

SCALE = 0.7  # flag units per canton grid unit
BIG_CENTER_GRID = (5, 5)
BIG_R_GRID = 3
SMALL_R_GRID = 1
SMALL_CENTERS_GRID = [(10, 2), (12, 4), (12, 7), (10, 9)]

# Inner radius for a regular 5-point star
INNER_RATIO = math.sin(math.radians(18)) / math.sin(math.radians(54))


def star_points(cx: float, cy: float, outer_r: float, rotation_deg: float = 0.0) -> str:
    """Return space-separated 'x y x y ...' for a 5-point star.

    rotation_deg = 0 means one outer point straight up.
    Angles increase clockwise (matches SVG y-down convention).
    """
    inner_r = outer_r * INNER_RATIO
    pts = []
    for i in range(10):
        # alternate outer / inner, starting with outer at the top
        r = outer_r if i % 2 == 0 else inner_r
        angle_deg = rotation_deg + i * 36
        rad = math.radians(angle_deg)
        x = cx + r * math.sin(rad)
        y = cy - r * math.cos(rad)
        pts.append(f"{x:.4f},{y:.4f}")
    return " ".join(pts)


def angle_to(cx: float, cy: float, tx: float, ty: float) -> float:
    """Bearing in degrees (0 = up, clockwise) from (cx,cy) to (tx,ty)."""
    dx = tx - cx
    dy = ty - cy
    # SVG y-down: 'up' direction has dy<0. angle = atan2(dx, -dy) gives clockwise from up.
    return math.degrees(math.atan2(dx, -dy))


def main() -> None:
    # Big star: scaled coords, no rotation
    bcx_grid, bcy_grid = BIG_CENTER_GRID
    bcx, bcy = bcx_grid * SCALE, bcy_grid * SCALE
    big_r = BIG_R_GRID * SCALE
    print("Big star center (flag coords):", (round(bcx, 3), round(bcy, 3)),
          "outer R:", round(big_r, 3))
    print("  points:", star_points(bcx, bcy, big_r))
    print()

    for i, (gx, gy) in enumerate(SMALL_CENTERS_GRID, start=1):
        scx, scy = gx * SCALE, gy * SCALE
        small_r = SMALL_R_GRID * SCALE
        # Rotate small star so one outer point aims at big star center.
        rot = angle_to(scx, scy, bcx, bcy)
        print(f"Small star {i} center:", (round(scx, 3), round(scy, 3)),
              "rotation:", round(rot, 3))
        print("  points:", star_points(scx, scy, small_r, rot))
        print()


if __name__ == "__main__":
    main()

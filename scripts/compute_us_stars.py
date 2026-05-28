"""Generate the 50 stars for the US canton at FlagKit's 21x15 scale.

Layout: 9 rows in the 9 wide x 8.0769 (= 15*7/13) tall canton.
  - rows 1, 3, 5, 7, 9: 6 stars each (30 total)
  - rows 2, 4, 6, 8: 5 stars each, offset by half a column (20 total)

Star outer radius ~ 0.36 to keep clear gaps in the 1.5 x 0.897 cell.
"""

import math

CANTON_W = 9.0
CANTON_H = 15.0 * 7 / 13  # 8.07692...
STAR_R = 0.36
INNER_RATIO = math.sin(math.radians(18)) / math.sin(math.radians(54))


def star_points(cx: float, cy: float, outer_r: float) -> str:
    inner_r = outer_r * INNER_RATIO
    pts = []
    for i in range(10):
        r = outer_r if i % 2 == 0 else inner_r
        rad = math.radians(i * 36)
        x = cx + r * math.sin(rad)
        y = cy - r * math.cos(rad)
        pts.append(f"{x:.4f},{y:.4f}")
    return " ".join(pts)


def main() -> None:
    cell_w = CANTON_W / 6
    cell_h = CANTON_H / 9
    polygons: list[str] = []
    for row in range(9):
        cy = (row + 0.5) * cell_h
        if row % 2 == 0:  # rows 0,2,4,6,8 -> 6 stars
            xs = [(col + 0.5) * cell_w for col in range(6)]
        else:             # rows 1,3,5,7 -> 5 stars offset by half a cell
            xs = [(col + 1.0) * cell_w for col in range(5)]
        for cx in xs:
            pts = star_points(cx, cy, STAR_R)
            polygons.append(f'<polygon points="{pts}"></polygon>')
    print(f"<!-- {len(polygons)} stars -->")
    for p in polygons:
        print("            " + p)


if __name__ == "__main__":
    main()

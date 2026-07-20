"""Odd-r staggered hex grid: coordinates, neighbors, and cell centers.

Layout (PRD v1.1 §7.2, §7.6):

- Rows are indexed r = 0 (top / anchor row) downward; columns c = 0 from the left.
- Each row has a stagger bit s in {0, 1}. s == 0 rows hold `width` cells;
  s == 1 rows are shifted right by half a cell diameter and hold `width - 1`
  cells. Adjacent rows always have opposite stagger.
- The board carries a `parity` bit: stagger(r) = (r + parity) & 1. Anchor-row
  insertion prepends a row at r = 0 and flips parity, so every existing row
  keeps its physical stagger (and therefore its width) as its index shifts
  down by one — this is the "stable cell identity across row insertion" rule.

Geometry (Q16.16, egg diameter D = FP_ONE = 1.0):

- center_x(r, c) = (2c + 1 + s) * D/2
- center_y(r)    = D/2 + r * ROW_H, with ROW_H = 56756 ~= sqrt(3)/2.
"""

from .fixedpoint import FP_ONE, FP_HALF

ROW_H = 56756  # floor(sqrt(3)/2 * 65536): vertical distance between row centers


def stagger(r, parity):
    return (r + parity) & 1


def row_width(width, s):
    return width if s == 0 else width - 1


def in_row(width, r, c, parity):
    return r >= 0 and 0 <= c < row_width(width, stagger(r, parity))


def center(r, c, parity):
    s = stagger(r, parity)
    x = (2 * c + 1 + s) * FP_HALF
    y = FP_HALF + r * ROW_H
    return x, y


def neighbors(width, r, c, parity):
    """The (up to 6) valid neighbor cells of (r, c), in fixed deterministic order:
    same-row left, same-row right, up-left, up-right, down-left, down-right."""
    s = stagger(r, parity)
    if s == 0:
        candidates = [
            (r, c - 1), (r, c + 1),
            (r - 1, c - 1), (r - 1, c),
            (r + 1, c - 1), (r + 1, c),
        ]
    else:
        candidates = [
            (r, c - 1), (r, c + 1),
            (r - 1, c), (r - 1, c + 1),
            (r + 1, c), (r + 1, c + 1),
        ]
    return [(nr, nc) for nr, nc in candidates if in_row(width, nr, nc, parity)]

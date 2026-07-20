"""Shot resolution: fixed-point ray march, wall reflection, contact, snapping.

All geometry is Q16.16 with egg diameter D = 1.0 (FP_ONE). The playfield is
`width` cell-diameters wide; side walls sit at x = 0 and x = width. The moving
egg is its center point; walls reflect the center at radius distance R = D/2.

Contact rule (PRD v1.1 §7.3 "consistent collision tolerance"): the moving egg
contacts the nest when its center comes within CONTACT = 0.85 * D of any
occupied cell center (squared-distance comparison, no square roots on the
contact path). The march step is D/8, small enough that a contact within
0.85 * D can never be tunneled past.

Snap rule (PRD v1.1 §7.3 "predictable snapping"): on contact (or on reaching
the ceiling band y <= D/2), the egg attaches to the candidate cell
(board.candidate_cells) whose center has the smallest squared distance to the
egg's stopped center; ties break on (row, col) ascending. Candidate cells are
by construction empty and connected, so overlaps and floating attachments are
impossible.
"""

from .fixedpoint import FP_ONE, FP_HALF, fp_mul, fp_div, fp_sqrt
from . import hexgrid

STEP = FP_ONE // 8          # march step: D/8
CONTACT = 55705             # floor(0.85 * 65536)
CONTACT_SQ = fp_mul(CONTACT, CONTACT)
MAX_STEPS = 8192            # hard bound; unreachable in legal play
MAX_BOUNCES_SCORED = 2      # bank bonus caps at two wall bounces


class ShotError(ValueError):
    pass


def resolve_shot(board, origin_x, origin_y, dx, dy):
    """March the shot from (origin_x, origin_y) along (dx, dy) until contact
    or ceiling. Returns ((row, col) snap cell, bounce_count).

    dy must be negative (upward). Raises ShotError for invalid aim.
    """
    if dy >= 0:
        raise ShotError("aim vector must point upward (dy < 0)")
    length = fp_sqrt(fp_mul(dx, dx) + fp_mul(dy, dy))
    if length == 0:
        raise ShotError("aim vector must be non-zero")
    ux = fp_div(fp_mul(dx, STEP), length)
    uy = fp_div(fp_mul(dy, STEP), length)

    min_x = FP_HALF
    max_x = board.width * FP_ONE - FP_HALF
    occupied = [(cell, hexgrid.center(cell[0], cell[1], board.parity))
                for cell in board.occupied()]

    x, y = origin_x, origin_y
    bounces = 0
    for _ in range(MAX_STEPS):
        x += ux
        y += uy
        if x < min_x:
            x = 2 * min_x - x
            ux = -ux
            bounces += 1
        elif x > max_x:
            x = 2 * max_x - x
            ux = -ux
            bounces += 1
        if y <= FP_HALF:
            return _snap(board, x, FP_HALF), bounces
        for _, (cx, cy) in occupied:
            ddx = x - cx
            ddy = y - cy
            if fp_mul(ddx, ddx) + fp_mul(ddy, ddy) < CONTACT_SQ:
                return _snap(board, x, y), bounces
    raise ShotError("shot did not resolve within MAX_STEPS")


def _snap(board, x, y):
    best_cell = None
    best_d2 = None
    for r, c in board.candidate_cells():
        cx, cy = hexgrid.center(r, c, board.parity)
        ddx = x - cx
        ddy = y - cy
        d2 = fp_mul(ddx, ddx) + fp_mul(ddy, ddy)
        if best_d2 is None or d2 < best_d2:
            best_d2 = d2
            best_cell = (r, c)
        # ties keep the earlier candidate: candidate_cells is (row, col) sorted
    if best_cell is None:
        raise ShotError("no attachment candidate available")
    return best_cell

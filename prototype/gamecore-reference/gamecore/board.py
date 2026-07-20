"""Board state: occupancy, matching, anchor connectivity, and row insertion.

Deterministic-order rules (PRD v1.1 §7.2 "Resolution order must be
deterministic"): every BFS iterates neighbors in the fixed order defined by
hexgrid.neighbors, and every returned cell collection is sorted by (row, col).
"""

from . import hexgrid

MATCH_THRESHOLD = 3


class Board:
    def __init__(self, width, rows=None, parity=0):
        if width < 2:
            raise ValueError("width must be >= 2")
        self.width = width
        self.parity = parity & 1
        # rows[r][c] is a color string or None. Row r's usable length is
        # row_width(width, stagger(r, parity)); storage is always `width` wide
        # with the trailing slot of staggered rows unused (kept None).
        self.rows = rows if rows is not None else []

    @classmethod
    def from_strings(cls, width, row_strings, parity=0):
        """Build a board from strings like 'RGB.Y' ('.' = empty). Staggered
        rows may be one character shorter."""
        board = cls(width, rows=[], parity=parity)
        for r, text in enumerate(row_strings):
            s = hexgrid.stagger(r, parity)
            usable = hexgrid.row_width(width, s)
            if len(text) > usable:
                raise ValueError(f"row {r} longer than usable width {usable}")
            row = [None] * width
            for c, ch in enumerate(text):
                if ch != ".":
                    row[c] = ch
            board.rows.append(row)
        return board

    # -- occupancy ---------------------------------------------------------

    def ensure_row(self, r):
        while len(self.rows) <= r:
            self.rows.append([None] * self.width)

    def get(self, r, c):
        if 0 <= r < len(self.rows) and hexgrid.in_row(self.width, r, c, self.parity):
            return self.rows[r][c]
        return None

    def set(self, r, c, color):
        if not hexgrid.in_row(self.width, r, c, self.parity):
            raise ValueError(f"cell ({r},{c}) invalid for this board")
        self.ensure_row(r)
        self.rows[r][c] = color

    def remove(self, cells):
        for r, c in cells:
            self.rows[r][c] = None

    def occupied(self):
        out = []
        for r, row in enumerate(self.rows):
            for c, color in enumerate(row):
                if color is not None:
                    out.append((r, c))
        return out  # naturally sorted by (row, col)

    def is_empty(self):
        return not self.occupied()

    def colors_present(self):
        return sorted({self.rows[r][c] for r, c in self.occupied()})

    # -- resolution --------------------------------------------------------

    def match_group(self, r, c):
        """Contiguous same-color group containing (r, c), sorted by (row, col).
        Caller removes it only if len >= MATCH_THRESHOLD."""
        color = self.get(r, c)
        if color is None:
            return []
        seen = {(r, c)}
        queue = [(r, c)]
        while queue:
            cr, cc = queue.pop(0)
            for nr, nc in hexgrid.neighbors(self.width, cr, cc, self.parity):
                if (nr, nc) not in seen and self.get(nr, nc) == color:
                    seen.add((nr, nc))
                    queue.append((nr, nc))
        return sorted(seen)

    def find_floating(self):
        """Occupied cells not connected (through occupancy) to the anchor row
        (r == 0), sorted by (row, col)."""
        anchored = set()
        queue = []
        for r, c in self.occupied():
            if r == 0:
                anchored.add((r, c))
                queue.append((r, c))
        while queue:
            cr, cc = queue.pop(0)
            for nr, nc in hexgrid.neighbors(self.width, cr, cc, self.parity):
                if (nr, nc) not in anchored and self.get(nr, nc) is not None:
                    anchored.add((nr, nc))
                    queue.append((nr, nc))
        return sorted(cell for cell in self.occupied() if cell not in anchored)

    # -- danger advancement (PRD v1.1 §7.6) --------------------------------

    def insert_top_row(self, colors, rng):
        """Prepend a full new anchor row; every existing row keeps its physical
        stagger because parity flips. New-row colors come from the seeded RNG
        in column order (a deterministic sequence consumption rule)."""
        self.parity ^= 1
        s = hexgrid.stagger(0, self.parity)
        usable = hexgrid.row_width(self.width, s)
        row = [None] * self.width
        for c in range(usable):
            row[c] = colors[rng.next_below(len(colors))]
        self.rows.insert(0, row)

    # -- attachment candidates ---------------------------------------------

    def candidate_cells(self):
        """Empty valid cells where a shot egg may legally attach: every empty
        anchor-row cell, plus every empty cell adjacent to an occupied cell
        (including the row just below the current bottom row). Sorted by
        (row, col). Guarantees connectivity and prevents overlaps/floaters."""
        candidates = set()
        s0 = hexgrid.stagger(0, self.parity)
        for c in range(hexgrid.row_width(self.width, s0)):
            if self.get(0, c) is None:
                candidates.add((0, c))
        for r, c in self.occupied():
            for nr, nc in hexgrid.neighbors(self.width, r, c, self.parity):
                if self.get(nr, nc) is None:
                    candidates.add((nr, nc))
        return sorted(candidates)

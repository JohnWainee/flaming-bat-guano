import unittest

from gamecore import hexgrid
from gamecore.fixedpoint import FP_HALF, FP_ONE


class TestHexGrid(unittest.TestCase):
    def test_stagger_and_width(self):
        self.assertEqual(hexgrid.stagger(0, 0), 0)
        self.assertEqual(hexgrid.stagger(1, 0), 1)
        self.assertEqual(hexgrid.stagger(0, 1), 1)
        self.assertEqual(hexgrid.row_width(8, 0), 8)
        self.assertEqual(hexgrid.row_width(8, 1), 7)

    def test_centers(self):
        # Unstaggered row 0, col 0: center (0.5, 0.5)
        self.assertEqual(hexgrid.center(0, 0, 0), (FP_HALF, FP_HALF))
        # Staggered row 1, col 0: shifted right half a cell
        x, y = hexgrid.center(1, 0, 0)
        self.assertEqual(x, FP_ONE)
        self.assertEqual(y, FP_HALF + hexgrid.ROW_H)

    def test_known_neighbors(self):
        # Unstaggered (2, 3) in width 8, parity 0: rows 1 and 3 are staggered.
        self.assertEqual(
            hexgrid.neighbors(8, 2, 3, 0),
            [(2, 2), (2, 4), (1, 2), (1, 3), (3, 2), (3, 3)],
        )
        # Staggered (1, 0): left same-row neighbor is off-board.
        self.assertEqual(
            hexgrid.neighbors(8, 1, 0, 0),
            [(1, 1), (0, 0), (0, 1), (2, 0), (2, 1)],
        )

    def test_neighbor_symmetry(self):
        width, parity = 8, 0
        for r in range(5):
            for c in range(hexgrid.row_width(width, hexgrid.stagger(r, parity))):
                for nr, nc in hexgrid.neighbors(width, r, c, parity):
                    self.assertIn(
                        (r, c), hexgrid.neighbors(width, nr, nc, parity),
                        f"asymmetric neighbors: ({r},{c}) <-> ({nr},{nc})",
                    )

    def test_neighbors_are_unit_distance(self):
        # Every neighbor pair's centers are exactly one diameter apart
        # (within fixed-point rounding of ROW_H).
        width, parity = 8, 1
        for r in range(4):
            for c in range(hexgrid.row_width(width, hexgrid.stagger(r, parity))):
                x, y = hexgrid.center(r, c, parity)
                for nr, nc in hexgrid.neighbors(width, r, c, parity):
                    nx, ny = hexgrid.center(nr, nc, parity)
                    dist2 = ((nx - x) ** 2 + (ny - y) ** 2) / FP_ONE ** 2
                    self.assertAlmostEqual(dist2, 1.0, places=3)


if __name__ == "__main__":
    unittest.main()

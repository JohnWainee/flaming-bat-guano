import unittest

from gamecore.board import Board
from gamecore.rng import Pcg32
from gamecore import hexgrid


class TestBoard(unittest.TestCase):
    def test_from_strings_and_get(self):
        b = Board.from_strings(4, ["RG.B", "GG."])
        self.assertEqual(b.get(0, 0), "R")
        self.assertIsNone(b.get(0, 2))
        self.assertEqual(b.get(1, 1), "G")
        self.assertIsNone(b.get(1, 3))  # staggered row: col 3 invalid
        with self.assertRaises(ValueError):
            Board.from_strings(4, ["RGBY", "RGBY"])  # staggered row too long

    def test_match_group(self):
        b = Board.from_strings(4, ["RG.B", "GG."])
        # G at (0,1) connects to (1,0) and (1,1): stagger row 1 neighbors of (0,1)
        self.assertEqual(b.match_group(0, 1), [(0, 1), (1, 0), (1, 1)])
        self.assertEqual(b.match_group(0, 0), [(0, 0)])
        self.assertEqual(b.match_group(0, 2), [])  # empty cell

    def test_find_floating(self):
        # (1,1) touches only empty anchor cells, so it and its dependent (2,1)
        # are both floating.
        b = Board.from_strings(4, ["R...", ".G.", ".Y.."])
        self.assertEqual(b.find_floating(), [(1, 1), (2, 1)])
        b2 = Board.from_strings(4, ["RR..", "RG.", ".Y.."])
        self.assertEqual(b2.find_floating(), [])

    def test_insert_top_row_preserves_stagger(self):
        b = Board.from_strings(4, ["RGBY", "RGB"])
        rng = Pcg32(1)
        b.insert_top_row(["R", "G"], rng)
        self.assertEqual(b.parity, 1)
        # Old row 0 (unstaggered, 4 cells) is now row 1 and must still be
        # unstaggered: stagger(1, parity=1) == 0.
        self.assertEqual(hexgrid.stagger(1, b.parity), 0)
        self.assertEqual(b.rows[1][:4], ["R", "G", "B", "Y"])
        # New top row is staggered (3 usable cells), fully populated.
        self.assertEqual(hexgrid.stagger(0, b.parity), 1)
        filled = [c for c in b.rows[0] if c is not None]
        self.assertEqual(len(filled), 3)
        self.assertTrue(all(c in ("R", "G") for c in filled))

    def test_candidate_cells(self):
        b = Board.from_strings(4, ["RG.."])
        cands = b.candidate_cells()
        # Empty anchor cells + empty neighbors of occupied cells.
        self.assertIn((0, 2), cands)
        self.assertIn((0, 3), cands)
        self.assertIn((1, 0), cands)  # below (0,0)/(0,1)
        self.assertNotIn((0, 0), cands)  # occupied
        self.assertEqual(cands, sorted(cands))
        # Candidates never overlap occupied cells
        occ = set(b.occupied())
        self.assertFalse(occ & set(cands))


if __name__ == "__main__":
    unittest.main()

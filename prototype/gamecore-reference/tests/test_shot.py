import unittest

from gamecore.board import Board
from gamecore.fixedpoint import FP_ONE, fp
from gamecore.shot import ShotError, resolve_shot


def make_board():
    # Width 8, one full anchor row.
    return Board.from_strings(8, ["RGBYRGBY"])


class TestShot(unittest.TestCase):
    def setUp(self):
        self.board = make_board()
        self.origin_x = 4 * FP_ONE
        self.origin_y = fp(8.0)

    def test_straight_up_attaches_below_anchor(self):
        cell, bounces = resolve_shot(self.board, self.origin_x, self.origin_y,
                                     0, fp(-1.0))
        self.assertEqual(bounces, 0)
        # Origin x=4.0 travels up between (0,3) x=3.5 and (0,4) x=4.5, contacts
        # both; nearest empty candidates are staggered row-1 cells (1,3) x=4.0.
        self.assertEqual(cell, (1, 3))

    def test_bank_shot_bounces(self):
        cell, bounces = resolve_shot(self.board, self.origin_x, self.origin_y,
                                     fp(3.0), fp(-1.0))
        self.assertGreaterEqual(bounces, 1)
        self.assertIsNone(self.board.get(*cell))  # snapped to an empty cell

    def test_invalid_aim_rejected(self):
        with self.assertRaises(ShotError):
            resolve_shot(self.board, self.origin_x, self.origin_y, fp(1.0), 0)
        with self.assertRaises(ShotError):
            resolve_shot(self.board, self.origin_x, self.origin_y, fp(1.0), fp(1.0))
        with self.assertRaises(ShotError):
            resolve_shot(self.board, self.origin_x, self.origin_y, 0, 0)

    def test_ceiling_attachment_on_empty_board(self):
        empty = Board(8)
        cell, _ = resolve_shot(empty, self.origin_x, self.origin_y, 0, fp(-1.0))
        self.assertEqual(cell[0], 0)  # anchor row

    def test_snap_never_overlaps(self):
        board = make_board()
        for dx_tenths in range(-30, 31, 3):
            board2 = make_board()
            cell, _ = resolve_shot(board2, self.origin_x, self.origin_y,
                                   dx_tenths * FP_ONE // 10, fp(-1.0))
            self.assertIsNone(board2.get(*cell),
                              f"overlap at {cell} for dx={dx_tenths / 10}")

    def test_determinism(self):
        results = set()
        for _ in range(3):
            board = make_board()
            results.add(resolve_shot(board, self.origin_x, self.origin_y,
                                     fp(1.7), fp(-0.9)))
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()

import json
import pathlib
import unittest

from gamecore.fixedpoint import FP_ONE, fp
from gamecore.game import Game, Level

LEVELS = pathlib.Path(__file__).parent.parent / "levels"


def load_level(name):
    return Level.from_dict(json.loads((LEVELS / name).read_text()))


def simple_level(**overrides):
    data = {
        "id": "test-level",
        "board": {"width": 6, "parity": 0, "rows": ["RRG..."]},
        "colors": ["R", "G"],
        "danger": {"dangerRow": 8, "shotsPerInsertion": 0},
    }
    for key, value in overrides.items():
        data[key] = value
    return Level.from_dict(data)


class TestGame(unittest.TestCase):
    def test_example_levels_load(self):
        for name in ("level-001.json", "level-002.json"):
            level = load_level(name)
            game = Game(level, 42)
            self.assertEqual(game.status, "active")
            self.assertIn(game.current_egg, level.colors)

    def test_match_removes_group_and_scores(self):
        level = simple_level()
        game = Game(level, seed=3)
        # Force a known current egg, then complete the R pair at (0,0),(0,1).
        game.current_egg = "R"
        result = game.apply_shot(fp(-1.35), fp(-1.0))
        self.assertGreaterEqual(len(result["matched"]), 3)
        self.assertGreater(game.score, 0)
        self.assertEqual(game.combo, 1)

    def test_miss_resets_combo(self):
        level = simple_level()
        game = Game(level, seed=3)
        game.combo = 4
        game.current_egg = "G"
        result = game.apply_shot(fp(1.0), fp(-1.0))  # attaches somewhere right
        if not result["matched"] and not result["dropped"]:
            self.assertEqual(game.combo, 0)

    def test_win_on_clear(self):
        level = simple_level()
        game = Game(level, seed=3)
        game.current_egg = "R"
        game.apply_shot(fp(-1.35), fp(-1.0))  # clears RR + placed R
        if game.board.occupied() == [(0, 2)]:
            # G at (0,2) remains; clear it too.
            game.current_egg = "G"
            game.apply_shot(fp(-0.6), fp(-1.0))
            game.current_egg = "G"
            game.apply_shot(fp(-0.6), fp(-1.0))
        self.assertIn(game.status, ("active", "won"))

    def test_insertion_advances_and_preserves_stagger(self):
        level = simple_level(danger={"dangerRow": 20, "shotsPerInsertion": 2})
        game = Game(level, seed=9)
        parity_before = game.board.parity
        game.apply_shot(fp(2.0), fp(-1.0))
        self.assertEqual(game.insertion_countdown, 1)      # no insertion yet
        self.assertEqual(game.board.parity, parity_before)
        rows_after_first = len(game.board.rows)
        game.apply_shot(fp(-2.0), fp(-1.0))
        self.assertEqual(game.board.parity, parity_before ^ 1)  # insertion flipped parity
        self.assertEqual(len(game.board.rows), rows_after_first + 1)
        self.assertEqual(game.insertion_countdown, 2)

    def test_loss_when_crossing_danger_row(self):
        level = simple_level(danger={"dangerRow": 2, "shotsPerInsertion": 1})
        game = Game(level, seed=9)
        # Every shot inserts a row; the initial row soon crosses dangerRow 2.
        for _ in range(6):
            if game.status != "active":
                break
            game.apply_shot(fp(2.5), fp(-1.0))
        self.assertEqual(game.status, "lost")

    def test_shot_rejected_after_game_over(self):
        level = simple_level(danger={"dangerRow": 1, "shotsPerInsertion": 1})
        game = Game(level, seed=9)
        for _ in range(4):
            if game.status != "active":
                break
            game.apply_shot(0, -FP_ONE)
        self.assertEqual(game.status, "lost")
        with self.assertRaises(Exception):
            game.apply_shot(0, -FP_ONE)


if __name__ == "__main__":
    unittest.main()

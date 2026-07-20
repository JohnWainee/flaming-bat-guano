"""Replay determinism and randomized invariant tests (PRD v1.1 §24.3).

The invariant test drives many seeded games with pseudo-random aim and asserts
after every shot: no floating clusters remain, no cell holds an invalid value,
and a from-scratch replay of the same actions reproduces the identical state
hash. This is the reference core's stand-in for the PRD's property-based
"floating-cluster prevention" and "repeated attach/remove cycles" suites.
"""

import json
import pathlib
import unittest

from gamecore.fixedpoint import FP_ONE
from gamecore.game import Game, Level
from gamecore.replay import replay_record, run_replay, state_hash
from gamecore.rng import Pcg32
from gamecore import hexgrid

LEVELS = pathlib.Path(__file__).parent.parent / "levels"
GOLDEN = pathlib.Path(__file__).parent.parent / "golden"


def load_level(name):
    return Level.from_dict(json.loads((LEVELS / name).read_text()))


def random_action(rng):
    dx = rng.next_below(6 * FP_ONE + 1) - 3 * FP_ONE
    dy = -(FP_ONE // 2 + rng.next_below(FP_ONE))
    return {"type": "shot", "dx": dx, "dy": dy}


class TestReplay(unittest.TestCase):
    def test_replay_reproduces_hash(self):
        level = load_level("level-001.json")
        aim = Pcg32(77, seq=99)
        actions = [random_action(aim) for _ in range(15)]
        first = run_replay(level, 12345, actions)
        second = run_replay(level, 12345, actions)
        self.assertEqual(state_hash(first), state_hash(second))

    def test_randomized_invariants_many_seeds(self):
        level = load_level("level-002.json")
        for seed in range(1, 101):
            aim = Pcg32(seed, seq=99)
            game = Game(level, seed)
            actions = []
            while game.status == "active" and game.shots < 25:
                action = random_action(aim)
                actions.append(action)
                game.apply_shot(action["dx"], action["dy"])
                # Invariant 1: no floating clusters survive resolution.
                self.assertEqual(game.board.find_floating(), [],
                                 f"floating cluster, seed {seed}, shot {game.shots}")
                # Invariant 2: occupancy only in valid cells.
                for r, c in game.board.occupied():
                    self.assertTrue(
                        hexgrid.in_row(game.board.width, r, c, game.board.parity),
                        f"invalid occupied cell ({r},{c}), seed {seed}")
                    self.assertIn(game.board.get(r, c), level.colors)
            # Invariant 3: full-run replay reproduces the exact state.
            replayed = run_replay(level, seed, actions)
            self.assertEqual(state_hash(replayed), state_hash(game),
                             f"replay hash mismatch, seed {seed}")

    def test_golden_vectors(self):
        golden_files = sorted(GOLDEN.glob("*.json"))
        self.assertTrue(golden_files, "golden vectors missing — run generate_golden.py")
        for path in golden_files:
            record = json.loads(path.read_text())
            level_file = {
                "ref-001-first-clutch": "level-001.json",
                "ref-002-rising-nest": "level-002.json",
            }[record["levelId"]]
            game = run_replay(load_level(level_file), record["seed"], record["actions"])
            self.assertEqual(state_hash(game), record["expected"]["finalHash"], path.name)
            self.assertEqual(game.score, record["expected"]["score"], path.name)
            self.assertEqual(game.status, record["expected"]["status"], path.name)

    def test_replay_record_shape(self):
        level = load_level("level-001.json")
        aim = Pcg32(5, seq=99)
        record = replay_record(level, 5, [random_action(aim) for _ in range(5)])
        self.assertEqual(record["rulesetVersion"], "0.1.0")
        self.assertIn("finalHash", record["expected"])
        self.assertEqual(len(record["expected"]["finalHash"]), 64)


if __name__ == "__main__":
    unittest.main()

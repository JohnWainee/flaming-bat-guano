import unittest

from gamecore.scoring import next_combo, shot_score


class TestScoring(unittest.TestCase):
    def test_non_scoring_shot(self):
        self.assertEqual(shot_score(0, 0, 0, combo=5), 0)
        self.assertEqual(shot_score(0, 0, 2, combo=5), 0)  # bank alone scores nothing

    def test_basic_match(self):
        self.assertEqual(shot_score(3, 0, 0, combo=0), 30)

    def test_drops_score_double(self):
        self.assertEqual(shot_score(3, 2, 0, combo=0), 70)

    def test_bank_multiplier_caps_at_three(self):
        self.assertEqual(shot_score(3, 0, 1, combo=0), 60)
        self.assertEqual(shot_score(3, 0, 2, combo=0), 90)
        self.assertEqual(shot_score(3, 0, 7, combo=0), 90)

    def test_combo_bonus_floor_division(self):
        # total = base * bank * (4 + combo) // 4
        self.assertEqual(shot_score(3, 0, 0, combo=1), 37)   # 30*5//4
        self.assertEqual(shot_score(3, 0, 0, combo=4), 60)   # 30*8//4
        self.assertEqual(shot_score(7, 1, 3, 1), (70 + 20) * 3 * 5 // 4)

    def test_next_combo(self):
        self.assertEqual(next_combo(0, True), 1)
        self.assertEqual(next_combo(3, True), 4)
        self.assertEqual(next_combo(3, False), 0)


if __name__ == "__main__":
    unittest.main()

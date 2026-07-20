import unittest

from gamecore.rng import Pcg32


class TestPcg32(unittest.TestCase):
    def test_reference_vectors_seed42_seq54(self):
        # First three values match the published PCG32 demo output for
        # srandom(42, 54): 0xa15c02b7, 0x7b47f409, 0xba1d3330 — external
        # confirmation the implementation is genuine PCG32. The rest are
        # port-oracle regression values.
        rng = Pcg32(42, seq=54)
        self.assertEqual(
            [rng.next_u32() for _ in range(6)],
            [2707161783, 2068313097, 3122475824, 2211639955, 3215226955, 3421331566],
        )

    def test_reference_vectors_seed2026_seq7(self):
        rng = Pcg32(2026, seq=7)
        self.assertEqual(
            [rng.next_u32() for _ in range(4)],
            [4207372542, 2322551327, 824720038, 942184700],
        )

    def test_same_seed_same_stream(self):
        a, b = Pcg32(9), Pcg32(9)
        self.assertEqual([a.next_u32() for _ in range(50)],
                         [b.next_u32() for _ in range(50)])

    def test_different_seeds_differ(self):
        a, b = Pcg32(1), Pcg32(2)
        self.assertNotEqual([a.next_u32() for _ in range(10)],
                            [b.next_u32() for _ in range(10)])

    def test_next_below(self):
        rng = Pcg32(5)
        for _ in range(100):
            self.assertIn(rng.next_below(4), range(4))
        with self.assertRaises(ValueError):
            rng.next_below(0)


if __name__ == "__main__":
    unittest.main()

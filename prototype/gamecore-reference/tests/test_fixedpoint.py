import unittest

from gamecore.fixedpoint import FP_ONE, fp, fp_div, fp_mul, fp_sqrt


class TestFixedPoint(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(FP_ONE, 65536)
        self.assertEqual(fp(1.0), 65536)
        self.assertEqual(fp(-0.5), -32768)

    def test_mul_floors_toward_negative_infinity(self):
        self.assertEqual(fp_mul(fp(2.0), fp(3.0)), fp(6.0))
        self.assertEqual(fp_mul(3, 3), 0)            # tiny positives floor to 0
        self.assertEqual(fp_mul(-1, 1), -1)          # arithmetic shift floors
        self.assertEqual(fp_mul(fp(-1.5), fp(2.0)), fp(-3.0))

    def test_div_floor_semantics(self):
        self.assertEqual(fp_div(fp(6.0), fp(3.0)), fp(2.0))
        self.assertEqual(fp_div(fp(1.0), fp(3.0)), 21845)      # floor(65536/3 * 65536 / 65536)
        self.assertEqual(fp_div(fp(-1.0), fp(3.0)), -21846)    # floors, not truncates

    def test_sqrt(self):
        self.assertEqual(fp_sqrt(fp(4.0)), fp(2.0))
        self.assertEqual(fp_sqrt(fp(2.0)), 92681)              # floor(sqrt(2) * 65536)
        self.assertEqual(fp_sqrt(0), 0)
        with self.assertRaises(ValueError):
            fp_sqrt(-1)


if __name__ == "__main__":
    unittest.main()

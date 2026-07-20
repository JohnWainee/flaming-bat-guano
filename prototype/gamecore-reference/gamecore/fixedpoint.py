"""Q16.16 fixed-point arithmetic — the bit-exact numeric spec for the Swift port.

All GameCore quantities (positions, direction vectors, distances) are Q16.16:
a signed integer whose value is `raw / 65536`. The Swift port must use Int64
and reproduce these exact semantics:

- fp_mul: (a * b) >> 16 with an ARITHMETIC right shift (floors toward -inf).
  Swift's `>>` on signed integers is arithmetic, matching Python.
- fp_div: floor((a << 16) / b). Python's `//` floors; Swift's `/` truncates
  toward zero, so the Swift port MUST implement floor division explicitly
  for negative operands.
- fp_sqrt: floor(sqrt(a << 16)) via exact integer isqrt (a >= 0).

Floats never appear on the gameplay path; `fp()` exists only for constants
and tests.
"""

import math

FP_SHIFT = 16
FP_ONE = 1 << FP_SHIFT  # 65536 == 1.0
FP_HALF = FP_ONE // 2


def fp(x):
    """Convert a float/int constant to Q16.16. Not for use in gameplay logic."""
    return int(round(x * FP_ONE))


def to_float(a):
    """For debugging/display only."""
    return a / FP_ONE


def fp_mul(a, b):
    return (a * b) >> FP_SHIFT


def fp_div(a, b):
    return (a << FP_SHIFT) // b


def fp_sqrt(a):
    if a < 0:
        raise ValueError("fp_sqrt of negative value")
    return math.isqrt(a << FP_SHIFT)

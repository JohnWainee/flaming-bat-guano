"""Seeded deterministic RNG: PCG32 (O'Neill), bit-exact reference for the Swift port.

State is 64-bit unsigned with wrapping arithmetic (Swift: UInt64 &* / &+).
Stream selection uses the standard PCG32 initseq scheme. `next_below` uses
plain modulo — the small bias is irrelevant for egg-color selection and keeps
the port trivial. Reference output vectors live in tests/test_rng.py; the
Swift implementation must reproduce them exactly.
"""

_MULT = 6364136223846793005
_MASK64 = (1 << 64) - 1

DEFAULT_SEQ = 54


class Pcg32:
    def __init__(self, seed, seq=DEFAULT_SEQ):
        self.inc = ((seq << 1) | 1) & _MASK64
        self.state = 0
        self.next_u32()
        self.state = (self.state + seed) & _MASK64
        self.next_u32()

    def next_u32(self):
        old = self.state
        self.state = (old * _MULT + self.inc) & _MASK64
        xorshifted = (((old >> 18) ^ old) >> 27) & 0xFFFFFFFF
        rot = old >> 59
        return ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & 0xFFFFFFFF

    def next_below(self, bound):
        if bound <= 0:
            raise ValueError("bound must be positive")
        return self.next_u32() % bound

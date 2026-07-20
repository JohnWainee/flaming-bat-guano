#!/usr/bin/env python3
"""Regenerate golden replay vectors (PRD v1.1 §24.3).

Fully deterministic: aim sequences are derived from a dedicated PCG32 stream
(seq 99), so running this script twice produces byte-identical files. The
future Swift GameCore must reproduce every `expected` block exactly.

Usage:  python3 generate_golden.py
"""

import json
import pathlib

from gamecore.fixedpoint import FP_ONE
from gamecore.game import Level
from gamecore.replay import replay_record
from gamecore.rng import Pcg32

HERE = pathlib.Path(__file__).parent
GOLDEN_DIR = HERE / "golden"
LEVELS_DIR = HERE / "levels"

AIM_STREAM_SEQ = 99
SHOTS_PER_RUN = 40
GAME_SEEDS = [1, 7, 12345, 99991, 2 ** 31 - 1]


def aim_sequence(seed, count):
    """Deterministic pseudo-random aim vectors: dx in [-3, 3], dy in [-1.5, -0.5]."""
    rng = Pcg32(seed, seq=AIM_STREAM_SEQ)
    actions = []
    for _ in range(count):
        dx = rng.next_below(6 * FP_ONE + 1) - 3 * FP_ONE
        dy = -(FP_ONE // 2 + rng.next_below(FP_ONE))
        actions.append({"type": "shot", "dx": dx, "dy": dy})
    return actions


def main():
    GOLDEN_DIR.mkdir(exist_ok=True)
    for level_path in sorted(LEVELS_DIR.glob("*.json")):
        level_data = json.loads(level_path.read_text())
        level = Level.from_dict(level_data)
        for seed in GAME_SEEDS:
            record = replay_record(level, seed, aim_sequence(seed, SHOTS_PER_RUN))
            # Trim unused trailing actions (run may end early) so vectors are minimal.
            record["actions"] = record["actions"][: record["expected"]["shots"]]
            out = GOLDEN_DIR / f"{level.level_id}-seed{seed}.json"
            out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
            print(f"{out.name}: shots={record['expected']['shots']} "
                  f"score={record['expected']['score']} "
                  f"status={record['expected']['status']}")


if __name__ == "__main__":
    main()

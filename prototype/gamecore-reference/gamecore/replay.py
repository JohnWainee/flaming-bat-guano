"""Deterministic replay: canonical state serialization, hashing, record/replay.

The state hash is sha256 over canonical JSON (sorted keys, no whitespace) of
the full logical state. Two runs of the same (level, seed, actions) must
produce identical hashes on any machine — this is the contract the Swift port
must satisfy against the golden vectors (PRD v1.1 §20.5, §24.3).
"""

import hashlib
import json

from .game import Game, RULESET_VERSION

REPLAY_SCHEMA_VERSION = 1


def canonical_state(game):
    return {
        "rulesetVersion": RULESET_VERSION,
        "levelId": game.level.level_id,
        "seed": game.seed,
        "shots": game.shots,
        "status": game.status,
        "score": game.score,
        "combo": game.combo,
        "parity": game.board.parity,
        "rows": game.board.rows,
        "insertionCountdown": game.insertion_countdown,
        "currentEgg": game.current_egg,
        "nextEgg": game.next_egg,
        "rngState": game.rng.state,
        "rngInc": game.rng.inc,
    }


def state_hash(game):
    blob = json.dumps(canonical_state(game), sort_keys=True,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def run_replay(level, seed, actions):
    """Run a recorded action list against a fresh game. Actions:
    {"type": "shot", "dx": <fp int>, "dy": <fp int>}. Stops early if the game
    ends. Returns the finished Game."""
    game = Game(level, seed)
    for action in actions:
        if game.status != "active":
            break
        if action["type"] != "shot":
            raise ValueError(f"unknown action type {action['type']!r}")
        game.apply_shot(action["dx"], action["dy"])
    return game


def replay_record(level, seed, actions):
    """Full replay record for persistence/golden vectors."""
    game = run_replay(level, seed, actions)
    return {
        "schemaVersion": REPLAY_SCHEMA_VERSION,
        "rulesetVersion": RULESET_VERSION,
        "levelId": level.level_id,
        "seed": seed,
        "actions": actions,
        "expected": {
            "finalHash": state_hash(game),
            "score": game.score,
            "shots": game.shots,
            "status": game.status,
        },
    }

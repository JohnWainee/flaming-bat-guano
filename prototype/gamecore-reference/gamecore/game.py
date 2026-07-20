"""Shot-indexed game loop (PRD v1.1 §6.2, §7.1): the only mutating entry point
is apply_shot; every state transition is a deterministic function of
(previous state, action, seed).

Per-shot resolution order (fixed, §7.2):
  1. Resolve trajectory → snap cell (shot.resolve_shot).
  2. Place the current egg.
  3. Match resolution: remove the placed egg's group if >= MATCH_THRESHOLD.
  4. Detachment: remove all floating clusters.
  5. Scoring + combo update (scoring.shot_score / next_combo).
  6. Win check: board empty → status 'won' (skips danger advancement).
  7. Danger advancement: decrement shots-until-insertion; at 0, insert a new
     anchor row (board.insert_top_row) and reset the counter.
  8. Loss check: any occupied cell with row >= danger_row → status 'lost'.
  9. Advance the egg queue from the seeded RNG; increment shot counter.
"""

from .board import Board, MATCH_THRESHOLD
from .fixedpoint import FP_ONE, FP_HALF
from .hexgrid import ROW_H
from .rng import Pcg32
from . import shot as shot_mod
from . import scoring

RULESET_VERSION = "0.1.0"


class Level:
    """Minimal level definition (docs/hatch-havoc/level-format.md)."""

    def __init__(self, level_id, width, rows, colors, danger_row,
                 shots_per_insertion, parity=0):
        self.level_id = level_id
        self.width = width
        self.rows = list(rows)
        self.colors = list(colors)
        self.danger_row = danger_row
        self.shots_per_insertion = shots_per_insertion  # 0 disables insertion
        self.parity = parity

    @classmethod
    def from_dict(cls, data):
        return cls(
            level_id=data["id"],
            width=data["board"]["width"],
            rows=data["board"]["rows"],
            colors=data["colors"],
            danger_row=data["danger"]["dangerRow"],
            shots_per_insertion=data["danger"]["shotsPerInsertion"],
            parity=data["board"].get("parity", 0),
        )


class Game:
    def __init__(self, level, seed):
        self.level = level
        self.seed = seed
        self.rng = Pcg32(seed)
        self.board = Board.from_strings(level.width, level.rows, parity=level.parity)
        self.score = 0
        self.combo = 0
        self.shots = 0
        self.status = "active"  # active | won | lost
        self.insertion_countdown = level.shots_per_insertion
        self.current_egg = self._draw_egg()
        self.next_egg = self._draw_egg()

    # Launcher sits centered, two rows below the danger boundary.
    @property
    def launcher_x(self):
        return self.level.width * FP_ONE // 2

    @property
    def launcher_y(self):
        return FP_HALF + (self.level.danger_row + 2) * ROW_H

    def _draw_egg(self):
        return self.level.colors[self.rng.next_below(len(self.level.colors))]

    def apply_shot(self, dx, dy):
        """Apply one shot action. Returns a result dict for presentation/replay."""
        if self.status != "active":
            raise shot_mod.ShotError(f"game is {self.status}")
        cell, bounces = shot_mod.resolve_shot(
            self.board, self.launcher_x, self.launcher_y, dx, dy)
        self.board.set(cell[0], cell[1], self.current_egg)

        group = self.board.match_group(cell[0], cell[1])
        matched = group if len(group) >= MATCH_THRESHOLD else []
        if matched:
            self.board.remove(matched)

        floating = self.board.find_floating()
        if floating:
            self.board.remove(floating)

        gained = scoring.shot_score(len(matched), len(floating), bounces, self.combo)
        scored = (len(matched) + len(floating)) > 0
        self.score += gained
        self.combo = scoring.next_combo(self.combo, scored)

        if self.board.is_empty():
            self.status = "won"
        else:
            if self.level.shots_per_insertion > 0:
                self.insertion_countdown -= 1
                if self.insertion_countdown == 0:
                    self.board.insert_top_row(self.level.colors, self.rng)
                    self.insertion_countdown = self.level.shots_per_insertion
            if any(r >= self.level.danger_row for r, _ in self.board.occupied()):
                self.status = "lost"

        self.current_egg = self.next_egg
        self.next_egg = self._draw_egg()
        self.shots += 1
        return {
            "cell": cell,
            "bounces": bounces,
            "matched": matched,
            "dropped": floating,
            "gained": gained,
            "status": self.status,
        }

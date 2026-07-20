"""Scoring and combo rules (PRD v1.1 §15). All integer arithmetic.

Per-shot score:

    base      = 10 * matched_eggs + 20 * dropped_eggs
    bank_mult = 1 + min(bounces, 2)          # only if base > 0
    shot      = base * bank_mult
    total     = shot * (4 + combo) // 4      # combo bonus, floor division

Combo: increments AFTER a scoring shot (a shot with base > 0), resets to 0 on
a non-scoring shot. The combo value applied to a shot is the value entering
the shot, so the first scoring shot of a streak gets no bonus.
"""

MATCH_VALUE = 10
DROP_VALUE = 20


def shot_score(matched, dropped, bounces, combo):
    base = MATCH_VALUE * matched + DROP_VALUE * dropped
    if base == 0:
        return 0
    bank_mult = 1 + min(bounces, 2)
    return base * bank_mult * (4 + combo) // 4


def next_combo(combo, scored):
    return combo + 1 if scored else 0

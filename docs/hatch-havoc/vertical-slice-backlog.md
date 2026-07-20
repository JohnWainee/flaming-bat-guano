# Hatch Havoc — Vertical Slice Backlog and Acceptance Tests

**Status:** Milestone 0 deliverable (PRD v1.1 §35 step 7)
**Scope authority:** PRD v1.1 §25.1 (scope) and §25.2 (exit criteria)
**Precondition:** Milestone 0 exit blockers closed (reference device named,
danger mechanic confirmed, visual style selected, voice tone confirmed — PRD §27/§34)

Epics are ordered by dependency. "AT" items are the acceptance tests that
close each epic; PRD references in parentheses.

## E1 — Swift GameCore port

The deterministic model, ported from `prototype/gamecore-reference/`.

- Q16.16 fixed-point module with floor-division semantics
- PCG32 RNG
- Hex grid, board, shot resolver, scoring, game loop, replay/hashing
- Level loader for `level-format.md` v1

**AT-1.1** Unit-test parity: every case in `prototype/gamecore-reference/tests/`
has a Swift XCTest equivalent, green. (§24.3 unit tests)
**AT-1.2** Golden conformance: all `golden/*.json` replay to identical
`finalHash`, score, and status. (§24.3 determinism tests)
**AT-1.3** Cross-device: AT-1.2 passes on the named reference device and the
newest supported device with identical hashes. (§20.2)
**AT-1.4** 100-seed randomized invariant run (no floating clusters, no
overlaps, replay-hash stability) passes in CI. (§24.2)

## E2 — Touch input and aiming

- Drag-anywhere lower-zone aiming; release to fire; cancellation gesture (§11.1, §11.3)
- Precision mode on hold threshold (§11.2)
- Trajectory preview: direct path + first ricochet (§7.1)
- Left/right-handed layout option; safe-area compliance (§11.3, §17.1)

**AT-2.1** A full level is completable one-handed on the reference device. (§25.2)
**AT-2.2** No unintended launches from system navigation gestures in a
scripted XCUITest gesture sweep. (§11.3)
**AT-2.3** Input-to-preview latency imperceptible at 60 fps on the reference
device (no dropped frames while aiming under Instruments). (§24.1)

## E3 — SpriteKit presentation

- Board/egg rendering driven by GameCore events (model is source of truth, §20.4)
- Squash/stretch launch, impact response, match flash, crack, cluster wobble
  + fall, particles, score popups, danger-line rendering (§12.1)
- Nest Keeper insertion telegraph animation (§7.6)
- Screen-shake (major events only) with toggle (§12.1, §17.1)

**AT-3.1** Presentation/model desync harness: after 1,000 scripted shots with
animations enabled, rendered board equals logical board every shot. (§24.3
integration: scene/model synchronization)
**AT-3.2** Reduced-motion setting disables shake/wobble without altering any
replay hash. (§17.1, §6.2)

## E4 — Audio and haptics

- 15–20 original SFX covering launch, impact, match, crack, drop, combo,
  danger, completion, failure, menus (§25.1, §12.3)
- ~12 situational non-verbal vocalizations, cooldowns + weighted selection (§12.4)
- Distinct haptic patterns per §12.2, honoring system settings
- Independent music/effects/voice volume controls (§12.4, §17.1)

**AT-4.1** Every §12.2 event fires its distinct haptic in a scripted run;
toggles silence them. (§24.3 haptic dispatch)
**AT-4.2** 30-minute repetition session: no vocalization plays twice in
succession; frequency setting audibly reduces rate. (§29.3)

## E5 — Modes and content

- Endless mode with escalating insertion cadence (§8.2, §7.6)
- Ten authored challenge levels introducing mechanics one at a time (§25.1, §16.2)
- Three special eggs behind ruleset extension: Wild, Blast, Crack (§9.2)
- Local high score persistence (§25.1)

**AT-5.1** All ten levels completable; each introduces at most one new
mechanic; tutorial goals 1–7 covered across them. (§16.1)
**AT-5.2** Special-egg resolutions are deterministic and covered by new
golden vectors under a bumped ruleset version. (§24.3)

## E6 — Accessibility baseline

- Colorblind-safe palette + pattern overlays (§17.1)
- Adjustable trajectory guide; high-contrast danger line (§17.1)
- VoiceOver for menus/settings; Dynamic Type in non-gameplay UI (§17.1)
- Pause/resume anywhere; suspended-game persistence (§17.1, §23.1)

**AT-6.1** Distinguishability audit of all egg types under deuteranopia/
protanopia/tritanopia simulation with patterns on. (§9.1)
**AT-6.2** Backgrounding mid-shot and relaunching restores the exact logical
state (hash-equal). (§25.2, §19.3)

## E7 — Instrumentation

- Replay recording always-on in playtest builds (§20.5)
- Basic telemetry events from PRD §22.1 (offline-queued)
- Performance profile captured on the reference device (§27 M1 deliverables)

**AT-7.1** A tester-reported defect is reproduced from its replay record
alone, as a drill. (§20.5)

## Slice exit review

The slice ships to internal playtest when every AT above is green plus the
qualitative §25.2 criteria are affirmed in a structured playtest review
(fun/readability/bank-shot reliability/one-hand play), and all included
assets appear in the clean-room register (`clean-room-registers.md`).

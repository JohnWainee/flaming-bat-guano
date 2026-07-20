# Hatch Havoc — Technical Risk Register (Milestone 0)

**Status:** Milestone 0 deliverable (PRD v1.1 §27); complements the product
risk register in PRD §29. Reviewed at every milestone exit.
Likelihood/impact: L/M/H.

| ID | Risk | L | I | Mitigation | Status / evidence |
|----|------|---|---|-----------|-------------------|
| TR-1 | Cross-device float nondeterminism breaks replays and daily leaderboards | H | H | Q16.16 integer math mandated in GameCore (PRD §20.2); golden replay vectors as cross-device CI gate (§24.3) | **Mitigated in design + prototype:** reference core is integer-only; 10 golden vectors generated, byte-stable; Swift port gated by AT-1.2/1.3 |
| TR-2 | Swift floor-division mismatch (Swift `/` truncates; spec floors) silently diverges the port | M | H | Semantics documented in `fixedpoint.py` and `gameplay-rules.md` §1; dedicated negative-operand unit tests required in port | Open until E1; test cases exist in reference suite |
| TR-3 | Ray-march tunneling through eggs at high aim angles | L | M | STEP = D/8 against CONTACT = 0.85·D makes tunneling geometrically impossible; randomized 100-seed invariant test | **Closed in prototype:** invariant suite green |
| TR-4 | Anchor-row insertion corrupts stagger/anchor bookkeeping | M | H | Parity-flip model with stable physical stagger (§7.6); insertion-specific unit tests + invariant suite | **Closed in prototype:** tests green |
| TR-5 | Snap rule produces overlaps or floating attachments in edge geometry | M | H | Candidate-set snap rule (only empty, connected cells are candidates); overlap/floating invariants asserted after every shot in fuzz suite | **Closed in prototype:** tests green |
| TR-6 | SpriteKit maintenance-mode risk strands presentation layer | M | M | Renderer-agnostic GameCore (PRD §20.2, §29.9); presentation isolated in GamePresentation module | Accepted; re-evaluate per §32.2 |
| TR-7 | Presentation/model desync (rendered board ≠ logical board) | M | H | Model is sole source of truth (§20.4); event-driven presentation; desync harness AT-3.1 | Open until E3 |
| TR-8 | Performance misses 60 fps on oldest device (particles, audio voices) | M | M | Reference device named at M0 (§24.1); particle/audio budgets (§29.7); profile at every milestone | **Blocked on Open Decision #1 (reference device)** |
| TR-9 | Ruleset drift: spec, reference core, and Swift port disagree | M | H | Single-source rule: `gameplay-rules.md` + reference core change together; ruleset version bump on any golden-hash change; golden suite in both CIs | Process defined; enforce in review |
| TR-10 | Daily-seed integrity: clients on old rulesets split leaderboards | M | M | Seed pinned to ruleset version; old clients play unranked (PRD §8.4) | Design closed; implement in E5+/Daily Eruption |
| TR-11 | RNG consumption-order changes silently invalidate goldens | M | M | Consumption order is specified ruleset content (`gameplay-rules.md` §2); goldens catch any deviation | Mitigated by golden suite |
| TR-12 | Save-schema migration loses progress across updates | M | H | Versioned saves + tested migrations + atomic writes (PRD §23.2); field-wise cloud merge (§23.3) | Open until M2 save system |

## Retired risks

*(none yet)*

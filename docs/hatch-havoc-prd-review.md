# Hatch Havoc PRD v1.0 — Review and Red-Team Report

**Reviewed document:** Hatch Havoc Product Requirements Document, v1.0 (approved concept)
**Review date:** 2026-07-20
**Companion document:** [`hatch-havoc-prd-v1.1.md`](hatch-havoc-prd-v1.1.md) — revised PRD incorporating every Critical and High finding below. Each amended section carries a `> **Changed in v1.1**` annotation referencing a finding ID from this report.

---

## 1. Overall assessment

This is a strong PRD — better structured and more disciplined than most v1.0 documents. Strengths worth preserving:

- The **clean-room posture** is woven through the whole document (§1, §6.6, §30) rather than bolted on: asset provenance registers, contractor original-contribution declarations, separated inspiration references, and a documented process are exactly the right controls.
- The **non-goals list** (§4) is genuinely disciplined and will resist scope creep.
- **Deterministic model separated from SpriteKit presentation** (§20.2, §20.4) is the correct architecture for this genre, and "SpriteKit nodes must not be treated as the source of truth" is the single most important sentence in the technical sections.
- The **vertical-slice gate before content production** (§25, §27) is the correct process decision, and the exit criteria are concrete and testable.
- The **monetization principles** (§18) and **accessibility baseline** (§17) are strong and differentiating.

The problems fall into three buckets: **internal contradictions** (the document promises things that conflict with each other), **gaps** (things a PRD at "approved concept" status should have settled or at least scoped), and one specific area of **legal exposure** the document underestimates.

Findings are numbered `C-n` (Critical), `H-n` (High), `M-n` (Medium), and `L-n` (Legal). A cross-reference checklist mapping findings to v1.1 changes is at the end.

---

## 2. Critical findings — internal contradictions

### C-1. Determinism vs. real-time mechanics

§6.2 and §20.5 promise deterministic, timing-independent replay ("timing-independent logical events"). But:

- §7.4 lists "a hazard timer completes" as a failure condition,
- §8.2 escalates via "faster nest advancement,"
- §1 promises "reactive nest behavior and visual physics."

Wall-clock timers and continuous physics break replayability from `seed + aim vectors`. Two consistent designs exist:

1. **Shot-indexed logic (recommended):** every pressure mechanic advances per shot — the nest advances every N shots, hazards spread per shot, "timers" count shots. This is how the classic games in this lineage actually work, and it makes §20.5 replay trivially correct.
2. Quantized-tick simulation with ticks recorded in the replay log — significantly more complex for no player-facing benefit in this genre.

The "reactive nest" then becomes presentation-layer response (wobble, anticipation animation) driven by logical events — which is fine, but must be stated so nobody implements physics into `GameCore`.

**Resolution in v1.1:** §7.4, §8.2, and §8.4 re-specified as shot-indexed; §6.2 and §20.5 clarified.

### C-2. Cross-device floating-point determinism is unaddressed

Deterministic daily challenges (§8.4) and replay-verified leaderboards (§20.5) across heterogeneous devices require **bit-identical simulation**. Floating-point trajectory math can diverge across chip generations, compiler versions, and optimization levels. Nothing in §20 addresses this.

**Resolution in v1.1:** §20.2 mandates integer or fixed-point arithmetic for all `GameCore` logic (collision, snapping, hazard spread, scoring); §24.3 adds cross-device golden-replay tests. This is cheap at Milestone 0 and miserable to retrofit.

### C-3. Leaderboard integrity vs. "no backend"

§8.2 wants "anti-cheat validation for submitted scores where practical"; §15.3 says "leaderboard submissions should reject impossible values and malformed runs"; §31.2 says avoid a custom backend. These cannot all hold: **Game Center performs zero server-side validation**, and client-side rejection is trivially bypassed by anyone who can forge a submission. There is no cheap middle ground.

**Resolution in v1.1:** an explicit decision replaces the vague requirement — launch with client-side sanity checks plus documented acceptance that Game Center leaderboards are best-effort/unverified; a replay-verification service moves to the post-launch backlog (consistent with §31.2). The phrase "where practical" is deleted; vague security requirements produce nothing.

### C-4. The free tier is undefined, but the success metrics depend on it

§18.1 offers a "free introductory chapter or limited demo"; §22.2 measures D1/D7 retention and full-game conversion. Whether **Daily Eruption and the Endless leaderboard sit inside or outside the paywall** is the single largest determinant of both metrics — daily challenges are the product's only recurring hook, and in the current reading they are locked behind the one-time purchase.

**Resolution in v1.1:** §18.1 defines the boundary — the free tier includes the introductory campaign chapter and Daily Eruption in unranked practice mode; ranked daily leaderboard, full campaign, Endless, and Fossil Excavation require the unlock.

---

## 3. High-priority gaps

### H-1. The danger mechanic is Open Decision #10 — but it is step 10 of the core loop

Nest advancement is central to game feel, difficulty, and the "reactive nest" differentiator, yet its grid mechanics are entirely unspecified: does a new anchor row insert at the top? Does the whole board translate? What happens to anchor relationships when it moves? The hex-grid prototype (Milestone 0) cannot be validated without this, and the vertical slice cannot be scoped with it open. The same applies to Open Decisions #11 (visual style) and #12 (voice tone).

**Resolution in v1.1:** §7 specifies an anchor-row insertion model as the working design; §34 marks decisions 10–12 as Milestone 0 exit blockers; §27 Milestone 0 exit condition updated.

### H-2. Zero quantitative targets, and "oldest supported device" is undefined

§3.2's success criteria are entirely qualitative, and §24.1 targets "stable frame rate on the oldest supported device" while Open Decision #2 leaves the minimum iOS version open — so the performance target is unmeasurable. Additionally, §3.2's "no material resemblance to a specific existing game's protected audiovisual expression" is unverifiable as written.

**Resolution in v1.1:** §3.2 gains numeric targets (tutorial completion ≥ 80 %, D1 ≥ 30 %, crash-free sessions ≥ 99.5 %, 60 fps sustained on a named reference device); the resemblance criterion becomes "external legal review sign-off obtained," which is measurable; §24.1 requires the reference device to be named at Milestone 0.

### H-3. The biggest business risk is missing from the risk register

§29 covers clone perception, scope, audio, and devices — but not the market: **a premium/one-time-unlock product in the single most F2P-saturated genre on the App Store.** The stated audience (casual players, parents, short sessions) is the least accustomed to paying upfront. The non-predatory stance is right — but it needs a discovery and revenue thesis: ASO, press angle, Apple featuring pitch, comparable premium-puzzle benchmarks, and an evaluation of **Apple Arcade** as an alternative channel (the product profile — premium, no IAP, family-friendly, offline-first — fits Arcade's acquisition criteria almost exactly).

**Resolution in v1.1:** new §5.4 "Market and competitive positioning"; §29 gains a market-risk entry with mitigations.

### H-4. Age-rating strategy should be decided now, not deferred

§5.3 defers the rating, but the decision constrains architecture: entering Apple's **Kids Category** prohibits third-party analytics, IDFA, and most SDKs, and triggers COPPA obligations. Deciding late risks rework in analytics, Game Center, and links-out.

**Resolution in v1.1:** §5.3 commits to general-audience 4+/9+ positioning and explicitly *not* the Kids Category; §22 analytics choices constrained accordingly.

### H-5. Compliance list is missing Apple's privacy manifest and StoreKit edge cases

`PrivacyInfo.xcprivacy` and required-reason API declarations have been mandatory since 2024 and appear nowhere in §26.2 or §33. StoreKit scope is also missing **refund/revocation handling** (an entitlement can be revoked after purchase; the app must respond gracefully) and a **Family Sharing** yes/no decision for the non-consumable unlock.

**Resolution in v1.1:** §26.2 and §33 amended; §23.1/§31 note revocation handling; Family Sharing added to Open Decisions.

### H-6. Recorded English voice lines create a permanent localization tax

§12.4 requires original recordings and §26.1 ships English-only — meaning every future locale requires re-casting, re-recording, re-rating, and re-testing the product's signature feature. **Non-verbal expressive vocalization** (creature "gibberish," Simlish-style) solves localization permanently, reduces repetition fatigue, fits dinosaurs naturally, and further distances the product from any predecessor's voice identity. Informational content stays in subtitled, localizable text. This is the single highest-leverage scope change available.

**Resolution in v1.1:** §12.4 re-specified as non-verbal vocal performance + localized text for informational content.

---

## 4. Medium findings

### M-1. Echo Egg is a testing and balance liability

§9.2's Echo Egg ("repeats or amplifies the last valid special effect") multiplies the special-egg interaction matrix — every new special doubles Echo's test surface, and "amplifies" is undefined. Marginal player value, outsized QA cost. **v1.1:** moved to the post-launch backlog.

### M-2. Cloud-save conflict rule is underspecified

§23.3's "prefer the state with the greatest verified progress" assumes progress is one-dimensional. It isn't: campaign progress, unlocks, high scores, habitat state, and settings advance independently, and a pick-one-save rule silently discards real progress on one axis. **v1.1:** field-wise merge — take the maximum of each independent monotonic axis (campaign, unlocks, ratings, high scores, achievements), last-writer-wins only for settings/preferences, with user-visible recovery preserved.

### M-3. iPad "responsive support" dodges the actual decision

Supporting iPad means choosing: Split View/Stage Manager resizability, or fullscreen-only. Each has real UI costs. **v1.1:** §19.1 commits to fullscreen-only portrait at launch; multitasking support deferred to the post-launch list.

### M-4. SpriteKit platform risk is absent from the risk register

SpriteKit is effectively in maintenance mode at Apple (no meaningful investment in recent releases, no visionOS story). It remains a reasonable 2D choice, and the mitigation is exactly what §20.2 already requires — a renderer-agnostic `GameCore` — but the risk should be named so the team keeps the presentation layer swappable. **v1.1:** added to §29.

### M-5. Minor items

- §8.4 "daily reset based on a clearly defined canonical time": recommend a fixed UTC boundary; already an open decision, flagged as needing closure before Daily Eruption implementation.
- §22: offline event queueing/batching for analytics is implied by offline-first but never stated. **v1.1:** stated.
- §25.1: "three special egg types" for the slice — v1.1 names them (Wild, Blast, Crack) so the slice backlog is concrete.

---

## 5. Legal red team

The clean-room process (§30) is well designed. Two sharpening points:

### L-1. The real exposure is "total concept and feel," not copied assets

This product is recognizably a successor to PopCap's *Dynomite!* (rights now with Electronic Arts), and the character roster maps almost one-to-one: launcher dinosaur, announcer/spotter dinosaur, hatchling rescues. U.S. case law (*Tetris Holding v. Xio Interactive*; *Spry Fox v. LOLApps*) establishes that a cloned **arrangement** of expressive elements can infringe even with 100 % original assets. Game *mechanics* are not protectable, and the mitigations already listed (original everything, plus genuinely new systems: fossils, habitats, hazard eggs, daily seeds) are the correct defense — but note:

- The **spotter/announcer** is the single most Dynomite-identifying feature. Its personality, vocabulary, and function must diverge visibly, not just its recordings. (Finding H-6's non-verbal voice direction helps here too.)
- The differentiators must be prominent **in the vertical slice**, not just in this document — the slice is what early press and any opposing counsel will see first.

### L-2. Legal review is scheduled too late, and one phrase must never go public

§30.2 schedules legal review "before App Store submission." Trademark screening and a total-concept-and-feel review should complete **before any public announcement or external playtest** — a demand letter after announcement is maximally expensive. And "clean-room spiritual successor" is an internal process description; in public-facing copy it reads as an admission of copying intent and invites exactly the claim it is meant to prevent. §30.1 gestures at this ("no marketing copy suggesting affiliation"); v1.1 makes it absolute: no public reference to any predecessor title, no "spiritual successor," "remake," "inspired by," or comparable framing in store copy, press kits, or social posts.

**Resolution in v1.1:** §30.2 re-sequenced; §30.1 marketing-language rule made explicit; §10.1 spotter divergence requirement added.

---

## 6. Findings → v1.1 cross-reference checklist

| ID | Finding | v1.1 change |
|----|---------|-------------|
| C-1 | Determinism vs. real-time mechanics | §6.2, §7.4, §8.2, §8.4, §20.5 — shot-indexed logic |
| C-2 | Cross-device float determinism | §20.2 fixed-point mandate; §24.3 golden-replay tests |
| C-3 | Leaderboard integrity vs. no backend | §8.2, §15.3, §31.2 — explicit best-effort decision |
| C-4 | Undefined free tier | §18.1 free-tier boundary defined |
| H-1 | Danger mechanic open but core | §7.6 working design; §27, §34 M0 blockers |
| H-2 | No quantitative targets / unnamed device | §3.2 numeric targets; §24.1 reference device |
| H-3 | Missing market risk | New §5.4; §29.8 market-risk entry |
| H-4 | Age-rating deferred | §5.3 non-Kids-Category commitment |
| H-5 | Privacy manifest, refunds, Family Sharing | §26.2, §33, §23.1, §34 |
| H-6 | English voice localization tax | §12.4 non-verbal vocal direction |
| M-1 | Echo Egg | §9.2 deferred to post-launch |
| M-2 | Cloud merge underspecified | §23.3 field-wise merge |
| M-3 | iPad decision dodged | §19.1 fullscreen-only at launch |
| M-4 | SpriteKit risk unnamed | §29.9 risk entry |
| M-5 | Minor items | §8.4, §22, §25.1 |
| L-1 | Total concept and feel | §10.1 spotter divergence; §29.1 strengthened |
| L-2 | Legal timing / public language | §30.1, §30.2 |

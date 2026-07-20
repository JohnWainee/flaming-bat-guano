# Hatch Havoc
## Product Requirements Document

**Document status:** Approved concept — implementation planning
**Version:** 1.1 (revision of v1.0; see [`hatch-havoc-prd-review.md`](hatch-havoc-prd-review.md) for the review that produced this revision — amended sections carry a `> **Changed in v1.1**` annotation with finding IDs)
**Platform:** iOS and iPadOS
**Working title:** Hatch Havoc
**Product type:** Dinosaur-themed arcade puzzle game
**Reference category:** Egg-launching color-match puzzle game
**Development posture:** Clean-room independent development; no reuse of third-party code, assets, audio, layouts, level data, branding, or proprietary implementation details. This posture is internal process language only and must never appear in public-facing copy (see §30.1).

---

## 1. Executive Summary

Hatch Havoc is a portrait-oriented iOS arcade puzzle game built around launching colorful dinosaur eggs into unstable prehistoric nests. Players match egg colors, create chain reactions, detach unsupported clusters, rescue hatchlings, excavate fossils, and prevent the nest from crossing a danger boundary.

The product is intended to preserve the broad appeal of classic egg-launching puzzle games while establishing its own identity through:

- Original dinosaur characters and habitats
- Touch-first aiming and bank-shot controls
- Reactive nest presentation and visual feedback driven by deterministic game logic
- Distinctive sound effects, voice reactions, music, and haptics
- Multiple objective-driven modes
- Deterministic daily challenges
- Accessible, non-predatory progression
- A clean-room implementation using native Apple technologies

The initial release will prioritize a highly polished core loop over breadth. The game must feel responsive, readable, funny, and satisfying within the first thirty seconds of play.

> **Changed in v1.1 (C-1):** "Reactive nest behavior and visual physics" reworded — nest reactivity is a presentation-layer response to logical events, never a physics simulation inside the game model.

---

## 2. Product Vision

Create the definitive dinosaur-themed egg puzzle game for iPhone: immediately understandable, mechanically precise, audibly memorable, and deep enough to reward skilled bank shots, board planning, and chain-reaction play.

### Product promise

> Aim carefully, crack the nest, rescue the hatchlings, and cause prehistoric chaos.

---

## 3. Product Goals

### 3.1 Primary goals

1. Deliver a polished one-handed puzzle experience designed specifically for touch.
2. Make every successful shot feel materially satisfying through animation, audio, and haptics.
3. Support both short casual sessions and score-driven mastery.
4. Establish an original dinosaur universe suitable for future characters, environments, modes, and sequels.
5. Ship a technically stable, offline-first product with deterministic core gameplay.
6. Avoid manipulative monetization mechanics.

### 3.2 Success criteria

> **Changed in v1.1 (H-2):** qualitative criteria replaced or backed with measurable targets; the unverifiable "no material resemblance" criterion replaced with a legal sign-off gate.

The product will be considered successful when it demonstrates:

- Tutorial completion rate ≥ 80 % of first sessions
- First-session comprehension without a text-heavy tutorial (validated in moderated playtests: ≥ 8 of 10 new players complete a level unaided)
- Reliable touch aiming and predictable collision behavior (zero non-deterministic collision defects in automated stress testing)
- Day-1 retention ≥ 30 %; Day-7 retention ≥ 12 % (initial targets; recalibrate after soft launch)
- Crash-free session rate ≥ 99.5 %
- Sustained 60 fps on the named reference device (see §24.1)
- Repeat play driven by score improvement, daily challenges, and content progression
- Positive qualitative response to sound design and character reactions
- No progression blocker requiring payment
- **External legal review sign-off obtained** covering trademark, trade dress, and total-concept-and-feel exposure (see §30)

---

## 4. Non-Goals

The initial product will not include:

- Real-time multiplayer
- Synchronous competitive matches
- User-generated levels
- A persistent online requirement
- Energy systems
- Loot boxes
- Consumable pay-to-win power-ups
- Forced interstitial advertising
- A large narrative campaign
- Full 3D environments
- Direct ports or replicas of third-party levels
- Reused third-party voice lines, music, art, UI, or sound effects
- A generalized cross-platform engine abstraction before product-market validation
- A custom backend or server-side anti-cheat at launch (see §15.3, §31.2)

---

## 5. Target Audience

### 5.1 Primary audience

Casual and mid-core mobile players who enjoy:

- Color-matching puzzle games
- Physics-adjacent aiming games
- Short sessions
- Cute or comedic character reactions
- Score chasing
- Collectible progression
- Daily challenges

### 5.2 Secondary audience

- Players nostalgic for early PC arcade puzzle games
- Parents seeking a low-friction, non-predatory mobile game
- Players who prefer offline-capable games
- Puzzle players who enjoy precision shots and deterministic outcomes

### 5.3 Age positioning

> **Changed in v1.1 (H-4):** rating strategy decided now instead of deferred, because it constrains analytics, SDK, and Game Center decisions.

- **General-audience positioning with an expected 4+ or 9+ rating.**
- The product will **not** enter Apple's Kids Category. This preserves the ability to use Game Center, modest first-party analytics, and standard SDKs, all of which the Kids Category restricts or prohibits.
- The product must nonetheless remain family-appropriate in content, and must not knowingly collect personal data from children (COPPA/GDPR-K obligations apply to conduct, not just category).
- Final rating confirmation happens at Beta (§27), but no design decision may assume Kids Category entry.

### 5.4 Market and competitive positioning

> **Added in v1.1 (H-3).**

The launch monetization (premium unlock, §18) places the product in the most F2P-saturated genre on the App Store, sold to an audience (casual players, parents) least accustomed to paying upfront. This is the product's largest business risk and requires an explicit go-to-market thesis:

- **Positioning:** the non-predatory premium model *is* the marketing message — "the bubble-shooter you pay for once, that never nags you." Target press and communities that celebrate premium mobile games.
- **Discovery plan:** ASO research during production; an Apple featuring pitch built on the accessibility baseline (§17), offline-first design, and family-safe monetization — all attributes Apple editorial favors.
- **Benchmarks:** before Milestone 2, gather revenue benchmarks for comparable premium mobile puzzle titles to validate the price point (Open Decision #3).
- **Apple Arcade evaluation:** the product profile — premium, no IAP, family-friendly, offline-first, Game Center-integrated — closely matches Apple Arcade acquisition criteria. Evaluate an Arcade pitch as an alternative or complementary channel before Milestone 3; an Arcade deal would substitute for the unlock model and de-risk discovery entirely.

---

## 6. Product Principles

### 6.1 Touch-first, not port-first

Controls, layout, pacing, and feedback must be designed for iPhone rather than adapted mechanically from desktop input.

### 6.2 Deterministic gameplay

> **Changed in v1.1 (C-1):** determinism defined precisely as shot-indexed.

The logical game model is **turn-based and shot-indexed**: all state transitions — matches, detachment, hazard spread, danger advancement, objective progress, scoring — occur as deterministic functions of (previous state, player action, seed). No gameplay-relevant state may depend on wall-clock time, frame rate, animation timing, or physics simulation. Real-time elements exist only in the presentation layer. Seeded challenges must be reproducible bit-for-bit on every supported device (see §20.2).

### 6.3 Readable chaos

Visual effects may be energetic, but they must never obscure:

- Current egg color
- Next egg color
- Aim direction
- Danger boundary
- Objective progress
- Remaining valid attachment spaces

### 6.4 Audio as a gameplay system

Sound is not decorative. It communicates:

- Contact
- Match quality
- Cluster detachment
- Combo escalation
- Danger
- Special egg activation
- Objective completion
- Failure

### 6.5 Fair progression

Progression should reward skill and continued play without creating artificial frustration.

### 6.6 Original identity

Dinosaurs, eggs, habitats, voices, music, effects, UI, names, animations, and level design must be independently created.

---

## 7. Core Gameplay

### 7.1 Core loop

1. The player receives a current egg and sees the next egg.
2. The player drags to aim.
3. The trajectory preview shows the direct path and permitted ricochet guidance.
4. The player releases to launch.
5. The egg collides with the nest or playfield boundary.
6. The egg attaches to the logical grid.
7. The game resolves color matches.
8. Unsupported clusters detach and fall.
9. Special eggs, hazards, objectives, scoring, audio, animation, and haptics resolve.
10. The danger state advances according to the active mode (per shot — see §7.6).
11. The player repeats until the objective is completed or the run ends.

### 7.2 Base match rules

- Eggs occupy a staggered hexagonal grid.
- A match occurs when the newly attached egg connects to a contiguous group meeting the configured threshold.
- The default threshold is three eggs of the same color.
- Matched eggs are removed.
- Any cluster no longer connected to an anchor row or anchor object is detached.
- Detached clusters score more than ordinary matches.
- Resolution order must be deterministic.

### 7.3 Shot behavior

Required:

- Direct shots
- Single-wall bank shots
- Multi-wall shots when geometry permits
- Consistent collision tolerance
- Predictable snapping to available cells
- Prevention of invalid overlaps
- Prevention of unresolved floating clusters

Optional after MVP:

- Limited multi-bounce trajectory preview
- Advanced "minimal assist" aiming mode
- Character-specific trajectory modifiers

### 7.4 Failure conditions

> **Changed in v1.1 (C-1):** all timers re-specified as shot counts.

Failure may occur when:

- Eggs cross the danger boundary
- A protected hatchling or fossil is destroyed
- A move limit expires
- A hazard shot-countdown completes (hazard "timers" count shots taken, not seconds)
- The player fails a mode-specific condition

No failure condition may depend on wall-clock time. Modes that want temporal pressure express it as shots-per-advancement, never seconds.

### 7.5 Victory conditions

Victory may require:

- Rescuing a target number of hatchlings
- Clearing all eggs
- Clearing all target eggs
- Dropping a fossil to the excavation zone
- Surviving a set number of nest shifts
- Reaching a score threshold
- Completing a challenge with limited shots
- Triggering a specified chain or combo

### 7.6 Danger and nest advancement (working design)

> **Added in v1.1 (H-1):** the danger mechanic was previously Open Decision #10 with no working design, yet it is step 10 of the core loop. This working design is the Milestone 0 prototype baseline; Milestone 0 exit requires confirming or replacing it (§27, §34).

- The board's top edge holds **anchor rows**. Danger pressure advances the nest by **inserting a new anchor row at the top every N shots** (N configured per level/mode), pushing all existing rows one row toward the danger boundary.
- Row insertion is a deterministic logical event: inserted row contents come from the seeded sequence; anchor relationships are recomputed after insertion by the standard connectivity rule (§7.2) — no special-case anchor bookkeeping.
- Hex-grid row parity: inserting a row flips the stagger parity of all existing rows' *rendered* positions; the logical grid stores axial coordinates relative to the current top row so cell identity is stable across insertions.
- The Nest Keeper character (§10.1) telegraphs insertion one shot in advance (animation + audio + haptic anticipation), and the presentation layer may wobble, creak, and shift the nest — but presentation never feeds back into the model.
- Endless mode escalates by reducing N; authored levels may fix, vary, or disable insertion.

---

## 8. Game Modes

### 8.1 Nest Rescue

The primary campaign mode.

Each level contains one or more objectives:

- Rescue hatchlings
- Clear target egg types
- Break fossilized shells
- Remove parasites
- Survive nest movement
- Complete within a move limit
- Trigger a required chain reaction
- Avoid protected objects

Requirements:

- Authored level layouts
- Difficulty progression
- Three-tier performance rating
- Optional assist mode
- Clear objective presentation before and during play
- Resume support for interrupted sessions

### 8.2 Extinction Endless

An infinite score-attack mode.

Difficulty may increase through:

- Additional colors
- Nest advancement every fewer shots (§7.6)
- Reduced safe space
- More hazards
- Increased armored-egg frequency
- Reduced preview assistance
- More irregular anchor patterns

Requirements:

> **Changed in v1.1 (C-3):** "anti-cheat validation where practical" replaced with an explicit integrity decision — see §15.3.

- Local high score
- Game Center leaderboard
- Deterministic score calculation
- Score integrity per §15.3 (client-side sanity checks; leaderboards are best-effort at launch)
- Run summary with score breakdown

### 8.3 Fossil Excavation

An authored puzzle mode centered on safely lowering fossils.

Requirements:

- Fossils act as gravity-bound objectives
- Fossils cannot be matched
- Surrounding support must be removed strategically
- Damage or impact rules must be explicit
- Levels emphasize planning rather than reaction speed

### 8.4 Daily Eruption

A seeded daily challenge shared by all players.

Requirements:

> **Changed in v1.1 (C-1, C-2, M-5):** reset time recommendation, and version-compatibility policy for shared seeds.

- Same starting board and egg sequence for all players
- Daily reset at a fixed **UTC boundary (recommended: 00:00 UTC)** — one global reset, no per-timezone boards (final confirmation: Open Decision #13)
- Each daily seed is **pinned to a ruleset version**; a client whose bundled ruleset is older than the seed's pinned version may play unranked practice but cannot submit a ranked score. This prevents split leaderboards across app versions.
- Local practice mode is separate from ranked attempts
- Game Center daily or periodic leaderboard
- Shareable result card
- Seed versioning to preserve reproducibility across releases

---

## 9. Egg Types

### 9.1 Standard eggs

- Four colors in tutorial content
- Five colors in normal play
- Optional sixth color in advanced content
- Color palette must remain distinguishable under supported accessibility modes

### 9.2 Special eggs

> **Changed in v1.1 (M-1):** Echo Egg deferred to the post-launch backlog — its "repeat/amplify last effect" rule multiplies the interaction-test matrix with every other special for marginal player value. Vertical-slice trio named.

#### Wild Egg
Matches with any adjacent color group.

#### Blast Egg
Destroys eggs within a defined radius.

#### Crack Egg
Damages armored or fossilized shells.

#### Swap Egg
Allows the player to exchange current and next eggs.

#### Anchor Egg
Attaches as a temporary structural support.

**Deferred to post-launch backlog:** Echo Egg (repeats or amplifies the last valid special effect).

The vertical slice requires exactly three special egg types: **Wild, Blast, and Crack** (they exercise the three distinct resolution paths: match logic, area removal, and durability damage).

### 9.3 Hazard eggs

#### Stone Egg
Cannot be matched normally.

#### Armored Egg
Requires multiple hits or a special effect.

#### Parasite Egg
Spreads under configured conditions if ignored (spread evaluated per shot, per §6.2).

#### Rotten Egg
Penalizes adjacent matches or releases a temporary obstruction.

Hazards must be introduced individually and explained through gameplay.

---

## 10. Dinosaur Characters

### 10.1 Character roles

#### Launcher Dinosaur
Represents the player during gameplay.

Functions:

- Aiming animation
- Launch animation
- Miss reaction
- Combo celebration
- Danger reaction
- Ability identity

#### Spotter Dinosaur
Acts as announcer and tactical commentator.

> **Changed in v1.1 (L-1):** the announcer role is the most genre-predecessor-identifying single feature. Its personality, function, and vocal identity must visibly diverge from any prior title's announcer: non-verbal vocal performance (§12.4), a distinct comedic persona defined in an original character brief, and commentary tied to Hatch-Havoc-specific systems (hatchling rescues, fossil handling, nest telegraphs) rather than generic shot callouts.

Functions:

- Calls out combos
- Warns about danger
- Reacts to bank shots
- Celebrates rescue events
- Provides limited tutorial guidance

#### Nest Keeper
Represents escalation pressure.

Functions:

- Advances the nest (telegraphs and performs row insertion, §7.6)
- Signals danger
- Introduces mode-specific disruptions
- Provides visual and audio anticipation before escalation

#### Hatchlings
Serve as rescue targets, rewards, and habitat occupants.

#### Fossil Curator
Introduces excavation content and provides dry commentary.

### 10.2 Character abilities

Post-MVP character variants may provide:

- Longer trajectory preview
- Better next-egg control
- Slower danger advance
- Increased detached-cluster score
- Larger wildcard radius
- One protected combo miss
- Improved power-egg generation

Abilities must be horizontally differentiated. No character may create a mandatory competitive advantage that requires payment.

---

## 11. Controls and Input

### 11.1 Default control model

- Touch and drag anywhere in the lower interaction zone to aim.
- Release to fire.
- Current egg remains visually associated with launcher position.
- Input must not require the player to cover the target area with a finger.

### 11.2 Precision mode

- Holding beyond a configurable threshold enables precision aiming.
- Precision mode reduces sensitivity.
- Optional stronger trajectory visualization may appear.

### 11.3 Input requirements

- No unintended launch from navigation gestures
- Support for left- and right-handed play
- Safe-area compliance
- Clear cancellation behavior
- Minimum touch targets consistent with platform conventions
- No reliance on high-precision finger movement for basic completion

---

## 12. Feedback and Game Feel

### 12.1 Visual feedback

Required:

- Egg squash and stretch on launch
- Shell impact response
- Match flash
- Crack animation
- Cluster wobble before detachment
- Falling cluster motion
- Particle effects
- Score popups
- Combo escalation
- Screen shake for major events only
- Danger-state environment response

### 12.2 Haptic feedback

Distinct haptic patterns for:

- Launch
- Wall ricochet
- Basic match
- Large match
- Cluster detachment
- Special egg activation
- Danger escalation
- Level completion
- Failure

Haptics must be optional and respect system-level limitations.

### 12.3 Audio feedback

Every important event must have a recognizable sound signature.

Audio categories:

- Launcher vocalizations
- Spotter commentary
- Hatchling sounds
- Shell impacts
- Match pops
- Cracks
- Falling whistles
- Cluster impacts
- Combo stingers
- Power effects
- Danger percussion
- Nest movement
- Level completion
- Failure
- Menu interactions
- Ambient habitat audio

### 12.4 Voice direction

> **Changed in v1.1 (H-6, L-1):** character voice is **non-verbal expressive vocalization** (original creature "gibberish"), not recorded language. This (a) eliminates the per-locale re-record/re-rate/re-test cost that spoken English would impose on every future localization, (b) reduces repetition fatigue because non-verbal barks tolerate far more repetition than words, and (c) further distances the product from any predecessor's voice identity. All *informational* content (tutorial guidance, objective callouts) is delivered as localized, subtitled text — never as speech the player must understand.

- Original recordings only; original vocal performances directed from original character briefs
- No spoken natural language in character vocalizations; emotional meaning carried by tone, pitch, and timing
- No imitation of recognizable third-party characters
- Context-aware playback
- Cooldowns to avoid repetition
- Weighted random selection
- Escalating combo vocalization pools
- Separate controls for voice, music, and effects
- Subtitle/text support for all informational communication
- Voice-frequency setting

---

## 13. Art Direction

### 13.1 Visual style

Recommended direction:

- Expressive 2D cartoon animation
- Readable silhouettes
- Bold shell patterns
- Warm prehistoric environments
- High contrast between interactive and decorative elements
- Broad facial animation
- Minimal visual realism
- Distinct environment palettes

### 13.2 Environment themes

Potential launch environments:

1. Fern Canyon
2. Volcano Nest
3. Crystal Cavern
4. Tar Marsh
5. Meteor Ridge

The vertical slice requires one environment.

### 13.3 UI style

- Original layout
- Portrait-first
- Large touch targets
- Minimal HUD
- Clear score and objective hierarchy
- Strong current/next egg visibility
- High contrast danger line
- No imitation of a specific legacy title's typography or menu structure

---

## 14. Progression

### 14.1 Campaign progression

- Level map or chapter sequence
- Gradual mechanic introduction
- Performance rating per level
- Optional replay goals
- Unlockable environments
- Unlockable characters
- Cosmetic habitat rewards

### 14.2 Habitat system

Rescued hatchlings populate interactive habitats.

Possible functions:

- Cosmetic collection
- Passive character animations
- Audio interactions
- Achievement display
- Environment customization
- Non-competitive progression

The habitat system must not become a mandatory resource-management layer in the initial release.

### 14.3 Unlock philosophy

Unlocks should be earned through:

- Campaign progress
- Score milestones
- Mode completion
- Achievements
- Optional premium entitlement

No randomized paid unlocks.

---

## 15. Scoring and Combo System

### 15.1 Base scoring

Score components may include:

- Eggs matched
- Cluster size
- Detached eggs
- Bank-shot multiplier
- Consecutive successful shots
- Objective bonuses
- Remaining shots
- Rescue bonuses
- Hazard-clearing bonuses

### 15.2 Combo rules

A combo increases when:

- A shot creates a valid match
- A shot detaches a cluster
- A special egg produces a valid scoring result

A combo resets when:

- A shot fails to create a qualifying result
- A mode-specific penalty occurs

Character abilities may protect one combo miss, but this must remain transparent.

### 15.3 Score integrity

> **Changed in v1.1 (C-3):** vague anti-cheat language replaced with an explicit launch decision consistent with §31.2 (no custom backend).

- Score calculation must occur in the deterministic game model.
- Presentation timing must not affect score.
- Daily challenge scores must include seed and ruleset version.
- **Launch decision:** Game Center performs no server-side validation, and the product ships without a custom backend. Therefore, at launch:
  - The client performs sanity checks before submission (score within the theoretical maximum for the seed/ruleset; run event log internally consistent).
  - Leaderboards are **explicitly best-effort**: a determined cheater can forge scores, and the team accepts this at launch rather than building server infrastructure prematurely.
  - Every ranked run records a replay log (§20.5) locally, so a **server-side replay-verification service is a post-launch option** (see §31.2) without client rework.
- No score duplication on resubmission (idempotent submission keyed by run identifier).

---

## 16. Tutorial and Onboarding

### 16.1 Tutorial goals

Teach without interrupting flow:

1. Aim and release
2. Match three
3. Use a wall bank
4. Detach unsupported clusters
5. Read the danger boundary
6. Understand objectives
7. Use a special egg

### 16.2 Tutorial requirements

- Interactive, not text-heavy
- Skippable after the first critical lesson
- Replayable from settings
- Contextual prompts
- No more than one new mechanic per introductory level
- No account requirement before gameplay

---

## 17. Accessibility

### 17.1 Required launch features

- Colorblind-safe egg differentiation
- Shape or pattern overlays independent of color
- Adjustable trajectory guide
- Reduced motion
- Screen shake toggle
- Haptics toggle
- Voice frequency control
- Independent music, effects, and voice volume
- High-contrast danger indicators
- Dynamic Type support in non-gameplay UI
- VoiceOver support for menus and settings
- Left-handed control option
- Pause and resume at any time
- No time pressure in tutorial and selected assist modes

### 17.2 Optional assist features

- Full projected trajectory
- Slower nest movement (more shots per advancement)
- Increased aim tolerance
- Undo token in authored puzzle modes
- Reduced hazard spread
- Extended move limits

Assist use should not disable campaign completion. Competitive leaderboard eligibility may use clearly labeled standardized settings.

---

## 18. Monetization

### 18.1 Model and free-tier boundary

> **Changed in v1.1 (C-4):** the free/paid boundary is now defined, because the retention and conversion metrics in §22.2 depend entirely on it.

**Model:** free download with a one-time in-app purchase to unlock the full game.

**Free tier includes:**

- The introductory campaign chapter (tutorial + first environment's opening levels)
- **Daily Eruption in unranked practice mode** — the daily board is playable by everyone, preserving the product's only recurring-engagement hook for unconverted players
- Settings, accessibility features, habitat viewing for earned content

**Full unlock includes:**

- Full campaign
- Extinction Endless (with Game Center leaderboard)
- Fossil Excavation
- **Ranked Daily Eruption** (leaderboard submission)
- All earnable characters and habitats

**Family Sharing** for the unlock: decide before Milestone 2 (Open Decision #16); default recommendation is to enable it — it fits the family-friendly positioning and costs little.

### 18.2 Prohibited launch monetization

- Forced interstitial ads
- Energy timers
- Loot boxes
- Paid randomized rewards
- Pay-to-win stat boosts
- Consumable retries sold during failure
- Dark-pattern purchase prompts
- Mandatory subscriptions

### 18.3 Optional post-launch purchases

Permitted only if they do not affect competitive fairness:

- Cosmetic dinosaur skins
- Habitat themes
- Soundtrack
- Expansion chapters
- Additional authored puzzle packs

---

## 19. Platform Requirements

### 19.1 Supported devices

> **Changed in v1.1 (M-3):** iPad support scoped precisely.

- iPhone first
- iPad: **fullscreen-only portrait at launch** — the app opts out of Split View / Slide Over / Stage Manager resizing. iPad-specific presentation improvements (and a multitasking decision) are on the post-launch list (§32.2).
- Portrait orientation for gameplay
- Landscape not required for initial release

### 19.2 Offline behavior

The following must work offline:

- Campaign
- Endless mode
- Fossil Excavation
- Settings
- Local progression
- Local high scores
- Habitat viewing

The following may require network access:

- Game Center
- Daily leaderboard submission
- Cloud synchronization
- Entitlement restoration
- Remote configuration
- Analytics upload

### 19.3 Interruption handling

The game must safely handle:

- Incoming calls
- App backgrounding
- Audio interruptions
- Device rotation attempts
- Low-memory events
- Store authentication prompts
- Network loss

---

## 20. Technical Architecture

### 20.1 Recommended stack

- Swift
- SwiftUI for application shell and non-gameplay interfaces
- SpriteKit for game rendering and animation (platform risk noted in §29.9; mitigated by §20.2's renderer-agnostic model)
- AVAudioEngine for responsive audio mixing
- Core Haptics for tactile feedback
- GameKit for achievements and leaderboards
- StoreKit 2 for entitlements
- CloudKit or platform-appropriate save synchronization if cloud save is enabled
- XCTest for deterministic model tests
- XCUITest for critical UI flows

### 20.2 Architecture principles

> **Changed in v1.1 (C-2):** numeric determinism mandated.

- Gameplay model independent from rendering
- Deterministic state transitions
- **All `GameCore` arithmetic uses integer or fixed-point math** — collision resolution, cell snapping, hazard spread, danger advancement, and scoring must not use floating point, so that replays and daily-challenge results are bit-identical across every supported device, chip generation, and compiler version. Floating point is permitted only in the presentation layer.
- Dependency injection for platform services
- Versioned save data
- Event-driven presentation
- Explicit finite-state management
- Replayable debug traces
- Asset identifiers separated from gameplay rules

### 20.3 Logical module structure

```text
HatchHavocApp
├── AppShell
│   ├── Navigation
│   ├── Settings
│   ├── Accessibility
│   └── Entitlements
├── GameCore
│   ├── BoardModel
│   ├── HexGrid
│   ├── ShotResolver
│   ├── AttachmentResolver
│   ├── MatchResolver
│   ├── ClusterResolver
│   ├── ObjectiveSystem
│   ├── HazardSystem
│   ├── ScoringSystem
│   ├── SeededRandom
│   └── ReplayLog
├── GamePresentation
│   ├── SpriteKitScene
│   ├── EggNodes
│   ├── CharacterNodes
│   ├── ParticleEffects
│   ├── CameraEffects
│   └── HUD
├── SensoryFeedback
│   ├── AudioDirector
│   ├── VoiceLineDirector
│   └── HapticDirector
├── Content
│   ├── LevelDefinitions
│   ├── CharacterDefinitions
│   ├── EggDefinitions
│   ├── Localization
│   └── AssetCatalog
├── Progression
│   ├── Campaign
│   ├── Unlocks
│   ├── Achievements
│   ├── Habitat
│   └── PlayerProfile
└── PlatformServices
    ├── GameCenter
    ├── StoreKit
    ├── CloudSave
    ├── Analytics
    └── RemoteConfig
```

### 20.4 Core state model

The model should contain:

- Board cell occupancy
- Egg identifiers and types
- Anchor relationships
- Current egg
- Next egg
- Shot state
- Combo state
- Score
- Objective state
- Hazard state
- Danger progression (shots-until-next-insertion counter, §7.6)
- Random seed
- Ruleset version
- Run event log

SpriteKit nodes must not be treated as the source of truth.

### 20.5 Deterministic replay

> **Changed in v1.1 (C-1):** replay inputs clarified — no timing data exists to record.

Each run must be exactly reproducible using:

- Initial seed
- Ruleset version
- Level identifier
- Ordered sequence of player actions (shot aim vectors as fixed-point values, swap uses, special-item activations)

Because the model is shot-indexed (§6.2), no timestamps or tick data are needed or permitted in the logical replay. Replay logging is required for debugging and is the foundation for optional post-launch leaderboard verification (§15.3).

---

## 21. Content Data Model

### 21.1 Level definition

Each authored level should define:

- Level identifier
- Environment
- Board dimensions
- Initial egg layout
- Available colors
- Special eggs
- Hazard rules
- Objective definitions
- Shot or move limits
- Danger behavior (shots-per-insertion, or disabled)
- Egg sequence policy
- Random seed policy
- Reward definition
- Tutorial prompts
- Assist overrides

### 21.2 Egg definition

Each egg type should define:

- Identifier
- Category
- Match behavior
- Attachment behavior
- Damage rules
- Detachment behavior
- Score value
- Visual asset set
- Sound event identifiers
- Particle event identifiers
- Accessibility pattern
- Localization keys

### 21.3 Character definition

Each character should define:

- Identifier
- Role
- Ability
- Animation set
- Voice set
- Unlock conditions
- Cosmetic variants
- Habitat behavior
- Accessibility metadata

---

## 22. Analytics and Telemetry

Analytics should be minimal, privacy-conscious, and purpose-driven.

> **Changed in v1.1 (H-4, M-5):** analytics choices constrained by the §5.3 rating decision; offline queueing stated.

Constraints from §5.3: the product is general-audience (not Kids Category), so a lightweight analytics SDK or first-party pipeline is permissible — but the provider must be selected against the privacy requirements below (Open Decision #14). Events are **queued locally while offline** and batch-uploaded opportunistically; analytics must never block or degrade offline play (§19.2).

### 22.1 Core events

- App launched
- Tutorial started
- Tutorial completed
- Level started
- Level completed
- Level failed
- Failure reason
- Session duration
- Mode selected
- Shot count
- Match size
- Detached-cluster size
- Special egg used
- Assist feature used
- Purchase screen viewed
- Purchase completed
- Entitlement restored
- Crash or recoverable error

### 22.2 Product metrics

- Tutorial completion rate (target ≥ 80 %, §3.2)
- First-session completion rate
- Day-1 and Day-7 retention (targets: ≥ 30 % / ≥ 12 %, §3.2)
- Median session length
- Levels completed per session
- Failure distribution
- Endless mode repeat rate
- Daily challenge participation (free practice vs. ranked, per §18.1)
- Audio-disabled rate
- Assist-feature adoption
- Full-game conversion rate
- Crash-free session rate (target ≥ 99.5 %, §3.2)

### 22.3 Privacy requirements

- Collect only necessary data
- Avoid sensitive personal data
- Avoid precise location
- Avoid advertising identifiers unless a future business requirement explicitly justifies them
- Provide clear disclosures
- Support consent requirements where applicable
- Allow analytics to be disabled where required or strategically appropriate
- Ship an accurate **privacy manifest (`PrivacyInfo.xcprivacy`)** including required-reason API declarations, covering the app and every third-party SDK (see §26.2, §33)

---

## 23. Save Data and Progression Integrity

### 23.1 Local save requirements

Persist:

- Campaign progress
- Level ratings
- Character unlocks
- Habitat state
- Settings
- Accessibility preferences
- Purchase entitlement cache
- Achievements pending submission
- Local high scores
- Active suspended game

> **Changed in v1.1 (H-5):** the entitlement cache must handle **revocation** — StoreKit 2 can revoke a transaction after refund or Family Sharing changes; the app must detect revocation on entitlement refresh and degrade gracefully to the free tier without corrupting progression data (progress is retained; only access is gated).

### 23.2 Save versioning

- Every save must include a schema version.
- Migrations must be tested.
- Corrupt saves must fail safely.
- The player should not lose paid entitlement due to local corruption.
- Critical state should use atomic writes.

### 23.3 Cloud synchronization

> **Changed in v1.1 (M-2):** pick-one-save conflict resolution replaced with field-wise merge, because progress is multi-dimensional and a whole-save winner silently discards real progress on the losing axes.

If implemented:

- Resolve conflicts by **field-wise merge**, not by choosing one save wholesale:
  - For each independent monotonic axis — campaign completion, per-level ratings, character/environment unlocks, achievements, local high scores — take the maximum/union of the two saves.
  - Settings and accessibility preferences: last-writer-wins.
  - Active suspended game: prefer the device with the newer suspension; never let it override monotonic progress.
- Never overwrite a materially more advanced axis without user-visible recovery.
- Keep local play functional during cloud outages.

---

## 24. Quality Requirements

### 24.1 Performance

> **Changed in v1.1 (H-2):** the reference device must be named for these targets to be testable.

Targets:

- Sustained 60 fps on the **named oldest supported reference device** — the device (and thereby minimum iOS version, Open Decision #2) must be fixed at Milestone 0 so every performance target is measurable from the first prototype
- No visible input latency during aiming
- No frame hitch on first use of common effects
- Fast scene transitions
- Controlled memory growth
- Bounded particle counts
- Preloaded critical audio
- No blocking network call on the gameplay path

### 24.2 Reliability

- No unresolved board state
- No invalid overlapping eggs
- No impossible level caused by random generation
- Safe recovery after interruption
- Idempotent entitlement restore
- Deterministic daily seeds
- No score duplication on resubmission
- No progression loss after app updates

### 24.3 Test strategy

#### Unit tests
- Hex-grid neighbor calculations (including across anchor-row insertion, §7.6)
- Shot snapping
- Match detection
- Cluster anchoring
- Detachment
- Scoring
- Objective resolution
- Hazard spread
- Seeded sequence generation
- Save migration

#### Property-based or fuzz tests
- Random board generation
- Collision edge cases
- Large chain reactions
- Repeated attach/remove cycles
- Floating-cluster prevention
- Serialization round trips

#### Determinism tests

> **Added in v1.1 (C-2).**

- **Golden replay suite:** a corpus of recorded runs whose final state hashes are asserted on every CI run and on every supported device class; any hash divergence across devices or app versions is a release blocker
- Replay round-trip: record → replay → identical event log and final state

#### Integration tests
- Scene/model synchronization
- Audio event dispatch
- Haptic event dispatch
- Game Center submission
- Store entitlement restore (including revocation, §23.1)
- Cloud save conflict handling (field-wise merge cases, §23.3)

#### UI tests
- First launch
- Tutorial
- Pause/resume
- Purchase flow
- Restore flow
- Accessibility settings
- Offline mode
- Daily challenge entry

---

## 25. Vertical Slice

### 25.1 Scope

The first playable vertical slice must include:

- One portrait playfield
- One environment
- Five standard egg colors
- Hex-grid attachment
- Direct and bank shots
- Match-three resolution
- Unsupported-cluster detachment
- The §7.6 danger system (anchor-row insertion)
- One launcher dinosaur
- One spotter dinosaur
- One hatchling type
- Three special egg types: **Wild, Blast, Crack** (§9.2)
- Fifteen to twenty original sound effects
- Approximately twelve situational non-verbal vocalizations (§12.4)
- Core haptics
- One Endless mode
- Ten authored challenge levels
- Local high score
- Accessibility baseline
- Deterministic replay logging

### 25.2 Exit criteria

The vertical slice is complete when:

- Input feels responsive and predictable.
- Players understand the primary mechanic without written explanation.
- Bank shots are reliable.
- Large cluster drops feel more rewarding than basic matches.
- Audio remains tolerable and entertaining across repeated sessions.
- No logical board corruption occurs in automated stress testing.
- Golden replays hash identically on at least two device classes (§24.3).
- The game resumes correctly after backgrounding.
- The named reference device (§24.1) maintains target performance.
- A full session can be played with one hand.
- All included assets are original or properly licensed.

---

## 26. Minimum Viable Product

### 26.1 MVP content target

Recommended:

- Three environments
- Forty-five to sixty campaign levels
- Endless mode
- Fossil Excavation mode
- Daily Eruption
- Three launcher dinosaurs
- One spotter dinosaur
- Four hatchling variants
- Six standard egg colors available across progression
- Five special egg types (Wild, Blast, Crack, Swap, Anchor — §9.2)
- Three hazard egg types
- Habitat system
- Game Center achievements and leaderboards
- One-time full-game unlock with defined free tier (§18.1)
- English localization (voice is locale-independent by design, §12.4)
- Accessibility baseline
- Local and optional cloud save

### 26.2 MVP release criteria

> **Changed in v1.1 (H-5).**

- All primary modes complete
- No critical or high-severity gameplay defects
- Stable entitlement handling, including refund/revocation paths (§23.1)
- Store assets complete
- Privacy disclosures complete, **including privacy manifest (`PrivacyInfo.xcprivacy`) and required-reason API audit for the app and all embedded SDKs**
- Legal and trademark review complete (per the §30.2 schedule — substantially before this point)
- Accessibility audit complete
- Device compatibility matrix passed
- Crash-free rate meets release threshold (§3.2)
- Audio, music, and voice licensing documented
- App Review package prepared

---

## 27. Milestones

### Milestone 0 — Discovery and Prototyping

Deliverables:

- Paper gameplay rules
- Touch-control prototype
- Hex-grid model prototype (fixed-point math, §20.2, including anchor-row insertion, §7.6)
- Shot and attachment tests
- IP clean-room inventory
- Art style exploration
- Audio tone exploration
- Technical risk register
- Named reference device and minimum iOS version (§24.1)

> **Changed in v1.1 (H-1):** exit condition extended — the previously open core-design decisions are now M0 exit blockers.

Exit conditions:

- Core shot, attachment, match, and detachment loop is demonstrably viable.
- **Danger mechanic confirmed or replaced** (Open Decision #10 closed against the §7.6 working design).
- **Visual style direction selected** (Open Decision #11 closed).
- **Voice tone confirmed** against the §12.4 non-verbal direction (Open Decision #12 closed).

### Milestone 1 — Vertical Slice

Deliverables:

- Complete vertical-slice scope
- Internal playtest build
- Basic telemetry
- Accessibility baseline
- Performance profile
- Replay logs

Exit condition:

- Core experience is fun, readable, and stable enough to justify full production.

### Milestone 2 — Production Foundation

Deliverables:

- Final architecture
- Content pipeline
- Level authoring format
- Save system
- Entitlement framework (including Family Sharing decision, §18.1)
- Game Center integration
- Audio pipeline
- Localization pipeline
- Premium price validated against market benchmarks; Apple Arcade evaluation complete (§5.4)

Exit condition:

- Team can create levels and content without core code changes.

### Milestone 3 — MVP Content Production

Deliverables:

- Campaign content
- Endless tuning
- Fossil Excavation content
- Daily challenge system
- Characters
- Habitats
- Final audio and music
- Store flow

Exit condition:

- Feature-complete build.

### Milestone 4 — Alpha

Focus:

- Functional completeness
- Progression tuning
- Device coverage
- Save reliability
- Accessibility
- Content balance

Exit condition:

- No unresolved architecture or content-pipeline blockers.

### Milestone 5 — Beta

Focus:

- Stability
- Performance
- Monetization validation
- App Store compliance (including privacy manifest, §26.2)
- Localization
- Analytics validation
- Legal review (final confirmation; substantive review completed earlier per §30.2)

Exit condition:

- Release candidate eligibility.

### Milestone 6 — Launch

Deliverables:

- Production build
- Store listing
- Privacy documentation
- Support workflow
- Crash and telemetry monitoring
- Release notes
- Post-launch backlog

---

## 28. Team Roles

Minimum recommended roles:

- Product owner
- Game designer
- iOS/gameplay engineer
- UI engineer or generalist
- 2D artist/animator
- Sound designer
- Composer
- Voice director/performers
- Level designer
- QA/test engineer
- Legal advisor for trademark, licensing, privacy, and clean-room review

Smaller teams may combine roles, but gameplay engineering, art, audio, and testing must each have explicit ownership.

---

## 29. Risks and Mitigations

### 29.1 Clone perception and total-concept-and-feel exposure

> **Changed in v1.1 (L-1):** risk restated — the exposure is the *arrangement* of expressive elements, not only copied assets.

**Risk:** The game is perceived — by players, press, or a rights holder — as a copy of an existing title. Case law (*Tetris Holding v. Xio*; *Spry Fox v. LOLApps*) shows a cloned arrangement of expressive elements can infringe even with fully original assets.

**Mitigation:**

- Original brand, UI, characters, animation, sound design, and level structures
- Mechanically prominent differentiators **in the vertical slice itself** (fossils, habitats, hazard eggs, daily seeds, nest-insertion danger system) — not only on paper
- Spotter/announcer persona and function designed to visibly diverge from any predecessor's announcer (§10.1); non-verbal voice identity (§12.4)
- Documented clean-room development process
- External legal review completed **before public announcement** (§30.2)
- No predecessor references in any public copy (§30.1)

### 29.2 Weak differentiation

**Risk:** The game is dismissed as a generic bubble shooter.

**Mitigation:**

- Reactive nest presentation
- Cluster-drop emphasis
- Dinosaur abilities
- Hatchling rescue
- Fossil objectives
- Dynamic audio escalation
- Daily deterministic challenges
- Habitat progression

### 29.3 Repetitive audio

**Risk:** Voice lines and effects become irritating.

**Mitigation:**

- Non-verbal vocalization (inherently more repetition-tolerant, §12.4)
- Multiple vocalization pools
- Playback cooldowns
- Context-aware triggers
- Voice frequency option
- Independent volume controls
- Broad effect variation
- Repetition testing over long sessions

### 29.4 Collision frustration

**Risk:** Shots feel inconsistent or unfair.

**Mitigation:**

- Deterministic fixed-point collision model (§20.2)
- Explicit snap rules
- Debug trajectory visualization
- Extensive edge-case tests
- Optional full trajectory assist
- Consistent wall-bounce behavior

### 29.5 Content production cost

**Risk:** Authored levels and animation exceed team capacity.

**Mitigation:**

- Data-driven content
- Reusable animation rigs
- Small initial character roster
- Limited environment count
- Strong level-authoring tools
- Vertical-slice validation before content expansion

### 29.6 Scope expansion

**Risk:** Habitats, progression, and online systems delay the core game.

**Mitigation:**

- Vertical-slice gate
- MVP feature freeze
- Explicit non-goals
- Separate post-launch backlog
- No multiplayer before validated demand

### 29.7 Device fragmentation

**Risk:** Effects and audio perform poorly on older hardware.

**Mitigation:**

- Early testing on the named reference device (§24.1)
- Scalable effect quality
- Particle budgets
- Audio voice limits
- Sprite atlas discipline
- Memory profiling

### 29.8 Market risk: premium product in a free-to-play genre

> **Added in v1.1 (H-3).**

**Risk:** The audience for bubble-shooter-style games overwhelmingly expects free-to-play; a paid unlock may fail to convert regardless of quality, and organic discovery of premium mobile games is weak.

**Mitigation:**

- Generous free tier including daily-challenge practice (§18.1)
- Go-to-market thesis and Apple featuring pitch built on the non-predatory model (§5.4)
- Price point validated against premium-puzzle benchmarks before Milestone 3
- Apple Arcade evaluated as an alternative channel (§5.4)
- Soft-launch conversion data reviewed before global rollout

### 29.9 Platform risk: SpriteKit maintenance mode

> **Added in v1.1 (M-4).**

**Risk:** SpriteKit receives minimal ongoing investment from Apple and has no visionOS path; a future deprecation or platform shift would strand the presentation layer.

**Mitigation:**

- `GameCore` is renderer-agnostic by mandate (§20.2); all gameplay logic survives a renderer swap
- Presentation code isolated in `GamePresentation` (§20.3)
- Re-evaluate renderer options at each major post-launch platform decision (§32.2)

---

## 30. IP, Legal, and Clean-Room Requirements

### 30.1 Prohibited material and language

> **Changed in v1.1 (L-2):** marketing-language rule made absolute.

The project must not use:

- Third-party source code
- Decompiled binaries
- Extracted art
- Extracted audio
- Existing voice lines
- Existing level files
- Existing UI assets
- Existing fonts unless separately licensed
- Existing logos or names
- Marketing copy suggesting affiliation
- Character designs that create confusing similarity

**Public-language rule (absolute):** no public-facing material — store copy, press kits, social posts, interviews, App Review notes — may reference any predecessor title or use framing such as "spiritual successor," "remake," "inspired by [title]," "unofficial sequel," or comparable language. "Clean-room spiritual successor" is internal process vocabulary only; in public it functions as an admission that invites exactly the claim the process is designed to prevent.

### 30.2 Required controls

> **Changed in v1.1 (L-2):** legal review re-sequenced to before public announcement.

- Maintain a source and license register for every asset.
- Store proof of license for third-party tools and libraries.
- Require original-contribution declarations from contractors.
- Keep inspiration references separate from production assets.
- Review names and logos before public announcement.
- Conduct trademark screening **before any public announcement or external playtest**, not merely before final naming.
- Complete substantive external legal review (trademark, trade dress, total concept and feel) **before public announcement**; final confirmation pass before App Store submission.
- Avoid advertising the product as a port, remake, or unofficial sequel (see §30.1 public-language rule).

### 30.3 Clean-room documentation

Maintain:

- Product requirements
- Original gameplay specifications
- Original art briefs
- Original audio briefs
- Original level-design rules
- Asset provenance
- Contributor agreements
- Dependency inventory
- Trademark review notes
- Release approval record

---

## 31. Security and Supply Chain

### 31.1 Requirements

- Pin dependency versions.
- Minimize external packages.
- Generate a software dependency inventory.
- Review package licenses.
- Protect signing credentials.
- Use least-privilege access for App Store Connect.
- Separate development, test, and production service credentials.
- Avoid embedding secrets in the application.
- Validate remote configuration.
- Sign and verify downloadable content if introduced.
- Maintain reproducible release procedures.

### 31.2 Backend minimization

> **Changed in v1.1 (C-3):** aligned with the §15.3 launch decision.

The launch product ships without a custom backend. Platform services cover:

- Leaderboards (best-effort integrity at launch, per §15.3)
- Achievements
- Entitlements
- Cloud save

A custom backend is a **post-launch option**, with server-side replay verification of ranked scores (enabled by the §20.5 replay log) as its first candidate feature, followed by cross-platform identity or live operations if validated demand appears.

---

## 32. Release and Operations

### 32.1 Operational requirements

- Crash reporting
- Performance monitoring
- Purchase failure monitoring
- Leaderboard submission monitoring
- Support contact path
- Privacy request process
- Save recovery guidance
- Release rollback plan
- Feature-flag controls for online features

### 32.2 Post-launch priorities

Recommended sequence:

1. Stability fixes
2. Difficulty and economy tuning
3. Additional authored levels
4. New character
5. New habitat
6. New special egg (Echo Egg is first candidate, §9.2)
7. Expanded daily challenge modifiers
8. Server-side replay verification for ranked leaderboards, if cheating becomes player-visible (§31.2)
9. Additional localization (text-only, by design — §12.4)
10. iPad-specific presentation improvements and multitasking decision (§19.1)
11. Evaluation of other Apple platforms

---

## 33. Acceptance Criteria Summary

The product is acceptable for launch when:

- Core gameplay is deterministic, shot-indexed, and stable (§6.2).
- Golden replays hash identically across the supported-device matrix (§24.3).
- Touch controls are predictable.
- Aiming works one-handed.
- Board state never depends on animation timing.
- Matches and detachments resolve correctly.
- Audio and haptics communicate gameplay state.
- Accessibility options are functional.
- Offline play works for all core modes.
- Saves migrate safely; cloud conflicts merge field-wise (§23.3).
- Purchases restore reliably, including refund/revocation handling (§23.1).
- Leaderboard scores follow the documented ruleset and integrity posture (§15.3).
- The visual and audio identity is original.
- All assets have documented provenance.
- Trademark and legal review are complete per the §30.2 schedule.
- Privacy manifest and required-reason API declarations are complete and accurate (§26.2).
- App Store submission materials are complete.
- The release candidate passes the supported-device matrix.

---

## 34. Open Product Decisions

> **Changed in v1.1 (H-1, H-5, C-4):** decisions re-sequenced with owners of a deadline; former decisions 10–12 are now Milestone 0 exit blockers; Family Sharing added; free-tier boundary and Kids-Category decisions closed by this revision.

**Milestone 0 exit blockers:**

1. Minimum supported iOS version and named reference device (§24.1)
2. Danger mechanic — confirm or replace the §7.6 working design
3. Final visual style
4. Voice tone — confirm the §12.4 non-verbal direction

**Before Milestone 2:**

5. Final product name (after trademark screening, §30.2)
6. Exact unlock price (validated per §5.4)
7. Whether cloud save ships in MVP
8. Family Sharing for the unlock (§18.1)
9. Analytics provider or analytics-free alternative (§22)
10. Apple Arcade pitch go/no-go (§5.4)

**Before Milestone 3:**

11. Campaign level count at launch
12. Daily challenge attempt policy (attempts per day for ranked)
13. Canonical daily reset time (recommended 00:00 UTC, §8.4)
14. Whether habitat customization ships in MVP or first update
15. Final character roster
16. Final special egg roster
17. Localization launch scope (text-only per §12.4)

**Closed by this revision:** free-tier boundary (§18.1), Kids Category (no — §5.3), Echo Egg in MVP (no — §9.2), iPad multitasking at launch (no — §19.1), leaderboard integrity posture (best-effort — §15.3).

---

## 35. Recommended Immediate Next Steps

1. Approve the working title only as an internal placeholder.
2. Name the reference device and minimum iOS version (§24.1).
3. Build a no-art interaction prototype for aiming, bouncing, attachment, matching, cluster detachment, **and anchor-row insertion** — in fixed-point math from day one (§20.2, §7.6).
4. Create a clean-room asset and dependency register.
5. Produce three distinct art-direction boards.
6. Produce an audio prototype containing launch, impact, match, drop, combo, and danger sounds, plus non-verbal vocalization tests (§12.4).
7. Test the core loop on the reference device before expanding scope.
8. Define the vertical-slice backlog and acceptance tests, including the golden-replay suite (§24.3).
9. Conduct trademark screening and begin the external legal review **before any external branding or announcement** (§30.2).
10. Establish a level-definition format and deterministic replay schema.
11. Begin structured playtesting as soon as the first ten levels are playable.

---

## 36. Product Decision Record

The following direction is approved for planning:

- Dinosaur theme retained
- Egg-launching color-match gameplay retained at the concept level
- Fun, expressive **non-verbal** sound effects and voice reactions treated as a core product requirement (§12.4)
- All branding, characters, art, audio, UI, levels, and implementation created independently
- Portrait-oriented iOS-first product
- Native Swift, SwiftUI, and SpriteKit architecture with renderer-agnostic core (§20.2)
- Shot-indexed deterministic game model with fixed-point arithmetic (§6.2, §20.2)
- One-handed touch controls
- Clean-room development process (internal language only — §30.1)
- Free download with one-time full-game unlock and defined free tier (§18.1)
- General-audience positioning; not Kids Category (§5.3)
- No forced advertisements
- No energy timers
- No pay-to-win systems
- Offline-first design
- Game Center integration; leaderboards best-effort at launch (§15.3)
- Accessible controls and feedback
- Vertical slice required before full production
- Legal review before public announcement (§30.2)

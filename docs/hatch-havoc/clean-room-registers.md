# Hatch Havoc — Clean-Room Asset Register & Dependency Inventory

**Status:** Milestone 0 deliverable (PRD v1.1 §35 step 3; controls per §30.2, §31.1)
**Owner:** Product owner (entries added by whoever introduces the asset/dependency)
**Review:** every entry verified at each milestone exit; full audit before
public announcement and again before App Store submission (§30.2)

## Rules of use

1. **Every** production asset (art, audio, voice, font, level, name, logo,
   marketing copy) gets a register entry **before** it enters the repository
   or a build. No entry, no merge.
2. Contractors sign the original-contribution declaration (§30.2) before
   their first delivery; the declaration id is referenced by their entries.
3. Inspiration/reference material lives **outside** the production
   repositories and build pipeline (§30.2) and is never listed here — this
   register holds production assets only.
4. Third-party code enters only via the dependency inventory, license-reviewed
   first (§31.1). Default posture: no new dependencies (the reference core is
   stdlib-only by design).
5. "Provenance" must name a person and a creation method. "Found online" is
   not provenance; such an asset is quarantined and removed.

## Asset provenance register

| ID | Asset | Type | Created by | Method / tool | Date | Declaration | License (if external) | Status |
|----|-------|------|-----------|---------------|------|-------------|----------------------|--------|
| A-0001 | Hatch Havoc PRD v1.1 | document | project team | original writing | 2026-07-20 | n/a (internal) | n/a | active |
| A-0002 | Gameplay rules spec (`docs/hatch-havoc/gameplay-rules.md`) | document | project team | original design | 2026-07-20 | n/a (internal) | n/a | active |
| A-0003 | Example levels `ref-001`, `ref-002` | level data | project team | original authoring | 2026-07-20 | n/a (internal) | n/a | active |
| A-0004 | "Hatch Havoc" working title | name | project team | original; **internal placeholder only — trademark screen pending (§34)** | 2026-07-20 | n/a | n/a | placeholder |

*(No art, audio, voice, or font assets exist yet. First entries are due with
the art-direction boards and audio prototype — PRD §35 steps 4–5.)*

## Dependency inventory

| ID | Dependency | Version | Scope | License | License proof stored | Approved by | Status |
|----|-----------|---------|-------|---------|----------------------|-------------|--------|
| D-0001 | Python 3.11 standard library | 3.11 | reference prototype only (never ships) | PSF-2.0 | python.org/psf/license | project team | active |
| D-0002 | Apple platform SDKs (Swift, SwiftUI, SpriteKit, AVAudioEngine, Core Haptics, GameKit, StoreKit 2, XCTest) | per Xcode release | product | Apple SDK agreement | Apple Developer Program agreement | project team | planned |

*(PRD §31.1: pin versions, minimize external packages. Any proposed
third-party Swift package requires an entry here with license review before
first import.)*

## Contractor declaration log

| Declaration ID | Contributor | Role | Signed | Covers |
|----------------|-------------|------|--------|--------|
| *(none yet)* | | | | |

## Audit log

| Date | Auditor | Scope | Result |
|------|---------|-------|--------|
| 2026-07-20 | project team | initial register creation | no third-party assets present |

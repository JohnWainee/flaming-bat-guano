# Task System & Sonnet ⇄ Codex Handoff Protocol

This directory is the execution plan for the remaining phases of the ServiceNow
LLM Assistant. Each task is a self-contained markdown file that **one Sonnet-tier
agent can execute end-to-end**, then hand to **Codex for an LLM-security
red-team**, and get back for fixes.

Tasks are the source of truth for *what* to build and *whether it's done*. They
are committed to git so the two agents — which do **not** share a session or
memory — coordinate purely through file state + the handoff log.

---

## Roles

| Role | Agent | Responsibility |
|---|---|---|
| **Builder** | Claude (Sonnet) | Implement the task, write/extend unit tests, run the suite, self-check acceptance criteria, then hand off. |
| **Red Team** | Codex | Independently attack the result (LLM-security focus, see below), file findings in the task, return it. Does **not** implement features. |
| **Fixer** | Claude (Sonnet) | Address red-team findings, re-run tests, hand back for re-check or close. |

Author and adversary are deliberately different agents. The Builder never marks
its own LLM-surface task `done` — only a clean red-team pass closes it.

---

## Task lifecycle

```
todo ──▶ in_progress ──▶ ready_for_redteam ──▶ red_teaming ──┐
 ▲            (Sonnet)         (Sonnet sets)      (Codex)     │
 │                                                            ▼
 └──────── changes_requested ◀───────────────────────── (findings?) ──▶ approved ──▶ done
              (Codex sets)                                   yes            no        (Sonnet)
                  │
                  ▼
             in_progress (Sonnet fixes, loops back to ready_for_redteam)

blocked ── any state can move here; record the blocker + who owns unblocking.
```

The `status` field in each task's front matter is authoritative. Whoever changes
status **must** append a dated entry to that task's `## Handoff Log`.

---

## Handoff mechanics (how a task physically passes between agents)

There is no shared runtime. Coordination is git.

1. **Builder (Sonnet)** picks a task whose `depends_on` are all `done` and whose
   `status: todo`. Sets `status: in_progress`, adds a log entry, commits.
2. Builder implements, writes tests, runs `python -m pytest tests/ -v`, checks
   every box in **Acceptance Criteria**, fills the **Test Evidence** block, sets
   `status: ready_for_redteam`, commits, pushes.
3. **Red Team (Codex)** pulls, finds `status: ready_for_redteam`, sets
   `status: red_teaming`, works the **Red-Team Checklist**, and records results
   in **Red-Team Findings**:
   - Clean → `status: approved`.
   - Findings → `status: changes_requested`, one numbered finding per issue with
     severity + repro + suggested direction.
   Commits, pushes.
4. **Fixer (Sonnet)** pulls `changes_requested`, addresses each finding (or
   rebuts it in the log with rationale), sets `status: ready_for_redteam`,
   commits, pushes. Loop until `approved`.
5. **Builder (Sonnet)** flips `approved → done` only after tests are green on the
   final state and the **Definition of Done** holds. Commits.

> **Whoever writes, pulls first.** Both agents rebase on the shared branch before
> editing a task file to avoid clobbering the other's log entry.

---

## Definition of Ready (a task may be started when…)

- All `depends_on` tasks are `status: done`.
- Scope, files, and acceptance criteria are unambiguous (no open design calls —
  if one appears mid-task, set `blocked` and escalate to the human, don't guess).

## Definition of Done (a task may close when…)

- All acceptance-criteria boxes checked.
- Unit tests added/updated; **full suite green**; count recorded in Test Evidence.
- Live-validation steps either executed (evidence recorded) or explicitly
  deferred with the gating reason (missing creds/env) noted.
- For LLM-surface tasks: red-team `approved` with no unresolved High/Critical
  findings.
- Docs touched where behavior/config changed (`CLAUDE.md`, `.env.example`).

---

## Red-Team: LLM-security scope

Per project decision, red-teaming targets **LLM security**, not general QA. Every
**LLM-surface task** (anything that puts model output, retrieved content, or user
text on a path to an action, a reply, or another user) carries a Red-Team
Checklist drawn from this canonical list, plus task-specific cases:

- **RT-1 Direct prompt injection** — user message (Teams/email body) attempts to
  override the system prompt: change ticket type/fields, force-escalate
  urgency/impact, auto-confirm submission, or inject attacker text into SNOW work
  notes/description.
- **RT-2 Indirect / stored injection** — malicious content embedded in historical
  tickets retrieved by vector search influences trend analysis, similar-ticket
  suggestions, or any analyst-facing summary.
- **RT-3 Data exfiltration** — coaxing the assistant to reveal another user's
  conversation state, other tickets, the system prompt, or environment/secrets.
- **RT-4 PII / cross-tenant leakage** — sensitive data echoed into replies, logs,
  or written into the wrong ticket/record.
- **RT-5 Tool / API abuse** — crafted input that causes unintended SNOW writes
  (e.g. `requested_for` spoofing, arbitrary PATCH), SSRF via constructed URLs, or
  unbounded API/LLM call volume.
- **RT-6 Identity / isolation** — user_id spoofing in group chats; forged email
  `From` creating tickets as someone else; conversation-state bleed across users.
- **RT-7 Output-handling** — model output rendered as trusted markup/links, or
  parsed as JSON without validation, enabling injection downstream.

**Non-LLM-surface tasks** (pure infra: K8s, HPA, Prometheus wiring) skip the LLM
checklist and instead carry **Security-Review Criteria** (secrets never in
images/logs, least-privilege RBAC, network policy, no plaintext creds). Each task
declares which mode it's in via `redteam: llm-surface | security-review`.

### Red-team method (Codex)

For LLM-surface tasks, prefer **codified adversarial tests** over manual probing
so findings are regression-proof: add cases under `tests/redteam/` (mock the LLM
where a deterministic assertion is possible; gate live-fire cases on creds).
Manual live-fire probes are recorded in the findings with transcripts.

---

## Conventions

- **Filename**: `tasks/phase-<N>/<NN>-<slug>.md`, `NN` ordering within a phase.
- **Branch**: all work stays on `claude/funny-johnson-ktstpu` unless the human
  says otherwise.
- **Commits**: reference the task id, e.g. `P2-01: render adaptive card on CONFIRM`.
- **One concern per task.** If a task grows a second concern, split it and add a
  `depends_on`.
- **Cross-phase deps** are allowed; reference by path in `depends_on`.
- New task → copy `_TEMPLATE.md`.

See `_TEMPLATE.md` for the exact file shape. Three worked examples ship in this
first drop: `phase-2/00-reland-chgprb-ews.md` (integration/re-land),
`phase-2/01-teams-adaptive-card-confirm.md` (LLM-surface feature, full red-team),
and `phase-4/05-rate-limiting-dead-letter.md` (infra, security-review mode).

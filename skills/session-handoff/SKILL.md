---
name: session-handoff
description: Comprehensive handoff documents for seamless Shannon session transfers. ALWAYS use when the user says "session handoff", "save session state", "context handoff", "next session pick up here", "out of context window", "hand off this work", or when a long-running autopilot/loop exhausts context. Captures critical files, decisions, gotchas, modified files, branch state, and validates secrets/staleness before saving.
triggers:
  - "session handoff"
  - "save session state"
  - "context handoff"
  - "next session pick up here"
  - "out of context window"
  - "hand off this work"
  - "continue in fresh context"
---

# session-handoff

Captures the durable state of a long-running session into a single artifact that a fresh agent can pick up without ambiguity. The canonical solution to context-window exhaustion in autonomous loops.

This is the cross-session continuity primitive Shannon previously lacked. Used by `autopilot-runner` and `loop-runner` when a run nears its turn budget without convergence and needs to continue in a fresh context.

## When to use

- Active session is near context window saturation and work is incomplete.
- Pausing autopilot/loop overnight or across days.
- Switching from one human reviewer to another mid-task.
- Closing out a working day with a half-done feature.
- User says "hand off this work" / "save this for tomorrow."

## When NOT to use

- The work is actually done — close the session, don't hand off.
- The session is fresh and has plenty of context left — premature handoff is overhead.
- The information would fit in a single sentence — just write a one-line memory with `memorize`.

## The handoff document

Each handoff is one file at:

```
.claude/handoffs/YYYY-MM-DD-HHMMSS-<slug>.md
```

The slug is a kebab-case summary (`login-flow-rate-limiter-debug`).

### Required sections

```markdown
---
name: <slug>
description: <one-line summary>
created: <ISO timestamp>
session_id: <SDK session_id if any>
run_id: <autopilot/loop run-id if any>
continues_from: <prior handoff slug, if chained>
score: <0-100 from the validator script>
---

# Handoff: <slug>

## Goal
<one-paragraph statement of what the next session must accomplish>

## Critical files
<files the next session must read first, with one-line per-file purpose>

## Key patterns discovered
<insights from this session that the next session shouldn't relearn>

## Potential gotchas
<traps that bit this session and will bite the next>

## Modified files (in this session)
<git status output OR a manual list>

## Recent commits
<git log -10 --oneline output>

## Branch state
<current branch name; whether dirty; any in-progress merges>

## Open questions
<things the next session needs to decide or ask the user>

## Recommended next step
<the single most useful action the next session should take first>

## Resume protocol
<if a /goal or autopilot was active: which command + run-id to resume>
```

### Optional sections

- **Failed attempts** — what was tried, why it didn't work. Borrowed from `progress.txt` of ralph loops.
- **Stall fingerprint** — if the prior session was on the verge of `STALLED_SAME_FAILURE`, record the fingerprint.
- **External deps** — environment, services, accounts the work depends on.

## Validation script

Every handoff runs through `scripts/validate_handoff.py` before save. The validator:

1. **Secret-scan** — regex pass for API key patterns (`AKIA*`, `sk-*`, `ghp_*`, `xoxb-*`), password patterns, JWT tokens. Refuse on hit.
2. **Completeness** — required sections present, no `<TODO>` placeholders.
3. **Score** — 0-100 quality score based on:
   - +10 each for the 8 required sections (= 80 max)
   - +10 for at least one entry in `Critical files`
   - +10 for at least one entry in `Recent commits` OR `Modified files`
4. **Refuse if score < 70.** Below threshold = thin handoff = next session will struggle.

## Chaining

When a series of handoffs span multiple sessions:

```yaml
continues_from: 2026-05-26-180000-login-flow-debug
```

The chain is reconstructable: next session reads the current handoff, then can walk backward via `continues_from` to see the full arc.

This is the cross-session analog of a ralph loop's `progress.txt`.

## Staleness

Handoffs older than 7 days print a warning when read. Older than 30 days are flagged as `STALE`. The `consolidate-memory` skill (run periodically) prunes very stale handoffs that weren't chained-into.

## /shannon:handoff command

`/shannon:handoff "<slug>"` — produces the handoff. Reads git state, runs the validator, saves to `.claude/handoffs/`, prints the resume command for the next session.

`/shannon:handoff --resume <slug>` — reads the latest handoff (or named one), surfaces the resume command, and primes the next session with the critical files and the recommended next step.

## Iron rules

- **Secret-scan is mandatory.** Refuse to save on hit. Refuse hard — don't ask "include anyway?"
- **Score >= 70 required.** Thin handoffs are worse than no handoff.
- **One handoff per session-end.** Don't litter with partial saves.
- **Chain explicitly.** `continues_from` is the only correct way to link.
- **No mutation.** Handoffs are append-only artifacts; new state = new file.
- **Resume protocol is recorded.** If a `/goal` or autopilot was active, the resume command is in the handoff.

## Cross-references

- `skills/memorize/SKILL.md` — for atomic patterns; handoffs are session-state, memories are patterns
- `skills/consolidate-memory/SKILL.md` — periodic staleness pruning
- `skills/autopilot-runner/SKILL.md` — produces handoffs on context-near-exhaustion
- `skills/loop-runner/SKILL.md` — same
- `skills/python-agent-sdk/SKILL.md` — `session_id` persistence used by Resume protocol
- `skills/observability-report/SKILL.md` — reads handoffs as part of retro/audit

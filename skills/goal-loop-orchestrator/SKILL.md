---
name: goal-loop-orchestrator
description: Run a /goal condition to completion unattended with transcript-evidence Iron Rule, stall detection, turn/token budgeting, and headless-mode support. ALWAYS use when the user says "run /goal to completion", "headless run", "unattended turns", "transcript-evidence loop", "turn budget", "stall detection", or hands you a `/goal ...` line to execute.
triggers:
  - "run /goal to completion"
  - "headless run"
  - "unattended turns"
  - "transcript-evidence loop"
  - "turn budget"
  - "stall detection"
  - "execute a goal condition"
---

# goal-loop-orchestrator

Executes a `/goal` completion condition to terminal verdict — `SATISFIED`, `BOUND_REACHED`, or `STALLED` — and never lies about which one happened.

This is the **execution** half of the autonomy stack. The **input shaping** half is `goal-condition-architect`. The end-to-end facade is `northstar`.

## The Iron Rule

**The evaluator reads only the transcript. The evaluator runs no tools.**

Therefore, the orchestrator's single most important job is making sure the proving commands' outputs end up in the transcript verbatim. Every turn that claims progress must surface real-system output:

- `pytest -q` → final-line summary like `==== 14 passed in 1.32s ====`
- `wc -l src/auth/login.py` → numeric output
- `curl -w "%{http_code}"` → status code
- `git diff --shortstat` → `3 files changed, 47 insertions(+), 12 deletions(-)`

A claim like "ran the tests, all pass" without the actual command output is **NOT EVIDENCE** and the orchestrator refuses to count it.

## When to use

- A `/goal` condition exists (from `goal-condition-architect` or hand-authored).
- The user wants it to "just run until done."
- Headless mode / CI / overnight unattended.

## When NOT to use

- No `/goal` condition exists yet → run `goal-condition-architect` first.
- The condition isn't transcript-provable → reshape it, don't run it.
- The task needs human approval between steps → use interactive `/shannon:cook`.

## Preconditions

Before turn 1:

1. **Trust dialog accepted.** `~/.claude/settings.json` shows the project is trusted.
2. **Hooks not globally disabled.** `disableAllHooks` not set; per-hook overrides reviewed.
3. **Auto-mode decision confirmed.** Either user passed `--auto` or accepted interactive prompt.
4. **One goal per session.** If another `/goal` is active, decide replace-or-clear with the user first. Don't run two in parallel.
5. **Clean starting state.** Working tree at known SHA recorded for diffing later.

Any failure → don't start. Report which precondition blocked.

## The loop

```text
turn = 1
while turn <= bound:
    1. Take one action — usually a tool call that produces real output.
    2. Surface that output verbatim in the transcript.
    3. Run the evaluator: read the condition + last-N transcript turns.
    4. If evaluator says SATISFIED → exit SATISFIED, record run summary.
    5. If the same evaluator reason has repeated 3 turns in a row → STALLED.
    6. turn += 1

if turn > bound → exit BOUND_REACHED
```

## Stall detection

The evaluator's `reason` field is the convergence signal. If three consecutive turns have an identical or near-identical reason ("step X still failing because Y"), exit `STALLED`. Don't burn the turn budget.

Stall fingerprint = first 80 chars of evaluator reason. Persisted to `~/.claude/logs/shannon/goal-<run-id>/stall-log.jsonl`.

## Live status

`/goal` with no argument is the canonical UX. Reads the active run state and prints:

```
[/goal] condition: <one-line summary>
        elapsed: 14m12s   turns: 27/60   tokens spent: ~143k
        last evaluator reason: "test_login_flow still failing on assertion line 47"
        stall fingerprint count: 2/3
```

Shannon's `/shannon:autopilot status` mirrors this UX (see `autopilot-runner`).

## Bound + bound-rationale

Bound is required. Common shapes:

- `or stop after N turns` — most common.
- `or stop after N minutes` — for time-bounded SLAs.
- `or stop after N tool calls` — for cost-bounded runs.

The bound MUST be tied to a one-line rationale recorded in the run state file (`bound_rationale`). Without one, write the default `"caller did not supply rationale"` and print a warning. This is the audit trail for runaway-loop investigations.

## Headless mode

For CI/cron:

```bash
claude -p "/goal <condition>" --auto --max-turns 60 --output-format json
```

`--output-format json` emits one JSON line per turn so the CI driver can parse progress without re-reading the conversation.

## Diagnose-on-stall

When `STALLED`, write a one-page diagnosis to `plans/reports/goal-<run-id>-STALLED.md` containing:

- The condition.
- The fingerprint that repeated.
- The last 3 turns' transcripts.
- A one-line recommended next manual step.

The orchestrator does NOT auto-escalate or auto-rewrite the condition. Stall = stop = human.

## Iron rules

- **The transcript is the only evidence.** Claims without surfaced command output do not count.
- **The evaluator never runs tools.** It reads.
- **Bound is mandatory.** No unbounded runs.
- **Stall after 3 identical fingerprints.**
- **One `/goal` per session.** No parallel goals.
- **Preconditions checked before turn 1.**
- **Headless mode passes `--auto` explicitly.** Don't fall through to interactive prompts in CI.

## Cross-references

- `skills/goal-condition-architect/SKILL.md` — produces the condition this loop proves
- `northstar` — end-to-end facade
- `goal-workflow` — input → condition → run pipeline; ships `/goalify`
- `goal-orchestration` — deeper orchestration patterns
- `condition-library` — reusable conditions
- `skills/autopilot-runner/SKILL.md` — Shannon's broader multi-phase analog
- `skills/loop-runner/SKILL.md` — Shannon's bounded loop primitive
- `skills/python-agent-sdk/SKILL.md` — SDK harness for headless invocation


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `goal-orchestration`

# goal-orchestration

Operational depth for running `/goal` conditions. Where `goal-loop-orchestrator` is the loop itself, this is the patterns for monitoring, diagnosing, recovering, and tuning runs in production.

## The run state file

Every active `/goal` writes state to `~/.claude/state/goal/<run-id>/state.json`:

```json
{
  "run_id": "goal-2026-05-27-1430",
  "condition": "<full /goal line>",
  "started_at": "2026-05-27T14:30:00Z",
  "bound": {"shape": "turns", "limit": 60, "rationale": "4 features × 15 turns"},
  "current_turn": 27,
  "session_id": "<sdk session id>",
  "last_evaluator_reason": "test_login_flow still failing on assertion line 47",
  "stall_fingerprint": "test_login_flow still failing",
  "stall_count": 2,
  "tokens_spent_estimate": 143000
}
```

`/goal` (no arg) reads this and renders the live status. So does `/shannon:trace --goal`.

## Live monitoring

```
[/goal] condition: <one-line summary>
        elapsed: 14m12s   turns: 27/60   tokens spent: ~143k
        last evaluator reason: "test_login_flow still failing on assertion line 47"
        stall fingerprint count: 2/3
```

Key signals:

- **last evaluator reason** — the convergence indicator. If it's evolving, the loop is progressing. If it's static for 3 turns, stall imminent.
- **stall fingerprint count** — 2/3 means one more identical reason triggers `STALLED`.
- **tokens spent vs turns** — sudden spike per turn suggests context bloat; consider compacting or restarting.

## Diagnosing stalls

When `STALLED`, read `plans/reports/goal-<run-id>-STALLED.md`:

```markdown
# Goal STALLED: <run-id>

## Condition
<full /goal>

## Fingerprint that repeated
"test_login_flow still failing on assertion line 47"

## Last 3 turns
... (excerpts)

## Recommended next manual step
Open `tests/auth/test_login_flow.py:47` and inspect the assertion. The loop tried these three fixes — all failed:
1. Updated `src/auth/login.py` cookie scope (turn 25)
2. Changed `SameSite` flag (turn 26)
3. Added `Secure` flag (turn 27)
The pattern suggests the test expects a structure the implementation doesn't provide.
```

The orchestrator does NOT auto-rewrite the condition. Stall = stop = human attention.

## Tuning the turn budget

Common mistakes:

- **Too tight** — bound reached without convergence. Symptom: `BOUND_REACHED` on a condition that was making visible progress. Fix: raise bound, run again with `--resume`.
- **Too loose** — runs burn cost on hopeless conditions. Symptom: many runs hit STALLED but never the bound. Fix: lower bound or invest in a stricter `goal-condition-architect` pass.

Rule of thumb: bound = (number of distinct checks) × 10-15 turns. Adjust based on prior stall history for the codebase.

## Headless mode for CI

```bash
claude -p "/goal <condition>" \
  --auto \
  --max-turns 60 \
  --output-format json \
  > goal-run.jsonl
```

Then parse `goal-run.jsonl` per-line for live progress (each line is a turn event). On terminal verdict, the last line carries `{"verdict": "SATISFIED"|"BOUND_REACHED"|"STALLED", ...}`.

CI integration pattern:

```bash
verdict=$(jq -r '.verdict' < <(tail -1 goal-run.jsonl))
case "$verdict" in
  SATISFIED) echo "::notice ::goal satisfied"; exit 0 ;;
  BOUND_REACHED) echo "::warning ::bound reached"; exit 1 ;;
  STALLED) echo "::error ::stalled"; cat plans/reports/goal-*-STALLED.md; exit 1 ;;
esac
```

## Recovery patterns

| Verdict | Recovery |
|---|---|
| `BOUND_REACHED` with visible progress | Raise bound, `--resume` |
| `BOUND_REACHED` with no progress | Stop. Stall in disguise. Investigate. |
| `STALLED` | Read `STALLED.md`. Manual step. Then run again with refined condition. |
| Crashed (process died) | Check session_id in state file. Resume with `claude --resume <sid>`. |
| User interrupted | State file is current. Resume identically. |

## One goal per session

Don't run two `/goal`s in the same Claude Code session. They will fight over the evaluator. If the user wants concurrent autonomous work:

- Use separate terminals / separate sessions.
- Use Shannon's `dispatch-parallel` / `omc-teams` patterns with isolated worktrees.

## Iron rules

- **State file is the source of truth.** All monitoring reads it.
- **Stall = stop = human.** No auto-recovery on stall.
- **Bound is mandatory.** No exceptions.
- **Headless mode passes `--auto`.** No interactive prompts in CI.
- **Resume reuses session_id.** Don't start fresh on `--resume`.

## Cross-references

- `skills/goal-loop-orchestrator/SKILL.md` — the loop this skill operates
- `skills/goal-condition-architect/SKILL.md` — the input shape
- `goal-engineering` — depth on condition craft
- `condition-library` — reusable conditions
- `skills/observability-report/SKILL.md` — log-reading for completed runs
- `skills/python-agent-sdk/SKILL.md` — programmatic invocation

## Absorbed from `goal-workflow`

# goal-workflow

The end-to-end pipeline: any input → hardened `/goal` condition → unattended run → terminal verdict. Composes `goal-condition-architect` (input shaping) and `goal-loop-orchestrator` (execution). Ships `/shannon:goalify` as the user-facing slash command.

This is the top-of-funnel for the autonomy stack. Most users should start here, not at the individual skills.

## The four stages

### Stage 1 — Understand the input

Read whatever the user dropped:
- A voice ramble (transcribed)
- A PLAN.md / spec / PRD
- A ticket from Linear/Jira/GitHub
- The current conversation
- A rough description in the user's own words

Extract the end-state as a single sentence. If extraction fails, ask ONE clarifying question (per `goal-condition-architect`).

### Stage 2 — Architect the condition

Delegate to `goal-condition-architect`:
- Produce the four-part `/goal` (end-state, checks, constraints, bound).
- Adversarial-harden against the four standard attacks (echoed PASS, comment-out, fixture-ize, force-complete).
- Present the full condition to the user for confirmation.

**The user pastes the `/goal` line.** The workflow can't self-execute the `/goal` command — it presents it. This is by design: the user owns the moment of "yes, run this autonomously."

### Stage 3 — Orchestrate the run

Once the user confirms and runs `/goal <condition>`, delegate to `goal-loop-orchestrator`:
- Check preconditions (trust, hooks, auto-mode, lock, clean tree).
- Drive turns to terminal verdict (`SATISFIED`, `BOUND_REACHED`, `STALLED`).
- Surface live status via `/goal` no-arg.

### Stage 4 — Monitor & diagnose

The workflow's last job is helping the user interpret the result:
- `SATISFIED` → present the achievement record, point at the proving transcript lines.
- `BOUND_REACHED` → suggest either a higher bound or breaking the condition into sub-conditions.
- `STALLED` → read the `STALLED.md`, present the fingerprint, recommend the next manual step.

## The /shannon:goalify command

```
/shannon:goalify "<rough input>"
```

Runs stages 1-2 only. Outputs the hardened `/goal` line for the user to paste and run. Does not execute. Does not commit to anything.

```
/shannon:goalify --auto "<rough input>"
```

Runs stages 1-3. After the condition is approved (one-prompt confirmation if `--yes` is also passed), automatically runs `/goal` with the condition. This is the "I trust the architect, just go" path.

## Composition with Shannon's own commands

- `/shannon:interview` (`deep-interview`) is the front-end when input is too vague even for the one-clarifier rule. Use it before goalify.
- `/shannon:plan` (plan-author) is for when the work needs decomposition before a single `/goal` makes sense — multiple goals chained.
- `/shannon:autopilot` is the Shannon-native multi-phase analog. It uses goal-style transcript-evidence internally but doesn't expose `/goal` semantics directly.

## Iron rules

- **Stage 1 asks at most one clarifying question.** If still vague after that, recommend `/shannon:interview` and stop.
- **Stage 2 always runs the adversarial harden.** No condition is presented without it.
- **Stage 3 requires explicit user paste of `/goal`** (unless `--auto --yes`). The workflow doesn't sneak past consent.
- **Stage 4 always interprets the verdict.** Don't drop the user at `STALLED` without a recommended next step.

## Cross-references

- `skills/goal-condition-architect/SKILL.md` — stage 2 delegate
- `skills/goal-loop-orchestrator/SKILL.md` — stage 3 delegate
- `northstar` — alternative end-to-end facade with slightly different posture
- `goal-engineering` — patterns for crafting goal conditions
- `condition-library` — reusable condition templates
- `deep-interview` (oh-my-claudecode plugin) — front-end when input is too vague
- `skills/autopilot-runner/SKILL.md` — Shannon's multi-phase analog

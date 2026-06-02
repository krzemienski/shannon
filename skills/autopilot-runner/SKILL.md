---
name: autopilot-runner
description: Full-lifecycle autopilot orchestrator for /shannon:autopilot. ALWAYS use when the user says "autopilot", "run autonomously", "Spec→Plan→Execute→QA→Validate→Cleanup", "keep retrying until it works", or invokes /shannon:autopilot. Drives a six-phase lifecycle with stall detection, multi-perspective validation, SDK harness instrumentation, resume semantics, and transcript-evidence Iron Rule enforcement.
triggers:
  - "autopilot"
  - "run autonomously"
  - "Spec to plan to execute to QA to validate"
  - "keep retrying until it works"
  - "refusal-driven retry"
  - "autopilot lifecycle"
  - "/shannon:autopilot --resume"
---

# autopilot-runner

Skill that backs `/shannon:autopilot`. v1's autopilot is **full lifecycle**, not single-phase retry: it drives the canonical six-phase pipeline (Spec → Plan → Execute → QA → Validate → Cleanup) on top of a `ClaudeSDKClient` harness with stall detection, multi-perspective validation, preconditions gate, and Iron-Rule transcript-evidence enforcement.

This is in-scope for v0.1.x per the user-approved architecture.

## When to use

- User invokes `/shannon:autopilot` with a task description
- User says "run autonomously until done" / "set this up as an autopilot run"
- Long-running work where refusal-driven retry is preferred over manual oversight
- Pre-validated plans from `/shannon:cook` that should run end-to-end without human re-confirmation

## When NOT to use

- Single-pass execution → use `/shannon:cook` directly
- Exploratory task without success criteria → use `/shannon:loop` (loop-runner) instead
- Production deploys where refusal must escalate to a human gate → use `/shannon:gate` + manual approval
- Ambiguous requirements → run `/shannon:interview` (deep-interview) first

## Behavior contract — six phases

Autopilot drives one `ClaudeSDKClient` session through these phases in order. Each phase can be skipped if pre-validated input exists from `/shannon:cook` or a previous resumed run.

| Phase | Command | Pre-validation skip rule | Stall fingerprint key |
|---|---|---|---|
| 1. Spec | `/shannon:spec` | `e2e-evidence/<run-id>/spec/spec.md` exists | first 80 chars of REFUSAL line |
| 2. Plan | `/shannon:plan` | `e2e-evidence/<run-id>/plan/plan.md` exists | failing MSC id |
| 3. Execute | `/shannon:cook` | n/a (always executes) | first failing MSC id |
| 4. QA | `/shannon:qa` (ultraqa-style) | QA passed last cycle in same run | failing test name |
| 5. Validate | multi-perspective (see below) | n/a (always validates) | failing perspective + reason |
| 6. Cleanup | `/shannon:cleanup` (ai-slop-cleaner) | clean tree | n/a |

Between every phase the harness writes the SDK `session_id` to `.shannon/state/autopilot-session.txt` so the run is resumable.

## Phase 5 — multi-perspective validation gate

Phase 5 is a v1 addition. Before COMPLETE can be declared, three reviewers must independently PASS in parallel:

1. `functional-validation` — real-system execution evidence
2. `judge` — secrets, auth paths, injection surfaces
3. `judge` — quality/architecture review (or `judge` with multi-perspective rubric)

All three verdicts persist to `e2e-evidence/<run-id>/validate/` as separate JSON reports. If any one is REFUSED, autopilot reads the union of cited blockers and synthesizes a remediation prompt — but the bound discipline applies (see below).

## Iron Rule: transcript-evidence

Inherited from `goal-loop-orchestrator`. **`verdict=COMPLETE` without surfaced command output is treated as REFUSED.**

The harness's post-tool hook checks: when a phase reports COMPLETE, the assistant message stream must contain the proving command's exit code or final-line summary verbatim within the same turn. If not, the harness rewrites the verdict to REFUSED with reason `iron_rule_no_transcript_proof`.

## Stall detection

Per `ralph` (3+ same failure) and `ultraqa` (same-failure-3x early exit):

- After each phase write a fingerprint to `e2e-evidence/<run-id>/stall-log.jsonl`:
  `{"phase": "qa", "verdict": "REFUSED", "fingerprint": "<first 80 chars of first cited blocker>"}`
- If the same `{phase, fingerprint}` pair appears three consecutive times across attempts, exit with `STALLED_SAME_BLOCKER`. Do not burn remaining attempts.
- Write `plans/reports/autopilot-<run-id>-STALLED.md` enumerating the fingerprint history and a recommended next manual step.

## Preconditions gate

Before phase 1 of attempt 1, verify (from `python-agent-sdk` patterns):

1. `~/.claude/settings.json` does not set `disableAllHooks: true`.
2. No other autopilot run holds `~/.claude/locks/shannon-autopilot.lock`.
3. User has either passed `--auto` or has accepted an interactive confirmation.
4. The repo working tree is at a known SHA (record `git rev-parse HEAD` to the state file; refuse if the tree is dirty unless `--allow-dirty`).

If any precondition fails, exit immediately with `PRECONDITION_FAILED:<which>`. Do not attempt phase 1.

## Resume semantics

`/shannon:autopilot --resume <run-id>` reads `.shannon/state/autopilot-session.txt` and the run's phase log, then jumps to the first phase whose evidence dir is missing a PASS report. The SDK `options.resume = <session_id>` ensures the client picks up the same conversation.

If `--resume <run-id>` is passed but the run-id has no state file, exit with `RESUME_NO_STATE`.

## Remediation prompt bounding

From northstar's "adversarial harden" pattern + the audit's prompt-sprawl warning: synthesized remediation prompts are capped at **~2000 chars**.

- If REFUSAL.md cites ≤ 2 blockers: attack them all.
- If 3-4 blockers: attack the top 2 by severity, defer the rest.
- If > 4 blockers: this is a structural failure — stall-exit with `STALLED_TOO_MANY_BLOCKERS`.

Severity ranking, in order: security > correctness > evidence-missing > drive-by.

## SDK harness layer

Autopilot does NOT run as pure prompt orchestration. It runs as a Python entry point that wraps `ClaudeSDKClient` (see `skills/python-agent-sdk/SKILL.md`).

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher
from shannon.autopilot_harness import (
    PHASES, preconditions_ok, phase_already_complete, stalled,
    record_fingerprint, surface_iron_rule, write_state,
)

async def autopilot(run_id: str, task: str, max_attempts: int = 6):
    ok, why = preconditions_ok()
    if not ok:
        return {"verdict": "PRECONDITION_FAILED", "reason": why}

    options = ClaudeAgentOptions(
        setting_sources=["user", "project"],
        permission_mode="bypassPermissions",
        model="claude-opus-4-5",
        allowed_tools=["Skill", "Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        hooks={
            "PreToolUse":  [HookMatcher(matcher="*", hooks=[pre_tool_log])],
            "PostToolUse": [HookMatcher(matcher="*", hooks=[post_tool_log, surface_iron_rule(run_id)])],
        },
    )

    async with ClaudeSDKClient(options=options) as client:
        for attempt in range(1, max_attempts + 1):
            for phase in PHASES:
                if phase_already_complete(run_id, phase):
                    continue
                await client.query(phase_prompt(phase, run_id, task))
                async for msg in client.receive_response():
                    pass
                verdict = read_phase_verdict(run_id, phase)
                record_fingerprint(run_id, phase, verdict)
                write_state(run_id, client.session_id)
                if stalled(run_id, phase):
                    return {"verdict": "STALLED_SAME_BLOCKER", "phase": phase, "attempts": attempt}
                if verdict.startswith("REFUSED"):
                    break  # next attempt
            else:
                # All phases complete in this attempt
                return {"verdict": "COMPLETE", "attempts": attempt, "run_id": run_id}

        return {"verdict": "REFUSED", "attempts": max_attempts, "run_id": run_id}
```

The harness lives at `core/autopilot_harness.py`. The slash command (`commands/sh_autopilot.md`) invokes it via a small Python wrapper rather than running entirely as a prompt.

## State & evidence layout

```
.shannon/state/
  autopilot-session.txt          # current SDK session_id
  autopilot-run.txt              # current run-id
  
~/.claude/locks/
  shannon-autopilot.lock         # single-run lock; contains run-id + pid

e2e-evidence/<run-id>/
  spec/                          # /shannon:spec output
  plan/                          # /shannon:plan output
  cook/                          # /shannon:cook output
  qa/                            # /shannon:qa output
  validate/
    functional.json
    security.json
    oracle.json
  cleanup/                       # /shannon:cleanup output
  phase-log.md                   # ordered list of (attempt, phase, verdict)
  stall-log.jsonl                # one line per phase verdict for fingerprinting
  transcript.jsonl               # iron-rule proving outputs

plans/reports/
  autopilot-<run-id>-ACHIEVED.md # symmetric "what passed" record on COMPLETE
  autopilot-<run-id>-REFUSAL.md  # union of blockers on terminal REFUSED
  autopilot-<run-id>-STALLED.md  # written when stall-exit triggers
```

## /shannon:autopilot status

Live status (analog of `/goal` no-arg). Reads `.shannon/state/autopilot-run.txt`, the phase-log, and the last 100 lines of `~/.claude/logs/shannon/hooks.jsonl`. Prints:

```
[shannon:autopilot] run=<run-id> phase=qa attempt=2/6
  elapsed: 14m12s
  tools fired: 312 (last: Bash)
  last verdict: REFUSED — "test_login_flow failed at assertion line 47"
  fingerprint history: REFUSED:test_login_flow x2 / fresh
```

## Iron rules

- **Never invent COMPLETE.** Verdict must trace to a `validate/*.json` file that itself cites proving command output in the transcript.
- **Never override REFUSAL.md.** Read it, bound the remediation, retry.
- **No `--force-complete` flag. Ever.
- **Single autopilot run per host.** Lock at `~/.claude/locks/shannon-autopilot.lock`.
- **Stall after 3 identical fingerprints — do not burn remaining attempts.**
- **Remediation prompts ≤ ~2000 chars.** If > 4 blockers, structural-fail instead.
- **Phase 5 validation requires ALL three perspectives to PASS** (functional + security + oracle).
- **Session_id persisted after every phase** so resume always works.

## Cross-references

- `skills/python-agent-sdk/SKILL.md` — the SDK foundation this harness rides on
- `skills/loop-runner/SKILL.md` — lower-level loop primitive (single phase, repeated)
- `skills/goal-loop-orchestrator/SKILL.md` — the transcript-evidence loop discipline
- `skills/goal-condition-architect/SKILL.md` — how to write the success condition this autopilot proves
- `skills/functional-validation/SKILL.md` — Phase 5 perspective #1
- `Task: critic` (severity-rated security + correctness pass) — Phase 5 perspective #2
- `skills/judge/SKILL.md` — Phase 5 perspective #3
- `skills/refusal-discipline/SKILL.md` — REFUSAL.md format this consumes
- `skills/completion-gate/SKILL.md` — the gate that produces phase verdicts
- `skills/session-handoff/SKILL.md` — cross-session continuity when autopilot exhausts context


---

# Absorbed (Phase 1 aggressive merge)

Skills merged into this canonical survivor during Shannon v0.1.0 Phase 1 curation. Content preserved for Phase 2 canonical-merge work.


## Absorbed from `autopilot`

# autopilot

The doctrine behind `/shannon:autopilot`. The Shannon-native executor is `autopilot-runner`. This skill is the **why**; `autopilot-runner` is the **how**.

## The lifecycle, six phases

| Phase | Purpose | Skip rule | Verdict source |
|---|---|---|---|
| 1. Spec | Lock the success criteria | `e2e-evidence/<run>/spec/spec.md` exists | `spec.md` present + non-empty |
| 2. Plan | Decompose into MSC-shaped tasks | `e2e-evidence/<run>/plan/plan.md` exists | `plan.md` present + plan-author verdict |
| 3. Execute | Implement against the plan | always runs | `cook/report.json:verdict` |
| 4. QA | Test/build/lint/typecheck loop (ultraqa-style) | last QA cycle in same run PASSed | `qa/state.json:verdict` |
| 5. Validate | Multi-perspective parallel gate | always runs | `validate/functional.json` ∧ `validate/security.json` ∧ `validate/oracle.json` |
| 6. Cleanup | ai-slop-cleaner + re-verify | tree already clean | `cleanup/diff.txt` empty AND re-verify PASS |

The lifecycle is the **single most important conceptual addition** over single-phase retry. Without phase progression, autopilot can't "skip earlier phases if input is pre-validated."

## Skip-on-pre-validated-input

If `/shannon:cook` produced a hardened spec + plan and saved them to `e2e-evidence/<run>/spec/` and `.../plan/`, autopilot's first two phases are no-ops. The run skips to Execute. This is the bridge between interview/forge and autopilot.

The skip rule is **artifact-based**, not flag-based. Autopilot looks at the file system; if the evidence directory has a passing report, the phase is done.

## Multi-perspective validation (phase 5)

The single biggest gap in single-phase retry: trusting one completion-gate verdict.

Phase 5 fans out to three independent validators **in parallel** (single user message, three `Skill(...)` invocations):

1. **Functional perspective** — `functional-validation` skill. Real-system execution, evidence in transcript.
2. **Security perspective** — `judge` skill. Secrets, injection, authz boundaries.
3. **Quality/architecture perspective** — `judge` skill. Design, maintainability, test coverage gaps.

**All three must PASS** before phase 5 reports COMPLETE. Any REFUSED feeds into phase 5's REFUSAL.md.

This is the autopilot equivalent of `judge-with-debate` for validation: three perspectives, no quorum, all must agree.

## Stall detection across attempts

Same as ralph (3 identical fingerprints exit). Applied at the **attempt** level, not the iteration level — autopilot's attempts are entire lifecycle traversals. If the SAME phase fails with the SAME fingerprint across 3 attempts, exit `STALLED_SAME_BLOCKER`. Write `STALLED.md`.

## Preconditions gate

Before attempt 1 of phase 1, verify (see `goal-loop-orchestrator`):

- `~/.claude/settings.json:disableAllHooks` is not true
- `~/.claude/locks/shannon-autopilot.lock` not held
- User has accepted auto-mode (or passed `--auto`)
- Repo tree at a known SHA (refuse on dirty tree without `--allow-dirty`)

Any failure → exit `PRECONDITION_FAILED:<which>`. Never attempt phase 1 if preconditions fail.

## Resume semantics

`/shannon:autopilot --resume <run-id>` is explicit, not implicit.

1. Read `.shannon/state/autopilot-session.txt` — must match `<run-id>`'s session.
2. Read `e2e-evidence/<run-id>/phase-log.md` — pick the first phase without a PASS report.
3. Pass the session_id to `ClaudeSDKClient(options=ClaudeAgentOptions(..., resume=<sid>))`.
4. Begin from the chosen phase.

If state is missing → exit `RESUME_NO_STATE`. Don't restart from spec by surprise.

## Bounded remediation prompts

Synthesized remediation prompts are capped at ~2000 chars:

- ≤ 2 blockers: attack all.
- 3-4 blockers: attack top 2 by severity, defer the rest.
- > 4 blockers: structural failure — exit `STALLED_TOO_MANY_BLOCKERS`.

Severity order: security > correctness > evidence-missing > drive-by.

## Live status

`/shannon:autopilot status` (no run-id needed; reads `.shannon/state/autopilot-run.txt`):

```
[shannon:autopilot] run=<run-id> phase=qa attempt=2/6
  elapsed: 14m12s
  tools fired: 312 (last: Bash)
  last verdict: REFUSED — "test_login_flow failed at assertion line 47"
  fingerprint history: REFUSED:test_login_flow x2 / fresh
```

Mirrors `/goal` no-arg UX.

## Iron rules

- **Six phases in order.** Skip-on-pre-validated-input is allowed; out-of-order is not.
- **Phase 5 requires ALL THREE perspectives.** No quorum, no "2 out of 3."
- **Iron Rule of transcript-evidence applies per phase.** Proving command output must surface in the SDK message stream of the phase's turn.
- **Preconditions gate before attempt 1.**
- **Single autopilot run per host.** Lock file enforced.
- **Stall after 3 identical fingerprints.**
- **Remediation prompts ≤ ~2000 chars.**
- **Session_id persisted after every phase.**

## Cross-references

- `skills/autopilot-runner/SKILL.md` — Shannon's executor of this doctrine
- `skills/python-agent-sdk/SKILL.md` — SDK foundation
- `ralph` (oh-my-claudecode plugin) — loop doctrine each phase implicitly uses
- `skills/loop-runner/SKILL.md` — single-phase loop executor
- `skills/functional-validation/SKILL.md` — perspective #1
- `Task: critic` (severity-rated review) — perspective #2
- `skills/judge/SKILL.md` — perspective #3
- `skills/goal-condition-architect/SKILL.md` — how the success criteria are written
- `skills/goal-loop-orchestrator/SKILL.md` — transcript-evidence discipline
- `deep-interview` (oh-my-claudecode plugin) — front-end "spec" stage when input is vague
- `skills/session-handoff/SKILL.md` — cross-session continuity

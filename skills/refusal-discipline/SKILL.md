---
name: refusal-discipline
description: When evidence is missing, write a structured REFUSAL.md and stop. ALWAYS use when the user says "evidence gap", "missing citation", "gate unmet", "refusal needed", "block completion", or when a gate cannot be satisfied. No override flag, no force-complete; refusal is a feature, not a failure mode.
triggers:
  - "evidence gap"
  - "missing citation"
  - "gate unmet"
  - "refusal needed"
  - "block completion"
required_hooks:
  - evidence-gate
---

# refusal-discipline

The refusal pattern, codified. Shannon's contribution to the upstream skill catalog — refusal-as-artifact is a missing primitive in anthropic-skills v6 and an ADOPT candidate for upstream v7.

## Behavior contract

When invoked (typically by `completion-gate` or `evidence-gate` finding a blocker):

1. Construct REFUSAL.md with structured sections:
   ```markdown
   # REFUSAL — <run-id>
   **Date:** <ISO-8601>
   **Phase:** <phase that produced the refusal>

   ## Cited Blockers

   ### Blocker 1
   - **MSC:** <criterion name>
   - **Why refused:** <one-line reason>
   - **Evidence expected:** <path that should exist>
   - **Evidence actual:** <missing | zero-byte | content-not-matching-claim>
   - **Remediation:** <what would unblock>

   ### Blocker 2
   ...

   ## What was NOT done
   - <phases skipped because of refusal>

   ## How to retry
   - Run /shannon:cook <remediation prompt>
   - Or /shannon:autopilot <task> — refusal-driven retry loop
   ```
2. Write to `plans/reports/REFUSAL-<run-id>.md`.
3. Set TaskUpdate status appropriately (`in_progress` with note, NOT `completed`).
4. Return from the calling skill; HALT the pipeline.

## When to use

- `completion-gate` finds any unmet MSC.
- `evidence-gate` refuses on any of Q1–Q6.
- Validator finds FAIL it cannot reconcile.
- Oracle quorum returns REFUSE.
- Loop hits max-iter without convergence.

## When NOT to use

- Recoverable error (re-try the same step is fine).
- Warning-level finding (LOW severity).

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Quietly mark the task `in_progress` and move on without REFUSAL.md | The next run has no remediation prompt; the refusal becomes context loss | Always emit `REFUSAL.md` to `plans/reports/REFUSAL-<run-id>.md`; the file IS the remediation prompt source |
| Cite prose-only blockers ("the screenshot looked wrong") | A future `/shannon:autopilot` cannot retry a vague refusal | Cite specific evidence paths and the specific MSC the artifact failed to satisfy |
| Treat a SPLIT consensus as MAJORITY by averaging or omission | Silently downgrading consensus voids the gate | A SPLIT is a SPLIT; emit it as a blocker; do not let one reviewer's PASS overwrite another's FAIL |
| Add a `--force-complete` flag "for emergencies" | Emergencies are when discipline matters most; bypass becomes default | No override flag exists. If the user insists, document the user-requested deviation as a separate run, not as a gate bypass |
| Refuse without naming the remediation step | A refusal that can't be retried is a dead end | Every Blocker block ends with a `Remediation:` line that names the concrete next action |
| Re-open the gate without re-running the producing step | "Maybe the evidence is fine now" without re-capture is wishful thinking | Re-run `functional-validation` (or the producing skill); only then re-gate |

## Iron rules

- **NO `--force-complete` flag.** Refusal is the final word.
- **NO silent downgrade.** A SPLIT consensus does not become a MAJORITY by omission.
- **Cite specific evidence file paths.** No prose-only blockers.
- The REFUSAL.md is the basis for the next `/shannon:autopilot` attempt's remediation prompt.

## Worked Example

**Scenario:** MSC "login flow PASS" requires `step-03-login-success.png`. Evidence directory contains step-01 and step-02 only; step-03 was never captured because the dev server crashed mid-journey.

`plans/reports/REFUSAL-2026-05-27-login-rebuild.md`:

```markdown
# REFUSAL — 2026-05-27-login-rebuild
**Date:** 2026-05-27T19:14:08Z
**Phase:** Phase 10 — completion-gate

## Cited Blockers

### Blocker 1
- **MSC:** login flow PASS — user signs in, lands on dashboard, dashboard shows username
- **Why refused:** MISSING evidence
- **Evidence expected:** e2e-evidence/2026-05-27-login-rebuild/login-journey/step-03-login-success.png
- **Evidence actual:** missing — directory contains step-01-login-loaded.png and step-02-credentials-entered.png only; dev server logs show crash at 19:11:42 mid-submit
- **Remediation:** restart dev server, replay login-journey, capture step-03-login-success.png with the username badge visible; re-gate

## What was NOT done
- PR not created
- TaskUpdate(completed) for "login flow rebuild" not set
- Three-reviewer consensus not assembled (gate refused before consensus phase)

## How to retry
- /shannon:cook "restart dev server, replay login-journey, capture step-03-login-success showing username badge; re-gate"
- Or /shannon:autopilot "complete login flow rebuild" — refusal-driven retry loop reads this file as remediation prompt
```

## Shannon Runtime Integration

- **Output location:** `plans/reports/REFUSAL-<run-id>.md` — `/shannon:autopilot` reads this file to construct its next remediation prompt.
- **Pipeline halt:** the skill HALTs the calling pipeline; downstream phases do not run after refusal until a re-gate succeeds.
- **TaskUpdate semantics:** the calling skill MUST reset the task to `in_progress` (with a note pointing at the refusal file) — not `completed`, not `blocked`. `in_progress + REFUSAL` is the canonical state.

## Related Skills

- `evidence-gate` — per-claim 6-question gate; refuses route here
- `completion-gate` — outer mechanical gate; refuses route here
- `functional-validation` — the producing skill; re-runs after remediation
- `autopilot-runner` — reads `REFUSAL.md` to construct retry remediation prompts
- `consensus-engine` — produces SPLIT verdicts this skill handles
- `judge` — produces REFUSE verdicts this skill handles

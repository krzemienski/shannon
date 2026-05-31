---
name: autopilot
description: "Refusal-driven retry loop around /shannon:cook. Preserves Iron Rule + refusal-discipline pattern."
argument-hint: "<task> [--max-attempts N]"
---

# /shannon:autopilot

Fully autonomous execution. Wraps `/shannon:cook` in a refusal-driven retry loop.

## Inputs

- `<task>` — task description or plan path
- `--max-attempts N` — retry cap (default 3)

## Behavior

For attempt 1..N:
1. Invoke `/shannon:cook <task>` (which spawns `Task: executor` with embedded validation).
2. After cook returns, check `Skill: completion-gate` verdict:
   - `COMPLETE` → exit success.
   - `REFUSED` → read `REFUSAL.md`, parse cited blockers, build remediation prompt for next attempt.
3. If attempt == max-attempts AND still REFUSED → emit final REFUSAL.md to `plans/reports/autopilot-<run-id>-REFUSAL.md`; exit failure.

Refusal is a feature, not a bug. No override flag. No force-complete (per `Skill: refusal-discipline`).

## Skills + agents

- `Skill: completion-gate`
- `Skill: refusal-discipline`
- `Skill: autopilot-runner` (this command IS the autopilot runner)
- `Task: executor` (delegated via cook)

## Success criteria

- `completion-gate` returns COMPLETE
- All cited blockers from prior attempts resolved with new evidence

## Examples

```
/shannon:autopilot "Add SSO with Okta to admin panel"
/shannon:autopilot plans/260528-feature-y/ --max-attempts 5
```

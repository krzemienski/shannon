---
name: loop
description: "Self-referential do-verify-reflect loop until goal verified or max iterations hit."
argument-hint: "<goal> [--max-iter N] [--verify-with <skill>]"
---

# /shannon:loop

Iterative {do → verify → reflect} loop. Converges when verify skill PASSes or max iterations exhausted.

## Inputs

- `<goal>` — natural language goal statement
- `--max-iter N` — iteration cap (default 5)
- `--verify-with <skill>` — verify skill name (default `functional-validation`)

## Behavior

Each iteration:
1. **Do** — `Task: shannon:executor` attempts goal step with current best understanding.
2. **Verify** — invoke `Skill: <verify-with>` against the artifact produced this iteration.
3. **Reflect** — invoke `Skill: reflect`; identify gap; produce next-iteration prompt.
4. If verify PASS AND `reflect` returns "converged" → exit success.
5. If iteration count == max-iter → emit REFUSAL via `Skill: refusal-discipline`; exit failure.

State persists under `e2e-evidence/loop-<run-id>/iter-N/` so iterations are inspectable.

## Skills + agents

- `Skill: loop-runner` (Shannon-specific orchestrator — this command IS the loop runner)
- `Skill: goal-loop-orchestrator` (goal-condition gating for the convergence check)
- `Task: shannon:executor` (per-iteration do step)
- `Skill: functional-validation` (default verify)
- `Skill: reflect`
- `Skill: refusal-discipline` (on max-iter exhaustion)

## Examples

```
/shannon:loop "Fix flaky CI in deploy-preview job"
/shannon:loop "Get LCP under 2.0s on /products" --max-iter 8 --verify-with functional-validation
```

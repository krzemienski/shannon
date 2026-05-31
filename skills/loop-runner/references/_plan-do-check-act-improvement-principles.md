# Improvement Principles (PDCA)

> The principles that distinguish improvement-by-iteration from improvement-by-rewriting. PDCA only produces real gains when each cycle is run with discipline.

## The PDCA loop

```
PLAN   →   DO   →   CHECK   →   ACT   →   (PLAN next cycle)
```

- **Plan:** define the change you'll make + the metric you'll measure
- **Do:** make the change
- **Check:** measure the metric against the baseline
- **Act:** if better, adopt; if worse, revert; if mixed, refine

The discipline is what makes this loop converge instead of oscillate.

## The 8 principles

### 1. One change per cycle

The cardinal rule. If you change 3 things and the metric moves, you don't know which change drove it.

Exception: refactors that don't change behavior (rename, reformat) — those can be batched.

### 2. Same evaluation set each cycle

The metric is meaningless if measured on different inputs each time. Build a stable eval set (50-200 cases) BEFORE the first cycle. Use it for every cycle.

If the eval set changes mid-run, you've lost comparability. Either restart the run or document the eval-set change as a finding.

### 3. Hypothesis, not hope

Each cycle starts with a written hypothesis:

```
"Adding 3 few-shot exemplars will improve format-adherence from 73% to >90%
because the model currently invents fields when format is ambiguous."
```

If you can't articulate WHY the change should help, you're guessing. Stop and re-think.

### 4. Measure before AND after

Baseline is non-negotiable. "I changed X and now it's better" without a recorded baseline is a story, not data.

Record:
- Pre-change metric
- Post-change metric
- Delta + statistical confidence if possible

### 5. Regression checks

When fixing target metric A, verify metric B, C, D didn't regress:

```
Target: accuracy ↑
Side metrics to monitor:
  - latency (didn't blow up)
  - cost / token count (didn't double)
  - refusal rate (didn't start refusing more)
  - format adherence (didn't break parser)
```

A "win" on accuracy that breaks 2 other metrics is net negative.

### 6. Revert mercilessly

If the cycle's hypothesis was wrong, REVERT. Don't keep the change "because it's almost good." Cycles compound; bad changes propagate through future iterations.

The revert button is your friend. Use it.

### 7. Convergence vs. perfection

PDCA produces local optima. The first 3-5 cycles often capture 80% of available improvement; the next 20 cycles capture another 5%.

Set a target before starting:

```
"Iterate until accuracy ≥ 90% OR 5 consecutive cycles each yield <1% improvement."
```

Stop at the target. Resist the urge to keep pushing — diminishing returns are real.

### 8. Document the run

Every PDCA run produces:
- Initial metric + hypothesis
- Per-cycle change + delta
- Final metric + decision (kept / reverted)
- Optional: post-mortem on what didn't work and why

Without this log, you can't:
- Reproduce the run
- Justify the changes to a reviewer
- Learn from the cycles for next time

## Common failure modes

### Premature convergence

Symptom: settling for "good enough" on cycle 2 because the metric moved up.

Fix: stick to the cycle budget. Run all planned cycles; stop on the convergence criterion, not on first-improvement.

### Overfitting to the eval set

Symptom: metric on eval set is 95%, but real-world performance is 70%.

Fix: hold out 10-20% of the eval set as a true-test set never used during cycles. Final reported metric is on the held-out set.

### Goodhart's law

Symptom: the metric goes up but the underlying quality didn't.

Fix: pick a metric that correlates with real value, not a metric that's easy to optimize. Periodically validate the metric itself.

### Cycle-time explosion

Symptom: each cycle takes 8 hours; only 2 cycles in a week.

Fix: shrink the eval set (50 cases is plenty for early cycles); automate measurement; batch independent dimensions.

### Lost cycle history

Symptom: "what was the change in cycle 4?" — no one remembers.

Fix: log each cycle to disk as it happens. `cycles.md` with: hypothesis, change, metric delta, decision. Future-you (and reviewers) will thank you.

## When to skip PDCA

PDCA is overhead. Skip it when:
- The change is obviously correct (typo fix, dead code removal)
- Measurement isn't possible (one-off creative work)
- The system is too small for systematic improvement
- The time budget doesn't allow even one cycle

Don't apply PDCA to everything. Apply it to changes where the right answer is unclear and the metric is measurable.

## PDCA in Shannon contexts

Shannon uses PDCA inside:

- **Skill quality iteration** — each skill's description and trigger phrases are optimized via PDCA across real user invocations
- **Prompt template optimization** — see `skills/prompt-engineering-patterns/references/prompt-optimization.md`
- **Loop convergence** — `loop-runner` and `autopilot-runner` are PDCA-shaped: plan → do → check → act → loop
- **Validation cycle improvement** — `ultraqa` cycles are PDCA on test failures

The principles above apply consistently across these contexts.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Multiple changes per cycle | Can't attribute improvement | One change per cycle |
| Different eval set per cycle | Not comparable | Lock the eval set |
| No hypothesis | Random walk, not improvement | Write the hypothesis first |
| No baseline measurement | "Better" is opinion | Always measure pre-change |
| No regression checks | Win on A breaks B | Monitor side metrics |
| Keeping a bad change | Compounds future cycles | Revert mercilessly |
| Infinite cycling | Diminishing returns | Set convergence criterion |
| Undocumented runs | Can't reproduce / learn | Per-cycle log |

## Cross-references

- _Historical: this content was absorbed from the legacy `plan-do-check-act` skill into its absorbing parent. The original `plan-do-check-act` skill no longer exists in v1._
- `skills/reflect/` — what to do after a PDCA run
- `skills/loop-runner/` — applies PDCA to autonomous loops
- `skills/ultraqa/` — applies PDCA to QA cycles
- `skills/prompt-engineering-patterns/references/prompt-optimization.md` — PDCA for prompts specifically

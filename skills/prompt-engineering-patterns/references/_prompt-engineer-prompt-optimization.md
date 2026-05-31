# Prompt-Engineer's Optimization View

> The optimization loop applied to prompts. Deep treatment lives in `skills/prompt-engineering-patterns/references/prompt-optimization.md`; this file is the prompt-engineer's quick-reference.

## The discipline (one-page version)

```
1. Define what "better" means — pick a metric
2. Baseline: measure current prompt
3. Hypothesize the change that addresses the dominant failure
4. Make ONE change
5. Re-measure on same eval set
6. Keep if better; revert if not; check for regressions
7. Repeat
```

The cardinal rule: one change per iteration, same eval set across iterations.

## Where prompt-engineer fits

Prompt-engineer is the skill you invoke when:
- You have a prompt that almost works but fails on N% of cases
- You don't know which lever to pull
- You want a structured iteration, not random tweaks

It walks you through:
1. Picking the right metric
2. Identifying the dominant failure mode
3. Choosing the lever to pull (which pattern from the catalog)
4. Measuring before/after
5. Deciding to keep / revert

## Levers (in priority order)

The levers most likely to help, in rough order of effect/cost:

### Lever 1: Add a format schema

If output format is inconsistent, this alone often closes the gap.

Effect: typically +30-60% on format-adherence metric
Cost: minimal prompt-token increase
Risk: low

### Lever 2: Add 2-3 few-shot exemplars

If the model defaults are subtly wrong, exemplars anchor it.

Effect: typically +10-25% on accuracy
Cost: medium prompt-token increase
Risk: low (if exemplars are diverse)

### Lever 3: Add CoT prefix

For multi-step reasoning tasks.

Effect: typically +5-30% on reasoning-task accuracy
Cost: low (one phrase)
Risk: low

### Lever 4: Tighten the persona

If outputs are generic, specific persona shapes defaults.

Effect: variable; sometimes large for tone-sensitive tasks
Cost: minimal
Risk: low

### Lever 5: Move critical instruction to start/end

If outputs are missing critical detail buried mid-prompt.

Effect: variable
Cost: zero
Risk: zero

### Lever 6: Switch model

E.g., Sonnet → Opus for quality, or Opus → Haiku for cost.

Effect: substantial (in either direction)
Cost: changes price + latency
Risk: medium (model-specific behavior)

### Lever 7: Decompose into multiple prompts

If one prompt is doing too much.

Effect: often substantial
Cost: more prompt invocations
Risk: medium (chain failures compound)

### Lever 8: Lower temperature

For tasks that should be deterministic.

Effect: more consistent outputs
Cost: less creative outputs
Risk: low

## Diagnosing the dominant failure mode

Before pulling a lever, diagnose:

1. Sample 10-20 failing outputs from the eval set
2. Cluster them into failure types (format-wrong, fact-wrong, refusal-wrong, etc.)
3. Identify the most common type — that's the dominant failure
4. Pick the lever that addresses THAT failure

Pulling a lever that doesn't address the dominant failure wastes a cycle.

## Convergence criterion

Set a target before iterating:

```
Target: accuracy ≥ 90% AND format-adherence ≥ 99% AND no-regression on
        secondary metrics
```

Stop when target met OR 5 consecutive iterations each yield <2% improvement.

Don't optimize past the target. Marginal returns shrink fast.

## When prompt-engineer can't help

Sometimes the prompt isn't the limiting factor:

- The model genuinely can't do the task at this size (need a bigger model)
- The eval set is mis-specified (re-build the eval set)
- The task is ambiguous (improve the spec, then the prompt)
- The data is bad (the model can't compensate for garbage input)

In these cases, prompt-engineer surfaces the underlying problem rather than chasing prompt iterations.

## Cross-references

- `skills/prompt-engineer/` — parent skill
- `skills/prompt-engineering-patterns/references/prompt-optimization.md` — the deep treatment of this loop
- `references/evaluation-frameworks.md` — building the eval set
- `references/prompt-patterns.md` — the catalog of levers
- `skills/optimize-prompt/` — alternate workflow for single-prompt optimization

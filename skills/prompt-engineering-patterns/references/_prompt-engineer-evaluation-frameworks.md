# Evaluation Frameworks

> How to measure whether a prompt is actually working. Evaluation is the discipline that turns prompt-iteration from opinion into engineering.

## The two-phase eval

```
Phase 1: Build an eval set (50-200 inputs with golden answers OR a rubric)
Phase 2: Score each prompt variant against the eval set
```

Without Phase 1, you don't know what "better" means. Without Phase 2, you don't know if you're getting better.

## Building an eval set

### Eval set requirements

- **Stable**: same inputs every iteration. Changes mid-run break comparability.
- **Diverse**: covers easy / medium / hard, plus edge cases.
- **Representative**: reflects the actual distribution of real-world inputs.
- **Scored consistently**: either golden answers (one correct output) or a rubric (criteria for partial credit).
- **Sized appropriately**: 30 inputs for fast iteration, 200 for confidence. 50-100 is the sweet spot.

### Golden answers vs. rubric

| Approach | When |
|----------|------|
| Golden answer per input | Classification, exact-match QA, deterministic outputs |
| Rubric per input | Open-ended generation, summarization, multi-criteria tasks |

Rubrics typically score per dimension (accuracy / completeness / format / tone) and sum/weight.

### Held-out test set

Reserve 10-20% of the eval set as a held-out test set. NEVER use it during iteration. After you ship a prompt, score it on the held-out set as your final reported metric.

Without held-out, you may be overfitting to your dev set.

## Metric categories

### Accuracy metrics

For classification or exact-match:

- **Top-1 accuracy**: fraction where the model's top answer exactly matches the golden answer
- **F1 / precision / recall**: for binary / multi-class with imbalance

For open-ended:

- **Rubric-scored accuracy**: average rubric score across inputs
- **ROUGE / BLEU / BERTScore**: surrogate metrics for text similarity (caveat: known weaknesses)
- **Judge-LLM scored**: use a separate model as judge; correlate with human ratings

### Format / structure metrics

- **Parse rate**: fraction of outputs that parse as expected format (JSON, schema, etc.)
- **Schema-validation pass rate**: fraction parsing AND conforming to schema
- **Field-presence rate**: average fraction of required fields present

### Behavior metrics

- **Refusal rate**: fraction where the model refused (split into "correctly refused" vs "incorrectly refused")
- **Hallucination rate**: fraction with unsupported claims (requires manual or auto fact-check)
- **Length compliance**: fraction within length bounds

### Operational metrics

- **Latency**: p50 / p99 response time
- **Cost**: tokens × price
- **Failure rate**: parse failures + retries + outright errors

## Scoring patterns

### Pattern: Auto-graded against golden answers

```python
correct = 0
for input, golden in eval_set:
    output = llm_call(prompt, input)
    if output.strip().lower() == golden.strip().lower():
        correct += 1
accuracy = correct / len(eval_set)
```

Cheap. Works for exact-match. Fails for open-ended.

### Pattern: Rubric-graded by judge LLM

```python
scores = []
for input, golden_rubric in eval_set:
    output = llm_call(prompt, input)
    rubric_score = judge_llm(
        rubric=golden_rubric,
        output=output
    )  # returns 0.0 to 1.0
    scores.append(rubric_score)
mean_score = sum(scores) / len(scores)
```

More expensive (one LLM call per item for grading). Works for open-ended. Watch for judge bias (use multiple judges; debate-style for disagreements).

See `skills/judge/`, `skills/judge-with-debate/`, `agents/meta-judge.md`.

### Pattern: A/B comparison

For variant comparison, paired evaluation is better than absolute scoring:

```python
for input, _ in eval_set:
    output_a = llm_call(prompt_a, input)
    output_b = llm_call(prompt_b, input)
    winner = judge_llm(input=input, output_a=output_a, output_b=output_b)
    # judge picks A, B, or "tie"
```

Aggregate: A wins X%, B wins Y%, ties Z%. Easier for the judge than scoring each independently.

## Iteration loop with evals

```
1. Baseline: score current prompt on eval set → metric_v1
2. Hypothesize a change that addresses dominant failure mode
3. Apply change → prompt_v2
4. Score prompt_v2 on eval set → metric_v2
5. Compare: if metric_v2 > metric_v1, keep change; otherwise revert
6. Check regressions: did secondary metrics get worse?
7. Repeat
```

One change per iteration. Same eval set across iterations. Documented per cycle.

Deep cycle discipline: `skills/prompt-engineering-patterns/references/prompt-optimization.md`.

## When evals lie

### Goodhart's law

The metric you optimize stops being a good measure of quality once it becomes the target.

Example: optimizing for "judge-LLM rates output 5/5" pushes the model to produce outputs that game the judge — verbose / superficially polished / format-locked outputs that don't actually answer better.

Mitigation: rotate the judge model; periodically validate metric against human ratings.

### Selection bias in eval set

If your eval set is drawn from easy cases (because hard cases are tedious to collect), the prompt overfits to easy cases.

Mitigation: deliberately collect edge cases. Sample real-world distribution, not what's convenient.

### Drift over time

Real user inputs evolve. An eval set built in January may not reflect April's traffic.

Mitigation: periodically refresh the eval set with recent real inputs. Mark old vs new in the eval set so you can see if recent changes are at risk of regression.

## Production telemetry

In production, score every output you can:

- Log: prompt version + input + output
- Track: parse rate, retry rate, user rating (thumbs / explicit feedback)
- Sample: send N% to manual review for ground-truth scoring

Telemetry feeds back into the eval set: failures in production become eval-set entries.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Iterating without an eval set | "Better" is opinion, not measurement | Build eval set first |
| Eval set of 5 inputs | Statistically meaningless | 50+ inputs minimum |
| Using held-out set during iteration | Overfits to test set | Reserve 10-20% for final report only |
| Single metric ignores regressions | "Win" on accuracy breaks format | Track 3-5 metrics; verify no regressions |
| Judge-LLM as sole truth | Goodhart's law | Periodically validate against human |

## Cross-references

- `skills/prompt-engineer/` — parent skill
- `references/prompt-optimization.md` — iteration discipline using these metrics
- `references/prompt-patterns.md` — the patterns being evaluated
- `skills/judge/`, `skills/judge-with-debate/`, `skills/consensus-engine/` — LLM-as-judge patterns
- `agents/meta-judge.md` — rubric-generation primitive

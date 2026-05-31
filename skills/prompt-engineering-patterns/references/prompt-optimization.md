# Prompt Optimization

> The iteration loop for improving a prompt: measure, hypothesize, change one thing, re-measure. Disciplined optimization beats random tweaking.

## The basic loop

```
1. Define what "better" means — pick a metric
2. Establish a baseline — run the current prompt on N inputs, score it
3. Identify the dominant failure mode — what does it get wrong?
4. Form a hypothesis — what change would address that failure mode?
5. Make ONE change
6. Re-run on the same N inputs, score it
7. Compare: did the metric improve? Did anything else regress?
8. Keep the change if net positive; revert if not
9. Repeat
```

The discipline that distinguishes optimization from random tweaking: ONE change per iteration, SAME evaluation set, EXPLICIT metric.

## Picking a metric

Metrics fall into categories. Pick one (or a weighted blend):

| Metric | Measures | How |
|---|---|---|
| Accuracy | Did it produce the right answer? | Manual scoring vs golden answers |
| Format adherence | Did it match the required output shape? | Regex / JSON-schema validation |
| Length | Token / character count | `len(response)` |
| Refusal rate | Did it refuse when it shouldn't? | Count refusal-like phrases |
| Hallucination rate | Did it invent unsupported claims? | Manual scoring with fact-check |
| User rating | Did the user find it useful? | Thumbs / 1-5 score from real users |
| Latency | Time to first token, total time | Wall clock |
| Cost | Tokens × price | Usage stats |

For most tasks, accuracy on a small (50-200 input) eval set + format adherence is the right blend.

## Building an evaluation set

Without an eval set, you're guessing. With one, you can measure.

A good eval set has:
- 30-200 inputs spanning the cases you actually see
- Mix of easy / medium / hard
- Edge cases (empty input, malformed, ambiguous)
- Golden answers OR a rubric for scoring
- Stable: same inputs every iteration

Build the eval set BEFORE optimizing. Iterating without one means each "improvement" is an opinion.

## Common failure modes and fixes

### Failure: model adds preamble ("Sure, here's the…")

**Hypothesis:** model is being polite when you want pure output.

**Fix candidates (try one at a time):**
1. Add to end of prompt: "Respond with the JSON only. No preamble."
2. In system prompt: "You are concise. Skip pleasantries."
3. Provide an example showing direct output.

### Failure: model invents facts (hallucination)

**Hypothesis:** model fills gaps with plausible-sounding fiction.

**Fixes:**
1. Add: "If you don't know, say 'unknown'. Don't guess."
2. Provide reference material as context.
3. Ask for citations: "For each claim, cite the source line."
4. Use a verification step.

### Failure: model refuses to answer in-distribution questions

**Hypothesis:** over-cautious refusal trigger.

**Fixes:**
1. Soften the refusal policy in the system prompt.
2. Clarify the legitimate use case: "This is for security research."
3. Show examples where similar questions get answered.

### Failure: output format inconsistent

**Hypothesis:** model thinks the format is a suggestion.

**Fixes:**
1. Provide a schema: "Respond with this exact JSON shape: {…}"
2. Show 2-3 examples of correctly-formatted outputs.
3. End prompt with "Respond with valid JSON only — no markdown fences."
4. Use a parser that retries on malformed output.

### Failure: model misses critical detail

**Hypothesis:** the critical detail is buried in the middle of the prompt.

**Fixes:**
1. Move the critical instruction to the END (recency bias).
2. Bold it or use ALL CAPS for emphasis.
3. State it twice — once at start, once at end.

### Failure: output too verbose

**Hypothesis:** model defaults to detail.

**Fixes:**
1. Add length cap: "Maximum 200 words."
2. State the form: "Bullet list, 3-5 items, each one sentence."
3. Show concise examples.
4. "Be terse."

### Failure: output too terse

**Hypothesis:** model is stripping context.

**Fixes:**
1. "Explain your reasoning before answering."
2. Show example outputs with the desired detail level.
3. "Cite specific lines/examples in your response."

## Variables to try (and their typical effects)

| Change | Typical effect | Cost |
|---|---|---|
| Add CoT prefix | +5-30% accuracy on reasoning tasks | low (token cost) |
| Add 3-5 exemplars | +10-25% accuracy on format-locked tasks | medium (prompt size) |
| Move critical instruction to end | Significant on long prompts | none |
| Switch model (Sonnet → Opus) | +5-15% on most quality metrics | 5x cost |
| Lower temperature | More consistent outputs, less creative | none |
| Add format schema | Massive lift on format adherence | low |
| Add refusal policy | Reduced bad outputs, occasional false refusals | low |
| Increase max_tokens | Allows model to complete longer outputs | none upfront |

## One-change discipline

The temptation: "I'll change three things at once and see if it gets better."

The problem: when it gets better, you don't know which change drove the improvement. When it gets worse, you don't know which change caused regression.

The rule: ONE change per iteration. If you must change multiple things, change them sequentially and measure between.

Exception: refactors that don't change behavior (renaming variables, reformatting markdown). These can be batched.

## Regression checks

When you make a change to fix failure mode A, verify it didn't break:
- Format adherence
- Refusal rate (didn't start refusing what it used to answer)
- Length (didn't become 10x longer)
- Latency (didn't become slower)

A "fix" that improves accuracy on the target case but breaks 5 other cases is net negative.

## Stop conditions

When to stop iterating:

1. **Hit the metric target** — accuracy is at 95% and that's enough.
2. **Diminishing returns** — last 3 iterations each moved the metric <1%.
3. **Cost ceiling reached** — prompt is now 8K tokens and that's too expensive.
4. **Model ceiling** — the model can't do better on this task; consider a different model or a different approach.

Don't optimize forever. The 90th percentile of quality usually arrives in <5 iterations.

## Telemetry

For production prompts, log:
- The exact prompt sent (template + version + slot values)
- The model response
- The user / downstream-system reaction (rating, success, failure, retry)

With this telemetry, you can iterate post-hoc: find failure cases, group them, identify dominant failure mode, propose fix.

## Optimization for prompt-using-agents

When your "prompt" is actually an agent (with tools), optimization expands:

- Tool-selection accuracy (does it pick the right tool?)
- Tool-argument quality (are the args correct?)
- Tool-result handling (does it react correctly to tool output?)
- Conversation length (does it ramble across many turns?)
- Backtracking behavior (does it abandon wrong paths?)

Use a controlled scenario set (replayable user goals) to measure all of these consistently.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Iterating without an eval set | Improvements are opinions, not measurements | Build a 50+ input eval set first |
| Changing multiple things per iteration | Can't attribute improvement to a specific change | One change per iteration |
| Optimizing on a single example | Overfits to that example | Eval set spans diverse cases |
| Not checking for regressions | "Fix" makes other cases worse | Always re-run full eval after changes |
| Optimizing past 95% | Diminishing returns + risk of overfitting | Set a target; stop at target |
| Optimizing the wrong metric | Better on metric, worse for user | Pick a metric that correlates with user value |

## Cross-references

- `references/chain-of-thought.md` — common optimization target
- `references/few-shot-learning.md` — common optimization tool
- `references/system-prompts.md` — primary optimization surface
- `references/prompt-templates.md` — versioning enables comparison
- `skills/optimize-prompt/` — the single-prompt-optimization workflow skill
- `skills/prompt-improver/` — light-touch single-pass improver
- `skills/prompt-engineering-patterns/` — parent skill

# Chain-of-Thought (CoT) Patterns

> Eliciting step-by-step reasoning from the model before it answers. The single most reliable accuracy lift for non-trivial reasoning tasks.

## When CoT helps (and when it doesn't)

CoT lifts accuracy on tasks where the answer depends on a multi-step derivation:
- Arithmetic word problems
- Causal reasoning ("A caused B because…")
- Multi-hop QA ("who was the mentor of the person who…")
- Code debugging (trace through state)
- Symbolic manipulation (logic puzzles, regex construction)

CoT does NOT meaningfully help on:
- Pattern recognition tasks where the answer is "look up and report" (no derivation)
- Tasks under ~3 steps of reasoning (where the model gets it right one-shot anyway)
- Tasks where the chain is more error-prone than the direct answer (e.g., simple lookups)
- Tasks with rigid output structure where verbose thinking pollutes the format

If your task lifts <2 percentage points from CoT, the prompt-token cost usually isn't worth it.

## Three CoT modes

### 1. Zero-shot CoT — the prompt prefix

The cheapest CoT. Add one of these phrases:
- `Let's think step by step.`
- `Let's work this out step by step to be sure we have the right answer.`
- `Break this down before answering.`

Place it at the end of the user prompt, before the model's response begins. Works on most modern models; sometimes lifts accuracy 10-30% on multi-step tasks at near-zero token cost.

```
User: A train leaves Chicago at 60mph. Another leaves NYC at 80mph going the
opposite direction. NYC and Chicago are 800 miles apart. When do they meet?

Let's think step by step.
```

### 2. Few-shot CoT — exemplars with reasoning shown

Provide 2-5 examples where the reasoning is fully written out, then ask the new question. Lifts accuracy MORE than zero-shot CoT on benchmark tasks, at higher prompt cost.

```
Q: A library has 120 books. They donate 1/4 and buy 30 new ones. How many books now?
A: They donate 120 / 4 = 30 books, leaving 120 - 30 = 90 books.
Then they buy 30 more, totaling 90 + 30 = 120 books.
The answer is 120.

Q: A jar has 50 marbles. We remove 1/5 then add 12. How many?
A: 50 / 5 = 10 marbles removed, leaving 40. Then 40 + 12 = 52.
The answer is 52.

Q: <your actual question>
A:
```

Show 2-3 exemplars at minimum. Diminishing returns past ~5.

### 3. Decomposed CoT — explicit sub-question structure

Break the task into named sub-steps and have the model fill each in:

```
Question: <complex multi-part question>

Step 1 — Identify what's known:
Step 2 — Identify what's asked:
Step 3 — Choose the relevant formula / approach:
Step 4 — Apply it:
Step 5 — Sanity check:
Final answer:
```

More verbose but most controllable — you specify the structure of the derivation. Use when you need the chain to follow a specific protocol.

## Common pitfalls

### Reasoning that confidently lies

Models can produce a fluent, plausible-looking chain that arrives at the wrong answer. Mitigation:

1. **Self-consistency** — ask N times, take the modal answer.
2. **Verification step** — append "Now verify: does the answer satisfy the constraints?" and re-prompt.
3. **Domain-specific check** — for arithmetic, evaluate the final expression with a calculator step; for code, run it.

### Chain pollutes structured output

If your downstream consumer expects pure JSON, CoT reasoning in the output breaks the parser. Two fixes:

1. Use a 2-message protocol: first message generates reasoning + answer; second extracts answer to JSON.
2. Use a "reasoning" key inside the JSON schema:

```json
{
  "reasoning": "First, I identify... Then I apply...",
  "answer": 42
}
```

### Chain length explodes

Models can be verbose. If a single chain consumes >500 tokens for a task that's solvable in 50, the model is rambling. Mitigations:

- "Be concise. Show only the steps that materially affect the answer."
- Hard limit: "Use at most 3 steps."
- Few-shot exemplars with brief reasoning anchor the model toward brief chains.

## CoT for code tasks

A code-specific CoT pattern that consistently helps:

```
Before writing code:
1. State what the function does in 1 sentence.
2. List inputs and their types.
3. List outputs and their types.
4. List edge cases (empty, single element, very large, malformed).
5. Sketch the algorithm in pseudocode.
THEN write the code.
```

This forces the model to surface assumptions before committing them to code, where they're harder to catch.

## CoT for debugging

```
Bug report: <symptom>

Reasoning:
1. What's the most direct trigger of this symptom?
2. What state would have to be true for that trigger to fire?
3. Where in the code does that state get set?
4. What invariant is violated if state-is-wrong?
5. Walk through the path that violates the invariant.
Hypothesis:
Verification plan:
```

This pattern, applied in the `root-cause-tracing` skill, surfaces non-obvious causal chains.

## CoT vs Tree-of-Thoughts (ToT)

CoT generates ONE chain. ToT generates multiple branching chains, prunes the bad ones, expands the good ones.

- Use CoT when the right answer is unambiguous once derived
- Use ToT when multiple plausible derivations exist and you need to compare

See `skills/tree-of-thoughts/` for the ToT protocol.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| "Think step by step" on a one-step task | Inflates output for no gain | Skip CoT below ~3 reasoning steps |
| Showing exemplars without diverse types | Model anchors on the exemplar pattern only | Diversify few-shot examples across edge cases |
| Asking for reasoning AND strict JSON in one message | Output gets corrupted | Two-message protocol or reasoning-key inside schema |
| Asking the same question 100x for "self-consistency" without aggregation | You get 100 chains and no answer | Aggregate explicitly: take modal answer, or have model vote |

## Cross-references

- `references/few-shot-learning.md` — exemplar selection for few-shot CoT
- `references/prompt-templates.md` — wrapping CoT in reusable templates
- `references/system-prompts.md` — system-level instructions to default-on CoT
- `skills/tree-of-thoughts/` — when CoT isn't enough
- `skills/prompt-engineering-patterns/` — the parent skill

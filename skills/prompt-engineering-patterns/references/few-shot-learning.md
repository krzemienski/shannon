# Few-Shot Learning

> Showing the model 2-5 input/output examples before the actual task. The most reliable way to lock in a specific output format, tone, or reasoning pattern.

## When few-shot is the right tool

Few-shot helps when:
- The output format is non-obvious or unusual (custom DSL, structured tag-soup)
- Tone needs to be specific (technical, casual, brand-voice-locked)
- The reasoning pattern matters (you want CoT-style derivations to follow a specific shape)
- The model defaults are subtly wrong (e.g., it adds preamble you don't want)

Few-shot is wasteful when:
- The task is in the model's training distribution and zero-shot already works
- The format is trivial (yes/no, single integer)
- Exemplars would consume more tokens than the actual output

Rule of thumb: if zero-shot accuracy is already >90%, few-shot's lift won't justify the prompt-token cost.

## How many examples

| Examples | When |
|---:|---|
| 0 | Default — try this first |
| 1 | One-shot — when format is simple but model needs a concrete pattern |
| 2-3 | Most common — enough to anchor pattern, low prompt cost |
| 4-5 | When the task has multiple sub-types and each needs an exemplar |
| 6+ | Rarely useful; diminishing returns + prompt bloat |

Empirically: 2-3 exemplars capture ~80% of the lift; 5+ shows minimal additional gain.

## Selecting exemplars

The two pitfalls of bad exemplar selection:

### Pitfall 1: Homogeneous exemplars

If all exemplars are the same type of case, the model overfits to that type and fails on edge cases. Solution: diversify deliberately across:
- Input length (short, medium, long)
- Output complexity (simple, complex)
- Edge cases (empty input, ambiguous input, well-formed input)
- Difficulty (easy, medium, hard)

### Pitfall 2: Cherry-picked exemplars

Choosing only "best case" exemplars sets the model up to fail on real-world dirty input. Solution: include at least one exemplar that handles a tricky case the right way.

## Format consistency

Critical: the exemplars must follow EXACTLY the format you want from the model. Any inconsistency teaches the model that variation is OK.

```
✓ GOOD — every exemplar uses the same prefix structure:

Input: "Schedule a meeting with Alex tomorrow at 2pm"
Output: {"intent": "schedule", "person": "Alex", "time": "tomorrow 2pm"}

Input: "Remind me to call mom on Sunday"
Output: {"intent": "remind", "person": "mom", "time": "Sunday"}

Input: <your actual input>
Output:
```

```
✗ BAD — inconsistent prefixes confuse the model:

Q: "Schedule a meeting…"
Result: {"intent":"schedule",…}

User: "Remind me…"
Response: {"intent":"remind",…}

Input: <your actual input>
???:
```

## Delimiter discipline

Use a clear delimiter between exemplars so the model knows where one ends and the next begins:

```
---

Input: <example 1 input>
Output: <example 1 output>

---

Input: <example 2 input>
Output: <example 2 output>

---

Input: <your actual input>
Output:
```

Common delimiters that work: `---`, `===`, `\n\n###\n\n`, XML tags like `<example></example>`.

Avoid delimiters that overlap with the content (e.g., `---` if the content contains markdown horizontal rules).

## Chain-of-thought few-shot

For multi-step reasoning tasks, exemplars should show the FULL chain, not just input → output:

```
Q: Anna has 5 apples. She gives 2 to her brother and buys 3 more. How many?
A: She starts with 5 apples. After giving 2 away, she has 5 - 2 = 3 apples.
Then she buys 3 more, totaling 3 + 3 = 6 apples.
The answer is 6.

Q: A box has 12 chocolates. We eat 1/4 and add 5 truffles. How many treats now?
A: 1/4 of 12 is 12 / 4 = 3 chocolates eaten, leaving 9.
Then we add 5 truffles, for 9 + 5 = 14 treats total.
The answer is 14.

Q: <new question>
A:
```

The reasoning shape in exemplars locks in the reasoning shape in the answer.

## Negative examples (use sparingly)

Sometimes you want to show the model what NOT to do:

```
INPUT: "The widget should be blue"
GOOD OUTPUT: {"property":"color","value":"blue"}
BAD OUTPUT: {"color":"blue"}  ← missing the property wrapper

INPUT: <your input>
GOOD OUTPUT:
```

Effective in moderation. Overuse pushes the model into a defensive output style that's overly hedged.

## Few-shot for classification

When asking the model to classify into known categories:

```
Classify each ticket into: bug | feature_request | question | spam.

"App crashes when I tap settings" → bug
"Please add a dark mode" → feature_request
"How do I export my data?" → question
"BUY CHEAP MEDS NOW!!!" → spam

"<new ticket>" →
```

For classification, the exemplar set should cover every category at least once. Otherwise the model may bias toward categories with more exemplars.

## Few-shot for transformation

When the task is "convert format A to format B":

```
SQL → English:

SELECT * FROM users WHERE age > 18
→ Get all users older than 18.

SELECT COUNT(*) FROM orders WHERE status = 'shipped' AND created > '2024-01-01'
→ Count shipped orders since January 1, 2024.

SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.name
→ List each user with their total order count, including users with no orders.

<your SQL>
→
```

## When few-shot fails: probe the model

If few-shot isn't working, try:

1. **Reduce to one exemplar** — sometimes the model is averaging across exemplars when it should be picking one
2. **Move exemplars closer to the actual task** — put them right before the actual query, not in the system prompt
3. **Match the difficulty** — if exemplars are too easy, the model thinks the task is easy too
4. **Explicit instruction** — "Follow the exact format shown in the examples above"

## Cost / quality trade-off

| Exemplars | Quality lift | Prompt-token cost | Use when |
|---:|---|---|---|
| 0 | baseline | low | task is in-distribution |
| 1 | +5-15% | low | format-anchoring |
| 3 | +10-25% | medium | most common sweet spot |
| 5 | +12-28% | high | difficult or multi-type task |
| 10+ | +13-30% | very high | rarely worth it |

The marginal lift past 3-5 examples is small; the marginal cost grows linearly.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| All exemplars from one category | Model overfits | Diversify across edge cases |
| Inconsistent formatting | Model thinks variation is allowed | Lock the format identically across exemplars |
| Exemplars in system prompt + new ones in user prompt | Conflicting signals | Put all exemplars in one location |
| Showing only successful outputs | Model fails on tricky inputs | Include at least one edge-case exemplar |
| Many vague exemplars instead of few precise ones | Quantity does not substitute for quality | 3 great exemplars beat 10 mediocre ones |

## Cross-references

- `references/chain-of-thought.md` — few-shot + CoT combined
- `references/prompt-templates.md` — reusable few-shot templates
- `references/system-prompts.md` — when to put exemplars in system vs user
- `skills/prompt-engineering-patterns/` — parent skill

# Clarifying Question Patterns

> The questions a prompt-improver asks to surface missing context. Patterns for asking ONLY what you can't infer.

## The two-tier rule

Tier 1 (always ask, if missing):
- Output format (if not derivable from context)
- Scope (in/out)
- Edge cases (what to do on empty / missing / invalid input)

Tier 2 (ask only if Tier 1 is met but the prompt still ambiguous):
- Audience / reader
- Length / depth budget
- Subjective-term quantification
- Multi-task ordering
- Refusal conditions

NEVER ask all questions every time. Each ask costs user attention.

## Question patterns by missing dimension

### Pattern Q-1: Output format

When the prompt asks for "a result" without specifying shape:

- "What format should the output be in — JSON, markdown, prose, table?"
- "Should this go in a file or be returned inline?"
- "What's the consuming context — human reader, downstream code, both?"

If multiple formats are plausible, propose 2-3 with concrete examples and ask user to pick.

### Pattern Q-2: Scope (the OUT list)

When the prompt is "do X with Y" and X could touch multiple things:

- "Anything I should explicitly NOT touch as part of this?"
- "Should this be scoped to <module>, or include <related-module>?"
- "Refactoring opportunities I encounter — fix them or leave alone?"

The "leave alone" list is more useful than the "fix" list — it bounds the work.

### Pattern Q-3: Edge cases

When the prompt describes the happy path:

- "What should happen if <input> is missing?"
- "What should happen if <field> is null / empty / very large?"
- "Should I fail fast or try to recover?"

Don't ask for every possible edge case — just the 1-3 most likely.

### Pattern Q-4: Audience / register

When the prompt produces communication:

- "Who reads this — internal team, customers, executives?"
- "Tone — technical, casual, formal?"
- "Should it assume background knowledge of <topic>?"

### Pattern Q-5: Length / depth

When the prompt could produce a paragraph or a book:

- "Length budget — one paragraph, one page, or comprehensive?"
- "How deep — overview, mid-depth, or full detail?"
- "Time budget — quick draft or polished?"

If user says "comprehensive," verify they understand the cost: "Comprehensive will be ~1000 words and take ~30 min — confirm?"

### Pattern Q-6: Subjective quantification

When the prompt has subjective words ("good", "fast", "professional"):

- "By 'fast', what's the metric — p99 latency, throughput, perceived response time?"
- "What's the current baseline, and the target?"
- "What's the trade-off you're willing to accept (cost, complexity)?"

This is where "make the API faster" becomes "reduce p99 from 800ms to <200ms."

### Pattern Q-7: Multi-task ordering

When the prompt bundles N tasks:

- "Order matters? Step 1 → Step 2 → Step 3, or any order?"
- "If Step 2 fails, do we still do Step 3?"
- "Should I report after each step, or just at the end?"

### Pattern Q-8: Refusal conditions

When the prompt skirts a sensitive area:

- "If I find a security issue while doing this, fix it or report and stop?"
- "If the change is bigger than expected, proceed or pause and confirm?"
- "Hard stop conditions — anything that should make me refuse and report?"

## The question-budget rule

Cap questions at 3-4 per round. If you have 8 questions, you've under-inferred. Re-read the prompt for things you can infer.

Some shortcuts to reduce questions:
- "Industry conventions" — if the prompt is in a domain (e.g., e-commerce checkout), default to industry-standard practices without asking
- "Prior context" — if the conversation has already established scope/format, don't re-ask
- "File attachments" — if the user uploaded a spec, infer constraints from there

## Question form: avoid yes/no traps

Don't ask binary questions when the answer space is wider:

```
✗ "Should the API return JSON?"
✓ "What format should the API return — JSON, XML, MessagePack, or other?"

✗ "Should I include error handling?"
✓ "For errors, do you want: (a) catch + log + retry, (b) catch + propagate,
   (c) fail fast and crash, or (d) something else?"
```

Yes/no traps the user into your assumption. Multi-choice respects that the answer space is broader than your prior.

## Question form: respect the user's time

Bundle related questions in one message. Don't drip-feed:

```
✗ Turn 1: "What format?"
✗ Turn 2: "What scope?"
✗ Turn 3: "What edge cases?"

✓ Single turn:
   "Before I start, three things:
    1. Output format: JSON / markdown / prose?
    2. Scope: just module X, or include Y?
    3. Edge case behavior on missing input: error, default, or skip?"
```

The bundled form lets the user respond once.

## Question form: provide defaults

When asking, provide what your default would be:

```
"Length: one paragraph (default), one page, or comprehensive?"
```

The user can confirm the default by saying "default" or pick a different option. This is faster than open-ended.

## When NOT to ask

Skip the interview when:
- The prompt is trivial (typo fix)
- Prior turns established everything
- Inference is high-confidence (the user's input + attachments make the answer clear)
- Asking would feel performative ("Of course this is a JSON API")

A prompt-improver that asks 5 questions on a 5-word task is annoying.

## When to ASK (vs. assume + caveat)

Sometimes the move is to assume + caveat rather than ask:

```
Assumption + caveat:
  "I'll generate this as JSON (standard for APIs). If you wanted XML / another
   format, say the word and I'll switch."
```

This is faster than asking. Use it when:
- The assumption is high-confidence
- The cost of being wrong is low (easy to redo)
- The user prefers velocity

Use ASK instead when:
- The cost of being wrong is high (e.g., schema decision baked into a migration)
- The user has signaled they want precision
- The space of plausible answers is wide

## Cross-references

- `skills/prompt-improver/` — parent skill
- `references/examples.md` — sibling reference (worked examples of improvements)
- `references/research-strategies.md` — when to research vs. ask
- `skills/interview-framework/` — deeper, structured intake protocol
- `skills/requirements-clarity/` — adjacent skill for requirements-specific clarification

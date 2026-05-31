# System Prompts — Prompt-Engineer's View

> Quick reference for system-prompt design from the prompt-engineer skill's perspective. The deeper treatment lives in `skills/prompt-engineering-patterns/references/system-prompts.md`.

## The system-prompt anatomy (recap)

Six components:

1. **Role / identity** — who is the model behaving as
2. **Capabilities + scope** — what's in / out
3. **Output format** — shape requirements
4. **Behavioral rules** — always / never
5. **Refusal policy** — what to decline
6. **Examples (optional)** — exemplar input/output pairs

Deep treatment of each: see the sibling cascade.

## Prompt-engineer's checklist for system prompts

When designing or reviewing a system prompt, walk this checklist:

- [ ] Is the **role** specific enough to shape defaults? ("senior security-conscious code reviewer" beats "helpful assistant")
- [ ] Is the **scope** explicit? (in / out / not-supported)
- [ ] Is the **output format** prescribed with a schema or example?
- [ ] Are **behavioral rules** stated as imperatives? ("you always X" / "you never Y")
- [ ] Are **refusal conditions** specific + paired with alternatives?
- [ ] Are **examples** present where the task is non-trivial?
- [ ] Is the system prompt **<500 words**? (longer is usually a sign to push detail to references/)
- [ ] Are the **most critical instructions at the start AND end**? (position bias)

A system prompt that ticks 7+ is usually production-ready.

## Common system-prompt failures the prompt-engineer skill fixes

### Failure: vague persona

```
Before: "You are a helpful coding assistant."
After:  "You are a senior backend engineer specialized in distributed systems.
         You think in terms of consistency, partition tolerance, and failure
         modes."
```

Specific domain expertise shapes the model's defaults — it stops giving generic answers and starts giving in-domain ones.

### Failure: no scope limit

```
Before: "Help users with code questions."
After:  "You answer questions about Python, TypeScript, Go, and Rust. You do
         not write code in other languages. You do not execute code. You do
         not access the internet."
```

Explicit scope prevents the model from drifting into out-of-domain territory.

### Failure: format-as-suggestion

```
Before: "Return the answer as JSON if possible."
After:  "Respond with valid JSON conforming to this schema:
         { 'reasoning': str, 'answer': any }
         Do not include any text outside the JSON object."
```

"If possible" reads to the model as "optional." Specific schema + "no text outside" produces parseable output reliably.

### Failure: friendly persona + safety rules

```
Before: persona=friendly + rules=refuses dangerous code
         (the friendly persona erodes the refusal under pressure)

After:  persona=security-conscious + rules=refuses dangerous code
         (aligned — the persona supports the rule)
```

Pick a persona whose natural disposition aligns with the constraints.

### Failure: critical rule buried in middle

```
Before: 800-word system prompt with the critical "always cite sources" rule
        in the middle paragraph.

After:  Critical rule at start ("Always cite sources for every claim.") +
        repeat at end ("Remember: every claim cites a source.")
```

Position bias is real. Critical rules anchor at start AND end.

## When to split into references/

If your system prompt grows past 500 words, consider:

```
SYSTEM: [base prompt, 200 words]
  + reference to: examples.md
  + reference to: refusal-policy.md
  + reference to: format-schema.md
```

This is the progressive-disclosure cascade pattern. The SKILL.md / SYSTEM stays focused; details live in references/*.md.

See `skills/prompt-engineering-patterns/references/system-prompts.md` for the full discussion.

## Anti-patterns specific to prompt-engineering

| Anti-pattern | Effect | Fix |
|---|---|---|
| Persona conflicts with rule | Persona wins under pressure | Align persona with rules |
| Length > 500 words | Model loses track of middle | Cascade to references/ |
| Output format buried | Format violations | Move to start AND end |
| Negative-only rules | Model lacks positive guidance | Pair "never X" with "always Y" |
| Refusal without alternative | User gets a wall | Pair refusal with redirect |

## Cross-references

- `skills/prompt-engineer/` — parent skill
- `skills/prompt-engineering-patterns/references/system-prompts.md` — deep treatment
- `references/prompt-patterns.md` — sibling pattern catalog
- `references/structured-outputs.md` — sibling for output format

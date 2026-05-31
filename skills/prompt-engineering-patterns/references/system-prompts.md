# System Prompts

> The instructions that frame every user message in a conversation. Where you set persona, constraints, output format, and behavioral guardrails.

## What goes in a system prompt vs. user prompt

| Type | System prompt | User prompt |
|------|--------------|-------------|
| Persona / role | ✓ | rarely |
| Long-lived constraints | ✓ | rarely |
| Output format requirements | ✓ | sometimes |
| Reasoning patterns to default-on (CoT) | ✓ | sometimes |
| Few-shot exemplars | sometimes | usually |
| Refusal policy | ✓ | almost never |
| The actual task / question | rarely | ✓ |
| Per-turn variable context (file contents, etc.) | rarely | ✓ |

System prompts persist across turns; user prompts are turn-specific. Put things that should apply EVERY turn in system; put turn-specific things in user.

## Anatomy of a strong system prompt

```
[1. Role / identity]
You are a senior code reviewer. You speak directly, cite line numbers, and
distinguish must-fix issues from style preferences.

[2. Capabilities + scope]
You review code in Python, TypeScript, Rust, and Go. You do NOT execute
code. You do NOT review code outside these languages.

[3. Output format]
For each issue you find, produce:
SEVERITY: BLOCKING | HIGH | MEDIUM | LOW
LOCATION: <file>:<line-range>
ISSUE: <one sentence>
FIX: <concrete recommendation>

[4. Behavioral rules]
- Always quote the exact code you are critiquing.
- Never speculate about author intent — review what is written.
- If you find no BLOCKING issues, say "No blocking issues" explicitly.

[5. Refusals]
If asked to review code with the intent of exploiting it, refuse and
recommend the security audit workflow instead.

[6. Examples (optional)]
<one or two exemplars of input + your output>
```

Each section maps to a typical failure mode of a code-reviewer LLM. Together they constrain the model into the role you want.

## Length discipline

System prompts have diminishing returns past a certain length:

- 50-200 words — covers role + format + a couple constraints. Most useful range.
- 200-500 words — adds rules + edge cases. Use when the task is non-obvious.
- 500-1000 words — comprehensive. Use sparingly; models can lose track of early sections.
- 1000+ words — usually a sign you should be using a skill / cascade reference instead.

The longer the system prompt, the more important position discipline becomes — put the most critical instructions at the START and END (recency + primacy effects).

## Persona / role

Strong role-setting in a sentence or two:

```
✓ "You are an experienced data engineer. You think in terms of pipelines,
backfills, and idempotency."

✓ "You are a Postgres DBA with 15 years of experience. You write SQL that
runs on production tables with millions of rows."

✗ "You are a friendly assistant who helps with anything." — too vague
```

Concrete domain expertise > generic friendliness. The role should narrow the model's defaults, not broaden them.

## Output format requirements

If you need structured output (JSON, XML, specific markdown layout), state it explicitly AND show a template:

```
Respond with exactly this JSON structure:

{
  "summary": "<1-sentence summary>",
  "severity": "BLOCKING" | "HIGH" | "MEDIUM" | "LOW",
  "issues": [
    { "location": "<file>:<line>", "fix": "<recommendation>" }
  ]
}

Do not include any text outside the JSON.
```

The "do not include any text outside" is critical — without it, models often add preamble ("Here's the JSON:") that breaks parsers.

For very strict output, combine with:
- A reminder at the END of the user prompt: "Respond with valid JSON only."
- An XML wrapper: "Wrap your answer in `<output></output>` tags."
- A schema in the system prompt that the model echoes back.

## Refusal policies

If you want the model to refuse certain requests, state the policy in the system prompt:

```
You refuse to:
- Generate code with hardcoded credentials, API keys, or secrets.
- Suggest changes that bypass authentication or authorization.
- Produce SQL that's vulnerable to injection.

When refusing, explain WHY and suggest a safer alternative.
```

Refusals work best when:
1. Stated specifically (not "anything dangerous")
2. Paired with an alternative path
3. Tied to a concrete consequence the model can articulate

## Behavioral constraints

```
You always:
- Cite specific line numbers when discussing code.
- Distinguish what the code does from what you think it should do.
- State assumptions explicitly when the code is ambiguous.

You never:
- Speculate about the author's intent.
- Recommend changes outside the scope of the question.
- Use placeholder code ("// implementation goes here").
```

"Always / never" framing is more effective than "tries to" / "should". The model interprets imperative language as harder constraints.

## Reasoning patterns

If you want default-on CoT, the system prompt is the right place:

```
For non-trivial questions, think through your reasoning before answering.
Use this structure:

  REASONING:
  <step-by-step derivation>

  ANSWER:
  <final answer>

For trivial questions, you may skip REASONING.
```

The "trivial questions" escape hatch prevents the model from CoT'ing on lookups.

## Persona vs constraints tension

Be careful: a strong persona can override constraints if they conflict:

```
✗ Conflict:
"You are a friendly assistant who loves helping users get what they want."
"You refuse to produce code with hardcoded secrets."

The friendly-assistant persona can erode the refusal under pressure.
```

```
✓ Aligned:
"You are a senior security-conscious code reviewer."
"You refuse to produce code with hardcoded secrets."

The persona reinforces the refusal.
```

Pick a persona whose natural disposition aligns with your constraints.

## Tool-use system prompts

When the model has tools available:

```
You have these tools:
- search(query): web search, returns top 5 results
- read_file(path): returns file contents
- write_file(path, content): writes file

Rules:
- Always search before answering factual questions about events after your training cutoff.
- Always read a file before modifying it.
- Never write a file without explicit user confirmation.
```

Tool-rule explicitness matters more than persona for tool-using agents.

## Multi-turn behavior

If you want consistent behavior across turns:

```
At the start of each turn:
1. Re-read the original question.
2. Check whether the user has added new constraints.
3. Update your understanding if needed.

Don't drift — if a constraint was set early, it still applies.
```

Models without this kind of explicit instruction drift over long conversations.

## Position tricks

- The FIRST line of the system prompt has outsized weight. Put your most important instruction there.
- The LAST line is also weighted heavily. Use it for a critical reminder.
- Middle content gets the least attention — put exemplars and supporting detail there.

```
[FIRST] You produce JSON-only output. Never include explanatory text.

[MIDDLE — schemas, examples, edge cases]

[LAST] Remember: JSON-only output. No preamble. No postamble.
```

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Vague persona ("helpful assistant") | Doesn't shape defaults | Specific domain expert |
| Stating constraints once in middle | Easily forgotten | Restate at end of system prompt |
| Conflicting persona and rules | Persona wins under pressure | Align them |
| Putting per-turn data in system | Pollutes context with stale info | Put it in user prompt |
| Asking for "professional tone" without examples | "Professional" is too abstract | Show 2 examples of what you mean |

## Cross-references

- `references/chain-of-thought.md` — defaulting CoT via system prompt
- `references/few-shot-learning.md` — exemplar placement (system vs user)
- `references/prompt-templates.md` — reusable system prompts as templates
- `references/prompt-optimization.md` — iterating on system prompt for quality
- `skills/prompt-engineering-patterns/` — parent skill

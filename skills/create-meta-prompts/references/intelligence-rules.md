# Intelligence Rules

This reference is loaded by `create-meta-prompts` step 1 alongside the purpose-specific patterns. It defines when generated prompts should invoke extended-thinking, parallel-tool patterns, and depth-decision heuristics.

The point of these rules: a generated prompt is read by another Claude. Telling that Claude when and how to think hard, when to run tools in parallel, and when to stop early produces measurably better outputs.

## Extended thinking

Add an extended-thinking instruction when:

- The Purpose is Plan or Research
- The artifact is decision-critical (architecture, security, multi-stakeholder)
- The user explicitly said "think deeply", "consider carefully", "evaluate alternatives"
- The prompt has 3+ decisions that interact

Template line to inject:

```
At the start, think extended-mode about: {topic boundaries, decision criteria, edge cases}.
Spend ~5–15 minutes in thinking before producing the artifact.
```

Do NOT add extended thinking for:
- Simple Do prompts (single file change, well-scoped)
- Pure information-retrieval research (look it up, write it down)
- Refine prompts unless the refine itself is non-trivial

## Parallel tools

When a prompt's research or context-gathering involves independent reads/searches, instruct the executor to do them in a single message.

```
For initial context, run ALL of these in parallel in one message:
- Read @<file-A>
- Read @<file-B>
- Grep "<pattern>" in <dir>
- Documentation-research --library <name>

Synthesize the four results together.
```

The phrasing matters: "in a single message" is the activation trigger that Claude treats as "do these in parallel via the Task tool block or by batching tool calls".

## Depth decisions

For Research and Plan prompts, instruct the executor to decide research depth from signals:

```
Research depth signals:
- High-risk topic (auth, payments, data) → deeper
- Existing-pattern question (does our codebase do X?) → grep, no web
- Brand-new pattern (best library for Y?) → official docs + 1 community source
- Compliance / standards question → primary source only (OWASP, NIST, RFC)

Stop researching when:
- The gap is closed
- The next source restates the previous
- The remaining ambiguity is product-strategy uncertainty, not knowledge gap
```

## Iron Rule reminder

Every generated prompt must restate the Iron Rule when the artifact will be built and executed:

```
Iron Rule applies to this prompt:
- NO test files (.test.*, _test.*, *Tests.*, test_*)
- NO mocks, stubs, in-memory databases
- NO test mode flags
- Validation via REAL SYSTEM only (real backend, real DB, real screenshot)
```

Embed this near the top of Do prompts and inside the Validation section of Plan prompts.

## Confidence reporting

Every Research and Plan prompt must produce a `<confidence>` element. The executor must self-report:

```
At the end of the artifact, include:
<confidence>high|medium|low</confidence>
<rationale>One sentence on what would change the confidence.</rationale>
```

Confidence is per-document, not per-finding (per-finding confidence is for Research-specific patterns).

## Open questions discipline

Research and Plan prompts must instruct the executor:

```
If you encountered any uncertainty during research/planning, list it under
<open_questions>. Do not silently resolve uncertainty by guessing. Each open
question must have:
- The question
- Why it's open (what evidence is missing)
- Suggested owner (PM, security, design, etc.)
- Resolution trigger (what would close it)
```

## Streaming-write rule

Long-running prompts should write incrementally:

```
Write findings/decisions to the output file AS YOU PRODUCE THEM. Do not buffer
the entire artifact in memory and write at the end. If your context overflows
mid-task, partial output is recoverable; buffered output is lost.

Use Edit tool to append sections; never re-write the whole file from scratch
mid-task.
```

This is especially important for Research prompts (which can span many sources) and large Plan prompts.

## Self-verification before submit

End every generated prompt with a self-verification block:

```
Before declaring complete, verify:
- [ ] Output file exists at the specified path
- [ ] Output file has more than 100 characters (not empty / placeholder)
- [ ] All required XML/metadata blocks present
- [ ] SUMMARY.md exists and has all required sections
- [ ] One-liner in SUMMARY.md is substantive (not "Task completed")
- [ ] No mocks, tests, or fabricated evidence anywhere in the output
- [ ] Citations resolve (links work, file paths exist)
```

The executor reads these and double-checks before claiming success.

## Anti-patterns

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Adding extended thinking to every prompt | Slows trivial tasks; user pays in latency | Reserve for decision-critical work |
| Instructing parallel tools when there's only one tool call needed | Cargo-cult parallelism; no benefit | Only inject parallel instruction when ≥3 independent fetches |
| Restating Iron Rule for pure research / docs prompts | Iron Rule doesn't apply (no system built) | Restate only for Do/Plan with executable outputs |
| Vague self-verification ("check your work") | Executor doesn't know what to check | Always concrete, checklist-style verification |
| Confidence reporting only at the end | Mid-stream low confidence gets lost | Encourage early flagging of low-confidence sections |

## Composition rules

When multiple intelligence rules apply, the order is:

1. Extended thinking instruction (top of prompt)
2. Parallel-tools instruction (in the Context section)
3. Iron Rule reminder (after Context, before Tasks/Findings)
4. Streaming-write instruction (in Output Specification)
5. Open-questions discipline (in Output Specification)
6. Self-verification checklist (at the very end of the prompt)

Each block is short (3–8 lines). Total intelligence-rule overhead per generated prompt should be under 50 lines.

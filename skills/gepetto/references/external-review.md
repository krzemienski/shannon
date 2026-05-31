# External Review

> The discipline of running another LLM (Codex, Gemini, or a different Claude generation) as an independent reviewer of an artifact. The "external" part is what gives the review credibility.

## Why external review

Single-model review has a known weakness: the model that produced an artifact often misses the same things when reviewing it. The cognitive blind spots are the same.

External review uses a DIFFERENT model — different training data, different architecture, different default biases — to scrutinize. The differences in the model's defaults surface blind spots the original review missed.

This is the same logic that drives:
- Pair programming (human + human, different priors)
- Multi-judge consensus (`judge-with-debate`, `consensus-engine`)
- Cross-model evaluation in research (GPT vs Claude vs Gemini)

## When to invoke external review

External review is high-value when:
- The artifact has high cost-of-being-wrong (production-bound decisions, security review, irreversible operations)
- The original author may have blind spots specific to the topic
- Stakeholders need a second opinion before committing

External review is low-value (skip) when:
- The artifact is trivial
- The reviewing model wouldn't be more informed than the original
- Latency / cost matter more than confidence

## Reviewer model selection

| Reviewer | When to use |
|----------|-------------|
| Codex / GPT | Code review, especially when adversarial scrutiny is helpful |
| Gemini | Long-context review (200k+ tokens); broad-knowledge questions |
| Different Claude generation | When neither of the above adds enough delta |
| Specialized models (e.g., MedPaLM for medical) | Domain-specific expertise |

The principle: pick a reviewer whose biases differ from the original author's.

## Review prompt structure

A strong external-review prompt:

```
You are reviewing an artifact produced by a different model. Your job is
NOT to rewrite. Your job is to find issues, ambiguities, missing
considerations, and blind spots.

The artifact:
<paste artifact>

The context the original author had:
<paste relevant context>

Output your review as:

# Strengths
- {what the artifact does well}

# Issues (ordered by severity)
- BLOCKING: {issues that must be fixed before this ships}
- HIGH: {issues that should be fixed}
- MEDIUM: {improvements}
- LOW: {style / nice-to-have}

# Blind spots
- {topics the original author may have missed entirely}

# Verdict
APPROVED | APPROVED_WITH_CHANGES | REJECTED

# Rationale
{2-4 sentences supporting the verdict}
```

The structure pre-constrains the review into useful shape.

## What external review catches that internal misses

Empirically, the most common external-review wins:

1. **Implicit assumptions** — the author assumed X without stating it; the reviewer notices because they didn't share the assumption.
2. **Domain confusion** — the artifact uses jargon from domain A in a way that's wrong by domain B's conventions.
3. **Missing edge cases** — the author covered cases they thought of; the reviewer thinks of cases the author didn't.
4. **Style inconsistency** — internal consistency is hard for one model; an external reader sees the inconsistency immediately.
5. **Over-confident claims** — the author hedged appropriately on what THEY knew was uncertain; the reviewer flags claims the author didn't realize were uncertain.
6. **Format drift** — the author followed the format approximately; the reviewer catches the drift.

## Aggregating multi-reviewer output

If you have 2-3 external reviewers, aggregate:

```
For each issue:
  - All reviewers flag it → BLOCKING
  - Multiple reviewers flag → HIGH
  - Single reviewer flags → MEDIUM (worth investigating)
  - No reviewer flags but author flagged → original assessment stands
```

When reviewers disagree:
- Pick the more conservative position
- OR escalate to judge-with-debate (see `skills/judge-with-debate/`)
- OR put the disagreement in front of a human

## Cost / quality trade-off

External review adds cost (extra LLM call) and latency (sequential). The trade-off:

| Stakes | Recommendation |
|--------|----------------|
| Trivial change | Skip external review |
| Internal-only artifact | Optional |
| External-facing (docs, API contracts) | Single external reviewer |
| Production-bound (deploy, schema migration) | Multi-reviewer + consensus |
| Irreversible (release, deletion) | Multi-reviewer + debate on disagreements |

## Review hygiene

- **Reviewer doesn't see the prior review.** Independent reviews give independent signal. Pipelining contaminates.
- **Reviewer gets the same context the author had.** Otherwise the review is mis-calibrated.
- **Don't let the reviewer rewrite.** The job is scrutiny, not authorship. Rewrites should go back to the author.
- **Log the review.** Future revisions cite the review; future reviewers see what was already addressed.

## Cross-references

- `skills/gepetto/` — parent skill
- `references/interview-protocol.md` — how to elicit good review inputs
- `references/research-protocol.md` — research that informs review
- `references/section-index.md` — structuring the artifact for review
- `skills/judge/`, `skills/judge-with-debate/` — single-model judge patterns
- `agents/meta-judge.md` — rubric generation before external review runs
- `skills/codex/`, `skills/gemini/` — invoking other LLMs
- `skills/ccg/` — Claude-Codex-Gemini tri-model orchestration

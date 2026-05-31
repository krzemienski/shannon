# Interview Protocol

> Gepetto's stakeholder-interview pattern for capturing rich context BEFORE planning. Borrowed from ralph-specum's interview-framework, adapted for multi-LLM review contexts.

## The protocol

```
Phase 1: Surface the implicit assumptions
Phase 2: Surface the constraints
Phase 3: Surface the trade-offs the user is willing to accept
Phase 4: Confirm + store the interview output
```

Each phase has 2-4 questions. The output of the interview is the "intent doc" that gepetto plans against.

## Phase 1 — Assumptions

Goal: surface what the user thinks is obvious but might not be.

Sample questions:
- "What's the existing context this is built on? (Codebase, prior work, current process)"
- "What stays the same after this work? Anything that explicitly shouldn't change?"
- "Who's the audience / user of the output?"
- "What does 'production-ready' mean in this context?"

The user's answers reveal their model of the problem. Mismatches between their model and yours become explicit.

## Phase 2 — Constraints

Goal: enumerate hard constraints and soft preferences.

Sample questions:
- "Hard constraints: what's not negotiable?" (compliance, performance, contract)
- "Soft preferences: where can we trade off?"
- "Time bound: when do you need this by?"
- "Cost / token / latency budget?"

Constraints scope the plan. Without them, gepetto produces options the user can't accept.

## Phase 3 — Trade-offs

Goal: where the user's willing to accept compromise.

Sample questions:
- "If we have to choose between X and Y, which matters more?"
- "Failure modes: which class of failure is least acceptable?"
- "If this ships with a known limitation, which limitations are tolerable?"

This phase distinguishes between "the user wants X and Y and Z" (impossible) and "the user wants X and Y, will tolerate trade-off on Z" (achievable).

## Phase 4 — Confirm + store

Goal: write the captured intent to disk so it survives context drops.

Output structure (`.gepetto/interview-<topic>.md`):

```markdown
# Interview — {topic}

## Assumptions (Phase 1)
- {captured assumption 1}
- {captured assumption 2}

## Constraints (Phase 2)
- Hard: {must-haves}
- Soft: {preferences}
- Time: {deadline if any}
- Budget: {cost / latency / token limits}

## Trade-offs (Phase 3)
- {when forced to choose, here's the priority order}
- {tolerable limitations}

## Open questions
- {questions the user couldn't answer; deferred or flagged}
```

This file becomes the input to gepetto's planning + section-index phases.

## Interview anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Asking ALL the questions every time | Annoys user; ignores prior context | Ask only what's not already known |
| Yes/no traps | User confirms your assumption | Multi-choice + escape hatches |
| Drip-feeding (one question per turn) | Wastes user attention | Bundle related questions |
| No defaults | User can't quickly accept the obvious | Always propose a default the user can confirm |
| Skipping Phase 4 (storage) | Intent lost on context drop | Always write to disk |

## Multi-stakeholder interviews

When the artifact will serve multiple stakeholders (engineering + product + design), interview each separately. Then surface conflicts in Phase 4.

Conflict example:
```
- Engineering wants: maintainability over delivery speed
- Product wants: delivery speed over edge-case coverage
- Conflict: maintainable code takes longer; quick delivery may skip edge cases.

Resolution needed: where does the team draw the line?
```

Gepetto's planning step asks the user (or a higher-level decision-maker) to resolve the conflict before continuing.

## Cross-references

- `skills/gepetto/` — parent skill
- `references/external-review.md` — what the interview output feeds into
- `references/research-protocol.md` — when research informs questions
- `references/section-index.md`, `section-splitting.md` — how interview-output structures the artifact
- `skills/interview-framework/` — the more general intake-interview skill

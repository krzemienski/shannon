# Interview Algorithm — 3 Phases

> The structured intake protocol that runs BEFORE planning starts. Three phases: Understand, Propose Approaches, Confirm and Store. Adapted from ralph-specum's interview pattern.

## When this runs

Before any spec or plan phase. Specifically:
- `/shannon:plan` — before writing PLAN.md
- `/shannon:spec` — before generating the spec
- `/shannon:autopilot` — Phase 0 expansion when input is vague
- Any skill that asks "what does the user actually want before I commit to a plan?"

## Why three phases

The most common planning failure: writing a great plan that doesn't match what the user actually wanted. Three phases prevent this by forcing intent capture before output generation.

```
Phase 1: UNDERSTAND      What is the user actually asking for?
Phase 2: PROPOSE          Given that, what are the 2-3 sensible approaches?
Phase 3: CONFIRM + STORE  Lock in the chosen approach + write it down so it survives context drops.
```

Skipping any phase produces a plan that drifts.

## Phase 1 — Understand

Goal: build a structured representation of intent from the user's (often vague) input.

### Inputs

- The raw user request (1 sentence or 1 paragraph, typically)
- Any context files the user has attached
- Any prior conversation history

### Activities

1. **Identify the noun.** What is this PLAN for? (a feature, a refactor, a migration, a research question, a release)
2. **Identify the goal.** What does "done" look like for THIS request?
3. **Identify constraints.** Hard constraints (must use X), preferences (would like Y), explicit non-goals (do NOT touch Z).
4. **Identify deferred decisions.** What is the user explicitly saying "you decide" vs "I'll tell you later"?

### Questions to ask (only the ones the input doesn't answer)

```
[Identification questions — only if unclear]
- "Is this for the existing codebase, or a new project?"
- "Which module is this scoped to?"

[Goal questions]
- "What does 'done' look like for this?"
- "What's the smallest version that ships?"

[Constraint questions]
- "Anything I must NOT touch?"
- "Any tech / library / pattern you want me to prefer?"
- "What's the budget — small / medium / large?"

[Defer questions]
- "Is there anything you want to defer to a later phase?"
```

Critical: ask ONLY the questions whose answers you can't infer from input. Asking for things already clear annoys the user and signals you didn't read.

### Output of Phase 1

A structured intent object:

```yaml
intent:
  noun: "feature | refactor | migration | research | release | other"
  short_name: "JWT auth migration"
  goal: "Migrate the auth module from session cookies to JWT with httpOnly"
  scope:
    in: ["auth module", "session-handler middleware", "login/logout endpoints"]
    out: ["UI changes", "OAuth providers", "anything in /admin/*"]
  constraints:
    must:
      - "All existing tests continue to pass"
      - "No client-side token storage (httpOnly cookies only)"
    prefer:
      - "Use jose library if possible"
      - "Refresh rotation per OWASP"
    forbid:
      - "Don't touch the user model schema"
  deferred:
    - "Refresh token lifetime — propose, I'll confirm"
    - "Library choice if jose has issues — propose alternative"
  inferred:
    - "User wants reversibility (mentioned 'careful migration')"
    - "User cares about security (JWT + httpOnly, not localStorage)"
```

## Phase 2 — Propose Approaches

Goal: surface 2-3 sensible ways to accomplish the intent, with trade-offs.

### Why multiple approaches

A single approach hides the trade-off space. The user might choose differently than your default if they see the alternatives. Surfacing alternatives also catches misunderstood intent — if the user picks the alternative you didn't recommend, you mis-read their preferences.

### Approach structure

For each approach (target 2-3):

```yaml
approach:
  name: "Big bang migration"
  summary: "Replace session-based auth across all endpoints in one commit"
  pros:
    - "Simpler — no dual-mode complexity"
    - "Faster — fewer commits, less coordination"
  cons:
    - "Higher risk — if it breaks, everything breaks"
    - "Hard to rollback"
  effort: "MEDIUM"
  risk: "HIGH"
```

### Inferred vs. recommended

Mark which approach you'd recommend AND why. Also surface the approach you'd NOT recommend AND why.

```
Recommended: phased migration (lowest risk)
Not recommended: big bang (high risk + hard rollback)
Alternative: keep both auth modes long-term (lowest risk but accumulates complexity)
```

### Output of Phase 2

Present approaches to the user via AskUserQuestion / elicitation form / inline question. Get a CHOICE.

## Phase 3 — Confirm and Store

Goal: lock the chosen approach into a written intent doc that survives context drops.

### Why "store"

The interview output disappears when context drops. If you continue planning without writing it down, the next prompt (or the next conversation turn) has to re-elicit the same intent.

Storing the intent doc to disk means:
- Successor agents can read it
- The user can review it before approving the plan
- It serves as the contract between the interview and the plan

### Storage location

```
.planning/intake/{topic}-intake.md
```

Or, for Shannon-style workflows:

```
.v7/decisions/{phase}-input.json
.shannon/spec/{topic}-spec.md
```

### Structure of stored intent

```markdown
# {topic} — Intake

**Stored**: 2026-05-27T10:00:00Z
**Phase**: pre-plan (after interview)

## Intent
{Phase 1 output verbatim}

## Approach Chosen
{Phase 2 output — the approach the user picked, full structure}

## Confirmations
- User confirmed scope on 2026-05-27.
- User chose phased migration (over big bang or dual-mode-forever).
- User deferred refresh-token-lifetime to plan-author.

## Open Questions
{Anything still unresolved}

## Next
The plan phase consumes this file as its primary input.
```

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Skipping Phase 1, starting on Phase 2 | Propose approaches in a vacuum, miss intent | Always Understand first |
| Asking every possible question | Annoys user, signals inability to infer | Ask ONLY what you can't infer |
| Single-approach Phase 2 | Hides the trade-off space | Always 2-3 alternatives with pros / cons |
| No "not recommended" approach | User can't tell what you'd avoid | Always mark recommended + anti-recommended |
| Skipping Phase 3 | Intent lost on context drop | Always write intake.md to disk |
| Intake.md without the chosen approach | Successor agent doesn't know what to plan | Include approach choice + rationale |

## Cross-references

- `references/examples.md` — worked interview examples
- `skills/plan-author/` — consumes intake.md as input
- `skills/spec-workflow/` — alternate consumer (ralph-specum style)
- `skills/interview-framework/` — parent skill

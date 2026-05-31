# Scope Estimation

> Predicting whether a planned phase will complete within a healthy context budget. Too-large phases produce degraded output; too-small phases produce overhead.

## The context-budget reality

LLMs degrade as context fills. Key thresholds:

- **0-30%**: peak quality
- **30-50%**: good quality, engaged
- **50-70%**: degrading, efficiency mode
- **70%+**: poor quality, self-lobotomization, rushed work

Critical insight: degradation begins around 40-50%, NOT 80%. By 80%, quality has already crashed.

**Aim to complete each phase within ~50% context usage.** If a phase will use more, split it.

## Phase-size heuristics

| Tasks per phase | When OK |
|-----------------|---------|
| 1 | Tiny phase — fix or single edit; often not worth a separate phase |
| 2-3 | Sweet spot — most phases |
| 4-5 | Acceptable if tasks are tight |
| 6+ | Almost always too large; split |

Each "task" should be itself atomic — one logical change, verifiable on its own.

## Why aggressive atomicity

Many small phases vs. few large phases:

| Many small | Few large |
|-----------|-----------|
| Peak quality every phase | Quality degrades within each |
| Easy to revert one bad phase | Hard to revert when bundled |
| Each commit is review-able | Huge commits resist review |
| Restart context cheaply between phases | Stuck if one phase blows up |

The "many small" tradeoff: more planning overhead. Worth it for non-trivial work.

## Estimating context usage

For a phase, sum:

| Factor | Token estimate |
|--------|---------------|
| Phase prompt itself | ~5K tokens |
| Files Claude needs to Read | sum of (file_size / 4) for each |
| Files Claude needs to Write | sum of (target_size / 4) |
| Tool calls Claude will make | ~200 tokens per tool call (in + out) |
| Reasoning + intermediate thoughts | ~30% overhead |

Multiply by 1.3 for safety margin.

If the estimate exceeds 100K tokens (50% of a 200K context), the phase is too large.

## Decomposition strategies

When a phase is too large, decompose:

### Strategy: Vertical slice

Split by feature dimension:

```
Bad: "Implement entire user system"
Better:
  Phase 1: User registration
  Phase 2: User login
  Phase 3: Password reset
  Phase 4: Email verification
```

Each phase ships a usable feature.

### Strategy: Layer slice

Split by architectural layer:

```
Bad: "Implement orders feature"
Better:
  Phase 1: DB schema + migrations for orders
  Phase 2: API endpoints
  Phase 3: Frontend (list view)
  Phase 4: Frontend (detail view)
```

Each layer is verifiable independently (DB query works, API curl works, etc.).

### Strategy: Action slice

Split by user action:

```
Bad: "CRUD for sessions"
Better:
  Phase 1: Create + List
  Phase 2: Read (detail view)
  Phase 3: Update
  Phase 4: Delete + confirmation flow
```

## When phases are too small

The opposite problem: 20 trivial phases for what could be 3 substantive ones.

Smells:
- A phase has 1 task
- Multiple consecutive phases all touch the same file
- The planning overhead exceeds the work

Merge phases when:
- They touch related code closely
- The combined size fits comfortably in one context budget
- The combined verification can be a single step

## Estimation accuracy improves over time

Your first plan's estimates will be off. Track:

```yaml
phase: 02-01
estimated_tokens: 30K
actual_tokens: 47K
estimated_minutes: 20
actual_minutes: 35
notes: "Underestimated number of files needing edits"
```

Build a calibration spreadsheet. Next plan's estimates will be more accurate.

## Estimating without context

Sometimes you must estimate before knowing exact files. Heuristics:

| Phase type | Typical size |
|------------|-------------|
| Small bug fix | 5-15K tokens, ~10 min |
| New small feature | 30-50K tokens, ~30-60 min |
| Refactor (touching ≤5 files) | 30-60K tokens, ~30-60 min |
| Refactor (touching 10+ files) | TOO LARGE — split |
| New medium feature (UI + API + DB) | 80-150K tokens — borderline; usually split |
| Migration / cross-cutting change | TOO LARGE — split by region |

When in doubt, err smaller. Splitting late is harder than splitting early.

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/checkpoints.md` — checkpoints at split boundaries
- `references/user-gates.md` — context-budget gates
- `references/milestone-management.md` — milestone-level estimation
- `references/git-integration.md` — atomic-commit alignment with phase atomicity

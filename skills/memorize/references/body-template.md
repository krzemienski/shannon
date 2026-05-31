# Memory Body Template

> The structure for the body of memory files. Names + descriptions live in the index (`MEMORY.md`); the body is the substantive content that captures the actual learning.

## Why a template

Without a template, memories drift in shape. One has bullet points; another has prose; a third has a code snippet. Future retrieval becomes guesswork — "did I write that as a bullet or a paragraph?"

A consistent template means:
- Same anchor sections every time
- Easier scan-and-retrieve in future sessions
- Future-you can pattern-match on the structure even before reading content

## Required structure (all types)

```markdown
---
name: {{short-kebab-case-slug}}
description: {{one-line summary — used to decide relevance in future conversations}}
metadata:
  type: {{user, feedback, project, reference}}
---

{{Body content — see type-specific templates below.}}
```

The frontmatter is identical across types. The body shape varies.

## Type-specific body templates

### User memory

Captures a stable fact about the user's role, preferences, or context.

```markdown
{{Brief statement of what was learned about the user.}}

Source: {{The exchange where this came up — short quote or context.}}

Implications: {{How this should change my future behavior — what to do or avoid.}}
```

Example:

```markdown
The user is a senior data engineer focused on pipeline reliability. They
specifically mention durability, idempotency, and backfills as design
priorities.

Source: "Anything I build, I think about: what happens if it crashes
mid-batch? Can I re-run it? That's job one."

Implications: When proposing data pipeline designs, lead with
durability/idempotency analysis; treat happy-path performance as a
secondary concern.
```

### Feedback memory

Captures guidance about how to approach work. The most important type for retention.

```markdown
{{The rule, stated as a directive.}}

**Why:** {{Reason the user gave — often references a past incident or strong preference.}}

**How to apply:** {{When/where this guidance kicks in. Specific situations, not abstract principles.}}
```

Example:

```markdown
Never propose ORM-level mocks for integration tests in this codebase.

**Why:** Last quarter, an ORM mock passed but the production query against
the real schema failed on column-rename. The user's mandate since: real
DB in test environment, even if slower.

**How to apply:** When the user mentions testing data-access code, propose
docker-compose Postgres + real migrations, not a mock layer. If asked
specifically "what about speed?", reference the past incident.
```

The **Why** + **How to apply** structure is what makes feedback memory survive context — it lets future-me judge edge cases rather than blindly applying the rule.

### Project memory

Captures the WHO/WHY/WHEN of ongoing work that isn't in code or git history.

```markdown
{{The fact or decision.}}

**Why:** {{Motivation — typically a constraint, deadline, or stakeholder ask.}}

**How to apply:** {{How this should shape my suggestions.}}
```

Example:

```markdown
The auth middleware rewrite is driven by legal/compliance, not tech-debt
cleanup. Legal flagged session-token storage in late Q3-2025 for not meeting
new SOC2 requirements.

**Why:** Compliance audit on 2025-12-15 will check token handling. Failing
the audit blocks the Enterprise contract.

**How to apply:** Scope decisions should favor compliance over ergonomics.
If a proposal would be cleaner with a non-compliant pattern, flag it
explicitly and propose the compliant version too.
```

Project memories age fast — the **Why** lets future-me judge whether the memory is still load-bearing or now-stale.

### Reference memory

Captures pointers to where to look in external systems.

```markdown
{{What kind of information lives there.}}

**Path / URL:** {{Concrete location.}}

**Use when:** {{Triggers that should make me check this resource.}}
```

Example:

```markdown
Pipeline-bug tickets live in the Linear project "INGEST".

**Path / URL:** https://linear.app/teams/ingest

**Use when:** the user references a bug number, mentions a pipeline failure,
or asks about ETL incidents.
```

## Body length

Memories aren't documents. The body should be:
- ≤200 words for user / feedback / project / reference memories
- ≤50 words for trivial facts

If the body grows past 300 words, the memory is doing too much. Split it into multiple memories or move detail to a project-doc.

## Linking related memories

Link liberally via `[[other-memory-slug]]`:

```markdown
The user prefers integration tests with real DB containers (see
[[testing-philosophy]] for the underlying rationale).
```

Links don't have to point at memories that exist yet — a `[[future-slug]]` is a placeholder that says "if I learn more about this, write it under this slug."

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Body without Why | Future-me can't judge edge cases | Always include **Why** for feedback / project |
| Body without How to apply | Memory becomes trivia, not behavioral guidance | Always include **How to apply** |
| 500-word body | Defeats the scan-and-retrieve purpose | Cap at ~200 words; split if needed |
| Memory of architecture / patterns / file paths | Derivable from current code state | Skip; trust code+git as authoritative |
| Memory of git log facts | `git log` is authoritative | Skip |
| Memory of debugging fixes | Commit message captures it | Skip |

## Cross-references

- `skills/memorize/` — parent skill
- `skills/consolidate-memory/` — pruning + deduplication pass
- `skills/learner/` — quality gate that decides what's memory-worthy

# SUMMARY.md template

> The standard structure for the executive summary that every Claude-to-Claude pipeline prompt produces. SUMMARY.md is the file humans read; the main output file is what downstream prompts consume.

## Why SUMMARY.md exists

A 4,000-line research / plan / implementation output is unreadable for a human scanning whether the work was useful. SUMMARY.md is the 30-second scan version. It exists to answer:

1. Is the one-liner substantive (not "Research completed")?
2. What are the top findings?
3. What requires a decision from me?
4. What was blocked?
5. What's next?

If a SUMMARY.md doesn't answer all five, it's incomplete.

## Required structure

```markdown
# {Topic} — Summary

**{ONE-LINER — substantive, specific, action-oriented}**

## Version
v1 (initial) | v2 (refinement after feedback) | …

## Key Findings
- {Finding 1 — concrete and citable}
- {Finding 2}
- {Finding 3}
- ... (5-10 bullets)

## Files Created
- {full path 1}
- {full path 2}
- ... (only the artifacts the user can open)

## Decisions Needed
{Numbered list of things requiring user input before next step}
{If none: "None — ready for next step"}

## Blockers
{External impediments — auth issues, missing dependencies, etc.}
{If none: "None"}

## Next Step
{Concrete forward action — usually invokes the next prompt in the chain}
```

## The one-liner test

The one-liner is the most-read piece. It must be SUBSTANTIVE — meaning specific enough that someone reading it alone gets useful signal.

```
✗ "Research completed."
✗ "Found several issues."
✗ "Plan ready."

✓ "JWT with jose library + httpOnly cookies recommended; refresh rotation
   required per OWASP."
✓ "Found 14 skills where anthropic-skills version is substantially stronger;
   11 adopt-candidates identified; 187 MB of root cruft to archive."
✓ "Phase 3 implementation landed: 23 commits on dev, 14 skill migrations,
   12 improvements implemented, 187 MB archived, 7 docs created."
```

Substantive = specific numbers, specific names, specific verdicts. Generic = "Done", "Completed", "Several".

## Key Findings discipline

- Each bullet stands on its own — readable without surrounding context.
- Lead with the verdict / number / name.
- Avoid "I found that..." — start with what you found.
- 5-10 bullets is the sweet spot. More than 10 = move detail to the main output.

```
✗ "I investigated authentication options and found that JWT seems good."
✓ "JWT outperforms session cookies for stateless APIs; chosen for our case."
```

## Decisions Needed precision

Each decision must be:
- Numbered
- Self-contained
- Have a default if possible
- Reference where the decision came from (audit ID, finding number, etc.)

```
✗ "Need to decide on the authentication approach."

✓ "1. Confirm JWT over session cookies (recommendation: JWT — see audit GM-12)
   2. Choose refresh token lifetime (recommendation: 7 days — see GM-15)
   3. Choose JWT library: jose (HIGH support) vs jsonwebtoken (legacy)"
```

If the user submits a form for these, capture the answers in a follow-up SUMMARY.md v2.

## Blockers vs. Decisions

These are different:
- **Decisions Needed** — the user needs to make a choice. The work is ready to continue once they choose.
- **Blockers** — an external impediment exists. Even with a decision, you can't continue until the blocker clears.

```
Decision: "Choose database: Postgres vs SQLite"
Blocker:  "Database credentials are missing from .env"
```

## Next Step precision

The Next Step is a concrete action, usually a prompt invocation or a command:

```
✗ "Continue with implementation."
✗ "Wait for user response."

✓ "Run prompt 002-shannon-v7-cleanup-architecture-plan.md, which consumes this
   audit's gap matrix to produce the v7 architecture and 10+ improvements plan."
✓ "User runs `bash /Users/nick/Desktop/shannon-framework/.v7/apply.sh` on host
   to land the dev branch + archive. Then re-invokes autopilot to resume Phase 5."
```

## Chained-prompt SUMMARY hygiene

When SUMMARY.md is part of a chain (one prompt's output feeds the next prompt), the Next Step should reference the next prompt by path:

```
## Next Step
Run prompt `.prompts/003-shannon-v7-implement-do/003-shannon-v7-implement-do.md`,
which consumes this plan's <migration> blocks + <improvement> blocks to land
the changes on the dev branch.
```

This lets a successor agent (or a human) follow the chain without context.

## When SUMMARY.md is updated

Two patterns:

### Pattern 1: Versioned (rare)

If the same prompt runs multiple times with different outcomes (rerun, refinement), increment the version field:

```
## Version
v3 (after refinement based on feedback from v2 user review)
```

### Pattern 2: Overwritten (default)

Most prompts produce ONE SUMMARY.md and don't update it. If the underlying work changes, a new prompt run produces a new SUMMARY.md, archiving the old one.

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| Generic one-liner | Reader can't tell what happened | Substantive: specific numbers + verdicts |
| 30+ key findings | Hard to scan | Top 5-10; detail in main output |
| Decisions Needed without options | User doesn't know what to choose | Always list options + recommendation |
| Blockers and Decisions mixed | Reader can't tell which to act on first | Separate sections |
| Vague Next Step | Reader doesn't know what to do | Concrete command / prompt path |
| Missing one of the five required sections | Incomplete summary | All five sections present, even if empty |

## Cross-references

- `references/metadata-guidelines.md` — confidence, dependencies, open-questions metadata
- `references/do-patterns.md`, `plan-patterns.md`, `research-patterns.md`, `refine-patterns.md` — purpose-specific output structures
- `skills/create-meta-prompts/` — parent skill

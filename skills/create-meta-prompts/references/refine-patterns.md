# Refine Patterns

This reference is loaded by `create-meta-prompts` step 1 when the user's selected purpose is **Refine**. It defines the structural template for refinement prompts — prompts that take an existing output and improve it.

## When to use Refine patterns

The Refine purpose covers: refine, improve, deepen, expand, iterate, update, harden, polish. The output is a new version of an existing document, not a different document.

## Required structure

A Refine prompt operates on a specific TARGET output from an earlier prompt. It must:

1. Identify the target by exact path
2. State what's missing or weak
3. State what to preserve
4. Produce a v2 in the same folder structure with the v1 archived

```markdown
# {Topic} Refine prompt

## Target
Path to the existing output being refined.

## Why refine
What's missing, weak, or stale in the current version.

## What to preserve
Sections / decisions / claims from the current version that should remain intact.

## What to change
Specific, scoped changes. Not a rewrite.

## Versioning
- Current: archive to {path}/archive/{name}-v1.md
- New: write to {path}/{name}.md (same name, replacing in place)

## Validation
How the refined version is better than v1 — measurable improvements.
```

## Refine vs Deepen

These are closely related but distinct:

- **Refine** — broad improvement; can change scope, structure, conclusions
- **Deepen** (separate skill `deepen-prompt-plan`) — narrow improvement focused on confidence gaps; preserves structure and intent

If the user wants to "make the plan stronger without changing it," route to `deepen-prompt-plan`. If they want to "rewrite this section because we learned new things," use Refine.

## Anti-patterns

| Pattern | Why it's wrong | Do instead |
|---|---|---|
| Refining without identifying a target | Ambiguous; agent guesses wrong document | Always cite exact target path |
| Refine that discards v1 | Loses history; can't compare or roll back | Always archive v1 before writing v2 |
| Refine that changes everything | Equivalent to creating from scratch | Scope changes; preserve what was working |
| Refine without measurable improvement | "Better feel" isn't validatable | State the specific improvement (more sources, gates added, etc.) |
| Refine that doesn't update SUMMARY.md | Downstream consumes stale summary | Always refresh SUMMARY.md too |

## Template — minimal Refine prompt

```markdown
# Password reset research — Refine prompt

## Target
.prompts/002-pwreset-research/pwreset-research.md (v1)

## Why refine
- Open question Q1 (single-use links) was resolved by PM (yes, single-use)
- New finding: jose v5.2.0 dropped Node 16 support; need to verify compat with our runtime
- v1 didn't compare deliverability data; Resend dashboard data now available

## What to preserve
- All v1 findings on JWT lifetime (OWASP citations)
- Library comparison table (still accurate)
- Confidence rating: high

## What to change
- Add finding on Node 16 compat for jose
- Update Q1 status from open to resolved
- Add deliverability comparison: SendGrid, Postmark, Resend (we now have data)
- Adjust recommendation if Resend's deliverability turns out lower than claimed

## Versioning
- Archive: .prompts/002-pwreset-research/archive/pwreset-research-v1.md
- Replace: .prompts/002-pwreset-research/pwreset-research.md
- Update: .prompts/002-pwreset-research/SUMMARY.md

## Validation
- Diff v1 vs v2 shows specific deltas (Q1 resolution + 2 new findings)
- No regression in v1 findings
- New findings cite real data (Resend dashboard URL, Node compat matrix URL)
```

## SUMMARY.md schema for Refine prompts

```markdown
# Password reset research — Summary v2

**One-liner:** JWT with jose (verified Node 20 OK) + Postmark (best deliverability after data review).
Single-use reset links confirmed by PM.

**Confidence:** high
**Version:** v2 (changed from v1 in 2 findings + 1 question resolved)
**Sources consulted:** 14 (added: Resend dashboard, jose changelog)

## What changed from v1
- Q1 (single-use vs N-use) → RESOLVED: single-use (PM 2026-05-26)
- Email provider recommendation flipped: was Resend, now Postmark — deliverability data
- Added compat note on jose v5.2.0 + Node 16

## Preserved from v1
- All JWT lifetime findings
- OWASP citations
- Library comparison (jose vs jsonwebtoken)

## Open questions
None.

## Next step
Plan prompt can now proceed with email provider = Postmark.
```

## Archive discipline

Refining destroys history if v1 isn't archived. The Refine prompt MUST:

1. Create `{folder}/archive/` if not present
2. Move (not copy) v1 to `archive/{name}-v1.md`
3. Write v2 to the original path
4. Note the archive path in v2's SUMMARY.md

If v3 is needed later, archive v2 first → continue.

## When NOT to refine

- The change is structural enough that a fresh Research / Plan prompt is faster
- The target is more than 2 versions old (better to do a fresh research with current state of the world)
- The original author's intent is no longer relevant (project pivoted) — start over

In these cases, suggest `Research` / `Plan` / `Do` purpose instead.
